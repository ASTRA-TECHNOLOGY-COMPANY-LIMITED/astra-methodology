---
name: user-test
description: >
  Performs end-user UAT (User Acceptance Testing) by driving a real browser
  through Chrome MCP, self-verifying each step with hard assertions
  (DOM / Network / URL / Console), auto-assigning severity on failure, and
  emitting an HTML report plus issues.md into a timestamped session folder.
  Supports two modes: interactive (URL + Vietnamese natural-language flow
  description) and --auto (batch-run pre-authored test cases under
  docs/tests/uat-cases/). Use when the user asks for "UAT", "user
  acceptance test", "kiểm thử người dùng", "regression test", or runs
  /user-test, /uat. Distinct from /test-run (developer-authored technical
  integration testing) and /test-scenario (scenario authoring from
  blueprints).
argument-hint: "[URL \"flow description\"] | --auto [--from file] [--priority critical|high|medium|low] [--feature name]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__click, mcp__chrome-devtools__fill, mcp__chrome-devtools__fill_form, mcp__chrome-devtools__press_key, mcp__chrome-devtools__hover, mcp__chrome-devtools__list_console_messages, mcp__chrome-devtools__get_console_message, mcp__chrome-devtools__list_network_requests, mcp__chrome-devtools__get_network_request, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__wait_for, mcp__chrome-devtools__emulate, mcp__chrome-devtools__resize_page, mcp__chrome-devtools__list_pages, mcp__chrome-devtools__select_page, mcp__chrome-devtools__new_page, mcp__chrome-devtools__handle_dialog
---

# ASTRA /user-test — AI-assisted UAT

Drives Chrome MCP to run end-user UAT flows. Claude executes each step, self-verifies with hard assertions, and writes a session folder containing an HTML report, `session.json`, and (when failures occur) `issues.md`. Output language follows the project's `/select-language` setting; default is Vietnamese (this skill was designed for Vietnamese-speaking teams).

Difference from sibling skills:
- `/test-run` — developer-authored technical integration tests (server launch + scenario verify).
- `/test-scenario` — generates E2E scenarios from blueprints.
- `/user-test` — UAT: input is natural-language Vietnamese or normalized UAT case files; output is a QA-readable report.

Detailed references (load on demand):
- `references/assertion-guide.md` — assertion syntax + severity rules.
- `assets/report-template.html` — HTML report template.

## 1. Mode Decision

| Trigger | Mode | Input |
|---|---|---|
| `$ARGUMENTS` contains `--auto` | **Auto** | UAT case files under `docs/tests/uat-cases/` (or `--from`) |
| `$ARGUMENTS` starts with `http://` or `https://` | **Interactive** | URL + Vietnamese flow description |
| Otherwise | **Interactive** | Prompt user for URL + description via `AskUserQuestion` |

### Argument parsing
- `--auto`: enable Auto mode.
- `--from {path}`: Auto-only. Restrict to a single case file. Default: glob `docs/tests/uat-cases/*.md`.
- `--priority {critical|high|medium|low}`: Auto-only. Filter by frontmatter `priority`.
- `--feature {name}`: Auto-only. Filter by frontmatter `feature`.

