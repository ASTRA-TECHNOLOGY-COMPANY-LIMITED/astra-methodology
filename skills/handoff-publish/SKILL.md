---
name: handoff-publish
description: "UX/UI/Dev/QA 협업을 위한 Handoff 패키지(브랜치 루트 `{feature}-handoff/`)를 생성합니다. Screen ID 4-segment 체계(DOMAIN-PAGE-SECTION-UC)로 화면을 식별하고, SSoT인 1-screen-registry.md를 중심으로 11개 문서(상태 매트릭스, 엣지 케이스, 반응형, 컴포넌트 명세, 비즈니스 규칙, UX writing, IA/사이트맵, 페르소나, Decision log)를 구성합니다. service-planner 산출물이 있으면 자동으로 변환/활용합니다."
argument-hint: "[feature-name 또는 기획 디렉토리명]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Skill
---

# ASTRA Handoff 패키지 자동 생성

HANDOFF_PROCESS_GUIDE v1.1 기반의 **Screen ID 중심 협업 패키지**를 생성합니다.

**핵심 원칙 (PDF §6)**:
- **Screen ID 기반 협업**: 모든 화면은 `DOMAIN-PAGE-SECTION-UC{NN}` 형식의 고유 ID로 식별
- **Single Source of Truth (SSoT)**: `1-screen-registry.md`가 모든 ID의 유일한 기준 (UX만 발행 권한)
- **상태 기반 설계**: 모든 화면은 상태(State) × 권한(Permission) × 디바이스(Device) 조합으로 정의

**생성 위치**: 브랜치 루트의 `{feature}-handoff/` 폴더 (PDF §8 구조 그대로)

**출력물 (14개 파일 + screenshots/)**:

| # | 파일 | 역할 |
|---|------|------|
| 0 | `0-README.md` | 이 가이드 + Quick Start |
| 1 | `1-screen-registry.md` | **SSoT** — 화면 등록부 |
| 2 | `2-flows.md` | 사용자 흐름 (Flow) 정의 |
| 3 | `3-state-matrix.md` | 상태 × 권한 매트릭스 |
| 4 | `4-edge-cases.md` | 예외/주의 케이스 |
| 5 | `5-responsive-guide.md` | 반응형 기준 |
| 6 | `6-component-specs.md` | 카드/컴포넌트 명세 (data anatomy) |
| 7 | `7-business-rules.md` | 화면별 비즈니스 규칙 / 노출 정책 |
| 8 | `8-content-guide.md` | UX Writing + 데이터 표시 규칙 |
| 9 | `9-ia-sitemap.md` | 정보 구조 / 사이트맵 |
| 10 | `10-personas.md` | 페르소나 / 핵심 시나리오 |
| 11 | `11-decision-log.md` | 디자인 결정 이력 |
| — | `DoD-CHECKLIST.md` | 역할별 Definition of Done 체크리스트 |
| — | `walkthrough.loom.md` | 설명 영상 링크 (수동 기록) |
| — | `screenshots/` | 화면 ID 기준 캡처 디렉토리 |

> **LANGUAGE RULE**: Before executing this skill, read the project's `CLAUDE.md` and check the `## Language` section to detect the project language. If the project language is NOT Korean (`ko`), translate ALL user-facing output — prompts, messages, generated headers, table labels, descriptions — into the project language. Technical identifiers (Screen IDs, file names, code snippets) remain untranslated.

---

## Out of Scope (PDF §24 — 본 프로세스를 적용하지 않는 경우)

다음의 경우 Handoff 프로세스를 적용하지 **않는다**. Step 0 초반에 사용자에게 명시적으로 확인한다:

- 1회성 마케팅/이벤트 페이지
- 빠른 프로토타입/A-B 테스트용 화면
- 외부 임베드 페이지 (Notion/Slack 임베드 등)
- 백오피스 어드민 화면 (UX 협업 불필요한 경우)

해당 사례에 해당하면 이 스킬을 조기 종료하고, 대신 단순한 블루프린트(`/feature-dev`) 또는 바로 구현을 권장한다.

또한 **기존 기능에는 자동 적용하지 않는다** (PDF §26). 큰 리뉴얼 시점에만 점진 적용한다.

---

## 실행 절차

### Step 0: Out of Scope 확인

`AskUserQuestion`으로 아래를 확인한다. 하나라도 해당되면 스킬을 조기 종료한다:

```
## Handoff 적용 범위 확인

본 Handoff 프로세스는 제품의 핵심 화면(여러 역할이 협업하는 장기 유지 화면)에만 적용합니다.
다음 중 하나에 해당하나요?

1. 1회성 마케팅/이벤트 페이지
2. 빠른 프로토타입/A-B 테스트용
3. 외부 임베드 페이지
4. 백오피스 어드민 (UX 협업 불필요)
5. 위 항목 해당 없음 (정상 진행)
```

1~4 선택 시:
```
Handoff 프로세스는 해당 화면에 적용하지 않습니다.
대신 아래 워크플로우를 권장합니다:
- 빠른 개발: /feature-dev "{feature-description}"
- 블루프린트만 생성: docs/blueprints/{NNN}-{feature}/blueprint.md 직접 작성
종료합니다.
```
→ 스킬 종료.

5 선택 시 Step 1로 진행한다.

---

### Step 1: 인자 파싱 및 Feature 컨텍스트 수집

#### A. `$ARGUMENTS` 분석

| 인자 형태 | 동작 |
|-----------|------|
| 기획 디렉토리명 (예: `001-auth`) | `docs/planner/{디렉토리}/` 와 `docs/blueprints/{디렉토리}/` 를 컨텍스트로 사용 |
| feature-name kebab-case (예: `expert-qa`) | 해당 feature를 주제로 설정, 기획 디렉토리 탐색 |
| 없음 | `docs/planner/` 스캔 후 `AskUserQuestion`으로 선택 |

선택된 feature-name을 `{FEATURE_NAME}`으로 저장한다.

#### B. Domain Code 결정

Screen ID의 첫 segment(`DOMAIN`)는 **프로덕트 약어**다. 예:
- FECT Academy → `ACAD`
- FECTQ → `FECTQ`
- AMA 결제 → `PAY`

`CLAUDE.md`에서 프로젝트명/도메인을 읽고 후보를 제시한 뒤, `AskUserQuestion`으로 `{DOMAIN_CODE}` (2~6자 대문자)를 확정한다. 이 도메인 코드는 향후 모든 화면 ID에 일관되게 사용된다.

> 기존 Handoff 패키지가 있으면 해당 폴더의 `1-screen-registry.md`에서 DOMAIN을 자동 추출한다.

#### C. 기존 산출물 로드 (있으면 활용, 없으면 스캐폴드)

다음 파일이 있으면 읽어서 Handoff 파일에 반영한다:

| 소스 | 매핑 대상 |
|------|-----------|
| `docs/planner/{NNN}-{feature}/ia-screen-design.md` | `1-screen-registry.md`, `9-ia-sitemap.md`, `2-flows.md` |
| `docs/planner/{NNN}-{feature}/interview-report.md` | `10-personas.md` |
| `docs/planner/{NNN}-{feature}/requirements-definition.md` | `7-business-rules.md`의 노출 정책 초안 |
| `docs/planner/{NNN}-{feature}/feature-definition.md` | `7-business-rules.md`, `3-state-matrix.md`의 권한 매트릭스 |
| `docs/blueprints/{NNN}-{feature}/blueprint.md` | `7-business-rules.md`의 API/데이터 정책 |
| `docs/design-system/components.md` | `6-component-specs.md` (글로벌 컴포넌트는 참조 링크만) |

> 모두 없으면 빈 스캐폴드를 생성하고 UX/PM이 채우도록 TODO 주석을 남긴다. 이 경우 Step 5~10의 AI 자동 채움은 생략된다.

#### D. 출력 디렉토리 결정

기본값: 브랜치 루트의 `{FEATURE_NAME}-handoff/` (예: `fect-academy-handoff/`)

이미 존재하면 `AskUserQuestion`:
- 기존 유지 + 업데이트 (기본)
- 삭제 후 재생성
- 중단

`{HANDOFF_DIR}`을 확정한다.

#### E. dev 브랜치 전환 및 최신화

산출물 파일을 생성하기 전에, `dev` 브랜치로 전환하고 최신 상태로 동기화한다. 작업 브랜치는 생성하지 않으며, `dev`에서 직접 작업한다. 작업 브랜치 생성은 `/pr-merge` 실행 시 자동으로 처리된다.

0. **메인 worktree 가드**: 격리 worktree(`.astra-worktrees/<slug>/`) 안에서 호출된 경우 중단한다. dev-sync는 메인 worktree에서만 실행한다:
   ```bash
   source "$CLAUDE_PLUGIN_ROOT/scripts/worktree-helpers.sh"
   astra_ensure_main_worktree || exit 1
   ```
