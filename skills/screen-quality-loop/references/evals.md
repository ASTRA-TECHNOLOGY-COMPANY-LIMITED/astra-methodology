# screen-quality-loop — Behavioral Evaluation Scenarios

Read when validating changes to this skill's loop-control behavior. Each scenario states the setup, the expected behavior, and the failure mode the scenario guards against.

## Scenario 1: New mockup batch triggers one loop over the whole set

- **Setup**: `/service-planner` Step 6.F generates `SCR-001.html` … `SCR-005.html` + `index.html` + `styles.css` in `{OUTPUT_DIR}`.
- **Expected**: exactly ONE loop starts (MODE=mockup) covering all five screens as a single set; sibling baseline = the other SCR files + `index.html`; reports land in `{OUTPUT_DIR}/screen-quality/verify-{i}.md`; the Step 6 user confirmation fires only after the loop finishes and includes the final score.
- **Guards against**: one-loop-per-file explosion (5 loops × 5 iterations), and confirming mockups with the user before verification ran.

## Scenario 2: Editing an existing screen does NOT trigger the loop

- **Setup**: the user asks to change the button label and padding on an existing `src/pages/settings.tsx`.
- **Expected**: the loop is skipped (edit to an existing screen, not a new screen batch); normal auto-applied skills (`coding-convention`) still run. No `screen-verifier` invocation.
- **Guards against**: the loop firing on every UI touch and burning 5 sub-agent runs on a padding tweak.

## Scenario 3: Missing tail line is FAIL, never PASS

- **Setup**: iteration 2's `screen-verifier` output has a truncated report with no `ASTRA_SCREEN_RESULT:` line.
- **Expected**: the parent re-invokes the verifier exactly once; if the line is still absent, the iteration is recorded as `score=0 verdict=FAIL p0=unknown` in `verify-2.md` and the loop continues to the next iteration decision. The loop NEVER interprets prose ("overall the screens look excellent") as a PASS.
- **Guards against**: prose-based verdict inference and silent PASS on malformed verifier output.

## Scenario 4: Early exit on PASS

- **Setup**: iteration 1 scores 78 with 1 P0; the parent applies the fix directives; iteration 2's tail line is `ASTRA_SCREEN_RESULT: score=93 verdict=PASS p0=0 iter=2`.
- **Expected**: the loop exits at iteration 2 with outcome `achieved` — it does not run the remaining 3 iterations. The final report shows the 78 → 93 trajectory.
- **Guards against**: cap-filling (always burning 5 iterations regardless of the score).

## Scenario 5: Cap reached — honest report, caller not blocked

- **Setup**: 5 iterations complete with scores 60 → 71 → 79 → 84 → 88 (p0=1 remaining).
- **Expected**: the loop stops (no 6th iteration, no HITL asking to extend), prints outcome `max-iter` with the remaining P0 and the top fix directives from `verify-5.md`, and hands control back to the caller — `/service-planner` proceeds to Step 7 with the score noted; `/autorun` Stage 6 proceeds to 6.3. No success banner is printed.
- **Guards against**: unbounded iteration, mid-loop HITL inside unattended pipelines, and claiming success at 88/100.

## Scenario 6: Template-owned deliverables are out of scope

- **Setup**: `/manual-generator` produces a self-contained HTML manual; later, `/design-redesign --apply` retrofits three existing pages.
- **Expected**: neither run triggers this loop — manual/catalog/handoff/UAT-report HTML is owned by its generator's templates, and `/design-redesign` has its own audit-fix loop.
- **Guards against**: double-looping (two competing fix loops editing the same files) and misapplying app-screen consistency rules to document deliverables.
