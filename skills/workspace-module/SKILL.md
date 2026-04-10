---
name: workspace-module
description: "워크스페이스 모듈을 자동으로 구축합니다. 레퍼런스 설계 문서를 기반으로 블루프린트 작성, 스프린트 생성, 구현, 테스트 시나리오 작성, 테스트 실행 및 디버깅까지 전체 파이프라인을 자동 실행합니다. 워크스페이스 CRUD, 멤버 관리, 초대 시스템(이메일/링크), 소유권 이전, 워크스페이스 전환, 인증/결제 모듈 연동 기능을 포함합니다."
argument-hint: "[target-project-path]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Agent
---

# ASTRA 워크스페이스 모듈 자동 구축

레퍼런스 설계 문서(`$CLAUDE_PLUGIN_ROOT/docs/workspace/`)를 기반으로 대상 프로젝트에 워크스페이스 모듈 전체를 자동 구축합니다.

**자동 구축 범위**:
- 워크스페이스 CRUD (생성/조회/수정/삭제)
- 멤버 관리 (목록/역할변경/강제퇴장/자발탈퇴/소유권이전)
- 초대 시스템 (이메일 초대 + 초대 링크 + 수락/거절/취소)
- 워크스페이스 전환 (WorkspaceSwitcher + 기본 워크스페이스)
- 화면 구현 (생성/설정/멤버관리/초대수락/전환기)
- 기존 모듈 통합 (인증: 회원가입 시 개인 WS 자동생성, 결제: 구독↔멤버수 연동)

## 실행 절차

### Step 0: 사전 준비 및 컨텍스트 수집

#### A. 레퍼런스 설계 문서 로드

`$CLAUDE_PLUGIN_ROOT/docs/workspace/` 디렉토리의 파일들을 읽어 레퍼런스 설계 정보를 로드한다:

**system-design.md** (핵심 설계 문서):
1. 아키텍처 개요 — 멀티테넌시, 멀티 워크스페이스 멤버십, 역할 체계 (섹션 1)
2. 기술 스택 — nanoid, slugify (섹션 2)
3. 데이터베이스 스키마 — TB_COMM_WKSPC, TR_COMM_WKSPC_MBR, TB_COMM_WKSPC_INVT + TB_COMM_USER 확장 (섹션 3)
4. API 설계 — 워크스페이스/멤버/초대 엔드포인트 (섹션 4)
5. 화면 구성 — 생성, 멤버관리, 초대수락, 전환기, 초대모달 (섹션 5)
6. 유즈케이스 및 데이터 플로우 — 9개 UC (섹션 6)
7. 보안 설계 — 접근 제어, 초대 보안, 데이터 격리, Rate Limiting (섹션 7)
8. 디렉토리 구조 (섹션 8)
9. 구현 순서 — Phase 1~5 (섹션 9)

**flow.md** (플로우 문서):
- 전체 플로우: 로그인 → 개인 WS 진입 → 팀 WS 생성 → 멤버 초대 → 결제 → 구독
- 회원가입 시 개인 워크스페이스 자동 생성 상세
- 이메일/링크 초대 플로우 상세
- 결제/구독 연동 플로우

> **중요**: 레퍼런스는 **AMA 프로젝트(Next.js 14 + PostgreSQL + Drizzle ORM)**를 기준으로 작성되었다. 대상 프로젝트의 기술 스택에 맞게 **적응(adapt)**해야 한다.

#### B. 대상 프로젝트 분석

`$ARGUMENTS`에서 대상 프로젝트 경로를 파싱한다. 인자가 없으면 현재 작업 디렉토리를 사용한다.

대상 프로젝트에서 다음을 분석한다:

1. `CLAUDE.md` 읽기 — 기술 스택, 프로젝트 구조, 컨벤션 확인
2. `package.json` 또는 `build.gradle` 또는 `pom.xml` 또는 `pyproject.toml` 읽기 — 프레임워크/의존성 파악
3. `docs/blueprints/` 스캔 — 기존 블루프린트 번호 확인 (다음 번호 결정)
4. `docs/database/database-design.md` 읽기 — 기존 DB 스키마 확인 (특히 인증 모듈 테이블)
5. `docs/sprints/` 스캔 — `sprint-{N}-{name}/` 패턴 디렉토리에서 현재 스프린트 번호 확인
6. `src/` 스캔 — 기존 코드 구조, 라우팅 패턴, 인증 모듈 코드 확인
7. `src/styles/design-tokens.css` + `docs/design-system/` 스캔 — 디자인 토큰, 컴포넌트 패턴 확인

#### C. 인증 모듈 의존성 확인

워크스페이스 모듈은 인증 모듈에 **의존**한다. 다음을 확인한다:

1. TB_COMM_USER 테이블 존재 여부
2. 인증 미들웨어/JWT 검증 코드 존재 여부
3. AuthContext/인증 상태 관리 존재 여부

인증 모듈이 없는 경우 `AskUserQuestion`으로 사용자에게 알린다:

```
## 인증 모듈 의존성 확인

워크스페이스 모듈은 인증 모듈(TB_COMM_USER, JWT 인증)에 의존합니다.
현재 프로젝트에서 인증 모듈이 감지되지 않았습니다.

다음 중 선택해 주세요:
1. 인증 모듈을 먼저 구축 (/auth-module 실행)
2. 기존 인증 시스템이 있으며 경로를 알려주겠음
3. 인증 모듈 없이 워크스페이스 모듈만 구축 (사용자 테이블 직접 생성)
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
| React (TSX) | React (TSX) | 그대로 사용 |
| React (TSX) | Vue 3 | Composition API + `<script setup>` |
| React (TSX) | Angular | Component + Service + Guard |
| React (TSX) | React Native | RN 컴포넌트 + AsyncStorage |
| nanoid | nanoid | 그대로 사용 |
| nanoid | UUID (Java) | `UUID.randomUUID()` |
| slugify | slugify | 그대로 사용 / 자체 유틸 |
| nodemailer (SMTP) | Spring Mail | `JavaMailSender` |
| nodemailer (SMTP) | NestJS Mailer | `@nestjs-modules/mailer` |

적응이 필요한 경우 `AskUserQuestion`으로 사용자에게 확인한다:

```
## 워크스페이스 모듈 기술 스택 확인

