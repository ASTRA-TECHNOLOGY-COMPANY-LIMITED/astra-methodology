---
name: pr-merge
description: "Runs an automated iterative cycle from PR creation through code review, issue fixes, and merge. In a sprint worktree (non-main), this command handles only the commit → push → PR-create → code-review → fix → re-review phase and then stops; the actual merge must be executed from the main worktree by re-invoking `/pr-merge` (the command auto-detects pending sprint PRs whose base is dev). With the --auto flag (e.g., from autorun), Sprint Phase completes and the command then auto-cd's into the main worktree to continue with Main Phase (merge + worktree removal) in a single invocation. Every confirmation prompt is auto-approved except for safe HITL points (gh authentication, merge conflicts, Critical issues)."
argument-hint: "[max-iterations] [--no-review] [--draft] [--auto] [--patch|--minor|--major] [--staging] [--main]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Agent
---

# ASTRA PR Review & Merge Workflow (v5.9+)

Automates the entire cycle from commit through code review, issue fixes, merge, and worktree removal.
The review → fix → re-review loop runs automatically up to the max iteration count.

**Branch strategy**: `feature → dev → staging → main`

**Two-phase policy (v5.9+)**: To keep the merge action observable from the main worktree (where the cascade, dev branch, and version bumps live), `/pr-merge` splits into two phases keyed off the current worktree location:

- **Sprint Phase** — invoked from inside a sprint worktree (`.astra-worktrees/sprint-<N>-<name>/`). Runs commit → push → PR creation → code review → automatic Critical/High fixes (the iteration loop). **Stops immediately after the review loop converges.** The actual `gh pr merge` and worktree removal are NOT performed here. The user is instructed to `cd` to the main worktree and re-invoke `/pr-merge` to finalize the merge.
- **Main Phase** — invoked from the main worktree (on a shared branch: main/master/staging/dev). Auto-detects open PRs whose base is `dev` and head is a sprint branch (`feat/sprint-*`). If exactly one such PR exists, merges it; if multiple exist, asks the user to pick; if none exists, falls back to the legacy one-shot path (Step 4.1 temporary worktree).
- **`--auto` flag** — when Sprint Phase completes successfully and the user passed `--auto`, the skill itself `cd`'s into the main worktree and continues directly into Main Phase (merge + cleanup), so `/autorun` and `/sprint-init --auto` still end in a single invocation as before.

**Worktree isolation policy (v5.0+)**: sprint-unit work happens inside the `.astra-worktrees/sprint-<N>-<name>/` worktree created by `/sprint-init`. Immediately after Main Phase merges into a shared branch (dev), it automatically removes the worktree. The main worktree always stays on a shared branch (main/staging/dev/master), so other Claude Code sessions are not affected by branch switches. Source the helpers from `$CLAUDE_PLUGIN_ROOT/scripts/worktree-helpers.sh`.

> **v5.0+ change**: `--start` mode is removed. All worktree creation is handled by `/sprint-init`. For users who worked one-off in the main worktree without `/sprint-init` and then invoked `/pr-merge`, Step 4.1 handles the fallback automatically (one-shot: PR creation + merge in a single invocation).
>
> **v5.9+ change**: the merge step (`gh pr merge`) only runs from the main worktree. Inside a sprint worktree, `/pr-merge` finishes after the review loop and asks the user to re-invoke it from the main worktree (unless `--auto` is set, in which case the skill performs the cross-worktree continuation itself).

## Execution Procedure

### Step 1: Argument parsing and preconditions

Parse `$ARGUMENTS` to determine options:

- **max-iterations**: numeric argument → max review-iteration count (default: 3)
- **--no-review**: skip code review; just commit → push → create PR → merge
- **--draft**: create the PR in Draft state
- **--auto**: unattended mode — auto-approve every `AskUserQuestion` prompt except for safe HITL points (see table below). Used when invoked from a parent pipeline like `/autorun`.
- **--patch / --minor / --major**: version-bump type (default: --patch)
- **--staging**: promotion mode — merge `dev` → `staging`
- **--main**: promotion mode — merge `staging` → `main`

**Mode decision**:
- `--staging` or `--main` → promotion mode (main-worktree only)
- Otherwise → default mode. Phase is decided by current location:
  - Inside a sprint worktree (`astra_is_isolated_worktree` is true) → **Sprint Phase**
  - In the main worktree on a shared branch (main/master/staging/dev) → **Main Phase** (auto-detect pending sprint PR; if none, Step 4.1 one-shot fallback)
  - In the main worktree on a work branch (compatibility) → one-shot fallback handled as before

**`--auto` flag policy**:

| Point | `--auto` behavior | Notes |
|-------|-------------------|-------|
| Step 6 commit confirmation (Sprint Phase) | auto-approve → commit immediately | change summary is still printed |
| Step 8.5 Sprint Phase → Main Phase handoff | `cd` to main worktree + continue automatically | normal mode prints guidance and exits |
| Step 8.3 final-merge confirmation (Main Phase) | auto-approve → merge immediately | PR metadata is still printed |
| Step 8.1 MAX reached + 0 Critical | **HITL preserved** (the existing AskUserQuestion as-is) | remaining High requires user judgment |
| Step 8.1 MAX reached + ≥ 1 Critical | **always halt** | unconditional, auto or manual |
| gh CLI not authenticated | **halt** + guidance | true blocker (auth cannot be automated) |
| Cascade / rebase merge conflict | **halt** + show conflicting files | true blocker (merge requires judgment) |
| dev branch absent on remote | auto-create and proceed | safe default |
| Multiple pending sprint PRs in Main Phase | `AskUserQuestion` (HITL preserved) | even `--auto` cannot pick blindly — picking the wrong PR is destructive |

> `--auto` does not bypass *safety gates* — on true blockers (auth, conflict, Critical, ambiguous PR), it halts just like normal mode.

Validate the following preconditions:

1. **gh CLI authentication**: run `gh auth status` to check the GitHub CLI auth state. If not authenticated, instruct the user to run `gh auth login` and abort.
2. **Clean-state check**: run `git status` to understand the current state (uncommitted changes, staged files, etc.).
   - In promotion mode, if there are uncommitted changes, warn and abort (run only from a clean state). Instruct the user to commit, stash, or discard them first and re-run.
3. **Load worktree helpers**: source the worktree helpers in every Bash step:
   ```bash
   PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
   if [ -z "$PLUGIN_ROOT" ] || [ ! -f "$PLUGIN_ROOT/scripts/worktree-helpers.sh" ]; then
     echo "ERROR: CLAUDE_PLUGIN_ROOT not found. Check the plugin cache path." >&2
     exit 1
   fi
   source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"
   ```
   After that, use the `astra_*` functions.

   **Per-mode worktree-location guard**:
   - **Promotion mode (`--staging`, `--main`)**: must run in the main worktree. If invoked inside an isolated worktree, instruct the user to move to the main worktree and re-run, then abort:
     ```bash
     astra_ensure_main_worktree || exit 1
     ```
   - **Default mode**: phase is decided by location.
     - **Inside a sprint worktree** → Sprint Phase (Step 4 → Step 5 → … → Step 8.2 → Step 8.5 handoff). The merge itself is deferred to Main Phase.
     - **In the main worktree** → Main Phase. Step 3.5 first checks whether an open PR with base `dev` and a `feat/sprint-*` head exists. If yes, jump to Main Phase merge (Step M1). If no, fall through to Step 4 / Step 4.1 (one-shot fallback for users who edited the main worktree directly).

### Step 1.1: Auto-select target branch (default mode only)

If not in promotion mode, set the target branch automatically to **`dev`**. Do not ask the user.

`{target-branch}` = `dev`

> **Note**: in every subsequent step, `{target-branch}` refers to the `dev` branch.

### Step 2: Branch sync (common to all modes)

Before all modes, pull `main`, `staging`, `dev` to the latest. Cascade merge is restricted to `staging → dev` only — `main → staging` is never run automatically by `/pr-merge` (operate on `main` only via the explicit `--main` promotion).

Save the current branch as `{current-branch}`.

#### Step 2.1: Remote fetch and per-branch pull

```bash
git fetch origin
```

`main`, `staging`, `dev` are **shared branches**, so handle them directly in the main worktree (not subject to worktree isolation). For each branch:
1. Check remote existence with `git ls-remote --heads origin {branch}`.
2. Skip branches that don't exist on the remote (warning only).
3. For remote-existing branches, if there's no local branch, create a tracking branch with `git checkout -b {branch} origin/{branch}`.
4. If the local branch already exists, checkout and pull:
   ```bash
   git checkout {branch}
   git pull --rebase origin {branch}
   ```

> **Note**: shared-branch checkouts happen consolidated in the main worktree. Other sessions working on a work branch in an isolated worktree are not affected.

> **Required**: the `{target-branch}` branch must exist. If `{target-branch}` is missing from the remote:
> - **Normal mode**: ask the user via **AskUserQuestion** whether to create `{target-branch}` from the default branch. If declined, abort.
> - **`--auto` mode**: auto-create `{target-branch}` from the default branch (`main`/`master`), push, and continue.
>
> (Since Step 1.1 runs before Step 2 in default mode, the `{target-branch}` value is already determined.)

#### Step 2.2: Cascade merge (staging → dev)

Sync upstream `staging` into downstream `dev`. The cascade scope is restricted to a single hop — `main → staging` is intentionally excluded so that production code on `main` is only touched via the explicit `--main` promotion.

**Per-mode cascade scope**:
- **Default mode**: run `staging → dev` (when both branches exist on the remote)
- **`--staging` promotion**: skip the cascade (no automatic `main → staging` sync; promote `dev → staging` as-is)
- **`--main` promotion**: skip the cascade (staging → main direction; no reverse sync needed)

When the cascade should run (default mode only):

1. **staging → dev** (when both `staging` and `dev` exist on the remote):
   ```bash
   git checkout dev
   git merge staging
   ```
   - On conflict: print the conflict file list and instruct the user to resolve manually; abort.
   - If there are changes after the merge: `git push origin dev`

2. `git checkout {current-branch}` to return to the original branch.

