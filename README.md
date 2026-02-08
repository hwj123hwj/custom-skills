# Custom Skills

Collection of specialized AI agent skills.

## 🌐 Custom Skills Hub

We now have a dedicated showcase website for all custom skills!

- **Website**: [Custom Skills Hub](https://custom-skills.pages.dev/) (Deployed on Tencent Cloud EdgeOne)
- **Features**: Browse skills, search by tags, and view detailed installation guides in a modern UI.

## 📚 Documentation

- [Product Requirements Document (PRD)](custom-skills-hub-prd.md)
- [Technical Architecture](custom-skills-hub-technical-architecture.md)

## 🛠️ Installation

You can install any skill using the **Skills CLI**:

```bash
npx skills add https://github.com/hwj123hwj/custom-skills --skill <skill-id>
```

Replace `<skill-id>` with the name of the skill (e.g., `analyze-up`).

## ✨ Available Skills

### 📺 bilibili-toolkit
B 站综合工具箱。集成视频下载、文稿采集、向量知识库构建、语义检索问答及 UP 主人格画像分析等功能。

**使用场景**: 视频处理、内容采集、知识库管理及深度分析

### 🏫 bjtuo-classroom-query
北京交通大学（BJTU）教室课表查询自动化。支持 AI 验证码识别登录、按周次、教学楼、房号查询占用情况。

**使用场景**: 查询教室占用情况

### 💡 idea-incubator
专业的 CPO + 技术合伙人助手，帮助用户孵化想法、分析可行性并编写技术文档。

**使用场景**: 产品孵化、可行性分析、技术方案制定、MVP 定义

### 🌐 skill-browser-crawl
基于浏览器的轻量级网页爬虫。支持 JavaScript 渲染、Markdown 提取，并能递归爬取文档类网站。

**使用场景**: 爬取动态网页、提取 Markdown 内容、下载文档网站、递归抓取

## 🚀 Developer Guide

All skills can be invoked using the `uv run` command from the project root directory. Each skill has its own `SKILL.md` file with detailed usage instructions.

Example:
```bash
uv run .claude/skills/<skill-name>/scripts/<script-name>.py [arguments]
```

## 📋 Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- PostgreSQL database (for most skills)
- API keys configured in `.env` file
