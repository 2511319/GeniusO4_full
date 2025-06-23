#!/usr/bin/env python3
"""
Тест валидации Telegram WebApp данных
Проверяет различные сценарии валидации initData
"""

import requests
import json
import time
from urllib.parse import quote, unquote

# Конфигурация
API_URL = "https://chartgenius-api-169129692197.europe-west1.run.app"

def test_webapp_validation():
    """Тест валидации WebApp данных"""
    print("🧪 Тестирование валидации Telegram WebApp")
    print("=" * 60)
    
    # Тест 1: Пустые данные
    print("\n1. Тест с пустыми данными:")
    try:
        response = requests.post(
            f"{API_URL}/api/auth/webapp-token",
            headers={'Content-Type': 'text/plain'},
            data="",
            timeout=10
        )
        print(f"   Статус: {response.status_code}")
        if response.status_code == 400:
            print("   ✅ Правильно отклонил пустые данные")
        else:
            print("   ❌ Неожиданный ответ")
            print(f"   Ответ: {response.text}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 2: Неверные данные
    print("\n2. Тест с неверными данными:")
    try:
        response = requests.post(
            f"{API_URL}/api/auth/webapp-token",
            headers={'Content-Type': 'text/plain'},
            data="invalid_data",
            timeout=10
        )
        print(f"   Статус: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Правильно отклонил неверные данные")
        else:
            print("   ❌ Неожиданный ответ")
            print(f"   Ответ: {response.text}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 3: Данные без hash
    print("\n3. Тест с данными без hash:")
    try:
        test_data = "user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22Test%22%7D&auth_date=1640995200"
        response = requests.post(
            f"{API_URL}/api/auth/webapp-token",
            headers={'Content-Type': 'text/plain'},
            data=test_data,
            timeout=10
        )
        print(f"   Статус: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Правильно отклонил данные без hash")
        else:
            print("   ❌ Неожиданный ответ")
            print(f"   Ответ: {response.text}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 4: Данные с неверным hash
    print("\n4. Тест с неверным hash:")
    try:
        test_data = "user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22Test%22%7D&auth_date=1640995200&hash=invalid_hash"
        response = requests.post(
            f"{API_URL}/api/auth/webapp-token",
            headers={'Content-Type': 'text/plain'},
            data=test_data,
            timeout=10
        )
        print(f"   Статус: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Правильно отклонил данные с неверным hash")
            try:
                error_data = response.json()
                print(f"   Сообщение: {error_data.get('detail', 'Нет сообщения')}")
            except:
                print(f"   Ответ: {response.text}")
        else:
            print("   ❌ Неожиданный ответ")
            print(f"   Ответ: {response.text}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 5: Проверка логов (если доступны)
    print("\n5. Проверка версии API:")
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Версия API: {health_data.get('version', 'неизвестно')}")
            print(f"   Статус: {health_data.get('status', 'неизвестно')}")
        else:
            print(f"   ❌ Не удалось получить информацию о здоровье API")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("📋 АНАЛИЗ РЕЗУЛЬТАТОВ:")
    print("=" * 60)
    print("✅ Если все тесты показывают статус 401 - валидация работает правильно")
    print("❌ Если есть статусы 500 - есть проблемы в коде валидации")
    print("⚠️ Если есть статусы 400 - проблемы с форматом данных")
    
    print("\n💡 СЛЕДУЮЩИЕ ШАГИ:")
    print("1. Протестировать с РЕАЛЬНЫМИ данными от Telegram WebApp")
    print("2. Проверить логи Cloud Run для детальной диагностики")
    print("3. Убедиться, что токен бота правильный")

def test_real_scenario():
    """Симуляция реального сценария"""
    print("\n🎯 СИМУЛЯЦИЯ РЕАЛЬНОГО СЦЕНАРИЯ:")
    print("=" * 60)
    print("1. Пользователь открывает WebApp в Telegram")
    print("2. JavaScript получает window.Telegram.WebApp.initData")
    print("3. Frontend отправляет initData на /api/auth/webapp-token")
    print("4. API валидирует данные с помощью bot token")
    print("5. Если валидация успешна - возвращает JWT токен")
    print("6. Frontend сохраняет токен и перенаправляет в dashboard")
    
    print("\n🔍 ЧТО ПРОВЕРИТЬ В РЕАЛЬНОМ ТЕСТИРОВАНИИ:")
    print("- Откройте DevTools в Telegram WebApp")
    print("- Проверьте console.log с initData")
    print("- Проверьте Network tab для запроса к API")
    print("- Проверьте ответ API (200 = успех, 401 = ошибка валидации)")

if __name__ == "__main__":
    test_webapp_validation()
    test_real_scenario()
