# Browser Procedures — cmux Built-in Browser Mode

Per-step browser commands for `BROWSER_MODE=cmux`, the **legacy backend**
(v5.21.0+ detection order: ego → Chrome MCP → cmux). Reached only when neither
`ego-browser` nor the Chrome DevTools MCP tools are available, or when the user
names `cmux` explicitly. Return to `SKILL.md` for the overall flow, state-file
handling, and the machine-anchored pass/fail gate. All cmux browser commands run
via the **Bash** tool.

## Contents
- [General notes](#general-notes)
- [Step 5 — Basic Page Verification](#step-5--basic-page-verification)
- [Step 6 — Scenario-based Integration Testing](#step-6--scenario-based-integration-testing)
- [Step 8 — Performance Measurement](#step-8--performance-measurement)

## General notes

- cmux browser commands are executed via the Bash tool.
- Use the `--snapshot-after` flag on interaction commands (click, fill, type,
  press) to auto-capture the DOM after the action.
- For network request inspection, use `cmux browser eval` with the Performance
  API, or inject a fetch interceptor.
- Performance tracing (Step 8) is not available in cmux — fall back to Chrome
  MCP for that step only, and note it in the report if Chrome MCP is unavailable.
- **Open the browser first** (cmux mode only):
  `cmux new-pane --type browser --url {target-url}` — opens a split pane.

## Step 5 — Basic Page Verification

Skip entirely if `BROWSER_MODE=none`. Perform the following for each page.

### A. Page Load Verification

```bash
cmux browser goto {target-url}
cmux browser wait --selector '{main-content-selector}' --timeout-ms 10000
cmux browser snapshot
```

### B. Console Error Check

```bash
cmux browser console list
```

1. Parse output for error/warn entries.
2. Cross-reference with server logs to classify backend vs. frontend errors.

### C. Network Request Verification

```bash
cmux browser eval 'JSON.stringify(performance.getEntriesByType("resource").filter(e => ["xmlhttprequest","fetch"].includes(e.initiatorType)).map(e => ({name:e.name, duration:e.duration, status:e.responseStatus})))'
```

1. Detect failed requests from the output.
2. For detailed inspection, inject a fetch interceptor via `cmux browser eval`.
3. Check backend processing logs for the corresponding requests in server logs.

### D. Responsive Layout Verification

```bash
cmux browser eval 'window.resizeTo(1280,720)' && cmux browser snapshot   # Desktop
cmux browser eval 'window.resizeTo(768,1024)' && cmux browser snapshot    # Tablet
cmux browser eval 'window.resizeTo(375,667)'  && cmux browser snapshot    # Mobile
```

Check for layout breakage at each viewport.

## Step 6 — Scenario-based Integration Testing

Skip browser-dependent scenarios if `BROWSER_MODE=none` (run API-level and
server-log tests only). Execute the Step 4 test cases in order. After each
scenario, record its result to the scenario log per SKILL.md Step 6 (this is the
machine-anchored count source — never tally from memory).

### Form Input Testing

```bash
cmux browser snapshot                                                # identify form selectors
cmux browser fill '{selector}' '{value}' --snapshot-after            # repeat per field
cmux browser click '{submit-selector}' --snapshot-after
cmux browser wait --selector '{result-selector}' --timeout-ms 10000
cmux browser eval 'JSON.stringify(performance.getEntriesByType("resource"))'   # verify API calls
cmux browser snapshot                                                # verify result screen
```

Verify request processing in server logs between the API call and the result
snapshot.

### Authentication Flow Testing

```bash
cmux browser goto {login-url}
cmux browser fill '{email-selector}' '{test-email}'
cmux browser fill '{password-selector}' '{test-password}'
cmux browser click '{login-button}' --snapshot-after
cmux browser eval 'document.cookie'                        # or localStorage.getItem("token")
cmux browser goto {protected-page-url}                     # verify authenticated access
```

Verify token refresh by manipulating token expiry via `cmux browser eval`.

### API Integration Testing

```bash
cmux browser goto {feature-page-url}
cmux browser eval 'JSON.stringify(performance.getEntriesByType("resource"))'   # verify data load
cmux browser snapshot                                                # response data matches screen
```

1. Verify DB query execution in server logs.
2. Perform CRUD operations via UI interactions and verify server logs + screen.

## Step 8 — Performance Measurement

Performance tracing requires the Chrome DevTools Protocol, which cmux lacks. Per
SKILL.md Step 8, use Chrome MCP (`performance_start_trace` / `performance_stop_trace`)
for this step regardless of mode. If Chrome MCP is unavailable, capture the basic
metrics below and note the limitation in the report.

```bash
cmux browser eval 'JSON.stringify(performance.timing)'
cmux browser eval 'JSON.stringify(performance.getEntriesByType("navigation")[0])'
```

1. Calculate basic metrics: TTFB, DOM Content Loaded, Full Load.
2. Note in the report: "Full Core Web Vitals (LCP, FID, CLS) not available
   without Chrome MCP."
