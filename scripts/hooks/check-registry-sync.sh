#!/usr/bin/env bash
# Stop hook: Check if skills/ has uncommitted changes that need registry sync
# Reminds the user (or agent) to run generate:registry before stopping

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")

# Check for modified or new SKILL.md files
CHANGED_SKILLS=$(cd "$REPO_ROOT" && git diff --name-only HEAD -- 'skills/*/SKILL.md' 2>/dev/null || true)
NEW_SKILLS=$(cd "$REPO_ROOT" && git ls-files --others --exclude-standard -- 'skills/*/SKILL.md' 2>/dev/null || true)

# Check for modified or new agent files
CHANGED_AGENTS=$(cd "$REPO_ROOT" && git diff --name-only HEAD -- 'agents/*.md' 2>/dev/null || true)
NEW_AGENTS=$(cd "$REPO_ROOT" && git ls-files --others --exclude-standard -- 'agents/*.md' 2>/dev/null || true)

# Check if registry is up to date (compare skills count)
if [[ -n "$CHANGED_SKILLS" || -n "$NEW_SKILLS" || -n "$CHANGED_AGENTS" || -n "$NEW_AGENTS" ]]; then
  # Check if generate:registry was run after the latest skill change
  REGISTRY_FILE="$REPO_ROOT/registry/skills.json"
  if [[ -f "$REGISTRY_FILE" ]]; then
    # Simple check: are there staged but un-generated changes?
    REGISTRY_IN_INDEX=$(cd "$REPO_ROOT" && git diff --name-only HEAD -- 'registry/skills.json' 2>/dev/null || true)
    
    if [[ -z "$REGISTRY_IN_INDEX" ]]; then
      echo "⚠️  Registry may be out of sync. Skills/agents were modified but registry/skills.json was not regenerated." >&2
      echo "Run: cd web && npm run generate:registry" >&2
      echo "" >&2
      if [[ -n "$NEW_SKILLS" ]]; then
        echo "New skills:" >&2
        echo "$NEW_SKILLS" | sed 's/^/  /' >&2
      fi
      if [[ -n "$CHANGED_SKILLS" ]]; then
        echo "Modified skills:" >&2
        echo "$CHANGED_SKILLS" | sed 's/^/  /' >&2
      fi
      if [[ -n "$NEW_AGENTS" ]]; then
        echo "New agents:" >&2
        echo "$NEW_AGENTS" | sed 's/^/  /' >&2
      fi
      if [[ -n "$CHANGED_AGENTS" ]]; then
        echo "Modified agents:" >&2
        echo "$CHANGED_AGENTS" | sed 's/^/  /' >&2
      fi
      echo "" >&2
      echo "Also remember to update web/src/i18n/skill-descriptions.ts if adding new skills/agents." >&2
    fi
  fi
fi

exit 0
