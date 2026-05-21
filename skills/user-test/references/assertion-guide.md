# Hard Assertions & Severity Guide

Reference for the `/user-test` skill. Defines the assertion grammar used in UAT case files and the **fixed severity rules** Claude applies when a step FAILs.

## 1. Philosophy

- **Hard assertion**: the expected result must be machine-verifiable via DOM / Network / URL / Console — never by human eye.
- **2–4 assertions per step**: fewer → false PASS; more → maintenance burden.
- **Prefer Network and URL over DOM** assertions: DOM changes with UI refactors, while URL paths and API contracts are more stable.

## 2. Assertion grammar

Each assertion is one bullet under `**Expected**:` in a step. Format: `{kind}: {body}`.

### 2.1 URL assertions

| Syntax | Meaning | Verify via |
|---|---|---|
| `url: equals {url}` | Current URL equals `{url}` exactly | `window.location.href` string compare |
| `url: contains {sub}` | URL contains substring | `href.includes(sub)` |
| `url: matches {regex}` | URL matches regex | `new RegExp(...).test(href)` |
| `url: pathname equals {path}` | Pathname equals | `window.location.pathname === path` |

Examples:
```
- url: contains `/verify-email`
- url: matches `/order/\d+/confirm`
```

### 2.2 Network assertions

| Syntax | Meaning |
|---|---|
| `network: {METHOD} {path} → {status}` | A request matching method+path exists with the given status |
| `network: {METHOD} {path} response contains "{x}"` | Response body contains `{x}` |
| `network: no failed requests` | No 4xx/5xx requests since the step started |

`{path}` may be exact (`/api/auth/login`) or use wildcards (`/api/users/*`).

Verify via `mcp__chrome-devtools__list_network_requests`, then filter. Use the time window from action start until DOM is stable (~2s after action).

Examples:
```
- network: POST `/api/auth/register` → 201
- network: GET `/api/me` → 200
- network: no failed requests
```

### 2.3 DOM assertions

| Syntax | Meaning |
|---|---|
| `dom: {selector} exists` | Element exists in DOM |
| `dom: {selector} not exists` | Element does NOT exist |
| `dom: {selector} visible` | Exists AND `offsetParent !== null` |
| `dom: {selector} contains "{text}"` | `textContent` contains `{text}` |
| `dom: {selector} has value "{x}"` | `.value === x` (input/textarea) |
| `dom: {selector} has value matching {regex}` | `.value` matches regex |
| `dom: {selector} has attribute {name}="{val}"` | `getAttribute(name) === val` |
| `dom: {selector} count = {n}` | `querySelectorAll(selector).length === n` |
| `dom: text "{text}" exists` | A text node containing `{text}` exists anywhere |
| `dom: title contains "{x}"` | `document.title.includes(x)` |

**Selector support:**
- Standard CSS: `button.primary`, `input[type="email"]`, `#main h1`.
- `:has-text("...")` is non-standard CSS — implement via `evaluate_script` scanning `textContent`.

Examples:
```
- dom: `button:has-text("Đăng ký")` exists
- dom: `input[name="email"]` has value matching `test\+\d+@example\.com`
- dom: `.error-message` not exists
```

### 2.4 Console assertions

| Syntax | Meaning |
|---|---|
| `console: no error` | No `error`-level messages since the step started |
| `console: no warning` | No `warning`-level messages |
| `console: contains "{x}"` | Any message contains `{x}` |

Verify via `mcp__chrome-devtools__list_console_messages`, filter by timestamp.

Note: pages may emit console errors from extensions or ad-blockers. If `console: no error` FAILs but the source is clearly not app code, still report — at severity LOW.

## 3. Severity assignment rules (MANDATORY — use exactly this table)

On any FAIL, reference this table to assign severity. Do not improvise.

### 3.1 CRITICAL

Any of:
- Any network request returns **5xx**.
- Page crash / white screen (`document.body` empty).
- Timeout > 30s loading a page.
- Console error containing `Uncaught` at window level.

Examples: server 500 on form submit; blank page after navigate.

### 3.2 HIGH

Any of (and not CRITICAL):
- Network **4xx** on a primary endpoint of the flow (POST/PUT/DELETE), except 404 on a valid "not found" page.
- URL did not change after a primary action (e.g. submit login form but still at `/login`).
- Unexpected 401/403 on an endpoint that should be authenticated.

Examples: `POST /register` → 400; click "Submit" but URL does not change.

### 3.3 MEDIUM

Any of (and not HIGH/CRITICAL):
- Element does not exist (`dom: ... exists` fail) when the element is a CTA, form field, or heading.
- Text does not match expected (label typo, mistranslation).
- Form missing or extraneous fields vs. expected.
- Network GET 4xx on a secondary endpoint (analytics, optional resource).

Examples: "Đăng ký" button not found by selector; label shows "Đăng kí" instead of "Đăng ký".

### 3.4 LOW

Everything else:
- Unusual redirect chain (multiple 3xx) but final URL correct.
- Console warning (not error).
- Slow load (> 3s navigate → DOMContentLoaded) when a perf assertion is declared.
- Element exists but not visible.
- Console error clearly attributable to extension/ad-blocker.

Examples: page loads in 5s; React `key duplicated` warning.

## 4. Writing "Lý do gán severity"

In `issues.md`, every issue must include a `### Lý do gán {SEVERITY}` section, 1–2 sentences, format:

> {Error type} at {location}. Per rule: {applied rule}.

Good:
- "Network 5xx tại endpoint chính `/api/auth/register`. Theo rule: 5xx ⇒ CRITICAL."
- "Element CTA `button:has-text('Đăng ký')` không tồn tại trên trang chủ. Theo rule: CTA thiếu ⇒ MEDIUM."

Bad (avoid):
- "Lỗi nghiêm trọng." (no rule cited)
- "Vì tôi cảm thấy quan trọng." (subjective)

## 5. Anti-flaky tips for case authors

1. **Avoid hyper-specific selectors**: `button:has-text("Đăng ký")` > `body > div.layout > main > section:nth-child(2) > button`.
2. **Insert `wait` before network assertions** when the request is async — `wait` 1–2s or `wait {selector}`.
3. **Use `{timestamp}`** for dynamic values: `value=test+{timestamp}@example.com`.
4. **Do not assert dynamic content**: today's date, cart counts that change between runs.
5. **One primary action per step**: do not bundle "click + fill + submit" into a single step.
6. **Declare `base_url` in frontmatter**: step 1 can `navigate {base_url}` so the same case runs against staging/prod by swapping a single field.

## 6. Quick-reference table

| Symptom | Severity | Reason |
|---|---|---|
| 500 server error | CRITICAL | Backend broken |
| White screen / timeout | CRITICAL | Page dead |
| 400/422 on primary submit | HIGH | Endpoint rejects |
| Unexpected 401/403 | HIGH | Auth wrong |
| Submit did not redirect | HIGH | Flow broken |
| Missing button / CTA | MEDIUM | UI missing |
| Text typo | MEDIUM | UI wrong |
| 404 on optional asset | MEDIUM | Secondary resource |
| Slow load > 3s | LOW | Performance |
| Console warning | LOW | Advisory |
| Long 3xx redirect chain | LOW | Redirect |
