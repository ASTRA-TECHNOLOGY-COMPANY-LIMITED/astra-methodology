---
name: sprint-init
description: "Initializes an ASTRA sprint in an isolated worktree (.worktrees/sprint-<N>-<name>/) with port isolation and scaffolding, then runs the pipeline to completion in the same session: /test-scenario → implementation → /test-run → adversarial verification gate (score ≥ 90 ∧ P0 == 0) → /pr-merge. Flags: --scaffold-stop, --scaffold-only (the /blueprint delegation mode), --auto, --resume. Use when starting a new sprint or scaffolding sprint infrastructure."
argument-hint: "[sprint-number] [sprint-name] [--auto] [--max-iter=N] [--resume] [--from-blueprint] [--scaffold-only] [--scaffold-stop]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Skill, Task, Agent, TodoWrite
---

# ASTRA Sprint Initialization (v5.16+ one-flow · v5.19+ worktree-always)

> **Korean output style**: for Korean user-facing text (HITL questions, status reports, answers), apply `$CLAUDE_PLUGIN_ROOT/docs/development/korean-style.md` — §"HITL 질문 작성 규칙" and §"답변·보고 원칙". Korean files written to disk are style-checked automatically by the korean-style PostToolUse hook.

Creates the sprint worktree, writes port-isolated env settings, generates prompt maps / progress trackers / retrospective templates, and **continues in the same session through implementation, the adversarial test loop, and `/pr-merge`** — the pipeline is the default, not an opt-in.

> **v5.19+ isolation policy (worktree-always)**: every sprint runs inside an isolated worktree at `.worktrees/sprint-<N>-<name>/` holding the `feat/sprint-<N>-<name>` branch. **Sprint work is never performed in the main worktree** — the main worktree stays on its shared branch (`dev`) for the whole sprint; the only main-worktree activity in the sprint lifecycle is `/blueprint`'s authoring + dev push, which happens *before* this skill creates the worktree. The v5.16 in-place mode (sprint branch checked out in the main worktree) is removed. Still: one PR per sprint, one continuous session, no user `cd` at any point (the skill performs the single `cd` into the worktree itself).

## Execution Procedure

### Step 0.A: Resume Detection (`--resume` flag)

`--resume` is **for true recovery only** — the LLM lost in-flight variables after context auto-compression, the user intentionally stopped mid-run, or the skill terminated abnormally. In normal `--auto` operation the skill never interrupts between stages (it silently checkpoints `auto-state.yaml` and auto-advances), so `--resume` is not on the happy path.

Parse the flag first:

```bash
RESUME_MODE=0
for arg in $ARGUMENTS; do
  [ "$arg" = "--resume" ] && RESUME_MODE=1 && break
done
```

If `RESUME_MODE=1`, follow the resume procedure in [references/auto-pipeline.md](references/auto-pipeline.md) (§Step 0.A) — it locates the in-progress worktree, reads `auto-state.yaml` as SSoT, restores all state variables, **skips Steps 0–4** (worktree/scaffold already exist), and jumps directly to `progress.next_stage`.

If `RESUME_MODE=0`, proceed normally to Step 0.B.

### Step 0.B: Main Worktree Guard (new sprint only)

This command *creates* a sprint worktree, so it must run in the main worktree only. Reject if already inside an isolated worktree:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(find ~/.claude/plugins/cache -maxdepth 3 -type d -path '*/astra-methodology/*' 2>/dev/null | sort -V | tail -1)}"
if [ -z "$PLUGIN_ROOT" ] || [ ! -f "$PLUGIN_ROOT/scripts/worktree-helpers.sh" ]; then
  echo "ERROR: CLAUDE_PLUGIN_ROOT not found. Verify the plugin cache path." >&2
  exit 1
