---
name: asr
description: |
  Unified ASR (Speech Recognition) skill with pluggable providers (strategy pattern).
  Supports: SiliconFlow (TeleAI/TeleSpeechASR).
  Use for transcribing audio/video files to text.
  Trigger: "转录", "识别语音", "语音转文字", "ASR", "transcribe", "语音识别".
  Auto-extracts audio from video files via ffmpeg.
allowed-tools: Bash(python3 */scripts/transcribe.py *)
---

# ASR — 语音识别技能

统一语音识别技能，基于策略模式，支持多个 ASR 后端切换。

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/transcribe.py` | 统一转录入口（自动从视频提取音频） |

## 用法

```bash
# 转录视频文件（自动提取音频）
python3 ${SKILL_DIR}/scripts/transcribe.py video.mp4

# 转录音频文件
python3 ${SKILL_DIR}/scripts/transcribe.py audio.wav

# 指定语言
python3 ${SKILL_DIR}/scripts/transcribe.py video.mp4 --language en

# JSON 输出
python3 ${SKILL_DIR}/scripts/transcribe.py video.mp4 --json

# 指定 provider
python3 ${SKILL_DIR}/scripts/transcribe.py video.mp4 --provider siliconflow
```

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input` | 音频/视频文件路径（必填） | - |
| `--language`, `-l` | 语言代码（zh, en, ja, auto） | zh |
| `--provider`, `-p` | ASR 后端 | 从 .env 读取 |
| `--json`, `-j` | JSON 格式输出 | 关 |

## Provider 切换

### 方式 1：修改 .env（永久切换）

编辑 `${SKILL_DIR}/.env`：
```
DEFAULT_ASR_PROVIDER=siliconflow
```

### 方式 2：命令行参数（单次覆盖）

```bash
python3 transcribe.py video.mp4 --provider siliconflow
```

### 方式 3：新增 Provider

1. 在 `scripts/providers/` 下新建 `xxx_provider.py`
2. 继承 `ASRProvider`，实现 `transcribe()` 方法
3. 在 `registry.py` 的 `PROVIDERS` 字典中注册

## API Key 配置

### SiliconFlow

读取优先级：
1. 环境变量 `SILICONFLOW_API_KEY`
2. `${SKILL_DIR}/.env` 中的 `SILICONFLOW_API_KEY=...`

## 支持的音频/视频格式

**音频**：wav, mp3, m4a, aac, flac, ogg
**视频**：mp4, mkv, mov, avi, webm（自动提取音频）

## 依赖

- Python 3（标准库，无需额外安装）
- ffmpeg（用于从视频提取音频）
