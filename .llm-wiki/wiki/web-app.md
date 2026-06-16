---
type: entity
date: 2026-06-14
tags: [web, react, vite, skill-plaza]
---

# Web App

> 技能与 Agent 广场前端，基于 React 19 + Vite 7。

## 技术栈

| 技术 | 版本 |
|------|------|
| React | 19 |
| TypeScript | 5.9 |
| Vite | 7 |
| Tailwind CSS | 3.4 |
| React Router | 7 |
| i18next | 26 |

## 页面结构

- **Skills tab**：按 5 个高层分类筛选（coding/content/platform/knowledge/product）
- **Agents tab**：展示 Agent 列表
- **Decks tab**：展示 showcase 幻灯片
- 共享 `CategoryChip` 组件

## 分类系统

5 个 SkillGroupId 映射到 tag 白名单中的多个 tag：

| 分组 | 包含 tag |
|------|----------|
| coding | Coding, Testing, Debugging, Architecture, Security |
| content | Writing, Content, Media, Audio, Video |
| platform | Bilibili, WeChat, Weibo, Xiaohongshu, Social |
| knowledge | Knowledge, Search, Research, Web, Crawler, Education, Analysis |
| product | Product, Planning, LocalData, Forensics, Marketplace, Installer, Monitoring, Recruitment, Summary |

## 构建与部署

- 静态站点，部署到 GitHub Pages
- `prebuild` 自动执行 `generate:registry`
- SEO 通过 `react-helmet-async` + 生成的 `sitemap.xml` + `index.html` meta 注入

相关：[[architecture]], [[registry-system]], [[skill-spec]]