fi
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"
astra_ensure_main_worktree || exit 1
```

### Step 1: Confirm Sprint Number, Sprint Name, and Mode

Parse from `$ARGUMENTS`:
- **Sprint number** (optional): If not provided, scan existing directories in `docs/sprints/` matching the `sprint-{N}-{name}/` pattern (e.g., `sprint-1-auth/`, `sprint-2-workspace/`) to determine the next number.
- **Sprint name** (optional): The primary blueprint/feature name for this sprint.
- **`--auto`** (optional flag): If present, set `AUTO_MODE=1` — the Step 5 pipeline runs **unattended** (`PIPELINE_MODE=auto`: merge confirmation auto-approved via `/pr-merge --auto`; promotion target stays HITL). **v5.16+ without this flag the pipeline still runs** — in `attended` mode (HITL at merge confirmation / promotion / Critical issues only).
- **`--scaffold-stop`** (optional flag, v5.16+): stop after Step 4 (scaffolding + planning guide) without entering the pipeline — the pre-v5.16 default behavior, for teams that fill the prompt map collaboratively before implementation.
- **`--max-iter=N`** (optional): max self-improving iteration count for the test/verification loop (1 ≤ N ≤ 10). **Default 5 — never asked** (the Step 5.4.5 adversarial gate governs quality; the cap is a runaway bound).
- **`--from-blueprint`** (optional flag, legacy): backward-compat alias for `--scaffold-only`. Set `FROM_BLUEPRINT=1`; treated identically to `SCAFFOLD_ONLY=1` at every read site.
- **`--scaffold-only`** (optional flag, v5.10+): Indicates this invocation is delegated from the `/blueprint` flow (v5.19+: the blueprint **has already been authored, committed to `dev`, and pushed** by the caller) — `/sprint-init` only creates the sprint worktree (branched from `origin/dev`, so it already contains the blueprint) + writes the port env file + scaffolds prompt-map / progress / retrospective, and then exits. Set `SCAFFOLD_ONLY=1` when present. **Read sites**:
  - Step 2 below — when `SCAFFOLD_ONLY=1`, the prompt-map omits the Feature 1.1 (`/blueprint ...`) line entirely and renumbers the remaining steps (1.1=DB Design, 1.2=Test Cases, 1.3=Implementation). The blueprint already exists on `dev` (authored by the calling `/blueprint` flow) and is present in the worktree base.
  - Step 4 — same suppression as `--from-blueprint` (parent renders consolidated output).
  - Step 5 — `--scaffold-only` is **incompatible** with `--auto`. If both are present, abort with `"❌ --scaffold-only and --auto cannot be combined (no blueprint exists yet to drive the auto pipeline)"`.

**Directory name format**: `sprint-{N}-{sprint-name}/` (e.g., `sprint-1-auth/`, `sprint-2-payment/`, `sprint-3-dashboard/`)

If the sprint name is not provided in `$ARGUMENTS`, ask the user for the primary feature/blueprint name. This name will be used as the directory suffix. Use kebab-case format (e.g., `auth`, `workspace`, `payment-dashboard`).

When scanning existing directories, extract the sprint number from directory names matching pattern `sprint-{N}-{name}` (e.g., `sprint-1-auth` → number `1`).

### Step 1.4: Main Worktree Branch Guard (v5.19+)

Sprints always run in an isolated worktree, so the main worktree's branch is never checked out or dirtied by this skill. Still, guard against a non-standard starting state (v5.10+ policy):

```bash
CUR_BRANCH=$(git branch --show-current)
case "$CUR_BRANCH" in
  dev|main|master|staging) : ;;   # standard — proceed
  *) echo "❌ ERROR: main worktree is on non-standard branch '$CUR_BRANCH'. Checkout dev and re-run." >&2
     exit 1 ;;
esac
```

> **Why this still matters with worktree-always isolation**: the worktree is created from `origin/${SOURCE_BRANCH}` (checkout-free for the main tree), but a main worktree parked on a stray branch usually means an interrupted flow (e.g., a pre-v5.19 in-place sprint) — surfacing it early beats debugging a mis-based sprint later. A dirty main tree is NOT a blocker anymore: worktree creation never touches it.

### Step 1.5: Choose Source Branch and Sync

The sprint worktree branches from a user-chosen base (default `origin/dev`). v5.11+ exposes this choice so a sprint can be branched from `staging` (matches an integration branch that's based on staging — cleanest sprint→integration→staging promotion) or from `main`/`master` (urgent hotfix path) when needed.

#### Step 1.5.1: Discover available source branches

```bash
git fetch origin --quiet
AVAILABLE=()
for b in dev staging main master; do
  git ls-remote --exit-code --heads origin "$b" >/dev/null 2>&1 && AVAILABLE+=("$b")
