#!/usr/bin/env python3
"""
Unified TTS CLI — synthesize text to speech using pluggable providers.

Usage:
  python tts.py "你好世界" -o hello.mp3
  python tts.py "Hello" --provider edge-tts
  python tts.py "你好" --provider vertex-tts --voice Aoede

Provider is read from .env (DEFAULT_TTS_PROVIDER=edge-tts).
Override per-call with --provider.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from providers.registry import get_provider, PROVIDERS

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")

# Common voice presets for edge-tts
EDGE_PRESETS = {
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",
    "xiaoyi": "zh-CN-XiaoyiNeural",
    "yunjian": "zh-CN-YunjianNeural",
    "yuxuan": "zh-CN-YuxuanNeural",
    "shimmer": "zh-CN-ShimmerNeural",
    "guy": "zh-CN-YunxiNeural",
    "xiaomeng": "zh-CN-XiaomengNeural",
    "zhiyu": "zh-CN-ZhiyuNeural",
}


def main():
    parser = argparse.ArgumentParser(
        description="Text-to-Speech with pluggable providers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tts.py "你好世界" -o hello.mp3
  python tts.py "Hello" --provider edge-tts
  python tts.py "测试" --provider vertex-tts --voice Aoede
  python tts.py "旁白" --preset xiaoxiao --rate -5%
        """,
    )
    parser.add_argument("text", help="Text to convert to speech")
    parser.add_argument("--output", "-o", help="Output audio file path")
    parser.add_argument(
        "--provider", "-p",
        default=None,
        choices=list(PROVIDERS.keys()),
        help=f"TTS provider. Available: {', '.join(PROVIDERS.keys())}",
    )
    parser.add_argument("--voice", "-v", default=None, help="Voice name (provider-specific)")
    parser.add_argument("--preset", default=None,
        choices=list(EDGE_PRESETS.keys()),
        help="Voice preset (edge-tts only)")
    parser.add_argument("--language", "-l", default="", help="Language code")
    parser.add_argument("--rate", "-r", default=None,
        help="Speech rate (e.g. +20%% or -10%%, edge-tts only)")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")

    args = parser.parse_args()

    if not args.text:
        parser.error("Text is required")

    # Determine output path
    if args.output:
        output_path = os.path.abspath(args.output)
    else:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, "output.mp3")

    # Build kwargs
    kwargs = {}
    from providers.registry import get_default_provider_name
    provider_name = args.provider or get_default_provider_name()
    voice = args.voice or ""
    speed = 1.0

    if args.preset and provider_name == "edge-tts":
        voice = EDGE_PRESETS[args.preset]
    if args.rate and provider_name == "edge-tts":
        rate_str = args.rate.strip().replace("%", "")
        try:
            speed = 1.0 + int(rate_str) / 100.0
        except ValueError:
            pass

    if provider_name == "vertex-tts" and not voice:
        voice = "Zephyr"
    elif provider_name == "edge-tts" and not voice:
        voice = "zh-CN-XiaoxiaoNeural"

    provider = get_provider(provider_name)
    print(f"Text: {args.text[:80]}{'...' if len(args.text) > 80 else ''}")
    print(f"Provider: {type(provider).__name__}, Voice: {voice}")

    result = provider.synthesize(
        text=args.text,
        output_path=output_path,
        voice=voice,
        language=args.language,
        speed=speed,
    )

    if result:
        if args.json:
            print(f'{{"output_path": "{result.output_path}", "provider": "{result.provider}"}}')
        else:
            size_kb = os.path.getsize(result.output_path) / 1024
            print(f"Output: {result.output_path} ({size_kb:.1f} KB)")
    else:
        print("TTS failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
