#!/bin/bash
# ==========================================================================
# ASTRA Sprint 0: Project Directory Structure Generation Script
#
# Usage: ./init-project.sh <project-root-path>
#
# Can be invoked from the /astra-methodology skill or run independently.
# ==========================================================================

set -euo pipefail

PROJECT_ROOT="${1:-.}"

echo "ASTRA Sprint 0: Generating project structure..."
echo "Target path: ${PROJECT_ROOT}"

# Create directories
directories=(
    ".claude"
    "docs/design-system/references"
    "docs/blueprints"
    "docs/database/migration"
    "docs/tests/test-cases"
    "docs/tests/test-reports"
    "docs/sprints"
    "docs/delivery"
    "src"
)

for dir in "${directories[@]}"; do
    target="${PROJECT_ROOT}/${dir}"
    if [ ! -d "$target" ]; then
        mkdir -p "$target"
        echo "  [Created] ${dir}/"
    else
        echo "  [Exists]  ${dir}/"
    fi
done

# Add .gitkeep to empty directories
gitkeep_dirs=(
    "docs/design-system/references"
    "docs/database/migration"
    "docs/tests/test-cases"
    "docs/tests/test-reports"
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
echo "ASTRA project structure generation complete!"
echo ""
echo "Next steps:"
echo "  1. Generate template files with the /astra-methodology skill"
echo "  2. Or manually create CLAUDE.md and design system files"
