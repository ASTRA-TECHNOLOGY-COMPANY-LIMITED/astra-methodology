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
│   ├── sprint-plan/       # Sprint planning & initialization (/sprint-plan)
│   ├── project-checklist/ # Sprint 0 completion verification (/project-checklist)
│   ├── data-standard/     # Korean public data standard terminology (/data-standard)
│   ├── test-run/          # Chrome MCP integration testing (/test-run)
│   ├── test-scenario/     # E2E test scenario generation (/test-scenario)
│   ├── pr-merge/          # Commit→review→fix→merge full cycle (/pr-merge)
│   ├── slack-to-sprint/   # Slack List → blueprint + sprint generation (/slack-to-sprint)
│   ├── coding-convention/ # Auto-applied coding convention (Java/TS/Python/CSS/SCSS)
│   ├── auth-module/       # Auth module auto-builder (/auth-module)
│   ├── workspace-module/  # Workspace module auto-builder (/workspace-module)
│   ├── payment-module/    # Payment module auto-builder (/payment-module)
│   ├── ai-agent-module/   # AI agent platform auto-builder (/ai-agent-module)
│   ├── code-standard/     # Auto-applied international code standards (ISO/ITU)
│   ├── sprint-progress/   # Auto-applied sprint progress tracking
│   ├── service-planner/   # Design thinking based planning deliverables (/service-planner)
│   ├── ux-publish/        # UX prototype publishing from planning docs (/ux-publish)
│   ├── manual-generator/  # Service manual auto-generator with Chrome MCP screenshots (/manual-generator)
│   └── catalog-generator/ # Product promotional catalog auto-generator (/catalog-generator)
├── agents/              # Specialized Claude Code subagents (read-only, auto-discovered)
│   ├── astra-verifier.md        # ASTRA methodology compliance checker (haiku)
│   ├── naming-validator.md      # DB naming standard validation (haiku)
│   ├── convention-validator.md   # Coding convention validation (haiku)
│   ├── blueprint-reviewer.md    # Design document quality & consistency (sonnet) — Gate 2
│   ├── design-token-validator.md # Design token system compliance (haiku) — Gate 2.5
│   ├── sprint-analyzer.md       # Sprint progress & retrospective analysis (sonnet)
│   ├── quality-gate-runner.md   # Integrated quality gate execution (sonnet) — Gate 3
│   └── test-coverage-analyzer.md # Test strategy & coverage analysis (haiku) — Gate 2
├── commands/            # Slash commands
│   ├── generate-entity.md       # /generate-entity — entity code from Korean definitions
│   ├── check-naming.md          # /check-naming — DB naming standard compliance check
│   ├── check-convention.md      # /check-convention — coding convention compliance check
│   ├── lookup-term.md           # /lookup-term — standard term dictionary lookup
│   ├── lookup-code.md           # /lookup-code — international code lookup (ISO/ITU)
│   └── slack-backlog.md         # /slack-backlog — extract backlog items from Slack
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
│   ├── auth/
│   │   └── system-design.md     # Auth module reference design (AMA project)
│   ├── workspace/
│   │   ├── system-design.md     # Workspace module reference design (AMA project)
│   │   └── flow.md              # Workspace → subscription payment flow
│   ├── payment/
│   │   └── system-design.md     # Payment module reference design (AMA project)
│   ├── ai-agent/
│   │   └── system-design.md     # AI agent platform reference design (fect-api-agent)
│   ├── ux/
│   │   └── ux-interaction-patterns.md  # UX/UI interaction patterns guide (11 categories)
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

### Auth Module Auto-Builder

The `/auth-module` skill automates the entire authentication module development lifecycle:

- **Reference**: `docs/auth/system-design.md` — AMA project auth design (Next.js 14 + Firebase + PostgreSQL)
- **Pipeline**: Blueprint → Sprint Plan → Implementation → Test Scenarios → Test Run & Debug
- **Features**: signup (email + social), login/logout, token management (JWT + Token Rotation), terms management (CRUD + versioning + consent), user management (profile + admin), security (Rate Limiting, CSRF, XSS)
- **Tech adaptation**: Automatically adapts the reference design to the target project's tech stack (Spring Boot, NestJS, FastAPI, React, Vue, Angular, etc.)
- **Auto-debug**: Up to 5 retry cycles for test failures before requesting user assistance

### Workspace Module Auto-Builder

The `/workspace-module` skill automates the entire workspace management module development lifecycle:

- **Reference**: `docs/workspace/system-design.md`, `flow.md` — AMA project workspace design (Next.js 14 + PostgreSQL + Drizzle ORM)
- **Pipeline**: Blueprint → Sprint Plan → Implementation → Test Scenarios → Test Run & Debug
- **Features**: workspace CRUD (create/read/update/delete), member management (list/role-change/remove/leave/transfer-ownership), invitation system (email + link invite, accept/decline/cancel), workspace switching (WorkspaceSwitcher + default workspace), auth integration (signup → personal WS auto-creation, withdrawal → WS cleanup), billing integration (subscription ↔ member count sync)
- **DB tables**: TB_COMM_WKSPC, TR_COMM_WKSPC_MBR, TB_COMM_WKSPC_INVT + TB_COMM_USER.BSC_WKSPC_ID extension
- **Auth dependency**: Requires auth module (TB_COMM_USER, JWT authentication). Prompts user to build auth module first if not detected.
- **Tech adaptation**: Automatically adapts the reference design to the target project's tech stack
- **Auto-debug**: Up to 5 retry cycles for test failures before requesting user assistance

