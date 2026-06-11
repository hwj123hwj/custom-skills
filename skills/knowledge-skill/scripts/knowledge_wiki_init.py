#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Initialize an agent-maintained Markdown wiki.

This creates the lightweight LLM Wiki directory used as the compiled knowledge
layer. The wiki is intentionally file-first: agents maintain Markdown pages,
humans browse/edit with any Markdown editor, and PostgreSQL remains the raw
knowledge pool.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


def init_wiki(root: Path, force: bool = False) -> dict:
    raw_dir = root / "raw"
    wiki_dir = root / "wiki"
    index_file = root / "index.md"
    log_file = root / "log.md"
    overview_file = wiki_dir / "overview.md"

    root.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    wiki_dir.mkdir(parents=True, exist_ok=True)

    created: list[str] = []

    if force or not index_file.exists():
        index_file.write_text(
            """# LLM Wiki Index

> Agent-maintained compiled knowledge. Prefer editing source material in `raw/` or upstream systems, then ingest.

## Sources
<!-- Source summaries will be listed here -->

## Entities
<!-- Entity pages will be listed here -->

## Concepts
<!-- Concept pages will be listed here -->

## Synthesis
<!-- Cross-cutting analysis pages will be listed here -->
""",
            encoding="utf-8",
        )
        created.append(str(index_file))

    if force or not log_file.exists():
        today = date.today().isoformat()
        log_file.write_text(
            f"""# LLM Wiki Log

> Chronological record of wiki operations.

## [{today}] init | Wiki Initialized
- Created wiki directory structure
- Ready for source ingestion
""",
            encoding="utf-8",
        )
        created.append(str(log_file))

    if force or not overview_file.exists():
        today = date.today().isoformat()
        overview_file.write_text(
            f"""---
type: overview
date: {today}
tags:
  - overview
---

# Overview

This page is the entry point for the compiled Markdown knowledge base.

Use `raw/` for immutable source material and `wiki/` for agent-maintained pages.
""",
            encoding="utf-8",
        )
        created.append(str(overview_file))

    return {
        "root": str(root),
        "raw": str(raw_dir),
        "wiki": str(wiki_dir),
        "index": str(index_file),
        "log": str(log_file),
        "created_or_overwritten": created,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize .llm-wiki directory structure")
    parser.add_argument("--root", default=".llm-wiki", help="Wiki root directory")
    parser.add_argument("--force", action="store_true", help="Overwrite index/log/overview if present")
    parser.add_argument("--output", choices=["json", "markdown"], default="json")
    args = parser.parse_args()

    result = init_wiki(Path(args.root).expanduser().resolve(), force=args.force)

    if args.output == "markdown":
        print("# LLM Wiki Initialized")
        print()
        for key in ("root", "raw", "wiki", "index", "log"):
            print(f"- {key}: `{result[key]}`")
        print(f"- created_or_overwritten: {len(result['created_or_overwritten'])}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
