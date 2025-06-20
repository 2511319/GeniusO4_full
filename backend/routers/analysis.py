# api/routers/analysis.py

import os
import json
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.crypto_compare_provider import fetch_ohlcv
from services.data_processor import DataProcessor
from services.chatgpt_analyzer import ChatGPTAnalyzer
from services.viz import create_chart

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

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    # если пользователь оставил пустой символ — подставляем дефолт
    symbol = req.symbol.strip().upper() or DEFAULT_SYMBOL

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

    # 4. Визуализация (рисуем выбранные слои)
    layers = req.indicators or ALL_LAYERS
    fig = create_chart(layers, df_ind, analysis)

    return AnalyzeResponse(
        # Преобразуем JSON-строку фигуры в dict, иначе Pydantic не сможет сериализовать
        figure=json.loads(fig.to_json()),
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
