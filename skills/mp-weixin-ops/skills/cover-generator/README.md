# Cover Generator

Generate cover images for WeChat Official Account articles using dvcode command-line tool.

## Prerequisites

dvcode requires:
1. Running in a directory with Git configured (for company project authentication)
2. Valid Git remote pointing to company GitLab

Recommended working directory: `dvcode_pictures/`

## Usage

```bash
# Basic usage
python3 ${SKILL_DIR}/scripts/generate_cover.py "Article Title"

# With custom prompt
python3 ${SKILL_DIR}/scripts/generate_cover.py "Tech Article" \
  --prompt "futuristic blue theme" -o cover.png

# With size
python3 ${SKILL_DIR}/scripts/generate_cover.py "Lifestyle Article" --size 1792x1024 -o cover.png
```

## Parameters

| Parameter | Description | Default |
|---|---|---|
| `title` | Article title (required) | - |
| `--prompt`, `-p` | Custom prompt (auto-generated from title if not provided) | - |
| `--size`, `-s` | Image size: `0.5K`, `1024x1024`, `1024x1792`, `1792x1024`, `2K`, `4K` | `1024x1024` |
| `--ratio`, `-r` | Aspect ratio: `1:1`, `16:9`, `9:16`, `4:3`, `3:4` (inferred from `--size` if not set) | auto |
| `--output`, `-o` | Output file path | `outputs/cover.png` |

## Image Sizes

| Size | dvcode Mapping | Aspect Ratio |
|------|----------------|-------------|
| `0.5K` | `0.5k` | 1:1 (preview) |
| `1024x1024` | `1k` | 1:1 square |
| `1024x1792` | `1k` | 9:16 portrait |
| `1792x1024` | `1k` | 16:9 landscape |
| `2K` | `2k` | 1:1 square |
| `4K` | `2k` | 1:1 square |

## Dependencies

```bash
pip install requests
```
