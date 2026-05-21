---
name: sprint-init
description: "Initializes a new ASTRA sprint. Creates an isolated sprint worktree (with port-isolated dev server settings), generates sprint prompt maps, progress trackers, and retrospective templates inside that worktree, and prints the cd path so all subsequent development and testing happens in the worktree. With --auto flag, also auto-executes the post-scaffolding pipeline: /test-scenario → implementation → /test-run → /pr-merge --auto (worktree auto-removed). Between each major stage (5.2/5.3/5.4/5.5 iteration/5.6), the skill performs a silent save (auto-state.yaml + commit) and applies a 'reference-avoidance' rule (don't re-read large prior artifacts; rely on yaml SSoT) so the system's built-in auto-compression keeps context manageable, then continues directly to the next stage without user intervention. --resume flag is reserved for true recovery (context crash, forced interrupt) — it reads auto-state.yaml and jumps to next_stage. Only halts on true blockers (gh auth, merge conflicts, Critical review issues)."
argument-hint: "[sprint-number] [sprint-name] [--auto] [--max-iter=N] [--resume]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Skill, Agent, TodoWrite
---

# ASTRA Sprint Initialization (v5.0+)

Creates a sprint-level isolated worktree, writes port-isolated env settings, and generates prompt maps / progress trackers / retrospective templates **inside that worktree**.

> **v5.0+ policy**: Every feature task and test for a sprint runs inside a single worktree (`.astra-worktrees/sprint-<N>-<name>/`). `/pr-merge` reflects the work into dev and auto-removes the worktree. Trade-off: one PR per sprint — no per-feature review granularity, but clean per-sprint merge/rollback.

## Execution Procedure

### Step 0.A: Resume Detection (`--resume` flag)

**When to use**: `--resume` is **for true recovery**. In normal operation, `--auto` mode never interrupts between stages — it only does a silent save (`auto-state.yaml` + commit) and then proceeds to the next stage automatically. Only in the following cases does the user explicitly invoke `/sprint-init --resume` to continue:

1. The LLM lost its in-flight variables after the system auto-compressed the context and progress halted
2. The user intentionally stopped mid-way and is now continuing
3. The skill execution terminated abnormally due to a crash or session end

Since `auto-state.yaml` is the single source of truth (SSoT), in any of the above cases we read `next_stage` from the yaml and resume from exactly that point.

Parse the `--resume` flag from `$ARGUMENTS` first:

```bash
RESUME_MODE=0
for arg in $ARGUMENTS; do
  if [ "$arg" = "--resume" ]; then
    RESUME_MODE=1
    break
  fi
done
```

#### `--resume` mode behavior
If `RESUME_MODE=1`:

1. **Invoked from the main worktree**: Glob `docs/sprints/sprint-*/auto-state.yaml` and filter entries with `merge.merge_success != true`. Adopt the **largest sprint number N** as the "most recent" (compare the N in directory names `sprint-{N}-...`). cd into that entry's `sprint.worktree_path` and continue the stages. If the worktree has already been removed (the case where only the yaml remains in dev after the merge), print an error and abort — `--resume` is only meaningful when an in-progress worktree is still alive.
2. **Invoked from inside a sprint worktree**: Read the current directory's `docs/sprints/sprint-{N}-{name}/auto-state.yaml` (abort if missing).
3. Read `auto-state.yaml` and restore all of the following variables:
   - `SPRINT_N`, `SPRINT_NAME`, `WT_PATH`, `MAX_ITER`, `CURRENT_ITER`
   - `progress.next_stage`, `progress.last_iteration_summary`, `files_to_patch_next`
   - Other per-stage deliverable paths
4. **Skip all of Step 0~4 (worktree creation·scaffolding)** — they already exist.
5. **Jump directly to `progress.next_stage`**. e.g., `next_stage: 5.4` → run Step 5.4 immediately.
6. Startup notice:
   ```
   🔄 sprint-init --resume resumed
      Sprint: sprint-{N}-{name}
      Worktree: {WT_PATH}
      Previously completed: {completed_stages}
      Resuming stage: Stage {next_stage} — {next_stage_description}
      Iteration: {current_iter}/{max_iter}
   ```

If `RESUME_MODE=0`, proceed normally to Step 0.B.

### Step 0.B: Main Worktree Guard (new sprint only)

This command *creates* a sprint worktree, so it must run in the main worktree only. Reject if already inside an isolated worktree:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
if [ -z "$PLUGIN_ROOT" ] || [ ! -f "$PLUGIN_ROOT/scripts/worktree-helpers.sh" ]; then
  echo "ERROR: CLAUDE_PLUGIN_ROOT not found. Verify the plugin cache path." >&2
  exit 1
