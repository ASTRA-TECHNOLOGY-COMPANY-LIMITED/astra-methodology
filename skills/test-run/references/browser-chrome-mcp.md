# Browser Procedures — Chrome DevTools MCP Mode

Per-step browser procedures for `BROWSER_MODE=chrome-mcp`, the **fallback
backend** (v5.21.0+) — used when `ego-browser` is unavailable (non-macOS hosts,
not installed), when the user names Chrome MCP explicitly, or for a single
escalated step. Return to `SKILL.md` for the overall flow, state-file handling,
and the machine-anchored pass/fail gate. All actions here use Chrome DevTools MCP
tools (`mcp__chrome-devtools__*`).

## Contents
- [General notes](#general-notes)
- [Step 5 — Basic Page Verification](#step-5--basic-page-verification)
- [Step 6 — Scenario-based Integration Testing](#step-6--scenario-based-integration-testing)
- [Step 8 — Performance Measurement](#step-8--performance-measurement)

## General notes

- The browser is auto-managed — no explicit open command; just call
  `navigate_page`.
- Snapshots return element `uid`s used by `click` / `fill` / `hover`.
- Chrome MCP is the only mode with a real performance trace
  (`performance_start_trace` / `performance_stop_trace`), so Step 8 escalates
  here even when `BROWSER_MODE` is `ego`/`cmux`.
- The MCP server is not bundled by the plugin — the user registers
  `chrome-devtools-mcp` themselves. In multi-session setups, attach one shared
  instance via `--browser-url` rather than launching per session (profile
  `SingletonLock` contention).

## Step 5 — Basic Page Verification

Skip entirely if `BROWSER_MODE=none`. Perform the following for each page.

### A. Page Load Verification

1. Navigate to the target URL with `navigate_page`.
2. Verify core content load with `wait_for`.
3. Check page structure with `take_snapshot`.

### B. Console Error Check

1. `list_console_messages` (types: `["error", "warn"]`).
2. If errors exist, get details with `get_console_message`.
3. Cross-reference with server logs to classify backend vs. frontend errors.

### C. Network Request Verification

1. `list_network_requests` (resourceTypes: `["xhr", "fetch"]`).
2. Detect failed requests (4xx, 5xx).
3. Inspect request/response details with `get_network_request`.
4. Check backend processing logs for the corresponding requests in server logs.

### D. Responsive Layout Verification

1. Desktop (1280x720) → `resize_page` + `take_snapshot`.
2. Tablet (768x1024) → `resize_page` + `take_snapshot`.
3. Mobile (375x667) → `resize_page` + `take_snapshot`.
4. Check for layout breakage at each viewport.

## Step 6 — Scenario-based Integration Testing

Skip browser-dependent scenarios if `BROWSER_MODE=none` (run API-level and
server-log tests only). Execute the Step 4 test cases in order. After each
scenario, record its result to the scenario log per SKILL.md Step 6 (this is the
machine-anchored count source — never tally from memory).

### Form Input Testing

1. Check form element `uid`s with `take_snapshot`.
2. Enter test data with `fill` / `fill_form`.
3. Click the submit button with `click`.
4. Wait for the response with `wait_for`.
5. Verify API calls with `list_network_requests`.
6. Verify request processing in server logs.
7. Verify the result screen with `take_snapshot`.

### Authentication Flow Testing

1. Navigate to the login page.
2. Attempt login with the test account.
3. Verify token issuance via network requests.
4. Verify access to authenticated pages.
5. Verify token refresh behavior on expiration.

### API Integration Testing

1. Navigate to the feature page.
2. Verify data-load requests (network).
3. Verify DB query execution in server logs.
4. Verify response data matches the screen display.
5. Perform CRUD operations and verify server logs and screen.

## Step 8 — Performance Measurement

```
1. performance_start_trace (reload=true, autoStop=true)
2. Analyze results after trace completion
3. Check Core Web Vitals (LCP, FID, CLS)
4. Identify bottlenecks and suggest improvements
```
