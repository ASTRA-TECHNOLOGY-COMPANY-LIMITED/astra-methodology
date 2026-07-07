---
name: loop
description: "Target-driven convergence loop (evaluator-optimizer pattern): iterates work until the adversarial loop-verifier scores ≥ 90/100 with zero P0 defects, or the HITL-confirmed max iteration count is reached (always asked; --max-iter=N only pre-selects). Rubric is frozen at start; each iteration runs work → objective test gate → fresh-context adversarial scoring. Use for open-ended convergence targets ('get Z to zero warnings', 'make X conform to Y') that don't fit the fixed /autorun pipeline."
argument-hint: "[target description] [--max-iter=N] (N only pre-selects an option in the mandatory HITL prompt — the question always fires)"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task, TodoWrite, Skill, AskUserQuestion
---

# ASTRA Convergence Loop (`/loop`)

Runs an **evaluator-optimizer loop**: the parent context (this skill) is the optimizer that does the work; the read-only `loop-verifier` agent is the adversarial evaluator that scores each iteration against a rubric frozen at loop start. The loop terminates on exactly three conditions — **target met** (score ≥ 90 AND p0 == 0), **max iterations reached**, or **stall** (user chooses to stop after 2 non-improving iterations).

> **🌐 LANGUAGE RULE**: Before executing this skill, read the project's `CLAUDE.md` and check the `## Language` section. If the project language is NOT Korean (`ko`), translate ALL user-facing output accordingly.

## Core principles

1. **Max iterations is the safety mechanism, the score is only the success signal.** The completion signal (score ≥ 90) can be wrong; the iteration cap cannot. That is why the max-iteration count is a **mandatory HITL** on every invocation — even when `--max-iter=N` is passed, the AskUserQuestion still fires with N pre-selected. There is no unattended bypass.
2. **Triple gate, not a single score.** Success requires the conjunction: objective gate pass (test-runner exit 0, when a runner exists) **AND** total score ≥ 90 **AND** P0 count == 0. LLM judge scores cluster near the top of the scale; a lone ≥ 90 threshold would false-pass within 1–2 iterations.
3. **Frozen rubric.** The evaluation criteria are decided once (Stage 0.3), confirmed by the user, written to `loop.md`, and never changed mid-loop. Score trajectories are only meaningful against a fixed yardstick.
4. **Fresh-context adversarial verification.** The verifier runs as a sub-agent that sees artifacts only — never this context's reasoning or self-assessment. A judge that reads the worker's explanation gets persuaded by it.
5. **Branch on the tail line only.** Loop decisions parse the `ASTRA_LOOP_RESULT:` line — never infer PASS/FAIL from report prose.
6. **Context efficiency.** Hand off between iterations using only the verifier's Fix Directives + `iter-{i}-summary.md` (≤ 200 lines). Do not re-read the full target artifacts each iteration.
7. **Surgical Changes.** Each iteration edits only what the fix directives require. Unrelated edits are scored down by the rubric itself.

## Input

```
/loop {target description} [--max-iter=N]
```

**Examples**:
- `/loop make every skill description in skills/ comply with the 7 description rules`
- `/loop get src/api to zero ESLint warnings --max-iter=5` (5 is pre-selected in the HITL prompt, which still fires)

**What /loop is NOT for**: the fixed weekly feature pipeline (use `/autorun` — it owns planning → blueprint → sprint worktree → PR merge). `/loop` performs no worktree creation, no PR, and no merge; it converges the working tree toward a target and stops. Combine freely: run `/loop` inside a sprint worktree, then `/pr-merge` as usual.

## Stage 0: Argument parsing and target registration

### 0.1 Extract the target description
Take the target description from `$ARGUMENTS` (strip a trailing `--max-iter=N` if present). If empty, print and stop:
```
❌ A target description is required.
Usage: /loop {target description} [--max-iter=N]
Example: /loop get src/api to zero ESLint warnings
```