레퍼런스: Next.js 14 + PostgreSQL + Drizzle ORM
대상 프로젝트: {detected-tech-stack}

다음 사항을 확인해 주세요:
1. ORM: {detected}
2. 이메일 발송 방식: SMTP / SendGrid / AWS SES / 기타 ({detected})
3. 프론트엔드 프레임워크: {detected}
4. 결제 모듈 존재 여부: {detected} (구독↔멤버수 연동에 사용)

추가 요구사항이 있으면 알려주세요 (예: SSO 연동, 조직 계층 구조 등).
```

#### E. 기능 모듈 정의

레퍼런스 설계 문서에서 추출한 워크스페이스 모듈 기능 목록:

| # | 모듈 | 기능 | API 엔드포인트 | 화면 |
|---|------|------|--------------|------|
| 1 | 워크스페이스 | 내 워크스페이스 목록 | `GET /workspaces` | `/workspaces` |
| 2 | 워크스페이스 | 워크스페이스 생성 | `POST /workspaces` | `/workspaces/new` |
| 3 | 워크스페이스 | 워크스페이스 상세 조회 | `GET /workspaces/[id]` | `/workspaces/[slug]/dashboard` |
| 4 | 워크스페이스 | 워크스페이스 수정 | `PATCH /workspaces/[id]` | `/workspaces/[slug]/settings` |
| 5 | 워크스페이스 | 워크스페이스 삭제 | `DELETE /workspaces/[id]` | - |
| 6 | 워크스페이스 | 워크스페이스 전환 | `PATCH /workspaces/[id]/switch` | WorkspaceSwitcher |
| 7 | 멤버 | 멤버 목록 조회 | `GET /workspaces/[id]/members` | `/workspaces/[slug]/settings/members` |
| 8 | 멤버 | 멤버 역할 변경 | `PATCH /workspaces/[id]/members/[memberId]/role` | - |
| 9 | 멤버 | 멤버 강제 퇴장 | `DELETE /workspaces/[id]/members/[memberId]` | - |
| 10 | 멤버 | 워크스페이스 탈퇴 | `POST /workspaces/[id]/members/leave` | - |
| 11 | 멤버 | 소유권 이전 | `POST /workspaces/[id]/transfer-ownership` | - |
| 12 | 초대 | 초대 목록 조회 | `GET /workspaces/[id]/invitations` | - |
| 13 | 초대 | 이메일 초대 발송 | `POST /workspaces/[id]/invitations` | InviteMemberModal |
| 14 | 초대 | 초대 링크 생성 | `POST /workspaces/[id]/invitations/link` | - |
| 15 | 초대 | 초대 취소 | `DELETE /workspaces/[id]/invitations/[invitationId]` | - |
| 16 | 초대 | 초대 정보 조회 | `GET /invitations/[token]` | `/invitations/[token]` |
| 17 | 초대 | 초대 수락 | `POST /invitations/[token]/accept` | - |
| 18 | 초대 | 초대 거절 | `POST /invitations/[token]/decline` | - |

---

### Step 1: 블루프린트 자동 생성

레퍼런스 설계 문서를 기반으로 워크스페이스 모듈 블루프린트를 생성한다.

#### A. 블루프린트 번호 결정

`docs/blueprints/` 디렉토리를 스캔하여 기존 블루프린트 번호를 확인하고 다음 번호를 결정한다.

```
NNN = (기존 최대 번호) + 1
```

#### A-1. dev 브랜치 전환 및 최신화

블루프린트 파일을 생성하기 전에, `dev` 브랜치로 전환하고 최신 상태로 동기화한다. 작업 브랜치는 생성하지 않으며, `dev`에서 직접 작업한다. 작업 브랜치 생성은 `/pr-merge` 실행 시 자동으로 처리된다.

1. **현재 브랜치 확인**: `git branch --show-current`
2. **이미 `dev` 브랜치인 경우 스킵**: 현재 브랜치가 `dev`이면 아래 3~5단계를 건너뛰고 pull만 실행한다 (`git pull origin dev`)
3. **미커밋 변경사항 보존**: `git status --porcelain`으로 확인하여 변경사항이 있으면 `git stash --include-untracked`로 임시 저장한다 (untracked 파일도 포함)
4. **dev 브랜치 전환 및 최신화**: `git fetch origin dev && git checkout dev && git pull origin dev`
5. **stash 복원**: step 3에서 stash 했으면 `git stash pop`으로 복원한다. 충돌 발생 시 충돌 파일 목록을 사용자에게 보고하고 수동 해결을 요청한다.

> **참고**: `dev` 브랜치가 존재하지 않으면 `main` 또는 `master` 브랜치에서 작업한다. 어떤 기본 브랜치도 없으면 현재 브랜치에서 작업한다.

#### B. 워크스페이스 모듈 블루프린트 생성

`docs/blueprints/{NNN}-workspace/blueprint.md` 파일을 생성한다.

레퍼런스 설계 문서의 내용을 대상 프로젝트 기술 스택에 맞게 적응하여 다음 섹션을 포함한다:

```markdown
# 워크스페이스 관리 모듈 설계 문서

## 1. 개요
- 설계 원칙: 멀티테넌시, 멀티 워크스페이스 멤버십, 워크스페이스=과금 주체 (레퍼런스 섹션 1.1)
- 아키텍처 다이어그램 (대상 프로젝트에 맞게 수정, 레퍼런스 섹션 1.2)
- 타 모듈 관계: 인증 ← 워크스페이스 → 결제/IAM (레퍼런스 섹션 1.3)
- 워크스페이스 역할 vs 시스템 역할 (레퍼런스 섹션 1.4)

