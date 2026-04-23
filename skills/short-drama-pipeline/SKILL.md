---
name: short-drama-pipeline
description: |
  AI 短剧/短视频全链路生产技能。从选题调研、脚本撰写、视频生成到成片输出的完整工作流。
  触发词：做一条短视频、做个短剧、AI短剧、帮我选题、生成视频、短视频制作、短剧制作、帮我创作。
  复用 tavily（调研）、xiaohongshu-cli/bilibili-cli（平台数据）、libtv-skill（视频生成）。
  所有子功能内置于 skills/ 子目录，无需单独安装。
allowed-tools: Bash(tvly *), Bash(bili *), Bash(xhs *), Bash(boss *), Read, Write, Glob, Grep
---

# short-drama-pipeline — AI 短剧/短视频全链路生产

选题 → 脚本 → 生成 → 成片，一个技能打通全流程。

## 快速开始

```
/short-drama-pipeline 帮我选个选题          # 只跑选题调研
/short-drama-pipeline 帮我做一条AI短视频     # 跑全流程
/short-drama-pipeline 做个修仙题材的短剧     # 带方向的全流程
```

## 内置子功能（skills/ 目录）

| 子目录 | 功能 | 依赖 |
|--------|------|------|
| `skills/topic-research/` | 选题调研：热点扫描 + 竞品数据 + 差异化建议 | tavily, xhs, bili |
| `skills/script-writer/` | 脚本撰写：创意简报（直接喂给 libtv-skill） | LLM |
| `skills/video-orchestrator/` | 视频生成编排：调用 libtv-skill 生成并下载 | libtv-skill |
| `skills/post-production/` | 后期合成：拼接 + 字幕 + 封面提取 | ffmpeg |

## MVP 工作流（4 步）

```
Step 1  选题调研    →  skills/topic-research/
Step 2  脚本撰写    →  skills/script-writer/
Step 3  视频生成    →  skills/video-orchestrator/
Step 4  后期合成    →  skills/post-production/
```

### 完整流程说明

**Step 1 — 选题调研**

详细步骤见 `skills/topic-research/README.md`。

```
1. 用户描述方向（或说"帮我选"）
2. tavily search — 搜索近期热点和趋势
3. xhs search — 小红书爆款数据（赞藏评）
4. bili search — B站播放数据
5. 综合分析 → 输出 3-5 个选题方案（附带数据支撑）
6. ⏸️ 审批节点：用户选择/确认选题后继续
```

**Step 2 — 脚本撰写**

详细步骤见 `skills/script-writer/README.md`。

```
1. 基于确定的选题，生成创意简报
2. 创意简报 = 一段自然语言描述，直接喂给 libtv-skill
3. 包含：题材、风格、内容概要、时长预期
4. ⏸️ 审批节点：用户确认创意简报后继续
```

**Step 3 — 视频生成**

详细步骤见 `skills/video-orchestrator/README.md`。

```
1. 将创意简报发送给 libtv-skill（create_session.py）
2. 每 8 秒轮询进展（query_session.py）
3. 生成完成后自动下载（download_results.py）
4. 结果保存到 output/assets/
```

**Step 4 — 后期合成**

详细步骤见 `skills/post-production/README.md`。

```
1. 抽取关键帧生成封面
2. 添加字幕（如有对话/旁白）
3. 输出成片到 output/final/
```

## 审批节点（必须等用户确认后继续）

1. **选题确认** — Step 1 完成后展示选题方案，用户选择后继续
2. **创意简报确认** — Step 2 完成后展示创意简报，用户确认后开始生成
3. **成片确认** — Step 4 完成后展示成片，用户确认满意

## 配置要求

**必须：**
- `LIBTV_ACCESS_KEY` 环境变量（用于 libtv-skill 视频生成）
- `tvly` 已登录（用于 tavily 搜索）
- `xhs` 已登录（用于小红书搜索）

**可选：**
- `bili` 已安装（用于 B站搜索）

## 脚本路径约定

所有路径均相对于**本 SKILL.md 所在目录**：

```bash
# 视频生成（通过 libtv-skill）
python3 ~/.claude/skills/libtv-skill/scripts/create_session.py "描述"

# 后期合成
bash skills/post-production/scripts/extract-cover.sh input.mp4 -o cover.jpg
bash skills/post-production/scripts/burn-subtitle.sh input.mp4 subtitle.srt -o output.mp4
bash skills/post-production/scripts/concat-videos.sh file1.mp4 file2.mp4 -o merged.mp4
```

## 输出目录

```
output/
├── drafts/      # 剧本、创意简报
├── assets/      # 生成的视频片段、封面
└── final/       # 最终成片
```
