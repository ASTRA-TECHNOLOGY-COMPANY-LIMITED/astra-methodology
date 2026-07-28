# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**astra-methodology** is a Claude Code plugin that implements the ASTRA (AI-augmented Sprint Through Rapid Assembly) methodology. It provides Sprint 0 project initialization, coding convention enforcement (Java/TypeScript/React Native/Python/CSS/SCSS), Korean public data standard enforcement, international code standards (ISO 3166-1/2, ITU-T E.164), naming validation, and quality gates for Korean enterprise software development.

This is NOT an application codebase — it is a Claude Code plugin consisting of skills, agents, hooks, commands, and scripts that get installed into target projects.

## Repository Structure

```
astra-methodology/
├── skills/              # Claude Code skills (each subdir has SKILL.md with full details)
├── agents/              # Specialized subagents (read-only, *-validator/*-reviewer/*-runner/*-analyzer/*-persona)
├── commands/            # Slash commands (lighter than skills)
├── hooks/               # PostToolUse hooks (hooks.json)
├── scripts/             # Shell scripts for hooks and verification
├── data/                # Standard dictionary + ISO/ITU code JSON files (large — use jq queries)
├── docs/                # Reference design/UX/dev guides (ux/, catalog/, manual/, plugin/, development/)
└── .claude-plugin/      # Plugin manifest (plugin.json, marketplace.json)
```

For per-skill details, read each `skills/{name}/SKILL.md`. For per-agent capabilities, read each `agents/{name}.md`. For full data file inventory, see `data/`.

## Key Concepts

### ASTRA Methodology

- **VIP Principles**: Vibe-driven Development, Instant Feedback Loop, Plugin-powered Quality
- **Sprint cycle**: 1 week
- **Team roles**: VA (Vibe Architect), PE (Prompt Engineer), DE (Domain Expert), DSA (Design System Architect)
- **Quality Gates**: Gate 1 (write-time/automatic), Gate 2 (review-time), Gate 2.5 (design review), Gate 3 (release-time)

### Korean Public Data Standard (행정안전부 공공데이터 공통표준)

The plugin enforces naming conventions from the Korean Ministry of the Interior and Safety's public data standard dictionary. Key rules:

- **Table prefixes**: `TB_` (general), `TC_` (code), `TH_` (history), `TL_` (log), `TR_` (relation)
- **Column suffixes**: `_YMD` (date), `_DT` (datetime), `_AMT` (amount), `_NM` (name), `_CD` (code), `_NO` (number), `_CN` (content), `_YN` (yes/no), `_SN` (sequence), `_ADDR` (address)
- **Forbidden words**: `standard_words.json` contains a `금칙어목록` field; violations trigger warnings with standard alternatives

### Coding Convention Enforcement

The plugin auto-applies coding conventions when editing language-specific files:

- **Java** (Google Java Style Guide): 2-space indent, 100-char limit, K&R braces, no wildcard imports, `UpperCamelCase` classes, `lowerCamelCase` methods, `UPPER_SNAKE_CASE` constants
- **TypeScript** (Google TypeScript Style Guide): Prettier formatting, no `export default`, no `any`, no `var`, no `.forEach()`, `===`/`!==` required, named exports only
- **React Native** (Airbnb React/JSX + Obytes RN Starter + React Native Official): Complementary layer on TypeScript convention for RN/Expo projects. `kebab-case` files, functional components only, `PascalCase` components, `StyleSheet.create()` or NativeWind, TanStack Query + Zustand, Expo Router, max 3 params/110 lines per function, no inline styles, no class components
- **Python** (PEP 8): 4-space indent, 79-char limit, `snake_case` functions, `CapWords` classes, `is None` required, no bare `except:`
- **CSS/SCSS** (CSS Guidelines + Sass Guidelines): 2-space indent, 80-char limit, BEM naming, no ID selectors, max 3-level nesting, mobile-first media queries

Reference files are in `skills/coding-convention/` (e.g., `java-coding-convention.md`, `typescript-coding-convention.md`, `react-native-coding-convention.md`). For mobile projects, the coding convention skill additionally references `docs/ux/mobile-design-guide.md`.

### Vibe Coding Design & Animation Guides

The plugin provides comprehensive design and animation guides under `docs/ux/` that should be referenced during all UI design and implementation work:

- **`vibe-coding-design-guide.md`**: anti-AI aesthetics prompting, reference-anchored design, constraint-first approach, design token injection, tool comparison, DO/DON'T patterns
- **`vibe-coding-animation-guide.md`**: CSS native (View Transitions API, Scroll-Driven Animations, `@starting-style`, `linear()` springs), Framer Motion/GSAP/Lottie/Rive, micro-interactions, performance, 3-tier motion accessibility, Disney 12 principles

These guides are automatically loaded by `/service-planner` (Step 6 HTML mockup generation) and should be referenced by any skill or workflow that involves UI design, design system work, or animation implementation.

### International Code Standards (ISO 3166-1/2, ITU-T E.164)

The plugin auto-applies international code standards when implementing phone number inputs, country/region selectors, and address forms:

- **ISO 3166-1**: alpha-2 country codes (e.g., `KR`, `US`, `JP`) — stored as `NATN_CD CHAR(2)`
- **ISO 3166-2**: region/subdivision codes (e.g., `KR-11`, `US-CA`) — stored as `RGN_CD VARCHAR(6)`
- **E.164**: international phone numbers (e.g., `+821012345678`) — stored as `INTL_TELNO VARCHAR(15)`

Data files: `iso_3166_1_countries.json` (249 countries), `iso_3166_2_regions.json` (653 regions), `country_calling_codes.json` (245 calling codes).

### Sprint Isolation — Worktree-always (v5.19+), Worktree-based (v5.0+)

**v5.19+ worktree-always isolation**: every sprint runs inside an isolated worktree at `.worktrees/sprint-<N>-<name>/` holding the `feat/sprint-<N>-<name>` branch. **Sprint work is never performed in the main worktree** — it stays on `dev` for the whole sprint. The only main-worktree step in the sprint lifecycle is `/blueprint`: the blueprint is authored, reviewed, committed, and **pushed on `dev` first**; the sprint worktree is then created from `origin/dev` (so it contains the blueprint from birth) and everything downstream — scenarios, implementation, tests, the PR — happens inside the worktree. The v5.16 adaptive/in-place mode (`ISOLATION_MODE=inplace`, `--isolated`, `IN_PLACE_SPRINT`) is removed.

**v5.16+ one-flow (retained)**: `/blueprint` and `/sprint-init` no longer stop after their authoring/scaffolding stage — they continue **in the same session** through `/test-scenario` → implementation → `/test-run` → an adversarial verification gate (`loop-verifier` with the fixed SPRINT PRESET rubric; exit = tests PASS ∧ score ≥ 90 ∧ P0 == 0, hard cap 5 iterations) → `/pr-merge`. The user is never instructed to `cd` or start a new session (KV-cache locality: one warm prefix from design through merge); the single `cd` into the worktree is performed by the skill itself. HITL fires only at real judgment points: blueprint design decisions, remaining Critical review issues, final merge confirmation, promotion target. `--scaffold-stop` (sprint-init) / `--design-only` (blueprint) restore the stop-early behavior; the shared pipeline SSoT is `skills/sprint-init/references/auto-pipeline.md`.

The worktree mechanism (v5.0+) prevents code/port interference across sprints in multi-session Claude Code environments:

