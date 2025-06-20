from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LLMProviderError(Exception):
    """Базовое исключение для ошибок LLM провайдеров"""
    pass

class LLMAPIError(LLMProviderError):
    """Ошибка API провайдера"""
    pass

class LLMNetworkError(LLMProviderError):
    """Сетевая ошибка при обращении к провайдеру"""
    pass

class LLMAuthenticationError(LLMProviderError):
    """Ошибка аутентификации"""
    pass

class LLMRateLimitError(LLMProviderError):
    """Превышен лимит запросов"""
    pass

class LLMResponse:
    """Стандартизированный ответ от LLM провайдера"""
    def __init__(
        self,
        content: str,
        model: Optional[str] = None,
        usage: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.model = model
        self.usage = usage or {}
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует ответ в словарь для обратной совместимости"""
        return {
            "content": self.content,
            "model": self.model,
            "usage": self.usage,
            "metadata": self.metadata
        }

class LLMProvider(ABC):
    """Базовый класс для всех LLM провайдеров"""

    def __init__(self):
        self.provider_name = self.__class__.__name__

    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        """
        Генерирует ответ от LLM модели

        Args:
            messages: список {"role": ..., "content": ...}
            **kwargs: дополнительные параметры для модели

        Returns:
            LLMResponse: стандартизированный ответ

        Raises:
            LLMProviderError: при ошибках провайдера
        """
        pass

    def _handle_error(self, error: Exception, context: str = "") -> None:
        """Обрабатывает и классифицирует ошибки"""
        error_msg = f"{self.provider_name}: {context} - {str(error)}"
        logger.error(error_msg)

        # Классификация ошибок по типам
        error_str = str(error).lower()

        if "authentication" in error_str or "unauthorized" in error_str or "api key" in error_str:
            raise LLMAuthenticationError(f"Ошибка аутентификации: {error}")
        elif "rate limit" in error_str or "quota" in error_str or "too many requests" in error_str:
            raise LLMRateLimitError(f"Превышен лимит запросов: {error}")
        elif "network" in error_str or "connection" in error_str or "timeout" in error_str:
            raise LLMNetworkError(f"Сетевая ошибка: {error}")
        else:
            raise LLMAPIError(f"Ошибка API: {error}")
