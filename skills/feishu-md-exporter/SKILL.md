---
name: feishu-md-exporter
displayName: Feishu Markdown Exporter
description: Export Feishu/Lark docs or entire Drive folders to local Markdown using the official Open Platform APIs. Use this skill whenever the user asks to export a Feishu/Lark document, docx link, wiki/doc link, Drive folder, folder tree, or batch of Feishu docs to md/Markdown, especially for personal backups of documents that are viewable but not copy/export enabled.
tags:
  - Automation
  - Productivity
  - LocalData
  - Utility
aliases:
  - 飞书文档导出
  - 飞书转 Markdown
  - 飞书文件夹导出
  - Lark 文档导出
scenarios:
  - 导出单个飞书文档为 Markdown
  - 递归导出飞书 Drive 文件夹为 Markdown 目录树
  - 备份有查看权限但禁用复制或导出的飞书文档
version: 0.1.0
---

# Feishu Markdown Exporter

Use this skill to export Feishu/Lark documents to Markdown. It supports the two common personal workflows:

1. Export one Feishu/Lark document URL to `.md`.
2. Recursively export a Feishu/Lark Drive folder tree to local `.md` files.

The implementation uses official Feishu Open Platform APIs:

- OAuth user authorization to obtain `user_access_token`.
- Drive folder listing API for folder recursion.
- Docx document metadata and blocks APIs to read document content.
- Local conversion from Feishu block JSON to Markdown.

It does not crack private documents or bypass view permissions. The user must have view access, and the app must have the required API scopes. It can still export Markdown when the UI disables copy/export, because reading document blocks and official file export are separate permission surfaces.

## Script

Run the bundled script:

```bash
python /Users/weijian/.agents/skills/feishu-md-exporter/scripts/export_feishu_md.py <feishu-url> --output <output-dir>
```

For a single document:

```bash
python /Users/weijian/.agents/skills/feishu-md-exporter/scripts/export_feishu_md.py \
  "https://example.feishu.cn/docx/xxxxx" \
  --output ./feishu_md_exports
```

For a folder:

```bash
python /Users/weijian/.agents/skills/feishu-md-exporter/scripts/export_feishu_md.py \
  "https://example.feishu.cn/drive/folder/xxxxx" \
  --output ./feishu_md_exports
```

## Credentials

Prefer environment variables:

```bash
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
```

Or pass them explicitly:

```bash
python scripts/export_feishu_md.py <url> --app-id cli_xxx --app-secret xxx
```

Or store them in:

```text
~/.feishu-md-exporter/config.json
```

Format:

```json
{
  "app_id": "cli_xxx",
  "app_secret": "xxx"
}
```

The OAuth token cache is stored at:

```text
~/.feishu-md-exporter/token_cache.json
```

## Required Feishu App Setup

In the Feishu/Lark developer console:

1. Add redirect URL exactly:

```text
http://localhost:9876/callback
```

2. Enable and publish the relevant scopes:

```text
docx:document:readonly
wiki:wiki:readonly
drive:drive:readonly
drive:file:readonly
```

`drive:export:readonly` is not required for Markdown block export, but it is harmless if already enabled.

3. On first run, complete the OAuth page in the browser.

## Workflow

1. Identify whether the URL is a single document, wiki node, or Drive folder.
2. If credentials are missing, ask for `app_id` and `app_secret`, or ask the user to create `~/.feishu-md-exporter/config.json`.
3. Run the script with a clear output directory.
4. If OAuth opens in the browser, tell the user to approve it. If the page says redirect URL error, tell them to add `http://localhost:9876/callback` under Security Settings -> Redirect URL.
5. After export, report:
   - Output directory or file path.
   - Number of Markdown files exported.
   - Any failed or skipped items.

## Common Errors

- `redirect URL error` / code `20029`: the app did not configure `http://localhost:9876/callback` as a redirect URL.
- `no permission` / `403`: the user or app lacks view/API permission for the document or folder.
- `scope` or authorization error: add and publish the required scopes, then delete `~/.feishu-md-exporter/token_cache.json` and retry.
- Folder export returns no docs: verify the URL is a Drive folder URL and the user has view access to the folder contents.

## Output Behavior

- Folder export preserves the Feishu folder tree locally.
- Unsupported path characters such as `/` are replaced with `_`.
- Duplicate names receive suffixes like `_2`.
- Images and files may be represented as placeholders if the Blocks API returns only tokens and the script does not download binary assets.

Keep the user-facing response short: say whether it worked, where the files are, and the counts.
