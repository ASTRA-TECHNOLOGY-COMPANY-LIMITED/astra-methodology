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

### Hooks Architecture

`hooks/hooks.json` defines hooks that run automatically:

**PostToolUse hooks** (run after Write/Edit operations):
1. **check-forbidden-words.sh** — scans DB-related files for forbidden words from the standard dictionary
2. **validate-naming.sh** — checks table name prefixes in SQL, Java (@Table), TypeScript (@Entity), Python (__tablename__)
3. **track-sprint-progress.sh** — detects sprint-related file events and appends activity log entries to the sprint progress tracker
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
Role-based mindset agents that bring senior-practitioner perspective. **Never auto-trigger** — must be explicitly invoked by user (e.g., "테스터 관점에서", "디자이너로서") or by orchestrating skills.

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
| `/service-planner` | Design Thinking 기반 기획 (markdown 6종 + HTML 기획화면). 모드: 신규/개선. 자동 결정: 디자인 톤 5종 중 페르소나 기반 선택. |
| `/handoff-publish` | UX/UI/Dev/QA 협업 패키지 — Screen ID 기반 14파일. UX가 ID 발급 단독 권한. `{feature-name}-handoff/`에 출력. |
| `/manual-generator` | Service URL + 프로젝트 docs → self-contained HTML 매뉴얼. Chrome MCP 스크린샷 + 어노테이션. |
| `/catalog-generator` | 제품 데이터 → self-contained HTML 카탈로그. AI 이미지(fect-image) + 영업 전략 자동 적용. |
| `/autorun` | 무인 풀 파이프라인: `/service-planner` → planner-reviewer → design-token-validator → blueprint → blueprint-reviewer → `/sprint-init` → 구현 → `/test-scenario` → `/test-run` (5회 자동 디버그). `/pr-merge` 직전 정지. |
| `/slack-import` | Slack List/메시지 → 청사진 + 스프린트 프롬프트 맵 + 진행 트래커. `SLACK_BOT_TOKEN` 필요. |
| `/extract-backlog` | Slack 채널 메시지 → 우선순위 백로그 표 (가벼운 명령). |

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

**ASTRA 자동 빌더 예외**: `/service-planner`, `/manual-generator`, `/catalog-generator`, `/handoff-publish`, `/project-init`, `/sprint-init`, `/autorun` 같은 *광범위 산출물 생성형 skill*은 사용자가 명시적으로 요청한 풀 스택 산출물을 생성하므로 "Simplicity First"의 범위 제한을 받지 않는다. 다만 그 내부에서 작성하는 *개별 코드*는 4원칙을 그대로 따른다.

**Source**: [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) (MIT) — adapted into existing skills with Korean translation and ASTRA-specific scope clauses.

## Skill Authoring

새 SKILL.md를 작성하거나 기존 스킬을 수정할 때는 [`docs/development/skill-authoring-guide.md`](docs/development/skill-authoring-guide.md)를 참조한다 — 핵심 원칙, frontmatter 필드, description 7원칙, progressive disclosure, 안티패턴, ASTRA 체크리스트.

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
  - **한국어 사용**: 사용자 워크플로우 진입점인 인터랙티브 도메인 스킬(`service-planner`, `handoff-publish`, `manual-generator`, `pr-merge`, `slack-import`, `autorun`). 한국 사용자가 `/help`로 발견할 때 의도가 즉시 이해되어야 함.
  - **frontmatter 형식**: auto-trigger 스킬은 `description: >` 블록 형식, 명시 호출 스킬은 `description: "..."` 단일 라인 형식.
- **Agent description 가드**: 페르소나 에이전트(`tester-persona`, `designer-persona`, `developer-persona`)는 description 첫 줄에 `[EXPLICIT-INVOCATION-ONLY — DO NOT AUTO-MATCH]` 가드 prefix를 필수로 둔다.
- Skill SKILL.md files follow a strict procedural format (단계: step-by-step instructions)
- Commands are simpler than skills — they define input/output format and delegate to data files
- All agents are read-only (`disallowedTools: Write, Edit`) — they analyze and report but never modify files
- Agent model selection: `haiku` for rule-based validation (fast), `sonnet` for complex analysis (accurate)
- Agent naming convention: `*-validator` (haiku, 규칙 검증), `*-reviewer` (sonnet, 산출물 품질 검토), `*-runner` (sonnet, 통합 실행), `*-analyzer` (sonnet, 패턴/메트릭), `*-persona` (sonnet, 시니어 관점 위임 — 명시 호출 전용)
- Hook scripts must always `exit 0` to avoid blocking the user's workflow
- `standard_terms.json` fields: `공통표준용어명` (Korean term), `공통표준용어영문약어명` (English abbreviation), `공통표준도메인명` (domain)
- `standard_words.json` fields: `공통표준단어명` (word), `공통표준단어영문약어명` (abbreviation), `금칙어목록` (forbidden words), `이음동의어목록` (synonyms)
