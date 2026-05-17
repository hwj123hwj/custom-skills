#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "python-dotenv",
# ]
# ///
"""
Wiki 编译结果体检脚本。
扫描 llm-wiki 目录，生成一份面向维护者的快照，帮助判断 wiki 编译线是否健康。
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_WIKI_DIR = Path.home() / ".openclaw" / "workspace" / "llm-wiki"


def split_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    if not raw.startswith("---\n"):
        return {}, raw

    try:
        _, frontmatter, body = raw.split("---\n", 2)
    except ValueError:
        return {}, raw

    metadata: dict[str, Any] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata, body.strip()


def normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def extract_mentions_count(body: str) -> int:
    match = re.search(r"## 关联来源 \(Mentions\)(.*)", body, flags=re.DOTALL)
    if not match:
        return 0
    section = match.group(1)
    return len(re.findall(r"^- \[\[", section, flags=re.MULTILINE))


def read_page(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(raw)
    title = frontmatter.get("title") or path.stem
    page_type = frontmatter.get("type") or infer_page_type(path.name)

    summary_text = normalize_text(body)
    summary_length = len(summary_text)

    concepts_count = 0
    entities_count = 0
    if page_type == "source":
        concept_match = re.search(r"相关概念 .*?: (.*)", body)
        entity_match = re.search(r"相关实体 .*?: (.*)", body)
        if concept_match and "无" not in concept_match.group(1):
            concepts_count = len(re.findall(r"\[\[", concept_match.group(1)))
        if entity_match and "无" not in entity_match.group(1):
            entities_count = len(re.findall(r"\[\[", entity_match.group(1)))

    return {
        "path": str(path),
        "filename": path.name,
        "title": title,
        "type": page_type,
        "summary_length": summary_length,
        "mentions_count": extract_mentions_count(body),
        "concepts_count": concepts_count,
        "entities_count": entities_count,
        "date": frontmatter.get("date") or "",
    }


def infer_page_type(filename: str) -> str:
    if filename.startswith("source-"):
        return "source"
    if filename.startswith("concept-"):
        return "concept"
    if filename.startswith("entity-"):
        return "entity"
    return "unknown"


def load_state(wiki_dir: Path) -> dict[str, Any]:
    state_file = wiki_dir / ".compile-state.json"
    if not state_file.exists():
        return {"last_compile": None, "compiled_ids": []}
    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"last_compile": None, "compiled_ids": []}


def build_next_actions(
    source_pages: list[dict[str, Any]],
    concept_pages: list[dict[str, Any]],
    entity_pages: list[dict[str, Any]],
) -> list[str]:
    actions: list[str] = []

    thin_sources = [page for page in source_pages if page["summary_length"] < 220]
    empty_sources = [
        page for page in source_pages
        if page["concepts_count"] == 0 and page["entities_count"] == 0
    ]
    weak_concepts = [page for page in concept_pages if page["mentions_count"] <= 1]
    weak_entities = [page for page in entity_pages if page["mentions_count"] <= 1]

    if thin_sources:
        actions.append(
            f"有 {len(thin_sources)} 个 source 页面正文偏薄，优先回看原始知识条目并补厚内容。"
        )
    if empty_sources:
        actions.append(
            f"有 {len(empty_sources)} 个 source 页面没有抽出概念或实体，优先检查 wiki_compile 的提取质量。"
        )
    if weak_concepts:
        actions.append(
            f"有 {len(weak_concepts)} 个 concept 页面只有单一 mentions，后续可继续补同主题 raw 条目。"
        )
    if weak_entities:
        actions.append(
            f"有 {len(weak_entities)} 个 entity 页面只有单一 mentions，后续可继续补同主题 raw 条目。"
        )

    if not actions:
        actions.append("当前 wiki 编译结果整体健康，可以继续扩充真实 raw 来源并复编译。")

    return actions


def review_wiki(wiki_dir: Path) -> dict[str, Any]:
    wiki_pages_dir = wiki_dir / "wiki"
    state = load_state(wiki_dir)

    if not wiki_pages_dir.exists():
        return {
            "wiki_dir": str(wiki_dir),
            "exists": False,
            "generated_at": datetime.now().isoformat(),
            "total_pages": 0,
            "source_pages": [],
            "concept_pages": [],
            "entity_pages": [],
            "weak_pages": [],
            "next_actions": ["Wiki 目录不存在，先运行 wiki_compile.py 生成基础页面。"],
            "compiled_ids_count": len(state.get("compiled_ids", [])),
            "last_compile": state.get("last_compile"),
        }

    pages = [read_page(path) for path in sorted(wiki_pages_dir.glob("*.md"))]
    source_pages = [page for page in pages if page["type"] == "source"]
    concept_pages = [page for page in pages if page["type"] == "concept"]
    entity_pages = [page for page in pages if page["type"] == "entity"]

    weak_pages: list[dict[str, Any]] = []
    for page in source_pages:
        reasons: list[str] = []
        if page["summary_length"] < 220:
            reasons.append("正文偏薄")
        if page["concepts_count"] == 0 and page["entities_count"] == 0:
            reasons.append("未抽出概念/实体")
        if reasons:
            weak_pages.append(
                {
                    "title": page["title"],
                    "type": page["type"],
                    "filename": page["filename"],
                    "reasons": reasons,
                }
            )

    for page in concept_pages + entity_pages:
        if page["mentions_count"] <= 1:
            weak_pages.append(
                {
                    "title": page["title"],
                    "type": page["type"],
                    "filename": page["filename"],
                    "reasons": ["mentions 偏少"],
                }
            )

    next_actions = build_next_actions(source_pages, concept_pages, entity_pages)

    return {
        "wiki_dir": str(wiki_dir),
        "exists": True,
        "generated_at": datetime.now().isoformat(),
        "total_pages": len(pages),
        "source_count": len(source_pages),
        "concept_count": len(concept_pages),
        "entity_count": len(entity_pages),
        "compiled_ids_count": len(state.get("compiled_ids", [])),
        "last_compile": state.get("last_compile"),
        "recent_sources": sorted(
            source_pages,
            key=lambda page: page.get("date") or "",
            reverse=True,
        )[:10],
        "weak_pages": weak_pages[:20],
        "next_actions": next_actions,
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = ["# Wiki Review", ""]
    lines.append(f"- Generated at: {result['generated_at']}")
    lines.append(f"- Wiki dir: `{result['wiki_dir']}`")
    lines.append(f"- Exists: `{result['exists']}`")
    lines.append(f"- Compiled IDs: {result['compiled_ids_count']}")
    if result.get("last_compile"):
        lines.append(f"- Last compile: {result['last_compile']}")
    lines.append("")

    if not result["exists"]:
        lines.append("## Next Actions")
        for action in result["next_actions"]:
            lines.append(f"- {action}")
        lines.append("")
        return "\n".join(lines)

    lines.append("## Snapshot")
    lines.append(f"- Total pages: {result['total_pages']}")
    lines.append(f"- Source pages: {result['source_count']}")
    lines.append(f"- Concept pages: {result['concept_count']}")
    lines.append(f"- Entity pages: {result['entity_count']}")
    lines.append("")

    lines.append("## Recent Sources")
    if result["recent_sources"]:
        for page in result["recent_sources"]:
            lines.append(
                f"- `{page['filename']}` | {page['title']} | concepts {page['concepts_count']} | entities {page['entities_count']} | chars {page['summary_length']}"
            )
    else:
        lines.append("- 暂无 source 页面")
    lines.append("")

    lines.append("## Weak Pages")
    if result["weak_pages"]:
        for page in result["weak_pages"]:
            reasons = " / ".join(page["reasons"])
            lines.append(f"- `{page['filename']}` | {page['type']} | {page['title']} | {reasons}")
    else:
        lines.append("- 当前没有明显弱页面")
    lines.append("")

    lines.append("## Next Actions")
    for action in result["next_actions"]:
        lines.append(f"- {action}")
    lines.append("")

    return "\n".join(lines)


def maybe_write(content: str, path_str: str | None) -> None:
    if not path_str:
        return
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="体检 llm-wiki 编译结果")
    parser.add_argument("--wiki-dir", default=str(DEFAULT_WIKI_DIR), help="llm-wiki 根目录")
    parser.add_argument("--output", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--write", help="把 markdown 结果写到指定路径")
    args = parser.parse_args()

    result = review_wiki(Path(args.wiki_dir).expanduser())

    if args.output == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    markdown = render_markdown(result)
    maybe_write(markdown, args.write)
    print(markdown)


if __name__ == "__main__":
    main()