fi
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"
astra_ensure_main_worktree || exit 1
```

### Step 1: Confirm Sprint Number, Sprint Name, and Mode

Parse from `$ARGUMENTS`:
- **Sprint number** (optional): If not provided, scan existing directories in `docs/sprints/` matching the `sprint-{N}-{name}/` pattern (e.g., `sprint-1-auth/`, `sprint-2-workspace/`) to determine the next number.
- **Sprint name** (optional): The primary blueprint/feature name for this sprint.
- **`--auto`** (optional flag): If present, set `AUTO_MODE=1` and proceed to Step 5 (Auto Continue) after scaffolding. Without this flag, the skill stops at Step 4 (Output Sprint Planning Guide) as before.
- **`--max-iter=N`** (optional, only meaningful with `--auto`): max self-improving iteration count for the test loop (1 ≤ N ≤ 10). If `--auto` is set but `--max-iter` is missing, ask the user **once** via `AskUserQuestion` (default 3).

**Directory name format**: `sprint-{N}-{sprint-name}/` (e.g., `sprint-1-auth/`, `sprint-2-payment/`, `sprint-3-dashboard/`)

If the sprint name is not provided in `$ARGUMENTS`, ask the user for the primary feature/blueprint name. This name will be used as the directory suffix. Use kebab-case format (e.g., `auth`, `workspace`, `payment-dashboard`).

When scanning existing directories, extract the sprint number from directory names matching pattern `sprint-{N}-{name}` (e.g., `sprint-1-auth` → number `1`).

### Step 1.5: Sync `dev` Branch

The sprint worktree branches from `origin/dev` (or `origin/main` when missing) as base. Aligning the main worktree to `dev` first keeps the base always up to date.

1. **Check current branch**: `git branch --show-current`
2. **Preserve uncommitted changes**: If `git status --porcelain` shows changes, stash with `git stash --include-untracked -m "astra-sprint-init"`
3. **Switch and pull**: `git fetch origin dev && git checkout dev && git pull origin dev` (if `dev` is absent, fall back to `main`/`master`; if neither exists, stay on the current branch)
4. **Restore stash**: If stashed in step 2, `git stash pop`. On conflict, report to the user and abort.

### Step 1.6: Create Sprint Worktree

Create a new isolated worktree on the `feat/sprint-{N}-{sprint-name}` branch. All feature code and test deliverables are written inside it.

```bash
SPRINT_N="{confirmed sprint number}"
SPRINT_NAME="{confirmed sprint name}"

if ! out=$(astra_create_sprint_worktree "$SPRINT_N" "$SPRINT_NAME"); then
  echo "ERROR: sprint worktree creation failed" >&2
  exit 1
fi
IFS=$'\t' read -r SPRINT_BRANCH WT_PATH <<< "$out"
if [ -z "$WT_PATH" ] || [ ! -d "$WT_PATH" ]; then
  echo "ERROR: could not determine sprint worktree path. helper output: '$out'" >&2
  exit 1
fi
```

`astra_create_sprint_worktree` absorbs branch/slug/port conflicts, so use the returned `$SPRINT_BRANCH`·`$WT_PATH` *as-is* (it may differ from the desired name).

### Step 1.7: Write Worktree Port Env File

Create `.astra-worktree.env` inside the worktree. `/test-run` sources this file before starting the server to apply the sprint-specific ports.

```bash
# Default port base: 3000 (Node-stack default). Other stacks are derived automatically by the conversion formula inside the env file.
PORT_BASE_DEFAULT=3000
if ! PORT_BASE=$(astra_compute_port_base "$PORT_BASE_DEFAULT" "$SPRINT_N"); then
  echo "ERROR: could not find an available port base" >&2
  exit 1
fi

astra_write_worktree_env "$WT_PATH" "$SPRINT_N" "$SPRINT_NAME" "$PORT_BASE" || exit 1
echo "Sprint port base: $PORT_BASE (offset=$((PORT_BASE - PORT_BASE_DEFAULT)))"
```

The generated file contains per-framework values such as `ASTRA_PORT_BASE`, `PORT`, `VITE_PORT`, `SERVER_PORT`, `DJANGO_PORT`, `FASTAPI_PORT`. `/test-run` picks the value matching the detected stack to start the server.

### Step 1.8: Move into Sprint Worktree

From here on, deliverable writing and progress tracking happen inside the worktree:

```bash
cd "$WT_PATH"
```

> From this point on, the "current working directory" is `$WT_PATH`, and every docs/sprints/* file is committed onto the sprint branch.

### Step 2: Create Sprint Prompt Map

Create the file `$WT_PATH/docs/sprints/sprint-{N}-{sprint-name}/prompt-map.md`.

Scan `docs/blueprints/` for numbered directories matching the sprint name (or use the blueprint names provided by the user). Each blueprint becomes a feature in the prompt map. Do NOT analyze or carry over items from previous sprints.

```markdown
# Sprint {N} Prompt Map

