---
name: blueprint
description: "Authors a Blueprint (design document) for a feature. v5.10+ runs in a worktree-first order: (1) determine slug + blueprint directory number on the main worktree, (2) auto-create the sprint worktree by delegating to /sprint-init --scaffold-only, (3) cd into that worktree, (4) author the blueprint inside the worktree (10 standard sections — data flow, schema, API contract, sequence, pseudocode logic, HITL Triggers — implementation code excluded), (5) blueprint-reviewer verifies quality, (6) commit to the sprint branch. If /service-planner deliverables (docs/planner/{NNN}-{slug}/) exist, they are auto-loaded. Only 1–3 core decisions that genuinely require human judgment (PK strategy, transaction boundary, sync/async for external dependencies) are asked via AskUserQuestion. Section 10 (HITL Triggers) is consulted by /feature-dev during implementation so the user is only asked on essential decisions. Already inside a sprint worktree → worktree creation skipped (secondary blueprint case). On non-standard branch (not dev/main/master) → error with checkout guidance."
argument-hint: "[feature-slug-or-blueprint-path] [--auto] [--from-planner=<planner-dir>]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Skill, Task, TodoWrite
---

# Blueprint Skill — Worktree-First Blueprint Authoring (v5.10+)

Taking the planning deliverables produced by `/service-planner` (or a direct user description) as input, this skill **first creates a sprint worktree, then authors a blueprint inside that worktree** focused on **data flow · schema definition · logic design** at `docs/blueprints/{NNN}-{feature-slug}/blueprint.md`.

## Design Philosophy

This skill defines the blueprint as "**the design agreement immediately before implementation**". Implementation code is written by `/feature-dev` (or `/generate-entity`) after reading the blueprint. Writing code at the blueprint stage causes (a) the implementation step to easily ignore the blueprint, (b) design intent to be obscured by code details, and (c) reviewers to fall into "code review" mode and miss the data model and contracts.

**v5.10+ order change**: The previous workflow authored the blueprint on dev (main worktree) and *then* created the sprint worktree. v5.10+ reverses this — the worktree is created first so that the blueprint commit naturally lands on the sprint branch. This removes the "dev visibility guarantee" complexity of v5.8/5.9 and gives every sprint a clean self-contained branch from the very first commit.

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

Set the `AUTO_MODE` variable (0 or 1). `--auto` → `AUTO_MODE=1`.

If no feature slug is provided, ask once via `AskUserQuestion` (with kebab-case guidance).

### Step 1: Determine blueprint directory number + load planner deliverables (on the main worktree)

> **Why this stays on the main worktree**: The blueprint directory number (`001`, `002`, ...) must be globally unique across all sprints. Scanning `docs/blueprints/` on the *main worktree* (dev branch) is the authoritative source. Once the number is reserved, we hand off to `/sprint-init` to create the worktree, and then *cd into the worktree* before any file is written.

```bash
# 1.1 Determine blueprint directory number (3-digit zero-padded) — scan main worktree
NEXT_NUM=$(ls -d docs/blueprints/[0-9][0-9][0-9]-* 2>/dev/null | \
  awk -F'[/-]' '{print $3}' | sort -n | tail -1)
NEXT_NUM=$((${NEXT_NUM:-0} + 1))
printf -v NUM "%03d" "$NEXT_NUM"
BLUEPRINT_DIR_REL="docs/blueprints/${NUM}-${FEATURE_SLUG}"

# 1.2 Locate planner directory
if [ -n "$FROM_PLANNER" ]; then
  PLANNER_DIR="$FROM_PLANNER"
else
  PLANNER_DIR=$(ls -d docs/planner/[0-9][0-9][0-9]-${FEATURE_SLUG} 2>/dev/null | head -1)
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

### Step 1.5: Location guards (decide whether to create the worktree)

```bash
# 1.5.1 Load worktree helpers
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
if [ -z "$PLUGIN_ROOT" ] || [ ! -f "$PLUGIN_ROOT/scripts/worktree-helpers.sh" ]; then
  echo "❌ ERROR: CLAUDE_PLUGIN_ROOT not found — cannot proceed (worktree helpers required)" >&2
  exit 1
fi
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"

