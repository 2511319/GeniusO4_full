# backend/app.py
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

# ↓ относительный импорт
from backend.routers.analysis import router as analysis_router
from backend.routers.auth import router as auth_router
from backend.routers.user import router as user_router

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import uvicorn
from dotenv import load_dotenv
from backend.db.session import create_db_and_tables

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
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# Инициализация БД при старте
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/health")
async def health():
    return {"status":"ok"}

# Подключаем роутер аутентификации (без зависимостей)
app.include_router(auth_router)

# Подключаем роутер пользователей (без JWT, используем X-Telegram-Id)
app.include_router(user_router)

# здесь подключаем анализ с аутентификацией
app.include_router(
    analysis_router,
    prefix="/api",
    dependencies=[Depends(verify_token)]
)

# Подключаем анализ для бота без аутентификации
app.include_router(
    analysis_router,
    prefix="/bot"
)

if __name__=="__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("API_PORT", 8000)),
        reload=True
    )
