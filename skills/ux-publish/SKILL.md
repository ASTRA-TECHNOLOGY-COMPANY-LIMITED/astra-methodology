---
name: ux-publish
description: "기획 산출물(service-planner)의 IA/화면설계서와 기능정의서를 기반으로 프로덕션 수준의 UX 프로토타입을 HTML로 퍼블리싱합니다. /frontend-design 스킬로 세련된 디자인을 적용하고, fect-image로 AI 생성 이미지 에셋을 포함하며, UX 인터랙션 패턴 가이드를 기반으로 화면별 맞춤 인터랙션을 구현합니다. 프로젝트의 디자인 시스템과 공통 컴포넌트를 사용하여 ux/ 디렉토리 하위에 반응형 HTML 페이지를 생성합니다."
argument-hint: "[기획 디렉토리명 또는 기능 설명]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Agent, Skill, mcp__fect-image__image_text2img
---

# ASTRA UX 프로토타입 퍼블리싱

기획 산출물(`/service-planner`)의 IA/화면설계서(`ia-screen-design.md`)와 기능정의서(`feature-definition.md`)를 분석하여, **프로덕션 수준의 세련된 디자인**을 적용한 인터랙티브 HTML 프로토타입을 `ux/` 디렉토리에 생성합니다.

**핵심 원칙**:
- **`/frontend-design` 스킬 연동** — 개성 있고 세련된 프로덕션급 UI 디자인 (AI 슬롭 방지)
- **`fect-image` MCP 도구 활용** — 히어로 이미지, 빈 상태 일러스트, 배경 등 AI 생성 이미지 에셋
- **`ux-interaction-patterns.md` 기반 인터랙션** — 화면 유형별 맞춤 마이크로 인터랙션, 전환 효과, 폼 패턴
- 프로젝트의 `src/styles/design-tokens.css`를 반드시 참조 (하드코딩 금지)
- `docs/design-system/components.md`의 컴포넌트 스펙을 준수
- `docs/design-system/layout-grid.md`의 레이아웃 시스템을 적용
- 반응형 (모바일/태블릿/데스크톱) 지원
- 다크 모드 지원
- 브라우저에서 바로 열어 확인 가능 (별도 빌드 불필요)

**생성물 위치**: `ux/{feature-name}/`

**디자인 품질 기준**:
- 단순한 와이어프레임 변환이 아닌, 실제 서비스처럼 보이는 프로덕션급 퍼블리싱
- 대담한 미학적 방향성 선택 (미니멀, 에디토리얼, 럭셔리, 플레이풀 등)
- 의도적인 타이포그래피, 색상 구성, 공간 배치, 모션 디자인
- 화면 유형에 최적화된 UX 인터랙션 패턴 적용

> **🌐 LANGUAGE RULE**: Before executing this skill, read the project's `CLAUDE.md` and check the `## Language` section to detect the project language. If the project language is NOT Korean (`ko`), you MUST translate ALL user-facing output — including HTML page titles, labels, placeholder text, navigation text — into the project language. Technical identifiers (file paths, CSS variable names, class names) remain untranslated. If no `CLAUDE.md` exists or no `## Language` section is found, default to Korean.

## 실행 절차

### Step 0: 사전 준비 및 컨텍스트 수집

#### A. 인자 파싱

`$ARGUMENTS`를 확인한다:

| 인자 형태 | 동작 |
|-----------|------|
| 기획 디렉토리명 (예: `001-auth`, `002-payment`) | 해당 디렉토리의 기획 산출물을 사용 |
| 기능 설명 문자열 (예: `인증 기능`) | 기능명으로 기획 산출물 디렉토리를 검색 |
| _(없음)_ | `docs/planner/` 하위 디렉토리를 스캔하여 사용자에게 선택 요청 |

인자가 없으면 `docs/planner/` 하위 디렉토리를 스캔하고 `AskUserQuestion`으로 선택을 요청한다:

```
## UX 프로토타입 생성

기획 산출물이 있는 디렉토리를 선택하세요.

| # | 디렉토리 | 기능 |
|---|---------|------|
| 1 | {NNN}-{feature-name} | {ia-screen-design.md 내 기능 설명} |
| 2 | {NNN}-{feature-name} | {ia-screen-design.md 내 기능 설명} |

선택할 번호 (콤마로 복수 선택 가능):
```

선택된 기획 디렉토리를 `{PLANNER_DIR}`로 저장한다.

#### B. 기획 산출물 로드

`{PLANNER_DIR}` 에서 다음 파일을 읽는다:

1. **`ia-screen-design.md`** (필수) — IA 구조, 화면 흐름도, 화면 목록, 와이어프레임
2. **`feature-definition.md`** (필수) — 기능 구조, 소기능 상세, 서비스 정책
3. **`usecase-definition.md`** (선택) — 유즈케이스 상세 흐름 (상호작용 패턴 참고용)
4. **`requirements-definition.md`** (선택) — 요구사항 (라벨링, 우선순위 참고용)

> **검증**: `ia-screen-design.md`가 존재하지 않으면 사용자에게 알리고 중단한다:
> "해당 디렉토리에 ia-screen-design.md가 없습니다. `/service-planner`로 기획 산출물을 먼저 생성해 주세요."

#### C. 디자인 시스템 로드

프로젝트의 디자인 시스템을 로드한다:

1. **`src/styles/design-tokens.css`** (필수) — CSS Custom Properties (색상, 타이포, 스페이싱 등)
2. **`docs/design-system/components.md`** (필수) — 컴포넌트 스타일 가이드
3. **`docs/design-system/layout-grid.md`** (필수) — 레이아웃 그리드 시스템

> **검증**: `src/styles/design-tokens.css`가 존재하지 않으면 사용자에게 알린다:
> "디자인 토큰 파일이 없습니다. `/project-init`으로 프로젝트를 먼저 초기화해 주세요."
> 파일이 없어도 `$CLAUDE_PLUGIN_ROOT/skills/project-init/templates/design-tokens.css`의 기본 토큰으로 대체하여 진행할 수 있다. 사용자에게 확인 후 진행한다.

#### D. 프로젝트 컨텍스트 분석

1. `CLAUDE.md` 읽기 — 프로젝트명, 기술 스택, 디자인 시스템 선택사항 확인
2. `ux/` 디렉토리 스캔 — 기존 UX 프로토타입 확인 (중복 방지)
3. 프로젝트에 설치된 공통 컴포넌트 확인 — `src/components/` 하위 구조 파악

