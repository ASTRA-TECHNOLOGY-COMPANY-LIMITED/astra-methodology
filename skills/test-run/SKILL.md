---
name: test-run
description: "Launches the server and performs integration testing with a real browser. Supports cmux built-in browser (primary) and Chrome MCP (fallback). Automatically conducts server log monitoring, page verification, API behavior checks, and performance measurement."
argument-hint: "[target URL or scenario] [Chrome MCP]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Skill, AskUserQuestion, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__click, mcp__chrome-devtools__fill, mcp__chrome-devtools__fill_form, mcp__chrome-devtools__press_key, mcp__chrome-devtools__hover, mcp__chrome-devtools__list_console_messages, mcp__chrome-devtools__get_console_message, mcp__chrome-devtools__list_network_requests, mcp__chrome-devtools__get_network_request, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__wait_for, mcp__chrome-devtools__emulate, mcp__chrome-devtools__resize_page, mcp__chrome-devtools__list_pages, mcp__chrome-devtools__select_page, mcp__chrome-devtools__new_page, mcp__chrome-devtools__handle_dialog, mcp__chrome-devtools__performance_start_trace, mcp__chrome-devtools__performance_stop_trace, mcp__chrome-devtools__performance_analyze_insight
---

# ASTRA Integration Testing

Launches the server and performs integration testing in a real browser environment.
Supports two browser backends: **cmux built-in browser** (primary) and **Chrome MCP** (fallback).
The LLM directly monitors server logs to detect errors and verifies page behavior.

## Execution Procedure

### Step 0: Worktree Context & Port Isolation (v5.0+)

Testing **runs on the current branch of the current worktree**. The previous policy of forcing a dev merge is no longer needed in the sprint worktree model — merging is `/pr-merge`'s responsibility.

#### A. Detect Worktree Context

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
if [ -z "$PLUGIN_ROOT" ] || [ ! -f "$PLUGIN_ROOT/scripts/worktree-helpers.sh" ]; then
  echo "ERROR: CLAUDE_PLUGIN_ROOT not found. Check the plugin cache path." >&2
  exit 1
fi
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"

CURRENT_BRANCH=$(git branch --show-current)
if astra_is_isolated_worktree; then
  IN_SPRINT_WT=1
else
  IN_SPRINT_WT=0
fi
```

| Context | Handling |
|---------|----------|
| Sprint worktree (isolated, sprint branch) | Test on current branch as-is (normal) |
| Main worktree + work branch (compatibility) | Test on current branch as-is |
| Main worktree + shared branch (dev/main/staging/master) | Test on current branch as-is (one-off fallback) |

> **v5.0+ important**: This skill does not perform dev merge/push. The previous Step 12/13 dev commit/push and `/pr-merge --staging` chaining have been removed; after sprint integration testing completes, the user invokes `/pr-merge` to enter the merge cycle.

#### B. Commit Unstaged Changes (if any)

If there are uncommitted changes on the current branch before testing, create a wip commit (so that file changes during testing do not introduce non-determinism):

```bash
if [ -n "$(git status --porcelain)" ]; then
  git add -u
  git commit -m "wip: pre-test commit on ${CURRENT_BRANCH}"
fi
```

> **Note**: `git add -u` only stages already-tracked files. Untracked files such as `.env`, `node_modules/`, and build artifacts are not included.

#### C. Load Worktree Port Env

A sprint worktree contains the `.astra-worktree.env` written by `/sprint-init`. Source this file to apply sprint-specific ports:

```bash
WT_ENV="$(astra_worktree_env_path "$(pwd)")"
if [ -f "$WT_ENV" ]; then
  # shellcheck disable=SC1090
  set -a; . "$WT_ENV"; set +a
  echo "Sprint worktree env loaded: PORT=$PORT (base=$ASTRA_PORT_BASE)"
else
  # Main worktree or v4.x-compatible case — keep default port
  echo "No .astra-worktree.env — using default port"
fi
```

#### D. Pre-launch Port Availability Check

Before starting the server, verify that *every* per-stack port defined in the env file is available; abort if any one is occupied (so as not to kill another worktree or external process). Checking only a single `PORT` cannot preemptively detect runtime conflicts in Spring Boot (`SERVER_PORT`), Django/FastAPI (`DJANGO_PORT`/`FASTAPI_PORT`), or Vite (`VITE_PORT`) stacks.

```bash
# If the default PORT is empty, fall back to 3000 (env-not-loaded fallback)
: "${PORT:=3000}"

