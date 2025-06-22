# production/bot/app.py

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google.cloud import secretmanager, firestore
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import json


class ProductionBotConfig:
    """Продакшн конфигурация для бота"""

    def __init__(self):
        # Cloud Run автоматически устанавливает GOOGLE_CLOUD_PROJECT
        self.gcp_project_id = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT") or "chartgenius-444017"
        self.environment = "production"
        self.admin_id = int(os.getenv("ADMIN_TELEGRAM_ID", "299820674"))
        self.webapp_url = self._get_webapp_url()
        self.webhook_url = self._get_webhook_url()
        self.use_webhook = os.getenv("USE_WEBHOOK", "true").lower() == "true"
        # Cloud Run резервирует PORT, используем SERVER_PORT или fallback на PORT
        self.port = int(os.getenv("SERVER_PORT", os.getenv("PORT", "8080")))

        # Отключаем Firestore для упрощения
        self.db = None

        # Настройка логирования
        self._setup_logging()

        # Логирование URL для отладки
        self.logger = logging.getLogger("ChartGeniusBotConfig")
        self.logger.info(f"WebApp URL: {repr(self.webapp_url)}")
        self.logger.info(f"Webhook URL: {repr(self.webhook_url)}")
        self.logger.info(f"Port: {self.port}")
        self.logger.info(f"Use webhook: {self.use_webhook}")
        
    def _get_webapp_url(self) -> str:
        """Получение URL веб-приложения"""
        region = os.getenv("GCP_REGION", "europe-west1")
        url = f"https://chartgenius-frontend-169129692197.{region}.run.app"
        # Очищаем URL от невидимых символов \r и \n
        return self._clean_url(url)

    def _get_webhook_url(self) -> str:
        """Получение URL для webhook"""
        # Используем новый URL бота
        url = "https://chartgenius-bot-new-169129692197.europe-west1.run.app/webhook"
        return self._clean_url(url)

    def _clean_url(self, url: str) -> str:
        """Очистка URL от невидимых символов включая \r"""
        if not url:
            return ""
        # Удаляем все невидимые символы и пробелы
        cleaned = url.replace('\r', '').replace('\n', '').replace('\t', '').strip()
        # Дополнительная очистка от всех управляющих символов (ASCII < 32)
        cleaned = ''.join(char for char in cleaned if ord(char) >= 32)
        # Убираем лишние пробелы внутри URL
        cleaned = ' '.join(cleaned.split())
        return cleaned

    def _init_firestore(self):
        """Инициализация Firestore клиента"""
        try:
            if self.gcp_project_id:
                # Используем default credentials для Cloud Run
                return firestore.Client()
            else:
                logging.warning("GCP_PROJECT_ID не установлен, Firestore недоступен")
                return None
        except Exception as e:
            logging.warning(f"Firestore недоступен: {e}")
            return None
    
    def _setup_logging(self):
        """Настройка логирования для продакшн"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        
        # Отключаем debug логи от внешних библиотек
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("telegram").setLevel(logging.INFO)
        
    def get_secret(self, secret_name: str) -> str:
        """Получение секрета из Google Cloud Secret Manager"""
        try:
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{self.gcp_project_id}/secrets/{secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            # Очищаем секрет от лишних символов (включая \r, \n)
            secret_value = response.payload.data.decode("UTF-8")
            return secret_value.replace('\r', '').replace('\n', '').strip()
        except Exception as e:
            logging.error(f"Ошибка получения секрета {secret_name}: {e}")
            raise
    
    def get_telegram_bot_token(self) -> str:
        """Получение токена Telegram бота"""
        # Сначала пытаемся получить из переменной окружения
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if token:
            return token.replace('\r', '').replace('\n', '').strip()

        # Если нет в переменной окружения, пытаемся получить из Secret Manager
        try:
            return self.get_secret("telegram-bot-token")
        except Exception as e:
            logging.error(f"Не удалось получить токен бота: {e}")
            raise


class ChartGeniusProductionBot:
    """Продакшн версия Telegram бота ChartGenius"""
    
    def __init__(self):
        self.config = ProductionBotConfig()
        self.logger = logging.getLogger("ChartGeniusBot")
        
        # Получаем токен из Secret Manager
        self.token = self.config.get_telegram_bot_token()
        
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
        
        self.logger.info("ChartGenius Bot инициализирован в продакшн режиме")
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("webapp", self.webapp_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Обработчик ошибок
        self.application.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        try:
            user = update.effective_user
            self.logger.info(f"Пользователь {user.id} ({user.username}) запустил бота")
            
            # Логируем пользователя (Firestore отключен)
            self.logger.info(f"Пользователь {user.id} ({user.username}) использует бота")
            
            # Создаем клавиатуру с WebApp
            keyboard = [
                [InlineKeyboardButton(
                    "🚀 Открыть ChartGenius",
                    web_app=WebAppInfo(url=self.config.webapp_url)
                )]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            welcome_text = (
                f"👋 Добро пожаловать в ChartGenius, {user.first_name}!\n\n"
                "🔍 Профессиональный анализ криптовалютных рынков\n"
                "📊 Технические индикаторы и паттерны\n"
                "🎯 Торговые рекомендации\n\n"
                "Нажмите кнопку ниже, чтобы начать анализ:"
            )
            
            await update.message.reply_text(
                welcome_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
        except Exception as e:
            self.logger.error(f"Ошибка в start_command: {e}")
            await update.message.reply_text(
                "Произошла ошибка при запуске. Попробуйте позже."
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = (
            "🤖 <b>ChartGenius Bot - Справка</b>\n\n"
            "📋 <b>Доступные команды:</b>\n"
            "/start - Запуск бота и открытие веб-приложения\n"
            "/webapp - Открыть веб-приложение\n"
            "/help - Показать эту справку\n"
            "/status - Статус системы\n\n"
            "🔗 <b>Веб-приложение:</b>\n"
            "Основной функционал доступен через веб-интерфейс.\n"
            "Нажмите кнопку 'Открыть ChartGenius' для доступа к анализу.\n\n"
            "💬 <b>Поддержка:</b>\n"
            "При возникновении проблем обратитесь к администратору."
        )
        
        await update.message.reply_text(help_text, parse_mode='HTML')
    
    async def webapp_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /webapp"""
        keyboard = [
            [InlineKeyboardButton(
                "🚀 Открыть ChartGenius",
                web_app=WebAppInfo(url=self.config.webapp_url)
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔗 Нажмите кнопку ниже для открытия веб-приложения:",
            reply_markup=reply_markup
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status"""
        try:
            # Проверяем доступность Firestore
            db_status = "✅ Подключена" if self.config.db else "❌ Недоступна"
            
            status_text = (
                "📊 <b>Статус системы ChartGenius</b>\n\n"
                f"🤖 Бот: ✅ Работает\n"
                f"🗄️ База данных: {db_status}\n"
                f"🌐 Веб-приложение: ✅ Доступно\n"
                f"🕐 Время: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                f"🏷️ Версия: 1.0.15\n"
                f"🌍 Регион: {os.getenv('GCP_REGION', 'europe-west1')}"
            )
            
            await update.message.reply_text(status_text, parse_mode='HTML')
            
        except Exception as e:
            self.logger.error(f"Ошибка в status_command: {e}")
            await update.message.reply_text("Ошибка получения статуса системы.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        await update.message.reply_text(
            "👋 Для работы с ChartGenius используйте команды бота.\n"
            "Введите /help для получения справки или /webapp для открытия приложения."
        )
    
    async def register_user(self, user):
        """Регистрация или обновление пользователя в Firestore"""
        try:
            if not self.config.db:
                self.logger.warning("Firestore недоступен для регистрации пользователя")
                return
            
            telegram_id = str(user.id)
            user_ref = self.config.db.collection('users').document(telegram_id)
            user_doc = user_ref.get()
            
            # Определяем роль пользователя
            role = "admin" if user.id == self.config.admin_id else "user"
            
            user_data = {
                'telegram_id': telegram_id,
                'username': user.username or '',
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'role': role,
                'last_seen': firestore.SERVER_TIMESTAMP
            }
            
            if user_doc.exists:
                # Обновляем существующего пользователя
                user_ref.update({
                    'username': user_data['username'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'last_seen': user_data['last_seen']
                })
                self.logger.info(f"Обновлен пользователь: {telegram_id}")
            else:
                # Создаем нового пользователя
                user_data['created_at'] = firestore.SERVER_TIMESTAMP
                user_ref.set(user_data)
                self.logger.info(f"Создан новый пользователь: {telegram_id} с ролью {role}")
                
        except Exception as e:
            self.logger.error(f"Ошибка регистрации пользователя {user.id}: {e}")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        self.logger.error(f"Ошибка в боте: {context.error}", exc_info=context.error)
        
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "Произошла ошибка при обработке запроса. "
                    "Попробуйте позже или обратитесь к администратору."
                )
            except Exception as e:
                self.logger.error(f"Ошибка отправки сообщения об ошибке: {e}")
    
    async def setup_webhook(self):
        """Настройка webhook для бота"""
        try:
            await self.application.bot.set_webhook(
                url=self.config.webhook_url,
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            self.logger.info(f"Webhook установлен: {self.config.webhook_url}")
        except Exception as e:
            self.logger.error(f"Ошибка установки webhook: {e}")
            raise

    async def remove_webhook(self):
        """Удаление webhook"""
        try:
            await self.application.bot.delete_webhook(drop_pending_updates=True)
            self.logger.info("Webhook удален")
        except Exception as e:
            self.logger.error(f"Ошибка удаления webhook: {e}")

    def run_polling(self):
        """Запуск бота в polling режиме"""
        self.logger.info("Запуск ChartGenius бота в polling режиме...")
        self.application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )

    def run(self):
        """Запуск бота в выбранном режиме"""
        if self.config.use_webhook:
            self.logger.info("Запуск в webhook режиме...")
            # Webhook режим будет обрабатываться через FastAPI
            return
        else:
            self.run_polling()


# FastAPI приложение для webhook режима
app = FastAPI(
    title="ChartGenius Telegram Bot",
    description="Продакшн Telegram бот для ChartGenius",
    version="1.0.15"
)

# Глобальная переменная для бота
bot_instance = None

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    global bot_instance
    try:
        bot_instance = ChartGeniusProductionBot()

        # ВАЖНО: Инициализируем Application для webhook режима
        await bot_instance.application.initialize()

        # НЕ устанавливаем webhook при старте - это будет сделано отдельно
        logging.info("Бот инициализирован и готов к работе с webhook")

    except Exception as e:
        logging.error(f"Ошибка инициализации бота: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при завершении"""
    global bot_instance
    if bot_instance:
        try:
            if bot_instance.config.use_webhook:
                await bot_instance.remove_webhook()

            # Завершаем работу Application
            await bot_instance.application.shutdown()

        except Exception as e:
            logging.error(f"Ошибка при завершении: {e}")

@app.post("/webhook")
async def webhook_handler(request: Request):
    """Обработчик webhook от Telegram"""
    try:
        if not bot_instance:
            raise HTTPException(status_code=500, detail="Бот не инициализирован")

        # Получаем данные от Telegram
        body = await request.body()
        update_data = json.loads(body.decode('utf-8'))

        # Создаем объект Update
        update = Update.de_json(update_data, bot_instance.application.bot)

        if update:
            # Обрабатываем обновление
            await bot_instance.application.process_update(update)

        return JSONResponse(content={"status": "ok"})

    except Exception as e:
        logging.error(f"Ошибка обработки webhook: {e}")
        raise HTTPException(status_code=500, detail="Ошибка обработки webhook")

@app.get("/health")
async def health_check():
    """Health check для Cloud Run"""
    return {
        "status": "healthy",
        "mode": "webhook" if bot_instance and bot_instance.config.use_webhook else "polling",
        "version": "1.0.15"
    }

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "service": "ChartGenius Telegram Bot",
        "version": "1.0.15",
        "mode": "webhook" if bot_instance and bot_instance.config.use_webhook else "polling"
    }

@app.post("/setup-webhook")
async def setup_webhook_endpoint():
    """Endpoint для ручной настройки webhook"""
    try:
        if not bot_instance:
            raise HTTPException(status_code=500, detail="Бот не инициализирован")

        await bot_instance.setup_webhook()
        return {"status": "success", "message": "Webhook успешно настроен"}

    except Exception as e:
        logging.error(f"Ошибка настройки webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка настройки webhook: {str(e)}")

@app.get("/webhook-info")
async def webhook_info():
    """Получение информации о webhook"""
    try:
        if not bot_instance:
            raise HTTPException(status_code=500, detail="Бот не инициализирован")

        webhook_info = await bot_instance.application.bot.get_webhook_info()
        return {
            "url": webhook_info.url,
            "pending_update_count": webhook_info.pending_update_count,
            "max_connections": webhook_info.max_connections,
            "allowed_updates": webhook_info.allowed_updates
        }

    except Exception as e:
        logging.error(f"Ошибка получения информации о webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения информации о webhook: {str(e)}")

if __name__ == "__main__":
    try:
        config = ProductionBotConfig()

        if config.use_webhook:
            # Запускаем FastAPI сервер для webhook
            logging.info(f"Запуск webhook сервера на порту {config.port}")
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=config.port,
                workers=1,
                access_log=False,
                log_level="info"
            )
        else:
            # Запускаем в polling режиме
            bot = ChartGeniusProductionBot()
            bot.run_polling()

    except Exception as e:
        logging.error(f"Критическая ошибка запуска бота: {e}")
        sys.exit(1)
