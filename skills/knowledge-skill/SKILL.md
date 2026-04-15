---
name: knowledge-skill
displayName: Knowledge Skill
description: >
  个人知识管理系统。支持将多来源内容（B站、微信公众号、小红书、网页）入库到 PostgreSQL，
  并提供关键词搜索和向量语义搜索功能。自动生成 AI 摘要和向量嵌入。
  支持B站视频ASR语音转文字，小红书/B站夜间自动收割。
  Use when: 用户要求保存内容到知识库、搜索历史知识、管理知识条目。
  Triggers: "保存到知识库", "入库", "搜索知识", "我之前看过", "知识管理"。
tags:
  - Knowledge
  - Search
  - Automation
aliases:
  - 知识库
  - 入库
  - 搜索知识
scenarios:
  - 保存网页、视频或文章到个人知识库
  - 根据关键词或语义搜索历史内容
  - 夜间自动收割 B 站或小红书内容
---

# Knowledge Skill - 个人知识管理

将碎片化信息转化为结构化知识库。

## 功能

| 功能 | 脚本 | 说明 |
|------|------|------|
| 入库 | `knowledge_save.py` | 保存内容到知识库，自动生成 AI 摘要和 embedding |
| 搜索 | `knowledge_search.py` | 关键词 + 向量语义搜索（支持混合搜索） |
| URL入库 | `knowledge_save_from_url.py` | 从 URL 自动获取并入库（支持视频ASR转录） |
| 夜间收割 | `nightly_harvest.py` | B站 + 小红书自动收割（含ASR），cron 定时运行 |
| 评测 | `eval.py` | 知识库搜索质量评测 |

## 模型配置

| 用途 | 模型 | 提供方 | 说明 |
|------|------|--------|------|
| **Embedding** | `BAAI/bge-m3` | SiliconFlow | 1024 维向量，支持 8192 tokens |
| **ASR 语音转文本** | `TeleAI/TeleSpeechASR` | SiliconFlow | 免费，比 SenseVoiceSmall 效果好 |
| **AI 摘要** | `LongCat-Flash-Lite` | 龙猫 API | 免费生成一句话摘要 |

> ⚠️ SiliconFlow 免费模型需 chargeBalance > 0（giftBalance 不可用）
> 龙猫 API 完全免费，无需充值

## 快速开始

### 入库内容

```bash
# 基本入库（自动生成 AI 摘要）
uv run ~/.agents/skills/knowledge-skill/scripts/knowledge_save.py \
  --source-type bilibili \
  --source-id BV1xxx \
  --title "AI Agent 开发实战" \
  --content "视频文稿全文..."

# 带 metadata 入库
uv run ~/.agents/skills/knowledge-skill/scripts/knowledge_save.py \
  --source-type wechat \
  --source-id "article_123" \
  --title "深度学习入门" \
  --content "文章内容..." \
  --metadata '{"author": "张三", "account": "AI科技评论"}'

# 手动指定 AI 摘要
uv run ~/.agents/skills/knowledge-skill/scripts/knowledge_save.py \
  --source-type xiaohongshu \
  --source-id "note_123" \
  --title "OpenClaw 配置指南" \
  --content "完整内容..." \
  --ai-summary "OpenClaw 新手配置教程，讲解流式回复等核心设置。"
```

### 搜索知识

```bash
# 关键词搜索
uv run ~/.agents/skills/knowledge-skill/scripts/knowledge_search.py \
  --query "AI Agent" \
  --mode keyword

# 向量语义搜索
uv run ~/.agents/skills/knowledge-skill/scripts/knowledge_search.py \
  --query "如何开发一个智能助手" \
  --mode vector

# 混合搜索（推荐）
uv run ~/.agents/skills/knowledge-skill/scripts/knowledge_search.py \
  --query "RAG 技术" \
  --mode hybrid \
  --limit 10
```

### 夜间自动收割

