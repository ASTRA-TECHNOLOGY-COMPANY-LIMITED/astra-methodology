---
name: payment-module
description: "구독 결제 모듈을 자동으로 구축합니다. 레퍼런스 설계 문서를 기반으로 블루프린트 작성, 스프린트 생성, 구현, 테스트 시나리오 작성, 테스트 실행 및 디버깅까지 전체 파이프라인을 자동 실행합니다. 플랜 관리, 결제 수단(빌링키), 구독 관리, 청구서/결제, PG사 연동(토스페이먼츠/KCP), 웹훅, 정기결제 스케줄러, Dunning(재시도), 크레딧 관리, 비례 배분(Proration) 기능을 포함합니다."
argument-hint: "[target-project-path]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Agent
---

# ASTRA 구독 결제 모듈 자동 구축

레퍼런스 설계 문서(`$CLAUDE_PLUGIN_ROOT/docs/payment/system-design.md`)를 기반으로 대상 프로젝트에 구독 결제 모듈 전체를 자동 구축합니다.

**자동 구축 범위**:
- 플랜 관리 (CRUD + 기능/제한 설정)
- 결제 수단 관리 (빌링키 발급/등록/삭제, AES-256 암호화)
- 구독 관리 (시작/변경/해지/일시정지/재개, 비례 배분)
- 청구서/결제 (자동 생성, 수동 결제, 환불)
- PG사 연동 (PG-Agnostic 추상화, 토스페이먼츠/KCP 어댑터)
- 웹훅 수신 (서명 검증, 멱등성 보장)
- 정기결제 스케줄러 (Cron 기반 자동 갱신)
- Dunning (결제 실패 재시도 4단계 전략)
- 크레딧 관리 (할당/차감/만료/재조정, 원자적 처리)
- 화면 구현 (요금제 안내, 결제 수단, 구독 관리, 결제 내역, 크레딧 관리)
- 모듈 통합 (인증: JWT, 워크스페이스: 멤버십+역할 검증)

## 실행 절차

### Step 0: 사전 준비 및 컨텍스트 수집

#### A. 레퍼런스 설계 문서 로드

`$CLAUDE_PLUGIN_ROOT/docs/payment/system-design.md` 파일을 읽어 레퍼런스 설계 정보를 로드한다:

1. 아키텍처 개요 — 워크스페이스 기반 구독, PG-Agnostic, Event-Driven, 멱등성, 금액 무결성 (섹션 1)
2. 기술 스택 — 토스페이먼츠 SDK, node-cron, crypto-js, dayjs, nanoid (섹션 2)
3. 데이터베이스 스키마 — 13개 테이블 (섹션 3):
   - TB_PAY_PLAN (플랜), TB_PAY_PLAN_FNC (플랜 기능)
   - TB_PAY_STLM_MTHD (결제 수단), TB_PAY_SBSC (구독), TH_PAY_SBSC (구독 이력)
   - TB_PAY_INVC (청구서), TB_PAY_INVC_ARTCL (청구 항목)
   - TB_PAY_STLM (결제), TL_PAY_BILNG_EVNT (빌링 이벤트 로그)
   - TL_PAY_WBHK_EVNT (웹훅 이벤트), TH_PAY_STLM_RTRY (결제 재시도 이력)
   - TB_PAY_CRDT_BLNC (크레딧 잔액), TL_PAY_CRDT_TRNS (크레딧 거래 로그)
4. API 설계 — 플랜/결제수단/구독/청구서/웹훅/크레딧 엔드포인트 (섹션 4)
5. 화면 구성 — 요금제, 결제 수단, 구독 관리, 결제 내역, 크레딧 관리, 관리자 페이지 (섹션 5)
6. 결제 흐름 — 구독 시작, 정기결제, 상태 전이, Dunning, 비례 배분, 크레딧 생명주기 (섹션 6)
7. 보안 설계 — 빌링키 암호화, 웹훅 서명, PCI DSS, Rate Limiting (섹션 7)
8. 디렉토리 구조 (섹션 8)
9. 구현 순서 — Phase 1~6 (섹션 9)

> **중요**: 레퍼런스는 **AMA 프로젝트(Next.js 14 + PostgreSQL + Drizzle ORM + 토스페이먼츠)**를 기준으로 작성되었다. 대상 프로젝트의 기술 스택에 맞게 **적응(adapt)**해야 한다.

#### B. 대상 프로젝트 분석

