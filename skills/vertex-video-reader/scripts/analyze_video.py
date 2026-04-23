#!/usr/bin/env python3
"""
Video Analysis using Google Gemini Models via Vertex AI API.

Usage:
  python analyze_video.py path/to/video.mp4
  python analyze_video.py path/to/video.mp4 -p "提炼出视频中出现的文字"
  python analyze_video.py path/to/video.mp4 -m gemini-3.1-flash

Models:
  gemini-3.1-flash-lite-preview (Default, fast & cheap video understanding)
  gemini-3.1-flash              (Higher intelligence, better for complex reasoning)
"""

import argparse
import base64
import json
import os
import sys
from urllib.request import Request, ProxyHandler, build_opener
from urllib.error import HTTPError

DEFAULT_MODEL = "gemini-3.1-flash-lite-preview"
DEFAULT_PROMPT = "请详细描述一下这个视频的内容。"

def load_api_key() -> str:
    key = os.environ.get("VERTEX_API_KEY")
    if key:
        return key

    # 只优先读取自身技能目录的 .env 以及项目根目录的 .env
    skill_dir = os.path.dirname(os.path.dirname(__file__))
    project_root = os.getcwd()

    env_paths = [
        os.path.join(skill_dir, ".env"),
        os.path.join(project_root, ".env")
    ]

    for path in env_paths:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    if "VERTEX_API_KEY" in line:
                        parts = line.strip().split("=", 1)
                        if len(parts) == 2:
                            return parts[1].strip()

    return ""

def get_proxy_handler():
    # 1. Check environment variables
    for env_var in ["https_proxy", "HTTPS_PROXY", "http_proxy", "HTTP_PROXY", "all_proxy", "ALL_PROXY"]:
        proxy = os.environ.get(env_var)
        if proxy:
            return ProxyHandler({"http": proxy, "https": proxy})

    # 2. Auto-detect common local proxy ports
    import socket
    for port in (7890, 7897, 1087):
        try:
            s = socket.create_connection(("127.0.0.1", port), timeout=1)
            s.close()
            proxy = f"http://127.0.0.1:{port}"
            print(f"   [proxy] Auto-detected proxy at {proxy}")
            return ProxyHandler({"http": proxy, "https": proxy})
        except OSError:
            continue

    return ProxyHandler()

def get_mime_type(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.mp4': return 'video/mp4'
    if ext in ['.mov', '.qt']: return 'video/quicktime'
    if ext == '.webm': return 'video/webm'
    if ext == '.mkv': return 'video/webm'
    return 'video/mp4'  # fallback

def analyze_video(video_path: str, prompt: str, model_id: str) -> bool:
    api_key = load_api_key()
    if not api_key:
        print("❌ VERTEX_API_KEY not found in environment or .env file")
        return False

    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False

    file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    if file_size_mb > 20:
        print(f"⚠️ Warning: Video file is {file_size_mb:.1f}MB. Inline API calls typically limit payloads to ~20MB. This may fail.")
        print(f"   If it fails, consider using Google Cloud Storage (gcs_uri) instead of inlineData.")

    print(f"Loading video: {video_path} ({file_size_mb:.1f} MB)")
    try:
        with open(video_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"❌ Error reading video file: {e}")
        return False

    mime_type = get_mime_type(video_path)

    url = f"https://aiplatform.googleapis.com/v1/publishers/google/models/{model_id}:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "role": "user",
            "parts": [
                {"text": prompt},
                {"inlineData": {"mimeType": mime_type, "data": b64_data}}
            ]
        }]
    }

    req = Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    opener = build_opener(get_proxy_handler())

    print(f"Analyzing with model {model_id} (Prompt: '{prompt}')...")
    try:
        with opener.open(req, timeout=120) as resp:
            data = json.loads(resp.read())

        candidates = data.get("candidates", [])
        if not candidates:
            print("❌ No valid response generated.")
            return False

        result_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")

        print("\n✅ Analysis Result:\n" + "-"*40)
        print(result_text.strip())
        print("-" * 40)
        return True

    except HTTPError as e:
        print(f"❌ HTTP Error: {e.code} {e.reason}")
        try:
            print(e.read().decode())
        except:
            pass
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Analyze video using Gemini Flash Lite via Vertex AI")
    parser.add_argument("video_path", help="Path to the video file (.mp4, .mov, etc.)")
    parser.add_argument(
        "-p", "--prompt",
        default=DEFAULT_PROMPT,
        help=f"Prompt to instruct the model (default: '{DEFAULT_PROMPT}')"
    )
    parser.add_argument(
        "-m", "--model",
        default=DEFAULT_MODEL,
        help=f"Model ID to use (default: {DEFAULT_MODEL})"
    )

    args = parser.parse_args()
    success = analyze_video(args.video_path, args.prompt, args.model)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()