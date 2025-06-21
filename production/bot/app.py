# production/bot/app.py

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Добавляем путь к backend для импортов
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebApp
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google.cloud import secretmanager
from backend.config.config import db
from backend.auth.dependencies import create_jwt_token
from google.cloud import firestore


class ProductionBotConfig:
    """Продакшн конфигурация для бота"""
    
    def __init__(self):
        self.gcp_project_id = os.getenv("GCP_PROJECT_ID")
        self.environment = "production"
        self.admin_id = int(os.getenv("ADMIN_TELEGRAM_ID", "299820674"))
        self.webapp_url = self._get_webapp_url()
        
        # Настройка логирования
        self._setup_logging()
        
    def _get_webapp_url(self) -> str:
        """Получение URL веб-приложения"""
        region = os.getenv("GCP_REGION", "europe-west1")
        return f"https://chartgenius-frontend-{region}-a.run.app"
    
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
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logging.error(f"Ошибка получения секрета {secret_name}: {e}")
            raise
    
    def get_telegram_bot_token(self) -> str:
        """Получение токена Telegram бота"""
        return self.get_secret("telegram-bot-token")


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
            
            # Регистрируем или обновляем пользователя в Firestore
            await self.register_user(user)
            
            # Создаем клавиатуру с WebApp
            keyboard = [
                [InlineKeyboardButton(
                    "🚀 Открыть ChartGenius", 
                    web_app=WebApp(url=self.config.webapp_url)
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
                web_app=WebApp(url=self.config.webapp_url)
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
            db_status = "✅ Подключена" if db else "❌ Недоступна"
            
            status_text = (
                "📊 <b>Статус системы ChartGenius</b>\n\n"
                f"🤖 Бот: ✅ Работает\n"
                f"🗄️ База данных: {db_status}\n"
                f"🌐 Веб-приложение: ✅ Доступно\n"
                f"🕐 Время: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                f"🏷️ Версия: 1.0.0\n"
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
            if not db:
                self.logger.warning("Firestore недоступен для регистрации пользователя")
                return
            
            telegram_id = str(user.id)
            user_ref = db.collection('users').document(telegram_id)
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
    
    def run(self):
        """Запуск бота"""
        self.logger.info("Запуск ChartGenius бота в продакшн режиме...")
        self.application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )


if __name__ == "__main__":
    try:
        bot = ChartGeniusProductionBot()
        bot.run()
    except Exception as e:
        logging.error(f"Критическая ошибка запуска бота: {e}")
        sys.exit(1)
