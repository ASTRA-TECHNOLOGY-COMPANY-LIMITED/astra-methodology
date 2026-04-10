---
name: auth-module
description: "인증 모듈을 자동으로 구축합니다. 레퍼런스 설계 문서를 기반으로 블루프린트 작성, 스프린트 생성, 구현, 테스트 시나리오 작성, 테스트 실행 및 디버깅까지 전체 파이프라인을 자동 실행합니다. 회원가입, 로그인, 로그아웃, 토큰 관리, 약관 관리, 사용자 관리, 프로필 관리 기능을 포함합니다."
argument-hint: "[target-project-path]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Agent
---

# ASTRA 인증 모듈 자동 구축

레퍼런스 설계 문서(`$CLAUDE_PLUGIN_ROOT/docs/auth/system-design.md`)를 기반으로 대상 프로젝트에 인증 모듈 전체를 자동 구축합니다.

**자동 구축 범위**:
- 회원가입 (이메일 + 소셜 로그인)
- 로그인 / 로그아웃 (단일 디바이스 + 전체 디바이스)
- 토큰 관리 (JWT Access/Refresh Token, Token Rotation)
- 약관 관리 (CRUD + 버전 관리 + 동의/철회)
- 사용자 관리 (프로필 조회/수정, 회원 탈퇴, 관리자 기능)

## 실행 절차

### Step 0: 사전 준비 및 컨텍스트 수집

#### A. 레퍼런스 설계 문서 로드

`$CLAUDE_PLUGIN_ROOT/docs/auth/system-design.md` 파일을 읽어 레퍼런스 설계 정보를 로드한다:

1. 아키텍처 개요 (섹션 1)
2. 기술 스택 (섹션 2)
3. 데이터베이스 스키마 — TB_COMM_USER, TB_COMM_TRMS, TH_COMM_USER_AGRE, TB_COMM_RFRSH_TKN (섹션 3)
4. API 설계 — 인증/사용자/약관 엔드포인트 (섹션 4)
5. 화면 구성 — 로그인, 회원가입, 약관, 프로필, 관리 페이지 (섹션 5)
6. 인증 흐름 — Firebase + JWT 시퀀스 (섹션 6)
7. 보안 설계 — 토큰 보안, CSRF, XSS, Rate Limiting (섹션 7)
8. 디렉토리 구조 (섹션 8)
9. 구현 순서 — Phase 1~5 (섹션 9)

> **중요**: 이 레퍼런스는 **AMA 프로젝트(Next.js 14 + Firebase + PostgreSQL)**를 기준으로 작성되었다. 설계 문서 내 "xframe"은 AMA 프로젝트의 기반 인증 아키텍처를 가리킨다. 대상 프로젝트의 기술 스택에 맞게 **적응(adapt)**해야 한다.

#### B. 대상 프로젝트 분석

`$ARGUMENTS`에서 대상 프로젝트 경로를 파싱한다. 인자가 없으면 현재 작업 디렉토리를 사용한다.

대상 프로젝트에서 다음을 분석한다:

1. `CLAUDE.md` 읽기 — 기술 스택, 프로젝트 구조, 컨벤션 확인
2. `package.json` 또는 `build.gradle` 또는 `pom.xml` 또는 `pyproject.toml` 읽기 — 프레임워크/의존성 파악
3. `docs/blueprints/` 스캔 — 기존 블루프린트 번호 확인 (다음 번호 결정)
4. `docs/database/database-design.md` 읽기 — 기존 DB 스키마 확인
5. `docs/sprints/` 스캔 — `sprint-{N}-{name}/` 패턴 디렉토리에서 현재 스프린트 번호 확인
6. `src/` 스캔 — 기존 코드 구조, 라우팅 패턴, 인증 관련 기존 코드 확인
7. `src/styles/design-tokens.css` + `docs/design-system/` 스캔 — 디자인 토큰, 컴포넌트 패턴 확인

#### C. 기술 스택 적응 매트릭스

대상 프로젝트의 기술 스택에 따라 레퍼런스 설계를 적응한다:

| 레퍼런스 (AMA) | 대상 프로젝트 | 적응 방법 |
|---------------|------------|----------|
| Next.js 14 API Routes | Spring Boot | `@RestController` + `@RequestMapping` |
| Next.js 14 API Routes | NestJS | `@Controller` + `@Get`/`@Post` |
| Next.js 14 API Routes | FastAPI | `@router.get`/`@router.post` |
| Next.js 14 API Routes | Next.js | 그대로 사용 |
| Drizzle ORM | JPA/Hibernate | `@Entity` + `@Table` + `@Column` |
| Drizzle ORM | TypeORM | `@Entity` + `@Column` |
| Drizzle ORM | Prisma | `schema.prisma` 모델 |
| Drizzle ORM | SQLAlchemy | `Base` + `Column` |
| Firebase Auth | Firebase Auth | 그대로 사용 |
| Firebase Auth | 없음/자체 | bcrypt + 이메일 검증 자체 구현 |
| React (TSX) | React (TSX) | 그대로 사용 |
| React (TSX) | Vue 3 | Composition API + `<script setup>` |
| React (TSX) | Angular | Component + Service + Guard |
| React (TSX) | React Native | RN 컴포넌트 + AsyncStorage |
| jose (JWT) | jsonwebtoken | `sign`/`verify` |
| jose (JWT) | jjwt (Java) | `Jwts.builder()`/`Jwts.parser()` |
| jose (JWT) | PyJWT | `jwt.encode`/`jwt.decode` |

