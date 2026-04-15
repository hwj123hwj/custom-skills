---
name: media-analyze
displayName: Media Analyze
description: "媒体分析报告生成。多源搜索话题，自动生成结构化分析报告。触发场景：(1) 用户要求分析某个话题 (2) 需要生成话题调研报告 (3) 了解事件的舆论反应。关键词：分析话题、媒体报告、话题调研、舆论分析。"
tags:
  - Research
  - Analysis
  - Social
aliases:
  - 媒体分析
  - 话题分析
  - 舆情分析
scenarios:
  - 分析某个社会话题的舆论反应
  - 生成结构化调研报告
  - 汇总多平台搜索结果并给出观点
---

# 媒体分析技能

多源搜索话题，自动生成结构化分析报告。

## 核心原则

- 优先调用仓库自带 CLI，不要手写 `curl`
- 只传稳定参数：`topic`、结果数量、搜索深度
- 先拿结构化搜索结果，再写结论和报告

## 推荐入口

```bash
uv run skills/media-analyze/scripts/analyze_topic.py --topic "<话题>"
```

常用变体：

```bash
uv run skills/media-analyze/scripts/analyze_topic.py --topic "武汉大学图书馆事件"
uv run skills/media-analyze/scripts/analyze_topic.py --topic "两会 2026" --max-results 10
uv run skills/media-analyze/scripts/analyze_topic.py --topic "机器人创业" --search-depth advanced --format json
```

## 工作流

### Step 1: 先跑统一搜索入口

- 默认命令已经封装好 Tavily 请求，不需要再构造 HTTP body 或 headers
- `--format markdown` 适合直接阅读，`--format json` 适合后续加工

### Step 2: 如果结果不足，再补外部信息

- 先判断结果是否覆盖了主流媒体、事件时间线、核心观点
- 不足时，再用其他技能补充
- 微信文章：调用 `wechat-search` 的脚本入口
- 微博热点：调用 `weibo-skill` 的脚本入口
- 网页全文：再考虑浏览器或网页抓取技能

### Step 3: 基于搜索结果写报告

整合数据，按以下结构输出：

```markdown
# XXX 话题媒体分析报告

> 报告生成时间：YYYY-MM-DD

## 事件概述
## 完整时间线
## 各平台热度分析
## 舆论焦点
## 媒体报道分析
## 结论与洞察
```

## 配置要求

需要在本地环境中提供 `TAVILY_API_KEY`：

```bash
export TAVILY_API_KEY="tvly-your-api-key-here"
```

## 参数说明

- `--topic`：必填，分析主题
- `--max-results`：默认 `8`
- `--search-depth`：`basic` 或 `advanced`
- `--format`：`markdown` 或 `json`

## 注意事项

- 默认先走脚本；只有脚本无法满足需求时，才考虑更底层的接口排查
- 标注数据获取时间
- 每个数据点标注来源
- 呈现多方观点
- 敏感信息脱敏处理
