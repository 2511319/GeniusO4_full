import os
from services.providers.openai_provider import OpenAIProvider
from services.providers.google_provider import GoogleVertexAIProvider
from services.providers.huggingface_provider import HuggingFaceProvider

class LLMService:
    def __init__(self):
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
        if provider == "google":
            self.client = GoogleVertexAIProvider()
        elif provider == "huggingface":
            self.client = HuggingFaceProvider()
        else:
            self.client = OpenAIProvider()

    def generate(self, messages, **kwargs):
        return self.client.generate(messages, **kwargs)
