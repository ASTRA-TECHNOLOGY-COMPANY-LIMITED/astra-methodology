# Sprint Prompt Map Templates

Templates instantiated by `/sprint-init` Step 2 into `$WT_PATH/docs/sprints/sprint-{N}-{sprint-name}/prompt-map.md`. Replace `{N}`, `{sprint-name}`, `{feature-name}`, `{NNN}` placeholders. Repeat the `## Feature` block per blueprint. Append the **At Sprint End** tail (bottom of this file) to whichever variant you instantiate.

## Table of contents

- **Variant A** — direct user invocation (neither `--scaffold-only` nor `--from-blueprint`). 4-step feature block: 1.1 Blueprint authoring · 1.2 DB Design · 1.3 Test Cases · 1.4 Implementation.
- **Variant B** — called by `/blueprint` (`SCAFFOLD_ONLY=1` OR `FROM_BLUEPRINT=1`). Blueprint authoring omitted (the caller authors it); renumbered 3-step feature block: 1.1 DB Design · 1.2 Test Cases · 1.3 Implementation.
- **At Sprint End tail** — shared Z.1 Integration Test + Z.2 Merge block appended to both variants.

Selection rule: `SCAFFOLD_ONLY=1` OR `FROM_BLUEPRINT=1` → Variant B; otherwise → Variant A.

---

## Variant A — neither flag set (legacy direct invocation)

```markdown
# Sprint {N} Prompt Map

## Sprint Goal
[Describe the business value to achieve in this sprint]

> **Isolation note (v5.16+)**: In the default **in-place** mode this sprint's `feat/sprint-{N}-{sprint-name}` branch is checked out directly in the main worktree — run every task from there, in this session, no `cd`. If this sprint was **escalated to worktree isolation**, every task instead runs inside `.astra-worktrees/sprint-{N}-{sprint-name}/` and new Claude Code sessions must be started from that path.

## Feature 1: {feature-name}

### 1.1 Blueprint Prompt
/blueprint {feature-name} --from-planner=docs/planner/{NNN}-{feature-name}

> The `/blueprint` skill takes `/service-planner` deliverables (auto-loaded when present) as input and writes a 10-standard-section blueprint to `docs/blueprints/{NNN}-{feature-name}/blueprint.md`.
> - **Included**: data flow, schema DDL, ER diagram, API JSON Schema, sequence diagrams, pseudocode logic, HITL Triggers
> - **Excluded**: executable implementation code, ORM annotations, framework-dependent expressions
> - Only asks 1-3 items that genuinely require human judgment (PK strategy, transaction boundary, external-dependency sync mode) automatically.
>
> **Numbering Rule**: Scan existing directories in `docs/blueprints/` to determine the next number. Use 3-digit zero-padded format (e.g., `001-`, `002-`).

### 1.2 DB Design Reflection Prompt
/feature-dev "Refer to docs/blueprints/{NNN}-{feature-name}/blueprint.md Section 3 (Data Model) and reflect those tables/columns/indexes/FK relationships into docs/database/database-design.md, including the ERD and FK relationship summary.

The blueprint is the single source of truth — do not change schema decisions, do not add columns not in the blueprint, do not rename. If you find a real inconsistency, stop and report instead of guessing.

HITL Guard: Before asking the user any question, first check Section 10 (HITL Triggers) of the blueprint. Only ask the user when the decision matches T1-T4 triggers (business decisions without a clear answer in the blueprint, security/permission choices, external dependency choices, destructive changes). For everything else, follow the blueprint and proceed automatically.

Do not modify any application code yet."

### 1.3 Test Case Prompt
/feature-dev "Based on docs/blueprints/{NNN}-{feature-name}/blueprint.md Section 9 (Test Strategy) and Section 9.1 (Required Test Cases), write test cases to docs/tests/test-cases/sprint-{N}/{feature-name}-test-cases.md.

Use Given-When-Then format. Cover: (a) Section 5.1 happy path, (b) Section 5.2 exception paths, (c) Section 2.3 business rules, (d) Section 7 error policy items. Include unit, integration, and edge cases.

HITL Guard: Section 10 (HITL Triggers) of the blueprint defines when to ask the user. Outside those triggers, derive test cases directly from the blueprint without asking. If a test case requires a decision not in the blueprint and not in Section 10, default to the most conservative coverage and note it as TODO instead of pausing.

Do not modify any application code yet."

### 1.4 Implementation Prompt
/feature-dev "Strictly follow docs/blueprints/{NNN}-{feature-name}/blueprint.md and docs/database/database-design.md to implement the feature. Write code that matches: Section 3 (DDL → ORM entities), Section 4 (API contract → controllers/DTOs), Section 5 (sequence diagrams → service orchestration), Section 6 (pseudocode → real implementation), Section 7 (error policy → exception handlers), Section 8 (non-functional → middleware/security config).

Write tests referencing docs/tests/test-cases/sprint-{N}/{feature-name}-test-cases.md. Once implementation is complete, run all tests and report results to docs/tests/test-reports/.

HITL Guard (important): The blueprint's Section 10 (HITL Triggers) tells you exactly when to ask the user during implementation. The four triggers are T1 (business decisions without a clear blueprint answer), T2 (security/permission policy choices), T3 (external dependency/3rd-party introduction), T4 (destructive changes like DROP/RENAME or public API signature change). Outside those triggers, do not ask — apply the blueprint as written and follow coding conventions.

Specifically do NOT ask the user about: variable/function names, code formatting, log levels, file layout, import order, DTO/Entity split, fine-grained HTTP status codes — those follow project conventions automatically. Waking the user too often defeats the automation."

## Feature 2: {feature-name}
{Repeat with the same structure as above}
```

