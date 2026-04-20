#!/usr/bin/env python3
"""
Wiki 编译脚本 (Karpathy LLM-Wiki 模式)
从知识库提取条目，利用 LLM 提取概念与实体，编译成带双向链接的结构化 wiki 页面。

用法: python skills/knowledge-skill/scripts/wiki_compile.py [--limit 10] [--dry-run]
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

import psycopg2
import psycopg2.extras
import requests

sys.stdout.reconfigure(line_buffering=True)

# 加载环境变量
load_dotenv(Path(__file__).parent.parent / ".env")
load_dotenv(Path.home() / ".openclaw" / "secrets.env")

# 配置
DB_CONFIG = {
    "host": os.getenv("DB_HOST", ""),
    "port": int(os.getenv("DB_PORT", 5433)),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "dbname": os.getenv("DB_NAME", ""),
}

LONGCAT_API_KEY = os.getenv("LONGCAT_API_KEY")
LONGCAT_BASE_URL = "https://api.longcat.chat/openai"

# 切换到 LLM-Wiki 规范的目录结构
WIKI_DIR = Path.home() / ".openclaw" / "workspace" / "llm-wiki"
STATE_FILE = WIKI_DIR / ".compile-state.json"
INDEX_FILE = WIKI_DIR / "index.md"
WIKI_PAGES_DIR = WIKI_DIR / "wiki"

# 用户画像关键词（用于筛选高价值内容进入 Wiki）
USER_PROFILE_KEYWORDS = [
    "agent", "linux", "security", "open source", "openclaw",
    "claude", "gpt", "llm", "ai", "自动化", "运维",
    "devops", "docker", "kubernetes", "后端", "go",
    "python", "工程", "框架", "开源", "rag", "karpathy"
]

def get_uncompiled_entries(limit=20):
    """查询未编译的条目"""
    state = load_state()
    compiled_ids = set(state.get("compiled_ids", []))

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cur.execute("""
            SELECT id, source_type, source_id, source_url, title, content, summary,
                   ai_summary, created_at, metadata
            FROM knowledge_items
            ORDER BY created_at DESC
            LIMIT %s
        """, [limit * 5])

        entries = cur.fetchall()
        # 过滤已编译的 (使用 id 和 source_id 双重判断防止重复)
        uncompiled = [e for e in entries if str(e["id"]) not in compiled_ids and str(e["source_id"]) not in compiled_ids]

        return [dict(e) for e in uncompiled]
    finally:
        cur.close()
        conn.close()

def filter_by_profile(entries):
    """根据用户画像筛选高价值条目"""
    scored = []
    for entry in entries:
        title = entry.get("title", "")
        content = entry.get("content", "") or entry.get("summary", "")
        score = sum(1 for kw in USER_PROFILE_KEYWORDS if kw.lower() in title.lower() or kw.lower() in content.lower())
        if score > 0:
            entry["profile_score"] = score
            entry["matched_keywords"] = [kw for kw in USER_PROFILE_KEYWORDS if kw.lower() in title.lower() or kw.lower() in content.lower()]
            scored.append(entry)
    scored.sort(key=lambda x: x["profile_score"], reverse=True)
    return scored

def analyze_article_with_llm(title, content):
    """用 LLM 提取摘要、概念和实体 (Karpathy 降维法)"""
    if not LONGCAT_API_KEY:
        return {"summary": "API 未配置", "concepts": [], "entities": []}

    text = re.sub(r'<[^>]+>', ' ', content)
    text = re.sub(r'\s+', ' ', text).strip()[:3000]

    prompt = f"""请分析以下文章，并提取核心信息。
标题：{title}
内容片段：{text}

请严格按以下 JSON 格式输出（不要输出代码块标记如 ```json，直接输出合法的 JSON 字符串）：
{{
  "summary": "一句话总结核心内容",
  "concepts": ["概念1", "概念2"],
  "entities": ["实体1", "实体2"]
}}
注意：
1. concepts 指技术、理论、方法论等（如 RAG, Agent, 混合检索），最多3个。
2. entities 指具体的人、公司、产品、开源库等（如 OpenAI, Postgres, Karpathy），最多3个。
"""
    try:
        resp = requests.post(
            f"{LONGCAT_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {LONGCAT_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "LongCat-Flash-Lite",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
                "temperature": 0.1,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            result_text = resp.json()["choices"][0]["message"]["content"].strip()
            result_text = re.sub(r'^```json\s*', '', result_text)
            result_text = re.sub(r'\s*```$', '', result_text)
            return json.loads(result_text)
        else:
            print(f"      LongCat API 失败: {resp.status_code}")
    except Exception as e:
        print(f"      解析异常: {e}")

    return {"summary": "解析失败", "concepts": [], "entities": []}

def make_slug(text):
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', slug).strip('-')[:50]

def update_or_create_node_page(node_type, name, source_title, source_filename):
    """创建或更新实体/概念页面，并添加反向链接 (Backlinks)"""
    slug = make_slug(name)
    if not slug:
        return None

    filename = f"{node_type}-{slug}.md"
    filepath = WIKI_PAGES_DIR / filename

    link_line = f"- [[{source_filename.replace('.md', '')}]] ({source_title})"

    if filepath.exists():
        content = filepath.read_text()
        if link_line not in content:
            # 追加到 Mentioned In 列表
            if "## 关联来源 (Mentions)" in content:
                content += f"\n{link_line}"
            else:
                content += f"\n\n## 关联来源 (Mentions)\n{link_line}"
            filepath.write_text(content)
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
        md = f"""---
type: {node_type}
title: {name}
date: {date_str}
---

# {name}

## 关联来源 (Mentions)
{link_line}
"""
        filepath.write_text(md)

    return filename

