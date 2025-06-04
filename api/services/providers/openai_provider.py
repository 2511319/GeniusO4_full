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
