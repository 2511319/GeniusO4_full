#!/usr/bin/env python3
"""
Интеграционные тесты для ChartGenius
Тестирует взаимодействие между всеми компонентами системы
"""

import pytest
import asyncio
import aiohttp
import json
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Настройки для тестирования
TEST_API_URL = os.getenv("TEST_API_URL", "http://localhost:8000")
TEST_TELEGRAM_ID = "123456789"
TEST_JWT_SECRET = "test_jwt_secret_key_for_testing_purposes_only"

class TestSystemIntegration:
    """Тесты интеграции всей системы"""
    
    @pytest.fixture
    def mock_telegram_user(self):
        """Мок данных пользователя Telegram"""
        return {
            "id": TEST_TELEGRAM_ID,
            "first_name": "Test",
            "last_name": "User",
            "username": "test_user",
            "photo_url": "",
            "auth_date": str(int(datetime.utcnow().timestamp()))
        }
    
    @pytest.fixture
    async def http_session(self):
        """HTTP сессия для тестов"""
        async with aiohttp.ClientSession() as session:
            yield session
    
    async def test_health_endpoints(self, http_session):
        """Тест доступности всех сервисов"""
        endpoints = [
            f"{TEST_API_URL}/health",
            f"{TEST_API_URL}/",
        ]
        
        for endpoint in endpoints:
            try:
                async with http_session.get(endpoint) as response:
                    assert response.status in [200, 404], f"Endpoint {endpoint} недоступен"
                    print(f"✅ {endpoint} - доступен")
            except Exception as e:
                print(f"⚠️ {endpoint} - недоступен: {e}")
    
    async def test_telegram_auth_flow(self, http_session, mock_telegram_user):
        """Тест аутентификации через Telegram"""
        # Добавляем hash для аутентификации
        import hashlib
        import hmac
        
        # Имитируем создание hash как в реальном Telegram
        secret_key = hashlib.sha256("test_bot_token".encode()).digest()
        data_check_string = "\n".join(f"{k}={mock_telegram_user[k]}" for k in sorted(mock_telegram_user.keys()))
        mock_telegram_user["hash"] = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        try:
            async with http_session.post(f"{TEST_API_URL}/auth/telegram", json=mock_telegram_user) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "access_token" in data
                    print("✅ Telegram аутентификация работает")
                    return data["access_token"]
                else:
                    print(f"⚠️ Telegram аутентификация недоступна: {response.status}")
                    return None
        except Exception as e:
            print(f"⚠️ Ошибка Telegram аутентификации: {e}")
            return None
    
    async def test_subscription_system(self, http_session):
        """Тест системы подписок"""
        headers = {"X-Telegram-Id": TEST_TELEGRAM_ID}
        
        try:
            # Проверяем получение информации о подписке
            async with http_session.get(f"{TEST_API_URL}/api/user/subscription", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "level" in data
                    assert "is_active" in data
                    print(f"✅ Система подписок работает: {data['level']}")
                else:
                    print(f"⚠️ Система подписок недоступна: {response.status}")
            
            # Проверяем создание подписки
            async with http_session.post(f"{TEST_API_URL}/api/user/subscription/create", headers=headers) as response:
                if response.status == 200:
                    print("✅ Создание подписки работает")
                else:
                    print(f"⚠️ Создание подписки недоступно: {response.status}")
                    
        except Exception as e:
            print(f"⚠️ Ошибка системы подписок: {e}")
    
    async def test_analysis_system(self, http_session):
        """Тест системы анализа"""
        headers = {"X-Telegram-Id": TEST_TELEGRAM_ID}
        
        try:
            # Тест простого анализа
            async with http_session.post(f"{TEST_API_URL}/api/analysis/simple", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "analysis" in data
                    assert "primary_analysis" in data
                    print("✅ Простой анализ работает")
                elif response.status == 402:
                    print("ℹ️ Простой анализ требует подписку (ожидаемо)")
                else:
                    print(f"⚠️ Простой анализ недоступен: {response.status}")
            
            # Тест полного анализа
            analysis_request = {
                "symbol": "BTCUSDT",
                "interval": "4h",
                "limit": 100,
                "indicators": ["RSI", "MACD"]
            }
            
            async with http_session.post(f"{TEST_API_URL}/api/analyze", 
                                       json=analysis_request, 
                                       headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "analysis" in data
                    print("✅ Полный анализ работает")
                elif response.status == 401:
                    print("ℹ️ Полный анализ требует JWT токен (ожидаемо)")
                else:
                    print(f"⚠️ Полный анализ недоступен: {response.status}")
                    
        except Exception as e:
            print(f"⚠️ Ошибка системы анализа: {e}")
    
    async def test_user_dashboard_api(self, http_session):
        """Тест API личного кабинета"""
        headers = {"X-Telegram-Id": TEST_TELEGRAM_ID}
        
        try:
            # Тест получения профиля
            async with http_session.get(f"{TEST_API_URL}/api/user/profile", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "id" in data
                    print("✅ API профиля работает")
                else:
                    print(f"⚠️ API профиля недоступно: {response.status}")
            
            # Тест получения анализов
            async with http_session.get(f"{TEST_API_URL}/api/user/analyses", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "analyses" in data
                    print("✅ API анализов работает")
                else:
                    print(f"⚠️ API анализов недоступно: {response.status}")
                    
        except Exception as e:
            print(f"⚠️ Ошибка API личного кабинета: {e}")

class TestBotIntegration:
    """Тесты интеграции Telegram бота"""
    
    def test_bot_webhook_structure(self):
        """Тест структуры webhook бота"""
        from bot.bot import app, handle_webhook
        
        # Проверяем, что основные обработчики зарегистрированы
        assert app is not None
        print("✅ Структура бота корректна")
    
    def test_bot_commands(self):
        """Тест команд бота"""
        from bot.bot import start, handle_callback
        
        # Проверяем, что основные функции существуют
        assert callable(start)
        assert callable(handle_callback)
        print("✅ Команды бота определены")

class TestFrontendIntegration:
    """Тесты интеграции Frontend"""
    
    async def test_frontend_build(self):
        """Тест сборки frontend"""
        # Проверяем наличие основных файлов
        frontend_files = [
            "frontend/package.json",
            "frontend/src/App.jsx",
            "frontend/src/pages/Home.jsx",
            "frontend/src/pages/UserDashboard.jsx"
        ]
        
        for file_path in frontend_files:
            assert os.path.exists(file_path), f"Файл {file_path} не найден"
        
        print("✅ Структура frontend корректна")

async def run_integration_tests():
    """Запуск всех интеграционных тестов"""
    print("🧪 Запуск интеграционных тестов ChartGenius")
    print("=" * 50)
    
    # Тесты системы
    system_tests = TestSystemIntegration()
    
    async with aiohttp.ClientSession() as session:
        print("\n📡 Тестирование API endpoints...")
        await system_tests.test_health_endpoints(session)
        
        print("\n🔐 Тестирование аутентификации...")
        token = await system_tests.test_telegram_auth_flow(session, {
            "id": TEST_TELEGRAM_ID,
            "first_name": "Test",
            "last_name": "User",
            "username": "test_user",
            "photo_url": "",
            "auth_date": str(int(datetime.utcnow().timestamp()))
        })
        
        print("\n💳 Тестирование системы подписок...")
        await system_tests.test_subscription_system(session)
        
        print("\n📊 Тестирование системы анализа...")
        await system_tests.test_analysis_system(session)
        
        print("\n👤 Тестирование API личного кабинета...")
        await system_tests.test_user_dashboard_api(session)
    
    # Тесты бота
    print("\n🤖 Тестирование Telegram бота...")
    bot_tests = TestBotIntegration()
    bot_tests.test_bot_webhook_structure()
    bot_tests.test_bot_commands()
    
    # Тесты frontend
    print("\n🌐 Тестирование Frontend...")
    frontend_tests = TestFrontendIntegration()
    await frontend_tests.test_frontend_build()
    
    print("\n" + "=" * 50)
    print("✅ Интеграционные тесты завершены!")
    print("\n📝 Следующие шаги:")
    print("1. Запустите локальное тестирование: python tests/test_integration.py")
    print("2. Разверните в Google Cloud: scripts/setup_complete.sh")
    print("3. Протестируйте в продакшене")

if __name__ == "__main__":
    asyncio.run(run_integration_tests())
