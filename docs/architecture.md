# 项目架构

## 总览

`custom-skills` 是一个以 `SKILL.md` 为唯一事实来源的技能注册表。它一方面通过 Web 技能广场服务人类用户，另一方面通过 CLI 为 AI Agent 提供发现与安装能力，同时承载个人博客系统。

## 主要模块

- `skills/`：技能源目录，每个技能都必须包含 `SKILL.md`
- `registry/`：自动生成的机器可读索引
- `web/`：基于 React + Vite 的技能广场与博客系统
- `cli/`：基于 TypeScript 的命令行工具，用于搜索、查看与安装

## 核心数据流

```text
skills/*/SKILL.md
  → web/scripts/sync-skills.ts
  → registry/skills.json + web/src/data/skills-data.json + README.md + sitemap
  → CLI（远程拉取）/ Web（静态导入）
```

## 目录说明

- `skills/`：存放技能定义
- `docs/`：存放详细规范与设计文档
- `prompts/`：存放提示词模板

## Web 技术栈

- React 19
- TypeScript 5.9
- Vite 7
- Tailwind CSS
- React Router
- i18next

## Web 分类筛选

Skills tab 通过 `web/src/lib/skill-categories.ts` 定义的 6 个高层分组（编程开发、内容创作、平台工具、效率工具、知识搜索、数据处理）进行分类筛选，每个分组映射到一组底层 tag。Decks tab 有独立的分类体系。两者共享 `CategoryChip` 组件。

## CLI 技术栈

- TypeScript
- Commander
- 远程 registry 拉取 + 本地缓存降级
