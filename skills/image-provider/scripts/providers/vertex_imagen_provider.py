"""
Vertex AI Imagen provider — uses Google Vertex AI Imagen API to generate images.

Requires:
- VERTEX_API_KEY in any .env file along the directory chain, or
- VERTEX_API_KEY environment variable, or
- ~/.config/image-provider/config.json with {"vertex_api_key": "..."}

Supported models:
- imagen-3.0-generate-002 (default, high quality)
- imagen-3.0-generate-001 (older version)

API docs: https://cloud.google.com/vertex-ai/generative-ai/docs/image/generate-images
"""

import base64
import json
import os
import time
from typing import Optional
from urllib.request import Request, ProxyHandler, build_opener
from urllib.error import HTTPError

from .base import ImageProvider

API_ENDPOINT = "https://aiplatform.googleapis.com/v1/publishers/google/models"
DEFAULT_MODEL = "imagen-3.0-generate-002"

# Imagen 3 supported aspect ratios: 1:1, 3:4, 4:3, 9:16, 16:9
RATIO_SUPPORTED = {"1:1", "3:4", "4:3", "9:16", "16:9"}


class VertexImagenProvider(ImageProvider):
    """Image generation via Google Vertex AI Imagen API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        max_retries: int = 3,
        retry_delay: int = 5,
    ):
        self.api_key = api_key or self._load_api_key()
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _load_api_key(self) -> Optional[str]:
        # 1. 环境变量
        key = os.environ.get("VERTEX_API_KEY")
        if key:
            return key

        # 2. 读取 registry 找出来的 .env (只查当前技能和项目根目录)
        from .registry import get_env_files
        for env_path in get_env_files():
            key = self._read_env_file(env_path)
            if key:
                return key

        # 3. 配置文件
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
                k = k.strip()
                v = v.strip()
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
            print("  ❌ [vertex-imagen] No API key found.")
            print("     Add VERTEX_API_KEY=... to a .env file in the skill directory,")
            print("     or set VERTEX_API_KEY env var,")
            print("     or add vertex_api_key to ~/.config/image-provider/config.json")
            return None

        aspect_ratio = self._normalize_ratio(ratio)
        print(f"  [vertex-imagen] model={self.model} ratio={aspect_ratio}")

        for attempt in range(1, self.max_retries + 1):
            try:
                result = self._call_api(prompt, aspect_ratio, output_path)
                if result:
                    if attempt > 1:
                        print(f"  ✅ Succeeded on attempt {attempt}")
                    return result
            except Exception as e:
                print(f"  ⚠️  Attempt {attempt}/{self.max_retries} failed: {e}")

            if attempt < self.max_retries:
                print(f"  Retrying in {self.retry_delay}s...")
                time.sleep(self.retry_delay)

        print(f"  ❌ Failed after {self.max_retries} attempts")
        return None

    def _normalize_ratio(self, ratio: str) -> str:
        if ratio in RATIO_SUPPORTED:
            return ratio
        return "1:1"

    def _call_api(self, prompt: str, aspect_ratio: str, output_path: str) -> Optional[str]:
        url = f"{API_ENDPOINT}/{self.model}:predict?key={self.api_key}"
        payload = json.dumps({
            "instances": [{"prompt": prompt}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": aspect_ratio,
            },
        }).encode()

        req = Request(url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")

        opener = self._build_opener()

        try:
            with opener.open(req, timeout=120) as resp:
                data = json.loads(resp.read())
        except HTTPError as e:
            body = e.read().decode()
            try:
                err = json.loads(body)
                msg = err.get("error", {}).get("message", body[:300])
            except Exception:
                msg = body[:300]
            raise RuntimeError(f"API error {e.code}: {msg}")

        predictions = data.get("predictions", [])
        if not predictions:
            raise RuntimeError("API returned no predictions")

        img_b64 = predictions[0].get("bytesBase64Encoded")
        if not img_b64:
            raise RuntimeError("No image data in response")

        img_bytes = base64.b64decode(img_b64)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(img_bytes)

        abs_path = os.path.abspath(output_path)
        print(f"  Generated image: {abs_path} ({len(img_bytes) // 1024}KB)")
        return abs_path

    def _build_opener(self):
        """Build URL opener with proxy support.

        Priority: HTTPS_PROXY env var > common local proxy ports (7890, 7897, 1087).
        Falls back to direct connection if no proxy found.
        """
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
                print(f"  [vertex-imagen] Auto-detected proxy at {proxy}")
                return build_opener(ProxyHandler({"https": proxy, "http": proxy}))
            except OSError:
                continue

        return build_opener()
