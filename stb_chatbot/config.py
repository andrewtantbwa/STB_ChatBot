"""Configuration handling for the chatbot prototype."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:  # pragma: no cover - optional dependency
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    def load_dotenv() -> bool:  # type: ignore
        return False


@dataclass(slots=True)
class Settings:
    """Container for environment configuration values."""

    openai_api_key: str
    openai_api_base: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-5"
    heygen_api_key: str | None = None
    heygen_voice_id: str = "charles"
    audio_format: str = "mp3"
    audio_dir: Path = field(default_factory=lambda: Path("output"))
    poll_interval: float = 1.0
    poll_timeout: float = 60.0

    @classmethod
    def load(cls) -> "Settings":
        """Load configuration from the environment, using `.env` if present."""

        load_dotenv()

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required")

        heygen_api_key = os.getenv("HEYGEN_API_KEY")

        audio_dir_raw: Optional[str] = os.getenv("CHATBOT_AUDIO_DIR")
        audio_dir = Path(audio_dir_raw) if audio_dir_raw else Path("output")

        return cls(
            openai_api_key=openai_api_key,
            openai_api_base=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-5"),
            heygen_api_key=heygen_api_key,
            heygen_voice_id=os.getenv("HEYGEN_VOICE_ID", "charles"),
            audio_format=os.getenv("HEYGEN_AUDIO_FORMAT", "mp3"),
            audio_dir=audio_dir,
            poll_interval=float(os.getenv("HEYGEN_POLL_INTERVAL", "1.0")),
            poll_timeout=float(os.getenv("HEYGEN_POLL_TIMEOUT", "60.0")),
        )

    def ensure_output_dir(self) -> None:
        """Create the output directory if it does not exist."""

        self.audio_dir.mkdir(parents=True, exist_ok=True)
