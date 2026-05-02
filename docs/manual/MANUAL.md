# ASTRA: AI-augmented Sprint Through Rapid Assembly

**SPI-based AI-Enhanced Scrum Development Methodology**

> ASTRA is an **AI-Enhanced Scrum** methodology that combines the AI agent ecosystem of
> Claude Code with the existing SPI (Success Path Integration) methodology's agile scrum process,
> eliminating residual waste in scrum and maximizing the advantages of vibe coding.

---

## Table of Contents

1. [Methodology Overview](#1-methodology-overview)
2. [Evolution from Scrum to ASTRA](#2-evolution-from-scrum-to-astra)
3. [Role Definitions](#3-role-definitions)
- [Development Workflow](#development-workflow)
4. [Plugin Initial Setup](#4-plugin-initial-setup)
5. [Design System Creation](#5-design-system-creation)
6. [Blueprint Creation](#6-blueprint-creation)
7. [Database Design](#7-database-design)
8. [Blueprint-based Sprint Creation](#8-blueprint-based-sprint-creation)
9. [Implementation](#9-implementation)
10. [Test Scenario Creation](#10-test-scenario-creation)
11. [Test Execution](#11-test-execution)
12. [PR / Review](#12-pr--review)
13. [Staging Branch Merge](#13-staging-branch-merge)
14. [User Testing](#14-user-testing)
15. [Main Branch Merge](#15-main-branch-merge)
- [Appendices](#appendices)
  - [A: Claude Code Tools Quick Reference](#appendix-a-claude-code-tools-quick-reference)
  - [A-2: Agents Quick Reference](#appendix-a-2-agents-quick-reference)
  - [B: Prompt Writing Guide](#appendix-b-prompt-writing-guide)
  - [C: Risk Management](#appendix-c-risk-management)
  - [D: AI Agent Task Time Estimation Rationale](#appendix-d-ai-agent-task-time-estimation-rationale)
  - [E: Sprint 0 Project Setup](#appendix-e-sprint-0-project-setup)
  - [F: Project Template](#appendix-f-project-template)
  - [G: Expected Benefits](#appendix-g-expected-benefits)
  - [H: Cost Effectiveness](#appendix-h-cost-effectiveness)

---

## 1. Methodology Overview

### What is ASTRA?

**A**I-augmented **S**print **T**hrough **R**apid **A**ssembly

ASTRA carries the meaning of "star (Astra, Latin)" and serves as a compass that rapidly guides projects to their destination.

### Core Philosophy

ASTRA **does not reject agile scrum.** It is an **evolved scrum** that maintains scrum's proven framework while AI agents absorb inefficiencies occurring in each scrum activity to produce faster and higher-quality results.

**What changed:** Sprint cycle (2 weeks to 1 week, smaller increments and faster feedback), AI automation of manual tasks (40-60% time reduction), built-in quality gates
**What stayed the same:** Scrum's incremental value delivery, the three pillars of transparency, inspection, and adaptation

### VIP Principles

| Principle | Core | Implementation Tools |
|-----------|------|---------------------|
| **V**ibe-driven Development | Don't write code, convey intent | `feature-dev`, `frontend-design` |
| **I**nstant Feedback Loop | Shorten the in-sprint feedback cycle to hours | `chrome-devtools` MCP, `code-review` |
| **P**lugin-powered Quality | Quality is built into the code | `astra-methodology`, `security-guidance`, `hookify` |

### Relationship with SPI

| SPI 5 Stages | ASTRA Implementation | Tools Used |
|--------------|---------------------|------------|
| 1. Strategy | Product Vision + Tech stack validation | `context7` MCP |
| 2. Process Map | Product Backlog refinement + Auto-generated design documents | `feature-dev` Phase 1-4 |
| 3. Iterative Build | AI parallel implementation (1-week sprint cycles) | `feature-dev` + `frontend-design` |
| 4. Integration | Real-time integration verification | `chrome-devtools` MCP |
| 5. Success Launch | Auto-documentation + Quality reports | `feature-dev` Phase 7 |

| SPI 3S Principles | ASTRA Implementation | Tools Used |
|-------------------|---------------------|------------|
| Standardization | Automatic enforcement at write-time | `astra-methodology` (PostToolUse hooks) |
| Scalability | Automated scalability review | `feature-dev` code-architect |
| Security | Real-time blocking of security patterns | `security-guidance` (PreToolUse hooks) |

---

## 2. Evolution from Scrum to ASTRA

This section consolidates all comparisons with traditional scrum. Subsequent sections focus on ASTRA's own execution methods.

### 2.1 Summary of Key Changes

```
Traditional Scrum:
  Product Backlog -> Sprint Planning -> Sprint(2wk) -> Sprint Review -> Retrospective
                                          |
                                     Dev -> Test -> Review (manual, sequential)

ASTRA:
  Product Backlog -> Sprint Planning -> Sprint(1wk) -> Sprint Review -> Retrospective
       |                 |               |               |               |
    AI Refinement    AI Estimation    AI Parallel      Real-time Demo   AI Analysis
  (code-explorer)  (Auto Analysis) (Dev+Test+Review) (chrome-devtools)  (hookify)
```

### 2.2 Activity-by-Activity Comparison

| Activity | Traditional Scrum | ASTRA | Reduction Rationale |
|----------|------------------|-------|---------------------|
| **Sprint Cycle** | 2 weeks | 1 week (smaller increments, faster feedback) | AI handles dev+test+review in parallel; shorter cycles improve agility |
| **Story Analysis/Design** | 1-2 days | 2-4 hours | AI analysis 20-40 min + human review/refinement 1-2 hours (`feature-dev` Phase 1-4) |
| **Manual Coding** | 5-7 days | 2-4 days | AI code generation 1-3 hours + human verification/iteration cycles (40-60% reduction based on METR research) |
| **Code Review Wait** | 1-2 days | 20-40 min | AI review execution 10-15 min + human result review 10-20 min (`code-review` agent in parallel) |
| **Unit Test Writing** | 1-2 days | Concurrent | `feature-dev` generates tests alongside code (human verification 30 min - 1 hour required) |
| **Coding Standard Debates** | Repeated every review | Eliminated at source | `astra-methodology` auto-applies at write-time |
| **Security Checks** | Separate sprint | Real-time blocking | `security-guidance` auto-blocks 9 patterns |
| **UI Design Handoff** | Designer to developer wait | Direct generation | AI generation 15-30 min + DSA review 1-2 hours (`frontend-design`) |
| **Retrospective Effectiveness** | "We'll improve next time" | Enforced as rules | Instantly converted to automated rules via `hookify` |
| **Requirements Change Response** | Next sprint (2+ weeks) | 1-2 days | Impact analysis + design doc updates + AI code reflection + human verification |

### 2.3 Ceremony Comparison

| Event | Traditional Duration | ASTRA Duration | AI Enhancement |
|-------|---------------------|----------------|----------------|
| Sprint Planning | 4 hours | 1 hour | Leverages `feature-dev` pre-analysis reports |
| Daily Scrum | 15 min x 10 days = 2.5h | Async | Commit-based automatic progress reporting |
| Design Review | (none) | 1 hour | DSA review of AI-generated UI |
| Sprint Review | 2 hours | 1 hour | `chrome-devtools` real-time demo |
| Retrospective | 1.5 hours | 30 min | `sprint-analyzer` AI analysis -> `hookify` automation |
| Backlog Refinement | 2 hours | 30 min | `feature-dev` code-explorer auto-analysis |
| **Total** | **~12 hours/sprint** | **~4 hours/sprint** | **67% reduction** |

### 2.4 Role Comparison

| Traditional Scrum | ASTRA | Change |
|------------------|-------|--------|
| Product Owner (PO) x1 | Domain Expert (DE) x1 | PO role maintained + real-time feedback |
| Scrum Master (SM) x1 | Vibe Architect (VA) x1 | SM + architecture + prompt design |
| Developers x3-5 | Prompt Engineer (PE) x1-2 | Manual coding -> prompt design + verification |
| UI Designer x1 | Design System Architect (DSA) x1 | Design system construction + review |
| QA x1-2 | (Replaced by AI agents) | `code-review` + `security-guidance` |
| **Total 7-10 people** | **Total 4-5 people** | **50% reduction** |

### 2.5 Artifact Comparison

| Scrum Artifact | ASTRA Evolution |
|---------------|-----------------|
| Product Backlog | + Linked to `docs/sprints/` prompt maps |
| Sprint Backlog | + Feature-specific prompts + design documents (MD) |
| Increment | + Auto quality reports + Living Documents |
| Definition of Done (manual check) | + AI quality gate auto-verification (Gate 1-3) |
| (Test docs scattered) | + Centralized test strategy/cases/reports in `docs/tests/` |
| (DB design scattered) | + Centralized DB design/naming/migration in `docs/database/` |

### 2.6 Cost Effectiveness

```
            Traditional Scrum    ASTRA              Savings
 Duration:  5 months             3 months           40% reduction
 Team:      8 people             4 people           50% reduction
 Labor:     320M KRW             96M KRW            70% reduction
 API cost:  -                    7M KRW             -
 Total:     350M KRW             110M KRW           69% reduction

 * Multiplier effect from simultaneous duration and team size reduction
 * Time reduction rates based on METR research at 40-60% (for structured AI workflows)
 * Quality actually improves with AI auto-gates (standard compliance 60-70% -> 95%+)
```

> **The secret to reducing both duration and team size simultaneously:**
> AI agents absorb **repetitive manual tasks** (coding, review, testing, standard checks),
> so people focus solely on **judgment and decision-making** (requirements, architecture, design, business logic).

---

## 3. Role Definitions

### VA (Vibe Architect) - 1 Senior Developer

Extends the Scrum Master role to also cover **AI agent orchestration**.

**Core Competencies:**
1. **Prompt Engineering**: Transform ambiguous backlog items into precise prompts
2. **AI Output Judgment**: Quickly assess the quality/accuracy of AI outputs
3. **Architecture Sense**: Select the optimal design from multiple proposals in `feature-dev` Phase 4
4. **Domain Knowledge**: Understand business logic and convey it accurately to AI

**Key Activities:**
- Sprint progress management + AI agent workflow design
- Prompt quality management and optimization
- Converting retrospective results into `hookify` rules
- Architecture decision-making + final quality gate judgment

### PE (Prompt Engineer) - 1-2 Junior Developers

Focuses on **prompt writing + AI output verification** rather than writing code directly.

**Key Activities:**
- Writing feature-specific prompts (based on design documents)
- Verifying AI-generated code and tests
- Reviewing and acting on AI review results
- Reviewing and refining design documents (MD)

### DE (Domain Expert) - 1 Client Business Representative

The traditional PO role with added **real-time feedback capabilities**.

**Key Activities:**
- Directly convey requirements in natural language (providing prompt material)
- Manage backlog priorities
- Provide immediate feedback during `chrome-devtools` real-time demos
- Directly perform acceptance verification on the working system

### DSA (Design System Architect) - 1 Designer

Even when AI generates UI code, **a professional designer's judgment is essential for design quality and consistency**.

**Key Activities:**
- **Sprint 0**: Build the design system (define color, typography, component, spacing tokens)
- **Feature Sprints**: Review AI-generated UI designs (verify design system compliance)
- **Release Sprint**: Final review of all screen designs

**Design Review Checklist:**
- [ ] Design token compliance (colors, fonts, spacing do not deviate from the token system)
- [ ] Component consistency (same component types are not rendered differently across screens)
- [ ] Responsive layout (mobile/tablet/desktop breakpoints are appropriate)
- [ ] Basic accessibility met (color contrast, focus indicators, text size)
- [ ] Interaction consistency (hover/focus/active states unified)
- [ ] Margins and alignment (grid system compliance)

---


## Development Workflow

> **Prerequisites**: The workflow below assumes that **Sprint 0 (initial project setup) has been completed**.
> Sprint 0 involves development environment setup (`/astra-setup`), project structure creation (`/project-init`), design system construction, CLAUDE.md creation, and hookify rule configuration.
> For details, refer to [Appendix E: Sprint 0 Project Setup](#appendix-e-sprint-0-project-setup).

```
[Sprint 0]
Design System Creation

[Feature Sprint]
Blueprint Creation -> Database Design -> Sprint Creation -> Implementation -> Test Scenarios -> Test Execution -> PR/Review
                                                                                                                      |
                                               Main Branch Merge <- User Testing <- Staging Branch Merge <-------------+
```

---

## 4. Plugin Initial Setup

To use the ASTRA methodology, you must first install the **astra-methodology plugin** and configure the global development environment. This process only needs to be performed **once per developer machine**.

> **Prerequisites**: [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) must be installed.

### 4.1 Installing the astra-methodology Plugin

Run the following commands in order from your terminal.

```bash
# Step 1: Register the ASTRA marketplace
claude plugin marketplace add https://github.com/ASTRA-TECHNOLOGY-COMPANY-LIMITED/astra-methodology.git

# Step 2: Install the astra-methodology plugin
claude plugin install astra-methodology@astra
```

### 4.2 Automatic Global Development Environment Setup

After installing the plugin, launch Claude Code and run the `/astra-setup` command to automatically configure the remaining environment.

```bash
# Launch Claude Code
claude

# Run global development environment setup within Claude Code
/astra-setup
```

Tasks automatically performed by `/astra-setup`:

> **Security Note**: `bypassPermissions` mode skips Claude Code's tool usage confirmation prompts. Only use this in trusted environments.

1. **Global Settings** (`~/.claude/settings.json`)
   - Enable Agent Teams environment variables
   - Configure Permission mode (bypassPermissions)
   - Enable Always Thinking

2. **MCP Server Registration** (`~/.claude/.mcp.json`)
   - `chrome-devtools` — for browser integration testing
   - `postgres` — for database connectivity
   - `context7` — for querying latest library documentation

3. **Automatic Installation of 9 Required Plugins**
   - `claude-code-setup`, `code-review`, `code-simplifier`, `commit-commands`
   - `feature-dev`, `frontend-design`, `hookify`, `security-guidance`, `context7`

4. **Prerequisite Tool Verification** — Checks for Node.js, npm/npx, Git, GitHub CLI installation

> After setup completes, a result report is displayed. Verify that all items are checked.

---

## 5. Design System Creation

During Sprint 0, the DSA leads the construction of the project's **design system**. The design system is the core foundation for AI to generate consistent UI. Design tokens (source code) are managed in `src/styles/`, and design documentation is managed in `docs/design-system/`.

> **Core Principle**: Without a design system, AI-generated UI will have inconsistent styles across screens. The token system serves as the design guardrail for AI.

### 5.1 Design System Directory Structure

```
src/styles/
└── design-tokens.css       # CSS Custom Properties (colors, fonts, spacing) — source code

docs/design-system/
├── components.md           # Core component style guide
├── layout-grid.md          # Layout grid system
└── references/             # Design references/moodboard images

tailwind.config.js          # For Tailwind-based projects (project root)
```

> **Why `src/styles/`?** `design-tokens.css` is source code that components `@import` and use. All major frameworks like shadcn/ui, MUI, and Next.js place token/theme files under `src/`. `docs/` is exclusively for human-readable documentation.

### 5.2 Design Token Definition

Design tokens define design values such as colors, typography, and spacing as CSS Custom Properties.

```
# Create design token file
/feature-dev "Define the project design tokens in src/styles/design-tokens.css.
- Color palette (Primary, Secondary, Neutral, Semantic)
- Typography (Font Family, Size Scale, Weight, Line Height)
- Spacing (4px-based grid: 4, 8, 12, 16, 24, 32, 48, 64)
- Breakpoints (Mobile: 375px, Tablet: 768px, Desktop: 1024px, Wide: 1440px)
- Shadows, border radius, transitions
Don't modify any code yet."
```

### 5.3 Component Style Guide

Document the design specifications for core UI components.

```
# Create component style guide
/feature-dev "Write a core component style guide in docs/design-system/components.md.
- Button (Primary, Secondary, Ghost, Danger — states: default, hover, active, disabled)
- Input (Text, Password, Search, TextArea — states: default, focus, error, disabled)
- Card, Modal, Toast/Alert
- Navigation (Header, Sidebar, Breadcrumb, Tab)
- Table, Pagination
- Each component must only use tokens from design-tokens.css
Don't modify any code yet."
```

### 5.4 Layout Grid System

```
# Define layout grid system
/feature-dev "Define the layout grid system in docs/design-system/layout-grid.md.
- 12-column grid (gutter: 16px mobile, 24px desktop)
- Page layout patterns (Sidebar + Content, Full-width, Centered)
- Responsive rules (mobile-first)
- Container max width
Don't modify any code yet."
```

### 5.5 Design System Preview Page Generation

Once design tokens, components, and the layout grid are defined, generate a **preview page that can be verified in an actual browser**. Since it is difficult to accurately judge colors, typography, and component states from documentation alone, a page that allows the DSA and the entire team to visually verify is needed.

> **Why is a preview page needed?**
> - Verify design token values (colors, fonts, spacing) through **actual rendering results**
> - **Interactively verify** each component state (default, hover, active, disabled)
> - DSA can **immediately test** responsiveness/accessibility via `chrome-devtools` MCP
> - Serves as the **baseline** for AI-generated UI in feature sprints

```
# Generate design system preview page
/frontend-design "Create a design system preview page that provides an at-a-glance view of
the design tokens from src/styles/design-tokens.css, component style guide from docs/design-system/,
and layout grid.
- Color palette swatches (all Primary, Secondary, Neutral, Semantic)
- Typography scale preview (each size/weight combination)
- Spacing system visualization (blocks for each 4px grid unit)
- Core component showcase (Button, Input, Card, Modal, Toast — all states included)
- Layout grid overlay (12-column grid visualization)
- Responsive breakpoint previews
- Must only use tokens from src/styles/design-tokens.css"
```

> **Preview Page Verification (led by DSA):**
> - Use `chrome-devtools` MCP to check rendering at each viewport (375px, 768px, 1024px, 1440px)
> - Check basic accessibility items such as color contrast ratios and focus indicators
> - If issues are found, modify design tokens or component guides and immediately reflect changes in the preview page

### 5.6 Design System Completion Checklist

- [ ] Color palette definition complete (accessibility contrast ratio 4.5:1 or higher)
- [ ] Typography scale definition complete
- [ ] Spacing system definition complete (4px or 8px based)
- [ ] Core component style guide complete
- [ ] Layout grid system definition complete
- [ ] **Design system preview page generated and DSA verification complete**
- [ ] Design references/moodboard collection complete (if applicable)

---

## 6. Blueprint Creation

Before implementing features, **design documents (Blueprints)** are written first. Blueprints are the core input for AI to generate accurate code, and are managed as **numbered directories** in `docs/blueprints/`.

> **Directory Structure**: Each feature blueprint is organized as a directory in the format `docs/blueprints/{NNN}-{feature-name}/` (e.g., `001-auth/`, `002-payment/`). The main design document is `blueprint.md`, and related supplementary files (diagrams, API specs, etc.) are placed in the same directory.

> **Core Principle**: Good blueprint = good code. Spec quality determines AI output quality.
> (1-2 hours with specs, 4-8+ hours without — see [Appendix D](#appendix-d-ai-agent-task-time-estimation-rationale))

### 6.1 Feature Design Document Creation

```
# Auto-generate design document for core feature
/feature-dev "Write a design document for a JWT-based user authentication system
at docs/blueprints/001-auth/blueprint.md.
- Include signup, login, token refresh, and RBAC authorization features
- Password hashing with bcrypt
- Access Token validity 30 minutes, Refresh Token 7 days
- Reference docs/database/database-design.md for DB schema
Don't modify any code yet."

# -> VA/DE directly opens and reviews/edits the generated docs/blueprints/001-auth/blueprint.md
# -> Proceed to the next step after DE approval
```

### 6.2 Blueprint Completion Checklist

- [ ] Feature design document complete (`docs/blueprints/{NNN}-{feature-name}/blueprint.md`)
- [ ] DE approval obtained

---

## 7. Database Design

Once the blueprint is complete, **reflect the required database tables in the central DB design document**. All table designs are managed in the single document `docs/database/database-design.md`.

> **Why a single document?**
> - AI can **recognize the entire table structure and relationships at once** for consistent design
> - Inter-table FK references, column duplication, and naming consistency can be verified in a single context

### 7.1 DB Design Document Update

```
# Blueprint-based DB table design
/feature-dev "Analyze the blueprint at docs/blueprints/001-auth/blueprint.md and
design the required database tables in docs/database/database-design.md.
- Derive required tables, columns, and relationships from the blueprint's functional requirements
- Also reflect FK relationships in the ERD and relationship summary sections for existing tables
- Comply with the standard terminology dictionary (use /lookup-term)
Don't modify any code yet."

# You can also specify tables directly for update
/feature-dev "Add/update the authentication module tables in
docs/database/database-design.md:
- TB_COMM_USER (users), TB_COMM_TRMS (terms), TH_COMM_USER_AGRE (consent history)
- Also reflect FK relationships in the ERD and relationship summary sections for existing tables
- Comply with the standard terminology dictionary (use /lookup-term)
Don't modify any code yet."

# Standard terminology lookup
/lookup-term 결제금액
/lookup-term 주문번호
```

### 7.2 International Code Standard Application (when applicable)

Apply when features require international codes such as phone number inputs, country/region selectors, and address forms.

| Standard | Purpose | DB Column Rule |
|----------|---------|---------------|
| ISO 3166-1 (alpha-2) | Country codes (`KR`, `US`, `JP`) | `NATN_CD CHAR(2)` |
| ISO 3166-2 | Region codes (`KR-11`, `US-CA`) | `RGN_CD VARCHAR(6)` |
| ITU-T E.164 | International phone numbers (`+821012345678`) | `INTL_TELNO VARCHAR(15)` |

```
/lookup-code KR
/lookup-code US-CA
/lookup-code +82
```

### 7.3 Migration SQL Creation

```
# Record migration SQL
/feature-dev "Write migration SQL for the order module tables added this time
from docs/database/database-design.md to docs/database/migration/v1.1.0-order.sql.
- Include CREATE TABLE statements + indexes + FK constraints
- Also write rollback SQL
Don't apply to the actual DB yet."
```

### 7.4 Database Design Completion Checklist

- [ ] Tables reflected in DB design document (`docs/database/database-design.md`)
- [ ] Standard terminology dictionary compliance verified (`/lookup-term`)
- [ ] International code standard application verified (if applicable)
- [ ] Migration SQL written

---

## 8. Blueprint-based Sprint Creation

Once the blueprint is complete, plan the sprint based on it. Use the `/sprint-init` command to initialize sprint documents and distribute the blueprint's features into the sprint backlog.

### 8.1 Sprint Initialization

```
# Generate sprint documents (prompt map, progress tracker, retrospective template)
/sprint-init 1
```

> Generated files:
> - `docs/sprints/sprint-1-auth/prompt-map.md` — Feature-specific prompt plan
> - `docs/sprints/sprint-1-auth/progress.md` — Progress tracking table
> - `docs/sprints/sprint-1-auth/retrospective.md` — Retrospective template

### 8.2 Sprint Planning (1 hour)

#### Preparation (day before Planning, executed by VA)

```
/feature-dev "Analyze the technical complexity of the candidate backlog items for this sprint:
1. User Authentication (OAuth 2.0 + JWT)
2. Payment Dashboard
3. Notification Settings Page
Summarize dependencies with the existing codebase, estimated work scope, and risk factors.
Don't modify any code yet."
```

#### Planning Meeting (1 hour)

| Time | Activity | Participants |
|------|----------|-------------|
| 10 min | Review AI analysis report (replaces story point estimation) | VA, PE |
| 20 min | Confirm business priorities with DE and agree on sprint goal | DE, VA |
| 20 min | Discuss prompt design direction per item + DSA shares design direction | VA, PE, DSA |
| 10 min | Finalize sprint backlog | All |

### 8.3 Prompt Map Creation

Decompose each blueprint feature into prompt units and record them in `prompt-map.md`.

```markdown
# Sprint 1 Prompt Map

## Sprint Goal
[Describe the business value to be achieved in this sprint]

## Feature 1: User Authentication
### 1.1 Blueprint Reference
- docs/blueprints/001-auth/blueprint.md
- docs/database/database-design.md (authentication module)

### 1.2 Implementation Prompt
/feature-dev "Strictly follow the content of docs/blueprints/001-auth/blueprint.md and
docs/database/database-design.md to proceed with development."

## Feature 2: Payment Dashboard
### 2.1 Blueprint Reference
- docs/blueprints/002-payment-dashboard/blueprint.md

### 2.2 Implementation Prompt
/feature-dev "Strictly follow the content of docs/blueprints/002-payment-dashboard/blueprint.md and
docs/database/database-design.md to proceed with development."
```

### 8.4 Backlog Refinement (30 min)

```
# Pre-AI analysis (before Refinement)
/feature-dev "Analyze the following backlog items:
1. Order cancellation/refund process
2. Admin dashboard statistics page
3. User notification settings management
Summarize relevance to the existing codebase, technical risks, and prerequisites.
Don't modify any code yet."

# Refinement Meeting (30 min)
# +-- Review AI analysis results
# +-- Confirm business value/priorities with DE
# +-- Split items if needed
```

---

## 9. Implementation

Implement actual code according to the sprint prompt map. During implementation, **Gate 1 (write-time)** quality gates are automatically applied.

### 9.1 Design Document-based Implementation

```
/feature-dev "Strictly follow the content of docs/blueprints/001-auth/blueprint.md and
docs/database/database-design.md to proceed with development. For tests, refer to
docs/tests/test-cases/sprint-1/auth-test-cases.md, and after implementation
is complete, run all tests and report results to docs/tests/test-reports/."
```

> **What is automatically executed with this single prompt:**
> 1. `code-explorer` analyzes the existing codebase (2-3 in parallel)
> 2. Clarification questions (edge cases, business rule confirmation)
> 3. `code-architect` presents implementation plans (2-3 in parallel)
> 4. Code writing after approval
>    - `astra-methodology` auto-checks forbidden words/naming (PostToolUse hooks)
>    - `security-guidance` auto-blocks security patterns (PreToolUse hooks)
>    - `coding-convention` skill auto-applies conventions
> 5. `code-reviewer` runs quality checks (3 in parallel)
> 6. Completion summary document generated

### 9.2 UI Implementation

When frontend work is requested, the `frontend-design` skill is automatically activated to generate production-level UI.

```
# Specifying an aesthetic direction yields better results
"Create a payment dashboard.
- Real-time payment status (today's count/amount)
- Daily revenue chart (last 30 days)
- Recent transaction list (with pagination)
- Dark mode default, minimalist style
- Must use the token system from src/styles/design-tokens.css"

# Various aesthetic direction examples
"Create a brutalist style portfolio page"
"Create an art deco, luxurious product detail page"
```

### 9.3 Real-time Verification (chrome-devtools MCP)

```
# Check layout
"Take a snapshot of the current page and check the layout"

# Verify API behavior
"Check the network requests to verify that API calls are working properly"

# Check for errors
"Check if there are any errors in the console"

# Check responsiveness (viewport switching)
"Switch to mobile viewport (375x667) and check the layout"
```

### 9.4 Latest API Reference (context7 MCP)

```
"use context7 - How to make async HTTP requests with WebClient in Spring Boot 3"
"use context7 - How to use transactions in Prisma"
"use context7 - Server Actions syntax in Next.js 15"
```

### 9.5 Commit

```
# Commit after each feature completion
/commit
```

### 9.6 Gate 1: WRITE-TIME (Automatically Applied)

Quality gates automatically applied to all code writing (Write/Edit) during implementation.

| Tool | Check Content | Behavior |
|------|--------------|----------|
| `security-guidance` | 9 security patterns (eval, innerHTML, etc.) | PreToolUse hook, **blocks** (exit 2) |
| `astra-methodology` | Forbidden words + naming rules | PostToolUse hook, warning (exit 0) |
| `hookify` | Project-specific custom rules | PreToolUse/PostToolUse hooks |
| `coding-convention` skill | Java/TS/RN/Python/CSS/SCSS convention auto-apply | Skill (auto-detected) |
| `data-standard` skill | Public data standard terminology dictionary application | Skill (auto-detected for DB code) |
| `code-standard` skill | ISO 3166-1/2, ITU-T E.164 standard application | Skill (auto-detected for phone/country/address) |

### 9.7 Requirements Change Response

Follow this procedure when requirements change mid-sprint.

```
# 1. Impact analysis (30 min - 1 hour)
/feature-dev "A request has come in to add 'simple payment (KakaoPay)' to payment methods.
Reference the existing codebase and docs/database/database-design.md to
analyze the impact scope on the payment module.
Don't modify any code yet."

# 2. Blueprint modification (1-2 hours)
# -> Add simple payment section to docs/blueprints/003-payment/blueprint.md
# -> Reflect table changes in docs/database/database-design.md

# 3. Code implementation (4-8 hours)
/feature-dev "Reflect the updated content of docs/blueprints/003-payment/blueprint.md and
docs/database/database-design.md to implement the simple payment (KakaoPay) feature.
Use the PaymentProvider pattern to avoid impacting existing payment logic."

# 4. Automated quality verification (30 min - 1 hour)
/code-review
```

---

## 10. Test Scenario Creation

Generate E2E test scenarios based on features implemented in the sprint. The `/test-scenario` command analyzes blueprints, DB design, routes, and API endpoints to automatically create comprehensive test scenarios.

### 10.1 E2E Test Scenario Generation

```
# Auto-generate E2E scenarios based on blueprints, DB, and routes
/test-scenario
```

> Items automatically analyzed by `/test-scenario`:
> - `docs/blueprints/{NNN}-{feature-name}/` — Feature requirements
> - `docs/database/database-design.md` — Data model
> - Routes/API endpoints — Screen flows
> - Existing test code — Missing scenarios

### 10.2 Example: Sprint 1 Test Scenario Creation

This is an example of creating test scenarios with the `/test-scenario` command after authentication feature implementation is complete in Sprint 1.

```
# Auto-generate Sprint 1 test scenarios
/test-scenario Write test scenarios for Sprint 1.

# -> Tasks automatically performed by /test-scenario:
# 1. Scan docs/blueprints/{NNN}-*/ — Collect Sprint 1 feature requirements
# 2. Analyze docs/database/database-design.md — Understand related table structures
# 3. Explore src/ routes/API endpoints — Map screen flows and API paths
# 4. Check existing test code — Identify missing scenarios
#
# -> Generated result: Test scenario documents created in docs/tests/test-cases/sprint-1/
#   - E2E scenarios (signup -> login -> token refresh -> authorization verification flow)
#   - Feature-specific test cases (Given-When-Then format)
#   - Edge cases and error scenarios
```

---

## 11. Test Execution

Execute actual tests based on test scenarios. The `/test-run` command automatically performs server startup + Chrome MCP integration testing.

### 11.1 Integration Test Execution

```
# Automatic server startup + Chrome MCP integration testing
/test-run

# -> Server auto-start + log monitoring
# -> Page verification (snapshots, layout)
# -> API behavior check (network requests)
# -> Performance measurement (Core Web Vitals)
# -> Console error check
```

### 11.2 Manual Detailed Verification

```
# API integration test
"Test the integration between the payment API and order API. Monitor network requests and verify responses."

# DB data integrity check
"Verify that the FK relationship definitions in docs/database/database-design.md match the actual DB schema"

# Performance profiling
"Run a performance trace on the entire page and analyze bottlenecks"

# Cross-browser/responsive test
"Switch to mobile viewport (375x667) and check the layout"
"Switch to tablet viewport (768x1024) and check"
```

### 11.3 Test Result Report

```
/feature-dev "Write the complete test execution results to docs/tests/test-reports/sprint-1-report.md.
Include the following:
- Module-level test pass/fail status
- Test coverage summary
- Issues found and remediation actions
- Achievement rate against docs/tests/test-strategy.md targets"
```

### 11.4 Example: Sprint 1 Test Execution

This is a complete flow example of performing actual tests after test scenarios have been written for the authentication feature in Sprint 1.

#### Step 1: Automated Integration Test Execution

```
# Automatic server startup + Chrome MCP integration testing
/test-run

# -> Automated execution flow:
# 1. Server auto-start + log monitoring
# 2. Navigate to signup page -> fill form -> submit -> verify success
# 3. Navigate to login page -> authenticate -> verify token issuance
# 4. Check network requests (verify POST /auth/signup, POST /auth/login responses)
# 5. Confirm 0 console errors
# 6. Performance measurement (Core Web Vitals)
```

#### Step 2: Manual Detailed Verification

```
# Verify authentication API endpoint behavior
"Test the signup -> login -> token refresh flow in order.
Check the network requests and responses at each step and report the results."

# Edge case verification
"Try logging in with an incorrect password. Verify the error response is correct."
"Call a protected API with an expired Access Token. Verify a 401 response is returned."

# Responsive check (login/signup forms)
"Switch to mobile viewport (375x667) and check the login page layout"

# DB data integrity check
"Verify that data was correctly inserted into the TB_COMM_USER table after signup"
```

#### Step 3: Test Result Report Creation

```
/feature-dev "Write the complete test execution results to docs/tests/test-reports/sprint-1-report.md.
Include the following:
- Authentication module test pass/fail status
- Test coverage summary (target: 70%+)
- Issues found and remediation actions
- Achievement rate against docs/tests/test-strategy.md targets"

# -> Example generated result (docs/tests/test-reports/sprint-1-report.md):
#
# ## Test Result Summary
# | Module      | Total | Pass | Fail | Coverage |
# |-------------|-------|------|------|----------|
# | Auth        | 15    | 14   |  1   | 82%      |
# | RBAC        | 8     |  8   |  0   | 78%      |
#
# ## Issues Found
# - ISS-001: Generic error message on Refresh Token expiration -> Fixed
#
# ## Achievement vs. Targets
# - Coverage target 70% -> Actual 80%
# - 100% coverage of high-risk scenarios
```

---

## 12. PR / Review

Once implementation and testing are complete, create a PR and perform code review. The `/pr-merge` command handles the entire commit -> PR creation -> review -> fix -> merge cycle.

### 12.1 PR Creation + Code Review

```
# Method 1: Full automated cycle (commit -> PR -> review -> fix -> merge)
/pr-merge

# Method 2: Step-by-step manual execution
/commit-push-pr          # Commit + push + PR creation
/code-review             # 5-agent parallel code review (only reports issues with 80+ confidence)
```

### 12.2 Design Review (led by DSA)

When UI features are included, the DSA performs design review.

```
[Design Review]
  +-- DSA checks actual screens via chrome-devtools MCP
  |   +-- Verify design token compliance
  |   +-- Check responsive layout (viewport switching)
  |   +-- Basic accessibility check
  |
  +-- Issue fixes
      +-- DSA: "This button color doesn't match the token", "Margins don't align to 8px grid"
      +-- PE: Reflect design feedback in prompt -> AI regeneration (5-10 min)
      +-- DSA: Immediately verify fixed result -> Approve
```

### 12.3 Gate 2: REVIEW-TIME

| Tool | Check Content |
|------|--------------|
| `feature-dev` (built-in code-reviewer) | Code quality/bugs/conventions (3 agents in parallel) |
| `/code-review` | CLAUDE.md compliance, bugs, history analysis (5 agents in parallel, 80+ score filtering) |
| `blueprint-reviewer` agent | Design document quality/consistency verification (Sonnet, read-only) |
| `test-coverage-analyzer` agent | Test strategy/coverage analysis (Haiku, read-only) |
| `convention-validator` agent | Coding convention verification (Haiku, read-only) |

### 12.4 Gate 2.5: DESIGN-TIME (DSA Review)

| Review Item | Verification Method |
|-------------|-------------------|
| Design token compliance | `chrome-devtools` snapshot + `design-token-validator` agent (Haiku, auto-verification) |
| Component consistency | Screen-by-screen comparison |
| Responsive layout | `chrome-devtools` viewport switching |
| Basic accessibility check | Color contrast, focus verification |

When issues are found: DSA feedback -> PE prompt modification -> AI regeneration -> DSA re-review (completed within 1 hour)

### 12.5 Additional Quality Checks

```
/check-convention src/      # Coding convention check
/check-naming src/entity/   # DB naming standard check
```

### 12.6 Example: Sprint 1 PR and Review Execution

This is a complete flow example from PR creation to merge after authentication feature implementation is complete in Sprint 1.

#### Step 1: Commit + PR Creation + Code Review + Merge (Automated)

```
# Execute the entire cycle automatically with a single /pr-merge
/pr-merge

# -> Automated execution flow:
# 1. Commit changes (auto-generated commit message)
# 2. Push feature branch (feature/sprint-1-auth -> origin)
# 3. Create PR (Sprint 1 authentication feature implementation)
# 4. Code review (5 agents in parallel — only reports 80+ confidence issues)
# 5. Auto-fix discovered issues
# 6. Re-review -> merge on pass
```

#### Step 2: Step-by-step Manual Execution (when fine-grained control is needed)

```
# Step 1: Commit + push + PR creation
/commit
git push -u origin feature/sprint-1-auth
gh pr create --title "feat: Sprint 1 user authentication implementation" --body "## Summary
- JWT-based signup/login/token refresh implementation
- RBAC authorization management
- Compliant with docs/blueprints/001-auth/blueprint.md design

## Test plan
- [ ] Unit test pass confirmation
- [ ] API integration test confirmation
- [ ] Security pattern check pass"

# Step 2: Code review (5 agents in parallel)
/code-review

# Step 3: Review results and fix issues
# -> Only high-confidence issues (80+) are reported, so focus on critical items

# Step 4: Quality checks
/check-convention src/
/check-naming src/entity/

# Step 5: Commit fixes + re-review
/commit
/code-review

# Step 6: Merge
gh pr merge --squash
```

#### Step 3: Design Review (when UI is included, led by DSA)

```
# DSA checks actual screens via chrome-devtools MCP
"Take a snapshot of the login page and verify design token compliance"
"Switch to mobile viewport (375x667) and check the login form layout"

# Reflect DSA feedback
# -> "The error state color of the password input field doesn't match the token"
# -> PE modifies prompt -> AI regeneration (5-10 min) -> DSA re-review
```

#### Step 4: Gate 2 Quality Verification Result Example

```
[Code Review Results — Sprint 1 Authentication Feature]
+---------------------------------------------+
| code-reviewer (3 agents)       PASS          |
| convention-validator           0 violations  |
| blueprint-reviewer             Design match  |
| test-coverage-analyzer         Coverage 82%  |
| security-guidance              0 issues      |
+---------------------------------------------+
-> All Gate 2 passed — Staging merge ready
```

---

## 13. Staging Branch Merge

Merge feature branches that passed testing into the staging (staging/develop) branch.

### 13.1 Pre-merge Quality Check

```
# Final coding convention check
/check-convention src/

# DB naming standard check
/check-naming src/entity/

# Confirm 0 console errors
"Check if there are any errors in the console"
```

### 13.2 Staging Branch Merge

```
# PR creation -> review -> merge automation (targeting staging/develop branch)
/pr-merge
```

> **Role of the staging branch:**
> - Integration environment for user acceptance testing (UAT)
> - After all feature branches are merged into staging, actual user testing proceeds
> - Final verification stage before main branch merge

---

## 14. User Testing

In the staging environment, **actual users (DE, stakeholders)** directly verify the system. This covers **domain expert judgment and usability evaluation** -- areas that AI cannot replace.

### 14.1 Sprint Review (1 hour)

```
[Sprint Review]
  +-- 30 min: Real-time demo (chrome-devtools MCP)
  |   +-- No separate demo preparation needed — demo immediately from staging environment
  |   +-- Real-time viewport switching across devices (mobile/tablet/desktop)
  |   +-- Real-time network request verification (proving API behavior)
  |   +-- Share performance trace results
  |
  +-- 30 min: DE feedback + immediate implementation
      +-- DE: "Please change this part like this"
      +-- PE: Modify prompt -> AI re-implementation (5-10 min)
      +-- Demo changed results immediately
```

### 14.2 User Acceptance Testing (UAT)

DE and stakeholders test directly in the staging environment.

**UAT Checklist:**
- [ ] Core business scenario behavior verified
- [ ] Data integrity verified (in a production-like data environment)
- [ ] UI/UX usability evaluation
- [ ] Edge cases and exception scenarios verified
- [ ] Perceived performance verified (response speed, page loading)

### 14.3 Feedback Implementation

Issues found during user testing are either fixed immediately or registered in the next sprint backlog.

| Issue Type | Response | Time |
|------------|----------|------|
| Immediately fixable | PE modifies prompt -> AI re-implementation | 30 min - 2 hours |
| Requires design change | Modify blueprint -> Reflect in next sprint | Registered in backlog |
| Requirements change | Impact analysis -> DE priority decision | 1-2 days |

### 14.4 Sprint Retrospective (30 min)

```
[AI-Enhanced Retrospective]
  +-- 10 min: Automatic analysis based on sprint data (sprint-analyzer agent, Sonnet)
  |   +-- Repeated issue patterns from code-review
  |   +-- security-guidance blocking history
  |   +-- astra-methodology violation frequency
  |   +-- Commit pattern/rhythm analysis
  |
  +-- 10 min: Team discussion (areas AI cannot catch)
  |   +-- Focus on domain logic misunderstandings, communication issues, etc.
  |
  +-- 10 min: Improvement automation
      +-- /hookify [Convert repeated mistakes from this sprint into rules]
      +-- CLAUDE.md updates
      +-- Improve next sprint prompt templates
```

**Retrospective hookify usage examples:**
```
# Convert repeated mistakes from this sprint into rules
/hookify Do not expose stack traces in error responses
/hookify Do not include sensitive information (passwords, tokens) in API responses

# Auto-detection based on conversation analysis (run without arguments)
/hookify
# -> conversation-analyzer agent detects repeated mistakes from recent conversations
```

---

## 15. Main Branch Merge

Merge the staging branch that passed user testing into the main (main/master) branch. Execute the final quality gate (Gate 3) and prepare for release.

### 15.1 Gate 3: BRIDGE-TIME (Final Quality Gate)

```
# Full code quality check
/code-review
/check-convention src/
/check-naming src/entity/

# Confirm 0 console errors
"Check if there are any errors in the console"

# DSA final design review (overall screen consistency)
# quality-gate-runner agent executes Gate 1-3 integration (Sonnet, read-only)
```

### 15.2 Quality Gate Pass Criteria Summary

| Gate | Pass Criteria | Action When Blocked |
|------|--------------|-------------------|
| Gate 1 | 0 security-guidance warnings, 0 forbidden words | Fix immediately and rewrite |
| Gate 2 | 0 high-confidence code-review issues, 70%+ coverage | Decide fix now / fix later |
| Gate 2.5 | DSA design review approval | Modify prompt -> regenerate -> re-review |
| Gate 3 | 0 convention/naming violations, 0 console errors | Batch fix before deployment |

### 15.3 Main Branch Merge

```
# Staging -> main branch merge
/pr-merge
```

### 15.4 Release Artifact Generation

```
# Auto-generate operations manual
/feature-dev "Write a project operations manual at docs/delivery/operation-manual.md.
Include deployment procedures, environment variables, monitoring points, and incident response guide.
Don't modify any code yet."

# Branch cleanup
/clean_gone
```

---

## Appendices

### Appendix A: Claude Code Tools Quick Reference

| Situation | Command/Tool | Notes |
|-----------|-------------|-------|
| Global dev environment setup | `/astra-setup` | Global settings, MCP, plugin auto-configuration |
| Quick reference guide | `/astra-guide` | Workflow, commands, quality gate summary |
| Project initial setup | `/project-init [project-name]` | Sprint 0 directory structure + template generation |
| Sprint 0 checklist | `/project-checklist` | Sprint 0 completion verification |
| Sprint initialization | `/sprint-init [N]` | Generate prompt map, progress tracker, retrospective template |
| Start feature design | `/feature-dev [description]` | 7-step automated workflow |
| Standard term lookup | `/lookup-term [Korean term]` | English abbreviation/domain/type |
| International code lookup | `/lookup-code [code]` | ISO 3166-1/2, E.164 (country/region/phone) |
| DB entity generation | `/generate-entity [Korean definition]` | Based on DB design doc, Java/TypeScript/SQL |
| E2E test scenario generation | `/test-scenario` | E2E scenarios based on blueprints, DB, routes |
| Integration test execution | `/test-run` | Server startup + Chrome MCP auto-verification |
| Coding standard check | `/check-convention [target]` | Java/TS/RN/Python/CSS/SCSS |
| DB naming check | `/check-naming [target]` | Based on standard terminology dictionary |
| Commit | `/commit` | Auto-generated message |
| PR creation | `/commit-push-pr` | Commit + push + PR combined |
| PR -> review -> merge automation | `/pr-merge` | Full cycle: commit -> PR -> review -> fix -> merge |
| Code review | `/code-review` | 5 agents in parallel |
| Hook rule creation | `/hookify [description]` | Behavior prevention rules |
| Hook rule list | `/hookify:list` | Current rule list |
| Latest docs lookup | `"use context7 - [question]"` | Library documentation |
| Browser check | `chrome-devtools` MCP | Snapshots/screenshots/performance |
| DB query | `postgres` MCP | Direct query execution |

### Appendix A-2: Agents Quick Reference

| Agent | Model | Gate | Role |
|-------|-------|------|------|
| `astra-validator` | Haiku | - | ASTRA methodology compliance check |
| `naming-validator` | Haiku | Gate 1/3 | DB naming standard verification (Gate 1: hook auto-warning, Gate 3: agent verification) |
| `convention-validator` | Haiku | Gate 1/2 | Coding convention verification (Gate 1: skill auto-apply, Gate 2: agent verification) |
| `blueprint-reviewer` | Sonnet | Gate 2 | Design document quality/consistency verification |
| `test-coverage-analyzer` | Haiku | Gate 2 | Test strategy/coverage analysis |
| `design-token-validator` | Haiku | Gate 2.5 | Design token system compliance auto-verification |
| `sprint-analyzer` | Sonnet | - | Sprint progress/retrospective auto-analysis |
| `quality-gate-runner` | Sonnet | Gate 3 | Gate 1-3 integrated execution |

> All agents are **read-only** (Write/Edit disabled) -- they only perform analysis and reporting.

### Appendix B: Prompt Writing Guide

**5 elements of a good prompt:**

1. **What**: Clear description of the feature to be built
2. **Why**: Business purpose and user value
3. **Constraint**: Technical constraints and performance requirements
4. **Reference**: Related design documents, existing code paths
5. **Acceptance**: Completion criteria and verification methods

```
BAD:
"Create a payment feature"

GOOD:
/feature-dev "Implement a payment processing module.
- Support card payment and bank transfer
- Integrate with PG provider API (Inicis)
- Auto-retry up to 3 times on payment failure
- Follow the design in docs/blueprints/003-payment/blueprint.md
- Reference docs/database/database-design.md for DB schema
- Write both unit tests and integration tests"
```

### Appendix C: Risk Management

| Risk | Probability | Impact | Mitigation Strategy |
|------|------------|--------|-------------------|
| AI hallucination (incorrect code generation) | Medium | Medium | Detected by Gate 2 code-review, verify latest API via context7 |
| Complex business logic misunderstanding | Medium | High | feature-dev Phase 3 clarification questions mandatory, DE participation |
| Claude API outage | Low | High | Maintain local dev environment in parallel, manual backup for core logic |
| Terms not registered in standard dictionary | Medium | Low | Generate abbreviations by combining words from standard_words.json |
| Undetected security vulnerabilities | Low | High | security-guidance 9 patterns + supplementary final security audit |
| 1-week sprint burnout | Medium | Medium | AI absorbs repetitive tasks, people focus on judgment/decision-making |
| Scrum ceremony neglect | Medium | Medium | Reduce time but always maintain the ceremonies themselves |

### Appendix D: AI Agent Task Time Estimation Rationale

The task time estimates in this document are based on actual research data and industry cases from 2025-2026.

#### Key Research Data

| Source | Key Finding | Application |
|--------|------------|-------------|
| [METR - Time Horizons](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) | 50% success rate baseline: Claude 3.7 Sonnet ~1 hour, GPT-5.2 ~6.5 hours (late 2025) | Autonomous execution time limits for complex tasks |
| [METR - Developer Study](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) | Experienced developers + AI tools (Cursor/Claude): 19% slower on ad-hoc usage for 2-hour tasks | Importance of structured workflows |
| [METR - Time Horizon Growth](https://metr.org/time-horizons/) | AI autonomous task time doubles every ~7 months, ~4 months during 2024-2025 | Estimated 2-4 hour autonomous tasks possible by 2026 |

#### Industry Cases

| Source | Key Finding | Application |
|--------|------------|-------------|
| [Faros AI - Best AI Coding Agents 2026](https://www.faros.ai/blog/best-ai-coding-agents-2026) | Cursor: strong for small-medium tasks, looping issues in large refactoring | Need to break tasks into smaller units |
| [Anthropic - Agentic Coding Trends 2026](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf) | 1 engineer + Claude Code = 1 month's work of a traditional team | Significant improvement with structured specs |
| [TELUS/Zapier cases](https://www.index.dev/blog/developer-productivity-statistics-with-ai-tools) | TELUS 30% deployment speed increase, 500K+ hours saved / Zapier 89% org adoption | Organization-level AI adoption effects |

#### Realistic Time Estimates by Task Type (Early 2026, Claude Opus 4.6 / Sonnet 4.5)

| Task Type | AI Autonomous Execution | Human Review/Modification | Total Time |
|-----------|------------------------|--------------------------|------------|
| Codebase analysis | 10-30 min | 30 min - 1 hour | 1-2 hours |
| Design document generation | 15-30 min | 1-2 hours | 1.5-3 hours |
| Simple feature implementation (CRUD) | 30 min - 1 hour | 1-2 hours | 2-3 hours |
| Medium feature implementation (auth, API integration) | 1-3 hours | 2-4 hours | 4-8 hours |
| Complex feature implementation (multi-service, complex business logic) | 3-6 hours | 4-8 hours | 1-2 days |
| Automated code review | 10-15 min | 10-20 min | 20-40 min |
| Unit test generation | Concurrent with code | 30 min - 1 hour | Concurrent with code |
| UI component generation | 15-30 min | 1-2 hours (DSA review) | 1.5-3 hours |
| Spec-based implementation (with specs) | 1-2 hours | 2-4 hours | 3-6 hours |
| Spec-less feature implementation (without specs) | 4-8 hours | 6-10 hours | 1-2 days+ |

> **Key Insight**: The quality of design documents (specs) is the decisive factor in AI task duration.
> A task achievable in 60 minutes with good specs can take 16+ hours without them.
> This is why ASTRA writes blueprints first.

#### Limitations of Time Estimates

- AI agent performance varies significantly depending on **model version, codebase size, and domain complexity**
- METR's "19% slower" finding is based on **ad-hoc AI usage**; **structured workflows** like ASTRA can achieve 30-60% time reduction
- AI autonomous task time is growing at **~2x every 7 months**, so the time estimates in this document need **re-evaluation every 6-12 months**
- Complex business logic, architecture decisions, and domain-specific verification remain **bottlenecked by human judgment**

### Appendix E: Sprint 0 Project Setup

Sprint 0 establishes the project foundation over 1 week. It is performed **only once** before all feature sprints.

#### Step 0.0: Development Environment Setup (Global)

> **Scope**: Per developer machine (one-time setup, applies to all projects)

```
# Step 1: Add plugin marketplace
claude plugin marketplace add https://github.com/ASTRA-TECHNOLOGY-COMPANY-LIMITED/astra-methodology.git

# Step 2: Install astra-methodology plugin
claude plugin install astra-methodology@astra

# Step 3: Global dev environment auto-setup (global settings, MCP servers, 9 plugins auto-installed)
/astra-setup
```

**Items automatically installed:**
- 9 required plugins (claude-code-setup, code-review, code-simplifier, commit-commands, feature-dev, frontend-design, hookify, security-guidance, context7)
- 3 MCP servers (chrome-devtools, postgres, context7)
- Global settings (Agent Teams, bypassPermissions, Always Thinking)

#### Step 0.1: Vision & Backlog (Day 1-2)

Establish the project vision through a kickoff meeting with DE and create the initial Product Backlog.

```
# Check latest documentation for the tech stack
"use context7 - Comparison of WebClient vs RestTemplate in Spring Boot 3. What is the latest recommended approach?"

# Pre-analysis of core features
/feature-dev "Analyze the overall architecture of the online payment system and
write it to docs/blueprints/overview.md. Don't modify any actual code yet."
```

#### Step 0.2: Design System Construction (Day 2-3) - Led by DSA

> For details, refer to [5. Design System Creation](#5-design-system-creation).

Build design tokens, component style guide, and layout grid system.

#### Step 0.3: Architecture & Standards (Day 3-4)

Create core feature design documents (see [6. Blueprint Creation](#6-blueprint-creation)), write the central DB design document (see [7. Database Design](#7-database-design)), and create the test strategy document (`docs/tests/test-strategy.md`).

#### Step 0.4: Guard Rails Setup (Day 4-5)

Pre-configure quality rules to be applied throughout sprints by writing CLAUDE.md + setting up hookify rules.

```
# Create project-specific custom rules
/hookify All API endpoints must include authentication middleware
/hookify Use a logger library instead of console.log
/hookify Use CSS Variables instead of hardcoded color values in CSS
```

**Sprint 0 Completion Checklist:**
- [ ] Initial Product Backlog created
- [ ] Design system construction complete (design tokens, component guide)
- [ ] Core feature design documents (MD) generated and DE approved
- [ ] Central DB design document written (`docs/database/database-design.md`)
- [ ] Test strategy document written (`docs/tests/test-strategy.md`)
- [ ] CLAUDE.md written (including design principles)
- [ ] hookify rules configured

> Sprint 0 verification: `/project-checklist`

### Appendix F: Project Template

#### F.1 Directory Structure

```
project-root/
├── CLAUDE.md                    # Project AI rules (critical!)
├── .claude/
│   ├── hookify.*.local.md       # Project-specific hookify rules
│   └── settings.json            # Project-specific Claude settings
│
├── docs/
│   ├── design-system/           # Design documentation (built by DSA during Sprint 0)
│   │   ├── components.md
│   │   ├── layout-grid.md
│   │   └── references/
│   │
│   ├── blueprints/              # Design documents (Living Documents)
│   │   ├── overview.md
│   │   ├── 001-auth/
│   │   │   └── blueprint.md
│   │   └── 002-payment/
│   │       └── blueprint.md
│   │
│   ├── database/                # Database-related documents
│   │   ├── database-design.md   # Central DB design document (all tables/ERD/FK)
│   │   ├── naming-rules.md      # DB naming rules and standard term mapping
│   │   └── migration/           # Migration history
│   │       └── v1.0.0.sql
│   │
│   ├── tests/                   # Test-related documents
│   │   ├── test-strategy.md     # Test strategy (unit/integration/E2E scope definition)
│   │   ├── test-cases/          # Feature-specific test case specifications
│   │   │   └── sprint-1/
│   │   │       └── auth-test-cases.md
│   │   └── test-reports/        # Sprint-specific test result reports
│   │       └── sprint-1-report.md
│   │
│   ├── sprints/                 # Sprint documents
│   │   ├── sprint-1-auth/
│   │   │   ├── prompt-map.md
│   │   │   ├── progress.md
│   │   │   └── retrospective.md
│   │   └── sprint-2-workspace/
│   │       └── prompt-map.md
│   │
│   └── delivery/                # Release Sprint artifacts
│       ├── operation-manual.md
│       └── quality-report.md
│
└── src/                         # Source code
    └── styles/
        └── design-tokens.css    # CSS Custom Properties — source code
```

#### F.2 Sprint Retrospective Template

```markdown
# Sprint [N] Retrospective

## AI Analysis Data
- code-review repeated issues: [auto-collected]
- security-guidance blocking count: [auto-collected]
- astra-methodology violation frequency: [auto-collected]

## Team Discussion (areas AI cannot catch)
### What went well (Keep)
-

### What to improve (Problem)
-

### What to try (Try)
-

## Automated Improvement Actions
- /hookify [Convert repeated mistakes from this sprint into rules]
- CLAUDE.md update details: [describe added rules]
```

### Appendix G: Expected Benefits

#### Quantitative Benefits

| Metric | ASTRA Target | Improvement Rate |
|--------|-------------|-----------------|
| Sprint cycle | 1 week (smaller increments, faster feedback) | 50% cycle reduction |
| Ceremony time per sprint | 4 hours | 67% reduction |
| Team size | 4-5 people | 50% reduction |
| Coding standard compliance rate | 95%+ (auto-enforced) | +30% improvement |
| Code review turnaround time | 20-40 min (automated) | 85-90% reduction |
| Requirements change response | 1-2 days | Significant reduction from 2+ weeks |
| Coding task time | 40-60% reduction vs. baseline | Based on METR research |
| Security vulnerability detection timing | At code write-time | Shift from post-hoc to proactive |
| Design document freshness | 100% (Living Documents) | +70% improvement |
| Definition of Done verification | Automated (Gate 1-3) | Shift from manual to automated |

#### Qualitative Benefits

1. **Focus on the essence of scrum**: Reduced ceremony time allows focus on "value delivery"
2. **Improved review culture**: Eliminating style/standard debates transforms reviews into business logic discussions
3. **Retrospective effectiveness**: From "We'll improve" to "Enforced via hookify rules"
4. **Increased DE engagement**: Real-time demos and immediate implementation make DE a true project partner
5. **Reduced technical debt**: Built-in quality at write-time eliminates "we'll fix it later"
6. **Easier knowledge transfer**: Living Documents minimize handover costs

### Appendix H: Cost Effectiveness

For details, refer to [2.6 Cost Effectiveness](#26-cost-effectiveness).
