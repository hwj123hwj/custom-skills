#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "python-dotenv",
#     "requests",
#     "psycopg2-binary"
# ]
# ///
"""
夜间知识收割脚本 v3
- 防风控：搜索/读取随机延迟
- 多集教程过滤
- 支持dry-run测试

用法: python nightly_harvest.py [--dry-run] [--keywords "AI Agent,AutoResearch"]
"""

import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
import requests

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# 配置
SCRIPTS = str(Path(__file__).parent)
VENV = str(Path(__file__).parent.parent / ".venv" / "bin" / "python3")
RESULTS_FILE = str(Path(__file__).parent.parent / "harvest_log.tsv")

DEFAULT_KEYWORDS = ["像素范", "水球泡", "一人公司", "AI焦虑", "AI Agent"]
PER_KEYWORD_LIMIT = 3
DELAY_SEARCH = (3, 8)
DELAY_READ = (2, 5)
DELAY_KEYWORD = (5, 10)
PROXY_ENV = {"http_proxy": "http://127.0.0.1:7890", "https_proxy": "http://127.0.0.1:7890"}

# 飞书通知配置
FEISHU_WEBHOOK = os.environ.get("FEISHU_WEBHOOK", "")  # 可选webhook
USER_OPEN_ID = "ou_0b6b3bb53deb827e26c5702e95582e46"  # 黄威健


def send_feishu_alert(title: str, content: str):
    """发送飞书通知（通过webhook或OpenClaw）"""
    if not FEISHU_WEBHOOK:
        # 无webhook时写入提醒文件，由heartbeat处理
        alert_file = Path(__file__).parent.parent / "alerts" / "cookie_expired.txt"
        alert_file.parent.mkdir(exist_ok=True)
        alert_file.write_text(f"{datetime.now().isoformat()}\n{title}\n{content}")
        return False

    try:
        import requests
        resp = requests.post(
            FEISHU_WEBHOOK,
            json={"msg_type": "text", "content": {"text": f"⚠️ {title}\n{content}"}},
            timeout=10,
        )
        return resp.status_code == 200
    except Exception as e:
        print(f"飞书通知失败: {e}")
        return False


def get_env():
    env = os.environ.copy()
    env.update(PROXY_ENV)
    return env


def run(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, env=get_env())
        return r.returncode == 0, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "TIMEOUT"


def safe_sleep(low, high):
    delay = random.uniform(low, high)
    time.sleep(delay)
    return delay


def harvest_xhs(keyword, limit=3):
    results = []
    xhs_out = subprocess.run(
        f"xhs search '{keyword}' --sort popular --json",
        shell=True, capture_output=True, text=True, timeout=15, env=get_env()
    )
    out_text = "\n".join(l for l in xhs_out.stdout.split("\n") if "WARNING" not in l and l.strip())

    try:
        data = json.loads(out_text)

        # 检测cookie失效（错误码-104）
        if not data.get("ok") and data.get("error", {}).get("code") == "api_error":
            err_msg = data.get("error", {}).get("message", "")
            if "-104" in err_msg or "没有权限" in err_msg or "登录" in err_msg:
                print(f"⚠️ 小红书cookie失效！")
                send_feishu_alert(
                    "小红书Cookie失效",
                    "请登录小红书网页版，导出cookie并发给我。\n"
                    "格式：loadts=xxx; web_session=xxx; ..."
                )
                return []

        items = data.get("data", {}).get("items", [])
    except Exception:
        return []

    for i, item in enumerate(items[:limit]):
        note = item.get("note_card", {})
        note_id = item.get("id", "")
        title = note.get("display_title", "无标题")
        if not note_id or note_id.startswith("#"):
            continue

        if i > 0:
            safe_sleep(*DELAY_READ)

        ok2, out2, _ = run(f"xhs read {note_id} --yaml 2>/dev/null | grep -v WARNING", timeout=15)
        desc = ""
        if ok2 and out2:
            try:
                import yaml
                d = yaml.safe_load(out2)
                items2 = d.get("data", {}).get("items", [])
                if items2:
                    desc = items2[0].get("note_card", {}).get("desc", "")
            except Exception:
                pass

        results.append({
            "source_type": "xiaohongshu",
            "source_id": note_id,
            "title": title,
            "content": desc or title,
            "source_url": f"https://www.xiaohongshu.com/discovery/item/{note_id}",
        })

    return results


