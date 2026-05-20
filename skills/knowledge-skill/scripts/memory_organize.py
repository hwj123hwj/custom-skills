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
记忆整理器
从 knowledge_items 中筛选高质量条目，生成 L2 领域知识卡片。
核心能力：结构化摘要生成、概念标签提取、去重合并。

用法:
  uv run scripts/memory_organize.py --limit 10
  uv run scripts/memory_organize.py --source-type bilibili --limit 5
  uv run scripts/memory_organize.py --dry-run
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import psycopg2
import psycopg2.extras
import requests
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

SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
LONGCAT_API_KEY = os.getenv("LONGCAT_API_KEY", "") or os.getenv("LONGMAO_API_KEY", "")
LONGCAT_BASE_URL = os.getenv("LONGCAT_BASE_URL", "") or os.getenv("LONGMAO_BASE_URL", "https://api.longcat.chat/openai")
AI_SUMMARY_MODEL = os.getenv("AI_SUMMARY_MODEL", "LongCat-Flash-Lite")

# L3 → L2 晋升阈值（优先从 .tune-params.env 读取，否则用默认值）
MIN_CONTENT_LENGTH = int(os.getenv("MEMORY_ORGANIZE_MIN_CONTENT", "180"))           # 正文最短长度
MIN_AI_SUMMARY_LENGTH = 10                                                              # AI 摘要最短长度
DEDUP_SIMILARITY_THRESHOLD = float(os.getenv("MEMORY_DEDUP_THRESHOLD", "0.95"))       # 去重相似度阈值


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


def generate_structured_summary(title: str, content: str, ai_summary: str) -> dict[str, str]:
    """用 LLM 生成结构化摘要（结论 + 前提 + 时效）"""
    text = content[:2000] if len(content) > 2000 else content

    prompt = f"""请将以下知识条目整理为结构化摘要，严格按 JSON 格式输出。

标题：{title}
AI 摘要：{ai_summary}
内容：{text}

输出 JSON 格式：
{{
  "conclusion": "核心结论（一句话，不超过80字）",
  "premise": "前提条件或适用场景（一句话）",
  "validity": "时效性判断（如：长期有效 / 近期有效 / 已过时）",
  "keywords": ["关键词1", "关键词2", "关键词3"]
}}

只输出 JSON，不要其他文字。"""

    try:
        response = requests.post(
            f"{LONGCAT_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {LONGCAT_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": AI_SUMMARY_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
                "temperature": 0.2,
            },
            timeout=30,
        )
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"].strip()

        # 提取 JSON（兼容 markdown 包裹）
        json_match = re.search(r'\{[\s\S]+\}', raw)
        if json_match:
            parsed = json.loads(json_match.group())
            return {
                "conclusion": parsed.get("conclusion", ai_summary)[:200],
                "premise": parsed.get("premise", "")[:200],
                "validity": parsed.get("validity", "长期有效"),
                "keywords": parsed.get("keywords", [])[:5],
            }
    except Exception as e:
        print(f"Warning: structured summary failed ({e}), using fallback", file=sys.stderr)

    # Fallback: 直接用 ai_summary 作为结论
    return {
        "conclusion": ai_summary[:200] if ai_summary else title[:200],
        "premise": "",
        "validity": "长期有效",
        "keywords": extract_keywords_fallback(title, content),
    }


def extract_keywords_fallback(title: str, content: str) -> list[str]:
    """Fallback 关键词提取：从标题和内容中提取高频中文词组"""
    text = f"{title} {content[:500]}"
    # 简单提取：2-4字中文词组
    patterns = re.findall(r'[一-鿿]{2,4}', text)
    # 去重并取前 5 个高频词
    from collections import Counter
    counter = Counter(patterns)
    return [word for word, _ in counter.most_common(5)]


