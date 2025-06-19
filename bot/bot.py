import os
import logging
import asyncio
import json
import aiohttp
import time
from datetime import datetime, timedelta
from jose import jwt
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

# Настройки
API_BASE = os.getenv("API_URL", "http://backend:8000")
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-frontend-url.com")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем приложение бота
app = Application.builder().token(TOKEN).build()

def create_jwt_token(telegram_id: str) -> str:
    """Создает JWT токен для пользователя"""
    expire = datetime.utcnow() + timedelta(days=7)
    payload = {
        "sub": telegram_id,
        "exp": expire,
        "telegram_id": telegram_id
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

async def register_user(query) -> bool:
    """Регистрирует пользователя в системе"""
    try:
        user = query.from_user
        user_data = {
            "id": str(user.id),
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "username": user.username or "",
            "photo_url": "",
            "auth_date": str(int(time.time()))
        }

        # Создаем hash для аутентификации
        import hashlib
        import hmac

        secret_key = hashlib.sha256(TOKEN.encode()).digest()
        data_check_string = "\n".join(f"{k}={user_data[k]}" for k in sorted(user_data.keys()) if k != "hash")
        user_data["hash"] = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        # Отправляем данные на backend для регистрации
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{API_BASE}/auth/telegram", json=user_data) as response:
                if response.status == 200:
                    logger.info(f"Пользователь {user.id} успешно зарегистрирован")
                    return True
                else:
                    logger.error(f"Ошибка регистрации пользователя {user.id}: {response.status}")
                    return False

    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя: {e}")
        return False

async def show_dashboard(query):
    """Показывает личный кабинет пользователя"""
    try:
        # Создаем JWT токен для доступа к веб-интерфейсу
        token = create_jwt_token(str(query.from_user.id))

        # Создаем ссылку на личный кабинет
        dashboard_link = f"{WEBAPP_URL}?token={token}&page=dashboard"

        # Получаем информацию о подписке
        async with aiohttp.ClientSession() as session:
            headers = {"X-Telegram-Id": str(query.from_user.id)}
            try:
                async with session.get(f"{API_BASE}/api/user/subscription", headers=headers) as response:
                    if response.status == 200:
                        sub_data = await response.json()
                        subscription_status = sub_data.get('level', 'none')
                        expires_at = sub_data.get('expires_at', 'N/A')
                    else:
                        subscription_status = 'none'
                        expires_at = 'N/A'
            except:
                subscription_status = 'none'
                expires_at = 'N/A'

        # Формируем сообщение о статусе
        status_emoji = "✅" if subscription_status != 'none' else "❌"
        status_text = {
            'premium': 'Премиум',
            'basic': 'Базовая',
            'none': 'Отсутствует',
            'expired': 'Истекла'
        }.get(subscription_status, 'Неизвестно')

        keyboard = [
            [InlineKeyboardButton("🌐 Открыть личный кабинет", url=dashboard_link)],
            [InlineKeyboardButton("📊 Получить анализ", callback_data="analyse")],
            [InlineKeyboardButton("📈 Полный веб-интерфейс", url=f"{WEBAPP_URL}?token={token}")],
            [InlineKeyboardButton("🔙 Назад", callback_data="continue")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message_text = (
            f"👤 <b>Личный кабинет</b>\n\n"
            f"🆔 ID: <code>{query.from_user.id}</code>\n"
            f"👤 Имя: {query.from_user.first_name or 'Не указано'}\n"
            f"📧 Username: @{query.from_user.username or 'Не указан'}\n\n"
            f"{status_emoji} <b>Подписка:</b> {status_text}\n"
            f"📅 <b>Действует до:</b> {expires_at}\n\n"
            f"Нажмите кнопку ниже для доступа к полному функционалу:"
        )

        await query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode='HTML')

    except Exception as e:
        logger.error(f"Ошибка при отображении личного кабинета: {e}")
        await query.edit_message_text(
            "❌ Произошла ошибка при загрузке личного кабинета. Попробуйте позже."
        )

async def get_login_payload(query) -> dict:
    """Создает payload для аутентификации через Telegram"""
    user = query.from_user
    auth_date = int(time.time())
    
    # Создаем данные для аутентификации
    data = {
        "id": str(user.id),
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "username": user.username or "",
        "photo_url": "",  # Можно добавить логику для получения фото
        "auth_date": str(auth_date)
    }
    
    # Вычисляем hash (упрощенная версия для демо)
    # В реальном проекте нужно использовать правильный алгоритм из telegram-webapp-auth
    import hashlib
    import hmac
    
    secret_key = hashlib.sha256(TOKEN.encode()).digest()
    data_check_string = "\n".join(f"{k}={data[k]}" for k in sorted(data.keys()))
    data["hash"] = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    return data

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = [[InlineKeyboardButton("📈 Продолжить", callback_data="continue")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "👋 Добро пожаловать в ChartGenius!\n\n"
        "Профессиональная платформа для анализа криптовалют с использованием "
        "передовых технических индикаторов и алгоритмов прогнозирования.\n\n"
        "🔹 Многоуровневый технический анализ\n"
        "🔹 Прогнозирование ценовых движений\n"
        "🔹 Торговые рекомендации\n"
        "🔹 Интерактивные графики\n\n"
        "Нажмите кнопку ниже для продолжения работы с системой:"
    )

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback запросов"""
    query = update.callback_query
    await query.answer()

    if query.data == "continue":
        # Автоматическая регистрация пользователя
        await register_user(query)

        # Показываем меню выбора
        keyboard = [
            [InlineKeyboardButton("📊 Получить анализ", callback_data="analyse")],
            [InlineKeyboardButton("👤 Личный кабинет", callback_data="dashboard")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "✅ Добро пожаловать в систему!\n\n"
            "Выберите действие:",
            reply_markup=reply_markup
        )
        return

    elif query.data == "dashboard":
        # Перенаправляем в личный кабинет
        await show_dashboard(query)
        return

    elif query.data == "analyse":
        await query.edit_message_text("⏳ Проверяю подписку и генерирую анализ...")
        
        try:
            # Проверяем подписку через API
            async with aiohttp.ClientSession() as session:
                headers = {"X-Telegram-Id": str(query.from_user.id)}
                async with session.post(f"{API_BASE}/api/analysis/simple", headers=headers) as response:
                    if response.status == 402:
                        # Подписка отсутствует
                        keyboard = [[InlineKeyboardButton("💳 Оформить подписку", url="https://your-payment-url.com")]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        await query.edit_message_text(
                            "🚫 Для получения анализа необходима активная подписка.\n\n"
                            "Оформите подписку, чтобы получить доступ к профессиональному анализу криптовалют.",
                            reply_markup=reply_markup
                        )
                        return
                    
                    if response.status != 200:
                        await query.edit_message_text(
                            "❌ Произошла ошибка при генерации анализа. Попробуйте позже."
                        )
                        return
                    
                    analysis_data = await response.json()
            
            # Создаем JWT токен для доступа к веб-интерфейсу
            token = create_jwt_token(str(query.from_user.id))
            
            # Создаем ссылку на веб-интерфейс с полным анализом
            web_link = f"{WEBAPP_URL}?token={token}&analysis_type=full&symbol={analysis_data.get('symbol', 'BTCUSDT')}"
            
            # Формируем краткий отчет
            analysis = analysis_data.get('analysis', {})
            primary = analysis_data.get('primary_analysis', {})

            # Используем данные из primary_analysis для краткого отчета
            trend = primary.get('trend', 'Не определен')
            signal = primary.get('signal', 'Нейтральный')
            risk_level = primary.get('risk_level', 'Средний')
            main_recommendation = primary.get('main_recommendation', 'Ожидание')

            # Определяем эмодзи для сигнала
            signal_emoji = {
                'Long': '🟢',
                'Short': '🔴',
                'Hold': '🟡',
                'Нейтральный': '⚪'
            }.get(signal, '⚪')

            # Определяем эмодзи для риска
            risk_emoji = {
                'Низкий': '🟢',
                'Средний': '🟡',
                'Высокий': '🔴'
            }.get(risk_level, '🟡')

            keyboard = [
                [InlineKeyboardButton("📊 Открыть полный отчет", url=web_link)],
                [InlineKeyboardButton("🔄 Новый анализ", callback_data="analyse")],
                [InlineKeyboardButton("👤 Личный кабинет", callback_data="dashboard")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            message_text = (
                f"✅ <b>Анализ готов!</b>\n\n"
                f"📈 <b>Символ:</b> {analysis_data.get('symbol', 'BTC/USDT')}\n"
                f"📊 <b>Тренд:</b> {trend}\n"
                f"{signal_emoji} <b>Сигнал:</b> {signal}\n"
                f"{risk_emoji} <b>Риск:</b> {risk_level}\n\n"
                f"💡 <b>Рекомендация:</b>\n{main_recommendation}\n\n"
                f"Нажмите кнопку ниже для просмотра полного интерактивного отчета с графиками:"
            )
            
            await query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error in callback handler: {e}")
            await query.edit_message_text(
                "❌ Произошла ошибка. Попробуйте позже или обратитесь в поддержку."
            )

# Регистрируем обработчики
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback))

def main():
    """Запуск бота"""
    port = int(os.getenv("PORT", 8080))
    webhook_url = os.getenv("BOT_WEBHOOK_URL")
    
    if webhook_url:
        # Запуск с webhook для продакшена
        logger.info(f"Starting bot with webhook: {webhook_url}")
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=TOKEN,
            webhook_url=f"{webhook_url}/{TOKEN}"
        )
    else:
        # Запуск с polling для разработки
        logger.info("Starting bot with polling")
        app.run_polling()

if __name__ == "__main__":
    main()
