import os
import sys
import re
import json
import yaml
import datetime
import argparse
import psycopg2
from psycopg2.extras import Json

# --- Configuration ---
DB_CONFIG = {
    "dbname": "idea_depot",
    "user": "root",
    "password": "15671040800q",
    "host": "localhost",
    "port": "5433"
}

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print("💡 Hint: Did you create the database? Try: CREATE DATABASE idea_depot;")
        sys.exit(1)

def init_db():
    """Create the ideas table if it doesn't exist."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Enable UUID extension if needed, but we use text ID from frontmatter for now
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS ideas (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        status TEXT,
        created_at TIMESTAMP,
        tags TEXT[], -- Array of text
        role TEXT,
        trigger_context TEXT,
        original_hypothesis TEXT,
        mvp_scope TEXT,
        content_raw TEXT,         -- Full Markdown content
        structured_data JSONB,    -- Parsed sections for RAG/Analysis
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        cur.execute(create_table_query)
        conn.commit()
        # print("✅ Database schema initialized.")
    except Exception as e:
        print(f"❌ Error initializing schema: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def parse_markdown(file_path):
    """
    Parse the Idea Markdown file to extract Frontmatter and Sections.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Extract Frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        print(f"⚠️ No frontmatter found in {file_path}")
        return None
    
    fm_text = frontmatter_match.group(1)
    metadata = yaml.safe_load(fm_text)
    
    # 2. Extract Title
    title_match = re.search(r'^# 💡 Idea: (.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Untitled"

    # 3. Extract Sections (Simple Regex for Core fields)
    # Using regex to capture content between headers
    def extract_section(header):
        pattern = re.compile(rf'## {header}.*?\n(.*?)(?=\n## |\Z)', re.DOTALL)
        match = pattern.search(content)
        return match.group(1).strip() if match else None

    # Specific parsers for key fields to put into columns
    def extract_field(key_pattern, text_block):
        if not text_block: return None
        match = re.search(key_pattern, text_block)
        return match.group(1).strip() if match else None

    core_section = extract_section(r'1\. 核心定义')
    spec_section = extract_section(r'3\. 执行规约')

    role = extract_field(r'\*\*Role.*?\*\*: (.*)', core_section)
    trigger = extract_field(r'\*\*Trigger.*?\*\*: (.*)', core_section)
    hypothesis = extract_field(r'\*\*Original Hypothesis.*?\*\*: (.*)', core_section)
    mvp = extract_field(r'\*\*MVP Scope.*?\*\*: (.*)', spec_section)

    return {
        "id": str(metadata.get('id', '')),
        "title": title,
        "status": metadata.get('status', 'incubating'),
        "created_at": metadata.get('created_at'),
        "tags": metadata.get('tags', []),
        "role": role,
        "trigger": trigger,
        "hypothesis": hypothesis,
        "mvp": mvp,
        "content_raw": content,
        "structured_data": {
            "core": core_section,
            "debate": extract_section(r'2\. 方案博弈'),
            "spec": spec_section,
            "closing": extract_section(r'4\. 落地复盘')
        }
    }

def sync_file_to_db(file_path):
    data = parse_markdown(file_path)
    if not data:
        return

    conn = get_db_connection()
    cur = conn.cursor()

    upsert_query = """
    INSERT INTO ideas (
        id, title, status, created_at, tags, 
        role, trigger_context, original_hypothesis, 
        mvp_scope, content_raw, structured_data, last_updated
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
    ON CONFLICT (id) DO UPDATE SET
        title = EXCLUDED.title,
        status = EXCLUDED.status,
        created_at = EXCLUDED.created_at,
        tags = EXCLUDED.tags,
        role = EXCLUDED.role,
        trigger_context = EXCLUDED.trigger_context,
        original_hypothesis = EXCLUDED.original_hypothesis,
        mvp_scope = EXCLUDED.mvp_scope,
        content_raw = EXCLUDED.content_raw,
        structured_data = EXCLUDED.structured_data,
        last_updated = NOW();
    """

    try:
        cur.execute(upsert_query, (
            data['id'],
            data['title'],
            data['status'],
            data['created_at'],
            data['tags'],
            data['role'],
            data['trigger'],
            data['hypothesis'],
            data['mvp'],
            data['content_raw'],
            Json(data['structured_data'])
        ))
        conn.commit()
        print(f"✅ Automatically synced to Database: {data['title']} ({data['id']})")
    except Exception as e:
        print(f"❌ Error syncing to DB: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync Idea Markdown to Postgres")
    parser.add_argument("file", help="Path to the .md file")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        sys.exit(1)

    init_db()  # Ensure table exists
    sync_file_to_db(args.file)
