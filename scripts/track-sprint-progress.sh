#!/bin/bash
# track-sprint-progress.sh
# PostToolUse hook: Detects sprint-related file events and appends to sprint progress activity log.
# Non-blocking (exit 0) — provides progress tracking messages only.

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.filePath // empty')

# Exit if no file path provided
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Exit if file does not exist
if [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# Skip self-referential writes to prevent loops
BASENAME=$(basename "$FILE_PATH")
if echo "$BASENAME" | grep -qE '^sprint-[0-9]+-progress\.md$'; then
  exit 0
fi

# Detect event type by file path
EVENT=""
DETAIL=""

case "$FILE_PATH" in
  */docs/blueprints/*.md)
    # Skip overview.md
    if [ "$BASENAME" = "overview.md" ]; then
      exit 0
    fi
    EVENT="blueprint"
    DETAIL=$(echo "$BASENAME" | sed 's/\.md$//')
    ;;
  */docs/tests/test-reports/*.md)
    EVENT="test_report"
    DETAIL=$(echo "$BASENAME" | sed 's/\.md$//')
    ;;
  */docs/tests/test-cases/*.md)
    EVENT="test_case"
    DETAIL=$(echo "$BASENAME" | sed 's/\.md$//')
    ;;
  */docs/database/database-design.md)
    EVENT="db_design"
    DETAIL="database-design"
    ;;
  */src/*.java|*/src/*.ts|*/src/*.tsx|*/src/*.py|*/src/*.js|*/src/*.jsx|*/src/*.kt|*/src/*.go|*/src/*.rs)
    EVENT="implementation"
    DETAIL=$(echo "$BASENAME" | sed 's/\.[^.]*$//')
    ;;
esac

# Exit if no matching event
if [ -z "$EVENT" ]; then
  exit 0
fi

# Find project root (walk up looking for CLAUDE.md)
PROJECT_ROOT=""
CHECK_DIR=$(dirname "$FILE_PATH")
while [ "$CHECK_DIR" != "/" ] && [ "$CHECK_DIR" != "." ]; do
  if [ -f "$CHECK_DIR/CLAUDE.md" ]; then
    PROJECT_ROOT="$CHECK_DIR"
    break
  fi
  CHECK_DIR=$(dirname "$CHECK_DIR")
done

if [ -z "$PROJECT_ROOT" ]; then
  exit 0
fi

PROMPTS_DIR="$PROJECT_ROOT/docs/prompts"

# Exit if prompts directory doesn't exist
if [ ! -d "$PROMPTS_DIR" ]; then
  exit 0
fi

# Detect current sprint number (highest sprint-{N}.md in docs/prompts/)
SPRINT_NUM=""
for f in "$PROMPTS_DIR"/sprint-*.md; do
  [ -f "$f" ] || continue
  NUM=$(basename "$f" | sed -n 's/^sprint-\([0-9]*\)\.md$/\1/p')
  if [ -n "$NUM" ]; then
    if [ -z "$SPRINT_NUM" ] || [ "$NUM" -gt "$SPRINT_NUM" ]; then
      SPRINT_NUM="$NUM"
    fi
  fi
done

if [ -z "$SPRINT_NUM" ]; then
  exit 0
fi

TRACKER_FILE="$PROMPTS_DIR/sprint-${SPRINT_NUM}-progress.md"

# If tracker file exists, append activity log entry
if [ -f "$TRACKER_FILE" ]; then
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
  REL_PATH=$(echo "$FILE_PATH" | sed "s|^$PROJECT_ROOT/||")
  LOG_ENTRY="| $TIMESTAMP | $EVENT | $REL_PATH | $DETAIL |"

  # Insert before <!-- ACTIVITY_LOG_END --> marker using temp file (awk for macOS/Linux portability)
  if grep -q '<!-- ACTIVITY_LOG_END -->' "$TRACKER_FILE"; then
    TMPFILE=$(mktemp)
    awk -v entry="$LOG_ENTRY" '/<!-- ACTIVITY_LOG_END -->/ { print entry } { print }' \
      "$TRACKER_FILE" > "$TMPFILE" && mv "$TMPFILE" "$TRACKER_FILE"
  fi
fi

# Output message for the LLM
echo "[ASTRA] Sprint progress: ${EVENT} detected for '${DETAIL}'. Update the progress table in sprint-${SPRINT_NUM}-progress.md."

exit 0
