#!/usr/bin/env python3
"""
B站字幕获取脚本 - 自动从浏览器读取 cookies 并获取视频字幕

功能：
- 自动检测已登录的浏览器并获取 B站 cookies
- 通过 B站 API 直接获取 AI 生成字幕（比本地 ASR 更快更准）
- 输出标准 SRT 格式字幕文件

Cookies 获取优先级：
1. yt-dlp --cookies-from-browser（最可靠，持续跟进浏览器加密更新）
2. browser_cookie3 Python 库（备选）
3. 手动配置 ~/.bilibili_cookies.txt 或环境变量（兜底）

用法：
    python fetch_bilibili_subtitle.py <BV号或URL> <输出SRT路径> [--browser chrome|firefox|safari|edge]

示例：
    python fetch_bilibili_subtitle.py BV1vdZ6BJEcQ output.srt
    python fetch_bilibili_subtitle.py "https://www.bilibili.com/video/BV1vdZ6BJEcQ/" output.srt
    python fetch_bilibili_subtitle.py BV1vdZ6BJEcQ output.srt --browser firefox
"""

import subprocess
import sys
import os
import re
import json
import tempfile
import argparse
from pathlib import Path

try:
    import requests
except ImportError:
    print(" requests 未安装: pip install requests")
    sys.exit(1)


# ============================================================
# BV号/URL 解析
# ============================================================

def extract_bvid(input_str: str) -> str:
    """从 URL、BV号 或文件名中提取 BV号"""
    # 直接是 BV号
    match = re.search(r'(BV[a-zA-Z0-9]{10})', input_str)
    if match:
        return match.group(1)

    # 短链需要解析重定向
    if 'b23.tv' in input_str:
        try:
            resp = requests.head(input_str, allow_redirects=True, timeout=10)
            match = re.search(r'(BV[a-zA-Z0-9]{10})', resp.url)
            if match:
                return match.group(1)
        except Exception:
            pass

    return ""


# ============================================================
# Cookies 获取策略
# ============================================================

