---
name: user-test
description: >
  Performs end-user UAT (User Acceptance Testing) by driving a real browser —
  ego (lite) by default, Chrome MCP as fallback — with hard assertions
  (DOM / Network / URL / Console), auto-assigned failure severity, and an HTML
  report + issues.md per session.
  Interactive mode (URL + natural-language flow) or --auto (batch-run
  docs/tests/uat-cases/). Use when the user asks for "UAT", "user acceptance
  test", "kiểm thử người dùng", "regression test", or runs /user-test or /uat.
  Distinct from /test-run (developer integration testing) and /test-scenario
  (scenario authoring).
argument-hint: "[URL \"flow description\"] | --auto [--from file] [--priority critical|high|medium|low] [--feature name] [--lang vi|en|ko]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__click, mcp__chrome-devtools__fill, mcp__chrome-devtools__fill_form, mcp__chrome-devtools__press_key, mcp__chrome-devtools__hover, mcp__chrome-devtools__list_console_messages, mcp__chrome-devtools__get_console_message, mcp__chrome-devtools__list_network_requests, mcp__chrome-devtools__get_network_request, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__wait_for, mcp__chrome-devtools__emulate, mcp__chrome-devtools__resize_page, mcp__chrome-devtools__list_pages, mcp__chrome-devtools__select_page, mcp__chrome-devtools__new_page, mcp__chrome-devtools__handle_dialog
---

# ASTRA /user-test — AI-assisted UAT

> **Korean output style**: for Korean user-facing text (HITL questions, status reports, answers), apply `$CLAUDE_PLUGIN_ROOT/docs/development/korean-style.md` — §"HITL 질문 작성 규칙" and §"답변·보고 원칙". Korean files written to disk are style-checked automatically by the korean-style PostToolUse hook.

Drives a real browser to run end-user UAT flows. Claude executes each step, self-verifies with hard assertions, and writes a session folder containing an HTML report, `session.json`, and (when failures occur) `issues.md`. Output language follows the project's `/select-language` setting; default is Vietnamese (this skill was designed for Vietnamese-speaking teams).

Difference from sibling skills:
- `/test-run` — developer-authored technical integration tests (server launch + scenario verify).
- `/test-scenario` — generates E2E scenarios from blueprints.
- `/user-test` — UAT: input is natural-language Vietnamese or normalized UAT case files; output is a QA-readable report.

Detailed references (load on demand):
- `$CLAUDE_PLUGIN_ROOT/docs/development/browser-backend-policy.md` — plugin-wide backend detection order + action mapping + ego operating rules.
- `references/browser-ego-uat.md` — ego step template, assertion evaluation, session start/end (read when `UAT_BACKEND=ego`).
- `references/assertion-guide.md` — assertion syntax + severity rules.
- `references/i18n-strings.json` — vi/en/ko translation table for HTML report + issues.md.
- `assets/report-template.html` — HTML report template (uses `{{LANG}}` + `{{T_*}}` placeholders).

## 1. Mode Decision

| Trigger | Mode | Input |
|---|---|---|
| `$ARGUMENTS` contains `--auto` | **Auto** | UAT case files under `docs/tests/uat-cases/` (or `--from`) |
| `$ARGUMENTS` starts with `http://` or `https://` | **Interactive** | URL + natural-language flow description |
| Otherwise | **Interactive** | Prompt user for URL + description via `AskUserQuestion` |

### Argument parsing
- `--auto`: enable Auto mode.
- `--from {path}`: Auto-only. Restrict to a single case file. Default: glob `docs/tests/uat-cases/*.md`.
- `--priority {critical|high|medium|low}`: Auto-only. Filter by frontmatter `priority`.
- `--feature {name}`: Auto-only. Filter by frontmatter `feature`.
- `--lang {vi|en|ko}`: Report-output language for `index.html`, `issues.md`, and console logs. If omitted, see Step 0 below.

## 2. Pipeline (shared by both modes)

### Step 0 — Language Selection (report output language)

Resolve `LANG_CODE` ∈ {`vi`, `en`, `ko`} exactly as specified in `references/language-selection.md` (shared with `/uat-parallel`): `--lang` flag → persisted `CLAUDE.md ## Language` → trilingual `AskUserQuestion` prompt, with the unattended `--auto` default of `vi`.

Consume-side (this skill): once resolved, hold `LANG_CODE` in memory for all downstream steps and load `references/i18n-strings.json` to get the strings dictionary for that language.

### Step 0-B — Browser backend

Resolve `UAT_BACKEND` per the plugin-wide detection order — **ego (default) →
Chrome MCP (fallback) → cmux is not supported by this skill** (its command set
has no equivalent for the DOM/console probes UAT assertions require). Rules and
the `$ARGUMENTS` keyword table: `$CLAUDE_PLUGIN_ROOT/docs/development/browser-backend-policy.md`.

