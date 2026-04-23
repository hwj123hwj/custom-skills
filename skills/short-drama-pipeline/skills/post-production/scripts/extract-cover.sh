#!/bin/bash
# extract-cover.sh — 从视频中抽取封面帧
# 用法: bash extract-cover.sh input.mp4 [-o cover.jpg]

set -euo pipefail

INPUT=""
OUTPUT="cover.jpg"

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    -o) OUTPUT="$2"; shift 2 ;;
    *)  INPUT="$1"; shift ;;
  esac
done

if [[ -z "$INPUT" ]]; then
  echo "用法: bash extract-cover.sh input.mp4 [-o cover.jpg]" >&2
  exit 1
fi

if [[ ! -f "$INPUT" ]]; then
  echo "错误: 文件不存在: $INPUT" >&2
  exit 1
fi

# 获取视频时长（秒）
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$INPUT")
# 抽取 20% 位置处的帧
OFFSET=$(echo "$DURATION * 0.2" | bc -l)

echo "正在从 ${INPUT} 抽取封面帧（${OFFSET}s 处）..."

ffmpeg -y -ss "$OFFSET" -i "$INPUT" \
  -vframes 1 \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" \
  -q:v 2 \
  "$OUTPUT" 2>/dev/null

echo "封面已保存: $OUTPUT"
