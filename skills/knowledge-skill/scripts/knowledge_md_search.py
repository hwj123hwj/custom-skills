#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Search compiled Markdown knowledge with ripgrep-style output."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


def run_rg(root: Path, query: str, limit: int) -> list[dict]:
    cmd = [
        "rg",
        "--line-number",
        "--with-filename",
        "--color",
        "never",
        "--glob",
        "*.md",
        query,
        str(root),
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if proc.returncode not in (0, 1):
        raise RuntimeError(proc.stderr.strip() or "rg failed")

    results = []
    for line in proc.stdout.splitlines():
        if len(results) >= limit:
            break
        parts = line.split(":", 2)
        if len(parts) != 3:
            continue
        path, lineno, text = parts
        results.append({"path": path, "line": int(lineno), "text": text.strip()})
    return results


def run_python_search(root: Path, query: str, limit: int, ignore_case: bool = True) -> list[dict]:
    flags = re.IGNORECASE if ignore_case else 0
    pattern = re.compile(re.escape(query), flags)
    results = []
    for path in sorted(root.rglob("*.md")):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for idx, line in enumerate(lines, 1):
            if pattern.search(line):
                results.append({"path": str(path), "line": idx, "text": line.strip()})
                if len(results) >= limit:
                    return results
    return results


def search_markdown(root: Path, query: str, limit: int, use_rg: bool = True) -> list[dict]:
    if use_rg and shutil.which("rg"):
        return run_rg(root, query, limit)
    return run_python_search(root, query, limit)


def render_markdown(query: str, results: list[dict]) -> str:
    lines = [f"# Markdown Knowledge Search: {query}", ""]
    if not results:
        lines.append("No matches found.")
        return "\n".join(lines)
    for item in results:
        lines.append(f"- [{Path(item['path']).name}]({item['path']}:{item['line']}): {item['text']}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Search compiled Markdown knowledge")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--root", default=".llm-wiki/wiki", help="Markdown root to search")
    parser.add_argument("--limit", type=int, default=20, help="Maximum matches")
    parser.add_argument("--no-rg", action="store_true", help="Use Python fallback instead of rg")
    parser.add_argument("--output", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    results = search_markdown(root, args.query, args.limit, use_rg=not args.no_rg)
    if args.output == "json":
        print(json.dumps({"query": args.query, "root": str(root), "total": len(results), "results": results}, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(args.query, results))


if __name__ == "__main__":
    main()
