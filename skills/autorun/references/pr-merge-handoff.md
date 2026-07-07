# Autorun — Stage 8 `/pr-merge --auto` Two-Phase Handoff & HITL Triggers

Read this for the full Stage 8 detail: the two-phase workflow table and the exhaustive HITL/blocker enumeration `/pr-merge --auto` surfaces. The mainline (invoke `Skill('pr-merge', '--auto')`, the always-on promotion HITL, the `MERGE_RESULT` value contract) stays in SKILL.md.

## 8.1 Two-phase workflow (v5.9+, single invocation under `--auto`)

`/pr-merge --auto` runs Sprint Phase → handoff → Main Phase end-to-end:

| Phase | Step | Handling |
|---|---|---|
| Sprint Phase (sprint worktree) | Commit uncommitted changes | auto (bypasses confirmation prompt) |
| Sprint Phase | Branch sync (`staging→dev` only — `main→staging` excluded; promotion modes skip cascade entirely) | auto, halts on conflict (HITL) |
| Sprint Phase | Create PR | auto (ASTRA template) |
| Sprint Phase | Code review (feature-dev:code-reviewer agent) | auto |
| Sprint Phase | Fix Critical/High issues (up to 3 iterations) | auto (Surgical Changes principle) |
| Sprint→Main handoff | `cd` to main worktree (Step 8.5 under `--auto`) | auto (skill performs the transition) |
| Main Phase (main worktree) | Final merge confirmation prompt | auto-approve |
| Main Phase | `gh pr merge` (sprint PR → integration branch) | auto |
| Main Phase | **Step 8.4.5 promotion target (dev / staging / skip)** | **HITL — `AskUserQuestion` always fires, even under `--auto`** |
| Main Phase | Promotion PR (only if user picked dev or staging) | auto (no fresh review — source sprint PR already passed) |
| Main Phase | **Remove sprint worktree** | auto (cwd ends in main worktree (dev)) |

## 8.2 HITL trigger conditions

In the following situations, `/pr-merge --auto` either halts (true blockers) or surfaces an `AskUserQuestion` prompt — autorun receives both directly and forwards them to the user as-is.

**Always-on HITL (not a blocker — a routine decision point under `--auto`)**:
- **Step 8.4.5 promotion target after sprint→integration merge**: `/pr-merge` asks the user to pick `dev` (standard) / `staging` (fast hotfix) / `skip` (defer). Even with `--auto`, this prompt is always shown — the deployment surface choice has no safe unattended default. autorun pauses here for the user's answer, then continues automatically through promotion-PR creation, merge, and worktree removal. This is the only routine HITL point in autorun once the pipeline is running.

**True blockers (halt + show guidance)**:
- **gh CLI not authenticated**: shows `gh auth login` guidance and exits
- **Cascade merge conflict**: prints the conflicting files and exits (manual resolution required)
- **Rebase conflict** (target branch → work branch): same
- **Critical review issues ≥ 1 remain after MAX iterations**: merge blocked (`gh pr merge` not called)
- **MAX iterations reached + only High issues remain**: `/pr-merge`'s own `AskUserQuestion` fires (a/b/c choice). autorun surfaces that prompt to the user as-is — does not bypass it.
- **Multiple pending sprint PRs on Main Phase entry** (rare): when `/pr-merge --auto` `cd`'s to the main worktree and the auto-detection in Step 3.5 finds more than one open `feat/sprint-*` PR against the integration namespace, `/pr-merge` asks the user to pick which one to merge (HITL preserved even under `--auto`, because picking the wrong one is destructive). Normally autorun only produces a single sprint PR, so this trigger rarely fires.
- **Main worktree on a non-shared branch**: the `--auto` handoff (Step 8.5) verifies the main worktree is on `main`/`master`/`staging`/`dev`. If it is on a custom branch, the skill aborts rather than risk a merge into the wrong base.
