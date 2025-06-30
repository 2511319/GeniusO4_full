# 📊 CCXT Integration Service for ChartGenius
# Версия: 1.1.0-dev
# Поэтапная интеграция CCXT для market data

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import ccxt.async_support as ccxt
import pandas as pd
from dataclasses import dataclass
from enum import Enum
import json

from backend.services.metrics_service import metrics
from backend.config.config import logger

class ExchangeStatus(Enum):
    """Статусы бирж"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"

@dataclass
class ExchangeConfig:
    """Конфигурация биржи"""
    name: str
    priority: int  # 1 = highest priority
    rate_limit: int  # requests per minute
    timeout: float = 30.0
    retry_attempts: int = 3

@dataclass
class MarketDataResponse:
    """Ответ с рыночными данными"""
    symbol: str
    timeframe: str
    data: List[List[float]]  # OHLCV format
    source: str
    timestamp: datetime
    count: int

class CCXTService:
    """Сервис для работы с CCXT"""
    
    def __init__(self):
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self.exchange_configs: Dict[str, ExchangeConfig] = {}
        self.exchange_health: Dict[str, ExchangeStatus] = {}
        self.fallback_order: List[str] = []
        
        # Инициализация бирж
        self._initialize_exchanges()
    
    def _initialize_exchanges(self):
        """Инициализация поддерживаемых бирж"""
        configs = [
            ExchangeConfig(name='binance', priority=1, rate_limit=1200),
            ExchangeConfig(name='coinbase', priority=2, rate_limit=600),
            ExchangeConfig(name='kraken', priority=3, rate_limit=900),
            ExchangeConfig(name='bybit', priority=4, rate_limit=600),
        ]
        
        for config in configs:
            try:
                exchange_class = getattr(ccxt, config.name)
                exchange = exchange_class({
                    'enableRateLimit': True,
                    'timeout': config.timeout * 1000,  # CCXT expects milliseconds
                    'options': {
                        'defaultType': 'spot',  # spot trading
                    }
                })
                
                self.exchanges[config.name] = exchange
                self.exchange_configs[config.name] = config
                self.exchange_health[config.name] = ExchangeStatus.HEALTHY
                
                logger.info(f"Initialized exchange: {config.name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize exchange {config.name}: {e}")
        
        # Устанавливаем порядок fallback по приоритету
        self.fallback_order = sorted(
            self.exchange_configs.keys(),
            key=lambda x: self.exchange_configs[x].priority
        )
    
    async def get_ohlcv_data(self, symbol: str, timeframe: str = '4h', 
                           limit: int = 500, preferred_exchange: Optional[str] = None) -> Optional[MarketDataResponse]:
        """
        Получение OHLCV данных с автоматическим fallback
        
        Args:
            symbol: Торговая пара (например, 'BTC/USDT')
            timeframe: Временной интервал ('1m', '5m', '1h', '4h', '1d')
            limit: Количество свечей
            preferred_exchange: Предпочитаемая биржа
            
        Returns:
            MarketDataResponse или None при ошибке
        """
        # Определяем порядок попыток
        exchanges_to_try = []
        
        if preferred_exchange and preferred_exchange in self.exchanges:
            exchanges_to_try.append(preferred_exchange)
        
        # Добавляем остальные биржи по порядку fallback
        for exchange_name in self.fallback_order:
            if exchange_name not in exchanges_to_try:
                exchanges_to_try.append(exchange_name)
        
        last_error = None
        
        for exchange_name in exchanges_to_try:
            # Пропускаем недоступные биржи
            if self.exchange_health[exchange_name] == ExchangeStatus.UNAVAILABLE:
                logger.warning(f"Skipping unavailable exchange: {exchange_name}")
                continue
            
            try:
                logger.info(f"Attempting to fetch OHLCV from {exchange_name}")
                
                exchange = self.exchanges[exchange_name]
                config = self.exchange_configs[exchange_name]
                
                # Получаем данные с retry логикой
                ohlcv_data = await self._fetch_with_retry(
                    exchange, symbol, timeframe, limit, config.retry_attempts
                )
                
                if ohlcv_data:
                    # Обновляем статус здоровья
                    self.exchange_health[exchange_name] = ExchangeStatus.HEALTHY
                    
                    # Трекинг метрик
                    metrics.track_user_action('ccxt_data_fetch_success', 'system')
                    
                    return MarketDataResponse(
                        symbol=symbol,
                        timeframe=timeframe,
                        data=ohlcv_data,
                        source=exchange_name,
                        timestamp=datetime.utcnow(),
                        count=len(ohlcv_data)
                    )
                
            except Exception as e:
                last_error = e
                logger.warning(f"Exchange {exchange_name} failed: {e}")
                
                # Обновляем статус здоровья
                self._update_exchange_health(exchange_name, False)
                
                # Трекинг ошибок
                metrics.track_error(type(e).__name__, 'ccxt_service')
                
                continue
        
        # Все биржи не сработали
        logger.error(f"All exchanges failed for {symbol}. Last error: {last_error}")
        metrics.track_user_action('ccxt_data_fetch_failed', 'system')
        return None
    
    async def _fetch_with_retry(self, exchange: ccxt.Exchange, symbol: str, 
                               timeframe: str, limit: int, max_retries: int) -> Optional[List[List[float]]]:
        """Получение данных с повторными попытками"""
        for attempt in range(max_retries):
            try:
                # Проверяем поддержку символа
                if not await self._check_symbol_support(exchange, symbol):
                    logger.warning(f"Symbol {symbol} not supported on {exchange.id}")
                    return None
                
                # Получаем OHLCV данные
                ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                
                if ohlcv and len(ohlcv) > 0:
                    logger.info(f"Successfully fetched {len(ohlcv)} candles from {exchange.id}")
                    return ohlcv
                
            except ccxt.NetworkError as e:
                logger.warning(f"Network error on {exchange.id}, attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                
            except ccxt.ExchangeError as e:
                logger.error(f"Exchange error on {exchange.id}: {e}")
                break  # Не повторяем при ошибках биржи
                
            except Exception as e:
                logger.error(f"Unexpected error on {exchange.id}: {e}")
                break
        
        return None
    
    async def _check_symbol_support(self, exchange: ccxt.Exchange, symbol: str) -> bool:
        """Проверка поддержки символа на бирже"""
        try:
            # Загружаем рынки если нужно
            if not exchange.markets:
                await exchange.load_markets()
            
            return symbol in exchange.markets
            
        except Exception as e:
            logger.error(f"Error checking symbol support: {e}")
            return False
    
    def _update_exchange_health(self, exchange_name: str, success: bool):
        """Обновление статуса здоровья биржи"""
        if success:
            self.exchange_health[exchange_name] = ExchangeStatus.HEALTHY
        else:
            current_status = self.exchange_health[exchange_name]
            
            if current_status == ExchangeStatus.HEALTHY:
                self.exchange_health[exchange_name] = ExchangeStatus.DEGRADED
            elif current_status == ExchangeStatus.DEGRADED:
                self.exchange_health[exchange_name] = ExchangeStatus.UNAVAILABLE
    
    async def get_ticker_data(self, symbol: str, preferred_exchange: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Получение текущих цен (ticker)"""
        exchanges_to_try = [preferred_exchange] if preferred_exchange else self.fallback_order
        
        for exchange_name in exchanges_to_try:
            if exchange_name not in self.exchanges:
                continue
                
            if self.exchange_health[exchange_name] == ExchangeStatus.UNAVAILABLE:
                continue
            
            try:
                exchange = self.exchanges[exchange_name]
                ticker = await exchange.fetch_ticker(symbol)
                
                if ticker:
                    self.exchange_health[exchange_name] = ExchangeStatus.HEALTHY
                    
                    return {
                        'symbol': ticker['symbol'],
                        'last': ticker['last'],
                        'bid': ticker['bid'],
                        'ask': ticker['ask'],
                        'volume': ticker['baseVolume'],
                        'change': ticker['change'],
                        'percentage': ticker['percentage'],
                        'timestamp': ticker['timestamp'],
                        'source': exchange_name
                    }
                
            except Exception as e:
                logger.warning(f"Ticker fetch failed on {exchange_name}: {e}")
                self._update_exchange_health(exchange_name, False)
                continue
        
        return None
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Проверка здоровья всех бирж"""
        results = {}
        
        for exchange_name, exchange in self.exchanges.items():
            try:
                start_time = datetime.utcnow()
                
                # Простая проверка - получение информации о бирже
                await exchange.fetch_status()
                
                response_time = (datetime.utcnow() - start_time).total_seconds()
                
                results[exchange_name] = {
                    'status': 'healthy',
                    'response_time': response_time,
                    'last_check': datetime.utcnow().isoformat()
                }
                
                self.exchange_health[exchange_name] = ExchangeStatus.HEALTHY
                
            except Exception as e:
                results[exchange_name] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'last_check': datetime.utcnow().isoformat()
                }
                
                self.exchange_health[exchange_name] = ExchangeStatus.UNAVAILABLE
        
        return results
    
    async def get_supported_symbols(self, exchange_name: Optional[str] = None) -> List[str]:
        """Получение списка поддерживаемых символов"""
        target_exchange = exchange_name or self.fallback_order[0]
        
        if target_exchange not in self.exchanges:
            return []
        
        try:
            exchange = self.exchanges[target_exchange]
            
            if not exchange.markets:
                await exchange.load_markets()
            
            # Фильтруем только USDT пары для криптовалют
            symbols = [
                symbol for symbol in exchange.markets.keys()
                if '/USDT' in symbol and not any(
                    excluded in symbol for excluded in ['BULL', 'BEAR', 'UP', 'DOWN']
                )
            ]
            
            return sorted(symbols)
            
        except Exception as e:
            logger.error(f"Error getting supported symbols: {e}")
            return []
    
    def get_exchange_stats(self) -> Dict[str, Any]:
        """Получение статистики бирж"""
        stats = {
            'total_exchanges': len(self.exchanges),
            'healthy_exchanges': sum(
                1 for status in self.exchange_health.values() 
                if status == ExchangeStatus.HEALTHY
            ),
            'exchange_details': {}
        }
        
        for exchange_name in self.exchanges.keys():
            config = self.exchange_configs[exchange_name]
            health = self.exchange_health[exchange_name]
            
            stats['exchange_details'][exchange_name] = {
                'status': health.value,
                'priority': config.priority,
                'rate_limit': config.rate_limit,
                'timeout': config.timeout
            }
        
        return stats
    
    async def close_all(self):
        """Закрытие всех соединений с биржами"""
        for exchange in self.exchanges.values():
            try:
                await exchange.close()
            except Exception as e:
                logger.error(f"Error closing exchange: {e}")

# Глобальный экземпляр сервиса
ccxt_service = CCXTService()

# === UTILITY FUNCTIONS ===
def normalize_symbol(symbol: str) -> str:
    """Нормализация символа для CCXT"""
    # Преобразуем BTCUSDT -> BTC/USDT
    if '/' not in symbol and len(symbol) >= 6:
        # Предполагаем что последние 4 символа - это quote currency
        if symbol.endswith('USDT'):
            base = symbol[:-4]
            quote = symbol[-4:]
            return f"{base}/{quote}"
        elif symbol.endswith('BTC') or symbol.endswith('ETH'):
            base = symbol[:-3]
            quote = symbol[-3:]
            return f"{base}/{quote}"
    
    return symbol

def ccxt_to_chartgenius_format(ohlcv_data: List[List[float]]) -> List[Dict[str, Any]]:
    """Преобразование CCXT формата в формат ChartGenius"""
    result = []
    
    for candle in ohlcv_data:
        if len(candle) >= 5:
            result.append({
                'timestamp': int(candle[0]),
                'open': float(candle[1]),
                'high': float(candle[2]),
                'low': float(candle[3]),
                'close': float(candle[4]),
                'volume': float(candle[5]) if len(candle) > 5 else 0.0
            })
    
    return result
