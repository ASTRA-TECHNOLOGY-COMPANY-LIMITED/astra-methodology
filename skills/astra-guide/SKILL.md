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
Planning & design:
  /service-planner [feature]   Design Thinking planning → 6 markdown deliverables + design-system HTML mockups
  /blueprint [feature]         Blueprint (10 sections: data flow/schema/API/sequences/pseudocode/HITL Triggers).
                               v5.16+ one-flow: authors on the sprint branch, then continues through
                               implementation → test loop → /pr-merge in the same session (--design-only stops early).
  /handoff-publish [feature]   UX/UI/Dev/QA handoff package — 14 Screen-ID files ({feature}-handoff/)

Sprint & pipeline:
  /project-init [info]         Sprint 0 project init (Web/Mobile; structure, CLAUDE.md, design + blueprint templates)
  /astra-setup                 Global dev-environment setup
  /sprint-init [slug]          Start a sprint (adaptive isolation; --scaffold-only / --auto / --resume)
  /autorun [feature]           Mostly-unattended full pipeline: planning → blueprint → sprint → tests → /pr-merge
  /loop [target]               Target-driven convergence loop (evaluator-optimizer) for open-ended goals
  /pr-merge                    Commit → PR → code review → fix loop → merge → promotion (dev/staging/skip)
  /project-checklist           Sprint 0 completion verification

Quality & testing:
  /test-scenario [context]     Generate E2E test scenarios from blueprints/DB/routes/APIs
  /test-run [URL/scenario]     Launch server + real-browser integration test (single-pass; pipeline drives retries)
  /user-test                   UAT session (interactive or batch) → HTML report
  /uat-parallel                Parallel UAT via Playwright workers (isolated BrowserContext per worker)
  /check-convention [target]   Coding convention compliance check
  /check-naming [target]       DB naming standard check
  /skill-lint [path]           Validate a SKILL.md against the 13-item best-practices checklist

Design system (DESIGN.md SSoT):
  /design-init                 Create/update DESIGN.md + regenerate design-tokens.css (--regenerate-css / --from-refs)
  /design-extract [refs]       Extract OKLCH tokens/fonts/spacing from images/PDFs/URLs → extract report
  /design-redesign [target]    Audit + fix UI against DESIGN.md (--apply / --pr)
  /design-audit [target]       Lightweight token-violation report (no fixes; for CI/PR pre-checks)

Data & code standards:
  /lookup-term [Korean term]   Standard term → English abbreviation / domain / data type
  /lookup-code [country|code]  ISO 3166-1/2 country/region + ITU-T E.164 calling-code lookup
  /generate-entity [defn]      Standard-compliant DB entity code from Korean table/column definitions
  (automatic)                  coding-convention / data-standard / code-standard auto-apply on write/edit

Docs & content:
  /manual-generator [feature]  Service URL + docs → self-contained HTML manual (Chrome MCP screenshots)
  /generate-manual <url> <f>   Command wrapper that drives /manual-generator
  /catalog-generator           Product data → self-contained HTML catalog (AI imagery + sales strategy)

Meta / authoring:
  /skill-author                Author or refactor a SKILL.md (13-item best-practices checklist)
  /tool-author                 Author/validate LLM tool descriptions & input schemas (Anthropic/MCP/LangChain/Pydantic/Zod)
  /select-language [ko|vi|en]  Choose the working language for generated documents & user-facing messages
  /astra-guide [section]       This quick-reference guide
  (automatic)                  sprint-progress (file-event tracking) + screen-quality-loop (new-screen QA convergence)

External (bundled plugins, not ASTRA):
  /feature-dev [description]   Guided feature development workflow
  /code-review                 Multi-agent PR review
  /commit · /commit-push-pr · /clean_gone   Git helpers
```

Sprint isolation (v5.16+ adaptive):
```
- Default is IN-PLACE: the feat/sprint-<N>-<slug> branch is checked out directly in the main
  worktree — no separate worktree, no cd, and /pr-merge finalizes single-phase in the same session.
- Escalates to a WORKTREE (.astra-worktrees/sprint-*) only when isolation is actually needed:
  the main worktree is already occupied by another in-place sprint, the tree is dirty, or --isolated.
  Worktree mode keeps the v5.9 two-phase merge (Sprint Phase → cd to main → Main Phase).
- One-flow: /blueprint (or /sprint-init) runs design → implementation → test loop → /pr-merge in a
  single session; HITL fires only at design decisions, remaining Critical issues, and merge/promotion.
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