1. **현재 브랜치 확인**: `git branch --show-current`
2. **이미 `dev` 브랜치인 경우 스킵**: 현재 브랜치가 `dev`이면 아래 3~5단계를 건너뛰고 pull만 실행한다 (`git pull origin dev`)
3. **미커밋 변경사항 보존**: `git status --porcelain`으로 확인하여 변경사항이 있으면 `git stash --include-untracked`로 임시 저장한다 (untracked 파일도 포함)
4. **dev 브랜치 전환 및 최신화**: `git fetch origin dev && git checkout dev && git pull origin dev`
5. **stash 복원**: step 3에서 stash 했으면 `git stash pop`으로 복원한다. 충돌 발생 시 충돌 파일 목록을 사용자에게 보고하고 수동 해결을 요청한다.

> **참고**: `dev` 브랜치가 존재하지 않으면 `main` 또는 `master` 브랜치에서 작업한다. 어떤 기본 브랜치도 없으면 현재 브랜치에서 작업한다.

---

### Step 2: Screen ID 발번 체계 설계

#### A. Screen ID 포맷 (PDF §6.1)

```
{DOMAIN}-{PAGE}-{SECTION}-UC{NN}
────   ─────   ───────   ────
도메인  페이지   섹션       유즈케이스 번호 (2자리)

예시: ACAD-EXPERT-DETAIL-UC03
      ACAD-EXPERT-LIST
      ACAD-EXPERT-LIST-EMPTY
      ACAD-EXPERT-MODAL01
```

세부 규칙:
- `DOMAIN`: 프로덕트 약어 (Step 1-B에서 결정)
- `PAGE`: 메뉴/라우트 단위 (대문자 영문, 필요시 하이픈 허용)
- `SECTION`: LIST / DETAIL / FORM / MODAL / DASHBOARD / SETTINGS 등 화면 유형. 없으면 생략 가능
- `UC{NN}`: 같은 페이지의 **상태/케이스 구분** (예: UC01=기본, UC02=채택 전, UC03=채택 완료)
- 상태 suffix: `-LOADING`, `-EMPTY`, `-ERROR`는 UC 대신 직접 접미사로 표기 가능

#### B. 기존 SCR-NNN 변환 규칙

`docs/planner/.../ia-screen-design.md`에 `SCR-001` 형식이 있으면 다음 규칙으로 변환한다:

1. 해당 화면의 `관련 UC`, `유형`, `화면명` 컬럼을 읽는다
2. PAGE = 라우트 또는 주요 기능 키워드 (예: `전문가 Q&A 목록` → `EXPERT-LIST`)
3. SECTION = 유형 매핑 (목록→LIST, 상세→DETAIL, 폼→WRITE, 모달→MODAL)
4. UC{NN} = `관련 UC` 번호를 2자리 zero-pad (UC-1 → UC01)
5. **변환 후 신/구 매핑 표를 `11-decision-log.md` 첫 엔트리에 기록**

예: `SCR-005` (질문 상세, 채택 완료, UC-3) → `ACAD-EXPERT-DETAIL-UC03`

#### C. 필수 포함 화면 (PDF §9.2)

등록부에 반드시 포함시켜야 할 최소 화면:

- 기본 화면 (DEFAULT)
- 모든 상태 (LOADING / EMPTY / DEFAULT / ERROR) — State Matrix 전개
- 모든 모달 (Confirm / Form / Error 포함)
- Edge case 화면
- URL 파라미터로만 진입하는 숨은 화면

기획 문서의 화면 목록이 위를 커버하지 않으면 사용자에게 경고한다:

```
⚠️ 다음 화면이 기획 문서에 누락되어 있습니다:
- {SCREEN-ID}-LOADING (로딩 상태)
- {SCREEN-ID}-EMPTY (빈 상태)
- {SCREEN-ID}-ERROR (에러 상태)

Registry에 플레이스홀더로 추가하고 "🔄 미착수"로 표기합니다.
진행할까요? (예/아니오)
```

---

### Step 3: 템플릿 복사 및 변수 치환

`$CLAUDE_PLUGIN_ROOT/skills/handoff-publish/templates/` 의 모든 파일(14개 템플릿)을 `{HANDOFF_DIR}`에 복사하고, 다음 변수를 치환한다:

> 복사 대상: `0-README.md` (1개), `1-screen-registry.md` ~ `11-decision-log.md` (11개), `DoD-CHECKLIST.md`, `walkthrough.loom.md`

| 변수 | 값 |
|------|-----|
| `{{FEATURE_NAME}}` | Step 1의 feature-name |
| `{{DOMAIN_CODE}}` | Step 1-B의 domain code |
| `{{TODAY}}` | 오늘 날짜 (YYYY-MM-DD) |
| `{{OWNER}}` | 프로젝트 UX Lead (CLAUDE.md 또는 `AskUserQuestion`으로 수집) |
| `{{PROJECT_NAME}}` | CLAUDE.md의 프로젝트명 |
| `{{LANGUAGE_POLICY}}` | 프로젝트 i18n 언어 목록 (기본: `ko / en / vi`) |

