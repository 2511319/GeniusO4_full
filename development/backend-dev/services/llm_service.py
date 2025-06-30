import os
import logging
from typing import List, Dict, Any, Optional
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

    async def get_active_prompt(self, prompt_type: str) -> Optional[str]:
        """
        Получение активного промпта из Cloud Storage

        Args:
            prompt_type: Тип промпта (technical_analysis, etc.)

        Returns:
            str: Содержимое промпта или None
        """
        try:
            # Импортируем здесь чтобы избежать циклических импортов
            from backend.services.cloud_storage_service import cloud_storage_service

            content = await cloud_storage_service.get_active_prompt(prompt_type)
            if content:
                logger.debug(f"Получен активный промпт {prompt_type}: {len(content)} символов")
                return content
            else:
                logger.warning(f"Активный промпт {prompt_type} не найден")
                return None

        except Exception as e:
            logger.error(f"Ошибка получения активного промпта {prompt_type}: {e}")
            return None

    async def generate_with_prompt(self, prompt_type: str, user_message: str,
                                 context_data: Dict[str, Any] = None, **kwargs) -> LLMResponse:
        """
        Генерация ответа с использованием промпта из Cloud Storage

        Args:
            prompt_type: Тип промпта
            user_message: Сообщение пользователя
            context_data: Контекстные данные для подстановки в промпт
            **kwargs: Дополнительные параметры для модели

        Returns:
            LLMResponse: Ответ от LLM
        """
        try:
            # Получаем активный промпт
            system_prompt = await self.get_active_prompt(prompt_type)

            if not system_prompt:
                # Fallback на базовый промпт
                system_prompt = self._get_fallback_prompt(prompt_type)

            # Подставляем контекстные данные в промпт
            if context_data:
                try:
                    system_prompt = system_prompt.format(**context_data)
                except KeyError as e:
                    logger.warning(f"Не удалось подставить переменную в промпт: {e}")

            # Формируем сообщения
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            # Генерируем ответ
            response = self.generate(messages, **kwargs)

            logger.info(f"Сгенерирован ответ с промптом {prompt_type}: {len(response.content)} символов")
            return response

        except Exception as e:
            logger.error(f"Ошибка генерации с промптом {prompt_type}: {e}")
            raise LLMProviderError(f"Не удалось сгенерировать ответ с промптом {prompt_type}: {e}")

    def _get_fallback_prompt(self, prompt_type: str) -> str:
        """Получение fallback промпта если основной недоступен"""
        fallback_prompts = {
            "technical_analysis": """Вы - эксперт по техническому анализу криптовалют.
            Проанализируйте предоставленные данные и дайте профессиональную оценку.""",

            "fundamental_analysis": """Вы - эксперт по фундаментальному анализу криптовалют.
            Проанализируйте рыночные условия и дайте обоснованную оценку.""",

            "sentiment_analysis": """Вы - эксперт по анализу настроений рынка криптовалют.
            Оцените текущие настроения и их влияние на цену.""",

            "risk_assessment": """Вы - эксперт по оценке рисков в криптовалютах.
            Проанализируйте потенциальные риски и дайте рекомендации."""
        }

        return fallback_prompts.get(prompt_type, "Проанализируйте предоставленные данные.")