#### E. UX 인터랙션 패턴 가이드 로드

`$CLAUDE_PLUGIN_ROOT/docs/ux/ux-interaction-patterns.md` 파일을 읽어 인터랙션 패턴 레퍼런스를 로드한다.

이 가이드는 11개 카테고리의 UX 인터랙션 패턴을 정의한다:

| 카테고리 | 핵심 패턴 | 적용 화면 유형 |
|---------|---------|-------------|
| 마이크로 인터랙션 | 버튼 피드백, 토글 애니메이션, 로딩 상태, 카운터 애니메이션 | 전체 |
| 내비게이션 | 탭 바, 브레드크럼, 바텀 시트 | 전체 |
| 피드백 & 응답 | 스켈레톤 스크린, 낙관적 업데이트, 토스트/스낵바 | 전체 |
| 제스처 기반 인터랙션 | 스와이프 액션, 핀치 투 줌, 드래그 앤 드롭, 롱 프레스, 더블 탭 | 목록(스와이프), 상세(핀치줌), 설정(드래그 정렬) |
| 스크롤 인터랙션 | 패럴랙스, 무한 스크롤, 고정 헤더, 스크롤 트리거 애니메이션, 스크롤 스냅 | 목록, 대시보드, 랜딩 |
| 폼 인터랙션 | 인라인 유효성 검사, 플로팅 라벨, 자동완성, 스마트 기본값, 단계별 마법사, 입력 마스크 | 폼, 로그인/가입 |
| 전환 & 애니메이션 | 페이지 전환, 공유 요소 전환, 모핑, 스프링 물리학, 시차 등장 | 전체 |
| 온보딩 | 점진적 공개, 툴팁, 코치 마크, 빈 상태, 기능 발견 | 대시보드, 첫 사용 화면 |
| 접근성 | 스크린 리더, 포커스 관리, 모션 감소, 색상 대비, 터치 타겟 | 전체 (필수) |
| 딜라이트 패턴 | 축하 애니메이션, 이스터 에그, 개인화 경험 | 성취/완료 화면 |
| 다크 패턴 방지 | 확인 수치심, 강제 행동, 트릭 질문, 숨겨진 비용 금지 | 전체 (필수 준수) |

각 화면 생성 시, **화면 유형과 사용자 시나리오에 맞는 인터랙션 패턴**을 선택하여 적용한다. 구체적인 적용 규칙은 Step 2에서 정의한다.

#### F. 디자인 방향성 선택

`AskUserQuestion`으로 프로토타입의 미학적 방향을 선택한다:

```
## UX 프로토타입 디자인 방향

프로토타입의 디자인 톤을 선택하세요.
(프로젝트의 디자인 토큰 위에 추가적인 미학적 방향을 적용합니다)

| # | 디자인 톤 | 설명 | 적합한 프로젝트 |
|---|---------|------|-------------|
| 1 | Refined Minimal | 깔끔하고 정제된 미니멀, 넉넉한 여백, 섬세한 타이포 | SaaS, 생산성 도구 |
| 2 | Bold & Vibrant | 대담한 색상, 강렬한 대비, 역동적 레이아웃 | 소비자 앱, 마케팅 |
| 3 | Soft & Warm | 부드러운 곡선, 파스텔 톤, 친근한 느낌 | 커뮤니티, 교육 |
| 4 | Editorial | 매거진 스타일, 대비되는 서체 조합, 그리드 파괴 | 콘텐츠, 미디어 |
| 5 | Professional Enterprise | 안정적이고 신뢰감 있는 엔터프라이즈 UI | B2B, 관리자 도구 |
| 6 | Auto (기능 특성에 맞게 자동 선택) | AI가 기능 설명 기반으로 최적 톤 선택 | 모든 유형 |

선택:
```

선택된 디자인 톤을 `{DESIGN_TONE}`으로 저장한다. 이 톤은 Step 1에서 `/frontend-design` 호출 시 전달되며, 컴포넌트 스타일링과 페이지 레이아웃에 영향을 준다.

#### G. 생성 범위 확인

`ia-screen-design.md`에서 추출한 화면 목록을 사용자에게 보여주고 생성 범위를 확인한다:

```
## UX 프로토타입 생성 범위 확인

다음 화면들의 HTML 프로토타입을 생성합니다.

| # | 화면ID | 화면명 | 유형 | 관련 UC |
|---|--------|--------|------|--------|
| 1 | SCR-001 | {화면명} | {유형} | UC-001 |
| 2 | SCR-002 | {화면명} | {유형} | UC-002 |
| ... | ... | ... | ... | ... |

생성할 화면 번호를 선택하세요 (전체: all, 선택: 1,3,5):
```

선택된 화면들을 `{SELECTED_SCREENS}` 배열로 저장한다.

---

### Step 1: UX 공통 리소스 생성

#### A. 디렉토리 구조 생성

`ux/{feature-name}/` 디렉토리를 생성한다. `{feature-name}`은 기획 디렉토리의 피처명에서 추출한다 (예: `001-auth` → `auth`).

```
ux/{feature-name}/
├── index.html              # 화면 인덱스 (네비게이션 허브)
├── assets/
│   ├── tokens.css          # 디자인 토큰 (프로젝트의 design-tokens.css 복사)
│   ├── ux-base.css         # UX 프로토타입 공통 스타일
│   ├── ux-components.css   # 공통 컴포넌트 CSS
│   └── ux-interactions.css # 인터랙션 & 애니메이션 CSS
├── images/
│   ├── hero-*.webp         # AI 생성 히어로/배너 이미지
│   ├── empty-*.webp        # AI 생성 빈 상태 일러스트
│   ├── onboarding-*.webp   # AI 생성 온보딩 일러스트
│   └── avatar-*.webp       # AI 생성 프로필 아바타
├── screens/
│   ├── {screen-id}.html    # 개별 화면 HTML (예: scr-001.html)
│   └── ...
└── shared/
    ├── nav.js              # 공통 네비게이션 JS
    └── interactions.js     # 인터랙션 패턴 JS (마이크로 인터랙션, 전환 효과)
```

#### B. 디자인 토큰 파일 생성

`ux/{feature-name}/assets/tokens.css` — 프로젝트의 `src/styles/design-tokens.css`를 **그대로 복사**한다. 수정하지 않는다.

