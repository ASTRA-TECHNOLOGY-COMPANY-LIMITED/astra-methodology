# Sprint Document Templates

Templates instantiated by `/sprint-init` into `$WT_PATH/docs/sprints/sprint-{N}-{sprint-name}/`. Replace `{N}`, `{sprint-name}`, `{PORT_BASE}`, `{feature-N}`, and date placeholders.

## Table of contents

- **Progress Tracker** (`progress.md`) — Step 2.5. Feature rows come from the `## Feature {#}: {name}` headers in prompt-map.md; all columns start `-` (Not Started). Keep the `<!-- *_START -->` / `<!-- *_END -->` marker comments — the `track-sprint-progress.sh` hook edits between them.
- **Retrospective** (`retrospective.md`) — Step 3. Static template; AI-analysis fields are auto-collected later.

---

## Progress Tracker — `progress.md` (Step 2.5)

Read the prompt map from Step 2 and extract feature names from `## Feature {#}: {name}` headers (`{#}` = ordinal). All features start as `-` in every column.

```markdown
# Sprint {N} Progress Tracker

## Sprint Information
- **Sprint Number**: {N}
- **Sprint Name**: {sprint-name}
- **Sprint Branch**: feat/sprint-{N}-{sprint-name}
- **Worktree**: .worktrees/sprint-{N}-{sprint-name}/
- **Port Base**: {PORT_BASE}
- **Sprint Goal**: [copy from prompt map Sprint Goal section]
- **Start Date**: {YYYY-MM-DD}
- **End Date**: {YYYY-MM-DD} (+7 days)
- **Status**: In Progress

<!-- PROGRESS_TABLE_START -->
## Feature Progress

| Feature | Blueprint | DB Design | Test Cases | Implementation | Test Report | Status |
|---------|-----------|-----------|------------|----------------|-------------|--------|
| {feature-1} | - | - | - | - | - | Not Started |
| {feature-2} | - | - | - | - | - | Not Started |

**Legend**: `-` Not Started, `WIP` In Progress, `Done` Completed, `N/A` Not Applicable
<!-- PROGRESS_TABLE_END -->

<!-- SUMMARY_START -->
## Summary
- **Total Features**: {N}
- **Completed**: 0
- **In Progress**: 0
- **Overall Progress**: 0%
- **Last Updated**: {YYYY-MM-DD HH:MM}
<!-- SUMMARY_END -->

<!-- ACTIVITY_LOG_START -->
## Activity Log

| Timestamp | Event | File | Details |
|-----------|-------|------|---------|
<!-- ACTIVITY_LOG_END -->
```

---

## Retrospective — `retrospective.md` (Step 3)

```markdown
# Sprint {N} Retrospective

## Date: {YYYY-MM-DD}

## AI Analysis Data
- code-review recurring issues: [auto-collected]
- security-guidance blocked count: [auto-collected]
- astra-methodology violation frequency: [auto-collected]

## Team Discussion (areas AI cannot catch)

### What went well (Keep)
-

### What to improve (Problem)
-

### What to try (Try)
-

## Automated Improvement Actions
- /hookify [codify recurring mistakes found in this sprint]
- CLAUDE.md update content: [describe added rules]
```
