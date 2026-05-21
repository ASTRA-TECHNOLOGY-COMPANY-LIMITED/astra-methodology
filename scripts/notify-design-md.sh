#!/bin/bash
# notify-design-md.sh
# PostToolUse hook: When UI source files (components, styles) are edited, emit
# a one-time advisory reminding the user to consult docs/design-system/DESIGN.md
# as the SSoT. Non-blocking (exit 0) — warnings only.

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.filePath // empty')

# Exit silently when no file path is present (some tool invocations omit it).
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Resolve absolute path; if file no longer exists, skip silently.
if [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# Locate project root by walking up to the nearest directory containing
# either docs/design-system/ or src/styles/. Fall back to cwd.
PROJECT_ROOT=""
DIR="$(cd "$(dirname "$FILE_PATH")" && pwd)"
while [ "$DIR" != "/" ]; do
  if [ -d "$DIR/docs/design-system" ] || [ -d "$DIR/src/styles" ]; then
    PROJECT_ROOT="$DIR"
    break
  fi
  DIR="$(dirname "$DIR")"
done
[ -z "$PROJECT_ROOT" ] && PROJECT_ROOT="$(pwd)"

# Match UI source files only. The patterns intentionally exclude design system
# documents themselves (DESIGN.md, components.md), the generated token CSS
# (whose header already announces it as generated), and test files.
FILENAME=$(basename "$FILE_PATH")
EXT="${FILENAME##*.}"
PATH_LOWER=$(echo "$FILE_PATH" | tr '[:upper:]' '[:lower:]')

case "$PATH_LOWER" in
  *design-system/design.md|*design-system/components.md|*design-system/layout-grid.md)
    exit 0 ;;
  *src/styles/design-tokens.css|*src/styles/design-tokens.ts)
    exit 0 ;;
  *.test.*|*.spec.*|*__tests__*|*node_modules*|*.next/*|*dist/*|*build/*)
    exit 0 ;;
esac

IS_UI_FILE=false
case "$EXT" in
  tsx|jsx|vue|svelte|css|scss|sass|less|html)
    IS_UI_FILE=true ;;
esac
case "$PATH_LOWER" in
  *src/components/*|*src/pages/*|*src/app/*|*components/*|*styles/*)
    IS_UI_FILE=true ;;
esac

[ "$IS_UI_FILE" = false ] && exit 0

# Skip if DESIGN.md does not exist yet — first-time users see the suggestion
# from /project-init instead of getting nagged on every edit.
DESIGN_MD="$PROJECT_ROOT/docs/design-system/DESIGN.md"
if [ ! -f "$DESIGN_MD" ]; then
  exit 0
fi

# Throttle: only emit once per session. Use a marker file under .claude/
# scoped to the project root.
MARKER_DIR="$PROJECT_ROOT/.claude/.astra-hooks"
MARKER_FILE="$MARKER_DIR/notify-design-md.session"
mkdir -p "$MARKER_DIR" 2>/dev/null || exit 0

# Marker is valid for 1 hour to avoid spamming long sessions.
if [ -f "$MARKER_FILE" ]; then
  if [ "$(find "$MARKER_FILE" -mmin -60 2>/dev/null | wc -l | tr -d ' ')" -gt 0 ]; then
    exit 0
  fi
fi
touch "$MARKER_FILE"

# Emit non-blocking advisory.
cat <<MSG
[ASTRA] UI code edited. Refer to the design system SSoT:
  • docs/design-system/DESIGN.md (Front Matter tokens + Body §4 component guidelines)
  • Token violation check:  /design-audit $FILE_PATH
  • Token change needed:    /design-init (edit DESIGN.md, then --regenerate-css)
MSG

exit 0
