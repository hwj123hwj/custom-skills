---
type: entity
date: 2026-06-14
tags: [registry, generation, validation]
---

# Registry System

> 自动生成的机器可读索引系统，来自 `docs/registry-workflow.md`。

## 生成流程

```bash
cd web && npm run generate:registry
```

这条命令依次执行：
1. `sync-skills.ts` — 读取 `skills/*/SKILL.md` → 生成 `registry/skills.json` + `web/src/data/skills-data.json`
2. `sync-readme.ts` — 更新 README 中的技能表
3. `sync-agents.ts` — 读取 `agents/*.md` → 生成 `registry/agents.json` + web data
4. `sync-stories.ts` — 生成 stories 数据
5. `sync-decks.ts` — 生成 decks 数据

同时也会更新：`web/public/robots.txt`、`web/public/sitemap.xml`、`web/index.html`（SEO meta）

## 校验

```bash
cd web && npm run validate:registry
```

检查内容：
- registry 与 web mirror 是否一致
- README 技能表是否同步
- 文件系统与 registry 是否一致
- tag 是否符合白名单
- i18n 覆盖是否完整
- Agent registry 存在时是否一致

## 设计决策

- 不允许手动编辑 registry JSON 文件
- 修改 `SKILL.md` 后必须重新 generate:registry
- CI 中的 Registry Check 会验证生成的 registry 是否与已提交的一致

## lastUpdated 策略

2026-06-14 修复：agents/decks/stories 的 sync 脚本已追加内容保护逻辑（内容不变保留旧 `lastUpdated`），与 skills 保持一致。防止 timestamp 漂移导致 CI 失败。

相关：[[architecture]], [[skill-spec]], [[ci-cd-workflows]], [[release-process]]
