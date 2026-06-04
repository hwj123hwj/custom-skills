#!/usr/bin/env python3
"""
whisper_transcriber.py - Local Whisper ASR (tiny model, no API key needed)

Uses openai-whisper with the "tiny" model (~75MB) for offline transcription.
First run auto-downloads the model from HuggingFace.
"""

from __future__ import annotations

import os
import sys
import tempfile
import subprocess
import shutil

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

_MODEL = "tiny"
_MODEL_SIZE_MB = 75


def _install_hint() -> str:
    return (
        "cd <WORKSPACE>/skills/video-analyze/scripts/video-analyzer && "
        "uv sync && "
        "uv pip install --index-url https://download.pytorch.org/whl/cpu torch && "
        "uv pip install openai-whisper && "
        "uv run va setup"
    )


def _find_tool(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    if sys.platform != "win32":
        for d in ["/opt/homebrew/bin", "/usr/local/bin", "/usr/bin"]:
            c = os.path.join(d, name)
            if os.path.isfile(c):
                if d not in os.environ.get("PATH", ""):
                    os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
                return c
        return None
    local_app = os.environ.get("LOCALAPPDATA", "")
    try:
        import pathlib
        winget_pkgs = pathlib.Path(local_app) / "Microsoft" / "WinGet" / "Packages"
        if winget_pkgs.exists():
            for pkg_dir in winget_pkgs.iterdir():
                for match in pkg_dir.rglob(f"{name}.exe"):
                    bin_dir = str(match.parent)
                    if bin_dir not in os.environ.get("PATH", ""):
                        os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
                    return str(match)
    except Exception:
        pass
    return None


def _extract_audio(video_path: str) -> str | None:
    ffmpeg = _find_tool("ffmpeg")
    if not ffmpeg:
        return None
    tmp_fd, tmp_audio = tempfile.mkstemp(suffix=".mp3", prefix="va_whisper_")
    os.close(tmp_fd)
    try:
        subprocess.run(
            [ffmpeg, "-i", video_path, "-vn", "-acodec", "libmp3lame",
             "-q:a", "4", "-ar", "16000", "-ac", "1", tmp_audio, "-y"],
            capture_output=True, check=True, timeout=300,
        )
        return tmp_audio
    except Exception:
        try:
            os.remove(tmp_audio)
        except OSError:
            pass
        return None


def is_available() -> bool:
    try:
        import whisper
        return True
    except ImportError:
        return False


def transcribe_with_whisper(video_path: str, language: str = "zh") -> tuple[str, bool]:
    """
    Transcribe video using local Whisper tiny model.

    Returns:
        (text, success):
            - (transcribed_text, True) on success
            - ("", False) if whisper not installed or transcription fails
    """
    try:
        import whisper
    except ImportError:
        print(f"[whisper] whisper not installed. Run: {_install_hint()}", file=sys.stderr)
        return "", False

    print(f"[whisper] Loading {_MODEL} model...", file=sys.stderr)

    try:
        model = whisper.load_model(_MODEL)
    except Exception as e:
        print(f"[whisper] Failed to load model: {e}", file=sys.stderr)
        return "", False

    audio_path = _extract_audio(video_path)
    if not audio_path:
        print("[whisper] Failed to extract audio (ffmpeg not available?)", file=sys.stderr)
        return "", False

    try:
        print(f"[whisper] Transcribing with language={language}...", file=sys.stderr)
        result = model.transcribe(audio_path, language=language, verbose=False)
        text = result.get("text", "").strip()

        if text:
            print(f"[whisper] Done: {len(text)} chars extracted", file=sys.stderr)
        else:
            print("[whisper] No speech detected", file=sys.stderr)

        return text, True
    except Exception as e:
        print(f"[whisper] Transcription error: {e}", file=sys.stderr)
        return "", False
    finally:
        try:
            os.remove(audio_path)
        except OSError:
            pass
