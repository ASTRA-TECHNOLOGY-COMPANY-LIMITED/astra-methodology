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
│   ├── coding-convention/ # Auto-applied coding convention (Java/TS/Python/CSS/SCSS)
│   ├── code-standard/     # Auto-applied international code standards (ISO/ITU)
│   └── sprint-progress/   # Auto-applied sprint progress tracking
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
│   └── lookup-code.md           # /lookup-code — international code lookup (ISO/ITU)
├── hooks/               # PostToolUse hooks (hooks.json)
├── scripts/             # Shell scripts for hooks and verification
├── data/                # Standard dictionary and international code JSON files
│   ├── standard_terms.json        # 13,176 standard terms (Korean→English abbreviation)
│   ├── standard_words.json        # 3,284 standard words (abbreviations, forbidden words)
│   ├── standard_domains.json      # 123 standard domains (type codes, lengths)
│   ├── iso_3166_1_countries.json  # 249 ISO 3166-1 country codes
│   ├── iso_3166_2_regions.json    # 653 ISO 3166-2 region codes (21 countries)
│   └── country_calling_codes.json # 245 ITU-T E.164 calling codes
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

`hooks/hooks.json` defines PostToolUse hooks that run automatically after Write/Edit operations:
1. **check-forbidden-words.sh** — scans DB-related files for forbidden words from the standard dictionary
2. **validate-naming.sh** — checks table name prefixes in SQL, Java (@Table), TypeScript (@Entity), Python (__tablename__)
3. **track-sprint-progress.sh** — detects sprint-related file events (blueprints, DB design, test cases, implementation, test reports) and appends activity log entries to the sprint progress tracker
4. All hooks are non-blocking (exit 0) — they emit warnings only

### Sprint Progress Tracking

The plugin provides automatic sprint progress tracking through a hook + skill hybrid system:

- **Hook** (`track-sprint-progress.sh`): Detects file write events matching sprint-related paths (blueprints, DB design, test cases, implementation files, test reports), appends activity log entries to the tracker file, and emits a message prompting the LLM to update the progress table
- **Auto-applied skill** (`sprint-progress/SKILL.md`): Guides the LLM to intelligently update the progress table columns (Blueprint, DB Design, Test Cases, Implementation, Test Report) based on the event type
- **Tracker file**: `docs/sprints/sprint-{N}/progress.md` — contains a feature progress table, summary statistics, and an activity log
- Tracker is auto-created during `/sprint-plan` initialization, or created on-demand by the skill when an event is detected but no tracker exists

### Target Project Structure (generated by /astra-methodology)

When the plugin initializes a target project, it creates:
```
{project}/
├── CLAUDE.md                          # Project-specific AI rules
├── docs/
│   ├── design-system/                 # Design tokens, components, layout grid
│   ├── blueprints/                    # Feature design documents
│   ├── database/                      # DB design (SSoT), naming rules, migrations
│   ├── tests/                         # Test strategy, test cases, test reports
│   ├── sprints/                       # Sprint documents (prompt maps, progress trackers, retrospectives)
│   └── delivery/                     # Release artifacts
└── src/
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
