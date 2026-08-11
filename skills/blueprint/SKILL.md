---
name: blueprint
description: "Authors a Blueprint (design document) with 10 standard sections — data flow, schema, API contract, sequences, pseudocode logic, HITL Triggers — implementation code excluded, then (v5.16+) continues in the same session through implementation, the adversarial test loop, and /pr-merge. v5.19+ order: the blueprint is authored, reviewed (blueprint-reviewer), committed, and pushed on dev in the MAIN worktree first; only then is the sprint worktree (.worktrees/sprint-<N>-<slug>/, branched from origin/dev) created via /sprint-init --scaffold-only, and all sprint work runs inside it. Planner deliverables (docs/planner/) are auto-loaded; only 1–3 core design decisions are asked via HITL. --design-only stops after the dev push (no worktree). Use when designing a feature before implementation or updating an existing blueprint."
argument-hint: "[feature-slug-or-blueprint-path] [--auto] [--from-planner=<planner-dir>] [--design-only]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Skill, Task, Agent, TodoWrite
---

# Blueprint Skill — Blueprint-on-dev, Sprint-in-worktree (v5.19+)

> **Korean output style**: for Korean user-facing text (HITL questions, status reports, answers), apply `$CLAUDE_PLUGIN_ROOT/docs/development/korean-style.md` — §"HITL 질문 작성 규칙" and §"답변·보고 원칙". Korean files written to disk are style-checked automatically by the korean-style PostToolUse hook.

Taking the planning deliverables produced by `/service-planner` (or a direct user description) as input, this skill **authors a blueprint on the `dev` branch in the main worktree** focused on **data flow · schema definition · logic design** at `docs/blueprints/{NNN}-{feature-slug}/blueprint.md`, **commits and pushes it to `dev`**, then **creates the sprint worktree** (`.worktrees/sprint-<N>-<slug>/`, branched from `origin/dev` so it already contains the blueprint) — and continues in the same session through implementation, the adversarial test loop, and `/pr-merge`, **all inside the worktree**. The blueprint is the only sprint-lifecycle artifact ever written in the main worktree.

## Design Philosophy

This skill defines the blueprint as "**the design agreement immediately before implementation**". Implementation code is written by `/feature-dev` (or `/generate-entity`) after reading the blueprint. Writing code at the blueprint stage causes (a) the implementation step to easily ignore the blueprint, (b) design intent to be obscured by code details, and (c) reviewers to fall into "code review" mode and miss the data model and contracts.

**v5.19+ order**: blueprint first, on `dev` in the main worktree (author → review → commit → **push**), then the sprint worktree is created from `origin/dev` by `/sprint-init --scaffold-only`. Sprint work (scenarios, implementation, tests, PR) never touches the main worktree. Full changelog: CLAUDE.md.

### Allowed expressions (DO)

| Category | Allowed deliverables |
|----------|---------------------|
| **Data model** | ER diagram (Mermaid), table DDL (`CREATE TABLE TB_xxx ...`), column types/constraints/indexes specified, FK relation tables |
| **Data flow** | Sequence diagrams (Mermaid `sequenceDiagram`), state diagrams (`stateDiagram-v2`), activity flow (`flowchart`) |
| **API contract** | OpenAPI-style tables (endpoint · method · request schema · response schema · error codes), JSON Schema |
| **Logic design** | Pseudocode (language-agnostic, `IF/WHILE/RETURN` keywords), decision trees, business rule tables |
| **Events/messages** | Event payload JSON Schema, queue/topic names, publisher/subscriber lists |

### Forbidden expressions (DON'T)

| Category | Reason |
|----------|--------|
| Executable function/method bodies (Java · TS · Python, etc.) | Implementation belongs to `/feature-dev` |
| Actual controller/service class definitions | Same as above |
| Code blocks with `import`/`require`/comments | Blueprint is language-neutral |
| ORM annotations (`@Entity`, `@Column`, etc.) | Schema is expressed via DDL or tables |
| Test code | This is `/test-scenario`'s area |