### 0.2 Auto-generate the target slug and directory
- Translate non-English text to English meaning, convert to kebab-case, abbreviate to 1–3 words → `LOOP_SLUG`.
- Determine the next target directory number: `NNN=$(find docs/loops -maxdepth 1 -type d -name '[0-9][0-9][0-9]-*' 2>/dev/null | sort | tail -1 | xargs -I{} basename {} | cut -d- -f1)`, then zero-padded `NNN+1` (start at `001` when none). `LOOP_DIR="docs/loops/{NNN}-{LOOP_SLUG}"`, `mkdir -p "$LOOP_DIR"`.

### 0.3 Instantiate and freeze the rubric (HITL 1 of 2)

1. Read `references/rubric-template.md` (relative to this SKILL.md).
2. Classify the target into a preset: **A feature-implementation** (build/add), **B bugfix** (fix/bug/error/broken/regression keywords), **C refactoring** (refactor/restructure/clean up/migrate), **D documentation** (docs/manual/guide deliverable), **E generic** (fallback). Apply target-specific adjustments within the template's bounds (±10 weight shift, ≤ 2 criteria added/replaced, objective gate and ≥ 1 P0 flag preserved).
3. Detect the project's test runner now (same first-match table as `/pr-merge` Step 8.2): `package.json` → `npm test --silent`, `pytest.ini`/`pyproject.toml` → `pytest -q`, `build.gradle*` → `./gradlew test`, `pom.xml` → `mvn -q test`, `go.mod` → `go test ./...`. No match → `TEST_CMD=""` and apply the template's no-runner reallocation rule.
4. Present the instantiated rubric table to the user and confirm via `AskUserQuestion`:
   - Question: "The loop will be judged against this rubric (frozen once started). Proceed?"
   - Options: `Use as-is (Recommended)` / `Adjust weights` / `Redefine criteria` — the latter two apply the user's notes within the template bounds, then re-present once.
5. Write `$LOOP_DIR/loop.md`: target statement (verbatim), classification, the frozen rubric table, `TEST_CMD`, and the date. **This file is immutable for the rest of the loop.**

### 0.4 Initialize progress tracking
Create todos via `TodoWrite`: Stage 0.5 max-iteration HITL → Stage 1 iteration loop (one todo per planned iteration is NOT needed — a single "iterate to convergence" todo, updated with `{i}/{N}` in its text) → Stage 2 final report.

## Stage 0.5: Max iteration count — MANDATORY HITL (2 of 2)

**This question always fires. No argument, flag, or auto mode skips it** — the iteration cap is the loop's only unconditional safety mechanism, so it must be a conscious user choice on every run.

- Parse `--max-iter=([0-9]+)` from `$ARGUMENTS`. If present and within 1 ≤ N ≤ 10, N becomes the pre-selected first option below (out of range → clamp + warn, then use the clamped value as the pre-selection).
- Call `AskUserQuestion` exactly once:
  - Question: "Max iteration count — how many work→verify cycles before the loop hard-stops? (early exit happens as soon as score ≥ 90 with 0 P0s)"
  - Options: when `--max-iter` was given → `{N} (from --max-iter) (Recommended)` / `3` / `5` / `enter manually`; otherwise → `3 (Recommended — default)` / `1 (single pass: work once, verify once)` / `5 (relentless convergence)` / `enter manually`.
  - No response / timeout: **3** is auto-adopted (or the valid `--max-iter` value if one was given).
- Validate 1 ≤ N ≤ 10 on manual entry; clamp + warn outside the range.

### 0.6 State-file protocol (MANDATORY)

