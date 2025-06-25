# backend/routers/admin.py

import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.config.config import logger, db
from backend.auth.dependencies import require_role, get_uid
from google.cloud import firestore


router = APIRouter(
    prefix='/admin',
    tags=['admin'],
    dependencies=[Depends(require_role('admin'))]
)


class SetRoleRequest(BaseModel):
    telegram_id: str
    role: str
    subscription_days: int = 0


class BroadcastRequest(BaseModel):
    text: str


@router.get('/stats')
async def get_stats():
    """Получение статистики пользователей"""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="База данных недоступна")
        
        # Получаем всех пользователей
        users_ref = db.collection('users')
        users = users_ref.stream()
        
        # Подсчитываем по ролям
        role_counts = {
            'admin': 0,
            'moderator': 0,
            'vip': 0,
            'premium': 0,
            'user': 0
        }
        
        total_users = 0
        for user in users:
            total_users += 1
            user_data = user.to_dict()
            role = user_data.get('role', 'user')
            if role in role_counts:
                role_counts[role] += 1
        
        # Получаем активные подписки
        subs_ref = db.collection('subscriptions')
        subs = subs_ref.stream()
        
        active_premium = 0
        active_vip = 0
        now = datetime.utcnow()
        
        for sub in subs:
            sub_data = sub.to_dict()
            expires_at = sub_data.get('expires_at')
            level = sub_data.get('level', '')
            
            if expires_at and expires_at > now:
                if level == 'premium':
                    active_premium += 1
                elif level == 'vip':
                    active_vip += 1
        
        return {
            'total_users': total_users,
            'roles': role_counts,
            'active_subscriptions': {
                'premium': active_premium,
                'vip': active_vip
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения статистики")


@router.post('/set_role')
async def set_role(request: SetRoleRequest):
    """Установка роли пользователю"""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="База данных недоступна")
        
        # Проверяем валидность роли
        valid_roles = ['user', 'premium', 'vip', 'moderator', 'admin']
        if request.role not in valid_roles:
            raise HTTPException(status_code=400, detail=f"Неверная роль. Доступные: {valid_roles}")
        
        # Обновляем роль пользователя
        user_ref = db.collection('users').document(request.telegram_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        user_ref.update({
            'role': request.role,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        
        # Если указаны дни подписки, создаем/обновляем подписку
        if request.subscription_days > 0:
            sub_ref = db.collection('subscriptions').document(request.telegram_id)
            expires_at = datetime.utcnow() + timedelta(days=request.subscription_days)
            
            sub_ref.set({
                'level': request.role if request.role in ['premium', 'vip'] else 'premium',
                'expires_at': expires_at,
                'created_at': firestore.SERVER_TIMESTAMP
            })
        
        logger.info(f"Роль {request.role} установлена пользователю {request.telegram_id}")
        
        return {
            'success': True,
            'message': f'Роль {request.role} установлена пользователю {request.telegram_id}'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка установки роли: {e}")
        raise HTTPException(status_code=500, detail="Ошибка установки роли")


@router.post('/broadcast')
async def broadcast_message(request: BroadcastRequest):
    """Рассылка сообщения всем пользователям"""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="База данных недоступна")
        
        # Получаем всех пользователей
        users_ref = db.collection('users')
        users = users_ref.stream()
        
        user_ids = []
        for user in users:
            user_ids.append(user.id)
        
        # Сохраняем задачу на рассылку в очередь
        broadcast_ref = db.collection('broadcast_queue').document()
        broadcast_ref.set({
            'text': request.text,
            'user_ids': user_ids,
            'status': 'pending',
            'created_at': firestore.SERVER_TIMESTAMP
        })
        
        logger.info(f"Создана задача на рассылку для {len(user_ids)} пользователей")
        
        return {
            'success': True,
            'message': f'Рассылка запланирована для {len(user_ids)} пользователей',
            'broadcast_id': broadcast_ref.id
        }
        
    except Exception as e:
        logger.error(f"Ошибка создания рассылки: {e}")
        raise HTTPException(status_code=500, detail="Ошибка создания рассылки")


@router.post('/gc')
async def garbage_collect():
    """Ручная очистка устаревших данных"""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="База данных недоступна")
        
        # Удаляем анализы старше 30 дней
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        analyses_ref = db.collection('analyses')
        old_analyses = analyses_ref.where('created_at', '<', cutoff_date).stream()
        
        deleted_analyses = 0
        for analysis in old_analyses:
            analysis.reference.delete()
            deleted_analyses += 1
        
        # Удаляем флаги старше 14 дней
        flags_cutoff = datetime.utcnow() - timedelta(days=14)
        flags_ref = db.collection('flags')
        old_flags = flags_ref.where('ts', '<', flags_cutoff).stream()
        
        deleted_flags = 0
        for flag in old_flags:
            flag.reference.delete()
            deleted_flags += 1
        
        # Удаляем истекшие баны
        bans_ref = db.collection('bans')
        expired_bans = bans_ref.where('expires_at', '<', datetime.utcnow()).stream()
        
        deleted_bans = 0
        for ban in expired_bans:
            ban.reference.delete()
            deleted_bans += 1
        
        logger.info(f"Очистка завершена: анализы={deleted_analyses}, флаги={deleted_flags}, баны={deleted_bans}")
        
        return {
            'success': True,
            'deleted': {
                'analyses': deleted_analyses,
                'flags': deleted_flags,
                'bans': deleted_bans
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка очистки данных: {e}")
        raise HTTPException(status_code=500, detail="Ошибка очистки данных")
