---
type: entity
date: 2026-06-14
tags: [ci, cd, github-actions, workflow]
---

# CI/CD Workflows

> 两个 GitHub Actions workflow。

## Registry Check

**触发**：push 到 `main`/`codex/**` 分支 或 pull_request

**步骤**：
1. checkout（`fetch-depth: 0` 确保完整 git 历史）
2. Setup Node 20 + 缓存
3. `npm ci`（web/）
4. `npm run generate:registry`（重新生成）
5. `npm run validate:registry`（校验）
6. **确保生成文件已 commit** — 检测 `git diff --exit-code` 在 README、registry、web/src/data、sitemap 等文件上
7. Build web
8. Build CLI

**常见失败原因**：改了 `SKILL.md` 或 agent 文件后没有重新 `generate:registry` 并 commit

## Sync Upstream Skills

**触发**：每天 UTC 02:00（北京 10:00）+ 手动触发

**步骤**：
1. 扫描所有含 `upstream` + `upstreamSha` 的 SKILL.md
2. 对比上游 HEAD SHA，跳过无变化
3. 对有变化的技能做三路合并（`git merge-file`，以 `upstreamSha` 为 base）
4. 二进制文件直接覆盖
5. 更新 `upstreamSha` 到新的 HEAD
6. 重新 `generate:registry`
7. 创建/更新 PR 到 `chore/sync-upstream-skills` 分支

**合并冲突**会写入标准 Git 冲突标记，需手动解决。

相关：[[registry-system]], [[upstream-sync]], [[release-process]]