또한 `screenshots/` 빈 디렉토리를 생성한다 (`walkthrough.loom.md`는 이미 템플릿으로 복사됨).

---

### Step 4: 1-screen-registry.md 자동 채움

Step 1-C에서 로드한 기획 산출물이 있으면, `ia-screen-design.md`의 화면 목록을 Screen Registry 테이블 형식으로 변환한다.

| 기획 컬럼 | Registry 컬럼 |
|-----------|--------------|
| 화면ID (SCR-NNN) | ID (변환된 4-segment) |
| 화면명 | 화면명 |
| 유형 | 상태/케이스 (기본 / 채택 전 / 답변 없음 등) |
| 설명 | 트리거 (원인/진입 경로) |
| — | 디자인 상태 (초기: 🔄 미착수) |

기획 문서가 없으면 PDF §9.1 예시 4행 (LIST, LIST-EMPTY, LIST-LOADING, DETAIL-UC01)만 플레이스홀더로 남긴다.

---

### Step 5: 2-flows.md 자동 채움

`usecase-definition.md`의 여정맵/Mermaid가 있으면 PDF §10 예시 형식의 트리 포맷으로 변환한다:

```
[{시나리오명} Flow]

{SCREEN-ID}
    └ "{액션}" 클릭
        ├ ({조건}) → {SCREEN-ID}
        └ ({조건}) → {SCREEN-ID}
            └ "{액션}" 클릭
                ├ (성공)    → {SCREEN-ID}
                ├ (토큰 부족) → {SCREEN-ID}
                └ (네트워크 에러) → {SCREEN-ID}
```

모든 버튼 클릭/제출의 **성공/실패/예외 분기**를 ID로 매핑한다. 누락된 분기가 발견되면 `11-decision-log.md` 에 기록하고 Registry에도 placeholder ID를 추가한다.

---

### Step 6: 3-state-matrix.md, 4-edge-cases.md 자동 채움

**3-state-matrix.md**: 상태 정의(LOADING/EMPTY/DEFAULT/ERROR/PARTIAL)는 템플릿 그대로 유지. 권한 매트릭스 섹션은 `feature-definition.md`의 `액터별 권한` 표가 있으면 자동 변환, 없으면 6열 표 헤더만 남긴다 (비로그인 / 일반 사용자 / 작성자 본인 / 답변자 / 관리자 + 기능 열).

**4-edge-cases.md**: PDF §13의 8개 기본 항목을 체크박스로 삽입. feature-definition.md의 리스크 섹션이 있으면 추가 항목으로 확장한다.

---

### Step 7: 5-responsive-guide.md 자동 채움

PDF §12 그대로. Desktop (≥1024) / Tablet (768~1023) / Mobile (<768) 분기점 + ID 표기 컨벤션(`-T`, `-M` suffix)만 유지. 프로젝트의 `src/styles/design-tokens.css`에 breakpoint가 정의되어 있으면 해당 값으로 오버라이드한다.

---

### Step 8: 6-component-specs.md 자동 채움

`docs/design-system/components.md`가 있으면 각 글로벌 컴포넌트를 참조 링크로 인용한다. Feature 고유 컴포넌트는 `feature-definition.md`의 UI 요소 섹션을 읽어 PDF §14.1 형식(props / variants / 사용처)으로 자동 생성한다. 카드류(CourseCard, QuestionCard, InsightCard, NoticeCard) + Modal(Confirm/Form/Error) 최소 4개는 틀만이라도 포함.

---

### Step 9: 7-business-rules.md 자동 채움

각 Registry ID에 대해 PDF §15.1 형식(노출 정책 / 사용 컴포넌트 / 권한별 분기 / 데이터 없을 때 / 데이터 소스 + 캐싱)의 빈 블록을 생성한다. `blueprint.md`의 API 엔드포인트가 있으면 `데이터 소스` 행을 자동 채움한다.

---

### Step 10: 8-content-guide.md 자동 채움

PDF §16~17의 전체 내용을 템플릿으로 그대로 반영:
- 브랜드 보이스 (톤/호칭/금지 표현)
- 마이크로카피 룰 (버튼/에러/Empty/모달)
- 데이터 표시 규칙 (이미지/날짜/숫자/텍스트 자르기)
- i18n 3개국어 정책 (ko/en/vi, 베트남어 1.4배 길이 가정)

