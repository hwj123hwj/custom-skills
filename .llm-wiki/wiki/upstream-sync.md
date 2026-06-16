---
type: guide
date: 2026-06-14
tags: [upstream, sync, third-party, three-way-merge]
---

# Upstream Sync

> 第三方 Skill 同步机制，来自 `docs/upstream-sync.md`。

## 目的

确保第三方 Skill 来源可追踪、可同步。通过 SKILL.md 中的 `upstream` / `upstreamPath` / `upstreamSha` 元数据实现。

## CI 自动同步

`.github/workflows/sync-upstream-skills.yml` 每日 UTC 02:00 运行。

### 同步流程

1. 扫描所有含 `upstream` + `upstreamSha` 的 SKILL.md
2. 对比上游 HEAD SHA
3. 对有变化的技能做**三路合并**（base=upstreamSha, ours=本地, theirs=最新上游）
4. 二进制文件直接覆盖，文本文件用 `git merge-file`
5. 更新 `upstreamSha`
6. `generate:registry` → 创建/更新 PR

## 必备元数据

| 字段 | 说明 |
|------|------|
| `author` | 上游作者 |
| `upstream` | 上游仓库 `owner/repo` |
| `upstreamSha` | 上次同步的 HEAD SHA |
| `upstreamPath` | Skill 不在上游根目录时必填 |

## 引入流程

1. `git ls-remote https://github.com/owner/repo.git HEAD` 获取 SHA
2. 创建 `skills/<skill-id>/`
3. 复制/适配上游 SKILL.md
4. 映射 tag 到白名单
5. 补充中文描述
6. `generate:registry` + `validate:registry`

相关：[[ci-cd-workflows]], [[skill-spec]], [[tag-system]]
