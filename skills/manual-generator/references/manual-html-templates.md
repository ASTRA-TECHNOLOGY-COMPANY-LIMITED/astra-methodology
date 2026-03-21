# 매뉴얼 HTML 템플릿

매뉴얼 생성 시 사용할 HTML 구조 템플릿을 정의한다.

## 1. 챕터 HTML 템플릿

각 챕터 파일 `chapters/{NN}-{name}.html`:

```html
<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{chapter-title} — {project-name} 매뉴얼</title>
  <link rel="stylesheet" href="../assets/tokens.css">
  <link rel="stylesheet" href="../assets/manual-base.css">
  <link rel="stylesheet" href="../assets/manual-components.css">
  <link rel="stylesheet" href="../assets/manual-print.css" media="print">
</head>
<body>
  <!-- 상단 헤더 -->
  <header class="manual-header">
    <button class="sidebar-toggle" aria-label="메뉴">☰</button>
    <h1 class="manual-title">{project-name} 매뉴얼</h1>
    <div class="header-actions">
      <button class="search-trigger" aria-label="검색">🔍</button>
      <button class="theme-toggle" aria-label="테마 변경">🌙</button>
      <button class="font-size-toggle" aria-label="글자 크기">A</button>
    </div>
  </header>

  <div class="manual-layout">
    <!-- 사이드바 TOC -->
    <aside class="toc-sidebar" id="tocSidebar">
      <nav class="toc-nav" aria-label="목차">
        <!-- TOC 항목: 모든 챕터 링크를 정적으로 삽입 -->
        <ul>
          <li><a href="01-getting-started.html">01. 시작하기</a></li>
          <!-- ... 나머지 챕터 ... -->
        </ul>
      </nav>
    </aside>

    <!-- 메인 콘텐츠 -->
    <main class="manual-content">
      <nav class="breadcrumb">
        <a href="../index.html">매뉴얼</a> › <span>{chapter-title}</span>
      </nav>

      <article class="chapter" data-chapter="{NN}">
        <h1>{chapter-title}</h1>
        <p class="chapter-intro">{챕터 소개 — 이 챕터에서 배울 내용 1-2문장}</p>

        <!-- 단계별 가이드 -->
        <section class="steps">
          <h2>{섹션 제목}</h2>

          <div class="step-card" id="step-1">
            <div class="step-number">1</div>
            <div class="step-content">
              <h3>{단계 제목}</h3>
              <p>{단계 설명 — 평이한 언어, 2인칭}</p>
              <div class="screenshot-frame">
                <div class="screenshot-chrome">
                  <span class="chrome-dot red"></span>
                  <span class="chrome-dot yellow"></span>
                  <span class="chrome-dot green"></span>
                  <span class="chrome-url">{url}</span>
                </div>
                <div class="screenshot-body">
                  <img src="../screenshots/desktop/{chapter}-step-1.png"
                       alt="{스크린샷 설명}"
                       loading="lazy">
                </div>
              </div>
              <!-- 선택: 팁/주의 박스 -->
              <div class="callout-tip">
                <strong>TIP</strong>: {도움이 되는 추가 정보}
              </div>
            </div>
          </div>

          <div class="step-card" id="step-2">
            <div class="step-number">2</div>
            <div class="step-content">
              <h3>{다음 단계 제목}</h3>
              <p>{다음 단계 설명}</p>
              <!-- 스크린샷 + 설명 반복 -->
            </div>
          </div>
        </section>

        <!-- 반응형 스크린샷 (RESPONSIVE_MODE >= 2일 때만 포함) -->
        <section class="responsive-preview">
          <h2>다양한 기기에서의 화면</h2>
          <div class="responsive-tabs">
            <button class="tab active" data-target="desktop">데스크톱</button>
            <button class="tab" data-target="tablet">태블릿</button>
            <button class="tab" data-target="mobile">모바일</button>
          </div>
          <div class="tab-content active" data-viewport="desktop">
            <img src="../screenshots/desktop/{chapter}-overview.png" alt="데스크톱 화면" loading="lazy">
          </div>
          <div class="tab-content" data-viewport="tablet">
            <img src="../screenshots/tablet/{chapter}-overview.png" alt="태블릿 화면" loading="lazy">
          </div>
          <div class="tab-content" data-viewport="mobile">
            <img src="../screenshots/mobile/{chapter}-overview.png" alt="모바일 화면" loading="lazy">
          </div>
        </section>
      </article>

      <!-- 챕터 내비게이션 -->
      <nav class="chapter-nav">
        <a href="{prev-chapter}.html" class="nav-prev">
          ← 이전: {prev-chapter-title}
        </a>
        <a href="{next-chapter}.html" class="nav-next">
          다음: {next-chapter-title} →
        </a>
      </nav>
    </main>
  </div>

  <!-- 검색 오버레이 -->
  <div class="search-overlay" id="searchOverlay" hidden>
    <div class="search-modal">
      <input type="search" class="search-input" placeholder="매뉴얼 검색..." autofocus>
      <div class="search-results"></div>
      <div class="search-footer">ESC로 닫기 · Enter로 이동</div>
    </div>
  </div>

  <script src="../shared/nav.js"></script>
  <script src="../shared/search.js"></script>
  <script src="../shared/theme.js"></script>
</body>
</html>
```

