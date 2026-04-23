"""
Provider registry — maps provider names to classes, and loads default from config.

Config: .env file (DEFAULT_ASR_PROVIDER=siliconflow)
   or: ~/.config/asr/config.json {"default_provider": "siliconflow"}

Default provider if no config: siliconflow
"""

import json
import os
from typing import Optional

from .base import ASRProvider
from .siliconflow_provider import SiliconFlowASRProvider

PROVIDERS: dict[str, type[ASRProvider]] = {
    "siliconflow": SiliconFlowASRProvider,
}

CONFIG_PATH = os.path.expanduser("~/.config/asr/config.json")
DEFAULT_PROVIDER = "siliconflow"


def _find_env_files() -> list[str]:
    paths = []
    # 1. 技能本身的目录 (asr/)
    skill_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    paths.append(os.path.join(skill_dir, ".env"))

    # 2. 项目的根目录 (假设运行脚本时的当前工作目录就是项目根目录)
    project_root = os.getcwd()
    paths.append(os.path.join(project_root, ".env"))

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


def get_env_files() -> list[str]:
    return _find_env_files()


def get_default_provider_name() -> str:
    name = _read_env_value("DEFAULT_ASR_PROVIDER")
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


def get_provider(name: Optional[str] = None, model: Optional[str] = None) -> ASRProvider:
    provider_name = name or get_default_provider_name()
    cls = PROVIDERS.get(provider_name)
    if cls is None:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown provider '{provider_name}'. Available: {available}")
    if model and provider_name == "siliconflow":
        return cls(model=model)
    return cls()
