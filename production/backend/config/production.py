# production/backend/config/production.py

import os
import logging
from typing import List
from google.cloud import secretmanager

class ProductionConfig:
    """Продакшн конфигурация для ChartGenius"""
    
    # Основные настройки
    ENVIRONMENT = "production"
    DEBUG = False
    DEBUG_LOGGING = False
    
    # Google Cloud настройки
    # Cloud Run автоматически устанавливает GOOGLE_CLOUD_PROJECT
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
    GCP_REGION = os.getenv("GCP_REGION", "europe-west1")
    
    # Сервисные настройки
    # Cloud Run резервирует PORT, используем SERVER_PORT или fallback на PORT
    API_PORT = int(os.getenv("SERVER_PORT", os.getenv("PORT", 8080)))
    API_HOST = "0.0.0.0"
    
    # CORS настройки для продакшн
    CORS_ORIGINS = [
        f"https://chartgenius-frontend-169129692197.{GCP_REGION}.run.app",
        f"https://chartgenius-frontend-{GCP_REGION}-a.run.app",
        f"https://chartgenius-frontend-{GCP_REGION}.run.app",
        "https://t.me",  # Для Telegram WebApp
        "*"  # Временно для отладки
    ]
    
    # Настройки логирования
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Настройки анализа
    DEFAULT_SYMBOL = "BTCUSDT"
    DEFAULT_QUOTE = "USD"
    
    # LLM настройки
    LLM_PROVIDER = "openai"
    OPENAI_MODEL = "gpt-4o-mini"
    
    # Telegram настройки
    ADMIN_TELEGRAM_ID = "299820674"
    
    # Firestore настройки
    FIRESTORE_DATABASE = "(default)"
    
    # Настройки производительности
    MAX_WORKERS = 4
    TIMEOUT_SECONDS = 30
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Настройки безопасности
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = 1440  # 24 часа для лучшего пользовательского опыта
    
    # Настройки кэширования
    CACHE_TTL_SECONDS = 300  # 5 минут
    
    @classmethod
    def get_secret(cls, secret_name: str) -> str:
        """Получение секрета из Google Cloud Secret Manager"""
        try:
            if not cls.GCP_PROJECT_ID:
                raise ValueError("GCP_PROJECT_ID не установлен")

            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{cls.GCP_PROJECT_ID}/secrets/{secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            # Очищаем секрет от лишних символов (включая \r, \n)
            secret_value = response.payload.data.decode("UTF-8")
            return secret_value.replace('\r', '').replace('\n', '').strip()
        except Exception as e:
            logging.error(f"Ошибка получения секрета {secret_name}: {e}")
            raise
    
    @classmethod
    def get_openai_api_key(cls) -> str:
        """Получение OpenAI API ключа"""
        return cls.get_secret("openai-api-key")
    
    @classmethod
    def get_jwt_secret_key(cls) -> str:
        """Получение JWT секретного ключа"""
        return cls.get_secret("jwt-secret-key")
    
    @classmethod
    def get_cryptocompare_api_key(cls) -> str:
        """Получение CryptoCompare API ключа"""
        return cls.get_secret("cryptocompare-api-key")
    
    @classmethod
    def get_telegram_bot_token(cls) -> str:
        """Получение Telegram Bot токена"""
        return cls.get_secret("telegram-bot-token")
    
    @classmethod
    def setup_logging(cls):
        """Настройка логирования для продакшн"""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format=cls.LOG_FORMAT,
            handlers=[
                logging.StreamHandler()  # Только в stdout для Cloud Run
            ]
        )
        
        # Отключаем debug логи от внешних библиотек
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("google").setLevel(logging.WARNING)
        
        return logging.getLogger("ChartGenius")
    
    @classmethod
    def validate_config(cls):
        """Валидация конфигурации при запуске"""
        # Проверяем наличие GCP_PROJECT_ID или GOOGLE_CLOUD_PROJECT
        if not cls.GCP_PROJECT_ID:
            raise ValueError("Отсутствует переменная окружения GCP_PROJECT_ID или GOOGLE_CLOUD_PROJECT")
        
        # Проверяем доступность секретов
        try:
            cls.get_openai_api_key()
            cls.get_jwt_secret_key()
            cls.get_cryptocompare_api_key()
        except Exception as e:
            raise ValueError(f"Ошибка доступа к секретам: {e}")
        
        logging.info("Продакшн конфигурация валидна")


# Глобальный экземпляр конфигурации
config = ProductionConfig()
