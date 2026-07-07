# Autorun — Stage 9 Output Templates & Hard-Stop Message

Read this when authoring the Stage 9 final output (working-directory reconciliation bash + pipeline-report markdown template + user-facing message), or when emitting the hard-stop message on an immediate-stop condition. The Stage 9 trigger and the completion gate stay in SKILL.md.

## 9.0 Ensure working-directory consistency

Under the v5.9+ two-phase policy, Stage 8's `/pr-merge --auto` performs the Sprint→Main handoff itself (Step 8.5 `--auto` `cd`s to the main worktree) and then removes the sprint worktree at the end of Step 9. After the sub-skill returns, the parent autorun context is *expected* to already be in the main worktree — but it is not guaranteed that the Skill tool propagates a sub-skill's cwd change to the parent context. Before authoring the Stage 9.1 output, explicitly `cd` into the main worktree:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"
astra_state_load "autorun-{FEATURE_SLUG}"   # recover MERGE_RESULT, SPRINT_N, WT_PATH (explicit scope — write the literal slug)

# If Stage 8 succeeded in merging and removed the worktree we should already be in the main worktree,
# but cwd may be lost at the Skill invocation boundary. Always cd to the main worktree.
MAIN_ROOT=$(astra_main_worktree_root)
if [ -z "$MAIN_ROOT" ] || [ ! -d "$MAIN_ROOT" ]; then
  echo "ERROR: cannot determine the main worktree path" >&2
  exit 1
fi
cd "$MAIN_ROOT"

# If the merge succeeded, dev is up to date — but explicitly sync to ensure the output is written against the correct base.
if [ "$MERGE_RESULT" = "success" ]; then
  git fetch origin dev 2>/dev/null
  git checkout dev 2>/dev/null
  git pull --rebase origin dev 2>/dev/null || true
fi
```

**Merge failure or skipped case**: the sprint worktree remains and Stage 8 was skipped. In that case it makes sense to write the output inside the worktree, but if autorun already `cd`-ed into the main worktree, reference the worktree path explicitly when writing it:

```bash
if [ "$MERGE_RESULT" != "success" ]; then
  REPORT_DIR="$MAIN_ROOT/.astra-worktrees/sprint-${SPRINT_N}-${FEATURE_SLUG}/docs/sprints/sprint-${SPRINT_N}-${FEATURE_SLUG}"
else
  REPORT_DIR="$MAIN_ROOT/docs/sprints/sprint-${SPRINT_N}-${FEATURE_SLUG}"
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
  ✅ Merge to dev complete — you are now back in the main worktree (dev).
  To start the next sprint, run /autorun or /sprint-init.

{On unresolved failure}:
  ❗ /pr-merge could not auto-execute.
  Cause: {Critical issues remain / merge conflict / environment error / test failure / non-shared main branch}
  After resolving:
    1. cd into the sprint worktree and run /pr-merge (Sprint Phase: PR refresh + review fixes).
    2. cd into the main worktree and re-run /pr-merge to finalize the merge.
  Or run /pr-merge --auto from the sprint worktree to chain both phases again.
═══════════════════════════════════════════════════════
```

### 9.3 `/pr-merge --auto` invocation policy
- Auto-invoke `/pr-merge --auto` in Stage 8 only when tests passed (early exit).
- On unresolved failure (MAX_ITER exhausted / ENV_ISSUE abort), do not invoke; just author the output in Stage 9.
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