## 2. Pipeline (shared by both modes)

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
    "started_at": "{ISO}",
    "test_cases": []
  }
  ```

### Step 3 — Test loop (Claude executes + self-verifies)

For each test case → for each step:

#### A. Execute action

| Action syntax | Chrome MCP tool |
|---|---|
| `navigate {url}` | `mcp__chrome-devtools__navigate_page` |
| `click {selector}` | `mcp__chrome-devtools__click` |
| `fill {selector} value={value}` | `mcp__chrome-devtools__fill` |
| `wait {ms}` or `wait {selector}` | `mcp__chrome-devtools__wait_for` |
| `press {key}` | `mcp__chrome-devtools__press_key` |
| `hover {selector}` | `mcp__chrome-devtools__hover` |

Replace literal `{timestamp}` in any value with `Date.now()` to avoid duplicate-data collisions.

Before the very first `navigate`, ensure a page exists via `list_pages`; if none, call `new_page`.

#### B. Screenshot every step

After each action, call `take_screenshot` into `{SESSION_DIR}/screenshots/step-{NN}-{slug}.png`. `{slug}` = step name lowercased, spaces → `-`, Vietnamese diacritics removed.

#### C. Verify hard assertions

Read the step's `expected` list and verify each. See `references/assertion-guide.md` for full syntax. Summary:

- `url: equals|contains|matches {x}` → compare via `evaluate_script` (`window.location.href`).
- `network: METHOD {path} → {status}` → `list_network_requests`, match method+path, check status.
- `dom: {selector} exists|visible|contains "..."|has value matching {re}` → `take_snapshot` or `evaluate_script`.
- `console: no error|no warning` → `list_console_messages`, filter by level.

**All assertions for a step must PASS for the step to PASS.**

#### D. Record result

- **PASS** → append step result to `session.json`; continue. Log: `[N/M] {step_name}   ✅ PASS`.
- **FAIL** → assign severity per `references/assertion-guide.md`, append to `issues.md`, log: `[N/M] {step_name}   ❌ FAIL — {SEVERITY}`, **skip remaining steps in this test case**, move to the next test case.

### Step 4 — Generate reports

After the loop completes:

**A. `index.html`** — load `assets/report-template.html` and substitute placeholders:
- `{{SESSION_ID}}`, `{{STARTED_AT}}`, `{{FINISHED_AT}}`, `{{MODE}}`
- `{{TOTAL_CASES}}`, `{{PASS_COUNT}}`, `{{FAIL_COUNT}}`, `{{DURATION}}`
- `{{TEST_CASES_HTML}}` — render each test case with thumbnails and per-step status (see template's HTML comment for the per-step structure).
- `{{ISSUES_HTML}}` — empty state if no FAIL, otherwise a link to `issues.md` with the severity breakdown.

Write to `{SESSION_DIR}/index.html`.

**B. `issues.md`** — only create if there is at least one FAIL. Format:

```markdown
# UAT Issues Report
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

**C. Finalize `session.json`** with `finished_at`, `summary` (pass/fail counts), and an `issues` array.

### Step 5 — (Interactive only) Offer to save the test case

Only when mode = interactive **and** at least one step PASSed. Use `AskUserQuestion`:

> "Lưu các bước đã chạy thành test case để chạy `--auto` lần sau không?"

If **yes**, ask for `feature` (slug, e.g. `dang-ky`) and `priority`, then write `docs/tests/uat-cases/{feature}.md` using the format in §3 below.

### Step 6 — Summarize

Print:
```
▶ Hoàn thành.
   📊 {PASS} PASS / {FAIL} FAIL
   📄 {SESSION_DIR}/index.html
   🐛 issues.md có {M} issue ({severity breakdown})
```

If no FAIL, skip the `issues.md` line.

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
```

## 6. Standing instructions

1. **User-facing output language**: follow `/select-language`. Default Vietnamese per this skill's design — logs, `issues.md` content, prompt strings, and report content all in Vietnamese. File slugs use ASCII (no diacritics).
2. **Minimal user interaction**: ask only at the start (missing URL) and end of an Interactive session (save case?). Never prompt inside the test loop.
3. **On FAIL, do not abort the whole run**: skip the current test case and continue with the next.
4. **Every step screenshots** — even on PASS — so the report is browsable.
5. **Severity assignment is rule-based**: always reference `references/assertion-guide.md`. Never guess by feel.
6. **`issues.md` always includes "Lý do gán severity"** — one sentence citing the rule, so devs can re-evaluate.
7. **No GitHub Issue integration** (removed in v2): write only to local `issues.md`.
8. **Hard assertions only**: do not assert on visual fidelity or human judgment. URL/Network/DOM/Console only.

## 7. Anti-scope (do NOT use for)

- Pure API testing (no UI) → use curl / integration tests.
- Unit tests → project's test framework (Jest/JUnit/pytest).
- Developer-written technical scenarios → use `/test-run`.
- Authoring new E2E scenarios from a blueprint → use `/test-scenario` first.