> **Note**: when the cascade merge has no changes (Already up to date), silently skip that step. If `staging` does not exist on the remote, skip the cascade entirely — do **not** fall back to `main → dev` (operating on `main` requires the explicit `--main` promotion).

### Step 3: Per-mode branching

- **Promotion mode** (`--staging` / `--main`): proceed to **Step 10**
- **Default mode**: proceed to **Step 3.5** (Main-Phase pending-PR detection) when in the main worktree, otherwise proceed to **Step 4** (Sprint Phase).

### Step 3.5: Main-Phase entry — detect pending sprint PR

Skip this step when invoked from inside a sprint worktree (`astra_is_isolated_worktree` returns true) — Sprint Phase always proceeds to Step 4.

In the main worktree on a shared branch (main/master/staging/dev), search for an open sprint PR awaiting merge:

```bash
PENDING_PRS=$(gh pr list --base dev --state open --json number,headRefName,title,url \
  --jq '[.[] | select(.headRefName | test("^feat/sprint-"))]')
PENDING_COUNT=$(echo "$PENDING_PRS" | jq 'length')
```

Branch on count:

- **`PENDING_COUNT == 0`** (no pending sprint PR): the user is in the main worktree without a sprint PR awaiting merge. This is the legacy one-shot path — fall through to **Step 4** (which routes to Step 4.1 fallback when the current branch is a shared branch). No `gh pr merge` is invoked unless a PR is created later in Step 7.
- **`PENDING_COUNT == 1`** (exactly one pending sprint PR): auto-select that PR. Save:
  ```bash
  PR_NUMBER=$(echo "$PENDING_PRS" | jq -r '.[0].number')
  PR_URL=$(echo "$PENDING_PRS" | jq -r '.[0].url')
  BRANCH_NAME=$(echo "$PENDING_PRS" | jq -r '.[0].headRefName')
  STARTED_FROM_ISOLATED=1     # so Step 9 removes the sprint worktree
  STARTED_FROM_SPRINT=0       # we are merging from the main worktree, not from inside the sprint worktree
  MAIN_PHASE_ENTRY=1          # Step 8.3 will jump straight to Step 8.4 (no Sprint Phase steps re-run)
  ```
  Print the PR summary (title, head, URL, change file count via `gh pr diff $PR_NUMBER --name-only | wc -l`) and proceed to **Step M1** (Main-Phase merge).
- **`PENDING_COUNT >= 2`** (multiple pending sprint PRs): the choice is destructive — print the list and ask via **AskUserQuestion** (HITL preserved even in `--auto`). Save the selected PR's metadata as above (with the same flags) and proceed to **Step M1**.

> **Why HITL on multi-PR even with `--auto`**: merging the wrong PR cascades to dev, triggers worktree removal of the wrong sprint, and is hard to undo. The cost of one prompt is far lower than the cost of a wrong merge.

---

## Sprint Phase (feature → PR creation + review loop)

### Step 4: Verify the work branch

Analyze the current branch and worktree location and branch:

```bash
CURRENT_BRANCH=$(git branch --show-current)
```

Three branching cases:

- **Inside a sprint worktree + work branch** (`astra_is_isolated_worktree` returns true and the current branch is not a shared branch): the *normal flow* — invoked from the sprint worktree created by `/sprint-init`. Set the following variables and proceed to **Step 5**:
  ```bash
  WT_PATH="$(pwd)"
  BRANCH_NAME="$CURRENT_BRANCH"
  STARTED_FROM_ISOLATED=1
  STARTED_FROM_SPRINT=1   # ← real sprint worktree; Step 8.3 will hand off to Main Phase (or auto-cd under --auto)
  ```
  > **Note**: the sprint worktree's branch name is typically `feat/sprint-<N>-<name>`, but isolated worktrees starting with other prefixes (`fix/`, `docs/`, etc.) are handled the same way.
- **Main worktree + shared branch (main/master/staging/dev)**: fallback case — direct dev changes without `/sprint-init`. Auto-create a temporary isolated worktree → proceed to **Step 4.1**.
- **Main worktree + work branch (feat/fix/docs/etc.)**: compatibility case for users who worked in the main worktree under pre-v4.1 policy. Set the following variables without forcing migration and proceed to **Step 5**:
  ```bash
  WT_PATH="$(pwd)"
  BRANCH_NAME="$CURRENT_BRANCH"
  STARTED_FROM_ISOLATED=0
  STARTED_FROM_SPRINT=0   # ← compat case: in-place merge in Step 8.3
  ```

### Step 4.1: Fallback — auto-create a temporary isolated worktree

> **When you reach this**: fallback path for users who invoke `/pr-merge` after making changes directly in the main worktree (dev) without `/sprint-init`. The normal flow is `/sprint-init` creates the sprint worktree in advance and you work there.

1. Analyze the current changes and recent work context via `git status` and `git log` to **auto-decide** an appropriate *intended* branch name (e.g., `feat/user-auth`, `fix/login-error`). Do not ask the user.
   - Determine the prefix from the nature of the changes: `feat/` (new feature), `fix/` (bug fix), `docs/` (documentation), `refactor/` (refactoring), `chore/` (config/build)
   - Determine the suffix by extracting key keywords from changed file names, the commit log, and directory structure
   - At this point this is an *intended* name. If the helper detects that the branch name/directory is already taken, it auto-appends `-2`, `-3` suffixes, so **the actually-used name must be read from the helper's return value**.
