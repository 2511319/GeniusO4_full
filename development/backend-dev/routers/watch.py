# backend/routers/watch.py

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.config.config import logger, db
from backend.auth.dependencies import require_any_role, get_uid
from google.cloud import firestore


router = APIRouter(
    prefix='/watch',
    tags=['watchlist'],
    dependencies=[Depends(require_any_role('premium', 'vip', 'admin', 'moderator'))]
)


class SetWatchlistRequest(BaseModel):
    symbols: List[str]


class AddSymbolRequest(BaseModel):
    symbol: str


class RemoveSymbolRequest(BaseModel):
    symbol: str


@router.post('/set')
async def set_watchlist(request: SetWatchlistRequest, uid: str = Depends(get_uid)):
    """Установить весь watchlist (перезаписать)"""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="База данных недоступна")
        
        # Валидация символов
        if len(request.symbols) > 50:
            raise HTTPException(status_code=400, detail="Максимум 50 символов в watchlist")
        
        # Очищаем и нормализуем символы
        clean_symbols = []
        for symbol in request.symbols:
            clean_symbol = symbol.strip().upper()
            if clean_symbol and len(clean_symbol) <= 20:  # Ограничение длины символа
                clean_symbols.append(clean_symbol)
        
        # Удаляем дубликаты
        clean_symbols = list(set(clean_symbols))
        
        # Сохраняем в Firestore
        watchlist_ref = db.collection('watchlists').document(uid)
        watchlist_ref.set({
            'symbols': clean_symbols,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        
        logger.info(f"Watchlist обновлен для пользователя {uid}: {len(clean_symbols)} символов")
        
        return {
            'success': True,
            'symbols': clean_symbols,
            'count': len(clean_symbols)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка установки watchlist: {e}")
        raise HTTPException(status_code=500, detail="Ошибка установки watchlist")


@router.get('/get')
async def get_watchlist(uid: str = Depends(get_uid)):
    """Получить watchlist пользователя"""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="База данных недоступна")
        
        watchlist_ref = db.collection('watchlists').document(uid)
        watchlist_doc = watchlist_ref.get()
        
        if not watchlist_doc.exists:
            return {
                'symbols': [],
                'count': 0
            }
        
        watchlist_data = watchlist_doc.to_dict()
        symbols = watchlist_data.get('symbols', [])
        
        return {
            'symbols': symbols,
            'count': len(symbols),
            'updated_at': watchlist_data.get('updated_at')
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения watchlist: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения watchlist")


@router.post('/add')
async def add_symbol(request: AddSymbolRequest, uid: str = Depends(get_uid)):
    """Добавить символ в watchlist"""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="База данных недоступна")
        
        # Нормализуем символ
        clean_symbol = request.symbol.strip().upper()
        if not clean_symbol or len(clean_symbol) > 20:
            raise HTTPException(status_code=400, detail="Неверный символ")
        
        # Получаем текущий watchlist
        watchlist_ref = db.collection('watchlists').document(uid)
        watchlist_doc = watchlist_ref.get()
        
        if watchlist_doc.exists:
            current_symbols = watchlist_doc.to_dict().get('symbols', [])
        else:
            current_symbols = []
        
        # Проверяем лимит
        if len(current_symbols) >= 50:
            raise HTTPException(status_code=400, detail="Достигнут лимит в 50 символов")
        
        # Добавляем символ, если его еще нет
        if clean_symbol not in current_symbols:
            current_symbols.append(clean_symbol)
            
            watchlist_ref.set({
                'symbols': current_symbols,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            logger.info(f"Символ {clean_symbol} добавлен в watchlist пользователя {uid}")
            
            return {
                'success': True,
                'message': f'Символ {clean_symbol} добавлен',
                'symbols': current_symbols,
                'count': len(current_symbols)
            }
        else:
            return {
                'success': False,
                'message': f'Символ {clean_symbol} уже в watchlist',
                'symbols': current_symbols,
                'count': len(current_symbols)
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка добавления символа: {e}")
        raise HTTPException(status_code=500, detail="Ошибка добавления символа")


@router.post('/remove')
async def remove_symbol(request: RemoveSymbolRequest, uid: str = Depends(get_uid)):
    """Удалить символ из watchlist"""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="База данных недоступна")
        
        # Нормализуем символ
        clean_symbol = request.symbol.strip().upper()
        
        # Получаем текущий watchlist
        watchlist_ref = db.collection('watchlists').document(uid)
        watchlist_doc = watchlist_ref.get()
        
        if not watchlist_doc.exists:
            raise HTTPException(status_code=404, detail="Watchlist не найден")
        
        current_symbols = watchlist_doc.to_dict().get('symbols', [])
        
        # Удаляем символ, если он есть
        if clean_symbol in current_symbols:
            current_symbols.remove(clean_symbol)
            
            watchlist_ref.set({
                'symbols': current_symbols,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            logger.info(f"Символ {clean_symbol} удален из watchlist пользователя {uid}")
            
            return {
                'success': True,
                'message': f'Символ {clean_symbol} удален',
                'symbols': current_symbols,
                'count': len(current_symbols)
            }
        else:
            return {
                'success': False,
                'message': f'Символ {clean_symbol} не найден в watchlist',
                'symbols': current_symbols,
                'count': len(current_symbols)
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка удаления символа: {e}")
        raise HTTPException(status_code=500, detail="Ошибка удаления символа")


@router.delete('/clear')
async def clear_watchlist(uid: str = Depends(get_uid)):
    """Очистить весь watchlist"""
    try:
        if not db:
            raise HTTPException(status_code=500, detail="База данных недоступна")
        
        watchlist_ref = db.collection('watchlists').document(uid)
        watchlist_ref.set({
            'symbols': [],
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        
        logger.info(f"Watchlist очищен для пользователя {uid}")
        
        return {
            'success': True,
            'message': 'Watchlist очищен',
            'symbols': [],
            'count': 0
        }
        
    except Exception as e:
        logger.error(f"Ошибка очистки watchlist: {e}")
        raise HTTPException(status_code=500, detail="Ошибка очистки watchlist")
