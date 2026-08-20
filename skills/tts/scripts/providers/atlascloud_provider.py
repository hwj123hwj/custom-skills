"""Atlas Cloud TTS provider with bounded prediction polling.

Config: ATLASCLOUD_API_KEY in env vars / .env. ATLASCLOUD_BASE_URL can
optionally point at a compatible deployment.
"""

import json
import os
import time
import urllib.error
import urllib.request
from typing import Callable, Optional

from .base import TTSProvider, TTSResult


class AtlasCloudTTSProvider(TTSProvider):
    """TTS via Atlas Cloud's asynchronous audio generation API."""

    DEFAULT_BASE_URL = "https://api.atlascloud.ai"
    DEFAULT_MODEL = "xai/tts-v1"
    COMPLETED_STATUSES = {"completed", "succeeded", "success"}
    FAILED_STATUSES = {"failed", "canceled", "cancelled"}

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        poll_interval: float = 2.0,
        max_polls: int = 60,
        sleep_fn: Callable[[float], None] = time.sleep,
    ):
        from .registry import _read_env_value

        self.api_key = (
            api_key
            or os.environ.get("ATLASCLOUD_API_KEY")
            or _read_env_value("ATLASCLOUD_API_KEY")
        )
        if not self.api_key:
            raise ValueError(
                "ATLASCLOUD_API_KEY not set. Set it in .env or as env var."
            )
        self.model = (
            model
            or self.DEFAULT_MODEL
        )
        if self.model != self.DEFAULT_MODEL:
            raise ValueError(
                f"Unsupported Atlas Cloud TTS model '{self.model}'. "
                f"Supported: {self.DEFAULT_MODEL}"
            )
        self.base_url = (
            base_url
            or os.environ.get("ATLASCLOUD_BASE_URL")
            or _read_env_value("ATLASCLOUD_BASE_URL")
            or self.DEFAULT_BASE_URL
        ).rstrip("/")
        self.poll_interval = poll_interval
        self.max_polls = max_polls
        self.sleep_fn = sleep_fn

    def _request_json(
        self,
        url: str,
        *,
        method: str = "GET",
        payload: Optional[dict] = None,
    ) -> dict:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "custom-skills-tts/1.0",
            },
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                result = json.load(response)
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace") if error.fp else ""
            raise RuntimeError(
                f"Atlas Cloud API error {error.code}: {body or error.reason}"
            ) from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"Atlas Cloud request failed: {error.reason}") from error

        if not isinstance(result, dict):
            raise RuntimeError("Atlas Cloud returned a non-object response")
        data_obj = result.get("data")
        return data_obj if isinstance(data_obj, dict) else result

    @staticmethod
    def _normalize_language(language: str) -> str:
        if not language:
            return "auto"
        normalized = language.strip()
        base = normalized.lower().split("-", 1)[0]
        if base in {"zh", "en"}:
            return base
        return normalized

    def _download_audio(self, url: str, output_path: str) -> None:
        request = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                audio = response.read()
        except (urllib.error.HTTPError, urllib.error.URLError) as error:
            raise RuntimeError(f"Atlas Cloud audio download failed: {error}") from error

        if not audio:
            raise RuntimeError("Atlas Cloud returned an empty audio file")
        output_dir = os.path.dirname(os.path.abspath(output_path))
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "wb") as audio_file:
            audio_file.write(audio)

    def synthesize(
        self,
        text: str,
        output_path: str,
        voice: str = "eve",
        language: str = "",
        speed: float = 1.0,
    ) -> Optional[TTSResult]:
        if not text:
            raise ValueError("Text cannot be empty")
        if not 0.7 <= speed <= 1.5:
            raise ValueError("Atlas Cloud xAI TTS speed must be between 0.7 and 1.5")

        prediction = self._request_json(
            f"{self.base_url}/api/v1/model/generateAudio",
            method="POST",
            payload={
                "model": self.model,
                "text": text,
                "voice_id": voice or "eve",
                "language": self._normalize_language(language),
                "codec": "mp3",
                "speed": speed,
            },
        )

        for poll_index in range(self.max_polls + 1):
            status = str(prediction.get("status", "")).lower()
            outputs = prediction.get("outputs") or []
            if status in self.COMPLETED_STATUSES and outputs:
                self._download_audio(str(outputs[0]), output_path)
                return TTSResult(
                    output_path=os.path.abspath(output_path),
                    provider="atlascloud",
                )
            if status in self.FAILED_STATUSES:
                detail = prediction.get("error") or prediction.get("message") or status
                raise RuntimeError(f"Atlas Cloud TTS prediction failed: {detail}")
            if poll_index == self.max_polls:
                break

            prediction_id = prediction.get("id") or prediction.get("request_id")
            if not prediction_id:
                raise RuntimeError("Atlas Cloud response did not include a prediction id")
            self.sleep_fn(self.poll_interval)
            prediction = self._request_json(
                f"{self.base_url}/api/v1/model/prediction/{prediction_id}"
            )

        raise TimeoutError(
            f"Atlas Cloud TTS prediction did not finish after {self.max_polls} polls"
        )
