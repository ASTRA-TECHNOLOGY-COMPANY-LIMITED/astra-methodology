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
argument-hint: "[URL \"flow description\"] | --auto [--from file] [--priority critical|high|medium|low] [--feature name] [--lang vi|en|ko]"
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
- `references/i18n-strings.md` — vi/en/ko translation table for HTML report + issues.md.
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

Determine `LANG_CODE` ∈ {`vi`, `en`, `ko`} — used for `index.html` (`<html lang>` + visible labels), `issues.md` headings, and console log messages. UAT case file contents themselves are not translated.

Resolution order:

1. **`--lang` flag** in `$ARGUMENTS` → normalize case-insensitive: `vi|vie|vietnamese` → `vi`, `en|eng|english` → `en`, `ko|kor|korean` → `ko`. If recognized, skip to Step 1.
2. **Persisted `CLAUDE.md ## Language`** in the project (set by `/select-language`) → if it resolves to `ko`, `vi`, or `en`, use it silently.
3. **Otherwise** → ask the user via `AskUserQuestion` with the trilingual prompt below. Default selection is Vietnamese (preserves the skill's original design).

```
Chọn ngôn ngữ cho báo cáo UAT.
Select the language for the UAT report.
UAT 보고서 언어를 선택하세요.
```

Options (single-select, header `Lang`):
- `Tiếng Việt` — Vietnamese (Recommended)
- `English` — English
- `한국어` — Korean

Map: `Tiếng Việt` → `vi`, `English` → `en`, `한국어` → `ko`.

**Under `--auto`**: if no `--lang` and no persisted `CLAUDE.md ## Language`, default to `vi` silently (no prompt) so `/autorun` stays unattended.

Once resolved, hold `LANG_CODE` in memory for all downstream steps. Load `references/i18n-strings.md` to get the strings dictionary for that language.

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

After the loop completes. All visible strings come from `references/i18n-strings.md` for the resolved `LANG_CODE`.

**A. `index.html`** — load `assets/report-template.html` and substitute placeholders:
- `{{LANG}}` → `LANG_CODE` (`vi` / `en` / `ko`)
- `{{SESSION_ID}}`, `{{STARTED_AT}}`, `{{FINISHED_AT}}`, `{{MODE}}`
- `{{TOTAL_CASES}}`, `{{PASS_COUNT}}`, `{{FAIL_COUNT}}`, `{{DURATION}}`
- `{{T_*}}` — every i18n placeholder from `i18n-strings.md` (report title, subtitle, labels, headings, footer, status badge text).
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

For `LANG_CODE = en`, replace every Markdown heading/label via `i18n-strings.md` (`# UAT Issues Report`, `**Test cases run**`, `**Total issues**`, `**Step**`, `### Reason for {SEVERITY}`, `### Hint for developers`). For `LANG_CODE = ko`, use the Korean column (`# UAT 이슈 리포트`, `**실행된 테스트 케이스**`, `**단계**`, `### {SEVERITY} 사유`, `### 개발자 가이드`). Severity badges (CRITICAL/HIGH/MEDIUM/LOW) stay untranslated.

**C. Finalize `session.json`** with `finished_at`, `summary` (pass/fail counts), `lang` (the resolved `LANG_CODE`), and an `issues` array.

### Step 5 — (Interactive only) Offer to save the test case

Only when mode = interactive **and** at least one step PASSed. Use `AskUserQuestion` with the `L_SAVE_PROMPT` string for the resolved `LANG_CODE` (see `references/i18n-strings.md`).

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

1. **User-facing output language**: resolved in Step 0 (`--lang` flag → `CLAUDE.md` ## Language → AskUserQuestion → default `vi`). The chosen `LANG_CODE` drives `<html lang>`, every `{{T_*}}` placeholder in the HTML template, `issues.md` headings/labels, and console log strings. File slugs always use ASCII (no diacritics). `references/i18n-strings.md` is the SSoT for translations.
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
