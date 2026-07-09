---
name: project-checklist
description: "Verifies the ASTRA Sprint 0 completion checklist. Runs the mechanical verify-setup.sh SSoT for file/setting existence, then layers judgment-based content checks and delegates structural scoring to the astra-validator agent."
argument-hint: "[project-root-path] (optional — defaults to current working directory)"
allowed-tools: Read, Bash, Glob, Grep, Task, Agent
---

# ASTRA Sprint 0 Completion Checklist Verification

Verifies that the ASTRA Sprint 0 setup for the current project has been correctly completed.

Verification is split into three layers so the same required-path list is never restated in more than one place:

1. **Mechanical checks** — delegated to `scripts/verify-setup.sh` (the SSoT for file/directory/setting existence and CLAUDE.md section presence). This skill runs it and parses its output; it does **not** re-list the required files in prose.
2. **Judgment-based content checks** — kept inline below (things a script cannot reliably verify: token completeness, ERD/section quality, test-strategy completeness, progress-tracker markers).
3. **Structural scoring** — delegated to the `astra-validator` agent for a scored compliance report.

## Step 1: Run the Mechanical SSoT

Resolve the plugin root, then run `verify-setup.sh` against the target project root (`$ARGUMENTS`, defaulting to the current working directory):

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(find ~/.claude/plugins/cache -maxdepth 3 -type d -path '*/astra-methodology/*' 2>/dev/null | sort -V | tail -1)}"
PROJECT_ROOT="${ARGUMENTS:-.}"
bash "$PLUGIN_ROOT/scripts/verify-setup.sh" "$PROJECT_ROOT"
```

Parse the script's stdout:
- Each line is `✅ <item>` (passed), `❌ <item>` (failed required item), or `⚠️ <item>` (optional item not found).
- The final `Results: {passed}/{total}` line and the exit code (0 = all required passed, non-zero = at least one failed) are the mechanical verdict.

Do **not** restate the file/directory list — the script owns it. Report the `❌` lines as the failed mechanical items with their resolution (create the missing file/directory).

## Step 2: Judgment-Based Content Checks (inline)

These require reading file *contents* and applying judgment; the script does not attempt them. Perform them only for files that Step 1 confirmed exist.

### A. Design System Completeness

Read `src/styles/design-tokens.css` (or the framework-specific token file) and confirm it defines a usable token set:

- [ ] Color tokens (primitive + semantic; token names vary by generator — OKLCH `--primitive-*` / `--surface-*` for DESIGN.md-generated files, or `--color-*` for legacy)
- [ ] Typography tokens (font size / weight scale)
- [ ] Spacing tokens
- [ ] Responsive breakpoints

### B. DB Design Document Completeness

Read `docs/database/database-design.md` and confirm it contains:

- [ ] Full ERD section
- [ ] Common rules (table prefixes, audit columns, naming)
- [ ] Module-specific table sections
- [ ] FK relationship summary section

Read `docs/database/naming-rules.md` and confirm:

- [ ] Table prefix rules (TB_/TC_/TH_/TL_/TR_)
- [ ] Column naming rules (suffixes such as _YMD/_DT/_AMT/_NM/_CD)
- [ ] Standard terminology dictionary integration method

### C. Test Strategy Completeness

Read `docs/tests/test-strategy.md` and confirm:

- [ ] Test level definitions (unit/integration/E2E)
- [ ] Test coverage goals
- [ ] Test naming conventions
- [ ] Test data management strategy

### D. Global Settings (content-level)

- [ ] Agent Teams / MCP configuration present in `~/.claude/settings.json` (the script only verifies existence; confirm the expected keys are actually configured for this environment)

### E. Sprint Progress Tracking

If `docs/sprints/sprint-1/progress.md` exists (optional), confirm it contains the tracker markers:

- [ ] Progress table section (`<!-- PROGRESS_TABLE_START -->` ... `<!-- PROGRESS_TABLE_END -->`)
- [ ] Activity log section (`<!-- ACTIVITY_LOG_START -->` ... `<!-- ACTIVITY_LOG_END -->`)
- [ ] Summary section (`<!-- SUMMARY_START -->` ... `<!-- SUMMARY_END -->`)

### F. CLAUDE.md Content (judgment)

The script greps for section keywords. Additionally confirm the sections are substantive (not empty headers): Architecture (backend/frontend/DB actually specified), Prohibited practices, and a design-document SSoT rule.

## Step 3: Delegate Structural Scoring (optional but recommended)

For a scored compliance report, invoke the `astra-validator` agent via the Task/Agent tool, passing the project root. The agent RUNs `verify-setup.sh` itself and layers the same judgment areas into a `{score}/100` report by area. Use its output to enrich the "Recommended Actions" below rather than duplicating the mechanical list.

## Result Output

Outputs verification results in the following format:

```
## ASTRA Sprint 0 Checklist Verification Results

### Mechanical (verify-setup.sh): {passed}/{total} required passed
- Failed: [ ] {item} — {create the missing file/directory}
- Optional not found: {item}

### Judgment-Based Content
- [x] {passed content check}
- [ ] {failed content check} — {resolution method}

### Recommended Actions
1. {specific action items, incl. astra-validator recommendations if run}
```

## Notes

- This skill is read-only. It does not modify files.
- The mechanical required-path list lives ONLY in `scripts/verify-setup.sh` — never restate it here.
- Clearly marks each item as passed/failed and provides specific resolution methods for failed items.
