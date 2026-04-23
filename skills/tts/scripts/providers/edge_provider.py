"""
Edge TTS provider — Microsoft Edge's free TTS service.

No API key required. Supports 400+ voices across 70+ languages.
"""

import os
import subprocess
import sys
from typing import Optional

from .base import TTSProvider, TTSResult


class EdgeTTSProvider(TTSProvider):
    """TTS via Microsoft Edge TTS (free, no API key)."""

    def __init__(self):
        self._ensure_installed()

    def _ensure_installed(self):
        try:
            result = subprocess.run(
                ["edge-tts", "--version"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode != 0:
                raise RuntimeError("edge-tts not working")
        except FileNotFoundError:
            print("Installing edge-tts...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "edge-tts", "--break-system-packages"],
                capture_output=True, timeout=120,
            )

    def synthesize(
        self,
        text: str,
        output_path: str,
        voice: str = "zh-CN-XiaoxiaoNeural",
        language: str = "",
        speed: float = 1.0,
    ) -> Optional[TTSResult]:
        if not text:
            raise ValueError("Text cannot be empty")

        rate = f"+{int((speed - 1) * 100)}%" if speed > 1 else f"{int((speed - 1) * 100)}%" if speed < 1 else ""

        cmd = [
            "edge-tts",
            "-v", voice,
            "-t", text,
            "--write-media", output_path,
        ]
        if rate:
            cmd.extend(["--rate", rate])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(f"edge-tts failed: {result.stderr}")

        if not os.path.isfile(output_path):
            raise RuntimeError(f"edge-tts did not produce output file: {output_path}")

        return TTSResult(
            output_path=os.path.abspath(output_path),
            provider="edge-tts",
        )
