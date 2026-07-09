# UAT Report i18n strings

The single source of truth for translatable UAT-report strings is the machine-readable
**[`i18n-strings.json`](./i18n-strings.json)** in this directory. This file is a thin,
human-readable pointer to it — it does **not** carry a second copy of the string table.

Used by `/user-test` and `/uat-parallel` when generating `index.html` and `issues.md`.
Supported languages: `vi` (Tiếng Việt — default), `en` (English), `ko` (한국어).

## Shape

`i18n-strings.json` is one JSON object keyed by string id; each value is a
`{ "vi": …, "en": …, "ko": … }` triple:

```json
{
  "T_REPORT_TITLE":  { "vi": "📋 Báo cáo UAT",   "en": "📋 UAT Report",       "ko": "📋 UAT 보고서" },
  "M_TOTAL_ISSUES":  { "vi": "Tổng số lỗi",       "en": "Total issues",        "ko": "전체 이슈 수" },
  "L_LANG_PROMPT":   { "vi": "…trilingual…",      "en": "…trilingual…",        "ko": "…trilingual…" }
}
```

Excerpt (see the JSON for the full ~39-key table):

| Key | vi | en | ko |
|---|---|---|---|
| `T_REPORT_TITLE` | 📋 Báo cáo UAT | 📋 UAT Report | 📋 UAT 보고서 |
| `T_STATUS_PASS` | PASS | PASS | 통과 |
| `M_ISSUES_REPORT_TITLE_PARALLEL` | # Báo cáo UAT Issues (parallel) | # UAT Issues Report (parallel) | # UAT 이슈 리포트 (병렬) |
| `M_STEP` | Bước | Step | 단계 |
| `L_FOUND_CASES` | Tìm thấy {N} test case sẽ chạy | Found {N} test cases to run | {N}개의 테스트 케이스를 실행합니다 |

## Key naming convention

- `T_*` — strings substituted into the HTML report template as `{{T_*}}` placeholders
  (title, subtitle, labels, headings, footer, status badge text). See
  `skills/user-test/assets/report-template.html`.
- `M_*` — Markdown headings/labels used when rendering `issues.md`.
- `L_*` — console log / interactive-prompt strings.

## How to add or change a string / language

1. Edit **`i18n-strings.json` only** — add or change the key's `{ "vi", "en", "ko" }` triple.
   Never re-introduce a full copy of the table into this `.md` or into any script.
2. Both consumers pick it up automatically:
   - `/uat-parallel` — `scripts/uat-parallel-report.sh` loads the JSON at runtime via `jq`
     for the resolved language, with per-key English fallback (missing file/key ⇒ one warning,
     never crashes).
   - `/user-test` — reads the JSON directly when localizing its report and `issues.md`.
3. To add a **new language**, add its BCP-47 short code as a third-level key to every entry
   and extend the `LANG_CODE` resolution in `references/language-selection.md`.

## Semantics worth knowing

- **`M_ISSUES_REPORT_TITLE` vs. `M_ISSUES_REPORT_TITLE_PARALLEL`**: `/user-test` uses the base
  key; `/uat-parallel` uses the `_PARALLEL` variant so the report header instantly signals
  whether the run was sequential (Chrome MCP) or parallel (Playwright workers).
- **`M_DEV_HINT`**: applies to `/user-test` interactive mode only — Claude authors the
  "Hint for developers" section from its own understanding of the failure. `/uat-parallel`'s
  Playwright runner has no LLM in the loop, so its `issues.md` omits this section by design.
- **`L_LANG_PROMPT`** is intentionally identical across all three columns: it is shown by
  Step 0 *before* a language is chosen, so it must read naturally in any of the three. All
  other `L_*` keys are properly localized per column (shown *after* `LANG_CODE` is set).
- Severity badge labels (CRITICAL / HIGH / MEDIUM / LOW) stay untranslated — they are
  technical taxonomy terms used identically across QA tooling.
- UAT case file content (under `docs/tests/uat-cases/`) is **not** translated by this
  dictionary — only the *report wrapper* (chrome, labels, generated messages) is localized.
- File slugs and identifiers (UAT-IDs, screenshot filenames) remain ASCII regardless of `lang`.
- The default `lang` is `vi` when neither `--lang` is provided nor the user picks one
  (preserves backward compatibility).
