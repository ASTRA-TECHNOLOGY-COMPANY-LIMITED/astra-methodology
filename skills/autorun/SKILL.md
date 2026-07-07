---
name: autorun
description: "Mostly-unattended ASTRA pipeline: /service-planner → /blueprint → /sprint-init → /test-scenario → implementation → /test-run → /pr-merge --auto → worktree removal, self-iterating up to N times until tests pass. HITL pauses only for the max-iteration count (start), the promotion target (dev/staging/skip), and true blockers (gh auth, merge conflicts, Critical review issues). Use when a single command should drive a feature end-to-end from planning to merged PR."
argument-hint: "[feature description] [--max-iter=N] (default 3 if N omitted; 1 means single pass)"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task, TodoWrite, Skill, AskUserQuestion
---

# ASTRA Mostly-Autonomous Execution (`/autorun`)

**Auto-executes** planning → design → blueprint → sprint plan → implementation → tests without user input, then runs `/pr-merge --auto` until the moment it would block. The pipeline has one routine HITL pause near the end (Stage 8.2 — promotion-target prompt: dev / staging / skip); beyond that, only true blockers stop execution.

> **🌐 LANGUAGE RULE**: Before executing this skill, read the project's `CLAUDE.md` and check the `## Language` section. If the project language is NOT Korean (`ko`), translate ALL user-facing output and propagate the language preference to all sub-skills invoked.

## Core principles

1. **Mostly-unattended execution (minimal interaction during pipeline)**: do not call `AskUserQuestion` while the pipeline is running, except at two well-defined points. **Exception 1**: at the start, if the `--max-iter` argument is absent, ask once for the *max iteration count*. **Exception 2**: at Stage 8.2, `/pr-merge --auto` always prompts for the *promotion target* (dev / staging / skip) — the deployment surface choice has no safe unattended default, so this HITL fires even under `--auto`. After the user answers, the pipeline continues automatically through cleanup. Every other decision is an automatic default.
2. **Sequential**: each stage must succeed before the next starts. Do not parallelize (because of document dependencies).
3. **Self-improving loop**: on Stage 7 (test) failure, do not stop immediately — classify the failure cause and *re-enter from the appropriate stage*. Repeat up to N times; on all-pass, exit immediately (early exit). After 5 debug attempts on the last iteration without success, stop.
4. **Context efficiency**: hand off between iterations using only `iter-{i}-summary.md` (≤ 200 lines). Do not reload the entire blueprint / planning documents each iteration.
5. **Full auto merge**: when all tests pass, automatically invoke `/pr-merge --auto` to perform PR creation, code review, merge, and worktree removal end-to-end. **However, on true blockers** (missing gh authentication, merge conflicts, Critical review issues), `/pr-merge` stops via HITL just like in normal mode.
6. **Idempotent**: on re-execution after a mid-failure, recognize all completed stages and iterations, and resume from the last incomplete point.
7. **Goal-Driven**: each stage has a verifiable success criterion (file existence, test pass).

## Input

```
/autorun {feature description} [--max-iter=N]
```

**Examples**:
- `/autorun build a user-auth feature` (interactively asks for N, default 3)
- `/autorun payment subscription system --max-iter=5` (unattended, up to 5 iterations)
- `/autorun student attendance feature --max-iter=1` (single pass, iteration disabled)

**Meaning of `--max-iter`**: the *maximum* number of plan→implement→test cycles. When tests pass it exits immediately (early exit), so it does not always fill N. Recommended value is 3 (1 = single-pass, 5+ cost explodes).

## Stage 0: Argument parsing and feature name determination

### 0.1 Extract the feature description
Take the feature description from `$ARGUMENTS`. If empty, print the following message and stop:
```
❌ A feature description is required.
Usage: /autorun {feature description}
Example: /autorun student attendance system
```

### 0.2 Auto-generate the feature name (slug)
- Translate non-English text to English meaning (LLM decides directly)
- Convert to kebab-case (e.g., "student attendance" → `student-attendance`)
- If too long, abbreviate to 1–2 key words
- Save as `FEATURE_SLUG` and persist: `astra_state_set FEATURE_SLUG "$FEATURE_SLUG" "autorun-{FEATURE_SLUG}"` (explicit scope — see 0.5.2 protocol)

