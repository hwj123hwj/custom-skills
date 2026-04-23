#!/bin/bash
# burn-subtitle.sh — 将 SRT 字幕烧录到视频
# 用法: bash burn-subtitle.sh input.mp4 subtitle.srt [-o output.mp4]

set -euo pipefail

INPUT=""
SUBTITLE=""
OUTPUT="output_subtitled.mp4"

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    -o) OUTPUT="$2"; shift 2 ;;
    *)  if [[ -z "$INPUT" ]]; then
          INPUT="$1"
        elif [[ -z "$SUBTITLE" ]]; then
          SUBTITLE="$1"
        fi
        shift ;;
  esac
done

if [[ -z "$INPUT" || -z "$SUBTITLE" ]]; then
  echo "用法: bash burn-subtitle.sh input.mp4 subtitle.srt [-o output.mp4]" >&2
  exit 1
fi

if [[ ! -f "$INPUT" ]]; then
  echo "错误: 视频文件不存在: $INPUT" >&2
  exit 1
fi

if [[ ! -f "$SUBTITLE" ]]; then
  echo "错误: 字幕文件不存在: $SUBTITLE" >&2
  exit 1
fi

# 将 SRT 路径转换为绝对路径（ffmpeg 的 subtitles 滤镜需要）
ABS_SUBTITLE="$(cd "$(dirname "$SUBTITLE")" && pwd)/$(basename "$SUBTITLE")"

echo "正在烧录字幕..."

ffmpeg -y -i "$INPUT" \
  -vf "subtitles='${ABS_SUBTITLE}':force_style='FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Shadow=1,MarginV=40'" \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 128k \
  "$OUTPUT" 2>/dev/null

echo "字幕烧录完成: $OUTPUT"
