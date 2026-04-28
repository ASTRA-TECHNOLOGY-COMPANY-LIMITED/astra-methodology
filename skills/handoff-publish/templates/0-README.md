# {{PROJECT_NAME}} — {{FEATURE_NAME}} Handoff 패키지

**작성일**: {{TODAY}}
**Owner**: {{OWNER}} (UX Lead)
**적용 범위**: {{PROJECT_NAME}}, 향후 모든 신규 기능 개발
**도메인 코드**: `{{DOMAIN_CODE}}`

> **TL;DR** — 모든 화면을 Screen ID로 정의 → 같은 이름으로 부른다 — `1-screen-registry.md` 가 ID의 유일한 기준 (Single Source of Truth) — 화면이 아니라 **"케이스(상태/권한/반응형)"** 를 정의한다 — 화면 정의 + 협업 정책 + 운영 규칙을 Handoff 패키지로 통합 전달

---

## 🎯 목적

UX → UI → 개발 → QA 가 동일한 기준으로 협업할 수 있는 효율적인 업무 프로세스를 정의합니다.

**지향점**:
- 팀 간 **공통 언어**를 통해 빠르고 정확한 커뮤니케이션
- **누구든 참여해도 같은 결과**가 나오는 표준화된 워크플로우
- 변경 사항이 **자동으로 추적·공유**되는 일관된 작업 환경
- Claude Code 등 AI 도구를 **공통 컨텍스트**로 활용 가능한 구조

---

## 👥 역할과 책임 (RACI)

| 작업 | UX | UI 디자이너 | 개발자 | QA |
|------|------|------|------|------|
| Screen ID 발행 | ✅ Owner | Consulted | Informed | Informed |
| Handoff 패키지 작성 | ✅ Owner | Consulted | Informed | Informed |
| Figma 프레임 작성 | Consulted | ✅ Owner | Informed | Informed |
| 코드 구현 | Consulted | Consulted | ✅ Owner | Informed |
| ID 변경/추가 결정 | ✅ Owner | Notified | Notified | Notified |
| 검증/누락 체크 | Reviewer | Reviewer | Reviewer | ✅ Owner |

**룰**: 다른 역할이 ID를 신규 발행하면 무효. 반드시 UX가 Screen Registry (`1-screen-registry.md`) 에 등록 후 사용.

---

## 🧠 핵심 원칙 3가지

### 1. Screen ID 기반 협업

모든 화면은 고유 ID로 식별합니다.

```
{{DOMAIN_CODE}}-EXPERT-DETAIL-UC03
─────────     ──────   ──────   ────
도메인         페이지   섹션     유즈케이스
```

→ 동일 화면을 서로 다른 이름으로 부르는 문제 방지 → 디자인 / 개발 / QA / Claude Code 모두 같은 기준 사용

### 2. Single Source of Truth (SSoT)

```
1-screen-registry.md = 모든 화면 ID의 유일한 기준 (Screen Registry / 화면 등록부)
```

⚠️ **반드시 준수**: 모든 ID는 이 문서에서 생성 — Figma는 이 문서를 따른다 — 코드도 이 문서를 따른다 — Figma/코드에서 임의로 ID 생성 **금지**

> 💡 **"Registry에 등록한다"의 의미**: `1-screen-registry.md` 파일의 표에 새 행을 추가하고 커밋하는 행위입니다. 예) 디자이너가 새 화면이 필요 → UX에 요청 → UX가 표에 한 줄 추가 → 그 후에 디자이너가 Figma 작업 시작.

### 3. 상태 기반 설계

모든 화면은 정적 화면이 아니라 **상태(State) × 권한(Permission) × 디바이스(Device)** 의 조합으로 정의합니다.

---

## 🚀 Quick Start — 역할별 5분 가이드

### 🎨 UI 디자이너