#### C. UX 베이스 스타일 생성

`ux/{feature-name}/assets/ux-base.css` — 디자인 토큰을 참조하는 기본 레이아웃 스타일을 생성한다.

이 파일은 `docs/design-system/layout-grid.md`의 규칙을 CSS로 구현한 것이다:

```css
/* UX Prototype Base Styles — design-tokens.css 참조 */

/* Reset */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
}

body {
  font-family: var(--font-family-sans);
  font-size: var(--font-size-base);
  line-height: var(--line-height-normal);
  color: var(--color-text-primary);
  background-color: var(--color-bg-primary);
}

/* Container — layout-grid.md 기반 */
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding-left: var(--spacing-4);
  padding-right: var(--spacing-4);
}

@media (min-width: 768px) {
  .container {
    padding-left: var(--spacing-6);
    padding-right: var(--spacing-6);
  }
}

@media (min-width: 1024px) {
  .container {
    padding-left: var(--spacing-8);
    padding-right: var(--spacing-8);
  }
}

/* Grid System — 12 Column */
.grid {
  display: grid;
  gap: var(--spacing-4);
  grid-template-columns: repeat(4, 1fr);
}

@media (min-width: 768px) {
  .grid {
    gap: var(--spacing-6);
    grid-template-columns: repeat(8, 1fr);
  }
}

@media (min-width: 1024px) {
  .grid {
    gap: var(--spacing-6);
    grid-template-columns: repeat(12, 1fr);
  }
}

/* Page Layout — GNB + Sidebar + Content */
.page-layout {
  display: flex;
  min-height: 100vh;
  padding-top: 64px; /* GNB height */
}

.page-sidebar {
  width: 240px;
  flex-shrink: 0;
  background: var(--color-bg-secondary);
  border-right: var(--border-width-default) solid var(--color-border-default);
  position: fixed;
  top: 64px;
  left: 0;
  bottom: 0;
  overflow-y: auto;
  transition: width var(--duration-normal) var(--easing-default);
  z-index: var(--z-sticky);
}

.page-content {
  flex: 1;
  margin-left: 240px;
  padding: var(--spacing-6);
  min-width: 0;
}

/* GNB — 64px fixed top */
.gnb {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: var(--color-bg-primary);
  border-bottom: var(--border-width-default) solid var(--color-border-default);
  display: flex;
  align-items: center;
  padding: 0 var(--spacing-6);
  z-index: var(--z-sticky);
}

/* Responsive: Tablet */
@media (max-width: 1023px) {
  .page-sidebar {
    width: 64px;
  }
  .page-sidebar .sidebar-label {
    display: none;
  }
  .page-content {
    margin-left: 64px;
  }
}

/* Responsive: Mobile */
@media (max-width: 767px) {
  .page-sidebar {
    transform: translateX(-100%);
    width: 240px;
    z-index: var(--z-modal);
  }
  .page-sidebar.open {
    transform: translateX(0);
  }
  .page-content {
    margin-left: 0;
    padding: var(--spacing-4);
  }
  .gnb .gnb-menu-btn {
    display: flex;
  }
}

/* Section spacing */
.section {
  margin-bottom: var(--spacing-8);
}

.section-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-4);
}

/* Page header */
.page-header {
  margin-bottom: var(--spacing-6);
}

.page-header h1 {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.page-header p {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin-top: var(--spacing-1);
}

/* Utility classes */
.text-center { text-align: center; }
.text-right { text-align: right; }
.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.gap-2 { gap: var(--spacing-2); }
.gap-4 { gap: var(--spacing-4); }
.gap-6 { gap: var(--spacing-6); }
.mt-4 { margin-top: var(--spacing-4); }
.mt-6 { margin-top: var(--spacing-6); }
.mb-4 { margin-bottom: var(--spacing-4); }
.mb-6 { margin-bottom: var(--spacing-6); }
.hidden { display: none; }

@media (min-width: 768px) {
  .md\:block { display: block; }
  .md\:flex { display: flex; }
  .md\:hidden { display: none; }
  .md\:grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 1024px) {
  .lg\:block { display: block; }
  .lg\:flex { display: flex; }
  .lg\:hidden { display: none; }
  .lg\:grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
  .lg\:grid-cols-4 { grid-template-columns: repeat(4, 1fr); }
}
```

위 CSS는 기본 템플릿이다. 프로젝트의 `layout-grid.md` 내용에 맞게 실제 값을 조정한다.

#### D. 프로덕션급 컴포넌트 스타일 생성

> **`/frontend-design` 연동**: `frontend-design` 스킬이 설치되어 있으면 `Skill` 도구로 호출하여 프로덕션급 디자인을 생성한다. 설치되어 있지 않으면 아래 프롬프트의 요구사항을 직접 구현하여 `ux-components.css` 파일을 작성한다. (frontend-design은 별도 Claude Code 플러그인으로, 설치 여부는 환경에 따라 다르다.)

호출 또는 직접 구현 시 다음 요구사항을 따른다:

```
"UX 프로토타입의 공통 컴포넌트 CSS를 프로덕션 수준으로 작성해 줘.

디자인 톤: {DESIGN_TONE}
기능: {FEATURE_DESCRIPTION}
디자인 토큰: ux/{feature-name}/assets/tokens.css 의 CSS Custom Properties를 반드시 사용
컴포넌트 스펙: docs/design-system/components.md 참조

출력 파일: ux/{feature-name}/assets/ux-components.css

다음 컴포넌트를 구현해 줘:
1. Button — Primary/Secondary/Danger/Ghost, sm/md/lg, 로딩/비활성 + 눌림 효과(scale 0.95), ripple effect
2. Input — 플로팅 라벨, 에러/성공 상태, 포커스 링, 헬퍼 텍스트
3. Card — Default/Elevated/Outlined/Interactive + hover lift 효과
4. Modal — 백드롭 fade-in, 모달 slide-up, 포커스 트랩
5. Table — 정렬, 호버, 반응형(모바일 카드 전환) + 시머 로딩
6. Navigation — 사이드바(접기/펼치기 애니메이션), 탭(인디케이터 슬라이드)
7. Toast — 슬라이드 인/아웃, 프로그레스 바(자동 닫힘)
8. Badge — 상태별 색상, 펄스 애니메이션(알림)
9. Skeleton — 시머 효과 로딩 플레이스홀더
10. Toggle — 슬라이드 전환, 색상 변화 애니메이션

핵심 요구사항:
- 모든 값은 var(--*) 디자인 토큰만 사용 (하드코딩 절대 금지)
- 다크 모드 [data-theme='dark'] 완전 대응
- 버튼 :active에 scale(0.95) + 150ms ease 눌림 효과
- 카드 hover에 translateY(-2px) + shadow 전환
- prefers-reduced-motion 대응 필수
- 접근성: focus-visible 포커스 링, 충분한 터치 타겟(44px)
- {DESIGN_TONE}에 맞는 미학적 디테일 (그라디언트, 배경 텍스처, 미묘한 애니메이션 등)
- 제네릭하고 평범한 AI 스타일이 아닌, 의도적이고 개성 있는 디자인"
```

