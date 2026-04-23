"""
Vertex AI TTS provider — Google Gemini TTS models.

Config: VERTEX_API_KEY or GEMINI_API_KEY in env vars / .env
"""

import base64
import json
import os
import subprocess
import tempfile
from typing import Optional
from urllib.request import Request, ProxyHandler, build_opener
from urllib.error import HTTPError

from .base import TTSProvider, TTSResult


API_MODELS = {
    "gemini-3.1-flash-tts": "gemini-3.1-flash-tts-preview",
    "gemini-2.5-flash-tts": "gemini-2.5-flash-preview-tts",
    "gemini-2.5-pro-tts": "gemini-2.5-pro-preview-tts",
}

VOICES = {
    "Zephyr", "Puck", "Charon", "Kore", "Fenrir", "Leda", "Orus", "Aoede",
    "Callirrhoe", "Autonoe", "Enceladus", "Iapetus", "Umbriel", "Algieba",
    "Despina", "Erinome", "Algenib", "Rasalgethi", "Laomedeia", "Achernar",
    "Alnilam", "Schedar", "Gacrux", "Pulcherrima", "Achird", "Zubenelgenubi",
    "Vindemiatrix", "Sadachbia", "Sadaltager", "Sulafat",
}


class VertexTTSProvider(TTSProvider):
    """TTS via Google Vertex AI Gemini."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-3.1-flash-tts"):
        from .registry import _read_env_value
        self.api_key = (
            api_key
            or os.environ.get("VERTEX_API_KEY")
            or os.environ.get("GEMINI_API_KEY")
            or _read_env_value("VERTEX_API_KEY")
            or _read_env_value("GEMINI_API_KEY")
        )
        if not self.api_key:
            raise ValueError("VERTEX_API_KEY not set. Set it in .env or as env var.")
        self.model = model

    def _get_proxy_handler(self):
        for env_var in ["https_proxy", "HTTPS_PROXY", "http_proxy", "HTTP_PROXY", "all_proxy", "ALL_PROXY"]:
            proxy = os.environ.get(env_var)
            if proxy:
                return ProxyHandler({"http": proxy, "https": proxy})
        import socket
        for port in (7890, 7897, 1087):
            try:
                s = socket.create_connection(("127.0.0.1", port), timeout=1)
                s.close()
                return ProxyHandler({"http": f"http://127.0.0.1:{port}", "https": f"http://127.0.0.1:{port}"})
            except OSError:
                continue
        return ProxyHandler()

    def _pcm_to_mp3(self, pcm_path: str, mp3_path: str) -> bool:
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1",
                 "-i", pcm_path, "-b:a", "128k", mp3_path],
                capture_output=True, timeout=60,
            )
            return os.path.isfile(mp3_path)
        except Exception:
            return False

    def synthesize(
        self,
        text: str,
        output_path: str,
        voice: str = "Zephyr",
        language: str = "",
        speed: float = 1.0,
    ) -> Optional[TTSResult]:
        if not text:
            raise ValueError("Text cannot be empty")

        model_id = API_MODELS.get(self.model, self.model)
        endpoint = f"https://aiplatform.googleapis.com/v1/publishers/google/models/{model_id}:generateContent"

        payload = {
            "contents": [{"role": "user", "parts": [{"text": text}]}],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {"voiceName": voice}
                    }
                }
            }
        }

        url = f"{endpoint}?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        opener = build_opener(self._get_proxy_handler())

        try:
            req = Request(url, data=json.dumps(payload).encode(), headers=headers, method="POST")
            with opener.open(req, timeout=120) as resp:
                result = json.load(resp)
        except HTTPError as e:
            raise RuntimeError(f"Vertex API error {e.code}: {e.reason}")
        except Exception as e:
            raise RuntimeError(f"Vertex TTS failed: {e}")

        candidates = result.get("candidates", [])
        parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
        audio_b64 = (
            parts[0].get("inlineData", {}).get("data")
            or parts[0].get("binary", {}).get("data")
        ) if parts else None

        if not audio_b64:
            raise RuntimeError("No audio data in Vertex API response")

        audio_data = base64.b64decode(audio_b64)
        with tempfile.NamedTemporaryFile(suffix=".pcm", delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name

        try:
            if not self._pcm_to_mp3(tmp_path, output_path):
                raise RuntimeError("ffmpeg conversion failed")
            return TTSResult(
                output_path=os.path.abspath(output_path),
                provider="vertex-tts",
            )
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
