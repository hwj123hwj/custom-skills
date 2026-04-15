---
name: wechat-search
displayName: WeChat Search
description: 用于搜索微信公众号文章的工具。每当用户要求搜索“微信公众号文章”、“微信文章”、或者通过关键词寻找特定话题（如“搜一下AI进展”）时，必须触发此技能。本技能负责搜索文章列表（标题、链接、摘要）。
tags:
  - Search
  - WeChat
  - Content
aliases:
  - 微信文章
  - 公众号搜索
  - 微信搜索
scenarios:
  - 搜索某个主题的微信公众号文章
  - 根据关键词找公众号内容
  - 汇总相关文章标题和链接
---

# 微信公众号搜索

本技能通过 `miku_ai` 库实现微信公众号文章搜索。

## 核心原则

- 优先调用 CLI wrapper，不要再写 `python3 -c`
- 只给它传 `query`、`limit`、`deep`
- 把换词、重试、去重封在脚本里，让模型少处理转义和异常

## 推荐入口

```bash
uv run skills/wechat-search/scripts/search_wechat.py --query "<关键词>" --deep
```

常用变体：

```bash
uv run skills/wechat-search/scripts/search_wechat.py --query "AI Agent" --deep
uv run skills/wechat-search/scripts/search_wechat.py --query "多模态创业" --limit 8 --deep
uv run skills/wechat-search/scripts/search_wechat.py --query "OpenClaw" --limit 5 --json
```

## 工作流

### Step 1: 默认启用深搜模式

- 微信搜索经常风控或空结果
- `--deep` 会自动做换词、重试和去重
- 一般不要自己手动拼“关联词 1、关联词 2”，先让脚本处理

### Step 2: 输出结果时做一层摘要整理

展示结果时建议用这个格式：

```markdown
1. 文章标题
   - 核心内容：从摘要里提炼 1-2 句
   - 阅读链接：https://...
```

### Step 3: 结果为空时的处理

- 先重试一次同样命令
- 再换更短、更口语化的关键词
- 再考虑用浏览器搜索公众号文章，而不是直接放弃

## 参数说明

- `--query`：必填，搜索关键词
- `--limit`：每轮最多返回条数，默认 `5`
- `--deep`：启用自动换词与重试
- `--json`：输出原始结构化结果

## 约束与限制

- 仅限搜索列表，阅读全文需要配合浏览器技能
- 链接常带临时签名，最好尽快阅读
- 需要环境里已安装 `miku_ai`