적응이 필요한 경우 `AskUserQuestion`으로 사용자에게 확인한다:

```
## 인증 모듈 기술 스택 확인

레퍼런스: Next.js 14 + Firebase + PostgreSQL + Drizzle ORM
대상 프로젝트: {detected-tech-stack}

다음 사항을 확인해 주세요:
1. 인증 제공자: Firebase Auth / 자체 구현 / 기타 ({detected})
2. ORM: {detected}
3. JWT 라이브러리: {detected or recommended}
4. 프론트엔드 프레임워크: {detected}

추가 요구사항이 있으면 알려주세요 (예: OAuth 제공자 추가/제거, 2FA 등).
```

#### D. 기능 모듈 정의

레퍼런스 설계 문서에서 추출한 인증 모듈 기능 목록:

| # | 모듈 | 기능 | API 엔드포인트 | 화면 |
|---|------|------|--------------|------|
| 1 | 인증 | 회원가입 | `POST /auth/signup` | `/auth/signup` |
| 2 | 인증 | 로그인 | `POST /auth/login` | `/auth/login` |
| 3 | 인증 | 토큰 갱신 | `POST /auth/refresh` | - |
| 4 | 인증 | 로그아웃 | `POST /auth/logout` | - |
| 5 | 인증 | 전체 로그아웃 | `POST /auth/logout-all` | - |
| 6 | 인증 | 비밀번호 찾기 | Firebase | `/auth/forgot-password` |
| 7 | 사용자 | 내 프로필 조회/수정 | `GET/PATCH /users/me` | `/admin/profile` |
| 8 | 사용자 | 비밀번호 변경 | Firebase | `/admin/profile/change-password` |
| 9 | 사용자 | 회원 탈퇴 | `DELETE /users/me` | - |
| 10 | 사용자 | 사용자 목록 (ADMIN) | `GET /users` | `/admin/settings/users` |
| 11 | 사용자 | 사용자 관리 (ADMIN) | `PATCH/POST /users/[id]/*` | `/admin/settings/users/[id]` |
| 12 | 약관 | 활성 약관 목록 | `GET /terms/active` | - |
| 13 | 약관 | 약관 동의/철회 | `POST /terms/agree`, `DELETE /terms/[id]/revoke` | `/auth/terms-agreement` |
| 14 | 약관 | 미동의 약관 | `GET /terms/pending` | - |
| 15 | 약관 | 약관 관리 (ADMIN) | `GET/POST/PATCH /terms` | `/admin/settings/terms` |

---

### Step 1: 블루프린트 자동 생성

레퍼런스 설계 문서를 기반으로 인증 모듈 블루프린트를 생성한다.

#### A. 블루프린트 번호 결정

`docs/blueprints/` 디렉토리를 스캔하여 기존 블루프린트 번호를 확인하고 다음 번호를 결정한다.

```
NNN = (기존 최대 번호) + 1
```

#### A-1. dev 브랜치 전환 및 최신화

블루프린트 파일을 생성하기 전에, `dev` 브랜치로 전환하고 최신 상태로 동기화한다. 작업 브랜치는 생성하지 않으며, `dev`에서 직접 작업한다. 작업 브랜치 생성은 `/pr-merge` 실행 시 자동으로 처리된다.

1. **현재 브랜치 확인**: `git branch --show-current`
2. **이미 `dev` 브랜치인 경우 스킵**: 현재 브랜치가 `dev`이면 아래 3~5단계를 건너뛰고 pull만 실행한다 (`git pull origin dev`)
3. **미커밋 변경사항 보존**: `git status --porcelain`으로 확인하여 변경사항이 있으면 `git stash`로 임시 저장한다
4. **dev 브랜치 전환 및 최신화**: `git fetch origin dev && git checkout dev && git pull origin dev`
5. **stash 복원**: step 3에서 stash 했으면 `git stash pop`으로 복원한다. 충돌 발생 시 충돌 파일 목록을 사용자에게 보고하고 수동 해결을 요청한다.

> **참고**: `dev` 브랜치가 존재하지 않으면 `main` 또는 `master` 브랜치에서 작업한다. 어떤 기본 브랜치도 없으면 현재 브랜치에서 작업한다.

#### B. 인증 모듈 블루프린트 생성

`docs/blueprints/{NNN}-auth/blueprint.md` 파일을 생성한다.

레퍼런스 설계 문서의 내용을 대상 프로젝트 기술 스택에 맞게 적응하여 다음 섹션을 포함한다:

