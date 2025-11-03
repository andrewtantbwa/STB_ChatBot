"""OpenAI GPT-5 interaction helpers."""

from __future__ import annotations

from typing import Iterable, List, Mapping

try:  # pragma: no cover - optional dependency
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore[misc,assignment]


class LLMClient:
    """Thin wrapper around the OpenAI SDK for chat completions."""

    def __init__(self, *, api_key: str, api_base: str, model: str) -> None:
        if OpenAI is None:  # pragma: no cover - defensive
            raise RuntimeError(
                "The 'openai' package is required to run the GPT-5 client. Install it via 'pip install openai'."
            )
        self._client = OpenAI(api_key=api_key, base_url=api_base)
        self._model = model

    def generate(self, messages: Iterable[Mapping[str, str]], *, temperature: float = 0.7) -> str:
        """Call the GPT-5 model and return the assistant message."""

        response = self._client.chat.completions.create(
            model=self._model,
            messages=list(messages),
            temperature=temperature,
        )
        choice = response.choices[0]
        if choice.message is None or choice.message.content is None:
            raise RuntimeError("GPT-5 response did not contain content")
        return choice.message.content

    @staticmethod
    def format_system_prompt(purpose: str) -> List[Mapping[str, str]]:
        """Create a simple system prompt."""

        return [
            {
                "role": "system",
                "content": purpose,
            }
        ]
