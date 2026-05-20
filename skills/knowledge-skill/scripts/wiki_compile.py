#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "psycopg2-binary",
#     "python-dotenv",
#     "requests"
# ]
# ///
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

psycopg2.extras.register_uuid()
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


def get_all_entries(limit=50):
    """查询所有条目（用于 --recompile 模式）"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cur.execute("""
            SELECT id, source_type, source_id, source_url, title, content, summary,
                   ai_summary, created_at, metadata
            FROM knowledge_items
            ORDER BY created_at DESC
            LIMIT %s
        """, [limit])
        return [dict(e) for e in cur.fetchall()]
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


def boost_by_targets(entries, target_concepts=None, target_entities=None):
    """对匹配目标 concept/entity 的条目提升优先级。
    当 --target-concepts 或 --target-entities 被指定时，
    优先编译能增强这些薄弱 concept/entity 页面的条目。
    """
    if not target_concepts and not target_entities:
        return entries

    target_terms_lower = set()
    for t in (target_concepts or []):
        target_terms_lower.add(t.lower())
    for t in (target_entities or []):
        target_terms_lower.add(t.lower())

    boosted = []
    rest = []
    for entry in entries:
        title = (entry.get("title") or "").lower()
        content = (entry.get("content", "") or entry.get("summary", "")).lower()
        haystack = f"{title} {content}"
        if any(term in haystack for term in target_terms_lower):
            # 给匹配条目额外加分
            entry["profile_score"] = entry.get("profile_score", 0) + 10
            boosted.append(entry)
        else:
            rest.append(entry)

    return boosted + rest

def analyze_article_with_llm(title, content):
    """用 LLM 提取摘要、概念、实体和关键论点 (Karpathy 降维法)"""
    if not LONGCAT_API_KEY:
        return {"summary": "API 未配置", "concepts": [], "entities": [], "key_points": []}

    text = re.sub(r'<[^>]+>', ' ', content)
    text = re.sub(r'\s+', ' ', text).strip()[:4000]

    prompt = f"""请深度分析以下文章，提取结构化知识。
标题：{title}
内容：{text}

请严格按以下 JSON 格式输出（不要输出代码块标记如 ```json，直接输出合法的 JSON 字符串）：
{{
  "summary": "一句话总结核心内容（30-60字，包含核心结论）",
  "concepts": ["概念1", "概念2"],
  "entities": ["实体1", "实体2"],
  "key_points": ["关键论点1", "关键论点2", "关键论点3"],
  "concept_details": {{
    "概念1": "一句话解释这个概念在此文中的具体含义或用法",
    "概念2": "..."
  }},
  "entity_details": {{
    "实体1": "一句话说明此实体在文中的角色或贡献",
    "实体2": "..."
  }}
}}
注意：
1. concepts 指技术、理论、方法论等（如 RAG, Agent, 混合检索），最多3个。
2. entities 指具体的人、公司、产品、开源库等（如 OpenAI, Postgres, Karpathy），最多3个。
3. key_points 是文章的核心论点或关键发现，2-4 条，每条 15-40 字。
4. concept_details 和 entity_details 是对应概念/实体在本文语境下的具体含义，帮助生成更稠密的 wiki 页面。
"""
    try:
        resp = requests.post(
            f"{LONGCAT_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {LONGCAT_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "LongCat-Flash-Lite",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.1,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            result_text = resp.json()["choices"][0]["message"]["content"].strip()
            result_text = re.sub(r'^```json\s*', '', result_text)
            result_text = re.sub(r'\s*```$', '', result_text)
            parsed = json.loads(result_text)
            # 确保所有字段都有默认值
            parsed.setdefault("key_points", [])
            parsed.setdefault("concept_details", {})
            parsed.setdefault("entity_details", {})
            return parsed
        else:
            print(f"      LongCat API 失败: {resp.status_code}")
    except Exception as e:
        print(f"      解析异常: {e}")

    return {"summary": "解析失败", "concepts": [], "entities": [], "key_points": [], "concept_details": {}, "entity_details": {}}

def make_slug(text):
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', slug).strip('-')[:50]

