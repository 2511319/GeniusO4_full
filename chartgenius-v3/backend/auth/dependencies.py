# backend/auth/dependencies.py
"""
Зависимости аутентификации для FastAPI
JWT и Telegram WebApp аутентификация
"""

import json
import hashlib
import hmac
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import unquote

from fastapi import HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from config.config import get_settings, logger, Constants
from config.database import execute_one, execute_query

settings = get_settings()
security = HTTPBearer()


class TelegramWebAppAuth:
    """Аутентификация Telegram WebApp"""
    
    @staticmethod
    def validate_telegram_data(init_data: str, bot_token: str) -> Optional[Dict[str, Any]]:
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
                bot_token.encode(),
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
                logger.warning("⚠️ Неверный hash Telegram WebApp")
                return None
            
            # Проверка времени (данные должны быть не старше 24 часов)
            auth_date = int(parsed_data.get('auth_date', 0))
            current_time = int(datetime.now().timestamp())
            
            if current_time - auth_date > 86400:  # 24 часа
                logger.warning("⚠️ Устаревшие данные Telegram WebApp")
                return None
            
            # Парсинг данных пользователя
            user_data = json.loads(parsed_data.get('user', '{}'))
            
            return {
                'telegram_id': user_data.get('id'),
                'username': user_data.get('username'),
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'language_code': user_data.get('language_code', 'ru'),
                'auth_date': auth_date
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка валидации Telegram WebApp: {e}")
            return None


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Получение текущего пользователя из JWT токена или Telegram WebApp"""
    
    # Проверяем JWT токен
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        telegram_id = payload.get("telegram_id")
        if not telegram_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен"
            )
        
        # Получаем пользователя из БД
        user = await get_user_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден"
            )
        
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен истек"
        )
    except jwt.JWTError:
        # Если JWT не валиден, пробуем Telegram WebApp
        pass
    
    # Проверяем Telegram WebApp данные
    init_data = request.headers.get("X-Telegram-Init-Data")
    if init_data:
        telegram_auth = TelegramWebAppAuth()
        user_data = telegram_auth.validate_telegram_data(
            init_data,
            settings.telegram_bot_token
        )
        
        if user_data:
            # Получаем или создаем пользователя
            user = await get_or_create_user(user_data)
            return user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Требуется аутентификация"
    )


async def get_user_by_telegram_id(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Получение пользователя по Telegram ID"""
    try:
        query = """
            SELECT id, telegram_id, username, first_name, last_name,
                   language_code, subscription_plan, subscription_expires_at,
                   role, is_active, analyses_today, last_analysis_date,
                   created_at, updated_at
            FROM users
            WHERE telegram_id = :telegram_id AND is_active = 1
        """
        
        result = await execute_one(query, {"telegram_id": telegram_id})
        
        if result:
            return {
                "id": result[0],
                "telegram_id": result[1],
                "username": result[2],
                "first_name": result[3],
                "last_name": result[4],
                "language_code": result[5],
                "subscription_plan": result[6],
                "subscription_expires_at": result[7],
                "role": result[8],
                "is_active": bool(result[9]),
                "analyses_today": result[10],
                "last_analysis_date": result[11],
                "created_at": result[12],
                "updated_at": result[13]
            }
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения пользователя {telegram_id}: {e}")
        return None


async def get_or_create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Получение или создание пользователя"""
    try:
        # Сначала пытаемся найти существующего пользователя
        user = await get_user_by_telegram_id(user_data['telegram_id'])
        
        if user:
            # Обновляем данные пользователя
            await update_user_data(user['id'], user_data)
            return user
        
        # Создаем нового пользователя
        query = """
            INSERT INTO users (
                telegram_id, username, first_name, last_name, language_code
            ) VALUES (
                :telegram_id, :username, :first_name, :last_name, :language_code
            ) RETURNING id
        """
        
        result = await execute_one(query, {
            "telegram_id": user_data['telegram_id'],
            "username": user_data.get('username'),
            "first_name": user_data.get('first_name'),
            "last_name": user_data.get('last_name'),
            "language_code": user_data.get('language_code', 'ru')
        })
        
        if result:
            user_id = result[0]
            logger.info(f"✅ Создан новый пользователь: {user_data['telegram_id']}")
            
            # Возвращаем созданного пользователя
            return await get_user_by_telegram_id(user_data['telegram_id'])
        
        raise Exception("Не удалось создать пользователя")
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания пользователя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка создания пользователя"
        )


async def update_user_data(user_id: int, user_data: Dict[str, Any]):
    """Обновление данных пользователя"""
    try:
        query = """
            UPDATE users 
            SET username = :username,
                first_name = :first_name,
                last_name = :last_name,
                language_code = :language_code,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :user_id
        """
        
        await execute_query(query, {
            "user_id": user_id,
            "username": user_data.get('username'),
            "first_name": user_data.get('first_name'),
            "last_name": user_data.get('last_name'),
            "language_code": user_data.get('language_code', 'ru')
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка обновления пользователя {user_id}: {e}")


async def check_analysis_limit(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> None:
    """Проверка лимита анализов пользователя"""
    try:
        # Сброс счетчика если новый день
        today = datetime.now().date()
        last_analysis_date = current_user.get('last_analysis_date')
        
        if last_analysis_date and last_analysis_date.date() != today:
            # Сбрасываем счетчик
            await execute_query(
                "UPDATE users SET analyses_today = 0 WHERE id = :user_id",
                {"user_id": current_user['id']}
            )
            current_user['analyses_today'] = 0
        
        # Получаем лимит для плана подписки
        subscription_plan = current_user.get('subscription_plan', 'free')
        plan_info = Constants.SUBSCRIPTION_PLANS.get(subscription_plan, Constants.SUBSCRIPTION_PLANS['free'])
        daily_limit = plan_info['analyses_per_day']
        
        # Проверяем лимит (-1 означает безлимитный)
        if daily_limit != -1 and current_user['analyses_today'] >= daily_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Превышен дневной лимит анализов ({daily_limit}). Обновите подписку."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка проверки лимита анализов: {e}")
        # Не блокируем пользователя при ошибке проверки


def create_access_token(telegram_id: int) -> str:
    """Создание JWT токена"""
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    
    payload = {
        "telegram_id": telegram_id,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )


async def require_admin(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Проверка прав администратора"""
    if current_user.get('role') not in ['admin', 'moderator']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    return current_user