2. If there are uncommitted changes in the main worktree, stash them temporarily:
   ```bash
   STASHED=0
   if [ -n "$(git status --porcelain)" ]; then
     git stash push --include-untracked -m "astra-pr-merge-step4.1" || exit 1
     STASHED=1
   fi
   ```
3. Create a new branch in an isolated worktree. The helper absorbs `(branch, slug, .gitignore)` collisions and returns the *final* branch name and the absolute worktree path tab-separated.
   ```bash
   if ! out=$(astra_create_worktree_new "{intended-branch-name}" "origin/{target-branch}"); then
     # On creation failure, restore the stash and exit — ensure the user's changes are not trapped in stash
     if [ "$STASHED" = "1" ]; then
       git stash pop || echo "WARN: stash pop failed. Check 'git stash list'."
     fi
     exit 1
   fi
   IFS=$'\t' read -r BRANCH_NAME WT_PATH <<< "$out"
   # Validate the read result — empty string would cause cd to home and pollute another repo
   if [ -z "$WT_PATH" ] || [ ! -d "$WT_PATH" ]; then
     echo "ERROR: cannot determine the worktree path. Helper output: '$out'" >&2
     [ "$STASHED" = "1" ] && git stash pop || true
     exit 1
   fi
   echo "Work worktree: $WT_PATH (branch: $BRANCH_NAME)"
   ```
4. If a stash exists, move into the new worktree and restore there (linked worktrees share the main's stash list, so `git stash pop` brings the main's stash here and applies it):
   ```bash
   cd "$WT_PATH"
   if [ "$STASHED" = "1" ]; then
     git stash pop || {
       echo "WARN: stash-restore conflict. Resolve manually via 'cd $WT_PATH && git stash list'."
       exit 1
     }
   fi
   ```
5. From here on, all git operations (commit, push, post-merge cleanup) happen inside `$WT_PATH`. In subsequent steps of this SKILL.md, "current branch" means `$BRANCH_NAME` checked out in the isolated worktree.
6. `{branch-name}` refers to `$BRANCH_NAME` (the actual name decided by the helper); `{work-tree-path}` refers to `$WT_PATH`. A numeric suffix may have been appended, so subsequent steps use *the helper return value, not the intended name*.
7. Set the `STARTED_FROM_ISOLATED=1` flag (used in Step 9 to decide worktree removal and local-branch deletion). Also set `STARTED_FROM_SPRINT=0` — this is a fallback temp worktree (not a real sprint worktree), so Step 8.3 must route to in-place merge, not to the Sprint→Main handoff.

### Step 5: Sync the target branch

Step 2 already completed the cascade merge, so reflect the latest `{target-branch}` changes into the work branch. **Run inside the isolated worktree (`{work-tree-path}`)**:

```bash
cd "$WT_PATH"  # or already cd-ed
git merge origin/{target-branch}
```

- **No conflict**: proceed to the next step
- **Conflict**: print the conflict file list and instruct the user to resolve manually, then abort. The user remains inside the isolated worktree (`$WT_PATH`); after resolving the conflict, re-run `/pr-merge` — worktree is not auto-removed.

**Skip condition**: if Step 4.1 was just executed (isolated worktree created from `origin/{target-branch}`), it is already in sync, so skip.

### Step 6: Commit & push

Process uncommitted changes inside the isolated worktree:

1. Check changes via `git status` (working directory is `$WT_PATH`).
2. If there are changes, print a change summary.
   - **Normal mode**: confirm whether to commit via **AskUserQuestion**.
   - **`--auto` mode**: skip the confirmation prompt and proceed to the next step.
3. (Auto or after user confirmation):
   - Stage modified files with `git add` (excluding sensitive files like `.env`, `credentials`, etc.)
   - Analyze staged changes via `git diff --staged`
   - Check the recent commit-message style via `git log`
   - Analyze changes, write a commit message, and run `git commit`
4. Push to the remote via `git push -u origin "$BRANCH_NAME"` (when going through Step 4.1 — otherwise `git push -u origin {branch-name}`).

If there are no changes, skip this step.

> **Note**: the isolated worktree shares git metadata (`.git`) with the main worktree, so push/remote settings do not need separate configuration.

### Step 7: Create the PR

Check whether an existing PR exists, and create a new one if not:

1. Check existing PRs via `gh pr list --head "$BRANCH_NAME" --base {target-branch} --state open` (when going through Step 4.1 — otherwise substitute `{branch-name}`).
2. **If an existing PR exists**: print the PR URL and proceed to Step 8
3. **If no existing PR**: create a PR with the ASTRA template

