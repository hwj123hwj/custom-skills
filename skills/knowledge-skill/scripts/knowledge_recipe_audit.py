#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "psycopg2-binary",
#     "python-dotenv",
#     "requests",
#     "pyyaml",
# ]
# ///
"""
批量审阅 showcase recipes，输出一份更可执行的健康度总览。
"""

import argparse
import json
from pathlib import Path
from typing import Any

from knowledge_candidate_review_recipe import generate_review_from_recipe
from knowledge_deck_recipe import load_recipe


def classify_health(result: dict[str, Any]) -> tuple[str, str]:
    exported = int(result.get("total_exported", 0))
    filtered = int(result.get("total_filtered", 0))
    reviewed = int(result.get("total_reviewed", 0))
    items = result.get("results", [])
    top_score = float(items[0].get("deck_score", 0)) if items else 0.0
    avg_score = (
        sum(float(item.get("deck_score", 0)) for item in items) / reviewed if reviewed else 0.0
    )
    filter_ratio = filtered / exported if exported else 0.0

    if reviewed == 0:
        return "weak", "没有留下可用于 deck 的候选"

    if exported > 0 and filtered == 1 and reviewed == 1 and top_score >= 8:
        return "focused", "候选池已被很好地收紧到单一主题"

    if reviewed <= 2 and top_score >= 8 and avg_score >= 7:
        return "healthy", "候选数量克制且顶部候选质量较高"

    if filter_ratio >= 0.8 and avg_score < 6:
        return "weak", "大部分候选仍然偏弱，说明知识池或 query 质量不足"

    if reviewed > 3:
        return "noisy", "候选偏多，后续建议继续收紧 recipe"

    return "watch", "基本可用，但仍建议继续观察候选纯度"


def infer_action(result: dict[str, Any], health: str, source_profile: str) -> str:
    exported = int(result.get("total_exported", 0))
    filtered = int(result.get("total_filtered", 0))
    reviewed = int(result.get("total_reviewed", 0))
    items = result.get("results", [])
    top_score = float(items[0].get("deck_score", 0)) if items else 0.0
    missing_ai = sum(1 for item in items if not item.get("ai_summary"))
    has_noise = any(
        any("标题疑似噪音/标题党" in reason for reason in item.get("reasons", [])) for item in items
    )

    if source_profile == "demo-only":
        if health in {"focused", "healthy"}:
            return "当前样板已稳定，下一步应补真实知识源并逐步减少对 test 条目的依赖"
        return "先稳定演示条目质量，再考虑迁移到真实知识源"
    if source_profile == "mixed":
        return "优先减少 test 条目占比，让 recipe 逐步过渡到真实知识源"

    if health == "focused":
        return "维持当前 recipe，优先继续补充同主题高质量知识源"
    if health == "healthy":
        if missing_ai:
            return "候选整体可用，优先补 AI 摘要以提升后续卡片压缩质量"
        return "候选质量稳定，可以继续产出 deck 或扩展同类 recipe"
    if health == "noisy":
        return "增加 requiredTerms 或 sourceType，必要时补 excludedTerms 收紧候选池"
    if health == "weak":
        if exported == 0:
            return "先补知识源或放宽 query，不要急着做 deck"
        if top_score < 6:
            return "优先重写 query 或补入更强知识条目，再考虑 deck 产出"
        return "先检查知识条目质量，确认不是摘要过短或内容过薄"
    if has_noise:
        return "候选里已有噪音信号，建议先加 excludedTerms 再复跑 review"
    if filtered == reviewed and reviewed >= 3:
        return "可进一步收紧 minScore 或 requiredTerms，避免 deck 过于分散"
    return "保持观察，下一轮优先检查 query 和候选纯度是否继续偏移"


def summarize_metrics(result: dict[str, Any]) -> dict[str, Any]:
    items = result.get("results", [])
    reviewed = int(result.get("total_reviewed", 0))
    avg_score = (
        round(sum(float(item.get("deck_score", 0)) for item in items) / reviewed, 2) if reviewed else 0.0
    )
    ai_coverage = (
        round(sum(1 for item in items if item.get("ai_summary")) / reviewed * 100, 1) if reviewed else 0.0
    )
    source_types = sorted({str(item.get("source_type") or "unknown") for item in items})
    return {
        "avg_score": avg_score,
        "ai_coverage": ai_coverage,
        "source_types": source_types,
    }


def classify_source_profile(source_types: list[str]) -> tuple[str, str]:
    normalized = {source.lower() for source in source_types}
    if not normalized:
        return "unknown", "暂时无法判断来源结构"
    if normalized == {"test"}:
        return "demo-only", "当前主要依赖演示条目，适合样板验证，不适合长期代表真实知识池"
    if "test" in normalized and len(normalized) > 1:
        return "mixed", "当前混合了演示条目和真实来源，适合过渡阶段验证"
    return "real-sources", "当前主要依赖真实来源，已经更接近长期可复用展示资产"


