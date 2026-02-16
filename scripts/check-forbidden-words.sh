#!/bin/bash
# check-forbidden-words.sh
# PostToolUse 훅: Write/Edit 후 DB 관련 파일에서 금칙어를 검사한다.
# 비블로킹(exit 0) — 경고만 제공하고 작업 흐름을 중단하지 않는다.

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.filePath // empty')

# 파일 경로가 없으면 종료
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# 파일이 존재하지 않으면 종료
if [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# DB 관련 파일만 검사 (엔티티, 모델, SQL, 마이그레이션, DTO, VO, 스키마)
FILENAME=$(basename "$FILE_PATH")
FILEPATH_LOWER=$(echo "$FILE_PATH" | tr '[:upper:]' '[:lower:]')

IS_DB_FILE=false
case "$FILEPATH_LOWER" in
  *entity*|*model*|*.sql|*migration*|*dto*|*vo*|*schema*|*repository*|*mapper*)
    IS_DB_FILE=true
    ;;
esac

# 파일 확장자 체크 (.sql 파일은 무조건 검사)
case "$FILENAME" in
  *.sql)
    IS_DB_FILE=true
    ;;
esac

if [ "$IS_DB_FILE" = false ]; then
  exit 0
fi

# 플러그인 루트 경로 결정
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PLUGIN_ROOT=$(dirname "$SCRIPT_DIR")
WORDS_FILE="$PLUGIN_ROOT/data/standard_words.json"

if [ ! -f "$WORDS_FILE" ]; then
  exit 0
fi

# 금칙어 목록이 있는 단어를 추출하여 검사
WARNINGS=""
WARNING_COUNT=0

while IFS=$'\t' read -r standard_word forbidden_words; do
  # 금칙어를 쉼표로 분리하여 각각 검사
  IFS=',' read -ra FORBIDDEN_LIST <<< "$forbidden_words"
  for forbidden in "${FORBIDDEN_LIST[@]}"; do
    # 공백 제거
    forbidden=$(echo "$forbidden" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    if [ -z "$forbidden" ]; then
      continue
    fi
    # 파일 내용에서 금칙어 검색 (대소문자 무시)
    if grep -qi "$forbidden" "$FILE_PATH" 2>/dev/null; then
      WARNINGS="${WARNINGS}[금칙어] '${forbidden}' 발견 → 표준어 '${standard_word}' 사용 권장\n"
      WARNING_COUNT=$((WARNING_COUNT + 1))
      if [ $WARNING_COUNT -ge 20 ]; then
        WARNINGS="${WARNINGS}... (추가 금칙어가 있을 수 있습니다)\n"
        break 2
      fi
    fi
  done
done < <(jq -r '.[] | select(.금칙어목록 != null and .금칙어목록 != "") | [.공통표준단어명, .금칙어목록] | @tsv' "$WORDS_FILE" 2>/dev/null)

if [ -n "$WARNINGS" ]; then
  echo -e "[astra-init] 금칙어 검사 결과 (${FILE_PATH}):"
  echo -e "$WARNINGS"
fi

exit 0
