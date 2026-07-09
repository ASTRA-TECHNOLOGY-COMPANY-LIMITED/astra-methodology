# Autorun — Resume Mode & Reference Notes

Read this when re-invoking `/autorun` on a feature that already has partial deliverables (idempotent resume / recovery), or when you need the appendix material (usage caveats, inter-skill relationships, ASTRA 4-principle mapping). Not needed on a first, clean run.

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
| `/pr-merge` | **Auto-invoked in Stage 8 as `/pr-merge --auto`** (only when tests pass). Not invoked on unresolved failure. v5.16+ adaptive isolation: for an **in-place sprint (default, `IN_PLACE_SPRINT=1`)** the sprint branch lives in the main worktree, so `--auto` merges **single-phase in place** (commit → PR → review + fix → merge → promotion → sprint-branch cleanup) with no `cd` and no worktree. For an **escalated worktree sprint** it falls back to the v5.9+ two-phase flow — Sprint Phase (PR + review + fix) → auto-`cd` to the main worktree → Main Phase (merge) → worktree removal, end-to-end in one invocation. Without `--auto` in worktree mode, Sprint Phase stops after the review loop and the user finalizes from the main worktree. |
| `/check-naming`, `/check-convention` | Replaced by auto-applied skills + validation agents |

## ASTRA 4-principle application

| Principle | Pipeline application |
|---|---|
| **Think Before Coding** | Ambiguity validation and direction clarification in the planning stage (/service-planner) |
| **Simplicity First** | ⚠️ Bundle of broad deliverable-generating skills → *principle exception* (noted in CLAUDE.md). Internal code still follows the 4 principles. |
| **Surgical Changes** | Add only a new feature directory without modifying existing code |
| **Goal-Driven** | Existence of each stage's deliverable files is a clear success criterion |

**Final note**: this skill is classified as a *broad deliverable-generating skill* and is not bounded by Simplicity First (see the "ASTRA auto-builder exception" section in CLAUDE.md). However, every piece of code generated internally still follows the coding convention and the 4 principles.
