# 📊 Market Data Service for ChartGenius
# Версия: 1.1.0-dev
# Unified market data service with CoinGecko + CCXT fallback

import os
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import pandas as pd
from dataclasses import dataclass
from enum import Enum

from backend.services.crypto_compare_provider import fetch_ohlcv as fetch_coingecko_ohlcv
from backend.services.ccxt_service import ccxt_service, normalize_symbol, ccxt_to_chartgenius_format
from backend.services.metrics_service import metrics

logger = logging.getLogger(__name__)

class DataSource(Enum):
    """Источники рыночных данных"""
    COINGECKO = "coingecko"
    CCXT_BINANCE = "ccxt_binance"
    CCXT_COINBASE = "ccxt_coinbase"
    CCXT_KRAKEN = "ccxt_kraken"
    CCXT_BYBIT = "ccxt_bybit"

@dataclass
class MarketDataConfig:
    """Конфигурация источника данных"""
    source: DataSource
    priority: int
    timeout: float
    enabled: bool = True

class MarketDataService:
    """
    Унифицированный сервис для получения рыночных данных
    с автоматическим fallback между источниками
    """
    
    def __init__(self):
        # Конфигурация источников по приоритету
        self.data_sources = [
            MarketDataConfig(DataSource.COINGECKO, 1, 15.0),
            MarketDataConfig(DataSource.CCXT_BINANCE, 2, 10.0),
            MarketDataConfig(DataSource.CCXT_COINBASE, 3, 15.0),
            MarketDataConfig(DataSource.CCXT_KRAKEN, 4, 20.0),
            MarketDataConfig(DataSource.CCXT_BYBIT, 5, 10.0),
        ]
        
        # Инициализируем CCXT сервис
        asyncio.create_task(self._initialize_ccxt())
        
        logger.info("Market Data Service инициализирован")
    
    async def _initialize_ccxt(self):
        """Инициализация CCXT сервиса"""
        try:
            await ccxt_service.initialize_exchanges()
            logger.info("CCXT exchanges инициализированы")
        except Exception as e:
            logger.error(f"Ошибка инициализации CCXT: {e}")
    
    async def get_ohlcv_data(self, symbol: str, interval: str = '4h', 
                           limit: int = 500, preferred_source: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Получение OHLCV данных с автоматическим fallback
        
        Args:
            symbol: Символ криптовалюты (BTCUSDT или BTC/USDT)
            interval: Временной интервал
            limit: Количество свечей
            preferred_source: Предпочитаемый источник данных
            
        Returns:
            pd.DataFrame: OHLCV данные или None
        """
        # Определяем порядок попыток
        sources_to_try = self._get_sources_order(preferred_source)
        
        for source_config in sources_to_try:
            if not source_config.enabled:
                continue
            
            try:
                logger.debug(f"Попытка получить данные из {source_config.source.value}")
                
                data = await self._fetch_from_source(
                    source_config.source, symbol, interval, limit
                )
                
                if data is not None and not data.empty:
                    logger.info(f"Данные получены из {source_config.source.value}: {len(data)} свечей")
                    
                    # Отслеживаем успешное получение данных
                    metrics.track_user_action(f'market_data_success_{source_config.source.value}', 'system')
                    
                    return data
                
            except Exception as e:
                logger.warning(f"Ошибка получения данных из {source_config.source.value}: {e}")
                metrics.track_error(type(e).__name__, f'market_data_{source_config.source.value}')
                continue
        
        logger.error(f"Не удалось получить данные для {symbol} из всех источников")
        metrics.track_user_action('market_data_all_failed', 'system')
        return None
    
    async def _fetch_from_source(self, source: DataSource, symbol: str, 
                               interval: str, limit: int) -> Optional[pd.DataFrame]:
        """Получение данных из конкретного источника"""
        
        if source == DataSource.COINGECKO:
            return await self._fetch_from_coingecko(symbol, interval, limit)
        
        elif source.value.startswith('ccxt_'):
            exchange_name = source.value.replace('ccxt_', '')
            return await self._fetch_from_ccxt(exchange_name, symbol, interval, limit)
        
        else:
            logger.error(f"Неизвестный источник данных: {source}")
            return None
    
    async def _fetch_from_coingecko(self, symbol: str, interval: str, limit: int) -> Optional[pd.DataFrame]:
        """Получение данных из CoinGecko (CryptoCompare)"""
        try:
            # Используем существующий CryptoCompare provider
            df = await fetch_coingecko_ohlcv(symbol, interval, limit)
            
            if df is not None and not df.empty:
                # Убеждаемся что у нас есть все необходимые колонки
                required_columns = ['Open Time', 'Close Time', 'Open', 'High', 'Low', 'Close', 'Volume']
                
                for col in required_columns:
                    if col not in df.columns:
                        logger.warning(f"Отсутствует колонка {col} в данных CoinGecko")
                        return None
                
                return df
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения данных из CoinGecko: {e}")
            return None
    
    async def _fetch_from_ccxt(self, exchange_name: str, symbol: str, 
                             interval: str, limit: int) -> Optional[pd.DataFrame]:
        """Получение данных из CCXT биржи"""
        try:
            # Нормализуем символ для CCXT
            normalized_symbol = normalize_symbol(symbol)
            
            # Получаем данные через CCXT сервис
            market_data_response = await ccxt_service.get_ohlcv_data(
                symbol=normalized_symbol,
                timeframe=interval,
                limit=limit,
                preferred_exchange=exchange_name
            )
            
            if market_data_response and market_data_response.data:
                # Конвертируем CCXT формат в pandas DataFrame
                df_data = ccxt_to_chartgenius_format(market_data_response.data)
                
                if df_data:
                    df = pd.DataFrame(df_data)
                    
                    # Конвертируем timestamp в datetime
                    df['Open Time'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df['Close Time'] = df['Open Time'] + pd.Timedelta(hours=4)  # Примерно для 4h интервала
                    
                    # Переименовываем колонки для совместимости
                    df.rename(columns={
                        'open': 'Open',
                        'high': 'High', 
                        'low': 'Low',
                        'close': 'Close',
                        'volume': 'Volume'
                    }, inplace=True)
                    
                    # Добавляем недостающие колонки
                    if 'Quote Asset Volume' not in df.columns:
                        df['Quote Asset Volume'] = df['Volume'] * df['Close']
                    
                    # Удаляем временную колонку timestamp
                    df.drop(columns=['timestamp'], inplace=True, errors='ignore')
                    
                    return df
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения данных из CCXT {exchange_name}: {e}")
            return None
    
    def _get_sources_order(self, preferred_source: Optional[str] = None) -> List[MarketDataConfig]:
        """Определение порядка источников для попыток"""
        sources = self.data_sources.copy()
        
        # Если указан предпочитаемый источник, ставим его первым
        if preferred_source:
            preferred_config = None
            remaining_sources = []
            
            for source_config in sources:
                if source_config.source.value == preferred_source:
                    preferred_config = source_config
                else:
                    remaining_sources.append(source_config)
            
            if preferred_config:
                return [preferred_config] + remaining_sources
        
        # Сортируем по приоритету
        return sorted(sources, key=lambda x: x.priority)
    
    async def get_ticker_data(self, symbol: str, preferred_source: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Получение текущих цен (ticker)
        
        Args:
            symbol: Символ криптовалюты
            preferred_source: Предпочитаемый источник
            
        Returns:
            Dict: Данные тикера или None
        """
        # Для ticker данных используем только CCXT (более актуальные данные)
        ccxt_sources = [s for s in self.data_sources if s.source.value.startswith('ccxt_')]
        
        if preferred_source and preferred_source.startswith('ccxt_'):
            exchange_name = preferred_source.replace('ccxt_', '')
        else:
            # Используем приоритетную CCXT биржу
            exchange_name = 'binance'
        
        try:
            normalized_symbol = normalize_symbol(symbol)
            ticker_data = await ccxt_service.get_ticker_data(normalized_symbol, exchange_name)
            
            if ticker_data:
                metrics.track_user_action(f'ticker_data_success_{exchange_name}', 'system')
                return ticker_data
            
        except Exception as e:
            logger.error(f"Ошибка получения ticker данных: {e}")
            metrics.track_error(type(e).__name__, 'ticker_data')
        
        return None
    
    async def get_supported_symbols(self, source: Optional[str] = None) -> List[str]:
        """
        Получение списка поддерживаемых символов
        
        Args:
            source: Источник данных
            
        Returns:
            List[str]: Список символов
        """
        try:
            if source and source.startswith('ccxt_'):
                exchange_name = source.replace('ccxt_', '')
                return await ccxt_service.get_supported_symbols(exchange_name)
            else:
                # Для CoinGecko возвращаем базовый список
                return [
                    'BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT',
                    'BNBUSDT', 'XRPUSDT', 'LTCUSDT', 'BCHUSDT', 'EOSUSDT'
                ]
                
        except Exception as e:
            logger.error(f"Ошибка получения поддерживаемых символов: {e}")
            return []
    
    async def get_data_sources_health(self) -> Dict[str, Any]:
        """Получение статуса здоровья всех источников данных"""
        health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'sources': {}
        }
        
        # Проверяем CoinGecko (простая проверка)
        try:
            test_data = await self._fetch_from_coingecko('BTCUSDT', '1h', 1)
            health_status['sources']['coingecko'] = {
                'status': 'healthy' if test_data is not None else 'unhealthy',
                'last_check': datetime.utcnow().isoformat()
            }
        except Exception as e:
            health_status['sources']['coingecko'] = {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }
        
        # Проверяем CCXT биржи
        try:
            ccxt_health = await ccxt_service.health_check_all()
            for exchange_name, health in ccxt_health.items():
                health_status['sources'][f'ccxt_{exchange_name}'] = {
                    'status': health.status.value,
                    'response_time': health.response_time,
                    'error_rate': health.error_rate,
                    'last_check': health.last_check.isoformat()
                }
        except Exception as e:
            logger.error(f"Ошибка проверки здоровья CCXT: {e}")
        
        return health_status

# Глобальный экземпляр сервиса
market_data_service = MarketDataService()
