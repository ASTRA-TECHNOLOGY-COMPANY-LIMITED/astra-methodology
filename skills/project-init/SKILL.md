---
name: project-init
description: "ASTRA Sprint 0 project initial setup. Supports Web and Mobile (React Native, Flutter, KMP) platforms. Creates project directory structure, CLAUDE.md, design system templates, blueprint templates, and sprint templates."
argument-hint: "[project-name] [platform: web|mobile] [tech-stack]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Skill, Agent
---

# ASTRA Sprint 0: Project Initial Setup

You are an expert in Sprint 0 setup for the ASTRA (AI-augmented Sprint Through Rapid Assembly) methodology.
You configure the initial setup tailored to the user's project.

## Execution Procedure

### Step 0: Select Language

Use the `Skill` tool to invoke the `select-language` command. This command presents the trilingual prompt and returns the selected language in a structured format.

```
Skill tool invocation:
- skill: "select-language"
- args: ""   (empty — let the user choose interactively)
```

Parse the `## Selected Language` block from the command's output and extract:
- **Language Name** — used in CLAUDE.md `## Language` section and the result summary
- **Language Code** (`ko` / `vi` / `en`) — used internally for template selection
- **Locale** (`ko-KR` / `vi-VN` / `en-US`) — used for date/number formatting if needed

Store the selection and apply it to **all subsequent steps**. Every user-facing text, template content, and output message must use the selected language throughout the entire setup process.

The selected language will be persisted in the target project's CLAUDE.md (see Step 4, `## Language` section) so that all team members sharing the repository automatically use the same language in every Claude Code session.

> **Note**: If `$ARGUMENTS` to `/project-init` already includes an explicit language hint (e.g., `--lang=ko`), pass that value through to `select-language` as the argument (e.g., `Skill(skill: "select-language", args: "ko")`) to skip the interactive prompt.

### Step 0.5: Select Platform Type

> **MANDATORY**: This step MUST always be executed. You MUST use AskUserQuestion to ask the user and wait for their response before proceeding.

Use AskUserQuestion to ask the user which platform they are building for:

> **IMPORTANT**: The option text below is in English as a reference. You MUST translate all option text into the language selected in Step 0 before presenting to the user.

```
Select the project platform:

1. Web — web application development (React, Next.js, Vue, Spring Boot, NestJS, FastAPI, etc.)
2. Mobile — Android/iOS app development (React Native, Flutter, Kotlin Multiplatform, etc.)
```

Store the selected platform type (`web` or `mobile`). This selection determines the flow of all subsequent steps.

### Step 1: Gather Project Information

If user arguments are insufficient, use AskUserQuestion to confirm the following (ask in the selected language).

If `$ARGUMENTS` is provided, parse and extract as much information as possible, and only ask additional questions for missing information.

#### Step 1-A: Web Platform

If the user selected **Web** in Step 0.5, gather:

1. **Project name** (e.g., online-payment-system)
2. **Project description** (one-line summary)
3. **Backend tech stack** (e.g., Spring Boot 3, NestJS, FastAPI)
4. **Frontend tech stack** (e.g., Next.js 15, React, Vue 3)
5. **Database** (e.g., PostgreSQL 16, MySQL 8, MongoDB)
6. **Key modules** (e.g., member management, product management, orders, payments, notifications)
7. **Team composition** (number of VA, PE, DE, DSA members)

#### Step 1-B: Mobile Platform

If the user selected **Mobile** in Step 0.5, gather:

1. **Project name** (e.g., my-delivery-app)
2. **Project description** (one-line summary)
3. **Mobile framework**: Use AskUserQuestion with the following options:

> **IMPORTANT**: The option text below is in English as a reference. You MUST translate all option text into the language selected in Step 0 before presenting to the user.

```
Select the mobile framework:

1. React Native / Expo — JavaScript/TypeScript based, largest ecosystem (★ leverages web dev experience)
2. Flutter — Dart based, excellent custom UI performance (★ fastest growing)
3. Kotlin Multiplatform (KMP) — Kotlin based, native UI + shared business logic (★ officially backed by Google)
```

4. **Target platforms**: Use AskUserQuestion:

```
Select the target platforms:

1. Android + iOS (both)
2. Android only
3. iOS only
```

5. **Backend strategy**: Use AskUserQuestion:

