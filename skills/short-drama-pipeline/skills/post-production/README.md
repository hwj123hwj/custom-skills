# post-production — 后期合成

基于生成的视频素材，进行后期处理（抽帧、字幕、拼接）。

## 依赖

- ffmpeg 8.0+（已安装，支持 Apple Silicon 硬件加速）

## 可用脚本

### extract-cover.sh — 抽取封面

从视频中抽取关键帧作为封面图。

```bash
bash skills/post-production/scripts/extract-cover.sh input.mp4 -o cover.jpg
```

参数：
- `input.mp4`：输入视频路径
- `-o`：输出图片路径（默认 `cover.jpg`）

逻辑：抽取视频 20% 位置处的帧（通常避开片头黑屏），缩放到 1080p。

### burn-subtitle.sh — 字幕烧录

将 SRT 字幕文件烧录到视频上。

```bash
bash skills/post-production/scripts/burn-subtitle.sh input.mp4 subtitle.srt -o output.mp4
```

参数：
- `input.mp4`：输入视频
- `subtitle.srt`：SRT 字幕文件
- `-o`：输出路径（默认 `output_subtitled.mp4`）

### concat-videos.sh — 视频拼接

将多个视频片段按顺序拼接成一个完整视频。

```bash
bash skills/post-production/scripts/concat-videos.sh scene1.mp4 scene2.mp4 scene3.mp4 -o final.mp4
```

参数：
- 多个视频文件路径（按拼接顺序）
- `-o`：输出路径（默认 `merged.mp4`）

逻辑：ffmpeg concat demuxer，自动处理不同分辨率的片段（缩放到统一的 1080p）。

## 输出

后期处理后的成片保存到 `output/final/`。
