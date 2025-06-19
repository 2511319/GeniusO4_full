#!/usr/bin/env python3
"""
Простая версия Telegram бота для тестирования
"""
import os
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from jose import jwt

# Настройки
API_BASE = "http://localhost:8000"
TOKEN = "7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0"
JWT_SECRET_KEY = "34sSDF542rf65EJ1kj"
WEBAPP_URL = "http://localhost:5173"

def create_jwt_token(telegram_id: str) -> str:
    """Создает JWT токен для пользователя"""
    expire = datetime.utcnow() + timedelta(days=7)
    payload = {
        "sub": telegram_id,
        "exp": expire,
        "telegram_id": telegram_id
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

async def send_message(chat_id: int, text: str, reply_markup=None):
    """Отправляет сообщение через Telegram Bot API"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()

async def get_updates(offset=0):
    """Получает обновления от Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"offset": offset, "timeout": 30}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            return await response.json()

async def handle_start(chat_id: int, user_id: int):
    """Обработчик команды /start"""
    print(f"🎯 Handling /start for user {user_id} in chat {chat_id}")

    keyboard = {
        "inline_keyboard": [[
            {"text": "🚀 Получить анализ", "callback_data": "analyse"}
        ]]
    }

    welcome_text = (
        "👋 <b>Добро пожаловать в GeniusO4!</b>\n\n"
        "Я помогу вам получить профессиональный анализ криптовалют с использованием ИИ.\n\n"
        "Нажмите кнопку ниже, чтобы получить анализ:"
    )

    try:
        result = await send_message(chat_id, welcome_text, keyboard)
        print(f"✅ Welcome message sent: {result}")
    except Exception as e:
        print(f"❌ Error sending welcome message: {e}")

async def handle_analyse(chat_id: int, user_id: int, message_id: int):
    """Обработчик запроса анализа"""
    # Редактируем сообщение
    url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": "⏳ Проверяю подписку и генерирую анализ...",
        "parse_mode": "HTML"
    }
    
    async with aiohttp.ClientSession() as session:
        await session.post(url, json=data)
    
    try:
        # Проверяем подписку через API
        headers = {"X-Telegram-Id": str(user_id)}
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{API_BASE}/bot/analysis/simple", headers=headers, timeout=30) as response:
                if response.status == 402:
                    # Подписка отсутствует
                    keyboard = {
                        "inline_keyboard": [[
                            {"text": "💳 Оформить подписку", "url": "https://your-payment-url.com"}
                        ]]
                    }
                    
                    text = (
                        "🚫 <b>Для получения анализа необходима активная подписка.</b>\n\n"
                        "Оформите подписку, чтобы получить доступ к профессиональному анализу криптовалют."
                    )
                    
                    # Редактируем сообщение
                    edit_data = {
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "text": text,
                        "parse_mode": "HTML",
                        "reply_markup": json.dumps(keyboard)
                    }
                    
                    async with aiohttp.ClientSession() as session:
                        await session.post(f"https://api.telegram.org/bot{TOKEN}/editMessageText", json=edit_data)
                    return
                
                if response.status != 200:
                    error_text = "❌ Произошла ошибка при генерации анализа. Попробуйте позже."
                    edit_data = {
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "text": error_text,
                        "parse_mode": "HTML"
                    }
                    async with aiohttp.ClientSession() as session:
                        await session.post(f"https://api.telegram.org/bot{TOKEN}/editMessageText", json=edit_data)
                    return
                
                analysis_data = await response.json()
        
        # Создаем JWT токен для доступа к веб-интерфейсу
        token = create_jwt_token(str(user_id))
        
        # Создаем ссылку на веб-интерфейс
        web_link = f"{WEBAPP_URL}?token={token}&analysis_id={analysis_data['id']}"
        
        # Формируем краткий отчет
        analysis = analysis_data.get('analysis', {})
        summary = analysis.get('summary', 'Анализ выполнен успешно')
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "📊 Открыть полный отчет", "url": web_link}],
                [{"text": "🔄 Новый анализ", "callback_data": "analyse"}]
            ]
        }
        
        message_text = (
            f"✅ <b>Анализ готов!</b>\n\n"
            f"📈 <b>Символ:</b> {analysis_data.get('symbol', 'BTC/USDT')}\n"
            f"📝 <b>Краткий обзор:</b> {summary[:200]}...\n\n"
            f"Нажмите кнопку ниже для просмотра полного интерактивного отчета с графиками:"
        )
        
        # Редактируем сообщение
        edit_data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": message_text,
            "parse_mode": "HTML",
            "reply_markup": json.dumps(keyboard)
        }
        
        async with aiohttp.ClientSession() as session:
            await session.post(f"https://api.telegram.org/bot{TOKEN}/editMessageText", json=edit_data)
        
    except Exception as e:
        print(f"Error in analyse handler: {e}")
        error_text = "❌ Произошла ошибка. Попробуйте позже или обратитесь в поддержку."
        edit_data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": error_text,
            "parse_mode": "HTML"
        }
        async with aiohttp.ClientSession() as session:
            await session.post(f"https://api.telegram.org/bot{TOKEN}/editMessageText", json=edit_data)

