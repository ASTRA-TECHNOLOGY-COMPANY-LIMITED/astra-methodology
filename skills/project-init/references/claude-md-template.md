# CLAUDE.md Template (Step 4)

Customize this skeleton with the project information gathered in Steps 0–2 and write it to `{project-root}/CLAUDE.md`. Sections marked "For Web" / "For Mobile" / "{additional when Mobile project:}" are conditional — include only the branch matching the Step 0.5 platform selection. If the user selected Korean or Vietnamese in Step 0, translate all prose (headers, tables, descriptions, diagrams, rules) into that language; keep technical identifiers (tool names, paths, command names) untranslated.

## Sections in this template
- Language · Architecture (Web/Mobile branches) · Key Modules
- ASTRA Methodology (VIP principles · sprint cycle · team roles)
- Development Workflow (+ per-stage reference table)
- Quality Gates (Gate 1 / 2 / 2.5 / 3 + pass-criteria summary)
- Coding Rules · Design Rules (Web/Mobile branches) · Prohibited Practices
- Testing Rules · Commit Convention · Design Document Rules
- Quick Command Reference · Prompt Writing Guide
- Per-tech-stack custom rules (Web frameworks / Mobile frameworks)

~~~markdown
# Project: {project-name}

> {project description}

## Language

- **Project language**: {selected language name} ({selected language code})
- All Claude responses, generated documents, and template content must be written in the language above.
- Technical identifiers (tool names, file paths, command names, code comments) remain in their original language.

## Architecture

**For Web projects (Step 0.5 = Web):**

- Backend: {backend tech stack}
- Frontend: {frontend tech stack}
- Database: {DB type}

**For Mobile projects (Step 0.5 = Mobile):**

- Platform: Mobile ({target platforms: Android/iOS/Both})
- Framework: {mobile framework} (e.g., React Native/Expo, Flutter, Kotlin Multiplatform)
- Backend Strategy: {backend strategy} (e.g., separate API server / Firebase / Supabase / existing API integration)
- Backend: {backend tech stack, if applicable}
- Database: {DB type, if applicable}

## Key Modules
{list modules as bullet points}

## ASTRA Methodology

This project follows the **ASTRA (AI-augmented Sprint Through Rapid Assembly)** methodology.

### VIP Principles
| Principle | Core | Realizing tools |
|-----------|------|-----------------|
| **V**ibe-driven Development | Do not write code — convey intent | `feature-dev`, `frontend-design` |
| **I**nstant Feedback Loop | Shorten feedback cycles to the hour | browser backend (ego → `chrome-devtools` MCP), `code-review` |
| **P**lugin-powered Quality | Quality is embedded into code | `astra-methodology`, `security-guidance`, `hookify` |

### Sprint cycle
- **1-week** sprint (small increments, fast feedback)
- AI processes development + tests + reviews in parallel to improve agility in short cycles

### Team roles
| Role | Assignment | Main activities |
|------|------------|-----------------|
| **VA** (Vibe Architect) | 1 senior developer | Sprint management, AI workflow design, architecture decisions, quality gate judgment |
| **PE** (Prompt Engineer) | 1-2 junior developers | Prompt authoring, AI output verification, design document supplementation |
| **DE** (Domain Expert) | 1 customer-side business owner | Requirements delivery, backlog prioritization, real-time feedback, acceptance verification |
| **DSA** (Design System Architect) | 1 designer | Design system construction, AI-generated UI review, design token management |

## Development Workflow

```
[Feature sprint]
Blueprint authoring → DB design → Sprint authoring → Implementation → Test scenarios → Test execution → PR/review
                                                                                                              ↓
                                            Main branch merge ← User test ← Staging merge ←──────────────────┘
```

### Per-stage reference documents
| Stage | Reference path | Main tool |
|-------|----------------|-----------|
| Service planning | `docs/planner/{NNN}-{feature-name}/` | `/service-planner` |
| Design system | `src/styles/design-tokens.css`, `docs/design-system/` | `/frontend-design` |
| Blueprint authoring | `docs/blueprints/{NNN}-{feature-name}/` | `/feature-dev` (do not modify code yet) |
| DB design | `docs/database/database-design.md` | `/feature-dev`, `/lookup-term` |
| Sprint planning | `docs/sprints/sprint-N/prompt-map.md` | `/sprint-init` |
| Implementation | `src/` | `/feature-dev` (based on Blueprint + DB design) |
| Test scenarios | `docs/tests/test-cases/sprint-N/` | `/test-scenario` |
| Test execution | `docs/tests/test-reports/` | `/test-run` |
| PR/review | - | `/pr-merge`, `/code-review` |

## Quality Gates

### Gate 1: WRITE-TIME (auto-applied — when writing code)
| Tool | Checks | Behavior |
|------|--------|----------|
| `security-guidance` | 9 security patterns (eval, innerHTML, etc.) | PreToolUse hook, **blocks** |
| `astra-methodology` | forbidden words + naming rules | PostToolUse hook, warning |
| `hookify` | per-project custom rules | PreToolUse/PostToolUse hook |
| `coding-convention` skill | Java/TS/RN/Python/CSS/SCSS convention | Auto-detect and apply |
| `data-standard` skill | Public data standard term dictionary | Auto-detected on DB code |
| `code-standard` skill | ISO 3166-1/2, ITU-T E.164 | Auto-detected on phone/country/address |

