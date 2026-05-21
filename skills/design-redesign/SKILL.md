---
name: design-redesign
description: "Audits existing UI components/pages/CSS against docs/design-system/DESIGN.md and applies fixes to restore design consistency. Uses design-token-validator to detect hardcoded color/font/spacing violations, and invokes designer-persona to report a senior-perspective score (0-10) and anti-AI aesthetic violations (generic shadcn look, purple gradient cliché). Fixes are applied automatically (--apply) or proposed as a PR (--pr); after changes, design-token-validator is re-run and must PASS before completion. Input: target directory (e.g., src/components/Button), single file, or git diff. Output: audit report (docs/design-system/audit-{date}.md) + fix proposals + application results."
argument-hint: "<target-path-or-glob> [--apply] [--pr] [--auto]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Skill, Task, TodoWrite
---

# /design-redesign — Existing UI Redesign and Consistency Recovery Skill

Audits existing UI assets against the DESIGN.md SSoT and applies fix proposals. Orchestrates two agents — `design-token-validator` + `designer-persona` — to perform quantitative and qualitative evaluation together.

## Design Philosophy

In ASTRA, design consistency breaks in two ways at once:
1. **Quantitative violation**: hardcoded `#fff`, `12px`, `'Helvetica'` and other token bypasses — detected quickly by `design-token-validator` (haiku).
2. **Qualitative violation**: tokens are all correct yet the result is a generic AI look, hover-only interaction, or ignores accessibility — detected by `designer-persona` (sonnet) from a senior perspective.

These two results are merged into a prioritized fix patch, applied after user confirmation.

## Procedure

### Step 0: Argument parsing and target identification

`$ARGUMENTS`:
- First positional argument: target path/glob (e.g., `src/components/Button`, `src/pages/*.tsx`, `--diff` for git staged)
- `--apply`: auto-apply fixes (Step 5)
- `--pr`: propose fix result as a PR (delegated to `/pr-merge`)
- `--auto`: HITL default handling

Build the target file list:

```bash
if [ "$TARGET" = "--diff" ]; then
  TARGETS=$(git diff --name-only --diff-filter=AM HEAD | grep -E '\.(tsx?|jsx?|vue|svelte|css|scss|html)$')
elif [ -d "$TARGET" ]; then
  TARGETS=$(find "$TARGET" -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.jsx" -o -name "*.css" -o -name "*.scss" -o -name "*.html" -o -name "*.vue" \))
else
  TARGETS="$TARGET"
fi
```

If there are 0 targets, exit with an error.

### Step 1: Verify DESIGN.md exists

```bash
if [ ! -f "docs/design-system/DESIGN.md" ]; then
  echo "ERROR: docs/design-system/DESIGN.md is missing."
  echo "Run /design-init first to initialize the design system."
  exit 1
fi
```

Load the DESIGN.md Front Matter and keep the following information as context:
- `tokens.color.primitive.*` — allowed color list
- `tokens.typography.fonts.*` — allowed font families
- `tokens.spacing.scale` — allowed spacing values
- `aesthetic_rules.forbidden_generic_patterns` — anti-AI rules

### Step 2: Quantitative audit — invoke design-token-validator

```
Task(
  subagent_type: "astra-methodology:design-token-validator",
  description: "Audit DESIGN.md token violations",
  prompt: "Detect every hardcoded value in the following files that bypasses the allowed tokens in the docs/design-system/DESIGN.md Front Matter:\n\nFile list:\n{TARGETS}\n\nDetection categories:\n- Hardcoded color: hex (#FFF, #f5f5f5), rgb(), rgba(), hsl() (non-token values)\n- Hardcoded spacing/size: direct 0-9999px, 0.x rem values (non-token)\n- Hardcoded font-family: font names not in DESIGN.md tokens.typography.fonts\n- Inline style usage (style={{...}}, style=\"...\")\n- !important overuse\n\nFor each violation, provide file path:line number + violated value + recommended token. Output as JSON."
)
```

Save the response to the `VIOLATIONS_QUANT` variable.

### Step 3: Qualitative audit — invoke designer-persona

