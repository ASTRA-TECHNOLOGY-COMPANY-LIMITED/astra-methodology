# Manual HTML Templates

Defines the HTML structure templates to use when generating a manual.

## 1. Chapter HTML Template

Each chapter file `chapters/{NN}-{name}.html`:

```html
<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{chapter-title} — {project-name} Manual</title>
  <link rel="stylesheet" href="../assets/tokens.css">
  <link rel="stylesheet" href="../assets/manual-base.css">
  <link rel="stylesheet" href="../assets/manual-components.css">
  <link rel="stylesheet" href="../assets/manual-print.css" media="print">
</head>
<body>
  <!-- Top header -->
  <header class="manual-header">
    <button class="sidebar-toggle" aria-label="Menu">☰</button>
    <h1 class="manual-title">{project-name} Manual</h1>
    <div class="header-actions">
      <button class="search-trigger" aria-label="Search">🔍</button>
      <button class="theme-toggle" aria-label="Toggle theme">🌙</button>
      <button class="font-size-toggle" aria-label="Font size">A</button>
    </div>
  </header>

  <div class="manual-layout">
    <!-- Sidebar TOC -->
    <aside class="toc-sidebar" id="tocSidebar">
      <nav class="toc-nav" aria-label="Table of contents">
        <!-- TOC entries: statically insert every chapter link -->
        <ul>
          <li><a href="01-getting-started.html">01. Getting Started</a></li>
          <!-- ... remaining chapters ... -->
        </ul>
      </nav>
    </aside>

    <!-- Main content -->
    <main class="manual-content">
      <nav class="breadcrumb">
        <a href="../index.html">Manual</a> › <span>{chapter-title}</span>
      </nav>

      <article class="chapter" data-chapter="{NN}">
        <h1>{chapter-title}</h1>
        <p class="chapter-intro">{Chapter intro — 1–2 sentences on what you will learn}</p>

        <!-- Step-by-step guide -->
        <section class="steps">
          <h2>{section title}</h2>

          <div class="step-card" id="step-1">
            <div class="step-number">1</div>
            <div class="step-content">
              <h3>{step title}</h3>
              <p>{step description — plain language, second person}</p>
              <div class="screenshot-frame">
                <div class="screenshot-chrome">
                  <span class="chrome-dot red"></span>
                  <span class="chrome-dot yellow"></span>
                  <span class="chrome-dot green"></span>
                  <span class="chrome-url">{url}</span>
                </div>
                <div class="screenshot-body">
                  <img src="../screenshots/desktop/{chapter}-step-1.png"
                       alt="{screenshot description}"
                       loading="lazy">
                </div>
              </div>
              <!-- Optional: tip / caution box -->
              <div class="callout-tip">
                <strong>TIP</strong>: {helpful extra information}
              </div>
            </div>
          </div>

          <div class="step-card" id="step-2">
            <div class="step-number">2</div>
            <div class="step-content">
              <h3>{next step title}</h3>
              <p>{next step description}</p>
              <!-- Repeat screenshot + description -->
            </div>
          </div>
        </section>

        <!-- Responsive screenshots (only when RESPONSIVE_MODE >= 2) -->
        <section class="responsive-preview">
          <h2>Screen across different devices</h2>
          <div class="responsive-tabs">
            <button class="tab active" data-target="desktop">Desktop</button>
            <button class="tab" data-target="tablet">Tablet</button>
            <button class="tab" data-target="mobile">Mobile</button>
          </div>
          <div class="tab-content active" data-viewport="desktop">
            <img src="../screenshots/desktop/{chapter}-overview.png" alt="Desktop view" loading="lazy">
          </div>
          <div class="tab-content" data-viewport="tablet">
            <img src="../screenshots/tablet/{chapter}-overview.png" alt="Tablet view" loading="lazy">
          </div>
          <div class="tab-content" data-viewport="mobile">
            <img src="../screenshots/mobile/{chapter}-overview.png" alt="Mobile view" loading="lazy">
          </div>
        </section>
      </article>

      <!-- Chapter navigation -->
      <nav class="chapter-nav">
        <a href="{prev-chapter}.html" class="nav-prev">
          ← Previous: {prev-chapter-title}
        </a>
        <a href="{next-chapter}.html" class="nav-next">
          Next: {next-chapter-title} →
        </a>
      </nav>
    </main>
  </div>

  <!-- Search overlay -->
  <div class="search-overlay" id="searchOverlay" hidden>
    <div class="search-modal">
      <input type="search" class="search-input" placeholder="Search the manual..." autofocus>
      <div class="search-results"></div>
      <div class="search-footer">ESC to close · Enter to go</div>
    </div>
  </div>

  <script src="../shared/nav.js"></script>
  <script src="../shared/search.js"></script>
  <script src="../shared/theme.js"></script>
</body>
</html>
```

