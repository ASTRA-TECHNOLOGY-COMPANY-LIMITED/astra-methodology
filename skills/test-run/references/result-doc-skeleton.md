# Step 9 — Test Result Document Skeleton

Full markdown skeleton for the document written to `docs/tests/test-reports/`.
Counts MUST come from the Step 11 machine-anchored parse, never memory. The
`ASTRA_TEST_RESULT` line must appear verbatim.

```markdown
# Integration Test Report

## Test Environment
- Date: {date}
- Server: {tech stack + version}
- Browser: {cmux built-in browser / ego (lite) / Chrome DevTools MCP / No browser (API-only)}

<!-- Machine-parseable gate line — values from captured command output only -->
ASTRA_TEST_RESULT: {PASS|FAIL} passed={N} failed={N} total={N} skipped={N}

## Test Result Summary

| Item | Result | Notes |
|------|------|------|
| Server Startup | PASS/FAIL | |
| Console Errors | {count} | |
| Network Failures | {count} | |
| Responsive Layout | PASS/FAIL | |
| Scenario Tests | {passed}/{total} | |
| Server Log Errors | {count} | |

## Detailed Results

### Per-page Verification
{per-page results}

### Scenario Tests
{per-scenario results}

### Server Log Analysis
{key log issues}

### Issues Found
1. [Critical|High|Medium|Low] {issue description}
   - Location: {page/API}
   - Server Log: {related log}
   - Reproduction Steps: {steps}

## Performance Measurement (if performed)
{Core Web Vitals results}
```
