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
- [개발 워크플로우](#개발-워크플로우)
4. [디자인 시스템 작성](#4-디자인-시스템-작성)
5. [블루프린트 작성](#5-블루프린트-작성)
6. [데이터베이스 설계](#6-데이터베이스-설계)
7. [블루프린트 기반 스프린트 작성](#7-블루프린트-기반-스프린트-작성)
8. [구현](#8-구현)
9. [테스트 시나리오 작성](#9-테스트-시나리오-작성)
10. [테스트 실행](#10-테스트-실행)
11. [PR / 리뷰](#11-pr--리뷰)
12. [스테이징 브랜치 머지](#12-스테이징-브랜치-머지)
13. [사용자 테스트](#13-사용자-테스트)
14. [메인 브랜치 머지](#14-메인-브랜치-머지)
- [부록](#부록)
  - [A: Claude Code 도구 빠른 참조](#부록-a-claude-code-도구-빠른-참조)
  - [A-2: 에이전트 빠른 참조](#부록-a-2-에이전트-빠른-참조)
  - [B: 프롬프트 작성 가이드](#부록-b-프롬프트-작성-가이드)
  - [C: 위험 관리](#부록-c-위험-관리)
  - [D: AI 에이전트 작업 시간 추정 근거](#부록-d-ai-에이전트-작업-시간-추정-근거)
  - [E: Sprint 0 프로젝트 셋업](#부록-e-sprint-0-프로젝트-셋업)
  - [F: 프로젝트 템플릿](#부록-f-프로젝트-템플릿)
  - [G: 기대 효과](#부록-g-기대-효과)
  - [H: 비용 효과](#부록-h-비용-효과)

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
| **P**lugin-powered Quality | 품질은 코드에 내장되는 것이다 | `astra-methodology`, `security-guidance`, `hookify` |

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
| Standardization | 작성 시점 자동 강제 | `astra-methodology` (PostToolUse 훅) |
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
| **코딩 표준 논쟁** | 리뷰마다 반복 | 원천 차단 | `astra-methodology`가 작성 시점 자동 적용 |
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
| Retrospective | 1.5시간 | 30분 | `sprint-analyzer` AI 분석 → `hookify` 자동화 |
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
| Product Backlog | + `docs/sprints/` 프롬프트 맵 연결 |
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


## 개발 워크플로우

> **사전 준비**: 아래 워크플로우는 **Sprint 0(프로젝트 초기 셋업)이 완료된 상태**를 전제합니다.
> Sprint 0에서는 개발환경 설정(`/astra-setup`), 프로젝트 구조 생성(`/project-init`), 디자인 시스템 구축, CLAUDE.md 작성, hookify 규칙 설정 등을 수행합니다.
> 상세 내용은 [부록 E: Sprint 0 프로젝트 셋업](#부록-e-sprint-0-프로젝트-셋업)을 참고하세요.

```
[Sprint 0]
디자인 시스템 작성

[기능 스프린트]
블루프린트 작성 → 데이터베이스 설계 → 스프린트 작성 → 구현 → 테스트 시나리오 → 테스트 실행 → PR/리뷰
                                                                                                       ↓
                                               메인 브랜치 머지 ← 사용자 테스트 ← 스테이징 브랜치 머지 ←──┘
```

---

## 4. 디자인 시스템 작성

Sprint 0에서 DSA가 주관하여 프로젝트의 **디자인 시스템**을 구축합니다. 디자인 시스템은 AI가 일관된 UI를 생성하기 위한 핵심 기반이며, `docs/design-system/`에서 관리합니다.

> **핵심 원칙**: 디자인 시스템 없이 AI가 생성한 UI는 화면마다 스타일이 달라집니다. 토큰 시스템이 AI의 디자인 가드레일 역할을 합니다.

### 4.1 디자인 시스템 디렉토리 구조

```
docs/design-system/
├── design-tokens.css       # CSS Custom Properties (컬러, 폰트, 스페이싱)
├── tailwind.config.js      # Tailwind 기반 프로젝트의 경우
├── components.md           # 핵심 컴포넌트 스타일 가이드
├── layout-grid.md          # 레이아웃 그리드 시스템
└── references/             # 디자인 레퍼런스/무드보드 이미지
```

### 4.2 디자인 토큰 정의

디자인 토큰은 컬러, 타이포그래피, 스페이싱 등의 디자인 값을 CSS Custom Properties로 정의합니다.

```
# 디자인 토큰 파일 생성
/feature-dev "docs/design-system/design-tokens.css에 프로젝트 디자인 토큰을 정의해줘.
- 컬러 팔레트 (Primary, Secondary, Neutral, Semantic)
- 타이포그래피 (Font Family, Size Scale, Weight, Line Height)
- 스페이싱 (4px 기반 그리드: 4, 8, 12, 16, 24, 32, 48, 64)
- 브레이크포인트 (모바일: 375px, 태블릿: 768px, 데스크톱: 1024px, 와이드: 1440px)
- 그림자, 라운딩, 트랜지션
아직 코드는 수정하지 마."
```

### 4.3 컴포넌트 스타일 가이드

핵심 UI 컴포넌트의 디자인 규격을 문서화합니다.

```
# 컴포넌트 스타일 가이드 작성
/feature-dev "docs/design-system/components.md에 핵심 컴포넌트 스타일 가이드를 작성해줘.
- Button (Primary, Secondary, Ghost, Danger — 각 상태: default, hover, active, disabled)
- Input (Text, Password, Search, TextArea — 상태: default, focus, error, disabled)
- Card, Modal, Toast/Alert
- Navigation (Header, Sidebar, Breadcrumb, Tab)
- Table, Pagination
- 각 컴포넌트는 design-tokens.css의 토큰만 사용할 것
아직 코드는 수정하지 마."
```

### 4.4 레이아웃 그리드 시스템

```
# 레이아웃 그리드 시스템 정의
/feature-dev "docs/design-system/layout-grid.md에 레이아웃 그리드 시스템을 정의해줘.
- 12컬럼 그리드 (거터: 16px 모바일, 24px 데스크톱)
- 페이지 레이아웃 패턴 (Sidebar + Content, Full-width, Centered)
- 반응형 규칙 (모바일 퍼스트)
- 컨테이너 최대 너비
아직 코드는 수정하지 마."
```

### 4.5 디자인 시스템 프리뷰 페이지 생성

디자인 토큰, 컴포넌트, 레이아웃 그리드가 정의되면, **실제 브라우저에서 확인할 수 있는 프리뷰 페이지**를 생성합니다. 문서만으로는 컬러, 타이포그래피, 컴포넌트 상태 등을 정확히 판단하기 어렵기 때문에, DSA와 팀 전체가 시각적으로 검증할 수 있는 페이지가 필요합니다.

> **왜 프리뷰 페이지가 필요한가?**
> - 디자인 토큰 값(컬러, 폰트, 스페이싱)을 **실제 렌더링 결과**로 확인
> - 컴포넌트의 각 상태(default, hover, active, disabled)를 **인터랙티브하게 검증**
> - DSA가 `chrome-devtools` MCP로 반응형/접근성을 **즉시 테스트**
> - 기능 스프린트에서 AI가 생성하는 UI의 **기준점(Baseline)** 역할

```
# 디자인 시스템 프리뷰 페이지 생성
/frontend-design "docs/design-system/의 디자인 토큰, 컴포넌트 스타일 가이드,
레이아웃 그리드를 한눈에 확인할 수 있는 디자인 시스템 프리뷰 페이지를 만들어줘.
- 컬러 팔레트 스와치 (Primary, Secondary, Neutral, Semantic 전체)
- 타이포그래피 스케일 미리보기 (각 사이즈/웨이트 조합)
- 스페이싱 시스템 시각화 (4px 그리드 단위별 블록)
- 핵심 컴포넌트 쇼케이스 (Button, Input, Card, Modal, Toast — 모든 상태 포함)
- 레이아웃 그리드 오버레이 (12컬럼 그리드 시각화)
- 반응형 브레이크포인트별 미리보기
- docs/design-system/design-tokens.css의 토큰만 사용할 것"
```

> **프리뷰 페이지 검증 (DSA 주관):**
> - `chrome-devtools` MCP로 각 뷰포트(375px, 768px, 1024px, 1440px)에서 렌더링 확인
> - 컬러 대비율, 포커스 표시 등 접근성 기본 항목 확인
> - 이슈 발견 시 디자인 토큰 또는 컴포넌트 가이드를 수정하고 프리뷰 페이지에 즉시 반영

### 4.6 디자인 시스템 완료 체크리스트

- [ ] 컬러 팔레트 정의 완료 (접근성 대비율 4.5:1 이상)
- [ ] 타이포그래피 스케일 정의 완료
- [ ] 스페이싱 시스템 정의 완료 (4px 또는 8px 기반)
- [ ] 핵심 컴포넌트 스타일 가이드 작성 완료
- [ ] 레이아웃 그리드 시스템 정의 완료
- [ ] **디자인 시스템 프리뷰 페이지 생성 및 DSA 검증 완료**
- [ ] 디자인 레퍼런스/무드보드 수집 완료 (해당 시)

---

## 5. 블루프린트 작성

기능 구현에 앞서 **설계 문서(Blueprint)**를 먼저 작성합니다. 블루프린트는 AI가 정확한 코드를 생성하기 위한 핵심 입력이며, `docs/blueprints/`에서 관리합니다.

> **핵심 원칙**: 좋은 블루프린트 = 좋은 코드. 스펙 품질이 AI 결과물 품질을 결정합니다.
> (스펙 기반 시 1~2시간, 스펙 없이 4~8시간+ 소요 — [부록 D](#부록-d-ai-에이전트-작업-시간-추정-근거) 참고)

### 5.1 기능 설계 문서 작성

```
# 핵심 기능의 설계 문서 자동 생성
/feature-dev "JWT 기반 사용자 인증 시스템의 설계 문서를
docs/blueprints/auth.md로 작성해줘.
- 회원가입, 로그인, 토큰 갱신, 권한 관리(RBAC) 기능을 포함
- 비밀번호는 bcrypt 해싱
- Access Token 유효기간 30분, Refresh Token 7일
- DB 스키마는 docs/database/database-design.md를 참조할 것
아직 코드는 수정하지 마."

# → VA/DE가 생성된 docs/blueprints/auth.md를 직접 열어 검토 및 수정
# → DE 승인 후 다음 단계 진행
```

### 5.2 블루프린트 완료 체크리스트

- [ ] 기능 설계 문서 작성 완료 (`docs/blueprints/`)
- [ ] DE 승인 완료

---

## 6. 데이터베이스 설계

블루프린트가 완료되면, 기능에 필요한 **데이터베이스 테이블을 중앙 DB 설계 문서에 반영**합니다. 모든 테이블 설계는 `docs/database/database-design.md` 단일 문서에서 관리합니다.

> **왜 하나의 문서인가?**
> - AI가 전체 테이블 구조와 연관관계를 **한번에 인식**하여 정합성 있는 설계 가능
> - 테이블 간 FK 참조, 컬럼 중복, 네이밍 일관성을 단일 컨텍스트에서 검증

### 6.1 DB 설계 문서 반영

```
# 블루프린트 기반 DB 테이블 설계
/feature-dev "docs/blueprints/auth.md 블루프린트를 분석해서
필요한 데이터베이스 테이블을 docs/database/database-design.md에 설계해줘.
- 블루프린트의 기능 요구사항에서 필요한 테이블, 컬럼, 관계를 도출할 것
- 기존 테이블과의 FK 관계를 ERD와 관계 요약 섹션에도 반영할 것
- 표준 용어 사전을 준수할 것 (/lookup-term 활용)
아직 코드는 수정하지 마."

# 테이블을 직접 지정하여 반영할 수도 있음
/feature-dev "docs/database/database-design.md에 인증 모듈 테이블을
추가/갱신해줘:
- TB_COMM_USER (사용자), TB_COMM_TRMS (약관), TH_COMM_USER_AGRE (동의이력)
- 기존 테이블과의 FK 관계를 ERD와 관계 요약 섹션에도 반영할 것
- 표준 용어 사전을 준수할 것 (/lookup-term 활용)
아직 코드는 수정하지 마."

# 표준 용어 조회
/lookup-term 결제금액
/lookup-term 주문번호
```

### 6.2 국제 코드 표준 적용 (해당 시)

전화번호 입력, 국가/지역 선택기, 주소 양식 등 국제 코드가 필요한 기능이 있을 때 적용합니다.

| 표준 | 용도 | DB 컬럼 규칙 |
|------|------|-------------|
| ISO 3166-1 (alpha-2) | 국가 코드 (`KR`, `US`, `JP`) | `NATN_CD CHAR(2)` |
| ISO 3166-2 | 지역 코드 (`KR-11`, `US-CA`) | `RGN_CD VARCHAR(6)` |
| ITU-T E.164 | 국제 전화번호 (`+821012345678`) | `INTL_TELNO VARCHAR(15)` |

```
/lookup-code KR
/lookup-code US-CA
/lookup-code +82
```

### 6.3 마이그레이션 SQL 작성

```
# 마이그레이션 SQL 기록
/feature-dev "docs/database/database-design.md에서 이번에 추가된 주문 모듈 테이블의
마이그레이션 SQL을 docs/database/migration/v1.1.0-order.sql로 작성해줘.
- CREATE TABLE 문 + 인덱스 + FK 제약조건 포함
- 롤백 SQL도 함께 작성할 것
아직 실제 DB에는 적용하지 마."
```

### 6.4 데이터베이스 설계 완료 체크리스트

- [ ] DB 설계 문서에 테이블 반영 완료 (`docs/database/database-design.md`)
- [ ] 표준 용어 사전 준수 확인 (`/lookup-term`)
- [ ] 국제 코드 표준 적용 확인 (해당 시)
- [ ] 마이그레이션 SQL 작성 완료

---

## 7. 블루프린트 기반 스프린트 작성

블루프린트가 완료되면, 이를 기반으로 스프린트를 계획합니다. `/sprint-plan` 명령으로 스프린트 문서를 초기화하고, 블루프린트의 기능을 스프린트 백로그로 분배합니다.

### 7.1 스프린트 초기화

```
# 스프린트 문서 생성 (프롬프트 맵, 진행 추적, 회고 템플릿)
/sprint-plan 1
```

> 생성되는 파일:
> - `docs/sprints/sprint-1/prompt-map.md` — 기능별 프롬프트 계획
> - `docs/sprints/sprint-1/progress.md` — 진행 추적 테이블
> - `docs/sprints/sprint-1/retrospective.md` — 회고 템플릿

### 7.2 Sprint Planning (1시간)

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

### 7.3 프롬프트 맵 작성

블루프린트의 각 기능을 프롬프트 단위로 분해하여 `prompt-map.md`에 기록합니다.

```markdown
# Sprint 1 프롬프트 맵

## 스프린트 목표
[이번 스프린트에서 달성할 비즈니스 가치를 서술]

## 기능 1: 사용자 인증
### 1.1 블루프린트 참조
- docs/blueprints/auth.md
- docs/database/database-design.md (인증 모듈)

### 1.2 구현 프롬프트
/feature-dev "docs/blueprints/auth.md와
docs/database/database-design.md의 내용을 엄격히 준수해서
개발을 진행해줘."

## 기능 2: 결제 대시보드
### 2.1 블루프린트 참조
- docs/blueprints/payment-dashboard.md

### 2.2 구현 프롬프트
/feature-dev "docs/blueprints/payment-dashboard.md와
docs/database/database-design.md의 내용을 엄격히 준수해서
개발을 진행해줘."
```

### 7.4 Backlog Refinement (30분)

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

---

## 8. 구현

스프린트 프롬프트 맵에 따라 실제 코드를 구현합니다. 구현 중에는 **Gate 1(작성 시점)** 품질 게이트가 자동 적용됩니다.

### 8.1 설계 문서 기반 구현

```
/feature-dev "docs/blueprints/auth.md와
docs/database/database-design.md의 내용을 엄격히 준수해서
개발을 진행해줘. 테스트는 docs/tests/test-cases/sprint-1/auth-test-cases.md를
참조하여 작성하고, 구현이 끝나면 모든 테스트를 실행하고
결과를 docs/tests/test-reports/에 보고해."
```

> **이 한 줄의 프롬프트로 자동 실행되는 것들:**
> 1. `code-explorer`가 기존 코드베이스 분석 (2~3개 병렬)
> 2. 명확화 질문 (엣지 케이스, 비즈니스 규칙 확인)
> 3. `code-architect`가 구현 계획 제시 (2~3개 병렬)
> 4. 승인 후 코드 작성
>    - `astra-methodology`가 금칙어/네이밍 자동 검사 (PostToolUse 훅)
>    - `security-guidance`가 보안 패턴 자동 차단 (PreToolUse 훅)
>    - `coding-convention` 스킬이 컨벤션 자동 적용
> 5. `code-reviewer`가 품질 검사 (3개 병렬)
> 6. 완료 요약 문서 생성

### 8.2 UI 구현

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
```

### 8.3 실시간 검증 (chrome-devtools MCP)

```
# 레이아웃 확인
"현재 페이지의 스냅샷을 찍어서 레이아웃을 확인해줘"

# API 동작 검증
"API 호출이 정상적으로 이루어지는지 네트워크 요청을 확인해줘"

# 에러 확인
"콘솔에 에러가 있는지 확인해줘"

# 반응형 확인 (뷰포트 전환)
"모바일 뷰포트(375x667)로 전환하고 레이아웃을 확인해줘"
```

### 8.4 최신 API 참조 (context7 MCP)

```
"use context7 - Spring Boot 3에서 WebClient로 비동기 HTTP 요청하는 방법"
"use context7 - Prisma에서 트랜잭션을 사용하는 방법"
"use context7 - Next.js 15에서 Server Actions 문법"
```

### 8.5 커밋

```
# 기능 완료 시마다 커밋
/commit
```

### 8.6 Gate 1: WRITE-TIME (자동 적용)

구현 중 모든 코드 작성(Write/Edit)에 자동 적용되는 품질 게이트입니다.

| 도구 | 검사 내용 | 동작 방식 |
|------|----------|----------|
| `security-guidance` | 9개 보안 패턴 (eval, innerHTML 등) | PreToolUse 훅, **차단** (exit 2) |
| `astra-methodology` | 금칙어 + 네이밍 규칙 | PostToolUse 훅, 경고 (exit 0) |
| `hookify` | 프로젝트별 커스텀 규칙 | PreToolUse/PostToolUse 훅 |
| `coding-convention` 스킬 | Java/TS/RN/Python/CSS/SCSS 컨벤션 자동 적용 | Skill (자동 감지) |
| `data-standard` 스킬 | 공공 데이터 표준 용어 사전 적용 | Skill (DB 코드 시 자동 감지) |
| `code-standard` 스킬 | ISO 3166-1/2, ITU-T E.164 표준 적용 | Skill (전화번호/국가/주소 시 자동 감지) |

### 8.7 요구사항 변경 대응

스프린트 중간에 요구사항 변경이 발생하면 다음 절차를 따릅니다.

```
# 1. 영향도 분석 (30분~1시간)
/feature-dev "결제 수단에 '간편결제(카카오페이)' 추가 요청이 들어왔어.
기존 코드베이스와 docs/database/database-design.md를 참조해서
결제 모듈의 영향 범위를 분석해줘.
아직 코드는 수정하지 마."

# 2. 블루프린트 수정 (1~2시간)
# → docs/blueprints/payment.md에 간편결제 섹션 추가
# → docs/database/database-design.md에 테이블 변경사항 반영

# 3. 코드 반영 (4~8시간)
/feature-dev "docs/blueprints/payment.md와
docs/database/database-design.md의 업데이트된 내용을 반영해서
간편결제(카카오페이) 기능을 구현해줘.
기존 결제 로직에 영향이 없도록 PaymentProvider 패턴을 사용할 것."

# 4. 자동 품질 검증 (30분~1시간)
/code-review
```

---

## 9. 테스트 시나리오 작성

스프린트에서 구현된 기능을 기반으로 E2E 테스트 시나리오를 생성합니다. `/test-scenario` 명령이 블루프린트, DB 설계, 라우트, API 엔드포인트를 분석하여 종합적인 테스트 시나리오를 자동 작성합니다.

### 9.1 E2E 테스트 시나리오 생성

```
# 블루프린트, DB, 라우트 기반 E2E 시나리오 자동 생성
/test-scenario
```

> `/test-scenario`가 자동으로 분석하는 항목:
> - `docs/blueprints/` — 기능 요구사항
> - `docs/database/database-design.md` — 데이터 모델
> - 라우트/API 엔드포인트 — 화면 흐름
> - 기존 테스트 코드 — 누락된 시나리오

### 9.2 예시: 스프린트 1 테스트 시나리오 작성

스프린트 1에서 인증 기능 구현이 완료된 후, `/test-scenario` 명령으로 테스트 시나리오를 작성하는 예시입니다.

```
# 스프린트 1 테스트 시나리오 자동 생성
/test-scenario 스프린트 1에 대한 테스트 시나리오 작성해줘.

# → /test-scenario가 자동으로 수행하는 작업:
# 1. docs/blueprints/ 스캔 — 스프린트 1 기능 요구사항 수집
# 2. docs/database/database-design.md 분석 — 관련 테이블 구조 파악
# 3. src/ 라우트/API 엔드포인트 탐색 — 화면 흐름 및 API 경로 매핑
# 4. 기존 테스트 코드 확인 — 누락된 시나리오 식별
#
# → 생성 결과: docs/tests/test-cases/sprint-1/ 에 테스트 시나리오 문서 생성
#   - E2E 시나리오 (회원가입→로그인→토큰갱신→권한검증 흐름)
#   - 기능별 테스트 케이스 (Given-When-Then 형식)
#   - 엣지 케이스 및 에러 시나리오
```

---

## 10. 테스트 실행

테스트 시나리오를 기반으로 실제 테스트를 수행합니다. `/test-run` 명령으로 서버 실행 + Chrome MCP 통합 테스트를 자동 수행합니다.

### 10.1 통합 테스트 실행

```
# 서버 실행 + Chrome MCP 통합 테스트 자동 수행
/test-run

# → 서버 자동 실행 + 로그 모니터링
# → 페이지 검증 (스냅샷, 레이아웃)
# → API 동작 확인 (네트워크 요청)
# → 성능 측정 (Core Web Vitals)
# → 콘솔 에러 확인
```

### 10.2 수동 상세 검증

```
# API 연동 테스트
"결제 API와 주문 API 간의 연동을 테스트해줘. 네트워크 요청을 모니터링하고 응답을 검증해."

# DB 데이터 정합성 확인
"docs/database/database-design.md의 FK 관계 정의와 실제 DB 스키마가 일치하는지 확인해줘"

# 성능 프로파일링
"전체 페이지의 성능 트레이스를 실행하고 병목 지점을 분석해줘"

# 크로스 브라우저/반응형 테스트
"모바일 뷰포트(375x667)로 전환하고 레이아웃을 확인해줘"
"태블릿 뷰포트(768x1024)로 전환하고 확인해줘"
```

### 10.3 테스트 결과 보고서

```
/feature-dev "전체 테스트 실행 결과를 docs/tests/test-reports/sprint-1-report.md로
작성해줘. 다음을 포함할 것:
- 모듈별 테스트 통과/실패 현황
- 테스트 커버리지 요약
- 발견된 이슈 및 조치 내역
- docs/tests/test-strategy.md의 목표 대비 달성률"
```

### 10.4 예시: 스프린트 1 테스트 실행

스프린트 1에서 인증 기능의 테스트 시나리오가 작성된 후, 실제 테스트를 수행하는 전체 흐름 예시입니다.

#### Step 1: 통합 테스트 자동 실행

```
# 서버 실행 + Chrome MCP 통합 테스트 자동 수행
/test-run

# → 자동 실행 흐름:
# 1. 서버 자동 실행 + 로그 모니터링
# 2. 회원가입 페이지 접근 → 폼 입력 → 제출 → 성공 확인
# 3. 로그인 페이지 접근 → 인증 → 토큰 발급 확인
# 4. 네트워크 요청 확인 (POST /auth/signup, POST /auth/login 응답 검증)
# 5. 콘솔 에러 0건 확인
# 6. 성능 측정 (Core Web Vitals)
```

#### Step 2: 수동 상세 검증

```
# 인증 API 엔드포인트 동작 검증
"회원가입 → 로그인 → 토큰 갱신 흐름을 순서대로 테스트해줘.
각 단계의 네트워크 요청과 응답을 확인하고 결과를 알려줘."

# 엣지 케이스 검증
"잘못된 비밀번호로 로그인을 시도해줘. 에러 응답이 올바른지 확인해."
"만료된 Access Token으로 보호된 API를 호출해줘. 401 응답이 오는지 확인해."

# 반응형 확인 (로그인/회원가입 폼)
"모바일 뷰포트(375x667)로 전환하고 로그인 페이지 레이아웃을 확인해줘"

# DB 데이터 정합성 확인
"회원가입 후 TB_COMM_USER 테이블에 데이터가 정상 입력되었는지 확인해줘"
```

#### Step 3: 테스트 결과 보고서 작성

```
/feature-dev "전체 테스트 실행 결과를 docs/tests/test-reports/sprint-1-report.md로
작성해줘. 다음을 포함할 것:
- 인증 모듈 테스트 통과/실패 현황
- 테스트 커버리지 요약 (목표: 70%+)
- 발견된 이슈 및 조치 내역
- docs/tests/test-strategy.md의 목표 대비 달성률"

# → 생성 결과 예시 (docs/tests/test-reports/sprint-1-report.md):
#
# ## 테스트 결과 요약
# | 모듈     | 전체 | 통과 | 실패 | 커버리지 |
# |----------|------|------|------|----------|
# | 인증     | 15   | 14   |  1   | 82%      |
# | 권한(RBAC)| 8   |  8   |  0   | 78%      |
#
# ## 발견된 이슈
# - ISS-001: Refresh Token 만료 시 에러 메시지가 일반적 → 수정 완료
#
# ## 목표 대비 달성률
# - 커버리지 목표 70% → 실제 80% ✅
# - 고위험 시나리오 100% 커버 ✅
```

---

## 11. PR / 리뷰

구현과 테스트가 완료되면 PR을 생성하고 코드 리뷰를 수행합니다. `/pr-merge` 명령으로 커밋→PR 생성→리뷰→수정→머지를 일괄 처리할 수 있습니다.

### 11.1 PR 생성 + 코드 리뷰

```
# 방법 1: 전체 자동화 사이클 (커밋→PR→리뷰→수정→머지)
/pr-merge

# 방법 2: 단계별 수동 실행
/commit-push-pr          # 커밋 + 푸시 + PR 생성
/code-review             # 5개 에이전트 병렬 코드 리뷰 (80점+ 고신뢰 이슈만 보고)
```

### 11.2 Design Review (DSA 주관)

UI 기능이 포함된 경우, DSA가 디자인 검수를 수행합니다.

```
[Design Review]
  ├─ DSA가 chrome-devtools MCP로 실제 화면 확인
  │   ├─ 디자인 토큰 준수 여부 확인
  │   ├─ 반응형 레이아웃 확인 (뷰포트 전환)
  │   └─ 접근성 기본 확인
  │
  └─ 이슈 수정
      ├─ DSA: "이 버튼 색상이 토큰과 다릅니다", "여백이 8px 그리드에 안 맞습니다"
      ├─ PE: 프롬프트에 디자인 피드백 반영 → AI 재생성 (5~10분)
      └─ DSA: 수정 결과 즉시 확인 → 승인
```

### 11.3 Gate 2: REVIEW-TIME

| 도구 | 검사 내용 |
|------|----------|
| `feature-dev` (내장 code-reviewer) | 코드 품질/버그/컨벤션 (3개 에이전트 병렬) |
| `/code-review` | CLAUDE.md 준수, 버그, 이력 분석 (5개 에이전트 병렬, 80점+ 필터링) |
| `blueprint-reviewer` 에이전트 | 설계 문서 품질/일관성 검증 (Sonnet, 읽기 전용) |
| `test-coverage-analyzer` 에이전트 | 테스트 전략/커버리지 분석 (Haiku, 읽기 전용) |
| `convention-validator` 에이전트 | 코딩 컨벤션 검증 (Haiku, 읽기 전용) |

### 11.4 Gate 2.5: DESIGN-TIME (DSA 검수)

| 검수 항목 | 확인 방법 |
|----------|----------|
| 디자인 토큰 준수 | `chrome-devtools` 스냅샷 + `design-token-validator` 에이전트 (Haiku, 자동 검증) |
| 컴포넌트 일관성 | 화면별 비교 |
| 반응형 레이아웃 | `chrome-devtools` 뷰포트 전환 |
| 접근성 기본 확인 | 컬러 대비, 포커스 확인 |

이슈 발견 시: DSA 피드백 → PE 프롬프트 수정 → AI 재생성 → DSA 재검수 (1시간 내 완료)

### 11.5 추가 품질 검사

```
/check-convention src/      # 코딩 컨벤션 검사
/check-naming src/entity/   # DB 네이밍 표준 검사
```

### 11.6 예시: 스프린트 1 PR 및 리뷰 실행

스프린트 1에서 인증 기능 구현이 완료된 후 PR 생성부터 머지까지의 전체 흐름 예시입니다.

#### Step 1: 커밋 + PR 생성 + 코드 리뷰 + 머지 (자동화)

```
# /pr-merge 한 번으로 전체 사이클 자동 실행
/pr-merge

# → 자동 실행 흐름:
# 1. 변경사항 커밋 (자동 커밋 메시지 생성)
# 2. 기능 브랜치 푸시 (feature/sprint-1-auth → origin)
# 3. PR 생성 (스프린트 1 인증 기능 구현)
# 4. 코드 리뷰 (5개 에이전트 병렬 — 80점+ 고신뢰 이슈만 보고)
# 5. 발견된 이슈 자동 수정
# 6. 재리뷰 → 통과 시 머지
```

#### Step 2: 단계별 수동 실행 (세밀한 제어가 필요한 경우)

```
# 1단계: 커밋 + 푸시 + PR 생성
/commit
git push -u origin feature/sprint-1-auth
gh pr create --title "feat: Sprint 1 사용자 인증 구현" --body "## Summary
- JWT 기반 회원가입/로그인/토큰갱신 구현
- RBAC 권한 관리
- docs/blueprints/auth.md 설계 준수

## Test plan
- [ ] 단위 테스트 통과 확인
- [ ] API 통합 테스트 확인
- [ ] 보안 패턴 검사 통과"

# 2단계: 코드 리뷰 (5개 에이전트 병렬)
/code-review

# 3단계: 리뷰 결과 확인 후 이슈 수정
# → 고신뢰 이슈(80점+)만 보고되므로 중요 항목에 집중

# 4단계: 품질 검사
/check-convention src/
/check-naming src/entity/

# 5단계: 수정사항 커밋 + 재리뷰
/commit
/code-review

# 6단계: 머지
gh pr merge --squash
```

#### Step 3: Design Review (UI 포함 시, DSA 주관)

```
# DSA가 chrome-devtools MCP로 실제 화면 확인
"로그인 페이지의 스냅샷을 찍어서 디자인 토큰 준수 여부를 확인해줘"
"모바일 뷰포트(375x667)로 전환하고 로그인 폼 레이아웃을 확인해줘"

# DSA 피드백 반영
# → "비밀번호 입력 필드의 에러 상태 컬러가 토큰과 다릅니다"
# → PE가 프롬프트 수정 → AI 재생성 (5~10분) → DSA 재검수
```

#### Step 4: Gate 2 품질 검증 결과 예시

```
[코드 리뷰 결과 — Sprint 1 인증 기능]
┌─────────────────────────────────────────────┐
│ code-reviewer (3개 에이전트)     ✅ 통과       │
│ convention-validator            ✅ 위반 0건   │
│ blueprint-reviewer              ✅ 설계 일치   │
│ test-coverage-analyzer          ✅ 커버리지 82%│
│ security-guidance               ✅ 보안 이슈 0 │
└─────────────────────────────────────────────┘
→ 전체 Gate 2 통과 — 스테이징 머지 가능
```

---

## 12. 스테이징 브랜치 머지

테스트를 통과한 기능 브랜치를 스테이징(staging/develop) 브랜치에 머지합니다.

### 12.1 머지 전 품질 확인

```
# 최종 코딩 컨벤션 검사
/check-convention src/

# DB 네이밍 표준 검사
/check-naming src/entity/

# 콘솔 에러 0건 확인
"콘솔에 에러가 있는지 확인해줘"
```

### 12.2 스테이징 브랜치 머지

```
# PR 생성 → 리뷰 → 머지 자동화 (staging/develop 브랜치 대상)
/pr-merge
```

> **스테이징 브랜치의 역할:**
> - 사용자 테스트(UAT)를 위한 통합 환경
> - 모든 기능 브랜치가 스테이징에 머지된 후, 실제 사용자 테스트 진행
> - 메인 브랜치 머지 전 최종 검증 단계

---

## 13. 사용자 테스트

스테이징 환경에서 **실제 사용자(DE, 이해관계자)**가 직접 시스템을 검증합니다. AI가 대체할 수 없는 **도메인 전문 판단과 사용성 평가** 영역입니다.

### 13.1 Sprint Review (1시간)

```
[Sprint Review]
  ├─ 30분: 실시간 데모 (chrome-devtools MCP)
  │   ├─ 별도 데모 준비 불필요 - 스테이징 환경에서 즉시 시연
  │   ├─ 다양한 뷰포트 실시간 전환 (모바일/태블릿/데스크톱)
  │   ├─ 네트워크 요청 실시간 확인 (API 동작 증명)
  │   └─ 성능 트레이스 결과 공유
  │
  └─ 30분: DE 피드백 + 즉시 반영
      ├─ DE: "이 부분은 이렇게 바꿔주세요"
      ├─ PE: 프롬프트 수정 → AI 재구현 (5~10분)
      └─ 변경 결과 즉시 데모
```

### 13.2 사용자 인수 테스트 (UAT)

DE와 이해관계자가 스테이징 환경에서 직접 테스트합니다.

**UAT 체크리스트:**
- [ ] 핵심 비즈니스 시나리오 동작 확인
- [ ] 데이터 정합성 확인 (실제 데이터 유사 환경)
- [ ] UI/UX 사용성 평가
- [ ] 엣지 케이스 및 예외 상황 확인
- [ ] 성능 체감 확인 (응답 속도, 페이지 로딩)

### 13.3 피드백 반영

사용자 테스트에서 발견된 이슈는 즉시 수정하거나 다음 스프린트 백로그에 등록합니다.

| 이슈 유형 | 대응 | 시간 |
|----------|------|------|
| 즉시 수정 가능 | PE가 프롬프트 수정 → AI 재구현 | 30분~2시간 |
| 설계 변경 필요 | 블루프린트 수정 → 다음 스프린트 반영 | 백로그 등록 |
| 요구사항 변경 | 영향도 분석 → DE 우선순위 결정 | 1~2일 |

### 13.4 Sprint Retrospective (30분)

```
[AI 강화 회고]
  ├─ 10분: 스프린트 데이터 기반 자동 분석 (sprint-analyzer 에이전트, Sonnet)
  │   ├─ code-review에서 반복된 이슈 패턴
  │   ├─ security-guidance 차단 이력
  │   ├─ astra-methodology 위반 빈도
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
```

---

## 14. 메인 브랜치 머지

사용자 테스트를 통과한 스테이징 브랜치를 메인(main/master) 브랜치에 머지합니다. 최종 품질 게이트(Gate 3)를 실행하고, 릴리스를 준비합니다.

### 14.1 Gate 3: BRIDGE-TIME (최종 품질 게이트)

```
# 전체 코드 품질 검사
/code-review
/check-convention src/
/check-naming src/entity/

# 콘솔 에러 0건 확인
"콘솔에 에러가 있는지 확인해줘"

# DSA 최종 디자인 검수 (전체 화면 일관성)
# quality-gate-runner 에이전트가 Gate 1~3 통합 실행 (Sonnet, 읽기 전용)
```

### 14.2 품질 게이트 통과 기준 요약

| 게이트 | 통과 기준 | 차단 시 조치 |
|--------|----------|-------------|
| Gate 1 | security-guidance 경고 0건, 금칙어 0건 | 즉시 수정 후 재작성 |
| Gate 2 | code-review 고신뢰 이슈 0건, 커버리지 70%+ | fix now / fix later 결정 |
| Gate 2.5 | DSA 디자인 검수 승인 | 프롬프트 수정 → 재생성 → 재검수 |
| Gate 3 | convention/naming 위반 0건, 콘솔 에러 0건 | 일괄 수정 후 배포 |

### 14.3 메인 브랜치 머지

```
# 스테이징 → 메인 브랜치 머지
/pr-merge
```

### 14.4 릴리스 산출물 생성

```
# 운영 매뉴얼 자동 생성
/feature-dev "프로젝트의 운영 매뉴얼을 docs/delivery/operation-manual.md로
작성해줘. 배포 절차, 환경 변수, 모니터링 포인트, 장애 대응 가이드를 포함할 것.
아직 코드는 수정하지 마."

# 브랜치 정리
/clean_gone
```

---

## 부록

### 부록 A: Claude Code 도구 빠른 참조

| 상황 | 사용 커맨드/도구 | 비고 |
|------|-----------------|------|
| 전역 개발환경 설정 | `/astra-setup` | 전역 설정, MCP, 플러그인 자동 구성 |
| 빠른 참조 가이드 | `/astra-guide` | 워크플로우, 커맨드, 품질 게이트 요약 |
| 프로젝트 초기 셋업 | `/project-init [프로젝트명]` | Sprint 0 디렉토리 구조 + 템플릿 생성 |
| Sprint 0 체크리스트 | `/project-checklist` | Sprint 0 완료 여부 검증 |
| 스프린트 초기화 | `/sprint-plan [N]` | 프롬프트 맵, 진행 추적, 회고 템플릿 생성 |
| 기능 설계 시작 | `/feature-dev [설명]` | 7단계 자동 워크플로우 |
| 표준 용어 확인 | `/lookup-term [한글 용어]` | 영문 약어/도메인/타입 |
| 국제 코드 조회 | `/lookup-code [코드]` | ISO 3166-1/2, E.164 (국가/지역/전화번호) |
| DB 엔티티 생성 | `/generate-entity [한글 정의]` | DB 설계 문서 기반, Java/TypeScript/SQL |
| E2E 테스트 시나리오 생성 | `/test-scenario` | 블루프린트, DB, 라우트 기반 E2E 시나리오 |
| 통합 테스트 실행 | `/test-run` | 서버 실행 + Chrome MCP 자동 검증 |
| 코딩 표준 검사 | `/check-convention [대상]` | Java/TS/RN/Python/CSS/SCSS |
| DB 네이밍 검사 | `/check-naming [대상]` | 표준 용어 사전 기반 |
| 커밋 | `/commit` | 자동 메시지 생성 |
| PR 생성 | `/commit-push-pr` | 커밋+푸시+PR 일괄 |
| PR→리뷰→머지 자동화 | `/pr-merge` | 커밋→PR→리뷰→수정→머지 전체 사이클 |
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
| `naming-validator` | Haiku | Gate 1/3 | DB 네이밍 표준 검증 (Gate 1: 훅 자동 경고, Gate 3: 에이전트 검증) |
| `convention-validator` | Haiku | Gate 1/2 | 코딩 컨벤션 검증 (Gate 1: 스킬 자동 적용, Gate 2: 에이전트 검증) |
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
> ASTRA가 블루프린트를 먼저 작성하는 이유입니다.

#### 시간 추정의 한계

- AI 에이전트 성능은 **모델 버전, 코드베이스 크기, 도메인 복잡도**에 따라 큰 편차 발생
- METR 연구의 "19% 느려짐"은 **ad-hoc AI 사용** 기준이며, ASTRA처럼 **구조화된 워크플로우**에서는 30~60% 시간 단축 달성 가능
- AI 자율 작업 시간은 **~7개월마다 2배** 성장 중이므로, 본 문서의 시간 추정치는 **6~12개월마다 재검토** 필요
- 복잡한 비즈니스 로직, 아키텍처 의사결정, 도메인 특화 검증은 여전히 **인간 판단이 병목**

### 부록 E: Sprint 0 프로젝트 셋업

Sprint 0는 1주간 프로젝트의 기반을 설정합니다. 모든 기능 스프린트에 앞서 **1회만** 수행합니다.

#### Step 0.0: 개발환경 설정 (전역)

> **범위**: 개발자 머신 단위 (1회 설정, 모든 프로젝트에 적용)

```
# 1단계: 플러그인 마켓플레이스 추가
claude plugin marketplace add https://github.com/ASTRA-TECHNOLOGY-COMPANY-LIMITED/astra-methodology.git

# 2단계: astra-methodology 플러그인 설치
claude plugin install astra-methodology@astra

# 3단계: 전역 개발환경 자동 셋업 (전역 설정, MCP 서버, 플러그인 9개 자동 설치)
/astra-methodology:astra-setup
```

**자동 설치되는 항목:**
- 필수 플러그인 9개 (claude-code-setup, code-review, code-simplifier, commit-commands, feature-dev, frontend-design, hookify, security-guidance, context7)
- MCP 서버 3개 (chrome-devtools, postgres, context7)
- 전역 설정 (Agent Teams, bypassPermissions, Always Thinking)

#### Step 0.1: Vision & Backlog (Day 1-2)

DE와 킥오프 미팅을 통해 프로젝트 비전을 수립하고, Product Backlog를 초기 작성합니다.

```
# 기술 스택의 최신 문서 확인
"use context7 - Spring Boot 3의 WebClient와 RestTemplate 비교. 최신 권장 방식은?"

# 핵심 기능에 대한 사전 분석
/feature-dev "온라인 결제 시스템의 전체 아키텍처를 분석하고
docs/blueprints/overview.md로 작성해줘. 아직 실제 코드는 수정하지 마."
```

#### Step 0.2: Design System 구축 (Day 2-3) - DSA 주관

> 상세 내용은 [4. 디자인 시스템 작성](#4-디자인-시스템-작성)을 참고하세요.

디자인 토큰, 컴포넌트 스타일 가이드, 레이아웃 그리드 시스템을 구축합니다.

#### Step 0.3: Architecture & Standards (Day 3-4)

핵심 기능 설계 문서 생성([5. 블루프린트 작성](#5-블루프린트-작성) 참고), 중앙 DB 설계 문서 작성([6. 데이터베이스 설계](#6-데이터베이스-설계) 참고), 테스트 전략 문서(`docs/tests/test-strategy.md`) 작성을 수행합니다.

#### Step 0.4: Guard Rails 설정 (Day 4-5)

CLAUDE.md 작성 + hookify 규칙 설정으로 스프린트 전체에 적용될 품질 규칙을 사전 설정합니다.

```
# 프로젝트별 커스텀 규칙 생성
/hookify 모든 API 엔드포인트에는 인증 미들웨어를 반드시 포함할 것
/hookify console.log 대신 logger 라이브러리를 사용할 것
/hookify CSS에서 하드코딩된 컬러값 대신 CSS Variable을 사용할 것
```

**Sprint 0 완료 체크리스트:**
- [ ] Product Backlog 초기 작성 완료
- [ ] 디자인 시스템 구축 완료 (디자인 토큰, 컴포넌트 가이드)
- [ ] 핵심 기능별 설계 문서(MD) 생성 및 DE 승인
- [ ] 중앙 DB 설계 문서 작성 완료 (`docs/database/database-design.md`)
- [ ] 테스트 전략 문서 작성 완료 (`docs/tests/test-strategy.md`)
- [ ] CLAUDE.md 작성 완료 (디자인 원칙 포함)
- [ ] hookify 규칙 설정 완료

> Sprint 0 검증: `/project-checklist`

### 부록 F: 프로젝트 템플릿

#### F.1 디렉토리 구조

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
│   │   │   └── sprint-1/
│   │   │       └── auth-test-cases.md
│   │   └── test-reports/        # 스프린트별 테스트 결과 보고서
│   │       └── sprint-1-report.md
│   │
│   ├── sprints/                 # 스프린트 문서
│   │   ├── sprint-1/
│   │   │   ├── prompt-map.md
│   │   │   ├── progress.md
│   │   │   └── retrospective.md
│   │   └── sprint-2/
│   │       └── prompt-map.md
│   │
│   └── delivery/                # Release Sprint 산출물
│       ├── operation-manual.md
│       └── quality-report.md
│
└── src/                         # 소스 코드
```

#### F.2 스프린트 회고 템플릿

```markdown
# Sprint [N] Retrospective

## AI 분석 데이터
- code-review 반복 이슈: [자동 수집]
- security-guidance 차단 건수: [자동 수집]
- astra-methodology 위반 빈도: [자동 수집]

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

### 부록 G: 기대 효과

#### 정량적 효과

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

#### 정성적 효과

1. **스크럼의 본질에 집중**: 세레모니 시간이 줄어 "가치 전달"에 집중
2. **리뷰 문화 개선**: 스타일/표준 논쟁 제거 → 비즈니스 로직 토론의 장으로 전환
3. **회고의 실효성**: "개선하겠습니다" → "hookify 규칙으로 강제합니다"
4. **DE 참여도 향상**: 실시간 데모와 즉시 반영으로 프로젝트의 진정한 파트너 참여
5. **기술 부채 감소**: 작성 시점 품질 내장으로 "나중에 고치자" 원천 제거
6. **지식 이전 용이**: Living Document로 인수인계 비용 최소화

### 부록 H: 비용 효과

상세 내용은 [2.6 비용 효과](#26-비용-효과)를 참고하세요.