# 1.5.2 Identify current branch + worktree location
CURRENT_BRANCH=$(git branch --show-current)
CWD=$(pwd)
```

Apply guards **in this priority order**:

| Priority | Guard | Action |
|----------|-------|--------|
| 1 | Already inside a sprint worktree (`astra_is_isolated_worktree` returns 0) | **Skip Step 1.6/1.7** (secondary blueprint case). `WORKTREE_CREATED=0`, `WORKTREE_SKIP_REASON="already in sprint worktree"`. The blueprint commit will land on the existing sprint branch in Step 6. |
| 2 | Current branch is **not** `dev` / `main` / `master` | **Abort with error** (per user decision). Print the message below and exit 1. |
| 3 | Otherwise (dev/main/master in the main worktree) | **Proceed to Step 1.6** to create the sprint worktree. |

**Priority 2 abort message**:

```
❌ ERROR: /blueprint requires the dev/main/master branch on the main worktree.
   Current branch: $CURRENT_BRANCH
   Current cwd:    $CWD

   /blueprint creates a sprint worktree as its first step, and that worktree
   must branch from dev (or main/master as fallback). Authoring a blueprint
   on an arbitrary branch leads to a worktree whose base is unintended.

   Fix:
     1. Stash or commit any local changes on '$CURRENT_BRANCH'
     2. git checkout dev    (or: git checkout main)
     3. /blueprint $FEATURE_SLUG ${FROM_PLANNER:+--from-planner=$FROM_PLANNER} ${AUTO_MODE:+--auto}
```

> **Why no fallback to "main-worktree-only blueprint"**: The user explicitly chose error-on-non-standard-branch over a partial fallback so behavior stays consistent — every successful `/blueprint` invocation guarantees a sprint worktree exists or is reused.

### Step 1.6: Create the sprint worktree (priority-3 branches only)

Delegate to `/sprint-init --scaffold-only` to create the worktree, write `.astra-worktree.env`, and scaffold prompt-map / progress / retrospective. The `--scaffold-only` flag (v5.10+) tells `/sprint-init` that **the blueprint does not exist yet** — so Step 5.0 Pre-checks (which validate blueprint presence under `--auto`) and Step 2's prompt-map Feature 1.1 (blueprint authoring) are suppressed.

```bash
# 1.6.1 Delegate to /sprint-init — pass slug + --scaffold-only
echo "🌿 Creating sprint worktree for '${FEATURE_SLUG}' (delegating to /sprint-init --scaffold-only)..."
Skill('sprint-init', "${FEATURE_SLUG} --scaffold-only")
WORKTREE_CREATED=1
```

After the `Skill()` call returns, the parent context's cwd is still the main worktree (skill-to-skill cd does not propagate). Discover the resolved worktree path by querying git directly:

```bash
# 1.6.2 Discover the worktree path that /sprint-init created (slug-prefix match)
WT_PATH=$(git worktree list --porcelain 2>/dev/null | awk -v slug="${FEATURE_SLUG}" '
  /^worktree / { p=$2 }
  /^branch refs\/heads\// {
    b=$2; sub("refs/heads/", "", b)
    if (b ~ "^feat/sprint-[0-9]+-" slug "(-[0-9]+)?$") { print p; exit }
  }
')
if [ -z "$WT_PATH" ]; then
  # Fallback: glob both bare and collision-suffixed dirs, pick most recent
  WT_PATH=$(ls -td .astra-worktrees/sprint-*-${FEATURE_SLUG} .astra-worktrees/sprint-*-${FEATURE_SLUG}-* 2>/dev/null | head -1)
fi
if [ -z "$WT_PATH" ] || [ ! -d "$WT_PATH" ]; then
  echo "❌ ERROR: /sprint-init returned but the worktree was not found" >&2
  exit 1
fi

# 1.6.3 Derive SPRINT_BRANCH and PORT_BASE from the resolved worktree
SPRINT_BRANCH=$(git -C "$WT_PATH" branch --show-current 2>/dev/null)
if [ -f "$WT_PATH/.astra-worktree.env" ]; then
  PORT_BASE=$(grep -E '^ASTRA_PORT_BASE=' "$WT_PATH/.astra-worktree.env" | cut -d= -f2)
