#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Offline self-test for knowledge_publish_feishu.py.

This test uses a fake client and local temp files, so it does not need Feishu
credentials or network access.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("knowledge_publish_feishu.py")


def load_module():
    spec = importlib.util.spec_from_file_location("knowledge_publish_feishu", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeClient:
    def __init__(self):
        self.calls: list[tuple] = []

    def get_wiki_node(self, token_or_url: str):
        self.calls.append(("get_wiki_node", token_or_url))
        return {"space_id": "spc_fake", "node_token": "wik_parent"}

    def create_directory_document(self, title: str):
        self.calls.append(("create_directory_document", title))
        return {"doc_token": f"doc_dir_{title}", "url": f"https://fake/docx/doc_dir_{title}"}

    def move_doc_to_wiki(self, doc_token: str, target_space_id: str, parent_token: str = "", apply: bool = False):
        self.calls.append(("move_doc_to_wiki", doc_token, target_space_id, parent_token, apply))
        return {"ready": True, "wiki_token": f"wik_{doc_token}"}

    def upload_import_media(self, md):
        self.calls.append(("upload_import_media", md.rel_path))
        return "file_token_fake"

    def create_import_task(self, md, file_token: str, folder_token: str = ""):
        self.calls.append(("create_import_task", md.rel_path, file_token, folder_token))
        return "ticket_fake"

    def poll_import_task(self, ticket: str):
        self.calls.append(("poll_import_task", ticket))
        return {"token": "doc_imported", "url": "https://fake/docx/doc_imported"}


def main() -> int:
    mod = load_module()

    assert mod.extract_feishu_ref("https://x.feishu.cn/wiki/wikcn123?from=copy") == ("wikcn123", "")
    assert mod.extract_feishu_ref("https://x.feishu.cn/docx/docx123") == ("docx123", "docx")
    assert mod.extract_feishu_ref("https://x.feishu.cn/sheets/sht123") == ("sht123", "sheet")
    assert mod.extract_feishu_token("wik_raw") == "wik_raw"

    client = FakeClient()
    space, parent, node = mod.resolve_wiki_target(
        client,
        target_space_id="",
        target_parent_token="",
        target_url="https://x.feishu.cn/wiki/wik_parent",
    )
    assert (space, parent, node["node_token"]) == ("spc_fake", "wik_parent", "wik_parent")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        md_dir = root / "topic"
        md_dir.mkdir()
        path = md_dir / "note.md"
        path.write_text("# Note\n\nBody\n", encoding="utf-8")
        md = mod.collect_markdown(root, [])[0]
        state = {"version": 1, "directories": {}, "files": {}}
        parent_token = mod.ensure_directory_pages(
            client,
            state,
            mod.directory_chain(md.rel_path),
            target_space_id=space,
            root_parent_token=parent,
            execute=True,
            output_events=[],
        )
        result = mod.publish_file(
            client,
            md,
            state,
            target_space_id=space,
            parent_token=parent_token,
            execute=True,
            update_existing=False,
            force_reimport=False,
            apply_move=False,
        )

    assert result["action"] == "imported_and_moved"
    assert result["doc_token"] == "doc_imported"
    assert result["wiki_token"] == "wik_doc_imported"
    assert state["directories"]["topic"]["wiki_token"] == "wik_doc_dir_topic"
    assert state["files"]["topic/note.md"]["doc_token"] == "doc_imported"
    print("knowledge_publish_feishu self-test ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