done
if [ ${#AVAILABLE[@]} -eq 0 ]; then
  echo "ERROR: none of dev/staging/main/master found on origin" >&2
  exit 1
fi
```

#### Step 1.5.2: Pick the source branch

**`--auto` mode** — safe default: pick `dev` if present, else `main`/`master`/`staging` in that order. No prompt.

**`--scaffold-only` / `--from-blueprint` mode** (called by `/blueprint`) — `/blueprint` Step 1 has already validated the user is on a standard branch (dev/main/master) in the main worktree, authored the blueprint there, and pushed it to that branch **without changing cwd**, so reading the current branch directly is correct:
```bash
SOURCE_BRANCH=$(git branch --show-current)
case "$SOURCE_BRANCH" in
  dev|main|master|staging) : ;;  # acceptable — /blueprint's guard passed
  "")
    # detached HEAD — shouldn't happen since /blueprint Step 1 guards against it,
    # but defensive fallback: pick dev if present, else main, else master
    for fallback in dev main master; do
      git ls-remote --exit-code --heads origin "$fallback" >/dev/null 2>&1 && { SOURCE_BRANCH="$fallback"; break; }
    done
    ;;
  *)
    # /blueprint should have aborted, but be defensive
    echo "ERROR: --scaffold-only invoked from non-standard branch '$SOURCE_BRANCH'; expected dev/main/master/staging" >&2
    exit 1
    ;;
esac
```
No prompt is issued — `/blueprint` already curated the entry conditions.

**Normal mode** — **AskUserQuestion** within the 4-option cap (`Other` is auto-appended by the harness outside the cap and lets the user type any custom ref like `release/2026Q2`). List only branches present in `AVAILABLE`:
- `dev` (Recommended — standard sprint base)
- `staging` (when present — for sprints that target the fast staging-direct promotion path)
- `main` (when present — for urgent hotfix sprints branching from production state)
- `master` (only when `main` doesn't exist — otherwise drop this slot to keep within 4)

Save the chosen branch as `SOURCE_BRANCH`. Validate:
```bash
git ls-remote --exit-code --heads origin "$SOURCE_BRANCH" >/dev/null 2>&1 || {
  echo "ERROR: source branch '$SOURCE_BRANCH' not found on origin" >&2
  exit 1
}
```

#### Step 1.5.3: Align the main worktree to the source branch

The sprint worktree is created from `origin/${SOURCE_BRANCH}` (Step 1.6), so the *only* alignment needed is a fresh local ref for `SOURCE_BRANCH`. **Do not checkout + pull** — a checkout disrupts other sessions/skills sharing the main worktree and can leave it on an unexpected branch. Prefer a checkout-free fast-forward of the ref:

```bash
CUR_BRANCH=$(git branch --show-current)
git fetch origin --quiet "$SOURCE_BRANCH" || { echo "ERROR: git fetch origin $SOURCE_BRANCH failed" >&2; exit 1; }

if [ "$SOURCE_BRANCH" = "$CUR_BRANCH" ]; then
  # SOURCE_BRANCH is checked out here → cannot update its ref without touching the working tree.
  # Rebase local commits onto origin; on conflict, warn and continue (base ref is origin/SOURCE_BRANCH anyway).
  if ! git pull --rebase --quiet origin "$SOURCE_BRANCH"; then
    git rebase --abort 2>/dev/null
    echo "⚠️  Could not fast-forward local '$SOURCE_BRANCH' (diverged/conflict). Continuing with origin/$SOURCE_BRANCH as the worktree base." >&2
  fi
else
  # Not checked out → update the ref WITHOUT a checkout (no working-tree disruption).
  # This fails on non-fast-forward (local has commits not on origin) — that's fine: warn and continue.
  if ! git fetch origin --quiet "$SOURCE_BRANCH:$SOURCE_BRANCH"; then
    echo "⚠️  Local '$SOURCE_BRANCH' is not a fast-forward of origin/$SOURCE_BRANCH (has un-pushed commits). Leaving it untouched; worktree base is origin/$SOURCE_BRANCH." >&2
  fi
