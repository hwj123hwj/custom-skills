# Agent Memory 方法论 — 知识库技能优化指南

> 核心论点：Memory 不是"把历史对话塞进向量库"，是**上下文管理**——什么值得留、怎么组织、什么时候取出来用。
> 存储 ≠ 记忆。**提取和整理 > 存储和检索**。

---

## 一、四组件框架

一个完整的 Agent Memory 系统由四个组件构成，缺一不可：

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   ① 写入    │───>│   ② 组织    │───>│   ③ 检索    │───>│   ④ 淘汰    │
│  Extraction  │    │  Organize   │    │  Retrieval  │    │  Eviction   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
   "什么值得留"      "怎么存才好用"     "用时怎么找到"     "旧的怎么清理"
```

| 组件 | 职责 | 常见错误 |
|------|------|----------|
| **① 写入（提取）** | 判断信息是否值得记忆；提取结构化摘要 | 全量存储，不做筛选 |
| **② 组织（整理）** | 分层分类、打标签、建关联、去重合并 | 扁平堆放，无层级无关联 |
| **③ 检索（召回）** | 语义 + 关键词混合搜索，按上下文排序 | 纯向量相似度，无场景感知 |
| **④ 淘汰（压缩）** | 定期合并、降级、归档、删除过期信息 | 只进不出，记忆膨胀 |

**第一个坑就是只做了 ①③，跳过 ②④。** 记忆越攒越多，最后跟垃圾堆一样。

---

## 二、六阶段路线图

```
阶段 1 ── 存文件           ──── 最基础的持久化
阶段 2 ── 加结构化标签     ──── 让记忆可分类、可筛选
阶段 3 ── 上混合检索       ──── 语义 + 关键词，覆盖模糊和精确两种查询
阶段 4 ── 分层记忆         ──── 工作记忆 / 领域知识 / 原始存档，按需召回
阶段 5 ── 图谱 / 时间线    ──── 概念关联 + 时序追溯
阶段 6 ── 自进化           ──── 记忆系统自我评估、自我优化
```

大多数人做到 2-3 就够用。

---

## 三、当前 knowledge-skill 状态评估

> 最后更新：2026-05-18

| 阶段 | 状态 | 已有能力 | 缺口 |
|------|------|----------|------|
| **阶段 1 存文件** | ✅ 完成 | `knowledge_save.py`、URL 导入、Markdown 导入、nightly harvest | — |
| **阶段 2 结构化标签** | ✅ 完成 | `source_type`、`metadata` JSONB、AI summary、`memory_cards.keywords` 概念标签、`valid_from/until` 时效标注 | — |
| **阶段 3 混合检索** | ✅ 完成 | `knowledge_search.py` 支持关键词/向量/混合 | — |
| **阶段 4 分层记忆** | ✅ 完成 | `memory_cards` 表（L1/L2/L3）、`memory_organize.py` 整理器、`memory_recall.py` 分层检索、`memory_save_working.py` L1 写入、`memory_compress.py` 压缩 | — |
| **阶段 5 图谱/时间线** | ✅ 完成 | `memory_timeline.py` 概念时间线、`wiki_compile.py` 概念提取与 `memory_cards` 双向关联 | — |
| **阶段 6 自进化** | ✅ 完成 | `memory_health.py` 健康度报告、`memory_self_tune.py` 爬山调优 + 棘轮回退、`.tune-params.env` 动态参数注入、TSV 追踪、低召回检测 | — |

**总结：已完成阶段 3→4 的跨越。** L1/L2/L3 分层记忆系统已落地，核心四组件（写入→组织→检索→淘汰）全部可用。

---

## 四、三个核心判断

### 判断 1：分层/树状 > 扁平向量库

扁平只能找相似条目，树和分层可以同时保留"概念"和"细节"。

**落地含义：**
- `knowledge_items` 保持为 L3 原始存档层（不动）
- 新建 `memory_cards` 表作为 L1/L2 整理层
- L1 = 工作记忆（当前任务相关，高时效）
- L2 = 领域知识（跨任务复用，长期有效）
- L3 = 原始存档（`knowledge_items`，按需追溯）

```
Agent 查询
    │
    ▼
┌──────────┐  命中  → 直接返回
│ L1 工作记忆 │  (最近7天, 当前项目相关)
└────┬─────┘
     │ 未命中
     ▼