def fetch_candidates(
    limit: int = 10,
    source_type: str | None = None,
    min_content_length: int = MIN_CONTENT_LENGTH,
) -> list[dict[str, Any]]:
    """从 knowledge_items 中筛选高质量条目"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        clauses = [
            "ki.status = 'active'",
            "ki.ai_summary IS NOT NULL",
            f"length(ki.ai_summary) >= {MIN_AI_SUMMARY_LENGTH}",
            f"length(ki.content) >= {min_content_length}",
            "ki.embedding IS NOT NULL",
            # 排除已整理过的条目（ki.id 是 integer，mc.source_item_ids 是 text[]）
            "NOT EXISTS (SELECT 1 FROM memory_cards mc WHERE ki.id::text = ANY(mc.source_item_ids))",
        ]
        params: list[Any] = []

        if source_type:
            clauses.append("ki.source_type = %s")
            params.append(source_type)

        params.append(limit)

        cur.execute(
            f"""
            SELECT
                ki.id, ki.source_type, ki.source_id, ki.source_url,
                ki.title, ki.content, ki.ai_summary, ki.summary,
                ki.metadata, ki.created_at
            FROM knowledge_items ki
            WHERE {' AND '.join(clauses)}
            ORDER BY ki.created_at DESC
            LIMIT %s
            """,
            params,
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def check_duplicate(embedding: list[float], threshold: float = DEDUP_SIMILARITY_THRESHOLD) -> str | None:
    """检查是否已有相似的记忆卡片"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT id, title, 1 - (embedding <=> %s::vector) AS similarity
            FROM memory_cards
            WHERE embedding IS NOT NULL AND layer = 2
            ORDER BY embedding <=> %s::vector
            LIMIT 1
            """,
            [str(embedding), str(embedding)],
        )
        row = cur.fetchone()
        if row and row[2] >= threshold:
            return str(row[0])  # 返回已有 card id
        return None
    finally:
        cur.close()
        conn.close()


def insert_memory_card(
    title: str,
    summary: str,
    keywords: list[str],
    context_tags: list[str],
    source_item_ids: list[str],
    embedding: list[float] | None,
    confidence: float = 0.8,
) -> dict[str, Any]:
    """写入一张 L2 记忆卡片"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO memory_cards
            (layer, title, summary, keywords, context_tags,
             source_item_ids, embedding, confidence)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at
            """,
            (
                2,  # L2 领域知识
                title,
                summary,
                keywords,
                context_tags,
                source_item_ids,
                str(embedding) if embedding else None,
                confidence,
            ),
        )
        result = cur.fetchone()
        conn.commit()

        return {
            "id": str(result[0]),
            "created_at": result[1].isoformat(),
        }
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()


def organize_items(
    limit: int = 10,
    source_type: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """主流程：筛选 → 生成结构化摘要 → 去重 → 写入 memory_cards"""
    candidates = fetch_candidates(limit=limit, source_type=source_type)

    if not candidates:
        return {
            "success": True,
            "candidates_found": 0,
            "organized": 0,
            "skipped_duplicate": 0,
            "results": [],
            "message": "没有找到符合条件的新条目",
        }

    organized: list[dict[str, Any]] = []
    skipped = 0

    for item in candidates:
        item_id = str(item["id"])
        title = item["title"] or ""
        content = item["content"] or ""
        ai_summary = item["ai_summary"] or ""
        source_type_val = item.get("source_type", "")

        print(f"  Processing: {title[:50]}...", file=sys.stderr)

        # 1. 生成结构化摘要
        structured = generate_structured_summary(title, content, ai_summary)

        # 2. 拼接摘要文本
        summary_parts = [structured["conclusion"]]
        if structured["premise"]:
            summary_parts.append(f"前提: {structured['premise']}")
        if structured["validity"]:
            summary_parts.append(f"时效: {structured['validity']}")
        full_summary = " | ".join(summary_parts)

        # 3. 生成 embedding
        embedding_text = f"{title}\n{full_summary}"
        embedding = get_embedding(embedding_text)

        # 4. 去重检查
        if embedding:
            dup_id = check_duplicate(embedding)
            if dup_id:
                print(f"    → 跳过（与已有卡片 {dup_id[:8]}... 重复）", file=sys.stderr)
                skipped += 1
                organized.append({
                    "source_id": item_id,
                    "title": title,
                    "action": "skipped_duplicate",
                    "duplicate_of": dup_id,
                    "structured_summary": structured,
                })
                continue

        # 5. 写入（或 dry-run）
        if dry_run:
            organized.append({
                "source_id": item_id,
                "title": title,
                "action": "dry_run",
                "structured_summary": structured,
                "keywords": structured["keywords"],
                "summary_preview": full_summary[:100],
            })
        else:
            context_tags = []
            if source_type_val:
                context_tags.append(f"source:{source_type_val}")

            result = insert_memory_card(
                title=title,
                summary=full_summary,
                keywords=structured["keywords"],
                context_tags=context_tags,
                source_item_ids=[item_id],
                embedding=embedding,
                confidence=0.8,
            )

            if "error" in result:
                organized.append({
                    "source_id": item_id,
                    "title": title,
                    "action": "error",
                    "error": result["error"],
                })
            else:
                organized.append({
                    "source_id": item_id,
                    "card_id": result["id"],
                    "title": title,
                    "action": "created",
                    "keywords": structured["keywords"],
                    "summary_preview": full_summary[:100],
                    "created_at": result["created_at"],
                })

    return {
        "success": True,
        "dry_run": dry_run,
        "candidates_found": len(candidates),
        "organized": sum(1 for r in organized if r["action"] == "created" or r["action"] == "dry_run"),
        "skipped_duplicate": skipped,
        "results": organized,
    }


def main():
    parser = argparse.ArgumentParser(description="记忆整理器：从 knowledge_items 提取 L2 领域知识卡片")
    parser.add_argument("--limit", type=int, default=10, help="最多处理多少条")
    parser.add_argument("--source-type", help="只处理某个来源类型")
    parser.add_argument("--dry-run", action="store_true", help="只预览，不写入数据库")
    parser.add_argument("--min-content-length", type=int, default=MIN_CONTENT_LENGTH,
                        help="正文最短长度阈值")
    args = parser.parse_args()

    result = organize_items(
        limit=args.limit,
        source_type=args.source_type,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
