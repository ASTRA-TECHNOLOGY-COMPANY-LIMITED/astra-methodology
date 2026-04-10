---
name: test-run
description: "Launches the server and performs integration testing with a real browser. Supports cmux built-in browser (primary) and Chrome MCP (fallback). Automatically conducts server log monitoring, page verification, API behavior checks, and performance measurement."
argument-hint: "[target URL or scenario] [크롬 MCP]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Skill, AskUserQuestion, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__click, mcp__chrome-devtools__fill, mcp__chrome-devtools__fill_form, mcp__chrome-devtools__press_key, mcp__chrome-devtools__hover, mcp__chrome-devtools__list_console_messages, mcp__chrome-devtools__get_console_message, mcp__chrome-devtools__list_network_requests, mcp__chrome-devtools__get_network_request, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__wait_for, mcp__chrome-devtools__emulate, mcp__chrome-devtools__resize_page, mcp__chrome-devtools__list_pages, mcp__chrome-devtools__select_page, mcp__chrome-devtools__new_page, mcp__chrome-devtools__handle_dialog, mcp__chrome-devtools__performance_start_trace, mcp__chrome-devtools__performance_stop_trace, mcp__chrome-devtools__performance_analyze_insight
---

# ASTRA Integration Testing

Launches the server and performs integration testing in a real browser environment.
Supports two browser backends: **cmux built-in browser** (primary) and **Chrome MCP** (fallback).
The LLM directly monitors server logs to detect errors and verifies page behavior.

## Execution Procedure

### Step 0: Prepare dev Branch (Pre-merge)

테스트는 **반드시 `dev` 브랜치에서 실행**한다. 현재 브랜치의 변경사항을 dev에 머지한 뒤 테스트를 진행한다.

#### A. Check Current Branch

```bash
CURRENT_BRANCH=$(git branch --show-current)
```

#### B. Branch Handling

| 현재 브랜치 | 처리 방법 |
|------------|----------|
| `dev` | 변경사항이 있으면 커밋 후 그대로 진행 |
| `feat/*`, `fix/*` 등 작업 브랜치 | 변경사항 커밋 → dev에 머지 → dev 체크아웃 |
| `main`, `master` | ⚠️ 경고 표시 후 dev 브랜치로 전환 |

#### C. Commit Unstaged Changes (if any)

현재 브랜치에 커밋되지 않은 변경사항이 있는 경우:

```bash
# 1. 변경사항 확인
git status --short

# 2. 변경사항이 있으면 커밋 (이미 추적 중인 파일만 스테이징 — .env, 빌드 아티팩트 등 untracked 파일 제외)
git add -u
git commit -m "wip: pre-test commit on {CURRENT_BRANCH}"
```

> **Note**: `git add -u`는 이미 Git이 추적 중인 파일의 변경사항만 스테이징한다. 새로 생성된 untracked 파일은 포함되지 않으므로 `.env`, `node_modules/`, 빌드 결과물이 실수로 커밋되는 것을 방지한다.

변경사항이 없으면 이 단계를 건너뛴다.

#### D. Switch to dev and Merge

현재 브랜치가 `dev`가 아닌 경우:

```bash
# 1. dev 브랜치로 전환
git checkout dev

# 2. dev 최신화 (원격 브랜치가 존재하는 경우에만)
git ls-remote --heads origin dev | grep -q dev && git pull origin dev --no-edit
```

**`main`/`master` 브랜치인 경우**: dev로 전환만 하고, 머지는 수행하지 않는다. `main`/`master`를 dev에 머지하면 역방향 머지가 발생하므로 금지한다.

**작업 브랜치 (`feat/*`, `fix/*` 등)인 경우에만 머지를 실행한다**:

```bash
# 3. 작업 브랜치를 dev에 머지 (main/master는 제외)
git merge {CURRENT_BRANCH} --no-edit
```

**머지 충돌 발생 시:**
1. 충돌 파일 목록을 사용자에게 표시
2. **AskUserQuestion**으로 처리 방법 확인:
   - **직접 해결** — 충돌 해결 후 계속
   - **머지 취소** — `git merge --abort` 후 워크플로우 종료
3. 충돌이 해결되면 `git commit --no-edit`으로 머지 완료

#### E. Confirm dev Branch

```bash
# dev 브랜치에 있는지 최종 확인
git branch --show-current  # must be "dev"
```

> **📌 테스트 실행 브랜치**: `dev` (원래 작업 브랜치: `{CURRENT_BRANCH}`)

---

### Step 1: Detect Browser Environment

Determine which browser backend to use for testing:

#### A. Check User Intent

Parse `$ARGUMENTS` for explicit browser preference:
- If arguments contain **"크롬 MCP"**, **"Chrome MCP"**, or **"chrome-devtools"** → force **Chrome MCP** mode
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
| `chrome-mcp` | cmux unavailable OR user requested "크롬 MCP" | Chrome DevTools MCP tools |
| `none` | No browser testing needed | No browser launched |

Display the detected mode to the user:
> **🔍 브라우저 환경 감지**: {cmux 브라우저 / Chrome MCP / 브라우저 불필요}

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

