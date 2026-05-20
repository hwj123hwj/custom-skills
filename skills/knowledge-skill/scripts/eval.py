#!/usr/bin/env python3
"""
Knowledge Skill 评测脚本 (AutoResearch 风格)
用法: python eval.py [--verbose] [--record]

--record  追加结果到 results.tsv
--verbose 显示详细输出
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

VENV = "uv run"
SCRIPTS = str(Path(__file__).parent)
RESULTS_FILE = str(Path(__file__).parent.parent / "eval_results.tsv")


def run_script(script_name, args_str, timeout=60):
    """运行脚本，返回 (ok, stdout, stderr, duration)"""
    cmd = f'{VENV} {SCRIPTS}/{script_name} {args_str}'
    start = time.time()
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        dur = time.time() - start
        return r.returncode == 0, r.stdout.strip(), r.stderr.strip(), dur
    except subprocess.TimeoutExpired:
        return False, "", "TIMEOUT", timeout


def test_save():
    """测试1: 基本入库"""
    ok, out, err, dur = run_script("knowledge_save.py",
        '--source-type test --source-id eval_auto_test '
        '--title "AutoResearch评测测试条目" '
        '--content "Karpathy的AutoResearch核心思路：给AI目标和评判标准，让它自己迭代优化。关键：评判标准必须想清楚。" '
        '--ai-summary "AutoResearch评测用测试条目"')
    
    if not ok:
        return False, f"exit_code!=0: {err[:80]}"
    
    try:
        data = json.loads(out)
        if not data.get("success"):
            return False, f"success=false: {data.get('error','?')}"
        if not data.get("has_embedding"):
            return False, "no embedding generated"
        return True, f"id={data['id'][:8]}... {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_ai_summary():
    """测试2: 自动AI摘要（不手动指定）"""
    ok, out, err, dur = run_script("knowledge_save.py",
        '--source-type test --source-id eval_ai_summary_test '
        '--title "向量数据库选型测试条目" '
        '--content "对比了pgvector、Milvus、Weaviate三个向量数据库。pgvector最轻量适合小规模，Milvus性能最好适合大规模生产，Weaviate内置AI管道但较重。对于个人知识库，pgvector足够。"')
    
    if not ok:
        return False, f"save failed: {err[:80]}"
    
    try:
        data = json.loads(out)
        summary = data.get("ai_summary", "")
        if not summary or len(summary) < 5:
            return False, f"ai_summary too short or empty: '{summary}'"
        if "save failed" in summary.lower():
            return False, f"unexpected content: {summary[:50]}"
        return True, f"摘要: {summary[:40]}... {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_vector_search():
    """测试3: 向量语义搜索"""
    ok, out, err, dur = run_script("knowledge_search.py",
        '--query "如何让AI自动迭代优化" --mode vector --limit 3')
    
    if not ok:
        return False, f"search failed: {err[:80]}"
    
    try:
        data = json.loads(out)
        total = data.get("total", 0)
        if total == 0:
            return False, "no results returned"
        
        results = data.get("results", [])
        # 检查第一条结果的相关性
        top = results[0]
        sim = top.get("similarity", 0)
        title = top.get("title", "")
        
        if sim < 0.3:
            return False, f"low similarity: {sim:.3f} top={title[:30]}"
        
        return True, f"total={total} top_sim={sim:.3f} '{title[:25]}' {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_keyword_search():
    """测试4: 关键词搜索"""
    ok, out, err, dur = run_script("knowledge_search.py",
        '--query "AutoResearch" --mode keyword --limit 3')
    
    if not ok:
        return False, f"search failed: {err[:80]}"
    
    try:
        data = json.loads(out)
        total = data.get("total", 0)
        if total == 0:
            return False, "no results for 'AutoResearch'"
        
        titles = [r.get("title", "") for r in data.get("results", [])]
        has_match = any("AutoResearch" in t or "评测" in t for t in titles)
        if not has_match:
            return False, f"no relevant results: {titles}"
        
        return True, f"total={total} found relevant {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_hybrid_search():
    """测试5: 混合搜索（关键词+向量融合）"""
    ok, out, err, dur = run_script("knowledge_search.py",
        '--query "AutoResearch 知识" --mode hybrid --limit 5')
    
    if not ok:
        return False, f"search failed: {err[:80]}"
    
    try:
        data = json.loads(out)
        total = data.get("total", 0)
        if total == 0:
            return False, "hybrid search returned 0 results"
        
        results = data.get("results", [])
        # 混合搜索应该返回结果，且每个结果有 search_type 标记
        has_type = all("search_type" in r for r in results)
        if not has_type:
            return False, "results missing search_type field"
        
        # 至少要有 vector 结果（keyword 结果可能因去重不存在，数据量小时正常）
        has_vector = any(r["search_type"] == "vector" for r in results)
        if not has_vector:
            return False, "no vector results in hybrid search"
        
        return True, f"total={total} types={set(r['search_type'] for r in results)} {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_export():
    """测试6: agent 候选导出"""
    ok, out, err, dur = run_script(
        "knowledge_export.py",
        '--query "AutoResearch 知识" --mode hybrid --limit 3 --content-chars 300',
    )

    if not ok:
        return False, f"export failed: {err[:80]}"

    try:
        data = json.loads(out)
        results = data.get("results", [])
        if not results:
            return False, "no export results"

        top = results[0]
        required_fields = [
            "title",
            "source_type",
            "summary",
            "ai_summary",
            "content",
            "metadata",
        ]
        missing = [field for field in required_fields if field not in top]
        if missing:
            return False, f"missing fields: {missing}"

        if len(top.get("content", "")) > 303:
            return False, "content not truncated as expected"

        return True, f"fields ok top='{top.get('title', '')[:20]}' {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_deck_brief():
    """测试7: 生成知识卡片和 deck brief"""
    ok, out, err, dur = run_script(
        "knowledge_to_deck_brief.py",
        '--query "AutoResearch 知识" --mode hybrid --limit 4 --cards 2 --content-chars 300',
    )

    if not ok:
        return False, f"deck brief failed: {err[:80]}"

    try:
        data = json.loads(out)
        cards = data.get("knowledge_cards", [])
        deck_brief = data.get("deck_brief", {})
        slide_notes = deck_brief.get("slide_notes", [])

        if not cards:
            return False, "no knowledge cards"
        if not deck_brief:
            return False, "missing deck_brief"
        if len(slide_notes) < 4:
            return False, f"too few slide notes: {len(slide_notes)}"

        top_card = cards[0]
        required_card_fields = [
            "title",
            "takeaway",
            "why_it_matters",
            "evidence_or_example",
            "suggested_slide_type",
        ]
        missing = [field for field in required_card_fields if not top_card.get(field)]
        if missing:
            return False, f"missing card fields: {missing}"

        return True, f"cards={len(cards)} slides={len(slide_notes)} {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_candidate_review():
    """测试8: 候选体检结果"""
    ok, out, err, dur = run_script(
        "knowledge_candidate_review.py",
        '--query "向量数据库 选型" --mode hybrid --limit 4 --min-score 4 --output json',
    )

    if not ok:
        return False, f"candidate review failed: {err[:80]}"

    try:
        data = json.loads(out)
        results = data.get("results", [])
        if not results:
            return False, "no reviewed candidates"

        top = results[0]
        if "deck_score" not in top or "reasons" not in top:
            return False, "missing review fields"
        if not isinstance(top["reasons"], list) or not top["reasons"]:
            return False, "empty reasons"

        return True, f"reviewed={len(results)} top_score={top['deck_score']} {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_recipe_audit():
    """测试9: recipe 审计总览"""
    ok, out, err, dur = run_script(
        "knowledge_recipe_audit.py",
        '--recipes-dir docs/showcase/recipes --output json',
    )

    if not ok:
        return False, f"recipe audit failed: {err[:80]}"

    try:
        data = json.loads(out)
        if not isinstance(data, list) or not data:
            return False, "audit output empty"

        first = data[0]
        required_fields = [
            "title",
            "health",
            "source_profile",
            "readiness",
            "action",
            "avg_score",
            "ai_coverage",
        ]
        missing = [field for field in required_fields if field not in first]
        if missing:
            return False, f"missing audit fields: {missing}"

        return True, f"recipes={len(data)} first={first['health']} {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_pool_report():
    """测试10: 知识池快照"""
    ok, out, err, dur = run_script(
        "knowledge_pool_report.py",
        '--days 3650 --output json',
    )

    if not ok:
        return False, f"pool report failed: {err[:80]}"

    try:
        data = json.loads(out)
        required_fields = ["total_active_items", "source_breakdown", "weak_items", "next_actions"]
        missing = [field for field in required_fields if field not in data]
        if missing:
            return False, f"missing pool fields: {missing}"
        if not isinstance(data["next_actions"], list) or not data["next_actions"]:
            return False, "missing next actions"

        return True, f"items={data['total_active_items']} sources={len(data['source_breakdown'])} {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_backfill_ai_summary():
    """测试11: AI 摘要回填"""
    for attempt in range(2):
        ok, out, err, _ = run_script(
            "knowledge_save.py",
            '--source-type test --source-id eval_missing_ai_summary '
            '--title "缺失摘要回填测试" '
            '--content "这是一条用于测试 AI 摘要回填的知识内容，它应该在回填脚本里被补上一句话摘要。" '
            '--ai-summary ""',
        )

        if not ok:
            return False, f"seed save failed: {err[:80]}"

        ok, out, err, dur = run_script(
            "knowledge_backfill_ai_summary.py",
            '--source-type test --source-id eval_missing_ai_summary',
            timeout=90,
        )
        if not ok:
            if attempt == 0:
                continue
            return False, f"backfill failed: {err[:80]}"

        try:
            data = json.loads(out)
            updated = int(data.get("updated", 0))
            results = data.get("results", [])
            if updated < 1 or not results:
                if attempt == 0:
                    continue
                return False, f"no items updated: {data}"
            if not results[0].get("ai_summary"):
                if attempt == 0:
                    continue
                return False, "updated item missing ai_summary"

            return True, f"updated={updated} title='{results[0].get('title', '')[:16]}' {dur:.1f}s"
        except json.JSONDecodeError:
            if attempt == 0:
                continue
            return False, f"invalid json: {out[:80]}"

    return False, "backfill retry exhausted"


def test_seed_demo_items():
    """测试12: 演示知识种子"""
    for attempt in range(2):
        ok, out, err, dur = run_script(
            "knowledge_seed_demo_items.py",
            "",
            timeout=90,
        )
        if not ok:
            if attempt == 0:
                continue
            return False, f"seed demo failed: {err[:80]}"

        try:
            data = json.loads(out)
            results = data.get("results", [])
            if int(data.get("seeded", 0)) < 2 or len(results) < 2:
                if attempt == 0:
                    continue
                return False, f"seeded too few items: {data}"
            if not all(item.get("success") for item in results):
                if attempt == 0:
                    continue
                return False, f"seed failures: {results}"

            return True, f"seeded={len(results)} {dur:.1f}s"
        except json.JSONDecodeError:
            if attempt == 0:
                continue
            return False, f"invalid json: {out[:80]}"

    return False, "seed demo retry exhausted"


def test_ingest_markdown():
    """测试13: Markdown 文档导入预览"""
    ok, out, err, dur = run_script(
        "knowledge_ingest_markdown.py",
        "--path docs/agent-infra/knowledge-to-deck-agent-spec.md --dry-run",
        timeout=90,
    )
    if not ok:
        return False, f"ingest markdown failed: {err[:80]}"

    try:
        data = json.loads(out)
        if not isinstance(data, list) or not data:
            return False, "dry-run output empty"
        first = data[0]
        required_fields = ["source_type", "source_id", "title", "content", "metadata"]
        missing = [field for field in required_fields if field not in first]
        if missing:
            return False, f"missing fields: {missing}"
        if first.get("source_type") != "docs":
            return False, f"unexpected source_type: {first.get('source_type')}"
        if int(first.get("content_length", 0)) < 200:
            return False, f"content too short: {first.get('content_length')}"

        return True, f"title='{first.get('title', '')[:24]}' {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_wiki_review():
    """测试14: wiki review 快照"""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        wiki_root = Path(tmpdir)
        wiki_pages = wiki_root / "wiki"
        wiki_pages.mkdir(parents=True, exist_ok=True)

        (wiki_root / ".compile-state.json").write_text(
            json.dumps({"last_compile": "2026-05-17T00:00:00", "compiled_ids": ["a", "b", "c"]}),
            encoding="utf-8",
        )

        (wiki_pages / "source-demo.md").write_text(
            """---
