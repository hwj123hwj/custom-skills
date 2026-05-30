---
name: skill-create
tags:
  - Automation
  - Utility
description: "Template-driven skill creation. Generates a compliant SKILL.md with correct frontmatter, adds i18n entries, and triggers registry sync. Use when creating a new skill to ensure it passes all validation checks."
---

# Skill Create

A template-driven process for creating new skills that pass all validation checks on the first try.

## When to Use

- After `skill: skill-scout` confirms the skill should be created
- When the user asks to create/add a new skill
- When importing a third-party skill

## Process

### Step 1: Gather Requirements

Ask the user (or determine from context):
1. **Skill name** (kebab-case, verified unique via skill-scout)
2. **Description** (1-2 sentences, include trigger phrases)
3. **Tags** (1-5 from ALLOWED_TAGS whitelist in `web/scripts/validate-registry.ts`)
4. **Source type**: original or third-party?
5. **Third-party details** (if applicable):
   - Upstream repo (`owner/repo`)
   - Upstream sub-path (if not at repo root)
   - Author GitHub ID

### Step 2: Create SKILL.md from Template

Use this template — **all fields must be present**:

```markdown
---
name: <kebab-case-id>
tags:
  - <Tag1>
  - <Tag2>
description: "<description with trigger phrases>"
---

# <Display Name>

<skill body content>
```

For third-party skills, add upstream metadata:

```yaml
---
name: <kebab-case-id>
author: <github-id>
upstream: <owner/repo>
upstreamPath: <sub/path>      # if not at repo root
upstreamSha: <commit-sha>     # from: git ls-remote <repo-url> HEAD
lastUpdated: "<ISO-8601>"
tags:
  - <Tag1>
  - <Tag2>
description: "<description>"
---
```

### Step 3: Add i18n Entry

Add Chinese description to `web/src/i18n/skill-descriptions.ts`:

```typescript
'<skill-id>':
  '中文描述，包含触发词。',
```

If the skill has a Chinese description in SKILL.md, also add English translation to `skillDescriptionsEn`.

### Step 4: Stage and Generate

```bash
# Stage the new skill
git add skills/<skill-id>/

# Generate registry (must run after staging)
cd web && npm run generate:registry

# Validate
cd web && npm run validate:registry
```

### Step 5: Verify

- Check that the skill appears in `registry/skills.json`
- Check that README.md skill table includes the new skill
- Check that `validate:registry` passes with no errors

## Validation Checklist

Before declaring done, verify:

- [ ] `name` is kebab-case and matches directory name
- [ ] `description` is at least 20 characters and includes trigger phrases
- [ ] `tags` are from the ALLOWED_TAGS whitelist (1-5 tags)
- [ ] If third-party: `author`, `upstream`, `upstreamSha` are all set
- [ ] i18n entry added to `skill-descriptions.ts`
- [ ] `npm run validate:registry` passes
- [ ] `npm run lint` passes
- [ ] `npm run build` passes

## Common Mistakes

- Forgetting to `git add` before `generate:registry` (skills won't be detected)
- Using tags not in the whitelist (CI will fail)
- Missing i18n entry (validation will fail)
- Using block scalar (`description: |`) — prefer inline string for description