# Check every candidate port defined in env. Skip undefined/empty values.
PORT_CHECK_FAILED=0
for var in PORT SERVER_PORT DJANGO_PORT FASTAPI_PORT VITE_PORT; do
  port_val="${!var:-}"
  [ -z "$port_val" ] && continue
  if astra_port_in_use "$port_val"; then
    echo "ERROR: $var=$port_val is already in use." >&2
    PORT_CHECK_FAILED=1
  fi
done

if [ "$PORT_CHECK_FAILED" = "1" ]; then
  echo "       Stop the dev server in another worktree or any external process, then retry." >&2
  echo "       Check the occupying process with: lsof -i :<PORT>" >&2
  exit 1
fi

TEST_PORT="$PORT"   # Representative port used from Step 2 onward (see Step 2 table for actual per-stack port)
echo "Port availability OK (PORT=$PORT, SERVER_PORT=${SERVER_PORT:-—}, DJANGO_PORT=${DJANGO_PORT:-—}, FASTAPI_PORT=${FASTAPI_PORT:-—}, VITE_PORT=${VITE_PORT:-—})"
```

> **Test execution branch**: `${CURRENT_BRANCH}` (worktree: `$(pwd)`, port: `$TEST_PORT`)

---

### Step 1: Detect Browser Environment

Determine which browser backend to use for testing:

#### A. Check User Intent

Parse `$ARGUMENTS` for explicit browser preference:
- If arguments contain **"Chrome MCP"** or **"chrome-devtools"** → force **Chrome MCP** mode
- Otherwise → proceed to auto-detection

#### B. Check Browser Necessity

Not all test scenarios require a browser. Evaluate test targets:
- **Browser required**: Page rendering, UI interactions, form submissions, responsive layout, visual verification, E2E scenarios
- **Browser NOT required**: API-only testing, server health checks, database verification, log analysis only

If browser is NOT required, skip browser initialization entirely and proceed with server-side testing only (Steps 2-4, 7, 9-13). Set `BROWSER_MODE=none`.

#### C. Auto-detect cmux Availability

```bash
# Check if cmux is available and running
which cmux >/dev/null 2>&1 && cmux ping >/dev/null 2>&1
```

- If cmux is available and responds to ping → set `BROWSER_MODE=cmux`
- If cmux is not available → set `BROWSER_MODE=chrome-mcp`

#### D. Browser Mode Summary

| Mode | Condition | Browser Tool |
|------|-----------|-------------|
| `cmux` | cmux available + no explicit Chrome MCP request | cmux browser commands (Bash) |
| `chrome-mcp` | cmux unavailable OR user requested "Chrome MCP" | Chrome DevTools MCP tools |
| `none` | No browser testing needed | No browser launched |

Display the detected mode to the user:
> **Browser environment detected**: {cmux browser / Chrome MCP / no browser needed}

---

### Step 1-A: Browser Command Reference

Use this mapping table throughout all browser interaction steps. Choose the correct column based on `BROWSER_MODE`:

| Action | cmux Browser (Bash) | Chrome MCP Tool |
|--------|---------------------|-----------------|
| **Open browser** | `cmux new-pane --type browser --url {url}` | (auto-managed) |
| **Navigate** | `cmux browser goto {url}` | `navigate_page` |
| **Snapshot (DOM)** | `cmux browser snapshot` | `take_snapshot` |
| **Screenshot** | `cmux browser screenshot` | `take_screenshot` |
| **Click** | `cmux browser click '{selector}'` | `click` |
| **Fill input** | `cmux browser fill '{selector}' '{text}'` | `fill` |
| **Press key** | `cmux browser press {key}` | `press_key` |
| **Hover** | `cmux browser hover '{selector}'` | `hover` |
| **Wait** | `cmux browser wait --selector '{css}' --timeout-ms {ms}` | `wait_for` |
| **Console errors** | `cmux browser console list` | `list_console_messages` |
| **JS evaluate** | `cmux browser eval '{script}'` | `evaluate_script` |
| **Dialog handle** | `cmux browser dialog accept` / `dismiss` | `handle_dialog` |
| **Tab list** | `cmux browser tab list` | `list_pages` |
| **Tab switch** | `cmux browser tab switch {index}` | `select_page` |
| **New tab** | `cmux browser tab new` | `new_page` |
| **Get URL** | `cmux browser get url` | (via evaluate_script) |
| **Get text** | `cmux browser get text '{selector}'` | (via take_snapshot) |
| **Check visible** | `cmux browser is visible '{selector}'` | (via take_snapshot) |
| **Scroll** | `cmux browser scroll --dy {pixels}` | (via evaluate_script) |
| **Highlight** | `cmux browser highlight '{selector}'` | (via evaluate_script) |
| **Resize viewport** | `cmux browser eval 'window.resizeTo({w},{h})'` | `resize_page` |
| **Network requests** | `cmux browser eval 'performance.getEntriesByType("resource")'` | `list_network_requests` |
| **Performance trace** | ⚠️ Not available — fallback to Chrome MCP | `performance_start_trace` / `performance_stop_trace` |

**cmux browser notes:**
- cmux browser commands are executed via Bash tool
- Use `--snapshot-after` flag on interaction commands (click, fill, type, press) to auto-capture DOM after action
- For network request inspection, use `cmux browser eval` with Performance API or inject a fetch interceptor
- For performance measurement (Step 8), always use Chrome MCP regardless of BROWSER_MODE — if Chrome MCP is unavailable, skip performance trace and note it in the report

---

### Step 2: Assess Project Environment

Assess the current project's tech stack and server launch method:

1. Check tech stack in `CLAUDE.md` (backend, frontend, DB)
2. Check run scripts in `package.json`, `build.gradle`, `pom.xml`, `pyproject.toml`, etc.
3. Check environment variables in `.env`, `.env.local`, etc. (port number, DB URL, etc.)

**Server launch command detection by tech stack (with port injection):**

| Tech Stack | Detection File | Launch Command (port-aware) | Port Var |
|----------|----------|-----------|----------|
| Next.js | `package.json` → `next dev` | `PORT=$TEST_PORT npm run dev` | PORT |
| React (CRA) | `package.json` → `react-scripts` | `PORT=$TEST_PORT npm start` | PORT |
| Vite | `package.json` → `vite` | `npm run dev -- --port $TEST_PORT` | (argument) |
| NestJS | `package.json` → `@nestjs/core` | `PORT=$TEST_PORT npm run start:dev` | PORT |
| Spring Boot (Gradle) | `build.gradle` | `./gradlew bootRun --args="--server.port=${SERVER_PORT:-$TEST_PORT}"` | SERVER_PORT |
| Spring Boot (Maven) | `pom.xml` | `./mvnw spring-boot:run -Dspring-boot.run.arguments="--server.port=${SERVER_PORT:-$TEST_PORT}"` | SERVER_PORT |
| FastAPI | `pyproject.toml` / `main.py` | `uvicorn main:app --reload --port ${FASTAPI_PORT:-$TEST_PORT}` | FASTAPI_PORT |
| Django | `manage.py` | `python manage.py runserver ${DJANGO_PORT:-$TEST_PORT}` | DJANGO_PORT |

> **Port injection rule**: In a sprint worktree, `.astra-worktree.env` predefines the variables above. In a main worktree or an environment without the env file, `$TEST_PORT` (default 3000) is applied as a fallback. Storing the *actual port number* used by the server launch command in `$LAUNCHED_PORT` lets the Step 10 / failure-branch cleanup terminate that port.

### Step 3: Start Server and Monitor Logs

**Launch the server in the background, capture PID and logs:**

```bash
# 1. Pick the port variable that matches the stack (see Step 2 table). Example: Next.js
LAUNCHED_PORT="$TEST_PORT"   # Record the actually-used port (for cleanup)