**Exception**: Pseudocode is allowed but must use the ` ```pseudo ` language tag in the Markdown code block. Using a real language tag (`java`, `typescript`, etc.) causes it to be misread as implementation code.

## Procedure

### Step 0: Argument parsing and mode determination

Parse from `$ARGUMENTS`:

| Token | Meaning | Example |
|-------|---------|---------|
| First positional argument | Feature slug or existing blueprint path | `user-auth`, `docs/blueprints/001-user-auth/blueprint.md` |
| `--auto` | Skip HITL (autorun-compatible). Conservative defaults applied to every decision | — |
| `--from-planner=<dir>` | Explicit planner directory. If omitted, slug-matched auto-detection under `docs/planner/` | `--from-planner=docs/planner/003-user-auth` |
| `--design-only` (v5.16+) | Stop after the blueprint is committed and pushed to `dev` (v5.19+: no worktree is created) instead of continuing into the Step 6.5 worktree creation + Step 8 pipeline | — |

Set the `AUTO_MODE` variable (0 or 1). `--auto` → `AUTO_MODE=1`. Likewise `DESIGN_ONLY`.

If no feature slug is provided, ask once via `AskUserQuestion` (with kebab-case guidance).

### Step 1: Location guards (before anything is written)

```bash
# 1.1 Load worktree helpers
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(find ~/.claude/plugins/cache -maxdepth 3 -type d -path '*/astra-methodology/*' 2>/dev/null | sort -V | tail -1)}"
if [ -z "$PLUGIN_ROOT" ] || [ ! -f "$PLUGIN_ROOT/scripts/worktree-helpers.sh" ]; then
  echo "❌ ERROR: CLAUDE_PLUGIN_ROOT not found — cannot proceed (worktree helpers required)" >&2
  exit 1
fi
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"

# 1.2 Identify current branch + worktree location
CURRENT_BRANCH=$(git branch --show-current)
CWD=$(pwd)
```

Apply guards **in this priority order**:

| Priority | Guard | Action |
|----------|-------|--------|
| 1 | Already inside a sprint worktree (`astra_is_isolated_worktree` returns 0) | **Secondary blueprint case** (mid-sprint). `PRIMARY_FLOW=0`, `WT_PATH=$(pwd)`, `SPRINT_BRANCH=$(git branch --show-current)`. The blueprint is authored *here* and committed to the existing sprint branch in Step 6 — it merges via the sprint PR. Steps 6.5/8 are skipped. |
| 2 | Main worktree, current branch is **not** `dev` / `main` / `master` | **Abort with error**. Print the message below and exit 1. (A main worktree on `feat/sprint-*` is a pre-v5.19 in-place leftover — finish it with `/pr-merge` or `git checkout dev` first.) |
| 3 | Otherwise (dev/main/master in the main worktree) | **Primary flow**: `PRIMARY_FLOW=1`, `BASE_BRANCH="$CURRENT_BRANCH"` (normally `dev`). The blueprint is authored right here in the main worktree, committed + pushed to `$BASE_BRANCH` (Step 6), and only then is the sprint worktree created (Step 6.5). |

**Priority 2 abort message**:

```
❌ ERROR: /blueprint requires the dev/main/master branch on the main worktree.
   Current branch: $CURRENT_BRANCH
   Current cwd:    $CWD

   v5.19+ flow: the blueprint is authored and pushed on dev in the main
   worktree, and the sprint worktree is then branched from origin/dev.
   Authoring on an arbitrary branch would push design docs to the wrong
   branch and mis-base the sprint worktree.

   Fix:
     1. Stash or commit any local changes on '$CURRENT_BRANCH'
     2. git checkout dev    (or: git checkout main)
     3. /blueprint $FEATURE_SLUG ${FROM_PLANNER:+--from-planner=$FROM_PLANNER} ${AUTO_MODE:+--auto}
```

> **Why no fallback**: error-on-non-standard-branch keeps behavior consistent — every successful primary `/blueprint` invocation guarantees the blueprint reached `dev` and the sprint worktree was branched from it.

### Step 1.5: Determine blueprint directory number + load planner deliverables

> **Primary flow runs this in the main worktree**: The blueprint directory number (`001`, `002`, ...) must be globally unique across all sprints, and `docs/blueprints/` on the main worktree (dev branch) is the authoritative source. In the secondary case (Priority 1), scan the same path inside the worktree — it inherited dev's numbering at branch time.

```bash
# 1.5.1 Determine blueprint directory number (3-digit zero-padded)
# (find, not `ls glob` — an unmatched glob in zsh errors before 2>/dev/null can suppress it)
NEXT_NUM=$(find docs/blueprints -maxdepth 1 -type d -name '[0-9][0-9][0-9]-*' 2>/dev/null | \
  awk -F'[/-]' '{print $3}' | sort -n | tail -1)
