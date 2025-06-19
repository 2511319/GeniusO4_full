import os
from datetime import datetime, timedelta
from jose import jwt

ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ACCESS_TTL_MIN = 60 * 24 * 7  # 7 дней

def create_access_token(sub: str | int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TTL_MIN)
    return jwt.encode({"sub": str(sub), "exp": expire}, JWT_SECRET_KEY, algorithm=ALGORITHM)
