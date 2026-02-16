---
name: test-scenario
description: "Creates E2E test scenarios based on the project's existing work context. Analyzes blueprints, DB design, routes, and API endpoints to generate comprehensive test scenarios for integration testing."
argument-hint: "[feature-name or 'all']"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# ASTRA E2E Test Scenario Generator

Analyzes the project's existing work context (blueprints, DB design, routes, API endpoints, existing code) to generate comprehensive E2E test scenarios in `docs/tests/test-cases/`.

Refer to `e2e-scenario-guide.md` in the same directory as this skill for scenario design guidelines and patterns.

## Execution Procedure

### Step 1: Collect Project Context

Gather project-level context to understand the overall architecture:

1. Read `CLAUDE.md` to identify tech stack, project structure, and conventions
2. Read `docs/tests/test-strategy.md` to understand test levels, coverage goals, and naming rules
3. Scan `docs/tests/test-cases/` for existing test case files to avoid duplication
4. Read `docs/database/database-design.md` to understand the data model

### Step 2: Feature Discovery

Scan the project to identify all testable features:

#### A. Blueprint Analysis

```
1. Glob docs/blueprints/*.md
2. For each blueprint, extract:
   - Feature name and description
   - User stories / functional requirements
   - API endpoints referenced
   - DB tables referenced
   - Dependencies on other features
```

#### B. Route/Page Structure

```
1. Scan for page/route files:
   - Next.js: src/app/**/page.tsx, src/pages/**/*.tsx
   - React: src/routes/, src/pages/
   - Vue: src/views/, src/pages/
   - Angular: src/app/**/*routing*
2. Build a page inventory with URL paths
```

#### C. API Endpoint Discovery

```
1. Scan for API controllers/route handlers:
   - Spring Boot: @RestController, @RequestMapping, @GetMapping, @PostMapping, etc.
   - NestJS: @Controller, @Get, @Post, etc.
   - Express/Fastify: router.get, router.post, app.get, app.post
   - FastAPI: @app.get, @app.post, @router.get
   - Next.js API: src/app/api/**/route.ts, src/pages/api/**/*.ts
2. Build an endpoint inventory with HTTP methods and paths
```

#### D. DB Table Scan

```
1. Read docs/database/database-design.md for the SSoT table list
2. Cross-reference with entity/model files in source code
3. Identify CRUD operations per table
```

### Step 3: Select Test Targets

Determine which features to generate scenarios for based on `$ARGUMENTS`:

| Argument | Behavior |
|----------|----------|
| `{feature-name}` | Generate scenarios for the specified feature only |
| `all` | Generate scenarios for all discovered features |
| _(empty)_ | Show discovered feature list and ask user to select with `AskUserQuestion` |

When asking the user, present the discovered features as a numbered list with brief descriptions:

```
Discovered features:
1. auth - Authentication (login, signup, token refresh)
2. order - Order management (create, cancel, status)
3. payment - Payment processing (pay, refund)

Which features should I generate E2E scenarios for?
```

### Step 4: Analyze Existing Test Cases

Before generating new scenarios, check for existing coverage:

1. Glob `docs/tests/test-cases/{feature-name}*` for each selected feature
2. If existing test case files are found:
   - Read and parse existing scenarios
   - Identify gaps (missing Happy Path, Edge Case, or Error Path)
   - Report to user: "Found {N} existing scenarios for {feature}. Will generate additional scenarios for uncovered paths."
3. If no existing files are found, proceed with full scenario generation

### Step 5: Design E2E Scenarios

For each selected feature, design scenarios following the user journey approach.

#### A. Analyze Feature Requirements

```
1. Read the feature's blueprint (docs/blueprints/{feature-name}.md)
2. Identify:
   - Primary user journeys (Happy Path)
   - Alternative paths (valid but non-standard flows)
   - Edge cases (boundary values, empty states, concurrent access)
   - Error paths (invalid input, unauthorized access, server errors)
3. Map each journey to specific pages, API calls, and DB operations
```

#### B. Build Scenario Groups

Organize scenarios into logical groups based on user journeys:

```
Scenario Group: {User Journey Name}
├── Happy Path scenarios (Critical/High priority)
├── Alternative Path scenarios (Medium priority)
├── Edge Case scenarios (Medium/Low priority)
└── Error Path scenarios (High/Medium priority)
```

#### C. Define Each Scenario

For each scenario, specify:

- **Scenario ID**: `E2E-{NNN}` (sequential within the feature)
- **Type**: Happy Path / Alternative Path / Edge Case / Error Path
- **Priority**: Critical / High / Medium / Low (refer to `e2e-scenario-guide.md` for criteria)
- **Preconditions**: Required state before test execution
- **User Journey**: Step-by-step actions with specific pages and UI elements
- **Expected Results**: Verification points for UI, API, DB, and server logs
- **Verification Method**: snapshot / console / network / server-log / db-query
- **Test Data**: Required input data for the scenario

### Step 6: Generate Scenario Files

Write scenario files to `docs/tests/test-cases/` using the following format:

**File naming**: `{feature-name}-e2e-scenarios.md`

**File template**:

```markdown
# {Feature Name} E2E Test Scenarios

## Overview
- **Feature**: {feature description from blueprint}
- **Related Modules**: {dependent modules}
- **API Endpoints**: {related endpoints}
- **DB Tables**: {related tables}
- **Blueprint**: docs/blueprints/{feature-name}.md

## Scenario Group 1: {User Journey Name}

### E2E-001: {Scenario Title}
- **Type**: Happy Path
- **Priority**: Critical
- **Preconditions**: {required state}
- **User Journey**:
  1. Navigate to {page URL}
  2. {action with specific UI element}
  3. {action}
- **Expected Results**:
  - UI: {expected screen state}
  - API: {expected API calls and responses}
  - DB: {expected data changes}
  - Server Log: {expected log entries}
- **Verification Method**: snapshot / network
- **Test Data**: {required test data}

### E2E-002: {Scenario Title}
- **Type**: Error Path
- **Priority**: High
...

## Scenario Group 2: {User Journey Name}
...

---

## Summary
| Type | Count |
|------|-------|
| Happy Path | {n} |
| Alternative Path | {n} |
| Edge Case | {n} |
| Error Path | {n} |
| **Total** | **{n}** |
```

Create the `docs/tests/test-cases/` directory if it does not exist.

### Step 7: Generate Cross-feature Scenarios

If multiple features are selected (or `all`), generate cross-feature integration scenarios:

1. Identify feature dependencies from blueprints and shared DB tables
2. Design end-to-end user journey scenarios that span multiple features

   Example: Sign up -> Login -> Browse products -> Add to cart -> Checkout -> Payment -> Order confirmation

3. Write to `docs/tests/test-cases/cross-feature-e2e-scenarios.md` using the same format as Step 6

**Skip this step** if only a single feature is selected.

### Step 8: User Review

Present the generated scenarios to the user for review:

```
## Generated E2E Test Scenarios

### {Feature 1 Name}
- File: docs/tests/test-cases/{feature-1}-e2e-scenarios.md
- Scenarios: {N} total ({n} Happy, {n} Alternative, {n} Edge, {n} Error)

### {Feature 2 Name}
- File: docs/tests/test-cases/{feature-2}-e2e-scenarios.md
- Scenarios: {N} total

### Cross-feature (if applicable)
- File: docs/tests/test-cases/cross-feature-e2e-scenarios.md
- Scenarios: {N} total

Would you like to review or modify any scenarios?
```

If the user requests changes, edit the corresponding scenario files accordingly.

### Step 9: Result Summary

After user confirmation, output a final summary:

```
## E2E Test Scenario Generation Complete

### Statistics
| Feature | Happy Path | Alt Path | Edge Case | Error Path | Total |
|---------|-----------|----------|-----------|------------|-------|
| {feature-1} | {n} | {n} | {n} | {n} | {n} |
| {feature-2} | {n} | {n} | {n} | {n} | {n} |
| Cross-feature | {n} | {n} | {n} | {n} | {n} |
| **Total** | **{n}** | **{n}** | **{n}** | **{n}** | **{n}** |

### Generated Files
- docs/tests/test-cases/{feature-1}-e2e-scenarios.md
- docs/tests/test-cases/{feature-2}-e2e-scenarios.md
- docs/tests/test-cases/cross-feature-e2e-scenarios.md

### Next Steps
1. Run `/test-run` to execute the generated scenarios in a real browser
2. Run test-coverage-analyzer agent to verify test coverage against test-strategy.md
3. Iterate: add missing scenarios as new edge cases are discovered during testing
```

## Quick Run Examples

```
# Generate E2E scenarios for a specific feature
/test-scenario auth

# Generate E2E scenarios for all discovered features
/test-scenario all

# Interactive mode — discover features and let user choose
/test-scenario
```

## Notes

- Scenario files are additive — running again for the same feature updates existing files rather than overwriting
- Scenarios are designed to be directly executable by the `/test-run` skill
- The scenario format is compatible with the test-coverage-analyzer agent for coverage verification
- Cross-feature scenarios are only generated when multiple features are selected
- Priority levels follow the criteria defined in `e2e-scenario-guide.md`
