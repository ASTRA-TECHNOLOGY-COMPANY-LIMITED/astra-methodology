---
name: astra-guide
description: "ASTRA methodology quick reference guide. Displays workflow, command, quality gate, handoff process, and behavioral guardrail summaries."
argument-hint: "[sprint|review|release|commands|gates|roles|handoff|dod|principles]"
allowed-tools: Read
---

# ASTRA Quick Reference Guide

Displays the guide for the relevant section based on `$ARGUMENTS`.
If no arguments are provided, displays the full summary.

## Full Summary (when no arguments)

```
ASTRA: AI-augmented Sprint Through Rapid Assembly
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VIP Principles:
  V - Vibe-driven Development (convey your intent)
  I - Instant Feedback Loop (hourly feedback)
  P - Plugin-powered Quality (quality is built into the code)

Sprint cycle: 1 week
Team composition: VA(1) + PE(1~2) + DE(1) + DSA(1) = 4~5 members
```

## Section-specific Guides

### sprint - Weekly Schedule

```
Monday:    Sprint Planning (1 hour) + Feature Build start
Tue-Thu:   Feature Build (AI code generation + human verification iteration)
Thursday:  Design Review (DSA inspection, afternoon)
Friday:    Code Review + Sprint Review + Retrospective
```

### review - Review Process

```
Design Review (1 hour - led by DSA):
  30 min: DSA inspects AI-generated UI (chrome-devtools)
  30 min: Fix design issues (PE modifies prompts → AI regenerates)

Code Review:
  /commit-push-pr        # Create PR
  /pr-merge       # Commit→review→fix→merge full cycle
  /code-review           # 5-agent parallel review
  /check-convention src/ # Coding standard check
  /check-naming src/entity/ # DB naming check
```

### release - Release Sprint

```
Step R.1: System Integration Testing
  /test-run                       Server launch + Chrome MCP integration testing
  - API integration testing
  - DB data consistency verification
  - Performance profiling
  - Cross-browser/responsive testing

Step R.2: Final Quality Gate (Gate 3)
  /code-review
  /check-convention src/
  /check-naming src/entity/

Step R.3: Deployment & Handover
  - Auto-generate operations manual
  - /clean_gone (branch cleanup)
```

### commands - Command Quick Reference

```
Feature Development:
  /feature-dev [description]     7-step feature development workflow
  /lookup-term [Korean term]     Standard term lookup
  /generate-entity [definition]  DB entity generation

Code Quality:
  /check-convention [target]     Coding standard check
  /check-naming [target]         DB naming check
  /code-review                   5-agent parallel review

Git Workflow:
  /commit                        Auto commit
  /commit-push-pr                Commit+push+PR batch
  /pr-merge               Commit→review→fix→merge full cycle
  /clean_gone                    Branch cleanup

Quality Rules:
  /hookify [description]         Create behavior prevention rule
  /hookify:list                  List current rules

Sprint Progress:
  (automatic)                    Sprint progress auto-tracking on file events
  /sprint-init [number]           Sprint plan init (includes progress tracker)

Planning:
  /service-planner [feature]     Design Thinking planning (6 deliverables: market analysis, interview, requirements+KPI, use cases+journey map, IA+wireframe, features+risk)
  /blueprint [feature]           Blueprint authoring — 10 sections (data flow / schema DDL / API contract / sequence / pseudocode logic / HITL Triggers). No implementation code. Auto-loads /service-planner artifacts. /feature-dev reads Section 10 to gate HITL during implementation.
  /handoff-publish [feature]     Generate UX/UI/Dev/QA handoff package ({feature}-handoff/ with 14 files)

Slack Integration:
  /slack-import [channel]     Slack messages → blueprints + sprint plan
  /extract-backlog [channel]       Extract backlog items from Slack channel

ASTRA Tools:
  /project-init [project info]   Sprint 0 initial setup
  /astra-setup                   Global dev environment setup
  /sprint-init [number]           Sprint planning & initialization
  /test-run [URL/scenario]         Server launch + Chrome MCP integration testing
  /project-checklist             Sprint 0 completion verification
  /astra-guide [section]         Quick reference guide
```

