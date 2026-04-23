#!/usr/bin/env python3
"""
通用视频链接提取工具
支持从分享文本中提取多个平台的视频链接

支持平台:
- 抖音 (Douyin)
- B站 (Bilibili)
- YouTube
- 小红书 (XHS)
- 快手 (Kuaishou)
"""

import re
from typing import Optional, Tuple


# Windows CMD 编码修复
import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def extract_douyin_url(text: str) -> Optional[str]:
    """提取抖音链接"""
    patterns = [
        r'https?://v\.douyin\.com/[A-Za-z0-9]+/?',
        r'https?://www\.douyin\.com/video/\d+',
        r'https?://m\.douyin\.com/\S+',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def extract_bilibili_url(text: str) -> Optional[str]:
    """提取B站链接"""
    patterns = [
        r'https?://www\.bilibili\.com/video/(BV[A-Za-z0-9]{10}|av\d+)',
        r'https?://b23\.tv/[A-Za-z0-9]+',
        r'https?://m\.bilibili\.com/video/(BV[A-Za-z0-9]{10}|av\d+)',
        r'(BV[A-Za-z0-9]{10})',  # 纯BV号
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            url = match.group(0)
            # 如果只是BV号，补全URL
            if url.startswith('BV'):
                return f'https://www.bilibili.com/video/{url}'
            return url
    return None


def extract_youtube_url(text: str) -> Optional[str]:
    """提取YouTube链接"""
    patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=[A-Za-z0-9_-]{11}',
        r'https?://youtu\.be/[A-Za-z0-9_-]{11}',
        r'https?://(?:www\.)?youtube\.com/shorts/[A-Za-z0-9_-]{11}',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def extract_xiaohongshu_url(text: str) -> Optional[str]:
    """提取小红书链接"""
    patterns = [
        r'https?://www\.xiaohongshu\.com/(?:discovery/item|explore)/[a-f0-9]+',
        r'https?://xhslink\.com/[A-Za-z0-9]+',
        r'http://xhslink\.com/[A-Za-z0-9]+',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def extract_kuaishou_url(text: str) -> Optional[str]:
    """提取快手链接"""
    patterns = [
        r'https?://www\.kuaishou\.com/\S+',
        r'https?://v\.kuaishou\.com/[A-Za-z0-9]+',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def detect_platform(url: str) -> str:
    """检测视频平台"""
    if 'douyin.com' in url:
        return 'douyin'
    elif 'bilibili.com' in url or 'b23.tv' in url or url.startswith('BV'):
        return 'bilibili'
    elif 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    elif 'xiaohongshu.com' in url or 'xhslink.com' in url:
        return 'xiaohongshu'
    elif 'kuaishou.com' in url:
        return 'kuaishou'
    else:
        return 'unknown'


def extract_video_url_from_text(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    从分享文本中提取视频链接

    返回: (URL, 平台名称)
    """
    # 尝试各个平台的提取器
    extractors = [
        (extract_douyin_url, 'douyin'),
        (extract_bilibili_url, 'bilibili'),
        (extract_youtube_url, 'youtube'),
        (extract_xiaohongshu_url, 'xiaohongshu'),
        (extract_kuaishou_url, 'kuaishou'),
    ]

    for extractor, platform in extractors:
        url = extractor(text)
        if url:
            return url, platform

    return None, None


def main():
    """测试入口"""
    if len(sys.argv) < 2:
        print("用法: python extract_video_url.py <分享文本>")
        print()
        print("示例:")
        print("  python extract_video_url.py '3.00 https://v.douyin.com/xxxxx 复制链接'")
        print("  python extract_video_url.py '【标题】BV1234567890 来自B站'")
        print("  python extract_video_url.py 'https://www.youtube.com/watch?v=xxxxx'")
        sys.exit(1)

    text = ' '.join(sys.argv[1:])
    url, platform = extract_video_url_from_text(text)

    if url:
        print(f" 提取成功")
        print(f"  平台: {platform}")
        print(f"  链接: {url}")
        sys.exit(0)
    else:
        print(" 未找到有效的视频链接")
        print(f"  输入: {text[:100]}...")
        sys.exit(1)


if __name__ == "__main__":
    main()