`$ARGUMENTS`에서 대상 프로젝트 경로를 파싱한다. 인자가 없으면 현재 작업 디렉토리를 사용한다.

대상 프로젝트에서 다음을 분석한다:

1. `CLAUDE.md` 읽기 — 기술 스택, 프로젝트 구조, 컨벤션 확인
2. `package.json` 또는 `build.gradle` 또는 `pom.xml` 또는 `pyproject.toml` 읽기 — 프레임워크/의존성 파악
3. `docs/blueprints/` 스캔 — 기존 블루프린트 번호 확인 (다음 번호 결정)
4. `docs/database/database-design.md` 읽기 — 기존 DB 스키마 확인 (특히 인증/워크스페이스 모듈 테이블)
5. `docs/sprints/` 스캔 — `sprint-{N}-{name}/` 패턴 디렉토리에서 현재 스프린트 번호 확인
6. `src/` 스캔 — 기존 코드 구조, 라우팅 패턴, 인증/워크스페이스 모듈 코드 확인
7. `src/styles/design-tokens.css` + `docs/design-system/` 스캔 — 디자인 토큰, 컴포넌트 패턴 확인

#### C. 선행 모듈 의존성 확인

결제 모듈은 **인증 모듈**과 **워크스페이스 모듈**에 **의존**한다. 다음을 확인한다:

**인증 모듈 (필수)**:
1. TB_COMM_USER 테이블 존재 여부
2. JWT 인증 미들웨어 존재 여부

**워크스페이스 모듈 (필수)**:
1. TB_COMM_WKSPC 테이블 존재 여부
2. TR_COMM_WKSPC_MBR 테이블 존재 여부
3. 워크스페이스 멤버십/역할 검증 미들웨어 존재 여부

선행 모듈이 없는 경우 `AskUserQuestion`으로 사용자에게 알린다:

```
## 선행 모듈 의존성 확인

결제 모듈은 인증 모듈(TB_COMM_USER, JWT)과 워크스페이스 모듈(TB_COMM_WKSPC, TR_COMM_WKSPC_MBR)에 의존합니다.

감지 결과:
- 인증 모듈: {감지됨/미감지}
- 워크스페이스 모듈: {감지됨/미감지}

다음 중 선택해 주세요:
1. 미감지된 모듈을 먼저 구축 (/auth-module, /workspace-module 순서대로 실행)
2. 기존 인증/워크스페이스 시스템이 있으며 경로를 알려주겠음
3. 선행 모듈 없이 결제 모듈만 구축 (사용자/워크스페이스 테이블 직접 생성)
```

#### D. 기술 스택 적응 매트릭스

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
| 토스페이먼츠 SDK | Stripe | `stripe` 라이브러리, Stripe Billing API |
| 토스페이먼츠 SDK | 자체 PG 연동 | PG 추상화 인터페이스에 맞춰 어댑터 구현 |
| node-cron | Spring Scheduler | `@Scheduled` 어노테이션 |
| node-cron | APScheduler (Python) | `BackgroundScheduler` |
| crypto-js (AES) | Java | `javax.crypto.Cipher` AES/GCM |
| crypto-js (AES) | Python | `cryptography.fernet` |
| React (TSX) | React (TSX) | 그대로 사용 |
| React (TSX) | Vue 3 | Composition API + `<script setup>` |
| React (TSX) | Angular | Component + Service + Guard |
| React (TSX) | React Native | RN 컴포넌트 + AsyncStorage |
| Zod (검증) | class-validator (Java/TS) | `@IsNotEmpty`, `@IsNumber` 등 |
| Zod (검증) | Pydantic (Python) | `BaseModel` + `Field` |

적응이 필요한 경우 `AskUserQuestion`으로 사용자에게 확인한다:

```
## 결제 모듈 기술 스택 확인

레퍼런스: Next.js 14 + PostgreSQL + Drizzle ORM + 토스페이먼츠
대상 프로젝트: {detected-tech-stack}

다음 사항을 확인해 주세요:
1. PG사: 토스페이먼츠 / Stripe / NHN KCP / 나이스페이 / 기타 ({detected})
2. ORM: {detected}
3. 암호화 라이브러리: {detected or recommended}
4. 프론트엔드 프레임워크: {detected}
5. 스케줄러: {detected or recommended}

추가 요구사항이 있으면 알려주세요 (예: PG사 추가, 통화 변경, 크레딧 미사용 등).
```

