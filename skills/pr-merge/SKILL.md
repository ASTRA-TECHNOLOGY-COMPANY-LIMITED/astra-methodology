---
name: pr-merge
description: "Automated PR cycle — commit, push, PR creation, code review, fix loop, merge, and promotion. Sprint PRs target an integration branch (feat/<name> or fix/<name>) picked or created interactively; after merge the user picks a promotion path (dev / staging / skip — always HITL, even under --auto). Inside a sprint worktree it stops after the review loop; the merge finalizes from the main worktree (--auto chains both phases). Use when creating or merging a PR, promoting with --staging/--main, or finishing a sprint."
argument-hint: "[max-iterations] [--no-review] [--draft] [--auto] [--patch|--minor|--major] [--staging] [--main]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Agent, TodoWrite
---

# ASTRA PR Review & Merge Workflow (v5.11+)

Automates the entire cycle from commit through code review, issue fixes, integration-branch merge, promotion, and worktree removal. The review → fix → re-review loop runs automatically up to the max iteration count.

**Branch strategy (v5.11+)**: `feat/sprint-<N>-<name>  →  feat/<name> | fix/<name>  (integration)  →  dev | staging  →  main`

The integration branch is the unit of promotion: pick any sprint's integration branch and push it to `staging` directly (fast hotfix path) or queue it via `dev` (standard path). Multiple sprints may target the same integration branch to accumulate a larger feature before promotion.

**Two-phase policy (v5.9+, retained)** — keyed off the current worktree location so the merge stays observable from the main worktree (where the cascade, shared branches, and version bumps live):

- **Sprint Phase** — inside a sprint worktree (`.astra-worktrees/sprint-<N>-<name>/`). Runs target-branch determination (Step 4.5) → commit → push → PR against the integration branch → code review → automatic Critical/High fixes, then **stops after the review loop converges**. `gh pr merge` and the promotion decision are NOT performed here; the user `cd`s to the main worktree and re-invokes `/pr-merge`.
- **Main Phase** — from the main worktree (shared branch). Auto-detects the open sprint PR (`head ~ feat/sprint-*`, `base ~ feat/*|fix/*`), merges it, then Step 8.4.5 asks where to promote the integration branch (staging / dev / skip).
- **`--auto` flag** — when Sprint Phase completes under `--auto`, the skill `cd`s into the main worktree itself and continues into Main Phase, so `/autorun` and `/sprint-init --auto` finish in one invocation. **The Step 8.4.5 promotion-target prompt is always HITL — even `--auto` fires it** (the promotion target changes the deployment surface; no safe unattended default).

**Worktree isolation policy (v5.0+)**: sprint-unit work happens inside the `/sprint-init`-created worktree; immediately after Main Phase merges into a shared branch, the worktree is auto-removed. The main worktree always stays on a shared branch. Source helpers from `$CLAUDE_PLUGIN_ROOT/scripts/worktree-helpers.sh`.

> Legacy fallbacks, backward-compat PR detection, and version-history rationale: see [references/fallbacks-and-recovery.md](references/fallbacks-and-recovery.md).

## Execution Procedure

### Step 1: Argument parsing and preconditions

**Step tracker (MANDATORY for this long workflow)**: immediately create one TodoWrite entry per major step of the phase you are entering (Sprint Phase: 2 · 4 · 4.5 · 5 · 6 · 7 · 8 · 8.5 / Main Phase: 2 · 3.5 · M1 · 8.4 · 8.4.5 · 9 / Promotion: 2 · 10.0 · 10.1 · 8 · 8.4 · 11), and mark each in_progress/completed as you go. This prevents losing your place across the many Bash calls below.

Parse `$ARGUMENTS` to determine options:

- **max-iterations**: numeric argument → max review-iteration count (default: 3)
- **--no-review**: skip code review; just commit → push → create PR → merge
- **--draft**: create the PR in Draft state
- **--auto**: unattended mode — auto-approve every `AskUserQuestion` prompt except for safe HITL points (see table below)
- **--patch / --minor / --major**: version-bump type (default: --patch)
- **--staging**: promotion mode — merge `dev` → `staging`
- **--main**: promotion mode — merge `staging` → `main`

**Mode decision**:
- `--staging` or `--main` → promotion mode (main-worktree only, see [references/promotion-modes.md](references/promotion-modes.md))
- Otherwise → default mode. Phase is decided by current location:
  - Inside a sprint worktree (`astra_is_isolated_worktree` true) → **Sprint Phase**
  - Main worktree on a shared branch → **Main Phase** (auto-detect pending sprint PR; if none, Step 4.1 one-shot fallback)
  - Main worktree on a work branch (compatibility) → one-shot fallback

