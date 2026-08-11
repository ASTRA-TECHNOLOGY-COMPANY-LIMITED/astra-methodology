---
name: uat-parallel
description: >
  Runs UAT (User Acceptance Testing) cases in TRUE PARALLEL using Playwright
  Test runner with isolated browser contexts per worker (separate cookies,
  localStorage, sessionStorage). Solves the two main limits of /user-test:
  (1) sequential single-page execution that does not scale beyond a few
  cases, and (2) one stuck case blocking the rest of the run. Reuses 100%
  of the /user-test UAT case Markdown+YAML format under
  docs/tests/uat-cases/, runs them via `npx playwright test --workers=N`,
  and emits the same report layout (index.html + issues.md + session.json
  + screenshots/) under docs/tests/uat-reports/. Use when the user asks
  to "run UAT in parallel", "speed up UAT", "test multi-user", "song song",
  "uat parallel", or runs /uat-parallel. Distinct from /user-test
  (sequential, ego → Chrome MCP, supports interactive mode), /test-run
  (developer integration tests), /test-scenario (scenario authoring).
argument-hint: "[--workers N] [--from glob] [--priority critical|high|medium|low] [--feature name] [--timeout 30s] [--headed] [--browser chromium|firefox|webkit] [--lang vi|en|ko]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# ASTRA /uat-parallel — Playwright-powered Parallel UAT

> **Korean output style**: for Korean user-facing text (HITL questions, status reports, answers), apply `$CLAUDE_PLUGIN_ROOT/docs/development/korean-style.md` — §"HITL 질문 작성 규칙" and §"답변·보고 원칙". Korean files written to disk are style-checked automatically by the korean-style PostToolUse hook.

Runs UAT cases concurrently using Playwright Test workers. Each worker holds an isolated browser context, so authentication, cookies, and localStorage do not leak between cases. Cases that hang are killed by per-step / per-case timeouts and never block other workers.

This skill is the **parallel sibling** of `/user-test`. Use `/user-test` for interactive ad-hoc testing or when you do not have Playwright installed; use `/uat-parallel` for batch regression runs.

| Aspect | `/user-test` | `/uat-parallel` |
|---|---|---|
| Driver | ego / Chrome MCP (in-Claude tool calls) | Playwright CLI (subprocess) |
| Concurrency | 1 page, sequential | N workers, parallel |
| Browser state | Shared across cases | Isolated per worker |
| Per-case timeout | None (Claude must self-abort) | Hard timeout enforced by Playwright |
| Interactive mode | Yes (URL + Vietnamese flow) | **No** (auto-batch only) |
| Trace / replay | Static screenshots only | Playwright trace viewer (`.zip`) |
| Bootstrap cost | Zero | One-time `npm i -D @playwright/test` |
| Case format | `docs/tests/uat-cases/*.md` | **Same** files, no migration |

Detailed references (load on demand):
- `references/parallel-guide.md` — worker count tuning, isolation guarantees, debugging flaky cases.
- `../user-test/references/assertion-guide.md` — assertion grammar and severity rules (reused as-is).
- `../user-test/references/i18n-strings.json` — vi/en/ko translation table (shared SSoT; the merge script reads `UAT_LANG` and loads this JSON via `jq` at runtime). `../user-test/references/i18n-strings.md` is a human-readable pointer to it.

## 1. Bootstrap (run once per project)

Check whether Playwright is available:

```bash
npx --no-install playwright --version 2>/dev/null
```

If the command exits non-zero **or** `package.json` does not contain `@playwright/test`:

1. Ask the user via `AskUserQuestion`:
   > "Skill này cần Playwright để chạy song song. Cài `@playwright/test` + Chromium ngay không? (~150 MB)"
   - **Có (Recommended)** → run installation
   - **Không** → abort with message: `Đã huỷ. Chạy thủ công: npm i -D @playwright/test && npx playwright install chromium`

2. On confirmation:
   ```bash
   # In project root
   if [ ! -f package.json ]; then npm init -y >/dev/null; fi
   npm i -D @playwright/test
   npx playwright install chromium
   ```

3. Verify: `npx playwright --version` must succeed.

Once installed, skip bootstrap on subsequent runs.

## 2. Argument parsing

| Flag | Default | Meaning |
|---|---|---|
| `--workers N` | `min(4, max(1, cpu/2))` | Number of parallel workers |
| `--from {glob}` | `docs/tests/uat-cases/*.md` | Restrict case files |
| `--priority X` | none | Filter by frontmatter `priority` |
| `--feature Y` | none | Filter by frontmatter `feature` |
| `--timeout 30s` | `30s` per step, `300s` per case | Hard timeouts |
| `--headed` | false (headless) | Show browser windows |
| `--browser X` | `chromium` | `chromium` \| `firefox` \| `webkit` |
| `--lang X` | resolved at Step 0 | Report-output language (`vi` \| `en` \| `ko`) |

## 3. Pipeline

### Step 0 — Language Selection (report output language)