def asr_video(bvid, title):
    """下载B站视频音频并用SiliconFlow ASR转录"""
    import tempfile
    import requests

    # 1. 下载音频
    audio_dir = tempfile.mkdtemp(prefix="bili_asr_")
    audio_file = os.path.join(audio_dir, "audio.m4a")

    ok, out, err = run(f"bili audio {bvid} --no-split -o {audio_dir} 2>&1", timeout=120)
    if not ok:
        print(f"      音频下载失败: {err[:50]}")
        return None

    # 找实际文件名
    actual_files = [f for f in os.listdir(audio_dir) if f.endswith(".m4a")]
    if not actual_files:
        print(f"      音频文件不存在")
        return None
    audio_file = os.path.join(audio_dir, actual_files[0])

    # 2. SiliconFlow ASR
    api_key = os.environ.get("SILICONFLOW_API_KEY")
    if not api_key:
        print(f"      无SILICONFLOW_API_KEY")
        return None

    print(f"      ASR转录中...")
    try:
        with open(audio_file, "rb") as f:
            resp = requests.post(
                "https://api.siliconflow.cn/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {api_key}"},
                files={"file": f},
                data={"model": "TeleAI/TeleSpeechASR"},
                timeout=180,
                proxies={"http": PROXY_ENV["http_proxy"], "https": PROXY_ENV["https_proxy"]}
            )

        if resp.status_code == 200:
            text = resp.json().get("text", "")
            print(f"      ASR成功: {len(text)} 字")
            return text
        else:
            print(f"      ASR失败: {resp.status_code} - {resp.text[:100]}")
            return None
    except Exception as e:
        print(f"      ASR异常: {e}")
        return None
    finally:
        # 清理临时文件
        shutil.rmtree(audio_dir, ignore_errors=True)


def harvest_bili(keyword, limit=3, use_asr=True):
    ok, out, _ = run(f"bili search --type video --json -n {limit * 2} '{keyword}' 2>/dev/null")
    if not ok or not out:
        return []

    try:
        data = json.loads(out)
        items = data.get("data", [])
    except json.JSONDecodeError:
        return []

    results = []
    for idx, item in enumerate(items):
        bvid = item.get("bvid", "")
        title = item.get("title", "无标题")
        duration_str = item.get("duration", "0:0")

        if not bvid:
            continue

        # 过滤多集教程
        junk_hits = sum(1 for kw in ["全", "集", "零基础", "从入门到", "从零开始",
            "最全最细", "最全最详细", "系统课", "完整版"] if kw in title)
        if junk_hits >= 2 or re.search(r"\d{2,}集", title):
            print(f"    跳过(多集教程): {title[:40]}")
            continue

        # 过滤超长视频（>30分钟不ASR，太慢）
        try:
            mins, secs = duration_str.split(":")
            duration_min = int(mins) + int(secs) / 60
        except:
            duration_min = 0

        content = f"作者: {item.get('author', '?')} | 播放: {item.get('play', 0)} | 时长: {duration_str}"

        # ASR转录（只对时长<30分钟的）
        if use_asr and duration_min > 0 and duration_min < 30:
            if idx > 0:
                safe_sleep(10, 20)  # ASR间隔长一些

            asr_text = asr_video(bvid, title)
            if asr_text:
                content = asr_text

        results.append({
            "source_type": "bilibili",
            "source_id": bvid,
            "title": title,
            "content": content,
            "source_url": f"https://www.bilibili.com/video/{bvid}",
        })

        if len(results) >= limit:
            break

    return results


