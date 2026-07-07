# Test Gate Scoring — severity rubric & test-runner summary parsing

Reference data for the Step 11 machine-anchored gate and the Step 9 report's
"Issues Found" list. Read this when assigning issue severity or when parsing a
unit/E2E test runner's summary output.

## Severity rubric (rule-based, not judgment call)

Assign every issue found a severity from this table; the overall gate keys off
Critical/High:

| Severity | Definition | Concrete examples |
|----------|-----------|-------------------|
| **Critical** | Blocks core flow; data loss/corruption; security hole | Server 5xx on a primary path; unhandled exception in server log; auth bypass; request that drops/corrupts data |
| **High** | Feature broken but flow reachable; no safe workaround | Form submit fails; API returns 4xx on a valid request; JS console `error` that breaks interaction; broken redirect in auth flow |
| **Medium** | Degraded UX; workaround exists | Console `warn`; slow response 3–10s; responsive layout breakage at one viewport; missing loading state |
| **Low** | Cosmetic / advisory | a11y nit (non-blocking); minor style drift; deprecation notice; response 1–3s |

## Test-runner summary lines to parse (Step 11)

If the project also has a unit/E2E test runner (e.g. `npm test`, `pytest`,
`./gradlew test`), **run it via the Bash tool**, capture its exit code, and parse
its own summary line for the numbers (add them into the scenario-log counts).
Examples of runner summary lines to grep — never substitute a remembered number:

| Runner | Summary line to parse |
|--------|-----------------------|
| Jest / Vitest | `Tests: N passed, N failed, N total` |
| pytest | `N passed, N failed in Xs` |
| Gradle / JUnit | `N tests completed, N failed` |

A non-zero runner exit code forces overall `FAIL` regardless of parsed counts.