#### E. 기능 모듈 정의

레퍼런스 설계 문서에서 추출한 결제 모듈 기능 목록:

| # | 그룹 | 기능 | API 엔드포인트 | 화면 |
|---|------|------|--------------|------|
| 1 | 플랜 | 플랜 목록 조회 | `GET /billing/plans` | `/pricing` |
| 2 | 플랜 | 플랜 상세 조회 | `GET /billing/plans/[id]` | - |
| 3 | 플랜 | 플랜 생성 | `POST /billing/plans` | `/admin/settings/plans` |
| 4 | 플랜 | 플랜 수정 | `PATCH /billing/plans/[id]` | `/admin/settings/plans/[id]` |
| 5 | 결제 수단 | 결제 수단 목록 | `GET /workspaces/[wsId]/billing/payment-methods` | `billing/payment-method` |
| 6 | 결제 수단 | 결제 수단 등록 (빌링키) | `POST /workspaces/[wsId]/billing/payment-methods` | `billing/payment-method` |
| 7 | 결제 수단 | 기본 결제 수단 변경 | `PATCH .../payment-methods/[id]/default` | - |
| 8 | 결제 수단 | 결제 수단 삭제 | `DELETE .../payment-methods/[id]` | - |
| 9 | 구독 | 현재 구독 조회 | `GET .../subscriptions/current` | `billing/subscription` |
| 10 | 구독 | 구독 시작 | `POST .../subscriptions` | `billing/subscription` |
| 11 | 구독 | 플랜 변경 (비례 배분) | `PATCH .../subscriptions/[id]/plan` | 모달 |
| 12 | 구독 | 구독 해지 | `POST .../subscriptions/[id]/cancel` | 모달 |
| 13 | 구독 | 구독 일시정지 | `POST .../subscriptions/[id]/pause` | - |
| 14 | 구독 | 구독 재개 | `POST .../subscriptions/[id]/resume` | - |
| 15 | 구독 | 전체 구독 목록 (관리자) | `GET /billing/subscriptions` | `/admin/settings/subscriptions` |
| 16 | 청구서 | 청구서 목록 | `GET .../invoices` | `billing/invoices` |
| 17 | 청구서 | 청구서 상세 | `GET .../invoices/[id]` | `billing/invoices/[id]` |
| 18 | 청구서 | 수동 결제 | `POST .../invoices/[id]/pay` | - |
| 19 | 결제 | 환불 처리 (관리자) | `POST /billing/payments/[id]/refund` | - |
| 20 | 웹훅 | 토스페이먼츠 웹훅 | `POST /billing/webhook/toss` | - |
| 21 | 웹훅 | KCP 웹훅 | `POST /billing/webhook/kcp` | - |
| 22 | 크레딧 | 내 크레딧 조회 | `GET .../credits/me` | `billing/subscription` |
| 23 | 크레딧 | 크레딧 사용 내역 | `GET .../credits/me/history` | - |
| 24 | 크레딧 | 크레딧 확인 | `GET .../credits/check` | - |
| 25 | 크레딧 | 크레딧 차감 (내부) | `POST .../credits/deduct` | - |
| 26 | 크레딧 | 멤버별 크레딧 현황 | `GET .../credits/members` | `billing/credits` |
| 27 | 크레딧 | 크레딧 수동 조정 | `POST .../credits/[userId]/adjust` | `billing/credits` |
| 28 | 인프라 | PG 추상화 레이어 | - | - |
| 29 | 인프라 | 빌링키 암호화/복호화 | - | - |
| 30 | 인프라 | 비례 배분 계산 유틸 | - | - |
| 31 | 인프라 | 정기결제 스케줄러 | - | - |
| 32 | 인프라 | Dunning 매니저 | - | - |

---

### Step 1: 블루프린트 자동 작성

#### A. 블루프린트 번호 결정

`docs/blueprints/` 디렉토리를 스캔하여 기존 번호 중 가장 큰 값 + 1로 결정한다.

#### A-1. 작업 브랜치 생성

블루프린트 파일을 생성하기 전에, `dev` 브랜치로부터 작업 브랜치를 생성한다.

