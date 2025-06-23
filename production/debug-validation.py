#!/usr/bin/env python3
"""
Отладка валидации Telegram WebApp
Тестируем разные способы обработки данных
"""

import hmac
import hashlib
from urllib.parse import parse_qsl, unquote

# Реальные данные от пользователя
REAL_INIT_DATA = "query_id=AAGC5t4RAAAAAILm3hEdkibA&user=%7B%22id%22%3A299820674%2C%22first_name%22%3A%22%D0%94%D0%B8%D0%BC%D0%B0%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22Dushnar%22%2C%22language_code%22%3A%22ru%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FXV2IBaxMPch2a19AJW5Q2zF3ccAOR6HvE9B7VMzx34k.svg%22%7D&auth_date=1750664616&signature=xWxiOLmAz1UH--VXWE-MpbHRVCA_2o3zXvytMlZECFQ1ZhFeXS7OGm5z84RElDyWFp59jwTvv3Sw4SEveX_BCg&hash=38c4dd29c1f05407714aa91bd9b6a87408ac72bab0dab215e700ec688725c0ac"

# Токен бота (замените на реальный)
BOT_TOKEN = "7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0"

def test_validation_method_1():
    """Метод 1: Без URL-декодирования (как в нашем исправленном коде)"""
    print("🧪 Метод 1: Без URL-декодирования")
    
    parsed_data = dict(parse_qsl(REAL_INIT_DATA))
    received_hash = parsed_data.pop('hash')
    
    data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(parsed_data.items())])
    
    print(f"📋 Data check string (первые 200 символов):")
    print(f"   {data_check_string[:200]}...")
    
    secret_key = hmac.new(
        "WebAppData".encode(),
        BOT_TOKEN.encode(),
        hashlib.sha256
    ).digest()
    
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    print(f"🔑 Received hash:  {received_hash}")
    print(f"🔑 Calculated hash: {calculated_hash}")
    print(f"✅ Совпадают: {received_hash == calculated_hash}")
    
    return received_hash == calculated_hash

def test_validation_method_2():
    """Метод 2: С URL-декодированием"""
    print("\n🧪 Метод 2: С URL-декодированием")
    
    decoded_data = unquote(REAL_INIT_DATA)
    parsed_data = dict(parse_qsl(decoded_data))
    received_hash = parsed_data.pop('hash')
    
    data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(parsed_data.items())])
    
    print(f"📋 Data check string (первые 200 символов):")
    print(f"   {data_check_string[:200]}...")
    
    secret_key = hmac.new(
        "WebAppData".encode(),
        BOT_TOKEN.encode(),
        hashlib.sha256
    ).digest()
    
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    print(f"🔑 Received hash:  {received_hash}")
    print(f"🔑 Calculated hash: {calculated_hash}")
    print(f"✅ Совпадают: {received_hash == calculated_hash}")
    
    return received_hash == calculated_hash

def test_validation_method_3():
    """Метод 3: Как в оригинальном gist (split & join)"""
    print("\n🧪 Метод 3: Оригинальный метод (split & join)")
    
    # Декодируем как в оригинальном примере
    encoded = unquote(REAL_INIT_DATA)
    
    # Разбиваем на параметры
    arr = encoded.split('&')
    hash_index = arr.index([s for s in arr if s.startswith('hash=')][0])
    hash_value = arr.pop(hash_index).split('=')[1]
    
    # Сортируем
    arr.sort()
    
    # Создаем строку
    data_check_string = '\n'.join(arr)
    
    print(f"📋 Data check string (первые 200 символов):")
    print(f"   {data_check_string[:200]}...")
    
    secret_key = hmac.new(
        "WebAppData".encode(),
        BOT_TOKEN.encode(),
        hashlib.sha256
    ).digest()
    
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    print(f"🔑 Received hash:  {hash_value}")
    print(f"🔑 Calculated hash: {calculated_hash}")
    print(f"✅ Совпадают: {hash_value == calculated_hash}")
    
    return hash_value == calculated_hash

def analyze_photo_url():
    """Анализ photo_url в разных форматах"""
    print("\n🔍 АНАЛИЗ PHOTO_URL:")
    print("=" * 60)
    
    # Без декодирования
    parsed_raw = dict(parse_qsl(REAL_INIT_DATA))
    user_raw = parsed_raw.get('user', '')
    print(f"📋 User (raw): {user_raw[:100]}...")
    
    # С декодированием
    parsed_decoded = dict(parse_qsl(unquote(REAL_INIT_DATA)))
    user_decoded = parsed_decoded.get('user', '')
    print(f"📋 User (decoded): {user_decoded[:100]}...")
    
    # Проверяем photo_url
    import json
    try:
        user_data_decoded = json.loads(user_decoded)
        photo_url = user_data_decoded.get('photo_url', '')
        print(f"🖼️ Photo URL: {photo_url}")
        print(f"   Содержит \\/ : {'\\/' in photo_url}")
        print(f"   Содержит %5C: {'%5C' in user_raw}")
    except Exception as e:
        print(f"❌ Ошибка парсинга JSON: {e}")

if __name__ == "__main__":
    print("🔍 ОТЛАДКА ВАЛИДАЦИИ TELEGRAM WEBAPP")
    print("=" * 60)
    
    analyze_photo_url()
    
    print("\n" + "=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ МЕТОДОВ ВАЛИДАЦИИ")
    print("=" * 60)
    
    method1_result = test_validation_method_1()
    method2_result = test_validation_method_2()
    method3_result = test_validation_method_3()
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ:")
    print("=" * 60)
    print(f"Метод 1 (без URL-декодирования): {'✅ РАБОТАЕТ' if method1_result else '❌ НЕ РАБОТАЕТ'}")
    print(f"Метод 2 (с URL-декодированием): {'✅ РАБОТАЕТ' if method2_result else '❌ НЕ РАБОТАЕТ'}")
    print(f"Метод 3 (оригинальный gist): {'✅ РАБОТАЕТ' if method3_result else '❌ НЕ РАБОТАЕТ'}")
    
    if method1_result:
        print("\n🎉 РЕШЕНИЕ: Использовать метод 1 (без URL-декодирования)")
    elif method2_result:
        print("\n🎉 РЕШЕНИЕ: Использовать метод 2 (с URL-декодированием)")
    elif method3_result:
        print("\n🎉 РЕШЕНИЕ: Использовать метод 3 (оригинальный)")
    else:
        print("\n❌ НИ ОДИН МЕТОД НЕ РАБОТАЕТ - проверьте bot token!")