### 0.3 Initialize progress tracking
Create the following todos via `TodoWrite`:
1. Stage 0.5: decide the max iteration count
2. Stage 1: planning + HTML mockup screens (/service-planner)
3. Stage 1.5: planning validation (planner-reviewer)
4. Stage 2.5: design token validation (design-token-validator) — target: mockup styles.css
5. Stage 3: blueprint authoring (blueprint.md)
6. Stage 3.5: blueprint validation (blueprint-reviewer)
7. Stage 4: sprint plan (/sprint-init)
8. Stage 5: test scenarios (/test-scenario) — TDD: before implementation
9. Stage 6: implementation (/generate-entity + blueprint-based)
10. Stage 7: test execution (/test-run)
11. Stage 7.5: iteration loop (re-enter on failure, early exit on pass)
12. Stage 8: /pr-merge --auto auto-invocation (PR creation, code review, merge, worktree removal)
13. Stage 9: final report (includes merge result)

## Stage 0.5: Decide the max iteration count (N)

### 0.5.1 Argument parsing
Find the `--max-iter=N` pattern in `$ARGUMENTS` (regex: `--max-iter=([0-9]+)`).

- **Argument found**: adopt N immediately (validate 1 ≤ N ≤ 10; if out of range, clamp + warn).
- **Argument missing**: call `AskUserQuestion` *exactly once*:
  - Question: "Enter the max iteration count (how many times to auto-repeat the plan→test cycle?)"
  - Options: `1 (single pass)` / `3 (Recommended — default)` / `5 (relentless self-improvement)` / `enter manually`
  - No response / timeout: **3** is auto-adopted.

### 0.5.2 Initialize iteration context variables — state-file protocol (MANDATORY)

Shell variables do NOT persist between separate Bash tool invocations, and this pipeline spans dozens of them. All pipeline state lives in the shared state file managed by `worktree-helpers.sh`:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"
astra_state_load "autorun-{FEATURE_SLUG}"    # start of EVERY Bash block in this skill
```

**State scope**: autorun's cwd moves between the main worktree and the sprint worktree, so NEVER rely on the default (cwd-derived) state scope. Every `astra_state_set`/`astra_state_load`/`astra_state_clear` call in this skill passes the explicit scope `autorun-{FEATURE_SLUG}` — where `{FEATURE_SLUG}` means you write the actual slug text from Stage 0.2 into the command (e.g., `astra_state_load "autorun-student-attendance"`). You know the slug from the conversation; it never needs to be read back from a file.

**Canonical pipeline variables** — set each exactly once at its capture point, persist immediately with `astra_state_set KEY "$VALUE" "autorun-{FEATURE_SLUG}"`, and never re-guess it later. Placeholders like `{NNN}`, `{N}`, `{feature-slug}` in the snippets below always mean these captured variables — substitute the variable (or the literal slug for the scope argument), never leave literal braces in an executed command:

| Variable | Captured at | How |
|---|---|---|
| `FEATURE_SLUG` | Stage 0.2 | the kebab-case slug (single canonical name — do not use `feature_slug`/`{feature-slug}` variants for new vars) |
| `MAX_ITER` / `CURRENT_ITER` | Stage 0.5 | from argument/HITL; `CURRENT_ITER=1` |
| `PLANNER_DIR` | Stage 1.3 | `find docs/planner -maxdepth 1 -type d -name "[0-9][0-9][0-9]-${FEATURE_SLUG}" \| sort \| tail -1` (find, not `ls glob` — an unmatched glob in zsh errors before `2>/dev/null` can suppress it) |
| `BLUEPRINT_DIR` / `NNN` | Stage 3 | `find docs/blueprints -maxdepth 1 -type d -name "[0-9][0-9][0-9]-${FEATURE_SLUG}" \| sort \| tail -1`; `NNN=$(basename "$BLUEPRINT_DIR" \| cut -d- -f1)` |
| `BLUEPRINT_PATH` | Stage 3 | `$BLUEPRINT_DIR/blueprint.md` (verify with `[ -f ]`) |
| `WT_PATH` | Stage 3.5/4 | worktree discovery snippet |
| `SPRINT_N` | Stage 4 | from the worktree branch: `git -C "$WT_PATH" branch --show-current \| sed -E 's\|^[^/]*/sprint-([0-9]+)-.*$\|\1\|'` |
| `SPRINT_DIR` / `ITER_DIR` / `TEST_DIR` | Stages 4/5 | paths inside the worktree |
| `MERGE_RESULT` | Stage 8.3 | `success` / `fail` (exact strings — Stage 9 branches on `success`) |

If any variable is empty after `astra_state_load`, re-derive it with the "How" command above before use — never proceed with an empty variable into a destructive command. Run `astra_state_clear` at the end of Stage 9.

### 0.5.3 Output to the user
```
🔁 ASTRA Autorun starting — max {N}-iteration mode
   Feature: {feature-slug}
   Iteration 1/{N} starting...
