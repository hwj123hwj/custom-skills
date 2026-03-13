---
name: wechat-search
description: 用于搜索微信公众号文章的工具。每当用户要求搜索“微信公众号文章”、“微信文章”、或者通过关键词寻找特定话题（如“搜一下AI进展”）时，必须触发此技能。本技能负责搜索文章列表（标题、链接、摘要）。
---

# 微信公众号搜索

本技能通过 `miku_ai` 库实现微信公众号文章的搜索。

## 核心工作流：深度鲁棒搜索模式
微信搜索接口存在严格的风控（302 重定向）和关键词过滤。**绝对不能**因为一次或一个词的失败就放弃。AI 必须展现出极强的“死磕”精神，尝试多种策略直到挖出结果。

### 1. 多维度搜索策略 (死磕逻辑)
如果初次搜索失败、返回空或被风控，AI **必须**自动尝试以下变体进行多轮搜索：
- **同义词/关联词替换**：例如 OpenClaw -> 小龙虾、大龙虾、开源智能体。
- **组合长尾词**：关键词 + “实操”、“教程”、“2026”、“行业报告”。
- **拼音/英文混搜**：中英文交替尝试。

**执行命令示例：**
```bash
python3 -c "
import asyncio, random
from miku_ai import get_wexin_article

async def deep_search(keywords_list, limit=5):
    all_results = []
    for kw in keywords_list:
        # 每个词组尝试多轮，直到成功或穷尽策略
        for i in range(3): 
            try:
                results = await get_wexin_article(kw, limit)
                if results:
                    all_results.extend(results)
                    break # 当前关键词成功，跳到下一个关键词
            except Exception:
                pass
            await asyncio.sleep(random.uniform(1.5, 3)) # 随机避开风控
    
    # 去重并输出结果
    seen = set()
    for a in all_results:
        if a['url'] not in seen:
            print(f\"[SUCCESS] {a.get('title')}\")
            print(f\"DIGEST: {a.get('digest', '无摘要')}\")
            print(f\"URL: {a.get('url')}\n---\")
            seen.add(a['url'])

asyncio.run(deep_search(['主关键词', '关联词1', '关联词2']))
"
```

## 回复格式规范 (重要)
AI 展示结果时，必须严格遵守以下格式（不显示不可靠的公众号名称）：

**[数字]. [文章标题]**
- **核心内容**：[从摘要中提取的 1-2 句核心观点]
- [阅读全文]([URL 链接])

---

## 搜索技巧
- **不要轻言放弃**：微信接口波动大，重试和换词是常态。
- **链接时效**：链接包含临时签名，建议引导用户尽快阅读。

## 约束与限制
- **仅限搜索**：阅读全文需配合 `browser` 技能。
- **环境依赖**：需确保 `pip install miku_ai --break-system-packages` 已执行。
