# E2E Scenario File Format (test-scenario Step 6 detail)

Read this when writing scenario files in Step 6 (and Step 7 cross-feature files use the same format). Files go to `docs/tests/test-cases/sprint-{SPRINT_N}/`; create the directory if it does not exist.

**File naming**: `{feature-name}-e2e-scenarios.md` (cross-feature: `cross-feature-e2e-scenarios.md`)

## File template

```markdown
# {Feature Name} E2E Test Scenarios

## Overview
- **Feature**: {feature description from blueprint}
- **Related Modules**: {dependent modules}
- **API Endpoints**: {related endpoints}
- **DB Tables**: {related tables}
- **Blueprint**: docs/blueprints/{NNN}-{feature-name}/blueprint.md

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
