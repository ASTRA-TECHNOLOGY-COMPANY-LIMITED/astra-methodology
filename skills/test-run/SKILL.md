---
name: test-run
description: "Launches the server and performs integration testing with a real browser. Supports cmux built-in browser (primary), ego (lite) browser (secondary), and Chrome MCP (fallback). Automatically conducts server log monitoring, page verification, API behavior checks, and performance measurement."
argument-hint: "[target URL or scenario] [Chrome MCP | ego]"
allowed-tools: Read, Write, Edit, Bash, BashOutput, KillShell, Glob, Grep, Skill, AskUserQuestion, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__click, mcp__chrome-devtools__fill, mcp__chrome-devtools__fill_form, mcp__chrome-devtools__press_key, mcp__chrome-devtools__hover, mcp__chrome-devtools__list_console_messages, mcp__chrome-devtools__get_console_message, mcp__chrome-devtools__list_network_requests, mcp__chrome-devtools__get_network_request, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__wait_for, mcp__chrome-devtools__emulate, mcp__chrome-devtools__resize_page, mcp__chrome-devtools__list_pages, mcp__chrome-devtools__select_page, mcp__chrome-devtools__new_page, mcp__chrome-devtools__handle_dialog, mcp__chrome-devtools__performance_start_trace, mcp__chrome-devtools__performance_stop_trace, mcp__chrome-devtools__performance_analyze_insight
---

# ASTRA Integration Testing

Launches the server and performs integration testing in a real browser. Supports
three backends — **cmux** (primary), **ego (lite)** (secondary, macOS-only) and
**Chrome MCP** (fallback); the LLM monitors server logs and verifies behavior.

## Execution Procedure

### Step 0: Worktree Context & Port Isolation (v5.0+)