```
Select the backend strategy:

1. Build a separate API server (Spring Boot, NestJS, FastAPI, etc.)
2. Use a BaaS (Firebase / Supabase)
3. Integrate with an existing API (an API server is already in operation)
```

- If **option 1** (separate API server): additionally ask **backend tech stack** and **database** (same as Web Step 1-A items 3, 5)
- If **option 2** (BaaS): ask which BaaS (`Firebase` or `Supabase`)
- If **option 3** (existing API): ask for the API base URL or spec document location

6. **Key modules** (e.g., authentication, push notifications, offline sync, chat, map/location)
7. **Team composition** (number of VA, PE, DE, DSA members)

### Step 2: Select Design System

> **MANDATORY**: This step MUST always be executed. Do NOT skip this step under any circumstances. You MUST use AskUserQuestion to ask the user and wait for their response before proceeding.

After gathering project info, use AskUserQuestion to ask the user which design system to use. Present framework-appropriate options based on the frontend tech stack gathered in Step 1.

> **IMPORTANT**: The option examples below are in English as a reference. You MUST translate all option text into the language selected in Step 0 before presenting to the user.

**For React / Next.js projects:**

```
Select a design system (common components will be auto-generated during project initialization):

1. shadcn/ui — Radix UI + Tailwind CSS, source-code-ownership model (★ most popular)
2. MUI (Material UI) — Google Material Design, largest component ecosystem
3. Ant Design — enterprise/admin focused, 60+ components
4. Mantine — 120+ components + 60+ hooks, excellent DX
5. Chakra UI — clean, highly accessible, composable components
6. Implement later (only generate design system templates)
```

**For Vue 3 projects:**

```
1. Ant Design Vue — Vue version of Ant Design, 100+ components
2. PrimeVue — 90+ components, multiple themes
3. Headless UI — official from Tailwind Labs, unstyled primitives
4. DaisyUI — Tailwind CSS plugin, framework-agnostic
5. Implement later (only generate design system templates)
```

**For React Native / Expo projects:**

```
1. Tamagui — RN + Web universal, optimized compiler
2. Gluestack UI — NativeBase successor, tree-shaking supported
3. NativeWind — Tailwind CSS for React Native
4. React Native Paper — Material Design 3 for RN, Google's official recommendation
5. Implement later (only generate design system templates)
```

**For Flutter projects:**

```
1. Material Design 3 — Flutter built-in, Google's official design system (★ most stable)
2. Cupertino (iOS-style) — iOS native look-and-feel, follows Apple HIG
3. Material + Cupertino adaptive — auto-switch per platform (Android=Material, iOS=Cupertino)
4. Implement later (only generate design system templates)
```

**For Kotlin Multiplatform (Compose Multiplatform) projects:**

```
1. Material Design 3 (Compose) — Compose Material3, Jetpack Compose default (★ recommended)
2. Implement later (only generate design system templates)
```

**For other frameworks or no frontend:**

```
1. DaisyUI — Tailwind CSS plugin, framework-agnostic
2. Implement later (only generate design system templates)
```

Store the user's selection. If the user chose a design system (not "Implement later"), it will be implemented in Step 5.

### Step 3: Create Project Directory Structure

Create the following structure in the current working directory (CWD).

#### Step 3 — Web Platform

If the user selected **Web** in Step 0.5:

```
{project-root}/
├── CLAUDE.md
├── .claude/
│   └── settings.json
│
├── docs/
│   ├── design-system/
│   │   ├── DESIGN.md              # SSoT (YAML Front Matter + Markdown Body) — generated by /design-init
│   │   ├── components.md          # Legacy detail reference — superseded by DESIGN.md §4
│   │   ├── layout-grid.md
│   │   └── references/
│   │       └── .gitkeep
│   │
│   ├── blueprints/
│   │   ├── overview.md
│   │   └── {NNN}-{feature-name}/    # e.g., 001-auth/
│   │       └── blueprint.md
│   │
│   ├── planner/
│   │   └── .gitkeep               # Planning deliverables (/service-planner)
│   │
│   ├── database/
│   │   ├── database-design.md
│   │   ├── naming-rules.md
│   │   └── migration/
│   │       └── .gitkeep
│   │
│   ├── tests/
│   │   ├── test-strategy.md
│   │   ├── test-cases/
│   │   │   └── sprint-1/
│   │   │       └── .gitkeep
│   │   └── test-reports/
│   │       └── .gitkeep
│   │
│   ├── sprints/
│   │   └── sprint-1/
│   │       └── .gitkeep
│   │
│   └── delivery/
│       └── .gitkeep
│
└── src/
    ├── styles/
    │   └── design-tokens.css
    └── .gitkeep
```

