---
name: knowledge-skill
displayName: Knowledge Skill
description: >
  个人知识库技能。支持将网页、B站、微信公众号、小红书等内容入库到 PostgreSQL，
  并通过关键词或语义检索找回历史知识。自动生成 AI 摘要与向量嵌入，
  同时支持 URL 一键入库和夜间自动收割。
tags:
  - Knowledge
  - Search
  - Automation
aliases:
  - 知识库
  - 入库
  - 搜索知识
  - 历史知识
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
| 文档入库 | `knowledge_ingest_markdown.py` | 把仓库内 Markdown 文档作为 `docs` 来源导入知识池，扩充真实知识源 |
| Docs 知识种子 | `knowledge_seed_docs_items.py` | 导入一批高价值 story / spec 文档，帮助 showcase 走向 `real-sources` |
| Wiki Docs 种子 | `knowledge_seed_wiki_docs_items.py` | 导入更适合 wiki 编译线的 story / spec / showcase docs，提升 concept/entity 的 mentions 密度 |
| 演示知识种子 | `knowledge_seed_demo_items.py` | 写入更厚实的演示知识条目，稳定 showcase / recipe 的基础候选 |
| 搜索 | `knowledge_search.py` | 关键词 + 向量语义搜索（支持混合搜索） |
| 导出候选 | `knowledge_export.py` | 面向 agent 导出更完整的候选知识对象，补齐 `ai_summary`、`content`、`metadata` |
| AI摘要回填 | `knowledge_backfill_ai_summary.py` | 为旧条目或缺失条目批量补齐 AI 摘要，优先修复知识池短板 |
| 候选体检 | `knowledge_candidate_review.py` | 对导出候选做 deck 适配度评分、噪音识别和版式建议，帮助判断知识池质量 |
| Recipe Audit | `knowledge_recipe_audit.py` | 批量审阅 showcase recipes，快速看哪些 recipe 健康、哪些还在串题 |
| Knowledge Pool Report | `knowledge_pool_report.py` | 直接体检知识池本身，统计来源分布、AI 摘要覆盖率和薄弱条目 |
| Wiki Review | `knowledge_wiki_review.py` | 扫描 llm-wiki 编译结果，统计 source / concept / entity 页面，并标出偏薄页面与下一步建议 |
| 生成 Deck Brief | `knowledge_to_deck_brief.py` | 从导出的候选知识中筛选高价值内容，压成知识卡片，并生成可交给 PPT Skill 的结构化 brief |
| 运行 Deck Recipe | `knowledge_deck_recipe.py` | 从 markdown recipe 复跑 deck 选题参数，生成更稳定的 brief |
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
python skills/knowledge-skill/scripts/knowledge_save.py \
  --source-type bilibili \
  --source-id BV1xxx \
  --title "AI Agent 开发实战" \
  --content "视频文稿全文..."

# 带 metadata 入库
python skills/knowledge-skill/scripts/knowledge_save.py \
  --source-type wechat \
  --source-id "article_123" \
  --title "深度学习入门" \
  --content "文章内容..." \
  --metadata '{"author": "张三", "account": "AI科技评论"}'

# 手动指定 AI 摘要
python skills/knowledge-skill/scripts/knowledge_save.py \
  --source-type xiaohongshu \
  --source-id "note_123" \
  --title "OpenClaw 配置指南" \
  --content "完整内容..." \
  --ai-summary "OpenClaw 新手配置教程，讲解流式回复等核心设置。"
```

### 搜索知识

```bash
# 关键词搜索
python skills/knowledge-skill/scripts/knowledge_search.py \
  --query "AI Agent" \
  --mode keyword

# 向量语义搜索
python skills/knowledge-skill/scripts/knowledge_search.py \
  --query "如何开发一个智能助手" \
  --mode vector

# 混合搜索（推荐）
python skills/knowledge-skill/scripts/knowledge_search.py \
  --query "RAG 技术" \
  --mode hybrid \
  --limit 10
```

### 导出候选知识（给 Agent 用）

```bash
# 导出更完整的候选结果（含 ai_summary / content / metadata）
python skills/knowledge-skill/scripts/knowledge_export.py \
  --query "Agent Infrastructure" \
  --mode hybrid \
  --limit 10

# 控制 content 截断长度，避免结果过长
python skills/knowledge-skill/scripts/knowledge_export.py \
  --query "个人知识管理" \
  --mode hybrid \
  --limit 8 \
  --content-chars 800