```

## Stage 1: Auto-execute planning (`/service-planner`)

### 1.1 Auto-decision defaults
Read `/service-planner`'s SKILL.md, but **bypass every user-prompt step with auto defaults**:

| Decision point | Auto default |
|---|---|
| Planning mode (new/improve) | `docs/planner/` empty → **new**; existing directory → **improve** |
| Multi-actor selection | **auto-select all** derived actors |
| Whether to run persona interviews | **always run** |
| Multi-idea selection | **auto-select top 5** by Impact score (or all if fewer than 5) |
| Proceed confirmation (Y/N) | **always Y** |
| Language selection | follow the `## Language` section in the project `CLAUDE.md`; default to Korean if absent |

### 1.2 Execute
Call `/service-planner {feature description}` while explicitly applying the defaults above. Invoke via the `Skill` tool.

### 1.3 Success criteria
All 6 files below must exist:
```
docs/planner/{NNN}-{feature-slug}/
├── market-analysis.md
├── interview-report.md
├── requirements-definition.md
├── usecase-definition.md
├── ia-screen-design.md
└── feature-definition.md
```

If any are missing, **STOP** + report the error.

Save the generated directory path in the `PLANNER_DIR` variable.

## Stage 1.5: Planning validation (auto, non-blocking)

```
Task(planner-reviewer, "validate {PLANNER_DIR}")
```

Record validation results to the progress log, but **proceed to the next stage even if there are P0 issues** (unattended-execution principle). P0 issues are emphasized in the final report.

## Stage 2.5: Design token validation (auto, non-blocking)

Validate token compliance against the HTML mockup screens generated by `/service-planner` (`{PLANNER_DIR}/styles.css`, `{PLANNER_DIR}/SCR-*.html`, `{PLANNER_DIR}/index.html`).

```
Task(design-token-validator, "validate {PLANNER_DIR} — check that styles.css, SCR-*.html, index.html do not bypass var(--*) tokens with hardcoded colors/sizes")
```

Record P0 issues in the final report and proceed.

## Stage 3: Auto-author the blueprint (`/blueprint` skill delegation)

Before v5.1+, the blueprint was authored inline, but it has been separated into the dedicated `/blueprint` skill. autorun simply invokes that skill in `--auto` mode.

### 3.1 Invoke the blueprint skill

```
Skill('blueprint', '{feature-slug} --auto --from-planner={PLANNER_DIR}')
```

- `--auto`: skip HITL (PK strategy, transaction boundary, external-call sync mode — all apply conservative defaults: auto-inc PK / single transaction + Outbox / synchronous + Circuit Breaker)
- `--from-planner`: auto-load `/service-planner` deliverables (`PLANNER_DIR`) and derive the blueprint body from the 6 deliverables

The invocation produces:
- `docs/blueprints/{NNN}-{feature-slug}/blueprint.md` — 10 standard sections (including Section 10 HITL Triggers)
- `docs/blueprints/{NNN}-{feature-slug}/review.md` — auto-result of blueprint-reviewer (performed inside the skill)

Save the blueprint path in the `BLUEPRINT_PATH` variable.

### 3.2 Blueprint standard sections (auto-authored by the `/blueprint` skill)

1. **Overview** (purpose, background, scope, KPI)
2. **Functional spec** (user scenarios, business rules)
3. **Data model** (ER diagram, table DDL — complies with the Korean public data standard)
4. **API spec** (endpoints, request/response JSON Schema, error codes)
5. **Sequence diagrams** (Happy / Error path — Mermaid)
6. **Business logic design** (pseudocode — not executable code)
7. **Error handling policy**
8. **Non-functional requirements** (performance, security, availability)
9. **Test strategy overview**
10. **HITL Triggers (for implementation phase)** — `/feature-dev` consults this in step 5 to ask the user only on *essential* decisions

