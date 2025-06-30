# 🤖 ChartGenius Telegram Bot - aiogram Version
# Версия: 1.1.0-dev
# Миграция с python-telegram-bot на aiogram

import asyncio
import logging
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo, BotCommand, BotCommandScopeDefault
)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from aiohttp.web_request import Request

# Импорты для интеграции с backend
import aiohttp
import jwt

logger = logging.getLogger(__name__)

# === CONFIGURATION ===
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://chartgenius-frontend.com")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "chartgenius_webhook_secret")

# === STATES ===
class UserStates(StatesGroup):
    waiting_for_symbol = State()
    waiting_for_settings = State()

# === BOT INITIALIZATION ===
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# === MIDDLEWARE ===
class AuthMiddleware:
    """Middleware для аутентификации пользователей"""

    async def __call__(self, handler, event, data):
        """Обработка события с проверкой аутентификации"""
        user_id = None

        if hasattr(event, 'from_user') and event.from_user:
            user_id = str(event.from_user.id)

            # Проверяем пользователя в backend (с fallback)
            user_data = await self.check_user_auth(user_id)
            data['user_data'] = user_data
            data['user_id'] = user_id

        return await handler(event, data)

    async def check_user_auth(self, telegram_id: str) -> Optional[Dict[str, Any]]:
        """Проверка аутентификации пользователя через backend"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{BACKEND_URL}/api/users/{telegram_id}",
                    timeout=aiohttp.ClientTimeout(total=3)  # Уменьшен таймаут
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except asyncio.TimeoutError:
            logger.warning(f"Backend timeout for user {telegram_id}, using fallback")
            # Возвращаем базовые данные пользователя для продолжения работы
            return {
                'telegram_id': telegram_id,
                'role': 'user',
                'subscription': 'free',
                'fallback': True
            }
        except Exception as e:
            logger.error(f"Error checking user auth: {e}")
            # Возвращаем базовые данные для продолжения работы
            return {
                'telegram_id': telegram_id,
                'role': 'user',
                'subscription': 'free',
                'fallback': True
            }

class LoggingMiddleware:
    """Middleware для логирования"""
    
    async def __call__(self, handler, event, data):
        """Логирование событий"""
        start_time = datetime.utcnow()
        
        try:
            result = await handler(event, data)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Event processed in {processing_time:.3f}s: {type(event).__name__}")
            
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Event failed after {processing_time:.3f}s: {e}")
            raise

# Регистрация middleware
dp.message.middleware(AuthMiddleware())
dp.callback_query.middleware(AuthMiddleware())
dp.message.middleware(LoggingMiddleware())
dp.callback_query.middleware(LoggingMiddleware())

# === HELPER FUNCTIONS ===
async def send_start_menu(chat_id: int, username: str, user_data: Optional[Dict[str, Any]] = None):
    """Отправка стартового меню"""
    try:
        # Создаем клавиатуру с WebApp
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🚀 Открыть ChartGenius",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )],
            [InlineKeyboardButton(
                text="📊 Быстрый анализ",
                callback_data="quick_analysis"
            )],
            [InlineKeyboardButton(
                text="⚙️ Настройки",
                callback_data="settings"
            )],
            [InlineKeyboardButton(
                text="ℹ️ Помощь",
                callback_data="help"
            )]
        ])

        welcome_text = f"""
🎯 <b>Добро пожаловать в ChartGenius!</b>

Привет, {username}! 👋

ChartGenius - это профессиональная система анализа криптовалютных рынков с использованием ИИ.

🔥 <b>Возможности:</b>
• Технический анализ с 20+ индикаторами
• ИИ-анализ рыночных трендов
• Поддержка и сопротивления
• Уровни Фибоначчи
• Волны Эллиотта
• Дивергенции и паттерны

💎 <b>Ваш статус:</b> {user_data.get('role', 'user').title() if user_data else 'User'}

