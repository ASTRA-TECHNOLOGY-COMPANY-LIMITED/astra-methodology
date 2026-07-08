# pr-merge — Promotion mechanics & promotion mode (`--staging` / `--main`)

This reference holds the promotion-PR mechanics shared by the default-mode post-merge promotion (Step 8.4.5) and the dedicated promotion mode (`--staging` / `--main`, Steps 10–11). SKILL.md keeps the promotion *decision* (Step 8.4.5.1 HITL) inline; the PR create/merge bash and the whole promotion mode live here.

Every Bash block below assumes the PREAMBLE (see SKILL.md Step 1 state protocol):

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(find ~/.claude/plugins/cache -maxdepth 3 -type d -path '*/astra-methodology/*' 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
```

---

## Step 8.4.5.1 answer mapping

SKILL.md Step 8.4.5.1 asks the promotion path (dev / staging / skip). Full answer → variable mapping:

| User's choice | Action |
|---|---|
| `Promote to dev (standard path)` | `PROMOTION_TARGET="dev"` |
| `Promote to staging (fast path)` | `PROMOTION_TARGET="staging"` |
| `Skip (keep integration branch as-is)` | jump to **Step 9** — no second PR is created |
| `Other` with typed text | typed `dev`/`staging` → use it. Anything else (`main`, `production`, …): explain direct promotion to `main` is only via `/pr-merge --main`, then treat as `Skip` (jump to Step 9). Never adopt a target outside {dev, staging}. |

Persist it: `astra_state_set PROMOTION_TARGET "$PROMOTION_TARGET"`. Verify `[ -n "$PROMOTION_TARGET" ]` before creating the promotion PR — an empty value would create a PR against a nonexistent base.

> **Note on `main`**: direct integration → `main` is intentionally *not* offered. Production releases go through `/pr-merge --main` (which carries the version bump and release checks). For a production-direct hotfix, choose `staging` here, then run `/pr-merge --main` and pick the same integration branch as source.

## Default-mode promotion PR mechanics (Step 8.4.5.2 / 8.4.5.3)

Reached from SKILL.md Step 8.4.5.1 after the user chose `dev` or `staging` (skip jumps straight to Step 9). `$PROMOTION_TARGET` holds the literal branch name; `$TARGET_BRANCH` is the just-merged integration branch.

### Step 8.4.5.2: Create the promotion PR

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(find ~/.claude/plugins/cache -maxdepth 3 -type d -path '*/astra-methodology/*' 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
# Guard: both refs must be known before creating a PR between them.
[ -n "${TARGET_BRANCH:-}" ] && [ -n "${PROMOTION_TARGET:-}" ] || { echo "ERROR: TARGET_BRANCH/PROMOTION_TARGET empty — redo Step 8.4.5.1" >&2; exit 1; }
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
astra_state_set PROMO_NUMBER "$PROMO_NUMBER"
astra_state_set PROMO_URL "$PROMO_URL"
```

### Step 8.4.5.3: Merge the promotion PR (no fresh review)

The source sprint PR already passed code review. Merge directly:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(find ~/.claude/plugins/cache -maxdepth 3 -type d -path '*/astra-methodology/*' 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
# Re-derive if state was lost — never merge an empty PR number.
if [ -z "${PROMO_NUMBER:-}" ]; then
  PROMO_NUMBER=$(gh pr list --head "$TARGET_BRANCH" --base "$PROMOTION_TARGET" --state open --json number --jq '.[0].number')
fi
[ -n "${PROMO_NUMBER:-}" ] || { echo "ERROR: cannot determine promotion PR number — aborting" >&2; exit 1; }
gh pr merge "$PROMO_NUMBER" --merge || { echo "ERROR: promotion merge failed — PR #$PROMO_NUMBER NOT merged. Stopping." >&2; exit 1; }
# Verify-before-claim: only print the success banner after confirming state.
[ "$(gh pr view "$PROMO_NUMBER" --json state --jq '.state')" = "MERGED" ] \
  || { echo "ERROR: promotion PR #$PROMO_NUMBER is not in MERGED state — do not print success" >&2; exit 1; }
```

- **Do not use `--delete-branch`** — the integration branch (`$TARGET_BRANCH`) is persistent and may accumulate more sprints.
- On merge conflict (rare — most conflicts surface in Step 5's sync): halt and instruct the user to resolve manually via the GitHub UI or local checkout.

Print the promotion result (only after the MERGED verification above passed):

```
═══════════════════════════════════════════════════════
✅ Promoted: $TARGET_BRANCH → $PROMOTION_TARGET
   PR: $PROMO_URL
═══════════════════════════════════════════════════════
```

Proceed to **Step 9**.

---

## Promotion mode (`--staging` / `--main`)

Entered from SKILL.md Step 3 when `--staging` or `--main` was passed. Runs only in the main worktree (`astra_ensure_main_worktree`). Step 2's cascade is skipped in promotion mode.

### Step 10: Promotion prep

Promotion mode is the workflow that *promotes* code between branches.

**Branch mapping (v5.11.1+)**:
- `--staging`: `{target-branch}` = `staging`. `{source-branch}` = **chosen in Step 10.0**: legacy `dev` (default — bulk promote all accumulated dev) OR a specific integration branch `feat/<name>` / `fix/<name>` (feature-level promotion — skip dev, land only this feature on staging).
- `--main`: `{target-branch}` = `main`. `{source-branch}` = **chosen in Step 10.0**: legacy `staging` (default — bulk promote all accumulated staging) OR a specific integration branch (feature-level promotion — land only this feature on main, bypassing other staging changes).

#### Step 10.0: Pick the promotion source

`{target-branch}` is fixed by the mode (`staging` for `--staging`, `main` for `--main`). The source is picked interactively so the user can choose between bulk promotion and feature-level promotion.

**`--auto` mode** — safe default: legacy bulk source.
```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(find ~/.claude/plugins/cache -maxdepth 3 -type d -path '*/astra-methodology/*' 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
case "$MODE" in
  --staging) SOURCE_BRANCH="dev" ;;
  --main)    SOURCE_BRANCH="staging" ;;
esac
PROMOTION_SOURCE_IS_INTEGRATION=0
astra_state_set SOURCE_BRANCH "$SOURCE_BRANCH"
astra_state_set PROMOTION_SOURCE_IS_INTEGRATION 0
echo "[--auto] Promotion source: $SOURCE_BRANCH (legacy bulk path)"
```

**Normal mode** — HITL via **AskUserQuestion**. Build the source option list:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(find ~/.claude/plugins/cache -maxdepth 3 -type d -path '*/astra-methodology/*' 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
# Default source per mode
case "$MODE" in
  --staging) DEFAULT_SOURCE="dev" ;;
  --main)    DEFAULT_SOURCE="staging" ;;
esac
astra_state_set DEFAULT_SOURCE "$DEFAULT_SOURCE"

# List existing integration branches (most-recent first, excluding sprint-*).
# Plain string variable (newline-separated) — `mapfile` is bash-4-only and
# fails on zsh / macOS default bash 3.2.
git fetch origin --quiet
INT_BRANCHES=$(git for-each-ref --sort=-committerdate \
    --format='%(refname:lstrip=3)' \
    refs/remotes/origin/feat refs/remotes/origin/fix 2>/dev/null \
    | grep -vE '^(feat|fix)/sprint-' \
    | head -3)
```

Within `AskUserQuestion`'s 4-option cap, list:
- `<DEFAULT_SOURCE>` — labeled "Bulk promote (Recommended)" with description "Promote all accumulated changes from $DEFAULT_SOURCE — runs Step 8 code-review loop"
- Up to 3 entries from `INT_BRANCHES` — each labeled with the integration branch name and description "Promote only this integration branch ($name) — skips code review (already passed on sprint PR)"

The harness-appended `Other` option lets the user type any custom source ref (e.g., a long-lived branch outside the integration namespace).

Decision logic:
- If user picks `DEFAULT_SOURCE` → `SOURCE_BRANCH=$DEFAULT_SOURCE`, `PROMOTION_SOURCE_IS_INTEGRATION=0`
- If user picks an integration branch → `SOURCE_BRANCH=<picked>`, `PROMOTION_SOURCE_IS_INTEGRATION=1`
- If user picks `Other` → take the typed value as `SOURCE_BRANCH`. Set `PROMOTION_SOURCE_IS_INTEGRATION=1` if `SOURCE_BRANCH` matches `^(feat|fix)/`, else 0 (treat unknown sources as bulk-like — review still runs).
- In every branch, persist: `astra_state_set SOURCE_BRANCH "$SOURCE_BRANCH"` and `astra_state_set PROMOTION_SOURCE_IS_INTEGRATION "$PROMOTION_SOURCE_IS_INTEGRATION"`.

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
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(find ~/.claude/plugins/cache -maxdepth 3 -type d -path '*/astra-methodology/*' 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
[ -n "${SOURCE_BRANCH:-}" ] || { echo "ERROR: SOURCE_BRANCH empty — redo Step 10.0" >&2; exit 1; }
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
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(find ~/.claude/plugins/cache -maxdepth 3 -type d -path '*/astra-methodology/*' 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh" && astra_state_load
[ -n "${SOURCE_BRANCH:-}" ] || { echo "ERROR: SOURCE_BRANCH empty — redo Step 10.0" >&2; exit 1; }
# In promotion mode the target is fixed by the flag — re-derive if state was lost:
if [ -z "${TARGET_BRANCH:-}" ]; then
  case "$MODE" in --staging) TARGET_BRANCH="staging" ;; --main) TARGET_BRANCH="main" ;; esac
  astra_state_set TARGET_BRANCH "$TARGET_BRANCH"
fi
[ -n "${TARGET_BRANCH:-}" ] || { echo "ERROR: TARGET_BRANCH unresolved" >&2; exit 1; }
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
7. Clear workflow state (`astra_state_clear`) and print the final summary:

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
