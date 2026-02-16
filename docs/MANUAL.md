# ASTRA: AI-augmented Sprint Through Rapid Assembly

**SPI 기반 AI 강화 스크럼 개발 방법론**

> ASTRA는 기존 SPI(Success Path Integration) 방법론의 애자일 스크럼 프로세스에
> Claude Code의 AI 에이전트 생태계를 결합하여, 스크럼의 잔존 낭비를 제거하고
> 바이브 코딩의 장점을 극대화하는 **AI 강화 스크럼(AI-Enhanced Scrum)** 방법론입니다.

---

## 목차

1. [방법론 개요](#1-방법론-개요)
2. [스크럼에서 ASTRA로의 진화](#2-스크럼에서-astra로의-진화)
3. [역할 정의](#3-역할-정의)
4. [Sprint 0: 프로젝트 셋업](#4-sprint-0-프로젝트-셋업)
   - [Step 0.0: 개발환경 설정 (전역)](#step-00-개발환경-설정-전역)
   - [Step 0.1: Vision & Backlog](#step-01-vision--backlog-day-1-2)
   - [Step 0.2: Design System 구축](#step-02-design-system-구축-day-2-3---dsa-주관)
   - [Step 0.3: Architecture & Standards](#step-03-architecture--standards-day-3-4)
   - [Step 0.4: Guard Rails 설정](#step-04-guard-rails-설정-day-4-5)
5. [품질 게이트](#5-품질-게이트)
   - [Gate 1: WRITE-TIME (작성 시점)](#gate-1-write-time-작성-시점)
   - [Gate 2: REVIEW-TIME (리뷰 시점)](#gate-2-review-time-리뷰-시점)
   - [Gate 2.5: DESIGN-TIME (디자인 검수 시점)](#gate-25-design-time-디자인-검수-시점)
   - [Gate 3: BRIDGE-TIME (릴리스 시점)](#gate-3-bridge-time-릴리스-시점)
6. [기능 스프린트 실행](#6-기능-스프린트-실행)
   - [6.1 주간 일정](#61-주간-일정)
   - [6.2 Sprint Planning](#62-sprint-planning-1시간)
   - [6.3 Feature Build](#63-feature-build-mondaythursday-오전)
   - [6.4 Daily Scrum → 비동기 AI 보고](#64-daily-scrum--비동기-ai-보고)
   - [6.5 Design Review & Code Review](#65-design-review-thursday-오후--code-review-friday-오전)
   - [6.6 Sprint Review](#66-sprint-review-friday-1시간)
   - [6.7 Sprint Retrospective](#67-sprint-retrospective-friday-30분)
   - [6.8 Backlog Refinement](#68-backlog-refinement-30분)
   - [6.9 요구사항 변경 대응](#69-요구사항-변경-대응)
7. [Release Sprint: 배포 준비](#7-release-sprint-배포-준비)
8. [프로젝트 템플릿](#8-프로젝트-템플릿)
9. [기대 효과](#9-기대-효과)
- [부록](#부록)

---

## 1. 방법론 개요

### ASTRA란?

**A**I-augmented **S**print **T**hrough **R**apid **A**ssembly

ASTRA는 "별(Astra, 라틴어)"이라는 의미를 담고 있으며, 프로젝트를 빠르게 목표 지점으로 이끄는 나침반 역할을 합니다.

### 핵심 철학

ASTRA는 **애자일 스크럼을 부정하지 않습니다.** 스크럼의 검증된 프레임워크를 유지하면서, AI 에이전트가 스크럼의 각 활동에서 발생하는 비효율을 흡수하여 더 빠르고 높은 품질의 결과물을 만드는 **진화된 스크럼**입니다.

**변한 것:** 스프린트 주기(2주→1주, 소규모 증분·빠른 피드백), 수동 작업의 AI 자동화(40~60% 시간 단축), 품질 게이트 내장
**변하지 않은 것:** 스크럼의 점진적 가치 전달, 투명성·검사·적응의 3기둥

### VIP 원칙

| 원칙 | 핵심 | 실현 도구 |
|------|------|----------|
| **V**ibe-driven Development | 코드를 작성하지 말고, 의도를 전달하라 | `feature-dev`, `frontend-design` |
| **I**nstant Feedback Loop | 스프린트 내 피드백 주기를 시간 단위로 단축 | `chrome-devtools` MCP, `code-review` |
| **P**lugin-powered Quality | 품질은 코드에 내장되는 것이다 | `standard-enforcer`, `security-guidance`, `hookify` |

### SPI와의 관계

| SPI 5단계 | ASTRA 구현 | 활용 도구 |
|-----------|-----------|----------|
| 1. Strategy | Product Vision + 기술 스택 검증 | `context7` MCP |
| 2. Process Map | Product Backlog 정제 + 자동 설계 문서 생성 | `feature-dev` Phase 1-4 |
| 3. Iterative Build | AI 병렬 구현 (1주 주기 스프린트) | `feature-dev` + `frontend-design` |
| 4. Integration | 실시간 통합 검증 | `chrome-devtools` MCP |
| 5. Success Launch | 자동 문서화 + 품질 리포트 | `feature-dev` Phase 7 |

| SPI 3S 원칙 | ASTRA 구현 | 활용 도구 |
|-------------|----------|----------|
| Standardization | 작성 시점 자동 강제 | `standard-enforcer` (PostToolUse 훅) |
| Scalability | 확장성 자동 검토 | `feature-dev` code-architect |
| Security | 보안 패턴 실시간 차단 | `security-guidance` (PreToolUse 훅) |

---

## 2. 스크럼에서 ASTRA로의 진화

이 섹션에서 기존 스크럼과의 모든 비교를 정리합니다. 이후 섹션부터는 ASTRA 자체의 실행 방법에 집중합니다.

### 2.1 핵심 변화 요약

```
기존 스크럼:
  Product Backlog → Sprint Planning → Sprint(2주) → Sprint Review → Retrospective
                                        │
                                   개발 → 테스트 → 리뷰 (수동, 직렬)

ASTRA:
  Product Backlog → Sprint Planning → Sprint(1주) → Sprint Review → Retrospective
       │                 │               │               │               │
    AI 정제          AI 추정         AI 병렬 실행      실시간 데모      AI 분석
  (code-explorer)  (자동 분석)    (개발+테스트+리뷰)  (chrome-devtools) (hookify)
```

### 2.2 활동별 비교

| 활동 | 기존 스크럼 | ASTRA | 단축 근거 |
|------|-----------|-------|----------|
| **스프린트 주기** | 2주 | 1주 (소규모 증분, 빠른 피드백) | AI가 개발+테스트+리뷰를 병렬 처리, 짧은 주기로 민첩성 향상 |
| **스토리 분석/설계** | 1~2일 | 2~4시간 | AI 분석 20~40분 + 인간 검토·보완 1~2시간 (`feature-dev` Phase 1-4) |
| **수동 코딩** | 5~7일 | 2~4일 | AI 코드 생성 1~3시간 + 인간 검증·수정 반복 사이클 (METR 연구 기반 40~60% 단축) |
| **코드 리뷰 대기** | 1~2일 | 20~40분 | AI 리뷰 실행 10~15분 + 인간 결과 검토 10~20분 (`code-review` 에이전트 병렬) |
| **단위 테스트 작성** | 1~2일 | 동시 처리 | `feature-dev`가 코드와 함께 테스트 생성 (인간 검증 30분~1시간 필요) |
| **코딩 표준 논쟁** | 리뷰마다 반복 | 원천 차단 | `standard-enforcer`가 작성 시점 자동 적용 |
| **보안 점검** | 별도 스프린트 | 실시간 차단 | `security-guidance` 9패턴 자동 차단 |
| **UI 디자인 핸드오프** | 디자이너→개발자 대기 | 직접 생성 | AI 생성 15~30분 + DSA 검수 1~2시간 (`frontend-design`) |
| **회고 실효성** | "다음엔 개선하겠습니다" | 규칙으로 강제 | `hookify`로 즉시 자동 규칙 전환 |
| **요구사항 변경 대응** | 다음 스프린트 (2주+) | 1~2일 | 영향도 분석 + 설계 문서 수정 + AI 코드 반영 + 인간 검증 |

### 2.3 세레모니 비교

| 이벤트 | 기존 소요 시간 | ASTRA 소요 시간 | AI 강화 내용 |
|--------|-------------|---------------|-------------|
| Sprint Planning | 4시간 | 1시간 | `feature-dev` 사전 분석 보고서 활용 |
| Daily Scrum | 15분 x 10일 = 2.5h | 비동기 | 커밋 기반 자동 진척 보고 |
| Design Review | (별도 없음) | 1시간 | DSA의 AI 생성 UI 검수 |
| Sprint Review | 2시간 | 1시간 | `chrome-devtools` 실시간 데모 |
| Retrospective | 1.5시간 | 30분 | AI 분석 → `hookify` 자동화 |
| Backlog Refinement | 2시간 | 30분 | `feature-dev` code-explorer 자동 분석 |
| **합계** | **~12시간/스프린트** | **~4시간/스프린트** | **67% 절감** |

### 2.4 역할 비교

| 기존 스크럼 | ASTRA | 변화 |
|-----------|-------|------|
| Product Owner (PO) 1명 | Domain Expert (DE) 1명 | PO 역할 유지 + 실시간 피드백 |
| Scrum Master (SM) 1명 | Vibe Architect (VA) 1명 | SM + 아키텍처 + 프롬프트 설계 |
| 개발자 3~5명 | Prompt Engineer (PE) 1~2명 | 수동 코딩 → 프롬프트 설계 + 검증 |
| UI 디자이너 1명 | Design System Architect (DSA) 1명 | 디자인 시스템 구축 + 검수 |
| QA 1~2명 | (AI 에이전트로 대체) | `code-review` + `security-guidance` |
| **총 7~10명** | **총 4~5명** | **50% 절감** |

### 2.5 아티팩트 비교

| 스크럼 아티팩트 | ASTRA 진화 형태 |
|-------------|---------------|
| Product Backlog | + `docs/prompts/` 프롬프트 맵 연결 |
| Sprint Backlog | + 기능별 프롬프트 + 설계 문서(MD) |
| Increment | + 자동 품질 리포트 + Living Document |
| Definition of Done (수동 체크) | + AI 품질 게이트 자동 검증 (Gate 1-3) |
| (테스트 문서 분산) | + `docs/tests/` 중앙 테스트 전략·케이스·리포트 관리 |
| (DB 설계 분산) | + `docs/database/` 중앙 DB 설계·네이밍·마이그레이션 관리 |

### 2.6 비용 효과

```
            기존 스크럼          ASTRA              절감
 기간:      5개월               3개월              40% ↓
 인원:      8명                 4명                50% ↓
 인건비:    3.2억원             0.96억원           70% ↓
 API비용:   -                   0.07억원           -
 총 비용:   3.5억원             1.1억원            69% ↓

 ※ 기간 단축 x 인원 절감의 승수 효과로 비용 절감
 ※ 시간 단축률은 METR 연구 기반 40~60% 적용 (구조화된 AI 워크플로우 기준)
 ※ 품질은 AI 자동 게이트로 오히려 향상 (표준 준수율 60~70% → 95%+)
```

> **기간과 인원이 동시에 줄어드는 비결:**
> AI 에이전트가 **반복적 수동 작업**(코딩, 리뷰, 테스트, 표준 검사)을 흡수하므로,
> 사람은 **판단과 의사결정**(요구사항, 아키텍처, 디자인, 비즈니스 로직)에만 집중합니다.

---

## 3. 역할 정의

### VA (Vibe Architect) - 시니어 개발자 1명

스크럼 마스터 역할을 확장하여, **AI 에이전트 오케스트레이션**까지 담당합니다.

**핵심 역량:**
1. **프롬프트 엔지니어링**: 모호한 백로그 아이템을 정밀한 프롬프트로 변환
2. **AI 결과물 판단력**: AI 출력의 품질/정확성을 빠르게 판단
3. **아키텍처 감각**: `feature-dev` Phase 4의 복수 설계안 중 최적안 선택
4. **도메인 지식**: 비즈니스 로직을 이해하고 AI에게 정확히 전달

**주요 활동:**
- 스프린트 진행 관리 + AI 에이전트 워크플로우 설계
- 프롬프트 품질 관리 및 최적화
- 회고 결과의 `hookify` 규칙 전환
- 아키텍처 의사결정 + 품질 게이트 최종 판단

### PE (Prompt Engineer) - 주니어 개발자 1~2명

코드 직접 작성이 아닌 **프롬프트 작성 + AI 결과물 검증**에 집중합니다.

**주요 활동:**
- 기능별 프롬프트 작성 (설계 문서 기반)
- AI가 생성한 코드 및 테스트 검증
- AI 리뷰 결과 확인 및 조치
- 설계 문서(MD) 검토 및 보완

### DE (Domain Expert) - 고객사 현업 담당자 1명

기존 PO 역할에 **실시간 피드백 방식**이 추가됩니다.

**주요 활동:**
- 자연어로 요구사항 직접 전달 (프롬프트 소재 제공)
- 백로그 우선순위 관리
- `chrome-devtools` 실시간 데모에서 즉시 피드백
- 동작하는 시스템에서 직접 인수 검증

### DSA (Design System Architect) - 디자이너 1명

AI가 UI 코드를 생성하더라도, **디자인 품질과 일관성은 전문 디자이너의 판단이 필수**입니다.

**주요 활동:**
- **Sprint 0**: 디자인 시스템 구축 (컬러, 타이포, 컴포넌트, 스페이싱 토큰 정의)
- **기능 스프린트**: AI 생성 UI 디자인 검수 (디자인 시스템 준수 확인)
- **Release Sprint**: 전체 화면 디자인 최종 검수

**디자인 검수 체크리스트:**
- [ ] 디자인 토큰 준수 (컬러, 폰트, 스페이싱이 토큰 시스템에서 벗어나지 않음)
- [ ] 컴포넌트 일관성 (동일 유형 컴포넌트가 화면마다 다르게 표현되지 않음)
- [ ] 반응형 레이아웃 (모바일/태블릿/데스크톱 브레이크포인트 적절)
- [ ] 접근성 기본 충족 (컬러 대비, 포커스 표시, 텍스트 크기)
- [ ] 인터랙션 일관성 (호버/포커스/액티브 상태 통일)
- [ ] 여백과 정렬 (그리드 시스템 준수)

---

## 4. Sprint 0: 프로젝트 셋업

Sprint 0는 1주간 프로젝트의 기반을 설정합니다. CLAUDE.md, 디자인 시스템, 설계 문서, 품질 규칙 등 모든 스프린트에 영향을 미치는 기반을 구축합니다.

**가장 먼저 Claude Code의 전역 개발환경을 설정합니다.** 이 설정은 프로젝트 단위가 아닌 개발자 머신 단위로 한 번만 수행하면 되며, 이후 모든 프로젝트에 공통 적용됩니다.

### Step 0.0: 개발환경 설정 (전역)

> **범위**: 개발자 머신 단위 (1회 설정, 모든 프로젝트에 적용)
> **소요 시간**: 30분~1시간
> **설정 경로**: `~/.claude/`

ASTRA 방법론의 모든 도구와 자동화가 동작하려면, Claude Code의 전역 설정이 사전에 완료되어 있어야 합니다. 프로젝트 설정(CLAUDE.md, hookify 등)은 Step 0.4에서 다루며, 이 단계에서는 **전역 인프라**만 구성합니다.

#### A. 전역 설정 (`~/.claude/settings.json`) — `astra-global-setup`이 자동 구성

> 아래 설정은 `/astra-methodology:astra-global-setup` 실행 시 자동으로 구성됩니다.
> 수동 설정이 필요한 경우에만 참고하세요.

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "permissions": {
    "defaultMode": "bypassPermissions"
  },
  "alwaysThinkingEnabled": true,
  "skipDangerousModePermissionPrompt": true
}
```

| 항목 | 값 | ASTRA에서의 역할 |
|------|-----|-----------------|
| Agent Teams | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` | `feature-dev`의 다중 에이전트 병렬 실행 (code-explorer, code-architect, code-reviewer) |
| 권한 모드 | `bypassPermissions` | AI 에이전트가 파일 편집/명령 실행 시 매번 승인 없이 자동 허용 |
| Always Thinking | `true` | AI의 사고 과정을 항상 표시하여 의사결정 과정 투명화 |

> **보안 참고**: `bypassPermissions`는 AI가 모든 도구를 자동 실행합니다.
> `security-guidance` 훅이 위험한 코드 패턴을 자동 차단하고,
> `hookify` 규칙이 프로젝트별 안전장치 역할을 하므로, ASTRA 환경에서는 안전하게 사용할 수 있습니다.

#### B. astra-methodology 플러그인 설치 및 전역 셋업

**1단계: 플러그인 마켓플레이스 추가**

```bash
claude plugin marketplace add https://github.com/ASTRA-TECHNOLOGY-COMPANY-LIMITED/astra-methodology.git
```

**2단계: astra-methodology 플러그인 설치**

```bash
claude plugin install astra-methodology@astra
```

**3단계: 전역 개발환경 자동 셋업**

Claude Code CLI 창에서 다음 명령어를 실행합니다:

```
/astra-methodology:astra-global-setup
```

> **이 명령어 하나로 자동 설치되는 항목:**
> - 필수 플러그인 8개 설치 (code-review, commit-commands, feature-dev, frontend-design, hookify, security-guidance, context7, astra-methodology)
> - MCP 서버 3개 등록 (chrome-devtools, postgres, context7)
> - 전역 설정 구성 (Agent Teams, bypassPermissions, Always Thinking)

**자동 설치되는 플러그인별 ASTRA 역할 요약**:

| 플러그인 | 타입 | ASTRA 역할 | 품질 게이트 |
|----------|------|-----------|-----------|
| `code-review` | 슬래시 커맨드 | PR 자동 리뷰 (5개 에이전트 병렬, 80점+ 필터링) | Gate 2 |
| `commit-commands` | 슬래시 커맨드 (3개) | Git 워크플로우 자동화 (커밋, PR 생성, 브랜치 정리) | - |
| `feature-dev` | 슬래시 커맨드 + 에이전트 (3종) | 7단계 기능 개발 워크플로우 (설계→구현→리뷰) | Gate 2 |
| `frontend-design` | 스킬 (자동 감지) | 프로덕션급 UI 자동 생성 | Gate 2.5 |
| `hookify` | 훅 + 슬래시 커맨드 | 프로젝트별 행동 방지 규칙 생성/관리 | Gate 1 |
| `security-guidance` | 훅 (자동) | 9개 보안 패턴 실시간 차단 (eval, innerHTML 등) | Gate 1 |
| `context7` | MCP 서버 | 라이브러리 최신 문서 조회 (환각 방지) | - |
| `standard-enforcer` | 훅 + 커맨드 + 스킬 + 에이전트 | 코딩 컨벤션 (Java/TS/Python/CSS/SCSS) + 공공 데이터 표준 네이밍 + 국제 코드 표준 (ISO/ITU) 자동 검사 | Gate 1 |

#### D. 설치 확인

```bash
# 전역 설정 확인
cat ~/.claude/settings.json

# MCP 서버 상태 확인
claude mcp list

# 설치된 플러그인 확인
claude plugin list
```

**전역 설정 완료 체크리스트:**
- [ ] `claude plugin marketplace add` 로 마켓플레이스 등록 완료
- [ ] `claude plugin install astra-methodology@astra` 실행 완료
- [ ] `/astra-methodology:astra-global-setup` 실행 완료 (전역 설정, MCP, 플러그인 자동 구성)
- [ ] `claude mcp list`로 MCP 서버 연결 확인 (chrome-devtools, postgres, context7)
- [ ] `claude plugin list`로 플러그인 활성화 확인 (8개)
- [ ] 사전 요구사항 확인: Node.js, Python 3.7+, jq, GitHub CLI (`gh`)

> **이 설정은 1회만 수행합니다.** 이후 새 프로젝트를 시작할 때는 Step 0.1부터 진행하면 됩니다.
> 프로젝트별 설정(CLAUDE.md, hookify 규칙 등)은 Step 0.4에서 다룹니다.

---

### Step 0.1: Vision & Backlog (Day 1-2)

DE와 킥오프 미팅을 통해 프로젝트 비전을 수립하고, Product Backlog를 초기 작성합니다.

```
# 기술 스택의 최신 문서 확인
"use context7 - Spring Boot 3의 WebClient와 RestTemplate 비교. 최신 권장 방식은?"

"use context7 - Next.js 15의 App Router 서버 컴포넌트 패턴을 알려줘"

# 핵심 기능에 대한 사전 분석 (코드 수정 없이 설계 문서만 생성)
/feature-dev "온라인 결제 시스템의 전체 아키텍처를 분석하고
docs/blueprints/overview.md로 작성해줘.
주요 모듈: 회원관리, 상품관리, 주문, 결제, 알림.
각 모듈 간 의존성과 데이터 흐름을 포함할 것.
아직 실제 코드는 수정하지 마."
```

### Step 0.2: Design System 구축 (Day 2-3) - DSA 주관

AI가 일관된 UI를 생성할 수 있도록 디자인 시스템을 정의합니다.

**DSA가 작성하는 산출물:**

```
docs/design-system/
├── design-tokens.css       # CSS Custom Properties (컬러, 폰트, 스페이싱)
├── tailwind.config.js      # Tailwind 기반 프로젝트의 경우
├── components.md           # 핵심 컴포넌트 스타일 가이드
├── layout-grid.md          # 레이아웃 그리드 시스템
└── references/             # 디자인 레퍼런스/무드보드 이미지
```

### Step 0.3: Architecture & Standards (Day 3-4)

핵심 기능에 대해 AI 기반 설계 문서를 생성하고, **중앙 DB 설계 문서**와 **테스트 전략 문서**를 작성합니다.

#### A. 기능 설계 문서 생성

```
# 핵심 기능의 설계 문서 자동 생성
/feature-dev "결제 알림 시스템의 설계 문서를 docs/blueprints/payment-notification.md로
작성해줘. 다음을 포함할 것:
- 목표: 결제 완료/실패 시 사용자에게 실시간 알림
- 알림 채널: 이메일, SMS, 푸시 알림
- 재시도 정책: 실패 시 3회까지 지수 백오프
아직 실제 코드는 수정하지 마."
```

#### B. 중앙 DB 설계 문서 작성 (핵심!)

**모든 테이블 설계를 `docs/database/database-design.md` 단일 문서에서 관리합니다.**

> **왜 하나의 문서인가?**
> - AI가 전체 테이블 구조와 연관관계를 **한번에 인식**하여 정합성 있는 설계 가능
> - 테이블 간 FK 참조, 컬럼 중복, 네이밍 일관성을 단일 컨텍스트에서 검증
> - 기능별 설계 문서에 테이블 DDL을 분산시키면 AI가 전체 스키마를 파악할 수 없음

```
# 1단계: 전체 DB 설계 문서 초안 생성
/feature-dev "프로젝트의 데이터베이스 설계 문서를 docs/database/database-design.md로
작성해줘. 다음 구조로 작성할 것:

## 포함 내용:
- 전체 ERD (모듈별 테이블 관계도)
- 모듈별 테이블 목록 및 DDL (인증, 워크스페이스, 결제, IAM 등)
- 테이블 간 FK 관계 명세
- 공통 컬럼 패턴 (감사 컬럼, 상태 코드 등)
- Enum/코드 값 정의

## 테이블 설계 규칙:
- 테이블명 접두사: TB_(일반), TC_(코드), TH_(이력), TL_(로그), TR_(관계)
- 공공 데이터 표준 용어 사전 준수 (/lookup-term 활용)
- 모든 테이블에 감사 컬럼 포함 (CRTR_ID, CRT_DT, MDFR_ID, MDFCN_DT)

## 주요 모듈:
- 인증: 회원(TB_COMM_USER), 약관(TB_COMM_TRMS), 동의이력(TH_COMM_USER_AGRE)
- 결제: 플랜(TB_PAY_PLAN), 구독(TB_PAY_SBSC), 결제(TB_PAY_STLM)
- 주문: 주문(TB_ORDR), 주문상품(TB_ORDR_PRDT)
- 알림: 알림이력(TH_NTFC_HIST)

아직 실제 코드는 수정하지 마."

# 2단계: 표준 용어 조회 및 검증
/lookup-term 결제금액
/lookup-term 주문번호

# 3단계: DB 설계 문서의 네이밍 표준 검증
# → VA가 docs/database/database-design.md를 검토
# → 표준 용어 사전 준수 여부 확인, DE 승인
```

**DB 설계 문서 구조 예시** (`docs/database/database-design.md`):

```markdown
# 데이터베이스 설계 문서

## 1. 전체 ERD
[모듈별 테이블 관계도]

## 2. 공통 규칙
### 2.1 테이블 접두사
### 2.2 공통 감사 컬럼
### 2.3 네이밍 규칙

## 3. 인증 모듈 (COMM)
### 3.1 TB_COMM_USER (사용자)
### 3.2 TB_COMM_TRMS (약관)
### 3.3 TH_COMM_USER_AGRE (동의이력)

## 4. 결제 모듈 (PAY)
### 4.1 TB_PAY_PLAN (플랜)
### 4.2 TB_PAY_SBSC (구독)
...

## 5. 테이블 간 FK 관계 요약
```

#### C. 국제 코드 표준 적용 (ISO 3166-1/2, ITU-T E.164)

전화번호 입력, 국가/지역 선택기, 주소 양식 등 **국제 코드가 필요한 기능**이 있다면 Sprint 0에서 표준을 사전 정의합니다.

**지원 표준:**

| 표준 | 용도 | DB 컬럼 규칙 | 데이터 |
|------|------|-------------|--------|
| ISO 3166-1 (alpha-2) | 국가 코드 (`KR`, `US`, `JP`) | `NATN_CD CHAR(2)` | 249개국 |
| ISO 3166-2 | 지역/행정구역 코드 (`KR-11`, `US-CA`) | `RGN_CD VARCHAR(6)` | 653개 지역 (21개국) |
| ITU-T E.164 | 국제 전화번호 (`+821012345678`) | `INTL_TELNO VARCHAR(15)` | 245개 국가 코드 |

**설계 문서에 반영:**
```
# 국제 코드 조회
/lookup-code KR
/lookup-code US-CA
/lookup-code +82

# DB 설계 문서에 국제 코드 컬럼 반영 (필요 시)
/feature-dev "docs/database/database-design.md의 사용자 테이블에
국가코드(NATN_CD), 지역코드(RGN_CD), 국제전화번호(INTL_TELNO) 컬럼을
ISO 3166-1/2, E.164 표준에 맞게 추가해줘.
아직 코드는 수정하지 마."

# 국제 코드 컴포넌트 생성 (구현 시)
/generate-intl-component 국가 선택기
/generate-intl-component 전화번호 입력
```

> **`code-standard` 스킬은 전화번호 입력, 국가/지역 선택기, 주소 양식 작업 시 자동 감지되어 적용됩니다.**

#### D. 테스트 전략 문서 작성

**테스트 범위, 전략, 기준을 `docs/tests/test-strategy.md`에서 관리합니다.**

```
# 테스트 전략 문서 생성
/feature-dev "프로젝트의 테스트 전략 문서를 docs/tests/test-strategy.md로
작성해줘. 다음 구조로 작성할 것:

## 포함 내용:
- 테스트 레벨 정의 (단위/통합/E2E 각 레벨의 범위와 목적)
- 테스트 커버리지 목표 (서비스 레이어 70%+, 핵심 비즈니스 로직 90%+)
- 테스트 환경 구성 (테스트 DB, 목 서버, 테스트 데이터 관리)
- 테스트 네이밍 규칙 (Given-When-Then 패턴)
- 테스트 데이터 관리 전략 (Fixture, Factory 패턴)
- 자동화 범위 (CI/CD 파이프라인 연동)

## 주요 모듈별 테스트 범위:
- 인증: 회원가입/로그인/토큰갱신 시나리오
- 결제: 결제 성공/실패/재시도/환불 시나리오
- 주문: 주문 생성/취소/상태 변경 시나리오

아직 실제 코드는 수정하지 마."
```

> **기능 스프린트에서 `docs/tests/test-cases/` 하위에 기능별 테스트 케이스 문서가 추가됩니다.**
> 설계 문서(blueprint)에 정의된 기능 요구사항을 기반으로 테스트 케이스를 사전 정의하고,
> AI가 코드와 테스트를 동시에 생성할 때 이 문서를 참조합니다.

### Step 0.4: Guard Rails 설정 (Day 4-5)

스프린트 전체에 적용될 품질 규칙을 사전 설정합니다.

**CLAUDE.md 작성:**
```markdown
# Project: 온라인 결제 시스템

## 아키텍처
- 백엔드: Spring Boot 3
- 프론트엔드: Next.js 15
- 데이터베이스: PostgreSQL 16

## 코딩 규칙
- 모든 API 엔드포인트에 인증 미들웨어 필수
- DB 스키마는 docs/database/database-design.md를 Single Source of Truth로 관리
- DB 엔티티는 공공 데이터 표준 용어 사전 준수 (/lookup-term 활용)
- 테이블명 접두사: TB_(일반), TC_(코드), TH_(이력), TL_(로그), TR_(관계)
- REST API 응답 형식: { success: boolean, data: T, error?: string }
- 에러 처리: 비즈니스 예외와 시스템 예외를 구분

## 디자인 규칙 (DSA 정의)
- 디자인 토큰: docs/design-system/design-tokens.css 참조 필수
- 컬러는 반드시 CSS Variable (--color-*) 사용, 하드코딩 금지
- 폰트 사이즈는 토큰 스케일 사용 (--font-size-*)
- 스페이싱은 8px 그리드 시스템 준수 (--spacing-*)
- 반응형 브레이크포인트: mobile(~767px), tablet(768~1023px), desktop(1024px~)

## 금지 사항
- console.log 사용 금지 (logger 사용)
- any 타입 사용 금지
- raw SQL 직접 작성 금지 (ORM 사용)
- .env 파일 커밋 금지

## 테스트 규칙
- 모든 서비스 레이어에 단위 테스트 작성
- 테스트 커버리지 최소 70%

## 커밋 컨벤션
- Conventional Commits (feat:, fix:, refactor:, docs:, test:)
```

**hookify 규칙 설정:**
```
# 프로젝트별 커스텀 규칙 생성
/hookify 모든 API 엔드포인트에는 인증 미들웨어를 반드시 포함할 것
/hookify console.log 대신 logger 라이브러리를 사용할 것
/hookify SQL 쿼리에 raw string을 직접 사용하지 말 것
/hookify CSS에서 하드코딩된 컬러값 대신 CSS Variable을 사용할 것

# 현재 규칙 확인
/hookify:list
```

**Sprint 0 완료 체크리스트:**
- [ ] Product Backlog 초기 작성 완료
- [ ] 디자인 시스템 구축 완료 (디자인 토큰, 컴포넌트 가이드)
- [ ] 핵심 기능별 설계 문서(MD) 생성 및 DE 승인
- [ ] **중앙 DB 설계 문서 작성 완료** (`docs/database/database-design.md`)
- [ ] DB 네이밍 규칙 문서 작성 완료 (`docs/database/naming-rules.md`)
- [ ] DB 설계 문서 표준 네이밍 검증 완료
- [ ] **국제 코드 표준 적용 확인** (해당 시: ISO 3166-1/2, ITU-T E.164)
- [ ] **테스트 전략 문서 작성 완료** (`docs/tests/test-strategy.md`)
- [ ] CLAUDE.md 작성 완료 (디자인 원칙 포함)
- [ ] hookify 규칙 설정 완료
- [ ] 기술 스택 최신 문서 확인 (Context7)

---

## 5. 품질 게이트

3단계 자동 품질 게이트로 Definition of Done을 자동 검증합니다.

### Gate 1: WRITE-TIME (작성 시점)

모든 코드 작성(Write/Edit)에 자동 적용됩니다. Sprint 0에서 한 번 설정하면 이후 개입이 불필요합니다.

| 도구 | 검사 내용 | 동작 방식 |
|------|----------|----------|
| `security-guidance` | 9개 보안 패턴 (eval, innerHTML 등) | PreToolUse 훅, **차단** (exit 2) |
| `standard-enforcer` | 금칙어 + 네이밍 규칙 | PostToolUse 훅, 경고 (exit 0) |
| `hookify` | 프로젝트별 커스텀 규칙 | PreToolUse/PostToolUse 훅 |
| `coding-convention` 스킬 | Java/TS/Python/CSS/SCSS 컨벤션 자동 적용 | Skill (자동 감지) |
| `data-standard` 스킬 | 공공 데이터 표준 용어 사전 적용 | Skill (DB 코드 시 자동 감지) |
| `code-standard` 스킬 | ISO 3166-1/2, ITU-T E.164 표준 적용 | Skill (전화번호/국가/주소 코드 시 자동 감지) |

**코딩 컨벤션 상세 (언어별 자동 적용 규칙):**

| 언어 | 기반 표준 | 핵심 규칙 |
|------|----------|----------|
| Java | Google Java Style Guide | 2-space 들여쓰기, 100자 제한, K&R 브레이스, 와일드카드 import 금지, `UpperCamelCase` 클래스, `UPPER_SNAKE_CASE` 상수 |
| TypeScript | Google TypeScript Style Guide | Prettier 포맷팅, `export default` 금지, `any` 금지, `var` 금지, `.forEach()` 금지, `===`/`!==` 필수 |
| Python | PEP 8 | 4-space 들여쓰기, 79자 제한, `snake_case` 함수, `CapWords` 클래스, `is None` 필수, bare `except:` 금지 |
| CSS/SCSS | CSS Guidelines + Sass Guidelines | 2-space 들여쓰기, 80자 제한, BEM 네이밍, ID 선택자 금지, 최대 3단계 중첩, 모바일 우선 미디어 쿼리 |

### Gate 2: REVIEW-TIME (리뷰 시점)

PR 생성/기능 완료 시 실행합니다.

| 도구 | 검사 내용 | 동작 방식 |
|------|----------|----------|
| `feature-dev` code-reviewer | 코드 품질/버그/컨벤션 | 3개 에이전트 병렬, Sonnet |
| `/code-review` | CLAUDE.md 준수, 버그, 이력 분석 | 5개 에이전트 병렬, 80점+ 필터링 |
| `blueprint-reviewer` 에이전트 | 설계 문서 품질/일관성 검증 | Sonnet, 읽기 전용 |
| `test-coverage-analyzer` 에이전트 | 테스트 전략/커버리지 분석 | Haiku, 읽기 전용 |
| `convention-checker` 에이전트 | 코딩 컨벤션 심층 분석 | Haiku, 읽기 전용 |

### Gate 2.5: DESIGN-TIME (디자인 검수 시점)

UI 기능 완료 시 DSA가 수동 검수합니다. **디자이너의 전문 판단이 필요한 영역**입니다.

| 검수 항목 | 확인 방법 |
|----------|----------|
| 디자인 토큰 준수 (컬러, 폰트, 스페이싱) | `chrome-devtools` 스냅샷 + `design-token-validator` 에이전트 (Haiku, 자동 검증) |
| 컴포넌트 일관성 | 화면별 비교 |
| 반응형 레이아웃 | `chrome-devtools` 뷰포트 전환 |
| 접근성 기본 확인 | 컬러 대비, 포커스 확인 |

이슈 발견 시: DSA 피드백 → PE 프롬프트 수정 → AI 재생성 → DSA 재검수 (1시간 내 완료)

### Gate 3: BRIDGE-TIME (릴리스 시점)

Release Sprint에서 실행합니다.

| 도구 | 검사 내용 |
|------|----------|
| `quality-gate-runner` 에이전트 | Gate 1~3 통합 실행 (Sonnet, 읽기 전용) |
| `/check-convention src/` | 전체 코드 컨벤션 |
| `/check-naming src/entity/` | 전체 DB 네이밍 표준 |
| `chrome-devtools` | UI/성능/네트워크/콘솔 에러 |

### 통과 기준 요약

| 게이트 | 통과 기준 | 차단 시 조치 |
|--------|----------|-------------|
| Gate 1 | security-guidance 경고 0건, standard-enforcer 금칙어 0건 | 즉시 수정 후 재작성 |
| Gate 2 | code-review 고신뢰 이슈 0건, 테스트 커버리지 70%+ | fix now / fix later 결정 |
| Gate 2.5 | DSA 디자인 검수 승인 | 프롬프트 수정 → 재생성 → 재검수 |
| Gate 3 | convention/naming 위반 0건, 콘솔 에러 0건 | 일괄 수정 후 배포 |

---

## 6. 기능 스프린트 실행

### 6.1 주간 일정

```
Monday: Sprint Planning (1시간) + Feature Build 시작

Tuesday-Thursday 오전: Feature Build (핵심 개발일, AI 코드 생성+인간 검증 반복)

Thursday 오후: Design Review (DSA 검수)

Friday: Code Review + Sprint Review + Retrospective
```

### 6.2 Sprint Planning (1시간)

#### 사전 준비 (Planning 전날, VA가 실행)

```
/feature-dev "이번 스프린트 후보 백로그 아이템들의 기술적 복잡도를 분석해줘:
1. 사용자 인증 (OAuth 2.0 + JWT)
2. 결제 대시보드
3. 알림 설정 페이지
기존 코드베이스와의 의존성, 예상 작업 규모, 위험 요소를 정리해줘.
아직 코드는 수정하지 마."
```

#### Planning 미팅 (1시간)

| 시간 | 활동 | 참여자 |
|------|------|--------|
| 10분 | AI 분석 보고서 리뷰 (스토리 포인트 추정 대체) | VA, PE |
| 20분 | DE와 비즈니스 우선순위 확인 및 스프린트 목표 합의 | DE, VA |
| 20분 | 아이템별 프롬프트 설계 방향 논의 + DSA 디자인 방향 공유 | VA, PE, DSA |
| 10분 | 스프린트 백로그 확정 | 전원 |

### 6.3 Feature Build (Monday~Thursday 오전)

#### A. 설계 문서 기반 구현

3단계 워크플로우: **기능 설계 문서 생성 → DB 설계 문서 반영 → 문서 기반 구현**

```
# 1단계: 기능 설계 문서 생성
/feature-dev "JWT 기반 사용자 인증 시스템의 설계 문서를
docs/blueprints/auth.md로 작성해줘.
- 회원가입, 로그인, 토큰 갱신, 권한 관리(RBAC) 기능을 포함
- 비밀번호는 bcrypt 해싱
- Access Token 유효기간 30분, Refresh Token 7일
- DB 스키마는 docs/database/database-design.md를 참조할 것
아직 코드는 수정하지 마."

# → VA/DE가 생성된 docs/blueprints/auth.md를 직접 열어 검토 및 수정
# → DE 승인 후 다음 단계 진행

# 2단계: DB 설계 문서에 신규/변경 테이블 반영
/feature-dev "docs/database/database-design.md에 인증 모듈 테이블을
추가/갱신해줘:
- TB_COMM_USER (사용자), TB_COMM_TRMS (약관), TH_COMM_USER_AGRE (동의이력)
- 기존 테이블과의 FK 관계를 ERD와 관계 요약 섹션에도 반영할 것
- 표준 용어 사전을 준수할 것 (/lookup-term 활용)
아직 코드는 수정하지 마."

# 3단계: 테스트 케이스 사전 정의
/feature-dev "docs/blueprints/auth.md의 기능 요구사항을 기반으로
테스트 케이스 문서를 docs/tests/test-cases/auth-test-cases.md로 작성해줘.
- 단위 테스트: 서비스 레이어 핵심 로직 (해싱, 토큰 생성/검증)
- 통합 테스트: API 엔드포인트 (회원가입/로그인/토큰갱신)
- 엣지 케이스: 만료 토큰, 잘못된 비밀번호, 중복 이메일
- Given-When-Then 형식으로 작성
아직 코드는 수정하지 마."

# 4단계: 설계 문서 기반 구현
/feature-dev "docs/blueprints/auth.md와
docs/database/database-design.md의 내용을 엄격히 준수해서
개발을 진행해줘. 테스트는 docs/tests/test-cases/auth-test-cases.md를
참조하여 작성하고, 구현이 끝나면 모든 테스트를 실행하고
결과를 docs/tests/test-reports/에 보고해."
```

> **이 한 줄의 프롬프트로 자동 실행되는 것들:**
> 1. `code-explorer`가 기존 코드베이스 분석 (2~3개 병렬)
> 2. 명확화 질문 (엣지 케이스, 비즈니스 규칙 확인)
> 3. `code-architect`가 구현 계획 제시 (2~3개 병렬)
> 4. 승인 후 코드 작성
>    - `standard-enforcer`가 금칙어/네이밍 자동 검사 (PostToolUse 훅)
>    - `security-guidance`가 보안 패턴 자동 차단 (PreToolUse 훅)
>    - `coding-convention` 스킬이 컨벤션 자동 적용
> 5. `code-reviewer`가 품질 검사 (3개 병렬)
> 6. 완료 요약 문서 생성

#### B. UI 구현 (frontend-design 자동 활성화)

프론트엔드 작업을 요청하면 `frontend-design` 스킬이 자동으로 활성화되어 프로덕션 수준 UI를 생성합니다.

```
# 미학 방향을 지정하면 더 좋은 결과
"결제 대시보드를 만들어줘.
- 실시간 결제 현황 (오늘 건수/금액)
- 일별 매출 차트 (최근 30일)
- 최근 거래 목록 (페이지네이션)
- 다크 모드 기본, 미니멀리스트 스타일
- docs/design-system/design-tokens.css의 토큰 시스템을 반드시 사용"

# 다양한 미학 방향 지정 예시
"brutalist 스타일의 포트폴리오 페이지를 만들어줘"
"art deco 느낌의 고급스러운 상품 상세 페이지를 만들어줘"
"retro-futuristic 스타일의 관리자 대시보드를 만들어줘"
```

#### C. DB 작업

**모든 DB 변경은 `docs/database/database-design.md`를 먼저 갱신한 후 코드에 반영합니다.**

```
# 1. DB 설계 문서에 테이블 추가/변경 (문서 먼저!)
/feature-dev "docs/database/database-design.md에 주문 모듈 테이블을 추가해줘:
- TB_ORDR (주문): 주문번호, 주문일시, 주문금액, 배송주소, 주문상태코드
- TB_ORDR_PRDT (주문상품): 주문번호FK, 상품번호FK, 수량, 단가
- 기존 테이블(TB_COMM_USER, TB_PAY_STLM 등)과의 FK 관계를 ERD에 반영
- 표준 용어 사전을 준수할 것
아직 코드는 수정하지 마."

# 2. 표준 용어 조회 (필요 시)
/lookup-term 주문금액

# 3. DB 설계 문서 기반으로 엔티티/DDL 코드 생성
/generate-entity docs/database/database-design.md의 주문 모듈 테이블

# 4. 생성된 엔티티 코드 네이밍 검사
/check-naming src/main/java/com/example/entity/Order.java

# 5. DB 스키마 확인 (postgres MCP)
"현재 DB의 테이블 목록과 docs/database/database-design.md의 정의가 일치하는지 확인해줘"

# 6. 마이그레이션 SQL 기록 (변경 이력 관리)
/feature-dev "docs/database/database-design.md에서 이번에 추가된 주문 모듈 테이블의
마이그레이션 SQL을 docs/database/migration/v1.1.0-order.sql로 작성해줘.
- CREATE TABLE 문 + 인덱스 + FK 제약조건 포함
- 롤백 SQL도 함께 작성할 것
아직 실제 DB에는 적용하지 마."
```

#### D. 국제 코드 활용 (해당 기능 시)

전화번호 입력, 국가/지역 선택기, 주소 양식 등을 구현할 때 국제 코드 표준을 적용합니다.

```
# 국제 코드 조회 (국가, 지역, 전화번호)
/lookup-code KR              # → KR, 대한민국, alpha-2
/lookup-code US-CA           # → US-CA, California, ISO 3166-2
/lookup-code +82             # → +82, 대한민국, E.164

# 국제 코드 컴포넌트 자동 생성
/generate-intl-component 국가 선택기     # → ISO 3166-1 기반 국가 드롭다운
/generate-intl-component 전화번호 입력   # → E.164 기반 국제 전화번호 입력 필드
/generate-intl-component 지역 선택기     # → ISO 3166-2 기반 지역 드롭다운 (국가 연동)

# DB 엔티티에 국제 코드 컬럼 포함 시 자동 검증
# → code-standard 스킬이 자동 감지되어 NATN_CD, RGN_CD, INTL_TELNO 규칙 적용
```

#### E. 실시간 검증 (chrome-devtools MCP)

개발 중 언제든 브라우저에서 직접 확인합니다.

```
# 레이아웃 확인
"현재 페이지의 스냅샷을 찍어서 레이아웃을 확인해줘"

# API 동작 검증
"API 호출이 정상적으로 이루어지는지 네트워크 요청을 확인해줘"

# 에러 확인
"콘솔에 에러가 있는지 확인해줘"

# 성능 측정
"페이지 로딩 성능을 측정하고 개선점을 제안해줘"

# 반응형 확인 (뷰포트 전환)
"모바일 뷰포트(375x667)로 전환하고 레이아웃을 확인해줘"
```

**자동 통합 테스트 (서버 실행 + 브라우저 검증):**
```
# 서버 실행 + Chrome MCP 통합 테스트 자동 수행
/astra-integration-test

# → 서버 자동 실행 + 로그 모니터링
# → 페이지 검증 (스냅샷, 레이아웃)
# → API 동작 확인 (네트워크 요청)
# → 성능 측정 (Core Web Vitals)
# → 콘솔 에러 확인
```

#### F. 최신 API 참조 (context7 MCP)

개발 중 라이브러리 API가 불확실할 때 최신 문서를 조회합니다.

```
"use context7 - Spring Boot 3에서 WebClient로 비동기 HTTP 요청하는 방법"
"use context7 - Prisma에서 트랜잭션을 사용하는 방법"
"use context7 - Next.js 15에서 Server Actions 문법"
```

#### G. 커밋

```
# 기능 완료 시마다 커밋
/commit
```

### 6.4 Daily Scrum → 비동기 AI 보고

매일 15분 스탠드업 대신, 커밋 로그 기반으로 진척을 비동기 파악합니다.

- **비동기 진척 보고**: 커밋 로그와 PR 기반으로 자동 요약
- **블로커 발생 시에만 동기 소통**: Slack/Teams로 즉시 공유
- **주 1회 15분 대면 동기화**: 방향성 확인 (선택사항)

VA가 매일 아침 커밋 이력을 확인하고 필요 시에만 대면 소통합니다.

### 6.5 Design Review (Thursday 오후) + Code Review (Friday 오전)

#### Design Review (1시간) - DSA 주관

```
[Design Review]
  ├─ 30분: DSA가 AI 생성 UI 검수
  │   ├─ chrome-devtools MCP로 실제 화면 확인
  │   ├─ 디자인 토큰 준수 여부 확인
  │   ├─ 반응형 레이아웃 확인 (뷰포트 전환)
  │   └─ 접근성 기본 확인
  │
  └─ 30분: 디자인 이슈 수정
      ├─ DSA: "이 버튼 색상이 토큰과 다릅니다", "여백이 8px 그리드에 안 맞습니다"
      ├─ PE: 프롬프트에 디자인 피드백 반영 → AI 재생성 (5~10분)
      └─ DSA: 수정 결과 즉시 확인 → 승인
```

#### Code Review

```
# PR 생성 + 자동 리뷰
/commit-push-pr

# 5개 에이전트 병렬 코드 리뷰 (80점+ 고신뢰 이슈만 보고)
/code-review

# 추가 품질 검사
/check-convention src/
/check-naming src/entity/
```

### 6.6 Sprint Review (Friday, 1시간)

Design Review를 통과한 상태에서 진행합니다.

```
[Sprint Review]
  ├─ 30분: 실시간 데모 (chrome-devtools MCP)
  │   ├─ 별도 데모 준비 불필요 - 개발 환경에서 즉시 시연
  │   ├─ 다양한 뷰포트 실시간 전환 (모바일/태블릿/데스크톱)
  │   ├─ 네트워크 요청 실시간 확인 (API 동작 증명)
  │   └─ 성능 트레이스 결과 공유
  │
  └─ 30분: DE 피드백 + 즉시 반영
      ├─ DE: "이 부분은 이렇게 바꿔주세요"
      ├─ PE: 프롬프트 수정 → AI 재구현 (5~10분)
      └─ 변경 결과 즉시 데모
```

### 6.7 Sprint Retrospective (Friday, 30분)

```
[AI 강화 회고]
  ├─ 10분: 스프린트 데이터 기반 자동 분석 (sprint-analyzer 에이전트, Sonnet)
  │   ├─ code-review에서 반복된 이슈 패턴
  │   ├─ security-guidance 차단 이력
  │   ├─ standard-enforcer 위반 빈도
  │   └─ 커밋 패턴/리듬 분석
  │
  ├─ 10분: 팀 논의 (AI가 잡지 못하는 영역)
  │   └─ 도메인 로직 오해, 소통 이슈 등에 집중
  │
  └─ 10분: 개선사항 자동화
      ├─ /hookify [회고에서 나온 반복 실수를 규칙으로 전환]
      ├─ CLAUDE.md 업데이트
      └─ 다음 스프린트 프롬프트 템플릿 개선
```

**회고에서 hookify 활용 예시:**
```
# 이번 스프린트에서 반복된 실수를 규칙화
/hookify 에러 응답에 스택트레이스를 노출하지 말 것
/hookify API 응답에 민감 정보(비밀번호, 토큰)를 포함하지 말 것

# 대화 분석 기반 자동 감지 (인자 없이 실행)
/hookify
# → conversation-analyzer 에이전트가 최근 대화에서 반복 실수 감지
# → 감지된 문제 행동 목록 제시
# → 선택 후 규칙 생성
```

### 6.8 Backlog Refinement (30분)

```
# 사전 AI 분석 (Refinement 전)
/feature-dev "다음 백로그 아이템들을 분석해줘:
1. 주문 취소/환불 프로세스
2. 관리자 대시보드 통계 페이지
3. 사용자 알림 설정 관리
기존 코드베이스와의 관련성, 기술적 위험, 선행 조건을 정리해줘.
아직 코드는 수정하지 마."

# Refinement 미팅 (30분)
# ├─ AI 분석 결과 리뷰
# ├─ DE와 비즈니스 가치/우선순위 확인
# └─ 필요 시 아이템 분할
```

### 6.9 요구사항 변경 대응

ASTRA에서는 변경 비용이 극적으로 낮아 스프린트 중간 변경도 유연하게 흡수합니다.

```
# 1. 영향도 분석 (30분~1시간: AI 분석 15분 + 인간 검토 30분)
/feature-dev "결제 수단에 '간편결제(카카오페이)' 추가 요청이 들어왔어.
기존 코드베이스와 docs/database/database-design.md를 참조해서
결제 모듈의 영향 범위를 분석해줘.
아직 코드는 수정하지 마."

# 2. 설계 문서 수정 (1~2시간: AI 생성 20분 + 인간 검토·보완 1시간)
# → docs/blueprints/payment.md에 간편결제 섹션 추가
# → docs/database/database-design.md에 테이블 변경사항 반영 (필요 시)

# 3. 코드 반영 (4~8시간: AI 코드 생성 1~2시간 + 인간 검증·수정 반복 3~6시간)
/feature-dev "docs/blueprints/payment.md와
docs/database/database-design.md의 업데이트된 내용을 반영해서
간편결제(카카오페이) 기능을 구현해줘.
기존 결제 로직에 영향이 없도록 PaymentProvider 패턴을 사용할 것."

# 4. 자동 품질 검증 (30분~1시간: AI 리뷰 15분 + 결과 확인 30분)
/code-review
```

---

## 7. Release Sprint: 배포 준비

기존 스크럼의 Hardening Sprint에 해당하며, 1주간 진행합니다.

### Step R.1: 시스템 통합 테스트

```
# 자동 통합 테스트 (서버 실행 + Chrome MCP 전체 검증)
/astra-integration-test
# → 서버 실행, 전체 페이지 검증, API 동작 확인, 성능 측정, 콘솔 에러 확인을 자동 수행

# API 연동 테스트 (수동 상세 확인)
"결제 API와 주문 API 간의 연동을 테스트해줘. 네트워크 요청을 모니터링하고 응답을 검증해."

# DB 데이터 정합성 확인 (중앙 DB 설계 문서 기준)
"docs/database/database-design.md의 FK 관계 정의와 실제 DB 스키마가 일치하는지 확인해줘"

# 성능 프로파일링
"전체 페이지의 성능 트레이스를 실행하고 병목 지점을 분석해줘"

# 크로스 브라우저/반응형 테스트
"모바일 뷰포트(375x667)로 전환하고 레이아웃을 확인해줘"
"태블릿 뷰포트(768x1024)로 전환하고 확인해줘"

# 통합 테스트 결과 보고서 생성
/feature-dev "전체 테스트 실행 결과를 docs/tests/test-reports/release-report.md로
작성해줘. 다음을 포함할 것:
- 모듈별 테스트 통과/실패 현황
- 테스트 커버리지 요약
- 발견된 이슈 및 조치 내역
- docs/tests/test-strategy.md의 목표 대비 달성률"
```

### Step R.2: 최종 품질 게이트 (Gate 3)

```
# 전체 코드 품질 검사
/code-review
/check-convention src/
/check-naming src/entity/

# 콘솔 에러 0건 확인
"콘솔에 에러가 있는지 확인해줘"

# DSA 최종 디자인 검수 (전체 화면 일관성)
```

### Step R.3: 배포 & 이관

```
# 운영 매뉴얼 자동 생성
/feature-dev "프로젝트의 운영 매뉴얼을 docs/delivery/operation-manual.md로
작성해줘. 배포 절차, 환경 변수, 모니터링 포인트, 장애 대응 가이드를 포함할 것.
아직 코드는 수정하지 마."

# 브랜치 정리
/clean_gone
```

---

## 8. 프로젝트 템플릿

### 8.1 디렉토리 구조

```
project-root/
├── CLAUDE.md                    # 프로젝트 AI 규칙 (핵심!)
├── .claude/
│   ├── hookify.*.local.md       # 프로젝트별 hookify 규칙
│   └── settings.json            # 프로젝트별 Claude 설정
│
├── docs/
│   ├── design-system/           # Sprint 0에서 DSA가 구축
│   │   ├── design-tokens.css
│   │   ├── tailwind.config.js
│   │   ├── components.md
│   │   ├── layout-grid.md
│   │   └── references/
│   │
│   ├── blueprints/              # 설계 문서 (Living Document)
│   │   ├── overview.md
│   │   ├── feature-001.md
│   │   └── feature-002.md
│   │
│   ├── database/                # 데이터베이스 관련 문서
│   │   ├── database-design.md   # 중앙 DB 설계 문서 (전체 테이블/ERD/FK)
│   │   ├── naming-rules.md      # DB 네이밍 규칙 및 표준 용어 매핑
│   │   └── migration/           # 마이그레이션 이력
│   │       └── v1.0.0.sql
│   │
│   ├── tests/                   # 테스트 관련 문서
│   │   ├── test-strategy.md     # 테스트 전략 (단위/통합/E2E 범위 정의)
│   │   ├── test-cases/          # 기능별 테스트 케이스 명세
│   │   │   └── auth-test-cases.md
│   │   └── test-reports/        # 스프린트별 테스트 결과 보고서
│   │       └── sprint-1-report.md
│   │
│   ├── prompts/                 # 스프린트별 프롬프트 맵
│   │   ├── sprint-1.md
│   │   └── sprint-2.md
│   │
│   ├── retrospectives/          # 스프린트 회고 기록
│   │   └── sprint-1-retro.md
│   │
│   └── delivery/                # Release Sprint 산출물
│       ├── operation-manual.md
│       └── quality-report.md
│
└── src/                         # 소스 코드
```

### 8.2 스프린트 프롬프트 맵 템플릿

```markdown
# Sprint [N] 프롬프트 맵

## 스프린트 목표
[이번 스프린트에서 달성할 비즈니스 가치를 서술]

## 기능 1: 사용자 인증
### 1.1 설계 프롬프트
/feature-dev "JWT 기반 사용자 인증 시스템의 설계 문서를
docs/blueprints/auth.md로 작성해줘. 회원가입, 로그인, 토큰 갱신,
권한 관리(RBAC) 기능을 포함.
DB 스키마는 docs/database/database-design.md를 참조할 것.
아직 코드는 수정하지 마."

### 1.2 DB 설계 반영 프롬프트
/feature-dev "docs/database/database-design.md에 인증 모듈 테이블을
추가/갱신해줘:
- TB_COMM_USER, TB_COMM_TRMS, TH_COMM_USER_AGRE, TB_COMM_RFRSH_TKN
- ERD와 FK 관계 요약도 갱신할 것. 표준 용어 사전 준수.
아직 코드는 수정하지 마."

### 1.3 테스트 케이스 프롬프트
/feature-dev "docs/blueprints/auth.md의 기능 요구사항을 기반으로
테스트 케이스를 docs/tests/test-cases/auth-test-cases.md로 작성해줘.
Given-When-Then 형식, 단위/통합/엣지 케이스를 포함.
아직 코드는 수정하지 마."

### 1.4 구현 프롬프트
/feature-dev "docs/blueprints/auth.md와
docs/database/database-design.md의 내용을 엄격히 준수해서
개발을 진행해줘. 테스트는 docs/tests/test-cases/auth-test-cases.md를
참조하여 작성하고, 구현이 끝나면 모든 테스트를 실행하고
결과를 docs/tests/test-reports/에 보고해."

## 기능 2: 결제 대시보드
### 2.1 설계 프롬프트
/feature-dev "결제 현황 대시보드의 설계 문서를
docs/blueprints/payment-dashboard.md로 작성해줘.
- 실시간 결제 현황 (오늘 건수/금액)
- 일별/월별 매출 차트
- 최근 거래 목록 (필터링, 페이지네이션)
- 결제 수단별 비율 차트
- DB 스키마는 docs/database/database-design.md를 참조할 것
아직 코드는 수정하지 마."

### 2.2 구현 프롬프트
/feature-dev "docs/blueprints/payment-dashboard.md와
docs/database/database-design.md의 내용을 엄격히 준수해서
개발을 진행해줘. 다크 모드 기본, 미니멀리스트 스타일로.
docs/design-system/design-tokens.css의 토큰 시스템을 반드시 사용할 것."
```

### 8.3 스프린트 회고 템플릿

```markdown
# Sprint [N] Retrospective

## AI 분석 데이터
- code-review 반복 이슈: [자동 수집]
- security-guidance 차단 건수: [자동 수집]
- standard-enforcer 위반 빈도: [자동 수집]

## 팀 논의 (AI가 잡지 못하는 영역)
### 잘한 것 (Keep)
-

### 개선할 것 (Problem)
-

### 시도할 것 (Try)
-

## 자동화된 개선 조치
- /hookify [이번 스프린트에서 발견된 반복 실수 규칙화]
- CLAUDE.md 업데이트 내용: [추가된 규칙 기술]
```

---

## 9. 기대 효과

### 정량적 효과

| 지표 | ASTRA 목표 | 개선율 |
|------|-----------|-------|
| 스프린트 주기 | 1주 (소규모 증분, 빠른 피드백) | 반복 주기 50% 단축 |
| 스프린트당 세레모니 시간 | 4시간 | 67% 절감 |
| 투입 인력 | 4~5명 | 50% 절감 |
| 코딩 표준 준수율 | 95%+ (자동 강제) | +30% 향상 |
| 코드 리뷰 소요 시간 | 20~40분 (자동) | 85~90% 단축 |
| 요구사항 변경 대응 | 1~2일 | 기존 2주+ 대비 대폭 단축 |
| 코딩 작업 시간 | 기존 대비 40~60% 단축 | METR 연구 기반 |
| 보안 취약점 발견 시점 | 코드 작성 시점 | 사후→사전 전환 |
| 설계 문서 최신율 | 100% (Living Document) | +70% 향상 |
| Definition of Done 검증 | 자동 (Gate 1-3) | 수동→자동 전환 |

### 정성적 효과

1. **스크럼의 본질에 집중**: 세레모니 시간이 줄어 "가치 전달"에 집중
2. **리뷰 문화 개선**: 스타일/표준 논쟁 제거 → 비즈니스 로직 토론의 장으로 전환
3. **회고의 실효성**: "개선하겠습니다" → "hookify 규칙으로 강제합니다"
4. **DE 참여도 향상**: 실시간 데모와 즉시 반영으로 프로젝트의 진정한 파트너 참여
5. **기술 부채 감소**: 작성 시점 품질 내장으로 "나중에 고치자" 원천 제거
6. **지식 이전 용이**: Living Document로 인수인계 비용 최소화

---

## 부록

### 부록 A: Claude Code 도구 빠른 참조

| 상황 | 사용 커맨드/도구 | 비고 |
|------|-----------------|------|
| 기능 설계 시작 | `/feature-dev [설명]` | 7단계 자동 워크플로우 |
| 표준 용어 확인 | `/lookup-term [한글 용어]` | 영문 약어/도메인/타입 |
| 국제 코드 조회 | `/lookup-code [코드]` | ISO 3166-1/2, E.164 (국가/지역/전화번호) |
| 국제 코드 컴포넌트 생성 | `/generate-intl-component [유형]` | 국가 선택기, 전화번호 입력, 지역 선택기 |
| DB 엔티티 생성 | `/generate-entity [한글 정의]` | DB 설계 문서 기반, Java/TypeScript/SQL |
| DB 설계 문서 갱신 | `/feature-dev` | `docs/database/database-design.md` 테이블 추가/변경 |
| DB 마이그레이션 생성 | `/feature-dev` | `docs/database/migration/` DDL 생성 |
| 테스트 케이스 작성 | `/feature-dev` | `docs/tests/test-cases/` 기능별 테스트 명세 |
| 테스트 결과 보고 | `/feature-dev` | `docs/tests/test-reports/` 스프린트별 보고서 |
| 통합 테스트 실행 | `/astra-integration-test` | 서버 실행 + Chrome MCP 자동 검증 |
| 코딩 표준 검사 | `/check-convention [대상]` | Java/TS/Python/CSS/SCSS |
| DB 네이밍 검사 | `/check-naming [대상]` | 표준 용어 사전 기반 |
| 커밋 | `/commit` | 자동 메시지 생성 |
| PR 생성 | `/commit-push-pr` | 커밋+푸시+PR 일괄 |
| 코드 리뷰 | `/code-review` | 5개 에이전트 병렬 |
| 훅 규칙 생성 | `/hookify [설명]` | 행동 방지 규칙 |
| 훅 규칙 확인 | `/hookify:list` | 현재 규칙 목록 |
| 최신 문서 조회 | `"use context7 - [질문]"` | 라이브러리 문서 |
| 브라우저 확인 | `chrome-devtools` MCP | 스냅샷/스크린샷/성능 |
| DB 쿼리 | `postgres` MCP | 직접 쿼리 실행 |

### 부록 A-2: 에이전트 빠른 참조

| 에이전트 | 모델 | 게이트 | 역할 |
|----------|------|--------|------|
| `astra-verifier` | Haiku | - | ASTRA 방법론 준수 여부 점검 |
| `naming-validator` | Haiku | Gate 1 | DB 네이밍 표준 검증 |
| `convention-checker` | Haiku | Gate 1/2 | 코딩 컨벤션 심층 분석 (Java/TS/Python/CSS/SCSS) |
| `blueprint-reviewer` | Sonnet | Gate 2 | 설계 문서 품질/일관성 검증 |
| `test-coverage-analyzer` | Haiku | Gate 2 | 테스트 전략/커버리지 분석 |
| `design-token-validator` | Haiku | Gate 2.5 | 디자인 토큰 시스템 준수 자동 검증 |
| `sprint-analyzer` | Sonnet | - | 스프린트 진척/회고 자동 분석 |
| `quality-gate-runner` | Sonnet | Gate 3 | Gate 1~3 통합 실행 |

> 모든 에이전트는 **읽기 전용** (Write/Edit 불가) — 분석과 보고만 수행합니다.

### 부록 B: 프롬프트 작성 가이드

**좋은 프롬프트의 5가지 요소:**

1. **What (무엇을)**: 만들어야 할 기능의 명확한 설명
2. **Why (왜)**: 비즈니스 목적과 사용자 가치
3. **Constraint (제약)**: 기술적 제약사항과 성능 요구사항
4. **Reference (참조)**: 관련 설계 문서, 기존 코드 경로
5. **Acceptance (기준)**: 완료 조건과 검증 방법

```
BAD:
"결제 기능을 만들어줘"

GOOD:
/feature-dev "결제 처리 모듈을 구현해줘.
- 카드 결제와 계좌이체를 지원
- PG사 API(이니시스)와 연동
- 결제 실패 시 3회까지 자동 재시도
- docs/blueprints/payment.md의 설계를 따를 것
- DB 스키마는 docs/database/database-design.md를 참조할 것
- 단위 테스트와 통합 테스트를 모두 작성할 것"
```

### 부록 C: 위험 관리

| 위험 | 확률 | 영향 | 대응 전략 |
|------|------|------|----------|
| AI 환각 (잘못된 코드 생성) | 중 | 중 | Gate 2 code-review로 검출, context7으로 최신 API 검증 |
| 복잡한 비즈니스 로직 오해 | 중 | 높음 | feature-dev Phase 3 명확화 질문 필수, DE 참여 |
| Claude API 장애 | 낮 | 높음 | 로컬 개발 환경 병행, 핵심 로직은 수동 백업 |
| 표준 용어 사전 미등록 용어 | 중 | 낮음 | standard_words.json 단어 조합으로 약어 생성 |
| 보안 취약점 미감지 | 낮 | 높음 | security-guidance 9패턴 + 최종 보안 감사 병행 |
| 1주 스프린트 번아웃 | 중 | 중 | AI가 반복 작업 흡수, 사람은 판단/의사결정에 집중 |
| 스크럼 세레모니 경시 | 중 | 중 | 시간은 줄이되 세레모니 자체는 반드시 유지 |

### 부록 D: AI 에이전트 작업 시간 추정 근거

본 문서의 작업 시간 추정치는 2025~2026년 실제 연구 데이터와 산업 사례를 기반으로 합니다.

#### 핵심 연구 데이터

| 출처 | 핵심 발견 | 적용 |
|------|----------|------|
| [METR - Time Horizons](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) | AI 50% 성공률 기준: Claude 3.7 Sonnet ~1시간, GPT-5.2 ~6.5시간 (2025년 말) | 복잡 작업의 자율 실행 시간 한계 |
| [METR - Developer Study](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) | 숙련 개발자 + AI 도구(Cursor/Claude): 2시간 규모 작업 기준 ad-hoc 사용 시 19% 느려짐 | 구조화된 워크플로우의 중요성 |
| [METR - Time Horizon Growth](https://metr.org/time-horizons/) | AI 자율 작업 시간이 ~7개월마다 2배 성장, 2024~2025년은 ~4개월마다 2배 | 2026년 기준 2~4시간 자율 작업 가능 추정 |

#### 산업 사례

| 출처 | 핵심 발견 | 적용 |
|------|----------|------|
| [Faros AI - Best AI Coding Agents 2026](https://www.faros.ai/blog/best-ai-coding-agents-2026) | Cursor: 소~중 규모 작업에 강점, 대규모 리팩토링에서 루핑 이슈 | 작업 단위를 소규모로 분할 필요 |
| [Anthropic - Agentic Coding Trends 2026](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf) | 엔지니어 1명 + Claude Code = 기존 팀 1개월 작업량 | 구조화된 스펙 기반 시 대폭 향상 |
| [TELUS/Zapier 사례](https://www.index.dev/blog/developer-productivity-statistics-with-ai-tools) | TELUS 30% 배포 속도 향상, 50만+ 시간 절감 / Zapier 89% 조직 도입 | 조직 수준 AI 도입 효과 |

#### 작업 유형별 현실적 소요 시간 (2026년 초, Claude Opus 4.6 / Sonnet 4.5 기준)

| 작업 유형 | AI 자율 실행 | 인간 검토·수정 | 총 소요 시간 |
|-----------|------------|-------------|------------|
| 코드베이스 분석 | 10~30분 | 30분~1시간 | 1~2시간 |
| 설계 문서 생성 | 15~30분 | 1~2시간 | 1.5~3시간 |
| 단순 기능 구현 (CRUD) | 30분~1시간 | 1~2시간 | 2~3시간 |
| 중간 기능 구현 (인증, API 연동) | 1~3시간 | 2~4시간 | 4~8시간 |
| 복잡 기능 구현 (멀티서비스, 복잡 비즈니스 로직) | 3~6시간 | 4~8시간 | 1~2일 |
| 자동 코드 리뷰 | 10~15분 | 10~20분 | 20~40분 |
| 단위 테스트 생성 | 코드와 동시 | 30분~1시간 | 코드와 동시 |
| UI 컴포넌트 생성 | 15~30분 | 1~2시간 (DSA 검수) | 1.5~3시간 |
| 설계 문서 기반 구현 (스펙 有) | 1~2시간 | 2~4시간 | 3~6시간 |
| 스펙 없는 기능 구현 (스펙 無) | 4~8시간 | 6~10시간 | 1~2일+ |

> **핵심 인사이트**: 설계 문서(스펙)의 품질이 AI 작업 시간을 결정적으로 좌우합니다.
> 좋은 스펙 기반 시 60분이면 가능한 작업이, 스펙 없이는 16시간 이상 소요될 수 있습니다.
> ASTRA가 Sprint 0에서 설계 문서를 먼저 작성하는 이유입니다.

#### 시간 추정의 한계

- AI 에이전트 성능은 **모델 버전, 코드베이스 크기, 도메인 복잡도**에 따라 큰 편차 발생
- METR 연구의 "19% 느려짐"은 **ad-hoc AI 사용** 기준이며, ASTRA처럼 **구조화된 워크플로우**에서는 30~60% 시간 단축 달성 가능
- AI 자율 작업 시간은 **~7개월마다 2배** 성장 중이므로, 본 문서의 시간 추정치는 **6~12개월마다 재검토** 필요
- 복잡한 비즈니스 로직, 아키텍처 의사결정, 도메인 특화 검증은 여전히 **인간 판단이 병목**
