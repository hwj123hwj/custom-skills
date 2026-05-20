#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "psycopg2-binary",
#     "python-dotenv",
#     "requests",
# ]
# ///
"""
记忆自进化调优器
参考 darwin-skill 紫金花机制：棘轮 + 爬山 + TSV 追踪。
每次只调一个参数，对比调优前后六维健康指标，不改善则回退。

用法:
  uv run scripts/memory_self_tune.py --dry-run
  uv run scripts/memory_self_tune.py
  uv run scripts/memory_self_tune.py --force
"""

import argparse
import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

load_dotenv(Path(__file__).parent.parent / ".env")
load_dotenv(Path(__file__).parent.parent / ".tune-params.env")


def log(msg: str = ""):
    """所有进度信息走 stderr，stdout 只输出 JSON"""
    print(msg, file=sys.stderr)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", ""),
    "port": int(os.getenv("DB_PORT", 5433)),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "dbname": os.getenv("DB_NAME", ""),
}

SKILL_DIR = Path(__file__).parent.parent
STATE_FILE = SKILL_DIR / ".tune-state.json"
TSV_FILE = SKILL_DIR / "tune-results.tsv"
PARAMS_ENV_FILE = SKILL_DIR / ".tune-params.env"

# --- 六维指标定义 ---
METRIC_DEFS = {
    "l1_hit_rate":       {"label": "L1 命中率",     "direction": "up"},
    "l2_hit_rate":       {"label": "L2 命中率",     "direction": "up"},
    "l3_fallback_rate":  {"label": "L3 回退率",     "direction": "down"},
    "coverage_rate":     {"label": "覆盖率",        "direction": "up"},
    "cold_ratio":        {"label": "冷门率",        "direction": "down"},
    "duplicate_ratio":   {"label": "疑似重复率",    "direction": "down"},
}

# --- 可调参数定义 ---
PARAM_DEFS = {
    "l1_expire_days": {
        "env_key": "MEMORY_L1_EXPIRE_DAYS",
        "current": 7,
        "low": 3, "high": 14,
        "step": 1,
        "affects": "l1_hit_rate",
        "file_hint": "memory_compress.py",
    },
    "l2_archive_days": {
        "env_key": "MEMORY_L2_ARCHIVE_DAYS",
        "current": 90,
        "low": 30, "high": 180,
        "step": 10,
        "affects": "coverage_rate",
        "file_hint": "memory_compress.py",
    },
    "merge_similarity": {
        "env_key": "MEMORY_MERGE_SIMILARITY",
        "current": 0.95,
        "low": 0.85, "high": 0.99,
        "step": 0.02,
        "affects": "duplicate_ratio",
        "file_hint": "memory_compress.py",
    },
    "organize_min_content": {
        "env_key": "MEMORY_ORGANIZE_MIN_CONTENT",
        "current": 180,
        "low": 50, "high": 500,
        "step": 30,
        "affects": "coverage_rate",
        "file_hint": "memory_organize.py",
    },
    "dedup_threshold": {
        "env_key": "MEMORY_DEDUP_THRESHOLD",
        "current": 0.95,
        "low": 0.85, "high": 0.99,
        "step": 0.02,
        "affects": "duplicate_ratio",
        "file_hint": "memory_organize.py",
    },
}

# --- 诊断查询（用于低召回检测） ---
DIAGNOSTIC_QUERIES = [
    "Agent", "RAG", "向量数据库", "Docker", "Python",
    "知识库", "自动化", "LLM", "开源", "框架",
]


# ==================== 指标采集 ====================

def _db_query(sql: str, params: list | None = None) -> list[dict]:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def _count_active_cards() -> int:
    rows = _db_query("SELECT COUNT(*) AS n FROM memory_cards WHERE confidence > 0")
    return int(rows[0]["n"]) if rows else 0


