#!/usr/bin/env python3
"""
Query LLM pricing from models.dev snapshots.

Usage:
  python3 query.py --provider openai,anthropic
  python3 query.py --model "gpt-5"
  python3 query.py --capability reasoning --max-cost 10
  python3 query.py --compare "claude-opus"
  python3 query.py --provider deepseek --format table
  python3 query.py --format csv > prices.csv
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"

# Capability filters mapped to data fields
CAPABILITIES = {
    "reasoning": "reasoning",
    "tool_call": "tool_call",
    "vision": "modalities.input[image]",
    "audio_input": "modalities.input[audio]",
    "audio_output": "modalities.output[audio]",
    "video": "modalities.input[video]",
    "image_output": "modalities.output[image]",
    "open_weights": "open_weights",
    "structured_output": "structured_output",
    "attachment": "attachment",
    "free": "cost",
}


def load_latest() -> dict:
    latest = DATA_DIR / "latest.json"
    if not latest.exists():
        print("No data. Run fetch.py first.", file=sys.stderr)
        sys.exit(1)
    return json.loads(latest.read_text())


def match_capability(model: dict, cap: str) -> bool:
    """Check if model satisfies a capability filter."""
    if cap == "free":
        cost = model.get("cost", {})
        return cost.get("input", 1) == 0 and cost.get("output", 1) == 0
    if cap == "vision":
        return "image" in model.get("modalities", {}).get("input", [])
    if cap == "audio_input":
        return "audio" in model.get("modalities", {}).get("input", [])
    if cap == "audio_output":
        return "audio" in model.get("modalities", {}).get("output", [])
    if cap == "video":
        return "video" in model.get("modalities", {}).get("input", [])
    if cap == "image_output":
        return "image" in model.get("modalities", {}).get("output", [])
    return bool(model.get(cap))


def filter_providers(data: dict, providers: list[str] | None, model_query: str | None,
                     capabilities: list[str] | None, max_cost: float | None) -> list[dict]:
    """Filter and flatten provider×model entries."""
    results = []
    for pid, pinfo in data.get("providers", {}).items():
        if providers and pid not in providers:
            continue
        for mid, model in pinfo.get("models", {}).items():
            # Model name search
            if model_query and model_query.lower() not in mid.lower() and model_query.lower() not in model.get("name", "").lower():
                continue
            # Capability filter
            if capabilities:
                if not all(match_capability(model, c) for c in capabilities):
                    continue
            # Max cost filter
            if max_cost is not None:
                output_cost = model.get("cost", {}).get("output")
                if output_cost is None or output_cost > max_cost:
                    continue
            results.append({
                "provider_id": pid,
                "provider_name": pinfo.get("name", pid),
                "model_id": mid,
                "model_name": model.get("name", mid),
                "family": model.get("family", ""),
                "cost": model.get("cost", {}),
                "limit": model.get("limit", {}),
                "modalities": model.get("modalities", {}),
                "reasoning": model.get("reasoning", False),
                "tool_call": model.get("tool_call", False),
                "open_weights": model.get("open_weights", False),
                "knowledge": model.get("knowledge", ""),
                "release_date": model.get("release_date", ""),
            })
    return results


def cross_compare(data: dict, family: str) -> list[dict]:
    """Find all providers offering models matching a family name, with pricing."""
    results = []
    for pid, pinfo in data.get("providers", {}).items():
        for mid, model in pinfo.get("models", {}).items():
            if family.lower() in mid.lower() or family.lower() in model.get("family", "").lower():
                results.append({
                    "provider_id": pid,
                    "provider_name": pinfo.get("name", pid),
                    "model_id": mid,
                    "model_name": model.get("name", mid),
                    "cost_input": model.get("cost", {}).get("input"),
                    "cost_output": model.get("cost", {}).get("output"),
                    "context": model.get("limit", {}).get("context"),
                    "max_output": model.get("limit", {}).get("output"),
                })
    return results


def format_table(results: list[dict], compare_mode: bool = False) -> str:
    """Format results as a console table."""
    if not results:
        return "No results found."

    if compare_mode:
        lines = [f"\n{'Provider':<25} {'Input/M':>10} {'Output/M':>10} {'Context':>12} {'Max Out':>10}"]
        lines.append("-" * 72)
        for r in results:
            inp = f"${r['cost_input']:.2f}" if r['cost_input'] is not None else "?"
            out = f"${r['cost_output']:.2f}" if r['cost_output'] is not None else "?"
            ctx = f"{r['context']:,}" if r['context'] else "?"
            mout = f"{r['max_output']:,}" if r['max_output'] else "?"
            lines.append(f"{r['provider_id']:<25} {inp:>10} {out:>10} {ctx:>12} {mout:>10}")
        return "\n".join(lines)
    else:
        lines = [f"\n{'Provider':<20} {'Model':<35} {'Input':>8} {'Output':>8} {'Context':>10} {'Features':<20}"]
        lines.append("-" * 115)
        for r in results:
            inp = f"${r['cost'].get('input', '?'):.2f}" if isinstance(r['cost'].get('input'), (int, float)) else "?"
            out = f"${r['cost'].get('output', '?'):.2f}" if isinstance(r['cost'].get('output'), (int, float)) else "?"
            ctx = f"{r['limit'].get('context', '?'):,}" if r['limit'].get('context') else "?"
            feats = []
            if r.get('reasoning'): feats.append("🧠")
            if r.get('tool_call'): feats.append("🔧")
            if r.get('open_weights'): feats.append("🔓")
            if "image" in r.get('modalities', {}).get('input', []): feats.append("👁️")
            lines.append(f"{r['provider_id']:<20} {r['model_id']:<35} {inp:>8} {out:>8} {ctx:>10} {' '.join(feats):<20}")
        return "\n".join(lines)


def format_csv(results: list[dict], compare_mode: bool = False) -> str:
    """Format results as CSV."""
    if compare_mode:
        lines = ["provider_id,provider_name,model_id,cost_input,cost_output,context,max_output"]
        for r in results:
            lines.append(f"{r['provider_id']},{r['provider_name']},{r['model_id']},{r['cost_input']},{r['cost_output']},{r['context']},{r['max_output']}")
    else:
        lines = ["provider_id,provider_name,model_id,model_name,cost_input,cost_output,cost_cache_read,context,reasoning,tool_call,open_weights,knowledge"]
        for r in results:
            lines.append(f"{r['provider_id']},{r['provider_name']},{r['model_id']},{r['model_name']},"
                        f"{r['cost'].get('input','')},{r['cost'].get('output','')},{r['cost'].get('cache_read','')},"
                        f"{r['limit'].get('context','')},{r['reasoning']},{r['tool_call']},{r['open_weights']},{r['knowledge']}")
    return "\n".join(lines)


def format_feishu(results: list[dict]) -> str:
    """Format results for Feishu markdown message."""
    if not results:
        return "暂无匹配结果。"
    lines = ["**LLM API 价格查询结果**\n"]
    for r in results[:20]:
        inp = f"${r['cost'].get('input', '?'):.2f}" if isinstance(r['cost'].get('input'), (int, float)) else "?"
        out = f"${r['cost'].get('output', '?'):.2f}" if isinstance(r['cost'].get('output'), (int, float)) else "?"
        ctx = f"{r['limit'].get('context', '?')/1000:.0f}K" if r['limit'].get('context') else "?"
        lines.append(f"• **{r['provider_id']}** / `{r['model_id']}` — in:{inp} out:{out} ctx:{ctx}")
    if len(results) > 20:
        lines.append(f"\n... 还有 {len(results) - 20} 条结果")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Query LLM pricing from models.dev")
    parser.add_argument("--provider", help="Comma-separated provider IDs")
    parser.add_argument("--model", help="Model name search (substring match)")
    parser.add_argument("--capability", help=f"Capability filter(s): {','.join(CAPABILITIES)}")
    parser.add_argument("--max-cost", type=float, help="Max output cost per million tokens (USD)")
    parser.add_argument("--compare", help="Cross-provider comparison for a model family")
    parser.add_argument("--format", choices=["json", "table", "csv", "feishu"], default="table")
    parser.add_argument("--sort", choices=["cost", "context", "date"], default="cost")
    args = parser.parse_args()

    data = load_latest()

    providers = args.provider.split(",") if args.provider else None
    capabilities = args.capability.split(",") if args.capability else None

    if args.compare:
        results = cross_compare(data, args.compare)
        if not results:
            print(f"No models matching '{args.compare}' found.")
            sys.exit(1)
        # Sort by cost
        results.sort(key=lambda r: r.get("cost_output") or 9999)
    else:
        results = filter_providers(data, providers, args.model, capabilities, args.max_cost)
        results.sort(key=lambda r: r['cost'].get('output', 9999))

    if args.format == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))
    elif args.format == "csv":
        print(format_csv(results, compare_mode=bool(args.compare)))
    elif args.format == "feishu":
        print(format_feishu(results))
    else:
        print(format_table(results, compare_mode=bool(args.compare)))
        print(f"\n{len(results)} results")


if __name__ == "__main__":
    main()
