---
name: pr-merge
description: "Runs an automated iterative cycle from PR creation through code review, issue fixes, and merge. v5.11+ uses an integration-branch model: sprint PRs (head=feat/sprint-*) target a feature- or fix-level integration branch (feat/<name> or fix/<name>) chosen interactively (pick from existing OR create new with user-chosen base). After the sprint PR merges into the integration branch, the user picks a promotion path — staging (fast/hotfix) or dev (standard) or skip — and a promotion PR is created and merged without a second review. In a sprint worktree, this command handles commit → push → PR-create → code-review → fix → re-review and then stops; the merge runs from the main worktree. With --auto, the command transitions phases by itself and uses safe defaults (reuse existing integration branch if name matches, else create new from dev; promotion = dev). Confirmation prompts auto-approve except for safe HITL points (gh authentication, merge conflicts, Critical issues, ambiguous multi-PR detection)."
argument-hint: "[max-iterations] [--no-review] [--draft] [--auto] [--patch|--minor|--major] [--staging] [--main]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Agent
---

# ASTRA PR Review & Merge Workflow (v5.11+)

Automates the entire cycle from commit through code review, issue fixes, integration-branch merge, promotion, and worktree removal.
The review → fix → re-review loop runs automatically up to the max iteration count.

**Branch strategy (v5.11+)**: `feat/sprint-<N>-<name>  →  feat/<name> | fix/<name>  (integration)  →  dev | staging  →  main`

The integration branch is the unit of promotion: pick any sprint's integration branch and push it to `staging` directly (fast hotfix path) or queue it via `dev` (standard path). Multiple sprints may target the same integration branch to accumulate a larger feature before promotion.

**Two-phase policy (v5.9+, retained)**: To keep the merge action observable from the main worktree (where the cascade, shared branches, and version bumps live), `/pr-merge` splits into two phases keyed off the current worktree location:

- **Sprint Phase** — invoked from inside a sprint worktree (`.astra-worktrees/sprint-<N>-<name>/`). Runs target-branch determination (Step 4.5: pick existing integration branch or create new with user-chosen base) → commit → push → PR creation against the integration branch → code review → automatic Critical/High fixes (the iteration loop). **Stops immediately after the review loop converges.** The actual `gh pr merge` and the promotion-path decision are NOT performed here. The user is instructed to `cd` to the main worktree and re-invoke `/pr-merge` to finalize.
- **Main Phase** — invoked from the main worktree (on a shared branch: main/master/staging/dev). Auto-detects open PRs whose `head` is a sprint branch (`feat/sprint-*`) and `base` is an integration branch (`feat/*` or `fix/*`). If exactly one such PR exists, merges it; if multiple exist, asks the user to pick; if none exists, falls back to the legacy one-shot path (Step 4.1 temporary worktree, target=dev). After the sprint PR merges into the integration branch, **Step 8.4.5** asks the user where to promote the integration branch (staging / dev / skip) and creates the promotion PR.
- **`--auto` flag** — when Sprint Phase completes successfully and the user passed `--auto`, the skill itself `cd`'s into the main worktree and continues directly into Main Phase (merge + promotion + cleanup), so `/autorun` and `/sprint-init --auto` still end in a single invocation as before. Under `--auto`, integration-branch selection reuses an existing branch with the inferred name or creates a new one from `dev`; promotion defaults to `dev` (safe standard path).

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
| Step 4.5 integration branch pick (Sprint Phase) | auto-reuse existing branch matching inferred name; else auto-create from `origin/dev` | safe default — no prompt |
| Step 4.5.4 base branch for new integration | always `origin/dev` | safe default — no prompt |
| Step 6 commit confirmation (Sprint Phase) | auto-approve → commit immediately | change summary is still printed |
| Step 8.5 Sprint Phase → Main Phase handoff | `cd` to main worktree + continue automatically | normal mode prints guidance and exits |
| Step 8.3 final-merge confirmation (Main Phase) | auto-approve → merge immediately | PR metadata is still printed |
| Step 8.4.5 promotion path (after integration merge) | auto-select `dev` (standard) → create + merge promotion PR | `staging` direct path requires explicit user choice |
| Step 10.0 promotion source (`--staging` / `--main`) | auto-select legacy bulk source: `dev` for `--staging`, `staging` for `--main` | feature-level integration-branch promotion requires explicit user choice |
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
     - **In the main worktree** → Main Phase. Step 3.5 first checks whether an open PR with `head` matching `feat/sprint-*` and `base` matching `^(feat|fix)/` exists (plus a backward-compat fallback to `base=dev` for pre-v5.11 PRs). If yes, jump to Main Phase merge (Step M1). If no, fall through to Step 4 / Step 4.1 (one-shot fallback for users who edited the main worktree directly).

### Step 1.1: Defer target branch (default mode only)

In v5.11+ the default-mode target branch is no longer the shared `dev` branch — it is an **integration branch** (`feat/<name>` or `fix/<name>`) so a single feature or bugfix can be promoted independently of the rest of `dev`. The actual integration branch is determined per phase, not here:

- **Sprint Phase** → **Step 4.5** picks (or creates) the integration branch *after* Step 4 confirms the sprint context. Existing integration branches under `feat/*` / `fix/*` are listed for the user to pick from; "create new" prompts for a base branch.
- **Main Phase** → **Step 3.5** discovers the integration branch implicitly from the pending sprint PR's `baseRefName`.
- **Step 4.1 fallback (one-shot)** → target stays `dev` (legacy one-shot behavior). Users who need integration-branch granularity should run `/sprint-init` first.

At this point, just initialize `TARGET_BRANCH=""` and continue. Subsequent steps that reference `{target-branch}` are interpreted relative to whichever phase set it. Step 2 (shared-branch sync) does *not* depend on `{target-branch}`.

> **Why the change**: feature-level / bugfix-level promotion means the integration branch can be merged directly to `staging` (fast hotfix path) or queued via `dev` (standard path). The choice is made post-merge in **Step 8.4.5**.

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

> **Required for promotion mode**: the `{target-branch}` branch must exist. If `{target-branch}` is missing from the remote:
> - **Normal mode**: ask the user via **AskUserQuestion** whether to create `{target-branch}` from the default branch. If declined, abort.
> - **`--auto` mode**: auto-create `{target-branch}` from the default branch (`main`/`master`), push, and continue.
>
> **Default mode**: `{target-branch}` is not yet determined at this point (Step 1.1 deferred it). Existence checks for the integration branch happen in **Step 4.5** (Sprint Phase) or **Step 3.5** (Main Phase).

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

In the main worktree on a shared branch (main/master/staging/dev), search for an open sprint PR awaiting merge. In v5.11+ the PR's base is an **integration branch** (`feat/<name>` or `fix/<name>`), not `dev` — so the filter matches by head pattern alone and includes the base name in the result:

```bash
PENDING_PRS=$(gh pr list --state open --json number,headRefName,baseRefName,title,url \
  --jq '[.[] | select(.headRefName | test("^feat/sprint-")) | select(.baseRefName | test("^(feat|fix)/"))]')
PENDING_COUNT=$(echo "$PENDING_PRS" | jq 'length')
```

> **Backward compatibility**: PRs created by pre-v5.11 `/pr-merge` use `baseRefName == "dev"`. If `PENDING_COUNT == 0` here, fall back to the legacy filter once before giving up:
> ```bash
> if [ "$PENDING_COUNT" = "0" ]; then
>   PENDING_PRS=$(gh pr list --base dev --state open --json number,headRefName,baseRefName,title,url \
>     --jq '[.[] | select(.headRefName | test("^feat/sprint-"))]')
>   PENDING_COUNT=$(echo "$PENDING_PRS" | jq 'length')
> fi
> ```

Branch on count:

- **`PENDING_COUNT == 0`** (no pending sprint PR): the user is in the main worktree without a sprint PR awaiting merge. This is the legacy one-shot path — fall through to **Step 4** (which routes to Step 4.1 fallback when the current branch is a shared branch). No `gh pr merge` is invoked unless a PR is created later in Step 7.
- **`PENDING_COUNT == 1`** (exactly one pending sprint PR): auto-select that PR. Save:
  ```bash
  PR_NUMBER=$(echo "$PENDING_PRS" | jq -r '.[0].number')
  PR_URL=$(echo "$PENDING_PRS" | jq -r '.[0].url')
  BRANCH_NAME=$(echo "$PENDING_PRS" | jq -r '.[0].headRefName')
  TARGET_BRANCH=$(echo "$PENDING_PRS" | jq -r '.[0].baseRefName')   # the integration branch
  STARTED_FROM_ISOLATED=1     # so Step 9 removes the sprint worktree
  STARTED_FROM_SPRINT=0       # we are merging from the main worktree, not from inside the sprint worktree
  MAIN_PHASE_ENTRY=1          # Step 8.3 will jump straight to Step 8.4 (no Sprint Phase steps re-run)
  ```
  Print the PR summary (title, head, base = integration branch, URL, change file count via `gh pr diff $PR_NUMBER --name-only | wc -l`) and proceed to **Step M1** (Main-Phase merge).
- **`PENDING_COUNT >= 2`** (multiple pending sprint PRs): the choice is destructive — print the list (each row showing head → base) and ask via **AskUserQuestion** (HITL preserved even in `--auto`). Save the selected PR's metadata as above (with the same flags, including `TARGET_BRANCH` = the chosen PR's `baseRefName`) and proceed to **Step M1**.

> **Why HITL on multi-PR even with `--auto`**: merging the wrong PR mutates the wrong integration branch (which then can be wrongly promoted in Step 8.4.5) and triggers worktree removal of the wrong sprint. The cost of one prompt is far lower than the cost of a wrong merge.

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

### Step 4.5: Determine integration target branch (Sprint Phase only)

