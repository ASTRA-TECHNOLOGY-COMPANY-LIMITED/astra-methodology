#!/bin/bash
# validate-naming.sh
# PostToolUse 훅: Write/Edit 후 DB 관련 파일의 네이밍 규칙을 검사한다.
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

# DB 관련 파일만 검사
FILEPATH_LOWER=$(echo "$FILE_PATH" | tr '[:upper:]' '[:lower:]')
FILENAME=$(basename "$FILE_PATH")

IS_DB_FILE=false
case "$FILEPATH_LOWER" in
  *entity*|*model*|*.sql|*migration*|*schema*|*dto*|*vo*|*mapper*)
    IS_DB_FILE=true
    ;;
esac

case "$FILENAME" in
  *.sql)
    IS_DB_FILE=true
    ;;
esac

if [ "$IS_DB_FILE" = false ]; then
  exit 0
fi

WARNINGS=""
WARNING_COUNT=0

# === SQL 파일 검사 ===
if [[ "$FILENAME" == *.sql ]]; then

  # 1. CREATE TABLE 문에서 테이블명 접두사 검사
  while IFS= read -r table_name; do
    # 공백 제거
    table_name=$(echo "$table_name" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    if [ -z "$table_name" ]; then
      continue
    fi
    # TB_, TC_, TH_, TL_, TR_ 접두사 확인
    if ! echo "$table_name" | grep -qE '^(TB_|TC_|TH_|TL_|TR_)'; then
      WARNINGS="${WARNINGS}[테이블명] '${table_name}': 표준 접두사(TB_/TC_/TH_/TL_/TR_) 누락\n"
      WARNING_COUNT=$((WARNING_COUNT + 1))
    fi
  done < <(grep -ioE 'CREATE[[:space:]]+TABLE[[:space:]]+(IF[[:space:]]+NOT[[:space:]]+EXISTS[[:space:]]+)?[A-Za-z_][A-Za-z0-9_]*' "$FILE_PATH" 2>/dev/null | sed -E 's/CREATE[[:space:]]+TABLE[[:space:]]+(IF[[:space:]]+NOT[[:space:]]+EXISTS[[:space:]]+)?//i')

  # 2. 소문자 테이블/컬럼명 검사 (혼용 경고)
  if grep -qE 'CREATE[[:space:]]+TABLE' "$FILE_PATH" 2>/dev/null; then
    if grep -qE '[a-z]{3,}_[a-z]' "$FILE_PATH" 2>/dev/null; then
      # 소문자 snake_case가 있으면 대문자 표준을 안내
      HAS_LOWERCASE=$(grep -cE 'CREATE[[:space:]]+TABLE[[:space:]]+[a-z]' "$FILE_PATH" 2>/dev/null || echo "0")
      if [ "$HAS_LOWERCASE" -gt 0 ]; then
        WARNINGS="${WARNINGS}[네이밍] SQL 내 소문자 테이블명 발견. 표준은 대문자(TB_CSTMR)를 사용합니다\n"
        WARNING_COUNT=$((WARNING_COUNT + 1))
      fi
    fi
  fi
fi

# === Java 엔티티 파일 검사 ===
if [[ "$FILENAME" == *.java ]]; then

  # @Table 어노테이션에서 테이블명 접두사 검사
  while IFS= read -r table_name; do
    table_name=$(echo "$table_name" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | tr -d '"')
    if [ -z "$table_name" ]; then
      continue
    fi
    if ! echo "$table_name" | grep -qE '^(TB_|TC_|TH_|TL_|TR_)'; then
      WARNINGS="${WARNINGS}[테이블명] @Table(name=\"${table_name}\"): 표준 접두사(TB_/TC_/TH_/TL_/TR_) 누락\n"
      WARNING_COUNT=$((WARNING_COUNT + 1))
    fi
  done < <(grep -oE '@Table\s*\(\s*name\s*=\s*"[^"]*"' "$FILE_PATH" 2>/dev/null | sed -E 's/@Table\s*\(\s*name\s*=\s*"([^"]*)"/\1/')

fi

# === TypeScript 파일 검사 (TypeORM/Prisma) ===
if [[ "$FILENAME" == *.ts || "$FILENAME" == *.tsx ]]; then

  # @Entity() 데코레이터에서 테이블명 검사
  while IFS= read -r table_name; do
    table_name=$(echo "$table_name" | sed "s/^[[:space:]]*//;s/[[:space:]]*$//" | tr -d "'" | tr -d '"')
    if [ -z "$table_name" ]; then
      continue
    fi
    if ! echo "$table_name" | grep -qE '^(TB_|TC_|TH_|TL_|TR_)'; then
      WARNINGS="${WARNINGS}[테이블명] @Entity('${table_name}'): 표준 접두사(TB_/TC_/TH_/TL_/TR_) 누락\n"
      WARNING_COUNT=$((WARNING_COUNT + 1))
    fi
  done < <(grep -oE "@Entity\s*\(\s*['\"][^'\"]*['\"]" "$FILE_PATH" 2>/dev/null | sed -E "s/@Entity\s*\(\s*['\"]([^'\"]*)['\"/\1/")

fi

# === Python 파일 검사 (SQLAlchemy/Django) ===
if [[ "$FILENAME" == *.py ]]; then

  # __tablename__ 에서 테이블명 검사
  while IFS= read -r table_name; do
    table_name=$(echo "$table_name" | sed "s/^[[:space:]]*//;s/[[:space:]]*$//" | tr -d "'" | tr -d '"')
    if [ -z "$table_name" ]; then
      continue
    fi
    if ! echo "$table_name" | grep -qE '^(TB_|TC_|TH_|TL_|TR_)'; then
      WARNINGS="${WARNINGS}[테이블명] __tablename__='${table_name}': 표준 접두사(TB_/TC_/TH_/TL_/TR_) 누락\n"
      WARNING_COUNT=$((WARNING_COUNT + 1))
    fi
  done < <(grep -oE "__tablename__\s*=\s*['\"][^'\"]*['\"]" "$FILE_PATH" 2>/dev/null | sed -E "s/__tablename__\s*=\s*['\"]([^'\"]*)['\"/\1/")

fi

if [ -n "$WARNINGS" ]; then
  echo -e "[astra-init] 네이밍 규칙 검사 결과 (${FILE_PATH}):"
  echo -e "$WARNINGS"
fi

exit 0
