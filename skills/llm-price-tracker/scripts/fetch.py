#!/usr/bin/env python3
"""
Fetch LLM pricing data from models.dev JSON API.

Usage:
  python3 fetch.py                  # Fetch full api.json
  python3 fetch.py --source models  # Fetch models.json (model specs only)
  python3 fetch.py --no-save        # Dry run, print stats only

Output: data/snapshots/YYYY-MM-DD.json + data/latest.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"

API_URL = "https://models.dev/api.json"
MODELS_URL = "https://models.dev/models.json"


def ensure_dirs():
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def fetch_json(url: str) -> dict:
    """Fetch JSON from URL with proper headers."""
    req = Request(url, headers={"User-Agent": "llm-price-tracker/1.0", "Accept": "application/json"})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def build_snapshot(api_data: dict) -> dict:
    """Convert raw api.json into snapshot format with stats."""
    provider_count = len(api_data)
    model_count = sum(len(p.get("models", {})) for p in api_data.values())

    return {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "models.dev",
        "source_url": API_URL,
        "api_version": "api.json",
        "model_count": model_count,
        "provider_count": provider_count,
        "providers": api_data,
    }


def print_stats(data: dict):
    """Print summary statistics."""
    print(f"Providers: {data['provider_count']}")
    print(f"Models (total entries): {data['model_count']}")

    # Count by capability
    reasoning = 0
    vision = 0
    tool_call = 0
    free = 0
    for prov in data["providers"].values():
        for model in prov.get("models", {}).values():
            cost = model.get("cost", {})
            if model.get("reasoning"):
                reasoning += 1
            if "image" in model.get("modalities", {}).get("input", []):
                vision += 1
            if model.get("tool_call"):
                tool_call += 1
            if cost.get("input", 0) == 0 and cost.get("output", 0) == 0:
                free += 1

    print(f"  Reasoning: {reasoning}")
    print(f"  Vision input: {vision}")
    print(f"  Tool calling: {tool_call}")
    print(f"  Free models: {free}")

    # Top providers by model count
    top = sorted(data["providers"].items(), key=lambda x: len(x[1].get("models", {})), reverse=True)[:10]
    print(f"\nTop 10 providers by model count:")
    for pid, pinfo in top:
        print(f"  {pid}: {len(pinfo.get('models', {}))} models")


def main():
    parser = argparse.ArgumentParser(description="Fetch LLM pricing from models.dev")
    parser.add_argument("--source", choices=["api", "models"], default="api", help="Data source")
    parser.add_argument("--no-save", action="store_true", help="Print stats without saving")
    args = parser.parse_args()

    ensure_dirs()

    url = MODELS_URL if args.source == "models" else API_URL
    print(f"Fetching {url} ...")
    data = fetch_json(url)

    if args.source == "models":
        print(f"Total model definitions: {len(data)}")
        return

    snapshot = build_snapshot(data)
    print_stats(snapshot)

    if args.no_save:
        return

    date_key = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    snapshot_path = SNAPSHOTS_DIR / f"{date_key}.json"
    snapshot_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))

    latest_path = DATA_DIR / "latest.json"
    latest_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))

    print(f"\nSaved: {snapshot_path}")
    print(f"Updated: {latest_path}")


if __name__ == "__main__":
    main()
