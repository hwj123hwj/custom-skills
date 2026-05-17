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
输出知识池质量快照，帮助判断下一步该补哪些知识源和摘要。
"""

import argparse
import json
from typing import Any

import psycopg2
import psycopg2.extras

from knowledge_search import DB_CONFIG


def fetch_rows(days: int = 30, source_type: str | None = None) -> list[dict[str, Any]]:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        params: list[Any] = [days]
        source_filter = ""
        if source_type:
            source_filter = "AND source_type = %s"
            params.append(source_type)

        cur.execute(
            f"""
            SELECT
                id,
                source_type,
                title,
                ai_summary,
                summary,
                content,
                metadata,
                created_at,
                updated_at,
                status
            FROM knowledge_items
            WHERE status = 'active'
              AND created_at >= NOW() - (%s || ' days')::interval
              {source_filter}
            ORDER BY created_at DESC
            """,
            params,
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def summarize_rows(rows: list[dict[str, Any]], days: int, source_type: str | None) -> dict[str, Any]:
    total = len(rows)
    by_source: dict[str, dict[str, Any]] = {}
    weak_items: list[dict[str, Any]] = []

    for row in rows:
        source = str(row.get("source_type") or "unknown")
        ai_summary = str(row.get("ai_summary") or "").strip()
        metadata = row.get("metadata") or {}
        content = str(row.get("content") or "")
        title = str(row.get("title") or "")

        bucket = by_source.setdefault(
            source,
            {
                "count": 0,
                "ai_summary_count": 0,
                "metadata_count": 0,
                "avg_content_length": 0.0,
            },
        )
        bucket["count"] += 1
        bucket["avg_content_length"] += len(content)
        if ai_summary:
            bucket["ai_summary_count"] += 1
        if metadata:
            bucket["metadata_count"] += 1

        if not ai_summary or len(content) < 180:
            weak_items.append(
                {
                    "title": title,
                    "source_type": source,
                    "created_at": row.get("created_at"),
                    "has_ai_summary": bool(ai_summary),
                    "content_length": len(content),
                }
            )

    for bucket in by_source.values():
        count = bucket["count"] or 1
        bucket["ai_coverage"] = round(bucket["ai_summary_count"] / count * 100, 1)
        bucket["metadata_coverage"] = round(bucket["metadata_count"] / count * 100, 1)
        bucket["avg_content_length"] = round(bucket["avg_content_length"] / count, 1)

    source_breakdown = [
        {"source_type": source, **data}
        for source, data in sorted(by_source.items(), key=lambda item: item[1]["count"], reverse=True)
    ]
    weak_items = weak_items[:5]

    actions: list[str] = []
    if total == 0:
        actions.append("当前时间窗口内没有活跃知识条目，先补入高质量原始内容再考虑 deck 产出。")
    else:
        low_ai_sources = [item["source_type"] for item in source_breakdown if item["ai_coverage"] < 80]
        if low_ai_sources:
            actions.append(f"优先补齐这些来源的 AI 摘要：{', '.join(low_ai_sources)}。")
        short_sources = [
            item["source_type"] for item in source_breakdown if float(item["avg_content_length"]) < 300
        ]
        if short_sources:
            actions.append(f"这些来源正文偏薄，后续 deck 前要谨慎：{', '.join(short_sources)}。")
        if not actions:
            actions.append("知识池整体可用，下一步优先继续按主题扩充高质量条目。")

    return {
        "days": days,
        "source_type": source_type,
        "total_active_items": total,
        "source_breakdown": source_breakdown,
        "weak_items": weak_items,
        "next_actions": actions,
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = ["# Knowledge Pool Report", ""]
    lines.append(f"- Days: {result['days']}")
    if result.get("source_type"):
        lines.append(f"- Source filter: {result['source_type']}")
    lines.append(f"- Total active items: {result['total_active_items']}")
    lines.append("")

    lines.append("## Source Breakdown")
    lines.append("")
    lines.append("| Source | Count | AI Coverage | Metadata Coverage | Avg Content Length |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for item in result["source_breakdown"]:
        lines.append(
            f"| {item['source_type']} | {item['count']} | {item['ai_coverage']}% | "
            f"{item['metadata_coverage']}% | {item['avg_content_length']} |"
        )
    lines.append("")

    lines.append("## Weak Items")
    lines.append("")
    if not result["weak_items"]:
        lines.append("- 暂无明显薄弱条目。")
    else:
        for item in result["weak_items"]:
            lines.append(f"### {item['title']}")
            lines.append(f"- Source: {item['source_type']}")
            lines.append(f"- Has AI summary: {'yes' if item['has_ai_summary'] else 'no'}")
            lines.append(f"- Content length: {item['content_length']}")
            lines.append("")

    lines.append("## Next Actions")
    lines.append("")
    for action in result["next_actions"]:
        lines.append(f"- {action}")

    return "\n".join(lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="输出知识池质量快照")
    parser.add_argument("--days", type=int, default=30, help="统计最近多少天的数据")
    parser.add_argument("--source-type", help="只看某个来源")
    parser.add_argument("--output", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--write", help="把 markdown 结果写入指定路径")
    args = parser.parse_args()

    rows = fetch_rows(days=args.days, source_type=args.source_type)
    result = summarize_rows(rows, days=args.days, source_type=args.source_type)

    if args.output == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        return

    markdown = render_markdown(result)
    if args.write:
        from pathlib import Path

        path = Path(args.write)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown, encoding="utf-8")
    print(markdown)


if __name__ == "__main__":
    main()
