---
type: guide
date: 2026-06-23
tags: [upstream, sync, third-party, three-way-merge, conflict-handling]
---

# Upstream Sync

> 第三方 Skill 同步机制，来自 `docs/upstream-sync.md` + 冲突处理改进。

## 目的

确保第三方 Skill 来源可追踪、可同步。通过 SKILL.md 中的 `upstream` / `upstreamPath` / `upstreamSha` 元数据实现。

## CI 自动同步

`.github/workflows/sync-upstream-skills.yml` 每日 UTC 02:00 运行。

### 同步流程

1. 扫描所有含 `upstream` + `upstreamSha` 的 SKILL.md
2. 对比上游 HEAD SHA，跳过无变化的技能
3. 对有变化的技能做**三路合并**（base=upstreamSha, ours=本地, theirs=最新上游）
4. 二进制文件直接覆盖，文本文件用 `git merge-file`
5. 无冲突时更新 `upstreamSha`
6. `generate:registry` → 创建/更新 PR

### 冲突处理策略（2026-06-23 改进）

**原问题**：
- 冲突标记（`<<<<<<<`, `=======`, `>>>>>>>`）被写入文件，导致 YAML 解析失败
- 冲突后仍更新 `upstreamSha`，导致下次同步使用错误的 base
- 冲突未在 PR 中正确报告

**改进后的行为**：
1. **检测已有冲突标记**：如果本地文件已含冲突标记，直接跳过并报告
2. **冲突时不写入文件**：保持本地文件原样，等用户手动解决
3. **冲突时跳过 upstreamSha 更新**：防止下次同步使用错误的 base
4. **独立报告冲突**：即使没有实际文件变更，也会创建 PR 报告冲突
5. **改进 PR 描述**：包含手动解决冲突的步骤说明

## 必备元数据

| 字段 | 说明 |
|------|------|
| `author` | 上游作者 |
| `upstream` | 上游仓库 `owner/repo` |
| `upstreamSha` | 上次同步的 HEAD SHA |
| `upstreamPath` | Skill 不在上游根目录时必填 |

## 引入新第三方技能

1. `git ls-remote https://github.com/owner/repo.git HEAD` 获取 SHA
2. 创建 `skills/<skill-id>/`
3. 复制/适配上游 SKILL.md
4. 添加 frontmatter 元数据（author, upstream, upstreamSha, upstreamPath）
5. 映射 tag 到白名单
6. 补充中文描述（`web/src/i18n/skill-descriptions.ts`）
7. `generate:registry` + `validate:registry`
8. 提交 PR

## 手动解决冲突步骤

当 PR 标记为"⚠️ 含冲突"时：

1. 本地 checkout PR 分支：`git checkout chore/sync-upstream-skills`
2. 查看冲突文件中本地修改 vs 上游最新版本的差异
3. 手动合并上游变更，保留本地自定义修改（如 `disable-model-invocation: true`）
4. 更新 SKILL.md 中的 `upstreamSha` 为最新版本
5. 运行 `cd web && npm run generate:registry`
6. 提交并合并 PR

## 当前上游技能来源

| 上游仓库 | 技能 |
|----------|------|
| mattpocock/skills | grill-me, handoff, improve-codebase-architecture, prototype, tdd, to-issues, to-prd, review |
| nextlevelbuilder/ui-ux-pro-max-skill | ui-ux-pro-max |

相关：[[ci-cd-workflows]], [[skill-spec]], [[tag-system]], [[source-readme-2026-06-23]]
