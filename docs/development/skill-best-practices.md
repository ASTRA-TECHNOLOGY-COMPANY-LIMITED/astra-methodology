# Claude Code Skill Authoring Best Practices

This plugin authors and maintains many SKILL.md files directly. Use this document as the SSoT (Single Source of Truth) when adding a new skill or modifying an existing one.

**Official guides (Anthropic)**
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Agent Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

This document is an integrated best-practice guide that combines the official guides above with ASTRA project conventions.

---

## 1. Core Philosophy — 4 Principles

| Principle | Meaning |
|-----------|---------|
| **Concise is key** | Once loaded, SKILL.md stays in the context for the entire session. Every line is a *repeated* token cost. Keep the body **under 500 lines**. One accepted exception: `pr-merge` (~535) — after all §13.7-safe extraction, what remains is executable guards and merge-safety decision rules that must stay inline; `scripts/lint-skills.sh` reports the overage as WARN, and any *new* skill exceeding 500 must extract, not cite this exception |
| **Claude is already smart** | Omit general knowledge Claude already knows ("what is a PDF", "how to use a library"). Ask of every sentence: "Does this line justify its token cost?" |
| **State, don't narrate** | Write only what to do, not lengthy explanations of how or why. Same principle as CLAUDE.md authoring |
| **Standing instructions** | Write the skill body as *persistent instructions* that continue to apply after the first invocation. Listing one-off steps alone makes them un-referenced in later turns |

---

## 2. Frontmatter Fields

| Field | Constraint | Notes |
|-------|------------|-------|
| `name` | 64 chars, lowercase/digits/hyphens | "anthropic" and "claude" reserved; no XML tags |
| `description` | Within 1,024 chars, must not be empty | Core of auto-triggering. **Must be third-person, noun-form** |
| `when_to_use` | Combined with description, capped at 1,536 chars | For reinforcing trigger phrases/examples |
| `allowed-tools` | Space-separated or YAML list | Permission pre-approval — least-privilege principle |
| `disable-model-invocation` | bool | Workflows with side effects (`/deploy`, `/commit`) should be `true` |
| `user-invocable` | bool | For background-knowledge skills, set `false` to hide from menu |
| `paths` | glob pattern | Auto-load only when working on specific files |
| `model` / `effort` | model / reasoning-strength override | Validation skills use haiku; analysis skills use sonnet |
| `context: fork` | Subagent isolated execution | Use only for skills with an explicit task |

---

## 3. Description Authoring — 7 Principles

1. **Write in third person**: "Processes Excel files..." (O) / "I can help you..." (X) / "You can use this to..." (X) — the description is injected into the system prompt, so point-of-view consistency matters
2. **Include both What + When**: what it does + when it should be invoked
3. **State trigger keywords explicitly**: pattern of `Use when [situation 1], [situation 2], or when user mentions "[keyword]"`
4. **Place the core use case in the first sentence**: it may get cut off at the 1,536-char cap
5. **Auto-trigger skills → English `description: >` block form**: LLM matching accuracy is higher in English
6. **Explicit-invocation entry points → English `description: "..."` single-line form**: all descriptions are English regardless of skill type (see §12.1) — the end user's runtime output language is governed by `/select-language`, never by the description
7. **Forbid ambiguous wording**: "Helps with documents", "Does stuff with files" → reject. Specify concrete behavior and triggers

**Good example (auto-trigger)**:
```yaml
description: >
  Validates Java/TypeScript/React Native/Python/CSS/SCSS code against project
  coding conventions. Use when reviewing code changes, before committing,
  after implementing features, or when the user asks to "check code quality".
```

**Good example (explicit invocation)** — single-line English form:
```yaml
description: "Authors a Blueprint (design document) with data flow, schema, and logic design — implementation code excluded. Use when designing a feature before implementation."
```

---

## 4. Progressive Disclosure

```
skills/my-skill/
├── SKILL.md              ← table of contents (under 500 lines)
├── references/           ← detailed materials
│   ├── api.md
│   └── examples.md
├── scripts/              ← executable scripts
│   └── validate.sh
└── assets/               ← templates / resources
```

