# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "miku_ai",
# ]
# ///

#!/usr/bin/env python3
"""Search WeChat articles through a stable CLI wrapper."""

from __future__ import annotations

import argparse
import asyncio
import json
import random
import sys
from typing import Iterable

from miku_ai import get_wexin_article


def build_query_variants(query: str, deep: bool) -> list[str]:
    variants = [query.strip()]
    if not deep:
        return variants

    suffixes = ["实操", "教程", "行业报告"]
    for suffix in suffixes:
        variants.append(f"{query} {suffix}")
    return list(dict.fromkeys(variants))


async def search_once(query: str, limit: int) -> list[dict]:
    results = await get_wexin_article(query, limit)
    normalized = []
    for item in results or []:
        normalized.append(
            {
                "title": item.get("title", "无标题"),
                "digest": item.get("digest", ""),
                "url": item.get("url", ""),
            }
        )
    return normalized


async def deep_search(queries: Iterable[str], limit: int) -> list[dict]:
    merged: list[dict] = []
    seen_urls: set[str] = set()

    for query in queries:
        for _ in range(3):
            try:
                results = await search_once(query, limit)
                for item in results:
                    url = item.get("url")
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    merged.append(item)
                if results:
                    break
            except Exception:
                pass
            await asyncio.sleep(random.uniform(1.5, 3.0))

    return merged


def to_markdown(results: list[dict]) -> str:
    if not results:
        return "未找到结果。"

    lines: list[str] = []
    for index, item in enumerate(results, start=1):
        lines.extend(
            [
                f"{index}. {item['title']}",
                f"   - 摘要: {item.get('digest') or '无摘要'}",
                f"   - 链接: {item.get('url') or '无链接'}",
                "",
            ]
        )
    return "\n".join(lines).strip()


async def async_main() -> int:
    parser = argparse.ArgumentParser(description="搜索微信公众号文章")
    parser.add_argument("--query", required=True, help="搜索关键词")
    parser.add_argument("--limit", type=int, default=5, help="每轮最多返回结果数")
    parser.add_argument("--deep", action="store_true", help="启用自动换词与重试")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    results = await deep_search(build_query_variants(args.query, args.deep), args.limit)

    if args.json:
        print(json.dumps({"query": args.query, "count": len(results), "results": results}, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(results))

    return 0 if results else 1


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(async_main()))
    except KeyboardInterrupt:
        raise SystemExit(130)