# 2. Launch with Bash run_in_background=true (PORT/SERVER_PORT/etc. exactly as in the Step 2 table)
#    The Bash tool returns a background shell id → store it in SERVER_SHELL_ID
#    Example: SERVER_SHELL_ID=$(Bash run_in_background=true command="PORT=$LAUNCHED_PORT npm run dev")

# 3. Capture child PIDs too (in case npm/gradle wrappers spawn the actual server as a child process).
#    In environments where the Bash tool's shell id cannot be converted to an OS PID, use lsof to trace back the PID occupying the port:
sleep 3  # initial startup wait
SERVER_PIDS=$(lsof -i ":$LAUNCHED_PORT" -sTCP:LISTEN -t 2>/dev/null | sort -u | tr '\n' ' ')
echo "Server PIDs: ${SERVER_PIDS:-(not detected yet)} (port=$LAUNCHED_PORT)"
```

**Server startup verification sequence:**
1. Start server process with Bash `run_in_background=true` — store the background shell id returned by the Bash tool in `SERVER_SHELL_ID`.
2. Periodically check server logs with `TaskOutput` to detect startup completion message.
3. After startup completes, capture every LISTENing PID with `lsof -i :$LAUNCHED_PORT -sTCP:LISTEN -t` and store them in `SERVER_PIDS` (used during the cleanup step).
4. If startup fails, analyze error cause from logs and report to user.

**Log monitoring patterns:**

| Tech Stack | Startup Complete Signal | Error Pattern |
|----------|---------------|----------|
| Next.js | `Ready in` / `Local:` | `Error:` / `EADDRINUSE` |
| Spring Boot | `Started .* in .* seconds` | `APPLICATION FAILED TO START` |
| NestJS | `Nest application successfully started` | `Error:` / `Cannot find module` |
| FastAPI | `Uvicorn running on` | `ERROR:` / `ModuleNotFoundError` |

### Step 4: Write Test Cases

Analyze the project and write test cases directly.

#### A. Analyze Test Targets

Check `$ARGUMENTS`:

- **If URL is provided**: Analyze the page and write test cases
- **If scenario is provided**: Write test cases based on the scenario
- **If no arguments**: Analyze the entire project and write test cases

#### B. Project Analysis Items

Analyze the following to write test cases:

1. **Route/page structure**: Identify page list from `src/app/`, `src/pages/`, `routes/`, etc.
2. **API endpoints**: Identify endpoint list from controllers and API route files
3. **Core features**: Identify key features from CLAUDE.md, README.md, and blueprint documents
4. **Forms/input elements**: Identify screens requiring user input
5. **Authentication/authorization**: Identify screens requiring login and permission checks

#### C. Write Test Cases

Write test cases in the `docs/tests/test-cases/sprint-{N}/` directory (where `{N}` is the current sprint number detected from `docs/sprints/` by scanning `sprint-{N}-{name}/` directories and finding the highest `{N}`).

> **Note**: Test cases are written on the *current* branch (the sprint branch in a sprint worktree, or the current branch in the main-worktree fallback). dev merge is `/pr-merge`'s responsibility.

```markdown
# {Feature Name} Test Cases

