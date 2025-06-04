# api/routers/analysis.py

import os
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
    symbol:   str
    interval: str
    limit:    int

class AnalyzeResponse(BaseModel):
    figure:   dict
    analysis: dict

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    # если пользователь оставил пустой символ — подставляем дефолт
    symbol = req.symbol.strip().upper() or DEFAULT_SYMBOL

    # 1. Получаем OHLCV
    df = await fetch_ohlcv(symbol, req.interval, req.limit)
    if df.empty:
        raise HTTPException(404, f"No data for symbol {symbol}")

    # 2. Расчёт всех индикаторов
    processor = DataProcessor(df)
    df_ind   = processor.perform_full_processing()

    # 3. Анализ ChatGPT
    analyzer = ChatGPTAnalyzer()
    analysis = analyzer.analyze(df_ind)

    # 4. Визуализация (рисуем всё, что посчитали)
    fig = create_chart(df_ind, analysis)

    return AnalyzeResponse(
        figure=fig.to_dict(),
        analysis=analysis
    )