### 3.3 Auto-applied skill triggers
While the `/blueprint` skill authors DDL, the `data-standard` skill and PostToolUse hook auto-fire to validate TB_/TC_ prefixes, _YMD/_DT suffixes, and forbidden words (autorun does not invoke them separately).

### 3.4 Collect validation results (formerly Stage 3.5)

`Task(blueprint-reviewer, ...)` is auto-run inside the `/blueprint` skill, so autorun does not invoke it separately. Read `review.md` and record only the P0-issue count in the final report; then proceed.

```bash
# Parse the authoritative machine-readable tail line the reviewer emits
# (a naive `grep -c "P0"` counts prose mentions like "P0: none" as issues).
P0_ISSUES=$(grep -oE 'ASTRA_REVIEW_RESULT: score=[0-9]+ verdict=(PASS|FAIL) p0=[0-9]+' \
  "docs/blueprints/${NNN}-${FEATURE_SLUG}/review.md" 2>/dev/null \
  | grep -oE 'p0=[0-9]+' | cut -d= -f2 | tail -1)
P0_ISSUES=${P0_ISSUES:-unknown}
echo "blueprint-reviewer P0 issues: $P0_ISSUES"   # 'unknown' if the tail line is missing — report as unverified, not 0
```

### 3.5 Blueprint auto-worktree (verify the worktree-first creation)

`/blueprint --auto` performs the following internally (v5.10+ worktree-first order):
1. **Step 1.5**: branch / location guards (non-standard branch aborts; secondary blueprint reuses worktree).
2. **Step 1.6**: delegates to `/sprint-init --scaffold-only` to create the sprint worktree.
3. **Step 1.7**: cd's into the worktree *within the skill execution*.
4. **Steps 2–5**: authors + reviews the blueprint *inside the worktree*.
5. **Step 6**: commits the blueprint to the **sprint branch** (`feat/sprint-N-slug`), NOT to dev. The blueprint reaches dev only via `/pr-merge` at sprint end.

The parent cwd of autorun remains the main worktree after `/blueprint` returns (skill-to-skill cd does not propagate). autorun must explicitly cd to enable the unattended downstream stages.

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"
astra_state_load "autorun-{FEATURE_SLUG}"   # write the literal slug (0.5.2 protocol)
[ -n "${FEATURE_SLUG:-}" ] || { echo "ERROR: FEATURE_SLUG unresolved — check the state scope slug" >&2; exit 1; }
# v5.10+ — blueprint is on the sprint branch, not dev, so verify the commit across all refs (current-branch git log is empty by design).
if [ -z "$(git log --all -1 --oneline -- "docs/blueprints/{NNN}-{feature-slug}/" 2>/dev/null)" ]; then
  echo "WARN: blueprint commit not detected on any branch — /blueprint may have failed."
fi

# Discover the worktree /blueprint Step 1.6 created. Anchored match handles bare and collision-suffixed ("-2") branches, not unrelated slugs.
WT_PATH=$(git worktree list --porcelain 2>/dev/null | awk -v slug="${FEATURE_SLUG}" '
  /^worktree / { p=$2 }
  /^branch refs\/heads\// {
    b=$2; sub("refs/heads/", "", b)
    if (b ~ "^feat/sprint-[0-9]+-" slug "(-[0-9]+)?$") { print p; exit }
  }
')

if [ -z "$WT_PATH" ]; then
  # Fallback: glob — include both bare and collision-suffixed dirs, pick most recent
  WT_PATH=$(ls -td .astra-worktrees/sprint-*-${FEATURE_SLUG} .astra-worktrees/sprint-*-${FEATURE_SLUG}-* 2>/dev/null | head -1)
fi

if [ -n "$WT_PATH" ] && [ -d "$WT_PATH" ]; then
  echo "✅ Sprint worktree created by /blueprint Step 1.6 (worktree-first, v5.10+): $WT_PATH"
  WORKTREE_READY=1
else
  echo "⚠️  /blueprint did not create a worktree — Stage 4 fallback will create it."
  WORKTREE_READY=0
