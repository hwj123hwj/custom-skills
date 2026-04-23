"""
Vertex provider — uses Google Vertex generateContent API for image generation.

Supported models:
- gemini-3.1-flash-image-preview  (Nanobanana 2, default — fast & cheap)
- gemini-3-pro-image-preview      (Nanobanana Pro — highest quality)

Requires:
- VERTEX_API_KEY (same key works for both Imagen and Gemini endpoints)

API endpoint: https://aiplatform.googleapis.com/v1/publishers/google/models/{model}:generateContent
"""

import base64
import json
import os
import time
import re
from typing import Optional
from urllib.request import Request, ProxyHandler, build_opener
from urllib.error import HTTPError

from .base import ImageProvider

API_BASE = "https://aiplatform.googleapis.com/v1/publishers/google/models"

MODELS = {
    "nanobanana2": "gemini-3.1-flash-image-preview",
    "nanobanana-pro": "gemini-3-pro-image-preview",
    # aliases
    "flash": "gemini-3.1-flash-image-preview",
    "pro": "gemini-3-pro-image-preview",
}

DEFAULT_MODEL_KEY = "nanobanana2"

SIZE_MAP = {
    "0.5K": "1K",
    "1024x1024": "1K",
    "1024x1792": "1K",
    "1792x1024": "1K",
    "2K": "2K",
    "4K": "4K",
}

# Supported aspect ratios for Vertex image generation
RATIO_SUPPORTED = {"1:1", "3:4", "4:3", "9:16", "16:9", "3:2", "2:3", "5:4", "4:5", "21:9"}


class VertexProvider(ImageProvider):
    """Image generation via Google Vertex generateContent API (Nanobanana series)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: int = 5,
    ):
        self.api_key = api_key or self._load_api_key()
        self.model = self._resolve_model(model)
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    @staticmethod
    def _resolve_model(model: Optional[str]) -> str:
        """Resolve model name from alias or full name."""
        if model is None:
            return MODELS[DEFAULT_MODEL_KEY]
        if model in MODELS:
            return MODELS[model]
        if model.startswith("gemini-"):
            return model
        raise ValueError(
            f"Unknown model '{model}'. Available: {', '.join(MODELS.keys())}"
        )

    def _load_api_key(self) -> Optional[str]:
        # 1. Environment variable
        key = os.environ.get("VERTEX_API_KEY")
        if key:
            return key

        # 2. Skill dir and project root (via registry)
        from .registry import get_env_files
        for env_path in get_env_files():
            key = self._read_env_file(env_path)
            if key:
                return key

        # 3. Config file
        config_path = os.path.expanduser("~/.config/image-provider/config.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                data = json.load(f)
            return data.get("vertex_api_key")

        return None

    @staticmethod
    def _read_env_file(path: str) -> Optional[str]:
        if not os.path.exists(path):
            return None
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip()
                if k in ("VERTEX_API_KEY", "VEXTEX_API_KEY"):
                    return v
        return None

    def generate(
        self,
        prompt: str,
        size: str,
        ratio: str,
        output_path: str,
    ) -> Optional[str]:
        if not self.api_key:
            print("  [vertex] No API key found.")
            print("     Add VERTEX_API_KEY=... to a .env file,")
            print("     or set VERTEX_API_KEY env var.")
            return None

        aspect_ratio = self._normalize_ratio(ratio)
        model_short = self.model.replace("gemini-", "").replace("-preview", "")
        print(f"  [vertex] model={self.model} ({model_short}) ratio={aspect_ratio}")

        for attempt in range(1, self.max_retries + 1):
            try:
                result = self._call_api(prompt, aspect_ratio, output_path, size)
                if result:
                    if attempt > 1:
                        print(f"  Succeeded on attempt {attempt}")
                    return result
            except Exception as e:
                print(f"  Attempt {attempt}/{self.max_retries} failed: {e}")
                if self._is_quota_error(e):
                    retry_after = self._extract_retry_after(str(e))
                    if retry_after:
                        print(f"  [vertex] Quota/rate limit hit. API suggests retry after about {retry_after}s.")
                    else:
                        print("  [vertex] Quota/rate limit hit. Check billing/quota for Gemini image models.")
                    return None

            if attempt < self.max_retries:
                print(f"  Retrying in {self.retry_delay}s...")
                time.sleep(self.retry_delay)

        print(f"  Failed after {self.max_retries} attempts")
        return None

    @staticmethod
    def _is_quota_error(error: Exception) -> bool:
        msg = str(error).lower()
        return "quota exceeded" in msg or "rate limit" in msg or "429" in msg

    @staticmethod
    def _extract_retry_after(message: str) -> Optional[int]:
        match = re.search(r"Please retry in ([0-9]+(?:\.[0-9]+)?)s", message)
        if not match:
            return None
        return int(float(match.group(1)))

    def _normalize_ratio(self, ratio: str) -> str:
        if ratio in RATIO_SUPPORTED:
            return ratio
        return "1:1"

    def _call_api(self, prompt: str, aspect_ratio: str, output_path: str, size: str = "1024x1024") -> Optional[str]:
        url = f"{API_BASE}/{self.model}:generateContent?key={self.api_key}"

        image_size = SIZE_MAP.get(size, "1K")

        payload = json.dumps({
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
                "imageConfig": {
                    "aspectRatio": aspect_ratio,
                    "imageSize": image_size,
                },
            },
        }).encode()

        req = Request(url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")

        opener = self._build_opener()

        try:
            with opener.open(req, timeout=180) as resp:
                data = json.loads(resp.read())
        except HTTPError as e:
            body = e.read().decode()
            try:
                err = json.loads(body)
                msg = err.get("error", {}).get("message", body[:300])
            except Exception:
                msg = body[:300]
            raise RuntimeError(f"API error {e.code}: {msg}")

        # Parse response: candidates[0].content.parts[].inlineData
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError(f"API returned no candidates: {json.dumps(data)[:300]}")

        parts = candidates[0].get("content", {}).get("parts", [])
        img_data = None
        for part in parts:
            inline = part.get("inlineData")
            if inline and inline.get("data"):
                img_data = inline
                break

        if not img_data:
            text_parts = [p.get("text", "") for p in parts if "text" in p]
            if text_parts:
                raise RuntimeError(f"No image generated. Model response: {' '.join(text_parts)[:300]}")
            raise RuntimeError("No image data in response")

        img_bytes = base64.b64decode(img_data["data"])
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(img_bytes)

        abs_path = os.path.abspath(output_path)
        print(f"  Generated image: {abs_path} ({len(img_bytes) // 1024}KB)")
        return abs_path

    def _build_opener(self):
        """Build URL opener with proxy support."""
        proxy_url = (
            os.environ.get("HTTPS_PROXY")
            or os.environ.get("https_proxy")
            or os.environ.get("ALL_PROXY")
            or os.environ.get("all_proxy")
        )
        if proxy_url:
            return build_opener(ProxyHandler({"https": proxy_url, "http": proxy_url}))

        import socket
        for port in (7890, 7897, 1087):
            try:
                s = socket.create_connection(("127.0.0.1", port), timeout=1)
                s.close()
                proxy = f"http://127.0.0.1:{port}"
                print(f"  [vertex] Auto-detected proxy at {proxy}")
                return build_opener(ProxyHandler({"https": proxy, "http": proxy}))
            except OSError:
                continue

        return build_opener()
