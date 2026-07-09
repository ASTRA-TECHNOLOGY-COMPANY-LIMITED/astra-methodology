---
name: sprint-progress
description: >
  Automatically updates sprint progress tracking when blueprint, database design,
  test case, implementation, or test report files are created or modified.
  Used when writing files under docs/blueprints/, docs/database/, docs/tests/,
  docs/sprints/, or src/ directories.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Sprint Progress Auto-Tracking Skill

When you create or modify sprint-related files, you must update the sprint progress tracker accordingly.
This skill defines the rules for detecting events and updating the progress table.

## Application Targets

This skill applies when writing or editing files matching these patterns:
- `docs/blueprints/{NNN}-{feature-name}/*.md` — blueprint event (any .md file inside a numbered blueprint directory)
- `docs/database/database-design.md` — DB design event
- `docs/tests/test-cases/sprint-*/*.md` — test case event
- `docs/tests/test-reports/*.md` — test report event
- `src/**/*.{java,ts,tsx,py,js,jsx,kt,go,rs}` — implementation event

## Current Sprint Detection

1. Look in `docs/sprints/` for directories matching `sprint-{N}-{name}/` (e.g., `sprint-1-auth/`, `sprint-2-workspace/`)
2. Extract the sprint number from each directory name (the `{N}` part before the second hyphen)
3. The highest `{N}` is the current sprint number
4. The tracker file is `docs/sprints/sprint-{N}-{name}/progress.md`

## Update Procedures

### Procedure 1: After Blueprint Creation/Modification

When a file inside a numbered blueprint directory (`docs/blueprints/{NNN}-{feature-name}/`) is written:

1. Open `docs/sprints/sprint-{N}-{name}/progress.md`
2. Extract the feature name from the directory name (strip the `{NNN}-` prefix, e.g., `001-auth` → `auth`)
3. Find the feature row that matches the extracted feature name
4. Set the **Blueprint** column to `Done`
5. If no matching feature row exists (ad-hoc feature), add a new row with the extracted feature name
6. Recalculate the Summary section

### Procedure 2: After DB Design Modification

When `docs/database/database-design.md` is modified:

1. Open the sprint progress tracker
2. Identify which feature(s) the DB changes relate to (check the section headers or table names in the modified content)
3. Set the **DB Design** column to `Done` for the relevant feature(s), or `WIP` if only partial tables were added
4. Recalculate the Summary section

### Procedure 3: After Test Case Creation/Modification

When a file under `docs/tests/test-cases/sprint-*/` is written:

1. Extract the sprint number from the file path (e.g., `docs/tests/test-cases/sprint-2/...` → sprint 2)
2. Open `docs/sprints/sprint-{extracted-N}-*/progress.md` (glob to find the directory; not necessarily the latest sprint)
3. Match the test case filename to a feature (e.g., `user-auth-test-cases.md` → `user-auth` feature)
4. Set the **Test Cases** column to `Done`
5. Recalculate the Summary section

### Procedure 4: After Implementation File Write

When a source file under `src/` is written:

1. Open the sprint progress tracker
2. Determine which feature the source file belongs to (by module directory, class name, or import relationships)
3. Set the **Implementation** column to `WIP`
4. **Never set Implementation to `Done` from a single write** — implementation is only `Done` when:
   - The user explicitly confirms implementation is complete, OR
   - A test report for the feature has been created, OR
   - All files referenced in the blueprint exist and are non-empty
5. Recalculate the Summary section

### Procedure 5: After Test Report Creation

When a file under `docs/tests/test-reports/` is written:

1. Open the sprint progress tracker
2. Match the test report to a feature
3. Set the **Test Report** column to `Done`
4. Check if the feature is now fully complete (all columns are `Done` or `N/A`)
5. If fully complete, set the **Status** column to `Completed`
6. Recalculate the Summary section

> **Legacy note (pre-v5.18)**: sprints created by the removed `/slack-import` skill may carry a `<!-- SLACK_LIST_MAPPING_START -->` section in progress.md — ignore it (Slack List status sync was removed together with the fect-slack integration).

## Tracker File Auto-Creation

If the tracker file `docs/sprints/sprint-{N}-{name}/progress.md` does not exist when an event occurs:

1. Read the sprint prompt map `docs/sprints/sprint-{N}-{name}/prompt-map.md`
2. Extract feature names from `## Feature {#}: {name}` headers (where `{#}` is the feature ordinal, e.g., 1, 2, 3)
3. Create the tracker file using the template below
4. Then apply the appropriate update procedure

### Tracker Template

```markdown
# Sprint {N} Progress Tracker

## Sprint Information
- **Sprint Number**: {N}
- **Sprint Goal**: [from prompt map Sprint Goal section]
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

## Feature-to-File Matching Rules

When matching files to features:
1. **Blueprint directory match**: Blueprint directory name matches feature name (e.g., `001-user-auth/` → `user-auth`, strip the `{NNN}-` prefix)
2. **Prefix match**: Test case/report filename starts with feature name (e.g., `user-auth-test-cases.md` → `user-auth`)
3. **Directory match**: Source files in a directory named after the feature (e.g., `src/modules/user-auth/` → `user-auth`)
4. **Content match**: If no name match, check if the file content references the feature by name

## Summary Recalculation

After each update to the progress table:
1. Count features with **Status** = `Completed` → **Completed** count
2. Count features with any column as `WIP` or `Done` but **Status** ≠ `Completed` → **In Progress** count
3. Calculate **Overall Progress** = (Completed / Total Features) × 100%
4. Update **Last Updated** to the current timestamp
