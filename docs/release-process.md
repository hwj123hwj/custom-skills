---
type: guide
date: 2026-06-12
tags: [release, npm, git, tag, workflow]
---

# Custom Skills 发版流程

> 参考 DeepVCode Client 的 release process，适配本项目的 npm 手动发版模式。

## 核心规则

1. **已推送的 commit 禁止 amend** — 需要修改就新建 commit
2. **package.json 版本号必须 < 仓库 tag 版本号** — 仓库 tag 是整体版本（如 `v1.5.0`），npm 包版本是 CLI 子包版本（如 `1.2.0`），两者独立递增
3. **打 tag 前本地 build 必须全绿** — `npm run build` 在 cli 目录下通过后才可发版

## 发版步骤

### Step 1: 修改代码 + 本地验证

```bash
# 在 cli 目录下验证构建
cd cli && npm run build
```

### Step 2: 更新版本号

手动修改 `cli/package.json` 的 `version` 字段。语义化版本：
- fix / refactor → patch (+0.0.1)
- feat → minor (+0.1.0)
- breaking change → major (+1.0.0)

### Step 3: 重新构建验证

```bash
cd cli && npm run build   # 必须 0 错误
```

### Step 4: npm publish

```bash
cd cli && npm publish --access public
```

如果遇到 401/404，先登录：
```bash
npm login
```

### Step 5: commit + push

```bash
git add cli/package.json
git commit -m "chore: bump cli version to x.y.z"
git push origin main
```

### Step 6: 打仓库 tag（可选，整体版本）

```bash
# 仓库 tag 和 npm 包版本独立递增
git tag vx.y.z
git push origin vx.y.z
```

## 版本号约定

| 类型 | 递增规则 | 示例 |
|------|----------|------|
| fix / refactor | patch (+0.0.1) | 1.1.2 → 1.1.3 |
| feat | minor (+0.1.0) | 1.1.2 → 1.2.0 |
| breaking change | major (+1.0.0) | 1.2.0 → 2.0.0 |

## 发版记录

### v1.2.0 (2026-06-12)

**变更内容：**
- 重写 `knowledge_export.py` 为自包含的 agent 导出层
  - 移除对 `knowledge_search.py` 函数的依赖
  - 搜索 + 补字段合在单一 `export_for_agent()` 函数
  - 关键词搜索新增 `ai_summary` 匹配
  - 输出 `content_preview`（截断 1000 字）替代原始 `content`
  - 默认 limit 从 10 改为 8

**仓库 tag：** v1.5.0
**npm 包版本：** 1.2.0