Resolve `LANG_CODE` ∈ {`vi`, `en`, `ko`} exactly as specified in `../user-test/references/language-selection.md` (shared SSoT): `--lang` flag → persisted `CLAUDE.md ## Language` → trilingual `AskUserQuestion` prompt, with the unattended default of `vi` (this skill is auto-batch only, so the prompt fires only when neither the flag nor a persisted language is present).

Consume-side (this skill): export `LANG_CODE` as the `UAT_LANG` environment variable so the merge script (`uat-parallel-report.sh`) reads it in Step 5.

### Step 1 — Validate and select cases

1. Glob case files using `--from` (default `docs/tests/uat-cases/*.md`).
2. Read YAML frontmatter from each; apply `--priority` and `--feature` filters.
3. If zero cases match → abort with: `Không tìm thấy UAT case phù hợp.`
4. Announce: `Tìm thấy {N} test case, sẽ chạy song song với {W} workers.`

### Step 2 — Initialize session folder

```
SESSION_ID  = {YYYY-MM-DD-HHmm}
SESSION_DIR = docs/tests/uat-reports/{SESSION_ID}/
```

Create:
- `{SESSION_DIR}/screenshots/`
- `{SESSION_DIR}/traces/`
- `{SESSION_DIR}/raw/` (Playwright JSON output lands here)

### Step 3 — Install runner files (idempotent)

The runner files live at `.astra/uat/` in the project. On every invocation, **copy from the plugin** (overwrite — these are managed files):

| Source (plugin) | Destination (project) |
|---|---|
| `$CLAUDE_PLUGIN_ROOT/skills/uat-parallel/assets/uat-runner.spec.ts` | `.astra/uat/uat-runner.spec.ts` |
| `$CLAUDE_PLUGIN_ROOT/skills/uat-parallel/assets/playwright.config.ts` | `.astra/uat/playwright.config.ts` |

Add `.astra/uat/` to `.gitignore` if missing.

### Step 4 — Run Playwright

Set environment variables that the runner spec reads, then invoke:

```bash
cd <project-root>
UAT_SESSION_DIR="{absolute SESSION_DIR}" \
UAT_CASES_GLOB="{--from glob or default}" \
UAT_FILTER_PRIORITY="{--priority value or empty}" \
UAT_FILTER_FEATURE="{--feature value or empty}" \
UAT_STEP_TIMEOUT_MS="{step ms}" \
UAT_CASE_TIMEOUT_MS="{case ms}" \
npx playwright test \
  --config .astra/uat/playwright.config.ts \
  --workers {N} \
  --browser {browser} \
  {--headed if requested} \
  --reporter json,html \
  --output {SESSION_DIR}/raw
```

The runner spec writes per-case results into `{SESSION_DIR}/raw/results/{case-id}.json` plus screenshots into `{SESSION_DIR}/screenshots/{case-id}/step-NN.png`. Failed cases also produce traces at `{SESSION_DIR}/traces/{case-id}.zip`.

Do not abort on non-zero exit — Playwright returns non-zero whenever any case FAILs, which is normal.

### Step 5 — Merge results

Invoke the merge helper. Pass `UAT_LANG` (the `LANG_CODE` from Step 0) and `UAT_WORKERS` (worker count) as environment variables so the script can localize HTML + issues.md:

```bash
UAT_LANG="{LANG_CODE}" \
UAT_WORKERS="{N}" \
bash $CLAUDE_PLUGIN_ROOT/skills/uat-parallel/scripts/uat-parallel-report.sh \
  "{SESSION_DIR}" \
  "$CLAUDE_PLUGIN_ROOT/skills/user-test/assets/report-template.html"
```

The script:
1. Reads every `{SESSION_DIR}/raw/results/*.json`.
2. Aggregates pass/fail counts, durations, severities.
3. Renders `{SESSION_DIR}/index.html` from the user-test template (reused) — substitutes `{{SESSION_ID}}`, `{{MODE}}` = `"auto-parallel (W workers)"`, summary stats, `{{TEST_CASES_HTML}}`, `{{ISSUES_HTML}}`.
4. Writes `{SESSION_DIR}/issues.md` if any FAIL exists, using the same schema as `/user-test`:
   ```markdown
   ## Issue #N — {SEVERITY}
   **Test Case**: {UAT-ID} - {name}
   **Bước**: {step_num}/{total} — {step_name}
   ### Expected ...
   ### Actual ...
   ### Lý do gán {SEVERITY}
   ### Screenshot
   ### Trace (Playwright)
   `npx playwright show-trace ./traces/{case-id}.zip`
   ```
5. Writes consolidated `{SESSION_DIR}/session.json` with `summary`, `cases`, `issues`.
6. Removes `{SESSION_DIR}/raw/` after a successful merge.

### Step 6 — Summarize

Print using the `L_DONE_PARALLEL` string for the resolved `LANG_CODE`. Example for `vi`:
```
▶ Hoàn thành (parallel, {W} workers).
   📊 {PASS} PASS / {FAIL} FAIL  ·  {DURATION}
   📄 {SESSION_DIR}/index.html
   🐛 issues.md có {M} issue ({severity breakdown})
   🎞️  Trace replay: npx playwright show-trace {SESSION_DIR}/traces/{first-failed}.zip
```

