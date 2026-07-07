# pr-merge — Fallbacks, backward compatibility & recovery

Non-mainline branches of `/pr-merge`: the one-shot temp-worktree fallback (Step 4.1), the pre-v5.11 `base=dev` PR-detection fallback (Step 3.5), the main-worktree compat cases (Step 4), and version-history prose. Read the relevant section when the standard sprint→integration→promotion path does not match the user's situation.

Every Bash block assumes the PREAMBLE (SKILL.md Step 1 state protocol).

---

## Step 3.5 fallback — pre-v5.11 `base=dev` sprint PRs

SKILL.md Step 3.5 first matches open PRs with `head ~ ^feat/sprint-` and `base ~ ^(feat|fix)/`. PRs created by pre-v5.11 `/pr-merge` instead use `baseRefName == "dev"`. If the primary filter returns `PENDING_COUNT == 0`, run the legacy filter once before falling through to Step 4:

```bash
if [ "$PENDING_COUNT" = "0" ]; then
  PENDING_PRS=$(gh pr list --base dev --state open --json number,headRefName,baseRefName,title,url \
    --jq '[.[] | select(.headRefName | test("^feat/sprint-"))]')
  PENDING_COUNT=$(echo "$PENDING_PRS" | jq 'length')
fi
```

> **Why HITL on multi-PR even with `--auto`**: merging the wrong PR mutates the wrong integration branch (which then can be wrongly promoted in Step 8.4.5) and triggers worktree removal of the wrong sprint. The cost of one prompt is far lower than the cost of a wrong merge.

---

## Step 4 compat cases (routing)

SKILL.md Step 4 keeps the normal flow (inside a sprint worktree + work branch). The other two cases route as follows:

- **Main worktree + shared branch (main/master/staging/dev)**: fallback case — direct dev changes without `/sprint-init`. Auto-create a temporary isolated worktree → proceed to **Step 4.1** (below).
- **Main worktree + work branch (feat/fix/docs/etc.)**: compatibility case for users who worked in the main worktree under pre-v4.1 policy. Do not force migration — set the flags and proceed to **Step 5**:
  ```bash
  PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
  source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
  WT_PATH="$(pwd)"
  BRANCH_NAME="$CURRENT_BRANCH"
  STARTED_FROM_ISOLATED=0
  STARTED_FROM_SPRINT=0   # ← compat case: in-place merge in Step 8.3
  for kv in WT_PATH BRANCH_NAME STARTED_FROM_ISOLATED STARTED_FROM_SPRINT; do
    eval "astra_state_set $kv \"\$$kv\""
  done
  ```
  Both compat/fallback cases set `TARGET_BRANCH="dev"` (Step 4.5 is skipped — legacy one-shot behavior).

---

## Step 4.1: Fallback — auto-create a temporary isolated worktree

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
5. From here on, all git operations (commit, push, post-merge cleanup) happen inside `$WT_PATH`. In subsequent steps of SKILL.md, "current branch" means `$BRANCH_NAME` checked out in the isolated worktree.
6. `{branch-name}` refers to `$BRANCH_NAME` (the actual name decided by the helper); `{work-tree-path}` refers to `$WT_PATH`. A numeric suffix may have been appended, so subsequent steps use *the helper return value, not the intended name*.
7. Set the `STARTED_FROM_ISOLATED=1` flag (used in Step 9 to decide worktree removal and local-branch deletion). Also set `STARTED_FROM_SPRINT=0` — this is a fallback temp worktree (not a real sprint worktree), so Step 8.3 must route to in-place merge, not to the Sprint→Main handoff. Persist `WT_PATH`, `BRANCH_NAME`, and both flags via `astra_state_set` (state protocol, Step 1).

`TARGET_BRANCH="dev"` for this fallback (legacy one-shot behavior). Skip Step 4.5 and proceed to **Step 5** (skip the sync itself — the worktree was just created from `origin/dev`, so it is already in sync).

---

## Version history & recovery notes