```bash
gh pr create --base {target-branch} --title "{PR title}" --body "$(cat <<'EOF'
## Summary
- {change summary 1}
- {change summary 2}

## Test plan
- [ ] Code review passes
- [ ] Verify the tests run

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- If `--draft` is specified, add the `--draft` flag
- The PR title must be ≤ 70 chars
- Print the PR URL

After the PR exists (whether re-used or just created), capture its metadata so later steps (especially Step 8.5's handoff message and Step M1) can refer to it directly:

```bash
PR_URL=$(gh pr view "$BRANCH_NAME" --json url --jq '.url')
PR_NUMBER=$(gh pr view "$BRANCH_NAME" --json number --jq '.number')
```

**Proceed to Step 8.**

---

## Common: code-review & merge cycle

### Step 8: Code review

Initialize the review iteration count to 0.

If `--no-review` is specified, skip this step and proceed to Step 8.3.

Spawn the `feature-dev:code-reviewer` agent to run a code review:

```
Agent tool (subagent_type: "feature-dev:code-reviewer")
- Run a code review based on the PR's changes
- Analyze bugs, logic errors, security vulnerabilities, code-quality issues
- **Important**: do not suggest removing any file under the kubernetes/ directory
```

Classify the review results into 4 severity levels and print:

| Severity | Description | Examples |
|----------|-------------|----------|
| **Critical** | Must fix immediately; risk of production outage | SQL injection, null reference, data loss |
| **High** | Recommended fix; important bug or security issue | Unhandled exception, possible auth bypass |
| **Medium** | Code-quality improvement; no functional impact | Duplicate code, inefficient logic, unclear naming |
| **Low** | Style/convention; optional improvement | Formatting, missing comments, unused imports |

### Step 8.1: Review-result decision

Based on the review results, decide the next action:

- **Critical + High = 0**: review passes → proceed to **Step 8.3**
- **Critical + High > 0 AND iteration < MAX**: issues need fixing → proceed to **Step 8.2**
- **Iteration = MAX reached**: provide options via **AskUserQuestion**
  - (a) Allow additional iterations (raise MAX)
  - (b) Ignore remaining issues and proceed to merge (but: do not offer this option if any Critical issue remains)
  - (c) Abort the workflow

**Merge-block condition**: if even one Critical issue remains, the merge cannot proceed.

### Step 8.2: Auto-fix issues & re-review

1. Show the issue list to the user.
2. **Proceed with auto-fix immediately, without user confirmation.**
3. Fix each issue in order — **apply the Surgical Changes principle**:
   - Read the relevant file and locate the issue.
   - With the Edit tool, **only modify the lines the review points out**. Do not arbitrarily "improve" adjacent code's formatting / comments / naming.
   - Do not refactor unbroken code (leave it alone unless flagged by an issue).
   - Remove only imports/variables made unused by your own fix. Leave pre-existing dead code as is.
   - Follow the existing style even if it differs from your taste.
   - Output a summary of the changes
   - **Test criterion**: every modified line must trace directly to an issue. Suggest splitting unrelated changes into a separate PR.
   - **Forbidden rule**: never delete files under the `kubernetes/` directory. Edits are allowed, but file-removal suggestions are ignored.
4. **Verifiable success criterion (Goal-Driven Execution)**: if the project has tests configured, run them to verify the fixes did not break existing functionality. If tests fail, address them first in the next iteration.
5. Stage the modified files with `git add`
6. Increment the iteration count by 1.
7. `git commit` — message format: "fix: address code review issues (iteration {N})" (N starts at 1)
8. Push to the remote with `git push`
9. **Return to Step 8** to re-review (keep the iteration count; do not reset)

> **Loop integrity**: this 5-attempt auto-debug loop is based on the principle that "an LLM can loop autonomously when there is a strong success criterion." With a weak criterion ("just make it work") the loop diverges — so every iteration has a clear verification gate of *review pass* or *test pass*.

### Step 8.3: Phase decision point

The review loop has converged (Critical + High = 0, or the user accepted the remaining issues in Step 8.1). Decide how to proceed based on the start-state flags set in Step 4 / Step 4.1 / Step 3.5:

- **Promotion mode (`--staging` / `--main`)**: proceed to **Step 8.4** (in-place merge — promotion always runs from the main worktree).
- **`STARTED_FROM_SPRINT=1`** (came from a real sprint worktree created by `/sprint-init`): proceed to **Step 8.5** (Sprint Phase ends; merge is deferred to Main Phase). This is the case the new two-phase policy is designed for.
- **`STARTED_FROM_SPRINT=0`** (Step 4.1 temp worktree, Step 4 main-worktree compat, or Step 3.5 Main-Phase entry): proceed to **Step 8.4** (in-place merge — we are operating relative to the main worktree).

```bash
case "$MODE" in
  --staging|--main) NEXT_STEP=8.4 ;;
  *)
    if [ "${STARTED_FROM_SPRINT:-0}" = "1" ]; then
      NEXT_STEP=8.5
    else
      NEXT_STEP=8.4
    fi ;;