> **핵심**: 프로덕션급 디자인은 "아름답고 기억에 남는 인터페이스"를 목표로 한다. 디자인 토큰 기반 위에 선택된 `{DESIGN_TONE}`에 맞는 추가적인 미학적 요소(미묘한 그라디언트, 배경 텍스처, 대담한 타이포그래피, 인텐셔널한 공간 배치)를 적용한다. `frontend-design` 스킬이 없는 경우에도 동일한 품질 기준으로 직접 CSS를 작성한다.

#### E. 인터랙션 & 애니메이션 CSS 생성

`ux/{feature-name}/assets/ux-interactions.css` — `ux-interaction-patterns.md` 가이드에서 추출한 공통 인터랙션 CSS를 생성한다.

이 파일은 화면에서 재사용되는 인터랙션 애니메이션을 정의한다:

```css
/* ux-interactions.css — UX 인터랙션 패턴 가이드 기반 */

/* ==========================================================================
   1. 마이크로 인터랙션 — 버튼 피드백 (1.1)
   ========================================================================== */
.btn { touch-action: manipulation; }
.btn:active { transform: scale(0.95); }

/* Ripple Effect */
.ripple { position: relative; overflow: hidden; }
.ripple::after {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(circle, rgba(255,255,255,0.3) 10%, transparent 70%);
  transform: scale(0); opacity: 0;
  transition: transform 400ms ease, opacity 400ms ease;
}
.ripple:active::after { transform: scale(2.5); opacity: 1; transition: 0ms; }

/* ==========================================================================
   2. 로딩 상태 — 스켈레톤 시머 (1.3, 3.2)
   ========================================================================== */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.skeleton {
  background: linear-gradient(90deg, var(--color-bg-tertiary) 25%, var(--color-bg-secondary) 50%, var(--color-bg-tertiary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-md);
}

/* ==========================================================================
   3. 스크롤 트리거 애니메이션 — 페이드 인 (5.4)
   ========================================================================== */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-on-scroll {
  opacity: 0;
  animation: fadeInUp 0.6s var(--easing-out) forwards;
}
/* 시차 등장 (7.5) */
.stagger-1 { animation-delay: 50ms; }
.stagger-2 { animation-delay: 100ms; }
.stagger-3 { animation-delay: 150ms; }
.stagger-4 { animation-delay: 200ms; }
.stagger-5 { animation-delay: 250ms; }

/* ==========================================================================
   4. 카운터 애니메이션 (1.6)
   ========================================================================== */
@keyframes countUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.counter-animate { animation: countUp 0.4s var(--easing-out) forwards; }

/* ==========================================================================
   5. 페이지 전환 (7.1)
   ========================================================================== */
@keyframes slideInFromRight {
  from { opacity: 0; transform: translateX(30px); }
  to { opacity: 1; transform: translateX(0); }
}
.page-enter { animation: slideInFromRight 0.3s var(--easing-out); }

/* ==========================================================================
   6. 빈 상태 (8.4)
   ========================================================================== */
.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: var(--spacing-16) var(--spacing-6);
  text-align: center;
}
.empty-state img { max-width: 200px; margin-bottom: var(--spacing-6); opacity: 0.8; }
.empty-state h3 { font-size: var(--font-size-lg); font-weight: var(--font-weight-semibold); margin-bottom: var(--spacing-2); }
.empty-state p { color: var(--color-text-secondary); margin-bottom: var(--spacing-6); }

/* ==========================================================================
   7. 토글 애니메이션 (1.2)
   ========================================================================== */
.toggle { /* ... 토글 스타일 ... */ transition: background-color 250ms ease; }
.toggle.active { background-color: var(--color-primary-600); }
.toggle-thumb { transition: transform 250ms cubic-bezier(0.4, 0, 0.2, 1); }

/* ==========================================================================
   8. 고정 헤더 — 스크롤 시 축소 (5.3)
   ========================================================================== */
.gnb.compact { height: 48px; box-shadow: var(--shadow-sm); }
.gnb { transition: height var(--duration-normal) var(--easing-default), box-shadow var(--duration-normal); }

/* ==========================================================================
   9. 모션 감소 대응 (9.3) — 접근성 필수
   ========================================================================== */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
  .animate-on-scroll { opacity: 1; transform: none; }
}
```

위 CSS는 기본 템플릿이다. 화면별로 필요한 추가 인터랙션 키프레임을 `ux-interactions.css`에 추가하거나, 화면별 `<style>` 블록에 작성한다.

#### F. AI 이미지 에셋 생성

> **`fect-image` MCP 연동**: `mcp__fect-image__image_text2img` 도구가 사용 가능한 경우 AI 이미지 에셋을 생성한다. MCP 도구가 사용 불가능한 경우(fect-image 서버가 설치되지 않은 환경), 이미지 대신 CSS 그라디언트/SVG 패턴 기반 플레이스홀더를 사용하고 이미지 생성 단계를 건너뛴다.

`mcp__fect-image__image_text2img` 도구를 사용하여 프로토타입에 필요한 이미지 에셋을 생성한다.

**생성할 이미지 목록** (화면 구성에 따라 선별 적용):