- **v5.0+ change**: `--start` mode is removed. All worktree creation is handled by `/sprint-init`. For users who worked one-off in the main worktree without `/sprint-init` and then invoked `/pr-merge`, Step 4.1 handles the fallback automatically (one-shot: PR creation + merge in a single invocation).
- **v5.9+ change**: the merge step (`gh pr merge`) only runs from the main worktree. Inside a sprint worktree, `/pr-merge` finishes after the review loop and asks the user to re-invoke it from the main worktree (unless `--auto` is set, in which case the skill performs the cross-worktree continuation itself).
- **v5.11+ change**: default-mode target is an integration branch (`feat/<name>` / `fix/<name>`), not `dev`. The Step 4.1 one-shot fallback intentionally keeps `TARGET_BRANCH=dev` — users who need integration-branch granularity should run `/sprint-init` first.
- **On conflict, the worktree remains**: if the workflow halts due to a cascade/rebase/sync conflict, the sprint worktree is NOT auto-removed. After resolving the conflict inside the worktree, re-run `/pr-merge` to continue.
- **On merge conflict, no auto-resolution**: instruct the user to resolve manually (local checkout or GitHub UI) and abort. Never attempt automatic conflict resolution.

---

## Cross-invocation state protocol (full rules — SKILL.md Step 1)

Shell variables do NOT persist between separate Bash tool invocations. This workflow's state lives in a **scoped** file (`astra_state_file` — scope defaults to the current work branch's slug inside a worktree, `main` on shared branches; concurrent runs on different sprints never cross-contaminate). SKILL.md Step 1 keeps rule 1 (the PREAMBLE) inline; the full rule set is:

1. **PREAMBLE — literal first lines of EVERY Bash block you run in this skill** (add it yourself to any command you compose):
   ```bash
   PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
   source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
   ```
2. **Whenever you set or change a workflow variable** — `MODE`, `TARGET_BRANCH`, `BRANCH_NAME`, `WT_PATH`, `PR_NUMBER`, `PR_URL`, `PROMOTION_TARGET`, `PROMO_NUMBER`, `SOURCE_BRANCH`, `STARTED_FROM_SPRINT`, `STARTED_FROM_ISOLATED`, `MAIN_PHASE_ENTRY`, `CREATE_NEW`, `BASE_REF`, `INFERRED_NAME`, `PROMOTION_SOURCE_IS_INTEGRATION` — persist it immediately: `astra_state_set KEY "$VALUE"`.
3. **Before any destructive command** (`gh pr merge`, `git push`, `git branch -d`, worktree removal): verify every variable it consumes is non-empty (`[ -n "$VAR" ]`). If empty after `astra_state_load`, re-derive from git/gh (e.g., `PR_NUMBER` via `gh pr list --head "$BRANCH_NAME" --state open --json number --jq '.[0].number'`) — **never run a destructive command with an empty variable**.
4. **Scope handoff**: the Sprint→Main transition (Step 3.5 / Step 8.5 `--auto` cd) runs `astra_state_adopt "$BRANCH_NAME"` from the main worktree so the sprint scope's state carries into the `main` scope.

At workflow end (Step 9 / Step 11) or on abort, run `astra_state_clear`. If `astra_state_load` reveals leftover state from a previous aborted run of a *different* branch, run `astra_state_clear` first and re-derive.

---

## `--auto` flag policy (full HITL points table — SKILL.md Step 1)

SKILL.md Step 1 keeps a condensed list of the **preserved-HITL** points; the full behavior matrix is:

| Point | `--auto` behavior |
|-------|-------------------|
| Step 4.5 integration branch pick (Sprint Phase) | auto-reuse existing matching inferred name; else auto-create from `origin/dev` |
| Step 4.5.4 base branch for new integration | always `origin/dev` |
| Step 6 commit confirmation (Sprint Phase) | auto-approve → commit immediately (summary still printed) |
| Step 8.5 Sprint → Main handoff | `cd` to main worktree + continue automatically |
| Step 8.3 final-merge confirmation (Main Phase) | auto-approve → merge immediately |
| **Step 8.4.5 promotion path (dev / staging / skip)** | **HITL preserved** — `AskUserQuestion` fires even under `--auto` |
| Step 10.0 promotion source (`--staging`/`--main`) | auto-select legacy bulk source (`dev` / `staging`) |
| Step 8.1 MAX reached + 0 Critical | **HITL preserved** (remaining High requires user judgment) |
| Step 8.1 MAX reached + ≥ 1 Critical | **always halt** (auto or manual) |
| gh CLI not authenticated | **halt** + guidance (auth cannot be automated) |
| Cascade / rebase merge conflict | **halt** + show conflicting files |
| dev branch absent on remote | auto-create and proceed |
| Multiple pending sprint PRs in Main Phase | `AskUserQuestion` (HITL preserved — a wrong pick is destructive) |