```markdown
# 인증 모듈 설계 문서

## 1. 개요
- 설계 원칙 (레퍼런스 섹션 1.1 적응)
- 아키텍처 다이어그램 (대상 프로젝트에 맞게 수정)
- 타 모듈과의 관계

## 2. 기술 스택
- 의존성 목록 (레퍼런스 섹션 2.1 적응)
- 환경 변수 (레퍼런스 섹션 2.2 적응 — 실제 값은 placeholder로)

## 3. 데이터베이스 스키마
- ER 다이어그램 (레퍼런스 섹션 3.1)
- 테이블 정의 (레퍼런스 섹션 3.2~3.5 적응)
- DDL (대상 DB에 맞게 변환)
- ORM 스키마 정의 (대상 ORM에 맞게 변환)

## 4. API 설계
- 엔드포인트 목록 (레퍼런스 섹션 4.1)
- 상세 API 스펙 (레퍼런스 섹션 4.2 적응)
  - Request/Response 스키마
  - 비즈니스 로직 (트랜잭션 포함)
  - 에러 코드
- JWT 토큰 구조

## 5. 화면 구성
- 화면 목록 (레퍼런스 섹션 5.1)
- 각 화면 와이어프레임 + 기능 상세 (레퍼런스 섹션 5.2~5.8 적응)
- 상태 관리

## 6. 인증 흐름
- 전체 인증 시퀀스 (레퍼런스 섹션 6.1)
- 토큰 자동 갱신 (레퍼런스 섹션 6.2)
- 미들웨어 인증 로직 (레퍼런스 섹션 6.3)

## 7. 보안 설계
- 토큰 보안 (레퍼런스 섹션 7.1)
- CSRF/XSS 방지 (레퍼런스 섹션 7.2~7.3)
- 비밀번호 정책 (레퍼런스 섹션 7.4)
- Rate Limiting (레퍼런스 섹션 7.5)

## 8. 디렉토리 구조
- 신규 추가 파일 목록 (대상 프로젝트 구조에 맞게)

## 9. 구현 순서
- Phase 1~5 (레퍼런스 섹션 9)
```

> **참고**: 레퍼런스 설계 문서의 모든 섹션을 빠짐없이 반영한다. 기술 스택만 대상 프로젝트에 맞게 변환하고, 비즈니스 로직과 보안 설계는 원본을 최대한 유지한다.

#### C. DB 설계 문서 반영

`docs/database/database-design.md`에 인증 모듈 테이블을 추가한다:

1. 레퍼런스의 4개 테이블(TB_COMM_USER, TB_COMM_TRMS, TH_COMM_USER_AGRE, TB_COMM_RFRSH_TKN)을 추가
2. ER 다이어그램 업데이트
3. FK 관계 요약 업데이트
4. 공공 데이터 표준 네이밍 규칙 준수 확인

#### D. 블루프린트 생성 완료 보고

```
## Step 1 완료: 블루프린트 생성

### 생성된 파일
- docs/blueprints/{NNN}-auth/blueprint.md (인증 모듈 설계 문서)
- docs/database/database-design.md (DB 테이블 4개 추가)

### 포함된 기능
- 인증 API 5개 (signup, login, refresh, logout, logout-all)
- 사용자 API 6개 (me, users, role, suspend, activate)
- 약관 API 8개 (active, detail, pending, agreements, agree, revoke, list, create/update)
- 화면 10개 (login, signup, forgot-password, terms-agreement, profile, change-password, terms-mgmt, terms-editor, users-mgmt, user-detail)

Step 2로 진행합니다...
```

---

### Step 2: 스프린트 계획 자동 생성

블루프린트의 구현 순서(Phase 1~5)를 기반으로 스프린트 프롬프트 맵을 생성한다.

#### A. 스프린트 번호 결정

`docs/sprints/` 디렉토리에서 `sprint-{N}-{name}/` 패턴 디렉토리를 스캔하여 다음 스프린트 번호를 결정한다.

#### B. 스프린트 프롬프트 맵 생성

`docs/sprints/sprint-{N}-auth/prompt-map.md`를 생성한다.

레퍼런스의 Phase를 스프린트 Feature 단위로 분할한다:

