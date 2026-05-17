---
title: AutoResearch 知识卡片样板
summary: 这是一份由 `knowledge-to-deck-agent` 最小闭环产出的展示样板。
category: knowledge-cards
sourceAgent: knowledge-to-deck-agent
tags:
  - knowledge
  - autoresearch
  - showcase
---

# AutoResearch 知识卡片样板

这是一份由 `knowledge-to-deck-agent` 最小闭环产出的展示样板。

## 生成链路

1. 用 `knowledge_export.py` 拉取适合 Agent 消费的完整候选
2. 用 `knowledge_to_deck_brief.py` 生成知识卡片和 deck brief
3. 参考 `guizang-ppt-skill` 的 Swiss 风格模板，整理成单文件 HTML deck

## 本次命令

```bash
uv run skills/knowledge-skill/scripts/knowledge_to_deck_brief.py \
  --query "AutoResearch" \
  --mode hybrid \
  --source-type test \
  --limit 4 \
  --cards 2 \
  --style swiss \
  --audience "程序员 / 产品经理" \
  --output markdown
```

## 知识卡片

### Card 1

- Title: AutoResearch评测条目
- Takeaway: AutoResearch评测用测试条目
- Why it matters: 这条内容与主题「AutoResearch」相关，且具备进一步压缩成展示卡片的潜力，对程序员 / 产品经理更值得关注。
- Evidence or example: 关键：评判标准必须想清楚
- Suggested slide type: statement

### Card 2

- Title: 向量数据库选型对比
- Takeaway: 对比了 pgvector、Milvus、Weaviate 三个向量数据库
- Why it matters: 这条内容与主题「AutoResearch」相关，且具备进一步压缩成展示卡片的潜力，对程序员 / 产品经理更值得关注。
- Evidence or example: pgvector 最轻量适合小规模，Milvus 性能最好适合大规模生产，Weaviate 内置 AI 管道但较重
- Suggested slide type: comparison

## Deck Brief

- Theme: AutoResearch
- Style: swiss
- Audience: 程序员 / 产品经理
- Card count: 2

## 备注

- 这份样板故意选了当前知识库里最干净的一组候选，重点验证“链路闭环”，不是追求内容广度
- 后续真实展示样板应优先来自更高质量的知识条目，而不是评测数据
