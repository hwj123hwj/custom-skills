# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "httpx",
#     "python-dotenv",
# ]
# ///

import os
import json
import wave
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

# ================= 配置加载通用逻辑 =================
def load_secrets():
    """递归向上查找 secrets.json"""
    import json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while True:
        secrets_path = os.path.join(current_dir, "secrets.json")
        if os.path.exists(secrets_path):
            try:
                with open(secrets_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # 到达根目录
            return {}
        current_dir = parent_dir

SECRETS = load_secrets()
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY") or SECRETS.get("SILICONFLOW_API_KEY")

# 兜底：尝试从 Windows 注册表读取用户环境变量（解决 VS Code 终端不刷新的问题）
if not SILICONFLOW_API_KEY:
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment")
        SILICONFLOW_API_KEY, _ = winreg.QueryValueEx(key, "SILICONFLOW_API_KEY")
        print(f"ℹ️ 从注册表读取到 API Key: {SILICONFLOW_API_KEY[:4]}***")
    except Exception:
        pass

if not SILICONFLOW_API_KEY:
    print("❌ 未找到 SILICONFLOW_API_KEY，无法测试。")
    exit(1)

def create_dummy_wav(filename="test.wav"):
    """创建一个 1 秒的静音 WAV 文件"""
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)      # 单声道
        wf.setsampwidth(2)      # 2 bytes (16 bit)
        wf.setframerate(16000)  # 16kHz
        wf.writeframes(b'\x00' * 16000 * 2) # 1秒静音
    return filename

async def test_model(model_name):
    filename = "test.wav"
    if not os.path.exists(filename):
        create_dummy_wav(filename)
    
    url = "https://api.siliconflow.cn/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {SILICONFLOW_API_KEY}"}
    
    # 读取文件
    with open(filename, "rb") as f:
        file_content = f.read()

    files = {"file": (filename, file_content, "audio/wav")}
    data = {"model": model_name}

    print(f"🔄 正在测试模型: {model_name} ...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, data=data, files=files, timeout=30)
            if response.status_code == 200:
                print(f"✅ 测试成功! 模型 {model_name} 可用。")
                print(f"   返回结果: {response.json()}")
                return True
            else:
                print(f"❌ 测试失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False

async def main():
    # 用户明确指定的模型 ID
    target_model = "TeleAI/TeleSpeechASR" 
    
    await test_model(target_model)
    
    # 清理临时文件
    if os.path.exists("test.wav"):
        os.remove("test.wav")

if __name__ == "__main__":
    asyncio.run(main())