## 2. 기술 스택
- 신규 의존성: nanoid, slugify (레퍼런스 섹션 2.1)
- 환경 변수 (레퍼런스 섹션 2.2 적응 — 실제 값은 placeholder)

## 3. 데이터베이스 스키마
- ER 다이어그램 (레퍼런스 섹션 3.1)
- TB_COMM_WKSPC 정의 (레퍼런스 섹션 3.2)
- TR_COMM_WKSPC_MBR 정의 (레퍼런스 섹션 3.3)
- TB_COMM_WKSPC_INVT 정의 (레퍼런스 섹션 3.4)
- TB_COMM_USER 확장 — BSC_WKSPC_ID (레퍼런스 섹션 3.5)
- DDL (대상 DB에 맞게 변환, 레퍼런스 섹션 3.6)
- ORM 스키마 정의 (대상 ORM에 맞게 변환, 레퍼런스 섹션 3.7)

## 4. API 설계
- 엔드포인트 목록: 워크스페이스 6개 + 멤버 5개 + 초대 7개 (레퍼런스 섹션 4.1)
- 상세 API 스펙 (레퍼런스 섹션 4.2 적응)
  - Request/Response 스키마 (Zod → 대상 검증 라이브러리)
  - 비즈니스 로직 (트랜잭션, 권한 검증)
  - 에러 코드
- 워크스페이스 멤버십 미들웨어 (레퍼런스 섹션 4.4)

## 5. 화면 구성
- 화면 목록 (레퍼런스 섹션 5.1)
- 워크스페이스 생성 페이지 (레퍼런스 섹션 5.2)
- 멤버 관리 페이지 (레퍼런스 섹션 5.3)
- 초대 수락 페이지 (레퍼런스 섹션 5.4)
- WorkspaceSwitcher (레퍼런스 섹션 5.5)
- 멤버 초대 모달 (레퍼런스 섹션 5.6)

## 6. 유즈케이스 및 데이터 플로우
- UC-01: 회원가입 → 개인 WS 자동 생성 (레퍼런스 섹션 6.1)
- UC-02: 팀 워크스페이스 생성 (레퍼런스 섹션 6.2)
- UC-03: 이메일 기반 멤버 초대 (레퍼런스 섹션 6.3)
- UC-04: 초대 링크 기반 멤버 참여 (레퍼런스 섹션 6.4)
- UC-05: 워크스페이스 기반 구독 결제 (레퍼런스 섹션 6.5)
- UC-06: 워크스페이스 정지 → 결제 실패 대응 (레퍼런스 섹션 6.6)
- UC-07: 소유권 이전 (레퍼런스 섹션 6.7)
- UC-08: 워크스페이스 전환 (레퍼런스 섹션 6.8)
- UC-09: 회원 탈퇴 → 워크스페이스 처리 (레퍼런스 섹션 6.9)

## 7. 보안 설계
- 접근 제어: 멤버십 미들웨어, 역할 계층 (레퍼런스 섹션 7.1)
- 초대 보안: 토큰 엔트로피, 만료, 사용 제한 (레퍼런스 섹션 7.2)
- 데이터 격리: WKSPC_ID 기반 논리적 격리 (레퍼런스 섹션 7.3)
- 소유권 이전 보안: 재인증, 트랜잭션 (레퍼런스 섹션 7.4)
- Rate Limiting (레퍼런스 섹션 7.5)

## 8. 디렉토리 구조
- 신규 추가 파일 목록 (대상 프로젝트 구조에 맞게, 레퍼런스 섹션 8)

## 9. 구현 순서
- Phase 1~5 (레퍼런스 섹션 9)
```

> **참고**: 레퍼런스 설계 문서의 모든 섹션을 빠짐없이 반영한다. 기술 스택만 대상 프로젝트에 맞게 변환하고, 비즈니스 로직과 보안 설계는 원본을 최대한 유지한다. flow.md의 내용도 해당 섹션에 통합한다.

#### C. DB 설계 문서 반영

`docs/database/database-design.md`에 워크스페이스 모듈 테이블을 추가한다:

1. 3개 테이블(TB_COMM_WKSPC, TR_COMM_WKSPC_MBR, TB_COMM_WKSPC_INVT) 추가
2. TB_COMM_USER 확장 (BSC_WKSPC_ID 컬럼 추가)
3. ER 다이어그램 업데이트 (인증 모듈과의 FK 관계 포함)
4. FK 관계 요약 업데이트
5. 공공 데이터 표준 네이밍 규칙 준수 확인

#### D. 블루프린트 생성 완료 보고

```
## Step 1 완료: 블루프린트 생성

### 생성된 파일
- docs/blueprints/{NNN}-workspace/blueprint.md (워크스페이스 모듈 설계 문서)
- docs/database/database-design.md (DB 테이블 3개 추가 + TB_COMM_USER 확장)

### 포함된 기능
- 워크스페이스 API 6개 (list, create, detail, update, delete, switch)
- 멤버 API 5개 (list, role-change, remove, leave, transfer-ownership)
- 초대 API 7개 (list, email-invite, link-invite, cancel, info, accept, decline)
- 화면 6개 (workspace-list, create, dashboard, settings, members, invitation-accept)
- 컴포넌트 5개 (WorkspaceSwitcher, InviteMemberModal, MemberRoleDropdown, InvitationAcceptCard, WorkspaceAvatar)

Step 2로 진행합니다...
```

---

### Step 2: 스프린트 계획 자동 생성

블루프린트의 구현 순서(Phase 1~5)를 기반으로 스프린트 프롬프트 맵을 생성한다.

#### A. 스프린트 번호 결정

`docs/sprints/` 디렉토리에서 `sprint-{N}-{name}/` 패턴 디렉토리를 스캔하여 다음 스프린트 번호를 결정한다.

#### B. 스프린트 프롬프트 맵 생성

`docs/sprints/sprint-{N}-workspace/prompt-map.md`를 생성한다.

레퍼런스의 Phase를 스프린트 Feature 단위로 분할한다:

```markdown
# Sprint {N} Prompt Map