프로젝트에 지정된 언어가 다르면 Step 3의 `{{LANGUAGE_POLICY}}`로 치환.

---

### Step 11: 9-ia-sitemap.md, 10-personas.md, 11-decision-log.md 자동 채움

- **9-ia-sitemap.md**: `ia-screen-design.md`의 메뉴 트리가 있으면 PDF §3 형식의 ASCII 트리로 재구성. URL 컨벤션 및 depth 정책(최대 3 depth 권장)은 템플릿 그대로.
- **10-personas.md**: `interview-report.md`의 페르소나 Top 3~5를 PDF §4 형식(목표/페인포인트/사용 맥락/디바이스)으로 정리. Top 5~10 핵심 시나리오도 추출.
- **11-decision-log.md**: Step 2-B의 SCR-NNN → 4-segment ID 변환 내역을 첫 엔트리로 기록. 이후 변경 시마다 UX가 직접 추가.

---

### Step 12: 0-README.md 변수 치환 확인

- **0-README.md**: 템플릿 그대로 (PDF §7 Quick Start + 역할별 5분 가이드). Step 3의 `{{FEATURE_NAME}}`/`{{DOMAIN_CODE}}` 치환이 정상 반영되었는지만 확인한다.
- **walkthrough.loom.md**: Step 3에서 템플릿으로 이미 복사되었으므로 별도 생성 불필요. UX가 녹화 후 Loom URL을 수동으로 추가한다.
- **DoD-CHECKLIST.md**: Step 3에서 템플릿으로 이미 복사되었으며, 역할별(UX/UI/Dev/QA) 체크리스트 포맷 그대로 유지한다.

---

### Step 13: 사용자에게 생성 결과 보고

다음 포맷으로 보고한다:

```
✅ Handoff 패키지 생성 완료

위치: {HANDOFF_DIR}
도메인 코드: {DOMAIN_CODE}
등록된 Screen ID: {N}개

생성된 파일:
  0-README.md
  1-screen-registry.md ({N}개 ID 등록)
  2-flows.md ({N}개 Flow 정의)
  3-state-matrix.md
  4-edge-cases.md
  5-responsive-guide.md
  6-component-specs.md ({N}개 컴포넌트)
  7-business-rules.md
  8-content-guide.md
  9-ia-sitemap.md
  10-personas.md ({N}개 페르소나)
  11-decision-log.md (변환 이력 {N}건)
  DoD-CHECKLIST.md
  walkthrough.loom.md
  screenshots/

⚠️ 자동 채움이 제한적인 섹션 (UX가 직접 보완 필요):
  - 1-screen-registry.md: 상태/트리거 정합성 검토
  - 3-state-matrix.md: 권한 매트릭스 (기능별)
  - 6-component-specs.md: feature 고유 컴포넌트 props
  - 10-personas.md: 실제 인터뷰 기반 보정

다음 단계 (PDF §7 Quick Start):
  1. UX: 1-screen-registry.md의 모든 ID 검증 및 결측 보완
  2. UI: Figma 프레임명을 Screen ID 형식으로 작성
  3. Dev: 컴포넌트에 `// @feature: {SCREEN-ID}` 주석 추가
  4. UX: Loom 워크스루 녹화 (5-10분)

DoD 체크는 PDF §19 참조. 향후 /check-dod 커맨드 예정.
```

---

## Anti-patterns (PDF §23)

이 스킬이 방지하려는 10가지 문제:

1. 모달/에러 화면 누락 → Registry에 모달 ID 등록
2. 상태별 UI 미정의 → State Matrix 의무화
3. Mobile 디자인 누락 → Responsive Guide 의무화
4. 권한별 UI 차이 미반영 → 권한 매트릭스 의무화
5. Figma/코드 ID 따로 생성 → SSoT (Registry) + UX만 발행 권한
6. 변경이 한쪽만 반영 → Decision Log + 변경 관리 프로세스
7. 카드 데이터 항목 제각각 → 6-component-specs.md 의무화
8. 노출 조건 임의 결정 → 7-business-rules.md 의무화
9. 베트남어 잘림 → 1.4배 길이 가정
10. 접근성 미준수 → Accessibility 가이드 + DoD

---

## 주의 사항

- **Registry 없는 ID 임의 생성 금지** (PDF §20): UI/Dev가 발견 시 UX에 추가 요청
- **화면 ID 발행은 UX 단독 권한**: 이 스킬 외에는 `1-screen-registry.md`를 직접 수정하지 말 것 (향후 `/register-screen` 커맨드로 강제 예정)
- **기존 기능 소급 적용 금지**: 새 기능 또는 큰 리뉴얼 시점에만 적용 (PDF §26)
