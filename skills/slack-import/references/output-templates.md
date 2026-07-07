# Slack-Import Output Templates

Literal deliverable skeletons for Steps 7 and 8. Instantiate each with the analyzed item data. Preserve every `{...}` placeholder, HTML comment (conditional-include markers), and marker pair (e.g., `<!-- PROGRESS_TABLE_START -->`).

## Templates in this file
- Blueprint (Step 7) → `docs/blueprints/{NNN}-{feature-name}/blueprint.md`
- Sprint prompt map (Step 8.B) → `docs/sprints/sprint-{N}-{primary-feature-name}/prompt-map.md`
- Progress tracker (Step 8.C) → `docs/sprints/sprint-{N}-{sprint-name}/progress.md`

## Blueprint template (Step 7)

~~~markdown
# {feature name}

## Overview
- **Feature name**: {feature name}
- **Source**: Slack List "{LIST_NAME}" — @{assignee}
  <!-- When merged: list all assignees as @{assignee1}, @{assignee2} -->
- **Priority**: {High/Medium/Low}
- **Related modules**: {module list}

<!-- Include this section only if a Figma link exists -->
## Design reference
- **Figma**: {Figma URL}

## Background and purpose
{background written from the item data}

## Functional requirements

### Must
- {requirement 1}
- {requirement 2}

### Should
- {requirement}

### Could
- {requirement}

## Technical design

### API endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/{resource} | {description} |

### Data model
{related table/entity structure — author by referencing docs/database/database-design.md}

### External integrations
{external APIs, services integrated}

## Dependencies
- **Predecessors**: {features this depends on}
- **Successors**: {features that depend on this}

## Acceptance criteria
- [ ] {acceptance criterion 1}
- [ ] {acceptance criterion 2}

## Original Slack List item

> **List**: {LIST_NAME}
> **Assignee**: @{assignee}
> **Status**: In progress

Below is the full original field data fetched via `slack_list_items_info`. Include all fields verbatim without abbreviation.

> **When merged (parenthesis grouping)**: include each original item's data under an `### Original Item {N}: {title}` subheading; omit none.

| Field | Value |
|-------|-------|
| {field-1 name} | {field-1 value — full content} |
| {field-2 name} | {field-2 value — full content} |
| ... | ... |

> **Long-text fields** (description, memo, body, etc.) are included below in full:
>
> {full original text — preserve line breaks as-is}
~~~

## Sprint prompt map template (Step 8.B)

**When creating a new sprint**: create the sprint directory as `sprint-{N}-{primary-feature-name}/` (e.g., `sprint-1-auth/`), using the first extracted feature name for `{primary-feature-name}`.

~~~markdown
# Sprint {N} Prompt Map

## Sprint Goal
Requirements collected from Slack List "{LIST_NAME}" — {feature summary}

## Source
- **Slack List**: {LIST_NAME} ({LIST_ID})
- **Slack Channel**: #{CHANNEL_NAME}
- **Collected**: {YYYY-MM-DD}
- **Items Analyzed**: {number of items analyzed}
- **Features Extracted**: {number of features extracted}

## Feature {F}: {feature-name}

> **Numbering rule**: `{F}` is the feature ordinal (1, 2, 3, …). Subsections are numbered `{F}.1`, `{F}.2` to match the feature number. This is the same format used by the `sprint-init` skill's prompt map.

### {F}.1 Design Prompt
/feature-dev "Based on the design in docs/blueprints/{NNN}-{feature-name}/blueprint.md,
author a detailed design document for {feature description}.
{core requirements summary}
Reference docs/database/database-design.md.
Do not modify code yet."

### {F}.2 DB Design Reflection Prompt
/feature-dev "Based on docs/blueprints/{NNN}-{feature-name}/blueprint.md,
add/modify the {related tables} tables in docs/database/database-design.md.
Also update the ERD and FK-relationship summary.
Follow the standard term dictionary.
Do not modify code yet."

### {F}.3 Test Case Prompt
/feature-dev "Based on the functional requirements in docs/blueprints/{NNN}-{feature-name}/blueprint.md,
author test cases in docs/tests/test-cases/sprint-{N}/{feature-name}-test-cases.md.
Use Given-When-Then format and include unit / integration / edge cases.
Do not modify code yet."

### {F}.4 Implementation Prompt
/feature-dev "Strictly follow docs/blueprints/{NNN}-{feature-name}/blueprint.md
and docs/database/database-design.md to proceed with development.
Reference docs/tests/test-cases/sprint-{N}/{feature-name}-test-cases.md to author tests,
and once implementation is complete, run all tests and
report the results in docs/tests/test-reports/."

## Feature {F+1}: {feature-name}
{repeat the same structure as above — keep subsection numbers aligned with the feature number}
~~~

**When adding to an existing sprint**: read the existing `prompt-map.md`, find the last feature number by matching the `## Feature {#}:` pattern, then number new features starting from that number + 1. Keep subsections as `{F}.1`, `{F}.2` aligned with the feature number.

## Progress tracker template (Step 8.C)

~~~markdown
# Sprint {N} Progress Tracker

## Sprint Information
- **Sprint Number**: {N}
- **Sprint Goal**: implement requirements based on Slack List "{LIST_NAME}"
- **Start Date**: {YYYY-MM-DD}
- **End Date**: {YYYY-MM-DD} (+7 days)
- **Status**: In Progress

<!-- SLACK_LIST_MAPPING_START -->
## Slack List Mapping

- **List ID**: {LIST_ID}
- **List Name**: {LIST_NAME}
- **Status Column**: {status_column_id}
- **Status Options**: `Not started`={not_started_option_id}, `In progress`={in_progress_option_id}, `Done`={done_option_id}

| Feature | Slack Item ID |
|---------|---------------|
| {feature-1} | {Rec_ID_1} |
| {feature-2} | {Rec_ID_2} |
<!-- SLACK_LIST_MAPPING_END -->

<!-- PROGRESS_TABLE_START -->
## Feature Progress

| Feature | Blueprint | DB Design | Test Cases | Implementation | Test Report | Status |
|---------|-----------|-----------|------------|----------------|-------------|--------|
| {feature-1} | Done | - | - | - | - | In Progress |
| {feature-2} | Done | - | - | - | - | In Progress |

**Legend**: `-` Not Started, `WIP` In Progress, `Done` Completed, `N/A` Not Applicable
<!-- PROGRESS_TABLE_END -->

<!-- SUMMARY_START -->
## Summary
- **Total Features**: {N}
- **Completed**: 0
- **In Progress**: {N}
- **Overall Progress**: 0%
- **Last Updated**: {YYYY-MM-DD HH:MM}
<!-- SUMMARY_END -->

<!-- ACTIVITY_LOG_START -->
## Activity Log

| Timestamp | Event | File | Details |
|-----------|-------|------|---------|
| {YYYY-MM-DD HH:MM} | Blueprint Created | docs/blueprints/{NNN}-{feature}/blueprint.md | Extracted from Slack List "{LIST_NAME}" |
<!-- ACTIVITY_LOG_END -->
~~~

When adding to an existing sprint, append new rows to the progress.md table and record in the Activity Log.
