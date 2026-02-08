# Custom Skills Hub

本项目是一个用于管理和运行自定义技能（Skills）的中心化仓库。它包含了一系列自动化脚本，可以帮助你处理 B 站视频、分析数据、同步内容等。

## 📖 快速开始

### 环境准备

本项目推荐使用 [uv](https://github.com/astral-sh/uv) 进行 Python 依赖管理和脚本运行。

1. 安装 `uv`:
   ```bash
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. 运行脚本:
   ```bash
   uv run bilibili-toolkit/scripts/bili_video.py
   ```

## 🛠️ 现有工具集

### 1. [Bilibili Toolkit](./bilibili-toolkit)
一站式的 B 站自动化工具箱，包含以下功能：
- **视频下载**: 自动下载视频和音频并合并。
- **内容采集与转录**: 采集 UP 主视频列表，利用 Whisper/ASR 进行文稿转录。
- **知识库构建**: 将视频文稿存入 PostgreSQL 并构建向量索引。
- **语义搜索**: 基于 LlamaIndex 的混合检索，支持 AI 回答和源文档溯源。
- **UP 主分析**: 分析 UP 主的核心观点和内容风格。

### 2. [BJTU Classroom Query](./bjtuo-classroom-query)
北京交通大学（BJTU）教室课表查询自动化工具：
- **AI 登录**: 集成智谱 AI 视觉模型，自动识别 CAS 验证码。
- **空闲分析**: 自动解析教务系统，提取每日空闲的大节信息。
- **结果截图**: 自动截取查询结果并保存。

### 3. [Idea Incubator](./idea-incubator)
专业的 CPO + 技术合伙人助手，用于孵化产品想法：
- **想法澄清**: 挖掘真实需求和痛点。
- **方案挑战**: 对技术方案进行压力测试。
- **文档生成**: 自动生成技术设计文档（RFC/Spec）。
- **同步归档**: 将想法 Markdown 同步到数据库。

### 4. [Browser Crawl](./skill-browser-crawl)
基于浏览器的轻量级网页爬虫：
- **单页提取**: 爬取单个 URL 并提取其 Markdown 内容。
- **深度爬取**: 递归爬取整个文档站点或多页网站。
- **JS 渲染**: 支持 JavaScript 渲染和页面截图。

## 📜 开发规范

为了保持代码质量和一致性，所有新技能的开发请参考 [GUIDELINES.md](./GUIDELINES.md)。

主要原则：
- 使用 `uv` 的 PEP 723 内联元数据管理依赖。
- 统一使用 `get_env_flexible` 加载配置。
- 优先使用异步 I/O。
- 使用 `rich` 提供美观的终端输出。