fi
astra_state_set WT_PATH "$WT_PATH" "autorun-{FEATURE_SLUG}"
astra_state_set WORKTREE_READY "$WORKTREE_READY" "autorun-{FEATURE_SLUG}"
```

## Stage 4: Sprint plan (idempotent re-entry)

### 4.1 Auto-decision defaults

| Decision point | Auto default |
|---|---|
| Sprint number | scan `docs/sprints/` and pick the next number |
| Feature name | use the feature slug automatically |
| Blueprint linkage | auto-map Stage 3's `BLUEPRINT_PATH` |
| Proceed confirmation | **always Y** |

### 4.2 Execute (idempotent — skip worktree creation if already done)

> **v5.10+ change**: `/blueprint` Step 1.6 already creates the sprint worktree, so this stage is an **idempotent re-entry** — it invokes `/sprint-init` only when the worktree was NOT created by `/blueprint` (rare; the non-standard-branch case aborts `/blueprint` earlier and never reaches Stage 4), and **always performs the explicit cd** into the worktree.

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"
astra_state_load "autorun-{FEATURE_SLUG}"   # restores FEATURE_SLUG (persisted at 0.2) for the ${FEATURE_SLUG} expansions below
[ -n "${FEATURE_SLUG:-}" ] || { echo "ERROR: FEATURE_SLUG unresolved — check the state scope slug" >&2; exit 1; }
if [ "$WORKTREE_READY" = "1" ]; then
  echo "ℹ️  Worktree already created by /blueprint Step 1.6 — using $WT_PATH"
  # Sprint files (prompt-map Variant B, progress.md, retrospective.md, .astra-worktree.env) already exist from the delegated --scaffold-only call.
else
  echo "🌿 Stage 4 fallback — invoking /sprint-init explicitly (worktree was not auto-created)"
  # --scaffold-only: blueprint already exists from Stage 3; keeps prompt-map Variant B consistent.
  Skill('sprint-init', '{feature-slug} --scaffold-only')
  # Re-discover the path (do not trust cwd propagation from the Skill call)
  WT_PATH=$(git worktree list --porcelain 2>/dev/null | awk -v slug="${FEATURE_SLUG}" '
    /^worktree / { p=$2 }
    /^branch refs\/heads\// {
      b=$2; sub("refs/heads/", "", b)
      if (b ~ "^feat/sprint-[0-9]+-" slug "(-[0-9]+)?$") { print p; exit }
    }
  ')
  WORKTREE_READY=1
fi

# Always perform explicit cd — autorun is unattended, so it must move into the worktree itself
if [ -z "$WT_PATH" ] || [ ! -d "$WT_PATH" ]; then
  echo "ERROR: cannot resolve sprint worktree path after Stage 4" >&2
  exit 1
fi
cd "$WT_PATH" || {
  echo "ERROR: cd into $WT_PATH failed" >&2
  exit 1
}
echo "📂 autorun is now inside the sprint worktree: $(pwd)"

# Capture sprint number from the worktree branch and persist core paths.
SPRINT_N=$(git branch --show-current | sed -E 's|^[^/]*/sprint-([0-9]+)-.*$|\1|')
astra_state_set SPRINT_N "$SPRINT_N" "autorun-${FEATURE_SLUG}"
astra_state_set WT_PATH "$WT_PATH" "autorun-${FEATURE_SLUG}"
astra_state_set SPRINT_DIR "docs/sprints/sprint-${SPRINT_N}-${FEATURE_SLUG}" "autorun-${FEATURE_SLUG}"
astra_state_set ITER_DIR "docs/sprints/sprint-${SPRINT_N}-${FEATURE_SLUG}/iterations" "autorun-${FEATURE_SLUG}"
# The iteration loop (7.5.1) writes into ITER_DIR — nobody else creates it
# (--scaffold-only exits before sprint-init Step 5's mkdir), so create it here:
mkdir -p "docs/sprints/sprint-${SPRINT_N}-${FEATURE_SLUG}/iterations"
```

> **v5.0+ important**: All Stage 5+ work happens inside the worktree — the autorun cwd must be `.astra-worktrees/sprint-<N>-<feature-slug>/` by the end of 4.2 (the explicit cd above guarantees this).

### 4.3 Success criteria + verify worktree state
```
.astra-worktrees/sprint-{N}-{feature-slug}/
├── .astra-worktree.env          # port base
└── docs/sprints/sprint-{N}-{feature-slug}/
    ├── prompt-map.md
    ├── progress.md
    └── retrospective.md
```

```bash
# Verify we landed inside the worktree
if [[ "$(pwd)" != *"/.astra-worktrees/sprint-"* ]]; then
  echo "ERROR: not inside a sprint worktree after Stage 4. cwd: $(pwd)" >&2
  exit 1
fi
```