# 先做候选体检，再决定要不要做 deck
python skills/knowledge-skill/scripts/knowledge_candidate_review.py \
  --query "Agent 基础设施" \
  --mode hybrid \
  --limit 8 \
  --min-score 5 \
  --output markdown

# 只看有 AI 摘要的高质量候选
python skills/knowledge-skill/scripts/knowledge_candidate_review.py \
  --query "AI 编程 工作流" \
  --mode hybrid \
  --limit 8 \
  --require-ai-summary \
  --output markdown

# 批量审阅所有 showcase recipe 的健康度
python skills/knowledge-skill/scripts/knowledge_recipe_audit.py \
  --write docs/showcase/reviews/index.md

# 直接看知识池快照，决定下一步该补哪些内容
python skills/knowledge-skill/scripts/knowledge_pool_report.py \
  --days 30 \
  --write docs/showcase/reviews/knowledge-pool.md

# 先预览哪些条目缺 AI 摘要，再批量回填
python skills/knowledge-skill/scripts/knowledge_backfill_ai_summary.py \
  --source-type bilibili \
  --limit 5 \
  --dry-run

python skills/knowledge-skill/scripts/knowledge_backfill_ai_summary.py \
  --source-type bilibili \
  --limit 5

# 重写 showcase 用的演示知识条目，让候选不再过薄
python skills/knowledge-skill/scripts/knowledge_seed_demo_items.py

# 把仓库内的高价值 Markdown 文档导入知识池
python skills/knowledge-skill/scripts/knowledge_ingest_markdown.py \
  --path docs/agent-stories/intel-agent.md \
  --path docs/agent-infra/knowledge-to-deck-agent-spec.md

# 一次性导入推荐的 docs 知识种子
python skills/knowledge-skill/scripts/knowledge_seed_docs_items.py

# 一次性导入更适合 wiki 编译线的 docs 种子
python skills/knowledge-skill/scripts/knowledge_seed_wiki_docs_items.py

# 体检当前 llm-wiki 编译结果
python skills/knowledge-skill/scripts/knowledge_wiki_review.py \
  --write docs/wiki/reviews/index.md
```

### 生成 Deck Brief（知识到展示）

```bash
# 生成结构化卡片 + deck brief（JSON）
python skills/knowledge-skill/scripts/knowledge_to_deck_brief.py \
  --query "Agent Infrastructure" \
  --mode hybrid \
  --cards 5 \
  --style swiss

# 生成人类更容易审阅的 Markdown 版本
python skills/knowledge-skill/scripts/knowledge_to_deck_brief.py \
  --query "个人知识管理" \
  --mode hybrid \
  --cards 4 \
  --style magazine \
  --audience "程序员 / 产品经理" \
  --output markdown

# 先限定来源，再生成更干净的专题卡片
python skills/knowledge-skill/scripts/knowledge_to_deck_brief.py \
  --query "AutoResearch" \
  --mode hybrid \
  --source-type test \
  --cards 2 \
  --style swiss \
  --output markdown

# 从 recipe 复跑一份 deck brief
python skills/knowledge-skill/scripts/knowledge_deck_recipe.py \
  --recipe docs/showcase/recipes/vector-database-decision-cards.md

# 输出 markdown 并写入文件
python skills/knowledge-skill/scripts/knowledge_deck_recipe.py \
  --recipe docs/showcase/recipes/autoresearch-knowledge-cards.md \
  --write /tmp/autoresearch-brief.md
```

如果某个主题容易串到不相关候选，可以在 recipe frontmatter 里补：

```yaml
requiredTerms:
  - autoresearch
excludedTerms:
  - 向量数据库
  - pgvector
```

这样 recipe runner 和 review runner 都会先按这组约束收紧候选池。

### Wiki 编译线体检

```bash
# 先补更适合 wiki 的 docs 知识种子
python skills/knowledge-skill/scripts/knowledge_seed_wiki_docs_items.py

# 再执行一轮 wiki 编译
python skills/knowledge-skill/scripts/wiki_compile.py --limit 5

# 扫描默认 llm-wiki 目录，输出 markdown 快照
python skills/knowledge-skill/scripts/knowledge_wiki_review.py \
  --write docs/wiki/reviews/index.md

# 输出 JSON，便于脚本消费
python skills/knowledge-skill/scripts/knowledge_wiki_review.py \
  --output json
