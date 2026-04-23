#!/usr/bin/env python3
"""
Image Generator — uses the built-in local providers only.

Usage:
  python generate_image.py "prompt" --size 1792x1024 -o output.png
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from providers.registry import get_provider, PROVIDERS

SIZE_TO_RATIO = {
    "1792x1024": "16:9",
    "1024x1792": "9:16",
    "1024x1024": "1:1",
    "0.5K": "1:1",
    "2K": "1:1",
    "4K": "1:1",
}

parser = argparse.ArgumentParser(description="Generate images")
parser.add_argument("prompt", help="Text prompt")
parser.add_argument("--output", "-o", help="Output file path")
parser.add_argument("--size", "-s", default="1024x1024",
                    choices=["0.5K", "1024x1024", "1024x1792", "1792x1024", "2K", "4K"])
parser.add_argument("--ratio", "-r", default=None,
                    choices=["1:1", "16:9", "9:16", "4:3", "3:4"])
parser.add_argument("--provider", "-P", default=None, choices=list(PROVIDERS.keys()))

args = parser.parse_args()
ratio = args.ratio or SIZE_TO_RATIO.get(args.size, "1:1")
output_path = args.output or f"output_{args.size.replace('x', '_')}.png"

provider = get_provider(args.provider)
print(f"Prompt: '{args.prompt}'")
print(f"Provider: {type(provider).__name__}, Ratio: {ratio}, Size: {args.size}")

result = provider.generate(prompt=args.prompt, size=args.size, ratio=ratio, output_path=output_path)
if result:
    print(f"IMAGE_RESULT: {result}")
else:
    print("❌ Image generation failed.")
    sys.exit(1)
