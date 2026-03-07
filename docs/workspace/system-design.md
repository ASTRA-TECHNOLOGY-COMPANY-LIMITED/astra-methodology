# 워크스페이스 관리 시스템 설계 문서

> **프로젝트**: 공통 워크스페이스 관리 모듈 (Workspace Management Module)
> **버전**: 1.1.0
> **작성일**: 2026-02-14
> **최종 수정일**: 2026-02-14 (멤버 가입/탈퇴 시 크레딧 생명주기 연동 추가)
> **기반 레퍼런스**: Slack Workspaces, Notion Teamspaces, Vercel Teams, Linear Workspaces

---

## 목차

1. [아키텍처 개요](#1-아키텍처-개요)
2. [기술 스택](#2-기술-스택)
3. [데이터베이스 스키마](#3-데이터베이스-스키마)
4. [API 설계](#4-api-설계)
5. [화면 구성](#5-화면-구성)
6. [유즈케이스 및 데이터 플로우](#6-유즈케이스-및-데이터-플로우)
7. [보안 설계](#7-보안-설계)
8. [디렉토리 구조](#8-디렉토리-구조)
9. [구현 순서](#9-구현-순서)

---

## 1. 아키텍처 개요

### 1.1 설계 원칙

워크스페이스는 시스템의 **멀티테넌시(Multi-tenancy) 핵심 단위**이다. 사용자(User)는 여러 워크스페이스에 소속될 수 있으며, 워크스페이스 단위로 구독·결제·권한·데이터가 격리된다.

**핵심 설계 원칙**:
- **멀티 워크스페이스 멤버십**: 한 사용자가 여러 워크스페이스에 동시 소속 가능 (Slack/Notion 모델)
- **워크스페이스 = 과금 주체**: 구독·결제·청구의 단위는 워크스페이스이며, 개별 사용자가 아님
- **워크스페이스 역할 분리**: 시스템 레벨 역할(IAM `ADMIN/MANAGER/USER`)과 워크스페이스 레벨 역할(`OWNER/ADMIN/MEMBER/GUEST`)을 분리하여 관리
- **자동 개인 워크스페이스**: 회원가입 시 개인 워크스페이스를 자동 생성하여 즉시 서비스 이용 가능
- **초대 기반 멤버 관리**: 이메일 초대 및 초대 링크를 통한 멤버 추가, 만료·취소 관리

### 1.2 아키텍처 다이어그램

```
┌──────────────────────────────────────────────────────────────────┐
│                    APP (Next.js 14)                                │
│                                                                    │
│  ┌──────────────────┐    ┌────────────────────────────────────┐  │
│  │   Client-Side     │    │           Server-Side               │  │
│  │                   │    │                                      │  │
│  │  WorkspaceSwitcher│───▶│  API Routes (/api/v1/workspaces/..) │  │
│  │  WorkspaceContext │    │  Workspace Membership Middleware     │  │
│  │  InvitationFlow   │    │  Workspace Role Guard               │  │
│  │  MemberManager    │◀───│  Invitation Service                 │  │
│  └──────────────────┘    └──────────┬─────────────────────────┘  │
│                                      │                            │
└──────────────────────────────────────┼────────────────────────────┘
                                       │
                       ┌───────────────┼───────────────────┐
                       ▼               ▼                   ▼
                ┌────────────┐  ┌────────────┐     ┌────────────┐
                │ PostgreSQL  │  │   SMTP      │     │  Redis     │
                │ (Drizzle)   │  │  (초대 메일) │     │  (캐시)    │
                └────────────┘  └────────────┘     └────────────┘
```

### 1.3 타 모듈과의 관계

```
┌───────────┐     ┌──────────────────┐     ┌───────────────┐
│  인증 모듈  │────▶│  워크스페이스 모듈  │◀────│  결제 모듈     │
│ (Auth)     │     │  (Workspace)      │     │ (Payment)     │
│            │     │                    │     │               │
│TB_COMM_USER│     │ TB_COMM_WKSPC     │     │ pay_subscrip- │
│ JWT 토큰   │     │ TR_COMM_WKSPC_    │     │   tions       │
│ 회원가입    │     │   MBR              │     │ pay_payment_  │
│            │     │ TB_COMM_WKSPC_    │     │   methods     │
│            │     │   INVT             │     │               │
└───────────┘     └──────────┬─────────┘     └───────────────┘
                              │
                              │
                    ┌─────────▼─────────┐
                    │   IAM 모듈         │
                    │ (Permission)       │
                    │                    │
                    │ 워크스페이스 리소스  │
                    │ 권한 검사           │
                    │ workspace.*:action │
                    └────────────────────┘
```

| 항목 | 인증 모듈 | 워크스페이스 모듈 | IAM 모듈 | 결제 모듈 |
|------|----------|-----------------|----------|----------|
| 사용자 식별 | `TB_COMM_USER.ID` | `TR_COMM_WKSPC_MBR.USER_ID` FK 참조 | `TB_COMM_USER.ID` FK 참조 | `TB_COMM_USER.ID` FK 참조 |
| 워크스페이스 식별 | - | `TB_COMM_WKSPC.ID` 정의 | 권한 검사 시 워크스페이스 컨텍스트 참조 | `WKSPC_ID` FK 참조 |
| 역할 체계 | `TB_COMM_USER.ROLE_CD` (시스템) | `TR_COMM_WKSPC_MBR.ROLE_CD` (워크스페이스) | 시스템 IAM 역할 + 워크스페이스 역할 이중 체계 | 워크스페이스 `OWNER/ADMIN`만 결제 관리 |
| 트리거 이벤트 | 회원가입 → 워크스페이스 생성 | 초대 수락 → 멤버 추가 | 역할 변경 → 감사 로그 | 구독 생성 → 워크스페이스 플랜 반영 |
| DB 스키마 | `app` 스키마 | 동일 `app` 스키마 내 워크스페이스 테이블 추가 | 동일 `app` 스키마 | 동일 `app` 스키마 |

### 1.4 워크스페이스 역할 vs 시스템 역할

워크스페이스 역할과 시스템(IAM) 역할은 **독립적인 차원**으로 운영된다.

| 구분 | 시스템 역할 (IAM) | 워크스페이스 역할 |
|------|------------------|----------------|
| 관리 위치 | `iam_roles` + `iam_user_roles` | `TR_COMM_WKSPC_MBR.ROLE_CD` |
| 적용 범위 | 시스템 전체 관리 기능 | 특정 워크스페이스 내 |

| 역할 종류 | `ADMIN`, `MANAGER`, `USER` 등 | `OWNER`, `ADMIN`, `MEMBER`, `GUEST` |
| 용도 | 시스템 관리 페이지 접근 (사용자 관리, 약관 관리, IAM 관리 등) | 워크스페이스 내 멤버 관리, 설정, 결제, 데이터 접근 |
| 예시 | 시스템 ADMIN이 전체 사용자 목록 조회 | 워크스페이스 OWNER가 해당 워크스페이스 구독 관리 |

> **권한 검사 흐름**: 시스템 관리 API → IAM 권한 검사 / 워크스페이스 API → 워크스페이스 멤버십 + 워크스페이스 역할 검사

---

## 2. 기술 스택

### 2.1 신규 추가 의존성

```json
{
  "dependencies": {
    "nanoid": "^5.x",
    "slugify": "^1.x"
  }
}
```

| 패키지 | 용도 |
|--------|------|
| `nanoid` | 초대 토큰, 초대 링크 코드 생성 |
| `slugify` | 워크스페이스 이름 → URL 슬러그 변환 |

> 기존 `drizzle-orm`, `jose`, `zod`, `nodemailer`(SMTP) 등은 인증 모듈에서 이미 설치되어 재사용한다.

### 2.2 환경 변수

```env
# Workspace
WORKSPACE_DEFAULT_MAX_MEMBERS=5              # 무료 플랜 기본 멤버 수 제한
WORKSPACE_INVITATION_EXPIRY_HOURS=168        # 초대 만료 시간 (7일 = 168시간)
WORKSPACE_INVITE_LINK_EXPIRY_HOURS=720       # 초대 링크 만료 시간 (30일)
WORKSPACE_MAX_PER_USER=10                    # 사용자당 최대 워크스페이스 소유 수

# Invitation Email
SMTP_FROM_NAME=YourApp
SMTP_FROM_EMAIL=noreply@astravision.co.kr
```

---

## 3. 데이터베이스 스키마

### 3.1 ER 다이어그램

```
┌──────────────────┐
│   TB_COMM_USER    │
│   (인증 모듈)      │
│                   │
│ ID (PK)          │
│ UID              │
│ EML_ADDR         │
│ DSPLY_NM         │
│ BSC_WKSPC_ID ◀───┼─────────────────────────────┐
└──────┬───────────┘                              │
       │                                          │
       │  1:N                                     │
       │                                          │
       ▼                                          │
┌──────────────────────┐                          │
│ TR_COMM_WKSPC_MBR     │     ┌──────────────────┤
│                       │     │                  │
├──────────────────────┤     │                  │
│ ID (PK)              │     │  ┌───────────────┴──────────┐
│ WKSPC_ID (FK) ───────┼─────┼─▶│ TB_COMM_WKSPC              │
│ USER_ID (FK)         │     │  ├────────────────────────────┤
│ ROLE_CD              │     │  │ ID (PK)                    │
│ STTS_CD              │     │  │ SLUG (UK)                  │
│ JOIN_DT              │     │  │ WKSPC_NM                   │
│ INVTR_ID             │     │  │ WKSPC_DC                   │
│ WHDWL_DT             │     │  │ LOGO_URL                   │
└──────────────────────┘     │  │ OWNR_ID (FK → TB_COMM_USER)│
                              │  │ TYPE_CD (PERSONAL/TEAM)    │
┌──────────────────────┐     │  │ MAX_MBR_CNT                │
│ TB_COMM_WKSPC_INVT    │     │  │ STTS_CD                    │
│                       │     │  │ STNG (JSONB)               │
├──────────────────────┤     │  │ DEL_DT                     │
│ ID (PK)              │     │  └────────────────────────────┘
│ WKSPC_ID (FK) ───────┼─────┘
│ EML_ADDR             │        ┌────────────────────────────┐
│ ROLE_CD              │        │ TB_PAY_SBSC           │
│ TKN (UK)             │        │ (결제 모듈)                  │
│ INVT_TYPE_CD         │        │                             │
│ INVTR_ID (FK)        │        │ WKSPC_ID (FK) ─────────────│
│ STTS_CD              │        │ → TB_COMM_WKSPC.ID          │
│ EXPRY_DT             │        └────────────────────────────┘
│ ACPT_DT              │
│ ACPTR_ID (FK)        │
└──────────────────────┘
```

### 3.2 TB_COMM_WKSPC 테이블

워크스페이스 정보를 관리하는 핵심 테이블.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 워크스페이스 고유 식별자 |
| `SLUG` | `VARCHAR(100)` | `UNIQUE NOT NULL` | - | URL 슬러그 (예: `my-team`, `acme-corp`) |
| `WKSPC_NM` | `VARCHAR(100)` | `NOT NULL` | - | 워크스페이스 이름 (표시용) |
| `WKSPC_DC` | `VARCHAR(500)` | - | NULL | 워크스페이스 설명 |
| `LOGO_URL` | `VARCHAR(2000)` | - | NULL | 로고 이미지 URL |
| `OWNR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID) NOT NULL` | - | 소유자 FK |
| `TYPE_CD` | `VARCHAR(20)` | `NOT NULL` | `'TEAM'` | 워크스페이스 유형 코드 |
| `MAX_MBR_CNT` | `INTEGER` | `NOT NULL` | `5` | 최대 멤버 수 (플랜 연동) |
| `STTS_CD` | `VARCHAR(20)` | `NOT NULL` | `'ACTIVE'` | 워크스페이스 상태 코드 |
| `STNG` | `JSONB` | `NOT NULL` | `'{}'` | 워크스페이스 설정 |
| `DEL_DT` | `TIMESTAMPTZ` | - | NULL | Soft Delete 일시 |
| `CRTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 생성자 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 생성 일시 |
| `MDFR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 수정자 |
| `MDFCN_DT` | `TIMESTAMPTZ` | - | NULL | 수정 일시 |

**인덱스**:
```sql
CREATE UNIQUE INDEX idx_TB_COMM_WKSPC_SLUG ON app.TB_COMM_WKSPC(SLUG);
CREATE INDEX idx_TB_COMM_WKSPC_OWNR ON app.TB_COMM_WKSPC(OWNR_ID);
CREATE INDEX idx_TB_COMM_WKSPC_STTS ON app.TB_COMM_WKSPC(STTS_CD);
```

**Enum 값**:

| 코드 유형 | 코드 | 한글명 | 설명 |
|-----------|------|--------|------|
| `WORKSPACE_TYPE` | `PERSONAL` | 개인 | 회원가입 시 자동 생성, 소유자 1명 전용 |
| | `TEAM` | 팀 | 여러 멤버가 협업하는 팀 워크스페이스 |
| `WORKSPACE_STATUS` | `ACTIVE` | 활성 | 정상 사용 중 |
| | `SUSPENDED` | 정지 | 결제 실패 등으로 정지 |
| | `DELETED` | 삭제 | Soft Delete |

**STNG JSONB 구조 예시**:
```json
{
  "default_locale": "ko",
  "notification_email": true,
  "allow_member_invite": false,
  "require_approval": false
}
```

### 3.3 TR_COMM_WKSPC_MBR 테이블

워크스페이스 멤버십(사용자-워크스페이스 매핑)을 관리하는 테이블. N:M 관계.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 멤버 식별자 |
| `WKSPC_ID` | `BIGINT` | `FK(TB_COMM_WKSPC.ID) ON DELETE CASCADE, NOT NULL` | - | 워크스페이스 FK |
| `USER_ID` | `BIGINT` | `FK(TB_COMM_USER.ID) ON DELETE CASCADE, NOT NULL` | - | 사용자 FK |
| `ROLE_CD` | `VARCHAR(20)` | `NOT NULL` | `'MEMBER'` | 워크스페이스 역할 코드 |
| `STTS_CD` | `VARCHAR(20)` | `NOT NULL` | `'ACTIVE'` | 멤버 상태 코드 |
| `INVTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 초대한 사용자 FK |
| `JOIN_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 가입(참여) 일시 |
| `WHDWL_DT` | `TIMESTAMPTZ` | - | NULL | 탈퇴 일시 |
| `CRTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 생성자 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 생성 일시 |
| `MDFR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 수정자 |
| `MDFCN_DT` | `TIMESTAMPTZ` | - | NULL | 수정 일시 |

**제약조건**:
```sql
CONSTRAINT uq_TR_COMM_WKSPC_MBR_ws_user UNIQUE (WKSPC_ID, USER_ID)
```

**인덱스**:
```sql
CREATE INDEX idx_TR_COMM_WKSPC_MBR_ws ON app.TR_COMM_WKSPC_MBR(WKSPC_ID, STTS_CD);
CREATE INDEX idx_TR_COMM_WKSPC_MBR_user ON app.TR_COMM_WKSPC_MBR(USER_ID, STTS_CD);
```

**Enum 값**:

| 코드 유형 | 코드 | 한글명 | 설명 |
|-----------|------|--------|------|
| `WS_ROLE` | `OWNER` | 소유자 | 워크스페이스 소유자 (1명, 양도 가능). 결제·삭제·소유권 이전 모든 권한 |
| | `ADMIN` | 관리자 | 멤버 관리, 설정 변경, 결제 관리 권한 |
| | `MEMBER` | 멤버 | 일반 멤버. 워크스페이스 기능 사용 가능 |
| | `GUEST` | 게스트 | 제한된 접근. 초대된 특정 리소스만 접근 가능 |
| `WS_MEMBER_STATUS` | `ACTIVE` | 활성 | 정상 활동 중 |
| | `SUSPENDED` | 정지 | 관리자에 의해 정지 |
| | `LEFT` | 탈퇴 | 자발적 탈퇴 또는 강제 퇴장 |

**워크스페이스 역할별 권한 매트릭스**:

| 기능 | OWNER | ADMIN | MEMBER | GUEST |
|------|-------|-------|--------|-------|
| 워크스페이스 데이터 조회 | ✓ | ✓ | ✓ | △ (제한적) |
| 워크스페이스 데이터 생성/수정 | ✓ | ✓ | ✓ | ✗ |
| 멤버 초대 | ✓ | ✓ | △ (설정에 따라) | ✗ |
| 멤버 역할 변경 | ✓ | ✓ (MEMBER↔GUEST만) | ✗ | ✗ |
| 멤버 강제 퇴장 | ✓ | ✓ (MEMBER, GUEST만) | ✗ | ✗ |
| 워크스페이스 설정 변경 | ✓ | ✓ | ✗ | ✗ |
| 결제 수단 관리 | ✓ | ✓ | ✗ | ✗ |
| 구독 플랜 변경 | ✓ | ✓ | ✗ | ✗ |
| 워크스페이스 삭제 | ✓ | ✗ | ✗ | ✗ |
| 소유권 이전 | ✓ | ✗ | ✗ | ✗ |
| ADMIN 역할 부여/해제 | ✓ | ✗ | ✗ | ✗ |

### 3.4 TB_COMM_WKSPC_INVT 테이블

워크스페이스 초대를 관리하는 테이블.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 초대 식별자 |
| `WKSPC_ID` | `BIGINT` | `FK(TB_COMM_WKSPC.ID) ON DELETE CASCADE, NOT NULL` | - | 워크스페이스 FK |
| `EML_ADDR` | `VARCHAR(100)` | - | NULL | 초대 대상 이메일 (EMAIL 초대 시) |
| `ROLE_CD` | `VARCHAR(20)` | `NOT NULL` | `'MEMBER'` | 부여할 역할 코드 |
| `INVT_TYPE_CD` | `VARCHAR(20)` | `NOT NULL` | `'EMAIL'` | 초대 유형 |
| `TKN` | `VARCHAR(128)` | `UNIQUE NOT NULL` | - | 초대 토큰 (URL에 사용) |
| `INVTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID) NOT NULL` | - | 초대한 사용자 FK |
| `STTS_CD` | `VARCHAR(20)` | `NOT NULL` | `'PENDING'` | 초대 상태 코드 |
| `MAX_USE_CNT` | `INTEGER` | - | NULL | 최대 사용 횟수 (LINK 초대 시) |
| `USE_CNT` | `INTEGER` | `NOT NULL` | `0` | 사용된 횟수 |
| `EXPRY_DT` | `TIMESTAMPTZ` | `NOT NULL` | - | 초대 만료 일시 |
| `ACPT_DT` | `TIMESTAMPTZ` | - | NULL | 수락 일시 |
| `ACPTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 수락한 사용자 FK |
| `CNCL_DT` | `TIMESTAMPTZ` | - | NULL | 취소 일시 |
| `CRTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 생성자 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 생성 일시 |
| `MDFR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 수정자 |
| `MDFCN_DT` | `TIMESTAMPTZ` | - | NULL | 수정 일시 |

**인덱스**:
```sql
CREATE UNIQUE INDEX idx_TB_COMM_WKSPC_INVT_TKN ON app.TB_COMM_WKSPC_INVT(TKN);
CREATE INDEX idx_TB_COMM_WKSPC_INVT_ws ON app.TB_COMM_WKSPC_INVT(WKSPC_ID, STTS_CD);
CREATE INDEX idx_TB_COMM_WKSPC_INVT_eml ON app.TB_COMM_WKSPC_INVT(EML_ADDR, STTS_CD);
CREATE INDEX idx_TB_COMM_WKSPC_INVT_expry ON app.TB_COMM_WKSPC_INVT(EXPRY_DT);
```

**Enum 값**:

| 코드 유형 | 코드 | 설명 |
|-----------|------|------|
| `INVITE_TYPE` | `EMAIL` | 특정 이메일로 1:1 초대 |
| | `LINK` | 초대 링크 (다수 사용 가능, `MAX_USE_CNT`로 제한) |
| `INVITE_STATUS` | `PENDING` | 초대 발송 완료, 수락 대기 중 |
| | `ACCEPTED` | 수락됨 |
| | `DECLINED` | 거절됨 |
| | `EXPIRED` | 만료됨 |
| | `CANCELED` | 초대자에 의해 취소됨 |

### 3.5 TB_COMM_USER 테이블 확장

인증 모듈의 `TB_COMM_USER` 테이블에 워크스페이스 관련 컬럼을 추가한다.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `BSC_WKSPC_ID` | `BIGINT` | `FK(TB_COMM_WKSPC.ID)` | NULL | 기본(마지막 접속) 워크스페이스 FK |

```sql
ALTER TABLE app.TB_COMM_USER ADD COLUMN BSC_WKSPC_ID BIGINT REFERENCES app.TB_COMM_WKSPC(ID);
```

### 3.6 DDL 전문

```sql
-- ============================================
-- 1. TB_COMM_WKSPC 테이블
-- ============================================
CREATE TABLE app.TB_COMM_WKSPC (
    ID              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    SLUG            VARCHAR(100)    NOT NULL,
    WKSPC_NM        VARCHAR(100)    NOT NULL,
    WKSPC_DC        VARCHAR(500),
    LOGO_URL        VARCHAR(2000),
    OWNR_ID         BIGINT          NOT NULL REFERENCES app.TB_COMM_USER(ID),
    TYPE_CD         VARCHAR(20)     NOT NULL DEFAULT 'TEAM',
    MAX_MBR_CNT     INTEGER         NOT NULL DEFAULT 5,
    STTS_CD         VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    STNG            JSONB           NOT NULL DEFAULT '{}',
    DEL_DT          TIMESTAMPTZ,
    CRTR_ID         BIGINT          REFERENCES app.TB_COMM_USER(ID),
    CRT_DT          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    MDFR_ID         BIGINT          REFERENCES app.TB_COMM_USER(ID),
    MDFCN_DT        TIMESTAMPTZ
);

CREATE UNIQUE INDEX idx_TB_COMM_WKSPC_SLUG ON app.TB_COMM_WKSPC(SLUG);
CREATE INDEX idx_TB_COMM_WKSPC_OWNR ON app.TB_COMM_WKSPC(OWNR_ID);
CREATE INDEX idx_TB_COMM_WKSPC_STTS ON app.TB_COMM_WKSPC(STTS_CD);

-- ============================================
-- 2. TR_COMM_WKSPC_MBR 테이블
-- ============================================
CREATE TABLE app.TR_COMM_WKSPC_MBR (
    ID              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    WKSPC_ID        BIGINT          NOT NULL REFERENCES app.TB_COMM_WKSPC(ID) ON DELETE CASCADE,
    USER_ID         BIGINT          NOT NULL REFERENCES app.TB_COMM_USER(ID) ON DELETE CASCADE,
    ROLE_CD         VARCHAR(20)     NOT NULL DEFAULT 'MEMBER',
    STTS_CD         VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    INVTR_ID        BIGINT          REFERENCES app.TB_COMM_USER(ID),
    JOIN_DT         TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    WHDWL_DT        TIMESTAMPTZ,
    CRTR_ID         BIGINT          REFERENCES app.TB_COMM_USER(ID),
    CRT_DT          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    MDFR_ID         BIGINT          REFERENCES app.TB_COMM_USER(ID),
    MDFCN_DT        TIMESTAMPTZ,
    CONSTRAINT uq_TR_COMM_WKSPC_MBR_ws_user UNIQUE (WKSPC_ID, USER_ID)
);

CREATE INDEX idx_TR_COMM_WKSPC_MBR_ws ON app.TR_COMM_WKSPC_MBR(WKSPC_ID, STTS_CD);
CREATE INDEX idx_TR_COMM_WKSPC_MBR_user ON app.TR_COMM_WKSPC_MBR(USER_ID, STTS_CD);

-- ============================================
-- 3. TB_COMM_WKSPC_INVT 테이블
-- ============================================
CREATE TABLE app.TB_COMM_WKSPC_INVT (
    ID              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    WKSPC_ID        BIGINT          NOT NULL REFERENCES app.TB_COMM_WKSPC(ID) ON DELETE CASCADE,
    EML_ADDR        VARCHAR(100),
    ROLE_CD         VARCHAR(20)     NOT NULL DEFAULT 'MEMBER',
    INVT_TYPE_CD    VARCHAR(20)     NOT NULL DEFAULT 'EMAIL',
    TKN             VARCHAR(128)    NOT NULL,
    INVTR_ID        BIGINT          NOT NULL REFERENCES app.TB_COMM_USER(ID),
    STTS_CD         VARCHAR(20)     NOT NULL DEFAULT 'PENDING',
    MAX_USE_CNT     INTEGER,
    USE_CNT         INTEGER         NOT NULL DEFAULT 0,
    EXPRY_DT        TIMESTAMPTZ     NOT NULL,
    ACPT_DT         TIMESTAMPTZ,
    ACPTR_ID        BIGINT          REFERENCES app.TB_COMM_USER(ID),
    CNCL_DT         TIMESTAMPTZ,
    CRTR_ID         BIGINT          REFERENCES app.TB_COMM_USER(ID),
    CRT_DT          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    MDFR_ID         BIGINT          REFERENCES app.TB_COMM_USER(ID),
    MDFCN_DT        TIMESTAMPTZ
);

CREATE UNIQUE INDEX idx_TB_COMM_WKSPC_INVT_TKN ON app.TB_COMM_WKSPC_INVT(TKN);
CREATE INDEX idx_TB_COMM_WKSPC_INVT_ws ON app.TB_COMM_WKSPC_INVT(WKSPC_ID, STTS_CD);
CREATE INDEX idx_TB_COMM_WKSPC_INVT_eml ON app.TB_COMM_WKSPC_INVT(EML_ADDR, STTS_CD);
CREATE INDEX idx_TB_COMM_WKSPC_INVT_expry ON app.TB_COMM_WKSPC_INVT(EXPRY_DT);

-- ============================================
-- 4. TB_COMM_USER 테이블 확장
-- ============================================
ALTER TABLE app.TB_COMM_USER ADD COLUMN BSC_WKSPC_ID BIGINT REFERENCES app.TB_COMM_WKSPC(ID);
```

### 3.7 Drizzle ORM 스키마 정의

```typescript
// lib/db/schema/workspace.ts
import {
  pgSchema, bigint, varchar, boolean, integer,
  timestamp, jsonb, uniqueIndex, index
} from 'drizzle-orm/pg-core';
import { users } from './auth';

export const app = pgSchema('app');

// ---- TB_COMM_WKSPC ----
export const workspaces = app.table('TB_COMM_WKSPC', {
  id:          bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  slug:        varchar('SLUG', { length: 100 }).notNull(),
  wkspcNm:     varchar('WKSPC_NM', { length: 100 }).notNull(),
  wkspcDc:     varchar('WKSPC_DC', { length: 500 }),
  logoUrl:     varchar('LOGO_URL', { length: 2000 }),
  ownrId:      bigint('OWNR_ID', { mode: 'number' }).notNull().references(() => users.id),
  typeCd:      varchar('TYPE_CD', { length: 20 }).notNull().default('TEAM'),
  maxMbrCnt:   integer('MAX_MBR_CNT').notNull().default(5),
  sttsCd:      varchar('STTS_CD', { length: 20 }).notNull().default('ACTIVE'),
  stng:        jsonb('STNG').notNull().default('{}'),
  delDt:       timestamp('DEL_DT', { withTimezone: true }),
  crtrId:      bigint('CRTR_ID', { mode: 'number' }),
  crtDt:       timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
  mdfrId:      bigint('MDFR_ID', { mode: 'number' }),
  mdfcnDt:     timestamp('MDFCN_DT', { withTimezone: true }),
}, (table) => [
  uniqueIndex('idx_TB_COMM_WKSPC_SLUG').on(table.slug),
  index('idx_TB_COMM_WKSPC_OWNR').on(table.ownrId),
  index('idx_TB_COMM_WKSPC_STTS').on(table.sttsCd),
]);

// ---- TR_COMM_WKSPC_MBR ----
export const workspaceMembers = app.table('TR_COMM_WKSPC_MBR', {
  id:          bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  wkspcId:     bigint('WKSPC_ID', { mode: 'number' }).notNull().references(() => workspaces.id, { onDelete: 'cascade' }),
  userId:      bigint('USER_ID', { mode: 'number' }).notNull().references(() => users.id, { onDelete: 'cascade' }),
  roleCd:      varchar('ROLE_CD', { length: 20 }).notNull().default('MEMBER'),
  sttsCd:      varchar('STTS_CD', { length: 20 }).notNull().default('ACTIVE'),
  invtrId:     bigint('INVTR_ID', { mode: 'number' }),
  joinDt:      timestamp('JOIN_DT', { withTimezone: true }).notNull().defaultNow(),
  whdwlDt:     timestamp('WHDWL_DT', { withTimezone: true }),
  crtrId:      bigint('CRTR_ID', { mode: 'number' }),
  crtDt:       timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
  mdfrId:      bigint('MDFR_ID', { mode: 'number' }),
  mdfcnDt:     timestamp('MDFCN_DT', { withTimezone: true }),
}, (table) => [
  uniqueIndex('uq_TR_COMM_WKSPC_MBR_ws_user').on(table.wkspcId, table.userId),
  index('idx_TR_COMM_WKSPC_MBR_ws').on(table.wkspcId, table.sttsCd),
  index('idx_TR_COMM_WKSPC_MBR_user').on(table.userId, table.sttsCd),
]);

// ---- TB_COMM_WKSPC_INVT ----
export const workspaceInvitations = app.table('TB_COMM_WKSPC_INVT', {
  id:          bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  wkspcId:     bigint('WKSPC_ID', { mode: 'number' }).notNull().references(() => workspaces.id, { onDelete: 'cascade' }),
  emlAddr:     varchar('EML_ADDR', { length: 100 }),
  roleCd:      varchar('ROLE_CD', { length: 20 }).notNull().default('MEMBER'),
  invtTypeCd:  varchar('INVT_TYPE_CD', { length: 20 }).notNull().default('EMAIL'),
  tkn:         varchar('TKN', { length: 128 }).notNull(),
  invtrId:     bigint('INVTR_ID', { mode: 'number' }).notNull().references(() => users.id),
  sttsCd:      varchar('STTS_CD', { length: 20 }).notNull().default('PENDING'),
  maxUseCnt:   integer('MAX_USE_CNT'),
  useCnt:      integer('USE_CNT').notNull().default(0),
  expryDt:     timestamp('EXPRY_DT', { withTimezone: true }).notNull(),
  acptDt:      timestamp('ACPT_DT', { withTimezone: true }),
  acptrId:     bigint('ACPTR_ID', { mode: 'number' }),
  cnclDt:      timestamp('CNCL_DT', { withTimezone: true }),
  crtrId:      bigint('CRTR_ID', { mode: 'number' }),
  crtDt:       timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
  mdfrId:      bigint('MDFR_ID', { mode: 'number' }),
  mdfcnDt:     timestamp('MDFCN_DT', { withTimezone: true }),
}, (table) => [
  uniqueIndex('idx_TB_COMM_WKSPC_INVT_TKN').on(table.tkn),
  index('idx_TB_COMM_WKSPC_INVT_ws').on(table.wkspcId, table.sttsCd),
  index('idx_TB_COMM_WKSPC_INVT_eml').on(table.emlAddr, table.sttsCd),
  index('idx_TB_COMM_WKSPC_INVT_expry').on(table.expryDt),
]);
```

---

## 4. API 설계

### 4.1 API 엔드포인트 총괄

#### 4.1.1 워크스페이스 API (`/api/v1/workspaces`)

| Method | Path | Auth | 설명 |
|--------|------|------|------|
| `GET` | `/api/v1/workspaces` | Bearer | 내 워크스페이스 목록 조회 |
| `POST` | `/api/v1/workspaces` | Bearer | 워크스페이스 생성 |
| `GET` | `/api/v1/workspaces/[id]` | WS MEMBER | 워크스페이스 상세 조회 |
| `PATCH` | `/api/v1/workspaces/[id]` | WS OWNER/ADMIN | 워크스페이스 정보 수정 |
| `DELETE` | `/api/v1/workspaces/[id]` | WS OWNER | 워크스페이스 삭제 (Soft Delete) |
| `PATCH` | `/api/v1/workspaces/[id]/switch` | Bearer | 기본 워크스페이스 전환 |

#### 4.1.2 멤버 API (`/api/v1/workspaces/[id]/members`)

| Method | Path | Auth | 설명 |
|--------|------|------|------|
| `GET` | `/api/v1/workspaces/[id]/members` | WS MEMBER | 멤버 목록 조회 |
| `PATCH` | `/api/v1/workspaces/[id]/members/[memberId]/role` | WS OWNER/ADMIN | 멤버 역할 변경 |
| `DELETE` | `/api/v1/workspaces/[id]/members/[memberId]` | WS OWNER/ADMIN | 멤버 강제 퇴장 (+ 크레딧 만료 처리) |
| `POST` | `/api/v1/workspaces/[id]/members/leave` | WS MEMBER | 워크스페이스 탈퇴 (+ 크레딧 만료 처리) |
| `POST` | `/api/v1/workspaces/[id]/transfer-ownership` | WS OWNER | 소유권 이전 |

#### 4.1.3 초대 API (`/api/v1/workspaces/[id]/invitations`)

| Method | Path | Auth | 설명 |
|--------|------|------|------|
| `GET` | `/api/v1/workspaces/[id]/invitations` | WS OWNER/ADMIN | 초대 목록 조회 |
| `POST` | `/api/v1/workspaces/[id]/invitations` | WS OWNER/ADMIN | 이메일 초대 발송 |
| `POST` | `/api/v1/workspaces/[id]/invitations/link` | WS OWNER/ADMIN | 초대 링크 생성 |
| `DELETE` | `/api/v1/workspaces/[id]/invitations/[invitationId]` | WS OWNER/ADMIN | 초대 취소 |
| `POST` | `/api/v1/invitations/[token]/accept` | Bearer | 초대 수락 |
| `POST` | `/api/v1/invitations/[token]/decline` | Bearer | 초대 거절 |
| `GET` | `/api/v1/invitations/[token]` | Public | 초대 정보 조회 (수락 전 미리보기) |

### 4.2 상세 API 스펙

#### 4.2.1 GET /api/v1/workspaces (내 워크스페이스 목록)

**Response 200**:
```json
[
  {
    "id": 1,
    "slug": "hong-personal",
    "name": "홍길동의 워크스페이스",
    "type_cd": "PERSONAL",
    "logo_url": null,
    "role_cd": "OWNER",
    "member_count": 1,
    "max_members": 1,
    "status_cd": "ACTIVE",
    "subscription": {
      "plan_name": "Free",
      "status_cd": "ACTIVE"
    },
    "is_default": true,
    "created_at": "2026-01-01T00:00:00Z"
  },
  {
    "id": 2,
    "slug": "acme-corp",
    "name": "Acme Corp",
    "type_cd": "TEAM",
    "logo_url": "https://...",
    "role_cd": "ADMIN",
    "member_count": 12,
    "max_members": 25,
    "status_cd": "ACTIVE",
    "subscription": {
      "plan_name": "Pro",
      "status_cd": "ACTIVE"
    },
    "is_default": false,
    "created_at": "2026-01-15T00:00:00Z"
  }
]
```

#### 4.2.2 POST /api/v1/workspaces (워크스페이스 생성)

**Request Body**:
```typescript
const createWorkspaceSchema = z.object({
  name: z.string().min(1).max(100),
  slug: z.string().min(2).max(100).regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/),
  description: z.string().max(500).optional(),
});
```

**Response 201**:
```json
{
  "id": 3,
  "slug": "new-team",
  "name": "New Team",
  "type_cd": "TEAM",
  "owner_id": 42,
  "role_cd": "OWNER",
  "max_members": 5,
  "status_cd": "ACTIVE",
  "created_at": "2026-02-14T10:00:00Z"
}
```

**비즈니스 로직**:
1. `SLUG` 중복 검사 (Unique)
2. 사용자당 소유 워크스페이스 수 제한 검사 (`WORKSPACE_MAX_PER_USER`)
3. `TB_COMM_WKSPC` 생성 (`TYPE_CD = 'TEAM'`)
4. `TR_COMM_WKSPC_MBR` 생성 (생성자를 `OWNER`로 자동 추가)
5. 사용자의 `BSC_WKSPC_ID`가 NULL이면 이 워크스페이스로 설정

**에러 응답**:

| HTTP 상태 | 에러 코드 | 설명 |
|-----------|----------|------|
| 400 | `VALIDATION_ERROR` | 요청 데이터 유효성 실패 |
| 409 | `SLUG_ALREADY_EXISTS` | 슬러그 중복 |
| 403 | `MAX_WORKSPACES_REACHED` | 최대 워크스페이스 소유 수 초과 |

#### 4.2.3 PATCH /api/v1/workspaces/[id] (워크스페이스 수정)

**Request Body**:
```typescript
const updateWorkspaceSchema = z.object({
  name: z.string().min(1).max(100).optional(),
  slug: z.string().min(2).max(100).regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/).optional(),
  description: z.string().max(500).optional(),
  logo_url: z.string().url().max(2000).optional().nullable(),
  settings: z.record(z.unknown()).optional(),
});
```

**Response 200**: 수정된 워크스페이스 정보

#### 4.2.4 POST /api/v1/workspaces/[id]/invitations (이메일 초대)

**Request Body**:
```typescript
const inviteByEmailSchema = z.object({
  emails: z.array(z.string().email()).min(1).max(20),
  role_cd: z.enum(['ADMIN', 'MEMBER', 'GUEST']).default('MEMBER'),
});
```

**Response 201**:
```json
{
  "invitations": [
    {
      "id": 10,
      "email": "user1@example.com",
      "role_cd": "MEMBER",
      "status_cd": "PENDING",
      "expires_at": "2026-02-21T10:00:00Z"
    },
    {
      "id": 11,
      "email": "user2@example.com",
      "role_cd": "MEMBER",
      "status_cd": "PENDING",
      "expires_at": "2026-02-21T10:00:00Z"
    }
  ],
  "already_members": ["user3@example.com"],
  "already_invited": []
}
```

**비즈니스 로직**:
1. 워크스페이스 멤버십 + 역할 검증 (OWNER 또는 ADMIN)
2. 워크스페이스 멤버 수 제한 검사 (`현재 멤버 + 대기 초대 < MAX_MBR_CNT`)
3. 이미 멤버인 이메일 필터링
4. 이미 대기 중인 초대가 있는 이메일 필터링
5. 각 이메일에 대해:
   a. `TB_COMM_WKSPC_INVT` 생성 (TKN 자동 생성, 만료 7일)
   b. 초대 이메일 발송 (수락 링크 포함)
6. OWNER가 아닌 ADMIN이 초대 시 `ADMIN` 역할로는 초대 불가

**에러 응답**:

| HTTP 상태 | 에러 코드 | 설명 |
|-----------|----------|------|
| 403 | `PERMISSION_DENIED` | 초대 권한 없음 |
| 409 | `MEMBER_LIMIT_REACHED` | 멤버 수 제한 초과 |
| 400 | `INVALID_ROLE_ASSIGNMENT` | ADMIN이 ADMIN 역할로 초대 시도 |

#### 4.2.5 POST /api/v1/workspaces/[id]/invitations/link (초대 링크 생성)

**Request Body**:
```typescript
const createInviteLinkSchema = z.object({
  role_cd: z.enum(['MEMBER', 'GUEST']).default('MEMBER'),
  max_uses: z.number().int().min(1).max(1000).optional(),
  expires_hours: z.number().int().min(1).max(720).default(720),
});
```

**Response 201**:
```json
{
  "id": 20,
  "invite_url": "https://your-app.com/invitations/abc123def456",
  "token": "abc123def456",
  "role_cd": "MEMBER",
  "max_uses": 50,
  "use_count": 0,
  "expires_at": "2026-03-16T10:00:00Z"
}
```

#### 4.2.6 POST /api/v1/invitations/[token]/accept (초대 수락)

**Response 200**:
```json
{
  "workspace": {
    "id": 2,
    "slug": "acme-corp",
    "name": "Acme Corp",
    "role_cd": "MEMBER"
  },
  "message": "워크스페이스에 참여했습니다."
}
```

**비즈니스 로직**:
1. 토큰 유효성 검증 (존재, 만료, 상태, 사용 횟수)
2. 이메일 초대인 경우 요청 사용자의 이메일 일치 확인
3. 이미 해당 워크스페이스의 멤버인지 확인
4. 멤버 수 제한 재확인
5. `TR_COMM_WKSPC_MBR` 생성 (역할은 초대에 지정된 `ROLE_CD`)
6. 초대 상태 업데이트 (`ACCEPTED`, `ACPT_DT`, `ACPTR_ID`)
7. 링크 초대인 경우 `USE_CNT` 증가
8. 사용자의 `BSC_WKSPC_ID`가 NULL이면 이 워크스페이스로 설정
9. 크레딧 할당: 워크스페이스에 활성 구독이 있으면 `creditManager.allocateCreditsForMember()` 호출 (잔여 일수 비례 배분)

**에러 응답**:

| HTTP 상태 | 에러 코드 | 설명 |
|-----------|----------|------|
| 404 | `INVITATION_NOT_FOUND` | 초대를 찾을 수 없음 |
| 410 | `INVITATION_EXPIRED` | 초대 만료 |
| 409 | `ALREADY_MEMBER` | 이미 워크스페이스 멤버 |
| 409 | `MEMBER_LIMIT_REACHED` | 멤버 수 제한 초과 |
| 403 | `EMAIL_MISMATCH` | 이메일 초대에서 이메일 불일치 |
| 410 | `INVITATION_USED_UP` | 초대 링크 사용 횟수 초과 |

#### 4.2.7 PATCH /api/v1/workspaces/[id]/members/[memberId]/role (역할 변경)

**Request Body**:
```typescript
const changeMemberRoleSchema = z.object({
  role_cd: z.enum(['ADMIN', 'MEMBER', 'GUEST']),
});
```

**Response 200**:
```json
{
  "id": 5,
  "user": { "id": 42, "email": "user@example.com", "display_nm": "홍길동" },
  "role_cd": "ADMIN",
  "updated_at": "2026-02-14T15:00:00Z"
}
```

**비즈니스 로직**:
1. 요청자 권한 검증:
   - OWNER → 모든 역할 변경 가능 (ADMIN 부여/해제 포함)
   - ADMIN → MEMBER↔GUEST 변경만 가능
2. OWNER 역할로의 변경은 불가 (소유권 이전 API 별도)
3. 자기 자신의 역할 변경 불가

#### 4.2.8 POST /api/v1/workspaces/[id]/transfer-ownership (소유권 이전)

**Request Body**:
```typescript
const transferOwnershipSchema = z.object({
  new_owner_user_id: z.number().int().positive(),
});
```

**Response 200**:
```json
{
  "workspace_id": 2,
  "previous_owner": { "id": 1, "email": "prev@example.com", "new_role_cd": "ADMIN" },
  "new_owner": { "id": 42, "email": "new@example.com", "role_cd": "OWNER" }
}
```

**비즈니스 로직**:
1. 현재 OWNER만 호출 가능
2. 대상 사용자가 해당 워크스페이스의 활성 멤버인지 확인
3. 트랜잭션 내에서:
   a. 기존 OWNER → ADMIN으로 변경
   b. 대상 멤버 → OWNER로 변경
   c. `TB_COMM_WKSPC.OWNR_ID` 업데이트
4. 개인 워크스페이스(`PERSONAL`)는 소유권 이전 불가

#### 4.2.9 DELETE /api/v1/workspaces/[id] (워크스페이스 삭제)

**Response**: `204 No Content`

**비즈니스 로직**:
1. OWNER만 호출 가능
2. 개인 워크스페이스(`PERSONAL`)는 삭제 불가
3. 활성 구독이 있으면 먼저 구독 해지 안내 (400 에러)
4. Soft Delete: `STTS_CD = 'DELETED'`, `DEL_DT = NOW()`
5. 모든 멤버의 `STTS_CD = 'LEFT'`, `WHDWL_DT = NOW()` 설정
6. 해당 워크스페이스가 `BSC_WKSPC_ID`인 사용자들의 `BSC_WKSPC_ID` 재설정
7. 대기 중인 초대 전체 취소

#### 4.2.10 PATCH /api/v1/workspaces/[id]/switch (워크스페이스 전환)

**Response 200**:
```json
{
  "default_ws_id": 2,
  "workspace": {
    "id": 2,
    "slug": "acme-corp",
    "name": "Acme Corp",
    "role_cd": "ADMIN"
  }
}
```

**비즈니스 로직**:
1. 해당 워크스페이스의 활성 멤버인지 확인
2. `TB_COMM_USER.BSC_WKSPC_ID` 업데이트

### 4.3 공통 에러 응답 형식

```json
{
  "error": {
    "code": "MEMBER_LIMIT_REACHED",
    "message": "워크스페이스 멤버 수 제한을 초과했습니다.",
    "details": {
      "current_members": 25,
      "max_members": 25,
      "plan": "Pro"
    }
  }
}
```

### 4.4 워크스페이스 멤버십 미들웨어

```typescript
// lib/workspace/membership-middleware.ts

type WorkspaceRole = 'OWNER' | 'ADMIN' | 'MEMBER' | 'GUEST';

/**
 * 워크스페이스 멤버십 및 역할 검증 미들웨어.
 * API 경로의 [workspaceId] 파라미터에서 워크스페이스를 식별하고,
 * 요청자의 멤버십과 역할을 검증한다.
 */
function requireWorkspaceRole(...allowedRoles: WorkspaceRole[]) {
  return async (request: NextRequest, workspaceId: number) => {
    const user = await getAuthenticatedUser(request);
    if (!user) {
      return NextResponse.json(
        { error: { code: 'UNAUTHORIZED', message: '인증이 필요합니다.' } },
        { status: 401 }
      );
    }

    // 워크스페이스 존재 및 상태 확인
    const workspace = await getWorkspace(workspaceId);
    if (!workspace || workspace.statusCd !== 'ACTIVE') {
      return NextResponse.json(
        { error: { code: 'WORKSPACE_NOT_FOUND', message: '워크스페이스를 찾을 수 없습니다.' } },
        { status: 404 }
      );
    }

    // 멤버십 확인
    const member = await getWorkspaceMember(workspaceId, user.id);
    if (!member || member.statusCd !== 'ACTIVE') {
      return NextResponse.json(
        { error: { code: 'NOT_WORKSPACE_MEMBER', message: '워크스페이스 멤버가 아닙니다.' } },
        { status: 403 }
      );
    }

    // 역할 확인
    if (!allowedRoles.includes(member.roleCd as WorkspaceRole)) {
      return NextResponse.json(
        { error: { code: 'INSUFFICIENT_WORKSPACE_ROLE', message: '해당 작업에 필요한 워크스페이스 역할이 없습니다.' } },
        { status: 403 }
      );
    }

    return null; // 통과
  };
}
```

**API Route 사용 예시**:
```typescript
// app/api/v1/workspaces/[id]/members/route.ts
export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  const workspaceId = Number(params.id);
  const denied = await requireWorkspaceRole('OWNER', 'ADMIN', 'MEMBER', 'GUEST')(request, workspaceId);
  if (denied) return denied;

  // ... 멤버 목록 조회 로직
}
```

---

## 5. 화면 구성

### 5.1 화면 목록 총괄

| 구분 | 경로 | 접근 권한 | 설명 |
|------|------|----------|------|
| 워크스페이스 생성 | `/workspaces/new` | Bearer | 새 팀 워크스페이스 생성 |
| 워크스페이스 대시보드 | `/workspaces/[slug]/dashboard` | WS MEMBER | 워크스페이스 홈 |
| 워크스페이스 설정 | `/workspaces/[slug]/settings` | WS OWNER/ADMIN | 일반 설정 |
| 멤버 관리 | `/workspaces/[slug]/settings/members` | WS OWNER/ADMIN | 멤버 목록, 초대, 역할 관리 |
| 초대 수락 | `/invitations/[token]` | Public/Bearer | 초대 미리보기 + 수락 |
| 워크스페이스 선택 | `/workspaces` | Bearer | 워크스페이스 목록 + 전환 |

### 5.2 워크스페이스 생성 페이지 (`/workspaces/new`)

```
┌──────────────────────────────────────┐
│           [앱 로고/아이콘]            │
│           워크스페이스 만들기            │
│     팀과 함께 협업할 공간을 만드세요      │
│                                      │
│  ┌──────────────────────────────┐   │
│  │  ┌─ 워크스페이스 이름 ────────┐   │
│  │  │ Acme Corp               │   │   │
│  │  └──────────────────────────┘   │
│  │  ┌─ URL 슬러그 ──────────────┐   │
│  │  │ acme-corp                │   │   │
│  │  └──────────────────────────┘   │
│  │  https://app.com/workspaces/acme-corp│
│  │                                  │
│  │  ┌─ 설명 (선택) ──────────────┐   │
│  │  │                            │   │
│  │  └──────────────────────────┘   │
│  │                                  │
│  │  ┌──────────────────────────┐   │
│  │  │    워크스페이스 만들기     │   │
│  │  └──────────────────────────┘   │
│  │                                  │
│  │  만들기 후 팀원을 초대할 수 있습니다 │
│  └──────────────────────────────────┘
└──────────────────────────────────────┘
```

### 5.3 멤버 관리 페이지 (`/workspaces/[slug]/settings/members`)

```
┌──────────────────────────────────────────────────┐
│  [WorkspaceLayout]                                │
│  ┌────────────────────────────────────────────┐  │
│  │  멤버 관리              [+ 멤버 초대]        │  │
│  │                                            │  │
│  │  ── 멤버 (12/25명) ──                       │  │
│  │  ┌─────┬──────┬────────┬──────┬────────┐  │  │
│  │  │ 사진 │ 이름  │ 이메일   │ 역할  │ 작업    │  │  │
│  │  ├─────┼──────┼────────┼──────┼────────┤  │  │
│  │  │ 👤  │관리자 │admin@..│OWNER │ -      │  │  │
│  │  │ 👤  │홍길동 │hong@.. │ADMIN │[▼][✕]  │  │  │
│  │  │ 👤  │김영희 │kim@..  │MEMBER│[▼][✕]  │  │  │
│  │  │ 👤  │이철수 │lee@..  │GUEST │[▼][✕]  │  │  │
│  │  └─────┴──────┴────────┴──────┴────────┘  │  │
│  │                                            │  │
│  │  ── 대기 중인 초대 (3건) ──                  │  │
│  │  ┌────────┬──────┬────────┬──────────┐    │  │
│  │  │ 이메일  │ 역할  │ 만료    │ 작업      │    │  │
│  │  ├────────┼──────┼────────┼──────────┤    │  │
│  │  │new1@.. │MEMBER│2.21    │[초대 취소] │    │  │
│  │  │new2@.. │MEMBER│2.21    │[초대 취소] │    │  │
│  │  └────────┴──────┴────────┴──────────┘    │  │
│  │                                            │  │
│  │  ── 초대 링크 ──                            │  │
│  │  ┌────────────────────────────────────┐   │  │
│  │  │ https://app.com/invitations/abc123  │   │  │
│  │  │ MEMBER 역할 | 50명 제한 | 3/50 사용  │   │  │
│  │  │ 만료: 2026.03.16                    │   │  │
│  │  │ [링크 복사]  [비활성화]               │   │  │
│  │  └────────────────────────────────────┘   │  │
│  │  [+ 새 초대 링크 생성]                      │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

### 5.4 초대 수락 페이지 (`/invitations/[token]`)

```
┌──────────────────────────────────────┐
│           [앱 로고/아이콘]            │
│                                      │
│  ┌──────────────────────────────┐   │
│  │                              │   │
│  │  관리자님이 "Acme Corp"       │   │
│  │  워크스페이스에 초대했습니다    │   │
│  │                              │   │
│  │  ┌──────┐                    │   │
│  │  │ 로고  │  Acme Corp        │   │
│  │  │      │  멤버 12명         │   │
│  │  └──────┘                    │   │
│  │                              │   │
│  │  역할: 멤버 (MEMBER)          │   │
│  │  초대자: admin@astravision.co│   │
│  │  만료: 2026.02.21            │   │
│  │                              │   │
│  │  ┌──────────────────────┐   │   │
│  │  │     초대 수락         │   │   │
│  │  └──────────────────────┘   │   │
│  │  ┌──────────────────────┐   │   │
│  │  │     거절하기          │   │   │
│  │  └──────────────────────┘   │   │
│  │                              │   │
│  │  * 수락 시 Acme Corp의       │   │
│  │    멤버로 참여하게 됩니다      │   │
│  └──────────────────────────────┘   │
│                                      │
│  비로그인 상태:                       │
│  [로그인하고 초대 수락] [회원가입]      │
└──────────────────────────────────────┘
```

### 5.5 워크스페이스 전환기 (WorkspaceSwitcher)

사이드바 상단에 위치하는 워크스페이스 전환 드롭다운.

```
┌──────────────────────┐
│ [로고] Acme Corp  [▼] │ ← 현재 워크스페이스 (클릭 시 드롭다운)
├──────────────────────┤
│ ☑ Acme Corp (ADMIN)  │ ← 현재 선택
│   홍길동 (OWNER)       │
│   Side Project (MEMBER)│
│ ──────────────────── │
│ + 워크스페이스 만들기   │
│   워크스페이스 관리     │
└──────────────────────┘
```

### 5.6 멤버 초대 모달

```
┌──────────────────────────────────────┐
│  멤버 초대                     [✕]   │
│                                      │
│  ── 이메일로 초대 ──                   │
│  ┌──────────────────────────────┐   │
│  │ 이메일 주소 (쉼표로 구분)      │   │
│  │ user1@example.com,           │   │
│  │ user2@example.com            │   │
│  └──────────────────────────────┘   │
│                                      │
│  역할: [멤버 (MEMBER) ▼]             │
│                                      │
│  ┌──────────────────────────────┐   │
│  │         초대 발송             │   │
│  └──────────────────────────────┘   │
│                                      │
│  ── 또는 ──                          │
│                                      │
│  ┌──────────────────────────────┐   │
│  │   초대 링크로 공유             │   │
│  └──────────────────────────────┘   │
└──────────────────────────────────────┘
```

---

## 6. 유즈케이스 및 데이터 플로우

### 6.1 UC-01: 회원가입 → 개인 워크스페이스 자동 생성

**트리거**: 사용자가 `POST /api/v1/auth/signup`으로 회원가입 완료

```
[사용자] ──────────────────────────────────────────────────────
  │
  │  1. 회원가입 요청 (Firebase ID Token + 약관 동의)
  ▼
[POST /api/v1/auth/signup] ───────────────────────────────────
  │
  │  2. Firebase ID Token 검증
  │  3. TB_COMM_USER 생성 (ID=42)
  │  4. TB_COMM_USER_AGRE 생성
  │
  │  ── 워크스페이스 자동 생성 (트랜잭션 내) ──
  │
  │  5. TB_COMM_WKSPC 생성
  │     ├─ SLUG: "{displayNm}-personal" (예: "hong-personal")
  │     ├─ WKSPC_NM: "{displayNm}의 워크스페이스"
  │     ├─ TYPE_CD: "PERSONAL"
  │     ├─ OWNR_ID: 42
  │     └─ MAX_MBR_CNT: 1
  │
  │  6. TR_COMM_WKSPC_MBR 생성
  │     ├─ WKSPC_ID: (생성된 워크스페이스 ID)
  │     ├─ USER_ID: 42
  │     └─ ROLE_CD: "OWNER"
  │
  │  7. TB_COMM_USER 업데이트
  │     └─ BSC_WKSPC_ID: (생성된 워크스페이스 ID)
  │
  │  8. JWT 토큰 발급 (ws_id 포함)
  ▼
[응답]: { access_token, refresh_token, user, workspace }
```

**주요 규칙**:
- 개인 워크스페이스는 삭제 불가
- 개인 워크스페이스의 소유권 이전 불가
- 개인 워크스페이스는 멤버 추가 불가 (`MAX_MBR_CNT = 1`)
- 슬러그 중복 시 자동 넘버링 (예: `hong-personal-2`)

### 6.2 UC-02: 팀 워크스페이스 생성

**트리거**: 로그인된 사용자가 워크스페이스 생성 요청

```
[사용자] ──────────────────────────────────────────────────────
  │
  │  1. 워크스페이스 이름, 슬러그 입력
  ▼
[POST /api/v1/workspaces] ────────────────────────────────────
  │
  │  2. 슬러그 중복 검사
  │  3. 사용자당 워크스페이스 소유 제한 검사
  │
  │  4. TB_COMM_WKSPC 생성
  │     ├─ SLUG: "acme-corp"
  │     ├─ WKSPC_NM: "Acme Corp"
  │     ├─ TYPE_CD: "TEAM"
  │     ├─ OWNR_ID: 42
  │     └─ MAX_MBR_CNT: 5 (무료 플랜 기본값)
  │
  │  5. TR_COMM_WKSPC_MBR 생성
  │     ├─ WKSPC_ID: (새 워크스페이스)
  │     ├─ USER_ID: 42
  │     └─ ROLE_CD: "OWNER"
  │
  │  6. 사용자에게 워크스페이스 전환 안내
  ▼
[응답]: { workspace, redirect_url }
  │
  ▼
[리다이렉트]: /workspaces/acme-corp/settings/members
  │  (멤버 초대 화면으로 이동하여 팀원 초대 유도)
```

### 6.3 UC-03: 이메일 기반 멤버 초대

**트리거**: OWNER/ADMIN이 멤버 초대 요청

```
[OWNER/ADMIN] ────────────────────────────────────────────────
  │
  │  1. 이메일 주소 입력 + 역할 선택
  ▼
[POST /api/v1/workspaces/:id/invitations] ────────────────────
  │
  │  2. 권한 검증 (OWNER 또는 ADMIN)
  │  3. 멤버 수 제한 검사
  │  4. 이미 멤버/초대 대기 중 필터링
  │
  │  5. TB_COMM_WKSPC_INVT 생성
  │     ├─ EML_ADDR: "user@example.com"
  │     ├─ ROLE_CD: "MEMBER"
  │     ├─ INVT_TYPE_CD: "EMAIL"
  │     ├─ TKN: nanoid(32)
  │     ├─ STTS_CD: "PENDING"
  │     └─ EXPRY_DT: NOW() + 7일
  │
  │  6. 초대 이메일 발송 (SMTP)
  │     ├─ 제목: "[YourApp] Acme Corp 워크스페이스에 초대되었습니다"
  │     ├─ 수락 링크: https://app.com/invitations/{token}
  │     └─ 발신자: 관리자 이름, 워크스페이스 이름
  ▼
[응답]: { invitations, already_members, already_invited }

  ... 시간 경과 ...

[초대받은 사용자] ─────────────────────────────────────────────
  │
  │  7. 이메일의 수락 링크 클릭
  ▼
[GET /api/v1/invitations/{token}] ── 초대 정보 미리보기 ──────
  │
  │  8. 초대 유효성 확인 (만료, 상태)
  │  9. 워크스페이스 이름, 초대자, 역할 표시
  ▼
[초대 수락 페이지] ────────────────────────────────────────────
  │
  │  ── 비로그인 상태 ──
  │  │  10a. 로그인 페이지로 이동 (redirect=초대 URL)
  │  │  10b. 로그인 후 자동으로 초대 수락 페이지 복귀
  │  │
  │  ── 미가입 상태 ──
  │  │  10c. 회원가입 페이지로 이동 (redirect=초대 URL)
  │  │  10d. 회원가입 완료 후 초대 수락 페이지 복귀
  │  │
  │  ── 로그인 상태 ──
  │
  │  11. "초대 수락" 클릭
  ▼
[POST /api/v1/invitations/{token}/accept] ─────────────────────
  │
  │  12. 토큰 재검증
  │  13. 요청 사용자 이메일 == 초대 이메일 확인
  │  14. 멤버 수 제한 재확인
  │
  │  15. TR_COMM_WKSPC_MBR 생성
  │      ├─ WKSPC_ID: 2
  │      ├─ USER_ID: (수락한 사용자)
  │      ├─ ROLE_CD: "MEMBER"
  │      └─ INVTR_ID: (초대자 ID)
  │
  │  16. TB_COMM_WKSPC_INVT 업데이트
  │      ├─ STTS_CD: "ACCEPTED"
  │      ├─ ACPT_DT: NOW()
  │      └─ ACPTR_ID: (사용자 ID)
  │
  │  17. 크레딧 할당 (결제 모듈 연동)
  │      ├─ 워크스페이스 활성 구독 조회
  │      ├─ 구독 있음 → creditManager.allocateCreditsForMember() 호출
  │      │   ├─ TB_PAY_PLAN_FNC에서 monthly_credits 조회
  │      │   ├─ "unlimited" → 할당 생략
  │      │   └─ 잔여 일수 비례 크레딧 할당
  │      │       └─ Math.floor(monthlyCredits × remainingDays / totalDays)
  │      └─ 구독 없음 → 크레딧 할당 생략
  │
  │  18. 알림: 초대자에게 "{이름}이 초대를 수락했습니다" 알림
  ▼
[리다이렉트]: /workspaces/acme-corp/dashboard
```

### 6.4 UC-04: 초대 링크 기반 멤버 참여

**트리거**: OWNER/ADMIN이 초대 링크 생성 → 공유

```
[OWNER/ADMIN] ────────────────────────────────────────────────
  │
  │  1. 초대 링크 생성 요청
  ▼
[POST /api/v1/workspaces/:id/invitations/link] ────────────────
  │
  │  2. TB_COMM_WKSPC_INVT 생성
  │     ├─ INVT_TYPE_CD: "LINK"
  │     ├─ EML_ADDR: NULL (특정 이메일 없음)
  │     ├─ ROLE_CD: "MEMBER"
  │     ├─ TKN: nanoid(32)
  │     ├─ MAX_USE_CNT: 50
  │     ├─ USE_CNT: 0
  │     └─ EXPRY_DT: NOW() + 30일
  ▼
[응답]: { invite_url, token, ... }
  │
  │  3. Slack, 메신저 등으로 링크 공유
  ▼

[초대받은 사용자 A] ──────────────────────────────────────────
  │
  │  4. 링크 클릭 → 초대 수락 페이지
  │  5. (필요 시 로그인/회원가입)
  │  6. "초대 수락" 클릭
  ▼
[POST /api/v1/invitations/{token}/accept] ─────────────────────
  │
  │  7. 이메일 검증 없음 (LINK 초대이므로)
  │  8. USE_CNT < MAX_USE_CNT 확인
  │  9. 멤버 생성 + USE_CNT 증가
  │  10. 크레딧 할당 (결제 모듈 연동)
  │      └─ creditManager.allocateCreditsForMember() (비례 배분)
  ▼
[성공]: USE_CNT = 1/50

[초대받은 사용자 B, C, ...] ── 동일 링크로 반복 사용 가능 ──
```

**이메일 초대와 링크 초대의 차이**:

| 항목 | 이메일 초대 (EMAIL) | 링크 초대 (LINK) |
|------|-------------------|-----------------|
| 대상 | 특정 이메일 1:1 | 링크를 가진 누구나 |
| 이메일 검증 | 수락 시 이메일 일치 확인 | 검증 없음 |
| 사용 횟수 | 1회 (1명) | `MAX_USE_CNT`까지 다수 |
| 이메일 발송 | 자동 발송 | 수동 공유 |
| 보안 수준 | 높음 | 중간 (링크 유출 시 누구나 가입 가능) |

### 6.5 UC-05: 워크스페이스 기반 구독 결제

**트리거**: 워크스페이스 OWNER/ADMIN이 유료 플랜 구독 시작

```
[WS OWNER/ADMIN] ─────────────────────────────────────────────
  │
  │  1. 요금제 안내 페이지에서 플랜 선택 (Pro)
  ▼
[/pricing → 워크스페이스 선택] ────────────────────────────────
  │
  │  2. 어떤 워크스페이스에 적용할지 선택
  │     (사용자가 OWNER/ADMIN인 워크스페이스 목록 표시)
  ▼
[워크스페이스 확인] ────────────────────────────────────────────
  │
  │  3. 결제 수단 등록 여부 확인
  │     ├─ 등록된 결제 수단 있음 → 구독 생성 진행
  │     └─ 없음 → 결제 수단 등록 페이지로 이동
  ▼
[POST /workspaces/:wsId/billing/payment-methods] ── (결제 수단 등록) ──
  │
  │  4. 토스페이먼츠 SDK 결제창 → 빌링키 발급
  │  5. TB_PAY_STLM_MTHD 생성
  ▼
[POST /workspaces/:wsId/billing/subscriptions] ── (구독 생성) ──
  │
  │  6. 워크스페이스 멤버십 + 역할 검증 (OWNER 또는 ADMIN)
  │  7. 기존 활성 구독 존재 검사
  │  8. 플랜 유효성 검증
  │
  │  9. TB_PAY_SBSC 생성
  │     ├─ WKSPC_ID: (선택한 워크스페이스)
  │     ├─ plan_id: Pro
  │     ├─ STTS_CD: "TRIALING" (14일 무료 체험)
  │     └─ current_period_end: NOW() + 14일
  │
  │  10. TB_COMM_WKSPC 업데이트
  │      └─ MAX_MBR_CNT: 25 (Pro 플랜 기준)
  │
  │  11. pay_billing_events 기록
  │      └─ event_type: "subscription.created"
  ▼
[응답]: { subscription, workspace }
```

**구독 상태 변경 → 워크스페이스 영향**:

| 구독 이벤트 | 워크스페이스 영향 |
|------------|---------------|
| `subscription.created` | `MAX_MBR_CNT`를 플랜 기능 값으로 업데이트 + 전체 멤버 크레딧 할당 |
| `subscription.upgraded` | `MAX_MBR_CNT` 증가 + 크레딧 재조정 (차액 추가) |
| `subscription.downgraded` | `MAX_MBR_CNT` 감소 (현재 멤버 > 새 제한이면 경고만, 강제 퇴장 없음) + 크레딧 재조정 (할당량 축소) |
| `subscription.renewed` | 이전 기간 크레딧 만료 + 신규 기간 크레딧 할당 |
| `subscription.canceled` | 기간 만료 후 `MAX_MBR_CNT`를 무료 기본값으로 복원 + 크레딧 만료 |
| `subscription.suspended` | 워크스페이스 `STTS_CD = 'SUSPENDED'` (읽기 전용 모드) |

### 6.6 UC-06: 워크스페이스 정지 → 결제 실패 대응

**트리거**: 정기결제 실패 → Dunning → 최종 실패

```
[Scheduler: 정기결제 시도] ────────────────────────────────────
  │
  │  1. 결제 실패 (잔액 부족 등)
  │  2. TB_PAY_SBSC.status_cd = "PAST_DUE"
  │  3. Dunning 재시도 시작 (1일 → 3일 → 7일 → 14일)
  │
  │  ── 14일간 재시도 모두 실패 ──
  │
  │  4. TB_PAY_SBSC.status_cd = "SUSPENDED"
  ▼
[워크스페이스 정지 처리] ──────────────────────────────────────
  │
  │  5. TB_COMM_WKSPC.STTS_CD = "SUSPENDED"
  │  6. 워크스페이스 읽기 전용 모드 전환
  │     ├─ 기존 데이터 조회 가능
  │     ├─ 새 데이터 생성/수정 불가
  │     └─ 멤버 초대 불가
  │
  │  7. OWNER/ADMIN에게 알림 발송
  │     ├─ 이메일: "결제 실패로 워크스페이스가 정지되었습니다"
  │     └─ 앱 내 배너: "결제 수단을 업데이트해주세요"
  ▼
[WS OWNER/ADMIN 대응] ────────────────────────────────────────
  │
  │  8. 결제 수단 업데이트 또는 수동 결제
  ▼
[결제 성공] ────────────────────────────────────────────────────
  │
  │  9. TB_PAY_SBSC.status_cd = "ACTIVE"
  │  10. TB_COMM_WKSPC.STTS_CD = "ACTIVE"
  │  11. 정상 서비스 복구
```

### 6.7 UC-07: 소유권 이전

**트리거**: OWNER가 다른 멤버에게 소유권 이전

```
[OWNER] ──────────────────────────────────────────────────────
  │
  │  1. 멤버 관리에서 대상 멤버 선택
  │  2. "소유권 이전" 클릭
  │  3. 확인 모달: "소유권을 이전하면 되돌릴 수 없습니다"
  │  4. 비밀번호/재인증 요구 (보안)
  ▼
[POST /api/v1/workspaces/:id/transfer-ownership] ──────────────
  │
  │  트랜잭션 시작
  │  5. TR_COMM_WKSPC_MBR: 기존 OWNER → ROLE_CD = "ADMIN"
  │  6. TR_COMM_WKSPC_MBR: 대상 멤버 → ROLE_CD = "OWNER"
  │  7. TB_COMM_WKSPC: OWNR_ID = (새 소유자)
  │  트랜잭션 커밋
  │
  │  8. 알림: 새 소유자에게 "워크스페이스 소유권이 이전되었습니다"
  │  9. 감사 로그: workspace.ownership.transferred
  ▼
[응답]: { previous_owner, new_owner }
```

### 6.8 UC-08: 워크스페이스 전환

**트리거**: 사용자가 다른 워크스페이스로 전환

```
[사용자] ──────────────────────────────────────────────────────
  │
  │  1. 사이드바 WorkspaceSwitcher 클릭
  │  2. 워크스페이스 목록에서 선택
  ▼
[PATCH /api/v1/workspaces/:id/switch] ─────────────────────────
  │
  │  3. 멤버십 확인 (해당 워크스페이스의 활성 멤버인지)
  │  4. TB_COMM_USER.BSC_WKSPC_ID 업데이트
  ▼
[클라이언트] ──────────────────────────────────────────────────
  │
  │  5. WorkspaceContext 상태 업데이트
  │  6. 사이드바 메뉴 재렌더링 (워크스페이스별 메뉴)
  │  7. 페이지 리다이렉트: /workspaces/{새 slug}/dashboard
```

### 6.9 UC-09: 회원 탈퇴 → 워크스페이스 처리

**트리거**: 사용자가 `DELETE /api/v1/users/me`로 회원 탈퇴

```
[사용자 탈퇴 처리] ────────────────────────────────────────────
  │
  │  1. 사용자가 OWNER인 워크스페이스 조회
  │
  │  ── OWNER인 팀 워크스페이스가 있는 경우 ──
  │  │  2a. 탈퇴 거부: "워크스페이스 소유권을 먼저 이전해주세요"
  │  │  (소유한 모든 팀 워크스페이스의 소유권을 이전하거나 삭제해야 탈퇴 가능)
  │  │
  │  ── OWNER인 팀 워크스페이스가 없는 경우 ──
  │
  │  3. MEMBER/ADMIN/GUEST로 속한 워크스페이스에서 탈퇴 처리
  │     └─ TR_COMM_WKSPC_MBR.STTS_CD = "LEFT", WHDWL_DT = NOW()
  │
  │  4. 크레딧 만료 처리 (결제 모듈 연동)
  │     └─ 각 워크스페이스별 creditManager.expireCreditsForMember() 호출
  │         ├─ ACTIVE 크레딧 잔액 → STTS_CD = 'EXPIRED'
  │         └─ TL_PAY_BILNG_EVNT INSERT (credit.expired)
  │
  │  5. 개인 워크스페이스(PERSONAL) Soft Delete
  │     └─ TB_COMM_WKSPC.STTS_CD = "DELETED", DEL_DT = NOW()
  │
  │  6. 인증 모듈의 기존 탈퇴 처리 계속 (개인정보 마스킹 등)
```

---

## 7. 보안 설계

### 7.1 접근 제어

| 항목 | 설계 |
|------|------|
| 멤버십 검증 | 모든 워크스페이스 API에서 멤버십 미들웨어 필수 적용 |
| 역할 계층 | OWNER > ADMIN > MEMBER > GUEST 순 권한 계층 |
| 자기 자신 보호 | 자신의 역할 변경/자신을 강제 퇴장 불가 |
| 마지막 OWNER 보호 | 워크스페이스에 최소 1명의 OWNER 유지 |

### 7.2 초대 보안

| 항목 | 설계 |
|------|------|
| 토큰 길이 | `nanoid(32)` 사용 (충분한 엔트로피) |
| 만료 시간 | 이메일 초대: 7일, 링크 초대: 최대 30일 |
| 사용 제한 | 링크 초대: `MAX_USE_CNT`로 제한 |
| 이메일 검증 | 이메일 초대: 수락 시 로그인 이메일과 초대 이메일 일치 확인 |
| 만료 초대 정리 | Cron Job으로 만료된 초대 상태 자동 업데이트 |


### 7.3 데이터 격리

| 항목 | 설계 |
|------|------|
| 논리적 격리 | 모든 워크스페이스 범위 데이터는 `WKSPC_ID` FK로 격리 |
| 쿼리 보호 | 워크스페이스 데이터 쿼리 시 항상 `WKSPC_ID` 조건 포함 |
| 교차 접근 방지 | 멤버십 미들웨어로 타 워크스페이스 데이터 접근 차단 |
| Soft Delete 격리 | 삭제된 워크스페이스 데이터는 `STTS_CD` 필터로 조회 제외 |

### 7.4 소유권 이전 보안

| 항목 | 설계 |
|------|------|
| 재인증 필요 | 소유권 이전 시 비밀번호 확인 또는 Firebase 재인증 요구 |
| 트랜잭션 보장 | 역할 변경을 단일 트랜잭션으로 처리하여 부분 실패 방지 |
| 감사 추적 | 소유권 이전 이벤트 감사 로그 필수 기록 |

### 7.5 Rate Limiting

| 엔드포인트 | 제한 | 창 |
|-----------|------|-----|
| `POST /workspaces` | 5회 | 1시간 |
| `POST /workspaces/:id/invitations` | 20회 | 1시간 |
| `POST /workspaces/:id/invitations/link` | 5회 | 1시간 |
| `POST /invitations/:token/accept` | 10회 | 1시간 |

---

## 8. 디렉토리 구조

### 8.1 신규 추가 파일 구조

```
app/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── workspaces/
│   │       │   ├── route.ts                           # GET, POST /api/v1/workspaces
│   │       │   └── [id]/
│   │       │       ├── route.ts                       # GET, PATCH, DELETE /api/v1/workspaces/:id
│   │       │       ├── switch/route.ts                # PATCH .../switch
│   │       │       ├── transfer-ownership/route.ts    # POST .../transfer-ownership
│   │       │       ├── members/
│   │       │       │   ├── route.ts                   # GET /api/v1/workspaces/:id/members
│   │       │       │   ├── leave/route.ts             # POST .../members/leave
│   │       │       │   └── [memberId]/
│   │       │       │       ├── role/route.ts          # PATCH .../members/:memberId/role
│   │       │       │       └── route.ts               # DELETE .../members/:memberId
│   │       │       └── invitations/
│   │       │           ├── route.ts                   # GET, POST /api/v1/workspaces/:id/invitations
│   │       │           ├── link/route.ts              # POST .../invitations/link
│   │       │           └── [invitationId]/route.ts    # DELETE .../invitations/:invitationId
│   │       └── invitations/
│   │           └── [token]/
│   │               ├── route.ts                       # GET /api/v1/invitations/:token
│   │               ├── accept/route.ts                # POST .../accept
│   │               └── decline/route.ts               # POST .../decline
│   └── [locale]/
│       ├── workspaces/
│       │   ├── page.tsx                               # 워크스페이스 목록/선택
│       │   ├── new/page.tsx                           # 워크스페이스 생성
│       │   └── [slug]/
│       │       ├── dashboard/page.tsx                 # 워크스페이스 대시보드
│       │       └── settings/
│       │           ├── page.tsx                       # 워크스페이스 일반 설정
│       │           └── members/page.tsx               # 멤버 관리
│       └── invitations/
│           └── [token]/page.tsx                       # 초대 수락 페이지
├── lib/
│   ├── db/
│   │   └── schema/
│   │       ├── auth.ts                                # (기존)
│   │       ├── workspace.ts                           # (신규) 워크스페이스 스키마
│   │       ├── iam.ts                                 # (기존)
│   │       ├── billing.ts                             # (수정) import 경로 변경
│   │       └── index.ts                               # 스키마 re-export (workspace 추가)
│   ├── workspace/
│   │   ├── membership-middleware.ts                    # 워크스페이스 멤버십 미들웨어
│   │   ├── invitation-service.ts                      # 초대 발송/검증 서비스
│   │   ├── workspace-service.ts                       # 워크스페이스 CRUD 서비스
│   │   └── slug-generator.ts                          # 슬러그 생성/중복 처리
│   └── validations/
│       ├── auth.ts                                    # (기존)
│       ├── workspace.ts                               # (신규) 워크스페이스 Zod 스키마
│       ├── iam.ts                                     # (기존)
│       └── billing.ts                                 # (기존)
├── contexts/
│   ├── AuthContext.tsx                                 # (기존)
│   ├── WorkspaceContext.tsx                            # (신규) 워크스페이스 상태 관리
│   └── SubscriptionContext.tsx                         # (기존)
├── hooks/
│   ├── useAuth.ts                                     # (기존)
│   ├── useWorkspace.ts                                # (신규) 현재 워크스페이스 훅
│   └── useWorkspaceRole.ts                            # (신규) 워크스페이스 역할 확인 훅
└── components/
    └── workspace/
        ├── WorkspaceSwitcher.tsx                       # 워크스페이스 전환 드롭다운
        ├── InviteMemberModal.tsx                       # 멤버 초대 모달
        ├── MemberRoleDropdown.tsx                      # 멤버 역할 변경 드롭다운
        ├── InvitationAcceptCard.tsx                    # 초대 수락 카드
        └── WorkspaceAvatar.tsx                         # 워크스페이스 로고/아바타
```

### 8.2 WorkspaceContext 설계

```typescript
// contexts/WorkspaceContext.tsx
interface WorkspaceInfo {
  id: number;
  slug: string;
  name: string;
  logoUrl: string | null;
  typeCd: 'PERSONAL' | 'TEAM';
  roleCd: 'OWNER' | 'ADMIN' | 'MEMBER' | 'GUEST';
  memberCount: number;
  maxMembers: number;
  statusCd: string;
  subscription: {
    planName: string;
    statusCd: string;
  } | null;
}

interface WorkspaceContextType {
  currentWorkspace: WorkspaceInfo | null;
  workspaces: WorkspaceInfo[];
  isLoading: boolean;
  switchWorkspace: (workspaceId: number) => Promise<void>;
  refreshWorkspaces: () => Promise<void>;
  isOwner: boolean;
  isAdmin: boolean;
  canManageBilling: boolean;
  canInviteMembers: boolean;
}
```

---

## 9. 구현 순서

### Phase 1: 기반 인프라 (1주차)

| 순서 | 작업 | 파일 |
|------|------|------|
| 1-1 | 의존성 설치 (`nanoid`, `slugify`) | `package.json` |
| 1-2 | 환경 변수 설정 | `.env.local` |
| 1-3 | Drizzle ORM 스키마 정의 | `lib/db/schema/workspace.ts` |
| 1-4 | DB 마이그레이션 실행 | DDL 적용 + `TB_COMM_USER.BSC_WKSPC_ID` 추가 |
| 1-5 | Zod 검증 스키마 | `lib/validations/workspace.ts` |
| 1-6 | 슬러그 생성 유틸 | `lib/workspace/slug-generator.ts` |

### Phase 2: 핵심 API (2주차)

| 순서 | 작업 | 파일 |
|------|------|------|
| 2-1 | 워크스페이스 멤버십 미들웨어 | `lib/workspace/membership-middleware.ts` |
| 2-2 | 워크스페이스 CRUD API | `app/api/v1/workspaces/...` |
| 2-3 | 멤버 관리 API | `app/api/v1/workspaces/[id]/members/...` |
| 2-4 | 워크스페이스 전환 API | `app/api/v1/workspaces/[id]/switch/...` |
| 2-5 | 소유권 이전 API | `app/api/v1/workspaces/[id]/transfer-ownership/...` |
| 2-6 | WorkspaceContext 구현 | `contexts/WorkspaceContext.tsx` |

### Phase 3: 초대 시스템 (3주차)

| 순서 | 작업 | 파일 |
|------|------|------|
| 3-1 | 초대 서비스 (이메일 발송 로직) | `lib/workspace/invitation-service.ts` |
| 3-2 | 이메일 초대 API | `app/api/v1/workspaces/[id]/invitations/...` |
| 3-3 | 초대 링크 생성 API | `app/api/v1/workspaces/[id]/invitations/link/...` |
| 3-4 | 초대 수락/거절 API | `app/api/v1/invitations/[token]/...` |
| 3-5 | 만료 초대 정리 Cron Job | 스케줄러 |

### Phase 4: 화면 구현 (4주차)

| 순서 | 작업 | 파일 |
|------|------|------|
| 4-1 | WorkspaceSwitcher 컴포넌트 | `components/workspace/WorkspaceSwitcher.tsx` |
| 4-2 | 워크스페이스 생성 페이지 | `app/[locale]/workspaces/new/page.tsx` |
| 4-3 | 워크스페이스 설정 페이지 | `app/[locale]/workspaces/[slug]/settings/page.tsx` |
| 4-4 | 멤버 관리 페이지 | `app/[locale]/workspaces/[slug]/settings/members/page.tsx` |
| 4-5 | 초대 수락 페이지 | `app/[locale]/invitations/[token]/page.tsx` |
| 4-6 | 멤버 초대 모달 | `components/workspace/InviteMemberModal.tsx` |

### Phase 5: 기존 시스템 통합 (5주차)

| 순서 | 작업 |
|------|------|
| 5-1 | 인증 모듈: 회원가입 시 개인 워크스페이스 자동 생성 로직 추가 |
| 5-2 | 인증 모듈: 회원 탈퇴 시 워크스페이스 처리 로직 추가 |
| 5-3 | 인증 모듈: JWT 토큰에 현재 워크스페이스 정보 추가 (선택) |
| 5-4 | 결제 모듈: `billing.ts` 스키마 import 경로 변경 (`./auth` → `./workspace`) |
| 5-5 | 결제 모듈: 구독 상태 변경 시 워크스페이스 `MAX_MBR_CNT` 연동 |
| 5-6 | IAM 모듈: 워크스페이스 리소스 권한 추가 (`workspace.*:action`) |
| 5-7 | 사이드바: WorkspaceSwitcher 통합 |
| 5-8 | 다국어 메시지 추가 (`messages/ko.json`, `messages/en.json`) |
| 5-9 | 기존 사용자 마이그레이션 (개인 워크스페이스 일괄 생성) |
| 5-10 | 통합 테스트 |

---

## 부록 A: 초기 데이터 (Seed)

```sql
-- 기존 사용자에 대한 개인 워크스페이스 일괄 생성 (마이그레이션 시)
INSERT INTO app.TB_COMM_WKSPC (SLUG, WKSPC_NM, OWNR_ID, TYPE_CD, MAX_MBR_CNT, STTS_CD)
SELECT
    CONCAT(LOWER(REPLACE(COALESCE(DSPLY_NM, 'user'), ' ', '-')), '-personal-', ID),
    CONCAT(COALESCE(DSPLY_NM, 'User'), '의 워크스페이스'),
    ID,
    'PERSONAL',
    1,
    'ACTIVE'
FROM app.TB_COMM_USER
WHERE STTS_CD = 'ACTIVE'
  AND DEL_DT IS NULL;

-- 개인 워크스페이스 멤버 자동 생성
INSERT INTO app.TR_COMM_WKSPC_MBR (WKSPC_ID, USER_ID, ROLE_CD, STTS_CD)
SELECT
    w.ID,
    w.OWNR_ID,
    'OWNER',
    'ACTIVE'
FROM app.TB_COMM_WKSPC w
WHERE w.TYPE_CD = 'PERSONAL';

-- 기본 워크스페이스 설정
UPDATE app.TB_COMM_USER u
SET BSC_WKSPC_ID = (
    SELECT w.ID FROM app.TB_COMM_WKSPC w
    WHERE w.OWNR_ID = u.ID AND w.TYPE_CD = 'PERSONAL'
    LIMIT 1
)
WHERE u.STTS_CD = 'ACTIVE' AND u.DEL_DT IS NULL;
```

## 부록 B: 초대 이메일 템플릿

```
제목: [{appName}] {inviterName}님이 "{workspaceName}" 워크스페이스에 초대했습니다

───────────────────────────────────
{inviterName}님이 {workspaceName}
워크스페이스에 초대했습니다.

역할: {roleName}
만료: {expiresAt}

[초대 수락하기] → {acceptUrl}

이 초대를 원하지 않으시면 무시하셔도 됩니다.
초대는 {expiresAt}에 자동 만료됩니다.
───────────────────────────────────
```
