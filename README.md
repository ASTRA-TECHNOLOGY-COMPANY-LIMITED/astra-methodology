# ASTRA Methodology

**AI-augmented Sprint Through Rapid Assembly** - Claude Code plugin for Sprint 0 project initialization, data standard enforcement, and quality gates.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Overview

ASTRA is an AI-augmented sprint methodology plugin based on Claude Code. It automates DB naming validation, entity code generation, and quality gates based on the Korean Public Data Standard (Ministry of the Interior and Safety Common Standard Terms, 8th edition).

### VIP Principles

| Principle | Description |
|------|------|
| **V**ibe-driven Development | Natural language-based development — design with prompts, AI implements |
| **I**nstant Feedback Loop | Validate as you write — hooks and agents verify quality in real-time |
| **P**lugin-powered Quality | Plugin-based quality management — automated gates ensure consistency |

## Installation

### 1. Global Environment Setup

```bash
# Run in Claude Code
/astra-setup
```

This command configures the following:
- `~/.claude/settings.json` — Global settings (agent team, bypass mode, etc.)
- `~/.claude/.mcp.json` — MCP server registration (Chrome DevTools, PostgreSQL, Context7)
- Required tools check (Node.js, Git, GitHub CLI)

### 2. Plugin Installation

```bash
claude plugin marketplace add https://github.com/ASTRA-TECHNOLOGY-COMPANY-LIMITED/astra-methodology.git
claude plugin install astra-methodology@astra
```

### 3. Project Initialization (Sprint 0)

```bash
# Run in Claude Code
/project-init [project-name] [backend-tech] [frontend-tech] [DB-type]
```

## Skills (Slash Commands)

| Command | Description |
|--------|------|
| `/astra-setup` | Global development environment setup (Step 0.0) |
| `/astra-guide` | ASTRA methodology quick reference (sprint, review, release, gates, roles) |
| `/project-init` | Sprint 0 project structure generation — CLAUDE.md, design system, DB design docs, test strategy templates |
| `/project-checklist` | Sprint 0 completion verification — checks project structure, CLAUDE.md, design tokens, DB design, test strategy |
| `/sprint-plan` | New sprint initialization — auto-generates prompt map, progress tracker, retrospective templates |
| `/test-run` | Chrome MCP-based E2E integration test — server startup, scenario execution, report generation |
| `/test-scenario` | E2E test scenario generation — analyzes blueprints, DB design, routes, and API endpoints |
| `/data-standard` | Korean public data standard term application guide |

### Auto-applied Skills (no slash command — applied automatically)

| Skill | Trigger |
|-------|---------|
| `coding-convention` | When editing Java, TypeScript, React Native, Python, CSS/SCSS files |
| `code-standard` | When implementing phone number inputs, country/region selectors |
| `sprint-progress` | When writing sprint-related files (blueprints, DB design, tests, src/) |

## Commands (Data Standard Tools)

| Command | Description | Usage Example |
|--------|------|-----------|
| `/lookup-term` | Standard term lookup | `/lookup-term 고객명` |
| `/lookup-code` | International code lookup (ISO/ITU) | `/lookup-code KR` |
| `/generate-entity` | Korean definition -> Entity code generation | `/generate-entity 고객 테이블: 고객명, 고객번호, 생년월일` |
| `/check-naming` | DB naming standard compliance check | `/check-naming src/entity/Customer.java` |
| `/check-convention` | Coding convention compliance check | `/check-convention src/` |

### `/lookup-term` Example

```
Input: /lookup-term 가입일자

Result:
┌──────────────┬─────────────┬───────────┬──────────┐
│ Standard Term│ Eng. Abbr.  │ Domain    │ Data Type│
├──────────────┼─────────────┼───────────┼──────────┤
│ 가입일자      │ JOIN_YMD    │ 연월일C8  │ CHAR(8)  │
└──────────────┴─────────────┴───────────┴──────────┘
```

### `/generate-entity` Example

```
Input: /generate-entity 고객 테이블: 고객명, 고객번호, 생년월일, 사용여부

Generated Code (Java JPA):
@Entity
@Table(name = "TB_CSTMR")
public class TbCstmr {
    @Id @Column(name = "CSTMR_SN")
    private Long cstmrSn;

    @Column(name = "CSTMR_NM", length = 100)
    private String cstmrNm;

    @Column(name = "CSTMR_NO", length = 20)
    private String cstmrNo;

    @Column(name = "BRDT_YMD", columnDefinition = "CHAR(8)")
    private String brdtYmd;

    @Column(name = "USE_YN", columnDefinition = "CHAR(1) DEFAULT 'Y'")
    private String useYn;
}
```