#### Step 3 — Mobile Platform

If the user selected **Mobile** in Step 0.5:

**For React Native / Expo projects:**

```
{project-root}/
├── CLAUDE.md
├── .claude/
│   └── settings.json
│
├── docs/
│   ├── design-system/
│   │   ├── DESIGN.md              # SSoT — generated by /design-init
│   │   ├── components.md          # Legacy detail reference
│   │   └── references/
│   │       └── .gitkeep
│   │
│   ├── blueprints/
│   │   ├── overview.md
│   │   └── {NNN}-{feature-name}/
│   │       └── blueprint.md
│   │
│   ├── planner/
│   │   └── .gitkeep
│   │
│   ├── database/               # If separate API server or BaaS
│   │   ├── database-design.md
│   │   ├── naming-rules.md
│   │   └── migration/
│   │       └── .gitkeep
│   │
│   ├── tests/
│   │   ├── test-strategy.md
│   │   ├── test-cases/
│   │   │   └── sprint-1/
│   │   │       └── .gitkeep
│   │   └── test-reports/
│   │       └── .gitkeep
│   │
│   ├── sprints/
│   │   └── sprint-1/
│   │       └── .gitkeep
│   │
│   └── delivery/
│       ├── android/
│       │   └── .gitkeep
│       └── ios/
│           └── .gitkeep
│
├── src/
│   ├── app/                    # Expo Router screens
│   │   └── .gitkeep
│   ├── components/             # Shared UI components
│   │   └── .gitkeep
│   ├── hooks/                  # Custom hooks
│   │   └── .gitkeep
│   ├── services/               # API clients, business logic
│   │   └── .gitkeep
│   ├── stores/                 # Zustand stores
│   │   └── .gitkeep
│   ├── styles/
│   │   └── design-tokens.ts    # Design tokens (TS for RN)
│   └── utils/
│       └── .gitkeep
│
└── assets/                     # Static assets (images, fonts)
    └── .gitkeep
```

**For Flutter projects:**

```
{project-root}/
├── CLAUDE.md
├── .claude/
│   └── settings.json
│
├── docs/
│   ├── design-system/
│   │   ├── DESIGN.md              # SSoT — generated by /design-init
│   │   ├── components.md          # Legacy detail reference
│   │   └── references/
│   │       └── .gitkeep
│   │
│   ├── blueprints/
│   │   ├── overview.md
│   │   └── {NNN}-{feature-name}/
│   │       └── blueprint.md
│   │
│   ├── planner/
│   │   └── .gitkeep
│   │
│   ├── database/
│   │   ├── database-design.md
│   │   ├── naming-rules.md
│   │   └── migration/
│   │       └── .gitkeep
│   │
│   ├── tests/
│   │   ├── test-strategy.md
│   │   ├── test-cases/
│   │   │   └── sprint-1/
│   │   │       └── .gitkeep
│   │   └── test-reports/
│   │       └── .gitkeep
│   │
│   ├── sprints/
│   │   └── sprint-1/
│   │       └── .gitkeep
│   │
│   └── delivery/
│       ├── android/
│       │   └── .gitkeep
│       └── ios/
│           └── .gitkeep
│
├── lib/                        # Flutter source code
│   ├── app/                    # App configuration, routes
│   │   └── .gitkeep
│   ├── features/               # Feature modules
│   │   └── .gitkeep
│   ├── shared/                 # Shared widgets, utils
│   │   ├── widgets/
│   │   │   └── .gitkeep
│   │   └── theme/
│   │       └── design_tokens.dart  # Design tokens (Dart)
│   ├── services/               # API clients, repositories
│   │   └── .gitkeep
│   └── main.dart               # Entry point (created in Step 3-B)
│
├── test/                       # Unit & widget tests
│   └── .gitkeep
│
└── assets/                     # Static assets (images, fonts)
    └── .gitkeep
```

**For Kotlin Multiplatform (KMP) projects:**

