---
type: entity
date: 2026-06-14
tags: [agent, spec, frontmatter]
---

# Agent Spec

> Agent 定义规范，来自 `docs/agent-spec.md`。

## Agent 与 Skill 的关系

- Skill = 原子能力
- Agent = 角色 + 行为规则 + 能力组合

Skill 可被多个 Agent 复用，Agent 可依赖多个 Skill。

## Agent 类型

### 通用型 Agent
- frontmatter 中不写 `skills`
- 正文通过 `skill: xxx` 提示可选增强能力

### 垂直型 Agent
- frontmatter 显式声明 `skills: [...]`
- 正文保留 `skill: xxx` 作为运行时指引

## Frontmatter 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 是 | kebab-case |
| `description` | 是 | 何时主动使用 |
| `tools` | 是 | 允许的工具列表 |
| `model` | 是 | opus/sonnet/haiku |
| `skills` | 垂直型必填 | 依赖的 Skill id |
| `tags` | 建议 | 展示与检索 |

## 推荐正文结构

```
# Identity → Goal → Scope → Inputs → Process → Decision Rules → Output Contract → Eval Contract → Collaboration Notes
```

## Agent Story 的关系

- `agents/*.md` → 执行用 Agent 本体（角色、流程、能力依赖）
- `docs/agent-stories/<agent-id>.md` → 复盘用 Story（创建原因、效果、调整记录）

## 当前 Agent 列表

| Agent | 类型 | 模型 | 关联 Skills |
|-------|------|------|-------------|
| architect | general | opus | — |
| coding-agent | vertical | sonnet | diagnose, tdd, review, prototype, improve-codebase-architecture, handoff, grill-me, to-prd, to-issues |
| intel-agent | vertical | sonnet | twitter-cli, bilibili-cli, xiaohongshu-cli, tavily |
| knowledge-to-deck-agent | vertical | sonnet | knowledge-skill, guizang-ppt-skill |
| tdd-guide | general | sonnet | — |
| vid-publisher-agent | vertical | sonnet | video-analyze, content-adapt, douyin-upload |

相关：[[architecture]], [[skill-spec]], [[agent-infrastructure]], [[registry-system]]
