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

> **IMPORTANT**: The option text below is in Korean. You MUST translate all option text into the language selected in Step 0 before presenting to the user.

```
프로젝트 플랫폼을 선택해 주세요:

1. 웹 (Web) — 웹 애플리케이션 개발 (React, Next.js, Vue, Spring Boot, NestJS, FastAPI 등)
2. 모바일 (Mobile) — Android/iOS 앱 개발 (React Native, Flutter, Kotlin Multiplatform 등)
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

> **IMPORTANT**: The option text below is in Korean. You MUST translate all option text into the language selected in Step 0 before presenting to the user.

```
모바일 프레임워크를 선택해 주세요:

1. React Native / Expo — JavaScript/TypeScript 기반, 가장 큰 생태계 (★ 웹 개발 경험 활용)
2. Flutter — Dart 기반, 뛰어난 커스텀 UI 성능 (★ 가장 빠르게 성장)
3. Kotlin Multiplatform (KMP) — Kotlin 기반, 네이티브 UI + 공유 비즈니스 로직 (★ Google 공식 지지)
```

4. **Target platforms**: Use AskUserQuestion:

```
타겟 플랫폼을 선택해 주세요:

1. Android + iOS (둘 다)
2. Android만
3. iOS만
```

5. **Backend strategy**: Use AskUserQuestion:

```
백엔드 전략을 선택해 주세요:

1. 별도 API 서버 구축 (Spring Boot, NestJS, FastAPI 등)
2. BaaS 사용 (Firebase / Supabase)
3. 기존 API 연동 (이미 운영 중인 API 서버가 있음)
```

- If **option 1** (separate API server): additionally ask **backend tech stack** and **database** (same as Web Step 1-A items 3, 5)
- If **option 2** (BaaS): ask which BaaS (`Firebase` or `Supabase`)
- If **option 3** (existing API): ask for the API base URL or spec document location

6. **Key modules** (e.g., authentication, push notifications, offline sync, chat, map/location)
7. **Team composition** (number of VA, PE, DE, DSA members)

### Step 2: Select Design System

> **MANDATORY**: This step MUST always be executed. Do NOT skip this step under any circumstances. You MUST use AskUserQuestion to ask the user and wait for their response before proceeding.

After gathering project info, use AskUserQuestion to ask the user which design system to use. Present framework-appropriate options based on the frontend tech stack gathered in Step 1.

> **IMPORTANT**: The option examples below are in Korean. You MUST translate all option text into the language selected in Step 0 before presenting to the user.

**For React / Next.js projects:**

```
디자인 시스템을 선택해 주세요 (프로젝트 초기 설정 시 공통 컴포넌트가 자동 생성됩니다):

1. shadcn/ui — Radix UI + Tailwind CSS 기반, 소스 코드 소유 방식 (★ 가장 인기)
2. MUI (Material UI) — Google Material Design, 가장 큰 컴포넌트 생태계
3. Ant Design — 엔터프라이즈/어드민 특화, 60+ 컴포넌트
4. Mantine — 120+ 컴포넌트 + 60+ 훅, 뛰어난 DX
5. Chakra UI — 깔끔하고 접근성 높은 컴포저블 컴포넌트
6. 추후 직접 구현 (디자인 시스템 템플릿만 생성)
```

**For Vue 3 projects:**

```
1. Ant Design Vue — Ant Design의 Vue 버전, 100+ 컴포넌트
2. PrimeVue — 90+ 컴포넌트, 다양한 테마
3. Headless UI — Tailwind Labs 공식, 비스타일드 프리미티브
4. DaisyUI — Tailwind CSS 플러그인, 프레임워크 무관
5. 추후 직접 구현 (디자인 시스템 템플릿만 생성)
```

**For React Native / Expo projects:**

```
1. Tamagui — RN + Web 유니버설, 최적화 컴파일러
2. Gluestack UI — NativeBase 후속, 트리쉐이킹 지원
3. NativeWind — Tailwind CSS for React Native
4. React Native Paper — Material Design 3 for RN, Google 공식 권장
5. 추후 직접 구현 (디자인 시스템 템플릿만 생성)
```

**For Flutter projects:**

```
1. Material Design 3 — Flutter 기본 내장, Google 공식 디자인 시스템 (★ 가장 안정적)
2. Cupertino (iOS-style) — iOS 네이티브 룩앤필, Apple HIG 준수
3. Material + Cupertino 적응형 — 플랫폼별 자동 전환 (Android=Material, iOS=Cupertino)
4. 추후 직접 구현 (디자인 시스템 템플릿만 생성)
```

**For Kotlin Multiplatform (Compose Multiplatform) projects:**

```
1. Material Design 3 (Compose) — Compose Material3, Jetpack Compose 기본 (★ 권장)
2. 추후 직접 구현 (디자인 시스템 템플릿만 생성)
```

**For other frameworks or no frontend:**

```
1. DaisyUI — Tailwind CSS 플러그인, 프레임워크 무관
2. 추후 직접 구현 (디자인 시스템 템플릿만 생성)
```

Store the user's selection. If the user chose a design system (not "추후 직접 구현"), it will be implemented in Step 5.

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
│   │   ├── components.md
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
│   │   ├── components.md
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
│   │   ├── components.md
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
│   │   ├── components.md
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

> **IMPORTANT**: The template below is written in Korean as a reference. If the user selected Vietnamese or English in Step 0, you MUST translate ALL Korean text in the template (section headers, table contents, descriptions, workflow diagrams, rules, guides) into the selected language BEFORE writing the file. Only technical identifiers (tool names, file paths, command names) remain untranslated.

Customize the template below according to the project information and generate it:

```markdown
# Project: {project-name}

