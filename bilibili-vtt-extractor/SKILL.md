# B站字幕提取与处理技能 (Bilibili VTT Extractor)

- **Version**: 1.0.0
- **Author**: 小明2 (OpenClaw Assistant)
- **Description**: 专门用于提取和清理 B 站视频字幕（VTT 格式）的工具。配合 `yt-dlp` 获取字幕后，通过此脚本可自动去除 VTT 头部信息、时间戳和重复行，输出整洁的纯文本内容，极大方便 AI 进行长视频摘要和观点总结。

## 功能特点
- **自动清理**：去除 WEBVTT 标记、时间戳（`00:00:00 --> ...`）和序号。
- **智能去重**：处理 B 站自动生成字幕中常见的行重复问题，同时保持内容顺序。
- **环境隔离**：使用 `uv` 管理依赖，零环境污染。

## Usage

### 1. 使用 yt-dlp 获取字幕
首先使用 `yt-dlp` 下载字幕（需自行安装并提供 cookies 如果有风控）：
```bash
yt-dlp --write-auto-sub --sub-lang "zh-Hans" --skip-download -o "video_id" "https://www.bilibili.com/video/BVxxx"
```

### 2. 使用本技能处理字幕
```bash
uv run bilibili-vtt-extractor/scripts/extract_vtt.py video_id.zh-Hans.vtt
```
处理完成后，会同级生成一个同名的 `.txt` 文件。

## 注意事项
- 脚本默认使用 UTF-8 编码。
- 依赖 Python 3.11+ 和 `uv` 环境。
