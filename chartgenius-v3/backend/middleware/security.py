# backend/middleware/security.py
"""
Security middleware для защиты API
"""

import time
from typing import Set
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from config.config import get_settings, logger

settings = get_settings()


class SecurityMiddleware(BaseHTTPMiddleware):
    """Основной security middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.blocked_ips: Set[str] = set()
        self.suspicious_patterns = [
            "script", "javascript:", "vbscript:", "onload", "onerror",
            "eval(", "alert(", "document.cookie", "window.location",
            "../", "..\\", "/etc/passwd", "/proc/", "cmd.exe",
            "powershell", "bash", "sh", "curl", "wget"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Основная обработка security проверок"""
        
        # Получаем IP клиента
        client_ip = self._get_client_ip(request)
        
        # Проверяем заблокированные IP
        if client_ip in self.blocked_ips:
            logger.warning(f"🚫 Заблокированный IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Проверяем подозрительные паттерны в URL
        if self._check_suspicious_url(request.url.path):
            logger.warning(f"⚠️ Подозрительный URL от {client_ip}: {request.url.path}")
            self._block_ip(client_ip)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request"
            )
        
        # Проверяем заголовки
        if not self._validate_headers(request):
            logger.warning(f"⚠️ Подозрительные заголовки от {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid headers"
            )
        
        # Выполняем запрос
        response = await call_next(request)
        
        # Добавляем security заголовки
        self._add_security_headers(response)
        
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
        
        return request.client.host if request.client else "unknown"
    
    def _check_suspicious_url(self, path: str) -> bool:
        """Проверка URL на подозрительные паттерны"""
        path_lower = path.lower()
        
        for pattern in self.suspicious_patterns:
            if pattern in path_lower:
                return True
        
        # Проверка на path traversal
        if "../" in path or "..\\" in path:
            return True
        
        # Проверка на SQL injection паттерны
        sql_patterns = ["union select", "drop table", "insert into", "delete from"]
        for pattern in sql_patterns:
            if pattern in path_lower:
                return True
        
        return False
    
    def _validate_headers(self, request: Request) -> bool:
        """Валидация заголовков запроса"""
        
        # Проверяем User-Agent
        user_agent = request.headers.get("User-Agent", "")
        if not user_agent or len(user_agent) > 500:
            return False
        
        # Проверяем подозрительные User-Agent
        suspicious_agents = [
            "sqlmap", "nikto", "nmap", "masscan", "zap",
            "burp", "w3af", "acunetix", "nessus"
        ]
        
        user_agent_lower = user_agent.lower()
        for agent in suspicious_agents:
            if agent in user_agent_lower:
                return False
        
        # Проверяем Content-Length
        content_length = request.headers.get("Content-Length")
        if content_length:
            try:
                length = int(content_length)
                if length > 10 * 1024 * 1024:  # 10MB лимит
                    return False
            except ValueError:
                return False
        
        return True
    
    def _block_ip(self, ip: str):
        """Блокировка IP адреса"""
        self.blocked_ips.add(ip)
        logger.warning(f"🚫 IP {ip} заблокирован")
    
    def _add_security_headers(self, response):
        """Добавление security заголовков"""
        if settings.enable_security_headers:
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
            
            if settings.environment == "production":
                response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """CSRF защита для state-changing операций"""
    
    def __init__(self, app):
        super().__init__(app)
        self.protected_methods = {"POST", "PUT", "DELETE", "PATCH"}
        self.exempt_paths = {
            "/api/webhooks/telegram",
            "/api/webhooks/telegram-payment",
            "/docs",
            "/redoc",
            "/openapi.json"
        }
    
    async def dispatch(self, request: Request, call_next):
        """CSRF проверка"""
        
        # Проверяем только защищенные методы
        if request.method in self.protected_methods:
            
            # Исключаем определенные пути
            if request.url.path not in self.exempt_paths:
                
                # Проверяем Origin или Referer
                if not self._validate_origin(request):
                    logger.warning(f"⚠️ CSRF попытка: {request.url.path}")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="CSRF validation failed"
                    )
        
        return await call_next(request)
    
    def _validate_origin(self, request: Request) -> bool:
        """Валидация Origin/Referer"""
        
        # Для Telegram WebApp разрешаем t.me
        origin = request.headers.get("Origin")
        referer = request.headers.get("Referer")
        
        allowed_origins = [
            "https://t.me",
            "https://web.telegram.org",
            "https://chartgenius.online",
            "http://localhost:5173",  # Для разработки
            "http://localhost:3000"   # Для разработки
        ]
        
        if origin:
            for allowed in allowed_origins:
                if origin.startswith(allowed):
                    return True
        
        if referer:
            for allowed in allowed_origins:
                if referer.startswith(allowed):
                    return True
        
        # Для API запросов без Origin/Referer требуем специальный заголовок
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return True
        
        return False


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Валидация входных данных"""
    
    def __init__(self, app):
        super().__init__(app)
        self.max_json_size = 1024 * 1024  # 1MB
    
    async def dispatch(self, request: Request, call_next):
        """Валидация входных данных"""
        
        # Проверяем размер JSON payload
        if request.headers.get("Content-Type", "").startswith("application/json"):
            content_length = request.headers.get("Content-Length")
            
            if content_length:
                try:
                    size = int(content_length)
                    if size > self.max_json_size:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail="JSON payload too large"
                        )
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid Content-Length"
                    )
        
        return await call_next(request)


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """Перенаправление HTTP на HTTPS"""
    
    def __init__(self, app):
        super().__init__(app)
        self.enable_redirect = settings.enable_https_redirect and settings.environment == "production"
    
    async def dispatch(self, request: Request, call_next):
        """HTTPS перенаправление"""
        
        if self.enable_redirect:
            # Проверяем схему
            if request.url.scheme == "http":
                # Создаем HTTPS URL
                https_url = request.url.replace(scheme="https")
                
                from fastapi.responses import RedirectResponse
                return RedirectResponse(url=str(https_url), status_code=301)
        
        return await call_next(request)
