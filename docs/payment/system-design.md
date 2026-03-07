# 공통 구독 결제 모듈 설계 문서

> **프로젝트**: 공통 구독 결제 모듈 (Subscription Payment Module)
> **버전**: 1.1.0
> **작성일**: 2026-02-14
> **최종 수정일**: 2026-02-14 (크레딧 관리 기능 추가)
> **기반 레퍼런스**: 토스페이먼츠 정기결제 API, Stripe Billing, PCI DSS v4.0

---

## 목차

1. [아키텍처 개요](#1-아키텍처-개요)
2. [기술 스택](#2-기술-스택)
3. [데이터베이스 스키마](#3-데이터베이스-스키마)
4. [API 설계](#4-api-설계)
5. [화면 구성](#5-화면-구성)
6. [결제 흐름](#6-결제-흐름)
7. [보안 설계](#7-보안-설계)
8. [디렉토리 구조](#8-디렉토리-구조)
9. [구현 순서](#9-구현-순서)

---

## 1. 아키텍처 개요

### 1.1 설계 원칙

공통 구독 결제 모듈은 **여러 앱에서 재사용 가능한 독립적인 결제 모듈**로 설계한다. Next.js 14 App Router의 API Routes와 Server Actions를 활용하며, PG사 비종속(PG-Agnostic) 아키텍처를 채택하여 토스페이먼츠, NHN KCP, 나이스페이 등 다양한 PG사를 지원한다.

**핵심 설계 원칙**:
- **워크스페이스 기반 구독**: 구독·결제·청구의 주체는 개별 사용자가 아닌 **워크스페이스(Workspace)** 단위로 관리
- **PG-Agnostic**: PG사 추상화 레이어를 통해 복수 PG사 지원 및 교체 용이
- **Event-Driven**: 결제 상태 변경을 이벤트로 기록하여 완전한 감사 추적(Audit Trail) 보장
- **멱등성(Idempotency)**: 모든 결제 API에 멱등성 키를 적용하여 중복 결제 방지
- **금액 무결성**: 모든 금액은 최소 화폐 단위(원)로 BIGINT 저장, 부동소수점 사용 금지

### 1.2 아키텍처 다이어그램

```
┌──────────────────────────────────────────────────────────────────┐
│                    APP (Next.js 14)                                │
│                                                                    │
│  ┌──────────────────┐    ┌────────────────────────────────────┐  │
│  │   Client-Side     │    │           Server-Side               │  │
│  │                   │    │                                      │  │
│  │  Pages/           │───▶│  API Routes (/app/api/v1/billing/..)│  │
│  │  Components       │    │  Server Actions (쿠키/세션)          │  │
│  │  SubscriptionCtx  │    │  Middleware (JWT 검증)               │  │
│  │  PaymentWidgets   │◀───│  Webhook Handler                    │  │
│  └──────────────────┘    └──────────┬─────────────────────────┘  │
│                                      │                            │
└──────────────────────────────────────┼────────────────────────────┘
                                       │
                       ┌───────────────┼───────────────────┐
                       │               │                   │
                       ▼               ▼                   ▼
                ┌────────────┐  ┌────────────┐     ┌────────────┐
                │ PostgreSQL  │  │  PG 추상화  │     │  Scheduler │
                │ (Drizzle)   │  │   Layer     │     │  (Cron)    │
                └────────────┘  └──────┬─────┘     └────────────┘
                                       │
                        ┌──────────────┼──────────────┐
                        ▼              ▼              ▼
                 ┌────────────┐ ┌────────────┐ ┌────────────┐
                 │토스페이먼츠 │ │  NHN KCP   │ │  나이스페이  │
                 └────────────┘ └────────────┘ └────────────┘
```

### 1.3 타 모듈과의 관계

| 항목 | 인증 모듈 | 워크스페이스 모듈 | IAM 모듈 | 결제 모듈 |
|------|----------|-----------------|----------|----------|
| 사용자 식별 | `TB_COMM_USER.ID` 정의 | `comm_workspace_members.user_id` FK 참조 | `iam_user_roles.user_id` FK 참조 | 감사 로그에서 FK 참조 |
| 워크스페이스 식별 | `TB_COMM_USER.BSC_WKSPC_ID` FK | `TB_COMM_WKSPC.ID` 정의 | 권한 검사 시 워크스페이스 컨텍스트 참조 | `WKSPC_ID` FK로 구독·결제수단·청구서의 주체 |
| 인증/권한 | Firebase + JWT | 워크스페이스 멤버십 + 역할 검사 | 시스템 레벨 RBAC | 인증 JWT + 워크스페이스 `OWNER/ADMIN` 역할 |
| 미들웨어 | 인증 검증 | 멤버십 검증 미들웨어 | 시스템 권한 미들웨어 | 인증 + 워크스페이스 멤버십·역할 미들웨어 |
| DB 스키마 | `app` 스키마 | `app` 스키마 | `app` 스키마 | 동일 `app` 스키마 내 결제 테이블 추가 |

> **워크스페이스 기반 구독 모델**: 하나의 워크스페이스는 하나의 활성 구독을 가진다. 워크스페이스에 속한 모든 멤버가 해당 구독의 혜택을 공유하며, 결제 관리 권한은 워크스페이스 `OWNER` 또는 `ADMIN` 역할을 가진 멤버에게만 부여된다.
>
> **워크스페이스 모듈 의존**: 결제 모듈의 `TB_COMM_WKSPC` 테이블 참조는 워크스페이스 모듈(`lib/db/schema/workspace.ts`)에 정의되어 있다. 워크스페이스 생성·멤버 관리·초대 등의 상세는 [워크스페이스 관리 시스템 설계 문서](./workspace.md)를 참조한다.

---

## 2. 기술 스택

### 2.1 신규 추가 의존성

```json
{
  "dependencies": {
    "@tosspayments/tosspayments-sdk": "^2.x",
    "node-cron": "^3.x",
    "crypto-js": "^4.x",
    "dayjs": "^1.x",
    "nanoid": "^5.x"
  },
  "devDependencies": {
    "@types/node-cron": "^3.x",
    "@types/crypto-js": "^4.x"
  }
}
```

| 패키지 | 용도 |
|--------|------|
| `@tosspayments/tosspayments-sdk` | 토스페이먼츠 결제창 SDK (빌링키 발급) |
| `node-cron` | 정기결제 스케줄러 (빌링 주기 실행) |
| `crypto-js` | 빌링키 AES-256 암호화/복호화 |
| `dayjs` | 날짜 계산 (빌링 주기, 비례 배분) |
| `nanoid` | 멱등성 키, 주문 ID 생성 |

### 2.2 환경 변수

```env
# PG - TossPayments
NEXT_PUBLIC_TOSS_CLIENT_KEY=test_ck_...
TOSS_SECRET_KEY=test_sk_...
TOSS_WEBHOOK_SECRET=whsec_...

# PG - NHN KCP (Fallback)
KCP_SITE_CD=T0000
KCP_SITE_KEY=...

# Billing
BILLING_KEY_ENCRYPTION_KEY=your-256-bit-aes-key-here
BILLING_SCHEDULER_ENABLED=true
BILLING_RETRY_MAX_ATTEMPTS=4
BILLING_GRACE_PERIOD_DAYS=14

# Webhook
WEBHOOK_ENDPOINT_URL=https://your-app.com/api/v1/billing/webhook
```

---

## 3. 데이터베이스 스키마

### 3.1 ER 다이어그램

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│ TB_COMM_USER    │     │ TB_PAY_PLAN       │     │ TB_PAY_PLAN_FNC       │
│ (인증 모듈)    │     ├──────────────────┤     ├──────────────────────┤
│              │     │ ID (PK)          │◀───│ PLAN_ID (FK)         │
└──────────────┘     │ PLAN_NM          │     │ FNC_KEY              │
                     │ BILNG_INTRVL_CD  │     │ FNC_VL               │
┌────────────────┐   │ PLAN_AMT         │     └──────────────────────┘
│TB_COMM_WKSPC  │   │ CRNC_CD          │
│ (워크스페이스 모듈)│   │ TRIAL_DAY_CNT    │
└──────┬─────────┘   └────────┬─────────┘
       │                      │
       │    ┌─────────────────┼──────────────────┐
       │    │                 │                  │
       ▼    ▼                 ▼                  │
┌──────────────────┐  ┌──────────────────┐      │
│ TB_PAY_SBSC       │  │ TB_PAY_STLM_     │      │
├──────────────────┤  │   MTHD             │      │
│ ID (PK)          │  ├──────────────────┤      │
│ WKSPC_ID (FK)    │  │ ID (PK)          │      │
│ PLAN_ID (FK)     │  │ WKSPC_ID (FK)    │      │
│ STTS_CD          │  │ BILNG_KEY_ENCPT  │      │
│ CRNT_PRD_*       │  │ PG_PRVDR_CD      │      │
│ PRD_END_CNCL_YN  │  │ CARD_LAST4       │      │
└────────┬─────────┘  └──────────────────┘      │
         │                                       │
         │    ┌──────────────────────────────────┘
         │    │
         ▼    ▼
┌──────────────────┐     ┌──────────────────┐
│ TB_PAY_INVC       │     │ TB_PAY_INVC_     │
├──────────────────┤     │   ARTCL            │
│ ID (PK)          │◀───├──────────────────┤
│ SBSC_ID          │     │ INVC_ID (FK)     │
│ STTS_CD          │     │ ARTCL_AMT        │
│ TOT_AMT          │     │ TYPE_CD          │
│ UNPAY_AMT        │     └──────────────────┘
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌──────────────────┐
│ TB_PAY_STLM       │     │ TL_PAY_BILNG_    │
├──────────────────┤     │   EVNT             │
│ ID (PK)          │     ├──────────────────┤
│ INVC_ID (FK)     │     │ EVNT_TYPE_CD     │
│ IDMPTN_KEY       │     │ ENTTY_TYPE_CD    │
│ PG_STLM_KEY      │     │ ENTTY_ID         │
│ STTS_CD          │     │ WKSPC_ID (FK)    │
└──────────────────┘     │ USER_ID (FK)     │
                         │ EVNT_DATA (JSONB)│
                         └──────────────────┘

┌──────────────────┐     ┌──────────────────┐
│ TL_PAY_WBHK_     │     │ TH_PAY_STLM_     │
│   EVNT             │     │   RTRY             │
├──────────────────┤     ├──────────────────┤
│ PRVDR_CD         │     │ SBSC_ID          │
│ EXTRL_EVNT_ID    │     │ INVC_ID          │
│ EVNT_TYPE_CD     │     │ ATMT_SN          │
│ PYLD (JSONB)     │     │ TYPE_CD          │
│ STTS_CD          │     │ STTS_CD          │
└──────────────────┘     └──────────────────┘

┌──────────────────┐     ┌──────────────────┐
│ TB_PAY_CRDT_     │     │ TL_PAY_CRDT_     │
│   BLNC             │     │   TRNS             │
├──────────────────┤     ├──────────────────┤
│ ID (PK)          │◀───│ CRDT_BLNC_ID(FK) │
│ WKSPC_ID (FK)    │     │ WKSPC_ID (FK)    │
│ USER_ID (FK)     │     │ USER_ID (FK)     │
│ SBSC_ID (FK)     │     │ TRNS_TYPE_CD     │
│ PRD_BGNG_DT      │     │ TRNS_QTY         │
│ PRD_END_DT       │     │ BLNC_BFR_QTY     │
│ ALOT_QTY         │     │ BLNC_AFT_QTY     │
│ USED_QTY         │     │ RFRNC_TYPE_CD    │
│ RMNN_QTY         │     │ RFRNC_ID         │
│ STTS_CD          │     │ TRNS_DC          │
└──────────────────┘     └──────────────────┘
```

### 3.2 TB_PAY_PLAN 테이블

구독 플랜(상품) 정보를 관리하는 테이블.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 플랜 고유 식별자 |
| `PLAN_NM` | `VARCHAR(100)` | `NOT NULL` | - | 플랜 이름 (예: "Basic", "Pro") |
| `PLAN_DC` | `VARCHAR(500)` | - | NULL | 플랜 설명 |
| `BILNG_INTRVL_CD` | `VARCHAR(20)` | `NOT NULL` | - | 청구 주기 (`MONTHLY`, `YEARLY`) |
| `INTRVL_CNT` | `INTEGER` | `NOT NULL` | `1` | 주기 반복 횟수 (1=매월, 3=분기) |
| `PLAN_AMT` | `BIGINT` | `NOT NULL` | - | 금액 (원 단위) |
| `CRNC_CD` | `VARCHAR(3)` | `NOT NULL` | `'KRW'` | 통화 코드 |
| `TRIAL_DAY_CNT` | `INTEGER` | `NOT NULL` | `0` | 무료 체험 일수 |
| `SORT_SN` | `INTEGER` | `NOT NULL` | `0` | 표시 순서 |
| `ACTV_YN` | `CHAR(1)` | `NOT NULL` | `'Y'` | 활성 여부 (`Y`/`N`) |
| `MTDT` | `JSONB` | - | `'{}'` | 추가 메타데이터 |
| `CRTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 생성자 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 생성 일시 |
| `MDFR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 수정자 |
| `MDFCN_DT` | `TIMESTAMPTZ` | - | NULL | 수정 일시 |

**인덱스**:
```sql
CREATE INDEX idx_tb_pay_plan_actv ON app.TB_PAY_PLAN(ACTV_YN, SORT_SN);
```

**Enum 값**:

| 코드 유형 | 코드 | 설명 |
|-----------|------|------|
| `BILLING_INTERVAL` | `MONTHLY` | 월간 구독 |
| | `YEARLY` | 연간 구독 |

### 3.3 TB_PAY_PLAN_FNC 테이블

플랜별 기능/제한 정보를 관리하는 테이블.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 기능 식별자 |
| `PLAN_ID` | `BIGINT` | `FK(TB_PAY_PLAN.ID) ON DELETE CASCADE, NOT NULL` | - | 플랜 FK |
| `FNC_KEY` | `VARCHAR(100)` | `NOT NULL` | - | 기능 키 (예: `max_users`, `storage_gb`) |
| `FNC_VL` | `VARCHAR(255)` | `NOT NULL` | - | 기능 값 (예: `10`, `unlimited`) |
| `FNC_DC` | `VARCHAR(500)` | - | NULL | 기능 설명 |
| `CRTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 생성자 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 생성 일시 |
| `MDFR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 수정자 |
| `MDFCN_DT` | `TIMESTAMPTZ` | - | NULL | 수정 일시 |

**제약조건**:
```sql
CONSTRAINT uq_tb_pay_plan_fnc_key UNIQUE (PLAN_ID, FNC_KEY)
```

### 3.4 TB_PAY_STLM_MTHD 테이블

워크스페이스 결제 수단(빌링키) 정보를 관리하는 테이블.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 결제 수단 식별자 |
| `WKSPC_ID` | `BIGINT` | `FK(TB_COMM_WKSPC.ID) ON DELETE CASCADE, NOT NULL` | - | 워크스페이스 FK |
| `PG_PRVDR_CD` | `VARCHAR(50)` | `NOT NULL` | - | PG사 코드 (`TOSS`, `KCP`, `NICE`) |
| `BILNG_KEY_ENCPT` | `VARCHAR(500)` | `NOT NULL` | - | 빌링키 (AES-256 암호화) |
| `CSTMR_KEY` | `VARCHAR(255)` | `NOT NULL` | - | PG사 고객 식별자 |
| `TYPE_CD` | `VARCHAR(20)` | `NOT NULL` | `'CARD'` | 결제 수단 유형 |
| `CARD_LAST4` | `VARCHAR(4)` | - | NULL | 카드 마지막 4자리 |
| `CARD_BRND_NM` | `VARCHAR(30)` | - | NULL | 카드 브랜드 (VISA, MC, 삼성 등) |
| `CARD_EXPRY_MM` | `INTEGER` | - | NULL | 카드 만료 월 |
| `CARD_EXPRY_YR` | `INTEGER` | - | NULL | 카드 만료 년 |
| `DFLT_YN` | `CHAR(1)` | `NOT NULL` | `'N'` | 기본 결제 수단 여부 (`Y`/`N`) |
| `STTS_CD` | `VARCHAR(20)` | `NOT NULL` | `'ACTIVE'` | 상태 코드 |
| `DEL_DT` | `TIMESTAMPTZ` | - | NULL | Soft Delete 일시 |
| `CRTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 생성자 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 생성 일시 |
| `MDFR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 수정자 |
| `MDFCN_DT` | `TIMESTAMPTZ` | - | NULL | 수정 일시 |

**인덱스**:
```sql
CREATE INDEX idx_tb_pay_stlm_mthd_wkspc ON app.TB_PAY_STLM_MTHD(WKSPC_ID, STTS_CD);
```

**Enum 값**:

| 코드 유형 | 코드 | 설명 |
|-----------|------|------|
| `PG_PROVIDER` | `TOSS` | 토스페이먼츠 |
| | `KCP` | NHN KCP |
| | `NICE` | 나이스페이 |
| `PAYMENT_METHOD_TYPE` | `CARD` | 신용/체크카드 |
| `PAYMENT_METHOD_STATUS` | `ACTIVE` | 사용 가능 |
| | `EXPIRED` | 만료 |
| | `FAILED` | 사용 불가 |

### 3.5 TB_PAY_SBSC 테이블

워크스페이스 단위 구독 정보를 관리하는 핵심 테이블. 하나의 워크스페이스는 하나의 활성 구독만 가질 수 있다.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 구독 식별자 |
| `WKSPC_ID` | `BIGINT` | `FK(TB_COMM_WKSPC.ID) ON DELETE CASCADE, NOT NULL` | - | 워크스페이스 FK |
| `PLAN_ID` | `BIGINT` | `FK(TB_PAY_PLAN.ID), NOT NULL` | - | 플랜 FK |
| `STLM_MTHD_ID` | `BIGINT` | `FK(TB_PAY_STLM_MTHD.ID)` | NULL | 결제 수단 FK |
| `STTS_CD` | `VARCHAR(20)` | `NOT NULL` | `'ACTIVE'` | 구독 상태 |
| `CRNT_PRD_BGNG_DT` | `TIMESTAMPTZ` | `NOT NULL` | - | 현재 구독 기간 시작일 |
| `CRNT_PRD_END_DT` | `TIMESTAMPTZ` | `NOT NULL` | - | 현재 구독 기간 종료일 |
| `TRIAL_BGNG_DT` | `TIMESTAMPTZ` | - | NULL | 체험 시작일 |
| `TRIAL_END_DT` | `TIMESTAMPTZ` | - | NULL | 체험 종료일 |
| `BILNG_STDR_DAY` | `INTEGER` | - | NULL | 매월 결제일 (1-28) |
| `PRD_END_CNCL_YN` | `CHAR(1)` | `NOT NULL` | `'N'` | 기간 종료 시 해지 여부 (`Y`/`N`) |
| `CNCL_DT` | `TIMESTAMPTZ` | - | NULL | 해지 일시 |
| `PAUS_DT` | `TIMESTAMPTZ` | - | NULL | 일시정지 일시 |
| `MTDT` | `JSONB` | - | `'{}'` | 추가 메타데이터 |
| `CRTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 생성자 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 생성 일시 |
| `MDFR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 수정자 |
| `MDFCN_DT` | `TIMESTAMPTZ` | - | NULL | 수정 일시 |

**인덱스**:
```sql
CREATE INDEX idx_tb_pay_sbsc_wkspc ON app.TB_PAY_SBSC(WKSPC_ID, STTS_CD);
CREATE INDEX idx_tb_pay_sbsc_prd_end ON app.TB_PAY_SBSC(CRNT_PRD_END_DT);
CREATE INDEX idx_tb_pay_sbsc_stts ON app.TB_PAY_SBSC(STTS_CD);
```

**구독 상태 (SUBSCRIPTION_STATUS)**:

| 코드 | 한글명 | 설명 |
|------|--------|------|
| `TRIALING` | 체험 중 | 무료 체험 기간 |
| `ACTIVE` | 활성 | 정상 구독 중 |
| `PAST_DUE` | 결제 지연 | 결제 실패, 재시도 중 |
| `PAUSED` | 일시정지 | 사용자 요청에 의한 일시정지 |
| `SUSPENDED` | 정지 | 연속 결제 실패로 정지 |
| `CANCELED` | 해지 | 구독 해지 완료 |

### 3.6 TH_PAY_SBSC 테이블

구독 변경 이력을 관리하는 테이블.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 이력 식별자 |
| `SBSC_ID` | `BIGINT` | `FK(TB_PAY_SBSC.ID), NOT NULL` | - | 구독 FK |
| `PRVS_PLAN_ID` | `BIGINT` | `FK(TB_PAY_PLAN.ID)` | NULL | 이전 플랜 FK |
| `NEW_PLAN_ID` | `BIGINT` | `FK(TB_PAY_PLAN.ID)` | NULL | 신규 플랜 FK |
| `CHG_TYPE_CD` | `VARCHAR(30)` | `NOT NULL` | - | 변경 유형 |
| `EFCTV_DT` | `TIMESTAMPTZ` | `NOT NULL` | - | 적용 일시 |
| `PRTN_AMT` | `BIGINT` | - | NULL | 비례 배분 금액 |
| `NOTE_CN` | `VARCHAR(2000)` | - | NULL | 변경 사유 |
| `CRTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 생성자 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 생성 일시 |
| `MDFR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 수정자 |
| `MDFCN_DT` | `TIMESTAMPTZ` | - | NULL | 수정 일시 |

**변경 유형 (CHANGE_TYPE)**:

| 코드 | 설명 |
|------|------|
| `UPGRADE` | 상위 플랜으로 변경 |
| `DOWNGRADE` | 하위 플랜으로 변경 |
| `CANCEL` | 구독 해지 |
| `REACTIVATE` | 구독 재활성화 |
| `PAUSE` | 구독 일시정지 |
| `RESUME` | 구독 재개 |

### 3.7 TB_PAY_INVC 테이블

청구서 정보를 관리하는 테이블. 구독 주기마다 자동 생성된다.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 청구서 식별자 |
| `WKSPC_ID` | `BIGINT` | `FK(TB_COMM_WKSPC.ID), NOT NULL` | - | 워크스페이스 FK |
| `SBSC_ID` | `BIGINT` | `FK(TB_PAY_SBSC.ID)` | NULL | 구독 FK |
| `INVC_NO` | `VARCHAR(50)` | `UNIQUE NOT NULL` | - | 청구서 번호 (INV-YYYYMMDD-XXXX) |
| `STTS_CD` | `VARCHAR(20)` | `NOT NULL` | `'DRAFT'` | 청구서 상태 |
| `PRD_BGNG_DT` | `TIMESTAMPTZ` | `NOT NULL` | - | 청구 기간 시작 |
| `PRD_END_DT` | `TIMESTAMPTZ` | `NOT NULL` | - | 청구 기간 종료 |
| `STOT_AMT` | `BIGINT` | `NOT NULL` | - | 소계 (원 단위) |
| `TX_AMT` | `BIGINT` | `NOT NULL` | `0` | 세금 (부가세 10%) |
| `DSCNT_AMT` | `BIGINT` | `NOT NULL` | `0` | 할인 금액 |
| `TOT_AMT` | `BIGINT` | `NOT NULL` | - | 총액 |
| `PAY_AMT` | `BIGINT` | `NOT NULL` | `0` | 결제 완료 금액 |
| `UNPAY_AMT` | `BIGINT` | `NOT NULL` | - | 미결제 금액 |
| `CRNC_CD` | `VARCHAR(3)` | `NOT NULL` | `'KRW'` | 통화 코드 |
| `STLM_DELN_DT` | `TIMESTAMPTZ` | - | NULL | 결제 마감일 |
| `STLM_DT` | `TIMESTAMPTZ` | - | NULL | 결제 완료 일시 |
| `CRTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 생성자 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 생성 일시 |
| `MDFR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 수정자 |
| `MDFCN_DT` | `TIMESTAMPTZ` | - | NULL | 수정 일시 |

**인덱스**:
```sql
CREATE UNIQUE INDEX idx_tb_pay_invc_no ON app.TB_PAY_INVC(INVC_NO);
CREATE INDEX idx_tb_pay_invc_wkspc ON app.TB_PAY_INVC(WKSPC_ID, STTS_CD);
CREATE INDEX idx_tb_pay_invc_sbsc ON app.TB_PAY_INVC(SBSC_ID);
CREATE INDEX idx_tb_pay_invc_deln ON app.TB_PAY_INVC(STLM_DELN_DT, STTS_CD);
```

**청구서 상태 (INVOICE_STATUS)**:

| 코드 | 한글명 | 설명 |
|------|--------|------|
| `DRAFT` | 임시 | 생성 직후, 아직 확정되지 않음 |
| `OPEN` | 발행 | 결제 대기 중 |
| `PAID` | 결제 완료 | 정상 결제 완료 |
| `VOID` | 무효 | 청구서 무효 처리 |
| `UNCOLLECTIBLE` | 미수 | 결제 불가 (dunning 실패) |

### 3.8 TB_PAY_INVC_ARTCL 테이블

청구서 항목 상세를 관리하는 테이블.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 항목 식별자 |
| `INVC_ID` | `BIGINT` | `FK(TB_PAY_INVC.ID) ON DELETE CASCADE, NOT NULL` | - | 청구서 FK |
| `ARTCL_DC` | `VARCHAR(500)` | `NOT NULL` | - | 항목 설명 |
| `ARTCL_AMT` | `BIGINT` | `NOT NULL` | - | 금액 (원 단위) |
| `QTY` | `INTEGER` | `NOT NULL` | `1` | 수량 |
| `UNIT_PRC` | `BIGINT` | - | NULL | 단가 |
| `TYPE_CD` | `VARCHAR(30)` | `NOT NULL` | - | 항목 유형 |
| `PLAN_ID` | `BIGINT` | `FK(TB_PAY_PLAN.ID)` | NULL | 관련 플랜 FK |
| `PRD_BGNG_DT` | `TIMESTAMPTZ` | - | NULL | 적용 기간 시작 |
| `PRD_END_DT` | `TIMESTAMPTZ` | - | NULL | 적용 기간 종료 |
| `PRTN_YN` | `CHAR(1)` | `NOT NULL` | `'N'` | 비례 배분 항목 여부 (`Y`/`N`) |
| `CRTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 생성자 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 생성 일시 |
| `MDFR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 수정자 |
| `MDFCN_DT` | `TIMESTAMPTZ` | - | NULL | 수정 일시 |

**항목 유형 (LINE_ITEM_TYPE)**:

| 코드 | 설명 |
|------|------|
| `SUBSCRIPTION` | 구독료 |
| `PRORATION_CREDIT` | 비례 배분 크레딧 (마이너스) |
| `PRORATION_DEBIT` | 비례 배분 추가 청구 |
| `DISCOUNT` | 할인 |
| `TAX` | 세금 |

### 3.9 TB_PAY_STLM 테이블

실제 결제 시도/완료 정보를 관리하는 테이블.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 결제 식별자 |
| `INVC_ID` | `BIGINT` | `FK(TB_PAY_INVC.ID), NOT NULL` | - | 청구서 FK |
| `STLM_MTHD_ID` | `BIGINT` | `FK(TB_PAY_STLM_MTHD.ID)` | NULL | 결제 수단 FK |
| `STLM_AMT` | `BIGINT` | `NOT NULL` | - | 결제 금액 (원 단위) |
| `CRNC_CD` | `VARCHAR(3)` | `NOT NULL` | `'KRW'` | 통화 코드 |
| `STTS_CD` | `VARCHAR(20)` | `NOT NULL` | `'PENDING'` | 결제 상태 |
| `PG_PRVDR_CD` | `VARCHAR(50)` | - | NULL | PG사 코드 |
| `PG_STLM_KEY` | `VARCHAR(255)` | - | NULL | PG사 결제 키 |
| `PG_ORDR_NO` | `VARCHAR(255)` | - | NULL | PG사 주문 번호 |
| `PG_RSPNS_CD` | `VARCHAR(20)` | - | NULL | PG사 응답 코드 |
| `PG_RSPNS_MSG` | `VARCHAR(2000)` | - | NULL | PG사 응답 메시지 |
| `PG_ORGNL_RSPNS` | `JSONB` | - | NULL | PG사 원본 응답 |
| `ATMT_CNT` | `INTEGER` | `NOT NULL` | `1` | 시도 횟수 |
| `IDMPTN_KEY` | `VARCHAR(255)` | `UNIQUE NOT NULL` | - | 멱등성 키 |
| `FAIL_DT` | `TIMESTAMPTZ` | - | NULL | 실패 일시 |
| `SCS_DT` | `TIMESTAMPTZ` | - | NULL | 성공 일시 |
| `RFND_DT` | `TIMESTAMPTZ` | - | NULL | 환불 일시 |
| `RFND_AMT` | `BIGINT` | - | `0` | 환불 금액 |
| `CRTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 생성자 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 생성 일시 |
| `MDFR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 수정자 |
| `MDFCN_DT` | `TIMESTAMPTZ` | - | NULL | 수정 일시 |

**인덱스**:
```sql
CREATE UNIQUE INDEX idx_tb_pay_stlm_idmptn ON app.TB_PAY_STLM(IDMPTN_KEY);
CREATE INDEX idx_tb_pay_stlm_invc ON app.TB_PAY_STLM(INVC_ID);
CREATE INDEX idx_tb_pay_stlm_pg_key ON app.TB_PAY_STLM(PG_STLM_KEY);
CREATE INDEX idx_tb_pay_stlm_stts ON app.TB_PAY_STLM(STTS_CD);
```

**결제 상태 (PAYMENT_STATUS)**:

| 코드 | 설명 |
|------|------|
| `PENDING` | 결제 대기 |
| `SUCCEEDED` | 결제 성공 |
| `FAILED` | 결제 실패 |
| `REFUNDED` | 전액 환불 |
| `PARTIAL_REFUNDED` | 부분 환불 |

### 3.10 TL_PAY_BILNG_EVNT 테이블

모든 결제 관련 이벤트를 불변(Immutable)으로 기록하는 감사 로그 테이블.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 이벤트 식별자 |
| `EVNT_TYPE_CD` | `VARCHAR(100)` | `NOT NULL` | - | 이벤트 유형 |
| `ENTTY_TYPE_CD` | `VARCHAR(50)` | `NOT NULL` | - | 대상 엔티티 유형 |
| `ENTTY_ID` | `BIGINT` | `NOT NULL` | - | 대상 엔티티 ID |
| `WKSPC_ID` | `BIGINT` | `FK(TB_COMM_WKSPC.ID)` | NULL | 관련 워크스페이스 FK |
| `USER_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 작업 수행자 FK (감사 추적) |
| `EVNT_DATA` | `JSONB` | `NOT NULL` | - | 이벤트 상세 데이터 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 생성 일시 |

**인덱스**:
```sql
CREATE INDEX idx_tl_pay_bilng_evnt_type ON app.TL_PAY_BILNG_EVNT(EVNT_TYPE_CD);
CREATE INDEX idx_tl_pay_bilng_evnt_entty ON app.TL_PAY_BILNG_EVNT(ENTTY_TYPE_CD, ENTTY_ID);
CREATE INDEX idx_tl_pay_bilng_evnt_wkspc ON app.TL_PAY_BILNG_EVNT(WKSPC_ID);
CREATE INDEX idx_tl_pay_bilng_evnt_user ON app.TL_PAY_BILNG_EVNT(USER_ID);
```

**이벤트 유형 예시**:

| EVNT_TYPE_CD | ENTTY_TYPE_CD | 설명 |
|-----------|-------------|------|
| `subscription.created` | `subscription` | 구독 생성 |
| `subscription.upgraded` | `subscription` | 플랜 업그레이드 |
| `subscription.canceled` | `subscription` | 구독 해지 |
| `invoice.created` | `invoice` | 청구서 생성 |
| `invoice.paid` | `invoice` | 청구서 결제 완료 |
| `payment.succeeded` | `payment` | 결제 성공 |
| `payment.failed` | `payment` | 결제 실패 |
| `payment.refunded` | `payment` | 결제 환불 |
| `credit.allocated` | `credit_balance` | 크레딧 할당 (기간 시작) |
| `credit.deducted` | `credit_balance` | 크레딧 차감 |
| `credit.exhausted` | `credit_balance` | 크레딧 소진 |
| `credit.adjusted` | `credit_balance` | 크레딧 수동 조정 |
| `credit.expired` | `credit_balance` | 크레딧 만료 (기간 종료) |
| `credit.plan_changed` | `credit_balance` | 플랜 변경에 따른 크레딧 재조정 |

### 3.11 TL_PAY_WBHK_EVNT 테이블

PG사로부터 수신한 웹훅 이벤트를 기록하는 테이블 (멱등성 보장).

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 웹훅 식별자 |
| `PRVDR_CD` | `VARCHAR(50)` | `NOT NULL` | - | PG사 코드 |
| `EXTRL_EVNT_ID` | `VARCHAR(255)` | `NOT NULL` | - | PG사 이벤트 고유 ID |
| `EVNT_TYPE_CD` | `VARCHAR(100)` | `NOT NULL` | - | 이벤트 유형 |
| `PYLD` | `JSONB` | `NOT NULL` | - | 원본 페이로드 |
| `STTS_CD` | `VARCHAR(20)` | `NOT NULL` | `'RECEIVED'` | 처리 상태 |
| `PROC_DT` | `TIMESTAMPTZ` | - | NULL | 처리 완료 일시 |
| `ERR_MSG_CN` | `VARCHAR(2000)` | - | NULL | 에러 메시지 |
| `RTRY_CNT` | `INTEGER` | `NOT NULL` | `0` | 처리 재시도 횟수 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 수신 일시 |

**제약조건**:
```sql
CONSTRAINT uq_tl_pay_wbhk_evnt_prvdr UNIQUE (PRVDR_CD, EXTRL_EVNT_ID)
```

### 3.12 TH_PAY_STLM_RTRY 테이블

결제 실패 시 재시도(Dunning) 이력을 관리하는 테이블.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 시도 식별자 |
| `SBSC_ID` | `BIGINT` | `FK(TB_PAY_SBSC.ID), NOT NULL` | - | 구독 FK |
| `INVC_ID` | `BIGINT` | `FK(TB_PAY_INVC.ID), NOT NULL` | - | 청구서 FK |
| `ATMT_SN` | `INTEGER` | `NOT NULL` | - | 시도 번호 (1, 2, 3, 4) |
| `TYPE_CD` | `VARCHAR(30)` | `NOT NULL` | - | 시도 유형 |
| `STTS_CD` | `VARCHAR(20)` | `NOT NULL` | `'SCHEDULED'` | 상태 |
| `SCHDL_DT` | `TIMESTAMPTZ` | `NOT NULL` | - | 예정 일시 |
| `EXEC_DT` | `TIMESTAMPTZ` | - | NULL | 실행 일시 |
| `NXT_ATMT_DT` | `TIMESTAMPTZ` | - | NULL | 다음 시도 예정 일시 |
| `PG_RSPNS_CD` | `VARCHAR(20)` | - | NULL | PG사 응답 코드 |
| `CRTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 생성자 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 생성 일시 |
| `MDFR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 수정자 |
| `MDFCN_DT` | `TIMESTAMPTZ` | - | NULL | 수정 일시 |

**인덱스**:
```sql
CREATE INDEX idx_th_pay_stlm_rtry_schdl ON app.TH_PAY_STLM_RTRY(SCHDL_DT, STTS_CD);
CREATE INDEX idx_th_pay_stlm_rtry_sbsc ON app.TH_PAY_STLM_RTRY(SBSC_ID);
```

**시도 유형 (DUNNING_TYPE)**:

| 코드 | 설명 |
|------|------|
| `AUTO_RETRY` | 자동 재시도 (알림 없음) |
| `RETRY_WITH_EMAIL` | 재시도 + 이메일 알림 |
| `RETRY_WITH_SMS` | 재시도 + SMS 알림 |
| `FINAL_NOTICE` | 최종 알림 (서비스 정지 예고) |

### 3.13 TB_PAY_CRDT_BLNC 테이블

워크스페이스 멤버별 빌링 주기 단위 크레딧 잔액을 관리하는 테이블.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 크레딧 잔액 식별자 |
| `WKSPC_ID` | `BIGINT` | `FK(TB_COMM_WKSPC.ID) ON DELETE CASCADE, NOT NULL` | - | 워크스페이스 FK |
| `USER_ID` | `BIGINT` | `FK(TB_COMM_USER.ID) ON DELETE CASCADE, NOT NULL` | - | 사용자 FK |
| `SBSC_ID` | `BIGINT` | `FK(TB_PAY_SBSC.ID), NOT NULL` | - | 구독 FK |
| `PRD_BGNG_DT` | `TIMESTAMPTZ` | `NOT NULL` | - | 빌링 기간 시작일 |
| `PRD_END_DT` | `TIMESTAMPTZ` | `NOT NULL` | - | 빌링 기간 종료일 |
| `ALOT_QTY` | `INTEGER` | `NOT NULL` | - | 할당 크레딧 수량 |
| `USED_QTY` | `INTEGER` | `NOT NULL` | `0` | 사용 크레딧 수량 |
| `RMNN_QTY` | `INTEGER` | `NOT NULL` | - | 잔여 크레딧 수량 |
| `STTS_CD` | `VARCHAR(20)` | `NOT NULL` | `'ACTIVE'` | 크레딧 상태 코드 |
| `CRTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 생성자 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 생성 일시 |
| `MDFR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 수정자 |
| `MDFCN_DT` | `TIMESTAMPTZ` | - | NULL | 수정 일시 |

**제약조건**:
```sql
CONSTRAINT uq_tb_pay_crdt_blnc_prd UNIQUE (WKSPC_ID, USER_ID, PRD_BGNG_DT)
```

**인덱스**:
```sql
CREATE INDEX idx_tb_pay_crdt_blnc_ws_user ON app.TB_PAY_CRDT_BLNC(WKSPC_ID, USER_ID, STTS_CD);
CREATE INDEX idx_tb_pay_crdt_blnc_prd ON app.TB_PAY_CRDT_BLNC(PRD_END_DT, STTS_CD);
CREATE INDEX idx_tb_pay_crdt_blnc_sbsc ON app.TB_PAY_CRDT_BLNC(SBSC_ID);
```

**크레딧 상태 (CREDIT_BALANCE_STATUS)**:

| 코드 | 한글명 | 설명 |
|------|--------|------|
| `ACTIVE` | 활성 | 현재 빌링 기간, 크레딧 사용 가능 |
| `EXHAUSTED` | 소진 | 크레딧 전량 사용 완료 (RMNN_QTY = 0) |
| `EXPIRED` | 만료 | 빌링 기간 종료로 만료 |

### 3.14 TL_PAY_CRDT_TRNS 테이블

모든 크레딧 변동을 불변(Immutable)으로 기록하는 감사 로그 테이블.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 거래 식별자 |
| `CRDT_BLNC_ID` | `BIGINT` | `FK(TB_PAY_CRDT_BLNC.ID), NOT NULL` | - | 크레딧 잔액 FK |
| `WKSPC_ID` | `BIGINT` | `FK(TB_COMM_WKSPC.ID), NOT NULL` | - | 워크스페이스 FK |
| `USER_ID` | `BIGINT` | `FK(TB_COMM_USER.ID), NOT NULL` | - | 사용자 FK |
| `TRNS_TYPE_CD` | `VARCHAR(20)` | `NOT NULL` | - | 거래 유형 코드 |
| `TRNS_QTY` | `INTEGER` | `NOT NULL` | - | 거래 수량 (차감 시 음수) |
| `BLNC_BFR_QTY` | `INTEGER` | `NOT NULL` | - | 거래 전 잔액 |
| `BLNC_AFT_QTY` | `INTEGER` | `NOT NULL` | - | 거래 후 잔액 |
| `RFRNC_TYPE_CD` | `VARCHAR(50)` | - | NULL | 참조 엔티티 유형 (예: `message`, `api_call`) |
| `RFRNC_ID` | `BIGINT` | - | NULL | 참조 엔티티 ID |
| `TRNS_DC` | `VARCHAR(500)` | - | NULL | 거래 설명 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 생성 일시 |

**인덱스**:
```sql
CREATE INDEX idx_tl_pay_crdt_trns_blnc ON app.TL_PAY_CRDT_TRNS(CRDT_BLNC_ID);
CREATE INDEX idx_tl_pay_crdt_trns_ws_user ON app.TL_PAY_CRDT_TRNS(WKSPC_ID, USER_ID);
CREATE INDEX idx_tl_pay_crdt_trns_type ON app.TL_PAY_CRDT_TRNS(TRNS_TYPE_CD);
CREATE INDEX idx_tl_pay_crdt_trns_crt ON app.TL_PAY_CRDT_TRNS(CRT_DT);
```

**거래 유형 (CREDIT_TRANSACTION_TYPE)**:

| 코드 | 한글명 | 설명 |
|------|--------|------|
| `ALLOCATION` | 할당 | 빌링 기간 시작 시 초기 크레딧 할당 |
| `DEDUCTION` | 차감 | 서비스 사용으로 인한 크레딧 차감 |
| `ADJUSTMENT` | 조정 | 관리자에 의한 수동 크레딧 조정 |
| `PLAN_CHANGE` | 플랜변경 | 플랜 변경에 따른 크레딧 재조정 |

### 3.15 DDL 전문

```sql
-- ============================================
-- 1. TB_PAY_PLAN 테이블
-- ============================================
CREATE TABLE app.TB_PAY_PLAN (
    ID                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    PLAN_NM           VARCHAR(100)    NOT NULL,
    PLAN_DC           VARCHAR(500),
    BILNG_INTRVL_CD   VARCHAR(20)     NOT NULL,
    INTRVL_CNT        INTEGER         NOT NULL DEFAULT 1,
    PLAN_AMT          BIGINT          NOT NULL,
    CRNC_CD           VARCHAR(3)      NOT NULL DEFAULT 'KRW',
    TRIAL_DAY_CNT     INTEGER         NOT NULL DEFAULT 0,
    SORT_SN           INTEGER         NOT NULL DEFAULT 0,
    ACTV_YN           CHAR(1)         NOT NULL DEFAULT 'Y',
    MTDT              JSONB           DEFAULT '{}',
    CRTR_ID           BIGINT          REFERENCES app.TB_COMM_USER(ID),
    CRT_DT            TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    MDFR_ID           BIGINT          REFERENCES app.TB_COMM_USER(ID),
    MDFCN_DT          TIMESTAMPTZ
);

CREATE INDEX idx_tb_pay_plan_actv ON app.TB_PAY_PLAN(ACTV_YN, SORT_SN);

-- ============================================
-- 2. TB_PAY_PLAN_FNC 테이블
-- ============================================
CREATE TABLE app.TB_PAY_PLAN_FNC (
    ID                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    PLAN_ID           BIGINT          NOT NULL REFERENCES app.TB_PAY_PLAN(ID) ON DELETE CASCADE,
    FNC_KEY           VARCHAR(100)    NOT NULL,
    FNC_VL            VARCHAR(255)    NOT NULL,
    FNC_DC            VARCHAR(500),
    CRTR_ID           BIGINT          REFERENCES app.TB_COMM_USER(ID),
    CRT_DT            TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    MDFR_ID           BIGINT          REFERENCES app.TB_COMM_USER(ID),
    MDFCN_DT          TIMESTAMPTZ,
    CONSTRAINT uq_tb_pay_plan_fnc_key UNIQUE (PLAN_ID, FNC_KEY)
);

-- ============================================
-- 3. TB_PAY_STLM_MTHD 테이블
-- ============================================
CREATE TABLE app.TB_PAY_STLM_MTHD (
    ID                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    WKSPC_ID          BIGINT          NOT NULL REFERENCES app.TB_COMM_WKSPC(ID) ON DELETE CASCADE,
    PG_PRVDR_CD       VARCHAR(50)     NOT NULL,
    BILNG_KEY_ENCPT   VARCHAR(500)    NOT NULL,
    CSTMR_KEY         VARCHAR(255)    NOT NULL,
    TYPE_CD           VARCHAR(20)     NOT NULL DEFAULT 'CARD',
    CARD_LAST4        VARCHAR(4),
    CARD_BRND_NM      VARCHAR(30),
    CARD_EXPRY_MM     INTEGER,
    CARD_EXPRY_YR     INTEGER,
    DFLT_YN           CHAR(1)         NOT NULL DEFAULT 'N',
    STTS_CD           VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    DEL_DT            TIMESTAMPTZ,
    CRTR_ID           BIGINT          REFERENCES app.TB_COMM_USER(ID),
    CRT_DT            TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    MDFR_ID           BIGINT          REFERENCES app.TB_COMM_USER(ID),
    MDFCN_DT          TIMESTAMPTZ
);

CREATE INDEX idx_tb_pay_stlm_mthd_wkspc ON app.TB_PAY_STLM_MTHD(WKSPC_ID, STTS_CD);

-- ============================================
-- 4. TB_PAY_SBSC 테이블
-- ============================================
CREATE TABLE app.TB_PAY_SBSC (
    ID                    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    WKSPC_ID              BIGINT          NOT NULL REFERENCES app.TB_COMM_WKSPC(ID) ON DELETE CASCADE,
    PLAN_ID               BIGINT          NOT NULL REFERENCES app.TB_PAY_PLAN(ID),
    STLM_MTHD_ID         BIGINT          REFERENCES app.TB_PAY_STLM_MTHD(ID),
    STTS_CD               VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    CRNT_PRD_BGNG_DT      TIMESTAMPTZ     NOT NULL,
    CRNT_PRD_END_DT       TIMESTAMPTZ     NOT NULL,
    TRIAL_BGNG_DT         TIMESTAMPTZ,
    TRIAL_END_DT          TIMESTAMPTZ,
    BILNG_STDR_DAY        INTEGER,
    PRD_END_CNCL_YN       CHAR(1)         NOT NULL DEFAULT 'N',
    CNCL_DT               TIMESTAMPTZ,
    PAUS_DT               TIMESTAMPTZ,
    MTDT                  JSONB           DEFAULT '{}',
    CRTR_ID               BIGINT          REFERENCES app.TB_COMM_USER(ID),
    CRT_DT                TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    MDFR_ID               BIGINT          REFERENCES app.TB_COMM_USER(ID),
    MDFCN_DT              TIMESTAMPTZ
);

CREATE INDEX idx_tb_pay_sbsc_wkspc ON app.TB_PAY_SBSC(WKSPC_ID, STTS_CD);
CREATE INDEX idx_tb_pay_sbsc_prd_end ON app.TB_PAY_SBSC(CRNT_PRD_END_DT);
CREATE INDEX idx_tb_pay_sbsc_stts ON app.TB_PAY_SBSC(STTS_CD);

-- ============================================
-- 5. TH_PAY_SBSC 테이블
-- ============================================
CREATE TABLE app.TH_PAY_SBSC (
    ID                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    SBSC_ID           BIGINT          NOT NULL REFERENCES app.TB_PAY_SBSC(ID),
    PRVS_PLAN_ID      BIGINT          REFERENCES app.TB_PAY_PLAN(ID),
    NEW_PLAN_ID       BIGINT          REFERENCES app.TB_PAY_PLAN(ID),
    CHG_TYPE_CD       VARCHAR(30)     NOT NULL,
    EFCTV_DT          TIMESTAMPTZ     NOT NULL,
    PRTN_AMT          BIGINT,
    NOTE_CN           VARCHAR(2000),
    CRTR_ID           BIGINT          REFERENCES app.TB_COMM_USER(ID),
    CRT_DT            TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    MDFR_ID           BIGINT          REFERENCES app.TB_COMM_USER(ID),
    MDFCN_DT          TIMESTAMPTZ
);

CREATE INDEX idx_th_pay_sbsc_sbsc ON app.TH_PAY_SBSC(SBSC_ID);

-- ============================================
-- 6. TB_PAY_INVC 테이블
-- ============================================
CREATE TABLE app.TB_PAY_INVC (
    ID                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    WKSPC_ID          BIGINT          NOT NULL REFERENCES app.TB_COMM_WKSPC(ID),
    SBSC_ID           BIGINT          REFERENCES app.TB_PAY_SBSC(ID),
    INVC_NO           VARCHAR(50)     NOT NULL,
    STTS_CD           VARCHAR(20)     NOT NULL DEFAULT 'DRAFT',
    PRD_BGNG_DT       TIMESTAMPTZ     NOT NULL,
    PRD_END_DT        TIMESTAMPTZ     NOT NULL,
    STOT_AMT          BIGINT          NOT NULL,
    TX_AMT            BIGINT          NOT NULL DEFAULT 0,
    DSCNT_AMT         BIGINT          NOT NULL DEFAULT 0,
    TOT_AMT           BIGINT          NOT NULL,
    PAY_AMT           BIGINT          NOT NULL DEFAULT 0,
    UNPAY_AMT         BIGINT          NOT NULL,
    CRNC_CD           VARCHAR(3)      NOT NULL DEFAULT 'KRW',
    STLM_DELN_DT     TIMESTAMPTZ,
    STLM_DT          TIMESTAMPTZ,
    CRTR_ID           BIGINT          REFERENCES app.TB_COMM_USER(ID),
    CRT_DT            TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    MDFR_ID           BIGINT          REFERENCES app.TB_COMM_USER(ID),
    MDFCN_DT          TIMESTAMPTZ
);

CREATE UNIQUE INDEX idx_tb_pay_invc_no ON app.TB_PAY_INVC(INVC_NO);
CREATE INDEX idx_tb_pay_invc_wkspc ON app.TB_PAY_INVC(WKSPC_ID, STTS_CD);
CREATE INDEX idx_tb_pay_invc_sbsc ON app.TB_PAY_INVC(SBSC_ID);
CREATE INDEX idx_tb_pay_invc_deln ON app.TB_PAY_INVC(STLM_DELN_DT, STTS_CD);

-- ============================================
-- 7. TB_PAY_INVC_ARTCL 테이블
-- ============================================
CREATE TABLE app.TB_PAY_INVC_ARTCL (
    ID                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    INVC_ID           BIGINT          NOT NULL REFERENCES app.TB_PAY_INVC(ID) ON DELETE CASCADE,
    ARTCL_DC          VARCHAR(500)    NOT NULL,
    ARTCL_AMT         BIGINT          NOT NULL,
    QTY               INTEGER         NOT NULL DEFAULT 1,
    UNIT_PRC          BIGINT,
    TYPE_CD           VARCHAR(30)     NOT NULL,
    PLAN_ID           BIGINT          REFERENCES app.TB_PAY_PLAN(ID),
    PRD_BGNG_DT       TIMESTAMPTZ,
    PRD_END_DT        TIMESTAMPTZ,
    PRTN_YN           CHAR(1)         NOT NULL DEFAULT 'N',
    CRTR_ID           BIGINT          REFERENCES app.TB_COMM_USER(ID),
    CRT_DT            TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    MDFR_ID           BIGINT          REFERENCES app.TB_COMM_USER(ID),
    MDFCN_DT          TIMESTAMPTZ
);

CREATE INDEX idx_tb_pay_invc_artcl_invc ON app.TB_PAY_INVC_ARTCL(INVC_ID);

-- ============================================
-- 8. TB_PAY_STLM 테이블
-- ============================================
CREATE TABLE app.TB_PAY_STLM (
    ID                    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    INVC_ID               BIGINT          NOT NULL REFERENCES app.TB_PAY_INVC(ID),
    STLM_MTHD_ID         BIGINT          REFERENCES app.TB_PAY_STLM_MTHD(ID),
    STLM_AMT              BIGINT          NOT NULL,
    CRNC_CD               VARCHAR(3)      NOT NULL DEFAULT 'KRW',
    STTS_CD               VARCHAR(20)     NOT NULL DEFAULT 'PENDING',
    PG_PRVDR_CD           VARCHAR(50),
    PG_STLM_KEY           VARCHAR(255),
    PG_ORDR_NO            VARCHAR(255),
    PG_RSPNS_CD           VARCHAR(20),
    PG_RSPNS_MSG          VARCHAR(2000),
    PG_ORGNL_RSPNS        JSONB,
    ATMT_CNT              INTEGER         NOT NULL DEFAULT 1,
    IDMPTN_KEY            VARCHAR(255)    NOT NULL,
    FAIL_DT               TIMESTAMPTZ,
    SCS_DT                TIMESTAMPTZ,
    RFND_DT               TIMESTAMPTZ,
    RFND_AMT              BIGINT          DEFAULT 0,
    CRTR_ID               BIGINT          REFERENCES app.TB_COMM_USER(ID),
    CRT_DT                TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    MDFR_ID               BIGINT          REFERENCES app.TB_COMM_USER(ID),
    MDFCN_DT              TIMESTAMPTZ
);

CREATE UNIQUE INDEX idx_tb_pay_stlm_idmptn ON app.TB_PAY_STLM(IDMPTN_KEY);
CREATE INDEX idx_tb_pay_stlm_invc ON app.TB_PAY_STLM(INVC_ID);
CREATE INDEX idx_tb_pay_stlm_pg_key ON app.TB_PAY_STLM(PG_STLM_KEY);
CREATE INDEX idx_tb_pay_stlm_stts ON app.TB_PAY_STLM(STTS_CD);

-- ============================================
-- 9. TL_PAY_BILNG_EVNT 테이블
-- ============================================
CREATE TABLE app.TL_PAY_BILNG_EVNT (
    ID                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    EVNT_TYPE_CD      VARCHAR(100)    NOT NULL,
    ENTTY_TYPE_CD     VARCHAR(50)     NOT NULL,
    ENTTY_ID          BIGINT          NOT NULL,
    WKSPC_ID          BIGINT          REFERENCES app.TB_COMM_WKSPC(ID),
    USER_ID           BIGINT          REFERENCES app.TB_COMM_USER(ID),
    EVNT_DATA         JSONB           NOT NULL,
    CRT_DT            TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tl_pay_bilng_evnt_type ON app.TL_PAY_BILNG_EVNT(EVNT_TYPE_CD);
CREATE INDEX idx_tl_pay_bilng_evnt_entty ON app.TL_PAY_BILNG_EVNT(ENTTY_TYPE_CD, ENTTY_ID);
CREATE INDEX idx_tl_pay_bilng_evnt_wkspc ON app.TL_PAY_BILNG_EVNT(WKSPC_ID);
CREATE INDEX idx_tl_pay_bilng_evnt_user ON app.TL_PAY_BILNG_EVNT(USER_ID);

-- ============================================
-- 10. TL_PAY_WBHK_EVNT 테이블
-- ============================================
CREATE TABLE app.TL_PAY_WBHK_EVNT (
    ID                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    PRVDR_CD            VARCHAR(50)     NOT NULL,
    EXTRL_EVNT_ID       VARCHAR(255)    NOT NULL,
    EVNT_TYPE_CD        VARCHAR(100)    NOT NULL,
    PYLD                JSONB           NOT NULL,
    STTS_CD             VARCHAR(20)     NOT NULL DEFAULT 'RECEIVED',
    PROC_DT             TIMESTAMPTZ,
    ERR_MSG_CN          VARCHAR(2000),
    RTRY_CNT            INTEGER         NOT NULL DEFAULT 0,
    CRT_DT              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_tl_pay_wbhk_evnt_prvdr UNIQUE (PRVDR_CD, EXTRL_EVNT_ID)
);

-- ============================================
-- 11. TH_PAY_STLM_RTRY 테이블
-- ============================================
CREATE TABLE app.TH_PAY_STLM_RTRY (
    ID                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    SBSC_ID           BIGINT          NOT NULL REFERENCES app.TB_PAY_SBSC(ID),
    INVC_ID           BIGINT          NOT NULL REFERENCES app.TB_PAY_INVC(ID),
    ATMT_SN           INTEGER         NOT NULL,
    TYPE_CD           VARCHAR(30)     NOT NULL,
    STTS_CD           VARCHAR(20)     NOT NULL DEFAULT 'SCHEDULED',
    SCHDL_DT          TIMESTAMPTZ     NOT NULL,
    EXEC_DT           TIMESTAMPTZ,
    NXT_ATMT_DT       TIMESTAMPTZ,
    PG_RSPNS_CD       VARCHAR(20),
    CRTR_ID           BIGINT          REFERENCES app.TB_COMM_USER(ID),
    CRT_DT            TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    MDFR_ID           BIGINT          REFERENCES app.TB_COMM_USER(ID),
    MDFCN_DT          TIMESTAMPTZ
);

CREATE INDEX idx_th_pay_stlm_rtry_schdl ON app.TH_PAY_STLM_RTRY(SCHDL_DT, STTS_CD);
CREATE INDEX idx_th_pay_stlm_rtry_sbsc ON app.TH_PAY_STLM_RTRY(SBSC_ID);

-- ============================================
-- 12. TB_PAY_CRDT_BLNC 테이블
-- ============================================
CREATE TABLE app.TB_PAY_CRDT_BLNC (
    ID              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    WKSPC_ID        BIGINT          NOT NULL REFERENCES app.TB_COMM_WKSPC(ID) ON DELETE CASCADE,
    USER_ID         BIGINT          NOT NULL REFERENCES app.TB_COMM_USER(ID) ON DELETE CASCADE,
    SBSC_ID         BIGINT          NOT NULL REFERENCES app.TB_PAY_SBSC(ID),
    PRD_BGNG_DT     TIMESTAMPTZ     NOT NULL,
    PRD_END_DT      TIMESTAMPTZ     NOT NULL,
    ALOT_QTY        INTEGER         NOT NULL,
    USED_QTY        INTEGER         NOT NULL DEFAULT 0,
    RMNN_QTY        INTEGER         NOT NULL,
    STTS_CD         VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    CRTR_ID         BIGINT          REFERENCES app.TB_COMM_USER(ID),
    CRT_DT          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    MDFR_ID         BIGINT          REFERENCES app.TB_COMM_USER(ID),
    MDFCN_DT        TIMESTAMPTZ,
    CONSTRAINT uq_tb_pay_crdt_blnc_prd UNIQUE (WKSPC_ID, USER_ID, PRD_BGNG_DT)
);

CREATE INDEX idx_tb_pay_crdt_blnc_ws_user ON app.TB_PAY_CRDT_BLNC(WKSPC_ID, USER_ID, STTS_CD);
CREATE INDEX idx_tb_pay_crdt_blnc_prd ON app.TB_PAY_CRDT_BLNC(PRD_END_DT, STTS_CD);
CREATE INDEX idx_tb_pay_crdt_blnc_sbsc ON app.TB_PAY_CRDT_BLNC(SBSC_ID);

-- ============================================
-- 13. TL_PAY_CRDT_TRNS 테이블
-- ============================================
CREATE TABLE app.TL_PAY_CRDT_TRNS (
    ID              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    CRDT_BLNC_ID    BIGINT          NOT NULL REFERENCES app.TB_PAY_CRDT_BLNC(ID),
    WKSPC_ID        BIGINT          NOT NULL REFERENCES app.TB_COMM_WKSPC(ID),
    USER_ID         BIGINT          NOT NULL REFERENCES app.TB_COMM_USER(ID),
    TRNS_TYPE_CD    VARCHAR(20)     NOT NULL,
    TRNS_QTY        INTEGER         NOT NULL,
    BLNC_BFR_QTY    INTEGER         NOT NULL,
    BLNC_AFT_QTY    INTEGER         NOT NULL,
    RFRNC_TYPE_CD   VARCHAR(50),
    RFRNC_ID        BIGINT,
    TRNS_DC         VARCHAR(500),
    CRT_DT          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tl_pay_crdt_trns_blnc ON app.TL_PAY_CRDT_TRNS(CRDT_BLNC_ID);
CREATE INDEX idx_tl_pay_crdt_trns_ws_user ON app.TL_PAY_CRDT_TRNS(WKSPC_ID, USER_ID);
CREATE INDEX idx_tl_pay_crdt_trns_type ON app.TL_PAY_CRDT_TRNS(TRNS_TYPE_CD);
CREATE INDEX idx_tl_pay_crdt_trns_crt ON app.TL_PAY_CRDT_TRNS(CRT_DT);
```

### 3.16 Drizzle ORM 스키마 정의

```typescript
// lib/db/schema/billing.ts
import {
  pgSchema, bigint, varchar, char, integer,
  timestamp, jsonb, uniqueIndex, index
} from 'drizzle-orm/pg-core';
import { users } from './auth';
import { workspaces } from './workspace';

export const app = pgSchema('app');

// ---- TB_PAY_PLAN ----
export const plans = app.table('TB_PAY_PLAN', {
  id:               bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  planNm:           varchar('PLAN_NM', { length: 100 }).notNull(),
  planDc:           varchar('PLAN_DC', { length: 500 }),
  bilngIntrvlCd:    varchar('BILNG_INTRVL_CD', { length: 20 }).notNull(),
  intrvlCnt:        integer('INTRVL_CNT').notNull().default(1),
  planAmt:          bigint('PLAN_AMT', { mode: 'number' }).notNull(),
  crncCd:           varchar('CRNC_CD', { length: 3 }).notNull().default('KRW'),
  trialDayCnt:      integer('TRIAL_DAY_CNT').notNull().default(0),
  sortSn:           integer('SORT_SN').notNull().default(0),
  actvYn:           char('ACTV_YN', { length: 1 }).notNull().default('Y'),
  mtdt:             jsonb('MTDT').default('{}'),
  crtrId:           bigint('CRTR_ID', { mode: 'number' }),
  crtDt:            timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
  mdfrId:           bigint('MDFR_ID', { mode: 'number' }),
  mdfcnDt:          timestamp('MDFCN_DT', { withTimezone: true }),
}, (table) => [
  index('idx_tb_pay_plan_actv').on(table.actvYn, table.sortSn),
]);

// ---- TB_PAY_PLAN_FNC ----
export const planFeatures = app.table('TB_PAY_PLAN_FNC', {
  id:            bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  planId:        bigint('PLAN_ID', { mode: 'number' }).notNull().references(() => plans.id, { onDelete: 'cascade' }),
  fncKey:        varchar('FNC_KEY', { length: 100 }).notNull(),
  fncVl:         varchar('FNC_VL', { length: 255 }).notNull(),
  fncDc:         varchar('FNC_DC', { length: 500 }),
  crtrId:        bigint('CRTR_ID', { mode: 'number' }),
  crtDt:         timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
  mdfrId:        bigint('MDFR_ID', { mode: 'number' }),
  mdfcnDt:       timestamp('MDFCN_DT', { withTimezone: true }),
}, (table) => [
  uniqueIndex('uq_tb_pay_plan_fnc_key').on(table.planId, table.fncKey),
]);

// ---- TB_PAY_STLM_MTHD ----
export const paymentMethods = app.table('TB_PAY_STLM_MTHD', {
  id:             bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  wkspcId:        bigint('WKSPC_ID', { mode: 'number' }).notNull().references(() => workspaces.id, { onDelete: 'cascade' }),
  pgPrvdrCd:      varchar('PG_PRVDR_CD', { length: 50 }).notNull(),
  bilngKeyEncpt:  varchar('BILNG_KEY_ENCPT', { length: 500 }).notNull(),
  cstmrKey:       varchar('CSTMR_KEY', { length: 255 }).notNull(),
  typeCd:         varchar('TYPE_CD', { length: 20 }).notNull().default('CARD'),
  cardLast4:      varchar('CARD_LAST4', { length: 4 }),
  cardBrndNm:     varchar('CARD_BRND_NM', { length: 30 }),
  cardExpryMm:    integer('CARD_EXPRY_MM'),
  cardExpryYr:    integer('CARD_EXPRY_YR'),
  dfltYn:         char('DFLT_YN', { length: 1 }).notNull().default('N'),
  sttsCd:         varchar('STTS_CD', { length: 20 }).notNull().default('ACTIVE'),
  delDt:          timestamp('DEL_DT', { withTimezone: true }),
  crtrId:         bigint('CRTR_ID', { mode: 'number' }),
  crtDt:          timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
  mdfrId:         bigint('MDFR_ID', { mode: 'number' }),
  mdfcnDt:        timestamp('MDFCN_DT', { withTimezone: true }),
}, (table) => [
  index('idx_tb_pay_stlm_mthd_wkspc').on(table.wkspcId, table.sttsCd),
]);

// ---- TB_PAY_SBSC ----
export const subscriptions = app.table('TB_PAY_SBSC', {
  id:                  bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  wkspcId:             bigint('WKSPC_ID', { mode: 'number' }).notNull().references(() => workspaces.id, { onDelete: 'cascade' }),
  planId:              bigint('PLAN_ID', { mode: 'number' }).notNull().references(() => plans.id),
  stlmMthdId:          bigint('STLM_MTHD_ID', { mode: 'number' }).references(() => paymentMethods.id),
  sttsCd:              varchar('STTS_CD', { length: 20 }).notNull().default('ACTIVE'),
  crntPrdBgngDt:       timestamp('CRNT_PRD_BGNG_DT', { withTimezone: true }).notNull(),
  crntPrdEndDt:        timestamp('CRNT_PRD_END_DT', { withTimezone: true }).notNull(),
  trialBgngDt:         timestamp('TRIAL_BGNG_DT', { withTimezone: true }),
  trialEndDt:          timestamp('TRIAL_END_DT', { withTimezone: true }),
  bilngStdrDay:        integer('BILNG_STDR_DAY'),
  prdEndCnclYn:        char('PRD_END_CNCL_YN', { length: 1 }).notNull().default('N'),
  cnclDt:              timestamp('CNCL_DT', { withTimezone: true }),
  pausDt:              timestamp('PAUS_DT', { withTimezone: true }),
  mtdt:                jsonb('MTDT').default('{}'),
  crtrId:              bigint('CRTR_ID', { mode: 'number' }),
  crtDt:               timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
  mdfrId:              bigint('MDFR_ID', { mode: 'number' }),
  mdfcnDt:             timestamp('MDFCN_DT', { withTimezone: true }),
}, (table) => [
  index('idx_tb_pay_sbsc_wkspc').on(table.wkspcId, table.sttsCd),
  index('idx_tb_pay_sbsc_prd_end').on(table.crntPrdEndDt),
  index('idx_tb_pay_sbsc_stts').on(table.sttsCd),
]);

// ---- TH_PAY_SBSC ----
export const subscriptionHistory = app.table('TH_PAY_SBSC', {
  id:              bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  sbscId:          bigint('SBSC_ID', { mode: 'number' }).notNull().references(() => subscriptions.id),
  prvsPlanId:      bigint('PRVS_PLAN_ID', { mode: 'number' }).references(() => plans.id),
  newPlanId:       bigint('NEW_PLAN_ID', { mode: 'number' }).references(() => plans.id),
  chgTypeCd:       varchar('CHG_TYPE_CD', { length: 30 }).notNull(),
  efctvDt:         timestamp('EFCTV_DT', { withTimezone: true }).notNull(),
  prtnAmt:         bigint('PRTN_AMT', { mode: 'number' }),
  noteCn:          varchar('NOTE_CN', { length: 2000 }),
  crtrId:          bigint('CRTR_ID', { mode: 'number' }),
  crtDt:           timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
  mdfrId:          bigint('MDFR_ID', { mode: 'number' }),
  mdfcnDt:         timestamp('MDFCN_DT', { withTimezone: true }),
}, (table) => [
  index('idx_th_pay_sbsc_sbsc').on(table.sbscId),
]);

// ---- TB_PAY_INVC ----
export const invoices = app.table('TB_PAY_INVC', {
  id:              bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  wkspcId:         bigint('WKSPC_ID', { mode: 'number' }).notNull().references(() => workspaces.id),
  sbscId:          bigint('SBSC_ID', { mode: 'number' }).references(() => subscriptions.id),
  invcNo:          varchar('INVC_NO', { length: 50 }).notNull(),
  sttsCd:          varchar('STTS_CD', { length: 20 }).notNull().default('DRAFT'),
  prdBgngDt:       timestamp('PRD_BGNG_DT', { withTimezone: true }).notNull(),
  prdEndDt:        timestamp('PRD_END_DT', { withTimezone: true }).notNull(),
  stotAmt:         bigint('STOT_AMT', { mode: 'number' }).notNull(),
  txAmt:           bigint('TX_AMT', { mode: 'number' }).notNull().default(0),
  dscntAmt:        bigint('DSCNT_AMT', { mode: 'number' }).notNull().default(0),
  totAmt:          bigint('TOT_AMT', { mode: 'number' }).notNull(),
  payAmt:          bigint('PAY_AMT', { mode: 'number' }).notNull().default(0),
  unpayAmt:        bigint('UNPAY_AMT', { mode: 'number' }).notNull(),
  crncCd:          varchar('CRNC_CD', { length: 3 }).notNull().default('KRW'),
  stlmDelnDt:      timestamp('STLM_DELN_DT', { withTimezone: true }),
  stlmDt:          timestamp('STLM_DT', { withTimezone: true }),
  crtrId:          bigint('CRTR_ID', { mode: 'number' }),
  crtDt:           timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
  mdfrId:          bigint('MDFR_ID', { mode: 'number' }),
  mdfcnDt:         timestamp('MDFCN_DT', { withTimezone: true }),
}, (table) => [
  uniqueIndex('idx_tb_pay_invc_no').on(table.invcNo),
  index('idx_tb_pay_invc_wkspc').on(table.wkspcId, table.sttsCd),
  index('idx_tb_pay_invc_sbsc').on(table.sbscId),
  index('idx_tb_pay_invc_deln').on(table.stlmDelnDt, table.sttsCd),
]);

// ---- TB_PAY_INVC_ARTCL ----
export const invoiceLineItems = app.table('TB_PAY_INVC_ARTCL', {
  id:           bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  invcId:       bigint('INVC_ID', { mode: 'number' }).notNull().references(() => invoices.id, { onDelete: 'cascade' }),
  artclDc:      varchar('ARTCL_DC', { length: 500 }).notNull(),
  artclAmt:     bigint('ARTCL_AMT', { mode: 'number' }).notNull(),
  qty:          integer('QTY').notNull().default(1),
  unitPrc:      bigint('UNIT_PRC', { mode: 'number' }),
  typeCd:       varchar('TYPE_CD', { length: 30 }).notNull(),
  planId:       bigint('PLAN_ID', { mode: 'number' }).references(() => plans.id),
  prdBgngDt:    timestamp('PRD_BGNG_DT', { withTimezone: true }),
  prdEndDt:     timestamp('PRD_END_DT', { withTimezone: true }),
  prtnYn:       char('PRTN_YN', { length: 1 }).notNull().default('N'),
  crtrId:       bigint('CRTR_ID', { mode: 'number' }),
  crtDt:        timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
  mdfrId:       bigint('MDFR_ID', { mode: 'number' }),
  mdfcnDt:      timestamp('MDFCN_DT', { withTimezone: true }),
}, (table) => [
  index('idx_tb_pay_invc_artcl_invc').on(table.invcId),
]);

// ---- TB_PAY_STLM ----
export const payments = app.table('TB_PAY_STLM', {
  id:                 bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  invcId:             bigint('INVC_ID', { mode: 'number' }).notNull().references(() => invoices.id),
  stlmMthdId:         bigint('STLM_MTHD_ID', { mode: 'number' }).references(() => paymentMethods.id),
  stlmAmt:            bigint('STLM_AMT', { mode: 'number' }).notNull(),
  crncCd:             varchar('CRNC_CD', { length: 3 }).notNull().default('KRW'),
  sttsCd:             varchar('STTS_CD', { length: 20 }).notNull().default('PENDING'),
  pgPrvdrCd:          varchar('PG_PRVDR_CD', { length: 50 }),
  pgStlmKey:          varchar('PG_STLM_KEY', { length: 255 }),
  pgOrdrNo:           varchar('PG_ORDR_NO', { length: 255 }),
  pgRspnsCd:          varchar('PG_RSPNS_CD', { length: 20 }),
  pgRspnsMsg:         varchar('PG_RSPNS_MSG', { length: 2000 }),
  pgOrgnlRspns:       jsonb('PG_ORGNL_RSPNS'),
  atmtCnt:            integer('ATMT_CNT').notNull().default(1),
  idmptnKey:          varchar('IDMPTN_KEY', { length: 255 }).notNull(),
  failDt:             timestamp('FAIL_DT', { withTimezone: true }),
  scsDt:              timestamp('SCS_DT', { withTimezone: true }),
  rfndDt:             timestamp('RFND_DT', { withTimezone: true }),
  rfndAmt:            bigint('RFND_AMT', { mode: 'number' }).default(0),
  crtrId:             bigint('CRTR_ID', { mode: 'number' }),
  crtDt:              timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
  mdfrId:             bigint('MDFR_ID', { mode: 'number' }),
  mdfcnDt:            timestamp('MDFCN_DT', { withTimezone: true }),
}, (table) => [
  uniqueIndex('idx_tb_pay_stlm_idmptn').on(table.idmptnKey),
  index('idx_tb_pay_stlm_invc').on(table.invcId),
  index('idx_tb_pay_stlm_pg_key').on(table.pgStlmKey),
  index('idx_tb_pay_stlm_stts').on(table.sttsCd),
]);

// ---- TL_PAY_BILNG_EVNT ----
export const billingEvents = app.table('TL_PAY_BILNG_EVNT', {
  id:           bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  evntTypeCd:   varchar('EVNT_TYPE_CD', { length: 100 }).notNull(),
  enttyTypeCd:  varchar('ENTTY_TYPE_CD', { length: 50 }).notNull(),
  enttyId:      bigint('ENTTY_ID', { mode: 'number' }).notNull(),
  wkspcId:      bigint('WKSPC_ID', { mode: 'number' }).references(() => workspaces.id),
  userId:       bigint('USER_ID', { mode: 'number' }).references(() => users.id),
  evntData:     jsonb('EVNT_DATA').notNull(),
  crtDt:        timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('idx_tl_pay_bilng_evnt_type').on(table.evntTypeCd),
  index('idx_tl_pay_bilng_evnt_entty').on(table.enttyTypeCd, table.enttyId),
  index('idx_tl_pay_bilng_evnt_wkspc').on(table.wkspcId),
  index('idx_tl_pay_bilng_evnt_user').on(table.userId),
]);

// ---- TL_PAY_WBHK_EVNT ----
export const webhookEvents = app.table('TL_PAY_WBHK_EVNT', {
  id:              bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  prvdrCd:         varchar('PRVDR_CD', { length: 50 }).notNull(),
  extrlEvntId:     varchar('EXTRL_EVNT_ID', { length: 255 }).notNull(),
  evntTypeCd:      varchar('EVNT_TYPE_CD', { length: 100 }).notNull(),
  pyld:            jsonb('PYLD').notNull(),
  sttsCd:          varchar('STTS_CD', { length: 20 }).notNull().default('RECEIVED'),
  procDt:          timestamp('PROC_DT', { withTimezone: true }),
  errMsgCn:        varchar('ERR_MSG_CN', { length: 2000 }),
  rtryCnt:         integer('RTRY_CNT').notNull().default(0),
  crtDt:           timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  uniqueIndex('uq_tl_pay_wbhk_evnt_prvdr').on(table.prvdrCd, table.extrlEvntId),
]);

// ---- TH_PAY_STLM_RTRY ----
export const dunningAttempts = app.table('TH_PAY_STLM_RTRY', {
  id:              bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  sbscId:          bigint('SBSC_ID', { mode: 'number' }).notNull().references(() => subscriptions.id),
  invcId:          bigint('INVC_ID', { mode: 'number' }).notNull().references(() => invoices.id),
  atmtSn:          integer('ATMT_SN').notNull(),
  typeCd:          varchar('TYPE_CD', { length: 30 }).notNull(),
  sttsCd:          varchar('STTS_CD', { length: 20 }).notNull().default('SCHEDULED'),
  schdlDt:         timestamp('SCHDL_DT', { withTimezone: true }).notNull(),
  execDt:          timestamp('EXEC_DT', { withTimezone: true }),
  nxtAtmtDt:       timestamp('NXT_ATMT_DT', { withTimezone: true }),
  pgRspnsCd:       varchar('PG_RSPNS_CD', { length: 20 }),
  crtrId:          bigint('CRTR_ID', { mode: 'number' }),
  crtDt:           timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
  mdfrId:          bigint('MDFR_ID', { mode: 'number' }),
  mdfcnDt:         timestamp('MDFCN_DT', { withTimezone: true }),
}, (table) => [
  index('idx_th_pay_stlm_rtry_schdl').on(table.schdlDt, table.sttsCd),
  index('idx_th_pay_stlm_rtry_sbsc').on(table.sbscId),
]);

// ---- TB_PAY_CRDT_BLNC ----
export const creditBalances = app.table('TB_PAY_CRDT_BLNC', {
  id:          bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  wkspcId:     bigint('WKSPC_ID', { mode: 'number' }).notNull().references(() => workspaces.id, { onDelete: 'cascade' }),
  userId:      bigint('USER_ID', { mode: 'number' }).notNull().references(() => users.id, { onDelete: 'cascade' }),
  sbscId:      bigint('SBSC_ID', { mode: 'number' }).notNull().references(() => subscriptions.id),
  prdBgngDt:   timestamp('PRD_BGNG_DT', { withTimezone: true }).notNull(),
  prdEndDt:    timestamp('PRD_END_DT', { withTimezone: true }).notNull(),
  alotQty:     integer('ALOT_QTY').notNull(),
  usedQty:     integer('USED_QTY').notNull().default(0),
  rmnnQty:     integer('RMNN_QTY').notNull(),
  sttsCd:      varchar('STTS_CD', { length: 20 }).notNull().default('ACTIVE'),
  crtrId:      bigint('CRTR_ID', { mode: 'number' }),
  crtDt:       timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
  mdfrId:      bigint('MDFR_ID', { mode: 'number' }),
  mdfcnDt:     timestamp('MDFCN_DT', { withTimezone: true }),
}, (table) => [
  uniqueIndex('uq_tb_pay_crdt_blnc_prd').on(table.wkspcId, table.userId, table.prdBgngDt),
  index('idx_tb_pay_crdt_blnc_ws_user').on(table.wkspcId, table.userId, table.sttsCd),
  index('idx_tb_pay_crdt_blnc_prd').on(table.prdEndDt, table.sttsCd),
  index('idx_tb_pay_crdt_blnc_sbsc').on(table.sbscId),
]);

// ---- TL_PAY_CRDT_TRNS ----
export const creditTransactions = app.table('TL_PAY_CRDT_TRNS', {
  id:            bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  crdtBlncId:    bigint('CRDT_BLNC_ID', { mode: 'number' }).notNull().references(() => creditBalances.id),
  wkspcId:       bigint('WKSPC_ID', { mode: 'number' }).notNull().references(() => workspaces.id),
  userId:        bigint('USER_ID', { mode: 'number' }).notNull().references(() => users.id),
  trnsTypeCd:    varchar('TRNS_TYPE_CD', { length: 20 }).notNull(),
  trnsQty:       integer('TRNS_QTY').notNull(),
  blncBfrQty:    integer('BLNC_BFR_QTY').notNull(),
  blncAftQty:    integer('BLNC_AFT_QTY').notNull(),
  rfrncTypeCd:   varchar('RFRNC_TYPE_CD', { length: 50 }),
  rfrncId:       bigint('RFRNC_ID', { mode: 'number' }),
  trnsDc:        varchar('TRNS_DC', { length: 500 }),
  crtDt:         timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('idx_tl_pay_crdt_trns_blnc').on(table.crdtBlncId),
  index('idx_tl_pay_crdt_trns_ws_user').on(table.wkspcId, table.userId),
  index('idx_tl_pay_crdt_trns_type').on(table.trnsTypeCd),
  index('idx_tl_pay_crdt_trns_crt').on(table.crtDt),
]);
```

---

## 4. API 설계

### 4.1 API 엔드포인트 총괄

모든 API는 Next.js API Routes로 구현한다. 워크스페이스 범위의 API는 `/api/v1/workspaces/[workspaceId]/billing/...` 경로를 사용하며, 요청 시 JWT의 사용자가 해당 워크스페이스의 `OWNER` 또는 `ADMIN` 역할인지 미들웨어에서 검증한다.

#### 4.1.1 플랜 API (`/api/v1/billing/plans`)

| Method | Path | Auth | 설명 |
|--------|------|------|------|
| `GET` | `/api/v1/billing/plans` | Public | 활성 플랜 목록 조회 |
| `GET` | `/api/v1/billing/plans/[id]` | Public | 플랜 상세 조회 |
| `POST` | `/api/v1/billing/plans` | SYSTEM ADMIN | 플랜 생성 |
| `PATCH` | `/api/v1/billing/plans/[id]` | SYSTEM ADMIN | 플랜 수정 |

#### 4.1.2 결제 수단 API (`/api/v1/workspaces/[workspaceId]/billing/payment-methods`)

| Method | Path | Auth | 설명 |
|--------|------|------|------|
| `GET` | `/api/v1/workspaces/[workspaceId]/billing/payment-methods` | WS OWNER/ADMIN | 워크스페이스 결제 수단 목록 |
| `POST` | `/api/v1/workspaces/[workspaceId]/billing/payment-methods` | WS OWNER/ADMIN | 빌링키 등록 (결제 수단 추가) |
| `PATCH` | `/api/v1/workspaces/[workspaceId]/billing/payment-methods/[id]/default` | WS OWNER/ADMIN | 기본 결제 수단 변경 |
| `DELETE` | `/api/v1/workspaces/[workspaceId]/billing/payment-methods/[id]` | WS OWNER/ADMIN | 결제 수단 삭제 |

#### 4.1.3 구독 API (`/api/v1/workspaces/[workspaceId]/billing/subscriptions`)

| Method | Path | Auth | 설명 |
|--------|------|------|------|
| `GET` | `/api/v1/workspaces/[workspaceId]/billing/subscriptions/current` | WS MEMBER | 워크스페이스 현재 구독 정보 조회 |
| `POST` | `/api/v1/workspaces/[workspaceId]/billing/subscriptions` | WS OWNER/ADMIN | 구독 시작 |
| `PATCH` | `/api/v1/workspaces/[workspaceId]/billing/subscriptions/[id]/plan` | WS OWNER/ADMIN | 플랜 변경 (업/다운그레이드) |
| `POST` | `/api/v1/workspaces/[workspaceId]/billing/subscriptions/[id]/cancel` | WS OWNER/ADMIN | 구독 해지 |
| `POST` | `/api/v1/workspaces/[workspaceId]/billing/subscriptions/[id]/pause` | WS OWNER/ADMIN | 구독 일시정지 |
| `POST` | `/api/v1/workspaces/[workspaceId]/billing/subscriptions/[id]/resume` | WS OWNER/ADMIN | 구독 재개 |
| `GET` | `/api/v1/billing/subscriptions` | SYSTEM ADMIN | 전체 구독 목록 조회 |

> **권한 모델**: `WS OWNER/ADMIN`은 해당 워크스페이스의 소유자 또는 관리자 역할을 가진 사용자를 의미한다. `WS MEMBER`는 워크스페이스에 속한 모든 멤버가 조회 가능하다.

#### 4.1.4 청구서/결제 API (`/api/v1/workspaces/[workspaceId]/billing/invoices`)

| Method | Path | Auth | 설명 |
|--------|------|------|------|
| `GET` | `/api/v1/workspaces/[workspaceId]/billing/invoices` | WS OWNER/ADMIN | 워크스페이스 청구서 목록 |
| `GET` | `/api/v1/workspaces/[workspaceId]/billing/invoices/[id]` | WS OWNER/ADMIN | 청구서 상세 조회 |
| `POST` | `/api/v1/workspaces/[workspaceId]/billing/invoices/[id]/pay` | WS OWNER/ADMIN | 수동 결제 (미결제 청구서) |
| `POST` | `/api/v1/billing/payments/[id]/refund` | SYSTEM ADMIN | 환불 처리 |

#### 4.1.5 웹훅 API (`/api/v1/billing/webhook`)

| Method | Path | Auth | 설명 |
|--------|------|------|------|
| `POST` | `/api/v1/billing/webhook/toss` | Webhook Signature | 토스페이먼츠 웹훅 수신 |
| `POST` | `/api/v1/billing/webhook/kcp` | Webhook Signature | NHN KCP 웹훅 수신 |

#### 4.1.6 크레딧 API (`/api/v1/workspaces/[workspaceId]/billing/credits`)

| Method | Path | Auth | 설명 |
|--------|------|------|------|
| `GET` | `/api/v1/workspaces/[wsId]/billing/credits/me` | WS MEMBER | 내 현재 크레딧 잔액 조회 |
| `GET` | `/api/v1/workspaces/[wsId]/billing/credits/me/history` | WS MEMBER | 내 크레딧 사용 내역 조회 |
| `GET` | `/api/v1/workspaces/[wsId]/billing/credits/check` | WS MEMBER | 크레딧 사용 가능 여부 확인 |
| `POST` | `/api/v1/workspaces/[wsId]/billing/credits/deduct` | Internal API | 크레딧 차감 (서비스 간 호출) |
| `GET` | `/api/v1/workspaces/[wsId]/billing/credits/members` | WS OWNER/ADMIN | 멤버별 크레딧 현황 조회 |
| `POST` | `/api/v1/workspaces/[wsId]/billing/credits/[userId]/adjust` | WS OWNER/ADMIN | 특정 멤버 크레딧 수동 조정 |

### 4.2 상세 API 스펙

#### 4.2.1 GET /api/v1/billing/plans (플랜 목록 조회, Public)

**Response 200**:
```json
[
  {
    "id": 1,
    "name": "Basic",
    "description": "개인 사용자를 위한 기본 플랜",
    "billing_interval": "MONTHLY",
    "interval_count": 1,
    "amount": 9900,
    "currency": "KRW",
    "trial_days": 14,
    "features": [
      { "feature_key": "max_projects", "feature_value": "3" },
      { "feature_key": "storage_gb", "feature_value": "10" }
    ]
  },
  {
    "id": 2,
    "name": "Pro",
    "description": "팀을 위한 프로 플랜",
    "billing_interval": "MONTHLY",
    "interval_count": 1,
    "amount": 29900,
    "currency": "KRW",
    "trial_days": 14,
    "features": [
      { "feature_key": "max_projects", "feature_value": "unlimited" },
      { "feature_key": "storage_gb", "feature_value": "100" }
    ]
  }
]
```

#### 4.2.2 POST /api/v1/workspaces/[workspaceId]/billing/payment-methods (결제 수단 등록)

빌링키 발급 후 서버에 등록하는 API. 클라이언트에서 토스페이먼츠 SDK를 통해 빌링키 발급 인증을 완료한 뒤, `authKey`와 `customerKey`를 서버로 전달한다. 워크스페이스 `OWNER` 또는 `ADMIN` 역할을 가진 사용자만 호출 가능하다.

**Request Body**:
```typescript
const createPaymentMethodSchema = z.object({
  auth_key: z.string().min(1),          // PG사 인증 키
  customer_key: z.string().min(1),      // PG사 고객 식별자
  pg_provider: z.enum(['TOSS', 'KCP', 'NICE']).default('TOSS'),
});
```

**Response 201**:
```json
{
  "id": 1,
  "pg_provider": "TOSS",
  "type_cd": "CARD",
  "card_last4": "4242",
  "card_brand": "삼성카드",
  "card_exp_month": 12,
  "card_exp_year": 2028,
  "is_default": true,
  "status_cd": "ACTIVE",
  "created_at": "2026-02-14T10:00:00Z"
}
```

**비즈니스 로직**:
1. PG사 빌링키 발급 API 호출 (`POST /v1/billing/authorizations/issue`)
2. 빌링키를 AES-256으로 암호화
3. `TB_PAY_STLM_MTHD` 테이블에 저장
4. 워크스페이스의 첫 결제 수단이면 `DFLT_YN = 'Y'` 설정
5. 이벤트 기록: `payment_method.created`

**에러 응답**:

| HTTP 상태 | 에러 코드 | 설명 |
|-----------|----------|------|
| 400 | `VALIDATION_ERROR` | 요청 데이터 유효성 실패 |
| 400 | `BILLING_KEY_ISSUE_FAILED` | PG사 빌링키 발급 실패 |
| 409 | `PAYMENT_METHOD_ALREADY_EXISTS` | 동일 카드 이미 등록 |

#### 4.2.3 POST /api/v1/workspaces/[workspaceId]/billing/subscriptions (구독 시작)

**Request Body**:
```typescript
const createSubscriptionSchema = z.object({
  plan_id: z.number().int().positive(),
  payment_method_id: z.number().int().positive(),
});
```

**Response 201**:
```json
{
  "id": 1,
  "plan": {
    "id": 2,
    "name": "Pro",
    "amount": 29900,
    "billing_interval": "MONTHLY"
  },
  "status_cd": "TRIALING",
  "current_period_start": "2026-02-14T00:00:00Z",
  "current_period_end": "2026-02-28T00:00:00Z",
  "trial_start": "2026-02-14T00:00:00Z",
  "trial_end": "2026-02-28T00:00:00Z",
  "cancel_at_period_end": false,
  "created_at": "2026-02-14T10:00:00Z"
}
```

**비즈니스 로직**:
1. 플랜 유효성 검증 (활성 플랜인지)
2. 해당 워크스페이스의 기존 활성 구독 존재 여부 확인 (워크스페이스당 1개 구독 제한)
3. 결제 수단 유효성 검증
4. 무료 체험이 있으면 `TRIALING` 상태로 시작, 없으면 즉시 결제
5. 즉시 결제 시: 청구서 생성 → 빌링키 결제 실행
6. `TB_PAY_SBSC` 생성
7. `TH_PAY_SBSC` 기록 (CHG_TYPE_CD: 최초 생성)
8. 이벤트 기록: `subscription.created`

**에러 응답**:

| HTTP 상태 | 에러 코드 | 설명 |
|-----------|----------|------|
| 400 | `INVALID_PLAN` | 플랜이 존재하지 않거나 비활성 |
| 400 | `INVALID_PAYMENT_METHOD` | 결제 수단 유효하지 않음 |
| 409 | `ACTIVE_SUBSCRIPTION_EXISTS` | 해당 워크스페이스에 이미 활성 구독 존재 |
| 402 | `PAYMENT_FAILED` | 첫 결제 실패 |

#### 4.2.4 PATCH /api/v1/workspaces/[workspaceId]/billing/subscriptions/[id]/plan (플랜 변경)

**Request Body**:
```typescript
const changePlanSchema = z.object({
  new_plan_id: z.number().int().positive(),
  proration_behavior: z.enum(['create_prorations', 'none']).default('create_prorations'),
});
```

**Response 200**:
```json
{
  "id": 1,
  "plan": {
    "id": 3,
    "name": "Enterprise",
    "amount": 99000,
    "billing_interval": "MONTHLY"
  },
  "status_cd": "ACTIVE",
  "proration": {
    "credit_amount": -14950,
    "debit_amount": 49500,
    "net_amount": 34550,
    "description": "Pro (잔여 15일 크레딧) → Enterprise (잔여 15일 청구)"
  },
  "current_period_start": "2026-02-01T00:00:00Z",
  "current_period_end": "2026-03-01T00:00:00Z"
}
```

**비즈니스 로직 (비례 배분)**:
1. 현재 구독 및 플랜 정보 조회
2. 신규 플랜 유효성 검증
3. 비례 배분(Proration) 계산:
   - 미사용 크레딧 = (기존 플랜 일 요금) x 잔여 일수
   - 신규 비례 요금 = (신규 플랜 일 요금) x 잔여 일수
   - 차액 = 신규 비례 요금 - 미사용 크레딧
4. 업그레이드: 차액 즉시 결제
5. 다운그레이드: 크레딧을 다음 청구서에 적용
6. 구독 플랜 업데이트
7. `TH_PAY_SBSC` 기록
8. 이벤트 기록: `subscription.upgraded` 또는 `subscription.downgraded`

#### 4.2.5 POST /api/v1/workspaces/[workspaceId]/billing/subscriptions/[id]/cancel (구독 해지)

**Request Body**:
```typescript
const cancelSubscriptionSchema = z.object({
  cancel_at_period_end: z.boolean().default(true),  // true: 기간 만료 후 해지, false: 즉시 해지
  reason: z.string().max(500).optional(),
});
```

**Response 200**:
```json
{
  "id": 1,
  "status_cd": "ACTIVE",
  "cancel_at_period_end": true,
  "canceled_at": "2026-02-14T15:00:00Z",
  "current_period_end": "2026-03-01T00:00:00Z",
  "message": "구독이 2026-03-01에 해지 예정입니다."
}
```

**비즈니스 로직**:
1. `cancel_at_period_end = true`: 현재 기간 종료 후 해지 (서비스 계속 이용 가능)
2. `cancel_at_period_end = false`: 즉시 해지 (잔여 기간 비례 환불 가능)
3. `CNCL_DT` 기록
4. 이벤트 기록: `subscription.canceled`

#### 4.2.6 GET /api/v1/workspaces/[workspaceId]/billing/subscriptions/current (워크스페이스 현재 구독 조회)

**Response 200**:
```json
{
  "workspace_id": 1,
  "subscription": {
    "id": 1,
    "status_cd": "ACTIVE",
    "plan": {
      "id": 2,
      "name": "Pro",
      "amount": 29900,
      "billing_interval": "MONTHLY",
      "features": [
        { "feature_key": "max_members", "feature_value": "25" },
        { "feature_key": "max_projects", "feature_value": "unlimited" },
        { "feature_key": "storage_gb", "feature_value": "100" }
      ]
    },
    "current_period_start": "2026-02-01T00:00:00Z",
    "current_period_end": "2026-03-01T00:00:00Z",
    "cancel_at_period_end": false,
    "created_at": "2026-01-01T00:00:00Z"
  },
  "payment_method": {
    "id": 1,
    "card_last4": "4242",
    "card_brand": "삼성카드",
    "is_default": true
  },
  "upcoming_invoice": {
    "amount_due": 29900,
    "next_payment_date": "2026-03-01T00:00:00Z"
  },
  "can_manage_billing": true
}
```

#### 4.2.7 POST /api/v1/billing/webhook/toss (웹훅 수신)

**비즈니스 로직**:
1. 웹훅 서명 검증 (HMAC)
2. `EXTRL_EVNT_ID`로 중복 수신 확인 (멱등성)
3. `TL_PAY_WBHK_EVNT` 테이블에 저장 (STTS_CD: `RECEIVED`)
4. 이벤트 유형별 비즈니스 처리
5. 처리 완료 후 STTS_CD: `PROCESSED` 업데이트
6. 10초 이내 200 응답 반환

### 4.3 공통 에러 응답 형식 (결제)

```json
{
  "error": {
    "code": "PAYMENT_FAILED",
    "message": "결제에 실패했습니다.",
    "details": {
      "pg_response_code": "INSUFFICIENT_BALANCE",
      "pg_response_message": "잔액이 부족합니다."
    }
  }
}
```

### 4.4 PG사 추상화 인터페이스

```typescript
// lib/billing/pg/types.ts
interface PaymentGateway {
  /** 빌링키 발급 */
  issueBillingKey(command: BillingKeyCommand): Promise<BillingKeyResult>;
  /** 빌링키 결제 */
  chargeBillingKey(command: ChargeCommand): Promise<PaymentResult>;
  /** 결제 조회 */
  getPayment(paymentKey: string): Promise<PaymentResult>;
  /** 결제 취소/환불 */
  cancelPayment(command: CancelCommand): Promise<CancelResult>;
}

interface BillingKeyCommand {
  authKey: string;
  customerKey: string;
}

interface BillingKeyResult {
  billingKey: string;
  customerKey: string;
  cardInfo: {
    last4: string;
    brand: string;
    expMonth: number;
    expYear: number;
  };
  rawResponse: unknown;
}

interface ChargeCommand {
  billingKey: string;
  customerKey: string;
  orderId: string;
  orderName: string;
  amount: number;
  idempotencyKey: string;
}

interface PaymentResult {
  paymentKey: string;
  orderId: string;
  status: 'SUCCEEDED' | 'FAILED';
  amount: number;
  approvedAt?: string;
  responseCode?: string;
  responseMessage?: string;
  rawResponse: unknown;
}

interface CancelCommand {
  paymentKey: string;
  cancelReason: string;
  cancelAmount?: number;  // 부분 환불 시
}

interface CancelResult {
  paymentKey: string;
  cancelAmount: number;
  status: 'CANCELED';
  rawResponse: unknown;
}
```

### 4.5 크레딧 상세 API 스펙

#### 4.5.1 GET /credits/me (내 크레딧 잔액 조회)

**Response 200**:
```json
{
  "workspace_id": 2,
  "user_id": 42,
  "credit_balance": {
    "id": 100,
    "allocated": 500,
    "used": 320,
    "remaining": 180,
    "status_cd": "ACTIVE",
    "period_start": "2026-02-01T00:00:00Z",
    "period_end": "2026-03-01T00:00:00Z",
    "usage_rate": 64.0
  },
  "plan": {
    "name": "Pro",
    "monthly_credits": 500,
    "is_unlimited": false
  }
}
```

#### 4.5.2 GET /credits/check?amount=10 (크레딧 사용 가능 여부 확인)

**Query Params**: `amount` (차감할 크레딧 수량)

**Response 200** (사용 가능):
```json
{
  "available": true,
  "remaining": 180,
  "requested": 10,
  "after_deduction": 170
}
```

**Response 200** (사용 불가):
```json
{
  "available": false,
  "remaining": 5,
  "requested": 10,
  "shortfall": 5
}
```

#### 4.5.3 POST /credits/deduct (크레딧 차감)

**Request Body**:
```typescript
const deductCreditSchema = z.object({
  amount: z.number().int().positive(),
  reference_type: z.string().max(50).optional(),
  reference_id: z.number().int().positive().optional(),
  description: z.string().max(500).optional(),
});
```

**Response 200** (차감 성공):
```json
{
  "transaction_id": 500,
  "deducted": 10,
  "remaining": 170,
  "status_cd": "ACTIVE"
}
```

**에러 응답**:

| HTTP 상태 | 에러 코드 | 설명 |
|-----------|----------|------|
| 403 | `CREDIT_EXHAUSTED` | 크레딧 소진, 서비스 사용 불가 |
| 400 | `INSUFFICIENT_CREDITS` | 요청한 차감량보다 잔여 크레딧 부족 |
| 404 | `NO_ACTIVE_CREDIT_BALANCE` | 활성 크레딧 잔액 없음 (구독 없음) |
| 400 | `UNLIMITED_PLAN` | 무제한 플랜은 차감 불필요 |

#### 4.5.4 GET /credits/members (멤버별 크레딧 현황)

**Response 200**:
```json
{
  "workspace_id": 2,
  "period": {
    "start": "2026-02-01T00:00:00Z",
    "end": "2026-03-01T00:00:00Z"
  },
  "plan_monthly_credits": 500,
  "members": [
    {
      "user_id": 42,
      "display_name": "홍길동",
      "allocated": 500,
      "used": 320,
      "remaining": 180,
      "status_cd": "ACTIVE",
      "usage_rate": 64.0
    },
    {
      "user_id": 43,
      "display_name": "김철수",
      "allocated": 500,
      "used": 500,
      "remaining": 0,
      "status_cd": "EXHAUSTED",
      "usage_rate": 100.0
    }
  ]
}
```

#### 4.5.5 GET /credits/me/history (내 크레딧 사용 내역)

**Query Params**: `page` (페이지), `limit` (조회 수)

**Response 200**:
```json
{
  "items": [
    {
      "id": 500,
      "type_cd": "DEDUCTION",
      "quantity": -10,
      "balance_before": 180,
      "balance_after": 170,
      "reference_type": "message",
      "reference_id": 1234,
      "description": "AI 메시지 생성",
      "created_at": "2026-02-14T10:30:00Z"
    }
  ],
  "total": 45,
  "page": 1,
  "limit": 20
}
```

#### 4.5.6 POST /credits/[userId]/adjust (크레딧 수동 조정)

**Request Body**:
```typescript
const adjustCreditSchema = z.object({
  amount: z.number().int(),  // 양수: 추가, 음수: 차감
  reason: z.string().min(1).max(500),
});
```

**Response 200**:
```json
{
  "transaction_id": 501,
  "adjusted": 50,
  "remaining": 230,
  "status_cd": "ACTIVE"
}
```

---

## 5. 화면 구성

### 5.1 화면 목록 총괄

워크스페이스 범위의 결제 페이지는 `/workspaces/[workspaceId]/billing/...` 경로를 사용한다.

| 구분 | 경로 | 접근 권한 | 설명 |
|------|------|----------|------|
| 요금제 안내 | `/pricing` | Public | 플랜 비교 및 구독 시작 |
| 결제 수단 등록 | `/workspaces/[workspaceId]/billing/payment-method` | WS OWNER/ADMIN | 카드 등록 (빌링키 발급) |
| 구독 관리 | `/workspaces/[workspaceId]/billing/subscription` | WS OWNER/ADMIN | 워크스페이스 구독 정보 + 플랜 변경 |
| 결제 내역 | `/workspaces/[workspaceId]/billing/invoices` | WS OWNER/ADMIN | 청구서 목록 + 영수증 |
| 결제 내역 상세 | `/workspaces/[workspaceId]/billing/invoices/[id]` | WS OWNER/ADMIN | 청구서 상세 |
| 결제 실패 안내 | `/workspaces/[workspaceId]/billing/payment-failed` | WS OWNER/ADMIN | 결제 실패 시 수단 변경 안내 |
| 멤버별 크레딧 관리 | `/workspaces/[workspaceId]/billing/credits` | WS OWNER/ADMIN | 멤버별 크레딧 현황 및 조정 |
| 구독 관리 (관리자) | `/admin/settings/subscriptions` | SYSTEM ADMIN | 전체 구독 현황 대시보드 |
| 플랜 관리 (관리자) | `/admin/settings/plans` | SYSTEM ADMIN | 플랜 CRUD |

### 5.2 요금제 안내 페이지 (`/pricing`)

```
┌──────────────────────────────────────────────────────────────────┐
│                        요금제 안내                                │
│            나에게 맞는 플랜을 선택하세요                            │
│                                                                  │
│    ┌─ 결제 주기 ──────────────────┐                              │
│    │  [● 월간 결제]  [○ 연간 결제 (20% 할인)]  │                  │
│    └──────────────────────────────┘                              │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │    Basic      │  │     Pro       │  │  Enterprise   │          │
│  │              │  │   인기        │  │              │          │
│  │  ₩9,900/월   │  │  ₩29,900/월  │  │  ₩99,000/월  │          │
│  │              │  │              │  │              │          │
│  │  ✓ 3 프로젝트 │  │  ✓ 무제한     │  │  ✓ 무제한     │          │
│  │  ✓ 10GB 저장  │  │  ✓ 100GB 저장 │  │  ✓ 무제한 저장 │          │
│  │  ✓ 이메일 지원│  │  ✓ 우선 지원   │  │  ✓ 전담 지원   │          │
│  │              │  │  ✓ API 접근   │  │  ✓ SSO/SAML  │          │
│  │              │  │              │  │  ✓ SLA 보장   │          │
│  │              │  │              │  │              │          │
│  │ [14일 무료 체험]│  │ [14일 무료 체험]│  │  [문의하기]   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  모든 플랜은 14일 무료 체험 후 자동 결제됩니다.                      │
│  언제든 해지할 수 있습니다.                                        │
└──────────────────────────────────────────────────────────────────┘
```

#### 기능 상세

| 항목 | 설명 |
|------|------|
| 플랜 로딩 | `GET /api/v1/billing/plans` 호출하여 동적 표시 |
| 월간/연간 토글 | 연간 결제 선택 시 할인 금액 표시 |
| 구독 시작 | 로그인 확인 → 워크스페이스 선택 → 결제 권한 확인 → 결제 수단 등록 → 구독 생성 |
| 비로그인 사용자 | 버튼 클릭 시 로그인 페이지로 이동 (redirect 파라미터 포함) |
| 워크스페이스 미소유 | 워크스페이스 생성 안내 또는 기존 워크스페이스 선택 화면 표시 |

### 5.3 결제 수단 등록 페이지 (`/workspaces/[workspaceId]/billing/payment-method`)

```
┌──────────────────────────────────────────────────────────────────┐
│  [Layout]                                                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  결제 수단 관리                                             │  │
│  │                                                            │  │
│  │  ── 등록된 결제 수단 ──                                     │  │
│  │  ┌────────────────────────────────────────────┐           │  │
│  │  │  💳 삼성카드 **** 4242          기본 결제 수단  │           │  │
│  │  │     만료: 12/2028                           │           │  │
│  │  │     [기본으로 설정]  [삭제]                    │           │  │
│  │  └────────────────────────────────────────────┘           │  │
│  │  ┌────────────────────────────────────────────┐           │  │
│  │  │  💳 현대카드 **** 1234                       │           │  │
│  │  │     만료: 06/2027                           │           │  │
│  │  │     [기본으로 설정]  [삭제]                    │           │  │
│  │  └────────────────────────────────────────────┘           │  │
│  │                                                            │  │
│  │  ┌──────────────────────────────┐                         │  │
│  │  │     + 새 결제 수단 추가       │                         │  │
│  │  └──────────────────────────────┘                         │  │
│  │                                                            │  │
│  │  * 결제 수단 추가 시 토스페이먼츠 보안 결제창이 표시됩니다.    │  │
│  │  * 카드 정보는 PG사에서 안전하게 관리됩니다.                  │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

#### 기능 상세

| 항목 | API | 설명 |
|------|-----|------|
| 결제 수단 목록 | `GET /workspaces/:wsId/billing/payment-methods` | 워크스페이스에 등록된 카드 목록 표시 |
| 새 카드 등록 | 토스페이먼츠 SDK → `POST /workspaces/:wsId/billing/payment-methods` | PG 결제창으로 카드 등록 |
| 기본 설정 | `PATCH /workspaces/:wsId/billing/payment-methods/:id/default` | 기본 결제 수단 변경 |
| 삭제 | `DELETE /workspaces/:wsId/billing/payment-methods/:id` | Soft Delete (활성 구독에 사용 중이면 거부) |

### 5.4 구독 관리 페이지 (`/workspaces/[workspaceId]/billing/subscription`)

```
┌──────────────────────────────────────────────────────────────────┐
│  [Layout]                                                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  구독 관리                                                  │  │
│  │                                                            │  │
│  │  ── 현재 구독 ──                                            │  │
│  │  ┌────────────────────────────────────────────┐           │  │
│  │  │  Pro 플랜                        활성 ●    │           │  │
│  │  │  ₩29,900/월                                │           │  │
│  │  │                                            │           │  │
│  │  │  구독 시작일: 2026.01.01                    │           │  │
│  │  │  다음 결제일: 2026.03.01                    │           │  │
│  │  │  결제 수단: 삼성카드 **** 4242              │           │  │
│  │  │                                            │           │  │
│  │  │  [플랜 변경]  [구독 일시정지]  [구독 해지]    │           │  │
│  │  └────────────────────────────────────────────┘           │  │
│  │                                                            │  │
│  │  ── 포함된 기능 ──                                          │  │
│  │  ✓ 프로젝트 무제한                                         │  │
│  │  ✓ 저장 공간 100GB                                         │  │
│  │  ✓ 우선 지원                                               │  │
│  │  ✓ API 접근                                                │  │
│  │                                                            │  │
│  │  ── 사용량 ──                                               │  │
│  │  프로젝트: 12 / 무제한                                      │  │
│  │  저장 공간: 45.2GB / 100GB  [████████░░░░] 45%              │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### 5.5 결제 내역 페이지 (`/workspaces/[workspaceId]/billing/invoices`)

```
┌──────────────────────────────────────────────────────────────────┐
│  [Layout]                                                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  결제 내역                                                  │  │
│  │                                                            │  │
│  │  ┌────┬──────────┬────────┬────────┬──────┬──────┐       │  │
│  │  │ No │ 청구서번호 │ 기간    │ 금액    │ 상태  │      │       │  │
│  │  ├────┼──────────┼────────┼────────┼──────┼──────┤       │  │
│  │  │  3 │INV-2602..│02.01~03│₩29,900 │ 결제  │영수증│       │  │
│  │  │  2 │INV-2601..│01.01~02│₩29,900 │ 결제  │영수증│       │  │
│  │  │  1 │INV-2512..│12.14~01│₩0      │ 체험  │  -  │       │  │
│  │  └────┴──────────┴────────┴────────┴──────┴──────┘       │  │
│  │                                                            │  │
│  │  < 1 2 3 >                                                 │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### 5.6 플랜 변경 모달

```
┌──────────────────────────────────────┐
│          플랜 변경                    │
│                                      │
│  현재: Pro (₩29,900/월)              │
│    ↓                                 │
│  변경: Enterprise (₩99,000/월)       │
│                                      │
│  ── 비례 배분 안내 ──                 │
│  현재 플랜 잔여 크레딧: -₩14,950      │
│  새 플랜 잔여 기간 요금: +₩49,500     │
│  ──────────────────                  │
│  즉시 결제 금액: ₩34,550             │
│                                      │
│  * 다음 정기 결제일: 2026.03.01       │
│  * 다음 결제 금액: ₩99,000           │
│                                      │
│        [취소]  [플랜 변경하기]         │
└──────────────────────────────────────┘
```

### 5.7 구독 해지 모달

```
┌──────────────────────────────────────┐
│          구독 해지                    │
│                                      │
│  정말 구독을 해지하시겠습니까?         │
│                                      │
│  ● 현재 기간 종료 후 해지             │
│    (2026.03.01까지 서비스 이용 가능)   │
│  ○ 즉시 해지                         │
│    (잔여 기간 비례 환불)              │
│                                      │
│  해지 사유 (선택):                    │
│  ┌──────────────────────────────┐   │
│  │ 비용이 부담됩니다              │   │
│  └──────────────────────────────┘   │
│                                      │
│  ⚠ 해지 후에도 현재 기간 종료까지     │
│    서비스를 이용할 수 있습니다.        │
│                                      │
│        [취소]  [구독 해지하기]         │
└──────────────────────────────────────┘
```

### 5.8 구독 관리 페이지 크레딧 사용량 섹션

기존 `/workspaces/[workspaceId]/billing/subscription` 페이지에 크레딧 사용량 섹션 추가:

```
│                                                               │
│  ── 크레딧 사용량 ──                                          │
│  이번 달 크레딧: 320 / 500 사용  [████████████░░░░░] 64%     │
│  잔여: 180 크레딧                                             │
│  리셋일: 2026.03.01                                           │
│                                                               │
│  [크레딧 사용 내역 보기]                                       │
│                                                               │
```

### 5.9 크레딧 소진 배너 (`CreditExhaustedBanner.tsx`)

크레딧이 소진된 사용자에게 표시하는 배너:

```
┌──────────────────────────────────────────────────────┐
│  ⚠ 이번 달 크레딧이 모두 소진되었습니다.               │
│  다음 크레딧 리셋: 2026.03.01                         │
│  [상위 플랜으로 업그레이드]                             │
└──────────────────────────────────────────────────────┘
```

### 5.10 멤버별 크레딧 관리 페이지 (`/workspaces/[workspaceId]/billing/credits`)

OWNER/ADMIN 전용 멤버별 크레딧 현황 관리 페이지:

```
┌──────────────────────────────────────────────────────────────┐
│  ── 멤버별 크레딧 현황 ──                                     │
│  ┌──────┬──────┬──────┬──────┬──────┬──────┐               │
│  │ 멤버  │ 할당  │ 사용  │ 잔여  │ 사용률 │ 상태  │               │
│  ├──────┼──────┼──────┼──────┼──────┼──────┤               │
│  │홍길동 │  500 │  320 │  180 │  64% │ 활성  │               │
│  │김철수 │  500 │  500 │    0 │ 100% │ 소진  │               │
│  │이영희 │  357 │  150 │  207 │  42% │ 활성  │               │
│  └──────┴──────┴──────┴──────┴──────┴──────┘               │
│  * 이영희: 월 중 가입으로 비례 할당 (500 × 20/28 = 357)       │
└──────────────────────────────────────────────────────────────┘
```

---

## 6. 결제 흐름

### 6.1 구독 시작 (빌링키 발급 + 첫 결제)

```
[워크스페이스 관리자] ──────────────────────────────────────────
  │
  │  1. 플랜 선택 + "구독 시작" 클릭
  │     (워크스페이스 OWNER/ADMIN 권한 확인)
  ▼
[Next.js Client] ────────────────────────────────────────────
  │
  │  2. 토스페이먼츠 SDK 결제창 호출
  │     → requestBillingAuth({ customerKey: ws_{workspaceId}, ... })
  ▼
[토스페이먼츠 결제창] ───────────────────────────────────────
  │
  │  3. 카드 정보 입력 + 본인 인증
  │  4. 리다이렉트 (authKey, customerKey)
  ▼
[Next.js Client] ────────────────────────────────────────────
  │
  │  5. POST /api/v1/workspaces/{workspaceId}/billing/payment-methods
  │     { auth_key, customer_key, pg_provider: "TOSS" }
  ▼
[Next.js API Route] ─────────────────────────────────────────
  │
  │  6. 워크스페이스 멤버십 + OWNER/ADMIN 권한 검증
  │  7. 토스페이먼츠 빌링키 발급 API 호출
  │     POST /v1/billing/authorizations/issue
  │  8. 빌링키 AES-256 암호화 → DB 저장 (WKSPC_ID 연결)
  │  9. 응답: 결제 수단 정보
  ▼
[Next.js Client] ────────────────────────────────────────────
  │
  │  10. POST /api/v1/workspaces/{workspaceId}/billing/subscriptions
  │      { plan_id, payment_method_id }
  ▼
[Next.js API Route] ─────────────────────────────────────────
  │
  │  11. 해당 워크스페이스의 활성 구독 존재 여부 확인
  │  12. 무료 체험 여부 확인
  │  ├─ 체험 있음 → TRIALING 상태 생성 (결제 없음)
  │  └─ 체험 없음 → 청구서 생성 → 빌링키 결제 실행
  │     POST /v1/billing/{billingKey} (토스 API)
  │  13. 구독 생성 (WKSPC_ID 연결) + 이벤트 기록
  ▼
[결제 완료 / 체험 시작 → 워크스페이스 전체 멤버 혜택 적용]
```

### 6.2 정기결제 실행 (스케줄러)

```
[Cron Scheduler] ─── 매일 09:00 KST 실행 ──────────────────
  │
  │  1. 오늘 결제 예정인 워크스페이스 구독 조회
  │     WHERE CRNT_PRD_END_DT <= NOW()
  │     AND STTS_CD IN ('ACTIVE', 'TRIALING')
  │     AND PRD_END_CNCL_YN = 'N'
  ▼
[각 워크스페이스 구독별 처리] ────────────────────────────────
  │
  │  2. 청구서(Invoice) 생성
  │     - INVC_NO: INV-YYYYMMDD-XXXX
  │     - 청구 항목(Line Items) 추가
  │  3. 빌링키 복호화 (AES-256)
  │  4. PG사 결제 요청
  │     - IDMPTN_KEY 생성 (중복 결제 방지)
  │     - POST /v1/billing/{billingKey}
  ▼
  ├─ 결제 성공
  │   │
  │   │  5a. Invoice: PAID, Payment: SUCCEEDED
  │   │  6a. 구독 기간 갱신 (CRNT_PRD_BGNG_DT/CRNT_PRD_END_DT)
  │   │  7a. 이벤트: invoice.paid, payment.succeeded
  │   │  8a. 결제 완료 알림 (이메일/푸시)
  │   ▼
  │  [다음 주기 대기]
  │
  └─ 결제 실패
      │
      │  5b. Payment: FAILED
      │  6b. 구독 상태: PAST_DUE
      │  7b. Dunning 프로세스 시작
      │     - 1차: 1시간 후 자동 재시도 (AUTO_RETRY)
      │     - 2차: 24시간 후 재시도 + 이메일 (RETRY_WITH_EMAIL)
      │     - 3차: 72시간 후 재시도 + SMS (RETRY_WITH_SMS)
      │     - 4차: 7일 후 최종 알림 (FINAL_NOTICE)
      │  8b. 이벤트: payment.failed
      ▼
     [Dunning 프로세스]
```

### 6.3 구독 상태 전이도

```
                          ┌─────────────────┐
                          │                 │
                  trial   │    trial_end    │   payment
                  start   │    + payment    │   success
[최초] ──────▶ [TRIALING] ──────────────▶ [ACTIVE] ◀────────────┐
                  │                         │    │               │
                  │ trial_end               │    │               │
                  │ + payment fail          │    │               │
                  │                         │    │               │
                  ▼              payment    │    │  payment      │
              [CANCELED]    ◀── failed ─────┘    │  success      │
                  ▲                              │               │
                  │                              ▼               │
                  │  dunning          ┌──── [PAST_DUE] ─────────┘
                  │  all failed       │          │
                  │                   │          │ dunning
                  ├───────────────────┘          │ exhausted
                  │                              ▼
                  │                        [SUSPENDED]
                  │                              │
                  │  grace period                │ payment method
                  │  expired                     │ updated + success
                  ├──────────────────────────────┘
                  │                              │
                  │         cancel               ▼
                  ├───────────────────────── [ACTIVE]
                  │
                  │         pause         resume
             [ACTIVE] ──────────▶ [PAUSED] ──────▶ [ACTIVE]
                                     │
                                     │ cancel
                                     ▼
                                 [CANCELED]
```

### 6.4 Dunning (결제 재시도) 전략

#### 재시도 스케줄

| 시도 | 시점 | 유형 | 알림 |
|------|------|------|------|
| 1차 | 결제 실패 + 1시간 | `AUTO_RETRY` | 없음 (자동 재시도) |
| 2차 | 결제 실패 + 24시간 | `RETRY_WITH_EMAIL` | 이메일: "결제 실패, 재시도 예정" |
| 3차 | 결제 실패 + 72시간 | `RETRY_WITH_SMS` | SMS: "결제수단 확인 요청" |
| 4차 | 결제 실패 + 7일 | `FINAL_NOTICE` | 이메일+SMS: "서비스 정지 예고" |
| 정지 | 결제 실패 + 14일 | - | 구독 `SUSPENDED` 처리 |

#### 카드사 응답 코드별 재시도 전략

| 응답 유형 | 대응 | 재시도 |
|-----------|------|--------|
| 잔액 부족 (`INSUFFICIENT_BALANCE`) | 다음 스케줄 재시도 | O |
| 한도 초과 (`EXCEED_LIMIT`) | 다음 스케줄 재시도 | O |
| 카드사 시스템 오류 (`CARD_COMPANY_ERROR`) | 1시간 후 즉시 재시도 | O |
| 통신 오류 (`PG_NETWORK_ERROR`) | 지수적 백오프 재시도 | O |
| 유효기간 만료 (`CARD_EXPIRED`) | 카드 재등록 요청 알림 | X |
| 분실/도난 카드 (`CARD_LOST_STOLEN`) | 카드 재등록 요청 알림 | X |
| 무효 빌링키 (`INVALID_BILLING_KEY`) | 카드 재등록 요청 알림 | X |

### 6.5 비례 배분(Proration) 계산

```
[업그레이드 예시]
─────────────────────────────────────────────────
현재 플랜: Pro (₩29,900/월), 시작일: 02.01, 종료일: 03.01
변경 시점: 02.15 (사용 14일, 잔여 14일)
신규 플랜: Enterprise (₩99,000/월)

해당 월 일수 = 28일

기존 플랜 일 요금 = ₩29,900 / 28 = ₩1,068 (반올림)
신규 플랜 일 요금 = ₩99,000 / 28 = ₩3,536 (반올림)

미사용 크레딧 = ₩1,068 × 14일 = ₩14,952
신규 비례 요금 = ₩3,536 × 14일 = ₩49,504

즉시 청구 = ₩49,504 - ₩14,952 = ₩34,552
─────────────────────────────────────────────────

[다운그레이드 예시]
─────────────────────────────────────────────────
현재 플랜: Enterprise (₩99,000/월), 시작일: 02.01, 종료일: 03.01
변경 시점: 02.20 (사용 19일, 잔여 9일)
신규 플랜: Pro (₩29,900/월)

해당 월 일수 = 28일

기존 플랜 일 요금 = ₩99,000 / 28 = ₩3,536
신규 플랜 일 요금 = ₩29,900 / 28 = ₩1,068

미사용 크레딧 = ₩3,536 × 9일 = ₩31,824
신규 비례 요금 = ₩1,068 × 9일 = ₩9,612

크레딧 잔액 = ₩31,824 - ₩9,612 = ₩22,212
→ 다음 청구서에 ₩22,212 크레딧 적용
─────────────────────────────────────────────────
```

### 6.6 크레딧 생명주기

#### 6.6.1 구독 생성/갱신 시 크레딧 할당

`lib/billing/subscription-manager.ts` 수정:
- 구독 생성 시 (`subscription.created`) → `creditManager.allocateCreditsForPeriod()` 호출
- 정기결제 갱신 시 (scheduler) → 이전 기간 크레딧 만료 + 신규 기간 크레딧 할당

```
[구독 생성/갱신] ──────────────────────────────────────────────
  │
  │  1. 구독 생성 또는 정기결제 갱신 성공
  │
  │  2. TB_PAY_PLAN_FNC에서 monthly_credits 조회
  │     ├─ "unlimited" → 크레딧 관리 생략
  │     └─ 정수값 → 크레딧 할당 진행
  │
  │  3. (갱신 시) 이전 기간 크레딧 EXPIRED 처리
  │     └─ creditManager.expireCreditsForPeriod()
  │
  │  4. 워크스페이스 전체 활성 멤버 조회
  │
  │  5. 각 멤버에게 크레딧 할당
  │     ├─ TB_PAY_CRDT_BLNC INSERT (ALOT_QTY = RMNN_QTY = monthly_credits)
  │     └─ TL_PAY_CRDT_TRNS INSERT (TRNS_TYPE_CD = 'ALLOCATION')
  │
  │  6. TL_PAY_BILNG_EVNT INSERT (credit.allocated)
  ▼
```

#### 6.6.2 크레딧 차감 (원자적 처리)

`lib/billing/credit-manager.ts`:

```
[서비스 호출] ──────────────────────────────────────────────────
  │
  │  1. POST /credits/deduct { amount, reference_type, reference_id }
  │
  │  ── 트랜잭션 시작 ──
  │
  │  2. SELECT FOR UPDATE: 현재 ACTIVE 크레딧 잔액 조회 (동시성 제어)
  │
  │  3. 잔액 검사
  │     ├─ RMNN_QTY < amount → CreditExhaustedException (403)
  │     └─ RMNN_QTY >= amount → 진행
  │
  │  4. TB_PAY_CRDT_BLNC UPDATE
  │     ├─ USED_QTY += amount
  │     ├─ RMNN_QTY -= amount
  │     └─ STTS_CD = (RMNN_QTY == 0 ? 'EXHAUSTED' : 'ACTIVE')
  │
  │  5. TL_PAY_CRDT_TRNS INSERT (TRNS_TYPE_CD = 'DEDUCTION')
  │
  │  6. TL_PAY_BILNG_EVNT INSERT (credit.deducted)
  │     └─ (RMNN_QTY == 0 이면 credit.exhausted 이벤트 추가)
  │
  │  ── 트랜잭션 커밋 ──
  ▼
```

#### 6.6.3 멤버 가입 시 비례 크레딧 할당

워크스페이스 모듈 연동 (초대 수락 시):

```
[초대 수락] ──────────────────────────────────────────────────
  │
  │  1. TR_COMM_WKSPC_MBR 생성 (멤버 추가)
  │
  │  2. 워크스페이스의 활성 구독 조회
  │     └─ 구독 없음 → 크레딧 할당 생략
  │
  │  3. TB_PAY_PLAN_FNC에서 monthly_credits 조회
  │     └─ "unlimited" → 크레딧 할당 생략
  │
  │  4. 비례 계산
  │     ├─ totalDays = PRD_END_DT - PRD_BGNG_DT
  │     ├─ remainingDays = PRD_END_DT - NOW()
  │     └─ proratedCredits = Math.floor(monthlyCredits * remainingDays / totalDays)
  │
  │  5. TB_PAY_CRDT_BLNC INSERT (ALOT_QTY = RMNN_QTY = proratedCredits)
  │  6. TL_PAY_CRDT_TRNS INSERT (TRNS_TYPE_CD = 'ALLOCATION')
  │  7. TL_PAY_BILNG_EVNT INSERT (credit.allocated)
  ▼
```

#### 6.6.4 멤버 탈퇴/강제퇴장 시 크레딧 만료

```
[멤버 탈퇴/강제퇴장] ──────────────────────────────────────────
  │
  │  1. TR_COMM_WKSPC_MBR.STTS_CD = "LEFT"
  │
  │  2. 해당 멤버의 ACTIVE 크레딧 잔액 조회
  │
  │  3. TB_PAY_CRDT_BLNC UPDATE (STTS_CD = 'EXPIRED')
  │  4. TL_PAY_BILNG_EVNT INSERT (credit.expired)
  ▼
```

#### 6.6.5 플랜 변경 시 크레딧 재조정

```
[플랜 변경] ──────────────────────────────────────────────────
  │
  │  ── 업그레이드 ──
  │  │  1. 모든 멤버의 ACTIVE 크레딧 잔액 조회
  │  │  2. 추가 크레딧 = (newPlanCredits - oldPlanCredits) * remainingDays / totalDays
  │  │  3. TB_PAY_CRDT_BLNC UPDATE (ALOT_QTY += 추가, RMNN_QTY += 추가)
  │  │  4. EXHAUSTED 상태면 ACTIVE로 복원
  │  │  5. TL_PAY_CRDT_TRNS INSERT (TRNS_TYPE_CD = 'PLAN_CHANGE')
  │
  │  ── 다운그레이드 ──
  │  │  1. 모든 멤버의 ACTIVE 크레딧 잔액 조회
  │  │  2. 새 할당량 = newPlanCredits * remainingDays / totalDays
  │  │  3. ALOT_QTY 조정, RMNN_QTY가 새 할당량 초과 시 제한
  │  │  4. TL_PAY_CRDT_TRNS INSERT (TRNS_TYPE_CD = 'PLAN_CHANGE')
  ▼
```

---

## 7. 보안 설계

### 7.1 빌링키 보안

| 항목 | 설계 |
|------|------|
| 암호화 알고리즘 | AES-256-GCM (AEAD 모드) |
| 암호화 키 관리 | 환경 변수 (`BILLING_KEY_ENCRYPTION_KEY`), 운영 시 AWS KMS/Vault 권장 |
| 저장 방식 | 암호화된 값만 DB에 저장 (`BILNG_KEY_ENCPT`) |
| 복호화 시점 | PG사 결제 요청 직전에만 복호화, 사용 후 즉시 메모리 소거 |
| 카드 정보 | PAN 저장 금지, 마지막 4자리/브랜드/만료일만 저장 |

```typescript
// lib/billing/crypto.ts
import CryptoJS from 'crypto-js';

const ENCRYPTION_KEY = process.env.BILLING_KEY_ENCRYPTION_KEY!;

export function encryptBillingKey(billingKey: string): string {
  return CryptoJS.AES.encrypt(billingKey, ENCRYPTION_KEY).toString();
}

export function decryptBillingKey(encrypted: string): string {
  const bytes = CryptoJS.AES.decrypt(encrypted, ENCRYPTION_KEY);
  return bytes.toString(CryptoJS.enc.Utf8);
}
```

### 7.2 웹훅 보안

| 항목 | 설계 |
|------|------|
| 서명 검증 | 토스페이먼츠 HMAC 서명 검증, 서명 불일치 시 거부 |
| 타임스탬프 검증 | 수신 후 5분 이내 전송된 웹훅만 허용 (Replay Attack 방지) |
| 멱등성 보장 | `EXTRL_EVNT_ID`로 중복 수신 차단 |
| IP 화이트리스트 | 운영 환경에서 PG사 IP 대역만 허용 권장 |
| 응답 시간 | 10초 이내 200 응답 (비동기 큐 처리 권장) |

### 7.3 결제 데이터 보안

| 항목 | 설계 |
|------|------|
| 금액 위변조 방지 | 서버 측에서 플랜 금액 재조회하여 검증, 클라이언트 금액 불신 |
| 멱등성 키 | 모든 결제 요청에 `IDMPTN_KEY` 필수 적용 |
| PG 원본 보관 | PG사 요청/응답 원본을 `PG_ORGNL_RSPNS`에 보관 (분쟁 대응) |
| 감사 로그 | 모든 결제 관련 상태 변경을 `TL_PAY_BILNG_EVNT`에 불변 기록 |
| Soft Delete | 결제 관련 데이터는 물리 삭제 금지 |

### 7.4 API 보안

| 항목 | 설계 |
|------|------|
| 인증 | 인증 모듈의 JWT Bearer 토큰 재사용 |
| 워크스페이스 검증 | 요청 경로의 `workspaceId`에 대해 사용자의 멤버십 및 역할(OWNER/ADMIN) 검증 |
| 권한 검증 | 구독/결제 수단은 해당 워크스페이스의 OWNER/ADMIN만 관리 가능, 구독 정보 조회는 멤버 전원 가능 |
| 입력 검증 | Zod 스키마로 서버 측 입력 검증 |
| CSRF | SameSite Cookie + Origin 헤더 검증 |

### 7.5 Rate Limiting

| 엔드포인트 | 제한 | 창 |
|-----------|------|-----|
| `POST /workspaces/:wsId/billing/payment-methods` | 5회/워크스페이스 | 1시간 |
| `POST /workspaces/:wsId/billing/subscriptions` | 3회/워크스페이스 | 1시간 |
| `POST /workspaces/:wsId/billing/subscriptions/:id/cancel` | 3회/워크스페이스 | 1시간 |
| `POST /workspaces/:wsId/billing/invoices/:id/pay` | 5회/워크스페이스 | 15분 |
| `POST /billing/webhook/*` | 100회 | 1분 |

### 7.6 PCI DSS 준수 사항

| 요구사항 | 적용 방법 |
|---------|----------|
| PAN 비저장 | 카드번호를 서버에 저장하지 않음 (PG사 토큰화 활용) |
| TLS 1.2+ | 모든 PG사 통신에 TLS 1.2 이상 필수 |
| 접근 제어 | 빌링키 복호화 권한을 결제 서비스에만 제한 |
| 로그 관리 | 결제 관련 로그에 민감 데이터 마스킹 |
| 정기 점검 | 암호화 키 분기별 로테이션 권장 |

---

## 8. 디렉토리 구조

### 8.1 신규 추가 파일 구조

```
app/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── billing/
│   │       │   ├── plans/
│   │       │   │   ├── route.ts                    # GET, POST /api/v1/billing/plans
│   │       │   │   └── [id]/route.ts               # GET, PATCH /api/v1/billing/plans/:id
│   │       │   ├── subscriptions/
│   │       │   │   └── route.ts                    # GET (SYSTEM ADMIN) 전체 구독 목록
│   │       │   ├── payments/
│   │       │   │   └── [id]/
│   │       │   │       └── refund/route.ts         # POST .../payments/:id/refund (SYSTEM ADMIN)
│   │       │   └── webhook/
│   │       │       ├── toss/route.ts               # POST /api/v1/billing/webhook/toss
│   │       │       └── kcp/route.ts                # POST /api/v1/billing/webhook/kcp
│   │       └── workspaces/
│   │           └── [workspaceId]/
│   │               └── billing/
│   │                   ├── payment-methods/
│   │                   │   ├── route.ts            # GET, POST .../billing/payment-methods
│   │                   │   └── [id]/
│   │                   │       ├── route.ts        # DELETE .../payment-methods/:id
│   │                   │       └── default/route.ts # PATCH .../payment-methods/:id/default
│   │                   ├── subscriptions/
│   │                   │   ├── route.ts            # POST .../billing/subscriptions (구독 시작)
│   │                   │   ├── current/route.ts    # GET .../subscriptions/current
│   │                   │   └── [id]/
│   │                   │       ├── plan/route.ts   # PATCH .../subscriptions/:id/plan
│   │                   │       ├── cancel/route.ts # POST .../subscriptions/:id/cancel
│   │                   │       ├── pause/route.ts  # POST .../subscriptions/:id/pause
│   │                   │       └── resume/route.ts # POST .../subscriptions/:id/resume
│   │                   ├── invoices/
│   │                   │   ├── route.ts            # GET .../billing/invoices
│   │                   │   └── [id]/
│   │                   │       ├── route.ts        # GET .../invoices/:id
│   │                   │       └── pay/route.ts    # POST .../invoices/:id/pay
│   │                   └── credits/
│   │                       ├── me/
│   │                       │   ├── route.ts               # GET /credits/me
│   │                       │   └── history/route.ts       # GET /credits/me/history
│   │                       ├── check/route.ts             # GET /credits/check
│   │                       ├── deduct/route.ts            # POST /credits/deduct
│   │                       ├── members/route.ts           # GET /credits/members
│   │                       └── [userId]/
│   │                           └── adjust/route.ts        # POST /credits/:userId/adjust
│   ├── [locale]/
│   │   ├── pricing/page.tsx                        # 요금제 안내 (Public)
│   │   ├── workspaces/
│   │   │   └── [workspaceId]/
│   │   │       └── billing/
│   │   │           ├── payment-method/page.tsx     # 워크스페이스 결제 수단 관리
│   │   │           ├── subscription/page.tsx       # 워크스페이스 구독 관리
│   │   │           ├── invoices/
│   │   │           │   ├── page.tsx                # 결제 내역 목록
│   │   │           │   └── [id]/page.tsx           # 결제 내역 상세
│   │   │           ├── credits/page.tsx            # 멤버별 크레딧 관리 (OWNER/ADMIN)
│   │   │           └── payment-failed/page.tsx     # 결제 실패 안내
│   │   └── admin/
│   │       └── settings/
│   │           ├── plans/
│   │           │   ├── page.tsx                    # 플랜 관리 (SYSTEM ADMIN)
│   │           │   └── [id]/page.tsx               # 플랜 생성/수정
│   │           └── subscriptions/page.tsx          # 구독 현황 대시보드 (SYSTEM ADMIN)
│   └── actions/
│       └── billing.ts                              # Server Actions (결제 관련)
├── lib/
│   ├── db/
│   │   └── schema/
│   │       ├── auth.ts                             # (기존) 인증 스키마
│   │       ├── workspace.ts                        # (기존) 워크스페이스 스키마
│   │       ├── billing.ts                          # (신규) 결제 스키마
│   │       └── index.ts                            # 스키마 re-export (workspace, billing 추가)
│   ├── billing/
│   │   ├── crypto.ts                               # 빌링키 암호화/복호화 유틸
│   │   ├── proration.ts                            # 비례 배분 계산 유틸
│   │   ├── invoice-generator.ts                    # 청구서 생성 로직
│   │   ├── subscription-manager.ts                 # 구독 상태 관리 로직
│   │   ├── credit-manager.ts                       # (신규) 크레딧 관리 핵심 로직
│   │   ├── credit-guard.ts                         # (신규) 크레딧 차단 미들웨어
│   │   ├── dunning-manager.ts                      # Dunning 재시도 관리
│   │   ├── scheduler.ts                            # 정기결제 Cron 스케줄러
│   │   └── pg/
│   │       ├── types.ts                            # PG 추상화 인터페이스
│   │       ├── factory.ts                          # PG 어댑터 팩토리
│   │       ├── toss-adapter.ts                     # 토스페이먼츠 구현체
│   │       ├── kcp-adapter.ts                      # NHN KCP 구현체
│   │       └── error-mapper.ts                     # PG 에러 코드 매핑
│   └── validations/
│       ├── auth.ts                                 # (기존)
│       ├── billing.ts                              # (신규) 결제 Zod 스키마
│       └── index.ts
├── contexts/
│   ├── AuthContext.tsx                              # (기존)
│   └── WorkspaceSubscriptionContext.tsx             # (신규) 워크스페이스 구독 상태 관리
├── hooks/
│   ├── useAuth.ts                                  # (기존)
│   ├── useWorkspaceSubscription.ts                  # 워크스페이스 구독 정보 훅
│   ├── useWorkspacePaymentMethod.ts                 # 워크스페이스 결제 수단 관리 훅
│   └── useWorkspaceCredit.ts                        # (신규) 크레딧 조회 훅
└── components/
    └── billing/
        ├── PricingCard.tsx                         # 플랜 카드 컴포넌트
        ├── PlanComparisonTable.tsx                  # 플랜 비교 테이블
        ├── PaymentMethodCard.tsx                    # 결제 수단 카드
        ├── SubscriptionStatusBadge.tsx              # 구독 상태 뱃지
        ├── InvoiceTable.tsx                         # 청구서 테이블
        ├── PlanChangeModal.tsx                      # 플랜 변경 모달
        ├── CancelSubscriptionModal.tsx              # 구독 해지 모달
        ├── PaymentFailedBanner.tsx                  # 결제 실패 배너
        ├── CreditUsageBadge.tsx                     # (신규) 크레딧 사용률 배지
        └── CreditExhaustedBanner.tsx                # (신규) 크레딧 소진 배너
```

### 8.2 WorkspaceSubscriptionContext 설계

```typescript
// contexts/WorkspaceSubscriptionContext.tsx
interface WorkspaceSubscriptionInfo {
  id: number;
  workspaceId: number;
  planId: number;
  planName: string;
  statusCd: string;
  currentPeriodStart: string;
  currentPeriodEnd: string;
  cancelAtPeriodEnd: boolean;
  features: Record<string, string>;
}

interface WorkspaceSubscriptionContextType {
  /** 현재 워크스페이스의 구독 정보 */
  subscription: WorkspaceSubscriptionInfo | null;
  isLoading: boolean;
  hasActiveSubscription: boolean;
  isTrialing: boolean;
  isPastDue: boolean;
  /** 현재 사용자가 결제 관리 권한(OWNER/ADMIN)을 가졌는지 */
  canManageBilling: boolean;
  /** 구독 정보 새로고침 */
  refreshSubscription: () => Promise<void>;
  /** 플랜 기능 제한 확인 (워크스페이스 전체에 적용) */
  checkFeature: (featureKey: string) => string | null;

  /** 크레딧 관련 */
  credit: {
    balance: CreditBalanceInfo | null;
    isUnlimited: boolean;
    isExhausted: boolean;
    usageRate: number;
    remainingCredits: number;
  } | null;
  /** 크레딧 잔액 새로고침 */
  refreshCredit: () => Promise<void>;
  /** 크레딧 사용 가능 여부 확인 */
  checkCredit: (amount: number) => boolean;
}
```

### 8.3 useWorkspaceCredit 훅 설계

```typescript
// hooks/useWorkspaceCredit.ts
function useWorkspaceCredit(workspaceId: number) {
  return {
    balance: CreditBalanceInfo | null;
    history: CreditTransaction[];
    isLoading: boolean;
    isExhausted: boolean;
    isUnlimited: boolean;
    usageRate: number;
    deductCredit: (amount: number, ref?: CreditReference) => Promise<DeductResult>;
    checkAvailability: (amount: number) => Promise<boolean>;
    refreshBalance: () => Promise<void>;
  };
}
```

### 8.4 credit-manager.ts 서비스 설계

```typescript
// lib/billing/credit-manager.ts
interface CreditManager {
  /** 빌링 기간 시작 시 워크스페이스 전체 멤버에게 크레딧 할당 */
  allocateCreditsForPeriod(workspaceId: number, subscriptionId: number, periodStart: Date, periodEnd: Date): Promise<void>;

  /** 특정 멤버에게 크레딧 할당 (중도 가입 시 비례 배분) */
  allocateCreditsForMember(workspaceId: number, userId: number, subscriptionId: number): Promise<CreditBalance>;

  /** 크레딧 차감 (트랜잭션 내 원자적 처리) */
  deductCredits(workspaceId: number, userId: number, amount: number, reference?: CreditReference): Promise<CreditTransaction>;

  /** 크레딧 잔액 확인 */
  checkCreditAvailability(workspaceId: number, userId: number, requiredAmount: number): Promise<CreditCheckResult>;

  /** 현재 빌링 기간의 크레딧 잔액 조회 */
  getCurrentBalance(workspaceId: number, userId: number): Promise<CreditBalance | null>;

  /** 플랜 변경 시 크레딧 재조정 */
  adjustCreditsForPlanChange(workspaceId: number, newPlanCredits: number): Promise<void>;

  /** 빌링 기간 만료 시 크레딧 만료 처리 */
  expireCreditsForPeriod(workspaceId: number, periodEndDate: Date): Promise<void>;

  /** 멤버 탈퇴 시 크레딧 만료 처리 */
  expireCreditsForMember(workspaceId: number, userId: number): Promise<void>;
}
```

**크레딧 차감 원자성** (PostgreSQL SELECT FOR UPDATE):
```typescript
async deductCredits(wkspcId, userId, amount, ref) {
  return await db.transaction(async (tx) => {
    // 1. SELECT FOR UPDATE로 현재 잔액 조회 (동시성 제어)
    const balance = await tx.select()
      .from(creditBalances)
      .where(and(
        eq(creditBalances.wkspcId, wkspcId),
        eq(creditBalances.userId, userId),
        eq(creditBalances.sttsCd, 'ACTIVE')
      ))
      .for('update')
      .limit(1);

    // 2. 잔액 부족 검사
    if (!balance || balance.rmnnQty < amount) {
      throw new CreditExhaustedException();
    }

    // 3. 잔액 업데이트
    const newUsed = balance.usedQty + amount;
    const newRemaining = balance.rmnnQty - amount;
    const newStatus = newRemaining === 0 ? 'EXHAUSTED' : 'ACTIVE';

    await tx.update(creditBalances)
      .set({ usedQty: newUsed, rmnnQty: newRemaining, sttsCd: newStatus, mdfcnDt: new Date() })
      .where(eq(creditBalances.id, balance.id));

    // 4. 거래 로그 기록
    await tx.insert(creditTransactions).values({...});

    // 5. 빌링 이벤트 기록
    await tx.insert(billingEvents).values({
      evntTypeCd: 'credit.deducted',
      enttyTypeCd: 'credit_balance',
      enttyId: balance.id,
      ...
    });
  });
}
```

### 8.5 credit-guard.ts 서비스 설계

```typescript
// lib/billing/credit-guard.ts
/** 크레딧 가드 - 크레딧 필요 API에 적용 */
export async function withCreditGuard(
  handler: NextApiHandler,
  options: { requiredCredits: number }
): NextApiHandler {
  return async (req, res) => {
    const { workspaceId, userId } = extractContext(req);
    const result = await creditManager.checkCreditAvailability(
      workspaceId, userId, options.requiredCredits
    );

    if (!result.available) {
      return res.status(403).json({
        error: {
          code: 'CREDIT_EXHAUSTED',
          message: '크레딧이 소진되었습니다. 다음 결제 주기까지 기다리거나 상위 플랜으로 업그레이드하세요.',
          details: {
            remaining: result.remaining,
            required: options.requiredCredits,
            period_end: result.periodEnd,
          }
        }
      });
    }

    return handler(req, res);
  };
}
```

### 8.6 Zod 검증 스키마 (`lib/validations/billing.ts` 추가)

```typescript
// 크레딧 관련 Zod 스키마
export const deductCreditSchema = z.object({
  amount: z.number().int().positive().max(10000),
  reference_type: z.string().max(50).optional(),
  reference_id: z.number().int().positive().optional(),
  description: z.string().max(500).optional(),
});

export const adjustCreditSchema = z.object({
  amount: z.number().int(),  // 양수: 추가, 음수: 차감
  reason: z.string().min(1).max(500),
});

export const checkCreditSchema = z.object({
  amount: z.number().int().positive(),
});
```

---

## 9. 구현 순서

### Phase 1: 기반 인프라 (1주차)

| 순서 | 작업 | 파일 |
|------|------|------|
| 1-1 | 의존성 설치 | `package.json` |
| 1-2 | 환경 변수 추가 | `.env.local` |
| 1-3 | DB 스키마 정의 (Drizzle) | `lib/db/schema/billing.ts` |
| 1-4 | DB 마이그레이션 실행 | DDL 전문 적용 |
| 1-5 | 빌링키 암호화 유틸 | `lib/billing/crypto.ts` |
| 1-6 | 비례 배분 계산 유틸 | `lib/billing/proration.ts` |
| 1-7 | Zod 검증 스키마 | `lib/validations/billing.ts` |
| 1-8 | PG 추상화 인터페이스 | `lib/billing/pg/types.ts` |

### Phase 2: PG 연동 + 결제 수단 (2주차)

| 순서 | 작업 | 파일 |
|------|------|------|
| 2-1 | 토스페이먼츠 어댑터 | `lib/billing/pg/toss-adapter.ts` |
| 2-2 | PG 어댑터 팩토리 | `lib/billing/pg/factory.ts` |
| 2-3 | PG 에러 코드 매핑 | `lib/billing/pg/error-mapper.ts` |
| 2-4 | 결제 수단 목록 API | `app/api/v1/billing/payment-methods/route.ts` |
| 2-5 | 결제 수단 등록 API | `app/api/v1/billing/payment-methods/route.ts` |
| 2-6 | 결제 수단 삭제/기본 설정 API | `app/api/v1/billing/payment-methods/[id]/...` |
| 2-7 | 웹훅 수신 핸들러 | `app/api/v1/billing/webhook/toss/route.ts` |

### Phase 3: 구독 관리 (3주차)

| 순서 | 작업 | 파일 |
|------|------|------|
| 3-1 | 플랜 CRUD API | `app/api/v1/billing/plans/...` |
| 3-2 | 구독 시작 API | `app/api/v1/billing/subscriptions/route.ts` |
| 3-3 | 내 구독 조회 API | `app/api/v1/billing/subscriptions/me/route.ts` |
| 3-4 | 플랜 변경 API (비례 배분) | `app/api/v1/billing/subscriptions/[id]/plan/route.ts` |
| 3-5 | 구독 해지 API | `app/api/v1/billing/subscriptions/[id]/cancel/route.ts` |
| 3-6 | 구독 일시정지/재개 API | `app/api/v1/billing/subscriptions/[id]/pause, resume` |
| 3-7 | 청구서 생성 로직 | `lib/billing/invoice-generator.ts` |
| 3-8 | 구독 상태 관리 로직 | `lib/billing/subscription-manager.ts` |

### Phase 3.5: 크레딧 관리

| 순서 | 작업 | 파일 |
|------|------|------|
| 3.5-1 | DB 스키마 추가 (Drizzle) | `lib/db/schema/billing.ts` |
| 3.5-2 | DB 마이그레이션 실행 | DDL 적용 |
| 3.5-3 | Zod 검증 스키마 추가 | `lib/validations/billing.ts` |
| 3.5-4 | 크레딧 매니저 서비스 | `lib/billing/credit-manager.ts` |
| 3.5-5 | 크레딧 가드 미들웨어 | `lib/billing/credit-guard.ts` |
| 3.5-6 | 내 크레딧 조회 API | `app/api/.../credits/me/route.ts` |
| 3.5-7 | 크레딧 사용 내역 API | `app/api/.../credits/me/history/route.ts` |
| 3.5-8 | 크레딧 확인/차감 API | `app/api/.../credits/check, deduct` |
| 3.5-9 | 멤버별 크레딧 조회/조정 API | `app/api/.../credits/members, [userId]/adjust` |
| 3.5-10 | 구독 생성/갱신 시 크레딧 할당 연동 | `lib/billing/subscription-manager.ts` 수정 |
| 3.5-11 | 스케줄러 크레딧 리셋 연동 | `lib/billing/scheduler.ts` 수정 |
| 3.5-12 | 멤버 가입/탈퇴 시 크레딧 연동 | 워크스페이스 모듈 연동 |
| 3.5-13 | useWorkspaceCredit 훅 | `hooks/useWorkspaceCredit.ts` |
| 3.5-14 | Context 확장 | `contexts/WorkspaceSubscriptionContext.tsx` |
| 3.5-15 | 크레딧 UI 컴포넌트 | `components/billing/CreditUsageBadge.tsx`, `CreditExhaustedBanner.tsx` |
| 3.5-16 | 크레딧 관리 페이지 | `app/[locale]/.../billing/credits/page.tsx` |
| 3.5-17 | Seed 데이터 | `monthly_credits` plan feature 추가 |

### Phase 4: 스케줄러 + Dunning (4주차)

| 순서 | 작업 | 파일 |
|------|------|------|
| 4-1 | 정기결제 스케줄러 | `lib/billing/scheduler.ts` |
| 4-2 | Dunning 매니저 | `lib/billing/dunning-manager.ts` |
| 4-3 | 청구서 목록/상세 API | `app/api/v1/billing/invoices/...` |
| 4-4 | 수동 결제 API | `app/api/v1/billing/invoices/[id]/pay/route.ts` |
| 4-5 | 환불 API | `app/api/v1/billing/payments/[id]/refund/route.ts` |
| 4-6 | WorkspaceSubscriptionContext | `contexts/WorkspaceSubscriptionContext.tsx` |
| 4-7 | 구독/결제 Hooks | `hooks/useWorkspaceSubscription.ts`, `hooks/useWorkspacePaymentMethod.ts` |

### Phase 5: 화면 구현 (5주차)

| 순서 | 작업 | 파일 |
|------|------|------|
| 5-1 | 요금제 안내 페이지 | `app/[locale]/pricing/page.tsx` |
| 5-2 | 결제 수단 관리 페이지 | `app/[locale]/workspaces/[workspaceId]/billing/payment-method/page.tsx` |
| 5-3 | 구독 관리 페이지 | `app/[locale]/workspaces/[workspaceId]/billing/subscription/page.tsx` |
| 5-4 | 결제 내역 페이지 | `app/[locale]/workspaces/[workspaceId]/billing/invoices/page.tsx`, `[id]/page.tsx` |
| 5-5 | 결제 실패 안내 페이지 | `app/[locale]/workspaces/[workspaceId]/billing/payment-failed/page.tsx` |
| 5-6 | 공통 컴포넌트 | `components/billing/*.tsx` |
| 5-7 | 플랜 변경/해지 모달 | `PlanChangeModal.tsx`, `CancelSubscriptionModal.tsx` |

### Phase 6: 관리자 + 통합 테스트 (6주차)

| 순서 | 작업 |
|------|------|
| 6-1 | 플랜 관리 페이지 (ADMIN) |
| 6-2 | 구독 현황 대시보드 (ADMIN) |
| 6-3 | 다국어 메시지 추가 (`messages/ko.json`, `messages/en.json`) |
| 6-4 | Rate Limiting 적용 |
| 6-5 | 통합 테스트 (결제 시나리오별) |
| 6-6 | 토스페이먼츠 테스트 키 기반 E2E 테스트 |

---

## 부록: 초기 데이터 (Seed)

```sql
-- 기본 구독 플랜
INSERT INTO app.TB_PAY_PLAN (PLAN_NM, PLAN_DC, BILNG_INTRVL_CD, INTRVL_CNT, PLAN_AMT, CRNC_CD, TRIAL_DAY_CNT, SORT_SN, ACTV_YN) VALUES
('Basic', '개인 사용자를 위한 기본 플랜', 'MONTHLY', 1, 9900, 'KRW', 14, 1, 'Y'),
('Pro', '팀을 위한 프로 플랜', 'MONTHLY', 1, 29900, 'KRW', 14, 2, 'Y'),
('Enterprise', '기업을 위한 엔터프라이즈 플랜', 'MONTHLY', 1, 99000, 'KRW', 0, 3, 'Y'),
('Basic (연간)', '개인 사용자를 위한 기본 플랜 (연간)', 'YEARLY', 1, 95000, 'KRW', 14, 4, 'Y'),
('Pro (연간)', '팀을 위한 프로 플랜 (연간)', 'YEARLY', 1, 287000, 'KRW', 14, 5, 'Y');

-- Basic 플랜 기능 (워크스페이스 단위 제한)
INSERT INTO app.TB_PAY_PLAN_FNC (PLAN_ID, FNC_KEY, FNC_VL) VALUES
(1, 'max_members', '5'),
(1, 'max_projects', '3'),
(1, 'storage_gb', '10'),
(1, 'support_level', 'email');

-- Pro 플랜 기능 (워크스페이스 단위 제한)
INSERT INTO app.TB_PAY_PLAN_FNC (PLAN_ID, FNC_KEY, FNC_VL) VALUES
(2, 'max_members', '25'),
(2, 'max_projects', 'unlimited'),
(2, 'storage_gb', '100'),
(2, 'support_level', 'priority'),
(2, 'api_access', 'true');

-- Enterprise 플랜 기능 (워크스페이스 단위 제한)
INSERT INTO app.TB_PAY_PLAN_FNC (PLAN_ID, FNC_KEY, FNC_VL) VALUES
(3, 'max_members', 'unlimited'),
(3, 'max_projects', 'unlimited'),
(3, 'storage_gb', 'unlimited'),
(3, 'support_level', 'dedicated'),
(3, 'api_access', 'true'),
(3, 'sso_saml', 'true'),
(3, 'sla_guarantee', 'true');

-- 플랜별 월간 크레딧 할당량 (멤버당)
INSERT INTO app.TB_PAY_PLAN_FNC (PLAN_ID, FNC_KEY, FNC_VL, FNC_DC) VALUES
(1, 'monthly_credits', '100', '월간 크레딧 할당량 (멤버당)'),
(2, 'monthly_credits', '500', '월간 크레딧 할당량 (멤버당)'),
(3, 'monthly_credits', 'unlimited', '월간 크레딧 할당량 (멤버당, 무제한)'),
(4, 'monthly_credits', '100', '월간 크레딧 할당량 (멤버당, 연간)'),
(5, 'monthly_credits', '500', '월간 크레딧 할당량 (멤버당, 연간)');
```