async def process_update(update):
    """Обрабатывает одно обновление"""
    print(f"🔄 Processing update type: {list(update.keys())}")

    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text", "")

        print(f"💬 Message: '{text}' from user {user_id}")

        if text == "/start":
            print(f"🎯 Calling handle_start for user {user_id}")
            await handle_start(chat_id, user_id)
        else:
            print(f"❓ Unknown command: {text}")
    
    elif "callback_query" in update:
        callback = update["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        user_id = callback["from"]["id"]
        message_id = callback["message"]["message_id"]
        data = callback["data"]
        
        # Отвечаем на callback
        url = f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery"
        answer_data = {"callback_query_id": callback["id"]}
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=answer_data)
        
        if data == "analyse":
            await handle_analyse(chat_id, user_id, message_id)

async def webhook_handler(request):
    """Обработчик webhook от Telegram"""
    try:
        data = await request.json()
        print(f"📨 Webhook received: {data}")
        await process_update(data)
        return {"status": "ok"}
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return {"status": "error", "message": str(e)}

async def main():
    """Главная функция бота"""
    print("🤖 Запуск Telegram бота...")
    print(f"📊 Backend API: {API_BASE}")
    print(f"🌐 Web App: {WEBAPP_URL}")

    # Проверяем режим работы
    webhook_url = os.getenv("BOT_WEBHOOK_URL")
    port = int(os.getenv("PORT", 8080))

    if webhook_url:
        # Webhook режим для продакшена
        print(f"🌐 Запуск в webhook режиме на порту {port}")
        from aiohttp import web

        app = web.Application()
        app.router.add_post(f"/{TOKEN}", webhook_handler)
        app.router.add_get("/health", lambda r: web.json_response({"status": "ok"}))

        # Настраиваем webhook
        webhook_full_url = f"{webhook_url}/{TOKEN}"
        print(f"🔗 Настройка webhook: {webhook_full_url}")

        async with aiohttp.ClientSession() as session:
            webhook_data = {"url": webhook_full_url}
            async with session.post(f"https://api.telegram.org/bot{TOKEN}/setWebhook", json=webhook_data) as response:
                result = await response.json()
                if result.get("ok"):
                    print("✅ Webhook настроен успешно")
                else:
                    print(f"❌ Ошибка настройки webhook: {result}")

        # Запускаем веб-сервер
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()

        print(f"✅ Бот запущен в webhook режиме на порту {port}")

        # Ждем бесконечно
        try:
            while True:
                await asyncio.sleep(3600)
        except KeyboardInterrupt:
            print("\n🛑 Остановка бота...")
        finally:
            await runner.cleanup()

    else:
        # Polling режим для локальной разработки
        print("🔄 Запуск в polling режиме")
        print("✅ Бот запущен! Отправьте /start боту @Chart_Genius_bot")

        offset = 0

        while True:
            try:
                # Получаем обновления
                print(f"🔄 Polling updates with offset {offset}...")
                result = await get_updates(offset)

                if result.get("ok"):
                    updates = result.get("result", [])
                    print(f"📨 Received {len(updates)} updates")

                    for update in updates:
                        print(f"📝 Processing update: {update}")
                        offset = update["update_id"] + 1
                        await process_update(update)
                else:
                    print(f"❌ Error getting updates: {result}")

                await asyncio.sleep(1)

            except KeyboardInterrupt:
                print("\n🛑 Остановка бота...")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
