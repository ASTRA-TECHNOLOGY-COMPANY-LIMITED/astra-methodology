---
name: manual-generator
description: "실행 중인 서비스 URL과 프로젝트 문서를 기반으로 전문적인 온라인 서비스 매뉴얼을 자동 생성합니다. Chrome MCP로 화면별 스크린샷을 캡처하고, 블루프린트/기획 문서에서 기능 설명을 추출하여 단계별 가이드를 HTML 패키지로 퍼블리싱합니다. 매뉴얼 생성, 사용자 가이드 작성, 도움말 문서 생성 시 사용합니다."
argument-hint: "[대상 URL 또는 기능명]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Agent, Skill, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__click, mcp__chrome-devtools__fill, mcp__chrome-devtools__wait_for, mcp__chrome-devtools__list_pages, mcp__chrome-devtools__select_page, mcp__chrome-devtools__new_page, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__resize_page, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__emulate, mcp__chrome-devtools__hover, mcp__chrome-devtools__fill_form, mcp__chrome-devtools__press_key
---

# ASTRA 서비스 매뉴얼 자동 생성

실행 중인 서비스 URL과 프로젝트 문서(blueprints, planner)를 분석하여, **전문적인 온라인 서비스 매뉴얼**을 자기완결형 HTML 패키지로 생성합니다.

**핵심 원칙**:
- **Chrome MCP 스크린샷 캡처** — 실제 서비스 화면을 탐색하며 단계별 스크린샷을 자동 캡처
- **스크린샷 주석 자동화** — CSS 주입으로 UI 요소 하이라이트 + 단계 번호 오버레이
- **`/frontend-design` 스킬 연동** — 세련되고 읽기 편한 프로덕션급 매뉴얼 디자인
- **전문가 수준 글쓰기** — 2인칭 존칭("~하세요"), 평이한 언어, step-by-step 형식
- 프로젝트의 `src/styles/design-tokens.css`를 참조 (하드코딩 금지)
- 다크 모드, 클라이언트 검색, 반응형, 인쇄용 스타일 지원
- 브라우저에서 바로 열어 확인 가능 (별도 빌드 불필요)

**생성물 위치**: `docs/manual/{feature-name}/`

**글쓰기 품질 기준**:
- 비기술 사용자도 따라할 수 있는 명확한 단계별 안내
- 모든 단계에 스크린샷 첨부 (67% 더 높은 이해도 — TechSmith 연구)
- 일관된 톤, 전문 용어 없는 평이한 언어
- 팁/주의/경고 박스로 핵심 정보 강조

> **🌐 LANGUAGE RULE**: Before executing this skill, read the project's `CLAUDE.md` and check the `## Language` section to detect the project language. If the project language is NOT Korean (`ko`), you MUST translate ALL user-facing output — including HTML page titles, labels, chapter titles, step descriptions, callout text — into the project language. Technical identifiers (file paths, CSS variable names, class names) remain untranslated. If no `CLAUDE.md` exists or no `## Language` section is found, default to Korean.

## 추가 리소스

- **글쓰기 원칙/스타일 규칙**: [references/manual-writing-guide.md](references/manual-writing-guide.md) 참조
- **CSS 컴포넌트 템플릿**: [references/manual-css-template.md](references/manual-css-template.md) 참조
- **HTML 구조 템플릿**: [references/manual-html-templates.md](references/manual-html-templates.md) 참조 (챕터, 인덱스, FAQ, 용어집)

---

## 실행 절차

### Step 0: 사전 준비 및 컨텍스트 수집

#### A. 인자 파싱

`$ARGUMENTS`를 확인한다:

| 인자 형태 | 동작 |
|-----------|------|
| URL (`http://` 또는 `https://` 시작) | 해당 URL을 대상 서비스로 사용 |
| 기능명 문자열 (예: `인증`, `결제`) | 해당 기능의 문서와 URL을 검색 |
| URL + 기능명 (예: `http://localhost:3000 인증`) | URL과 기능 범위를 모두 사용 |
| _(없음)_ | `AskUserQuestion`으로 대상 정보를 질문 |

인자가 없으면 다음을 질문한다:

```
## 서비스 매뉴얼 생성

매뉴얼을 생성할 서비스 정보를 알려주세요.

1. **서비스 URL** (선택): 실행 중인 서비스 URL (예: http://localhost:3000)
   → URL이 있으면 실제 화면 스크린샷을 캡처합니다.
   → URL이 없으면 문서 기반으로만 매뉴얼을 생성합니다.

2. **문서화 대상**: 매뉴얼로 작성할 기능 (예: "인증 기능", "결제 시스템", "전체")

입력:
```

