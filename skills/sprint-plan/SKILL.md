---
name: sprint-plan
description: "Initializes a new ASTRA sprint. Creates sprint prompt maps, progress trackers, and retrospective templates."
argument-hint: "[sprint-number]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# ASTRA Sprint Initialization

Creates prompt maps and retrospective templates for a new sprint.

## Execution Procedure

### Step 1: Confirm Sprint Number and Sprint Name

Parse from `$ARGUMENTS`:
- **Sprint number** (optional): If not provided, scan existing directories in `docs/sprints/` matching the `sprint-{N}-{name}/` pattern (e.g., `sprint-1-auth/`, `sprint-2-workspace/`) to determine the next number.
- **Sprint name** (optional): The primary blueprint/feature name for this sprint.

**Directory name format**: `sprint-{N}-{sprint-name}/` (e.g., `sprint-1-auth/`, `sprint-2-payment/`, `sprint-3-dashboard/`)

If the sprint name is not provided in `$ARGUMENTS`, ask the user for the primary feature/blueprint name. This name will be used as the directory suffix. Use kebab-case format (e.g., `auth`, `workspace`, `payment-dashboard`).

When scanning existing directories, extract the sprint number from directory names matching pattern `sprint-{N}-{name}` (e.g., `sprint-1-auth` → number `1`).

### Step 1.5: Switch to dev Branch

Before generating output files, switch to the `dev` branch and sync with the latest state. Do not create a work branch — work directly on `dev`. Work branch creation is handled automatically by `/pr-merge`.

1. **Check current branch**: `git branch --show-current`
2. **Skip if already on `dev`**: If the current branch is `dev`, skip steps 3–5 and run only the pull (`git pull origin dev`)
3. **Preserve uncommitted changes**: Check with `git status --porcelain`; if there are changes, save them with `git stash --include-untracked` (includes untracked files)
4. **Switch to dev and sync**: `git fetch origin dev && git checkout dev && git pull origin dev`
5. **Restore stash**: If step 3 stashed changes, restore them with `git stash pop`. On conflict, report the conflicting files to the user and request manual resolution.

> **Note**: If the `dev` branch does not exist, fall back to `main` or `master`. If no default branch exists, work on the current branch.

### Step 2: Create Sprint Prompt Map

Create the `docs/sprints/sprint-{N}-{sprint-name}/prompt-map.md` file.

Scan `docs/blueprints/` for numbered directories matching the sprint name (or use the blueprint names provided by the user). Each blueprint becomes a feature in the prompt map. Do NOT analyze or carry over items from previous sprints.

```markdown
# Sprint {N} Prompt Map

## Sprint Goal
[Describe the business value to achieve in this sprint]

## Feature 1: {feature-name}

### 1.1 Design Prompt
/feature-dev "Write the design document for {feature description}
to docs/blueprints/{NNN}-{feature-name}/blueprint.md.
{detailed requirements}
Refer to docs/database/database-design.md for DB schema.
Do not modify any code yet."

> **Numbering Rule**: Scan existing directories in `docs/blueprints/` to determine the next number. Use 3-digit zero-padded format (e.g., `001-`, `002-`).

### 1.2 DB Design Reflection Prompt
/feature-dev "Add/update the {module-name} tables in
docs/database/database-design.md:
- {table list}
- Also update the ERD and FK relationship summary. Follow standard terminology dictionary.
Do not modify any code yet."

### 1.3 Test Case Prompt
/feature-dev "Based on the feature requirements in docs/blueprints/{NNN}-{feature-name}/blueprint.md,
write test cases to docs/tests/test-cases/sprint-{N}/{feature-name}-test-cases.md.
Use Given-When-Then format, include unit/integration/edge cases.
Do not modify any code yet."

### 1.4 Implementation Prompt
/feature-dev "Strictly follow the contents of docs/blueprints/{NNN}-{feature-name}/blueprint.md and
docs/database/database-design.md to proceed with development.
Write tests referencing docs/tests/test-cases/sprint-{N}/{feature-name}-test-cases.md,
and once implementation is complete, run all tests and
report results to docs/tests/test-reports/."

## Feature 2: {feature-name}
{Repeat with the same structure as above}
```

### Step 2.5: Create Sprint Progress Tracker

Read the prompt map created in Step 2 (`docs/sprints/sprint-{N}-{sprint-name}/prompt-map.md`) and extract feature names from `## Feature {#}: {name}` headers (where `{#}` is the feature ordinal, e.g., 1, 2, 3).

Create the `docs/sprints/sprint-{N}-{sprint-name}/progress.md` file:

```markdown
# Sprint {N} Progress Tracker

## Sprint Information
- **Sprint Number**: {N}
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

- All features start as `-` (Not Started) in every column.

### Step 3: Create Retrospective Template

Create the `docs/sprints/sprint-{N}-{sprint-name}/retrospective.md` file:

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

### Step 4: Output Sprint Planning Guide

```
## Sprint {N} Initialization Complete

### Generated Files
- docs/sprints/sprint-{N}-{sprint-name}/prompt-map.md (prompt map)
- docs/sprints/sprint-{N}-{sprint-name}/progress.md (progress tracker)
- docs/sprints/sprint-{N}-{sprint-name}/retrospective.md (retrospective template)

### Sprint Planning Procedure (1 hour)
1. (10 min) Review AI analysis report
2. (20 min) Confirm business priorities with DE and agree on sprint goal
3. (20 min) Discuss prompt design direction per item + DSA shares design direction
4. (10 min) Finalize sprint backlog

### Pre-Planning Preparation (day before Planning, executed by VA)
/feature-dev "Analyze the technical complexity of candidate backlog items for this sprint.
Summarize dependencies with the existing codebase, estimated work scope, and risk factors.
Do not modify any code yet."
```

## Notes

- Existing sprint files are not overwritten.
- The prompt map is filled in collaboratively by VA and PE during the Planning meeting.
