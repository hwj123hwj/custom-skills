#!/usr/bin/env python3
"""
抖音视频下载脚本
支持从抖音分享链接或分享文本中提取并下载视频（无水印版本）

 增强功能: 自动从分享文本中提取链接

使用方法:
    python download_douyin.py <抖音链接或分享文本> <输出路径>

示例:
    # 方式1: 纯链接
    python download_douyin.py "https://v.douyin.com/xxxxx" ./video.mp4

    # 方式2: 完整分享文本（自动提取链接）
    python download_douyin.py "3.00 12/31 以色列 https://v.douyin.com/xxxxx 打开抖音" ./video.mp4
"""

import requests
import re
import json
import sys
import os
import shutil
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlparse

# Windows CMD 编码修复：设置 UTF-8 输出
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python 3.6 及以下版本
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def extract_douyin_url_from_text(text: str) -> str:
    """
    从分享文本中提取抖音链接

    支持格式:
    - 纯链接: https://v.douyin.com/xxxxx
    - 分享文本: "3.00 12/31 复制此链接 https://v.douyin.com/xxxxx 打开抖音"
    - 混合文本: 包含标题、标签、链接的完整分享文本

    返回提取到的第一个有效抖音链接，如果没有则返回None
    """
    # 先尝试匹配 douyin.com/video/数字ID 格式（更具体，优先匹配）
    video_pattern = r'https?://(?:www\.)?douyin\.com/video/\d+'
    match = re.search(video_pattern, text)
    if match:
        url = match.group(0)
        print(f"ℹ  从分享文本中提取到链接: {url}")
        return url

    # 再尝试短链接格式
    url_pattern = r'https?://(?:v\.douyin\.com|m\.douyin\.com)/[A-Za-z0-9]+/?'
    match = re.search(url_pattern, text)
    if match:
        url = match.group(0)
        print(f"ℹ  从分享文本中提取到链接: {url}")
        return url

    return None


def is_douyin_url(url: str) -> bool:
    """检查是否为抖音链接"""
    douyin_patterns = [
        r'v\.douyin\.com',
        r'www\.douyin\.com',
        r'm\.douyin\.com',
        r'douyin\.com/video/',
        r'douyin\.com/jingxuan',
    ]
    return any(re.search(pattern, url) for pattern in douyin_patterns)