## Sprint Goal
워크스페이스 모듈 전체 구축 — 워크스페이스 CRUD, 멤버 관리, 초대 시스템, 기존 모듈 통합

## Feature 1: 기반 인프라 (Phase 1)

### 1.1 Design Prompt
(Already completed — see docs/blueprints/{NNN}-workspace/blueprint.md 섹션 2~3)

### 1.2 DB Design Reflection Prompt
/feature-dev "docs/blueprints/{NNN}-workspace/blueprint.md 섹션 3의 DDL을 기반으로
docs/database/database-design.md에 워크스페이스 모듈 테이블 3개를 추가/업데이트한다.
TB_COMM_USER 확장(BSC_WKSPC_ID)도 반영한다.
ER 다이어그램과 FK 관계도 반영한다. 코드 수정 없음."

### 1.3 Test Case Prompt
/feature-dev "docs/blueprints/{NNN}-workspace/blueprint.md를 기반으로
docs/tests/test-cases/sprint-{N}/workspace-infra-test-cases.md에
DB 스키마 검증, 슬러그 생성 유틸, Zod 검증 스키마 테스트 케이스를 작성한다. 코드 수정 없음."

### 1.4 Implementation Prompt
/feature-dev "docs/blueprints/{NNN}-workspace/blueprint.md Phase 1을 참조하여
워크스페이스 기반 인프라를 구현한다:
- 의존성 설치 (nanoid, slugify)
- 환경 변수 설정
- ORM 스키마 정의 (TB_COMM_WKSPC, TR_COMM_WKSPC_MBR, TB_COMM_WKSPC_INVT)
- DB 마이그레이션 (+ TB_COMM_USER.BSC_WKSPC_ID 추가)
- Zod 검증 스키마
- 슬러그 생성 유틸 (중복 처리 포함)
테스트 실행 후 결과를 docs/tests/test-reports/에 기록한다."

## Feature 2: 핵심 API — 워크스페이스 CRUD + 멤버 관리 (Phase 2)

### 2.1 Design Prompt
(Already completed — see docs/blueprints/{NNN}-workspace/blueprint.md 섹션 4.2.1~4.2.10)

### 2.2 Test Case Prompt
/feature-dev "docs/blueprints/{NNN}-workspace/blueprint.md 섹션 4.2.1~4.2.10을 기반으로
docs/tests/test-cases/sprint-{N}/workspace-api-test-cases.md에
워크스페이스 CRUD, 멤버 관리, 소유권 이전, 워크스페이스 전환 API 테스트 케이스를 작성한다.
Happy Path, Error Path, Edge Case 포함. 코드 수정 없음."

### 2.3 Implementation Prompt
/feature-dev "docs/blueprints/{NNN}-workspace/blueprint.md Phase 2를 참조하여 구현:
- 워크스페이스 멤버십 미들웨어 (멤버십 확인 + 역할 검증)
- 워크스페이스 CRUD API (list, create, detail, update, delete)
  - 생성 시 OWNER 자동 등록, 슬러그 중복 검사, 소유 수 제한
  - 삭제 시 Soft Delete, 멤버 전체 탈퇴, BSC_WKSPC_ID 재설정
- 멤버 관리 API (list, role-change, remove, leave)
  - 역할 계층 기반 권한 검증 (OWNER > ADMIN > MEMBER > GUEST)
  - 자기 자신 보호 (역할 변경/퇴장 불가)
- 워크스페이스 전환 API (BSC_WKSPC_ID 업데이트)
- 소유권 이전 API (트랜잭션 내 역할 교환 + OWNR_ID 변경)
- WorkspaceContext 구현 (currentWorkspace, switchWorkspace, 역할 유틸)
테스트 실행 후 결과를 docs/tests/test-reports/에 기록한다."

## Feature 3: 초대 시스템 (Phase 3)

### 3.1 Design Prompt
(Already completed — see docs/blueprints/{NNN}-workspace/blueprint.md 섹션 4.2.4~4.2.6, 섹션 6.3~6.4)

### 3.2 Test Case Prompt
/feature-dev "docs/blueprints/{NNN}-workspace/blueprint.md 초대 관련 섹션을 기반으로
docs/tests/test-cases/sprint-{N}/invitation-test-cases.md에
이메일 초대, 링크 초대, 초대 수락/거절/취소 테스트 케이스를 작성한다.
토큰 만료, 사용 횟수 제한, 이메일 불일치 등 Edge Case 포함. 코드 수정 없음."

### 3.3 Implementation Prompt
/feature-dev "docs/blueprints/{NNN}-workspace/blueprint.md Phase 3을 참조하여 구현:
- 초대 서비스 (이메일 발송, 토큰 생성/검증)
- 이메일 초대 API (복수 이메일, 역할 지정, 멤버 수 제한, 중복 필터링)
- 초대 링크 생성 API (MAX_USE_CNT, 만료 설정)
- 초대 정보 조회 API (Public, 수락 전 미리보기)
- 초대 수락 API (이메일 검증, 멤버 생성, USE_CNT 증가, 크레딧 할당)
- 초대 거절 API
- 초대 취소 API
- 만료 초대 정리 (Cron Job 또는 스케줄러)
테스트 실행 후 결과를 docs/tests/test-reports/에 기록한다."

## Feature 4: 화면 구현 (Phase 4)

### 4.1 Design Prompt
(Already completed — see docs/blueprints/{NNN}-workspace/blueprint.md 섹션 5)

### 4.2 Test Case Prompt
/feature-dev "docs/blueprints/{NNN}-workspace/blueprint.md 섹션 5를 기반으로
docs/tests/test-cases/sprint-{N}/workspace-ui-test-cases.md에
워크스페이스 생성, 멤버 관리, 초대 수락, 워크스페이스 전환 화면의 E2E 테스트 시나리오를 작성한다.
사용자 여정 기반으로 Happy/Error/Edge 시나리오 포함. 코드 수정 없음."

