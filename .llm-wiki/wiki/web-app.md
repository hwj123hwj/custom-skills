---
type: entity
date: 2026-06-23
tags: [web, react, vite, skill-plaza, i18n]
---

# Web App

> 技能与 Agent 广场前端，基于 React 19 + Vite 7。当前展示 48 个技能和 6 个 Agent。

## 技术栈

| 技术 | 版本 |
|------|------|
| React | 19 |
| TypeScript | 5.9 |
| Vite | 7 |
| Tailwind CSS | 3.4 |
| React Router | 7 |
| i18next | 26 |
| Lucide React | 0.563 |

## 页面结构

- **Skills tab**：按 6 个高层分类筛选（见下方分类系统）
- **Agents tab**：展示 Agent 列表
- **Decks tab**：展示 showcase 幻灯片
- 共享 `CategoryChip` 组件

## 分类系统（6 组）

2026-06-23 更新：从 5 组扩展为 6 组。

| 分组 | 包含 tag |
|------|----------|
| 编程开发 | Architecture, Backend, CLI, Coding, DevOps, Engineering, Frontend, Mobile, Testing |
| 内容创作 | Audio, Content, Media, Publishing, Video, Writing |
| 平台工具 | Platform, Productivity, Social, Tools |
| 效率工具 | Automation, Planning, Workflow |
| 知识搜索 | Knowledge, Research, Search |
| 数据处理 | Data, Documents, OCR, PDF |

分组定义在 `web/src/lib/skill-categories.ts`。

## i18n 支持

- 中英文双语（zh/en）
- 技能描述在 `web/src/i18n/skill-descriptions.ts` 中维护
- 新增技能**必须**补充中文描述（CI 校验覆盖率）

## 构建与部署

- 静态站点，部署到 GitHub Pages
- `prebuild` 自动执行 `generate:registry`
- SEO 通过 `react-helmet-async` + 生成的 `sitemap.xml` + `index.html` meta 注入

## 常用开发命令

```bash
cd web && npm run dev              # 启动开发服务器
cd web && npm run build            # 构建生产版本
cd web && npm run lint             # ESLint 检查
cd web && npm run validate:registry  # 验证 registry 一致性
cd web && npm run generate:registry  # 重新生成 registry + README
```

相关：[[architecture]], [[registry-system]], [[skill-spec]], [[tag-system]], [[source-readme-2026-06-23]]
