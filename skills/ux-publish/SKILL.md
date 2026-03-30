---
name: ux-publish
description: "기획 산출물(service-planner)의 IA/화면설계서와 기능정의서를 기반으로 프로덕션 수준의 UI 컴포넌트를 생성합니다. 프로젝트의 기술 스택(React/Vue/Angular/Svelte)에 맞는 컴포넌트를 publish/ 디렉토리에 생성하고, 이후 개발 시 각각의 실제 위치(src/)로 복사하여 사용할 수 있는 구조를 제공합니다. Vibe Coding 디자인 가이드와 애니메이션 가이드를 기반으로 세련된 프로덕션급 UI를 구현합니다."
argument-hint: "[기획 디렉토리명 또는 기능 설명]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Agent, Skill, mcp__fect-image__image_text2img
---

# ASTRA UX 컴포넌트 퍼블리싱

기획 산출물(`/service-planner`)의 IA/화면설계서(`ia-screen-design.md`)와 기능정의서(`feature-definition.md`)를 분석하여, **프로덕션 수준의 UI 컴포넌트**를 `publish/` 디렉토리에 생성합니다. 생성된 컴포넌트는 검수 후 프로젝트의 실제 `src/` 디렉토리로 복사하여 즉시 사용할 수 있습니다.

**핵심 원칙**:
- **컴포넌트 기반 출력** — 프로젝트의 기술 스택(React/Vue/Angular/Svelte)에 맞는 실제 컴포넌트 코드 생성
- **`publish/` 스테이징 구조** — 검수 후 `src/`로 복사 가능한 명확한 매핑 제공 (`COPY-GUIDE.md`)
- **Vibe Coding 디자인 가이드 준수** — `$CLAUDE_PLUGIN_ROOT/docs/ux/vibe-coding-design-guide.md` 기반 프로덕션급 디자인
- **Vibe Coding 애니메이션 가이드 준수** — `$CLAUDE_PLUGIN_ROOT/docs/ux/vibe-coding-animation-guide.md` 기반 모션 디자인
- **`/frontend-design` 스킬 연동** — 개성 있고 세련된 프로덕션급 UI 디자인 (AI 슬롭 방지)
- **`fect-image` MCP 도구 활용** — 히어로 이미지, 빈 상태 일러스트, 배경 등 AI 생성 이미지 에셋
- **`ux-interaction-patterns.md` 기반 인터랙션** — 화면 유형별 맞춤 마이크로 인터랙션, 전환 효과, 폼 패턴
- 프로젝트의 `src/styles/design-tokens.css`를 반드시 참조 (하드코딩 금지)
- `docs/design-system/components.md`의 컴포넌트 스펙을 준수
- `docs/design-system/layout-grid.md`의 레이아웃 시스템을 적용
- 반응형 (모바일/태블릿/데스크톱) 지원
- 다크 모드 지원
- **브라우저 프리뷰 제공** — `publish/{feature-name}/preview/`에 빌드 없이 확인 가능한 HTML 프리뷰 포함

**생성물 위치**: `publish/{feature-name}/`

**디자인 품질 기준** (Vibe Coding 디자인 가이드 기반):
- 단순한 와이어프레임 변환이 아닌, 실제 서비스처럼 보이는 프로덕션급 UI
- Anti-AI 미학: 제네릭한 AI 생성 느낌을 배제하는 의도적 디자인 선택
- 레퍼런스 앵커링: 실제 서비스의 디자인 패턴 참조
- 디자인 토큰 기반 일관된 시각 언어 (Primitive → Semantic → Component 3-tier)
- 화면 유형에 최적화된 UX 인터랙션 패턴 적용

**애니메이션 품질 기준** (Vibe Coding 애니메이션 가이드 기반):
- 스프링 물리학 기반 자연스러운 모션 (CSS `linear()` 또는 프레임워크 spring)
- 마이크로 인터랙션: 버튼 피드백, 스켈레톤, 토스트, 토글
- 스크롤 기반 애니메이션: 패럴랙스, 진입 효과, 진행률 표시
- 페이지 전환: View Transitions API 또는 프레임워크 전환 라이브러리
- 접근성: 3-tier 모션 접근성 (full/reduced/none)
- 성능: GPU 가속 속성(transform, opacity) 우선, `will-change` 최적화

> **LANGUAGE RULE**: Before executing this skill, read the project's `CLAUDE.md` and check the `## Language` section to detect the project language. If the project language is NOT Korean (`ko`), you MUST translate ALL user-facing output — including component labels, placeholder text, navigation text — into the project language. Technical identifiers (file paths, CSS variable names, class names) remain untranslated. If no `CLAUDE.md` exists or no `## Language` section is found, default to Korean.

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
## UX 컴포넌트 퍼블리싱

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

#### D. 프로젝트 컨텍스트 및 기술 스택 분석

1. `CLAUDE.md` 읽기 — 프로젝트명, 기술 스택, 디자인 시스템 선택사항 확인
2. **기술 스택 감지** — 프로젝트의 프레임워크를 판별하여 `{FRAMEWORK}`를 결정한다:

| 감지 기준 | 프레임워크 | 컴포넌트 확장자 | 스타일 방식 |
|-----------|-----------|----------------|-----------|
| `package.json`에 `react` | React (TSX) | `.tsx` | CSS Modules / Tailwind / styled-components |
| `package.json`에 `next` | Next.js (TSX) | `.tsx` | CSS Modules / Tailwind |
| `package.json`에 `vue` | Vue (SFC) | `.vue` | `<style scoped>` / Tailwind |
| `package.json`에 `nuxt` | Nuxt (Vue SFC) | `.vue` | `<style scoped>` / Tailwind |
| `package.json`에 `@angular/core` | Angular | `.ts` + `.html` + `.scss` | Component SCSS |
| `package.json`에 `svelte` | Svelte | `.svelte` | `<style>` / Tailwind |
| `package.json`에 `react-native` 또는 `expo` | React Native | `.tsx` | `StyleSheet.create()` / NativeWind |
| 감지 실패 | `AskUserQuestion`으로 선택 요청 | - | - |

3. **스타일링 방식 감지** — `{STYLE_METHOD}`를 결정한다:
   - `tailwind.config.*` 존재 → Tailwind CSS
   - `*.module.css` 패턴 사용 → CSS Modules
   - `styled-components` / `@emotion` 의존성 → CSS-in-JS
   - `.scss` 파일 패턴 → SCSS Modules
   - 기본값: CSS Modules

4. **기존 컴포넌트 구조 분석** — `src/components/` 하위 디렉토리 패턴을 파악한다:
   - 디렉토리 구조 (flat / grouped by feature / atomic design)
   - 네이밍 컨벤션 (PascalCase / kebab-case)
   - import 패턴 (barrel exports / direct imports)
   - 기존 공통 컴포넌트 목록 (중복 생성 방지)

5. `publish/` 디렉토리 스캔 — 기존 퍼블리싱 결과 확인 (중복 방지)

#### E. UX/디자인 가이드 로드

다음 가이드 파일들을 순서대로 로드한다:

##### E-1. Vibe Coding 디자인 가이드 (필수)

`$CLAUDE_PLUGIN_ROOT/docs/ux/vibe-coding-design-guide.md` 파일을 읽어 디자인 레퍼런스를 로드한다. 파일이 존재하지 않으면 "⚠️ Vibe Coding 디자인 가이드 파일이 없습니다. 플러그인을 최신 버전으로 업데이트해 주세요." 경고를 출력하고, 가이드 없이 진행한다.

이 가이드는 Vibe Coding 전문가들의 디자인 접근법을 정의한다:
- Anti-AI 미학 프롬프팅 (제네릭 AI 슬롭 방지)
- 레퍼런스 앵커 프롬프팅 (실제 서비스 디자인 참조)
- 제약 우선 프롬프팅 (금지 규칙으로 품질 보장)
- 레이어드 온이언 프롬프팅 (구조→스타일→인터랙션 단계적 적용)
- 디자인 토큰 주입 프롬프팅 (일관된 시각 언어)
- 도구별 특성 (v0, Bolt.new, Lovable, Cursor, Claude Code 등)

컴포넌트 생성 시 이 가이드의 프롬프팅 원칙과 DO/DON'T 규칙을 준수한다.

