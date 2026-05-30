#!/usr/bin/env bash
# PostToolUse hook: After writing SKILL.md, check if i18n entry exists
# Reminds to add Chinese description to skill-descriptions.ts

set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)

# Only check SKILL.md files
if [[ "$FILE_PATH" != *"/SKILL.md" ]]; then
  exit 0
fi

# Extract skill name from frontmatter
NAME=""
if [[ -f "$FILE_PATH" ]]; then
  NAME=$(awk '/^---$/{if(!start){start=1;next}else{exit}}start && /^name:/{gsub(/^name:[[:space:]]*/,""); gsub(/["'"'"']/,""); print; exit}' "$FILE_PATH")
fi

if [[ -z "$NAME" ]]; then
  exit 0
fi

# Find skill-descriptions.ts
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
I18N_FILE="$REPO_ROOT/web/src/i18n/skill-descriptions.ts"

if [[ -f "$I18N_FILE" ]]; then
  if ! grep -q "'$NAME'" "$I18N_FILE"; then
    echo "💡 New skill '$NAME' detected. Remember to add Chinese description to web/src/i18n/skill-descriptions.ts" >&2
    echo "Add this entry to skillDescriptionsZh:" >&2
    echo "  '$NAME': '中文描述'" >&2
  fi
fi

exit 0
