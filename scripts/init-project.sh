#!/bin/bash
# ==========================================================================
# ASTRA Sprint 0: 프로젝트 디렉토리 구조 생성 스크립트
#
# 사용법: ./init-project.sh <project-root-path>
#
# /astra-init 스킬에서 호출하거나 독립 실행할 수 있습니다.
# ==========================================================================

set -euo pipefail

PROJECT_ROOT="${1:-.}"

echo "ASTRA Sprint 0: 프로젝트 구조 생성 중..."
echo "대상 경로: ${PROJECT_ROOT}"

# 디렉토리 생성
directories=(
    ".claude"
    "docs/design-system/references"
    "docs/blueprints"
    "docs/prompts"
    "docs/retrospectives"
    "docs/delivery"
    "src"
)

for dir in "${directories[@]}"; do
    target="${PROJECT_ROOT}/${dir}"
    if [ ! -d "$target" ]; then
        mkdir -p "$target"
        echo "  [생성] ${dir}/"
    else
        echo "  [존재] ${dir}/"
    fi
done

# 빈 디렉토리에 .gitkeep 추가
gitkeep_dirs=(
    "docs/design-system/references"
    "docs/retrospectives"
    "docs/delivery"
    "src"
)

for dir in "${gitkeep_dirs[@]}"; do
    gitkeep="${PROJECT_ROOT}/${dir}/.gitkeep"
    if [ ! -f "$gitkeep" ]; then
        touch "$gitkeep"
    fi
done

echo ""
echo "ASTRA 프로젝트 구조 생성 완료!"
echo ""
echo "다음 단계:"
echo "  1. /astra-init 스킬로 템플릿 파일 생성"
echo "  2. 또는 수동으로 CLAUDE.md, 디자인 시스템 파일 작성"