```
1. git pull → {{FEATURE_NAME}}-handoff/ 폴더 확인
2. 1-screen-registry.md 에서 작업할 ID 선택
3. 3-state-matrix.md 에서 해당 화면의 상태/권한 확인
4. 5-responsive-guide.md 에서 반응형 정의 확인
5. 7-business-rules.md 에서 노출 정책 / 데이터 매핑 확인
6. 6-component-specs.md 에서 사용할 카드/컴포넌트 명세 확인
7. Figma 프레임명 = Screen ID 형식으로 작성
   예: "{{DOMAIN_CODE}}-EXPERT-DETAIL-UC03 / 질문 상세 / 채택 완료"
8. 작업 완료 → PR 또는 Figma 링크 공유
```

### 💻 개발자

```
1. {{FEATURE_NAME}}-handoff/ 폴더에서 ID 확인
2. 컴포넌트/페이지에 ID 주석 추가
   // @feature: {{DOMAIN_CODE}}-EXPERT-DETAIL-UC03
3. Figma에서 같은 ID 프레임 찾기
4. 7-business-rules.md 에서 데이터 정책 확인
5. 8-content-guide.md 에서 카피/i18n 키 확인
6. ID 누락이나 모순 발견 시 UX에 즉시 컨택
```

### 🤖 Claude Code 활용

```
디자이너: "Figma의 {{DOMAIN_CODE}}-* 프레임과 1-screen-registry.md를 비교해서
           디자인 빠진 ID 알려줘"

개발자:   "{{DOMAIN_CODE}}-EXPERT-DETAIL-UC03 구현해줘.
           디자인은 Figma 같은 ID 프레임 참조,
           비즈니스 룰은 7-business-rules.md 참조"

UX:       "1-screen-registry.md 와 코드의 @feature 주석을 비교해서
           ID 동기화 안 된 부분 찾아줘"
```

→ 같은 ID로 컨텍스트 전달 → AI가 누락 자동 검출

---

## 📂 패키지 구조

```
{{FEATURE_NAME}}-handoff/
├── 0-README.md              (이 파일 — 가이드 + Quick Start)
├── 1-screen-registry.md     (Screen Registry / 화면 등록부 — SSoT)
├── 2-flows.md               (사용자 흐름)
├── 3-state-matrix.md        (상태 + 권한 정의)
├── 4-edge-cases.md          (예외/주의 케이스)
├── 5-responsive-guide.md    (반응형 기준)
├── 6-component-specs.md     (카드/컴포넌트 명세 + 데이터 anatomy)
├── 7-business-rules.md      (화면별 비즈니스 규칙 / 노출 정책)
├── 8-content-guide.md       (UX Writing + 데이터 표시 규칙)
├── 9-ia-sitemap.md          (정보 구조 / 사이트맵)
├── 10-personas.md           (페르소나 / 핵심 시나리오)
├── 11-decision-log.md       (디자인 결정 이력)
├── screenshots/             (화면 ID 기준 캡처)
│   ├── {{DOMAIN_CODE}}-EXPERT-LIST.png
│   └── {{DOMAIN_CODE}}-EXPERT-DETAIL-UC03.png
└── walkthrough.loom.md      (설명 영상 링크)
```

---

## ✅ 핵심 요약

1. 화면이 아니라 **"케이스"** 를 정의한다
2. **ID** 를 기준으로 협업한다 (UX 단독 발행)
3. **Screen Registry** (`1-screen-registry.md`) 가 모든 것의 기준이다 (SSoT)
4. **Business Rules + Component Specs** 로 무엇을 어떻게 보여줄지 명시
5. **Content Guide + i18n + a11y** 로 일관성 / 다국어 / 접근성 확보
6. **Definition of Done** 으로 각 단계의 완료 기준 통일
7. **Decision Log** 로 의사결정 이력 보존
8. **Claude Code** 와 같은 ID로 대화한다

---

> 💬 "디자인을 만드는 게 아니라, 제품의 동작을 정의하는 것이 UX의 역할이다."

**문서 버전**: v1.1 | **기준 가이드**: HANDOFF_PROCESS_GUIDE (FECT Academy UX Lead Joy)
