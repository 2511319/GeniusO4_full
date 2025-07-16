# backend/services/crypto_compare_provider.py
"""
Провайдер данных CryptoCompare для получения OHLCV данных
"""

import httpx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from config.config import get_settings, logger

settings = get_settings()


class CryptoCompareProvider:
    """Провайдер данных CryptoCompare"""
    
    def __init__(self):
        self.base_url = "https://min-api.cryptocompare.com/data"
        self.api_key = settings.cryptocompare_api_key
        self.session: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "authorization": f"Apikey {self.api_key}",
                "User-Agent": "ChartGenius-v3/1.0"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.aclose()
    
    async def get_ohlcv_data(
        self,
        symbol: str,
        interval: str,
        limit: int = 144
    ) -> List[Dict[str, Any]]:
        """
        Получение OHLCV данных для символа
        
        Args:
            symbol: Торговая пара (например, BTCUSDT)
            interval: Интервал (1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d)
            limit: Количество свечей
        
        Returns:
            Список OHLCV данных
        """
        try:
            # Преобразование символа для CryptoCompare
            from_symbol, to_symbol = self._parse_symbol(symbol)
            
            # Определение endpoint в зависимости от интервала
            endpoint = self._get_endpoint(interval)
            
            # Параметры запроса
            params = {
                "fsym": from_symbol,
                "tsym": to_symbol,
                "limit": min(limit, 2000),  # CryptoCompare лимит
                "api_key": self.api_key
            }
            
            # Добавляем aggregate для минутных интервалов
            if interval in ["5m", "15m", "30m"]:
                params["aggregate"] = int(interval.replace("m", ""))
                endpoint = f"{self.base_url}/histominute"
            elif interval in ["2h", "4h", "6h", "8h", "12h"]:
                params["aggregate"] = int(interval.replace("h", ""))
                endpoint = f"{self.base_url}/histohour"
            
            logger.info(f"📡 Запрос OHLCV данных: {symbol} {interval} limit={limit}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("Response") == "Error":
                    logger.error(f"❌ CryptoCompare API error: {data.get('Message')}")
                    return []
                
                raw_data = data.get("Data", [])
                
                if not raw_data:
                    logger.warning(f"⚠️ Нет данных для {symbol}")
                    return []
                
                # Преобразование в стандартный формат
                ohlcv_data = []
                for item in raw_data:
                    if item.get("volumeto", 0) > 0:  # Фильтруем свечи с объемом
                        ohlcv_data.append({
                            "timestamp": item["time"],
                            "datetime": datetime.fromtimestamp(item["time"]).isoformat(),
                            "open": float(item["open"]),
                            "high": float(item["high"]),
                            "low": float(item["low"]),
                            "close": float(item["close"]),
                            "volume": float(item["volumeto"])
                        })
                
                logger.info(f"✅ Получено {len(ohlcv_data)} свечей для {symbol}")
                return ohlcv_data
                
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ HTTP error при получении данных {symbol}: {e}")
            return []
        except httpx.RequestError as e:
            logger.error(f"❌ Request error при получении данных {symbol}: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Unexpected error при получении данных {symbol}: {e}")
            return []
    
    def _parse_symbol(self, symbol: str) -> tuple[str, str]:
        """Парсинг торговой пары"""
        symbol = symbol.upper()
        
        # Стандартные пары
        if symbol.endswith("USDT"):
            return symbol[:-4], "USDT"
        elif symbol.endswith("BTC"):
            return symbol[:-3], "BTC"
        elif symbol.endswith("ETH"):
            return symbol[:-3], "ETH"
        elif symbol.endswith("USD"):
            return symbol[:-3], "USD"
        else:
            # По умолчанию предполагаем USDT
            return symbol, "USDT"
    
    def _get_endpoint(self, interval: str) -> str:
        """Получение endpoint в зависимости от интервала"""
        if interval in ["1m", "5m", "15m", "30m"]:
            return f"{self.base_url}/histominute"
        elif interval in ["1h", "2h", "4h", "6h", "8h", "12h"]:
            return f"{self.base_url}/histohour"
        elif interval in ["1d", "3d", "1w"]:
            return f"{self.base_url}/histoday"
        else:
            # По умолчанию часовые данные
            return f"{self.base_url}/histohour"
    
    async def get_current_price(self, symbol: str) -> Optional[float]:
        """Получение текущей цены символа"""
        try:
            from_symbol, to_symbol = self._parse_symbol(symbol)
            
            params = {
                "fsym": from_symbol,
                "tsyms": to_symbol,
                "api_key": self.api_key
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/price",
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                return float(data.get(to_symbol, 0))
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения текущей цены {symbol}: {e}")
            return None
    
    async def get_multiple_symbols_data(
        self,
        symbols: List[str],
        interval: str,
        limit: int = 144
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Получение данных для нескольких символов параллельно"""
        tasks = []
        
        for symbol in symbols:
            task = self.get_ohlcv_data(symbol, interval, limit)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        symbol_data = {}
        for i, result in enumerate(results):
            symbol = symbols[i]
            if isinstance(result, Exception):
                logger.error(f"❌ Ошибка получения данных для {symbol}: {result}")
                symbol_data[symbol] = []
            else:
                symbol_data[symbol] = result
        
        return symbol_data
    
    async def validate_symbol(self, symbol: str) -> bool:
        """Проверка доступности символа"""
        try:
            data = await self.get_ohlcv_data(symbol, "1h", 1)
            return len(data) > 0
        except Exception:
            return False
    
    async def get_available_symbols(self) -> List[str]:
        """Получение списка доступных символов"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://min-api.cryptocompare.com/data/all/coinlist",
                    params={"api_key": self.api_key}
                )
                response.raise_for_status()
                
                data = response.json()
                coins = data.get("Data", {})
                
                # Возвращаем топ криптовалюты с USDT парами
                popular_coins = [
                    "BTC", "ETH", "ADA", "DOT", "LINK", "LTC", "BCH", 
                    "XLM", "EOS", "TRX", "BNB", "SOL", "AVAX", "MATIC"
                ]
                
                available_symbols = []
                for coin in popular_coins:
                    if coin in coins:
                        available_symbols.append(f"{coin}USDT")
                
                return available_symbols
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка символов: {e}")
            return [
                "BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT",
                "LTCUSDT", "BCHUSDT", "XLMUSDT", "EOSUSDT", "TRXUSDT"
            ]


# Глобальный экземпляр провайдера
crypto_provider = CryptoCompareProvider()
