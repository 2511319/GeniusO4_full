# backend/services/analysis_storage.py

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)

# Для локального тестирования
LOCAL_TESTING = os.getenv("LOCAL_TESTING", "true").lower() == "true"

def save_analysis(telegram_id: str, analysis_data: Dict[str, Any]) -> str:
    """
    Сохраняет результат анализа в Firestore
    """
    if LOCAL_TESTING:
        analysis_id = f"analysis_{telegram_id}_{int(datetime.utcnow().timestamp())}"
        logger.info(f"[LOCAL] Анализ сохранен с ID: {analysis_id}")
        return analysis_id

    try:
        from backend.config.config import db
        if db is None:
            logger.error("Firestore Client не инициализирован.")
            return None

        # Генерируем уникальный ID для анализа
        analysis_id = f"analysis_{telegram_id}_{int(datetime.utcnow().timestamp())}"
        
        # Подготавливаем данные для сохранения
        analysis_doc = {
            'id': analysis_id,
            'telegram_id': str(telegram_id),
            'symbol': analysis_data.get('symbol', 'UNKNOWN'),
            'analysis_type': analysis_data.get('type', 'simple'),
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(days=30),  # TTL 30 дней
            'analysis_result': analysis_data.get('analysis', {}),
            'primary_analysis': analysis_data.get('primary_analysis', {}),
            'ohlc_data': analysis_data.get('ohlc', []),
            'indicators': analysis_data.get('indicators', []),
            'metadata': {
                'interval': analysis_data.get('interval', '4h'),
                'limit': analysis_data.get('limit', 100),
                'timestamp': analysis_data.get('timestamp', int(datetime.utcnow().timestamp()))
            }
        }
        
        # Сохраняем в коллекцию analyses
        analyses_ref = db.collection('analyses').document(analysis_id)
        analyses_ref.set(analysis_doc)
        
        logger.info(f"Анализ сохранен в Firestore с ID: {analysis_id}")
        return analysis_id
        
    except Exception as e:
        logger.error(f"Ошибка сохранения анализа: {e}")
        return None

def get_analysis(analysis_id: str) -> Optional[Dict[str, Any]]:
    """
    Получает анализ по ID из Firestore
    """
    if LOCAL_TESTING:
        logger.info(f"[LOCAL] Запрос анализа с ID: {analysis_id}")
        return {
            'id': analysis_id,
            'symbol': 'BTCUSDT',
            'analysis_type': 'simple',
            'created_at': datetime.utcnow(),
            'analysis_result': {'summary': 'Тестовый анализ'},
            'primary_analysis': {'trend': 'Восходящий', 'signal': 'Long'}
        }

    try:
        from backend.config.config import db
        if db is None:
            logger.error("Firestore Client не инициализирован.")
            return None

        analysis_ref = db.collection('analyses').document(analysis_id)
        analysis_doc = analysis_ref.get()
        
        if analysis_doc.exists:
            data = analysis_doc.to_dict()
            
            # Проверяем, не истек ли анализ
            expires_at = data.get('expires_at')
            if expires_at and expires_at < datetime.utcnow():
                logger.warning(f"Анализ {analysis_id} истек")
                return None
                
            return data
        else:
            logger.warning(f"Анализ {analysis_id} не найден")
            return None
            
    except Exception as e:
        logger.error(f"Ошибка получения анализа: {e}")
        return None

def get_user_analyses(telegram_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Получает список анализов пользователя
    """
    if LOCAL_TESTING:
        logger.info(f"[LOCAL] Запрос анализов для пользователя: {telegram_id}")
        return [
            {
                'id': f'analysis_{telegram_id}_1',
                'symbol': 'BTCUSDT',
                'analysis_type': 'full',
                'created_at': datetime.utcnow() - timedelta(hours=2),
                'primary_analysis': {'trend': 'Восходящий', 'signal': 'Long'}
            },
            {
                'id': f'analysis_{telegram_id}_2',
                'symbol': 'ETHUSDT', 
                'analysis_type': 'simple',
                'created_at': datetime.utcnow() - timedelta(hours=5),
                'primary_analysis': {'trend': 'Боковой', 'signal': 'Hold'}
            }
        ]

    try:
        from backend.config.config import db
        if db is None:
            logger.error("Firestore Client не инициализирован.")
            return []

        # Запрашиваем анализы пользователя, отсортированные по дате создания
        analyses_ref = db.collection('analyses') \
            .where('telegram_id', '==', str(telegram_id)) \
            .where('expires_at', '>', datetime.utcnow()) \
            .order_by('created_at', direction='DESCENDING') \
            .limit(limit)
        
        analyses = []
        for doc in analyses_ref.stream():
            data = doc.to_dict()
            analyses.append({
                'id': data.get('id'),
                'symbol': data.get('symbol'),
                'analysis_type': data.get('analysis_type'),
                'created_at': data.get('created_at'),
                'primary_analysis': data.get('primary_analysis', {})
            })
        
        logger.info(f"Найдено {len(analyses)} анализов для пользователя {telegram_id}")
        return analyses
        
    except Exception as e:
        logger.error(f"Ошибка получения анализов пользователя: {e}")
        return []

def delete_analysis(analysis_id: str, telegram_id: str) -> bool:
    """
    Удаляет анализ (только владелец может удалить)
    """
    if LOCAL_TESTING:
        logger.info(f"[LOCAL] Удаление анализа {analysis_id} пользователем {telegram_id}")
        return True

    try:
        from backend.config.config import db
        if db is None:
            logger.error("Firestore Client не инициализирован.")
            return False

        # Сначала проверяем, что анализ принадлежит пользователю
        analysis_ref = db.collection('analyses').document(analysis_id)
        analysis_doc = analysis_ref.get()
        
        if not analysis_doc.exists:
            logger.warning(f"Анализ {analysis_id} не найден")
            return False
            
        data = analysis_doc.to_dict()
        if data.get('telegram_id') != str(telegram_id):
            logger.warning(f"Пользователь {telegram_id} не может удалить анализ {analysis_id}")
            return False
        
        # Удаляем анализ
        analysis_ref.delete()
        logger.info(f"Анализ {analysis_id} удален пользователем {telegram_id}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка удаления анализа: {e}")
        return False

def cleanup_expired_analyses():
    """
    Очищает истекшие анализы (для периодического запуска)
    """
    if LOCAL_TESTING:
        logger.info("[LOCAL] Очистка истекших анализов пропущена")
        return

    try:
        from backend.config.config import db
        if db is None:
            logger.error("Firestore Client не инициализирован.")
            return

        # Находим истекшие анализы
        expired_ref = db.collection('analyses') \
            .where('expires_at', '<', datetime.utcnow()) \
            .limit(100)  # Обрабатываем по 100 за раз
        
        deleted_count = 0
        for doc in expired_ref.stream():
            doc.reference.delete()
            deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"Удалено {deleted_count} истекших анализов")
            
    except Exception as e:
        logger.error(f"Ошибка очистки истекших анализов: {e}")
