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
从 showcase recipe 复跑候选体检结果。
"""

import argparse
from pathlib import Path

from knowledge_candidate_review import render_markdown, review_candidates
from knowledge_deck_recipe import load_recipe


def generate_review_from_recipe(recipe_path: str) -> dict:
    recipe, _notes = load_recipe(recipe_path)
    query = str(recipe.get("query") or "").strip()
    if not query:
        raise ValueError(f"Recipe 缺少 query: {recipe_path}")

    min_score = recipe.get("reviewMinScore")
    return review_candidates(
        query=query,
        mode=str(recipe.get("mode") or "hybrid"),
        limit=int(recipe.get("limit") or 12),
        source_type=str(recipe["sourceType"]) if recipe.get("sourceType") else None,
        content_chars=int(recipe.get("contentChars") or 1000),
        min_score=int(min_score) if min_score is not None else None,
        require_ai_summary=bool(recipe.get("requireAiSummary")),
    )


def maybe_write(markdown: str, output_path: str | None) -> None:
    if not output_path:
        return
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="从 recipe 复跑候选体检")
    parser.add_argument("--recipe", required=True, help="recipe markdown 路径")
    parser.add_argument("--write", help="把 markdown 结果写入指定路径")
    args = parser.parse_args()

    result = generate_review_from_recipe(args.recipe)
    markdown = render_markdown(result)
    maybe_write(markdown, args.write)
    print(markdown)


if __name__ == "__main__":
    main()
