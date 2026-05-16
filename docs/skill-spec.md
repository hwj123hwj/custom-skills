# Skill 规范

## 基本结构

每个 Skill 都位于 `skills/<skill-id>/` 目录下，并且必须包含 `SKILL.md`。

可选子目录：

- `scripts/`
- `data/`
- `references/`

## Frontmatter 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 是 | kebab-case，必须与目录名一致 |
| `description` | 是 | 触发描述，是 Agent 自动识别最重要的字段 |
| `tags` | 是 | 1-3 个，必须来自白名单 |
| `displayName` | 否 | 展示名，默认取正文 H1 |
| `aliases` | 否 | 别名，用于模糊匹配 |
| `scenarios` | 否 | 触发场景列表 |
| `author` | 否 | 作者或上游作者 |
| `upstream` | 否 | 上游仓库，格式为 `owner/repo` |
| `upstreamPath` | 否 | 当 Skill 不在上游仓库根目录时使用 |
| `upstreamSha` | 否 | 上游同步基准 SHA |
| `version` | 否 | 版本号 |

## Tag 白名单

当前允许的 tag：

```text
Analysis, Audio, Automation, CLI, Content, Crawler, Education,
Forensics, Installer, Knowledge, LocalData, Marketplace, Media,
Monitoring, Planning, Product, Productivity, Recruitment,
Research, Search, Social, Summary, Utility, Video, Web, Writing,
Bilibili, WeChat, Weibo, Xiaohongshu
```

新增 tag 前，必须先更新 `web/scripts/validate-registry.ts`。

## 第三方 Skill 规则

- 上游 tag 往往是自由格式，接入时必须映射到本仓库的 tag 白名单
- 需要记录 `author`、`upstream`、`upstreamSha`
- 如果 Skill 位于上游子目录中，必须补充 `upstreamPath`
- 需要在 `web/src/i18n/skill-descriptions.ts` 中补充中文描述

### 外部 CLI 型 Skill 的轻量接入原则

对于 `twitter-cli`、`bilibili-cli`、`xiaohongshu-cli`、`wx-cli` 这类“运行时依赖外部已发布 CLI”的 Skill，本仓库优先保存：

- `SKILL.md`
- `SCHEMA.md`（如果 `SKILL.md` 有引用）
- 少量对 Agent 真正有用的补充说明文件

通常不需要把上游仓库完整 vendoring 进来，例如：

- `.github/`
- `tests/`
- `pyproject.toml`
- `uv.lock`
- 源码目录

这类 Skill 在本仓库中的主要职责是提供安装方式、认证步骤、输出契约与使用策略，而不是镜像整个上游实现。

## Python 脚本规则

- 优先使用 PEP 723 内联元数据
- 优先使用 `uv run`
- Secret 必须走环境变量或 `.env`
- 在合适的地方补充类型标注
