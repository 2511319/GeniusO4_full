#!/usr/bin/env python3
# production/test-full-system.py
# Комплексное тестирование всей системы ChartGenius

import requests
import json
import time
from datetime import datetime

# URLs всех компонентов
FRONTEND_URL = "https://chartgenius-frontend-169129692197.europe-west1.run.app"
API_URL = "https://chartgenius-api-working-169129692197.europe-west1.run.app"
BOT_URL = "https://chartgenius-bot-working-169129692197.europe-west1.run.app"

# Реальные данные Telegram WebApp для тестирования
REAL_INIT_DATA = "query_id=AAGC5t4RAAAAAILm3hF4OoMR&user=%7B%22id%22%3A299820674%2C%22first_name%22%3A%22%D0%94%D0%B8%D0%BC%D0%B0%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22Dushnar%22%2C%22language_code%22%3A%22ru%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FXV2IBaxMPch2a19AJW5Q2zF3ccAOR6HvE9B7VMzx34k.svg%22%7D&auth_date=1750669916&signature=tWj0BgfvWVmIfUBWlrQGFElyrs68eF1Lp4QUjsU8XMe1iwZDqG4CybLjGXdA7Y0NSU-gBtxsh6GI4GvqQi8JCA&hash=080de3032960cb91f896b86c807e24d60a1bcea7056005584852e9a7f7aeefd5"

def test_component(name, url, endpoint="", expected_status=200, timeout=10):
    """Тестирование компонента системы"""
    try:
        print(f"🔍 Тестирование {name}...")
        full_url = f"{url}{endpoint}"
        
        response = requests.get(full_url, timeout=timeout)
        
        if response.status_code == expected_status:
            print(f"✅ {name}: OK (статус {response.status_code})")
            return True, response
        else:
            print(f"❌ {name}: ОШИБКА (статус {response.status_code})")
            return False, response
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: НЕДОСТУПЕН ({e})")
        return False, None

def test_api_auth():
    """Тестирование авторизации API"""
    try:
        print(f"🔐 Тестирование авторизации API...")
        
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
            # API возвращает токен в поле access_token
            token = data.get('access_token', '') or data.get('token', '')
            if token and len(token) > 50:
                print(f"✅ API авторизация: OK (токен получен, длина: {len(token)})")
                return True, token
            else:
                print(f"❌ API авторизация: Токен не получен")
                print(f"   Ответ: {data}")
                return False, None
        else:
            print(f"❌ API авторизация: ОШИБКА (статус {response.status_code})")
            print(f"   Ответ: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ API авторизация: ОШИБКА ({e})")
        return False, None

def test_api_with_token(token):
    """Тестирование API с токеном"""
    try:
        print(f"🔑 Тестирование API с токеном...")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Тест доступа к защищенному endpoint (тестовые данные)
        response = requests.get(f"{API_URL}/testdata", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                print(f"✅ API с токеном: OK (тестовые данные получены)")
                return True
            else:
                print(f"❌ API с токеном: Неверный ответ")
                return False
        else:
            print(f"❌ API с токеном: ОШИБКА (статус {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ API с токеном: ОШИБКА ({e})")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ CHARTGENIUS")
    print("=" * 60)
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # 1. Тестирование Frontend
    print("📱 ТЕСТИРОВАНИЕ FRONTEND")
    print("-" * 30)
    success, response = test_component("Frontend", FRONTEND_URL)
    results['frontend'] = success
    print()
    
    # 2. Тестирование API
    print("🔧 ТЕСТИРОВАНИЕ API")
    print("-" * 30)
    success, response = test_component("API Health", API_URL, "/health")
    results['api_health'] = success
    
    success, response = test_component("API Root", API_URL)
    results['api_root'] = success
    print()
    
    # 3. Тестирование авторизации
    print("🔐 ТЕСТИРОВАНИЕ АВТОРИЗАЦИИ")
    print("-" * 30)
    auth_success, token = test_api_auth()
    results['api_auth'] = auth_success
    
    if auth_success and token:
        token_success = test_api_with_token(token)
        results['api_with_token'] = token_success
    else:
        results['api_with_token'] = False
    print()
    
    # 4. Тестирование Telegram бота
    print("🤖 ТЕСТИРОВАНИЕ TELEGRAM БОТА")
    print("-" * 30)
    success, response = test_component("Bot Health", BOT_URL, "/health")
    results['bot_health'] = success
    
    success, response = test_component("Bot Root", BOT_URL)
    results['bot_root'] = success
    
    success, response = test_component("Bot Webhook Info", BOT_URL, "/webhook-info")
    results['bot_webhook'] = success
    print()
    
    # 5. Итоговый отчет
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"📋 Всего тестов: {total_tests}")
    print(f"✅ Пройдено: {passed_tests}")
    print(f"❌ Провалено: {total_tests - passed_tests}")
    print(f"📈 Успешность: {(passed_tests/total_tests)*100:.1f}%")
    print()
    
    print("🔍 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    print()
    
    # 6. Рекомендации
    print("💡 РЕКОМЕНДАЦИИ:")
    if passed_tests == total_tests:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Система готова к использованию!")
        print("🚀 Можно переходить к финальному развертыванию.")
    elif passed_tests >= total_tests * 0.8:
        print("⚠️  Большинство тестов пройдено, но есть проблемы.")
        print("🔧 Исправьте провалившиеся тесты перед продакшн.")
    else:
        print("🚨 КРИТИЧЕСКИЕ ПРОБЛЕМЫ! Система не готова.")
        print("🛠️  Требуется серьезная отладка.")
    
    print()
    print("🔗 ССЫЛКИ ДЛЯ ПРОВЕРКИ:")
    print(f"   Frontend: {FRONTEND_URL}")
    print(f"   API: {API_URL}")
    print(f"   Bot: {BOT_URL}")
    print()

    print("🎯 ТЕСТИРОВАНИЕ НАВИГАЦИИ:")
    print("   1. Откройте Frontend в Telegram WebApp")
    print("   2. Авторизуйтесь автоматически")
    print("   3. Нажмите 'К анализу' в личном кабинете")
    print("   4. Проверьте работу страницы анализа")
    print("   5. Нажмите 'Выйти' и убедитесь, что повторная авторизация не происходит")
    print()
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
