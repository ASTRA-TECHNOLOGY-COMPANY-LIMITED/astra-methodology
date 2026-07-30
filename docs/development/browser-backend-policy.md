# Browser Backend Policy (v5.21.0+)

**SSoT for every ASTRA skill that drives a real browser.** Skills reference this
document instead of restating the detection order or the ego helper API — a
change here is a change everywhere.

Consumers: `/test-run`, `/user-test`, `/manual-generator`, `/catalog-generator`, `/landing-page`.
Not a consumer: `/uat-parallel` (drives Playwright as a subprocess and owns its
own `BrowserContext` per worker — no MCP/ego backend involved).

## Contents
- [Detection order](#detection-order)
- [Capability matrix](#capability-matrix)
- [Action mapping](#action-mapping)
- [ego operating rules](#ego-operating-rules)
- [Escalation to Chrome MCP](#escalation-to-chrome-mcp)
- [Task Space naming](#task-space-naming)

## Detection order

**ego (default) → Chrome MCP (fallback) → cmux (legacy)**, first match wins:

1. **Necessity** — if the task needs no page rendering (API-only checks, pure
   document generation with no `{SERVICE_URL}`), set `BROWSER_MODE=none` and skip
   browser init entirely.
2. **Explicit intent** — `$ARGUMENTS` names a backend: `"Chrome MCP"` /
   `"chrome-devtools"` / `"chrome-mcp"` → `chrome-mcp`; `"ego"` / `"ego-browser"`
   / `"ego lite"` → `ego`; `"cmux"` → `cmux`. An explicit request always wins over
   auto-detection, including over the ego default.
3. **Auto-detect** — run the snippet below, then apply the Chrome MCP check:

```bash
# Shell-detectable backends only. Prints: ego | cmux | (empty)
# zsh-safe: no ${!var} indirection, no `local status`.
if command -v ego-browser >/dev/null 2>&1; then
  echo ego
elif command -v cmux >/dev/null 2>&1 && cmux ping >/dev/null 2>&1; then
  echo cmux
else
  echo ""
fi
```

- Snippet printed `ego` → `BROWSER_MODE=ego`.
- Snippet printed nothing **and** `mcp__chrome-devtools__*` tools are present in
  this session → `BROWSER_MODE=chrome-mcp`.
- Snippet printed `cmux` → prefer `chrome-mcp` when the MCP tools are present;
  otherwise `BROWSER_MODE=cmux`.
- Nothing available → report the gap to the user (`ego-browser` install or
  `chrome-devtools-mcp` registration) rather than silently degrading; a skill
  whose only output is screenshots must not report success without them.

> **Why shell-detect ego but not Chrome MCP**: MCP tool availability is a
> property of the *session's tool list*, not of `PATH` — the model reads it
> directly. `ego-browser` and `cmux` are binaries, so a `command -v` probe is the
> authoritative check.

Announce the resolved mode once, before the first browser action:
> **Browser backend**: {ego (lite) / Chrome DevTools MCP / cmux / none}

## Capability matrix

| Capability | ego (lite) | Chrome MCP | cmux |
|---|---|---|---|
| Availability | macOS only, `ego-browser` binary | any OS, user-registered MCP server | inside cmux panes |
| Multi-session safety | isolated Task Space per agent — no `SingletonLock` contention | shared profile; needs `--browser-url` attach | pane-scoped |
| Login-state inheritance | **yes** (user's real session) | no (dedicated profile) | no |
| Driven through | Bash heredoc (`ego-browser nodejs`) | MCP tool calls | Bash commands |
| Console messages | ⚠️ no helper — CDP collector required | native | native |
| Performance trace | ❌ | **only backend with a real trace** | ❌ |
| Screenshot after scroll | ⚠️ blank-frame caveat (see below) | fine | fine |

## Action mapping

| Action | ego (inside one `ego-browser nodejs` heredoc) | Chrome MCP tool | cmux (Bash) |
|---|---|---|---|
| **Open** | `useOrCreateTaskSpace('{space}')` → `openOrReuseTab({url}, { wait: true })` | (auto-managed) | `cmux new-pane --type browser --url {url}` |
| **Navigate** | `gotoAndWait({url}, { timeout: 20 })` | `navigate_page` | `cmux browser goto {url}` |
| **Snapshot (DOM)** | `snapshotText()` → `[ref=N, loc=…]` | `take_snapshot` | `cmux browser snapshot` |
| **Screenshot** | `captureScreenshot('{abs-path}')` | `take_screenshot` | `cmux browser screenshot` |
| **Click** | `click('@N' / '{css}' / [x,y], { label })` | `click` | `cmux browser click '{sel}'` |
| **Fill input** | `fillInput('{sel}', '{text}')` | `fill` / `fill_form` | `cmux browser fill '{sel}' '{text}'` |
| **Press key / type** | `pressKey('{key}')` / `typeText('{text}')` | `press_key` | `cmux browser press {key}` |
| **Hover** | `hover('{sel}')` | `hover` | `cmux browser hover '{sel}'` |
| **Wait** | `waitForElement('{css}')` / `wait({sec})` / `waitForNetworkIdle()` | `wait_for` | `cmux browser wait --selector '{css}' --timeout-ms {ms}` |
| **Console errors** | ⚠️ no helper — `cdp('Runtime.enable')` + `cdp('Log.enable')` before navigation, then `drainEvents()` | `list_console_messages` / `get_console_message` | `cmux browser console list` |
| **JS evaluate** | ``js(String.raw`(() => { … })()`)`` | `evaluate_script` | `cmux browser eval '{script}'` |
| **Dialog** | `cdp('Page.handleJavaScriptDialog', { accept: true })` | `handle_dialog` | `cmux browser dialog accept` |
| **Tabs** | `listTabs()` / `switchTab({id})` / `openOrReuseTab({url})` | `list_pages` / `select_page` / `new_page` | `cmux browser tab list` / `tab switch {i}` |
| **Page info** | `pageInfo()` (url, title, viewport, dialog) | via `evaluate_script` | `cmux browser get url` |
| **Scroll** | `scrollBy({px})` / `scrollToBottomUntil(fn)` | via `evaluate_script` | `cmux browser scroll --dy {px}` |
| **Viewport / device** | `cdp('Emulation.setDeviceMetricsOverride', {…})` → clear with `cdp('Emulation.clearDeviceMetricsOverride')` | `resize_page` / `emulate` | `cmux browser eval 'window.resizeTo(w,h)'` |
| **Network requests** | `drainEvents()` / `js('performance.getEntriesByType("resource")')` | `list_network_requests` / `get_network_request` | `cmux browser eval '…'` |
| **Performance trace** | ❌ escalate | `performance_start_trace` / `performance_stop_trace` | ❌ escalate |
| **Close** | `completeTaskSpace('{space}', { keep: false })` | `close_page` (optional) | close the pane |

## ego operating rules

Load-bearing conventions — violating them produces silent no-ops, not errors.

1. **One heredoc = one round.** The Node runtime exits after each heredoc and
   keeps no state. Every heredoc re-selects the space first:
   `const task = await useOrCreateTaskSpace('{space}')`.
2. **`cliLog(...)` is the only output channel.** A returned or `console.log`-ed
   value never reaches the transcript. Anything you must *read* — an assertion
   target, a captured path, a page title — has to be `cliLog`-ed.
3. **Seconds, not milliseconds.** Waits and `timeout` values are in seconds;
   only `…Ms`-suffixed parameters take milliseconds.
4. **`@N` refs expire with the snapshot.** They are valid only for the most
   recent `snapshotText()` in the *same* heredoc. Across rounds, use the `loc=…`
   value or a plain CSS selector.
5. **`captureScreenshot(absolutePath)` takes a path and returns it.** Verified on
   ego lite 0.4.5.8: the helper writes the PNG and resolves to the path string,
   so `cliLog(await captureScreenshot(p))` both saves and confirms the file. A
   relative path is not resolved against the worktree — always pass an absolute
   one. Called with no argument it still works for ad-hoc inspection, but a
   deliverable or a piece of evidence must go to a known path.
6. **Screenshot blank-frame caveat** (reported on ego lite 0.4.5.5; the guard is
   free, so keep applying it) — `captureScreenshot()` can return a blank frame
   when `scrollY != 0`. Scroll to the top (`js('window.scrollTo(0,0)')`) before
   capturing, and re-take a blank frame rather than shipping it.
7. **`drainEvents()` returns a CDP event array** — each entry is
   `{ method, params, sessionId }`, e.g. `Runtime.consoleAPICalled`
   (`params.type`, `params.args[].value`), `Network.requestWillBeSent`
   (`params.request.method`, `params.request.url`), `Network.responseReceived`
   (`params.response.url`, `params.response.status`). It **consumes** the queue,
   so one drain per logical step keeps the payload attributable to that step.
   Enable the domains (`Runtime.enable` / `Log.enable` / `Network.enable`) before
   the navigation you want to observe.
8. **The user's browser extensions are in the evidence.** Login-state
   inheritance also inherits the profile's extensions: a drain on a plain
   `example.com` load returned four `Network.responseReceived` entries, three of
   them `chrome-extension://…/contentscript.js`. Before asserting on network or
   console data, drop entries whose URL starts with `chrome-extension://` (and
   treat extension-sourced console errors as noise, per the UAT severity rules) —
   otherwise "no failed requests" and "no console errors" fail for reasons that
   have nothing to do with the app under test. This noise does not exist in
   Chrome MCP mode with a dedicated profile.
9. **Handoff is a hard stop.** If a helper fails with "user is controlling" /
   "inactive space", do not retry and do not call `takeOverTaskSpace` — the user
   has the browser. Report the interruption and stop; resuming is the user's call.
10. **Login-state inheritance is inherited, not clean.** The space carries the
   user's real session for the target origin. Advantage: SSO-gated internal
   services need no re-login. Trap: an auth flow may start already logged in, and
   writes land in the **real account**. Before any auth-flow or write-heavy
   scenario, assert the starting state explicitly; clear the session
   origin-scoped (never `Network.clearBrowserCookies` — it is browser-wide):

   ```bash
   ego-browser nodejs <<'EOF'
   const task = await useOrCreateTaskSpace('{space}')
   await openOrReuseTab('{target-url}', { wait: true, timeout: 20 })
   const origin = await js(String.raw`(() => location.origin)()`)
   await cdp('Storage.clearDataForOrigin', { origin, storageTypes: 'cookies,local_storage' })
   await js(String.raw`(() => { sessionStorage.clear(); return true })()`)
   await gotoAndWait('{target-url}', { timeout: 20, settle: 1 })
   cliLog('session cleared; state: ' + JSON.stringify(await pageInfo()))
   EOF
   ```

   Never run destructive scenarios against a production origin in ego mode —
   switch to `chrome-mcp` with a dedicated test profile.
11. **Always close the space.** The final heredoc of a workflow runs
   `completeTaskSpace('{space}', { keep: false })`; an un-closed space leaves
   orphaned browser windows behind. This must run on every exit path, including
   failure.

## Escalation to Chrome MCP

Two capabilities have no ego equivalent. When the running mode is `ego` (or
`cmux`) and one of them is required:

| Need | Rule |
|---|---|
| **Performance trace** (Core Web Vitals: LCP, CLS, …) | Use Chrome MCP for that step regardless of `BROWSER_MODE`. If the MCP server is not registered, capture basic metrics via `performance.getEntriesByType('navigation'\|'paint')` (TTFB / DCL / Load / FCP) and state the limitation verbatim in the report: "Full Core Web Vitals unavailable ({mode} mode, Chrome MCP not connected)". |
| **Console message list** | Install the CDP collector *before* navigation (`Runtime.enable` + `Log.enable`, then `drainEvents()`). A collector installed after navigation misses everything already emitted. If it yields nothing for a page known to log errors, fall back to an in-page `window.addEventListener('error', …)` collector and note the limitation — never record a silent "0 errors". |

Escalation is per-step, not per-session: the rest of the workflow stays on the
detected backend.

## Deliverable screenshot capture

Shared recipe for `/manual-generator` and `/catalog-generator`, whose screenshots
are **published artifacts**, not test evidence. Quality bar accordingly: no blank
frames, no cookie banners, no chat widgets.

Backend-neutral sequence per screen:

1. **Navigate** to the target route, then **wait** for the main-content selector
   (10–15 s) — never capture on a bare navigation return.
2. **Clean the UI** — inject a stylesheet hiding overlays
   (`[class*="cookie"]`, `[class*="chat"]`, `[class*="intercom"]`,
   `.popup-overlay`, `[class*="notification-bar"]`). Give the injected `<style>`
   an id so step 6 can remove it.
3. **Annotate** when the skill calls for it (highlight outline + numbered badge);
   the exact snippets stay in the owning skill's references.
4. **Scroll to the top** — mandatory in ego mode (blank-frame caveat), harmless
   elsewhere.
5. **Capture** to an **absolute** path.
6. **Remove** the injected style/annotation nodes before the next capture, so
   they never leak into the following screenshot.

ego does all six in **one heredoc** per screen:

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('{space}')
await gotoAndWait('{url}', { timeout: 20, settle: 1 })
await waitForElement('{main-content-selector}')
await js(String.raw`(() => {
  const s = document.createElement('style'); s.id = 'astra-capture-style'
  s.textContent = '[class*="cookie"],[class*="chat"],[class*="intercom"],.popup-overlay,[class*="notification-bar"]{display:none !important}'
  document.head.appendChild(s); window.scrollTo(0, 0); return true
})()`)
await wait(1)
await captureScreenshot('{ABS_OUTPUT_DIR}/{name}.png')
await js(String.raw`(() => { const s = document.getElementById('astra-capture-style'); if (s) s.remove(); return true })()`)
cliLog('captured {name}: ' + JSON.stringify(await pageInfo()))
EOF
```

**Responsive variants** — override the viewport, capture, then clear the override
so later captures are not silently mobile-sized:

```bash
await cdp('Emulation.setDeviceMetricsOverride', { width: 768, height: 1024, deviceScaleFactor: 1, mobile: false })
// … capture …
await cdp('Emulation.clearDeviceMetricsOverride')
```

Chrome MCP equivalent: `resize_page` per viewport, restoring 1280×800 at the end.

**Verify before shipping.** A screenshot is a deliverable — confirm each file
exists and is non-blank (`pageInfo()` reporting `w: 0`/`h: 0`, or a zero-byte
/uniform-color PNG, means re-take). If capture is impossible for a screen, the
skill continues in document-only mode for that screen and **says so in the
output**; a manual that silently ships without its screenshots is a failure
reported as success.

**Interaction captures** (multi-step flows) use the Action mapping table above
for fill/click/press. Prefer read-only flows; in ego mode remember the session is
the user's real one — never drive a write flow against production data.

## Task Space naming

One space per skill invocation, stable across all its heredocs, closed at the end:

| Skill | Space name |
|---|---|
| `/test-run` | `astra test-run sprint-{N}` |
| `/user-test` | `astra user-test {SESSION_ID}` |
| `/manual-generator` | `astra manual {feature-name}` |
| `/catalog-generator` | `astra catalog {catalog-name}` |
| `/landing-page` | `astra landing {slug}` |

Distinct names keep concurrent sprint sessions from sharing a space (the
multi-session isolation that motivates the ego default in the first place).
