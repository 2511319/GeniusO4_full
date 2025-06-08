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
from services.statistical_analysis import StatisticalAnalyzer

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

    stat_analyzer = StatisticalAnalyzer(df_ind)
    divergences = []
    divergences.extend(stat_analyzer.find_divergences("RSI"))
    divergences.extend(stat_analyzer.find_divergences("MACD"))

    # список вычисленных индикаторов
    base_cols = [
        'Open Time', 'Close Time', 'Open', 'High', 'Low', 'Close',
        'Volume', 'Quote Asset Volume', 'Number of Trades', 'Ignore',
        'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume'
    ]
    indicator_cols = [c for c in df_ind.columns if c not in base_cols]

    # 3. Анализ ChatGPT
    analyzer = ChatGPTAnalyzer()
    analysis = analyzer.analyze({"ohlc": ohlc}) or {}
    analysis["divergence_analysis"] = divergences

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