> `--auto` does not bypass *safety gates* — on true blockers (auth, conflict, Critical, ambiguous PR) and on the promotion-target decision, it halts/prompts just like normal mode.

---

## Step 8.5 `--auto` cross-worktree transition (bash)

Normal mode (the recommended two-invocation flow) prints the handoff message and exits — that stays inline in SKILL.md Step 8.5. Only `--auto` continues automatically; its transition bash lives here. The skill `cd`s into the main worktree itself so `/autorun` and `/sprint-init --auto` complete end-to-end in one invocation:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
[ -n "${BRANCH_NAME:-}" ] || BRANCH_NAME=$(git branch --show-current)
MAIN_ROOT=$(astra_main_worktree_root)
if [ -z "$MAIN_ROOT" ] || [ ! -d "$MAIN_ROOT" ]; then
  echo "ERROR: cannot determine the main worktree path" >&2
  exit 1
fi
cd "$MAIN_ROOT"
astra_state_adopt "$BRANCH_NAME"   # carry the sprint scope's state into the main scope
CURRENT_MAIN_BRANCH=$(git branch --show-current)
case "$CURRENT_MAIN_BRANCH" in
  main|master|staging|dev) : ;;
  *) echo "ERROR: main worktree is on '$CURRENT_MAIN_BRANCH' (expected main/master/staging/dev). Aborting --auto handoff." >&2; exit 1 ;;
esac
```

Then proceed to **Step M1**. `BRANCH_NAME`, `PR_URL`, `PR_NUMBER`, `STARTED_FROM_ISOLATED=1` are already set from Sprint Phase.

---

## Step 9 cleanup mechanics (bash)

SKILL.md Step 9 keeps the numbered procedure inline; the verbose guard bash lives here.

**Worktree removal + local sprint-branch deletion** (both guarded by `STARTED_FROM_ISOLATED=1`; integration branches without the `sprint-` segment are persistent and never deleted):
```bash
if [ "${STARTED_FROM_ISOLATED:-0}" = "1" ] && [ -n "${BRANCH_NAME:-}" ]; then
  astra_remove_worktree "$BRANCH_NAME"   # helper only warns (workflow continues) if the worktree is dirty
  case "$BRANCH_NAME" in
    feat/sprint-*|fix/sprint-*)
      git branch -d "$BRANCH_NAME" || echo "INFO: skipped deleting $BRANCH_NAME (not merged or already deleted on remote)" ;;
    *)
      echo "INFO: keeping local branch $BRANCH_NAME (not a sprint branch — likely an integration or fallback temp branch)" ;;
  esac
fi
```
The `STARTED_FROM_ISOLATED=0` compat case skips both (the main worktree must not be removed, and its checked-out branch cannot be `git branch -d`'d).

**Completion Gate — verify before reporting success.** Print the final summary ONLY when all three gates pass; otherwise report exactly which failed:
```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
[ "$(gh pr view "$PR_NUMBER" --json state --jq '.state')" = "MERGED" ] && echo "GATE1 PASS" || echo "GATE1 FAIL: PR #$PR_NUMBER not merged"
if [ "${STARTED_FROM_ISOLATED:-0}" = "1" ]; then
  git worktree list --porcelain | grep -qF "$WT_PATH" && echo "GATE2 FAIL: worktree still present: $WT_PATH" || echo "GATE2 PASS"
else echo "GATE2 PASS (n/a)"; fi
[ "$(git branch --show-current)" = "dev" ] && echo "GATE3 PASS" || echo "GATE3 FAIL: current branch is $(git branch --show-current), expected dev"
astra_state_clear
```

> **Integration branch retention**: integration branches are **never** auto-deleted by `/pr-merge`. They accumulate sprint PRs and are referenced by promotion PRs. To delete an obsolete one, the user runs `git push origin --delete <name> && git branch -D <name>` manually after confirming no in-flight PRs target it.