NEXT_NUM=$((${NEXT_NUM:-0} + 1))
printf -v NUM "%03d" "$NEXT_NUM"
BLUEPRINT_DIR_REL="docs/blueprints/${NUM}-${FEATURE_SLUG}"
BLUEPRINT_DIR="$(pwd)/${BLUEPRINT_DIR_REL}"
BLUEPRINT_PATH="${BLUEPRINT_DIR}/blueprint.md"
mkdir -p "$BLUEPRINT_DIR"

# 1.5.2 Locate planner directory
if [ -n "$FROM_PLANNER" ]; then
  PLANNER_DIR="$FROM_PLANNER"
else
  PLANNER_DIR=$(find docs/planner -maxdepth 1 -type d -name "[0-9][0-9][0-9]-${FEATURE_SLUG}" 2>/dev/null | sort | head -1)
fi
```

**If planner deliverables exist, read all 6**:
- `market-analysis.md` — market analysis (input for the Background section)
- `interview-report.md` — persona interviews (input for user scenarios)
- `requirements-definition.md` — KPI/OKR, functional/non-functional requirements (input for performance/security sections)
- `usecase-definition.md` — use cases / journey maps (input for sequence diagrams)
- `ia-screen-design.md` — IA / screens (input for API spec — API calls per screen)
- `feature-definition.md` — story map · risks (input for test strategy)

**If planner deliverables are missing**, proceed from user description alone. In that case, leave a "❓ Additional information needed" marker for ambiguous sections.

### Step 2: Auto-draft the 10 standard sections

Write to `BLUEPRINT_PATH` using the reference skeleton. Each section is derived from planner deliverables automatically; portions that cannot be derived are filled with conservative defaults.

> **Shell variables do NOT persist across separate `Bash` tool calls.** `BASE_BRANCH`, `PRIMARY_FLOW`, `BLUEPRINT_DIR`, `BLUEPRINT_DIR_REL`, `NUM`, and `FEATURE_SLUG` were set in Steps 0–1.5 but are lost the moment a new `Bash` invocation starts. Every later Bash step (2, 4, 6) that needs them MUST re-derive them at the top of its own block using the snippet below (do not assume they carry over):
>
> ```bash
> # Re-derive location + blueprint paths (safe to run in any later Bash block, both flows)
> FEATURE_SLUG="{feature-slug}"   # known from Step 0 arguments
> ROOT=$(git rev-parse --show-toplevel) || { echo "❌ ERROR: not in a git tree" >&2; exit 1; }
> if [ "$(git rev-parse --git-dir)" = "$(git rev-parse --git-common-dir)" ]; then
>   PRIMARY_FLOW=1; BASE_BRANCH=$(git branch --show-current)          # main worktree (dev/main/master)
> else
>   PRIMARY_FLOW=0; SPRINT_BRANCH=$(git branch --show-current); WT_PATH="$ROOT"   # sprint worktree (secondary)
> fi
> BLUEPRINT_DIR=$(find "$ROOT/docs/blueprints" -maxdepth 1 -type d -name "[0-9][0-9][0-9]-${FEATURE_SLUG}" 2>/dev/null | sort | head -1)
> [ -z "$BLUEPRINT_DIR" ] && { echo "❌ ERROR: cannot re-derive blueprint dir for slug '$FEATURE_SLUG'" >&2; exit 1; }
> BLUEPRINT_DIR_REL="${BLUEPRINT_DIR#"$ROOT"/}"
> BLUEPRINT_PATH="${BLUEPRINT_DIR}/blueprint.md"
> ```

> **Section 10 (HITL Triggers) authoring rule**: After Sections 1–9 of the blueprint body are written, *re-scan that body* to identify items that require decisions during implementation, and fill the 10.2 table. Items that already have a clear answer in the body are marked "auto"; items that are not specified are marked "user question required". `/feature-dev` consults this table during implementation to decide whether HITL fires.

Read `references/blueprint-skeleton.md` and instantiate all 10 sections with {feature} content. The skeleton is the authoritative template (illustrative `TB_USER` / `POST /api/users` example values — replace them). The 10 sections and their required content:

| # | Section | Required content |
|---|---------|------------------|
| 1 | Overview | Purpose · Background · Scope (in/out) · Success Metrics (KPI table) |
| 2 | Functional Spec | Actors · User Journey (Mermaid `journey`) · Business Rules table (BR-NN) |
| 3 | Data Model | ER Diagram (Mermaid `erDiagram`) · Table DDL (`TB_`/`TC_`… prefixes, `_YMD`/`_DT`… suffixes) · Index Strategy · FK Relations |
| 4 | API Contract | Endpoint List · Request/Response JSON Schemas · Error Response Codes |
| 5 | Sequence Diagrams | Happy Path + Error Path (Mermaid `sequenceDiagram`) |
| 6 | Business Logic Design | Pseudocode only — ` ```pseudo ` tag mandatory; no real language tag |
| 7 | Error Handling Policy | Per-area handling table (input / business-rule / DB / external / unexpected) |
| 8 | Non-Functional | Performance (P95, RPS, txn boundary) · Security (auth, PII, OWASP) · Availability |
| 9 | Test Strategy | Levels table (Unit/Integration/E2E) + Required test-case checklist |
| 10 | HITL Triggers | Firing principles (T1–T4) · feature-specific trigger table · question rules · anti-HITL list. **Consulted by `/feature-dev` during implementation** — see Step 2's Section-10 authoring rule above. |