def collect_metrics() -> dict[str, float]:
    """从数据库采集六维健康指标"""
    metrics: dict[str, float] = {}

    total_cards = _count_active_cards()

    # L1/L2/L3 各层卡片数
    layer_rows = _db_query(
        "SELECT layer, COUNT(*) AS n FROM memory_cards WHERE confidence > 0 GROUP BY layer"
    )
    layer_counts = {row["layer"]: int(row["n"]) for row in layer_rows}
    l1_count = layer_counts.get(1, 0)
    l2_count = layer_counts.get(2, 0)

    # L1 命中率：L1 卡中有 embedding 的比例（proxy for "可检索"）
    emb_rows = _db_query(
        "SELECT COUNT(*) AS n FROM memory_cards WHERE confidence > 0 AND layer = 1 AND embedding IS NOT NULL"
    )
    l1_with_emb = int(emb_rows[0]["n"]) if emb_rows else 0
    metrics["l1_hit_rate"] = l1_with_emb / l1_count if l1_count > 0 else 0.0

    # L2 命中率：L2 卡中有 embedding 的比例
    emb_rows_l2 = _db_query(
        "SELECT COUNT(*) AS n FROM memory_cards WHERE confidence > 0 AND layer = 2 AND embedding IS NOT NULL"
    )
    l2_with_emb = int(emb_rows_l2[0]["n"]) if emb_rows_l2 else 0
    metrics["l2_hit_rate"] = l2_with_emb / l2_count if l2_count > 0 else 0.0

    # L3 回退率：如果有 knowledge_items 但没有对应 memory_card 的比例
    ki_rows = _db_query("SELECT COUNT(*) AS n FROM knowledge_items WHERE status = 'active'")
    ki_total = int(ki_rows[0]["n"]) if ki_rows else 0
    organized_rows = _db_query(
        """
        SELECT COUNT(DISTINCT ki.id) AS n
        FROM knowledge_items ki
        JOIN memory_cards mc ON ki.id::text = ANY(mc.source_item_ids) AND mc.confidence > 0
        WHERE ki.status = 'active'
        """
    )
    organized = int(organized_rows[0]["n"]) if organized_rows else 0
    metrics["l3_fallback_rate"] = 1.0 - (organized / ki_total) if ki_total > 0 else 0.0

    # 覆盖率
    metrics["coverage_rate"] = (organized / ki_total * 100) if ki_total > 0 else 0.0

    # 冷门率：access_count=0 且 >30 天的活跃卡片占比
    cold_rows = _db_query(
        """
        SELECT COUNT(*) AS n FROM memory_cards
        WHERE confidence > 0 AND access_count = 0
          AND created_at < NOW() - INTERVAL '30 days'
        """
    )
    cold_count = int(cold_rows[0]["n"]) if cold_rows else 0
    metrics["cold_ratio"] = cold_count / total_cards if total_cards > 0 else 0.0

    # 疑似重复率：similarity > 0.90 的卡片对数 / 总卡片数
    dup_rows = _db_query(
        """
        SELECT COUNT(*) AS n
        FROM memory_cards a
        JOIN memory_cards b ON a.id < b.id
        WHERE a.embedding IS NOT NULL AND b.embedding IS NOT NULL
          AND a.confidence > 0 AND b.confidence > 0
          AND 1 - (a.embedding <=> b.embedding) > 0.90
        """
    )
    dup_pairs = int(dup_rows[0]["n"]) if dup_rows else 0
    metrics["duplicate_ratio"] = dup_pairs / total_cards if total_cards > 0 else 0.0

    return metrics


def calculate_composite_score(metrics: dict[str, float]) -> float:
    """综合分（满分 100）"""
    l1 = metrics.get("l1_hit_rate", 0)
    l2 = metrics.get("l2_hit_rate", 0)
    l3_fb = metrics.get("l3_fallback_rate", 0)
    cov = metrics.get("coverage_rate", 0)
    cold = metrics.get("cold_ratio", 0)
    dup = metrics.get("duplicate_ratio", 0)

    score = (
        l1 * 20                            # 满分 20
        + l2 * 25                          # 满分 25
        + (1 - l3_fb) * 20                 # 满分 20
        + min(cov / 50, 1.0) * 20          # 满分 20（50% 覆盖率算满分）
        + (1 - cold) * 8                   # 满分 8
        + (1 - dup) * 7                    # 满分 7
    )
    return round(score, 2)


