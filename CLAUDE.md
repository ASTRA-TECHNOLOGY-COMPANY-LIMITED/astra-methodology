# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**astra-methodology** is a Claude Code plugin that implements the ASTRA (AI-augmented Sprint Through Rapid Assembly) methodology. It provides Sprint 0 project initialization, coding convention enforcement (Java/TypeScript/React Native/Python/CSS/SCSS), Korean public data standard enforcement, international code standards (ISO 3166-1/2, ITU-T E.164), naming validation, and quality gates for Korean enterprise software development.

This is NOT an application codebase — it is a Claude Code plugin consisting of skills, agents, hooks, commands, and scripts that get installed into target projects.

## Repository Structure

```
astra-methodology/
├── skills/              # Claude Code skills (invoked via /command or auto-applied)
│   ├── astra-setup/     # Global dev environment setup (/astra-setup)
│   ├── astra-guide/     # Quick reference guide (/astra-guide)
│   ├── project-init/    # Sprint 0 project scaffolding (/project-init)
│   ├── sprint-init/       # Sprint planning & initialization (/sprint-init)
│   ├── project-checklist/ # Sprint 0 completion verification (/project-checklist)
│   ├── data-standard/     # Korean public data standard terminology (/data-standard)
│   ├── test-run/          # Integration testing — cmux browser (primary) / Chrome MCP (fallback) (/test-run)
│   ├── test-scenario/     # E2E test scenario generation (/test-scenario)
│   ├── pr-merge/          # Commit→review→fix→merge full cycle (/pr-merge)
│   ├── slack-import/   # Slack List → blueprint + sprint generation (/slack-import)
│   ├── coding-convention/ # Auto-applied coding convention (Java/TS/Python/CSS/SCSS)
│   ├── code-standard/     # Auto-applied international code standards (ISO/ITU)
│   ├── sprint-progress/   # Auto-applied sprint progress tracking
│   ├── service-planner/   # Design thinking based planning deliverables (/service-planner)
│   ├── ux-publish/        # UX component publishing from planning docs (/ux-publish)
│   ├── handoff-publish/   # UX/UI/Dev/QA handoff package generator — Screen ID based (/handoff-publish)
│   ├── manual-generator/  # Service manual auto-generator with Chrome MCP screenshots (/manual-generator)
│   ├── catalog-generator/ # Product promotional catalog auto-generator (/catalog-generator)
│   └── autorun/           # Zero-interaction full pipeline: planning → testing (/autorun)
├── agents/              # Specialized Claude Code subagents (read-only, auto-discovered)
│   ├── astra-validator.md           # ASTRA methodology compliance checker (haiku)
│   ├── naming-validator.md          # DB naming standard validation (haiku)
│   ├── convention-validator.md      # Coding convention validation (haiku)
│   ├── blueprint-reviewer.md        # Design document quality & consistency (sonnet) — Gate 2
│   ├── design-token-validator.md    # Design token system compliance (haiku) — Gate 2.5
│   ├── sprint-analyzer.md           # Sprint progress & retrospective analysis (sonnet)
│   ├── quality-gate-runner.md       # Integrated quality gate execution (sonnet) — Gate 3
│   ├── test-coverage-analyzer.md    # Test strategy & coverage analysis (haiku) — Gate 2
│   ├── planner-reviewer.md          # Planning deliverables quality & traceability (sonnet) — Gate 1.5
│   ├── tester-persona.md            # QA engineer role-based delegation (sonnet) — explicit only
│   ├── designer-persona.md          # UX/UI designer role-based delegation (sonnet) — explicit only
│   └── developer-persona.md         # Senior developer role-based delegation (sonnet) — explicit only
├── commands/            # Slash commands
│   ├── generate-entity.md       # /generate-entity — entity code from Korean definitions
│   ├── check-naming.md          # /check-naming — DB naming standard compliance check
│   ├── check-convention.md      # /check-convention — coding convention compliance check
│   ├── lookup-term.md           # /lookup-term — standard term dictionary lookup
│   ├── lookup-code.md           # /lookup-code — international code lookup (ISO/ITU)
│   ├── select-language.md       # /select-language — workflow language selection (ko/vi/en), reusable across skills
│   └── extract-backlog.md         # /extract-backlog — extract backlog items from Slack
├── hooks/               # PostToolUse hooks (hooks.json)
├── scripts/             # Shell scripts for hooks and verification
├── data/                # Standard dictionary and international code JSON files
│   ├── standard_terms.json        # 13,176 standard terms (Korean→English abbreviation)
│   ├── standard_words.json        # 3,284 standard words (abbreviations, forbidden words)
│   ├── standard_domains.json      # 123 standard domains (type codes, lengths)
│   ├── iso_3166_1_countries.json  # 249 ISO 3166-1 country codes
│   ├── iso_3166_2_regions.json    # 653 ISO 3166-2 region codes (21 countries)
│   └── country_calling_codes.json # 245 ITU-T E.164 calling codes
├── docs/                # Reference design & UX documents
│   ├── ux/
│   │   ├── vibe-coding-design-guide.md    # Vibe Coding design guide (anti-AI aesthetics, prompting techniques, tool comparison)
│   │   ├── vibe-coding-animation-guide.md # Vibe Coding animation guide (CSS/Framer Motion/GSAP, micro-interactions, scroll, performance, accessibility)
│   │   ├── ux-interaction-patterns.md     # UX/UI interaction patterns guide (11 categories)
│   │   └── mobile-design-guide.md         # Mobile app design guide (HIG, Material 3, touch, animation, haptics, accessibility, expert tips)
│   ├── catalog/
│   │   ├── catalog-expert-workflow.md     # Catalog design expert workflow & know-how
│   │   ├── catalog-expert-workflow.ko.md  # Korean translation
│   │   └── catalog-expert-workflow.vi.md  # Vietnamese translation
│   ├── manual/                            # Service methodology manuals
│   │   ├── MANUAL.md                      # English manual
│   │   ├── MANUAL.ko.md                   # Korean manual
│   │   └── MANUAL.vi.md                   # Vietnamese manual
│   └── plugin/                            # Plugin development guides
│       └── claude-code-plugins-guide.md   # Claude Code plugins guide
└── .claude-plugin/      # Plugin manifest (plugin.json, marketplace.json)
```

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