```
{project-root}/
├── CLAUDE.md
├── .claude/
│   └── settings.json
│
├── docs/
│   ├── design-system/
│   │   ├── DESIGN.md              # SSoT — generated by /design-init
│   │   ├── components.md          # Legacy detail reference
│   │   └── references/
│   │       └── .gitkeep
│   │
│   ├── blueprints/
│   │   ├── overview.md
│   │   └── {NNN}-{feature-name}/
│   │       └── blueprint.md
│   │
│   ├── planner/
│   │   └── .gitkeep
│   │
│   ├── database/
│   │   ├── database-design.md
│   │   ├── naming-rules.md
│   │   └── migration/
│   │       └── .gitkeep
│   │
│   ├── tests/
│   │   ├── test-strategy.md
│   │   ├── test-cases/
│   │   │   └── sprint-1/
│   │   │       └── .gitkeep
│   │   └── test-reports/
│   │       └── .gitkeep
│   │
│   ├── sprints/
│   │   └── sprint-1/
│   │       └── .gitkeep
│   │
│   └── delivery/
│       ├── android/
│       │   └── .gitkeep
│       └── ios/
│           └── .gitkeep
│
├── shared/                     # KMP shared module
│   └── src/
│       ├── commonMain/         # Shared business logic
│       │   └── kotlin/
│       │       └── .gitkeep
│       ├── androidMain/        # Android-specific implementations
│       │   └── kotlin/
│       │       └── .gitkeep
│       └── iosMain/            # iOS-specific implementations
│           └── kotlin/
│               └── .gitkeep
│
├── composeApp/                 # Compose Multiplatform UI
│   └── src/
│       ├── commonMain/
│       │   └── kotlin/
│       │       ├── theme/
│       │       │   └── DesignTokens.kt  # Design tokens (Kotlin)
│       │       └── .gitkeep
│       ├── androidMain/
│       │   └── kotlin/
│       │       └── .gitkeep
│       └── iosMain/
│           └── kotlin/
│               └── .gitkeep
│
└── assets/
    └── .gitkeep
```

> **Note**: If the user selected "existing API integration" (backend strategy option 3), omit the `docs/database/` directory entirely. If the user selected BaaS, create `docs/database/` but adjust `database-design.md` to document Firestore collections or Supabase tables instead of traditional SQL schemas.

### Step 3-B: Create Project Scaffolding

Based on the tech stack gathered in Step 1, create the basic project management files. This step ensures the project is immediately runnable after setup.

**For Node.js-based projects (Next.js, React, Vue, NestJS, Express):**
- `package.json` — project name, version, scripts (dev, build, start, lint, test), dependencies based on selected tech stack and design system
- `tsconfig.json` — TypeScript configuration (if TypeScript is used)
- `.gitignore` — Node.js standard ignores (node_modules, .next, dist, .env, etc.)
- `.env.example` — environment variable template with placeholder values
- `.prettierrc` — Prettier configuration aligned with coding conventions
- `.eslintrc.json` or `eslint.config.mjs` — ESLint configuration for the tech stack
- Run `npm install` (or the appropriate package manager) to install dependencies

**For React Native / Expo projects:**
- `package.json` — with expo, react-native, and selected design system dependencies
- `tsconfig.json` — React Native TypeScript config
- `app.json` or `app.config.ts` — Expo configuration (includes app name, slug, target platforms from Step 1-B)
- `babel.config.js` — Babel configuration for React Native
- `eas.json` — EAS Build configuration for Android/iOS builds
- `.gitignore` — React Native standard ignores (node_modules, .expo, android/, ios/, *.jks, *.keystore)
- `.env.example` — environment variable template (API_BASE_URL, etc.)
- Run `npx create-expo-app . --template blank-typescript` or `npx expo install` for dependencies

**For Flutter projects:**
- `pubspec.yaml` — project metadata, dependencies (flutter, provider/riverpod/bloc for state management, dio for HTTP, go_router for routing, freezed for code generation, selected design system packages)
- `analysis_options.yaml` — Dart lint rules (flutter_lints)
- `lib/main.dart` — Flutter app entry point with MaterialApp/CupertinoApp and router setup
- `lib/shared/theme/design_tokens.dart` — Design tokens as Dart constants
- `.gitignore` — Flutter standard ignores (.dart_tool, build/, .flutter-plugins, *.iml)
- `.env.example` — environment variable template
- Run `flutter create . --org {org-domain} --project-name {project-name}` if not already a Flutter project, then `flutter pub get`

