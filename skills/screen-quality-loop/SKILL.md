---
name: screen-quality-loop
description: >
  Automatically runs an adversarial screen-quality convergence loop right after a NEW UI screen is implemented —
  a new page, route, view, screen component (e.g., app/**/page.tsx, *-screen.tsx, src/pages/**, src/views/**),
  standalone HTML page, or planner HTML mockup (SCR-NNN.html). Each iteration delegates the screen set to the
  read-only screen-verifier agent, which adversarially scores design-system application, cross-screen layout
  consistency, and polish/sophistication; the loop applies the fix directives and repeats until score ≥ 90 with
  zero P0 defects, or 5 iterations (hard cap). Used when creating or implementing new screens, pages, or views.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task, Agent, TodoWrite
---

# Screen Quality Convergence Loop

Runs an **evaluator-optimizer loop over newly authored screens**: the parent context (this skill) implements and fixes; the read-only `screen-verifier` agent adversarially scores each iteration against its fixed three-axis rubric — **design-system application (35) · cross-screen layout consistency (30) · polish & sophistication (35)**. The loop terminates on exactly two conditions: **quality met** (score ≥ 90 AND p0 == 0) or **5 iterations reached**.

> **🌐 LANGUAGE RULE**: Before executing this skill, read the project's `CLAUDE.md` and check the `## Language` section. If the project language is NOT Korean (`ko`), translate ALL user-facing output accordingly.

## Core principles

1. **The 5-iteration cap is the safety mechanism; the score is only the success signal.** The cap is fixed — this loop runs unattended inside other workflows (`/service-planner`, `/autorun`, ad-hoc screen work), so it never asks the user mid-loop. There is no HITL and no unattended bypass of the cap.
2. **Triple discipline, single gate.** Success is the conjunction score ≥ 90 **AND** P0 count == 0 — never the score alone (LLM judge scores cluster near the top; the P0 gate is the leniency-bias mitigation).
3. **Fresh-context adversarial verification.** The verifier sees artifacts only — never this context's reasoning or self-assessment.
4. **Branch on the tail line only.** Loop decisions parse the `ASTRA_SCREEN_RESULT:` line — never infer PASS/FAIL from report prose. **Line absent = FAIL, never PASS.**
5. **Surgical fixes.** Each iteration executes ONLY the previous report's Fix Directives, in their stated order, in this parent context (so `coding-convention` / auto-applied skills still trigger on the edits).
6. **One loop per authoring batch.** Screens created together are verified together as one set — not one loop per file.

## Trigger and skip conditions

**Trigger** — a NEW screen-level artifact was just created (initial implementation complete):

| MODE | New-screen signals |
|------|--------------------|
| `mockup` | `SCR-*.html` under `docs/planner/*/` (with `styles.css` / `index.html`) — invoked by `/service-planner` Step 6.F.6 |
| `app` | New `app/**/page.*`, `src/pages/**`, `src/views/**`, `src/routes/**` page file, `*-screen.tsx` (React Native), or a standalone `.html` page in the web root |

**Skip** (do NOT run the loop) when:
- The change only *edits an existing* screen or touches non-screen units (shared components, hooks, utils, styles-only tweaks).
- The artifact is a report/manual/catalog/proposal HTML deliverable (`/manual-generator`, `/catalog-generator`, `/handoff-publish`, UAT reports) — those pipelines own their templates and layout rules.
- `/design-redesign` is running — it has its own audit-fix loop.
- The user explicitly opts out for this batch (e.g., "skip the screen quality loop").
- The screen cannot render yet because upstream work is unfinished (run the loop after the batch compiles/opens).

## Stage 1: Scope capture

Determine, and print as a kickoff block:

1. **MODE** — `mockup` or `app` (table above).
2. **NEW SCREENS** — the screen files created this batch (from the conversation; verify with `[ -f ]` / Glob before claiming them).
3. **SIBLING BASELINE** — the 2–3 existing screens most comparable to the new ones (same section of the app, same layout family; for mockups: the other `SCR-NNN.html` plus `index.html`). No prior screens → pass "none" (the verifier falls back to the design SSoT's layout definitions).
4. **DESIGN SSoT PATHS** — first match per mode: `app` → `docs/design-system/DESIGN.md`, `src/styles/design-tokens.css`; `mockup` → `docs/design-system/DESIGN.md`, `{OUTPUT_DIR}/styles.css`.
5. **REPORT_DIR** — where verify reports land: `mockup` → `{OUTPUT_DIR}/screen-quality/`; `app` → `docs/design-system/screen-quality/{kebab-case-batch-slug}/`. `mkdir -p` it.

```
🖼  Screen quality loop starting — max 5 iterations, exit gate: score ≥ 90 AND p0 == 0
   Screens: {list}   Baseline: {list | none}   Mode: {MODE}
   Reports: {REPORT_DIR}/verify-{i}.md
```

> **State**: no state-file protocol is needed — every Bash block below is self-contained (parse-only). The iteration counter `I` is **always re-derived at 2.3, never trusted from conversational memory**: the written `verify-{I}.md` reports are the durable counter, so a crash, compaction, or resume can never reset the 5-iteration cap.

## Stage 2: Iteration loop (I = 1..5)

### 2.1 Adversarial verification

```
VERIFY_OUTPUT=(Task(screen-verifier, "
MODE: {mockup|app}
NEW SCREENS: {file list}
SIBLING BASELINE: {file list | none}
DESIGN SSoT PATHS: {paths, with [missing] markers for absent files}
ITERATION: {I}
Attempt to refute screen quality per your adversarial mandate. Score additively from 0 against your fixed rubric.
End with the ASTRA_SCREEN_RESULT tail line."))
```

The agent is read-only; the parent writes the report: `Write("{REPORT_DIR}/verify-{I}.md", VERIFY_OUTPUT)`.

### 2.2 Parse the tail line (branch on this line ONLY)

```bash
RESULT_LINE=$(printf '%s\n' "$VERIFY_OUTPUT" | grep -oE 'ASTRA_SCREEN_RESULT: score=[0-9]+ verdict=(PASS|FAIL) p0=[0-9]+ iter=[0-9]+' | tail -1)
if [ -z "$RESULT_LINE" ]; then
  # Tail line absent → re-invoke the verifier ONCE. If the second run also lacks the line:
  # record verdict=FAIL score=0 p0=unknown in verify-{I}.md and continue to 2.3. Never assume PASS.
  SCREEN_SCORE=0; SCREEN_VERDICT="FAIL"; SCREEN_P0="unknown"
else
  SCREEN_SCORE=$(echo "$RESULT_LINE" | grep -oE 'score=[0-9]+' | cut -d= -f2)
  SCREEN_VERDICT=$(echo "$RESULT_LINE" | grep -oE 'verdict=(PASS|FAIL)' | cut -d= -f2)
  SCREEN_P0=$(echo "$RESULT_LINE" | grep -oE 'p0=[0-9]+' | cut -d= -f2)
fi
```

### 2.3 Loop decision (evaluate in this order)

First re-derive the iteration counter from disk — the cap must survive a crash, compaction, or resume; never trust a remembered `I`. Substitute the literal Stage-1 path for `{REPORT_DIR}` (shell variables do NOT survive between Bash blocks — an empty `$REPORT_DIR` would yield `I=0` and disarm the cap):

```bash
I=$(find "{REPORT_DIR}" -name 'verify-*.md' 2>/dev/null | wc -l | tr -d ' ')
```

1. **Quality met — early exit**: `SCREEN_VERDICT == PASS` (encodes score ≥ 90 AND p0 == 0) →
   `✅ Iteration {I}/5 — score {score} ≥ 90, p0 = 0 — screen quality met, exiting early` → Stage 3, outcome `achieved`.
2. **Cap reached**: `I == 5` →
   `❌ Max iterations (5) exhausted — final score {score}, {p0} P0 defect(s) remaining` → Stage 3, outcome `max-iter`.
3. **Next iteration**: apply the report's **Fix Directives** in this parent context — surgically, in their stated order, nothing else (unrelated "improvements" get re-scored anyway). Print `🔁 Iteration {I}/5 — score {score} — re-entering`, then return to 2.1 with `I += 1`.

## Stage 3: Final report

Print (this block is the loop's user-facing deliverable — the caller workflow continues after it):

```
🖼  Screen quality loop finished — {✅ achieved | ❌ max-iter reached}
   Screens: {list}

   Score trajectory:
   | Iter | Score | P0 | Verdict |
   |------|-------|----|---------|
   ...

   {If not achieved: Remaining P0 defects and top fix directives from verify-5.md +
    "Recommended: apply the remaining directives manually, or re-run the loop after fixing them."}

   Reports: {REPORT_DIR}/verify-1..{I}.md
```

This skill does **not** commit, create PRs, or block the caller — an unachieved outcome is reported honestly and handed back to the calling workflow (`/service-planner` continues to Step 7 with the score noted; `/autorun` Stage 6 proceeds to its own success criteria; ad-hoc work hands the directives to the user).

## Relationship with other skills

- **`screen-verifier`** (agents/screen-verifier.md) is invoked ONLY by this skill and `/service-planner` Step 6.F.6 — it never auto-triggers.
- **vs `/loop`**: `/loop` converges an arbitrary user-stated target with a HITL-frozen rubric and mandatory iteration HITL; this loop is a fixed-rubric, fixed-cap (5), zero-HITL quality gate specialized for new screens. For a custom screen target ("make this dashboard match Stripe's density"), use `/loop`.
- **vs `design-token-validator`**: the single-pass token check (Gate 2.5) is subsumed by rubric criterion A — do not run both in the same batch.
- **vs `/design-redesign`**: that skill retrofits *existing* UI against DESIGN.md; this loop gates *new* screens at authoring time.
- Behavioral evaluation scenarios live in [references/evals.md](references/evals.md) — read when validating changes to this skill's loop-control behavior.