fi
```

### Step 1.7: Move into the sprint worktree (within this skill execution)

```bash
cd "$WT_PATH"
```

> **Why this `cd` is safe here (unlike skill-to-skill propagation)**: This is a `Bash` invocation *within the same skill execution*. Subsequent `Bash` commands in this skill execute relative to `$WT_PATH`. The `Read`/`Write` tools use absolute paths anyway, so this is purely for shell-relative commands (git, ls, etc.). When the skill returns, the parent context's cwd reverts to the main worktree — this is fine; Step 7 explicitly instructs the user to `cd $WT_PATH` to start subsequent commands.

From this point on, every file written to `docs/blueprints/{NNN}-{slug}/` lands **inside the worktree**, and every git operation acts on the **sprint branch** (`feat/sprint-N-slug`).

```bash
# 1.7.1 Build the absolute blueprint path inside the worktree
BLUEPRINT_DIR="${WT_PATH}/${BLUEPRINT_DIR_REL}"
BLUEPRINT_PATH="${BLUEPRINT_DIR}/blueprint.md"
mkdir -p "$BLUEPRINT_DIR"
```

> **Secondary-blueprint path (Priority 1 from Step 1.5)**: When `WORKTREE_CREATED=0`, `WT_PATH=$(pwd)` and `SPRINT_BRANCH=$(git branch --show-current)` are derived directly from the current location, and the rest of the flow runs unchanged.

### Step 2: Auto-draft the 10 standard sections

Write to `BLUEPRINT_PATH` using the skeleton below. Each section is derived from planner deliverables automatically; portions that cannot be derived are filled with conservative defaults.

> **Section 10 (HITL Triggers) authoring rule**: After Sections 1–9 of the blueprint body are written, *re-scan that body* to identify items that require decisions during implementation, and fill the 10.2 table. Items that already have a clear answer in the body are marked "auto"; items that are not specified are marked "user question required". `/feature-dev` consults this table during implementation to decide whether HITL fires.

#### Blueprint skeleton

```markdown
# Blueprint: {feature name}

> **Generated by**: `/blueprint` skill v2 (worktree-first)
> **Planner Source**: {PLANNER_DIR or "direct input"}
> **Sprint Branch**: {SPRINT_BRANCH}
> **Status**: Draft (awaiting blueprint-reviewer verification)

## 1. Overview

### 1.1 Purpose
{the user/business problem this feature solves — pain point from interview-report.md}

### 1.2 Background
{why this feature is needed now — market signal from market-analysis.md}

### 1.3 Scope
- **In Scope**:
  - {story map items from feature-definition.md}
- **Out of Scope**:
  - {items explicitly split out to a later sprint or a separate feature}

### 1.4 Success Metrics (KPI)
| Metric | Target | Measurement |
|--------|--------|-------------|
| {KPI from requirements-definition.md} | {target value} | {measurement method} |

## 2. Functional Spec

### 2.1 Actors
{actors from usecase-definition.md — user types, systems, external systems}

### 2.2 User Scenario (Mermaid User Journey)

