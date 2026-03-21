# 매뉴얼 CSS 컴포넌트 템플릿

매뉴얼 생성 시 사용할 CSS 컴포넌트의 상세 스펙과 코드 템플릿을 정의한다. 모든 CSS는 `assets/tokens.css`의 디자인 토큰을 `var()` 참조한다.

## 1. manual-base.css — 레이아웃

### 핵심 레이아웃 구조

```css
/* 매뉴얼 레이아웃 — 읽기 최적화 */

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  scroll-behavior: smooth;
}

/* 폰트 크기 조절 (theme.js 연동) */
html[data-font="small"] { font-size: 14px; }
html[data-font="medium"] { font-size: 16px; }
html[data-font="large"] { font-size: 18px; }

body {
  font-family: var(--font-family-sans, 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif);
  font-size: var(--font-size-base, 1rem);
  line-height: 1.7;
  color: var(--color-text-primary, #1a1a2e);
  background-color: var(--color-bg-primary, #ffffff);
  transition: color 0.2s ease, background-color 0.2s ease;
}

/* 다크 모드 */
[data-theme="dark"] body {
  color: var(--color-text-primary-dark, #e2e8f0);
  background-color: var(--color-bg-primary-dark, #0f172a);
}

/* 상단 헤더 (64px) */
.manual-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: var(--color-bg-primary, #ffffff);
  border-bottom: 1px solid var(--color-border-default, #e2e8f0);
  display: flex;
  align-items: center;
  padding: 0 var(--spacing-6, 1.5rem);
  z-index: 100;
  gap: var(--spacing-4, 1rem);
}

[data-theme="dark"] .manual-header {
  background: var(--color-bg-primary-dark, #0f172a);
  border-bottom-color: var(--color-border-default-dark, #334155);
}

.manual-title {
  font-size: var(--font-size-lg, 1.125rem);
  font-weight: var(--font-weight-semibold, 600);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-actions {
  margin-left: auto;
  display: flex;
  gap: var(--spacing-2, 0.5rem);
}

.header-actions button {
  background: none;
  border: 1px solid var(--color-border-default, #e2e8f0);
  border-radius: var(--radius-md, 0.375rem);
  padding: var(--spacing-2, 0.5rem);
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.15s ease;
}

.header-actions button:hover {
  background: var(--color-bg-secondary, #f8fafc);
}

/* 메인 레이아웃 — 사이드바 + 콘텐츠 */
.manual-layout {
  display: flex;
  min-height: 100vh;
  padding-top: 64px;
}

/* 사이드바 TOC (240px, sticky) */
.toc-sidebar {
  width: 240px;
  flex-shrink: 0;
  position: fixed;
  top: 64px;
  left: 0;
  bottom: 0;
  overflow-y: auto;
  background: var(--color-bg-secondary, #f8fafc);
  border-right: 1px solid var(--color-border-default, #e2e8f0);
  padding: var(--spacing-4, 1rem) 0;
  z-index: 50;
  transition: transform 0.3s ease;
}

[data-theme="dark"] .toc-sidebar {
  background: var(--color-bg-secondary-dark, #1e293b);
  border-right-color: var(--color-border-default-dark, #334155);
}

/* 메인 콘텐츠 (max-width 800px, 읽기 최적) */
.manual-content {
  flex: 1;
  margin-left: 240px;
  padding: var(--spacing-8, 2rem) var(--spacing-6, 1.5rem);
  max-width: calc(800px + 240px + 3rem);
}

.chapter {
  max-width: 800px;
}

.chapter h1 {
  font-size: var(--font-size-3xl, 1.875rem);
  font-weight: var(--font-weight-bold, 700);
  margin-bottom: var(--spacing-4, 1rem);
  line-height: 1.3;
}

.chapter h2 {
  font-size: var(--font-size-xl, 1.25rem);
  font-weight: var(--font-weight-semibold, 600);
  margin-top: var(--spacing-10, 2.5rem);
  margin-bottom: var(--spacing-4, 1rem);
  padding-bottom: var(--spacing-2, 0.5rem);
  border-bottom: 1px solid var(--color-border-default, #e2e8f0);
}

.chapter h3 {
  font-size: var(--font-size-lg, 1.125rem);
  font-weight: var(--font-weight-semibold, 600);
  margin-top: var(--spacing-6, 1.5rem);
  margin-bottom: var(--spacing-3, 0.75rem);
}

.chapter p {
  margin-bottom: var(--spacing-4, 1rem);
}

.chapter-intro {
  font-size: var(--font-size-lg, 1.125rem);
  color: var(--color-text-secondary, #64748b);
  margin-bottom: var(--spacing-8, 2rem);
}

/* 반응형: 태블릿 */
@media (max-width: 1023px) {
  .toc-sidebar {
    transform: translateX(-100%);
    width: 280px;
    z-index: 200;
    box-shadow: 4px 0 12px rgba(0,0,0,0.1);
  }
  .toc-sidebar.open {
    transform: translateX(0);
  }
  .manual-content {
    margin-left: 0;
    max-width: none;
  }
}

/* 반응형: 모바일 */
@media (max-width: 767px) {
  .manual-content {
    padding: var(--spacing-4, 1rem);
  }
  .chapter h1 {
    font-size: var(--font-size-2xl, 1.5rem);
  }
}
```

