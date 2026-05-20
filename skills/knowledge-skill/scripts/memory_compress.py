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
记忆压缩器
定时任务（cron），每天执行：
  1. 将过期的 L1 降级为 L2（提取长期有效部分）
  2. 将冷门的 L2 归档（标记 confidence = 0，不删除）
  3. 合并相似的 L2 卡片（cosine similarity > 0.95）

所有规则硬编码在 SQL 中，不依赖 LLM 判断。

用法:
  uv run scripts/memory_compress.py
  uv run scripts/memory_compress.py --dry-run
  uv run scripts/memory_compress.py --similarity-threshold 0.90
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")
load_dotenv(Path(__file__).parent.parent / ".tune-params.env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", ""),
    "port": int(os.getenv("DB_PORT", 5433)),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "dbname": os.getenv("DB_NAME", ""),
}

# 规则阈值（优先从 .tune-params.env 读取，否则用默认值）
L1_EXPIRE_DAYS = int(os.getenv("MEMORY_L1_EXPIRE_DAYS", "7"))           # L1 超过此天数且 access_count < 2 降级
L2_ARCHIVE_DAYS = int(os.getenv("MEMORY_L2_ARCHIVE_DAYS", "90"))         # L2 超过此天数且 access_count < 1 归档
DEFAULT_SIMILARITY = float(os.getenv("MEMORY_MERGE_SIMILARITY", "0.95")) # 去重合并阈值


def downgrade_expired_l1(dry_run: bool = False) -> dict[str, Any]:
    """将过期的 L1 降级为 L2"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # 查找过期的 L1 条目
        cur.execute(
            """
            SELECT id, title, summary, keywords, context_tags,
                   source_item_ids, access_count, created_at
            FROM memory_cards
            WHERE layer = 1
              AND (
                  valid_until < NOW()
                  OR (created_at < NOW() - INTERVAL '%s days' AND access_count < 2)
              )
            """,
            [L1_EXPIRE_DAYS],
        )
        expired = [dict(row) for row in cur.fetchall()]

        if not expired:
            return {"action": "downgrade_l1_to_l2", "count": 0, "message": "无过期 L1 条目"}

        if dry_run:
            return {
                "action": "downgrade_l1_to_l2",
                "count": len(expired),
                "dry_run": True,
                "items": [
                    {"id": str(item["id"]), "title": item["title"][:50], "access_count": item["access_count"]}
                    for item in expired
                ],
            }

        # 执行降级
        ids = [item["id"] for item in expired]
        cur.execute(
            """
            UPDATE memory_cards
            SET layer = 2,
                valid_until = NULL,
                confidence = LEAST(confidence, 0.7),
                updated_at = NOW()
            WHERE id = ANY(%s::uuid[])
            """,
            [ids],
        )
        conn.commit()

        return {
            "action": "downgrade_l1_to_l2",
            "count": len(ids),
            "items": [
                {"id": str(item["id"]), "title": item["title"][:50]}
                for item in expired
            ],
        }
    finally:
        cur.close()
        conn.close()


def archive_cold_l2(dry_run: bool = False) -> dict[str, Any]:
    """将冷门的 L2 归档（confidence → 0，不删除）"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cur.execute(
            """
            SELECT id, title, access_count, created_at
            FROM memory_cards
            WHERE layer = 2
              AND confidence > 0
              AND created_at < NOW() - INTERVAL '%s days'
              AND access_count < 1
            """,
            [L2_ARCHIVE_DAYS],
        )
        cold = [dict(row) for row in cur.fetchall()]

        if not cold:
            return {"action": "archive_cold_l2", "count": 0, "message": "无冷门 L2 条目"}

        if dry_run:
            return {
                "action": "archive_cold_l2",
                "count": len(cold),
                "dry_run": True,
                "items": [
                    {"id": str(item["id"]), "title": item["title"][:50], "age_days": (item["created_at"]).days if hasattr(item["created_at"], 'days') else "N/A"}
                    for item in cold
                ],
            }

        ids = [item["id"] for item in cold]
        cur.execute(
            """
            UPDATE memory_cards
            SET confidence = 0,
                updated_at = NOW()
            WHERE id = ANY(%s::uuid[])
            """,
            [ids],
        )
        conn.commit()

        return {
            "action": "archive_cold_l2",
            "count": len(ids),
            "items": [
                {"id": str(item["id"]), "title": item["title"][:50]}
                for item in cold
            ],
        }
    finally:
        cur.close()
        conn.close()


