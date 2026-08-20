---
name: tts
description: |
  Unified TTS (Text-to-Speech) skill with pluggable providers (strategy pattern).
  Supports: Edge TTS (free, no API key), Vertex AI Gemini TTS (Google),
  and Atlas Cloud TTS (optional, asynchronous API).
  Use for generating voiceovers, narration, dubbing.
  Trigger: "配音", "生成语音", "TTS", "text-to-speech", "合成语音", "语音合成".
allowed-tools: Bash(python3 */scripts/tts.py *)
aliases:
  - 配音
  - 语音合成
  - TTS
  - 合成语音
tags:
  - Audio
  - Utility
---

# TTS — 语音合成技能

统一语音合成技能，基于策略模式，支持多个 TTS 后端切换。

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/tts.py` | 统一合成入口 |

## 用法

```bash
# 默认用 edge-tts（免费，无需 API Key）
python3 ${SKILL_DIR}/scripts/tts.py "你好世界" -o hello.mp3

# 指定 provider
python3 ${SKILL_DIR}/scripts/tts.py "你好" --provider vertex-tts

# 指定 voice
python3 ${SKILL_DIR}/scripts/tts.py "旁白" --provider vertex-tts --voice Aoede

# 通过 Atlas Cloud 生成 MP3（默认 xai/tts-v1）
python3 ${SKILL_DIR}/scripts/tts.py "统一语音接口" --provider atlascloud --voice eve

# 使用中文预设 voice（edge-tts）
python3 ${SKILL_DIR}/scripts/tts.py "测试旁白" --preset yunjian

# 调整语速（edge-tts）
python3 ${SKILL_DIR}/scripts/tts.py "快速朗读" --rate +20%

# JSON 输出
python3 ${SKILL_DIR}/scripts/tts.py "你好" --json
```

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `text` | 要转换的文本（必填） | - |
| `--output`, `-o` | 输出音频路径 | `outputs/output.mp3` |
| `--provider`, `-p` | TTS 后端 | 从 .env 读取 |
| `--voice`, `-v` | 音色名称 | edge-tts: zh-CN-XiaoxiaoNeural / vertex-tts: Zephyr / atlascloud: eve |
| `--preset` | 中文预设（edge-tts） | - |
| `--language`, `-l` | 语言代码 | - |
| `--rate`, `-r` | 语速调整 | 0% |
| `--json`, `-j` | JSON 格式输出 | 关 |

## 中文预设（edge-tts）

| 预设名 | Voice ID | 特点 |
|--------|---------|------|
| `xiaoxiao` | zh-CN-XiaoxiaoNeural | 女声，温柔亲切（默认） |
| `xiaoyi` | zh-CN-XiaoyiNeural | 女声，活泼可爱 |
| `yunjian` | zh-CN-YunjianNeural | 男声，沉稳大气 |
| `yuxuan` | zh-CN-YuxuanNeural | 女声，温柔知性 |
| `shimmer` | zh-CN-ShimmerNeural | 女声，清亮甜美 |
| `guy` | zh-CN-YunxiNeural | 男声，自然对话 |
| `xiaomeng` | zh-CN-XiaomengNeural | 童声，萌系 |
| `zhiyu` | zh-CN-ZhiyuNeural | 女声，情感丰富 |

## Provider 切换

### 方式 1：修改 .env（永久切换）

编辑 `${SKILL_DIR}/.env`：
```
DEFAULT_TTS_PROVIDER=edge-tts
# 或
DEFAULT_TTS_PROVIDER=vertex-tts
# 或
DEFAULT_TTS_PROVIDER=atlascloud
```

### 方式 2：命令行参数（单次覆盖）

```bash
python3 tts.py "text" --provider vertex-tts
python3 tts.py "text" --provider atlascloud
```

### 方式 3：新增 Provider

1. 在 `scripts/providers/` 下新建 `xxx_provider.py`
2. 继承 `TTSProvider`，实现 `synthesize()` 方法
3. 在 `registry.py` 的 `PROVIDERS` 字典中注册

## Provider 对比

| 维度 | edge-tts | vertex-tts | atlascloud |
|------|---------|------------|------------|
| 费用 | 免费 | 需要 API Key | 需要 API Key |
| 音质 | 好 | 更好 | 取决于所选模型 |
| 中文支持 | 400+ 音色 | 30 音色 | 多语言音色 |
| 速度 | 快 | 较慢 | 异步任务 |
| 语速控制 | 支持 | 暂不支持 | 支持（0.7-1.5） |
| 依赖 | edge-tts CLI | ffmpeg | Python 标准库 |

## API Key 配置

### edge-tts

无需 API Key。

### Vertex AI

读取优先级：
1. 环境变量 `VERTEX_API_KEY` / `GEMINI_API_KEY`
2. `${SKILL_DIR}/.env` 中的 `VERTEX_API_KEY=...`
3. 项目根目录 `.env`

### Atlas Cloud

读取优先级：
1. 环境变量 `ATLASCLOUD_API_KEY`
2. `${SKILL_DIR}/.env` 中的 `ATLASCLOUD_API_KEY=...`
3. 项目根目录 `.env`

当前使用 `xai/tts-v1` 的实时请求 schema。可用 `ATLASCLOUD_BASE_URL`
指向兼容部署。提交生成请求后，provider 只轮询 prediction GET 接口，
轮询次数有上限，不会自动重试生成 POST。

## 依赖

- Python 3（标准库 + edge-tts）
- ffmpeg（vertex-tts 需要，edge-tts 不需要）
