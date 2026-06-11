#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests>=2.28.0"]
# ///
"""Publish local Markdown files to a Feishu/Lark Wiki knowledge space.

The script calls Feishu OpenAPI directly. It intentionally does not require
`lark-cli` at runtime, because this workflow is meant to run inside a bot or
agent backend.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import mimetypes
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests


DEFAULT_BASE_URL = "https://open.feishu.cn"
DEFAULT_STATE = ".llm-wiki/feishu-sync.json"
IMPORT_POLL_ATTEMPTS = 30
IMPORT_POLL_INTERVAL = 2.0
WIKI_MOVE_POLL_ATTEMPTS = 30
WIKI_MOVE_POLL_INTERVAL = 2.0


class FeishuError(RuntimeError):
    """Raised when Feishu OpenAPI returns a non-success response."""


@dataclass(frozen=True)
class MarkdownFile:
    path: Path
    rel_path: str
    title: str
    sha256: str
    size: int


class FeishuClient:
    def __init__(self, app_id: str, app_secret: str, base_url: str = DEFAULT_BASE_URL, timeout: int = 60):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._tenant_access_token: str | None = None

    def tenant_access_token(self) -> str:
        if self._tenant_access_token:
            return self._tenant_access_token

        data = self._request(
            "POST",
            "/open-apis/auth/v3/tenant_access_token/internal",
            json_body={"app_id": self.app_id, "app_secret": self.app_secret},
            auth=False,
        )
        token = data.get("tenant_access_token")
        if not token:
            raise FeishuError("tenant_access_token missing from auth response")
        self._tenant_access_token = token
        return token

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        auth: bool = True,
    ) -> dict[str, Any]:
        headers = {}
        if auth:
            headers["Authorization"] = f"Bearer {self.tenant_access_token()}"

        resp = requests.request(
            method,
            f"{self.base_url}{path}",
            params=params,
            json=json_body,
            files=files,
            data=data,
            headers=headers,
            timeout=self.timeout,
        )
        try:
            payload = resp.json()
        except ValueError as exc:
            raise FeishuError(f"{method} {path} returned non-JSON response: HTTP {resp.status_code}") from exc

        if resp.status_code >= 400:
            raise FeishuError(f"{method} {path} HTTP {resp.status_code}: {payload}")

        code = payload.get("code", 0)
        if code not in (0, None):
            msg = payload.get("msg") or payload.get("message") or "OpenAPI error"
            raise FeishuError(f"{method} {path} code={code}: {msg}; response={payload}")

        return payload.get("data") or payload

    def upload_import_media(self, md: MarkdownFile) -> str:
        extra = json.dumps({"obj_type": "docx", "file_extension": md.path.suffix.lstrip(".").lower()}, ensure_ascii=False)
        mime_type = mimetypes.guess_type(md.path.name)[0] or "text/markdown"
        with md.path.open("rb") as fh:
            files = {"file": (md.path.name, fh, mime_type)}
            data = {
                "file_name": md.path.name,
                "parent_type": "ccm_import_open",
                "parent_node": "",
                "size": str(md.size),
                "extra": extra,
            }
            result = self._request("POST", "/open-apis/drive/v1/medias/upload_all", files=files, data=data)
        file_token = result.get("file_token") or result.get("file", {}).get("file_token")
        if not file_token:
            raise FeishuError(f"file_token missing after uploading {md.rel_path}: {result}")
        return file_token

    def create_import_task(self, md: MarkdownFile, file_token: str, folder_token: str = "") -> str:
        body = {
            "file_extension": md.path.suffix.lstrip(".").lower(),
            "file_token": file_token,
            "type": "docx",
            "file_name": md.title,
            "point": {"mount_type": 1, "mount_key": folder_token},
        }
        result = self._request("POST", "/open-apis/drive/v1/import_tasks", json_body=body)
        ticket = result.get("ticket")
        if not ticket:
            raise FeishuError(f"ticket missing after creating import task for {md.rel_path}: {result}")
        return ticket

    def poll_import_task(self, ticket: str) -> dict[str, Any]:
        last: dict[str, Any] = {}
        for _ in range(IMPORT_POLL_ATTEMPTS):
            result = self._request("GET", f"/open-apis/drive/v1/import_tasks/{ticket}")
            last = result
            status = result.get("result") or result
            job_status = int(status.get("job_status", status.get("status", 0)) or 0)
            if job_status == 0 and (status.get("token") or status.get("url")):
                return status
            if job_status < 0:
                raise FeishuError(f"import task failed: ticket={ticket}, result={result}")
            time.sleep(IMPORT_POLL_INTERVAL)
        raise FeishuError(f"import task timed out: ticket={ticket}, last={last}")

    def move_doc_to_wiki(self, doc_token: str, target_space_id: str, parent_token: str = "", apply: bool = False) -> dict[str, Any]:
        body: dict[str, Any] = {"obj_type": "docx", "obj_token": doc_token}
        if parent_token:
            body["parent_wiki_token"] = parent_token
        if apply:
            body["apply"] = True
        result = self._request("POST", f"/open-apis/wiki/v2/spaces/{target_space_id}/nodes/move_docs_to_wiki", json_body=body)
        if result.get("wiki_token"):
            return {"ready": True, "wiki_token": result["wiki_token"], "raw": result}
        if result.get("applied"):
            return {"ready": False, "applied": True, "raw": result}
        task_id = result.get("task_id")
        if not task_id:
            raise FeishuError(f"move_docs_to_wiki returned no wiki_token/task_id/applied: {result}")
        return self.poll_wiki_move_task(task_id)

    def get_wiki_node(self, token_or_url: str) -> dict[str, Any]:
        token = extract_feishu_token(token_or_url)
        result = self._request("GET", "/open-apis/wiki/v2/spaces/get_node", params={"token": token})
        node = result.get("node") or result
        if not node.get("space_id"):
            raise FeishuError(f"could not resolve wiki node from {token_or_url}: {result}")
        return node

    def poll_wiki_move_task(self, task_id: str) -> dict[str, Any]:
        last: dict[str, Any] = {}
        for _ in range(WIKI_MOVE_POLL_ATTEMPTS):
            result = self._request("GET", f"/open-apis/wiki/v2/tasks/{task_id}", params={"task_type": "move"})
            last = result
            task = result.get("task") or result
            move_results = task.get("move_results") or []
            if move_results:
                failed = [item for item in move_results if int(item.get("status", 1)) < 0]
                if failed:
                    raise FeishuError(f"wiki move task failed: task_id={task_id}, result={result}")
                ready = all(int(item.get("status", 1)) == 0 for item in move_results)
                if ready:
                    node = move_results[0].get("node") or {}
                    return {"ready": True, "wiki_token": node.get("node_token") or node.get("wiki_token"), "node": node, "raw": result}
            time.sleep(WIKI_MOVE_POLL_INTERVAL)
        raise FeishuError(f"wiki move task timed out: task_id={task_id}, last={last}")

    def create_directory_document(self, title: str) -> dict[str, Any]:
        body: dict[str, Any] = {
            "format": "markdown",
            "content": f"# {title}\n\n> Directory page generated for Markdown knowledge sync.\n",
        }
        result = self._request("POST", "/open-apis/docs_ai/v1/documents", json_body=body)
        doc = result.get("document") or result
        doc_token = doc.get("document_id") or doc.get("token")
        if not doc_token:
            raise FeishuError(f"directory doc token missing after creating {title}: {result}")
        return {"doc_token": doc_token, "url": doc.get("url"), "raw": result}

    def overwrite_document_markdown(self, doc_token: str, md: MarkdownFile) -> dict[str, Any]:
        content = md.path.read_text(encoding="utf-8", errors="replace")
        body = {"format": "markdown", "command": "overwrite", "revision_id": -1, "content": content}
        return self._request("PUT", f"/open-apis/docs_ai/v1/documents/{doc_token}", json_body=body)


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "directories": {}, "files": {}}
    with path.open("r", encoding="utf-8") as fh:
        state = json.load(fh)
    state.setdefault("version", 1)
    state.setdefault("directories", {})
    state.setdefault("files", {})
    return state


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def markdown_title(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped[2:].strip() or path.stem
    except OSError:
        pass
    return path.stem


def should_exclude(rel_path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel_path, pattern) for pattern in patterns)


def collect_markdown(source: Path, exclude: list[str]) -> list[MarkdownFile]:
    source = source.expanduser().resolve()
    if source.is_file():
        paths = [source]
        base = source.parent
    else:
        base = source
        paths = sorted(source.rglob("*.md"))

    files: list[MarkdownFile] = []
    for path in paths:
        if not path.is_file() or path.suffix.lower() not in (".md", ".markdown", ".mark"):
            continue
        rel_path = path.relative_to(base).as_posix()
        if should_exclude(rel_path, exclude):
            continue
        files.append(
            MarkdownFile(
                path=path,
                rel_path=rel_path,
                title=markdown_title(path),
                sha256=sha256_file(path),
                size=path.stat().st_size,
            )
        )
    return files


def directory_chain(rel_path: str) -> list[str]:
    parent = Path(rel_path).parent
    if str(parent) in ("", "."):
        return []
    parts: list[str] = []
    current = Path()
    for part in parent.parts:
        current = current / part
        parts.append(current.as_posix())
    return parts


def extract_feishu_token(value: str) -> str:
    raw = value.strip()
    if not raw:
        return ""
    if not raw.startswith(("http://", "https://")):
        return raw
    parsed = urlparse(raw)
    parts = [part for part in parsed.path.split("/") if part]
    for idx, part in enumerate(parts[:-1]):
        if part in {"wiki", "docx", "doc", "folder", "file"}:
            return parts[idx + 1]
    return parts[-1] if parts else raw


def resolve_wiki_target(
    client: FeishuClient,
    *,
    target_space_id: str,
    target_parent_token: str,
    target_url: str,
) -> tuple[str, str, dict[str, Any] | None]:
    if target_url:
        node = client.get_wiki_node(target_url)
        return (
            target_space_id or str(node.get("space_id") or ""),
            target_parent_token or str(node.get("node_token") or extract_feishu_token(target_url)),
            node,
        )

    if target_parent_token and not target_space_id:
        node = client.get_wiki_node(target_parent_token)
        return str(node.get("space_id") or ""), target_parent_token, node

    return target_space_id, target_parent_token, None


def ensure_directory_pages(
    client: FeishuClient,
    state: dict[str, Any],
    chain: list[str],
    *,
    target_space_id: str,
    root_parent_token: str,
    execute: bool,
    output_events: list[dict[str, Any]],
) -> str:
    parent_token = root_parent_token
    for rel_dir in chain:
        item = state["directories"].get(rel_dir)
        if item and item.get("wiki_token"):
            parent_token = item["wiki_token"]
            continue

        title = Path(rel_dir).name
        if not execute:
            output_events.append({"action": "create_directory_page", "dir": rel_dir, "title": title, "parent_token": parent_token})
            parent_token = f"<dry-run:{rel_dir}>"
            continue

        created = client.create_directory_document(title)
        doc_token = created["doc_token"]
        moved = client.move_doc_to_wiki(doc_token, target_space_id=target_space_id, parent_token=parent_token)
        wiki_token = moved.get("wiki_token") or doc_token
        state["directories"][rel_dir] = {
            "title": title,
            "doc_token": doc_token,
            "wiki_token": wiki_token,
            "url": created.get("url"),
            "parent_token": parent_token,
            "updated_at": int(time.time()),
        }
        output_events.append({"action": "created_directory_page", "dir": rel_dir, "title": title, "wiki_token": wiki_token})
        parent_token = wiki_token
    return parent_token


def publish_file(
    client: FeishuClient,
    md: MarkdownFile,
    state: dict[str, Any],
    *,
    target_space_id: str,
    parent_token: str,
    execute: bool,
    update_existing: bool,
    force_reimport: bool,
    apply_move: bool,
) -> dict[str, Any]:
    existing = state["files"].get(md.rel_path)
    if existing and existing.get("sha256") == md.sha256 and not force_reimport:
        return {"path": md.rel_path, "action": "skip_unchanged", "title": md.title}

    if existing and existing.get("doc_token") and update_existing and not force_reimport:
        if not execute:
            return {"path": md.rel_path, "action": "update_existing", "doc_token": existing["doc_token"], "title": md.title}
        client.overwrite_document_markdown(existing["doc_token"], md)
        existing.update({"sha256": md.sha256, "title": md.title, "updated_at": int(time.time())})
        return {"path": md.rel_path, "action": "updated_existing", "doc_token": existing["doc_token"], "title": md.title}

    if not execute:
        return {"path": md.rel_path, "action": "import_and_move", "title": md.title, "parent_token": parent_token}

    file_token = client.upload_import_media(md)
    ticket = client.create_import_task(md, file_token)
    imported = client.poll_import_task(ticket)
    doc_token = imported.get("token")
    if not doc_token:
        raise FeishuError(f"import completed without doc token for {md.rel_path}: {imported}")
    moved = client.move_doc_to_wiki(doc_token, target_space_id=target_space_id, parent_token=parent_token, apply=apply_move)
    wiki_token = moved.get("wiki_token")
    record = {
        "title": md.title,
        "sha256": md.sha256,
        "doc_token": doc_token,
        "wiki_token": wiki_token,
        "url": imported.get("url"),
        "parent_token": parent_token,
        "updated_at": int(time.time()),
    }
    state["files"][md.rel_path] = record
    return {"path": md.rel_path, "action": "imported_and_moved", "doc_token": doc_token, "wiki_token": wiki_token, "title": md.title}


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish Markdown files to a Feishu/Lark Wiki knowledge space")
    parser.add_argument("--source", default=".llm-wiki/wiki", help="Markdown file or directory to publish")
    parser.add_argument("--state", default=DEFAULT_STATE, help="Sync state JSON path")
    parser.add_argument("--app-id", default=os.environ.get("FEISHU_APP_ID", ""), help="Feishu app id; defaults to FEISHU_APP_ID")
    parser.add_argument("--app-secret", default=os.environ.get("FEISHU_APP_SECRET", ""), help="Feishu app secret; defaults to FEISHU_APP_SECRET")
    parser.add_argument("--target-space-id", default=os.environ.get("FEISHU_TARGET_SPACE_ID", ""), help="Target Wiki space_id")
    parser.add_argument("--target-parent-token", default=os.environ.get("FEISHU_TARGET_PARENT_TOKEN", ""), help="Optional target parent wiki node token")
    parser.add_argument("--target-url", default=os.environ.get("FEISHU_TARGET_URL", ""), help="Optional target Wiki URL; resolves space_id and parent node token")
    parser.add_argument("--base-url", default=os.environ.get("FEISHU_OPENAPI_BASE_URL", DEFAULT_BASE_URL), help="OpenAPI base URL")
    parser.add_argument("--execute", action="store_true", help="Actually write to Feishu. Omit for dry-run.")
    parser.add_argument("--update-existing", action="store_true", help="Overwrite changed docs recorded in the sync state instead of re-importing")
    parser.add_argument("--force-reimport", action="store_true", help="Re-import changed/existing files as new docs")
    parser.add_argument("--flat", action="store_true", help="Do not create directory pages for subdirectories")
    parser.add_argument("--apply-move", action="store_true", help="Submit move request if direct docs-to-wiki move lacks permission")
    parser.add_argument("--exclude", action="append", default=[], help="Glob pattern to exclude, relative to source root; can be repeated")
    parser.add_argument("--output", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    source = Path(args.source)
    state_path = Path(args.state)
    exclude = args.exclude + ["**/.DS_Store", "**/node_modules/**"]
    md_files = collect_markdown(source, exclude)

    if not md_files:
        print("No Markdown files found.", file=sys.stderr)
        return 1

    if args.execute:
        missing = [name for name, value in (
            ("FEISHU_APP_ID/--app-id", args.app_id),
            ("FEISHU_APP_SECRET/--app-secret", args.app_secret),
        ) if not value]
        if missing:
            print(f"Missing required config for execute mode: {', '.join(missing)}", file=sys.stderr)
            return 2

    state = load_state(state_path)
    client = FeishuClient(args.app_id, args.app_secret, base_url=args.base_url)
    resolved_target: dict[str, Any] | None = None
    target_space_id = args.target_space_id
    target_parent_token = args.target_parent_token
    if args.execute:
        target_space_id, target_parent_token, resolved_target = resolve_wiki_target(
            client,
            target_space_id=args.target_space_id,
            target_parent_token=args.target_parent_token,
            target_url=args.target_url,
        )
        if not target_space_id:
            print("Missing target Wiki space. Set FEISHU_TARGET_SPACE_ID/--target-space-id or FEISHU_TARGET_URL/--target-url.", file=sys.stderr)
            return 2

    events: list[dict[str, Any]] = []

    for md in md_files:
        parent_token = target_parent_token
        if not args.flat:
            parent_token = ensure_directory_pages(
                client,
                state,
                directory_chain(md.rel_path),
                target_space_id=target_space_id,
                root_parent_token=target_parent_token,
                execute=args.execute,
                output_events=events,
            )
        events.append(
            publish_file(
                client,
                md,
                state,
                target_space_id=target_space_id,
                parent_token=parent_token,
                execute=args.execute,
                update_existing=args.update_existing,
                force_reimport=args.force_reimport,
                apply_move=args.apply_move,
            )
        )

    if args.execute:
        save_state(state_path, state)

    result = {
        "dry_run": not args.execute,
        "source": str(source.expanduser().resolve()),
        "state": str(state_path.expanduser().resolve()),
        "target_url": args.target_url,
        "target_space_id": target_space_id,
        "target_parent_token": target_parent_token,
        "resolved_target": resolved_target,
        "total_markdown_files": len(md_files),
        "events": events,
    }
    if args.output == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        mode = "Dry Run" if result["dry_run"] else "Published"
        print(f"# Feishu Wiki Publish {mode}")
        print()
        print(f"- source: `{result['source']}`")
        print(f"- state: `{result['state']}`")
        if args.target_url:
            print(f"- target_url: `{args.target_url}`")
        if target_space_id:
            print(f"- target_space_id: `{target_space_id}`")
        if target_parent_token:
            print(f"- target_parent_token: `{target_parent_token}`")
        print(f"- markdown files: {len(md_files)}")
        print()
        for event in events:
            print(f"- {event['action']}: `{event.get('path') or event.get('dir')}`")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
