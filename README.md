# Custom Skills Hub

一个以 `SKILL.md` 为源头的个人 AI 技能仓库（Agent Skills Registry）。提供人类可读的展示网页和供 AI / Agent 消费的 CLI 交互。

## 🌟 项目简介

Custom Skills Hub 旨在以现代化、开发者友好的方式呈现和分发 AI Agent 技能。为用户提供清晰的技能描述、使用场景和安装指南。

项目包含三大核心模块：
- **Skills 库 (`skills/`)**: 存放各种自动化脚本、爬虫、分析工具的核心能力仓库。
- **Web 技能广场 (`web/`)**: 作为一个美观的技能集合页面，用来展示、搜索和浏览技能。
- **CLI 工具 (`cli/`)**: 提供给终端用户和 AI Agent 安装、查看技能的命令行工具。

## 📦 快速使用

本仓库同时兼容两种使用场景：**供人类开发者浏览安装**（标准生态）与**供自主 Agent 自动化安装**（OpenClaw 专属）。

### 1. 面向开发者/终端用户 (Vercel 生态兼容)

如果你是开发者，在 Web 技能广场看到心仪的技能后，可以直接在终端运行以下标准的 `skills` 命令：

```bash
npx skills add https://github.com/hwj123hwj/custom-skills --skill <技能名>
```
该命令会唤起一个交互式 TUI 界面，允许你将技能安装给 Cursor、Cline 或 RooCode 等主流 AI Agent。

### 2. 面向本站专属 Agent (OpenClaw)

`custom-skills` 仓库自带了一个无交互、全自动的 CLI（`cli/`），这是专为本站的 Agent（如 OpenClaw）打造的快捷工具。Agent 可以通过执行该 CLI，静默地将所需技能拉取到它自己的工作区。

```bash
# 搜索技能
npx custom-skills search <关键词>

# 安装技能到本地 (Agent 自主安装)
npx custom-skills install <技能名>
```

### 启动本地 Web 站点

如果你想在本地预览技能广场（基于 Vite + React）：

```bash
cd web
npm install
npm run dev
```

> **注意：** 网站的数据来源于 `registry/skills.json`。当你新增或修改了技能后，可以在 `web` 目录下运行 `npm run generate:registry` 来更新索引。

## 📖 技能列表

<!-- SKILL_TABLE:START -->
| 技能 | 说明 |
|------|------|
| [bilibili-cli](./skills/bilibili-cli) | CLI skill for Bilibili (哔哩哔哩, B站) with token-eff... |
| [bjtuo-classroom-query](./skills/bjtuo-classroom-query) | 北京交通大学（BJTU）教室综合查询。 |
| [idea-incubator](./skills/idea-incubator) | 专业的 CPO + 技术合伙人助手，帮助用户孵化想法、分析可行性并编写技术文档。 |
| [knowledge-skill](./skills/knowledge-skill) | 个人知识库技能。 |
| [llm-wiki](./skills/llm-wiki) | 基于 Karpathy LLM Wiki 模式的个人知识库技能。 |
| [media-analyze](./skills/media-analyze) | 媒体分析报告生成。 |
| [memory-organizer](./skills/memory-organizer) | 长期记忆整理指南。 |
| [rss-monitor](./skills/rss-monitor) | RSS 消息监控与智能摘要。 |
| [skill-browser-crawl](./skills/skill-browser-crawl) | 基于浏览器的轻量级网页爬虫。 |
| [skills-sh-installer](./skills/skills-sh-installer) | 从 skills. |
| [wechat-decrypt](./skills/wechat-decrypt) | 解密微信 macOS 数据库，提取聊天记录。 |
| [wechat-search](./skills/wechat-search) | 用于搜索微信公众号文章的工具。 |
| [weibo-skill](./skills/weibo-skill) | 微博内容搜索、热搜查看、用户动态及评论读取。 |
<!-- SKILL_TABLE:END -->

## 🤝 参与贡献

如果你是 AI Agent，想要阅读本项目的技术架构、开发规范以及数据流机制，请阅读 [AGENT.md](./AGENT.md)。

## 📜 License

MIT License