### 인덱스 페이지 전용

```css
/* index.html — 표지 + 목차 */
.index-content {
  max-width: 960px;
  margin: 0 auto;
  padding: var(--spacing-8, 2rem) var(--spacing-6, 1.5rem);
  padding-top: calc(64px + var(--spacing-8, 2rem));
}

.cover {
  text-align: center;
  padding: var(--spacing-16, 4rem) 0;
}

.cover-title {
  font-size: var(--font-size-4xl, 2.25rem);
  font-weight: var(--font-weight-bold, 700);
  margin-bottom: var(--spacing-2, 0.5rem);
}

.cover-subtitle {
  font-size: var(--font-size-xl, 1.25rem);
  color: var(--color-text-secondary, #64748b);
  margin-bottom: var(--spacing-6, 1.5rem);
}

.cover-meta {
  display: flex;
  justify-content: center;
  gap: var(--spacing-6, 1.5rem);
  font-size: var(--font-size-sm, 0.875rem);
  color: var(--color-text-tertiary, #94a3b8);
}

.quick-start-callout {
  background: var(--color-bg-accent, #eff6ff);
  border-radius: var(--radius-lg, 0.5rem);
  padding: var(--spacing-6, 1.5rem);
  text-align: center;
  margin: var(--spacing-8, 2rem) 0;
}

[data-theme="dark"] .quick-start-callout {
  background: var(--color-bg-accent-dark, #1e3a5f);
}

.cta-button {
  display: inline-block;
  margin-top: var(--spacing-4, 1rem);
  padding: var(--spacing-3, 0.75rem) var(--spacing-6, 1.5rem);
  background: var(--color-primary, #2563eb);
  color: #ffffff;
  border-radius: var(--radius-md, 0.375rem);
  text-decoration: none;
  font-weight: var(--font-weight-semibold, 600);
  transition: background 0.15s ease;
}

.cta-button:hover {
  background: var(--color-primary-hover, #1d4ed8);
}

/* 목차 카드 그리드 */
.toc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-4, 1rem);
  margin-top: var(--spacing-6, 1.5rem);
}

.toc-card {
  display: block;
  padding: var(--spacing-5, 1.25rem);
  border: 1px solid var(--color-border-default, #e2e8f0);
  border-radius: var(--radius-lg, 0.5rem);
  text-decoration: none;
  color: inherit;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.toc-card:hover {
  border-color: var(--color-primary, #2563eb);
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.1);
}

.toc-card-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: var(--color-primary, #2563eb);
  color: #ffffff;
  border-radius: 50%;
  font-size: var(--font-size-sm, 0.875rem);
  font-weight: var(--font-weight-bold, 700);
  margin-bottom: var(--spacing-3, 0.75rem);
}

.toc-card h3 {
  font-size: var(--font-size-base, 1rem);
  font-weight: var(--font-weight-semibold, 600);
  margin-bottom: var(--spacing-2, 0.5rem);
}

.toc-card p {
  font-size: var(--font-size-sm, 0.875rem);
  color: var(--color-text-secondary, #64748b);
  margin-bottom: var(--spacing-3, 0.75rem);
}

.toc-card-meta {
  font-size: var(--font-size-xs, 0.75rem);
  color: var(--color-text-tertiary, #94a3b8);
}
```

## 2. manual-components.css — 컴포넌트

### Step Card (단계 카드)

