"""
analyzer_cli.py - CLI entry point for video-analyzer.

Usage:
    uv run va extract --file /path/to/video.mp4 [--output-dir /tmp/va_xxx] [--language zh]
    uv run va doctor [--region domestic|overseas]
    uv run va bootstrap [--region domestic|overseas]
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence

# Windows UTF-8 fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def existing_file_path(value: str) -> Path:
    path = Path(value)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"File not found: {value}")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="va",
        description="Video content analyzer: keyframe extraction + ASR transcription.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("setup", help="Download Whisper tiny model (run once after environment is ready)")

    doctor_parser = sub.add_parser("doctor", help="Inspect local video-analyze environment status")
    doctor_parser.add_argument(
        "--region",
        choices=["auto", "domestic", "overseas"],
        default="auto",
        help="Environment region hint (default: auto)",
    )

    bootstrap_parser = sub.add_parser("bootstrap", help="Initialize CPU-only video-analyze environment")
    bootstrap_parser.add_argument(
        "--region",
        choices=["auto", "domestic", "overseas"],
        default="auto",
        help="Environment region hint (default: auto)",
    )

    extract_parser = sub.add_parser("extract", help="Extract keyframes and transcribe audio")
    extract_parser.add_argument("--file", required=True, type=existing_file_path, help="Video file path")
    extract_parser.add_argument("--output-dir", default=None, help="Directory to save keyframe images (default: auto temp dir)")
    extract_parser.add_argument("--language", default="zh", help="ASR language code (default: zh)")

    return parser


def _run_command(cmd: list[str]) -> int:
    print(f"[va-bootstrap] $ {' '.join(cmd)}", file=sys.stderr)
    result = subprocess.run(cmd)
    return result.returncode


def _install_torch_for_region(region: str) -> int:
    if region == "domestic":
        return _run_command(["uv", "pip", "install", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple", "torch"])
    return _run_command(["uv", "pip", "install", "--index-url", "https://download.pytorch.org/whl/cpu", "torch"])


def _detect_region(region: str) -> str:
    if region != "auto":
        return region
    tz = Path("/etc/timezone").read_text(encoding="utf-8").strip() if Path("/etc/timezone").exists() else ""
    env_lang = os.environ.get("LANG") or os.environ.get("LC_ALL") or ""
    text = f"{tz} {env_lang}".lower()
    domestic_markers = ["shanghai", "beijing", "asia/shanghai", "zh_cn", "zh-cn", "chinese"]
    return "domestic" if any(m in text for m in domestic_markers) else "overseas"


def cmd_doctor(args: argparse.Namespace) -> int:
    from transcriber import find_tool

    region = _detect_region(args.region)
    ffmpeg = find_tool("ffmpeg")
    ffprobe = find_tool("ffprobe")
    uv_bin = shutil.which("uv")

    try:
        import torch  # type: ignore

        torch_ok = True
        torch_version = getattr(torch, "__version__", "unknown")
        cuda_available = bool(getattr(getattr(torch, "cuda", None), "is_available", lambda: False)())
    except Exception:
        torch_ok = False
        torch_version = None
        cuda_available = False

    try:
        import whisper  # type: ignore

        whisper_ok = True
    except Exception:
        whisper_ok = False

    whisper_cache = Path.home() / ".cache" / "whisper"
    model_ready = whisper_cache.exists() and any(whisper_cache.iterdir()) if whisper_cache.exists() else False

    result = {
        "region": region,
        "ffmpeg": bool(ffmpeg),
        "ffprobe": bool(ffprobe),
        "uv": bool(uv_bin),
        "torch_installed": torch_ok,
        "torch_version": torch_version,
        "torch_cuda_available": cuda_available,
        "whisper_installed": whisper_ok,
        "whisper_model_ready": model_ready,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_bootstrap(args: argparse.Namespace) -> int:
    region = _detect_region(args.region)
    print(f"[va-bootstrap] region={region}", file=sys.stderr)

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print(
            "[va-bootstrap] ffmpeg is missing. Install it first with a system package manager (for example: sudo apt install ffmpeg -y), then rerun bootstrap.",
            file=sys.stderr,
        )
        return 2

    commands = [
        ["uv", "sync"] if region != "domestic" else ["env", "UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple", "uv", "sync"],
    ]
    for cmd in commands:
        code = _run_command(cmd)
        if code != 0:
            return code

    code = _install_torch_for_region(region)
    if code != 0:
        return code

    if region == "domestic":
        commands = [
            ["uv", "pip", "install", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple", "openai-whisper"],
            ["uv", "run", "va", "setup"],
        ]
    else:
        commands = [
            ["uv", "pip", "install", "openai-whisper"],
            ["uv", "run", "va", "setup"],
        ]

    for cmd in commands:
        code = _run_command(cmd)
        if code != 0:
            return code
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    from extractor import extract_keyframes, get_video_duration

    video_path = str(args.file)

    # Step 1: Get duration
    print(f"[va] Analyzing: {video_path}", file=sys.stderr)
    duration = get_video_duration(video_path)
    if duration:
        print(f"[va] Duration: {duration:.1f}s ({duration/60:.1f}min)", file=sys.stderr)

    # Step 2: Extract keyframes
    print("[va] Extracting keyframes...", file=sys.stderr)
    try:
        frames = extract_keyframes(video_path, output_dir=args.output_dir, duration=duration)
        print(f"[va] Extracted {len(frames)} frames", file=sys.stderr)
    except RuntimeError as e:
        print(f"[va] Frame extraction failed: {e}", file=sys.stderr)
        frames = []

    # Step 3: ASR transcription (Whisper-only; setup guide on missing model/dependency)
    print("[va] Transcribing audio...", file=sys.stderr)
    transcript = ""
    audio_empty = False
    asr_method = "none"
    try:
        from transcriber import transcribe_video_fallback, get_setup_guide

        transcript, asr_method = transcribe_video_fallback(video_path, language=args.language)

        if transcript:
            print(f"[va] Transcript ({asr_method}): {len(transcript)} chars", file=sys.stderr)
        else:
            audio_empty = True
            if asr_method in ("no_whisper", "whisper_failed"):
                print(get_setup_guide(), file=sys.stderr)
            else:
                print("[va] No speech detected (silent or music-only)", file=sys.stderr)
    except Exception as e:
        audio_empty = True
        print(f"[va] ASR failed (non-fatal): {e}", file=sys.stderr)

    # Step 4: Output JSON to stdout
    result = {
        "frames": frames,
        "transcript": transcript,
        "duration": round(duration, 1) if duration else None,
        "audio_empty": audio_empty,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "setup":
            from transcriber import ensure_model

            ok = ensure_model()
            return 0 if ok else 1
        if args.command == "doctor":
            return cmd_doctor(args)
        if args.command == "bootstrap":
            return cmd_bootstrap(args)
        if args.command == "extract":
            return cmd_extract(args)
        raise RuntimeError(f"Unknown command: {args.command}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
