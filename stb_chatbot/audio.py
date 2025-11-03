"""HeyGen audio synthesis utilities."""

from __future__ import annotations

import base64
import logging
import time
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class HeyGenError(RuntimeError):
    """Raised when the HeyGen API returns an error."""


class HeyGenClient:
    """Simple HeyGen API client for text-to-speech tasks."""

    base_url = "https://api.heygen.com/v1"

    def __init__(
        self,
        *,
        api_key: str,
        voice_id: str,
        audio_format: str = "mp3",
        poll_interval: float = 1.0,
        poll_timeout: float = 60.0,
        session: Optional[Any] = None,
    ) -> None:
        self._api_key = api_key
        self._voice_id = voice_id
        self._audio_format = audio_format
        self._poll_interval = poll_interval
        self._poll_timeout = poll_timeout
        self._session = session or self._build_session()

    def synthesize_to_file(self, text: str, destination: Path) -> Path:
        """Create speech audio for *text* and write it to *destination*."""

        audio_bytes = self._synthesize(text)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(audio_bytes)
        logger.info("Saved HeyGen audio to %s", destination)
        return destination

    def _build_session(self) -> Any:
        try:
            import requests  # type: ignore
        except ImportError as exc:  # pragma: no cover - thin wrapper
            raise HeyGenError("The 'requests' package is required for HeyGen integration") from exc
        return requests.Session()

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _synthesize(self, text: str) -> bytes:
        payload = {
            "voice_id": self._voice_id,
            "text": text,
            "format": self._audio_format,
        }
        response = self._session.post(
            f"{self.base_url}/tts",
            json=payload,
            headers=self._headers(),
            timeout=30,
        )
        self._raise_for_error(response)
        data = response.json().get("data", {})

        if "audio" in data:
            return base64.b64decode(data["audio"])

        task_id = data.get("task_id")
        if not task_id:
            raise HeyGenError("HeyGen response missing audio or task_id")

        return self._poll_for_audio(task_id)

    def _poll_for_audio(self, task_id: str) -> bytes:
        deadline = time.monotonic() + self._poll_timeout
        status_url = f"{self.base_url}/task-status/{task_id}"
        while time.monotonic() < deadline:
            response = self._session.get(status_url, headers=self._headers(), timeout=15)
            self._raise_for_error(response)
            data = response.json().get("data", {})
            status = data.get("status")
            if status == "completed":
                audio_url = data.get("audio_url")
                audio_base64 = data.get("audio")
                if audio_base64:
                    return base64.b64decode(audio_base64)
                if not audio_url:
                    raise HeyGenError("Completed task missing audio data")
                download = self._session.get(audio_url, timeout=30)
                download.raise_for_status()
                return download.content
            if status in {"failed", "error"}:
                raise HeyGenError(f"HeyGen task {task_id} failed: {data}")
            time.sleep(self._poll_interval)

        raise HeyGenError(f"Timed out waiting for HeyGen task {task_id}")

    @staticmethod
    def _raise_for_error(response: Any) -> None:
        try:
            response.raise_for_status()
        except Exception as exc:  # pragma: no cover - thin wrapper
            text = getattr(response, "text", "")
            message = f"HeyGen API error: {exc} - {text}"
            raise HeyGenError(message) from exc
