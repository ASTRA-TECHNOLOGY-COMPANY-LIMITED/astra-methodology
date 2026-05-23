---
description: Authors a Blueprint (design document) focused on data flow, schema, and logic design (excludes implementation code). v5.10+ runs in a worktree-first order — worktree creation → blueprint authoring inside the worktree → reviewer → commit on sprint branch.
argument-hint: "[feature-slug-or-blueprint-path] [--auto] [--from-planner=<planner-dir>]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Skill, Task, TodoWrite
---

# /blueprint — Blueprint Authoring Slash Command (v5.10+)

Thin wrapper that invokes `Skill('blueprint', '$ARGUMENTS')`. The full procedure (worktree-first order) is implemented in `skills/blueprint/SKILL.md`.

## Usage Examples

```
/blueprint user-auth
/blueprint user-auth --from-planner=docs/planner/003-user-auth
/blueprint user-auth --auto                       # Auto-run without HITL (autorun-compatible)
/blueprint docs/blueprints/003-user-auth/blueprint.md   # Update an existing Blueprint
```

## Behavior Summary (v5.10+ worktree-first order)

| Step | Content |
|------|---------|
| 1 | Parse `$ARGUMENTS` (slug / `--auto` / `--from-planner`) on the main worktree (dev/main/master) |
| 2 | Determine the next blueprint directory number (`{NNN}`) by scanning `docs/blueprints/` on the main worktree |
| 3 | Auto-load `docs/planner/{NNN}-{slug}/` deliverables (if present) |
| 4 | **Create the sprint worktree** by delegating to `/sprint-init {slug} --scaffold-only` (worktree + `.astra-worktree.env` + scaffold prompt-map / progress / retrospective) |
| 5 | **`cd` into the new worktree** (within the skill execution) |
| 6 | Auto-draft the 10 standard sections of the blueprint *inside the worktree* (Overview / Functional Spec / Data Model / API Contract / Sequence / Logic Pseudocode / Error Policy / Non-functional / Test Strategy / **HITL Triggers**) |
| 7 | HITL on only 1–3 core design decisions (skipped under `--auto`) — PK strategy, transaction boundary, external-call synchronicity |
| 8 | Validate TB_/`_YMD`/forbidden words via the `data-standard` auto-skill |
| 9 | Quality validation via the `blueprint-reviewer` agent |
| 10 | Commit the blueprint to the sprint branch (`feat/sprint-{N}-{slug}`) |
| 11 | Print the consolidated next-steps block — the user runs `cd {worktree-path}` then continues with `/feature-dev` / `/test-scenario` / `/test-run` / `/pr-merge` |

## Branch / location guards

- **Already inside a sprint worktree** → worktree creation is skipped (secondary blueprint case); the blueprint is added to the existing sprint branch.
- **Non-standard branch** (not dev / main / master) → **abort with error**. The user must `git checkout dev` and re-invoke.

## Output

- `{worktree}/docs/blueprints/{NNN}-{feature-slug}/blueprint.md` — Blueprint body (10 sections)
- `{worktree}/docs/blueprints/{NNN}-{feature-slug}/review.md` — blueprint-reviewer report
- `{worktree}/.astra-worktree.env` — port-isolated env (written by `/sprint-init`)
- `{worktree}/docs/sprints/sprint-{N}-{slug}/{prompt-map,progress,retrospective}.md` — sprint scaffolding (written by `/sprint-init`)

## Relationship with /feature-dev

The Blueprint's **Section 10 (HITL Triggers)** is later followed verbatim by `/feature-dev` during implementation so that the user is only asked about *truly required decisions*. The prompt-map authored by `/sprint-init --scaffold-only` (v5.10+ variant) starts directly at 1.1 = DB Design (the blueprint authoring step is omitted because it has already been done by this command).

See `skills/blueprint/SKILL.md` for the detailed procedure including step-by-step shell commands.
