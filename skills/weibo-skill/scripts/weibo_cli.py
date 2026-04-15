# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
# ]
# ///

#!/usr/bin/env python3
"""Thin CLI wrapper for common Weibo actions."""

from __future__ import annotations

import argparse
import json
import sys

import requests


MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
    "Mobile/15E148 Safari/604.1"
)


class WeiboClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": MOBILE_UA,
                "Referer": "https://m.weibo.cn/",
                "Accept": "application/json, text/plain, */*",
            }
        )
        self.bootstrap()

    def bootstrap(self) -> None:
        # Best-effort cookie/bootstrap flow. Even if this is partial, it keeps
        # the skill logic inside the wrapper instead of asking the model to
        # reconstruct mobile Weibo requests by hand.
        for url in [
            "https://m.weibo.cn/api/config",
            "https://m.weibo.cn/visitor/genvisitor2",
        ]:
            try:
                self.session.get(url, timeout=20)
            except requests.RequestException:
                pass

    def get_json(self, url: str, params: dict | None = None) -> dict:
        response = self.session.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError("微博接口返回格式异常")
        return data

    def hot(self) -> dict:
        return self.get_json(
            "https://m.weibo.cn/api/container/getIndex",
            {
                "containerid": "106003type=25",
                "t": "3",
                "disable_hot": "1",
                "filter_type": "realtimehot",
            },
        )

    def search(self, query: str, search_type: str) -> dict:
        container_map = {
            "content": "100103type=1",
            "user": "100103type=3",
            "topic": "100103type=38",
        }
        return self.get_json(
            "https://m.weibo.cn/api/container/getIndex",
            {
                "containerid": f"{container_map[search_type]}&q={query}",
            },
        )

    def comments(self, feed_id: str, page: int) -> dict:
        return self.get_json(
            "https://m.weibo.cn/api/comments/show",
            {
                "id": feed_id,
                "page": str(page),
            },
        )

    def user_feed(self, uid: str, since_id: str | None = None) -> dict:
        profile = self.get_json(
            "https://m.weibo.cn/api/container/getIndex",
            {
                "type": "uid",
                "value": uid,
            },
        )

        container_id = None
        tabs = ((profile.get("data") or {}).get("tabsInfo") or {}).get("tabs") or []
        for tab in tabs:
            if tab.get("tabKey") == "weibo":
                container_id = tab.get("containerid")
                break
        if not container_id:
            raise RuntimeError("未找到微博动态 containerid")

        params = {
            "type": "uid",
            "value": uid,
            "containerid": container_id,
        }
        if since_id:
            params["since_id"] = since_id
        return self.get_json("https://m.weibo.cn/api/container/getIndex", params)


def main() -> int:
    parser = argparse.ArgumentParser(description="微博技能统一 CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("hot", help="查看微博热搜")

    search_parser = subparsers.add_parser("search", help="搜索微博")
    search_parser.add_argument("--query", required=True, help="搜索关键词")
    search_parser.add_argument(
        "--type",
        choices=["content", "user", "topic"],
        default="content",
        help="搜索类型",
    )

    comments_parser = subparsers.add_parser("comments", help="查看微博评论")
    comments_parser.add_argument("--id", required=True, help="微博 feed id")
    comments_parser.add_argument("--page", type=int, default=1, help="页码")

    feed_parser = subparsers.add_parser("user-feed", help="查看用户动态")
    feed_parser.add_argument("--uid", required=True, help="用户 UID")
    feed_parser.add_argument("--since-id", help="分页 since_id")

    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    client = WeiboClient()
    if args.command == "hot":
        data = client.hot()
    elif args.command == "search":
        data = client.search(args.query, args.type)
    elif args.command == "comments":
        data = client.comments(args.id, args.page)
    else:
        data = client.user_feed(args.uid, args.since_id)

    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.RequestException as exc:
        print(f"请求失败: {exc}", file=sys.stderr)
        raise SystemExit(1)
    except Exception as exc:  # pragma: no cover - CLI error path
        print(f"错误: {exc}", file=sys.stderr)
        raise SystemExit(1)
