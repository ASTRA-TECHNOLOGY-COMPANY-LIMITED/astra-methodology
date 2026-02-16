---
name: test-run
description: "Launches the server and performs integration testing with Chrome MCP. Automatically conducts server log monitoring, page verification, API behavior checks, and performance measurement."
argument-hint: "[target URL or scenario]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__click, mcp__chrome-devtools__fill, mcp__chrome-devtools__fill_form, mcp__chrome-devtools__press_key, mcp__chrome-devtools__hover, mcp__chrome-devtools__list_console_messages, mcp__chrome-devtools__get_console_message, mcp__chrome-devtools__list_network_requests, mcp__chrome-devtools__get_network_request, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__wait_for, mcp__chrome-devtools__emulate, mcp__chrome-devtools__resize_page, mcp__chrome-devtools__list_pages, mcp__chrome-devtools__select_page, mcp__chrome-devtools__new_page, mcp__chrome-devtools__handle_dialog, mcp__chrome-devtools__performance_start_trace, mcp__chrome-devtools__performance_stop_trace, mcp__chrome-devtools__performance_analyze_insight
---

# ASTRA Integration Testing

Launches the server and performs integration testing in a real browser environment through Chrome MCP (chrome-devtools).
The LLM directly monitors server logs to detect errors and verifies page behavior.

## Execution Procedure

### Step 1: Assess Project Environment

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

### Step 2: Start Server and Monitor Logs

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

### Step 3: Write Test Cases

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

Write test cases in the `docs/tests/test-cases/` directory:

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

### Step 4: Basic Page Verification

Automatically perform the following for each page:

#### A. Page Load Verification

```
1. Navigate to target URL with chrome-devtools navigate_page
2. Verify core content load with wait_for
3. Check page structure with take_snapshot
```

#### B. Console Error Check

```
1. list_console_messages (types: ["error", "warn"])
2. If errors exist, get details with get_console_message
3. Cross-reference with server logs to classify backend/frontend errors
```

#### C. Network Request Verification

```
1. list_network_requests (resourceTypes: ["xhr", "fetch"])
2. Detect failed requests (4xx, 5xx)
3. Check request/response details with get_network_request
4. Check backend processing logs for corresponding requests in server logs
```

#### D. Responsive Layout Verification

```
1. Desktop (1280x720) → take_snapshot
2. Tablet (768x1024) → take_snapshot
3. Mobile (375x667) → take_snapshot
4. Check for layout breakage at each viewport
```

### Step 5: Scenario-based Integration Testing

Execute test cases written in Step 3 in order:

#### Form Input Testing

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

```
1. Navigate to login page
2. Attempt login with test account
3. Verify token issuance (network requests)
4. Verify access to authenticated pages
5. Verify token refresh behavior on expiration
```

#### API Integration Testing

```
1. Navigate to feature page
2. Verify data load requests (network)
3. Verify DB query execution in server logs
4. Verify response data matches screen display
5. Perform CRUD operations and verify server logs and screen
```

### Step 6: Server Log Analysis

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

### Step 7: Performance Measurement (optional)

When the user requests performance measurement, or for key pages:

```
1. performance_start_trace (reload=true, autoStop=true)
2. Analyze results after trace completion
3. Check Core Web Vitals (LCP, FID, CLS)
4. Identify bottlenecks and suggest improvements
```

### Step 8: Generate Test Result Report

Record test results in `docs/tests/test-reports/`:

```markdown
# Integration Test Report

## Test Environment
- Date: {date}
- Server: {tech stack + version}
- Browser: Chrome (chrome-devtools MCP)

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

### Step 9: Shut Down Server

Shut down the server process after testing is complete:

```
# Stop background server process with TaskStop
# Or send Ctrl+C signal
```

Confirm with the user before shutting down the server.

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
