#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "psycopg2-binary",
#     "python-dotenv",
# ]
# ///
"""
memory_cards 表迁移脚本
创建分层记忆表及索引，用于 Agent Memory 阶段 4 升级。
用法: uv run scripts/memory_migrate.py [--drop]
"""

import argparse
import json
import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", ""),
    "port": int(os.getenv("DB_PORT", 5433)),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "dbname": os.getenv("DB_NAME", ""),
}

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS memory_cards (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 分层
    layer         SMALLINT NOT NULL DEFAULT 2,
    --  1 = 工作记忆（当前任务，高时效，自动过期）
    --  2 = 领域知识（跨任务复用，长期有效）
    --  3 = 原始存档（由 knowledge_items 映射，不直接写入）

    -- 内容
    title         TEXT NOT NULL,
    summary       TEXT NOT NULL,
    keywords      TEXT[] DEFAULT '{}',
    context_tags  TEXT[] DEFAULT '{}',

    -- 时效
    valid_from    TIMESTAMP DEFAULT NOW(),
    valid_until   TIMESTAMP,

    -- 关联（knowledge_items.id 是 integer，用 TEXT 存储跨表引用）
    source_item_ids TEXT[] DEFAULT '{}',
    related_card_ids UUID[] DEFAULT '{}',

    -- 向量
    embedding     vector(1024),

    -- 元数据
    access_count  INT DEFAULT 0,
    last_accessed TIMESTAMP,
    confidence    REAL DEFAULT 0.8,
    created_at    TIMESTAMP DEFAULT NOW(),
    updated_at    TIMESTAMP DEFAULT NOW()
);
"""

CREATE_INDEXES_SQL = """
-- 按层索引
CREATE INDEX IF NOT EXISTS idx_memory_cards_layer ON memory_cards(layer);

-- 向量索引（ivfflat，需要已有数据才能训练，此处先创建占位）
CREATE INDEX IF NOT EXISTS idx_memory_cards_embedding
    ON memory_cards USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- 关键词 GIN 索引
CREATE INDEX IF NOT EXISTS idx_memory_cards_keywords
    ON memory_cards USING GIN(keywords);

-- context_tags GIN 索引（L1 精确匹配用）
CREATE INDEX IF NOT EXISTS idx_memory_cards_context_tags
    ON memory_cards USING GIN(context_tags);

-- 时效索引（压缩/降级查询用）
CREATE INDEX IF NOT EXISTS idx_memory_cards_valid_until
    ON memory_cards(valid_until) WHERE valid_until IS NOT NULL;

-- 访问计数索引（冷门归档查询用）
CREATE INDEX IF NOT EXISTS idx_memory_cards_access_count
    ON memory_cards(access_count, created_at);
"""

DROP_TABLE_SQL = """
DROP TABLE IF EXISTS memory_cards CASCADE;
"""


def run_migrate(drop: bool = False) -> dict:
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        if drop:
            print("Dropping existing memory_cards table...", file=sys.stderr)
            cur.execute(DROP_TABLE_SQL)

        print("Creating memory_cards table...", file=sys.stderr)
        cur.execute(CREATE_TABLE_SQL)

        print("Creating indexes...", file=sys.stderr)
        cur.execute(CREATE_INDEXES_SQL)

        # 验证表存在
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'memory_cards'
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()

        print(f"Table created with {len(columns)} columns.", file=sys.stderr)

        return {
            "success": True,
            "table": "memory_cards",
            "columns": [
                {"name": col[0], "type": col[1]} for col in columns
            ],
            "dropped_previous": drop,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
    finally:
        cur.close()
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="创建 memory_cards 分层记忆表")
    parser.add_argument("--drop", action="store_true", help="先删除已有表（危险操作，会丢失数据）")
    args = parser.parse_args()

    result = run_migrate(drop=args.drop)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