Testing **runs on the current branch of the current worktree** — this skill never
performs a dev merge/push (that is `/pr-merge`'s responsibility). Read
**`references/worktree-port-setup.md`** for the full Block A–D prose. First
wip-commit any dirty tree (Block B) so file edits during testing stay
deterministic. The load-bearing pre-flight below must run inline — a model that
skips the reference still gets: source helpers → set `TEST_PORT` → abort if bound.

```bash
# Source helpers (REQUIRED — Step 10 cleanup re-sources the same line)
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(find ~/.claude/plugins/cache -maxdepth 3 -type d -path '*/astra-methodology/*' 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"
CURRENT_BRANCH=$(git branch --show-current)

# Load sprint ports from .astra-worktree.env (SSoT); if absent, derive a
# sprint-isolated base via astra_compute_port_base (base 3000 + 100*N).
WT_ENV="$(astra_worktree_env_path "$(pwd)")"
[ -f "$WT_ENV" ] && { set -a; . "$WT_ENV"; set +a; }
if [ -n "$PORT" ]; then
  TEST_PORT="$PORT"
else
  SPRINT_N=$(find docs/sprints -maxdepth 1 -type d -name 'sprint-*' 2>/dev/null | sed -E 's#.*/sprint-([0-9]+).*#\1#' | sort -n | tail -1)
  TEST_PORT=$(astra_compute_port_base 3000 "${SPRINT_N:-0}") || TEST_PORT=3000
fi

# Abort if ANY per-stack port is bound. Iterate over VALUES (each quoted = one
# word) — zsh-safe, no bash ${!var} indirect expansion. Never kill another process.
for p in "$PORT" "$SERVER_PORT" "$DJANGO_PORT" "$FASTAPI_PORT" "$VITE_PORT" "$TEST_PORT"; do
  [ -z "$p" ] && continue
  if astra_port_in_use "$p"; then
    echo "ERROR: port $p is already in use. Stop the other server/worktree, then retry (lsof -i :$p)." >&2
    exit 1
  fi
done
echo "Port pre-flight OK — test branch ${CURRENT_BRANCH}, TEST_PORT=$TEST_PORT"
```

---

### Step 1: Detect Browser Environment

Set `BROWSER_MODE` by this order (first match wins):

1. **Necessity** — if the targets are API-only (server health, DB verification,
   log analysis, no page rendering/UI), set `BROWSER_MODE=none` and skip browser
   init (run Steps 2-4, 7, 9-13 only).
2. **Explicit intent** — `$ARGUMENTS` contains "Chrome MCP"/"chrome-devtools" →
   `chrome-mcp`; contains "ego"/"ego-browser"/"ego lite" → `ego`.
3. **Auto-detect** — `which cmux >/dev/null 2>&1 && cmux ping >/dev/null 2>&1`
   → `cmux`; else `which ego-browser >/dev/null 2>&1` → `ego`; else `chrome-mcp`.

| Mode | Browser tool |
|------|-------------|
| `cmux` | cmux browser commands (Bash) |
| `ego` | `ego-browser nodejs` heredoc scripts (Bash) — macOS-only |
| `chrome-mcp` | Chrome DevTools MCP tools |
| `none` | No browser launched |

Display the detected mode:
> **Browser environment detected**: {cmux browser / ego (lite) / Chrome MCP / no browser needed}

---

### Step 1-A: Browser Command Reference

Use this mapping table throughout all browser interaction steps. Choose the correct column based on `BROWSER_MODE`:

| Action | cmux Browser (Bash) | ego (lite) — inside `ego-browser nodejs` heredoc | Chrome MCP Tool |
|--------|---------------------|------------------------------------------------|-----------------|
| **Open browser** | `cmux new-pane --type browser --url {url}` | `useOrCreateTaskSpace('{task}')` then `openOrReuseTab({url}, { wait: true })` | (auto-managed) |
| **Navigate** | `cmux browser goto {url}` | `gotoAndWait({url}, { timeout: 20 })` | `navigate_page` |
| **Snapshot (DOM)** | `cmux browser snapshot` | `snapshotText()` → `[ref=N, loc=…]` | `take_snapshot` |
| **Screenshot** | `cmux browser screenshot` | `captureScreenshot()` (⚠️ scroll caveat — see ref) | `take_screenshot` |
| **Click** | `cmux browser click '{selector}'` | `click('@N' / '{css}' / [x,y], { label })` | `click` |
| **Fill input** | `cmux browser fill '{selector}' '{text}'` | `fillInput('{selector}', '{text}')` | `fill` |
| **Press key** | `cmux browser press {key}` | `pressKey('{key}')` / `typeText('{text}')` | `press_key` |
| **Hover** | `cmux browser hover '{selector}'` | `hover('{selector}')` | `hover` |
| **Wait** | `cmux browser wait --selector '{css}' --timeout-ms {ms}` | `waitForElement('{css}')` / `wait({sec})` / `waitForNetworkIdle()` | `wait_for` |
| **Console errors** | `cmux browser console list` | ⚠️ no helper — inject a collector via `js(...)` before navigating (see ref) | `list_console_messages` |
| **JS evaluate** | `cmux browser eval '{script}'` | ``js(String.raw`(() => { … })()`)`` | `evaluate_script` |
| **Dialog handle** | `cmux browser dialog accept` / `dismiss` | `cdp('Page.handleJavaScriptDialog', { accept: true })` | `handle_dialog` |
| **Tab list / switch / new** | `cmux browser tab list` / `tab switch {i}` / `tab new` | `listTabs()` / `switchTab({id})` / `openOrReuseTab({url})` | `list_pages` / `select_page` / `new_page` |
| **Read URL / text / visibility** | `cmux browser get url` / `get text '{sel}'` / `is visible '{sel}'` | `pageInfo()` / `snapshotText()` / `js(…)` | (via `evaluate_script` / `take_snapshot`) |
| **Scroll** | `cmux browser scroll --dy {pixels}` | `scrollBy({px})` / `scrollToBottomUntil(fn)` | (via evaluate_script) |
| **Resize viewport** | `cmux browser eval 'window.resizeTo({w},{h})'` | `cdp('Emulation.setDeviceMetricsOverride', {…})` | `resize_page` |
| **Network requests** | `cmux browser eval 'performance.getEntriesByType("resource")'` | `drainEvents()` / `js('performance.getEntriesByType("resource")')` | `list_network_requests` |
| **Performance trace** | ⚠️ Not available — fallback to Chrome MCP | ⚠️ Not available — fallback to Chrome MCP | `performance_start_trace` / `performance_stop_trace` |

cmux commands run via the Bash tool (`--snapshot-after` auto-captures the DOM);
ego actions are helper calls **inside one heredoc**, never standalone shell
commands. Per-mode detail: `references/browser-{cmux,ego,chrome-mcp}.md`.

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

> **Port injection**: `.astra-worktree.env` predefines these vars in a sprint
> worktree; otherwise `$TEST_PORT` (default 3000) is the fallback. Record the
> actual launch port as `$LAUNCHED_PORT` so Step 10 cleanup can terminate it.

### Step 3: Start Server and Monitor Logs

> **Shell state does not persist between Bash tool calls.** `SERVER_SHELL_ID`,
> `SERVER_PIDS`, and `LAUNCHED_PORT` are captured here but needed again in Steps
> 7/10/11 (later, separate Bash calls). Persist them to the state file the moment
> they are captured; every later block sources it, then re-derives from the live
> port via `lsof`.

#### State file: `.astra-test-run-state.env`

Worktree-root, gitignored (like `.astra-worktree.env`). Holds the launched port,
background shell id, and captured PIDs. Launch sequence (in order):

1. **Pick the port variable** matching the stack (see Step 2 table) and record it
   as `LAUNCHED_PORT`.
2. **Invoke the Bash tool with `run_in_background=true`** and the stack-specific
   launch command from the Step 2 table (e.g. command `PORT=<LAUNCHED_PORT> npm run dev`).
   The Bash tool result contains a **background shell id** — this is a Claude
   tool return value, not a shell variable. Record that id as `SERVER_SHELL_ID`.
3. **Persist state and capture PIDs** in a normal (foreground) Bash call,
   substituting the real values for `<LAUNCHED_PORT>` and `<SERVER_SHELL_ID>`:

```bash
LAUNCHED_PORT="<LAUNCHED_PORT>"        # from step 1
SERVER_SHELL_ID="<SERVER_SHELL_ID>"    # from the background Bash tool result (step 2)

sleep 3  # initial startup wait; npm/gradle wrappers spawn the server as a child
SERVER_PIDS=$(lsof -i ":$LAUNCHED_PORT" -sTCP:LISTEN -t 2>/dev/null | sort -u | tr '\n' ' ')

STATE_FILE="$(pwd)/.astra-test-run-state.env"
cat > "$STATE_FILE" <<EOF
LAUNCHED_PORT=$LAUNCHED_PORT
SERVER_SHELL_ID=$SERVER_SHELL_ID
SERVER_PIDS="$SERVER_PIDS"
EOF

# Gitignore the state file (idempotent) so `git add -A` never stages it.
GI="$(pwd)/.gitignore"
grep -Fxq ".astra-test-run-state.env" "$GI" 2>/dev/null \
  || printf '\n# Local test-run state (auto-generated by /test-run)\n.astra-test-run-state.env\n' >> "$GI"

echo "Server PIDs: ${SERVER_PIDS:-(not detected yet)} (port=$LAUNCHED_PORT)"
```

**Verify startup:** read the accumulating logs with the **`BashOutput` tool**
(pass the background shell id) until the startup-complete signal appears, then
rewrite the state file so `SERVER_PIDS` reflects the final `lsof` process set. On
startup failure, diagnose from the `BashOutput` logs, report, and run Step 10.

**Log monitoring patterns:**

| Tech Stack | Startup Complete Signal | Error Pattern |
|----------|---------------|----------|
| Next.js | `Ready in` / `Local:` | `Error:` / `EADDRINUSE` |
| Spring Boot | `Started .* in .* seconds` | `APPLICATION FAILED TO START` |
| NestJS | `Nest application successfully started` | `Error:` / `Cannot find module` |
| FastAPI | `Uvicorn running on` | `ERROR:` / `ModuleNotFoundError` |

### Step 4: Write Test Cases

Pick the scope from `$ARGUMENTS`: a URL → analyze that page; a scenario → base
cases on it; no arguments → analyze the whole project. Derive cases from:
route/page structure (`src/app/`, `src/pages/`, `routes/`), API endpoints
(controllers/route files), core features (CLAUDE.md, README, blueprints),
forms/input elements, and auth/permission screens.

#### Write Test Cases

Write test cases in `docs/tests/test-cases/sprint-{N}/` on the current branch.
See **`references/test-authoring.md`** for the TC template, the six test-case
types, and the sprint-number detection rule. After writing, show the test case
list to the user and get confirmation.

### Step 5: Basic Page Verification

If `BROWSER_MODE=none`, skip this step entirely.

**cmux mode: open the browser pane first** (all later cmux commands target it):
`cmux new-pane --type browser --url {target-url}`. **ego mode: every heredoc
starts with `useOrCreateTaskSpace('astra test-run sprint-{N}')`**, and Step 10
closes it. Chrome MCP auto-manages the browser — just call `navigate_page`.

Then read **`references/browser-<mode>.md`** for the per-step commands of the
detected mode — `browser-cmux.md`, `browser-ego.md`, or
`browser-chrome-mcp.md`, Step 5 section:
page-load verification, console-error check, network-request verification, and
responsive-layout verification for each page.

### Step 6: Scenario-based Integration Testing

If `BROWSER_MODE=none`, skip browser-dependent scenarios; run only API-level and
server-log tests. Execute the test cases written in Step 4 in order. Read
**`references/browser-<mode>.md`** (Step 6 section) for the per-step commands of
the detected mode — form input, authentication flow, and API integration testing.

#### Record each scenario result (machine-anchored count source)

The Step 11 pass/fail gate counts scenarios by parsing a log file, **not** from
memory. Immediately after executing each test case, append one line to the
scenario log — `PASS` only when you actually observed the expected result in this
session; `FAIL` on any mismatch/error; `SKIP` if you did not execute it:

```bash
STATE_FILE="$(pwd)/.astra-test-run-state.env"
[ -f "$STATE_FILE" ] && . "$STATE_FILE"
SCENARIO_LOG="$(pwd)/.astra-test-run-scenarios.log"
# One append per test case. STATUS ∈ {PASS, FAIL, SKIP}. Example:
echo "TC-001 PASS" >> "$SCENARIO_LOG"   # substitute the real TC id + observed status
```

Register `.astra-test-run-scenarios.log` in `.gitignore` the same way as the
state file if not already present.

### Step 7: Server Log Analysis

Periodically check server logs during testing:

**Check items:**
- Exception/stack trace occurrence
- SQL query execution logs (N+1 problem detection)
- API response time anomalies (over 3 seconds)
- Memory/resource warnings
- Authentication/authorization failure logs

**Log checking method:**
- Read the server process output with the **`BashOutput` tool**, passing the
  `SERVER_SHELL_ID` recorded in the state file (source
  `.astra-test-run-state.env` if it is not in the current shell).
- Search the returned output for error patterns: `ERROR`, `Exception`, `WARN`,
  `FATAL`.

### Step 8: Performance Measurement (optional)

When the user requests performance measurement, or for key pages. A full trace
(Core Web Vitals) requires the Chrome DevTools Protocol, so use Chrome MCP for
this step regardless of `BROWSER_MODE`. Read **`references/browser-<mode>.md`**
(Step 8 section) for the exact procedure; if `BROWSER_MODE` is `cmux`/`ego` and
Chrome MCP is unavailable, follow the basic-metrics fallback in that reference
and note "Performance trace unavailable ({mode} mode, Chrome MCP not connected)"
in the report.

### Step 9: Generate Test Result Report

Record test results in `docs/tests/test-reports/`. The `{passed}`/`{failed}`/
`{total}` values below MUST come from the Step 11 machine-anchored count
(parsing the scenario log and any test-runner summary) — do not fill them from
memory. The `ASTRA_TEST_RESULT` line is the machine-parseable gate signal and
must appear verbatim in the report:

```markdown
# Integration Test Report

## Test Environment
- Date: {date}
- Server: {tech stack + version}
- Browser: {cmux built-in browser / ego (lite) / Chrome DevTools MCP / No browser (API-only)}

<!-- Machine-parseable gate line — values from captured command output only -->
ASTRA_TEST_RESULT: {PASS|FAIL} passed={N} failed={N} total={N} skipped={N}

## Test Result Summary

| Item | Result | Notes |
|------|------|------|
| Server Startup | PASS/FAIL | |
| Console Errors | {count} | |
| Network Failures | {count} | |
| Responsive Layout | PASS/FAIL | |
| Scenario Tests | {passed}/{total} | |
| Server Log Errors | {count} | |
```

Follow the summary with Detailed Results (per-page, per-scenario, server-log
analysis), an **Issues Found** list where each entry is tagged with a severity
from the rubric in **`references/test-gate-scoring.md`** (`1. [Critical] … —
Location / Server Log / Reproduction Steps`), and a Performance section if
measured. See **`references/result-doc-skeleton.md`** for the full skeleton.

### Step 10: Shut Down Server (Guaranteed Cleanup)

This step **must always run**, whether the test finished (regardless of success/failure) or the workflow was interrupted by an error. If the port is left occupied, the next `/test-run` invocation or a server in another worktree will fail to start.

The cleanup runs automatically without user confirmation (the dev server
launched via Bash background is owned by this workflow). It **must work even if
the state file is missing** — always re-derive PIDs from the live port.

**ego mode only:** close the browser side first, in its own final heredoc —
`ego-browser nodejs` running
`completeTaskSpace('astra test-run sprint-{N}', { keep: false })`; an un-closed
space leaves orphaned browser windows behind.

**Step 1 (tool call, not shell):** Stop the background server shell. Source
`.astra-test-run-state.env` to recover `SERVER_SHELL_ID`, then **invoke the
`KillShell` tool** with that shell id. If the id is unknown/missing, skip to
step 2 — the port-based kill below is the safety net.

**Steps 2–4 (foreground Bash call):** re-derive PIDs from the port so cleanup
works regardless of state-file presence.

```bash
# Source helpers FIRST — this is a separate Bash call, so astra_port_in_use is
# otherwise undefined (cleanup would crash and falsely report "port released").
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(find ~/.claude/plugins/cache -maxdepth 3 -type d -path '*/astra-methodology/*' 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"

# Recover state; re-derive defensively from the live port (state file may be absent)
STATE_FILE="$(pwd)/.astra-test-run-state.env"
[ -f "$STATE_FILE" ] && . "$STATE_FILE"
CLEAN_PORT="${LAUNCHED_PORT:-${PORT:-$TEST_PORT}}"
LIVE_PIDS=$(lsof -i ":$CLEAN_PORT" -sTCP:LISTEN -t 2>/dev/null | sort -u)
# Union of state-file PIDs and freshly-derived live PIDs, one PID per line.
KILL_PIDS=$(printf '%s\n%s\n' "${SERVER_PIDS:-}" "$LIVE_PIDS" | tr ' ' '\n' | sort -u)

# 2. SIGTERM (covers npm/gradle wrappers that launched the server as a child).
#    Stream one PID per line — zsh does NOT word-split an unquoted "$KILL_PIDS".
printf '%s\n' "$KILL_PIDS" | while IFS= read -r pid; do
  [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null && kill "$pid" 2>/dev/null
done
sleep 2

# 3. If still alive, force-kill including child processes.
printf '%s\n' "$KILL_PIDS" | while IFS= read -r pid; do
  [ -z "$pid" ] && continue
  if kill -0 "$pid" 2>/dev/null; then
    pgrep -P "$pid" 2>/dev/null | while IFS= read -r child; do
      [ -n "$child" ] && kill -9 "$child" 2>/dev/null
    done
    kill -9 "$pid" 2>/dev/null
  fi
done

# 4. Verify the port has been released
if astra_port_in_use "$CLEAN_PORT"; then
  echo "WARN: Port $CLEAN_PORT is still in use." >&2
  echo "      Manual termination commands:" >&2
  echo "        lsof -i :$CLEAN_PORT" >&2
  echo "        kill -9 \$(lsof -i :$CLEAN_PORT -sTCP:LISTEN -t)" >&2
else
  echo "Port $CLEAN_PORT released"
  rm -f "$STATE_FILE"   # cleanup succeeded — remove stale state
fi
```

> **Guarantee (v5.0+)**: pre-launch occupancy check (Step 0.D) → state-file +
> `lsof` PID capture (Step 3) → this cleanup on **every** outcome (success,
> failure, exception) → re-check with `astra_port_in_use`, giving manual
> instructions if still held. Call this block in the Step 11 failure branch, the
> Step 13 exit branch, and at any exception. Cleanup never asks for confirmation.

### Step 11: Determine Test Success/Failure (machine-anchored gate)

Downstream automation (`/pr-merge --auto`) reads the `ASTRA_TEST_RESULT` line to
decide whether to merge. The counts on that line **gate a destructive action**,
so they must be derived from captured command output in *this* session — never
from the model's recollection of what it "saw pass".

#### Anti-fabrication rule (load-bearing)

- **If you did not execute a scenario, it is NOT passed** — record it as `SKIP`
  in the scenario log, and treat the presence of any `SKIP` as `FAIL` for the
  overall result.
- **Never write a pass count you cannot trace to command output in this
  session.** The passed/failed/total numbers MUST come from `grep`/parse of the
  scenario log and the test-runner summary below — not from memory.
- If the scenario log is empty or missing while browser scenarios were in scope,
  the result is `FAIL` (nothing was verifiably executed).

#### Compute the counts from captured output

```bash
SCENARIO_LOG="$(pwd)/.astra-test-run-scenarios.log"
PASSED=$(grep -c ' PASS$' "$SCENARIO_LOG" 2>/dev/null || echo 0)
FAILED=$(grep -c ' FAIL$' "$SCENARIO_LOG" 2>/dev/null || echo 0)
SKIPPED=$(grep -c ' SKIP$' "$SCENARIO_LOG" 2>/dev/null || echo 0)
TOTAL=$((PASSED + FAILED + SKIPPED))
```

If the project also has a unit/E2E test runner (e.g. `npm test`, `pytest`,
`./gradlew test`), **run it via the Bash tool**, capture its exit code, and parse
its own summary line for the numbers (add them into the counts above) — never
substitute a remembered number. **Per-runner summary-line patterns to grep are in
`references/test-gate-scoring.md`.** A non-zero runner exit code forces overall
`FAIL` regardless of parsed counts.

#### Severity rubric (rule-based, not judgment call)

Assign every issue found a severity from the rubric in
**`references/test-gate-scoring.md`** (Critical / High / Medium / Low); the
overall gate keys off Critical/High. Read it when scoring issues.

#### Decide and emit the gate line

**Overall result is `PASS` only when ALL hold:**
- Server Startup: PASS
- `FAILED == 0` **and** `SKIPPED == 0` (every in-scope scenario actually ran and passed)
- Test-runner exit code (if run): `0`
- No Critical and no High issue found (per the rubric above)

Otherwise the result is `FAIL`.

Emit this exact line to the terminal (and it must also be in the Step 9 report):

```bash
RESULT=PASS   # set to FAIL if any failure condition above is met
echo "ASTRA_TEST_RESULT: $RESULT passed=$PASSED failed=$FAILED total=$TOTAL skipped=$SKIPPED"
```

If **tests FAILED**:
1. **Run Step 10 cleanup first** (release the port). Skipping cleanup will cause port conflicts on the next attempt.
2. Provide the test report location
3. List the failed items with brief descriptions
4. End the workflow — do NOT proceed to branch creation or commit

If the **only** failure condition is Severity-High issues (no Critical, no failed
scenario, no skipped scenario, runner exit 0) — the gate line still reads `FAIL`
(High blocks the machine gate), but a human may override interactively:
1. List the High-severity issues.
2. Use **AskUserQuestion** to ask whether to proceed despite High issues:
   - **Proceed** — human override; continue to Step 12. (Downstream `--auto` never
     reaches here: `ASTRA_TEST_RESULT: FAIL` already halted the auto-merge.)
   - **Stop** — **after running Step 10 cleanup**, end the workflow.
3. If the user chooses to stop, end the workflow.

If **tests PASSED** (`ASTRA_TEST_RESULT: PASS`): proceed to Step 12.

### Step 12: Commit Test Report on Current Branch

Commit the report on `${CURRENT_BRANCH}` of the current worktree. **No dev
merge/push** — that is `/pr-merge`'s job.

```bash
git add docs/tests/ docs/sprints/
git add -u   # tracked-file modifications only (.env, node_modules/, dist/ excluded)
```

Show `git diff --staged --stat` and use **AskUserQuestion** to confirm before
committing (Proceed / Cancel — Cancel runs Step 10 cleanup then exits). On
confirm, commit with type `test:` (result files only) or `fix:` (also source
edits):

```bash
git commit -m "{type}: sprint-{N} integration test passed on ${CURRENT_BRANCH}

- Scenario tests: {passed}/{total} passed
- Console errors: {count} · Network failures: {count}
- Test report: docs/tests/test-reports/{report-file}

Generated with Claude Code"
```

Do not push — `/pr-merge` pushes when it creates the PR.

### Step 13: Suggest `/pr-merge`

Use **AskUserQuestion**: run `/pr-merge` now (from `$(pwd)`, branch
`${CURRENT_BRANCH}`) → sprint PR + automatic worktree removal? On **Yes**, call
`Skill('pr-merge')`; on **No**, exit. For a direct promotion the user may instead
run `/pr-merge --staging`.

## Usage & Notes

Invocation forms (URL / scenario / whole-project) and the operational caveats —
worktree-aware port sourcing, the port-termination guarantee, the never-kill-an-
external-process rule, secret handling, perf disclaimer, and merge/push
separation — are in **`references/test-run-usage.md`**.