## 2. 인덱스(표지) HTML 템플릿

`docs/manual/{feature-name}/index.html`:

```html
<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{project-name} — 서비스 매뉴얼</title>
  <link rel="stylesheet" href="assets/tokens.css">
  <link rel="stylesheet" href="assets/manual-base.css">
  <link rel="stylesheet" href="assets/manual-components.css">
  <link rel="stylesheet" href="assets/manual-print.css" media="print">
</head>
<body>
  <header class="manual-header">
    <h1 class="manual-title">{project-name} 매뉴얼</h1>
    <div class="header-actions">
      <button class="search-trigger" aria-label="검색">🔍</button>
      <button class="theme-toggle" aria-label="테마 변경">🌙</button>
    </div>
  </header>

  <main class="index-content">
    <!-- 표지 섹션 -->
    <section class="cover">
      <h1 class="cover-title">{project-name}</h1>
      <p class="cover-subtitle">서비스 매뉴얼</p>
      <div class="cover-meta">
        <span>버전: {version}</span>
        <span>생성일: {date}</span>
        <span>최종 수정: {date}</span>
      </div>
    </section>

    <!-- 빠른 시작 안내 -->
    <section class="quick-start-callout">
      <h2>처음 사용하시나요?</h2>
      <p>시작하기 가이드에서 기본적인 사용법을 확인하세요.</p>
      <a href="chapters/01-getting-started.html" class="cta-button">시작하기 →</a>
    </section>

    <!-- 검색 -->
    <section class="index-search">
      <input type="search" class="search-input-large" placeholder="궁금한 내용을 검색하세요...">
    </section>

    <!-- 목차 -->
    <section class="index-toc">
      <h2>목차</h2>
      <div class="toc-grid">
        <!-- 챕터 카드: 각 챕터마다 반복 -->
        <a href="chapters/{NN}-{name}.html" class="toc-card">
          <span class="toc-card-number">{NN}</span>
          <h3>{챕터 제목}</h3>
          <p>{간략 설명}</p>
          <span class="toc-card-meta">{N}단계 · {N}장 스크린샷</span>
        </a>
      </div>
    </section>
  </main>

  <footer class="manual-footer">
    <p>이 매뉴얼은 ASTRA 방법론으로 자동 생성되었습니다.</p>
  </footer>

  <!-- 검색 오버레이 -->
  <div class="search-overlay" id="searchOverlay" hidden>
    <div class="search-modal">
      <input type="search" class="search-input" placeholder="매뉴얼 검색..." autofocus>
      <div class="search-results"></div>
      <div class="search-footer">ESC로 닫기 · Enter로 이동</div>
    </div>
  </div>

  <script src="shared/nav.js"></script>
  <script src="shared/search.js"></script>
  <script src="shared/theme.js"></script>
</body>
</html>
```

## 3. search-index.json 형식

```json
[
  {
    "chapter": "01",
    "title": "시작하기",
    "url": "chapters/01-getting-started.html",
    "sections": [
      { "heading": "서비스 소개", "anchor": "#intro", "content": "처음 200자..." },
      { "heading": "접속 방법", "anchor": "#access", "content": "처음 200자..." }
    ]
  },
  {
    "chapter": "02",
    "title": "{기능명}",
    "url": "chapters/02-{name}.html",
    "sections": [
      { "heading": "{섹션 제목}", "anchor": "#{anchor}", "content": "처음 200자..." }
    ]
  }
]
```

각 섹션의 `content`는 해당 섹션 본문 텍스트의 처음 200자를 포함한다 (클라이언트 검색 매칭용).

## 4. FAQ 챕터 템플릿

```html
<!-- FAQ 아코디언 형식 -->
<section class="faq-section">
  <h2>{카테고리}</h2>

  <details class="faq-item">
    <summary class="faq-question">{질문 — "~하려면 어떻게 하나요?" 형식}</summary>
    <div class="faq-answer">
      <p>{답변 도입}</p>
      <ol>
        <li>{단계 1}</li>
        <li>{단계 2}</li>
      </ol>
      <p>자세한 내용은 <a href="{관련 챕터 링크}">{관련 챕터명}</a>을 참조하세요.</p>
    </div>
  </details>

  <details class="faq-item">
    <summary class="faq-question">{다음 질문}</summary>
    <div class="faq-answer">...</div>
  </details>
</section>
```

## 5. 용어집 챕터 템플릿

```html
<!-- 용어집 — 정의 목록 형식 -->
<section class="glossary-section">
  <dl class="glossary-list">
    <dt id="term-{id}">{용어}</dt>
    <dd>{정의}</dd>

    <dt id="term-{id}">{용어}</dt>
    <dd>{정의}</dd>
  </dl>
</section>
```
