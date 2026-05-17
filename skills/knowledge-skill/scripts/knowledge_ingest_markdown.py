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
把仓库内的 Markdown 文档导入知识池，作为 docs 来源的真实知识条目。
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

from knowledge_save import save_knowledge

REPO_ROOT = Path(__file__).resolve().parents[3]
REPO_BLOB_BASE = "https://github.com/hwj123hwj/custom-skills/blob/main"


def split_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    if not raw.startswith("---\n"):
        return {}, raw

    try:
        _, frontmatter, body = raw.split("---\n", 2)
    except ValueError:
        return {}, raw

    data = yaml.safe_load(frontmatter) or {}
    if not isinstance(data, dict):
        data = {}
    return data, body.strip()


def normalize_body(body: str) -> str:
    body = body.replace("\r\n", "\n").strip()
    body = re.sub(r"^#{1,6}\s*", "", body, flags=re.MULTILINE)
    body = re.sub(r"`{3,}.*?`{3,}", "", body, flags=re.DOTALL)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip()


def infer_title(frontmatter: dict[str, Any], body: str, path: Path) -> str:
    title = str(frontmatter.get("title") or "").strip()
    if title:
        return title

    for line in body.splitlines():
        clean = line.strip()
        if clean.startswith("# "):
            return clean[2:].strip()

    return path.stem.replace("-", " ").replace("_", " ").strip().title()


def infer_doc_type(relative_path: str) -> str:
    if relative_path.startswith("docs/agent-stories/"):
        return "story"
    if relative_path.startswith("docs/agent-infra/"):
        return "spec"
    if relative_path.startswith("docs/showcase/reviews/"):
        return "review"
    if relative_path.startswith("docs/showcase/recipes/"):
        return "recipe"
    if relative_path.startswith("docs/showcase/"):
        return "showcase"
    return "docs"


def build_metadata(frontmatter: dict[str, Any], relative_path: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "path": relative_path,
        "docType": infer_doc_type(relative_path),
    }

    for key in ("category", "sourceAgent", "agent", "status", "stage", "owner"):
        value = frontmatter.get(key)
        if isinstance(value, str) and value.strip():
            metadata[key] = value.strip()

    tags = frontmatter.get("tags")
    if isinstance(tags, list):
        metadata["tags"] = [str(tag).strip() for tag in tags if str(tag).strip()]

    return metadata


def remove_duplicate_title_prefix(content: str, title: str) -> str:
    lines = [line.rstrip() for line in content.splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)

    if lines and normalize_text(lines[0]) == normalize_text(title):
        lines.pop(0)
        while lines and not lines[0].strip():
            lines.pop(0)

    return "\n".join(lines).strip()


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip().lower()


def infer_ai_summary(content: str, title: str) -> str | None:
    paragraphs = [line.strip() for line in content.splitlines() if line.strip()]
    for paragraph in paragraphs:
        if paragraph.startswith("- "):
            continue
        if len(paragraph) < 12:
            continue
        cleaned = paragraph.replace("-", " ")
        cleaned = re.sub(r"[`*_#>]+", "", cleaned).strip()
        if normalize_text(cleaned) == normalize_text(title):
            continue
        if re.fullmatch(r"[A-Za-z0-9 _-]+", cleaned) and len(cleaned.split()) <= 4:
            continue
        if cleaned.endswith("：") or cleaned.endswith(":"):
            continue
        if len(cleaned) > 50:
            return cleaned[:50] + "..."
        return cleaned
    return None


def prepare_markdown_doc(path_str: str) -> dict[str, Any]:
    path = Path(path_str).resolve()
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")

    try:
        relative_path = str(path.relative_to(REPO_ROOT))
    except ValueError as exc:
        raise ValueError(f"文件不在仓库内: {path}") from exc

    raw = path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(raw)
    content = normalize_body(body)
    title = infer_title(frontmatter, body, path)
    content = remove_duplicate_title_prefix(content, title)

    return {
        "source_type": "docs",
        "source_id": relative_path,
        "source_url": f"{REPO_BLOB_BASE}/{relative_path}",
        "title": title,
        "content": content,
        "ai_summary": infer_ai_summary(content, title),
        "metadata": build_metadata(frontmatter, relative_path),
    }


def ingest_markdown_docs(paths: list[str], dry_run: bool = False) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for path in paths:
        payload = prepare_markdown_doc(path)
        if dry_run:
            payload["content_length"] = len(payload["content"])
            results.append(payload)
            continue

        saved = save_knowledge(
            source_type=payload["source_type"],
            source_id=payload["source_id"],
            title=payload["title"],
            content=payload["content"],
            source_url=payload["source_url"],
            metadata=payload["metadata"],
            ai_summary=payload.get("ai_summary"),
        )
        results.append(
            {
                "path": payload["source_id"],
                "title": payload["title"],
                "success": saved.get("success", False),
                "id": saved.get("id"),
                "ai_summary": saved.get("ai_summary"),
                "has_embedding": saved.get("has_embedding"),
                "error": saved.get("error"),
            }
        )
    return results


def main():
    parser = argparse.ArgumentParser(description="把 Markdown 文档导入知识池")
    parser.add_argument("--path", action="append", required=True, help="Markdown 路径，可重复传入")
    parser.add_argument("--dry-run", action="store_true", help="只解析，不写入数据库")
    parser.add_argument("--output", choices=["json"], default="json")
    args = parser.parse_args()

    results = ingest_markdown_docs(paths=args.path, dry_run=args.dry_run)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