1. **현재 브랜치 확인**: `git branch --show-current`
2. **이미 작업 브랜치인 경우 스킵**: 현재 브랜치가 `feat/` 접두사로 시작하면 브랜치 생성을 건너뛴다
3. **미커밋 변경사항 보존**: `git status --porcelain`으로 확인하여 변경사항이 있으면 `git stash`로 임시 저장한다
4. **dev 브랜치 최신화**: `git fetch origin dev && git checkout dev && git pull origin dev`
5. **작업 브랜치 생성**: `git checkout -b feat/{NNN}-payment`
6. **stash 복원**: step 3에서 stash 했으면 `git stash pop`으로 복원한다
7. **브랜치 충돌 시**: 동일 이름의 브랜치가 이미 존재하면 `-v2`, `-v3` 접미사를 붙인다

> **참고**: `dev` 브랜치가 존재하지 않으면 `main` 또는 `master` 브랜치에서 생성한다. 어떤 기본 브랜치도 없으면 현재 브랜치에서 생성한다.

#### B. 블루프린트 파일 생성

`docs/blueprints/{NNN}-payment/blueprint.md` 파일을 생성한다.

블루프린트에 포함할 내용 (레퍼런스 설계를 대상 프로젝트에 맞게 적응):

1. **모듈 개요**: 워크스페이스 기반 구독 결제, PG-Agnostic, Event-Driven, 멱등성
2. **아키텍처 설계**: 클라이언트-서버-PG사 3계층, 추상화 레이어
3. **기술 스택**: 대상 프로젝트에 맞게 적응된 의존성
4. **데이터베이스 설계**: 13개 테이블 DDL (대상 ORM에 맞게 변환)
   - 플랜: TB_PAY_PLAN, TB_PAY_PLAN_FNC
   - 결제 수단: TB_PAY_STLM_MTHD
   - 구독: TB_PAY_SBSC, TH_PAY_SBSC
   - 청구서: TB_PAY_INVC, TB_PAY_INVC_ARTCL
   - 결제: TB_PAY_STLM
   - 이벤트: TL_PAY_BILNG_EVNT, TL_PAY_WBHK_EVNT
   - 재시도: TH_PAY_STLM_RTRY
   - 크레딧: TB_PAY_CRDT_BLNC, TL_PAY_CRDT_TRNS
5. **API 설계**: 32개 기능의 엔드포인트, 요청/응답 스키마, 권한 모델
6. **화면 설계**: 요금제 안내, 결제 수단, 구독 관리, 결제 내역, 크레딧 관리, 관리자 페이지
7. **결제 흐름**: 구독 시작, 정기결제, 상태 전이도, Dunning 전략, 비례 배분 계산
8. **크레딧 생명주기**: 할당, 차감, 만료, 재조정, 멤버 가입/탈퇴 연동
9. **보안 설계**: 빌링키 AES-256, 웹훅 HMAC, 멱등성 키, PCI DSS, Rate Limiting
10. **구현 순서**: Phase 1~6 순서

`docs/database/database-design.md`에 결제 모듈 테이블 13개를 추가한다 (기존 내용 보존).

블루프린트 작성 완료 후 `AskUserQuestion`으로 사용자에게 확인한다:

```
## 블루프린트 검토

결제 모듈 블루프린트가 생성되었습니다:
- 파일: docs/blueprints/{NNN}-payment/blueprint.md
- DB 테이블: 13개 (TB_PAY_PLAN, TB_PAY_SBSC 등)
- API: 32개 기능 (6개 그룹)
- 화면: 9개 페이지
- 크레딧 관리: 6개 API + 크레딧 생명주기

블루프린트를 확인하고 수정사항이 있으면 알려주세요.
계속 진행할까요?
```

선택지: "예, 계속 진행", "수정 필요 — 피드백 제공"

---

### Step 2: 스프린트 생성

#### 스프린트 번호 결정

`docs/sprints/` 디렉토리에서 `sprint-{N}-{name}/` 패턴 디렉토리를 스캔하여 다음 스프린트 번호를 결정한다.

#### 프롬프트 맵 생성

결제 모듈의 6개 Phase를 Feature 단위로 분할하여 `docs/sprints/sprint-{N}-payment/prompt-map.md` 파일을 생성한다:

```markdown
# Sprint {N} - 구독 결제 모듈

## Feature 1: 기반 인프라
- DB 스키마 정의 (13개 테이블)
- DB 마이그레이션
- 빌링키 암호화/복호화 유틸
- 비례 배분 계산 유틸
- Zod 검증 스키마
- PG 추상화 인터페이스

## Feature 2: PG 연동 + 결제 수단
- PG사 어댑터 (토스페이먼츠/KCP)
- PG 어댑터 팩토리 + 에러 매핑
- 결제 수단 CRUD API (4개)
- 웹훅 수신 핸들러 (토스/KCP)

## Feature 3: 구독 관리
- 플랜 CRUD API (4개)
- 구독 시작/조회/변경/해지/일시정지/재개 API (7개)
- 청구서 생성 로직
- 구독 상태 관리 로직

## Feature 4: 크레딧 + 스케줄러 + Dunning
- 크레딧 매니저 서비스 (할당/차감/만료/재조정)
- 크레딧 API (6개)
- 크레딧 가드 미들웨어
- 정기결제 스케줄러 (Cron)
- Dunning 매니저 (4단계 재시도)
- 청구서/결제 API (4개)

## Feature 5: 화면 구현
- 요금제 안내 페이지 (Public)
- 결제 수단 관리 페이지
- 구독 관리 페이지 + 플랜 변경/해지 모달
- 결제 내역 페이지 (목록/상세)
- 결제 실패 안내 페이지
- 크레딧 관리 페이지
- 크레딧 UI 컴포넌트 (사용률 배지, 소진 배너)

## Feature 6: 관리자 + 통합
- 플랜 관리 페이지 (SYSTEM ADMIN)
- 구독 현황 대시보드 (SYSTEM ADMIN)
- 워크스페이스 모듈 연동 (멤버 가입/탈퇴 → 크레딧 할당/만료)
- WorkspaceSubscriptionContext
- Rate Limiting 적용
```

#### 프로그레스 트래커 생성

`docs/sprints/sprint-{N}-payment/progress.md` 파일을 생성한다:

```markdown
# Sprint {N} Progress Tracker

## Sprint Information
- **Sprint Number**: {N}
- **Sprint Goal**: 구독 결제 모듈 전체 구축
- **Start Date**: {TODAY}
- **End Date**: {TODAY + 7 days}
- **Status**: In Progress

<!-- PROGRESS_TABLE_START -->
## Feature Progress

| Feature | Blueprint | DB Design | Test Cases | Implementation | Test Report | Status |
|---------|-----------|-----------|------------|----------------|-------------|--------|
| F1. 기반 인프라 | Done | - | - | - | - | Not Started |
| F2. PG 연동 + 결제 수단 | Done | Done | - | - | - | Not Started |
| F3. 구독 관리 | Done | Done | - | - | - | Not Started |
| F4. 크레딧 + 스케줄러 + Dunning | Done | Done | - | - | - | Not Started |
| F5. 화면 구현 | Done | N/A | - | - | - | Not Started |
| F6. 관리자 + 통합 | Done | N/A | - | - | - | Not Started |

**Legend**: `-` Not Started, `WIP` In Progress, `Done` Completed, `N/A` Not Applicable
<!-- PROGRESS_TABLE_END -->

<!-- SUMMARY_START -->
## Summary
- **Total Features**: 6
- **Completed**: 0
- **In Progress**: 0
- **Overall Progress**: 0%
- **Last Updated**: {TIMESTAMP}
<!-- SUMMARY_END -->

<!-- ACTIVITY_LOG_START -->
## Activity Log

| Timestamp | Event | File | Details |
|-----------|-------|------|---------|
| {TIMESTAMP} | blueprint | docs/blueprints/{NNN}-payment/blueprint.md | 결제 모듈 블루프린트 생성 |
| {TIMESTAMP} | db-design | docs/database/database-design.md | 결제 테이블 13개 추가 |
<!-- ACTIVITY_LOG_END -->
```

---

### Step 3: 구현 실행

Step 0에서 분석한 대상 프로젝트의 기술 스택에 맞게 레퍼런스 설계를 적응하여 구현한다.

#### Phase 1: 기반 인프라

1. **의존성 설치**: PG SDK, 스케줄러, 암호화, 날짜, nanoid
2. **환경 변수 추가**: PG 키, 빌링키 암호화 키, 스케줄러 설정
3. **DB 스키마 정의**: 13개 테이블을 대상 ORM에 맞게 작성
   - Drizzle: `lib/db/schema/billing.ts`
   - JPA: 엔티티 클래스 13개
   - Prisma: `schema.prisma` 모델 추가
   - SQLAlchemy: 모델 클래스 13개
