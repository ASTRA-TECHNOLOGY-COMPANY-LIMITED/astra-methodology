---
name: project-init
description: "ASTRA Sprint 0 project initial setup. Creates project directory structure, CLAUDE.md, design system templates, blueprint templates, and sprint templates."
argument-hint: "[project-name] [backend-tech] [frontend-tech] [db-type]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# ASTRA Sprint 0: Project Initial Setup

You are an expert in Sprint 0 setup for the ASTRA (AI-augmented Sprint Through Rapid Assembly) methodology.
You configure the initial setup tailored to the user's project.

## Execution Procedure

### Step 1: Gather Project Information

If user arguments are insufficient, use AskUserQuestion to confirm the following:

1. **Project name** (e.g., online-payment-system)
2. **Project description** (one-line summary)
3. **Backend tech stack** (e.g., Spring Boot 3, NestJS, FastAPI)
4. **Frontend tech stack** (e.g., Next.js 15, React, Vue 3)
5. **Database** (e.g., PostgreSQL 16, MySQL 8, MongoDB)
6. **Key modules** (e.g., member management, product management, orders, payments, notifications)
7. **Team composition** (number of VA, PE, DE, DSA members)

If `$ARGUMENTS` is provided, parse and extract as much information as possible, and only ask additional questions for missing information.

### Step 2: Create Project Directory Structure

Create the following structure in the current working directory (CWD):

```
{project-root}/
├── CLAUDE.md
├── .claude/
│   └── settings.json
│
├── docs/
│   ├── design-system/
│   │   ├── design-tokens.css
│   │   ├── components.md
│   │   ├── layout-grid.md
│   │   └── references/
│   │       └── .gitkeep
│   │
│   ├── blueprints/
│   │   └── overview.md
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
│   │   │   └── .gitkeep
│   │   └── test-reports/
│   │       └── .gitkeep
│   │
│   ├── prompts/
│   │   └── sprint-1.md
│   │
│   ├── retrospectives/
│   │   └── .gitkeep
│   │
│   └── delivery/
│       └── .gitkeep
│
└── src/
    └── .gitkeep
```

### Step 3: Create CLAUDE.md

Customize the template below according to the project information and generate it:

```markdown
# Project: {project-name}

> {project description}

## Architecture
- Backend: {backend tech stack}
- Frontend: {frontend tech stack}
- Database: {DB type}

## Key Modules
{list modules as bullet points}

## Coding Rules
- Authentication middleware is required for all API endpoints
- DB schema is managed using docs/database/database-design.md as the Single Source of Truth
- DB entities must comply with the public data standard terminology dictionary (use /lookup-term)
- Table name prefixes: TB_ (general), TC_ (code), TH_ (history), TL_ (log), TR_ (relation)
- REST API response format: { success: boolean, data: T, error?: string }
- Error handling: distinguish between business exceptions and system exceptions

## Design Rules (defined by DSA)
- Design tokens: must reference docs/design-system/design-tokens.css
- Colors must use CSS Variables (--color-*), hardcoding is prohibited
- Font sizes must use token scale (--font-size-*)
- Spacing must follow the 8px grid system (--spacing-*)
- Responsive breakpoints: mobile(~767px), tablet(768~1023px), desktop(1024px~)

## Prohibited Practices
- No console.log (use logger)
- No any type
- No raw SQL (use ORM)
- No committing .env files

## Testing Rules
- Write unit tests for all service layers
- Minimum test coverage of 70%

## Commit Convention
- Conventional Commits (feat:, fix:, refactor:, docs:, test:)

## Design Document Rules
- Feature-specific design documents go in the docs/blueprints/ directory
- DB design is centrally managed in docs/database/database-design.md
- Design documents must be written and approved before feature implementation
```

**Tech stack-specific customization rules:**

- **Spring Boot**: `@RestControllerAdvice` global exception handling, `@Valid` input validation, Lombok usage
- **NestJS**: `ExceptionFilter` global exception handling, `class-validator` DTO validation, Prisma ORM
- **FastAPI**: Use `HTTPException`, Pydantic model validation, SQLAlchemy ORM
- **Next.js**: App Router by default, Server Components first, leverage Server Actions
- **React**: Functional components only, custom hooks pattern
- **Vue 3**: Composition API by default, use `<script setup>`

### Step 4: Create Design System Templates

Create the following files under `docs/design-system/`.

**design-tokens.css**: Base design token set (colors, typography, spacing, shadows, responsive breakpoints)

**components.md**: Core component style guide template (buttons, inputs, cards, modals, tables, navigation)

**layout-grid.md**: Layout grid system definition (column system, containers, behavior per breakpoint)

### Step 5: Create Blueprint Template

**docs/blueprints/overview.md**: Project overview document (vision, goals, module structure, tech stack decision rationale)

### Step 6: Create Database Document Templates

**docs/database/database-design.md**: Central DB design document template (full ERD, common rules, module-specific tables, FK relationship summary)

**docs/database/naming-rules.md**: DB naming rules and standard terminology mapping document (table prefixes, column naming, standard terminology dictionary integration)

### Step 7: Create Test Document Template

**docs/tests/test-strategy.md**: Test strategy document (test level definitions, coverage goals, test environments, naming conventions, automation scope)

### Step 8: Create Sprint Template

**docs/prompts/sprint-1.md**: First sprint prompt map template

**docs/prompts/sprint-1-progress.md**: First sprint progress tracker (template format with placeholder features — features will be populated when the sprint is actually planned)

### Step 9: Create Project Configuration File

**.claude/settings.json**: Project-specific Claude Code settings

### Step 10: Output Result Summary

After all files are created, output the following:

```
## ASTRA Sprint 0 Initial Setup Complete

### Generated File List
- CLAUDE.md (project AI rules)
- .claude/settings.json (project settings)
- docs/design-system/ (design system templates)
- docs/blueprints/ (design document templates)
- docs/database/ (DB design documents, naming rules, migrations)
- docs/tests/ (test strategy, test cases, test reports)
- docs/prompts/ (sprint prompt maps)
- docs/retrospectives/ (for retrospective records)
- docs/delivery/ (for release artifacts)

### Next Steps (Sprint 0 progress)
1. [ ] Review CLAUDE.md and customize for the project
2. [ ] Define docs/design-system/ files with DSA
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
- All text is written in Korean (except code comments).