## Sprint Goal
[Describe the business value to achieve in this sprint]

> **Worktree note**: Every task in this sprint runs inside `.astra-worktrees/sprint-{N}-{sprint-name}/`.
> New Claude Code sessions must be started from that path.

## Feature 1: {feature-name}

### 1.1 Blueprint Prompt
/blueprint {feature-name} --from-planner=docs/planner/{NNN}-{feature-name}

> The `/blueprint` skill takes `/service-planner` deliverables (auto-loaded when present) as input and writes a 10-standard-section blueprint to `docs/blueprints/{NNN}-{feature-name}/blueprint.md`.
> - **Included**: data flow, schema DDL, ER diagram, API JSON Schema, sequence diagrams, pseudocode logic, HITL Triggers
> - **Excluded**: executable implementation code, ORM annotations, framework-dependent expressions
> - Only asks 1-3 items that genuinely require human judgment (PK strategy, transaction boundary, external-dependency sync mode) automatically.
>
> **Numbering Rule**: Scan existing directories in `docs/blueprints/` to determine the next number. Use 3-digit zero-padded format (e.g., `001-`, `002-`).

### 1.2 DB Design Reflection Prompt
/feature-dev "Refer to docs/blueprints/{NNN}-{feature-name}/blueprint.md Section 3 (Data Model) and reflect those tables/columns/indexes/FK relationships into docs/database/database-design.md, including the ERD and FK relationship summary.

The blueprint is the single source of truth — do not change schema decisions, do not add columns not in the blueprint, do not rename. If you find a real inconsistency, stop and report instead of guessing.

HITL Guard: Before asking the user any question, first check Section 10 (HITL Triggers) of the blueprint. Only ask the user when the decision matches T1-T4 triggers (business decisions without a clear answer in the blueprint, security/permission choices, external dependency choices, destructive changes). For everything else, follow the blueprint and proceed automatically.

Do not modify any application code yet."

### 1.3 Test Case Prompt
/feature-dev "Based on docs/blueprints/{NNN}-{feature-name}/blueprint.md Section 9 (Test Strategy) and Section 9.1 (Required Test Cases), write test cases to docs/tests/test-cases/sprint-{N}/{feature-name}-test-cases.md.

Use Given-When-Then format. Cover: (a) Section 5.1 happy path, (b) Section 5.2 exception paths, (c) Section 2.3 business rules, (d) Section 7 error policy items. Include unit, integration, and edge cases.

HITL Guard: Section 10 (HITL Triggers) of the blueprint defines when to ask the user. Outside those triggers, derive test cases directly from the blueprint without asking. If a test case requires a decision not in the blueprint and not in Section 10, default to the most conservative coverage and note it as TODO instead of pausing.

Do not modify any application code yet."

### 1.4 Implementation Prompt
/feature-dev "Strictly follow docs/blueprints/{NNN}-{feature-name}/blueprint.md and docs/database/database-design.md to implement the feature. Write code that matches: Section 3 (DDL → ORM entities), Section 4 (API contract → controllers/DTOs), Section 5 (sequence diagrams → service orchestration), Section 6 (pseudocode → real implementation), Section 7 (error policy → exception handlers), Section 8 (non-functional → middleware/security config).

Write tests referencing docs/tests/test-cases/sprint-{N}/{feature-name}-test-cases.md. Once implementation is complete, run all tests and report results to docs/tests/test-reports/.

HITL Guard (important): The blueprint's Section 10 (HITL Triggers) tells you exactly when to ask the user during implementation. The four triggers are T1 (business decisions without a clear blueprint answer), T2 (security/permission policy choices), T3 (external dependency/3rd-party introduction), T4 (destructive changes like DROP/RENAME or public API signature change). Outside those triggers, do not ask — apply the blueprint as written and follow coding conventions.

Specifically do NOT ask the user about: variable/function names, code formatting, log levels, file layout, import order, DTO/Entity split, fine-grained HTTP status codes — those follow project conventions automatically. Waking the user too often defeats the automation."

## Feature 2: {feature-name}
{Repeat with the same structure as above}

