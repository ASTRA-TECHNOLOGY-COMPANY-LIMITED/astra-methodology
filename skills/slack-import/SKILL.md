---
name: slack-import
description: "Analyzes Slack channel List items to auto-generate blueprints and sprint prompt maps. Provides a workflow of channel selection → List selection → Item selection → status update → requirements analysis → blueprint / sprint generation."
argument-hint: "[channel-name or channel-id]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, mcp__fect-slack__slack_list_channels, mcp__fect-slack__slack_get_history, mcp__fect-slack__slack_search_channels, mcp__fect-slack__slack_get_user_info, mcp__fect-slack__slack_add_reaction, mcp__fect-slack__slack_post_message, mcp__fect-slack__slack_file_list, mcp__fect-slack__slack_list_items_list, mcp__fect-slack__slack_list_items_info, mcp__fect-slack__slack_list_items_update
---

# Slack Import: Blueprint / Sprint Generation from a Slack List

Collects and analyzes items from a Slack-channel List to auto-generate ASTRA blueprints and sprint prompt maps.

## Procedure

### Step 1: Pick the Slack channel

#### A. Parse arguments

Inspect `$ARGUMENTS`:

| Argument form | Behavior |
|---------------|----------|
| Channel ID (starts with `C`) | Use the channel directly |
| Channel name (e.g., `project-tasks`) | Search via `mcp__fect-slack__slack_search_channels` and match |
| _(none)_ | Go to Step 1.B for interactive selection |

#### B. Interactive channel selection

If no argument is provided, call `mcp__fect-slack__slack_list_channels` to fetch the channel list.

Show the list to the user and request a selection via `AskUserQuestion`:

```
## Slack channel list

| # | Channel | ID | Type | Member |
|---|---------|----|----|--------|
| 1 | general | C01234 | Public | Yes |
| 2 | project-tasks | C05678 | Private | Yes |
| 3 | dev-requirements | C09012 | Public | Yes |

Enter the number or name of the channel to query Lists from:
```

When the user selects by number or channel name, save the channel ID as `{CHANNEL_ID}` and the channel name as `{CHANNEL_NAME}`.

### Step 2: Pick the Slack List

#### A. Query Lists in the channel

Call `mcp__fect-slack__slack_file_list` to fetch the list of files shared in the selected channel:

- `channel`: `{CHANNEL_ID}`
- `count`: 100

From the returned file list, filter Slack-List-type files (where `mimetype` is list-related, or `filetype` is `list`, etc.).

> **Note**: Slack Lists have IDs starting with `F` in the file system. Extract only items identified as Lists from the file list. If `file_list` cannot find Lists, query channel messages via `mcp__fect-slack__slack_get_history` and extract the List ID from messages (attachment or file info) where a List was shared.

#### B. Show Lists and select

Show the discovered List set to the user and request a selection via `AskUserQuestion`:

```
## Slack Lists in #{CHANNEL_NAME}

| # | List name | ID | Created |
|---|-----------|----|---------|
| 1 | Requirements backlog | F01ABC | 2026-03-01 |
| 2 | Sprint tasks | F02DEF | 2026-03-05 |

Select the number of the List to query:
```

> **If no List is found**: if the channel has no List, inform the user and ask whether to enter a List ID manually or fall back to the message-based workflow.

When the user selects, save the List ID as `{LIST_ID}` and the List name as `{LIST_NAME}`.

### Step 3: Pick List Items

#### A. Query List items

Call `mcp__fect-slack__slack_list_items_list` to fetch items in the selected List:

- `list_id`: `{LIST_ID}`
- `limit`: 100

#### B. Status filtering (show only "Not started")

From the fetched item list, filter only items whose status is **"Not started"**:

1. Look up the **known status-column mapping** below to identify the status column ID and the "Not started" option ID:

   | List ID | Status column ID | Not started | In progress | Done |
   |---------|------------------|-------------|--------------|------|
   | `F0A5ZLTQ4T0` | `Col0A5L8XT9RD` | `Opt7MNHB19N` | `OptXBPNOYKC` | `OptTR35W8NA` |

2. Extract only items whose status-column value equals the "Not started" option ID
   - e.g., only items whose `Col0A5L8XT9RD` value is `Opt7MNHB19N`
3. For Lists with no known mapping, ask the user to confirm the status column and the "Not started" option, then filter
4. Also include items whose status column is empty (treat as "Not started")

> **If 0 filtered results**: ask via `AskUserQuestion`: "No items in 'Not started' status. Show all items?"

#### C. Show item list

