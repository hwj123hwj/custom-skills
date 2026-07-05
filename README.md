# Custom Skills Hub

> 一个以 `SKILL.md` 为唯一事实来源的 AI Agent 技能注册表，同时服务人类用户（Web 技能广场）和 AI Agent（CLI 安装工具）。

[![CI](https://github.com/hwj123hwj/custom-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/hwj123hwj/custom-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## ✨ 核心特性

- 📦 **73 技能**：覆盖编程开发、内容创作、平台工具、效率工具等多个领域，含全量 [Matt Pocock](https://github.com/mattpocock/skills) 技能合集
- 🌐 **Web 技能广场**：基于 React 19 + Vite 的现代化界面，支持中英文双语
- 🔧 **CLI 安装工具**：一键安装技能到 Claude Code 或其他 AI Agent
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

#### Claude Code

```bash
# 安装到当前项目 (.claude/skills/<id>/)
npx custom-skills install <skill-id> --claude

# 安装到全局 (~/.claude/skills/<id>/)
npx custom-skills install <skill-id> --claude --global

# 安装 Agent 及其依赖的所有技能
npx custom-skills install <agent-id> --agent
npx custom-skills install <agent-id> --agent --global
```

#### OpenClaw

```bash
# 安装到 ~/.openclaw/workspace/skills/
npx custom-skills install <skill-id>

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
├── agents/              # Agent 定义
│   └── <agent-id>.md
├── registry/            # 自动生成的注册表
│   ├── skills.json
│   ├── agents.json
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
| [ask-matt](./skills/ask-matt) | Ask which skill or flow fits your situation. |
| [asr](./skills/asr) | Unified ASR (Speech Recognition) skill with pluggable providers (strategy pattern). |
| [bilibili-cli](./skills/bilibili-cli) | CLI skill for Bilibili (哔哩哔哩, B站) with token-efficient YAML output for AI agents to browse videos... |
| [boss-cli](./skills/boss-cli) | Use boss-cli for ALL BOSS 直聘 operations — searching jobs, viewing recommendations, managing appli... |
| [brainstorming](./skills/brainstorming) | You MUST use this before any creative work - creating features, building components, adding funct... |
| [butler](./skills/butler) | 管家技能 — 项目感知、日报分析、知识库维护。 |
| [code-review](./skills/code-review) | Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes — Stan... |
| [codebase-design](./skills/codebase-design) | Shared vocabulary for designing deep modules. |
| [content-adapt](./skills/content-adapt) | 根据视频内容分析结果，生成适合目标平台发布的标题、描述、标签等信息。 |
| [content-repurposer](./skills/content-repurposer) | Markdown 提示工程驱动的内容复用技能，含 7 个子技能（LinkedIn/Twitter/Medium/Substack/Newsletter/GitHub Pages + 编排器）。 |
| [darwin-skill](./skills/darwin-skill) | Darwin Skill (达尔文.skill): autonomous skill optimizer inspired by Karpathy's autoresearch. |
| [decision-mapping](./skills/decision-mapping) | Turn a loose idea into a sequenced map of investigation tickets, then drive them to resolution on... |
| [diagnose](./skills/diagnose) | Disciplined diagnosis loop for hard bugs and performance regressions. |
| [diagnosing-bugs](./skills/diagnosing-bugs) | Diagnosis loop for hard bugs and performance regressions. |
| [domain-modeling](./skills/domain-modeling) | Build and sharpen a project's domain model. |
| [douyin-upload](./skills/douyin-upload) | 当你需要登录抖音账号、检查 Cookie、上传视频或发布图文时使用本技能。 |
| [drawio-skill](./skills/drawio-skill) | Use when user requests diagrams, flowcharts, architecture charts, or visualizations. |
| [edit-article](./skills/edit-article) | Edit and improve articles by restructuring sections, improving clarity, and tightening prose. |
| [emil-design-eng](./skills/emil-design-eng) | This skill encodes Emil Kowalski's philosophy on UI polish, component design, animation decisions... |
| [feishu-md-exporter](./skills/feishu-md-exporter) | Export Feishu/Lark docs or entire Drive folders to local Markdown using the official Open Platfor... |
| [frontend-design](./skills/frontend-design) | Guidance for distinctive, intentional visual design when building new UI or reshaping an existing... |
| [frontend-slides](./skills/frontend-slides) | Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint files. |
| [git-guardrails-claude-code](./skills/git-guardrails-claude-code) | Set up Claude Code hooks to block dangerous git commands (push, reset --hard, clean, branch -D, e... |
| [grill-me](./skills/grill-me) | Interview the user relentlessly about a plan or design until reaching shared understanding, resol... |
| [grill-with-docs](./skills/grill-with-docs) | A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary)... |
| [grilling](./skills/grilling) | Interview the user relentlessly about a plan or design. |
| [guizang-ppt-skill](./skills/guizang-ppt-skill) | 生成横向翻页网页 PPT（单 HTML 文件），含 WebGL 背景、章节幕封、数据大字报、图片网格等模板。 |
| [handoff](./skills/handoff) | Compact the current conversation into a handoff document for another agent to pick up. |
| [huashu-design](./skills/huashu-design) | 花叔Design（Huashu-Design）——用HTML做高保真原型、交互Demo、幻灯片、动画、设计变体探索+设计方向顾问+专家评审的一体化设计能力。 |
| [huashu-nuwa](./skills/huashu-nuwa) | 女娲造人：输入人名/主题/甚至只是模糊需求，自动深度调研→思维框架提炼→生成可运行的人物Skill。 |
| [image-provider](./skills/image-provider) | Unified image generation skill with pluggable providers (strategy pattern). |
| [impeccable](./skills/impeccable) | Designs and iterates production-grade frontend interfaces. |
| [implement](./skills/implement) | Implement a piece of work based on a PRD or set of issues. |
| [improve-codebase-architecture](./skills/improve-codebase-architecture) | Find deepening opportunities in a codebase, informed by the domain language in CONTEXT.md and the... |
| [knowledge-skill](./skills/knowledge-skill) | 个人知识流水线技能。 |
| [llm-price-tracker](./skills/llm-price-tracker) | Track and compare LLM API pricing across 147+ providers. |
| [loop-me](./skills/loop-me) | Grill me about specs for the workflows I want to build, within this workspace. |
| [memory-organizer](./skills/memory-organizer) | 长期记忆整理指南。 |
| [migrate-to-shoehorn](./skills/migrate-to-shoehorn) | Migrate test files from `as` type assertions to @total-typescript/shoehorn. |
| [mp-weixin-ops](./skills/mp-weixin-ops) | 微信公众号一站式运营 Skill。 |
| [obsidian-vault](./skills/obsidian-vault) | Search, create, and manage notes in the Obsidian vault with wikilinks and index notes. |
| [officecli-docx](./skills/officecli-docx) | Use this skill any time a .docx file is involved -- as input, output, or both. |
| [paddleocr-doc-parsing](./skills/paddleocr-doc-parsing) | Use this skill to extract structured Markdown/JSON from PDFs and document images—tables with cell... |
| [paddleocr-text-recognition](./skills/paddleocr-text-recognition) | Use this skill whenever the user wants text extracted from images, photos, scans, screenshots, or... |
| [prototype](./skills/prototype) | Build a throwaway prototype to flesh out a design before committing to it. |
| [react-native-best-practices](./skills/react-native-best-practices) | Provides React Native performance optimization guidelines for FPS, TTI, bundle size, memory leaks... |
| [resolving-merge-conflicts](./skills/resolving-merge-conflicts) | Use when you need to resolve an in-progress git merge/rebase conflict. |
| [review](./skills/review) | Two-axis code review — Standards (does code follow documented standards?) and Spec (does code mat... |
| [scaffold-exercises](./skills/scaffold-exercises) | Create exercise directory structures with sections, problems, solutions, and explainers that pass... |
| [setup-matt-pocock-skills](./skills/setup-matt-pocock-skills) | Configure this repo for the engineering skills — set up its issue tracker, triage label vocabular... |
| [setup-pre-commit](./skills/setup-pre-commit) | Set up Husky pre-commit hooks with lint-staged (Prettier), type checking, and tests in the curren... |
| [short-drama-pipeline](./skills/short-drama-pipeline) | AI 短剧/短视频全链路生产技能。 |
| [short-video-replicator](./skills/short-video-replicator) | 短视频爆款复刻一站式工具。 |
| [stock-analysis](./skills/stock-analysis) | 股票智能分析技能。 |
| [storage-analyzer](./skills/storage-analyzer) | macOS / Windows 只读存储分析助手（自动识别系统）。 |
| [taste-skill](./skills/taste-skill) | Anti-slop frontend skill for landing pages, portfolios, and redesigns. |
| [tavily](./skills/tavily) | Unified Tavily CLI skill — web search, URL extraction, and deep research via `tvly`. |
| [tdd](./skills/tdd) | Test-driven development with red-green-refactor loop. |
| [teach](./skills/teach) | Teach the user a new skill or concept, within this workspace. |
| [to-issues](./skills/to-issues) | Break a plan, spec, or PRD into independently-grabbable issues on the project issue tracker using... |
| [to-prd](./skills/to-prd) | Turn the current conversation context into a PRD (Product Requirements Document). |
| [triage](./skills/triage) | Move issues and external PRs through a state machine of triage roles — categorise, verify, grill... |
| [tts](./skills/tts) | Unified TTS (Text-to-Speech) skill with pluggable providers (strategy pattern). |
| [twitter-cli](./skills/twitter-cli) | Use twitter-cli for ALL Twitter/X operations — reading tweets, posting, replying, quoting, liking... |
| [ui-ux-pro-max](./skills/ui-ux-pro-max) | UI/UX design intelligence for web and mobile. |
| [vertex-video-reader](./skills/vertex-video-reader) | Use this skill to read, analyze, and understand video files using Google Cloud Vertex AI's lightw... |
| [video-analyze](./skills/video-analyze) | 当你需要分析视频内容（抽取关键帧、识别语音）时使用本技能。 |
| [videocut](./skills/videocut) | 口播视频一站式剪辑 Skill。 |
| [web-design-guidelines](./skills/web-design-guidelines) | Review UI code for Web Interface Guidelines compliance. |
| [weibo-skill](./skills/weibo-skill) | 微博内容搜索、热搜查看、用户动态及评论读取。 |
| [weread-skills](./skills/weread-skills) | 微信读书助手 — 搜索书籍、管理书架、查看笔记划线、浏览书评、阅读统计、发现推荐好书 |
| [wizard](./skills/wizard) | Generate an interactive bash wizard that walks a human through a manual procedure — third-party s... |
| [writing-beats](./skills/writing-beats) | Writing, exploit — assemble raw material into a journey of beats, grounding each term before a be... |
| [writing-fragments](./skills/writing-fragments) | Writing, explore — mine raw fragments, no structure yet. |
| [writing-great-skills](./skills/writing-great-skills) | Reference for writing and editing skills well — the vocabulary and principles that make a skill p... |
| [writing-shape](./skills/writing-shape) | Writing, exploit — shape raw material into an article, paragraph by paragraph. |
| [xiaohongshu-cli](./skills/xiaohongshu-cli) | Use xiaohongshu-cli for ALL Xiaohongshu (Little Red Book, 小红书) operations — searching notes, read... |
<!-- SKILL_TABLE:END -->

---

## 🤖 Agent 定义

除了单个技能，本项目还支持 Agent 定义，用于组合多个技能：

```bash
# 安装 Agent 及其依赖的所有技能
npx custom-skills install <agent-id> --agent
```

Agent 定义位于 `agents/` 目录，详见 [Agent 规范](./docs/agent-spec.md)。

---

## 📚 文档

- [项目架构](./docs/architecture.md) — 模块划分、数据流、技术栈
- [Skill 规范](./docs/skill-spec.md) — SKILL.md frontmatter、tag 白名单、命名规则
- [Agent 规范](./docs/agent-spec.md) — Agent 定义、类型、frontmatter
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

- **Registry Check**：每次 PR 验证 registry 一致性（72 技能 + i18n 覆盖 + Agent 校验）
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
- [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) - 提供 UI/UX 设计技能
