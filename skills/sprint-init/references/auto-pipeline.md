# Sprint execution pipeline (shared SSoT — default continuous mode, `--auto`, `--resume`)

Non-mainline detail extracted from `SKILL.md`. **v5.16+: this file is the shared pipeline SSoT** — read it whenever a sprint continues past scaffolding, in any of these entry paths:

| Caller | `PIPELINE_MODE` | Behavior |
|--------|-----------------|----------|
| `/sprint-init` (default, no flags) | `attended` | Continuous one-session run. HITL fires only at real judgment points: remaining Critical review issues, final merge confirmation, promotion target. No per-stage questions. |
| `/blueprint` (default, after blueprint dev-push + worktree creation) | `attended` | Same as above — `/blueprint` drives Steps 5.0–5.7 itself after Step 6.5, inside the sprint worktree. |
| `/sprint-init --auto`, `/autorun` | `auto` | Unattended. Merge confirmation auto-approved (`/pr-merge --auto`); promotion target stays HITL (v5.11.2+ policy). |

Mode differences are confined to **Step 5.6** (pr-merge invocation) and abort wording — every other stage is identical. The mainline SKILL.md (Steps 0.B–4.6) covers worktree creation, port-isolated env, scaffolding, and flag handling; everything below is the self-improvement pipeline and its recovery path.

> **Isolation (v5.19+, worktree-always)**: every sprint runs inside `.worktrees/sprint-<N>-<name>/` and `WT_PATH` always points at that worktree. Every pipeline stage below executes inside it — the main worktree stays untouched on `dev`. The v5.16 in-place mode is removed.

---

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

---

### Step 5: Pipeline continuation (default; `--auto` = unattended variant)

After scaffolding finishes, run the following pipeline sequentially **in the same session** (v5.16+ — the pipeline is the default continuation; `--scaffold-stop` is the only way to stop after scaffolding):

```
/test-scenario all → implementation (blueprint-based) → /test-run → adversarial verification gate (Step 5.4.5)
  → (fix loop until score ≥ 90 ∧ P0 == 0 ∧ tests PASS, or MAX_ITER exhausted) → /pr-merge → cleanup
```

**Default principles**:
- During the pipeline, do not call `AskUserQuestion` between stages. `attended` mode allows HITL **only** at the pr-merge judgment points (remaining Critical issues, final merge confirmation, promotion target); `auto` mode reduces those to the promotion target + true blockers.
- Each stage's success criterion is judged solely from *verifiable file/test results and the adversarial verifier's machine-parseable tail line* — never from prose impressions.
- HITL fires on true blockers in both modes (gh auth, merge conflict, Critical review issues).
- **Cache-locality rule**: never instruct the user to `cd` or start a new session mid-pipeline — every stage runs in this session (the whole point of the continuous flow is one warm KV-cache prefix). Respond to HITL prompts promptly; a stall > 5 min costs one full-price cache re-write of the entire context.

#### Step 5.0: Pre-checks

1. **Verify the current worktree is the sprint worktree**: Steps 1.6/1.8 already created the worktree and cd'd in, so `$(pwd)` must equal `$WT_PATH`. Abort if not.
2. **Verify blueprints exist**: For every feature extracted from prompt-map.md, `docs/blueprints/[0-9][0-9][0-9]-{feature-name}/blueprint.md` must exist inside the worktree (or in the merged base branch).
   - Abort message when missing:
     ```
     ❌ The pipeline requires blueprints to be authored in advance.
        Missing blueprint: {feature-name}
        Fix: author the blueprint with /blueprint {feature-name} (it continues into this pipeline itself), then re-run.
     ```
3. **Determine MAX_ITER**: Use the `--max-iter=N` argument (1 ≤ N ≤ 10). If absent, **default to 5 — do not ask** (v5.16+: the adversarial gate in Step 5.4.5 makes the iteration bound a quality mechanism, not a user preference; 5 matches the `screen-quality-loop` hard cap).

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
  worktree_path: {WT_PATH}          # always a .worktrees/sprint-* path (v5.19+)
  pipeline_mode: attended | auto
  branch: feat/sprint-{N}-{sprint-name}
  port_base: {PORT_BASE}

