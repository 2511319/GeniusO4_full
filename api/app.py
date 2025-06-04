# api/app.py
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

# ↓ относительный импорт
from routers.analysis import router as analysis_router

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import uvicorn
from dotenv import load_dotenv

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

@app.get("/health")
async def health():
    return {"status":"ok"}

# здесь подключаем анализ
app.include_router(
    analysis_router,
    prefix="/api",
    dependencies=[Depends(verify_token)]
)

if __name__=="__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("API_PORT", 8000)),
        reload=True
    )