Show the filtered items as a table. Each item's field (column) values are presented readably:

```
## {LIST_NAME} — item list (Not started)

| # | Title | Status | Assignee | Due | Other |
|---|-------|--------|----------|-----|-------|
| 1 | Sign-up email verification | Not started | @kim | 03-15 | High |
| 2 | PG payment integration | Not started | @lee | 03-20 | High |
| ... | ... | ... | ... | ... | ... |

Showing {filtered} of {total} items (Not started only)

Select items to process (number, range, or 'all'):
e.g., 1  or  1,3,5  or  all
To merge multiple items into one blueprint, use parentheses: (1,2,3)
```

> **Column mapping**: build the table header dynamically based on the List's schema (column definitions). Call `mcp__fect-slack__slack_list_items_info` on the first item to inspect the schema structure.

#### D. User item selection

Receive the user's selection via `AskUserQuestion`.

**Default behavior**: each item becomes **1 independent blueprint**. To merge multiple items into one blueprint, use the parenthesis `()` grouping syntax.

Supported input forms:

- `1` — pick a single item
- `1,3,5` — individual numbers (comma-separated; each becomes a separate blueprint)
- `1-5` — range (each becomes a separate blueprint)
- `all` — pick all (each becomes a separate blueprint)
- `1-3,7,9-12` — mix of ranges and individuals (each becomes a separate blueprint)
- `(1,2,3)` — parenthesis grouping: merge items 1, 2, 3 into **one blueprint**
- `(1-3),4,(5,6)` — ranges inside parens are supported: 1+2+3 merged, 4 standalone, 5+6 merged
- `(1,2),3,(4,5)` — mix: 1+2 merged, 3 standalone, 4+5 merged

> **Parse order**:
> 1. Split top-level tokens by commas outside parentheses
> 2. Parenthesized tokens: parse the inside and treat as one merge group (expanding inner ranges like `1-3`)
> 3. Unparenthesized tokens: expand ranges to individual numbers, each becoming a separate blueprint

Guidance message example:
```
Select items to process (number, range, or 'all'):
e.g., 1  or  1,3,5  or  all
To merge multiple items into one blueprint, use parentheses: (1,2,3)
```

### Step 4: Update the status of selected items

Update each selected item's status to "In progress".

#### A. Identify the status field

Identify the status-related column in the List's schema:

1. **Check the known status-column mapping**: if the List matches the table in Step 3.B, use the mapping directly.

2. **If no known mapping**: identify the status-meaning column among `select`-type columns.
   - Sample 3+ items to inspect the distribution of option IDs in select columns
   - Confirm the label of each option ID (Not started / In progress / Done) via `AskUserQuestion`
   - Append the confirmed mapping to the table in this skill file so it can be reused on the next run

> **If the status values cannot be found**: ask the user to specify the status column and values via `AskUserQuestion`.

#### B. Execute the status update (→ In progress)

For each selected item, verify the current status and change the **status-select option** to **"In progress"**:

> **Caution**: never touch the Slack-List item checkbox (completion check). The checkbox is for the assignee to manually check after they have tested it themselves. **Only the option value of the status (status) select column is changed.**

1. Check each item's current status. Skip items already "In progress" or "Done" and inform the user.
2. Only for items in "Not started" status, call `mcp__fect-slack__slack_list_items_update` **individually per item**:

- `list_id`: `{LIST_ID}`
- `cells`: `[{ "column_id": "{status_column_id}", "row_id": "{item_id}", "select": ["{in_progress_option_id}"] }]`
  - e.g., `[{ "column_id": "Col0A5L8XT9RD", "row_id": "Rec...", "select": ["OptXBPNOYKC"] }]` (using the known mapping)
  - When processing multiple items, make a separate API call per item

Report the update results to the user:

```
## Status update complete

| # | Item | Previous | Current |
|---|------|----------|---------|
| 1 | Sign-up email verification | Pending | In progress |
| 2 | PG payment integration | Pending | In progress |

{N} items updated to "In progress".
```

### Step 5: Detail analysis of selected items

#### A. Collect item data

For **every** selected item, **always** call `mcp__fect-slack__slack_list_items_info` to fetch detail info. Field data from the list API (`slack_list_items_list`) may be incomplete, so do not skip the per-item detail fetch.

- Collect **every field value of each item verbatim** (title, description, status, assignee, due, priority, body/memo, custom fields, etc.)
- If a long-text field (description, notes/memo, etc.) exists, **preserve the full content without abbreviating**
- If the assignee field contains a user ID, look up the name via `mcp__fect-slack__slack_get_user_info` at this point (call each unique user ID exactly once; avoid duplicate calls)

