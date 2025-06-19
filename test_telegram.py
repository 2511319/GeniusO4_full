#!/usr/bin/env python3
import requests
import json

TOKEN = '7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0'

def test_telegram_connection():
    print("🔍 Тестирование соединения с Telegram API...")
    
    # Проверяем, что бот работает
    try:
        response = requests.get(f'https://api.telegram.org/bot{TOKEN}/getMe', timeout=10)
        print(f'Bot info status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            result = data['result']
            print(f'✅ Bot name: {result["first_name"]}')
            print(f'✅ Bot username: @{result["username"]}')
            print(f'✅ Bot ID: {result["id"]}')
        else:
            print(f'❌ Error: {response.text}')
            return False
            
        # Проверяем обновления
        response = requests.get(f'https://api.telegram.org/bot{TOKEN}/getUpdates', timeout=10)
        print(f'Updates status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            updates = data['result']
            print(f'📨 Updates count: {len(updates)}')
            if updates:
                last_update = updates[-1]
                print(f'📝 Last update ID: {last_update["update_id"]}')
                if 'message' in last_update:
                    msg = last_update['message']
                    print(f'💬 Last message: "{msg.get("text", "")}" from {msg["from"]["first_name"]}')
                elif 'callback_query' in last_update:
                    cb = last_update['callback_query']
                    print(f'🔘 Last callback: "{cb["data"]}" from {cb["from"]["first_name"]}')
            else:
                print("📭 No updates found")
        else:
            print(f'❌ Updates error: {response.text}')
            return False
            
        return True
        
    except Exception as e:
        print(f'❌ Connection error: {e}')
        return False

if __name__ == "__main__":
    test_telegram_connection()
