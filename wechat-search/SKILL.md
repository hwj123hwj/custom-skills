---
name: wechat-search
description: 用于搜索微信公众号文章的工具。每当用户要求搜索“微信公众号文章”、“微信文章”、或者通过关键词寻找特定话题（如“搜一下AI进展”）时，必须触发此技能。本技能负责搜索文章列表（标题、链接、摘要）。
---

# 微信公众号搜索

本技能通过 `miku_ai` 库实现微信公众号文章的搜索。

## 核心工作流：鲁棒搜索模式
微信搜索接口对高频词有严格风控（302 重定向）。**必须**使用以下带重试逻辑的 Python 一行流进行搜索，以提高成功率。

### 1. 搜索文章列表（带重试与关键词优化）
如果初次搜索失败或返回空，AI 应自动尝试更具体的长尾关键词（如加上年份“2026”或关联词）。

**执行命令：**
```bash
python3 -c "
import asyncio, random
from miku_ai import get_wexin_article

async def robust_search(kw, limit=5):
    for i in range(3): # 最多尝试3次
        try:
            results = await get_wexin_article(kw, limit)
            if results:
                for a in results:
                    print(f\"[SUCCESS] {a.get('title')} | {a.get('account', 'N/A')}\")
                    print(f\"URL: {a.get('url')}\n---\")
                return True
        except Exception:
            pass
        await asyncio.sleep(random.uniform(1, 2))
    return False

asyncio.run(robust_search('用户关键词'))
```

## 搜索技巧
- **精准匹配**：遇到 302 错误或无结果时，建议将关键词优化为“关键词 + 年份”或“关键词 + 观点词”（如“教育 2026”、“AI 行业报告”）。
- **链接时效**：返回的 `mp.weixin.qq.com` 链接通常包含临时签名，建议引导用户尽快阅读。

## 约束与限制
- **仅限搜索**：只返回列表，阅读全文需配合 `browser` 技能。
- **环境依赖**：需确保 `pip install miku_ai --break-system-packages` 已执行。
