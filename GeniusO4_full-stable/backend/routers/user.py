# backend/routers/user.py

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.config.config import logger
from backend.auth.dependencies import get_uid
from backend.services.oracle_client import oracle_client


router = APIRouter(
    prefix='/user',
    tags=['user']
)


class UserProfile(BaseModel):
    telegram_id: str
    role: str
    created_at: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserStats(BaseModel):
    analyses_today: int
    total_analyses: int
    watchlist_count: int
    days_with_us: int


class UserSubscription(BaseModel):
    level: str
    expires_at: Optional[str] = None
    is_active: bool


@router.get('/profile')
async def get_user_profile(uid: str = Depends(get_uid)):
    """Получение профиля пользователя"""
    try:
        # Получаем данные пользователя из Oracle AJD
        user_data = oracle_client.get_document('users', uid)
        
        if not user_data:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        return UserProfile(
            telegram_id=user_data.get('telegram_id', uid),
            role=user_data.get('role', 'user'),
            created_at=user_data.get('created_at', datetime.now().isoformat()),
            username=user_data.get('username'),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name')
        )
        
    except Exception as e:
        logger.error(f"Ошибка получения профиля пользователя {uid}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@router.get('/stats')
async def get_user_stats(uid: str = Depends(get_uid)):
    """Получение статистики пользователя"""
    try:
        # Получаем данные пользователя
        user_data = oracle_client.get_document('users', uid)
        if not user_data:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Подсчитываем анализы
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        
        # Получаем все анализы пользователя
        analyses = oracle_client.query_documents(
            'analyses',
            filter_conditions={'telegram_id': uid},
            limit=10000
        )
        
        # Подсчитываем анализы за сегодня
        analyses_today = 0
        for analysis in analyses:
            analysis_date = analysis.get('created_at')
            if analysis_date:
                try:
                    if isinstance(analysis_date, str):
                        analysis_datetime = datetime.fromisoformat(analysis_date.replace('Z', '+00:00'))
                    else:
                        analysis_datetime = analysis_date
                    
                    if analysis_datetime.date() == today:
                        analyses_today += 1
                except:
                    continue
        
        # Получаем watchlist
        watchlist = oracle_client.query_documents(
            'watchlist',
            filter_conditions={'telegram_id': uid},
            limit=1000
        )
        
        # Вычисляем дни с нами
        created_at = user_data.get('created_at')
        days_with_us = 0
        if created_at:
            try:
                if isinstance(created_at, str):
                    created_datetime = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                else:
                    created_datetime = created_at
                days_with_us = (datetime.now() - created_datetime).days
            except:
                days_with_us = 0
        
        return UserStats(
            analyses_today=analyses_today,
            total_analyses=len(analyses),
            watchlist_count=len(watchlist),
            days_with_us=max(0, days_with_us)
        )
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики пользователя {uid}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@router.get('/subscription')
async def get_user_subscription(uid: str = Depends(get_uid)):
    """Получение информации о подписке пользователя"""
    try:
        # Получаем данные пользователя
        user_data = oracle_client.get_document('users', uid)
        if not user_data:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        role = user_data.get('role', 'user')
        
        # Проверяем активную подписку
        subscription_data = oracle_client.query_documents(
            'subscriptions',
            filter_conditions={'telegram_id': uid},
            limit=1
        )
        
        if subscription_data:
            sub = subscription_data[0]
            expires_at = sub.get('expires_at')
            
            # Проверяем, не истекла ли подписка
            is_active = True
            if expires_at:
                try:
                    if isinstance(expires_at, str):
                        expires_datetime = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    else:
                        expires_datetime = expires_at
                    
                    is_active = expires_datetime > datetime.now()
                except:
                    is_active = False
            
            # Если подписка истекла, но роль еще premium/vip, обновляем роль
            if not is_active and role in ['premium', 'vip']:
                oracle_client.update_document('users', uid, {'role': 'user'})
                role = 'user'
            
            return UserSubscription(
                level=role if is_active else 'free',
                expires_at=expires_at,
                is_active=is_active
            )
        else:
            # Нет записи о подписке, определяем по роли
            level = 'free' if role == 'user' else role
            return UserSubscription(
                level=level,
                expires_at=None,
                is_active=role in ['premium', 'vip', 'admin', 'moderator']
            )
        
    except Exception as e:
        logger.error(f"Ошибка получения подписки пользователя {uid}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@router.get('/analyses')
async def get_user_analyses(uid: str = Depends(get_uid), limit: int = 50, offset: int = 0):
    """Получение истории анализов пользователя"""
    try:
        # Получаем анализы пользователя с пагинацией
        analyses = oracle_client.query_documents(
            'analyses',
            filter_conditions={'telegram_id': uid},
            limit=limit,
            offset=offset,
            order_by='created_at',
            order_direction='desc'
        )
        
        # Форматируем данные для фронтенда
        formatted_analyses = []
        for analysis in analyses:
            formatted_analyses.append({
                'id': analysis.get('id'),
                'symbol': analysis.get('symbol'),
                'created_at': analysis.get('created_at'),
                'analysis_type': analysis.get('analysis_type', 'technical'),
                'status': analysis.get('status', 'completed')
            })
        
        return {
            'analyses': formatted_analyses,
            'total': len(analyses),
            'limit': limit,
            'offset': offset
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения анализов пользователя {uid}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@router.get('/watchlist')
async def get_user_watchlist(uid: str = Depends(get_uid)):
    """Получение watchlist пользователя"""
    try:
        # Получаем watchlist пользователя
        watchlist = oracle_client.query_documents(
            'watchlist',
            filter_conditions={'telegram_id': uid},
            limit=1000
        )
        
        # Форматируем данные
        formatted_watchlist = []
        for item in watchlist:
            formatted_watchlist.append({
                'symbol': item.get('symbol'),
                'added_at': item.get('added_at'),
                'notes': item.get('notes', '')
            })
        
        return {
            'watchlist': formatted_watchlist,
            'count': len(formatted_watchlist)
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения watchlist пользователя {uid}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@router.post('/watchlist/{symbol}')
async def add_to_watchlist(symbol: str, uid: str = Depends(get_uid)):
    """Добавление символа в watchlist"""
    try:
        # Проверяем, есть ли уже такой символ
        existing = oracle_client.query_documents(
            'watchlist',
            filter_conditions={'telegram_id': uid, 'symbol': symbol.upper()},
            limit=1
        )
        
        if existing:
            raise HTTPException(status_code=400, detail="Символ уже в watchlist")
        
        # Добавляем в watchlist
        watchlist_item = {
            'telegram_id': uid,
            'symbol': symbol.upper(),
            'added_at': datetime.now().isoformat(),
            'notes': ''
        }
        
        oracle_client.create_document('watchlist', watchlist_item)
        
        return {'message': 'Символ добавлен в watchlist', 'symbol': symbol.upper()}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка добавления в watchlist {uid}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@router.delete('/watchlist/{symbol}')
async def remove_from_watchlist(symbol: str, uid: str = Depends(get_uid)):
    """Удаление символа из watchlist"""
    try:
        # Находим и удаляем символ
        existing = oracle_client.query_documents(
            'watchlist',
            filter_conditions={'telegram_id': uid, 'symbol': symbol.upper()},
            limit=1
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Символ не найден в watchlist")
        
        # Удаляем документ (предполагаем, что у документа есть ID)
        doc_id = existing[0].get('id')
        if doc_id:
            oracle_client.delete_document('watchlist', doc_id)
        
        return {'message': 'Символ удален из watchlist', 'symbol': symbol.upper()}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка удаления из watchlist {uid}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")
