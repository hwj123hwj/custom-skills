---
name: knowledge-skill
displayName: Knowledge Skill
description: >
  个人知识流水线技能。将网页、B站、微信公众号、小红书、Markdown 等内容先入库到
  PostgreSQL 原料池，再编译为 Agent 友好的 Markdown / LLM Wiki 知识网络。
  支持 URL 入库、摘要与向量、Markdown 检索、Wiki 编译、飞书知识库发布、记忆层整理和夜间自动收割。
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
  - 保存网页、视频或文章到 PostgreSQL 原料池
  - 将原料编译成 Markdown / LLM Wiki 知识网络
  - 使用 rg/Markdown 文件检索已编译知识
  - 将本地 Markdown / LLM Wiki 发布到飞书知识库
  - 夜间自动收割 B 站或小红书内容
---

# Knowledge Skill - 个人知识流水线

将碎片化信息转化为可检索、可阅读、可沉淀的结构化知识。

核心分层：

```text
PostgreSQL knowledge_items = 原料池 / 采集池 / 状态层
memory_cards               = 结构化记忆卡 / 中间整理层
.llm-wiki/wiki/*.md        = Agent 优先检索的 Markdown 编译层
Feishu / Lark              = 人类编辑、协作、展示和长期沉淀层
```

当用户要“查资料、召回历史内容、找原始证据”时，用 PG / memory 脚本；当用户要“沉淀成知识库、让 Agent 以后能直接读”时，优先走 `.llm-wiki` Markdown 编译工作流。详细规则见 `references/llm-wiki-workflow.md`。

## 功能

| 功能 | 脚本 | 说明 |
|------|------|------|
| 入库 | `knowledge_save.py` | 保存内容到知识库，自动生成 AI 摘要和 embedding |
| 文档入库 | `knowledge_ingest_markdown.py` | 把仓库内 Markdown 文档作为 `docs` 来源导入知识池，扩充真实知识源 |
| Docs 知识种子 | `knowledge_seed_docs_items.py` | 导入一批高价值 story / spec 文档，帮助 showcase 走向 `real-sources` |
| Wiki Docs 种子 | `knowledge_seed_wiki_docs_items.py` | 导入更适合 wiki 编译线的 story / spec / showcase docs，提升 concept/entity 的 mentions 密度 |
| 演示知识种子 | `knowledge_seed_demo_items.py` | 写入更厚实的演示知识条目，稳定 showcase / recipe 的基础候选 |
| 搜索 | `knowledge_search.py` | 关键词 + 向量语义搜索（支持混合搜索） |
| Markdown 检索 | `knowledge_md_search.py` | 用 `rg` / 文件扫描检索已编译的 Markdown 知识层 |
| 导出候选 | `knowledge_export.py` | 自包含的 agent 导出层：混合搜索 + 补齐 `ai_summary`、`content_preview`、`metadata`，关键词搜索也匹配 `ai_summary` |
| AI摘要回填 | `knowledge_backfill_ai_summary.py` | 为旧条目或缺失条目批量补齐 AI 摘要，优先修复知识池短板 |
| 候选体检 | `knowledge_candidate_review.py` | 对导出候选做 deck 适配度评分、噪音识别和版式建议，帮助判断知识池质量 |
| Recipe Audit | `knowledge_recipe_audit.py` | 批量审阅 showcase recipes，快速看哪些 recipe 健康、哪些还在串题 |
| Knowledge Pool Report | `knowledge_pool_report.py` | 直接体检知识池本身，统计来源分布、AI 摘要覆盖率和薄弱条目 |
| Wiki 初始化 | `knowledge_wiki_init.py` | 初始化 DeepV-style `.llm-wiki/raw + wiki + index.md + log.md` 目录结构 |
| Wiki 状态 | `knowledge_wiki_status.py` | 统计 raw 文件、wiki 页面、source 页面和最近维护日志 |
| Wiki Review | `knowledge_wiki_review.py` | 扫描 llm-wiki 编译结果，统计 source / concept / entity 页面，标出偏薄页面，并输出可执行的编译目标命令 |
| Wiki Coverage | `knowledge_wiki_coverage.py` | 桥接 raw 知识池和 wiki 编译产出的覆盖率报告，分析未编译条目、薄弱 concept/entity，生成定向编译建议 |
| 发布到飞书知识库 | `knowledge_publish_feishu.py` | 直接调用飞书 OpenAPI，把本地 Markdown 导入为 docx 并迁入 Wiki 知识空间；运行时不依赖 `lark-cli` |
| 生成 Deck Brief | `knowledge_to_deck_brief.py` | 从导出的候选知识中筛选高价值内容，压成知识卡片，并生成可交给 PPT Skill 的结构化 brief |
| 运行 Deck Recipe | `knowledge_deck_recipe.py` | 从 markdown recipe 复跑 deck 选题参数，生成更稳定的 brief |
| URL入库 | `knowledge_save_from_url.py` | 从 URL 自动获取并入库（支持视频ASR转录） |
| 夜间收割 | `nightly_harvest.py` | B站 + 小红书自动收割（含ASR），cron 定时运行 |
| **记忆表迁移** | `memory_migrate.py` | 创建 `memory_cards` 分层记忆表及索引 |
| **记忆整理** | `memory_organize.py` | 从 `knowledge_items` 提取高质量条目，生成 L2 领域知识卡片（结构化摘要 + 去重） |
| **分层检索** | `memory_recall.py` | L1 工作记忆 → L2 领域知识 → L3 原始存档，逐层召回 |
| **写入工作记忆** | `memory_save_working.py` | Agent 任务中的关键决策写入 L1（自动设置 7 天有效期） |
| **记忆压缩** | `memory_compress.py` | 定期压缩：L1→L2 降级 + L2 冷门归档 + 相似合并 |
| **概念时间线** | `memory_timeline.py` | 按时间展示某概念的演化路径 |
| **记忆健康度** | `memory_health.py` | 分层统计、覆盖率、冷门卡片、疑似重复、摘要质量抽检 |
| **自进化调优** | `memory_self_tune.py` | 紫金花机制：六维指标采集 → 爬山调参 → 棘轮回退 → TSV 追踪 |
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