```
Task(
  subagent_type: "astra-methodology:designer-persona",
  description: "Senior designer-perspective audit",
  prompt: "Using the brand·aesthetic_rules·accessibility sections of docs/design-system/DESIGN.md as the baseline, review the following files from a senior designer's perspective:\n\nFile list:\n{TARGETS}\n\nReview items:\n1. Design system consistency (0-10): token usage, component variants, spacing consistency\n2. Component reusability (0-10): duplicated definitions, hardcoding, prop design\n3. WCAG 2.1 AA accessibility (0-10): contrast, focus ring, keyboard, aria\n4. Interaction patterns (0-10): hover-only reliance, touch target, feedback timing\n5. Motion appropriateness (0-10): over-eager spring, looping, missing prefers-reduced-motion\n6. Vibe Coding aesthetic (0-10): generic AI look, purple gradient cliché, emoji feature icons\n\nFor each item: score + 1-2 sentences on what would have to change to make it a 10 + priority (P0/P1/P2).\nOutput as a markdown table."
)
```

Save the response to the `VIOLATIONS_QUAL` variable.

### Step 4: Generate audit report

Write the following to `docs/design-system/audit-{YYYY-MM-DD-HHmm}.md`:

```markdown
# Design Audit Report

**Date**: {timestamp}
**Targets**: {N} files
**DESIGN.md version**: {meta.version}

## Summary
- Quantitative violations: {VIOLATIONS_QUANT.count}
- Qualitative violations: {average score from VIOLATIONS_QUAL}
- P0 (Critical): {n}
- P1 (Major): {n}
- P2 (Minor): {n}

## Quantitative Violations (design-token-validator)
{VIOLATIONS_QUANT rendered as a markdown table}

| File | Line | Violation | Recommended token | Severity |
|------|------|-----------|-------------------|----------|
| ... | ... | `#fff` | `var(--surface-base)` | P0 |

## Qualitative Findings (designer-persona)
{VIOLATIONS_QUAL quoted verbatim}

## Recommended Fix Plan
{fix items by priority — P0 first}

### P0 (Critical — merge-blocking)
1. {file:line} — {fix content} (auto-fix: ✅/❌)
...

### P1 (Major — within 1 week)
...

### P2 (Minor — backlog)
...

## Aesthetic Red Flags
{patterns detected from DESIGN.md aesthetic_rules.forbidden_generic_patterns}
```

### Step 5: Apply fixes (--apply or user confirmation)

If `--apply` is set or the user agrees to apply, start with P0 items and auto-fix per the rules below:

#### Step 5.1: Token substitution (mechanical)

| Violation pattern | Substitution rule |
|-------------------|-------------------|
| `#ffffff` / `#FFF` | `var(--surface-base)` (semantic) |
| `#000000` / `#000` | `var(--primitive-neutral-1000)` |
| `rgba(0, 0, 0, 0.X)` shadow | match to `var(--shadow-{xs|sm|md|lg|xl})` |
| `font-family: 'Helvetica', ...` | `var(--font-sans)` |
| `padding: 16px` | `padding: var(--space-4)` |
| `border-radius: 8px` | `border-radius: var(--radius-lg)` |
| `transition: ... 200ms ease` | `transition: ... var(--duration-normal) var(--ease-out)` |

Before each substitution, ask the user for confirmation in batches (5-10 at a time):

```
Apply the following 12 quantitative fixes?
  src/components/Button.tsx:42 — #3b82f6 → var(--action-primary)
  src/components/Card.tsx:18 — padding: 16px → var(--space-4)
  ...
```

In `--auto` mode, apply P0 automatically; leave P1/P2 in the report only.

#### Step 5.2: Structural fixes (semantic)

For P0 items flagged by `designer-persona` that require code structure changes:
- **Inline style → className**: `style={{color: '#fff'}}` → define a class and apply it
- **Hardcoded variant → DESIGN.md-registered component**: ad-hoc card → unified `<Card variant="elevated">`
- **Hover-only → equivalent focus handling**: apply the `:hover` effect equivalently to `:focus-visible`
- **`outline: none` → apply focus_ring**: use DESIGN.md `accessibility.focus_ring`

Structural changes are hard to automate, so confirm each fix one-by-one with the user before applying. In `--auto` mode, classify them as P1 in the report and skip.

