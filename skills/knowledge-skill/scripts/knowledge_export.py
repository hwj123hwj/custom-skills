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
知识导出脚本 — 为 agent 提供结构化输出

与 knowledge_search.py 不同，这个脚本返回完整的决策信息：
- ai_summary（一句话总结）
- content 截断（前 1000 字，足够判断结论和价值）
- metadata（来源、作者等结构化信息）

用法：
    python knowledge_export.py --query "Agent Infrastructure" --limit 8
"""

import argparse
import json
import os
import sys
from pathlib import Path

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

CONTENT_TRUNCATE_LEN = 1000


def get_embedding(text: str) -> list[float]:
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


def export_for_agent(query: str, limit: int = 8, source_type: str = None) -> list[dict]:
    """
    混合搜索 + 返回 agent 决策所需的完整字段
    """
    embedding = get_embedding(query)

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # 向量搜索部分
        vector_ids = []
        if embedding:
            sql_vec = """
                SELECT id, 1 - (embedding <=> %s::vector) as similarity
                FROM knowledge_items
                WHERE embedding IS NOT NULL AND status = 'active'
            """
            params_vec = [str(embedding)]
            if source_type:
                sql_vec += " AND source_type = %s"
                params_vec.append(source_type)
            sql_vec += " ORDER BY embedding <=> %s::vector LIMIT %s"
            params_vec.extend([str(embedding), limit * 2])
            cur.execute(sql_vec, params_vec)
            vector_ids = [(r["id"], r["similarity"]) for r in cur.fetchall()]

        # 关键词搜索部分
        words = [w.strip() for w in query.split() if len(w.strip()) >= 2]
        if not words:
            words = [query]
        conditions = []
        params_kw = []
        for word in words:
            conditions.append("(title ILIKE %s OR content ILIKE %s OR ai_summary ILIKE %s)")
            params_kw.extend([f"%{word}%", f"%{word}%", f"%{word}%"])

        sql_kw = f"""
            SELECT id FROM knowledge_items
            WHERE ({" OR ".join(conditions)}) AND status = 'active'
        """
        if source_type:
            sql_kw += " AND source_type = %s"
            params_kw.append(source_type)
        sql_kw += " LIMIT %s"
        params_kw.append(limit * 2)
        cur.execute(sql_kw, params_kw)
        keyword_ids = [r["id"] for r in cur.fetchall()]

        # 合并去重，向量结果优先
        seen = set()
        ordered_ids = []
        id_similarity = {}
        for id_, sim in vector_ids:
            if id_ not in seen:
                ordered_ids.append(id_)
                id_similarity[id_] = sim
                seen.add(id_)
        for id_ in keyword_ids:
            if id_ not in seen:
                ordered_ids.append(id_)
                seen.add(id_)

        # 取前 limit 个，然后批量查完整字段
        target_ids = ordered_ids[:limit]
        if not target_ids:
            return []

        sql_full = """
            SELECT id, source_type, source_id, source_url, title,
                   summary, ai_summary, content, metadata,
                   created_at, updated_at
            FROM knowledge_items
            WHERE id = ANY(%s)
        """
        cur.execute(sql_full, [target_ids])
        rows = cur.fetchall()

        # 按 ordered_ids 的顺序排列
        row_map = {r["id"]: r for r in rows}
        results = []
        for id_ in target_ids:
            if id_ not in row_map:
                continue
            r = dict(row_map[id_])
            # 截断 content，避免输出过长
            if r.get("content") and len(r["content"]) > CONTENT_TRUNCATE_LEN:
                r["content_preview"] = r["content"][:CONTENT_TRUNCATE_LEN] + "..."
            else:
                r["content_preview"] = r.get("content", "")
            # 不输出完整 content 和 embedding
            r.pop("content", None)
            # 补上 similarity（如果有）
            if id_ in id_similarity:
                r["similarity"] = id_similarity[id_]
            results.append(r)

        return results
    finally:
        cur.close()
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="导出知识库内容（面向 agent 的结构化输出）")
    parser.add_argument("--query", required=True, help="搜索关键词")
    parser.add_argument("--limit", type=int, default=8, help="返回数量（默认 8）")
    parser.add_argument("--source-type", help="筛选来源类型")

    args = parser.parse_args()

    results = export_for_agent(args.query, args.limit, args.source_type)

    output = {
        "query": args.query,
        "total": len(results),
        "results": results,
    }

    print(json.dumps(output, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
