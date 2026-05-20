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
HANDOFF_PROCESS_GUIDE v1.1 — Screen ID 기반 협업
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3 Core Principles:
  1. Screen ID 기반 협업 (DOMAIN-PAGE-SECTION-UC)
       예: ACAD-EXPERT-DETAIL-UC03
  2. Single Source of Truth
       1-screen-registry.md이 유일한 ID 기준
       UX만 발행 권한 — UI/Dev/QA는 임의 생성 금지
  3. 상태 기반 설계
       State (LOADING/EMPTY/DEFAULT/ERROR) × Permission × Device

RACI:
  Screen ID 발행    → UX (Owner)
  Handoff 패키지 작성 → UX (Owner)
  Figma 프레임       → UI Designer (Owner)
  코드 구현          → Developer (Owner)
  ID 변경/추가 결정   → UX (Owner)
  검증/누락 체크      → QA (Owner)

Handoff Package (branch root: {feature}-handoff/):
  0-README.md              (가이드 + Quick Start)
  1-screen-registry.md     ★ SSoT — 화면 등록부
  2-flows.md               사용자 흐름
  3-state-matrix.md        상태 + 권한 정의
  4-edge-cases.md          예외/주의 케이스
  5-responsive-guide.md    반응형 기준
  6-component-specs.md     카드/컴포넌트 명세
  7-business-rules.md      화면별 비즈니스 규칙
  8-content-guide.md       UX Writing + 데이터 표시
  9-ia-sitemap.md          정보 구조 / 사이트맵
  10-personas.md           페르소나 / 핵심 시나리오
  11-decision-log.md       디자인 결정 이력
  DoD-CHECKLIST.md         단계별 완료 조건
  walkthrough.loom.md      설명 영상 링크
  screenshots/             화면 ID 기준 캡처

Workflow:
  /service-planner feature   → 기획 산출물 (docs/planner/...)
  /blueprint feature         → 청사진 (docs/blueprints/...) — data flow + schema + logic + Section 10 HITL Triggers
  /handoff-publish feature   → Handoff 패키지 생성
  UX: 1-screen-registry.md 보완 + Loom 녹화
  UI: Figma 프레임명 = Screen ID
  Dev: // @feature: SCREEN-ID 주석 + 상태 분기 + i18n 3개국어
  QA: DoD-CHECKLIST.md 기반 ID × 상태 × 권한 검증

Out of Scope (적용 안 함):
  - 1회성 마케팅/이벤트 페이지
  - 빠른 프로토타입 / A-B 테스트
  - 외부 임베드 (Notion/Slack)
  - 백오피스 어드민 (UX 협업 불필요)
  - 기존 기능 (큰 리뉴얼 시점에만 점진 적용)

Anti-patterns (PDF §23):
  모달/에러 누락, DEFAULT만 디자인, Mobile 누락,
  권한 UI 미반영, Figma/코드 ID 따로, 변경 통보 누락,
  카드 anatomy 제각각, 노출 조건 임의, 베트남어 잘림, a11y 미준수
```

### dod - Definition of Done (단계별 완료 조건)

```
19.1 UX DoD:
  [ ] Screen Registry 등록
  [ ] State Matrix 작성
  [ ] Permission Matrix 작성
  [ ] Business Rules 작성
  [ ] Edge Cases 정리
  [ ] Component Specs (신규 컴포넌트 시)
  [ ] Decision Log 갱신 (변경 발생 시)
  [ ] Loom 워크스루 녹화 (5~10분)

19.2 UI Designer DoD:
  [ ] 모든 ID에 Figma 프레임 생성 (프레임명 = ID)
  [ ] 모든 상태 (LOADING/EMPTY/DEFAULT/ERROR) 디자인
  [ ] 권한별 UI 차이 반영
  [ ] Mobile / Tablet 분기점 디자인
  [ ] 색상 대비 검증 (WCAG AA)
  [ ] Focus state 디자인
  [ ] 디자인 시스템 토큰만 사용

19.3 Developer DoD:
  [ ] // @feature: {SCREEN-ID} 주석
  [ ] 상태 분기 처리 (isLoading / isEmpty / isError)
  [ ] i18n 3개국어 (ko/en/vi) 등록
  [ ] 키보드 / Focus / ARIA 검증
  [ ] Lighthouse 90+ (모바일)
  [ ] npm run lint / npx tsc --noEmit 통과

19.4 QA DoD:
  [ ] 모든 ID × 상태 × 권한 검증
  [ ] 디바이스 매트릭스 (Chrome/Safari × Desktop/Tablet/Mobile)
  [ ] 다국어 3개 검증 (베트남어 길이 잘림)
  [ ] 접근성 (키보드 + 스크린 리더)
  [ ] 회귀 테스트
```

### principles - Behavioral Guardrails (LLM 코딩 4원칙)

```
LLM 코딩 실수를 줄이기 위한 행동 원칙
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
출처: forrestchang/andrej-karpathy-skills (MIT)
영감: Andrej Karpathy의 LLM 코딩 함정 관찰
트레이드오프: 속도보다 신중함 (caution over speed)

1. Think Before Coding (생각 먼저)
   - 가정을 명시화한다. 불확실하면 질문한다.
   - 여러 해석이 존재하면 침묵 속에 한 해석을 고르지 않는다.
   - 단순한 접근이 보이면 푸시백한다.
   - 불명확하면 멈추고 무엇이 혼란스러운지 명명한다.

2. Simplicity First (단순함 먼저)
   - 요청되지 않은 기능, 추상화, 유연성, 설정 가능성 금지
   - 일어날 수 없는 시나리오의 에러 처리 금지
   - 자가 점검: "시니어 엔지니어가 보면 과설계라 할까?"
   - 200줄로 작성한 것이 50줄로 가능했다면 다시 써라

3. Surgical Changes (외과적 변경)
   - 인접 코드 "개선" 금지, 무관한 리팩토링 금지
   - 기존 스타일을 따르라 (본인 취향 우선시 금지)
   - 무관한 데드 코드는 언급은 하되 삭제하지 말 것
   - 본인 변경으로 발생한 미사용 import만 제거
   - 변경된 모든 라인은 사용자 요청에 직접 추적 가능해야 함

4. Goal-Driven Execution (목표 기반 실행)
   - "검증 추가" → "잘못된 입력 테스트 작성하고 통과시켜라"
   - "버그 수정" → "재현 테스트 작성하고 통과시켜라"
   - "리팩토링" → "전후 모두 테스트 통과 보장하라"
   - 강한 성공 기준이 있으면 LLM이 독립 루프 가능
   - 약한 기준 ("일단 동작하게")은 발산을 부른다

적용 위치 (이 플러그인 내):
  - skills/coding-convention      모든 코드 작성/수정에 자동 적용
  - skills/pr-merge Step 8.2      이슈 자동 수정 시 외과적 변경
  - skills/service-planner Step 0  기획 시작 시 모호성 검증

적용 제외 (자동 빌더):
  /service-planner, /manual-generator, /catalog-generator,
  /handoff-publish, /project-init, /sprint-init, /autorun
  → 사용자가 명시 요청한 풀 스택 산출물이므로
     "Simplicity First" 범위 제한을 받지 않음
  → 단, 그 내부 개별 코드 작성에는 4원칙 그대로 적용
```

## Guide Display Rules

- If `$ARGUMENTS` matches one of the section names above (sprint, review, release, commands, gates, roles, handoff, dod, principles), display only that section
- If `$ARGUMENTS` is empty, display the full summary + commands section
- If `$ARGUMENTS` is "all", display all sections