4. **DB 마이그레이션**: DDL 전문 또는 ORM 마이그레이션 실행
5. **빌링키 암호화 유틸**: AES-256-GCM 암호화/복호화
6. **비례 배분 계산 유틸**: 업그레이드/다운그레이드 일할 계산
7. **Zod/검증 스키마**: 모든 API 입력 검증 스키마
8. **PG 추상화 인터페이스**: `PaymentGateway` 인터페이스 (issueBillingKey, chargeBillingKey, getPayment, cancelPayment)

#### Phase 2: PG 연동 + 결제 수단

1. **토스페이먼츠 어댑터**: 빌링키 발급, 빌링키 결제, 결제 조회, 결제 취소
2. **KCP 어댑터** (선택): 대체 PG사 어댑터
3. **PG 어댑터 팩토리**: `PG_PRVDR_CD`에 따른 어댑터 선택
4. **PG 에러 코드 매핑**: PG사별 에러 코드 → 공통 에러 변환
5. **결제 수단 목록 API**: `GET /workspaces/[wsId]/billing/payment-methods`
6. **결제 수단 등록 API**: `POST /workspaces/[wsId]/billing/payment-methods` (빌링키 발급 → 암호화 → 저장)
7. **기본 결제 수단 변경 API**: `PATCH .../payment-methods/[id]/default`
8. **결제 수단 삭제 API**: `DELETE .../payment-methods/[id]` (활성 구독 사용 중이면 거부)
9. **웹훅 핸들러**: HMAC 서명 검증, 멱등성 체크, 이벤트 처리

#### Phase 3: 구독 관리

1. **플랜 CRUD API**: 활성 플랜 목록 (Public), 플랜 생성/수정 (SYSTEM ADMIN)
2. **구독 시작 API**: 플랜 검증 → 활성 구독 중복 확인 → 무료 체험/즉시 결제 분기
3. **현재 구독 조회 API**: 플랜 정보 + 결제 수단 + 다음 결제 예정
4. **플랜 변경 API**: 비례 배분 계산 → 업그레이드(즉시 결제) / 다운그레이드(크레딧)
5. **구독 해지 API**: 기간 종료 해지 / 즉시 해지(비례 환불)
6. **구독 일시정지/재개 API**: 상태 전이 + 이벤트 기록
7. **청구서 생성 로직**: 구독 갱신 시 자동 생성, 항목 추가, 세금 계산
8. **구독 상태 관리 로직**: 상태 전이도 구현 (TRIALING → ACTIVE → PAST_DUE → SUSPENDED → CANCELED)

#### Phase 3.5: 크레딧 관리

1. **크레딧 매니저 서비스**: `allocateCreditsForPeriod`, `deductCredits` (SELECT FOR UPDATE), `expireCreditsForPeriod`, `adjustCreditsForPlanChange`
2. **크레딧 가드 미들웨어**: 크레딧 필요 API에 적용, 잔액 부족 시 403
3. **크레딧 API 6개**: 내 잔액 조회, 사용 내역, 확인, 차감, 멤버별 현황, 수동 조정
4. **구독 생성/갱신 시 크레딧 할당 연동**: subscription-manager 수정
5. **스케줄러 크레딧 리셋 연동**: 이전 기간 만료 + 신규 기간 할당
6. **멤버 가입/탈퇴 시 크레딧 연동**: 비례 할당 / 만료 처리

#### Phase 4: 스케줄러 + Dunning

1. **정기결제 스케줄러**: 매일 09:00 KST 실행, 만료 구독 조회, 청구서 생성 + 결제
2. **Dunning 매니저**: 4단계 재시도 (1시간/24시간/72시간/7일), 카드사 응답별 전략
3. **청구서 목록/상세 API**: 워크스페이스별 청구서 조회
4. **수동 결제 API**: 미결제 청구서 수동 결제
5. **환불 API**: 전액/부분 환불 (SYSTEM ADMIN)
6. **WorkspaceSubscriptionContext**: 구독 상태 + 크레딧 정보 Context
7. **구독/결제 Hooks**: `useWorkspaceSubscription`, `useWorkspacePaymentMethod`, `useWorkspaceCredit`

#### Phase 5: 화면 구현

