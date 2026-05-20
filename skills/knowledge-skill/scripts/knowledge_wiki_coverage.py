#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "psycopg2-binary",
#     "python-dotenv",
# ]
# ///
"""
Wiki Coverage Report — 桥接 raw 知识池和 wiki 编译产出的覆盖率报告。
回答三个核心问题：
1. 知识池中有多少条目已被 wiki 编译 vs 未编译？
2. 按 source_type 和 profile_score 的覆盖情况如何？
3. 哪些 concept/entity 页面 mentions 偏少，需要补充更多 raw 条目？
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")
load_dotenv(Path.home() / ".openclaw" / "secrets.env")

DEFAULT_WIKI_DIR = Path.home() / ".openclaw" / "workspace" / "llm-wiki"

USER_PROFILE_KEYWORDS = [
    "agent", "linux", "security", "open source", "openclaw",
    "claude", "gpt", "llm", "ai", "自动化", "运维",
    "devops", "docker", "kubernetes", "后端", "go",
    "python", "工程", "框架", "开源", "rag", "karpathy"
]


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


def count_mentions(body: str) -> int:
    return len(re.findall(r"^- \[\[", body, flags=re.MULTILINE))


def read_page_summary(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(raw)
    title = frontmatter.get("title") or path.stem
    page_type = frontmatter.get("type") or "unknown"
    mentions = count_mentions(body)
    has_context = "## 来源语境" in body
    normalized = re.sub(r"\s+", " ", body or "").strip()
    return {
        "filename": path.name,
        "title": title,
        "type": page_type,
        "mentions": mentions,
        "has_context": has_context,
        "body_length": len(normalized),
    }


def scan_wiki(wiki_dir: Path) -> dict[str, Any]:
    """扫描 wiki 编译产出，统计 source/concept/entity 页面质量。"""
    wiki_pages_dir = wiki_dir / "wiki"
    if not wiki_pages_dir.exists():
        return {"pages": [], "source_pages": [], "concept_pages": [], "entity_pages": []}

    pages = []
    for path in sorted(wiki_pages_dir.glob("*.md")):
        pages.append(read_page_summary(path))

    source_pages = [p for p in pages if p["type"] == "source"]
    concept_pages = [p for p in pages if p["type"] == "concept"]
    entity_pages = [p for p in pages if p["type"] == "entity"]

    return {
        "pages": pages,
        "source_pages": source_pages,
        "concept_pages": concept_pages,
        "entity_pages": entity_pages,
    }


def load_compile_state(wiki_dir: Path) -> dict[str, Any]:
    state_file = wiki_dir / ".compile-state.json"
    if not state_file.exists():
        return {"last_compile": None, "compiled_ids": []}
    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"last_compile": None, "compiled_ids": []}


def query_pool_stats(compiled_ids: set[str]) -> dict[str, Any] | None:
    """尝试查询知识池统计。如果 DB 不可用则返回 None。"""
    db_config = {
        "host": os.getenv("DB_HOST", ""),
        "port": int(os.getenv("DB_PORT", 5433)),
        "user": os.getenv("DB_USER", ""),
        "password": os.getenv("DB_PASSWORD", ""),
        "dbname": os.getenv("DB_NAME", ""),
    }

    if not db_config["host"]:
        return None

    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        return None

    try:
        conn = psycopg2.connect(**db_config)
    except Exception:
        return None

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # 总量和按来源统计
        cur.execute("""
            SELECT source_type, count(*) as cnt,
                   avg(length(content))::int as avg_content,
                   count(CASE WHEN ai_summary IS NOT NULL AND ai_summary != '' THEN 1 END) as ai_count
            FROM knowledge_items
            WHERE status = 'active' OR status IS NULL
            GROUP BY source_type
            ORDER BY cnt DESC
        """)
        source_stats = [dict(row) for row in cur.fetchall()]

        cur.execute("SELECT count(*) FROM knowledge_items WHERE status = 'active' OR status IS NULL")
        total = cur.fetchone()["count"]

        # 按 profile_score 分桶看哪些高价值条目还没编译
        cur.execute("""
            SELECT id, source_type, title, length(content) as content_len,
                   ai_summary IS NOT NULL AND ai_summary != '' as has_ai
            FROM knowledge_items
            WHERE status = 'active' OR status IS NULL
            ORDER BY created_at DESC
        """)
        all_items = [dict(row) for row in cur.fetchall()]

        cur.close()
        conn.close()

        # 计算 profile_score
        scored_items = []
        for item in all_items:
            title = item.get("title", "")
            content_hint = title  # 简化：只用 title 计算 profile_score
            score = sum(1 for kw in USER_PROFILE_KEYWORDS if kw.lower() in title.lower() or kw.lower() in content_hint.lower())
            item["profile_score"] = score
            scored_items.append(item)

        # 分桶：已编译 vs 未编译
        compiled = [i for i in scored_items if str(i["id"]) in compiled_ids]
        uncompiled = [i for i in scored_items if str(i["id"]) not in compiled_ids]
        high_value_uncompiled = [i for i in uncompiled if i["profile_score"] > 0]

        return {
            "total": total,
            "compiled_count": len(compiled),
            "uncompiled_count": len(uncompiled),
            "high_value_uncompiled": len(high_value_uncompiled),
            "source_stats": source_stats,
            "coverage_pct": round(len(compiled) / total * 100, 1) if total else 0,
            "high_value_uncompiled_items": [
                {"title": i["title"], "source_type": i["source_type"], "profile_score": i["profile_score"]}
                for i in sorted(high_value_uncompiled, key=lambda x: x["profile_score"], reverse=True)[:15]
            ],
        }
    except Exception:
        return None


def build_coverage_report(wiki_dir: Path) -> dict[str, Any]:
    """生成完整的 wiki coverage report。"""
    state = load_compile_state(wiki_dir)
    compiled_ids = set(state.get("compiled_ids", []))
    wiki_data = scan_wiki(wiki_dir)
    pool_stats = query_pool_stats(compiled_ids)

    # 分析 concept/entity 薄弱页面
    weak_concepts = [
        {"filename": p["filename"], "title": p["title"], "mentions": p["mentions"], "has_context": p["has_context"]}
        for p in wiki_data["concept_pages"]
        if p["mentions"] <= 1 or not p["has_context"]
    ]
    weak_entities = [
        {"filename": p["filename"], "title": p["title"], "mentions": p["mentions"], "has_context": p["has_context"]}
        for p in wiki_data["entity_pages"]
        if p["mentions"] <= 1 or not p["has_context"]
    ]

    # 薄 source 页面
    thin_sources = [
        {"filename": p["filename"], "title": p["title"], "body_length": p["body_length"]}
        for p in wiki_data["source_pages"]
        if p["body_length"] < 400
    ]

    # 生成建议的 target concepts/entities（给 wiki_compile --target-concept 用）
    target_concepts = sorted(set(p["title"] for p in weak_concepts if p["mentions"] <= 1))[:10]
    target_entities = sorted(set(p["title"] for p in weak_entities if p["mentions"] <= 1))[:10]

    # 构建下一步建议
    actions = []
    if pool_stats is None:
        actions.append("⚠️ 数据库不可用，无法获取知识池覆盖率。请确保 PostgreSQL 正在运行。")
    else:
        if pool_stats["coverage_pct"] < 50:
            actions.append(
                f"当前 wiki 编译覆盖率仅 {pool_stats['coverage_pct']}%，"
                f"还有 {pool_stats['high_value_uncompiled']} 条高价值条目未编译。"
                f"建议运行 `wiki_compile.py --limit 10` 扩大覆盖。"
            )
        if pool_stats["high_value_uncompiled"] > 5:
            actions.append(
                f"知识池中有 {pool_stats['high_value_uncompiled']} 条高价值条目未编译，"
                f"优先执行编译。"
            )
        low_ai = [s for s in pool_stats["source_stats"] if s["cnt"] > 0 and s["ai_count"] / s["cnt"] < 0.8]
        if low_ai:
            actions.append(
                f"以下来源 AI 摘要覆盖率低：{', '.join(s['source_type'] for s in low_ai)}。"
                f"先跑 `knowledge_backfill_ai_summary.py` 补摘要。"
            )

    if weak_concepts:
        actions.append(
            f"有 {len(weak_concepts)} 个 concept 页面 mentions ≤1 且缺少来源语境，"
            f"建议运行 `wiki_compile.py --target-concept concept名` 定向增强。"
        )
    if weak_entities:
        actions.append(
            f"有 {len(weak_entities)} 个 entity 页面 mentions ≤1 且缺少来源语境，"
            f"建议运行 `wiki_compile.py --target-entity entity名` 定向增强。"
        )
    if thin_sources:
        actions.append(
            f"有 {len(thin_sources)} 个 source 页面正文过薄（<400 chars），"
            f"需要回看原始知识条目补充内容。"
        )
    if not actions:
        actions.append("Wiki 编译覆盖率合理，concept/entity 密度足够，可以继续扩充知识池。")

    return {
        "generated_at": datetime.now().isoformat(),
        "wiki_dir": str(wiki_dir),
        "compile_state": {
            "last_compile": state.get("last_compile"),
            "compiled_ids_count": len(compiled_ids),
        },
        "wiki_pages": {
            "total": len(wiki_data["pages"]),
            "sources": len(wiki_data["source_pages"]),
            "concepts": len(wiki_data["concept_pages"]),
            "entities": len(wiki_data["entity_pages"]),
        },
        "pool_stats": pool_stats,
        "weak_concepts": weak_concepts[:20],
        "weak_entities": weak_entities[:20],
        "thin_sources": thin_sources[:10],
        "target_concepts": target_concepts,
        "target_entities": target_entities,
        "next_actions": actions,
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = ["# Wiki Coverage Report", ""]
    lines.append(f"- Generated at: {result['generated_at']}")
    lines.append(f"- Wiki dir: `{result['wiki_dir']}`")
    lines.append("")

    # 编译状态
    cs = result["compile_state"]
    lines.append("## 编译状态")
    lines.append(f"- 已编译条目数: {cs['compiled_ids_count']}")
    if cs.get("last_compile"):
        lines.append(f"- 最后编译时间: {cs['last_compile']}")
    lines.append("")

    # Wiki 页面统计
    wp = result["wiki_pages"]
    lines.append("## Wiki 页面统计")
    lines.append(f"- 总页面数: {wp['total']}")
    lines.append(f"- Source 页面: {wp['sources']}")
    lines.append(f"- Concept 页面: {wp['concepts']}")
    lines.append(f"- Entity 页面: {wp['entities']}")
    lines.append("")

    # 知识池覆盖率（如果 DB 可用）
    pool = result.get("pool_stats")
    if pool:
        lines.append("## 知识池覆盖率")
        lines.append(f"- 知识池总量: {pool['total']}")
        lines.append(f"- 已编译: {pool['compiled_count']}")
        lines.append(f"- 未编译: {pool['uncompiled_count']}")
        lines.append(f"- **覆盖率: {pool['coverage_pct']}%**")
        lines.append(f"- 高价值未编译: {pool['high_value_uncompiled']}")
        lines.append("")

        if pool.get("source_stats"):
            lines.append("### 按来源分布")
            lines.append("")
            lines.append("| Source | Count | AI Coverage | Avg Content |")
            lines.append("| --- | ---: | ---: | ---: |")
            for s in pool["source_stats"]:
                ai_pct = round(s["ai_count"] / s["cnt"] * 100, 1) if s["cnt"] else 0
                lines.append(f"| {s['source_type']} | {s['cnt']} | {ai_pct}% | {s['avg_content']} |")
            lines.append("")

        if pool.get("high_value_uncompiled_items"):
            lines.append("### 高价值未编译条目")
            for item in pool["high_value_uncompiled_items"][:10]:
                lines.append(f"- [{item['source_type']}] {item['title']} (score: {item['profile_score']})")
            lines.append("")
    else:
        lines.append("## 知识池覆盖率")
        lines.append("- ⚠️ 数据库不可用，无法获取覆盖率数据")
        lines.append("")

    # 薄弱页面
    if result["weak_concepts"]:
        lines.append("## 薄弱 Concept 页面")
        for c in result["weak_concepts"]:
            ctx = "有语境" if c["has_context"] else "无语境"
            lines.append(f"- `{c['filename']}` | mentions: {c['mentions']} | {ctx}")
        lines.append("")

    if result["weak_entities"]:
        lines.append("## 薄弱 Entity 页面")
        for e in result["weak_entities"]:
            ctx = "有语境" if e["has_context"] else "无语境"
            lines.append(f"- `{e['filename']}` | mentions: {e['mentions']} | {ctx}")
        lines.append("")

    if result["thin_sources"]:
        lines.append("## 偏薄 Source 页面")
        for s in result["thin_sources"]:
            lines.append(f"- `{s['filename']}` | {s['body_length']} chars | {s['title']}")
        lines.append("")

    # 建议的定向编译目标
    if result["target_concepts"] or result["target_entities"]:
        lines.append("## 建议定向编译")
        if result["target_concepts"]:
            concepts_args = " ".join(f"--target-concept '{c}'" for c in result["target_concepts"][:5])
            lines.append(f"```bash")
            lines.append(f"python wiki_compile.py --limit 5 {concepts_args}")
            lines.append(f"```")
        if result["target_entities"]:
            entities_args = " ".join(f"--target-entity '{e}'" for e in result["target_entities"][:5])
            lines.append(f"```bash")
            lines.append(f"python wiki_compile.py --limit 5 {entities_args}")
            lines.append(f"```")
        lines.append("")

    # 下一步建议
    lines.append("## 下一步建议")
    for action in result["next_actions"]:
        lines.append(f"- {action}")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Wiki 编译覆盖率报告")
    parser.add_argument("--wiki-dir", default=str(DEFAULT_WIKI_DIR), help="llm-wiki 根目录")
    parser.add_argument("--output", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--write", help="把 markdown 结果写到指定路径")
    args = parser.parse_args()

    result = build_coverage_report(Path(args.wiki_dir).expanduser())

    if args.output == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        return

    markdown = render_markdown(result)
    if args.write:
        path = Path(args.write)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown, encoding="utf-8")
    print(markdown)


if __name__ == "__main__":
    main()
