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

## CI/CD 修复记录（2026-06-25）

### frontend-design 中文描述缺失

**问题**：新增 `frontend-design` 技能后，`web/src/i18n/skill-descriptions.ts` 中缺少对应的中文描述条目，导致 `validate:registry` 步骤失败。

**错误信息**：
```
i18n 覆盖检查失败，缺少以下技能的中文描述:
  - frontend-design
```

**修复**：在 `skillDescriptionsZh` 对象中添加：
```typescript
'frontend-design':
  'Anthropic 官方前端设计指导技能。为新 UI 或现有界面提供独特的视觉设计方案，覆盖调色板、字体排版、布局、动效和文案写作。采用头脑风暴→规划→评审→构建→自评的结构化流程，避免千篇一律的模板化 AI 设计。触发词：UI设计、前端设计、视觉设计、网页设计。',
```

**验证**：本地 `npm run validate:registry` 通过，CI build 成功。

### 提交历史恢复

**背景**：`chore/sync-upstream-skills` 分支之前是主开发分支，包含 319 个提交。由于分支管理问题，main 分支只有 132 个提交。

**操作**：
1. 备份 main 分支
2. 将 main 重置到 `chore/sync-upstream-skills`
3. 从备份中恢复 `frontend-design` 技能
4. 更新 registry 和所有生成文件
5. 删除远程 `chore/sync-upstream-skills` 分支

**结果**：
- 提交数: 132 → 320
- 技能数: 26 → 48

### Matt Pocock 批量导入 + Merge 冲突（2026-07-01）

**背景**：[[mattpocock-collection\]\] 批量导入期间，上游同步 CI 同时创建了 `chore/sync-upstream-skills` 分支，导致 merge 时有 13 个文件冲突。

**冲突文件**：8 个已有 Matt Pocock 技能（grill-me, handoff, tdd, to-issues, to-prd, prototype, improve-codebase-architecture, git-guardrails-claude-code）+ 5 个生成文件（README, registry, web data, sitemap, index.html）

**解决策略**：对所有冲突文件使用 `--ours`（保留本地版本含 Matt Pocock 标签和更新后的 upstreamSha），然后 re-generate registry 确保一致性。

**导入所用脚本**：`scripts/import_mattpocock.py`、`scripts/update_existing.py`

**最终规模**：73 个技能（+25 净增）

## 已知问题

- Node.js 20 deprecated 警告：Actions 使用 Node.js 20 但被强制运行在 Node.js 24 上（不影响功能）

## 嵌入向量生成流程（2026-07-03）

[[vector-search|向量检索]]功能引入了 `registry/skills-embeddings.json` 文件，需要在技能更新后重新生成。

**当前流程**（手动）：
```bash
SILICONFLOW_API_KEY=sk-xxx npx tsx scripts/generate-embeddings.ts
```

**注意事项**：
- 嵌入文件（~2.2MB）已纳入 git 版本管理
- 技能新增/修改后需重新生成嵌入并 commit
- i18n 中文描述变更也需重新生成（嵌入文本依赖 `skill-descriptions.ts`）
- CI 目前不自动验证嵌入一致性（未来可加入）

相关：[[registry-system]], [[upstream-sync]], [[release-process]], [[mattpocock-collection]], [[source-mattpocock-collection]], [[vector-search]], [[siliconflow-api]]
