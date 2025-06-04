#!/usr/bin/env python3
# scripts/add_llm_providers.py
import os

# Куда кладём файлы
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api", "services", "providers"))
LLM_SERVICE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api", "services"))

# Содержимое файлов
FILES = {
    "base.py": '''\
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMProvider(ABC):
    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        messages: список {"role": ..., "content": ...}
        Возвращает dict с ключом "content".
        """
        pass
''',
    "openai_provider.py": '''\
import os
import openai
from .base import LLMProvider

class OpenAIProvider(LLMProvider):
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def generate(self, messages, **kwargs):
        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return {
            "content": resp.choices[0].message["content"].strip()
        }
''',
    "google_provider.py": '''\
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
''',
    "huggingface_provider.py": '''\
import os
from huggingface_hub import InferenceClient
from .base import LLMProvider

class HuggingFaceProvider(LLMProvider):
    def __init__(self):
        self.client = InferenceClient(api_key=os.getenv("HF_API_KEY"))
        self.model = os.getenv("HF_MODEL", "gpt2")

    def generate(self, messages, **kwargs):
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return {
            "content": resp.choices[0].message
        }
''',
}

LLM_SERVICE = {
    "llm_service.py": '''\
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
''',
}

def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)

def write_files(folder, files_dict):
    for name, content in files_dict.items():
        path = os.path.join(folder, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✔ Создан {path}")

def main():
    # 1. Папка providers
    ensure_dir(BASE)
    write_files(BASE, FILES)

    # 2. LLMService
    write_files(LLM_SERVICE_DIR, LLM_SERVICE)

    print("\n✅ Aдаптеры LLM-провайдеров добавлены.")
    print("Не забудьте в .env.* прописать: LLM_PROVIDER=openai")

if __name__ == "__main__":
    main()
