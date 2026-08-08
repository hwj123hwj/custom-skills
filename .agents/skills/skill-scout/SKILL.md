---
name: skill-scout
tags:
  - Automation
  - Utility
description: "Search existing skills before creating a new one. Checks for naming conflicts, tag overlap, and functional duplication. Use BEFORE creating any new skill to prevent wasted effort and registry bloat."
---

# Skill Scout

Use this skill **before** creating a new skill. It checks whether an existing skill already covers the intended capability.

## When to Use

- Before creating a new skill
- When thinking "I need a skill for X"
- When a user asks to add a new capability
- Before importing a third-party skill

## Process

### Step 1: Capture Intent

Record what the new skill would do:
- Target capability (1-sentence summary)
- Key scenarios it should handle
- Intended tags

### Step 2: Search Local Registry

Scan existing skills for overlap:

```bash
# Search by keyword in skill names and descriptions
cd web && npx tsx -e "
import skillsData from './src/data/skills-data.json' assert { type: 'json' };
const query = process.argv[1].toLowerCase();
const matches = skillsData.filter(s =>
  s.id.includes(query) ||
  s.description.toLowerCase().includes(query) ||
  s.tags.some(t => t.toLowerCase().includes(query))
);
matches.forEach(s => console.log(s.id, '|', s.tags.join(','), '|', s.description.slice(0,80)));
" "<keyword>"
```

Also check manually:
- Read `registry/skills.json` for tag-based overlap
- Read `skills/*/SKILL.md` titles for name collision

### Step 3: Check Tag Coverage

Determine if the new skill's intended tags are already well-covered:
- If there are 5+ skills with the same tag combination, the new skill must offer something genuinely different
- If the tag is rare (< 2 skills), the new skill is likely additive

### Step 4: Decision

Present the verdict:

| Verdict | Meaning |
|---------|---------|
| **Create** | No overlap found. Proceed with creation. |
| **Extend** | An existing skill covers 80%+ of the intent. Suggest extending it instead. |
| **Duplicate** | An existing skill already does this. Point to it and stop. |
| **Merge** | Multiple skills cover parts of the intent. Suggest merging or creating a meta-skill. |

### Step 5: If Creating

After confirming the skill should be created, suggest:
- A unique kebab-case name (verified not taken)
- Appropriate tags from the ALLOWED_TAGS whitelist
- Whether upstream metadata is needed (if derived from a third-party source)

## Anti-Patterns

- Don't create "better" versions of existing skills without checking first
- Don't create skills with overlapping tags without clear differentiation
- Don't skip this step even when "obviously" new — the registry grows fast
