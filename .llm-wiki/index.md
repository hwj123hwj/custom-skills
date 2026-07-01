# .llm-wiki Index

> 项目知识库，维护架构、流程和关键决策的沉淀文档。

## Source Ingests

- [[source-project-overview]] — 2026-06-14 全仓库摄取
- [[source-easycode-skill-integration]] — 2026-06-16 Easy Code 集成方案摄取
- [[source-readme-2026-06-23]] — 2026-06-23 README 重写摄取（6 组分类、贡献指南、冲突处理改进）
- [[source-custom-skills-overview]] — 2026-06-25 全仓概览摄取（48 技能、CI/CD 修复、提交历史恢复）

## Pages

### 架构与规范

- [[architecture]] — 项目架构和数据流（含 Easy Code 集成、6 组分类）
- [[skill-spec]] — SKILL.md 规范与 frontmatter 字段
- [[agent-spec]] — Agent 定义规范与 6 个 Agent 列表
- [[tag-system]] — Tag 白名单与 6 组分类体系
- [[registry-system]] — Registry 生成与校验流程

### 集成

- [[skill-hub-tool]] — Easy Code 内置 skill_hub 工具（JIT 搜索/安装）

### 组件

- [[cli-tool]] — CLI 工具（安装、命令、数据获取策略）
- [[web-app]] — Web 技能广场（React 19 + Vite 7，6 组分类）

### 流程与 CI/CD

- [[release-process]] — 8 步发版流程与版本号约定
- [[ci-cd-workflows]] — Registry Check + Sync Upstream Skills（含冲突处理改进）
- [[upstream-sync]] — 第三方 Skill 同步机制（含冲突处理改进）

### 演进方向

- [[agent-infrastructure]] — Agent 基础设施总览与 MVP
