#!/usr/bin/env python3
"""
Скрипт для получения информации о Telegram боте
"""
import requests
import sys

def get_bot_info(token):
    """Получает информацию о боте"""
    url = f"https://api.telegram.org/bot{token}/getMe"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        if data.get('ok'):
            bot_info = data['result']
            print("✅ Информация о боте:")
            print(f"   ID: {bot_info.get('id')}")
            print(f"   Имя: {bot_info.get('first_name')}")
            print(f"   Username: @{bot_info.get('username')}")
            print(f"   Может присоединяться к группам: {bot_info.get('can_join_groups')}")
            print(f"   Может читать все сообщения: {bot_info.get('can_read_all_group_messages')}")
            print(f"   Поддерживает inline режим: {bot_info.get('supports_inline_queries')}")
            
            return bot_info.get('username')
        else:
            print(f"❌ Ошибка API: {data.get('description')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сети: {e}")
        return None
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return None

if __name__ == "__main__":
    token = "7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0"
    
    print("🤖 Получение информации о Telegram боте...")
    username = get_bot_info(token)
    
    if username:
        print(f"\n📝 Добавьте в ваши .env файлы:")
        print(f"TELEGRAM_BOT_USERNAME={username}")
    else:
        print("\n❌ Не удалось получить информацию о боте. Проверьте токен.")
        sys.exit(1)
