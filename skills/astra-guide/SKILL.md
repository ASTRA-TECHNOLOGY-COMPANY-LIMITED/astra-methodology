---
name: astra-guide
description: "ASTRA methodology quick reference guide. Displays workflow, command, and quality gate summaries."
argument-hint: "[sprint|review|release|commands|gates|roles]"
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
  /clean_gone                    Branch cleanup

Quality Rules:
  /hookify [description]         Create behavior prevention rule
  /hookify:list                  List current rules

Sprint Progress:
  (automatic)                    Sprint progress auto-tracking on file events
  /sprint-plan [number]           Sprint plan init (includes progress tracker)

ASTRA Tools:
  /project-init [project info]   Sprint 0 initial setup
  /astra-setup                   Global dev environment setup
  /sprint-plan [number]           Sprint planning & initialization
  /test-run [URL/scenario]         Server launch + Chrome MCP integration testing
  /project-checklist             Sprint 0 completion verification
  /astra-guide [section]         Quick reference guide
```

### gates - Quality Gates

```
Gate 1: WRITE-TIME (at write time, automatic)
  ├─ security-guidance: 9 security pattern blocks
  ├─ standard-enforcer: Forbidden word + naming check
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

## Guide Display Rules

- If `$ARGUMENTS` matches one of the section names above, display only that section
- If `$ARGUMENTS` is empty, display the full summary + commands section
- If `$ARGUMENTS` is "all", display all sections