**Server launch command detection by tech stack:**

| Tech Stack | Detection File | Launch Command |
|----------|----------|-----------|
| Next.js | `package.json` → `next dev` | `npm run dev` |
| React (CRA/Vite) | `package.json` → `vite` / `react-scripts` | `npm run dev` / `npm start` |
| Spring Boot (Gradle) | `build.gradle` | `./gradlew bootRun` |
| Spring Boot (Maven) | `pom.xml` | `./mvnw spring-boot:run` |
| NestJS | `package.json` → `@nestjs/core` | `npm run start:dev` |
| FastAPI | `pyproject.toml` / `main.py` | `uvicorn main:app --reload` |
| Django | `manage.py` | `python manage.py runserver` |

### Step 3: Start Server and Monitor Logs

**Launch the server in the background and capture logs:**

```
# Launch server in background (Bash run_in_background=true)
{server launch command}

# Wait for server startup (until port is open)
# Maximum 60 seconds wait, check every 5 seconds
```

**Server startup verification sequence:**
1. Start server process with Bash `run_in_background=true`
2. Periodically check server logs with `TaskOutput` to detect startup completion message
3. If startup fails, analyze error cause from logs and report to user

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

> **Note**: Test cases are written on the `dev` branch (merged in Step 0):

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

### Step 10: Shut Down Server

Shut down the server process after testing is complete:

```
# Stop background server process with TaskStop
# Or send Ctrl+C signal
```

Confirm with the user before shutting down the server.

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
1. Provide the test report location
2. List the failed items with brief descriptions
3. End the workflow — do NOT proceed to branch creation or commit

If **tests PASSED with Severity-High issues only** (no Critical):
1. List the High-severity issues
2. Use **AskUserQuestion** to ask the user whether to proceed despite High issues:
   - **Proceed** — acknowledge and continue to Step 12
   - **Stop** — end the workflow
3. If user chooses to stop, end the workflow.

If **tests PASSED** (no Critical or High issues): proceed to Step 12.

### Step 12: Commit & Push on dev Branch

테스트가 통과했으므로 dev 브랜치에서 테스트 결과를 커밋하고 푸시한다.

> **Note**: Step 0에서 이미 dev 브랜치로 전환된 상태이다. 테스트 중 생성된 파일(테스트 리포트 등)도 dev에 커밋한다.

#### A. Stage Changes

```bash
# Stage new test result files (untracked)
git add docs/tests/ docs/sprints/

# Stage modifications to existing tracked source files (safe: excludes .env, build artifacts)
git add -u
```

> **Note**: `git add -u`는 이미 추적 중인 파일의 변경사항만 스테이징한다. `git add -A`와 달리 `.env`, `credentials`, `node_modules/`, `dist/` 등 untracked 파일이 포함되지 않는다.

Show `git diff --staged --stat` to the user and use **AskUserQuestion** to confirm before committing:

> **커밋할 변경사항을 확인해주세요:**
> {staged file list}
> - **커밋 진행** (기본값)
> - **취소** — 워크플로우 중단

#### B. Commit

After user confirms:

```bash
# Detect current sprint from docs/sprints/
# Determine commit type based on staged files:
# - If only docs/tests/ and docs/sprints/ changed → use "test:"
# - If src/ or other source directories also changed → use "fix:"
git commit -m "{type}: sprint-{N} {feature-name} integration test passed

- Scenario tests: {passed}/{total} passed
- Console errors: {count}
- Network failures: {count}
- Test report: docs/tests/test-reports/{report-file}

🤖 Generated with Claude Code"
```

#### C. Push dev to Remote

```bash
git push origin dev
```

**Push failure handling:**
- If push fails due to non-fast-forward (remote dev has new commits), pull and re-push:
  ```bash
  git pull origin dev --no-edit && git push origin dev
  ```
- If push fails due to authentication or network error, display the error and end the workflow.

After push completes, display the push result.

### Step 13: PR Review & Merge (Optional)

After successful push, ask the user whether to promote `dev` to `staging`:

1. Use **AskUserQuestion** to confirm:

> **테스트 통과 → dev 커밋 → 푸시 완료!**
> Branch: `dev`
> **dev → staging 프로모션을 진행할까요?**
> - **예** (기본값) — `/pr-merge --staging` 실행
> - **아니오** — 워크플로우 종료

2. If the user approves, invoke `pr-merge --staging` using the Skill tool:

```
Use Skill tool: invoke "pr-merge" with arguments "--staging"
```

> **Note**: PR은 `dev → staging` 방향으로 생성된다. 추가 옵션이 필요한 경우 (`--no-review`, `--draft` 등) 사용자에게 확인한다.

3. If the user declines, provide the test report location and end the workflow.

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

- If the server is already running, do not start it again. Check port usage first.
- Do not expose sensitive information from `.env` files in logs.
- Use test data only in test-dedicated DB/environments.
- Mask sections containing personal information in server logs.
- Performance measurements are based on the development environment and may differ from production performance.
- Always shut down the server process after testing is complete.
