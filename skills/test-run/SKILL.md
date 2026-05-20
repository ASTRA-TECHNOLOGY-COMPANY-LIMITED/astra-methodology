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

### Step 0: Worktree Context & Port Isolation (v5.0+)

테스트는 **현재 worktree의 현재 브랜치에서 실행**한다. 이전 정책의 dev 강제 머지는 sprint worktree 모델에서 더 이상 필요 없다 — 머지는 `/pr-merge`가 담당한다.

#### A. Detect Worktree Context

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"

CURRENT_BRANCH=$(git branch --show-current)
if astra_is_isolated_worktree; then
  IN_SPRINT_WT=1
else
  IN_SPRINT_WT=0
fi
```

| 컨텍스트 | 처리 |
|---------|------|
| sprint worktree (격리, sprint 브랜치) | 현재 브랜치 그대로 테스트 (정상) |
| 메인 worktree + 작업 브랜치 (호환성) | 현재 브랜치 그대로 테스트 |
| 메인 worktree + 공유 브랜치(dev/main/staging/master) | 현재 브랜치 그대로 테스트 (단발성 폴백) |

> **v5.0+ 중요**: dev 머지·푸시는 이 스킬에서 수행하지 않는다. 이전 Step 12/13의 dev 커밋·푸시·`/pr-merge --staging` 체이닝은 제거되었으며, sprint 통합 테스트가 끝나면 사용자가 `/pr-merge`를 호출해 머지 사이클에 진입한다.

#### B. Commit Unstaged Changes (if any)

테스트 전 현재 브랜치에 미커밋 변경이 있으면 wip 커밋한다 (테스트 중 파일 변경이 비결정성을 만들지 않도록):

```bash
if [ -n "$(git status --porcelain)" ]; then
  git add -u
  git commit -m "wip: pre-test commit on ${CURRENT_BRANCH}"
fi
```

> **Note**: `git add -u`는 이미 추적 중인 파일만 스테이징한다. `.env`, `node_modules/`, 빌드 결과물 등 untracked 파일은 포함되지 않는다.

#### C. Load Worktree Port Env

sprint worktree에는 `/sprint-init`이 생성한 `.astra-worktree.env`가 있다. 이 파일을 source 해 sprint 전용 포트를 적용한다:

```bash
WT_ENV="$(astra_worktree_env_path "$(pwd)")"
if [ -f "$WT_ENV" ]; then
  # shellcheck disable=SC1090
  set -a; . "$WT_ENV"; set +a
  echo "📦 sprint worktree env loaded: PORT=$PORT (base=$ASTRA_PORT_BASE)"
else
  # 메인 worktree 또는 v4.x 호환 케이스 — 기본 포트 유지
  echo "ℹ️  .astra-worktree.env 없음 — 기본 포트 사용"
fi
```

#### D. Pre-launch Port Availability Check

서버 기동 전 env 파일에 정의된 *모든* 스택별 포트가 사용 가능한지 확인하고, 하나라도 점유 중이면 abort 한다 (다른 worktree나 외부 프로세스를 종료하지 않도록). 단일 `PORT`만 검사하면 Spring Boot(`SERVER_PORT`)·Django/FastAPI(`DJANGO_PORT`/`FASTAPI_PORT`)·Vite(`VITE_PORT`) 스택에서 런타임 충돌을 선제 감지할 수 없다.

```bash
# 기본 PORT가 비어 있으면 3000으로 보정 (env 미로드 케이스 폴백)
: "${PORT:=3000}"

# env에 정의된 후보 포트를 모두 검사. 미정의/빈 값은 건너뛴다.
PORT_CHECK_FAILED=0
for var in PORT SERVER_PORT DJANGO_PORT FASTAPI_PORT VITE_PORT; do
  port_val="${!var:-}"
  [ -z "$port_val" ] && continue
  if astra_port_in_use "$port_val"; then
    echo "ERROR: $var=$port_val 가 이미 사용 중입니다." >&2
    PORT_CHECK_FAILED=1
  fi
done

