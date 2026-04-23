"""
SiliconFlow ASR provider — uses TeleAI/TeleSpeechASR model via OpenAI-compatible API.

Config: SILICONFLOW_API_KEY in .env or env var
"""

import os
import json
import urllib.request
import urllib.error
from typing import Optional

from .base import ASRProvider, ASRResult


class SiliconFlowASRProvider(ASRProvider):
    """ASR via SiliconFlow API (OpenAI-compatible)."""

    API_URL = "https://api.siliconflow.cn/v1/audio/transcriptions"

    def __init__(self, api_key: Optional[str] = None, model: str = "TeleAI/TeleSpeechASR"):
        from .registry import _read_env_value
        self.api_key = api_key or os.environ.get("SILICONFLOW_API_KEY") or _read_env_value("SILICONFLOW_API_KEY")
        if not self.api_key:
            raise ValueError("SILICONFLOW_API_KEY not set. Set it in .env or as env var.")
        self.model = model

    def transcribe(self, audio_path: str, language: str = "zh") -> Optional[ASRResult]:
        if not os.path.isfile(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        boundary = "----FormBoundary7MA4YWxkTrZu0gW"
        filename = os.path.basename(audio_path)

        with open(audio_path, "rb") as f:
            file_data = f.read()

        parts = [
            f"--{boundary}\r\n".encode("utf-8"),
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"),
            b"Content-Type: application/octet-stream\r\n\r\n",
            file_data,
            b"\r\n",
            f"--{boundary}\r\n".encode("utf-8"),
            f'Content-Disposition: form-data; name="model"\r\n\r\n'.encode("utf-8"),
            f"{self.model}\r\n".encode("utf-8"),
            f"--{boundary}\r\n".encode("utf-8"),
            f'Content-Disposition: form-data; name="language"\r\n\r\n'.encode("utf-8"),
            f"{language}\r\n".encode("utf-8"),
            f"--{boundary}--\r\n".encode("utf-8"),
        ]
        form_data = b"".join(parts)

        req = urllib.request.Request(
            self.API_URL,
            data=form_data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                text = result.get("text", "").strip()
                if not text:
                    return None
                return ASRResult(
                    text=text,
                    language=language,
                    provider="siliconflow",
                )
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace") if e.fp else ""
            raise RuntimeError(f"SiliconFlow API error {e.code}: {body}")
        except Exception as e:
            raise RuntimeError(f"SiliconFlow ASR failed: {e}")
