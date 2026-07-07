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

Create the directory structure matching the platform (Step 0.5) and, for mobile, the framework (Step 1-B). Read `references/directory-structures.md` and create the corresponding tree (Web / React Native / Flutter / KMP) in the current working directory (CWD).

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

Read `references/claude-md-template.md` and instantiate the template with the project information, writing the result to `{project-root}/CLAUDE.md`. Include only the Web or Mobile conditional branches matching the Step 0.5 selection, and append the matching per-tech-stack custom rules block (also in that reference file).

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

Read `references/component-implementation-prompts.md` and invoke `frontend-design` with the matching prompt: the "Web project prompt" for Web projects, or the "Mobile project prompt" for Mobile projects. Substitute the `{...}` placeholders and translate the prompt into the Step 0 language before invoking.

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
