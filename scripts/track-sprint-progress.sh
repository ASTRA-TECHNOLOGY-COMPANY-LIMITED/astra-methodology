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
if [ "$BASENAME" = "progress.md" ] && echo "$FILE_PATH" | grep -q '/docs/sprints/sprint-[0-9]*-[^/]*/'; then
  exit 0
fi

# Detect event type by file path
EVENT=""
DETAIL=""
SPRINT_FROM_PATH=""

case "$FILE_PATH" in
  */docs/blueprints/overview.md)
    # Skip overview.md (project-level document, not a feature blueprint)
    exit 0
    ;;
  */docs/blueprints/[0-9][0-9][0-9]-*/*)
    # Numbered blueprint directory: extract feature name from directory (strip NNN- prefix)
    EVENT="blueprint"
    BLUEPRINT_DIR=$(echo "$FILE_PATH" | sed -n 's|.*/docs/blueprints/\([^/]*\)/.*|\1|p')
    DETAIL=$(echo "$BLUEPRINT_DIR" | sed 's/^[0-9]*-//')
    ;;
  */docs/tests/test-reports/*.md)
    EVENT="test_report"
    DETAIL=$(echo "$BASENAME" | sed 's/\.md$//')
    ;;
  */docs/tests/test-cases/sprint-*/*.md)
    EVENT="test_case"
    DETAIL=$(echo "$BASENAME" | sed 's/\.md$//')
    # Extract sprint number from the file path for accurate attribution
    SPRINT_FROM_PATH=$(echo "$FILE_PATH" | sed -n 's|.*/test-cases/sprint-\([0-9]*\)/.*|\1|p')
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

SPRINTS_DIR="$PROJECT_ROOT/docs/sprints"

# Exit if sprints directory doesn't exist
if [ ! -d "$SPRINTS_DIR" ]; then
  exit 0
fi

# Detect current sprint number and directory (highest sprint-{N}-{name} directory in docs/sprints/)
SPRINT_NUM=""
SPRINT_DIR=""
for d in "$SPRINTS_DIR"/sprint-*-*/; do
  [ -d "$d" ] || continue
  NUM=$(basename "$d" | sed -n 's/^sprint-\([0-9]*\)-.*$/\1/p')
  if [ -n "$NUM" ]; then
    if [ -z "$SPRINT_NUM" ] || [ "$NUM" -gt "$SPRINT_NUM" ]; then
      SPRINT_NUM="$NUM"
      SPRINT_DIR="$d"
    fi
  fi
done

if [ -z "$SPRINT_NUM" ]; then
  exit 0
fi

# For test_case events, use sprint number from file path instead of latest sprint
if [ -n "$SPRINT_FROM_PATH" ]; then
  # Find sprint directory matching the number from test case path
  FOUND_DIR=""
  for d in "$SPRINTS_DIR"/sprint-${SPRINT_FROM_PATH}-*/; do
    [ -d "$d" ] && FOUND_DIR="$d" && break
  done
  if [ -n "$FOUND_DIR" ]; then
    SPRINT_NUM="$SPRINT_FROM_PATH"
    SPRINT_DIR="$FOUND_DIR"
  else
    echo "[ASTRA] Warning: test case file is under sprint-${SPRINT_FROM_PATH} but no docs/sprints/sprint-${SPRINT_FROM_PATH}-*/ directory exists. Progress will be logged to sprint-${SPRINT_NUM} tracker. Run /sprint-init to initialize the sprint."
  fi
fi

# Use detected SPRINT_DIR to find tracker file
TRACKER_FILE="${SPRINT_DIR%/}/progress.md"

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
SPRINT_DIR_NAME=$(basename "${SPRINT_DIR%/}")
echo "[ASTRA] Sprint progress: ${EVENT} detected for '${DETAIL}'. Update the progress table in docs/sprints/${SPRINT_DIR_NAME}/progress.md."

exit 0
