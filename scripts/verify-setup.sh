#!/bin/bash
# ==========================================================================
# ASTRA Sprint 0: Setup Verification Script
#
# Usage: ./verify-setup.sh [project-root-path]
#
# SINGLE SOURCE OF TRUTH (SSoT) for the mechanical Sprint 0 file/directory
# and CLAUDE.md-section checks. Both the /project-checklist skill and the
# astra-validator agent RUN this script and interpret its output rather than
# restating the required-path list themselves. Content-quality and
# structural-scoring judgments (token completeness, ERD quality, TB_/TC_
# prefix compliance, test-strategy completeness) are intentionally NOT here —
# they live in astra-validator (agent judgment) and the /project-checklist
# skill (inline judgment checks).
#
# Exit code: 0 = all required checks passed, non-zero = at least one failed.
# Optional checks report ⚠️ but never affect the exit code.
# ==========================================================================

set -euo pipefail

PROJECT_ROOT="${1:-.}"
PASS=0
FAIL=0
TOTAL=0

# Required check — counts toward PASS/FAIL and the exit code.
check() {
    local description="$1"
    local condition="$2"
    TOTAL=$((TOTAL + 1))

    if eval "$condition" > /dev/null 2>&1; then
        echo "  ✅ ${description}"
        PASS=$((PASS + 1))
    else
        echo "  ❌ ${description}"
        FAIL=$((FAIL + 1))
    fi
}

# Optional check — reported for visibility only; never affects the exit code.
check_optional() {
    local description="$1"
    local condition="$2"

    if eval "$condition" > /dev/null 2>&1; then
        echo "  ✅ ${description}"
    else
        echo "  ⚠️  ${description} (optional — not found)"
    fi
}

echo "========================================"
echo "  ASTRA Sprint 0 Setup Verification"
echo "========================================"
echo ""

# 1. Global settings verification
echo "--- Global Settings ---"
check "~/.claude/settings.json exists" "[ -f ~/.claude/settings.json ]"
check "~/.claude/.mcp.json exists" "[ -f ~/.claude/.mcp.json ]"
check "Node.js installed" "command -v node"
check "npx installed" "command -v npx"
check "Git installed" "command -v git"
check "GitHub CLI installed" "command -v gh"
check_optional "ego (lite) browser installed (default browser backend, macOS)" \
    "command -v ego-browser"
check_optional "MCP servers configured (chrome-devtools fallback + context7)" \
    "[ -f ~/.claude/.mcp.json ] && grep -q chrome-devtools ~/.claude/.mcp.json && grep -q context7 ~/.claude/.mcp.json"
echo ""

# 2. Project structure verification (directories)
echo "--- Project Structure (${PROJECT_ROOT}) ---"
check ".claude/ directory" "[ -d '${PROJECT_ROOT}/.claude' ]"
check_optional ".claude/settings.json (project-specific settings)" "[ -f '${PROJECT_ROOT}/.claude/settings.json' ]"
check "docs/design-system/" "[ -d '${PROJECT_ROOT}/docs/design-system' ]"
check "docs/blueprints/" "[ -d '${PROJECT_ROOT}/docs/blueprints' ]"
check "docs/database/" "[ -d '${PROJECT_ROOT}/docs/database' ]"
check "docs/database/migration/" "[ -d '${PROJECT_ROOT}/docs/database/migration' ]"
check "docs/tests/" "[ -d '${PROJECT_ROOT}/docs/tests' ]"
check "docs/tests/test-cases/" "[ -d '${PROJECT_ROOT}/docs/tests/test-cases' ]"
check "docs/tests/test-cases/sprint-1/" "[ -d '${PROJECT_ROOT}/docs/tests/test-cases/sprint-1' ]"
check "docs/tests/test-reports/" "[ -d '${PROJECT_ROOT}/docs/tests/test-reports' ]"
check "docs/sprints/" "[ -d '${PROJECT_ROOT}/docs/sprints' ]"
check "docs/delivery/" "[ -d '${PROJECT_ROOT}/docs/delivery' ]"
check "src/" "[ -d '${PROJECT_ROOT}/src' ]"
echo ""

# 3. Required files verification
echo "--- Required Files ---"
check "CLAUDE.md" "[ -f '${PROJECT_ROOT}/CLAUDE.md' ]"
check "design-tokens.css" "[ -f '${PROJECT_ROOT}/src/styles/design-tokens.css' ]"
check "components.md" "[ -f '${PROJECT_ROOT}/docs/design-system/components.md' ]"
check "layout-grid.md" "[ -f '${PROJECT_ROOT}/docs/design-system/layout-grid.md' ]"
check "overview.md" "[ -f '${PROJECT_ROOT}/docs/blueprints/overview.md' ]"
check "database-design.md" "[ -f '${PROJECT_ROOT}/docs/database/database-design.md' ]"
check "naming-rules.md" "[ -f '${PROJECT_ROOT}/docs/database/naming-rules.md' ]"
check "test-strategy.md" "[ -f '${PROJECT_ROOT}/docs/tests/test-strategy.md' ]"
check "sprint-1/prompt-map.md" "[ -f '${PROJECT_ROOT}/docs/sprints/sprint-1/prompt-map.md' ]"
echo ""

# 4. CLAUDE.md content verification
echo "--- CLAUDE.md Content ---"
if [ -f "${PROJECT_ROOT}/CLAUDE.md" ]; then
    check "Architecture section" "grep -q 'Architecture' '${PROJECT_ROOT}/CLAUDE.md'"
    check "Coding rules section" "grep -q 'Coding' '${PROJECT_ROOT}/CLAUDE.md'"
    check "Design rules section" "grep -q 'Design' '${PROJECT_ROOT}/CLAUDE.md'"
    check "Restrictions section" "grep -q 'Restriction\|Forbidden\|Prohibit' '${PROJECT_ROOT}/CLAUDE.md'"
    check "Test rules section" "grep -q 'Test' '${PROJECT_ROOT}/CLAUDE.md'"
    check "Commit convention section" "grep -q 'Commit' '${PROJECT_ROOT}/CLAUDE.md'"
    check "DB design doc reference" "grep -q 'docs/database/database-design' '${PROJECT_ROOT}/CLAUDE.md'"
else
    echo "  [SKIP] CLAUDE.md not found, content verification skipped"
fi
echo ""

# 5. Quality gate verification (hookify rules)
echo "--- Quality Gate ---"
check_optional "hookify rules configured (.claude/hookify.*.local.md)" \
    "find '${PROJECT_ROOT}/.claude' -maxdepth 1 -type f -name 'hookify.*.local.md' 2>/dev/null | grep -q ."
echo ""

# Results summary
echo "========================================"
echo "  Results: ${PASS}/${TOTAL} required checks passed (${FAIL} failed)"
echo "========================================"

if [ "$FAIL" -eq 0 ]; then
    echo "  Sprint 0 setup is complete!"
    exit 0
else
    echo "  ${FAIL} required item(s) are incomplete."
    echo "  Run /project-checklist for detailed guidance."
    exit 1
fi