fi
```

The worktree base is always `origin/${SOURCE_BRANCH}` regardless of the local-ref outcome, so a warning here is non-fatal.

> **Main worktree post-state**: this step leaves the main worktree **on whatever branch it was already on** (no checkout). The sprint worktree is independent — feature work happens inside it on the sprint branch. `/pr-merge` Step 9 returns the main worktree to `dev` after merge.

### Step 1.6: Create the Sprint Worktree

Create a new isolated worktree at `.worktrees/sprint-{N}-{sprint-name}/` on the `feat/sprint-{N}-{sprint-name}` branch. Every downstream step (and the shared pipeline) uses the two variables set here — `SPRINT_BRANCH` and `WT_PATH`.

```bash
SPRINT_N="{confirmed sprint number}"
SPRINT_NAME="{confirmed sprint name}"

# Pass the user-chosen SOURCE_BRANCH from Step 1.5.2 as the base-ref (3rd arg).
# astra_create_sprint_worktree prepends "origin/" automatically when missing.
if ! out=$(astra_create_sprint_worktree "$SPRINT_N" "$SPRINT_NAME" "origin/${SOURCE_BRANCH}"); then
  echo "ERROR: sprint worktree creation failed" >&2
  exit 1
fi
IFS=$'\t' read -r SPRINT_BRANCH WT_PATH <<< "$out"
if [ -z "$WT_PATH" ] || [ ! -d "$WT_PATH" ]; then
  echo "ERROR: could not determine sprint worktree path. helper output: '$out'" >&2
  exit 1
fi
echo "Sprint worktree created from origin/${SOURCE_BRANCH}: $WT_PATH (branch: $SPRINT_BRANCH)"
```

`astra_create_sprint_worktree` absorbs branch/slug/port conflicts, so use the returned `$SPRINT_BRANCH`·`$WT_PATH` *as-is* (it may differ from the desired name).

### Step 1.7: Write Worktree Port Env File

Create `.astra-worktree.env` inside the worktree. `/test-run` sources this file before starting the server to apply the sprint-specific ports.

```bash
# Default port base: 3000 (Node-stack default). Other stacks are derived automatically by the conversion formula inside the env file.
PORT_BASE_DEFAULT=3000
if ! PORT_BASE=$(astra_compute_port_base "$PORT_BASE_DEFAULT" "$SPRINT_N"); then
  echo "ERROR: could not find an available port base" >&2
  exit 1
fi

astra_write_worktree_env "$WT_PATH" "$SPRINT_N" "$SPRINT_NAME" "$PORT_BASE" || exit 1
echo "Sprint port base: $PORT_BASE (offset=$((PORT_BASE - PORT_BASE_DEFAULT)))"
```

The generated file contains per-framework values such as `ASTRA_PORT_BASE`, `PORT`, `VITE_PORT`, `SERVER_PORT`, `DJANGO_PORT`, `FASTAPI_PORT`. `/test-run` picks the value matching the detected stack to start the server.

### Step 1.8: Anchor in the Sprint Worktree

From here on, deliverable writing and progress tracking happen on the sprint branch, inside the worktree:

```bash
cd "$WT_PATH"
```

> From this point on, the "current working directory" is `$WT_PATH`, and every docs/sprints/* file is committed onto the sprint branch. This is the **only** directory change in the entire sprint lifecycle, and the skill performs it itself — the user is never asked to `cd`. The main worktree is left untouched on its shared branch.

### Step 2: Create Sprint Prompt Map

Create the file `$WT_PATH/docs/sprints/sprint-{N}-{sprint-name}/prompt-map.md`.

Scan `docs/blueprints/` for numbered directories matching the sprint name (or use the blueprint names provided by the user). Each blueprint becomes a feature in the prompt map. Do NOT analyze or carry over items from previous sprints.

Instantiate the correct variant from `references/prompt-map-templates.md`:

- **`SCAFFOLD_ONLY=1` OR `FROM_BLUEPRINT=1`** (called by `/blueprint`) → **Variant B** (blueprint authoring step omitted; feature block renumbered 1.1 DB Design / 1.2 Test Cases / 1.3 Implementation).
- **Otherwise** (direct user invocation) → **Variant A** (full 4-step feature block: 1.1 Blueprint / 1.2 DB Design / 1.3 Test Cases / 1.4 Implementation).

Repeat the `## Feature` block per blueprint discovered above, then append the shared **At Sprint End tail** from the same reference file. Substitute `{N}`, `{sprint-name}`, `{feature-name}`, `{NNN}` placeholders.

