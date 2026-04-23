#!/bin/bash
# concat-videos.sh — 按顺序拼接多个视频片段
# 用法: bash concat-videos.sh scene1.mp4 scene2.mp4 [-o final.mp4]

set -euo pipefail

INPUTS=()
OUTPUT="merged.mp4"

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    -o) OUTPUT="$2"; shift 2 ;;
    *)  INPUTS+=("$1"); shift ;;
  esac
done

if [[ ${#INPUTS[@]} -lt 2 ]]; then
  echo "用法: bash concat-videos.sh scene1.mp4 scene2.mp4 [-o final.mp4]" >&2
  echo "至少需要 2 个视频文件" >&2
  exit 1
fi

# 检查所有输入文件
for f in "${INPUTS[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "错误: 文件不存在: $f" >&2
    exit 1
  fi
done

echo "正在拼接 ${#INPUTS[@]} 个视频片段..."

# 创建临时 concat 文件
TMPDIR=$(mktemp -d)
CONCAT_LIST="$TMPDIR/concat.txt"

for f in "${INPUTS[@]}"; do
  ABS_PATH="$(cd "$(dirname "$f")" && pwd)/$(basename "$f")"
  echo "file '${ABS_PATH}'" >> "$CONCAT_LIST"
done

# 拼接（自动缩放到 1080p）
ffmpeg -y -f concat -safe 0 -i "$CONCAT_LIST" \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 128k \
  "$OUTPUT" 2>/dev/null

rm -rf "$TMPDIR"
echo "拼接完成: $OUTPUT"