### Gate 2: REVIEW-TIME (during PR/review)
| Tool | Checks |
|------|--------|
| `feature-dev` (built-in code-reviewer) | Code quality/bugs/conventions (3 parallel agents) |
| `/code-review` | CLAUDE.md compliance, bugs, history analysis (80+ score filtering) |
| `blueprint-reviewer` agent | Design document quality/consistency verification |
| `test-coverage-analyzer` agent | Test strategy/coverage analysis |
| `convention-validator` agent | Coding convention verification |

### Gate 2.5: DESIGN-TIME (DSA design review)
| Review item | Verification method |
|-------------|---------------------|
| Design token compliance | browser backend + `design-token-validator` agent |
| Component consistency | Per-screen comparison |
| Responsive layout | browser viewport switching (`/test-run`) |
| Basic accessibility check | Color contrast, focus check |

### Gate 3: BRIDGE-TIME (final quality gate at release time)
- `quality-gate-runner` agent runs Gate 1~3 integrated
- 0 convention/naming violations and 0 console errors required

### Quality gate pass-criteria summary
| Gate | Pass criteria | Action when blocked |
|------|---------------|---------------------|
| Gate 1 | 0 security-guidance warnings, 0 forbidden words | Fix immediately and re-author |
| Gate 2 | 0 high-confidence code-review issues, 70%+ coverage | Decide fix now / fix later |
| Gate 2.5 | DSA design review approved | Edit prompts → regenerate → re-review |
| Gate 3 | 0 convention/naming violations, 0 console errors | Bulk-fix then release |

## Coding Rules
- An authentication middleware is required on every API endpoint
- Manage the DB schema as the single source of truth (SSoT) in docs/database/database-design.md
- DB entities must comply with the public data standard term dictionary (use `/lookup-term`)
- Table name prefixes: TB_ (general), TC_ (code), TH_ (history), TL_ (log), TR_ (relation)
- REST API response shape: `{ success: boolean, data: T, error?: string }`
- Error handling: distinguish business exceptions from system exceptions
- Per-language coding conventions are auto-applied by the `coding-convention` skill (Java/TypeScript/React Native/Python/CSS/SCSS)
- Use `/check-convention src/` to manually verify convention compliance

## Design Rules (DSA-defined)

**Web projects:**
- Design tokens: src/styles/design-tokens.css must be referenced (3-tier: Primitive → Semantic → Component)
- Color: based on OKLCH color space; using Semantic tokens (--surface-*, --text-*, --action-*, --status-*) is required; do not reference Primitive directly
- Fonts: Geist Sans + Pretendard (Korean script) by default; size must use Fluid tokens (--fluid-*) or Static tokens (--text-*)
- Spacing: 4px base grid; follow the token scale (--space-*) or Fluid (--fluid-space-*)
- Responsive: 5-tier breakpoints (xs~2xl); implement component-level responsiveness with Container Queries
- Animation: use Spring easing (--ease-spring-*); `prefers-reduced-motion` handling required
- Dark mode: Semantic token swap approach (no pure black; use layered elevation)
- Verify tokens/components visually with the design system preview page
- Auto-verify with the `design-token-validator` agent (Gate 2.5)

