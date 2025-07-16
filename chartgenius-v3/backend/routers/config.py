# backend/routers/config.py
"""
Роутер конфигурации для получения настроек приложения
"""

from typing import Dict, Any, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from auth.dependencies import get_current_user
from config.config import get_settings, Constants

router = APIRouter()
settings = get_settings()


class AppConfig(BaseModel):
    """Конфигурация приложения"""
    supported_symbols: List[str]
    supported_intervals: List[str]
    default_symbol: str
    default_interval: str
    default_days: int
    subscription_plans: Dict[str, Any]


class UserLimits(BaseModel):
    """Лимиты пользователя"""
    analyses_today: int
    daily_limit: int
    remaining_analyses: int
    subscription_plan: str


@router.get("/app", response_model=AppConfig)
async def get_app_config():
    """Получение конфигурации приложения"""
    return AppConfig(
        supported_symbols=list(Constants.SUPPORTED_SYMBOLS),
        supported_intervals=list(Constants.SUPPORTED_INTERVALS),
        default_symbol=settings.default_symbol,
        default_interval=settings.default_interval,
        default_days=settings.default_days,
        subscription_plans=Constants.SUBSCRIPTION_PLANS
    )


@router.get("/user-limits", response_model=UserLimits)
async def get_user_limits(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Получение лимитов текущего пользователя"""
    subscription_plan = current_user.get('subscription_plan', 'free')
    plan_info = Constants.SUBSCRIPTION_PLANS.get(subscription_plan, Constants.SUBSCRIPTION_PLANS['free'])
    
    analyses_today = current_user.get('analyses_today', 0)
    daily_limit = plan_info['analyses_per_day']
    
    if daily_limit == -1:
        remaining_analyses = -1  # Безлимитно
    else:
        remaining_analyses = max(0, daily_limit - analyses_today)
    
    return UserLimits(
        analyses_today=analyses_today,
        daily_limit=daily_limit,
        remaining_analyses=remaining_analyses,
        subscription_plan=subscription_plan
    )