### Markdown / LLM Wiki 编译层

```bash
# 初始化当前项目的 .llm-wiki
python skills/knowledge-skill/scripts/knowledge_wiki_init.py \
  --root .llm-wiki \
  --output markdown

# 查看 wiki 状态
python skills/knowledge-skill/scripts/knowledge_wiki_status.py \
  --root .llm-wiki

# 用 rg 优先检索已编译 wiki 页面
python skills/knowledge-skill/scripts/knowledge_md_search.py \
  --root .llm-wiki/wiki \
  --query "Agent"
```

LLM Wiki 维护方式：

1. 把原始材料放进 `.llm-wiki/raw/`，或指定任意源文件。
2. Agent 读取源文件，提取实体、概念、事实、关系和矛盾点。
3. Agent 在 `.llm-wiki/wiki/` 创建 `source-*`、`entity-*`、`concept-*` 页面。
4. Agent 更新 `.llm-wiki/index.md` 和 `.llm-wiki/log.md`。
5. 后续查询优先读 `.llm-wiki/index.md` 和 `.llm-wiki/wiki/`，不要直接把 raw 当答案来源。

如果要执行 DeepV-style 的 ingest/query/lint 流程，先阅读：

```text
skills/knowledge-skill/references/llm-wiki-workflow.md
```

### 发布 Markdown 到飞书知识库

适用于“机器人 / Agent 后端把本地编译好的 Markdown 传到飞书，作为人类可编辑的知识库页面”。脚本直接调用飞书 OpenAPI，不要求本地安装 `lark-cli`。

首次运行前配置环境变量：

```bash
export FEISHU_APP_ID=cli_xxx
export FEISHU_APP_SECRET=xxx
export FEISHU_TARGET_URL=https://example.feishu.cn/wiki/wikcn_xxx
# 也可以不用 URL，改为显式传 space_id
export FEISHU_TARGET_SPACE_ID=spc_xxx
# 可选：发布到某个 Wiki 父页面下
export FEISHU_TARGET_PARENT_TOKEN=wikcn_xxx
```

