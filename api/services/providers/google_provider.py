import os
from google.cloud import aiplatform
from .base import LLMProvider

class GoogleVertexAIProvider(LLMProvider):
    def __init__(self):
        aiplatform.init(
            project=os.getenv("GCP_PROJECT_ID"),
            location=os.getenv("GCP_REGION")
        )
        self.endpoint = os.getenv("GOOGLE_AI_ENDPOINT")

    def generate(self, messages, **kwargs):
        client = aiplatform.gapic.PredictionServiceClient()
        # Берём последний user-сообщение
        instance = {"content": messages[-1]["content"]}
        response = client.predict(
            endpoint=self.endpoint,
            instances=[instance],
            parameters={}
        )
        return {
            "content": response.predictions[0].get("content", "")
        }
