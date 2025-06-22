# backend/app.py
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

# ↓ абсолютный импорт
from backend.routers.analysis import router as analysis_router
from backend.routers.admin import router as admin_router
from backend.routers.mod import router as mod_router
from backend.routers.watch import router as watch_router

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import uvicorn
from dotenv import load_dotenv
from backend.config.config import logger

load_dotenv()  # подхватит .env.dev

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
security = HTTPBearer()

def verify_token(creds: HTTPAuthorizationCredentials = Depends(security)):
    try:
        return jwt.decode(creds.credentials, SECRET_KEY, algorithms=["HS256"])
    except:
        raise HTTPException(401, "Invalid token")

app = FastAPI(title="GeniusO4 API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Development frontend
        "http://localhost:3000",  # Alternative dev port
        "https://t.me",           # Telegram WebApp
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status":"ok"}

@app.get("/api/test")
async def test_api():
    return {"message": "API работает!", "timestamp": "2025-06-20"}


@app.post("/api/auth/webapp-token")
async def create_webapp_token(init_data: str):
    """Создание JWT токена для WebApp (10 минут)"""
    try:
        from backend.middleware.telegram_webapp import TelegramWebAppAuth

        auth = TelegramWebAppAuth()

        # Валидируем данные от Telegram WebApp
        if not auth.validate_webapp_data(init_data):
            raise HTTPException(status_code=401, detail="Неверные данные WebApp")

        # Извлекаем пользователя
        user_data = auth.extract_user_from_init_data(init_data)
        if not user_data:
            raise HTTPException(status_code=401, detail="Не удалось извлечь данные пользователя")

        telegram_id = str(user_data.get('id'))

        # Создаем JWT токен на 10 минут
        from backend.auth.dependencies import create_jwt_token
        token = create_jwt_token(telegram_id, expires_minutes=10)

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 600  # 10 минут в секундах
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка создания WebApp токена: {e}")
        raise HTTPException(status_code=500, detail="Ошибка создания токена")

# здесь подключаем анализ БЕЗ аутентификации для тестирования
app.include_router(
    analysis_router,
    prefix="/api"
    # dependencies=[Depends(verify_token)]  # Временно отключено
)

# Подключаем новые роутеры с аутентификацией
app.include_router(admin_router, prefix="/api")
app.include_router(mod_router, prefix="/api")
app.include_router(watch_router, prefix="/api")

if __name__=="__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("API_PORT", 8000)),
        reload=True
    )
