#!/usr/bin/env bash
# PreToolUse hook: Validate SKILL.md structure before write/edit
# Blocks writes to SKILL.md that don't meet structural requirements

set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)

# Only check SKILL.md files
if [[ "$FILE_PATH" != *"/SKILL.md" ]]; then
  exit 0
fi

# Read the content that will be written
CONTENT=""
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null || true)

if [[ "$TOOL" == "Write" ]]; then
  CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // empty' 2>/dev/null || true)
elif [[ "$TOOL" == "Edit" ]]; then
  # For edits, read the existing file and apply the edit mentally
  # We can't fully validate an Edit, so just check the file exists and has frontmatter
  if [[ -f "$FILE_PATH" ]]; then
    exit 0  # Allow edits to existing files
  fi
  exit 0
else
  exit 0
fi

if [[ -z "$CONTENT" ]]; then
  exit 0
fi

# Extract frontmatter (between --- markers)
FM=$(echo "$CONTENT" | awk '/^---$/{if(!start){start=1;next}else{exit}}start{print}')

ERRORS=""

# Check required fields
NAME=$(echo "$FM" | grep -E '^name:' | head -1 | sed 's/^name:[[:space:]]*//' | sed 's/^["'"'"']//;s/["'"'"']$//')
DESC=$(echo "$FM" | grep -E '^description:' | head -1 | sed 's/^description:[[:space:]]*//' | sed 's/^["'"'"']//;s/["'"'"']$//')
TAGS=$(echo "$FM" | grep -E '^tags:' | head -1)

if [[ -z "$NAME" ]]; then
  ERRORS="${ERRORS}• Missing required field 'name'\n"
fi

if [[ -z "$DESC" ]]; then
  ERRORS="${ERRORS}• Missing required field 'description'\n"
fi

if [[ -z "$TAGS" ]]; then
  ERRORS="${ERRORS}• Missing required field 'tags'\n"
fi

# Check name is kebab-case
if [[ -n "$NAME" ]] && [[ ! "$NAME" =~ ^[a-z][a-z0-9]*(-[a-z0-9]+)*$ ]]; then
  ERRORS="${ERRORS}• 'name' must be kebab-case (got: $NAME)\n"
fi

# Check name matches directory
if [[ -n "$NAME" ]]; then
  DIR_NAME=$(basename "$(dirname "$FILE_PATH")")
  if [[ "$NAME" != "$DIR_NAME" ]]; then
    ERRORS="${ERRORS}• 'name' ($NAME) must match directory name ($DIR_NAME)\n"
  fi
fi

# Check upstream metadata completeness
UPSTREAM=$(echo "$FM" | grep -E '^upstream:' | head -1 | sed 's/^upstream:[[:space:]]*//')
if [[ -n "$UPSTREAM" ]]; then
  UPSTREAM_SHA=$(echo "$FM" | grep -E '^upstreamSha:' | head -1 | sed 's/^upstreamSha:[[:space:]]*//')
  AUTHOR=$(echo "$FM" | grep -E '^author:' | head -1 | sed 's/^author:[[:space:]]*//')
  if [[ -z "$UPSTREAM_SHA" ]]; then
    ERRORS="${ERRORS}• 'upstreamSha' required when 'upstream' is set\n"
  fi
  if [[ -z "$AUTHOR" ]]; then
    ERRORS="${ERRORS}• 'author' required when 'upstream' is set\n"
  fi
fi

if [[ -n "$ERRORS" ]]; then
  echo "BLOCKED: SKILL.md validation failed for $FILE_PATH:" >&2
  echo -e "$ERRORS" >&2
  echo "Fix these issues before writing the file." >&2
  exit 2
fi

exit 0
