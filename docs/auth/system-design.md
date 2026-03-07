# 공통 인증 시스템 설계 문서

> **프로젝트**: 공통 인증 모듈 (Authentication Module)
> **버전**: 1.0.0
> **작성일**: 2026-02-14
> **기반 레퍼런스**: xframe 인증 시스템 (Firebase + JWT)

---

## 목차

1. [아키텍처 개요](#1-아키텍처-개요)
2. [기술 스택](#2-기술-스택)
3. [데이터베이스 스키마](#3-데이터베이스-스키마)
4. [API 설계](#4-api-설계)
5. [화면 구성](#5-화면-구성)
6. [인증 흐름](#6-인증-흐름)
7. [보안 설계](#7-보안-설계)
8. [디렉토리 구조](#8-디렉토리-구조)
9. [구현 순서](#9-구현-순서)

---

## 1. 아키텍처 개요

### 1.1 설계 원칙

본 모듈은 **별도의 백엔드 API 프로젝트 없이** Next.js 14 App Router의 API Routes와 Server Actions를 활용하여 인증 시스템을 구현한다. xframe의 인증 아키텍처(Firebase + JWT + 약관 관리)를 참조하되, 단일 프로젝트 내에서 프론트엔드와 백엔드를 모두 처리하는 풀스택 구조로 설계한다.

### 1.2 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────┐
│                    APP (Next.js 14)                      │
│                                                          │
│  ┌──────────────┐    ┌──────────────────────────────┐   │
│  │  Client-Side │    │        Server-Side            │   │
│  │              │    │                                │   │
│  │  Pages/      │───▶│  API Routes (/app/api/...)    │   │
│  │  Components  │    │  Server Actions               │   │
│  │  AuthContext  │    │  Middleware (JWT 검증)         │   │
│  │              │◀───│                                │   │
│  └──────────────┘    └───────────┬──────────────────┘   │
│                                   │                      │
└───────────────────────────────────┼──────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              ┌──────────┐   ┌──────────┐   ┌──────────┐
              │ Firebase  │   │PostgreSQL│   │  SMTP    │
              │   Auth    │   │(Drizzle) │   │ (메일)   │
              └──────────┘   └──────────┘   └──────────┘
```

### 1.3 xframe과의 차이점

| 항목 | xframe | 본 모듈 |
|------|--------|-----|
| 백엔드 프레임워크 | Hono (별도 서버) | Next.js API Routes (동일 프로젝트) |
| ORM | Drizzle ORM | Drizzle ORM |
| 인증 제공자 | Firebase Authentication | Firebase Authentication |
| 토큰 관리 | JWT (Access + Refresh) | JWT (Access + Refresh) |
| 토큰 저장 | HttpOnly Cookies (Server Action) | HttpOnly Cookies (Server Action) |
| API 통신 | REST API (별도 서버) | Next.js API Routes + Server Actions |
| 약관 관리 | 별도 API 서버 | Next.js API Routes |
| 워크스페이스 | 미지원 | 회원가입 시 개인 워크스페이스 자동 생성, `BSC_WKSPC_ID`로 기본 워크스페이스 관리 |

### 1.4 타 모듈과의 관계

| 항목 | 인증 모듈 | 워크스페이스 모듈 | IAM 모듈 | 결제 모듈 |
|------|----------|-----------------|----------|----------|
| 사용자 식별 | `TB_COMM_USER.ID` 정의 | `TB_COMM_WKSPC_MBR.USER_ID` FK 참조 | `TB_IAM_USER_ROLE.USER_ID` FK 참조 | 감사 로그에서 FK 참조 |
| 워크스페이스 연결 | `TB_COMM_USER.BSC_WKSPC_ID` FK 참조 | `TB_COMM_WKSPC.ID` 정의 | 권한 검사 시 워크스페이스 컨텍스트 참조 | `WKSPC_ID` FK 참조 |
| 트리거 이벤트 | 회원가입 → 워크스페이스 모듈에 개인 WS 생성 요청 | 초대 수락 → 멤버 추가 | 역할 변경 → 감사 로그 | 구독 생성 → 워크스페이스 플랜 반영 |
| 탈퇴 처리 | 사용자 Soft Delete + 워크스페이스 모듈에 소유 WS 처리 위임 | 소유한 팀 WS 이전/삭제, 멤버십 정리 | 역할 매핑 정리 | 구독 해지 처리 |
| DB 스키마 | `app` 스키마 (`TB_COMM_USER`, `TB_COMM_TRMS` 등) | `app` 스키마 (`TB_COMM_WKSPC` 등) | `app` 스키마 (`TB_IAM_ROLE` 등) | `app` 스키마 (`TB_PAY_` 테이블) |

---

## 2. 기술 스택

### 2.1 신규 추가 의존성

```json
{
  "dependencies": {
    "firebase": "^11.x",
    "drizzle-orm": "^0.38.x",
    "postgres": "^3.4.x",
    "jose": "^6.x",
    "bcryptjs": "^3.x",
    "zod": "^3.x"
  },
  "devDependencies": {
    "drizzle-kit": "^0.30.x",
    "@types/bcryptjs": "^2.x"
  }
}
```

| 패키지 | 용도 |
|--------|------|
| `firebase` | Firebase Authentication 클라이언트 SDK (소셜 로그인) |
| `drizzle-orm` + `postgres` | PostgreSQL ORM (타입 안전 쿼리) |
| `jose` | JWT 생성/검증 (Edge Runtime 호환) |
| `bcryptjs` | 비밀번호 해싱 (이메일 회원가입 시) |
| `zod` | 요청 유효성 검증 스키마 |

### 2.2 환경 변수

```env
# Database
DATABASE_URL=postgresql://astra_staging:Astra%402025@34.64.188.199:5432/astra_staging
DATABASE_SCHEMA=app

# JWT
JWT_SECRET=your-256-bit-secret-key-here
JWT_ACCESS_EXPIRES=30m
JWT_REFRESH_EXPIRES=7d

# Firebase
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
NEXT_PUBLIC_FIREBASE_PROJECT_ID=...
FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}

# App
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

---

## 3. 데이터베이스 스키마

### 3.1 ER 다이어그램

```
┌────────────────────┐    ┌────────────────────┐    ┌────────────────────────┐
│   TB_COMM_USER      │    │   TB_COMM_TRMS      │    │  TB_COMM_RFRSH_TKN     │
├────────────────────┤    ├────────────────────┤    ├────────────────────────┤
│ ID (PK)            │    │ ID (PK)            │    │ ID (PK)                │
│ UID (UK)           │    │ TY_CD              │    │ USER_ID (FK)           │
│ EML_ADDR           │◀─┐│ VER_NO             │    │ TKN_HASH (UK)          │
│ INDCT_NM           │  ││ TTL                │    │ DVC_ID                 │
│ PVSN_CD            │  ││ CN                 │    │ DVC_INFO               │
│ ROLE_CD            │  ││ REQD_YN            │    │ EXPRY_DT               │
│ STTS_CD            │  ││ ENFC_DT            │    │ DSCD_DT                │
│ BSC_WKSPC_ID ──────┼──┼│ ACTV_YN            │    │ CRT_DT                 │
│ ...                │  ││ ...                │    └────────────────────────┘
└─────────┬──────────┘  │└─────────┬──────────┘
          │             │          │
          │    ┌────────┴──────────┴──────┐
          │    │  TH_COMM_USER_AGRE        │
          └───▶├──────────────────────────┤
               │ ID (PK)                  │
               │ USER_ID (FK)             │
               │ TRMS_ID (FK)             │
               │ AGRE_YN                  │
               │ AGRE_DT                  │
               │ IP_ADDR                  │
               │ DVC_INFO                 │
               │ ...                      │
               └──────────────────────────┘

         ┌─────────────────────────────────┐
         │ TB_COMM_WKSPC (워크스페이스 모듈)  │
         ├─────────────────────────────────┤
         │ ID (PK) ◀── TB_COMM_USER.      │
         │               BSC_WKSPC_ID     │
         │ SLUG (UK)                       │
         │ NM                              │
         │ OWNR_ID (FK → TB_COMM_USER)     │
         │ TY_CD (PERSONAL/TEAM)           │
         │ ...                             │
         └─────────────────────────────────┘
```

> **참고**: `TB_COMM_WKSPC` 테이블의 전체 스키마는 [워크스페이스 관리 시스템 설계 문서](./workspace.md)를 참조한다.

### 3.2 TB_COMM_USER 테이블

사용자 계정 정보를 관리하는 핵심 테이블.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 사용자 고유 식별자 |
| `UID` | `VARCHAR(128)` | `UNIQUE NOT NULL` | - | Firebase UID |
| `EML_ADDR` | `VARCHAR(100)` | `INDEX` | NULL | 이메일 주소 |
| `TELNO` | `VARCHAR(20)` | - | NULL | 전화번호 |
| `INDCT_NM` | `VARCHAR(100)` | - | NULL | 표시 이름 |
| `PHOTO_URL` | `VARCHAR(2000)` | - | NULL | 프로필 이미지 URL |
| `PVSN_CD` | `VARCHAR(20)` | `NOT NULL` | - | 인증 제공자 코드 |
| `ROLE_CD` | `VARCHAR(20)` | `NOT NULL` | `'USER'` | 사용자 역할 코드 |
| `STTS_CD` | `VARCHAR(20)` | `NOT NULL` | `'ACTIVE'` | 계정 상태 코드 |
| `EML_CERT_YN` | `CHAR(1)` | `NOT NULL` | `'N'` | 이메일 인증 여부 (Y/N) |
| `AUTHRT` | `VARCHAR(500)` | - | NULL | 추가 권한 (공백 구분) |
| `PVSN_UID` | `VARCHAR(256)` | - | NULL | 제공자별 고유 ID |
| `PVSN_DATA` | `JSONB` | - | NULL | Firebase 제공자 데이터 |
| `LAST_CNTN_DT` | `TIMESTAMPTZ` | - | NULL | Firebase 마지막 로그인 일시 |
| `LAST_LOGIN_DT` | `TIMESTAMPTZ` | - | NULL | 서비스 마지막 로그인 일시 |
| `BSC_WKSPC_ID` | `BIGINT` | `FK(TB_COMM_WKSPC.ID)` | NULL | 기본 워크스페이스 ID (로그인 시 진입 워크스페이스) |
| `WHDWL_DT` | `TIMESTAMPTZ` | - | NULL | 탈퇴 일시 |
| `DEL_DT` | `TIMESTAMPTZ` | - | NULL | Soft Delete 일시 |
| `CRTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 생성자 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 생성 일시 |
| `MDFR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 수정자 |
| `MDFCN_DT` | `TIMESTAMPTZ` | - | NULL | 수정 일시 |

**인덱스**:
```sql
CREATE UNIQUE INDEX idx_tb_comm_user_uid ON app.TB_COMM_USER(UID);
CREATE INDEX idx_tb_comm_user_eml_addr ON app.TB_COMM_USER(EML_ADDR);
CREATE INDEX idx_tb_comm_user_stts_cd ON app.TB_COMM_USER(STTS_CD);
CREATE INDEX idx_tb_comm_user_bsc_wkspc ON app.TB_COMM_USER(BSC_WKSPC_ID);
```

**Enum 값**:

| 코드 유형 | 코드 | 한글명 | 설명 |
|-----------|------|--------|------|
| `AUTH_PROVIDER` | `EMAIL` | 이메일 | 이메일/비밀번호 인증 |
| | `GOOGLE` | 구글 | Google OAuth |
| | `APPLE` | 애플 | Apple Sign In |
| | `KAKAO` | 카카오 | Kakao OAuth |
| `USER_ROLE` | `USER` | 일반 사용자 | 기본 역할 |
| | `ADMIN` | 관리자 | 전체 관리 권한 |
| | `MANAGER` | 매니저 | 사용자 관리 권한 |
| `USER_STATUS` | `ACTIVE` | 정상 | 정상 활성 계정 |
| | `SUSPENDED` | 정지 | 이용 정지 |
| | `WITHDRAWN` | 탈퇴 | 탈퇴 처리 |

### 3.3 TB_COMM_TRMS 테이블

약관 정보를 관리하는 테이블. 유형별 버전 관리를 지원한다.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 약관 고유 식별자 |
| `TY_CD` | `VARCHAR(20)` | `NOT NULL` | - | 약관 유형 코드 |
| `VER_NO` | `VARCHAR(10)` | `NOT NULL` | - | 약관 버전 (예: "1.0") |
| `TTL` | `VARCHAR(200)` | `NOT NULL` | - | 약관 제목 |
| `CN` | `VARCHAR(4000)` | `NOT NULL` | - | 약관 전문 (HTML/Markdown) |
| `REQD_YN` | `CHAR(1)` | `NOT NULL` | `'Y'` | 필수 동의 여부 (Y/N) |
| `ENFC_DT` | `DATE` | `NOT NULL` | - | 시행일 |
| `ACTV_YN` | `CHAR(1)` | `NOT NULL` | `'Y'` | 활성 여부 (Y/N) |
| `CRTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 생성자 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 생성 일시 |
| `MDFR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 수정자 |
| `MDFCN_DT` | `TIMESTAMPTZ` | - | NULL | 수정 일시 |

**제약조건**:
```sql
CONSTRAINT uq_tb_comm_trms_ty_ver UNIQUE (TY_CD, VER_NO)
```

**인덱스**:
```sql
CREATE INDEX idx_tb_comm_trms_ty_actv ON app.TB_COMM_TRMS(TY_CD, ACTV_YN);
```

**약관 유형 (TERMS_TYPE)**:

| 코드 | 한글명 | 필수 여부 | 설명 |
|------|--------|----------|------|
| `SERVICE` | 서비스 이용약관 | 필수 | 서비스 이용 조건 |
| `PRIVACY` | 개인정보 처리방침 | 필수 | 개인정보 수집/이용 동의 |
| `MARKETING` | 마케팅 수신 동의 | 선택 | 마케팅 정보 수신 동의 |
| `THIRD_PARTY` | 제3자 정보 제공 | 선택 | 제3자 정보 제공 동의 |

### 3.4 TH_COMM_USER_AGRE 테이블

사용자별 약관 동의 이력을 관리하는 테이블.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 동의 이력 식별자 |
| `USER_ID` | `BIGINT` | `FK(TB_COMM_USER.ID) ON DELETE CASCADE, NOT NULL` | - | 사용자 FK |
| `TRMS_ID` | `BIGINT` | `FK(TB_COMM_TRMS.ID), NOT NULL` | - | 약관 FK |
| `AGRE_YN` | `CHAR(1)` | `NOT NULL` | `'Y'` | 동의 여부 (Y/N) |
| `AGRE_DT` | `TIMESTAMPTZ` | `NOT NULL` | - | 동의 일시 |
| `IP_ADDR` | `VARCHAR(45)` | - | NULL | 동의 시 IP 주소 (IPv6 지원) |
| `DVC_INFO` | `VARCHAR(200)` | - | NULL | 디바이스 정보 (User-Agent) |
| `CRTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 생성자 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 생성 일시 |
| `MDFR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 수정자 |
| `MDFCN_DT` | `TIMESTAMPTZ` | - | NULL | 수정 일시 |

**제약조건**:
```sql
CONSTRAINT uq_th_comm_user_agre_user_trms UNIQUE (USER_ID, TRMS_ID)
```

**인덱스**:
```sql
CREATE INDEX idx_th_comm_user_agre_user_id ON app.TH_COMM_USER_AGRE(USER_ID);
CREATE INDEX idx_th_comm_user_agre_trms_id ON app.TH_COMM_USER_AGRE(TRMS_ID);
```

### 3.5 TB_COMM_RFRSH_TKN 테이블

Refresh Token을 관리하는 테이블. 디바이스별 세션 관리를 지원한다.

| 컬럼명 | 타입 | 제약조건 | 기본값 | 설명 |
|--------|------|---------|--------|------|
| `ID` | `BIGSERIAL` | `PRIMARY KEY` | AUTO | 토큰 식별자 |
| `USER_ID` | `BIGINT` | `FK(TB_COMM_USER.ID) ON DELETE CASCADE, NOT NULL` | - | 사용자 FK |
| `TKN_HASH` | `VARCHAR(256)` | `UNIQUE NOT NULL` | - | 토큰 SHA-256 해시 |
| `DVC_ID` | `VARCHAR(100)` | - | NULL | 디바이스 식별자 |
| `DVC_INFO` | `VARCHAR(200)` | - | NULL | 디바이스 정보 |
| `EXPRY_DT` | `TIMESTAMPTZ` | `NOT NULL` | - | 만료 일시 |
| `DSCD_DT` | `TIMESTAMPTZ` | - | NULL | 폐기 일시 |
| `CRTR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 생성자 |
| `CRT_DT` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 생성 일시 |
| `MDFR_ID` | `BIGINT` | `FK(TB_COMM_USER.ID)` | NULL | 수정자 |
| `MDFCN_DT` | `TIMESTAMPTZ` | - | NULL | 수정 일시 |

**인덱스**:
```sql
CREATE UNIQUE INDEX idx_tb_comm_rfrsh_tkn_hash ON app.TB_COMM_RFRSH_TKN(TKN_HASH);
CREATE INDEX idx_tb_comm_rfrsh_tkn_user_id ON app.TB_COMM_RFRSH_TKN(USER_ID);
CREATE INDEX idx_tb_comm_rfrsh_tkn_expry ON app.TB_COMM_RFRSH_TKN(EXPRY_DT);
```

### 3.6 DDL 전문

```sql
-- 스키마 생성
CREATE SCHEMA IF NOT EXISTS app;

-- ============================================
-- 1. TB_COMM_USER 테이블
-- ============================================
CREATE TABLE app.TB_COMM_USER (
    ID              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    UID             VARCHAR(128)    NOT NULL,
    EML_ADDR        VARCHAR(100),
    TELNO           VARCHAR(20),
    INDCT_NM        VARCHAR(100),
    PHOTO_URL       VARCHAR(2000),
    PVSN_CD         VARCHAR(20)     NOT NULL,
    ROLE_CD         VARCHAR(20)     NOT NULL DEFAULT 'USER',
    STTS_CD         VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    EML_CERT_YN     CHAR(1)         NOT NULL DEFAULT 'N',
    AUTHRT          VARCHAR(500),
    PVSN_UID        VARCHAR(256),
    PVSN_DATA       JSONB,
    LAST_CNTN_DT    TIMESTAMPTZ,
    LAST_LOGIN_DT   TIMESTAMPTZ,
    BSC_WKSPC_ID    BIGINT,
    WHDWL_DT        TIMESTAMPTZ,
    DEL_DT          TIMESTAMPTZ,
    CRTR_ID         BIGINT,
    CRT_DT          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    MDFR_ID         BIGINT,
    MDFCN_DT        TIMESTAMPTZ,
    CONSTRAINT fk_tb_comm_user_crtr FOREIGN KEY (CRTR_ID) REFERENCES app.TB_COMM_USER(ID),
    CONSTRAINT fk_tb_comm_user_mdfr FOREIGN KEY (MDFR_ID) REFERENCES app.TB_COMM_USER(ID),
    CONSTRAINT fk_tb_comm_user_bsc_wkspc FOREIGN KEY (BSC_WKSPC_ID) REFERENCES app.TB_COMM_WKSPC(ID) ON DELETE SET NULL
);

CREATE UNIQUE INDEX idx_tb_comm_user_uid ON app.TB_COMM_USER(UID);
CREATE INDEX idx_tb_comm_user_eml_addr ON app.TB_COMM_USER(EML_ADDR);
CREATE INDEX idx_tb_comm_user_stts_cd ON app.TB_COMM_USER(STTS_CD);
CREATE INDEX idx_tb_comm_user_bsc_wkspc ON app.TB_COMM_USER(BSC_WKSPC_ID);

-- ============================================
-- 2. TB_COMM_TRMS 테이블
-- ============================================
CREATE TABLE app.TB_COMM_TRMS (
    ID              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    TY_CD           VARCHAR(20)     NOT NULL,
    VER_NO          VARCHAR(10)     NOT NULL,
    TTL             VARCHAR(200)    NOT NULL,
    CN              VARCHAR(4000)   NOT NULL,
    REQD_YN         CHAR(1)         NOT NULL DEFAULT 'Y',
    ENFC_DT         DATE            NOT NULL,
    ACTV_YN         CHAR(1)         NOT NULL DEFAULT 'Y',
    CRTR_ID         BIGINT          REFERENCES app.TB_COMM_USER(ID),
    CRT_DT          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    MDFR_ID         BIGINT          REFERENCES app.TB_COMM_USER(ID),
    MDFCN_DT        TIMESTAMPTZ,
    CONSTRAINT uq_tb_comm_trms_ty_ver UNIQUE (TY_CD, VER_NO)
);

CREATE INDEX idx_tb_comm_trms_ty_actv ON app.TB_COMM_TRMS(TY_CD, ACTV_YN);

-- ============================================
-- 3. TH_COMM_USER_AGRE 테이블
-- ============================================
CREATE TABLE app.TH_COMM_USER_AGRE (
    ID              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    USER_ID         BIGINT          NOT NULL REFERENCES app.TB_COMM_USER(ID) ON DELETE CASCADE,
    TRMS_ID         BIGINT          NOT NULL REFERENCES app.TB_COMM_TRMS(ID),
    AGRE_YN         CHAR(1)         NOT NULL DEFAULT 'Y',
    AGRE_DT         TIMESTAMPTZ     NOT NULL,
    IP_ADDR         VARCHAR(45),
    DVC_INFO        VARCHAR(200),
    CRTR_ID         BIGINT          REFERENCES app.TB_COMM_USER(ID),
    CRT_DT          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    MDFR_ID         BIGINT          REFERENCES app.TB_COMM_USER(ID),
    MDFCN_DT        TIMESTAMPTZ,
    CONSTRAINT uq_th_comm_user_agre_user_trms UNIQUE (USER_ID, TRMS_ID)
);

CREATE INDEX idx_th_comm_user_agre_user_id ON app.TH_COMM_USER_AGRE(USER_ID);
CREATE INDEX idx_th_comm_user_agre_trms_id ON app.TH_COMM_USER_AGRE(TRMS_ID);

-- ============================================
-- 4. TB_COMM_RFRSH_TKN 테이블
-- ============================================
CREATE TABLE app.TB_COMM_RFRSH_TKN (
    ID              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    USER_ID         BIGINT          NOT NULL REFERENCES app.TB_COMM_USER(ID) ON DELETE CASCADE,
    TKN_HASH        VARCHAR(256)    NOT NULL,
    DVC_ID          VARCHAR(100),
    DVC_INFO        VARCHAR(200),
    EXPRY_DT        TIMESTAMPTZ     NOT NULL,
    DSCD_DT         TIMESTAMPTZ,
    CRTR_ID         BIGINT          REFERENCES app.TB_COMM_USER(ID),
    CRT_DT          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    MDFR_ID         BIGINT          REFERENCES app.TB_COMM_USER(ID),
    MDFCN_DT        TIMESTAMPTZ
);

CREATE UNIQUE INDEX idx_tb_comm_rfrsh_tkn_hash ON app.TB_COMM_RFRSH_TKN(TKN_HASH);
CREATE INDEX idx_tb_comm_rfrsh_tkn_user_id ON app.TB_COMM_RFRSH_TKN(USER_ID);
CREATE INDEX idx_tb_comm_rfrsh_tkn_expry ON app.TB_COMM_RFRSH_TKN(EXPRY_DT);
```

### 3.7 Drizzle ORM 스키마 정의

```typescript
// lib/db/schema/auth.ts
import {
  pgSchema, bigint, varchar, char, date,
  timestamp, jsonb, uniqueIndex, index
} from 'drizzle-orm/pg-core';

export const app = pgSchema('app');

// ---- TB_COMM_USER ----
export const users = app.table('TB_COMM_USER', {
  id:               bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  uid:              varchar('UID', { length: 128 }).notNull(),
  emlAddr:          varchar('EML_ADDR', { length: 100 }),
  telno:            varchar('TELNO', { length: 20 }),
  indctNm:          varchar('INDCT_NM', { length: 100 }),
  photoUrl:         varchar('PHOTO_URL', { length: 2000 }),
  pvsnCd:           varchar('PVSN_CD', { length: 20 }).notNull(),
  roleCd:           varchar('ROLE_CD', { length: 20 }).notNull().default('USER'),
  sttsCd:           varchar('STTS_CD', { length: 20 }).notNull().default('ACTIVE'),
  emlCertYn:        char('EML_CERT_YN', { length: 1 }).notNull().default('N'),
  authrt:           varchar('AUTHRT', { length: 500 }),
  pvsnUid:          varchar('PVSN_UID', { length: 256 }),
  pvsnData:         jsonb('PVSN_DATA'),
  lastCntnDt:       timestamp('LAST_CNTN_DT', { withTimezone: true }),
  lastLoginDt:      timestamp('LAST_LOGIN_DT', { withTimezone: true }),
  bscWkspcId:       bigint('BSC_WKSPC_ID', { mode: 'number' }),  // FK → TB_COMM_WKSPC.ID (워크스페이스 모듈)
  whdwlDt:          timestamp('WHDWL_DT', { withTimezone: true }),
  delDt:            timestamp('DEL_DT', { withTimezone: true }),
  crtrId:           bigint('CRTR_ID', { mode: 'number' }),
  crtDt:            timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
  mdfrId:           bigint('MDFR_ID', { mode: 'number' }),
  mdfcnDt:          timestamp('MDFCN_DT', { withTimezone: true }),
}, (table) => [
  uniqueIndex('idx_tb_comm_user_uid').on(table.uid),
  index('idx_tb_comm_user_eml_addr').on(table.emlAddr),
  index('idx_tb_comm_user_stts_cd').on(table.sttsCd),
  index('idx_tb_comm_user_bsc_wkspc').on(table.bscWkspcId),
]);

// NOTE: bscWkspcId의 FK 관계는 워크스페이스 모듈(lib/db/schema/workspace.ts)의
// TB_COMM_WKSPC 테이블을 참조한다. 순환 참조를 방지하기 위해 Drizzle relations에서 설정한다.

// ---- TB_COMM_TRMS ----
export const terms = app.table('TB_COMM_TRMS', {
  id:            bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  tyCd:          varchar('TY_CD', { length: 20 }).notNull(),
  verNo:         varchar('VER_NO', { length: 10 }).notNull(),
  ttl:           varchar('TTL', { length: 200 }).notNull(),
  cn:            varchar('CN', { length: 4000 }).notNull(),
  reqdYn:        char('REQD_YN', { length: 1 }).notNull().default('Y'),
  enfcDt:        date('ENFC_DT').notNull(),
  actvYn:        char('ACTV_YN', { length: 1 }).notNull().default('Y'),
  crtrId:        bigint('CRTR_ID', { mode: 'number' }),
  crtDt:         timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
  mdfrId:        bigint('MDFR_ID', { mode: 'number' }),
  mdfcnDt:       timestamp('MDFCN_DT', { withTimezone: true }),
}, (table) => [
  uniqueIndex('uq_tb_comm_trms_ty_ver').on(table.tyCd, table.verNo),
  index('idx_tb_comm_trms_ty_actv').on(table.tyCd, table.actvYn),
]);

// ---- TH_COMM_USER_AGRE ----
export const userAgreements = app.table('TH_COMM_USER_AGRE', {
  id:          bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  userId:      bigint('USER_ID', { mode: 'number' }).notNull().references(() => users.id, { onDelete: 'cascade' }),
  trmsId:      bigint('TRMS_ID', { mode: 'number' }).notNull().references(() => terms.id),
  agreYn:      char('AGRE_YN', { length: 1 }).notNull().default('Y'),
  agreDt:      timestamp('AGRE_DT', { withTimezone: true }).notNull(),
  ipAddr:      varchar('IP_ADDR', { length: 45 }),
  dvcInfo:     varchar('DVC_INFO', { length: 200 }),
  crtrId:      bigint('CRTR_ID', { mode: 'number' }),
  crtDt:       timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
  mdfrId:      bigint('MDFR_ID', { mode: 'number' }),
  mdfcnDt:     timestamp('MDFCN_DT', { withTimezone: true }),
}, (table) => [
  uniqueIndex('uq_th_comm_user_agre_user_trms').on(table.userId, table.trmsId),
  index('idx_th_comm_user_agre_user_id').on(table.userId),
  index('idx_th_comm_user_agre_trms_id').on(table.trmsId),
]);

// ---- TB_COMM_RFRSH_TKN ----
export const refreshTokens = app.table('TB_COMM_RFRSH_TKN', {
  id:          bigint('ID', { mode: 'number' }).primaryKey().generatedAlwaysAsIdentity(),
  userId:      bigint('USER_ID', { mode: 'number' }).notNull().references(() => users.id, { onDelete: 'cascade' }),
  tknHash:     varchar('TKN_HASH', { length: 256 }).notNull(),
  dvcId:       varchar('DVC_ID', { length: 100 }),
  dvcInfo:     varchar('DVC_INFO', { length: 200 }),
  expryDt:     timestamp('EXPRY_DT', { withTimezone: true }).notNull(),
  dscdDt:      timestamp('DSCD_DT', { withTimezone: true }),
  crtrId:      bigint('CRTR_ID', { mode: 'number' }),
  crtDt:       timestamp('CRT_DT', { withTimezone: true }).notNull().defaultNow(),
  mdfrId:      bigint('MDFR_ID', { mode: 'number' }),
  mdfcnDt:     timestamp('MDFCN_DT', { withTimezone: true }),
}, (table) => [
  uniqueIndex('idx_tb_comm_rfrsh_tkn_hash').on(table.tknHash),
  index('idx_tb_comm_rfrsh_tkn_user_id').on(table.userId),
  index('idx_tb_comm_rfrsh_tkn_expry').on(table.expryDt),
]);
```

---

## 4. API 설계

### 4.1 API 엔드포인트 총괄

모든 API는 Next.js API Routes (`app/api/v1/...`)로 구현한다.

#### 4.1.1 인증 API (`/api/v1/auth`)

| Method | Path | Auth | 설명 |
|--------|------|------|------|
| `POST` | `/api/v1/auth/signup` | Public | 회원가입 |
| `POST` | `/api/v1/auth/login` | Public | 로그인 |
| `POST` | `/api/v1/auth/refresh` | Public | 액세스 토큰 갱신 |
| `POST` | `/api/v1/auth/logout` | Bearer | 로그아웃 (현재 디바이스) |
| `POST` | `/api/v1/auth/logout-all` | Bearer | 전체 디바이스 로그아웃 |

#### 4.1.2 사용자 API (`/api/v1/users`)

| Method | Path | Auth | 설명 |
|--------|------|------|------|
| `GET` | `/api/v1/users/me` | Bearer | 내 프로필 조회 |
| `PATCH` | `/api/v1/users/me` | Bearer | 내 프로필 수정 |
| `DELETE` | `/api/v1/users/me` | Bearer | 회원 탈퇴 (Soft Delete) |
| `GET` | `/api/v1/users` | ADMIN | 사용자 목록 조회 (페이징) |
| `GET` | `/api/v1/users/[id]` | ADMIN | 사용자 상세 조회 |
| `PATCH` | `/api/v1/users/[id]/role` | ADMIN | 역할 변경 |
| `POST` | `/api/v1/users/[id]/suspend` | ADMIN/MANAGER | 계정 정지 |
| `POST` | `/api/v1/users/[id]/activate` | ADMIN/MANAGER | 계정 활성화 |

#### 4.1.3 약관 API (`/api/v1/terms`)

| Method | Path | Auth | 설명 |
|--------|------|------|------|
| `GET` | `/api/v1/terms/active` | Public | 활성 약관 목록 |
| `GET` | `/api/v1/terms/[id]` | Public | 약관 상세 조회 |
| `GET` | `/api/v1/terms/pending` | Bearer | 미동의 약관 목록 |
| `GET` | `/api/v1/terms/my/agreements` | Bearer | 내 약관 동의 현황 |
| `POST` | `/api/v1/terms/agree` | Bearer | 약관 동의 |
| `DELETE` | `/api/v1/terms/[id]/revoke` | Bearer | 선택 약관 동의 철회 |
| `GET` | `/api/v1/terms` | ADMIN | 전체 약관 목록 (관리용) |
| `POST` | `/api/v1/terms` | ADMIN | 약관 생성 |
| `PATCH` | `/api/v1/terms/[id]` | ADMIN | 약관 수정 |

### 4.2 상세 API 스펙

#### 4.2.1 POST /api/v1/auth/signup (회원가입)

**Request Body** (Zod Schema):
```typescript
const signupSchema = z.object({
  id_token: z.string().min(1),                           // Firebase ID Token
  display_nm: z.string().max(100).optional(),             // 표시 이름
  agreed_terms_ids: z.array(z.number()).min(1),           // 동의한 약관 ID 배열
  device_id: z.string().max(100).optional(),              // 디바이스 식별자
  device_info: z.string().max(200).optional(),            // 디바이스 정보
});
```

**Response 201** (성공):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "uid": "firebase-uid-xxx",
    "email": "user@example.com",
    "display_nm": "홍길동",
    "photo_url": "https://lh3.googleusercontent.com/...",
    "provider_cd": "GOOGLE",
    "role_cd": "USER",
    "status_cd": "ACTIVE",
    "default_ws_id": 1,
    "created_at": "2026-02-14T10:00:00Z"
  },
  "default_workspace": {
    "id": 1,
    "slug": "honggildong-ws",
    "name": "홍길동의 워크스페이스",
    "type_cd": "PERSONAL",
    "role_cd": "OWNER"
  }
}
```

**에러 응답**:

| HTTP 상태 | 에러 코드 | 설명 |
|-----------|----------|------|
| 400 | `VALIDATION_ERROR` | 요청 데이터 유효성 실패 |
| 400 | `REQUIRED_TERMS_NOT_AGREED` | 필수 약관 미동의 |
| 409 | `USER_ALREADY_EXISTS` | 이미 가입된 Firebase UID |
| 401 | `INVALID_ID_TOKEN` | Firebase ID Token 검증 실패 |

**비즈니스 로직**:
1. Firebase ID Token 검증 (Firebase Admin SDK)
2. uid로 기존 사용자 중복 검사
3. 필수 약관 (`REQD_YN = 'Y'`) 전체 동의 여부 검증
4. **[트랜잭션 시작]**
5. `TB_COMM_USER` 테이블에 사용자 생성
6. `TH_COMM_USER_AGRE` 테이블에 동의 이력 저장 (IP, Device 포함)
7. **개인 워크스페이스 자동 생성** (워크스페이스 모듈 호출):
   - `TB_COMM_WKSPC` 생성: `TY_CD='PERSONAL'`, `NM='{INDCT_NM}의 워크스페이스'`, `OWNR_ID=사용자ID`
   - `TB_COMM_WKSPC_MBR` 생성: `ROLE_CD='OWNER'`, `STTS_CD='ACTIVE'`
   - `TB_COMM_USER.BSC_WKSPC_ID` 업데이트: 생성된 개인 워크스페이스 ID로 설정
8. **[트랜잭션 커밋]**
9. Access Token (30분) + Refresh Token (7일) 생성
10. Refresh Token 해시를 `TB_COMM_RFRSH_TKN` 테이블에 저장
11. HttpOnly 쿠키에 토큰 저장 (Server Action)

> **워크스페이스 연동**: 회원가입 시 개인 워크스페이스가 자동 생성되며, 사용자는 즉시 서비스를 이용할 수 있다. 상세한 워크스페이스 생성 플로우는 [워크스페이스 관리 시스템 설계 문서 UC-01](./workspace.md#uc-01-회원가입-시-개인-워크스페이스-자동-생성)을 참조한다.

---

#### 4.2.2 POST /api/v1/auth/login (로그인)

**Request Body**:
```typescript
const loginSchema = z.object({
  id_token: z.string().min(1),                // Firebase ID Token
  device_id: z.string().max(100).optional(),
  device_info: z.string().max(200).optional(),
});
```

**Response 200** (성공):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 1800,
  "user": { ... },
  "default_workspace": {
    "id": 1,
    "slug": "honggildong-ws",
    "name": "홍길동의 워크스페이스",
    "type_cd": "PERSONAL",
    "role_cd": "OWNER"
  },
  "workspaces": [
    { "id": 1, "slug": "honggildong-ws", "name": "홍길동의 워크스페이스", "type_cd": "PERSONAL", "role_cd": "OWNER" },
    { "id": 5, "slug": "astravision", "name": "Astravision", "type_cd": "TEAM", "role_cd": "MEMBER" }
  ],
  "requires_signup": false,
  "requires_terms_agreement": true,
  "pending_terms": [
    {
      "id": 5,
      "type_cd": "PRIVACY",
      "version": "2.0",
      "title": "개인정보 처리방침 v2.0",
      "required_yn": true
    }
  ]
}
```

**에러 응답**:

| HTTP 상태 | 에러 코드 | 설명 |
|-----------|----------|------|
| 401 | `INVALID_ID_TOKEN` | Firebase ID Token 검증 실패 |
| 404 | `USER_NOT_FOUND` | 미가입 사용자 (→ `requires_signup: true` 반환) |
| 403 | `ACCOUNT_SUSPENDED` | 정지된 계정 |
| 403 | `ACCOUNT_WITHDRAWN` | 탈퇴한 계정 |

**비즈니스 로직**:
1. Firebase ID Token 검증
2. uid로 사용자 조회 → 미가입이면 `requires_signup: true` 반환
3. 계정 상태 확인 (SUSPENDED/WITHDRAWN 시 거부)
4. 미동의 필수 약관 확인 → 있으면 `requires_terms_agreement: true` + `pending_terms` 반환
5. `LAST_LOGIN_DT` 업데이트
6. Firebase 프로필 데이터 동기화 (이름, 사진 등)
7. 해당 디바이스의 기존 Refresh Token revoke
8. 새 Access/Refresh Token 발급

---

#### 4.2.3 POST /api/v1/auth/refresh (토큰 갱신)

**Request Body**:
```typescript
const refreshSchema = z.object({
  refresh_token: z.string().min(1),
  device_id: z.string().max(100).optional(),
});
```

**Response 200**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 1800
}
```

**비즈니스 로직**:
1. Refresh Token JWT 검증 (서명, 만료)
2. 토큰 해시로 `TB_COMM_RFRSH_TKN` 테이블 조회
3. `DSCD_DT` 확인 (이미 폐기된 토큰인지)
4. 사용자 상태 확인
5. 기존 Refresh Token revoke (Token Rotation)
6. 새 Access/Refresh Token 발급

---

#### 4.2.4 POST /api/v1/auth/logout (로그아웃)

**Request Header**: `Authorization: Bearer <access_token>`

**Request Body**:
```typescript
const logoutSchema = z.object({
  refresh_token: z.string().min(1),
});
```

**Response**: `204 No Content`

**비즈니스 로직**:
1. Access Token에서 사용자 ID 추출
2. Refresh Token 해시로 DB 조회
3. `DSCD_DT = NOW()` 설정

---

#### 4.2.5 POST /api/v1/auth/logout-all (전체 로그아웃)

**Request Header**: `Authorization: Bearer <access_token>`

**Response**: `204 No Content`

**비즈니스 로직**:
1. Access Token에서 사용자 ID 추출
2. 해당 사용자의 모든 활성 Refresh Token에 `DSCD_DT = NOW()` 설정

---

#### 4.2.6 GET /api/v1/users/me (내 프로필 조회)

**Response 200**:
```json
{
  "id": 1,
  "uid": "firebase-uid-xxx",
  "email": "user@example.com",
  "phone_no": "010-1234-5678",
  "display_nm": "홍길동",
  "photo_url": "https://...",
  "provider_cd": "GOOGLE",
  "role_cd": "USER",
  "status_cd": "ACTIVE",
  "email_verified_yn": true,
  "default_ws_id": 1,
  "last_login_at": "2026-02-14T10:00:00Z",
  "created_at": "2026-01-01T00:00:00Z",
  "default_workspace": {
    "id": 1,
    "slug": "honggildong-ws",
    "name": "홍길동의 워크스페이스",
    "type_cd": "PERSONAL",
    "role_cd": "OWNER"
  }
}
```

---

#### 4.2.7 PATCH /api/v1/users/me (내 프로필 수정)

**Request Body**:
```typescript
const updateProfileSchema = z.object({
  display_nm: z.string().max(100).optional(),
  phone_no: z.string().max(20).optional(),
  photo_url: z.string().url().max(2000).optional(),
});
```

**Response 200**: 수정된 사용자 정보

---

#### 4.2.8 DELETE /api/v1/users/me (회원 탈퇴)

**Response**: `204 No Content`

**에러 응답**:

| HTTP 상태 | 에러 코드 | 설명 |
|-----------|----------|------|
| 409 | `WORKSPACE_OWNER_TRANSFER_REQUIRED` | 소유한 팀 워크스페이스의 소유권 이전이 필요 |
| 409 | `ACTIVE_SUBSCRIPTION_EXISTS` | 활성 구독이 있는 워크스페이스 소유 중 |

**비즈니스 로직**:
1. **워크스페이스 소유권 사전 검증** (워크스페이스 모듈 호출):
   - 소유한 팀 워크스페이스(`TY_CD='TEAM'`, `OWNR_ID=사용자ID`) 확인
   - 팀 워크스페이스가 있고 다른 멤버가 존재하면 → 소유권 이전 요구 (409 에러)
   - 팀 워크스페이스에 활성 구독이 있으면 → 구독 해지 요구 (409 에러)
2. **[트랜잭션 시작]**
3. `STTS_CD = 'WITHDRAWN'`, `WHDWL_DT = NOW()`, `DEL_DT = NOW()` 설정
4. `BSC_WKSPC_ID = NULL` 설정
5. 모든 Refresh Token revoke
6. 개인정보 마스킹 (EML_ADDR → `withdrawn_xxx@deleted.local`)
7. **워크스페이스 정리** (워크스페이스 모듈 호출):
   - 개인 워크스페이스: `STTS_CD = 'DELETED'`, `DEL_DT = NOW()`
   - 멤버로만 참여 중인 워크스페이스: 멤버십 `STTS_CD = 'LEFT'`, `LEFT_DT = NOW()`
   - 소유한 팀 워크스페이스(멤버 없음): `STTS_CD = 'DELETED'`, `DEL_DT = NOW()`
8. **[트랜잭션 커밋]**

> **워크스페이스 연동**: 탈퇴 시 워크스페이스 처리 상세는 [워크스페이스 관리 시스템 설계 문서 UC-09](./workspace.md#uc-09-사용자-탈퇴-시-워크스페이스-처리)를 참조한다.

---

#### 4.2.9 GET /api/v1/terms/active (활성 약관 목록)

**Response 200**:
```json
[
  {
    "id": 1,
    "type_cd": "SERVICE",
    "version": "1.0",
    "title": "서비스 이용약관",
    "required_yn": true,
    "effective_dt": "2026-01-01"
  },
  {
    "id": 2,
    "type_cd": "PRIVACY",
    "version": "1.0",
    "title": "개인정보 처리방침",
    "required_yn": true,
    "effective_dt": "2026-01-01"
  },
  {
    "id": 3,
    "type_cd": "MARKETING",
    "version": "1.0",
    "title": "마케팅 정보 수신 동의",
    "required_yn": false,
    "effective_dt": "2026-01-01"
  }
]
```

---

#### 4.2.10 POST /api/v1/terms/agree (약관 동의)

**Request Body**:
```typescript
const agreeTermsSchema = z.object({
  terms_ids: z.array(z.number()).min(1),
  device_info: z.string().max(200).optional(),
});
```

**Response 201**:
```json
[
  {
    "id": 10,
    "terms_id": 5,
    "agreed_yn": true,
    "agreed_at": "2026-02-14T10:30:00Z"
  }
]
```

---

#### 4.2.11 POST /api/v1/terms (약관 생성 - ADMIN)

**Request Body**:
```typescript
const createTermsSchema = z.object({
  type_cd: z.enum(['SERVICE', 'PRIVACY', 'MARKETING', 'THIRD_PARTY']),
  version: z.string().max(10),
  title: z.string().max(200),
  content: z.string(),
  required_yn: z.boolean().default(true),
  effective_dt: z.string().date(),   // "YYYY-MM-DD"
});
```

**Response 201**: 생성된 약관 정보

---

#### 4.2.12 PATCH /api/v1/terms/[id] (약관 수정 - ADMIN)

**Request Body**:
```typescript
const updateTermsSchema = z.object({
  title: z.string().max(200).optional(),
  content: z.string().optional(),
  is_active: z.boolean().optional(),
});
```

**Response 200**: 수정된 약관 정보

---

#### 4.2.13 GET /api/v1/users (사용자 목록 - ADMIN)

**Query Parameters**:

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `page` | number | 1 | 페이지 번호 |
| `size` | number | 20 | 페이지 크기 |
| `status` | string | - | 상태 필터 (ACTIVE, SUSPENDED, WITHDRAWN) |
| `role` | string | - | 역할 필터 (USER, ADMIN, MANAGER) |
| `search` | string | - | 이메일/이름 검색 |

**Response 200**:
```json
{
  "items": [
    {
      "id": 1,
      "email": "user@example.com",
      "display_nm": "홍길동",
      "provider_cd": "GOOGLE",
      "role_cd": "USER",
      "status_cd": "ACTIVE",
      "last_login_at": "2026-02-14T10:00:00Z",
      "created_at": "2026-01-01T00:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "size": 20,
  "total_pages": 8
}
```

---

### 4.3 공통 에러 응답 형식

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "요청 데이터가 유효하지 않습니다.",
    "details": [
      {
        "field": "email",
        "message": "올바른 이메일 형식이 아닙니다."
      }
    ]
  }
}
```

### 4.4 JWT 토큰 구조

#### Access Token Payload
```json
{
  "sub": 42,
  "role": "USER",
  "default_ws_id": 1,
  "type": "access",
  "iat": 1738828800,
  "exp": 1738830600
}
```

#### Refresh Token Payload
```json
{
  "sub": 42,
  "type": "refresh",
  "device": "device-id-xxx",
  "iat": 1738828800,
  "exp": 1739433600
}
```

---

## 5. 화면 구성

### 5.1 화면 목록 총괄

| 구분 | 경로 | 접근 권한 | 설명 |
|------|------|----------|------|
| 로그인 | `/auth/login` | Public | 이메일/소셜 로그인 |
| 회원가입 | `/auth/signup` | Public | 회원가입 + 약관 동의 |
| 비밀번호 찾기 | `/auth/forgot-password` | Public | 비밀번호 재설정 메일 발송 |
| 약관 동의 | `/auth/terms-agreement` | Bearer | 미동의 약관 추가 동의 |
| 내 프로필 | `/admin/profile` | Bearer | 프로필 조회/수정 |
| 비밀번호 변경 | `/admin/profile/change-password` | Bearer | 비밀번호 변경 (이메일 가입자) |
| 약관 관리 | `/admin/settings/terms` | ADMIN | 약관 CRUD |
| 약관 생성/수정 | `/admin/settings/terms/[id]` | ADMIN | 약관 상세 에디터 |
| 사용자 관리 | `/admin/settings/users` | ADMIN | 사용자 목록/역할 관리 |
| 사용자 상세 | `/admin/settings/users/[id]` | ADMIN | 사용자 상세 정보 |

### 5.2 로그인 페이지 (`/auth/login`)

#### 화면 구성

```
┌──────────────────────────────────────┐
│           [앱 로고/아이콘]            │
│     Astravision Messaging Agent      │
│     AI 기반 스마트 메시징 플랫폼        │
│                                      │
│  ┌──────────────────────────────┐   │
│  │  ┌─ 이메일 ──────────────┐   │   │
│  │  │ example@email.com     │   │   │
│  │  └──────────────────────┘   │   │
│  │  ┌─ 비밀번호 ────────────┐   │   │
│  │  │ ••••••••              │   │   │
│  │  └──────────────────────┘   │   │
│  │                              │   │
│  │  ☐ 로그인 상태 유지  비밀번호 찾기 │
│  │                              │   │
│  │  ┌──────────────────────┐   │   │
│  │  │       로그인          │   │   │
│  │  └──────────────────────┘   │   │
│  │                              │   │
│  │  ──── 또는 ────             │   │
│  │                              │   │
│  │  [G] Google로 로그인         │   │
│  │  [] Apple로 로그인          │   │
│  │  [K] Kakao로 로그인          │   │
│  │                              │   │
│  │  계정이 없으신가요? 회원가입    │   │
│  └──────────────────────────────┘   │
│                                      │
│  이용약관 | 개인정보처리방침            │
└──────────────────────────────────────┘
```

#### 기능 상세

| 항목 | 설명 |
|------|------|
| 이메일 로그인 | 이메일 + 비밀번호 입력 → Firebase Auth `signInWithEmailAndPassword` → ID Token 획득 → `/api/v1/auth/login` 호출 |
| 소셜 로그인 | Firebase Social Provider 팝업 → ID Token 획득 → `/api/v1/auth/login` 호출 |
| 로그인 상태 유지 | 체크 시 Refresh Token 만료일 연장 (30일) |
| 로그인 후 리다이렉트 | 미들웨어에서 저장한 `redirect` 쿼리 파라미터로 원래 경로 복귀 |
| 미가입 사용자 | `requires_signup: true` 응답 시 → 회원가입 페이지로 이동 (Firebase Token 유지) |
| 미동의 약관 | `requires_terms_agreement: true` 응답 시 → 약관 동의 페이지로 이동 |
| 에러 표시 | 인증 실패 시 화면 상단에 에러 배너 표시 |

#### 상태 관리

```typescript
interface LoginState {
  email: string;
  password: string;
  rememberMe: boolean;
  isLoading: boolean;
  errors: { email?: string; password?: string; general?: string };
}
```

---

### 5.3 회원가입 페이지 (`/auth/signup`)

#### 화면 구성

```
┌──────────────────────────────────────┐
│           [앱 로고/아이콘]            │
│             회원가입                   │
│     AI 기반 스마트 메시징 플랫폼 시작하기 │
│                                      │
│  ┌──────────────────────────────┐   │
│  │  ┌─ 이름 ───────────────┐   │   │
│  │  │ 홍길동                │   │   │
│  │  └──────────────────────┘   │   │
│  │  ┌─ 이메일 ──────────────┐   │   │
│  │  │ example@email.com     │   │   │
│  │  └──────────────────────┘   │   │
│  │  ┌─ 비밀번호 ────────────┐   │   │
│  │  │ ••••••••              │   │   │
│  │  └──────────────────────┘   │   │
│  │   • 최소 8자 이상 ✓          │   │
│  │   • 대문자, 소문자, 숫자 포함  │   │
│  │  ┌─ 비밀번호 확인 ────────┐   │   │
│  │  │ ••••••••              │   │   │
│  │  └──────────────────────┘   │   │
│  │                              │   │
│  │  ── 약관 동의 ──             │   │
│  │  ☐ 전체 동의                 │   │
│  │  ─────────────────          │   │
│  │  ☑ [필수] 이용약관 동의  [보기] │   │
│  │  ☑ [필수] 개인정보처리방침  [보기]│   │
│  │  ☐ [선택] 마케팅 수신 동의 [보기] │   │
│  │                              │   │
│  │  ┌──────────────────────┐   │   │
│  │  │       회원가입         │   │   │
│  │  └──────────────────────┘   │   │
│  │                              │   │
│  │  ──── 또는 ────             │   │
│  │                              │   │
│  │  [G] Google로 가입           │   │
│  │  [] Apple로 가입            │   │
│  │  [K] Kakao로 가입            │   │
│  │                              │   │
│  │  이미 계정이 있으신가요? 로그인  │   │
│  └──────────────────────────────┘   │
└──────────────────────────────────────┘
```

#### 기능 상세

| 항목 | 설명 |
|------|------|
| 이메일 회원가입 | Firebase `createUserWithEmailAndPassword` → ID Token → `/api/v1/auth/signup` |
| 소셜 회원가입 | Firebase Social Login → ID Token → `/api/v1/auth/signup` |
| 약관 동적 로딩 | `/api/v1/terms/active` 호출하여 약관 목록 동적 표시 |
| 전체 동의 체크 | 모든 약관 일괄 동의/해제 토글 |
| 약관 내용 보기 | [보기] 클릭 시 모달로 약관 전문 표시 (`/api/v1/terms/:id`) |
| 비밀번호 강도 표시 | 실시간 유효성 검증 결과를 시각적으로 표시 |
| 폼 유효성 검증 | 클라이언트 측 + 서버 측 이중 검증 |

#### 소셜 회원가입 흐름

소셜 로그인으로 진입한 경우 (로그인에서 `requires_signup: true` 응답 시):
1. Firebase 프로필 정보 (이름, 이메일, 사진)를 자동 채움
2. 이메일/비밀번호 입력 필드 비활성화 (소셜 인증 완료 상태)
3. 약관 동의만 받고 가입 완료

---

### 5.4 비밀번호 찾기 페이지 (`/auth/forgot-password`)

#### 화면 구성

기존 UI 유지. 기능 연동 추가:

| 항목 | 설명 |
|------|------|
| 이메일 입력 | Firebase `sendPasswordResetEmail` 호출 |
| 성공 메시지 | "이메일을 전송했습니다" + 이메일 확인 안내 |
| 링크 유효기간 | Firebase 기본 설정 (1시간) |

---

### 5.5 약관 동의 페이지 (`/auth/terms-agreement`)

로그인 후 미동의 필수 약관이 있을 때 리다이렉트되는 페이지.

#### 화면 구성

```
┌──────────────────────────────────────┐
│           [앱 로고/아이콘]            │
│         약관 동의가 필요합니다          │
│   서비스를 계속 이용하려면 아래 약관에    │
│         동의해주세요.                  │
│                                      │
│  ┌──────────────────────────────┐   │
│  │  ☐ 전체 동의                 │   │
│  │  ─────────────────          │   │
│  │  ☐ [필수] 개인정보처리방침 v2.0│   │
│  │    2026.03.01 시행            │   │
│  │    [약관 전문 보기]            │   │
│  │  ☐ [선택] 마케팅 수신 동의 v1.0│   │
│  │    [약관 전문 보기]            │   │
│  │                              │   │
│  │  ┌──────────────────────┐   │   │
│  │  │      동의하고 계속      │   │   │
│  │  └──────────────────────┘   │   │
│  └──────────────────────────────┘   │
└──────────────────────────────────────┘
```

#### 기능 상세

| 항목 | 설명 |
|------|------|
| 약관 로딩 | 로그인 응답의 `pending_terms` 데이터 사용 |
| 필수 약관 | 모든 필수 약관 동의 시에만 "동의하고 계속" 버튼 활성화 |
| 동의 처리 | `/api/v1/terms/agree` 호출 → 성공 시 원래 경로로 이동 |

---

### 5.6 내 프로필 페이지 (`/admin/profile`)

#### 화면 구성

```
┌──────────────────────────────────────────────────┐
│  [AdminLayout]                                    │
│  ┌────────────────────────────────────────────┐  │
│  │  내 프로필                                  │  │
│  │                                            │  │
│  │  ┌───┐  홍길동                              │  │
│  │  │   │  user@example.com                   │  │
│  │  │ 사진│  Google 계정으로 로그인               │  │
│  │  │   │  가입일: 2026.01.01                  │  │
│  │  └───┘                                     │  │
│  │                                            │  │
│  │  ── 기본 정보 ──                            │  │
│  │  이름:     [홍길동            ]              │  │
│  │  전화번호: [010-1234-5678     ]              │  │
│  │  이메일:   user@example.com (수정 불가)       │  │
│  │                                            │  │
│  │  [프로필 수정]  [비밀번호 변경]                │  │
│  │                                            │  │
│  │  ── 약관 동의 현황 ──                        │  │
│  │  ☑ 서비스 이용약관 v1.0 (2026.01.01 동의)    │  │
│  │  ☑ 개인정보 처리방침 v1.0 (2026.01.01 동의)   │  │
│  │  ☑ 마케팅 수신 동의 v1.0 (2026.01.15 동의)   │  │
│  │    [마케팅 수신 동의 철회]                     │  │
│  │                                            │  │
│  │  ── 로그인 기기 관리 ──                      │  │
│  │  Chrome / macOS (현재 기기)                  │  │
│  │  Safari / iOS (2026.02.10 접속)  [로그아웃]   │  │
│  │                                            │  │
│  │  ────────────────────────                  │  │
│  │  [전체 기기 로그아웃]  [회원 탈퇴]             │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

#### 기능 상세

| 항목 | API | 설명 |
|------|-----|------|
| 프로필 조회 | `GET /users/me` | 사용자 정보 + 약관 동의 현황 |
| 프로필 수정 | `PATCH /users/me` | 이름, 전화번호, 프로필 사진 |
| 비밀번호 변경 | Firebase `updatePassword` | 이메일 가입자만 표시 |
| 약관 동의 철회 | `DELETE /terms/:id/revoke` | 선택 약관만 철회 가능 |
| 기기 로그아웃 | `POST /auth/logout` | 특정 디바이스 세션 종료 |
| 전체 로그아웃 | `POST /auth/logout-all` | 모든 디바이스 세션 종료 |
| 회원 탈퇴 | `DELETE /users/me` | 확인 모달 후 Soft Delete |

---

### 5.7 약관 관리 페이지 (`/admin/settings/terms`) - ADMIN 전용

#### 화면 구성

```
┌──────────────────────────────────────────────────┐
│  [AdminLayout]                                    │
│  ┌────────────────────────────────────────────┐  │
│  │  약관 관리                    [+ 약관 등록]   │  │
│  │                                            │  │
│  │  ┌─ 필터 ──────────────────────────────┐  │  │
│  │  │ 유형: [전체 ▼]  상태: [전체 ▼]       │  │  │
│  │  └─────────────────────────────────────┘  │  │
│  │                                            │  │
│  │  ┌────┬──────┬──────┬────┬────┬────┬──┐  │  │
│  │  │ ID │ 유형  │ 버전  │제목 │필수 │상태│  │  │  │
│  │  ├────┼──────┼──────┼────┼────┼────┼──┤  │  │
│  │  │  1 │서비스 │ 1.0  │서비스│ Y  │활성│수정│  │  │
│  │  │  2 │개인정보│ 1.0  │개인정│ Y  │활성│수정│  │  │
│  │  │  3 │마케팅 │ 1.0  │마케팅│ N  │활성│수정│  │  │
│  │  │  4 │서비스 │ 2.0  │서비스│ Y  │비활성│수정│ │  │
│  │  └────┴──────┴──────┴────┴────┴────┴──┘  │  │
│  │                                            │  │
│  │  < 1 2 3 >                                 │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

#### 약관 등록/수정 화면 (`/admin/settings/terms/[id]`)

```
┌──────────────────────────────────────────────────┐
│  [AdminLayout]                                    │
│  ┌────────────────────────────────────────────┐  │
│  │  ← 약관 관리  /  약관 등록                    │  │
│  │                                            │  │
│  │  약관 유형:   [서비스 이용약관 ▼]              │  │
│  │  버전:       [2.0                ]          │  │
│  │  제목:       [서비스 이용약관 v2.0  ]          │  │
│  │  시행일:     [2026-03-01          ]          │  │
│  │  필수 여부:  ● 필수  ○ 선택                   │  │
│  │  활성 상태:  [ON ●───]                       │  │
│  │                                            │  │
│  │  약관 내용:                                  │  │
│  │  ┌──────────────────────────────────────┐  │  │
│  │  │ [B] [I] [H1] [H2] [UL] [OL] [Link]  │  │  │
│  │  ├──────────────────────────────────────┤  │  │
│  │  │                                      │  │  │
│  │  │  (리치 텍스트 에디터)                   │  │  │
│  │  │                                      │  │  │
│  │  └──────────────────────────────────────┘  │  │
│  │                                            │  │
│  │              [취소]  [저장]                  │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

#### 기능 상세

| 항목 | API | 설명 |
|------|-----|------|
| 약관 목록 | `GET /terms` | DataTable + 필터 + 페이징 |
| 약관 생성 | `POST /terms` | 유형 + 버전 조합 중복 검사 |
| 약관 수정 | `PATCH /terms/:id` | 제목, 내용, 활성 상태 수정 |
| 리치 텍스트 | `react-quill-new` | 기존 RichTextEditor 컴포넌트 활용 |
| 버전 관리 | 동일 유형의 이전 버전 자동 비활성화 로직 | 새 버전 활성화 시 이전 버전 `ACTV_YN = 'N'` |

---

### 5.8 사용자 관리 페이지 (`/admin/settings/users`) - ADMIN 전용

#### 화면 구성

```
┌──────────────────────────────────────────────────┐
│  [AdminLayout]                                    │
│  ┌────────────────────────────────────────────┐  │
│  │  사용자 관리                                 │  │
│  │                                            │  │
│  │  ┌─ 검색/필터 ─────────────────────────┐   │  │
│  │  │ 검색: [이메일/이름 검색...     ]       │   │  │
│  │  │ 역할: [전체 ▼]  상태: [전체 ▼]       │   │  │
│  │  └─────────────────────────────────────┘   │  │
│  │                                            │  │
│  │  ┌────┬──────┬──────┬────┬────┬────────┐  │  │
│  │  │ ID │ 이메일 │ 이름  │역할 │상태│ 최근 로그인│  │
│  │  ├────┼──────┼──────┼────┼────┼────────┤  │  │
│  │  │  1 │admin@│관리자 │ADMIN│활성│02.14 10:00│ │
│  │  │  2 │user@ │홍길동 │USER │활성│02.13 15:00│ │
│  │  │  3 │test@ │김철수 │USER │정지│02.10 09:00│ │
│  │  └────┴──────┴──────┴────┴────┴────────┘  │  │
│  │                                            │  │
│  │  총 150명  < 1 2 3 ... 8 >                  │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

#### 사용자 상세 화면

| 항목 | API | 설명 |
|------|-----|------|
| 사용자 상세 | `GET /users/:id` | 기본 정보 + 약관 동의 현황 + 로그인 이력 |
| 역할 변경 | `PATCH /users/:id/role` | Dropdown으로 역할 선택 → 확인 모달 |
| 계정 정지 | `POST /users/:id/suspend` | 사유 입력 → 확인 모달 |
| 계정 활성화 | `POST /users/:id/activate` | 확인 모달 |

---

## 6. 인증 흐름

### 6.1 전체 인증 시퀀스

```
[사용자] ──────────────────────────────────────────────────────
  │
  │  1. 소셜 로그인 버튼 클릭
  ▼
[Firebase Auth] ──────────────────────────────────────────────
  │
  │  2. OAuth 팝업 → 인증 완료 → ID Token 반환
  ▼
[Next.js Client] ────────────────────────────────────────────
  │
  │  3. POST /api/v1/auth/login { id_token }
  ▼
[Next.js API Route] ─────────────────────────────────────────
  │
  │  4. Firebase Admin SDK로 ID Token 검증
  │  5. DB에서 사용자 조회
  │  6. JWT Access/Refresh Token 생성
  │  7. Refresh Token 해시 DB 저장
  │
  │  응답: { access_token, refresh_token, user }
  ▼
[Next.js Server Action] ─────────────────────────────────────
  │
  │  8. HttpOnly 쿠키에 토큰 저장
  │     - app_access_token (HttpOnly, Secure, SameSite=Lax)
  │     - app_refresh_token (HttpOnly, Secure, SameSite=Lax)
  ▼
[Next.js Middleware] ─────────────────────────────────────────
  │
  │  9. 이후 요청마다:
  │     - 쿠키에서 access_token 확인
  │     - 보호된 경로 접근 시 토큰 유효성 검증
  │     - 만료 시 자동 갱신 (refresh)
  ▼
[보호된 페이지 접근 허용]
```

### 6.2 토큰 자동 갱신 흐름

```
[Client] → [API Route] 요청
  │
  ├─ Access Token 유효 → 정상 응답
  │
  └─ Access Token 만료 (401)
       │
       └─ [Client] apiClient 인터셉터
            │
            ├─ POST /api/v1/auth/refresh { refresh_token }
            │   │
            │   ├─ 성공 → 새 토큰으로 원래 요청 재시도
            │   │
            │   └─ 실패 (Refresh Token도 만료/폐기)
            │       │
            │       └─ 로그인 페이지로 리다이렉트
            │          쿠키 삭제
```

### 6.3 미들웨어 인증 로직 (강화)

```typescript
// proxy.ts 인증 검증 강화
export async function proxy(request: NextRequest) {
  // ... 기존 locale 처리 ...

  const accessToken = request.cookies.get(ACCESS_TOKEN_KEY)?.value;
  const refreshToken = request.cookies.get(REFRESH_TOKEN_KEY)?.value;

  // 토큰 유효성 검증 (서명 + 만료 확인)
  let isAuthenticated = false;
  if (accessToken) {
    try {
      await verifyJWT(accessToken, 'access');
      isAuthenticated = true;
    } catch {
      // Access Token 만료 → Refresh 시도
      if (refreshToken) {
        const refreshResult = await refreshAccessToken(refreshToken);
        if (refreshResult) {
          isAuthenticated = true;
          // 새 토큰으로 쿠키 갱신
          response.cookies.set(ACCESS_TOKEN_KEY, refreshResult.access_token, cookieOptions);
          response.cookies.set(REFRESH_TOKEN_KEY, refreshResult.refresh_token, cookieOptions);
        }
      }
    }
  }

  // ... 기존 보호 경로 / 인증 경로 리다이렉트 로직 ...
}
```

---

## 7. 보안 설계

### 7.1 토큰 보안

| 항목 | 설계 |
|------|------|
| Access Token 저장 | HttpOnly Cookie (`app_access_token`) |
| Refresh Token 저장 | HttpOnly Cookie (`app_refresh_token`) |
| Cookie 속성 | `HttpOnly`, `Secure` (HTTPS), `SameSite=Lax`, `Path=/` |
| Token Rotation | Refresh 시 기존 토큰 폐기 + 새 토큰 발급 |
| Refresh Token DB 저장 | SHA-256 해시 저장 (원본 노출 방지) |
| 만료 시간 | Access: 30분, Refresh: 7일 (Remember Me: 30일) |

### 7.2 CSRF 방지

| 항목 | 설계 |
|------|------|
| SameSite Cookie | `SameSite=Lax` 설정으로 Cross-site POST 방지 |
| Origin 검증 | API Route에서 `Origin`/`Referer` 헤더 검증 |
| State 변경 API | 모든 변경 API는 POST/PATCH/DELETE (GET 제외) |

### 7.3 XSS 방지

| 항목 | 설계 |
|------|------|
| HttpOnly Cookie | JavaScript에서 토큰 접근 불가 |
| React 기본 보호 | JSX 자동 이스케이프 |
| Content Security Policy | next.config.mjs에 CSP 헤더 설정 |
| 입력 검증 | Zod 스키마로 서버 측 입력 검증 |

### 7.4 비밀번호 정책

| 항목 | 규칙 |
|------|------|
| 최소 길이 | 8자 이상 |
| 복잡도 | 대문자 + 소문자 + 숫자 필수 |
| 해싱 | bcrypt (salt rounds: 12) |
| Firebase 위임 | 비밀번호 관리는 Firebase Auth에 위임 |

### 7.5 Rate Limiting

| 엔드포인트 | 제한 | 창 |
|-----------|------|-----|
| `/auth/login` | 5회 | 15분 |
| `/auth/signup` | 3회 | 1시간 |
| `/auth/refresh` | 10회 | 1분 |
| `/auth/forgot-password` | 3회 | 1시간 |

### 7.6 계정 보안

| 항목 | 설계 |
|------|------|
| 계정 잠금 | 로그인 5회 실패 시 15분 잠금 (Firebase 제공) |
| Soft Delete | 회원 탈퇴 시 데이터 보존 (30일 후 영구 삭제) |
| 개인정보 마스킹 | 탈퇴 시 이메일, 이름, 전화번호 마스킹 처리 |
| 세션 관리 | 디바이스별 세션 관리, 의심 활동 시 전체 로그아웃 |

---

## 8. 디렉토리 구조

### 8.1 신규 추가 파일 구조

```
app/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth/
│   │       │   ├── signup/route.ts          # POST /api/v1/auth/signup
│   │       │   ├── login/route.ts           # POST /api/v1/auth/login
│   │       │   ├── refresh/route.ts         # POST /api/v1/auth/refresh
│   │       │   ├── logout/route.ts          # POST /api/v1/auth/logout
│   │       │   └── logout-all/route.ts      # POST /api/v1/auth/logout-all
│   │       ├── users/
│   │       │   ├── me/
│   │       │   │   └── route.ts             # GET, PATCH, DELETE /api/v1/users/me
│   │       │   ├── [id]/
│   │       │   │   ├── route.ts             # GET /api/v1/users/:id
│   │       │   │   ├── role/route.ts        # PATCH /api/v1/users/:id/role
│   │       │   │   ├── suspend/route.ts     # POST /api/v1/users/:id/suspend
│   │       │   │   └── activate/route.ts    # POST /api/v1/users/:id/activate
│   │       │   └── route.ts                 # GET /api/v1/users
│   │       └── terms/
│   │           ├── active/route.ts          # GET /api/v1/terms/active
│   │           ├── pending/route.ts         # GET /api/v1/terms/pending
│   │           ├── agree/route.ts           # POST /api/v1/terms/agree
│   │           ├── my/
│   │           │   └── agreements/route.ts  # GET /api/v1/terms/my/agreements
│   │           ├── [id]/
│   │           │   ├── route.ts             # GET, PATCH /api/v1/terms/:id
│   │           │   └── revoke/route.ts      # DELETE /api/v1/terms/:id/revoke
│   │           └── route.ts                 # GET, POST /api/v1/terms
│   ├── [locale]/
│   │   ├── auth/
│   │   │   ├── login/page.tsx               # (기존 - 수정)
│   │   │   ├── signup/page.tsx              # (기존 - 수정)
│   │   │   ├── forgot-password/page.tsx     # (기존 - 수정)
│   │   │   └── terms-agreement/page.tsx     # (신규) 미동의 약관 동의
│   │   └── admin/
│   │       ├── profile/
│   │       │   ├── page.tsx                 # (신규) 내 프로필
│   │       │   └── change-password/page.tsx # (신규) 비밀번호 변경
│   │       └── settings/
│   │           ├── terms/
│   │           │   ├── page.tsx             # (신규) 약관 관리
│   │           │   └── [id]/page.tsx        # (신규) 약관 생성/수정
│   │           └── users/
│   │               ├── page.tsx             # (신규) 사용자 관리
│   │               └── [id]/page.tsx        # (신규) 사용자 상세
│   └── actions/
│       └── auth.ts                          # Server Actions (쿠키 관리)
├── lib/
│   ├── db/
│   │   ├── index.ts                         # Drizzle 클라이언트 인스턴스
│   │   ├── schema/
│   │   │   ├── auth.ts                      # TB_COMM_USER, TB_COMM_TRMS, TH_COMM_USER_AGRE, TB_COMM_RFRSH_TKN 스키마
│   │   │   ├── workspace.ts                 # workspaces, members, invitations 스키마 (워크스페이스 모듈)
│   │   │   └── index.ts                     # 스키마 re-export
│   │   └── migrate.ts                       # 마이그레이션 실행기
│   ├── auth/
│   │   ├── jwt.ts                           # JWT 생성/검증 유틸 (jose)
│   │   ├── firebase-admin.ts                # Firebase Admin SDK 초기화
│   │   ├── firebase-client.ts               # Firebase Client SDK 초기화
│   │   ├── middleware-auth.ts               # API Route용 인증 미들웨어
│   │   └── password.ts                      # bcrypt 해싱 유틸
│   ├── api/
│   │   ├── client.ts                        # (기존 - 수정: 인터셉터 추가)
│   │   └── menu.ts                          # (기존)
│   └── validations/
│       ├── auth.ts                          # Zod 인증 스키마
│       ├── user.ts                          # Zod 사용자 스키마
│       └── terms.ts                         # Zod 약관 스키마
├── contexts/
│   ├── SidebarContext.tsx                    # (기존)
│   └── AuthContext.tsx                       # (신규) 인증 상태 관리
├── hooks/
│   ├── useAuth.ts                           # 인증 커스텀 훅
│   └── useFirebaseAuth.ts                   # Firebase 인증 훅
├── middleware.ts                             # (기존 - 수정: JWT 검증 강화)
├── proxy.ts                                 # (기존 - 수정: 토큰 자동 갱신)
├── drizzle.config.ts                        # Drizzle Kit 설정
└── .env.local                               # 환경 변수
```

### 8.2 AuthContext 설계

```typescript
// contexts/AuthContext.tsx
interface AuthUser {
  id: number;
  uid: string;
  email: string | null;
  displayNm: string | null;
  photoUrl: string | null;
  providerCd: string;
  roleCd: string;
  statusCd: string;
  defaultWsId: number | null;
}

interface WorkspaceInfo {
  id: number;
  slug: string;
  name: string;
  typeCd: 'PERSONAL' | 'TEAM';
  roleCd: 'OWNER' | 'ADMIN' | 'MEMBER' | 'GUEST';
}

interface AuthContextType {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  currentWorkspace: WorkspaceInfo | null;       // 현재 활성 워크스페이스
  workspaces: WorkspaceInfo[];                   // 소속 워크스페이스 목록
  login: (idToken: string, deviceId?: string) => Promise<LoginResult>;
  signup: (idToken: string, displayNm: string, agreedTermsIds: number[]) => Promise<void>;
  logout: () => Promise<void>;
  logoutAll: () => Promise<void>;
  refreshUser: () => Promise<void>;
  switchWorkspace: (workspaceId: number) => void; // 워크스페이스 전환
}
```

### 8.3 API 클라이언트 인터셉터

```typescript
// lib/api/client.ts (수정)
async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    credentials: 'include',  // 쿠키 자동 포함
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  // 401 → 토큰 갱신 시도
  if (response.status === 401) {
    const refreshResult = await refreshTokens();
    if (refreshResult) {
      // 갱신 성공 → 원래 요청 재시도
      return apiRequest<T>(endpoint, options);
    }
    // 갱신 실패 → 로그인 페이지로 이동
    window.location.href = '/auth/login';
    throw new Error('Authentication required');
  }

  // ... 기존 응답 처리 ...
}
```

---

## 9. 구현 순서

### Phase 1: 기반 인프라 (1주차)

| 순서 | 작업 | 파일 |
|------|------|------|
| 1-1 | 의존성 설치 | `package.json` |
| 1-2 | 환경 변수 설정 | `.env.local`, `.env.example` |
| 1-3 | Drizzle ORM 설정 | `lib/db/index.ts`, `drizzle.config.ts` |
| 1-4 | DB 스키마 정의 | `lib/db/schema/auth.ts` |
| 1-5 | DB 마이그레이션 | `lib/db/migrate.ts` |
| 1-6 | Firebase Admin 초기화 | `lib/auth/firebase-admin.ts` |
| 1-7 | Firebase Client 초기화 | `lib/auth/firebase-client.ts` |
| 1-8 | JWT 유틸리티 | `lib/auth/jwt.ts` |
| 1-9 | Zod 검증 스키마 | `lib/validations/*.ts` |

### Phase 2: 인증 API (2주차)

| 순서 | 작업 | 파일 |
|------|------|------|
| 2-1 | 인증 미들웨어 | `lib/auth/middleware-auth.ts` |
| 2-2 | 회원가입 API | `app/api/v1/auth/signup/route.ts` |
| 2-3 | 로그인 API | `app/api/v1/auth/login/route.ts` |
| 2-4 | 토큰 갱신 API | `app/api/v1/auth/refresh/route.ts` |
| 2-5 | 로그아웃 API | `app/api/v1/auth/logout/route.ts` |
| 2-6 | 전체 로그아웃 API | `app/api/v1/auth/logout-all/route.ts` |
| 2-7 | Server Action (쿠키) | `app/actions/auth.ts` |
| 2-8 | AuthContext | `contexts/AuthContext.tsx` |
| 2-9 | API 클라이언트 수정 | `lib/api/client.ts` |
| 2-10 | 미들웨어 강화 | `middleware.ts`, `proxy.ts` |

### Phase 3: 사용자/약관 API (3주차)

| 순서 | 작업 | 파일 |
|------|------|------|
| 3-1 | 내 프로필 API | `app/api/v1/users/me/route.ts` |
| 3-2 | 사용자 관리 API | `app/api/v1/users/route.ts`, `[id]/...` |
| 3-3 | 활성 약관 목록 API | `app/api/v1/terms/active/route.ts` |
| 3-4 | 약관 상세 API | `app/api/v1/terms/[id]/route.ts` |
| 3-5 | 약관 동의 API | `app/api/v1/terms/agree/route.ts` |
| 3-6 | 약관 철회 API | `app/api/v1/terms/[id]/revoke/route.ts` |
| 3-7 | 미동의 약관 API | `app/api/v1/terms/pending/route.ts` |
| 3-8 | 약관 관리 API (ADMIN) | `app/api/v1/terms/route.ts` |

### Phase 4: 화면 구현 (4주차)

| 순서 | 작업 | 파일 |
|------|------|------|
| 4-1 | 로그인 페이지 수정 | `app/[locale]/auth/login/page.tsx` |
| 4-2 | 회원가입 페이지 수정 | `app/[locale]/auth/signup/page.tsx` |
| 4-3 | 비밀번호 찾기 수정 | `app/[locale]/auth/forgot-password/page.tsx` |
| 4-4 | 약관 동의 페이지 | `app/[locale]/auth/terms-agreement/page.tsx` |
| 4-5 | 내 프로필 페이지 | `app/[locale]/admin/profile/page.tsx` |
| 4-6 | 비밀번호 변경 페이지 | `app/[locale]/admin/profile/change-password/page.tsx` |
| 4-7 | 약관 관리 페이지 | `app/[locale]/admin/settings/terms/page.tsx` |
| 4-8 | 약관 에디터 페이지 | `app/[locale]/admin/settings/terms/[id]/page.tsx` |
| 4-9 | 사용자 관리 페이지 | `app/[locale]/admin/settings/users/page.tsx` |
| 4-10 | 사용자 상세 페이지 | `app/[locale]/admin/settings/users/[id]/page.tsx` |

### Phase 5: 통합/보안 (5주차)

| 순서 | 작업 |
|------|------|
| 5-1 | 다국어 메시지 추가 (`messages/ko.json`, `messages/en.json`) |
| 5-2 | Rate Limiting 구현 |
| 5-3 | CSP 헤더 설정 |
| 5-4 | 에러 처리 통합 |
| 5-5 | E2E 테스트 |
| 5-6 | 배포 환경 설정 (Docker, K8s) |

---

## 부록: 초기 데이터 (Seed)

```sql
-- 기본 약관 데이터
INSERT INTO app.TB_COMM_TRMS (TY_CD, VER_NO, TTL, CN, REQD_YN, ENFC_DT, ACTV_YN) VALUES
('SERVICE', '1.0', '서비스 이용약관', '(서비스 이용약관 전문)', 'Y', '2026-01-01', 'Y'),
('PRIVACY', '1.0', '개인정보 처리방침', '(개인정보 처리방침 전문)', 'Y', '2026-01-01', 'Y'),
('MARKETING', '1.0', '마케팅 정보 수신 동의', '(마케팅 수신 동의 전문)', 'N', '2026-01-01', 'Y');

-- 관리자 계정 (Firebase 가입 후 수동 설정)
-- UPDATE app.TB_COMM_USER SET ROLE_CD = 'ADMIN' WHERE EML_ADDR = 'admin@astravision.co.kr';

-- 기존 사용자 개인 워크스페이스 마이그레이션
-- 상세한 마이그레이션 SQL은 워크스페이스 설계 문서의 부록을 참조한다.
-- (./workspace.md 부록: 기존 사용자 마이그레이션)
```
