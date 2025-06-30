import os
import requests
from .base import LLMProvider, LLMResponse, LLMProviderError

# Опциональный импорт HuggingFace
try:
    from huggingface_hub import InferenceClient
    from huggingface_hub.utils import HfHubHTTPError
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    InferenceClient = None
    HfHubHTTPError = None

class HuggingFaceProvider(LLMProvider):
    def __init__(self):
        super().__init__()

        if not HUGGINGFACE_AVAILABLE:
            raise LLMProviderError(
                "HuggingFace библиотеки не установлены. "
                "Установите: pip install huggingface_hub"
            )

        api_key = os.getenv("HF_API_KEY")
        if not api_key:
            raise LLMProviderError("HF_API_KEY не найден в переменных окружения")

        self.client = InferenceClient(api_key=api_key)
        self.model = os.getenv("HF_MODEL", "microsoft/DialoGPT-medium")

    def generate(self, messages, **kwargs):
        try:
            # HuggingFace может иметь разные API в зависимости от модели
            # Пробуем chat completions API
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    **kwargs
                )

                # ИСПРАВЛЕНИЕ БАГА: добавляем .content
                content = resp.choices[0].message.content
                if content is None:
                    content = resp.choices[0].message  # fallback для старых версий

            except (AttributeError, TypeError):
                # Fallback для моделей, которые не поддерживают chat completions
                # Объединяем сообщения в один текст
                text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
                resp = self.client.text_generation(
                    text,
                    model=self.model,
                    **kwargs
                )
                content = resp.generated_text if hasattr(resp, 'generated_text') else str(resp)

            if isinstance(content, str):
                content = content.strip()
            else:
                content = str(content).strip()

            return LLMResponse(
                content=content,
                model=self.model,
                usage={},  # HuggingFace не всегда предоставляет информацию об использовании
                metadata={"provider": "huggingface"}
            )

        except HfHubHTTPError as e:
            if e.response.status_code == 401:
                self._handle_error(e, "Ошибка аутентификации HuggingFace")
            elif e.response.status_code == 429:
                self._handle_error(e, "Превышен лимит запросов HuggingFace")
            else:
                self._handle_error(e, "Ошибка HuggingFace API")
        except requests.exceptions.RequestException as e:
            self._handle_error(e, "Сетевая ошибка при обращении к HuggingFace")
        except Exception as e:
            self._handle_error(e, "Неожиданная ошибка HuggingFace")