사용자 입력에서 `{SERVICE_URL}`과 `{TARGET_FEATURE}`를 추출한다.

#### B. 프로젝트 컨텍스트 로드

1. `CLAUDE.md` 읽기 — 프로젝트명, 기술 스택, 언어 설정(LANGUAGE RULE 적용)
2. `docs/blueprints/` 스캔 — 기능별 블루프린트 목록 수집
3. `docs/planner/` 스캔 — 기획 산출물 목록 수집
4. `ux/` 스캔 — 기존 UX 프로토타입 확인 (라우트/화면 참고)
5. `src/styles/design-tokens.css` 존재 확인

> **검증**: `src/styles/design-tokens.css`가 없으면 사용자에게 알린다:
> "디자인 토큰 파일이 없습니다. `/project-init`으로 프로젝트를 먼저 초기화해 주세요."
> 파일이 없어도 `$CLAUDE_PLUGIN_ROOT/skills/project-init/templates/design-tokens.css`의 기본 토큰으로 대체할 수 있다.

#### C. URL 접근성 검증

`{SERVICE_URL}`이 제공된 경우:

1. `mcp__chrome-devtools__navigate_page`로 URL에 접근
2. `mcp__chrome-devtools__wait_for`로 페이지 로드 대기 (최대 15초)
3. 접근 실패 시 사용자에게 알리고 문서 기반 모드로 전환:
   "서비스에 접근할 수 없습니다. 서비스가 실행 중인지 확인해 주세요. 문서 기반으로만 매뉴얼을 생성할까요?"

#### D. 문서 소스 분석

다음 문서들을 읽어 기능 맵을 구축한다:

| 소스 | 경로 | 추출 정보 |
|------|------|----------|
| 블루프린트 | `docs/blueprints/{NNN}-*/blueprint.md` | 기능 설계, API 엔드포인트, 유저 스토리 |
| 기능 정의서 | `docs/planner/{NNN}-*/feature-definition.md` | 기능 구조, 소기능 상세, 서비스 정책 |
| IA/화면 설계서 | `docs/planner/{NNN}-*/ia-screen-design.md` | IA 구조, 화면 목록, 화면 흐름도 |
| 유즈케이스 | `docs/planner/{NNN}-*/usecase-definition.md` | 사용자 흐름, 대안 흐름, 예외 흐름 |
| UX 프로토타입 | `ux/*/index.html` | 화면 인덱스, 라우트 구조 |

`{TARGET_FEATURE}`가 "전체"가 아닌 경우, 해당 기능과 관련된 문서만 필터링한다.

#### E. 매뉴얼 설정 선택

`AskUserQuestion`으로 매뉴얼 생성 옵션을 선택한다:

```
## 매뉴얼 생성 설정

### 1. 매뉴얼 범위
문서화할 기능을 선택하세요.

| # | 기능 | 소스 | 화면 수 |
|---|------|------|---------|
| 1 | {feature-1} | {blueprint + URL / blueprint only / planner only} | {N} |
| 2 | {feature-2} | {소스} | {N} |
| ... | ... | ... | ... |

선택 (전체: all, 선택: 1,3):

### 2. 언어
| # | 언어 |
|---|------|
| 1 | 한국어 |
| 2 | English |
| 3 | Auto (CLAUDE.md 기준) |

### 3. 디자인 톤
| # | 톤 | 설명 |
|---|-----|------|
| 1 | Professional Enterprise | 안정적이고 신뢰감 있는 엔터프라이즈 문서 |
| 2 | Refined Minimal | 깔끔하고 정제된 미니멀 문서 |
| 3 | Soft & Warm | 부드럽고 친근한 도움말 스타일 |
| 4 | Auto | 프로젝트 특성에 맞게 자동 선택 |

### 4. 반응형 스크린샷
| # | 옵션 |
|---|------|
| 1 | 데스크톱만 |
| 2 | 데스크톱 + 모바일 |
| 3 | 데스크톱 + 태블릿 + 모바일 |
```

선택 결과를 `{SELECTED_FEATURES}`, `{LANGUAGE}`, `{DESIGN_TONE}`, `{RESPONSIVE_MODE}`로 저장한다.

---

