---
name: astra-init
description: "ASTRA Sprint 0 프로젝트 초기 세팅. 프로젝트 디렉토리 구조, CLAUDE.md, 디자인 시스템 템플릿, 블루프린트 템플릿, 스프린트 템플릿을 생성합니다."
argument-hint: "[프로젝트명] [백엔드기술] [프론트엔드기술] [DB종류]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# ASTRA Sprint 0: 프로젝트 초기 세팅

당신은 ASTRA(AI-augmented Sprint Through Rapid Assembly) 방법론의 Sprint 0 설정 전문가입니다.
사용자의 프로젝트에 맞는 초기 세팅을 구성합니다.

## 실행 절차

### 1단계: 프로젝트 정보 수집

사용자 인자가 부족할 경우 AskUserQuestion으로 다음을 확인하세요:

1. **프로젝트명** (예: online-payment-system)
2. **프로젝트 설명** (한 줄 요약)
3. **백엔드 기술 스택** (예: Spring Boot 3, NestJS, FastAPI)
4. **프론트엔드 기술 스택** (예: Next.js 15, React, Vue 3)
5. **데이터베이스** (예: PostgreSQL 16, MySQL 8, MongoDB)
6. **주요 모듈** (예: 회원관리, 상품관리, 주문, 결제, 알림)
7. **팀 구성** (VA, PE, DE, DSA 인원 수)

`$ARGUMENTS`가 제공된 경우 파싱하여 가능한 정보를 추출하고, 부족한 정보만 추가 질문합니다.

### 2단계: 프로젝트 디렉토리 구조 생성

현재 작업 디렉토리(CWD)에 다음 구조를 생성합니다:

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

### 3단계: CLAUDE.md 생성

아래 템플릿을 프로젝트 정보에 맞게 커스터마이즈하여 생성합니다:

```markdown
# Project: {프로젝트명}

> {프로젝트 설명}

## 아키텍처
- 백엔드: {백엔드 기술 스택}
- 프론트엔드: {프론트엔드 기술 스택}
- 데이터베이스: {DB 종류}

## 주요 모듈
{모듈 목록을 bullet point로 나열}

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

## 설계 문서 규칙
- 기능별 설계 문서는 docs/blueprints/ 디렉토리에 작성
- DB 설계는 docs/database/database-design.md에 통합 관리
- 기능 구현 전 반드시 설계 문서 작성 및 승인 필요
```

**기술 스택별 커스터마이즈 규칙:**

- **Spring Boot**: `@RestControllerAdvice` 글로벌 예외 처리, `@Valid` 입력 검증, Lombok 사용
- **NestJS**: `ExceptionFilter` 글로벌 예외 처리, `class-validator` DTO 검증, Prisma ORM
- **FastAPI**: `HTTPException` 사용, Pydantic 모델 검증, SQLAlchemy ORM
- **Next.js**: App Router 기본, Server Components 우선, Server Actions 활용
- **React**: 함수형 컴포넌트만 사용, custom hooks 패턴
- **Vue 3**: Composition API 기본, `<script setup>` 사용

### 4단계: 디자인 시스템 템플릿 생성

`docs/design-system/` 아래에 다음 파일을 생성합니다.

**design-tokens.css**: 기본 디자인 토큰 세트 (컬러, 타이포그래피, 스페이싱, 그림자, 반응형 브레이크포인트)

**components.md**: 핵심 컴포넌트 스타일 가이드 템플릿 (버튼, 입력, 카드, 모달, 테이블, 네비게이션)

**layout-grid.md**: 레이아웃 그리드 시스템 정의 (컬럼 시스템, 컨테이너, 브레이크포인트별 동작)

### 5단계: 블루프린트 템플릿 생성

**docs/blueprints/overview.md**: 프로젝트 개요 문서 (비전, 목표, 모듈 구조, 기술 스택 결정 근거)

### 6단계: 데이터베이스 문서 템플릿 생성

**docs/database/database-design.md**: 중앙 DB 설계 문서 템플릿 (전체 ERD, 공통 규칙, 모듈별 테이블, FK 관계 요약)

**docs/database/naming-rules.md**: DB 네이밍 규칙 및 표준 용어 매핑 문서 (테이블 접두사, 컬럼 네이밍, 표준 용어 사전 연동)

### 7단계: 테스트 문서 템플릿 생성

**docs/tests/test-strategy.md**: 테스트 전략 문서 (테스트 레벨 정의, 커버리지 목표, 테스트 환경, 네이밍 규칙, 자동화 범위)

### 8단계: 스프린트 템플릿 생성

**docs/prompts/sprint-1.md**: 첫 번째 스프린트 프롬프트 맵 템플릿

### 9단계: 프로젝트 설정 파일 생성

**.claude/settings.json**: 프로젝트별 Claude Code 설정

### 10단계: 결과 요약 출력

모든 파일 생성 후 다음을 출력합니다:

```
## ASTRA Sprint 0 초기 세팅 완료

### 생성된 파일 목록
- CLAUDE.md (프로젝트 AI 규칙)
- .claude/settings.json (프로젝트 설정)
- docs/design-system/ (디자인 시스템 템플릿)
- docs/blueprints/ (설계 문서 템플릿)
- docs/database/ (DB 설계 문서, 네이밍 규칙, 마이그레이션)
- docs/tests/ (테스트 전략, 테스트 케이스, 테스트 리포트)
- docs/prompts/ (스프린트 프롬프트 맵)
- docs/retrospectives/ (회고 기록용)
- docs/delivery/ (릴리스 산출물용)

### 다음 단계 (Sprint 0 진행)
1. [ ] CLAUDE.md 검토 및 프로젝트에 맞게 수정
2. [ ] DSA와 docs/design-system/ 파일 정의
3. [ ] /astra-global-setup 으로 전역 개발환경 확인
4. [ ] /feature-dev 로 핵심 기능 설계 문서 생성
5. [ ] docs/database/database-design.md 작성
6. [ ] docs/database/naming-rules.md 검토
7. [ ] docs/tests/test-strategy.md 작성
8. [ ] hookify 규칙 설정
9. [ ] /astra-checklist 로 Sprint 0 완료 확인
```

## 주의사항

- 이미 존재하는 파일은 **덮어쓰지 않습니다**. 기존 파일이 있으면 사용자에게 확인합니다.
- .gitkeep 파일은 빈 디렉토리 유지용으로만 생성합니다.
- 기술 스택에 따라 CLAUDE.md의 규칙을 자동으로 조정합니다.
- 모든 텍스트는 한국어로 작성합니다 (코드 내 주석 제외).
