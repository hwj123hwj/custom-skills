---
type: concept
date: 2026-07-03
tags: [vector-search, embeddings, rrf, hybrid-search, cosine-similarity, bge-m3]
---

# Vector Search

> CLI 的向量检索能力，基于 [[siliconflow-api|SiliconFlow API]] 的 [[bge-m3|BGE-M3]] 嵌入模型，通过 RRF 融合关键词匹配和语义检索。

## 搜索模式

| 模式 | 触发条件 | 说明 |
|------|----------|------|
| 🔀 hybrid（默认） | 有 API Key | 关键词 + 向量 RRF 融合 |
| 🎯 vector | `--vector` 显式指定 | 纯向量余弦相似度 |
| 🔤 keyword | 无 API Key | 原有关键词匹配（向后兼容） |

## 混合搜索架构

```
用户查询 "帮我做个幻灯片"
  ├─ 关键词路径: scoreSkill() → 11 个结果（通过 ZH_EN_ALIASES 映射）
  ├─ 向量路径: embedQuery() → cosine similarity → 15 个结果
  └─ RRF 融合: keywordWeight=3.0, vectorWeight=1.0, k=30
       → frontend-slides (#1), guizang-ppt-skill (#2), huashu-design (#3)
```

## RRF（Reciprocal Rank Fusion）

公式：`score = Σ weight / (k + rank_i)`

| 参数 | 值 | 说明 |
|------|-----|------|
| keywordWeight | 3.0 | 关键词匹配权重 3 倍于向量 |
| vectorWeight | 1.0 | 向量检索基础权重 |
| k | 30 | 衰减常数（越小前排差距越大） |
| vectorTopK | min(limit*2, 15) | 向量结果上限 |

**关键设计**：关键词无结果时直接返回向量结果（保留真实余弦相似度分数），避免 RRF 分数扁平化。

## 嵌入文本策略

每个技能的嵌入文本格式：

```
{name} | {description} | 标签: {tags}
```

- 优先使用 i18n 中文描述（人工维护，50-100 字符）
- 无中文描述时回退到英文 description（截断至 200 字符）
- 不包含 scenarios 和触发词列表（避免过长）
- 73/73 技能均有中文描述覆盖

## 跨语言关键词匹配

matcher.ts 中的 `ZH_EN_ALIASES` 映射表支持中文查询匹配英文技能：

| 中文关键词 | 对应英文 |
|-----------|---------|
| 幻灯片 | ppt, slides, presentation, deck |
| 视频 | video |
| 图片 | image, picture, photo |
| 文档 | document, doc, word |
| 搜索 | search |

匹配流程：
1. 从查询中提取中文子串（2-6 字滑动窗口）
2. 对每个子串检查直接匹配 + 映射表匹配
3. n-gram Jaccard 相似度兜底

## 配置管理

```bash
# 设置 API Key（永久保存）
npx custom-skills config --set-key <siliconflow-key>

# 查看配置
npx custom-skills config --show

# 环境变量（临时）
export SILICONFLOW_API_KEY=<key>
```

配置文件位置：`~/.config/custom-skills/config.json`

## 嵌入向量生成

```bash
# 重新生成嵌入（技能更新后需执行）
SILICONFLOW_API_KEY=sk-xxx npx tsx scripts/generate-embeddings.ts
```

输出：`registry/skills-embeddings.json`（73 个 1024 维向量，~2.2MB）

相关：[[siliconflow-api]], [[bge-m3]], [[cli-tool]], [[architecture]]
