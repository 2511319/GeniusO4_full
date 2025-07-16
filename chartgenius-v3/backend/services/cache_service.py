# backend/services/cache_service.py
"""
Сервис кэширования для оптимизации производительности
"""

import json
import asyncio
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from config.config import get_settings, logger

settings = get_settings()


class CacheService:
    """Сервис кэширования с поддержкой Redis и in-memory fallback"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_enabled = settings.enable_cache
        self.default_ttl = settings.cache_ttl_seconds
        
        # Инициализация Redis если доступен
        if REDIS_AVAILABLE and self.cache_enabled:
            asyncio.create_task(self._init_redis())
    
    async def _init_redis(self):
        """Инициализация Redis подключения"""
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                password=settings.redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Тестируем подключение
            await self.redis_client.ping()
            logger.info("✅ Redis подключен успешно")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis недоступен, используется memory cache: {e}")
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Получение значения из кэша"""
        if not self.cache_enabled:
            return None
        
        try:
            # Пытаемся получить из Redis
            if self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    return json.loads(value)
            
            # Fallback на memory cache
            if key in self.memory_cache:
                cache_item = self.memory_cache[key]
                
                # Проверяем TTL
                if cache_item['expires_at'] > datetime.now():
                    return cache_item['value']
                else:
                    # Удаляем устаревший элемент
                    del self.memory_cache[key]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения из кэша {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Сохранение значения в кэш"""
        if not self.cache_enabled:
            return False
        
        ttl = ttl or self.default_ttl
        
        try:
            # Сериализуем значение
            serialized_value = json.dumps(value, ensure_ascii=False, default=str)
            
            # Сохраняем в Redis
            if self.redis_client:
                await self.redis_client.setex(key, ttl, serialized_value)
                return True
            
            # Fallback на memory cache
            expires_at = datetime.now() + timedelta(seconds=ttl)
            self.memory_cache[key] = {
                'value': value,
                'expires_at': expires_at
            }
            
            # Очищаем устаревшие элементы
            await self._cleanup_memory_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения в кэш {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Удаление значения из кэша"""
        if not self.cache_enabled:
            return False
        
        try:
            # Удаляем из Redis
            if self.redis_client:
                await self.redis_client.delete(key)
            
            # Удаляем из memory cache
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка удаления из кэша {key}: {e}")
            return False
    
    async def clear(self, pattern: Optional[str] = None) -> bool:
        """Очистка кэша"""
        if not self.cache_enabled:
            return False
        
        try:
            if pattern:
                # Очищаем по паттерну
                if self.redis_client:
                    keys = await self.redis_client.keys(pattern)
                    if keys:
                        await self.redis_client.delete(*keys)
                
                # Очищаем memory cache по паттерну
                keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
                for key in keys_to_delete:
                    del self.memory_cache[key]
            else:
                # Полная очистка
                if self.redis_client:
                    await self.redis_client.flushdb()
                
                self.memory_cache.clear()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка очистки кэша: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Проверка существования ключа в кэше"""
        if not self.cache_enabled:
            return False
        
        try:
            # Проверяем Redis
            if self.redis_client:
                return bool(await self.redis_client.exists(key))
            
            # Проверяем memory cache
            if key in self.memory_cache:
                cache_item = self.memory_cache[key]
                if cache_item['expires_at'] > datetime.now():
                    return True
                else:
                    del self.memory_cache[key]
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки существования {key}: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        stats = {
            "enabled": self.cache_enabled,
            "redis_available": self.redis_client is not None,
            "memory_cache_size": len(self.memory_cache),
            "default_ttl": self.default_ttl
        }
        
        if self.redis_client:
            try:
                info = await self.redis_client.info()
                stats.update({
                    "redis_used_memory": info.get("used_memory_human", "N/A"),
                    "redis_connected_clients": info.get("connected_clients", 0),
                    "redis_total_commands": info.get("total_commands_processed", 0)
                })
            except Exception as e:
                logger.error(f"❌ Ошибка получения статистики Redis: {e}")
        
        return stats
    
    async def _cleanup_memory_cache(self):
        """Очистка устаревших элементов memory cache"""
        try:
            current_time = datetime.now()
            expired_keys = [
                key for key, item in self.memory_cache.items()
                if item['expires_at'] <= current_time
            ]
            
            for key in expired_keys:
                del self.memory_cache[key]
            
            # Ограничиваем размер memory cache
            if len(self.memory_cache) > 1000:
                # Удаляем самые старые элементы
                sorted_items = sorted(
                    self.memory_cache.items(),
                    key=lambda x: x[1]['expires_at']
                )
                
                # Оставляем только 800 элементов
                for key, _ in sorted_items[:-800]:
                    del self.memory_cache[key]
                
                logger.info("🧹 Memory cache очищен от старых элементов")
            
        except Exception as e:
            logger.error(f"❌ Ошибка очистки memory cache: {e}")


class AnalysisCacheService(CacheService):
    """Специализированный сервис кэширования для анализов"""
    
    def __init__(self):
        super().__init__()
        self.analysis_ttl = settings.redis_ttl_ohlcv  # 15 минут
    
    async def get_analysis(self, symbol: str, interval: str, days: int) -> Optional[Dict[str, Any]]:
        """Получение кэшированного анализа"""
        cache_key = f"analysis:{symbol}:{interval}:{days}"
        return await self.get(cache_key)
    
    async def set_analysis(
        self,
        symbol: str,
        interval: str,
        days: int,
        analysis_data: Dict[str, Any]
    ) -> bool:
        """Сохранение анализа в кэш"""
        cache_key = f"analysis:{symbol}:{interval}:{days}"
        return await self.set(cache_key, analysis_data, self.analysis_ttl)
    
    async def get_ohlcv_data(self, symbol: str, interval: str, limit: int) -> Optional[list]:
        """Получение кэшированных OHLCV данных"""
        cache_key = f"ohlcv:{symbol}:{interval}:{limit}"
        return await self.get(cache_key)
    
    async def set_ohlcv_data(
        self,
        symbol: str,
        interval: str,
        limit: int,
        ohlcv_data: list
    ) -> bool:
        """Сохранение OHLCV данных в кэш"""
        cache_key = f"ohlcv:{symbol}:{interval}:{limit}"
        # OHLCV данные кэшируем на меньшее время
        return await self.set(cache_key, ohlcv_data, 300)  # 5 минут
    
    async def clear_symbol_cache(self, symbol: str) -> bool:
        """Очистка кэша для конкретного символа"""
        patterns = [
            f"analysis:{symbol}:*",
            f"ohlcv:{symbol}:*"
        ]
        
        for pattern in patterns:
            await self.clear(pattern)
        
        return True


# Глобальные экземпляры сервисов
cache_service = CacheService()
analysis_cache = AnalysisCacheService()
