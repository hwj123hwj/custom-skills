# Agent Stories

本目录用于存放 `agent story` 文档。

`agent story` 不是 Agent 定义本身，而是记录这个 Agent 为什么被创建、当前效果如何、经历了哪些演进，以及接下来还要如何继续优化。

## 文件位置

每个 Agent 对应一份 Story 文档，统一放在：

`docs/agent-stories/<agent-id>.md`

例如：

- `docs/agent-stories/intel-agent.md`

## Frontmatter 规范

每份 Story 文档顶部使用 `frontmatter`，第一版固定使用以下字段：

| 字段 | 必填 | 说明 |
|------|------|------|
| `title` | 是 | Story 展示标题 |
| `agent` | 是 | 对应的 Agent id，需和 `agents/*.md` 对齐 |
| `status` | 是 | 当前状态，见下方枚举 |
| `stage` | 是 | 当前阶段，见下方枚举 |
| `owner` | 建议 | 当前主要维护者 |
| `lastUpdated` | 是 | 最后更新时间，使用 `YYYY-MM-DD` |
| `summary` | 是 | 用于列表页展示的简短摘要 |
| `tags` | 建议 | 用于筛选、聚类和展示的标签 |

推荐示例：

```yaml
---
title: Intel Agent
agent: intel-agent
status: active
stage: iterating
owner: weijian
lastUpdated: 2026-05-16
summary: 从泛媒体分析收敛到关注流优先的信息整理 Agent。
tags:
  - analysis
  - knowledge
  - following-first
  - eval-driven
---
```

## 正文 Section 规范

正文第一版固定使用以下顺序：

```md
## 为什么做
## 当前效果
## 进化时间线
## 反馈与待优化
## 下一步
```

说明：

- `为什么做`：记录真实问题和创建动机
- `当前效果`：记录现在已经有效的地方，以及仍不稳定的地方
- `进化时间线`：按时间记录关键调整与判断变化
- `反馈与待优化`：记录真实测试反馈、已知问题和后续风险
- `下一步`：记录接下来要做什么，而不是泛泛愿景

## 状态与阶段枚举

### `status`

- `active`：当前仍在使用、维护或持续关注
- `paused`：暂时搁置，但未彻底废弃
- `archived`：转入历史记录，不再继续推进

### `stage`

- `idea`：问题和方向已明确，但尚未落地
- `building`：正在接能力、写 Agent、补流程
- `testing`：已可运行，当前重点是验证效果
- `iterating`：已有真实反馈，正持续调优
- `stable`：形态相对稳定，改动频率较低

## 推荐 Story Tags

第一版建议优先使用以下标签：

- `analysis`
- `knowledge`
- `productivity`
- `research`
- `workflow`
- `automation`
- `following-first`
- `eval-driven`
- `community-feedback`

可以新增标签，但应优先复用已有标签，避免 Story 体系快速分裂。

## 编写原则

- 写真实问题，不写空泛愿景
- 写当前效果，也写已知不足，不只写成功
- 写能够支持后续优化的信息，不写流水账
- 避免把 Agent 运行规则重复抄到 Story 里，流程定义应继续留在 `agents/*.md`