## TC-001: {Test Case Title}
- **Preconditions**: {required pre-state}
- **Test Steps**:
  1. {step 1}
  2. {step 2}
- **Expected Result**: {expected outcome}
- **Verification Method**: snapshot / console / network / server-log

## TC-002: {Test Case Title}
...
```

**Test case types:**

| Type | Description | Example |
|------|------|------|
| Page Load | Page access and rendering verification | Main page 200 response |
| Form Submission | Input validation and submit behavior | Successful registration form submission |
| CRUD Operations | Data create/read/update/delete | Post creation reflected in list |
| Auth Flow | Login/logout/permission verification | Redirect when not logged in |
| Error Handling | Behavior on invalid input/access | 404 page display |
| Responsive | Layout verification per viewport | Menu collapse on mobile |

After writing, show the test case list to the user and get confirmation.

### Step 5: Basic Page Verification

If `BROWSER_MODE=none`, skip this step entirely.

**First, open the browser** (cmux mode only):
- cmux: `cmux new-pane --type browser --url {target-url}` — opens browser in a split pane
- Chrome MCP: browser is auto-managed, just call `navigate_page`

Automatically perform the following for each page:

#### A. Page Load Verification

**cmux mode:**
```
1. cmux browser goto {target-url}
2. cmux browser wait --selector '{main-content-selector}' --timeout-ms 10000
3. cmux browser snapshot
```

**Chrome MCP mode:**
```
1. Navigate to target URL with navigate_page
2. Verify core content load with wait_for
3. Check page structure with take_snapshot
```

#### B. Console Error Check

**cmux mode:**
```
1. cmux browser console list
2. Parse output for error/warn entries
3. Cross-reference with server logs to classify backend/frontend errors
```

**Chrome MCP mode:**
```
1. list_console_messages (types: ["error", "warn"])
2. If errors exist, get details with get_console_message
3. Cross-reference with server logs to classify backend/frontend errors
```

#### C. Network Request Verification

**cmux mode:**
```
1. cmux browser eval 'JSON.stringify(performance.getEntriesByType("resource").filter(e => ["xmlhttprequest","fetch"].includes(e.initiatorType)).map(e => ({name:e.name, duration:e.duration, status:e.responseStatus})))'
2. Detect failed requests from the output
3. For detailed inspection, inject a fetch interceptor via cmux browser eval if needed
4. Check backend processing logs for corresponding requests in server logs
```

**Chrome MCP mode:**
```
1. list_network_requests (resourceTypes: ["xhr", "fetch"])
2. Detect failed requests (4xx, 5xx)
3. Check request/response details with get_network_request
4. Check backend processing logs for corresponding requests in server logs
```

#### D. Responsive Layout Verification

**cmux mode:**
```
1. Desktop: cmux browser eval 'window.resizeTo(1280,720)' → cmux browser snapshot
2. Tablet: cmux browser eval 'window.resizeTo(768,1024)' → cmux browser snapshot
3. Mobile: cmux browser eval 'window.resizeTo(375,667)' → cmux browser snapshot
4. Check for layout breakage at each viewport
```

**Chrome MCP mode:**
```
1. Desktop (1280x720) → resize_page + take_snapshot
2. Tablet (768x1024) → resize_page + take_snapshot
3. Mobile (375x667) → resize_page + take_snapshot
4. Check for layout breakage at each viewport
```

### Step 6: Scenario-based Integration Testing

If `BROWSER_MODE=none`, skip browser-dependent scenarios. Only execute API-level and server-log tests.

Execute test cases written in Step 4 in order. Use the **Browser Command Reference** table from Step 1-A to select the correct tool for each action based on `BROWSER_MODE`.

#### Form Input Testing

**cmux mode:**
```
1. cmux browser snapshot → identify form element selectors
2. cmux browser fill '{selector}' '{value}' --snapshot-after (repeat per field)
3. cmux browser click '{submit-selector}' --snapshot-after
4. cmux browser wait --selector '{result-selector}' --timeout-ms 10000
5. Verify API calls: cmux browser eval 'performance.getEntriesByType("resource")...'
6. Verify request processing in server logs
7. cmux browser snapshot → verify result screen
```

**Chrome MCP mode:**
```
1. Check form element uids with take_snapshot
2. Enter test data with fill / fill_form
3. Click submit button with click
4. Wait for response with wait_for
5. Verify API calls with list_network_requests
6. Verify request processing in server logs
7. Verify result screen with take_snapshot
```

#### Authentication Flow Testing

**cmux mode:**
```
1. cmux browser goto {login-url}
2. cmux browser fill '{email-selector}' '{test-email}' → fill '{password-selector}' '{test-password}'
3. cmux browser click '{login-button}' --snapshot-after
4. Verify token: cmux browser eval 'document.cookie' or 'localStorage.getItem("token")'
5. cmux browser goto {protected-page-url} → verify access
6. Verify token refresh by manipulating token expiry via eval
```

**Chrome MCP mode:**
```
1. Navigate to login page
2. Attempt login with test account
3. Verify token issuance (network requests)
4. Verify access to authenticated pages
5. Verify token refresh behavior on expiration
```

#### API Integration Testing

**cmux mode:**
```
1. cmux browser goto {feature-page-url}
2. Verify data load: cmux browser eval 'performance.getEntriesByType("resource")...'
3. Verify DB query execution in server logs
4. cmux browser snapshot → verify response data matches screen
5. Perform CRUD operations via UI interactions and verify server logs + screen
```

**Chrome MCP mode:**
```
1. Navigate to feature page
2. Verify data load requests (network)
3. Verify DB query execution in server logs
4. Verify response data matches screen display
5. Perform CRUD operations and verify server logs and screen
```

### Step 7: Server Log Analysis

Periodically check server logs during testing:

**Check items:**
- Exception/stack trace occurrence
- SQL query execution logs (N+1 problem detection)
- API response time anomalies (over 3 seconds)
- Memory/resource warnings
- Authentication/authorization failure logs

**Log checking method:**
```
# Check recent output from server process with TaskOutput (block=false)
# Search for error patterns: ERROR, Exception, WARN, FATAL
```

### Step 8: Performance Measurement (optional)

When the user requests performance measurement, or for key pages.

> **Note**: Performance trace requires Chrome DevTools Protocol. If `BROWSER_MODE=cmux`, temporarily use Chrome MCP tools for this step only. If Chrome MCP is unavailable, skip this step and note "Performance trace unavailable (cmux mode, Chrome MCP not connected)" in the report.

**Chrome MCP mode (or temporary fallback from cmux):**
```
1. performance_start_trace (reload=true, autoStop=true)
2. Analyze results after trace completion
3. Check Core Web Vitals (LCP, FID, CLS)
4. Identify bottlenecks and suggest improvements
```

**cmux mode (basic metrics only, when Chrome MCP unavailable):**
```
1. cmux browser eval 'JSON.stringify(performance.timing)'
2. Calculate basic metrics: TTFB, DOM Content Loaded, Full Load
3. cmux browser eval 'JSON.stringify(performance.getEntriesByType("navigation")[0])'
4. Note: Full Core Web Vitals (LCP, FID, CLS) not available without Chrome MCP
```

### Step 9: Generate Test Result Report

Record test results in `docs/tests/test-reports/`:

```markdown
# Integration Test Report

