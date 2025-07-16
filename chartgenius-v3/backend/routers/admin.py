# backend/routers/admin.py
"""
Административный роутер для управления системой
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel

from auth.dependencies import require_admin
from config.config import logger
from config.database import execute_query, execute_one

router = APIRouter()


class UserStats(BaseModel):
    """Статистика пользователя"""
    total_users: int
    active_users: int
    premium_users: int
    new_users_today: int


class SystemStats(BaseModel):
    """Системная статистика"""
    total_analyses: int
    analyses_today: int
    avg_processing_time: float
    active_subscriptions: int


class UserInfo(BaseModel):
    """Информация о пользователе"""
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    subscription_plan: str
    analyses_today: int
    created_at: str
    is_active: bool


@router.get("/stats/users", response_model=UserStats)
async def get_user_stats(
    admin_user: Dict[str, Any] = Depends(require_admin)
):
    """Получение статистики пользователей"""
    try:
        # Общее количество пользователей
        total_users_result = await execute_one(
            "SELECT COUNT(*) FROM users WHERE is_active = 1"
        )
        total_users = total_users_result[0] if total_users_result else 0
        
        # Активные пользователи (заходили за последние 7 дней)
        active_users_result = await execute_one(
            """SELECT COUNT(*) FROM users 
               WHERE is_active = 1 AND updated_at > :week_ago""",
            {"week_ago": datetime.now() - timedelta(days=7)}
        )
        active_users = active_users_result[0] if active_users_result else 0
        
        # Премиум пользователи
        premium_users_result = await execute_one(
            """SELECT COUNT(*) FROM users 
               WHERE is_active = 1 AND subscription_plan != 'free'"""
        )
        premium_users = premium_users_result[0] if premium_users_result else 0
        
        # Новые пользователи сегодня
        new_users_result = await execute_one(
            """SELECT COUNT(*) FROM users 
               WHERE DATE(created_at) = DATE(CURRENT_TIMESTAMP)"""
        )
        new_users_today = new_users_result[0] if new_users_result else 0
        
        return UserStats(
            total_users=total_users,
            active_users=active_users,
            premium_users=premium_users,
            new_users_today=new_users_today
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения статистики пользователей: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения статистики"
        )


@router.get("/stats/system", response_model=SystemStats)
async def get_system_stats(
    admin_user: Dict[str, Any] = Depends(require_admin)
):
    """Получение системной статистики"""
    try:
        # Общее количество анализов
        total_analyses_result = await execute_one(
            "SELECT COUNT(*) FROM analyses"
        )
        total_analyses = total_analyses_result[0] if total_analyses_result else 0
        
        # Анализы сегодня
        analyses_today_result = await execute_one(
            """SELECT COUNT(*) FROM analyses 
               WHERE DATE(created_at) = DATE(CURRENT_TIMESTAMP)"""
        )
        analyses_today = analyses_today_result[0] if analyses_today_result else 0
        
        # Среднее время обработки
        avg_time_result = await execute_one(
            """SELECT AVG(processing_time_ms) FROM analyses 
               WHERE processing_time_ms IS NOT NULL"""
        )
        avg_processing_time = float(avg_time_result[0]) if avg_time_result and avg_time_result[0] else 0.0
        
        # Активные подписки
        active_subs_result = await execute_one(
            """SELECT COUNT(*) FROM subscriptions 
               WHERE status = 'active' AND expires_at > CURRENT_TIMESTAMP"""
        )
        active_subscriptions = active_subs_result[0] if active_subs_result else 0
        
        return SystemStats(
            total_analyses=total_analyses,
            analyses_today=analyses_today,
            avg_processing_time=avg_processing_time,
            active_subscriptions=active_subscriptions
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения системной статистики: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения статистики"
        )


@router.get("/users", response_model=List[UserInfo])
async def get_users(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    admin_user: Dict[str, Any] = Depends(require_admin)
):
    """Получение списка пользователей"""
    try:
        # Базовый запрос
        base_query = """
            SELECT id, telegram_id, username, first_name, 
                   subscription_plan, analyses_today, created_at, is_active
            FROM users
        """
        
        # Условия поиска
        where_conditions = []
        params = {"limit": limit, "offset": offset}
        
        if search:
            where_conditions.append(
                "(LOWER(username) LIKE LOWER(:search) OR LOWER(first_name) LIKE LOWER(:search))"
            )
            params["search"] = f"%{search}%"
        
        # Формируем финальный запрос
        if where_conditions:
            query = f"{base_query} WHERE {' AND '.join(where_conditions)}"
        else:
            query = base_query
        
        query += " ORDER BY created_at DESC OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY"
        
        results = await execute_query(query, params)
        
        users = []
        for row in results:
            users.append(UserInfo(
                id=row[0],
                telegram_id=row[1],
                username=row[2],
                first_name=row[3],
                subscription_plan=row[4],
                analyses_today=row[5],
                created_at=row[6].isoformat() if row[6] else "",
                is_active=bool(row[7])
            ))
        
        return users
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения списка пользователей: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения пользователей"
        )


@router.post("/users/{user_id}/subscription")
async def update_user_subscription(
    user_id: int,
    plan_code: str,
    days: int = 30,
    admin_user: Dict[str, Any] = Depends(require_admin)
):
    """Обновление подписки пользователя"""
    try:
        from config.config import Constants
        
        # Проверяем план
        if plan_code not in Constants.SUBSCRIPTION_PLANS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный план подписки"
            )
        
        # Обновляем подписку пользователя
        expires_at = datetime.now() + timedelta(days=days) if plan_code != 'free' else None
        
        await execute_query(
            """UPDATE users 
               SET subscription_plan = :plan_code,
                   subscription_expires_at = :expires_at,
                   analyses_today = 0
               WHERE id = :user_id""",
            {
                "user_id": user_id,
                "plan_code": plan_code,
                "expires_at": expires_at
            }
        )
        
        # Логируем действие администратора
        await _log_admin_action(
            admin_user['id'],
            "update_subscription",
            user_id,
            f"Обновлена подписка на {plan_code} на {days} дней"
        )
        
        logger.info(f"✅ Администратор {admin_user['telegram_id']} обновил подписку пользователя {user_id}")
        
        return {
            "success": True,
            "message": f"Подписка обновлена на {plan_code}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка обновления подписки: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка обновления подписки"
        )


@router.post("/users/{user_id}/block")
async def block_user(
    user_id: int,
    reason: str = "Нарушение правил",
    admin_user: Dict[str, Any] = Depends(require_admin)
):
    """Блокировка пользователя"""
    try:
        # Блокируем пользователя
        await execute_query(
            "UPDATE users SET is_active = 0 WHERE id = :user_id",
            {"user_id": user_id}
        )
        
        # Логируем действие
        await _log_admin_action(
            admin_user['id'],
            "block_user",
            user_id,
            f"Пользователь заблокирован. Причина: {reason}"
        )
        
        logger.info(f"🚫 Администратор {admin_user['telegram_id']} заблокировал пользователя {user_id}")
        
        return {
            "success": True,
            "message": "Пользователь заблокирован"
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка блокировки пользователя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка блокировки пользователя"
        )


@router.post("/users/{user_id}/unblock")
async def unblock_user(
    user_id: int,
    admin_user: Dict[str, Any] = Depends(require_admin)
):
    """Разблокировка пользователя"""
    try:
        # Разблокируем пользователя
        await execute_query(
            "UPDATE users SET is_active = 1 WHERE id = :user_id",
            {"user_id": user_id}
        )
        
        # Логируем действие
        await _log_admin_action(
            admin_user['id'],
            "unblock_user",
            user_id,
            "Пользователь разблокирован"
        )
        
        logger.info(f"✅ Администратор {admin_user['telegram_id']} разблокировал пользователя {user_id}")
        
        return {
            "success": True,
            "message": "Пользователь разблокирован"
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка разблокировки пользователя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка разблокировки пользователя"
        )


@router.get("/logs")
async def get_admin_logs(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    admin_user: Dict[str, Any] = Depends(require_admin)
):
    """Получение логов действий администраторов"""
    try:
        query = """
            SELECT al.id, al.action, al.target_user_id, al.details,
                   al.created_at, u.username as admin_username
            FROM admin_logs al
            LEFT JOIN users u ON al.admin_user_id = u.id
            ORDER BY al.created_at DESC
            OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
        """
        
        results = await execute_query(query, {
            "limit": limit,
            "offset": offset
        })
        
        logs = []
        for row in results:
            logs.append({
                "id": row[0],
                "action": row[1],
                "target_user_id": row[2],
                "details": row[3],
                "created_at": row[4].isoformat() if row[4] else None,
                "admin_username": row[5]
            })
        
        return {
            "success": True,
            "logs": logs
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения логов: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения логов"
        )


async def _log_admin_action(
    admin_user_id: int,
    action: str,
    target_user_id: Optional[int],
    details: str
):
    """Логирование действий администратора"""
    try:
        await execute_query(
            """INSERT INTO admin_logs (admin_user_id, action, target_user_id, details)
               VALUES (:admin_user_id, :action, :target_user_id, :details)""",
            {
                "admin_user_id": admin_user_id,
                "action": action,
                "target_user_id": target_user_id,
                "details": details
            }
        )
    except Exception as e:
        logger.error(f"❌ Ошибка логирования действия администратора: {e}")