esac
```

### Step 8.4: PR merge (Main Phase / promotion mode)

Print the PR URL, the review-result summary (pass/fail, iteration count), and the changed-file count.

- **Normal mode**: ask for final merge confirmation via **AskUserQuestion**. On decline, abort the workflow.
- **`--auto` mode**: skip the confirmation prompt and proceed directly to the merge.

After user confirmation (or under `--auto`), merge the PR:

1. If the PR is a Draft, first change to Ready via `gh pr ready`
2. Run the merge via `gh pr merge --merge`
   - **Do not use the `--delete-branch` option** — preserve the merged remote work branch for merge-history tracking, rollback reference, and syncing to other environments.
   - Local-branch cleanup is performed separately in Step 9 via `git branch -d` (safe delete).
   - Promotion-mode source branches (`dev`, `staging`) are likewise preserved (they are permanent branches).

**Mode check**: if `--staging` or `--main` is specified, proceed to **Step 11**; otherwise proceed to **Step 9**.

### Step 8.5: Sprint Phase → Main Phase handoff

The review loop has converged inside a sprint worktree. The merge itself runs from the main worktree (so the cascade, dev sync, and worktree removal happen in a stable location). Branch on the flag:

- **Normal mode**: print the handoff message and exit cleanly. The sprint worktree is preserved (the user's commits and PR are intact; only the merge is pending). Resolve `MAIN_ROOT` first so the printed `cd` path is concrete and copy-pastable:
  ```bash
  MAIN_ROOT=$(astra_main_worktree_root)
  ```
  ```
  ═══════════════════════════════════════════════════════
  ✅ Sprint Phase complete — review loop converged

  📦 Branch:     {BRANCH_NAME}
  🔗 PR:         {PR URL}
  🔁 Review iterations: {N}
  🛠  Fixed issues: Critical 0 / High 0 (remaining as accepted)

  ▶︎  Next step (merge runs in the main worktree):

      cd "{MAIN_ROOT}"
      /pr-merge

      The re-invoked /pr-merge will auto-detect this PR (#{PR_NUMBER}),
      ask for final merge confirmation, perform the merge, and remove
      the sprint worktree.
  ═══════════════════════════════════════════════════════
  ```
  After printing, **exit the workflow** (do NOT call `gh pr merge`, do NOT remove the worktree).

- **`--auto` mode**: continue automatically. The skill itself performs the cross-worktree transition so that `/autorun` and `/sprint-init --auto` still complete end-to-end in one invocation:
  ```bash
  MAIN_ROOT=$(astra_main_worktree_root)
  if [ -z "$MAIN_ROOT" ] || [ ! -d "$MAIN_ROOT" ]; then
    echo "ERROR: cannot determine the main worktree path" >&2
    exit 1
  fi
  cd "$MAIN_ROOT"
  # Ensure the main worktree is on a shared branch (it should be — the user
  # never branched off main/dev/staging/master from the main worktree under
  # the v5.0+ policy). If somehow detached, abort with a clear message.
  CURRENT_MAIN_BRANCH=$(git branch --show-current)
  case "$CURRENT_MAIN_BRANCH" in
    main|master|staging|dev) : ;;
    *)
      echo "ERROR: main worktree is on '$CURRENT_MAIN_BRANCH' (expected main/master/staging/dev). Aborting --auto handoff." >&2
      exit 1
      ;;
  esac
  ```
  Then proceed to **Step M1** (Main-Phase merge of the sprint PR just produced). `BRANCH_NAME`, `PR_URL`, `PR_NUMBER`, and `STARTED_FROM_ISOLATED=1` are already set from Sprint Phase.

### Step M1: Main-Phase merge (entry from Step 3.5 or Step 8.5)

This step exists for two callers:
- **Step 3.5 → M1**: the user re-invoked `/pr-merge` from the main worktree, and exactly one (or a user-picked) pending sprint PR was found.
- **Step 8.5 → M1**: `--auto` transitioned from Sprint Phase directly to here.

Both callers have `PR_NUMBER`, `PR_URL`, `BRANCH_NAME`, and `STARTED_FROM_ISOLATED=1` set, and the current working directory is the main worktree.

> **No re-review by default**: Sprint Phase already ran the review loop. If the user pushed additional commits between Sprint Phase and Main Phase, the existing PR review on GitHub remains the source of truth — we do not re-spawn the `feature-dev:code-reviewer` agent here. Users who want a fresh review can re-run Sprint Phase by `cd`'ing back into the sprint worktree and invoking `/pr-merge` there.

Proceed to **Step 8.4** (in-place merge using the variables set above).

---

## Cleanup (Main Phase only)

### Step 9: Cleanup and version update

After the merge, clean up the isolated worktree and the local environment. Step 8.4 always runs from the main worktree under the new two-phase policy (Step 3.5 / Step 4.1 enter the main worktree; Step 8.5 `--auto` `cd`'s here before Step M1). Re-anchor to the main worktree defensively in case any tool boundary lost the cwd:

1. **Re-anchor in the main worktree**:
   ```bash
   MAIN_ROOT=$(astra_main_worktree_root)
   cd "$MAIN_ROOT"
   ```
2. Fetch the latest remote state with `git fetch origin`.
3. Switch to `dev` with `git checkout dev` (even when `{target-branch}` is not dev, the final position is unified to dev).
4. Sync to latest with `git pull --rebase origin dev`.
5. **Remove the isolated worktree**: only when `STARTED_FROM_ISOLATED=1` (invoked from inside a sprint worktree, or started from a temporary worktree auto-created in Step 4.1):
   ```bash
   if [ "${STARTED_FROM_ISOLATED:-0}" = "1" ] && [ -n "${BRANCH_NAME:-}" ]; then
     astra_remove_worktree "$BRANCH_NAME"
   fi
   ```
   If `git worktree remove` fails (e.g., dirty changes in `{work-tree-path}`), the helper only prints a warning and the workflow continues. The compatibility case where you started on a work branch in the main worktree (`STARTED_FROM_ISOLATED=0`) skips worktree removal (the main worktree itself must not be removed).
6. **Delete the merged local branch**: only when `STARTED_FROM_ISOLATED=1`. Only if the PR has actually been merged, `git branch -d "$BRANCH_NAME"` (safe delete — fails if not merged):
   ```bash
   if [ "${STARTED_FROM_ISOLATED:-0}" = "1" ] && [ -n "${BRANCH_NAME:-}" ]; then
     git branch -d "$BRANCH_NAME" || echo "INFO: skipped deleting $BRANCH_NAME (not merged or already deleted on remote)"
   fi
   ```
   The compatibility case where you started on a work branch in the main worktree (`STARTED_FROM_ISOLATED=0`) is skipped because the current branch is checked out in the main worktree and cannot be deleted with `git branch -d`. If safe delete fails (not merged), only inform the user; do not force delete.
7. Print the final summary:

> **Note**: in default mode, version bumping is not performed. Version bumps run only in `--main` promotion (Step 11).

```
## PR Review & Merge complete