iteration:
  max_iter: {MAX_ITER}
  current_iter: {CURRENT_ITER}

verifier:                            # filled by Step 5.4.5 (adversarial gate)
  last_score: null | 0-100
  last_p0: null | N
  history: []                        # [{iter: 1, score: 72, p0: 2}, ...]

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

> **Note**: This protocol applies to every pipeline run (`attended` and `auto`). Only `--scaffold-stop` / `--scaffold-only` invocations, which never enter Step 5, are unaffected.

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

**Determine pass/fail from the machine-parseable result line only.** `/test-run` runs via the Skill tool, so its output is **conversation text in the skill's return, not a shell variable** — do not try to capture it with a Bash pipe. Instead, read the `/test-run` skill's final output text directly and find the single line of this exact form (illustrative — not an executable snippet):

```
ASTRA_TEST_RESULT: PASS|FAIL passed=N failed=N total=N skipped=N
```

Then, as an LLM-level judgement (no shell):

1. Scan the `/test-run` skill output for a line matching `ASTRA_TEST_RESULT: (PASS|FAIL) passed=N failed=N total=N skipped=N` (a skipped scenario forces FAIL on the producer side — `/test-run` Step 11).
2. Take `TEST_VERDICT` (PASS or FAIL) and the `passed` / `failed` / `total` counts **from that line only** — never infer pass from prose ("tests look green", "seems to work").
3. If no such line exists anywhere in the skill output, set `TEST_VERDICT=FAIL` (a missing result line means the run did not complete cleanly), record `passed=0 failed=unknown total=unknown`, and route to Step 5.5.

Use `TEST_VERDICT` (not free-form reading) for the 5.4.Z branch below.

##### 5.4.Z 💾 Silent Save

`/test-run` accumulates large artifacts in the context (browser snapshots, console logs, network request logs). **Always run the 5.1.5 Silent Save Protocol**:
- Record `completed_stages: [..., 5.4]`, `last_test_result: { passed, total, failed_tests, log_excerpt }` (from the parsed `ASTRA_TEST_RESULT` fields) in `auto-state.yaml` + commit
  - `TEST_VERDICT=PASS` → `next_stage: 5.4.5` (adversarial verification gate — a green test suite alone never unlocks the merge)
  - `TEST_VERDICT=FAIL` + `CURRENT_ITER < MAX_ITER` → `next_stage: 5.5`
  - `TEST_VERDICT=FAIL` + `CURRENT_ITER == MAX_ITER` → `next_stage: 5.7` (jump directly to the report)
- Abbreviate `log_excerpt` to the essence of the last failure log within 100 lines (do not embed the full log in the yaml)
- Apply the 5.1.5.C reference-avoidance rule (browser snapshots, full console logs, network requests are no longer re-referenced — carry only the `log_excerpt` from the yaml into the next stage)
- **Auto-jump to `next_stage` immediately** — no exit / no user input

#### Step 5.4.5: Adversarial verification gate (v5.16+ — runs only when `TEST_VERDICT=PASS`)