### 4.3 Implementation Prompt
/feature-dev "docs/blueprints/{NNN}-workspace/blueprint.md Phase 4를 참조하여 구현:
- WorkspaceSwitcher 컴포넌트 (드롭다운, 현재 WS 표시, 전환)
- 워크스페이스 생성 페이지 (이름, 슬러그, 설명 입력 + 자동 슬러그 생성)
- 워크스페이스 설정 페이지 (이름/슬러그/설명 수정, 삭제)
- 멤버 관리 페이지 (멤버 목록, 역할 변경, 강제 퇴장, 대기 초대, 초대 링크)
- 초대 수락 페이지 (미리보기, 수락/거절, 비로그인 시 리다이렉트)
- 멤버 초대 모달 (이메일 입력, 역할 선택, 초대 링크 생성)
테스트 실행 후 결과를 docs/tests/test-reports/에 기록한다."

## Feature 5: 기존 모듈 통합 (Phase 5)

### 5.1 Test Case Prompt
/feature-dev "docs/blueprints/{NNN}-workspace/blueprint.md 섹션 6.1, 6.9를 기반으로
docs/tests/test-cases/sprint-{N}/workspace-integration-test-cases.md에
통합 테스트 케이스를 작성한다: 회원가입→개인WS생성, 회원탈퇴→WS처리, 구독→멤버수연동,
워크스페이스 전환→메뉴 반영. 코드 수정 없음."

### 5.2 Implementation Prompt
/feature-dev "docs/blueprints/{NNN}-workspace/blueprint.md Phase 5를 참조하여 구현:
- 인증 모듈: 회원가입 시 개인 워크스페이스 자동 생성 로직 추가
- 인증 모듈: 회원 탈퇴 시 워크스페이스 처리 로직 추가 (소유권 이전 강제, 멤버 탈퇴)
- 인증 모듈: JWT 토큰에 현재 워크스페이스 정보 추가 (선택)
- 결제 모듈 연동 (있는 경우): 구독 상태 변경 시 MAX_MBR_CNT 연동
- 사이드바: WorkspaceSwitcher 통합
- 다국어 메시지 추가 (ko/en)
- 기존 사용자 마이그레이션 스크립트 (개인 워크스페이스 일괄 생성)
- Rate Limiting 적용
테스트 실행 후 결과를 docs/tests/test-reports/에 기록한다."
```

#### C. 스프린트 프로그레스 트래커 생성

`docs/sprints/sprint-{N}-workspace/progress.md`를 생성한다:

```markdown
# Sprint {N} Progress Tracker

## Sprint Information
- **Sprint Number**: {N}
- **Sprint Goal**: 워크스페이스 모듈 전체 구축
- **Start Date**: {TODAY}
- **End Date**: {TODAY + 7 days}
- **Status**: In Progress

<!-- PROGRESS_TABLE_START -->
## Feature Progress

| Feature | Blueprint | DB Design | Test Cases | Implementation | Test Report | Status |
|---------|-----------|-----------|------------|----------------|-------------|--------|
| 기반 인프라 | Done | - | - | - | - | Not Started |
| 핵심 API (CRUD + 멤버) | Done | Done | - | - | - | Not Started |
| 초대 시스템 | Done | Done | - | - | - | Not Started |
| 화면 구현 | Done | N/A | - | - | - | Not Started |
| 기존 모듈 통합 | Done | N/A | - | - | - | Not Started |

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
| {TIMESTAMP} | blueprint | docs/blueprints/{NNN}-workspace/blueprint.md | 워크스페이스 모듈 블루프린트 생성 |
| {TIMESTAMP} | db-design | docs/database/database-design.md | 워크스페이스 테이블 3개 추가 |
<!-- ACTIVITY_LOG_END -->
```

#### D. 스프린트 계획 완료 보고

```
## Step 2 완료: 스프린트 계획 생성

### 생성된 파일
- docs/sprints/sprint-{N}-workspace/prompt-map.md (프롬프트 맵)
- docs/sprints/sprint-{N}-workspace/progress.md (프로그레스 트래커)

### 스프린트 구조
- Feature 1: 기반 인프라 (의존성, DB 스키마, 슬러그 유틸)
- Feature 2: 핵심 API (워크스페이스 CRUD, 멤버 관리, 전환, 소유권 이전)
- Feature 3: 초대 시스템 (이메일/링크 초대, 수락/거절/취소)
- Feature 4: 화면 구현 (6개 페이지 + 5개 컴포넌트)
- Feature 5: 기존 모듈 통합 (인증/결제 연동, 마이그레이션)

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

#### B. Feature 1: 기반 인프라 구현

레퍼런스 Phase 1에 해당하는 작업을 실행한다:

1. **의존성 설치** — `nanoid`, `slugify` (또는 대상 프레임워크 동등 패키지)
2. **환경 변수 템플릿** — `.env.example`에 워크스페이스 관련 환경 변수 추가
   - `WORKSPACE_DEFAULT_MAX_MEMBERS=5`
   - `WORKSPACE_INVITATION_EXPIRY_HOURS=168`
   - `WORKSPACE_INVITE_LINK_EXPIRY_HOURS=720`
   - `WORKSPACE_MAX_PER_USER=10`
   - SMTP 관련 변수 (초대 이메일 발송용)
3. **ORM 스키마 정의** — 레퍼런스의 Drizzle 스키마를 대상 ORM으로 변환
   - TB_COMM_WKSPC (워크스페이스 마스터)
   - TR_COMM_WKSPC_MBR (멤버십 매핑)
   - TB_COMM_WKSPC_INVT (초대 관리)
4. **DB 마이그레이션** — 마이그레이션 파일 생성 및 실행 + TB_COMM_USER.BSC_WKSPC_ID 추가
5. **검증 스키마** — Zod 또는 대상 프레임워크의 검증 라이브러리로 스키마 정의
6. **슬러그 생성 유틸** — 이름→슬러그 변환, 중복 시 자동 넘버링

