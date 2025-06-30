# 🔄 LLM Adapter Pattern for ChartGenius
# Версия: 1.1.0-dev
# Унифицированный интерфейс для LLM провайдеров

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import json

from backend.services.providers.openai_provider import OpenAIProvider
from backend.services.providers.google_provider import GoogleVertexAIProvider
from backend.services.providers.huggingface_provider import HuggingFaceProvider
from backend.services.providers.base import LLMResponse, LLMProviderError
from backend.services.metrics_service import metrics

logger = logging.getLogger(__name__)

class ProviderType(Enum):
    """Типы LLM провайдеров"""
    OPENAI = "openai"
    GOOGLE = "google"
    HUGGINGFACE = "huggingface"
    ANTHROPIC = "anthropic"

class ProviderStatus(Enum):
    """Статусы провайдеров"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"

@dataclass
class ProviderConfig:
    """Конфигурация провайдера"""
    provider_type: ProviderType
    model: str
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: float = 30.0
    retry_attempts: int = 3
    cost_per_token: float = 0.00002
    priority: int = 1  # 1 = highest priority

@dataclass
class ProviderHealth:
    """Состояние здоровья провайдера"""
    status: ProviderStatus
    last_check: datetime
    response_time: float
    error_rate: float
    success_count: int
    error_count: int

class LLMAdapter(ABC):
    """Базовый адаптер для LLM провайдеров"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.health = ProviderHealth(
            status=ProviderStatus.HEALTHY,
            last_check=datetime.utcnow(),
            response_time=0.0,
            error_rate=0.0,
            success_count=0,
            error_count=0
        )
    
    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Генерация ответа от LLM"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Проверка здоровья провайдера"""
        pass
    
    def update_health(self, success: bool, response_time: float):
        """Обновление метрик здоровья"""
        if success:
            self.health.success_count += 1
        else:
            self.health.error_count += 1
        
        total_requests = self.health.success_count + self.health.error_count
        self.health.error_rate = self.health.error_count / total_requests if total_requests > 0 else 0
        self.health.response_time = response_time
        self.health.last_check = datetime.utcnow()
        
        # Определяем статус на основе метрик
        if self.health.error_rate > 0.5:
            self.health.status = ProviderStatus.UNAVAILABLE
        elif self.health.error_rate > 0.2 or response_time > 10.0:
            self.health.status = ProviderStatus.DEGRADED
        else:
            self.health.status = ProviderStatus.HEALTHY