1. **요금제 안내 페이지** (`/pricing`): 플랜 비교, 월간/연간 토글, 구독 시작 CTA
2. **결제 수단 관리 페이지**: 카드 목록, PG 결제창 연동, 기본 설정, 삭제
3. **구독 관리 페이지**: 현재 구독 정보, 포함 기능, 사용량, 크레딧 사용률
4. **결제 내역 페이지**: 청구서 목록 테이블, 상세 페이지
5. **결제 실패 안내 페이지**: 결제 수단 변경 안내
6. **크레딧 관리 페이지**: 멤버별 크레딧 현황 테이블, 수동 조정
7. **모달**: 플랜 변경 모달 (비례 배분 안내), 구독 해지 모달
8. **공통 컴포넌트**: PricingCard, PaymentMethodCard, SubscriptionStatusBadge, InvoiceTable, CreditUsageBadge, CreditExhaustedBanner

#### Phase 6: 관리자 + 통합

1. **플랜 관리 페이지** (SYSTEM ADMIN): 플랜 CRUD
2. **구독 현황 대시보드** (SYSTEM ADMIN): 전체 구독 통계
3. **워크스페이스 모듈 연동**: 멤버 가입 → 비례 크레딧 할당, 멤버 탈퇴 → 크레딧 만료
4. **Rate Limiting 적용**: 결제 관련 엔드포인트별 제한
5. **다국어 메시지**: 결제 관련 번역 키 추가

각 Phase 완료 시 `progress.md`를 업데이트한다.

---

### Step 4: 테스트 시나리오 자동 작성

구현 완료 후 `docs/tests/` 디렉토리에 E2E 테스트 시나리오를 생성한다.

#### 테스트 시나리오 그룹

**TS-1: 플랜 관리**
- TC-1.1: 활성 플랜 목록 조회 (Public)
- TC-1.2: 플랜 상세 조회 (기능 포함)
- TC-1.3: 플랜 생성 (SYSTEM ADMIN)
- TC-1.4: 비인가 사용자 플랜 생성 시도 (403)

**TS-2: 결제 수단**
- TC-2.1: 빌링키 발급 + 결제 수단 등록
- TC-2.2: 결제 수단 목록 조회
- TC-2.3: 기본 결제 수단 변경
- TC-2.4: 결제 수단 삭제 (활성 구독 없음)
- TC-2.5: 활성 구독 사용 중 삭제 시도 (거부)
- TC-2.6: 비 OWNER/ADMIN 결제 수단 등록 시도 (403)

**TS-3: 구독 관리**
- TC-3.1: 구독 시작 (무료 체험 포함)
- TC-3.2: 구독 시작 (즉시 결제)
- TC-3.3: 기존 활성 구독 있는 WS에 중복 구독 시도 (409)
- TC-3.4: 현재 구독 조회 (플랜 정보 + 다음 결제일)
- TC-3.5: 플랜 업그레이드 (비례 배분 즉시 결제)
- TC-3.6: 플랜 다운그레이드 (크레딧 적용)
- TC-3.7: 구독 해지 (기간 종료 후)
- TC-3.8: 구독 즉시 해지 (비례 환불)
- TC-3.9: 구독 일시정지 + 재개
- TC-3.10: 비인가 사용자 구독 관리 시도 (403)

**TS-4: 청구서/결제**
- TC-4.1: 청구서 목록 조회 (워크스페이스별)
- TC-4.2: 청구서 상세 조회 (항목 포함)
- TC-4.3: 미결제 청구서 수동 결제
- TC-4.4: 환불 처리 (SYSTEM ADMIN)

**TS-5: 웹훅**
- TC-5.1: 유효한 웹훅 수신 + 처리
- TC-5.2: 서명 불일치 웹훅 거부
- TC-5.3: 중복 웹훅 멱등성 처리

**TS-6: 정기결제 + Dunning**
- TC-6.1: 정기결제 스케줄러 실행 (결제 성공 → 구독 갱신)
- TC-6.2: 정기결제 실패 → PAST_DUE → Dunning 시작
- TC-6.3: Dunning 재시도 성공 → ACTIVE 복귀
- TC-6.4: Dunning 전체 실패 → SUSPENDED

**TS-7: 크레딧**
- TC-7.1: 구독 생성 시 크레딧 자동 할당
- TC-7.2: 크레딧 차감 (잔액 충분)
- TC-7.3: 크레딧 차감 (잔액 부족 → 403)
- TC-7.4: 크레딧 소진 → EXHAUSTED 상태
- TC-7.5: 빌링 기간 갱신 시 크레딧 리셋
- TC-7.6: 멤버 중도 가입 시 비례 크레딧 할당
- TC-7.7: 멤버 탈퇴 시 크레딧 만료
- TC-7.8: 플랜 변경 시 크레딧 재조정
- TC-7.9: 관리자 크레딧 수동 조정

