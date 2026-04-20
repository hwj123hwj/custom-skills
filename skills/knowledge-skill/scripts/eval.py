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

HEADER = "timestamp\tpassed\ttotal\trate\ttest_1_save\ttest_2_ai_summary\ttest_3_vector_search\ttest_4_keyword_search\ttest_5_hybrid_search\tnotes"


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


TESTS = [
    ("test_1_save", test_save),
    ("test_2_ai_summary", test_ai_summary),
    ("test_3_vector_search", test_vector_search),
    ("test_4_keyword_search", test_keyword_search),
    ("test_5_hybrid_search", test_hybrid_search),
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
            "",
        ]
        with open(RESULTS_FILE, "a") as f:
            f.write("\t".join(row) + "\n")
        print(f"📝 已记录到 eval_results.tsv")


if __name__ == "__main__":
    main()
