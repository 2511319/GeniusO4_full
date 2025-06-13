# api/routers/analysis.py

import os
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.crypto_compare_provider import fetch_ohlcv
from services.data_processor import DataProcessor
from services.chatgpt_analyzer import ChatGPTAnalyzer
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
    analysis: dict
    ohlc: List[dict]
    indicators: List[str]
    invalid_chatgpt_response: bool = False


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
    if hasattr(processor, 'get_candlestick_patterns'):
        patterns = processor.get_candlestick_patterns(req.limit)
    else:
        patterns = []

    # список вычисленных индикаторов
    base_cols = [
        'Open Time', 'Close Time', 'Open', 'High', 'Low', 'Close',
        'Volume', 'Quote Asset Volume', 'Number of Trades', 'Ignore',
        'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume'
    ]
    indicator_cols = [c for c in df_ind.columns if c not in base_cols]

    # 3. Анализ ChatGPT
    analyzer = ChatGPTAnalyzer()
    analysis, invalid = analyzer.analyze({"ohlc": ohlc})
    analysis = analysis or {}
    analysis["divergence_analysis"] = divergences
    analysis["candlestick_patterns"] = patterns

    return AnalyzeResponse(
        analysis=analysis,
        ohlc=ohlc,
        indicators=indicator_cols,
        invalid_chatgpt_response=invalid,
    )
