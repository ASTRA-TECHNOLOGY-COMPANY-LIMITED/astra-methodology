---
name: autorun
description: "ASTRA full autonomous execution — runs the entire pipeline from planning through PR merge and worktree removal without user input, auto-iterating up to N times until tests pass. Sequentially executes /service-planner (with HTML mockup screens) → blueprint → /sprint-init → /test-scenario → implementation (/generate-entity + blueprint-based) → /test-run → /pr-merge --auto → automatic worktree removal; on test failure it classifies the cause and re-enters from the appropriate stage (self-improvement loop). Every user-choice step is auto-decided via smart defaults; only the max-iteration count is asked once at start. HITL fires only on true blockers — missing gh authentication, merge conflicts, or Critical review issues. Use when you want a single command to unattended-run a week's worth of work."
argument-hint: "[feature description] [--max-iter=N] (default 3 if N omitted; 1 means single pass)"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task, TodoWrite, Skill, AskUserQuestion
---

# ASTRA Full Autonomous Execution (`/autorun`)

**Auto-executes** planning → design → blueprint → sprint plan → implementation → tests without user input, then runs `/pr-merge --auto` until the moment it would block.

> **🌐 LANGUAGE RULE**: Before executing this skill, read the project's `CLAUDE.md` and check the `## Language` section. If the project language is NOT Korean (`ko`), translate ALL user-facing output and propagate the language preference to all sub-skills invoked.

## Core principles

1. **Unattended execution (Zero-Interaction during pipeline)**: do not call `AskUserQuestion` while the pipeline is running. **Single exception**: at the start, if the `--max-iter` argument is absent, ask once for the *max iteration count*. After that, every decision is an automatic default.
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

### 0.5.2 Initialize iteration context variables
Preserve the following variables in the session context:
- `MAX_ITER` = N (maximum iteration count)
- `CURRENT_ITER` = 1 (iteration currently in progress)
- `ITER_DIR` = `docs/sprints/sprint-{N}-{feature-slug}/iterations/` (finalized after Stage 4)
- `ITER_HISTORY` = [] (per-iteration result accumulation)

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
P0_ISSUES=$(grep -c "P0" "docs/blueprints/{NNN}-{feature-slug}/review.md" 2>/dev/null || echo 0)
echo "blueprint-reviewer P0 issues: $P0_ISSUES"
```

### 3.5 Blueprint auto-commit (guarantee worktree visibility)

`/blueprint --auto` auto-commits the blueprint to the current branch (dev) of the main worktree in its internal Step 6. autorun only needs to verify the commit result.

```bash
# Since autorun is in the main worktree (dev), the blueprint is committed to dev.
# When Stage 4's sprint-init creates a sprint worktree from dev as base, the blueprint is carried over together.
git log -1 --oneline -- "docs/blueprints/{NNN}-{feature-slug}/" || {
  echo "WARN: blueprint commit not detected. The blueprint may not be visible in the sprint worktree."
}
```

## Stage 4: Sprint plan (`/sprint-init`)

### 4.1 Auto-decision defaults

| Decision point | Auto default |
|---|---|
| Sprint number | scan `docs/sprints/` and pick the next number |
| Feature name | use the feature slug automatically |
| Blueprint linkage | auto-map Stage 3's `BLUEPRINT_PATH` |
| Proceed confirmation | **always Y** |

### 4.2 Execute
Call `Skill('sprint-init', '{feature-slug}')`.

> **v5.0+ important**: `/sprint-init` creates a sprint worktree at `.astra-worktrees/sprint-<N>-<feature-slug>/` and writes all sprint deliverables inside it. autorun **must `cd` into the worktree path** right after the call, before executing Stage 5+. If you do not `cd`, the Stage 5 (test scenarios) / Stage 6 (implementation) deliverables and the Stage 7 `/test-run` and Stage 8 `/pr-merge --auto` will all happen in the main worktree, breaking isolation.

### 4.3 Success criteria + move into the worktree
```
.astra-worktrees/sprint-{N}-{feature-slug}/
├── .astra-worktree.env          # port base
└── docs/sprints/sprint-{N}-{feature-slug}/
    ├── prompt-map.md
    ├── progress.md
    └── retrospective.md