**For Kotlin Multiplatform (KMP) projects:**
- `build.gradle.kts` (root) — Kotlin Multiplatform plugin configuration, Compose Multiplatform plugin
- `shared/build.gradle.kts` — shared module dependencies (Ktor for HTTP, Kotlinx Serialization, Koin for DI, SQLDelight for local DB)
- `composeApp/build.gradle.kts` — Compose Multiplatform UI module, Material3 dependencies
- `gradle.properties` — Kotlin/JVM/Android configuration
- `settings.gradle.kts` — module include configuration
- `.gitignore` — Kotlin/Gradle standard ignores (.gradle, build/, .idea/, *.iml, local.properties)
- `.env.example` — environment variable template
- Use the Kotlin Multiplatform Wizard template or `kmp-app-template` if available, then run `./gradlew build`

**For Spring Boot projects (Java/Kotlin):**
- `build.gradle` (Gradle) or `pom.xml` (Maven) — project coordinates, dependencies (Spring Web, Spring Data JPA, selected DB driver, Lombok, etc.)
- `application.yml` — default configuration template with DB, server port, logging settings
- `src/main/java/{package}/Application.java` — main application entry point
- `src/main/resources/application.yml` — configuration placeholder
- `.gitignore` — Java/Gradle/Maven standard ignores
- `.env.example` — environment variable template

**For FastAPI projects (Python):**
- `pyproject.toml` — project metadata, dependencies (fastapi, uvicorn, sqlalchemy, alembic, etc.) — primary dependency definition file
- `requirements.txt` — generated from pyproject.toml for deployment compatibility (`pip freeze` format). Both files are created; `pyproject.toml` is the source of truth.
- `.gitignore` — Python standard ignores (__pycache__, .venv, .env, etc.)
- `.env.example` — environment variable template
- `src/main.py` — FastAPI application entry point skeleton

**Design system dependencies**: If a design system was selected in Step 2, include its required packages in the dependency file:
| Design System | Key Dependencies |
|--------------|-----------------|
| shadcn/ui | `tailwindcss`, `@radix-ui/*`, `class-variance-authority`, `clsx`, `tailwind-merge`, `lucide-react` |
| MUI | `@mui/material`, `@mui/icons-material`, `@emotion/react`, `@emotion/styled` |
| Ant Design | `antd`, `@ant-design/icons` |
| Mantine | `@mantine/core`, `@mantine/hooks`, `@mantine/form`, `@mantine/notifications` |
| Chakra UI | `@chakra-ui/react`, `@emotion/react`, `@emotion/styled`, `framer-motion` |
| Ant Design Vue | `ant-design-vue`, `@ant-design/icons-vue` |
| PrimeVue | `primevue`, `primeicons`, `@primevue/themes` |
| Headless UI | `@headlessui/vue`, `tailwindcss` |
| DaisyUI | `tailwindcss`, `daisyui` |
| Tamagui | `tamagui`, `@tamagui/core`, `@tamagui/config` |
| Gluestack UI | `@gluestack-ui/themed`, `@gluestack-style/react` |
| NativeWind | `nativewind`, `tailwindcss` |
| React Native Paper | `react-native-paper`, `react-native-vector-icons` |
| Material Design 3 (Flutter) | `flutter` built-in (no extra pub dependency) |
| Cupertino (Flutter) | `flutter` built-in (no extra pub dependency) |
| Material + Cupertino Adaptive (Flutter) | `flutter_adaptive_scaffold`, `flutter_platform_widgets` |
| Material Design 3 (Compose/KMP) | `compose.material3` (Compose Multiplatform BOM) |

> **Important**:
> - Before running any install command (`npm install`, `npx expo install`, etc.), verify that the CWD is the project root directory where `package.json` was created. Use `cd {project-root}` explicitly.
> - If the install command fails (e.g., Node.js not installed, network unavailable), display the error to the user and continue with the remaining steps. Do not block the entire setup process.
> - Adapt all configuration files to the specific versions and conventions of the selected tech stack. Use the latest stable versions of all dependencies. If the project uses a monorepo structure, adjust accordingly.

### Step 4: Create CLAUDE.md

> **IMPORTANT**: The template below is written in English as a reference. If the user selected Korean or Vietnamese in Step 0, you MUST translate ALL text in the template (section headers, table contents, descriptions, workflow diagrams, rules, guides) into the selected language BEFORE writing the file. Only technical identifiers (tool names, file paths, command names) remain untranslated.

Customize the template below according to the project information and generate it:

```markdown
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
| **I**nstant Feedback Loop | Shorten feedback cycles to the hour | `chrome-devtools` MCP, `code-review` |
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
| Design token compliance | `chrome-devtools` + `design-token-validator` agent |
| Component consistency | Per-screen comparison |
| Responsive layout | `chrome-devtools` viewport switching |
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
- Auto-generate E2E scenarios with `/test-scenario`; run Chrome MCP integration tests with `/test-run`
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
| Slack → blueprint + sprint | `/slack-import [channel]` |
| Extract Slack backlog | `/extract-backlog [channel]` |
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
```

**Per-tech-stack custom rules:**

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

### Step 5: Create Design System Templates & Implement Components

#### Step 5-A: Create design system files

Create the design system SSoT and supporting documents.

**`docs/design-system/DESIGN.md`** (NEW — SSoT as of plugin v5.2.0):

This is the **single source of truth** for the project's design system. It bundles YAML Front Matter (machine-readable tokens) with Markdown Body (design philosophy, persona, component guidelines, anti-AI aesthetic rules). All other design assets (`src/styles/design-tokens.css`, `docs/design-system/components.md`) reference or are generated from this file.

Invoke the `/design-init --auto` skill to generate DESIGN.md with the project context:

```
Skill("astra-methodology:design-init", args="--auto")
```

This populates DESIGN.md from the bundled template (`skills/project-init/templates/DESIGN.md`) with defaults: Blue primary, Geist+Pretendard typography, Comfortable density, Calm tone. `/design-init` then automatically generates `src/styles/design-tokens.css` from DESIGN.md Front Matter.

**For Web projects:**

**`src/styles/design-tokens.css`** (GENERATED — do not hand-edit): 3-tier design token set (Primitive → Semantic → Component) auto-generated by `/design-init` from DESIGN.md Front Matter. OKLCH color space, Geist Sans + Pretendard Korean font stack, fluid typography with clamp(), 4px base grid spacing, spring-based animation easings, reduced-motion support, and dark mode via semantic token overrides. Header carries a `AUTO-GENERATED from DESIGN.md` warning. This is a source file consumed by components via `@import`, so it belongs in `src/styles/`, NOT in `docs/`. Regenerate via `/design-init --regenerate-css` whenever DESIGN.md changes.

**`docs/design-system/components.md`**: Core component style guide (13 components: buttons, inputs, cards, modals, tables, navigation, toasts, badges, skeleton loading, avatar, sheet/drawer, command palette, toggle). All values reference Semantic or Component tokens only — never Primitive tokens directly. Includes transition/animation guidance per component.

**`docs/design-system/layout-grid.md`**: Layout grid system with 5-tier breakpoints (xs~2xl), CSS Grid/Subgrid patterns, Container Queries for component-level responsiveness, fluid spacing with clamp()

**For Mobile projects:**

> **IMPORTANT**: When creating design tokens and components for mobile projects, you MUST read and follow the mobile design guide at `$CLAUDE_PLUGIN_ROOT/docs/ux/mobile-design-guide.md`. This guide contains platform-specific guidelines (Apple HIG, Material Design 3), touch interaction patterns, typography scales, color system & dark mode principles, haptic feedback mapping, animation timing, accessibility requirements, and expert-level polish tips. All design decisions below should align with this guide.

Create the design token source file in the framework-appropriate location:

- **React Native**: `src/styles/design-tokens.ts` — TypeScript object with colors, typography, spacing, shadows as constants. Export typed theme object. Follow the token hierarchy (Reference → Semantic → Component) from the mobile design guide.
- **Flutter**: `lib/shared/theme/design_tokens.dart` — Dart class with static const values for ColorScheme, TextTheme, spacing. Includes `lightTheme()` and `darkTheme()` factory methods. Follow the token hierarchy from the mobile design guide.
- **KMP**: `composeApp/src/commonMain/kotlin/theme/DesignTokens.kt` — Kotlin object with Material3 ColorScheme, Typography, spacing values. Follow the token hierarchy from the mobile design guide.

**`docs/design-system/components.md`**: Core component style guide template adapted for mobile (buttons, text inputs, bottom sheet, bottom navigation, list items, cards, dialogs/alerts, snackbar/toast, avatar, loading indicators). Reference the mobile design guide's Section 14 ("Expert Know-How") for polish-level quality standards.

#### Step 5-B: Implement Design System Components (if a design system was selected)

