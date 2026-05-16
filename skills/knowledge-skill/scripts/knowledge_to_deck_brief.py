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
从知识库候选中生成 deck brief。
第一版走轻量启发式，不依赖额外数据库字段。
"""

import argparse
import json
import re
from typing import Any

from knowledge_export import export_candidates


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def split_sentences(text: str) -> list[str]:
    text = normalize_text(text)
    if not text:
        return []
    parts = re.split(r"[。！？!?；;]\s*|\.\s+", text)
    return [part.strip(" -\n\t") for part in parts if part.strip()]


def title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", (title or "").lower())


def infer_slide_type(title: str, text: str) -> str:
    combined = f"{title}\n{text}".lower()

    if any(keyword in combined for keyword in ["对比", "比较", "vs", "versus", "替代", "取舍", "trade-off"]):
        return "comparison"
    if any(keyword in combined for keyword in ["时间线", "timeline", "演进", "阶段", "历程"]):
        return "timeline"
    if any(keyword in combined for keyword in ["框架", "framework", "方法论", "工作流", "流程", "pipeline", "loop"]):
        return "framework"
    if any(keyword in combined for keyword in ["案例", "case", "实践", "复盘", "经验", "踩坑"]):
        return "case"
    return "statement"


def build_takeaway(item: dict[str, Any]) -> str:
    ai_summary = normalize_text(item.get("ai_summary") or "")
    if ai_summary:
        return ai_summary

    summary = normalize_text(item.get("summary") or "")
    if summary:
        return split_sentences(summary)[0] if split_sentences(summary) else summary

    content = normalize_text(item.get("content") or "")
    sentences = split_sentences(content)
    if sentences:
        return sentences[0]

    return item.get("title") or "Untitled insight"


def build_why_it_matters(item: dict[str, Any], query: str, audience: str | None) -> str:
    source_type = item.get("source_type") or "unknown"
    audience_clause = f"，对{audience}更值得关注" if audience else ""

    if source_type == "bilibili":
        return f"这条内容更可能包含具体案例、流程演示或经验细节，适合做展示卡片{audience_clause}。"
    if source_type == "wechat":
        return f"这条内容更可能包含完整论述和观点展开，适合提炼成主题洞察{audience_clause}。"
    if source_type == "xiaohongshu":
        return f"这条内容更偏经验贴或实操心得，适合用作案例型卡片{audience_clause}。"
    if source_type == "web":
        return f"这条内容与主题「{query}」相关，适合补充背景、结论或关键证据{audience_clause}。"

    return f"这条内容与主题「{query}」相关，且具备进一步压缩成展示卡片的潜力{audience_clause}。"


def build_evidence(item: dict[str, Any]) -> str:
    content = normalize_text(item.get("content") or "")
    sentences = split_sentences(content)
    if len(sentences) >= 2:
        return sentences[1][:180]
    if sentences:
        return sentences[0][:180]

    summary = normalize_text(item.get("summary") or "")
    if summary:
        return summary[:180]

    return "原始条目中缺少可直接引用的案例或证据，后续需要人工补充。"


def score_item(item: dict[str, Any], query_terms: list[str]) -> int:
    score = 0
    title = normalize_text(item.get("title") or "").lower()
    summary = normalize_text(item.get("summary") or "").lower()
    ai_summary = normalize_text(item.get("ai_summary") or "").lower()
    content = normalize_text(item.get("content") or "").lower()
    metadata = item.get("metadata") or {}

    if ai_summary:
        score += 3
    if len(content) >= 180:
        score += 2
    if metadata:
        score += 1
    if item.get("source_type") in {"bilibili", "wechat", "web"}:
        score += 1

    haystack = f"{title}\n{summary}\n{ai_summary}\n{content}"
    for term in query_terms:
        if term in haystack:
            score += 2
        if term in title:
            score += 1

    return score


def select_candidates(
    items: list[dict[str, Any]],
    query: str,
    cards: int,
) -> list[dict[str, Any]]:
    query_terms = [term.lower() for term in re.split(r"\s+", query) if len(term.strip()) >= 2]

    unique: dict[str, dict[str, Any]] = {}
    for item in items:
        key = title_key(item.get("title") or str(item.get("id")))
        existing = unique.get(key)
        if not existing:
            unique[key] = item
            continue
        if len(normalize_text(item.get("content") or "")) > len(normalize_text(existing.get("content") or "")):
            unique[key] = item

    ranked = sorted(
        unique.values(),
        key=lambda item: score_item(item, query_terms),
        reverse=True,
    )
    return ranked[:cards]


def build_cards(
    items: list[dict[str, Any]],
    query: str,
    audience: str | None,
) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for item in items:
        takeaway = build_takeaway(item)
        why_it_matters = build_why_it_matters(item, query, audience)
        evidence = build_evidence(item)
        slide_type = infer_slide_type(item.get("title") or "", f"{takeaway}\n{evidence}")

        cards.append(
            {
                "title": item.get("title") or "Untitled",
                "takeaway": takeaway,
                "why_it_matters": why_it_matters,
                "evidence_or_example": evidence,
                "suggested_slide_type": slide_type,
                "source_refs": [
                    {
                        "title": item.get("title"),
                        "url": item.get("source_url"),
                        "source_type": item.get("source_type"),
                    }
                ],
            }
        )
    return cards


def build_deck_brief(
    query: str,
    cards: list[dict[str, Any]],
    style: str,
    audience: str | None,
) -> dict[str, Any]:
    title = query.strip()
    slide_notes: list[dict[str, Any]] = [
        {
            "slide": 1,
            "role": "cover",
            "purpose": "建立主题和展示基调",
            "core_content": title,
            "suggested_layout": "cover",
        },
        {
            "slide": 2,
            "role": "framing",
            "purpose": "说明为什么这个主题值得关注",
            "core_content": f"围绕「{title}」提炼高价值知识精华，服务于{audience or '通用观众'}。",
            "suggested_layout": "statement",
        },
    ]

    for index, card in enumerate(cards, start=3):
        slide_notes.append(
            {
                "slide": index,
                "role": "knowledge-card",
                "purpose": "展示一条高价值知识卡片",
                "core_content": {
                    "title": card["title"],
                    "takeaway": card["takeaway"],
                    "why_it_matters": card["why_it_matters"],
                    "evidence_or_example": card["evidence_or_example"],
                },
                "suggested_layout": card["suggested_slide_type"],
            }
        )

    slide_notes.append(
        {
            "slide": len(slide_notes) + 1,
            "role": "closing",
            "purpose": "收束主题并给出总结",
            "core_content": f"这组卡片展示了「{title}」中最值得复用和展示的知识精华，可继续扩展成更完整的专题 deck。",
            "suggested_layout": "closing",
        }
    )

    return {
        "title": title,
        "style": style,
        "audience": audience or "通用观众",
        "card_count": len(cards),
        "structure": [
            "cover",
            "framing",
            "knowledge-cards",
            "closing",
        ],
        "slide_notes": slide_notes,
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Knowledge Cards")
    lines.append("")
    for idx, card in enumerate(result["knowledge_cards"], start=1):
        lines.append(f"## Card {idx}")
        lines.append(f"- Title: {card['title']}")
        lines.append(f"- Takeaway: {card['takeaway']}")
        lines.append(f"- Why it matters: {card['why_it_matters']}")
        lines.append(f"- Evidence or example: {card['evidence_or_example']}")
        lines.append(f"- Suggested slide type: {card['suggested_slide_type']}")
        lines.append("")

    lines.append("# Deck Brief")
    lines.append("")
    deck = result["deck_brief"]
    lines.append(f"- Theme: {deck['title']}")
    lines.append(f"- Style: {deck['style']}")
    lines.append(f"- Audience: {deck['audience']}")
    lines.append(f"- Card count: {deck['card_count']}")
    lines.append("")
    lines.append("## Slide Notes")
    lines.append("")
    for slide in deck["slide_notes"]:
        lines.append(f"### Slide {slide['slide']} · {slide['role']}")
        lines.append(f"- Purpose: {slide['purpose']}")
        lines.append(f"- Suggested layout: {slide['suggested_layout']}")
        core = slide["core_content"]
        if isinstance(core, dict):
            for key, value in core.items():
                lines.append(f"- {key}: {value}")
        else:
            lines.append(f"- Core content: {core}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def generate_deck_brief(
    query: str,
    mode: str = "hybrid",
    limit: int = 12,
    cards: int = 5,
    style: str = "swiss",
    audience: str | None = None,
    source_type: str | None = None,
    content_chars: int = 1000,
) -> dict[str, Any]:
    exported = export_candidates(
        query=query,
        mode=mode,
        limit=limit,
        source_type=source_type,
        content_chars=content_chars,
    )
    selected = select_candidates(exported.get("results", []), query=query, cards=cards)
    knowledge_cards = build_cards(selected, query=query, audience=audience)
    deck_brief = build_deck_brief(query=query, cards=knowledge_cards, style=style, audience=audience)

    return {
        "query": query,
        "mode": mode,
        "total_candidates": exported.get("total", 0),
        "selected_count": len(knowledge_cards),
        "knowledge_cards": knowledge_cards,
        "deck_brief": deck_brief,
    }


def main():
    parser = argparse.ArgumentParser(description="从知识库候选生成知识卡片和 deck brief")
    parser.add_argument("--query", required=True, help="主题或查询词")
    parser.add_argument("--mode", choices=["keyword", "vector", "hybrid"], default="hybrid", help="搜索模式")
    parser.add_argument("--limit", type=int, default=12, help="候选数量上限")
    parser.add_argument("--cards", type=int, default=5, help="最终卡片数量")
    parser.add_argument("--style", choices=["magazine", "swiss"], default="swiss", help="deck 风格")
    parser.add_argument("--audience", help="目标受众")
    parser.add_argument("--source-type", help="筛选来源类型")
    parser.add_argument("--content-chars", type=int, default=1000, help="导出 content 截断长度")
    parser.add_argument("--output", choices=["json", "markdown"], default="json", help="输出格式")

    args = parser.parse_args()

    result = generate_deck_brief(
        query=args.query,
        mode=args.mode,
        limit=args.limit,
        cards=args.cards,
        style=args.style,
        audience=args.audience,
        source_type=args.source_type,
        content_chars=args.content_chars,
    )

    if args.output == "markdown":
        print(render_markdown(result))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