```

```bash
WT_PATH=".astra-worktrees/sprint-${N}-${feature-slug}"
cd "$WT_PATH" || {
  echo "ERROR: failed to move into the sprint worktree: $WT_PATH" >&2
  exit 1
}
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

### 6.3 Success criteria
- Entity/service/controller files are generated under `src/` or the project's standard location
- The blueprint's data model and API spec are fully reflected in code

On failure, **STOP** + request user intervention.

## Stage 7: Test execution (`/test-run`)

### 7.1 Auto-decision defaults

| Decision point | Auto default |
|---|---|
| Test environment | **cmux browser** (if available), fallback: **Chrome MCP** |
| Auto-debug retry | **enabled** (up to 5 times) |
| Proceed confirmation | **always Y** |

### 7.2 Execute
Call `Skill('test-run', '{feature-slug}')`.

### 7.3 Success criteria
- A test report file exists: `docs/tests/test-reports/sprint-{N}-{feature-slug}/`
- **All tests pass** OR after 5 retries, a clear failure report

### 7.4 Result branching
- **All tests pass** → enter Stage 7.5's *early-exit path* → go to Stage 8.
- **Still failing after 5 auto-debug attempts** → enter Stage 7.5's *iteration-decision path*.

## Stage 7.5: Iteration loop (self-improvement)

### 7.5.1 End-of-iteration handling (always run at the end of every iteration)

**Changed-file tracking mechanism**: do not rely on git diff (autorun does not commit mid-pipeline — **single exception**: in v5.1+ Stage 3.5, `/blueprint --auto` makes a single blueprint commit to dev. That is for worktree visibility and happens *before* the iteration loop starts, so it does not affect the baseline snapshot). Instead, **snapshot the baseline file list at iteration start** and diff at end.

1. **At iteration start (once)**: create `{ITER_DIR}/iter-{CURRENT_ITER}-baseline.txt`:
   ```bash
   # Snapshot the file list (with mtime) of the tracked directories.
   # Use -exec stat to be compatible with both macOS (BSD) find and Linux (GNU) find.
   # (BSD find doesn't support -printf, so use `stat -f '%N %m'`.)
   find docs/planner/{NNN}-{slug} docs/blueprints/{NNN}-{slug} \
        src docs/tests/test-cases/sprint-{N}-{slug} \
        -type f 2>/dev/null \
        -exec stat -f '%N %m' {} \; 2>/dev/null \
        | sort > {ITER_DIR}/iter-{CURRENT_ITER}-baseline.txt
   # On Linux (GNU coreutils stat) the command above may fail.
   # In that case fall back to: -exec stat -c '%n %Y' {} \;
   ```
   - In iteration 1, the baseline may be empty (normal).
   - Files autorun edits directly are detected by mtime changes.
   - **Platform detection**: branch on `uname -s` (Darwin/Linux) when needed (macOS: `stat -f '%N %m'`, Linux: `stat -c '%n %Y'`).

2. **At iteration end**: take a current snapshot the same way and diff against the baseline:
   ```bash
   # Take the current snapshot the same way, then compare.
   diff {ITER_DIR}/iter-{CURRENT_ITER}-baseline.txt \
        <(find docs/planner/{NNN}-{slug} docs/blueprints/{NNN}-{slug} \
               src docs/tests/test-cases/sprint-{N}-{slug} \
               -type f 2>/dev/null \
               -exec stat -f '%N %m' {} \; 2>/dev/null | sort) \
        | grep '^>' | awk '{print $2}' > /tmp/changed_files.txt
   ```
   - Record the result in the "Changed deliverables" section of the summary.