##### E-2. Vibe Coding 애니메이션 가이드 (필수)

`$CLAUDE_PLUGIN_ROOT/docs/ux/vibe-coding-animation-guide.md` 파일을 읽어 애니메이션 레퍼런스를 로드한다. 파일이 존재하지 않으면 "⚠️ Vibe Coding 애니메이션 가이드 파일이 없습니다. 플러그인을 최신 버전으로 업데이트해 주세요." 경고를 출력하고, 가이드 없이 진행한다.

이 가이드는 프로덕션급 애니메이션 구현 방법을 정의한다:
- CSS 네이티브: View Transitions API, Scroll-Driven Animations, `@starting-style`, `linear()` 스프링
- 프레임워크별: Framer Motion (React), Vue Transition, Angular Animations, Svelte transitions
- 마이크로 인터랙션: 버튼 피드백, 스켈레톤, 토스트, 토글, 아코디언
- 스크롤 기반: 패럴랙스, reveal, 진행률, sticky 헤더
- 페이지 전환: SPA 라우트 전환, 공유 요소 전환
- 성능 최적화: GPU 가속, `will-change`, `contain`
- 접근성: 3-tier 모션 접근성 (`prefers-reduced-motion`)
- 디자인 원칙: Disney 12원칙의 UI 적용, 타이밍 가이드라인, 이징 커브

컴포넌트 생성 시 `{FRAMEWORK}`에 적합한 애니메이션 구현 방식을 선택하여 적용한다.

##### E-3. UX 인터랙션 패턴 가이드 (필수)

`$CLAUDE_PLUGIN_ROOT/docs/ux/ux-interaction-patterns.md` 파일을 읽어 인터랙션 패턴 레퍼런스를 로드한다. 파일이 존재하지 않으면 "⚠️ UX 인터랙션 패턴 가이드 파일이 없습니다. 플러그인을 최신 버전으로 업데이트해 주세요." 경고를 출력하고, 가이드 없이 진행한다.

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

각 컴포넌트 생성 시, **화면 유형과 사용자 시나리오에 맞는 인터랙션 패턴**을 선택하여 구현한다.

##### E-4. 모바일 디자인 가이드 로드 (모바일 프로젝트만)

프로젝트의 `CLAUDE.md`에서 기술 스택이 모바일(React Native, Expo, Flutter, Swift, Kotlin 등)인 경우에만 실행한다.

`$CLAUDE_PLUGIN_ROOT/docs/ux/mobile-design-guide.md` 파일을 읽어 모바일 디자인 레퍼런스를 로드한다. (플랫폼 가이드라인, 터치 인터랙션, 네비게이션, 햅틱 피드백 등 14개 섹션)

#### F. 디자인 방향성 선택

`AskUserQuestion`으로 프로토타입의 미학적 방향을 선택한다:

```
## UX 컴포넌트 디자인 방향

컴포넌트의 디자인 톤을 선택하세요.
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

선택된 디자인 톤을 `{DESIGN_TONE}`으로 저장한다.

#### G. 생성 범위 확인

`ia-screen-design.md`에서 추출한 화면 목록을 사용자에게 보여주고 생성 범위를 확인한다:

```
## UX 컴포넌트 생성 범위 확인

다음 화면들의 컴포넌트를 생성합니다.
프레임워크: {FRAMEWORK} | 스타일: {STYLE_METHOD}

| # | 화면ID | 화면명 | 유형 | 관련 UC |
|---|--------|--------|------|--------|
| 1 | SCR-001 | {화면명} | {유형} | UC-001 |
| 2 | SCR-002 | {화면명} | {유형} | UC-002 |

생성할 화면 번호를 선택하세요 (전체: all, 선택: 1,3,5):
```

선택된 화면들을 `{SELECTED_SCREENS}` 배열로 저장한다.

---

### Step 1: 공통 리소스 및 공통 컴포넌트 생성

#### A. 디렉토리 구조 생성

`publish/{feature-name}/` 디렉토리를 생성한다. `{feature-name}`은 기획 디렉토리의 피처명에서 추출한다 (예: `001-auth` → `auth`).

```
publish/{feature-name}/
├── COPY-GUIDE.md               # 복사 가이드: 각 파일의 실제 프로젝트 위치 매핑
├── components/                  # 재사용 가능한 UI 컴포넌트
│   ├── common/                  # 공통 UI 컴포넌트
│   │   ├── Button.{ext}         # Primary/Secondary/Danger/Ghost
│   │   ├── Input.{ext}          # 플로팅 라벨, 유효성 검사
│   │   ├── Card.{ext}           # Default/Elevated/Outlined/Interactive
│   │   ├── Modal.{ext}          # 백드롭, 포커스 트랩
│   │   ├── Table.{ext}          # 정렬, 반응형, 시머 로딩
│   │   ├── Toast.{ext}          # 슬라이드 인/아웃, 프로그레스 바
│   │   ├── Badge.{ext}          # 상태별 색상, 펄스
│   │   ├── Skeleton.{ext}       # 시머 효과 로딩
│   │   ├── Toggle.{ext}         # 슬라이드 전환
│   │   └── index.{ts|js}        # barrel export
│   ├── layout/                  # 레이아웃 컴포넌트
│   │   ├── GNB.{ext}            # 글로벌 네비게이션 바
│   │   ├── Sidebar.{ext}        # 사이드바 (접기/펼치기)
│   │   ├── PageLayout.{ext}     # GNB + Sidebar + Content 조합
│   │   └── index.{ts|js}        # barrel export
│   └── {feature}/               # 기능 전용 컴포넌트 (화면 분석 후 결정)
│       └── ...
├── screens/                     # 화면(페이지) 컴포넌트
│   ├── {ScreenName}Screen.{ext} # 각 화면별 페이지 컴포넌트
│   └── ...
├── hooks/                       # 커스텀 훅 (React/Vue Composable)
│   ├── useScrollAnimation.{ts}  # 스크롤 기반 애니메이션
│   ├── useFloatingLabel.{ts}    # 플로팅 라벨
│   ├── useIntersectionObserver.{ts} # Intersection Observer
│   ├── useTheme.{ts}            # 다크모드 전환
│   └── index.{ts|js}            # barrel export
├── styles/                      # 스타일 파일
│   ├── tokens.css               # 디자인 토큰 (프로젝트에서 복사)
│   ├── base.css                 # 베이스/리셋 스타일
│   ├── animations.css           # 공통 애니메이션 키프레임
│   └── {component}.module.css   # 컴포넌트별 CSS 모듈 (CSS Modules 방식일 때)
├── utils/                       # 유틸리티
│   ├── cn.{ts}                  # 클래스명 병합 유틸 (clsx/cn)
│   └── constants.{ts}           # 상수 (애니메이션 타이밍 등)
├── assets/                      # 정적 에셋
│   └── images/                  # AI 생성 이미지
│       ├── hero-*.webp
│       ├── empty-*.webp
│       └── ...
└── preview/                     # HTML 프리뷰 (브라우저에서 확인용)
    ├── index.html               # 화면 인덱스 (네비게이션 허브)
    └── screens/                 # 개별 화면 프리뷰
        └── {screen-id}.html
```

> **`{ext}` 결정**: `{FRAMEWORK}`에 따라 확장자가 결정된다.
> - React/Next.js: `.tsx`
> - Vue/Nuxt: `.vue`
> - Angular: `.component.ts` + `.component.html` + `.component.scss`
> - Svelte: `.svelte`
> - React Native: `.tsx`

#### B. 디자인 토큰 복사

`publish/{feature-name}/styles/tokens.css` — 프로젝트의 `src/styles/design-tokens.css`를 **그대로 복사**한다. 수정하지 않는다.

#### C. 베이스 스타일 생성

`publish/{feature-name}/styles/base.css` — 디자인 토큰을 참조하는 기본 레이아웃 스타일을 생성한다. `docs/design-system/layout-grid.md`의 규칙을 CSS로 구현한다.

포함 내용:
- CSS Reset (box-sizing, margin, padding)
- 기본 폰트, 색상, 배경 (디자인 토큰 `var(--*)` 참조)
- Container, Grid System (12-column responsive)
- 반응형 breakpoint 유틸리티
- 섹션/페이지 헤더 기본 스타일

#### D. 애니메이션 CSS 생성

`publish/{feature-name}/styles/animations.css` — Vibe Coding 애니메이션 가이드 + UX 인터랙션 패턴 가이드에서 추출한 공통 애니메이션을 생성한다.

**애니메이션 가이드 기반 구현**:

```css
/* animations.css — Vibe Coding 애니메이션 가이드 + UX 인터랙션 패턴 기반 */

