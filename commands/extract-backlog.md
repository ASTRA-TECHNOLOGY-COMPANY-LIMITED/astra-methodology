---
description: Extracts and summarizes backlog items from a Slack channel
argument-hint: "<channel-name or channel-id> [limit]"
allowed-tools: mcp__fect-slack__slack_list_channels, mcp__fect-slack__slack_get_history, mcp__fect-slack__slack_search_channels, mcp__fect-slack__slack_get_user_info, AskUserQuestion
---

# Slack Backlog Extraction

Analyzes messages from a Slack channel and organizes them into development backlog items.

> To also generate the Blueprint and Sprint, use the `/slack-import` skill.

## Input

Parsed from `$ARGUMENTS`:

| Position | Meaning | Example |
|----------|---------|---------|
| 1st | Channel name or ID | `project-tasks`, `C01234567890` |
| 2nd (optional) | Number of messages to fetch | `30` (default: 20) |

If no arguments are provided, list channels with `mcp__fect-slack__slack_list_channels` and prompt the user via `AskUserQuestion`.

## Analysis Procedure

1. Resolve the channel ID (if a name is given, search with `mcp__fect-slack__slack_search_channels`)
2. Fetch messages with `mcp__fect-slack__slack_get_history`
3. Identify content that has a requirement/task/issue nature in each message
4. Call `mcp__fect-slack__slack_get_user_info` for each unique user ID
5. Merge duplicate/similar items

## Output Format

```
## Slack Backlog — #{channel-name}

Period: {oldest_msg_date} ~ {latest_msg_date}
Messages analyzed: {N}
Items extracted: {M}

### Backlog Items

| # | Feature | Description | Requester | Date | Priority | Message |
|---|---------|-------------|-----------|------|----------|---------|
| 1 | Email verification | Send/verify email verification code at sign-up | @kim | 03-06 | High | [first 30 chars of original message...] |
| 2 | PG payment integration | Inicis PG card/bank-transfer processing | @lee | 03-06 | High | [first 30 chars of original message...] |
| 3 | Admin dashboard | Separate dashboards by admin permission | @park | 03-06 | Medium | [first 30 chars of original message...] |

### Recommended Next Steps
- `/slack-import {channel}` — Auto-generate Blueprint + Sprint from the selected items (bulk)
- `/blueprint {feature-slug}` — Author Blueprint per feature (data flow, schema, logic)
- `/sprint-init {feature-slug}` — Start the sprint after the Blueprint is ready
- `/feature-dev "..."` — Implement inside the sprint worktree (HITL follows Blueprint Section 10)
```

## Priority Decision Criteria

| Signal | Decision |
|--------|----------|
| 3 or more reactions, or :fire: :rotating_light: :exclamation: reactions | High |
| 3 or more thread replies | High |
| Keywords such as "urgent", "ASAP", "important", "critical" | High |
| 1–2 thread replies | Medium |
| Simple mention, idea-only nature | Low |
