---
name: vertex-video-reader
description: Use this skill to read, analyze, and understand video files using Google Cloud Vertex AI's lightweight video model (gemini-3.1-flash-lite-preview). Use it whenever the user asks to summarize a video, extract text/actions from a video, describe what happens in an mp4/mov file, or ask questions about a specific video clip.
---

# Vertex AI Video Reader Skill

This skill allows you to analyze and understand video contents using the fast and cost-effective `gemini-3.1-flash-lite-preview` model via Google Vertex AI.

## Usage

To analyze a video, use the `run_shell_command` tool to execute the provided Python script:

```bash
python .claude/skills/vertex-video-reader/scripts/analyze_video.py "/path/to/video.mp4" -p "具体的提问或提示词"
```

### Parameters
- **video_path** (Required): The absolute or relative path to the video file (`.mp4`, `.mov`, `.webm`).
- **-p, --prompt** (Optional): Instructions for what to extract or analyze. Default is "请详细描述一下这个视频的内容。" (Please describe the contents of this video in detail).
- **-m, --model** (Optional): Model to use. Default is `gemini-3.1-flash-lite-preview` (cheaper/faster). You can switch to `gemini-3.1-flash` for tasks requiring deeper reasoning, complex extraction, or longer context.

## Important Constraints
- **File Size Limit**: This script uses `inlineData` (Base64 encoding) to send the video directly in the JSON payload. Vertex AI usually restricts inline video payloads to around `20MB`. It works best for small to medium video clips (e.g., short drama clips, Tiktok/Reels videos).
- **Supported Formats**: `mp4`, `mov`, `webm`, `mkv`.
- **API Key**: The script automatically looks for `VERTEX_API_KEY` in the skill's `.env` file or the project root `.env`.

## Examples

**Example 1: General Video Summary**
```bash
python .claude/skills/vertex-video-reader/scripts/analyze_video.py "./downloads/clip1.mp4"
```

**Example 2: Specific Question/Extraction**
```bash
python .claude/skills/vertex-video-reader/scripts/analyze_video.py "./assets/tutorial.mov" -p "提取出视频中屏幕上出现的所有中文字幕和关键步骤"
```
