# 🔄 WebSocket Service for ChartGenius
# Версия: 1.1.0-dev
# Real-time уведомления для пользователей

import json
import asyncio
import logging
from typing import Dict, Set, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import redis.asyncio as redis
from backend.services.metrics_service import metrics

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Менеджер WebSocket соединений"""
    
    def __init__(self):
        # Активные соединения: user_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # Подписки на задачи: task_id -> Set[user_id]
        self.task_subscriptions: Dict[str, Set[str]] = {}
        # Redis для pub/sub
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub_task: Optional[asyncio.Task] = None
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Подключение нового клиента"""
        try:
            await websocket.accept()
            self.active_connections[user_id] = websocket
            
            # Инициализируем Redis если нужно
            if not self.redis_client:
                await self._init_redis()
            
            # Отправляем приветственное сообщение
            await self.send_personal_message({
                'type': 'connection_established',
                'message': 'WebSocket соединение установлено',
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': user_id
            }, user_id)
            
            logger.info(f"WebSocket connected: user {user_id}")
            metrics.track_user_action('websocket_connect', 'user')
            
        except Exception as e:
            logger.error(f"Error connecting WebSocket for user {user_id}: {e}")
            raise
    
    def disconnect(self, user_id: str):
        """Отключение клиента"""
        try:
            if user_id in self.active_connections:
                del self.active_connections[user_id]
            
            # Удаляем из всех подписок на задачи
            for task_id, subscribers in self.task_subscriptions.items():
                subscribers.discard(user_id)
            
            # Очищаем пустые подписки
            self.task_subscriptions = {
                task_id: subscribers 
                for task_id, subscribers in self.task_subscriptions.items() 
                if subscribers
            }
            
            logger.info(f"WebSocket disconnected: user {user_id}")
            metrics.track_user_action('websocket_disconnect', 'user')
            
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket for user {user_id}: {e}")
    
    async def send_personal_message(self, message: Dict[str, Any], user_id: str):
        """Отправка персонального сообщения"""
        try:
            if user_id in self.active_connections:
                websocket = self.active_connections[user_id]
                await websocket.send_text(json.dumps(message))
                logger.debug(f"Message sent to user {user_id}: {message['type']}")
            else:
                logger.warning(f"User {user_id} not connected, message not sent")
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected during message send: user {user_id}")
            self.disconnect(user_id)
        except Exception as e:
            logger.error(f"Error sending message to user {user_id}: {e}")
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Широковещательная отправка сообщения"""
        try:
            disconnected_users = []
            
            for user_id, websocket in self.active_connections.items():
                try:
                    await websocket.send_text(json.dumps(message))
                except WebSocketDisconnect:
                    disconnected_users.append(user_id)
                except Exception as e:
                    logger.error(f"Error broadcasting to user {user_id}: {e}")
                    disconnected_users.append(user_id)
            
            # Удаляем отключенных пользователей
            for user_id in disconnected_users:
                self.disconnect(user_id)
            
            logger.info(f"Broadcast message sent to {len(self.active_connections)} users")
            
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
    
    async def subscribe_to_task(self, user_id: str, task_id: str):
        """Подписка пользователя на обновления задачи"""
        try:
            if task_id not in self.task_subscriptions:
                self.task_subscriptions[task_id] = set()
            
            self.task_subscriptions[task_id].add(user_id)
            
            await self.send_personal_message({
                'type': 'task_subscription',
                'message': f'Подписка на задачу {task_id} активирована',
                'task_id': task_id,
                'timestamp': datetime.utcnow().isoformat()
            }, user_id)
            
            logger.info(f"User {user_id} subscribed to task {task_id}")
            
        except Exception as e:
            logger.error(f"Error subscribing user {user_id} to task {task_id}: {e}")
    
    async def notify_task_update(self, task_id: str, update_data: Dict[str, Any]):
        """Уведомление подписчиков об обновлении задачи"""
        try:
            if task_id not in self.task_subscriptions:
                return
            
            subscribers = self.task_subscriptions[task_id]
            message = {
                'type': 'task_update',
                'task_id': task_id,
                'data': update_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            for user_id in subscribers.copy():  # Копируем для безопасной итерации
                await self.send_personal_message(message, user_id)
            
            logger.info(f"Task update sent to {len(subscribers)} subscribers for task {task_id}")
            
        except Exception as e:
            logger.error(f"Error notifying task update for {task_id}: {e}")
    
    async def _init_redis(self):
        """Инициализация Redis для pub/sub"""
        try:
            self.redis_client = redis.Redis(
                host='localhost', 
                port=6379, 
                decode_responses=True
            )
            
            # Запускаем задачу прослушивания Redis pub/sub
            self.pubsub_task = asyncio.create_task(self._redis_listener())
            
            logger.info("Redis pub/sub initialized for WebSocket")
            
        except Exception as e:
            logger.error(f"Error initializing Redis for WebSocket: {e}")
    
    async def _redis_listener(self):
        """Прослушивание Redis pub/sub для уведомлений"""
        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe('chartgenius:notifications')
            
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        await self._handle_redis_notification(data)
                    except Exception as e:
                        logger.error(f"Error handling Redis notification: {e}")
                        
        except Exception as e:
            logger.error(f"Error in Redis listener: {e}")
    
    async def _handle_redis_notification(self, data: Dict[str, Any]):
        """Обработка уведомлений из Redis"""
        try:
            notification_type = data.get('type')
            
            if notification_type == 'task_update':
                task_id = data.get('task_id')
                update_data = data.get('data', {})
                await self.notify_task_update(task_id, update_data)
                
            elif notification_type == 'broadcast':
                message = data.get('message', {})
                await self.broadcast_message(message)
                
            elif notification_type == 'personal':
                user_id = data.get('user_id')
                message = data.get('message', {})
                if user_id:
                    await self.send_personal_message(message, user_id)
            
        except Exception as e:
            logger.error(f"Error handling Redis notification: {e}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Получение статистики соединений"""
        return {
            'active_connections': len(self.active_connections),
            'task_subscriptions': len(self.task_subscriptions),
            'total_subscribers': sum(len(subs) for subs in self.task_subscriptions.values()),
            'connected_users': list(self.active_connections.keys())
        }