### Payment Module Auto-Builder

The `/payment-module` skill automates the entire subscription payment module development lifecycle:

- **Reference**: `docs/payment/system-design.md` — AMA project payment design (Next.js 14 + PostgreSQL + Drizzle ORM + TossPayments)
- **Pipeline**: Blueprint → Sprint Plan → Implementation → Test Scenarios → Test Run & Debug
- **Features**: plan management (CRUD + features/limits), payment methods (billing key issuance + AES-256 encryption), subscription management (start/change/cancel/pause/resume + proration), invoices (auto-generation + manual payment + refund), PG integration (PG-Agnostic abstraction + TossPayments/KCP adapters), webhooks (signature verification + idempotency), recurring payment scheduler (cron-based auto-renewal), dunning (4-step retry strategy), credit management (allocate/deduct/expire/adjust + atomic processing)
- **DB tables**: TB_PAY_PLAN, TB_PAY_PLAN_FNC, TB_PAY_STLM_MTHD, TB_PAY_SBSC, TH_PAY_SBSC, TB_PAY_INVC, TB_PAY_INVC_ARTCL, TB_PAY_STLM, TL_PAY_BILNG_EVNT, TL_PAY_WBHK_EVNT, TH_PAY_STLM_RTRY, TB_PAY_CRDT_BLNC, TL_PAY_CRDT_TRNS (13 tables)
- **Module dependency**: Requires auth module (TB_COMM_USER, JWT) and workspace module (TB_COMM_WKSPC, TR_COMM_WKSPC_MBR). Prompts user to build prerequisite modules first if not detected.
- **Tech adaptation**: Automatically adapts the reference design to the target project's tech stack (including PG provider: TossPayments/Stripe/KCP)
- **Auto-debug**: Up to 5 retry cycles for test failures before requesting user assistance

### AI Agent Module Auto-Builder

The `/ai-agent-module` skill automates the entire AI agent platform module development lifecycle:

- **Reference**: `docs/ai-agent/system-design.md` — fect-api-agent design (Next.js 14 + PostgreSQL + Drizzle ORM + Anthropic/OpenAI)
- **Pipeline**: Blueprint → Sprint Plan → Implementation → Test Scenarios → Test Run & Debug
- **Features**: multi-provider LLM client (Anthropic/OpenAI/Ollama via native fetch), SSE real-time streaming (20+ event types), Agent Core Loop (executeLoop with 4 safety guards), Context Building (10-step pipeline), Plugin-based tool system (PLUGIN.md → PluginManager → 20+ built-in tools), Skill system (GLOBAL/WORKSPACE/Agent mapping with on-demand + direct injection), HITL (hitl_prompt + SSE + loop interruption), Memory (pgvector flat + Neo4j graph hybrid ranking), RAG (Agentic query classification + HyDE + reranking), Sub-agent orchestration (spawn/steer/kill with depth/child limits), Model routing (complexity-based SIMPLE/VAGUE/COMPLEX) + multi-provider fallback, Conversation management (CRUD + compaction + auto-title), Secret management (AES-256-GCM + OAuth PKCE), Channel integration (Slack/Teams/Discord webhooks)
- **DB tables**: TB_AI_AGNT_CTGRY, TB_AI_AGNT, TB_AI_CNVRSTN, TH_AI_MSG, TB_AI_MMRY, TB_AI_KNWLDG_BS, TB_AI_KNWLDG_DOC, TB_AI_EMBDNG_CHNK, TB_AI_SKILL_DEF, TR_AI_CNFG_SKILL, TB_AI_MCP_SRVR, TR_AI_CNFG_MCP_SRVR, TB_AI_SBAGNT_RUN, TL_AI_SBAGNT_LOG, TL_AI_TKN_USG, TB_AI_WKSPC_SCRT, TB_AI_SYS_CRED, TH_AI_OAUTH_SESSION, TL_AI_SCRT_ACCS_LOG, TB_AI_CHNL_CNFG, TL_AI_CHNL_MSG_LOG, TB_AI_PRJCT, TL_AI_MCP_SRVR_LOG, TB_AI_SGGSTN_TMPL (24 tables)
- **Module dependency**: Requires auth module (TB_COMM_USER, JWT) and workspace module (TB_COMM_WKSPC). Optionally integrates with payment module for credit-based billing.
- **Tech adaptation**: Automatically adapts the reference design to the target project's tech stack (SSE: WebFlux/NestJS @Sse/FastAPI StreamingResponse, LLM: native fetch vs SDK, Vector DB: pgvector/Pinecone/Qdrant)
- **Auto-debug**: Up to 5 retry cycles for test failures before requesting user assistance

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
- `overview.md` remains at the root level as the project overview document

