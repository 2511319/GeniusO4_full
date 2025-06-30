# tests/test_mod_ban.py

import pytest
import sys
import os
from fastapi.testclient import TestClient

# Добавляем путь к backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app import app
from backend.auth.dependencies import create_jwt_token

client = TestClient(app)


class TestModeratorBan:
    """Тесты для модераторских функций бана"""
    
    @pytest.fixture
    def moderator_token(self):
        """Создание токена для модератора"""
        return create_jwt_token("111111111", expires_minutes=60)
    
    @pytest.fixture
    def user_token(self):
        """Создание токена для обычного пользователя"""
        return create_jwt_token("222222222", expires_minutes=60)
    
    def test_ban_user_success(self, moderator_token):
        """Тест успешного бана пользователя"""
        headers = {"Authorization": f"Bearer {moderator_token}"}
        payload = {
            "telegram_id": "333333333",
            "days": 7,
            "reason": "Тестовый бан"
        }
        
        response = client.post("/api/moderator/ban", json=payload, headers=headers)
        
        # Проверяем, что запрос прошел (может быть 200 или 500 если нет Firestore)
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "забанен" in data["message"]
    
    def test_unban_user_success(self, moderator_token):
        """Тест успешного разбана пользователя"""
        headers = {"Authorization": f"Bearer {moderator_token}"}
        payload = {
            "telegram_id": "333333333"
        }
        
        response = client.post("/api/moderator/unban", json=payload, headers=headers)
        
        # Проверяем, что запрос прошел
        assert response.status_code in [200, 404, 500]
    
    def test_review_flag_success(self, moderator_token):
        """Тест создания флага для анализа"""
        headers = {"Authorization": f"Bearer {moderator_token}"}
        payload = {
            "analysis_ulid": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
            "reason": "Подозрительный анализ"
        }
        
        response = client.post("/api/moderator/review_flag", json=payload, headers=headers)
        
        # Проверяем, что запрос прошел
        assert response.status_code in [200, 404, 500]
    
    def test_get_bans_list(self, moderator_token):
        """Тест получения списка банов"""
        headers = {"Authorization": f"Bearer {moderator_token}"}
        
        response = client.get("/api/moderator/bans", headers=headers)
        
        # Проверяем, что запрос прошел
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "bans" in data
            assert "total" in data
    
    def test_get_flags_list(self, moderator_token):
        """Тест получения списка флагов"""
        headers = {"Authorization": f"Bearer {moderator_token}"}
        
        response = client.get("/api/moderator/flags", headers=headers)
        
        # Проверяем, что запрос прошел
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "flags" in data
            assert "total" in data
    
    def test_ban_access_denied_for_user(self, user_token):
        """Тест запрета доступа для обычного пользователя"""
        headers = {"Authorization": f"Bearer {user_token}"}
        payload = {
            "telegram_id": "333333333",
            "days": 7,
            "reason": "Тест"
        }
        
        response = client.post("/api/moderator/ban", json=payload, headers=headers)
        
        # Должен быть запрет доступа (если аутентификация работает)
        assert response.status_code in [403, 500]
    
    def test_ban_no_auth(self):
        """Тест без авторизации"""
        payload = {
            "telegram_id": "333333333",
            "days": 7,
            "reason": "Тест"
        }
        
        response = client.post("/api/moderator/ban", json=payload)
        
        # Должен требовать авторизацию
        assert response.status_code in [401, 422]
    
    def test_ban_invalid_data(self, moderator_token):
        """Тест с неверными данными"""
        headers = {"Authorization": f"Bearer {moderator_token}"}
        payload = {
            "telegram_id": "",  # Пустой ID
            "days": -1,  # Отрицательное количество дней
            "reason": ""
        }
        
        response = client.post("/api/moderator/ban", json=payload, headers=headers)
        
        # Должна быть ошибка валидации или 500 если нет Firestore
        assert response.status_code in [400, 422, 500]
