# Browser Procedures — ego (lite) Mode

Per-step browser procedures for `BROWSER_MODE=ego`. Return to `SKILL.md` for the
overall flow, state-file handling, and the machine-anchored pass/fail gate. Every
action here runs through the **Bash** tool as an `ego-browser nodejs` heredoc.

## Contents
- [General notes](#general-notes)
- [Login-state inheritance — read before auth testing](#login-state-inheritance--read-before-auth-testing)
- [Step 5 — Basic Page Verification](#step-5--basic-page-verification)
- [Step 6 — Scenario-based Integration Testing](#step-6--scenario-based-integration-testing)
- [Step 8 — Performance Measurement](#step-8--performance-measurement)

## General notes

- **One heredoc = one round.** The Node runtime exits after each heredoc and
  keeps no state, so every heredoc starts by re-selecting the space:
  `const task = await useOrCreateTaskSpace('astra test-run sprint-{N}')`. Reuse
  the *same* space name for the whole `/test-run` invocation.
- **`cliLog(...)` is the only output channel.** A value that is merely returned
  or `console.log`-ed never reaches the transcript — and a scenario whose result
  you cannot read is a `SKIP`, not a `PASS` (SKILL.md Step 11 anti-fabrication
  rule).
- Waits and `timeout` values are in **seconds** (only `…Ms` parameters are
  milliseconds).
- `@N` refs are valid only for the most recent `snapshotText()`. For anything
  referenced across rounds, use the `loc=…` value from the snapshot or a plain
  CSS selector.
- `js()` runs in the page; navigation, waits and `cliLog` belong in the heredoc
  body. Wrap multi-step page logic in one self-invoking closure and return once.
  Use `String.raw` for regex-bearing sources.
- **Handoff is a hard stop for automated testing.** If a helper fails with "user
  is controlling" / "inactive space", do **not** retry and do **not** call
  `takeOverTaskSpace` — record the remaining scenarios as `SKIP`, run the Step 10
  cleanup, and report. `/test-run` is a machine gate; a human-assisted retry is
  the user's call, not the model's.
- **Known caveats (ego lite 0.4.5.5)** — `captureScreenshot()` can return a blank
  frame when the page is scrolled (`scrollY != 0`); scroll back to the top
  (`scrollBy(-999999)` or `js('window.scrollTo(0,0)')`) before capturing, and
  discard/re-take a blank frame rather than filing it as evidence. There is no
  performance-trace helper (see Step 8), and no console-message helper (see
  Step 5-B).
- Screenshots taken as evidence go under `docs/tests/test-reports/assets/`;
  pass an absolute path to `captureScreenshot(...)`.

## Login-state inheritance — read before auth testing

An ego task space **inherits the user's real login state** for the target
origin. That is the mode's main advantage (no re-login on internal/staging
systems behind SSO) and its main trap for `/test-run`:

- An authentication scenario may start **already logged in as the real user**,
  making a broken login flow look like a `PASS`.
- Test data written during a scenario lands in the **real account**.

Rules for `BROWSER_MODE=ego`:

1. Before any auth-flow scenario, assert the starting state explicitly and log
   it — never assume a clean session.
2. If the target origin already carries a session and the scenario is about
   *logging in*, clear it first (below) or record the scenario as `SKIP` with the
   reason; do not report an inherited session as a login success.
3. Never run destructive or write-heavy scenarios against a production origin in
   this mode — switch to `chrome-mcp`/`cmux` with a dedicated test profile.

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('astra test-run sprint-{N}')
await openOrReuseTab('{target-url}', { wait: true, timeout: 20 })
// Clear the inherited session for this origin before login-flow scenarios
await cdp('Network.clearBrowserCookies')
await js(String.raw`(() => { localStorage.clear(); sessionStorage.clear(); return true })()`)
await gotoAndWait('{target-url}', { timeout: 20, settle: 1 })
cliLog('session cleared; starting state: ' + JSON.stringify(await pageInfo()))
EOF
```

## Step 5 — Basic Page Verification

Skip entirely if `BROWSER_MODE=none`. Perform the following for each page.

### A. Page Load Verification

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('astra test-run sprint-{N}')
await openOrReuseTab('{target-url}', { wait: true, timeout: 20 })
await waitForElement('{main-content-selector}')
cliLog(JSON.stringify(await pageInfo()))
cliLog(await snapshotText())
EOF
```

`pageInfo()` resolving to `{ dialog: … }` means a native dialog is blocking page
JS — handle it with `cdp('Page.handleJavaScriptDialog', { accept: true })` first.
If it reports `w: 0` / `h: 0`, fix the viewport before any screenshot or
coordinate action.

### B. Console Error Check

ego has no console-message helper, so **install a collector before the page
loads** — a collector injected after navigation misses everything already
emitted:

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('astra test-run sprint-{N}')
await openOrReuseTab('about:blank', { wait: true })
await cdp('Runtime.enable')
await cdp('Log.enable')
await gotoAndWait('{target-url}', { timeout: 20, settle: 2 })
// Console/error entries surface as CDP events on the page event queue
cliLog(JSON.stringify(await drainEvents(), null, 2))
EOF
```

Cross-reference the entries with the server logs to classify backend vs.
frontend errors. If `drainEvents()` returns no console entries for a page you
know logs errors, fall back to an in-page collector installed via
`js('window.addEventListener("error", …)')` before navigation, and note the
limitation in the report rather than recording a silent "0 errors".

### C. Network Request Verification

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('astra test-run sprint-{N}')
const reqs = await js(String.raw`(() => performance.getEntriesByType('resource')
  .filter(e => ['xmlhttprequest','fetch'].includes(e.initiatorType))
  .map(e => ({ name: e.name, duration: Math.round(e.duration), status: e.responseStatus })))()`)
cliLog(JSON.stringify(reqs.filter(r => !r.status || r.status >= 400), null, 2))
EOF
```

`responseStatus` requires a same-origin or CORS-exposed Timing-Allow-Origin
response; for anything it cannot see, verify the request in the server logs
instead of assuming success.

### D. Responsive Layout Verification

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('astra test-run sprint-{N}')
for (const [w, h, name] of [[1280,720,'desktop'], [768,1024,'tablet'], [375,667,'mobile']]) {
  await cdp('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: w < 768 })
  await wait(1)
  await js(String.raw`(() => { window.scrollTo(0, 0); return true })()`)   // blank-frame guard
  await captureScreenshot(`{abs-report-assets-dir}/${name}.png`)
  cliLog(name + ': ' + JSON.stringify(await pageInfo()))
}
await cdp('Emulation.clearDeviceMetricsOverride')
EOF
```

Check each viewport for layout breakage, then confirm the captured files are
non-blank before citing them as evidence.

## Step 6 — Scenario-based Integration Testing

Skip browser-dependent scenarios if `BROWSER_MODE=none`. Execute the Step 4 test
cases in order. After each scenario, append its result to the scenario log per
SKILL.md Step 6 — that log is the machine-anchored count source; never tally from
memory. Batch one scenario per heredoc so a failure is attributable.

### Form Input Testing

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('astra test-run sprint-{N}')
cliLog(await snapshotText())                       // identify refs/loc for the form
await fillInput('{field-selector}', '{value}')     // repeat per field
await click('{submit-selector}', { label: 'submit test form' })
await waitForNetworkIdle()
await waitForElement('{result-selector}')
cliLog(JSON.stringify(await pageInfo()))
cliLog(await snapshotText())                       // verify the result screen
EOF
```

Verify request processing in the server logs between the submit and the result
snapshot.

### Authentication Flow Testing

Run the session-clearing block above first (see
[Login-state inheritance](#login-state-inheritance--read-before-auth-testing)).

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('astra test-run sprint-{N}')
await gotoAndWait('{login-url}', { timeout: 20 })
await fillInput('{email-selector}', '{test-email}')
await fillInput('{password-selector}', '{test-password}')
await click('{login-button}', { label: 'submit login' })
await waitForNetworkIdle()
cliLog('token: ' + await js(String.raw`(() => localStorage.getItem('token') || document.cookie)()`))
await gotoAndWait('{protected-page-url}', { timeout: 20 })
cliLog(JSON.stringify(await pageInfo()))           // authenticated access verified
EOF
```

If the flow requires a real captcha / 2FA, the correct outcome is `SKIP` with the
reason recorded — not a handoff-and-continue.

### API Integration Testing

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('astra test-run sprint-{N}')
await gotoAndWait('{feature-page-url}', { timeout: 20 })
await waitForNetworkIdle()
cliLog(await js(String.raw`(() => JSON.stringify(performance.getEntriesByType('resource').slice(-20)))()`))
cliLog(await snapshotText())                       // response data matches the screen
EOF
```

1. Verify DB query execution in the server logs.
2. Perform CRUD operations through the UI and verify server logs + screen.

## Step 8 — Performance Measurement

ego exposes raw CDP but no trace helper, and ASTRA does not treat a hand-rolled
`Tracing.*` session as a supported path. Per SKILL.md Step 8, use Chrome MCP
(`performance_start_trace` / `performance_stop_trace`) for this step regardless
of mode. If Chrome MCP is unavailable, capture the basic metrics below and state
the limitation in the report.

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('astra test-run sprint-{N}')
cliLog(await js(String.raw`(() => JSON.stringify(performance.getEntriesByType('navigation')[0]))()`))
cliLog(await js(String.raw`(() => JSON.stringify(performance.getEntriesByType('paint')))()`))
EOF
```

1. Calculate basic metrics: TTFB, DOM Content Loaded, Full Load, FCP.
2. Note in the report: "Full Core Web Vitals (LCP, FID, CLS) not available
   without Chrome MCP."
