# backend/routers/analysis.py
"""
Роутер для технического анализа криптовалют
Основной endpoint для получения 24 объектов AI анализа
"""

import time
import json
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, validator

from auth.dependencies import get_current_user, check_analysis_limit
from services.crypto_compare_provider import CryptoCompareProvider
from services.chatgpt_analyzer import ChatGPTAnalyzer
from services.cache_service import CacheService
from config.config import get_settings, logger, Constants
from config.database import execute_query, execute_one

router = APIRouter()
settings = get_settings()


class AnalysisRequest(BaseModel):
    """Модель запроса анализа"""
    symbol: str = "BTCUSDT"
    interval: str = "4h"
    days: int = 15
    
    @validator('symbol')
    def validate_symbol(cls, v):
        if v not in Constants.SUPPORTED_SYMBOLS:
            raise ValueError(f'Символ должен быть одним из: {Constants.SUPPORTED_SYMBOLS}')
        return v.upper()
    
    @validator('interval')
    def validate_interval(cls, v):
        if v not in Constants.SUPPORTED_INTERVALS:
            raise ValueError(f'Интервал должен быть одним из: {Constants.SUPPORTED_INTERVALS}')
        return v
    
    @validator('days')
    def validate_days(cls, v):
        if not 7 <= v <= 30:
            raise ValueError('Количество дней должно быть от 7 до 30')
        return v


class AnalysisResponse(BaseModel):
    """Модель ответа анализа"""
    success: bool
    analysis_id: Optional[int] = None
    symbol: str
    interval: str
    days: int
    processing_time_ms: int
    ai_model: str
    timestamp: str
    data: Dict[str, Any]  # 24 объекта AI анализа


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_symbol(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    _: None = Depends(check_analysis_limit)
):
    """
    Основной endpoint для технического анализа
    Возвращает 24 объекта AI анализа согласно chatgpt_response_1749154674.json
    """
    start_time = time.time()
    
    try:
        logger.info(f"🔍 Начат анализ {request.symbol} {request.interval} для пользователя {current_user['telegram_id']}")
        
        # Проверяем кэш
        cache_service = CacheService()
        cache_key = f"analysis:{request.symbol}:{request.interval}:{request.days}"
        
        if settings.enable_cache:
            cached_result = await cache_service.get(cache_key)
            if cached_result:
                logger.info(f"📦 Возвращен кэшированный результат для {request.symbol}")
                return AnalysisResponse(
                    success=True,
                    symbol=request.symbol,
                    interval=request.interval,
                    days=request.days,
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    ai_model=settings.openai_model,
                    timestamp=datetime.now().isoformat(),
                    data=cached_result
                )
        
        # Получение OHLCV данных
        crypto_provider = CryptoCompareProvider()
        ohlcv_data = await crypto_provider.get_ohlcv_data(
            symbol=request.symbol,
            interval=request.interval,
            limit=_calculate_limit(request.interval, request.days)
        )
        
        if not ohlcv_data or len(ohlcv_data) < 50:
            raise HTTPException(
                status_code=400,
                detail=f"Недостаточно данных для анализа {request.symbol}"
            )
        
        logger.info(f"📊 Получено {len(ohlcv_data)} свечей для {request.symbol}")
        
        # AI анализ
        analyzer = ChatGPTAnalyzer()
        analysis_result = await analyzer.analyze_ohlcv_data(
            ohlcv_data=ohlcv_data,
            symbol=request.symbol,
            interval=request.interval
        )
        
        if not analysis_result:
            raise HTTPException(
                status_code=500,
                detail="Ошибка при выполнении AI анализа"
            )
        
        # Валидация структуры ответа (24 объекта)
        if not _validate_analysis_structure(analysis_result):
            logger.error("❌ AI анализ не содержит все 24 объекта")
            raise HTTPException(
                status_code=500,
                detail="Неполный AI анализ"
            )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Сохранение в базу данных (в фоне)
        background_tasks.add_task(
            _save_analysis_to_db,
            user_id=current_user['id'],
            symbol=request.symbol,
            interval=request.interval,
            days=request.days,
            analysis_data=analysis_result,
            ohlcv_data=ohlcv_data,
            processing_time_ms=processing_time_ms
        )
        
        # Кэширование результата
        if settings.enable_cache:
            background_tasks.add_task(
                cache_service.set,
                cache_key,
                analysis_result,
                settings.cache_ttl_seconds
            )
        
        # Обновление счетчика анализов пользователя
        background_tasks.add_task(
            _update_user_analysis_count,
            current_user['id']
        )
        
        logger.info(f"✅ Анализ {request.symbol} завершен за {processing_time_ms}ms")
        
        return AnalysisResponse(
            success=True,
            symbol=request.symbol,
            interval=request.interval,
            days=request.days,
            processing_time_ms=processing_time_ms,
            ai_model=settings.openai_model,
            timestamp=datetime.now().isoformat(),
            data=analysis_result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка анализа {request.symbol}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка при анализе: {str(e)}"
        )