구현 후 progress.md를 업데이트한다:
- 기반 인프라: Implementation → `Done`

#### C. Feature 2: 핵심 API 구현

레퍼런스 Phase 2에 해당하는 작업을 실행한다:

1. **워크스페이스 멤버십 미들웨어** — `requireWorkspaceRole()` 구현
   - 워크스페이스 존재 + 상태(ACTIVE) 확인
   - 멤버십 확인 (활성 멤버 여부)
   - 역할 확인 (OWNER/ADMIN/MEMBER/GUEST)
2. **워크스페이스 목록 API** — 내가 속한 워크스페이스 목록 + 역할 + 구독 정보
3. **워크스페이스 생성 API** — 슬러그 중복 검사, 소유 수 제한, OWNER 자동 등록
4. **워크스페이스 상세/수정 API** — 멤버십 미들웨어 적용
5. **워크스페이스 삭제 API** — Soft Delete, 전체 멤버 탈퇴, 대기 초대 취소, BSC_WKSPC_ID 재설정
6. **멤버 목록 API** — 워크스페이스 멤버 목록 + 역할/상태
7. **멤버 역할 변경 API** — 역할 계층 기반 권한 검증
8. **멤버 강제 퇴장 API** — 자기 자신 보호, 크레딧 만료 처리
9. **워크스페이스 탈퇴 API** — OWNER 탈퇴 불가, 크레딧 만료 처리
10. **워크스페이스 전환 API** — BSC_WKSPC_ID 업데이트
11. **소유권 이전 API** — 트랜잭션 내 역할 교환, 개인 WS 이전 불가
12. **WorkspaceContext** — currentWorkspace, switchWorkspace, isOwner/isAdmin 유틸

#### D. Feature 3: 초대 시스템 구현

레퍼런스 Phase 3에 해당하는 작업을 실행한다:

1. **초대 서비스** — 토큰 생성(nanoid), 이메일 발송, 만료 검증
2. **이메일 초대 API** — 복수 이메일, 멤버 수 제한, 중복 필터링, 이메일 발송
3. **초대 링크 생성 API** — MAX_USE_CNT, 만료 설정
4. **초대 정보 조회 API** — Public 접근, 수락 전 미리보기
5. **초대 수락 API** — 토큰/이메일 검증, 멤버 생성, USE_CNT 증가, 크레딧 할당(결제 모듈 있는 경우)
6. **초대 거절/취소 API**
7. **만료 초대 정리** — Cron Job 또는 스케줄러

#### E. Feature 4: 화면 구현

레퍼런스 Phase 4에 해당하는 화면을 구현한다:

1. **WorkspaceSwitcher** — 사이드바 드롭다운, 현재 WS 표시, 전환
2. **워크스페이스 생성 페이지** — 이름→슬러그 자동 변환, URL 미리보기
3. **워크스페이스 설정 페이지** — 일반 설정, 위험 영역(삭제)
4. **멤버 관리 페이지** — 멤버 목록, 역할 드롭다운, 퇴장 버튼, 대기 초대 목록, 초대 링크 관리
5. **초대 수락 페이지** — 워크스페이스 정보 미리보기, 수락/거절, 비로그인 시 로그인 유도
6. **멤버 초대 모달** — 이메일 입력(쉼표 구분), 역할 선택, 초대 링크 생성 탭

각 화면 구현 시 `src/styles/design-tokens.css`의 디자인 토큰과 `docs/design-system/`의 컴포넌트 패턴을 따른다.

#### F. Feature 5: 기존 모듈 통합

레퍼런스 Phase 5에 해당하는 작업을 실행한다:

1. **인증 모듈 연동: 회원가입** — POST /auth/signup 트랜잭션에 개인 WS 자동 생성 추가
   - TB_COMM_WKSPC 생성 (TYPE_CD='PERSONAL', MAX_MBR_CNT=1)
   - TR_COMM_WKSPC_MBR 생성 (ROLE_CD='OWNER')
   - TB_COMM_USER.BSC_WKSPC_ID 설정
2. **인증 모듈 연동: 회원 탈퇴** — DELETE /users/me에 워크스페이스 처리 추가
   - OWNER인 팀 WS가 있으면 탈퇴 거부 (소유권 이전 먼저)
   - 비-OWNER WS에서 멤버 탈퇴 처리
   - 크레딧 만료 처리 (결제 모듈 있는 경우)
   - 개인 WS Soft Delete
3. **인증 모듈 연동: JWT** — 토큰 페이로드에 ws_id 추가 (선택)
4. **결제 모듈 연동** — 구독 이벤트에 따른 MAX_MBR_CNT 업데이트 (있는 경우)
5. **사이드바 통합** — WorkspaceSwitcher를 기존 레이아웃에 삽입
6. **다국어 메시지** — 워크스페이스 관련 메시지 ko/en 추가
7. **기존 사용자 마이그레이션** — 개인 워크스페이스 일괄 생성 스크립트 (레퍼런스 부록 A)
8. **Rate Limiting** — 워크스페이스/초대 엔드포인트별 제한

#### G. 구현 완료 보고

```
## Step 3 완료: 구현

### 구현된 Feature
| Feature | 파일 수 | 상태 |
|---------|---------|------|
| 기반 인프라 | {N}개 | Done |
| 핵심 API (CRUD + 멤버) | {N}개 | Done |
| 초대 시스템 | {N}개 | Done |
| 화면 구현 | {N}개 | Done |
| 기존 모듈 통합 | {N}개 | Done |

Step 4로 진행합니다...
```

---

### Step 4: 테스트 시나리오 자동 생성

구현된 워크스페이스 모듈에 대해 종합적인 E2E 테스트 시나리오를 생성한다.

#### A. 테스트 시나리오 생성

`Agent` 도구를 사용하여 `/test-scenario workspace` 스킬과 동일한 방식으로 테스트 시나리오를 생성한다.