def classify_readiness(health: str, source_profile: str, avg_score: float) -> tuple[str, str]:
    if source_profile == "real-sources":
        if health in {"focused", "healthy"} and avg_score >= 8:
            return "production-track", "候选质量和来源结构都较健康，可以继续扩成长期 deck 资产"
        return "stabilizing", "来源结构已经真实，但候选质量仍需继续调优"

    if source_profile == "mixed":
        if health in {"focused", "healthy"}:
            return "transitioning", "展示链已稳定，下一步应继续减少对演示条目的依赖"
        return "mixed-watch", "来源结构和候选质量都还需要继续观察"

    if source_profile == "demo-only":
        if health in {"focused", "healthy"}:
            return "demo-stable", "适合作为样板，但下一步应补真实知识源，避免长期停留在演示层"
        return "demo-fragile", "当前既依赖演示条目，候选质量也不够稳"

    return "unknown", "暂时无法判断就绪度"


def audit_recipe(recipe_path: Path) -> dict[str, Any]:
    recipe, _notes = load_recipe(str(recipe_path))
    review = generate_review_from_recipe(str(recipe_path))
    health, note = classify_health(review)
    metrics = summarize_metrics(review)
    source_profile, source_note = classify_source_profile(metrics["source_types"])
    readiness, readiness_note = classify_readiness(health, source_profile, metrics["avg_score"])
    action = infer_action(review, health, source_profile)
    top_title = review["results"][0]["title"] if review.get("results") else ""
    top_score = review["results"][0]["deck_score"] if review.get("results") else None

    return {
        "id": recipe_path.stem,
        "title": recipe.get("title") or recipe.get("query") or recipe_path.stem,
        "category": recipe.get("category") or "knowledge-cards",
        "query": recipe.get("query") or "",
        "health": health,
        "health_note": note,
        "source_profile": source_profile,
        "source_note": source_note,
        "readiness": readiness,
        "readiness_note": readiness_note,
        "action": action,
        "exported": review.get("total_exported", 0),
        "filtered": review.get("total_filtered", 0),
        "reviewed": review.get("total_reviewed", 0),
        "top_title": top_title,
        "top_score": top_score,
        "avg_score": metrics["avg_score"],
        "ai_coverage": metrics["ai_coverage"],
        "source_types": metrics["source_types"],
        "recipe_path": str(recipe_path),
    }


def render_markdown(items: list[dict[str, Any]]) -> str:
    lines = ["# Recipe Audit", ""]
    lines.append(
        "| Recipe | Category | Health | Source Profile | Readiness | Exported | Filtered | Reviewed | Avg Score | AI Coverage | Top Candidate |"
    )
    lines.append("| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |")

    for item in items:
        top = item["top_title"] or "—"
        lines.append(
            f"| {item['title']} | {item['category']} | {item['health']} | {item['source_profile']} | {item['readiness']} | "
            f"{item['exported']} | {item['filtered']} | {item['reviewed']} | "
            f"{item['avg_score']} | {item['ai_coverage']}% | {top} |"
        )

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    for item in items:
        lines.append(f"### {item['title']}")
        lines.append(f"- Query: {item['query']}")
        lines.append(f"- Health: {item['health']}")
        lines.append(f"- Note: {item['health_note']}")
        lines.append(f"- Source profile: {item['source_profile']}")
        lines.append(f"- Source note: {item['source_note']}")
        lines.append(f"- Readiness: {item['readiness']}")
        lines.append(f"- Readiness note: {item['readiness_note']}")
        lines.append(f"- Avg score: {item['avg_score']}")
        lines.append(f"- AI coverage: {item['ai_coverage']}%")
        lines.append(f"- Source types: {', '.join(item['source_types']) or '—'}")
        if item["top_title"]:
            lines.append(f"- Top candidate: {item['top_title']} (score: {item['top_score']})")
        lines.append(f"- Next action: {item['action']}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def maybe_write(markdown: str, output_path: str | None) -> None:
    if not output_path:
        return
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="批量审阅 showcase recipes")
    parser.add_argument(
        "--recipes-dir",
        default="docs/showcase/recipes",
        help="recipe 目录",
    )
    parser.add_argument("--write", help="把 markdown 结果写入指定路径")
    parser.add_argument("--output", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    recipes_dir = Path(args.recipes_dir)
    recipe_files = sorted(
        path for path in recipes_dir.glob("*.md") if path.name.lower() != "readme.md"
    )

    audited = [audit_recipe(path) for path in recipe_files]

    if args.output == "json":
        print(json.dumps(audited, ensure_ascii=False, indent=2, default=str))
        return

    markdown = render_markdown(audited)
    maybe_write(markdown, args.write)
    print(markdown)


if __name__ == "__main__":
    main()
