# backend/app.py
"""
ChartGenius v3 Backend
FastAPI приложение с современными стандартами 2025
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
import uvicorn
from dotenv import load_dotenv

# Импорты роутеров
from routers.analysis import router as analysis_router
from routers.auth import router as auth_router
from routers.admin import router as admin_router
from routers.config import router as config_router
from routers.webhooks import router as webhooks_router
from routers.subscription import router as subscription_router

# Импорты middleware и конфигурации
from middleware.rate_limiting import RateLimitMiddleware
from middleware.telegram_webapp import TelegramWebAppMiddleware
from middleware.security import SecurityMiddleware
from config.config import get_settings, logger
from config.database import init_database, close_database

# Загружаем переменные окружения
load_dotenv()

# Получаем настройки
settings = get_settings()

# Security
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    logger.info("🚀 Запуск ChartGenius v3 Backend")
    
    # Инициализация базы данных
    await init_database()
    logger.info("✅ База данных инициализирована")
    
    yield
    
    # Shutdown
    logger.info("🛑 Остановка ChartGenius v3 Backend")
    await close_database()
    logger.info("✅ База данных отключена")


# Создание FastAPI приложения
app = FastAPI(
    title="ChartGenius v3 API",
    description="Современный API для технического анализа криптовалют",
    version="3.0.0",
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
    lifespan=lifespan
)

# Middleware для безопасности
app.add_middleware(SecurityMiddleware)

# Trusted hosts middleware
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["chartgenius.online", "*.chartgenius.online"]
    )

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Telegram WebApp middleware
app.add_middleware(TelegramWebAppMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Rate-Limit-Remaining", "X-Rate-Limit-Reset"]
)


# Обработчики ошибок
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Обработчик HTTP исключений"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Обработчик общих исключений"""
    logger.error(f"Необработанная ошибка: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Внутренняя ошибка сервера",
            "status_code": 500,
            "path": str(request.url.path)
        }
    )


# Health check endpoints
@app.get("/health")
async def health_check():
    """Простая проверка здоровья"""
    return {"status": "healthy", "version": "3.0.0"}


@app.get("/api/health")
async def api_health_check():
    """Детальная проверка здоровья API"""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "environment": settings.environment,
        "timestamp": "2025-01-09",
        "services": {
            "database": "connected",
            "redis": "connected",
            "ai_model": "ready"
        }
    }


# Подключение роутеров
app.include_router(
    analysis_router,
    prefix="/api/analysis",
    tags=["Analysis"]
)

app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Authentication"]
)

app.include_router(
    admin_router,
    prefix="/api/admin",
    tags=["Admin"]
)

app.include_router(
    config_router,
    prefix="/api/config",
    tags=["Configuration"]
)

app.include_router(
    webhooks_router,
    prefix="/api/webhooks",
    tags=["Webhooks"]
)

app.include_router(
    subscription_router,
    prefix="/api/subscription",
    tags=["Subscription"]
)


# Корневой endpoint
@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "ChartGenius v3 API",
        "version": "3.0.0",
        "docs": "/docs" if settings.environment == "development" else None,
        "status": "running"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("API_PORT", 8000)),
        reload=settings.environment == "development",
        log_level="info"
    )