생성할 시나리오 파일:

1. `docs/tests/test-cases/sprint-{N}/workspace-e2e-scenarios.md` — 워크스페이스 CRUD E2E
2. `docs/tests/test-cases/sprint-{N}/member-mgmt-e2e-scenarios.md` — 멤버 관리 E2E
3. `docs/tests/test-cases/sprint-{N}/invitation-e2e-scenarios.md` — 초대 시스템 E2E
4. `docs/tests/test-cases/sprint-{N}/workspace-integration-e2e-scenarios.md` — 통합 E2E

#### B. 시나리오 그룹 구성

레퍼런스 설계 문서의 유즈케이스에 기반한 시나리오 그룹:

**워크스페이스 CRUD 시나리오**:
| 그룹 | 시나리오 유형 |
|------|------------|
| 워크스페이스 생성 | Happy: 팀 WS 생성 / Error: 슬러그 중복, 소유 수 초과 / Edge: 슬러그 특수문자 |
| 워크스페이스 수정 | Happy: 이름/설명 변경 / Error: 권한 없음 / Edge: 슬러그 변경 시 기존 URL |
| 워크스페이스 삭제 | Happy: Soft Delete / Error: 개인 WS 삭제 시도, 활성 구독 / Edge: 전체 멤버 BSC 재설정 |
| 워크스페이스 전환 | Happy: BSC_WKSPC_ID 변경 / Error: 비멤버 WS 전환 |
| 워크스페이스 목록 | Happy: 소속 WS 전체 조회 / Edge: 구독 정보 포함 |

**멤버 관리 시나리오**:
| 그룹 | 시나리오 유형 |
|------|------------|
| 멤버 목록 | Happy: 역할/상태별 조회 / Error: 비멤버 접근 |
| 역할 변경 | Happy: MEMBER→ADMIN / Error: ADMIN이 ADMIN 변경 시도, 자기 자신 / Edge: OWNER→ADMIN (소유권 이전과 구분) |
| 멤버 강제 퇴장 | Happy: MEMBER 퇴장 / Error: 자기 자신, OWNER 퇴장 / Edge: 크레딧 만료 |
| 워크스페이스 탈퇴 | Happy: MEMBER 자발 탈퇴 / Error: OWNER 탈퇴 시도 |
| 소유권 이전 | Happy: 정상 이전 / Error: 개인 WS, 비멤버 대상 / Edge: 재인증 요구 |

**초대 시스템 시나리오**:
| 그룹 | 시나리오 유형 |
|------|------------|
| 이메일 초대 | Happy: 복수 초대 / Error: 멤버 수 초과, 이미 멤버 / Edge: ADMIN이 ADMIN 초대 시도 |
| 초대 링크 | Happy: 링크 생성/공유 / Error: 사용 횟수 초과 / Edge: 만료 전 비활성화 |
| 초대 수락 | Happy: 이메일/링크 수락 / Error: 만료, 이메일 불일치 / Edge: 비로그인→로그인→수락 |
| 초대 거절/취소 | Happy: 정상 거절/취소 / Edge: 이미 수락된 초대 취소 |

**통합 시나리오**:
| 그룹 | 시나리오 유형 |
|------|------------|
| 회원가입→개인WS | Happy: 가입 시 자동 생성 / Edge: 슬러그 자동 넘버링 |
| 회원탈퇴→WS처리 | Happy: 비-OWNER 탈퇴 / Error: OWNER 탈퇴 거부 / Edge: 크레딧 만료 |
| 구독→멤버수 | Happy: 구독 시 MAX_MBR_CNT 업데이트 / Edge: 다운그레이드 시 현재>신규 |
| WS전환→메뉴 | Happy: 전환 시 사이드바 갱신 / Edge: 정지된 WS 전환 |

#### C. 시나리오 생성 완료 보고

```
## Step 4 완료: 테스트 시나리오 생성

### 생성된 파일
- docs/tests/test-cases/sprint-{N}/workspace-e2e-scenarios.md ({N}개 시나리오)
- docs/tests/test-cases/sprint-{N}/member-mgmt-e2e-scenarios.md ({N}개 시나리오)
- docs/tests/test-cases/sprint-{N}/invitation-e2e-scenarios.md ({N}개 시나리오)
- docs/tests/test-cases/sprint-{N}/workspace-integration-e2e-scenarios.md ({N}개 시나리오)

### 시나리오 통계
| Type | Workspace | Member | Invitation | Integration | Total |
|------|-----------|--------|------------|-------------|-------|
| Happy Path | {n} | {n} | {n} | {n} | {n} |
| Error Path | {n} | {n} | {n} | {n} | {n} |
| Edge Case | {n} | {n} | {n} | {n} | {n} |
| **Total** | **{n}** | **{n}** | **{n}** | **{n}** | **{n}** |

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
3. **API 테스트** — `curl` 또는 `fetch`로 워크스페이스 API 엔드포인트 테스트:
   - `GET /api/v1/workspaces` → 200 (내 워크스페이스 목록)
   - `POST /api/v1/workspaces` → 201 (팀 WS 생성)
   - `GET /api/v1/workspaces/[id]/members` → 200 (멤버 목록)
   - `POST /api/v1/workspaces/[id]/invitations` → 201 (이메일 초대)
   - `POST /api/v1/workspaces/[id]/invitations/link` → 201 (초대 링크)
   - `POST /api/v1/invitations/[token]/accept` → 200 (초대 수락)
   - `PATCH /api/v1/workspaces/[id]/switch` → 200 (WS 전환)
4. **UI 테스트** — Chrome MCP 사용 가능 시 (`/test-run` 스킬 위임):
   - 워크스페이스 생성 페이지 렌더링 확인
   - 멤버 관리 페이지 목록/역할 변경 확인
   - WorkspaceSwitcher 드롭다운 동작 확인
   - 초대 수락 페이지 렌더링 확인

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

테스트 결과를 `docs/tests/test-reports/sprint-{N}/workspace-test-report.md`에 기록한다:

```markdown
# 워크스페이스 모듈 테스트 리포트