应用需要具备文档导入、素材上传、Wiki 节点移动/读取等权限，并且应用或机器人需要被加入目标知识库，否则 OpenAPI 会返回权限错误。
如果配置了 `FEISHU_TARGET_URL`，脚本会调用 Wiki `get_node` 自动解析 `space_id` 和父页面 `node_token`。

```bash
# 预览将发布哪些 Markdown，不写入飞书
python skills/knowledge-skill/scripts/knowledge_publish_feishu.py \
  --source .llm-wiki/wiki

# 执行发布：导入 md 为 docx，再迁入目标 Wiki 知识库
python skills/knowledge-skill/scripts/knowledge_publish_feishu.py \
  --source .llm-wiki/wiki \
  --execute

# 保留目录层级：子目录会变成轻量目录页，md 会挂在对应目录页下
python skills/knowledge-skill/scripts/knowledge_publish_feishu.py \
  --source .llm-wiki/wiki \
  --execute

# 扁平发布到目标父节点下
python skills/knowledge-skill/scripts/knowledge_publish_feishu.py \
  --source .llm-wiki/wiki \
  --flat \
  --execute

# 已有映射且内容变化时，覆盖更新原 docx，而不是重新导入新文档
python skills/knowledge-skill/scripts/knowledge_publish_feishu.py \
  --source .llm-wiki/wiki \
  --update-existing \
  --execute

# 无凭证离线自测 OpenAPI 编排逻辑
python skills/knowledge-skill/scripts/knowledge_publish_feishu_selftest.py
```

同步状态默认保存在 `.llm-wiki/feishu-sync.json`。它记录 `local path -> sha256/doc_token/wiki_token`，用于跳过未变化文件和避免重复发布。

### 记忆层管理（L1/L2/L3 分层）

```bash
# 初始化记忆表（首次使用）
python skills/knowledge-skill/scripts/memory_migrate.py

# 从 knowledge_items 提取 L2 领域知识卡片
python skills/knowledge-skill/scripts/memory_organize.py --limit 10

# 预览模式（不写入数据库）
python skills/knowledge-skill/scripts/memory_organize.py --dry-run --source-type docs --limit 5

# 分层检索（L1 → L2 → L3 逐层召回）
python skills/knowledge-skill/scripts/memory_recall.py \
  --query "Agent 基础设施" \
  --mode hybrid \
  --limit 5

# 带 context_tags 精确检索
python skills/knowledge-skill/scripts/memory_recall.py \
  --query "API Key" \
  --context-tags "project:knowledge-skill"

# 写入 L1 工作记忆（Agent 任务中的关键决策）
python skills/knowledge-skill/scripts/memory_save_working.py \
  --title "决定使用 pgvector 而非 Milvus" \
  --summary "pgvector 轻量、与 PostgreSQL 原生集成，适合个人知识库规模" \
  --keywords "pgvector,选型,向量数据库" \
  --context-tags "project:knowledge-skill"

# 记忆压缩（L1降级 + L2归档 + 相似合并）
python skills/knowledge-skill/scripts/memory_compress.py

# 预览压缩效果
python skills/knowledge-skill/scripts/memory_compress.py --dry-run

# 概念时间线（展示某概念的演化路径）
python skills/knowledge-skill/scripts/memory_timeline.py \
  --query "Agent" \
  --output markdown

# 记忆健康度报告
python skills/knowledge-skill/scripts/memory_health.py --output markdown

# 写入报告到文件
python skills/knowledge-skill/scripts/memory_health.py \
  --output markdown \
  --write docs/wiki/reviews/memory-health.md

# 自进化调优（dry-run，只采集指标不调参）
python skills/knowledge-skill/scripts/memory_self_tune.py --dry-run

# 自进化调优（实际调优：采集→爬出最差维度→调参→验证→keep/revert）
python skills/knowledge-skill/scripts/memory_self_tune.py

# 强制调优（即使综合分 >= 80 也执行）
python skills/knowledge-skill/scripts/memory_self_tune.py --force

# 输出 markdown 格式的调优报告
python skills/knowledge-skill/scripts/memory_self_tune.py --dry-run --output markdown
```

