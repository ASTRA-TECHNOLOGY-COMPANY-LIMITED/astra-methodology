# Autorun — End-of-Iteration Mechanics (7.5.1)

Read this at the end of **every** iteration of the Stage 7.5 loop, when snapshotting changed files and authoring `iter-{CURRENT_ITER}-summary.md`. The baseline snapshot bash and the summary template live here; the loop's control flow (early-exit / max-iter / classification branch) stays in SKILL.md.

## 7.5.1 End-of-iteration handling (always run at the end of every iteration)

**Changed-file tracking mechanism**: do not rely on git diff (autorun does not commit mid-pipeline — **single exception**: in v5.10+ Stage 3, `/blueprint --auto` makes a single blueprint commit to the sprint branch inside the sprint worktree (previously v5.1–5.9: to dev for visibility). That happens *before* the iteration loop starts, so it does not affect the baseline snapshot). Instead, **snapshot the baseline file list at iteration start** and diff at end.

1. **At iteration start (once)**: create `{ITER_DIR}/iter-{CURRENT_ITER}-baseline.txt`:
   ```bash
   # Snapshot the file list (with mtime) of the tracked directories.
   # Use -exec stat to be compatible with both macOS (BSD) find and Linux (GNU) find.
   # (BSD find doesn't support -printf, so use `stat -f '%N %m'`.)
   find docs/planner/{NNN}-{slug} docs/blueprints/{NNN}-{slug} \
        src docs/tests/test-cases/sprint-{N}-{slug} \
        -type f 2>/dev/null \
        -exec stat -f '%N %m' {} \; 2>/dev/null \
        | sort > {ITER_DIR}/iter-{CURRENT_ITER}-baseline.txt
   # On Linux (GNU coreutils stat) the command above may fail.
   # In that case fall back to: -exec stat -c '%n %Y' {} \;
   ```
   - In iteration 1, the baseline may be empty (normal).
   - Files autorun edits directly are detected by mtime changes.
   - **Platform detection**: branch on `uname -s` (Darwin/Linux) when needed (macOS: `stat -f '%N %m'`, Linux: `stat -c '%n %Y'`).

2. **At iteration end**: take a current snapshot the same way and diff against the baseline:
   ```bash
   # Take the current snapshot the same way, then compare.
   diff {ITER_DIR}/iter-{CURRENT_ITER}-baseline.txt \
        <(find docs/planner/{NNN}-{slug} docs/blueprints/{NNN}-{slug} \
               src docs/tests/test-cases/sprint-{N}-{slug} \
               -type f 2>/dev/null \
               -exec stat -f '%N %m' {} \; 2>/dev/null | sort) \
        | grep '^>' | awk '{print $2}' > /tmp/changed_files.txt
   ```
   - Record the result in the "Changed deliverables" section of the summary.

3. **Author the iteration summary**: create `{ITER_DIR}/iter-{CURRENT_ITER}-summary.md` (≤ 200 lines):
   ```markdown
   # Iteration {i} Summary

   **Result**: PASS / FAIL
   **Duration**: {duration}
   **Tests**: {passed}/{total}

   ## Changed deliverables (this iteration; baseline diff result)
   - {list of file paths — extracted from /tmp/changed_files.txt}

   ## Failure classification (FAIL only)
   - **Classification**: CODE_BUG / SPEC_GAP / DESIGN_MISALIGN / ENV_ISSUE
   - **Evidence**: {1–3 lines summarizing the failure message / stack / log essentials}
   - **Next re-entry stage**: Stage {3|5|2|1|abort}
   - **Fix direction**: {1–2 lines — which file, which part, how to fix}
   - **Files to edit** (the next iteration will Edit these): {concrete path list}

   ## Remaining P0 issues
   - {P0 items from planner-reviewer / blueprint-reviewer / design-token-validator}

   ## Next iteration input context (the next round should read)
   - Deliverables to read: {path list — the "Files to edit" above + 1–2 directly dependent documents}
   - Do NOT read: the entire blueprint or planning documents (no reloading)
   ```

4. Append `{iter, result, classification, target_stage, changed_files_count}` to `ITER_HISTORY`.
