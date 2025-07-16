# backend/routers/auth.py
"""
Роутер аутентификации
JWT и Telegram WebApp аутентификация
"""

from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

from auth.dependencies import (
    get_current_user, create_access_token, TelegramWebAppAuth,
    get_or_create_user
)
from config.config import get_settings, logger

router = APIRouter()
settings = get_settings()


class TelegramAuthRequest(BaseModel):
    """Модель запроса Telegram аутентификации"""
    init_data: str


class AuthResponse(BaseModel):
    """Модель ответа аутентификации"""
    success: bool
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class UserProfileResponse(BaseModel):
    """Модель ответа профиля пользователя"""
    success: bool
    user: Dict[str, Any]


@router.post("/telegram", response_model=AuthResponse)
async def authenticate_telegram(request: TelegramAuthRequest):
    """
    Аутентификация через Telegram WebApp
    """
    try:
        logger.info("🔐 Попытка аутентификации через Telegram WebApp")
        
        # Валидация данных Telegram
        telegram_auth = TelegramWebAppAuth()
        user_data = telegram_auth.validate_telegram_data(
            request.init_data,
            settings.telegram_bot_token
        )
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверные данные Telegram WebApp"
            )
        
        # Получение или создание пользователя
        user = await get_or_create_user(user_data)
        
        # Создание JWT токена
        access_token = create_access_token(user['telegram_id'])
        
        logger.info(f"✅ Успешная аутентификация пользователя {user['telegram_id']}")
        
        return AuthResponse(
            success=True,
            access_token=access_token,
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка аутентификации Telegram: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка аутентификации"
        )


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Получение профиля текущего пользователя
    """
    try:
        # Добавляем дополнительную информацию о подписке
        subscription_info = _get_subscription_info(current_user)
        
        user_profile = {
            **current_user,
            "subscription_info": subscription_info
        }
        
        return UserProfileResponse(
            success=True,
            user=user_profile
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения профиля: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения профиля"
        )


@router.post("/refresh")
async def refresh_token(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Обновление JWT токена
    """
    try:
        # Создаем новый токен
        new_token = create_access_token(current_user['telegram_id'])
        
        return {
            "success": True,
            "access_token": new_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка обновления токена: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка обновления токена"
        )


@router.get("/verify")
async def verify_token(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Проверка валидности токена
    """
    return {
        "success": True,
        "valid": True,
        "user_id": current_user['id'],
        "telegram_id": current_user['telegram_id']
    }


def _get_subscription_info(user: Dict[str, Any]) -> Dict[str, Any]:
    """Получение информации о подписке пользователя"""
    from config.config import Constants
    
    subscription_plan = user.get('subscription_plan', 'free')
    plan_info = Constants.SUBSCRIPTION_PLANS.get(
        subscription_plan, 
        Constants.SUBSCRIPTION_PLANS['free']
    )
    
    # Проверяем активность подписки
    subscription_expires_at = user.get('subscription_expires_at')
    is_active = True
    
    if subscription_expires_at and subscription_plan != 'free':
        is_active = subscription_expires_at > datetime.now()
        if not is_active:
            # Подписка истекла, переводим на бесплатный план
            subscription_plan = 'free'
            plan_info = Constants.SUBSCRIPTION_PLANS['free']
    
    # Расчет оставшихся анализов
    analyses_today = user.get('analyses_today', 0)
    daily_limit = plan_info['analyses_per_day']
    
    if daily_limit == -1:
        remaining_analyses = "Безлимитно"
    else:
        remaining_analyses = max(0, daily_limit - analyses_today)
    
    return {
        "plan_name": plan_info['name'],
        "plan_code": subscription_plan,
        "price_stars": plan_info['price'],
        "daily_limit": daily_limit,
        "analyses_today": analyses_today,
        "remaining_analyses": remaining_analyses,
        "is_active": is_active,
        "expires_at": subscription_expires_at.isoformat() if subscription_expires_at else None
    }
