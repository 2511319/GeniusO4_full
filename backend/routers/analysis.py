# api/routers/analysis.py

import os
import json
import time
from typing import List

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

from backend.services.crypto_compare_provider import fetch_ohlcv
from backend.services.data_processor import DataProcessor
from backend.services.chatgpt_analyzer import ChatGPTAnalyzer
from backend.services.viz import create_chart
from backend.services.subscription_manager import check_subscription, can_perform_analysis, increment_analysis_count
from backend.services.analysis_storage import save_analysis

router = APIRouter()

# Тикер по умолчанию из окружения
DEFAULT_SYMBOL = os.getenv("DEFAULT_SYMBOL", "BTCUSDT")

class AnalyzeRequest(BaseModel):
    symbol: str
    interval: str
    limit: int
    indicators: List[str] = []
    drop_na: bool = True

class AnalyzeResponse(BaseModel):
    figure: dict
    analysis: dict
    ohlc: List[dict]
    indicators: List[str]

ALL_LAYERS = [
    'MACD', 'RSI', 'OBV', 'ATR', 'ADX', 'Stochastic_Oscillator', 'Volume',
    'Bollinger_Bands', 'Ichimoku_Cloud', 'Parabolic_SAR', 'VWAP',
    'Moving_Average_Envelopes', 'support_resistance_levels', 'trend_lines',
    'unfinished_zones', 'imbalances', 'fibonacci_analysis',
    'elliott_wave_analysis', 'structural_edge', 'candlestick_patterns',
    'divergence_analysis', 'fair_value_gaps', 'gap_analysis',
    'psychological_levels', 'anomalous_candles', 'price_prediction',
    'recommendations'
]

def create_primary_analysis(full_analysis: dict) -> dict:
    """
    Создает краткую сводку анализа для быстрого просмотра
    """
    try:
        primary = {
            "summary": full_analysis.get("summary", "Анализ выполнен"),
            "trend": "Не определен",
            "signal": "Нейтральный",
            "risk_level": "Средний",
            "key_levels": [],
            "main_recommendation": "Ожидание"
        }

        # Извлекаем основной тренд
        if "trend_analysis" in full_analysis:
            trend_data = full_analysis["trend_analysis"]
            if isinstance(trend_data, dict):
                primary["trend"] = trend_data.get("direction", "Не определен")

        # Извлекаем торговый сигнал
        if "recommendations" in full_analysis:
            recommendations = full_analysis["recommendations"]
            if isinstance(recommendations, dict):
                primary["signal"] = recommendations.get("action", "Нейтральный")
                primary["main_recommendation"] = recommendations.get("summary", "Ожидание")

        # Извлекаем уровни поддержки/сопротивления
        if "support_resistance_levels" in full_analysis:
            levels_data = full_analysis["support_resistance_levels"]
            if isinstance(levels_data, dict):
                support = levels_data.get("support_levels", [])
                resistance = levels_data.get("resistance_levels", [])
                primary["key_levels"] = {
                    "support": support[:2] if isinstance(support, list) else [],
                    "resistance": resistance[:2] if isinstance(resistance, list) else []
                }

        # Определяем уровень риска
        if "risk_analysis" in full_analysis:
            risk_data = full_analysis["risk_analysis"]
            if isinstance(risk_data, dict):
                primary["risk_level"] = risk_data.get("level", "Средний")

        return primary

    except Exception as e:
        # В случае ошибки возвращаем базовую структуру
        return {
            "summary": "Анализ выполнен, но возникли проблемы с обработкой данных",
            "trend": "Не определен",
            "signal": "Нейтральный",
            "risk_level": "Средний",
            "key_levels": [],
            "main_recommendation": "Рекомендуется дополнительный анализ"
        }

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest, x_telegram_id: str = Header(None)):
    # если пользователь оставил пустой символ — подставляем дефолт
    symbol = req.symbol.strip().upper() or DEFAULT_SYMBOL

    # Проверяем лимиты для полного анализа (если передан telegram_id)
    if x_telegram_id:
        can_perform, error_message = can_perform_analysis(x_telegram_id, 'full')
        if not can_perform:
            if "лимит" in error_message.lower():
                raise HTTPException(429, error_message)
            else:
                raise HTTPException(402, error_message)

    # 1. Получаем OHLCV с небольшим запасом, чтобы индикаторы успели "разогнаться"
    extra_candles = 200
    fetch_limit = req.limit + extra_candles
    df = await fetch_ohlcv(symbol, req.interval, fetch_limit)
    if df.empty:
        raise HTTPException(404, f"No data for symbol {symbol}")

    # 2. Расчёт всех индикаторов
    processor = DataProcessor(df)
    df_ind = processor.perform_full_processing(drop_na=req.drop_na)
    ohlc = processor.get_ohlc_data(req.limit)

    # список вычисленных индикаторов
    base_cols = [
        'Open Time', 'Close Time', 'Open', 'High', 'Low', 'Close',
        'Volume', 'Quote Asset Volume', 'Number of Trades', 'Ignore',
        'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume'
    ]
    indicator_cols = [c for c in df_ind.columns if c not in base_cols]

    # 3. Анализ ChatGPT
    analyzer = ChatGPTAnalyzer()
    analysis = analyzer.analyze({"ohlc": ohlc})

    # 4. Увеличиваем счетчик анализов (если есть telegram_id)
    if x_telegram_id:
        increment_analysis_count(x_telegram_id)

    # 5. Визуализация (рисуем выбранные слои)
    layers = req.indicators or ALL_LAYERS
    fig = create_chart(layers, df_ind, analysis)

    # 6. Сохраняем полный анализ (если есть telegram_id)
    if x_telegram_id:
        analysis_data = {
            "symbol": symbol,
            "type": "full",
            "interval": req.interval,
            "limit": req.limit,
            "analysis": analysis,
            "primary_analysis": create_primary_analysis(analysis),
            "ohlc": ohlc,
            "indicators": indicator_cols,
            "layers": layers,
            "timestamp": int(time.time())
        }
        save_analysis(x_telegram_id, analysis_data)

    return AnalyzeResponse(
        # Преобразуем JSON-строку фигуры в dict, иначе Pydantic не сможет сериализовать
        figure=json.loads(fig.to_json()),
        analysis=analysis,
        ohlc=ohlc,
        indicators=indicator_cols
    )