### Step 1: 대상 서비스 분석 및 목차 설계

#### A. 기능 맵 구축

Step 0에서 수집한 문서를 분석하여 기능별로 다음을 추출한다:

| 항목 | 소스 |
|------|------|
| 기능명/설명 | blueprint.md → 개요 섹션 |
| 화면 목록 | ia-screen-design.md → 화면 목록 테이블 |
| 사용자 흐름 | usecase-definition.md → 기본 흐름 / 대안 흐름 |
| API 엔드포인트 | blueprint.md → API 설계 섹션 |
| 비즈니스 규칙 | feature-definition.md → 서비스 정책 |
| 화면 흐름도 | ia-screen-design.md → 화면 전환 다이어그램 |

#### B. 서비스 탐색 (URL 있는 경우)

`{SERVICE_URL}`이 제공된 경우, Chrome MCP로 실제 서비스를 탐색한다:

1. `mcp__chrome-devtools__navigate_page`로 기본 URL 접근
2. `mcp__chrome-devtools__take_snapshot`으로 페이지 구조 파악
3. 내비게이션 메뉴/라우트를 분석하여 문서의 화면 목록과 대조
4. 문서에 없는 추가 화면이 발견되면 기능 맵에 추가

#### C. 목차(TOC) 생성

기능 맵을 기반으로 매뉴얼 목차를 설계한다:

```
챕터 구조 규칙:
- 01: 시작하기 (Getting Started) — 항상 첫 번째
  - 서비스 소개, 접속 방법, 시스템 요구사항, 첫 로그인
- 02~NN-2: 기능별 가이드 — 문서 순서 또는 사용자 여정 순서
  - 각 기능: 개요 → 단계별 사용법 → 팁/주의사항
  - 대기능은 여러 챕터로 분리 (예: 02-auth-login, 03-auth-signup)
- NN-1: FAQ / 문제 해결 — usecase의 대안/예외 흐름에서 추출
- NN: 용어집 (선택) — 프로젝트 도메인 용어 정의
```

#### D. TOC 승인 요청

`AskUserQuestion`으로 목차를 사용자에게 보여주고 승인을 받는다:

```
## 매뉴얼 목차 확인

다음 목차로 매뉴얼을 생성합니다.

| # | 챕터 | 포함 내용 | 예상 스크린샷 수 |
|---|------|----------|---------------|
| 01 | 시작하기 | 서비스 소개, 접속, 첫 화면 | 3-5 |
| 02 | {기능명} — {서브기능} | {설명} | {N} |
| 03 | {기능명} — {서브기능} | {설명} | {N} |
| ... | ... | ... | ... |
| {NN-1} | FAQ / 문제 해결 | 자주 묻는 질문, 오류 해결 | 0-3 |
| {NN} | 용어집 | 서비스 용어 정의 | 0 |

총 {N}개 챕터, 예상 스크린샷 약 {N}장

이대로 진행할까요? (수정이 필요하면 변경사항을 알려주세요):
```

수정 요청이 있으면 TOC를 조정하고, 승인되면 `{APPROVED_TOC}` 배열로 저장한다.

---

### Step 2: 공통 리소스 생성

#### A. 디렉토리 구조 생성

`docs/manual/{feature-name}/` 디렉토리를 생성한다. `{feature-name}`은:
- 단일 기능: 기능명 (예: `auth`, `payment`)
- 전체: 프로젝트명 또는 `service-guide`

```
docs/manual/{feature-name}/
├── index.html
├── chapters/
├── assets/
├── screenshots/
│   ├── desktop/
│   ├── tablet/    (RESPONSIVE_MODE >= 2일 때)
│   └── mobile/    (RESPONSIVE_MODE >= 2일 때)
└── shared/
```

#### B. 디자인 토큰 복사

`src/styles/design-tokens.css` → `docs/manual/{feature-name}/assets/tokens.css`로 **그대로 복사**한다.

#### C. `/frontend-design` 스킬 연동

`/frontend-design` 스킬을 호출하여 매뉴얼 전용 CSS를 생성한다. 호출 시 다음 컨텍스트를 전달한다:

```
문서/매뉴얼용 CSS를 생성해 주세요.
디자인 톤: {DESIGN_TONE}
용도: 온라인 서비스 매뉴얼 (읽기 최적화)
필요 컴포넌트: 사이드바 TOC, step-card, callout boxes, screenshot-frame, breadcrumb, chapter-nav, search overlay
디자인 토큰: assets/tokens.css를 var() 참조
다크 모드: 지원 필수
반응형: 모바일/태블릿/데스크톱
```

