"""Helpers that normalize raw client responses for command-layer use."""

from __future__ import annotations

from typing import Any


def normalize_xhs_user_payload(info: dict[str, Any]) -> dict[str, object]:
    """Normalize Xiaohongshu user info for structured command output."""
    basic = info.get("basic_info", info) if isinstance(info, dict) else {}
    if not isinstance(basic, dict):
        basic = {}

    user_id = (
        basic.get("user_id")
        or info.get("user_id")
        or info.get("userid")
        or basic.get("red_id")
        or info.get("red_id")
        or ""
    )

    return {
        "id": user_id,
        "name": basic.get("nickname") or info.get("nickname", "Unknown"),
        "username": basic.get("red_id") or info.get("red_id", ""),
        "nickname": basic.get("nickname") or info.get("nickname", "Unknown"),
        "red_id": basic.get("red_id") or info.get("red_id", ""),
        "ip_location": basic.get("ip_location") or info.get("ip_location", ""),
        "desc": basic.get("desc") or info.get("desc", ""),
        "guest": bool(info.get("guest", False)),
    }


def normalize_unread_summary(data: dict[str, Any]) -> dict[str, int]:
    return {
        "mentions": int(data.get("mentions", 0)),
        "likes": int(data.get("likes", 0)),
        "connections": int(data.get("connections", 0)),
        "unread_count": int(data.get("unread_count", 0)),
    }


def normalize_paged_notes(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "notes": data.get("notes", []),
        "has_more": bool(data.get("has_more", False)),
        "cursor": data.get("cursor", ""),
    }


def select_topic_payload(topic_data: Any, fallback_name: str) -> list[dict[str, str]]:
    topics = topic_data if isinstance(topic_data, list) else topic_data.get("topic_info_dtos", [])
    if not topics:
        return []
    first = topics[0]
    return [{
        "id": first.get("id", ""),
        "name": first.get("name", fallback_name),
        "type": "topic",
    }]


def resolve_current_user_id(info: dict[str, Any]) -> str:
    return info.get("user_id", "") if isinstance(info, dict) else ""