- **SKILL.md = the table of contents**; split detailed materials into `references/`, `scripts/`, `assets/`
- **All reference links from SKILL.md, directly** (one level deep). Nested references (SKILL → A → B) are easy for Claude to miss via partial reads (e.g., `head -100`)
- **Reference files over 100 lines**: include a table of contents at the top — so a partial read still reveals the full scope
- **Split by domain**: if a skill spans multiple areas, separate into `reference/finance.md`, `reference/sales.md`, etc., to block loading unrelated context
- **Scripts: state "execute" vs "read" intent explicitly** — "Run `analyze.py`" (execute) / "See `analyze.py` for the algorithm" (read). Most cases are execute

---

## 5. Skill vs Command vs Agent — distinctions

| Aspect | Skill | Command | Agent |
|--------|-------|---------|-------|
| Auto-load | ✓ (description-based) | ✗ | ✗ (explicit invocation) |
| Multi-file support | ✓ (SKILL.md + references) | ✗ | AGENT.md only |
| Context | Parent context | Parent context | Isolated (optional) |
| Use | Persistent workflow | Quick single invocation | Role-based delegation |

**Selection criteria**:
- Multi-step + user interaction + context preservation → **Skill**
- Simple command + delegation to a data file → **Command**
- Senior-perspective delegation + isolated execution → **Agent**

---

## 6. Degrees of Freedom Matching

| Freedom | When to apply | Form |
|---------|---------------|------|
| **High** (text guidance) | Multiple approaches valid, context-dependent | Guide such as "Analyze code structure and suggest improvements" |
| **Medium** (parameterized scripts) | Pattern exists but some variation allowed | Template functions + parameters |
| **Low** (fixed scripts) | Fragile / consistency-critical, fixed order | "Run exactly this command, do not modify" |

DB migrations = low / code review = high

---

## 7. Workflow & Feedback Loop Patterns

Structure complex multi-step work as a **checklist + verification loop**:

```markdown
## Form filling workflow
- [ ] Step 1: run analyze_form.py
- [ ] Step 2: write fields.json
- [ ] Step 3: run validate_fields.py (on failure, return to Step 2)
- [ ] Step 4: run fill_form.py only when validation passes
- [ ] Step 5: final verification via verify_output.py
```

Write explicit loops at validation steps — matches the Goal-Driven Execution of the ASTRA 4 principles.

---

## 8. Anti-Patterns — Strictly Forbidden

1. **Windows-style paths**: `scripts\helper.py` ❌ → `scripts/helper.py` ✅ (cross-platform)
2. **Time-bound information**: "Before August 2025, use the old API" ❌ → split into a separate `## Old patterns` section + `<details>`
3. **Too many choices**: "Use pypdf, or pdfplumber, or PyMuPDF, or..." ❌ → one default + an escape hatch if needed
4. **Vague description**: "Helps with files", "Does stuff" ❌ → concrete behavior + trigger keywords
5. **Nested references 3+ levels deep**: SKILL → A → B → C ❌ → link every reference directly from SKILL.md
6. **Voodoo magic numbers**: `TIMEOUT = 47` ❌ → state the rationale in a comment (`# Most requests complete within 30s`)
7. **Error punting**: do not let a script fail and rely on "Claude figures it out" — write explicit error handling + fallback
8. **Inconsistent terminology**: "field/box/element/control" mixed ❌ → one term per concept
9. **Self-introducing description**: "I can help with..." / "You can use this..." ❌ → always third person
10. **Unqualified MCP tool references**: `bigquery_schema` ❌ → `BigQuery:bigquery_schema` (server-name prefix)

---

## 9. Evaluation-Driven Development

The skill development cycle recommended by Anthropic's official guide:

1. Without a skill, attempt representative tasks with Claude → record failure/missing points
2. Write **at least 3** evaluation scenarios (input + expected behavior)
3. **Measure the baseline**, then write a minimal SKILL.md — do not pre-document hypothetical requirements
4. Run evaluation → compare against baseline → iterate

---

## 10. Per-Model Testing

