"""
Provider registry — maps provider names to classes, and loads default from config.

Config: .env file (DEFAULT_TTS_PROVIDER=edge-tts)
   or: ~/.config/tts/config.json {"default_provider": "edge-tts"}

Default provider if no config: edge-tts
"""

import json
import os
from typing import Optional

from .base import TTSProvider
from .edge_provider import EdgeTTSProvider
from .vertex_provider import VertexTTSProvider

PROVIDERS: dict[str, type[TTSProvider]] = {
    "edge-tts": EdgeTTSProvider,
    "vertex-tts": VertexTTSProvider,
}

CONFIG_PATH = os.path.expanduser("~/.config/tts/config.json")
DEFAULT_PROVIDER = "edge-tts"


def _find_env_files() -> list[str]:
    paths = []
    # 1. 技能本身的目录 (tts/)
    skill_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    paths.append(os.path.join(skill_dir, ".env"))

    # 2. 项目的根目录 (假设运行脚本时的当前工作目录就是项目根目录)
    project_root = os.getcwd()
    paths.append(os.path.join(project_root, ".env"))

    # 过滤掉不存在的文件
    return [p for p in paths if os.path.isfile(p)]


def _read_env_value(key: str) -> Optional[str]:
    for path in _find_env_files():
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == key:
                    return v.strip()
    return None


def get_default_provider_name() -> str:
    name = _read_env_value("DEFAULT_TTS_PROVIDER")
    if name and name in PROVIDERS:
        return name
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as f:
                data = json.load(f)
            name = data.get("default_provider", DEFAULT_PROVIDER)
            if name in PROVIDERS:
                return name
        except Exception:
            pass
    return DEFAULT_PROVIDER


def get_provider(name: Optional[str] = None, **kwargs) -> TTSProvider:
    provider_name = name or get_default_provider_name()
    cls = PROVIDERS.get(provider_name)
    if cls is None:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown provider '{provider_name}'. Available: {available}")
    return cls(**kwargs)
