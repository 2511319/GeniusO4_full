# 🧪 Tests for CCXT Service
# Версия: 1.1.0-dev
# Тесты для сервиса интеграции с биржами

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from backend.services.ccxt_service import CCXTService, ExchangeStatus, normalize_symbol, ccxt_to_chartgenius_format


class TestCCXTService:
    """Тесты для CCXTService"""
    
    @pytest.fixture
    def service(self):
        """Фикстура для создания экземпляра сервиса"""
        with patch('backend.services.ccxt_service.ccxt'):
            service = CCXTService()
            return service
    
    @pytest.fixture
    def mock_exchange(self):
        """Мок для CCXT биржи"""
        exchange = AsyncMock()
        exchange.id = "binance"
        exchange.markets = {
            "BTC/USDT": {"symbol": "BTC/USDT"},
            "ETH/USDT": {"symbol": "ETH/USDT"}
        }
        return exchange
    
    @pytest.mark.asyncio
    async def test_initialize_exchanges(self, service):
        """Тест инициализации бирж"""
        with patch('backend.services.ccxt_service.ccxt.binance') as mock_binance:
            mock_exchange = AsyncMock()
            mock_binance.return_value = mock_exchange
            
            await service.initialize_exchanges()
            
            assert "binance" in service.exchanges
            mock_binance.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_ohlcv_data_success(self, service, mock_exchange):
        """Тест успешного получения OHLCV данных"""
        # Настраиваем сервис
        service.exchanges["binance"] = mock_exchange
        service.exchange_health["binance"] = ExchangeStatus.HEALTHY
        
        # Мокаем данные
        ohlcv_data = [
            [1640995200000, 47000, 48000, 46500, 47500, 1000],
            [1640998800000, 47500, 48500, 47000, 48000, 1200]
        ]
        mock_exchange.fetch_ohlcv.return_value = ohlcv_data
        mock_exchange.load_markets.return_value = {"BTC/USDT": {}}
        
        # Мокаем Redis
        redis_mock = AsyncMock()
        redis_mock.get.return_value = None
        redis_mock.setex = AsyncMock()
        service.get_redis = AsyncMock(return_value=redis_mock)
        
        # Тестируем получение данных
        result = await service.get_ohlcv_data("BTC/USDT", "1h", 100)
        
        # Проверяем результат
        assert result is not None
        assert len(result) == 2
        mock_exchange.fetch_ohlcv.assert_called_once_with("BTC/USDT", "1h", limit=100)
    
    @pytest.mark.asyncio
    async def test_get_ohlcv_data_from_cache(self, service):
        """Тест получения OHLCV данных из кэша"""
        # Мокаем Redis с кэшированными данными
        cached_data = [[1640995200000, 47000, 48000, 46500, 47500, 1000]]
        redis_mock = AsyncMock()
        redis_mock.get.return_value = str(cached_data).encode()
        service.get_redis = AsyncMock(return_value=redis_mock)
        
        # Тестируем получение данных
        result = await service.get_ohlcv_data("BTC/USDT", "1h", 100)
        
        # Проверяем результат
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_get_ohlcv_data_fallback(self, service):
        """Тест fallback между биржами"""
        # Настраиваем биржи
        binance_mock = AsyncMock()
        coinbase_mock = AsyncMock()
        
        service.exchanges["binance"] = binance_mock
        service.exchanges["coinbase"] = coinbase_mock
        service.exchange_health["binance"] = ExchangeStatus.UNAVAILABLE
        service.exchange_health["coinbase"] = ExchangeStatus.HEALTHY
        
        # Мокаем Redis
        redis_mock = AsyncMock()
        redis_mock.get.return_value = None
        redis_mock.setex = AsyncMock()
        service.get_redis = AsyncMock(return_value=redis_mock)
        
        # Мокаем данные только для coinbase
        ohlcv_data = [[1640995200000, 47000, 48000, 46500, 47500, 1000]]
        coinbase_mock.fetch_ohlcv.return_value = ohlcv_data
        coinbase_mock.load_markets.return_value = {"BTC/USDT": {}}
        
        # Тестируем получение данных
        result = await service.get_ohlcv_data("BTC/USDT", "1h", 100)
        
        # Проверяем что binance был пропущен, а coinbase использован
        binance_mock.fetch_ohlcv.assert_not_called()
        coinbase_mock.fetch_ohlcv.assert_called_once()
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_get_ticker_data_success(self, service, mock_exchange):
        """Тест успешного получения ticker данных"""
        # Настраиваем сервис
        service.exchanges["binance"] = mock_exchange
        service.exchange_health["binance"] = ExchangeStatus.HEALTHY
        
        # Мокаем ticker данные
        ticker_data = {
            "symbol": "BTC/USDT",
            "last": 47500,
            "bid": 47450,
            "ask": 47550,
            "baseVolume": 1000,
            "change": 500,
            "percentage": 1.06,
            "timestamp": 1640995200000
        }
        mock_exchange.fetch_ticker.return_value = ticker_data
        
        # Мокаем Redis
        redis_mock = AsyncMock()
        redis_mock.get.return_value = None
        redis_mock.setex = AsyncMock()
        service.get_redis = AsyncMock(return_value=redis_mock)
        
        # Тестируем получение ticker
        result = await service.get_ticker_data("BTC/USDT")
        
        # Проверяем результат
        assert result is not None
        assert result["symbol"] == "BTC/USDT"
        assert result["last"] == 47500
        mock_exchange.fetch_ticker.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_all(self, service, mock_exchange):
        """Тест проверки здоровья всех бирж"""
        # Настраиваем сервис
        service.exchanges["binance"] = mock_exchange
        service.exchange_health["binance"] = ExchangeStatus.HEALTHY
        
        # Мокаем успешный health check
        mock_exchange.fetch_ticker.return_value = {"symbol": "BTC/USDT"}
        
        # Тестируем health check
        result = await service.health_check_all()
        
        # Проверяем результат
        assert "binance" in result
        assert result["binance"].status == ExchangeStatus.HEALTHY
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, service, mock_exchange):
        """Тест health check при ошибке биржи"""
        # Настраиваем сервис
        service.exchanges["binance"] = mock_exchange
        service.exchange_health["binance"] = ExchangeStatus.HEALTHY
        
        # Мокаем ошибку
        mock_exchange.fetch_ticker.side_effect = Exception("Network error")
        
        # Тестируем health check
        result = await service.health_check_all()
        
        # Проверяем результат
        assert "binance" in result
        assert result["binance"].status == ExchangeStatus.UNAVAILABLE
    
    @pytest.mark.asyncio
    async def test_get_supported_symbols(self, service, mock_exchange):
        """Тест получения поддерживаемых символов"""
        # Настраиваем сервис
        service.exchanges["binance"] = mock_exchange
        
        # Мокаем markets
        mock_exchange.load_markets.return_value = {
            "BTC/USDT": {},
            "ETH/USDT": {},
            "ADA/USDT": {}
        }
        mock_exchange.markets = {
            "BTC/USDT": {},
            "ETH/USDT": {},
            "ADA/USDT": {}
        }
        
        # Тестируем получение символов
        result = await service.get_supported_symbols("binance")
        
        # Проверяем результат
        assert len(result) == 3
        assert "BTC/USDT" in result
        assert "ETH/USDT" in result
        assert "ADA/USDT" in result
    
    def test_normalize_symbol(self):
        """Тест нормализации символов"""
        # Тестируем различные форматы
        assert normalize_symbol("BTCUSDT") == "BTC/USDT"
        assert normalize_symbol("ETHBTC") == "ETH/BTC"
        assert normalize_symbol("BTC/USDT") == "BTC/USDT"
        assert normalize_symbol("ADAETH") == "ADA/ETH"
    
    def test_ccxt_to_chartgenius_format(self):
        """Тест конвертации CCXT формата в ChartGenius формат"""
        # Тестовые данные CCXT
        ccxt_data = [
            [1640995200000, 47000, 48000, 46500, 47500, 1000],
            [1640998800000, 47500, 48500, 47000, 48000, 1200]
        ]
        
        # Конвертируем
        result = ccxt_to_chartgenius_format(ccxt_data)
        
        # Проверяем результат
        assert len(result) == 2
        assert result[0]["timestamp"] == 1640995200000
        assert result[0]["open"] == 47000
        assert result[0]["high"] == 48000
        assert result[0]["low"] == 46500
        assert result[0]["close"] == 47500
        assert result[0]["volume"] == 1000
    
    @pytest.mark.asyncio
    async def test_close_all_exchanges(self, service, mock_exchange):
        """Тест закрытия всех соединений"""
        # Настраиваем сервис
        service.exchanges["binance"] = mock_exchange
        mock_exchange.close = AsyncMock()
        
        # Тестируем закрытие
        await service.close_all_exchanges()
        
        # Проверяем что close был вызван
        mock_exchange.close.assert_called_once()


