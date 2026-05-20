#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "psycopg2-binary",
#     "python-dotenv",
# ]
# ///
"""
概念时间线视图
按 valid_from 排列，展示某个概念的时间演化路径。
输出格式：[2024-03] 观点A → [2024-06] 修正为观点B → [2024-09] 观点B被验证

用法:
  uv run scripts/memory_timeline.py --query "Agent"
  uv run scripts/memory_timeline.py --query "知识库" --limit 20 --output markdown
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

DB_CONFIG = {
    "host": os.getenv("DB_HOST", ""),
    "port": int(os.getenv("DB_PORT", 5433)),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "dbname": os.getenv("DB_NAME", ""),
}


def fetch_timeline(query: str, limit: int = 20, layer: int | None = None) -> list[dict[str, Any]]:
    """按时间顺序查询记忆卡片"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        conditions = ["confidence > 0"]
        params: list[Any] = []

        if layer is not None:
            conditions.append("layer = %s")
            params.append(layer)

        # 关键词搜索：匹配 title、summary 或 keywords
        words = [w.strip() for w in query.split() if len(w.strip()) >= 2]
        if not words:
            words = [query]

        word_conditions = []
        for word in words:
            word_conditions.append("(title ILIKE %s OR summary ILIKE %s)")
            params.extend([f"%{word}%", f"%{word}%"])
        conditions.append(f"({' OR '.join(word_conditions)})")

        params.append(limit)

        cur.execute(
            f"""
            SELECT id, layer, title, summary, keywords, context_tags,
                   valid_from, valid_until, confidence, access_count, created_at
            FROM memory_cards
            WHERE {' AND '.join(conditions)}
            ORDER BY valid_from ASC, created_at ASC
            LIMIT %s
            """,
            params,
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def build_timeline_events(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """将卡片列表转化为时间线事件"""
    events = []
    for card in cards:
        valid_from = card.get("valid_from")
        month_label = valid_from.strftime("%Y-%m") if valid_from else "unknown"

        # 从 summary 提取核心结论（summary 格式: "结论 | 前提: xxx | 时效: xxx"）
        summary_text = card.get("summary", "")
        conclusion = summary_text.split(" | ")[0] if " | " in summary_text else summary_text

        events.append({
            "card_id": str(card["id"]),
            "date": month_label,
            "title": card.get("title", ""),
            "conclusion": conclusion[:100],
            "keywords": [str(k) for k in (card.get("keywords") or [])],
            "layer": card.get("layer"),
            "confidence": card.get("confidence", 0),
            "access_count": card.get("access_count", 0),
        })

    return events


def detect_evolution(events: list[dict[str, Any]]) -> list[str]:
    """检测概念演化路径（简化版：按时间排列结论）"""
    if not events:
        return []

    path = []
    prev_conclusion = None

    for event in events:
        conclusion = event["conclusion"]
        arrow = " → " if path else ""
        date = event["date"]
        title = event["title"][:30]

        if prev_conclusion and _is_revision(prev_conclusion, conclusion):
            path.append(f"{arrow}[{date}] 修正: {conclusion[:60]}")
        elif prev_conclusion and _is_validation(prev_conclusion, conclusion):
            path.append(f"{arrow}[{date}] 验证: {conclusion[:60]}")
        else:
            path.append(f"{arrow}[{date}] {title}: {conclusion[:60]}")

        prev_conclusion = conclusion

    return path


def _is_revision(old: str, new: str) -> bool:
    """简单判断是否是修正（新结论和旧结论有显著差异）"""
    revision_keywords = ["修正", "更新", "改为", "调整", "不再", "纠正"]
    new_lower = new.lower()
    return any(kw in new_lower for kw in revision_keywords)


def _is_validation(old: str, new: str) -> bool:
    """简单判断是否是验证"""
    validation_keywords = ["验证", "确认", "证实", "证明", "实测"]
    new_lower = new.lower()
    return any(kw in new_lower for kw in validation_keywords)


def timeline(query: str, limit: int = 20, layer: int | None = None) -> dict[str, Any]:
    """主函数：构建概念时间线"""
    cards = fetch_timeline(query=query, limit=limit, layer=layer)
    events = build_timeline_events(cards)
    evolution = detect_evolution(events)

    return {
        "query": query,
        "total_events": len(events),
        "events": events,
        "evolution_path": evolution,
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = ["# Memory Timeline", ""]
    lines.append(f"- Query: {result['query']}")
    lines.append(f"- Events: {result['total_events']}")
    lines.append("")

    # 演化路径
    if result.get("evolution_path"):
        lines.append("## Evolution Path")
        lines.append("")
        full_path = "".join(result["evolution_path"])
        lines.append(full_path)
        lines.append("")

    # 事件详情
    lines.append("## Events")
    lines.append("")
    for idx, event in enumerate(result.get("events", []), 1):
        layer_label = {1: "L1", 2: "L2", 3: "L3"}.get(event.get("layer"), "?")
        lines.append(f"### {idx}. [{event['date']}] {event['title']}")
        lines.append(f"- Layer: {layer_label}")
        lines.append(f"- Conclusion: {event['conclusion']}")
        if event.get("keywords"):
            lines.append(f"- Keywords: {', '.join(event['keywords'])}")
        lines.append(f"- Confidence: {event['confidence']}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="概念时间线视图：展示某概念的时间演化路径")
    parser.add_argument("--query", required=True, help="搜索概念/关键词")
    parser.add_argument("--limit", type=int, default=20, help="最多返回多少个事件")
    parser.add_argument("--layer", type=int, choices=[1, 2, 3], help="只看某个层级")
    parser.add_argument("--output", choices=["json", "markdown"], default="json")
    args = parser.parse_args()

    result = timeline(query=args.query, limit=args.limit, layer=args.layer)

    if args.output == "markdown":
        print(render_markdown(result))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