```bash
command -v ego-browser >/dev/null 2>&1 && echo ego || echo ""
```

- `ego` → `UAT_BACKEND=ego`; read `references/browser-ego-uat.md` before Step 3.
- empty **and** `mcp__chrome-devtools__*` tools present → `UAT_BACKEND=chrome-mcp`.
- neither → stop and tell the user to install `ego-browser` or register
  `chrome-devtools-mcp`. Do not write a session report for a run that never
  executed a step.

Record the resolved backend in `session.json` (`"backend"`) and in the HTML
report's environment line, so a reader can tell which engine produced the
evidence.

### Step 1 — Load input and prepare test cases

**Interactive:**
1. Extract URL and Vietnamese flow description from `$ARGUMENTS`.
2. Decompose the description into steps. Each step needs an `action` (navigate / click / fill / wait) and `expected` hard assertions.
3. If the description is vague (e.g., "đăng ký"), reason from the URL: open page → find primary CTA → fill form → submit → verify next page. **Do not interrupt to ask the user** — reason and proceed.
4. Hold the draft case in memory; do not write to disk yet.

**Auto:**
1. Glob test case files (or honor `--from`).
2. Read each YAML frontmatter; apply `--priority` / `--feature` filters.
3. Announce: "Tìm thấy N test case sẽ chạy" then continue (no confirmation prompt).

### Step 2 — Initialize session folder

```
SESSION_ID  = {YYYY-MM-DD-HHmm}     # e.g. 2026-05-21-1030
SESSION_DIR = docs/tests/uat-reports/{SESSION_ID}/
```

Create:
- `{SESSION_DIR}/screenshots/`
- `{SESSION_DIR}/session.json` initialized with:
  ```json
  {
    "session_id": "{SESSION_ID}",
    "mode": "interactive | auto",
    "backend": "ego | chrome-mcp",
    "started_at": "{ISO}",
    "test_cases": []
  }
  ```

**ego only**: open the Task Space (`astra user-test {SESSION_ID}`) and install
the CDP collectors now — see `references/browser-ego-uat.md` (*Session start*).
Collectors installed after the first navigation miss everything already emitted.

### Step 3 — Test loop (Claude executes + self-verifies)

For each test case → for each step:

#### A. Execute action

| Action syntax | ego (`UAT_BACKEND=ego`) | Chrome MCP (`UAT_BACKEND=chrome-mcp`) |
|---|---|---|
| `navigate {url}` | `gotoAndWait('{url}', { timeout: 20, settle: 1 })` | `mcp__chrome-devtools__navigate_page` |
| `click {selector}` | `click('{selector}', { label })` | `mcp__chrome-devtools__click` |
| `fill {selector} value={value}` | `fillInput('{selector}', '{value}')` | `mcp__chrome-devtools__fill` |
| `wait {ms}` or `wait {selector}` | `wait({seconds})` / `waitForElement('{selector}')` | `mcp__chrome-devtools__wait_for` |
| `press {key}` | `pressKey('{key}')` | `mcp__chrome-devtools__press_key` |
| `hover {selector}` | `hover('{selector}')` | `mcp__chrome-devtools__hover` |

Replace literal `{timestamp}` in any value with `Date.now()` to avoid duplicate-data collisions.

**ego**: the whole step (action + screenshot + assertion inputs) is **one
heredoc** — use the template in `references/browser-ego-uat.md`. Open the Task
Space and install the CDP collectors once at session start, before the first
navigation; `wait {ms}` values from the case file must be converted to seconds.
**Chrome MCP**: before the very first `navigate`, ensure a page exists via
`list_pages`; if none, call `new_page`.

#### B. Screenshot every step

Capture into `{SESSION_DIR}/screenshots/step-{NN}-{slug}.png` after each action. `{slug}` = step name lowercased, spaces → `-`, Vietnamese diacritics removed.

- **ego**: `captureScreenshot('{ABS_SESSION_DIR}/screenshots/…')` — absolute path required, and scroll to the top first (blank-frame caveat). A blank capture is re-taken, not filed.
- **Chrome MCP**: `take_screenshot`.

#### C. Verify hard assertions

Read the step's `expected` list and verify each. See `references/assertion-guide.md` for full syntax and severity rules. Evidence source per backend:

