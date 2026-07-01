---
type: entity
date: 2026-06-14
tags: [skill, spec, frontmatter]
---

# Skill Spec

> SKILL.md 规范，来自 `docs/skill-spec.md`。

## 基本结构

每个 Skill 位于 `skills/<skill-id>/` 目录下，必须包含 `SKILL.md`。

可选子目录：`scripts/`、`data/`、`references/`

## Frontmatter 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 是 | kebab-case，必须与目录名一致 |
| `description` | 是 | 触发描述，Agent 自动识别最重要的字段 |
| `tags` | 是 | 1-5 个，必须来自白名单（含 `Matt Pocock` 来源标签）|
| `displayName` | 否 | 展示名，默认取正文 H1 |
| `aliases` | 否 | 别名，用于模糊匹配 |
| `scenarios` | 否 | 触发场景列表 |
| `author` | 否 | 作者或上游作者 |
| `upstream` | 否 | 上游仓库，格式 `owner/repo` |
| `upstreamPath` | 否 | Skill 不在上游根目录时使用 |
| `upstreamSha` | 否 | 上游同步基准 SHA |
| `version` | 否 | 版本号 |
| `disable-model-invocation` | 否 | 设为 true 时技能仅限手动 `/invoke`，不占用上下文 |
| `argument-hint` | 否 | 用户 `/invoke` 时可传入的参数提示 |

## Python 脚本规则

- 优先使用 PEP 723 内联元数据
- 优先使用 `uv run`
- Secret 必须走环境变量或 `.env`

## 外部 CLI Skill 轻量接入原则

对于 `twitter-cli`、`bilibili-cli`、`xiaohongshu-cli` 等外部 CLI 型 Skill，只保存：
- `SKILL.md`
- `SCHEMA.md`（如有引用）
- 少量补充说明文件

不做完整 vendoring（不包含 `.github/`、`tests/`、`pyproject.toml` 等）。

相关：[[architecture]], [[registry-system]], [[tag-system]], [[upstream-sync]], [[mattpocock-collection]]
