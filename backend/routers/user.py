# backend/routers/user.py

from fastapi import APIRouter, HTTPException, Header, Depends
from sqlmodel import Session
from backend.models.user import User
from backend.db.session import get_session
from backend.services.subscription_manager import (
    check_subscription, create_subscription, renew_subscription,
    get_subscription_details, can_perform_analysis, increment_analysis_count
)
from backend.services.analysis_storage import get_user_analyses, get_analysis, delete_analysis
from backend.core.security import create_access_token
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/user", tags=["user"])

@router.get("/subscription")
async def get_user_subscription(x_telegram_id: str = Header(None)):
    """
    Получает информацию о подписке пользователя
    """
    if not x_telegram_id:
        raise HTTPException(400, "X-Telegram-Id header required")

    try:
        subscription_details = get_subscription_details(x_telegram_id)

        if not subscription_details:
            raise HTTPException(500, "Failed to get subscription details")

        # Форматируем дату для фронтенда
        expires_at = None
        if subscription_details['expires_at']:
            expires_at = subscription_details['expires_at'].strftime("%Y-%m-%d")

        return {
            "level": subscription_details['level'],
            "expires_at": expires_at,
            "is_active": subscription_details['is_active'],
            "features": subscription_details['features'],
            "analysis_count": subscription_details['analysis_count'],
            "analysis_limit": subscription_details['analysis_limit']
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения подписки для {x_telegram_id}: {e}")
        raise HTTPException(500, "Failed to get subscription info")

@router.get("/profile")
async def get_user_profile(x_telegram_id: str = Header(None), db: Session = Depends(get_session)):
    """
    Получает профиль пользователя
    """
    if not x_telegram_id:
        raise HTTPException(400, "X-Telegram-Id header required")
    
    try:
        user = db.get(User, int(x_telegram_id))
        if not user:
            raise HTTPException(404, "User not found")
            
        subscription_level = check_subscription(x_telegram_id)
        
        return {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "photo_url": user.photo_url,
            "subscription": {
                "level": subscription_level,
                "is_active": subscription_level not in ['none', 'expired']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения профиля для {x_telegram_id}: {e}")
        raise HTTPException(500, "Failed to get user profile")

@router.post("/subscription/create")
async def create_user_subscription(
    x_telegram_id: str = Header(None),
    level: str = "premium",
    duration_days: int = 30
):
    """
    Создает подписку для пользователя
    """
    if not x_telegram_id:
        raise HTTPException(400, "X-Telegram-Id header required")
    
    try:
        create_subscription(x_telegram_id, level, duration_days)
        return {
            "message": "Subscription created successfully",
            "level": level,
            "duration_days": duration_days
        }
        
    except Exception as e:
        logger.error(f"Ошибка создания подписки для {x_telegram_id}: {e}")
        raise HTTPException(500, "Failed to create subscription")

@router.post("/subscription/renew")
async def renew_user_subscription(
    x_telegram_id: str = Header(None),
    level: str = "premium",
    duration_days: int = 30
):
    """
    Обновляет подписку пользователя
    """
    if not x_telegram_id:
        raise HTTPException(400, "X-Telegram-Id header required")
    
    try:
        renew_subscription(x_telegram_id, level, duration_days)
        return {
            "message": "Subscription renewed successfully",
            "level": level,
            "duration_days": duration_days
        }
        
    except Exception as e:
        logger.error(f"Ошибка обновления подписки для {x_telegram_id}: {e}")
        raise HTTPException(500, "Failed to renew subscription")

@router.get("/analyses")
async def get_user_analyses_list(x_telegram_id: str = Header(None), limit: int = 10):
    """
    Получает список анализов пользователя
    """
    if not x_telegram_id:
        raise HTTPException(400, "X-Telegram-Id header required")

    try:
        analyses = get_user_analyses(x_telegram_id, limit)

        # Форматируем данные для фронтенда
        formatted_analyses = []
        for analysis in analyses:
            formatted_analyses.append({
                "id": analysis.get('id'),
                "symbol": analysis.get('symbol'),
                "created_at": analysis.get('created_at').isoformat() if analysis.get('created_at') else None,
                "type": analysis.get('analysis_type'),
                "summary": analysis.get('primary_analysis', {}).get('summary', 'Анализ выполнен')
            })

        return {
            "analyses": formatted_analyses,
            "total": len(formatted_analyses)
        }

    except Exception as e:
        logger.error(f"Ошибка получения анализов для {x_telegram_id}: {e}")
        raise HTTPException(500, "Failed to get user analyses")

@router.get("/analyses/{analysis_id}")
async def get_analysis_details(analysis_id: str, x_telegram_id: str = Header(None)):
    """
    Получает детали конкретного анализа
    """
    if not x_telegram_id:
        raise HTTPException(400, "X-Telegram-Id header required")

    try:
        analysis = get_analysis(analysis_id)

        if not analysis:
            raise HTTPException(404, "Analysis not found")

        # Проверяем, что анализ принадлежит пользователю
        if analysis.get('telegram_id') != str(x_telegram_id):
            raise HTTPException(403, "Access denied")

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения анализа {analysis_id}: {e}")
        raise HTTPException(500, "Failed to get analysis details")

@router.delete("/analyses/{analysis_id}")
async def delete_user_analysis(analysis_id: str, x_telegram_id: str = Header(None)):
    """
    Удаляет анализ пользователя
    """
    if not x_telegram_id:
        raise HTTPException(400, "X-Telegram-Id header required")

    try:
        success = delete_analysis(analysis_id, x_telegram_id)

        if success:
            return {"message": "Analysis deleted successfully"}
        else:
            raise HTTPException(404, "Analysis not found or access denied")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка удаления анализа {analysis_id}: {e}")
        raise HTTPException(500, "Failed to delete analysis")

@router.post("/analysis/check")
async def check_analysis_availability(
    x_telegram_id: str = Header(None),
    analysis_type: str = "simple"
):
    """
    Проверяет, может ли пользователь выполнить анализ
    """
    if not x_telegram_id:
        raise HTTPException(400, "X-Telegram-Id header required")

    try:
        can_perform, message = can_perform_analysis(x_telegram_id, analysis_type)

        return {
            "can_perform": can_perform,
            "message": message,
            "analysis_type": analysis_type
        }

    except Exception as e:
        logger.error(f"Ошибка проверки доступности анализа для {x_telegram_id}: {e}")
        raise HTTPException(500, "Failed to check analysis availability")

@router.post("/analysis/increment")
async def increment_user_analysis_count(x_telegram_id: str = Header(None)):
    """
    Увеличивает счетчик использованных анализов
    """
    if not x_telegram_id:
        raise HTTPException(400, "X-Telegram-Id header required")

    try:
        success = increment_analysis_count(x_telegram_id)

        if success:
            return {"message": "Analysis count incremented successfully"}
        else:
            raise HTTPException(500, "Failed to increment analysis count")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка увеличения счетчика анализов для {x_telegram_id}: {e}")
        raise HTTPException(500, "Failed to increment analysis count")