def update_or_create_node_page(node_type, name, source_title, source_filename,
                               context_description=None):
    """创建或更新实体/概念页面，增加上下文描述让页面更稠密。"""
    slug = make_slug(name)
    if not slug:
        return None

    filename = f"{node_type}-{slug}.md"
    filepath = WIKI_PAGES_DIR / filename

    link_line = f"- [[{source_filename.replace('.md', '')}]] ({source_title})"

    if filepath.exists():
        content = filepath.read_text()
        changed = False

        # 追加 context 到相关来源描述（如果有新的上下文描述）
        if context_description and "## 来源语境" in content:
            # 检查这个 source 是否已有语境
            if source_title not in content:
                content = content.replace(
                    "## 来源语境",
                    f"## 来源语境\n- **{source_title}**: {context_description}",
                )
                changed = True
        elif context_description and "## 来源语境" not in content:
            # 在 Mentions 之前插入语境段
            context_section = f"## 来源语境\n- **{source_title}**: {context_description}\n\n"
            if "## 关联来源 (Mentions)" in content:
                content = content.replace("## 关联来源 (Mentions)", context_section + "## 关联来源 (Mentions)")
            else:
                content += "\n\n" + context_section
            changed = True

        # 追加到关联来源列表
        if link_line not in content:
            if "## 关联来源 (Mentions)" in content:
                content += f"\n{link_line}"
            else:
                content += f"\n\n## 关联来源 (Mentions)\n{link_line}"
            changed = True

        if changed:
            filepath.write_text(content)
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
        # 新页面：如果有 context_description 则加入
        context_section = ""
        if context_description:
            context_section = f"\n## 来源语境\n- **{source_title}**: {context_description}\n"

        md = f"""---
type: {node_type}
title: {name}
date: {date_str}
---

# {name}
{context_section}
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

    # 建立图谱链接，传递 context_description 让 concept/entity 页面更稠密
    concept_details = analysis.get("concept_details", {})
    entity_details = analysis.get("entity_details", {})

    concept_links = []
    for c in analysis.get("concepts", []):
        context_desc = concept_details.get(c)
        c_file = update_or_create_node_page("concept", c, title, filename,
                                            context_description=context_desc)
        if c_file:
            concept_links.append(f"[[{c_file.replace('.md', '')}]]")

    entity_links = []
    for e in analysis.get("entities", []):
        context_desc = entity_details.get(e)
        e_file = update_or_create_node_page("entity", e, title, filename,
                                            context_description=context_desc)
        if e_file:
            entity_links.append(f"[[{e_file.replace('.md', '')}]]")

    # 如果本身有ai_summary就用，否则用提取的
    final_summary = entry.get("ai_summary") or analysis.get("summary", "无摘要")

    # 构建关键论点段落（让 source 页面更厚）
    key_points = analysis.get("key_points", [])
    key_points_section = ""
    if key_points:
        points_lines = "\n".join(f"{i+1}. {p}" for i, p in enumerate(key_points))
        key_points_section = f"""
## 关键论点
{points_lines}
"""

    # 完整内容（不硬截断，用更长的上限）
    content_display = content[:2000]
    content_suffix = "..." if len(content) > 2000 else ""

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
{key_points_section}
## 知识图谱 (Knowledge Graph)
- **相关概念 (Concepts)**: {', '.join(concept_links) if concept_links else '无'}
- **相关实体 (Entities)**: {', '.join(entity_links) if entity_links else '无'}

## 内容片段
{content_display}{content_suffix}
"""
    return filename, article_md, analysis


