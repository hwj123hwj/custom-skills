#!/usr/bin/env python3
"""
transcriber.py - Audio transcription via local Whisper (tiny model, offline)

Usage: python3 transcriber.py <audio_file> [--language zh]

First run auto-downloads the tiny model (~75MB) from HuggingFace.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

MODEL = "tiny"


# ─── Find tool ───────────────────────────────────────────

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


def find_tool(name: str) -> str | None:
    """Public wrapper used by other modules (e.g. extractor.py)."""
    return _find_tool(name)


# ─── Extract audio from video ────────────────────────────

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


def _install_hint() -> str:
    return (
        "cd <WORKSPACE>/skills/video-analyze/scripts/video-analyzer && "
        "uv sync && "
        "uv pip install --index-url https://download.pytorch.org/whl/cpu torch && "
        "uv pip install openai-whisper && "
        "uv run va setup"
    )


# ─── Ensure model downloaded ─────────────────────────────

def ensure_model() -> bool:
    """Download Whisper tiny model if not already cached. Returns True on success."""
    try:
        import whisper
    except ImportError:
        print(
            f"[transcribe] whisper not installed. Run: {_install_hint()}",
            file=sys.stderr,
        )
        return False

    print(f"[transcribe] Checking Whisper {MODEL} model...", file=sys.stderr)
    try:
        whisper.load_model(MODEL)
        print(f"[transcribe] Whisper {MODEL} model ready.", file=sys.stderr)
        return True
    except Exception as e:
        print(f"[transcribe] Failed to load/download model: {e}", file=sys.stderr)
        return False


# ─── Transcribe ──────────────────────────────────────────

def transcribe_video(video_path: str, language: str = "zh") -> str:
    """Transcribe video using local Whisper tiny model. Returns transcript text."""
    try:
        import whisper
    except ImportError:
        print(
            f"[transcribe] whisper not installed. Run: {_install_hint()}",
            file=sys.stderr,
        )
        return ""

    print(f"[transcribe] Loading Whisper {MODEL} model...", file=sys.stderr)
    try:
        model = whisper.load_model(MODEL)
    except Exception as e:
        print(f"[transcribe] Failed to load model: {e}", file=sys.stderr)
        return ""

    audio_path = _extract_audio(video_path)
    if not audio_path:
        print("[transcribe] Failed to extract audio (ffmpeg not available?)", file=sys.stderr)
        return ""

    try:
        print(f"[transcribe] Transcribing (language={language})...", file=sys.stderr)
        result = model.transcribe(audio_path, language=language, verbose=False)
        text = result.get("text", "").strip()
        if text:
            print(f"[transcribe] Done: {len(text)} chars", file=sys.stderr)
        else:
            print("[transcribe] No speech detected", file=sys.stderr)
        return text
    except Exception as e:
        print(f"[transcribe] Transcription error: {e}", file=sys.stderr)
        return ""
    finally:
        try:
            os.remove(audio_path)
        except OSError:
            pass


def transcribe_video_fallback(video_path: str, language: str = "zh") -> tuple[str, str]:
    """
    Adapter for analyzer_cli.py.
    Returns (text, method) where method is "whisper" or "no_whisper".
    """
    try:
        import whisper  # noqa: F401
    except ImportError:
        return "", "no_whisper"

    text = transcribe_video(video_path, language)
    return text, "whisper"


def get_setup_guide() -> str:
    return (
        "\n[va] ⚠️  Whisper is not ready. Run:\n"
        "[va]   cd <WORKSPACE>/skills/video-analyze/scripts/video-analyzer\n"
        "[va]   uv sync\n"
        "[va]   uv pip install --index-url https://download.pytorch.org/whl/cpu torch\n"
        "[va]   uv pip install openai-whisper\n"
        "[va]   uv run va setup\n"
        "[va]\n"
        "[va] This skill is CPU-only by default; do not install CUDA-enabled torch packages on lightweight servers.\n"
        "[va] Then retry the analysis. Video will be analyzed from visuals only for now.\n"
    )


# ─── Main ────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe video via local Whisper")
    parser.add_argument("file", help="Video or audio file path")
    parser.add_argument("--language", default="zh", help="Language code (default: zh)")
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    text = transcribe_video(args.file, args.language)
    print(text)
