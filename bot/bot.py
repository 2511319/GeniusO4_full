# bot/bot.py

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Добавляем путь к backend для импортов
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebApp
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from backend.config.config import logger, db
from backend.auth.dependencies import create_jwt_token
from google.cloud import firestore


class ChartGeniusBot:
    """Основной класс Telegram бота"""
    
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.admin_id = int(os.getenv("ADMIN_TELEGRAM_ID", "299820674"))
        self.webapp_url = os.getenv("WEBAPP_URL", "https://your-webapp-url.com")
        
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN не установлен")
        
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        # Основные команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Пользовательские команды
        self.application.add_handler(CommandHandler("watch", self.watch_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        
        # Модераторские команды
        self.application.add_handler(CommandHandler("ban", self.ban_command))
        self.application.add_handler(CommandHandler("unban", self.unban_command))
        self.application.add_handler(CommandHandler("review", self.review_command))
        
        # Админские команды
        self.application.add_handler(CommandHandler("setrole", self.setrole_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("broadcast", self.broadcast_command))
        self.application.add_handler(CommandHandler("gc", self.gc_command))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        try:
            user = update.effective_user
            telegram_id = str(user.id)
            
            # Создаем или обновляем пользователя в Firestore
            await self.get_or_create_user(telegram_id, user)
            
            # Создаем клавиатуру с кнопками
            keyboard = [
                [InlineKeyboardButton(
                    "🚀 Открыть терминал", 
                    web_app=WebApp(url=self.webapp_url)
                )],
                [
                    InlineKeyboardButton("📊 Мой watch-лист", callback_data="watchlist"),
                    InlineKeyboardButton("⚙️ Настройки", callback_data="settings")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            welcome_text = (
                f"👋 Добро пожаловать в ChartGenius, {user.first_name}!\n\n"
                "🔍 Анализируйте криптовалютные рынки с помощью ИИ\n"
                "📈 Получайте детальные технические анализы\n"
                "⚡ Быстрый доступ через мини-приложение\n\n"
                "Выберите действие:"
            )
            
            await update.message.reply_text(welcome_text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ошибка в команде /start: {e}")
            await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        try:
            user = update.effective_user
            telegram_id = str(user.id)
            
            # Получаем роль пользователя
            user_data = await self.get_user_data(telegram_id)
            role = user_data.get('role', 'user')
            
            # Базовые команды для всех
            help_text = "📋 **Доступные команды:**\n\n"
            help_text += "👤 **Пользователь:**\n"
            help_text += "/start - Главное меню\n"
            help_text += "/help - Список команд\n"
            help_text += "/watch BTC,ETH - Обновить watch-лист\n"
            help_text += "/settings lang=ru tz=UTC+3 - Настройки\n\n"
            
            # Команды для модераторов
            if role in ['moderator', 'admin']:
                help_text += "🛡️ **Модератор:**\n"
                help_text += "/ban @user_id 15 - Забанить на 15 дней\n"
                help_text += "/unban @user_id - Разбанить\n"
                help_text += "/review <ulid> <reason> - Пометить анализ\n\n"
            
            # Команды для админов
            if role == 'admin':
                help_text += "👑 **Администратор:**\n"
                help_text += "/setrole @user_id vip 60 - Установить роль\n"
                help_text += "/stats - Статистика\n"
                help_text += "/broadcast <текст> - Рассылка\n"
                help_text += "/gc - Очистка данных\n"
            
            await update.message.reply_text(help_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Ошибка в команде /help: {e}")
            await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
    
    async def watch_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /watch"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "📊 Использование: /watch BTC,ETH,ADA\n"
                    "Укажите символы через запятую для обновления watch-листа"
                )
                return
            
            symbols_str = ' '.join(context.args)
            symbols = [s.strip().upper() for s in symbols_str.split(',')]
            
            # Ограничиваем количество символов
            if len(symbols) > 50:
                await update.message.reply_text("❌ Максимум 50 символов в watch-листе")
                return
            
            telegram_id = str(update.effective_user.id)
            
            # Сохраняем в Firestore
            if db:
                watchlist_ref = db.collection('watchlists').document(telegram_id)
                watchlist_ref.set({
                    'symbols': symbols,
                    'updated_at': firestore.SERVER_TIMESTAMP
                })
            
            await update.message.reply_text(
                f"✅ Watch-лист обновлён!\n"
                f"📊 Символы ({len(symbols)}): {', '.join(symbols)}"
            )
            
        except Exception as e:
            logger.error(f"Ошибка в команде /watch: {e}")
            await update.message.reply_text("❌ Ошибка обновления watch-листа")
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /settings"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "⚙️ Использование: /settings lang=ru tz=UTC+3\n"
                    "Доступные параметры:\n"
                    "• lang - язык (ru, en)\n"
                    "• tz - часовой пояс (UTC+3, UTC-5, etc.)"
                )
                return
            
            settings = {}
            for arg in context.args:
                if '=' in arg:
                    key, value = arg.split('=', 1)
                    settings[key] = value
            
            telegram_id = str(update.effective_user.id)
            
            # Сохраняем настройки в Firestore
            if db:
                settings_ref = db.collection('user_settings').document(telegram_id)
                settings_ref.set({
                    **settings,
                    'updated_at': firestore.SERVER_TIMESTAMP
                })
            
            await update.message.reply_text("🛠 Настройки сохранены!")
            
        except Exception as e:
            logger.error(f"Ошибка в команде /settings: {e}")
            await update.message.reply_text("❌ Ошибка сохранения настроек")
    
    async def get_or_create_user(self, telegram_id: str, user) -> Dict[str, Any]:
        """Получение или создание пользователя в Firestore"""
        try:
            if not db:
                return {}
            
            user_ref = db.collection('users').document(telegram_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                # Обновляем данные пользователя
                user_ref.update({
                    'username': user.username or '',
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'last_seen': firestore.SERVER_TIMESTAMP
                })
                return user_doc.to_dict()
            else:
                # Создаем нового пользователя
                role = "admin" if int(telegram_id) == self.admin_id else "user"
                
                new_user = {
                    'telegram_id': telegram_id,
                    'username': user.username or '',
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'role': role,
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'last_seen': firestore.SERVER_TIMESTAMP
                }
                
                user_ref.set(new_user)
                logger.info(f"Создан новый пользователь: {telegram_id} с ролью {role}")
                
                return new_user
                
        except Exception as e:
            logger.error(f"Ошибка работы с пользователем: {e}")
            return {}
    
    async def get_user_data(self, telegram_id: str) -> Dict[str, Any]:
        """Получение данных пользователя"""
        try:
            if not db:
                return {}
            
            user_ref = db.collection('users').document(telegram_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                return user_doc.to_dict()
            
            return {}
            
        except Exception as e:
            logger.error(f"Ошибка получения данных пользователя: {e}")
            return {}
    
    async def ban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /ban (только для модераторов)"""
        try:
            telegram_id = str(update.effective_user.id)
            user_data = await self.get_user_data(telegram_id)
            role = user_data.get('role', 'user')

            if role not in ['moderator', 'admin']:
                await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
                return

            if len(context.args) < 1:
                await update.message.reply_text("Использование: /ban @user_id [дни] [причина]")
                return

            target_id = context.args[0].replace('@', '')
            days = int(context.args[1]) if len(context.args) > 1 else 30
            reason = ' '.join(context.args[2:]) if len(context.args) > 2 else "Нарушение правил"

            # Создаем бан в Firestore
            if db:
                ban_ref = db.collection('bans').document(target_id)
                expires_at = datetime.utcnow() + timedelta(days=days)

                ban_ref.set({
                    'telegram_id': target_id,
                    'moderator_id': telegram_id,
                    'reason': reason,
                    'expires_at': expires_at,
                    'created_at': firestore.SERVER_TIMESTAMP
                })

            await update.message.reply_text(f"✅ Пользователь {target_id} забанен на {days} дней")

        except Exception as e:
            logger.error(f"Ошибка в команде /ban: {e}")
            await update.message.reply_text("❌ Ошибка выполнения команды")

    async def unban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /unban (только для модераторов)"""
        try:
            telegram_id = str(update.effective_user.id)
            user_data = await self.get_user_data(telegram_id)
            role = user_data.get('role', 'user')

            if role not in ['moderator', 'admin']:
                await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
                return

            if len(context.args) < 1:
                await update.message.reply_text("Использование: /unban @user_id")
                return

            target_id = context.args[0].replace('@', '')

            # Удаляем бан из Firestore
            if db:
                ban_ref = db.collection('bans').document(target_id)
                ban_ref.delete()

            await update.message.reply_text(f"✅ Пользователь {target_id} разбанен")

        except Exception as e:
            logger.error(f"Ошибка в команде /unban: {e}")
            await update.message.reply_text("❌ Ошибка выполнения команды")

    async def review_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /review (только для модераторов)"""
        try:
            telegram_id = str(update.effective_user.id)
            user_data = await self.get_user_data(telegram_id)
            role = user_data.get('role', 'user')

            if role not in ['moderator', 'admin']:
                await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
                return

            if len(context.args) < 2:
                await update.message.reply_text("Использование: /review <ulid> <причина>")
                return

            analysis_ulid = context.args[0]
            reason = ' '.join(context.args[1:])

            # Создаем флаг в Firestore
            if db:
                flag_ref = db.collection('flags').document(analysis_ulid)
                flag_ref.set({
                    'analysis_ulid': analysis_ulid,
                    'reason': reason,
                    'flagged_by': telegram_id,
                    'ts': firestore.SERVER_TIMESTAMP
                })

            await update.message.reply_text(f"✅ Анализ {analysis_ulid} помечен для проверки")

        except Exception as e:
            logger.error(f"Ошибка в команде /review: {e}")
            await update.message.reply_text("❌ Ошибка выполнения команды")

    async def setrole_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /setrole (только для админов)"""
        try:
            telegram_id = str(update.effective_user.id)
            user_data = await self.get_user_data(telegram_id)
            role = user_data.get('role', 'user')

            if role != 'admin':
                await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
                return

            if len(context.args) < 2:
                await update.message.reply_text("Использование: /setrole @user_id роль [дни_подписки]")
                return

            target_id = context.args[0].replace('@', '')
            new_role = context.args[1]
            sub_days = int(context.args[2]) if len(context.args) > 2 else 0

            valid_roles = ['user', 'premium', 'vip', 'moderator', 'admin']
            if new_role not in valid_roles:
                await update.message.reply_text(f"❌ Неверная роль. Доступные: {', '.join(valid_roles)}")
                return

            # Обновляем роль в Firestore
            if db:
                user_ref = db.collection('users').document(target_id)
                user_ref.update({
                    'role': new_role,
                    'updated_at': firestore.SERVER_TIMESTAMP
                })

                # Если указаны дни подписки
                if sub_days > 0:
                    sub_ref = db.collection('subscriptions').document(target_id)
                    expires_at = datetime.utcnow() + timedelta(days=sub_days)

                    sub_ref.set({
                        'level': new_role if new_role in ['premium', 'vip'] else 'premium',
                        'expires_at': expires_at,
                        'created_at': firestore.SERVER_TIMESTAMP
                    })

            message = f"✅ Роль {new_role} установлена пользователю {target_id}"
            if sub_days > 0:
                message += f"\n📅 Подписка на {sub_days} дней"

            await update.message.reply_text(message)

        except Exception as e:
            logger.error(f"Ошибка в команде /setrole: {e}")
            await update.message.reply_text("❌ Ошибка выполнения команды")

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /stats (только для админов)"""
        try:
            telegram_id = str(update.effective_user.id)
            user_data = await self.get_user_data(telegram_id)
            role = user_data.get('role', 'user')

            if role != 'admin':
                await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
                return

            if not db:
                await update.message.reply_text("❌ База данных недоступна")
                return

            # Получаем статистику пользователей
            users_ref = db.collection('users')
            users = users_ref.stream()

            role_counts = {'admin': 0, 'moderator': 0, 'vip': 0, 'premium': 0, 'user': 0}
            total_users = 0

            for user in users:
                total_users += 1
                user_data = user.to_dict()
                user_role = user_data.get('role', 'user')
                if user_role in role_counts:
                    role_counts[user_role] += 1

            # Получаем активные подписки
            subs_ref = db.collection('subscriptions')
            subs = subs_ref.stream()

            active_premium = 0
            active_vip = 0
            now = datetime.utcnow()

            for sub in subs:
                sub_data = sub.to_dict()
                expires_at = sub_data.get('expires_at')
                level = sub_data.get('level', '')

                if expires_at and expires_at > now:
                    if level == 'premium':
                        active_premium += 1
                    elif level == 'vip':
                        active_vip += 1

            stats_text = f"📊 **Статистика ChartGenius**\n\n"
            stats_text += f"👥 Всего пользователей: {total_users}\n\n"
            stats_text += f"**По ролям:**\n"
            stats_text += f"👑 Админы: {role_counts['admin']}\n"
            stats_text += f"🛡️ Модераторы: {role_counts['moderator']}\n"
            stats_text += f"💎 VIP: {role_counts['vip']}\n"
            stats_text += f"⭐ Premium: {role_counts['premium']}\n"
            stats_text += f"👤 Обычные: {role_counts['user']}\n\n"
            stats_text += f"**Активные подписки:**\n"
            stats_text += f"⭐ Premium: {active_premium}\n"
            stats_text += f"💎 VIP: {active_vip}"

            await update.message.reply_text(stats_text, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Ошибка в команде /stats: {e}")
            await update.message.reply_text("❌ Ошибка получения статистики")

    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /broadcast (только для админов)"""
        try:
            telegram_id = str(update.effective_user.id)
            user_data = await self.get_user_data(telegram_id)
            role = user_data.get('role', 'user')

            if role != 'admin':
                await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
                return

            if not context.args:
                await update.message.reply_text("Использование: /broadcast <текст сообщения>")
                return

            message_text = ' '.join(context.args)

            # Получаем всех пользователей
            if db:
                users_ref = db.collection('users')
                users = users_ref.stream()

                user_ids = []
                for user in users:
                    user_ids.append(user.id)

                # Сохраняем задачу на рассылку
                broadcast_ref = db.collection('broadcast_queue').document()
                broadcast_ref.set({
                    'text': message_text,
                    'user_ids': user_ids,
                    'status': 'pending',
                    'created_at': firestore.SERVER_TIMESTAMP
                })

            await update.message.reply_text(f"✅ Рассылка запланирована для {len(user_ids)} пользователей")

        except Exception as e:
            logger.error(f"Ошибка в команде /broadcast: {e}")
            await update.message.reply_text("❌ Ошибка создания рассылки")

    async def gc_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /gc (только для админов)"""
        try:
            telegram_id = str(update.effective_user.id)
            user_data = await self.get_user_data(telegram_id)
            role = user_data.get('role', 'user')

            if role != 'admin':
                await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
                return

            if not db:
                await update.message.reply_text("❌ База данных недоступна")
                return

            # Удаляем старые анализы (>30 дней)
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            analyses_ref = db.collection('analyses')
            old_analyses = analyses_ref.where('created_at', '<', cutoff_date).stream()

            deleted_analyses = 0
            for analysis in old_analyses:
                analysis.reference.delete()
                deleted_analyses += 1

            # Удаляем старые флаги (>14 дней)
            flags_cutoff = datetime.utcnow() - timedelta(days=14)
            flags_ref = db.collection('flags')
            old_flags = flags_ref.where('ts', '<', flags_cutoff).stream()

            deleted_flags = 0
            for flag in old_flags:
                flag.reference.delete()
                deleted_flags += 1

            result_text = f"🧹 **Очистка завершена:**\n"
            result_text += f"📊 Удалено анализов: {deleted_analyses}\n"
            result_text += f"🚩 Удалено флагов: {deleted_flags}"

            await update.message.reply_text(result_text, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Ошибка в команде /gc: {e}")
            await update.message.reply_text("❌ Ошибка очистки данных")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        await update.message.reply_text(
            "👋 Используйте команды для взаимодействия с ботом.\n"
            "Введите /help для списка доступных команд."
        )
    
    def run(self):
        """Запуск бота"""
        logger.info("Запуск ChartGenius бота...")
        self.application.run_polling()


if __name__ == "__main__":
    try:
        bot = ChartGeniusBot()
        bot.run()
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        sys.exit(1)