if [ "$PORT_CHECK_FAILED" = "1" ]; then
  echo "       다른 worktree의 dev 서버나 외부 프로세스를 먼저 종료한 뒤 재실행하세요." >&2
  echo "       점유 프로세스 확인: lsof -i :<PORT>" >&2
  exit 1
fi

TEST_PORT="$PORT"   # Step 2 이후에서 사용하는 대표 포트 (스택별 실제 포트는 Step 2 표 참조)
echo "✅ 포트 사용 가능 확인 (PORT=$PORT, SERVER_PORT=${SERVER_PORT:-—}, DJANGO_PORT=${DJANGO_PORT:-—}, FASTAPI_PORT=${FASTAPI_PORT:-—}, VITE_PORT=${VITE_PORT:-—})"
```

> **📌 테스트 실행 브랜치**: `${CURRENT_BRANCH}` (worktree: `$(pwd)`, 포트: `$TEST_PORT`)

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

**Server launch command detection by tech stack (포트 주입 포함):**

| Tech Stack | Detection File | Launch Command (port-aware) | Port Var |
|----------|----------|-----------|----------|
| Next.js | `package.json` → `next dev` | `PORT=$TEST_PORT npm run dev` | PORT |
| React (CRA) | `package.json` → `react-scripts` | `PORT=$TEST_PORT npm start` | PORT |
| Vite | `package.json` → `vite` | `npm run dev -- --port $TEST_PORT` | (인자) |
| NestJS | `package.json` → `@nestjs/core` | `PORT=$TEST_PORT npm run start:dev` | PORT |
| Spring Boot (Gradle) | `build.gradle` | `./gradlew bootRun --args="--server.port=${SERVER_PORT:-$TEST_PORT}"` | SERVER_PORT |
| Spring Boot (Maven) | `pom.xml` | `./mvnw spring-boot:run -Dspring-boot.run.arguments="--server.port=${SERVER_PORT:-$TEST_PORT}"` | SERVER_PORT |
| FastAPI | `pyproject.toml` / `main.py` | `uvicorn main:app --reload --port ${FASTAPI_PORT:-$TEST_PORT}` | FASTAPI_PORT |
| Django | `manage.py` | `python manage.py runserver ${DJANGO_PORT:-$TEST_PORT}` | DJANGO_PORT |

> **포트 주입 규칙**: sprint worktree에서는 `.astra-worktree.env`가 위 변수들을 미리 정의해 둔다. 메인 worktree나 env 파일이 없는 환경에서는 `$TEST_PORT`(기본 3000)가 폴백으로 적용된다. 서버 launch command에서 사용한 *실제 포트 번호*를 `$LAUNCHED_PORT` 변수에 저장해 두면 Step 10/실패 분기의 cleanup이 이 포트를 종료할 수 있다.

### Step 3: Start Server and Monitor Logs

**Launch the server in the background, capture PID and logs:**

```bash
# 1. 스택에 맞는 포트 변수 선택 (Step 2 표 참조). 예시: Next.js
LAUNCHED_PORT="$TEST_PORT"   # 실제 사용한 포트를 기록 (cleanup용)

# 2. Bash run_in_background=true로 기동 (PORT/SERVER_PORT 등은 Step 2 표 명령 그대로)
#    Bash 도구는 background shell id를 반환한다 → SERVER_SHELL_ID 변수에 저장
#    예: SERVER_SHELL_ID=$(Bash run_in_background=true command="PORT=$LAUNCHED_PORT npm run dev")