#### B. Extract requirements

Extract the following from each item:

1. **Feature name**: a core feature based on the item title (English in kebab-case)
2. **Feature description**: a 2–3-sentence summary of the requirements based on the item's field data
3. **Requirements list**: concrete functional requirements (bullet list)
4. **Priority**: determined from the item's priority field or by analyzing the content (High/Medium/Low)
5. **Related modules**: estimated related system modules
6. **Technical considerations**: tech elements such as API, DB, external integration
7. **Dependencies**: precedence relations with other features
8. **Design reference (Figma)**: detect Figma links (`https://www.figma.com/...` or `https://figma.com/...`) from the item fields and collect. Leave empty if none.
9. **Assignee**: the item's assignee info

**Merge rule**: only items the user grouped together with parenthesis `()` in Step 3.D are merged into one feature. Items selected without parentheses are processed as independent features. Do not auto-merge by topic similarity.

#### C. Confirm the analysis result

Show the extracted feature list to the user and request confirmation:

```
## Requirements-analysis result

### Feature 1: email verification (email-verification)
- **Source**: {LIST_NAME} — Item #1 (@kim)
- **Description**: send and validate an email verification code at sign-up
- **Requirements**:
  - send a 6-digit verification code by email
  - 5-minute validity for the code
  - on 3 failures, force resend
- **Priority**: High
- **Related modules**: member management, notifications
- **Tech notes**: SMTP integration, Redis temporary storage
- **Design reference**: https://www.figma.com/file/abc123 (or none)

### Feature 2: PG payment integration (pg-payment)
- **Source**: {LIST_NAME} — Item #2 (@lee)
- **Description**: card/bank-transfer payments via Inicis PG integration
- **Requirements**: ...
- **Priority**: High
- **Related modules**: payments, orders
- **Design reference**: none

...

Let me know if you want anything changed. If not, type "OK":
```

If the user requests changes, adjust the items. On "OK", proceed to Step 6.

### Step 6: Check existing project context

Before generating blueprints and sprints, check the existing project state.

#### A. Verify the project structure

1. Verify `CLAUDE.md` exists — if missing, instruct the user to run `/project-init` and abort
2. Scan the `docs/blueprints/` directory — determine existing blueprint numbers
3. Scan the `docs/sprints/` directory — determine the current sprint number
4. Verify whether `docs/database/database-design.md` exists

#### B. Check for duplicates

Compare existing blueprint directory names with the extracted feature names:

- If there is a blueprint with a similar name, inform the user
- Ask: "Update the existing blueprint, or create a new one?"

#### C. Determine numbering

Find the largest number among existing blueprint directories and decide the next:

- e.g., if `001-auth/`, `002-payment/` exist → start from `003`
- Zero-padded to 3 digits (e.g., `003`, `004`, ...)

#### D. Switch to the dev branch and sync to latest

Before creating blueprint files, switch to `dev` and sync to latest. Do not create a work branch; work directly on `dev`. Work-branch creation is handled automatically when `/pr-merge` runs.

0. **Main-worktree guard**: if called from inside an isolated worktree (`.astra-worktrees/<slug>/`), abort. dev-sync runs only in the main worktree:
   ```bash
   PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
   if [ -z "$PLUGIN_ROOT" ] || [ ! -f "$PLUGIN_ROOT/scripts/worktree-helpers.sh" ]; then
     echo "ERROR: CLAUDE_PLUGIN_ROOT not found. Check the plugin cache path." >&2
     exit 1
   fi
   source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"
   astra_ensure_main_worktree || exit 1
   ```
1. **Check the current branch**: `git branch --show-current`
2. **Skip if already on `dev`**: if the current branch is `dev`, skip steps 3–5 below and just pull (`git pull origin dev`)
3. **Preserve uncommitted changes**: check with `git status --porcelain`; if changes exist, stash temporarily via `git stash --include-untracked` (untracked files included)
4. **Switch to dev and sync**: `git fetch origin dev && git checkout dev && git pull origin dev`
5. **Restore stash**: if you stashed in step 3, restore via `git stash pop`. On conflict, report the conflicting files to the user and request manual resolution.

> **Note**: if the `dev` branch does not exist, work on `main` or `master`. If no default branch exists, work on the current branch.

### Step 7: Generate the blueprints

For each feature, create `docs/blueprints/{NNN}-{feature-name}/blueprint.md`.

Read `references/output-templates.md` (section "Blueprint template") and instantiate it per feature with the analyzed item data.