Выберите действие ниже или откройте полную версию приложения! 🚀
        """

        await bot.send_message(
            chat_id=chat_id,
            text=welcome_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Error sending start menu: {e}")
        await bot.send_message(
            chat_id=chat_id,
            text="❌ Ошибка при загрузке меню. Попробуйте позже."
        )

# === COMMAND HANDLERS ===
@router.message(CommandStart())
async def start_command(message: Message, user_data: Optional[Dict[str, Any]] = None):
    """Обработчик команды /start"""
    try:
        user_id = str(message.from_user.id)
        username = message.from_user.username or "Пользователь"
        
        # Регистрируем пользователя в backend если нужно
        if not user_data or user_data.get('fallback'):
            await register_user_in_backend(user_id, username)

        # Используем helper функцию для отправки меню
        await send_start_menu(message.chat.id, username, user_data)
        
        logger.info(f"Start command processed for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.answer(
            "❌ Произошла ошибка. Попробуйте позже.",
            parse_mode="HTML"
        )

@router.message(Command("help"))
async def help_command(message: Message):
    """Обработчик команды /help"""
    try:
        help_text = """
📚 <b>Справка по ChartGenius</b>

<b>Основные команды:</b>
/start - Главное меню
/help - Эта справка
/settings - Настройки уведомлений
/watch - Добавить в отслеживание
/unwatch - Убрать из отслеживания

<b>Как использовать:</b>
1. Нажмите "🚀 Открыть ChartGenius" для доступа к веб-приложению
2. Выберите криптовалютную пару для анализа
3. Настройте технические индикаторы
4. Получите ИИ-анализ рынка

<b>Поддержка:</b>
Если у вас есть вопросы, обратитесь к администратору.

<b>Версия:</b> 1.1.0-dev (aiogram)
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🚀 Открыть ChartGenius",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )],
            [InlineKeyboardButton(
                text="🔙 Назад в меню",
                callback_data="back_to_menu"
            )]
        ])
        
        await message.answer(help_text, reply_markup=keyboard, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await message.answer("❌ Ошибка при получении справки.")

@router.message(Command("settings"))
async def settings_command(message: Message, user_data: Optional[Dict[str, Any]] = None):
    """Обработчик команды /settings"""
    try:
        user_role = user_data.get('role', 'user') if user_data else 'user'
        
        settings_text = f"""
⚙️ <b>Настройки</b>

<b>Ваш статус:</b> {user_role.title()}
<b>Уведомления:</b> Включены
<b>Язык:</b> Русский

<b>Доступные настройки:</b>
• Уведомления о сигналах
• Частота анализов
• Предпочитаемые пары
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🔔 Уведомления",
                callback_data="settings_notifications"
            )],
            [InlineKeyboardButton(
                text="📊 Предпочтения",
                callback_data="settings_preferences"
            )],
            [InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="back_to_menu"
            )]
        ])
        
        await message.answer(settings_text, reply_markup=keyboard, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in settings command: {e}")
        await message.answer("❌ Ошибка при загрузке настроек.")

# === CALLBACK QUERY HANDLERS ===
@router.callback_query(F.data == "quick_analysis")
async def quick_analysis_callback(callback: CallbackQuery, state: FSMContext):
    """Быстрый анализ"""
    try:
        await callback.answer()
        
        text = """
📊 <b>Быстрый анализ</b>

Введите символ криптовалютной пары для анализа.

<b>Примеры:</b>
• BTCUSDT
• ETHUSDT
• ADAUSDT

Или выберите из популярных:
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="₿ BTC/USDT", callback_data="analyze_BTCUSDT"),
                InlineKeyboardButton(text="⟠ ETH/USDT", callback_data="analyze_ETHUSDT")
            ],
            [
                InlineKeyboardButton(text="🔵 ADA/USDT", callback_data="analyze_ADAUSDT"),
                InlineKeyboardButton(text="🟡 BNB/USDT", callback_data="analyze_BNBUSDT")
            ],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await state.set_state(UserStates.waiting_for_symbol)
        
    except Exception as e:
        logger.error(f"Error in quick analysis: {e}")
        await callback.answer("❌ Ошибка при запуске анализа.")