/* === 스프링 물리학 이징 (애니메이션 가이드 §5) === */
:root {
  --spring-bounce: linear(0, 0.004, 0.016, 0.035, 0.063, 0.098, 0.141, 0.191, 0.25, 0.316,
    0.391, 0.474, 0.562, 0.654, 0.75, 0.847, 0.941, 1.031, 1.115, 1.191,
    1.259, 1.316, 1.362, 1.395, 1.416, 1.424, 1.42, 1.405, 1.382, 1.351,
    1.316, 1.279, 1.241, 1.207, 1.176, 1.15, 1.13, 1.114, 1.103, 1.096,
    1.091, 1.089, 1.088, 1.089, 1.091, 1.093, 1.096, 1.099, 1.101, 1.102,
    1.103, 1.103, 1.102, 1.101, 1.1, 1.099, 1.098, 1.097, 1.096, 1);
  --spring-smooth: linear(0, 0.002, 0.01, 0.022, 0.04, 0.064, 0.094, 0.131, 0.176, 0.228,
    0.289, 0.357, 0.435, 0.519, 0.609, 0.701, 0.793, 0.878, 0.952, 1.013,
    1.058, 1.088, 1.104, 1.107, 1.1, 1.086, 1.067, 1.046, 1.024, 1.004,
    0.988, 0.976, 0.969, 0.966, 0.966, 0.969, 0.974, 0.981, 0.988, 0.994,
    0.999, 1.002, 1.004, 1.004, 1.003, 1.002, 1.001, 1, 1, 1);
}

/* === 마이크로 인터랙션 — 버튼 피드백 (인터랙션 1.1) === */
.btn { touch-action: manipulation; }
.btn:active { transform: scale(0.95); transition: transform 150ms ease; }

/* Ripple Effect */
.ripple { position: relative; overflow: hidden; }
.ripple::after {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(circle, rgba(255,255,255,0.3) 10%, transparent 70%);
  transform: scale(0); opacity: 0;
  transition: transform 400ms ease, opacity 400ms ease;
}
.ripple:active::after { transform: scale(2.5); opacity: 1; transition: 0ms; }

/* === 스켈레톤 시머 (인터랙션 3.2) === */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.skeleton {
  background: linear-gradient(90deg,
    var(--color-bg-tertiary) 25%,
    var(--color-bg-secondary) 50%,
    var(--color-bg-tertiary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-md);
}

/* === 스크롤 트리거 — Fade In Up (인터랙션 5.4) === */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-on-scroll {
  opacity: 0;
  animation: fadeInUp 0.6s var(--spring-smooth) forwards;
}
/* 시차 등장 (인터랙션 7.5) */
.stagger-1 { animation-delay: 50ms; }
.stagger-2 { animation-delay: 100ms; }
.stagger-3 { animation-delay: 150ms; }
.stagger-4 { animation-delay: 200ms; }
.stagger-5 { animation-delay: 250ms; }

/* === 카운터 애니메이션 (인터랙션 1.6) === */
@keyframes countUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.counter-animate { animation: countUp 0.4s var(--spring-smooth) forwards; }

/* === 페이지 전환 (인터랙션 7.1, 애니메이션 가이드 §12) === */
@keyframes slideInFromRight {
  from { opacity: 0; transform: translateX(30px); }
  to { opacity: 1; transform: translateX(0); }
}
.page-enter { animation: slideInFromRight 0.3s var(--spring-smooth); }

/* === @starting-style 기반 진입 애니메이션 (애니메이션 가이드 §3) === */
/* dialog, popover 등에 적용 */

/* === 토글 애니메이션 (인터랙션 1.2) === */
.toggle { transition: background-color 250ms cubic-bezier(0.4, 0, 0.2, 1); }
.toggle-thumb { transition: transform 250ms cubic-bezier(0.4, 0, 0.2, 1); }

/* === 빈 상태 (인터랙션 8.4) === */
.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: var(--spacing-16) var(--spacing-6);
  text-align: center;
}

/* === 3-tier 모션 접근성 (애니메이션 가이드 §16) === */
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

위 CSS는 기본 템플릿이다. 프로젝트의 Vibe Coding 애니메이션 가이드 참조 내용 + `layout-grid.md` 내용에 맞게 실제 값을 조정한다. 프레임워크에서 제공하는 애니메이션 라이브러리(Framer Motion, Vue Transition 등)가 있으면 CSS 키프레임 대신 해당 라이브러리를 활용한다.

#### E. 공통 UI 컴포넌트 생성

`publish/{feature-name}/components/common/` — 프로젝트 프레임워크에 맞는 **실제 사용 가능한** 공통 컴포넌트를 생성한다.

> **`/frontend-design` 연동**: `frontend-design` 스킬이 설치되어 있으면 `Skill` 도구로 호출하여 프로덕션급 디자인을 생성한다. 설치되어 있지 않으면 아래 요구사항을 직접 구현한다.

생성할 컴포넌트 (프레임워크별 적절한 패턴으로 구현):

| 컴포넌트 | Props/API | 인터랙션 |
|---------|----------|---------|
| Button | variant, size, loading, disabled, onClick | 눌림 효과(scale 0.95), ripple, 로딩 스피너 |
| Input | label, error, success, helperText, type | 플로팅 라벨, 인라인 유효성, 포커스 링 |
| Card | variant(default/elevated/outlined/interactive), onClick | hover lift, shadow 전환 |
| Modal | isOpen, onClose, title, children | 백드롭 fade, slide-up, 포커스 트랩, ESC 닫기 |
| Table | columns, data, sortable, loading | 호버, 반응형(모바일 카드), 시머 로딩 |
| Toast | message, type(success/error/info), duration | 슬라이드 인/아웃, 프로그레스 바 |
| Badge | variant(status colors), pulse | 상태 색상, 펄스 애니메이션 |
| Skeleton | width, height, variant(text/circle/rect) | 시머 효과 |
| Toggle | checked, onChange, label | 슬라이드 전환, 색상 변화 |

**컴포넌트 구현 규칙**:

1. **Vibe Coding 디자인 가이드 준수**:
   - Anti-AI 미학: 제네릭한 디자인 배제, 의도적 디테일 추가
   - `{DESIGN_TONE}`에 맞는 미학적 디테일 (그라디언트, 텍스처, 애니메이션)
   - 디자인 토큰만 사용 (`var(--*)` 또는 Tailwind 토큰)

2. **Vibe Coding 애니메이션 가이드 준수**:
   - 스프링 물리학 기반 이징 (CSS `linear()` 또는 프레임워크 spring)
   - GPU 가속 속성 우선 (transform, opacity)
   - `prefers-reduced-motion` 대응 필수

3. **프레임워크 네이티브 패턴 사용**:
   - React: FC + TypeScript interface + forwardRef (필요 시)
   - Vue: `<script setup>` + `defineProps` + `defineEmits`
   - Angular: standalone component + `@Input()` + `@Output()`
   - Svelte: `export let` props + slot

4. **스타일링은 `{STYLE_METHOD}`를 따른다**:
   - CSS Modules: `{Component}.module.css` + `styles` import
   - Tailwind: className 직접 작성 + `cn()` 유틸
   - styled-components: 컴포넌트 내 styled 정의
   - SCSS: `{Component}.module.scss`

5. **기존 프로젝트 컴포넌트와 중복 방지**:
   - Step 0.D에서 파악한 기존 공통 컴포넌트가 있으면 해당 컴포넌트를 import하여 사용
   - 새로 생성하는 컴포넌트만 `components/common/`에 배치
   - `COPY-GUIDE.md`에 기존 컴포넌트 재사용 안내 포함

6. **접근성 필수**:
   - 시맨틱 HTML 요소 사용
   - ARIA 속성
   - `focus-visible` 포커스 링
   - 충분한 터치 타겟 (44px)

