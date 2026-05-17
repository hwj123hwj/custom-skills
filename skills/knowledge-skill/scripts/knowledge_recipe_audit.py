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
批量审阅 showcase recipes，输出一份健康度总览。
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

    if reviewed == 0:
        return "weak", "没有留下可用于 deck 的候选"

    if exported > 0 and filtered == 1 and reviewed == 1:
        return "focused", "候选池已被很好地收紧到单一主题"

    if reviewed <= 2 and items and (items[0].get("deck_score") or 0) >= 8:
        return "healthy", "候选数量克制且顶部候选质量较高"

    if reviewed > 3:
        return "noisy", "候选偏多，后续建议继续收紧 recipe"

    return "watch", "基本可用，但仍建议继续观察候选纯度"


def audit_recipe(recipe_path: Path) -> dict[str, Any]:
    recipe, _notes = load_recipe(str(recipe_path))
    review = generate_review_from_recipe(str(recipe_path))
    health, note = classify_health(review)
    top_title = review["results"][0]["title"] if review.get("results") else ""
    top_score = review["results"][0]["deck_score"] if review.get("results") else None

    return {
        "id": recipe_path.stem,
        "title": recipe.get("title") or recipe.get("query") or recipe_path.stem,
        "category": recipe.get("category") or "knowledge-cards",
        "query": recipe.get("query") or "",
        "health": health,
        "health_note": note,
        "exported": review.get("total_exported", 0),
        "filtered": review.get("total_filtered", 0),
        "reviewed": review.get("total_reviewed", 0),
        "top_title": top_title,
        "top_score": top_score,
        "recipe_path": str(recipe_path),
    }


def render_markdown(items: list[dict[str, Any]]) -> str:
    lines = ["# Recipe Audit", ""]
    lines.append("| Recipe | Category | Health | Exported | Filtered | Reviewed | Top Candidate |")
    lines.append("| --- | --- | --- | ---: | ---: | ---: | --- |")

    for item in items:
        top = item["top_title"] or "—"
        lines.append(
            f"| {item['title']} | {item['category']} | {item['health']} | "
            f"{item['exported']} | {item['filtered']} | {item['reviewed']} | {top} |"
        )

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    for item in items:
        lines.append(f"### {item['title']}")
        lines.append(f"- Query: {item['query']}")
        lines.append(f"- Health: {item['health']}")
        lines.append(f"- Note: {item['health_note']}")
        if item["top_title"]:
            lines.append(f"- Top candidate: {item['top_title']} (score: {item['top_score']})")
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
