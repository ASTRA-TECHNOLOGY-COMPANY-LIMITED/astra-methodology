# Rubric Template (read by /loop Stage 0.3)

The rubric is the contract between the worker (`/loop` parent context) and the judge (`loop-verifier`). It is instantiated ONCE at Stage 0.3, confirmed by the user via HITL, frozen for the whole loop, and injected verbatim into every `Task(loop-verifier, ...)` prompt. Changing criteria or weights after the loop starts is forbidden (moving the yardstick mid-loop makes the score trajectory meaningless).

## Rubric structure (all presets follow this shape)

| Field | Rule |
|-------|------|
| Criterion | One measurable statement. One criterion = one concern (never combine "works AND is documented"). |
| Weight | Integer points. **Weights across all criteria MUST sum to exactly 100.** |
| Award rule | Deterministic mapping from evidence to points (all-or-nothing, or a stepped formula). No "judge's impression" awards. |
| Evidence required | What the verifier must cite: file:line, command + exit code, or grep count. |
| P0 flag | `yes` = scoring below the award threshold on this criterion is target-blocking (forces verdict=FAIL regardless of total). |

**Anti-leniency rules baked into every award rule** (LLM-as-judge calibration best practice — judge scores cluster near the top of the scale unless forced down):

1. Scoring is additive from 0 — a criterion with no cited evidence stays at 0.
2. "Partially present" earns points only when the award rule defines an explicit step for it; otherwise partial = 0.
3. A placeholder (`TBD`, `TODO`, `pass`, empty body) never earns points.
4. When a test runner exists in the project, at least one criterion MUST be objective (exit-code based) and P0-flagged.

## Preset A — feature-implementation (default when the target asks to build/add something)

| Criterion | Weight | Award rule | Evidence | P0 |
|-----------|--------|-----------|----------|----|
| Functional completeness — every capability named in the target statement exists and is reachable | 40 | 40 × (implemented capabilities / capabilities named in target), rounded down; a capability with placeholder body counts 0 | file:line per capability | yes |
| Objective gate — project test runner exits 0 | 25 | all-or-nothing: exit 0 → 25, else 0. No runner configured → reallocate 25 to "Self-verification evidence" (run/build/manual-check transcript with exit codes) | command + exit code | yes |
| Tests cover the new behavior — at least one test per capability exercises the new code path | 15 | 15 × (covered capabilities / capabilities), rounded down | test file:line ↔ capability mapping | no |
| Convention compliance — no violations from `convention-validator` scope rules on changed files | 10 | 10 − 2 per violation class found (floor 0) | grep pattern + file:line | no |
| No regression / no unrelated edits (Surgical Changes) | 10 | all-or-nothing: changed-file list ⊆ target scope → 10; any unrelated file modified → 0 | `git diff --name-only` vs. target scope | no |

## Preset B — bugfix (target mentions fix/bug/error/broken/regression)

| Criterion | Weight | Award rule | Evidence | P0 |
|-----------|--------|-----------|----------|----|
| Defect no longer reproduces — the failure path named in the target is exercised and passes | 40 | all-or-nothing with cited reproduction command/test | command + exit code, or test file:line | yes |
| Regression test added that fails-before/passes-after | 20 | all-or-nothing; a test that would also have passed before the fix counts 0 | test file:line + reasoning from the diff | no |
| Objective gate — full test suite exits 0 | 20 | all-or-nothing; no runner → reallocate to self-verification evidence | command + exit code | yes |
| Root cause addressed, not symptom-patched (fix is at the layer the target/defect analysis names) | 10 | all-or-nothing | file:line | no |
| No unrelated edits | 10 | all-or-nothing | `git diff --name-only` | no |

## Preset C — refactoring (target mentions refactor/restructure/clean up/migrate, behavior preserved)

| Criterion | Weight | Award rule | Evidence | P0 |
|-----------|--------|-----------|----------|----|
| Behavior preserved — objective gate exits 0 (suite unchanged except moves/renames) | 35 | all-or-nothing; if tests were themselves edited beyond mechanical moves, cap at 0 and flag | command + exit code + test-diff check | yes |
| Target structure achieved — the end state named in the target holds everywhere in scope | 35 | 35 × (conforming sites / total sites found by grep sweep), rounded down | grep counts + sample file:line | yes |
| No leftover legacy — old pattern count in scope is 0 | 15 | all-or-nothing (grep count == 0) | grep pattern + count | no |
| Convention compliance on changed files | 10 | 10 − 2 per violation class (floor 0) | file:line | no |
| Diff proportionality — no drive-by features | 5 | all-or-nothing | `git diff --stat` review | no |

## Preset D — documentation (target produces docs/manual/guide content)

| Criterion | Weight | Award rule | Evidence | P0 |
|-----------|--------|-----------|----------|----|
| Section completeness vs. the structure agreed in the target | 40 | 40 × (substantive sections / agreed sections); placeholder section = 0 | heading grep + per-section read | yes |
| Factual accuracy — claims about code/behavior verified against the repo | 30 | 30 − 5 per unverifiable or false claim (floor 0) | file:line per spot-checked claim (≥ 5 checks or all claims if fewer) | yes |
| Internal consistency — links, cross-references, and referenced files resolve | 15 | 15 − 3 per broken reference (floor 0) | Glob/Read per reference | no |
| Language & format policy compliance (project language rule, format conventions) | 15 | all-or-nothing per policy area (rounded) | file:line | no |

## Preset E — generic (no other preset matches)

| Criterion | Weight | Award rule | Evidence | P0 |
|-----------|--------|-----------|----------|----|
| Target end-state holds — decompose the target statement into 2–5 verifiable sub-claims; all verified | 50 | 50 × (verified sub-claims / sub-claims), rounded down | evidence per sub-claim | yes |
| Verifiability — each sub-claim was checked by command or read, not assumed | 20 | all-or-nothing | commands/reads cited | yes |
| Objective gate when a runner exists | 15 | all-or-nothing; no runner → reallocate to sub-claim depth (re-verify with a second independent method) | command + exit code | yes |
| No unrelated edits | 15 | all-or-nothing | `git diff --name-only` | no |

## Target-specific adjustment (Stage 0.3, before the HITL freeze)

The preset may be adjusted to fit the specific target, within these bounds:

- Shift up to **±10 points total** between criteria (weights must still sum to 100).
- Add or replace at most **2 criteria**, each with a deterministic award rule and evidence requirement.
- Never remove the objective-gate criterion when a test runner exists.
- Never leave the rubric with zero P0-flagged criteria.

The adjusted rubric is what the user confirms in the Stage 0.3 HITL — after confirmation it is written to `docs/loops/{NNN}-{slug}/loop.md` and becomes immutable for the loop.