3. **Author the iteration summary**: create `{ITER_DIR}/iter-{CURRENT_ITER}-summary.md` (≤ 200 lines):
   ```markdown
   # Iteration {i} Summary

   **Result**: PASS / FAIL
   **Duration**: {duration}
   **Tests**: {passed}/{total}

   ## Changed deliverables (this iteration; baseline diff result)
   - {list of file paths — extracted from /tmp/changed_files.txt}

   ## Failure classification (FAIL only)
   - **Classification**: CODE_BUG / SPEC_GAP / DESIGN_MISALIGN / ENV_ISSUE
   - **Evidence**: {1–3 lines summarizing the failure message / stack / log essentials}
   - **Next re-entry stage**: Stage {3|5|2|1|abort}
   - **Fix direction**: {1–2 lines — which file, which part, how to fix}
   - **Files to edit** (the next iteration will Edit these): {concrete path list}

   ## Remaining P0 issues
   - {P0 items from planner-reviewer / blueprint-reviewer / design-token-validator}

   ## Next iteration input context (the next round should read)
   - Deliverables to read: {path list — the "Files to edit" above + 1–2 directly dependent documents}
   - Do NOT read: the entire blueprint or planning documents (no reloading)
   ```

4. Append `{iter, result, classification, target_stage, changed_files_count}` to `ITER_HISTORY`.

### 7.5.2 Early-exit decision
On **tests PASS**:
- Print: `✅ Iteration {CURRENT_ITER}/{MAX_ITER} passed — early exit`
- Go straight to Stage 8.

### 7.5.3 Reached max-iteration decision
**FAIL** and `CURRENT_ITER == MAX_ITER`:
- Print: `❌ Max iterations ({MAX_ITER}) exhausted; unresolved failure — stopping`
- Proceed to Stage 8 (highlight the unresolved failure in the report).

### 7.5.4 Failure classification (decide the re-entry stage)
Only run when **FAIL** and `CURRENT_ITER < MAX_ITER`.

#### 1st: pattern matching (low cost, first)
Analyze the last failure log of the `/test-run` output:

| Signal (regex/keyword) | Classification | Re-entry stage |
|---|---|---|
| `TypeError`, `Cannot read property`, `NullPointer`, `panic:`, `Traceback`, `AttributeError`, `assertion failed`, `expected ... received`, stack traces with `src/` paths | `CODE_BUG` | **Stage 6 (implementation)** |
| `404 Not Found`, `endpoint not implemented`, `missing field`, `schema mismatch`, tests demand behavior not in the blueprint | `SPEC_GAP` | **Stage 3 (blueprint)** |
| `screenshot diff > threshold`, `aria-label missing`, `contrast insufficient`, UI interaction / accessibility failures | `DESIGN_MISALIGN` | **Stage 2 (UX)** |
| `ECONNREFUSED`, `port already in use`, `database connection`, `permission denied`, environment / infra errors | `ENV_ISSUE` | **abort** (user intervention required) |
| None of the above OR mixed signals | `AMBIGUOUS` | go to 2nd classification |

**Language-bias note**: the keywords above are skewed toward JS/TS/Java/Python. Go (`panic:`, `runtime error`) and Rust (`thread '...' panicked`) are partially included, but other languages/frameworks are likely to fall through to AMBIGUOUS and be delegated to the 2nd classification (tester-persona). This is intentional fall-through — accept the cost for correct classification.

#### 2nd: tester-persona delegation (only when the 1st is ambiguous)
```
Task(tester-persona, "
Analyze the following test failure log and decide the re-entry stage.
- Log: {last 100 lines}
- Blueprint path: {BLUEPRINT_PATH}
- Test scenarios: {TEST_DIR}
Output format:
  classification: CODE_BUG | SPEC_GAP | DESIGN_MISALIGN | ENV_ISSUE
  target_stage: 1 | 2 | 3 | 6
  reason: <one sentence>
")
```
- Adopt the result as-is. If `ENV_ISSUE`, abort + Stage 8.

### 7.5.5 Enter the next iteration — Direct Patch (no sub-skill re-invocation)

**Important design decision**: sub-skills (`/service-planner`, `/sprint-init`, etc.) do not have a patch/modify mode. Re-invoking them either regenerates everything or behaves unpredictably due to idempotency conflicts. Therefore, **in iteration ≥ 2 we do not invoke sub-skills; autorun directly patches files in-place via Read/Edit/Write**. Sub-skill invocation happens only in iteration 1.