> `/frontend-design`이 사용 불가한 경우, `references/manual-css-template.md`의 CSS 템플릿을 직접 사용한다.

#### D. CSS 파일 생성

`/frontend-design` 결과를 기반으로 다음 파일들을 생성한다. 각 CSS 파일의 상세 컴포넌트 스펙은 `references/manual-css-template.md`를 참조한다:

1. **`assets/manual-base.css`** — 읽기 최적화 레이아웃:
   - `max-width: 800px` 콘텐츠 영역 (가독성 최적)
   - 왼쪽 사이드바 TOC (240px, 접을 수 있음, sticky)
   - 64px 상단 헤더바
   - 타이포그래피: 문서 최적화 (line-height 1.7, 충분한 문단 간격)
   - 반응형: 태블릿에서 사이드바 접힘, 모바일에서 오버레이
   - 다크 모드: `[data-theme="dark"]` 셀렉터

2. **`assets/manual-components.css`** — 매뉴얼 전용 컴포넌트:
   - `.step-card` — 번호가 매겨진 단계 카드 (번호 원형 + 내용 + 스크린샷)
   - `.callout-tip`, `.callout-warning`, `.callout-note`, `.callout-danger` — 정보 박스
   - `.screenshot-frame` — 브라우저 크롬 모의 프레임 + 스크린샷 이미지
   - `.screenshot-annotation` — 위치 지정 번호 원형 (스크린샷 위 오버레이)
   - `.breadcrumb` — 챕터 브레드크럼
   - `.chapter-nav` — 이전/다음 챕터 내비게이션
   - `.responsive-tabs` — 데스크톱/태블릿/모바일 스크린샷 탭 전환
   - `.toc-sidebar` — 사이드바 목차
   - `.search-overlay` — 검색 모달

3. **`assets/manual-print.css`** — 인쇄용:
   - 사이드바/헤더/내비게이션 숨김
   - 스크린샷 페이지 넘김 방지
   - 링크 URL 텍스트 출력

4. **`assets/manual-search.css`** — 검색 오버레이 전용 스타일

#### E. JavaScript 파일 생성

1. **`shared/nav.js`**:
   - 사이드바 TOC 토글 (모바일: 햄버거 메뉴)
   - 챕터 이전/다음 내비게이션
   - 스크롤스파이: 현재 읽고 있는 섹션을 TOC에서 하이라이트
   - 키보드 내비게이션: `←` / `→`로 챕터 이동

2. **`shared/search.js`**:
   - `search-index.json` 로드
   - 검색어 입력 시 실시간 결과 표시
   - 결과 클릭 시 해당 챕터+섹션으로 이동
   - 키보드: `Ctrl+K` / `Cmd+K`로 검색 열기

3. **`shared/theme.js`**:
   - 다크 모드 토글 (`localStorage` 저장)
   - 폰트 크기 A+/A- 조절 (3단계)
   - 시스템 테마 감지 (`prefers-color-scheme`)

#### F. 진행 보고

```
✅ 공통 리소스 생성 완료
   - CSS: manual-base.css, manual-components.css, manual-print.css, manual-search.css
   - JS: nav.js, search.js, theme.js
   - 디자인 토큰: tokens.css
```

---

### Step 3: 스크린샷 캡처

> `{SERVICE_URL}`이 없는 경우(문서 기반 모드), 이 단계를 건너뛰고 Step 4에서 스크린샷 없이 매뉴얼을 생성한다. `ux/` 디렉토리에 UX 프로토타입이 있으면 해당 HTML을 열어 스크린샷을 캡처할 수 있다.

승인된 TOC의 각 챕터에 필요한 스크린샷을 캡처한다.

#### A. 스크린샷 캡처 워크플로우 (화면별)

각 화면에 대해:

1. **페이지 이동**:
   ```
   mcp__chrome-devtools__navigate_page({ url: "{SERVICE_URL}/{route}" })
   ```

2. **콘텐츠 로드 대기**:
   ```
   mcp__chrome-devtools__wait_for({ selector: "{main-content-selector}", timeout: 10000 })
   ```