| Assertion | ego | Chrome MCP |
|---|---|---|
| `url: equals\|contains\|matches {x}` | `pageInfo()` → `url` | `evaluate_script` (`window.location.href`) |
| `network: METHOD {path} → {status}` | `drainEvents()` → `Network.*` entries; Performance-API fallback | `list_network_requests`, match method+path |
| `dom: {sel} exists\|visible\|contains\|has value matching {re}` | DOM probe via `js(...)` (see ref) | `take_snapshot` or `evaluate_script` |
| `console: no error\|no warning` | `drainEvents()` → `Runtime.*` / `Log.entryAdded`, filter by level | `list_console_messages`, filter by level |

**All assertions for a step must PASS for the step to PASS.** An assertion whose
evidence could not be read is a **FAIL** with the actual value recorded as
unobservable — never a PASS. In ego mode this most often hits network status on
cross-origin responses; `references/browser-ego-uat.md` gives the exact wording
and the `chrome-mcp` re-run escape hatch.

#### D. Record result

- **PASS** → append step result to `session.json`; continue. Log: `[N/M] {step_name}   ✅ PASS`.
- **FAIL** → assign severity per `references/assertion-guide.md`, append to `issues.md`, log: `[N/M] {step_name}   ❌ FAIL — {SEVERITY}`, **skip remaining steps in this test case**, move to the next test case.

### Step 4 — Generate reports

After the loop completes. All visible strings come from `references/i18n-strings.json` for the resolved `LANG_CODE`.

