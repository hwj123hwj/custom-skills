#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests>=2.28.0",
# ]
# ///
"""Export Feishu/Lark docs or Drive folders to Markdown.

This is a small personal-export script built around the official Feishu Open
Platform APIs. It exports viewable docx documents by reading document blocks and
rendering them to Markdown.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

try:
    import requests
except ImportError:  # pragma: no cover
    print("Missing dependency: requests. Install with: pip install requests", file=sys.stderr)
    raise


BASE_URL = "https://open.feishu.cn/open-apis"
REDIRECT_URI = "http://localhost:9876/callback"
DEFAULT_HOME = Path.home() / ".feishu-md-exporter"
DEFAULT_CONFIG = DEFAULT_HOME / "config.json"
DEFAULT_TOKEN_CACHE = DEFAULT_HOME / "token_cache.json"

SCOPES = " ".join(
    [
        "wiki:wiki:readonly",
        "docx:document:readonly",
        "drive:drive:readonly",
        "drive:file:readonly",
    ]
)


BLOCK_PAGE = 1
BLOCK_TEXT = 2
BLOCK_HEADING1 = 3
BLOCK_HEADING9 = 11
BLOCK_BULLET = 12
BLOCK_ORDERED = 13
BLOCK_CODE = 14
BLOCK_QUOTE = 15
BLOCK_TODO = 17
BLOCK_CALLOUT = 19
BLOCK_DIVIDER = 22
BLOCK_FILE = 23
BLOCK_IMAGE = 27
BLOCK_TABLE = 31
BLOCK_QUOTE_CONTAINER = 35

LANG_MAP = {
    1: "plaintext",
    7: "bash",
    10: "c",
    16: "cpp",
    17: "csharp",
    18: "css",
    31: "html",
    34: "javascript",
    35: "json",
    37: "kotlin",
    54: "python",
    58: "rust",
    63: "shell",
    64: "sql",
    67: "typescript",
    72: "yaml",
}


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    auth_code: str | None = None

    def do_GET(self) -> None:
        query = parse_qs(urlparse(self.path).query)
        code = query.get("code", [None])[0]
        if code:
            OAuthCallbackHandler.auth_code = code
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("授权成功，可以关闭此页面。".encode("utf-8"))
        else:
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("授权失败，未收到 code 参数。".encode("utf-8"))

    def log_message(self, *_args: Any) -> None:
        return


class FeishuClient:
    def __init__(self, app_id: str, app_secret: str, token_cache: Path):
        self.app_id = app_id
        self.app_secret = app_secret
        self.token_cache = token_cache
        self.user_token: str | None = None
        self.refresh_token: str | None = None
        self.expire_at = 0.0
        self.session = requests.Session()
        self.session.trust_env = False

    def app_access_token(self) -> str:
        resp = self.session.post(
            f"{BASE_URL}/auth/v3/app_access_token/internal/",
            json={"app_id": self.app_id, "app_secret": self.app_secret},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"获取 app_access_token 失败: {data.get('msg')}")
        return data["app_access_token"]

    def load_cache(self) -> bool:
        if not self.token_cache.exists():
            return False
        cache = json.loads(self.token_cache.read_text(encoding="utf-8"))
        self.user_token = cache.get("user_access_token")
        self.refresh_token = cache.get("refresh_token")
        self.expire_at = cache.get("expire_at", 0)
        return bool(self.user_token)

    def save_cache(self) -> None:
        self.token_cache.parent.mkdir(parents=True, exist_ok=True)
        self.token_cache.write_text(
            json.dumps(
                {
                    "user_access_token": self.user_token,
                    "refresh_token": self.refresh_token,
                    "expire_at": self.expire_at,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        try:
            self.token_cache.chmod(0o600)
        except OSError:
            pass

    def oauth_login(self) -> None:
        auth_url = (
            f"https://open.feishu.cn/open-apis/authen/v1/authorize"
            f"?app_id={self.app_id}&redirect_uri={REDIRECT_URI}&response_type=code"
            f"&scope={SCOPES}"
        )
        print("Opening browser for Feishu OAuth authorization...")
        print("If it does not open automatically, visit:")
        print(auth_url)
        webbrowser.open(auth_url)

        OAuthCallbackHandler.auth_code = None
        server = HTTPServer(("localhost", 9876), OAuthCallbackHandler)
        server.timeout = 180
        while OAuthCallbackHandler.auth_code is None:
            server.handle_request()
        server.server_close()

        resp = self.session.post(
            f"{BASE_URL}/authen/v1/oidc/access_token",
            headers={
                "Authorization": f"Bearer {self.app_access_token()}",
                "Content-Type": "application/json",
            },
            json={"grant_type": "authorization_code", "code": OAuthCallbackHandler.auth_code},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"获取 user_access_token 失败: {data.get('msg')}")
        token_data = data["data"]
        self.user_token = token_data["access_token"]
        self.refresh_token = token_data.get("refresh_token")
        self.expire_at = time.time() + token_data.get("expires_in", 7200)
        self.save_cache()
        print("Authorization succeeded.")

    def refresh_user_token(self) -> None:
        if not self.refresh_token:
            self.oauth_login()
            return
        resp = self.session.post(
            f"{BASE_URL}/authen/v1/oidc/refresh_access_token",
            headers={
                "Authorization": f"Bearer {self.app_access_token()}",
                "Content-Type": "application/json",
            },
            json={"grant_type": "refresh_token", "refresh_token": self.refresh_token},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            print("Cached token expired; starting OAuth again.")
            self.oauth_login()
            return
        token_data = data["data"]
        self.user_token = token_data["access_token"]
        self.refresh_token = token_data.get("refresh_token", self.refresh_token)
        self.expire_at = time.time() + token_data.get("expires_in", 7200)
        self.save_cache()

    def ensure_token(self) -> None:
        if not self.user_token:
            self.load_cache()
        if self.user_token and time.time() < self.expire_at - 60:
            return
        if self.user_token and self.refresh_token:
            self.refresh_user_token()
            return
        self.oauth_login()

    def headers(self) -> dict[str, str]:
        self.ensure_token()
        return {"Authorization": f"Bearer {self.user_token}"}

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.session.get(f"{BASE_URL}{path}", headers=self.headers(), params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"{path} failed: {data.get('msg')} (code={data.get('code')})")
        return data

    def resolve_wiki(self, wiki_token: str) -> tuple[str, str]:
        data = self.get_json("/wiki/v2/spaces/get_node", {"token": wiki_token})
        node = data["data"]["node"]
        return node["obj_token"], node["obj_type"]

    def document_meta(self, doc_token: str) -> dict[str, Any]:
        return self.get_json(f"/docx/v1/documents/{doc_token}")["data"]["document"]

    def document_blocks(self, doc_token: str) -> list[dict[str, Any]]:
        blocks: list[dict[str, Any]] = []
        page_token = None
        while True:
            params: dict[str, Any] = {"page_size": 500}
            if page_token:
                params["page_token"] = page_token
            data = self.get_json(f"/docx/v1/documents/{doc_token}/blocks", params)
            blocks.extend(data["data"].get("items", []))
            if not data["data"].get("has_more"):
                break
            page_token = data["data"].get("page_token")
        return blocks

    def list_folder(self, folder_token: str) -> list[dict[str, Any]]:
        files: list[dict[str, Any]] = []
        page_token = None
        while True:
            params: dict[str, Any] = {"folder_token": folder_token, "page_size": 200}
            if page_token:
                params["page_token"] = page_token
            data = self.get_json("/drive/v1/files", params)
            files.extend(data.get("data", {}).get("files", []))
            if not data.get("data", {}).get("has_more"):
                break
            page_token = data.get("data", {}).get("page_token")
        return files


def render_elements(elements: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for elem in elements:
        if "text_run" in elem:
            tr = elem["text_run"]
            content = tr.get("content", "")
            style = tr.get("text_element_style", {})
            if style.get("inline_code"):
                content = f"`{content}`"
            else:
                if style.get("bold"):
                    content = f"**{content}**"
                if style.get("italic"):
                    content = f"*{content}*"
                if style.get("strikethrough"):
                    content = f"~~{content}~~"
            link = style.get("link", {})
            if link.get("url"):
                content = f"[{content}]({unquote(link['url'])})"
            parts.append(content)
        elif "equation" in elem:
            parts.append(f"${elem['equation'].get('content', '')}$")
        elif "mention_user" in elem:
            parts.append("@user")
        elif "mention_doc" in elem:
            doc = elem["mention_doc"]
            parts.append(f"[{doc.get('title', '文档')}]({unquote(doc.get('url', ''))})")
    return "".join(parts)


def block_text(block: dict[str, Any], key: str) -> str:
    return render_elements(block.get(key, {}).get("elements", []))


class MarkdownConverter:
    def __init__(self, blocks: list[dict[str, Any]], title: str):
        self.blocks = {b["block_id"]: b for b in blocks}
        self.title = title
        self.lines: list[str] = []
        self.ordered_counters: dict[str, int] = {}

    def convert(self) -> str:
        if self.title:
            self.lines.extend([f"# {self.title}", ""])
        root = next((b for b in self.blocks.values() if b.get("block_type") == BLOCK_PAGE), None)
        if root:
            self.children(root.get("children", []), 0)
        text = "\n".join(self.lines)
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        return text.strip() + "\n"

    def children(self, child_ids: list[str], depth: int, in_quote: bool = False) -> None:
        for child_id in child_ids:
            block = self.blocks.get(child_id)
            if block:
                self.block(block, depth, in_quote)

    def block(self, block: dict[str, Any], depth: int, in_quote: bool = False) -> None:
        bt = block.get("block_type")
        prefix = "> " if in_quote else ""
        if bt == BLOCK_TEXT:
            self.lines.extend([f"{prefix}{block_text(block, 'text')}", ""])
        elif isinstance(bt, int) and BLOCK_HEADING1 <= bt <= BLOCK_HEADING9:
            level = bt - BLOCK_HEADING1 + 1
            self.lines.extend([f"{prefix}{'#' * min(level, 6)} {block_text(block, f'heading{level}')}", ""])
        elif bt == BLOCK_BULLET:
            self.lines.append(f"{prefix}{'  ' * depth}- {block_text(block, 'bullet')}")
            self.children(block.get("children", []), depth + 1, in_quote)
        elif bt == BLOCK_ORDERED:
            key = f"{block.get('parent_id', '')}_{depth}"
            self.ordered_counters[key] = self.ordered_counters.get(key, 0) + 1
            self.lines.append(f"{prefix}{'  ' * depth}{self.ordered_counters[key]}. {block_text(block, 'ordered')}")
            self.children(block.get("children", []), depth + 1, in_quote)
        elif bt == BLOCK_CODE:
            code_data = block.get("code", {})
            code_text = "".join(e.get("text_run", {}).get("content", "") for e in code_data.get("elements", []))
            lang = LANG_MAP.get(code_data.get("language"), "")
            self.lines.append(f"{prefix}```{lang}")
            self.lines.extend(f"{prefix}{line}" for line in code_text.rstrip().split("\n"))
            self.lines.extend([f"{prefix}```", ""])
        elif bt == BLOCK_QUOTE:
            self.lines.extend([f"> {block_text(block, 'quote')}", ""])
        elif bt in (BLOCK_QUOTE_CONTAINER, BLOCK_CALLOUT):
            self.children(block.get("children", []), depth, True)
            self.lines.append("")
        elif bt == BLOCK_TODO:
            todo = block.get("todo", {})
            checkbox = "[x]" if todo.get("style", {}).get("done") else "[ ]"
            self.lines.append(f"{prefix}{'  ' * depth}- {checkbox} {render_elements(todo.get('elements', []))}")
            self.children(block.get("children", []), depth + 1, in_quote)
        elif bt == BLOCK_DIVIDER:
            self.lines.extend([f"{prefix}---", ""])
        elif bt == BLOCK_IMAGE:
            self.lines.extend([f"{prefix}[图片: {block.get('image', {}).get('token', '')}]", ""])
        elif bt == BLOCK_FILE:
            self.lines.extend([f"{prefix}[文件: {block.get('file', {}).get('name', '未知文件')}]", ""])
        elif bt == BLOCK_TABLE:
            self.table(block, prefix)

    def table(self, block: dict[str, Any], prefix: str) -> None:
        prop = block.get("table", {}).get("property", {})
        rows, cols = prop.get("row_size", 0), prop.get("column_size", 0)
        cells = block.get("children", [])
        if not rows or not cols:
            return
        table_rows: list[list[str]] = []
        for r in range(rows):
            row = []
            for c in range(cols):
                idx = r * cols + c
                cell = self.blocks.get(cells[idx], {}) if idx < len(cells) else {}
                row.append(self.cell_text(cell))
            table_rows.append(row)
        if not table_rows:
            return
        self.lines.append(f"{prefix}| " + " | ".join(table_rows[0]) + " |")
        self.lines.append(f"{prefix}| " + " | ".join(["---"] * cols) + " |")
        for row in table_rows[1:]:
            self.lines.append(f"{prefix}| " + " | ".join(row) + " |")
        self.lines.append("")

    def cell_text(self, cell: dict[str, Any]) -> str:
        parts = []
        for child_id in cell.get("children", []):
            child = self.blocks.get(child_id, {})
            bt = child.get("block_type")
            if bt == BLOCK_TEXT:
                parts.append(block_text(child, "text"))
            elif isinstance(bt, int) and BLOCK_HEADING1 <= bt <= BLOCK_HEADING9:
                parts.append(block_text(child, f"heading{bt - BLOCK_HEADING1 + 1}"))
            elif bt == BLOCK_BULLET:
                parts.append(block_text(child, "bullet"))
            elif bt == BLOCK_ORDERED:
                parts.append(block_text(child, "ordered"))
            else:
                for key in ["text", "bullet", "ordered", "todo"]:
                    elements = child.get(key, {}).get("elements", [])
                    if elements:
                        parts.append(render_elements(elements))
                        break
        return " <br> ".join(p for p in parts if p)


def parse_url(raw: str) -> tuple[str, str]:
    domain = r"(?:feishu\.cn|larkoffice\.com|larksuite\.com)"
    patterns = {
        "folder": domain + r"/drive/folder/([A-Za-z0-9]+)",
        "docx": domain + r"/docx/([A-Za-z0-9]+)",
        "doc": domain + r"/docs/([A-Za-z0-9]+)",
        "wiki": domain + r"/wiki/([A-Za-z0-9]+)",
    }
    for kind, pattern in patterns.items():
        match = re.search(pattern, raw)
        if match:
            return match.group(1), kind
    return raw.strip(), "docx"


def clean_name(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "_", name or "untitled").strip().strip(".")
    return (name[:160] or "untitled")


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    for idx in range(2, 10000):
        candidate = path.with_name(f"{path.stem}_{idx}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Too many duplicate names near {path}")


def export_doc(client: FeishuClient, token: str, doc_type: str, output_dir: Path, fallback_name: str = "") -> Path:
    if doc_type == "wiki":
        token, doc_type = client.resolve_wiki(token)
    if doc_type not in ("docx", "doc"):
        raise RuntimeError(f"Unsupported document type for Markdown export: {doc_type}")
    meta = client.document_meta(token)
    title = meta.get("title") or fallback_name or token
    blocks = client.document_blocks(token)
    markdown = MarkdownConverter(blocks, title).convert()
    output_dir.mkdir(parents=True, exist_ok=True)
    path = unique_path(output_dir / f"{clean_name(title)}.md")
    path.write_text(markdown, encoding="utf-8")
    return path


def export_folder(client: FeishuClient, folder_token: str, output_dir: Path, stats: dict[str, int], depth: int = 0) -> None:
    for item in client.list_folder(folder_token):
        name = item.get("name") or item.get("token") or "untitled"
        typ = item.get("type")
        token = item.get("token")
        indent = "  " * depth
        if typ == "folder":
            stats["folders"] += 1
            print(f"{indent}[dir] {name}", flush=True)
            export_folder(client, token, output_dir / clean_name(name), stats, depth + 1)
        elif typ in ("docx", "doc"):
            try:
                path = export_doc(client, token, typ, output_dir, name)
                stats["docs"] += 1
                print(f"{indent}[md] {name} -> {path}", flush=True)
                time.sleep(0.15)
            except Exception as exc:
                stats["failed"] += 1
                print(f"{indent}[fail] {name}: {exc}", flush=True)
        elif typ == "wiki":
            try:
                path = export_doc(client, token, "wiki", output_dir, name)
                stats["docs"] += 1
                print(f"{indent}[md] {name} -> {path}", flush=True)
            except Exception as exc:
                stats["failed"] += 1
                print(f"{indent}[fail] {name}: {exc}", flush=True)
        else:
            stats["skipped"] += 1
            print(f"{indent}[skip:{typ}] {name}", flush=True)


def load_credentials(args: argparse.Namespace) -> tuple[str, str]:
    app_id = args.app_id or os.getenv("FEISHU_APP_ID")
    app_secret = args.app_secret or os.getenv("FEISHU_APP_SECRET")
    config_path = Path(args.config).expanduser() if args.config else DEFAULT_CONFIG
    if (not app_id or not app_secret) and config_path.exists():
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
        app_id = app_id or cfg.get("app_id")
        app_secret = app_secret or cfg.get("app_secret")
    if not app_id or not app_secret:
        raise SystemExit(
            "Missing Feishu app credentials. Set FEISHU_APP_ID/FEISHU_APP_SECRET, "
            "pass --app-id/--app-secret, or create ~/.feishu-md-exporter/config.json."
        )
    return app_id, app_secret


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Feishu/Lark doc or folder to Markdown.")
    parser.add_argument("url", help="Feishu/Lark docx/wiki/doc URL, folder URL, or doc token")
    parser.add_argument("--output", "-o", default="./feishu_md_exports", help="Output directory")
    parser.add_argument("--app-id", help="Feishu app_id, e.g. cli_xxx")
    parser.add_argument("--app-secret", help="Feishu app_secret")
    parser.add_argument("--config", help="Credential config path, default ~/.feishu-md-exporter/config.json")
    parser.add_argument("--token-cache", default=str(DEFAULT_TOKEN_CACHE), help="OAuth token cache path")
    args = parser.parse_args()

    app_id, app_secret = load_credentials(args)
    token_cache = Path(args.token_cache).expanduser()
    client = FeishuClient(app_id, app_secret, token_cache)
    token, kind = parse_url(args.url)
    output_root = Path(args.output).expanduser().resolve()

    if kind == "folder":
        stats = {"folders": 0, "docs": 0, "failed": 0, "skipped": 0}
        folder_dir = output_root / token
        folder_dir.mkdir(parents=True, exist_ok=True)
        export_folder(client, token, folder_dir, stats)
        print(f"\nDone. Output: {folder_dir}")
        print(
            f"Exported {stats['docs']} Markdown files; "
            f"folders={stats['folders']}, failed={stats['failed']}, skipped={stats['skipped']}."
        )
    else:
        path = export_doc(client, token, kind, output_root)
        print(f"Done. Output: {path}")


if __name__ == "__main__":
    main()
