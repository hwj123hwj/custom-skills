#!/usr/bin/env python3
"""Sync Chinese descriptions from skill-descriptions.ts to skill-desc-zh.json."""
import json, re
from pathlib import Path

ROOT = Path("/home/q/custom-skills")

# 1. Extract from TS
ts_path = ROOT / "web/src/i18n/skill-descriptions.ts"
ts_content = ts_path.read_text(encoding='utf-8')

# Find all skill descriptions in the TS object
# Pattern: 'skill-id':\n    'Description text',
desc_map = {}
for m in re.finditer(r"'([^']+)':\s*\n\s*'([^']*)'", ts_content):
    skill_id = m.group(1)
    desc = m.group(2).replace("\\'", "'")
    if skill_id not in ('emoji',):  # Skip metadata keys
        desc_map[skill_id] = desc

# 2. Get all skills from registry
reg_path = ROOT / "registry/skills.json"
with open(reg_path) as f:
    registry = json.load(f)

# 3. Build complete zh map
zh_map = {}
for skill in registry:
    sid = skill['id']
    if sid in desc_map:
        zh_map[sid] = desc_map[sid]
    else:
        zh_map[sid] = skill.get('description', '')

# 4. Write
zh_path = ROOT / "web/src/i18n/locales/skill-desc-zh.json"
zh_path.write_text(json.dumps(zh_map, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

print(f"Synced {len(zh_map)} skills to skill-desc-zh.json")
print(f"Previous: 12 keys → Now: {len(zh_map)} keys")
