# backend/middleware/telegram_webapp.py

import os
import hashlib
import hmac
import json
from urllib.parse import unquote
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request
from telegram_webapp_auth.auth import TelegramAuthenticator
from backend.config.config import logger, db
from google.cloud import firestore


class TelegramWebAppAuth:
    """Middleware для аутентификации Telegram WebApp"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.bot_token:
            logger.error("TELEGRAM_BOT_TOKEN не установлен")
    
    def validate_webapp_data(self, init_data: str) -> bool:
        """
        Валидация данных от Telegram WebApp
        """
        try:
            if not self.bot_token:
                return False

            # Используем библиотеку telegram-webapp-auth для валидации
            authenticator = TelegramAuthenticator(self.bot_token)
            authenticator.validate(init_data)
            return True

        except Exception as e:
            logger.error(f"Ошибка валидации Telegram WebApp данных: {e}")
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
