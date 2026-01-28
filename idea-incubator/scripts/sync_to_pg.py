import os
import sys
import re
import yaml
import argparse
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime, ARRAY, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import JSONB

# --- Configuration ---
# 使用 SQLAlchemy 格式的连接串
# 格式: postgresql://user:password@host:port/dbname
DB_URL = "postgresql://root:15671040800q@localhost:5433/idea_depot"

Base = declarative_base()

class Idea(Base):
    __tablename__ = 'ideas'

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    status = Column(String)
    created_at = Column(DateTime)
    tags = Column(ARRAY(String))  # 需要数据库支持数组类型，PG支持
    role = Column(String)
    trigger_context = Column(Text)
    original_hypothesis = Column(Text)
    mvp_scope = Column(Text)
    content_raw = Column(Text)
    structured_data = Column(JSONB) # 使用 JSONB 存储结构化数据
    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)

def init_db(engine):
    """Create tables if they don't exist."""
    try:
        Base.metadata.create_all(engine)
        # print("✅ Database schema initialized.")
    except Exception as e:
        print(f"❌ Error initializing schema: {e}")
        sys.exit(1)

def parse_markdown(file_path):
    """
    使用 PyYAML 解析 Frontmatter，使用正则提取正文段落
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Extract Frontmatter (PyYAML 的用武之地)
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        print(f"⚠️ No frontmatter found in {file_path}")
        return None
    
    fm_text = frontmatter_match.group(1)
    metadata = yaml.safe_load(fm_text) # PyYAML 在这里把 YAML 字符串转成 Python 字典
    
    # 2. Extract Title
    title_match = re.search(r'^# 💡 Idea: (.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Untitled"

    # 3. Helper to extract sections
    def extract_section(header):
        pattern = re.compile(rf'## {header}.*?\n(.*?)(?=\n## |\Z)', re.DOTALL)
        match = pattern.search(content)
        return match.group(1).strip() if match else None

    def extract_field(key_pattern, text_block):
        if not text_block: return None
        match = re.search(key_pattern, text_block)
        return match.group(1).strip() if match else None

    core_section = extract_section(r'1\. 核心定义')
    spec_section = extract_section(r'3\. 执行规约')
    debate_section = extract_section(r'2\. 方案博弈')
    closing_section = extract_section(r'4\. 落地复盘')

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
            "debate": debate_section,
            "spec": spec_section,
            "closing": closing_section
        }
    }

def sync_file_to_db(file_path):
    # 1. Parse File
    idea_data = parse_markdown(file_path)
    if not idea_data:
        return

    # 2. Connect DB
    engine = create_engine(DB_URL)
    init_db(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 3. Upsert Logic (Merge in SQLAlchemy automatically handles PK conflicts)
        idea = Idea(
            id=idea_data['id'],
            title=idea_data['title'],
            status=idea_data['status'],
            created_at=idea_data['created_at'],
            tags=idea_data['tags'],
            role=idea_data['role'],
            trigger_context=idea_data['trigger'],
            original_hypothesis=idea_data['hypothesis'],
            mvp_scope=idea_data['mvp'],
            content_raw=idea_data['content_raw'],
            structured_data=idea_data['structured_data']
        )
        
        # Merge: 如果主键存在则更新，不存在则插入
        session.merge(idea)
        session.commit()
        print(f"✅ Automatically synced to Database: {idea_data['title']} ({idea_data['id']})")
        
    except Exception as e:
        print(f"❌ Error syncing to DB: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync Idea Markdown to Database (SQLAlchemy)")
    parser.add_argument("file", help="Path to the .md file")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        sys.exit(1)

    sync_file_to_db(args.file)
