# Image Provider

Unified image generation skill with pluggable providers (strategy pattern).

## Supported Providers

| Provider | Backend | Auth | Notes |
|----------|---------|------|-------|
| `vertex-imagen` | Google Vertex AI Imagen 3 | API Key | Personal, portable |
| `dvcode` | dvcode CLI /nanobanana | Git auth | Company tool |

## Quick Start

```bash
# Generate inline image
python3 scripts/generate.py "a futuristic city" --size 1792x1024 -o image.png

# Generate cover from title
python3 scripts/generate.py --mode cover --title "My Article" -o cover.png

# Use specific provider
python3 scripts/generate.py "prompt" --provider dvcode
```

## Configuration

Edit `.env` in this directory:

```env
# API Key for Vertex AI Imagen
VERTEX_API_KEY=your_key_here

# Default provider
DEFAULT_PROVIDER=vertex-imagen
```

## Architecture

```
image-provider/
├── .env                          # API keys + default provider
├── SKILL.md                      # Skill metadata
├── README.md                     # This file
├── outputs/                      # Default output directory
└── scripts/
    ├── generate.py               # Unified CLI entry point
    └── providers/
        ├── base.py               # ImageProvider abstract interface
        ├── dvcode_provider.py    # dvcode implementation
        ├── vertex_imagen_provider.py  # Vertex AI Imagen implementation
        └── registry.py           # Provider registry + config loading
```

## Adding a New Provider

1. Create `scripts/providers/myservice_provider.py`
2. Subclass `ImageProvider`, implement `generate()`
3. Add to `PROVIDERS` dict in `registry.py`
4. Add API key loading logic if needed

Example skeleton:

```python
from .base import ImageProvider

class MyServiceProvider(ImageProvider):
    def generate(self, prompt, size, ratio, output_path):
        # call API, save image to output_path
        return output_path  # or None on failure
```

## Dependencies

```bash
pip install requests  # only needed for dvcode provider
```

Vertex AI Imagen provider uses only stdlib (`urllib`, `json`, `base64`).
