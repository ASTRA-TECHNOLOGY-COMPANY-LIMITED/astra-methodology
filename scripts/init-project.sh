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
    "docs/planner"
    "docs/database/migration"
    "docs/tests/test-cases/sprint-1"
    "docs/tests/test-reports"
    "docs/sprints"
    "docs/delivery"
    "src/styles"
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
    "docs/planner"
    "docs/database/migration"
    "docs/tests/test-cases/sprint-1"
    "docs/tests/test-reports"
    "docs/delivery"
    "src/styles"
)

for dir in "${gitkeep_dirs[@]}"; do
    gitkeep="${PROJECT_ROOT}/${dir}/.gitkeep"
    if [ ! -f "$gitkeep" ]; then
        touch "$gitkeep"
    fi
done

# Register ASTRA worktree directory in .gitignore (idempotent).
# Isolated work branches (feat/*, fix/*, etc.) are checked out under
# .astra-worktrees/<slug>/ by /pr-merge — these are ephemeral and must
# never be committed back into the repo they belong to.
gitignore="${PROJECT_ROOT}/.gitignore"
worktree_pattern=".astra-worktrees/"
if [ -f "$gitignore" ]; then
    if ! grep -Fxq "$worktree_pattern" "$gitignore"; then
        printf '\n# ASTRA isolated worktrees (managed by /pr-merge)\n%s\n' "$worktree_pattern" >> "$gitignore"
        echo "  [Updated] .gitignore (+ .astra-worktrees/)"
    fi
else
    printf '# ASTRA isolated worktrees (managed by /pr-merge)\n%s\n' "$worktree_pattern" > "$gitignore"
    echo "  [Created] .gitignore"
fi

echo ""
echo "ASTRA project structure generation complete!"
echo ""
echo "Next steps:"
echo "  1. Generate template files with the /astra-methodology skill"
echo "  2. Or manually create CLAUDE.md and design system files"
echo "  3. Initialize the design system SSoT: /design-init --auto"
echo "     (Creates docs/design-system/DESIGN.md and regenerates src/styles/design-tokens.css)"
