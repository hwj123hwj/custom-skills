#!/usr/bin/env python3
"""
使用 EasyClaw Platform API 进行语音转录 (gpt-4o-mini-transcribe)
"""

import os
import sys
import json
import tempfile
import urllib.request
import urllib.error
from pathlib import Path


def load_easyclaw_config() -> dict:
    home = Path.home()
    identity_file = home / ".easyclaw" / "identity" / "easyclaw-userinfo.json"
    config_file = home / ".easyclaw" / "easyclaw.json"

    if not identity_file.exists():
        raise FileNotFoundError(f"EasyClaw 身份文件不存在，请先登录: {identity_file}")
    if not config_file.exists():
        raise FileNotFoundError(f"EasyClaw 配置文件不存在: {config_file}")

    with open(identity_file, "r", encoding="utf-8") as f:
        identity = json.load(f)
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    base_url = config.get("models", {}).get("providers", {}).get("easyclaw", {}).get("baseUrl", "")
    if not base_url:
        raise ValueError("未找到 EasyClaw baseUrl 配置")

    return {
        "uid": identity.get("uid"),
        "token": identity.get("token"),
        "base_url": base_url.rstrip("/")
    }


def extract_audio(video_path: Path) -> Path:
    """用 ffmpeg 从视频提取音频，压缩为低码率 mono mp3 减少上传体积"""
    import subprocess

    audio_path = Path(tempfile.mktemp(suffix=".mp3"))
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vn",                  # 去掉视频流
        "-acodec", "libmp3lame",
        "-ar", "16000",         # 16kHz，语音转录足够
        "-ac", "1",             # mono
        "-q:a", "5",            # 适当压缩，减少文件大小
        str(audio_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"音频提取失败: {result.stderr}")

    size_mb = audio_path.stat().st_size / 1024 / 1024
    print(f"   音频提取完成: {size_mb:.1f}MB")
    return audio_path


def transcribe_audio(audio_path: Path, config: dict) -> dict:
    """上传音频到 EasyClaw API 进行转录"""
    boundary = "----EasyClawBoundary"

    # 流式构建 multipart body，避免大文件全量读入内存
    with open(audio_path, "rb") as f:
        file_content = f.read()

    body = b""
    body += f'--{boundary}\r\nContent-Disposition: form-data; name="model"\r\n\r\ngpt-4o-mini-transcribe\r\n'.encode()
    body += f'--{boundary}\r\nContent-Disposition: form-data; name="response_format"\r\n\r\nverbose_json\r\n'.encode()
    body += (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="{audio_path.name}"\r\n'
        f'Content-Type: audio/mpeg\r\n\r\n'
    ).encode() + file_content + b'\r\n'
    body += f'--{boundary}--\r\n'.encode()

    req = urllib.request.Request(
        f"{config['base_url']}/audio/transcriptions",
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "X-Auth-Uid": config["uid"],
            "X-Auth-Token": config["token"]
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"API 请求失败 {e.code}: {e.read().decode('utf-8')}")


def write_srt(result: dict, output_srt: Path) -> None:
    """将转录结果写为 SRT 文件"""
    segments = result.get("segments", [])
    if not segments:
        segments = [{
            "id": 1,
            "start": 0.0,
            "end": result.get("duration", 60.0) or 60.0,
            "text": result.get("text", "")
        }]

    def fmt(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    with open(output_srt, "w", encoding="utf-8") as f:
        for seg in segments:
            f.write(f"{seg.get('id', 1)}\n")
            f.write(f"{fmt(seg['start'])} --> {fmt(seg['end'])}\n")
            f.write(f"{seg['text'].strip()}\n\n")


def main():
    if len(sys.argv) < 2:
        print("用法: python transcribe_api.py <视频/音频路径> [输出SRT路径]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_srt = Path(sys.argv[2]) if len(sys.argv) > 2 else input_path.with_suffix(".srt")

    if not input_path.exists():
        print(f" 文件不存在: {input_path}")
        sys.exit(1)

    print(f" 开始转录: {input_path.name}")

    config = load_easyclaw_config()

    is_video = input_path.suffix.lower() in (".mp4", ".mov", ".avi", ".mkv", ".webm")
    audio_path = None

    try:
        if is_video:
            print("   从视频提取音频...")
            audio_path = extract_audio(input_path)
        else:
            audio_path = input_path

        print("   上传到 EasyClaw API...")
        result = transcribe_audio(audio_path, config)

        write_srt(result, output_srt)

        print(f" 转录完成: {len(result.get('segments', []))} 片段 → {output_srt.name}")

    finally:
        # 确保临时音频文件一定被清理（无论成功还是失败）
        if is_video and audio_path and audio_path.exists():
            audio_path.unlink()


if __name__ == "__main__":
    main()
