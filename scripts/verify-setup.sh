#!/bin/bash
# ==========================================================================
# ASTRA Sprint 0: 설정 검증 스크립트
#
# 사용법: ./verify-setup.sh [project-root-path]
#
# 전역 설정과 프로젝트 구조를 검증합니다.
# /astra-checklist 스킬에서 호출하거나 독립 실행할 수 있습니다.
# ==========================================================================

set -euo pipefail

PROJECT_ROOT="${1:-.}"
PASS=0
FAIL=0
TOTAL=0

check() {
    local description="$1"
    local condition="$2"
    TOTAL=$((TOTAL + 1))

    if eval "$condition" > /dev/null 2>&1; then
        echo "  [PASS] ${description}"
        PASS=$((PASS + 1))
    else
        echo "  [FAIL] ${description}"
        FAIL=$((FAIL + 1))
    fi
}

echo "========================================"
echo "  ASTRA Sprint 0 설정 검증"
echo "========================================"
echo ""

# 1. 전역 설정 검증
echo "--- 전역 설정 ---"
check "~/.claude/settings.json 존재" "[ -f ~/.claude/settings.json ]"
check "~/.claude/.mcp.json 존재" "[ -f ~/.claude/.mcp.json ]"
check "Node.js 설치" "command -v node"
check "npx 설치" "command -v npx"
check "Git 설치" "command -v git"
check "GitHub CLI 설치" "command -v gh"
echo ""

# 2. 프로젝트 구조 검증
echo "--- 프로젝트 구조 (${PROJECT_ROOT}) ---"
check "CLAUDE.md" "[ -f '${PROJECT_ROOT}/CLAUDE.md' ]"
check ".claude/ 디렉토리" "[ -d '${PROJECT_ROOT}/.claude' ]"
check "docs/design-system/" "[ -d '${PROJECT_ROOT}/docs/design-system' ]"
check "docs/blueprints/" "[ -d '${PROJECT_ROOT}/docs/blueprints' ]"
check "docs/database/" "[ -d '${PROJECT_ROOT}/docs/database' ]"
check "docs/database/migration/" "[ -d '${PROJECT_ROOT}/docs/database/migration' ]"
check "docs/tests/" "[ -d '${PROJECT_ROOT}/docs/tests' ]"
check "docs/tests/test-cases/" "[ -d '${PROJECT_ROOT}/docs/tests/test-cases' ]"
check "docs/tests/test-reports/" "[ -d '${PROJECT_ROOT}/docs/tests/test-reports' ]"
check "docs/prompts/" "[ -d '${PROJECT_ROOT}/docs/prompts' ]"
check "docs/retrospectives/" "[ -d '${PROJECT_ROOT}/docs/retrospectives' ]"
check "docs/delivery/" "[ -d '${PROJECT_ROOT}/docs/delivery' ]"
check "src/" "[ -d '${PROJECT_ROOT}/src' ]"
echo ""

# 3. 필수 파일 검증
echo "--- 필수 파일 ---"
check "design-tokens.css" "[ -f '${PROJECT_ROOT}/docs/design-system/design-tokens.css' ]"
check "components.md" "[ -f '${PROJECT_ROOT}/docs/design-system/components.md' ]"
check "layout-grid.md" "[ -f '${PROJECT_ROOT}/docs/design-system/layout-grid.md' ]"
check "overview.md" "[ -f '${PROJECT_ROOT}/docs/blueprints/overview.md' ]"
check "database-design.md" "[ -f '${PROJECT_ROOT}/docs/database/database-design.md' ]"
check "naming-rules.md" "[ -f '${PROJECT_ROOT}/docs/database/naming-rules.md' ]"
check "test-strategy.md" "[ -f '${PROJECT_ROOT}/docs/tests/test-strategy.md' ]"
check "sprint-1.md (프롬프트 맵)" "[ -f '${PROJECT_ROOT}/docs/prompts/sprint-1.md' ]"
echo ""

# 4. CLAUDE.md 내용 검증
echo "--- CLAUDE.md 내용 ---"
if [ -f "${PROJECT_ROOT}/CLAUDE.md" ]; then
    check "아키텍처 섹션" "grep -q '아키텍처\|Architecture' '${PROJECT_ROOT}/CLAUDE.md'"
    check "코딩 규칙 섹션" "grep -q '코딩 규칙\|코딩규칙' '${PROJECT_ROOT}/CLAUDE.md'"
    check "디자인 규칙 섹션" "grep -q '디자인 규칙\|디자인규칙' '${PROJECT_ROOT}/CLAUDE.md'"
    check "금지 사항 섹션" "grep -q '금지' '${PROJECT_ROOT}/CLAUDE.md'"
    check "테스트 규칙 섹션" "grep -q '테스트' '${PROJECT_ROOT}/CLAUDE.md'"
    check "커밋 컨벤션 섹션" "grep -q '커밋\|Commit' '${PROJECT_ROOT}/CLAUDE.md'"
    check "DB 설계 문서 참조" "grep -q 'docs/database/database-design' '${PROJECT_ROOT}/CLAUDE.md'"
else
    echo "  [SKIP] CLAUDE.md가 존재하지 않아 내용 검증 불가"
fi
echo ""

# 결과 요약
echo "========================================"
echo "  검증 결과: ${PASS}/${TOTAL} 통과 (${FAIL}건 실패)"
echo "========================================"

if [ $FAIL -eq 0 ]; then
    echo "  Sprint 0 설정이 완료되었습니다!"
    exit 0
else
    echo "  ${FAIL}건의 항목이 미완료 상태입니다."
    echo "  /astra-checklist 로 상세 안내를 확인하세요."
    exit 1
fi
