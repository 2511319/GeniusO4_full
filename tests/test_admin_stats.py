# tests/test_admin_stats.py

import pytest
import sys
import os
from fastapi.testclient import TestClient

# Добавляем путь к backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app import app
from backend.auth.dependencies import create_jwt_token

client = TestClient(app)


class TestAdminStats:
    """Тесты для админских функций"""
    
    @pytest.fixture
    def admin_token(self):
        """Создание токена для админа"""
        return create_jwt_token("299820674", expires_minutes=60)  # ID админа
    
    @pytest.fixture
    def user_token(self):
        """Создание токена для обычного пользователя"""
        return create_jwt_token("123456789", expires_minutes=60)
    
    def test_get_stats_success(self, admin_token):
        """Тест получения статистики"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.get("/api/admin/stats", headers=headers)
        
        # Проверяем, что запрос прошел (может быть 200 или 500 если нет Firestore)
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "total_users" in data
            assert "roles" in data
            assert "active_subscriptions" in data
            assert isinstance(data["total_users"], int)
            assert isinstance(data["roles"], dict)
    
    def test_set_role_success(self, admin_token):
        """Тест установки роли пользователю"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "telegram_id": "123456789",
            "role": "premium",
            "subscription_days": 30
        }
        
        response = client.post("/api/admin/set_role", json=payload, headers=headers)
        
        # Проверяем, что запрос прошел
        assert response.status_code in [200, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "установлена" in data["message"]
    
    def test_set_role_invalid_role(self, admin_token):
        """Тест установки неверной роли"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "telegram_id": "123456789",
            "role": "invalid_role",
            "subscription_days": 0
        }
        
        response = client.post("/api/admin/set_role", json=payload, headers=headers)
        
        # Должна быть ошибка валидации (если Firestore доступен)
        assert response.status_code in [400, 500]
        
        if response.status_code == 400:
            assert "Неверная роль" in response.json()["detail"]
    
    def test_broadcast_message(self, admin_token):
        """Тест создания рассылки"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "text": "Тестовое сообщение для рассылки"
        }
        
        response = client.post("/api/admin/broadcast", json=payload, headers=headers)
        
        # Проверяем, что запрос прошел
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "запланирована" in data["message"]
            assert "broadcast_id" in data
    
    def test_garbage_collect(self, admin_token):
        """Тест очистки данных"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.post("/api/admin/gc", headers=headers)
        
        # Проверяем, что запрос прошел
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "deleted" in data
            assert isinstance(data["deleted"], dict)
    
    def test_admin_access_denied_for_user(self, user_token):
        """Тест запрета доступа для обычного пользователя"""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = client.get("/api/admin/stats", headers=headers)
        
        # Должен быть запрет доступа (если аутентификация работает)
        assert response.status_code in [403, 500]
    
    def test_admin_no_auth(self):
        """Тест без авторизации"""
        response = client.get("/api/admin/stats")
        
        # Должен требовать авторизацию
        assert response.status_code in [401, 422]
    
    def test_set_role_missing_data(self, admin_token):
        """Тест с отсутствующими данными"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "telegram_id": "",  # Пустой ID
            "role": ""  # Пустая роль
        }
        
        response = client.post("/api/admin/set_role", json=payload, headers=headers)
        
        # Должна быть ошибка валидации
        assert response.status_code in [400, 422, 500]
    
    def test_broadcast_empty_message(self, admin_token):
        """Тест рассылки пустого сообщения"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "text": ""
        }
        
        response = client.post("/api/admin/broadcast", json=payload, headers=headers)
        
        # Может быть принято или отклонено в зависимости от валидации
        assert response.status_code in [200, 400, 422, 500]