\`\`\`mermaid
journey
    title {feature name}
    section {stage}
      {action}: {satisfaction}: {actor}
\`\`\`

### 2.3 Business Rules
| ID | Rule | Source |
|----|------|--------|
| BR-01 | {e.g., "duplicate sign-up by the same email is not allowed"} | {requirements-definition.md item number} |

## 3. Data Model

### 3.1 ER Diagram

\`\`\`mermaid
erDiagram
    TB_USER ||--o{ TB_USER_AUTH : has
    TB_USER {
        bigint USER_ID PK
        varchar USER_NM
        varchar EMAIL_ADDR UK
        char USE_YN
        datetime REG_DT
    }
\`\`\`

### 3.2 Table Definitions (DDL)

> **Korean public data standard**: every table follows the `TB_`/`TC_`/`TH_`/`TL_`/`TR_` prefix and every column follows the `_YMD`/`_DT`/`_AMT`/`_NM`/`_CD`/`_NO`/`_CN`/`_YN`/`_SN`/`_ADDR` suffix rules. The `data-standard` auto-skill validates this at Write time.

\`\`\`sql
-- TB_USER: user master
CREATE TABLE TB_USER (
  USER_ID     BIGINT       NOT NULL AUTO_INCREMENT COMMENT 'User ID',
  USER_NM     VARCHAR(50)  NOT NULL COMMENT 'User name',
  EMAIL_ADDR  VARCHAR(255) NOT NULL COMMENT 'Email address',
  USE_YN      CHAR(1)      NOT NULL DEFAULT 'Y' COMMENT 'Use flag',
  REG_DT      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Registration datetime',
  PRIMARY KEY (USER_ID),
  UNIQUE KEY UK_USER_EMAIL (EMAIL_ADDR)
);
\`\`\`

### 3.3 Index Strategy
| Index | Columns | Purpose |
|-------|---------|---------|
| `UK_USER_EMAIL` | `EMAIL_ADDR` | Login lookup (O(log N)) |

### 3.4 FK Relations
| Child table.column | Parent table.column | ON DELETE | ON UPDATE |
|---------------------|---------------------|-----------|-----------|
| `TB_USER_AUTH.USER_ID` | `TB_USER.USER_ID` | CASCADE | RESTRICT |

## 4. API Contract

### 4.1 Endpoint List
| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| POST | `/api/users` | Register a user | none |
| GET | `/api/users/{id}` | Look up a user | Bearer |

### 4.2 Request/Response Schemas

**POST /api/users**

Request (JSON Schema):
\`\`\`json
{
  "type": "object",
  "required": ["userName", "emailAddress"],
  "properties": {
    "userName": {"type": "string", "minLength": 1, "maxLength": 50},
    "emailAddress": {"type": "string", "format": "email"}
  }
}
\`\`\`

Response 200:
\`\`\`json
{
  "userId": 1,
  "userName": "John Doe",
  "emailAddress": "john@example.com",
  "registeredAt": "2026-05-20T12:34:56Z"
}
\`\`\`

### 4.3 Error Response Codes
| HTTP | code | message | Trigger |
|------|------|---------|---------|
| 400 | `INVALID_EMAIL` | Invalid email format | RFC 5322 not satisfied |
| 409 | `DUPLICATE_EMAIL` | Email already registered | UK violation |

## 5. Sequence Diagrams

### 5.1 Happy Path

\`\`\`mermaid
sequenceDiagram
    actor User
    participant API
    participant Service
    participant DB

    User->>API: POST /api/users {userName, emailAddress}
    API->>Service: registerUser(dto)
    Service->>DB: SELECT 1 FROM TB_USER WHERE EMAIL_ADDR = ?
    DB-->>Service: none
    Service->>DB: INSERT INTO TB_USER
    DB-->>Service: USER_ID
    Service-->>API: UserResponse
    API-->>User: 200 OK
\`\`\`

### 5.2 Error Path (Duplicate Email)

\`\`\`mermaid
sequenceDiagram
    actor User
    participant API
    participant Service
    participant DB

    User->>API: POST /api/users
    API->>Service: registerUser(dto)
    Service->>DB: SELECT 1 FROM TB_USER WHERE EMAIL_ADDR = ?
    DB-->>Service: exists
    Service-->>API: throw DuplicateEmailException
    API-->>User: 409 {code: DUPLICATE_EMAIL}
\`\`\`

## 6. Business Logic Design

> **Notation**: pseudocode (language-agnostic). Executable code is not written here.

### 6.1 Core logic: register user

\`\`\`pseudo
FUNCTION registerUser(userName, emailAddress):
    IF NOT isValidEmail(emailAddress):
        THROW InvalidEmailError

    IF userRepository.existsByEmail(emailAddress):
        THROW DuplicateEmailError

    user = User(userName, emailAddress, regDt=NOW())
    userRepository.save(user)
    eventBus.publish(UserRegisteredEvent(user.id))
    RETURN user
\`\`\`

### 6.2 Decision tree: authentication branching
{decision diagram if needed}

## 7. Error Handling Policy

| Area | Handling policy |
|------|-----------------|
| Input validation | 400 response at the API Gateway layer; blocked before entering transactions |
| Business-rule violation | Domain exception at the Service layer → 409/422 response |
| DB integrity violation | UK/FK violation is converted to a domain exception and handled the same way |
| External-dependency failure | 3 retries (exponential backoff 200ms/400ms/800ms) → Circuit Breaker → 503 |
| Unexpected exception | 5xx + correlation_id logging; generic message shown to the user |

## 8. Non-Functional Requirements

### 8.1 Performance
- **P95 response time**: under 200 ms (registration API baseline)
- **Concurrent throughput**: 100 RPS
- **Transaction boundary**: {decided by Step 3 HITL}

### 8.2 Security
- **Authentication method**: {decided by Step 3 HITL}
- **Sensitive data**: email is PII; masked when logged (`h***@example.com`)
- **OWASP coverage**: SQL Injection (Prepared Statement), Mass Assignment (DTO whitelist)

### 8.3 Availability
- **Failure isolation**: {external dependency → decided by Step 3 HITL}
- **Rollback strategy**: migrations are forward-only; when adding FKs, allow NULL → backfill → NOT NULL

## 9. Test Strategy Overview

> **Detailed scenarios**: the `/test-scenario` skill takes this blueprint as input and writes to `docs/tests/test-cases/sprint-{N}/`.

| Level | Scope | Tool |
|-------|-------|------|
| Unit | Pseudocode branches from Section 6 | JUnit / Vitest / pytest |
| Integration | Section 4 API contract + Section 3 DB | Testcontainers |
| E2E | Section 2.2 user scenario | Playwright / cmux browser |

### 9.1 Required test cases (coverage priority)
- [ ] {Section 5.1 happy path}
- [ ] {all Section 5.2 error paths}
- [ ] {all Section 2.3 business rules BR-01 ~ BR-N}
- [ ] {each Section 7 error-handling policy item}

## 10. HITL Triggers (for implementation phase)

> **This section is consulted by `/feature-dev` when it implements based on this blueprint**. Any decision that does *not* match a trigger condition listed here is **automatically applied per the blueprint spec without asking the user**. Only decisions matching a trigger are asked of the user.

### 10.1 HITL firing principles

During implementation, ask via `AskUserQuestion` only when one of the four conditions below applies. Otherwise proceed automatically per the blueprint spec:

| # | Trigger | Reason |
|---|---------|--------|
| T1 | Business decision with no clear answer in the blueprint | An LLM guess risks violating domain rules |
| T2 | Security/permission/authentication policy choice | A wrong auto-decision can become a security incident |
| T3 | Introducing an external dependency / 3rd-party library | Permanent impact on package.json / build.gradle |
| T4 | Destructive change (DROP/RENAME in DB migration, breaking a public API signature) | Hard to roll back and may impact other callers |

### 10.2 HITL triggers specific to this feature (concrete items)

> Only *foreseeable* decision points are filled in during blueprint authoring. Decisions invisible at authoring time are judged during implementation per principle 10.1 above.

| ID | Trigger category | Decision required during implementation | Options (if the blueprint already answers, auto-applied) |
|----|------------------|-----------------------------------------|----------------------------------------------------------|
| HITL-01 | T1 business | {e.g., "Validity duration of the email verification code"} | {answer: BR-03 in Section 2.3 specifies "10 minutes"} → **auto** |
| HITL-02 | T2 security | {e.g., "Password hashing algorithm choice"} | {not specified in blueprint} → **user question required** |
| HITL-03 | T3 external dependency | {e.g., "Email-sending library"} | {e.g., SendGrid / AWS SES / Mailgun} → **user question required** |
| HITL-04 | T4 destructive | {e.g., "RENAME of existing TB_USER.USER_NM to FULL_NM, or removal of a response field from GET /api/users"} | {not specified in blueprint — downstream caller / migration impact must be reviewed} → **user question required** |

### 10.3 HITL question authoring rules

When `/feature-dev` consults this table to ask the user, it follows this format:

1. **Question in a single sentence** — clearly state what is being asked
2. **2–4 options** — every option must include all three of:
   - Option name (within 5 words)
   - One-line description (the trade-off in a sentence)
   - Impact scope (where and how the choice is reflected)
3. **The first option is the recommended one** — place the most conservative/safe choice on top and append "(Recommended)"
4. **Free input via 'Other'** — if the 4 options do not fit, the user can type a custom answer
5. **Answers are written back into the blueprint** — when an answer arrives, the relevant blueprint section is updated via `Edit` (e.g., HITL-02 answer reflected in 8.2)

**Example question format**:

```
Q. Which password hashing algorithm should we use? (HITL-02)