# Глобальный менеджер соединений
connection_manager = ConnectionManager()

# === NOTIFICATION HELPERS ===
async def notify_analysis_started(user_id: str, task_id: str, symbol: str, interval: str):
    """Уведомление о начале анализа"""
    message = {
        'type': 'analysis_started',
        'task_id': task_id,
        'symbol': symbol,
        'interval': interval,
        'message': f'Анализ {symbol} ({interval}) запущен',
        'timestamp': datetime.utcnow().isoformat()
    }
    
    await connection_manager.send_personal_message(message, user_id)

async def notify_analysis_progress(task_id: str, progress: int, status: str):
    """Уведомление о прогрессе анализа"""
    update_data = {
        'progress': progress,
        'status': status,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    await connection_manager.notify_task_update(task_id, update_data)

async def notify_analysis_completed(user_id: str, task_id: str, symbol: str):
    """Уведомление о завершении анализа"""
    message = {
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
    
    await connection_manager.send_personal_message(message, user_id)

async def notify_analysis_error(user_id: str, task_id: str, error_message: str):
    """Уведомление об ошибке анализа"""
    message = {
        'type': 'analysis_error',
        'task_id': task_id,
        'error': error_message,
        'message': 'Произошла ошибка при анализе',
        'timestamp': datetime.utcnow().isoformat()
    }
    
    await connection_manager.send_personal_message(message, user_id)

async def notify_system_maintenance(message: str, duration_minutes: int = 0):
    """Уведомление о системном обслуживании"""
    broadcast_message = {
        'type': 'system_maintenance',
        'message': message,
        'duration_minutes': duration_minutes,
        'timestamp': datetime.utcnow().isoformat(),
        'severity': 'info'
    }
    
    await connection_manager.broadcast_message(broadcast_message)

# === REDIS PUBLISHER ===
async def publish_notification(notification_data: Dict[str, Any]):
    """Публикация уведомления через Redis pub/sub"""
    try:
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        await redis_client.publish('chartgenius:notifications', json.dumps(notification_data))
        await redis_client.close()
        
    except Exception as e:
        logger.error(f"Error publishing notification: {e}")

# === WEBSOCKET ENDPOINT HANDLER ===
async def websocket_endpoint_handler(websocket: WebSocket, user_id: str):
    """Обработчик WebSocket endpoint"""
    try:
        await connection_manager.connect(websocket, user_id)
        
        while True:
            # Ожидаем сообщения от клиента
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await _handle_client_message(message, user_id)
            except json.JSONDecodeError:
                await connection_manager.send_personal_message({
                    'type': 'error',
                    'message': 'Неверный формат сообщения',
                    'timestamp': datetime.utcnow().isoformat()
                }, user_id)
                
    except WebSocketDisconnect:
        connection_manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        connection_manager.disconnect(user_id)

async def _handle_client_message(message: Dict[str, Any], user_id: str):
    """Обработка сообщений от клиента"""
    try:
        message_type = message.get('type')
        
        if message_type == 'subscribe_task':
            task_id = message.get('task_id')
            if task_id:
                await connection_manager.subscribe_to_task(user_id, task_id)
        
        elif message_type == 'ping':
            await connection_manager.send_personal_message({
                'type': 'pong',
                'timestamp': datetime.utcnow().isoformat()
            }, user_id)
        
        elif message_type == 'get_stats':
            stats = connection_manager.get_connection_stats()
            await connection_manager.send_personal_message({
                'type': 'connection_stats',
                'data': stats,
                'timestamp': datetime.utcnow().isoformat()
            }, user_id)
        
        else:
            await connection_manager.send_personal_message({
                'type': 'error',
                'message': f'Неизвестный тип сообщения: {message_type}',
                'timestamp': datetime.utcnow().isoformat()
            }, user_id)
            
    except Exception as e:
        logger.error(f"Error handling client message from user {user_id}: {e}")
        await connection_manager.send_personal_message({
            'type': 'error',
            'message': 'Ошибка обработки сообщения',
            'timestamp': datetime.utcnow().isoformat()
        }, user_id)
