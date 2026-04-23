---
name: image-generator
description: |
  Generate images for WeChat articles using dvcode command-line tool.
  Called by article-writer after article completion.
---

# Image Generator

Generate inline images for WeChat Official Account articles using dvcode.

This skill does **not** decide by itself whether an article should have images. The agent must make that decision first, then call `generate_image.py` for each approved image.

## Use Cases

- Triggered by article-writer after it decides inline images are needed
- User explicitly requests "add images to this article"
- Generate specific image with custom prompt

## Prerequisites

dvcode requires:
1. Running in a directory with Git configured (for company project authentication)
2. Valid Git remote pointing to company GitLab

Recommended working directory: `dvcode_pictures/`

## Usage

```bash
# Basic usage
python3 ${SKILL_DIR}/scripts/generate_image.py "a futuristic city at sunset"

# With size
python3 ${SKILL_DIR}/scripts/generate_image.py "blue gradient" --size 0.5K

# With output path
python3 ${SKILL_DIR}/scripts/generate_image.py "landscape" -o output.png
```

## Parameters

| Parameter | Description | Default |
|---|---|---|
| `prompt` | Text prompt (required) | - |
| `--size`, `-s` | Image size: `0.5K`, `1024x1024`, `1024x1792`, `1792x1024`, `2K`, `4K` | `1024x1024` |
| `--ratio`, `-r` | Aspect ratio: `1:1`, `16:9`, `9:16`, `4:3`, `3:4` (inferred from `--size` if not set) | auto |
| `--output`, `-o` | Output file path | `outputs/pending.png` |

## Image Sizes

| Size | dvcode Mapping | Aspect Ratio |
|------|----------------|-------------|
| `0.5K` | `0.5k` | 1:1 (preview) |
| `1024x1024` | `1k` | 1:1 square |
| `1024x1792` | `1k` | 9:16 portrait |
| `1792x1024` | `1k` | 16:9 landscape |
| `2K` | `2k` | 1:1 square |
| `4K` | `2k` | 1:1 square |

## Script Directory

| Script | Purpose |
|--------|---------|
| `scripts/generate_image.py` | Generate single image |

## Dependencies

```bash
pip install requests
```