Non-derivable sections get a `❓ Additional information needed` marker so blueprint-reviewer flags them P0.

### Step 3: Core-decision HITL (conditional 1–3 questions)

Among items filled with conservative defaults in the auto-draft, ask **only the decisions whose human judgment has a major cost impact** via `AskUserQuestion`. **If `AUTO_MODE=1`, skip this step and keep the defaults**.

Ask **only** those decisions, in the 3 decision areas below, **not already specified by planner deliverables or the user description** (up to 3 questions):

#### 3.1 PK strategy (always)

```
question: "Which PK strategy should the data model use? (Applies to USER_ID etc. in Section 3.2)"
header: "PK strategy"
options:
  - "auto-increment BIGINT (Recommended — standard for single-DB environments)"
    description: "MySQL/PostgreSQL IDENTITY column. Simplest and best index efficiency. Default for a single RDBMS environment."
  - "UUID v7 (time-sortable)"
    description: "Distributed / multi-region environments. Useful when ID exposure is a security concern. Index size grows to 16 bytes."
  - "Snowflake ID (Twitter)"
    description: "Thousands of inserts per second + multi-node ID issuance. Monotonic 64-bit. Requires a separate ID-issuance service."
```

#### 3.2 Transaction boundary (when DB writes > 1)

If the Step 2 pseudocode contains multiple writes (`INSERT` + event publication, etc.), ask:

```
question: "How should DB writes and event publication be grouped in the Section 6 pseudocode?"
header: "Transaction boundary"
options:
  - "Single DB transaction + Outbox pattern (Recommended)"
    description: "Events are also INSERTed into an outbox table inside the same transaction. A separate publisher dispatches them. Guarantees consistency."
  - "Single DB transaction + publish immediately after commit"
    description: "After the transaction commits, publish inside a try/catch. Simpler to implement but messages may be lost on publish failure."
  - "Two-phase commit (XA)"
    description: "Both DB and message broker must support XA. Heavy performance overhead. Use when strong consistency is required (e.g., finance)."
```

#### 3.3 External-dependency call (when external system in sequence diagram)

If Section 5 contains an external API/service, ask:

```
question: "Should the external system ({system name}) be called synchronously or asynchronously?"
header: "External-call sync mode"
options:
  - "Synchronous call + Circuit Breaker (Recommended)"
    description: "The external response is on the user-facing latency path. On external failure, the circuit opens and falls back. Simple, with immediate consistency."
  - "Asynchronous message (event publication)"
    description: "Publish a message to the external system and respond immediately. Eventual consistency. A status column is needed to track the result."
  - "Asynchronous + polling/callback"
    description: "Receive a request ID from the external system, store it → poll periodically or receive a webhook. Most complex, most robust."
```

Reflect each answer in Section 3.2 (PK), 7 (transaction policy), and 8.3 (availability), updating the blueprint via `Edit`.

### Step 4: data-standard auto-skill delegation + forbidden-word verification

For the DDL section of the blueprint (Section 3.2), the `data-standard` auto-skill and the PostToolUse hook automatically perform the following (no separate invocation required):
- Table prefix verification (`TB_`/`TC_`/`TH_`/`TL_`/`TR_`)
- Column suffix verification (`_YMD`/`_DT`/`_AMT`/`_NM`/`_CD`, etc.)
- Forbidden-word check (`금칙어목록` field in `standard_words.json`)