## 실행 환경
- Date: {TIMESTAMP}
- Framework: {test-framework}
- Node/Java/Python: {version}

## 유닛/통합 테스트 결과
| Suite | Tests | Pass | Fail | Skip | Coverage |
|-------|-------|------|------|------|----------|
| workspace-infra | {n} | {n} | {n} | {n} | {n}% |
| workspace-api | {n} | {n} | {n} | {n} | {n}% |
| member-api | {n} | {n} | {n} | {n} | {n}% |
| invitation-api | {n} | {n} | {n} | {n} | {n}% |
| integration | {n} | {n} | {n} | {n} | {n}% |
| **Total** | **{n}** | **{n}** | **{n}** | **{n}** | **{n}%** |

## E2E 테스트 결과
| Scenario | Result | Notes |
|----------|--------|-------|
| 팀 WS 생성 | PASS/FAIL | {notes} |
| 멤버 초대 (이메일) | PASS/FAIL | {notes} |
| 초대 수락 | PASS/FAIL | {notes} |
| 소유권 이전 | PASS/FAIL | {notes} |
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

`docs/sprints/sprint-{N}-workspace/progress.md`의 모든 Feature 상태를 최종 업데이트한다.

#### B. 최종 결과 보고

```
## 워크스페이스 모듈 자동 구축 완료

### 파이프라인 실행 결과
| 단계 | 결과 | 산출물 |
|------|------|--------|
| 1. 블루프린트 | Done | docs/blueprints/{NNN}-workspace/blueprint.md |
| 2. 스프린트 계획 | Done | docs/sprints/sprint-{N}-workspace/prompt-map.md, progress.md |
| 3. 구현 | Done | {총 파일 수}개 파일 생성/수정 |
| 4. 테스트 시나리오 | Done | {총 시나리오 수}개 시나리오 |
| 5. 테스트/디버깅 | Done | Pass: {n}, Fail: {n}, Coverage: {n}% |

### 구현된 기능 요약
| 카테고리 | 기능 | API | 화면 | 테스트 |
|---------|------|-----|------|--------|
| 워크스페이스 | WS 생성 | POST /workspaces | /workspaces/new | {n}개 |
| 워크스페이스 | WS 목록/상세 | GET /workspaces, /workspaces/[id] | /workspaces | {n}개 |
| 워크스페이스 | WS 수정 | PATCH /workspaces/[id] | /workspaces/[slug]/settings | {n}개 |
| 워크스페이스 | WS 삭제 | DELETE /workspaces/[id] | - | {n}개 |
| 워크스페이스 | WS 전환 | PATCH /workspaces/[id]/switch | WorkspaceSwitcher | {n}개 |
| 멤버 | 멤버 관리 | GET/PATCH/DELETE members | /workspaces/[slug]/settings/members | {n}개 |
| 멤버 | 소유권 이전 | POST /transfer-ownership | - | {n}개 |
| 멤버 | WS 탈퇴 | POST /members/leave | - | {n}개 |
| 초대 | 이메일 초대 | POST /invitations | InviteMemberModal | {n}개 |
| 초대 | 초대 링크 | POST /invitations/link | - | {n}개 |
| 초대 | 초대 수락/거절 | POST /invitations/[token]/accept,decline | /invitations/[token] | {n}개 |
| 통합 | 회원가입→개인WS | (auth/signup 수정) | - | {n}개 |
| 통합 | 회원탈퇴→WS처리 | (users/me 수정) | - | {n}개 |

### 보안 체크리스트
- [ ] 멤버십 미들웨어로 모든 워크스페이스 API 보호
- [ ] 역할 계층 기반 접근 제어 (OWNER > ADMIN > MEMBER > GUEST)
- [ ] 자기 자신 보호 (역할 변경/퇴장 불가)
- [ ] 초대 토큰 nanoid(32) 사용 (충분한 엔트로피)
- [ ] 초대 만료 시간 적용 (이메일 7일, 링크 30일)
- [ ] WKSPC_ID 기반 데이터 격리
- [ ] 개인 워크스페이스 보호 (삭제/이전/멤버추가 불가)
- [ ] Rate Limiting 적용
- [ ] 소유권 이전 시 재인증 요구

### 다음 단계
1. `/test-run`으로 Chrome MCP 기반 UI 테스트 실행
2. 환경 변수 실제 값 설정 (SMTP, WS 제한값)
3. 결제 모듈 연동 검증 (있는 경우)
4. 기존 사용자 마이그레이션 실행 (프로덕션 데이터)
5. 프로덕션 배포 전 보안 검토
```

## Quick Run Examples

```
# 현재 프로젝트에 워크스페이스 모듈 구축
/workspace-module

# 특정 프로젝트 경로에 워크스페이스 모듈 구축
/workspace-module /path/to/my-project

# 인자로 프로젝트 경로 지정
/workspace-module ~/projects/my-app
```

## Notes

- 레퍼런스 설계 문서는 AMA 프로젝트 기준이며, 대상 프로젝트 기술 스택에 자동 적응됨
- **인증 모듈 의존**: TB_COMM_USER, JWT 인증이 필수. 인증 모듈이 없으면 먼저 구축 안내
- 결제 모듈 연동은 대상 프로젝트에 결제 모듈이 있는 경우에만 적용
- 기존 워크스페이스 코드가 있는 경우 덮어쓰지 않고 통합/확장 방식으로 처리
- 모든 DB 컬럼명은 공공 데이터 표준 네이밍 규칙을 따름
- 디버깅 자동화는 최대 5회까지 시도하며, 이후 사용자에게 도움 요청
- 개인 워크스페이스는 삭제/이전/멤버추가 불가 (보호 규칙)
- 초대 이메일 발송은 SMTP 설정이 필수 (없으면 로그 출력으로 대체)
