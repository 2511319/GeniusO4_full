#!/usr/bin/env python3
# АРХИВНЫЙ ФАЙЛ - быстрый тест Telegram bot
import requests
import json

def test_bot():
    """Быстрый тест Telegram bot"""
    bot_token = "7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0"
    
    print("🤖 БЫСТРЫЙ ТЕСТ TELEGRAM BOT")
    print("=" * 40)
    
    # Тест 1: getMe
    try:
        r = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe")
        if r.status_code == 200:
            bot_info = r.json()["result"]
            print(f"✅ Bot активен: @{bot_info['username']}")
        else:
            print(f"❌ Bot недоступен: {r.status_code}")
    except Exception as e:
        print(f"❌ Ошибка getMe: {e}")
    
    # Тест 2: getWebhookInfo
    try:
        r = requests.get(f"https://api.telegram.org/bot{bot_token}/getWebhookInfo")
        if r.status_code == 200:
            webhook_info = r.json()["result"]
            webhook_url = webhook_info.get("url", "")
            if webhook_url:
                print(f"✅ Webhook установлен: {webhook_url[:50]}...")
            else:
                print("❌ Webhook НЕ установлен")
        else:
            print(f"❌ Ошибка webhook info: {r.status_code}")
    except Exception as e:
        print(f"❌ Ошибка webhook: {e}")
    
    # Тест 3: Проверка Cloud Run сервиса
    try:
        bot_url = "https://chartgenius-bot-working-w7tck47geq-ew.a.run.app"
        r = requests.get(f"{bot_url}/health", timeout=10)
        if r.status_code == 200:
            print(f"✅ Bot сервис доступен")
        else:
            print(f"❌ Bot сервис недоступен: {r.status_code}")
    except Exception as e:
        print(f"❌ Ошибка bot сервиса: {e}")
    
    print("\n🎯 Тест завершен")

if __name__ == "__main__":
    test_bot()