┌──────────┐  命中  → 返回 + 提升
│ L2 领域知识 │  (长期有效, 跨任务复用)
└────┬─────┘
     │ 未命中
     ▼
┌──────────┐  命中  → 整理后返回
│ L3 原始存档 │  (knowledge_items 原始条目)
└─────────┘
```

### 判断 2：摘要式 + 原文可追溯 > 纯图谱

图谱看着高级，但结构化提取太容易丢信息——语气、否定、条件、时间范围，经常进不了三元组。

**落地含义：**
- `memory_cards` 存**结构化摘要**（不是三元组）
- 每张卡保留 `source_item_ids` 指向原始 `knowledge_items`
- 摘要字段必须包含：结论、前提条件、时效、来源
- 图谱（`wiki_compile.py`）作为**辅助索引**，不作为主存储

### 判断 3：Memory 落地靠工程设计，不是靠模型窗口拉长

Claude Code Memory、Letta、Cursor Rules，全是 Workflow 方法，没有一个是靠纯模型能力解决的。

**落地含义：**
- 用脚本 + SQL 实现分层，不依赖 LLM 实时判断
- 用定时任务（cron）做压缩和归档
- 用明确的 SQL 规则做晋升/降级，不靠 LLM 打分
- 检索优先级硬编码：L1 > L2 > L3

---

## 五、`memory_cards` 分层表设计

```sql
CREATE TABLE memory_cards (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 分层
    layer         SMALLINT NOT NULL DEFAULT 2,
    --  1 = 工作记忆（当前任务，高时效，自动过期）
    --  2 = 领域知识（跨任务复用，长期有效）
    --  3 = 原始存档（由 knowledge_items 映射，不直接写入）

    -- 内容
    title         TEXT NOT NULL,
    summary       TEXT NOT NULL,          -- 结构化摘要（结论 + 前提 + 时效）
    keywords      TEXT[] DEFAULT '{}',    -- 概念标签
    context_tags  TEXT[] DEFAULT '{}',    -- 上下文标签（项目名、技术栈等）

    -- 时效
    valid_from    TIMESTAMP DEFAULT NOW(),
    valid_until   TIMESTAMP,             -- NULL = 长期有效

    -- 关联
    source_item_ids UUID[] DEFAULT '{}',  -- 指向 knowledge_items 原始条目
    related_card_ids UUID[] DEFAULT '{}', -- 关联的其他 memory_cards

    -- 向量
    embedding     vector(1024),

    -- 元数据
    access_count  INT DEFAULT 0,          -- 被召回次数
    last_accessed TIMESTAMP,
    confidence    REAL DEFAULT 0.8,       -- 可信度
    created_at    TIMESTAMP DEFAULT NOW(),
    updated_at    TIMESTAMP DEFAULT NOW()
);

-- 按层索引
CREATE INDEX idx_memory_cards_layer ON memory_cards(layer);
-- 向量索引
CREATE INDEX idx_memory_cards_embedding ON memory_cards USING ivfflat (embedding vector_cosine_ops);
-- 关键词索引
CREATE INDEX idx_memory_cards_keywords ON memory_cards USING GIN(keywords);
```

---

## 六、优化实施路线

### Phase 1：建分层表 + 记忆整理器（阶段 4）✅ 已完成

> 完成时间：2026-05-18
> 新增脚本：`memory_migrate.py`、`memory_organize.py`、`memory_recall.py`
> 验证：eval.py test_16/17/18 全部通过

### Phase 2：工作记忆 + 时效管理（阶段 4 完善）✅ 已完成

> 完成时间：2026-05-18
> 新增脚本：`memory_save_working.py`、`memory_compress.py`
> 验证：eval.py test_19/20 全部通过

### Phase 3：图谱联动 + 时间线（阶段 5）🔸 部分完成

> 完成时间：2026-05-18（时间线部分）
> 新增脚本：`memory_timeline.py`
> 验证：时间线功能可用
> 待完成：`wiki_compile.py` 与 `memory_cards.related_card_ids` 双向关联

### Phase 4：自进化闭环（阶段 6）✅ 已完成

> 完成时间：2026-05-18
> 新增脚本：`memory_health.py`、`memory_self_tune.py`
> 验证：eval.py test_21/22/23 全部通过
> 机制：棘轮 + 爬山调优 + TSV 追踪 + 环境变量参数注入

---

### 原始实施计划（保留作为参考）

### Phase 1 原始：建分层表 + 记忆整理器（阶段 4）

**目标：** 从 `knowledge_items` 自动提取高价值条目，生成 L2 领域知识卡片。

**新增脚本：**
- `scripts/memory_organize.py` — 记忆整理器
  - 从 `knowledge_items` 中筛选高质量条目（candidate_score >= 7）
  - 用 LLM 生成结构化摘要（结论、前提、时效）
  - 提取概念标签，写入 `memory_cards` (layer=2)
  - 去重合并：相似度 > 0.95 的条目合并为一张卡

- `scripts/memory_recall.py` — 分层检索
  - 输入：query + 可选 context_tags
  - 输出：L1 → L2 → L3 逐层召回，按优先级返回
  - 命中 L1/L2 时更新 `access_count` 和 `last_accessed`

**关键规则（硬编码，不依赖 LLM）：**
```python
# L1 → L2 降级条件
DOWNGRADE_L1_TO_L2 = {
    "age_days > 7 AND access_count < 2",     # 超过7天且很少被访问
    "valid_until < NOW()",                     # 已过期
}

