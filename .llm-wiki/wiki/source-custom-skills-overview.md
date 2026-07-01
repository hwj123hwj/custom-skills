---
type: source
source_path: .
date: 2026-06-25
tags: [overview, skills, registry, cli, web, ci-cd, frontend-design, i18n]
---

# Source: Custom Skills 全仓概览

> 2026-06-25 对项目根目录 `.` 的全面摄取，涵盖项目状态、最新变更和 CI/CD 修复。

## Key Takeaways

1. **技能规模**: 48 个技能，覆盖编程开发、内容创作、平台工具、效率工具、知识搜索、数据处理 6 大类别
2. **Agent 规模**: 6 个 Agent 定义（architect, coding-agent, intel-agent, knowledge-to-deck-agent, tdd-guide, vid-publisher-agent）
3. **技术栈**: Web (React 19 + Vite 7 + Tailwind CSS), CLI (TypeScript + Commander), Registry (Node.js 脚本生成)
4. **最新变更**: 新增 `frontend-design` 技能（Anthropic 官方设计指导）
5. **CI/CD 修复**: 修复了 `frontend-design` 缺少中文描述导致的验证失败
6. **提交历史恢复**: 从 `chore/sync-upstream-skills` 分支恢复了 320 个提交

## 项目结构

```
custom-skills/
├── skills/              # 48 个技能源目录
├── agents/              # 6 个 Agent 定义
├── registry/            # 自动生成的 JSON 注册表
├── web/                 # React 技能广场
├── cli/                 # TypeScript CLI 工具
├── docs/                # 详细文档
└── .github/workflows/   # CI/CD 配置
```

## 新增技能: frontend-design

**来源**: Anthropic 官方前端设计指导
**功能**: 为新 UI 或现有界面提供独特的视觉设计方案
**覆盖领域**:
- 调色板选择
- 字体排版
- 布局设计
- 动效设计
- 文案写作

**设计流程**: 头脑风暴 → 规划 → 评审 → 构建 → 自评

**触发词**: UI设计、前端设计、视觉设计、网页设计

## CI/CD 修复详情

### 问题
`frontend-design` 技能在 `registry/skills.json` 中存在，但缺少 `web/src/i18n/skill-descriptions.ts` 中的中文描述条目。

### 错误信息
```
i18n 覆盖检查失败，缺少以下技能的中文描述:
  - frontend-design
请在 web/src/i18n/skill-descriptions.ts 中添加缺失的描述条目
```

### 修复方案
在 `skillDescriptionsZh` 对象中添加：
```typescript
'frontend-design':
  'Anthropic 官方前端设计指导技能。为新 UI 或现有界面提供独特的视觉设计方案，覆盖调色板、字体排版、布局、动效和文案写作。采用头脑风暴→规划→评审→构建→自评的结构化流程，避免千篇一律的模板化 AI 设计。触发词：UI设计、前端设计、视觉设计、网页设计。',
```

### 验证
- ✅ `npm run validate:registry` 通过
- ✅ `npm run generate:registry` 成功
- ✅ CI build 成功

## 提交历史恢复

**背景**: `chore/sync-upstream-skills` 分支之前是主开发分支，包含 319 个提交。

**操作**:
1. 备份当前 main 分支
2. 将 main 重置到 `chore/sync-upstream-skills`
3. 从备份中恢复 `frontend-design` 技能
4. 更新 registry 和所有生成文件
5. 删除远程 `chore/sync-upstream-skills` 分支

**结果**:
- 提交数: 132 → 320
- 技能数: 26 → 48

## 技能分类体系

| 分组 | 技能数 | 代表技能 |
|------|--------|----------|
| 编程开发 | ~15 | tdd, diagnose, review, improve-codebase-architecture |
| 内容创作 | ~12 | content-repurposer, short-drama-pipeline, videocut |
| 平台工具 | ~10 | bilibili-cli, boss-cli, twitter-cli, xiaohongshu-cli |
| 效率工具 | ~5 | brainstorming, handoff, to-issues, to-prd |
| 知识搜索 | ~3 | tavily, knowledge-skill |
| 数据处理 | ~3 | paddleocr-doc-parsing, officecli-docx |

## 关键文件

| 文件 | 用途 |
|------|------|
| `registry/skills.json` | 主注册表，由脚本自动生成 |
| `web/src/i18n/skill-descriptions.ts` | 中文描述，手动维护 |
| `web/scripts/sync-skills.ts` | 从 SKILL.md 生成 registry |
| `web/scripts/validate-registry.ts` | 验证一致性 |
| `.github/workflows/registry-check.yml` | CI 流程 |

## 交叉引用

- [[architecture]] — 项目架构
- [[skill-spec]] — SKILL.md 规范
- [[registry-system]] — Registry 生成与校验
- [[ci-cd-workflows]] — CI/CD 流程
- [[web-app]] — Web 技能广场
- [[cli-tool]] — CLI 工具
- [[tag-system]] — 标签分类体系