```css
.steps {
  margin-top: var(--spacing-6, 1.5rem);
}

.step-card {
  display: flex;
  gap: var(--spacing-4, 1rem);
  margin-bottom: var(--spacing-8, 2rem);
  padding: var(--spacing-6, 1.5rem);
  background: var(--color-bg-primary, #ffffff);
  border: 1px solid var(--color-border-default, #e2e8f0);
  border-radius: var(--radius-lg, 0.5rem);
  transition: border-color 0.15s ease;
}

[data-theme="dark"] .step-card {
  background: var(--color-bg-secondary-dark, #1e293b);
  border-color: var(--color-border-default-dark, #334155);
}

.step-card:hover {
  border-color: var(--color-primary, #2563eb);
}

.step-number {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: var(--color-primary, #2563eb);
  color: #ffffff;
  border-radius: 50%;
  font-size: var(--font-size-lg, 1.125rem);
  font-weight: var(--font-weight-bold, 700);
}

.step-content {
  flex: 1;
  min-width: 0;
}

.step-content h3 {
  margin-top: 0;
  margin-bottom: var(--spacing-2, 0.5rem);
}

.step-content p {
  color: var(--color-text-secondary, #64748b);
}

@media (max-width: 767px) {
  .step-card {
    flex-direction: column;
    align-items: flex-start;
  }
}
```

### Callout Boxes (정보 박스)

```css
.callout-tip,
.callout-note,
.callout-warning,
.callout-danger {
  padding: var(--spacing-4, 1rem) var(--spacing-5, 1.25rem);
  border-radius: var(--radius-md, 0.375rem);
  margin: var(--spacing-4, 1rem) 0;
  font-size: var(--font-size-sm, 0.875rem);
  line-height: 1.6;
  border-left: 4px solid;
}

.callout-tip {
  background: #f0fdf4;
  border-left-color: #22c55e;
  color: #166534;
}

.callout-note {
  background: #eff6ff;
  border-left-color: #3b82f6;
  color: #1e40af;
}

.callout-warning {
  background: #fffbeb;
  border-left-color: #f59e0b;
  color: #92400e;
}

.callout-danger {
  background: #fef2f2;
  border-left-color: #ef4444;
  color: #991b1b;
}

/* 다크 모드 callout */
[data-theme="dark"] .callout-tip {
  background: rgba(34, 197, 94, 0.1);
  color: #86efac;
}

[data-theme="dark"] .callout-note {
  background: rgba(59, 130, 246, 0.1);
  color: #93c5fd;
}

[data-theme="dark"] .callout-warning {
  background: rgba(245, 158, 11, 0.1);
  color: #fcd34d;
}

[data-theme="dark"] .callout-danger {
  background: rgba(239, 68, 68, 0.1);
  color: #fca5a5;
}

.callout-tip strong,
.callout-note strong,
.callout-warning strong,
.callout-danger strong {
  display: block;
  margin-bottom: var(--spacing-1, 0.25rem);
}
```

### Screenshot Frame (스크린샷 프레임)

```css
.screenshot-frame {
  margin: var(--spacing-4, 1rem) 0;
  border-radius: var(--radius-lg, 0.5rem);
  overflow: hidden;
  border: 1px solid var(--color-border-default, #e2e8f0);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

[data-theme="dark"] .screenshot-frame {
  border-color: var(--color-border-default-dark, #334155);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

/* 브라우저 크롬 모의 */
.screenshot-chrome {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #f1f5f9;
  border-bottom: 1px solid var(--color-border-default, #e2e8f0);
}

[data-theme="dark"] .screenshot-chrome {
  background: #1e293b;
  border-bottom-color: #334155;
}

.chrome-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.chrome-dot.red { background: #ef4444; }
.chrome-dot.yellow { background: #f59e0b; }
.chrome-dot.green { background: #22c55e; }

.chrome-url {
  margin-left: 8px;
  font-size: 12px;
  color: var(--color-text-tertiary, #94a3b8);
  background: var(--color-bg-primary, #ffffff);
  padding: 2px 12px;
  border-radius: 4px;
  flex: 1;
  max-width: 400px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

[data-theme="dark"] .chrome-url {
  background: #0f172a;
  color: #64748b;
}

.screenshot-body {
  position: relative;
  background: var(--color-bg-primary, #ffffff);
}

.screenshot-body img {
  display: block;
  width: 100%;
  height: auto;
}

/* 스크린샷 위 번호 주석 원형 */
.screenshot-annotation {
  position: absolute;
  width: 28px;
  height: 28px;
  background: var(--color-primary, #2563eb);
  color: #ffffff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 10;
  cursor: help;
  transition: transform 0.15s ease;
}

.screenshot-annotation:hover {
  transform: scale(1.15);
}
```

### Breadcrumb (이동 경로)

