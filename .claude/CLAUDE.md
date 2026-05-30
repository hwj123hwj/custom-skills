# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Custom Skills Hub — 一个以 `skills/*/SKILL.md` 为数据源的 AI Agent 技能注册表，同时服务人类用户（Web 技能广场）和 AI Agent（CLI 安装工具）。

## Commands

```bash
# Web 开发
cd web && npm run dev              # 启动 Vite 开发服务器
cd web && npm run build            # tsc + vite build（会自动先 generate:registry）
cd web && npm run lint             # ESLint 检查
cd web && npm run validate:registry  # 验证 registry 一致性

# 修改 SKILL.md 后必须运行（CI 强制）
cd web && npm run generate:registry  # 重新生成 skills.json + README 技能表 + SEO

# CLI 开发
cd cli && npm run dev -- <command>   # 用 ts-node 运行 CLI（如 -- search bilibili）
cd cli && npm run build              # TypeScript 编译
```

## Architecture

**数据流（核心）：**
```
skills/*/SKILL.md (唯一数据源)
  → web/scripts/sync-skills.ts (解析 frontmatter)
  → registry/skills.json + web/src/data/skills-data.json + README.md (自动生成)
  → CLI (远程拉取) / Web (静态导入)
```

**四大模块：**
- `skills/` — 技能目录，每个必须有 `SKILL.md`（YAML frontmatter + 使用说明），含自研技能和第三方同步技能
- `agents/` — Agent 定义（`.md`），分为通用型（弱关联 Skill）和垂直型（强关联，frontmatter 声明 `skills`）
- `web/` — React 19 + Vite + Tailwind 技能广场，支持 i18n（zh/en）和分类筛选
- `cli/` — TypeScript + Commander CLI，`npx custom-skills install/search/list/info`

**Web 技术栈：** React 19, TypeScript 5.9, Vite 7, Tailwind CSS, React Router, i18next, Lucide React

## Critical Rules

- **永远不要手动编辑** `registry/skills.json` 或 `web/src/data/skills-data.json`，它们由 `generate:registry` 自动生成
- 修改任何 `SKILL.md` 后，提交前**必须**运行 `cd web && npm run generate:registry`，否则 CI 失败
- 新增 tag 必须先在 `web/scripts/validate-registry.ts` 的 `ALLOWED_TAGS` 中注册
- 技能 `name` 字段必须 kebab-case 且与目录名一致
- Python 脚本使用 PEP 723 内联元数据，用 `uv run` 执行
- 新增技能后，**必须**在 `web/src/i18n/skill-descriptions.ts` 中补充中文描述（CI 会校验覆盖率）

## Upstream Sync

带有 `upstream` + `upstreamSha` frontmatter 的技能由 CI 自动同步（每日 UTC 02:00）。
CI 会对比上游仓库 HEAD SHA，有变化则做三路合并并自动提 PR 到 `chore/sync-upstream-skills` 分支。
新技能若来源于第三方仓库，务必填写 `author`、`upstream`、`upstreamPath`、`upstreamSha`。
详见 `docs/upstream-sync.md`。

## Web 分类筛选

技能广场的 Skills tab 按 `web/src/lib/skill-categories.ts` 中定义的 6 个高层分组进行分类筛选（编程开发、内容创作、平台工具、效率工具、知识搜索、数据处理）。
新增 tag 后如需影响分类归属，需同步更新该文件。

## SKILL.md Frontmatter

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | kebab-case，必须匹配目录名 |
| `description` | Yes | 触发描述，对 Agent 自动识别最关键 |
| `tags` | Yes | 1-3 个，从 `ALLOWED_TAGS` 白名单选取 |
| `displayName` | No | 展示名，默认取 H1 标题 |
| `aliases` | No | 中文别名列表 |
| `scenarios` | No | 触发场景列表 |
| `author` | No | 第三方贡献者 GitHub ID |
| `version` | No | 版本号，第三方 skill 建议填写 |

详细规范见 `docs/skill-spec.md`。
