"""
cli.py — Douyin upload CLI entry point.

Commands:
  douyin login          --account <name> [--headed|--headless]
  douyin check          --account <name>
  douyin verify         --account <name> --code <6-digit>
  douyin upload-video   --account <name> --file <path> --title <str>
                        [--desc <str>] [--tags <tag1,tag2>]
                        [--schedule "YYYY-MM-DD HH:MM"]
                        [--thumbnail <path>]
                        [--product-link <url> --product-title <str>]
                        [--headed|--headless]
  douyin upload-note    --account <name> --images <p1> [<p2> ...]
                        --title <str> [--note <str>] [--tags <tag1,tag2>]
                        [--schedule "YYYY-MM-DD HH:MM"]
                        [--headed|--headless]
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from conf import BASE_DIR
from uploader.douyin_uploader.main import (
    DOUYIN_PUBLISH_STRATEGY_IMMEDIATE,
    DOUYIN_PUBLISH_STRATEGY_SCHEDULED,
    DouYinNote,
    DouYinVideo,
    cookie_auth as douyin_cookie_auth,
    douyin_setup,
)

SCHEDULE_FORMAT = "%Y-%m-%d %H:%M"


# ─── Helpers ────────────────────────────────────────────────────────────────

def _resolve_account_file(account_name: str) -> Path:
    path = Path(BASE_DIR) / "cookies" / f"douyin_{account_name}.json"
    path.parent.mkdir(exist_ok=True)
    return path


def _parse_tags(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [t.strip().lstrip("#") for t in raw.split(",") if t.strip()]


def _parse_schedule(raw: str | None) -> datetime | int:
    if not raw:
        return 0
    return datetime.strptime(raw, SCHEDULE_FORMAT)


def _existing_file(value: str) -> Path:
    p = Path(value)
    if not p.is_file():
        raise argparse.ArgumentTypeError(f"File not found: {value}")
    return p


def _schedule_value(value: str) -> datetime:
    try:
        return _parse_schedule(value)
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            f"Invalid schedule '{value}'. Expected: {SCHEDULE_FORMAT}"
        ) from e


def _add_runtime_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--headed", dest="headless", action="store_false", help="Run with visible browser")
    g.add_argument("--headless", dest="headless", action="store_true", help="Run in headless mode")
    parser.set_defaults(headless=False)


# ─── Async actions ──────────────────────────────────────────────────────────

async def _login(account_name: str, headless: bool) -> None:
    account_file = _resolve_account_file(account_name)
    result = await douyin_setup(
        str(account_file), handle=True, return_detail=True, headless=headless
    )
    if result["success"]:
        print(f"[LOGIN_SUCCESS] account={account_name} file={account_file}", flush=True)
    else:
        print(f"[LOGIN_FAILED] account={account_name} reason={result['message']}", flush=True)
        sys.exit(1)


async def _check(account_name: str) -> None:
    account_file = _resolve_account_file(account_name)
    if not account_file.exists():
        print("invalid", flush=True)
        sys.exit(1)
    ok = await douyin_cookie_auth(str(account_file))
    print("valid" if ok else "invalid", flush=True)
    if not ok:
        sys.exit(1)


def _verify(account_name: str, code: str) -> None:
    account_file = _resolve_account_file(account_name)
    verify_path = account_file.parent / f"{account_file.stem}_verify_code.json"
    verify_path.write_text(json.dumps({"code": code}), encoding="utf-8")
    print(f"[VERIFY_WRITTEN] account={account_name} code={code}", flush=True)


async def _upload_video(
    account_name: str,
    file: Path,
    title: str,
    desc: str,
    tags: list[str],
    schedule: datetime | int,
    thumbnail: Path | None,
    product_link: str,
    product_title: str,
    headless: bool,
    debug: bool,
) -> None:
    account_file = _resolve_account_file(account_name)
    is_ready = await douyin_setup(str(account_file), handle=False)
    if not is_ready:
        print(
            f"[COOKIE_INVALID] account={account_name} — run: douyin login --account {account_name}",
            flush=True,
        )
        sys.exit(1)

    strategy = (
        DOUYIN_PUBLISH_STRATEGY_SCHEDULED
        if isinstance(schedule, datetime)
        else DOUYIN_PUBLISH_STRATEGY_IMMEDIATE
    )
    app = DouYinVideo(
        title=title,
        file_path=str(file),
        tags=tags,
        publish_date=schedule,
        account_file=str(account_file),
        desc=desc,
        thumbnail_portrait_path=str(thumbnail) if thumbnail else None,
        productLink=product_link,
        productTitle=product_title,
        publish_strategy=strategy,
        debug=debug,
        headless=headless,
    )
    await app.douyin_upload_video()
    print(f"[UPLOAD_SUCCESS] account={account_name} title={title}", flush=True)


async def _upload_note(
    account_name: str,
    images: list[Path],
    title: str,
    note: str,
    tags: list[str],
    schedule: datetime | int,
    headless: bool,
    debug: bool,
) -> None:
    account_file = _resolve_account_file(account_name)
    is_ready = await douyin_setup(str(account_file), handle=False)
    if not is_ready:
        print(
            f"[COOKIE_INVALID] account={account_name} — run: douyin login --account {account_name}",
            flush=True,
        )
        sys.exit(1)

    strategy = (
        DOUYIN_PUBLISH_STRATEGY_SCHEDULED
        if isinstance(schedule, datetime)
        else DOUYIN_PUBLISH_STRATEGY_IMMEDIATE
    )
    app = DouYinNote(
        image_paths=[str(p) for p in images],
        title=title,
        note=note,
        tags=tags,
        publish_date=schedule,
        account_file=str(account_file),
        publish_strategy=strategy,
        debug=debug,
        headless=headless,
    )
    await app.douyin_upload_note()
    print(f"[UPLOAD_SUCCESS] account={account_name} title={title}", flush=True)


# ─── CLI parser ─────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    fmt = SCHEDULE_FORMAT.replace("%", "%%")
    parser = argparse.ArgumentParser(prog="douyin", description="Douyin upload CLI")
    sub = parser.add_subparsers(dest="action", required=True)

    # login
    p_login = sub.add_parser("login", help="Login to Douyin and save cookie")
    p_login.add_argument("--account", required=True)
    _add_runtime_flags(p_login)

    # check
    p_check = sub.add_parser("check", help="Check if cookie is valid")
    p_check.add_argument("--account", required=True)

    # verify
    p_verify = sub.add_parser("verify", help="Submit SMS verification code")
    p_verify.add_argument("--account", required=True)
    p_verify.add_argument("--code", required=True, help="6-digit SMS code")

    # upload-video
    p_uv = sub.add_parser("upload-video", help="Upload a video to Douyin")
    p_uv.add_argument("--account", required=True)
    p_uv.add_argument("--file", required=True, type=_existing_file)
    p_uv.add_argument("--title", required=True)
    p_uv.add_argument("--desc", default="")
    p_uv.add_argument("--tags", default="", help="Comma-separated, e.g. tag1,tag2")
    p_uv.add_argument("--schedule", type=_schedule_value, help=f"Format: {fmt}")
    p_uv.add_argument("--thumbnail", type=_existing_file)
    p_uv.add_argument("--product-link", default="")
    p_uv.add_argument("--product-title", default="")
    _add_runtime_flags(p_uv)

    # upload-note
    p_un = sub.add_parser("upload-note", help="Upload an image note to Douyin")
    p_un.add_argument("--account", required=True)
    p_un.add_argument("--images", required=True, nargs="+", type=_existing_file)
    p_un.add_argument("--title", required=True)
    p_un.add_argument("--note", default="")
    p_un.add_argument("--tags", default="")
    p_un.add_argument("--schedule", type=_schedule_value, help=f"Format: {fmt}")
    _add_runtime_flags(p_un)

    return parser


# ─── Entry point ────────────────────────────────────────────────────────────

def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.action == "login":
        asyncio.run(_login(args.account, args.headless))

    elif args.action == "check":
        asyncio.run(_check(args.account))

    elif args.action == "verify":
        _verify(args.account, args.code)

    elif args.action == "upload-video":
        asyncio.run(
            _upload_video(
                account_name=args.account,
                file=args.file,
                title=args.title,
                desc=args.desc,
                tags=_parse_tags(args.tags),
                schedule=args.schedule or 0,
                thumbnail=args.thumbnail,
                product_link=args.product_link,
                product_title=args.product_title,
                headless=args.headless,
                debug=args.debug,
            )
        )

    elif args.action == "upload-note":
        asyncio.run(
            _upload_note(
                account_name=args.account,
                images=args.images,
                title=args.title,
                note=args.note,
                tags=_parse_tags(args.tags),
                schedule=args.schedule or 0,
                headless=args.headless,
                debug=args.debug,
            )
        )


if __name__ == "__main__":
    main()
