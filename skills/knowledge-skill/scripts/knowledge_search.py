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
知识搜索脚本
支持关键词搜索、向量语义搜索、混合搜索
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

# 加载环境变量
load_dotenv(Path(__file__).parent.parent / ".env")

# 配置
DB_CONFIG = {
    "host": os.getenv("DB_HOST", ""),
    "port": int(os.getenv("DB_PORT", 5433)),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "dbname": os.getenv("DB_NAME", ""),
}

SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")


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


def search_keyword(query: str, limit: int = 10, source_type: str = None) -> list[dict]:
    """关键词搜索（分词后逐词 OR 匹配）"""
    # 分词：按空格拆分，每词单独匹配
    words = [w.strip() for w in query.split() if len(w.strip()) >= 2]
    if not words:
        words = [query]

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # 每个词生成 OR 条件
        conditions = []
        params = []
        for word in words:
            conditions.append("(title ILIKE %s OR content ILIKE %s)")
            params.extend([f"%{word}%", f"%{word}%"])

        sql = f"""
            SELECT id, source_type, source_id, source_url, title, summary,
                   created_at, updated_at, status
            FROM knowledge_items
            WHERE ({" OR ".join(conditions)})
        """

        if source_type:
            sql += " AND source_type = %s"
            params.append(source_type)

        sql += " ORDER BY status='active' DESC, created_at DESC LIMIT %s"
        params.append(limit)

        cur.execute(sql, params)
        results = cur.fetchall()

        return [dict(r) for r in results]
    finally:
        cur.close()
        conn.close()


def search_vector(query: str, limit: int = 10, source_type: str = None) -> list[dict]:
    """向量语义搜索"""
    embedding = get_embedding(query)
    if not embedding:
        print("Error: Could not generate embedding for query", file=sys.stderr)
        return []

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        sql = """
            SELECT id, source_type, source_id, source_url, title, summary,
                   created_at, updated_at,
                   1 - (embedding <=> %s::vector) as similarity
            FROM knowledge_items
            WHERE embedding IS NOT NULL
        """
        params = [str(embedding)]

        if source_type:
            sql += " AND source_type = %s"
            params.append(source_type)

        sql += " ORDER BY embedding <=> %s::vector LIMIT %s"
        params.extend([str(embedding), limit])

        cur.execute(sql, params)
        results = cur.fetchall()

        return [dict(r) for r in results]
    finally:
        cur.close()
        conn.close()


def search_hybrid(query: str, limit: int = 10, source_type: str = None) -> list[dict]:
    """混合搜索：关键词 + 向量"""
    # 向量搜索
    vector_results = search_vector(query, limit=limit * 2, source_type=source_type)

    # 关键词搜索
    keyword_results = search_keyword(query, limit=limit * 2, source_type=source_type)

    # 合并结果（简单的去重和排序）
    seen_ids = set()
    combined = []

    # 优先向量搜索结果
    for r in vector_results:
        if r["id"] not in seen_ids:
            r["search_type"] = "vector"
            combined.append(r)
            seen_ids.add(r["id"])

    # 补充关键词搜索结果
    for r in keyword_results:
        if r["id"] not in seen_ids:
            r["search_type"] = "keyword"
            r["similarity"] = None
            combined.append(r)
            seen_ids.add(r["id"])

    # 按 similarity 排序（有 similarity 的排前面）
    combined.sort(key=lambda x: x.get("similarity") or 0, reverse=True)

    return combined[:limit]


def main():
    parser = argparse.ArgumentParser(description="搜索知识库")
    parser.add_argument("--query", required=True, help="搜索关键词")
    parser.add_argument("--mode", choices=["keyword", "vector", "hybrid"],
                       default="hybrid", help="搜索模式")
    parser.add_argument("--limit", type=int, default=10, help="返回数量")
    parser.add_argument("--source-type", help="筛选来源类型")

    args = parser.parse_args()

    # 搜索
    if args.mode == "keyword":
        results = search_keyword(args.query, args.limit, args.source_type)
    elif args.mode == "vector":
        results = search_vector(args.query, args.limit, args.source_type)
    else:
        results = search_hybrid(args.query, args.limit, args.source_type)

    # 格式化输出
    output = {
        "query": args.query,
        "mode": args.mode,
        "total": len(results),
        "results": results,
    }

    print(json.dumps(output, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()