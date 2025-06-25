import os
from openai import OpenAI
from openai import OpenAIError, RateLimitError, AuthenticationError
import requests
from .base import LLMProvider, LLMResponse, LLMProviderError

class OpenAIProvider(LLMProvider):
    def __init__(self):
        super().__init__()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMProviderError("OPENAI_API_KEY не найден в переменных окружения")

        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def generate(self, messages, **kwargs):
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )

            content = resp.choices[0].message.content
            if content is None:
                content = ""
            else:
                content = content.strip()

            # Извлекаем информацию об использовании
            usage = {}
            if hasattr(resp, 'usage') and resp.usage:
                usage = {
                    "prompt_tokens": getattr(resp.usage, 'prompt_tokens', 0),
                    "completion_tokens": getattr(resp.usage, 'completion_tokens', 0),
                    "total_tokens": getattr(resp.usage, 'total_tokens', 0)
                }

            return LLMResponse(
                content=content,
                model=resp.model,
                usage=usage,
                metadata={"provider": "openai"}
            )

        except AuthenticationError as e:
            self._handle_error(e, "Ошибка аутентификации OpenAI")
        except RateLimitError as e:
            self._handle_error(e, "Превышен лимит запросов OpenAI")
        except requests.exceptions.RequestException as e:
            self._handle_error(e, "Сетевая ошибка при обращении к OpenAI")
        except OpenAIError as e:
            self._handle_error(e, "Ошибка OpenAI API")
        except Exception as e:
            self._handle_error(e, "Неожиданная ошибка OpenAI")
