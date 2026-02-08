# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "SQLAlchemy",
#     "psycopg[binary]",
#     "httpx",
#     "rich",
# ]
# ///

import os
import httpx
from typing import List
import sys
import io
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

# 强制 UTF-8 输出
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ================= 配置加载 =================
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

# ================= 数据库操作 =================
_ENGINE = None

def get_db_config():
    """从环境变量或 secrets.json 获取数据库配置"""
    return {
        "dbname": get_env_flexible("DB_NAME", "media_knowledge_base"),
        "user": get_env_flexible("DB_USER", "root"),
        "password": get_env_flexible("DB_PASSWORD", "15671040800q"),
        "host": get_env_flexible("DB_HOST", "127.0.0.1"),
        "port": get_env_flexible("DB_PORT", "5433")
    }

def get_engine():
    global _ENGINE
    if _ENGINE is not None:
        return _ENGINE

    config = get_db_config()
    port = config.get("port")
    try:
        port = int(port) if port is not None else None
    except (TypeError, ValueError):
        port = None

    dbname = config.get("dbname")

    _ENGINE = create_engine(
        URL.create(
            "postgresql+psycopg",
            username=config.get("user"),
            password=config.get("password"),
            host=config.get("host"),
            port=port,
            database=dbname,
        ),
        pool_pre_ping=True,
    )
    return _ENGINE

# ================= 环境变量增强加载 =================
def get_env_flexible(key_name, default=None):
    """优先从 os.getenv 获取，如果为空则 Windows 注册表读取，最后 secrets.json"""
    val = os.getenv(key_name)
    if val: return val
    
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                val, _ = winreg.QueryValueEx(key, key_name)
                if val: return val
        except Exception:
            pass
            
    if SECRETS and key_name in SECRETS:
        return SECRETS[key_name]
    return default

# 优先从环境变量加载，secrets.json 作为备用
LONGMAO_API_KEY = get_env_flexible("LONGMAO_API_KEY")
LONGMAO_BASE_URL = get_env_flexible("LONGMAO_BASE_URL")
LONGMAO_MODEL = get_env_flexible("LONGMAO_MODEL", "LongCat-Flash-Chat")

def get_up_hot_content(up_mid: int, top_n: int = 5):
    """
    从数据库中筛选指定 UP 主权值最高的 N 个视频文稿
    权值公式: 点赞*5 + 投币*10 + 播放量
    """
    query = text("""
    SELECT bvid, title, content_text, view_count, like_count, coin_count
    FROM bili_video_contents
    WHERE up_mid = :up_mid AND content_text IS NOT NULL
    ORDER BY (like_count * 5 + coin_count * 10 + view_count) DESC
    LIMIT :top_n;
    """)

    with get_engine().connect() as conn:
        return conn.execute(query, {"up_mid": up_mid, "top_n": top_n}).fetchall()

def summarize_views(up_name: str, video_contents: List[dict]):
    """调用 LLM 进行核心观点提炼"""
    print(f"正在分析 {up_name} 的 {len(video_contents)} 个核心热门视频...")
    
    context = ""
    for idx, item in enumerate(video_contents):
        context += f"--- 视频 {idx+1}: {item['title']} ---\n{item['content']}\n\n"
    
    prompt = f"""
你是一位深度的内容分析专家。下面是 B 站 UP 主“{up_name}”的多个热门视频转录文稿。
请基于这些文稿，深度总结并分析该 UP 主的核心观点、底层思维逻辑以及他/她反复强调的价值观。

要求：
1. 分析要深刻，不要停留在表面，要挖掘其思维的“元逻辑”。
2. 总结出该 UP 主最核心的 3-5 个观点。
3. 如果内容涉及方法论，请提炼出具体的可复用步骤。
4. 语言要精炼且富有洞察力。

资料内容如下：
{context}
"""

    headers = {"Authorization": f"Bearer {LONGMAO_API_KEY}"}
    payload = {
        "model": LONGMAO_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    with httpx.Client(timeout=120) as client:
        response = client.post(f"{LONGMAO_BASE_URL}/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

def main(up_mid_input: str):
    try:
        up_mid = int(up_mid_input)
    except ValueError:
        print("错误: 请输入有效的 UID（数字）")
        return

    # 1. 查找数据
    hot_videos = get_up_hot_content(up_mid)
    
    if not hot_videos:
        print(f"❌ 数据库中未找到 UID 为 {up_mid} 的已采集视频文稿。")
        print("请先通过 crawl-and-export 技能采集该 UP 主的视频。")
        return

    # 从第一条数据尝试获取 UP 名
    up_name = "该UP主"
    try:
        with get_engine().connect() as conn:
            res = conn.execute(
                text("SELECT up_name FROM bili_video_contents WHERE up_mid = :up_mid LIMIT 1"),
                {"up_mid": up_mid},
            ).fetchone()
            if res:
                up_name = res[0]
    except Exception:
        pass

    # 重新组织数据
    formatted_videos = [
        {"bvid": r[0], "title": r[1], "content": r[2]} for r in hot_videos
    ]
    
    print(f"✅ 找到 {len(formatted_videos)} 个热门视频，正在进行深度总结...")
    
    # 2. 调用总结
    summary = summarize_views(up_name, formatted_videos)
    
    if not summary:
        console.print("[red]❌ 未能生成总结内容。[/red]")
        return
    
    console.print(Panel(Markdown(summary), title=f"📊 UP 主 {up_mid} 内容总结", border_style="blue"))
    
    # 3. 写入固定临时文件，供 AI 稳定读取
    try:
        with open("up_analysis_report.tmp", "w", encoding="utf-8") as f:
            f.write(f"UP_NAME: {up_name}\n")
            f.write(f"UP_MID: {up_mid}\n")
            f.write("="*50 + "\n")
            f.write(summary)
            f.write("\n" + "="*50 + "\n")
    except Exception as e:
        console.print(f"[yellow]⚠️ 写入报告文件失败: {e}[/yellow]")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: uv run python bili_up_summarizer.py <UP_UID>")
    else:
        main(sys.argv[1])