### Step 6: Re-verification

After fixes are applied, re-invoke design-token-validator to confirm 0 violations remain:

```
Task(
  subagent_type: "astra-methodology:design-token-validator",
  description: "Re-verification after fixes",
  prompt: "Re-verify that all violations against docs/design-system/DESIGN.md have been resolved in the files just modified. Report any remaining violations."
)
```

If violations remain, re-enter Step 5 (max 3 times). If violations persist after 3 attempts, instruct the user to handle them manually.

### Step 7: Create PR (--pr)

If `--pr` is set, delegate to `/pr-merge`:

```
Skill("astra-methodology:pr-merge",
      args="--title='Design audit: apply DESIGN.md compliance fixes' --body-file=docs/design-system/audit-{date}.md")
```

Without `--pr`, leave the changes in the working tree and instruct the user to commit manually.

### Step 8: Output result

```
✅ Design Audit Complete

Targets: {N} files
Fixes applied: P0 {n} / P1 {n} / P2 0 (skipped)
Re-verification: PASS (0 remaining violations)

📋 Next steps:
- Review changes: git diff
- Report: docs/design-system/audit-{date}.md
- Create PR: /pr-merge
```

## Workflow checklist

- [ ] Step 0: argument parsing + target file identification
- [ ] Step 1: verify DESIGN.md exists + load Front Matter
- [ ] Step 2: design-token-validator quantitative audit
- [ ] Step 3: designer-persona qualitative audit
- [ ] Step 4: generate integrated audit report
- [ ] Step 5: apply fixes (5.1 token substitution + 5.2 structural fixes)
- [ ] Step 6: re-verification (confirm 0 remaining violations)
- [ ] Step 7: delegate to /pr-merge when --pr is set
- [ ] Step 8: output result

## Behavior mode matrix

| Argument | Behavior |
|----------|----------|
| `<path>` (no option) | Generate audit report only. No fixes applied. |
| `<path> --apply` | P0 auto-applied. P1/P2 confirmed with user. |
| `<path> --apply --auto` | P0 auto-applied. P1/P2 skipped. No HITL. |
| `<path> --apply --pr` | Above + create a PR via /pr-merge after applying. |
| `--diff` | Audit only git staged changes. CI / pre-commit scenario. |

## Anti-patterns — strictly forbidden

- **Never modify DESIGN.md itself**: This skill aligns code to DESIGN.md. Changes to the design system itself belong to `/design-init`.
- **Do not exit without re-verification**: Entering Step 8 without Step 6 PASS is forbidden.
- **Do not auto-apply P1/P2**: Qualitative assessment is the user's judgment area.
- **No auto-fix loops beyond 3 attempts**: After 3 attempts with violations still present, explicitly hand off to the user (infinite-loop prevention).

## ASTRA integration points

| Timing | Invocation |
|--------|-----------|
| Just before PR after feature development | `/design-redesign --diff --apply` |
| Legacy component refactor | `/design-redesign src/components/legacy/ --apply --pr` |
| Sprint retrospective | `/design-redesign src/` (report only) |
| CI gate (future) | `/design-redesign --diff` + non-zero exit code on P0 |

## Evaluation scenarios

1. **New project (0 violations)**: All files use only DESIGN.md tokens → "no violations" report and immediate exit.
2. **Legacy (mass violations)**: 100 violations. P0 auto-applied, then P1 batch-confirmed. Re-verification PASS in 1 attempt.
3. **Qualitative-only violations (tokens all correct)**: hover-only / purple gradient cliché etc. detected only by designer-persona. Structural fixes confirmed one-by-one with the user.

## Four-principles application

- **Think Before Coding**: Generate the Step 4 report first and give the user a chance to review. No jumping straight to fixes.
- **Simplicity First**: Token substitution is mechanical; structural changes are conservative. Do not arbitrarily apply auto-inferred "better designs".
- **Surgical Changes**: Only P0 is auto-applied. P1/P2 stay in user space. Do not cram all changes into a single PR.
- **Goal-Driven Execution**: Step 6 re-verification is the explicit PASS criterion. Do not exit while violations remain.
