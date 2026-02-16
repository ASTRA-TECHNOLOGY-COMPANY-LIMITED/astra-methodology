---
name: sprint-plan
description: "Initializes a new ASTRA sprint. Creates sprint prompt maps, progress trackers, and retrospective templates."
argument-hint: "[sprint-number]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# ASTRA Sprint Initialization

Creates prompt maps and retrospective templates for a new sprint.

## Execution Procedure

### Step 1: Confirm Sprint Number

Parse the sprint number from `$ARGUMENTS`. If not provided, check existing files in the `docs/prompts/` directory to automatically determine the next number.

### Step 1.5: Analyze Previous Sprint (skip if N = 1)

If this is Sprint 2 or later, analyze the previous sprint's results before creating the prompt map.

#### A. Read Previous Sprint Progress Tracker

Read `docs/prompts/sprint-{N-1}-progress.md` and extract:

1. **Incomplete features**: rows where Status ≠ `Completed` — these are carryover candidates
2. **Partially completed features**: rows where some columns are `Done` but Status ≠ `Completed` — identify exactly which pipeline stages remain (e.g., "Blueprint Done, Implementation WIP, Test Report missing")
3. **Completed features**: rows where Status = `Completed` — these are done and do not carry over

#### B. Read Previous Sprint Retrospective

Read `docs/retrospectives/sprint-{N-1}-retro.md` and extract:

1. **Improvement actions** from the "What to try (Try)" section
2. **Automated improvement actions** (hookify rules, CLAUDE.md updates)
3. **Recurring issues** from the "What to improve (Problem)" section

If the retro file does not exist or is empty (template only), note this as "Retrospective not conducted".

#### C. Compare Blueprints vs Implementation Status

1. List all files in `docs/blueprints/` (excluding `overview.md`)
2. For each blueprint, check if corresponding implementation exists:
   - Source files in `src/` matching the feature name (by directory or filename)
   - Test reports in `docs/tests/test-reports/` matching the feature name
3. Identify **designed but not implemented** features — potential carryover or deprioritization candidates

#### D. Output Previous Sprint Summary

Display the analysis before proceeding to the prompt map:

```
## Previous Sprint (Sprint {N-1}) Analysis

### Carryover Candidates
| Feature | Remaining Stages | Priority |
|---------|-----------------|----------|
| {feature} | {Implementation, Test Report} | {High/Medium/Low} |

### Blueprints Without Implementation
- {blueprint-name}.md — designed in Sprint {X}, not yet implemented

### Retrospective Actions to Address
- {action item from retro}

### Recommendation
- Carry over {M} incomplete features as priority items
- {N} blueprints exist without implementation — confirm with DE whether to include
```

Ask the user (VA/PE) to confirm which carryover items to include in this sprint before proceeding to Step 2.

### Step 2: Create Sprint Prompt Map

Create the `docs/prompts/sprint-{N}.md` file.

If there are carryover items from Step 1.5, list them first as `(Carryover)` features before new features. Carryover features that already have blueprints should skip the Design Prompt (1.1) and note the existing blueprint path instead. Similarly, skip any pipeline stage that is already `Done` from the previous sprint.

```markdown
# Sprint {N} Prompt Map

## Sprint Goal
[Describe the business value to achieve in this sprint]

## Previous Sprint Carryover
{If N >= 2, summarize carried-over items and retrospective actions. If N = 1, omit this section.}

## Feature 1: {carryover-feature} (Carryover from Sprint {N-1})

### 1.1 Design Prompt
(Already completed — see docs/blueprints/{feature-name}.md)

### 1.2 DB Design Reflection Prompt
(Already completed — reflected in docs/database/database-design.md)

### 1.3 Test Case Prompt
{Include only if test cases were not written in the previous sprint}

### 1.4 Implementation Prompt
{Include — this is the remaining work}

## Feature 2: {new-feature-name}

### 2.1 Design Prompt
/feature-dev "Write the design document for {feature description}
to docs/blueprints/{feature-name}.md.
{detailed requirements}
Refer to docs/database/database-design.md for DB schema.
Do not modify any code yet."

### 2.2 DB Design Reflection Prompt
/feature-dev "Add/update the {module-name} tables in
docs/database/database-design.md:
- {table list}
- Also update the ERD and FK relationship summary. Follow standard terminology dictionary.
Do not modify any code yet."

### 2.3 Test Case Prompt
/feature-dev "Based on the feature requirements in docs/blueprints/{feature-name}.md,
write test cases to docs/tests/test-cases/{feature-name}-test-cases.md.
Use Given-When-Then format, include unit/integration/edge cases.
Do not modify any code yet."

### 2.4 Implementation Prompt
/feature-dev "Strictly follow the contents of docs/blueprints/{feature-name}.md and
docs/database/database-design.md to proceed with development.
Write tests referencing docs/tests/test-cases/{feature-name}-test-cases.md,
and once implementation is complete, run all tests and
report results to docs/tests/test-reports/."

## Feature 3: {feature-name}
{Repeat with the same structure as above}
```

### Step 2.5: Create Sprint Progress Tracker

Read the prompt map created in Step 2 (`docs/prompts/sprint-{N}.md`) and extract feature names from `## Feature {N}: {name}` headers.

Create the `docs/prompts/sprint-{N}-progress.md` file:

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

- **New features** start as `-` (Not Started) in every column.
- **Carryover features** carry forward their previous sprint's column statuses (e.g., if Blueprint was `Done` in Sprint {N-1}, it starts as `Done` in Sprint {N}).

### Step 3: Create Retrospective Template

Create the `docs/retrospectives/sprint-{N}-retro.md` file:

```markdown
# Sprint {N} Retrospective

## Date: {YYYY-MM-DD}

## AI Analysis Data
- code-review recurring issues: [auto-collected]
- security-guidance blocked count: [auto-collected]
- standard-enforcer violation frequency: [auto-collected]

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
- docs/prompts/sprint-{N}.md (prompt map)
- docs/prompts/sprint-{N}-progress.md (progress tracker)
- docs/retrospectives/sprint-{N}-retro.md (retrospective template)

### Sprint Planning Procedure (1 hour)
1. (10 min) Review previous sprint analysis & AI analysis report
2. (20 min) Confirm business priorities with DE, review carryover items, and agree on sprint goal
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
