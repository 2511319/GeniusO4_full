# 🧪 Tests for WebSocket Service
# Версия: 1.1.0-dev
# Тесты для WebSocket сервиса

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from backend.services.websocket_service import ConnectionManager, WebSocketMessage, NotificationType


class TestConnectionManager:
    """Тесты для ConnectionManager"""
    
    @pytest.fixture
    def manager(self):
        """Фикстура для создания экземпляра менеджера"""
        return ConnectionManager()
    
    @pytest.fixture
    def mock_websocket(self):
        """Мок для WebSocket соединения"""
        websocket = AsyncMock()
        websocket.accept = AsyncMock()
        websocket.send_text = AsyncMock()
        websocket.close = AsyncMock()
        return websocket
    
    @pytest.mark.asyncio
    async def test_connect_new_user(self, manager, mock_websocket):
        """Тест подключения нового пользователя"""
        user_id = "test_user_123"
        
        # Тестируем подключение
        await manager.connect(mock_websocket, user_id)
        
        # Проверяем результат
        assert user_id in manager.active_connections
        assert manager.active_connections[user_id] == mock_websocket
        mock_websocket.accept.assert_called_once()
        mock_websocket.send_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connect_existing_user(self, manager, mock_websocket):
        """Тест переподключения существующего пользователя"""
        user_id = "test_user_123"
        old_websocket = AsyncMock()
        
        # Добавляем старое соединение
        manager.active_connections[user_id] = old_websocket
        
        # Тестируем переподключение
        await manager.connect(mock_websocket, user_id)
        
        # Проверяем что старое соединение закрыто
        old_websocket.close.assert_called_once()
        
        # Проверяем что новое соединение активно
        assert manager.active_connections[user_id] == mock_websocket
    
    @pytest.mark.asyncio
    async def test_disconnect_user(self, manager, mock_websocket):
        """Тест отключения пользователя"""
        user_id = "test_user_123"
        task_id = "task_123"
        
        # Добавляем соединение и подписку
        manager.active_connections[user_id] = mock_websocket
        manager.task_subscriptions[task_id] = {user_id}
        
        # Тестируем отключение
        await manager.disconnect(user_id)
        
        # Проверяем результат
        assert user_id not in manager.active_connections
        assert len(manager.task_subscriptions[task_id]) == 0
    
    @pytest.mark.asyncio
    async def test_send_personal_message_success(self, manager, mock_websocket):
        """Тест успешной отправки персонального сообщения"""
        user_id = "test_user_123"
        manager.active_connections[user_id] = mock_websocket
        
        message = WebSocketMessage(
            type="test_message",
            data={"content": "Hello"},
            timestamp=datetime.utcnow().isoformat(),
            user_id=user_id
        )
        
        # Тестируем отправку
        await manager.send_personal_message(user_id, message)
        
        # Проверяем что сообщение отправлено
        mock_websocket.send_text.assert_called_once()
        sent_data = json.loads(mock_websocket.send_text.call_args[0][0])
        assert sent_data["type"] == "test_message"
        assert sent_data["data"]["content"] == "Hello"
    
    @pytest.mark.asyncio
    async def test_send_personal_message_user_not_connected(self, manager):
        """Тест отправки сообщения неподключенному пользователю"""
        user_id = "nonexistent_user"
        
        message = WebSocketMessage(
            type="test_message",
            data={"content": "Hello"},
            timestamp=datetime.utcnow().isoformat(),
            user_id=user_id
        )
        
        # Тестируем отправку (не должно вызвать ошибку)
        await manager.send_personal_message(user_id, message)
        
        # Проверяем что пользователь не добавлен
        assert user_id not in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_broadcast_message(self, manager):
        """Тест рассылки сообщения всем пользователям"""
        # Добавляем несколько пользователей
        users = ["user1", "user2", "user3"]
        websockets = []
        
        for user_id in users:
            websocket = AsyncMock()
            websockets.append(websocket)
            manager.active_connections[user_id] = websocket
        
        message = WebSocketMessage(
            type="broadcast",
            data={"content": "Broadcast message"},
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Тестируем рассылку
        await manager.broadcast_message(message)
        
        # Проверяем что всем отправлено
        for websocket in websockets:
            websocket.send_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_broadcast_message_with_exclusion(self, manager):
        """Тест рассылки с исключением пользователя"""
        # Добавляем пользователей
        users = ["user1", "user2", "user3"]
        websockets = {}
        
        for user_id in users:
            websocket = AsyncMock()
            websockets[user_id] = websocket
            manager.active_connections[user_id] = websocket
        
        message = WebSocketMessage(
            type="broadcast",
            data={"content": "Broadcast message"},
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Тестируем рассылку с исключением user2
        await manager.broadcast_message(message, exclude_user="user2")
        
        # Проверяем результат
        websockets["user1"].send_text.assert_called_once()
        websockets["user2"].send_text.assert_not_called()
        websockets["user3"].send_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_subscribe_to_task(self, manager):
        """Тест подписки на задачу"""
        user_id = "test_user"
        task_id = "task_123"
        
        # Тестируем подписку
        await manager.subscribe_to_task(user_id, task_id)
        
        # Проверяем результат
        assert task_id in manager.task_subscriptions
        assert user_id in manager.task_subscriptions[task_id]
    
    @pytest.mark.asyncio
    async def test_unsubscribe_from_task(self, manager):
        """Тест отписки от задачи"""
        user_id = "test_user"
        task_id = "task_123"
        
        # Добавляем подписку
        manager.task_subscriptions[task_id] = {user_id}
        
        # Тестируем отписку
        await manager.unsubscribe_from_task(user_id, task_id)
        
        # Проверяем результат
        assert task_id not in manager.task_subscriptions
    
    @pytest.mark.asyncio
    async def test_notify_task_subscribers(self, manager):
        """Тест уведомления подписчиков задачи"""
        # Настраиваем подписчиков
        task_id = "task_123"
        users = ["user1", "user2"]
        websockets = {}
        
        for user_id in users:
            websocket = AsyncMock()
            websockets[user_id] = websocket
            manager.active_connections[user_id] = websocket
        
        manager.task_subscriptions[task_id] = set(users)
        
        message = WebSocketMessage(
            type="task_update",
            data={"progress": 50},
            timestamp=datetime.utcnow().isoformat(),
            task_id=task_id
        )
        
        # Тестируем уведомление
        await manager.notify_task_subscribers(task_id, message)
        
        # Проверяем что всем подписчикам отправлено
        for websocket in websockets.values():
            websocket.send_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_message_subscribe_task(self, manager):
        """Тест обработки сообщения подписки на задачу"""
        user_id = "test_user"
        websocket = AsyncMock()
        manager.active_connections[user_id] = websocket
        
        message_data = {
            "type": "subscribe_task",
            "data": {"task_id": "task_123"}
        }
        
        # Тестируем обработку
        await manager.handle_message(user_id, message_data)
        
        # Проверяем что подписка создана
        assert "task_123" in manager.task_subscriptions
        assert user_id in manager.task_subscriptions["task_123"]
        
        # Проверяем что отправлено подтверждение
        websocket.send_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_message_unsubscribe_task(self, manager):
        """Тест обработки сообщения отписки от задачи"""
        user_id = "test_user"
        task_id = "task_123"
        websocket = AsyncMock()
        
        # Настраиваем начальное состояние
        manager.active_connections[user_id] = websocket
        manager.task_subscriptions[task_id] = {user_id}
        
        message_data = {
            "type": "unsubscribe_task",
            "data": {"task_id": task_id}
        }
        
        # Тестируем обработку
        await manager.handle_message(user_id, message_data)
        
        # Проверяем что подписка удалена
        assert task_id not in manager.task_subscriptions
        
        # Проверяем что отправлено подтверждение
        websocket.send_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_message_ping(self, manager):
        """Тест обработки ping сообщения"""
        user_id = "test_user"
        websocket = AsyncMock()
        manager.active_connections[user_id] = websocket
        
        message_data = {
            "type": "ping",
            "data": {}
        }
        
        # Тестируем обработку
        await manager.handle_message(user_id, message_data)
        
        # Проверяем что отправлен pong
        websocket.send_text.assert_called_once()
        sent_data = json.loads(websocket.send_text.call_args[0][0])
        assert sent_data["type"] == "pong"
    
    def test_get_connection_stats(self, manager):
        """Тест получения статистики соединений"""
        # Добавляем тестовые данные
        manager.active_connections["user1"] = Mock()
        manager.active_connections["user2"] = Mock()
        manager.task_subscriptions["task1"] = {"user1", "user2"}
        manager.task_subscriptions["task2"] = {"user1"}
        
        # Получаем статистику
        stats = manager.get_connection_stats()
        
        # Проверяем результат
        assert stats["active_connections"] == 2
        assert stats["task_subscriptions"] == 2
        assert stats["total_subscribers"] == 3  # user1 в двух подписках + user2 в одной
        assert "user1" in stats["connected_users"]
        assert "user2" in stats["connected_users"]


class TestWebSocketMessage:
    """Тесты для WebSocketMessage"""
    
    def test_websocket_message_creation(self):
        """Тест создания WebSocket сообщения"""
        message = WebSocketMessage(
            type="test_message",
            data={"content": "Hello"},
            timestamp="2023-01-01T00:00:00Z",
            user_id="user123",
            task_id="task456"
        )
        
        assert message.type == "test_message"
        assert message.data["content"] == "Hello"
        assert message.timestamp == "2023-01-01T00:00:00Z"
        assert message.user_id == "user123"
        assert message.task_id == "task456"


class TestNotificationType:
    """Тесты для NotificationType enum"""
    
    def test_notification_types(self):
        """Тест типов уведомлений"""
        assert NotificationType.ANALYSIS_STARTED.value == "analysis_started"
        assert NotificationType.ANALYSIS_PROGRESS.value == "analysis_progress"
        assert NotificationType.ANALYSIS_COMPLETED.value == "analysis_completed"
        assert NotificationType.ANALYSIS_FAILED.value == "analysis_failed"
        assert NotificationType.TASK_UPDATE.value == "task_update"
        assert NotificationType.SYSTEM_ALERT.value == "system_alert"
        assert NotificationType.USER_MESSAGE.value == "user_message"


# Интеграционные тесты
class TestWebSocketServiceIntegration:
    """Интеграционные тесты для WebSocket сервиса"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_redis_integration(self):
        """Тест интеграции с Redis"""
        # Этот тест требует запущенного Redis
        pytest.skip("Requires running Redis instance")
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_websocket_flow(self):
        """Тест полного потока WebSocket взаимодействия"""
        # Этот тест требует запущенного WebSocket сервера
        pytest.skip("Requires running WebSocket server")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