When a violation is found, the hook prints a warning to stderr. The skill receives the warning, reports it to the user once, and proceeds (non-blocking).

### Step 5: Invoke blueprint-reviewer

```
REVIEW_OUTPUT=$(Task(blueprint-reviewer, "Verify quality of {BLUEPRINT_PATH} — check completeness of the 10 standard sections, data-model consistency, and API-contract clarity. Additionally verify code pollution (executable language code blocks outside Section 6). Check whether the HITL Triggers table in Section 10 is empty or missing unspecified decisions. Return the response as a Markdown report containing Overall Score, P0/P1/P2 issue lists, and recommended actions."))
```

The `blueprint-reviewer` agent has `disallowedTools: Write, Edit`, so it cannot write files directly. The skill (parent context) takes the return value of the `Task()` call and writes it to `$BLUEPRINT_DIR/review.md` via the `Write` tool.

```
Write("$BLUEPRINT_DIR/review.md", REVIEW_OUTPUT)
```

**Parse the machine-parseable tail line for the branch decision.** `blueprint-reviewer` emits a final line of the exact form:

```
ASTRA_REVIEW_RESULT: score=NN verdict=PASS|FAIL p0=N
```

Branch on **that line only** — do not infer PASS/FAIL from the prose body:

```bash
Write "$BLUEPRINT_DIR/review.md" with REVIEW_OUTPUT   # (via the Write tool)
RESULT_LINE=$(printf '%s\n' "$REVIEW_OUTPUT" | grep -oE 'ASTRA_REVIEW_RESULT: score=[0-9]+ verdict=(PASS|FAIL) p0=[0-9]+' | tail -1)
if [ -z "$RESULT_LINE" ]; then
  # Tail line absent → treat as FAIL and re-invoke the reviewer ONCE. Never assume PASS.
  echo "⚠️ blueprint-reviewer emitted no ASTRA_REVIEW_RESULT line — treating as FAIL, re-invoking once" >&2
  # (re-run the Task(blueprint-reviewer, ...) call above exactly once; if the second run also
  #  lacks the tail line, record verdict=FAIL p0=unknown in review.md and surface it to the user)
  REVIEW_VERDICT="FAIL"; REVIEW_SCORE="N/A"; REVIEW_P0="unknown"
else
  REVIEW_SCORE=$(echo "$RESULT_LINE" | grep -oE 'score=[0-9]+' | cut -d= -f2)
  REVIEW_VERDICT=$(echo "$RESULT_LINE" | grep -oE 'verdict=(PASS|FAIL)' | cut -d= -f2)
  REVIEW_P0=$(echo "$RESULT_LINE" | grep -oE 'p0=[0-9]+' | cut -d= -f2)
fi
```

After `review.md` is written, summarize the P0 issues to the user. `REVIEW_SCORE` / `REVIEW_VERDICT` / `REVIEW_P0` (re-derived the same way in Step 6 if the shell context reset) drive the commit message and the P0 report.

### Step 6: Commit the blueprint to `dev` and push (primary flow)

> **v5.19+**: the blueprint is the *only* sprint artifact committed on `dev` in the main worktree. Pushing it before worktree creation means the sprint worktree (branched from `origin/dev` in Step 6.5) contains the blueprint from birth — no cross-branch carry-over.

```bash
# 6.1 Re-derive BASE_BRANCH/BLUEPRINT_DIR_REL (shell vars do not persist — see Step 2 snippet).
#     <run the re-derivation snippet from Step 2 here>

# 6.2 Extract the blueprint-reviewer score from the ASTRA_REVIEW_RESULT tail line (fallback: N/A)
REVIEW_SCORE=$(grep -oE 'ASTRA_REVIEW_RESULT: score=[0-9]+' "$BLUEPRINT_DIR/review.md" 2>/dev/null | grep -oE '[0-9]+' | tail -1 || echo "N/A")
: "${REVIEW_SCORE:=N/A}"
```

**Commit handling**:

- **`AUTO_MODE=1` (called by autorun)**: commit + push automatically without asking.
- **Manual mode**: show changed files via `git status -- "$BLUEPRINT_DIR_REL/"` and ask once via `AskUserQuestion`:
  - Question: "Commit the blueprint you just authored to `$BASE_BRANCH` and push it to origin now? (the sprint worktree will branch from it)"
  - Option 1: "Yes, commit & push now (Recommended)" — auto commit + push
  - Option 2: "No, I will commit it myself" — skip; show the commands (`git add docs/blueprints/{NNN}-... && git commit -m "..." && git push origin dev`) and **stop here** (Steps 6.5/8 need the blueprint on origin).

```bash
# 6.3 Execute the commit — verify exit code, then machine-check the file is actually committed.
git add "$BLUEPRINT_DIR_REL"
if ! git commit -m "docs(blueprint): scaffold ${BLUEPRINT_DIR_REL##*/} blueprint

- 10 standard sections (data flow / schema / API / sequence / pseudo / HITL Triggers)
- Generated by /blueprint skill v3 (blueprint-on-dev, v5.19+)
- Reviewed by blueprint-reviewer (score: ${REVIEW_SCORE}/100, verdict: ${REVIEW_VERDICT:-unknown})
"; then
  echo "❌ ERROR: git commit failed (exit $?) — blueprint NOT committed. Resolve and retry; do not declare success." >&2
  exit 1
fi

# 6.4 Machine verification: the blueprint file must appear in the branch history.
if [ -z "$(git log -1 --oneline -- "$BLUEPRINT_DIR_REL/blueprint.md" 2>/dev/null)" ]; then
  echo "❌ ERROR: blueprint.md is not present in the last commit on $BASE_BRANCH — commit verification failed." >&2
  echo "   Check: git status, git log --oneline -5. Do not report the blueprint as committed." >&2
  exit 1
fi
COMMIT_SHA=$(git rev-parse --short HEAD)

# 6.5-pre Push to origin — the worktree base is origin/$BASE_BRANCH, so an unpushed
# commit would be invisible to Step 6.5. Verify the remote actually advanced.
git push origin "$BASE_BRANCH" || { echo "❌ ERROR: git push origin $BASE_BRANCH failed — resolve (pull --rebase?) and retry." >&2; exit 1; }
if [ "$(git rev-parse HEAD)" != "$(git ls-remote origin "refs/heads/$BASE_BRANCH" | cut -f1)" ]; then
  echo "❌ ERROR: origin/$BASE_BRANCH does not match local HEAD after push — do not proceed to worktree creation." >&2
  exit 1
fi
echo "✅ Blueprint committed ($COMMIT_SHA) and pushed to origin/$BASE_BRANCH — verified."
```

> **Only declare Step 6 success after the git log AND push checks pass** (research: mid-tier models overclaim completion — completion claim ≠ evidence). If the commit exit code is non-zero, `git log -1 -- blueprint.md` is empty, or the remote head does not match, the step failed regardless of what the shell printed.

> **Secondary-blueprint case (`PRIMARY_FLOW=0`)**: commit on the existing sprint branch instead (message trailer `Sprint branch: ${SPRINT_BRANCH}`), **no push** — `/pr-merge` pushes the sprint branch at sprint end. This is the prompt-map Step 1.1 flow; skip Step 6.5 and Step 8.

### Step 6.5: Create the sprint worktree (primary flow only; skipped under `--design-only`)

The blueprint now exists on `origin/${BASE_BRANCH}`. Delegate to `/sprint-init --scaffold-only` to create the sprint worktree at `.worktrees/sprint-<N>-<slug>/` (branched from `origin/dev` — it contains the blueprint), write `.astra-worktree.env`, and scaffold prompt-map / progress / retrospective. The `--scaffold-only` flag tells `/sprint-init` the blueprint **already exists on dev** — the prompt-map omits the blueprint-authoring step (Variant B), and the pipeline is not entered (this skill drives it in Step 8).

```bash
# 6.5.1 Delegate to /sprint-init — pass slug + --scaffold-only
echo "🌿 Creating sprint worktree for '${FEATURE_SLUG}' (delegating to /sprint-init --scaffold-only)..."
Skill('sprint-init', "${FEATURE_SLUG} --scaffold-only")
```

After the `Skill()` call returns, the parent context's cwd is still the main worktree (skill-to-skill cd does not propagate). Discover the resolved worktree path by querying git directly:

