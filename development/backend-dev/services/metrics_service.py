# 📊 Metrics Service for ChartGenius
# Версия: 1.1.0-dev
# Prometheus metrics collection with Redis integration

import os
import time
import asyncio
import json
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import CollectorRegistry
import psutil
import logging
from datetime import datetime, timedelta
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class ChartGeniusMetrics:
    """Централизованный сбор метрик для ChartGenius"""

    def __init__(self):
        # Создаем отдельный registry для изоляции
        self.registry = CollectorRegistry()
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        # === API METRICS ===
        self.api_requests_total = Counter(
            'chartgenius_api_requests_total',
            'Total API requests',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )
        
        self.api_request_duration = Histogram(
            'chartgenius_api_request_duration_seconds',
            'API request duration',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # === LLM METRICS ===
        self.llm_requests_total = Counter(
            'chartgenius_llm_requests_total',
            'Total LLM requests',
            ['provider', 'model', 'status'],
            registry=self.registry
        )
        
        self.llm_request_duration = Histogram(
            'chartgenius_llm_request_duration_seconds',
            'LLM request duration',
            ['provider', 'model'],
            registry=self.registry
        )
        
        self.llm_tokens_used = Counter(
            'chartgenius_llm_tokens_total',
            'Total LLM tokens used',
            ['provider', 'model', 'type'],  # type: prompt, completion
            registry=self.registry
        )
        
        self.llm_cost_estimate = Counter(
            'chartgenius_llm_cost_usd_total',
            'Estimated LLM costs in USD',
            ['provider', 'model'],
            registry=self.registry
        )
        
        # === USER METRICS ===
        self.active_users = Gauge(
            'chartgenius_active_users',
            'Currently active users',
            registry=self.registry
        )
        
        self.user_actions_total = Counter(
            'chartgenius_user_actions_total',
            'Total user actions',
            ['action_type', 'user_role'],
            registry=self.registry
        )
        
        # === SYSTEM METRICS ===
        self.system_info = Info(
            'chartgenius_system_info',
            'System information',
            registry=self.registry
        )
        
        self.cache_hits_total = Counter(
            'chartgenius_cache_hits_total',
            'Cache hits',
            ['cache_type'],
            registry=self.registry
        )
        
        self.cache_misses_total = Counter(
            'chartgenius_cache_misses_total',
            'Cache misses',
            ['cache_type'],
            registry=self.registry
        )
        
        # === ERROR METRICS ===
        self.errors_total = Counter(
            'chartgenius_errors_total',
            'Total errors',
            ['error_type', 'component'],
            registry=self.registry
        )
        
        # Инициализируем system info
        self._update_system_info()
        
        logger.info("ChartGenius metrics initialized")

    async def get_redis(self) -> redis.Redis:
        """Получение Redis клиента"""
        return redis.from_url(self.redis_url)

    def _update_system_info(self):
        """Обновляет системную информацию"""
        try:
            self.system_info.info({
                'version': '1.1.0-dev',
                'python_version': f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}",
                'environment': 'development'
            })
        except Exception as e:
            logger.error(f"Error updating system info: {e}")
    
    # === API TRACKING ===
    def track_api_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Отслеживание API запросов"""
        self.api_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        self.api_request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    # === LLM TRACKING ===
    def track_llm_request(self, provider: str, model: str, status: str, 
                         duration: float, tokens_used: Dict[str, int] = None,
                         cost_estimate: float = 0.0):
        """Отслеживание LLM запросов"""
        self.llm_requests_total.labels(
            provider=provider,
            model=model,
            status=status
        ).inc()
        
        self.llm_request_duration.labels(
            provider=provider,
            model=model
        ).observe(duration)
        
        if tokens_used:
            for token_type, count in tokens_used.items():
                self.llm_tokens_used.labels(
                    provider=provider,
                    model=model,
                    type=token_type
                ).inc(count)
        
        if cost_estimate > 0:
            self.llm_cost_estimate.labels(
                provider=provider,
                model=model
            ).inc(cost_estimate)
    
    # === USER TRACKING ===
    def track_user_action(self, action_type: str, user_role: str = 'user'):
        """Отслеживание действий пользователей"""
        self.user_actions_total.labels(
            action_type=action_type,
            user_role=user_role
        ).inc()
    
    def update_active_users(self, count: int):
        """Обновление количества активных пользователей"""
        self.active_users.set(count)
    
    # === CACHE TRACKING ===
    def track_cache_hit(self, cache_type: str):
        """Отслеживание попаданий в кэш"""
        self.cache_hits_total.labels(cache_type=cache_type).inc()
    
    def track_cache_miss(self, cache_type: str):
        """Отслеживание промахов кэша"""
        self.cache_misses_total.labels(cache_type=cache_type).inc()
    
    # === ERROR TRACKING ===
    def track_error(self, error_type: str, component: str):
        """Отслеживание ошибок"""
        self.errors_total.labels(
            error_type=error_type,
            component=component
        ).inc()
    
    def get_metrics(self) -> str:
        """Получение метрик в формате Prometheus"""
        return generate_latest(self.registry)

    async def update_active_users_from_redis(self):
        """Обновление количества активных пользователей из Redis"""
        try:
            redis_client = await self.get_redis()

            # Активные пользователи за последние 5 минут
            five_min_ago = datetime.utcnow() - timedelta(minutes=5)
            active_5m_key = f"active_users:5m:{five_min_ago.strftime('%Y%m%d%H%M')}"
            active_5m = await redis_client.scard(active_5m_key) or 0

            self.active_users.set(active_5m)
            logger.debug(f"Active users updated from Redis: {active_5m}")

        except Exception as e:
            logger.error(f"Ошибка обновления активных пользователей из Redis: {e}")

    async def track_user_activity(self, user_id: str):
        """Отслеживание активности пользователя в Redis"""
        try:
            redis_client = await self.get_redis()
            now = datetime.utcnow()

            # Добавляем в набор активных пользователей
            await redis_client.sadd(f"active_users:5m:{now.strftime('%Y%m%d%H%M')}", user_id)

            # Устанавливаем TTL
            await redis_client.expire(f"active_users:5m:{now.strftime('%Y%m%d%H%M')}", 300)

        except Exception as e:
            logger.error(f"Ошибка отслеживания активности пользователя: {e}")

    async def get_system_health(self) -> Dict[str, Any]:
        """Получение общего состояния системы"""
        try:
            redis_client = await self.get_redis()

            # Проверяем Redis
            redis_healthy = True
            try:
                await redis_client.ping()
            except:
                redis_healthy = False

            # Собираем основные метрики
            health_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "services": {
                    "redis": "healthy" if redis_healthy else "unhealthy",
                    "metrics": "healthy"
                },
                "version": "1.1.0-dev",
                "environment": "development"
            }

            return health_data

        except Exception as e:
            logger.error(f"Ошибка получения состояния системы: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }

# Глобальный экземпляр метрик
metrics = ChartGeniusMetrics()

# === DECORATORS ===
def track_api_metrics(endpoint: str):
    """Декоратор для отслеживания API метрик"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = 200
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = getattr(e, 'status_code', 500)
                metrics.track_error(type(e).__name__, 'api')
                raise
            finally:
                duration = time.time() - start_time
                # Извлекаем метод из request если доступен
                method = getattr(args[0] if args else None, 'method', 'GET')
                metrics.track_api_request(method, endpoint, status_code, duration)
        
        return wrapper
    return decorator

def track_llm_metrics(provider: str, model: str):
    """Декоратор для отслеживания LLM метрик"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 'success'
            
            try:
                result = await func(*args, **kwargs)
                
                # Извлекаем информацию об использовании токенов
                tokens_used = {}
                cost_estimate = 0.0
                
                if hasattr(result, 'usage') and result.usage:
                    tokens_used = {
                        'prompt': result.usage.get('prompt_tokens', 0),
                        'completion': result.usage.get('completion_tokens', 0)
                    }
                    # Простая оценка стоимости (можно улучшить)
                    total_tokens = result.usage.get('total_tokens', 0)
                    cost_estimate = total_tokens * 0.00002  # Примерная стоимость
                
                return result
            except Exception as e:
                status = 'error'
                metrics.track_error(type(e).__name__, 'llm')
                raise
            finally:
                duration = time.time() - start_time
                metrics.track_llm_request(provider, model, status, duration, 
                                        tokens_used, cost_estimate)
        
        return wrapper
    return decorator
