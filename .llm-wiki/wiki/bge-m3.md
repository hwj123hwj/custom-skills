---
type: entity
date: 2026-07-03
tags: [model, embedding, bge-m3, multilingual, nlp]
---

# BGE-M3

> BAAI 发布的多语言嵌入模型，通过 [[siliconflow-api|SiliconFlow API]] 免费调用。用于 CLI [[vector-search|向量检索]]的语义匹配。

## 基本信息

| 属性 | 值 |
|------|-----|
| 全称 | BAAI/bge-m3 |
| 发布方 | 北京智源人工智能研究院（BAAI） |
| 嵌入维度 | 1024 |
| 上下文窗口 | ~512 token |
| 多语言支持 | 中英文等 100+ 语言 |
| 调用方式 | [[siliconflow-api|SiliconFlow API]] `/embeddings` |

## 在本项目中的应用

### 嵌入生成

`scripts/generate-embeddings.ts` 使用 BGE-M3 为每个技能生成嵌入向量。

嵌入文本格式：`{name} | {description} | 标签: {tags}`

- 优先使用 i18n 中文描述（50-100 字符）
- 控制在 200 字符内，避免超出上下文窗口

### 查询嵌入

CLI 运行时对用户查询调用 BGE-M3 API 生成查询向量，再与预计算的技能向量做余弦相似度。

## 已知限制

1. **跨语言匹配区分度有限**：中文查询对英文技能的余弦相似度集中在 0.45-0.55 区间，差异较小
2. **长文本截断**：超过 ~512 token 的文本会被截断，影响嵌入质量
3. **概念性查询**：对"优化代码质量"等抽象概念的语义理解有限，需依赖关键词映射补充

## 替代方案考虑

- 本地 ONNX 模型（零 API 依赖，但增加包体积）
- OpenAI text-embedding-3-small（付费，质量更高）
- 当前方案（SiliconFlow BGE-M3 免费）是成本和质量的最佳平衡

相关：[[siliconflow-api]], [[vector-search]], [[cli-tool]]