## Agents

| Agent | Model | Description |
|----------|------|------|
| `naming-validator` | haiku | DB entity naming standard validation — column names, suffix patterns, domain rules, forbidden word detection |
| `astra-verifier` | haiku | ASTRA methodology compliance verification (read-only) — project structure, CLAUDE.md, design document checks |
| `convention-validator` | haiku | Coding convention validation (Java/TS/RN/Python/CSS/SCSS) — Gate 1/2 |
| `blueprint-reviewer` | sonnet | Design document quality & consistency — Gate 2 |
| `design-token-validator` | haiku | Design token system compliance — Gate 2.5 |
| `sprint-analyzer` | sonnet | Sprint progress & retrospective analysis |
| `quality-gate-runner` | sonnet | Integrated quality gate execution — Gate 3 |
| `test-coverage-analyzer` | haiku | Test strategy & coverage analysis — Gate 2 |

## Hooks (Automatic Quality Verification)

PostToolUse hooks that run automatically when files are created/modified:

| Hook | Trigger | Action |
|----|--------|------|
| `validate-naming.sh` | Write/Edit (DB-related files) | Table name prefix validation (TB_, TC_, TH_, TL_, TR_) |
| `check-forbidden-words.sh` | Write/Edit (DB-related files) | Forbidden word detection and standard term replacement recommendation |
| `track-sprint-progress.sh` | Write/Edit (sprint-related files) | Sprint progress activity log auto-tracking |

All hooks are non-blocking (exit 0) — they display warnings only and do not interrupt the workflow.

## Quality Gates