1. `CURRENT_ITER += 1`
2. Print:
   ```
   🔁 Entering iteration {CURRENT_ITER}/{MAX_ITER} (Direct Patch mode)
      Re-entry stage: Stage {target_stage}
      Classification: {classification}
      Reference context: {ITER_DIR}/iter-{CURRENT_ITER-1}-summary.md
   ```
3. **Context-efficiency rule** (mandatory):
   - Read `iter-{CURRENT_ITER-1}-summary.md` first.
   - Only additionally load the files listed under "Deliverables to read" in the summary.
   - Do **not** re-Read the entire blueprint / planning documents. The summary states the delta and fix direction precisely.
4. **Direct-patch procedure per re-entry stage** (no sub-skill invocation; autorun edits directly via the Edit tool):

   | target_stage | Direct-patch target | Action |
   |---|---|---|
   | **1** (planning) | `docs/planner/{NNN}-{slug}/feature-definition.md` etc. files the summary points to | Edit the relevant section. Do **not** re-invoke Stage 4 (/sprint-init) — the sprint dir already exists. Continue Stage 6 via Direct Patch. |
   | **2** (UX HTML mockup) | files in `docs/planner/{NNN}-{slug}/styles.css`, `SCR-*.html`, `index.html` the summary points to | Edit tokens / markup. When changing the design tone, update only styles.css. |
   | **3** (blueprint) | `docs/blueprints/{NNN}-{slug}/blueprint.md` | Edit the data model / API spec. The data-standard auto-applied skill still fires. When the blueprint changes, the affected test scenarios are auto-included in the Stage 5 patch targets. |
   | **6** (implementation) | `src/...` code files — modules/methods the summary points to | Edit the code directly. coding-convention auto-applies. Do **not** re-invoke `/generate-entity` (if table definitions are unchanged). |

5. Subsequent execution after patch:
   - When blueprint / planning / UX changed → regenerate only the affected cases in Stage 5 (test scenarios) directly via Edit → partially re-patch Stage 6 (implementation) → **re-invoke** Stage 7 (`/test-run`) (this is a sub-skill but idempotent)
   - When only implementation changed → re-invoke Stage 7 immediately
6. Accumulate the changed file list into the next iteration summary (see 7.5.1).

### 7.5.6 Exception: re-invocation policy for Stage 5 test scenarios
`/test-scenario` may not be idempotent. So on re-entry:
- Edit the test-case files the summary points to directly
- Re-invoke `/test-scenario` only when new scenarios are needed (specify "additional scenarios: {list}" in the input)

`/test-run` is idempotent, so invoke it as-is every iteration.

## Stage 8: `/pr-merge --auto` auto-invocation (only when tests pass)

Enter this stage only when tests passed (early exit). Unresolved failures (`MAX_ITER` exhausted or `ENV_ISSUE` abort) skip this stage and go straight to Stage 9.

### 8.0 Preconditions
- `CURRENT_ITER`'s final state is PASS
- The working directory is inside the sprint worktree (`$WT_PATH`) — must remain `cd`-ed from Stage 4.3.

### 8.1 Invoke `/pr-merge --auto`

```
Skill('pr-merge', '--auto')
```

`/pr-merge --auto` auto-handles the following:

| Stage | Handling |
|---|---|
| Commit uncommitted changes | auto (bypasses confirmation prompt) |
| Branch sync (staging→dev cascade only) | auto, halts on conflict (HITL) |
| Create PR | auto (ASTRA template) |
| Code review (feature-dev:code-reviewer agent) | auto |
| Fix Critical/High issues (up to 3 iterations) | auto (Surgical Changes principle) |
| Merge (final confirmation prompt) | auto-approve |
| **Remove sprint worktree** | auto (return to main worktree (dev)) |

### 8.2 HITL trigger conditions (true blockers)

In the following situations, `/pr-merge --auto` halts and requests user intervention — autorun receives these directly:

- **gh CLI not authenticated**: shows `gh auth login` guidance and exits
- **Cascade merge conflict**: prints the conflicting files and exits (manual resolution required)
- **Rebase conflict** (target branch → work branch): same
- **Critical review issues ≥ 1 remain after MAX iterations**: merge blocked (`gh pr merge` not called)
- **MAX iterations reached + only High issues remain**: `/pr-merge`'s own `AskUserQuestion` fires (a/b/c choice). autorun surfaces that prompt to the user as-is — does not bypass it.