Run this step **only when `STARTED_FROM_SPRINT=1`** (the normal flow from a real sprint worktree). Skip for:
- Step 4.1 fallback (temp worktree from main worktree without `/sprint-init`) → `TARGET_BRANCH="dev"` (legacy one-shot behavior, kept simple)
- Main worktree + work branch compat case (`STARTED_FROM_SPRINT=0` set in Step 4) → `TARGET_BRANCH="dev"`
- Promotion mode (`--staging` / `--main`) → target already set in Step 10

For the skipped cases, set `TARGET_BRANCH="dev"` and proceed to **Step 5**.

#### Step 4.5.1: Infer classification (feat vs fix)

Derive the integration-branch prefix from three signals, in priority order:

```bash
# 1) Count Conventional Commits on this sprint branch since branch-off from dev.
# Note: `grep -c` always prints a number to stdout (even "0" for no matches),
# so DO NOT chain `|| echo 0` — that would produce a multi-line value like "0\n0"
# and break the arithmetic comparisons below. Defaulting via :- handles the case
# where git log itself fails (e.g., shallow clone with no origin/dev ref).
FEAT_COUNT=$(git log origin/dev..HEAD --pretty=%s 2>/dev/null \
  | grep -cE '^(feat|feature)(\(.*\))?:')
FEAT_COUNT=${FEAT_COUNT:-0}
FIX_COUNT=$(git log origin/dev..HEAD --pretty=%s 2>/dev/null \
  | grep -cE '^(fix|bugfix|hotfix)(\(.*\))?:')
FIX_COUNT=${FIX_COUNT:-0}

# 2) Sprint slug keyword scan — BRANCH_NAME looks like feat/sprint-<N>-<slug>
SLUG=$(echo "$BRANCH_NAME" | sed -E 's|^[^/]+/sprint-[0-9]+-||')
SLUG_HINTS_FIX=$(echo "$SLUG" | grep -cE '(fix|bug|hotfix|patch|error|issue|typo|broken)')
SLUG_HINTS_FIX=${SLUG_HINTS_FIX:-0}

# 3) Blueprint context (best-effort — fail silently if blueprint missing)
BP_HINTS_FIX=0
BP_DIR=$(ls -d "docs/blueprints/"*"-${SLUG}" 2>/dev/null | head -1)
if [ -n "$BP_DIR" ] && [ -f "$BP_DIR/blueprint.md" ]; then
  BP_HINTS_FIX=$(grep -cE '(버그|장애|수정|결함|bug|fix|defect|hotfix|regression)' "$BP_DIR/blueprint.md" 2>/dev/null)
  BP_HINTS_FIX=${BP_HINTS_FIX:-0}
fi

# Decision rule: fix wins when commit signal favors fix OR (commit tie AND slug/blueprint hints)
if [ "$FIX_COUNT" -gt "$FEAT_COUNT" ]; then
  PREFIX="fix"
elif [ "$FIX_COUNT" = "$FEAT_COUNT" ] && [ $((SLUG_HINTS_FIX + BP_HINTS_FIX)) -ge 2 ]; then
  PREFIX="fix"
else
  PREFIX="feat"
fi
INFERRED_NAME="${PREFIX}/${SLUG}"
echo "Inferred integration branch: $INFERRED_NAME (commits: feat=$FEAT_COUNT fix=$FIX_COUNT, slug-hints=$SLUG_HINTS_FIX, blueprint-hints=$BP_HINTS_FIX)"
```

#### Step 4.5.2: List existing integration branches

```bash
git fetch origin --quiet
# Sort by recent activity, exclude sprint-* branches, keep only feat/* and fix/*
mapfile -t EXISTING_INTS < <(
  git for-each-ref --sort=-committerdate \
    --format='%(refname:lstrip=3)' \
    refs/remotes/origin/feat refs/remotes/origin/fix 2>/dev/null \
    | grep -vE '^(feat|fix)/sprint-' \
    | head -10
)
```

#### Step 4.5.3: Pick existing or create new

**`--auto` mode** — safe default (no prompts):
```bash
if printf '%s\n' "${EXISTING_INTS[@]}" | grep -qxF "$INFERRED_NAME"; then
  TARGET_BRANCH="$INFERRED_NAME"   # reuse existing
  echo "[--auto] Reusing existing integration branch: $TARGET_BRANCH"
else
  TARGET_BRANCH="$INFERRED_NAME"   # create new from origin/dev
  CREATE_NEW=1
  BASE_REF="origin/dev"
  echo "[--auto] Creating new integration branch: $TARGET_BRANCH (base: $BASE_REF)"
fi
```

**Normal mode** — branch on whether existing integration branches were found:

