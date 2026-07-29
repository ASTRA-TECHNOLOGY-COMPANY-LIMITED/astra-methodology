# UAT Procedures — ego (lite) Mode

Per-step procedures for `UAT_BACKEND=ego`, the **default backend** (v5.21.0+).
Return to `SKILL.md` for the pipeline, and to `assertion-guide.md` for assertion
syntax and severity rules — this file only translates those assertions into ego
helper calls.

**Read first**: the *ego operating rules* in
`$CLAUDE_PLUGIN_ROOT/docs/development/browser-backend-policy.md` (one heredoc =
one round, `cliLog` as the only output channel, seconds-not-milliseconds, `@N`
ref expiry, blank-screenshot-on-scroll, handoff-is-a-hard-stop, login-state
inheritance, mandatory `completeTaskSpace`).

## UAT-specific rules

- **Task Space**: `astra user-test {SESSION_ID}` — same name for every heredoc of
  the session; Step 4 closes it.
- **An unreadable assertion is a FAIL, not a PASS.** Every value an assertion
  compares against must be `cliLog`-ed and read back. If a helper returns nothing
  usable, record the step as FAIL with the observed value `"(not readable)"`
  rather than assuming success.
- **Login-state inheritance is the top UAT trap.** A registration or login case
  will start **already authenticated as the real user**, so the flow silently
  short-circuits to a dashboard and the case reports PASS. Before the first step
  of any case whose `feature` involves auth (`dang-ky`, `dang-nhap`, `auth`,
  `login`, `signup`, `register`), run the origin-scoped session-clearing block
  from the policy doc against `base_url`. Test data written by any case lands in
  the **real account** — never point ego mode at a production `base_url`.

## Session start — open the space and install collectors

Console and network assertions need CDP domains enabled **before** the first
navigation; a collector installed later misses everything already emitted.

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('astra user-test {SESSION_ID}')
await openOrReuseTab('about:blank', { wait: true })
await cdp('Runtime.enable')
await cdp('Log.enable')
await cdp('Network.enable')
cliLog('uat space ready')
EOF
```

## Step execution template

One heredoc per UAT step: perform the action, screenshot, then emit every value
the step's assertions need. `drainEvents()` empties the queue, which matches the
"since the step started" semantics in `assertion-guide.md` exactly — one drain
per step, and the drained payload belongs to that step only.

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('astra user-test {SESSION_ID}')

// --- A. Action (pick one; see the mapping table below) ---
await gotoAndWait('{url}', { timeout: 20, settle: 1 })

// --- B. Screenshot (every step, PASS or FAIL) ---
await js(String.raw`(() => { window.scrollTo(0, 0); return true })()`)   // blank-frame guard
await captureScreenshot('{ABS_SESSION_DIR}/screenshots/step-{NN}-{slug}.png')

// --- C. Assertion inputs ---
cliLog('PAGEINFO ' + JSON.stringify(await pageInfo()))                   // url / title
cliLog('EVENTS '   + JSON.stringify(await drainEvents()))                // console + network
cliLog('DOM '      + await snapshotText())                               // element presence
EOF
```

`{ABS_SESSION_DIR}` must be an **absolute** path — `captureScreenshot` does not
resolve relative paths against the worktree. It returns the saved path, so
`cliLog(await captureScreenshot(p))` doubles as the write confirmation.

## Action mapping

| Case-file action | ego call |
|---|---|
| `navigate {url}` | `gotoAndWait('{url}', { timeout: 20, settle: 1 })` — first navigation of the session uses `openOrReuseTab('{url}', { wait: true, timeout: 20 })` |
| `click {selector}` | `click('{selector}', { label: '{step_name}' })` |
| `fill {selector} value={value}` | `fillInput('{selector}', '{value}')` |
| `wait {ms}` | `wait({seconds})` — **convert**: the case file writes milliseconds, ego takes seconds |
| `wait {selector}` | `waitForElement('{selector}')` |
| `press {key}` | `pressKey('{key}')` |
| `hover {selector}` | `hover('{selector}')` |

