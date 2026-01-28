import os
import psycopg2
from dotenv import load_dotenv
import httpx
from typing import List
import sys
import io

# 强制 UTF-8 输出
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

# ================= 配置区 =================
DB_CONFIG = {
    "dbname": "media_knowledge_base",
    "user": "root",
    "password": "15671040800q",
    "host": "127.0.0.1",
    "port": "5433"
}

LONGMAO_API_KEY = os.getenv("LONGMAO_API_KEY")
LONGMAO_BASE_URL = os.getenv("LONGMAO_BASE_URL")
LLM_MODEL_NAME = os.getenv("LONGMAO_MODEL") or "LongCat-Flash-Chat"

def get_up_hot_content(up_mid: int, top_n: int = 5):
    """
    从数据库中筛选指定 UP 主权值最高的 N 个视频文稿
    权值公式: 点赞*5 + 投币*10 + 播放量
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    query = """
    SELECT bvid, title, content_text, view_count, like_count, coin_count
    FROM bili_video_contents
    WHERE up_mid = %s AND content_text IS NOT NULL
    ORDER BY (like_count * 5 + coin_count * 10 + view_count) DESC
    LIMIT %s;
    """
    
    cur.execute(query, (up_mid, top_n))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

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
        "model": LLM_MODEL_NAME,
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
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT up_name FROM bili_video_contents WHERE up_mid = %s LIMIT 1", (up_mid,))
                res = cur.fetchone()
                if res: up_name = res[0]
    except Exception:
        pass

    # 重新组织数据
    formatted_videos = [
        {"bvid": r[0], "title": r[1], "content": r[2]} for r in hot_videos
    ]
    
    print(f"✅ 找到 {len(formatted_videos)} 个热门视频，正在进行深度总结...")
    
    # 2. 调用总结
    summary = summarize_views(up_name, formatted_videos)
    
    print("\n" + "="*50)
    print(f"✨ UP主核心观点深度总结 ✨")
    print("="*50 + "\n")
    print(summary)
    print("\n" + "="*50)

    # 3. 写入固定临时文件，供 AI 稳定读取
    try:
        with open("up_analysis_report.tmp", "w", encoding="utf-8") as f:
            f.write(f"UP_NAME: {up_name}\n")
            f.write(f"UP_MID: {up_mid}\n")
            f.write("="*50 + "\n")
            f.write(summary)
            f.write("\n" + "="*50 + "\n")
    except Exception as e:
        print(f"写入报告文件失败: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: uv run python bili_up_summarizer.py <UP_UID>")
    else:
        main(sys.argv[1])
