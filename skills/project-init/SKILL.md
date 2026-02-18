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
│   │   ├── overview.md
│   │   └── {NNN}-{feature-name}/    # e.g., 001-auth/
│   │       └── blueprint.md
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
| 디자인 시스템 | `docs/design-system/` | `/frontend-design` |
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
- 디자인 토큰: docs/design-system/design-tokens.css를 반드시 참조할 것
- 컬러는 CSS Variables (--color-*) 사용 필수, 하드코딩 금지
- 폰트 크기는 토큰 스케일 (--font-size-*) 사용 필수
- 스페이싱은 8px 그리드 시스템 (--spacing-*) 준수
- 반응형 브레이크포인트: 모바일(~767px), 태블릿(768~1023px), 데스크톱(1024px~)
- 디자인 시스템 프리뷰 페이지로 토큰/컴포넌트를 시각적으로 검증
- `design-token-validator` 에이전트로 자동 검증 (Gate 2.5)

## Prohibited Practices
- console.log 금지 (logger 사용)
- any 타입 금지
- 직접 SQL 금지 (ORM 사용)
- .env 파일 커밋 금지

## Testing Rules
- 모든 서비스 레이어에 단위 테스트 작성
- 최소 테스트 커버리지 70%
- 테스트 전략: `docs/tests/test-strategy.md`
- 테스트 케이스: `docs/tests/test-cases/sprint-N/` (스프린트별 관리)
- 테스트 보고서: `docs/tests/test-reports/` (커버리지 달성률 포함)
- `/test-scenario`로 E2E 시나리오 자동 생성, `/test-run`으로 Chrome MCP 통합 테스트

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

- **Spring Boot**: `@RestControllerAdvice` 전역 예외 처리, `@Valid` 입력 검증, Lombok 사용
- **NestJS**: `ExceptionFilter` 전역 예외 처리, `class-validator` DTO 검증, Prisma ORM
- **FastAPI**: `HTTPException` 사용, Pydantic 모델 검증, SQLAlchemy ORM
- **Next.js**: App Router 기본, Server Components 우선, Server Actions 활용
- **React**: 함수형 컴포넌트만 사용, 커스텀 훅 패턴
- **Vue 3**: Composition API 기본, `<script setup>` 사용

### Step 4: Create Design System Templates

Create the following files under `docs/design-system/`.

**design-tokens.css**: Base design token set (colors, typography, spacing, shadows, responsive breakpoints)

**components.md**: Core component style guide template (buttons, inputs, cards, modals, tables, navigation)

**layout-grid.md**: Layout grid system definition (column system, containers, behavior per breakpoint)

### Step 5: Create Blueprint Template

**docs/blueprints/overview.md**: Project overview document (vision, goals, module structure, tech stack decision rationale)

> **Blueprint Directory Convention**: Individual feature blueprints are organized as numbered directories under `docs/blueprints/`. Each directory uses the format `{NNN}-{feature-name}/` (e.g., `001-auth/`, `002-payment/`) and contains `blueprint.md` as the main design document along with any related supplementary files (diagrams, API specs, etc.).

### Step 6: Create Database Document Templates

**docs/database/database-design.md**: Central DB design document template (full ERD, common rules, module-specific tables, FK relationship summary)

**docs/database/naming-rules.md**: DB naming rules and standard terminology mapping document (table prefixes, column naming, standard terminology dictionary integration)

### Step 7: Create Test Document Template

**docs/tests/test-strategy.md**: Test strategy document (test level definitions, coverage goals, test environments, naming conventions, automation scope)

### Step 8: Create Sprint Template

**docs/sprints/sprint-1/prompt-map.md**: First sprint prompt map template

**docs/sprints/sprint-1/progress.md**: First sprint progress tracker (template format with placeholder features — features will be populated when the sprint is actually planned)

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
- docs/sprints/ (sprint prompt maps, progress trackers, retrospectives)
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
