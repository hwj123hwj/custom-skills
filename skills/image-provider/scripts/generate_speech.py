#!/usr/bin/env python3
"""
Text-to-Speech using Google Gemini TTS API.

Usage:
  python generate_speech.py "Hello world" -o hello.mp3
  python generate_speech.py "你好世界" -o hello.mp3 --voice Zephyr
  python generate_speech.py "Welcome" -o welcome.mp3 --model gemini-3.1-flash-tts

Models:
  gemini-3.1-flash-tts  (default, gemini-3.1-flash-tts-preview, fast, 70+ languages)
  gemini-2.5-flash-tts  (gemini-2.5-flash-preview-tts, low latency)
  gemini-2.5-pro-tts    (gemini-2.5-pro-preview-tts, high quality)

Voices (30 prebuilt):
  Zephyr, Puck, Charon, Kore, Fenrir, Leda, Orus, Aoede, Callirrhoe, Autonoe,
  Enceladus, Iapetus, Umbriel, Algieba, Despina, Erinome, Algenib, Rasalgethi,
  Laomedeia, Achernar, Alnilam, Schedar, Gacrux, Pulcherrima, Achird,
  Zubenelgenubi, Vindemiatrix, Sadachbia, Sadaltager, Sulafat
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
from urllib.request import Request, ProxyHandler, build_opener
from urllib.error import HTTPError

API_MODELS = {
    "gemini-3.1-flash-tts": "gemini-3.1-flash-tts-preview",
    "gemini-2.5-flash-tts": "gemini-2.5-flash-preview-tts",
    "gemini-2.5-pro-tts": "gemini-2.5-pro-preview-tts",
}

DEFAULT_MODEL = "gemini-3.1-flash-tts"
DEFAULT_VOICE = "Zephyr"

VOICES = {
    "Zephyr", "Puck", "Charon", "Kore", "Fenrir", "Leda", "Orus", "Aoede",
    "Callirrhoe", "Autonoe", "Enceladus", "Iapetus", "Umbriel", "Algieba",
    "Despina", "Erinome", "Algenib", "Rasalgethi", "Laomedeia", "Achernar",
    "Alnilam", "Schedar", "Gacrux", "Pulcherrima", "Achird", "Zubenelgenubi",
    "Vindemiatrix", "Sadachbia", "Sadaltager", "Sulafat",
}


def load_api_key() -> str:
    key = os.environ.get("VERTEX_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if key:
        return key

    # 向上寻找 .env 文件
    d = os.getcwd()
    env_paths = [
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
    ]
    for _ in range(6):
        env_paths.append(os.path.join(d, ".env"))
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent

    for path in env_paths + [os.path.expanduser("~/.config/image-provider/config.json")]:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    if "VERTEX_API_KEY" in line or "GEMINI_API_KEY" in line:
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


def pcm_to_mp3(pcm_path: str, mp3_path: str) -> bool:
    cmd = [
        "ffmpeg", "-y",
        "-f", "s16le",
        "-ar", "24000",
        "-ac", "1",
        "-i", pcm_path,
        "-b:a", "128k",
        mp3_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"   ffmpeg error: {result.stderr[:200]}")
            return False
        return True
    except Exception as e:
        print(f"   ffmpeg exception: {e}")
        return False


def generate_speech(
    text: str,
    output_path: str,
    model: str = DEFAULT_MODEL,
    voice: str = DEFAULT_VOICE,
) -> bool:
    api_key = load_api_key()
    if not api_key:
        print("❌ VERTEX_API_KEY or GEMINI_API_KEY not found")
        return False

    model_id = API_MODELS.get(model, model)
    endpoint = f"https://aiplatform.googleapis.com/v1/publishers/google/models/{model_id}:generateContent"

    payload = {
        "contents": [{"role": "user", "parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {"voiceName": voice}
                }
            }
        }
    }

    url = f"{endpoint}?key={api_key}"
    headers = {"Content-Type": "application/json"}

    proxy_handler = get_proxy_handler()
    opener = build_opener(proxy_handler)

    print(f"Model: {model_id}")
    print(f"Voice: {voice}")
    print(f"Text: {text[:60]}{'...' if len(text) > 60 else ''}")

    try:
        req = Request(url, data=json.dumps(payload).encode(), headers=headers, method="POST")
        with opener.open(req, timeout=120) as resp:
            result = json.load(resp)
    except HTTPError as e:
        print(f"❌ HTTP Error: {e.code} {e.reason}")
        try:
            error_body = json.load(e)
            print(f"   {error_body}")
        except:
            print(f"   {e.read().decode()[:200]}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    try:
        candidates = result.get("candidates", [])
        if not candidates:
            print(f"❌ No candidates in response: {result}")
            return False

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            print(f"❌ No parts in content: {candidates[0]}")
            return False

        # Vertex AI uses inlineData, AI Studio uses binary
        audio_data_b64 = (
            parts[0].get("inlineData", {}).get("data") or
            parts[0].get("binary", {}).get("data")
        )
        if not audio_data_b64:
            print(f"❌ No audio binary data in response")
            print(f"   Parts: {parts}")
            return False

        audio_data = base64.b64decode(audio_data_b64)

        with tempfile.NamedTemporaryFile(suffix=".pcm", delete=False) as tmp_pcm:
            tmp_pcm.write(audio_data)
            tmp_pcm_path = tmp_pcm.name

        try:
            if not pcm_to_mp3(tmp_pcm_path, output_path):
                os.remove(tmp_pcm_path)
                return False

            size_kb = os.path.getsize(output_path) / 1024
            print(f"✅ Saved: {output_path} ({size_kb:.1f} KB)")
            return True
        finally:
            if os.path.exists(tmp_pcm_path):
                os.remove(tmp_pcm_path)

    except Exception as e:
        print(f"❌ Parse error: {e}")
        print(f"   Response: {json.dumps(result, indent=2)[:500]}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Text-to-Speech using Gemini TTS")
    parser.add_argument("text", help="Text to convert to speech")
    parser.add_argument("--output", "-o", default="output.mp3", help="Output audio file")
    parser.add_argument(
        "--model", "-m",
        default="gemini-3.1-flash-tts",
        choices=list(API_MODELS.keys()),
        help="TTS model (default: gemini-3.1-flash-tts)",
    )
    parser.add_argument(
        "--voice", "-v",
        default=DEFAULT_VOICE,
        help=f"Voice name (default: {DEFAULT_VOICE})",
    )

    args = parser.parse_args()

    if args.voice not in VOICES:
        print(f"⚠️  Unknown voice '{args.voice}', using {DEFAULT_VOICE}")
        args.voice = DEFAULT_VOICE

    success = generate_speech(
        text=args.text,
        output_path=args.output,
        model=args.model,
        voice=args.voice,
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