type: source
title: Demo Source
date: 2026-05-17
---

# Demo Source

## 核心摘要
这是一个用于测试 wiki review 的 source 页面，它包含更长的正文内容，足以避免被误判成极薄页面。

## 知识图谱 (Knowledge Graph)
- **相关概念 (Concepts)**: [[concept-agent]]
- **相关实体 (Entities)**: [[entity-openai]]

## 内容片段
这里是一段更长的内容片段，用于模拟 source 页面被编译后的正文。
""",
            encoding="utf-8",
        )
        (wiki_pages / "concept-agent.md").write_text(
            """---
type: concept
title: Agent
date: 2026-05-17
---

# Agent

## 关联来源 (Mentions)
- [[source-demo]] (Demo Source)
""",
            encoding="utf-8",
        )
        (wiki_pages / "entity-openai.md").write_text(
            """---
type: entity
title: OpenAI
date: 2026-05-17
---

# OpenAI

## 关联来源 (Mentions)
- [[source-demo]] (Demo Source)
""",
            encoding="utf-8",
        )

        ok, out, err, dur = run_script(
            "knowledge_wiki_review.py",
            f'--wiki-dir "{wiki_root}" --output json',
        )

        if not ok:
            return False, f"wiki review failed: {err[:80]}"

        try:
            data = json.loads(out)
            required_fields = [
                "exists",
                "total_pages",
                "source_count",
                "concept_count",
                "entity_count",
                "recent_sources",
                "next_actions",
            ]
            missing = [field for field in required_fields if field not in data]
            if missing:
                return False, f"missing wiki review fields: {missing}"
            if not data.get("exists"):
                return False, "wiki dir should exist"
            if data.get("source_count") != 1:
                return False, f"unexpected source_count: {data.get('source_count')}"
            if not isinstance(data.get("next_actions"), list) or not data["next_actions"]:
                return False, "missing next actions"

            return True, f"pages={data['total_pages']} sources={data['source_count']} {dur:.1f}s"
        except json.JSONDecodeError:
            return False, f"invalid json: {out[:80]}"


def test_seed_wiki_docs():
    """测试15: wiki docs 种子 dry-run"""
    ok, out, err, dur = run_script(
        "knowledge_seed_wiki_docs_items.py",
        "--dry-run",
        timeout=90,
    )

    if not ok:
        return False, f"seed wiki docs failed: {err[:80]}"

    try:
        data = json.loads(out)
        if not isinstance(data, list) or len(data) < 4:
            return False, f"too few wiki docs seeds: {data}"

        first = data[0]
        required_fields = ["source_type", "source_id", "title", "content", "metadata"]
        missing = [field for field in required_fields if field not in first]
        if missing:
            return False, f"missing fields: {missing}"
        if first.get("source_type") != "docs":
            return False, f"unexpected source_type: {first.get('source_type')}"

        return True, f"seeded={len(data)} docs {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_memory_migrate():
    """测试16: memory_cards 表迁移"""
    ok, out, err, dur = run_script("memory_migrate.py", "", timeout=30)

    if not ok:
        return False, f"migrate failed: {err[:80]}"

    try:
        data = json.loads(out)
        if not data.get("success"):
            return False, f"success=false: {data.get('error', '?')}"
        columns = data.get("columns", [])
        if len(columns) < 15:
            return False, f"too few columns: {len(columns)}"
        required = {"layer", "title", "summary", "keywords", "embedding", "confidence"}
        col_names = {c["name"] for c in columns}
        missing = required - col_names
        if missing:
            return False, f"missing columns: {missing}"
        return True, f"columns={len(columns)} {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_memory_organize():
    """测试17: 记忆整理器（dry-run）"""
    ok, out, err, dur = run_script(
        "memory_organize.py",
        "--dry-run --limit 3",
        timeout=90,
    )

    if not ok:
        return False, f"organize failed: {err[:80]}"

    try:
        data = json.loads(out)
        if not data.get("success"):
            return False, f"success=false"
        results = data.get("results", [])
        if not results:
            return True, f"dry_run=0 candidates (pool may be fully organized) {dur:.1f}s"
        top = results[0]
        if "structured_summary" not in top:
            return False, "missing structured_summary"
        ss = top["structured_summary"]
        if "conclusion" not in ss or "keywords" not in ss:
            return False, "structured_summary missing fields"
        return True, f"candidates={data.get('candidates_found', 0)} organized={data.get('organized', 0)} {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_memory_recall():
    """测试18: 分层记忆检索"""
    ok, out, err, dur = run_script(
        "memory_recall.py",
        '--query "Agent" --mode hybrid --limit 5',
        timeout=60,
    )

    if not ok:
        return False, f"recall failed: {err[:80]}"

    try:
        data = json.loads(out)
        total = data.get("total", 0)
        if total == 0:
            return False, "no results from memory recall"

        results = data.get("results", [])
        layers = {r.get("layer") for r in results}
        stats = data.get("layer_stats", {})

        # 至少应有 L2 结果（前面 organize 过）
        if not layers.intersection({1, 2}):
            return False, f"no L1/L2 hits: layers={layers}"

        top = results[0]
        required_fields = ["id", "title", "summary", "keywords", "layer", "source"]
        missing = [f for f in required_fields if f not in top]
        if missing:
            return False, f"missing fields: {missing}"

        return True, f"total={total} L1={stats.get('l1',0)} L2={stats.get('l2',0)} L3={stats.get('l3',0)} {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_memory_save_working():
    """测试19: 写入 L1 工作记忆"""
    ok, out, err, dur = run_script(
        "memory_save_working.py",
        '--title "Eval Test Working Memory" '
        '--summary "This is a test working memory card for evaluation." '
        '--keywords "test,eval" '
        '--context-tags "project:eval" '
        '--ttl-days 1',
        timeout=60,
    )

    if not ok:
        return False, f"save working failed: {err[:80]}"

    try:
        data = json.loads(out)
        if not data.get("success"):
            return False, f"success=false: {data.get('error', '?')}"
        if data.get("layer") != 1:
            return False, f"wrong layer: {data.get('layer')}"
        if not data.get("id"):
            return False, "missing id"
        if not data.get("valid_until"):
            return False, "missing valid_until"

        return True, f"id={data['id'][:8]}... ttl={data['ttl_days']}d has_emb={data.get('has_embedding')} {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_memory_compress():
    """测试20: 记忆压缩（dry-run）"""
    ok, out, err, dur = run_script(
        "memory_compress.py",
        "--dry-run",
        timeout=30,
    )

    if not ok:
        return False, f"compress failed: {err[:80]}"

    try:
        data = json.loads(out)
        if not data.get("success"):
            return False, "success=false"
        steps = data.get("steps", [])
        if len(steps) < 3:
            return False, f"too few steps: {len(steps)}"
        required_actions = {"downgrade_l1_to_l2", "archive_cold_l2", "merge_similar_l2"}
        actions = {s.get("action") for s in steps}
        missing = required_actions - actions
        if missing:
            return False, f"missing steps: {missing}"
        summary = data.get("summary", {})
        return True, f"downgraded={summary.get('downgraded',0)} archived={summary.get('archived',0)} merged={summary.get('merged',0)} {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_memory_health():
    """测试21: 记忆健康度报告"""
    ok, out, err, dur = run_script(
        "memory_health.py",
        '--output json',
        timeout=30,
    )

    if not ok:
        return False, f"health failed: {err[:80]}"

    try:
        data = json.loads(out)
        required_fields = ["summary", "layer_stats", "source_coverage", "next_actions"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            return False, f"missing fields: {missing}"

        summary = data.get("summary", {})
        if "total_cards" not in summary or "active_cards" not in summary:
            return False, "summary missing metrics"

        layer_stats = data.get("layer_stats", {})
        if not layer_stats:
            return False, "empty layer_stats"

        return True, f"cards={summary.get('total_cards', 0)} coverage={summary.get('knowledge_coverage', 0)}% {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_memory_self_tune():
    """测试22: 记忆自进化调优 dry-run"""
    ok, out, err, dur = run_script(
        "memory_self_tune.py",
        "--dry-run",
        timeout=90,
    )

    if not ok:
        return False, f"self_tune failed: {err[:80]}"

    try:
        data = json.loads(out)
        if not data.get("dry_run"):
            return False, "dry_run != True"
        if "metrics" not in data:
            return False, "missing metrics"
        if "composite_score" not in data:
            return False, "missing composite_score"
        metrics = data.get("metrics", {})
        if len(metrics) < 6:
            return False, f"too few metrics: {len(metrics)}"
        return True, f"score={data['composite_score']} weakest={data.get('weakest_dimension','?')} {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_memory_self_tune_state():
    """测试23: 记忆自进化调优实际运行并生成状态文件"""
    ok, out, err, dur = run_script(
        "memory_self_tune.py",
        "",
        timeout=120,
    )

    if not ok:
        return False, f"self_tune failed: {err[:80]}"

    try:
        data = json.loads(out)
        # 验证状态文件被创建
        state_path = Path(SCRIPTS) / ".." / ".tune-state.json"
        if not state_path.exists():
            return False, ".tune-state.json not created"

        state = json.loads(state_path.read_text())
        if "current_params" not in state:
            return False, "state missing current_params"
        if "last_metrics" not in state:
            return False, "state missing last_metrics"

        action = data.get("action", "N/A")
        score = data.get("composite_score", 0)
        return True, f"action={action} score={score} state_ok {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_wiki_memory_link():
    """测试24: wiki_compile → memory_cards 双向关联回归测试（调用真实实现）"""
    import tempfile

    inline_script = r'''
# /// script
# requires-python = ">=3.10"
# dependencies = ["psycopg2-binary", "python-dotenv", "requests"]
# ///
import json, os, sys, time
from pathlib import Path

# 导入真实的 wiki_compile 模块（cwd = skills/knowledge-skill/）
sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
import wiki_compile

import psycopg2, psycopg2.extras
from dotenv import load_dotenv

load_dotenv(Path(".env"))
psycopg2.extras.register_uuid()

DB = {
    "host": os.getenv("DB_HOST", ""),
    "port": int(os.getenv("DB_PORT", 5433)),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "dbname": os.getenv("DB_NAME", ""),
}

conn = psycopg2.connect(**DB)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
start = time.time()

try:
    # Seed: source_card — 模拟从 knowledge_item 编译来的 memory_card
    cur.execute("""
        INSERT INTO memory_cards (layer, title, summary, keywords, context_tags, confidence, source_item_ids)
        VALUES (2, 'Wiki Link Test Source', 'Source card', ARRAY['Agent', 'RAG'], ARRAY['test:wiki_link'], 1.0, ARRAY['99999'])
        RETURNING id
    """)
    source_id = cur.fetchone()["id"]

    # Seed: match_card — 与概念关键词有交集的 memory_card
    cur.execute("""
        INSERT INTO memory_cards (layer, title, summary, keywords, context_tags, confidence)
        VALUES (2, 'Wiki Link Test Match', 'Match card', ARRAY['RAG', '向量数据库'], ARRAY['test:wiki_link'], 1.0)
        RETURNING id
    """)
    match_id = cur.fetchone()["id"]
    conn.commit()

    # 调用 wiki_compile.py 中的真实 link_wiki_to_memory_cards 函数
    linked = wiki_compile.link_wiki_to_memory_cards(99999, ["RAG"], [])

    # 验证双向关联
    cur.execute("SELECT related_card_ids FROM memory_cards WHERE id = %s", [source_id])
    source_rel = cur.fetchone()["related_card_ids"] or []
    cur.execute("SELECT related_card_ids FROM memory_cards WHERE id = %s", [match_id])
    match_rel = cur.fetchone()["related_card_ids"] or []
    bidirectional = (match_id in source_rel and source_id in match_rel)

    # 验证幂等：再次调用，关联不应重复
    linked2 = wiki_compile.link_wiki_to_memory_cards(99999, ["RAG"], [])
    cur.execute("SELECT related_card_ids FROM memory_cards WHERE id = %s", [source_id])
    final = cur.fetchone()["related_card_ids"] or []
    idempotent = sum(1 for x in final if x == match_id) == 1

    dur = time.time() - start
    print(json.dumps({
        "ok": bidirectional and idempotent,
        "detail": f"linked={linked} linked2={linked2} bidirectional={bidirectional} idempotent={idempotent} {dur:.1f}s"
    }))
except Exception as e:
    print(json.dumps({"ok": False, "detail": f"error: {str(e)[:80]}"}))
    sys.exit(0)
finally:
    try:
        cur.execute("DELETE FROM memory_cards WHERE context_tags @> ARRAY['test:wiki_link']")
        conn.commit()
    except Exception:
        pass
    cur.close()
    conn.close()
'''

    # 写入临时文件，通过 uv run 执行（eval.py 本身无 psycopg2 依赖）
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(inline_script)
        tmp_path = f.name

    try:
        start = time.time()
        r = subprocess.run(
            f"{VENV} {tmp_path}",
            shell=True, capture_output=True, text=True, timeout=30,
            cwd=str(Path(SCRIPTS).parent),
        )
        dur = time.time() - start
        out = r.stdout.strip()
        err = r.stderr.strip()

        try:
            data = json.loads(out)
            if not data.get("ok"):
                return False, data.get("detail", "unknown failure")
            return True, data.get("detail", "ok") + f" {dur:.1f}s"
        except json.JSONDecodeError:
            if err:
                return False, f"json error, stderr: {err[:60]}"
            return False, f"invalid json: {out[:80]}"
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    finally:
        os.unlink(tmp_path)


# 重量级测试集合（涉及多轮 DB 采集 + 实际调优，默认跳过）
HEAVY = {"test_22_memory_self_tune", "test_23_memory_self_tune_state"}

TESTS = [
    ("test_1_save", test_save),
    ("test_2_ai_summary", test_ai_summary),
    ("test_3_vector_search", test_vector_search),
    ("test_4_keyword_search", test_keyword_search),
    ("test_5_hybrid_search", test_hybrid_search),
    ("test_6_export", test_export),
    ("test_7_deck_brief", test_deck_brief),
    ("test_8_candidate_review", test_candidate_review),
    ("test_9_recipe_audit", test_recipe_audit),
    ("test_10_pool_report", test_pool_report),
    ("test_11_backfill_ai_summary", test_backfill_ai_summary),
    ("test_12_seed_demo_items", test_seed_demo_items),
    ("test_13_ingest_markdown", test_ingest_markdown),
    ("test_14_wiki_review", test_wiki_review),
    ("test_15_seed_wiki_docs", test_seed_wiki_docs),
    ("test_16_memory_migrate", test_memory_migrate),
    ("test_17_memory_organize", test_memory_organize),
    ("test_18_memory_recall", test_memory_recall),
    ("test_19_memory_save_working", test_memory_save_working),
    ("test_20_memory_compress", test_memory_compress),
    ("test_21_memory_health", test_memory_health),
    ("test_22_memory_self_tune", test_memory_self_tune),
    ("test_23_memory_self_tune_state", test_memory_self_tune_state),
    ("test_24_wiki_memory_link", test_wiki_memory_link),
]


# HEADER 由 TESTS 自动生成，保证三者始终一致
# TSV 列数始终固定（包含全部测试），跳过的测试标记 SKIP
HEADER = "\t".join(["timestamp", "passed", "total", "rate"] + [name for name, _ in TESTS] + ["notes"])


def main():
    parser = argparse.ArgumentParser(description="Knowledge Skill Eval")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--record", "-r", action="store_true", help="Append to results.tsv")
    parser.add_argument("--extended", "-e", action="store_true",
                        help="Include heavy tests (self_tune, etc.). Default: skip heavy tests for fast CI.")
    args = parser.parse_args()

    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    mode = "extended" if args.extended else "fast"
    print(f"{'='*55}")
    print(f"Knowledge Skill Eval — {ts} [{mode}]")
    print(f"{'='*55}")

    results = {}
    passed = 0

    for name, test_fn in TESTS:
        # 默认跳过重量级测试，--extended 才运行
        if not args.extended and name in HEAVY:
            results[name] = (None, "SKIP")
            print(f"  ⏭️  {name}: SKIP (use --extended to run)")
            continue

        ok, detail = test_fn()
        results[name] = (ok, detail)
        if ok:
            passed += 1
        status = "✅" if ok else "❌"
        print(f"  {status} {name}: {detail}")

    total = len(TESTS)
    rate = f"{passed}/{total} ({passed/total*100:.0f}%)"
    print(f"\n{'='*55}")
    print(f"结果: {rate}")
    print(f"{'='*55}")

    if args.record:
        # 由 TESTS 驱动 row 生成，保证与 HEADER 一一对应
        row = [ts, str(passed), str(total), rate]
        for name, _ in TESTS:
            ok, detail = results[name]
            if ok is None:
                row.append("SKIP")
            elif ok:
                row.append("PASS")
            else:
                row.append(f"FAIL:{detail[:30]}")
        row.append("")  # notes 列

        if not os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, "w") as f:
                f.write(HEADER + "\n")

        with open(RESULTS_FILE, "a") as f:
            f.write("\t".join(row) + "\n")
        print(f"📝 已记录到 eval_results.tsv")


if __name__ == "__main__":
    main()