> {project description}

## Language

- **프로젝트 언어**: {selected language name} ({selected language code})
- 모든 Claude 응답, 생성 문서, 템플릿 콘텐츠는 위 언어로 작성되어야 합니다.
- 기술 식별자(도구명, 파일 경로, 명령어명, 코드 주석)는 원래 언어를 유지합니다.

## Architecture

**For Web projects (Step 0.5 = Web):**

- Backend: {backend tech stack}
- Frontend: {frontend tech stack}
- Database: {DB type}

**For Mobile projects (Step 0.5 = Mobile):**

- Platform: Mobile ({target platforms: Android/iOS/Both})
- Framework: {mobile framework} (e.g., React Native/Expo, Flutter, Kotlin Multiplatform)
- Backend Strategy: {backend strategy} (e.g., 별도 API 서버 / Firebase / Supabase / 기존 API 연동)
- Backend: {backend tech stack, if applicable}
- Database: {DB type, if applicable}

## Key Modules
{list modules as bullet points}

## ASTRA Methodology

이 프로젝트는 **ASTRA (AI-augmented Sprint Through Rapid Assembly)** 방법론을 따릅니다.

### VIP 원칙
| 원칙 | 핵심 | 실현 도구 |
|------|------|----------|
| **V**ibe-driven Development | 코드를 작성하지 말고, 의도를 전달하라 | `feature-dev`, `frontend-design` |
| **I**nstant Feedback Loop | 피드백 주기를 시간 단위로 단축 | `chrome-devtools` MCP, `code-review` |
| **P**lugin-powered Quality | 품질은 코드에 내장되는 것이다 | `astra-methodology`, `security-guidance`, `hookify` |

### 스프린트 주기
- **1주 단위** 스프린트 (소규모 증분, 빠른 피드백)
- AI가 개발+테스트+리뷰를 병렬 처리하여 짧은 주기로 민첩성 향상

### 팀 역할
| 역할 | 담당 | 주요 활동 |
|------|------|----------|
| **VA** (Vibe Architect) | 시니어 개발자 1명 | 스프린트 관리, AI 워크플로우 설계, 아키텍처 의사결정, 품질 게이트 판단 |
| **PE** (Prompt Engineer) | 주니어 개발자 1~2명 | 프롬프트 작성, AI 결과물 검증, 설계 문서 보완 |
| **DE** (Domain Expert) | 고객사 현업 1명 | 요구사항 전달, 백로그 우선순위, 실시간 피드백, 인수 검증 |
| **DSA** (Design System Architect) | 디자이너 1명 | 디자인 시스템 구축, AI 생성 UI 검수, 디자인 토큰 관리 |

## Development Workflow

```
[기능 스프린트]
블루프린트 작성 → DB 설계 → 스프린트 작성 → 구현 → 테스트 시나리오 → 테스트 실행 → PR/리뷰
                                                                                          ↓
                                    메인 브랜치 머지 ← 사용자 테스트 ← 스테이징 머지 ←──────┘
```

### 단계별 참조 문서
| 단계 | 참조 경로 | 주요 도구 |
|------|----------|----------|
| 서비스 기획 | `docs/planner/{NNN}-{feature-name}/` | `/service-planner` |
| 디자인 시스템 | `src/styles/design-tokens.css`, `docs/design-system/` | `/frontend-design` |
| 블루프린트 작성 | `docs/blueprints/{NNN}-{feature-name}/` | `/feature-dev` (아직 코드는 수정하지 마) |
| DB 설계 | `docs/database/database-design.md` | `/feature-dev`, `/lookup-term` |
| 스프린트 계획 | `docs/sprints/sprint-N/prompt-map.md` | `/sprint-plan` |
| 구현 | `src/` | `/feature-dev` (블루프린트+DB 설계 기반) |
| 테스트 시나리오 | `docs/tests/test-cases/sprint-N/` | `/test-scenario` |
| 테스트 실행 | `docs/tests/test-reports/` | `/test-run` |
| PR/리뷰 | - | `/pr-merge`, `/code-review` |

