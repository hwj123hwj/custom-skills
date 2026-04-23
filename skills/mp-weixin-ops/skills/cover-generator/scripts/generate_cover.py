#!/usr/bin/env python3
"""
Cover Generator — delegates to image-provider shared skill if available,
otherwise uses the built-in providers.

Usage:
  python generate_cover.py "Article Title" -o cover.png
"""

import argparse
import os
import sys


def find_shared_skill(name: str) -> str:
    """Find a shared skill (image-provider) by walking up from this script."""
    d = os.path.abspath(os.path.dirname(__file__))
    for _ in range(10):
        candidate = os.path.join(d, name, "scripts")
        if os.path.isdir(candidate):
            return candidate
        candidate = os.path.join(d, ".claude", "skills", name, "scripts")
        if os.path.isdir(candidate):
            return candidate
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return ""


# Parse our args first (before forwarding)
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("title")
parser.add_argument("--prompt", default=None)
parser.add_argument("--output", "-o", default=None)
parser.add_argument("--size", "-s", default="1024x1024")
parser.add_argument("--ratio", "-r", default=None)
parser.add_argument("--provider", "-p", default=None)
args, _ = parser.parse_known_args()

SHARED = find_shared_skill("image-provider")

if SHARED:
    # Shared skill found — rewrite args for generate.py
    new_argv = [os.path.join(SHARED, "generate.py")]
    if args.prompt:
        new_argv.append(args.prompt)
    new_argv.extend(["--mode", "cover", "--title", args.title])
    new_argv.extend(["--size", args.size])
    if args.ratio:
        new_argv.extend(["--ratio", args.ratio])
    if args.provider:
        new_argv.extend(["--provider", args.provider])
    if args.output:
        new_argv.extend(["--output", args.output])
    sys.argv = new_argv
    sys.path.insert(0, SHARED)
    exec(open(sys.argv[0]).read())
else:
    # Use built-in providers (shared with image-generator)
    builtin = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..", "image-generator", "scripts"
    ))
    sys.path.insert(0, builtin)
    from providers.registry import get_provider, PROVIDERS

    SIZE_TO_RATIO = {
        "1792x1024": "16:9",
        "1024x1792": "9:16",
        "1024x1024": "1:1",
        "0.5K": "1:1",
        "2K": "1:1",
        "4K": "1:1",
    }

    prompt = args.prompt or f"{args.title} cover image, editorial style"
    ratio = args.ratio or SIZE_TO_RATIO.get(args.size, "1:1")
    output_path = args.output or "cover.png"

    provider = get_provider(args.provider)
    print(f"Title: '{args.title}'")
    print(f"Prompt: '{prompt}'")
    print(f"Provider: {type(provider).__name__}, Ratio: {ratio}, Size: {args.size}")

    result = provider.generate(prompt=prompt, size=args.size, ratio=ratio, output_path=output_path)
    if result:
        print(f"IMAGE_RESULT: {result}")
    else:
        print("❌ Cover generation failed.")
        sys.exit(1)