If the user selected a design system in Step 2 (not "Implement later"), invoke the `/frontend-design` skill to implement the following **common base components**. Pass the selected design system, tech stack, and design tokens as context.

> **IMPORTANT**: The prompt below is written in English as a reference. You MUST translate the entire prompt into the language selected in Step 0 BEFORE invoking the frontend-design skill.

**For Web projects**, use the Skill tool to invoke `frontend-design` with a prompt like:

```
"Implement the design system common components for project {project-name}.

- Design system: {selected-design-system}
- Frontend: {frontend-tech-stack}
- **Design system SSoT**: docs/design-system/DESIGN.md (YAML Front Matter + Markdown Body — unifies tokens, persona, anti-AI aesthetic rules)
- Design tokens CSS: src/styles/design-tokens.css (artifact auto-generated from DESIGN.md — do not hand-edit)
- Component guide: docs/design-system/DESIGN.md §4 (legacy: docs/design-system/components.md)
- Layout guide: see docs/design-system/layout-grid.md

Implement the following common components:
1. Button — Primary/Secondary/Danger/Ghost/Outline variants, sm/md/lg sizes, loading/disabled states
2. Input — text input, label, error state, helper text, disabled state
3. Card — Default/Elevated/Outlined/Interactive/Ghost variants, Container Query responsive
4. Modal/Dialog — header/body/footer structure, backdrop, sm/md/lg/full sizes, Spring animation
5. Toast — Success/Warning/Error/Info variants, Spring entry animation, auto-dismiss
6. Badge — status badges, category tags, sm/md/lg sizes, dot indicator
7. Table — sorting, hover, sticky header, responsive (mobile card switch)
8. Dropdown/Select — option list, search, multi-select, Command Palette style
9. Tabs — animated indicator, active/inactive states
10. Sidebar Layout — collapse/expand, Spring transition animation, active menu highlight
11. Skeleton — text/avatar/card/table shimmer patterns
12. Avatar — image/initials/icon, xs~xl sizes, online indicator, group stacking
13. Toggle/Switch — sm/md sizes, Spring bounce transition

All components must:
- Reference Semantic/Component tokens only (no direct Primitive references)
- Support OKLCH-based dark mode
- Be responsive + Container Query compatible
- Follow accessibility (ARIA, focus ring, keyboard navigation)
- Use Spring easing (--ease-spring-*) + prefers-reduced-motion handling
- Follow the project's coding conventions
- Also generate a design system preview page (where every component can be verified in light/dark mode)"
```

**For Mobile projects**, use the Skill tool to invoke `frontend-design` with a prompt adapted to the mobile framework:

```
"Implement the mobile design system common components for project {project-name}.

- Design system: {selected-design-system}
- Mobile framework: {mobile-framework}
- **Design system SSoT**: docs/design-system/DESIGN.md (YAML Front Matter + Markdown Body)
- Design tokens: {token-file-path} (artifact auto-generated from DESIGN.md)
- Component guide: docs/design-system/DESIGN.md §4 (legacy: docs/design-system/components.md)
- Mobile design guide: see $CLAUDE_PLUGIN_ROOT/docs/ux/mobile-design-guide.md (platform guidelines, touch interactions, animation timing, haptic feedback, accessibility criteria)

Implement the following common components:
1. Button — Primary/Secondary/Danger/Ghost variants, sm/md/lg sizes, loading/disabled states, haptic feedback
2. TextInput — text input, label, error state, helper text, disabled state, keyboard-type support
3. Card — Default/Elevated/Outlined/Pressable variants
4. BottomSheet — snap points, drag handle, backdrop, size variants
5. Toast/Snackbar — Success/Warning/Error/Info variants, auto-dismiss, swipe-to-dismiss
6. Badge — status badges, notification counts, sm/md sizes
7. ListItem — leading icon, title/subtitle, trailing accessory, swipe actions
8. BottomNavigation — tab icon + label, active indicator, badge support
9. Avatar — image/initials/icon, sm/md/lg/xl sizes, online status indicator
10. LoadingIndicator — Spinner/Skeleton/Shimmer variants, full-screen overlay
11. Dialog/Alert — title/message/action buttons, confirm/cancel pattern
12. SearchBar — search icon, clear button, cancel button, autocomplete support

All components must:
- Use design tokens (theme system)
- Support dark mode (linked to system setting)
- Provide a minimum touch area of 44×44dp
- Follow accessibility (screen reader labels, focus management)
- Follow the project's coding conventions
- Also generate a design system preview screen (Storybook or an in-app preview screen)"
```