---

## Variant B — `SCAFFOLD_ONLY=1` OR `FROM_BLUEPRINT=1` (v5.16+ context-first flow, or legacy v5.8/5.9 delegation)

The blueprint authoring step is omitted because `/blueprint` already wrote (or is about to write) the blueprint immediately after this skill returns. The user will start from "1.1 DB Design Reflection".

```markdown
# Sprint {N} Prompt Map

## Sprint Goal
[Describe the business value to achieve in this sprint]

> **Isolation note (v5.16+)**: In the default **in-place** mode this sprint's `feat/sprint-{N}-{sprint-name}` branch is checked out directly in the main worktree — run every task from there, in this session, no `cd`. If this sprint was **escalated to worktree isolation**, every task instead runs inside `.astra-worktrees/sprint-{N}-{sprint-name}/` and new Claude Code sessions must be started from that path.
>
> **Blueprint authoring note (v5.10+)**: The blueprint(s) for this sprint are authored by the `/blueprint` skill that created this sprint context. When this prompt-map is opened by the user, the blueprint already exists under `docs/blueprints/{NNN}-{feature-name}/blueprint.md` on the sprint branch. Start from 1.1 below.

## Feature 1: {feature-name}

### 1.1 DB Design Reflection Prompt
/feature-dev "Refer to docs/blueprints/{NNN}-{feature-name}/blueprint.md Section 3 (Data Model) and reflect those tables/columns/indexes/FK relationships into docs/database/database-design.md, including the ERD and FK relationship summary.

The blueprint is the single source of truth — do not change schema decisions, do not add columns not in the blueprint, do not rename. If you find a real inconsistency, stop and report instead of guessing.

HITL Guard: Before asking the user any question, first check Section 10 (HITL Triggers) of the blueprint. Only ask the user when the decision matches T1-T4 triggers (business decisions without a clear answer in the blueprint, security/permission choices, external dependency choices, destructive changes). For everything else, follow the blueprint and proceed automatically.

Do not modify any application code yet."

### 1.2 Test Case Prompt
/feature-dev "Based on docs/blueprints/{NNN}-{feature-name}/blueprint.md Section 9 (Test Strategy) and Section 9.1 (Required Test Cases), write test cases to docs/tests/test-cases/sprint-{N}/{feature-name}-test-cases.md.

Use Given-When-Then format. Cover: (a) Section 5.1 happy path, (b) Section 5.2 exception paths, (c) Section 2.3 business rules, (d) Section 7 error policy items. Include unit, integration, and edge cases.

HITL Guard: Section 10 (HITL Triggers) of the blueprint defines when to ask the user. Outside those triggers, derive test cases directly from the blueprint without asking. If a test case requires a decision not in the blueprint and not in Section 10, default to the most conservative coverage and note it as TODO instead of pausing.

Do not modify any application code yet."

### 1.3 Implementation Prompt
/feature-dev "Strictly follow docs/blueprints/{NNN}-{feature-name}/blueprint.md and docs/database/database-design.md to implement the feature. Write code that matches: Section 3 (DDL → ORM entities), Section 4 (API contract → controllers/DTOs), Section 5 (sequence diagrams → service orchestration), Section 6 (pseudocode → real implementation), Section 7 (error policy → exception handlers), Section 8 (non-functional → middleware/security config).

Write tests referencing docs/tests/test-cases/sprint-{N}/{feature-name}-test-cases.md. Once implementation is complete, run all tests and report results to docs/tests/test-reports/.

HITL Guard (important): The blueprint's Section 10 (HITL Triggers) tells you exactly when to ask the user during implementation. The four triggers are T1 (business decisions without a clear blueprint answer), T2 (security/permission policy choices), T3 (external dependency/3rd-party introduction), T4 (destructive changes like DROP/RENAME or public API signature change). Outside those triggers, do not ask — apply the blueprint as written and follow coding conventions.

Specifically do NOT ask the user about: variable/function names, code formatting, log levels, file layout, import order, DTO/Entity split, fine-grained HTTP status codes — those follow project conventions automatically. Waking the user too often defeats the automation."

## Feature 2: {feature-name}
{Repeat with 1.1/1.2/1.3 structure — additional blueprints are added via secondary /blueprint invocations inside this worktree.}
```

---

## At Sprint End tail (append to both Variant A and Variant B)

```markdown
---

## At Sprint End (after all features are implemented)

### Z.1 Integration Test
/test-run

> Boots the server using the sprint-specific ports in `.astra-worktree.env` and runs tests.
> When the tests finish, the server processes on those ports are also cleaned up automatically.

### Z.2 Merge (v5.16+ adaptive isolation)
/pr-merge

> **In-place sprint (`ISOLATION_MODE=inplace`, the default)**: the `feat/sprint-{N}-{sprint-name}` branch is checked out in the main worktree, so `/pr-merge` completes **single-phase in this same session** — commit → push → PR → code review → fix loop → merge → promotion → sprint-branch cleanup. There is **no `cd`** and no second invocation.
>
> **Worktree sprint (`ISOLATION_MODE=worktree`, escalated isolation)**: two-phase (v5.9+). Sprint Phase runs commit → push → PR → code review → fix loop inside this worktree, then stops. Follow the printed `cd` command to move to the main worktree and re-invoke `/pr-merge` — it auto-detects the pending sprint PR (head=feat/sprint-*, base=feat/*|fix/* integration branch, with a legacy base=dev fallback for pre-v5.11 PRs), finalizes the merge, then removes this sprint worktree.
>
> Tip: `/pr-merge --auto` runs both modes end-to-end in one invocation (sprint-init's auto pipeline and /autorun do this automatically).
```