def compile_wiki_article(entry):
    """将知识条目编译成 source wiki 页面"""
    title = entry["title"]
    content = entry.get("content", "") or entry.get("summary", "")
    source_url = entry.get("source_url", "")
    created_at = entry.get("created_at", datetime.now())

    print(f"    [LLM] 正在深度分析并提取知识图谱...")
    analysis = analyze_article_with_llm(title, content)

    slug = make_slug(title)
    filename = f"source-{slug}.md"

    tags = entry.get("matched_keywords", [])[:3]
    date_str = created_at.strftime("%Y-%m-%d") if hasattr(created_at, 'strftime') else str(created_at)[:10]

    # 建立图谱链接并生成/更新实体概念文件
    concept_links = []
    for c in analysis.get("concepts", []):
        c_file = update_or_create_node_page("concept", c, title, filename)
        if c_file:
            concept_links.append(f"[[{c_file.replace('.md', '')}]]")

    entity_links = []
    for e in analysis.get("entities", []):
        e_file = update_or_create_node_page("entity", e, title, filename)
        if e_file:
            entity_links.append(f"[[{e_file.replace('.md', '')}]]")

    # 如果本身有ai_summary就用，否则用提取的
    final_summary = entry.get("ai_summary") or analysis.get("summary", "无摘要")

    article_md = f"""---
type: source
title: {title}
date: {date_str}
tags: [{', '.join(tags)}]
---

# {title}

> 🔗 [原文链接]({source_url}) | 来源类型：{entry.get('source_type', 'unknown')}

## 核心摘要
{final_summary}

## 知识图谱 (Knowledge Graph)
- **相关概念 (Concepts)**: {', '.join(concept_links) if concept_links else '无'}
- **相关实体 (Entities)**: {', '.join(entity_links) if entity_links else '无'}

## 内容片段
{content[:800]}...
"""
    return filename, article_md, analysis

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_compile": None, "compiled_ids": []}

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))

def update_index():
    """扫描 wiki 目录，动态生成总索引"""
    sources, concepts, entities = [], [], []

    for f in WIKI_PAGES_DIR.glob("*.md"):
        if f.name.startswith("source-"): sources.append(f.name)
        elif f.name.startswith("concept-"): concepts.append(f.name)
        elif f.name.startswith("entity-"): entities.append(f.name)

    index_md = f"""# LLM Wiki 知识总线

> 基于大模型自动编译的个人结构化知识图谱
> 更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

## 📚 知识图谱统计
- **信息源 (Sources)**: {len(sources)} 篇
- **核心概念 (Concepts)**: {len(concepts)} 个
- **关键实体 (Entities)**: {len(entities)} 个

## 🧠 概念网络 (Concepts)
"""
    for c in sorted(concepts):
        index_md += f"- [[{c.replace('.md', '')}]]\n"

    index_md += "\n## 🏢 实体网络 (Entities)\n"
    for e in sorted(entities):
        index_md += f"- [[{e.replace('.md', '')}]]\n"

    index_md += "\n## 📄 信息源 (Sources)\n"
    for s in sorted(sources, reverse=True)[:50]: # 只列出最新的50个
        index_md += f"- [[{s.replace('.md', '')}]]\n"

    INDEX_FILE.write_text(index_md)

def main():
    parser = argparse.ArgumentParser(description="Karpathy LLM-Wiki 编译器")
    parser.add_argument("--limit", type=int, default=5, help="编译数量上限")
    parser.add_argument("--dry-run", action="store_true", help="只打印不写入")
    args = parser.parse_args()

    print("="*50)
    print(f"🕸️ LLM Wiki 图谱编译 — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*50)

    WIKI_PAGES_DIR.mkdir(parents=True, exist_ok=True)

    uncompiled = get_uncompiled_entries(args.limit * 2)
    filtered = filter_by_profile(uncompiled)[:args.limit]

    if not filtered:
        print("✅ 当前没有需要编译的新知识条目。")
        return

    if args.dry_run:
        print(f"🔍 待编译条目 (dry-run): {len(filtered)} 条")
        return

    state = load_state()

    for entry in filtered:
        print(f"\n➡️ 处理: {entry['title'][:40]}...")
        filename, article_md, analysis = compile_wiki_article(entry)

        article_file = WIKI_PAGES_DIR / filename
        article_file.write_text(article_md)

        # 记录已编译
        state["compiled_ids"].append(str(entry.get("source_id", entry["id"])))
        state["compiled_ids"].append(str(entry["id"]))
        print(f"  ✅ 页面已生成: {filename}")
        print(f"  🧠 提取概念: {', '.join(analysis.get('concepts', []))}")
        print(f"  🏢 提取实体: {', '.join(analysis.get('entities', []))}")

    save_state(state)
    update_index()
    print("\n✅ 知识图谱索引 index.md 已更新。编译完成！")

if __name__ == "__main__":
    main()