### Sprint Progress Tracking

The plugin provides automatic sprint progress tracking through a hook + skill hybrid system:

- **Hook** (`track-sprint-progress.sh`): Detects file write events matching sprint-related paths (blueprints, DB design, test cases, implementation files, test reports), appends activity log entries to the tracker file, and emits a message prompting the LLM to update the progress table
- **Auto-applied skill** (`sprint-progress/SKILL.md`): Guides the LLM to intelligently update the progress table columns (Blueprint, DB Design, Test Cases, Implementation, Test Report) based on the event type
- **Sprint directory format**: `sprint-{N}-{feature-name}/` (e.g., `sprint-1-auth/`, `sprint-2-workspace/`) — includes the primary blueprint name for traceability
- **Tracker file**: `docs/sprints/sprint-{N}-{feature-name}/progress.md` — contains a feature progress table, summary statistics, and an activity log
- Tracker is auto-created during `/sprint-plan` initialization, or created on-demand by the skill when an event is detected but no tracker exists

### UX Prototype Publishing

The `/ux-publish` skill generates production-grade HTML prototypes from planning documents:

- **Input**: `docs/planner/{NNN}-{feature-name}/` (requires `ia-screen-design.md` + `feature-definition.md` from `/service-planner`)
- **Output**: `ux/{feature-name}/` — self-contained HTML prototype viewable in browser (no build required)
- **Design quality**: Uses `/frontend-design` skill for production-grade, distinctive UI (avoids generic AI aesthetics)
- **AI images**: Uses `fect-image` MCP (`mcp__fect-image__image_text2img`) for hero banners, empty state illustrations, avatars, backgrounds
- **Interaction patterns**: References `docs/ux/ux-interaction-patterns.md` (11 categories: micro-interactions, navigation, feedback, scroll, form, transitions, onboarding, accessibility, delight, dark patterns to avoid)
- **Design tokens**: Strictly references project's `src/styles/design-tokens.css` (no hardcoded values)
- **Components**: Follows `docs/design-system/components.md` specifications
- **Layout**: Implements `docs/design-system/layout-grid.md` grid system
- **Features**: Responsive (mobile/tablet/desktop), dark mode, accessibility (WCAG AA), `prefers-reduced-motion` support
- **Design direction**: User selects aesthetic tone (Refined Minimal, Bold & Vibrant, Soft & Warm, Editorial, Professional Enterprise, or Auto)

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
- **Document-only mode**: If no URL provided, generates manual from blueprints/planner docs without screenshots (or uses `ux/` prototypes)

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

### Slack Integration

The plugin integrates with Slack via the `fect-slack` MCP server to collect requirements directly from team communication channels:

- **`/slack-to-sprint`** (skill): Full interactive workflow — list channels → select channel → select List → select Items → update status → analyze requirements → generate blueprints + sprint prompt map + progress tracker
- **`/slack-backlog`** (command): Quick extraction — fetch messages from a channel and output a structured backlog table with priorities
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
├── ux/                                # UX prototypes (generated by /ux-publish)
│   └── {feature-name}/               # Per-feature prototype
│       ├── index.html                 # Screen index & navigation hub
│       ├── assets/                    # CSS (tokens, base, components, interactions)
│       ├── images/                    # AI-generated image assets (fect-image)
│       ├── screens/                   # Individual screen HTML files
│       └── shared/                    # Common JS (nav, interactions)
├── catalog/                           # Product catalogs (generated by /catalog-generator)
│   └── {catalog-name}/               # Per-catalog package
│       ├── index.html                 # Catalog main page
│       ├── assets/                    # CSS, JS, fonts
│       └── images/                    # Product & lifestyle images (fect-image)
└── src/
    └── styles/
        └── design-tokens.css         # CSS Custom Properties (source code)
```

## Development Notes

- All skill files use YAML frontmatter for metadata (`name`, `description`, `allowed-tools`, etc.)
- Agent files specify `tools`, `disallowedTools`, `model`, and `maxTurns` in frontmatter
- The plugin uses `$ARGUMENTS` and `$CLAUDE_PLUGIN_ROOT` as runtime variables
- Scripts receive tool input via stdin as JSON (parsed with `jq`)
- All user-facing text is in Korean (code comments excluded)
- The `data/` JSON files are large (13K+ terms) — use targeted `jq` queries rather than loading entirely

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
- Skill SKILL.md files follow a strict procedural format (단계: step-by-step instructions)
- Commands are simpler than skills — they define input/output format and delegate to data files
- All agents are read-only (`disallowedTools: Write, Edit`) — they analyze and report but never modify files
- Agent model selection: `haiku` for rule-based validation (fast), `sonnet` for complex analysis (accurate)
- Hook scripts must always `exit 0` to avoid blocking the user's workflow
- `standard_terms.json` fields: `공통표준용어명` (Korean term), `공통표준용어영문약어명` (English abbreviation), `공통표준도메인명` (domain)
- `standard_words.json` fields: `공통표준단어명` (word), `공통표준단어영문약어명` (abbreviation), `금칙어목록` (forbidden words), `이음동의어목록` (synonyms)
