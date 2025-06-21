# backend/routers/analysis.py

import os
import json
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator

from backend.services.crypto_compare_provider import fetch_ohlcv
from backend.services.data_processor import DataProcessor
from backend.services.chatgpt_analyzer import ChatGPTAnalyzer
from backend.services.viz import create_chart
from backend.validators.analysis_validators import (
    validate_analysis_request_data,
    ValidationError,
    SUPPORTED_INTERVALS,
    SUPPORTED_INDICATORS,
    MIN_LIMIT,
    MAX_LIMIT,
    DEFAULT_LIMIT
)

router = APIRouter()

# Тикер по умолчанию из окружения
DEFAULT_SYMBOL = os.getenv("DEFAULT_SYMBOL", "BTCUSDT")

class AnalyzeRequest(BaseModel):
    """
    Модель запроса для анализа с расширенной валидацией
    """
    symbol: str = Field(
        ...,
        min_length=2,
        max_length=20,
        description="Торговый символ (например: BTCUSDT, BTC-USDT, BTC/USDT)",
        example="BTCUSDT"
    )
    interval: str = Field(
        ...,
        description=f"Временной интервал. Поддерживаемые: {', '.join(sorted(SUPPORTED_INTERVALS))}",
        example="4h"
    )
    limit: int = Field(
        DEFAULT_LIMIT,
        ge=MIN_LIMIT,
        le=MAX_LIMIT,
        description=f"Количество свечей для анализа (от {MIN_LIMIT} до {MAX_LIMIT})",
        example=144
    )
    indicators: List[str] = Field(
        default_factory=list,
        description="Список индикаторов для отображения (пустой список = все индикаторы)",
        example=["RSI", "MACD", "Bollinger_Bands"]
    )
    drop_na: bool = Field(
        True,
        description="Удалять ли свечи с пропущенными значениями индикаторов"
    )

    @validator('symbol')
    def validate_symbol(cls, v):
        """Валидация торгового символа"""
        if not v or not v.strip():
            raise ValueError("Символ не может быть пустым")
        return v.strip().upper()

    @validator('interval')
    def validate_interval(cls, v):
        """Валидация временного интервала"""
        if not v or not v.strip():
            raise ValueError("Интервал не может быть пустым")

        clean_interval = v.strip().lower()
        if clean_interval not in SUPPORTED_INTERVALS:
            raise ValueError(
                f"Неподдерживаемый интервал: {v}. "
                f"Поддерживаемые: {', '.join(sorted(SUPPORTED_INTERVALS))}"
            )
        return clean_interval

    @validator('indicators')
    def validate_indicators(cls, v):
        """Валидация списка индикаторов"""
        if not v:
            return []

        if len(v) > len(SUPPORTED_INDICATORS):
            raise ValueError(f"Слишком много индикаторов: {len(v)}")

        clean_indicators = []
        invalid_indicators = []

        for indicator in v:
            if not isinstance(indicator, str):
                raise ValueError(f"Индикатор должен быть строкой: {indicator}")

            clean_indicator = indicator.strip()
            if not clean_indicator:
                continue

            # Ищем индикатор без учета регистра
            found_indicator = None
            for supported in SUPPORTED_INDICATORS:
                if clean_indicator.upper() == supported.upper():
                    found_indicator = supported
                    break

            if found_indicator is None:
                invalid_indicators.append(clean_indicator)
            else:
                clean_indicators.append(found_indicator)

        if invalid_indicators:
            raise ValueError(
                f"Неподдерживаемые индикаторы: {', '.join(invalid_indicators)}"
            )

        # Удаляем дубликаты
        return list(dict.fromkeys(clean_indicators))

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "BTCUSDT",
                "interval": "4h",
                "limit": 144,
                "indicators": ["RSI", "MACD", "Bollinger_Bands"],
                "drop_na": True
            }
        }

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

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    """
    Анализ криптовалютных данных с расширенной валидацией
    """
    try:
        # Дополнительная валидация с детальными проверками
        validated_symbol, validated_interval, validated_limit, validated_indicators = \
            validate_analysis_request_data(
                req.symbol,
                req.interval,
                req.limit,
                req.indicators
            )

        # Используем валидированные данные или дефолт
        symbol = validated_symbol or DEFAULT_SYMBOL

        # 1. Получаем OHLCV с небольшим запасом, чтобы индикаторы успели "разогнаться"
        extra_candles = 200
        fetch_limit = validated_limit + extra_candles

        try:
            df = await fetch_ohlcv(symbol, validated_interval, fetch_limit)
        except KeyError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Ошибка получения данных для символа {symbol} с интервалом {validated_interval}: {e}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка при получении данных: {e}"
            )

        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Нет данных для символа {symbol} с интервалом {validated_interval}"
            )

    except ValidationError:
        # ValidationError уже содержит правильный HTTP статус и детали
        raise
    except HTTPException:
        # Пробрасываем HTTP исключения как есть
        raise
    except Exception as e:
        # Обрабатываем неожиданные ошибки
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {e}"
        )

    # 2. Расчёт всех индикаторов
    try:
        processor = DataProcessor(df)
        df_ind = processor.perform_full_processing(drop_na=req.drop_na)
        ohlc = processor.get_ohlc_data(validated_limit)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке данных: {e}"
        )

    # список вычисленных индикаторов
    base_cols = [
        'Open Time', 'Close Time', 'Open', 'High', 'Low', 'Close',
        'Volume', 'Quote Asset Volume', 'Number of Trades', 'Ignore',
        'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume'
    ]
    indicator_cols = [c for c in df_ind.columns if c not in base_cols]

    # 3. Анализ с помощью LLM
    try:
        analyzer = ChatGPTAnalyzer()
        analysis = analyzer.analyze({"ohlc": ohlc})

        # Проверяем, что анализ содержит необходимые данные
        if not analysis or not isinstance(analysis, dict):
            raise ValueError("Получен пустой или некорректный анализ")

    except Exception as e:
        # Логируем ошибку для мониторинга
        from backend.config.config import logger
        logger.error(f"Ошибка анализа для {validated_symbol}: {e}")

        # Возвращаем ошибку клиенту вместо пустого анализа
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Сервис анализа временно недоступен",
                "message": "Попробуйте повторить запрос через несколько минут",
                "symbol": validated_symbol,
                "retry_after": 60
            }
        )

    # 4. Визуализация (рисуем выбранные слои)
    try:
        layers = validated_indicators or ALL_LAYERS
        fig = create_chart(layers, df_ind, analysis)
        figure_dict = json.loads(fig.to_json())
    except Exception as e:
        # Если визуализация не удалась, возвращаем пустую фигуру
        figure_dict = {"error": f"Визуализация не удалась: {e}"}

    return AnalyzeResponse(
        figure=figure_dict,
        analysis=analysis,
        ohlc=ohlc,
        indicators=indicator_cols
    )

