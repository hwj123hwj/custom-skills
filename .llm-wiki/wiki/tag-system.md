---
type: concept
date: 2026-06-14
tags: [tags, validation, white-list]
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

新增 tag 必须同步更新 `web/scripts/validate-registry.ts`。

## 分类映射

Tag 通过 `skill-categories.ts` 映射到 5 个高层分组，供 UI 筛选使用。

相关：[[skill-spec]], [[web-app]], [[registry-system]]
