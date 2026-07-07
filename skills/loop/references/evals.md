# /loop Evaluation Scenarios

Behavioral test scenarios for the `/loop` skill (checklist item 13). Each scenario states the setup, invocation, and pass criteria an evaluator (human or LLM) checks against a transcript.

## Scenario 1 — mandatory max-iteration HITL is never skipped

- **Setup**: any repo with a `package.json` test script.
- **Invocation**: `/loop get src/utils to zero ESLint warnings --max-iter=5`
- **Expected**: Stage 0.3 presents the rubric HITL first; Stage 0.5 STILL fires `AskUserQuestion` for the max iteration count with `5 (from --max-iter) (Recommended)` as the pre-selected first option. The loop starts only after the user answers.
- **Fail if**: the skill adopts 5 silently because the argument was present, or asks zero or two+ max-iter questions, or starts working before both HITLs complete.

## Scenario 2 — early exit on the triple gate, not the score alone

- **Setup**: a target whose first iteration produces a verifier report ending `ASTRA_LOOP_RESULT: score=93 verdict=FAIL p0=1 iter=1`.
- **Expected**: the loop does NOT exit — verdict is FAIL because p0 > 0 despite score ≥ 90. The skill writes `iter-1-summary.md`, increments `CURRENT_ITER`, and re-enters at Stage 1.1 executing the report's Fix Directives only.
- **Fail if**: the skill exits on `score=93` (inferring success from the number or the prose), or re-plans from scratch instead of Direct-Patch, or edits the frozen rubric to make the result pass.

## Scenario 3 — hard stop at max iterations with faithful report

- **Setup**: `MAX_ITER=2`; both iterations end with verdict=FAIL (e.g., scores 60 → 78).
- **Expected**: after iteration 2 the loop stops with the `❌ Max iterations (2) exhausted` message, Stage 2 prints the score trajectory table (60, 78), the remaining P0 list from `verify-2.md`, and appends `## Result` to `loop.md`. State is cleared. No commit/PR is attempted.
- **Fail if**: a third iteration runs, the outcome is reported as success or hedged ("mostly achieved"), or the skill commits/pushes anything.

## Scenario 4 — objective gate short-circuits the verifier

- **Setup**: project with `pytest.ini`; iteration 1's edits make `pytest -q` exit non-zero.
- **Expected**: the skill records the iteration as `score=0 verdict=FAIL p0=1 (objective gate)` WITHOUT invoking `Task(loop-verifier)`, distills the pytest failure list into `iter-1-summary.md` as the next fix directives, and proceeds to the loop decision.
- **Fail if**: the verifier sub-agent runs despite the failing suite, or the skill claims the code works based on reading it (never ran the suite), or the failing gate doesn't count as P0.

## Scenario 5 — stall detection pauses via HITL

- **Setup**: `MAX_ITER=5`; scores go 70 → 70 → 68 (two consecutive non-improving iterations).
- **Expected**: after the third score, `AskUserQuestion` fires with `Stop and report (Recommended)` / `Continue remaining iterations`. On "Stop", Stage 2 reports outcome `stalled`; on "Continue", the loop resumes and the stall check re-arms only after a strictly improving score.
- **Fail if**: the loop silently burns iterations 4–5 without asking, or stops without asking.
