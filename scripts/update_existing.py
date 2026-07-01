#!/usr/bin/env python3
"""Update existing mattpocock skills: add Matt Pocock tag, fix upstream paths."""
import re
from pathlib import Path

DST = Path("/home/q/custom-skills/skills")
NEW_SHA = "b38badf7091afc614dedffc03ea8c8ad2b643cb4"
NEW_DATE = "2026-06-25T17:00:00.000Z"

# Skills to update
UPDATES = {
    "diagnose": {"upstreamPath": "skills/engineering/diagnosing-bugs"},
    "review": {"upstreamPath": "skills/engineering/code-review"},
    "grill-me": {},
    "handoff": {},
    "improve-codebase-architecture": {},
    "prototype": {},
    "tdd": {},
    "to-issues": {},
    "to-prd": {},
    "git-guardrails-claude-code": {},
}

def update_skill(name, extra):
    path = DST / name / "SKILL.md"
    if not path.exists():
        print(f"  SKIP {name}: not found")
        return

    text = path.read_text(encoding='utf-8')

    # Update upstreamSha
    text = re.sub(r'upstreamSha: .*', f'upstreamSha: {NEW_SHA}', text)

    # Update upstreamPath if provided
    if "upstreamPath" in extra:
        text = re.sub(r'upstreamPath: .*', f'upstreamPath: {extra["upstreamPath"]}', text)

    # Update lastUpdated
    text = re.sub(r'lastUpdated: .*', f'lastUpdated: "{NEW_DATE}"', text)

    # Add Matt Pocock tag if not present
    if "Matt Pocock" not in text:
        # Find the tags list and add Matt Pocock before the closing bracket
        text = re.sub(r'(tags:\s*\n(?:  - .+\n)*)', lambda m: m.group(1) + '  - Matt Pocock\n', text, count=1)

    path.write_text(text, encoding='utf-8')
    print(f"  OK: {name}")

for name, extra in UPDATES.items():
    update_skill(name, extra)

print("Done updating existing skills")