A skill is a layer added on top of a model. Validate on each model you plan to use (Haiku/Sonnet/Opus):

- **Haiku** — is the guidance sufficient? (suits validation/rule skills)
- **Sonnet** — clear and efficient? (suits analysis/review skills)
- **Opus** — over-explained?

Align with the ASTRA model-selection convention:
- `*-validator` → `haiku` (rule-based validation, fast)
- `*-reviewer` / `*-analyzer` / `*-runner` / `*-persona` → `sonnet` (complex analysis, accurate)

---

## 11. Iterative Development (Claude A ↔ Claude B Pattern)

The most effective way to author skills is to use Claude itself:

- **Claude A**: an instance that helps design/refactor the skill ("Create a Skill that captures this pattern")
- **Claude B**: a fresh instance that tests the authored skill against real tasks
- Loop: **observe → feed back to Claude A → improve → re-test**

---

## 12. ASTRA Project Conventions

### 12.1 Description Language Policy

**All skill `description` fields are written in English** — the only thing that varies by skill type is the *form*:

| Type | Language | Form | Example skills |
|------|----------|------|----------------|
| Auto-trigger skill | English | `description: >` block | `coding-convention`, `data-standard`, `code-standard`, `sprint-progress` |
| Validation/utility skill | English | `description: >` block | `project-checklist`, `astra-setup`, `sprint-init`, `astra-guide`, `test-run` |
| Meta skill | English | `description: >` block + `paths` glob | `skill-author` — multi-step interactive, but "edit/create SKILL.md" must trigger via both natural language and paths |
| Interactive domain skill | English | `description: "..."` single line | `service-planner`, `blueprint`, `handoff-publish`, `manual-generator`, `pr-merge`, `autorun` |

**Rationale**:
- The LLM matches English descriptions more accurately (this favors both auto-trigger and intent routing), and the repo's authoring language is English
- The end user's runtime output language (Korean / Vietnamese / English) is controlled by `/select-language` — description language does not affect deliverable language
- The pre-v5.13 policy of Korean descriptions for interactive domain skills is **retired**; do not reintroduce Korean descriptions

### 12.2 Persona Agent Guard

The persona agents (`tester-persona`, `designer-persona`, `developer-persona`) must include the following guard prefix as the first line of their description:

```
[EXPLICIT-INVOCATION-ONLY — DO NOT AUTO-MATCH]
```

Persona agents are explicit-invocation only and must not be auto-triggered.

### 12.3 Broad Auto-Builder Exception

The following *broad-deliverable producing skills* generate full-stack deliverables explicitly requested by the user, so they are not bound by the "Simplicity First" scope limit:

- `/service-planner`, `/blueprint`, `/manual-generator`, `/catalog-generator`, `/landing-page`
- `/handoff-publish`, `/project-init`, `/sprint-init`, `/autorun`

However, the *individual code* authored inside them still follows the ASTRA 4 principles (Think Before / Simplicity / Surgical / Goal-Driven).

### 12.4 Naming Conventions

- `*-validator` → rule validation (haiku, read-only)
- `*-reviewer` → deliverable quality review (sonnet, read-only)
- `*-runner` → integrated execution (sonnet, read-only)
- `*-analyzer` → pattern/metric analysis (sonnet, read-only)
- `*-persona` → senior-perspective delegation (sonnet, read-only, explicit-invocation only)

All agents are read-only via `disallowedTools: Write, Edit` — they analyze and report only, never modifying files.

---

## 13. Harness Robustness Conventions (v5.12+)

Conventions that make skills reliable across model tiers, established by the 2026-07 harness hardening. These are structural-harness mechanisms (machine contracts, code-enforced state, verify-before-claim) — per the Claude 5 prompting guidance they remain in force on frontier models too; what scales down on stronger models is prose-level emphasis, never these contracts (see `docs/development/claude-5-prompting-guidance.ko.html`). Apply to every new/modified skill:

1. **Machine-parseable contract lines** — a skill/agent whose result gates another skill's branch MUST emit a single-line, greppable verdict as the FINAL line, and the consumer MUST parse only that line (never prose). Existing contracts: `ASTRA_TEST_RESULT: PASS|FAIL passed=N failed=N total=N skipped=N` (test-run), `ASTRA_REVIEW_RESULT: score=N verdict=PASS|FAIL p0=N` (blueprint/planner-reviewer), `ASTRA_GATE_RESULT: verdict=... critical=N warning=N info=N` (quality-gate-runner), `SEVERITY_COUNTS: critical=N high=N medium=N low=N` (pr-merge Step 8 reviewer contract), `ASTRA_LOOP_RESULT: score=N verdict=PASS|FAIL p0=N iter=I` (loop-verifier ← /loop, sprint pipeline Step 5.4.5, autorun Stage 7.6), `ASTRA_SCREEN_RESULT: score=N verdict=PASS|FAIL p0=N iter=I` (screen-verifier ← screen-quality-loop, /service-planner Step 6.F.6). **Line absent = FAIL/unverified, never 0 issues.** Producer and every consumer MUST state the identical field list — adding a field on the producer without updating this inventory and all consumers is a contract break.
2. **Cross-invocation state protocol** — shell variables do NOT survive between Bash tool calls. Persist workflow state via `astra_state_set KEY "$VALUE" [scope]` / `astra_state_load [scope]` (worktree-helpers.sh; scoped per work branch). Every bash fence that consumes persisted variables carries the literal PREAMBLE as its first lines (resolve `PLUGIN_ROOT` → `source worktree-helpers.sh` → `astra_state_load`). Invisible prose rules are not enough for literal-minded models — the code in the fence is the only reliable enforcement.
3. **Verify-before-claim** — never print a success banner or set a success flag without a captured verification in the same session: `gh pr view --json state` == MERGED after merges, test-runner exit codes after fixes, `[ -f ]` after file generation. Guard every destructive command with `[ -n "$VAR" ]` and re-derive empty values from git/gh; never run destructive commands with empty variables.
4. **zsh-safety (the Bash tool runs zsh on macOS)** — no `mapfile`/`readarray` (use newline-joined strings or `while IFS= read`), no `local status` (read-only special var in zsh — assignment kills the shell), no reliance on word-splitting unquoted variables (`for x in $LIST` and `cmd $FLAGS` do NOT split in zsh — use `while read` loops and arrays `"${ARR[@]}"`), no `ls glob 2>/dev/null` for may-not-match patterns (zsh NOMATCH errors before redirection — use `find`), no PCRE lookahead in `grep -E`.
5. **Regexes live in code fences, not markdown tables** — table-cell `\|` escaping silently destroys alternation when copied into grep.
6. **"Unable to verify" beats guessing** — validators/reviewers must have an explicit unable-to-verify/unable-to-score reporting path (including a template variant), mandatory lookup commands for dictionary/data checks, and score formulas with defined numerator/denominator + minimum-sample rules.
7. **Extraction boundary** — when splitting content to `references/`, move ONLY template/reference material. Executable guards, `source` lines, decision rules, success criteria, and HITL logic stay inline in SKILL.md.

## 14. ASTRA New/Modified SKILL.md Checklist

- [ ] description in third person + What + When + trigger keywords
- [ ] Auto-trigger skill → English `description: >` block / interactive skill → Korean `description: "..."` single line
- [ ] Body within 500 lines (split into `references/`, `scripts/`, `assets/` when exceeded)
- [ ] All file paths use forward slashes (`/`)
- [ ] Reference file links one level deep
- [ ] No time-bound information (if present, isolate under an `## Old patterns` section)
- [ ] Terminology used consistently
- [ ] `allowed-tools` specified + least privilege
- [ ] Side-effect risk → `disable-model-invocation: true`
- [ ] Background-knowledge skill → `user-invocable: false`
- [ ] No violation of the 4 principles (Think Before / Simplicity / Surgical / Goal-Driven)
- [ ] Persona agent description keeps the `[EXPLICIT-INVOCATION-ONLY — DO NOT AUTO-MATCH]` guard prefix
- [ ] Pre-validated against at least 3 evaluation scenarios