```bash
# 6.5.2 Discover the worktree path that /sprint-init created (slug-prefix match)
WT_PATH=$(git worktree list --porcelain 2>/dev/null | awk -v slug="${FEATURE_SLUG}" '
  /^worktree / { p=$2 }
  /^branch refs\/heads\// {
    b=$2; sub("refs/heads/", "", b)
    if (b ~ "^feat/sprint-[0-9]+-" slug "(-[0-9]+)?$") { print p; exit }
  }
')
if [ -z "$WT_PATH" ]; then
  # Fallback: glob both bare and collision-suffixed dirs, pick most recent
  WT_PATH=$(find .worktrees -maxdepth 1 -type d \( -name "sprint-*-${FEATURE_SLUG}" -o -name "sprint-*-${FEATURE_SLUG}-[0-9]*" \) 2>/dev/null | sort | tail -1)
fi
if [ -z "$WT_PATH" ] || [ ! -d "$WT_PATH" ]; then
  echo "❌ ERROR: /sprint-init returned but the worktree was not found" >&2
  exit 1
fi

# 6.5.3 Derive SPRINT_BRANCH and PORT_BASE from the resolved worktree
SPRINT_BRANCH=$(git -C "$WT_PATH" branch --show-current 2>/dev/null)
if [ -f "$WT_PATH/.astra-worktree.env" ]; then
  PORT_BASE=$(grep -E '^ASTRA_PORT_BASE=' "$WT_PATH/.astra-worktree.env" | cut -d= -f2)
fi

# 6.5.4 Sanity check: the worktree base must contain the blueprint (it was pushed in Step 6)
if [ ! -f "$WT_PATH/$BLUEPRINT_DIR_REL/blueprint.md" ]; then
  echo "❌ ERROR: worktree $WT_PATH does not contain $BLUEPRINT_DIR_REL/blueprint.md — was the dev push skipped?" >&2
  exit 1
fi

# 6.5.5 Move into the sprint worktree — from here on, ALL sprint work happens inside it
cd "$WT_PATH"
```

> **Why this `cd` is safe here (unlike skill-to-skill propagation)**: This is a `Bash` invocation *within the same skill execution*. Subsequent `Bash` commands in this skill execute relative to `$WT_PATH`. The `Read`/`Write` tools use absolute paths anyway. **The user is never instructed to `cd`** — Step 8 continues the pipeline in this same session, re-anchoring with `cd "$WT_PATH"` itself wherever needed. The main worktree stays on `dev`, clean, for the whole sprint.

### Step 7: Output

Output format branches on the flow decided in Step 1.

#### Case A: Primary flow (`PRIMARY_FLOW=1`) — default path

```
✅ Blueprint authored on {BASE_BRANCH} and pushed (v5.19+ flow)

📄 Blueprint: docs/blueprints/{NNN}-{slug}/blueprint.md
📋 Review:    docs/blueprints/{NNN}-{slug}/review.md ({score}/100)
📦 Commit:    {commit SHA} on {BASE_BRANCH} (pushed to origin)

🌿 Sprint worktree (created after the push — all sprint work happens here):
   Path:      {WT_PATH}   (.worktrees/sprint-{N}-{slug}/)
   Branch:    {SPRINT_BRANCH}
   Port base: {PORT_BASE}
   env file:  {WT_PATH}/.astra-worktree.env

⚠️ P0 issues ({count}):
  - {summary}

▶︎ Continuing in this session (one-flow, inside the worktree):
   /test-scenario → implementation → /test-run
   → adversarial verification (score ≥ 90 ∧ P0 == 0, max 5 iterations) → /pr-merge
```

Then branch:

- **`--design-only`** → Step 6.5 was skipped: the blueprint is on `origin/dev`, no worktree exists, and the main worktree is clean on `dev`. Print one closing line and stop: `Design-only mode — start the sprint anytime with /sprint-init {FEATURE_SLUG} (it creates the worktree from origin/dev and runs the pipeline).` Omit the "Sprint worktree" block from the output above.
- **`--auto`** → **return to the caller** (`/autorun` drives the downstream stages itself; do not run Step 8). The worktree from Step 6.5 is already in place.
- **Otherwise (default)** → proceed to **Step 8** immediately. No exit, no user input, no `cd` instruction.

#### Case B: Already inside a sprint worktree (`PRIMARY_FLOW=0`, secondary blueprint)