Reference files are in `skills/coding-convention/` (e.g., `java-coding-convention.md`, `typescript-coding-convention.md`, `react-native-coding-convention.md`).

For mobile projects, the coding convention skill additionally references `docs/ux/mobile-design-guide.md` for UI/UX implementation decisions (platform guidelines, touch interaction, animation timing, haptic feedback, dark mode, accessibility).

### Vibe Coding Design & Animation Guides

The plugin provides comprehensive design and animation guides under `docs/ux/` that should be referenced during all UI design and implementation work:

- **`vibe-coding-design-guide.md`**: Expert-level Vibe Coding design practices — anti-AI aesthetics prompting, reference-anchored design, constraint-first approach, layered onion method, design token injection, tool comparison (v0/Bolt.new/Lovable/Cursor/Claude Code), DO/DON'T patterns, Korean market adoption insights
- **`vibe-coding-animation-guide.md`**: Production-grade animation techniques — CSS native (View Transitions API, Scroll-Driven Animations, `@starting-style`, `linear()` springs), Framer Motion/GSAP/Lottie/Rive patterns, micro-interactions, scroll-based animations, page transitions, performance optimization (GPU acceleration, `will-change`), 3-tier motion accessibility, Disney 12 principles for UI, mobile gestures/haptics, animation design tokens

These guides are automatically loaded by `/ux-publish` and should be referenced by any skill or workflow that involves UI component creation, design system work, or animation implementation.

### International Code Standards (ISO 3166-1/2, ITU-T E.164)

The plugin auto-applies international code standards when implementing phone number inputs, country/region selectors, and address forms:

- **ISO 3166-1**: alpha-2 country codes (e.g., `KR`, `US`, `JP`) — stored as `NATN_CD CHAR(2)`
- **ISO 3166-2**: region/subdivision codes (e.g., `KR-11`, `US-CA`) — stored as `RGN_CD VARCHAR(6)`
- **E.164**: international phone numbers (e.g., `+821012345678`) — stored as `INTL_TELNO VARCHAR(15)`

Data files: `iso_3166_1_countries.json` (249 countries), `iso_3166_2_regions.json` (653 regions), `country_calling_codes.json` (245 calling codes).

### Hooks Architecture

`hooks/hooks.json` defines hooks that run automatically:

**Stop hooks** (run when Claude finishes responding):
1. **enforce-work-summary.sh** — ensures Claude provides a work summary in the user's language after completing tasks. Uses `decision: "block"` with `reason` to make Claude continue if summary is missing. Checks `stop_hook_active` to prevent infinite loops. Skips short responses (<80 words) and question-only responses.

**PostToolUse hooks** (run after Write/Edit operations):
1. **check-forbidden-words.sh** — scans DB-related files for forbidden words from the standard dictionary
2. **validate-naming.sh** — checks table name prefixes in SQL, Java (@Table), TypeScript (@Entity), Python (__tablename__)
3. **track-sprint-progress.sh** — detects sprint-related file events (blueprints, DB design, test cases, implementation, test reports) and appends activity log entries to the sprint progress tracker
4. All PostToolUse hooks are non-blocking (exit 0) — they emit warnings only

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

#### Persona Agents (explicit invocation only, read-only orchestrators)
Role-based mindset agents that bring senior-practitioner perspective to analysis. **Never auto-trigger** — must be explicitly invoked by user (e.g., "테스터 관점에서", "디자이너로서") or by orchestrating skills.

| Persona | Model | When to Invoke | Returns |
|---------|-------|----------------|---------|
| `tester-persona` | sonnet | Edge case discovery, scenario gap analysis, risk-based prioritization, production readiness | Prioritized findings + Given-When-Then test suggestions; hands back to `/test-scenario` or `/test-run` |
| `designer-persona` | sonnet | Design system audit, Vibe Coding aesthetic critique, WCAG 2.1 AA review, motion analysis, Screen ID handoff audit | Prioritized findings + token/component suggestions; hands back to `/ux-publish` or `/handoff-publish` |
| `developer-persona` | sonnet | Architecture review, ASTRA 4-principle audit, code smell, OWASP security audit, tech debt prioritization | Prioritized findings + ASTRA principle compliance; hands back to `/pr-merge` or `/generate-entity` |

**Architectural principle**: Persona agents are **orchestrators, not executors**. They analyze and recommend, but all file edits happen back in the parent context — this preserves auto-applied skills (`coding-convention`, `data-standard`, `code-standard`) which only trigger on parent-context Write/Edit operations.