@router.callback_query(F.data.startswith("analyze_"))
async def analyze_symbol_callback(callback: CallbackQuery):
    """Анализ конкретного символа"""
    try:
        await callback.answer("🔄 Запускаем анализ...")
        
        symbol = callback.data.replace("analyze_", "")
        user_id = str(callback.from_user.id)
        
        # Запускаем анализ через backend
        analysis_result = await start_analysis_in_backend(user_id, symbol)
        
        if analysis_result:
            text = f"""
✅ <b>Анализ запущен!</b>

<b>Пара:</b> {symbol}
<b>Статус:</b> Обработка...
<b>ID задачи:</b> {analysis_result.get('task_id', 'N/A')}

Результат будет готов через 30-60 секунд.
Вы получите уведомление когда анализ завершится.
            """
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="🚀 Открыть в приложении",
                    web_app=WebAppInfo(url=f"{WEBAPP_URL}/analysis")
                )],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
            ])
            
        else:
            text = "❌ Не удалось запустить анализ. Попробуйте позже."
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
            ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error analyzing symbol: {e}")
        await callback.answer("❌ Ошибка при анализе.")

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback(callback: CallbackQuery):
    """Возврат в главное меню"""
    try:
        await callback.answer()

        # Создаем новое сообщение для отправки стартового меню
        if callback.message:
            # Удаляем старое сообщение
            try:
                await callback.message.delete()
            except:
                pass

            # Отправляем новое стартовое сообщение
            await send_start_menu(callback.message.chat.id, callback.from_user.username or "Пользователь")

    except Exception as e:
        logger.error(f"Error returning to menu: {e}")
        await callback.answer("❌ Ошибка при возврате в меню.")

# === MESSAGE HANDLERS ===
@router.message(UserStates.waiting_for_symbol)
async def handle_symbol_input(message: Message, state: FSMContext):
    """Обработка ввода символа для анализа"""
    try:
        symbol = message.text.upper().strip()
        
        # Валидация символа
        if not symbol or len(symbol) < 3:
            await message.answer(
                "❌ Неверный формат символа. Попробуйте еще раз.\n"
                "Пример: BTCUSDT"
            )
            return
        
        user_id = str(message.from_user.id)
        
        # Запускаем анализ
        analysis_result = await start_analysis_in_backend(user_id, symbol)
        
        if analysis_result:
            text = f"""
✅ <b>Анализ {symbol} запущен!</b>

<b>ID задачи:</b> {analysis_result.get('task_id', 'N/A')}
<b>Статус:</b> Обработка...

Результат будет готов через 30-60 секунд.
            """
        else:
            text = f"❌ Не удалось запустить анализ для {symbol}."
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_menu")]
        ])
        
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error handling symbol input: {e}")
        await message.answer("❌ Ошибка при обработке символа.")

# === BACKEND INTEGRATION ===
async def register_user_in_backend(telegram_id: str, username: str) -> bool:
    """Регистрация пользователя в backend"""
    try:
        async with aiohttp.ClientSession() as session:
            data = {
                'telegram_id': telegram_id,
                'username': username,
                'source': 'telegram_bot'
            }
            
            async with session.post(
                f"{BACKEND_URL}/api/users/register",
                json=data,
                timeout=aiohttp.ClientTimeout(total=5)  # Уменьшен таймаут
            ) as response:
                return response.status in [200, 201]

    except asyncio.TimeoutError:
        logger.warning(f"Backend timeout during user registration for {telegram_id}")
        return False
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        return False

