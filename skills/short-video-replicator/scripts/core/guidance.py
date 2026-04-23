"""文字稿生成模块"""

from datetime import datetime
from pathlib import Path


def read_srt_text(srt_path: Path) -> str:
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = []
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.isdigit() or "-->" in line:
            continue
        lines.append(line)

    text = " ".join(lines)
    return text.replace("  ", " ")


def generate_transcript(srt_path: Path, output_dir: Path, video_source: str) -> Path:
    """从 SRT 生成原始文字稿"""
    video_id = srt_path.stem
    transcript_path = output_dir / f"{video_id}_transcript.md"

    text_content = read_srt_text(srt_path)

    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(f"# {video_id} Transcript\n\n")
        f.write(f"**Source**: {video_source}\n")
        f.write(f"**Video**: {video_id}.mp4\n")
        f.write(f"**Model**: gpt-4o-mini-transcribe (EasyClaw API)\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        f.write("## Full Transcript\n\n")
        f.write(text_content)
        f.write("\n")

    return transcript_path
