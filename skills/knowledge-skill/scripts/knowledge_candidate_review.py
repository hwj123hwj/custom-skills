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
面向 deck / showcase 的知识候选体检脚本。
在 export 结果之上增加轻量评分、理由和筛选，帮助判断知识池质量。
"""

import argparse
import json
from typing import Any

from knowledge_export import export_candidates
from knowledge_to_deck_brief import (
    CLICKBAIT_PATTERNS,
    METHOD_PATTERNS,
    extract_query_terms,
    infer_slide_type,
    normalize_text,
    score_item,
)


def build_reasons(item: dict[str, Any], query_terms: list[str]) -> list[str]:
    reasons: list[str] = []
    title = normalize_text(item.get("title") or "").lower()
    summary = normalize_text(item.get("summary") or "").lower()
    ai_summary = normalize_text(item.get("ai_summary") or "").lower()
    content = normalize_text(item.get("content") or "").lower()
    metadata = item.get("metadata") or {}
    source_type = str(item.get("source_type") or "unknown")
    haystack = f"{title}\n{summary}\n{ai_summary}\n{content}"

    if ai_summary:
        reasons.append("有 AI 摘要")
    else:
        reasons.append("缺少 AI 摘要")

    if len(content) >= 180:
        reasons.append("正文长度较充足")
    elif len(content) >= 80:
        reasons.append("正文长度一般")
    else:
        reasons.append("正文偏短")

    if metadata:
        reasons.append("带 metadata")

    matched_terms = [term for term in query_terms if term in haystack]
    if matched_terms:
        reasons.append(f"命中主题词: {', '.join(matched_terms[:4])}")

    method_hits = [pattern for pattern in METHOD_PATTERNS if pattern in haystack]
    if method_hits:
        reasons.append(f"方法论信号: {', '.join(method_hits[:3])}")

    if any(pattern in title for pattern in CLICKBAIT_PATTERNS):
        reasons.append("标题疑似噪音/标题党")

    slide_type = infer_slide_type(title, f"{ai_summary}\n{summary}\n{content}")
    reasons.append(f"推荐版式: {slide_type}")
    reasons.append(f"来源: {source_type}")

    return reasons


def review_candidates(
    query: str,
    mode: str = "hybrid",
    limit: int = 10,
    source_type: str | None = None,
    content_chars: int = 1000,
    min_score: int | None = None,
    require_ai_summary: bool = False,
) -> dict[str, Any]:
    exported = export_candidates(
        query=query,
        mode=mode,
        limit=limit,
        source_type=source_type,
        content_chars=content_chars,
    )
    query_terms = extract_query_terms(query)

    reviewed: list[dict[str, Any]] = []
    for item in exported.get("results", []):
        deck_score = score_item(item, query_terms)
        if min_score is not None and deck_score < min_score:
            continue
        if require_ai_summary and not normalize_text(item.get("ai_summary") or ""):
            continue

        reviewed.append(
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "source_type": item.get("source_type"),
                "source_url": item.get("source_url"),
                "ai_summary": item.get("ai_summary"),
                "summary": item.get("summary"),
                "deck_score": deck_score,
                "suggested_slide_type": infer_slide_type(
                    item.get("title") or "",
                    f"{item.get('ai_summary') or ''}\n{item.get('summary') or ''}\n{item.get('content') or ''}",
                ),
                "reasons": build_reasons(item, query_terms),
            }
        )

    reviewed.sort(
        key=lambda item: (
            item["deck_score"],
            bool(item.get("ai_summary")),
            item.get("title") or "",
        ),
        reverse=True,
    )

    return {
        "query": query,
        "mode": mode,
        "total_exported": exported.get("total", 0),
        "total_reviewed": len(reviewed),
        "results": reviewed,
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = ["# Candidate Review", ""]
    lines.append(f"- Query: {result['query']}")
    lines.append(f"- Mode: {result['mode']}")
    lines.append(f"- Exported: {result['total_exported']}")
    lines.append(f"- Reviewed: {result['total_reviewed']}")
    lines.append("")

    for idx, item in enumerate(result["results"], start=1):
        lines.append(f"## Candidate {idx}")
        lines.append(f"- Title: {item['title']}")
        lines.append(f"- Deck score: {item['deck_score']}")
        lines.append(f"- Source type: {item['source_type']}")
        lines.append(f"- Suggested slide type: {item['suggested_slide_type']}")
        if item.get("ai_summary"):
            lines.append(f"- AI summary: {item['ai_summary']}")
        if item.get("source_url"):
            lines.append(f"- Source URL: {item['source_url']}")
        lines.append("- Reasons:")
        for reason in item["reasons"]:
            lines.append(f"  - {reason}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="审阅知识候选的 deck 适配度")
    parser.add_argument("--query", required=True, help="搜索主题")
    parser.add_argument("--mode", choices=["keyword", "vector", "hybrid"], default="hybrid")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--source-type")
    parser.add_argument("--content-chars", type=int, default=1000)
    parser.add_argument("--min-score", type=int, help="最小 deck score")
    parser.add_argument("--require-ai-summary", action="store_true", help="仅保留有 AI 摘要的条目")
    parser.add_argument("--output", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    result = review_candidates(
        query=args.query,
        mode=args.mode,
        limit=args.limit,
        source_type=args.source_type,
        content_chars=args.content_chars,
        min_score=args.min_score,
        require_ai_summary=args.require_ai_summary,
    )

    if args.output == "markdown":
        print(render_markdown(result))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