- **Shared branches** (`main`, `master`, `staging`, `dev`): kept in the main worktree. The cascade merge (`staging → dev` only — `main → staging` is intentionally excluded) and promotions (`/pr-merge --staging`, `/pr-merge --main`) are also performed in the main worktree.
- **Integration branches** (v5.11+: `feat/<name>` / `fix/<name>` without the `sprint-` segment): persistent feature- or fix-level branches that aggregate one or more sprint PRs. They are the *unit of promotion* — `/pr-merge` Step 8.4.5 picks an integration branch and promotes it directly to `staging` (fast hotfix path) or via `dev` (standard path). Created in the main worktree on demand by `/pr-merge` Step 4.5; never auto-deleted.
- **Sprint worktree** (`.worktrees/sprint-<N>-<name>/`): created by `/sprint-init`, holding the `feat/sprint-<N>-<name>` branch (branched from a user-chosen source — `dev`/`staging`/`main`/`master`/custom in v5.11+; under the `/blueprint` flow always `origin/dev`, after the blueprint push). *All* feature code and tests for that sprint are written, committed, and pushed inside this worktree. **v5.9+ two-phase merge** (retained internally): `/pr-merge` invoked from inside the sprint worktree runs Sprint Phase (Step 4.5 integration-branch pick → commit → push → PR → code review → fix loop), then asks one "finalize now?" HITL (v5.16+) and performs the cross-worktree transition itself — the actual `gh pr merge`, the integration-branch promotion (Step 8.4.5), and worktree removal run from the main worktree in the same invocation. A standalone Main-Phase re-entry from the main worktree also works (auto-detects the pending sprint PR via `gh pr list --state open` filtered on `head ~ feat/sprint-*` and `base ~ ^(feat|fix)/`, with a backward-compat fallback to `base=dev` for pre-v5.11 PRs). With `--auto` (used by `/autorun` and `/sprint-init --auto`), the transition is auto-approved so unattended pipelines complete in one invocation.
- **Port isolation**: `/sprint-init` writes `.astra-worktree.env` inside the worktree. The port base is `base + 100*N` (e.g., sprint 2 → 3200). On collision detection, the helper shifts by +100. `/test-run` sources this file to launch the server on the sprint-specific port, and on shutdown releases the port through a 4-step cleanup (shell stop → SIGTERM → SIGKILL + children → verify).
- **dev-sync skill guards** (main-worktree-only, 4 skills): `service-planner`, `handoff-publish`, `manual-generator`, `catalog-generator` — all planning-phase deliverables, so they run in the main worktree (`dev`) before sprint start. `sprint-init`, which was guarded in v4.x, is responsible for worktree creation in v5.0+ and therefore remains main-worktree-only. `test-scenario` and `test-run` had their guards removed in v5.0+ so they can run inside sprint worktrees.
- **Helper script**: `scripts/worktree-helpers.sh` (use via `source`). Main functions: `astra_ensure_main_worktree`, `astra_create_sprint_worktree`, `astra_remove_sprint_worktree`, `astra_compute_port_base`, `astra_port_in_use`, `astra_write_worktree_env`, `astra_is_isolated_worktree`. Isolated-worktree detection compares `git rev-parse --git-dir` vs. `--git-common-dir` (not path matching).
- **`.gitignore`**: when initializing a target project (`init-project.sh`), `.worktrees/` is automatically registered.
- **Recommended workflow (v5.19+ — one command, one session)**:
  1. `/blueprint <feature-slug>` — invoked from the main worktree (`dev`). The skill: authors the blueprint **on `dev` in the main worktree** → runs blueprint-reviewer → commits → **pushes to `origin/dev`** → delegates to `/sprint-init --scaffold-only` to create the sprint worktree (`.worktrees/sprint-<N>-<slug>/`, branched from `origin/dev` — blueprint included) → **continues in the same session inside the worktree** (Step 8): `/test-scenario` → implementation → `/test-run` → adversarial verification gate (score ≥ 90 ∧ P0 == 0, max 5 iterations) → `/pr-merge` (merge confirmation + promotion target HITL) → cleanup, session back on `dev`, worktree removed.
  2. That's it — answer the HITL prompts as they surface (design decisions up front; merge/promotion at the end). `--design-only` stops after the dev push (no worktree — continue later with `/sprint-init <slug>`); `/sprint-init --scaffold-stop` scaffolds without running the pipeline; `/sprint-init --resume` recovers a crashed run in a fresh session.

  Skip cases / aborts for Step 1's location guards:
  - **Secondary blueprint in the same sprint** — cwd inside a sprint worktree (Priority 1) → the blueprint is authored there and committed to the existing sprint branch (no dev push; it merges via the sprint PR); the pipeline is NOT re-launched (the sprint's own flow is already driving).
  - **Non-dev/main/master branch on the main worktree** → the skill **aborts with error** (per v5.10+ policy). The user must run `git checkout dev` and re-invoke `/blueprint` (Priority 2 guard; a `feat/sprint-*` main-worktree branch is a pre-v5.19 in-place leftover).

  **Legacy workflow (pre-v5.10)** still works: explicitly invoke `/sprint-init <slug>` from `dev`, then run the prompt-map inside the worktree (its Feature 1.1 `/blueprint` invocation lands as a secondary blueprint on the sprint branch). The prompt-map Variant A (`SCAFFOLD_ONLY=0`) flow in `/sprint-init` remains intact for this case.

  A one-shot fallback flow is also supported: change files directly in the main worktree and invoke `/pr-merge` (Step 4.1 creates a temporary worktree).
- **Trade-off**: one worktree per sprint = one PR per sprint. Per-feature code-review granularity disappears and the rollback unit is the sprint. If small-unit review is required, split sprints smaller or use the fallback (main worktree + `/pr-merge`).

> **Version history (v4.x → v5.19.0)**: per-version change rationale lives in [docs/development/changelog-v5.md](docs/development/changelog-v5.md); the sections above authoritatively describe the current (v5.19.0) behavior.

### Hooks Architecture

`hooks/hooks.json` defines hooks that run automatically:

**PostToolUse hooks** (run after Write/Edit operations): a single dispatcher entry, **posttooluse-dispatch.sh**, reads the tool-input JSON once (fast-exit when no `file_path`) and fans out sequentially to the per-check scripts — each remains independently invokable with the same stdin-JSON contract:
1. **notify-design-doc-edit.sh** — detects design document edits
2. **check-forbidden-words.sh** — scans DB-related files for forbidden words from the standard dictionary
3. **validate-naming.sh** — checks table name prefixes in SQL, Java (@Table), TypeScript (@Entity), Python (__tablename__)
4. **track-sprint-progress.sh** — detects sprint-related file events and appends activity log entries to the sprint progress tracker
5. **notify-design-md.sh** (v5.4.0+) — when UI source files (src/components/, *.tsx, *.css, etc.) are edited and `docs/design-system/DESIGN.md` exists, emits a one-time-per-session advisory pointing to the DESIGN.md SSoT and `/design-audit`. Throttled to once per hour via marker file under `.claude/.astra-hooks/`. Skips the design system docs themselves and generated `design-tokens.css`. Non-blocking.
6. All PostToolUse hooks are non-blocking (exit 0) — they emit warnings only

**UserPromptSubmit hooks** (run when user submits a prompt):
1. **inject-feature-dev-cwd.sh** — when `/feature-dev` is invoked from inside a sprint worktree (`.worktrees/sprint-*`; the pre-v5.19 `.astra-worktrees/` path is still matched for legacy worktrees), injects cwd-anchored sprint paths into the LLM context so the external feature-dev plugin does not fall back to the main worktree (where uncommitted sprint files are not visible). Non-blocking (exit 0). No output when the trigger does not match.

### Hybrid Agent Architecture (Validators + Personas)

ASTRA uses a **hybrid agent strategy** that pairs workflow-driven skills with two distinct agent types:

#### Validator Agents (auto-triggerable, read-only)
Stateless quality checkers that report violations without modifying files. Activated automatically by skills or quality gates.

| Agent | Model | Gate | Purpose |
|-------|-------|------|---------|
| `astra-validator` | haiku | Setup | ASTRA project structure compliance |
| `naming-validator` | haiku | Gate 1 | DB naming standard (TB_/TC_/TH_/TL_/TR_, _YMD/_DT/_AMT...) |
| `convention-validator` | haiku | Gate 1 | Java/TS/Python/RN/CSS/SCSS coding convention |
| `design-token-validator` | haiku | Gate 2.5 | Hardcoded colors/fonts/spacing detection |
| `planner-reviewer` | sonnet | Gate 1.5 | `docs/planner/` 6-doc completeness, KPI/OKR traceability, Handoff convertibility |
| `blueprint-reviewer` | sonnet | Gate 2 | Blueprint quality + design-implementation consistency |
| `test-coverage-analyzer` | haiku | Gate 2 | Test strategy adherence + coverage gaps |
| `sprint-analyzer` | sonnet | Daily/Retro | Commit pattern + sprint progress analysis |
| `quality-gate-runner` | sonnet | Gate 3 | Integrated Gate 1/2/3 execution |
| `loop-verifier` | sonnet | `/loop` + sprint pipeline (per-iteration) | Adversarial target-achievement scoring against a frozen rubric — additive from 0, file:line evidence required, `ASTRA_LOOP_RESULT` tail line. Invoked only by `/loop` (user rubric) and the `/sprint-init`·`/blueprint` pipeline Step 5.4.5 (fixed SPRINT PRESET rubric), never auto-triggers |
| `screen-verifier` | sonnet | Screen authoring (per-batch) | Adversarial new-screen quality scoring against a fixed rubric — design-system application (35) · cross-screen layout consistency (30) · polish & sophistication (35), `ASTRA_SCREEN_RESULT` tail line. Invoked only by `screen-quality-loop` / `/service-planner` Step 6.F.6, never auto-triggers |

> **Wiring note**: `sprint-analyzer` and `quality-gate-runner` are intentionally not invoked by any skill — they are user-invoked entry points (Daily Scrum / retrospective analysis, and Gate 3 release checks respectively; target projects reference `quality-gate-runner` from their generated CLAUDE.md). This unwired state is by design, not an omission.

#### Persona Agents (explicit invocation only, read-only orchestrators)
Role-based mindset agents that bring senior-practitioner perspective. **Never auto-trigger** — must be explicitly invoked by the user (e.g., "as a tester", "as a designer", or their Korean equivalents "테스터 관점에서" / "디자이너로서") or by orchestrating skills.

| Persona | Model | When to Invoke | Hands back to |
|---------|-------|----------------|---------------|
| `tester-persona` | sonnet | Edge case discovery, scenario gap analysis, risk-based prioritization | `/test-scenario` or `/test-run` |
| `designer-persona` | sonnet | Design system audit, Vibe Coding aesthetic critique, WCAG 2.1 AA review, Screen ID handoff audit | `/service-planner` or `/handoff-publish` |
| `developer-persona` | sonnet | Architecture review, ASTRA 4-principle audit, code smell, OWASP security audit | `/pr-merge` or `/generate-entity` |

**Architectural principle**: Persona agents are **orchestrators, not executors**. They analyze and recommend, but all file edits happen back in the parent context — this preserves auto-applied skills (`coding-convention`, `data-standard`, `code-standard`) which only trigger on parent-context Write/Edit operations.

**When to use which**:
- Stateful multi-turn workflow with user interaction → **Skill**
- Stateless validation against rules → **Validator agent**
- Senior-practitioner mindset on a specific artifact → **Persona agent**
- Parallel role-based work → Multiple personas via `Task()` calls in parallel

### Skill Catalog (per-skill details in each SKILL.md)

| Skill | Purpose |
|-------|---------|
| `/service-planner` | Design Thinking–based planning (6 markdown files + HTML mockups). Modes: new / improve. Auto-decision: persona-based selection among 5 design tones. |
| `/blueprint` | Dedicated blueprint (design document) authoring. 10 standard sections (data model · API contract · sequences · pseudocode logic · **HITL Triggers**) — no implementation code. Planner deliverables auto-loaded. Only 1–3 core decisions surface as HITL. Section 10 serves as the HITL guard for `/feature-dev` during implementation. **v5.19+: blueprint-on-dev + one-flow** — the skill authors the blueprint on `dev` in the main worktree, commits + **pushes to origin/dev**, delegates to `/sprint-init --scaffold-only` to create the sprint worktree from `origin/dev`, then **continues in the same session inside the worktree** through implementation, the adversarial test loop (score ≥ 90 ∧ P0 == 0, max 5), and `/pr-merge`. `--design-only` stops after the dev push (no worktree). Secondary blueprints (invoked inside a sprint worktree) commit to the sprint branch, no pipeline re-launch. **Aborts with error** when invoked on a non-standard branch (not dev/main/master). |
| `/handoff-publish` | UX / UI / Dev / QA collaboration package — 14 Screen-ID–based files. UX holds the sole right to issue IDs. Outputs to `{feature-name}-handoff/`. |
| `/manual-generator` | Service URL + project docs → self-contained HTML manual. Chrome MCP screenshots + annotations. |
| `/catalog-generator` | Product data → self-contained HTML catalog. AI imagery (fect-image) + sales-strategy auto-applied. |
| `/autorun` | Mostly-unattended full pipeline: `/service-planner` → planner-reviewer → design-token-validator → blueprint (v5.19+: authored + pushed on `dev`, then the sprint worktree is created by `/blueprint` Step 6.5 from `origin/dev`) → blueprint-reviewer → `/sprint-init` (idempotent re-entry — usually skipped since `/blueprint` already created the worktree) → `/test-scenario` (TDD) → implementation → `/test-run` (single-pass; retries are driven by autorun's Stage 7.5 iteration loop up to `--max-iter`) → **Stage 7.6 adversarial verification gate** (loop-verifier SPRINT PRESET, same triple gate as the sprint pipeline: tests PASS ∧ score ≥ 90 ∧ P0 == 0 — FAIL at max iterations skips the merge) → `/pr-merge --auto` (v5.11+: Step 4.5 auto-picks integration branch matching inferred name or creates from dev; **Step 8.4.5 promotion target is HITL even under `--auto` (v5.11.2+) — user picks dev / staging / skip**) → cleanup (worktree removal). All Stage 5+ work runs inside `.worktrees/sprint-*`. Routine HITL: max-iteration at start + promotion target at Stage 8.2. Other halts only on real blockers (gh auth, merge conflicts, Critical review issues). `/sprint-init --auto` can enter the same downstream pipeline. |
| `/loop` (v5.12.0+) | Target-driven convergence loop (evaluator-optimizer pattern) for open-ended targets that don't fit the fixed `/autorun` pipeline. Stage 0.3 freezes an evaluation rubric (presets A–E + bounded target-specific adjustment, HITL-confirmed, immutable mid-loop); Stage 0.5 **always** asks the max iteration count via HITL (1–10, default 3 — `--max-iter=N` only pre-selects the option, never skips the question). Each iteration: work → objective gate (project test-runner exit code; a failing suite short-circuits the verifier) → adversarial `loop-verifier` scoring → branch on the `ASTRA_LOOP_RESULT` tail line. Exit gate is a triple conjunction: test pass ∧ score ≥ 90 ∧ P0 == 0 (never the LLM score alone — leniency-bias mitigation). Hard-stops at max iterations; stall detection (2 consecutive non-improving scores) pauses via HITL. No commit/PR/merge — hands off to `/pr-merge` or manual git flow. Artifacts: `docs/loops/{NNN}-{slug}/` (frozen `loop.md`, `verify-{i}.md`, `iter-{i}-summary.md`). |
| `screen-quality-loop` (v5.15.0+, auto-trigger) | Adversarial convergence loop for **newly authored screens** (app pages/routes/views/`*-screen.tsx`, standalone HTML pages, planner `SCR-NNN.html` mockups). Auto-triggers after the initial implementation of a new screen batch; each iteration delegates the set to `screen-verifier` (fixed rubric: design-system application 35 · cross-screen layout consistency 30 · polish 35), branches on the `ASTRA_SCREEN_RESULT` tail line, applies the fix directives in the parent context, and repeats until **score ≥ 90 AND p0 == 0** or **5 iterations** (hard cap, zero HITL — safe inside `/autorun`). Reports: `{OUTPUT_DIR}/screen-quality/` (mockups) or `docs/design-system/screen-quality/{slug}/` (app). Skips edits to existing screens, manual/catalog/handoff deliverables, and `/design-redesign` runs. Never blocks the calling workflow — an unachieved outcome is reported with remaining P0s/directives. |
| `/design-init` (v5.4.0+) | Create / update the design-system SSoT. Generates `docs/design-system/DESIGN.md` (YAML Front Matter + Markdown Body) and auto-regenerates `src/styles/design-tokens.css`. Modes: new / update / `--regenerate-css` / `--from-refs=...`. 4 core HITL questions (brand tone · primary color · typography · density). `--auto` proceeds with conservative defaults. |
| `/design-extract` (v5.4.0+) | Extracts OKLCH tokens, fonts, and spacing from image / PDF / URL / screenshot references. Uses Vision MCP (fect-mcp) or WebFetch. Generates an extraction report (`docs/design-system/extract-report-{date}.md`) and feeds into `/design-init`. |
| `/design-redesign` (v5.4.0+) | Audits and redesigns existing UI components / pages against DESIGN.md. Orchestrates `design-token-validator` (quantitative) + `designer-persona` (qualitative). P0 auto-applied; P1/P2 require user confirmation. `--apply` / `--pr` flags. |
| `/design-audit` (v5.4.0+) | Lightweight token-violation report against DESIGN.md (no modifications). For CI gates and PR pre-checks. A lightweight entry point to `/design-redesign`. |
| `/skill-author` | Author a new SKILL.md or refactor an existing skill (based on the 13-item best-practices checklist). Modes: new / improve. Auto-writes frontmatter + auto-blocks anti-patterns + 500-line gate + Progressive Disclosure separation recommendations. Triggered on `paths: skills/**/SKILL.md` as a complementary trigger. |
| `/uat-parallel` | Parallel sibling of `/user-test` driven by Playwright Test (`--workers N`). Reuses 100% of the `docs/tests/uat-cases/*.md` format and the `/user-test` HTML report template. Each worker holds an isolated `BrowserContext` (separate cookies / localStorage) so multi-user flows do not collide; per-step/per-case hard timeouts kill stuck cases without blocking other workers. Bootstraps `@playwright/test` + chromium on first run (one HITL confirmation). No interactive mode — auto-batch only. Output: `docs/tests/uat-reports/{SESSION_ID}/` (index.html + issues.md + session.json + screenshots + Playwright `traces/`). |
| `/user-test` | Interactive AI-assisted UAT: runs `docs/tests/uat-cases/*.md` case-by-case in a browser (Chrome MCP), records evidence, and emits an HTML report + issues list. Sequential sibling of `/uat-parallel`. |
| `/sprint-init` | Sprint scaffolding + worktree-always isolation (`.worktrees/sprint-<N>-<name>/`, v5.19+) + the shared execution pipeline (see Sprint Isolation section above). `--scaffold-stop` / `--scaffold-only` / `--auto` / `--resume`. |
| `/pr-merge` | Automated PR cycle — commit, push, PR, code review, fix loop, merge, integration-branch promotion (see Sprint Isolation section above). |
| `/test-scenario` | Authors TDD test scenarios from the blueprint (Given/When/Then per §3 endpoint). |
| `/test-run` | Single-pass integration test execution with port isolation and the `ASTRA_TEST_RESULT` machine gate line (retries are driven by the calling pipeline, not internally). Browser backends in detection order: `cmux` → `ego` (ego lite, macOS-only) → `chrome-mcp`. |
| `/project-init` | Target-project bootstrap: directory structure, CLAUDE.md, DESIGN.md seed, `.gitignore` wiring. |
| `/project-checklist` | Read-only Sprint 0 completeness verification of a target project (delegates mechanical checks to `scripts/verify-setup.sh` / `astra-validator`). |
| `/astra-setup` | Global (user-level) ASTRA environment setup — one-time per machine. |
| `/astra-guide` | User-facing quick reference for the methodology, skills, and commands. |
| `/sprint-progress` (auto-trigger) | Sprint progress tracker updates on sprint-file events (paired with the `track-sprint-progress.sh` hook). |
| `coding-convention` / `data-standard` / `code-standard` (auto-trigger) | Language conventions, Korean public data standard, ISO/ITU code standards — auto-applied on Write/Edit (see their sections above). |
| `/tool-author` | Authors MCP tool definitions (TypeScript+Zod / Python+Pydantic templates). |

### Design System SSoT (v5.4.0+) — DESIGN.md as Single Source of Truth

ASTRA consolidates the design-system SSoT into the `docs/design-system/DESIGN.md` hybrid format (YAML Front Matter + Markdown Body). It combines the Google Stitch DESIGN.md spec with ASTRA's 3-tier token structure (Primitive → Semantic → Component).

- **Front Matter (machine-readable)**: `meta`, `brand` (philosophy / personality / target_persona / voice_tone), `tokens.color/typography/spacing/radius/shadow/motion/breakpoints/z_index`, `accessibility` (WCAG · focus_ring · touch_target · motion_levels), `components` registry, `aesthetic_rules` (forbidden_generic_patterns · required_distinctive_elements).
- **Body (humans + AI)**: §1 Design Philosophy → §2 Brand Identity & Persona → §3 Visual Language → §4 Component Guidelines → §5 Anti-AI Aesthetic Rules → §6 Animation & Motion → §7 Accessibility → §8 Token-to-CSS Generation → §9 Evolution Log.
- **`src/styles/design-tokens.css`** is a **generated artifact** with an `AUTO-GENERATED from DESIGN.md` header. Never hand-edit — regenerate via `/design-init --regenerate-css` after DESIGN.md changes. Conversion: `tokens.color.primitive.primary.50` → `--primitive-primary-50`, `tokens.color.semantic.surface.base` → `--surface-base`, etc.
- **Legacy `components.md` / `layout-grid.md`** remain as fallback references for pre-v5.4.0 projects. New projects use only DESIGN.md.
- **Integration points**: `/project-init` Step 5-A bootstraps DESIGN.md → `/service-planner` Step E loads DESIGN.md as the primary token + persona source → `/handoff-publish` 6-component-specs.md references DESIGN.md §4 → `design-token-validator` enforces DESIGN.md Front Matter — at every layer, DESIGN.md is the single referenced document.

### Blueprint & Sprint Conventions

- **Blueprint directory**: `docs/blueprints/{NNN}-{feature-name}/blueprint.md` (3-digit zero-padded). Related files (diagrams, API specs) in same directory. Created on `dev` branch (falls back to `main`/`master`); work branches auto-created by `/pr-merge`.
- **Sprint directory**: `docs/sprints/sprint-{N}-{feature-name}/progress.md` — auto-tracked by `track-sprint-progress.sh` hook + `sprint-progress` skill. Updates Blueprint/DB Design/Test Cases/Implementation/Test Report columns based on file event type.
- **`overview.md`** stays at `docs/blueprints/overview.md` root level.

### Target Project Structure

When the plugin initializes a target project, it creates a structured layout under `docs/`, `catalog/`, and `src/styles/`. See [`docs/development/target-project-structure.md`](docs/development/target-project-structure.md) for the full tree and per-skill output locations.

## Development Notes

- All skill files use YAML frontmatter for metadata (`name`, `description`, `allowed-tools`, etc.)
- Agent files specify `tools`, `disallowedTools`, `model`, and `maxTurns` in frontmatter
- The plugin uses `$ARGUMENTS` and `$CLAUDE_PLUGIN_ROOT` as runtime variables
- Scripts receive tool input via stdin as JSON (parsed with `jq`)
- All plugin-internal documentation, skill instructions, and user-facing strings inside this repository are written in English. The runtime output language for end users is controlled by the `/select-language` command (Korean / Vietnamese / English) — translating this repository's documentation does not change the deliverable language for existing projects.
- The `data/` JSON files are large (13K+ terms) — use targeted `jq` queries rather than loading entirely
- **MCP servers (v5.18+)**: the plugin bundles only `fect-image` / `fect-gpt-image` in `plugin.json`. The `chrome-devtools` MCP server is **not bundled** — skills that drive a browser (`manual-generator`, `catalog-generator`, `user-test`, `uat-parallel`, `test-run`, …) require the user to register `chrome-devtools-mcp` themselves (this also avoids profile `SingletonLock` conflicts in multi-session setups — attach one shared instance via `--browser-url` instead of launching per session). The former `fect-slack` integration (`/slack-import`, `/extract-backlog`, Slack List status sync) was removed in v5.18.
- **ego (lite) browser (optional, `/test-run` only)**: a third-party Chromium browser ([citrolabs/ego-lite](https://github.com/citrolabs/ego-lite), macOS-only) whose `ego-browser` skill drives it through Bash heredocs instead of MCP tool calls — isolated Task Spaces per agent (no `SingletonLock` contention) and inherited login state. `/test-run` auto-detects it as the **second** backend (`cmux` → `ego` → `chrome-mcp`); nothing else in the plugin depends on it, and it is never bundled. Procedures + caveats (login-state inheritance, blank-screenshot-on-scroll, no perf trace) live in `skills/test-run/references/browser-ego.md`.

## Behavioral Guardrails (LLM Coding 4 Principles)

Four behavioral principles apply to all coding work in target projects, derived from observations on common LLM coding pitfalls (Andrej Karpathy / forrestchang). They bias toward **caution over speed** — for trivial tasks, use judgment.

These principles are inlined into the relevant skills rather than being a standalone skill:

| Principle | Inlined location | Trigger |
|-----------|------------------|---------|
| **Think Before Coding** | `skills/service-planner/SKILL.md` (Step 0.A.1 ambiguity check) | At the start of planning, when feature descriptions are ambiguous → present interpretation options |
| **Simplicity First** | `skills/coding-convention/SKILL.md` (Behavioral Guardrails) | Auto-applied on every code write/edit |
| **Surgical Changes** | `skills/coding-convention/SKILL.md` + `skills/pr-merge/SKILL.md` (Step 8.2) | Code edits + PR review issue remediation |
| **Goal-Driven Execution** | `skills/pr-merge/SKILL.md` (Step 8.2 auto-debug loop) | Iteration driven by verifiable success criteria |

**Quick reference**: `/astra-guide principles`

**ASTRA auto-builder exception**: *broad deliverable-generating skills* such as `/service-planner`, `/blueprint`, `/manual-generator`, `/catalog-generator`, `/handoff-publish`, `/project-init`, `/sprint-init`, `/autorun` produce the full-stack deliverables explicitly requested by the user, so the "Simplicity First" scope-restriction does not apply to them. The *individual code* they author internally still follows the 4 principles.

> **⚠️ Automated merge warning (v5.x+)**: `/autorun` and `/sprint-init --auto` automatically invoke `/pr-merge --auto` upon passing both the test run and the adversarial verification gate. The sprint PR merges into its integration branch automatically; the integration branch's onward promotion (to `dev`, `staging`, or skip) is **always asked from the user via HITL (v5.11.2+)** — `--auto` does not silently promote to `dev` anymore. Unattended mode is protected by the safety gates below, but is *only as safe as those gates*:
> - Test pass (`/test-run` is single-pass — the autorun / sprint-pipeline iteration loop drives retries up to MAX-iteration)
> - Adversarial verification pass (loop-verifier SPRINT PRESET: score ≥ 90 ∧ P0 == 0 — sprint pipeline Step 5.4.5 / autorun Stage 7.6)
> - Code-review pass (Critical-issue count = 0 from the feature-dev:code-reviewer agent — any remaining Critical blocks the merge)
> - No merge conflicts (cascade / rebase conflicts auto-halt)
> - **Promotion target HITL** — the user explicitly picks `dev` / `staging` / `skip` at Step 8.4.5 (the deployment surface choice has no safe unattended default)
>
> `--auto` is **not** recommended for sensitive business logic, compliance-impacting features, or legacy integrations — instead of `/autorun` (which has no "no-merge" mode beyond picking `skip` at the promotion HITL), use `/sprint-init` (scaffold only) + run the prompt-map manually, then invoke `/pr-merge` explicitly after user review.

**Source**: [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) (MIT) — adapted into existing skills with English translation and ASTRA-specific scope clauses.

## Skill Authoring

When authoring a new SKILL.md or modifying an existing skill, use [`docs/development/skill-best-practices.md`](docs/development/skill-best-practices.md) as the SSoT — core principles, frontmatter fields, the 7 description rules, progressive disclosure, anti-patterns, and the ASTRA checklist.

**Authoring / modification entry points**:
- **`/skill-author`** (skill) — author a new SKILL.md or refactor an existing skill. Interactive mentoring: auto-writes frontmatter → auto-blocks anti-patterns → 500-line separation gate → writes evaluation scenarios → final validation via `/skill-lint`.
- **`/skill-lint <path>`** (command) — one-shot validation. Executes the 13-item checklist in auto/semi-auto/manual modes and reports as a PASS/FAIL/WARN/MANUAL table. With no argument, auto-detects SKILL.md changes from `git status`.

The LLM is configured so that editing a path under `skills/**/SKILL.md` triggers the `/skill-author` skill's `paths` trigger automatically — explicit user invocation and the path trigger operate complementarily.

## Scripts

```bash
# Repo-level lint (run before pushing): frontmatter, 500-line gate, English descriptions,
# persona guards, version sync, CLAUDE.md catalog drift, verifier/contract-line sync, zsh smells.
# Tail line: ASTRA_LINT_RESULT: PASS|FAIL fail=N warn=N (non-zero exit on FAIL)
./scripts/lint-skills.sh

# Verify Sprint 0 setup — the SSoT for the mechanical checklist (run by /project-checklist and astra-validator)
./scripts/verify-setup.sh [project-root-path]

# Initialize project directory structure only (quick-start subset of /project-init)
./scripts/init-project.sh [project-root-path]

# Hook scripts (not invoked directly — called by hooks.json)
./scripts/sessionstart-notice.sh     # SessionStart: banner + 24h-throttled env-var warnings
./scripts/check-forbidden-words.sh   # stdin: JSON tool input
./scripts/validate-naming.sh         # stdin: JSON tool input
./scripts/track-sprint-progress.sh   # stdin: JSON tool input
```

## Conventions

- **Version bump required**: before pushing to the main branch, the `version` field in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` must be updated. Follows SemVer — bug fixes are patch (x.x.+1), feature additions are minor (x.+1.0), and breaking changes are major (+1.0.0).
- **Skill description language policy**: all skill `description` fields are written in **English** (auto-trigger accuracy is highest with English descriptions, and the project's authoring language is English). Both auto-trigger skills (e.g., `coding-convention`, `data-standard`, `code-standard`, `sprint-progress`) and interactive user-workflow skills (e.g., `service-planner`, `blueprint`, `handoff-publish`, `manual-generator`, `pr-merge`, `autorun`) use English. Runtime output language for end users is controlled separately by `/select-language`.
  - **frontmatter form**: auto-trigger skills use the `description: >` block form; explicitly-invoked skills use the single-line `description: "..."` form.
- **Agent description guard**: persona agents (`tester-persona`, `designer-persona`, `developer-persona`) MUST keep the `[EXPLICIT-INVOCATION-ONLY — DO NOT AUTO-MATCH]` guard prefix on the first line of their description.
- Skill SKILL.md files follow a strict procedural format (Step-by-step instructions)
- Commands are simpler than skills — they define input/output format and delegate to data files
- All agents are read-only (`disallowedTools: Write, Edit`) — they analyze and report but never modify files
- Agent model selection: `haiku` for rule-based validation (fast), `sonnet` for complex analysis (accurate)
- Agent naming convention: `*-validator` (haiku, rule validation), `*-reviewer` (sonnet, deliverable quality review), `*-runner` (sonnet, integrated execution), `*-analyzer` (sonnet, pattern/metrics), `*-persona` (sonnet, senior-perspective delegation — explicit-invocation only), `*-verifier` (sonnet, adversarial loop-gate scoring against a frozen rubric — invoked only by its owning skill, e.g. `loop-verifier` ← `/loop`, `screen-verifier` ← `screen-quality-loop` / `/service-planner` Step 6.F.6)
- Hook scripts must always `exit 0` to avoid blocking the user's workflow
- `standard_terms.json` fields: `공통표준용어명` (Korean term), `공통표준용어영문약어명` (English abbreviation), `공통표준도메인명` (domain)
- `standard_words.json` fields: `공통표준단어명` (word), `공통표준단어영문약어명` (abbreviation), `금칙어목록` (forbidden words), `이음동의어목록` (synonyms)
- **Dataset caveat (v5.17+)**: in the bundled datasets the Korean name fields (`공통표준용어명`, `공통표준단어명`) are **empty in every row** — match Korean input against `이음동의어목록`/descriptions instead. Rows live under `.data[]`, and Korean field names require jq bracket form (`.["금칙어목록"]` — bare `.금칙어목록` is a jq syntax error).