## Test Environment
- Date: {date}
- Server: {tech stack + version}
- Browser: {cmux built-in browser / Chrome DevTools MCP / No browser (API-only)}

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
1. [Severity] {issue description}
   - Location: {page/API}
   - Server Log: {related log}
   - Reproduction Steps: {steps}

## Performance Measurement (if performed)
{Core Web Vitals results}
```

### Step 10: Shut Down Server (Guaranteed Cleanup)

This step **must always run**, whether the test finished (regardless of success/failure) or the workflow was interrupted by an error. If the port is left occupied, the next `/test-run` invocation or a server in another worktree will fail to start.

The following cleanup runs automatically without user confirmation (the dev server launched via Bash background is owned by this workflow):

```bash
# 1. Stop the Bash background shell (using the shell id returned by the Bash tool)
#    Terminate SERVER_SHELL_ID via the KillShell tool or TaskStop
#    Example: KillShell shell_id=$SERVER_SHELL_ID

# 2. Terminate the SERVER_PIDS captured via lsof (covers the case where npm/gradle wrappers launched the actual server as a child process)
for pid in $SERVER_PIDS; do
  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
  fi
done
sleep 2

# 3. If still alive, force-kill including child processes
for pid in $SERVER_PIDS; do
  if kill -0 "$pid" 2>/dev/null; then
    # Use pgrep -P to also kill child PIDs
    children=$(pgrep -P "$pid" 2>/dev/null | tr '\n' ' ')
    [ -n "$children" ] && kill -9 $children 2>/dev/null || true
    kill -9 "$pid" 2>/dev/null || true
  fi