Replace a literal `{timestamp}` in any value with `Date.now()` inside the heredoc
(it is Node — `Date.now()` is available there) before passing it to `fillInput`.

After a submit-like action, add `await waitForNetworkIdle()` before section B so
the screenshot and the drained events cover the completed request.

## Assertion evaluation

`EVENTS` is an array of CDP events shaped `{ method, params, sessionId }`
(verified on ego lite 0.4.5.8). Exact paths:

| Assertion | Source in the drained output |
|---|---|
| `url: equals\|contains\|matches` | `PAGEINFO`'s `url` field. |
| `dom: {sel} exists\|visible\|contains\|count` | Prefer an explicit probe over reading the snapshot — see the DOM probe below. `:has-text(...)` is non-standard CSS: implement it in the probe by scanning `textContent`. |
| `dom: title contains` | `PAGEINFO`'s `title` field. |
| `console: no error\|no warning\|contains` | `method === 'Runtime.consoleAPICalled'` → `params.type` (`'error'` / `'warning'`), text in `params.args[].value`; plus `Runtime.exceptionThrown` and `Log.entryAdded`. |
| `network: {METHOD} {path} → {status}` | `method === 'Network.responseReceived'` → `params.response.url`, `params.response.status`; the HTTP method comes from the paired `Network.requestWillBeSent` (`params.request.method`, matched on `params.requestId`). |
| `network: no failed requests` | Same, filtered to `params.response.status >= 400`. |

> **Filter out the user's extensions first.** The Task Space inherits the real
> profile, so extensions inject their own requests and console output: a drain on
> a plain page load returned four responses, three of them
> `chrome-extension://…/contentscript.js`. **Drop every event whose URL starts
> with `chrome-extension://` before evaluating network assertions**, and treat
> extension-sourced console errors per the extension rule in
> `assertion-guide.md` §2.4 (report at LOW, never as an app defect). Without this
> filter, `network: no failed requests` and `console: no error` fail for reasons
> unrelated to the app under test.

**DOM probe** — deterministic, and returns exactly what the assertion compares:

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('astra user-test {SESSION_ID}')
cliLog('PROBE ' + await js(String.raw`(() => {
  const el = document.querySelector('{selector}')
  if (!el) return JSON.stringify({ exists: false })
  return JSON.stringify({
    exists: true,
    visible: el.offsetParent !== null,
    text: (el.textContent || '').trim().slice(0, 200),
    value: 'value' in el ? el.value : null,
    count: document.querySelectorAll('{selector}').length,
  })
})()`))
EOF
```

**Network fallback.** `Network.*` events are delivered as long as
`cdp('Network.enable')` ran before the navigation (verified). If a drain comes
back without them anyway — collectors installed too late, or a step that never
navigated — fall back to the Performance API and record the limitation in
`issues.md`; never treat an unverifiable network assertion as PASS:

```bash
cliLog('PERF ' + await js(String.raw`(() => JSON.stringify(
  performance.getEntriesByType('resource')
    .filter(e => ['xmlhttprequest','fetch'].includes(e.initiatorType))
    .map(e => ({ name: e.name, status: e.responseStatus, duration: Math.round(e.duration) }))))()`))
```

`responseStatus` is only populated for same-origin or `Timing-Allow-Origin`
responses. When it is `undefined`, the status assertion is **not verifiable** —
mark the step FAIL with actual `"status not observable (CORS-restricted)"`, or
re-run that case under `chrome-mcp`, where `list_network_requests` returns the
real status.

## Session end

Runs on every exit path, including an aborted run:

```bash
ego-browser nodejs <<'EOF'
await completeTaskSpace('astra user-test {SESSION_ID}', { keep: false })
cliLog('uat space closed')
EOF
```