### 8.3 Capture results
Extract the following from the `/pr-merge --auto` output and save in the `MERGE_RESULT` variable:
- PR URL
- merge success (true/false)
- review iteration count
- worktree removal status

> **Important**: when `/pr-merge` removes the worktree, the current working directory automatically changes to the main worktree (dev). Stage 9 report authoring happens in the main worktree.

---

## Stage 9: Final report

### 9.0 Ensure working-directory consistency

When Stage 8's `/pr-merge --auto` succeeds and removes the worktree, it `cd`s into the main worktree. However, it is not guaranteed that the Skill tool propagates a sub-skill's cwd change to the parent context. Before authoring the Stage 9.1 report, explicitly `cd` into the main worktree:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"

# If Stage 8 succeeded in merging and removed the worktree we should already be in the main worktree,
# but cwd may be lost at the Skill invocation boundary. Always cd to the main worktree.
MAIN_ROOT=$(astra_main_worktree_root)
if [ -z "$MAIN_ROOT" ] || [ ! -d "$MAIN_ROOT" ]; then
  echo "ERROR: cannot determine the main worktree path" >&2
  exit 1
fi
cd "$MAIN_ROOT"

# If the merge succeeded, dev is up to date — but explicitly sync to ensure the report is written against the correct base.
if [ "$MERGE_RESULT" = "success" ]; then
  git fetch origin dev 2>/dev/null
  git checkout dev 2>/dev/null
  git pull --rebase origin dev 2>/dev/null || true
fi
```

**Merge failure or skipped case**: the sprint worktree remains and Stage 8 was skipped. In that case it makes sense to write the report inside the worktree, but if autorun already `cd`-ed into the main worktree, reference the worktree path explicitly when writing the report:

```bash
if [ "$MERGE_RESULT" != "success" ]; then
  REPORT_DIR="$MAIN_ROOT/.astra-worktrees/sprint-${SPRINT_N}-${FEATURE_SLUG}/docs/sprints/sprint-${SPRINT_N}-${FEATURE_SLUG}"
else
  REPORT_DIR="$MAIN_ROOT/docs/sprints/sprint-${SPRINT_N}-${FEATURE_SLUG}"
fi
```

### 9.1 Author the pipeline-execution report
Write the following to `$REPORT_DIR/pipeline-report.md`:

```markdown
# ASTRA Autorun automatic-execution report

**Feature**: {feature-slug}
**Run time**: {timestamp}
**Total duration**: {duration}
**Final result**: ✅ MERGED / ❌ FAIL (max iterations exhausted) / ⚠️ ABORT (env issue) / 🟡 BLOCKED (Critical review issue remains)
**iterations_used**: {final_iter}/{MAX_ITER}
**Merge result**: {MERGE_RESULT} (PR URL: {pr_url}, worktree removed: {yes/no})

## Iteration summary (self-improvement loop)

| Iter | Result | Re-entry stage | Classification | Test pass rate | Summary |
|---|---|---|---|---|---|
| 1 | ❌ FAIL | - | CODE_BUG | 12/15 | iterations/iter-1-summary.md |
| 2 | ❌ FAIL | Stage 6 | SPEC_GAP | 14/15 | iterations/iter-2-summary.md |
| 3 | ✅ PASS | Stage 3 | - | 15/15 | iterations/iter-3-summary.md |

## Per-stage result of the last iteration

| Stage | Result | Deliverable | Validation result |
|---|---|---|---|
| 1. Planning | ✅ / ⚠️ / ❌ | {path} | planner-reviewer: {summary} |
| 2. UX components | ✅ / ⚠️ / ❌ | {path} | design-token: {summary} |
| 3. Blueprint | ✅ / ⚠️ / ❌ | {path} | blueprint-reviewer: {summary} |
| 4. Sprint plan | ✅ / ⚠️ / ❌ | {path} | - |
| 5. Test scenarios | ✅ / ⚠️ / ❌ | {path} | - |
| 6. Implementation | ✅ / ⚠️ / ❌ | {N files} | coding-convention: {summary} |
| 7. Test execution | ✅ / ⚠️ / ❌ | {path} | passed: {N}/{M} |
| 8. PR merge (/pr-merge --auto) | ✅ / 🟡 / ⏭️ | PR {url} | review iterations: {N}, worktree: {removed/preserved} |