### Result summary
- PR: {PR URL}
- Merge: {branch-name} → {target-branch}
- Review iterations: {N}
- Fixed issues: Critical {n}, High {n}
- Status: ✅ merged

### Changes
- {commit summary 1}
- {commit summary 2}
```

---

## Promotion mode (--staging / --main)

### Step 10: Promotion prep

Promotion mode is the workflow that *promotes* code between branches.

**Branch mapping**:
- `--staging`: `{source-branch}` = `dev`, `{target-branch}` = `staging`
- `--main`: `{source-branch}` = `staging`, `{target-branch}` = `main`

**Validation procedure**:

> **Note**: in promotion mode, source/target are always shared branches (dev/staging/main), so they are not subject to worktree isolation. All checkouts run in the main worktree.

1. **Verify the source branch**: with `git ls-remote --heads origin {source-branch}`, check whether `{source-branch}` exists on the remote. If not, print an error message and abort.
2. **Verify the target branch**: with `git ls-remote --heads origin {target-branch}`, check whether `{target-branch}` exists on the remote.
   - **If it does not exist**: ask via **AskUserQuestion** whether to create `{target-branch}` from `{source-branch}`. On approval, create and push; on decline, abort.
3. **Switch to the source branch**: in the main worktree, `git checkout {source-branch}`
4. **Verify the diff**: with `git log origin/{target-branch}..origin/{source-branch} --oneline`, check whether commits to promote exist. If there is no diff, print "No changes to promote" and abort.
5. Show the commit list to the user.

### Step 10.1: Create the promotion PR

1. Check existing promotion PRs via `gh pr list --head {source-branch} --base {target-branch} --state open`
2. **If an existing PR exists**: print the PR URL and proceed to Step 8
3. **If no existing PR**: create a promotion PR

```bash
gh pr create --head {source-branch} --base {target-branch} --title "promote: {source-branch} → {target-branch}" --body "$(cat <<'EOF'
## Promotion: {source-branch} → {target-branch}

### Commits included
{commit list}

### Checklist
- [ ] Code review passes
- [ ] Tests pass

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- If `--draft` is specified, add the `--draft` flag
- Print the PR URL and proceed to **Step 8** (common code-review & merge cycle)

> **Note**: when fixing issues in Step 8.2, commit and push from `{source-branch}`.

---

## Promotion mode: cleanup

### Step 11: Promotion-completion cleanup

1. Fetch the latest remote with `git fetch origin`.
2. Switch to `{target-branch}` with `git checkout {target-branch}`.
3. Sync to latest with `git pull --rebase`
4. Do not delete the source branch in promotion (`dev`, `staging` are permanent branches).
5. Version bump runs only for `--main` promotion (release version management):
   - Verify the existence of `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
   - When the files exist, bump the SemVer version per the `--patch` / `--minor` / `--major` option:
     - `--patch` (default): `x.y.z` → `x.y.z+1`
     - `--minor`: `x.y.z` → `x.y+1.0`
     - `--major`: `x.y.z` → `x+1.0.0`
   - Update both files to the same version.
   - Commit directly to `main` and push: "chore: bump version to {new-version}"
6. **Return to the `dev` branch**: after promotion, switch to `dev` so subsequent development can continue seamlessly:
   ```bash
   git checkout dev
   git pull --rebase origin dev
   ```
7. Print the final summary:

```
## Promotion complete

