---
type: guide
date: 2026-06-14
tags: [release, npm, git, tag, workflow]
---

# Custom Skills 发版流程

> 参考 DeepVCode Client 的 release process，适配本项目的 npm 手动发版模式。

## 核心规则

1. **已推送的 commit 禁止 amend** — 需要修改就新建 commit
2. **package.json 版本号必须 < 仓库 tag 版本号** — 仓库 tag 是整体版本（如 `v1.5.0`），npm 包版本是 CLI 子包版本（如 `1.2.0`），两者独立递增
3. **打 tag 前本地 build 必须全绿** — `npm run build` 在 cli 目录下通过后才可发版
4. **发版前必须重新生成 registry 并 commit** — `cd web && npm run generate:registry`，否则 CI 会因生成文件未 commit 而失败
5. **发版前必须确认 CI 全绿** — `gh run list --limit 3` 检查最近 push 的 Registry Check 状态

## 发版步骤（8 步）

### Step 1: 修改代码 + 本地验证
```bash
cd cli && npm run build
```

### Step 2: 重新生成 registry 文件（必须！）
```bash
cd web && npm run generate:registry
git add registry/ web/src/data/ web/public/ web/index.html README.md
git commit -m "chore: regenerate registry"
```

### Step 3: 更新版本号
手动修改 `cli/package.json` 的 `version` 字段：fix → patch, feat → minor, breaking → major

### Step 4: 重新构建验证
```bash
cd cli && npm run build   # 必须 0 错误
```

### Step 5: npm publish
```bash
# 方式 1：automation token（推荐，免 OTP）
npm config set //registry.npmjs.org/:_authToken <token> --location=user
npm publish --access public

# 方式 2：OTP（6 位数字，有效期约 30 秒）
npm publish --access public --otp=<6位数字>
```

### Step 6: commit + push
```bash
git add cli/package.json
git commit -m "chore: bump cli version to x.y.z"
git push origin main
```

### Step 7: 确认 CI 全绿
```bash
gh run list --limit 3
```

### Step 8: 打仓库 tag（可选）
```bash
git tag vx.y.z
git push origin vx.y.z
```

## 版本号约定

| 类型 | 递增 | 示例 |
|------|------|------|
| fix/refactor | patch (+0.0.1) | 1.1.2 → 1.1.3 |
| feat | minor (+0.1.0) | 1.1.2 → 1.2.0 |
| breaking | major (+1.0.0) | 1.2.0 → 2.0.0 |

## 发版记录

### v1.2.0 (2026-06-12)
- 重写 knowledge_export.py 为自包含导出层
- npm 1.2.0 | tag v1.5.0 | ⚠️ 当时 npm publish 未完成（token 过期）

### v1.2.1-v1.2.3
（发版记录未详细整理）

### v1.3.0 (2026-06-13)
- 删除 wx-cli 技能
- lastUpdated 内容保护逻辑（agents/decks/stories）
- npm 1.3.0 | tag v1.6.0

### v1.3.1 (2026-06-14)
- 添加 jsdelivr CDN 镜像源（国内友好）
- 8s timeout
- npm 1.3.1

相关：[[ci-cd-workflows]], [[registry-system]], [[cli-tool]], [[architecture]]

