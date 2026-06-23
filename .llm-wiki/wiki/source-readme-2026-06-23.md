---
type: source
source_path: "README.md"
date: 2026-06-23
tags: [readme, documentation, contributing, categories]
---

# Source: README.md (2026-06-23 Rewrite)

## Key Takeaways

- README 经历全面重写，从 ~60 行扩展到 230+ 行，结构更清晰
- 项目定位：以 `SKILL.md` 为唯一事实来源的 AI Agent 技能注册表
- 当前规模：48+ 技能，覆盖编程开发、内容创作、平台工具等多个领域
- 支持两大用户群体：人类用户（Web 技能广场）和 AI Agent（CLI 安装工具）
- 技能分类从 5 组扩展为 **6 组**：编程开发、内容创作、平台工具、效率工具、知识搜索、数据处理
- 新增完整的**贡献指南**章节，明确贡献流程和注意事项
- 新增**上游同步**文档，说明第三方技能的 CI 自动同步机制

## Important Entities

| 实体 | 说明 |
|------|------|
| Web 技能广场 | React 19 + Vite 构建，支持中英文双语，GitHub Pages 部署 |
| CLI 工具 | `npx custom-skills` 命令行，支持 list/search/info/install |
| Claude Code | 主要安装目标，支持项目级和全局安装 |
| OpenClaw | 兼容的 AI Agent 平台 |
| mattpocock/skills | 上游贡献者，提供 grill-me, handoff, tdd 等工程类技能 |
| nextlevelbuilder/ui-ux-pro-max-skill | 上游贡献者，提供 UI/UX 设计技能 |

## Notable Claims

- 技能安装支持 `--agent` 模式，可一次安装 Agent 及其所有依赖技能
- CI 每日 UTC 02:00 自动检查上游更新
- 新增 tag 必须先在 `validate-registry.ts` 的 `ALLOWED_TAGS` 中注册
- 新增技能必须在 `skill-descriptions.ts` 中补充中文描述（CI 校验覆盖率）

## Changes vs. Existing Wiki

### ⚠️ 分类体系变更（5 → 6 组）

README 显示技能分类从原来的 5 组变为 6 组：

| 旧分组 | 新分组 |
|--------|--------|
| coding | 编程开发 |
| content | 内容创作 |
| platform | 平台工具 |
| knowledge | 知识搜索 |
| product | **效率工具** + **数据处理**（拆分为两组） |

需更新：[[tag-system]], [[web-app]]

### ⚠️ 上游同步冲突处理改进

README 未直接提及，但本次会话中已修复同步脚本的冲突处理逻辑。需更新：[[upstream-sync]], [[ci-cd-workflows]]

## Related Pages

- [[architecture]]
- [[skill-spec]]
- [[tag-system]]
- [[web-app]]
- [[upstream-sync]]
- [[ci-cd-workflows]]
- [[cli-tool]]
