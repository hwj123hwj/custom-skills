"""
Codex provider — uses the local `codex` CLI tool (ChatGPT OAuth) to generate images.

Requires:
- codex CLI installed at ~/.npm-global/bin/codex
- Authenticated via ChatGPT OAuth (~/.codex/auth.json, auth_mode: "chatgpt")
- Do NOT set OPENAI_API_KEY — it overrides OAuth and breaks generation
- Proxy: http://127.0.0.1:7890 (auto-used)
"""

import os
import shutil
import subprocess
import time
from typing import Optional

from .base import ImageProvider

CODEX_BIN = os.path.expanduser("~/.npm-global/bin/codex")
GENERATED_DIR = os.path.expanduser("~/.codex/generated_images")
PROXY = "http://127.0.0.1:7890"
TIMEOUT = 120


class CodexProvider(ImageProvider):
    """Image generation via OpenAI Codex CLI (gpt-image)."""

    def generate(
        self,
        prompt: str,
        size: str,
        ratio: str,
        output_path: str,
    ) -> Optional[str]:
        if not os.path.isfile(CODEX_BIN):
            print(f"  ❌ [codex] codex CLI not found at {CODEX_BIN}")
            return None

        print(f"  [codex] prompt={prompt[:60]}...")

        # Record the latest image before generation to detect new ones
        before = self._latest_image()
        before_mtime = os.path.getmtime(before) if before else 0

        env = os.environ.copy()
        # Proxy — codex 内部的 Rust reqwest 只认大写变量
        env["HTTPS_PROXY"] = PROXY
        env["HTTP_PROXY"] = PROXY
        env["https_proxy"] = PROXY
        env["http_proxy"] = PROXY
        # Make sure codex bin is in PATH
        env["PATH"] = f"{os.path.expanduser('~/.npm-global/bin')}:{env.get('PATH', '')}"
        # Unset OPENAI_API_KEY to ensure OAuth mode is used
        env.pop("OPENAI_API_KEY", None)

        cmd = [
            CODEX_BIN,
            "exec",
            "--sandbox", "danger-full-access",
            "--skip-git-repo-check",
            f"Generate an image: {prompt}. Save it as /tmp/codex-gen/output.png",
        ]

        try:
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=TIMEOUT,
            )
            if result.returncode != 0:
                print(f"  ❌ [codex] CLI error: {result.stderr[:300]}")
                return None
        except subprocess.TimeoutExpired:
            print(f"  ❌ [codex] Timed out after {TIMEOUT}s")
            return None
        except Exception as e:
            print(f"  ❌ [codex] Failed: {e}")
            return None

        # Locate the newly generated image
        src = self._latest_image()
        if not src or (os.path.getmtime(src) <= before_mtime):
            print("  ❌ [codex] No new image found after generation")
            return None

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        shutil.copy2(src, output_path)

        abs_path = os.path.abspath(output_path)
        size_kb = os.path.getsize(abs_path) // 1024
        print(f"  Generated image: {abs_path} ({size_kb}KB)")
        return abs_path

    @staticmethod
    def _latest_image() -> Optional[str]:
        """Find the most recently modified PNG under ~/.codex/generated_images/."""
        if not os.path.isdir(GENERATED_DIR):
            return None
        candidates = []
        for root, _, files in os.walk(GENERATED_DIR):
            for f in files:
                if f.lower().endswith(".png"):
                    full = os.path.join(root, f)
                    candidates.append((os.path.getmtime(full), full))
        if not candidates:
            return None
        return max(candidates)[1]
