#!/usr/bin/env python3
# 🧪 Test Script for ChartGenius Telegram Bot
# Версия: 1.1.0-dev
# Скрипт для тестирования бота локально

import asyncio
import aiohttp
import json
import os
from datetime import datetime

# Конфигурация
BOT_TOKEN = "7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0"
ADMIN_USER_ID = "299820674"
TEST_USER_ID = "123456789"
BACKEND_URL = "http://localhost:8001"
BOT_URL = "http://localhost:8002"

class BotTester:
    """Класс для тестирования Telegram бота"""
    
    def __init__(self):
        self.session = None
        self.test_results = []
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_bot_info(self):
        """Тест получения информации о боте"""
        print("🔍 Тестирование getMe...")
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ok'):
                        bot_info = data['result']
                        print(f"✅ Бот активен: @{bot_info['username']}")
                        print(f"   ID: {bot_info['id']}")
                        print(f"   Имя: {bot_info['first_name']}")
                        return True
                    else:
                        print(f"❌ Ошибка API: {data}")
                        return False
                else:
                    print(f"❌ HTTP ошибка: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Исключение: {e}")
            return False
    
    async def test_webhook_info(self):
        """Тест информации о webhook"""
        print("\n🔍 Тестирование getWebhookInfo...")
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ok'):
                        webhook_info = data['result']
                        print(f"✅ Webhook URL: {webhook_info.get('url', 'Не установлен')}")
                        print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
                        print(f"   Last error: {webhook_info.get('last_error_message', 'Нет ошибок')}")
                        return True
                    else:
                        print(f"❌ Ошибка API: {data}")
                        return False
                else:
                    print(f"❌ HTTP ошибка: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Исключение: {e}")
            return False
    
    async def test_backend_health(self):
        """Тест здоровья backend"""
        print("\n🔍 Тестирование backend health...")
        try:
            url = f"{BACKEND_URL}/health"
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    print("✅ Backend доступен")
                    return True
                else:
                    print(f"❌ Backend недоступен: {response.status}")
                    return False
        except asyncio.TimeoutError:
            print("❌ Backend timeout")
            return False
        except Exception as e:
            print(f"❌ Backend ошибка: {e}")
            return False
    
    async def test_bot_health(self):
        """Тест здоровья бота"""
        print("\n🔍 Тестирование bot health...")
        try:
            url = f"{BOT_URL}/health"
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    print("✅ Bot webhook доступен")
                    return True
                else:
                    print(f"❌ Bot webhook недоступен: {response.status}")
                    return False
        except asyncio.TimeoutError:
            print("❌ Bot webhook timeout")
            return False
        except Exception as e:
            print(f"❌ Bot webhook ошибка: {e}")
            return False
    
    async def test_send_message(self, user_id: str, text: str):
        """Тест отправки сообщения"""
        print(f"\n🔍 Тестирование отправки сообщения пользователю {user_id}...")
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": user_id,
                "text": text,
                "parse_mode": "HTML"
            }
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('ok'):
                        print("✅ Сообщение отправлено")
                        return True
                    else:
                        print(f"❌ Ошибка отправки: {result}")
                        return False
                else:
                    print(f"❌ HTTP ошибка: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Исключение: {e}")
            return False
    
    async def test_webhook_simulation(self):
        """Симуляция webhook запроса"""
        print("\n🔍 Тестирование webhook симуляции...")
        try:
            # Симулируем /start команду
            webhook_data = {
                "update_id": 123456789,
                "message": {
                    "message_id": 1,
                    "from": {
                        "id": int(TEST_USER_ID),
                        "is_bot": False,
                        "first_name": "Test",
                        "username": "testuser"
                    },
                    "chat": {
                        "id": int(TEST_USER_ID),
                        "first_name": "Test",
                        "username": "testuser",
                        "type": "private"
                    },
                    "date": int(datetime.now().timestamp()),
                    "text": "/start",
                    "entities": [
                        {
                            "offset": 0,
                            "length": 6,
                            "type": "bot_command"
                        }
                    ]
                }
            }
            
            url = f"{BOT_URL}/webhook"
            async with self.session.post(url, json=webhook_data, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    print("✅ Webhook обработан успешно")
                    return True
                else:
                    print(f"❌ Webhook ошибка: {response.status}")
                    text = await response.text()
                    print(f"   Ответ: {text}")
                    return False
        except asyncio.TimeoutError:
            print("❌ Webhook timeout")
            return False
        except Exception as e:
            print(f"❌ Webhook исключение: {e}")
            return False
    
    async def run_all_tests(self):
        """Запуск всех тестов"""
        print("🚀 Запуск тестов ChartGenius Telegram Bot")
        print("=" * 50)
        
        tests = [
            ("Bot Info", self.test_bot_info()),
            ("Webhook Info", self.test_webhook_info()),
            ("Backend Health", self.test_backend_health()),
            ("Bot Health", self.test_bot_health()),
            ("Send Test Message", self.test_send_message(ADMIN_USER_ID, "🧪 Тестовое сообщение от ChartGenius")),
            ("Webhook Simulation", self.test_webhook_simulation())
        ]
        
        results = []
        for test_name, test_coro in tests:
            try:
                result = await test_coro
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ Тест {test_name} упал с ошибкой: {e}")
                results.append((test_name, False))
        
        # Результаты
        print("\n" + "=" * 50)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:.<30} {status}")
            if result:
                passed += 1
        
        print("-" * 50)
        print(f"Пройдено: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
            return True
        else:
            print("⚠️  ЕСТЬ ПРОБЛЕМЫ, ТРЕБУЮЩИЕ ВНИМАНИЯ")
            return False

async def main():
    """Главная функция"""
    async with BotTester() as tester:
        success = await tester.run_all_tests()
        
        if success:
            print("\n✅ Бот готов к деплою в production!")
        else:
            print("\n❌ Исправьте проблемы перед деплоем")
            exit(1)

if __name__ == "__main__":
    asyncio.run(main())
