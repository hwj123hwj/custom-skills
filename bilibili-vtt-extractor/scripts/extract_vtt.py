# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "rich",
# ]
# ///

import sys
import re
import os
from pathlib import Path
from rich.console import Console

console = Console()

def extract_vtt_text(vtt_path: str):
    """提取 VTT 文件中的纯文本内容并去重保序"""
    path = Path(vtt_path)
    if not path.exists():
        console.print(f"[red]错误: 文件 {vtt_path} 不存在[/red]")
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        lines = content.splitlines()
        text_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # 跳过头、时间戳和纯数字序号
            if line.startswith("WEBVTT") or "-->" in line or re.match(r"^\d+$", line):
                continue
            text_lines.append(line)
        
        # 去重保序
        unique_text = list(dict.fromkeys(text_lines))
        
        output_path = path.with_suffix(".txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(unique_text))
            
        console.print(f"[green]提取成功![/green] 纯文本已保存至: [bold]{output_path}[/bold]")
        
    except Exception as e:
        console.print(f"[red]处理失败: {str(e)}[/red]")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("[yellow]用法: uv run scripts/extract_vtt.py <path_to_vtt_file>[/yellow]")
    else:
        extract_vtt_text(sys.argv[1])
