#!/usr/bin/env python3
"""
URL 一键入库脚本
从 URL 自动获取内容并保存到知识库
支持：B站、微信公众号、小红书、通用网页
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(Path(__file__).parent.parent / ".env")

# 导入 knowledge_save
sys.path.insert(0, str(Path(__file__).parent))
from knowledge_save import save_knowledge

# 配置
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
ASR_MODEL = os.getenv("ASR_MODEL", "TeleAI/TeleSpeechASR")


def transcribe_audio(audio_path: str) -> str:
    """使用 SiliconFlow ASR 转录音频"""
    with open(audio_path, "rb") as f:
        response = requests.post(
            "https://api.siliconflow.cn/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {SILICONFLOW_API_KEY}"},
            files={"file": f},
            data={"model": ASR_MODEL},
            timeout=300,
        )
    
    result = response.json()
    if "text" in result:
        return result["text"]
    else:
        raise ValueError(f"ASR 转录失败: {result}")


def video_to_wav(video_path: str, wav_path: str) -> None:
    """将视频转换为 WAV 音频"""
    result = subprocess.run(
        [
            "ffmpeg", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            wav_path, "-y"
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise ValueError(f"ffmpeg 转换失败: {result.stderr}")


def get_xiaohongshu_content(url: str) -> dict:
    """获取小红书笔记内容（支持视频转录）"""
    # 提取笔记 ID
    match = re.search(r"item/([a-f0-9]+)", url)
    if not match:
        match = re.search(r"discovery/item/([a-f0-9]+)", url)
    if not match:
        match = re.search(r"xhslink\.com/([a-zA-Z0-9]+)", url)
    
    if not match:
        raise ValueError("无法从 URL 中提取笔记 ID")
    
    note_id = match.group(1) if "xhslink" not in url else None
    
    # 如果是短链接，先解析
    if "xhslink.com" in url:
        response = requests.head(url, allow_redirects=True, timeout=10)
        final_url = response.url
        match = re.search(r"item/([a-f0-9]+)", final_url)
        if match:
            note_id = match.group(1)
    
    # 使用 xiaohongshu-skills 获取笔记详情
    xhs_cli = Path.home() / ".agents/skills/xiaohongshu-skills/scripts/cli.py"
    
    if xhs_cli.exists():
        # 尝试获取笔记详情
        result = subprocess.run(
            ["uv", "run", str(xhs_cli), "get-feed-detail", 
             "--feed-id", note_id],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(xhs_cli.parent),
        )
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                note = data.get("note", {})
                title = note.get("title", "小红书笔记")
                desc = note.get("desc", "")
                note_type = note.get("type", "图文")
                
                content = f"标题: {title}\n\n{desc}"
                
                # 如果是视频笔记，尝试转录
                if note_type == "video":
                    print("检测到视频笔记，尝试下载并转录...")
                    try:
                        video_content = transcribe_xiaohongshu_video(note_id)
                        if video_content:
                            content = f"{content}\n\n=== 视频转录 ===\n\n{video_content}"
                    except Exception as e:
                        print(f"视频转录失败: {e}", file=sys.stderr)
                
                return {
                    "source_type": "xiaohongshu",
                    "source_id": note_id,
                    "source_url": url,
                    "title": title,
                    "content": content,
                    "metadata": {
                        "type": note_type,
                        "user": note.get("user", {}).get("nickname", ""),
                    },
                }
            except json.JSONDecodeError:
                pass
    
    # 备用方案：使用网页抓取
    raise ValueError("请先登录小红书（运行 xiaohongshu-skills 的 login 命令）")


def transcribe_xiaohongshu_video(note_id: str) -> str:
    """下载小红书视频并转录"""
    import asyncio
    from playwright.async_api import async_playwright
    
    async def get_video_url():
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else await context.new_page()
            
            video_urls = []
            
            def handle_response(response):
                url = response.url
                if '.mp4' in url and ('xhscdn' in url or 'xiaohongshu' in url):
                    video_urls.append(url)
            
            page.on('response', handle_response)
            
            await page.goto(f"https://www.xiaohongshu.com/explore/{note_id}")
            await page.wait_for_timeout(5000)
            
            try:
                await page.click('video')
                await page.wait_for_timeout(3000)
            except:
                pass
            
            return video_urls[0] if video_urls else None
    
    video_url = asyncio.run(get_video_url())
    
    if not video_url:
        return ""
    
    # 下载视频
    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = os.path.join(tmpdir, "video.mp4")
        wav_path = os.path.join(tmpdir, "audio.wav")
        
        response = requests.get(video_url, timeout=120)
        with open(video_path, "wb") as f:
            f.write(response.content)
        
        # 转换为 WAV
        video_to_wav(video_path, wav_path)
        
        # ASR 转录
        return transcribe_audio(wav_path)


def get_bilibili_content(url: str) -> dict:
    """获取 B站视频文稿"""
    # 提取 BV 号
    match = re.search(r"BV[\w]+", url)
    if not match:
        raise ValueError("无法从 URL 中提取 BV 号")
    
    bvid = match.group(0)
    
    # 使用 yt-dlp 获取视频信息
    result = subprocess.run(
        ["yt-dlp", "--dump-json", url],
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    if result.returncode != 0:
        raise ValueError(f"yt-dlp 获取失败: {result.stderr}")
    
    info = json.loads(result.stdout)
    
    title = info.get("title", "")
    content = info.get("description", "")
    
    # 尝试获取字幕
    subtitle_result = subprocess.run(
        ["yt-dlp", "--write-sub", "--write-auto-sub", 
         "--sub-lang", "zh-Hans,zh,en", 
         "--skip-download", 
         "-o", "/tmp/%(id)s", url],
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    # 读取字幕文件
    import glob
    subtitle_files = glob.glob(f"/tmp/{info.get('id', '')}*.vtt")
    if subtitle_files:
        with open(subtitle_files[0], "r") as f:
            subtitle_text = f.read()
            subtitle_text = re.sub(r"<\d+:\d+:\d+\.\d+>", "", subtitle_text)
            subtitle_text = re.sub(r"WEBVTT.*?\n", "", subtitle_text)
            content = subtitle_text.strip() or content
    
    # 字幕为空时自动 ASR 转录
    if not content or len(content.strip()) < 10:
        print("无字幕，自动下载音频进行 ASR 转录...")
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                audio_path = os.path.join(tmpdir, "audio.wav")
                # 直接下载音频
                dl_result = subprocess.run(
                    ["yt-dlp", "-f", "worstaudio", "--extract-audio",
                     "--audio-format", "wav", "-o", audio_path, url],
                    capture_output=True, text=True, timeout=120,
                )
                if dl_result.returncode == 0 and os.path.exists(audio_path):
                    asr_text = transcribe_audio(audio_path)
                    if asr_text:
                        content = asr_text
                        print(f"ASR 转录完成，长度: {len(content)}")
        except Exception as e:
            print(f"ASR 转录失败: {e}", file=sys.stderr)
    
    return {
        "source_type": "bilibili",
        "source_id": bvid,
        "source_url": url,
        "title": title,
        "content": content,
        "metadata": {
            "bvid": bvid,
            "duration": info.get("duration"),
            "uploader": info.get("uploader"),
        },
    }


def get_wechat_content(url: str) -> dict:
    """获取微信公众号文章"""
    script_path = Path.home() / ".agent-reach/tools/wechat-article-for-ai/main.py"
    
    if not script_path.exists():
        raise ValueError("wechat-article-for-ai 工具未安装")
    
    result = subprocess.run(
        ["python3", str(script_path), url],
        capture_output=True,
        text=True,
        timeout=120,
    )
    
    if result.returncode != 0:
        raise ValueError(f"获取微信文章失败: {result.stderr}")
    
    content = result.stdout
    
    match = re.search(r"s/([a-zA-Z0-9]+)", url)
    article_id = match.group(1) if match else hashlib.md5(url.encode()).hexdigest()[:12]
    
    return {
        "source_type": "wechat",
        "source_id": article_id,
        "source_url": url,
        "title": "微信公众号文章",
        "content": content,
        "metadata": {},
    }


def get_web_content(url: str) -> dict:
    """获取通用网页内容"""
    response = requests.get(
        f"https://r.jina.ai/{url}",
        timeout=30,
    )
    
    if response.status_code != 200:
        raise ValueError(f"获取网页失败: {response.status_code}")
    
    content = response.text
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    
    return {
        "source_type": "web",
        "source_id": url_hash,
        "source_url": url,
        "title": url,
        "content": content,
        "metadata": {},
    }


def save_from_url(url: str) -> dict:
    """从 URL 获取内容并保存到知识库"""
    
    # 判断 URL 类型
    if "bilibili.com" in url:
        data = get_bilibili_content(url)
    elif "mp.weixin.qq.com" in url:
        data = get_wechat_content(url)
    elif "xiaohongshu.com" in url or "xhslink.com" in url:
        data = get_xiaohongshu_content(url)
    else:
        data = get_web_content(url)
    
    # 保存到知识库
    return save_knowledge(**data)


def main():
    parser = argparse.ArgumentParser(description="从 URL 保存内容到知识库")
    parser.add_argument("--url", required=True, help="内容 URL")
    
    args = parser.parse_args()
    
    result = save_from_url(args.url)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()