# /uat-parallel — Parallelism, Isolation & Tuning Guide

Companion reference for the `/uat-parallel` skill. Explains how the parallel runner achieves isolation, how to tune `--workers`, and how to debug flaky cases.

## 1. Isolation guarantees

Each Playwright test runs inside its own `BrowserContext`, automatically created by the framework. A context owns:

- An isolated cookie jar
- Isolated `localStorage` and `sessionStorage`
- Isolated `IndexedDB`
- An isolated origin permission set (geolocation, notifications, etc.)

Consequence for UAT authoring:

- **Multi-user flows are safe**: two cases can each log in as a different user with no cross-contamination.
- **Each case starts cold**: cookies do not persist across cases. If a case needs a logged-in state, perform the login as its first steps (or use Playwright `storageState` — not yet wired in this runner).
- **Race conditions are real**: if two cases hit the same backend resource (`POST /api/users` with the same email), they will collide. Use `value=user+{timestamp}@example.com` so the case-generated value is unique per run.

## 2. Worker count tuning

| `--workers` value | When to use |
|---|---|
| `1` | Debugging a single case (`--headed --workers 1`) |
| `2` | Slow / memory-bound app, or low-spec CI |
| `cpu/2` (default) | Typical local dev workstation |
| `cpu - 1` | Dedicated CI runner with sufficient RAM |
| `> cpu` | Never — context switching outweighs gains |

Rule of thumb: each Chromium worker takes ~150–250 MB RAM. A 16 GB laptop comfortably runs 6–8 workers; a 4 GB CI runner caps at 2.

## 3. Per-step and per-case timeouts

| Env var | Default | Purpose |
|---|---|---|
| `UAT_STEP_TIMEOUT_MS` | `30000` | Single action (navigate / click / fill) timeout |
| `UAT_CASE_TIMEOUT_MS` | `300000` | Whole-case wall-clock budget |

When a step hits the step timeout, Playwright kills the action and the case FAILs (severity assigned by the rule table). The worker is recycled and picks up the next queued case. A stuck case never starves the run.

## 4. Trace replay for failed cases

`playwright.config.ts` sets `trace: 'retain-on-failure'`. Every FAILed case yields a `.zip` archive containing the DOM snapshot timeline, network log, and console output:

```bash
npx playwright show-trace docs/tests/uat-reports/{SESSION_ID}/traces/UAT-042.zip
```

Use this when the static screenshot is not enough — the trace viewer steps through the case interactively.

## 5. Debugging flaky parallel runs

| Symptom | Common cause | Fix |
|---|---|---|
| One case passes alone, fails in parallel | Race on shared DB row | Use `{timestamp}` in unique fields, or scope by per-worker namespace |
| All cases time out | Dev server only accepts N concurrent connections | Lower `--workers` to N, or scale the server |
| FAIL on first run, PASS on retry | Cold cache / lazy build | Warm up: run a single navigate-only case first |
| Screenshots missing for late steps | Action threw before screenshot call | Inspect `action_error` in `session.json` |
| Network assertion fails intermittently | Async XHR not finished when assertion fires | Insert `wait 1s` or `wait {selector}` before the assertion |

## 6. Severity reuse from `/user-test`

The severity rubric is defined once, in `../../user-test/references/assertion-guide.md` §3 (relative to this file) — that table is the single source of truth. Do not re-tabulate it here.

Parallel-specific delta: the runner's `assignSeverity()` function in `assets/uat-runner.spec.ts` is a code mirror of that same table. If you update the §3 rubric, also update `assignSeverity()` to keep the code mirror in sync.

## 7. Comparison: when to use which UAT tool

| Need | Tool |
|---|---|
| Quick one-off interactive UAT in Vietnamese | `/user-test` (interactive mode) |
| Run 1–3 cases sequentially, no Playwright | `/user-test --auto` |
| 5+ cases regression, want speed | `/uat-parallel --workers 4` |
| Multi-user flows (two contexts at once) | `/uat-parallel` |
| Visual debugging with `--headed` | `/uat-parallel --workers 1 --headed --from {one-case.md}` |
| Cross-browser (Firefox / WebKit) | `/uat-parallel --browser firefox` |
| Trace replay needed | `/uat-parallel` (always retains trace on failure) |

## 8. CI integration sketch

```yaml
# .github/workflows/uat.yml
name: UAT (parallel)
on: [pull_request]
jobs:
  uat:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: |
          # /uat-parallel installs runner files on first invocation, but
          # in CI we copy them ourselves to skip the interactive bootstrap.
          mkdir -p .astra/uat
          cp .astra-plugin/skills/uat-parallel/assets/*.ts .astra/uat/
          export UAT_SESSION_DIR="$PWD/docs/tests/uat-reports/ci-${{ github.run_id }}"
          mkdir -p "$UAT_SESSION_DIR/screenshots" "$UAT_SESSION_DIR/traces"
          npx playwright test --config .astra/uat/playwright.config.ts --workers 2 || true
          bash .astra-plugin/skills/uat-parallel/scripts/uat-parallel-report.sh \
            "$UAT_SESSION_DIR" .astra-plugin/skills/user-test/assets/report-template.html
      - uses: actions/upload-artifact@v4
        with:
          name: uat-report
          path: docs/tests/uat-reports/ci-${{ github.run_id }}/
```
