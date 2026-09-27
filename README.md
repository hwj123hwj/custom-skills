# Custom Skills Hub

> 一个以 `SKILL.md` 为唯一事实来源的 AI 技能注册表，同时服务人类用户（Web 技能广场）和 AI Agent（CLI 安装工具）。

[![CI](https://github.com/hwj123hwj/custom-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/hwj123hwj/custom-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## ✨ 核心特性

- 📦 **69 技能**：覆盖编程开发、内容创作、平台工具、效率工具等多个领域，含全量 [Matt Pocock](https://github.com/mattpocock/skills) 技能合集
- 🌐 **Web 技能广场**：基于 React 19 + Vite 的现代化界面，支持中英文双语
- 🔧 **CLI 安装工具**：一键安装技能到 `.agents/skills/` 目录，兼容任意 AI Agent 工具
- 🔄 **上游同步**：CI 自动同步第三方技能仓库，保持技能最新
- 📋 **标准化规范**：统一的 SKILL.md 格式，支持 frontmatter 元数据
- 🏷️ **智能分类**：基于标签的技能分类与筛选系统

---

## 🚀 快速开始

### 浏览技能

访问 [Web 技能广场](https://hwj123hwj.asia/) 在线浏览所有技能。

或使用 CLI：

```bash
# 列出所有技能
npx custom-skills list

# 按关键词搜索
npx custom-skills search <keyword>

# 查看技能详情
npx custom-skills info <skill-id>
```

### 安装技能

```bash
# 安装到当前项目 (.agents/skills/<id>/)
npx custom-skills install <skill-id>

# 安装到全局 (~/.agents/skills/<id>/)
npx custom-skills install <skill-id> --global

# 或使用标准 skills CLI
npx skills add https://github.com/hwj123hwj/custom-skills --skill <skill-id>
```

---

## 📁 项目结构

```
custom-skills/
├── skills/              # 技能目录（唯一数据源）
│   ├── <skill-id>/
│   │   ├── SKILL.md     # 技能定义（YAML frontmatter + 使用说明）
│   │   └── scripts/     # 可选：技能脚本
│   └── ...
├── registry/            # 自动生成的注册表
│   ├── skills.json
│   └── ...
├── web/                 # React 技能广场
│   ├── src/
│   ├── scripts/         # 生成与校验脚本
│   └── package.json
├── cli/                 # TypeScript CLI 工具
│   ├── src/
│   └── package.json
└── docs/                # 详细文档
```

---

## 🛠️ 开发指南

### 前置要求

- Node.js 20+
- npm 或 yarn

### 常用命令

```bash
# Web 开发
cd web && npm run dev              # 启动开发服务器
cd web && npm run build            # 构建生产版本
cd web && npm run lint             # ESLint 检查
cd web && npm run validate:registry  # 验证 registry 一致性

# 修改 SKILL.md 后必须运行（CI 强制）
cd web && npm run generate:registry  # 重新生成 registry + README 技能表

# CLI 开发
cd cli && npm run dev -- <command>  # 用 ts-node 运行 CLI
cd cli && npm run build             # TypeScript 编译
```

### 添加新技能

1. 在 `skills/` 下创建目录：`skills/<skill-id>/`
2. 创建 `SKILL.md`，包含 YAML frontmatter：

```yaml
---
name: <skill-id>          # 必填，kebab-case，与目录名一致
description: <触发描述>    # 必填，对 Agent 自动识别最关键
tags:                     # 必填，1-5 个标签
  - <tag1>
  - <tag2>
displayName: <展示名>      # 可选，默认取 H1 标题
author: <作者>            # 可选
version: <版本号>          # 可选
---

# 技能使用说明
...
```

3. 运行 `cd web && npm run generate:registry`
4. 在 `web/src/i18n/skill-descriptions.ts` 中添加中文描述
5. 提交 PR

### 添加第三方技能（上游同步）

在 SKILL.md 中添加以下 frontmatter：

```yaml
---
name: <skill-id>
upstream: <owner/repo>        # 上游仓库
upstreamPath: <path/to/skill> # 上游技能路径
upstreamSha: <commit-sha>     # 当前同步的 commit
author: <author-id>           # 原作者
---
```

CI 会在每天 UTC 02:00 自动检查上游更新，如有变更会创建 PR。

---

## 📋 技能列表

<!-- SKILL_TABLE:START -->
| 技能 | 说明 |
|------|------|
| [archify](./skills/archify) | Create polished, validated architecture, workflow, sequence, data-flow, and lifecycle/state diagr... |
| [asr](./skills/asr) | Unified ASR (Speech Recognition) skill with pluggable providers (strategy pattern). |
| [bilibili-cli](./skills/bilibili-cli) | CLI skill for Bilibili (哔哩哔哩, B站) with token-efficient YAML output for AI agents to browse videos... |
| [boss-cli](./skills/boss-cli) | Use boss-cli for ALL BOSS 直聘 operations — searching jobs, viewing recommendations, managing appli... |
| [butler](./skills/butler) | 管家技能 — 项目感知、日报分析、知识库维护。 |
| [content-adapt](./skills/content-adapt) | 根据视频内容分析结果，生成适合目标平台发布的标题、描述、标签等信息。 |
| [content-repurposer](./skills/content-repurposer) | Markdown 提示工程驱动的内容复用技能，含 7 个子技能（LinkedIn/Twitter/Medium/Substack/Newsletter/GitHub Pages + 编排器）。 |
| [darwin-skill](./skills/darwin-skill) | Darwin Skill (达尔文.skill): autonomous skill optimizer inspired by Karpathy's autoresearch. |
| [douyin-upload](./skills/douyin-upload) | 当你需要登录抖音账号、检查 Cookie、上传视频或发布图文时使用本技能。 |
| [drawio-skill](./skills/drawio-skill) | Use when user requests diagrams, flowcharts, architecture charts, or visualizations. |
| [emil-design-eng](./skills/emil-design-eng) | This skill encodes Emil Kowalski's philosophy on UI polish, component design, animation decisions... |
| [feishu-md-exporter](./skills/feishu-md-exporter) | Export Feishu/Lark docs or entire Drive folders to local Markdown using the official Open Platfor... |
| [frontend-design](./skills/frontend-design) | Guidance for distinctive, intentional visual design when building new UI or reshaping an existing... |
| [guizang-ppt-skill](./skills/guizang-ppt-skill) | 生成横向翻页网页 PPT（单 HTML 文件），含 WebGL 背景、章节幕封、数据大字报、图片网格等模板。 |
| [huashu-nuwa](./skills/huashu-nuwa) | 女娲造人：输入人名/主题/甚至只是模糊需求，自动深度调研→思维框架提炼→生成可运行的人物Skill。 |
| [image-provider](./skills/image-provider) | Unified image generation skill with pluggable providers (strategy pattern). |
| [impeccable](./skills/impeccable) | Designs and iterates production-grade frontend interfaces. |
| [knowledge-skill](./skills/knowledge-skill) | 个人知识流水线技能。 |
| [llm-price-tracker](./skills/llm-price-tracker) | Track and compare LLM API pricing across 147+ providers. |
| [memory-organizer](./skills/memory-organizer) | 长期记忆整理指南。 |
| [mp-weixin-ops](./skills/mp-weixin-ops) | 微信公众号一站式运营 Skill。 |
| [officecli-docx](./skills/officecli-docx) | Use this skill any time a .docx file is involved -- as input, output, or both. |
| [open-kimi-ppt](./skills/open-kimi-ppt) | Create, edit, replicate, read, and export presentations. |
| [paddleocr-doc-parsing](./skills/paddleocr-doc-parsing) | Use this skill to extract structured Markdown/JSON from PDFs and document images—tables with cell... |
| [paddleocr-text-recognition](./skills/paddleocr-text-recognition) | Use this skill whenever the user wants text extracted from images, photos, scans, screenshots, or... |
| [react-native-best-practices](./skills/react-native-best-practices) | Provides React Native performance optimization guidelines for FPS, TTI, bundle size, memory leaks... |
| [short-drama-pipeline](./skills/short-drama-pipeline) | AI 短剧/短视频全链路生产技能。 |
| [short-video-replicator](./skills/short-video-replicator) | 短视频爆款复刻一站式工具。 |
| [stock-analysis](./skills/stock-analysis) | 股票智能分析技能。 |
| [storage-analyzer](./skills/storage-analyzer) | macOS / Windows 只读存储分析助手（自动识别系统）。 |
| [taste-skill](./skills/taste-skill) | Anti-slop frontend skill for landing pages, portfolios, and redesigns. |
| [tavily](./skills/tavily) | Unified Tavily CLI skill — web search, URL extraction, and deep research via `tvly`. |
| [tts](./skills/tts) | Unified TTS (Text-to-Speech) skill with pluggable providers (strategy pattern). |
| [vertex-video-reader](./skills/vertex-video-reader) | Use this skill to read, analyze, and understand video files using Google Cloud Vertex AI's lightw... |
| [video-analyze](./skills/video-analyze) | 当你需要分析视频内容（抽取关键帧、识别语音）时使用本技能。 |
| [videocut](./skills/videocut) | 口播视频一站式剪辑 Skill。 |
| [weibo-skill](./skills/weibo-skill) | 微博内容搜索、热搜查看、用户动态及评论读取。 |
| [weread-skills](./skills/weread-skills) | 微信读书助手 — 搜索书籍、管理书架、查看笔记划线、浏览书评、阅读统计、发现推荐好书 |
| [xiaohongshu-cli](./skills/xiaohongshu-cli) | Use xiaohongshu-cli for ALL Xiaohongshu (Little Red Book, 小红书) operations — searching notes, read... |
<!-- SKILL_TABLE:END -->

---

## 📚 文档

- [项目架构](./docs/architecture.md) — 模块划分、数据流、技术栈
- [Skill 规范](./docs/skill-spec.md) — SKILL.md frontmatter、tag 白名单、命名规则
- [Registry 生成与校验](./docs/registry-workflow.md) — generate/validate 命令与提交流程
- [上游同步机制](./docs/upstream-sync.md) — CI 自动同步第三方技能
- [文档索引](./docs/README.md) — 所有文档的完整列表

---

## 🏷️ 标签分类

技能通过标签进行分类，支持以下高层分组：

| 分组 | 标签 |
|------|------|
| 编程开发 | Architecture, Backend, CLI, Coding, DevOps, Engineering, Frontend, Mobile, Testing |
| 内容创作 | Audio, Content, Media, Publishing, Video, Writing |
| 平台工具 | Platform, Productivity, Social, Tools |
| 效率工具 | Automation, Planning, Workflow |
| 知识搜索 | Knowledge, Research, Search |
| 数据处理 | Data, Documents, OCR, PDF |

### 🧠 Matt Pocock 技能合集

已收录 [mattpocock/skills](https://github.com/mattpocock/skills) 全部技能（34 个），通过 `Matt Pocock` 标签统一筛选。涵盖工程流程、代码设计、产品思维、写作方法论四大领域：

| 领域 | 技能数 | 代表技能 |
|------|--------|----------|
| 工程流程 | 10 | ask-matt, triage, implement, tdd, diagnosing-bugs, code-review |
| 代码设计 | 5 | codebase-design, domain-modeling, improve-codebase-architecture, prototype, resolving-merge-conflicts |
| 产品思维 | 7 | grill-me, grill-with-docs, grilling, handoff, to-prd, to-issues, decision-mapping |
| 工具 & 写作 | 12 | teach, wizard, setup-pre-commit, scaffold-exercises, writing-great-skills, writing-beats, writing-fragments, writing-shape, edit-article, migrate-to-shoehorn, setup-matt-pocock-skills, obsidian-vault |

> **上游自动同步**：CI 每日 UTC 02:00 检查上游更新，自动创建 PR。所有 Matt Pocock 技能均标注 `upstream`/`upstreamSha` 元数据。

---

## 🔄 CI/CD

本项目使用 GitHub Actions 进行自动化：

- **Registry Check**：每次 PR 验证 registry 一致性（技能数 + i18n 覆盖）
- **Upstream Sync**：每日 UTC 02:00 检查上游技能更新（当前覆盖：Matt Pocock 34 个技能）
- **Web Build**：自动构建并部署到 GitHub Pages

---

## 🤝 贡献

欢迎贡献新技能或改进现有技能！

1. Fork 本仓库
2. 创建你的技能目录 `skills/<skill-id>/`
3. 编写 `SKILL.md`（参考 [Skill 规范](./docs/skill-spec.md)）
4. 运行 `cd web && npm run generate:registry`
5. 提交 PR

### 贡献指南

- 技能 `name` 必须是 kebab-case，且与目录名一致
- 新增 tag 需先在 `web/scripts/validate-registry.ts` 的 `ALLOWED_TAGS` 中注册
- 新增技能需在 `web/src/i18n/skill-descriptions.ts` 中补充中文描述
- 不要手动编辑 `registry/skills.json`，它由脚本自动生成

---

## 📄 License

MIT License - 详见 [LICENSE](./LICENSE)

---

## 🔗 相关链接

- [Web 技能广场](https://hwj123hwj.asia/)
- [GitHub 仓库](https://github.com/hwj123hwj/custom-skills)
- [问题反馈](https://github.com/hwj123hwj/custom-skills/issues)

---

## 🙏 致谢

感谢所有技能贡献者和上游仓库维护者！

特别感谢：
- [mattpocock/skills](https://github.com/mattpocock/skills) - 提供多个工程类技能
