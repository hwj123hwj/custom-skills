#!/bin/bash
# compose-v3.sh — 将配图+配音+字幕合成最终视频（竖屏9:16）
# 用法: bash compose-v3.sh [output_dir]

set -euo pipefail

DIR="${1:-.}"
OUTPUT="$DIR/final.mp4"
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

echo "=== Step 1: 拼接配音 ==="
# 先把所有配音和静音间隔合并成一条音轨
for i in 1 2 3 4; do
  sox "$DIR/s${i}.mp3" "$TMPDIR/padded_${i}.mp3" pad 0.5 0 2>/dev/null || \
  ffmpeg -y -i "$DIR/s${i}.mp3" -af "apad=pad_dur=0.5" "$TMPDIR/padded_${i}.mp3" 2>/dev/null
done
# 最后一个场景多留白1秒
ffmpeg -y -i "$TMPDIR/padded_4.mp3" -af "apad=pad_dur=1.0" "$TMPDIR/padded_4_final.mp3" 2>/dev/null

# 用 concat demuxer 拼接
echo "file '$TMPDIR/padded_1.mp3'
file '$TMPDIR/padded_2.mp3'
file '$TMPDIR/padded_3.mp3'
file '$TMPDIR/padded_4_final.mp3'" > "$TMPDIR/audio_concat.txt"

ffmpeg -y -f concat -safe 0 -i "$TMPDIR/audio_concat.txt" \
  -c:a aac -b:a 128k "$TMPDIR/voice_all.m4a" 2>/dev/null

VOICE_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$TMPDIR/voice_all.m4a")
echo "配音总时长: ${VOICE_DUR}s"

echo "=== Step 2: 为每张图片生成对应时长的视频片段 ==="
# 场景时长分配（基于配音时长 + 间隔）
S1_DUR=6.5    # 6s配音 + 0.5s间隔
S2_DUR=5.1    # 4.6s配音 + 0.5s间隔
S3_DUR=2.2    # 1.7s配音 + 0.5s间隔
S4_DUR=3.7    # 2.7s配音 + 1.0s结尾留白

# 场景时长配置
DURS=("6.5" "5.1" "2.2" "3.7")
FRAMES=("195" "153" "66" "111")  # 秒数 * 30fps

for i in 0 1 2 3; do
  idx=$((i+1))
  # 缩放到 1080x1920 (9:16竖屏)
  ffmpeg -y -loop 1 -i "$DIR/scene_0${idx}.png" -t "${DURS[$i]}" \
    -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/black" \
    -c:v libx264 -preset fast -crf 23 \
    -pix_fmt yuv420p -r 30 "$TMPDIR/seg_${idx}.mp4" 2>/dev/null
  echo "场景${idx}: ${DURS[$i]}s"
done

echo "=== Step 3: 拼接视频片段 ==="
# 创建 concat 列表
for i in 1 2 3 4; do
  echo "file '$TMPDIR/seg_${i}.mp4'" >> "$TMPDIR/concat.txt"
done

ffmpeg -y -f concat -safe 0 -i "$TMPDIR/concat.txt" \
  -c:v libx264 -preset fast -crf 23 \
  -pix_fmt yuv420p "$TMPDIR/video_only.mp4" 2>/dev/null

echo "=== Step 4: 合成视频 + 配音 ==="
ffmpeg -y -i "$TMPDIR/video_only.mp4" -i "$TMPDIR/voice_all.m4a" \
  -c:v copy -c:a aac -b:a 128k \
  -shortest "$TMPDIR/video_voice.mp4" 2>/dev/null

echo "=== Step 5: 烧录字幕 ==="
ABS_SRT="$(cd "$(dirname "$DIR/subtitles.srt")" && pwd)/$(basename "$DIR/subtitles.srt")"

ffmpeg -y -i "$TMPDIR/video_voice.mp4" \
  -vf "subtitles='${ABS_SRT}':force_style='FontName=PingFang SC,FontSize=28,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Shadow=1,MarginV=60,BorderStyle=3'" \
  -c:v libx264 -preset fast -crf 23 \
  -c:a copy \
  "$OUTPUT" 2>/dev/null

FINAL_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUTPUT")
echo ""
echo "=== 完成 ==="
echo "输出: $OUTPUT"
echo "时长: ${FINAL_DUR}s"