## Quality Gates

### Gate 1: WRITE-TIME (자동 적용 — 코드 작성 시)
| 도구 | 검사 내용 | 동작 |
|------|----------|------|
| `security-guidance` | 9개 보안 패턴 (eval, innerHTML 등) | PreToolUse 훅, **차단** |
| `astra-methodology` | 금칙어 + 네이밍 규칙 | PostToolUse 훅, 경고 |
| `hookify` | 프로젝트별 커스텀 규칙 | PreToolUse/PostToolUse 훅 |
| `coding-convention` 스킬 | Java/TS/RN/Python/CSS/SCSS 컨벤션 | 자동 감지 적용 |
| `data-standard` 스킬 | 공공 데이터 표준 용어 사전 | DB 코드 시 자동 감지 |
| `code-standard` 스킬 | ISO 3166-1/2, ITU-T E.164 | 전화번호/국가/주소 시 자동 감지 |

### Gate 2: REVIEW-TIME (PR/리뷰 시)
| 도구 | 검사 내용 |
|------|----------|
| `feature-dev` (내장 code-reviewer) | 코드 품질/버그/컨벤션 (3개 병렬 에이전트) |
| `/code-review` | CLAUDE.md 준수, 버그, 이력 분석 (80점+ 필터링) |
| `blueprint-reviewer` 에이전트 | 설계 문서 품질/일관성 검증 |
| `test-coverage-analyzer` 에이전트 | 테스트 전략/커버리지 분석 |
| `convention-validator` 에이전트 | 코딩 컨벤션 검증 |

### Gate 2.5: DESIGN-TIME (DSA 디자인 검수)
| 검수 항목 | 확인 방법 |
|----------|----------|
| 디자인 토큰 준수 | `chrome-devtools` + `design-token-validator` 에이전트 |
| 컴포넌트 일관성 | 화면별 비교 |
| 반응형 레이아웃 | `chrome-devtools` 뷰포트 전환 |
| 접근성 기본 확인 | 컬러 대비, 포커스 확인 |

### Gate 3: BRIDGE-TIME (릴리스 시 최종 품질 게이트)
- `quality-gate-runner` 에이전트가 Gate 1~3 통합 실행
- convention/naming 위반 0건, 콘솔 에러 0건 필수

### 품질 게이트 통과 기준 요약
| 게이트 | 통과 기준 | 차단 시 조치 |
|--------|----------|-------------|
| Gate 1 | security-guidance 경고 0건, 금칙어 0건 | 즉시 수정 후 재작성 |
| Gate 2 | code-review 고신뢰 이슈 0건, 커버리지 70%+ | fix now / fix later 결정 |
| Gate 2.5 | DSA 디자인 검수 승인 | 프롬프트 수정 → 재생성 → 재검수 |
| Gate 3 | convention/naming 위반 0건, 콘솔 에러 0건 | 일괄 수정 후 배포 |

## Coding Rules
- 모든 API 엔드포인트에 인증 미들웨어 필수
- DB 스키마는 docs/database/database-design.md를 단일 진실 원천(SSoT)으로 관리
- DB 엔티티는 공공 데이터 표준 용어 사전을 준수할 것 (`/lookup-term` 활용)
- 테이블명 접두사: TB_ (일반), TC_ (코드), TH_ (이력), TL_ (로그), TR_ (관계)
- REST API 응답 형식: `{ success: boolean, data: T, error?: string }`
- 에러 처리: 비즈니스 예외와 시스템 예외를 구분할 것
- 언어별 코딩 컨벤션은 `coding-convention` 스킬이 자동 적용 (Java/TypeScript/React Native/Python/CSS/SCSS)
- `/check-convention src/` 으로 컨벤션 준수 여부를 수동 검사 가능

## Design Rules (DSA 정의)

