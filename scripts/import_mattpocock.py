#!/usr/bin/env python3
"""Batch-import mattpocock skills into custom-skills repo."""
import json, os, shutil, re, yaml
from pathlib import Path
from datetime import datetime, timezone, timedelta

UPSTREAM = "mattpocock/skills"
UPSTREAM_SHA = "b38badf7091afc614dedffc03ea8c8ad2b643cb4"
SRC = Path("/tmp/mattpocock-skills/skills")
DST = Path("/home/q/custom-skills/skills")
DATE = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%dT%H:%M:%S.000Z")

SKILLS_MAP = [
    # (name, src_rel_path, tags, displayName)
    # --- Engineering ---
    ("ask-matt", "engineering/ask-matt", ["Planning", "Productivity", "Matt Pocock"], "Ask Matt"),
    ("codebase-design", "engineering/codebase-design", ["Architecture", "Coding", "Matt Pocock"], "Codebase Design"),
    ("code-review", "engineering/code-review", ["Coding", "Testing", "Matt Pocock"], "Code Review"),
    ("diagnosing-bugs", "engineering/diagnosing-bugs", ["Coding", "Debugging", "Matt Pocock"], "Diagnosing Bugs"),
    ("domain-modeling", "engineering/domain-modeling", ["Architecture", "Planning", "Matt Pocock"], "Domain Modeling"),
    ("grill-with-docs", "engineering/grill-with-docs", ["Planning", "Productivity", "Matt Pocock"], "Grill With Docs"),
    ("implement", "engineering/implement", ["Coding", "Workflow", "Matt Pocock"], "Implement"),
    ("resolving-merge-conflicts", "engineering/resolving-merge-conflicts", ["Coding", "DevOps", "Matt Pocock"], "Resolving Merge Conflicts"),
    ("setup-matt-pocock-skills", "engineering/setup-matt-pocock-skills", ["DevOps", "Tools", "Matt Pocock"], "Setup Matt Pocock Skills"),
    ("triage", "engineering/triage", ["Planning", "Workflow", "Matt Pocock"], "Triage"),
    # --- Productivity ---
    ("grilling", "productivity/grilling", ["Planning", "Productivity", "Matt Pocock"], "Grilling"),
    ("teach", "productivity/teach", ["Productivity", "Education", "Matt Pocock"], "Teach"),
    ("writing-great-skills", "productivity/writing-great-skills", ["Writing", "Productivity", "Matt Pocock"], "Writing Great Skills"),
    # --- Misc ---
    ("migrate-to-shoehorn", "misc/migrate-to-shoehorn", ["Coding", "Testing", "Matt Pocock"], "Migrate to Shoehorn"),
    ("scaffold-exercises", "misc/scaffold-exercises", ["Coding", "Tools", "Matt Pocock"], "Scaffold Exercises"),
    ("setup-pre-commit", "misc/setup-pre-commit", ["DevOps", "Tools", "Matt Pocock"], "Setup Pre-Commit"),
    # --- Personal ---
    ("edit-article", "personal/edit-article", ["Writing", "Content", "Matt Pocock"], "Edit Article"),
    ("obsidian-vault", "personal/obsidian-vault", ["Knowledge", "Tools", "Matt Pocock"], "Obsidian Vault"),
    # --- In-Progress ---
    ("decision-mapping", "in-progress/decision-mapping", ["Planning", "Workflow", "Matt Pocock"], "Decision Mapping"),
    ("loop-me", "in-progress/loop-me", ["Planning", "Productivity", "Matt Pocock"], "Loop Me"),
    ("wizard", "in-progress/wizard", ["DevOps", "Tools", "Matt Pocock"], "Wizard"),
    ("writing-beats", "in-progress/writing-beats", ["Writing", "Content", "Matt Pocock"], "Writing Beats"),
    ("writing-fragments", "in-progress/writing-fragments", ["Writing", "Content", "Matt Pocock"], "Writing Fragments"),
    ("writing-shape", "in-progress/writing-shape", ["Writing", "Content", "Matt Pocock"], "Writing Shape"),
]

def parse_frontmatter(text):
    """Extract YAML frontmatter from markdown text."""
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
    if not m:
        return {}, text
    fm = yaml.safe_load(m.group(1)) or {}
    body = text[m.end():]
    return fm, body

def build_skill(name, src_path, tags, display_name):
    """Create SKILL.md and copy companion files."""
    skill_dir = DST / name
    skill_dir.mkdir(parents=True, exist_ok=True)

    upstream_md = SRC / src_path / "SKILL.md"
    if not upstream_md.exists():
        print(f"  SKIP {name}: SKILL.md not found at {upstream_md}")
        return False

    raw = upstream_md.read_text(encoding='utf-8')
    fm, body = parse_frontmatter(raw)

    desc = fm.get('description', display_name)
    if isinstance(desc, str):
        desc = ' '.join(desc.split())

    our_fm = {
        'name': name,
        'author': 'mattpocock',
        'upstream': UPSTREAM,
        'upstreamPath': f"skills/{src_path}",
        'upstreamSha': UPSTREAM_SHA,
        'lastUpdated': DATE,
        'tags': tags,
        'description': desc,
    }

    if fm.get('disable-model-invocation'):
        our_fm['disable-model-invocation'] = True
    if fm.get('argument-hint'):
        our_fm['argument-hint'] = fm['argument-hint']

    fm_yaml = yaml.dump(our_fm, allow_unicode=True, sort_keys=False, width=200).strip()
    content = f"---\n{fm_yaml}\n---\n\n{body}"

    out_path = skill_dir / "SKILL.md"
    out_path.write_text(content, encoding='utf-8')

    # Copy companion files
    src_dir = SRC / src_path
    for f in src_dir.iterdir():
        if f.name in ("SKILL.md", "README.md"):
            continue
        if f.is_file():
            shutil.copy2(str(f), str(skill_dir / f.name))

    return True

def main():
    created = []
    for name, src_path, tags, display_name in SKILLS_MAP:
        print(f"  {name}...")
        if build_skill(name, src_path, tags, display_name):
            created.append(name)

    print(f"\nCreated {len(created)} skills")
    return created

if __name__ == "__main__":
    main()
