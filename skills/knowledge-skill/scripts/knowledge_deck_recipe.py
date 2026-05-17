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
从 markdown recipe 生成可复跑的 deck brief。
"""

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from knowledge_to_deck_brief import generate_deck_brief, render_markdown


def load_recipe(recipe_path: str) -> tuple[dict[str, Any], str]:
    path = Path(recipe_path)
    raw = path.read_text(encoding="utf-8")

    if not raw.startswith("---\n"):
        raise ValueError(f"Recipe 缺少 frontmatter: {recipe_path}")

    try:
        _, frontmatter, body = raw.split("---\n", 2)
    except ValueError as exc:
        raise ValueError(f"Recipe frontmatter 格式不正确: {recipe_path}") from exc

    data = yaml.safe_load(frontmatter) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Recipe frontmatter 必须是对象: {recipe_path}")

    return data, body.strip()


def generate_from_recipe(recipe_path: str) -> dict[str, Any]:
    recipe, notes = load_recipe(recipe_path)

    query = str(recipe.get("query") or "").strip()
    if not query:
        raise ValueError(f"Recipe 缺少 query: {recipe_path}")

    result = generate_deck_brief(
        query=query,
        mode=str(recipe.get("mode") or "hybrid"),
        limit=int(recipe.get("limit") or 12),
        cards=int(recipe.get("cards") or 5),
        style=str(recipe.get("style") or "swiss"),
        audience=str(recipe["audience"]) if recipe.get("audience") else None,
        source_type=str(recipe["sourceType"]) if recipe.get("sourceType") else None,
        content_chars=int(recipe.get("contentChars") or 1000),
        required_terms=recipe.get("requiredTerms"),
        excluded_terms=recipe.get("excludedTerms"),
    )

    result["recipe"] = {
        "title": recipe.get("title") or query,
        "category": recipe.get("category") or "knowledge-cards",
        "source_agent": recipe.get("sourceAgent") or "knowledge-to-deck-agent",
        "tags": recipe.get("tags") or [],
        "notes": notes,
        "path": recipe_path,
    }
    return result


def maybe_write_markdown(markdown: str, output_path: str | None) -> None:
    if not output_path:
        return
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="从 markdown recipe 生成 deck brief")
    parser.add_argument("--recipe", required=True, help="recipe markdown 路径")
    parser.add_argument("--output", choices=["json", "markdown"], default="markdown", help="输出格式")
    parser.add_argument("--write", help="把 markdown 结果写入指定路径")
    args = parser.parse_args()

    result = generate_from_recipe(args.recipe)

    if args.output == "markdown":
        markdown = render_markdown(result)
        maybe_write_markdown(markdown, args.write)
        print(markdown)
        return

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