Option 1: Argon2id (Recommended)
  Description: Memory-hard function. Recommended by OWASP 2025. Strong against GPU/ASIC attacks.
  Impact: add `de.mkammerer:argon2-jvm:2.11` to build.gradle; update Section 8.2.

Option 2: bcrypt
  Description: Older standard. Battle-tested library. Memory-hardness is lower.
  Impact: use Spring Security's default PasswordEncoder; no additional dependency.

Option 3: scrypt
  Description: Memory-hard + tunable cost. Predecessor to Argon2.
  Impact: add bouncy castle library.
```

### 10.4 Decisions the user must *not* be asked (Anti-HITL)

The following are auto-decided per the blueprint / conventions and must not surface a question:

- Variable, function, and class names — coding convention auto-applied
- Code formatting (indent, line breaks, quotes) — convention auto-applied
- Logging location/level — convention (INFO: business events, DEBUG: branches, ERROR: exceptions)
- Whether to add unit test cases — if Section 9.1 has a checklist, writing them is mandatory
- File splitting / directory structure — follow the project's existing structure
- Import order, wildcard imports — convention auto-applied
- DTO/Entity separation — project convention
- Fine response-code tuning (e.g., 200 vs. 201) — REST convention

> **Principle**: "If it is ambiguous whether to ask the user, do not ask — pick the default specified in the blueprint or a conservative auto-decision." If the LLM wakes the user too often, the value of automation disappears.
```

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

