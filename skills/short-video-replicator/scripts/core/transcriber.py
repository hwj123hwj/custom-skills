"""语音转录模块"""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent.resolve()


def transcribe_video(video_path: Path, output_srt: Path) -> None:
    script_path = SCRIPT_DIR / "scripts" / "transcribe_api.py"

    result = subprocess.run(
        [sys.executable, str(script_path), str(video_path), str(output_srt)],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        err = result.stderr or result.stdout
        raise RuntimeError(f"转录失败: {err}")

    if not output_srt.exists():
        raise RuntimeError("转录完成但未找到 SRT 文件")
