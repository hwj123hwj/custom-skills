# Media Agent 重构规范

## 目标

把 `media-agent` 从“泛媒体分析角色”升级成“面向日常信息摄取、去噪、洞察提炼与知识候选沉淀”的结构化编排 Agent。

## 推荐 Frontmatter

- `name`
- `description`
- `tools`
- `model`
- `skills`
- `tags`

## 推荐正文结构

```md
## Identity
## Goal
## Scope
## Inputs
## Process
## Decision Rules
## Output Contract
## Eval Contract
## Collaboration Notes
```

## 关键流程

```text
Collect
  → Filter
  → Cluster
  → Distill
  → Promote
  → Render
```

## 关键输出接口

### Daily Brief

- top themes
- key insights
- why it matters
- signals and sources
- suggested follow-ups

### Knowledge Candidates

- title
- distilled takeaway
- why save
- audience
- suggested tags
- shelf life

## 评估维度

- coverage
- noise
- compression
- retention value
