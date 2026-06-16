#!/bin/bash
# Butler: Daily Session Summary
# Scans ~/.easycode-user/tmp/ for today's session activity
# Output: structured JSON report for AI to summarize

TODAY=$(date +%Y-%m-%d)
BASE_DIR="$HOME/.easycode-user/tmp"

echo "=== Butler Daily Report ==="
echo "Date: $TODAY"
echo "---"

if [ ! -d "$BASE_DIR" ]; then
  echo "ERROR: No session data found at $BASE_DIR"
  exit 1
fi

for WORKSPACE in "$BASE_DIR"/*/; do
  WS_ID=$(basename "$WORKSPACE")
  SESSION_DIR="$WORKSPACE/sessions"
  [ ! -d "$SESSION_DIR" ] && continue

  for SESSION in "$SESSION_DIR"/feishu-oc_* "$SESSION_DIR"/session-*/; do
    META="$SESSION/metadata.json"
    [ ! -f "$META" ] && continue

    # Parse metadata
    TITLE=$(python3 -c "import json; d=json.load(open('$META')); print(d.get('title',''))" 2>/dev/null)
    MODEL=$(python3 -c "import json; d=json.load(open('$META')); print(d.get('model',''))" 2>/dev/null)
    MSG_COUNT=$(python3 -c "import json; d=json.load(open('$META')); print(d.get('messageCount',0))" 2>/dev/null)
    TOKENS=$(python3 -c "import json; d=json.load(open('$META')); print(d.get('totalTokens',0))" 2>/dev/null)
    CREATED=$(python3 -c "import json; d=json.load(open('$META')); print(d.get('createdAt',''))" 2>/dev/null)
    LAST=$(python3 -c "import json; d=json.load(open('$META')); print(d.get('lastActiveAt',''))" 2>/dev/null)
    FIRST_MSG=$(python3 -c "import json; d=json.load(open('$META')); print(d.get('firstUserMessage','')[:80])" 2>/dev/null)

    # Check if session was active today
    if [[ "$LAST" == "$TODAY"* ]]; then
      echo "[workspace: $WS_ID]"
      echo "  session: $(basename "$SESSION")"
      echo "  title: $TITLE"
      echo "  model: $MODEL"
      echo "  messages: $MSG_COUNT"
      echo "  tokens: $TOKENS"
      echo "  created: $CREATED"
      echo "  last: $LAST"
      echo "  first: $FIRST_MSG"
      echo "---"
    fi
  done
done
