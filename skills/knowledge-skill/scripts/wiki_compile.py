#!/usr/bin/env python3
"""
Wiki 编译脚本
从知识库筛选 bestblogs 条目，编译成结构化 wiki 文章

用法: python wiki_compile.py [--limit 10] [--dry-run]
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

WIKI_DIR = Path.home() / ".openclaw" / "workspace" / "wiki"
STATE_FILE = WIKI_DIR / ".compile-state.json"
INDEX_FILE = WIKI_DIR / "index.md"
ARTICLES_DIR = WIKI_DIR / "articles"

# 用户画像关键词（用于筛选）
USER_PROFILE_KEYWORDS = [
    "agent", "linux", "security", "open source", "openclaw",
    "claude", "gpt", "llm", "ai", "自动化", "运维",
    "devops", "docker", "kubernetes", "后端", "go",
    "python", "工程", "框架", "开源"
]


def get_uncompiled_entries(limit=20):
    """查询未编译的 bestblogs 条目"""
    state = load_state()
    compiled_ids = set(state.get("compiled_ids", []))
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cur.execute("""
            SELECT id, source_id, source_url, title, content, summary,
                   ai_summary, created_at, metadata
            FROM knowledge_items
            WHERE source_type = 'bestblogs'
            AND status = 'active'
            ORDER BY created_at DESC
            LIMIT %s
        """, [limit * 2])  # 取更多，后面再筛选
        
        entries = cur.fetchall()
        
        # 过滤已编译的
        uncompiled = [e for e in entries if e["source_id"] not in compiled_ids]
        
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
        
        # 计算匹配分数
        score = 0
        matched_keywords = []
        
        for kw in USER_PROFILE_KEYWORDS:
            if kw.lower() in title.lower() or kw.lower() in content.lower():
                score += 1
                matched_keywords.append(kw)
        
        if score > 0:
            entry["profile_score"] = score
            entry["matched_keywords"] = matched_keywords
            scored.append(entry)
    
    # 按分数排序
    scored.sort(key=lambda x: x["profile_score"], reverse=True)
    
    return scored


def generate_ai_summary(title, content):
    """用龙猫 API 生成一句话摘要"""
    if not LONGCAT_API_KEY:
        return None
    
    try:
        # 提取核心内容（去掉HTML标签）
        text = re.sub(r'<[^>]+>', ' ', content)
        text = re.sub(r'\s+', ' ', text).strip()[:2000]
        
        prompt = f"请用一句话总结这篇文章的核心内容（不超过50字）：\n标题：{title}\n内容：{text}"
        
        resp = requests.post(
            f"{LONGCAT_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {LONGCAT_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "LongCat-Flash-Lite",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100,
            },
            timeout=30,
        )
        
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
        else:
            print(f"      LongCat API 失败: {resp.status_code}")
            return None
    except Exception as e:
        print(f"      LongCat API 异常: {e}")
        return None


def compile_wiki_article(entry):
    """将知识条目编译成 wiki 文章"""
    source_id = entry["source_id"]
    title = entry["title"]
    content = entry.get("content", "") or entry.get("summary", "")
    source_url = entry.get("source_url", "")
    created_at = entry.get("created_at", datetime.now())
    
    # AI 摘要（如果没有的话）
    ai_summary = entry.get("ai_summary")
    if not ai_summary and content:
        print(f"    生成 AI 摘要...")
        ai_summary = generate_ai_summary(title, content)
    
    # 生成文件名（slug）
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')[:50]
    filename = f"{slug}.md"
    
    # 提取 metadata 中的标签
    metadata = entry.get("metadata", {}) or {}
    tags = metadata.get("tags", [])
    if not tags:
        # 从标题/内容推断标签
        tags = entry.get("matched_keywords", [])[:3]
    
    # AI Score（如果有）
    ai_score = metadata.get("ai_score", "-")
    
    # 构建文章内容
    date_str = created_at.strftime("%Y-%m-%d") if hasattr(created_at, 'strftime') else str(created_at)[:10]
    
    article_md = f"""# {title}

> 📅 {date_str} | 🏷️ {', '.join(tags) if tags else '未分类'} | AI Score: {ai_score}
> 🔗 [原文]({source_url}) | 来源：bestblogs

## 概要

{ai_summary if ai_summary else '（待补充）'}

## 内容摘要

{content[:500]}...

## 关键词匹配

{', '.join(entry.get('matched_keywords', ['无']))}

## 对我们的启示