```markdown
# Sprint {N} Prompt Map

## Sprint Goal
인증 모듈 전체 구축 — 회원가입, 로그인, 로그아웃, 토큰 관리, 약관 관리, 사용자 관리

## Feature 1: 인증 기반 인프라 (Phase 1)

### 1.1 Design Prompt
(Already completed — see docs/blueprints/{NNN}-auth/blueprint.md 섹션 2~3)

### 1.2 DB Design Reflection Prompt
/feature-dev "docs/blueprints/{NNN}-auth/blueprint.md 섹션 3의 DDL을 기반으로
docs/database/database-design.md에 인증 모듈 테이블 4개를 추가/업데이트한다.
ER 다이어그램과 FK 관계도 반영한다. 코드 수정 없음."

### 1.3 Test Case Prompt
/feature-dev "docs/blueprints/{NNN}-auth/blueprint.md를 기반으로
docs/tests/test-cases/sprint-{N}/auth-infra-test-cases.md에
DB 스키마 검증, JWT 유틸, Firebase 초기화 테스트 케이스를 작성한다. 코드 수정 없음."

### 1.4 Implementation Prompt
/feature-dev "docs/blueprints/{NNN}-auth/blueprint.md Phase 1을 참조하여
인증 기반 인프라를 구현한다:
- 의존성 설치, 환경 변수 설정
- ORM 설정 및 DB 스키마 정의
- DB 마이그레이션
- Firebase Admin/Client 초기화
- JWT 유틸리티 (생성/검증)
- Zod 검증 스키마
테스트 실행 후 결과를 docs/tests/test-reports/에 기록한다."

## Feature 2: 인증 API (Phase 2)

### 2.1 Design Prompt
(Already completed — see docs/blueprints/{NNN}-auth/blueprint.md 섹션 4.2.1~4.2.5, 섹션 6)

### 2.2 Test Case Prompt
/feature-dev "docs/blueprints/{NNN}-auth/blueprint.md 섹션 4.2.1~4.2.5를 기반으로
docs/tests/test-cases/sprint-{N}/auth-api-test-cases.md에
회원가입, 로그인, 토큰갱신, 로그아웃 API 테스트 케이스를 작성한다.
Happy Path, Error Path, Edge Case 포함. 코드 수정 없음."

### 2.3 Implementation Prompt
/feature-dev "docs/blueprints/{NNN}-auth/blueprint.md Phase 2를 참조하여 구현:
- 인증 미들웨어 (JWT 검증, 역할 기반 접근 제어)
- 회원가입 API (Firebase ID Token 검증, 약관 동의, 워크스페이스 생성)
- 로그인 API (사용자 조회, 미동의 약관 확인, 토큰 발급)
- 토큰 갱신 API (Token Rotation)
- 로그아웃 / 전체 로그아웃 API
- Server Action (쿠키 관리)
- AuthContext (클라이언트 인증 상태 관리)
- API 클라이언트 인터셉터 (401 자동 갱신)
- 미들웨어 강화 (보호 경로 리다이렉트)
테스트 실행 후 결과를 docs/tests/test-reports/에 기록한다."

## Feature 3: 사용자/약관 API (Phase 3)

### 3.1 Design Prompt
(Already completed — see docs/blueprints/{NNN}-auth/blueprint.md 섹션 4.2.6~4.2.13)

### 3.2 Test Case Prompt
/feature-dev "docs/blueprints/{NNN}-auth/blueprint.md 섹션 4.2.6~4.2.13을 기반으로
docs/tests/test-cases/sprint-{N}/user-terms-api-test-cases.md에
프로필 CRUD, 회원탈퇴, 약관 CRUD, 약관 동의/철회, 관리자 API 테스트 케이스를 작성한다. 코드 수정 없음."

### 3.3 Implementation Prompt
/feature-dev "docs/blueprints/{NNN}-auth/blueprint.md Phase 3을 참조하여 구현:
- 내 프로필 API (조회/수정/탈퇴)
- 사용자 관리 API (목록/상세/역할변경/정지/활성화) — ADMIN
- 활성 약관 목록 / 약관 상세 API
- 약관 동의 / 동의 철회 API
- 미동의 약관 / 내 약관 동의 현황 API
- 약관 관리 CRUD API — ADMIN
테스트 실행 후 결과를 docs/tests/test-reports/에 기록한다."

## Feature 4: 인증 화면 구현 (Phase 4)

### 4.1 Design Prompt
(Already completed — see docs/blueprints/{NNN}-auth/blueprint.md 섹션 5)

### 4.2 Test Case Prompt
/feature-dev "docs/blueprints/{NNN}-auth/blueprint.md 섹션 5를 기반으로
docs/tests/test-cases/sprint-{N}/auth-ui-test-cases.md에
로그인, 회원가입, 약관동의, 프로필, 관리자 화면의 E2E 테스트 시나리오를 작성한다.
사용자 여정 기반으로 Happy/Error/Edge 시나리오 포함. 코드 수정 없음."

### 4.3 Implementation Prompt
/feature-dev "docs/blueprints/{NNN}-auth/blueprint.md Phase 4를 참조하여 구현:
- 로그인 페이지 (이메일 + 소셜 로그인, 에러 처리)
- 회원가입 페이지 (폼 검증, 약관 동의, 소셜 가입)
- 비밀번호 찾기 페이지
- 약관 동의 페이지 (미동의 필수 약관 처리)
- 내 프로필 페이지 (정보 수정, 약관 현황, 기기 관리, 탈퇴)
- 비밀번호 변경 페이지
- 약관 관리 페이지 — ADMIN (DataTable + 필터 + 에디터)
- 사용자 관리 페이지 — ADMIN (검색 + 역할/상태 관리)
테스트 실행 후 결과를 docs/tests/test-reports/에 기록한다."

## Feature 5: 통합/보안 강화 (Phase 5)

### 5.1 Test Case Prompt
/feature-dev "docs/blueprints/{NNN}-auth/blueprint.md 섹션 7을 기반으로
docs/tests/test-cases/sprint-{N}/auth-security-test-cases.md에
보안 테스트 케이스를 작성한다: Rate Limiting, CSRF, XSS, 토큰 보안, 계정 잠금. 코드 수정 없음."

### 5.2 Implementation Prompt
/feature-dev "docs/blueprints/{NNN}-auth/blueprint.md Phase 5를 참조하여 구현:
- 다국어 메시지 (인증 관련 ko/en)
- Rate Limiting (엔드포인트별 제한)
- CSP 헤더 설정
- 에러 처리 통합 (공통 에러 응답 형식)
- 초기 데이터 Seed (기본 약관 3건)
테스트 실행 후 결과를 docs/tests/test-reports/에 기록한다."
```

#### C. 스프린트 프로그레스 트래커 생성

