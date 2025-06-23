#!/usr/bin/env python3
# production/test-analysis.py
# Тестирование API анализа

import requests
import json
import time
from datetime import datetime

# URLs
API_URL = "https://chartgenius-api-working-169129692197.europe-west1.run.app"

# Реальные данные Telegram WebApp для получения токена
REAL_INIT_DATA = "query_id=AAGC5t4RAAAAAILm3hF4OoMR&user=%7B%22id%22%3A299820674%2C%22first_name%22%3A%22%D0%94%D0%B8%D0%BC%D0%B0%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22Dushnar%22%2C%22language_code%22%3A%22ru%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FXV2IBaxMPch2a19AJW5Q2zF3ccAOR6HvE9B7VMzx34k.svg%22%7D&auth_date=1750669916&signature=tWj0BgfvWVmIfUBWlrQGFElyrs68eF1Lp4QUjsU8XMe1iwZDqG4CybLjGXdA7Y0NSU-gBtxsh6GI4GvqQi8JCA&hash=080de3032960cb91f896b86c807e24d60a1bcea7056005584852e9a7f7aeefd5"

def get_auth_token():
    """Получение токена авторизации"""
    try:
        print("🔐 Получение токена авторизации...")
        
        response = requests.post(
            f"{API_URL}/api/auth/webapp-token",
            headers={
                'Content-Type': 'text/plain',
                'Host': 'chartgenius-api-working-169129692197.europe-west1.run.app',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            data=REAL_INIT_DATA,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token', '')
            if token:
                print(f"✅ Токен получен (длина: {len(token)})")
                return token
            else:
                print(f"❌ Токен не найден в ответе")
                return None
        else:
            print(f"❌ Ошибка получения токена: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def test_analysis_with_auth():
    """Тестирование анализа с авторизацией"""
    token = get_auth_token()
    if not token:
        print("❌ Не удалось получить токен")
        return False
    
    try:
        print("🚀 Тестирование анализа с авторизацией...")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        body = {
            "symbol": "BTCUSDT",
            "interval": "4h", 
            "limit": 144,
            "indicators": ["RSI", "MACD"]
        }
        
        response = requests.post(
            f"{API_URL}/api/analyze",
            headers=headers,
            json=body,
            timeout=60
        )
        
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ АНАЛИЗ УСПЕШЕН!")
            print(f"📈 Получены данные для {body['symbol']}")
            if 'analysis' in data:
                print(f"📋 Анализ содержит: {list(data['analysis'].keys())}")
            if 'ohlc' in data:
                print(f"📊 OHLC данных: {len(data['ohlc'])} записей")
            return True
        else:
            print(f"❌ ОШИБКА АНАЛИЗА: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📋 Детали ошибки: {error_data}")
            except:
                print(f"📋 Текст ошибки: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Исключение при анализе: {e}")
        return False

def test_analysis_without_auth():
    """Тестирование анализа без авторизации"""
    try:
        print("🔓 Тестирование анализа без авторизации...")
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        body = {
            "symbol": "BTCUSDT",
            "interval": "4h", 
            "limit": 144,
            "indicators": ["RSI", "MACD"]
        }
        
        response = requests.post(
            f"{API_URL}/api/analyze",
            headers=headers,
            json=body,
            timeout=60
        )
        
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ АНАЛИЗ БЕЗ АВТОРИЗАЦИИ РАБОТАЕТ!")
            return True
        else:
            print(f"❌ Анализ без авторизации не работает: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📋 Детали ошибки: {error_data}")
            except:
                print(f"📋 Текст ошибки: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 ТЕСТИРОВАНИЕ API АНАЛИЗА")
    print("=" * 50)
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 API URL: {API_URL}")
    print()
    
    # Тест 1: Анализ с авторизацией
    print("📋 ТЕСТ 1: Анализ с авторизацией")
    print("-" * 30)
    auth_result = test_analysis_with_auth()
    print()
    
    # Тест 2: Анализ без авторизации (для десктопной версии)
    print("📋 ТЕСТ 2: Анализ без авторизации")
    print("-" * 30)
    no_auth_result = test_analysis_without_auth()
    print()
    
    # Итоги
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 50)
    print(f"✅ Анализ с авторизацией: {'РАБОТАЕТ' if auth_result else 'НЕ РАБОТАЕТ'}")
    print(f"✅ Анализ без авторизации: {'РАБОТАЕТ' if no_auth_result else 'НЕ РАБОТАЕТ'}")
    print()
    
    if auth_result or no_auth_result:
        print("🎉 API АНАЛИЗА РАБОТАЕТ!")
        if not no_auth_result:
            print("⚠️  Десктопная версия может не работать без авторизации")
    else:
        print("🚨 API АНАЛИЗА НЕ РАБОТАЕТ!")
        print("🔧 Проверьте логи Google Cloud Run")
    
    return auth_result or no_auth_result

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