3. **하이라이트 CSS 주입** — `evaluate_script`로 `.manual-highlight` 클래스를 대상 요소에 추가:
   - 스타일: `outline: 3px solid #2563EB`, `outline-offset: 2px`, `box-shadow: 0 0 0 6px rgba(37,99,235,0.15)`
   - `<style id="manual-highlight-style">`을 head에 주입 후 `querySelector('{target-selector}').classList.add('manual-highlight')`

4. **단계 번호 오버레이 주입** — `evaluate_script`로 대상 요소 우상단에 원형 배지 추가:
   - 28x28px 파란 원형, 흰 글씨, `z-index: 10001`
   - `getBoundingClientRect()`로 위치 계산, `position: fixed`

5. **스크린샷 캡처** — `take_screenshot()` → `screenshots/desktop/{chapter}-step-{N}.png`

6. **주입 요소 제거** — `evaluate_script`로 `.manual-highlight` 클래스 제거, `.manual-step-badge` 요소 제거, 스타일 태그 제거

#### B. 반응형 스크린샷 (RESPONSIVE_MODE >= 2일 때)

각 화면의 주요 스크린샷(첫 번째 또는 대표 스크린샷)에 대해:

1. **태블릿** (RESPONSIVE_MODE >= 3):
   ```
   mcp__chrome-devtools__resize_page({ width: 768, height: 1024 })
   ```
   → 캡처 → `screenshots/tablet/{chapter}-overview.png`

2. **모바일** (RESPONSIVE_MODE >= 2):
   ```
   mcp__chrome-devtools__resize_page({ width: 375, height: 812 })
   ```
   → 캡처 → `screenshots/mobile/{chapter}-overview.png`

3. **데스크톱으로 원복**:
   ```
   mcp__chrome-devtools__resize_page({ width: 1280, height: 800 })
   ```

#### C. 멀티스텝 흐름 캡처

사용자 흐름(로그인, 폼 제출, CRUD 등)이 있는 챕터에서:

1. 시작 화면 캡처 (Step A 워크플로우)
2. 인터랙션 실행:
   - 입력: `mcp__chrome-devtools__fill({ selector: "{input}", value: "{test-data}" })`
   - 클릭: `mcp__chrome-devtools__click({ selector: "{button}" })`
   - 키입력: `mcp__chrome-devtools__press_key({ key: "Enter" })`
3. 결과 대기: `mcp__chrome-devtools__wait_for({ selector: "{result-indicator}" })`
4. 다음 단계 캡처 (Step A 워크플로우 반복)
5. 최종 결과 화면 캡처

> **주의**: 테스트 데이터로만 인터랙션한다. 실제 데이터를 변경하지 않도록 주의한다. 가능하면 읽기 전용 흐름(조회, 검색)을 우선 캡처하고, 쓰기 흐름(생성, 수정, 삭제)은 사용자에게 확인 후 진행한다.

#### D. 진행 보고

```
📸 스크린샷 캡처 진행: {completed}/{total} 챕터
   - 챕터 01 시작하기: 3장 완료
   - 챕터 02 {기능}: {N}장 완료
   - ...
```

---

### Step 4: 챕터 작성

승인된 TOC의 각 챕터를 HTML로 작성한다.

#### A. 글쓰기 규칙

`references/manual-writing-guide.md`를 읽어 글쓰기 규칙을 적용한다. 핵심 규칙:

| 규칙 | 적용 |
|------|------|
| 2인칭 존칭 | "로그인 버튼을 클릭하세요" (O), "로그인 버튼을 클릭한다" (X) |
| 평이한 언어 | "인증 토큰이 갱신됩니다" (X) → "자동으로 로그인이 유지됩니다" (O) |
| 단계별 형식 | 모든 절차를 번호가 매겨진 단계로 분리 |
| 시각 우선 | 텍스트보다 스크린샷이 명확한 경우 스크린샷 사용 |
| 일관된 용어 | 동일 UI 요소는 매뉴얼 전체에서 동일 이름 사용 |
| 팁/주의 박스 | 선택적 정보는 `.callout-tip`, 위험한 작업은 `.callout-warning` |

#### B. 챕터 HTML 구조

`references/manual-html-templates.md`의 **챕터 HTML 템플릿**을 참조하여 각 챕터를 생성한다.