# 3. 자식 PID까지 캡처 (npm/gradle wrapper 등이 자식 프로세스로 실제 서버를 띄우는 경우 대비)
#    Bash 도구의 shell id를 OS PID로 변환할 수 없는 환경에서는 lsof로 포트 점유 PID를 역추적한다:
sleep 3  # 기동 초기 대기
SERVER_PIDS=$(lsof -i ":$LAUNCHED_PORT" -sTCP:LISTEN -t 2>/dev/null | sort -u | tr '\n' ' ')
echo "🚀 서버 기동 PIDs: ${SERVER_PIDS:-(아직 미감지)} (port=$LAUNCHED_PORT)"
```

**Server startup verification sequence:**
1. Start server process with Bash `run_in_background=true` — Bash 도구가 반환한 background shell id를 `SERVER_SHELL_ID`에 저장.
2. Periodically check server logs with `TaskOutput` to detect startup completion message.
3. 기동 완료 후 `lsof -i :$LAUNCHED_PORT -sTCP:LISTEN -t`로 LISTEN 중인 PID를 모두 캡처해 `SERVER_PIDS` 에 저장 (cleanup 단계에서 사용).
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

> **Note**: Test cases are written on the *current* branch (sprint worktree에서는 sprint 브랜치, 메인 worktree 폴백에서는 현재 브랜치). dev 머지는 `/pr-merge`가 담당한다.

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

테스트가 끝났거나(성공·실패 무관) 워크플로우가 실패로 중단되더라도 **반드시 이 단계를 수행**한다. 포트를 점유한 채로 끝나면 다음 `/test-run` 또는 다른 worktree의 서버가 기동 실패한다.

다음 cleanup은 사용자 확인 없이 자동 실행한다 (Bash background에서 띄운 dev 서버는 본 워크플로우의 소유물이므로):

```bash
# 1. Bash background shell 정지 (Bash 도구가 반환했던 shell id 사용)
#    KillShell tool 또는 TaskStop을 통해 SERVER_SHELL_ID 종료
#    예: KillShell shell_id=$SERVER_SHELL_ID

# 2. lsof로 캡처한 SERVER_PIDS 종료 (npm/gradle wrapper가 자식 프로세스로 실제 서버를 띄운 경우)
for pid in $SERVER_PIDS; do
  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
  fi
done
sleep 2

# 3. 여전히 살아 있으면 자식 프로세스까지 포함해 강제 종료
for pid in $SERVER_PIDS; do
  if kill -0 "$pid" 2>/dev/null; then
    # pgrep -P로 자식 PID도 함께 종료
    children=$(pgrep -P "$pid" 2>/dev/null | tr '\n' ' ')
    [ -n "$children" ] && kill -9 $children 2>/dev/null || true
    kill -9 "$pid" 2>/dev/null || true
  fi
done

# 4. 포트가 풀렸는지 검증
if astra_port_in_use "${LAUNCHED_PORT:-$TEST_PORT}"; then
  echo "WARN: 포트 ${LAUNCHED_PORT:-$TEST_PORT}가 여전히 사용 중입니다." >&2
  echo "      수동 종료 명령:" >&2
  echo "        lsof -i :${LAUNCHED_PORT:-$TEST_PORT}" >&2
  echo "        kill -9 \$(lsof -i :${LAUNCHED_PORT:-$TEST_PORT} -sTCP:LISTEN -t)" >&2
else
  echo "✅ 포트 ${LAUNCHED_PORT:-$TEST_PORT} 해제 완료"
