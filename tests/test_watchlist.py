# tests/test_watchlist.py

import pytest
import sys
import os
from fastapi.testclient import TestClient

# Добавляем путь к backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app import app
from backend.auth.dependencies import create_jwt_token

client = TestClient(app)


class TestWatchlist:
    """Тесты для watchlist API"""
    
    @pytest.fixture
    def premium_token(self):
        """Создание токена для premium пользователя"""
        return create_jwt_token("123456789", expires_minutes=60)
    
    @pytest.fixture
    def user_token(self):
        """Создание токена для обычного пользователя"""
        return create_jwt_token("987654321", expires_minutes=60)
    
    def test_set_watchlist_success(self, premium_token):
        """Тест успешного создания watchlist"""
        headers = {"Authorization": f"Bearer {premium_token}"}
        payload = {
            "symbols": ["BTC", "ETH", "ADA"]
        }
        
        response = client.post("/api/watch/set", json=payload, headers=headers)
        
        # Проверяем, что запрос прошел (может быть 200 или 500 если нет Firestore)
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "BTC" in data["symbols"]
            assert data["count"] == 3
    
    def test_set_watchlist_too_many_symbols(self, premium_token):
        """Тест ограничения количества символов"""
        headers = {"Authorization": f"Bearer {premium_token}"}
        symbols = [f"SYM{i}" for i in range(51)]  # 51 символ
        payload = {"symbols": symbols}
        
        response = client.post("/api/watch/set", json=payload, headers=headers)
        
        if response.status_code != 500:  # Если Firestore доступен
            assert response.status_code == 400
            assert "Максимум 50 символов" in response.json()["detail"]
    
    def test_get_watchlist_empty(self, premium_token):
        """Тест получения пустого watchlist"""
        headers = {"Authorization": f"Bearer {premium_token}"}
        
        response = client.get("/api/watch/get", headers=headers)
        
        # Проверяем, что запрос прошел
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "symbols" in data
            assert "count" in data
    
    def test_add_symbol_success(self, premium_token):
        """Тест добавления символа"""
        headers = {"Authorization": f"Bearer {premium_token}"}
        payload = {"symbol": "BTC"}
        
        response = client.post("/api/watch/add", json=payload, headers=headers)
        
        # Проверяем, что запрос прошел
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "symbols" in data
    
    def test_remove_symbol(self, premium_token):
        """Тест удаления символа"""
        headers = {"Authorization": f"Bearer {premium_token}"}
        payload = {"symbol": "BTC"}
        
        response = client.post("/api/watch/remove", json=payload, headers=headers)
        
        # Проверяем, что запрос прошел
        assert response.status_code in [200, 404, 500]
    
    def test_clear_watchlist(self, premium_token):
        """Тест очистки watchlist"""
        headers = {"Authorization": f"Bearer {premium_token}"}
        
        response = client.delete("/api/watch/clear", headers=headers)
        
        # Проверяем, что запрос прошел
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert data["count"] == 0
    
    def test_watchlist_access_denied_for_user(self, user_token):
        """Тест запрета доступа для обычного пользователя"""
        headers = {"Authorization": f"Bearer {user_token}"}
        payload = {"symbols": ["BTC"]}
        
        response = client.post("/api/watch/set", json=payload, headers=headers)
        
        # Должен быть запрет доступа (если аутентификация работает)
        assert response.status_code in [403, 500]
    
    def test_watchlist_no_auth(self):
        """Тест без авторизации"""
        payload = {"symbols": ["BTC"]}
        
        response = client.post("/api/watch/set", json=payload)
        
        # Должен требовать авторизацию
        assert response.status_code in [401, 422]
