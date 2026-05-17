#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "psycopg2-binary",
#     "python-dotenv",
#     "requests",
# ]
# ///
"""
为缺少 AI 摘要的知识条目批量回填一句话摘要。
"""

import argparse
import json
from typing import Any

import psycopg2
import psycopg2.extras

from knowledge_save import DB_CONFIG, generate_ai_summary


def fetch_missing_items(
    limit: int = 10,
    source_type: str | None = None,
    source_id: str | None = None,
) -> list[dict[str, Any]]:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        clauses = [
            "status = 'active'",
            "(ai_summary IS NULL OR btrim(ai_summary) = '')",
            "content IS NOT NULL",
            "btrim(content) <> ''",
        ]
        params: list[Any] = []
        if source_type:
            clauses.append("source_type = %s")
            params.append(source_type)
        if source_id:
            clauses.append("source_id = %s")
            params.append(source_id)

        params.append(limit)
        cur.execute(
            f"""
            SELECT id, source_type, source_id, title, content, created_at
            FROM knowledge_items
            WHERE {' AND '.join(clauses)}
            ORDER BY created_at DESC
            LIMIT %s
            """,
            params,
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def update_ai_summary(item_id: Any, ai_summary: str) -> None:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE knowledge_items
            SET ai_summary = %s,
                updated_at = NOW()
            WHERE id = %s
            """,
            (ai_summary, item_id),
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()


def backfill_ai_summary(
    limit: int = 10,
    source_type: str | None = None,
    source_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    items = fetch_missing_items(limit=limit, source_type=source_type, source_id=source_id)
    processed: list[dict[str, Any]] = []

    for item in items:
        title = str(item.get("title") or "")
        content = str(item.get("content") or "")
        ai_summary = generate_ai_summary(title, content).strip()
        if not ai_summary:
            continue

        if not dry_run:
            update_ai_summary(item["id"], ai_summary)

        processed.append(
            {
                "id": str(item["id"]),
                "source_type": item.get("source_type"),
                "source_id": item.get("source_id"),
                "title": title,
                "ai_summary": ai_summary,
            }
        )

    return {
        "dry_run": dry_run,
        "requested_limit": limit,
        "matched": len(items),
        "updated": len(processed),
        "results": processed,
    }


def main():
    parser = argparse.ArgumentParser(description="批量补齐缺失的 AI 摘要")
    parser.add_argument("--limit", type=int, default=10, help="最多处理多少条")
    parser.add_argument("--source-type", help="只处理某个来源类型")
    parser.add_argument("--source-id", help="只处理某个 source_id")
    parser.add_argument("--dry-run", action="store_true", help="只预览，不写入数据库")
    args = parser.parse_args()

    result = backfill_ai_summary(
        limit=args.limit,
        source_type=args.source_type,
        source_id=args.source_id,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
