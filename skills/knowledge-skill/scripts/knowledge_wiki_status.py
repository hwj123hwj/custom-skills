#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Report status for an agent-maintained Markdown wiki."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def count_files(root: Path, pattern: str = "*") -> int:
    if not root.exists():
        return 0
    return sum(1 for path in root.rglob(pattern) if path.is_file() and not path.name.startswith("."))


def recent_log_entries(log_file: Path, limit: int = 5) -> list[str]:
    if not log_file.exists():
        return []
    text = log_file.read_text(encoding="utf-8", errors="replace")
    headings = re.findall(r"^## \[.+$", text, flags=re.MULTILINE)
    return headings[-limit:]


def wiki_status(root: Path, recent: int = 5) -> dict:
    raw_dir = root / "raw"
    wiki_dir = root / "wiki"
    index_file = root / "index.md"
    log_file = root / "log.md"
    pages = [p for p in wiki_dir.rglob("*.md")] if wiki_dir.exists() else []

    return {
        "root": str(root),
        "initialized": index_file.exists() and log_file.exists() and wiki_dir.exists(),
        "raw_files": count_files(raw_dir),
        "wiki_pages": len(pages),
        "source_pages": len([p for p in pages if p.name.startswith("source-")]),
        "index_exists": index_file.exists(),
        "log_exists": log_file.exists(),
        "recent_activity": recent_log_entries(log_file, limit=recent),
    }


def render_markdown(status: dict) -> str:
    lines = [
        "# LLM Wiki Status",
        "",
        f"- Root: `{status['root']}`",
        f"- Initialized: `{status['initialized']}`",
        f"- Raw files: `{status['raw_files']}`",
        f"- Wiki pages: `{status['wiki_pages']}`",
        f"- Source pages: `{status['source_pages']}`",
        f"- Index exists: `{status['index_exists']}`",
        f"- Log exists: `{status['log_exists']}`",
        "",
        "## Recent Activity",
    ]
    if status["recent_activity"]:
        lines.extend(f"- {entry}" for entry in status["recent_activity"])
    else:
        lines.append("- No log entries")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Show .llm-wiki status")
    parser.add_argument("--root", default=".llm-wiki", help="Wiki root directory")
    parser.add_argument("--recent", type=int, default=5, help="Recent log headings to show")
    parser.add_argument("--output", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    status = wiki_status(Path(args.root).expanduser().resolve(), recent=args.recent)
    if args.output == "json":
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(status))


if __name__ == "__main__":
    main()
