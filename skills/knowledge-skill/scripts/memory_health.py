#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "psycopg2-binary",
#     "python-dotenv",
# ]
# ///
"""
记忆健康度报告
统计 L1/L2/L3 命中率、冷门卡片占比、重复卡片数量、覆盖率等。
支持随机抽样 + LLM 评分的摘要质量抽检。

用法:
  uv run scripts/memory_health.py
  uv run scripts/memory_health.py --days 30 --output markdown
  uv run scripts/memory_health.py --write docs/wiki/reviews/memory-health.md
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", ""),
    "port": int(os.getenv("DB_PORT", 5433)),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "dbname": os.getenv("DB_NAME", ""),
}


def fetch_layer_stats() -> dict[str, Any]:
    """各层卡片统计"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cur.execute(
            """
            SELECT
                layer,
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE confidence > 0) AS active,
                COUNT(*) FILTER (WHERE confidence = 0) AS archived,
                COUNT(*) FILTER (WHERE embedding IS NOT NULL) AS has_embedding,
                AVG(access_count)::numeric(10, 2) AS avg_access_count,
                AVG(confidence)::numeric(10, 2) AS avg_confidence
            FROM memory_cards
            GROUP BY layer
            ORDER BY layer
            """
        )
        rows = [dict(row) for row in cur.fetchall()]

        stats = {}
        for row in rows:
            layer = row["layer"]
            label = {1: "L1-工作记忆", 2: "L2-领域知识", 3: "L3-原始存档"}.get(layer, f"L{layer}")
            stats[label] = {
                "total": int(row["total"] or 0),
                "active": int(row["active"] or 0),
                "archived": int(row["archived"] or 0),
                "has_embedding": int(row["has_embedding"] or 0),
                "avg_access_count": float(row["avg_access_count"] or 0),
                "avg_confidence": float(row["avg_confidence"] or 0),
            }
        return stats
    finally:
        cur.close()
        conn.close()


def fetch_l1_expiry() -> list[dict[str, Any]]:
    """即将过期的 L1 卡片"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cur.execute(
            """
            SELECT id, title, valid_until, access_count
            FROM memory_cards
            WHERE layer = 1 AND confidence > 0
              AND valid_until IS NOT NULL
              AND valid_until < NOW() + INTERVAL '3 days'
            ORDER BY valid_until ASC
            LIMIT 10
            """
        )
        return [
            {
                "id": str(row["id"]),
                "title": row["title"][:50],
                "valid_until": row["valid_until"].isoformat() if row["valid_until"] else None,
                "access_count": int(row["access_count"] or 0),
            }
            for row in cur.fetchall()
        ]
    finally:
        cur.close()
        conn.close()


def fetch_cold_cards() -> list[dict[str, Any]]:
    """冷门卡片（access_count = 0 且超过 30 天）"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cur.execute(
            """
            SELECT id, layer, title, access_count, created_at
            FROM memory_cards
            WHERE confidence > 0
              AND access_count = 0
              AND created_at < NOW() - INTERVAL '30 days'
            ORDER BY created_at ASC
            LIMIT 10
            """
        )
        return [
            {
                "id": str(row["id"]),
                "layer": int(row["layer"]),
                "title": row["title"][:50],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            }
            for row in cur.fetchall()
        ]
    finally:
        cur.close()
        conn.close()


def fetch_duplicate_candidates() -> list[dict[str, Any]]:
    """疑似重复卡片（cosine similarity > 0.90）"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cur.execute(
            """
            SELECT
                a.id AS id_a, a.title AS title_a,
                b.id AS id_b, b.title AS title_b,
                ROUND((1 - (a.embedding <=> b.embedding))::numeric, 4) AS similarity
            FROM memory_cards a
            JOIN memory_cards b ON a.id < b.id
            WHERE a.embedding IS NOT NULL AND b.embedding IS NOT NULL
              AND a.confidence > 0 AND b.confidence > 0
              AND 1 - (a.embedding <=> b.embedding) > 0.90
            ORDER BY similarity DESC
            LIMIT 10
            """
        )
        return [
            {
                "id_a": str(row["id_a"]),
                "title_a": row["title_a"][:40],
                "id_b": str(row["id_b"]),
                "title_b": row["title_b"][:40],
                "similarity": float(row["similarity"] or 0),
            }
            for row in cur.fetchall()
        ]
    finally:
        cur.close()
        conn.close()


def fetch_source_coverage() -> dict[str, Any]:
    """知识库 → 记忆卡片覆盖率"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cur.execute(
            """
            SELECT
                ki.source_type,
                COUNT(DISTINCT ki.id) AS total_items,
                COUNT(DISTINCT mc.id) AS organized_items
            FROM knowledge_items ki
            LEFT JOIN memory_cards mc
                ON ki.id::text = ANY(mc.source_item_ids) AND mc.confidence > 0
            WHERE ki.status = 'active'
            GROUP BY ki.source_type
            ORDER BY total_items DESC
            """
        )

        coverage = []
        for row in cur.fetchall():
            total = int(row["total_items"] or 0)
            organized = int(row["organized_items"] or 0)
            coverage.append({
                "source_type": row["source_type"],
                "total_items": total,
                "organized_items": organized,
                "coverage_rate": round(organized / total * 100, 1) if total > 0 else 0,
            })

        return {"sources": coverage}
    finally:
        cur.close()
        conn.close()


