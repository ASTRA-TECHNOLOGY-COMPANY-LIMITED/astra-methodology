---
name: skill-author
description: >
  Creates new SKILL.md files or refactors existing skills to comply with the
  ASTRA skill best practices guide (docs/development/skill-best-practices.md).
  Use when user mentions "new skill", "create skill", "SKILL.md", "skill
  authoring", "스킬 작성", "스킬 만들기", or when editing any file matching
  skills/**/SKILL.md.
paths:
  - "skills/**/SKILL.md"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion
---

# Skill Author

Writes a new SKILL.md or refactors an existing skill to comply with the ASTRA best practices. The SSoT is `docs/development/skill-best-practices.md` (hereafter BP); this skill *partially references* BP's 13 sections step-by-step — never load the whole file (BP §1 "Concise is key", §4 progressive disclosure).

## 0. Mode Decision

Confirm the mode via user input or `AskUserQuestion`.

| Mode | Trigger | Entry point |
|------|---------|-------------|
| **new** | "write new skill", empty directory, `/skill-author <name>` | Step 1 |
| **refactor** | existing SKILL.md argument, "improve this skill" | Step 5 |
| **lint-only** | "validation only", "checklist only" | Delegate to `/skill-lint` command (this skill exits) |

## 1. Collect Base Metadata (new mode)

Ask the four questions *at once* with `AskUserQuestion` to reduce user load:

1. **Skill name** (kebab-case, 64 chars, "anthropic"/"claude" forbidden)
2. **Type**: auto-trigger / validation-utility / meta / interactive-domain
3. **Side-effect risk**: yes/no (yes → `disable-model-invocation: true`)
4. **Permission scope**: read-only / file edits / Bash execution / external tools

Apply BP §12 ASTRA conventions based on the answers:
- auto-trigger / validation / utility / meta → English `description: >` block
- interactive-domain → English `description: "..."` single line
- For meta skills, add `paths` glob as a supplementary trigger (BP §12.1)

## 2. Write the Frontmatter

Apply the BP §2 field table and the §3 description 7 principles. If needed, Read only BP §2-3:

```bash
sed -n '25,63p' docs/development/skill-best-practices.md
```

### 2.1 Description self-check

Immediately self-check the description against these patterns:

| Violation | Pattern | Action |
|-----------|---------|--------|
| First-person self-introduction | First-person phrases ("I can", "I will", "you can use") | Rewrite in third person as "Does X. Use when..." |
| Vague verbs | "helps with", "does stuff" | Replace with concrete verbs (validates, generates, extracts...) |
| Missing trigger keywords | "Use when" absent | Add "Use when [situation 1], [situation 2], or when user mentions [keyword]" |
| Over 1,024 chars | `wc -c` result | Compress the core use case into the first sentence |

## 3. Design the Body Steps

Match BP §6 freedom levels and §7 workflow patterns:

| Freedom | Format | Suitable domain |
|---------|--------|-----------------|
| High | Text guide | Code review, design |
| Medium | Template + parameters | Document generation |
| Low | Fixed script | DB migration, CI |

Structure complex multi-step work as a **checklist + validation loop**:

```markdown
- [ ] Step N: action
- [ ] Step N+1: validation (on failure, return to Step N)
```

### 3.1 User interaction points

Recommend using `AskUserQuestion` at these moments:
- Mode/direction decision (right after start)
- Design choices that cannot be applied automatically (color/tone, manual grouping, etc.)
- 1–3 core decisions (HITL gate)

Too many questions increase user burden — bundle them together or proceed with defaults and confirm after the fact.

## 4. Automatic Anti-pattern Blocking

If the SKILL.md body being written/edited contains any of the following 6 patterns, block immediately:

1. **Windows paths** — backslash separators
2. **Time-sensitive expressions** — "Before/After/Until {date}" style
3. **First-person description** — "I can", "I will", "you can use", etc.
4. **3-level nested references** — another `references/` link from inside a references file
5. **Vague verbs** — "helps with", "does stuff", "processes things"
6. **Unqualified MCP tool references** — missing server-name prefix

The *exact grep commands* for each pattern are separated into [`references/anti-pattern-grep.md`](references/anti-pattern-grep.md) — inlining them in the body would cause grep meta-characters to false-positive against the Windows-path detection regex. See BP §8 for the full list of 10 anti-patterns (if needed, `sed -n '132,143p' docs/development/skill-best-practices.md`).

## 5. Refactor Mode

1. Read the target SKILL.md
2. Invoke `/skill-lint <path>` to receive the 13-check result
3. Classify violations into P0/P1/P2:
   - **P0** (auto-fix): description 1st→3rd person, Windows path → forward slash, vague verb replacement
   - **P1** (user confirmation): over 500 lines → references split, side-effect detected → add `disable-model-invocation`
   - **P2** (flag only): 4-principle general inspection, consistent terminology, scenario reinforcement
4. Apply P0 immediately; for P1 use `AskUserQuestion`; leave P2 in the report
5. After fixes, re-run `/skill-lint` to verify regression

## 6. Progressive Disclosure Split Gate

If `wc -l <SKILL.md>` exceeds **500 lines**, recommend a split to the user:

```
skills/<name>/
├── SKILL.md            ← table of contents / entry point (≤500 lines)
├── references/         ← detailed materials (one level deep)
│   ├── domain-a.md
│   └── domain-b.md
├── scripts/            ← executable scripts
└── assets/             ← templates / resources
```

Split rules (BP §4):
- All reference links must come *directly* from SKILL.md (one level deep)
- References over 100 lines need a table of contents at the top
- Split by domain (`reference/finance.md` ↔ `reference/sales.md`)

## 7. Write Evaluation Scenarios (Evaluation-Driven Development)

Per BP §9, after the skill is complete, write *at least 3* evaluation scenarios in `references/evals.md` in the same directory:

```markdown
# {{skill-name}} Evaluations

## Scenario 1: <representative use case>
- Input: <user utterance or argument>
- Expected: <which skill should be invoked and what steps should run>
- Pass criteria: <verifiable result>

## Scenario 2: <edge case>
...

## Scenario 3: <misuse / negative>
...
```

Establish the baseline by attempting the same task without the skill.

## 8. Final Checklist

When authoring/editing is finished, pass all 13 items of BP §13 — this skill delegates to `/skill-lint`:

```bash
/skill-lint skills/<name>/SKILL.md
```

Done if the report is 13/13 PASS. If any FAIL/WARN remain, return to Step 5 (refactor).

## 9. CLAUDE.md Update Notice (user task)

A new skill usually also needs one line added to the **Skill Catalog table** in `CLAUDE.md`. This skill does not update it automatically — emit a one-line notice so the user decides the table format and placement (section):

> Add a `/<skill-name>` row to the Skill Catalog table in `CLAUDE.md`. Format: `| /<skill-name> | <one-line English description> |`

## 10. Version Bump Notice (user task)

Adding a new skill is a minor bump (`x.+1.0`). Only when the user signals an intent to push to main, emit:

> Bump the `version` field in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` by +1 minor. (Check current: `cat .claude-plugin/plugin.json | jq .version`)

This skill never bumps the version on its own.

---

**Reference location guide** (use when partially referencing BP):

| Information needed | BP section | Line range (approx.) |
|--------------------|------------|----------------------|
| Frontmatter fields | §2 | 25-38 |
| Description 7 principles | §3 | 41-63 |
| Progressive Disclosure | §4 | 66-84 |
| 10 anti-patterns | §8 | 132-144 |
| ASTRA conventions | §12 | 182-225 |
| 13-item checklist | §13 | 229-243 |