For `en` use `▶ Done (parallel, {W} workers)` + `issues.md has {M} issues`; for `ko` use `▶ 완료 (병렬, {W} workers)` + `issues.md에 {M}건의 이슈`. Skip the `issues.md` and trace lines when no FAIL.

## 4. UAT case file format

**100% identical to `/user-test`** — no migration required. See `skills/user-test/SKILL.md` §3. Recap:

```markdown
---
id: UAT-001
name: Đăng ký tài khoản
priority: critical
feature: auth
base_url: https://staging.fect.app
---

## Bước 1: Mở trang chủ
**Action**: navigate `{base_url}`
**Expected**:
- url: equals `{base_url}/`
- dom: `button:has-text("Đăng ký")` exists
```

Action verbs (`navigate`, `click`, `fill`, `wait`, `press`, `hover`) and assertion kinds (`url`, `network`, `dom`, `console`) are interpreted by `.astra/uat/uat-runner.spec.ts`. The grammar reference is shared with `/user-test` at `skills/user-test/references/assertion-guide.md`.

## 5. Output structure

```
docs/tests/uat-reports/2026-05-29-1830/
├── index.html              # Same look as /user-test report
├── issues.md               # Only if FAIL > 0
├── session.json
├── screenshots/
│   └── UAT-001/
│       ├── step-01.png
│       └── step-02.png
└── traces/                 # Only for failed cases
    └── UAT-001.zip
```

## 6. Examples

```bash
# Run all cases with default workers
/uat-parallel

# Run with 6 workers, only critical priority
/uat-parallel --workers 6 --priority critical

# Single case, headed mode for visual debugging
/uat-parallel --from docs/tests/uat-cases/dang-ky.md --headed --workers 1

# Cross-browser regression
/uat-parallel --browser firefox --workers 3

# Generate report in English / Korean
/uat-parallel --lang en
/uat-parallel --workers 6 --priority critical --lang ko
```

## 7. Standing instructions

1. **User-facing output language**: resolved at Step 0 (`--lang` flag → `CLAUDE.md` ## Language → AskUserQuestion → default `vi`). Passed to the merge script via `UAT_LANG`. The script loads the string table from the single source of truth `skills/user-test/references/i18n-strings.json` at runtime via `jq` (resolving the chosen language with per-key English fallback; a missing file or key emits one warning and never crashes) and substitutes every visible string in `index.html` + `issues.md` accordingly. When adding or changing strings, edit that JSON only — the script holds no embedded copy. `/uat-parallel` does not render `M_DEV_HINT` (the Playwright runner has no LLM to author per-failure hints) and uses `M_ISSUES_REPORT_TITLE_PARALLEL` instead of the base title key. File slugs always use ASCII.
2. **Reuse `/user-test` assets**: do NOT duplicate the HTML template or assertion grammar — load from `skills/user-test/` paths. Future updates to `/user-test`'s template propagate automatically.
3. **Hard assertions only**: same rule as `/user-test`. URL / Network / DOM / Console only.
4. **Severity rules are shared**: identical to `references/assertion-guide.md` §3. The runner emits the raw failure; the merge script applies the severity rules.
5. **Per-case isolation is the value prop**: never share `BrowserContext` across cases. The runner enforces this via Playwright's per-test `context` fixture.
6. **Timeout is non-negotiable**: a stuck case must die, not block. Default 30s/step, 300s/case. Caller can override via `--timeout`.
7. **No GitHub Issue integration**: write only to local `issues.md`, same as `/user-test` v2+.
8. **Idempotent runner install**: copy `.astra/uat/` files from the plugin on every run — they are managed artifacts, not user-editable.

## 8. Anti-scope (do NOT use for)

- **Interactive ad-hoc UAT** (URL + Vietnamese flow on the fly) → use `/user-test`.
- **Authoring new UAT cases** from a blueprint → use `/test-scenario` first.
- **Developer technical scenarios** → use `/test-run`.
- **Pure API testing** (no UI) → use curl / integration tests.
- **Unit tests** → use the project's test framework (Jest/JUnit/pytest).
- **Visual regression** (pixel diff) → Playwright `toHaveScreenshot()` is supported by Playwright itself, but this skill enforces hard assertions only.

## 9. Failure modes & remedies

| Symptom | Likely cause | Remedy |
|---|---|---|
| Bootstrap fails: `EACCES` on `npm i` | Permission on `node_modules/` | Run `sudo chown -R $USER node_modules` |
| `npx playwright install` hangs | Network blocked | Set `HTTPS_PROXY` or pre-download browsers |
| All cases fail with "timeout waiting for selector" | `base_url` unreachable | Verify dev server, prefer `staging` URL in frontmatter |
| Worker count higher than CPU → slower run | Context switching overhead | Lower `--workers` to `cpu/2` |
| Auth state leaks across cases | Manual `context` reuse in spec | Should not happen — re-install `.astra/uat/` files from plugin |
| Trace files missing | `--trace on-first-retry` skipped | Re-run with `--workers 1` to force trace on first attempt |