Shell variables do not persist between Bash invocations. All loop state lives in the shared state file from `worktree-helpers.sh`, with the explicit scope `loop-{LOOP_SLUG}`:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"
astra_state_load "loop-{LOOP_SLUG}"    # start of EVERY Bash block in this skill
```

Canonical variables — set once at capture, persist immediately with `astra_state_set KEY "$VALUE" "loop-{LOOP_SLUG}"`:

| Variable | Captured at | Content |
|---|---|---|
| `LOOP_SLUG` / `LOOP_DIR` | Stage 0.2 | slug and `docs/loops/{NNN}-{slug}` |
| `TEST_CMD` | Stage 0.3 | detected runner command, or empty |
| `MAX_ITER` / `CURRENT_ITER` | Stage 0.5 | cap from HITL; `CURRENT_ITER=1` |
| `SCORE_HISTORY` | Stage 1.5, every iteration | space-separated scores, e.g. `"42 67 81"` — drives stall detection and the final trajectory table |
| `BASELINE_FILES` | Stage 1.1, iteration 1 | `git diff --name-only` baseline (or `git stash create` ref) to compute per-iteration scope |

If any variable is empty after `astra_state_load`, re-derive it before use. Run `astra_state_clear "loop-{LOOP_SLUG}"` at the end of Stage 2.

### 0.7 Kickoff output
```
🎯 ASTRA Loop starting — max {N} iterations, exit gate: score ≥ 90 AND p0 == 0{ AND `TEST_CMD` exit 0 | (no test runner — subjective gates only, see rubric)}
   Target: {target statement}
   Rubric: {LOOP_DIR}/loop.md (frozen)
   Iteration 1/{N} starting...
