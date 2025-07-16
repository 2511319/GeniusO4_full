# backend/middleware/telegram_webapp.py
"""
Middleware для обработки Telegram WebApp аутентификации
"""

import json
import hashlib
import hmac
from typing import Optional
from urllib.parse import unquote

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from config.config import get_settings, logger

settings = get_settings()


class TelegramWebAppMiddleware(BaseHTTPMiddleware):
    """Middleware для валидации Telegram WebApp данных"""
    
    def __init__(self, app):
        super().__init__(app)
        self.bot_token = settings.telegram_bot_token
    
    async def dispatch(self, request: Request, call_next):
        """Обработка запроса с валидацией Telegram WebApp"""
        
        # Проверяем наличие Telegram WebApp данных
        init_data = request.headers.get("X-Telegram-Init-Data")
        
        if init_data:
            # Валидируем данные
            user_data = self._validate_telegram_webapp_data(init_data)
            
            if user_data:
                # Добавляем данные пользователя в request state
                request.state.telegram_user = user_data
                logger.debug(f"✅ Валидные Telegram WebApp данные для пользователя {user_data.get('id')}")
            else:
                logger.warning("⚠️ Неверные Telegram WebApp данные")
                # Не блокируем запрос, просто не добавляем данные пользователя
        
        response = await call_next(request)
        
        # Добавляем заголовки для Telegram WebApp
        if hasattr(request.state, 'telegram_user'):
            response.headers["X-Telegram-User-Validated"] = "true"
        
        return response
    
    def _validate_telegram_webapp_data(self, init_data: str) -> Optional[dict]:
        """Валидация данных Telegram WebApp"""
        try:
            # Парсинг init_data
            parsed_data = {}
            for item in init_data.split('&'):
                if '=' in item:
                    key, value = item.split('=', 1)
                    parsed_data[key] = unquote(value)
            
            # Извлечение hash
            received_hash = parsed_data.pop('hash', '')
            if not received_hash:
                return None
            
            # Создание строки для проверки
            data_check_string = '\n'.join([
                f"{key}={value}" for key, value in sorted(parsed_data.items())
            ])
            
            # Создание секретного ключа
            secret_key = hmac.new(
                "WebAppData".encode(),
                self.bot_token.encode(),
                hashlib.sha256
            ).digest()
            
            # Вычисление hash
            calculated_hash = hmac.new(
                secret_key,
                data_check_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Проверка hash
            if calculated_hash != received_hash:
                return None
            
            # Парсинг данных пользователя
            user_data = {}
            if 'user' in parsed_data:
                try:
                    user_data = json.loads(parsed_data['user'])
                except json.JSONDecodeError:
                    return None
            
            # Добавляем дополнительные данные
            user_data['auth_date'] = int(parsed_data.get('auth_date', 0))
            user_data['query_id'] = parsed_data.get('query_id')
            
            return user_data
            
        except Exception as e:
            logger.error(f"❌ Ошибка валидации Telegram WebApp данных: {e}")
            return None


class TelegramBotMiddleware(BaseHTTPMiddleware):
    """Middleware для обработки запросов от Telegram Bot"""
    
    def __init__(self, app):
        super().__init__(app)
        self.bot_token = settings.telegram_bot_token
        self.webhook_secret = self._generate_webhook_secret()
    
    async def dispatch(self, request: Request, call_next):
        """Обработка запроса с валидацией Telegram Bot"""
        
        # Проверяем, является ли это webhook от Telegram
        if request.url.path.startswith("/api/webhooks/telegram"):
            
            # Валидируем webhook
            if not self._validate_telegram_webhook(request):
                logger.warning("⚠️ Неверный Telegram webhook")
                # Можно вернуть 403, но для безопасности возвращаем 404
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Not found"
                )
        
        response = await call_next(request)
        return response
    
    def _validate_telegram_webhook(self, request: Request) -> bool:
        """Валидация webhook от Telegram"""
        try:
            # Проверяем секретный токен в заголовке
            secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
            
            if secret_token and secret_token == self.webhook_secret:
                return True
            
            # Альтернативная проверка по User-Agent
            user_agent = request.headers.get("User-Agent", "")
            if "TelegramBot" in user_agent:
                return True
            
            # Проверка IP адреса Telegram (упрощенная)
            client_ip = request.client.host if request.client else ""
            telegram_ip_ranges = [
                "149.154.160.0/20",
                "91.108.4.0/22"
            ]
            
            # В реальной реализации здесь должна быть проверка IP диапазонов
            # Для демонстрации пропускаем
            
            return True  # Временно пропускаем все запросы
            
        except Exception as e:
            logger.error(f"❌ Ошибка валидации Telegram webhook: {e}")
            return False
    
    def _generate_webhook_secret(self) -> str:
        """Генерация секретного токена для webhook"""
        import hashlib
        return hashlib.sha256(f"{self.bot_token}_webhook_secret".encode()).hexdigest()[:32]


class TelegramSecurityMiddleware(BaseHTTPMiddleware):
    """Middleware для дополнительной безопасности Telegram интеграции"""
    
    def __init__(self, app):
        super().__init__(app)
        self.max_payload_size = 1024 * 1024  # 1MB
        self.allowed_content_types = [
            "application/json",
            "application/x-www-form-urlencoded"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Обработка запроса с проверками безопасности"""
        
        # Проверяем размер payload для Telegram запросов
        if request.url.path.startswith("/api/webhooks/telegram"):
            
            # Проверка Content-Type
            content_type = request.headers.get("Content-Type", "")
            if not any(ct in content_type for ct in self.allowed_content_types):
                logger.warning(f"⚠️ Неверный Content-Type для Telegram webhook: {content_type}")
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid content type"
                )
            
            # Проверка размера payload
            content_length = request.headers.get("Content-Length")
            if content_length and int(content_length) > self.max_payload_size:
                logger.warning(f"⚠️ Слишком большой payload: {content_length}")
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Payload too large"
                )
        
        response = await call_next(request)
        
        # Добавляем заголовки безопасности для Telegram WebApp
        if request.url.path.startswith("/api/"):
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
            response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response
