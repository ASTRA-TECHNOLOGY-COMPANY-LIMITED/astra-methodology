#!/bin/bash
# check-korean-style.sh
# PostToolUse hook: runs the Korean style gate (scripts/check-style.py) on
# Korean-bearing files after Write/Edit. Advisory only — echoes findings as
# warnings and always exits 0 (same non-blocking guarantee as every ASTRA hook).
#
# Surface mapping: *.md -> doc, source-code comment lines -> comment.
# Conversation-only surfaces (answer / hitl / report) never hit the filesystem,
# so they are covered by the rules in docs/development/korean-style.md instead.
# Plugin-internal files are out of gate scope (instructional prose needs
# contrast/emphasis structures the gate would fight), so anything inside the
# plugin root is skipped wholesale.

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.filePath // empty')

# Exit if no file path provided or file does not exist
if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PLUGIN_ROOT_DIR=$(dirname "$SCRIPT_DIR")
CS="$SCRIPT_DIR/check-style.py"
if [ ! -f "$CS" ]; then
  exit 0
fi

# Out-of-scope paths: the plugin's own files, generated artifacts, data, caches.
case "$FILE_PATH" in
  "$PLUGIN_ROOT_DIR"/*) exit 0 ;;
  */.claude/*|*/node_modules/*) exit 0 ;;
  */design-tokens.css|*.json|*.lock|*.svg) exit 0 ;;
esac

# Korean-only gate: nothing to check when the file has no Hangul.
grep -q -m1 '[가-힣]' "$FILE_PATH" 2>/dev/null || exit 0

# Surface by file type. Unknown types are out of scope.
EXT="${FILE_PATH##*.}"
case "$EXT" in
  md|markdown)
    SURFACE="doc"
    ;;
  ts|tsx|js|jsx|mjs|py|java|kt|kts|swift|dart|go|rb|css|scss|sh|sql)
    SURFACE="comment"
    ;;
  *)
    exit 0
    ;;
esac

# Self-test guard first: a checker whose rules are broken (missing file, regex
# that dies at import, corrupted fixtures) must not render verdicts. ast-level
# syntax checks cannot catch these — only the built-in fixtures can.
if ! python3 "$CS" --selftest >/dev/null 2>&1; then
  echo "[korean-style] check-style.py selftest failed or python3 unavailable — style gate unverified, skipped"
  exit 0
fi

if [ "$SURFACE" = "doc" ]; then
  OUT=$(python3 "$CS" --surface doc "$FILE_PATH" 2>/dev/null)
  RC=$?
else
  # Feed only Korean-bearing comment-ish lines; Korean inside string literals
  # (log/UI text) is runtime data, not prose, and fixing it changes behavior.
  LINES=$(grep -E '(//|#|/\*|^[[:space:]]*\*|<!--|^[[:space:]]*--)' "$FILE_PATH" 2>/dev/null | grep '[가-힣]' 2>/dev/null)
  if [ -z "$LINES" ]; then
    exit 0
  fi
  OUT=$(printf '%s\n' "$LINES" | python3 "$CS" --surface comment - 2>/dev/null)
  RC=$?
fi

# Measured failure mode: exit 1 with empty stdout means the checker died, not a
# style warning. Report as unverified instead of pretending it passed.
if [ "$RC" -eq 1 ] && [ -z "$OUT" ]; then
  echo "[korean-style] checker returned rc=1 with no output — unverified, skipped"
  exit 0
fi

if [ "$RC" -eq 1 ] || [ "$RC" -eq 2 ]; then
  echo "⚠️  [korean-style] $(basename "$FILE_PATH") ($SURFACE) — Korean style findings, advisory only:"
  printf '%s\n' "$OUT" | head -20
  echo "   rules: \$CLAUDE_PLUGIN_ROOT/docs/development/korean-style.md (nothing is blocked)"
fi

exit 0
