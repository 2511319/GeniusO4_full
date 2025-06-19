from fastapi import APIRouter, Request, Depends, HTTPException
from sqlmodel import Session
from backend.auth.telegram import verify
from backend.core.security import create_access_token
from backend.models.user import User
from backend.db.session import get_session

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/telegram")
async def auth_telegram(request: Request, db: Session = Depends(get_session)):
    """
    Аутентификация через Telegram Login Widget
    """
    try:
        payload = await request.json()
        data = verify(payload)
        
        # Получаем или создаем пользователя
        user = db.get(User, data["id"])
        if not user:
            user = User(
                id=int(data["id"]),
                username=data.get("username"),
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                photo_url=data.get("photo_url")
            )
            db.add(user)
        else:
            # Обновляем данные пользователя
            user.username = data.get("username")
            user.first_name = data.get("first_name")
            user.last_name = data.get("last_name")
            user.photo_url = data.get("photo_url")
            
        db.commit()
        db.refresh(user)
        
        # Создаем JWT токен
        token = create_access_token(user.id)
        
        return {"access_token": token, "token_type": "bearer"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