#### F. 레이아웃 컴포넌트 생성

`publish/{feature-name}/components/layout/` — GNB, Sidebar, PageLayout 컴포넌트를 생성한다.

| 컴포넌트 | 역할 | 인터랙션 |
|---------|------|---------|
| GNB | 고정 헤더 (64px), 로고, 사용자, 다크모드 토글 | 스크롤 시 축소/그림자, show-on-scroll-up |
| Sidebar | 좌측 네비게이션, IA 메뉴 구조 반영 | 접기/펼치기 애니메이션, 모바일 오버레이 |
| PageLayout | GNB + Sidebar + Content 조합 | 반응형 레이아웃 전환 |

레이아웃 컴포넌트는 `docs/design-system/layout-grid.md` 규칙을 구현한다:
- 데스크톱: 사이드바 240px + 12열 콘텐츠
- 태블릿: 사이드바 64px (아이콘만) + 콘텐츠
- 모바일: 사이드바 숨김 (오버레이) + 풀 콘텐츠

#### G. 커스텀 훅/유틸 생성

프레임워크에 맞는 커스텀 훅(React hooks / Vue composables / Angular services)을 생성한다:

| 훅/유틸 | 용도 | 기반 가이드 |
|--------|------|-----------|
| `useScrollAnimation` | Intersection Observer 기반 스크롤 트리거 | 인터랙션 5.4, 애니메이션 §11 |
| `useFloatingLabel` | 입력 필드 플로팅 라벨 | 인터랙션 6.2 |
| `useIntersectionObserver` | 범용 IO 훅 | 애니메이션 §11 |
| `useTheme` | 다크모드 전환 (localStorage) | - |
| `useCountUp` | 숫자 카운터 애니메이션 | 인터랙션 1.6 |
| `cn` (유틸) | 클래스명 병합 | - |

> **React Native 프로젝트**: 웹 훅 대신 `useAnimatedStyle`, `useSharedValue` (Reanimated), `Animated.spring` 등 네이티브 애니메이션 훅을 생성한다.

#### H. AI 이미지 에셋 생성 (fect-image 적극 활용)

> **필수**: `mcp__fect-image__image_text2img` 도구를 **적극적으로 활용**하여 세련되고 고급지며 가독성 높은 트렌디한 디자인을 구현한다. 이미지는 프로토타입의 완성도를 결정하는 핵심 요소이다. CSS 그라디언트/SVG 플레이스홀더는 fect-image가 완전히 불가능한 경우에만 최후 수단으로 사용한다.

`publish/{feature-name}/assets/images/`에 프로토타입에 필요한 **모든 비주얼 에셋**을 생성한다.

##### H-1. 디자인 톤별 이미지 스타일 가이드

`{DESIGN_TONE}`에 따라 이미지 프롬프트의 스타일 키워드를 결정한다:

| 디자인 톤 | 스타일 키워드 | 색상 팔레트 | 분위기 |
|-----------|------------|-----------|--------|
| Refined Minimal | "clean lines, generous whitespace, monochromatic palette, Swiss design, editorial photography style, subtle grain texture" | 모노크롬 + 단일 액센트 | 정제된, 차분한 |
| Bold & Vibrant | "vivid saturated colors, dynamic composition, energetic gradients, bold geometric shapes, pop art influence, high contrast" | 고채도 대비 팔레트 | 역동적, 강렬한 |
| Soft & Warm | "soft pastels, organic shapes, warm golden light, watercolor texture, rounded corners, cozy atmosphere, hand-drawn feel" | 파스텔 + 웜톤 | 친근한, 부드러운 |
| Editorial | "magazine layout, dramatic typography contrast, asymmetric grid, editorial photography, high fashion aesthetic, noir influence" | 흑백 + 강렬한 액센트 | 세련된, 대담한 |
| Professional Enterprise | "corporate clean, trustworthy blue tones, isometric 3D icons, data visualization aesthetic, structured grid, professional photography" | 블루 + 뉴트럴 | 신뢰감, 안정적 |

##### H-2. 이미지 카테고리별 프롬프트 패턴

| 카테고리 | 프롬프트 패턴 | 비율 | 저장 경로 | 생성 조건 |
|---------|------------|------|---------|----------|
| **히어로 배너** | "Premium hero banner for {기능 설명}, {스타일 키워드}, ultra high quality, professional web design, 8k render, no text no letters no words" | 16:9 | `hero-{name}.webp` | 대시보드, 랜딩, 메인 화면 |
| **섹션 배경** | "Abstract background texture, {스타일 키워드}, subtle pattern, seamless tileable, premium feel, no text" | 16:9 | `bg-{section}.webp` | CTA 영역, 강조 섹션 |
| **빈 상태 일러스트** | "Elegant empty state illustration for {상황}, {스타일 키워드}, centered composition, metaphorical visual, no text no letters, premium quality" | 1:1 | `empty-{name}.webp` | 목록 빈 상태, 검색 결과 없음 |
| **온보딩 일러스트** | "Onboarding step illustration showing {설명}, {스타일 키워드}, isometric or flat layered, storytelling visual, no text no letters" | 4:3 | `onboarding-{step}.webp` | 온보딩, 튜토리얼 |
| **기능 소개 아이콘** | "Feature icon illustration for {기능명}, {스타일 키워드}, detailed 3D icon style, glass morphism, gradient lighting, no text" | 1:1 | `feature-{name}.webp` | 기능 카드, KPI 카드 |
| **프로필 아바타** | "Professional portrait avatar, {성별/스타일}, modern flat illustration, {스타일 키워드}, neutral background, friendly expression" | 1:1 | `avatar-{n}.webp` | 사용자 목록, 프로필 |
| **로그인/인증 배경** | "Premium authentication page background, {스타일 키워드}, abstract flowing shapes, depth of field effect, cinematic lighting, no text" | 16:9 | `auth-bg.webp` | 로그인, 가입, 비밀번호 |
| **성공/완료 일러스트** | "Celebration success illustration, {스타일 키워드}, confetti or sparkle, achievement feeling, joyful composition, no text" | 1:1 | `success-{name}.webp` | 완료, 축하 화면 |
| **에러/경고 일러스트** | "Friendly error illustration for {상황}, {스타일 키워드}, empathetic visual, not scary, solution-oriented, no text" | 1:1 | `error-{name}.webp` | 404, 에러, 접근 제한 |
| **카드 썸네일** | "Content card thumbnail for {주제}, {스타일 키워드}, 16:9 composition, editorial quality, no text no letters" | 16:9 | `card-{name}.webp` | 콘텐츠 카드, 게시물 |
| **배지/뱃지 아이콘** | "Achievement badge icon, {스타일 키워드}, metallic sheen, premium feel, centered, no text" | 1:1 | `badge-{name}.webp` | 등급, 성취, 상태 |

##### H-3. 고급 프롬프트 작성 원칙 (Vibe Coding 디자인 가이드 기반)

프롬프트 작성 시 다음 원칙을 반드시 준수한다:

1. **Anti-AI 슬롭 방지**: 제네릭한 스톡 이미지 느낌을 배제한다
   - ❌ "modern web design banner" (너무 일반적)
   - ✅ "Bauhaus-inspired geometric composition with overlapping translucent shapes, muted earth tones with single coral accent, subtle paper grain texture" (구체적 레퍼런스)

2. **레퍼런스 앵커링**: 실제 디자인 트렌드/스타일을 구체적으로 명시한다
   - 스타일 레퍼런스: "Dribbble trending", "Behance featured", "Apple design language", "Stripe dashboard aesthetic"
   - 아트 레퍼런스: "Bauhaus", "Swiss design", "Japanese minimalism", "Scandinavian clean"

3. **제약 우선**: 원하지 않는 것을 명확히 배제한다
   - 필수 네거티브: "no text, no letters, no words, no watermark, no stock photo feel"
   - 추가 네거티브: "no generic clip art, no cheesy gradients, no oversaturated"

4. **계층적 디테일**: 구도 → 색상 → 질감 → 조명 순서로 프롬프트를 구성한다
   - 예: "[구도] centered isometric composition → [색상] deep navy and warm amber palette → [질감] subtle noise grain overlay → [조명] soft diffused top-right lighting"

