---
type: concept
date: 2026-06-23
tags: [tags, validation, white-list, categories]
---

# Tag System

> SKILL.md frontmatter 中的 tag 白名单与分类体系。当前 40+ 个允许标签。

## Tag 白名单

当前允许的 40+ 个 tag：

```
Analysis, Architecture, Audio, Automation, CLI, Coding, Content,
Crawler, Debugging, DevOps, Education, Forensics, Installer, Knowledge,
LocalData, Marketplace, Matt Pocock, Media, Monitoring, Planning, Product,
Productivity, Recruitment, Research, Search, Security, Social,
Summary, Testing, Tools, Utility, Video, Web, Workflow, Writing,
Bilibili, WeChat, Weibo, Xiaohongshu
```

**2026-07-01 新增**：`DevOps`、`Tools`、`Workflow`、`Matt Pocock`

新增 tag 必须同步更新 `web/scripts/validate-registry.ts` 中的 `ALLOWED_TAGS`。

## 分类映射（6 组）

Tag 通过 `skill-categories.ts` 映射到 **6 个高层分组**（2026-06 更新），供 Web UI 筛选使用：

| 分组 | 包含 tag |
|------|----------|
| 编程开发 | Architecture, Backend, CLI, Coding, DevOps, Engineering, Frontend, Mobile, Testing |
| 内容创作 | Audio, Content, Media, Publishing, Video, Writing |
| 平台工具 | Platform, Productivity, Social, Tools |
| 效率工具 | Automation, Planning, Workflow |
| 知识搜索 | Knowledge, Research, Search |
| 数据处理 | Data, Documents, OCR, PDF |

### 历史演变

- **2026-06-14**：初始 5 组（coding/content/platform/knowledge/product）
- **2026-06-23**：扩展为 6 组，product 拆分为「效率工具」和「数据处理」

## Tag 注册流程

1. 在 `web/scripts/validate-registry.ts` 的 `ALLOWED_TAGS` 数组中添加新 tag
2. 在 `web/src/lib/skill-categories.ts` 中将新 tag 映射到对应分组
3. 运行 `cd web && npm run generate:registry` 验证
4. 提交 PR

## 常见 Tag 使用场景

| 场景 | 推荐 Tag |
|------|----------|
| 命令行工具 | CLI |
| 视频相关 | Video, Media |
| 社交平台 | Social, Bilibili, WeChat, Weibo, Xiaohongshu |
| 代码质量 | Testing, Debugging, Architecture |
| 内容生成 | Writing, Content |
| 数据处理 | Data, Documents, OCR, PDF |
| CI/CD 和工具 | DevOps, Tools |
| 工作流 | Workflow |
| Matt Pocock 来源 | Matt Pocock（配合其他功能标签使用）|

## 来源标签

`Matt Pocock` 是一个**来源标签**（Source Tag），标记技能来自 mattpocock/skills 仓库，用于 Web 广场按来源筛选和上游同步。当前共 34 个技能标记此标签，详见 [[mattpocock-collection]]。

### 历史演变

- **2026-06-14**：初始 5 组
- **2026-06-23**：扩展为 6 组
- **2026-07-01**：新增 `DevOps`、`Tools`、`Workflow`、`Matt Pocock`；引入"来源标签"概念

相关：[[skill-spec]], [[web-app]], [[registry-system]], [[mattpocock-collection]], [[source-readme-2026-06-23]]