| 용도 | 프롬프트 패턴 | 비율 | 저장 경로 |
|------|------------|------|---------|
| 히어로/배너 | "{기능 설명} web application hero banner, modern {DESIGN_TONE} style, abstract geometric, professional, clean background" | 16:9 | `ux/{feature-name}/images/hero-{name}.webp` |
| 빈 상태 일러스트 | "Empty state illustration for {상황}, minimalist line art, soft pastel colors, friendly and inviting, no text" | 1:1 | `ux/{feature-name}/images/empty-{name}.webp` |
| 온보딩 일러스트 | "Onboarding step illustration showing {단계 설명}, flat design, modern, cheerful colors, no text" | 4:3 | `ux/{feature-name}/images/onboarding-{step}.webp` |
| 프로필 아바타 | "Professional avatar illustration, diverse person, flat modern style, neutral background, friendly expression" | 1:1 | `ux/{feature-name}/images/avatar-{n}.webp` |
| 로그인 배경 | "Abstract background for login page, {DESIGN_TONE} aesthetic, subtle gradient, modern, professional" | 16:9 | `ux/{feature-name}/images/login-bg.webp` |
| 카드 썸네일 | "Abstract thumbnail for {카테고리}, modern {DESIGN_TONE} style, geometric shapes, vibrant" | 4:3 | `ux/{feature-name}/images/thumb-{name}.webp` |

**이미지 생성 규칙**:
1. 화면 구성을 분석하여 **필요한 이미지만** 선별 생성한다 (과다 생성 금지)
2. 빈 상태가 있는 화면 → 반드시 빈 상태 일러스트 생성
3. 대시보드/랜딩 → 히어로 배너 생성
4. 사용자 목록/프로필 → 아바타 2~3개 생성
5. 로그인/가입 화면 → 배경 또는 사이드 일러스트 생성
6. 모든 이미지는 `imageSize: "2K"` 사용 (model 파라미터는 MCP 서버 기본값 사용)
7. 프롬프트는 영어로 작성 (더 나은 품질)
8. `mcp__fect-image__image_text2img` 도구가 사용 불가능하면 이 단계를 건너뛰고, HTML에서 CSS 그라디언트/SVG 기반 플레이스홀더를 대신 사용한다

#### G. 공통 네비게이션 & 인터랙션 JS 생성

**`ux/{feature-name}/shared/nav.js`** 와 **`ux/{feature-name}/shared/interactions.js`** 두 파일을 생성한다.

`nav.js`는 기본 네비게이션(사이드바 토글, 다크모드, 모달, 토스트, 탭 전환)을 담당한다.

`interactions.js`는 `$CLAUDE_PLUGIN_ROOT/docs/ux/ux-interaction-patterns.md` 가이드의 패턴을 JavaScript로 구현한다:

| 인터랙션 | 패턴 # | 구현 |
|---------|--------|------|
| 스크롤 트리거 애니메이션 | 5.4 | Intersection Observer + fadeInUp |
| 고정 헤더 축소/숨김 | 5.3 | scroll 이벤트 + show-on-scroll-up |
| 카운터 애니메이션 | 1.6 | requestAnimationFrame + ease-out |
| 인라인 유효성 검사 | 6.1 | onBlur + 에러/성공 표시 |
| 플로팅 라벨 | 6.2 | focus/blur/input 이벤트 |
| 빈 상태 전환 | 8.4 | opacity/display 전환 |
| 축하 애니메이션 | 10.2 | 파티클 confetti (CSS 변수 색상) |
| 드래그 앤 드롭 | 4.3 | HTML5 drag API |
| 토스트 프로그레스 바 | 3.5 | CSS animation + 자동 닫힘 |
| 포커스 트랩 (모달) | 9.2 | 첫 포커서블 요소로 이동 |

각 JS 파일의 구체적인 구현은 `frontend-design` 스킬이 설치되어 있으면 `Skill` 도구로 호출하고, 없으면 아래 요구사항을 직접 구현한다:

```
"UX 프로토타입의 공통 JavaScript 파일 2개를 작성해 줘.

디자인 톤: {DESIGN_TONE}
기능: {FEATURE_DESCRIPTION}
인터랙션 패턴 참조: $CLAUDE_PLUGIN_ROOT/docs/ux/ux-interaction-patterns.md

출력 파일 1: ux/{feature-name}/shared/nav.js — 기본 네비게이션 & 코어 컨트롤
  - 사이드바 토글 (모바일 오버레이 + 스크림)
  - 다크모드 전환 (localStorage 저장 + 아이콘 업데이트)
  - 모달 열기/닫기 (포커스 트랩 + ESC 키 닫기)
  - 토스트 알림 (프로그레스 바 + 에러는 수동 닫기)
  - 탭 전환 (인디케이터 슬라이드 애니메이션)
  - 현재 페이지 사이드바 하이라이트

출력 파일 2: ux/{feature-name}/shared/interactions.js — UX 인터랙션 패턴
  - Intersection Observer 기반 스크롤 트리거 (animate-on-scroll, 시차 등장)
  - 스크롤 방향 감지 헤더 숨김/표시 (show-on-scroll-up)
  - requestAnimationFrame 카운터 (data-count-to 속성)
  - 인라인 유효성 검사 (onBlur, 에러/성공 피드백)
  - 플로팅 라벨 (focus/blur/input)
  - 빈 상태 → 데이터 전환
  - 파티클 축하 효과 (celebrate 함수)
  - 간단한 드래그 정렬 (initSortable)

핵심 요구사항:
- prefers-reduced-motion 대응 필수
- 접근성: aria 속성, 포커스 관리, 키보드 조작
- 순수 JavaScript (외부 라이브러리 금지)
- {DESIGN_TONE}에 맞는 세련된 이징, 타이밍, 효과"
```

#### H. 완료 보고

```
✅ UX 공통 리소스 생성 완료
- ux/{feature-name}/assets/tokens.css (디자인 토큰)
- ux/{feature-name}/assets/ux-base.css (레이아웃 시스템)
- ux/{feature-name}/assets/ux-components.css (프로덕션급 컴포넌트 — /frontend-design)
- ux/{feature-name}/assets/ux-interactions.css (인터랙션 애니메이션)
- ux/{feature-name}/shared/nav.js (네비게이션 & 코어)
- ux/{feature-name}/shared/interactions.js (UX 인터랙션 패턴)
- ux/{feature-name}/images/*.webp (AI 생성 이미지 에셋)

다음 단계: 개별 화면 HTML 생성을 진행합니다.
```

---

### Step 2: 개별 화면 HTML 생성

`{SELECTED_SCREENS}` 배열의 각 화면에 대해 HTML 파일을 생성한다.

#### A. 화면 정보 추출

`ia-screen-design.md`에서 각 화면의 다음 정보를 추출한다:

1. **화면ID** (SCR-001)
2. **화면명**
3. **화면 유형** (목록/상세/폼/모달/대시보드)
4. **와이어프레임** (ASCII 아트 구조)
5. **UI 요소 설명** (요소명, 유형, 설명, 동작)
6. **관련 UC 및 FR**

`feature-definition.md`에서 추가 정보를 추출한다:

1. **관련 소기능의 비즈니스 규칙** (입력 필드 유효성, 상태 전환 등)
2. **서비스 정책** (예외 처리 메시지 등)

`usecase-definition.md`에서 참고 정보를 추출한다:

1. **유즈케이스 기본 흐름** (화면 내 사용자-시스템 상호작용 순서)
2. **대안 흐름 / 예외 흐름** (에러 상태, 빈 상태 등)

#### B. 화면 유형별 템플릿 + 인터랙션 패턴 매핑

화면 유형에 따라 적절한 레이아웃과 **적용할 인터랙션 패턴**을 결정한다. 인터랙션 패턴 번호는 `ux-interaction-patterns.md`의 섹션 번호에 대응한다:

| 화면 유형 | 레이아웃 패턴 | 주요 컴포넌트 | 필수 인터랙션 패턴 |
|-----------|-------------|-------------|-----------------|
| 목록 (List) | 사이드바 + 테이블/카드 그리드 | Table, Card, Badge, Pagination, 검색/필터 | 스켈레톤 로딩(3.2), 고정 헤더(5.3), 스크롤 트리거(5.4), 시차 등장(7.5), 빈 상태(8.4) |
| 상세 (Detail) | 사이드바 + 콘텐츠 영역 | Card, Badge, Button, Tab | 탭 전환(2.6), 스크롤 트리거(5.4), 브레드크럼(2.4), 페이지 전환(7.1) |
| 폼 (Form) | 사이드바 + 2열 폼 | Input, Select, Button, 유효성 메시지 | **인라인 유효성(6.1)**, **플로팅 라벨(6.2)**, 입력 마스크(6.6), 단계별 마법사(6.5, 복잡 폼 시), 스마트 기본값(6.4) |
| 모달 (Modal) | 오버레이 + 모달 창 | Modal, Input, Button | **포커스 트랩(9.2)**, 모달 slide-up 전환(7.1), 백드롭 fade |
| 대시보드 (Dashboard) | 사이드바 + KPI 카드 + 차트 영역 | Card, Badge, Table | **카운터 애니메이션(1.6)**, 시차 등장(7.5), 스크롤 트리거(5.4), 스켈레톤(3.2) |
| 설정 (Settings) | 사이드바 + 탭 + 폼 | Tab, Input, Button, Toggle | **토글 애니메이션(1.2)**, 탭 전환(2.6), 인라인 유효성(6.1), 토스트 피드백(3.5) |
| 로그인/가입 (Auth) | 중앙 정렬 카드 (사이드바 없음) | Card, Input, Button | **플로팅 라벨(6.2)**, **인라인 유효성(6.1)**, 버튼 로딩(1.3), 페이지 전환(7.1) |
| 온보딩 (Onboarding) | 전체 화면 스텝 | Card, Button, Progress | **점진적 공개(8.1)**, **코치 마크(8.3)**, 스크롤 스냅(5.5), 프로그레스(3.4) |

**모든 화면에 공통 적용되는 인터랙션**:
- 버튼 피드백(1.1): `:active` scale(0.95) + ripple
- 토스트/스낵바(3.5): 성공/실패 피드백
- 모션 감소 대응(9.3): `prefers-reduced-motion`
- 포커스 관리(9.2): `focus-visible` 포커스 링
- 색상 대비(9.4): WCAG AA 기준 준수
- 터치 타겟(9.5): 최소 44px

#### C. 개별 화면 HTML 생성 (프로덕션 수준)

각 화면에 대해 **프로덕션 수준의 HTML**을 생성한다. `frontend-design` 스킬이 설치되어 있으면 `Skill` 도구로 호출하고, 없으면 아래 요구사항을 직접 구현하여 HTML 파일을 작성한다.

화면마다 다음 요구사항을 적용한다:

```
"UX 프로토타입 화면을 프로덕션 수준으로 작성해 줘.

출력 파일: ux/{feature-name}/screens/{screen-id}.html

디자인 톤: {DESIGN_TONE}
화면 정보:
- 화면ID: {SCR-ID}
- 화면명: {화면명}
- 화면 유형: {유형}
- 관련 유즈케이스: {UC-IDs}

와이어프레임 (ia-screen-design.md에서 추출):
{와이어프레임 ASCII 아트 원문}

UI 요소 설명:
{UI 요소 테이블 원문}

비즈니스 규칙 (feature-definition.md에서 추출):
{관련 소기능의 규칙 원문}

적용할 인터랙션 패턴 (ux-interaction-patterns.md 기반):
{화면 유형별 필수 인터랙션 목록}

CSS/JS 참조:
- <link rel='stylesheet' href='../assets/tokens.css'>
- <link rel='stylesheet' href='../assets/ux-base.css'>
- <link rel='stylesheet' href='../assets/ux-components.css'>
- <link rel='stylesheet' href='../assets/ux-interactions.css'>
- <script src='../shared/nav.js'>
- <script src='../shared/interactions.js'>

이미지 참조: ../images/ 디렉토리의 AI 생성 이미지 사용

핵심 요구사항:
- 와이어프레임의 모든 UI 요소를 실제 HTML 컴포넌트로 구현
- {DESIGN_TONE}에 맞는 세련된 디자인 (제네릭한 AI 스타일 금지)
- 사실적인 더미 데이터 채우기
- 빈 상태, 에러 상태, 로딩 상태(스켈레톤) 포함
- 반응형 (모바일/태블릿/데스크톱)
- 다크 모드 대응
- 접근성: 시맨틱 HTML, ARIA, focus-visible, 충분한 터치 타겟"
```

**HTML 구조 규칙** (모든 화면 공통):

