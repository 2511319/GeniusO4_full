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