Save `SPRINT_DIR` as the path inside the worktree (`docs/sprints/sprint-{N}-{feature-slug}/`). All subsequent stages (5/6/7) execute from this directory.

## Stage 5: Test scenarios (`/test-scenario`) — TDD: before implementation

> **Order change (v5.x+)**: write the test scenarios *before* implementation to follow TDD. The blueprint spec is encoded as tests first, and implementation is then made to satisfy them. The scenarios use the blueprint as SSoT; scanning route/endpoint code that does not exist yet will naturally miss (normal).

### 5.1 Auto-decision defaults

| Decision point | Auto default |
|---|---|
| Input blueprint / sprint | auto-pass the paths from Stages 3 and 4 |
| Scenario depth | **standard** (happy path + major edge cases) |
| Given-When-Then format | **enabled** |
| Proceed confirmation | **always Y** |

### 5.2 Execute
Call `Skill('test-scenario', '{feature-slug}')`.

### 5.3 Success criteria
```
docs/tests/test-cases/sprint-{N}-{feature-slug}/
└── (test-case files)
```

Save in the `TEST_DIR` variable.

## Stage 6: Implementation (`/generate-entity` + blueprint-based)

Implement based on the blueprint's data model and API spec sections, **shaped to satisfy the test scenarios written in Stage 5**:

1. **Auto-generate entities**: extract table definitions from the blueprint → for each table call `Skill('generate-entity', '...')` or `/generate-entity`.
2. **Author services/controllers**: author the service/controller/repository layers by referencing the blueprint's API spec + the Given-When-Then from the test scenarios together.
3. **Auto-applied skill triggers**: on every Write/Edit, `coding-convention`, `data-standard`, and `code-standard` are auto-applied.

### 6.2 HITL guard (autorun unattended-execution principle)

When you hit a decision point during implementation, first check the blueprint's **Section 10 (HITL Triggers)**:

- If the decision is listed in Section 10 (e.g., HITL-02 security algorithm, HITL-03 external dependency) but the blueprint body has no answer → autorun **STOP + report to user**. Proceeding unattended is risky.
- If the decision is not in Section 10, or the answer is specified in the blueprint → **proceed automatically**. Do not ask the user.
- If the decision matches the Section 10 Anti-HITL list (variable names, formatting, log level, etc.) → **proceed automatically** per the coding convention.

> In autorun mode, *minimize* `AskUserQuestion` under all circumstances (the initial max-iter ask is the only one). When a Section 10 trigger fires, halt and clearly hand off to the user.

### 6.3 Success criteria (machine-verifiable — do not self-assess from memory)
Run ALL of these checks and record command + exit code; Stage 6 passes only when every check passes:

1. **File existence**: for each table in the blueprint Section 3.2, verify an entity file exists (`ls` / `find` — count must match); verify service/controller files exist for each Section 4.1 endpoint group.
2. **Compile/typecheck** (first configured match): `tsconfig.json` → `npx tsc --noEmit`; `build.gradle*` → `./gradlew compileJava compileTestJava`; `pom.xml` → `mvn -q compile`; Python → `python -m compileall src` (or `ruff check` if configured). Exit code non-zero → Stage 6 is NOT complete: fix within Stage 6 before entering Stage 7. If no compiler/checker is configured, record "typecheck: not configured".
3. Never claim "implementation complete" without printing the check outputs above in this session.

On unresolvable failure, **STOP** + request user intervention.

## Stage 7: Test execution (`/test-run`)

### 7.1 Auto-decision defaults

| Decision point | Auto default |
|---|---|
| Test environment | **cmux browser** (if available), fallback: **Chrome MCP** |
| Auto-debug retry | **enabled** (up to 5 times) |
| Proceed confirmation | **always Y** |

### 7.2 Execute
Call `Skill('test-run', '{feature-slug}')`.

### 7.3 Success criteria (anchored on the machine-parseable result line)
- A test report file exists: `docs/tests/test-reports/sprint-{N}-{feature-slug}/`
- `/test-run` output contains the line `ASTRA_TEST_RESULT: PASS|FAIL passed=N failed=N total=N`. **Parse pass/fail from THAT line only** — never infer "all tests pass" from prose or from the report's narrative sections.
- If the `ASTRA_TEST_RESULT:` line is absent from the `/test-run` output, treat the run as **FAIL** (classification `ENV_ISSUE` candidate) — a missing result line means the tests were not verifiably executed.

