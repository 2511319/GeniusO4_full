# production/backend/app.py

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Добавляем путь к backend модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from production.backend.config.production import config
from backend.routers.analysis import router as analysis_router
from backend.routers.admin import router as admin_router
from backend.routers.mod import router as mod_router
from backend.routers.watch import router as watch_router
from backend.auth.dependencies import create_jwt_token
from backend.middleware.telegram_webapp import TelegramWebAppAuth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    config.validate_config()
    logger = config.setup_logging()
    logger.info("ChartGenius API запущен в продакшн режиме")
    logger.info(f"Версия: {app.version}")
    logger.info(f"Регион: {config.GCP_REGION}")
    
    yield
    
    # Shutdown
    logger.info("ChartGenius API завершает работу")


# Создание приложения FastAPI
app = FastAPI(
    title="ChartGenius API",
    description="Продакшн API для анализа криптовалютных данных",
    version="1.0.0",
    docs_url=None,  # Отключаем Swagger в продакшн
    redoc_url=None,  # Отключаем ReDoc в продакшн
    lifespan=lifespan
)

# Middleware для безопасности
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        f"chartgenius-api-{config.GCP_REGION}-a.run.app",
        f"chartgenius-api-{config.GCP_REGION}.run.app",
        "localhost",  # Для локального тестирования
    ]
)

# CORS middleware с ограниченными origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Глобальный обработчик исключений"""
    logger = config.setup_logging()
    logger.error(f"Необработанная ошибка: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Внутренняя ошибка сервера",
            "message": "Произошла неожиданная ошибка. Обратитесь к администратору.",
            "request_id": getattr(request.state, 'request_id', 'unknown')
        }
    )


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Добавление ID запроса для трассировки"""
    import uuid
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health")
async def health_check():
    """Health check endpoint для Cloud Run"""
    return {
        "status": "healthy",
        "version": app.version,
        "environment": config.ENVIRONMENT,
        "region": config.GCP_REGION
    }


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "service": "ChartGenius API",
        "version": app.version,
        "status": "running",
        "environment": config.ENVIRONMENT
    }


@app.post("/api/auth/webapp-token")
async def create_webapp_token(request: Request):
    """Создание JWT токена для Telegram WebApp"""
    try:
        # Получаем init_data из тела запроса
        body = await request.body()
        init_data = body.decode('utf-8')
        
        if not init_data:
            raise HTTPException(status_code=400, detail="init_data отсутствует")
        
        auth = TelegramWebAppAuth()
        
        # Валидируем данные от Telegram WebApp
        if not auth.validate_webapp_data(init_data):
            raise HTTPException(status_code=401, detail="Неверные данные WebApp")
        
        # Извлекаем пользователя
        user_data = auth.extract_user_from_init_data(init_data)
        if not user_data:
            raise HTTPException(status_code=401, detail="Не удалось извлечь данные пользователя")
        
        telegram_id = str(user_data.get('id'))
        
        # Создаем JWT токен
        token = create_jwt_token(telegram_id, expires_minutes=config.JWT_EXPIRE_MINUTES)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": config.JWT_EXPIRE_MINUTES * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger = config.setup_logging()
        logger.error(f"Ошибка создания WebApp токена: {e}")
        raise HTTPException(status_code=500, detail="Ошибка создания токена")


# Подключение роутеров
app.include_router(analysis_router, prefix="/api", tags=["analysis"])
app.include_router(admin_router, prefix="/api", tags=["admin"])
app.include_router(mod_router, prefix="/api", tags=["moderator"])
app.include_router(watch_router, prefix="/api", tags=["watchlist"])


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=config.API_HOST,
        port=config.API_PORT,
        workers=1,  # Cloud Run использует один worker
        access_log=False,  # Отключаем access log в продакшн
        log_level="info"
    )
