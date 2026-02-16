---
name: project-checklist
description: "Verifies the ASTRA Sprint 0 completion checklist. Checks required files, settings, and quality gate configurations."
allowed-tools: Read, Bash, Glob, Grep
---

# ASTRA Sprint 0 Completion Checklist Verification

Verifies that the ASTRA Sprint 0 setup for the current project has been correctly completed.

## Verification Items

### A. Project Structure Verification

Checks the existence of the following files/directories:

| Path | Required | Description |
|------|----------|-------------|
| `CLAUDE.md` | Required | Project AI rules |
| `.claude/settings.json` | Optional | Project-specific settings |
| `docs/design-system/design-tokens.css` | Required | Design tokens |
| `docs/design-system/components.md` | Required | Component guide |
| `docs/design-system/layout-grid.md` | Required | Layout grid |
| `docs/blueprints/overview.md` | Required | Project overview |
| `docs/database/database-design.md` | Required | Central DB design document |
| `docs/database/naming-rules.md` | Required | DB naming rules |
| `docs/tests/test-strategy.md` | Required | Test strategy document |
| `docs/prompts/sprint-1.md` | Required | First sprint prompt map |

### B. CLAUDE.md Content Verification

Checks whether CLAUDE.md contains the following sections:

- [ ] Architecture (backend, frontend, DB)
- [ ] Coding rules
- [ ] Design rules
- [ ] Prohibited practices
- [ ] Testing rules
- [ ] Commit convention
- [ ] Design document rules

### C. Design System Verification

Checks whether the following tokens are defined in `docs/design-system/design-tokens.css`:

- [ ] Color tokens (`--color-*`)
- [ ] Typography tokens (`--font-size-*`, `--font-weight-*`)
- [ ] Spacing tokens (`--spacing-*`)
- [ ] Responsive breakpoints

### D. DB Design Document Verification

Checks whether `docs/database/database-design.md` contains the following sections:

- [ ] Full ERD section
- [ ] Common rules (table prefixes, audit columns, naming)
- [ ] Module-specific table sections
- [ ] FK relationship summary section

Checks whether `docs/database/naming-rules.md` contains the following:

- [ ] Table prefix rules
- [ ] Column naming rules
- [ ] Standard terminology dictionary integration method

### E. Test Strategy Document Verification

Checks whether `docs/tests/test-strategy.md` contains the following sections:

- [ ] Test level definitions (unit/integration/E2E)
- [ ] Test coverage goals
- [ ] Test naming conventions
- [ ] Test data management strategy

### F. Global Settings Verification

- [ ] Agent Teams environment variable in `~/.claude/settings.json`
- [ ] 3 MCP servers in `~/.claude/.mcp.json` (chrome-devtools, postgres, context7)

### G. Quality Gate Verification

Checks whether hookify rules are configured:
- Existence of `hookify.*.local.md` files in the `.claude/` directory

### H. Sprint Progress Tracking Verification

Checks whether sprint progress tracking is configured:

| Path | Required | Description |
|------|----------|-------------|
| `docs/prompts/sprint-1-progress.md` | Optional | Sprint 1 progress tracker |

If `docs/prompts/sprint-1-progress.md` exists, verify it contains:
- [ ] Progress table section (`<!-- PROGRESS_TABLE_START -->` ... `<!-- PROGRESS_TABLE_END -->`)
- [ ] Activity log section (`<!-- ACTIVITY_LOG_START -->` ... `<!-- ACTIVITY_LOG_END -->`)
- [ ] Summary section (`<!-- SUMMARY_START -->` ... `<!-- SUMMARY_END -->`)

## Result Output

Outputs verification results in the following format:

```
## ASTRA Sprint 0 Checklist Verification Results

### Score: {passed}/{total} ({percent}%)

### Passed Items
- [x] {item name}

### Failed Items
- [ ] {item name} - {resolution method}

### Recommended Actions
1. {specific action items}
```

## Notes

- This skill is read-only. It does not modify files.
- Clearly marks each item as passed/failed.
- Provides specific resolution methods for failed items.
