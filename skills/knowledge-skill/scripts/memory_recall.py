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
分层记忆检索
实现 L1(工作记忆) → L2(领域知识) → L3(原始存档) 逐层召回。

用法:
  uv run scripts/memory_recall.py --query "Agent 基础设施"
  uv run scripts/memory_recall.py --query "知识库" --context-tags "source:bilibili"
  uv run scripts/memory_recall.py --query "RAG" --limit 5 --mode hybrid
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import psycopg2
import psycopg2.extras
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", ""),
    "port": int(os.getenv("DB_PORT", 5433)),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "dbname": os.getenv("DB_NAME", ""),
}

SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")


def get_embedding(text: str) -> list[float] | None:
    """调用 SiliconFlow API 生成 embedding"""
    if not SILICONFLOW_API_KEY:
        return None
    try:
        response = requests.post(
            "https://api.siliconflow.cn/v1/embeddings",
            headers={
                "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": EMBEDDING_MODEL,
                "input": text[:8000],
                "encoding_format": "float",
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]
    except Exception as e:
        print(f"Error generating embedding: {e}", file=sys.stderr)
        return None


def update_access_stats(card_ids: list[str]) -> None:
    """更新命中卡片的访问计数和最后访问时间"""
    if not card_ids:
        return
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE memory_cards
            SET access_count = access_count + 1,
                last_accessed = NOW(),
                updated_at = NOW()
            WHERE id = ANY(%s::uuid[])
            """,
            [card_ids],
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()


def recall_l1_keyword(query: str, context_tags: list[str] | None, limit: int) -> list[dict[str, Any]]:
    """L1 工作记忆 — 关键词 + context_tags 精确匹配"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        words = [w.strip() for w in query.split() if len(w.strip()) >= 2]
        if not words:
            words = [query]

        conditions = ["layer = 1", "valid_until IS NULL OR valid_until > NOW()"]
        params: list[Any] = []

        # context_tags 精确匹配（如果提供了）
        if context_tags:
            conditions.append("context_tags @> %s")
            params.append(context_tags)

        # 关键词搜索
        word_conditions = []
        for word in words:
            word_conditions.append("(title ILIKE %s OR summary ILIKE %s)")
            params.extend([f"%{word}%", f"%{word}%"])
        conditions.append(f"({ ' OR '.join(word_conditions) })")

        params.append(limit)

        cur.execute(
            f"""
            SELECT id, layer, title, summary, keywords, context_tags,
                   valid_from, valid_until, source_item_ids, confidence,
                   access_count, created_at
            FROM memory_cards
            WHERE {' AND '.join(conditions)}
            ORDER BY
                CASE WHEN valid_until IS NOT NULL THEN 0 ELSE 1 END,
                access_count DESC,
                created_at DESC
            LIMIT %s
            """,
            params,
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def recall_l2_vector(query_embedding: list[float], limit: int) -> list[dict[str, Any]]:
    """L2 领域知识 — 向量语义搜索"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(
            """
            SELECT id, layer, title, summary, keywords, context_tags,
                   valid_from, valid_until, source_item_ids, confidence,
                   1 - (embedding <=> %s::vector) AS similarity,
                   access_count, created_at
            FROM memory_cards
            WHERE layer = 2 AND embedding IS NOT NULL
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            [str(query_embedding), str(query_embedding), limit],
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def recall_l2_keyword(query: str, limit: int) -> list[dict[str, Any]]:
    """L2 领域知识 — 关键词搜索"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        words = [w.strip() for w in query.split() if len(w.strip()) >= 2]
        if not words:
            words = [query]

        word_conditions = []
        params: list[Any] = []
        for word in words:
            word_conditions.append("(title ILIKE %s OR summary ILIKE %s)")
            params.extend([f"%{word}%", f"%{word}%"])

        params.append(limit)

        cur.execute(
            f"""
            SELECT id, layer, title, summary, keywords, context_tags,
                   valid_from, valid_until, source_item_ids, confidence,
                   access_count, created_at
            FROM memory_cards
            WHERE layer = 2 AND ({' OR '.join(word_conditions)})
            ORDER BY access_count DESC, created_at DESC
            LIMIT %s
            """,
            params,
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def recall_l3(query_embedding: list[float], limit: int) -> list[dict[str, Any]]:
    """L3 原始存档 — 回退到 knowledge_items"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(
            """
            SELECT id, source_type, source_id, source_url, title,
                   ai_summary, summary, created_at,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM knowledge_items
            WHERE embedding IS NOT NULL AND status = 'active'
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            [str(query_embedding), str(query_embedding), limit],
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def recall_l3_keyword(query: str, limit: int) -> list[dict[str, Any]]:
    """L3 原始存档 — 关键词回退"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        words = [w.strip() for w in query.split() if len(w.strip()) >= 2]
        if not words:
            words = [query]

        word_conditions = []
        params: list[Any] = []
        for word in words:
            word_conditions.append("(title ILIKE %s OR content ILIKE %s)")
            params.extend([f"%{word}%", f"%{word}%"])

        params.append(limit)

        cur.execute(
            f"""
            SELECT id, source_type, source_id, source_url, title,
                   ai_summary, summary, created_at
            FROM knowledge_items
            WHERE ({' OR '.join(word_conditions)}) AND status = 'active'
            ORDER BY created_at DESC
            LIMIT %s
            """,
            params,
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def recall(
    query: str,
    mode: str = "hybrid",
    limit: int = 10,
    context_tags: list[str] | None = None,
) -> dict[str, Any]:
    """
    分层检索主函数
    L1 → L2 → L3 逐层召回，每层命中后更新 access_count
    """
    results: list[dict[str, Any]] = []
    hit_card_ids: list[str] = []
    layer_stats = {"l1": 0, "l2": 0, "l3": 0}

    # ── L1 工作记忆 ──
    l1_results = recall_l1_keyword(query, context_tags=context_tags, limit=min(limit, 5))
    for r in l1_results:
        r["layer"] = 1
        r["source"] = "L1-工作记忆"
        results.append(r)
        hit_card_ids.append(str(r["id"]))
    layer_stats["l1"] = len(l1_results)

    remaining = limit - len(results)

    # ── L2 领域知识 ──
    if remaining > 0:
        if mode in ("vector", "hybrid"):
            query_embedding = get_embedding(query)
            if query_embedding:
                l2_vector = recall_l2_vector(query_embedding, limit=remaining)
                seen_ids = {r["id"] for r in results}
                for r in l2_vector:
                    if r["id"] not in seen_ids:
                        r["layer"] = 2
                        r["source"] = "L2-领域知识"
                        r["search_type"] = "vector"
                        results.append(r)
                        hit_card_ids.append(str(r["id"]))
                        seen_ids.add(r["id"])
                layer_stats["l2"] = len([r for r in results if r.get("layer") == 2])

        if mode in ("keyword", "hybrid"):
            l2_keyword = recall_l2_keyword(query, limit=max(remaining, 5))
            seen_ids = {r["id"] for r in results}
            for r in l2_keyword:
                if r["id"] not in seen_ids:
                    r["layer"] = 2
                    r["source"] = "L2-领域知识"
                    r["search_type"] = "keyword"
                    results.append(r)
                    hit_card_ids.append(str(r["id"]))
                    seen_ids.add(r["id"])
            layer_stats["l2"] = len([r for r in results if r.get("layer") == 2])

    remaining = limit - len(results)

    # ── L3 原始存档（回退） ──
    if remaining > 0:
        if mode in ("vector", "hybrid"):
            if query_embedding if mode == "hybrid" else get_embedding(query):
                emb = query_embedding if mode == "hybrid" else get_embedding(query)
                if emb:
                    l3_vector = recall_l3(emb, limit=remaining)
                    for r in l3_vector:
                        r["layer"] = 3
                        r["source"] = "L3-原始存档"
                        r["search_type"] = "vector"
                        results.append(r)
                    layer_stats["l3"] = len([r for r in results if r.get("layer") == 3])

        if mode in ("keyword", "hybrid"):
            l3_keyword = recall_l3_keyword(query, limit=max(remaining, 5))
            seen_l3_ids = {r["id"] for r in results if r.get("layer") == 3}
            for r in l3_keyword:
                if r["id"] not in seen_l3_ids:
                    r["layer"] = 3
                    r["source"] = "L3-原始存档"
                    r["search_type"] = "keyword"
                    results.append(r)
                    seen_l3_ids.add(r["id"])
            layer_stats["l3"] = len([r for r in results if r.get("layer") == 3])

    # 截断到 limit
    results = results[:limit]

    # 更新 L1/L2 卡片的访问计数
    update_access_stats(hit_card_ids)

    return {
        "query": query,
        "mode": mode,
        "total": len(results),
        "layer_stats": layer_stats,
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description="分层记忆检索：L1 工作记忆 → L2 领域知识 → L3 原始存档")
    parser.add_argument("--query", required=True, help="搜索关键词")
    parser.add_argument("--mode", choices=["keyword", "vector", "hybrid"],
                        default="hybrid", help="搜索模式")
    parser.add_argument("--limit", type=int, default=10, help="返回数量")
    parser.add_argument("--context-tags", nargs="*", help="上下文标签（如 source:bilibili）")
    parser.add_argument("--output", choices=["json", "markdown"], default="json")
    args = parser.parse_args()

    result = recall(
        query=args.query,
        mode=args.mode,
        limit=args.limit,
        context_tags=args.context_tags,
    )

    if args.output == "markdown":
        print(render_markdown(result))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


def render_markdown(result: dict[str, Any]) -> str:
    lines = ["# Memory Recall", ""]
    lines.append(f"- Query: {result['query']}")
    lines.append(f"- Mode: {result['mode']}")
    lines.append(f"- Total: {result['total']}")
    stats = result.get("layer_stats", {})
    lines.append(f"- L1 hits: {stats.get('l1', 0)} | L2 hits: {stats.get('l2', 0)} | L3 hits: {stats.get('l3', 0)}")
    lines.append("")

    for idx, item in enumerate(result.get("results", []), 1):
        layer = item.get("layer", "?")
        source = item.get("source", "")
        title = item.get("title", "")
        summary = item.get("summary", "")
        keywords = item.get("keywords", [])
        sim = item.get("similarity")

        lines.append(f"## {idx}. [{source}] {title}")
        if sim is not None:
            lines.append(f"- Similarity: {sim:.3f}")
        if keywords:
            lines.append(f"- Keywords: {', '.join(str(k) for k in keywords)}")
        if summary:
            lines.append(f"- Summary: {summary[:150]}...")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


if __name__ == "__main__":
    main()
