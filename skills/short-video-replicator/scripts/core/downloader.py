"""视频下载模块"""

import subprocess
import shutil
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent.resolve()


def get_ytdlp() -> str:
    """优先用 venv 里的 yt-dlp，否则用系统的"""
    venv_ytdlp = SCRIPT_DIR / "venv" / "bin" / "yt-dlp"
    if venv_ytdlp.exists():
        return str(venv_ytdlp)
    if shutil.which("yt-dlp"):
        return "yt-dlp"
    raise RuntimeError("yt-dlp not found. Install: pip install yt-dlp")


def extract_video_id(url: str) -> str:
    bilibili_match = re.search(r'(BV[\w]+|av\d+)', url)
    if bilibili_match:
        return bilibili_match.group(1)

    youtube_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
    if youtube_match:
        return youtube_match.group(1)

    douyin_match = re.search(r'video/(\d+)', url)
    if douyin_match:
        return f"douyin_{douyin_match.group(1)}"

    return hex(hash(url) & 0xFFFFFFFF)[2:]


def download_douyin(url: str, output_dir: Path) -> Path:
    video_id = extract_video_id(url)
    output_file = output_dir / f"{video_id}.mp4"
    script_path = SCRIPT_DIR / "scripts" / "download_douyin.py"

    result = subprocess.run(
        [sys.executable, str(script_path), url, str(output_file)],
        capture_output=True, text=True
    )

    # exit code 2 = NEED_LOGIN，给 Agent 明确的错误信息
    if result.returncode == 2:
        raise RuntimeError("NEED_LOGIN: 该视频需要登录抖音才能下载，请在浏览器中登录后重试")

    if result.returncode != 0:
        raise RuntimeError(f"抖音下载失败: {result.stderr or result.stdout}")

    if not output_file.exists():
        raise RuntimeError("未找到下载的视频文件")

    return output_file


def download_ytdlp(url: str, output_dir: Path) -> Path:
    video_id = extract_video_id(url)
    output_template = str(output_dir / f"{video_id}.%(ext)s")

    result = subprocess.run(
        [
            get_ytdlp(),
            "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "--merge-output-format", "mp4",
            "-o", output_template,
            url
        ],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp 下载失败: {result.stderr}")

    for ext in ["mp4", "mkv", "webm"]:
        video_file = output_dir / f"{video_id}.{ext}"
        if video_file.exists():
            return video_file

    raise RuntimeError("未找到下载的视频文件")


def download_video(url: str, output_dir: Path) -> Path:
    is_douyin = "douyin.com" in url or "v.douyin.com" in url
    if is_douyin:
        return download_douyin(url, output_dir)
    else:
        return download_ytdlp(url, output_dir)
