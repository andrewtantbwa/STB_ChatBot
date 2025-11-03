"""High-level chatbot orchestration."""

from __future__ import annotations

import datetime as dt
import logging
from pathlib import Path
from typing import List, Mapping

from .audio import HeyGenClient, HeyGenError
from .config import Settings
from .llm import LLMClient

logger = logging.getLogger(__name__)


class ChatBot:
    """Conversation manager that links the GPT-5 model with HeyGen audio."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.ensure_output_dir()

        self._llm = LLMClient(
            api_key=settings.openai_api_key,
            api_base=settings.openai_api_base,
            model=settings.openai_model,
        )

        self._heygen: HeyGenClient | None = None
        if settings.heygen_api_key:
            self._heygen = HeyGenClient(
                api_key=settings.heygen_api_key,
                voice_id=settings.heygen_voice_id,
                audio_format=settings.audio_format,
                poll_interval=settings.poll_interval,
                poll_timeout=settings.poll_timeout,
            )

        self._history: List[Mapping[str, str]] = self._initial_history()

    def ask(self, prompt: str) -> str:
        """Send a user prompt to GPT-5 and return the assistant's reply."""

        self._history.append({"role": "user", "content": prompt})
        response = self._llm.generate(self._history)
        self._history.append({"role": "assistant", "content": response})
        return response

    def speak(self, message: str) -> Path | None:
        """Generate audio for the assistant *message* if HeyGen is configured."""

        if not self._heygen:
            logger.debug("HeyGen not configured; skipping audio synthesis")
            return None

        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audio_{timestamp}.{self.settings.audio_format}"
        destination = self.settings.audio_dir / filename
        try:
            return self._heygen.synthesize_to_file(message, destination)
        except HeyGenError as exc:
            logger.error("Failed to synthesize audio: %s", exc)
            return None

    def _initial_history(self) -> List[Mapping[str, str]]:
        return LLMClient.format_system_prompt(
            "You are an enthusiastic assistant that creates friendly, helpful replies. "
            "Keep answers concise and include actionable steps where possible."
        )

    @property
    def history(self) -> List[Mapping[str, str]]:
        """Expose the chat history (primarily for testing)."""

        return list(self._history)