- **`EXISTING_INTS` is empty** (first sprint of a new project, or no integration branches ever created): skip the pick-or-create AskUserQuestion entirely — there is nothing to pick from and `AskUserQuestion` requires `minItems: 2`. Set `TARGET_BRANCH="$INFERRED_NAME"`, `CREATE_NEW=1`, print the inferred name for transparency, and proceed directly to Step 4.5.4 (base selection).
- **`EXISTING_INTS` has 1+ entries**: HITL via **AskUserQuestion**. Total options must stay within `AskUserQuestion`'s `maxItems: 4`. Build the option list as:
  - Up to 3 most-recent existing integration branches from `EXISTING_INTS`
  - Final option (always): `Create new with inferred name: <INFERRED_NAME>` — selecting this proceeds directly to Step 4.5.4 with `TARGET_BRANCH="$INFERRED_NAME"`, `CREATE_NEW=1`.
  - The harness-added `Other` option (auto-appended outside the 4-slot count) lets the user type a custom name. If the typed name matches an entry in `EXISTING_INTS`, treat as pick; otherwise treat as create-new (set `TARGET_BRANCH=<typed>`, `CREATE_NEW=1`) and proceed to Step 4.5.4.

If the user picks an existing branch → set `TARGET_BRANCH=<picked>`, `CREATE_NEW=0`.

#### Step 4.5.4: Choose base branch (only when creating new)

Skip when `CREATE_NEW=0` (existing branch reused).

**`--auto` mode**: `BASE_REF="origin/dev"`, no prompt.