def get_cookies_via_ytdlp(browser: str = "chrome") -> dict:
    """
    策略1: 通过 yt-dlp 从浏览器获取 cookies（最可靠）
    yt-dlp 持续跟进浏览器加密更新，比第三方库更稳定
    """
    print(f"    尝试从 {browser} 获取 cookies (via yt-dlp)...")

    try:
        # 用 yt-dlp 导出 cookies 到临时文件
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode='w') as tmp:
            cookies_file = tmp.name

        cmd = [
            "yt-dlp",
            "--cookies-from-browser", browser,
            "--cookies", cookies_file,
            "--skip-download",
            "--no-warnings",
            "-q",
            "https://www.bilibili.com/video/BV1xx411c7mD/",  # 任意有效BV号
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if os.path.exists(cookies_file) and os.path.getsize(cookies_file) > 0:
            cookies = _parse_netscape_cookies(cookies_file, ".bilibili.com")
            os.unlink(cookies_file)

            if cookies.get("SESSDATA"):
                print(f"    成功获取 cookies (SESSDATA={cookies['SESSDATA'][:8]}...)")
                return cookies
            else:
                print(f"    cookies 中无 SESSDATA（可能未登录B站）")
                return {}
        else:
            os.unlink(cookies_file) if os.path.exists(cookies_file) else None
            print(f"    yt-dlp 未能导出 cookies")
            return {}

    except FileNotFoundError:
        print(f"    yt-dlp 未安装，跳过")
        return {}
    except subprocess.TimeoutExpired:
        print(f"    yt-dlp 超时（可能需要系统钥匙串权限）")
        return {}
    except Exception as e:
        print(f"    yt-dlp 获取失败: {e}")
        return {}


def get_cookies_via_browser_cookie3(browser: str = "chrome") -> dict:
    """
    策略2: 通过 browser_cookie3 库获取 cookies
    注意: Chrome 2024年后新加密可能导致部分 cookies 值为空
    """
    print(f"    尝试从 {browser} 获取 cookies (via browser_cookie3)...")

    try:
        import browser_cookie3

        browser_map = {
            "chrome": browser_cookie3.chrome,
            "firefox": browser_cookie3.firefox,
            "edge": browser_cookie3.edge,
            "opera": browser_cookie3.opera,
        }

        if browser not in browser_map:
            print(f"    browser_cookie3 不支持 {browser}")
            return {}

        cj = browser_map[browser](domain_name=".bilibili.com")
        cookies = {}
        for cookie in cj:
            if cookie.domain and ".bilibili.com" in cookie.domain:
                cookies[cookie.name] = cookie.value

        if cookies.get("SESSDATA"):
            print(f"    成功获取 cookies (SESSDATA={cookies['SESSDATA'][:8]}...)")
            return cookies
        else:
            print(f"    cookies 中无 SESSDATA（可能未登录或加密问题）")
            return {}

    except ImportError:
        print(f"    browser_cookie3 未安装，跳过 (pip install browser_cookie3)")
        return {}
    except Exception as e:
        print(f"    browser_cookie3 获取失败: {e}")
        return {}


def get_cookies_from_config() -> dict:
    """
    策略3: 从配置文件或环境变量获取 cookies（兜底方案）

    支持：
    - 环境变量: BILIBILI_SESSDATA, BILIBILI_BILI_JCT
    - cookies 文件: ~/.bilibili_cookies.txt (Netscape 格式)
    """
    print("    尝试从配置文件/环境变量获取 cookies...")

    cookies = {}

    # 方式A: 环境变量
    sessdata = os.environ.get("BILIBILI_SESSDATA", "")
    if sessdata:
        cookies["SESSDATA"] = sessdata
        bili_jct = os.environ.get("BILIBILI_BILI_JCT", "")
        if bili_jct:
            cookies["bili_jct"] = bili_jct
        print(f"    从环境变量获取 (SESSDATA={sessdata[:8]}...)")
        return cookies

    # 方式B: Netscape cookies 文件
    cookies_file = os.path.expanduser("~/.bilibili_cookies.txt")
    if os.path.exists(cookies_file):
        cookies = _parse_netscape_cookies(cookies_file, ".bilibili.com")
        if cookies.get("SESSDATA"):
            print(f"    从 {cookies_file} 获取 (SESSDATA={cookies['SESSDATA'][:8]}...)")
            return cookies

    print("    未找到配置的 cookies")
    return {}


def _parse_netscape_cookies(filepath: str, domain_filter: str = "") -> dict:
    """解析 Netscape 格式 cookies 文件"""
    cookies = {}
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('\t')
                    if len(parts) >= 7:
                        domain = parts[0]
                        name = parts[5]
                        value = parts[6]
                        if not domain_filter or domain_filter in domain:
                            cookies[name] = value
    except Exception:
        pass
    return cookies


def get_bilibili_cookies(preferred_browser: str = "chrome") -> dict:
    """
    按优先级尝试获取 B站 cookies

    优先级：yt-dlp > browser_cookie3 > 配置文件/环境变量
    """
    print("\n 获取 B站 cookies...")

    # 要尝试的浏览器列表
    browsers = [preferred_browser]
    for b in ["chrome", "firefox", "edge", "safari"]:
        if b not in browsers:
            browsers.append(b)

    # 策略1: yt-dlp（按浏览器优先级）
    for browser in browsers:
        cookies = get_cookies_via_ytdlp(browser)
        if cookies.get("SESSDATA"):
            return cookies

    # 策略2: browser_cookie3（按浏览器优先级）
    for browser in browsers:
        cookies = get_cookies_via_browser_cookie3(browser)
        if cookies.get("SESSDATA"):
            return cookies

    # 策略3: 配置文件/环境变量
    cookies = get_cookies_from_config()
    if cookies.get("SESSDATA"):
        return cookies

    return {}


# ============================================================
# B站 API 字幕获取
# ============================================================

def fetch_subtitle(bvid: str, cookies: dict, output_srt: str) -> bool:
    """通过 B站 API 获取字幕并保存为 SRT"""

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://www.bilibili.com",
    }

    try:
        # 步骤1: BV号 → CID
        print("\n 调用 B站 API...")
        url = f"https://api.bilibili.com/x/player/pagelist?bvid={bvid}"
        resp = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        data = resp.json()

        if data.get("code") != 0 or not data.get("data"):
            print(f"    获取视频信息失败: {data.get('message', '未知错误')}")
            return False

        cid = data["data"][0]["cid"]
        part_name = data["data"][0].get("part", "")
        duration = data["data"][0].get("duration", 0)
        print(f"    视频: {part_name} (时长: {duration}s, CID: {cid})")

        # 步骤2: 获取 AID
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        resp = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        data = resp.json()

        if data.get("code") != 0:
            print(f"    获取AID失败: {data.get('message', '未知错误')}")
            return False

        aid = data["data"]["aid"]
        title = data["data"].get("title", "")
        print(f"    标题: {title}")

        # 步骤3: 获取字幕列表
        url = f"https://api.bilibili.com/x/player/wbi/v2?aid={aid}&cid={cid}"
        resp = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        data = resp.json()

        if data.get("code") != 0:
            print(f"    获取字幕信息失败: {data.get('message', '未知错误')}")
            return False

        subtitles = data.get("data", {}).get("subtitle", {}).get("subtitles", [])

        if not subtitles:
            print("    该视频无字幕（未开启AI字幕或需要登录）")
            return False

        # 显示可用字幕
        print(f"    可用字幕: {len(subtitles)} 条")
        for s in subtitles:
            print(f"      - {s.get('lan_doc', '?')} ({s.get('lan', '?')})")

        # 选择中文字幕（优先 ai-zh）
        chosen = subtitles[0]
        for s in subtitles:
            if s.get("lan") in ("ai-zh", "zh-Hans", "zh-CN", "zh"):
                chosen = s
                break

        subtitle_url = chosen.get("subtitle_url", "")
        if not subtitle_url:
            print("    字幕URL为空")
            return False

        if subtitle_url.startswith("//"):
            subtitle_url = "https:" + subtitle_url

        # 步骤4: 下载字幕 JSON
        resp = requests.get(subtitle_url, headers=headers, timeout=10)
        subtitle_data = resp.json()

        body = subtitle_data.get("body", [])
        if not body:
            print("    字幕内容为空")
            return False

        # 步骤5: 转换为 SRT 格式
        with open(output_srt, 'w', encoding='utf-8') as f:
            for i, item in enumerate(body, 1):
                start = item.get("from", 0)
                end = item.get("to", 0)
                content = item.get("content", "").strip()

                if content:
                    start_ts = _format_srt_timestamp(start)
                    end_ts = _format_srt_timestamp(end)
                    f.write(f"{i}\n{start_ts} --> {end_ts}\n{content}\n\n")

        print(f"\n 字幕获取成功！")
        print(f"   条数: {len(body)}")
        print(f"   语言: {chosen.get('lan_doc', '未知')}")
        print(f"   输出: {output_srt}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"    网络请求失败: {e}")
        return False
    except Exception as e:
        print(f"    字幕获取失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def _format_srt_timestamp(seconds: float) -> str:
    """格式化时间戳为 SRT 格式 HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="从 B站获取视频字幕（自动读取浏览器 cookies）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python fetch_bilibili_subtitle.py BV1vdZ6BJEcQ output.srt
    python fetch_bilibili_subtitle.py "https://b23.tv/W2ot8As" output.srt
    python fetch_bilibili_subtitle.py BV1vdZ6BJEcQ output.srt --browser firefox

Cookies 获取优先级:
    1. yt-dlp --cookies-from-browser（最可靠）
    2. browser_cookie3 Python 库
    3. ~/.bilibili_cookies.txt 或环境变量 BILIBILI_SESSDATA

如果所有自动方式都失败，可以手动配置:
    export BILIBILI_SESSDATA="你的SESSDATA值"
    export BILIBILI_BILI_JCT="你的bili_jct值"
        """
    )
    parser.add_argument("input", help="B站 BV号 或 视频URL")
    parser.add_argument("output", help="输出 SRT 文件路径")
    parser.add_argument("--browser", default="chrome",
                        help="优先使用的浏览器 (default: chrome)")

    args = parser.parse_args()

    # 解析 BV号
    print("=" * 50)
    print(" B站字幕获取工具")
    print("=" * 50)

    bvid = extract_bvid(args.input)
    if not bvid:
        print(f" 无法解析 BV号: {args.input}")
        sys.exit(1)

    print(f" BV号: {bvid}")

    # 获取 cookies
    cookies = get_bilibili_cookies(args.browser)
    if not cookies.get("SESSDATA"):
        print("\n 无法获取 B站 cookies，请确保：")
        print("   1. 已在浏览器中登录 bilibili.com")
        print("   2. 已安装 yt-dlp: pip install yt-dlp")
        print("   3. 或安装 browser_cookie3: pip install browser_cookie3")
        print("   4. 或手动设置: export BILIBILI_SESSDATA='你的值'")
        sys.exit(1)

    # 获取字幕
    success = fetch_subtitle(bvid, cookies, args.output)

    if success:
        sys.exit(0)
    else:
        print("\n 提示: 如果字幕获取失败，可以回退到本地转录方式:")
        print("   python scripts/transcribe_api.py <视频文件> <输出SRT>")
        sys.exit(1)


if __name__ == "__main__":
    main()
