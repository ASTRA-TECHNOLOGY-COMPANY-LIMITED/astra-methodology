# UAT Report Language Selection (shared)

Shared Step-0 language-resolution block for `/user-test` and `/uat-parallel`. Both skills resolve `LANG_CODE` identically; only what they do with the resolved value differs (each skill's consume-side tail).

`LANG_CODE` ∈ {`vi`, `en`, `ko`} controls `index.html` (`<html lang>` + visible labels), `issues.md` headings, and console log messages. UAT case file contents themselves are **not** translated.

## Resolution order

1. **`--lang` flag** in `$ARGUMENTS` → normalize case-insensitive: `vi|vie|vietnamese` → `vi`, `en|eng|english` → `en`, `ko|kor|korean` → `ko`. If recognized, skip the prompt.
2. **Persisted `CLAUDE.md ## Language`** in the project (set by `/select-language`) → if it resolves to `ko`, `vi`, or `en`, use it silently.
3. **Otherwise** → ask the user via `AskUserQuestion` with the trilingual prompt below. Default selection is Vietnamese (preserves the original design).

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

## Unattended default

When running unattended (e.g. under `/autorun`), if there is no `--lang` flag and no persisted `CLAUDE.md ## Language`, default to `vi` silently — never block on the prompt.
