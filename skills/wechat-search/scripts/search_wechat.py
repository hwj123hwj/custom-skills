# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "miku_ai",
# ]
# ///

#!/usr/bin/env python3
"""
微信公众号文章搜索

Usage:
    python search_wechat.py <keyword1> [keyword2] [keyword3] [--limit N]

Examples:
    python search_wechat.py "AI Agent"
    python search_wechat.py "OpenClaw" "小龙虾" "开源智能体" --limit 5
"""

import asyncio
import random
import sys
import argparse


async def deep_search(keywords_list: list[str], limit: int = 5):
    from miku_ai import get_wexin_article

    all_results = []
    for kw in keywords_list:
        for _ in range(3):
            try:
                results = await get_wexin_article(kw, limit)
                if results:
                    all_results.extend(results)
                    break
            except Exception:
                pass
            await asyncio.sleep(random.uniform(1.5, 3))

    seen = set()
    count = 0
    for a in all_results:
        url = a.get("url", "")
        if url and url not in seen:
            count += 1
            print(f"[{count}] {a.get('title', '(无标题)')}")
            print(f"    摘要: {a.get('digest', '无摘要')}")
            print(f"    链接: {url}")
            print("---")
            seen.add(url)

    if count == 0:
        print("[EMPTY] 未找到相关文章，请尝试其他关键词")


def main():
    parser = argparse.ArgumentParser(description="微信公众号文章搜索")
    parser.add_argument("keywords", nargs="+", help="搜索关键词（可多个）")
    parser.add_argument("--limit", type=int, default=5, help="每个关键词最多返回条数（默认 5）")
    args = parser.parse_args()

    asyncio.run(deep_search(args.keywords, args.limit))


if __name__ == "__main__":
    main()