@router.post("/analysis/simple")
async def simple_analysis(x_telegram_id: str = Header(None)):
    """
    Упрощенный анализ для Telegram бота
    """
    if not x_telegram_id:
        raise HTTPException(400, "X-Telegram-Id header required")

    # Проверяем возможность выполнения анализа
    can_perform, error_message = can_perform_analysis(x_telegram_id, 'simple')
    if not can_perform:
        if "лимит" in error_message.lower():
            raise HTTPException(429, error_message)  # Too Many Requests
        else:
            raise HTTPException(402, error_message)  # Payment Required

    # Выполняем базовый анализ
    symbol = DEFAULT_SYMBOL
    interval = "4h"
    limit = 100

    try:
        # Получаем данные
        df = await fetch_ohlcv(symbol, interval, limit + 200)
        if df.empty:
            raise HTTPException(404, f"No data for symbol {symbol}")

        # Обрабатываем данные
        processor = DataProcessor(df)
        df_ind = processor.perform_full_processing(drop_na=True)
        ohlc = processor.get_ohlc_data(limit)

        # Анализ
        analyzer = ChatGPTAnalyzer()
        analysis = analyzer.analyze({"ohlc": ohlc})

        # Увеличиваем счетчик использованных анализов
        increment_analysis_count(x_telegram_id)

        # Создаем краткую сводку анализа (primary_analysis)
        primary_analysis = create_primary_analysis(analysis)

        # Подготавливаем данные для сохранения
        analysis_data = {
            "symbol": symbol,
            "type": "simple",
            "interval": interval,
            "limit": limit,
            "analysis": analysis,
            "primary_analysis": primary_analysis,
            "ohlc": ohlc,
            "timestamp": int(time.time())
        }

        # Сохраняем анализ в Firestore
        analysis_id = save_analysis(x_telegram_id, analysis_data)

        # Возвращаем упрощенный результат
        return {
            "id": analysis_id or f"analysis_{x_telegram_id}_{int(time.time())}",
            "symbol": symbol,
            "analysis": analysis,
            "primary_analysis": primary_analysis,
            "timestamp": int(time.time())
        }

    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")
