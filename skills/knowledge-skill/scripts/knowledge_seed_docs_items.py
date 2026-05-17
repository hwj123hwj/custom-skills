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
导入一批高价值仓库文档，作为 docs 来源的真实知识种子。
"""

import argparse
import json
from pathlib import Path

from knowledge_ingest_markdown import ingest_markdown_docs

REPO_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_DOCS = [
    "docs/agent-infra/knowledge-to-deck-mvp.md",
    "docs/agent-infra/knowledge-to-deck-agent-spec.md",
    "docs/agent-stories/intel-agent.md",
]


def main():
    parser = argparse.ArgumentParser(description="导入 docs 来源的知识种子")
    parser.add_argument("--path", action="append", help="额外指定 markdown 路径，可重复传入")
    parser.add_argument("--dry-run", action="store_true", help="只解析，不写库")
    args = parser.parse_args()

    paths = [str(REPO_ROOT / item) for item in DEFAULT_DOCS]
    if args.path:
        paths.extend(
            str((REPO_ROOT / item).resolve()) if not Path(item).is_absolute() else item
            for item in args.path
        )

    results = ingest_markdown_docs(paths=paths, dry_run=args.dry_run)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