```
Gate 1 (Write-time)          Gate 2 (Review-time)         Gate 2.5 (Design)            Gate 3 (Release)
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ - Forbidden word │    │ - Code review    │    │ - Design review  │    │ - /check-naming  │
│   check          │    │ - PR review      │    │ - Chrome MCP     │    │ - Integration    │
│ - Naming valid.  │    │ - Manual + AI    │    │ - Responsive     │    │   test           │
│ - Auto (Hook)    │    │                  │    │   validation     │    │ - Pre-deploy     │
│                  │    │                  │    │                  │    │   verification   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Korean Public Data Standard

Based on Ministry of the Interior and Safety Common Public Data Standard, 8th edition (2025-11):

| Data | Count | Description |
|--------|------|------|
| `standard_terms.json` | 13,176 | Standard terms (Korean name -> English abbreviation -> domain) |
| `standard_words.json` | 3,284 | Standard words (abbreviations, forbidden words, synonyms) |
| `standard_domains.json` | 123 | Standard domains (data type, length, decimal places) |

### Naming Rules

**Table Prefixes:**
- `TB_` — General table
- `TC_` — Code table
- `TH_` — History table
- `TL_` — Log table
- `TR_` — Relation table

**Column Suffixes:**

| Suffix | Meaning | Example |
|--------|------|------|
| `_NM` | Name | `CSTMR_NM` (customer name) |
| `_CD` | Code | `STTS_CD` (status code) |
| `_NO` | Number | `CSTMR_NO` (customer number) |
| `_YMD` | Date (YYYYMMDD) | `JOIN_YMD` (join date) |
| `_DT` | Datetime | `REG_DT` (registration datetime) |
| `_AMT` | Amount | `SLE_AMT` (sales amount) |
| `_CN` | Content | `NTIC_CN` (notice content) |
| `_YN` | Yes/No flag | `USE_YN` (use status) |
| `_SN` | Sequence number | `CSTMR_SN` (customer sequence) |
| `_CNT` | Count | `INQR_CNT` (inquiry count) |
| `_ADDR` | Address | `BASS_ADDR` (base address) |

## Project Structure (Generated Project)

Structure generated in the target project when `/project-init` is executed:

```
{project}/
├── CLAUDE.md                              # Project AI rules
├── .claude/settings.json                  # Claude Code project settings
├── docs/
│   ├── design-system/                     # Design tokens, components, layout
│   │   └── references/                    # Design reference images
│   ├── blueprints/                        # Feature design documents
│   ├── database/                          # DB design (SSoT), naming rules
│   │   └── migration/                     # Migration history
│   ├── tests/                             # Test strategy, cases, reports
│   │   ├── test-cases/
│   │   └── test-reports/
│   ├── sprints/                           # Sprint documents (prompt maps, progress, retrospectives)
│   └── delivery/                          # Release artifacts
└── src/                                   # Source code
```

## Sprint Workflow

### Sprint 0 (Project Setup)

```
Step 0.0  /astra-setup            → Global environment setup
Step 0.1  /project-init           → Project structure generation
Step 0.2  Design document writing  → Design tokens, DB design, test strategy
Step 0.3  /project-checklist      → Sprint 0 completion verification
```

### Sprint N (Feature Development)

```
Mon  Sprint Planning    → /sprint-plan N → Write prompt map
Tue  Feature Dev        → /feature-dev → Design → Implement → Test
Wed  Feature Dev        → Hook auto-verification (forbidden words, naming)
Thu  Review             → /check-naming → Code review → Design review
Fri  Release            → /test-run → Deploy
```

### Team Roles

| Role | Description |
|------|------|
| **VA** (Vibe Architect) | Project vision design, Sprint 0 lead, quality gate management |
| **PE** (Prompt Engineer) | Prompt map writing, AI pair programming, code review |
| **DE** (Domain Expert) | Domain requirements definition, data standard verification, acceptance testing |
| **DSA** (Design System Architect) | Design token management, UI consistency verification, responsive testing |

## Repository Structure

```
astra-methodology/
├── skills/                        # 11 Claude Code skills
│   ├── astra-setup/               #   Global dev environment setup (/astra-setup)
│   ├── astra-guide/               #   Methodology quick reference (/astra-guide)
│   ├── project-init/              #   Sprint 0 project initialization (/project-init)
│   ├── project-checklist/         #   Sprint 0 completion verification (/project-checklist)
│   ├── sprint-plan/               #   Sprint planning & initialization (/sprint-plan)
│   ├── sprint-progress/           #   Sprint progress auto-tracking (auto-applied)
│   ├── test-run/                  #   Chrome MCP integration test (/test-run)
│   ├── test-scenario/             #   E2E test scenario generation (/test-scenario)
│   ├── data-standard/             #   Public data standard guide (/data-standard, auto-applied)
│   ├── coding-convention/         #   Coding convention (auto-applied)
│   └── code-standard/             #   International code standards (auto-applied)
├── agents/                        # 8 specialized agents
│   ├── astra-verifier.md          #   ASTRA compliance verification
│   ├── naming-validator.md        #   DB naming standard validation
│   ├── convention-validator.md     #   Coding convention validation
│   ├── blueprint-reviewer.md      #   Design document quality & consistency
│   ├── design-token-validator.md  #   Design token system compliance
│   ├── sprint-analyzer.md         #   Sprint progress & retrospective analysis
│   ├── quality-gate-runner.md     #   Integrated quality gate execution
│   └── test-coverage-analyzer.md  #   Test strategy & coverage analysis
├── commands/                      # 6 slash commands
│   ├── generate-entity.md         #   /generate-entity
│   ├── check-naming.md            #   /check-naming
│   ├── check-convention.md        #   /check-convention
│   ├── lookup-term.md             #   /lookup-term
│   └── lookup-code.md             #   /lookup-code
├── hooks/                         # PostToolUse hooks
│   └── hooks.json
├── scripts/                       # Shell scripts
│   ├── verify-setup.sh            #   Sprint 0 verification
│   ├── init-project.sh            #   Directory structure generation
│   ├── validate-naming.sh         #   Table name prefix validation
│   ├── check-forbidden-words.sh   #   Forbidden word detection
│   └── track-sprint-progress.sh   #   Sprint progress tracking
├── data/                          # Public data standard & international code dictionary
│   ├── standard_terms.json        #   13,176 standard terms
│   ├── standard_words.json        #   3,284 standard words
│   ├── standard_domains.json      #   123 standard domains
│   ├── iso_3166_1_countries.json  #   249 ISO 3166-1 country codes
│   ├── iso_3166_2_regions.json    #   653 ISO 3166-2 region codes
│   └── country_calling_codes.json #   245 ITU-T E.164 calling codes
├── .claude-plugin/
│   └── plugin.json                # Plugin manifest
└── CLAUDE.md                      # Project AI rules
```

## Prerequisites

- [Claude Code](https://claude.com/claude-code) CLI
- Node.js 18+
- Git
- GitHub CLI (`gh`)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**Zeans.L** — [zeans@astravision.co.kr](mailto:zeans@astravision.co.kr)

ASTRA TECHNOLOGY COMPANY LIMITED