### Step 8: Generate the sprint prompt map

#### A. Determine the sprint number

1. Scan the `docs/sprints/` directory for `sprint-{N}-{name}/` patterns and find the largest sprint number
2. Read that sprint's `progress.md` and parse the **End Date** field. Run `date` via `Bash` to get today's date.
   - **End Date is after today**: treat as an active sprint → ask the user: "Sprint {N} is in progress (ends: {End Date}). Add to this sprint, or start a new one?"
   - **End Date is before today or cannot be parsed**: treat as a completed sprint → create a new sprint with the next number
3. If no active sprint exists or the user wants a new one, create the next-numbered sprint

#### B. Generate or update the prompt map

**When creating a new sprint**: create the sprint directory as `sprint-{N}-{primary-feature-name}/` (e.g., `sprint-1-auth/`, `sprint-2-workspace/`). Use the first extracted feature name for `{primary-feature-name}`. Read `references/output-templates.md` (section "Sprint prompt map template") and instantiate it at `docs/sprints/sprint-{N}-{primary-feature-name}/prompt-map.md`.

**When adding to an existing sprint**: read the existing `prompt-map.md`, find the last feature number by matching the `## Feature {#}:` pattern, then number new features starting from that number + 1. Keep subsections as `{F}.1`, `{F}.2` aligned with the feature number.

#### C. Create / update the progress tracker

For a new sprint, read `references/output-templates.md` (section "Progress tracker template") and instantiate it at `docs/sprints/sprint-{N}-{sprint-name}/progress.md`.

When adding to an existing sprint, append new rows to the progress.md table and record in the Activity Log.

#### D. Generate the retrospective template

For a new sprint, generate `docs/sprints/sprint-{N}-{sprint-name}/retrospective.md` (same format as the sprint-init skill).

### Step 9: Slack feedback (optional)

Ask the user whether to post the processing result back to the Slack channel:

```
Post the processing result to Slack #{CHANNEL_NAME}? (y/n)
```

If the user selects `y`, post a summary message via `mcp__fect-slack__slack_post_message`:

```
:clipboard: *ASTRA Sprint {N} — requirements reflected*

The following items were registered to the Sprint {N} backlog:

{feature list (bullet)}

:page_facing_up: Blueprints: check under docs/blueprints/
:spiral_calendar_pad: Prompt map: docs/sprints/sprint-{N}-{sprint-name}/prompt-map.md
```

### Step 10: Result summary

```
## Slack to Sprint complete

### Source
- **Channel**: #{CHANNEL_NAME}
- **List**: {LIST_NAME} ({LIST_ID})
- **Items analyzed**: {N}
- **Features extracted**: {M}
- **Status updates**: {N} items → "In progress"

### Generated blueprints
| # | Feature | Path | Priority |
|---|---------|------|----------|
| {NNN} | {feature} | docs/blueprints/{NNN}-{name}/ | High |
| {NNN} | {feature} | docs/blueprints/{NNN}-{name}/ | Medium |

### Sprint
- **Sprint {N}** prompt map: docs/sprints/sprint-{N}-{sprint-name}/prompt-map.md
- **Sprint {N}** progress tracker: docs/sprints/sprint-{N}-{sprint-name}/progress.md
- **Sprint {N}** retrospective template: docs/sprints/sprint-{N}-{sprint-name}/retrospective.md

### Next steps
1. Review the generated blueprints and confirm requirements with DE
2. Adjust sprint details via `/sprint-init {N}`
3. Execute each step of the prompt map in order
4. Generate E2E test scenarios via `/test-scenario`
```

## Quick run examples

```
# Interactive — choose from the channel list
/slack-import

# Specify channel by name directly
/slack-import project-tasks

# Specify channel by ID directly
/slack-import C01234567890
```

## Caveats

- The `SLACK_BOT_TOKEN` environment variable must be set. If not set, print a guidance message and abort.
- The project must already be initialized for ASTRA (`CLAUDE.md`, `docs/blueprints/` exist). If not, guide to `/project-init`.
- Existing blueprint files are not overwritten. On duplication, ask the user first.
- The List Item's field structure may differ per List, so the schema is inspected dynamically.
- Status-update guard: in Step 4.B, items in "In progress" or "Done" status are auto-skipped. The same applies when the "show all items" fallback is selected.
- **Checkbox forbidden**: do not modify the Slack-List item checkbox (completion check) via automation. The checkbox is for the assignee to manually check after they have tested it themselves. All status changes are only applied to the option value of the status-select column.
