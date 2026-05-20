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
L1 工作记忆写入
Agent 在任务中产出的关键决策、中间结论写入 L1。
自动设置 valid_until = NOW() + 7 days，打上当前项目/任务的 context_tags。

用法:
  uv run scripts/memory_save_working.py \
    --title "决定使用 pgvector 而非 Milvus" \
    --summary "pgvector 轻量、与 PostgreSQL 原生集成，适合个人知识库规模" \
    --keywords "pgvector,选型,向量数据库"

  uv run scripts/memory_save_working.py \
    --title "API Key 配置问题" \
    --summary "LONGCAT_API_KEY 是正确的环境变量名，LONGMAO_API_KEY 是旧名" \
    --context-tags "project:knowledge-skill" "task:debug"
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
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

# L1 默认过期时间
DEFAULT_TTL_DAYS = 7


def get_embedding(text: str) -> list[float] | None:
    """调用 SiliconFlow API 生成 embedding"""
    if not SILICONFLOW_API_KEY:
        print("Warning: SILICONFLOW_API_KEY not set, skipping embedding", file=sys.stderr)
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


def save_working_memory(
    title: str,
    summary: str,
    keywords: list[str] | None = None,
    context_tags: list[str] | None = None,
    ttl_days: int = DEFAULT_TTL_DAYS,
    source_item_ids: list[str] | None = None,
) -> dict:
    """写入 L1 工作记忆卡片"""

    # 生成 embedding
    embedding_text = f"{title}\n{summary}"
    embedding = get_embedding(embedding_text)

    # 计算 valid_until
    valid_until = datetime.now() + timedelta(days=ttl_days)

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO memory_cards
            (layer, title, summary, keywords, context_tags,
             source_item_ids, embedding, valid_from, valid_until, confidence)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at
            """,
            (
                1,  # L1 工作记忆
                title,
                summary,
                keywords or [],
                context_tags or [],
                source_item_ids or [],
                str(embedding) if embedding else None,
                datetime.now(),  # valid_from
                valid_until,
                0.9,  # L1 默认高可信度（刚产出的知识）
            ),
        )
        result = cur.fetchone()
        conn.commit()

        return {
            "success": True,
            "id": str(result[0]),
            "layer": 1,
            "created_at": result[1].isoformat(),
            "valid_until": valid_until.isoformat(),
            "ttl_days": ttl_days,
            "has_embedding": embedding is not None,
        }
    except Exception as e:
        conn.rollback()
        return {
            "success": False,
            "error": str(e),
        }
    finally:
        cur.close()
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="写入 L1 工作记忆（Agent 任务中的关键决策和中间结论）")
    parser.add_argument("--title", required=True, help="记忆标题（如：决定使用 X 方案）")
    parser.add_argument("--summary", required=True, help="记忆内容/结论")
    parser.add_argument("--keywords", help="关键词，逗号分隔")
    parser.add_argument("--context-tags", nargs="*", help="上下文标签（如 project:xxx task:xxx）")
    parser.add_argument("--ttl-days", type=int, default=DEFAULT_TTL_DAYS,
                        help=f"有效期天数，默认 {DEFAULT_TTL_DAYS}")
    parser.add_argument("--source-item-ids", nargs="*", help="关联的 knowledge_items ID")
    args = parser.parse_args()

    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()] if args.keywords else []
    context_tags = args.context_tags or []
    source_item_ids = args.source_item_ids or []

    result = save_working_memory(
        title=args.title,
        summary=args.summary,
        keywords=keywords,
        context_tags=context_tags,
        ttl_days=args.ttl_days,
        source_item_ids=source_item_ids,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
