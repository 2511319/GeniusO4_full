import os
from openai import OpenAI
from .base import LLMProvider

class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def generate(self, messages, **kwargs):
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return {
            "content": resp.choices[0].message.content.strip()
        }
