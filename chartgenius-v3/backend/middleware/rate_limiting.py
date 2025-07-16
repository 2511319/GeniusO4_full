# backend/middleware/rate_limiting.py
"""
Middleware для ограничения частоты запросов (Rate Limiting)
"""

import time
from typing import Dict, Any
from collections import defaultdict, deque

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from config.config import get_settings, logger

settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware для ограничения частоты запросов"""
    
    def __init__(self, app):
        super().__init__(app)
        # Хранилище запросов по IP
        self.requests: Dict[str, deque] = defaultdict(lambda: deque())
        # Хранилище для блокированных IP
        self.blocked_ips: Dict[str, float] = {}
        
        # Настройки rate limiting
        self.max_requests = settings.rate_limit_requests
        self.window_seconds = settings.rate_limit_window
        self.block_duration = 300  # 5 минут блокировки
    
    async def dispatch(self, request: Request, call_next):
        """Обработка запроса с проверкой rate limit"""
        
        # Получаем IP адрес клиента
        client_ip = self._get_client_ip(request)
        
        # Проверяем, не заблокирован ли IP
        if self._is_blocked(client_ip):
            logger.warning(f"🚫 Заблокированный IP пытается сделать запрос: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="IP адрес временно заблокирован из-за превышения лимита запросов"
            )
        
        # Проверяем rate limit
        if not self._check_rate_limit(client_ip, request):
            # Блокируем IP при превышении лимита
            self._block_ip(client_ip)
            
            logger.warning(f"⚠️ Rate limit превышен для IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Превышен лимит запросов: {self.max_requests} запросов за {self.window_seconds} секунд"
            )
        
        # Выполняем запрос
        response = await call_next(request)
        
        # Добавляем заголовки с информацией о rate limit
        remaining_requests = self._get_remaining_requests(client_ip)
        reset_time = self._get_reset_time(client_ip)
        
        response.headers["X-Rate-Limit-Limit"] = str(self.max_requests)
        response.headers["X-Rate-Limit-Remaining"] = str(remaining_requests)
        response.headers["X-Rate-Limit-Reset"] = str(reset_time)
        response.headers["X-Rate-Limit-Window"] = str(self.window_seconds)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Получение IP адреса клиента"""
        # Проверяем заголовки прокси
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback на IP из соединения
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str, request: Request) -> bool:
        """Проверка rate limit для IP"""
        current_time = time.time()
        
        # Получаем очередь запросов для IP
        ip_requests = self.requests[client_ip]
        
        # Удаляем старые запросы (вне окна)
        while ip_requests and ip_requests[0] < current_time - self.window_seconds:
            ip_requests.popleft()
        
        # Проверяем количество запросов
        if len(ip_requests) >= self.max_requests:
            return False
        
        # Добавляем текущий запрос
        ip_requests.append(current_time)
        
        return True
    
    def _is_blocked(self, client_ip: str) -> bool:
        """Проверка, заблокирован ли IP"""
        if client_ip not in self.blocked_ips:
            return False
        
        # Проверяем, истекло ли время блокировки
        block_time = self.blocked_ips[client_ip]
        if time.time() - block_time > self.block_duration:
            # Разблокируем IP
            del self.blocked_ips[client_ip]
            # Очищаем историю запросов
            if client_ip in self.requests:
                del self.requests[client_ip]
            return False
        
        return True
    
    def _block_ip(self, client_ip: str):
        """Блокировка IP адреса"""
        self.blocked_ips[client_ip] = time.time()
        logger.warning(f"🚫 IP {client_ip} заблокирован на {self.block_duration} секунд")
    
    def _get_remaining_requests(self, client_ip: str) -> int:
        """Получение количества оставшихся запросов"""
        if client_ip not in self.requests:
            return self.max_requests
        
        current_requests = len(self.requests[client_ip])
        return max(0, self.max_requests - current_requests)
    
    def _get_reset_time(self, client_ip: str) -> int:
        """Получение времени сброса счетчика"""
        if client_ip not in self.requests or not self.requests[client_ip]:
            return int(time.time() + self.window_seconds)
        
        # Время сброса = время первого запроса + окно
        first_request_time = self.requests[client_ip][0]
        return int(first_request_time + self.window_seconds)


class APIKeyRateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware для rate limiting по API ключу"""
    
    def __init__(self, app):
        super().__init__(app)
        self.api_requests: Dict[str, deque] = defaultdict(lambda: deque())
        
        # Более высокие лимиты для API ключей
        self.max_requests = 1000
        self.window_seconds = 3600  # 1 час
    
    async def dispatch(self, request: Request, call_next):
        """Обработка запроса с проверкой API key rate limit"""
        
        # Проверяем наличие API ключа
        api_key = request.headers.get("X-API-Key")
        
        if api_key:
            if not self._check_api_rate_limit(api_key):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Превышен лимит API: {self.max_requests} запросов в час"
                )
        
        response = await call_next(request)
        
        # Добавляем заголовки для API ключей
        if api_key:
            remaining = self._get_api_remaining_requests(api_key)
            response.headers["X-API-Rate-Limit-Remaining"] = str(remaining)
        
        return response
    
    def _check_api_rate_limit(self, api_key: str) -> bool:
        """Проверка rate limit для API ключа"""
        current_time = time.time()
        
        # Получаем очередь запросов для API ключа
        api_requests = self.api_requests[api_key]
        
        # Удаляем старые запросы
        while api_requests and api_requests[0] < current_time - self.window_seconds:
            api_requests.popleft()
        
        # Проверяем лимит
        if len(api_requests) >= self.max_requests:
            return False
        
        # Добавляем запрос
        api_requests.append(current_time)
        return True
    
    def _get_api_remaining_requests(self, api_key: str) -> int:
        """Получение оставшихся запросов для API ключа"""
        if api_key not in self.api_requests:
            return self.max_requests
        
        current_requests = len(self.api_requests[api_key])
        return max(0, self.max_requests - current_requests)
