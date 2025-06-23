#!/usr/bin/env python3
"""
Тест валидации с реальными данными от Telegram WebApp
"""

import requests
import json

# Конфигурация
API_URL = "https://chartgenius-api-working-169129692197.europe-west1.run.app"

# Реальные данные от пользователя (НОВЫЕ из последних логов)
REAL_INIT_DATA = "query_id=AAGC5t4RAAAAAILm3hF4OoMR&user=%7B%22id%22%3A299820674%2C%22first_name%22%3A%22%D0%94%D0%B8%D0%BC%D0%B0%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22Dushnar%22%2C%22language_code%22%3A%22ru%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FXV2IBaxMPch2a19AJW5Q2zF3ccAOR6HvE9B7VMzx34k.svg%22%7D&auth_date=1750669916&signature=tWj0BgfvWVmIfUBWlrQGFElyrs68eF1Lp4QUjsU8XMe1iwZDqG4CybLjGXdA7Y0NSU-gBtxsh6GI4GvqQi8JCA&hash=080de3032960cb91f896b86c807e24d60a1bcea7056005584852e9a7f7aeefd5"

def test_real_data():
    """Тест с реальными данными от Telegram WebApp"""
    print("🧪 Тестирование с реальными данными Telegram WebApp")
    print("=" * 60)
    
    print(f"📋 Длина данных: {len(REAL_INIT_DATA)}")
    print(f"📋 Данные: {REAL_INIT_DATA[:100]}...")
    
    try:
        print("\n🔄 Отправка запроса на API...")
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
        
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ УСПЕХ! Валидация прошла успешно!")
            try:
                data = response.json()
                print(f"🎉 Получен токен: {data.get('access_token', 'отсутствует')[:50]}...")
                print(f"⏰ Срок действия: {data.get('expires_minutes', 'неизвестно')} минут")
            except:
                print(f"📄 Ответ: {response.text}")
        elif response.status_code == 401:
            print("❌ ОШИБКА: Валидация не прошла")
            try:
                error_data = response.json()
                print(f"💬 Сообщение: {error_data.get('detail', 'Нет сообщения')}")
            except:
                print(f"📄 Ответ: {response.text}")
        else:
            print(f"⚠️ Неожиданный статус: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

def analyze_data():
    """Анализ структуры данных"""
    print("\n🔍 АНАЛИЗ ДАННЫХ:")
    print("=" * 60)
    
    from urllib.parse import parse_qsl, unquote
    
    # Парсим данные
    parsed = dict(parse_qsl(REAL_INIT_DATA))
    
    print("📋 Структура данных:")
    for key, value in sorted(parsed.items()):
        if key == 'user':
            # Декодируем JSON пользователя
            try:
                import json
                user_data = json.loads(unquote(value))
                print(f"   {key}: {json.dumps(user_data, indent=6, ensure_ascii=False)}")
            except:
                print(f"   {key}: {value[:100]}...")
        else:
            print(f"   {key}: {value}")
    
    print(f"\n🔑 Hash: {parsed.get('hash', 'отсутствует')}")
    print(f"📅 Auth date: {parsed.get('auth_date', 'отсутствует')}")
    
    # Проверяем photo_url
    if 'user' in parsed:
        try:
            user_data = json.loads(unquote(parsed['user']))
            photo_url = user_data.get('photo_url', '')
            if photo_url:
                print(f"\n🖼️ Photo URL найден:")
                print(f"   Оригинал: {photo_url}")
                print(f"   Содержит экранированные слеши: {'\\/' in photo_url}")
        except:
            pass

if __name__ == "__main__":
    analyze_data()
    test_real_data()
    
    print("\n" + "=" * 60)
    print("📝 ВЫВОДЫ:")
    print("=" * 60)
    print("1. Если статус 200 - валидация исправлена и работает!")
    print("2. Если статус 401 - нужно дополнительно настроить алгоритм")
    print("3. Обратите внимание на photo_url с экранированными слешами")
    print("4. Проверьте, что bot token правильный в Google Cloud Secrets")
