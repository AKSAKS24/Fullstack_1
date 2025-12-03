"""
Model provider registry.  Providers abstract away the details of communicating
with external language model APIs (OpenAI, Anthropic, etc.).  Each provider
implements an asynchronous `generate` method that takes a prompt and returns
generated text.
"""
import os
from typing import Dict, Protocol, Any
import openai


class Provider(Protocol):
    async def generate(self, prompt: str) -> str:
        ...


class OpenAIProvider:
    def __init__(self, model_name: str = "gpt-3.5-turbo") -> None:
        openai.api_key = os.environ.get("OPENAI_API_KEY", "")
        self.model_name = model_name

    async def generate(self, prompt: str) -> str:
        response = await openai.ChatCompletion.acreate(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=1024,
        )
        return response.choices[0].message.content


# Registry for available providers
_providers: Dict[str, Any] = {
    "openai": OpenAIProvider,
    # Future providers can be added here (Anthropic, Gemini, etc.)
}


def get_model(model_name: str) -> Provider:
    """
    Return an instance of the appropriate provider class based on the model name.
    For example, model names starting with 'gpt' use OpenAI.
    """
    if model_name.startswith("gpt"):
        return OpenAIProvider(model_name)
    # Add more conditional branches for other providers
    raise ValueError(f"No provider found for model '{model_name}'")