done

# 4. Verify the port has been released
if astra_port_in_use "${LAUNCHED_PORT:-$TEST_PORT}"; then
  echo "WARN: Port ${LAUNCHED_PORT:-$TEST_PORT} is still in use." >&2
  echo "      Manual termination commands:" >&2
  echo "        lsof -i :${LAUNCHED_PORT:-$TEST_PORT}" >&2
  echo "        kill -9 \$(lsof -i :${LAUNCHED_PORT:-$TEST_PORT} -sTCP:LISTEN -t)" >&2
else
  echo "Port ${LAUNCHED_PORT:-$TEST_PORT} released"
fi
```

> **Port-termination guarantee policy (v5.0+)**:
> 1. *Before* starting the server (Step 0.D), check port occupancy with `lsof` → abort if occupied (protects external processes).
> 2. After startup (Step 3), capture both `SERVER_SHELL_ID` and the `lsof`-based `SERVER_PIDS`.
> 3. Step 10 cleanup runs on **every test outcome — success, failure, and exception** (also called before exiting via the Step 11 failure branch). If skipped, port conflicts between worktrees will occur.
> 4. After cleanup, re-check with `astra_port_in_use` → if still not released, give the user manual termination instructions.

**Call this cleanup block in the Step 11 failure branch, the Step 13 exit branch, and at any workflow-interruption point caused by an exception.** Cleanup never requires user confirmation.

### Step 11: Determine Test Success/Failure

Evaluate the overall test result based on the test report generated in Step 9:

**Success criteria (ALL must be met):**
- Server Startup: PASS
- Scenario Tests: 100% passed (all passed/total)
- No Severity-Critical issues found
- No Severity-High issues found

**Failure criteria (ANY triggers failure):**
- Server Startup: FAIL
- Scenario Tests: any test failed
- Severity-Critical issue detected
- Severity-High issue detected
- Server Log Errors with unhandled exceptions

If **tests FAILED**:
1. **Run Step 10 cleanup first** (release the port). Skipping cleanup will cause port conflicts on the next attempt.
2. Provide the test report location
3. List the failed items with brief descriptions
4. End the workflow — do NOT proceed to branch creation or commit

If **tests PASSED with Severity-High issues only** (no Critical):
1. List the High-severity issues
2. Use **AskUserQuestion** to ask the user whether to proceed despite High issues:
   - **Proceed** — acknowledge and continue to Step 12
   - **Stop** — **after running Step 10 cleanup**, end the workflow
3. If user chooses to stop, end the workflow.

If **tests PASSED** (no Critical or High issues): proceed to Step 12.

### Step 12: Commit Test Report on Current Branch

Since tests passed, commit the test report on the current branch (`${CURRENT_BRANCH}`) of the current worktree. **Do not perform dev merge/push** — the merge cycle is `/pr-merge`'s responsibility.

#### A. Stage Changes

```bash
git add docs/tests/ docs/sprints/
git add -u  # Stage only modifications to already-tracked files
```

> **Note**: `git add -u` only stages changes to already-tracked files. Untracked files such as `.env`, `credentials`, `node_modules/`, and `dist/` are not included.

Show `git diff --staged --stat` to the user and use **AskUserQuestion** to confirm before committing:

> **Please confirm the staged changes:**
> {staged file list}
> - **Proceed with commit** (default)
> - **Cancel** — abort the workflow (run Step 10 cleanup before exiting)

#### B. Commit

After user confirms:

```bash
# Commit type: "test:" if only test-result files; "fix:" if it also includes source modifications
git commit -m "{type}: sprint-{N} integration test passed on ${CURRENT_BRANCH}