def link_wiki_to_memory_cards(entry_id, concepts, entities):
    """
    将 wiki 编译提取的概念/实体与 memory_cards 双向关联。
    找到 keywords 与 concepts/entities 有交集的 memory_cards，
    将它们互相添加到 related_card_ids。
    """
    all_terms = list(set(concepts + entities))
    if not all_terms:
        return 0

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # 找到 keywords 与提取的概念有交集的活跃 memory_cards
        cur.execute(
            """
            SELECT id, related_card_ids
            FROM memory_cards
            WHERE confidence > 0
              AND keywords && %s
            """,
            [all_terms],
        )
        matching_cards = [dict(row) for row in cur.fetchall()]

        if not matching_cards:
            return 0

        # 找到该 knowledge_item 对应的 memory_card（如果有）
        cur.execute(
            """
            SELECT id, related_card_ids
            FROM memory_cards
            WHERE source_item_ids @> ARRAY[%s]
              AND confidence > 0
            """,
            [str(entry_id)],
        )
        source_cards = [dict(row) for row in cur.fetchall()]

        linked = 0
        for match_card in matching_cards:
            for source_card in source_cards:
                # 双向添加关联（related_card_ids 是 UUID[]，必须传 UUID 对象）
                match_id = match_card["id"]
                source_id = source_card["id"]

                if match_id == source_id:
                    continue

                # source_card → match_card
                existing = source_card.get("related_card_ids") or []
                if match_id not in existing:
                    existing.append(match_id)
                    cur.execute(
                        "UPDATE memory_cards SET related_card_ids = %s, updated_at = NOW() WHERE id = %s",
                        [existing, source_card["id"]],
                    )

                # match_card → source_card
                existing_m = match_card.get("related_card_ids") or []
                if source_id not in existing_m:
                    existing_m.append(source_id)
                    cur.execute(
                        "UPDATE memory_cards SET related_card_ids = %s, updated_at = NOW() WHERE id = %s",
                        [existing_m, match_card["id"]],
                    )

                linked += 1

        conn.commit()
        return linked
    except Exception as e:
        print(f"      Warning: memory card linking failed: {e}")
        conn.rollback()
        return 0
    finally:
        cur.close()
        conn.close()

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
    parser.add_argument("--recompile", action="store_true",
                        help="重编译模式：对所有已编译条目重新提取，用增强版 LLM prompt 覆盖旧页面")
    parser.add_argument("--target-concept", action="append", help="优先编译能增强此 concept 的条目，可重复传入")
    parser.add_argument("--target-entity", action="append", help="优先编译能增强此 entity 的条目，可重复传入")
    args = parser.parse_args()

    print("="*50)
    print(f"🕸️ LLM Wiki 图谱编译 — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    if args.recompile:
        print("🔄 重编译模式：覆盖已有页面")
    print("="*50)

    if args.target_concept or args.target_entity:
        targets = (args.target_concept or []) + (args.target_entity or [])
        print(f"🎯 定向增强: {', '.join(targets)}")

    WIKI_PAGES_DIR.mkdir(parents=True, exist_ok=True)

    if args.recompile:
        # 重编译模式：获取所有条目（含已编译），重新生成增强版页面
        all_entries = get_all_entries(args.limit * 2)
        filtered = filter_by_profile(all_entries)
        filtered = boost_by_targets(filtered, args.target_concept, args.target_entity)
        filtered = filtered[:args.limit]
    else:
        # 正常模式：只编译新条目
        uncompiled = get_uncompiled_entries(args.limit * 2)
        filtered = filter_by_profile(uncompiled)
        filtered = boost_by_targets(filtered, args.target_concept, args.target_entity)
        filtered = filtered[:args.limit]

    if not filtered:
        print("✅ 当前没有需要编译的新知识条目。")
        return

    if args.dry_run:
        print(f"🔍 待编译条目 (dry-run): {len(filtered)} 条")
        for entry in filtered:
            print(f"  - {entry['title'][:60]}")
        return

    state = load_state()

    for entry in filtered:
        print(f"\n➡️ 处理: {entry['title'][:40]}...")
        filename, article_md, analysis = compile_wiki_article(entry)

        article_file = WIKI_PAGES_DIR / filename
        article_file.write_text(article_md)

        # 记录已编译
        entry_id = str(entry.get("id"))
        source_id = str(entry.get("source_id", entry["id"]))
        if entry_id not in state["compiled_ids"]:
            state["compiled_ids"].append(entry_id)
        if source_id not in state["compiled_ids"]:
            state["compiled_ids"].append(source_id)
        print(f"  ✅ 页面已生成: {filename}")
        print(f"  🧠 提取概念: {', '.join(analysis.get('concepts', []))}")
        print(f"  🏢 提取实体: {', '.join(analysis.get('entities', []))}")
        if analysis.get("key_points"):
            print(f"  📌 关键论点: {len(analysis['key_points'])} 条")
        if analysis.get("concept_details") or analysis.get("entity_details"):
            print(f"  🔗 来源语境: {len(analysis.get('concept_details', {})) + len(analysis.get('entity_details', {}))} 条")

        # 将概念/实体与 memory_cards 双向关联
        linked = link_wiki_to_memory_cards(
            entry["id"],
            analysis.get("concepts", []),
            analysis.get("entities", []),
        )
        if linked > 0:
            print(f"  🔗 已关联 {linked} 对 memory_cards")

    save_state(state)
    update_index()
    print("\n✅ 知识图谱索引 index.md 已更新。编译完成！")

if __name__ == "__main__":
    main()