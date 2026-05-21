---
description: Lightly audits UI code against docs/design-system/DESIGN.md and reports token violations and anti-AI aesthetic violations (no fixes applied)
argument-hint: "<target-path-or-glob-or-diff>"
allowed-tools: Read, Glob, Grep, Bash, Task
---

# /design-audit — Lightweight Design System Compliance Audit Command

Audits the target files against `docs/design-system/DESIGN.md` and reports violations. Does not auto-fix — use `/design-redesign --apply` if fixes are needed.

## Usage Examples

```
/design-audit src/components/Button.tsx
/design-audit src/components/                   # Entire directory
/design-audit "src/**/*.tsx"                    # glob
/design-audit --diff                             # Only git staged changes
```

## Behavior Summary

| Step | Content |
|------|---------|
| 1 | Verify `docs/design-system/DESIGN.md` exists. If absent, guide to `/design-init` and exit |
| 2 | Load the allowed token list from the DESIGN.md Front Matter |
| 3 | Invoke the `design-token-validator` agent — detect quantitative violations (hardcoded color/spacing/font, inline style, `!important`) |
| 4 | Output the results as a table — file, line, violating value, recommended token, Severity |
| 5 | Show ✅ if 0 violations, ⚠️ + next-step guidance if 1 or more |

## Violation Categories

| Category | Detected Pattern | Recommendation |
|---------|------------------|----------------|
| Hardcoded color | `#FFF`, `#3b82f6`, `rgb(...)`, `rgba(...)` (outside DESIGN.md tokens) | `var(--surface-base)`, `var(--action-primary)`, etc. |
| Hardcoded spacing | `padding: 16px`, `margin: 1.5rem` (outside `tokens.spacing.scale`) | `var(--space-4)`, `var(--space-6)` |
| Hardcoded font | `font-family: 'Helvetica'` (outside DESIGN.md `tokens.typography.fonts`) | `var(--font-sans)`, `var(--font-mono)` |
| Inline style | `style={{...}}`, `style="..."` | CSS Module / className |
| `!important` overuse | 3 or more in the same file | Make selectors explicit or change tokens |
| `outline: none` alone | `outline` removed without a focus ring | Apply DESIGN.md `accessibility.focus_ring` |

## Output Format

```
🔍 Design Audit Report

Target: 5 files (src/components/Button.tsx and 4 others)
DESIGN.md version: 1.0.0

| File | Line | Violation | Recommended Token | Severity |
|------|------|-----------|-------------------|----------|
| Button.tsx | 42 | `#3b82f6` | `var(--action-primary)` | P0 |
| Card.tsx | 18 | `padding: 16px` | `var(--space-4)` | P1 |
| Input.css | 5 | `outline: none` (no focus handling) | Apply `accessibility.focus_ring` | P0 |

Total violations: 3 (P0: 2 / P1: 1 / P2: 0)

📋 Next steps:
- Auto-fix: /design-redesign <target> --apply
- Add senior-perspective qualitative audit: /design-redesign <target>
- If DESIGN.md itself needs revision: /design-init
```

## Operating Modes

| Argument | Behavior |
|----------|----------|
| `<path>` | Single-file audit |
| `<dir>` | Recursive directory audit (auto-collects `.tsx/.ts/.jsx/.css/.scss/.html/.vue`) |
| `<glob>` | glob matching (quotes required) |
| `--diff` | Audit only the result of `git diff --name-only --diff-filter=AM HEAD` |

## This Command vs `/design-redesign`

| Item | `/design-audit` | `/design-redesign` |
|------|-----------------|--------------------|
| Violation detection | ✅ | ✅ |
| Qualitative audit (designer-persona) | ❌ | ✅ |
| Auto-fix | ❌ | ✅ (`--apply`) |
| PR creation | ❌ | ✅ (`--pr`) |
| Re-validation | ❌ | ✅ |
| Purpose | Quick diagnosis / CI gate | Full redesign |

## 4-Principle Application

- **Surgical Changes**: This command never modifies files — it only generates a report.
- **Goal-Driven Execution**: 0 violations = PASS, 1 or more = WARN. Clear exit criteria.