A passing test suite is the *objective* gate; this step is the *adversarial* gate. Delegate scoring to the `loop-verifier` agent (fresh context — the verifier never sees this session's accumulated rationale, which both prevents leniency bias and keeps the heavy artifact-reading out of the parent context):

```
Task(loop-verifier, prompt = the following, model default):
  1. Target statement: "Sprint {N} ({sprint-name}): every feature in prompt-map.md is implemented
     per its blueprint and verified by the sprint test suite."
  2. Frozen rubric (SPRINT PRESET — immutable across iterations of this sprint):
     | Criterion | Weight | Award rule | P0 |
     |-----------|--------|-----------|----|
     | Blueprint conformance | 40 | Every table in blueprint §2 and endpoint in §3 exists in code (file:line evidence); §6 logic branches implemented | ✅ |
     | Test integrity | 30 | Objective-gate input line (item 4) reads PASS with skipped=0; scenario files cover every §3 endpoint; no stubbed/no-op assertions (verify by reading the scenario files — the browser suite itself is NOT re-runnable from the verifier) | ✅ |
     | Convention & quality | 30 | No convention violations in changed files; no placeholder bodies (TODO/pass/not-implemented); no dead scaffolding | — |
  3. Scope: implementation.{entities,services,controllers}_created + scenarios.files from auto-state.yaml,
     plus the blueprint path(s) from features[].
  4. Objective-gate result: the parsed ASTRA_TEST_RESULT line, verbatim.
  5. Iteration number: CURRENT_ITER.
```

**Parse the verifier's tail line only** (same protocol as `/loop`): `ASTRA_LOOP_RESULT: score=N verdict=PASS|FAIL p0=N iter=I`. If the line is missing → treat as `verdict=FAIL p0=1` (an unparseable verification never unlocks a merge).

Branch (the exit gate is the triple conjunction — **tests PASS ∧ score ≥ 90 ∧ p0 == 0**, encoded in the verifier's verdict):

- **`verdict=PASS`** → record `verifier: { score, p0, iter }` in `auto-state.yaml`, `next_stage: 5.6` → proceed to merge.
- **`verdict=FAIL` + `CURRENT_ITER < MAX_ITER`** → carry the verifier's **Fix Directives** (not the full report) into Step 5.5 as the patch work-list (`files_to_patch_next`), set `last_iteration_classification: VERIFIER_FAIL`, `CURRENT_ITER += 1`, run the 5.5.Z Silent Save, then Direct-Patch the directives and re-enter Step 5.4 (re-test). No user input.
- **`verdict=FAIL` + `CURRENT_ITER == MAX_ITER`** → `next_stage: 5.7`; **do not merge**. The report lists the remaining P0s and directives.

> **Stall guard**: if two consecutive iterations produce non-increasing scores, note it in the report but keep iterating until MAX_ITER — the hard cap (default 5) is the stop, matching the user-confirmed convergence policy (score ≥ 90 ∧ P0 == 0, else ≤ 5 loops).

#### Step 5.5: Self-improvement loop (on test failure or verifier FAIL)

Entry from Step 5.4 (`TEST_VERDICT=FAIL`) or Step 5.4.5 (`VERIFIER_FAIL` — in that case Step 5.4.5 has **already** incremented `CURRENT_ITER` and run its Silent Save: skip the classification (step 1) **and** the step-4 increment below, execute only the Direct-Patch (step 2, on the Fix Directives ordered by score impact) and the iteration summary (step 3). `CURRENT_ITER` increments exactly once per loop pass, whichever gate failed).

`TEST_VERDICT=FAIL` + `CURRENT_ITER < MAX_ITER`:

1. **Failure classification** (same pattern matching as autorun Stage 7.5.4 + in-context QA analysis as fallback):
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

`TEST_VERDICT=FAIL` + `CURRENT_ITER == MAX_ITER`:
- Print: `❌ Max iterations ({MAX_ITER}) exhausted with unresolved failures — stopping without /pr-merge`
- Jump directly to Step 5.7 (report); **do not invoke `/pr-merge`**.

#### Step 5.6: PR merge (only when the Step 5.4.5 gate passed — tests PASS ∧ score ≥ 90 ∧ P0 == 0)

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

##### 5.6.B Invoke `/pr-merge` (mode-aware)

- **`PIPELINE_MODE=attended`** → `Skill('pr-merge', '')`. Normal-mode pr-merge: commit → PR → review loop → **HITL final merge confirmation** → merge → **HITL promotion target** → cleanup. pr-merge never instructs a mid-flow `cd`: it asks one HITL ("finalize the merge now?") and performs the cross-worktree transition itself (Step 8.5).
- **`PIPELINE_MODE=auto`** → `Skill('pr-merge', '--auto')`. Same flow with the merge confirmation auto-approved; the promotion target stays HITL (v5.11.2+); halt on remaining Critical issues (true HITL).

End state in both modes: the PR is merged into its integration branch, the promotion decision is made, the sprint branch and worktree are cleaned up, and **the session continues in the main worktree on `dev`** — no user `cd` at any point.

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
{✅ / ❌ / ⚠️} Sprint {N} pipeline complete ({pipeline_mode})

🔁 Iterations: {iteration.current_iter}/{iteration.max_iter}
✅ Tests: {last_test_result.passed}/{last_test_result.total}
🎯 Verifier: {verifier.last_score}/100, P0 = {verifier.last_p0} (gate: ≥ 90 ∧ P0 == 0)
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