### gates - Quality Gates

```
Gate 1: WRITE-TIME (at write time, automatic)
  ├─ security-guidance: 9 security pattern blocks
  ├─ astra-methodology: Forbidden word + naming check
  ├─ hookify: Project-specific custom rules
  └─ coding-convention: Convention auto-application

Gate 2: REVIEW-TIME (at review time)
  ├─ feature-dev code-reviewer: Code quality/bugs
  └─ /code-review: 5-agent parallel, 80+ score filtering

Gate 2.5: DESIGN-TIME (design inspection)
  └─ DSA manual inspection (design tokens, components, responsiveness, accessibility)

Gate 3: BRIDGE-TIME (at release time)
  ├─ /check-convention src/
  ├─ /check-naming src/entity/
  └─ chrome-devtools: UI/performance/network/console errors
```

### roles - Role Definitions

```
VA (Vibe Architect) - 1 senior developer
  Scrum master + AI orchestration + architecture decision-making

PE (Prompt Engineer) - 1~2 junior developers
  Prompt writing + AI output verification

DE (Domain Expert) - 1 client-side business representative
  Requirements delivery + priority management + real-time feedback

DSA (Design System Architect) - 1 designer
  Design system building + AI-generated UI inspection
```

### handoff - UX / UI / Dev / QA Handoff Process (v1.1)

```
HANDOFF_PROCESS_GUIDE v1.1 — Screen ID-based collaboration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3 Core Principles:
  1. Screen ID-based collaboration (DOMAIN-PAGE-SECTION-UC)
       Example: ACAD-EXPERT-DETAIL-UC03
  2. Single Source of Truth
       1-screen-registry.md is the only ID source
       Only UX may issue IDs — UI/Dev/QA may not create them arbitrarily
  3. State-based design
       State (LOADING/EMPTY/DEFAULT/ERROR) × Permission × Device

RACI:
  Screen ID issuance       → UX (Owner)
  Handoff package authoring → UX (Owner)
  Figma frames              → UI Designer (Owner)
  Code implementation       → Developer (Owner)
  ID change/addition        → UX (Owner)
  Verification/gap check    → QA (Owner)

Handoff Package (branch root: {feature}-handoff/):
  0-README.md              (guide + Quick Start)
  1-screen-registry.md     SSoT — screen registry
  2-flows.md               user flows
  3-state-matrix.md        state + permission definitions
  4-edge-cases.md          exception / caution cases
  5-responsive-guide.md    responsive breakpoints
  6-component-specs.md     card / component specs
  7-business-rules.md      per-screen business rules
  8-content-guide.md       UX Writing + data display
  9-ia-sitemap.md          information architecture / sitemap
  10-personas.md           personas / core scenarios
  11-decision-log.md       design decision history
  DoD-CHECKLIST.md         stage-by-stage completion criteria
  walkthrough.loom.md      explanation video links
  screenshots/             captures indexed by Screen ID

Workflow:
  /service-planner feature   → planning deliverables (docs/planner/...)
  /blueprint feature         → Blueprint (docs/blueprints/...) — data flow + schema + logic + Section 10 HITL Triggers
  /handoff-publish feature   → generate Handoff package
  UX: refine 1-screen-registry.md + record Loom
  UI: Figma frame name = Screen ID
  Dev: // @feature: SCREEN-ID comments + state branching + i18n (3 languages)
  QA: verify ID × state × permission based on DoD-CHECKLIST.md

Out of Scope (does not apply):
  - One-off marketing / event pages
  - Quick prototypes / A-B tests
  - External embeds (Notion/Slack)
  - Back-office admin (UX collaboration not needed)
  - Existing features (apply incrementally only at major renewal points)

Anti-patterns (PDF §23):
  Missing modal/error states, designing DEFAULT only, missing Mobile,
  permission UI not reflected, separate Figma/code IDs, missing change notifications,
  inconsistent card anatomy, arbitrary visibility conditions, Vietnamese text truncation, a11y non-compliance
```