### 7.4 Result branching
- **`ASTRA_TEST_RESULT: PASS`** → enter Stage 7.5's *early-exit path* → go to Stage 8.
- **`ASTRA_TEST_RESULT: FAIL` (or line absent) after 5 auto-debug attempts** → enter Stage 7.5's *iteration-decision path*.

## Stage 7.5: Iteration loop (self-improvement)

### 7.5.1 End-of-iteration handling (always run at the end of every iteration)

At the end of every iteration: snapshot the baseline file list at iteration start and diff it at iteration end to track changed deliverables (do **not** rely on git diff — autorun does not commit mid-pipeline), then author `{ITER_DIR}/iter-{CURRENT_ITER}-summary.md` (≤ 200 lines) and append the iteration record to `ITER_HISTORY`. The summary is the sole hand-off context to the next iteration (context-efficiency rule 4).

Baseline-snapshot bash (BSD/GNU-portable), the diff command, and the full summary template: see [references/iteration-mechanics.md](references/iteration-mechanics.md). Read it at the start/end of each iteration.

### 7.5.2 Early-exit decision
On **tests PASS**:
- Print: `✅ Iteration {CURRENT_ITER}/{MAX_ITER} passed — early exit`
- Go straight to Stage 8.

### 7.5.3 Reached max-iteration decision
**FAIL** and `CURRENT_ITER == MAX_ITER`:
- Print: `❌ Max iterations ({MAX_ITER}) exhausted; unresolved failure — stopping`
- Proceed to Stage 8 (highlight the unresolved failure in the report).

### 7.5.4 Failure classification + Direct-Patch re-entry (FAIL, `CURRENT_ITER < MAX_ITER`)

Only run when **FAIL** and `CURRENT_ITER < MAX_ITER`. Classify the failure (pattern-match table → tester-persona for AMBIGUOUS) into `CODE_BUG`/`SPEC_GAP`/`DESIGN_MISALIGN`/`ENV_ISSUE`, map to a re-entry stage (6/3/2/abort), then `CURRENT_ITER += 1` and **patch the target files in place** (no sub-skill re-invocation in iteration ≥ 2; `/test-run` is re-invoked idempotently). `ENV_ISSUE` → abort + Stage 8.

The classification signal table, the tie/AMBIGUOUS rule, the tester-persona delegation prompt, the per-stage Direct-Patch procedure, and the `/test-scenario` re-invocation exception: see [references/failure-classification.md](references/failure-classification.md). Read it whenever an iteration FAILs and you must decide the re-entry stage.

## Stage 8: `/pr-merge --auto` auto-invocation (only when tests pass)

Enter this stage only when tests passed (early exit). Unresolved failures (`MAX_ITER` exhausted or `ENV_ISSUE` abort) skip this stage and go straight to Stage 9.

### 8.0 Preconditions
- `CURRENT_ITER`'s final state is PASS
- The working directory is inside the sprint worktree (`$WT_PATH`) — must remain `cd`-ed from Stage 4.3.

### 8.1 Invoke `/pr-merge --auto`

```
Skill('pr-merge', '--auto')
```

`/pr-merge --auto` runs the two-phase workflow (v5.9+) end-to-end in a single invocation: Sprint Phase (commit → branch sync → PR → code review → fix Critical/High) → auto `cd` to the main worktree → Main Phase (`gh pr merge` sprint→integration → promotion → worktree removal). All steps are automatic **except** the Step 8.4.5 promotion-target choice.

### 8.2 HITL trigger conditions

`/pr-merge --auto` either halts (true blockers) or surfaces an `AskUserQuestion` — autorun forwards both to the user as-is.

- **Always-on HITL (routine, not a blocker)**: **Step 8.4.5 promotion target** after the sprint→integration merge — `/pr-merge` asks the user to pick `dev` (standard) / `staging` (fast hotfix) / `skip` (defer). This prompt fires even under `--auto` (the deployment surface has no safe unattended default); autorun pauses for the answer, then continues automatically through promotion-PR creation, merge, and worktree removal. This is the only routine HITL point once the pipeline is running.
- **True blockers (halt + guidance)**: gh not authenticated · cascade/rebase merge conflict · Critical review issues remaining after MAX iterations · MAX iterations with only High issues remaining (a/b/c prompt) · multiple pending sprint PRs on Main Phase entry · main worktree on a non-shared branch.

