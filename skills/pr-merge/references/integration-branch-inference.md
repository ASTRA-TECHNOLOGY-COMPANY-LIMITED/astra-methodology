# pr-merge — Integration branch inference & selection (Step 4.5 detail)

Full detail for SKILL.md **Step 4.5** (Sprint Phase only, `STARTED_FROM_SPRINT=1`). SKILL.md keeps a summary + the outcome contract (`TARGET_BRANCH`, `CREATE_NEW`, `BASE_REF`); the classification heuristic and per-sub-step bash live here.

Run this **only when `STARTED_FROM_SPRINT=1`** (the normal flow from a real sprint worktree). For every skipped case — Step 4.1 temp-worktree fallback, main-worktree work-branch compat (`STARTED_FROM_SPRINT=0`), promotion mode — set `TARGET_BRANCH="dev"` and proceed to **Step 5**.

Every Bash block assumes the PREAMBLE (SKILL.md Step 1 state protocol).

## Step 4.5.1: Infer classification (feat vs fix)

Derive the integration-branch prefix from three signals, in priority order:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
[ -n "${BRANCH_NAME:-}" ] || BRANCH_NAME=$(git branch --show-current)   # re-derive if state was lost
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
# find, not `ls glob` — an unmatched glob in zsh errors before 2>/dev/null applies
BP_HINTS_FIX=0
BP_DIR=$(find docs/blueprints -maxdepth 1 -type d -name "*-${SLUG}" 2>/dev/null | head -1)
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
astra_state_set INFERRED_NAME "$INFERRED_NAME"
echo "Inferred integration branch: $INFERRED_NAME (commits: feat=$FEAT_COUNT fix=$FIX_COUNT, slug-hints=$SLUG_HINTS_FIX, blueprint-hints=$BP_HINTS_FIX)"
```

## Step 4.5.2: List existing integration branches

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
git fetch origin --quiet
# Sort by recent activity, exclude sprint-* branches, keep only feat/* and fix/*.
# NOTE: plain string variable (newline-separated), NOT a bash array — `mapfile`
# does not exist in zsh or macOS's default bash 3.2.
EXISTING_INTS=$(git for-each-ref --sort=-committerdate \
    --format='%(refname:lstrip=3)' \
    refs/remotes/origin/feat refs/remotes/origin/fix 2>/dev/null \
    | grep -vE '^(feat|fix)/sprint-' \
    | head -10)
astra_state_set EXISTING_INTS "$EXISTING_INTS"
```

## Step 4.5.3: Pick existing or create new

**`--auto` mode** — safe default (no prompts):
```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
if printf '%s\n' "$EXISTING_INTS" | grep -qxF "$INFERRED_NAME"; then
  TARGET_BRANCH="$INFERRED_NAME"   # reuse existing
  echo "[--auto] Reusing existing integration branch: $TARGET_BRANCH"
else
  TARGET_BRANCH="$INFERRED_NAME"   # create new from origin/dev
  CREATE_NEW=1
  BASE_REF="origin/dev"
  echo "[--auto] Creating new integration branch: $TARGET_BRANCH (base: $BASE_REF)"
fi
astra_state_set TARGET_BRANCH "$TARGET_BRANCH"
astra_state_set CREATE_NEW "${CREATE_NEW:-0}"
```

**Normal mode** — branch on whether existing integration branches were found:

- **`EXISTING_INTS` is empty** (first sprint of a new project, or no integration branches ever created): skip the pick-or-create AskUserQuestion entirely — there is nothing to pick from and `AskUserQuestion` requires `minItems: 2`. Set `TARGET_BRANCH="$INFERRED_NAME"`, `CREATE_NEW=1`, print the inferred name for transparency, and proceed directly to Step 4.5.4 (base selection).
- **`EXISTING_INTS` has 1+ entries**: HITL via **AskUserQuestion**. Total options must stay within `AskUserQuestion`'s `maxItems: 4`. Build the option list as:
  - Up to 3 most-recent existing integration branches from `EXISTING_INTS`
  - Final option (always): `Create new with inferred name: <INFERRED_NAME>` — selecting this proceeds directly to Step 4.5.4 with `TARGET_BRANCH="$INFERRED_NAME"`, `CREATE_NEW=1`.
  - The harness-added `Other` option (auto-appended outside the 4-slot count) lets the user type a custom name. If the typed name matches an entry in `EXISTING_INTS`, treat as pick; otherwise treat as create-new (set `TARGET_BRANCH=<typed>`, `CREATE_NEW=1`) and proceed to Step 4.5.4.

If the user picks an existing branch → set `TARGET_BRANCH=<picked>`, `CREATE_NEW=0`. In every branch of this decision, persist the outcome: `astra_state_set TARGET_BRANCH "$TARGET_BRANCH"` and `astra_state_set CREATE_NEW "$CREATE_NEW"`.

## Step 4.5.4: Choose base branch (only when creating new)

Skip when `CREATE_NEW=0` (existing branch reused).

**`--auto` mode**: `BASE_REF="origin/dev"`, no prompt.

**Normal mode**: ask via **AskUserQuestion** which base to branch from. Within the 4-option cap, list (existence-checked via `git ls-remote --heads origin`):
- `origin/dev` (Recommended — matches sprint worktree's base, cleanest sprint→integration merge)
- `origin/staging` (cleaner integration→staging promotion, but possible sprint→integration conflicts)
- `origin/main` (closest to production — for hotfix integration branches)
- `origin/master` (only when `main` doesn't exist — otherwise drop this slot)

The harness auto-adds an `Other` option outside the 4-slot count, letting the user type a custom ref like a specific commit SHA or a `release/*` branch. Skip listed options whose underlying remote branch doesn't exist (e.g., projects without `staging` only see dev/main/master).

Validate the chosen ref exists, then persist it:
```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
git ls-remote --exit-code --heads origin "${BASE_REF#origin/}" >/dev/null 2>&1 || {
  echo "ERROR: base ref '$BASE_REF' not found on remote" >&2
  exit 1
}
astra_state_set BASE_REF "$BASE_REF"
```

## Step 4.5.5: Create the integration branch on the remote (if new)

Skip when `CREATE_NEW=0`.

Guard against the race where the user typed (or selected "create with inferred name" for) a branch name that already exists on the remote — this happens when `INFERRED_NAME` collides with an existing entry of `EXISTING_INTS` and the user picked the "Create new" option anyway. Without the guard, `git push origin <base>:refs/heads/<existing>` would be rejected and the user would have to re-run.

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
# Guard: never push with empty refs (state loss would create a wrong branch)
[ -n "${TARGET_BRANCH:-}" ] || { echo "ERROR: TARGET_BRANCH empty — re-run Step 4.5.3" >&2; exit 1; }
[ "${CREATE_NEW:-0}" = "1" ] && [ -z "${BASE_REF:-}" ] && { echo "ERROR: BASE_REF empty — re-run Step 4.5.4" >&2; exit 1; }
if git ls-remote --exit-code --heads origin "$TARGET_BRANCH" >/dev/null 2>&1; then
  echo "INFO: integration branch '$TARGET_BRANCH' already exists on origin — reusing instead of creating"
  CREATE_NEW=0
  astra_state_set CREATE_NEW 0
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

After this step, `$TARGET_BRANCH` is the integration branch the sprint PR will target. All subsequent steps that reference `{target-branch}` use this value. Return to SKILL.md **Step 5**.