```

如果这份 review 里出现大量：

- source 页面正文偏薄
- 未抽出概念/实体
- concept/entity 页面只有单一 mentions

说明当前问题主要在 `raw -> wiki` 的 compile 层，而不是 deck 展示层。

### 夜间自动收割

```bash
# 手动运行一次
python skills/knowledge-skill/scripts/nightly_harvest.py

# Cron 配置（每晚3点，路径按实际安装位置调整）
0 3 * * * python /path/to/skills/knowledge-skill/scripts/nightly_harvest.py >> /path/to/skills/knowledge-skill/harvest.log 2>&1
```

收割关键词：像素范、水球泡、一人公司、AI焦虑、AI Agent

### URL 一键入库

```bash
# B站视频（自动获取字幕或ASR转录）
python skills/knowledge-skill/scripts/knowledge_save_from_url.py \
  --url "https://www.bilibili.com/video/BV1xxx"

# 小红书笔记
python skills/knowledge-skill/scripts/knowledge_save_from_url.py \
  --url "https://www.xiaohongshu.com/discovery/item/xxx"

# 微信公众号（curl + 手机UA提取正文）
python skills/knowledge-skill/scripts/knowledge_save_from_url.py \
  --url "https://mp.weixin.qq.com/s/xxx"

# 通用网页
python skills/knowledge-skill/scripts/knowledge_save_from_url.py \
  --url "https://example.com/article"
```

## 来源类型

| source_type | 说明 | source_id 格式 |
|-------------|------|----------------|
| `bilibili` | B站视频 | BV号 |
| `wechat` | 微信公众号 | 文章ID |
| `xiaohongshu` | 小红书 | 笔记ID |
| `web` | 通用网页 | URL hash |
| `docs` | 仓库内 Markdown 文档 | 相对路径 |
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
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name

# SiliconFlow API (Embedding + ASR)
SILICONFLOW_API_KEY=sk-xxx

# 龙猫 API (AI 摘要，免费)
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

> ⚠️ API Key 请勿明文写入，建议通过环境变量或 `.env` 文件管理

## 注意事项

- **频率控制**: 搜索间隔 3-8 秒，ASR 间隔 10-20 秒，避免触发风控
- **ASR 仅限短视频**: 时长 < 30 分钟的视频才做 ASR
- **小红书 Cookie**: 约 7 天过期，失效时通过飞书通知
- **多集教程过滤**: 标题含"全"、"集"、"零基础"等关键词 ≥2 个自动跳过
- **Cron 环境**: 不加载 .env，脚本内需显式 `load_dotenv()`
- **Agent 消费建议**: 如果后续要做 deck、知识卡片或结构化筛选，优先使用 `knowledge_export.py`，不要直接消费 `knowledge_search.py` 的简化结果
- **展示前先体检**: 如果目标是做 deck 或知识精华展示，先跑 `knowledge_candidate_review.py` 看候选质量，再决定是否进入 `knowledge_to_deck_brief.py`
- **批量看健康度**: 如果 recipe 多起来，优先跑 `knowledge_recipe_audit.py`，先找出串题或候选过宽的 recipe，再做逐份 review
- **先看知识池**: 如果问题不是 recipe 串题，而是“库里就没什么好条目”，优先跑 `knowledge_pool_report.py`
- **优先补摘要**: 如果 `knowledge_pool_report.py` 显示某个来源的 AI 摘要覆盖率低，先跑 `knowledge_backfill_ai_summary.py`
- **样板过薄时先补种子**: 如果 deck 主要依赖演示条目，优先跑 `knowledge_seed_demo_items.py`，不要让 showcase 长期建立在过薄样例上
- **先把文档变成知识**: 如果仓库里已经有高价值 spec / story / 复盘文档，但 deck 还在靠 demo 条目，先跑 `knowledge_ingest_markdown.py` 或 `knowledge_seed_docs_items.py`
- **Deck 编排建议**: 如果目标是把知识变成展示资产，先跑 `knowledge_to_deck_brief.py`，再把生成的 brief 交给 `guizang-ppt-skill`
- **Recipe 优先**: 同一类 deck 需要反复调优时，优先沉淀为 `docs/showcase/recipes/*.md`，不要长期依赖手敲命令
- **主题收紧**: 如果 recipe 容易串题，优先增加 `requiredTerms` / `excludedTerms`，而不是一味提高分数阈值
