import os
import logging
from typing import List, Dict, Any
from backend.services.providers.openai_provider import OpenAIProvider
from backend.services.providers.google_provider import GoogleVertexAIProvider
from backend.services.providers.huggingface_provider import HuggingFaceProvider
from backend.services.providers.base import LLMProviderError, LLMResponse

logger = logging.getLogger(__name__)

class LLMService:
    """
    Сервис для работы с различными LLM провайдерами.
    Обеспечивает единый интерфейс для всех провайдеров.
    """

    def __init__(self):
        provider_name = os.getenv("LLM_PROVIDER", "openai").lower()

        try:
            if provider_name == "google":
                self.client = GoogleVertexAIProvider()
            elif provider_name == "huggingface":
                self.client = HuggingFaceProvider()
            else:
                self.client = OpenAIProvider()

            self.provider_name = provider_name
            logger.info(f"Инициализирован LLM провайдер: {provider_name}")

        except LLMProviderError as e:
            logger.error(f"Ошибка инициализации провайдера {provider_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка при инициализации провайдера {provider_name}: {e}")
            raise LLMProviderError(f"Не удалось инициализировать провайдер {provider_name}: {e}")

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """
        Генерирует ответ от LLM модели

        Args:
            messages: список сообщений в формате [{"role": "user", "content": "..."}]
            **kwargs: дополнительные параметры для модели

        Returns:
            LLMResponse: стандартизированный ответ

        Raises:
            LLMProviderError: при ошибках провайдера
        """
        if not messages:
            raise LLMProviderError("Список сообщений не может быть пустым")

        try:
            response = self.client.generate(messages, **kwargs)
            logger.debug(f"Получен ответ от {self.provider_name}: {len(response.content)} символов")
            return response

        except LLMProviderError:
            # Пробрасываем ошибки провайдера как есть
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка в LLMService: {e}")
            raise LLMProviderError(f"Ошибка при генерации ответа: {e}")

    def generate_dict(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Генерирует ответ и возвращает его в виде словаря для обратной совместимости

        Args:
            messages: список сообщений
            **kwargs: дополнительные параметры

        Returns:
            Dict с ключом "content" и дополнительной информацией
        """
        response = self.generate(messages, **kwargs)
        return response.to_dict()
