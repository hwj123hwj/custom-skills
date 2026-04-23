#!/usr/bin/env python3
"""
视频文案分析工具 - 主入口
用法: python main.py <视频URL或分享文本或文件路径> [输出目录]
"""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.downloader import download_video, extract_video_id
from core.transcriber import transcribe_video
from core.guidance import generate_transcript

try:
    from scripts.extract_video_url import extract_video_url_from_text
except ImportError:
    extract_video_url_from_text = None

try:
    from scripts.check_environment import check_and_setup
except ImportError:
    check_and_setup = None


def is_url(path: str) -> bool:
    return path.startswith(("http://", "https://", "BV"))


def report_stage(stage: int, name: str, file: Path = None, status: str = None):
    print(f"\n 阶段 {stage}/3: {name}")
    if file:
        print(f"    {file.name}")
    if status:
        print(f"    {status}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: python main.py <video_url/share_text/file_path> [output_dir]")
        print("")
        print("Default output dir: <sub-agent>/canvas (auto-detected)")
        print("")
        print("Examples:")
        print("  python main.py 'https://www.bilibili.com/video/BVxxxx'")
        print("  python main.py BV1234567890")
        print("  python main.py ./my_video.mp4 ./output")
        sys.exit(0)

    input_text = sys.argv[1]
    # 默认使用 sub-agent 的 canvas 目录，可通过参数指定其他目录
    # 自动检测：从脚本位置向上查找 workspace-* 目录
    script_dir = Path(__file__).parent.resolve()
    subagent_dir = script_dir
    while subagent_dir.name and not subagent_dir.name.startswith("workspace-"):
        subagent_dir = subagent_dir.parent
    canvas_base = subagent_dir / "canvas" if subagent_dir.name.startswith("workspace-") else Path.home() / "canvas"
    today = datetime.now().strftime("%Y-%m-%d")

    # 输出目录：canvas/{date}/{video_id}/，video_id 在下载后确定，先用日期目录占位
    if len(sys.argv) > 2:
        output_dir = Path(sys.argv[2])
    else:
        output_dir = canvas_base / today  # 先用日期目录，后续会加 video_id 层

    # 提取链接
    url = input_text
    if extract_video_url_from_text and not os.path.exists(input_text):
        extracted, platform = extract_video_url_from_text(input_text)
        if extracted:
            print(f" 提取到{platform}链接: {extracted}")
            url = extracted

    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 50)
    print(" 视频文案分析工具")
    print("=" * 50)

    # 按需检测环境：下载视频需要 ffmpeg+yt-dlp，转录需要 EasyClaw 认证
    need_download = is_url(url) or not os.path.exists(url)
    if check_and_setup:
        if not check_and_setup(need_download=need_download, need_transcribe=True):
            print(" 环境检测未通过，请按提示处理后重试")
            sys.exit(1)

    start_time = datetime.now()

    # 阶段1: 下载视频
    if is_url(url):
        # 先下载到日期目录，获取 video_id 后再移入子目录
        output_dir.mkdir(parents=True, exist_ok=True)
        video_path = download_video(url, output_dir)
        video_source = url
    else:
        video_path = Path(url)
        if not video_path.exists():
            print(f" 文件不存在: {video_path}")
            sys.exit(1)
        video_source = str(video_path)

    # 确定最终输出目录：canvas/{date}/{video_id}/
    video_id = video_path.stem
    if len(sys.argv) <= 2:
        output_dir = canvas_base / today / video_id
        output_dir.mkdir(parents=True, exist_ok=True)
        # 把已下载的视频移入子目录
        new_video_path = output_dir / video_path.name
        if video_path != new_video_path:
            import shutil
            shutil.copy2(str(video_path), str(new_video_path))
            video_path = new_video_path
    else:
        output_dir.mkdir(parents=True, exist_ok=True)

    print(f" 输出: {output_dir}\n")

    size_mb = video_path.stat().st_size / 1024 / 1024
    report_stage(1, "下载视频", video_path, f"{size_mb:.1f}MB")

    # 阶段2: 语音转录
    srt_path = output_dir / f"{video_path.stem}.srt"
    transcribe_video(video_path, srt_path)

    segment_count = sum(1 for line in open(srt_path, "r", encoding="utf-8") if line.strip().isdigit())
    report_stage(2, "语音转录", srt_path, f"{segment_count} 片段")

    # 阶段3: 生成文字稿
    transcript_path = generate_transcript(srt_path, output_dir, video_source)

    with open(transcript_path, "r", encoding="utf-8") as f:
        text = f.read()
        if "## Full Transcript" in text:
            text = text.split("## Full Transcript")[1].strip()
    report_stage(3, "生成文字稿", transcript_path, f"{len(text)} 字符")

    # 完成
    duration = (datetime.now() - start_time).total_seconds()

    print("\n" + "=" * 50)
    print(" 完成!")
    print("=" * 50)
    print(f"⏱  耗时: {duration:.1f}秒")
    print(f" 目录: {output_dir}\n")

    print(" 生成文件:")
    print(f"   • {video_path.name}")
    print(f"   • {srt_path.name}")
    print(f"   • {transcript_path.name}")

    print("\n Agent Next Step:")
    print("   Read analysis framework from prompt/")
    print("   Call LLM to generate de-ai-fied analysis report")
    print(f"   Output: {output_dir}/{video_path.stem}_structured.md")


if __name__ == "__main__":
    main()
