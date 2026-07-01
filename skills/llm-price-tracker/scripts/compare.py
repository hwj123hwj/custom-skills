#!/usr/bin/env python3
"""
Compare LLM pricing snapshots to detect price changes and new models.

Usage:
  python3 compare.py                    # Compare latest with previous snapshot
  python3 compare.py --days 7           # Compare latest with snapshot from 7 days ago
  python3 compare.py --from 2026-06-01 --to 2026-07-01
  python3 compare.py --format feishu    # Feishu-friendly output
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"


def find_snapshots() -> list[Path]:
    """List all snapshot files sorted by date."""
    if not SNAPSHOTS_DIR.exists():
        return []
    return sorted(SNAPSHOTS_DIR.glob("*.json"))


def find_snapshot_by_date(target_date: str) -> Path | None:
    """Find the snapshot closest to a target date."""
    snapshots = find_snapshots()
    if not snapshots:
        return None
    target = datetime.fromisoformat(target_date)
    best = None
    best_diff = None
    for s in snapshots:
        d = datetime.fromisoformat(s.stem)
        diff = abs((d - target).days)
        if best_diff is None or diff < best_diff:
            best = s
            best_diff = diff
    return best


def find_previous_snapshot(current: Path) -> Path | None:
    """Find the snapshot immediately before the given one."""
    snapshots = find_snapshots()
    for i, s in enumerate(snapshots):
        if s == current and i > 0:
            return snapshots[i - 1]
    return None


def compare(old_data: dict, new_data: dict) -> dict:
    """Compare two snapshots and return changes grouped by type."""
    changes = {
        "old_date": old_data.get("date", "unknown"),
        "new_date": new_data.get("date", "unknown"),
        "price_drops": [],
        "price_increases": [],
        "new_models": [],
        "removed_models": [],
        "new_providers": [],
    }

    old_providers = old_data.get("providers", {})
    new_providers = new_data.get("providers", {})

    # New providers
    for pid in new_providers:
        if pid not in old_providers:
            count = len(new_providers[pid].get("models", {}))
            changes["new_providers"].append({"id": pid, "name": new_providers[pid].get("name", pid), "models": count})

    for pid, pinfo in new_providers.items():
        old_pinfo = old_providers.get(pid, {})
        old_models = old_pinfo.get("models", {})
        new_models = pinfo.get("models", {})

        # New models
        for mid, model in new_models.items():
            if mid not in old_models:
                cost = model.get("cost", {})
                changes["new_models"].append({
                    "provider": pid,
                    "model_id": mid,
                    "model_name": model.get("name", mid),
                    "cost_input": cost.get("input"),
                    "cost_output": cost.get("output"),
                    "context": model.get("limit", {}).get("context"),
                })

        # Price changes
        for mid, model in new_models.items():
            if mid not in old_models:
                continue
            old_model = old_models[mid]
            old_cost = old_model.get("cost", {})
            new_cost = model.get("cost", {})

            for field in ["input", "output", "cache_read", "cache_write"]:
                old_val = old_cost.get(field)
                new_val = new_cost.get(field)
                if old_val and new_val and old_val != new_val:
                    entry = {
                        "provider": pid,
                        "model_id": mid,
                        "model_name": model.get("name", mid),
                        "field": field,
                        "old": old_val,
                        "new": new_val,
                        "delta": new_val - old_val,
                        "pct": round((new_val - old_val) / old_val * 100, 1),
                    }
                    if new_val < old_val:
                        changes["price_drops"].append(entry)
                    else:
                        changes["price_increases"].append(entry)

    # Removed models
    for pid, pinfo in old_providers.items():
        if pid not in new_providers:
            continue
        new_models = new_providers[pid].get("models", {})
        for mid in pinfo.get("models", {}):
            if mid not in new_models:
                changes["removed_models"].append({"provider": pid, "model_id": mid})

    return changes


def format_changes(changes: dict) -> str:
    """Format changes as a readable report."""
    lines = [f"# LLM Price Changes", f"{changes['old_date']} → {changes['new_date']}", ""]

    # Price drops
    if changes["price_drops"]:
        lines.append(f"## ⬇️ Price Drops ({len(changes['price_drops'])})")
        for c in sorted(changes["price_drops"], key=lambda x: x["pct"]):
            lines.append(f"- {c['provider']}/{c['model_id']} {c['field']}: ${c['old']:.2f} → ${c['new']:.2f} ({c['pct']:+.1f}%)")

    # Price increases
    if changes["price_increases"]:
        lines.append(f"\n## ⬆️ Price Increases ({len(changes['price_increases'])})")
        for c in sorted(changes["price_increases"], key=lambda x: -x["pct"]):
            lines.append(f"- {c['provider']}/{c['model_id']} {c['field']}: ${c['old']:.2f} → ${c['new']:.2f} ({c['pct']:+.1f}%)")

    # New models
    if changes["new_models"]:
        lines.append(f"\n## 🆕 New Models ({len(changes['new_models'])})")
        for m in sorted(changes["new_models"], key=lambda x: x["cost_output"] or 9999):
            inp = f"${m['cost_input']:.2f}" if m['cost_input'] else "?"
            out = f"${m['cost_output']:.2f}" if m['cost_output'] else "?"
            lines.append(f"- {m['provider']}/{m['model_id']} — in:{inp} out:{out}")

    # New providers
    if changes["new_providers"]:
        lines.append(f"\n## 🏢 New Providers ({len(changes['new_providers'])})")
        for p in changes["new_providers"]:
            lines.append(f"- {p['id']} ({p['name']}): {p['models']} models")

    # Removed
    if changes["removed_models"]:
        lines.append(f"\n## ❌ Removed Models ({len(changes['removed_models'])})")
        for m in changes["removed_models"][:10]:
            lines.append(f"- {m['provider']}/{m['model_id']}")

    if not any([changes["price_drops"], changes["price_increases"], changes["new_models"], changes["new_providers"]]):
        lines.append("No significant changes detected.")

    return "\n".join(lines)


def format_feishu(changes: dict) -> str:
    """Compact Feishu-friendly format."""
    lines = ["**LLM 价格变动报告**\n"]

    drops = len(changes["price_drops"])
    increases = len(changes["price_increases"])
    new_m = len(changes["new_models"])
    new_p = len(changes["new_providers"])

    lines.append(f"📅 {changes['old_date']} → {changes['new_date']}")
    lines.append(f"⬇️ 降价: {drops} | ⬆️ 涨价: {increases} | 🆕 新模型: {new_m} | 🏢 新供应商: {new_p}\n")

    if changes["price_drops"]:
        lines.append("**降价 TOP 5:**")
        for c in sorted(changes["price_drops"], key=lambda x: x["pct"])[:5]:
            lines.append(f"• {c['provider']}/{c['model_id']} {c['field']}: {c['pct']:+.1f}% (${c['old']:.2f}→${c['new']:.2f})")

    if changes["new_models"]:
        lines.append(f"\n**新模型 ({new_m}):**")
        for m in sorted(changes["new_models"], key=lambda x: x["cost_output"] or 9999)[:5]:
            lines.append(f"• {m['provider']}/{m['model_id']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Compare LLM pricing snapshots")
    parser.add_argument("--days", type=int, help="Compare latest with snapshot N days ago")
    parser.add_argument("--from", dest="from_date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", dest="to_date", help="End date (YYYY-MM-DD, default: latest)")
    parser.add_argument("--format", choices=["report", "feishu", "json"], default="report")
    args = parser.parse_args()

    snapshots = find_snapshots()
    if len(snapshots) < 1:
        print("No snapshots found. Run fetch.py first.", file=sys.stderr)
        sys.exit(1)

    # Determine old/new snapshots
    new_path = snapshots[-1]  # latest

    if args.from_date:
        old_path = find_snapshot_by_date(args.from_date)
        if not old_path:
            print(f"No snapshot found near {args.from_date}", file=sys.stderr)
            sys.exit(1)
    elif args.days:
        target_date = datetime.now(timezone.utc) - timedelta(days=args.days)
        old_path = find_snapshot_by_date(target_date.isoformat())
        if not old_path:
            print(f"No snapshot found from {args.days} days ago", file=sys.stderr)
            sys.exit(1)
    else:
        old_path = find_previous_snapshot(new_path)
        if not old_path:
            print("Only one snapshot exists. Need at least 2 for comparison.", file=sys.stderr)
            sys.exit(1)

    if args.to_date:
        new_path_candidate = find_snapshot_by_date(args.to_date)
        if new_path_candidate:
            new_path = new_path_candidate

    old_data = json.loads(old_path.read_text())
    new_data = json.loads(new_path.read_text())

    changes = compare(old_data, new_data)

    if args.format == "json":
        print(json.dumps(changes, indent=2, ensure_ascii=False))
    elif args.format == "feishu":
        print(format_feishu(changes))
    else:
        print(format_changes(changes))


if __name__ == "__main__":
    main()
