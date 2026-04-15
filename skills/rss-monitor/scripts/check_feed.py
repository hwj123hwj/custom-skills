# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

#!/usr/bin/env python3
"""Fetch and normalize RSS feed entries for rss-monitor."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET


def resolve_feed_url(feed_id: str | None, feed_url: str | None) -> str:
    if feed_url:
        return feed_url
    if not feed_id:
        raise ValueError("必须提供 --feed-id 或 --feed-url")

    template = os.getenv("WEWE_RSS_FEED_URL_TEMPLATE")
    if not template:
        raise ValueError("缺少 WEWE_RSS_FEED_URL_TEMPLATE 环境变量")
    return template.replace("{feed_id}", feed_id)


def parse_feed(xml_text: str, limit: int) -> list[dict]:
    root = ET.fromstring(xml_text)
    items = root.findall(".//item")
    entries = []
    for item in items[:limit]:
        entries.append(
            {
                "title": item.findtext("title", default="无标题"),
                "link": item.findtext("link", default=""),
                "published": item.findtext("pubDate", default=""),
                "description": item.findtext("description", default=""),
            }
        )
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description="检查 RSS feed 更新")
    parser.add_argument("--feed-id", help="feed_id，配合模板环境变量使用")
    parser.add_argument("--feed-url", help="直接提供 RSS URL")
    parser.add_argument("--limit", type=int, default=10, help="最多返回条目数")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    url = resolve_feed_url(args.feed_id, args.feed_url)
    with urllib.request.urlopen(url, timeout=30) as response:
        xml_text = response.read().decode("utf-8", errors="ignore")

    entries = parse_feed(xml_text, args.limit)

    if args.json:
        print(json.dumps({"feed_url": url, "count": len(entries), "entries": entries}, ensure_ascii=False, indent=2))
    else:
        print(f"Feed: {url}")
        for index, entry in enumerate(entries, start=1):
            print(f"{index}. {entry['title']}")
            print(f"   - 发布时间: {entry['published']}")
            print(f"   - 链接: {entry['link']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - CLI error path
        print(f"错误: {exc}", file=sys.stderr)
        raise SystemExit(1)