`docs/sprints/sprint-{N}-auth/progress.md`를 생성한다:

```markdown
# Sprint {N} Progress Tracker

## Sprint Information
- **Sprint Number**: {N}
- **Sprint Goal**: 인증 모듈 전체 구축
- **Start Date**: {TODAY}
- **End Date**: {TODAY + 7 days}
- **Status**: In Progress

<!-- PROGRESS_TABLE_START -->
## Feature Progress

| Feature | Blueprint | DB Design | Test Cases | Implementation | Test Report | Status |
|---------|-----------|-----------|------------|----------------|-------------|--------|
| 인증 기반 인프라 | Done | - | - | - | - | Not Started |
| 인증 API | Done | Done | - | - | - | Not Started |
| 사용자/약관 API | Done | Done | - | - | - | Not Started |
| 인증 화면 구현 | Done | N/A | - | - | - | Not Started |
| 통합/보안 강화 | Done | N/A | - | - | - | Not Started |

**Legend**: `-` Not Started, `WIP` In Progress, `Done` Completed, `N/A` Not Applicable
<!-- PROGRESS_TABLE_END -->

<!-- SUMMARY_START -->
## Summary
- **Total Features**: 5
- **Completed**: 0
- **In Progress**: 0
- **Overall Progress**: 0%
- **Last Updated**: {TIMESTAMP}
<!-- SUMMARY_END -->

<!-- ACTIVITY_LOG_START -->
## Activity Log

| Timestamp | Event | File | Details |
|-----------|-------|------|---------|
| {TIMESTAMP} | blueprint | docs/blueprints/{NNN}-auth/blueprint.md | 인증 모듈 블루프린트 생성 |
| {TIMESTAMP} | db-design | docs/database/database-design.md | 인증 테이블 4개 추가 |
<!-- ACTIVITY_LOG_END -->
```

#### D. 스프린트 계획 완료 보고

```
## Step 2 완료: 스프린트 계획 생성

### 생성된 파일
- docs/sprints/sprint-{N}-auth/prompt-map.md (프롬프트 맵)
- docs/sprints/sprint-{N}-auth/progress.md (프로그레스 트래커)

### 스프린트 구조
- Feature 1: 인증 기반 인프라 (의존성, DB, Firebase, JWT)
- Feature 2: 인증 API (signup, login, refresh, logout)
- Feature 3: 사용자/약관 API (profile, users, terms CRUD)
- Feature 4: 인증 화면 구현 (10개 페이지)
- Feature 5: 통합/보안 강화 (Rate Limiting, CSP, i18n)

Step 3으로 진행합니다...
```

---

### Step 3: 구현 자동 실행

스프린트 프롬프트 맵의 각 Feature를 순서대로 구현한다.

#### A. Feature별 구현 순서

각 Feature에 대해 다음 순서로 진행한다:

1. **테스트 케이스 작성** — 프롬프트 맵의 Test Case Prompt 실행
2. **구현** — 프롬프트 맵의 Implementation Prompt 실행
3. **프로그레스 업데이트** — progress.md 테이블 갱신

#### B. Feature 1: 인증 기반 인프라 구현

레퍼런스 Phase 1에 해당하는 작업을 실행한다:

1. **의존성 설치** — 프로젝트 패키지 매니저로 필요 패키지 설치
2. **환경 변수 템플릿** — `.env.example`에 인증 관련 환경 변수 추가 (실제 값은 placeholder)
3. **DB 클라이언트 설정** — ORM 초기화 및 연결 설정
4. **DB 스키마 정의** — 레퍼런스의 Drizzle 스키마를 대상 ORM으로 변환하여 작성
5. **DB 마이그레이션** — 마이그레이션 파일 생성 및 실행 (가능한 경우)
6. **Firebase 초기화** — Admin SDK + Client SDK 설정
7. **JWT 유틸리티** — 토큰 생성/검증 함수 (레퍼런스 섹션 4.4 페이로드 구조)
8. **검증 스키마** — Zod 또는 대상 프레임워크의 검증 라이브러리로 스키마 정의

구현 후 progress.md를 업데이트한다:
- 인증 기반 인프라: Implementation → `Done`

#### C. Feature 2: 인증 API 구현

레퍼런스 Phase 2에 해당하는 작업을 실행한다:

1. **인증 미들웨어** — JWT 검증 + 역할 기반 접근 제어
2. **회원가입 API** — 레퍼런스 섹션 4.2.1 비즈니스 로직 구현
   - Firebase ID Token 검증
   - UID 중복 검사
   - 필수 약관 동의 검증
   - 트랜잭션: 사용자 생성 + 약관 동의 이력 + (워크스페이스 생성)
   - Access/Refresh Token 발급
3. **로그인 API** — 레퍼런스 섹션 4.2.2 비즈니스 로직 구현
   - 미가입 사용자 처리 (`requires_signup`)
   - 미동의 약관 확인 (`requires_terms_agreement`)
   - Firebase 프로필 동기화