@router.get("/history")
async def get_analysis_history(
    limit: int = 10,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Получение истории анализов пользователя"""
    try:
        query = """
            SELECT id, symbol, interval_type, days_count, 
                   created_at, processing_time_ms
            FROM analyses 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC 
            OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
        """
        
        results = await execute_query(query, {
            "user_id": current_user['id'],
            "offset": offset,
            "limit": min(limit, 50)  # Максимум 50 записей
        })
        
        history = []
        for row in results:
            history.append({
                "id": row[0],
                "symbol": row[1],
                "interval": row[2],
                "days": row[3],
                "created_at": row[4].isoformat() if row[4] else None,
                "processing_time_ms": row[5]
            })
        
        return {
            "success": True,
            "history": history,
            "total": len(history)
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения истории: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения истории")


@router.get("/history/{analysis_id}")
async def get_analysis_by_id(
    analysis_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Получение конкретного анализа по ID"""
    try:
        query = """
            SELECT analysis_data, symbol, interval_type, days_count, 
                   created_at, processing_time_ms
            FROM analyses 
            WHERE id = :analysis_id AND user_id = :user_id
        """
        
        result = await execute_one(query, {
            "analysis_id": analysis_id,
            "user_id": current_user['id']
        })
        
        if not result:
            raise HTTPException(status_code=404, detail="Анализ не найден")
        
        analysis_data = json.loads(result[0]) if result[0] else {}
        
        return {
            "success": True,
            "analysis": {
                "id": analysis_id,
                "data": analysis_data,
                "symbol": result[1],
                "interval": result[2],
                "days": result[3],
                "created_at": result[4].isoformat() if result[4] else None,
                "processing_time_ms": result[5]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка получения анализа {analysis_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения анализа")


def _calculate_limit(interval: str, days: int) -> int:
    """Расчет количества свечей для запроса"""
    intervals_per_day = {
        "1m": 1440, "5m": 288, "15m": 96, "30m": 48,
        "1h": 24, "2h": 12, "4h": 6, "6h": 4, "8h": 3, "12h": 2, "1d": 1
    }
    
    per_day = intervals_per_day.get(interval, 6)  # По умолчанию 4h
    limit = per_day * days
    
    return min(max(limit, Constants.MIN_LIMIT), Constants.MAX_LIMIT)


def _validate_analysis_structure(analysis: Dict[str, Any]) -> bool:
    """Валидация структуры AI анализа (24 объекта)"""
    required_keys = [
        "primary_analysis", "confidence_in_trading_decisions", "support_resistance_levels",
        "trend_lines", "pivot_points", "fibonacci_levels", "volume_analysis",
        "momentum_indicators", "oscillators", "moving_averages", "bollinger_bands",
        "ichimoku_cloud", "candlestick_patterns", "chart_patterns", "elliott_wave",
        "market_structure", "risk_management", "entry_exit_points", "price_targets",
        "stop_loss_levels", "market_sentiment", "correlation_analysis", 
        "volatility_analysis", "time_frame_analysis"
    ]
    
    missing_keys = [key for key in required_keys if key not in analysis]
    
    if missing_keys:
        logger.warning(f"⚠️ Отсутствуют ключи в AI анализе: {missing_keys}")
        return False
    
    return True


async def _save_analysis_to_db(
    user_id: int,
    symbol: str,
    interval: str,
    days: int,
    analysis_data: Dict[str, Any],
    ohlcv_data: list,
    processing_time_ms: int
):
    """Сохранение анализа в базу данных"""
    try:
        query = """
            INSERT INTO analyses (
                user_id, symbol, interval_type, days_count, 
                analysis_data, ohlcv_data, ai_model, processing_time_ms
            ) VALUES (
                :user_id, :symbol, :interval_type, :days_count,
                :analysis_data, :ohlcv_data, :ai_model, :processing_time_ms
            )
        """
        
        await execute_query(query, {
            "user_id": user_id,
            "symbol": symbol,
            "interval_type": interval,
            "days_count": days,
            "analysis_data": json.dumps(analysis_data, ensure_ascii=False),
            "ohlcv_data": json.dumps(ohlcv_data, ensure_ascii=False),
            "ai_model": settings.openai_model,
            "processing_time_ms": processing_time_ms
        })
        
        logger.info(f"💾 Анализ {symbol} сохранен в БД для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения анализа в БД: {e}")


async def _update_user_analysis_count(user_id: int):
    """Обновление счетчика анализов пользователя"""
    try:
        query = """
            UPDATE users 
            SET analyses_today = analyses_today + 1,
                last_analysis_date = CURRENT_DATE
            WHERE id = :user_id
        """
        
        await execute_query(query, {"user_id": user_id})
        
    except Exception as e:
        logger.error(f"❌ Ошибка обновления счетчика анализов: {e}")