**Normal mode**: ask via **AskUserQuestion** which base to branch from. Within the 4-option cap, list (existence-checked via `git ls-remote --heads origin`):
- `origin/dev` (Recommended — matches sprint worktree's base, cleanest sprint→integration merge)
- `origin/staging` (cleaner integration→staging promotion, but possible sprint→integration conflicts)
- `origin/main` (closest to production — for hotfix integration branches)
- `origin/master` (only when `main` doesn't exist — otherwise drop this slot)

The harness auto-adds an `Other` option outside the 4-slot count, letting the user type a custom ref like a specific commit SHA or a `release/*` branch. Skip listed options whose underlying remote branch doesn't exist (e.g., projects without `staging` only see dev/main/master).

Validate the chosen ref exists:
```bash
git ls-remote --exit-code --heads origin "${BASE_REF#origin/}" >/dev/null 2>&1 || {
  echo "ERROR: base ref '$BASE_REF' not found on remote" >&2
  exit 1
}
```

#### Step 4.5.5: Create the integration branch on the remote (if new)

Skip when `CREATE_NEW=0`.

Guard against the race where the user typed (or selected "create with inferred name" for) a branch name that already exists on the remote — this happens when `INFERRED_NAME` collides with an existing entry of `EXISTING_INTS` and the user picked the "Create new" option anyway. Without the guard, `git push origin <base>:refs/heads/<existing>` would be rejected and the user would have to re-run.

```bash
if git ls-remote --exit-code --heads origin "$TARGET_BRANCH" >/dev/null 2>&1; then
  echo "INFO: integration branch '$TARGET_BRANCH' already exists on origin — reusing instead of creating"
  CREATE_NEW=0
  git fetch origin "$TARGET_BRANCH" --quiet
else
  # Create the remote branch from the chosen base without checking out locally
  git push origin "${BASE_REF}:refs/heads/${TARGET_BRANCH}" || {
    echo "ERROR: failed to create integration branch '$TARGET_BRANCH' on origin" >&2
    exit 1
  }
  git fetch origin "$TARGET_BRANCH" --quiet
  echo "Created integration branch: $TARGET_BRANCH (from $BASE_REF)"
fi
```

After this step, `$TARGET_BRANCH` is the integration branch the sprint PR will target. All subsequent steps that reference `{target-branch}` use this value.

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

**Skip conditions** — when ANY of these are true, skip this step and proceed to **Step 8.3**:
- `--no-review` flag is specified (explicit user opt-out)
- `PROMOTION_SOURCE_IS_INTEGRATION=1` (promotion mode picked an integration branch in Step 10.0 — review already ran on the source sprint PRs; re-reviewing the same code is wasteful and slows hotfix paths)

Both conditions converge on the same outcome (no review loop), so they are checked together at Step 8 entry. The `PROMOTION_SOURCE_IS_INTEGRATION=1` path also routes through Step 10.1's "branch on source type" jump that bypasses Step 8 entirely; this check at Step 8 is a defensive backstop for non-promotion entry paths that might somehow set the flag.

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

**Mode check**:
- If `--staging` or `--main` is specified → proceed to **Step 11**.
- If `TARGET_BRANCH` matches `^(feat|fix)/` (default mode merged into an integration branch) → proceed to **Step 8.4.5** (promotion path).
- Otherwise (legacy: target was `dev`) → proceed to **Step 9**.

### Step 8.4.5: Promotion path (integration branch only)

The sprint PR has just merged into the integration branch (e.g., `feat/login`). The integration branch now carries the sprint's changes and is ready to be promoted onward. The user chooses whether to push the integration branch into `staging` (fast hotfix path) or `dev` (standard path), or to defer.

Refresh the integration branch locally so its `HEAD` reflects the freshly merged state:

```bash
git fetch origin "$TARGET_BRANCH" --quiet
```

#### Step 8.4.5.1: Ask the promotion path

**`--auto` mode** — safe default: `PROMOTION_TARGET="dev"` (standard path), no prompt. The user picked the integration model knowingly; defaulting to `staging` would be too aggressive for unattended runs.

**Normal mode** — **AskUserQuestion** with 3 options:
- `Promote to dev (standard path)` — queue for the next staging promotion. **Recommended** for most features.
- `Promote to staging (fast path)` — bypass dev, go directly to staging. Use for urgent hotfixes or features that must land on production quickly.
- `Skip (keep integration branch as-is)` — don't promote now. The integration branch persists; the user can run `/pr-merge --staging-from=<integration>` later (or accumulate more sprints into it first).

If `Skip`, jump to **Step 9** (cleanup) — no second PR is created.

#### Step 8.4.5.2: Create the promotion PR

```bash
# {target} is the chosen promotion target: "dev" or "staging"
gh pr list --head "$TARGET_BRANCH" --base "$PROMOTION_TARGET" --state open --json number,url --jq '.[0]' > /tmp/_promo_pr.json
PROMO_NUMBER=$(jq -r '.number // empty' /tmp/_promo_pr.json)

if [ -z "$PROMO_NUMBER" ]; then
  # Build a body that lists the recently-merged sprint PR for traceability
  PROMO_URL=$(gh pr create \
    --head "$TARGET_BRANCH" \
    --base "$PROMOTION_TARGET" \
    --title "promote: $TARGET_BRANCH → $PROMOTION_TARGET" \
    --body "$(cat <<EOF
## Promotion: $TARGET_BRANCH → $PROMOTION_TARGET

### Source sprint PR
- #$PR_NUMBER ($BRANCH_NAME)

### Notes
- Review was performed on the source sprint PR — promotion PR skips fresh review.
- If conflicts surface during merge, resolve and re-run \`/pr-merge\`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)")
  PROMO_NUMBER=$(echo "$PROMO_URL" | sed -E 's|.*/pull/([0-9]+)$|\1|')
else
  PROMO_URL=$(jq -r '.url' /tmp/_promo_pr.json)
  echo "Reusing existing promotion PR: $PROMO_URL"
fi
```

#### Step 8.4.5.3: Merge the promotion PR (no fresh review)

The source sprint PR already passed code review. Merge directly:

```bash
gh pr merge "$PROMO_NUMBER" --merge
```

- **Do not use `--delete-branch`** — the integration branch (`$TARGET_BRANCH`) is persistent and may accumulate more sprints.
- On merge conflict (rare — most conflicts surface in Step 5's sync): halt and instruct the user to resolve manually via the GitHub UI or local checkout.

Print the promotion result:

```
═══════════════════════════════════════════════════════
✅ Promoted: $TARGET_BRANCH → $PROMOTION_TARGET
   PR: $PROMO_URL
═══════════════════════════════════════════════════════
```

Proceed to **Step 9**.

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
6. **Delete the merged local sprint branch**: only when `STARTED_FROM_ISOLATED=1` AND the branch is a sprint branch (matches `^(feat|fix)/sprint-`). Integration branches (`feat/<name>`, `fix/<name>` without `sprint-`) are **persistent** and must not be deleted — they receive future sprint PRs and promotion PRs:
   ```bash
   if [ "${STARTED_FROM_ISOLATED:-0}" = "1" ] && [ -n "${BRANCH_NAME:-}" ]; then
     case "$BRANCH_NAME" in
       feat/sprint-*|fix/sprint-*)
         git branch -d "$BRANCH_NAME" || echo "INFO: skipped deleting $BRANCH_NAME (not merged or already deleted on remote)"
         ;;
       *)
         echo "INFO: keeping local branch $BRANCH_NAME (not a sprint branch — likely an integration branch or fallback temp branch)"
         ;;
     esac
   fi
   ```
   The compatibility case where you started on a work branch in the main worktree (`STARTED_FROM_ISOLATED=0`) is skipped because the current branch is checked out in the main worktree and cannot be deleted with `git branch -d`. If safe delete fails (not merged), only inform the user; do not force delete.

   > **Integration branch retention**: integration branches (`feat/login`, `fix/payment-typo`, etc.) are **never** auto-deleted by `/pr-merge`. They accumulate sprint PRs across multiple sprints and are referenced by promotion PRs. To delete an obsolete integration branch, the user runs `git push origin --delete <name> && git branch -D <name>` manually after confirming no in-flight PRs target it.
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

**Branch mapping (v5.11.1+)**:
- `--staging`: `{target-branch}` = `staging`. `{source-branch}` = **chosen in Step 10.0**: legacy `dev` (default — bulk promote all accumulated dev) OR a specific integration branch `feat/<name>` / `fix/<name>` (feature-level promotion — skip dev, land only this feature on staging).
- `--main`: `{target-branch}` = `main`. `{source-branch}` = **chosen in Step 10.0**: legacy `staging` (default — bulk promote all accumulated staging) OR a specific integration branch (feature-level promotion — land only this feature on main, bypassing other staging changes).

#### Step 10.0: Pick the promotion source

`{target-branch}` is fixed by the mode (`staging` for `--staging`, `main` for `--main`). The source is picked interactively so the user can choose between bulk promotion and feature-level promotion.

**`--auto` mode** — safe default: legacy bulk source.
```bash
case "$MODE" in
  --staging) SOURCE_BRANCH="dev" ;;
  --main)    SOURCE_BRANCH="staging" ;;
esac
PROMOTION_SOURCE_IS_INTEGRATION=0
echo "[--auto] Promotion source: $SOURCE_BRANCH (legacy bulk path)"
```

**Normal mode** — HITL via **AskUserQuestion**. Build the source option list:

```bash
# Default source per mode
case "$MODE" in
  --staging) DEFAULT_SOURCE="dev" ;;
  --main)    DEFAULT_SOURCE="staging" ;;
esac

# List existing integration branches (most-recent first, excluding sprint-*)
git fetch origin --quiet
mapfile -t INT_BRANCHES < <(
  git for-each-ref --sort=-committerdate \
    --format='%(refname:lstrip=3)' \
    refs/remotes/origin/feat refs/remotes/origin/fix 2>/dev/null \
    | grep -vE '^(feat|fix)/sprint-' \
    | head -3
)
```

Within `AskUserQuestion`'s 4-option cap, list:
- `<DEFAULT_SOURCE>` — labeled "Bulk promote (Recommended)" with description "Promote all accumulated changes from $DEFAULT_SOURCE — runs Step 8 code-review loop"
- Up to 3 entries from `INT_BRANCHES` — each labeled with the integration branch name and description "Promote only this integration branch ($name) — skips code review (already passed on sprint PR)"

The harness-appended `Other` option lets the user type any custom source ref (e.g., a long-lived branch outside the integration namespace).

Decision logic:
- If user picks `DEFAULT_SOURCE` → `SOURCE_BRANCH=$DEFAULT_SOURCE`, `PROMOTION_SOURCE_IS_INTEGRATION=0`
- If user picks an integration branch → `SOURCE_BRANCH=<picked>`, `PROMOTION_SOURCE_IS_INTEGRATION=1`
- If user picks `Other` → take the typed value as `SOURCE_BRANCH`. Set `PROMOTION_SOURCE_IS_INTEGRATION=1` if `SOURCE_BRANCH` matches `^(feat|fix)/`, else 0 (treat unknown sources as bulk-like — review still runs).

**Edge case — `INT_BRANCHES` is empty** (no integration branches exist yet, e.g., a project that hasn't merged any sprint PR through the v5.11+ flow): skip the AskUserQuestion entirely and set:
```bash
SOURCE_BRANCH="$DEFAULT_SOURCE"
PROMOTION_SOURCE_IS_INTEGRATION=0
echo "INFO: no integration branches found — defaulting to bulk promotion from $DEFAULT_SOURCE (Step 8 review will run)"
```
This avoids `AskUserQuestion`'s `minItems: 2` constraint and gives the user a clear log line explaining why no prompt was shown.

> **Why review skip on integration source**: the integration branch's content was already reviewed when sprint PRs merged into it via Step 8 (Sprint Phase). Re-running review on the promotion PR re-reviews the *same code* — wasteful and slows hotfix paths. Bulk dev/staging sources, in contrast, may carry multiple sprints' worth of changes that interact in ways not seen during individual sprint reviews, so the review loop is preserved there.

**Validation procedure**:

> **Note**: in promotion mode, source/target are not subject to worktree isolation. All checkouts run in the main worktree.

1. **Verify the source branch**: with `git ls-remote --heads origin "$SOURCE_BRANCH"`, check whether `$SOURCE_BRANCH` exists on the remote. If not, print an error message and abort.
2. **Verify the target branch**: with `git ls-remote --heads origin {target-branch}`, check whether `{target-branch}` exists on the remote.
   - **If it does not exist**: ask via **AskUserQuestion** whether to create `{target-branch}` from `$SOURCE_BRANCH`. On approval, create and push; on decline, abort.
3. **Switch to the source branch**: in the main worktree, `git checkout "$SOURCE_BRANCH"`
4. **Verify the diff**: with `git log origin/{target-branch}..origin/"$SOURCE_BRANCH" --oneline`, check whether commits to promote exist. If there is no diff, print "No changes to promote" and abort.
5. Show the commit list to the user (when integration source: title the commit list as "Sprint commits accumulated in $SOURCE_BRANCH"; when bulk source: "Commits to promote from $SOURCE_BRANCH").

### Step 10.1: Create the promotion PR

1. Check existing promotion PRs via `gh pr list --head "$SOURCE_BRANCH" --base {target-branch} --state open`
2. **If an existing PR exists**: print the PR URL and proceed to Step 8
3. **If no existing PR**: create a promotion PR. The body varies by source type so the reviewer / approver can tell at a glance whether code review was performed on this PR or inherited from upstream sprint PRs:

**Bulk source (`PROMOTION_SOURCE_IS_INTEGRATION=0`)** — `{source-branch}` is `dev` or `staging`:
```bash
gh pr create --head "$SOURCE_BRANCH" --base {target-branch} --title "promote: $SOURCE_BRANCH → {target-branch}" --body "$(cat <<EOF
## Promotion: $SOURCE_BRANCH → {target-branch}

### Commits included
{commit list}

### Checklist
- [ ] Code review passes (runs in Step 8)
- [ ] Tests pass

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

**Integration source (`PROMOTION_SOURCE_IS_INTEGRATION=1`)** — `{source-branch}` is `feat/<name>` or `fix/<name>`. Compute the aggregated sprint-PR list *outside* the heredoc to avoid jq-vs-bash quoting collisions (the `\(.number)` syntax inside a non-quoted heredoc would let bash try to interpret backslash sequences):

```bash
# Pre-compute the sprint PR list as a plain string, then interpolate.
# `--state merged --base "$SOURCE_BRANCH"` returns every sprint PR that ever
# merged INTO this integration branch (head→base=$SOURCE_BRANCH).
AGGREGATED_SPRINT_PRS=$(gh pr list --base "$SOURCE_BRANCH" --state merged \
  --json number,title --jq '.[] | "- #\(.number) \(.title)"' 2>/dev/null)
if [ -z "$AGGREGATED_SPRINT_PRS" ]; then
  AGGREGATED_SPRINT_PRS="(none found — integration branch may have been written to outside the sprint PR flow)"
fi

gh pr create --head "$SOURCE_BRANCH" --base "$TARGET_BRANCH" \
  --title "promote: $SOURCE_BRANCH → $TARGET_BRANCH (feature-level)" \
  --body "$(cat <<EOF
## Feature-level promotion: $SOURCE_BRANCH → $TARGET_BRANCH

### Sprint PRs aggregated into this integration branch
$AGGREGATED_SPRINT_PRS

### Code review status
Reviews ran on the source sprint PRs. This promotion PR skips a fresh review loop (Step 8 is bypassed).

### Checklist
- [x] Source sprint PRs reviewed
- [ ] Tests pass (verify on $SOURCE_BRANCH)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- If `--draft` is specified, add the `--draft` flag
- Print the PR URL.
- **Branch on source type for next step**:
  - `PROMOTION_SOURCE_IS_INTEGRATION=1` → proceed directly to **Step 8.3** (skip the code-review loop entirely — equivalent to `--no-review`)
  - Otherwise → proceed to **Step 8** (common code-review & merge cycle)

> **Note**: when fixing issues in Step 8.2 (bulk source path only), commit and push from `$SOURCE_BRANCH`. Integration sources bypass Step 8 entirely, so this note does not apply to them.

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
# Two-phase (v5.9+) with integration-branch model (v5.11+) — inside a sprint worktree
#   Sprint Phase: pick/create integration branch (Step 4.5) → commit → push → PR
#                 (base = integration branch) → review → fix loop, then exits.
#   The merge runs from the main worktree.
cd .astra-worktrees/sprint-3-user-auth
/pr-merge

# After Sprint Phase, finalize the merge from the main worktree
cd "$(git rev-parse --git-common-dir)/.."
/pr-merge      # auto-detects the pending sprint PR (head=feat/sprint-*, base=feat/*|fix/*)
               # exactly one match → in-place merge confirmation
               # multiple matches → AskUserQuestion picks which PR
               # after merge → AskUserQuestion picks promotion path (staging/dev/skip)

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

# Unattended end-to-end (Sprint Phase → integration branch auto-pick → auto-cd to
# main worktree → Main Phase → merge → promotion to dev (default) → worktree removal)
/pr-merge --auto

# Promotion (default bulk path): dev → staging
/pr-merge --staging
#   v5.11.1+: Step 10.0 asks the source — accept the recommended `dev` to keep
#   the legacy bulk behavior, or pick an integration branch (e.g., feat/login)
#   to promote ONLY that feature to staging (skips code review, fast hotfix path).

# Promotion (default bulk path): staging → main (release)
/pr-merge --main
#   v5.11.1+: Step 10.0 asks the source — accept the recommended `staging` for
#   bulk release, or pick an integration branch to land ONLY that feature on
#   main without dragging other staging changes (production-direct hotfix).

# Promotion + minor version bump
/pr-merge --main --minor

# Promotion + skip review
/pr-merge --staging --no-review
```

## Notes

- **Branch strategy (v5.11+)**: `feat/sprint-<N>-<name>  →  feat/<name> | fix/<name>  (integration)  →  dev | staging  →  main`. The integration branch is persistent and may receive multiple sprint PRs before promotion.
- **Two-phase policy (v5.9+, retained)**: `gh pr merge` only runs from the main worktree. Inside a sprint worktree, `/pr-merge` runs Sprint Phase (Step 4.5 integration-branch pick · commit · push · PR · review · fix loop) and stops. The user then `cd`s into the main worktree and re-invokes `/pr-merge` — Step 3.5 auto-detects the pending sprint PR (`head=feat/sprint-*`, `base=feat/*|fix/*`) and merges it, then Step 8.4.5 asks the promotion path. With `--auto`, the skill performs the cross-worktree transition itself.
- **Worktree policy (v5.0+)**: sprint worktrees are created by `/sprint-init` (`.astra-worktrees/sprint-<N>-<name>/`). Right after Main Phase merges into the integration branch (+ optional promotion to staging/dev), the sprint worktree is auto-removed (Step 9). Cross-shared-branch (main/staging/dev/master) cascade merges and promotions run directly in the main worktree. If the workflow halts due to a conflict, the worktree remains — after resolving, re-run `/pr-merge` to continue.
- **Fallback flow (one-shot, target=dev)**: when a user without `/sprint-init` invokes `/pr-merge` after making changes directly in the main worktree (dev), Step 3.5 finds no pending sprint PR, falls through to Step 4.1 which auto-creates a temporary isolated worktree. **The fallback keeps `TARGET_BRANCH=dev`** (legacy one-shot behavior — no integration branch, no promotion step). Users who need feature-level promotion should start with `/sprint-init` instead.
- **Common preprocessing**: in every mode, pull `main` / `staging` / `dev` before execution. The cascade merge itself is restricted to `staging → dev` and runs only in default mode — promotion modes (`--staging`, `--main`) skip the cascade entirely. `main → staging` is never auto-cascaded; operate on `main` only via the explicit `--main` promotion.
- **Default mode (v5.11+)**: the merge target branch is an integration branch chosen interactively in Step 4.5 — pick an existing `feat/*` / `fix/*` integration branch or create a new one from a user-chosen base (default `origin/dev`). Classification (feat vs fix) and the branch name slug are auto-inferred from commit prefixes, the sprint slug, and the blueprint, then surfaced to the user. Under `--auto`, the inferred name is reused if it exists on the remote; otherwise auto-created from `origin/dev`.
- **Promotion mode (`--staging`)** (v5.11.1+): the source is picked in **Step 10.0** — default `dev` (bulk, runs code review) or a specific `feat/<name>` / `fix/<name>` integration branch (feature-level, skips review). Target = `staging`. Under `--auto`, defaults to `dev`.
- **Promotion mode (`--main`)** (v5.11.1+): the source is picked in **Step 10.0** — default `staging` (bulk, runs code review) or a specific integration branch (feature-level, skips review, lands ONLY that feature on main bypassing other staging changes — useful for production-direct hotfix delivery). Target = `main`. As this is a release promotion, the version bump runs at this stage. Under `--auto`, defaults to `staging`.
- Final checkout location after merge: default mode goes to `{target-branch}` (`dev`); promotion mode returns to the `dev` branch.
- If Critical issues remain, merging is blocked.
- On conflict, do not attempt auto-resolution; instruct the user and abort.
- The version bump runs only in `--main` promotion, and applies only to projects with `.claude-plugin/plugin.json`.
- Before commits and merges, user confirmation is always required. However, after-review issue fixes proceed automatically without user confirmation.
- **kubernetes protection rule**: during code review and issue fixes, do not delete files under the `kubernetes/` directory.
- **Remote-branch preservation policy**: after merging, remote work branches (`feat/*`, `fix/*`, `docs/*`, `refactor/*`, `chore/*`, etc.) are not deleted from the remote. They are preserved for merge-history tracking, rollback reference, and reuse in other environments. Only local sprint branches (`feat/sprint-*`, `fix/sprint-*`) are safely deleted with `git branch -d` (auto-skipped if unmerged). **Integration branches** (`feat/<name>`, `fix/<name>` without the `sprint-` segment) are persistent on both local and remote — Step 9 protects them from auto-deletion. Manually clean them up only after confirming no in-flight PRs target them.
- In promotion mode, source branches are not deleted: `dev` and `staging` are permanent shared branches; `feat/<name>` and `fix/<name>` integration branches are persistent (consistent with Step 9 retention rule — they may receive future sprint PRs or be promoted again).
- **`--no-review` precedence**: when `--no-review` is explicitly set, Step 8 is skipped regardless of source type (both bulk and integration sources). The `PROMOTION_SOURCE_IS_INTEGRATION=1` skip is additive — either condition alone is sufficient to bypass review.
- **Surgical Changes principle**: during Step 8.2 issue fixes, change only the lines flagged by the review. Arbitrary refactoring, format changes, or naming "improvements" on adjacent code are forbidden. Every modified line must trace directly to an issue. Split unrelated improvements into a separate PR. (See: Behavioral Guardrails in the `coding-convention` skill.)