def extract_video_id(url: str) -> str:
    """从抖音链接中提取视频ID"""
    # 尝试从各种格式的链接中提取ID
    patterns = [
        r'/video/(\d+)',
        r'modal_id=(\d+)',
        r'share/video/(\d+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    # 如果是短链接，返回None，需要获取重定向后的URL
    return None


def get_redirect_url(short_url: str) -> tuple:
    """获取重定向后的完整URL"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }

    try:
        response = requests.get(short_url, headers=headers, allow_redirects=True, timeout=10)
        return response.url, headers['User-Agent'], response.text
    except Exception as e:
        print(f" 获取重定向URL失败: {e}")
        return None, None, None


def extract_render_data(html: str) -> dict:
    """从HTML中提取RENDER_DATA"""
    # 尝试多种可能的模式
    patterns = [
        r'<script id="RENDER_DATA" type="application/json">([^<]+)</script>',
        r'window\._ROUTER_DATA\s*=\s*(\{.+?\});?\s*</script>',
        r'window\._SSR_DATA\s*=\s*(\{.+?\});?\s*</script>',
        r'window\._SSR_HYDRATED_DATA\s*=\s*(\{.+?\});?\s*</script>',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, html, re.DOTALL)
        if matches:
            data_str = matches[0]
            # URL解码
            if '%' in data_str:
                data_str = unquote(data_str)
            try:
                return json.loads(data_str)
            except json.JSONDecodeError:
                continue

    return None


def extract_video_url(data: dict) -> str:
    """从RENDER_DATA中提取视频URL"""

    def get_nested(obj, path):
        """安全地获取嵌套字典/列表值"""
        current = obj
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and isinstance(key, int) and key < len(current):
                current = current[key]
            else:
                return None
        return current

    # 尝试多种可能的路径
    possible_paths = [
        ['loaderData', 'video_(id)/page', 'videoInfoRes', 'item_list', 0, 'video', 'play_addr', 'url_list'],
        ['loaderData', 'video_(id)/page', 'aweme_detail', 'video', 'play_addr', 'url_list'],
        ['videoInfoRes', 'item_list', 0, 'video', 'play_addr', 'url_list'],
        ['app', 'videoInfoRes', 'item_list', 0, 'video', 'play_addr', 'url_list'],
        ['app', 'videoDetail', 'video', 'play_addr', 'url_list'],
        ['video', 'play_addr', 'url_list'],
        ['aweme_detail', 'video', 'play_addr', 'url_list'],
    ]

    for path in possible_paths:
        url_list = get_nested(data, path)
        if url_list and isinstance(url_list, list) and len(url_list) > 0:
            video_url = url_list[0]
            # 替换playwm为play获取无水印版本
            video_url = video_url.replace('playwm', 'play')
            return video_url

    # 如果路径查找失败，尝试正则搜索
    json_str = json.dumps(data)
    play_patterns = [
        r'"play_addr":\s*\{[^}]*"url_list":\s*\["([^"]+)"',
        r'"playAddr":\s*\["([^"]+)"',
        r'"download_addr":\s*\{[^}]*"url_list":\s*\["([^"]+)"',
    ]

    for pattern in play_patterns:
        matches = re.findall(pattern, json_str)
        if matches:
            video_url = matches[0].replace('playwm', 'play')
            return video_url

    return None


def download_video(video_url: str, output_path: str, user_agent: str) -> bool:
    """下载视频"""
    headers = {
        'User-Agent': user_agent,
        'Referer': 'https://www.douyin.com/',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }

    try:
        response = requests.get(video_url, headers=headers, stream=True, timeout=60)

        if response.status_code not in [200, 206]:
            print(f" 下载失败，状态码: {response.status_code}")
            return False

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r进度: {percent:.1f}% ({downloaded:,}/{total_size:,} bytes)", end='', flush=True)

        print()  # 换行
        return True

    except Exception as e:
        print(f" 下载视频时出错: {e}")
        return False


def download_with_api(video_id: str, output_path: str) -> bool:
    """通过 iesdouyin 分享页无登录下载（已验证有效）"""
    iphone_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"

    print("   trying iesdouyin share page (no login)...")
    try:
        share_url = f"https://www.iesdouyin.com/share/video/{video_id}"
        response = requests.get(share_url, headers={"User-Agent": iphone_ua}, timeout=10)
        if response.status_code == 200:
            play_match = re.search(r'play_addr.*?url_list.*?\["([^"]+)"', response.text, re.DOTALL)
            if not play_match:
                play_match = re.search(r'"playAddr":\s*\["([^"]+)"', response.text)
            if play_match:
                raw = play_match.group(1)
                dl_url = raw.encode().decode("unicode_escape").replace("playwm", "play")
                resp = requests.get(dl_url, headers={"User-Agent": iphone_ua, "Referer": "https://www.douyin.com/"}, timeout=60, stream=True)
                if resp.status_code == 200:
                    with open(output_path, "wb") as f:
                        for chunk in resp.iter_content(8192):
                            f.write(chunk)
                    if os.path.getsize(output_path) > 0:
                        print("   share page download success")
                        return True
    except Exception as e:
        print(f"   share page failed: {e}")

    return False


def download_with_ytdlp(url: str, output_path: str) -> bool:
    """尝试用 yt-dlp 下载（无需登录）"""
    if not shutil.which("yt-dlp"):
        return False

    print("   trying yt-dlp (no login)...")
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "-o", output_path, url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and os.path.exists(output_path):
        print("   yt-dlp success")
        return True

    return False


def download_with_browser_cookies(url: str, output_path: str) -> bool:
    """用浏览器已有 cookies 下载（需用户已在浏览器登录抖音）"""
    if not shutil.which("yt-dlp"):
        return False

    for browser in ["chrome", "edge", "firefox"]:
        cmd = [
            "yt-dlp",
            "--cookies-from-browser", browser,
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "-o", output_path, url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and os.path.exists(output_path):
            print(f"   downloaded with {browser} cookies")
            return True

    return False



def download_douyin_video(url: str, output_path: str) -> bool:
    """
    下载抖音视频的主函数

    Args:
        url: 抖音视频链接（支持短链接和长链接）
        output_path: 输出文件路径

    Returns:
        bool: 下载是否成功
    """
    print(f" 开始下载抖音视频")
    print(f"   链接: {url}")
    print(f"   输出: {output_path}")
    print()

    # 对于 www.douyin.com/video/ 长链
    is_long_url = "www.douyin.com/video/" in url
    if is_long_url:
        print("检测到长链接，尝试无登录方案...")

        # 1. iesdouyin API（无登录）
        video_id = extract_video_id(url)
        if video_id and download_with_api(video_id, output_path):
            return True

        # 2. yt-dlp（无登录）
        if download_with_ytdlp(url, output_path):
            return True

        # 3. 尝试用浏览器已有 cookies（用户可能已登录）
        if download_with_browser_cookies(url, output_path):
            return True

        # 4. 所有方式失败，输出特定错误码让 Agent 处理
        print("NEED_LOGIN")
        sys.exit(2)  # exit code 2 = 需要登录

    # 短链：先解析重定向拿到 video_id，再走 iesdouyin 分享页
    print("短链接，解析中...")
    full_url, user_agent, html = get_redirect_url(url)
    video_id = extract_video_id(full_url or url)

    # 1. iesdouyin 分享页（无登录，优先）
    if video_id and download_with_api(video_id, output_path):
        return True

    # 2. yt-dlp（无登录）
    if download_with_ytdlp(url, output_path):
        return True

    # 3. 浏览器 cookies
    if download_with_browser_cookies(url, output_path):
        return True

    # 4. HTML 解析兜底（基本失效，保留作最后手段）
    if html:
        render_data = extract_render_data(html)
        if render_data:
            video_url = extract_video_url(render_data)
            if video_url:
                success = download_video(video_url, output_path, user_agent)
                if success:
                    file_size = os.path.getsize(output_path)
                    print(f" 下载完成: {file_size:,} bytes")
                    return True

    print("NEED_LOGIN")
    sys.exit(2)


def main():
    if len(sys.argv) < 3:
        print("用法: python download_douyin.py <抖音链接或分享文本> <输出路径>")
        print()
        print("支持格式:")
        print("  1. 纯链接:   https://v.douyin.com/xxxxx")
        print("  2. 分享文本: '3.00 12/31 复制此链接 https://v.douyin.com/xxxxx 打开抖音'")
        print()
        print("示例:")
        print("  python download_douyin.py 'https://v.douyin.com/xxxxx' ./video.mp4")
        print("  python download_douyin.py '复制链接 https://v.douyin.com/xxxxx' ./video.mp4")
        sys.exit(1)

    input_text = sys.argv[1]
    output_path = sys.argv[2]

    # 尝试从输入文本中提取抖音链接
    url = extract_douyin_url_from_text(input_text)

    # 如果提取失败，尝试将输入文本本身作为URL
    if not url:
        url = input_text

    # 检查是否为抖音链接
    if not is_douyin_url(url):
        print(f" 未找到有效的抖音链接")
        print(f"   输入: {input_text[:100]}...")
        sys.exit(1)

    success = download_douyin_video(url, output_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
