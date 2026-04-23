#!/bin/bash
#
# 高清导出：2-pass 编码 + 锐化，匹配或超越原片画质
#
# 用法: ./hd_export.sh <input.mp4> [output.mp4] [bitrate_multiplier]
#
# bitrate_multiplier: 码率倍率，默认 1.2（原片的 1.2 倍）
#

INPUT="$1"
OUTPUT="${2:-}"
MULTIPLIER="${3:-1.2}"

if [ -z "$INPUT" ]; then
  echo "❌ 用法: ./hd_export.sh <input.mp4> [output.mp4] [码率倍率]"
  exit 1
fi

if [ ! -f "$INPUT" ]; then
  echo "❌ 找不到输入文件: $INPUT"
  exit 1
fi

# 默认输出文件名
if [ -z "$OUTPUT" ]; then
  BASENAME=$(basename "$INPUT" .mp4)
  OUTPUT_DIR=$(dirname "$INPUT")
  OUTPUT="${OUTPUT_DIR}/${BASENAME}_hd.mp4"
fi

# 获取视频信息
BITRATE=$(ffprobe -v error -show_entries stream=bit_rate -select_streams v:0 -of csv=p=0 "file:$INPUT")
PROFILE=$(ffprobe -v error -show_entries stream=profile -select_streams v:0 -of csv=p=0 "file:$INPUT")
PIX_FMT=$(ffprobe -v error -show_entries stream=pix_fmt -select_streams v:0 -of csv=p=0 "file:$INPUT")
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "file:$INPUT")

# 计算目标码率
TARGET_BR=$(node -e "console.log(Math.round($BITRATE / 1000 * $MULTIPLIER))")
MAXRATE=$((TARGET_BR * 13 / 10))
BUFSIZE=$((TARGET_BR * 2))

# 映射 profile
PROFILE_LC=$(echo "$PROFILE" | tr '[:upper:]' '[:lower:]')
case "$PROFILE_LC" in
  "high") X264_PROFILE="high" ;;
  "main") X264_PROFILE="main" ;;
  "baseline") X264_PROFILE="baseline" ;;
  *) X264_PROFILE="high" ;;
esac

echo "📹 输入: $INPUT"
echo "📹 时长: ${DURATION}s"
echo "📊 原片: ${BITRATE}bps ($(($BITRATE/1000))kbps), profile=$PROFILE, pix_fmt=$PIX_FMT"
echo "🎯 目标: ${TARGET_BR}kbps (${MULTIPLIER}x), 2-pass + 锐化"
echo ""

# 临时文件
PASSLOG=$(mktemp /tmp/ffmpeg2pass.XXXXXX)
trap "rm -f ${PASSLOG}*" EXIT

# Pass 1: 分析
echo "⚙️ Pass 1/2: 分析画面复杂度..."
ffmpeg -y -v error -stats \
  -i "file:$INPUT" \
  -vf "unsharp=5:5:0.3:5:5:0.3" \
  -c:v libx264 -profile:v "$X264_PROFILE" \
  -b:v "${TARGET_BR}k" -preset slow \
  -pix_fmt "$PIX_FMT" \
  -pass 1 -passlogfile "$PASSLOG" \
  -an -f null /dev/null

if [ $? -ne 0 ]; then
  echo "❌ Pass 1 失败"
  exit 1
fi

echo ""

# Pass 2: 编码
echo "⚙️ Pass 2/2: 高清编码 + 锐化..."
ffmpeg -y -v error -stats \
  -i "file:$INPUT" \
  -vf "unsharp=5:5:0.3:5:5:0.3" \
  -c:v libx264 -profile:v "$X264_PROFILE" \
  -b:v "${TARGET_BR}k" -maxrate "${MAXRATE}k" -bufsize "${BUFSIZE}k" \
  -preset slow \
  -pix_fmt "$PIX_FMT" \
  -pass 2 -passlogfile "$PASSLOG" \
  -c:a copy \
  -movflags +faststart \
  "file:$OUTPUT"

if [ $? -eq 0 ]; then
  echo ""
  echo "✅ 已保存: $OUTPUT"
  NEW_BR=$(ffprobe -v error -show_entries stream=bit_rate -select_streams v:0 -of csv=p=0 "file:$OUTPUT")
  NEW_SIZE=$(ls -lh "$OUTPUT" | awk '{print $5}')
  echo "📊 码率: $(($BITRATE/1000))kbps → $(($NEW_BR/1000))kbps (${MULTIPLIER}x)"
  echo "📦 文件: $NEW_SIZE"
else
  echo "❌ Pass 2 失败"
  exit 1
fi