@router.post("/analyze-test")
async def analyze_test(req: AnalyzeRequest):
    """Тестовый endpoint с фиктивными данными"""
    # Создаем тестовые OHLC данные
    test_ohlc = [
        {
            "Open Time": "2024-01-01T00:00:00Z",
            "Close Time": "2024-01-01T04:00:00Z",
            "Open": 42000.0,
            "High": 42500.0,
            "Low": 41800.0,
            "Close": 42200.0,
            "Volume": 1000.0
        },
        {
            "Open Time": "2024-01-01T04:00:00Z",
            "Close Time": "2024-01-01T08:00:00Z",
            "Open": 42200.0,
            "High": 42800.0,
            "Low": 42000.0,
            "Close": 42600.0,
            "Volume": 1200.0
        }
    ]

    # Создаем тестовый анализ
    test_analysis = {
        "primary_analysis": "Тестовый анализ показывает восходящий тренд",
        "confidence_in_trading_decisions": "Высокая уверенность в сигналах",
        "support_resistance_levels": {
            "supports": [{"level": 41800, "date": "2024-01-01T00:00:00Z"}],
            "resistances": [{"level": 42800, "date": "2024-01-01T04:00:00Z"}]
        },
        "recommendations": {
            "trading_strategies": [
                {
                    "strategy": "Покупка на откате к поддержке",
                    "stop_loss": 41500,
                    "take_profit": 43000,
                    "risk": "Средний"
                }
            ]
        },
        "price_prediction": {
            "direction": "Вверх",
            "target_price": 43000,
            "confidence": 0.75
        }
    }

    return AnalyzeResponse(
        figure={},
        analysis=test_analysis,
        ohlc=test_ohlc,
        indicators=["RSI", "MACD"]
    )
