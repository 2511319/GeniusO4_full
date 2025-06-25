# backend/routers/mod.py

from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.config.config import logger, db
from backend.auth.dependencies import require_role, get_uid
from google.cloud import firestore


router = APIRouter(
    prefix='/moderator',
    tags=['moderator'],
    dependencies=[Depends(require_role('moderator'))]
)


class BanRequest(BaseModel):
    telegram_id: str
    days: int = 30
    reason: str = ""


class UnbanRequest(BaseModel):
    telegram_id: str


class ReviewFlagRequest(BaseModel):
    analysis_ulid: str
    reason: str


@router.post('/ban')
async def ban_user(request: BanRequest, moderator_id: str = Depends(get_uid)):
    """Забанить пользователя"""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="База данных недоступна")
        
        # Проверяем, существует ли пользователь
        user_ref = db.collection('users').document(request.telegram_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        user_data = user_doc.to_dict()
        user_role = user_data.get('role', 'user')
        
        # Модераторы не могут банить админов и других модераторов
        if user_role in ['admin', 'moderator']:
            raise HTTPException(status_code=403, detail="Нельзя забанить администратора или модератора")
        
        # Создаем запись о бане
        ban_ref = db.collection('bans').document(request.telegram_id)
        expires_at = datetime.utcnow() + timedelta(days=request.days)
        
        ban_ref.set({
            'telegram_id': request.telegram_id,
            'moderator_id': moderator_id,
            'reason': request.reason,
            'expires_at': expires_at,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        
        logger.info(f"Пользователь {request.telegram_id} забанен модератором {moderator_id} на {request.days} дней")
        
        return {
            'success': True,
            'message': f'Пользователь {request.telegram_id} забанен на {request.days} дней',
            'expires_at': expires_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка бана пользователя: {e}")
        raise HTTPException(status_code=500, detail="Ошибка бана пользователя")


@router.post('/unban')
async def unban_user(request: UnbanRequest, moderator_id: str = Depends(get_uid)):
    """Разбанить пользователя"""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="База данных недоступна")
        
        # Проверяем, забанен ли пользователь
        ban_ref = db.collection('bans').document(request.telegram_id)
        ban_doc = ban_ref.get()
        
        if not ban_doc.exists:
            raise HTTPException(status_code=404, detail="Пользователь не забанен")
        
        # Удаляем бан
        ban_ref.delete()
        
        logger.info(f"Пользователь {request.telegram_id} разбанен модератором {moderator_id}")
        
        return {
            'success': True,
            'message': f'Пользователь {request.telegram_id} разбанен'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка разбана пользователя: {e}")
        raise HTTPException(status_code=500, detail="Ошибка разбана пользователя")


@router.post('/review_flag')
async def review_flag(request: ReviewFlagRequest, moderator_id: str = Depends(get_uid)):
    """Пометить анализ флагом для проверки"""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="База данных недоступна")
        
        # Проверяем, существует ли анализ
        analysis_ref = db.collection('analyses').document(request.analysis_ulid)
        analysis_doc = analysis_ref.get()
        
        if not analysis_doc.exists:
            raise HTTPException(status_code=404, detail="Анализ не найден")
        
        # Создаем флаг
        flag_ref = db.collection('flags').document(request.analysis_ulid)
        flag_ref.set({
            'analysis_ulid': request.analysis_ulid,
            'reason': request.reason,
            'flagged_by': moderator_id,
            'ts': firestore.SERVER_TIMESTAMP
        })
        
        logger.info(f"Анализ {request.analysis_ulid} помечен флагом модератором {moderator_id}")
        
        return {
            'success': True,
            'message': f'Анализ {request.analysis_ulid} помечен для проверки'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка создания флага: {e}")
        raise HTTPException(status_code=500, detail="Ошибка создания флага")


@router.get('/bans')
async def get_bans():
    """Получить список активных банов"""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="База данных недоступна")
        
        # Получаем активные баны
        bans_ref = db.collection('bans')
        active_bans = bans_ref.where('expires_at', '>', datetime.utcnow()).stream()
        
        bans_list = []
        for ban in active_bans:
            ban_data = ban.to_dict()
            bans_list.append({
                'telegram_id': ban_data.get('telegram_id'),
                'reason': ban_data.get('reason', ''),
                'expires_at': ban_data.get('expires_at').isoformat() if ban_data.get('expires_at') else None,
                'moderator_id': ban_data.get('moderator_id'),
                'created_at': ban_data.get('created_at').isoformat() if ban_data.get('created_at') else None
            })
        
        return {
            'bans': bans_list,
            'total': len(bans_list)
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения списка банов: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения списка банов")


@router.get('/flags')
async def get_flags():
    """Получить список флагов для проверки"""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="База данных недоступна")
        
        # Получаем все флаги
        flags_ref = db.collection('flags')
        flags = flags_ref.order_by('ts', direction=firestore.Query.DESCENDING).limit(50).stream()
        
        flags_list = []
        for flag in flags:
            flag_data = flag.to_dict()
            flags_list.append({
                'analysis_ulid': flag_data.get('analysis_ulid'),
                'reason': flag_data.get('reason', ''),
                'flagged_by': flag_data.get('flagged_by'),
                'ts': flag_data.get('ts').isoformat() if flag_data.get('ts') else None
            })
        
        return {
            'flags': flags_list,
            'total': len(flags_list)
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения списка флагов: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения списка флагов")
