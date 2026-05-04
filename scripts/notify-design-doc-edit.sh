#!/bin/bash
# notify-design-doc-edit.sh
# PostToolUse hook: Notifies when blueprint or DB design documents are modified,
# prompting VA review before code reflection.
# Non-blocking (exit 0) — provides notification only.

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.filePath // empty')

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Match: docs/database/database-design.md OR docs/blueprints/{NNN}-{slug}/*.md
if echo "$FILE_PATH" | grep -qE '(database-design\.md|blueprints/[0-9]{3}-.*/.*\.md)$'; then
  echo '[ASTRA] 설계 문서가 수정되었습니다. VA 검토 후 코드 반영을 진행하세요.'
fi

exit 0
