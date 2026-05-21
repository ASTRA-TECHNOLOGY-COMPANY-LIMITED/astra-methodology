---
description: Authors a Blueprint (design document) focused on data flow, schema, and logic design (excludes implementation code)
argument-hint: "[feature-slug-or-blueprint-path] [--auto] [--from-planner=<planner-dir>]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Skill, Task, TodoWrite
---

# /blueprint — Blueprint Authoring Slash Command

Calls `Skill('blueprint', '$ARGUMENTS')` to author a Blueprint.

## Usage Examples

```
/blueprint user-auth
/blueprint user-auth --from-planner=docs/planner/003-user-auth
/blueprint user-auth --auto                       # Auto-run without HITL (autorun-compatible)
/blueprint docs/blueprints/003-user-auth/blueprint.md   # Update an existing Blueprint
```

## Behavior Summary

| Step | Content |
|------|---------|
| 1 | Parse `$ARGUMENTS` (slug / `--auto` / `--from-planner`) |
| 2 | Auto-load `docs/planner/{NNN}-{slug}/` deliverables (if present) |
| 3 | Auto-draft 10 standard sections (Overview / Functional Spec / Data Model / API Contract / Sequence / Logic Pseudocode / Error Policy / Non-functional / Test Strategy / **HITL Triggers**) |
| 4 | HITL on only 1–3 core design decisions (skipped under `--auto`) — PK strategy, transaction boundary, external-call synchronicity |
| 5 | Validate TB_/`_YMD`/forbidden words via the `data-standard` auto-skill (automatically triggered) |
| 6 | Quality validation via the `blueprint-reviewer` agent |

## Output

- `docs/blueprints/{NNN}-{feature-slug}/blueprint.md` — Blueprint body (10 sections)
- `docs/blueprints/{NNN}-{feature-slug}/review.md` — blueprint-reviewer report

## Relationship with /feature-dev

The Blueprint's **Section 10 (HITL Triggers)** is later followed verbatim by `/feature-dev` during implementation so that the user is only asked about *truly required decisions*. Since the Blueprint is the single source of truth (SoT), passing only the Blueprint path when invoking `/feature-dev` from prompt-map.md automatically activates the HITL guard.

See `skills/blueprint/SKILL.md` for detailed steps.