> **Token file paths by framework:**
> - React Native: `src/styles/design-tokens.ts`
> - Flutter: `lib/shared/theme/design_tokens.dart`
> - KMP: `composeApp/src/commonMain/kotlin/theme/DesignTokens.kt`

If the user chose to implement later, skip Step 5-B entirely. Only the design system documentation templates (Step 5-A) are created.

### Step 6: Create Blueprint Template

**docs/blueprints/overview.md**: Project overview document (vision, goals, module structure, tech stack decision rationale)

> **Blueprint Directory Convention**: Individual feature blueprints are organized as numbered directories under `docs/blueprints/`. Each directory uses the format `{NNN}-{feature-name}/` (e.g., `001-auth/`, `002-payment/`) and contains `blueprint.md` as the main design document along with any related supplementary files (diagrams, API specs, etc.).

### Step 7: Create Database Document Templates

**docs/database/database-design.md**: Central DB design document template (full ERD, common rules, module-specific tables, FK relationship summary)

**docs/database/naming-rules.md**: DB naming rules and standard terminology mapping document (table prefixes, column naming, standard terminology dictionary integration)

### Step 8: Create Test Document Template

**docs/tests/test-strategy.md**: Test strategy document (test level definitions, coverage goals, test environments, naming conventions, automation scope)

### Step 9: Create Sprint Template

**docs/sprints/sprint-1/prompt-map.md**: First sprint prompt map template

**docs/sprints/sprint-1/progress.md**: First sprint progress tracker (template format with placeholder features — features will be populated when the sprint is actually planned)

### Step 10: Create Project Configuration File

**.claude/settings.json**: Project-specific Claude Code settings

### Step 11: Output Result Summary

After all files are created, output the following summary.

> **IMPORTANT**: The output block below is in English as a reference. You MUST translate it into the language selected in Step 0 before presenting to the user.

```
## ASTRA Sprint 0 Initial Setup Complete

### Generated File List
- CLAUDE.md (project AI rules)
- .claude/settings.json (project settings)
- package.json / build.gradle / pubspec.yaml / pyproject.toml (project dependencies & scripts)
- tsconfig.json / .eslintrc / .prettierrc / analysis_options.yaml (dev tooling configs)
- .gitignore, .env.example (project essentials)
- {design-token-file} (design tokens — source code)
- docs/design-system/ (design system documentation)
- docs/blueprints/ (design document templates)
- docs/database/ (DB design documents, naming rules, migrations — if applicable)
- docs/tests/ (test strategy, test cases, test reports)
- docs/sprints/ (sprint prompt maps, progress trackers, retrospectives)
- docs/delivery/ (for release artifacts)
- {components-directory} (common UI components — if design system was selected)

### Platform & Architecture
- Platform: {Web or Mobile}
{when Mobile: Framework: {React Native/Flutter/KMP}, Target: {Android/iOS/Both}, Backend: {strategy}}

### Design System
- Selected: {design-system-name} (or "Implement later")
- **Web**: Common components: Button, Input, Card, Modal, Toast, Badge, Table, Dropdown, Tabs, Sidebar Layout
- **Mobile**: Common components: Button, TextInput, Card, BottomSheet, Toast, Badge, ListItem, BottomNavigation, Avatar, LoadingIndicator, Dialog, SearchBar
- Preview: {preview-page-path} (if design system was selected)

### Next Steps (Sprint 0 progress)
1. [ ] Review CLAUDE.md and customize for the project
2. [ ] Verify design system preview page and adjust design tokens with DSA
3. [ ] Verify global dev environment with /astra-setup
4. [ ] Generate core feature design documents with /feature-dev
5. [ ] Write docs/database/database-design.md
6. [ ] Review docs/database/naming-rules.md
7. [ ] Write docs/tests/test-strategy.md
8. [ ] Set up hookify rules
9. [ ] Verify Sprint 0 completion with /project-checklist
```

## Notes

- Existing files are **not overwritten**. If existing files are found, confirm with the user.
- .gitkeep files are created only to maintain empty directories.
- CLAUDE.md rules are automatically adjusted based on the tech stack.
- All text is written in the language selected in Step 0 (except code comments and technical identifiers).
