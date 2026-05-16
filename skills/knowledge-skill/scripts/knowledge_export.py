#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "psycopg2-binary",
#     "python-dotenv",
#     "requests"
# ]
# ///
"""
知识导出脚本
面向 agent 提供更完整的候选知识结果。
"""

import argparse
import json
from typing import Any

import psycopg2
import psycopg2.extras

from knowledge_search import DB_CONFIG, search_hybrid, search_keyword, search_vector


def fetch_full_items(
    ids_in_order: list[int],
    content_chars: int = 1000,
) -> dict[int, dict[str, Any]]:
    """按 id 拉取完整知识条目，并截断 content 便于 agent 消费。"""
    if not ids_in_order:
        return {}

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cur.execute(
            """
            SELECT
                id,
                source_type,
                source_id,
                source_url,
                title,
                summary,
                ai_summary,
                content,
                metadata,
                created_at,
                updated_at,
                status
            FROM knowledge_items
            WHERE id = ANY(%s)
            """,
            [ids_in_order],
        )

        rows = cur.fetchall()
        items: dict[int, dict[str, Any]] = {}

        for row in rows:
            data = dict(row)
            raw_content = data.get("content") or ""
            if content_chars > 0 and len(raw_content) > content_chars:
                data["content"] = raw_content[:content_chars] + "..."
            items[int(data["id"])] = data

        return items
    finally:
        cur.close()
        conn.close()


def export_candidates(
    query: str,
    mode: str = "hybrid",
    limit: int = 10,
    source_type: str | None = None,
    content_chars: int = 1000,
) -> dict[str, Any]:
    """搜索后导出更完整的候选知识对象。"""
    if mode == "keyword":
        search_results = search_keyword(query, limit, source_type)
    elif mode == "vector":
        search_results = search_vector(query, limit, source_type)
    else:
        search_results = search_hybrid(query, limit, source_type)

    ids_in_order = [int(item["id"]) for item in search_results]
    full_items = fetch_full_items(ids_in_order, content_chars=content_chars)

    results: list[dict[str, Any]] = []
    for item in search_results:
        item_id = int(item["id"])
        full_item = full_items.get(item_id)
        if not full_item:
            continue

        merged = {
            "id": str(item_id),
            "title": full_item.get("title"),
            "source_type": full_item.get("source_type"),
            "source_id": full_item.get("source_id"),
            "source_url": full_item.get("source_url"),
            "summary": full_item.get("summary"),
            "ai_summary": full_item.get("ai_summary"),
            "content": full_item.get("content"),
            "metadata": full_item.get("metadata") or {},
            "created_at": full_item.get("created_at"),
            "updated_at": full_item.get("updated_at"),
            "status": full_item.get("status"),
            "search_type": item.get("search_type", mode),
            "similarity": item.get("similarity"),
        }
        results.append(merged)

    return {
        "query": query,
        "mode": mode,
        "total": len(results),
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description="导出适合 agent 消费的知识候选结果")
    parser.add_argument("--query", required=True, help="搜索关键词")
    parser.add_argument(
        "--mode",
        choices=["keyword", "vector", "hybrid"],
        default="hybrid",
        help="搜索模式",
    )
    parser.add_argument("--limit", type=int, default=10, help="返回数量")
    parser.add_argument("--source-type", help="筛选来源类型")
    parser.add_argument(
        "--content-chars",
        type=int,
        default=1000,
        help="content 截断长度，默认 1000 字符",
    )

    args = parser.parse_args()

    output = export_candidates(
        query=args.query,
        mode=args.mode,
        limit=args.limit,
        source_type=args.source_type,
        content_chars=args.content_chars,
    )

    print(json.dumps(output, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