```css
.breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--spacing-2, 0.5rem);
  font-size: var(--font-size-sm, 0.875rem);
  color: var(--color-text-tertiary, #94a3b8);
  margin-bottom: var(--spacing-6, 1.5rem);
}

.breadcrumb a {
  color: var(--color-primary, #2563eb);
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}
```

### Chapter Navigation (이전/다음)

```css
.chapter-nav {
  display: flex;
  justify-content: space-between;
  margin-top: var(--spacing-12, 3rem);
  padding-top: var(--spacing-6, 1.5rem);
  border-top: 1px solid var(--color-border-default, #e2e8f0);
  gap: var(--spacing-4, 1rem);
}

.nav-prev,
.nav-next {
  display: flex;
  flex-direction: column;
  padding: var(--spacing-4, 1rem);
  border: 1px solid var(--color-border-default, #e2e8f0);
  border-radius: var(--radius-md, 0.375rem);
  text-decoration: none;
  color: inherit;
  transition: border-color 0.15s ease;
  max-width: 45%;
}

.nav-prev:hover,
.nav-next:hover {
  border-color: var(--color-primary, #2563eb);
}

.nav-next {
  text-align: right;
  margin-left: auto;
}

@media (max-width: 767px) {
  .chapter-nav {
    flex-direction: column;
  }
  .nav-prev, .nav-next {
    max-width: 100%;
  }
}
```

### Responsive Tabs (반응형 스크린샷 탭)

```css
.responsive-preview {
  margin-top: var(--spacing-8, 2rem);
}

.responsive-tabs {
  display: flex;
  gap: var(--spacing-1, 0.25rem);
  margin-bottom: var(--spacing-4, 1rem);
  background: var(--color-bg-secondary, #f8fafc);
  border-radius: var(--radius-md, 0.375rem);
  padding: 4px;
}

.responsive-tabs .tab {
  flex: 1;
  padding: var(--spacing-2, 0.5rem) var(--spacing-4, 1rem);
  border: none;
  background: transparent;
  border-radius: var(--radius-sm, 0.25rem);
  cursor: pointer;
  font-size: var(--font-size-sm, 0.875rem);
  color: var(--color-text-secondary, #64748b);
  transition: all 0.15s ease;
}

.responsive-tabs .tab.active {
  background: var(--color-bg-primary, #ffffff);
  color: var(--color-text-primary, #1a1a2e);
  font-weight: var(--font-weight-semibold, 600);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.tab-content {
  display: none;
}

.tab-content.active {
  display: block;
}

.tab-content img {
  display: block;
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-md, 0.375rem);
  border: 1px solid var(--color-border-default, #e2e8f0);
}
```

### TOC Sidebar (사이드바 목차)

```css
.toc-nav {
  padding: 0 var(--spacing-3, 0.75rem);
}

.toc-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-nav li {
  margin-bottom: 2px;
}

.toc-nav a {
  display: block;
  padding: var(--spacing-2, 0.5rem) var(--spacing-3, 0.75rem);
  font-size: var(--font-size-sm, 0.875rem);
  color: var(--color-text-secondary, #64748b);
  text-decoration: none;
  border-radius: var(--radius-sm, 0.25rem);
  transition: all 0.15s ease;
  border-left: 2px solid transparent;
}

.toc-nav a:hover {
  background: rgba(37, 99, 235, 0.05);
  color: var(--color-text-primary, #1a1a2e);
}

.toc-nav a.active {
  background: rgba(37, 99, 235, 0.08);
  color: var(--color-primary, #2563eb);
  border-left-color: var(--color-primary, #2563eb);
  font-weight: var(--font-weight-medium, 500);
}

/* 들여쓰기 (섹션 레벨) */
.toc-nav .toc-section {
  padding-left: var(--spacing-6, 1.5rem);
  font-size: var(--font-size-xs, 0.75rem);
}
```

### Search Overlay (검색 모달)

