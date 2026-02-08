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

### 🎯 analyze-up
分析指定 B 站 UP 主的核心观点和思维逻辑，基于已采集的视频数据进行 AI 深度分析并生成人格画像报告。

**使用场景**: 总结某 UP 主观点/思维模式与生成画像分析报告

### 🔍 ask-kb
对已采集的 B 站视频知识库进行语义检索和问答（向量搜索 + 上下文抽取 + 回答）。

**使用场景**: 查找相关视频片段与回答内容相关问题

### 🏫 bjtuo-classroom-query
北京交通大学（BJTU）教室课表查询自动化。支持 AI 验证码识别登录、按周次、教学楼、房号查询占用情况。

**使用场景**: 查询教室占用情况

### 📚 build-kb
构建/更新 B 站视频知识库向量索引（Embedding + PostgreSQL/pgvector），用于语义检索。

**使用场景**: 首次构建、增量更新、重建/验证索引

### 🕷️ crawl-and-export
采集 B 站视频（按 UP/按 BVID）并入库，同时支持从数据库导出文稿到 TXT。

**使用场景**: 批量采集、导出文稿与准备知识库数据

### 🎥 download-video
下载指定 BVID 的 B 站视频并用 FFmpeg 合并音视频为 MP4。

**使用场景**: 离线观看、编辑素材与批量下载

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
