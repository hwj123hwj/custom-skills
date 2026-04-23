#!/usr/bin/env python3
"""
Unified image generation CLI.

Usage:
  python generate.py "prompt" -o output.png
  python generate.py "prompt" --size 1792x1024 --provider vertex-imagen
  python generate.py "prompt" --mode cover --title "Article Title"

Provider is read from .env (DEFAULT_PROVIDER) or ~/.config/image-provider/config.json.
Override per-call with --provider.
"""

import argparse
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from providers.registry import get_provider, PROVIDERS

SIZE_TO_RATIO = {
    "1792x1024": "16:9",
    "1024x1792": "9:16",
    "1024x1024": "1:1",
    "0.5K":      "1:1",
    "2K":        "1:1",
    "4K":        "1:1",
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")


def main():
    parser = argparse.ArgumentParser(
        description="Generate images (inline or cover)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Inline image
  python generate.py "a futuristic city at sunset" -o img.png

  # Cover image (auto-generates prompt from title)
  python generate.py --mode cover --title "My Article Title" -o cover.png

  # Specify provider
  python generate.py "landscape" --size 1792x1024 --provider dvcode

  # Quick preview
  python generate.py "test" --size 0.5K
        """,
    )
    parser.add_argument("prompt", nargs="?", default=None, help="Text prompt (required for image mode)")
    parser.add_argument(
        "--mode", "-m",
        default="image",
        choices=["image", "cover"],
        help="Generation mode: 'image' for inline, 'cover' for article cover (default: image)",
    )
    parser.add_argument("--title", "-t", help="Article title (used in cover mode to auto-generate prompt)")
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: auto-generated in outputs/)",
    )
    parser.add_argument(
        "--size", "-s",
        default="1024x1024",
        choices=["0.5K", "1024x1024", "1024x1792", "1792x1024", "2K", "4K"],
        help="Image size (default: 1024x1024)",
    )
    parser.add_argument(
        "--ratio", "-r",
        default=None,
        choices=["1:1", "16:9", "9:16", "4:3", "3:4"],
        help="Aspect ratio (default: inferred from --size)",
    )
    parser.add_argument(
        "--provider", "-p",
        default=None,
        choices=list(PROVIDERS.keys()),
        help=f"Image provider. Available: {', '.join(PROVIDERS.keys())}",
    )

    parser.add_argument(
        "--model",
        default=None,
        help="Model name for vertex provider (nanobanana2, nanobanana-pro, flash, pro). Default: nanobanana2",
    )

    args = parser.parse_args()

    # Determine prompt
    if args.mode == "cover":
        if not args.title and not args.prompt:
            parser.error("Cover mode requires --title or a prompt")
        prompt = args.prompt or f"{args.title} cover image, editorial style"
    else:
        if not args.prompt:
            parser.error("Image mode requires a prompt")
        prompt = args.prompt

    ratio = args.ratio or SIZE_TO_RATIO.get(args.size, "1:1")

    # Determine output path
    if args.output:
        output_path = os.path.abspath(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ratio_str = ratio.replace(":", "x")
        prefix = "cover" if args.mode == "cover" else "image"
        filename = f"{prefix}_{timestamp}_{ratio_str}.png"
        output_path = os.path.abspath(os.path.join(OUTPUT_DIR, filename))

    provider = get_provider(args.provider, model=args.model)

    if args.mode == "cover" and args.title:
        print(f"Title: '{args.title}'")
    print(f"Prompt: '{prompt}'")
    print(f"Provider: {type(provider).__name__}, Ratio: {ratio}, Size: {args.size}")

    result = provider.generate(
        prompt=prompt,
        size=args.size,
        ratio=ratio,
        output_path=output_path,
    )

    if result:
        print(f"IMAGE_RESULT: {result}")
    else:
        print("\u274c Image generation failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
