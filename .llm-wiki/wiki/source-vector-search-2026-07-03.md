---
type: source
source_path: "."
date: 2026-07-03
tags: [cli, vector-search, embeddings, bge-m3, siliconflow, hybrid-search, rrf, i18n]
---

# Source: 向量检索功能实现（2026-07-03）

> 项目根目录摄取，覆盖 CLI v1.4.0 → v1.7.0 的向量检索全链路实现。

## Key Takeaways

1. **向量检索功能上线**：CLI search 命令新增基于 [[siliconflow-api|SiliconFlow API]]（[[bge-m3|BGE-M3 模型]]）的语义搜索能力
2. **混合搜索架构**：采用 [[vector-search|RRF 混合搜索]]，关键词权重 3x 优先于向量检索
3. **嵌入文本策略优化**：用 i18n 中文描述替代原始 description，控制在 150-200 字符，显著提升跨语言匹配质量
4. **跨语言关键词匹配**：新增 ZH_EN_ALIASES 映射表（"幻灯片"→"PPT"），支持中文查询匹配英文技能
5. **配置管理**：新增 `config` 子命令管理 API Key（`~/.config/custom-skills/config.json`）
6. **CLI 版本从 1.3.3 升级到 1.7.0**，共 4 个版本迭代

## 新增文件

| 文件 | 说明 |
|------|------|
| `cli/src/utils/vector-search.ts` | 向量检索核心模块：API 调用、余弦相似度、RRF 融合 |
| `scripts/generate-embeddings.ts` | 构建时批量生成技能嵌入向量（SiliconFlow BGE-M3） |
| `registry/skills-embeddings.json` | 预计算的 73 个技能嵌入向量（1024 维，~2.2MB） |

## 修改文件

| 文件 | 改动 |
|------|------|
| `cli/src/commands/search.ts` | 新增 `--vector`/`--api-key`/`--api-base`/`--model` 选项 |
| `cli/src/index.ts` | 新增 `config` 子命令 |
| `cli/src/utils/cache.ts` | 新增 `readConfig`/`writeConfig` 配置管理 |
| `cli/src/utils/data-fetcher.ts` | 泛型化 fetchFromUrl + 新增 `loadEmbeddingsData` |
| `cli/src/utils/matcher.ts` | 新增 ZH_EN_ALIASES 中英映射 + 中文子串提取 + n-gram 模糊匹配 |
| `cli/src/utils/output.ts` | `printSkillCard` 描述截断至 120 字符 |
| `cli/src/utils/vector-search.ts` | RRF 权重调优（keywordWeight=3.0, k=30） |

## 演进记录

| 版本 | 变更 | 效果 |
|------|------|------|
| 1.4.0 | 初始向量检索（BGE-M3 + RRF k=60） | 基础语义搜索可用 |
| 1.5.0 | 中文跨语言匹配（ZH_EN_ALIASES + 子串提取） | "帮我做个幻灯片"→frontend-slides |
| 1.6.0 | 嵌入文本策略优化（i18n 中文描述替代原始 description） | 区分度显著提升 |
| 1.7.0 | RRF 调权（keywordWeight 3x, k=30）+ 描述截断 | 关键词匹配优先级高于向量 |

## 设计决策

1. **预计算嵌入 + 运行时查询向量**：嵌入在构建时通过 SiliconFlow API 生成并存储在 registry，运行时只对用户查询做一次 embedding API 调用
2. **混合搜索而非纯向量**：保留原有关键词匹配（精确/前缀/包含），向量检索作为补充，通过 RRF 融合
3. **无 API Key 降级**：未配置 API Key 时自动降级为纯关键词搜索，零破坏性
4. **嵌入文本用 i18n 描述**：73/73 技能均有中文描述覆盖，语义聚焦且长度统一

## 已知限制

- BGE-M3 跨语言匹配对概念性查询（如"优化代码质量"）仍有限制，依赖关键词映射补充
- 嵌入向量需定期重新生成（技能更新后需运行 `generate-embeddings.ts`）
- 嵌入文件 2.2MB，对 npm 包体积有一定影响

## Notable Contradictions

- 无与现有 wiki 内容的矛盾

相关：[[vector-search]], [[siliconflow-api]], [[cli-tool]], [[architecture]], [[release-process]]