## 2. Index (Cover) HTML Template

`docs/manual/{feature-name}/index.html`:

```html
<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{project-name} — Service Manual</title>
  <link rel="stylesheet" href="assets/tokens.css">
  <link rel="stylesheet" href="assets/manual-base.css">
  <link rel="stylesheet" href="assets/manual-components.css">
  <link rel="stylesheet" href="assets/manual-print.css" media="print">
</head>
<body>
  <header class="manual-header">
    <h1 class="manual-title">{project-name} Manual</h1>
    <div class="header-actions">
      <button class="search-trigger" aria-label="Search">🔍</button>
      <button class="theme-toggle" aria-label="Toggle theme">🌙</button>
    </div>
  </header>

  <main class="index-content">
    <!-- Cover section -->
    <section class="cover">
      <h1 class="cover-title">{project-name}</h1>
      <p class="cover-subtitle">Service Manual</p>
      <div class="cover-meta">
        <span>Version: {version}</span>
        <span>Created: {date}</span>
        <span>Last updated: {date}</span>
      </div>
    </section>

    <!-- Quick-start callout -->
    <section class="quick-start-callout">
      <h2>First time here?</h2>
      <p>Check the getting-started guide for the basics.</p>
      <a href="chapters/01-getting-started.html" class="cta-button">Get started →</a>
    </section>

    <!-- Search -->
    <section class="index-search">
      <input type="search" class="search-input-large" placeholder="Search for what you need...">
    </section>

    <!-- Table of contents -->
    <section class="index-toc">
      <h2>Table of Contents</h2>
      <div class="toc-grid">
        <!-- Chapter card: repeated per chapter -->
        <a href="chapters/{NN}-{name}.html" class="toc-card">
          <span class="toc-card-number">{NN}</span>
          <h3>{chapter title}</h3>
          <p>{brief description}</p>
          <span class="toc-card-meta">{N} steps · {N} screenshots</span>
        </a>
      </div>
    </section>
  </main>

  <footer class="manual-footer">
    <p>This manual was auto-generated by the ASTRA methodology.</p>
  </footer>

  <!-- Search overlay -->
  <div class="search-overlay" id="searchOverlay" hidden>
    <div class="search-modal">
      <input type="search" class="search-input" placeholder="Search the manual..." autofocus>
      <div class="search-results"></div>
      <div class="search-footer">ESC to close · Enter to go</div>
    </div>
  </div>

  <script src="shared/nav.js"></script>
  <script src="shared/search.js"></script>
  <script src="shared/theme.js"></script>
</body>
</html>
```

## 3. search-index.json Format

```json
[
  {
    "chapter": "01",
    "title": "Getting Started",
    "url": "chapters/01-getting-started.html",
    "sections": [
      { "heading": "Service Overview", "anchor": "#intro", "content": "first 200 chars..." },
      { "heading": "How to Access", "anchor": "#access", "content": "first 200 chars..." }
    ]
  },
  {
    "chapter": "02",
    "title": "{feature name}",
    "url": "chapters/02-{name}.html",
    "sections": [
      { "heading": "{section title}", "anchor": "#{anchor}", "content": "first 200 chars..." }
    ]
  }
]
```

Each section's `content` includes the first 200 characters of the section body (for client-side search matching).

## 4. FAQ Chapter Template

```html
<!-- FAQ accordion format -->
<section class="faq-section">
  <h2>{category}</h2>

  <details class="faq-item">
    <summary class="faq-question">{question — "How do I ...?" form}</summary>
    <div class="faq-answer">
      <p>{answer intro}</p>
      <ol>
        <li>{step 1}</li>
        <li>{step 2}</li>
      </ol>
      <p>For details, see <a href="{related chapter link}">{related chapter name}</a>.</p>
    </div>
  </details>

  <details class="faq-item">
    <summary class="faq-question">{next question}</summary>
    <div class="faq-answer">...</div>
  </details>
</section>
```

## 5. Glossary Chapter Template

```html
<!-- Glossary — definition list format -->
<section class="glossary-section">
  <dl class="glossary-list">
    <dt id="term-{id}">{term}</dt>
    <dd>{definition}</dd>

    <dt id="term-{id}">{term}</dt>
    <dd>{definition}</dd>
  </dl>
</section>
```