```
✅ Blueprint authoring complete (secondary blueprint — existing worktree reused)

🌿 Existing sprint worktree:
   Path:      {WT_PATH}
   Branch:    {SPRINT_BRANCH}

📄 Blueprint: {BLUEPRINT_PATH}
📋 Review:    {BLUEPRINT_DIR}/review.md ({score}/100)
📦 Commit:    {commit SHA} on {SPRINT_BRANCH}

🎯 Next steps (same session — the sprint's own flow is already in progress):
  /feature-dev "Implement {BLUEPRINT_DIR_REL}/blueprint.md. Comply with Section 10 HITL Triggers."
  /test-scenario {feature-slug}
  /test-run

⚠️ P0 issues ({count}):
  - {summary}
```

> Case B does **not** auto-continue into Step 8 — a secondary blueprint lands mid-sprint, and the sprint's pipeline (or the user's manual flow) is already driving; kicking off a second pipeline would double-run test-scenario/test-run.

### Step 8: Pipeline continuation (default path only)

The sprint worktree, scaffolding, and blueprint all exist; the session context is warm. Continue exactly as `/sprint-init` would:

1. `cd "$WT_PATH"` (re-anchor inside the sprint worktree).
2. Read `skills/sprint-init/references/auto-pipeline.md` (§Step 5) and execute **Steps 5.0 → 5.7** with `PIPELINE_MODE=attended` and `MAX_ITER` = 5 unless `--max-iter=N` was passed. Every stage runs inside the worktree.
3. The pipeline ends with `/pr-merge` (HITL: merge confirmation + promotion target) and leaves the session in the main worktree on `dev`, with the sprint worktree removed.

> **Why continuation lives here**: the blueprint stage is when planner deliverables, schema, and API design are hottest in context — re-entering from a fresh session would re-read all of it at full price. One warm KV-cache prefix carries design straight through implementation and verification.

> **`/autorun` note**: under autorun, this Step 8 never runs (`--auto` returns to the caller at Step 7) — Stage 3 (blueprint) pushes the blueprint to dev and creates the sprint worktree, Stage 4 (`/sprint-init` re-entry) is an idempotent no-op guard, and autorun drives the downstream stages itself (inside the worktree).

## FAQ

**Q. Why is the blueprint authored on dev in the main worktree (v5.19+)?**
The blueprint is a *design agreement*, not sprint code — pushing it to `dev` first makes it visible to every session and every future sprint immediately, and the sprint worktree (branched from `origin/dev` after the push) contains it from birth. Everything after the push — scenarios, implementation, tests, the PR — happens exclusively inside `.worktrees/sprint-<N>-<slug>/`, so the main worktree is never dirtied by sprint work.

**Q. What happens if `/sprint-init --scaffold-only` fails midway?**
`/sprint-init` aborts with a non-zero exit. `/blueprint` reports the failure and stops. The blueprint itself is safe — it is already committed and pushed on `dev` (Step 6 ran first), so recovery is simply `/sprint-init {slug}` once the cause is fixed. A partial worktree (if any) is left in `git worktree list` for the user to remove manually with `git worktree remove <path>`.

**Q. Isn't pseudocode also code?**
Pseudocode is a design tool that expresses algorithmic intent in a language-neutral form. It is not executable, hence not "implementation". The ` ```pseudo ` language tag is mandated because, without it, an LLM may misread it as real code.

**Q. Why are ORM annotations forbidden?**
`@Entity`, `@Column`, etc. are framework-specific (JPA/Hibernate). The blueprint is sufficient with DDL + tables, and annotation translation is `/generate-entity`'s job. Writing annotations at the blueprint stage (a) is wasted when porting to a non-JVM project, and (b) creates inconsistencies between translated DDL and annotations.

**Q. What about a brand-new feature without planner deliverables?**
In Step 2, create the empty skeleton and fill it from the user description alone. Sections that cannot be derived (e.g., 1.4 KPI) leave the marker `❓ Additional information needed — planner deliverables or user input required`, so that blueprint-reviewer flags them as P0.

**Q. How do I update an existing blueprint?**
Pass an existing path (`docs/blueprints/003-user-auth/blueprint.md`) as the first argument. The skill detects the path form (vs. a slug) and skips number allocation (Step 1.5.1) and worktree creation (Step 6.5) — it edits the file where it lives: if a sprint worktree currently owns this blueprint's sprint (resolved via `git worktree list`), edit and commit there (sprint-branch commit, no push); otherwise edit on `dev` in the main worktree, re-run the reviewer in Step 5, and commit + push per Step 6.