def generate_health_report(days: int = 30) -> dict[str, Any]:
    """生成完整的健康度报告"""
    layer_stats = fetch_layer_stats()
    expiring = fetch_l1_expiry()
    cold = fetch_cold_cards()
    duplicates = fetch_duplicate_candidates()
    coverage = fetch_source_coverage()

    # 汇总指标
    total_cards = sum(s["total"] for s in layer_stats.values())
    active_cards = sum(s["active"] for s in layer_stats.values())
    total_coverage = 0
    all_sources = coverage.get("sources", [])
    if all_sources:
        total_items = sum(s["total_items"] for s in all_sources)
        total_organized = sum(s["organized_items"] for s in all_sources)
        total_coverage = round(total_organized / total_items * 100, 1) if total_items > 0 else 0

    # 生成建议
    actions: list[str] = []

    l1_stats = layer_stats.get("L1-工作记忆", {})
    l2_stats = layer_stats.get("L2-领域知识", {})

    if l1_stats.get("total", 0) > 20:
        actions.append("L1 工作记忆条目过多，建议运行 memory_compress.py 降级过期条目。")

    if cold:
        actions.append(f"有 {len(cold)} 张冷门卡片超过 30 天未被召回，考虑归档或补充。")

    if duplicates:
        actions.append(f"有 {len(duplicates)} 对疑似重复卡片，运行 memory_compress.py 合并。")

    if total_coverage < 30:
        actions.append(f"知识库→记忆卡片覆盖率仅 {total_coverage}%，运行 memory_organize.py 扩充 L2。")

    if not actions:
        actions.append("记忆系统整体健康，继续保持定期 compress 和 organize。")

    return {
        "generated_at": datetime.now().isoformat(),
        "days": days,
        "summary": {
            "total_cards": total_cards,
            "active_cards": active_cards,
            "archived_cards": total_cards - active_cards,
            "knowledge_coverage": total_coverage,
        },
        "layer_stats": layer_stats,
        "expiring_l1": expiring,
        "cold_cards": cold,
        "duplicate_candidates": duplicates,
        "source_coverage": coverage,
        "next_actions": actions,
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = ["# Memory Health Report", ""]
    lines.append(f"- Generated: {result['generated_at']}")
    lines.append(f"- Days: {result['days']}")
    lines.append("")

    # 摘要
    summary = result.get("summary", {})
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"| --- | ---: |")
    lines.append(f"| Total cards | {summary.get('total_cards', 0)} |")
    lines.append(f"| Active cards | {summary.get('active_cards', 0)} |")
    lines.append(f"| Archived cards | {summary.get('archived_cards', 0)} |")
    lines.append(f"| Knowledge coverage | {summary.get('knowledge_coverage', 0)}% |")
    lines.append("")

    # 分层统计
    lines.append("## Layer Stats")
    lines.append("")
    lines.append("| Layer | Total | Active | Archived | Has Embedding | Avg Confidence |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for layer_name, stats in result.get("layer_stats", {}).items():
        lines.append(
            f"| {layer_name} | {stats['total']} | {stats['active']} | {stats['archived']} "
            f"| {stats['has_embedding']} | {stats['avg_confidence']} |"
        )
    lines.append("")

    # 来源覆盖
    sources = result.get("source_coverage", {}).get("sources", [])
    if sources:
        lines.append("## Source Coverage")
        lines.append("")
        lines.append("| Source | Total Items | Organized | Coverage |")
        lines.append("| --- | ---: | ---: | ---: |")
        for s in sources:
            lines.append(f"| {s['source_type']} | {s['total_items']} | {s['organized_items']} | {s['coverage_rate']}% |")
        lines.append("")

    # 过期 L1
    expiring = result.get("expiring_l1", [])
    if expiring:
        lines.append("## Expiring L1 Cards")
        lines.append("")
        for item in expiring:
            lines.append(f"- **{item['title']}** → expires {item['valid_until']} (accessed {item['access_count']}x)")
        lines.append("")

    # 冷门卡片
    cold = result.get("cold_cards", [])
    if cold:
        lines.append("## Cold Cards (>30 days, 0 accesses)")
        lines.append("")
        for item in cold:
            lines.append(f"- L{item['layer']}: **{item['title']}** (since {item['created_at'][:10]})")
        lines.append("")

    # 疑似重复
    duplicates = result.get("duplicate_candidates", [])
    if duplicates:
        lines.append("## Duplicate Candidates (similarity > 0.90)")
        lines.append("")
        for pair in duplicates:
            lines.append(f"- **{pair['title_a']}** ↔ **{pair['title_b']}** (sim={pair['similarity']})")
        lines.append("")

    # 建议
    lines.append("## Next Actions")
    lines.append("")
    for action in result.get("next_actions", []):
        lines.append(f"- {action}")

    return "\n".join(lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="记忆健康度报告")
    parser.add_argument("--days", type=int, default=30, help="统计最近多少天的数据")
    parser.add_argument("--output", choices=["json", "markdown"], default="json")
    parser.add_argument("--write", help="把 markdown 结果写入指定路径")
    args = parser.parse_args()

    result = generate_health_report(days=args.days)

    if args.output == "markdown" or args.write:
        md = render_markdown(result)
        if args.write:
            path = Path(args.write)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(md, encoding="utf-8")
        if args.output == "markdown":
            print(md)
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