The full two-phase workflow table and the exhaustive blocker descriptions: see [references/pr-merge-handoff.md](references/pr-merge-handoff.md). Read it when `/pr-merge --auto` halts or you need the per-step handling detail.

### 8.3 Capture results (value contract — Stage 9 branches on these exact strings)
Set and persist (`astra_state_set`) the following after `/pr-merge --auto` returns:
- `MERGE_RESULT` = **`success`** ONLY after verifying the PR is really merged: `gh pr view "$PR_NUMBER" --json state --jq '.state'` returns `MERGED`. Any other outcome (halt, conflict, blocked, unverifiable) → **`fail`**. These two literal strings are the whole contract — Stage 9.0 tests `[ "$MERGE_RESULT" = "success" ]`.
- `PR_URL` (from the `/pr-merge` output; empty if no PR was created)
- `REVIEW_ITERATIONS` (integer)
- `WORKTREE_REMOVED` = `yes` / `no` (verify: `git worktree list --porcelain | grep -qF "$WT_PATH"` → present means `no`)

> **Important**: when `/pr-merge` removes the worktree, the current working directory automatically changes to the main worktree (dev). Stage 9 report authoring happens in the main worktree.

---

## Stage 9: Final report

**Mainline**: after Stage 8 returns, always `cd` into the main worktree (the Skill boundary may not propagate a sub-skill's cwd change), sync `dev` when `MERGE_RESULT=success`, then resolve `REPORT_DIR` (main worktree on success, or the still-present sprint worktree on merge failure/skip). Author `$REPORT_DIR/pipeline-report.md` and print the user-facing completion message.

**Report Completion Gate** (mandatory before finishing): verify the report file was actually written (`[ -f "$REPORT_DIR/pipeline-report.md" ]`) and that every ✅/❌ mark in it traces to a check executed in this session (test-result line, gh pr state, worktree list). Then clear pipeline state: `astra_state_clear`.

The 9.0 working-directory-reconciliation bash, the 9.1 `pipeline-report.md` markdown template, the 9.2 user-facing message template, and the 9.3 `/pr-merge --auto` invocation policy: see [references/stage9-output.md](references/stage9-output.md). Read it when authoring the final report and message.

## Failure-handling policy

### Immediate-stop conditions (Hard Stop — before entering the iteration loop)
- Any of Stages 1–6 produces a missing deliverable file (the iteration loop only applies to Stage 7 failure)
- `/generate-entity` or an auto-applied skill returns an explicit error
- The classification result is `ENV_ISSUE` (environment/infra issues cannot be resolved by iterating)

### Iteration-loop entry condition (on Stage 7 failure)
- `/test-run` still fails after 5 auto-debug attempts + `CURRENT_ITER < MAX_ITER`
  → run the 7.5 classification and re-entry logic
- On reaching `CURRENT_ITER == MAX_ITER`, stop at that point. **Skip** Stage 8 (`/pr-merge --auto`) and go straight to the Stage 9 report.

### Non-blocking conditions (Continue with Warning)
- P0 issues from validation agents (planner-reviewer, blueprint-reviewer, design-token-validator)
- `convention-validator`, `naming-validator` warnings
- Minor missing deliverables (e.g., README, some diagrams)

### Stop output format
On a hard stop, emit the standard stop message (stage name, cause, stages-completed list, recommended actions). Template: see the "Hard-Stop output format" section of [references/stage9-output.md](references/stage9-output.md).

## Resume mode, usage caveats & reference notes

When re-invoked on a feature that already has partial deliverables, `/autorun` runs in **idempotent resume mode**: it scans `iter-*-summary.md` first (PASS → done; FAIL → resume at `CURRENT_ITER = LAST_ITER + 1` from the summary's `target_stage`), then skips any stage whose deliverables already exist. `--max-iter` handling on resume follows Stage 0.5.1 (use the argument as-is, or ask once if absent).

The full resume decision order, the resume status message, the suitable/unsuitable use cases, the recommended follow-up workflow, the inter-skill relationship table, and the ASTRA 4-principle mapping: see [references/resume-and-notes.md](references/resume-and-notes.md). Read it when resuming a prior run or when you need the appendix material.

---

**Final note**: this skill is classified as a *broad deliverable-generating skill* and is not bounded by Simplicity First (see the "ASTRA auto-builder exception" section in CLAUDE.md). However, every piece of code generated internally still follows the coding convention and the 4 principles.
