#!/usr/bin/env python3
import os
import sys

# Устанавливаем переменные окружения
os.environ['TELEGRAM_BOT_TOKEN'] = '7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0'
os.environ['JWT_SECRET_KEY'] = '34sSDF542rf65EJ1kj'
os.environ['API_URL'] = 'http://localhost:8000'
os.environ['WEBAPP_URL'] = 'http://localhost:5173'

# Добавляем путь к боту
sys.path.append('bot')

# Импортируем и запускаем бота
if __name__ == "__main__":
    import bot
    bot.main()