class OpenAIAdapter(LLMAdapter):
    """Адаптер для OpenAI"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.provider = OpenAIProvider()
    
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Генерация ответа от OpenAI"""
        start_time = datetime.utcnow()
        
        try:
            # Применяем конфигурацию
            params = {
                'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
                'temperature': kwargs.get('temperature', self.config.temperature),
                **kwargs
            }
            
            response = await asyncio.to_thread(self.provider.generate, messages, **params)
            
            # Обновляем метрики
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self.update_health(True, response_time)
            
            # Трекинг метрик
            metrics.track_llm_request(
                provider=self.config.provider_type.value,
                model=self.config.model,
                status='success',
                duration=response_time,
                tokens_used=response.usage,
                cost_estimate=self._calculate_cost(response.usage)
            )
            
            return response
            
        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self.update_health(False, response_time)
            
            metrics.track_llm_request(
                provider=self.config.provider_type.value,
                model=self.config.model,
                status='error',
                duration=response_time
            )
            
            logger.error(f"OpenAI adapter error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Проверка здоровья OpenAI"""
        try:
            test_messages = [{"role": "user", "content": "test"}]
            await asyncio.wait_for(
                asyncio.to_thread(self.provider.generate, test_messages, max_tokens=1),
                timeout=5.0
            )
            return True
        except Exception:
            return False
    
    def _calculate_cost(self, usage: Dict[str, int]) -> float:
        """Расчет стоимости запроса"""
        if not usage:
            return 0.0
        
        total_tokens = usage.get('total_tokens', 0)
        return total_tokens * self.config.cost_per_token

class GoogleAdapter(LLMAdapter):
    """Адаптер для Google Vertex AI"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.provider = GoogleVertexAIProvider()
    
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Генерация ответа от Google"""
        start_time = datetime.utcnow()
        
        try:
            response = await asyncio.to_thread(self.provider.generate, messages, **kwargs)
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self.update_health(True, response_time)
            
            metrics.track_llm_request(
                provider=self.config.provider_type.value,
                model=self.config.model,
                status='success',
                duration=response_time
            )
            
            return response
            
        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self.update_health(False, response_time)
            
            metrics.track_llm_request(
                provider=self.config.provider_type.value,
                model=self.config.model,
                status='error',
                duration=response_time
            )
            
            logger.error(f"Google adapter error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Проверка здоровья Google Vertex AI"""
        try:
            test_messages = [{"role": "user", "content": "test"}]
            await asyncio.wait_for(
                asyncio.to_thread(self.provider.generate, test_messages),
                timeout=10.0
            )
            return True
        except Exception:
            return False

class HuggingFaceAdapter(LLMAdapter):
    """Адаптер для HuggingFace"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.provider = HuggingFaceProvider()
    
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Генерация ответа от HuggingFace"""
        start_time = datetime.utcnow()
        
        try:
            response = await asyncio.to_thread(self.provider.generate, messages, **kwargs)
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self.update_health(True, response_time)
            
            metrics.track_llm_request(
                provider=self.config.provider_type.value,
                model=self.config.model,
                status='success',
                duration=response_time
            )
            
            return response
            
        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self.update_health(False, response_time)
            
            metrics.track_llm_request(
                provider=self.config.provider_type.value,
                model=self.config.model,
                status='error',
                duration=response_time
            )
            
            logger.error(f"HuggingFace adapter error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Проверка здоровья HuggingFace"""
        try:
            test_messages = [{"role": "user", "content": "test"}]
            await asyncio.wait_for(
                asyncio.to_thread(self.provider.generate, test_messages),
                timeout=15.0
            )
            return True
        except Exception:
            return False

class LLMAdapterManager:
    """Менеджер LLM адаптеров с fallback логикой"""
    
    def __init__(self):
        self.adapters: Dict[ProviderType, LLMAdapter] = {}
        self.primary_provider: Optional[ProviderType] = None
        self.fallback_order: List[ProviderType] = []
    
    def register_adapter(self, adapter: LLMAdapter, is_primary: bool = False):
        """Регистрация адаптера"""
        provider_type = adapter.config.provider_type
        self.adapters[provider_type] = adapter
        
        if is_primary:
            self.primary_provider = provider_type
        
        # Обновляем порядок fallback по приоритету
        self._update_fallback_order()
        
        logger.info(f"Registered LLM adapter: {provider_type.value}")
    
    def _update_fallback_order(self):
        """Обновление порядка fallback провайдеров"""
        # Сортируем по приоритету (1 = highest)
        sorted_adapters = sorted(
            self.adapters.items(),
            key=lambda x: (x[1].config.priority, x[1].health.error_rate)
        )
        
        self.fallback_order = [provider_type for provider_type, _ in sorted_adapters]
    
    async def generate(self, messages: List[Dict[str, str]], 
                      preferred_provider: Optional[ProviderType] = None,
                      **kwargs) -> LLMResponse:
        """
        Генерация ответа с автоматическим fallback
        
        Args:
            messages: Сообщения для LLM
            preferred_provider: Предпочитаемый провайдер
            **kwargs: Дополнительные параметры
            
        Returns:
            LLMResponse: Ответ от LLM
        """
        # Определяем порядок попыток
        providers_to_try = []
        
        if preferred_provider and preferred_provider in self.adapters:
            providers_to_try.append(preferred_provider)
        
        if self.primary_provider and self.primary_provider not in providers_to_try:
            providers_to_try.append(self.primary_provider)
        
        # Добавляем остальные провайдеры по порядку fallback
        for provider in self.fallback_order:
            if provider not in providers_to_try:
                providers_to_try.append(provider)
        
        last_error = None
        
        for provider_type in providers_to_try:
            adapter = self.adapters.get(provider_type)
            if not adapter:
                continue
            
            # Пропускаем недоступные провайдеры
            if adapter.health.status == ProviderStatus.UNAVAILABLE:
                logger.warning(f"Skipping unavailable provider: {provider_type.value}")
                continue
            
            try:
                logger.info(f"Attempting LLM request with provider: {provider_type.value}")
                response = await adapter.generate(messages, **kwargs)
                
                # Добавляем информацию о провайдере в метаданные
                response.metadata['used_provider'] = provider_type.value
                response.metadata['fallback_used'] = provider_type != providers_to_try[0]
                
                return response
                
            except Exception as e:
                last_error = e
                logger.warning(f"Provider {provider_type.value} failed: {e}")
                continue
        
        # Все провайдеры не сработали
        error_msg = f"All LLM providers failed. Last error: {last_error}"
        logger.error(error_msg)
        raise LLMProviderError(error_msg)
    
    async def health_check_all(self) -> Dict[ProviderType, bool]:
        """Проверка здоровья всех провайдеров"""
        results = {}
        
        for provider_type, adapter in self.adapters.items():
            try:
                is_healthy = await adapter.health_check()
                results[provider_type] = is_healthy
                
                if not is_healthy:
                    adapter.health.status = ProviderStatus.UNAVAILABLE
                
            except Exception as e:
                logger.error(f"Health check failed for {provider_type.value}: {e}")
                results[provider_type] = False
                adapter.health.status = ProviderStatus.UNAVAILABLE
        
        return results
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Получение статистики провайдеров"""
        stats = {}
        
        for provider_type, adapter in self.adapters.items():
            stats[provider_type.value] = {
                'status': adapter.health.status.value,
                'error_rate': adapter.health.error_rate,
                'response_time': adapter.health.response_time,
                'success_count': adapter.health.success_count,
                'error_count': adapter.health.error_count,
                'last_check': adapter.health.last_check.isoformat(),
                'priority': adapter.config.priority
            }
        
        return stats

# === FACTORY FUNCTIONS ===
def create_adapter_manager() -> LLMAdapterManager:
    """Создание менеджера адаптеров с конфигурацией по умолчанию"""
    manager = LLMAdapterManager()
    
    # OpenAI (primary)
    openai_config = ProviderConfig(
        provider_type=ProviderType.OPENAI,
        model="gpt-4o-mini",
        max_tokens=4000,
        temperature=0.7,
        priority=1,
        cost_per_token=0.00002
    )
    openai_adapter = OpenAIAdapter(openai_config)
    manager.register_adapter(openai_adapter, is_primary=True)
    
    # Google (fallback)
    google_config = ProviderConfig(
        provider_type=ProviderType.GOOGLE,
        model="gemini-pro",
        max_tokens=4000,
        temperature=0.7,
        priority=2,
        cost_per_token=0.00001
    )
    google_adapter = GoogleAdapter(google_config)
    manager.register_adapter(google_adapter)
    
    # HuggingFace (fallback)
    hf_config = ProviderConfig(
        provider_type=ProviderType.HUGGINGFACE,
        model="microsoft/DialoGPT-large",
        max_tokens=2000,
        temperature=0.7,
        priority=3,
        cost_per_token=0.0
    )
    hf_adapter = HuggingFaceAdapter(hf_config)
    manager.register_adapter(hf_adapter)
    
    return manager

# Глобальный экземпляр менеджера
llm_adapter_manager = create_adapter_manager()