fi
```

> **포트 종료 보장 정책 (v5.0+)**:
> 1. 서버 기동 *전* (Step 0.D)에 `lsof`로 포트 점유 검사 → 점유 중이면 abort (외부 프로세스 보호).
> 2. 기동 후 (Step 3) `SERVER_SHELL_ID`와 `lsof` 기반 `SERVER_PIDS`를 모두 캡처.
> 3. Step 10 cleanup은 **테스트 성공·실패·예외 분기 모두에서 실행**한다 (Step 11에서 실패 분기로 종료할 때도 호출 후 종료). 누락 시 worktree 간 포트 충돌이 발생.
> 4. cleanup 후 `astra_port_in_use`로 재확인 → 풀리지 않았으면 사용자에 수동 종료 명령 안내.

**Step 11 실패 분기, Step 13 종료 분기, 예외 발생 시 워크플로우 중단 시점 모두에서 이 cleanup 블록을 호출**한다. cleanup 호출은 사용자 확인을 요구하지 않는다.

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
1. **Step 10 cleanup을 먼저 실행**(포트 해제). cleanup 미실행 시 다음 시도에서 포트 충돌 발생.
2. Provide the test report location
3. List the failed items with brief descriptions
4. End the workflow — do NOT proceed to branch creation or commit

If **tests PASSED with Severity-High issues only** (no Critical):
1. List the High-severity issues
2. Use **AskUserQuestion** to ask the user whether to proceed despite High issues:
   - **Proceed** — acknowledge and continue to Step 12
   - **Stop** — **Step 10 cleanup 실행 후** end the workflow
3. If user chooses to stop, end the workflow.

If **tests PASSED** (no Critical or High issues): proceed to Step 12.

### Step 12: Commit Test Report on Current Branch

테스트가 통과했으므로 현재 worktree의 현재 브랜치(`${CURRENT_BRANCH}`)에 테스트 리포트를 커밋한다. **dev 머지·푸시는 수행하지 않는다** — 머지 사이클은 `/pr-merge`가 담당한다.

#### A. Stage Changes

```bash
git add docs/tests/ docs/sprints/
git add -u  # 추적 중인 파일의 수정만 스테이징
```

> **Note**: `git add -u`는 이미 추적 중인 파일의 변경사항만 스테이징한다. `.env`, `credentials`, `node_modules/`, `dist/` 등 untracked 파일은 포함되지 않는다.

Show `git diff --staged --stat` to the user and use **AskUserQuestion** to confirm before committing:

> **커밋할 변경사항을 확인해주세요:**
> {staged file list}
> - **커밋 진행** (기본값)
> - **취소** — 워크플로우 중단 (Step 10 cleanup 실행 후 종료)

#### B. Commit

After user confirms:

```bash
# 커밋 타입: 테스트 결과 파일만이면 "test:", 소스 수정이 함께면 "fix:"
git commit -m "{type}: sprint-{N} integration test passed on ${CURRENT_BRANCH}

- Scenario tests: {passed}/{total} passed
- Console errors: {count}
- Network failures: {count}
- Test report: docs/tests/test-reports/{report-file}

🤖 Generated with Claude Code"
```

원격 push는 하지 않는다 — `/pr-merge`가 PR 생성 시점에 함께 push 한다.

### Step 13: Suggest `/pr-merge`

테스트 통과 + 리포트 커밋 완료. 사용자에게 다음 단계로 `/pr-merge` 실행을 제안한다:

1. Use **AskUserQuestion** to confirm:

> **테스트 통과 + 리포트 커밋 완료!**
> - Worktree: `$(pwd)`
> - Branch: `${CURRENT_BRANCH}`
> - 다음 단계: `/pr-merge` (현재 worktree에서 호출) → dev 머지 + worktree 자동 제거
>
> **/pr-merge를 지금 실행할까요?**
> - **예** (기본값) — Skill tool로 `/pr-merge` 실행
> - **아니오** — 워크플로우 종료 (사용자가 직접 실행)

2. 사용자가 승인하면 `Skill('pr-merge')` 호출. 사용자가 거부하면 종료한다.

> **Note**: 사용자가 directly `--staging` 프로모션을 원하는 경우 `/pr-merge --staging`을 별도로 안내할 수 있다. 기본 흐름은 sprint 브랜치 → dev 머지(기본 `/pr-merge`)이다.

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

- **Worktree-aware port (v5.0+)**: sprint worktree에서는 `/sprint-init`이 작성한 `.astra-worktree.env`의 `PORT`/`SERVER_PORT`/`VITE_PORT` 등을 자동 source 한다. 메인 worktree(dev)의 서버와 포트가 충돌하지 않는다.
- **포트 종료 보장**: Step 0.D에서 기동 전 점유 검사, Step 3에서 PID 캡처, Step 10에서 4단계 cleanup (shell 종료 → SIGTERM → SIGKILL+자식 → 검증). 테스트 성공·실패·중단 모두 cleanup 호출.
- If the server is already running on the target port, **abort** (do not kill the external process). 사용자가 직접 종료한 뒤 재실행해야 한다.
- Do not expose sensitive information from `.env` files in logs.
- Use test data only in test-dedicated DB/environments.
- Mask sections containing personal information in server logs.
- Performance measurements are based on the development environment and may differ from production performance.
- **머지·푸시 분리 (v5.0+)**: 이 스킬은 dev 머지·푸시를 수행하지 않는다. 머지 사이클은 `/pr-merge`가 담당하며, sprint worktree는 머지 완료 후 자동 제거된다.