```

## Stage 1: Iteration loop (repeat per iteration)

### 1.1 Work execution
- **Iteration 1**: plan the minimal set of edits that satisfies the rubric criteria (Think Before Coding — if the target is ambiguous in a way the rubric doesn't resolve, that ambiguity should have been caught at Stage 0.3; do not re-ask mid-loop). Execute the edits in this parent context (so `coding-convention` / `data-standard` auto-skills trigger).
- **Iteration ≥ 2**: execute ONLY the previous verifier report's **Fix Directives**, in their stated order (Direct-Patch mode). Do not re-plan from scratch and do not re-read the full target artifacts — the directives plus `iter-{i-1}-summary.md` are the working context.

### 1.2 Objective gate (short-circuit)
If `TEST_CMD` is non-empty, run it and capture the exit code — never assess the work by reading the code alone.
- **Exit ≠ 0**: the iteration is an automatic FAIL. **Skip the verifier for this iteration** (its score cannot gate anything a failing suite hasn't already decided; skipping saves a full sub-agent run). Record `score=0 verdict=FAIL p0=1 (objective gate)` in the history, distill the test output's failure list into `iter-{i}-summary.md` as the next iteration's fix directives, and jump to 1.5.
- **Exit 0** (or no runner): proceed to 1.3.

### 1.3 Adversarial verification
Compute this iteration's scope: `git diff --name-only` against `BASELINE_FILES` (plus `$LOOP_DIR`). Then:

```
VERIFY_OUTPUT=$(Task(loop-verifier, "
TARGET STATEMENT: {verbatim target}
FROZEN RUBRIC: {the full rubric table from $LOOP_DIR/loop.md}
SCOPE (files changed this loop): {file list}
OBJECTIVE-GATE RESULT: {TEST_CMD + exit code | 'not configured'}
ITERATION: {CURRENT_ITER}
Attempt to refute target achievement per your adversarial mandate. Score additively from 0 against the frozen rubric only. End with the ASTRA_LOOP_RESULT tail line."))
```

The agent is read-only; the parent writes the report: `Write("$LOOP_DIR/verify-{CURRENT_ITER}.md", VERIFY_OUTPUT)`.

### 1.4 Parse the tail line (branch on this line ONLY)

```bash
RESULT_LINE=$(printf '%s\n' "$VERIFY_OUTPUT" | grep -oE 'ASTRA_LOOP_RESULT: score=[0-9]+ verdict=(PASS|FAIL) p0=[0-9]+ iter=[0-9]+' | tail -1)
if [ -z "$RESULT_LINE" ]; then
  # Tail line absent → treat as FAIL and re-invoke the verifier ONCE. Never assume PASS.
  # If the second run also lacks the line: record verdict=FAIL score=0 p0=unknown in verify-{i}.md and continue to 1.5.
  LOOP_SCORE=0; LOOP_VERDICT="FAIL"; LOOP_P0="unknown"
else
  LOOP_SCORE=$(echo "$RESULT_LINE" | grep -oE 'score=[0-9]+' | cut -d= -f2)
  LOOP_VERDICT=$(echo "$RESULT_LINE" | grep -oE 'verdict=(PASS|FAIL)' | cut -d= -f2)
  LOOP_P0=$(echo "$RESULT_LINE" | grep -oE 'p0=[0-9]+' | cut -d= -f2)
fi
```

Append `LOOP_SCORE` to `SCORE_HISTORY` and persist.

### 1.5 Loop decision (evaluate in this order)

1. **Target met — early exit**: `LOOP_VERDICT == PASS` (which already encodes score ≥ 90 AND p0 == 0; the objective gate passed to even reach 1.3) →
   ```
   ✅ Iteration {i}/{N} — score {score} ≥ 90, p0 = 0 — target met, exiting early
   ```
   → Stage 2 with outcome `achieved`.
2. **Max iterations reached**: `CURRENT_ITER == MAX_ITER` →
   ```
   ❌ Max iterations ({N}) exhausted — final score {score}, {p0} P0 defect(s) remaining — stopping
   ```
   → Stage 2 with outcome `max-iter`.
3. **Stall detection**: `SCORE_HISTORY` has ≥ 3 entries AND the last score ≤ the second-to-last AND the second-to-last ≤ the third-to-last (2 consecutive iterations without improvement) → the loop is spending tokens without converging. `AskUserQuestion`:
   - Question: "Score stalled ({third-to-last} → {second-to-last} → {last}) with {N − i} iteration(s) remaining. Continue?"
   - Options: `Stop and report (Recommended)` / `Continue remaining iterations`
   - Stop → Stage 2 with outcome `stalled`. Continue → fall through to 4 (stall check re-arms only after a strictly improving iteration).
4. **Next iteration**: write `$LOOP_DIR/iter-{i}-summary.md` (≤ 200 lines: score, P0 list, fix directives carried forward, files touched), `CURRENT_ITER += 1`, persist, print `🔁 Iteration {i}/{N} — score {score} — re-entering`, and return to 1.1.

## Stage 2: Final report and cleanup

Print (and append to `$LOOP_DIR/loop.md` under a `## Result` heading):

```
🎯 Loop finished — {✅ achieved | ❌ max-iter reached | ⏸ stalled (user stop)}
   Target: {target statement}

   Score trajectory:
   | Iter | Score | P0 | Objective gate | Verdict |
   |------|-------|----|----------------|---------|
   ...

   {If not achieved: Remaining P0 defects (from the last verify-{i}.md) + recommended next actions —
    typically: fix the listed P0s manually, or re-invoke /loop (it will ask for a fresh iteration budget).}

   Artifacts: {LOOP_DIR}/loop.md, verify-1..{i}.md, iter-*-summary.md
```

Then `astra_state_clear "loop-{LOOP_SLUG}"`. `/loop` does not commit, create PRs, or merge — hand off to the normal git flow (`/pr-merge` in a sprint worktree, or manual commits).

## Hard-stop conditions (outside the loop's own exits)

| Signal | Action |
|--------|--------|
| Target description empty | Stop at 0.1 with usage message |
| User declines the rubric twice at Stage 0.3 | Stop — "rubric not agreed; re-invoke /loop with a more specific target" |
| `TEST_CMD` itself broken (runner crashes on config, not on tests) at iteration 1 | Stop — environment issue, report the command output; do not burn iterations on an un-runnable gate |
| Verifier tail line missing twice in the same iteration | Score that iteration as FAIL (see 1.4) and continue — never assume PASS |

## Relationship with other skills

- **vs `/autorun`**: `/autorun` drives the fixed planning→merge pipeline with its own iteration loop over *test failures*; `/loop` converges an arbitrary target against a *scored rubric* and stops at the working tree. They share the state-file protocol, the ≤ 200-line iteration summary rule, and the tail-line contract style.
- **`loop-verifier`** (agents/loop-verifier.md) is invoked ONLY by this skill — it never auto-triggers.
- The rubric template lives in `references/rubric-template.md` (progressive disclosure — loaded once at Stage 0.3).
- Behavioral evaluation scenarios live in [references/evals.md](references/evals.md) — read when validating changes to this skill's loop-control behavior.
