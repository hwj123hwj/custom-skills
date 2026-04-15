# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
# ]
# ///

#!/usr/bin/env python3
"""Live classroom occupancy wrapper for BJTU classroom skill."""

from __future__ import annotations

import argparse
import json
import sys
from urllib.parse import urlencode

import requests


API_URL = "http://yaya.csoci.com:2333/api/classnum/"


def normalize_room_name(value: str) -> str:
    return "".join(ch for ch in value.upper() if ch.isalnum())


def fetch_live_data(building: str) -> dict:
    response = requests.get(f"{API_URL}?{urlencode({'building': building})}", timeout=20)
    response.raise_for_status()
    return response.json()


def filter_classroom_rows(data: dict, classroom: str | None) -> list[dict]:
    rows = []
    target = normalize_room_name(classroom) if classroom else None
    for row in data.get("data", []):
        room_name = str(row[0])
        room_norm = normalize_room_name(room_name)
        if target and target not in room_norm:
            continue
        rows.append(
            {
                "classroom": room_name,
                "occupancy_rate": row[1],
                "current_people": row[2],
                "capacity": row[3],
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="查询 BJTU 教室实时人数")
    parser.add_argument("--building", required=True, help="教学楼名称，如 思源东楼")
    parser.add_argument("--classroom", help="教室号，如 102")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    payload = fetch_live_data(args.building)
    rows = filter_classroom_rows(payload, args.classroom)
    result = {
        "building": args.building,
        "time": payload.get("time", []),
        "count": len(rows),
        "rows": rows,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"教学楼: {args.building}")
        for row in rows:
            print(
                f"- {row['classroom']}: {row['current_people']} / {row['capacity']} "
                f"({row['occupancy_rate']}%)"
            )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.RequestException as exc:
        print(f"请求失败: {exc}", file=sys.stderr)
        raise SystemExit(1)
