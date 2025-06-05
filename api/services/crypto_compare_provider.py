# api/services/crypto_compare_provider.py

import os
import re
import time
import pandas as pd
import httpx

# API key для CryptoCompare
API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY", "")
# базовый URL для исторических данных
BASE_URL = "https://min-api.cryptocompare.com/data/v2/histo"

# Тикер по умолчанию
DEFAULT_SYMBOL = os.getenv("DEFAULT_SYMBOL", "BTCUSDT")
# Валюта по умолчанию для котируемой части
DEFAULT_QUOTE = os.getenv("DEFAULT_QUOTE", "USD")
# Флаг логирования
DEBUG = os.getenv("DEBUG_LOGGING", "false").lower() == "true"
DEV_LOG_DIR = os.path.join(os.getcwd(), "api", "dev_logs")


async def fetch_ohlcv(symbol: str, interval: str, limit: int) -> pd.DataFrame:
    """
    Получает OHLCV из CryptoCompare, возвращает DataFrame
    с колонками:
      Open Time, Close Time, Open, High, Low, Close, Volume, Quote Asset Volume
    """
    # 1) Подготовка параметров
    pair = (symbol or "").strip().upper() or DEFAULT_SYMBOL
    base, quote = pair, DEFAULT_QUOTE

    if any(sep in pair for sep in ["-", "_", "/"]):
        parts = re.split(r"[-_/]", pair)
        if len(parts) >= 2:
            base, quote = parts[0], parts[1]
    else:
        known_quotes = [
            "USDT", "USDC", "BUSD", "BTC", "ETH", "BNB",
            "USD", "EUR", "TRY",
        ]
        for q in known_quotes:
            if pair.endswith(q) and len(pair) > len(q):
                base, quote = pair[:-len(q)], q
                break

    if base == pair:
        quote = DEFAULT_QUOTE

    period = {
        "1m": "minute", "5m": "minute", "15m": "minute",
        "1h": "hour", "4h": "hour", "1d": "day"
    }[interval]
    agg = int(interval[:-1]) if period == "minute" else 1

    url = f"{BASE_URL}{period}"
    params = {
        "fsym": base,
        "tsym": quote,
        "limit": limit,
        "aggregate": agg,
        "api_key": API_KEY
    }

    # 2) Запрос к API
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=10)
    payload = resp.json().get("Data", {}).get("Data", [])

    # 3) Конвертация в DataFrame
    df = pd.DataFrame(payload)
    if df.empty:
        return df

    # 4) Отладочное логирование сырого DataFrame
    if DEBUG:
        os.makedirs(DEV_LOG_DIR, exist_ok=True)
        ts = int(time.time())
        cols_file = os.path.join(DEV_LOG_DIR, f"raw_cols_{base}_{quote}_{interval}_{ts}.txt")
        with open(cols_file, "w", encoding="utf-8") as f:
            f.write("Columns:\n" + "\n".join(df.columns) + "\n\n")
            f.write("First rows:\n" + df.head(5).to_string())

    # 5) Переименовываем основные поля
    df.rename(columns={
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volumefrom": "Volume",
        "volumeto": "Quote Asset Volume"
    }, inplace=True)

    # 6) Делаем временные колонки из исходного time
    df["Open Time"] = pd.to_datetime(df["time"], unit="s")
    df["Close Time"] = df["Open Time"] + pd.to_timedelta(agg, unit=period)
    # убираем уже ненужную колонку time
    df.drop(columns=["time"], inplace=True)

    return df