**TS-8: 보안/엣지 케이스**
- TC-8.1: 멱등성 키 중복 결제 방지
- TC-8.2: Rate Limiting 초과 (429)
- TC-8.3: 비례 배분 금액 무결성 검증
- TC-8.4: 동시 크레딧 차감 원자성 (SELECT FOR UPDATE)
- TC-8.5: 만료된 카드 결제 시도 처리

---

### Step 5: 테스트 실행 및 디버깅

#### 테스트 환경 설정

1. 테스트용 PG 키 설정 (토스페이먼츠 테스트 키)
2. 테스트 DB 설정 (테스트용 스키마)
3. 테스트 데이터 Seed (플랜 + 플랜 기능 초기 데이터)

#### 테스트 실행

1. 서버 실행 (개발 모드)
2. 테스트 시나리오 순서대로 실행:
   - API 테스트: curl/fetch로 직접 호출
   - UI 테스트: Chrome MCP로 화면 검증 (사용 가능한 경우)
3. 각 TC의 성공/실패 기록

#### 자동 디버깅 사이클 (최대 5회 반복)

```
[테스트 실패 감지]
  │
  │ 1. 에러 메시지 분석
  │ 2. 관련 코드 확인 (API Route, Service, Schema)
  │ 3. 원인 파악 및 수정
  │ 4. 재테스트
  │
  └─ 성공 시 다음 TC로 이동
  └─ 5회 실패 시 사용자에게 도움 요청:
```

```
## 테스트 디버깅 지원 요청

다음 테스트 케이스가 5회 반복 디버깅 후에도 통과하지 못했습니다:
- TC: {테스트 케이스 ID}
- 에러: {에러 메시지}
- 시도한 수정: {수정 내역 목록}

도움을 주시거나 이 TC를 건너뛸지 결정해 주세요.
```

#### 테스트 리포트 생성

`docs/tests/test-reports/sprint-{N}/payment-test-report.md` 파일에 결과를 기록한다:

```markdown
# Test Report - Sprint {N} (구독 결제 모듈)

## Summary
- Total: {총 TC 수}
- Passed: {통과 수}
- Failed: {실패 수}
- Skipped: {건너뜀 수}

## Results
| TC ID | 시나리오 | 결과 | 비고 |
|-------|---------|------|------|
| TC-1.1 | 플랜 목록 조회 | PASS | - |
| ... | ... | ... | ... |
```

---

### Step 6: 최종 보고

모든 단계가 완료되면 최종 보고를 출력한다:

```
## 구독 결제 모듈 구축 완료

### 생성된 파일 요약
- 블루프린트: docs/blueprints/{NNN}-payment/blueprint.md
- DB 스키마: {schema-file-path} (13개 테이블)
- API: {api-count}개 엔드포인트
- 화면: {page-count}개 페이지
- 테스트: {tc-count}개 시나리오 ({pass-count} PASS)

### 주요 기능
- 플랜 관리 (CRUD + 기능/제한)
- 결제 수단 관리 (빌링키 AES-256 암호화)
- 구독 관리 (상태 전이 + 비례 배분)
- 크레딧 관리 (할당/차감/만료/재조정)
- PG사 연동 (PG-Agnostic 추상화)
- 정기결제 + Dunning (4단계 재시도)

### 환경 변수 설정 필요
- PG 키 (TOSS_SECRET_KEY 등)
- 빌링키 암호화 키 (BILLING_KEY_ENCRYPTION_KEY)
- 스케줄러 설정 (BILLING_SCHEDULER_ENABLED)

### 운영 전 체크리스트
- [ ] PG사 운영 키 발급 및 설정
- [ ] 빌링키 암호화 키를 KMS/Vault로 이전
- [ ] 웹훅 엔드포인트 PG사에 등록
- [ ] IP 화이트리스트 설정 (웹훅)
- [ ] Rate Limiting 임계값 조정
- [ ] 정기결제 스케줄러 cron 설정 확인
- [ ] Dunning 알림 이메일/SMS 템플릿 설정
- [ ] 초기 플랜 데이터 Seed 실행
```

`progress.md`의 해당 Feature 상태를 모두 완료로 업데이트한다.
