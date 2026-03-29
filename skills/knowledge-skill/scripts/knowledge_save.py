#!/usr/bin/env python3
"""
知识入库脚本
将内容保存到知识库，自动生成 embedding 和摘要
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import psycopg2
import psycopg2.extras
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(Path(__file__).parent.parent / ".env")

# 配置
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", 5433)),
    "user": os.getenv("DB_USER", "bili"),
    "password": os.getenv("DB_PASSWORD", "bili123456"),
    "dbname": os.getenv("DB_NAME", "bilibili"),
}

SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
# AI 摘要模型（使用免费的 Qwen 模型）
AI_SUMMARY_MODEL = os.getenv("AI_SUMMARY_MODEL", "Qwen/Qwen2.5-7B-Instruct")


def get_embedding(text: str) -> list[float]:
    """调用 SiliconFlow API 生成 embedding"""
    if not SILICONFLOW_API_KEY:
        print("Warning: SILICONFLOW_API_KEY not set, skipping embedding", file=sys.stderr)
        return None

    # 截断超长文本（SiliconFlow 限制约 8000 tokens）
    max_chars = 8000
    text = text[:max_chars]

    try:
        response = requests.post(
            "https://api.siliconflow.cn/v1/embeddings",
            headers={
                "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": EMBEDDING_MODEL,
                "input": text,
                "encoding_format": "float",
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]
    except Exception as e:
        print(f"Error generating embedding: {e}", file=sys.stderr)
        return None


def generate_summary(title: str, content: str) -> str:
    """生成摘要（内容过长时截断）"""
    if len(content) <= 500:
        return content
    
    return content[:500] + "..."


def generate_ai_summary(title: str, content: str) -> str:
    """使用 AI 生成一句话摘要"""
    if not SILICONFLOW_API_KEY:
        return None
    
    # 截取内容（最多 2000 字符）
    text = content[:2000] if len(content) > 2000 else content
    
    prompt = f"""请用一句话（不超过50字）总结以下内容的要点：

标题：{title}

内容：
{text}

一句话总结："""

    try:
        response = requests.post(
            "https://api.siliconflow.cn/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": AI_SUMMARY_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100,
                "temperature": 0.3,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error generating AI summary: {e}", file=sys.stderr)
        return None


def save_knowledge(
    source_type: str,
    source_id: str,
    title: str,
    content: str,
    source_url: str = None,
    metadata: dict = None,
    ai_summary: str = None,  # 可选，手动传入 AI 摘要
) -> dict:
    """保存知识到数据库"""
    
    # 生成摘要
    summary = generate_summary(title, content)
    
    # 生成 AI 摘要（如果没有手动传入）
    if ai_summary is None:
        print("正在生成 AI 摘要...", file=sys.stderr)
        ai_summary = generate_ai_summary(title, content)
    
    # 生成 embedding（使用 title + ai_summary，语义更精准）
    embedding_text = f"{title}\n{ai_summary}" if ai_summary else f"{title}\n{summary}"
    embedding = get_embedding(embedding_text)
    
    # 连接数据库
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # 构建 SQL（包含 ai_summary）
        sql = """
            INSERT INTO knowledge_items 
            (source_type, source_id, source_url, title, content, summary, ai_summary, embedding, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (source_type, source_id) DO UPDATE
            SET title = EXCLUDED.title,
                content = EXCLUDED.content,
                summary = EXCLUDED.summary,
                ai_summary = EXCLUDED.ai_summary,
                embedding = EXCLUDED.embedding,
                metadata = EXCLUDED.metadata,
                updated_at = NOW()
            RETURNING id, created_at
        """
        cur.execute(sql, (
            source_type,
            source_id,
            source_url,
            title,
            content,
            summary,
            ai_summary,
            str(embedding) if embedding else None,
            psycopg2.extras.Json(metadata or {}),
        ))
        
        result = cur.fetchone()
        conn.commit()
        
        return {
            "success": True,
            "id": str(result[0]),
            "created_at": result[1].isoformat(),
            "summary": summary,
            "ai_summary": ai_summary,
            "has_embedding": embedding is not None,
        }
    except Exception as e:
        conn.rollback()
        return {
            "success": False,
            "error": str(e),
        }
    finally:
        cur.close()
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="保存知识到知识库")
    parser.add_argument("--source-type", required=True, help="来源类型")
    parser.add_argument("--source-id", required=True, help="来源ID")
    parser.add_argument("--title", required=True, help="标题")
    parser.add_argument("--content", required=True, help="内容")
    parser.add_argument("--source-url", help="原始链接")
    parser.add_argument("--metadata", help="元数据 (JSON)")
    parser.add_argument("--ai-summary", help="AI 摘要（可选，不传则自动生成）")
    
    args = parser.parse_args()
    
    # 解析 metadata
    metadata = None
    if args.metadata:
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in metadata", file=sys.stderr)
            sys.exit(1)
    
    # 保存
    result = save_knowledge(
        source_type=args.source_type,
        source_id=args.source_id,
        title=args.title,
        content=args.content,
        source_url=args.source_url,
        metadata=metadata,
        ai_summary=args.ai_summary,
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()