def merge_similar_l2(dry_run: bool = False, threshold: float = DEFAULT_SIMILARITY) -> dict[str, Any]:
    """合并相似的 L2 卡片（cosine similarity > threshold）"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # 找出所有有 embedding 的 L2 卡片
        cur.execute(
            """
            SELECT id, title, summary, keywords, context_tags,
                   source_item_ids, embedding
            FROM memory_cards
            WHERE layer = 2 AND embedding IS NOT NULL AND confidence > 0
            ORDER BY created_at ASC
            """,
        )
        cards = [dict(row) for row in cur.fetchall()]

        if len(cards) < 2:
            return {"action": "merge_similar_l2", "count": 0, "message": "L2 卡片不足 2 张，无需合并"}

        # 找相似对（用 SQL 交叉比对）
        cur.execute(
            """
            SELECT
                a.id AS id_a, a.title AS title_a,
                b.id AS id_b, b.title AS title_b,
                1 - (a.embedding <=> b.embedding) AS similarity
            FROM memory_cards a
            JOIN memory_cards b ON a.id < b.id
            WHERE a.layer = 2 AND b.layer = 2
              AND a.embedding IS NOT NULL AND b.embedding IS NOT NULL
              AND a.confidence > 0 AND b.confidence > 0
              AND 1 - (a.embedding <=> b.embedding) >= %s
            ORDER BY similarity DESC
            """,
            [threshold],
        )
        similar_pairs = [dict(row) for row in cur.fetchall()]

        if not similar_pairs:
            return {"action": "merge_similar_l2", "count": 0, "message": "无相似卡片需要合并"}

        if dry_run:
            return {
                "action": "merge_similar_l2",
                "count": len(similar_pairs),
                "dry_run": True,
                "threshold": threshold,
                "pairs": [
                    {
                        "id_a": str(pair["id_a"]),
                        "title_a": pair["title_a"][:40],
                        "id_b": str(pair["id_b"]),
                        "title_b": pair["title_b"][:40],
                        "similarity": round(pair["similarity"], 4),
                    }
                    for pair in similar_pairs
                ],
            }

        # 合并：保留较早的卡片，把较晚的 source_item_ids 合并进来
        merged = []
        for pair in similar_pairs:
            # 保留 a（较早），合并 b 的数据
            cur.execute(
                """
                UPDATE memory_cards a
                SET source_item_ids = a.source_item_ids || b.source_item_ids,
                    confidence = GREATEST(a.confidence, b.confidence),
                    updated_at = NOW()
                FROM memory_cards b
                WHERE a.id = %s AND b.id = %s
                """,
                [pair["id_a"], pair["id_b"]],
            )

            # 删除 b（被合并的卡片）
            cur.execute(
                "DELETE FROM memory_cards WHERE id = %s",
                [pair["id_b"]],
            )

            merged.append({
                "kept": str(pair["id_a"]),
                "kept_title": pair["title_a"][:40],
                "removed": str(pair["id_b"]),
                "removed_title": pair["title_b"][:40],
                "similarity": round(pair["similarity"], 4),
            })

        conn.commit()

        return {
            "action": "merge_similar_l2",
            "count": len(merged),
            "threshold": threshold,
            "pairs": merged,
        }
    finally:
        cur.close()
        conn.close()


def compress(dry_run: bool = False, similarity_threshold: float = DEFAULT_SIMILARITY) -> dict[str, Any]:
    """执行完整的记忆压缩流程"""
    results = []

    # Step 1: L1 → L2 降级
    print("Step 1: 降级过期 L1 → L2...", file=sys.stderr)
    downgrade = downgrade_expired_l1(dry_run=dry_run)
    results.append(downgrade)
    print(f"  → {downgrade['count']} 条降级", file=sys.stderr)

    # Step 2: L2 冷门归档
    print("Step 2: 归档冷门 L2...", file=sys.stderr)
    archive = archive_cold_l2(dry_run=dry_run)
    results.append(archive)
    print(f"  → {archive['count']} 条归档", file=sys.stderr)

    # Step 3: L2 相似合并
    print("Step 3: 合并相似 L2 卡片...", file=sys.stderr)
    merge = merge_similar_l2(dry_run=dry_run, threshold=similarity_threshold)
    results.append(merge)
    print(f"  → {merge['count']} 对合并", file=sys.stderr)

    return {
        "success": True,
        "dry_run": dry_run,
        "steps": results,
        "summary": {
            "downgraded": downgrade["count"],
            "archived": archive["count"],
            "merged": merge["count"],
        },
    }


def main():
    parser = argparse.ArgumentParser(description="记忆压缩器：L1 降级 + L2 归档 + 相似合并")
    parser.add_argument("--dry-run", action="store_true", help="只预览，不写入数据库")
    parser.add_argument("--similarity-threshold", type=float, default=DEFAULT_SIMILARITY,
                        help=f"合并相似度阈值，默认 {DEFAULT_SIMILARITY}")
    args = parser.parse_args()

    result = compress(
        dry_run=args.dry_run,
        similarity_threshold=args.similarity_threshold,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
