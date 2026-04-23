"""
Provider registry — maps provider names to classes, and loads default from config.

Config: .env file (DEFAULT_PROVIDER=vertex-imagen)
   or: ~/.config/image-provider/config.json {"default_provider": "dvcode"}

Default provider if no config: vertex-imagen
"""

import json
import os
from typing import Optional

from .base import ImageProvider
from .codex_provider import CodexProvider
from .dvcode_provider import DvcodeProvider
from .vertex_imagen_provider import VertexImagenProvider
from .vertex_provider import VertexProvider

PROVIDERS: dict[str, type[ImageProvider]] = {
    "dvcode": DvcodeProvider,
    "vertex-imagen": VertexImagenProvider,
    "vertex": VertexProvider,
    "codex": CodexProvider,
}

CONFIG_PATH = os.path.expanduser("~/.config/image-provider/config.json")
DEFAULT_PROVIDER = "vertex"


def _find_env_files() -> list[str]:
    """Collect candidate .env paths: skill dir and project root."""
    paths = []
    # 1. 技能本身的目录
    skill_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    paths.append(os.path.join(skill_dir, ".env"))

    # 2. 项目的根目录 (假设运行脚本时的当前工作目录就是项目根目录)
    project_root = os.getcwd()
    paths.append(os.path.join(project_root, ".env"))

    return [p for p in paths if os.path.isfile(p)]


def _read_env_value(key: str) -> Optional[str]:
    """Read a value from the nearest .env file containing the key."""
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


def get_env_files() -> list[str]:
    """Public: expose discovered .env paths (used by VertexImagenProvider)."""
    return _find_env_files()


def get_default_provider_name() -> str:
    """Read default provider from .env or config file."""
    # 1. .env file
    name = _read_env_value("DEFAULT_PROVIDER")
    if name and name in PROVIDERS:
        return name

    # 2. Config file
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


def get_provider(name: Optional[str] = None, model: Optional[str] = None) -> ImageProvider:
    """Instantiate and return a provider by name, optionally with a model override."""
    provider_name = name or get_default_provider_name()
    cls = PROVIDERS.get(provider_name)
    if cls is None:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown provider '{provider_name}'. Available: {available}")
    # Pass model to providers that support it (VertexProvider)
    if model and provider_name == "vertex":
        return cls(model=model)
    return cls()