### 导出候选知识（给 Agent 用）

```bash
# 导出更完整的候选结果（含 ai_summary / content_preview / metadata）
python skills/knowledge-skill/scripts/knowledge_export.py \
  --query "Agent Infrastructure" \
  --limit 8

# 筛选特定来源
python skills/knowledge-skill/scripts/knowledge_export.py \
  --query "个人知识管理" \
  --limit 8 \
  --source-type bilibili

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

# 再执行一轮 wiki 编译（增强版：提取关键论点+来源语境）
python skills/knowledge-skill/scripts/wiki_compile.py --limit 5

# 重编译已有条目（用增强版 LLM prompt 覆盖旧页面，补充语境和关键论点）
python skills/knowledge-skill/scripts/wiki_compile.py --recompile --limit 5

# 定向增强特定 concept/entity（优先编译能增强薄页面的条目）
python skills/knowledge-skill/scripts/wiki_compile.py --limit 5 \
  --target-concept 'Agent' --target-entity 'OpenAI'

# 扫描默认 llm-wiki 目录，输出 markdown 快照（含可执行编译建议）
python skills/knowledge-skill/scripts/knowledge_wiki_review.py \
  --write docs/wiki/reviews/index.md

# 输出 JSON，便于脚本消费
python skills/knowledge-skill/scripts/knowledge_wiki_review.py \
  --output json

# Wiki 覆盖率报告（桥接 raw 知识池和 wiki 编译产出）
python skills/knowledge-skill/scripts/knowledge_wiki_coverage.py \
  --write docs/wiki/reviews/coverage.md
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

memory_cards (
  id              uuid PRIMARY KEY,
  layer           smallint,       -- 1=工作记忆 2=领域知识 3=原始存档
  title           text,
  summary         text,           -- 结构化摘要（结论 | 前提 | 时效）
  keywords        text[],         -- 概念标签
  context_tags    text[],         -- 上下文标签（项目名、技术栈等）
  valid_from      timestamp,
  valid_until     timestamp,      -- NULL = 长期有效
  source_item_ids text[],         -- 指向 knowledge_items 原始条目
  related_card_ids uuid[],        -- 关联的其他 memory_cards
  embedding       vector(1024),
  access_count    int,            -- 被召回次数
  last_accessed   timestamp,
  confidence      real,           -- 可信度（0 = 已归档）
  created_at      timestamp,
  updated_at      timestamp
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
- **记忆层优先**: Agent 检索知识时，优先使用 `memory_recall.py`（L1→L2→L3 分层召回），比直接用 `knowledge_search.py` 更精准
- **定期整理**: 建议每周运行 `memory_organize.py`，将新的高质量条目提取为 L2 卡片
- **定期压缩**: 建议每天运行 `memory_compress.py`（可 cron），保持记忆层干净
- **写入工作记忆**: Agent 在任务中做出关键决策时，用 `memory_save_working.py` 写入 L1，7 天内可快速召回
- **先看健康度**: 如果不确定记忆系统状态，先跑 `memory_health.py` 看分层统计和覆盖率
- **自进化调优**: `memory_self_tune.py` 会自动爬山调参，建议 cron 每周运行一次，参数变更记录在 `tune-results.tsv`
- **调参安全**: 自进化使用棘轮机制——调参后指标不改善会自动回退到旧参数，不会让系统变差
- **强制调优**: 如果综合分 >= 80 但仍想微调，使用 `--force` 标志
- **Wiki 编译工作流**: review → coverage → compile 反馈闭环：先跑 `knowledge_wiki_review.py` 看薄弱页面，再跑 `knowledge_wiki_coverage.py` 看覆盖率，最后按建议跑 `wiki_compile.py --target-concept/entity` 定向增强
- **Wiki 重编译**: 如果已有条目是旧版编译产物（缺少关键论点、来源语境），用 `wiki_compile.py --recompile` 重新提取，覆盖旧页面
- **Wiki 密度优先**: wiki 编译线的目标不是页面数量，而是 concept/entity 页面的 mentions 密度和来源语境覆盖