**웹 프로젝트:**
- 디자인 토큰: src/styles/design-tokens.css를 반드시 참조할 것 (3-tier: Primitive → Semantic → Component)
- 컬러: OKLCH 색상 공간 기반, Semantic 토큰 (--surface-*, --text-*, --action-*, --status-*) 사용 필수, Primitive 직접 참조 금지
- 폰트: Geist Sans + Pretendard(한글) 기본, 크기는 Fluid 토큰 (--fluid-*) 또는 Static 토큰 (--text-*) 사용 필수
- 스페이싱: 4px 베이스 그리드, 토큰 스케일 (--space-*) 또는 Fluid (--fluid-space-*) 준수
- 반응형: 5단계 브레이크포인트 (xs~2xl), Container Query로 컴포넌트 레벨 반응형 구현
- 애니메이션: Spring 이징 (--ease-spring-*) 활용, `prefers-reduced-motion` 대응 필수
- 다크 모드: Semantic 토큰 교체 방식 (순수 검정 사용 금지, 레이어드 엘리베이션)
- 디자인 시스템 프리뷰 페이지로 토큰/컴포넌트를 시각적으로 검증
- `design-token-validator` 에이전트로 자동 검증 (Gate 2.5)

**모바일 프로젝트 (Step 0.5 = Mobile일 때 대체):**
- **모바일 디자인 가이드 필독**: 모든 UI 구현 시 ASTRA 모바일 디자인 가이드를 참조할 것 (플랫폼 가이드라인, 터치 인터랙션, 애니메이션 타이밍, 햅틱 피드백, 접근성, 전문가 노하우)
- React Native: `src/styles/design-tokens.ts`를 반드시 참조, StyleSheet 또는 NativeWind 유틸리티 사용
- Flutter: `lib/shared/theme/design_tokens.dart`를 반드시 참조, `Theme.of(context)` 사용 필수
- KMP: `composeApp/src/commonMain/kotlin/theme/DesignTokens.kt`를 반드시 참조, MaterialTheme 사용 필수
- 디자인 토큰 3계층 구조 (Reference → Semantic → Component) 준수
- 컬러, 폰트, 스페이싱 하드코딩 절대 금지 (토큰 상수/테마 참조)
- 8dp 그리드 시스템 준수
- 다크 모드 지원 필수 (시스템 설정 연동, 순수 검정(#000000) 대신 #121212 사용)
- 접근성: 최소 터치 영역 44x44dp (iOS 44pt, Android 48dp), 스크린 리더 라벨 필수, 색상 대비 4.5:1
- 애니메이션: 마이크로 피드백 50~150ms, 상태 전환 150~300ms, 화면 전환 250~400ms, `prefers-reduced-motion` 대응 필수
- 햅틱 피드백: 상태 변경 인터랙션에 적절한 햅틱 유형 적용 (Selection, Impact, Notification)
- 엄지 영역(Thumb Zone): CTA 버튼은 화면 하단 1/3에 배치
- 디자인 시스템 프리뷰 화면으로 토큰/컴포넌트를 시각적으로 검증

## Prohibited Practices
- console.log 금지 (logger 사용)
- any 타입 금지
- 직접 SQL 금지 (ORM 사용)
- .env 파일 커밋 금지
{모바일 프로젝트일 때 추가:}
- 인라인 스타일 금지 (디자인 토큰/테마 사용)
- 하드코딩된 API URL 금지 (환경 변수 사용)
- 플랫폼 분기를 `Platform.OS === 'ios'`로 직접 하지 말고 추상화 레이어 사용
- keystore/signing key 커밋 금지

## Testing Rules
- 모든 서비스 레이어에 단위 테스트 작성
- 최소 테스트 커버리지 70%
- 테스트 전략: `docs/tests/test-strategy.md`
- 테스트 케이스: `docs/tests/test-cases/sprint-N/` (스프린트별 관리)
- 테스트 보고서: `docs/tests/test-reports/` (커버리지 달성률 포함)
- `/test-scenario`로 E2E 시나리오 자동 생성, `/test-run`으로 Chrome MCP 통합 테스트
{모바일 프로젝트일 때 추가:}
- React Native: Jest + React Native Testing Library로 컴포넌트 테스트, Detox/Maestro로 E2E 테스트
- Flutter: `flutter test`로 유닛/위젯 테스트, `integration_test/`로 통합 테스트
- KMP: `commonTest`에 공유 로직 테스트, 플랫폼별 테스트는 `androidTest`/`iosTest`

## Commit Convention
- Conventional Commits (feat:, fix:, refactor:, docs:, test:)
- `/commit` — 자동 커밋 메시지 생성
- `/commit-push-pr` — 커밋+푸시+PR 일괄 생성
- `/pr-merge` — 커밋→PR→리뷰→수정→머지 전체 사이클

## Design Document Rules
- 기능별 설계 문서는 docs/blueprints/{NNN}-{feature-name}/ 디렉토리로 구성 (예: 001-auth/, 002-payment/)
- 각 블루프린트 디렉토리의 메인 파일은 blueprint.md, 관련 보조 파일(다이어그램, API 스펙 등)도 같은 디렉토리에 배치
- DB 설계는 docs/database/database-design.md에서 중앙 관리
- 설계 문서는 기능 구현 전에 반드시 작성 및 승인 완료
- 블루프린트 기반 워크플로우: 블루프린트 작성 → DE 승인 → DB 설계 반영 → 스프린트 프롬프트 맵 작성 → 구현
- 설계 문서 품질은 `blueprint-reviewer` 에이전트가 검증 (Gate 2)

## Quick Command Reference

| 상황 | 커맨드 |
|------|--------|
| 프로젝트 초기 셋업 | `/project-init` |
| Sprint 0 체크리스트 | `/project-checklist` |
| 스프린트 초기화 | `/sprint-plan [N]` |
| 기능 설계/구현 | `/feature-dev [설명]` |
| 표준 용어 확인 | `/lookup-term [한글 용어]` |
| 국제 코드 조회 | `/lookup-code [코드]` |
| DB 엔티티 생성 | `/generate-entity [한글 정의]` |
| E2E 테스트 시나리오 | `/test-scenario` |
| 통합 테스트 실행 | `/test-run` |
| 코딩 컨벤션 검사 | `/check-convention [대상]` |
| DB 네이밍 검사 | `/check-naming [대상]` |
| 커밋 | `/commit` |
| 커밋+푸시+PR 일괄 | `/commit-push-pr` |
| PR→리뷰→머지 자동화 | `/pr-merge` |
| 코드 리뷰 | `/code-review` |
| Slack→블루프린트+스프린트 | `/slack-to-sprint [채널]` |
| Slack 백로그 추출 | `/slack-backlog [채널]` |
| 훅 규칙 생성 | `/hookify [설명]` |
| 빠른 참조 가이드 | `/astra-guide` |

## Prompt Writing Guide

좋은 프롬프트의 5요소:

1. **What** (무엇을): 만들어야 할 기능의 명확한 설명
2. **Why** (왜): 비즈니스 목적과 사용자 가치
3. **Constraint** (제약): 기술적 제약사항과 성능 요구사항
4. **Reference** (참조): 관련 설계 문서 경로 (docs/blueprints/{NNN}-{feature-name}/, docs/database/)
5. **Acceptance** (기준): 완료 조건과 검증 방법

    BAD: "결제 기능을 만들어줘"

    GOOD:
    /feature-dev "결제 처리 모듈을 구현해줘.
    - 카드 결제와 계좌이체를 지원
    - PG사 API(이니시스)와 연동
    - 결제 실패 시 3회까지 자동 재시도
    - docs/blueprints/003-payment/blueprint.md의 설계를 따를 것
    - DB 스키마는 docs/database/database-design.md를 참조할 것
    - 단위 테스트와 통합 테스트를 모두 작성할 것"
```

**기술 스택별 커스텀 규칙:**

**웹 프레임워크:**
- **Spring Boot**: `@RestControllerAdvice` 전역 예외 처리, `@Valid` 입력 검증, Lombok 사용
- **NestJS**: `ExceptionFilter` 전역 예외 처리, `class-validator` DTO 검증, Prisma ORM
- **FastAPI**: `HTTPException` 사용, Pydantic 모델 검증, SQLAlchemy ORM
- **Next.js**: App Router 기본, Server Components 우선, Server Actions 활용
- **React**: 함수형 컴포넌트만 사용, 커스텀 훅 패턴
- **Vue 3**: Composition API 기본, `<script setup>` 사용

**모바일 프레임워크 (Step 0.5 = Mobile일 때만 포함):**
- **React Native / Expo**: 함수형 컴포넌트 + TypeScript 필수, Expo Router 기반 네비게이션, Zustand 상태 관리, TanStack Query 서버 상태, `kebab-case` 파일명, `StyleSheet.create()` 또는 NativeWind, 인라인 스타일 금지, `expo-secure-store`로 민감 데이터 저장
- **Flutter**: Dart strict mode (`analysis_options.yaml`), Feature-first 디렉토리 구조, Riverpod/Bloc 상태 관리, GoRouter 네비게이션, Freezed 불변 모델, `snake_case` 파일명, Theme.of(context) 토큰 참조 필수, 하드코딩 컬러/폰트 금지, `flutter_secure_storage`로 민감 데이터 저장
- **Kotlin Multiplatform (KMP)**: shared 모듈에 비즈니스 로직 집중, expect/actual 패턴으로 플랫폼 분기, Compose Multiplatform UI, Koin DI, Ktor HTTP 클라이언트, Kotlinx Serialization, SQLDelight 로컬 DB, `camelCase` 함수/변수, `PascalCase` 클래스

### Step 5: Create Design System Templates & Implement Components

#### Step 5-A: Create design system files

Create the design token source file and documentation files separately.

**For Web projects:**

**`src/styles/design-tokens.css`**: 3-tier design token set (Primitive → Semantic → Component). OKLCH color space, Geist Sans + Pretendard Korean font stack, fluid typography with clamp(), 4px base grid spacing, spring-based animation easings, reduced-motion support, and dark mode via semantic token overrides. This is a source file consumed by components via `@import`, so it belongs in `src/styles/`, NOT in `docs/`.

**`docs/design-system/components.md`**: Core component style guide (13 components: buttons, inputs, cards, modals, tables, navigation, toasts, badges, skeleton loading, avatar, sheet/drawer, command palette, toggle). All values reference Semantic or Component tokens only — never Primitive tokens directly. Includes transition/animation guidance per component.

**`docs/design-system/layout-grid.md`**: Layout grid system with 5-tier breakpoints (xs~2xl), CSS Grid/Subgrid patterns, Container Queries for component-level responsiveness, fluid spacing with clamp()

**For Mobile projects:**

> **IMPORTANT**: When creating design tokens and components for mobile projects, you MUST read and follow the mobile design guide at `$CLAUDE_PLUGIN_ROOT/docs/ux/mobile-design-guide.md`. This guide contains platform-specific guidelines (Apple HIG, Material Design 3), touch interaction patterns, typography scales, color system & dark mode principles, haptic feedback mapping, animation timing, accessibility requirements, and expert-level polish tips. All design decisions below should align with this guide.

Create the design token source file in the framework-appropriate location:

- **React Native**: `src/styles/design-tokens.ts` — TypeScript object with colors, typography, spacing, shadows as constants. Export typed theme object. Follow the token hierarchy (Reference → Semantic → Component) from the mobile design guide.
- **Flutter**: `lib/shared/theme/design_tokens.dart` — Dart class with static const values for ColorScheme, TextTheme, spacing. Includes `lightTheme()` and `darkTheme()` factory methods. Follow the token hierarchy from the mobile design guide.
- **KMP**: `composeApp/src/commonMain/kotlin/theme/DesignTokens.kt` — Kotlin object with Material3 ColorScheme, Typography, spacing values. Follow the token hierarchy from the mobile design guide.

**`docs/design-system/components.md`**: Core component style guide template adapted for mobile (buttons, text inputs, bottom sheet, bottom navigation, list items, cards, dialogs/alerts, snackbar/toast, avatar, loading indicators). Reference the mobile design guide's Section 14 ("전문가 노하우") for polish-level quality standards.

#### Step 5-B: Implement Design System Components (if a design system was selected)

If the user selected a design system in Step 2 (not "추후 직접 구현"), invoke the `/frontend-design` skill to implement the following **common base components**. Pass the selected design system, tech stack, and design tokens as context.

> **IMPORTANT**: The prompt below is written in Korean as a reference. You MUST translate the entire prompt into the language selected in Step 0 BEFORE invoking the frontend-design skill.

**For Web projects**, use the Skill tool to invoke `frontend-design` with a prompt like:

```
"프로젝트 {project-name}의 디자인 시스템 공통 컴포넌트를 구현해 줘.

- 디자인 시스템: {selected-design-system}
- 프론트엔드: {frontend-tech-stack}
- 디자인 토큰: src/styles/design-tokens.css 참조 (3-tier: Primitive → Semantic → Component, OKLCH 색상)
- 컴포넌트 가이드: docs/design-system/components.md 참조
- 레이아웃 가이드: docs/design-system/layout-grid.md 참조

아래 공통 컴포넌트를 구현해 줘:
1. Button — Primary/Secondary/Danger/Ghost/Outline 변형, sm/md/lg 크기, 로딩/비활성 상태
2. Input — 텍스트 입력, 라벨, 에러 상태, 헬퍼 텍스트, 비활성 상태
3. Card — Default/Elevated/Outlined/Interactive/Ghost 변형, Container Query 반응형
4. Modal/Dialog — 헤더/바디/푸터 구조, 백드롭, sm/md/lg/full 크기, Spring 애니메이션
5. Toast — Success/Warning/Error/Info 변형, Spring 진입 애니메이션, 자동 닫힘
6. Badge — 상태 뱃지, 카테고리 태그, sm/md/lg 크기, dot 인디케이터
7. Table — 정렬, 호버, sticky 헤더, 반응형 (모바일 카드 전환)
8. Dropdown/Select — 옵션 목록, 검색, 다중 선택, Command Palette 스타일
9. Tabs — 애니메이션 인디케이터, 활성/비활성 상태
10. Sidebar Layout — 접기/펼치기, Spring 전환 애니메이션, 활성 메뉴 하이라이트
11. Skeleton — 텍스트/아바타/카드/테이블 Shimmer 패턴
12. Avatar — 이미지/이니셜/아이콘, xs~xl 크기, 온라인 인디케이터, 그룹 스태킹
13. Toggle/Switch — sm/md 크기, Spring 바운스 전환

모든 컴포넌트는:
- Semantic/Component 토큰만 참조 (Primitive 직접 참조 금지)
- OKLCH 기반 다크 모드 지원
- 반응형 + Container Query 대응
- 접근성(ARIA, 포커스 링, 키보드 내비게이션) 준수
- Spring 이징 (--ease-spring-*) + prefers-reduced-motion 대응
- 프로젝트의 코딩 컨벤션 준수
- 디자인 시스템 프리뷰 페이지도 함께 생성해 줘 (모든 컴포넌트를 라이트/다크 모드로 확인 가능)"
```

**For Mobile projects**, use the Skill tool to invoke `frontend-design` with a prompt adapted to the mobile framework:

```
"프로젝트 {project-name}의 모바일 디자인 시스템 공통 컴포넌트를 구현해 줘.

- 디자인 시스템: {selected-design-system}
- 모바일 프레임워크: {mobile-framework}
- 디자인 토큰: {token-file-path} 참조
- 컴포넌트 가이드: docs/design-system/components.md 참조
- 모바일 디자인 가이드: $CLAUDE_PLUGIN_ROOT/docs/ux/mobile-design-guide.md 참조 (플랫폼 가이드라인, 터치 인터랙션, 애니메이션 타이밍, 햅틱 피드백, 접근성 기준)

아래 공통 컴포넌트를 구현해 줘:
1. Button — Primary/Secondary/Danger/Ghost 변형, sm/md/lg 크기, 로딩/비활성 상태, 햅틱 피드백
2. TextInput — 텍스트 입력, 라벨, 에러 상태, 헬퍼 텍스트, 비활성 상태, 키보드 타입 지원
3. Card — Default/Elevated/Outlined/Pressable 변형
4. BottomSheet — 스냅 포인트, 드래그 핸들, 백드롭, 크기 변형
5. Toast/Snackbar — Success/Warning/Error/Info 변형, 자동 닫힘, 스와이프 해제
6. Badge — 상태 뱃지, 알림 카운트, sm/md 크기
7. ListItem — 좌측 아이콘, 제목/부제목, 우측 액세서리, 스와이프 액션
8. BottomNavigation — 탭 아이콘+라벨, 활성 인디케이터, 뱃지 지원
9. Avatar — 이미지/이니셜/아이콘, sm/md/lg/xl 크기, 온라인 상태 인디케이터
10. LoadingIndicator — Spinner/Skeleton/Shimmer 변형, 풀 스크린 오버레이
11. Dialog/Alert — 제목/메시지/액션 버튼, 확인/취소 패턴
12. SearchBar — 검색 아이콘, 클리어 버튼, 취소 버튼, 자동완성 지원

모든 컴포넌트는:
- 디자인 토큰(테마 시스템) 사용
- 다크 모드 지원 (시스템 설정 연동)
- 최소 터치 영역 44x44dp
- 접근성(스크린 리더 라벨, 포커스 관리) 준수
- 프로젝트의 코딩 컨벤션 준수
- 디자인 시스템 프리뷰 화면도 함께 생성해 줘 (Storybook 또는 앱 내 프리뷰 스크린)"
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

### Step 11: Module Auto-Builder (Multi-Agent)

> **MANDATORY**: This step MUST always be executed. You MUST use AskUserQuestion to present the module selection and wait for the user's response before proceeding. The module building itself is optional (the user may choose to skip), but the question MUST always be asked.

After all templates and scaffolding are created, ask the user whether to auto-build common modules. These modules run the full pipeline: **Blueprint → Sprint Plan → Implementation → Test Scenarios → Test Run & Debug**.

> **Mobile adaptation**: When the platform is Mobile, the module builders automatically adapt their output to the mobile framework and backend strategy selected in Step 1-B. For example, the auth module will generate mobile login screens (with biometric auth, social login SDKs) instead of web forms, and API integration code will use the appropriate HTTP client (Ktor for KMP, Dio for Flutter, Axios/fetch for React Native).

> **IMPORTANT**: The option text below is in Korean. You MUST translate all option text into the language selected in Step 0 before presenting to the user.

Use AskUserQuestion:

```
## 공통 모듈 자동 구축

프로젝트 초기 설정이 완료되었습니다. 다음 공통 모듈을 자동으로 구축할 수 있습니다.
각 모듈은 블루프린트 작성 → 스프린트 생성 → 구현 → 테스트 시나리오 → 테스트 실행까지 전체 파이프라인을 자동 실행합니다.

구축할 모듈을 선택해 주세요 (복수 선택 가능, 쉼표로 구분):

1. 인증 모듈 — 회원가입, 로그인/로그아웃, JWT 토큰, 약관 관리, 사용자 관리
2. 워크스페이스 모듈 — 워크스페이스 CRUD, 멤버 관리, 초대 시스템, 전환기 (인증 모듈 필요)
3. 결제 모듈 — 구독/플랜, 빌링키, PG 연동, 정기결제, Dunning, 크레딧 (인증+워크스페이스 필요)
4. 전체 선택 (1→2→3 순서로 자동 실행)
5. 건너뛰기 (나중에 /auth-module, /workspace-module, /payment-module로 개별 실행)
```

If the user selects option 5, skip to Step 12.

#### Step 11-A: Execute module builders respecting dependency order

Module dependency chain: **Auth → Workspace → Payment**

- Workspace requires Auth (TB_COMM_USER, JWT)
- Payment requires Auth + Workspace (TB_COMM_WKSPC, TR_COMM_WKSPC_MBR)

**Prerequisite confirmation (before execution):**

If the user selects a module that has missing prerequisites (e.g., Workspace without Auth), use **AskUserQuestion** to confirm before adding prerequisites:

```
워크스페이스 모듈은 인증 모듈(TB_COMM_USER, JWT)에 의존합니다.
인증 모듈을 먼저 자동 구축한 후 워크스페이스 모듈을 실행합니다. 계속하시겠습니까?

1. 예 — 인증 모듈을 먼저 구축 후 워크스페이스 모듈 실행
2. 아니오 — 모듈 구축을 건너뛰기
```

If the user declines, skip module building and proceed to Step 12.

**Execution strategy (after prerequisite confirmation):**

| User Selection | Execution Plan |
|---|---|
| Auth only | Auth |
| Workspace only | Auth (confirmed prerequisite) → Workspace |
| Payment only | Auth → Workspace (confirmed prerequisites) → Payment |
| Auth + Workspace | Auth → Workspace |
| Auth + Payment | Auth → Workspace (confirmed prerequisite) → Payment |
| Workspace + Payment | Auth (confirmed prerequisite) → Workspace → Payment |
| All (option 4) | Auth → Workspace → Payment |

**Agent invocation pattern:**

For each module, invoke the corresponding skill using the Skill tool. After each dependency completes, immediately launch the next module.

```
Phase 1 — Auth (if selected or required as dependency):
  Use Skill tool: invoke "auth-module"

Phase 2 — Workspace (if selected or required as dependency, after Auth completes):
  Use Skill tool: invoke "workspace-module"

Phase 3 — Payment (if selected, after Workspace completes):
  Use Skill tool: invoke "payment-module"
```

Each skill internally handles the full pipeline:
1. Reference design document loading
2. Blueprint generation (`docs/blueprints/{NNN}-{module}/blueprint.md`)
3. Sprint plan generation
4. Implementation (backend API + frontend screens)
5. Test scenario generation
6. Test run & auto-debug (up to 5 retry cycles)

#### Step 11-B: Module build progress reporting

After each module completes, output a brief status update:

```
## 모듈 자동 구축 진행 상황

| 모듈 | 상태 | 블루프린트 | 구현 | 테스트 |
|------|------|-----------|------|--------|
| 인증 | ✅ 완료 | docs/blueprints/001-auth/ | src/... | ✅ Pass |
| 워크스페이스 | 🔄 진행중 | - | - | - |
| 결제 | ⏳ 대기 | - | - | - |
```

When all selected modules are complete, proceed to Step 12.

### Step 12: Output Result Summary

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
{Mobile일 때: Framework: {React Native/Flutter/KMP}, Target: {Android/iOS/Both}, Backend: {strategy}}

### Design System
- Selected: {design-system-name} (or "Implement later")
- **Web**: Common components: Button, Input, Card, Modal, Toast, Badge, Table, Dropdown, Tabs, Sidebar Layout
- **Mobile**: Common components: Button, TextInput, Card, BottomSheet, Toast, Badge, ListItem, BottomNavigation, Avatar, LoadingIndicator, Dialog, SearchBar
- Preview: {preview-page-path} (if design system was selected)

### Module Auto-Build Results (if modules were selected)
| Module | Status | Blueprint | Implementation | Tests |
|--------|--------|-----------|----------------|-------|
| Auth | {status} | {path} | {path} | {result} |
| Workspace | {status} | {path} | {path} | {result} |
| Payment | {status} | {path} | {path} | {result} |

(Only include rows for modules that were selected. Omit this section entirely if the user chose "Skip".)

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
