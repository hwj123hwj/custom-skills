---
type: concept
date: 2026-07-01
tags: [matt-pocock, skills, collection, upstream]
---

# Matt Pocock Skill Collection

> 完整收录的 [mattpocock/skills](https://github.com/mattpocock/skills) 技能合集，共 34 个技能，通过 `Matt Pocock` 标签统一筛选。

## 概述

Matt Pocock 是 TypeScript 社区知名教育者和开源贡献者，他的技能仓库围绕**工程流程**和**产品思维**设计了一套完整的 AI Agent 工作流体系。

本合集于 2026-07-01 完整导入 custom-skills，所有技能通过 `Matt Pocock` 标签可在 [[web-app]] 一键筛选。

## 技能分类

### 工程流程（10 个）
围绕代码从想法到交付的完整流程。

| 技能 | 角色 |
|------|------|
| [[ask-matt]] | 路由导航：快速定位该用哪个技能 |
| [[triage]] | Issue 分类：将原始 Issue/PR 按状态机流转 |
| [[grill-with-docs]] | 需求访谈（带 ADR 和 CONTEXT.md 输出）|
| [[to-prd]] | 对话→PRD 文档 |
| [[to-issues]] | PRD→独立可抓取的 Issue |
| [[implement]] | Issue→代码（内部驱动 [[tdd]]）|
| [[code-review]] | 双轴评审（Standards + Spec）|
| [[diagnosing-bugs]] | Bug 诊断循环 |
| [[resolving-merge-conflicts]] | 合并冲突解决 |
| [[setup-matt-pocock-skills]] | 首次初始化：Issue Tracker + Labels |

**主流程**：`grill-with-docs → to-prd → to-issues → implement → code-review`

### 代码设计（5 个）
围绕模块设计、领域建模和架构优化。

| 技能 | 角色 |
|------|------|
| [[codebase-design]] | 深层模块设计词汇（Interface/Seam/Depth/Adapter）|
| [[domain-modeling]] | 领域建模：维护 CONTEXT.md + ADR |
| [[improve-codebase-architecture]] | 发现深化机会 |
| [[prototype]] | 一次性原型验证设计问题 |
| [[tdd]] | 红绿重构循环 |

### 产品思维（7 个）
围绕需求梳理和上下文管理。

| 技能 | 角色 |
|------|------|
| [[grill-me]] | 无代码库的需求访谈 |
| [[grilling]] | 需求拷问原语（底层基座）|
| [[handoff]] | 跨会话上下文压缩和转移 |
| [[diagnose]] | 诊断循环（旧名，上游已更名为 diagnosing-bugs）|
| [[review]] | 代码评审（旧版，上游已更名为 code-review）|
| [[decision-mapping]] | 模糊想法→决策票据序列 |
| [[loop-me]] | 工作流设计拷问 |

### 工具与写作（12 个）

| 技能 | 角色 |
|------|------|
| [[teach]] | 多会话教学工坊 |
| [[wizard]] | 交互式 Bash 向导生成器 |
| [[migrate-to-shoehorn]] | 测试断言迁移（`as` → `fromPartial`）|
| [[scaffold-exercises]] | 练习目录脚手架 |
| [[setup-pre-commit]] | Husky + lint-staged 配置 |
| [[edit-article]] | 文章编辑与润色 |
| [[obsidian-vault]] | Obsidian 笔记管理 |
| [[writing-great-skills]] | Skill 编写权威参考 |
| [[writing-beats]] | 节拍式写作（Exploit）|
| [[writing-fragments]] | 写作碎片采集（Explore）|
| [[writing-shape]] | 文章塑形（Exploit）|
| [[git-guardrails-claude-code]] | Claude Code 危险命令防护 |

## 上游同步

所有 34 个技能均标记了 `upstream: mattpocock/skills` + `upstreamSha`，CI 每日 UTC 02:00 自动检查更新。

同步流程：[[upstream-sync]]

## 导入技术细节

### Frontmatter 扩展

所有 Matt Pocock 技能的 SKILL.md 在原始 frontmatter 基础上扩展了：
- `author: mattpocock`
- `upstream: mattpocock/skills`
- `upstreamPath: skills/<category>/<name>`
- `upstreamSha: <current-commit>`
- `lastUpdated: <import-date>`
- `tags: [..., Matt Pocock]`

### 上游路径映射

Matt Pocock 仓库按类别组织（`engineering/`、`productivity/` 等），而 custom-skills 为扁平布局（`skills/<name>/`）。`upstreamPath` 记录了上游真实路径，供同步脚本使用。

### 配套文件

部分技能带有额外参考文件，已一并导入：
- `codebase-design`：DEEPENING.md, DESIGN-IT-TWICE.md
- `domain-modeling`：ADR-FORMAT.md, CONTEXT-FORMAT.md
- `setup-matt-pocock-skills`：5 个配置模板（issue-tracker-*.md, triage-labels.md, domain.md）
- `teach`：4 个格式模板（MISSION/GLOSSARY/LEARNING-RECORD/RESOURCES）
- `triage`：AGENT-BRIEF.md, OUT-OF-SCOPE.md
- `wizard`：template.sh
- `writing-great-skills`：GLOSSARY.md

## 技能演进

以下为 Matt Pocock 上游已发生的重命名/移动，已同步到 custom-skills：

| 旧名（custom-skills）| 新名（上游当前）| 操作 |
|------|------|------|
| `diagnose` (upstream: engineering/diagnose) | `diagnosing-bugs` (upstream: engineering/diagnosing-bugs) | 更新 upstreamPath |
| `review` (upstream: in-progress/review) | `code-review` (upstream: engineering/code-review) | 更新 upstreamPath；新 `code-review` 技能已独立导入 |

相关：[[source-mattpocock-collection]], [[skill-spec]], [[tag-system]], [[upstream-sync]], [[web-app]]
