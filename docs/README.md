# 文档索引

本目录用于存放项目的详细规范、架构说明与设计文档。

## 核心规范

- [项目架构](./architecture.md) — 模块划分、数据流、技术栈
- [Skill 规范](./skill-spec.md) — SKILL.md frontmatter、tag 白名单、命名规则
- [Agent 规范](./agent-spec.md) — Agent 定义、类型（vertical/general）、frontmatter
- [Registry 生成与校验流程](./registry-workflow.md) — generate/validate 命令与提交流程
- [第三方 Skill 同步规范](./upstream-sync.md) — upstream 元数据、CI 自动同步机制

## Agent 基础设施

- [总览](./agent-infra/overview.md) — 方法论与核心对象
- [MVP 定义](./agent-infra/mvp.md) — 最小可行 Agent 平台
- [Knowledge Compile Layer](./agent-infra/knowledge-compile-layer.md) — 知识编译方法论
- [Knowledge to Deck MVP](./agent-infra/knowledge-to-deck-mvp.md) — 知识到展示的最小流水线
- [Knowledge to Deck Agent Spec](./agent-infra/knowledge-to-deck-agent-spec.md) — 知识到展示 Agent 规格
- [Intel Agent 重构规范](./agent-infra/intel-agent-spec.md) — Intel Agent 重构设计
- [Eval Case 规范](./agent-infra/eval-case-spec.md) — 评估用例结构定义
- [Run Artifact 规范](./agent-infra/run-artifact-spec.md) — 运行产物与晋级逻辑

## Agent Stories

- [Story 规范](./agent-stories/README.md) — Story frontmatter 与结构
- [Intel Agent Story](./agent-stories/intel-agent.md) — Intel Agent 演进记录

## Showcase

- [Showcase 索引](./showcase/README.md) — 展示原则与产出物列表
- [AutoResearch 知识卡片 Brief](./showcase/autoresearch-knowledge-cards.md)
- [Knowledge to Deck Pipeline Notes](./showcase/knowledge-to-deck-pipeline-notes.md)
- [Programmer Workflow Shift Notes](./showcase/programmer-workflow-shift-notes.md)
- [Vector Database Decision Cards](./showcase/vector-database-decision-cards.md)
- [Recipes 索引](./showcase/recipes/README.md) — Deck 配方文档
- [Reviews 索引](./showcase/reviews/README.md) — 产出物审核快照

## Wiki Reviews

- [Wiki Reviews 说明](./wiki/reviews/README.md)
- [Wiki Review 快照](./wiki/reviews/index.md)
- [Wiki 覆盖率分析](./wiki/reviews/coverage.md)

## 历史规格

- [v1 基线快照](./spec/v1-baseline/v1-current-state.md) — 初始状态快照（不再更新）
- [v2 Agent 平台演进](./spec/v2-agent-platform/AGENT_EVOLUTION.md) — Skills → Agents 演进路线
- [v2 CLI 规格](./spec/v2-agent-platform/CLI_SPEC.md) — Claude Code CLI 扩展设计
- [v2 Web 规格](./spec/v2-agent-platform/WEB_SPEC.md) — Web Agent 广场设计
- [v2 i18n 规格](./spec/v2-agent-platform/I18N_SPEC.md) — 国际化设计

## 代码审查

- [2026-05-20 项目审查](./codebase-review-2026-05-20.md) — P0/P1/P2 问题与优化路线

## 阶段性计划

- [2026-05-02 Agent 痛点分析](./plans/2026-05-02-agent-pain-points.md)
- [2026-05-02 CLI 安装方案](./plans/2026-05-02-claude-agent-install.md)
- [2026-05-02 痛点解决方案](./plans/2026-05-02-pain-points-solution.md)
- [2026-05-02 Web Agent 广场方案](./plans/2026-05-02-web-agent-plaza.md)
- [2026-05-18 Knowledge Skill Memory 审查](./plans/2026-05-18-knowledge-skill-memory-review.md)
- [2026-05-20 项目优化优先级路线](./plans/2026-05-20-codebase-priorities.md)
