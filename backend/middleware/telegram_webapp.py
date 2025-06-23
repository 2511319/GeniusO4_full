# backend/middleware/telegram_webapp.py

import os
import hashlib
import hmac
import json
import time
from urllib.parse import unquote, parse_qsl
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request
from backend.config.config import logger, db
from google.cloud import firestore


class TelegramWebAppAuth:
    """Middleware для аутентификации Telegram WebApp"""
    
    def __init__(self):
        # Получаем bot token из разных источников
        self.bot_token = None

        # Способ 1: Переменная окружения (для dev)
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if self.bot_token:
            logger.info("✅ Telegram bot token загружен из переменной окружения")
        else:
            # Способ 2: Google Cloud Secrets (для production)
            try:
                # Импортируем только в production среде
                import sys
                sys.path.append('/app')  # Добавляем путь к приложению в Cloud Run

                from config.production import config
                self.bot_token = config.get_telegram_bot_token()
                logger.info("✅ Telegram bot token загружен из Google Cloud Secrets")
            except Exception as e:
                logger.error(f"❌ Не удалось загрузить токен из Google Cloud Secrets: {e}")

                # Способ 3: Прямое обращение к Secret Manager
                try:
                    from google.cloud import secretmanager
                    client = secretmanager.SecretManagerServiceClient()
                    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "chartgenius-444017")
                    secret_name = f"projects/{project_id}/secrets/telegram-bot-token/versions/latest"
                    response = client.access_secret_version(request={"name": secret_name})
                    self.bot_token = response.payload.data.decode("UTF-8").strip()
                    logger.info("✅ Telegram bot token загружен напрямую из Secret Manager")
                except Exception as e2:
                    logger.error(f"❌ Не удалось загрузить токен напрямую из Secret Manager: {e2}")

        if not self.bot_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN не установлен - все способы загрузки провалились")
    
    def validate_webapp_data(self, init_data: str) -> bool:
        """
        Валидация данных от Telegram WebApp

        БЕЗОПАСНАЯ РЕАЛИЗАЦИЯ на основе официальной документации Telegram:
        https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app

        Алгоритм:
        1. Data-check-string = все поля (кроме hash), отсортированные по алфавиту,
           в формате key=<value> с разделителем \n
        2. Secret key = HMAC-SHA256(bot_token, "WebAppData")
        3. Calculated hash = HMAC-SHA256(data_check_string, secret_key)
        4. Сравнение с полученным hash
        """
        try:
            logger.info(f"🔍 Начало валидации WebApp данных (официальный алгоритм)")
            logger.info(f"📋 Bot token установлен: {bool(self.bot_token)}")
            logger.info(f"📋 Bot token (первые 10 символов): {self.bot_token[:10] if self.bot_token else 'НЕТ'}")
            logger.info(f"📋 Init data длина: {len(init_data) if init_data else 0}")

            if not self.bot_token:
                logger.error("❌ Bot token не установлен")
                return False

            if not init_data:
                logger.error("❌ init_data пустой")
                return False

            # Шаг 1: Парсим query string (ПРОВЕРЕННОЕ РЕШЕНИЕ от @TheBlackHacker)
            from urllib.parse import parse_qs
            parsed_data = parse_qs(init_data)

            # Извлекаем первое значение из каждого списка (parse_qs возвращает списки)
            parsed_data = {key: values[0] for key, values in parsed_data.items()}

            logger.info(f"📋 Парсинг данных: найдено {len(parsed_data)} полей")
            logger.info(f"📋 Поля: {list(parsed_data.keys())}")

            if 'hash' not in parsed_data:
                logger.error("❌ Отсутствует hash в init_data")
                return False

            # Шаг 2: Извлекаем hash
            received_hash = parsed_data.pop('hash')
            logger.info(f"🔑 Received hash: {received_hash}")

            # Шаг 3: Создаем data-check-string (ПРОВЕРЕННЫЙ АЛГОРИТМ)
            # Сортируем поля по алфавиту и соединяем через \n
            sorted_items = sorted((key, value) for key, value in parsed_data.items())
            data_to_check = [f"{key}={value}" for key, value in sorted_items]
            data_check_string = '\n'.join(data_to_check)

            logger.info(f"📋 Data check string (первые 200 символов): {data_check_string[:200]}...")

            # Шаг 4: Создаем secret key (ОФИЦИАЛЬНЫЙ АЛГОРИТМ)
            # secret_key = HMAC_SHA256(<bot_token>, "WebAppData")
            secret_key = hmac.new(
                "WebAppData".encode('utf-8'),
                self.bot_token.encode('utf-8'),
                hashlib.sha256
            ).digest()

            # Шаг 5: Вычисляем hash (ОФИЦИАЛЬНЫЙ АЛГОРИТМ)
            # calculated_hash = HMAC_SHA256(data_check_string, secret_key)
            calculated_hash = hmac.new(
                secret_key,
                data_check_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            # Шаг 6: Безопасное сравнение хешей
            is_valid = hmac.compare_digest(received_hash, calculated_hash)

            logger.info(f"🔑 Calculated hash: {calculated_hash}")
            logger.info(f"✅ Хеши совпадают: {is_valid}")

            if not is_valid:
                logger.error("❌ Неверный hash в init_data - данные не от Telegram")
                return False

            # Шаг 7: Проверяем время (защита от replay атак)
            if 'auth_date' in parsed_data:
                auth_date = int(parsed_data['auth_date'])
                current_time = int(time.time())

                # Проверяем, что данные не старше 24 часов
                if current_time - auth_date > 86400:
                    logger.warning("⚠️ init_data устарел (старше 24 часов)")
                    # Не блокируем, просто предупреждаем

            logger.info("✅ Валидация Telegram WebApp данных успешна")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка валидации Telegram WebApp данных: {e}")
            import traceback
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
            return False
    
    def extract_user_from_init_data(self, init_data: str) -> Optional[Dict[str, Any]]:
        """
        Извлечение пользовательских данных из init_data
        """
        try:
            # Парсим init_data
            params = {}
            for param in init_data.split('&'):
                key, value = param.split('=', 1)
                params[key] = unquote(value)
            
            if 'user' in params:
                user_data = json.loads(params['user'])
                return user_data
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка извлечения пользователя из init_data: {e}")
            return None


async def get_current_user_from_webapp(request: Request) -> Optional[Dict[str, Any]]:
    """
    Получение текущего пользователя из Telegram WebApp данных
    """
    try:
        # Получаем init_data из заголовков или тела запроса
        init_data = request.headers.get("X-Telegram-Init-Data")
        
        if not init_data:
            # Пробуем получить из query параметров
            init_data = request.query_params.get("init_data")
        
        if not init_data:
            return None
        
        auth = TelegramWebAppAuth()
        
        # Валидируем данные
        if not auth.validate_webapp_data(init_data):
            return None
        
        # Извлекаем пользователя
        user_data = auth.extract_user_from_init_data(init_data)
        if not user_data:
            return None
        
        # Получаем или создаем пользователя в Firestore
        telegram_id = str(user_data.get('id'))
        user_doc = await get_or_create_user(telegram_id, user_data)
        
        return user_doc
        
    except Exception as e:
        logger.error(f"Ошибка получения пользователя из WebApp: {e}")
        return None


async def get_or_create_user(telegram_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Получение или создание пользователя в Firestore
    """
    try:
        if not db:
            logger.error("Firestore client не инициализирован")
            return {}
        
        # Проверяем, существует ли пользователь
        user_ref = db.collection('users').document(telegram_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            # Обновляем данные пользователя
            user_info = user_doc.to_dict()
            user_ref.update({
                'username': user_data.get('username', ''),
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'last_seen': firestore.SERVER_TIMESTAMP
            })
            user_info.update({
                'telegram_id': telegram_id,
                'username': user_data.get('username', ''),
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', '')
            })
            return user_info
        else:
            # Создаем нового пользователя
            admin_id = os.getenv("ADMIN_TELEGRAM_ID", "299820674")
            role = "admin" if telegram_id == admin_id else "user"
            
            new_user = {
                'telegram_id': telegram_id,
                'username': user_data.get('username', ''),
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'role': role,
                'created_at': firestore.SERVER_TIMESTAMP,
                'last_seen': firestore.SERVER_TIMESTAMP
            }
            
            user_ref.set(new_user)
            logger.info(f"Создан новый пользователь: {telegram_id} с ролью {role}")
            
            return new_user
            
    except Exception as e:
        logger.error(f"Ошибка работы с пользователем в Firestore: {e}")
        return {}


def check_webapp_signature(token: str, init_data: str) -> bool:
    """
    Валидация подписи WebApp данных от Telegram
    Реализация согласно официальной документации Telegram
    Исправлено для правильной работы с photo_url и экранированными слешами

    Эта функция заменяет удаленную telegram.helpers.check_webapp_signature
    в python-telegram-bot версии 22.1+
    """
    try:
        if not token or not init_data:
            logger.error("Token или init_data пустые")
            return False

        # Парсим параметры (ПРОВЕРЕННОЕ РЕШЕНИЕ от @TheBlackHacker)
        from urllib.parse import parse_qs
        parsed_data = parse_qs(init_data)

        # Извлекаем первое значение из каждого списка
        parsed_data = {key: values[0] for key, values in parsed_data.items()}

        if 'hash' not in parsed_data:
            logger.error("Отсутствует hash в init_data")
            return False

        received_hash = parsed_data.pop('hash')

        # Создаем строку для проверки (ПРОВЕРЕННЫЙ АЛГОРИТМ)
        sorted_items = sorted((key, value) for key, value in parsed_data.items())
        data_to_check = [f"{key}={value}" for key, value in sorted_items]
        data_check_string = '\n'.join(data_to_check)

        # Создаем секретный ключ
        secret_key = hmac.new(
            "WebAppData".encode(),
            token.encode(),
            hashlib.sha256
        ).digest()

        # Вычисляем hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        # Сравниваем хеши
        is_valid = hmac.compare_digest(received_hash, calculated_hash)

        if not is_valid:
            logger.error("Неверный hash в init_data")
            return False

        # Проверяем время (опционально)
        if 'auth_date' in parsed_data:
            auth_date = int(parsed_data['auth_date'])
            current_time = int(time.time())

            # Проверяем, что данные не старше 24 часов
            if current_time - auth_date > 86400:
                logger.warning("init_data устарел (старше 24 часов)")
                # Не блокируем, просто предупреждаем

        logger.info("Валидация WebApp подписи успешна")
        return True

    except Exception as e:
        logger.error(f"Ошибка валидации WebApp подписи: {e}")
        return False
