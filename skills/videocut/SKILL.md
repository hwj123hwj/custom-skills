---
name: videocut
description: 口播视频一站式剪辑 Skill。覆盖转录、口误识别、字幕生成、高清导出的完整工作流。触发词：剪口播、处理视频、帮我剪辑、生成字幕、导出高清。从视频到成片，一步到位。
---

# videocut — 口播视频一站式剪辑

> 火山引擎转录 + AI 口误识别 + 字幕生成 + 高清导出

## 快速使用

```
用户: 帮我剪这个口播视频
用户: 处理一下这个视频
用户: 生成字幕
用户: 导出高清
```

## 内置子功能（skills/ 目录）

| 子目录 | 功能 | 触发词 |
|--------|------|--------|
| `skills/剪口播/` | 转录 + 口误识别 + 审核 | 剪口播、处理视频 |
| `skills/字幕/` | 字幕校对 + 烧录 | 字幕、加字幕 |
| `skills/高清化/` | 2-pass 高清导出 | 高清化、导出高清 |
| `skills/自进化/` | 记录反馈、持续改进 | 记录反馈、更新规则 |

## 完整工作流（4 步）

```
Step 1  剪口播      →  skills/剪口播/（转录 + 口误识别 + 审核）
Step 2  字幕        →  skills/字幕/（校对 + 烧录）
Step 3  高清导出    →  skills/高清化/（2-pass + 锐化）
Step 4  自进化      →  skills/自进化/（记录反馈，可选）
```

## 首次使用前

### 安装依赖

```bash
brew install node ffmpeg
```

### 配置 API Key

在项目根目录创建 `.env`：

```bash
VOLCENGINE_API_KEY=your_api_key_here
```

详见 [references/dependencies.md](references/dependencies.md)

```
output/
└── YYYY-MM-DD_视频名/
    ├── 剪口播/
    │   ├── 1_转录/
    │   │   ├── audio.mp3
    │   │   ├── volcengine_result.json
    │   │   └── subtitles_words.json
    │   ├── 2_分析/
    │   │   ├── readable.txt
    │   │   ├── sentences.txt
    │   │   ├── auto_selected.json
    │   │   └── 口误分析.md
    │   └── 3_审核/
    │       ├── review.html
    │       └── video.mp4 → 源视频(符号链接)
    ├── 字幕/
    │   ├── 1_转录/
    │   │   ├── audio.mp3
    │   │   └── volcengine_result.json
    │   ├── subtitles_with_time.json
    │   └── 3_输出/
    │       ├── video.srt
    │       └── video_字幕.mp4
    └── 高清化/
        └── video_hd.mp4
```

## 审批节点

1. **审核确认** — 剪口播 Step 6 完成后，用户在网页确认删除项
2. **发布确认** — 高清化完成后，用户确认最终成品

## 配置要求

### 必须：火山引擎 API Key

控制台：https://console.volcengine.com/speech/new/experience/asr?projectName=default

在工作区根目录创建 `.env`：

```bash
VOLCENGINE_API_KEY=your_api_key_here
```

详细配置见 [references/dependencies.md](references/dependencies.md)

## 脚本路径约定

所有脚本路径均相对于**本 SKILL.md 所在目录**：

```bash
# 转录（剪口播）
bash skills/剪口播/scripts/volcengine_transcribe.sh "audio_url"

# 剪辑视频
bash skills/剪口播/scripts/cut_video.sh input.mp4 delete_list.json output.mp4

# 高清导出
bash skills/高清化/scripts/hd_export.sh input.mp4 [output.mp4] [bitrate_multiplier]

# 字幕烧录
ffmpeg -i "video.mp4" -vf "subtitles='video.srt':force_style=..." -c:a copy output.mp4
```

详细步骤说明见 [references/workflow.md](references/workflow.md)
