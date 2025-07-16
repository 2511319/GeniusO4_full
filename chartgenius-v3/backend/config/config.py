# backend/config/config.py
"""
Конфигурация приложения ChartGenius v3
"""

import os
import logging
from functools import lru_cache
from typing import List, Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    environment: str = "development"
    debug: bool = False
    api_port: int = 8000
    
    # JWT Configuration
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "o4-mini-2025-04-16"
    
    # CryptoCompare Configuration
    cryptocompare_api_key: str
    
    # Telegram Bot Configuration
    telegram_bot_token: str
    admin_telegram_id: int
    webapp_url: str = "https://chartgenius.online"
    
    # Oracle Database Configuration
    oracle_username: str = "ADMIN"
    oracle_password: str
    oracle_dsn: str
    oracle_pool_min: int = 2
    oracle_pool_max: int = 10
    oracle_pool_increment: int = 1
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_password: Optional[str] = None
    redis_ttl_ohlcv: int = 900  # 15 minutes
    
    # Payment Configuration
    telegram_payment_token: Optional[str] = None
    enable_telegram_payments: bool = True
    default_currency: str = "XTR"
    
    # Application Configuration
    default_symbol: str = "BTCUSDT"
    default_interval: str = "4h"
    default_days: int = 15
    
    # LLM Configuration
    default_llm_provider: str = "openai"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/chartgenius.log"
    
    # CORS Configuration
    allowed_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://t.me",
        "https://chartgenius.online",
        "https://*.chartgenius.online"
    ]
    
    # Cache Configuration
    enable_cache: bool = False
    cache_ttl_seconds: int = 900
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Security
    enable_https_redirect: bool = True
    enable_security_headers: bool = True
    
    @validator('allowed_origins', pre=True)
    def parse_cors_origins(cls, v):
        """Парсинг CORS origins из строки или списка"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('environment')
    def validate_environment(cls, v):
        """Валидация окружения"""
        if v not in ['development', 'production', 'testing']:
            raise ValueError('Environment must be development, production, or testing')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Получение настроек с кэшированием"""
    return Settings()


# Настройка логирования
def setup_logging():
    """Настройка системы логирования"""
    settings = get_settings()
    
    # Создаем директорию для логов
    log_dir = os.path.dirname(settings.log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Настройка форматирования
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Настройка уровня логирования
    log_level = getattr(logging, settings.log_level.upper())
    
    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Файловый обработчик
    if settings.log_file:
        file_handler = logging.FileHandler(settings.log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Настройка логгеров сторонних библиотек
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return root_logger


# Инициализация логгера
logger = setup_logging()


# Константы приложения
class Constants:
    """Константы приложения"""
    
    # Поддерживаемые интервалы
    SUPPORTED_INTERVALS = {
        "1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w"
    }
    
    # Поддерживаемые символы
    SUPPORTED_SYMBOLS = {
        "BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT",
        "LTCUSDT", "BCHUSDT", "XLMUSDT", "EOSUSDT", "TRXUSDT"
    }
    
    # Лимиты
    MIN_LIMIT = 50
    MAX_LIMIT = 1000
    DEFAULT_LIMIT = 144
    
    # Роли пользователей
    USER_ROLES = {
        "user": "Обычный пользователь",
        "premium": "Премиум пользователь", 
        "moderator": "Модератор",
        "admin": "Администратор"
    }
    
    # Планы подписки
    SUBSCRIPTION_PLANS = {
        "free": {"name": "Бесплатный", "price": 0, "analyses_per_day": 3},
        "basic": {"name": "Базовый", "price": 100, "analyses_per_day": 20},
        "premium": {"name": "Премиум", "price": 300, "analyses_per_day": 100},
        "unlimited": {"name": "Безлимитный", "price": 500, "analyses_per_day": -1}
    }
