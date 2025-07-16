#!/usr/bin/env python3
"""
Скрипт для тестирования ChartGenius v3 Backend
Проверяет основные компоненты и API endpoints
"""

import asyncio
import json
import sys
from typing import Dict, Any

import httpx
from config.config import get_settings
from config.database import init_database, close_database
from services.crypto_compare_provider import CryptoCompareProvider
from services.chatgpt_analyzer import ChatGPTAnalyzer
from services.cache_service import cache_service

settings = get_settings()


class BackendTester:
    """Тестер backend компонентов"""
    
    def __init__(self):
        self.base_url = f"http://localhost:{settings.api_port}"
        self.results = {}
    
    async def run_all_tests(self):
        """Запуск всех тестов"""
        print("🧪 Запуск тестов ChartGenius v3 Backend\n")
        
        tests = [
            ("Database Connection", self.test_database),
            ("CryptoCompare API", self.test_cryptocompare),
            ("AI Analyzer", self.test_ai_analyzer),
            ("Cache Service", self.test_cache),
            ("Health Endpoints", self.test_health_endpoints),
            ("Analysis Endpoint", self.test_analysis_endpoint),
        ]
        
        for test_name, test_func in tests:
            print(f"🔍 Тестирование: {test_name}")
            try:
                result = await test_func()
                self.results[test_name] = {"status": "✅ PASS", "details": result}
                print(f"   ✅ {test_name}: PASS")
            except Exception as e:
                self.results[test_name] = {"status": "❌ FAIL", "error": str(e)}
                print(f"   ❌ {test_name}: FAIL - {e}")
            print()
        
        self.print_summary()
    
    async def test_database(self) -> Dict[str, Any]:
        """Тест подключения к базе данных"""
        await init_database()
        
        from config.database import execute_one
        result = await execute_one("SELECT 1 FROM DUAL")
        
        await close_database()
        
        return {"connection": "OK", "test_query": result[0] if result else None}
    
    async def test_cryptocompare(self) -> Dict[str, Any]:
        """Тест CryptoCompare API"""
        provider = CryptoCompareProvider()
        
        # Тест получения OHLCV данных
        ohlcv_data = await provider.get_ohlcv_data("BTCUSDT", "4h", 10)
        
        # Тест получения текущей цены
        current_price = await provider.get_current_price("BTCUSDT")
        
        return {
            "ohlcv_data_count": len(ohlcv_data),
            "current_price": current_price,
            "api_working": len(ohlcv_data) > 0
        }
    
    async def test_ai_analyzer(self) -> Dict[str, Any]:
        """Тест AI анализатора"""
        analyzer = ChatGPTAnalyzer()
        
        # Тест подключения
        connection_ok = await analyzer.test_connection()
        
        # Тест анализа (с mock данными)
        mock_ohlcv = [
            {
                "timestamp": 1704067200,
                "datetime": "2024-01-01T00:00:00",
                "open": 42000.0,
                "high": 42500.0,
                "low": 41800.0,
                "close": 42200.0,
                "volume": 1000000.0
            }
        ] * 50  # 50 свечей
        
        analysis_result = await analyzer.analyze_ohlcv_data(
            ohlcv_data=mock_ohlcv,
            symbol="BTCUSDT",
            interval="4h"
        )
        
        return {
            "connection": connection_ok,
            "analysis_generated": analysis_result is not None,
            "analysis_objects_count": len(analysis_result) if analysis_result else 0
        }
    
    async def test_cache(self) -> Dict[str, Any]:
        """Тест сервиса кэширования"""
        # Тест записи и чтения
        test_key = "test_key"
        test_value = {"test": "data", "timestamp": "2025-01-09"}
        
        # Запись
        set_result = await cache_service.set(test_key, test_value, 60)
        
        # Чтение
        get_result = await cache_service.get(test_key)
        
        # Проверка существования
        exists_result = await cache_service.exists(test_key)
        
        # Удаление
        delete_result = await cache_service.delete(test_key)
        
        # Статистика
        stats = await cache_service.get_stats()
        
        return {
            "set_success": set_result,
            "get_success": get_result == test_value,
            "exists_success": exists_result,
            "delete_success": delete_result,
            "stats": stats
        }
    
    async def test_health_endpoints(self) -> Dict[str, Any]:
        """Тест health endpoints"""
        async with httpx.AsyncClient() as client:
            # Простой health check
            health_response = await client.get(f"{self.base_url}/health")
            
            # Детальный health check
            api_health_response = await client.get(f"{self.base_url}/api/health")
            
            return {
                "health_status": health_response.status_code,
                "health_data": health_response.json() if health_response.status_code == 200 else None,
                "api_health_status": api_health_response.status_code,
                "api_health_data": api_health_response.json() if api_health_response.status_code == 200 else None
            }
    
    async def test_analysis_endpoint(self) -> Dict[str, Any]:
        """Тест endpoint анализа (без аутентификации)"""
        async with httpx.AsyncClient() as client:
            # Тест без аутентификации (должен вернуть 401)
            analysis_response = await client.post(
                f"{self.base_url}/api/analysis/analyze",
                json={
                    "symbol": "BTCUSDT",
                    "interval": "4h",
                    "days": 15
                }
            )
            
            return {
                "endpoint_accessible": True,
                "auth_required": analysis_response.status_code == 401,
                "response_status": analysis_response.status_code
            }
    
    def print_summary(self):
        """Печать сводки результатов"""
        print("=" * 60)
        print("📊 СВОДКА РЕЗУЛЬТАТОВ ТЕСТИРОВАНИЯ")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for test_name, result in self.results.items():
            status = result["status"]
            print(f"{status} {test_name}")
            
            if "✅" in status:
                passed += 1
            else:
                failed += 1
                if "error" in result:
                    print(f"    Ошибка: {result['error']}")
        
        print("\n" + "=" * 60)
        print(f"📈 ИТОГО: {passed} прошли, {failed} провалились")
        
        if failed == 0:
            print("🎉 Все тесты прошли успешно! Backend готов к работе.")
        else:
            print("⚠️ Некоторые тесты провалились. Проверьте конфигурацию.")
        
        print("=" * 60)


async def main():
    """Основная функция"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
ChartGenius v3 Backend Tester

Использование:
    python test_backend.py              # Запуск всех тестов
    python test_backend.py --help       # Показать справку

Тесты:
    - Database Connection    # Подключение к Oracle AJD
    - CryptoCompare API     # Получение OHLCV данных
    - AI Analyzer           # OpenAI анализатор
    - Cache Service         # Redis/Memory кэш
    - Health Endpoints      # Health check endpoints
    - Analysis Endpoint     # Основной API endpoint

Требования:
    - Настроенный .env файл
    - Доступ к Oracle AJD
    - OpenAI API ключ
    - CryptoCompare API ключ
    - (Опционально) Redis сервер
        """)
        return
    
    tester = BackendTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
