---
name: content-repurposer
displayName: Content Repurposer
description: "Markdown 提示工程驱动的内容复用技能，含 7 个子技能（LinkedIn/Twitter/Medium/Substack/Newsletter/GitHub Pages + 编排器）。支持语音配置系统、emoji 控制系统、正则黑名单。零依赖零修改即可用。"
emoji: "📝"
tags:
  - Content
  - Writing
  - Social
scenarios:
  - "把文章复用为 LinkedIn 帖子"
  - "把技术博客转成 Twitter 推文线程"
  - "把内容适配 Medium/Substack/Newsletter 发布"
  - "生成 GitHub Pages 博客文章"
aliases:
  - 内容复用
  - 跨平台发布
  - content repurpose
---

# Content Repurposer

把一份技术文章复用为 7 个平台的原生内容。纯 Markdown 提示工程，内置语音配置、emoji 控制和正则黑名单。

## 子技能

| 子技能 | 平台 | 说明 |
|--------|------|------|
| linkedin-write | LinkedIn | 专业社交平台帖子 |
| twitter-write | Twitter/X | 推文线程 |
| medium-write | Medium | 长文发布 |
| substack-write | Substack | Newsletter 风格文章 |
| newsletter-write | Newsletter | 邮件通讯 |
| github-page-write | GitHub Pages | 技术博客 |
| repurpose-all | 全平台 | 编排器，一键复用到所有平台 |

## 安装

```bash
./install.sh                 # symlink 7 个子技能到 ~/.claude/skills/
./install.sh /custom/path    # 自定义安装路径
```

## 使用

调用任意子技能即可，如 `/linkedin-write`、`/twitter-write` 等。`/repurpose-all` 可一键生成所有平台内容。

## 来源

- 上游仓库: [asadani/content-repurposer-skill](https://github.com/asadani/content-repurposer-skill)
