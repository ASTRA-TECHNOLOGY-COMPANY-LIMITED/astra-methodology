# Autorun — Failure Classification & Direct-Patch Re-entry

Read this when a `/test-run` iteration ends in **FAIL** and `CURRENT_ITER < MAX_ITER`, i.e. the Stage 7.5 self-improvement loop must decide *which stage to re-enter* and patch files in place. Not needed on a passing run.

## 7.5.4 Failure classification (decide the re-entry stage)
Only run when **FAIL** and `CURRENT_ITER < MAX_ITER`.

### 1st: pattern matching (low cost, first)
Analyze the last failure log of the `/test-run` output.

**Tie rule (evaluate ALL rows before deciding)**: check every row of the table against the log. If signals from **two or more different classification rows** are detected (e.g., a stack trace containing both `TypeError` and `404 Not Found`), that IS the "mixed signals" case — classify as `AMBIGUOUS` and go to the 2nd classification. Only when **exactly one** row matches may you adopt its classification directly.

| Signal (regex/keyword) | Classification | Re-entry stage |
|---|---|---|
| `TypeError`, `Cannot read property`, `NullPointer`, `panic:`, `Traceback`, `AttributeError`, `assertion failed`, `expected ... received`, stack traces with `src/` paths | `CODE_BUG` | **Stage 6 (implementation)** |
| `404 Not Found`, `endpoint not implemented`, `missing field`, `schema mismatch`, tests demand behavior not in the blueprint | `SPEC_GAP` | **Stage 3 (blueprint)** |
| `screenshot diff > threshold`, `aria-label missing`, `contrast insufficient`, UI interaction / accessibility failures | `DESIGN_MISALIGN` | **Stage 2 (UX)** |
| `ECONNREFUSED`, `port already in use`, `database connection`, `permission denied`, environment / infra errors | `ENV_ISSUE` | **abort** (user intervention required) |
| None of the above OR mixed signals | `AMBIGUOUS` | go to 2nd classification |

**Language-bias note**: the keywords above are skewed toward JS/TS/Java/Python. Go (`panic:`, `runtime error`) and Rust (`thread '...' panicked`) are partially included, but other languages/frameworks are likely to fall through to AMBIGUOUS and be delegated to the 2nd classification (tester-persona). This is intentional fall-through — accept the cost for correct classification.

### 2nd: tester-persona delegation (only when the 1st is ambiguous)
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

## 7.5.5 Enter the next iteration — Direct Patch (no sub-skill re-invocation)

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
6. Accumulate the changed file list into the next iteration summary (see the iteration-mechanics reference).

## 7.5.6 Exception: re-invocation policy for Stage 5 test scenarios
`/test-scenario` may not be idempotent. So on re-entry:
- Edit the test-case files the summary points to directly
- Re-invoke `/test-scenario` only when new scenarios are needed (specify "additional scenarios: {list}" in the input)

`/test-run` is idempotent, so invoke it as-is every iteration.
