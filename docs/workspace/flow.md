# 워크스페이스 생성 ~ 구독 결제 플로우

> **프로젝트**: 공통 워크스페이스 관리 모듈 (Workspace Management Module)
> **작성일**: 2026-02-14
> **참조 문서**: auth-system-design.md, workspace-system-design.md, subscription-payment-system-design.md

---

## 목차

1. [전체 플로우 개요](#1-전체-플로우-개요)
2. [STEP 1: 로그인 후 개인 워크스페이스 진입](#2-step-1-로그인-후-개인-워크스페이스-진입)
3. [STEP 2: 팀 워크스페이스 생성](#3-step-2-팀-워크스페이스-생성)
4. [STEP 3: 멤버 초대](#4-step-3-멤버-초대)
5. [STEP 4: 결제 수단 등록](#5-step-4-결제-수단-등록)
6. [STEP 5: 구독 플랜 선택 및 결제](#6-step-5-구독-플랜-선택-및-결제)
7. [STEP 6: 구독 이후 운영](#7-step-6-구독-이후-운영)
8. [화면 경로 요약](#8-화면-경로-요약)
9. [API 호출 순서 요약](#9-api-호출-순서-요약)
10. [상태 코드 정리](#10-상태-코드-정리)

---

## 1. 전체 플로우 개요

```
로그인 ──▶ 개인 WS 진입 ──▶ 팀 WS 생성 ──▶ 멤버 초대 ──▶ 결제수단 등록 ──▶ 구독 결제
  │                           │              │             │               │
  │ Firebase Auth             │ POST         │ EMAIL/LINK  │ 토스 SDK      │ 플랜 선택
  │ + JWT 발급                │ /workspaces   │ 초대 발송    │ 빌링키 발급    │ + 결제 실행
  ▼                           ▼              ▼             ▼               ▼
개인 WS 자동생성          OWNER로 등록    초대 수락 시     카드 정보 저장    TRIALING 또는
(회원가입 시)            + 멤버 관리 시작  멤버 추가       (AES-256 암호화)  ACTIVE 시작
```

### 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **워크스페이스 = 과금 주체** | 구독/결제/청구의 단위는 워크스페이스이며, 개별 사용자가 아님 |
| **워크스페이스당 1개 구독** | 하나의 워크스페이스는 하나의 활성 구독만 가질 수 있음 |
| **OWNER/ADMIN만 결제 관리** | 결제 수단 등록, 구독 생성/변경/해지는 OWNER 또는 ADMIN만 가능 |
| **멀티 워크스페이스** | 한 사용자가 여러 워크스페이스에 동시 소속 가능 |

---

## 2. STEP 1: 로그인 후 개인 워크스페이스 진입

### 2.1 신규 사용자 (회원가입)

회원가입 시 **개인 워크스페이스가 자동 생성**되어 즉시 서비스를 이용할 수 있다.

```
[사용자] ──── Firebase 인증 (이메일/Google/Apple/Kakao) ────▶ ID Token 획득
    │
    ▼
[POST /api/v1/auth/signup]
    │  Request: { id_token, display_nm, agreed_terms_ids }
    │
    │  1. Firebase ID Token 검증
    │  2. 기존 사용자 중복 검사 (uid)
    │  3. 필수 약관 동의 여부 검증 (SERVICE, PRIVACY)
    │
    │  ── 트랜잭션 시작 ──
    │  4. TB_COMM_USER 생성
    │  5. TH_COMM_USER_AGRE 생성 (약관 동의 이력)
    │  6. TB_COMM_WKSPC 생성 (TYPE_CD='PERSONAL', OWNR_ID=사용자ID)
    │  7. TR_COMM_WKSPC_MBR 생성 (ROLE_CD='OWNER')
    │  8. TB_COMM_USER.BSC_WKSPC_ID 업데이트
    │  ── 트랜잭션 커밋 ──
    │
    │  9. Access Token (30분) + Refresh Token (7일) 발급
    │  10. HttpOnly 쿠키에 토큰 저장
    ▼
[응답 201]
    {
      access_token, refresh_token,
      user: { id, email, role_cd: "USER", default_ws_id },
      default_workspace: { id, slug, name, type_cd: "PERSONAL", role_cd: "OWNER" }
    }
```

**개인 워크스페이스 특징**:
- 삭제 불가, 소유권 이전 불가
- 멤버 추가 불가 (`MAX_MBR_CNT = 1`)
- 슬러그: `{displayNm}-personal` (중복 시 자동 넘버링)

### 2.2 기존 사용자 (로그인)

```
[사용자] ──── Firebase 인증 ────▶ ID Token 획득
    │
    ▼
[POST /api/v1/auth/login]
    │  Request: { id_token, device_id }
    │
    │  1. Firebase ID Token 검증
    │  2. uid로 사용자 조회 → 미가입이면 requires_signup: true 반환
    │  3. 계정 상태 확인 (SUSPENDED/WITHDRAWN 시 거부)
    │  4. 미동의 약관 확인 → 있으면 requires_terms_agreement: true
    │  5. LAST_LOGIN_DT 업데이트
    │  6. Access/Refresh Token 발급
    ▼
[응답 200]
    {
      access_token, refresh_token,
      user: { ... },
      default_workspace: { id, slug, name, type_cd, role_cd },
      workspaces: [ ... ],  // 소속된 전체 워크스페이스 목록
      requires_terms_agreement: true/false,
      pending_terms: [ ... ]
    }
```

**로그인 후 분기**:

| 상황 | 리다이렉트 |
|------|-----------|
| 정상 로그인 | `BSC_WKSPC_ID` 워크스페이스 대시보드 |
| 미동의 약관 있음 | `/auth/terms-agreement` |
| 미가입 사용자 | `/auth/signup` |

---

## 3. STEP 2: 팀 워크스페이스 생성

로그인 후, 사용자는 팀 협업을 위한 **팀 워크스페이스를 생성**할 수 있다.

### 3.1 생성 화면

**경로**: `/workspaces/new`

```
┌──────────────────────────────────────┐
│           워크스페이스 만들기            │
│     팀과 함께 협업할 공간을 만드세요      │
│                                      │
│  ┌─ 워크스페이스 이름 ────────────┐    │
│  │ Acme Corp                    │    │
│  └──────────────────────────────┘    │
│  ┌─ URL 슬러그 ──────────────────┐    │
│  │ acme-corp                    │    │
│  └──────────────────────────────┘    │
│  https://app.com/workspaces/acme-corp │
│                                      │
│  ┌─ 설명 (선택) ──────────────────┐    │
│  │                              │    │
│  └──────────────────────────────┘    │
│                                      │
│  ┌──────────────────────────────┐    │
│  │      워크스페이스 만들기       │    │
│  └──────────────────────────────┘    │
│  만들기 후 팀원을 초대할 수 있습니다    │
└──────────────────────────────────────┘
```

### 3.2 생성 플로우

```
[사용자]
    │
    │  워크스페이스 이름, 슬러그, 설명 입력
    ▼
[POST /api/v1/workspaces]
    │  Request: { name: "Acme Corp", slug: "acme-corp", description: "..." }
    │
    │  1. SLUG 중복 검사
    │  2. 사용자당 소유 워크스페이스 수 제한 검사 (최대 10개)
    │  3. TB_COMM_WKSPC 생성 (TYPE_CD='TEAM', MAX_MBR_CNT=5)
    │  4. TR_COMM_WKSPC_MBR 생성 (생성자를 OWNER로 등록)
    ▼
[응답 201]
    { id: 3, slug: "acme-corp", name: "Acme Corp", type_cd: "TEAM", role_cd: "OWNER" }
    │
    ▼
[리다이렉트] → /workspaces/acme-corp/settings/members (멤버 초대 유도)
```

### 3.3 워크스페이스 전환

사이드바의 **WorkspaceSwitcher** 드롭다운으로 워크스페이스를 전환한다.

```
[사용자] ── 드롭다운에서 워크스페이스 선택 ──▶ PATCH /api/v1/workspaces/[id]/switch
    │
    │  TB_COMM_USER.BSC_WKSPC_ID 업데이트
    ▼
[리다이렉트] → /workspaces/{slug}/dashboard
```

---

## 4. STEP 3: 멤버 초대

워크스페이스 OWNER/ADMIN이 팀원을 초대하는 두 가지 방식이 있다.

### 4.1 이메일 초대

```
[OWNER/ADMIN]
    │
    │  이메일 주소 입력 + 역할 선택 (ADMIN/MEMBER/GUEST)
    ▼
[POST /api/v1/workspaces/[id]/invitations]
    │  Request: { emails: ["user1@example.com", "user2@example.com"], role_cd: "MEMBER" }
    │
    │  1. OWNER/ADMIN 권한 검증
    │  2. 멤버 수 제한 검사 (현재 멤버 + 대기 초대 < MAX_MBR_CNT)
    │  3. 이미 멤버/초대 대기 중인 이메일 필터링
    │  4. TB_COMM_WKSPC_INVT 생성 (TKN=nanoid(32), 만료 7일)
    │  5. 초대 이메일 발송 (수락 링크 포함)
    ▼
[초대받은 사용자]
    │
    │  이메일의 수락 링크 클릭 → /invitations/{token}
    │
    │  ── 비로그인 → 로그인 페이지 (redirect=초대URL) ──
    │  ── 미가입 → 회원가입 페이지 (redirect=초대URL) ──
    │  ── 로그인 상태 ──
    ▼
[POST /api/v1/invitations/{token}/accept]
    │
    │  1. 토큰 유효성 검증 (존재, 만료, 상태)
    │  2. 이메일 일치 확인
    │  3. TR_COMM_WKSPC_MBR 생성
    │  4. 초대 상태 → ACCEPTED
    │  5. 활성 구독 있으면 → 크레딧 비례 할당
    ▼
[리다이렉트] → /workspaces/{slug}/dashboard
```

### 4.2 초대 링크

```
[OWNER/ADMIN]
    │
    │  초대 링크 생성 요청
    ▼
[POST /api/v1/workspaces/[id]/invitations/link]
    │  Request: { role_cd: "MEMBER", max_uses: 50, expires_hours: 720 }
    │
    │  TB_COMM_WKSPC_INVT 생성 (INVT_TYPE_CD='LINK', MAX_USE_CNT=50)
    ▼
[응답] → invite_url: "https://app.com/invitations/abc123def456"
    │
    │  Slack, 메신저 등으로 링크 공유
    ▼
[링크를 받은 사용자] ── 동일한 수락 플로우 (이메일 검증 없음) ── 최대 50명까지 사용 가능
```

### 4.3 이메일 초대 vs 링크 초대

| 항목 | 이메일 초대 | 링크 초대 |
|------|-----------|---------|
| 대상 | 특정 이메일 1:1 | 링크를 가진 누구나 |
| 이메일 검증 | 수락 시 이메일 일치 확인 | 없음 |
| 사용 횟수 | 1회 (1명) | MAX_USE_CNT까지 |
| 만료 기간 | 7일 | 최대 30일 |
| 보안 수준 | 높음 | 중간 |

---

## 5. STEP 4: 결제 수단 등록

유료 플랜을 구독하려면 먼저 워크스페이스에 **결제 수단(카드)을 등록**해야 한다.

### 5.1 등록 화면

**경로**: `/workspaces/[workspaceId]/billing/payment-method`

### 5.2 등록 플로우 (토스페이먼츠 SDK)

```
[WS OWNER/ADMIN]
    │
    │  1. "새 결제 수단 추가" 클릭
    ▼
[토스페이먼츠 SDK 결제창]
    │
    │  2. 카드 정보 입력 + 본인 인증
    │  3. 인증 완료 → authKey, customerKey 반환
    ▼
[POST /api/v1/workspaces/{wsId}/billing/payment-methods]
    │  Request: { auth_key, customer_key, pg_provider: "TOSS" }
    │
    │  4. 워크스페이스 멤버십 + OWNER/ADMIN 권한 검증
    │  5. 토스페이먼츠 빌링키 발급 API 호출 (POST /v1/billing/authorizations/issue)
    │  6. 빌링키 AES-256 암호화 → TB_PAY_STLM_MTHD 저장
    │  7. 첫 결제 수단이면 기본 결제 수단(DFLT_YN='Y')으로 설정
    ▼
[응답 201]
    {
      id: 1,
      pg_provider: "TOSS",
      type_cd: "CARD",
      card_last4: "4242",
      card_brand: "삼성카드",
      is_default: true
    }
```

**PG사 추상화**: 토스페이먼츠 외에 NHN KCP, 나이스페이도 동일 인터페이스로 지원 가능한 PG-Agnostic 구조.

---

## 6. STEP 5: 구독 플랜 선택 및 결제

### 6.1 플랜 종류

| 플랜 | 월 요금 | 연 요금 (20% 할인) | 무료 체험 | 주요 기능 |
|------|--------|-------------------|---------|----------|
| **Basic** | 9,900원 | 95,040원 | 14일 | 3 프로젝트, 10GB 저장, 이메일 지원 |
| **Pro** | 29,900원 | 287,040원 | 14일 | 무제한 프로젝트, 100GB 저장, 우선 지원, API 접근 |
| **Enterprise** | 99,000원 | 950,400원 | - | 무제한 저장, 전담 지원, SSO/SAML, SLA 보장 |

### 6.2 구독 시작 플로우

```
[WS OWNER/ADMIN]
    │
    │  1. /pricing 페이지에서 플랜 선택
    │  2. 적용할 워크스페이스 선택 (OWNER/ADMIN인 WS 목록 표시)
    │  3. 결제 수단 확인 (없으면 → 결제 수단 등록 페이지)
    ▼
[POST /api/v1/workspaces/{wsId}/billing/subscriptions]
    │  Request: { plan_id: 2, payment_method_id: 1 }
    │
    │  4. 워크스페이스 멤버십 + OWNER/ADMIN 권한 검증
    │  5. 기존 활성 구독 존재 여부 확인 (워크스페이스당 1개)
    │  6. 플랜 유효성 검증
    │  7. 결제 수단 유효성 검증
    │
    │  ── 무료 체험 있는 플랜 ──
    │  8a. TB_PAY_SBSC 생성 (STTS_CD='TRIALING')
    │      TRIAL_BGNG_DT = NOW()
    │      TRIAL_END_DT = NOW() + 14일
    │      (결제 없음, 체험 종료 후 자동 결제)
    │
    │  ── 무료 체험 없는 플랜 ──
    │  8b. 청구서(TB_PAY_INVC) 생성 → 빌링키 결제 실행
    │      결제 성공 → TB_PAY_SBSC 생성 (STTS_CD='ACTIVE')
    │
    │  9. TB_COMM_WKSPC.MAX_MBR_CNT 업데이트 (플랜 기준값)
    │  10. 전체 멤버에게 크레딧 할당
    │  11. 이벤트 기록: subscription.created
    ▼
[응답 201]
    {
      id: 1,
      plan: { name: "Pro", amount: 29900 },
      status_cd: "TRIALING",
      trial_start: "2026-02-14T00:00:00Z",
      trial_end: "2026-02-28T00:00:00Z"
    }
```

### 6.3 구독 상태 전이도

```
                     trial start         trial end + payment success
[최초] ──────────▶ [TRIALING] ──────────────────────────────▶ [ACTIVE] ◀──────┐
                     │                                          │    │        │
                     │ trial end + payment fail                 │    │        │
                     ▼                                          │    │        │
                 [CANCELED]  ◀── cancel ────────────────────────┘    │        │
                     ▲                                               │        │
                     │                                    payment    │        │
                     │  dunning all failed                failed     │        │
                     │                                               ▼        │
                     ├─────────────────────────────── [PAST_DUE] ─────────────┘
                     │                                     │     payment success
                     │                                     │ dunning exhausted
                     │                                     ▼
                     ├────────────────────────────── [SUSPENDED]
                     │                                     │
                     │                                     │ 결제수단 변경 + 성공
                     │                                     ▼
                     │                                  [ACTIVE]
                     │
                     │         pause           resume
                [ACTIVE] ────────────▶ [PAUSED] ────────────▶ [ACTIVE]
```

---

## 7. STEP 6: 구독 이후 운영

### 7.1 정기결제 (매월 자동)

```
[Cron Scheduler - 매일 09:00 KST]
    │
    │  CRNT_PRD_END_DT <= NOW() && STTS_CD IN ('ACTIVE','TRIALING') 구독 조회
    ▼
[각 워크스페이스 구독별]
    │
    │  1. 청구서 생성 (INVC_NO: INV-YYYYMMDD-XXXX)
    │  2. 빌링키 복호화 (AES-256)
    │  3. PG사 결제 요청 (멱등성 키 포함)
    │
    ├── 결제 성공
    │     Invoice: PAID, 구독 기간 갱신
    │     이전 기간 크레딧 만료 → 신규 기간 크레딧 할당
    │
    └── 결제 실패
          구독: PAST_DUE → Dunning 시작
```

### 7.2 Dunning (결제 재시도) 전략

| 시도 | 시점 | 유형 | 알림 |
|------|------|------|------|
| 1차 | 실패 + 1시간 | 자동 재시도 | 없음 |
| 2차 | 실패 + 24시간 | 재시도 + 이메일 | "결제 실패, 재시도 예정" |
| 3차 | 실패 + 72시간 | 재시도 + SMS | "결제수단 확인 요청" |
| 4차 | 실패 + 7일 | 최종 알림 | "서비스 정지 예고" |
| 정지 | 실패 + 14일 | - | 구독 SUSPENDED, 워크스페이스 읽기 전용 |

### 7.3 플랜 변경 (업/다운그레이드)

**비례 배분(Proration) 방식으로 차액을 정산한다.**

```
[업그레이드 예시]
현재: Pro (₩29,900/월), 변경 시점: 02.15 (잔여 14일/28일)
변경: Enterprise (₩99,000/월)

미사용 크레딧 = (₩29,900 / 28) × 14 = ₩14,950
신규 비례 요금 = (₩99,000 / 28) × 14 = ₩49,500
즉시 결제 = ₩49,500 - ₩14,950 = ₩34,550
```

```
[다운그레이드 예시]
현재: Enterprise (₩99,000/월), 변경 시점: 02.20 (잔여 9일/28일)
변경: Pro (₩29,900/월)

크레딧 잔액 = (₩99,000/28 × 9) - (₩29,900/28 × 9) = ₩22,212
→ 다음 청구서에 크레딧으로 적용
```

### 7.4 구독 해지

| 해지 방식 | 설명 |
|----------|------|
| **기간 종료 후 해지** (기본) | 현재 기간 종료까지 서비스 이용 가능, 이후 해지 |
| **즉시 해지** | 잔여 기간 비례 환불 가능, 즉시 서비스 중단 |

### 7.5 크레딧 시스템

- **멤버별 빌링 주기 단위** 크레딧 할당 (TB_PAY_CRDT_BLNC)
- 서비스 사용(AI 메시지 생성 등) 시 크레딧 차감
- 소진 시 서비스 사용 불가, 상위 플랜 업그레이드 안내
- 월 중 가입 멤버는 잔여 일수 비례 배분 할당
- OWNER/ADMIN이 멤버별 크레딧 수동 조정 가능

### 7.6 구독 이벤트 → 워크스페이스 영향

| 이벤트 | 워크스페이스 영향 |
|--------|---------------|
| `subscription.created` | MAX_MBR_CNT 업데이트 + 전체 멤버 크레딧 할당 |
| `subscription.upgraded` | MAX_MBR_CNT 증가 + 크레딧 재조정 |
| `subscription.downgraded` | MAX_MBR_CNT 감소 (경고만, 강제 퇴장 없음) |
| `subscription.renewed` | 이전 크레딧 만료 + 신규 크레딧 할당 |
| `subscription.canceled` | 기간 만료 후 MAX_MBR_CNT 무료 기본값 복원 |
| `subscription.suspended` | 워크스페이스 읽기 전용 모드 전환 |

---

## 8. 화면 경로 요약

### 인증 관련

| 경로 | 접근 권한 | 설명 |
|------|----------|------|
| `/auth/login` | Public | 이메일/소셜 로그인 |
| `/auth/signup` | Public | 회원가입 + 약관 동의 |
| `/auth/terms-agreement` | Bearer | 미동의 약관 추가 동의 |

### 워크스페이스 관련

| 경로 | 접근 권한 | 설명 |
|------|----------|------|
| `/workspaces` | Bearer | 워크스페이스 목록/선택 |
| `/workspaces/new` | Bearer | 팀 워크스페이스 생성 |
| `/workspaces/[slug]/dashboard` | WS MEMBER | 대시보드 |
| `/workspaces/[slug]/settings` | WS OWNER/ADMIN | 일반 설정 |
| `/workspaces/[slug]/settings/members` | WS OWNER/ADMIN | 멤버 관리/초대 |
| `/invitations/[token]` | Public/Bearer | 초대 수락 |

### 결제 관련

| 경로 | 접근 권한 | 설명 |
|------|----------|------|
| `/pricing` | Public | 요금제 안내 + 플랜 선택 |
| `/workspaces/[wsId]/billing/payment-method` | WS OWNER/ADMIN | 결제 수단 관리 |
| `/workspaces/[wsId]/billing/subscription` | WS OWNER/ADMIN | 구독 관리 |
| `/workspaces/[wsId]/billing/invoices` | WS OWNER/ADMIN | 결제 내역 |
| `/workspaces/[wsId]/billing/credits` | WS OWNER/ADMIN | 멤버별 크레딧 관리 |
| `/workspaces/[wsId]/billing/payment-failed` | WS OWNER/ADMIN | 결제 실패 안내 |

---

## 9. API 호출 순서 요약

전체 플로우에서 호출되는 API를 순서대로 정리한다.

```
① 회원가입/로그인
   POST /api/v1/auth/signup          ← 회원가입 (+ 개인 WS 자동 생성)
   POST /api/v1/auth/login           ← 로그인

② 워크스페이스 생성
   POST /api/v1/workspaces           ← 팀 WS 생성
   PATCH /api/v1/workspaces/[id]/switch  ← WS 전환

③ 멤버 초대
   POST /api/v1/workspaces/[id]/invitations       ← 이메일 초대
   POST /api/v1/workspaces/[id]/invitations/link   ← 초대 링크 생성
   GET  /api/v1/invitations/[token]                ← 초대 정보 조회
   POST /api/v1/invitations/[token]/accept         ← 초대 수락

④ 결제 수단 등록
   GET  /api/v1/workspaces/[wsId]/billing/payment-methods      ← 목록 조회
   POST /api/v1/workspaces/[wsId]/billing/payment-methods      ← 카드 등록

⑤ 구독 결제
   GET  /api/v1/billing/plans                                   ← 플랜 목록
   POST /api/v1/workspaces/[wsId]/billing/subscriptions         ← 구독 시작
   GET  /api/v1/workspaces/[wsId]/billing/subscriptions/current ← 현재 구독 조회

⑥ 구독 관리
   PATCH /api/v1/workspaces/[wsId]/billing/subscriptions/[id]/plan    ← 플랜 변경
   POST  /api/v1/workspaces/[wsId]/billing/subscriptions/[id]/cancel  ← 구독 해지
   GET   /api/v1/workspaces/[wsId]/billing/invoices                   ← 결제 내역

⑦ 크레딧
   GET  /api/v1/workspaces/[wsId]/billing/credits/me           ← 내 크레딧 조회
   GET  /api/v1/workspaces/[wsId]/billing/credits/me/history   ← 사용 내역
   GET  /api/v1/workspaces/[wsId]/billing/credits/members      ← 멤버별 현황
```

---

## 10. 상태 코드 정리

### 사용자 상태 (TB_COMM_USER.STTS_CD)

| 코드 | 설명 |
|------|------|
| `ACTIVE` | 정상 활성 계정 |
| `SUSPENDED` | 이용 정지 |
| `WITHDRAWN` | 탈퇴 처리 |

### 워크스페이스 상태 (TB_COMM_WKSPC.STTS_CD)

| 코드 | 설명 |
|------|------|
| `ACTIVE` | 정상 사용 중 |
| `SUSPENDED` | 결제 실패 등으로 정지 (읽기 전용) |
| `DELETED` | Soft Delete |

### 워크스페이스 역할 (TR_COMM_WKSPC_MBR.ROLE_CD)

| 코드 | 결제 관리 | 멤버 관리 | 설정 변경 | 삭제/이전 |
|------|----------|---------|---------|----------|
| `OWNER` | O | O | O | O |
| `ADMIN` | O | O (제한적) | O | X |
| `MEMBER` | X | X | X | X |
| `GUEST` | X | X | X | X |

### 구독 상태 (TB_PAY_SBSC.STTS_CD)

| 코드 | 설명 |
|------|------|
| `TRIALING` | 무료 체험 기간 (14일) |
| `ACTIVE` | 정상 구독 중 |
| `PAST_DUE` | 결제 실패, 재시도 중 |
| `PAUSED` | 사용자 요청 일시정지 |
| `SUSPENDED` | 연속 결제 실패로 정지 |
| `CANCELED` | 구독 해지 완료 |

### 청구서 상태 (TB_PAY_INVC.STTS_CD)

| 코드 | 설명 |
|------|------|
| `DRAFT` | 생성 직후, 미확정 |
| `OPEN` | 결제 대기 중 |
| `PAID` | 결제 완료 |
| `VOID` | 무효 처리 |
| `UNCOLLECTIBLE` | 미수 (dunning 실패) |

### 결제 상태 (TB_PAY_STLM.STTS_CD)

| 코드 | 설명 |
|------|------|
| `PENDING` | 결제 대기 |
| `SUCCEEDED` | 결제 성공 |
| `FAILED` | 결제 실패 |
| `REFUNDED` | 전액 환불 |
| `PARTIAL_REFUNDED` | 부분 환불 |