**Mobile projects (replacement when Step 0.5 = Mobile):**
- **Read the mobile design guide first**: reference the ASTRA mobile design guide for every UI implementation (platform guidelines, touch interactions, animation timing, haptic feedback, accessibility, expert know-how)
- React Native: must reference `src/styles/design-tokens.ts`; use StyleSheet or NativeWind utilities
- Flutter: must reference `lib/shared/theme/design_tokens.dart`; required use of `Theme.of(context)`
- KMP: must reference `composeApp/src/commonMain/kotlin/theme/DesignTokens.kt`; required use of MaterialTheme
- Follow the 3-tier design token structure (Reference → Semantic → Component)
- Hardcoding color, font, and spacing is strictly forbidden (reference token constants/theme)
- Follow the 8dp grid system
- Dark mode support is required (linked to system setting; use #121212 instead of pure black (#000000))
- Accessibility: minimum touch area 44×44dp (iOS 44pt, Android 48dp), screen reader labels required, color contrast 4.5:1
- Animation: micro feedback 50~150ms, state transitions 150~300ms, screen transitions 250~400ms, `prefers-reduced-motion` handling required
- Haptic feedback: apply appropriate haptic types to state-change interactions (Selection, Impact, Notification)
- Thumb zone: place CTA buttons in the lower 1/3 of the screen
- Verify tokens/components visually with the design system preview screen

## Prohibited Practices
- console.log forbidden (use a logger)
- `any` type forbidden
- Direct SQL forbidden (use an ORM)
- Committing .env files forbidden
{additional when Mobile project:}
- Inline styles forbidden (use design tokens/themes)
- Hardcoded API URLs forbidden (use environment variables)
- Do not branch directly on `Platform.OS === 'ios'`; use an abstraction layer
- Committing keystore/signing keys forbidden

## Testing Rules
- Write unit tests on every service layer
- Minimum test coverage 70%
- Test strategy: `docs/tests/test-strategy.md`
- Test cases: `docs/tests/test-cases/sprint-N/` (managed per sprint)
- Test reports: `docs/tests/test-reports/` (with coverage achievement)
- Auto-generate E2E scenarios with `/test-scenario`; run real-browser integration tests with `/test-run` (ego (lite) by default, Chrome MCP as fallback)
{additional when Mobile project:}
- React Native: component tests with Jest + React Native Testing Library; E2E with Detox/Maestro
- Flutter: unit/widget tests with `flutter test`; integration tests under `integration_test/`
- KMP: shared logic tests in `commonTest`; platform-specific tests in `androidTest`/`iosTest`

## Commit Convention
- Conventional Commits (feat:, fix:, refactor:, docs:, test:)
- `/commit` — auto-generate commit messages
- `/commit-push-pr` — commit + push + PR in one go
- `/pr-merge` — full cycle: commit → PR → review → fix → merge

## Design Document Rules
- Per-feature design documents are organized as docs/blueprints/{NNN}-{feature-name}/ directories (e.g., 001-auth/, 002-payment/)
- The main file in each blueprint directory is blueprint.md; place related supporting files (diagrams, API specs) in the same directory
- DB design is centrally managed in docs/database/database-design.md
- Design documents must be authored and approved before feature implementation
- Blueprint-driven workflow: blueprint authoring → DE approval → DB design reflection → sprint prompt map authoring → implementation
- Design document quality is verified by the `blueprint-reviewer` agent (Gate 2)

## Quick Command Reference

| Situation | Command |
|-----------|---------|
| Initial project setup | `/project-init` |
| Sprint 0 checklist | `/project-checklist` |
| Sprint initialization | `/sprint-init [N]` |
| Feature design/implementation | `/feature-dev [description]` |
| Standard-term lookup | `/lookup-term [Korean term]` |
| International code lookup | `/lookup-code [code]` |
| DB entity generation | `/generate-entity [Korean definition]` |
| E2E test scenarios | `/test-scenario` |
| Run integration tests | `/test-run` |
| Check coding conventions | `/check-convention [target]` |
| Check DB naming | `/check-naming [target]` |
| Commit | `/commit` |
| Commit + push + PR in one | `/commit-push-pr` |
| Automate PR → review → merge | `/pr-merge` |
| Code review | `/code-review` |
| Generate hook rules | `/hookify [description]` |
| Quick reference guide | `/astra-guide` |

## Prompt Writing Guide

The 5 elements of a good prompt:

1. **What**: a clear description of the feature to build
2. **Why**: business purpose and user value
3. **Constraint**: technical constraints and performance requirements
4. **Reference**: paths to related design documents (docs/blueprints/{NNN}-{feature-name}/, docs/database/)
5. **Acceptance**: completion conditions and verification methods

    BAD: "build a payment feature"

    GOOD:
    /feature-dev "Implement the payment processing module.
    - Support card payments and bank transfers
    - Integrate with the PG API (Inicis)
    - Auto-retry up to 3 times on payment failure
    - Follow the design in docs/blueprints/003-payment/blueprint.md
    - Reference the DB schema in docs/database/database-design.md
    - Write both unit and integration tests"
~~~

## Per-tech-stack custom rules (append to CLAUDE.md)

**Web frameworks:**
- **Spring Boot**: global exception handling with `@RestControllerAdvice`, input validation with `@Valid`, use Lombok
- **NestJS**: global exception handling with `ExceptionFilter`, DTO validation with `class-validator`, Prisma ORM
- **FastAPI**: use `HTTPException`, Pydantic model validation, SQLAlchemy ORM
- **Next.js**: App Router by default, Server Components first, leverage Server Actions
- **React**: functional components only, custom hook patterns
- **Vue 3**: Composition API by default, use `<script setup>`

**Mobile frameworks (only included when Step 0.5 = Mobile):**
- **React Native / Expo**: functional components + TypeScript required, Expo Router-based navigation, Zustand for state management, TanStack Query for server state, `kebab-case` file names, `StyleSheet.create()` or NativeWind, no inline styles, store sensitive data with `expo-secure-store`
- **Flutter**: Dart strict mode (`analysis_options.yaml`), feature-first directory layout, Riverpod/Bloc state management, GoRouter navigation, Freezed immutable models, `snake_case` file names, Theme.of(context) token reference required, no hardcoded colors/fonts, store sensitive data with `flutter_secure_storage`
- **Kotlin Multiplatform (KMP)**: business logic concentrated in the shared module, branch by platform via expect/actual, Compose Multiplatform UI, Koin DI, Ktor HTTP client, Kotlinx Serialization, SQLDelight local DB, `camelCase` functions/variables, `PascalCase` classes