---

## At Sprint End (after all features are implemented)

### Z.1 Integration Test
/test-run

> Boots the server using the sprint-specific ports in `.astra-worktree.env` and runs tests.
> When the tests finish, the server processes on those ports are also cleaned up automatically.

### Z.2 Merge to dev
/pr-merge

> Merges the sprint branch into dev and removes the worktree. The user is automatically returned to the main worktree (dev).
```

### Step 2.5: Create Sprint Progress Tracker

Read the prompt map created in Step 2 (`docs/sprints/sprint-{N}-{sprint-name}/prompt-map.md`) and extract feature names from `## Feature {#}: {name}` headers (where `{#}` is the feature ordinal, e.g., 1, 2, 3).

Create the `docs/sprints/sprint-{N}-{sprint-name}/progress.md` file:

```markdown
# Sprint {N} Progress Tracker

## Sprint Information
- **Sprint Number**: {N}
- **Sprint Name**: {sprint-name}
- **Sprint Branch**: feat/sprint-{N}-{sprint-name}
- **Worktree**: .astra-worktrees/sprint-{N}-{sprint-name}/
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

### Step 3.5: Commit Sprint Scaffolding

Commit the 3 generated sprint documents (`prompt-map.md`, `progress.md`, `retrospective.md`) to the sprint branch. This keeps them separate from later feature commits and makes tracking easy at merge time.

```bash
git add "docs/sprints/sprint-${SPRINT_N}-${SPRINT_NAME}/"
git commit -m "chore: scaffold sprint ${SPRINT_N} (${SPRINT_NAME})"
```

Do not push to remote — the push is bundled with the first feature commit or with `/pr-merge`.

### Step 4: Output Sprint Planning Guide

```
## Sprint {N} Initialization Complete

### Worktree
- Path: {WT_PATH}
- Branch: {SPRINT_BRANCH}
- Port base: {PORT_BASE}
- env file: {WT_PATH}/.astra-worktree.env

### Generated Files (in worktree)
- docs/sprints/sprint-{N}-{sprint-name}/prompt-map.md (prompt map)
- docs/sprints/sprint-{N}-{sprint-name}/progress.md (progress tracker)
- docs/sprints/sprint-{N}-{sprint-name}/retrospective.md (retrospective template)

### Next Steps
1. cd {WT_PATH}
2. Run Feature 1.1 ~ 1.4 of the prompt-map above in order (design → DB → tests → implementation)
3. After every feature is done: /test-run → /pr-merge

> **Multi-session note**: New Claude Code sessions must be started from {WT_PATH}.
> The main worktree (dev) may have other sprint work in progress.

### Sprint Planning Procedure (1 hour, run inside worktree)
1. (10 min) Review AI analysis report
2. (20 min) Confirm business priorities with DE and agree on sprint goal
3. (20 min) Discuss prompt design direction per item + DSA shares design direction
4. (10 min) Finalize sprint backlog
```

> **Branch**: Without the `--auto` flag, stop here. With `--auto`, continue to **Step 5**.

---

### Step 5: Auto Continue (only if `--auto` flag is set)

After scaffolding finishes, run the following pipeline sequentially in unattended mode:

```
/test-scenario all → implementation (blueprint-based) → /test-run → (self-improvement loop on failure) → /pr-merge --auto → worktree auto-removed
```

**Default principles** (same as autorun):
- During the pipeline, do not call `AskUserQuestion` (the only exception is the one-time prompt in Step 1 when `--max-iter` is not provided).
- Each stage's success criterion is judged solely from *verifiable file/test results*.
- HITL fires only on true blockers (gh auth, merge conflict, Critical review issues).

#### Step 5.0: Pre-checks

1. **Verify the current worktree is the sprint worktree**: Steps 1.6/1.8 already created the worktree and cd'd in, so `$(pwd)` must equal `$WT_PATH`. Abort if not.
2. **Verify blueprints exist**: For every feature extracted from prompt-map.md, `docs/blueprints/[0-9][0-9][0-9]-{feature-name}/blueprint.md` must exist inside the worktree (or in the merged base branch).
   - Abort message when missing:
     ```
     ❌ --auto mode requires blueprints to be authored in advance.
        Missing blueprint: {feature-name}
        Fix: author the blueprint with /service-planner {feature-name} or /feature-dev, then re-run.
     ```
3. **Determine MAX_ITER**: Use the `--max-iter=N` argument. If absent, ask once via `AskUserQuestion` (options 1/3/5, default 3).

#### Step 5.1: Initialize progress tracking

Create todos via `TodoWrite`:
1. Step 5.2: generate test scenarios
2. Step 5.3: implementation (per feature)
3. Step 5.4: run integration tests
4. Step 5.5: self-improvement loop (on failure)
5. Step 5.6: run /pr-merge --auto
6. Step 5.7: final report

Iteration tracking variables:
- `MAX_ITER` = the N determined above
- `CURRENT_ITER` = 1
- `ITER_DIR` = `docs/sprints/sprint-{N}-{sprint-name}/iterations/`
- `mkdir -p "$ITER_DIR"`

#### Step 5.1.5: Silent Save Protocol (reusable shared pattern)

`--auto` mode accumulates a large amount of context per stage (file contents, test logs, code review output). **At the end of each major stage, persist the state to yaml, then apply the "reference-avoidance rule" and immediately proceed to the next stage**. No user intervention.

The manual `/compact` slash command is intentionally not used — Claude Code's system auto-compression triggers on its own as the context approaches the limit, and in the meantime the LLM avoids re-referencing large objects to minimize new token accumulation.

This protocol is invoked at the end of Step 5.2, end of 5.3, end of 5.4, end of 5.5 iteration, and end of 5.6.

##### 5.1.5.A Write the checkpoint file

At the end of each stage, update `$WT_PATH/docs/sprints/sprint-{N}-{sprint-name}/auto-state.yaml`:

```yaml
# auto-state.yaml — SSoT for sprint-init --auto resume
sprint:
  number: {N}
  name: {sprint-name}
  worktree_path: {WT_PATH}
  branch: feat/sprint-{N}-{sprint-name}
  port_base: {PORT_BASE}