5. **일관된 시각 언어**: 같은 프로젝트 내 모든 이미지는 동일한 스타일 키워드 세트를 공유한다

##### H-4. 이미지 생성 실행 규칙

1. **화면 분석 기반 선별 생성**: `ia-screen-design.md`의 와이어프레임을 분석하여 이미지가 필요한 위치를 식별한다. 각 화면의 히어로, 카드 썸네일, 빈 상태, 아바타 등 **실제 UI에 배치될 이미지만** 생성한다.
2. **최소 생성 기준**: 프로젝트당 최소 다음 이미지를 생성한다:
   - 히어로/배너 1~2개 (메인 화면용)
   - 빈 상태 일러스트 2~3개 (데이터 없음, 검색 결과 없음, 첫 사용)
   - 기능 아이콘 3~5개 (주요 기능 카드용)
   - 프로필 아바타 3~4개 (더미 사용자 데이터용)
   - 인증 배경 1개 (로그인/가입 화면)
3. **모든 이미지는 `imageSize: "2K"` 사용**
4. **프롬프트는 영어로 작성** (한국어 기능명은 영어로 번역하여 사용)
5. **일관된 스타일**: 같은 프로젝트 내 모든 이미지에 동일한 `{스타일 키워드}` 세트를 적용하여 시각적 통일감을 유지한다
6. **생성 후 확인**: 이미지 파일이 정상적으로 저장되었는지 확인하고, 프리뷰 HTML에서 올바르게 참조되는지 검증한다

#### I. 완료 보고

```
✅ 공통 리소스 및 컴포넌트 생성 완료

- publish/{feature-name}/styles/ (디자인 토큰, 베이스, 애니메이션)
- publish/{feature-name}/components/common/ (공통 UI 컴포넌트 {N}개)
- publish/{feature-name}/components/layout/ (레이아웃 컴포넌트 3개)
- publish/{feature-name}/hooks/ (커스텀 훅 {N}개)
- publish/{feature-name}/assets/images/ (AI 이미지 {N}개)

프레임워크: {FRAMEWORK} | 스타일: {STYLE_METHOD}
다음 단계: 개별 화면 컴포넌트 생성을 진행합니다.
```

---

### Step 2: 화면(Screen) 컴포넌트 생성

`{SELECTED_SCREENS}` 배열의 각 화면에 대해 컴포넌트를 생성한다.

#### A. 화면 정보 추출

`ia-screen-design.md`에서 각 화면의 다음 정보를 추출한다:

1. **화면ID** (SCR-001)
2. **화면명**
3. **화면 유형** (목록/상세/폼/모달/대시보드)
4. **와이어프레임** (ASCII 아트 구조)
5. **UI 요소 설명** (요소명, 유형, 설명, 동작)
6. **관련 UC 및 FR**

`feature-definition.md`에서 비즈니스 규칙, `usecase-definition.md`에서 상호작용 흐름을 추출한다.

#### B. 화면 유형별 인터랙션 패턴 매핑

화면 유형에 따라 적용할 인터랙션 패턴을 결정한다:

| 화면 유형 | 필수 인터랙션 패턴 | 애니메이션 가이드 참조 |
|-----------|-----------------|-------------------|
| 목록 (List) | 스켈레톤 로딩(3.2), 고정 헤더(5.3), 스크롤 트리거(5.4), 시차 등장(7.5), 빈 상태(8.4) | §11 스크롤 기반, §8 마이크로인터랙션 |
| 상세 (Detail) | 탭 전환(2.6), 스크롤 트리거(5.4), 브레드크럼(2.4), 페이지 전환(7.1) | §12 페이지 전환 |
| 폼 (Form) | 인라인 유효성(6.1), 플로팅 라벨(6.2), 입력 마스크(6.6), 스마트 기본값(6.4) | §8 폼 마이크로인터랙션 |
| 모달 (Modal) | 포커스 트랩(9.2), slide-up 전환(7.1), 백드롭 fade | §3 @starting-style |
| 대시보드 (Dashboard) | 카운터 애니메이션(1.6), 시차 등장(7.5), 스켈레톤(3.2) | §8 카운터, §10 stagger |
| 설정 (Settings) | 토글 애니메이션(1.2), 탭 전환(2.6), 토스트(3.5) | §8 토글 |
| 로그인/가입 (Auth) | 플로팅 라벨(6.2), 인라인 유효성(6.1), 버튼 로딩(1.3) | §12 페이지 전환 |
| 온보딩 (Onboarding) | 점진적 공개(8.1), 코치 마크(8.3), 스크롤 스냅(5.5) | §2 Scroll-Driven |
| 랜딩 (Landing) | 패럴랙스(5.1), 스크롤 트리거(5.4), 시차 등장(7.5), 카운터(1.6), 스크롤 스냅(5.5), 스크롤 진행률(5.4) | §2 Scroll-Driven, §11 스크롤 기반, §12 페이지 전환 |

**모든 화면 공통**:
- 버튼 피드백(1.1): scale(0.95) + ripple
- 토스트(3.5): 성공/실패 피드백
- 모션 감소 대응(9.3): `prefers-reduced-motion`
- 포커스 관리(9.2): `focus-visible`
- 터치 타겟(9.5): 최소 44px

**화면 유형별 애니메이션 구현 세부 지침** (Vibe Coding 애니메이션 가이드 기반):

| 화면 유형 | 진입 애니메이션 | 인터랙션 애니메이션 | 전환 애니메이션 |
|-----------|--------------|-------------------|---------------|
| 목록 (List) | 행 시차 등장 (stagger 50ms), 스켈레톤→콘텐츠 fade | 행 호버 하이라이트, 스와이프 액션 | 필터/정렬 시 레이아웃 morph |
| 상세 (Detail) | 히어로 이미지 scale-in, 콘텐츠 cascade fadeInUp | 이미지 줌, 탭 슬라이드 전환 | 목록↔상세 공유 요소 전환 |
| 폼 (Form) | 필드 순차 등장 (stagger 80ms) | 플로팅 라벨 rise, 유효성 shake, 포커스 glow | 단계별 슬라이드 전환 |
| 대시보드 | KPI 카운터 rollup, 카드 시차 등장 | 차트 호버 tooltips, 카드 hover lift | 기간 전환 시 차트 morph |
| 설정 | 섹션 accordion 펼침 | 토글 슬라이드, 선택 체크 bounce | 저장 성공 pulse |
| 로그인/가입 | 폼 center-in + 배경 패럴랙스 | 입력 포커스 glow, 소셜 버튼 hover scale | 로그인→대시보드 페이지 전환 |
| **랜딩** | 히어로 cinematic reveal (scale+fade), 섹션별 cascade fadeInUp, 숫자 카운터 rollup, 로고/파트너 infinite scroll | 패럴랙스 레이어(3~5단계), CTA 버튼 pulse+glow, 카드 hover 3D tilt, 이미지 reveal mask | 스크롤 스냅 섹션 전환, 스크롤 진행률 바, sticky 헤더 축소 |

**프레임워크별 애니메이션 라이브러리 설치 및 구현 방식**:

> **필수**: 애니메이션 구현에 필요한 라이브러리가 프로젝트에 설치되어 있지 않으면 **즉시 설치**한 후 진행한다. `package.json`을 확인하여 미설치 시 `Bash`로 설치 명령을 실행한다.

| 프레임워크 | 필수 라이브러리 | 설치 명령 | 주요 API |
|-----------|--------------|----------|---------|
| **React/Next.js** | `framer-motion` | `npm install framer-motion` | `motion.div`, `AnimatePresence`, `useScroll`, `useInView`, `useSpring` |
| **Vue/Nuxt** | `@vueuse/motion` | `npm install @vueuse/motion` | `v-motion` 디렉티브, `useMotion`, 빌트인 `<Transition>`, `<TransitionGroup>` |
| **Angular** | `@angular/animations` | `ng add @angular/animations` (보통 기본 포함) | `trigger`, `transition`, `animate`, `query`, `stagger` |
| **Svelte** | (빌트인) | 추가 설치 불필요 | `svelte/transition`, `svelte/motion` (`spring`, `tweened`), `svelte/animate` |
| **React Native** | `react-native-reanimated`, `react-native-gesture-handler` | `npx expo install react-native-reanimated react-native-gesture-handler` | `useAnimatedStyle`, `withSpring`, `withTiming`, `useSharedValue` |

