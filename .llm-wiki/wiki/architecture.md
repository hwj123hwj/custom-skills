---
type: entity
date: 2026-06-14
tags: [architecture, dataflow, modules]
---

# Architecture

> 项目架构概述，当前规模：73 个技能，6 个 Agent。来自 `docs/architecture.md`。

## 总览

`custom-skills` 是一个以 `SKILL.md` 为唯一事实来源的 AI 能力注册表，通过 Web 技能广场服务人类用户，通过 CLI 为 AI Agent 提供发现与安装能力。

## 主要模块

| 模块 | 说明 |
|------|------|
| `skills/` | 73 个技能源目录，含全量 [[mattpocock-collection\|Matt Pocock 技能合集]]（34个）|
| `agents/` | 可复用的 Agent 定义，组合角色、规则与技能 |
| `registry/` | 自动生成的机器可读索引 |
| `web/` | React + Vite 技能与 Agent 广场 |
| `cli/` | TypeScript 命令行工具（搜索/查看/安装） |
| `docs/` | 详细规范与设计文档 |
| `docs/agent-infra/` | 下一代 Agent 基础设施设计 |

## 核心数据流

```
skills/*/SKILL.md
  → web/scripts/sync-skills.ts
  → registry/skills.json + web/src/data/skills-data.json + README.md + sitemap
  → CLI（远程拉取）/ Web（静态导入）
```

## Web 技术栈

React 19 + TypeScript 5.9 + Vite 7 + Tailwind CSS + React Router + i18next

Skills tab 通过 `web/src/lib/skill-categories.ts` 的 **6 个高层分组**（编程开发/内容创作/平台工具/效率工具/知识搜索/数据处理）分类筛选。此外，[[mattpocock-collection\|Matt Pocock 合集]]通过 `Matt Pocock` 标签可实现独立筛选。

## CLI 技术栈

TypeScript + Commander，远程 registry 拉取 + 本地缓存降级。

## 演进方向

正在从"技能注册表"演进为"Agent 基础设施"：

- `skills` → 可复用能力
- `agents` → 结构化编排
- `eval cases` → 验证场景
- `run artifacts` → 比较与优化依据

## Easy Code 集成

custom-skills 通过 [[skill-hub-tool]] 与 Easy Code 集成：

```
Easy Code agent → skill_hub(action="search/install")
  → jsdelivr CDN → registry/skills.json / skills/{id}/SKILL.md
  → ~/.easycode-user/skills/{id}/SKILL.md
  → SkillLoader 发现 → use_skill 加载
```

JIT 模式：启动时只消耗 ~150 tokens（一条 tool description），按需搜索安装。

相关：[[skill-spec]], [[agent-spec]], [[registry-system]], [[agent-infrastructure]], [[cli-tool]], [[web-app]], [[skill-hub-tool]], [[mattpocock-collection]]