핵심 구조 요약:
- `manual-header` — 상단 고정 헤더 (프로젝트명, 검색/테마/폰트 버튼)
- `toc-sidebar` — 왼쪽 고정 사이드바 (전체 챕터 링크)
- `breadcrumb` — 이동 경로 (매뉴얼 › 챕터명)
- `chapter` > `steps` > `step-card` — 번호 매겨진 단계별 가이드
- `screenshot-frame` > `screenshot-chrome` + `screenshot-body` — 브라우저 모의 프레임
- `callout-tip/warning/note/danger` — 정보 박스
- `responsive-preview` > `responsive-tabs` — 반응형 스크린샷 탭 (선택)
- `chapter-nav` — 이전/다음 챕터 내비게이션
- `search-overlay` — 검색 모달

#### C. 챕터별 콘텐츠 작성

**01-getting-started.html** (시작하기):
- 서비스 소개 (1-2 문단, 프로젝트 CLAUDE.md에서 추출)
- 시스템 요구사항 (브라우저, 해상도 등)
- 접속 방법 (URL + 스크린샷)
- 첫 로그인/가입 흐름 (step-card)
- 메인 화면 구성 안내 (주요 영역 설명 + annotated 스크린샷)

**02~NN-2: 기능별 챕터**:
- 기능 개요 (blueprint/feature-definition에서 추출)
- 단계별 사용법 (usecase의 기본 흐름 → step-card)
- 고급 기능/설정 (선택적)
- 주의사항 (usecase의 대안/예외 흐름 → callout-warning)
- 관련 팁 (callout-tip)

**NN-1: FAQ / 문제 해결**:
- usecase의 예외 흐름에서 추출한 FAQ
- 일반적인 오류 상황과 해결 방법
- 질문-답변 형식 (`<details><summary>` 아코디언)

**NN: 용어집** (선택):
- 서비스에서 사용되는 전문 용어 정의
- 알파벳/가나다 순 정렬
- `<dl>` 정의 목록 사용

#### D. 진행 보고 (2챕터마다)

```
📝 챕터 작성 진행: {completed}/{total}
   - ✅ 01 시작하기
   - ✅ 02 {기능}
   - 🔄 03 {기능} (작성 중)
   - ⏳ 04 {기능}
```

---

### Step 5: 표지 + 목차 인덱스 생성

#### A. index.html 생성

`references/manual-html-templates.md`의 **인덱스(표지) HTML 템플릿**을 참조하여 생성한다.

핵심 구조 요약:
- `cover` — 프로젝트명, 매뉴얼 제목, 버전/생성일 메타 정보
- `quick-start-callout` — "처음 사용하시나요?" CTA → 01-getting-started.html 링크
- `index-search` — 대형 검색 입력란
- `index-toc` > `toc-grid` > `toc-card` — 챕터별 카드 (번호, 제목, 설명, 메타)

#### B. search-index.json 생성

모든 챕터를 스캔하여 검색 인덱스를 생성한다:

```json
[
  {
    "chapter": "01",
    "title": "시작하기",
    "url": "chapters/01-getting-started.html",
    "sections": [
      { "heading": "서비스 소개", "anchor": "#intro", "content": "..." },
      { "heading": "접속 방법", "anchor": "#access", "content": "..." }
    ]
  }
]
```

각 섹션의 `content`는 본문 텍스트의 처음 200자를 포함한다 (검색 매칭용).

---

### Step 6: 검증 및 마무리

#### A. 파일 무결성 검증

1. 모든 챕터 HTML 파일이 생성되었는지 확인
2. 모든 스크린샷 참조가 실제 파일과 매칭되는지 검증:
   ```
   Glob으로 screenshots/ 하위 모든 이미지 수집
   각 챕터 HTML에서 <img src=""> 추출
   매칭되지 않는 참조가 있으면 경고
   ```
3. 챕터 간 링크 (prev/next, 브레드크럼) 검증
4. `search-index.json`에 모든 챕터가 포함되었는지 확인

#### B. 생성 결과 보고

```
## ✅ 매뉴얼 생성 완료

| 항목 | 값 |
|------|-----|
| 위치 | docs/manual/{feature-name}/ |
| 챕터 수 | {N}개 |
| 스크린샷 | desktop {N}장, tablet {N}장, mobile {N}장 |
| 총 파일 수 | {N}개 |
| 총 크기 | {N} MB |

### 브라우저에서 열기
\`\`\`bash
open docs/manual/{feature-name}/index.html
\`\`\`

### 생성된 챕터
| # | 챕터 | 스크린샷 |
|---|------|---------|
| 01 | 시작하기 | {N}장 |
| 02 | {기능} | {N}장 |
| ... | ... | ... |
```