4. **토큰 갱신 API** — Token Rotation 구현 (레퍼런스 섹션 4.2.3)
5. **로그아웃 API** — 단일/전체 디바이스 (레퍼런스 섹션 4.2.4~4.2.5)
6. **Server Action** — HttpOnly 쿠키 관리 (대상 프레임워크에 맞게)
7. **AuthContext** — 클라이언트 인증 상태 관리 (레퍼런스 섹션 8.2)
8. **API 클라이언트 인터셉터** — 401 자동 갱신 (레퍼런스 섹션 8.3)
9. **미들웨어 강화** — 보호 경로 + 토큰 자동 갱신 (레퍼런스 섹션 6.3)

#### D. Feature 3: 사용자/약관 API 구현

레퍼런스 Phase 3에 해당하는 작업을 실행한다:

1. **내 프로필 API** — GET/PATCH/DELETE /users/me (레퍼런스 섹션 4.2.6~4.2.8)
2. **사용자 관리 API** — 목록/상세/역할변경/정지/활성화 (ADMIN, 레퍼런스 섹션 4.2.13)
3. **활성 약관 API** — GET /terms/active (레퍼런스 섹션 4.2.9)
4. **약관 동의 API** — POST /terms/agree (레퍼런스 섹션 4.2.10)
5. **약관 철회 API** — DELETE /terms/[id]/revoke
6. **미동의 약관 API** — GET /terms/pending
7. **약관 관리 API** — GET/POST/PATCH (ADMIN, 레퍼런스 섹션 4.2.11~4.2.12)

#### E. Feature 4: 인증 화면 구현

레퍼런스 Phase 4에 해당하는 화면을 구현한다:

1. **로그인 페이지** — 이메일 + 소셜 로그인, 리다이렉트 (레퍼런스 섹션 5.2)
2. **회원가입 페이지** — 폼 검증, 약관 동의, 소셜 가입 (레퍼런스 섹션 5.3)
3. **비밀번호 찾기** — Firebase 연동 (레퍼런스 섹션 5.4)
4. **약관 동의 페이지** — 미동의 필수 약관 (레퍼런스 섹션 5.5)
5. **내 프로필** — 정보 수정, 약관 현황, 기기 관리, 탈퇴 (레퍼런스 섹션 5.6)
6. **비밀번호 변경** — 이메일 가입자 전용
7. **약관 관리** — DataTable + 필터 + 에디터 (ADMIN, 레퍼런스 섹션 5.7)
8. **사용자 관리** — 검색 + 역할/상태 관리 (ADMIN, 레퍼런스 섹션 5.8)

각 화면 구현 시 `src/styles/design-tokens.css`의 디자인 토큰과 `docs/design-system/`의 컴포넌트 패턴을 따른다.

#### F. Feature 5: 통합/보안 강화

레퍼런스 Phase 5에 해당하는 작업을 실행한다:

1. **다국어 메시지** — 인증 관련 메시지 ko/en 추가
2. **Rate Limiting** — 엔드포인트별 제한 구현 (레퍼런스 섹션 7.5)
3. **CSP 헤더** — Content Security Policy 설정
4. **에러 처리 통합** — 공통 에러 응답 형식 (레퍼런스 섹션 4.3)
5. **초기 데이터 Seed** — 기본 약관 3건 (레퍼런스 부록)

#### G. 구현 완료 보고

```
## Step 3 완료: 구현

### 구현된 Feature
| Feature | 파일 수 | 상태 |
|---------|---------|------|
| 인증 기반 인프라 | {N}개 | Done |
| 인증 API | {N}개 | Done |
| 사용자/약관 API | {N}개 | Done |
| 인증 화면 구현 | {N}개 | Done |
| 통합/보안 강화 | {N}개 | Done |

Step 4로 진행합니다...
```

---

### Step 4: 테스트 시나리오 자동 생성

구현된 인증 모듈에 대해 종합적인 E2E 테스트 시나리오를 생성한다.

#### A. 테스트 시나리오 생성

`Agent` 도구를 사용하여 `/test-scenario auth` 스킬과 동일한 방식으로 테스트 시나리오를 생성한다.

생성할 시나리오 파일:

1. `docs/tests/test-cases/sprint-{N}/auth-e2e-scenarios.md` — 인증 흐름 E2E
2. `docs/tests/test-cases/sprint-{N}/user-mgmt-e2e-scenarios.md` — 사용자 관리 E2E
3. `docs/tests/test-cases/sprint-{N}/terms-mgmt-e2e-scenarios.md` — 약관 관리 E2E

#### B. 시나리오 그룹 구성

레퍼런스 설계 문서의 기능 목록에 기반한 시나리오 그룹:

**인증 흐름 시나리오**:
| 그룹 | 시나리오 유형 |
|------|------------|
| 이메일 회원가입 | Happy: 정상 가입 / Error: 중복 UID, 필수 약관 미동의, 잘못된 토큰 / Edge: 동시 가입 |
| 소셜 회원가입 | Happy: Google/Apple/Kakao 가입 / Error: Firebase 오류 / Edge: 기존 이메일 |
| 이메일 로그인 | Happy: 정상 로그인 / Error: 미가입, 정지계정, 잘못된 비밀번호 / Edge: 미동의 약관 |
| 소셜 로그인 | Happy: 각 소셜 로그인 / Error: 팝업 취소, 네트워크 오류 |
| 토큰 갱신 | Happy: 자동 갱신 / Error: 폐기된 토큰, 만료된 토큰 / Edge: 동시 갱신 |
| 로그아웃 | Happy: 단일/전체 로그아웃 / Edge: 이미 로그아웃된 세션 |
| 비밀번호 찾기 | Happy: 이메일 발송 / Error: 미등록 이메일 |