## ⚠️ Items needing attention (P0 issues)

{List of P0 issues found at the validation stages — based on the last iteration}

## 🚫 Unresolved failures (only on FAIL/ABORT/BLOCKED termination)

- {classification}: {cause summary}
- Last attempt: re-entered Stage {N}, result {fail/abort/blocked}
- Recommended action: {manual debug / environment check / blueprint redesign / manual Critical-issue resolution}

## 📋 Next steps

**On successful merge**:
1. Start the next sprint from the main worktree (dev).
2. For further review, invoke persona analysis:
   - Dev review: `Task(developer-persona)`
   - Test review: `Task(tester-persona)`

**On unresolved failure**:
1. Review the deliverables above (in the worktree or on dev) and apply fixes.
2. If the sprint worktree remains, fix inside it and re-run `/pr-merge`.
3. For related persona analysis, invoke:
   - Planning review: `Task(planner-reviewer)`
   - Design review: `Task(designer-persona)`
   - Dev review: `Task(developer-persona)`
   - Test review: `Task(tester-persona)`
```

### 9.2 User-facing message output

```
═══════════════════════════════════════════════════════
{✅ MERGED / ❌ FAIL / ⚠️ ABORT / 🟡 BLOCKED} ASTRA Autorun fully automatic execution complete

🔁 Iterations: {final_iter}/{MAX_ITER} ({early-exit on PASS / max reached / abort})

🎯 Merge result:
  - PR URL: {pr_url or "—"}
  - Merge success: {yes / no}
  - Review auto-fix iterations: {N}
  - Sprint worktree: {removed (returned to main dev) / preserved (kept on failure)}

📁 Deliverable locations:
  - Planning + HTML mockups: docs/planner/{NNN}-{feature-slug}/
  - Blueprint: docs/blueprints/{NNN}-{feature-slug}/
  - Sprint: docs/sprints/sprint-{N}-{feature-slug}/
  - Tests: docs/tests/test-cases/sprint-{N}-{feature-slug}/
  - Iteration summaries: docs/sprints/sprint-{N}-{feature-slug}/iterations/
  - Report: docs/sprints/sprint-{N}-{feature-slug}/pipeline-report.md

⚠️ P0 issues: {N} (see report)
✅ Tests: {pass}/{total}

{On successful merge}:
  ✅ Merge to dev complete — you are now back in the main worktree (dev).
  To start the next sprint, run /autorun or /sprint-init.

{On unresolved failure}:
  ❗ /pr-merge could not auto-execute.
  Cause: {Critical issues remain / merge conflict / environment error / test failure}
  After resolving, manually run /pr-merge inside the sprint worktree.
═══════════════════════════════════════════════════════
```

### 9.3 `/pr-merge --auto` invocation policy
- Auto-invoke `/pr-merge --auto` in Stage 8 only when tests passed (early exit).
- On unresolved failure (MAX_ITER exhausted / ENV_ISSUE abort), do not invoke; just author the report in Stage 9.
- In situations that truly need HITL (gh auth, merge conflict, Critical issues), `/pr-merge` itself stops; autorun reflects that in the report as-is.

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
```
❌ ASTRA Autorun stopped (Stage {N}: {stage name})

Cause: {concrete error message}

Stages completed so far:
- ✅ Stage 1: planning — {path}
- ✅ Stage 2: UX components — {path}
- ❌ Stage 3: blueprint — failed