### Result summary
- PR: {PR URL}
- Promotion: {source-branch} → {target-branch}
- Commits included: {N}
- Review iterations: {N}
- Version: {old-version} → {new-version} (only with --main)
- Status: ✅ promoted
```

---

## Quick Run Examples

```
# Two-phase (v5.9+) — inside a sprint worktree
#   Sprint Phase: commit → push → PR → review → fix loop, then exits.
#   The merge runs from the main worktree.
cd .astra-worktrees/sprint-3-user-auth
/pr-merge

# After Sprint Phase, finalize the merge from the main worktree
cd "$(git rev-parse --git-common-dir)/.."
/pr-merge      # auto-detects the pending sprint PR (base=dev, head=feat/sprint-*)
               # exactly one match → in-place merge confirmation
               # multiple matches → AskUserQuestion picks which PR

# Up to 5 review iterations (Sprint Phase only — Main Phase doesn't re-review)
/pr-merge 5

# Quick merge without code review (Sprint Phase: skip review and stop; Main Phase: merge directly)
/pr-merge --no-review

# Create as Draft PR then review (Sprint Phase)
/pr-merge --draft

# Run with minor version bump (only matters on --main promotion)
/pr-merge --minor

# Option combinations
/pr-merge 5 --minor --draft

# Unattended end-to-end (Sprint Phase → auto-cd to main worktree → Main Phase → merge → worktree removal)
/pr-merge --auto

# Promotion: dev → staging
/pr-merge --staging

# Promotion: staging → main (release)
/pr-merge --main

# Promotion + minor version bump
/pr-merge --main --minor

# Promotion + skip review
/pr-merge --staging --no-review
```

## Notes

- **Branch strategy**: promote code in the order `feature → dev → staging → main`.
- **Two-phase policy (v5.9+)**: `gh pr merge` only runs from the main worktree. Inside a sprint worktree, `/pr-merge` runs Sprint Phase (commit · push · PR · review · fix loop) and stops. The user then `cd`s into the main worktree and re-invokes `/pr-merge` — Step 3.5 auto-detects the pending sprint PR (`base=dev`, `head=feat/sprint-*`) and merges it. With `--auto`, the skill performs the cross-worktree transition itself so unattended pipelines still complete in one invocation.
- **Worktree policy (v5.0+)**: sprint worktrees are created by `/sprint-init` (`.astra-worktrees/sprint-<N>-<name>/`). Right after Main Phase merges into dev, the sprint worktree is auto-removed (Step 9). Cross-shared-branch (main/staging/dev/master) cascade merges and promotions run directly in the main worktree. If the workflow halts due to a conflict, the worktree remains — after resolving, re-run `/pr-merge` to continue.
- **Fallback flow (one-shot)**: when a user without `/sprint-init` invokes `/pr-merge` after making changes directly in the main worktree (dev), Step 3.5 finds no pending sprint PR, falls through to Step 4.1 which auto-creates a temporary isolated worktree, then runs Sprint Phase + Main Phase together in the same invocation (Step 8.3 routes to Step 8.4 in-place because we are conceptually in the main worktree's perspective). Use this for one-off work; starting with `/sprint-init` is Recommended in general.
- **Common preprocessing**: in every mode, pull `main` / `staging` / `dev` before execution. The cascade merge itself is restricted to `staging → dev` and runs only in default mode — promotion modes (`--staging`, `--main`) skip the cascade entirely. `main → staging` is never auto-cascaded; operate on `main` only via the explicit `--main` promotion.
- **Default mode**: the merge target branch is automatically set to `dev` (no user prompt). When running from `main`/`master`/`staging`/`dev`, a work branch is auto-created. The branch name is also auto-decided by analyzing the changes. If `{target-branch}` is missing on the remote, it is auto-created from the default branch.
- **Promotion mode (`--staging`)**: promote `dev` → `staging`. Skips the work-branch creation/commit steps and focuses on PR-based merging.
- **Promotion mode (`--main`)**: promote `staging` → `main`. As this is a release promotion, the version bump runs at this stage.
- Final checkout location after merge: default mode goes to `{target-branch}` (`dev`); promotion mode returns to the `dev` branch.
- If Critical issues remain, merging is blocked.
- On conflict, do not attempt auto-resolution; instruct the user and abort.
- The version bump runs only in `--main` promotion, and applies only to projects with `.claude-plugin/plugin.json`.
- Before commits and merges, user confirmation is always required. However, after-review issue fixes proceed automatically without user confirmation.
- **kubernetes protection rule**: during code review and issue fixes, do not delete files under the `kubernetes/` directory.
- **Remote-branch preservation policy**: after merging, remote work branches (`feat/*`, `fix/*`, `docs/*`, `refactor/*`, `chore/*`, etc.) are not deleted from the remote. They are preserved for merge-history tracking, rollback reference, and reuse in other environments. Only local branches are safely deleted with `git branch -d` (auto-skipped if unmerged).
- In promotion mode, source branches (`dev`, `staging`) are not deleted.
- **Surgical Changes principle**: during Step 8.2 issue fixes, change only the lines flagged by the review. Arbitrary refactoring, format changes, or naming "improvements" on adjacent code are forbidden. Every modified line must trace directly to an issue. Split unrelated improvements into a separate PR. (See: Behavioral Guardrails in the `coding-convention` skill.)
