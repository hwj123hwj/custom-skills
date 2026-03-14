---
name: knowledge-skill
description: >
  个人知识管理系统。支持将多来源内容（B站、微信公众号、小红书、网页）入库到 PostgreSQL，
  并提供关键词搜索和向量语义搜索功能。自动生成 AI 摘要和向量嵌入。
  Use when: 用户要求保存内容到知识库、搜索历史知识、管理知识条目。
  Triggers: "保存到知识库", "入库", "搜索知识", "我之前看过", "知识管理"。
---

# Knowledge Skill - 个人知识管理

将碎片化信息转化为结构化知识库。

## 功能

| 功能 | 脚本 | 说明 |
|------|------|------|
| 入库 | `knowledge_save.py` | 保存内容到知识库，自动生成 AI 摘要和 embedding |
| 搜索 | `knowledge_search.py` | 关键词 + 向量语义搜索 |
| URL入库 | `knowledge_save_from_url.py` | 从 URL 自动获取并入库（支持视频转录） |

## 模型配置

| 用途 | 模型 | 说明 |
|------|------|------|
| **Embedding** | `BAAI/bge-m3` | 支持 8192 tokens，1024 维向量 |
| **ASR 语音转文本** | `TeleAI/TeleSpeechASR` | 免费，需 WAV 格式 |
| **AI 摘要** | `Qwen/Qwen2.5-7B-Instruct` | 免费生成一句话摘要 |

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

### URL 一键入库

```bash
# B站视频（自动获取字幕）
uv run ~/.agents/skills/knowledge-skill/scripts/knowledge_save_from_url.py \
  --url "https://www.bilibili.com/video/BV1xxx"

# 小红书视频（自动转录）
# 需要先登录小红书
uv run ~/.agents/skills/xiaohongshu-skills/scripts/cli.py login
uv run ~/.agents/skills/knowledge-skill/scripts/knowledge_save_from_url.py \
  --url "https://www.xiaohongshu.com/discovery/item/xxx"

# 微信公众号
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

# SiliconFlow API
SILICONFLOW_API_KEY=sk-xxx

# 模型配置
EMBEDDING_MODEL=BAAI/bge-m3
ASR_MODEL=TeleAI/TeleSpeechASR
AI_SUMMARY_MODEL=Qwen/Qwen2.5-7B-Instruct
```