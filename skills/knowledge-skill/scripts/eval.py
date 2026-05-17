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

HEADER = "timestamp\tpassed\ttotal\trate\ttest_1_save\ttest_2_ai_summary\ttest_3_vector_search\ttest_4_keyword_search\ttest_5_hybrid_search\ttest_6_export\ttest_7_deck_brief\ttest_8_candidate_review\ttest_9_recipe_audit\ttest_10_pool_report\ttest_11_backfill_ai_summary\ttest_12_seed_demo_items\tnotes"


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
        '--source-type test --source-id eval_auto '
        '--title "AutoResearch评测条目" '
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
        '--source-type test --source-id eval_ai_summary '
        '--title "向量数据库选型对比" '
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
        required_fields = ["title", "health", "action", "avg_score", "ai_coverage"]
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
    ok, out, err, dur = run_script(
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
        return False, f"backfill failed: {err[:80]}"

    try:
        data = json.loads(out)
        updated = int(data.get("updated", 0))
        results = data.get("results", [])
        if updated < 1 or not results:
            return False, f"no items updated: {data}"
        if not results[0].get("ai_summary"):
            return False, "updated item missing ai_summary"

        return True, f"updated={updated} title='{results[0].get('title', '')[:16]}' {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


def test_seed_demo_items():
    """测试12: 演示知识种子"""
    ok, out, err, dur = run_script(
        "knowledge_seed_demo_items.py",
        "",
        timeout=90,
    )
    if not ok:
        return False, f"seed demo failed: {err[:80]}"

    try:
        data = json.loads(out)
        results = data.get("results", [])
        if int(data.get("seeded", 0)) < 2 or len(results) < 2:
            return False, f"seeded too few items: {data}"
        if not all(item.get("success") for item in results):
            return False, f"seed failures: {results}"

        return True, f"seeded={len(results)} {dur:.1f}s"
    except json.JSONDecodeError:
        return False, f"invalid json: {out[:80]}"


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
]


def main():
    parser = argparse.ArgumentParser(description="Knowledge Skill Eval")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--record", "-r", action="store_true", help="Append to results.tsv")
    args = parser.parse_args()
    
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"{'='*55}")
    print(f"Knowledge Skill Eval — {ts}")
    print(f"{'='*55}")
    
    results = {}
    passed = 0
    
    for name, test_fn in TESTS:
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
        # 写入 TSV
        if not os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, "w") as f:
                f.write(HEADER + "\n")
        
        row = [
            ts,
            str(passed),
            str(total),
            rate,
            "PASS" if results["test_1_save"][0] else f"FAIL:{results['test_1_save'][1][:30]}",
            "PASS" if results["test_2_ai_summary"][0] else f"FAIL:{results['test_2_ai_summary'][1][:30]}",
            "PASS" if results["test_3_vector_search"][0] else f"FAIL:{results['test_3_vector_search'][1][:30]}",
            "PASS" if results["test_4_keyword_search"][0] else f"FAIL:{results['test_4_keyword_search'][1][:30]}",
            "PASS" if results["test_5_hybrid_search"][0] else f"FAIL:{results['test_5_hybrid_search'][1][:30]}",
            "PASS" if results["test_6_export"][0] else f"FAIL:{results['test_6_export'][1][:30]}",
            "PASS" if results["test_7_deck_brief"][0] else f"FAIL:{results['test_7_deck_brief'][1][:30]}",
            "PASS" if results["test_8_candidate_review"][0] else f"FAIL:{results['test_8_candidate_review'][1][:30]}",
            "PASS" if results["test_9_recipe_audit"][0] else f"FAIL:{results['test_9_recipe_audit'][1][:30]}",
            "PASS" if results["test_10_pool_report"][0] else f"FAIL:{results['test_10_pool_report'][1][:30]}",
            "PASS" if results["test_11_backfill_ai_summary"][0] else f"FAIL:{results['test_11_backfill_ai_summary'][1][:30]}",
            "PASS" if results["test_12_seed_demo_items"][0] else f"FAIL:{results['test_12_seed_demo_items'][1][:30]}",
            "",
        ]
        with open(RESULTS_FILE, "a") as f:
            f.write("\t".join(row) + "\n")
        print(f"📝 已记录到 eval_results.tsv")


if __name__ == "__main__":
    main()