```css
.search-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 15vh;
  backdrop-filter: blur(4px);
}

.search-overlay[hidden] {
  display: none;
}

.search-modal {
  background: var(--color-bg-primary, #ffffff);
  border-radius: var(--radius-xl, 0.75rem);
  width: 90%;
  max-width: 600px;
  max-height: 70vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
}

[data-theme="dark"] .search-modal {
  background: var(--color-bg-secondary-dark, #1e293b);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

.search-input {
  width: 100%;
  padding: var(--spacing-4, 1rem) var(--spacing-5, 1.25rem);
  border: none;
  border-bottom: 1px solid var(--color-border-default, #e2e8f0);
  font-size: var(--font-size-lg, 1.125rem);
  outline: none;
  background: transparent;
  color: inherit;
}

.search-results {
  overflow-y: auto;
  flex: 1;
}

.search-result-item {
  display: block;
  padding: var(--spacing-3, 0.75rem) var(--spacing-5, 1.25rem);
  text-decoration: none;
  color: inherit;
  border-bottom: 1px solid var(--color-border-default, #e2e8f0);
  transition: background 0.1s ease;
}

.search-result-item:hover,
.search-result-item.selected {
  background: var(--color-bg-secondary, #f8fafc);
}

.search-result-chapter {
  font-size: var(--font-size-xs, 0.75rem);
  color: var(--color-primary, #2563eb);
  margin-bottom: 2px;
}

.search-result-title {
  font-weight: var(--font-weight-semibold, 600);
  margin-bottom: 2px;
}

.search-result-excerpt {
  font-size: var(--font-size-sm, 0.875rem);
  color: var(--color-text-tertiary, #94a3b8);
}

.search-result-excerpt mark {
  background: #fef08a;
  color: inherit;
  border-radius: 2px;
  padding: 0 2px;
}

.search-footer {
  padding: var(--spacing-2, 0.5rem) var(--spacing-4, 1rem);
  font-size: var(--font-size-xs, 0.75rem);
  color: var(--color-text-tertiary, #94a3b8);
  border-top: 1px solid var(--color-border-default, #e2e8f0);
  text-align: center;
}
```

## 3. manual-print.css — 인쇄용

```css
@media print {
  .manual-header,
  .toc-sidebar,
  .sidebar-toggle,
  .header-actions,
  .search-overlay,
  .chapter-nav,
  .responsive-tabs {
    display: none !important;
  }

  .manual-content {
    margin-left: 0 !important;
    padding: 0 !important;
    max-width: 100% !important;
  }

  .chapter {
    max-width: 100% !important;
  }

  body {
    font-size: 11pt;
    line-height: 1.5;
    color: #000;
    background: #fff;
  }

  .step-card {
    break-inside: avoid;
    border: 1px solid #ccc;
    page-break-inside: avoid;
  }

  .screenshot-frame {
    break-inside: avoid;
    page-break-inside: avoid;
    box-shadow: none;
    border: 1px solid #ccc;
  }

  .screenshot-chrome {
    display: none;
  }

  a[href]::after {
    content: " (" attr(href) ")";
    font-size: 9pt;
    color: #666;
  }

  a[href^="#"]::after,
  a[href^="javascript"]::after {
    content: none;
  }

  .callout-tip, .callout-note,
  .callout-warning, .callout-danger {
    border: 1px solid #ccc;
    background: #f9f9f9 !important;
    color: #000 !important;
  }
}
```

## 4. JavaScript 템플릿

### shared/nav.js 핵심 기능

```javascript
// 기능 목록 (구현 가이드):
// 1. 사이드바 토글: .sidebar-toggle 클릭 시 .toc-sidebar에 .open 클래스 토글
// 2. 스크롤스파이: IntersectionObserver로 현재 보이는 섹션 감지 → TOC에서 .active 클래스 이동
// 3. 챕터 내비게이션: ← → 키보드 이벤트로 prev/next 링크 이동
// 4. 모바일 오버레이 닫기: 사이드바 외부 클릭 시 닫기
// 5. 반응형 탭: .responsive-tabs .tab 클릭 시 .tab-content 전환
```

### shared/search.js 핵심 기능

```javascript
// 기능 목록 (구현 가이드):
// 1. search-index.json fetch → 메모리에 저장
// 2. Cmd+K / Ctrl+K → 검색 오버레이 열기
// 3. 입력 시 실시간 필터링 (title + content 매칭)
// 4. 결과 하이라이트 (매칭 키워드 <mark> 감싸기)
// 5. ↑↓ 키로 결과 선택, Enter로 이동
// 6. ESC로 닫기
```

### shared/theme.js 핵심 기능

```javascript
// 기능 목록 (구현 가이드):
// 1. 다크 모드 토글: html[data-theme] 속성 전환 + localStorage 저장
// 2. 시스템 테마 감지: prefers-color-scheme 미디어 쿼리 → 초기값 설정
// 3. 폰트 크기 조절: html[data-font] 속성 순환 (small → medium → large) + localStorage 저장
// 4. 페이지 로드 시 저장된 설정 복원
```
