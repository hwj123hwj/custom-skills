#!/usr/bin/env python3
"""
环境检测 + 自动安装 - video-copy-analyzer
按需检测：下载视频需要 ffmpeg + yt-dlp，转录需要 EasyClaw 认证
"""

import subprocess
import sys
import json
import shutil
from pathlib import Path

EASYCLAW_DIR = Path.home() / ".easyclaw"
USERINFO_JSON = EASYCLAW_DIR / "identity" / "easyclaw-userinfo.json"


def is_installed(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def run(cmd: list) -> bool:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


# --- 自动安装 ---

def install_ffmpeg() -> bool:
    print("   trying to install ffmpeg...")
    try:
        if sys.platform == "darwin":
            ok = run(["brew", "install", "ffmpeg"])
        elif sys.platform == "linux":
            if shutil.which("apt-get"):
                ok = run(["sudo", "apt-get", "install", "-y", "ffmpeg"])
            elif shutil.which("dnf"):
                ok = run(["sudo", "dnf", "install", "-y", "ffmpeg"])
            else:
                ok = False
        elif sys.platform == "win32":
            if shutil.which("winget"):
                ok = run(["winget", "install", "ffmpeg", "--silent"])
            elif shutil.which("choco"):
                ok = run(["choco", "install", "ffmpeg", "-y"])
            elif shutil.which("scoop"):
                ok = run(["scoop", "install", "ffmpeg"])
            else:
                # 终极兜底：提示用户手动下载
                ok = False
        else:
            ok = False

        if ok and is_installed("ffmpeg"):
            print("   ffmpeg installed")
            return True

        print("   auto install failed, please install manually:")
        _print_ffmpeg_hint()
        return False

    except Exception as e:
        print(f"   install error: {e}")
        _print_ffmpeg_hint()
        return False


def install_ytdlp() -> bool:
    print("   trying to install yt-dlp...")
    try:
        ok = run([sys.executable, "-m", "pip", "install", "-q", "yt-dlp"])
        if ok and is_installed("yt-dlp"):
            print("   yt-dlp installed")
            return True
        print("   auto install failed: pip install yt-dlp")
        return False
    except Exception as e:
        print(f"   install error: {e}")
        return False


def _print_ffmpeg_hint():
    if sys.platform == "darwin":
        print("   brew install ffmpeg")
    elif sys.platform == "linux":
        print("   sudo apt-get install ffmpeg")
    elif sys.platform == "win32":
        print("   option 1: winget install ffmpeg")
        print("   option 2: choco install ffmpeg")
        print("   option 3: scoop install ffmpeg")
        print("   option 4: download from https://www.gyan.dev/ffmpeg/builds/ and add to PATH")


# --- 检测逻辑 ---

def check_ffmpeg() -> bool:
    if is_installed("ffmpeg"):
        return True
    return install_ffmpeg()


def check_ytdlp() -> bool:
    if is_installed("yt-dlp"):
        return True
    return install_ytdlp()


def check_easyclaw_auth() -> bool:
    if not USERINFO_JSON.exists():
        print(f"   EasyClaw identity file not found, please login first")
        return False

    with open(USERINFO_JSON) as f:
        info = json.load(f)

    if info.get("uid") and info.get("token"):
        return True

    print("   EasyClaw auth info incomplete, please re-login")
    return False


# --- 主入口 ---

def check_and_setup(need_download: bool = False, need_transcribe: bool = False) -> bool:
    """
    按需检测并自动安装所需环境。

    Args:
        need_download:   需要下载视频时传 True（检测 ffmpeg + yt-dlp）
        need_transcribe: 需要语音转录时传 True（检测 EasyClaw 认证）

    Returns:
        True = 环境就绪，False = 有问题需处理
    """
    all_ok = True

    if need_download:
        if not check_ffmpeg():
            all_ok = False
        if not check_ytdlp():
            all_ok = False

    if need_transcribe:
        if not check_easyclaw_auth():
            all_ok = False

    return all_ok


if __name__ == "__main__":
    ok = check_and_setup(need_download=True, need_transcribe=True)
    sys.exit(0 if ok else 1)
