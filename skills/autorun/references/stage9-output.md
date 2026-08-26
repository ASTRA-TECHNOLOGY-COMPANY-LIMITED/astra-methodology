# Autorun — Stage 9 Output Templates & Hard-Stop Message

Read this when authoring the Stage 9 final output (working-directory reconciliation bash + pipeline-report markdown template + user-facing message), or when emitting the hard-stop message on an immediate-stop condition. The Stage 9 trigger and the completion gate stay in SKILL.md.

## 9.0 Ensure working-directory consistency

Stage 8's `/pr-merge --auto` ran the v5.9+ two-phase workflow end-to-end (v5.19+, every sprint is a worktree sprint) — Sprint Phase inside the worktree → Step 8.5 `cd` to the main worktree → Main Phase merge → sprint-worktree removal at the end of Step 9. After the sub-skill returns, the parent autorun context is *expected* to already be in the main worktree, but the Skill tool does not guarantee it propagates a sub-skill's cwd change. Explicitly `cd` back.

Resolve the main worktree root and settle the cwd there before authoring the Stage 9.1 output:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(find ~/.claude/plugins/cache -maxdepth 3 -type d -path '*/astra-methodology/*' 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"
astra_state_load "autorun-{FEATURE_SLUG}"   # recover MERGE_RESULT, SPRINT_N, WT_PATH (explicit scope — write the literal slug)

MAIN_ROOT=$(astra_main_worktree_root)
if [ -z "$MAIN_ROOT" ] || [ ! -d "$MAIN_ROOT" ]; then
  echo "ERROR: cannot determine the main worktree path" >&2
  exit 1
fi

# The worktree may have lost the cwd at the Skill boundary — settle in the main worktree.
cd "$MAIN_ROOT"

# If the merge succeeded, dev is up to date — but explicitly sync to ensure the output is written against the correct base.
if [ "$MERGE_RESULT" = "success" ]; then
  git fetch origin dev 2>/dev/null
  git checkout dev 2>/dev/null
  git pull --rebase origin dev 2>/dev/null || true
fi
```

**Merge failure or skipped case**: Stage 8 was skipped, so the sprint worktree remains and holds the deliverables. Point `REPORT_DIR` accordingly:

```bash
if [ "$MERGE_RESULT" = "success" ]; then
  REPORT_DIR="$MAIN_ROOT/docs/sprints/sprint-${SPRINT_N}-${FEATURE_SLUG}"
else
  REPORT_DIR="$MAIN_ROOT/.worktrees/sprint-${SPRINT_N}-${FEATURE_SLUG}/docs/sprints/sprint-${SPRINT_N}-${FEATURE_SLUG}"
fi
```

## 9.1 Author the pipeline-execution summary
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
2. For further review, ask for a senior-perspective pass in the session:
   - Dev review: "개발자 관점에서 검토해줘"
   - Test review: "테스터 관점에서 검토해줘"

**On unresolved failure**:
1. Review the deliverables above (inside the preserved sprint worktree) and apply fixes.
2. Fix inside the sprint worktree and re-run `/pr-merge` there.
3. For related reviews:
   - Planning review: `Task(planner-reviewer)`
   - Design / dev / test review: ask for a senior-perspective pass in the session ("디자이너/개발자/테스터 관점에서 검토해줘")
```

**Completion Gate**: before printing 9.2, verify the file was actually written (`[ -f "$REPORT_DIR/pipeline-report.md" ]`) and that every ✅/❌ mark in it traces to a check executed in this session (test-result line, gh pr state, worktree list). Then clear pipeline state: `astra_state_clear`.

## 9.2 User-facing message output

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
  ✅ Merge to dev complete — you are on dev in the main worktree.
  To start the next sprint, run /autorun or /sprint-init.

{On unresolved failure}:
  ❗ /pr-merge could not auto-execute.
  Cause: {Critical issues remain / merge conflict / environment error / test failure / non-shared main branch}
  The sprint worktree (.worktrees/sprint-{N}-{feature-slug}/) is preserved with all deliverables.
  After resolving inside it, re-run /pr-merge there — it chains Sprint Phase and Main Phase itself
  (or /pr-merge --auto to auto-approve the merge confirmation).
═══════════════════════════════════════════════════════
```

### 9.3 `/pr-merge --auto` invocation policy
- Auto-invoke `/pr-merge --auto` in Stage 8 only when the Stage 7.6 adversarial verification gate passed (tests PASS ∧ score ≥ 90 ∧ P0 == 0).
- On unresolved failure (MAX_ITER exhausted / verifier FAIL at max / ENV_ISSUE abort), do not invoke; just author the output in Stage 9.
- In situations that truly need HITL (gh auth, merge conflict, Critical issues), `/pr-merge` itself stops; autorun reflects that in the output as-is.

## Hard-Stop output format
Emitted on an immediate-stop condition (see the Failure-handling policy in SKILL.md):

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