**라이브러리 설치 절차**:
1. `package.json`에서 해당 라이브러리의 설치 여부를 확인한다
2. 미설치 시 `Bash` 도구로 설치 명령을 실행한다 (프로젝트의 패키지 매니저에 맞게: `npm`, `yarn`, `pnpm`, `bun`)
3. 필요 시 프레임워크 설정 파일을 업데이트한다 (예: React Native의 `babel.config.js`에 reanimated 플러그인 추가)
4. 설치 완료 후 해당 라이브러리의 API를 사용하여 애니메이션을 구현한다
5. **CSS만으로도 가능한 간단한 애니메이션**(hover, transition, keyframe)은 라이브러리 없이 구현하되, **복잡한 제스처/스프링/시퀀스/공유 요소 전환**은 반드시 라이브러리를 활용한다

**공통 CSS 네이티브 (라이브러리 보조)**:
- `@starting-style`: dialog/popover 진입 애니메이션
- View Transitions API: 페이지 전환 (Next.js `unstable_ViewTransition` 등)
- Scroll-Driven Animations: 스크롤 연동 (`animation-timeline: scroll()`)
- CSS `linear()` 스프링: 커스텀 스프링 이징

**화면별 AI 이미지 연동 지침**:
- 화면 구성 분석 중 이미지가 필요한 UI 영역(히어로, 카드, 빈 상태, 아바타 등)을 식별한다
- Step 1.H에서 미리 생성한 이미지가 있으면 해당 이미지를 참조한다
- **부족한 이미지는 즉시 `mcp__fect-image__image_text2img`로 추가 생성**한다 (Step 1.H의 프롬프트 원칙 적용)
- 이미지 로딩 시 항상 블러 플레이스홀더 또는 스켈레톤을 표시한다 (CLS 방지)

#### C. 화면 컴포넌트 생성

각 화면에 대해 `publish/{feature-name}/screens/{ScreenName}Screen.{ext}` 컴포넌트를 생성한다.

**컴포넌트 생성 규칙**:

1. **공통 컴포넌트 재사용** — Step 1에서 생성한 `components/common/`, `components/layout/` 컴포넌트를 import하여 조합
2. **기능 전용 컴포넌트 분리** — 화면 분석 중 특정 기능에서만 사용하는 복잡한 UI가 있으면 `components/{feature}/`에 별도 컴포넌트로 분리
3. **와이어프레임 완전 구현** — ASCII 와이어프레임의 모든 UI 요소를 실제 컴포넌트로 변환
4. **사실적 더미 데이터** — 테이블 5~10행, 카드 3~6개, 폼 placeholder, KPI 수치
5. **AI 이미지 적극 활용** (fect-image 필수):
   - 히어로/배너 영역: Step 1.H에서 생성한 `assets/images/hero-*.webp` 적용
   - 빈 상태: AI 일러스트 (`empty-*.webp`) + 설명 + CTA
   - 카드 썸네일: AI 이미지 (`card-*.webp`) 또는 기능 아이콘 (`feature-*.webp`) 적용
   - 프로필 영역: AI 아바타 (`avatar-*.webp`) 적용
   - 인증 배경: AI 배경 (`auth-bg.webp`) 적용
   - **화면 분석 중 추가 이미지가 필요하면** 즉시 `mcp__fect-image__image_text2img`로 생성하여 `assets/images/`에 저장
6. **상태(State) 표현 포함**:
   - 빈 상태: AI 일러스트 + 설명 + CTA (플레이스홀더 절대 금지, 반드시 fect-image로 생성)
   - 로딩 상태: Skeleton 컴포넌트 + 시머 애니메이션
   - 에러 상태: AI 에러 일러스트 + 인라인 유효성 + 에러 메시지
   - 성공 피드백: Toast 컴포넌트 + 성공 애니메이션 (축하 일러스트 포함 가능)
7. **Vibe Coding 디자인 가이드 필수 적용**:
   - Anti-AI 미학: 제네릭한 AI 슬롭을 배제하는 의도적 디자인 선택
   - 레퍼런스 앵커링: 화면 유형에 맞는 실제 서비스 디자인 패턴 참조
   - 디자인 토큰 전용: 모든 색상/타이포/스페이싱은 `var(--*)` 또는 Tailwind 토큰만 사용
   - `{DESIGN_TONE}`에 맞는 시각적 디테일 (그라디언트, 텍스처, 그림자, 보더)
   - 폰트 계층 구조: 제목/본문/캡션 간 명확한 크기+무게 대비
   - 색상 대비: 정보 계층에 맞는 의도적 색상 사용 (강조/일반/보조)
8. **Vibe Coding 애니메이션 가이드 필수 적용**:
   - **모든 화면**에 최소 3가지 이상의 애니메이션을 적용한다:
     - 진입 애니메이션: 페이지/섹션 등장 시 fadeInUp + 시차 등장 (stagger)
     - 인터랙션 애니메이션: 버튼 피드백(scale), 호버 효과, 포커스 링
     - 상태 전환 애니메이션: 로딩→콘텐츠, 열림/닫힘, 토글
   - 스프링 물리학 기반 이징: CSS `linear()` 스프링 또는 프레임워크 spring 함수 사용
   - GPU 가속 속성 우선: `transform`, `opacity` 위주 (layout 속성 피하기)
   - 타이밍 가이드라인: 마이크로 인터랙션 100~300ms, 페이지 전환 300~500ms, 복잡한 시퀀스 500~800ms
   - 이징 선택: 진입(ease-out/spring), 퇴장(ease-in), 강조(bounce/spring-bounce)
   - Disney 12원칙 UI 적용: Squash & Stretch(버튼 누름), Anticipation(드래그 시작), Follow Through(목록 스크롤)
   - **3-tier 모션 접근성 필수**: `prefers-reduced-motion: reduce`에서 애니메이션 비활성화
9. **반응형 레이아웃**:
   - 모바일: 1열, 사이드바 숨김, 테이블→카드 전환
   - 태블릿: 2열, 사이드바 축소
   - 데스크톱: 12열 그리드, 사이드바 확장
10. **다크 모드 대응**: 테마 전환 지원 + AI 이미지는 다크모드에서도 조화롭게 보이도록 반투명 오버레이 또는 `mix-blend-mode` 적용
11. **접근성**: 시맨틱 HTML, ARIA, focus-visible, 터치 타겟(44px), 색상 대비(4.5:1)

##### 랜딩 페이지 전용 지침 (이미지 + 애니메이션 집중 활용)

랜딩 페이지(`landing`, `home`, `main`, `marketing` 유형)는 이미지, 일러스트, 애니메이션을 **최대한 효과적으로** 활용하여 몰입감 있는 경험을 제공해야 한다. 일반 CRUD 화면보다 **비주얼 밀도가 2배 이상** 높아야 한다.

**필수 이미지 (fect-image로 모두 생성)**:
| 섹션 | 이미지 종류 | 프롬프트 가이드 |
|------|-----------|--------------|
| Hero | 풀 블리드 히어로 배너 (16:9) | "Cinematic hero banner, {기능 설명}, {스타일 키워드}, ultra wide composition, dramatic lighting, depth layers, 8k, no text no letters" |
| Features | 기능별 아이콘 일러스트 (1:1) × 3~6개 | "3D glassmorphism icon for {기능명}, {스타일 키워드}, floating on gradient, soft shadow, premium, no text" |
| Social Proof | 사용자 아바타 (1:1) × 3~5개 | "Professional portrait avatar, {다양한 인물}, {스타일 키워드}, warm friendly expression, no text" |
| CTA 배경 | 그라디언트 배경 또는 추상 이미지 (16:9) | "Abstract gradient background, {스타일 키워드}, vibrant flowing shapes, premium feel, no text" |
| 제품 스크린샷 | 앱/대시보드 목업 (16:9) | "Clean UI mockup of {화면 설명}, {스타일 키워드}, floating device frame, shadow depth, no text" |
| 파트너/로고 영역 | 로고 플레이스홀더 | CSS로 회색 로고 플레이스홀더 생성 (이미지 불필요) |

