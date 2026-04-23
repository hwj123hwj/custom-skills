#!/usr/bin/env python3
"""
Unified ASR CLI — transcribe audio files using pluggable providers.

Usage:
  python transcribe.py audio.wav
  python transcribe.py video.mp4 --provider siliconflow
  python transcribe.py video.mp4 --language auto --json
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from providers.registry import get_provider, PROVIDERS

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")


def extract_audio(media_path: str) -> str:
    """Extract audio from video/audio file to 16kHz mono WAV."""
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", media_path,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            tmp.name,
        ],
        capture_output=True,
    )
    if not os.path.isfile(tmp.name) or os.path.getsize(tmp.name) < 100:
        os.unlink(tmp.name)
        raise RuntimeError("Failed to extract audio")
    return tmp.name


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio/video files using ASR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic transcription
  python transcribe.py video.mp4

  # Specify language
  python transcribe.py audio.wav --language en

  # JSON output
  python transcribe.py video.mp4 --json

  # Specify provider
  python transcribe.py video.mp4 --provider siliconflow
        """,
    )
    parser.add_argument("input", help="Audio or video file path")
    parser.add_argument(
        "--language", "-l",
        default="zh",
        help="Language code (zh, en, ja, auto, etc.) (default: zh)",
    )
    parser.add_argument(
        "--provider", "-p",
        default=None,
        choices=list(PROVIDERS.keys()),
        help=f"ASR provider. Available: {', '.join(PROVIDERS.keys())}",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON",
    )

    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    if not os.path.isfile(input_path):
        parser.error(f"File not found: {input_path}")

    # Extract audio if needed (mp4, mkv, etc.)
    ext = os.path.splitext(input_path)[1].lower()
    if ext not in (".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"):
        print(f"Extracting audio from {ext}...")
        audio_path = extract_audio(input_path)
        cleanup = True
    else:
        audio_path = input_path
        cleanup = False

    try:
        provider = get_provider(args.provider)
        print(f"Transcribing: {os.path.basename(input_path)}")
        print(f"Provider: {type(provider).__name__}, Language: {args.language}")

        result = provider.transcribe(audio_path, language=args.language)

        if result is None:
            print("No speech detected.")
            if args.json:
                print(json.dumps({"text": "", "language": args.language, "provider": type(provider).__name__}))
            sys.exit(0)

        if args.json:
            output = {
                "text": result.text,
                "language": result.language,
                "provider": result.provider,
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            print(f"\n{result.text}")

    finally:
        if cleanup:
            os.unlink(audio_path)


if __name__ == "__main__":
    main()