```html
<!DOCTYPE html>
<html lang="{project-language}" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{화면명} — {기능명} UX Prototype</title>
  <link rel="stylesheet" href="../assets/tokens.css">
  <link rel="stylesheet" href="../assets/ux-base.css">
  <link rel="stylesheet" href="../assets/ux-components.css">
  <link rel="stylesheet" href="../assets/ux-interactions.css">
</head>
<body class="page-enter">

  <!-- GNB — 고정 헤더 (5.3) -->
  <header class="gnb">
    <button class="gnb-menu-btn" onclick="toggleSidebar()" aria-label="메뉴 토글">☰</button>
    <div class="gnb-logo">{프로젝트명 또는 기능명}</div>
    <div class="gnb-spacer" style="flex:1"></div>
    <button class="btn btn-ghost btn-sm theme-toggle-icon" onclick="toggleTheme()">🌙</button>
    <div class="gnb-user">
      <img src="../images/avatar-1.webp" alt="사용자" width="32" height="32" style="border-radius:50%">
    </div>
  </header>

  <!-- Sidebar Overlay (모바일) -->
  <div class="sidebar-overlay" onclick="toggleSidebar()"></div>

  <!-- Page Layout -->
  <div class="page-layout">

    <!-- Sidebar — IA 메뉴 구조 기반 -->
    <nav class="page-sidebar" aria-label="메인 내비게이션">
      <ul class="sidebar-nav">
        <!-- ia-screen-design.md의 IA 메뉴 구조에서 생성 -->
        <li class="sidebar-item active">
          <a href="{screen-id}.html">
            <span class="sidebar-icon">{아이콘}</span>
            <span class="sidebar-label">{메뉴명}</span>
          </a>
        </li>
      </ul>
    </nav>

    <!-- Main Content — 시차 등장 (7.5) -->
    <main class="page-content">
      <div class="page-header animate-on-scroll">
        <h1>{화면명}</h1>
        <p>{화면 설명}</p>
      </div>

      <!-- 화면 유형별 콘텐츠 + 인터랙션 패턴 적용 -->

    </main>
  </div>

  <!-- Modal (필요한 경우 — 포커스 트랩 9.2) -->

  <script src="../shared/nav.js"></script>
  <script src="../shared/interactions.js"></script>
</body>
</html>
```

**와이어프레임 → HTML 변환 규칙**:

1. **ASCII 와이어프레임의 각 영역을 실제 HTML 컴포넌트로 변환**한다
   - `[버튼명]` → `<button class="btn btn-primary">버튼명</button>`
   - `{입력 필드}` → `<div class="input-group"><label>...</label><input class="input"></div>`
   - `{데이터 영역}` → `<div class="card">...</div>` 또는 `<table class="table">...</table>`
   - `{탭 영역}` → 탭 네비게이션 + 탭 콘텐츠 패널
   - `메뉴` → 사이드바 네비게이션 (IA 구조 반영)

2. **UI 요소 설명 테이블의 모든 요소를 구현**한다
   - 요소 유형에 맞는 HTML + CSS 클래스 적용
   - 동작(Action)은 JavaScript 인터랙션으로 구현 (모달 열기/닫기, 탭 전환, 토스트 표시 등)

3. **더미 데이터로 채운다**
   - 테이블: 5~10행의 사실적인 더미 데이터
   - 카드: 3~6개의 더미 카드
   - 폼: placeholder 텍스트와 기본값
   - 대시보드: KPI 수치와 그래프 영역 (텍스트 플레이스홀더)

4. **상태(State) 표현을 포함**한다 (인터랙션 패턴 참조)
   - **빈 상태 (8.4)**: AI 생성 일러스트(`images/empty-*.webp`) + 설명 메시지 + CTA 버튼. `.empty-state` 클래스 사용
   - **로딩 상태 (1.3, 3.2)**: 스켈레톤 UI(`.skeleton` + 시머 애니메이션). 실제 콘텐츠와 동일한 레이아웃 형태. `<div class="skeleton" style="height:20px;width:60%"></div>`
   - **에러 상태 (6.1)**: 인라인 유효성 — 필드 아래 에러 메시지 + 빨간 테두리, `.has-error` 클래스
   - **성공 상태 (6.1)**: 인라인 성공 — 녹색 체크마크, `.has-success` 클래스
   - **성공/실패 피드백 (3.5)**: `showToast(message, type)` — 프로그레스 바 포함 토스트. 에러 토스트는 수동 닫기

5. **반응형 레이아웃을 적용**한다
   - 모바일: 1열 레이아웃, 사이드바 숨김, 테이블→카드 전환
   - 태블릿: 2열 레이아웃, 사이드바 축소(64px)
   - 데스크톱: 12열 그리드, 사이드바 확장(240px)

6. **화면 유형별 인터랙션 패턴을 구현**한다 (Step 2.B 매핑 참조)

   **목록 화면**:
   - `.animate-on-scroll` + `.stagger-{n}` 클래스로 리스트 아이템 시차 등장 (7.5)
   - 스켈레톤 로딩 → 데이터 fade-in 전환 (3.2)
   - 빈 상태 일러스트 + CTA (8.4)
   - 테이블 행 hover 하이라이트

   **폼 화면**:
   - `.floating-label-group` 으로 플로팅 라벨 (6.2)
   - `validateField()` 연동 인라인 유효성 (6.1)
   - 비밀번호 강도 실시간 피드백
   - 전화번호/카드번호 입력 마스크 (6.6)
   - 제출 버튼 로딩 상태 (1.3)

   **대시보드 화면**:
   - KPI 숫자에 `data-count-to` 속성으로 카운터 애니메이션 (1.6)
   - 카드 `.animate-on-scroll` + 시차 등장
   - 차트 영역 스켈레톤 → 콘텐츠 전환

   **설정 화면**:
   - 토글 스위치 애니메이션 (1.2)
   - 변경 시 `showToast('설정이 저장되었습니다', 'success')` (3.5)
   - 탭 인디케이터 슬라이드 (2.6)

   **로그인/가입 화면**:
   - 배경 이미지 (`images/login-bg.webp`) 또는 그라디언트
   - 플로팅 라벨 (6.2) + 인라인 유효성 (6.1)
   - 로그인 버튼 로딩 + 성공 시 `celebrate()` (10.2)
   - 소셜 로그인 버튼 hover 효과

#### D. 화면 간 연결

`ia-screen-design.md`의 **화면 흐름도 (Screen Flow)**를 기반으로 화면 간 링크를 설정한다:
- 버튼 클릭 → 다른 화면으로 이동 (`href` 또는 `onclick`)
- 목록 행 클릭 → 상세 화면으로 이동
- 폼 제출 → 결과 화면 또는 이전 화면으로 이동 (토스트 + redirect)
- 모달 확인 → 모달 닫기 + 토스트 표시

#### E. 진행 상황 보고

화면 3개마다 사용자에게 중간 보고한다:

```
🔄 진행 상황: {완료 수}/{전체 수} 화면 생성됨
- ✅ SCR-001: {화면명}
- ✅ SCR-002: {화면명}
- ✅ SCR-003: {화면명}
- ⏳ SCR-004: {화면명} (다음)

계속 진행할까요?
```

---

### Step 3: 인덱스 페이지 생성

#### A. 인덱스 HTML 생성

`ux/{feature-name}/index.html` — 모든 화면을 한눈에 보고 이동할 수 있는 허브 페이지를 생성한다.

인덱스 페이지 구성:

1. **프로토타입 헤더** — 기능명, 생성일, 화면 수
2. **화면 흐름도 시각화** — `ia-screen-design.md`의 Screen Flow를 CSS로 시각화 (박스 + 화살표 형태)
3. **화면 카드 그리드** — 각 화면을 카드로 표시:
   - 화면 ID + 화면명
   - 화면 유형 (Badge)
   - 관련 유즈케이스 ID
   - 화면 간략 설명
   - 클릭 시 해당 화면으로 이동
4. **범례 & 컨벤션** — 색상/아이콘의 의미
5. **다크모드 토글** — 전체 프로토타입의 다크모드 전환

인덱스 페이지는 카드 기반 그리드 레이아웃으로, 반응형 대응한다:
- 모바일: 1열
- 태블릿: 2열
- 데스크톱: 3~4열

#### B. 화면 흐름도 시각화

`ia-screen-design.md`의 Mermaid 플로우차트를 HTML/CSS로 변환하여 화면 간 관계를 시각적으로 표현한다:

- 각 화면을 클릭 가능한 박스로 표현
- 화면 간 이동 경로를 선/화살표로 표현
- 현재 화면 하이라이트
- 시작점과 종료점을 구분하여 표시

CSS 기반 간단한 플로우 시각화 (JavaScript 라이브러리 불필요):

```html
<div class="flow-diagram">
  <div class="flow-node" data-screen="scr-001">
    <a href="screens/scr-001.html">SCR-001<br>{화면명}</a>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-node" data-screen="scr-002">
    <a href="screens/scr-002.html">SCR-002<br>{화면명}</a>
  </div>
</div>
```

---

### Step 4: 프로토타입 검증 및 완료

#### A. 생성물 검증

생성된 모든 HTML 파일을 검증한다:

1. **디자인 토큰 사용 확인** — 하드코딩된 색상값(`#`, `rgb(`, `hsl(`)이 없는지 확인
   - `tokens.css`를 통해 참조되는 `var(--*)` 만 허용
   - 발견 시 자동으로 해당 값을 디자인 토큰으로 교체

2. **링크 유효성 확인** — 모든 `href` 경로가 실제 파일을 가리키는지 확인

3. **필수 컴포넌트 포함 확인** — 각 화면에 와이어프레임의 모든 UI 요소가 구현되었는지 확인

4. **반응형 구조 확인** — viewport meta, 반응형 클래스 사용 확인

#### B. CLAUDE.md 업데이트 확인

프로젝트의 `CLAUDE.md`에 UX 프로토타입 경로를 추가할지 사용자에게 확인한다:

```
## UX 프로토타입 경로 등록

CLAUDE.md에 다음 항목을 추가할까요?

### Quick Command Reference 테이블에 추가:
| UX 프로토타입 확인 | `ux/{feature-name}/index.html` 브라우저에서 열기 |

추가할까요? (y/n):
```

#### C. 완료 보고

```
## UX 프로토타입 생성 완료

📁 위치: ux/{feature-name}/

### 생성 파일
| # | 파일 | 설명 | 상태 |
|---|------|------|------|
| 1 | index.html | 화면 인덱스 (네비게이션 허브) | ✅ |
| 2 | assets/tokens.css | 디자인 토큰 | ✅ |
| 3 | assets/ux-base.css | 레이아웃 시스템 | ✅ |
| 4 | assets/ux-components.css | 프로덕션급 컴포넌트 (/frontend-design) | ✅ |
| 5 | assets/ux-interactions.css | 인터랙션 애니메이션 CSS | ✅ |
| 6 | shared/nav.js | 네비게이션 & 코어 컨트롤 | ✅ |
| 7 | shared/interactions.js | UX 인터랙션 패턴 JS | ✅ |
| 8 | images/*.webp | AI 생성 이미지 에셋 ({N}개) | ✅ |
| 9+ | screens/scr-*.html | 개별 화면 ({N}개) | ✅ |

### 요약
- 기획 기반: {PLANNER_DIR}
- 디자인 톤: {DESIGN_TONE}
- 생성 화면 수: {N}개
- AI 이미지 에셋: {N}개 (fect-image)
- 디자인 품질: /frontend-design 프로덕션급
- 디자인 토큰: src/styles/design-tokens.css 참조
- 컴포넌트 스펙: docs/design-system/components.md 준수
- 레이아웃: docs/design-system/layout-grid.md 기반
- 인터랙션: ux-interaction-patterns.md 가이드 기반
- 반응형: 모바일/태블릿/데스크톱 대응
- 다크 모드: 지원
- 접근성: WCAG AA (포커스 관리, 모션 감소, 색상 대비, 터치 타겟)

### 적용된 인터랙션 패턴
| 패턴 | 적용 화면 |
|------|---------|
| 버튼 피드백 (1.1) | 전체 |
| 스켈레톤 로딩 (3.2) | {적용된 화면 목록} |
| 토스트 알림 (3.5) | {적용된 화면 목록} |
| 스크롤 트리거 (5.4) | {적용된 화면 목록} |
| 인라인 유효성 (6.1) | {적용된 화면 목록} |
| 플로팅 라벨 (6.2) | {적용된 화면 목록} |
| 카운터 애니메이션 (1.6) | {적용된 화면 목록} |
| 시차 등장 (7.5) | 전체 |
| 모션 감소 대응 (9.3) | 전체 |

### 확인 방법
브라우저에서 `ux/{feature-name}/index.html`을 열어 프로토타입을 확인할 수 있습니다.
`/test-run`으로 Chrome MCP 기반 시각 확인 및 반응형 테스트도 가능합니다.

### 다음 단계
- DSA가 화면별 디자인을 검수합니다 (Gate 2.5)
- `design-token-validator` 에이전트로 토큰 준수 자동 검증
- 피드백 반영 후 블루프린트 작성으로 진행할 수 있습니다
```
