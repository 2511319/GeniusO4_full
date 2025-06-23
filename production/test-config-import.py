#!/usr/bin/env python3
"""
Тест импорта конфигурации
"""

import sys
import os

print("🧪 Тестирование импорта конфигурации")
print("=" * 60)

# Добавляем путь к production backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print(f"📋 Python path: {sys.path[:3]}...")
print(f"📋 Current directory: {os.getcwd()}")
print(f"📋 Script directory: {os.path.dirname(__file__)}")

# Тест 1: Импорт как в app.py
print("\n1. Тест импорта как в app.py:")
try:
    from production.backend.config.production import config
    token = config.get_telegram_bot_token()
    print(f"✅ Успех! Token (первые 10 символов): {token[:10] if token else 'НЕТ'}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# Тест 2: Импорт как в middleware
print("\n2. Тест импорта как в middleware:")
try:
    from config.production import config
    token = config.get_telegram_bot_token()
    print(f"✅ Успех! Token (первые 10 символов): {token[:10] if token else 'НЕТ'}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# Тест 3: Прямой импорт
print("\n3. Тест прямого импорта:")
try:
    import production.backend.config.production as prod_config
    token = prod_config.config.get_telegram_bot_token()
    print(f"✅ Успех! Token (первые 10 символов): {token[:10] if token else 'НЕТ'}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# Тест 4: Проверка файлов
print("\n4. Проверка существования файлов:")
config_path = os.path.join(os.path.dirname(__file__), 'backend', 'config', 'production.py')
print(f"📁 Config файл: {config_path}")
print(f"📁 Существует: {os.path.exists(config_path)}")

if os.path.exists(config_path):
    print(f"📁 Размер: {os.path.getsize(config_path)} байт")

# Тест 5: Переменные окружения
print("\n5. Проверка переменных окружения:")
env_vars = ['TELEGRAM_BOT_TOKEN', 'GOOGLE_CLOUD_PROJECT', 'PORT']
for var in env_vars:
    value = os.getenv(var)
    if value:
        if 'TOKEN' in var:
            print(f"📋 {var}: {value[:10]}...")
        else:
            print(f"📋 {var}: {value}")
    else:
        print(f"📋 {var}: НЕ УСТАНОВЛЕНА")

print("\n" + "=" * 60)
print("📝 ВЫВОДЫ:")
print("Если все тесты провалились - проблема в структуре импорта")
print("Если тест 1 работает - используем этот импорт в middleware")
print("Если тест 2 работает - текущий импорт правильный")
print("Если тест 3 работает - используем прямой импорт")