# L2 → L3 归档条件
ARCHIVE_L2_TO_L3 = {
    "age_days > 90 AND access_count < 1",     # 90天无人问津
}

# L3 → L2 晋升条件（从 knowledge_items 提取）
PROMOTE_L3_TO_L2 = {
    "candidate_score >= 7",                    # 质量过关
    "ai_summary IS NOT NULL",                  # 有摘要
    "NOT EXISTS similar memory_card",          # 不重复
}
```

### Phase 2：工作记忆 + 时效管理（阶段 4 完善）

**目标：** 支持 L1 工作记忆的写入、过期、降级。

**新增脚本：**
- `scripts/memory_save_working.py` — 写入 L1 工作记忆
  - Agent 在任务中产出的关键决策、中间结论写入 L1
  - 自动设置 `valid_until = NOW() + 7 days`
  - 打上当前项目/任务的 `context_tags`

- `scripts/memory_compress.py` — 定期压缩
  - cron 任务，每天执行
  - 将过期的 L1 降级为 L2（提取长期有效部分）
  - 将冷门的 L2 归档（不删除，标记 `confidence = 0`）
  - 合并相似的 L2 卡片

### Phase 3：图谱联动 + 时间线（阶段 5）

**目标：** 将 `wiki_compile.py` 的概念提取与 `memory_cards` 关联。

**改造：**
- `wiki_compile.py` 编译时，同时更新 `memory_cards.related_card_ids`
- 新增 `scripts/memory_timeline.py` — 时间线视图
  - 按 `valid_from` 排列，展示某个概念的时间演化
  - 输出格式：`[2024-03] 观点A → [2024-06] 修正为观点B → [2024-09] 观点B被验证`

### Phase 4：自进化闭环（阶段 6）

**目标：** 记忆系统自我评估和优化。

**新增脚本：**
- `scripts/memory_health.py` — 记忆健康度报告
  - L1 命中率、L2 命中率、L3 回退率
  - 冷门卡片占比、重复卡片数量
  - 摘要质量抽检（随机抽样 + LLM 评分）

- `scripts/memory_self_tune.py` — 自动调参
  - 根据命中率调整降级/归档的时间阈值
  - 根据用户反馈（点赞/踩）调整 confidence
  - 识别高频查询但低召回的场景，触发补充提取

---

## 七、检索优先级规则

```python
def recall(query: str, context_tags: list[str] = None) -> list[MemoryCard]:
    results = []

    # 1. L1 工作记忆 — 精确匹配 context_tags
    l1 = search_memory_cards(query, layer=1, context_tags=context_tags, limit=5)
    results.extend(l1)

    # 2. L2 领域知识 — 语义搜索
    if len(results) < 10:
        l2 = search_memory_cards(query, layer=2, limit=10 - len(results))
        results.extend(l2)

    # 3. L3 原始存档 — fallback
    if len(results) < 10:
        l3 = search_knowledge_items(query, limit=10 - len(results))
        # 实时整理：命中但未整理的条目触发异步提取
        trigger_async_organize(l3)
        results.extend(l3)

    # 更新访问计数
    for card in results:
        update_access(card.id)

    return results
