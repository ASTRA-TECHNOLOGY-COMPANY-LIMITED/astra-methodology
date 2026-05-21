---
description: Validates a SKILL.md file against the ASTRA skill best practices 13-point checklist and reports pass/fail per item
argument-hint: "<path to SKILL.md or skill directory> (omit to auto-detect from git status)"
allowed-tools: Read, Glob, Grep, Bash
---

# Skill Lint

Validate a SKILL.md against the ASTRA skill best practices checklist (`docs/development/skill-best-practices.md` §13).

> For interactive authoring/refactoring, use the `/skill-author` skill instead. This command is read-only validation.

## Resolve Target

```bash
# Case 1: explicit path
TARGET="$ARGUMENTS"

# Case 2: directory → auto-detect SKILL.md inside
if [ -d "$TARGET" ]; then TARGET="$TARGET/SKILL.md"; fi

# Case 3: no args → auto-detect from git status
if [ -z "$ARGUMENTS" ]; then
  TARGET=$(git status --porcelain | grep -E 'skills/[^/]+/SKILL\.md' | awk '{print $2}' | head -1)
fi
```

If still empty, abort and ask the user for an explicit path.

## Check Procedure

1. Read the target SKILL.md
2. Parse YAML frontmatter (between leading `---` markers)
3. Run each check below — categorize as **Auto** (deterministic), **Semi-auto** (grep + user confirmation), or **Manual** (qualitative flag)
4. Emit the verdict table

## Checklist (13 items from best-practices.md §13)

| # | Item | Auto/Semi/Manual | Check Method |
|---|------|------------------|--------------|
| 1 | description 3rd-person + What + When + trigger keywords | **Auto** | `grep -iE '\b(I (can|will|am)|you can use|let me)\b'` in description → FAIL if any match. `grep -iE '\b(use when|when (the user|you))\b'` → require ≥1 match for trigger keyword |
| 2 | Language policy compliance | **Semi-auto** | Detect description language by Hangul ratio (`grep -c '[가-힣]'`). Auto-trigger / validation-utility / meta type must use `description: >` block (English). Interactive-domain type must use `description: "..."` single line (Korean). Cross-check `description` block style with the declared type — ask user to confirm type if ambiguous |
| 3 | Body ≤ 500 lines | **Auto** | `wc -l SKILL.md` — strip frontmatter (`awk '/^---$/{n++; next} n==2'`) then count |
| 4 | Forward-slash paths only | **Auto** | `grep -nE '[A-Za-z_-]+\\\\[A-Za-z_]'` — any match in body = FAIL (Windows path) |
| 5 | References one level deep | **Auto** | For each `references/*.md` linked from SKILL.md, `grep -nE '\]\(references/' references/*.md` — any match = nested reference FAIL |
| 6 | No time-sensitive expressions | **Auto** | `grep -niE '(before|after|until|as of) ((jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* (19\|20)[0-9]{2}\|(19\|20)[0-9]{2})'` — match = WARN |
| 7 | Consistent terminology | **Semi-auto** | If user provides `--terms field,box,element` arg, grep each candidate and report counts so user can pick a canonical term. Without args, emit MANUAL flag |
| 8 | `allowed-tools` specified | **Auto** | Frontmatter must contain `allowed-tools:` key — absent = FAIL |
| 9 | Side-effect risk → `disable-model-invocation: true` | **Semi-auto** | If body contains `git push`, `gh pr`, `npm publish`, `rm`, `deploy`, `merge` keywords AND frontmatter lacks `disable-model-invocation: true` → WARN with user confirmation prompt |
| 10 | Background-knowledge skill → `user-invocable: false` | **Semi-auto** | If body lacks `AskUserQuestion`, `ExitPlanMode`, and any interactive question phrasing AND frontmatter lacks `user-invocable: false` → WARN. Inverse: if `user-invocable: false` is set but interactive elements exist → also WARN |
| 11 | 4 principles (Think Before / Simplicity / Surgical / Goal-Driven) | **Manual** | Qualitative flag only — emit a section listing potential violations for human review (e.g., body adds abstractions without clear trigger, scope creep beyond declared purpose) |
| 12 | Persona agent guard prefix (agents only — N/A for skills) | **Auto** | Skip for SKILL.md targets. If target is `agents/*-persona.md`, require `[EXPLICIT-INVOCATION-ONLY — DO NOT AUTO-MATCH]` as the first description line — absent = FAIL |
| 13 | ≥3 evaluation scenarios | **Auto** | `[ -f references/evals.md ]` AND count `## Scenario` headings ≥ 3 — absent or fewer = WARN |

## Output Format

```
Skill Lint Report: <path>
═══════════════════════════════════════════════════

| # | Item                              | Mode      | Verdict | Detail / Location           |
|---|-----------------------------------|-----------|---------|------------------------------|
| 1 | description 3rd-person + trigger  | Auto      | PASS    | -                            |
| 2 | Language policy                   | Semi-auto | PASS    | English block, meta-skill OK |
| 3 | Body ≤ 500 lines                  | Auto      | FAIL    | SKILL.md = 680 lines         |
| 4 | Forward-slash paths               | Auto      | PASS    | -                            |
| ...                                                                                |
═══════════════════════════════════════════════════
Summary: PASS 10/13 · FAIL 1/13 · WARN 2/13 · MANUAL 1/13

Next steps:
- FAIL → must fix before merge
- WARN → user confirmation; suggested fix listed in Detail column
- MANUAL → human review only; not auto-blocking
```

If any **FAIL** remains, recommend invoking `/skill-author` in refactor mode:

> `/skill-author <path>` — interactive refactor flow will auto-apply P0 fixes and prompt for P1 decisions.

## Severity Criteria

- **FAIL** (Error): Hard violations of explicit BP rules (Windows paths, 1st-person description, missing `allowed-tools`, persona guard missing)
- **WARN** (Warning): Soft violations needing user judgment (500-line overage, side-effect signals, missing evals)
- **MANUAL** (Info): Qualitative items that require human review (4 principles, terminology consistency without `--terms` arg)
- **PASS**: No issues detected
