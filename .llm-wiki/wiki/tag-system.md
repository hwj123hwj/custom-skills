---
type: concept
date: 2026-06-23
tags: [tags, validation, white-list, categories]
---

# Tag System

> SKILL.md frontmatter 中的 tag 白名单与分类体系。

## Tag 白名单

当前允许的 30+ 个 tag：

```
Analysis, Architecture, Audio, Automation, CLI, Coding, Content,
Crawler, Debugging, Education, Forensics, Installer, Knowledge,
LocalData, Marketplace, Media, Monitoring, Planning, Product,
Productivity, Recruitment, Research, Search, Security, Social,
Summary, Testing, Utility, Video, Web, Writing,
Bilibili, WeChat, Weibo, Xiaohongshu
```

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

相关：[[skill-spec]], [[web-app]], [[registry-system]], [[source-readme-2026-06-23]]
