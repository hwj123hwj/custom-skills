# Custom Skills 安装指南

> 本文档供 AI Agent 读取，用于了解如何使用和安装本站的 AI 技能。

## 概述

`custom-skills` 是一个 AI 技能集合仓库。本仓库支持“双轨制”安装模式：
1. **标准生态安装 (面向外部终端用户及任意 Agent)**
2. **专属 CLI 静默安装 (面向站内专属 Agent, 如 OpenClaw)**

## 安装模式详述

### 模式 1: 标准生态安装 (推荐外部使用)

任何兼容 Vercel `skills.sh` 协议的 Agent（如 Cursor, Cline, RooCode 等），都可以通过以下通用标准命令安装本仓库中的技能：

```bash
npx skills add https://github.com/hwj123hwj/custom-skills --skill <技能名>
```

**说明**: 该命令会唤起终端 TUI，由人类用户选择要安装到的目标 Agent 工作区中。

### 模式 2: 专属 CLI 安装 (适用于 OpenClaw 自主化执行)

本仓库提供了一个专属的 Node.js CLI 工具 `custom-skills`，专为全自动、无交互静默安装设计。

**搜索技能:**
```bash
npx custom-skills search <关键词>
```

**静默安装技能:**
```bash
npx custom-skills install <技能名或关键词>
```
*注: 此命令会将代码直接克隆并放入默认工作区 (例如 `~/.openclaw/workspace/skills/`)。支持 `--target-dir <dir>` 自定义路径。*

**查看所有技能:**
```bash
npx custom-skills list
```

**获取技能详情:**
```bash
npx custom-skills info <技能名>
```

## JSON 输出模式 (针对模式 2)

所有 `custom-skills` 命令支持 `--json` 参数，返回供 Agent 易于解析的结构化数据：

```bash
npx custom-skills search 微博 --json
```

## 常用技能清单

| 技能名 | 功能 | 触发场景关键词 |
|--------|------|--------|
| `weibo-skill` | 微博搜索、热搜、评论 | 微博、热搜 |
| `rss-monitor` | RSS 监控与摘要 | RSS、公众号监控、信息流 |
| `knowledge-skill` | 知识入库与搜索 | 入库、知识库、知识管理 |
| `wechat-search` | 微信文章搜索 | 微信文章、公众号 |
| `skill-browser-crawl` | 网页爬虫 | 爬虫、网页抓取 |
| `media-analyze` | 媒体话题分析 | 话题调研、舆情 |
| `idea-incubator` | 产品孵化与方案 | 产品想法、技术方案 |

## 相关链接

- 技能仓库：https://github.com/hwj123hwj/custom-skills
- 技能索引数据：https://github.com/hwj123hwj/custom-skills/blob/main/registry/skills.json
- Agent 开发上下文：https://github.com/hwj123hwj/custom-skills/blob/main/AGENT.md
