#!/usr/bin/env python3
"""
LLM Price Tracker - Fetch prices from providers and aggregators.

Usage:
  python fetch_prices.py                  # Fetch all providers
  python fetch_prices.py --provider deepseek  # Fetch specific provider
  python fetch_prices.py --compare        # Compare with last snapshot

Output: data/snapshots/YYYY-MM-DD.json + data/latest.json
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"

# All known provider pricing URLs
PROVIDERS = {
    "deepseek": {
        "url": "https://api-docs.deepseek.com/zh-cn/quick_start/pricing",
        "currency": "CNY",
    },
    "openai": {
        "url": "https://openai.com/api/pricing/",
        "currency": "USD",
    },
    "anthropic": {
        "url": "https://www.anthropic.com/pricing",
        "currency": "USD",
    },
    "google": {
        "url": "https://ai.google.dev/pricing",
        "currency": "USD",
    },
    "siliconflow": {
        "url": "https://siliconflow.cn/pricing",
        "currency": "CNY",
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/models",
        "currency": "USD",
        "type": "json_api",
    },
}

AGGREGATORS = {
    "pricepertoken": {
        "url_template": "https://pricepertoken.com/pricing-page/provider/{provider}",
    },
}


def ensure_dirs():
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def load_latest() -> dict:
    latest_path = DATA_DIR / "latest.json"
    if latest_path.exists():
        return json.loads(latest_path.read_text())
    return {"date": None, "providers": {}}


def save_snapshot(data: dict):
    date_str = data["date"]
    snapshot_path = SNAPSHOTS_DIR / f"{date_str}.json"
    snapshot_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    # Also update latest
    latest_path = DATA_DIR / "latest.json"
    latest_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"Snapshot saved: {snapshot_path}")


def compare_snapshots(old: dict, new: dict) -> list:
    """Compare two snapshots and return list of changes."""
    changes = []
    old_providers = old.get("providers", {})
    new_providers = new.get("providers", {})

    for prov_name, prov_data in new_providers.items():
        old_prov = old_providers.get(prov_name, {})
        old_models = {m["name"]: m for m in old_prov.get("models", [])}

        for model in prov_data.get("models", []):
            name = model["name"]
            if name not in old_models:
                changes.append({"type": "new_model", "provider": prov_name, "model": name})
                continue

            old_model = old_models[name]
            for field in ["input_cache_hit", "input_cache_miss", "output"]:
                old_val = old_model.get(field)
                new_val = model.get(field)
                if old_val and new_val and new_val != old_val:
                    direction = "drop" if new_val < old_val else "increase"
                    changes.append({
                        "type": "price_change",
                        "direction": direction,
                        "provider": prov_name,
                        "model": name,
                        "field": field,
                        "old": old_val,
                        "new": new_val,
                    })

    return changes


def format_changes(changes: list) -> str:
    if not changes:
        return "No price changes detected."
    
    lines = []
    for c in changes:
        if c["type"] == "new_model":
            lines.append(f"🆕 New model: {c['provider']}/{c['model']}")
        elif c["type"] == "price_change":
            emoji = "⬇️" if c["direction"] == "drop" else "⬆️"
            lines.append(
                f"{emoji} {c['provider']}/{c['model']} {c['field']}: "
                f"{c['old']} → {c['new']}"
            )
    return "\n".join(lines)


def format_table(data: dict) -> str:
    """Format snapshot as markdown table."""
    lines = [f"# LLM API Pricing - {data['date']}\n"]
    
    for prov_name, prov_data in data.get("providers", {}).items():
        lines.append(f"\n## {prov_name.title()}\n")
        lines.append("| Model | Input (cache miss) | Input (cache hit) | Output | Context |")
        lines.append("|-------|-------------------|-------------------|--------|---------|")
        currency = prov_data.get("currency", "USD")
        symbol = "¥" if currency == "CNY" else "$"
        unit = "/M tokens"
        
        for m in prov_data.get("models", []):
            inp = f"{symbol}{m.get('input_cache_miss', '?')}{unit}" if m.get('input_cache_miss') else "-"
            cache = f"{symbol}{m.get('input_cache_hit', '?')}{unit}" if m.get('input_cache_hit') else "-"
            out = f"{symbol}{m.get('output', '?')}{unit}" if m.get('output') else "-"
            ctx = m.get("context", "?")
            lines.append(f"| {m['name']} | {inp} | {cache} | {out} | {ctx} |")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="LLM Price Tracker")
    parser.add_argument("--provider", help="Fetch specific provider only")
    parser.add_argument("--compare", action="store_true", help="Compare with last snapshot")
    parser.add_argument("--format", choices=["json", "table"], default="json", help="Output format")
    args = parser.parse_args()

    ensure_dirs()

    # This script provides the structure. Actual fetching is done by the AI agent
    # using web_fetch tool, since it handles HTML parsing better than raw requests.
    
    # Load existing data
    latest = load_latest()
    
    if args.compare:
        if not latest.get("date"):
            print("No previous snapshot to compare with.")
            return
        print(f"Latest snapshot: {latest['date']}")
        print(f"Providers: {', '.join(latest.get('providers', {}).keys())}")
        return

    # Show current data
    if args.format == "table" and latest.get("date"):
        print(format_table(latest))
    else:
        print(json.dumps(latest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