**`--auto` flag policy — HITL points that `--auto` NEVER suppresses** (everything else auto-approves with smart defaults):
- **Step 8.4.5 promotion path (dev / staging / skip)** — `AskUserQuestion` fires even under `--auto` (the deployment surface has no safe default).
- **Step 8.1 MAX reached + 0 Critical** — remaining High requires user judgment (≥ 1 Critical → **always halt**, auto or manual).
- **Multiple pending sprint PRs in Main Phase** — a wrong pick is destructive.
- **True blockers** — gh not authenticated, or a cascade/rebase/merge conflict → **halt** (cannot be automated).

> `--auto` does not bypass *safety gates*. The full per-step behavior matrix (Step 4.5 pick, base branch, commit, handoff, promotion source, dev-branch auto-create, …) is in **[references/fallbacks-and-recovery.md](references/fallbacks-and-recovery.md#--auto-flag-policy-full-hitl-points-table--skillmd-step-1)**.

Validate the following preconditions:

1. **gh CLI authentication**: run `gh auth status`. If not authenticated, instruct the user to run `gh auth login` and abort.
2. **Clean-state check**: run `git status`. In promotion mode, if there are uncommitted changes, warn and abort (run only from a clean state).
3. **Load worktree helpers** (source in every Bash step):
   ```bash
   PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
   if [ -z "$PLUGIN_ROOT" ] || [ ! -f "$PLUGIN_ROOT/scripts/worktree-helpers.sh" ]; then
     echo "ERROR: CLAUDE_PLUGIN_ROOT not found. Check the plugin cache path." >&2
     exit 1
   fi
   source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"
   ```
   After that, use the `astra_*` functions.

   **Cross-invocation state protocol (MANDATORY)**: shell variables do NOT persist between separate Bash tool invocations, so this workflow's state lives in a **scoped** state file. The core rules:
   1. **PREAMBLE — literal first lines of EVERY Bash block you run in this skill** (add it yourself to any command you compose):
      ```bash
      PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
      source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
      ```
   2. **Whenever you set or change a workflow variable** (`TARGET_BRANCH`, `BRANCH_NAME`, `PR_NUMBER`, `STARTED_FROM_SPRINT`, `PROMOTION_TARGET`, …), persist it immediately: `astra_state_set KEY "$VALUE"`.
   3. **Before any destructive command** (`gh pr merge`, `git push`, `git branch -d`, worktree removal), verify every variable it consumes is non-empty; if empty after `astra_state_load`, re-derive from git/gh — **never run a destructive command with an empty variable**.

   Full rule set (variable list, scope handoff via `astra_state_adopt`, `astra_state_clear` at end/abort): **[references/fallbacks-and-recovery.md](references/fallbacks-and-recovery.md#cross-invocation-state-protocol-full-rules--skillmd-step-1)**.

   **Per-mode worktree-location guard**:
   - **Promotion mode (`--staging`, `--main`)**: must run in the main worktree — `astra_ensure_main_worktree || exit 1`. Then proceed per [references/promotion-modes.md](references/promotion-modes.md).
   - **Default mode**: phase is decided by location.
     - **Inside a sprint worktree** → Sprint Phase (Step 4 → 5 → … → 8.2 → 8.5 handoff). The merge is deferred to Main Phase.
     - **In the main worktree** → Main Phase. Step 3.5 checks for an open PR with `head ~ feat/sprint-*` and `base ~ ^(feat|fix)/`. If yes, jump to Main Phase merge (Step M1). If no, fall through to Step 4 / Step 4.1.

### Step 1.1: Defer target branch (default mode only)

In v5.11+ the default-mode target is an **integration branch** (`feat/<name>` / `fix/<name>`), determined per phase, not here:
- **Sprint Phase** → **Step 4.5** picks/creates it after Step 4 confirms the sprint context.
- **Main Phase** → **Step 3.5** discovers it from the pending sprint PR's `baseRefName`.
- **Step 4.1 fallback** → target stays `dev` (legacy one-shot).

Initialize `TARGET_BRANCH=""` and continue. Step 2 (shared-branch sync) does not depend on `{target-branch}`.

### Step 2: Branch sync (common to all modes)

Before all modes, pull `main`, `staging`, `dev` to latest. Cascade merge is restricted to `staging → dev` only — `main → staging` is never run automatically (operate on `main` only via the explicit `--main` promotion). Save the current branch as `{current-branch}`.

#### Step 2.1: Remote fetch and shared-branch sync (no checkout)

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
astra_sync_shared_branches
```

The helper updates local `main`/`master`/`staging`/`dev` refs from origin **without checking any out** (`git fetch origin <b>:<b>` fast-forward), so other sessions and linked worktrees are never disturbed. Only the checked-out branch is updated via `git pull --rebase`. Branches missing on the remote are skipped; non-fast-forwardable local refs are left alone with a warning.

> **Promotion mode**: if `{target-branch}` is missing from the remote — normal mode asks (AskUserQuestion) whether to create it from the default branch (abort if declined); `--auto` auto-creates it. **Default mode**: `{target-branch}` isn't determined yet — existence checks happen in Step 4.5 (Sprint) / Step 3.5 (Main).

#### Step 2.2: Cascade merge (staging → dev)

Sync upstream `staging` into downstream `dev`. Single hop only — `main → staging` is intentionally excluded.

**Per-mode cascade scope**: default mode runs `staging → dev` (when both exist); `--staging` / `--main` promotions skip the cascade.

When the cascade runs (default mode, both branches exist on remote):
```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
# Dry-run conflict detection FIRST — never leave the shared main worktree
# in a half-merged state (other sessions depend on it being clean).
astra_merge_precheck origin/dev origin/staging; PRECHECK=$?
if [ "$PRECHECK" = "1" ]; then
  echo "ERROR: cascade staging→dev would conflict (files listed above)." >&2
  echo "       Resolve manually: git checkout dev && git merge staging" >&2
  exit 1   # abort BEFORE touching the working tree
fi
git checkout dev
if ! git merge staging; then
  git merge --abort 2>/dev/null   # PRECHECK=2 fallback (git < 2.38): clean up, then abort
  echo "ERROR: cascade merge conflict — aborted cleanly. Resolve manually and re-run." >&2
  exit 1
fi
# If there are changes after the merge: git push origin dev
git checkout {current-branch}   # return to the original branch
```

> **Note**: when the cascade has no changes (Already up to date), silently skip. If `staging` does not exist on the remote, skip the cascade entirely — do **not** fall back to `main → dev`.

### Step 3: Per-mode branching

- **Promotion mode** (`--staging` / `--main`): proceed to **Step 10** ([references/promotion-modes.md](references/promotion-modes.md)).
- **Default mode**: proceed to **Step 3.5** (Main-Phase pending-PR detection) when in the main worktree, otherwise **Step 4** (Sprint Phase).

### Step 3.5: Main-Phase entry — detect pending sprint PR

Skip when invoked from inside a sprint worktree (`astra_is_isolated_worktree` true) — Sprint Phase always proceeds to Step 4.

In the main worktree on a shared branch, search for an open sprint PR awaiting merge. In v5.11+ the base is an **integration branch** (`feat/<name>` / `fix/<name>`), so the filter matches by head pattern and includes the base name:

```bash
PENDING_PRS=$(gh pr list --state open --json number,headRefName,baseRefName,title,url \
  --jq '[.[] | select(.headRefName | test("^feat/sprint-")) | select(.baseRefName | test("^(feat|fix)/"))]')
PENDING_COUNT=$(echo "$PENDING_PRS" | jq 'length')
```

> **Backward compatibility**: pre-v5.11 PRs use `baseRefName == "dev"`. If `PENDING_COUNT == 0`, run the legacy fallback once before giving up — see [references/fallbacks-and-recovery.md](references/fallbacks-and-recovery.md#step-35-fallback--pre-v511-basedev-sprint-prs).

Branch on count:

- **`PENDING_COUNT == 0`**: no pending sprint PR — legacy one-shot path. Fall through to **Step 4** (routes to Step 4.1 fallback when on a shared branch). No `gh pr merge` unless a PR is created later in Step 7.
- **`PENDING_COUNT == 1`**: auto-select that PR. Save and persist:
  ```bash
  PR_NUMBER=$(echo "$PENDING_PRS" | jq -r '.[0].number')
  PR_URL=$(echo "$PENDING_PRS" | jq -r '.[0].url')
  BRANCH_NAME=$(echo "$PENDING_PRS" | jq -r '.[0].headRefName')
  TARGET_BRANCH=$(echo "$PENDING_PRS" | jq -r '.[0].baseRefName')   # the integration branch
  STARTED_FROM_ISOLATED=1     # so Step 9 removes the sprint worktree
  STARTED_FROM_SPRINT=0       # merging from the main worktree, not from inside the sprint worktree
  MAIN_PHASE_ENTRY=1          # Step 8.3 jumps straight to Step 8.4
  # PREAMBLE required at top of this block. Adopt Sprint-Phase state first, then persist:
  astra_state_adopt "$BRANCH_NAME"
  for kv in PR_NUMBER PR_URL BRANCH_NAME TARGET_BRANCH STARTED_FROM_ISOLATED STARTED_FROM_SPRINT MAIN_PHASE_ENTRY; do
    eval "astra_state_set $kv \"\$$kv\""
  done
  ```
  Print the PR summary (title, head, base = integration branch, URL, change file count via `gh pr diff $PR_NUMBER --name-only | wc -l`) and proceed to **Step M1**.
- **`PENDING_COUNT >= 2`**: destructive choice — print the list (each row head → base) and ask via **AskUserQuestion** (HITL preserved even in `--auto`). Save the selected PR's metadata as above and proceed to **Step M1**.

---

## Sprint Phase (feature → PR creation + review loop)

### Step 4: Verify the work branch

```bash
CURRENT_BRANCH=$(git branch --show-current)
```

- **Inside a sprint worktree + work branch** (`astra_is_isolated_worktree` true and current branch is not shared): the *normal flow* — invoked from the sprint worktree created by `/sprint-init`. Set variables and proceed to **Step 4.5**:
  ```bash
  PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
  source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
  WT_PATH="$(pwd)"
  BRANCH_NAME="$CURRENT_BRANCH"
  STARTED_FROM_ISOLATED=1
  STARTED_FROM_SPRINT=1   # ← real sprint worktree; Step 8.3 hands off to Main Phase (or auto-cd under --auto)
  for kv in WT_PATH BRANCH_NAME STARTED_FROM_ISOLATED STARTED_FROM_SPRINT; do
    eval "astra_state_set $kv \"\$$kv\""
  done
  ```
  > The sprint worktree's branch is typically `feat/sprint-<N>-<name>`, but isolated worktrees with other prefixes (`fix/`, `docs/`, …) are handled the same way.
- **Main worktree + shared branch** or **main worktree + work branch (compat)**: fallback / compatibility cases — see [references/fallbacks-and-recovery.md](references/fallbacks-and-recovery.md#step-4-compat-cases-routing). The shared-branch case creates a temp worktree (**Step 4.1** in that reference); both set `TARGET_BRANCH="dev"` and skip Step 4.5.

### Step 4.5: Determine integration target branch (Sprint Phase only)

Run **only when `STARTED_FROM_SPRINT=1`**. For all skipped cases (Step 4.1 fallback, main-worktree compat, promotion mode) set `TARGET_BRANCH="dev"` and proceed to **Step 5**.

Determine the integration branch in five sub-steps:
1. **Infer classification (feat vs fix)** from commit prefixes + sprint slug keywords + blueprint context → `INFERRED_NAME`.
2. **List existing integration branches** (`feat/*` / `fix/*`, excluding `sprint-*`) → `EXISTING_INTS`.
3. **Pick existing or create new** — `--auto` reuses the inferred name (else creates from `origin/dev`); normal mode asks via AskUserQuestion when `EXISTING_INTS` is non-empty. Sets `TARGET_BRANCH`, `CREATE_NEW`.
4. **Choose base branch** (only when `CREATE_NEW=1`) — `--auto` uses `origin/dev`; normal mode asks (dev/staging/main/master/Other). Sets `BASE_REF`.
5. **Create the integration branch on the remote** (only when `CREATE_NEW=1`), guarding the already-exists race.

Full heuristic and per-sub-step bash: **[references/integration-branch-inference.md](references/integration-branch-inference.md)** — read it now (this step needs its bash to run). After it completes, `$TARGET_BRANCH` is the integration branch the sprint PR will target; proceed to **Step 5**.

### Step 5: Sync the target branch

Step 2 already ran the cascade; reflect the latest `{target-branch}` into the work branch. **Run inside the isolated worktree (`{work-tree-path}`)**:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
[ -n "${WT_PATH:-}" ] || WT_PATH=$(pwd)
[ -n "${TARGET_BRANCH:-}" ] || { echo "ERROR: TARGET_BRANCH empty — re-run Step 4.5" >&2; exit 1; }
cd "$WT_PATH"
git fetch origin "$TARGET_BRANCH" --quiet
# Dry-run conflict detection first — keep the worktree clean when a conflict is coming.
astra_merge_precheck HEAD "origin/$TARGET_BRANCH"; PRECHECK=$?
if [ "$PRECHECK" = "1" ]; then
  echo "ERROR: merging origin/$TARGET_BRANCH into $BRANCH_NAME would conflict (files listed above)." >&2
  echo "       Resolve inside this worktree: git merge origin/$TARGET_BRANCH  (fix conflicts, commit), then re-run /pr-merge." >&2
  exit 1   # working tree untouched — no half-merged state
fi
git merge "origin/$TARGET_BRANCH"   # PRECHECK 0 → clean; 2 → precheck unavailable
```

- **No conflict**: proceed. **Conflict** (only when `PRECHECK=2`, git < 2.38): print the conflict files, instruct manual resolution, abort. The user stays inside `$WT_PATH`; after resolving, re-run `/pr-merge` (worktree not auto-removed).

**Skip condition**: if the Step 4.1 fallback just ran (worktree created from `origin/{target-branch}`), it is already in sync — skip.

### Step 6: Commit & push

Process uncommitted changes inside the isolated worktree:

1. Check changes via `git status` (working directory is `$WT_PATH`).
2. If there are changes, print a change summary. **Normal mode**: confirm via **AskUserQuestion**. **`--auto` mode**: skip the prompt.
3. (Auto or after confirmation):
   - Stage with a sensitive-file exclusion pathspec, then verify nothing sensitive slipped through:
     ```bash
     git add -A -- ':(exclude,glob)**/.env*' ':(exclude,glob)**/*.pem' ':(exclude,glob)**/*.key' \
                   ':(exclude,glob)**/*credential*' ':(exclude,glob)**/*secret*'
     SENSITIVE=$(git diff --staged --name-only | grep -Ei '(^|/)\.env(\..+)?$|\.(pem|key|p12)$|credential|secret' || true)
     if [ -n "$SENSITIVE" ]; then
       echo "WARN: unstaging sensitive-looking files:" ; printf '%s\n' "$SENSITIVE"
       printf '%s\n' "$SENSITIVE" | while IFS= read -r f; do git restore --staged "$f"; done
     fi
     ```
   - Analyze `git diff --staged`, check recent commit-message style via `git log`, write a commit message, `git commit`.
4. Push via `git push -u origin "$BRANCH_NAME"`.

If there are no changes, skip this step.

> The isolated worktree shares git metadata (`.git`) with the main worktree, so push/remote settings need no separate configuration.

### Step 7: Create the PR

1. Check existing PRs via `gh pr list --head "$BRANCH_NAME" --base {target-branch} --state open`.
2. **If an existing PR exists**: print the PR URL and proceed to Step 8.
3. **If no existing PR**: create a PR with the ASTRA template:

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

- If `--draft` is specified, add `--draft`. The PR title must be ≤ 70 chars. Print the PR URL.

After the PR exists (re-used or created), capture its metadata:
```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
[ -n "${BRANCH_NAME:-}" ] || BRANCH_NAME=$(git branch --show-current)
PR_URL=$(gh pr view "$BRANCH_NAME" --json url --jq '.url')
PR_NUMBER=$(gh pr view "$BRANCH_NAME" --json number --jq '.number')
astra_state_set PR_URL "$PR_URL"
astra_state_set PR_NUMBER "$PR_NUMBER"
```

**Proceed to Step 8.**

---

## Common: code-review & merge cycle

### Step 8: Code review

Initialize the review iteration count to 0.

**Skip conditions** — when ANY is true, skip to **Step 8.3**:
- `--no-review` flag (explicit opt-out)
- `PROMOTION_SOURCE_IS_INTEGRATION=1` (promotion mode picked an integration branch in Step 10.0 — review already ran on the source sprint PRs). This path also routes through Step 10.1's jump; the check here is a defensive backstop.

Spawn the `feature-dev:code-reviewer` agent:

```
Agent tool (subagent_type: "feature-dev:code-reviewer")
- Run a code review based on the PR's changes
- Analyze bugs, logic errors, security vulnerabilities, code-quality issues
- **Important**: do not suggest removing any file under the kubernetes/ directory
- **Required output contract**: the FINAL line of the report must be exactly
  `SEVERITY_COUNTS: critical=N high=N medium=N low=N` (integers, all four keys),
  where each N equals the number of issues listed in the report body at that severity.
```

**Parse the counts ONLY from the `SEVERITY_COUNTS:` line** — do not infer from prose. If the line is missing or malformed:
1. Re-invoke the agent once, quoting the required format.
2. If still missing, treat the review as **failed** (do NOT assume 0 issues) and halt with guidance to re-run `/pr-merge` — an unparseable review must never unlock a merge.

Classify results into 4 severity levels and print:

| Severity | Description | Examples |
|----------|-------------|----------|
| **Critical** | Must fix immediately; risk of production outage | SQL injection, null reference, data loss |
| **High** | Recommended fix; important bug or security issue | Unhandled exception, possible auth bypass |
| **Medium** | Code-quality improvement; no functional impact | Duplicate code, inefficient logic, unclear naming |
| **Low** | Style/convention; optional improvement | Formatting, missing comments, unused imports |

### Step 8.1: Review-result decision

- **Critical + High = 0**: review passes → **Step 8.3**
- **Critical + High > 0 AND iteration < MAX**: → **Step 8.2**
- **Iteration = MAX reached**: options via **AskUserQuestion**
  - (a) Allow additional iterations (raise MAX)
  - (b) Ignore remaining issues and proceed to merge (**not** offered if any Critical remains)
  - (c) Abort the workflow

**Merge-block condition**: if even one Critical issue remains, the merge cannot proceed.

### Step 8.2: Auto-fix issues & re-review

1. Show the issue list to the user.
2. **Proceed with auto-fix immediately, without user confirmation.**
3. Fix each issue in order — **apply the Surgical Changes principle**:
   - Read the relevant file, locate the issue. With Edit, **only modify the lines the review points out** — do not "improve" adjacent formatting / comments / naming.
   - Do not refactor unbroken code. Remove only imports/variables made unused by your own fix; leave pre-existing dead code. Follow the existing style.
   - **Test criterion**: every modified line must trace directly to an issue. Suggest splitting unrelated changes into a separate PR.
   - **Forbidden rule**: never delete files under `kubernetes/` (edits allowed, removals ignored).
4. **Verifiable success criterion (Goal-Driven Execution)**: detect and run the project's test runner, capturing the exit code — never assess fixes by reading code alone.

   | Detection (first match wins) | Command |
   |---|---|
   | `package.json` has a `test` script | `npm test --silent` |
   | `pytest.ini` / `pyproject.toml` `[tool.pytest]` | `pytest -q` |
   | `build.gradle` / `build.gradle.kts` | `./gradlew test` |
   | `pom.xml` | `mvn -q test` |
   | `go.mod` | `go test ./...` |

   - Exit code 0 → fixes verified; continue. Non-zero → NOT verified: record the failing output, address it first next iteration, do not report fixes complete. No runner detected → record "tests: not configured".
5. Stage modified files with `git add`.
6. Increment the iteration count by 1.
7. `git commit` — message "fix: address code review issues (iteration {N})" (N starts at 1).
8. Push via `git push`.
9. **Return to Step 8** to re-review (keep the iteration count; do not reset).

> **Loop integrity**: this auto-debug loop works only because every iteration has a strong success criterion (*review pass* or *test pass*). With a weak criterion the loop diverges.

### Step 8.3: Phase decision point

The review loop converged. Decide how to proceed based on the start-state flags:

- **Promotion mode (`--staging` / `--main`)**: → **Step 8.4** (in-place merge — promotion always runs from the main worktree).
- **`STARTED_FROM_SPRINT=1`** (real sprint worktree): → **Step 8.5** (Sprint Phase ends; merge deferred to Main Phase).
- **`STARTED_FROM_SPRINT=0`** (Step 4.1 temp worktree, Step 4 compat, or Step 3.5 Main-Phase entry): → **Step 8.4** (in-place merge).

> **NO silent default**: if `STARTED_FROM_SPRINT` is unset after `astra_state_load`, re-derive it (`astra_is_isolated_worktree` → 1, else 0) and persist — never assume 0, which would in-place-merge from inside a sprint worktree.

### Step 8.4: PR merge (Main Phase / promotion mode)

Print the PR URL, review-result summary (pass/fail, iteration count), and changed-file count.

- **Normal mode**: ask for final merge confirmation via **AskUserQuestion**. On decline, abort.
- **`--auto` mode**: skip the prompt and merge directly.

After confirmation (or under `--auto`), merge the PR:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
# Never merge blind: PR_NUMBER must be known (gh cannot infer the PR from a shared branch).
if [ -z "${PR_NUMBER:-}" ]; then
  PR_NUMBER=$(gh pr list --head "$BRANCH_NAME" --state open --json number --jq '.[0].number')
fi
[ -n "${PR_NUMBER:-}" ] || { echo "ERROR: cannot determine PR number — aborting before merge" >&2; exit 1; }
# If the PR is a Draft, flip to Ready first
[ "$(gh pr view "$PR_NUMBER" --json isDraft --jq '.isDraft')" = "true" ] && gh pr ready "$PR_NUMBER"
gh pr merge "$PR_NUMBER" --merge || { echo "ERROR: gh pr merge failed — PR #$PR_NUMBER NOT merged. Stopping (no cleanup)." >&2; exit 1; }
# Verify-before-claim: confirm the PR state actually became MERGED.
PR_STATE=$(gh pr view "$PR_NUMBER" --json state --jq '.state')
[ "$PR_STATE" = "MERGED" ] || { echo "ERROR: PR #$PR_NUMBER state is '$PR_STATE', not MERGED — do not proceed to promotion/cleanup" >&2; exit 1; }
echo "✅ PR #$PR_NUMBER merged (verified state=MERGED)"
```

- **Do not use `--delete-branch`** — preserve the merged remote work branch for history/rollback/sync. Local-branch cleanup happens separately in Step 9 via `git branch -d`. Promotion-mode source branches (`dev`, `staging`) are likewise preserved.

**Mode check**:
- If `--staging` or `--main` → proceed to **Step 11** ([references/promotion-modes.md](references/promotion-modes.md)).
- If `TARGET_BRANCH` matches `^(feat|fix)/` (default mode merged into an integration branch) → proceed to **Step 8.4.5**.
- Otherwise (legacy: target was `dev`) → proceed to **Step 9**.

### Step 8.4.5: Promotion path (integration branch only)

The sprint PR has just merged into the integration branch (e.g., `feat/login`). The user chooses whether to push it into `staging` (fast hotfix path) or `dev` (standard path), or to defer.

Refresh the integration branch locally so its `HEAD` reflects the freshly merged state:
```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
[ -n "${TARGET_BRANCH:-}" ] || { echo "ERROR: TARGET_BRANCH empty — cannot promote" >&2; exit 1; }
git fetch origin "$TARGET_BRANCH" --quiet
```

#### Step 8.4.5.1: Ask the promotion path

**Always HITL** — **AskUserQuestion** fires for every invocation, including `--auto`. The promotion target materially changes the deployment surface (dev queue vs. staging deployment) and has no safe unattended default; `--auto` only suppresses low-risk confirmations (commit, final-merge approval).

The 3 options (presented in every mode):
- `Promote to dev (standard path)` — queue for the next staging promotion. **Recommended (first option)**.
- `Promote to staging (fast path)` — bypass dev, go directly to staging. For urgent hotfixes.
- `Skip (keep integration branch as-is)` — don't promote now. The integration branch persists; the user can run `/pr-merge --staging` later and pick it as the source.

**Map the answer to `$PROMOTION_TARGET`** (the literal branch name): dev → `"dev"`, staging → `"staging"`, Skip → jump to **Step 9** (no second PR). Persist via `astra_state_set` and verify `[ -n "$PROMOTION_TARGET" ]` before creating the promotion PR. Direct integration → `main` is intentionally *not* offered (production releases go through `/pr-merge --main`); `Other`-typed handling and the rationale are in [references/promotion-modes.md](references/promotion-modes.md#step-8451-answer-mapping).

#### Step 8.4.5.2–8.4.5.3: Create + merge the promotion PR

Create the promotion PR (`$TARGET_BRANCH` → `$PROMOTION_TARGET`, body lists the source sprint PR), then merge it directly (no fresh review — the source sprint PR already passed). Full bash and the result banner: **[references/promotion-modes.md](references/promotion-modes.md#default-mode-promotion-pr-mechanics-step-8452--8453)**. After the promotion PR merges (verified `state=MERGED`), proceed to **Step 9**.

### Step 8.5: Sprint Phase → Main Phase handoff

The review loop converged inside a sprint worktree. The merge runs from the main worktree (so the cascade, dev sync, and worktree removal happen in a stable location). Branch on the flag:

- **Normal mode**: print the handoff message and exit cleanly. The sprint worktree is preserved (commits and PR intact; only the merge is pending). Resolve `MAIN_ROOT` first so the printed `cd` path is concrete:
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

- **`--auto` mode**: continue automatically — the skill `cd`s into the main worktree itself (validating it lands on a shared branch and adopting the sprint scope's state via `astra_state_adopt`), then proceeds to **Step M1** so `/autorun` and `/sprint-init --auto` complete end-to-end in one invocation. Transition bash: **[references/fallbacks-and-recovery.md](references/fallbacks-and-recovery.md#step-85---auto-cross-worktree-transition-bash)**. `BRANCH_NAME`, `PR_URL`, `PR_NUMBER`, `STARTED_FROM_ISOLATED=1` are already set from Sprint Phase.

### Step M1: Main-Phase merge (entry from Step 3.5 or Step 8.5)

Two callers: **Step 3.5 → M1** (user re-invoked from the main worktree, exactly one or a user-picked pending sprint PR found) and **Step 8.5 → M1** (`--auto` transitioned directly). Both have `PR_NUMBER`, `PR_URL`, `BRANCH_NAME`, `STARTED_FROM_ISOLATED=1` set — recover with `astra_state_load` (re-derive via `gh pr list` if any is empty). The cwd is the main worktree.

> **No re-review by default**: Sprint Phase already ran the review loop. If the user pushed additional commits between phases, the existing PR review on GitHub remains the source of truth — we do not re-spawn the reviewer here. To force a fresh review, `cd` back into the sprint worktree and re-run `/pr-merge` there.

Proceed to **Step 8.4** (in-place merge using the variables set above).

---

## Cleanup (Main Phase only)

### Step 9: Cleanup and version update

After the merge, clean up the isolated worktree and local environment. Step 8.4 always runs from the main worktree under the two-phase policy. Re-anchor defensively in case a tool boundary lost the cwd:

1. **Re-anchor in the main worktree**:
   ```bash
   PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
   source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
   MAIN_ROOT=$(astra_main_worktree_root)
   cd "$MAIN_ROOT"
   ```
2. `git fetch origin`.
3. `git checkout dev` (even when `{target-branch}` is not dev, the final position unifies to dev).
4. `git pull --rebase origin dev`.
5. **Remove the isolated worktree** — only when `STARTED_FROM_ISOLATED=1`, via `astra_remove_worktree "$BRANCH_NAME"` (helper only warns and continues if the worktree is dirty). The `STARTED_FROM_ISOLATED=0` compat case skips removal (the main worktree must not be removed).
6. **Delete the merged local sprint branch** — only when `STARTED_FROM_ISOLATED=1` AND the branch matches `^(feat|fix)/sprint-` (safe `git branch -d`, auto-skipped if unmerged). Integration branches (`feat/<name>`, `fix/<name>` without `sprint-`) are **persistent** and must not be deleted.
6.5. **Completion Gate — verify before reporting success**: print the final summary ONLY when all three gates pass — (1) PR state = MERGED, (2) sprint worktree gone (when `STARTED_FROM_ISOLATED=1`), (3) current branch = dev — otherwise report exactly which failed. Then `astra_state_clear`.

   Exact guard bash for steps 5 / 6 / 6.5 and the integration-branch retention note: **[references/fallbacks-and-recovery.md](references/fallbacks-and-recovery.md#step-9-cleanup-mechanics-bash)**.

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

## Promotion mode (`--staging` / `--main`)

Promotes code between branches: `--staging` (source `dev` or an integration branch → `staging`), `--main` (source `staging` or an integration branch → `main`, with version bump). Runs only in the main worktree; Step 2's cascade is skipped. Full procedure — Step 10 (prep + source pick), Step 10.1 (create promotion PR), Step 11 (cleanup + version bump): **[references/promotion-modes.md](references/promotion-modes.md)**. Read it when `--staging` or `--main` was passed.

---

## Quick Run Examples

```
cd .astra-worktrees/sprint-3-user-auth && /pr-merge   # Sprint Phase: pick/create integration branch → commit → push → PR → review loop, then exits
cd "$(git rev-parse --git-common-dir)/.." && /pr-merge # Main Phase: auto-detect pending sprint PR → merge → promotion path prompt (staging/dev/skip)

/pr-merge 5                 # up to 5 review iterations (Sprint Phase only)
/pr-merge --no-review       # quick merge without code review
/pr-merge --draft           # create as Draft PR then review
/pr-merge --minor           # minor version bump (only matters on --main promotion)
/pr-merge --auto            # unattended end-to-end (both phases + auto-cd); promotion target still HITL

/pr-merge --staging         # promote dev → staging (Step 10.0 asks source: bulk dev or an integration branch)
/pr-merge --main            # promote staging → main / release (Step 10.0 asks source; version bump here)
/pr-merge --staging --no-review
```

## Notes

- **Branch strategy (v5.11+)**: `feat/sprint-<N>-<name> → feat/<name> | fix/<name> (integration) → dev | staging → main`. The integration branch is persistent and may receive multiple sprint PRs before promotion.
- **Two-phase policy (v5.9+)**: `gh pr merge` only runs from the main worktree. Inside a sprint worktree, `/pr-merge` runs Sprint Phase and stops; the user `cd`s to the main worktree and re-invokes it (Step 3.5 auto-detects the pending sprint PR, then Step 8.4.5 always asks the promotion path — HITL even under `--auto`). With `--auto`, the skill performs the cross-worktree transition itself.
- **Worktree policy (v5.0+)**: sprint worktrees are created by `/sprint-init`. Right after Main Phase merges into the integration branch (+ optional promotion), the sprint worktree is auto-removed (Step 9). Cascade merges and promotions run in the main worktree. On conflict the worktree remains — after resolving, re-run `/pr-merge`.
- **Default mode (v5.11+)**: the merge target is an integration branch chosen in Step 4.5 — pick existing or create from a user-chosen base (default `origin/dev`). Classification (feat vs fix) and slug are auto-inferred (see [references/integration-branch-inference.md](references/integration-branch-inference.md)). Under `--auto`, the inferred name is reused if it exists, else auto-created from `origin/dev`.
- **Promotion / fallback details**: promotion modes (`--staging`/`--main`) → [references/promotion-modes.md](references/promotion-modes.md); one-shot temp-worktree fallback, pre-v5.11 PR detection, compat cases → [references/fallbacks-and-recovery.md](references/fallbacks-and-recovery.md).
- Final checkout location after merge: default mode ends on `dev`; promotion mode returns to `dev`.
- If Critical issues remain, merging is blocked. On conflict, do not auto-resolve — instruct the user and abort.
- Before commits and merges, user confirmation is required. After-review issue fixes proceed automatically without confirmation.
- **kubernetes protection rule**: during review and fixes, do not delete files under `kubernetes/`.
- **Remote-branch preservation policy**: after merging, remote work branches (`feat/*`, `fix/*`, `docs/*`, …) are not deleted from the remote (history/rollback/reuse). Only local sprint branches (`feat/sprint-*`, `fix/sprint-*`) are safely deleted with `git branch -d`. **Integration branches** (`feat/<name>`, `fix/<name>` without `sprint-`) are persistent on both local and remote — Step 9 protects them. Clean them up manually only after confirming no in-flight PRs target them.
- **`--no-review` precedence**: when `--no-review` is set, Step 8 is skipped regardless of source type. The `PROMOTION_SOURCE_IS_INTEGRATION=1` skip is additive — either condition alone bypasses review.
- **Surgical Changes principle**: during Step 8.2 fixes, change only the lines flagged by the review. Arbitrary refactoring / format / naming "improvements" on adjacent code are forbidden. Split unrelated improvements into a separate PR. (See: Behavioral Guardrails in the `coding-convention` skill.)