- Scenario tests: {passed}/{total} passed
- Console errors: {count}
- Network failures: {count}
- Test report: docs/tests/test-reports/{report-file}

Generated with Claude Code"
```

Do not push to the remote — `/pr-merge` pushes together when it creates the PR.

### Step 13: Suggest `/pr-merge`

Tests passed and the report has been committed. Suggest `/pr-merge` as the next step:

1. Use **AskUserQuestion** to confirm:

> **Tests passed and report committed.**
> - Worktree: `$(pwd)`
> - Branch: `${CURRENT_BRANCH}`
> - Next step: `/pr-merge` (called from the current worktree) → dev merge + automatic worktree removal
>
> **Run `/pr-merge` now?**
> - **Yes** (default) — invoke `/pr-merge` via the Skill tool
> - **No** — end the workflow (user will run it manually)

2. If the user approves, call `Skill('pr-merge')`. If the user declines, exit.

> **Note**: If the user wants a direct `--staging` promotion, you can additionally suggest `/pr-merge --staging`. The default flow is sprint branch → dev merge (plain `/pr-merge`).

## Quick Run Examples

```
# Test specific URL (analyze the page → write test cases → execute)
/test-run http://localhost:3000

# Test specific scenario (write test cases based on scenario → execute)
/test-run login flow

# Full integration test (analyze project → write test cases → execute)
/test-run
```

## Notes

- **Worktree-aware port (v5.0+)**: In a sprint worktree, automatically sources `PORT`/`SERVER_PORT`/`VITE_PORT` and friends from the `.astra-worktree.env` written by `/sprint-init`. Will not conflict with the server in the main worktree (dev).
- **Port-termination guarantee**: Pre-launch occupancy check in Step 0.D, PID capture in Step 3, and 4-stage cleanup in Step 10 (shell stop → SIGTERM → SIGKILL+children → verification). Cleanup runs on test success, failure, and interruption.
- If the server is already running on the target port, **abort** (do not kill the external process). The user must terminate it manually and rerun.
- Do not expose sensitive information from `.env` files in logs.
- Use test data only in test-dedicated DB/environments.
- Mask sections containing personal information in server logs.
- Performance measurements are based on the development environment and may differ from production performance.
- **Merge/push separation (v5.0+)**: This skill does not perform dev merge/push. The merge cycle is `/pr-merge`'s responsibility, and the sprint worktree is automatically removed after the merge completes.
