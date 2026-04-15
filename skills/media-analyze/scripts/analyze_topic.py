# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

#!/usr/bin/env python3
"""Topic analysis search wrapper.

This script gives agents a single stable entrypoint for topic analysis.
It currently uses Tavily as the primary search backend and returns a
normalized result shape so the skill does not need to teach raw curl usage.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


TAVILY_URL = "https://api.tavily.com/search"


def tavily_search(topic: str, max_results: int, search_depth: str) -> dict:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("缺少 TAVILY_API_KEY 环境变量")

    payload = json.dumps(
        {
            "query": topic,
            "max_results": max_results,
            "search_depth": search_depth,
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        TAVILY_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Tavily 请求失败: HTTP {exc.code} {body}") from exc


def to_markdown(topic: str, data: dict) -> str:
    results = data.get("results", [])
    lines = [
        f"# 话题搜索结果: {topic}",
        "",
        f"- 结果数量: {len(results)}",
        "",
    ]

    for index, item in enumerate(results, start=1):
        title = item.get("title") or "无标题"
        url = item.get("url") or ""
        snippet = item.get("content") or item.get("snippet") or ""
        lines.extend(
            [
                f"{index}. {title}",
                f"   - 链接: {url}",
                f"   - 摘要: {snippet}",
                "",
            ]
        )

    return "\n".join(lines).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="按话题搜索媒体分析资料")
    parser.add_argument("--topic", required=True, help="要分析的话题")
    parser.add_argument("--max-results", type=int, default=8, help="返回结果数")
    parser.add_argument(
        "--search-depth",
        choices=["basic", "advanced"],
        default="advanced",
        help="Tavily 搜索深度",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="输出格式",
    )
    args = parser.parse_args()

    data = tavily_search(args.topic, args.max_results, args.search_depth)

    if args.format == "json":
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    print(to_markdown(args.topic, data))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - CLI error path
        print(f"错误: {exc}", file=sys.stderr)
        sys.exit(1)