# Интеграционные тесты
class TestCCXTServiceIntegration:
    """Интеграционные тесты для CCXTService"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_exchange_connection(self):
        """Тест реального подключения к бирже"""
        # Этот тест требует интернет соединения
        pytest.skip("Requires internet connection and may hit rate limits")
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_redis_caching(self):
        """Тест кэширования в Redis"""
        # Этот тест требует запущенного Redis
        pytest.skip("Requires running Redis instance")


# Тесты утилитарных функций
class TestUtilityFunctions:
    """Тесты утилитарных функций"""
    
    def test_normalize_symbol_edge_cases(self):
        """Тест граничных случаев нормализации символов"""
        # Пустая строка
        assert normalize_symbol("") == ""
        
        # Короткие символы
        assert normalize_symbol("BTC") == "BTC"
        
        # Уже нормализованные
        assert normalize_symbol("BTC/USDT") == "BTC/USDT"
        
        # Специальные случаи
        assert normalize_symbol("BTCUSDT") == "BTC/USDT"
        assert normalize_symbol("1000SHIBUSDT") == "1000SHIB/USDT"
    
    def test_ccxt_to_chartgenius_format_edge_cases(self):
        """Тест граничных случаев конвертации формата"""
        # Пустой список
        assert ccxt_to_chartgenius_format([]) == []
        
        # Неполные данные
        incomplete_data = [[1640995200000, 47000, 48000]]
        result = ccxt_to_chartgenius_format(incomplete_data)
        assert len(result) == 0  # Должен пропустить неполные записи
        
        # Данные без volume
        no_volume_data = [[1640995200000, 47000, 48000, 46500, 47500]]
        result = ccxt_to_chartgenius_format(no_volume_data)
        assert len(result) == 1
        assert result[0]["volume"] == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
