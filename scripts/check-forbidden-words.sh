#!/bin/bash
# check-forbidden-words.sh
# PostToolUse hook: Checks DB-related files for forbidden words after Write/Edit.
# Non-blocking (exit 0) — provides warnings only without interrupting workflow.

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

# Check only DB-related files (entity, model, SQL, migration, DTO, VO, schema)
FILENAME=$(basename "$FILE_PATH")
FILEPATH_LOWER=$(echo "$FILE_PATH" | tr '[:upper:]' '[:lower:]')

IS_DB_FILE=false
case "$FILEPATH_LOWER" in
  *entity*|*model*|*.sql|*migration*|*dto*|*vo*|*schema*|*repository*|*mapper*)
    IS_DB_FILE=true
    ;;
esac

# Check file extension (.sql files are always checked)
case "$FILENAME" in
  *.sql)
    IS_DB_FILE=true
    ;;
esac

if [ "$IS_DB_FILE" = false ]; then
  exit 0
fi

# Determine plugin root path
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PLUGIN_ROOT=$(dirname "$SCRIPT_DIR")
WORDS_FILE="$PLUGIN_ROOT/data/standard_words.json"

if [ ! -f "$WORDS_FILE" ]; then
  exit 0
fi

# Extract words with forbidden word lists and check against file
WARNINGS=""
WARNING_COUNT=0

while IFS=$'\t' read -r standard_word forbidden_words; do
  # Split forbidden words by comma and check each one
  IFS=',' read -ra FORBIDDEN_LIST <<< "$forbidden_words"
  for forbidden in "${FORBIDDEN_LIST[@]}"; do
    # Trim whitespace
    forbidden=$(echo "$forbidden" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    if [ -z "$forbidden" ]; then
      continue
    fi
    # Search for forbidden word in file content (case-insensitive)
    if grep -qi "$forbidden" "$FILE_PATH" 2>/dev/null; then
      WARNINGS="${WARNINGS}[Forbidden] '${forbidden}' found -> Use the standard word (abbreviation '${standard_word}') instead\n"
      WARNING_COUNT=$((WARNING_COUNT + 1))
      if [ $WARNING_COUNT -ge 20 ]; then
        WARNINGS="${WARNINGS}... (there may be additional forbidden words)\n"
        break 2
      fi
    fi
  done
# Rows live under .data[]; Korean field names need jq bracket form (bare .금칙어목록 is a
# jq syntax error). The Korean word-name field is empty in the bundled dataset, so the
# suggestion uses the English abbreviation (the physical column name).
done < <(jq -r '.data[] | select(.["금칙어목록"] != null and .["금칙어목록"] != "") | [.["공통표준단어영문약어명"], .["금칙어목록"]] | @tsv' "$WORDS_FILE" 2>/dev/null)

if [ -n "$WARNINGS" ]; then
  echo -e "[astra-methodology] Forbidden word check results (${FILE_PATH}):"
  echo -e "$WARNINGS"
fi

exit 0
