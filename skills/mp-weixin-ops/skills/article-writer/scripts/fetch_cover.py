#!/usr/bin/env python3
"""
获取文章封面图
- 默认：从 picsum.photos 下载随机图（1200x630）
- 自定义：复制用户指定的本地图片到输出目录
"""
import argparse
import os
import shutil
import sys
import urllib.request
from datetime import datetime
from pathlib import Path


def fetch_random(output_path: Path):
    """从 picsum.photos 下载随机封面图"""
    url = "https://picsum.photos/1200/630"
    print("[INFO] 正在从 picsum.photos 获取随机封面图...")
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = resp.read()
    except Exception as e:
        print(f"[ERROR] 下载失败：{e}", file=sys.stderr)
        sys.exit(1)

    with open(output_path, "wb") as f:
        f.write(data)


def use_custom(custom_path: str, output_path: Path):
    """使用用户提供的本地图片"""
    src = Path(custom_path)
    if not src.exists():
        print(f"[ERROR] 文件不存在：{custom_path}", file=sys.stderr)
        sys.exit(1)
    shutil.copy2(src, output_path)
    print(f"[INFO] 使用自定义图片：{custom_path}")


def main():
    parser = argparse.ArgumentParser(description="获取微信文章封面图")
    parser.add_argument("--output", default=None, help="输出文件路径（可选）")
    parser.add_argument("--custom", default=None, help="使用本地图片作为封面，传入文件路径")
    args = parser.parse_args()

    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = Path(__file__).parent.parent / "output" / "covers"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"cover_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

    if args.custom:
        use_custom(args.custom, output_path)
    else:
        fetch_random(output_path)

    size_kb = os.path.getsize(output_path) / 1024
    print(f"[OK] 封面图已保存：{output_path}（{size_kb:.1f} KB）")
    print("[提示] 如需替换封面，可重新运行并加 --custom 参数，或在微信草稿箱中手动替换")


if __name__ == "__main__":
    main()