Recommended actions:
1. {concrete next action, e.g., "manually author the blueprint, then /autorun {feature} --resume"}
2. Or run only the failed stage manually: {e.g., "/sprint-init {feature}"}
3. Diagnose: Task({relevant agent}, "...")
```

## Resume mode (Idempotent Resume)

### Behavior on re-execution
When re-invoked with the same feature slug, decide automatically in the following order:

1. **Check iteration progress first**: scan `docs/sprints/sprint-{N}-{feature-slug}/iterations/iter-*-summary.md`
   - Save the largest i value as `LAST_ITER`
   - If `LAST_ITER`'s summary is PASS → work is complete, no re-execution needed. Inform the user of the report location and exit.
   - If `LAST_ITER`'s summary is FAIL → start with `CURRENT_ITER = LAST_ITER + 1`, jump to the summary's `target_stage`.
   - No summary file → resume at the normal stage level (steps 2–7 below).

2. All 6 markdowns + `index.html` + `styles.css` + `SCR-*.html` in `docs/planner/{NNN}-{feature-slug}/` exist → skip Stage 1
3. `docs/blueprints/{NNN}-{feature-slug}/blueprint.md` exists → skip Stage 3
4. `docs/sprints/sprint-{N}-{feature-slug}/` exists → skip Stage 4
5. `docs/tests/test-cases/sprint-{N}-{feature-slug}/` exists → skip Stage 5 (test scenarios)
6. Implementation deliverables detected (per-module signature files exist) → skip Stage 6 (implementation)

`MAX_ITER` handling on re-execution:
- If `--max-iter=N` is provided, use it as-is (follow the Stage 0.5.1 rule; do not prompt).
- If absent, ask once exactly as in 0.5.1 (so the user can raise the limit and retry).

Report this behavior to the user:
```
🔄 Resume mode detected
  - Previous iterations: 2 completed (last: FAIL, CODE_BUG)
  - Stages 1–5: ✅ skipped
  - Stage 6 (implementation): ⏳ resuming Iteration 3 (target: Stage 6)
  - Context: see iter-2-summary.md
```

## Usage caveats

### Suitable use cases
- **Rapidly prototyping a new feature**
- When you need the **first feature seed right after Sprint 0**
- **Demo-environment setup** that needs a quick full-stack generation

### Unsuitable use cases
- **Partial modification / bug fix** of an existing codebase (the self-invocation cost is too high)
- **Sensitive business logic** (proceeds without user review gates — risky)
- **Legacy integration** (auto-decisions alone cannot guarantee compatibility)
- Features with **regulatory / compliance impact** (manual review is mandatory)

### Recommended follow-up workflow
1. Pipeline complete → review `pipeline-report.md`
2. Manually fix P0 issues
3. Persona-agent review (`Task(developer-persona)`, `Task(tester-persona)`)
4. After passing review, run `/pr-merge`

## Relationship with other skills

| Skill | Relationship with `/autorun` |
|---|---|
| `/service-planner` | Invoked in Stage 1 (default auto-applied + HTML mockups generated together) |
| `/handoff-publish` | **Not invoked** (optional deliverable; only when the user explicitly requests) |
| `/sprint-init` | Invoked in Stage 4 |
| `/generate-entity` | Invoked in Stage 6 (generates entities from the blueprint's data model) |
| `/test-scenario` | Invoked in Stage 5 (*before* implementation, TDD flow) |
| `/test-run` | Invoked in Stage 7 (re-invoked each iteration, up to MAX_ITER times) |
| `tester-persona` | Invoked only at Stage 7.5's *AMBIGUOUS* branch (failure classification) |
| `/pr-merge` | **Auto-invoked in Stage 8 as `/pr-merge --auto`** (only when tests pass). Not invoked on unresolved failure. Worktree removal is handled by /pr-merge. |
| `/check-naming`, `/check-convention` | Replaced by auto-applied skills + validation agents |

## ASTRA 4-principle application

| Principle | Pipeline application |
|---|---|
| **Think Before Coding** | Ambiguity validation and direction clarification in the planning stage (/service-planner) |
| **Simplicity First** | ⚠️ Bundle of broad deliverable-generating skills → *principle exception* (noted in CLAUDE.md). Internal code still follows the 4 principles. |
| **Surgical Changes** | Add only a new feature directory without modifying existing code |
| **Goal-Driven** | Existence of each stage's deliverable files is a clear success criterion |

---

**Final note**: this skill is classified as a *broad deliverable-generating skill* and is not bounded by Simplicity First (see the "ASTRA auto-builder exception" section in CLAUDE.md). However, every piece of code generated internally still follows the coding convention and the 4 principles.