**필수 애니메이션 (Vibe Coding 애니메이션 가이드 기반)**:
1. **히어로 섹션**: cinematic reveal — 배경 이미지 slow scale(1.05→1.0, 2s) + 텍스트 cascade fadeInUp(stagger 100ms) + CTA 버튼 delayed bounce-in
2. **스크롤 기반 진입**: 각 섹션이 뷰포트에 진입할 때 fadeInUp + stagger (Intersection Observer 또는 Scroll-Driven Animations)
3. **패럴랙스 레이어**: 히어로 배경 이미지와 전경 요소 사이에 3~5단계 속도 차이
4. **숫자 카운터**: 통계/KPI 섹션에서 카운터 rollup 애니메이션 (0 → 목표값, 1.5s, ease-out)
5. **기능 카드**: hover 시 subtle 3D tilt (perspective + rotateY) + 아이콘 bounce
6. **CTA 버튼**: 지속적 pulse glow + hover scale(1.05) + click scale(0.95)
7. **이미지 reveal**: 이미지 등장 시 clip-path 또는 mask 애니메이션으로 드라마틱한 공개 효과
8. **스크롤 진행률**: 상단에 스크롤 진행률 바 (CSS Scroll-Driven 또는 JS)
9. **infinite scroll 배너**: 파트너 로고/사용자 후기를 marquee-style 무한 스크롤
10. **모션 접근성**: `prefers-reduced-motion: reduce`에서 모든 애니메이션을 opacity 전환으로 대체

**랜딩 페이지 섹션 구성 (권장 순서)**:
1. **Hero** — 풀 블리드 이미지 + 헤드라인 + 서브카피 + CTA (cinematic reveal)
2. **Social Proof Bar** — 파트너 로고/수치 infinite scroll
3. **Features** — 3~6개 기능 카드 (아이콘 + 설명) (시차 등장)
4. **Product Showcase** — 제품 스크린샷 + 하이라이트 기능 (패럴랙스 또는 스크롤 스냅)
5. **Testimonials** — 사용자 후기 카드 (아바타 + 인용문) (캐러셀 또는 그리드)
6. **Statistics** — 숫자 KPI 카운터 (카운터 rollup)
7. **CTA** — 강조 배경 + CTA 버튼 (pulse glow)
8. **Footer** — 링크 + 소셜 아이콘

**프레임워크별 화면 컴포넌트 패턴**:

**React/Next.js 예시**:
```tsx
import { useState } from 'react';
import { PageLayout } from '../components/layout';
import { Button, Card, Table, Skeleton, Toast } from '../components/common';
import { useScrollAnimation, useCountUp } from '../hooks';
import styles from '../styles/DashboardScreen.module.css';

export function DashboardScreen() {
  const [loading, setLoading] = useState(true);
  const sectionRef = useScrollAnimation();

  return (
    <PageLayout title="대시보드" activeMenu="dashboard">
      {/* KPI 카드 영역 — 카운터 애니메이션 + 시차 등장 */}
      <section ref={sectionRef} className={styles.kpiGrid}>
        {loading ? <Skeleton variant="rect" /> : <KPICards />}
      </section>
      {/* ... */}
    </PageLayout>
  );
}
```

**Vue 예시**:
```vue
<script setup lang="ts">
import { ref } from 'vue';
import PageLayout from '../components/layout/PageLayout.vue';
import { Button, Card, Table } from '../components/common';
import { useScrollAnimation } from '../hooks/useScrollAnimation';

const loading = ref(true);
const { sectionRef } = useScrollAnimation();
</script>

<template>
  <PageLayout title="대시보드" active-menu="dashboard">
    <section ref="sectionRef" :class="$style.kpiGrid">
      <!-- KPI 카드 영역 -->
    </section>
  </PageLayout>
</template>

<style module>
/* ... */
</style>
```

#### D. 화면 간 연결

`ia-screen-design.md`의 **화면 흐름도**를 기반으로 화면 간 라우팅을 설정한다:
- 프레임워크 라우터 링크 사용 (`<Link>`, `<RouterLink>`, `routerLink` 등)
- 버튼 클릭 → 다른 화면으로 이동
- 목록 행 클릭 → 상세 화면
- 폼 제출 → 결과 화면 + 토스트

> **참고**: `publish/` 내에서는 상대 import 경로를 사용한다. `COPY-GUIDE.md`에서 실제 프로젝트 라우팅 구조에 맞게 경로를 변경하는 안내를 포함한다.

#### E. 진행 상황 보고

화면 3개마다 사용자에게 중간 보고한다:

```
🔄 진행 상황: {완료 수}/{전체 수} 화면 컴포넌트 생성됨
- ✅ SCR-001: {화면명} → {ScreenName}Screen.{ext}
- ✅ SCR-002: {화면명} → {ScreenName}Screen.{ext}
- ⏳ SCR-003: {화면명} (다음)

계속 진행할까요?
```

---

### Step 3: 프리뷰 및 복사 가이드 생성

#### A. HTML 프리뷰 생성

`publish/{feature-name}/preview/` — 컴포넌트를 브라우저에서 바로 확인할 수 있는 HTML 프리뷰를 생성한다. 빌드 없이 브라우저에서 열어 디자인/인터랙션을 검수할 수 있다.

**프리뷰 인덱스** (`preview/index.html`):
- 프로토타입 헤더 (기능명, 생성일, 화면 수, 기술 스택)
- 화면 흐름도 시각화 (`ia-screen-design.md` 기반)
- 화면 카드 그리드 (각 화면 클릭 시 프리뷰 이동) — fect-image 생성 이미지를 카드 썸네일로 활용
- 다크모드 토글
- 인덱스 자체에도 시차 등장 + hover 애니메이션 적용 (실제 서비스처럼 보이도록)

**개별 화면 프리뷰** (`preview/screens/{screen-id}.html`):
- 컴포넌트가 렌더링된 결과와 **완전히 동일한** 형태의 HTML — 실제 서비스와 구분이 안 될 정도의 완성도
- `styles/` 디렉토리의 CSS를 참조 (`animations.css` 포함)
- `assets/images/`의 **AI 생성 이미지를 실제로 참조** — 플레이스홀더 박스 절대 금지, 모든 이미지 슬롯에 fect-image 생성 이미지를 배치
- 순수 JS로 **모든 애니메이션과 인터랙션 동작** 구현 (프레임워크 불필요):
  - 스크롤 기반 진입 애니메이션 (IntersectionObserver)
  - 버튼/카드 hover 효과
  - 모달 열기/닫기 전환
  - 카운터 rollup 애니메이션
  - 패럴랙스 효과 (랜딩 페이지)
  - 토스트 알림 데모
- 반응형 (모바일/태블릿/데스크톱 전환 가능), 다크모드 토글 동작
- `prefers-reduced-motion` 미디어 쿼리 대응

> **품질 기준**: 프리뷰를 브라우저에서 열었을 때 **실제 출시된 서비스와 동일한 수준의 비주얼**이어야 한다. AI 이미지, 애니메이션, 타이포그래피, 색상이 모두 적용된 상태여야 하며, 빈 이미지 박스나 placeholder 텍스트가 보여서는 안 된다.

> **주의**: 프리뷰는 디자인 검수용이다. 실제 프로젝트에서 사용하는 것은 컴포넌트 파일이다.

#### B. COPY-GUIDE.md 생성

`publish/{feature-name}/COPY-GUIDE.md` — 각 생성 파일을 프로젝트의 실제 위치로 복사하는 가이드를 생성한다.

