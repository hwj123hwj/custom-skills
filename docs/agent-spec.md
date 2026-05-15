# Agent 规范

## Agent 与 Skill 的关系

- Skill = 原子能力
- Agent = 角色 + 行为规则 + 能力组合

一个 Skill 可以被多个 Agent 复用，一个 Agent 也可以依赖多个 Skill。

## Agent 类型

### 通用型 Agent

适合不依赖固定 Skill 的广义角色。

- frontmatter 中不写 `skills`
- 可以在正文中通过 `skill: xxx` 提示可选增强能力

### 垂直型 Agent

适合离开特定 Skill 就无法完整工作的领域型角色。

- frontmatter 中显式声明 `skills: [...]`
- 正文里继续保留 `skill: xxx` 作为运行时指引

## Frontmatter 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 是 | kebab-case，通常应与文件名一致 |
| `description` | 是 | 描述“什么时候应该主动使用这个 Agent” |
| `tools` | 是 | 允许使用的工具列表 |
| `model` | 是 | `opus`、`sonnet` 或 `haiku` |
| `skills` | 垂直型必填 | 依赖的 Skill id 列表 |
| `tags` | 建议 | 用于展示与检索 |

## 推荐正文结构

```md
# Agent 名称

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

这套结构尤其适合会持续验证、持续优化的编排型 Agent。

## 当前演进方向

仓库正在向“结构化 Agent”演进。未来一个 Agent 不只是提示词，还应能清晰定义：

- 角色
- 流程
- 输出接口
- 评估接口

这样才更容易比较、验证和持续优化。