async def start_analysis_in_backend(user_id: str, symbol: str) -> Optional[Dict[str, Any]]:
    """Запуск асинхронного анализа через backend"""
    try:
        async with aiohttp.ClientSession() as session:
            data = {
                'symbol': symbol,
                'interval': '4h',
                'indicators': ['RSI', 'MACD', 'MA_20'],
                'user_id': user_id
            }

            async with session.post(
                f"{BACKEND_URL}/api/analyze/async",
                json=data,
                timeout=aiohttp.ClientTimeout(total=10)  # Уменьшен таймаут
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None

    except asyncio.TimeoutError:
        logger.warning(f"Backend timeout during analysis start for {user_id}")
        return None
    except Exception as e:
        logger.error(f"Error starting async analysis: {e}")
        return None

async def get_analysis_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Получение статуса анализа"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BACKEND_URL}/api/analyze/status/{task_id}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None

    except Exception as e:
        logger.error(f"Error getting analysis status: {e}")
        return None

async def send_analysis_notification(user_id: str, task_id: str, symbol: str, status: str):
    """Отправка уведомления о статусе анализа"""
    try:
        if status == "completed":
            text = f"""
✅ <b>Анализ завершен!</b>

<b>Пара:</b> {symbol}
<b>ID задачи:</b> {task_id}

Результат готов к просмотру.
            """

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="📊 Посмотреть результат",
                    web_app=WebAppInfo(url=f"{WEBAPP_URL}/analysis/result/{task_id}")
                )],
                [InlineKeyboardButton(
                    text="🚀 Новый анализ",
                    callback_data="quick_analysis"
                )]
            ])

        elif status == "failed":
            text = f"""
❌ <b>Анализ не удался</b>

<b>Пара:</b> {symbol}
<b>ID задачи:</b> {task_id}

Попробуйте запустить анализ еще раз.
            """

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="🔄 Попробовать снова",
                    callback_data=f"analyze_{symbol}"
                )]
            ])
        else:
            return  # Не отправляем уведомления для промежуточных статусов

        await bot.send_message(
            chat_id=int(user_id),
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

        logger.info(f"Analysis notification sent to user {user_id}: {status}")

    except Exception as e:
        logger.error(f"Error sending analysis notification: {e}")

# === BOT SETUP ===
async def set_bot_commands():
    """Установка команд бота"""
    commands = [
        BotCommand(command="start", description="🚀 Главное меню"),
        BotCommand(command="help", description="📚 Справка"),
        BotCommand(command="settings", description="⚙️ Настройки"),
    ]
    
    await bot.set_my_commands(commands, BotCommandScopeDefault())

# Регистрация роутера
dp.include_router(router)

# === WEBHOOK SETUP ===
async def on_startup():
    """Инициализация при запуске"""
    await set_bot_commands()
    
    if WEBHOOK_URL:
        webhook_url = f"{WEBHOOK_URL.rstrip('/')}{WEBHOOK_PATH}"
        await bot.set_webhook(
            url=webhook_url,
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=True
        )
        logger.info(f"Webhook set to: {webhook_url}")
    else:
        logger.info("Starting in polling mode")

async def on_shutdown():
    """Очистка при завершении"""
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()

# === MAIN FUNCTION ===
async def main():
    """Главная функция запуска бота"""
    try:
        await on_startup()
        
        if WEBHOOK_URL:
            # Webhook mode
            app = web.Application()

            # Добавляем middleware для обработки ошибок
            async def error_middleware(request, handler):
                try:
                    return await handler(request)
                except Exception as e:
                    logger.error(f"Webhook error: {e}")
                    return web.Response(status=500, text="Internal Server Error")

            app.middlewares.append(error_middleware)

            # Добавляем health check endpoint
            async def health_check(request):
                return web.Response(text="OK", status=200)

            app.router.add_get("/health", health_check)

            webhook_requests_handler = SimpleRequestHandler(
                dispatcher=dp,
                bot=bot,
                secret_token=WEBHOOK_SECRET
            )
            webhook_requests_handler.register(app, path=WEBHOOK_PATH)

            setup_application(app, dp, bot=bot)

            return app
        else:
            # Polling mode
            await dp.start_polling(bot, skip_updates=True)
            
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise
    finally:
        await on_shutdown()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    if WEBHOOK_URL:
        # Для webhook режима нужен web server
        web.run_app(main(), host="0.0.0.0", port=8000)
    else:
        # Polling режим
        asyncio.run(main())