def save_to_knowledge(items):
    saved = 0
    skipped = 0
    for item in items:
        ok, out, _ = run(
            f'{VENV} {SCRIPTS}/knowledge_search.py '
            f'--query "{item["source_id"]}" --mode keyword --limit 1',
            timeout=15
        )
        if ok and out:
            try:
                data = json.loads(out)
                if any(r.get("source_id") == item["source_id"] for r in data.get("results", [])):
                    skipped += 1
                    continue
            except json.JSONDecodeError:
                pass

        escaped_title = item["title"].replace('"', '\\"').replace("'", "\\'")
        escaped_content = item["content"].replace('"', '\\"').replace("'", "\\'")[:2000]

        ok, out, _ = run(
            f'{VENV} {SCRIPTS}/knowledge_save.py '
            f'--source-type {item["source_type"]} '
            f'--source-id {item["source_id"]} '
            f'--title "{escaped_title}" '
            f'--content "{escaped_content}" '
            f'--source-url "{item.get("source_url", "")}"',
            timeout=30
        )

        if ok:
            try:
                data = json.loads(out)
                if data.get("success"):
                    saved += 1
                else:
                    skipped += 1
            except json.JSONDecodeError:
                skipped += 1
        else:
            skipped += 1

    return saved, skipped


def main():
    parser = argparse.ArgumentParser(description="夜间知识收割")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keywords", help="逗号分隔")
    parser.add_argument("--limit", type=int, default=PER_KEYWORD_LIMIT)
    args = parser.parse_args()

    keywords = args.keywords.split(",") if args.keywords else DEFAULT_KEYWORDS
    limit = args.limit
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    print(f"{'='*50}")
    print(f"🌙 夜间知识收割 v3 — {ts}")
    print(f"{'='*50}")
    print(f"关键词: {keywords}")
    print(f"每词爬取: {limit}")
    print(f"搜索延迟: {DELAY_SEARCH[0]}~{DELAY_SEARCH[1]}秒")
    print(f"读取延迟: {DELAY_READ[0]}~{DELAY_READ[1]}秒")

    print(f"\n📡 Step 1: 爬取内容")
    all_items = []

    for kw_idx, kw in enumerate(keywords):
        if kw_idx > 0:
            safe_sleep(*DELAY_KEYWORD)

        print(f"\n  小红书 '{kw}':")
        xhs_items = harvest_xhs(kw, limit)
        print(f"    找到 {len(xhs_items)} 条")
        all_items.extend(xhs_items)

        safe_sleep(*DELAY_SEARCH)

        print(f"  B站 '{kw}':")
        bili_items = harvest_bili(kw, limit)
        print(f"    找到 {len(bili_items)} 条")
        all_items.extend(bili_items)

    print(f"\n  总计: {len(all_items)} 条")

    if args.dry_run:
        print(f"\n爬取结果 ({len(all_items)} 条):")
        for item in all_items:
            print(f"  [{item['source_type']}] {item['title'][:50]}")
        print("\n(dry-run 模式，不入库)")
        # 保存结果到文件
        result_path = f"/tmp/harvest_{datetime.now().strftime('%Y-%m-%d')}.md"
        with open(result_path, "w") as f:
            f.write(f"# 夜间知识收割 {ts}\n\n")
            f.write(f"总计: {len(all_items)} 条\n\n")
            for item in all_items:
                f.write(f"- [{item['source_type']}] [{item['title']}]({item['source_url']})\n")
        print(f"\n结果已保存: {result_path}")
        return

    print(f"\n💾 Step 2: 入库")
    saved, skipped = save_to_knowledge(all_items)
    print(f"  新增: {saved}, 跳过: {skipped}")

    with open(RESULTS_FILE, "a") as f:
        if os.stat(RESULTS_FILE).st_size == 0:
            f.write("timestamp\tsaved\tskipped\ttotal_found\n")
        f.write(f"{ts}\t{saved}\t{skipped}\t{len(all_items)}\n")

    print(f"\n✅ 收割完成! 入库: {saved} 条 | 跳过: {skipped} 条")


if __name__ == "__main__":
    main()