```markdown
# {Feature Name} 컴포넌트 복사 가이드

> 이 가이드는 `publish/{feature-name}/`에서 생성된 컴포넌트를 프로젝트의 실제 위치로 복사하는 방법을 안내합니다.

## 기본 정보

- 기획 기반: `docs/planner/{PLANNER_DIR}`
- 프레임워크: {FRAMEWORK}
- 스타일 방식: {STYLE_METHOD}
- 생성일: {DATE}

## 복사 매핑

### 공통 컴포넌트 → `src/components/common/`

| 소스 (publish/) | 대상 (src/) | 비고 |
|----------------|------------|------|
| `components/common/Button.tsx` | `src/components/common/Button.tsx` | 기존 Button이 있으면 병합 필요 |
| `components/common/Input.tsx` | `src/components/common/Input.tsx` | |
| ... | ... | |

### 레이아웃 컴포넌트 → `src/components/layout/`

| 소스 (publish/) | 대상 (src/) | 비고 |
|----------------|------------|------|
| `components/layout/GNB.tsx` | `src/components/layout/GNB.tsx` | |
| `components/layout/Sidebar.tsx` | `src/components/layout/Sidebar.tsx` | |
| `components/layout/PageLayout.tsx` | `src/components/layout/PageLayout.tsx` | |

### 화면 컴포넌트 → `src/pages/` 또는 `src/app/`

| 소스 (publish/) | 대상 (src/) | 라우트 |
|----------------|------------|-------|
| `screens/DashboardScreen.tsx` | `src/pages/dashboard/index.tsx` | `/dashboard` |
| `screens/LoginScreen.tsx` | `src/pages/auth/login.tsx` | `/auth/login` |
| ... | ... | ... |

### 커스텀 훅 → `src/hooks/`

| 소스 (publish/) | 대상 (src/) |
|----------------|------------|
| `hooks/useScrollAnimation.ts` | `src/hooks/useScrollAnimation.ts` |
| `hooks/useTheme.ts` | `src/hooks/useTheme.ts` |
| ... | ... |

### 스타일 → `src/styles/`

| 소스 (publish/) | 대상 (src/) | 비고 |
|----------------|------------|------|
| `styles/base.css` | `src/styles/base.css` | 기존 파일 있으면 병합 |
| `styles/animations.css` | `src/styles/animations.css` | |
| `styles/*.module.css` | 각 컴포넌트 옆으로 이동 | CSS Modules 방식일 때 |

### 이미지 에셋 → `public/images/` 또는 `src/assets/`

| 소스 (publish/) | 대상 | 비고 |
|----------------|------|------|
| `assets/images/*` | `public/images/{feature-name}/` | Next.js/Vite 등 |

## 복사 명령어 (한번에 실행)

```bash
# 공통 컴포넌트
cp -r publish/{feature-name}/components/common/* src/components/common/

# 레이아웃
cp -r publish/{feature-name}/components/layout/* src/components/layout/

# 화면 (경로 조정 필요)
# cp publish/{feature-name}/screens/DashboardScreen.tsx src/pages/dashboard/index.tsx

# 훅
cp -r publish/{feature-name}/hooks/* src/hooks/

# 스타일
cp publish/{feature-name}/styles/base.css src/styles/
cp publish/{feature-name}/styles/animations.css src/styles/

# 이미지
cp -r publish/{feature-name}/assets/images/* public/images/{feature-name}/
```

## 복사 후 체크리스트

- [ ] import 경로 확인 및 조정 (publish/ 상대 경로 → src/ 절대/상대 경로)
- [ ] 라우터 설정에 화면 추가
- [ ] 기존 컴포넌트와 중복 확인 및 병합
- [ ] 디자인 토큰 파일이 프로젝트에 이미 있는지 확인 (tokens.css 복사 불필요할 수 있음)
- [ ] 빌드 확인 (`npm run build` 또는 `npm run dev`)

## 기존 컴포넌트 재사용 안내

다음 컴포넌트는 프로젝트에 이미 존재하여 publish에서 생성하지 않았습니다.
화면 컴포넌트에서 기존 컴포넌트를 import하고 있으니, 복사 시 import 경로만 조정하세요:

| 컴포넌트 | 기존 위치 |
|---------|---------|
| {기존 컴포넌트명} | {기존 경로} |
```

> **매핑 자동화**: COPY-GUIDE.md는 Step 0.D에서 분석한 프로젝트의 실제 디렉토리 구조와 네이밍 컨벤션을 반영하여 생성한다. Next.js App Router라면 `src/app/`, Pages Router라면 `src/pages/`, Vue CLI라면 `src/views/` 등으로 대상 경로를 조정한다.

#### C. 인덱스 페이지 생성

`publish/{feature-name}/preview/index.html` — 모든 화면을 한눈에 보고 이동할 수 있는 허브 페이지를 생성한다.

구성:
1. **프로토타입 헤더** — 기능명, 기술 스택, 생성일, 화면 수
2. **화면 흐름도 시각화** — `ia-screen-design.md`의 Screen Flow를 CSS로 시각화
3. **화면 카드 그리드** — 화면 ID, 화면명, 유형(Badge), 관련 UC, 클릭 시 프리뷰 이동
4. **범례** — 색상/아이콘 의미
5. **다크모드 토글**

---

### Step 4: 검증 및 완료

#### A. 생성물 검증

1. **디자인 토큰 사용 확인** — 하드코딩된 색상값(`#`, `rgb(`, `hsl(`)이 없는지 확인. 발견 시 디자인 토큰으로 교체
2. **import 경로 유효성** — 모든 컴포넌트 import가 `publish/` 내에서 유효한지 확인
3. **와이어프레임 완전 구현 확인** — 각 화면의 모든 UI 요소가 컴포넌트로 구현되었는지 확인
4. **TypeScript 타입 검증** — props interface가 정확한지 확인 (TSX 프로젝트)
5. **접근성 확인** — ARIA 속성, 시맨틱 HTML, 포커스 관리
6. **Vibe Coding 가이드 준수 확인** — Anti-AI 미학, 스프링 물리학, 3-tier 모션 접근성

#### B. CLAUDE.md 업데이트 확인

프로젝트의 `CLAUDE.md`에 퍼블리싱 경로를 추가할지 사용자에게 확인한다:

```
## 퍼블리싱 경로 등록

CLAUDE.md에 다음 항목을 추가할까요?

### Quick Command Reference 테이블에 추가:
| UX 컴포넌트 확인 | `publish/{feature-name}/preview/index.html` 브라우저에서 열기 |
| 컴포넌트 복사 가이드 | `publish/{feature-name}/COPY-GUIDE.md` 참조 |

추가할까요? (y/n):
```

#### C. 완료 보고

```
## UX 컴포넌트 퍼블리싱 완료

📁 위치: publish/{feature-name}/

### 생성 파일 요약
| 카테고리 | 파일 수 | 위치 |
|---------|--------|------|
| 공통 UI 컴포넌트 | {N}개 | components/common/ |
| 레이아웃 컴포넌트 | 3개 | components/layout/ |
| 기능 전용 컴포넌트 | {N}개 | components/{feature}/ |
| 화면 컴포넌트 | {N}개 | screens/ |
| 커스텀 훅 | {N}개 | hooks/ |
| 스타일 파일 | {N}개 | styles/ |
| AI 이미지 에셋 | {N}개 | assets/images/ |
| HTML 프리뷰 | {N}개 | preview/ |

### 프로젝트 정보
- 기획 기반: {PLANNER_DIR}
- 프레임워크: {FRAMEWORK}
- 스타일 방식: {STYLE_METHOD}
- 디자인 톤: {DESIGN_TONE}

### 디자인 품질
- Vibe Coding 디자인 가이드 준수 (Anti-AI 미학, 디자인 토큰)
- Vibe Coding 애니메이션 가이드 준수 (스프링 물리학, GPU 가속)
- UX 인터랙션 패턴 가이드 적용
- 프로덕션급 컴포넌트 (/frontend-design)
- 반응형: 모바일/태블릿/데스크톱
- 다크 모드 지원
- 접근성: WCAG AA (포커스, 모션 감소, 색상 대비, 터치 타겟)

### 적용된 인터랙션 패턴
| 패턴 | 적용 화면 |
|------|---------|
| 버튼 피드백 (1.1) | 전체 |
| 스켈레톤 로딩 (3.2) | {목록} |
| 토스트 알림 (3.5) | {목록} |
| 카운터 애니메이션 (1.6) | {목록} |
| 시차 등장 (7.5) | 전체 |
| 모션 감소 대응 (9.3) | 전체 |

### 다음 단계
1. **디자인 검수**: `publish/{feature-name}/preview/index.html`을 브라우저에서 열어 확인
2. **컴포넌트 복사**: `publish/{feature-name}/COPY-GUIDE.md`를 따라 src/로 복사
3. **DSA 검수**: Gate 2.5 디자인 리뷰
4. **개발 진행**: 복사된 컴포넌트에 비즈니스 로직 연결
```