- （待补充：结合用户画像分析）
"""
    
    return filename, article_md


def load_state():
    """加载编译状态"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {
        "last_compile": None,
        "compiled_ids": [],
        "new_entries_found": 0,
        "articles_created": 0,
    }


def save_state(state):
    """保存编译状态"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def update_index(articles_info):
    """更新 wiki 索引"""
    # 构建索引
    index_md = f"""# Wiki 索引

> 编译自 bestblogs.dev RSS，根据用户画像筛选
> 更新时间：{datetime.now().strftime('%Y-%m-%d')}

## 文章列表

| 主题 | AI Score | 文件 |
|------|----------|------|
"""
    
    for info in sorted(articles_info, key=lambda x: x.get("created_at", ""), reverse=True):
        score = info.get("ai_score", "-")
        index_md += f"| {info['title'][:40]} | {score} | [{info['filename']}](articles/{info['filename']}) |\n"
    
    index_md += f"""
## 筛选标准

- **数据源**：bestblogs.dev RSS（400+ 信息源，LLM 筛选过的精选内容）
- **用户画像**：Go/后端/AI/Agent/开源/运维
- **筛选方式**：标题关键词匹配（{', '.join(USER_PROFILE_KEYWORDS[:5])}）
- **编译方式**：提取摘要 + AI 一句话总结

## 编译记录

| 日期 | 新增文章 | 来源条目数 |
|------|----------|------------|
"""
    
    # 添加历史记录
    state = load_state()
    last_compile = state.get("last_compile", "未知")
    if last_compile:
        date_str = last_compile[:10] if isinstance(last_compile, str) else last_compile.strftime("%Y-%m-%d")
        index_md += f"| {date_str} | {state.get('articles_created', 0)} 篇 | {state.get('new_entries_found', 0)} 条筛选 |\n"
    
    INDEX_FILE.write_text(index_md)


def main():
    parser = argparse.ArgumentParser(description="Wiki 编译")
    parser.add_argument("--limit", type=int, default=10, help="编译数量上限")
    parser.add_argument("--dry-run", action="store_true", help="只打印不写入")
    args = parser.parse_args()
    
    print("="*50)
    print(f"📚 Wiki 编译 — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*50)
    
    # 1. 查询未编译条目
    print("\n📡 Step 1: 查询知识库")
    uncompiled = get_uncompiled_entries(args.limit * 2)
    print(f"  未编译条目: {len(uncompiled)} 条")
    
    # 2. 筛选高价值内容
    print("\n🎯 Step 2: 用户画像筛选")
    filtered = filter_by_profile(uncompiled)
    print(f"  匹配条目: {len(filtered)} 条")
    
    # 限制数量
    to_compile = filtered[:args.limit]
    
    if args.dry_run:
        print("\n🔍 筛选结果 (dry-run):")
        for entry in to_compile:
            print(f"  [{entry['profile_score']}] {entry['title'][:50]}")
            print(f"    匹配: {', '.join(entry['matched_keywords'])}")
        print("\n(dry-run 模式，不编译)")
        return
    
    # 3. 编译文章
    print(f"\n📝 Step 3: 编译文章 ({len(to_compile)} 篇)")
    
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    
    state = load_state()
    articles_info = []
    
    # 加载已有文章信息（用于更新索引）
    for f in ARTICLES_DIR.glob("*.md"):
        # 从文件提取标题（简单方式）
        content = f.read_text()
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if title_match:
            articles_info.append({
                "filename": f.name,
                "title": title_match.group(1),
                "created_at": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                "ai_score": "-",
            })
    
    for entry in to_compile:
        filename, article_md = compile_wiki_article(entry)
        
        article_file = ARTICLES_DIR / filename
        article_file.write_text(article_md)
        
        print(f"  ✅ {filename}")
        
        # 更新状态
        state["compiled_ids"].append(entry["source_id"])
        articles_info.append({
            "filename": filename,
            "title": entry["title"],
            "created_at": datetime.now().isoformat(),
            "ai_score": entry.get("metadata", {}).get("ai_score", "-"),
        })
    
    # 4. 更新状态和索引
    print("\n📊 Step 4: 更新索引")
    state["last_compile"] = datetime.now().isoformat()
    state["new_entries_found"] = len(filtered)
    state["articles_created"] = len(to_compile)
    save_state(state)
    
    update_index(articles_info)
    print(f"  ✅ index.md 已更新")
    
    print("\n✅ 编译完成!")
    print(f"  新增文章: {len(to_compile)} 篇")
    print(f"  累计文章: {len(articles_info)} 篇")


if __name__ == "__main__":
    main()