```

---

## 八、验收标准

| 阶段 | 验收指标 |
|------|----------|
| Phase 1 完成 | `memory_cards` 表存在；`memory_organize.py` 可从现有 `knowledge_items` 提取 L2 卡片；`memory_recall.py` 返回分层结果 |
| Phase 2 完成 | Agent 可写入 L1 工作记忆；过期自动降级；`memory_compress.py` 可合并相似卡片 |
| Phase 3 完成 | 概念图谱与 `memory_cards` 双向关联；时间线可查询某概念的演化路径 |
| Phase 4 完成 | 健康度报告自动生成；命中率持续提升；冷门卡片自动归档 |

---

## 九、设计原则（来自工业实践）

1. **不动 `knowledge_items`** — 原始数据层保持不变，`memory_cards` 是新建的整理层
2. **硬编码规则优先** — 分层晋升/降级用 SQL 条件，不依赖 LLM 实时判断
3. **摘要 > 图谱** — 结构化摘要为主存储，图谱只做辅助索引
4. **定时 > 实时** — 压缩、归档、整理用 cron 定时任务，不阻塞主流程
5. **可追溯** — 每张 `memory_card` 都能追溯到原始 `knowledge_items`
6. **渐进式** — 每个 Phase 独立可用，不依赖后续 Phase

---

## 十、自进化调优机制（紫金花）

参考 darwin-skill 的进化机制，实现了**棘轮 + 爬山 + TSV 追踪**的自进化闭环。

### 核心流程

```
采集六维指标 → 找最差维度 → 提出参数调整 → 保存快照 → 应用新参数
     ↑                                                    ↓
     └──────── 对比新旧指标 ←──── 重新采集指标 ←───────────┘
                    │
              IF 综合分提升 → keep（保留）
              ELSE           → revert（回退到快照参数）
```

### 六维健康指标

| 维度 | 含义 | 方向 | 权重 |
|------|------|------|------|
| L1 命中率 | L1 卡片有 embedding 的比例 | ↑ | 20 |
| L2 命中率 | L2 卡片有 embedding 的比例 | ↑ | 25 |
| L3 回退率 | knowledge_items 未被 memory_cards 覆盖的比例 | ↓ | 20 |
| 覆盖率 | knowledge_items → memory_cards 的组织比例 | ↑ | 20 |
| 冷门率 | access_count=0 且 >30 天的卡片占比 | ↓ | 8 |
| 疑似重复率 | similarity>0.90 的卡片对占比 | ↓ | 7 |

综合分满分 100，公式：`l1*20 + l2*25 + (1-l3_fb)*20 + min(cov/50,1)*20 + (1-cold)*8 + (1-dup)*7`

### 可调参数

| 参数 | 默认值 | 调优范围 | 影响维度 | 所在脚本 |
|------|--------|----------|----------|----------|
| `MEMORY_L1_EXPIRE_DAYS` | 7 | 3~14 | L1 命中率 | memory_compress.py |
| `MEMORY_L2_ARCHIVE_DAYS` | 90 | 30~180 | 覆盖率 | memory_compress.py |
| `MEMORY_MERGE_SIMILARITY` | 0.95 | 0.85~0.99 | 疑似重复率 | memory_compress.py |
| `MEMORY_ORGANIZE_MIN_CONTENT` | 180 | 50~500 | 覆盖率 | memory_organize.py |
| `MEMORY_DEDUP_THRESHOLD` | 0.95 | 0.85~0.99 | 疑似重复率 | memory_organize.py |

### 参数注入机制

不修改源码硬编码值，而是通过 `.tune-params.env` 环境变量文件注入：

```bash
# memory_self_tune.py 自动生成 .tune-params.env
MEMORY_L1_EXPIRE_DAYS=7
MEMORY_L2_ARCHIVE_DAYS=90
MEMORY_MERGE_SIMILARITY=0.95
MEMORY_ORGANIZE_MIN_CONTENT=180
MEMORY_DEDUP_THRESHOLD=0.95
```

`memory_compress.py` 和 `memory_organize.py` 启动时自动加载该文件。

### 追踪文件

- `.tune-state.json` — 当前参数 + 历史指标 + 调优记录
- `tune-results.tsv` — 每次调优的参数变更、分数变化、keep/revert 结果

---

*本文档基于"Agent Memory 实战选型"方法论整理，用于指导 knowledge-skill 从阶段 3 向阶段 6 的渐进升级。阶段 6 已全部完成。*