```bash
# 手动运行一次
~/.agents/skills/knowledge-skill/.venv/bin/python3 \
  ~/.agents/skills/knowledge-skill/scripts/nightly_harvest.py

# Cron 配置（每晚3点）
0 3 * * * /home/q/.agents/skills/knowledge-skill/.venv/bin/python3 /home/q/.agents/skills/knowledge-skill/scripts/nightly_harvest.py >> /home/q/.agents/skills/knowledge-skill/harvest.log 2>&1
```

收割关键词：像素范、水球泡、一人公司、AI焦虑、AI Agent

### URL 一键入库

```bash
# B站视频（自动获取字幕或ASR转录）
uv run ~/.agents/skills/knowledge-skill/scripts/knowledge_save_from_url.py \
  --url "https://www.bilibili.com/video/BV1xxx"

# 小红书笔记
uv run ~/.agents/skills/knowledge-skill/scripts/knowledge_save_from_url.py \
  --url "https://www.xiaohongshu.com/discovery/item/xxx"

# 微信公众号（curl + 手机UA提取正文）
uv run ~/.agents/skills/knowledge-skill/scripts/knowledge_save_from_url.py \
  --url "https://mp.weixin.qq.com/s/xxx"

# 通用网页
uv run ~/.agents/skills/knowledge-skill/scripts/knowledge_save_from_url.py \
  --url "https://example.com/article"
```

## 来源类型

| source_type | 说明 | source_id 格式 |
|-------------|------|----------------|
| `bilibili` | B站视频 | BV号 |
| `wechat` | 微信公众号 | 文章ID |
| `xiaohongshu` | 小红书 | 笔记ID |
| `web` | 通用网页 | URL hash |
| `manual` | 手动录入 | 自定义ID |

## 数据库结构

```sql
knowledge_items (
  id            uuid PRIMARY KEY,
  source_type   varchar(50),
  source_id     varchar(255),
  source_url    text,
  title         varchar(500),
  content       text,           -- 原文
  summary       text,           -- 截取摘要
  ai_summary    text,           -- AI 一句话总结
  embedding     vector(1024),   -- 向量嵌入
  metadata      jsonb,
  created_at    timestamp,
  updated_at    timestamp
)
```

## 配置

配置文件位于 `.env`：

```env
# 数据库
DB_HOST=127.0.0.1
DB_PORT=5433
DB_USER=bili
DB_PASSWORD=bili123456
DB_NAME=bilibili

# SiliconFlow API (Embedding + ASR)
# Key 存储在 ~/.openclaw/secrets.env
SILICONFLOW_API_KEY=sk-xxx

# 龙猫 API (AI 摘要，免费)
# Key 存储在 ~/.openclaw/secrets.env
LONGCAT_API_KEY=ak-xxx

# 模型配置
EMBEDDING_MODEL=BAAI/bge-m3
ASR_MODEL=TeleAI/TeleSpeechASR

# 代理（可选）
HTTP_PROXY=http://127.0.0.1:7890

# 小红书 Cookie
XHS_COOKIE_PATH=~/.xiaohongshu-cli/cookies.json

# B站 Cookie
BILI_COOKIE_PATH=~/.bilibili-cookies.json
```

> ⚠️ API Key 请勿明文写入，统一存储在 `~/.openclaw/secrets.env`，详见军团共享文档 `API_KEY_MANAGEMENT.md`

## 注意事项

- **频率控制**: 搜索间隔 3-8 秒，ASR 间隔 10-20 秒，避免触发风控
- **ASR 仅限短视频**: 时长 < 30 分钟的视频才做 ASR
- **小红书 Cookie**: 约 7 天过期，失效时通过飞书通知
- **多集教程过滤**: 标题含"全"、"集"、"零基础"等关键词 ≥2 个自动跳过
- **Cron 环境**: 不加载 .env，脚本内需显式 `load_dotenv()`
