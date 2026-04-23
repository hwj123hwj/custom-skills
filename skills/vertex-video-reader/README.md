# Vertex AI Video Reader Skill

Use Google Cloud Vertex AI's lightweight video model (`gemini-3.1-flash-lite-preview`) to understand, analyze, and describe videos.

## Features
- Ask questions about the contents of a video.
- Transcribe text on the screen or describe actions/characters.
- Automatically handles network proxies (e.g., `7890`).
- Directly passes small to medium videos to the API via `inlineData` Base64 encoding.

## Requirements
- A valid Google Cloud Vertex AI or Gemini Developer API Key.
  - Save it as `VERTEX_API_KEY` in a `.env` file in the skill's root directory or your project root.
- The video file size must not exceed the API inline limits (typically around ~20MB for Base64 encoded payload, works perfectly for short clips).

## Usage (CLI)

```bash
python .claude/skills/vertex-video-reader/scripts/analyze_video.py "/path/to/video.mp4" -p "请描述视频中发生的动作"
```

### Options

- `video_path`: The path to your video file (`.mp4`, `.mov`, `.webm`).
- `-p, --prompt`: Your question or instruction about the video (Default: "请详细描述一下这个视频的内容。").
- `-m, --model`: The video-capable model to use. Defaults to `gemini-3.1-flash-lite-preview`. You can also switch to `gemini-3.1-flash` for more complex reasoning.
