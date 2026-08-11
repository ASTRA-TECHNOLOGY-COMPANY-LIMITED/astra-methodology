#!/bin/bash
# posttooluse-dispatch.sh
# Single PostToolUse dispatcher: reads the tool-input JSON from stdin once and
# fans out to every per-check script sequentially. Replaces five separate hook
# entries in hooks.json so the harness spawns one hook process per Write/Edit
# instead of five, and adds a shared fast path (no file_path -> exit before any
# child script or additional jq spawn).
# Each child script keeps its own stdin-JSON contract, so all scripts remain
# independently invokable (see CLAUDE.md "Scripts").
# Non-blocking (exit 0) — same guarantee as every ASTRA hook script.

INPUT=$(cat)
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# Shared fast path: nothing to check when the tool input carries no file path.
FILE_PATH=$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // .tool_input.filePath // empty' 2>/dev/null)
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

for script in \
  notify-design-doc-edit.sh \
  check-forbidden-words.sh \
  validate-naming.sh \
  track-sprint-progress.sh \
  notify-design-md.sh \
  check-korean-style.sh; do
  if [ -f "$SCRIPT_DIR/$script" ]; then
    printf '%s' "$INPUT" | bash "$SCRIPT_DIR/$script"
  fi
done

exit 0
