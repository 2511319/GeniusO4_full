import pytest
import time
import hashlib
import hmac
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.auth.telegram import verify, _calc_hash
from backend.core.security import create_access_token
from backend.app import app

client = TestClient(app)

class TestTelegramAuth:
    """Тесты для Telegram аутентификации"""
    
    def setup_method(self):
        """Настройка для каждого теста"""
        self.bot_token = "test_bot_token"
        self.secret_key = hashlib.sha256(self.bot_token.encode()).digest()
        
    def create_valid_payload(self, user_id="123456789"):
        """Создает валидный payload для тестирования"""
        auth_date = str(int(time.time()))
        payload = {
            "id": user_id,
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser",
            "auth_date": auth_date
        }
        
        # Вычисляем hash
        data_check = "\n".join(f"{k}={payload[k]}" for k in sorted(payload.keys()))
        payload["hash"] = hmac.new(self.secret_key, data_check.encode(), hashlib.sha256).hexdigest()
        
        return payload
    
    @patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_bot_token'})
    def test_valid_telegram_auth(self):
        """Тест успешной аутентификации через Telegram"""
        payload = self.create_valid_payload()
        
        # Проверяем, что verify не выбрасывает исключение
        result = verify(payload)
        assert result["id"] == "123456789"
        assert result["username"] == "testuser"
    
    @patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_bot_token'})
    def test_missing_hash(self):
        """Тест с отсутствующим hash"""
        payload = self.create_valid_payload()
        del payload["hash"]
        
        with pytest.raises(Exception) as exc_info:
            verify(payload)
        assert "hash missing" in str(exc_info.value)
    
    @patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_bot_token'})
    def test_invalid_hash(self):
        """Тест с неверным hash"""
        payload = self.create_valid_payload()
        payload["hash"] = "invalid_hash"
        
        with pytest.raises(Exception) as exc_info:
            verify(payload)
        assert "invalid hash" in str(exc_info.value)
    
    @patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_bot_token'})
    def test_expired_auth(self):
        """Тест с истекшим временем аутентификации"""
        payload = self.create_valid_payload()
        # Устанавливаем время в прошлом (более 5 минут назад)
        old_time = str(int(time.time()) - 400)  # 400 секунд назад
        payload["auth_date"] = old_time
        
        # Пересчитываем hash с новым auth_date
        data_check = "\n".join(f"{k}={payload[k]}" for k in sorted(payload.keys()) if k != "hash")
        payload["hash"] = hmac.new(self.secret_key, data_check.encode(), hashlib.sha256).hexdigest()
        
        with pytest.raises(Exception) as exc_info:
            verify(payload)
        assert "login expired" in str(exc_info.value)

class TestJWTSecurity:
    """Тесты для JWT токенов"""
    
    @patch.dict('os.environ', {'JWT_SECRET_KEY': 'test_secret_key'})
    def test_create_access_token(self):
        """Тест создания JWT токена"""
        user_id = "123456789"
        token = create_access_token(user_id)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Проверяем, что токен можно декодировать
        from jose import jwt
        decoded = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        assert decoded["sub"] == user_id

class TestAuthEndpoint:
    """Тесты для эндпоинта аутентификации"""
    
    @patch.dict('os.environ', {
        'TELEGRAM_BOT_TOKEN': 'test_bot_token',
        'JWT_SECRET_KEY': 'test_secret_key'
    })
    def test_telegram_auth_endpoint(self):
        """Тест эндпоинта /auth/telegram"""
        # Создаем валидный payload
        bot_token = "test_bot_token"
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        auth_date = str(int(time.time()))
        
        payload = {
            "id": "123456789",
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser",
            "auth_date": auth_date
        }
        
        data_check = "\n".join(f"{k}={payload[k]}" for k in sorted(payload.keys()))
        payload["hash"] = hmac.new(secret_key, data_check.encode(), hashlib.sha256).hexdigest()
        
        # Отправляем запрос
        response = client.post("/auth/telegram", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