After `review.md` is written, summarize the P0 issues to the user. In Step 6, grep the `Overall Score: NN` line to extract `REVIEW_SCORE`.

### Step 6: Commit the blueprint to the sprint branch

> **v5.10+ simplification**: In the old v5.8/5.9 flow, the blueprint had to be committed to `dev` before `/sprint-init` ran (so the worktree's base would contain the blueprint). In v5.10+, the worktree already exists *before* the blueprint is written, so the commit naturally lands on the sprint branch — no cross-branch visibility concern remains.

```bash
# 6.1 Confirm we are still inside the sprint worktree (sanity check)
if [ "$WORKTREE_CREATED" = "1" ] && [ "$(pwd)" != "$WT_PATH" ]; then
  cd "$WT_PATH"  # Re-cd defensively if something earlier popped us out
fi

# 6.2 Extract the blueprint-reviewer score
REVIEW_SCORE=$(grep -oE 'Overall Score: [0-9]+' "$BLUEPRINT_DIR/review.md" 2>/dev/null | grep -oE '[0-9]+' || echo "N/A")
```

**Commit handling**:

- **`AUTO_MODE=1` (called by autorun)**: commit automatically without asking.
- **Manual mode**: show changed files via `git status -- "$BLUEPRINT_DIR_REL/"` and ask once via `AskUserQuestion`:
  - Question: "Commit the blueprint you just authored to the sprint branch (`$SPRINT_BRANCH`) now?"
  - Option 1: "Yes, commit now (Recommended)" — auto commit
  - Option 2: "No, I will commit it myself" — skip commit, show the user the commands (`git add docs/blueprints/{NNN}-... && git commit -m "..."`)

```bash
# 6.3 Execute the commit
git add "$BLUEPRINT_DIR_REL"
git commit -m "docs(blueprint): scaffold ${NUM}-${FEATURE_SLUG} blueprint

- 10 standard sections (data flow / schema / API / sequence / pseudo / HITL Triggers)
- Generated by /blueprint skill v2 (worktree-first)
- Reviewed by blueprint-reviewer (score: ${REVIEW_SCORE}/100)
- Sprint branch: ${SPRINT_BRANCH}
"
```

> **No remote push** — `/pr-merge` handles pushing the sprint branch at the end of the sprint.

> **Secondary-blueprint case (`WORKTREE_CREATED=0`)**: the commit lands on the existing sprint branch (whichever branch the user was on). This is the prompt-map Step 1.1 flow — no additional handling.

### Step 7: Output

Output format branches on whether Step 1.6 created a new worktree.

#### Case A: Worktree was created (`WORKTREE_CREATED=1`) — default path

```
✅ Blueprint authoring complete (worktree-first flow)

🌿 Sprint worktree (created at the start of /blueprint):
   Path:      {WT_PATH}
   Branch:    {SPRINT_BRANCH}
   Port base: {PORT_BASE}
   env file:  {WT_PATH}/.astra-worktree.env

📄 Blueprint: {BLUEPRINT_PATH}
   (relative to worktree: {BLUEPRINT_DIR_REL}/blueprint.md)
📋 Review:    {BLUEPRINT_DIR}/review.md ({score}/100)
📦 Commit:    {commit SHA} on {SPRINT_BRANCH}

────────────────────────────────────────────────────────────────
👉 Run this next to enter the sprint worktree (your shell is still in main):

   cd {WT_PATH}

   Then continue with the prompts below.
────────────────────────────────────────────────────────────────

🎯 Next steps (after `cd {WT_PATH}`):
  /feature-dev "Implement the data model / API / logic in {BLUEPRINT_DIR_REL}/blueprint.md. Comply with Section 10 HITL Triggers."
  /test-scenario {feature-slug}            # generate blueprint-based test cases
  /test-run                                 # integration tests on the sprint-specific port
  /pr-merge                                 # Sprint Phase (review loop) — then cd to main worktree to finalize

⚠️ P0 issues ({count}):
  - {summary}
```

> **The skill does not auto-cd from the user's interactive shell**. Inside this skill execution the cwd was already moved to `$WT_PATH` for git operations, but the parent shell context reverts on return. The user must run the `cd` command above before continuing.

#### Case B: Already inside a sprint worktree (`WORKTREE_CREATED=0`, secondary blueprint)

```
✅ Blueprint authoring complete (secondary blueprint — existing worktree reused)

🌿 Existing sprint worktree:
   Path:      {WT_PATH}
   Branch:    {SPRINT_BRANCH}

📄 Blueprint: {BLUEPRINT_PATH}
📋 Review:    {BLUEPRINT_DIR}/review.md ({score}/100)
📦 Commit:    {commit SHA} on {SPRINT_BRANCH}

🎯 Next steps (you are already in the sprint worktree):
  /feature-dev "Implement {BLUEPRINT_DIR_REL}/blueprint.md. Comply with Section 10 HITL Triggers."
  /test-scenario {feature-slug}
  /test-run

⚠️ P0 issues ({count}):
  - {summary}
```

## Invocation pattern from autorun

```
Skill('blueprint', '{feature-slug} --auto --from-planner=docs/planner/{NNN}-{feature-slug}')
```

With `--auto`, all Step 3 HITL questions are skipped and the defaults (auto-inc PK / single transaction + Outbox / sync + CB) are applied. This guarantees unattended execution.

> **v5.10+ note for `/autorun`**: Stage 3 (blueprint) now creates the sprint worktree as its very first sub-step. Stage 4 (the old `/sprint-init` re-entry) is therefore a no-op in the standard path — `/autorun` keeps the Stage 4 invocation as an idempotent guard (it detects the existing worktree via `astra_is_isolated_worktree` and exits) but no new scaffolding occurs. The Stage 4.5 explicit `cd $WT_PATH` performed by `/autorun` is still required to align the parent context cwd with the worktree before Stage 5 begins.

## FAQ

**Q. Why does the worktree come before the blueprint now?**
In v5.8/5.9 the blueprint was written first (on dev), then `/sprint-init` was invoked which had to *carry the blueprint over to the new worktree's base*. That required a dev commit before worktree creation, plus careful timing of git push. v5.10+ flips the order — the worktree exists first, so the blueprint commit is naturally the first commit on the sprint branch. No cross-branch visibility logic, no dev-commit-then-worktree race, simpler invariants.

**Q. What happens if `/sprint-init --scaffold-only` fails midway?**
`/sprint-init` aborts with a non-zero exit. `/blueprint` then reports the failure and exits without writing the blueprint file. There is nothing to clean up — the partial worktree (if any) is left in `git worktree list` for the user to remove manually with `git worktree remove <path>`. A future enhancement could add automatic cleanup, but the conservative behavior is to leave artifacts visible.

**Q. Isn't pseudocode also code?**
Pseudocode is a design tool that expresses algorithmic intent in a language-neutral form. It is not executable, hence not "implementation". The ` ```pseudo ` language tag is mandated because, without it, an LLM may misread it as real code.

**Q. Why are ORM annotations forbidden?**
`@Entity`, `@Column`, etc. are framework-specific (JPA/Hibernate). The blueprint is sufficient with DDL + tables, and annotation translation is `/generate-entity`'s job. Writing annotations at the blueprint stage (a) is wasted when porting to a non-JVM project, and (b) creates inconsistencies between translated DDL and annotations.

**Q. What about a brand-new feature without planner deliverables?**
In Step 2, create the empty skeleton and fill it from the user description alone. Sections that cannot be derived (e.g., 1.4 KPI) leave the marker `❓ Additional information needed — planner deliverables or user input required`, so that blueprint-reviewer flags them as P0.

**Q. How do I update an existing blueprint?**
Pass an existing path (`docs/blueprints/003-user-auth/blueprint.md`) as the first argument. The skill detects the path form (vs. a slug) and skips Step 1.5/1.6/1.7 worktree creation — instead it `cd`'s into the worktree that already owns this blueprint (resolved via `git worktree list`), runs `Edit` on the existing file, re-runs the reviewer in Step 5, and commits the update in Step 6.
