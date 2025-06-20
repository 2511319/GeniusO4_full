# backend/auth/dependencies.py

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.config.config import logger, db
from backend.middleware.telegram_webapp import get_current_user_from_webapp


security = HTTPBearer()


class RoleChecker:
    """Класс для проверки ролей пользователей"""
    
    ROLE_HIERARCHY = {
        'user': 0,
        'premium': 1,
        'vip': 2,
        'moderator': 3,
        'admin': 4
    }
    
    def __init__(self, required_roles: List[str]):
        self.required_roles = required_roles
    
    def __call__(self, user: Dict[str, Any] = Depends(get_current_user)):
        user_role = user.get('role', 'user')
        user_level = self.ROLE_HIERARCHY.get(user_role, 0)
        
        # Проверяем, есть ли у пользователя достаточный уровень доступа
        required_level = min([self.ROLE_HIERARCHY.get(role, 0) for role in self.required_roles])
        
        if user_level < required_level:
            raise HTTPException(
                status_code=403,
                detail=f"Недостаточно прав. Требуется роль: {', '.join(self.required_roles)}"
            )
        
        return user


def require_role(role: str):
    """Декоратор для проверки роли пользователя"""
    return RoleChecker([role])


def require_any_role(*roles: str):
    """Декоратор для проверки любой из указанных ролей"""
    return RoleChecker(list(roles))


async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Получение текущего пользователя из JWT токена или Telegram WebApp
    """
    try:
        # Сначала пробуем получить пользователя из Telegram WebApp
        webapp_user = await get_current_user_from_webapp(request)
        if webapp_user:
            return webapp_user
        
        # Если не получилось, пробуем JWT токен
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Токен авторизации не найден")
        
        token = auth_header.split(" ")[1]
        return await get_user_from_jwt(token)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения текущего пользователя: {e}")
        raise HTTPException(status_code=401, detail="Ошибка авторизации")


async def get_user_from_jwt(token: str) -> Dict[str, Any]:
    """Получение пользователя из JWT токена"""
    try:
        secret_key = os.getenv("JWT_SECRET_KEY")
        if not secret_key:
            raise HTTPException(status_code=500, detail="JWT_SECRET_KEY не настроен")
        
        # Декодируем токен
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        telegram_id = payload.get("telegram_id")
        
        if not telegram_id:
            raise HTTPException(status_code=401, detail="Неверный токен")
        
        # Получаем пользователя из Firestore
        if not db:
            raise HTTPException(status_code=500, detail="База данных недоступна")
        
        user_ref = db.collection('users').document(str(telegram_id))
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=401, detail="Пользователь не найден")
        
        user_data = user_doc.to_dict()
        user_data['telegram_id'] = telegram_id
        
        return user_data
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истек")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Неверный токен")
    except Exception as e:
        logger.error(f"Ошибка получения пользователя из JWT: {e}")
        raise HTTPException(status_code=401, detail="Ошибка авторизации")


async def get_uid(user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """Получение Telegram ID текущего пользователя"""
    return str(user.get('telegram_id'))


def create_jwt_token(telegram_id: str, expires_minutes: int = 10) -> str:
    """Создание JWT токена для пользователя"""
    try:
        secret_key = os.getenv("JWT_SECRET_KEY")
        if not secret_key:
            raise ValueError("JWT_SECRET_KEY не настроен")
        
        expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
        payload = {
            "telegram_id": telegram_id,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        return token
        
    except Exception as e:
        logger.error(f"Ошибка создания JWT токена: {e}")
        raise


async def check_subscription(user: Dict[str, Any]) -> Dict[str, Any]:
    """Проверка подписки пользователя"""
    try:
        if not db:
            return {'level': 'none', 'expires_at': None}
        
        telegram_id = str(user.get('telegram_id'))
        sub_ref = db.collection('subscriptions').document(telegram_id)
        sub_doc = sub_ref.get()
        
        if not sub_doc.exists:
            return {'level': 'none', 'expires_at': None}
        
        sub_data = sub_doc.to_dict()
        expires_at = sub_data.get('expires_at')
        
        # Проверяем, не истекла ли подписка
        if expires_at and expires_at < datetime.utcnow():
            return {'level': 'expired', 'expires_at': expires_at}
        
        return sub_data
        
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return {'level': 'none', 'expires_at': None}


async def is_banned(telegram_id: str) -> bool:
    """Проверка, забанен ли пользователь"""
    try:
        if not db:
            return False
        
        ban_ref = db.collection('bans').document(str(telegram_id))
        ban_doc = ban_ref.get()
        
        if not ban_doc.exists:
            return False
        
        ban_data = ban_doc.to_dict()
        expires_at = ban_data.get('expires_at')
        
        # Если бан истек, удаляем запись
        if expires_at and expires_at < datetime.utcnow():
            ban_ref.delete()
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка проверки бана: {e}")
        return False