iteration:
  max_iter: {MAX_ITER}
  current_iter: {CURRENT_ITER}

progress:
  completed_stages: [5.0, 5.1, 5.2, ...]   # list of stage numbers completed so far
  next_stage: 5.3                           # stage to jump to on resume
  next_stage_description: "Implementation (iteration 1 only)"

features:
  - name: {feature-name-1}
    blueprint: docs/blueprints/{NNN}-{feature-name-1}/blueprint.md
    status: pending | done | in-progress

scenarios:
  generated_dir: docs/tests/test-cases/sprint-{N}-{sprint-name}/
  files: [auth-test-cases.md, payment-test-cases.md, ...]   # filled after 5.2

implementation:
  entities_created: [User.java, Payment.java, ...]
  services_created: [...]
  controllers_created: [...]

last_test_result:
  passed: {N}
  total: {M}
  failed_tests: []
  log_excerpt: "..."   # last failure log essence, within 100 lines

last_iteration_classification: null | CODE_BUG | SPEC_GAP | DESIGN_MISALIGN | ENV_ISSUE
files_to_patch_next: []   # used on iteration 2+ entry (src/ files indicated by the summary)

merge:
  pr_url: null
  merge_success: null
  worktree_removed: null
```

##### 5.1.5.B Commit the checkpoint file (required)

Commit the state file to the sprint branch. **Skipping this step** causes the file to disappear in the following cases:
- Right after 5.6.A, `/pr-merge --auto`'s `git add -u` only stages *tracked* files → untracked `auto-state.yaml` is not included in the merge → it is removed together with the worktree.
- When `--resume` looks for the yaml from the main worktree, the yaml must exist in the merged dev.

```bash
git add "docs/sprints/sprint-${SPRINT_N}-${SPRINT_NAME}/auto-state.yaml"
git commit -m "chore: auto-state checkpoint after Stage ${X}"
```

> Since this commit occurs during `--auto` progress, the message is generated automatically. Push is handled in bulk by `/pr-merge --auto` or the next checkpoint, so it can be omitted here (however, if the user wants to `--resume` from another machine mid-way, push is needed).

##### 5.1.5.C Apply the reference-avoidance rule and auto-advance to the next stage

Right after writing/committing the checkpoint, lightly print the following one line and **immediately invoke the next stage**. Do not exit:

```
✅ Stage {X} complete → auto-advancing to Stage {Y} (state: docs/sprints/sprint-{N}-{sprint-name}/auto-state.yaml)
```

And just before entering the next stage, **the LLM must apply the following context-efficiency rule to itself**:

> ⚡ **Context-efficiency rule (at every auto-advance stage boundary)**
> - **Do not re-reference** the large objects loaded in the previous stage (entire test logs, browser snapshots, full contents of previously implemented files).
> - Single source of truth (SSoT): `auto-state.yaml` (+ on iteration resume, the `last_iteration_summary` file).
> - For files needed in the next stage, Read/Edit them **selectively** — do not re-read the full directory tree or the full blueprint.
> - This makes Claude Code's system auto-compression (triggered when nearing the context limit) work effectively and prevents mid-skill token explosion.

##### 5.1.5.D `--resume` mode (true-recovery only)

`--resume` is not invoked on the normal path. Use only on the following abnormal paths (see Step 0.A):

- The LLM lost in-flight variables after system auto-compression and could not auto-invoke the next stage
- The user intentionally stopped mid-way and is now continuing
- The skill execution terminated abnormally due to a crash or session end

Key points:
1. `auto-state.yaml` is the SSoT — even if variables vaporized due to context compression, this file restores everything
2. Jump directly to `progress.next_stage`
3. On iteration resume, additionally load only the `last_iteration_summary` file and the `files_to_patch_next` list

##### 5.1.5.E Idempotency

At every checkpoint, *fully overwrite* `auto-state.yaml`. Partial updates are forbidden — they can break inter-stage consistency. Always write the latest state snapshot as a whole.

Each checkpoint creates a new git commit (`chore: auto-state checkpoint after Stage X`). When the PR is merged, those commits are either squashed or merged as-is (depending on the user's git workflow).

> **Note**: This protocol is `--auto` mode only. Running sprint-init without `--auto` is unaffected.

#### Step 5.2: Generate test scenarios (Iteration 1 only)

Invoke `Skill('test-scenario', 'all')`. Scenarios are generated under `docs/tests/test-cases/sprint-{N}-{sprint-name}/` for every feature.

Success criterion: ≥ 1 scenario file exists.

##### 5.2.Z 💾 Silent Save

Immediately after Step 5.2 ends, **run the Step 5.1.5 Silent Save Protocol**:
- Record `completed_stages: [5.0, 5.1, 5.2]`, `next_stage: 5.3`, `scenarios.files: [...]` in `auto-state.yaml` + commit
- Apply the 5.1.5.C reference-avoidance rule (the full blueprint content loaded during scenario generation is no longer re-referenced)
- **Auto-advance to Step 5.3 immediately** — no exit / no user input

#### Step 5.3: Implementation (Iteration 1 only)

For each feature extracted from prompt-map.md, run sequentially:

1. Read blueprint.md and extract table definitions from the **Data Model section**
2. For each table, invoke `Skill('generate-entity', '{table-name}')` (or author the entity directly from the blueprint)
3. According to the **API spec section**, author the service/controller/repository layers
4. Auto-applied skills (`coding-convention`, `data-standard`, `code-standard`) fire on every Write/Edit.

Success criterion: every table definition and API endpoint in the blueprint is reflected in code under `src/` (or the project's standard location).

##### 5.3.Z 💾 Silent Save

Step 5.3 is the stage that accumulates the most context (multiple entity/service/controller generations). **Always run the 5.1.5 Silent Save Protocol**:
- Record `completed_stages: [..., 5.3]`, `next_stage: 5.4`, `implementation.{entities/services/controllers}_created: [...]` in `auto-state.yaml` + commit
- Apply the 5.1.5.C reference-avoidance rule (the full contents of just-generated entity/service/controller files are no longer re-referenced — the next stage is the test run and only file paths are needed)
- **Auto-advance to Step 5.4 immediately** — no exit / no user input

#### Step 5.4: Run integration tests

Invoke `Skill('test-run', '')`. Boots the server using the sprint-specific ports in `.astra-worktree.env`, runs tests, and cleans up the ports automatically on exit.

##### 5.4.Z 💾 Silent Save

`/test-run` accumulates large artifacts in the context (browser snapshots, console logs, network request logs). **Always run the 5.1.5 Silent Save Protocol**:
- Record `completed_stages: [..., 5.4]`, `last_test_result: { passed, total, failed_tests, log_excerpt }` in `auto-state.yaml` + commit
  - If tests pass → `next_stage: 5.6`
  - Tests failed + `CURRENT_ITER < MAX_ITER` → `next_stage: 5.5`
  - Tests failed + `CURRENT_ITER == MAX_ITER` → `next_stage: 5.7` (jump directly to the report)
- Abbreviate `log_excerpt` to the essence of the last failure log within 100 lines (do not embed the full log in the yaml)
- Apply the 5.1.5.C reference-avoidance rule (browser snapshots, full console logs, network requests are no longer re-referenced — carry only the `log_excerpt` from the yaml into the next stage)
- **Auto-jump to `next_stage` immediately** — no exit / no user input

#### Step 5.5: Self-improvement loop (on test failure)

**All tests pass** → proceed immediately to Step 5.6 (early exit).

**Failed** + `CURRENT_ITER < MAX_ITER`:

1. **Failure classification** (same pattern matching as autorun Stage 7.5.4 + `tester-persona` delegation as fallback):
   | Signal | Classification | Re-entry |
   |--------|----------------|----------|
   | TypeError, NullPointer, panic, `src/` in stack trace | `CODE_BUG` | Direct Patch (Edit src/ files, no sub-skill re-invocation) |
   | 404 Not Found, schema mismatch, behavior not in blueprint | `SPEC_GAP` | **abort** (blueprint fix required) |
   | UI failure such as screenshot diff, aria-label, contrast | `DESIGN_MISALIGN` | **abort** (UX fix required) |
   | ECONNREFUSED, port in use, db connection | `ENV_ISSUE` | **abort** (user intervention) |

2. **Direct Patch** (no sub-skill re-invocation — same principle as autorun Stage 7.5.5):
   - `CODE_BUG` case: directly Edit the `src/` files indicated by the summary. Re-invoking sub-skills such as new entity generation is forbidden.
   - Other classifications: abort.

3. **Clear abort message**:
   ```
   ❌ {classification} category — sprint-init --auto does not self-improve this category.

   {when SPEC_GAP}:
     A blueprint fix is required. sprint-init does not redraw blueprints.
     Two resolutions:
       (1) Manually edit docs/blueprints/{NNN}-{feature}/blueprint.md, then /pr-merge --auto
       (2) /autorun "{feature description}" --max-iter=N — the full pipeline that auto-patches blueprints too

   {when DESIGN_MISALIGN}:
     HTML planning screens (styles.css, SCR-*.html) need to be fixed.
     Resolution: re-run /service-planner then /pr-merge --auto, or use the /autorun full pipeline.

   {when ENV_ISSUE}:
     Environment/infrastructure problem — needs user diagnosis.
     Log: {log location}
   ```

3. **Write iteration summary**: `$ITER_DIR/iter-{CURRENT_ITER}-summary.md` (within 200 lines, same format as autorun).

4. `CURRENT_ITER += 1`.

##### 5.5.Z 💾 Silent Save (run between iterations)

**Inter-iteration context cleanup is mandatory**. Debug logs, previous patch attempts, and classification analyses accumulate, posing a high risk that the next iteration hits the token limit early. **Always run the 5.1.5 Silent Save Protocol**:
- Record in `auto-state.yaml`: `current_iter: {CURRENT_ITER}`, `last_iteration_classification: {classification}`, `files_to_patch_next: [{list of src/ file paths flagged by the summary}]`, `next_stage: 5.5` (or 5.4 — retry flow) + commit
- Also record the iteration summary path (`$ITER_DIR/iter-{CURRENT_ITER-1}-summary.md`) in `auto-state.yaml`'s `progress.last_iteration_summary` field (so the next iteration reads *only this summary file* on resume)
- **Strictly apply** the 5.1.5.C reference-avoidance rule — debug logs, classification analyses, and attempted-patch diffs from previous iterations are no longer re-referenced. Carry only the summary file and `files_to_patch_next` into the next iteration.
- **Resume immediately**: first read the summary file, Direct Patch the `files_to_patch_next` files, then re-invoke 5.4 (test-run) — no exit / no user input

> **Context-efficiency rule (on iteration re-entry)**: Read only `auto-state.yaml` and `last_iteration_summary`, then Edit the patch target files. **Do not** Read the full blueprint, planning docs, or src files from a previous iteration again.

**Failed** + `CURRENT_ITER == MAX_ITER`:
- Print: `❌ Max iterations ({MAX_ITER}) exhausted with unresolved failures — stopping without /pr-merge`
- Jump directly to Step 5.7 (report); **do not invoke `/pr-merge`**.

#### Step 5.6: PR merge (only when tests pass)

##### 5.6.A 💾 Pre-merge Silent Save (especially important)

Persist the state one more time just before the merge. `/pr-merge --auto` itself consumes additional context for PR creation, code review, issue fixes, and re-review — the lighter the entering context, the more stable.

**This save is stricter than others**: once pr-merge starts and merges, the worktree disappears, so `auto-state.yaml` must be included in a sprint branch commit so it is accessible from the main worktree after dev merge.

**Run the 5.1.5 Silent Save Protocol** with the following extra checks:

1. Record `completed_stages: [..., 5.5_passed]`, `next_stage: 5.6.B`, final `last_test_result` in `auto-state.yaml`
2. **Always git commit** (5.1.5.B rule — to prevent the accident where an untracked yaml disappears with the worktree):
   ```bash
   git add docs/sprints/sprint-${N}-${SPRINT_NAME}/auto-state.yaml
   git commit -m "chore: pre-merge checkpoint (Stage 5.6.A)"
   ```
3. Lightly print the following one line and **immediately auto-invoke Step 5.6.B**:
   ```
   ✅ Pre-merge save complete → invoking /pr-merge --auto (worktree will be removed)
   ```
4. Apply the 5.1.5.C reference-avoidance rule — previous iteration logs, full blueprint, and test outputs are no longer re-referenced. pr-merge works from git diff and PR metadata.

##### 5.6.B Invoke `/pr-merge --auto`

Invoke `Skill('pr-merge', '--auto')`.

`/pr-merge --auto` handles automatically:
- Commit the changes (confirmation prompts auto-approved)
- Create the PR
- Code review → issue fixes → re-review cycle (up to 3 times)
- Halt on remaining Critical issues (true HITL)
- Merge (final confirmation prompt auto-approved)
- **Auto-remove the worktree** + return to the main worktree (dev)

> Since sprint-init is running inside the sprint worktree, after the merge completes, /pr-merge removes the very worktree it is in. The user is automatically returned to the main worktree (dev) upon merge completion.

##### 5.6.C Record merge result in `auto-state.yaml`

Right after the worktree is removed, **in the main worktree** do the following:
1. `cd $(astra_main_worktree_root)` (it should already be the main worktree once the sprint worktree is removed, but specify it explicitly for safety)
2. Record the merge result (`pr_url`, `merge_success: true`, `worktree_removed: true`) into `docs/sprints/sprint-{N}-{sprint-name}/auto-state.yaml` (main worktree path)

> **Path note**: With the worktree removed, `auto-state.yaml` now lives in the *main worktree's* `docs/sprints/sprint-{N}-{sprint-name}/` (the file landed in dev via the sprint branch merge). If the path is missing in the main worktree (the sprint branch should have carried the file into dev), sync with `git pull origin dev` and verify again.

##### 5.6.D Final Silent Save — skipped, auto-advance

The Step 5.7 report is generally lightweight on context, so no separate silent save is needed. Since 5.6.C already recorded the merge result (pr_url, merge_success) in the yaml, Step 5.7 only needs to re-read that yaml — proceed directly to Step 5.7 with no exit / no user confirmation.

#### Step 5.7: Final report output

**Data source**: Re-read `auto-state.yaml` to fill the report values. To guard against the case where in-flight variables vaporized due to system auto-compression, do not rely on values left in context — use the state file as the single source of truth.

```
═══════════════════════════════════════════════════════
{✅ / ❌ / ⚠️} Sprint {N} --auto complete