### Step 2.5: Create Sprint Progress Tracker

Read the prompt map created in Step 2 (`docs/sprints/sprint-{N}-{sprint-name}/prompt-map.md`) and extract feature names from `## Feature {#}: {name}` headers (where `{#}` is the feature ordinal, e.g., 1, 2, 3).

Instantiate the **Progress Tracker** template from `references/sprint-doc-templates.md` into `docs/sprints/sprint-{N}-{sprint-name}/progress.md`. All features start as `-` (Not Started) in every column. Keep the `<!-- *_START -->` / `<!-- *_END -->` marker comments intact — the `track-sprint-progress.sh` hook edits between them.

### Step 3: Create Retrospective Template

Instantiate the **Retrospective** template from `references/sprint-doc-templates.md` into `docs/sprints/sprint-{N}-{sprint-name}/retrospective.md`.

### Step 3.5: Commit Sprint Scaffolding

Commit the 3 generated sprint documents (`prompt-map.md`, `progress.md`, `retrospective.md`) to the sprint branch. This keeps them separate from later feature commits and makes tracking easy at merge time.

```bash
git add "docs/sprints/sprint-${SPRINT_N}-${SPRINT_NAME}/"
git commit -m "chore: scaffold sprint ${SPRINT_N} (${SPRINT_NAME})"
```

Do not push to remote — the push is bundled with the first feature commit or with `/pr-merge`.

### Step 4: Output Sprint Planning Guide

> **Delegated-from-/blueprint mode (`FROM_BLUEPRINT=1` or `SCAFFOLD_ONLY=1`)**: `/blueprint` prints its own consolidated output (Step 7) after this skill returns. To avoid duplication, prefix this section with `(invoked from /blueprint — see consolidated output below)` and keep the body to just worktree path, branch, and port base.

```
## Sprint {N} Initialization Complete

### Worktree
- Path: {WT_PATH}
- Branch: {SPRINT_BRANCH}
- Port base: {PORT_BASE}
- env file: {WT_PATH}/.astra-worktree.env

### Generated Files (in worktree)
- docs/sprints/sprint-{N}-{sprint-name}/prompt-map.md (prompt map)
- docs/sprints/sprint-{N}-{sprint-name}/progress.md (progress tracker)
- docs/sprints/sprint-{N}-{sprint-name}/retrospective.md (retrospective template)

### Next
▶︎ Continuing in this session: /test-scenario → implementation → /test-run
   → adversarial verification (score ≥ 90 ∧ P0 == 0, max {MAX_ITER} iterations) → /pr-merge
   (stop-after-scaffold was requested via --scaffold-stop? then: run the prompt-map features in
    this same session when ready — no cd, no new session needed)
```

> **Only under `--scaffold-stop`**, additionally print the Sprint Planning Procedure (1 hour): ① 10 min AI analysis review → ② 20 min business priorities with DE + sprint goal → ③ 20 min prompt design direction per item + DSA design direction → ④ 10 min finalize sprint backlog. Then stop cleanly — and note that resuming later is just invoking the next skill *in the same session* (or `/sprint-init --resume` after a session loss).

> **Branch (v5.16+)**: `--scaffold-stop` → stop here. `--scaffold-only` → Step 4.5 early exit (caller continues). **Otherwise — including the no-flag default — continue to Step 5** with `PIPELINE_MODE=attended` (or `auto` when `--auto` was passed).

---

### Step 4.5: `--scaffold-only` early exit

If `SCAFFOLD_ONLY=1`, the calling context (typically `/blueprint`) is responsible for the remaining flow (blueprint authoring + commit + final output). Do **not** enter Step 5 even if `--auto` was somehow also passed — instead:

1. **Reject the incompatible flag combo**: if both `SCAFFOLD_ONLY=1` and `AUTO_MODE=1`, abort with `"❌ --scaffold-only and --auto cannot be combined (no blueprint exists yet to drive the auto pipeline)"`.
2. **Suppress duplicate output**: Step 4 already emitted the minimal worktree info block (`--from-blueprint` mode wording also covers `--scaffold-only`). Nothing more to print.
3. **Return cleanly** so the caller can continue.

```bash
if [ "$SCAFFOLD_ONLY" = "1" ] || [ "$FROM_BLUEPRINT" = "1" ]; then
  if [ "$SCAFFOLD_ONLY" = "1" ] && [ "$AUTO_MODE" = "1" ]; then
    echo "❌ --scaffold-only and --auto cannot be combined (no blueprint exists yet to drive the auto pipeline)" >&2
    exit 1
  fi
  # --from-blueprint (legacy alias) exits here too — both flags trip the same clean return.
  exit 0
fi
```

> **Why the guard sits between Steps 4 and 5**: Steps 1.5–3.5 (worktree, env, scaffold, commit) are exactly what a `--scaffold-only` caller wants; only the auto pipeline (Step 5+) is out of scope.

### Step 5: Pipeline Continuation (v5.16+ default; `--auto` = unattended variant)

Run the shared pipeline sequentially in this session — `PIPELINE_MODE=attended` by default, `auto` when `--auto` was passed:

```
/test-scenario all → implementation (blueprint-based) → /test-run
  → Step 5.4.5 adversarial verification gate (loop-verifier; exit = tests PASS ∧ score ≥ 90 ∧ P0 == 0)
  → (fix loop, hard cap MAX_ITER = 5 default) → /pr-merge → cleanup (back on dev)
```

The full stage-by-stage procedure lives in [references/auto-pipeline.md](references/auto-pipeline.md) (§Step 5). **Read it whenever the pipeline continues (i.e., on every run except `--scaffold-stop`/`--scaffold-only`, and on `--resume`).** It covers: pre-checks (5.0), progress init (5.1), the Silent Save Protocol (5.1.5: checkpoint yaml → commit → reference-avoidance rule → auto-advance), test-scenario (5.2), implementation (5.3), integration test with `ASTRA_TEST_RESULT` parsing (5.4), the adversarial verification gate (5.4.5), the self-improvement loop (5.5), mode-aware `/pr-merge` (5.6), and the final report (5.7).

**Flag-handling summary** (mainline): `--auto` is incompatible with `--scaffold-only` (already rejected in Step 4.5). During the pipeline `AskUserQuestion` is never called between stages; `attended` mode surfaces HITL only inside `/pr-merge` (merge confirmation, promotion target, remaining Critical issues), `auto` mode only at the promotion target + true blockers (gh auth, merge conflict).

---

## Notes

- Existing sprint files are not overwritten.
- The prompt map is filled in collaboratively by VA and PE during the Planning meeting (`--scaffold-stop` exists for exactly this ritual).
- **v5.19+ merge flow**: every sprint is a worktree sprint. After the review loop, `/pr-merge` asks one HITL ("finalize now?"), then performs the cross-worktree transition itself and removes the worktree. The user is never instructed to `cd`. If a worktree remains due to a conflict or interruption, the user resolves it and re-invokes `/pr-merge` in the same session.
- The user must not edit `.astra-worktree.env` — `/test-run` sources it automatically.
- **Pipeline caveats**:
  - Blueprints must exist before Step 5 (author them via `/blueprint`, which runs this same pipeline afterwards).
  - When a failure is classified `SPEC_GAP` / `DESIGN_MISALIGN`, abort without merging — blueprint/UX fixes require user judgment.
  - For full-stack auto-generation starting from planning, use `/autorun {feature description}` instead.
  - The Step 5.4.5 adversarial gate never merges unverified work: if the hard cap (default 5) is reached with `score < 90` or `P0 > 0`, the pipeline stops at the report and leaves the branch/worktree intact for manual follow-up.
