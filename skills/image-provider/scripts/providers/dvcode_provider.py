"""
dvcode provider — uses the local `dvcode` CLI tool with /nanobanana command.

Requires:
- dvcode CLI installed and authenticated (Git-based company auth)
- Running in a directory with a valid Git remote (dvcode_pictures/ recommended)
"""

import json
import os
import subprocess
import time
from typing import Optional

import requests

from .base import ImageProvider

SIZE_MAP = {
    "0.5K":      "0.5k",
    "1024x1024": "1k",
    "1024x1792": "1k",
    "1792x1024": "1k",
    "2K":        "2k",
    "4K":        "2k",
}


class DvcodeProvider(ImageProvider):
    """Image generation via dvcode CLI (/nanobanana command)."""

    def __init__(self, max_retries: int = 3, retry_delay: int = 10):
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def generate(
        self,
        prompt: str,
        size: str,
        ratio: str,
        output_path: str,
    ) -> Optional[str]:
        dvcode_size = SIZE_MAP.get(size, "1k")
        cmd = [
            "dvcode",
            "--output-format", "stream-json",
            "--yolo",
            f"/nanobanana {ratio} {dvcode_size} {prompt}",
        ]

        print(f"  [dvcode] ratio={ratio} size={dvcode_size}")

        for attempt in range(1, self.max_retries + 1):
            try:
                result = self._run_once(cmd, output_path)
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

    def _run_once(self, cmd: list, output_path: str) -> Optional[str]:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        image_url = None
        for line in process.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if data.get("type") == "nanobanana_completed":
                urls = data.get("image_urls", [])
                if urls:
                    image_url = urls[0].strip()
                    break

        # fallback: some versions write to stderr
        if not image_url:
            for line in process.stderr:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if data.get("type") == "nanobanana_completed":
                    urls = data.get("image_urls", [])
                    if urls:
                        image_url = urls[0].strip()
                        break

        process.wait()

        if not image_url:
            print(f"  ❌ dvcode returned no image URL")
            return None

        print(f"  Generated image URL: {image_url}")

        resp = requests.get(image_url, timeout=60)
        resp.raise_for_status()

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(resp.content)

        return os.path.abspath(output_path)
