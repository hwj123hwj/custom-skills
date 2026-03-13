---
name: wechat-search
description: 用于搜索微信公众号文章的工具。每当用户要求搜索“微信公众号文章”、“微信文章”、或者通过关键词在微信平台上寻找特定话题、新闻、深度报道（如“公众号搜一下AI进展”）时，必须触发此技能。本技能仅负责搜索文章列表（标题、链接、摘要、账号名），不负责抓取全文（阅读全文需要 camoufox 或其他技能）。
---

# 微信公众号搜索

本技能通过 `miku_ai` 库实现微信公众号文章的快速搜索。

## 依赖安装
```bash
pip install miku_ai
```

## 核心工作流

### 1. 搜索文章列表
使用 Python 一行流命令调用 `miku_ai.get_wexin_article` 进行异步搜索。

**执行命令：**
```bash
python3 -c "
import asyncio
from miku_ai import get_wexin_article
async def search():
    results = await get_wexin_article('搜索关键词', 5)
    for a in results:
        print(f\"{a['title']} | {a['account']} | {a['url']}\")
        print(f\"摘要: {a['digest']}\n---\")
asyncio.run(search())
"
```

## 数据说明
搜索结果通常包含以下字段：
- `title`: 文章标题
- `account`: 公众号名称
- `digest`: 文章摘要
- `url`: 微信文章链接 (`mp.weixin.qq.com`)

## 约束与限制
- **仅限搜索**：只返回搜索结果列表和摘要。
- **全文阅读**：获取链接后，若需阅读全文，请使用 `camoufox` 或 `browser` 技能。
- **搜狗索引**：结果基于搜狗微信搜索，部分新发或冷门文章可能存在延迟。

## 排障指引
- **ImportError**: 请运行 `pip install miku_ai`。
- **结果为空**: 尝试更换更通用的关键词。
- **网络超时**: 搜狗接口偶发不稳定，重试即可。