# ==================== 状态管理 ====================

def load_tune_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "version": 1,
        "current_params": {k: v["current"] for k, v in PARAM_DEFS.items()},
        "last_metrics": {},
        "metric_history": [],
        "last_tune": None,
    }


def save_tune_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def append_tsv_record(
    param_old: str, param_new: str, weakest: str,
    old_score: float, new_score: float, status: str, note: str
):
    """追加一行调优记录到 TSV"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    header_needed = not TSV_FILE.exists()
    with open(TSV_FILE, "a", encoding="utf-8") as f:
        if header_needed:
            f.write("timestamp\tparam_old\tparam_new\tweakest_dim\told_score\tnew_score\tstatus\tnote\n")
        f.write(f"{ts}\t{param_old}\t{param_new}\t{weakest}\t{old_score}\t{new_score}\t{status}\t{note}\n")


# ==================== 爬山调优 ====================

def find_weakest_dimension(metrics: dict[str, float]) -> str:
    """找到最需要改进的维度（爬山起点）"""
    worst_dim = None
    worst_score = float("inf")

    for dim, defn in METRIC_DEFS.items():
        val = metrics.get(dim, 0)
        if defn["direction"] == "up":
            # 越高越好，找最低的
            if val < worst_score:
                worst_score = val
                worst_dim = dim
        else:
            # 越低越好，找最高的
            effective = -val  # 取反比较
            if effective < worst_score:
                worst_score = effective
                worst_dim = dim

    return worst_dim or "l3_fallback_rate"


def propose_param_adjustment(weakest: str, current_params: dict) -> tuple[str, Any, Any]:
    """
    根据最差维度，建议调整哪个参数、调整到什么值。
    返回 (param_key, old_value, new_value)。
    """
    # 建立 weakest → param 映射
    for pkey, pdef in PARAM_DEFS.items():
        if pdef["affects"] == weakest:
            current_val = current_params.get(pkey, pdef["current"])
            # 数字类型判断
            step = pdef["step"]
            if isinstance(step, float) or isinstance(current_val, float):
                step = float(step)
                # 随机方向（+ 或 -）
                direction = 1 if current_val - step >= pdef["low"] else 1
                new_val = round(current_val + direction * step, 2)
                if new_val > pdef["high"]:
                    new_val = round(current_val - step, 2)
                if new_val < pdef["low"]:
                    return pkey, current_val, current_val  # 已到边界
            else:
                step = int(step)
                direction = 1 if current_val - step >= pdef["low"] else 1
                new_val = current_val + direction * step
                if new_val > pdef["high"]:
                    new_val = current_val - step
                if new_val < pdef["low"]:
                    return pkey, current_val, current_val  # 已到边界
            return pkey, current_val, new_val

    # fallback: 调 l2_archive_days
    pkey = "l2_archive_days"
    current_val = current_params.get(pkey, 90)
    return pkey, current_val, current_val + 10


def apply_params_to_env(params: dict):
    """将参数写入 .tune-params.env 供 compress/organize 读取"""
    lines = []
    for k, v in params.items():
        pdef = PARAM_DEFS.get(k, {})
        env_key = pdef.get("env_key", f"MEMORY_{k.upper()}")
        lines.append(f"{env_key}={v}")
    PARAMS_ENV_FILE.write_text("\n".join(lines) + "\n")
    log(f"  ✅ 参数已写入 {PARAMS_ENV_FILE.name}")


def run_diagnostic_queries() -> list[dict[str, Any]]:
    """运行预设查询，收集各层命中情况"""
    results = []

    for query in DIAGNOSTIC_QUERIES:
        try:
            # L1+L2 命中
            l1_l2_rows = _db_query(
                """
                SELECT COUNT(*) AS n FROM memory_cards
                WHERE confidence > 0 AND layer IN (1, 2)
                  AND (
                    title ILIKE %s
                    OR summary ILIKE %s
                    OR %s = ANY(keywords)
                  )
                """,
                [f"%{query}%", f"%{query}%", query],
            )
            l1_l2_hits = int(l1_l2_rows[0]["n"]) if l1_l2_rows else 0

            # L3 命中
            l3_rows = _db_query(
                """
                SELECT COUNT(*) AS n FROM knowledge_items
                WHERE status = 'active'
                  AND (
                    title ILIKE %s
                    OR content ILIKE %s
                    OR ai_summary ILIKE %s
                  )
                """,
                [f"%{query}%", f"%{query}%", f"%{query}%"],
            )
            l3_hits = int(l3_rows[0]["n"]) if l3_rows else 0

            if l1_l2_hits < 2 and l3_hits > 0:
                # 找到缺口：L3 有内容但 L1/L2 没有
                gap_items = _db_query(
                    """
                    SELECT id, title FROM knowledge_items
                    WHERE status = 'active'
                      AND (title ILIKE %s OR content ILIKE %s)
                    ORDER BY created_at DESC LIMIT 3
                    """,
                    [f"%{query}%", f"%{query}%"],
                )
                results.append({
                    "query": query,
                    "l1_l2_hits": l1_l2_hits,
                    "l3_hits": l3_hits,
                    "item_ids": [str(row["id"]) for row in gap_items],
                })
        except Exception as e:
            log(f"  ⚠️ 诊断查询 '{query}' 失败: {e}")

    return results


# ==================== 主调优流程 ====================

def tune(dry_run: bool = False, force: bool = False) -> dict:
    """主调优循环：采集 → 评估 → 调整 → 验证 → 保留/回退"""
    log("=" * 50)
    log(f"🧬 记忆自进化调优 — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log("=" * 50)

    state = load_tune_state()
    current_params = dict(state.get("current_params", {k: v["current"] for k, v in PARAM_DEFS.items()}))

    # 1. 采集当前指标
    log("\n📊 采集六维健康指标...")
    metrics = collect_metrics()
    composite = calculate_composite_score(metrics)
    log(f"  综合分: {composite}/100")

    for dim, val in metrics.items():
        defn = METRIC_DEFS.get(dim, {})
        arrow = "↑" if defn.get("direction") == "up" else "↓"
        val_str = f"{val*100:.1f}%" if val <= 1.0 else f"{val:.1f}%"
        log(f"  {defn.get('label', dim):12s} {val_str:10s} {arrow}")

    # 2. 找到最差维度
    weakest = find_weakest_dimension(metrics)
    weakest_label = METRIC_DEFS.get(weakest, {}).get("label", weakest)
    log(f"\n🎯 最差维度: {weakest_label} ({weakest})")

    if dry_run:
        # dry-run 也输出低召回检测
        gaps = run_diagnostic_queries()
        if gaps:
            log(f"\n🔍 低召回缺口: {len(gaps)} 个查询")
            for g in gaps:
                log(f"  - '{g['query']}': L1+L2={g['l1_l2_hits']}, L3={g['l3_hits']}")

        return {
            "dry_run": True,
            "metrics": metrics,
            "composite_score": composite,
            "weakest_dimension": weakest,
            "current_params": current_params,
            "low_recall_gaps": gaps,
        }

    # 3. 检查是否需要调优（综合分 > 80 且无低召回则跳过）
    last_score = state.get("last_metrics", {}).get("composite_score", 0)
    gaps = run_diagnostic_queries()

    if composite >= 80 and not gaps and not force:
        log(f"\n✅ 综合分已达 {composite}，系统健康，无需调优。")
        log("   使用 --force 强制调优。")
        return {
            "dry_run": False,
            "metrics": metrics,
            "composite_score": composite,
            "action": "skip",
            "reason": "score >= 80 and no gaps",
        }

    # 4. 提出参数调整
    pkey, old_val, new_val = propose_param_adjustment(weakest, current_params)
    if old_val == new_val:
        log(f"\n⚠️ 参数 {pkey} 已到边界，无法继续调整。")
        return {
            "dry_run": False,
            "metrics": metrics,
            "composite_score": composite,
            "action": "boundary",
            "param": pkey,
        }

    param_label = f"{pkey}={old_val}"
    param_new_label = f"{pkey}={new_val}"
    log(f"\n🔧 建议调整: {param_label} → {param_new_label}")
    log(f"   目标: 改善 {weakest_label}")

    # 5. 保存参数快照
    snapshot_params = dict(current_params)

    # 6. 应用新参数
    current_params[pkey] = new_val
    apply_params_to_env(current_params)

    # 7. 重新采集指标
    log("\n📊 重新采集指标...")
    new_metrics = collect_metrics()
    new_composite = calculate_composite_score(new_metrics)
    log(f"  新综合分: {new_composite}/100 (旧: {composite})")

    # 8. 对比：棘轮机制 — 只保留改善
    score_diff = new_composite - composite
    if score_diff >= 0:
        # keep
        status = "keep"
        note = f"综合分 {composite}→{new_composite} (+{score_diff:.1f})"
        state["current_params"] = current_params
        log(f"  ✅ 保留新参数 — {note}")
    else:
        # revert
        status = "revert"
        note = f"综合分 {composite}→{new_composite} ({score_diff:.1f})"
        current_params = snapshot_params
        apply_params_to_env(current_params)
        state["current_params"] = current_params
        log(f"  ↩️  回退参数 — {note}")

    # 9. 记录到 TSV
    append_tsv_record(param_label, param_new_label, weakest, composite, new_composite, status, note)

    # 10. 更新状态
    state["last_metrics"] = {
        **new_metrics,
        "composite_score": new_composite,
    }
    state["metric_history"].append({
        "date": datetime.now().isoformat(),
        "metrics": new_metrics,
        "params": dict(current_params),
        "composite_score": new_composite,
    })
    state["last_tune"] = datetime.now().isoformat()
    save_tune_state(state)

    # 11. 低召回缺口提示
    if gaps:
        log(f"\n🔍 低召回缺口: {len(gaps)} 个查询需要补充提取")
        for g in gaps[:5]:
            log(f"  - '{g['query']}': L1+L2={g['l1_l2_hits']}, L3={g['l3_hits']}")
        log("  💡 运行 memory_organize.py 补充提取: uv run scripts/memory_organize.py --limit 10")

    log(f"\n📝 调优记录已追加到 {TSV_FILE.name}")

    return {
        "dry_run": False,
        "metrics": new_metrics,
        "composite_score": new_composite,
        "old_composite_score": composite,
        "action": status,
        "param_changed": pkey,
        "old_value": old_val,
        "new_value": new_val,
        "weakest_dimension": weakest,
        "low_recall_gaps": gaps,
        "tune_status": status,
    }


def main():
    parser = argparse.ArgumentParser(description="记忆自进化调优器（紫金花机制）")
    parser.add_argument("--dry-run", action="store_true", help="只采集指标，不调参")
    parser.add_argument("--force", action="store_true", help="即使综合分 >= 80 也强制调优")
    parser.add_argument("--output", choices=["json", "markdown"], default="json")
    args = parser.parse_args()

    result = tune(dry_run=args.dry_run, force=args.force)

    if args.output == "markdown":
        lines = ["# Memory Self-Tune Report", ""]
        lines.append(f"- Generated: {datetime.now().isoformat()}")
        lines.append(f"- Action: {result.get('action', 'N/A')}")
        lines.append(f"- Composite Score: {result.get('composite_score', 0)}/100")
        lines.append("")
        if "metrics" in result:
            lines.append("## Metrics")
            lines.append("")
            for dim, val in result["metrics"].items():
                defn = METRIC_DEFS.get(dim, {})
                val_str = f"{val*100:.1f}%" if val <= 1.0 else f"{val:.1f}%"
                lines.append(f"- {defn.get('label', dim)}: {val_str}")
            lines.append("")
        if result.get("low_recall_gaps"):
            lines.append("## Low Recall Gaps")
            lines.append("")
            for g in result["low_recall_gaps"]:
                lines.append(f"- '{g['query']}': L1+L2={g['l1_l2_hits']}, L3={g['l3_hits']}")
            lines.append("")
        print("\n".join(lines))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