**When to use which**:
- Stateful multi-turn workflow with user interaction → **Skill** (e.g., `/service-planner`'s 10-step pipeline)
- Stateless validation against rules → **Validator agent** (e.g., naming check)
- Senior-practitioner mindset on a specific artifact → **Persona agent** (e.g., "tester reviews edge cases")
- Parallel role-based work → Multiple personas via `Task()` calls in parallel

### Service Planner (Design Thinking Based)

The `/service-planner` skill automates the planning phase using Design Thinking methodology:

- **Methodology**: Design Thinking (Empathize → Define → Ideate → Prototype)
- **Modes**: New service planning (from scratch) / Existing service improvement (data-driven, leverages existing analytics, CS logs, and user feedback)
- **Pipeline**: Mode Selection → Market Analysis(PEST/SWOT) → Actor Derivation → Persona Interview → Pain Point Analysis → Idea Generation(HMW/SCAMPER/JTBD) → Requirements(KPI/OKR) → Use Cases(Journey Map) → IA/Screen Design(Wireframe) → Feature Definition(Story Map/Risk/Policy)
- **Interactive**: Mode select, actor multi-select, idea multi-select with user confirmation at each major step
- **Deliverables** (6 files under `docs/planner/{NNN}-{feature-name}/`):
  1. `market-analysis.md` — Market/competitor analysis with PEST, benchmarking, SWOT
  2. `interview-report.md` — Persona interview results with pain point analysis
  3. `requirements-definition.md` — Requirements with KPI/OKR, JTBD, traceability
  4. `usecase-definition.md` — Use case definitions with Mermaid diagrams and customer journey maps
  5. `ia-screen-design.md` — Information Architecture, screen flow, text-based wireframes
  6. `feature-definition.md` — Feature definition with User Story Map, MoSCoW, risk analysis, service policies
- **Persona generation**: 3 personas per selected actor type with realistic interview simulation
- **Idea generation**: HMW + SCAMPER + JTBD Job Statements, 10-15 ideas with implementation difficulty and expected impact
- **Business alignment**: OKR/KPI metrics linked to features for strategy-to-execution traceability
- **Risk management**: Risk register with likelihood/impact scoring and mitigation strategies

### Blueprint Directory Convention

Individual feature blueprints are organized as numbered directories under `docs/blueprints/`:
- **Directory format**: `{NNN}-{feature-name}/` (e.g., `001-auth/`, `002-payment/`, `003-payment-dashboard/`)
- **Main file**: `blueprint.md` inside each directory
- **Related files**: Supplementary materials (diagrams, API specs, etc.) are placed in the same directory
- **Numbering**: 3-digit zero-padded sequential numbers. Next number is determined by scanning existing directories.
- **Work branch**: Blueprint creation works directly on the `dev` branch (falls back to `main`/`master`). Work branches (`feat/`, `fix/`, etc.) are not created during blueprint creation — they are automatically created by `/pr-merge` when committing and opening a PR.
- `overview.md` remains at the root level as the project overview document

### Sprint Progress Tracking

The plugin provides automatic sprint progress tracking through a hook + skill hybrid system:

- **Hook** (`track-sprint-progress.sh`): Detects file write events matching sprint-related paths (blueprints, DB design, test cases, implementation files, test reports), appends activity log entries to the tracker file, and emits a message prompting the LLM to update the progress table
- **Auto-applied skill** (`sprint-progress/SKILL.md`): Guides the LLM to intelligently update the progress table columns (Blueprint, DB Design, Test Cases, Implementation, Test Report) based on the event type
- **Sprint directory format**: `sprint-{N}-{feature-name}/` (e.g., `sprint-1-auth/`, `sprint-2-workspace/`) — includes the primary blueprint name for traceability
- **Tracker file**: `docs/sprints/sprint-{N}-{feature-name}/progress.md` — contains a feature progress table, summary statistics, and an activity log
- Tracker is auto-created during `/sprint-init` initialization, or created on-demand by the skill when an event is detected but no tracker exists

### UX Component Publishing

The `/ux-publish` skill generates production-grade UI components from planning documents:

- **Input**: `docs/planner/{NNN}-{feature-name}/` (requires `ia-screen-design.md` + `feature-definition.md` from `/service-planner`)
- **Output**: `publish/{feature-name}/` — framework-specific components (React/Vue/Angular/Svelte) with copy guide for `src/` integration
- **Component-based output**: Generates actual reusable components (common UI, layout, screen, hooks) instead of standalone HTML
- **Staging directory**: `publish/` serves as a staging area — components are reviewed, then copied to their actual `src/` locations via `COPY-GUIDE.md`
- **Framework detection**: Auto-detects project framework (React/Next.js/Vue/Nuxt/Angular/Svelte/React Native) and styling method (CSS Modules/Tailwind/CSS-in-JS/SCSS)
- **Vibe Coding design guide**: References `docs/ux/vibe-coding-design-guide.md` for anti-AI aesthetics, reference-anchored prompting, constraint-first design, design token injection
- **Vibe Coding animation guide**: References `docs/ux/vibe-coding-animation-guide.md` for spring physics, micro-interactions, scroll animations, page transitions, 3-tier motion accessibility
- **Design quality**: Uses `/frontend-design` skill for production-grade, distinctive UI (avoids generic AI aesthetics)
- **AI images**: Uses `fect-image` MCP (`mcp__fect-image__image_text2img`) for hero banners, empty state illustrations, avatars, backgrounds
- **Interaction patterns**: References `docs/ux/ux-interaction-patterns.md` (11 categories: micro-interactions, navigation, feedback, scroll, form, transitions, onboarding, accessibility, delight, dark patterns to avoid)
- **Mobile design**: For mobile projects, additionally references `docs/ux/mobile-design-guide.md` (14 sections)
- **Design tokens**: Strictly references project's `src/styles/design-tokens.css` (no hardcoded values)
- **Components**: Follows `docs/design-system/components.md` specifications
- **Layout**: Implements `docs/design-system/layout-grid.md` grid system
- **Browser preview**: `publish/{feature-name}/preview/` contains build-free HTML previews for design review
- **Features**: Responsive (mobile/tablet/desktop), dark mode, accessibility (WCAG AA), `prefers-reduced-motion` support
- **Design direction**: User selects aesthetic tone (Refined Minimal, Bold & Vibrant, Soft & Warm, Editorial, Professional Enterprise, or Auto)

### Handoff Package (UX/UI/Dev/QA 협업 패키지)

The `/handoff-publish` skill generates a Screen ID based collaboration package for long-lived product features, following the FECT `HANDOFF_PROCESS_GUIDE v1.1` (see `docs/workflow/HANDOFF_PROCESS_GUIDE.pdf`):

- **Output location**: Branch root `{feature-name}-handoff/` (intentional — designers/QA clone without navigating into engineering code)
- **Screen ID format**: `{DOMAIN}-{PAGE}-{SECTION}-UC{NN}` (e.g., `ACAD-EXPERT-DETAIL-UC03`). Domain code is project-wide (2–6 uppercase chars). State suffixes: `-LOADING`, `-EMPTY`, `-ERROR`.
- **Single Source of Truth**: `1-screen-registry.md` is the authoritative ID list. **UX holds exclusive issuance rights** — UI/Dev/QA cannot create new IDs (they must request via UX).
- **14 output files**:
  - `0-README.md` (guide + Quick Start), `1-screen-registry.md` (SSoT)
  - `2-flows.md`, `3-state-matrix.md`, `4-edge-cases.md`, `5-responsive-guide.md`
  - `6-component-specs.md`, `7-business-rules.md`, `8-content-guide.md`
  - `9-ia-sitemap.md`, `10-personas.md`, `11-decision-log.md`
  - `DoD-CHECKLIST.md` (role-based Definition of Done)
  - `walkthrough.loom.md` (manual recording link)
  - `screenshots/` (ID-named capture folder, populated by UI)
- **Design principle**: Every screen = State (LOADING/EMPTY/DEFAULT/ERROR/PARTIAL) × Permission × Device combination
- **Integration with existing assets**:
  - Reads `docs/planner/{NNN}-{feature}/ia-screen-design.md` if present → auto-converts `SCR-NNN` to 4-segment Screen IDs, records conversion in `11-decision-log.md`
  - Reads `interview-report.md` → populates `10-personas.md`
  - Reads `feature-definition.md` → seeds `3-state-matrix.md` permission matrix + `7-business-rules.md`
  - Reads `blueprint.md` → seeds API/data policy in `7-business-rules.md`
- **Out of scope (PDF §24)**: One-off marketing pages, prototypes/A-B tests, external embeds (Notion/Slack), admin back-offices not requiring UX collaboration. Skill prompts user at Step 0 and exits early.
- **Legacy code policy (PDF §26)**: Not auto-applied to existing features. Only new features or major renewals adopt Handoff. No retroactive enforcement hooks.
- **DoD automation (Developer stage)**: Lint + tsc + Lighthouse + axe-core CLI checks are scripted; Loom walkthrough, Figma↔code parity, screen reader test remain manual.

### Manual Generator

The `/manual-generator` skill automatically creates professional online service manuals as self-contained HTML packages:

- **Input sources**: Running service URL (Chrome MCP screenshots) + project docs (`docs/blueprints/`, `docs/planner/`)
- **Output**: `docs/manual/{feature-name}/` — self-contained HTML manual viewable in browser (no build required)
- **Chrome MCP integration**: Navigates real service, injects CSS highlights on target UI elements, adds step number overlays, captures annotated screenshots (desktop/tablet/mobile)
- **Writing quality**: Expert-level manual writing — 2nd person polite form, plain language, step-by-step format, visual-first approach (references `references/manual-writing-guide.md`)
- **Design quality**: Uses `/frontend-design` skill for polished reading-optimized layout (references `references/manual-css-template.md`)
- **Features**: Dark mode, client-side full-text search (Cmd+K), keyboard navigation, print stylesheet, responsive layout
- **Structure**: Cover + searchable TOC → Getting Started → Feature-by-feature guides (step-cards with screenshots) → FAQ/Troubleshooting → Glossary
- **User interaction gates**: Manual scope selection → TOC approval → design tone selection (Professional Enterprise, Refined Minimal, Soft & Warm, Auto)
- **Document-only mode**: If no URL provided, generates manual from blueprints/planner docs without screenshots (or uses `publish/` component previews)

### Catalog Generator

The `/catalog-generator` skill automatically produces professional product promotional catalogs as self-contained HTML packages:

- **Input**: Product data file (CSV/JSON/text), URL, or product description
- **Output**: `catalog/{catalog-name}/` — self-contained HTML catalog viewable in browser (no build required)
- **Expert workflow**: Based on `docs/catalog/catalog-expert-workflow.md` — professional catalog designers' workflows and know-how
- **Design quality**: Uses `/frontend-design` skill for polished, production-grade design (avoids generic AI aesthetics)
- **AI images**: Uses `fect-image` MCP for hero banners, lifestyle images, editorial illustrations, and category visuals
- **Chrome MCP integration**: Captures real product/service screenshots for "See it in action" showcases
- **Built-in sales strategies**: Cross-selling, upselling, price anchoring, and CTA placement applied automatically
- **Professional copywriting**: Benefit-driven, sensory language, storytelling, social proof techniques
- **Features**: Responsive (mobile/tablet/desktop), dark mode, print stylesheet, accessibility (WCAG AA)
- **Fully autonomous**: All decisions (design tone, layout, copy, product placement) are made by AI based on product characteristics — zero user interaction required

### Autorun (Zero-Interaction Full Pipeline)

The `/autorun` skill orchestrates the entire ASTRA workflow from planning through testing without any user input, stopping just before `/pr-merge`:

- **Input**: Feature description (Korean or English)
- **Pipeline**: `/service-planner` → planner-reviewer (Gate 1.5) → `/ux-publish` → design-token-validator (Gate 2.5) → blueprint generation → blueprint-reviewer (Gate 2) → `/sprint-init` → implementation (`/generate-entity` + blueprint-driven) → `/test-scenario` → `/test-run` (with 5-retry auto-debug) → final report
- **Auto-defaults**: All interactive decision points (mode selection, actor selection, idea selection, design tone, sprint number) are filled with smart defaults — no `AskUserQuestion` calls.
- **Fail-safe**: Hard-stops on output file missing, blocked dependencies, or test failures after 5 auto-debug retries. Continues with warnings on validator P0 issues (recorded in final report).
- **Idempotent resume**: Re-running with the same feature slug detects completed stages by output file existence and resumes from the failed/missing stage.
- **`/pr-merge` is never invoked** — the skill ends with an explicit instruction for the user to review outputs and run `/pr-merge` manually.
- **Final report**: Generates `docs/sprints/sprint-{N}-{feature-slug}/pipeline-report.md` summarizing all stage outcomes, P0 issues, and recommended persona reviews.
- **Use cases**: Rapid prototyping, full-stack module bootstrap, demo environment setup, post-Sprint-0 first feature seeding
- **Anti-use cases**: Bug fixes, sensitive business logic, legacy integration, compliance-impacting changes (require manual review gates)

### Slack Integration

The plugin integrates with Slack via the `fect-slack` MCP server to collect requirements directly from team communication channels:

- **`/slack-import`** (skill): Full interactive workflow — list channels → select channel → select List → select Items → update status → analyze requirements → generate blueprints + sprint prompt map + progress tracker
- **`/extract-backlog`** (command): Quick extraction — fetch messages from a channel and output a structured backlog table with priorities
- **MCP tools used**: `slack_list_channels`, `slack_get_history`, `slack_search_channels`, `slack_get_user_info`, `slack_post_message`, `slack_add_reaction`, `slack_file_list`, `slack_list_items_list`, `slack_list_items_info`, `slack_list_items_update`
- **Environment**: Requires `SLACK_BOT_TOKEN` environment variable
- **MCP config**: Defined in `.mcp.json` (auto-configured by plugin manifest `mcpServers` field)

### Target Project Structure (generated by /astra-methodology)

When the plugin initializes a target project, it creates:
```
{project}/
├── CLAUDE.md                          # Project-specific AI rules
├── docs/
│   ├── design-system/                 # Component guides, layout grid (documentation only)
│   ├── blueprints/                    # Feature design documents
│   │   ├── overview.md                # Project overview
│   │   ├── {NNN}-{feature-name}/      # Numbered feature directories (e.g., 001-auth/)
│   │   │   └── blueprint.md           # Main design document + related files
│   ├── planner/                       # Planning deliverables (Design Thinking)
│   │   └── {NNN}-{feature-name}/      # Numbered feature directories (e.g., 001-auth/)
│   │       ├── market-analysis.md     # Market/competitor analysis (PEST, SWOT, benchmarking)
│   │       ├── interview-report.md    # Persona interview results
│   │       ├── requirements-definition.md # Requirements (KPI/OKR, JTBD, traceability)
│   │       ├── usecase-definition.md  # Use cases with customer journey maps
│   │       ├── ia-screen-design.md    # IA structure, screen flow, wireframes
│   │       └── feature-definition.md  # Features with story map, risk, policies
│   ├── database/                      # DB design (SSoT), naming rules, migrations
│   ├── tests/                         # Test strategy, test cases (per sprint), test reports
│   ├── sprints/                       # Sprint documents (prompt maps, progress trackers, retrospectives)
│   ├── delivery/                     # Release artifacts
│   └── manual/                       # Service manuals (generated by /manual-generator)
│       └── {feature-name}/           # Per-feature manual
│           ├── index.html            # Cover + TOC + search
│           ├── chapters/             # Chapter HTML files (01-getting-started.html, etc.)
│           ├── assets/               # CSS (tokens, base, components, print)
│           ├── screenshots/          # Captured screenshots (desktop/, tablet/, mobile/)
│           └── shared/               # Common JS (nav, search, theme)
├── publish/                            # UI component staging (generated by /ux-publish)
│   └── {feature-name}/                # Per-feature component package
│       ├── COPY-GUIDE.md              # Copy mapping guide (publish/ → src/)
│       ├── components/                # Reusable UI components
│       │   ├── common/                # Common UI (Button, Input, Card, Modal, etc.)
│       │   ├── layout/                # Layout (GNB, Sidebar, PageLayout)
│       │   └── {feature}/             # Feature-specific components
│       ├── screens/                   # Screen/page components
│       ├── hooks/                     # Custom hooks (useScrollAnimation, useTheme, etc.)
│       ├── styles/                    # CSS (tokens, base, animations, modules)
│       ├── utils/                     # Utilities (cn, constants)
│       ├── assets/images/             # AI-generated image assets (fect-image)
│       └── preview/                   # HTML previews for design review (no build required)
│           ├── index.html             # Screen index & navigation hub
│           └── screens/               # Individual screen HTML previews
├── catalog/                           # Product catalogs (generated by /catalog-generator)
│   └── {catalog-name}/               # Per-catalog package
│       ├── index.html                 # Catalog main page
│       ├── assets/                    # CSS, JS, fonts
│       └── images/                    # Product & lifestyle images (fect-image)
└── src/
    └── styles/
        └── design-tokens.css         # CSS Custom Properties — 3-tier tokens (OKLCH colors, Geist+Pretendard fonts, fluid typography, spring animations)
```

## Development Notes

- All skill files use YAML frontmatter for metadata (`name`, `description`, `allowed-tools`, etc.)
- Agent files specify `tools`, `disallowedTools`, `model`, and `maxTurns` in frontmatter
- The plugin uses `$ARGUMENTS` and `$CLAUDE_PLUGIN_ROOT` as runtime variables
- Scripts receive tool input via stdin as JSON (parsed with `jq`)
- All user-facing text is in Korean (code comments excluded)
- The `data/` JSON files are large (13K+ terms) — use targeted `jq` queries rather than loading entirely

## Behavioral Guardrails (LLM 코딩 4원칙)

Four behavioral principles apply to all coding work in target projects, derived from observations on common LLM coding pitfalls (Andrej Karpathy / forrestchang). They bias toward **caution over speed** — for trivial tasks, use judgment.

These principles are inlined into the relevant skills rather than being a standalone skill:

| Principle | Inlined location | Trigger |
|-----------|-----------------|---------|
| **Think Before Coding** | `skills/service-planner/SKILL.md` (Step 0.A.1 모호성 검증) | 기획 시작 시 모호한 기능 설명 → 해석 선택지 제시 |
| **Simplicity First** | `skills/coding-convention/SKILL.md` (Behavioral Guardrails) | 모든 코드 작성/수정 시 자동 적용 |
| **Surgical Changes** | `skills/coding-convention/SKILL.md` + `skills/pr-merge/SKILL.md` (Step 8.2) | 코드 편집 + PR 리뷰 이슈 수정 시 |
| **Goal-Driven Execution** | `skills/pr-merge/SKILL.md` (Step 8.2 자동 디버그 루프) | 검증 가능한 성공 기준 기반 반복 |

**Quick reference**: `/astra-guide principles`

**ASTRA 자동 빌더 예외**: `/service-planner`, `/manual-generator`, `/catalog-generator`, `/ux-publish`, `/handoff-publish`, `/project-init`, `/sprint-init`, `/autorun` 같은 *광범위 산출물 생성형 skill*은 사용자가 명시적으로 요청한 풀 스택 산출물을 생성하므로 "Simplicity First"의 범위 제한을 받지 않는다. 다만 그 내부에서 작성하는 *개별 코드*는 4원칙을 그대로 따른다.

**Source**: [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) (MIT) — adapted into existing skills with Korean translation and ASTRA-specific scope clauses. Original inspiration: [Karpathy's LLM coding pitfall observations](https://x.com/karpathy/status/2015883857489522876).

## Scripts

```bash
# Verify Sprint 0 setup (checks global settings + project structure)
./scripts/verify-setup.sh [project-root-path]

# Initialize project directory structure only (no template content)
./scripts/init-project.sh [project-root-path]

# Hook scripts (not invoked directly — called by hooks.json)
./scripts/check-forbidden-words.sh   # stdin: JSON tool input
./scripts/validate-naming.sh         # stdin: JSON tool input
./scripts/track-sprint-progress.sh   # stdin: JSON tool input
```

## Conventions

- **버전업 필수**: main 브랜치에 푸시하기 전 반드시 `.claude-plugin/plugin.json`과 `.claude-plugin/marketplace.json`의 `version` 필드를 업데이트해야 한다. SemVer 규칙을 따른다 — 버그 수정은 patch(x.x.+1), 기능 추가는 minor(x.+1.0), 호환성 깨지는 변경은 major(+1.0.0).
- **Skill description 언어 정책**:
  - **영어 사용**: auto-trigger 스킬(`coding-convention`, `data-standard`, `code-standard`, `sprint-progress`), 검증/유틸 스킬(`project-checklist`, `astra-setup`, `sprint-init`, `astra-guide`, `test-run`, `test-scenario`, `project-init`, `catalog-generator`). LLM의 영어 description 매칭 정확도가 더 높아 자동 트리거/유틸 호출에 유리.
  - **한국어 사용**: 사용자 워크플로우 진입점인 인터랙티브 도메인 스킬(`service-planner`, `ux-publish`, `handoff-publish`, `manual-generator`, `pr-merge`, `slack-import`, `autorun`). 한국 사용자가 `/help`로 발견할 때 의도가 즉시 이해되어야 함.
  - **frontmatter 형식**: auto-trigger 스킬은 `description: >` 블록 형식(여러 줄로 트리거 조건을 명시), 명시 호출 스킬은 `description: "..."` 단일 라인 형식.
- **Agent description 가드**: 페르소나 에이전트(`tester-persona`, `designer-persona`, `developer-persona`)는 description 첫 줄에 `[EXPLICIT-INVOCATION-ONLY — DO NOT AUTO-MATCH]` 가드 prefix를 필수로 둔다. 자동 매칭 신호 약화 + 사용자 의도 명시 호출만 허용.
- Skill SKILL.md files follow a strict procedural format (단계: step-by-step instructions)
- Commands are simpler than skills — they define input/output format and delegate to data files
- All agents are read-only (`disallowedTools: Write, Edit`) — they analyze and report but never modify files
- Agent model selection: `haiku` for rule-based validation (fast), `sonnet` for complex analysis (accurate)
- Agent naming convention: `*-validator` (haiku, 규칙 검증), `*-reviewer` (sonnet, 산출물 품질 검토), `*-runner` (sonnet, 통합 실행), `*-analyzer` (sonnet, 패턴/메트릭), `*-persona` (sonnet, 시니어 관점 위임 — 명시 호출 전용)
- Hook scripts must always `exit 0` to avoid blocking the user's workflow
- `standard_terms.json` fields: `공통표준용어명` (Korean term), `공통표준용어영문약어명` (English abbreviation), `공통표준도메인명` (domain)
- `standard_words.json` fields: `공통표준단어명` (word), `공통표준단어영문약어명` (abbreviation), `금칙어목록` (forbidden words), `이음동의어목록` (synonyms)
