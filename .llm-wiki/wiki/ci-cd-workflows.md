---
type: entity
date: 2026-06-23
tags: [ci, cd, github-actions, workflow, conflict-handling]
---

# CI/CD Workflows

> GitHub Actions workflow 定义与行为。

## Registry Check

**触发**：push 到 `main`/`codex/**` 分支 或 pull_request

**文件**：`.github/workflows/registry-check.yml`

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

**文件**：`.github/workflows/sync-upstream-skills.yml`

**步骤**：
1. 扫描所有含 `upstream` + `upstreamSha` 的 SKILL.md
2. 对比上游 HEAD SHA，跳过无变化
3. 对有变化的技能做三路合并（`git merge-file`，以 `upstreamSha` 为 base）
4. 二进制文件直接覆盖
5. 无冲突时更新 `upstreamSha` 到新的 HEAD
6. 重新 `generate:registry`
7. 创建/更新 PR 到 `chore/sync-upstream-skills` 分支

### 冲突处理改进（2026-06-23）

**原问题**：
- 冲突标记被写入文件 → YAML 解析失败 → Registry Check 失败
- 冲突后仍更新 `upstreamSha` → 下次同步使用错误的 base → 级联问题
- 冲突未在 PR 中正确报告 → 用户不知情

**改进后**：
1. 检测已有冲突标记 → 跳过并报告
2. 冲突时不写入文件 → 保持本地原样
3. 冲突时跳过 `upstreamSha` 更新 → 防止级联问题
4. 独立报告冲突 → 即使无变更也创建 PR
5. PR 描述包含手动解决步骤

**关键代码变更**（`sync-upstream-skills.yml`）：
- 添加冲突标记检测：`grep -q '^<<<<<<< ' "$LOCAL_FILE"`
- 冲突时不执行 `cp "$MERGE_TMP" "$LOCAL_FILE"`
- `upstreamSha` 更新条件从 `always` 改为 `only when no conflicts`
- 冲突报告逻辑移出 `SKILL_CHANGED > 0` 条件

## 已知问题

- Node.js 20 deprecated 警告：Actions 使用 Node.js 20 但被强制运行在 Node.js 24 上（不影响功能）

相关：[[registry-system]], [[upstream-sync]], [[release-process]], [[source-readme-2026-06-23]]
