import os
import requests
from .base import LLMProvider, LLMResponse, LLMProviderError

# Опциональный импорт Google Cloud
try:
    from google.cloud import aiplatform
    from google.api_core import exceptions as gcp_exceptions
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    aiplatform = None
    gcp_exceptions = None

class GoogleVertexAIProvider(LLMProvider):
    def __init__(self):
        super().__init__()

        if not GOOGLE_AVAILABLE:
            raise LLMProviderError(
                "Google Cloud библиотеки не установлены. "
                "Установите: pip install google-cloud-aiplatform"
            )

        project_id = os.getenv("GCP_PROJECT_ID")
        region = os.getenv("GCP_REGION")
        endpoint = os.getenv("GOOGLE_AI_ENDPOINT")

        if not all([project_id, region, endpoint]):
            raise LLMProviderError(
                "Не найдены обязательные переменные окружения для Google: "
                "GCP_PROJECT_ID, GCP_REGION, GOOGLE_AI_ENDPOINT"
            )

        try:
            aiplatform.init(project=project_id, location=region)
            self.endpoint = endpoint
        except Exception as e:
            raise LLMProviderError(f"Ошибка инициализации Google AI Platform: {e}")

    def generate(self, messages, **kwargs):
        try:
            client = aiplatform.gapic.PredictionServiceClient()

            # Берём последний user-сообщение или объединяем все сообщения
            if len(messages) == 1:
                content = messages[0]["content"]
            else:
                # Объединяем все сообщения в один текст
                content = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

            instance = {"content": content}
            response = client.predict(
                endpoint=self.endpoint,
                instances=[instance],
                parameters=kwargs
            )

            # Извлекаем контент из ответа
            predictions = response.predictions
            if not predictions:
                content = ""
            else:
                content = predictions[0].get("content", "")

            return LLMResponse(
                content=content,
                model="google-vertex-ai",
                usage={},  # Google не всегда предоставляет информацию об использовании
                metadata={"provider": "google", "endpoint": self.endpoint}
            )

        except gcp_exceptions.Unauthenticated as e:
            self._handle_error(e, "Ошибка аутентификации Google")
        except gcp_exceptions.PermissionDenied as e:
            self._handle_error(e, "Нет разрешений для Google AI")
        except gcp_exceptions.ResourceExhausted as e:
            self._handle_error(e, "Превышен лимит запросов Google")
        except gcp_exceptions.GoogleAPICallError as e:
            self._handle_error(e, "Ошибка Google API")
        except requests.exceptions.RequestException as e:
            self._handle_error(e, "Сетевая ошибка при обращении к Google")
        except Exception as e:
            self._handle_error(e, "Неожиданная ошибка Google")