**사용자 관리 시나리오**:
| 그룹 | 시나리오 유형 |
|------|------------|
| 프로필 관리 | Happy: 조회/수정 / Error: 인증 없음 / Edge: 빈 필드 |
| 비밀번호 변경 | Happy: 정상 변경 / Error: 기존 비밀번호 불일치 |
| 회원 탈퇴 | Happy: 정상 탈퇴 / Error: 워크스페이스 소유자 / Edge: 탈퇴 후 재가입 |
| 사용자 목록 (ADMIN) | Happy: 목록/검색/필터 / Error: 권한 없음 |
| 사용자 관리 (ADMIN) | Happy: 역할변경/정지/활성화 / Error: 자기 자신 정지 |

**약관 관리 시나리오**:
| 그룹 | 시나리오 유형 |
|------|------------|
| 약관 동의 | Happy: 전체 동의, 선택 동의 / Error: 미존재 약관 ID |
| 약관 철회 | Happy: 선택 약관 철회 / Error: 필수 약관 철회 시도 |
| 약관 생성 (ADMIN) | Happy: 신규 약관 / Error: 중복 유형+버전 |
| 약관 수정 (ADMIN) | Happy: 내용 수정, 비활성화 / Edge: 버전 업 시 이전 버전 자동 비활성화 |

#### C. 시나리오 생성 완료 보고

```
## Step 4 완료: 테스트 시나리오 생성

### 생성된 파일
- docs/tests/test-cases/sprint-{N}/auth-e2e-scenarios.md ({N}개 시나리오)
- docs/tests/test-cases/sprint-{N}/user-mgmt-e2e-scenarios.md ({N}개 시나리오)
- docs/tests/test-cases/sprint-{N}/terms-mgmt-e2e-scenarios.md ({N}개 시나리오)

### 시나리오 통계
| Type | Auth | User | Terms | Total |
|------|------|------|-------|-------|
| Happy Path | {n} | {n} | {n} | {n} |
| Error Path | {n} | {n} | {n} | {n} |
| Edge Case | {n} | {n} | {n} | {n} |
| **Total** | **{n}** | **{n}** | **{n}** | **{n}** |

Step 5로 진행합니다...
```

---

### Step 5: 테스트 실행 및 디버깅

#### A. 유닛/통합 테스트 실행

프로젝트의 테스트 프레임워크를 자동 감지하여 테스트를 실행한다:

| 프레임워크 | 명령어 |
|-----------|-------|
| Jest | `npx jest --coverage --passWithNoTests` |
| Vitest | `npx vitest run --coverage` |
| JUnit | `./gradlew test` 또는 `mvn test` |
| pytest | `python -m pytest --cov` |

```bash
# 테스트 실행 및 결과 수집
{TEST_COMMAND} 2>&1
```

#### B. 서버 기동 및 E2E 테스트

1. **서버 기동** — 프로젝트의 개발 서버를 백그라운드로 실행
2. **서버 준비 대기** — 헬스체크 엔드포인트 또는 포트 확인
3. **API 테스트** — `curl` 또는 `fetch`로 인증 API 엔드포인트 테스트:
   - `GET /api/v1/terms/active` → 200 (활성 약관 목록)
   - `POST /api/v1/auth/signup` → 테스트 계정 생성 (Firebase 에뮬레이터 사용 권장)
   - `POST /api/v1/auth/login` → 토큰 발급 확인
   - `GET /api/v1/users/me` → 프로필 조회
   - `POST /api/v1/auth/refresh` → 토큰 갱신
   - `POST /api/v1/auth/logout` → 로그아웃
4. **UI 테스트** — Chrome MCP 사용 가능 시 (`/test-run` 스킬 위임):
   - 로그인 페이지 렌더링 확인
   - 회원가입 폼 필드 확인
   - 약관 관리 페이지 CRUD 확인

#### C. 디버깅 자동화

테스트 실패 시 다음 디버깅 사이클을 자동으로 수행한다:

```
반복 (최대 5회):
  1. 실패한 테스트 / 에러 로그 분석
  2. 원인 파악 (컴파일 에러, 런타임 에러, 로직 에러)
  3. 수정 코드 작성 및 적용
  4. 테스트 재실행
  5. 성공 시 → 사이클 종료
  6. 실패 시 → 1로 돌아감
```

5회 반복 후에도 실패하면 `AskUserQuestion`으로 사용자에게 도움을 요청한다:

```
## 테스트 디버깅 지원 요청

다음 테스트가 {N}회 시도 후에도 실패합니다:

### 실패 테스트
- {test-name}: {error-message}

### 시도한 수정
1. {attempt-1}
2. {attempt-2}
...

### 현재 상태
- 에러 로그: {last-error}
- 의심 원인: {suspected-cause}

환경 설정이나 외부 서비스 연동 문제일 수 있습니다.
확인이 필요한 사항을 알려주세요.
```

#### D. 테스트 리포트 생성