🔁 Iterations: {iteration.current_iter}/{iteration.max_iter}
✅ Tests: {last_test_result.passed}/{last_test_result.total}
📦 Sprint Branch: feat/sprint-{N}-{sprint-name}
🌿 Worktree: {merge.worktree_removed ? "removed" : "preserved (kept due to failure)"}

📁 Deliverables:
  - Blueprint: docs/blueprints/[NNN]-*/blueprint.md
  - Sprint: docs/sprints/sprint-{N}-{sprint-name}/
  - Tests: docs/tests/test-cases/sprint-{N}-{sprint-name}/
  - Iteration summaries: docs/sprints/sprint-{N}-{sprint-name}/iterations/
  - Auto-run state: docs/sprints/sprint-{N}-{sprint-name}/auto-state.yaml

{merge.pr_url (on merge success)}
{If last_iteration_classification is set, summarize unresolved failures}
═══════════════════════════════════════════════════════
```

After the report is printed, preserve `auto-state.yaml` (for debug/reproduction). A new file is written in the next sprint.

---

## Notes

- Existing sprint files are not overwritten.
- The prompt map is filled in collaboratively by VA and PE during the Planning meeting.
- Once work, tests, and merge inside the sprint worktree complete, `/pr-merge` auto-removes the worktree. If the worktree remains due to a conflict or interruption, the user resolves it and re-invokes `/pr-merge` to continue.
- The user must not edit `.astra-worktree.env` — `/test-run` sources it automatically.
- **Caveats when using `--auto` mode**:
  - The blueprint must be prepared in advance (sprint-init does not create blueprints).
  - When classified as `SPEC_GAP` / `DESIGN_MISALIGN`, abort without auto-merge — blueprint/UX fixes require user judgment.
  - For full-stack auto-generation starting from planning, use `/autorun {feature description}` instead.