### dod - Definition of Done (stage-by-stage completion criteria)

```
19.1 UX DoD:
  [ ] Screen Registry entries
  [ ] State Matrix authored
  [ ] Permission Matrix authored
  [ ] Business Rules authored
  [ ] Edge Cases organized
  [ ] Component Specs (when new components are added)
  [ ] Decision Log updated (when changes occur)
  [ ] Loom walkthrough recorded (5~10 min)

19.2 UI Designer DoD:
  [ ] Figma frame created for every ID (frame name = ID)
  [ ] Every state (LOADING/EMPTY/DEFAULT/ERROR) designed
  [ ] Per-permission UI differences reflected
  [ ] Mobile / Tablet breakpoints designed
  [ ] Color contrast verified (WCAG AA)
  [ ] Focus state designed
  [ ] Only design system tokens used

19.3 Developer DoD:
  [ ] // @feature: {SCREEN-ID} comments
  [ ] State branching (isLoading / isEmpty / isError)
  [ ] i18n in 3 languages (ko/en/vi) registered
  [ ] Keyboard / Focus / ARIA verified
  [ ] Lighthouse 90+ (mobile)
  [ ] npm run lint / npx tsc --noEmit passing

19.4 QA DoD:
  [ ] Every ID × state × permission verified
  [ ] Device matrix (Chrome/Safari × Desktop/Tablet/Mobile)
  [ ] 3-language verification (Vietnamese text truncation)
  [ ] Accessibility (keyboard + screen reader)
  [ ] Regression tests
```

### principles - Behavioral Guardrails (4 LLM coding principles)

```
Behavioral principles to reduce LLM coding mistakes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source: forrestchang/andrej-karpathy-skills (MIT)
Inspired by: Andrej Karpathy's observations on LLM coding pitfalls
Trade-off: caution over speed

1. Think Before Coding
   - Make assumptions explicit. When uncertain, ask.
   - When multiple interpretations exist, do not silently pick one.
   - Push back when a simpler approach is visible.
   - When unclear, stop and name what is confusing.

2. Simplicity First
   - No unrequested features, abstractions, flexibility, or configurability
   - No error handling for scenarios that cannot occur
   - Self-check: "If a senior engineer saw this, would they call it over-engineered?"
   - If you wrote 200 lines and it could have been 50, rewrite it

3. Surgical Changes
   - No "improving" adjacent code, no unrelated refactoring
   - Follow the existing style (do not prioritize your taste)
   - Mention unrelated dead code but do not delete it
   - Remove only unused imports introduced by your own change
   - Every changed line must trace directly to the user's request

4. Goal-Driven Execution
   - "Add validation" → "Write a test for invalid input and make it pass"
   - "Fix bug" → "Write a reproduction test and make it pass"
   - "Refactor" → "Ensure tests pass both before and after"
   - With strong success criteria, the LLM can loop autonomously
   - Weak criteria ("just make it work") cause divergence

Application locations (within this plugin):
  - skills/coding-convention      Auto-applied to all code writing/modification
  - skills/pr-merge Step 8.2      Surgical changes during auto-fix of issues
  - skills/service-planner Step 0 Ambiguity validation at planning kickoff

Excluded (auto-builders):
  /service-planner, /manual-generator, /catalog-generator,
  /handoff-publish, /project-init, /sprint-init, /autorun
  → Generate full-stack deliverables explicitly requested by the user,
     so they are not bound by the "Simplicity First" scope limit
  → However, the four principles still apply to individual code written inside them
```

## Guide Display Rules

- If `$ARGUMENTS` matches one of the section names above (sprint, review, release, commands, gates, roles, handoff, dod, principles), display only that section
- If `$ARGUMENTS` is empty, display the full summary + commands section
- If `$ARGUMENTS` is "all", display all sections
