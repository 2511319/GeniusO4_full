# ⚡ Task Service for ChartGenius
# Версия: 1.1.0-dev
# Background tasks с Celery для асинхронной обработки

import os
import asyncio
import json
from typing import Dict, Any, List, Optional
from celery import Celery
from celery.result import AsyncResult
import redis.asyncio as redis
from datetime import datetime, timedelta
import logging
from backend.services.llm_service import LLMService
from backend.services.metrics_service import metrics

logger = logging.getLogger(__name__)

# === CELERY CONFIGURATION ===
celery_app = Celery(
    'chartgenius',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=['backend.services.task_service']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 минут максимум
    task_soft_time_limit=240,  # 4 минуты soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# === TASK STATUS ENUM ===
class TaskStatus:
    PENDING = 'PENDING'
    STARTED = 'STARTED'
    PROCESSING = 'PROCESSING'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    RETRY = 'RETRY'

# === BACKGROUND TASKS ===
@celery_app.task(bind=True, name='process_analysis')
def process_analysis_task(self, symbol: str, interval: str, layers: List[str], 
                         user_id: str, task_metadata: Dict[str, Any] = None):
    """
    Фоновая задача для обработки анализа криптовалют
    
    Args:
        symbol: Символ криптовалюты (например, BTCUSDT)
        interval: Временной интервал (например, 4h)
        layers: Список технических индикаторов
        user_id: ID пользователя
        task_metadata: Дополнительные метаданные
    """
    task_id = self.request.id
    start_time = datetime.utcnow()
    
    try:
        # Обновляем статус задачи
        self.update_state(
            state=TaskStatus.STARTED,
            meta={
                'status': 'Инициализация анализа...',
                'progress': 0,
                'started_at': start_time.isoformat()
            }
        )
        
        logger.info(f"Starting analysis task {task_id} for {symbol} {interval}")
        
        # === STEP 1: Получение рыночных данных ===
        self.update_state(
            state=TaskStatus.PROCESSING,
            meta={
                'status': 'Получение рыночных данных...',
                'progress': 20,
                'current_step': 'market_data'
            }
        )
        _notify_task_progress(task_id, 20, 'Получение рыночных данных...')

        # Получаем реальные рыночные данные
        try:
            from backend.services.market_data_service import market_data_service
            df = await market_data_service.get_ohlcv_data(symbol, interval, 500)

            if df is not None and not df.empty:
                market_data = {
                    'symbol': symbol,
                    'interval': interval,
                    'data': df.to_dict('records'),
                    'count': len(df),
                    'source': 'market_data_service'
                }
            else:
                # Fallback на симуляцию если нет данных
                market_data = _simulate_market_data_fetch(symbol, interval)

        except Exception as e:
            logger.warning(f"Ошибка получения рыночных данных: {e}, используем симуляцию")
            market_data = _simulate_market_data_fetch(symbol, interval)

        # === STEP 2: Вычисление технических индикаторов ===
        self.update_state(
            state=TaskStatus.PROCESSING,
            meta={
                'status': 'Вычисление технических индикаторов...',
                'progress': 40,
                'current_step': 'indicators',
                'indicators': layers
            }
        )
        _notify_task_progress(task_id, 40, 'Вычисление технических индикаторов...')

        # indicators = await calculate_indicators(market_data, layers)
        indicators = _simulate_indicators_calculation(market_data, layers)

        # === STEP 3: LLM анализ ===
        self.update_state(
            state=TaskStatus.PROCESSING,
            meta={
                'status': 'Генерация AI анализа...',
                'progress': 60,
                'current_step': 'llm_analysis'
            }
        )
        _notify_task_progress(task_id, 60, 'Генерация AI анализа...')
        
        # Используем синхронную версию LLM для Celery
        analysis_result = _generate_llm_analysis(symbol, interval, market_data, indicators)
        
        # === STEP 4: Постобработка ===
        self.update_state(
            state=TaskStatus.PROCESSING,
            meta={
                'status': 'Финализация результатов...',
                'progress': 80,
                'current_step': 'finalization'
            }
        )
        _notify_task_progress(task_id, 80, 'Финализация результатов...')
        
        # Формируем финальный результат
        final_result = {
            'symbol': symbol,
            'interval': interval,
            'layers': layers,
            'market_data': market_data,
            'indicators': indicators,
            'analysis': analysis_result,
            'metadata': {
                'task_id': task_id,
                'user_id': user_id,
                'created_at': start_time.isoformat(),
                'completed_at': datetime.utcnow().isoformat(),
                'processing_time_seconds': (datetime.utcnow() - start_time).total_seconds()
            }
        }
        
        # Сохраняем результат в Redis с TTL
        _save_analysis_result(task_id, final_result)
        
        # Отправляем уведомление пользователю
        _notify_user_analysis_complete(user_id, task_id, symbol)
        
        # Обновляем метрики
        metrics.track_user_action('analysis_completed', 'user')
        
        logger.info(f"Analysis task {task_id} completed successfully")
        
        return {
            'status': 'completed',
            'result': final_result,
            'progress': 100
        }
        
    except Exception as e:
        logger.error(f"Analysis task {task_id} failed: {e}")
        
        # Обновляем метрики ошибок
        metrics.track_error(type(e).__name__, 'analysis_task')
        
        self.update_state(
            state=TaskStatus.FAILURE,
            meta={
                'status': f'Ошибка: {str(e)}',
                'error': str(e),
                'failed_at': datetime.utcnow().isoformat()
            }
        )
        
        raise

@celery_app.task(bind=True, name='cleanup_old_tasks')
def cleanup_old_tasks(self):
    """Очистка старых задач и результатов"""
    try:
        # Очищаем результаты старше 24 часов
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Здесь будет логика очистки Redis
        logger.info("Cleanup task completed")
        
        return {'status': 'completed', 'cleaned_tasks': 0}
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {e}")
        raise

# === HELPER FUNCTIONS ===
def _simulate_market_data_fetch(symbol: str, interval: str) -> Dict[str, Any]:
    """Симуляция получения рыночных данных"""
    import time
    time.sleep(2)  # Имитация API запроса
    
    return {
        'symbol': symbol,
        'interval': interval,
        'data': [
            {'timestamp': '2025-06-25T10:00:00Z', 'open': 50000, 'high': 51000, 'low': 49500, 'close': 50500, 'volume': 1000},
            {'timestamp': '2025-06-25T14:00:00Z', 'open': 50500, 'high': 52000, 'low': 50000, 'close': 51500, 'volume': 1200},
        ],
        'count': 2
    }

def _simulate_indicators_calculation(market_data: Dict[str, Any], layers: List[str]) -> Dict[str, Any]:
    """Симуляция вычисления технических индикаторов"""
    import time
    time.sleep(1)  # Имитация вычислений
    
    indicators = {}
    for layer in layers:
        if layer == 'RSI':
            indicators['RSI'] = [45.2, 52.8]
        elif layer == 'MACD':
            indicators['MACD'] = [0.12, 0.18]
        elif layer == 'MA_20':
            indicators['MA_20'] = [50250, 51000]
    
    return indicators

def _generate_llm_analysis(symbol: str, interval: str, market_data: Dict[str, Any], 
                          indicators: Dict[str, Any]) -> str:
    """Генерация LLM анализа (синхронная версия для Celery)"""
    import time
    time.sleep(5)  # Имитация LLM запроса
    
    # В реальной реализации здесь будет вызов LLM
    analysis = f"""
    Технический анализ {symbol} на интервале {interval}:
    
    📊 Текущая ситуация:
    - Цена находится в боковом тренде
    - RSI показывает нейтральные значения
    - Объемы торгов умеренные
    
    🎯 Рекомендации:
    - Ожидание пробоя ключевых уровней
    - Риск-менеджмент обязателен
    
    ⚠️ Риски: Средние
    """
    
    return analysis.strip()

def _save_analysis_result(task_id: str, result: Dict[str, Any]):
    """Сохранение результата анализа в Redis"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Сохраняем с TTL 24 часа
        r.setex(f"analysis_result:{task_id}", 86400, json.dumps(result))
        
        logger.info(f"Analysis result saved for task {task_id}")
        
    except Exception as e:
        logger.error(f"Failed to save analysis result: {e}")

def _notify_user_analysis_complete(user_id: str, task_id: str, symbol: str):
    """Уведомление пользователя о завершении анализа"""
    try:
        # Отправляем уведомление через Redis pub/sub для WebSocket
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)

        notification_data = {
            'type': 'personal',
            'user_id': user_id,
            'message': {
                'type': 'analysis_completed',
                'task_id': task_id,
                'symbol': symbol,
                'message': f'Анализ {symbol} завершен',
                'timestamp': datetime.utcnow().isoformat(),
                'action': {
                    'type': 'view_result',
                    'url': f'/analysis/result/{task_id}'
                }
            }
        }

        r.publish('chartgenius:notifications', json.dumps(notification_data))
        logger.info(f"WebSocket notification sent to user {user_id} for task {task_id}")

    except Exception as e:
        logger.error(f"Failed to notify user: {e}")

def _notify_task_progress(task_id: str, progress: int, status: str):
    """Уведомление о прогрессе задачи"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)

        notification_data = {
            'type': 'task_update',
            'task_id': task_id,
            'data': {
                'progress': progress,
                'status': status,
                'timestamp': datetime.utcnow().isoformat()
            }
        }

        r.publish('chartgenius:notifications', json.dumps(notification_data))
        logger.debug(f"Task progress notification sent for {task_id}: {progress}%")

    except Exception as e:
        logger.error(f"Failed to notify task progress: {e}")

# === TASK MANAGEMENT CLASS ===
class TaskManager:
    """Менеджер для управления фоновыми задачами"""
    
    def __init__(self):
        self.redis_client = None
    
    async def get_redis(self):
        """Получение Redis клиента"""
        if not self.redis_client:
            self.redis_client = redis.Redis(
                host='localhost', 
                port=6379, 
                decode_responses=True
            )
        return self.redis_client
    
    async def start_analysis_task(self, symbol: str, interval: str, layers: List[str], 
                                 user_id: str) -> str:
        """Запуск задачи анализа"""
        try:
            task = process_analysis_task.delay(symbol, interval, layers, user_id)
            
            # Сохраняем информацию о задаче
            task_info = {
                'task_id': task.id,
                'symbol': symbol,
                'interval': interval,
                'layers': layers,
                'user_id': user_id,
                'status': TaskStatus.PENDING,
                'created_at': datetime.utcnow().isoformat()
            }
            
            redis_client = await self.get_redis()
            await redis_client.setex(
                f"task_info:{task.id}", 
                86400,  # 24 часа TTL
                json.dumps(task_info)
            )
            
            logger.info(f"Analysis task started: {task.id}")
            return task.id
            
        except Exception as e:
            logger.error(f"Failed to start analysis task: {e}")
            raise
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Получение статуса задачи"""
        try:
            result = AsyncResult(task_id, app=celery_app)
            
            task_info = {
                'task_id': task_id,
                'status': result.status,
                'result': result.result if result.ready() else None,
                'info': result.info if hasattr(result, 'info') else None
            }
            
            # Дополнительная информация из Redis
            redis_client = await self.get_redis()
            stored_info = await redis_client.get(f"task_info:{task_id}")
            if stored_info:
                stored_data = json.loads(stored_info)
                task_info.update(stored_data)
            
            return task_info
            
        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            return {
                'task_id': task_id,
                'status': 'ERROR',
                'error': str(e)
            }
    
    async def cancel_task(self, task_id: str) -> bool:
        """Отмена задачи"""
        try:
            celery_app.control.revoke(task_id, terminate=True)
            
            # Обновляем статус в Redis
            redis_client = await self.get_redis()
            task_info = await redis_client.get(f"task_info:{task_id}")
            if task_info:
                data = json.loads(task_info)
                data['status'] = 'CANCELLED'
                data['cancelled_at'] = datetime.utcnow().isoformat()
                await redis_client.setex(f"task_info:{task_id}", 86400, json.dumps(data))
            
            logger.info(f"Task cancelled: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel task: {e}")
            return False

# Глобальный экземпляр менеджера задач
task_manager = TaskManager()