**A. `index.html`** — load `assets/report-template.html` and substitute placeholders:
- `{{LANG}}` → `LANG_CODE` (`vi` / `en` / `ko`)
- `{{SESSION_ID}}`, `{{STARTED_AT}}`, `{{FINISHED_AT}}`, `{{MODE}}`
- `{{TOTAL_CASES}}`, `{{PASS_COUNT}}`, `{{FAIL_COUNT}}`, `{{DURATION}}`
- `{{T_*}}` — every i18n placeholder from `i18n-strings.json` (report title, subtitle, labels, headings, footer, status badge text).
- `{{TEST_CASES_HTML}}` — render each test case with thumbnails and per-step status (see template's HTML comment for the per-step structure). Use `T_STATUS_PASS` / `T_STATUS_FAIL` / `T_STATUS_SKIPPED` for the badge text.
- `{{ISSUES_HTML}}` — when no FAIL: `<div class="empty"><div class="icon">🎉</div>{T_EMPTY_NO_ISSUES}</div>`. Otherwise: `<p>{T_SEE_DETAILS_AT} <a href="./issues.md">issues.md</a> ({M} {T_ISSUES_WORD}: …)</p>`.

Write to `{SESSION_DIR}/index.html`.

**B. `issues.md`** — only create if there is at least one FAIL. Use the `M_*` strings dictionary for headings. Example for `LANG_CODE = vi`:

```markdown
# Báo cáo UAT Issues
**Session**: {YYYY-MM-DD HH:mm}
**Test Cases chạy**: {N}
**Tổng số lỗi**: {M} ({X} CRITICAL, {Y} HIGH, {Z} MEDIUM, {W} LOW)

---

## Issue #1 — {SEVERITY}
**Test Case**: {UAT-ID} - {name}
**Bước**: {step_num}/{total} — {step_name}

### Expected
- {assertion 1}

### Actual
- {observed value}

### Lý do gán {SEVERITY}
{One-sentence rationale referencing the rule from assertion-guide.md.}

### Screenshot
![step-NN-slug](./screenshots/step-NN-slug.png)

### Gợi ý cho dev
- {hint 1}
```

For `LANG_CODE = en`, replace every Markdown heading/label via `i18n-strings.json` (`# UAT Issues Report`, `**Test cases run**`, `**Total issues**`, `**Step**`, `### Reason for {SEVERITY}`, `### Hint for developers`). For `LANG_CODE = ko`, use the Korean column (`# UAT 이슈 리포트`, `**실행된 테스트 케이스**`, `**단계**`, `### {SEVERITY} 사유`, `### 개발자 가이드`). Severity badges (CRITICAL/HIGH/MEDIUM/LOW) stay untranslated.

**C. Finalize `session.json`** with `finished_at`, `summary` (pass/fail counts), `lang` (the resolved `LANG_CODE`), `backend` (the resolved `UAT_BACKEND`), and an `issues` array.

**D. Close the browser session** — **ego only**: run the final heredoc with
`completeTaskSpace('astra user-test {SESSION_ID}', { keep: false })`. This runs
on **every** exit path, including an aborted or errored run; an un-closed space
leaves orphaned browser windows behind.

### Step 5 — (Interactive only) Offer to save the test case

Only when mode = interactive **and** at least one step PASSed. Use `AskUserQuestion` with the `L_SAVE_PROMPT` string for the resolved `LANG_CODE` (see `references/i18n-strings.json`).

If **yes**, ask for `feature` (slug, e.g. `dang-ky`) and `priority`, then write `docs/tests/uat-cases/{feature}.md` using the format in §3 below.

### Step 6 — Summarize

Print the `L_DONE` string for the resolved `LANG_CODE`, followed by stats. Example for `vi`:
```
▶ Hoàn thành.
   📊 {PASS} PASS / {FAIL} FAIL
   📄 {SESSION_DIR}/index.html
   🐛 issues.md có {M} issue ({severity breakdown})
```

For `en` / `ko`, swap the `▶ Done` / `▶ 완료` heading and translate the issues-line label (`issues.md has {M} issues` / `issues.md에 {M}건의 이슈`). Skip the `issues.md` line when no FAIL.

## 3. UAT case file format (Markdown + YAML frontmatter)

```markdown
---
id: UAT-001
name: Đăng ký tài khoản với email hợp lệ
priority: critical
created: 2026-05-21
feature: auth
base_url: https://staging.fect.app
---

# Đăng ký tài khoản

## Bước 1: Mở trang chủ
**Action**: navigate `https://staging.fect.app`
**Expected**:
- url: equals `https://staging.fect.app/`
- network: GET `/` → 200
- dom: `button:has-text("Đăng ký")` exists
- dom: `title` contains "Fect"

## Bước 2: Click "Đăng ký"
**Action**: click `button:has-text("Đăng ký")`
**Expected**:
- url: contains `/register`
- dom: `input[type="email"]` exists

## Bước 3: Điền email
**Action**: fill `input[type="email"]` value=`test+{timestamp}@example.com`
**Expected**:
- dom: `input[type="email"]` has value matching `test\+\d+@example\.com`

## Bước 4: Submit form
**Action**: click `button[type="submit"]`
**Expected**:
- network: POST `/api/auth/register` → 201
- url: contains `/verify-email`
- dom: text "Kiểm tra email" exists
```

Conventions:
- Each `## Bước N: {name}` is one step.
- `**Action**`: single line, `verb selector [value=...]`.
- `**Expected**`: bullet list, one assertion per line.

## 4. Output structure

```
docs/tests/uat-reports/2026-05-21-1030/
├── index.html              # Visual report (open in browser)
├── issues.md               # Only if FAIL count > 0
├── session.json            # Raw data for re-run/debug
└── screenshots/
    ├── step-01-home.png
    └── ...

docs/tests/uat-cases/
├── dang-ky.md
├── dang-nhap.md
└── tao-workspace.md
```

## 5. Examples

```
/user-test https://staging.fect.app "đăng ký tài khoản bằng email test@example.com"
/user-test --auto
/user-test --auto --from docs/tests/uat-cases/dang-ky.md
/user-test --auto --priority critical
/user-test --auto --lang en              # English report
/user-test --auto --lang ko              # Korean report
/user-test https://staging.fect.app "register a new account" --lang en
```

## 6. Standing instructions

1. **User-facing output language**: resolved in Step 0 (`--lang` flag → `CLAUDE.md` ## Language → AskUserQuestion → default `vi`). The chosen `LANG_CODE` drives `<html lang>`, every `{{T_*}}` placeholder in the HTML template, `issues.md` headings/labels, and console log strings. File slugs always use ASCII (no diacritics). `references/i18n-strings.json` is the SSoT for translations.
2. **Minimal user interaction**: ask only at the start (missing URL) and end of an Interactive session (save case?). Never prompt inside the test loop.
3. **On FAIL, do not abort the whole run**: skip the current test case and continue with the next.
4. **Every step screenshots** — even on PASS — so the report is browsable.
5. **Severity assignment is rule-based**: always reference `references/assertion-guide.md`. Never guess by feel.
6. **`issues.md` always includes "Lý do gán severity"** — one sentence citing the rule, so devs can re-evaluate.
7. **No GitHub Issue integration** (removed in v2): write only to local `issues.md`.
8. **Hard assertions only**: do not assert on visual fidelity or human judgment. URL/Network/DOM/Console only.
9. **Backend is resolved once, in Step 0-B** (ego default → Chrome MCP fallback) and recorded in `session.json` + the report. Never mix backends inside one session — a case that cannot be verified under ego is re-run as a whole under `chrome-mcp`, not step-by-step.
10. **ego mode inherits the user's real login state**: clear the session origin-scoped before auth-flow cases, and never target a production `base_url` — UAT cases write data into the real account.

## 7. Anti-scope (do NOT use for)

- Pure API testing (no UI) → use curl / integration tests.
- Unit tests → project's test framework (Jest/JUnit/pytest).
- Developer-written technical scenarios → use `/test-run`.
- Authoring new E2E scenarios from a blueprint → use `/test-scenario` first.
