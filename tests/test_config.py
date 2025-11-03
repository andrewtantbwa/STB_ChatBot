from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from stb_chatbot.config import Settings


def test_load_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_BASE", "https://example.test")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-5")
    monkeypatch.setenv("HEYGEN_API_KEY", "hg-test")
    monkeypatch.setenv("HEYGEN_VOICE_ID", "mira")
    monkeypatch.setenv("HEYGEN_AUDIO_FORMAT", "wav")
    monkeypatch.setenv("HEYGEN_POLL_INTERVAL", "0.5")
    monkeypatch.setenv("HEYGEN_POLL_TIMEOUT", "10")
    audio_dir = tmp_path / "audio"
    monkeypatch.setenv("CHATBOT_AUDIO_DIR", str(audio_dir))

    settings = Settings.load()

    assert settings.openai_api_key == "test-key"
    assert settings.openai_api_base == "https://example.test"
    assert settings.heygen_api_key == "hg-test"
    assert settings.heygen_voice_id == "mira"
    assert settings.audio_format == "wav"
    assert settings.audio_dir == audio_dir
    assert settings.poll_interval == pytest.approx(0.5)
    assert settings.poll_timeout == pytest.approx(10.0)


def test_load_settings_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in list(os.environ):
        if key.startswith("OPENAI_") or key.startswith("HEYGEN_") or key == "CHATBOT_AUDIO_DIR":
            monkeypatch.delenv(key, raising=False)

    with pytest.raises(RuntimeError):
        Settings.load()