테스트 결과를 `docs/tests/test-reports/sprint-{N}/auth-test-report.md`에 기록한다:

```markdown
# 인증 모듈 테스트 리포트

## 실행 환경
- Date: {TIMESTAMP}
- Framework: {test-framework}
- Node/Java/Python: {version}

## 유닛/통합 테스트 결과
| Suite | Tests | Pass | Fail | Skip | Coverage |
|-------|-------|------|------|------|----------|
| auth-infra | {n} | {n} | {n} | {n} | {n}% |
| auth-api | {n} | {n} | {n} | {n} | {n}% |
| user-api | {n} | {n} | {n} | {n} | {n}% |
| terms-api | {n} | {n} | {n} | {n} | {n}% |
| **Total** | **{n}** | **{n}** | **{n}** | **{n}** | **{n}%** |

## E2E 테스트 결과
| Scenario | Result | Notes |
|----------|--------|-------|
| 회원가입 (이메일) | PASS/FAIL | {notes} |
| 로그인 (소셜) | PASS/FAIL | {notes} |
| ... | | |

## 디버깅 이력
| # | 실패 원인 | 수정 내용 | 결과 |
|---|----------|----------|------|
| 1 | {cause} | {fix} | Fixed |
| 2 | {cause} | {fix} | Fixed |

## 미해결 이슈
- {unresolved-issue-1}
- {unresolved-issue-2}
```

---

### Step 6: 최종 보고 및 프로그레스 업데이트

#### A. 프로그레스 트래커 최종 업데이트

`docs/sprints/sprint-{N}-auth/progress.md`의 모든 Feature 상태를 최종 업데이트한다.

#### B. 최종 결과 보고

```
## 인증 모듈 자동 구축 완료

### 파이프라인 실행 결과
| 단계 | 결과 | 산출물 |
|------|------|--------|
| 1. 블루프린트 | Done | docs/blueprints/{NNN}-auth/blueprint.md |
| 2. 스프린트 계획 | Done | docs/sprints/sprint-{N}-auth/prompt-map.md, progress.md |
| 3. 구현 | Done | {총 파일 수}개 파일 생성/수정 |
| 4. 테스트 시나리오 | Done | {총 시나리오 수}개 시나리오 |
| 5. 테스트/디버깅 | Done | Pass: {n}, Fail: {n}, Coverage: {n}% |

### 구현된 기능 요약
| 카테고리 | 기능 | API | 화면 | 테스트 |
|---------|------|-----|------|--------|
| 인증 | 회원가입 (이메일+소셜) | POST /auth/signup | /auth/signup | {n}개 |
| 인증 | 로그인 | POST /auth/login | /auth/login | {n}개 |
| 인증 | 토큰 갱신 | POST /auth/refresh | - | {n}개 |
| 인증 | 로그아웃 | POST /auth/logout, /logout-all | - | {n}개 |
| 인증 | 비밀번호 찾기 | Firebase | /auth/forgot-password | {n}개 |
| 사용자 | 프로필 관리 | GET/PATCH/DELETE /users/me | /admin/profile | {n}개 |
| 사용자 | 비밀번호 변경 | Firebase | /admin/profile/change-password | {n}개 |
| 사용자 | 사용자 관리 (ADMIN) | /users, /users/[id]/* | /admin/settings/users | {n}개 |
| 약관 | 약관 동의/철회 | /terms/agree, /terms/[id]/revoke | /auth/terms-agreement | {n}개 |
| 약관 | 약관 관리 (ADMIN) | /terms CRUD | /admin/settings/terms | {n}개 |

### 보안 체크리스트
- [ ] HttpOnly Cookie로 토큰 저장
- [ ] Token Rotation 구현
- [ ] Refresh Token 해시 저장
- [ ] Rate Limiting 적용
- [ ] CSRF 방지 (SameSite Cookie)
- [ ] XSS 방지 (CSP 헤더)
- [ ] 비밀번호 정책 적용
- [ ] Soft Delete + 개인정보 마스킹

### 다음 단계
1. `/test-run`으로 Chrome MCP 기반 UI 테스트 실행
2. 환경 변수 실제 값 설정 (Firebase, DB, JWT Secret)
3. Firebase 프로젝트 설정 (소셜 로그인 제공자 활성화)
4. 프로덕션 배포 전 보안 검토
```

## Quick Run Examples

```
# 현재 프로젝트에 인증 모듈 구축
/auth-module

# 특정 프로젝트 경로에 인증 모듈 구축
/auth-module /path/to/my-project

# 인자로 프로젝트 경로 지정
/auth-module ~/projects/my-app
```

## Notes

- 레퍼런스 설계 문서는 AMA 프로젝트 기준이며, 대상 프로젝트 기술 스택에 자동 적응됨
- Firebase Auth 없이 자체 인증을 구현하는 경우에도 지원 (bcrypt + 이메일 검증)
- 워크스페이스 연동은 대상 프로젝트에 워크스페이스 모듈이 있는 경우에만 적용
- 기존 인증 코드가 있는 경우 덮어쓰지 않고 통합/확장 방식으로 처리
- 모든 DB 컬럼명은 공공 데이터 표준 네이밍 규칙을 따름
- 디버깅 자동화는 최대 5회까지 시도하며, 이후 사용자에게 도움 요청
