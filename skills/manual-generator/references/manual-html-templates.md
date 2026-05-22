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

## 6. Help Center Index Template (DESIGN_TONE = "Help Center")

A search-driven landing variant of the index page that replaces Section 2's plain cover + TOC grid. Use this layout when `DESIGN_TONE = Help Center` is chosen in Step 0.E. Composition:

1. **Sticky dark header** — brand mark + product link + language switch
2. **Hero with large search input** — gradient-tinted background, centered title, prominent search box
3. **FAQ grid (2-column)** — top frequently-asked questions extracted from `usecase` exception flows
4. **Category cards (3-column)** — one card per top-level feature group, linking to the feature's first chapter
5. **Banner CTAs (2-row, gradient + soft)** — optional links to video guides / academy / changelog
6. **Contact CTA** — fallback callout when the user cannot find an answer
7. **Multi-column footer**

Brand colors and gradient come from `assets/tokens.css` via `var(--primary-blue)`, `var(--primary-purple)`, `var(--brand-gradient)`. Do **not** hardcode `#155EEF` / `#7F56D9` — these are the reference document's brand values and must not leak into other projects.

```html
<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{PROJECT_NAME}} — Help Center</title>
  <link rel="stylesheet" href="assets/tokens.css">
  <link rel="stylesheet" href="assets/manual-base.css">
  <link rel="stylesheet" href="assets/manual-components.css">
  <link rel="stylesheet" href="assets/manual-helpcenter.css">
  <link rel="stylesheet" href="assets/manual-print.css" media="print">
</head>
<body class="hc-body">
  <header class="hc-header">
    <div class="hc-wrap nav">
      <a class="brand" href="index.html">
        <span class="brand-mark">{{PROJECT_NAME}}</span>
        <span class="sep"></span>
        <span class="tag">Help Center</span>
      </a>
      <nav class="nav-right">
        <a class="nav-link" href="index.html">Home</a>
        <a class="nav-link" href="{{SERVICE_URL}}" target="_blank" rel="noopener">Go to {{PROJECT_NAME}} →</a>
      </nav>
    </div>
  </header>

  <section class="hero">
    <div class="hc-wrap">
      <h1 class="hero-title">How can we <span class="grad">help you?</span></h1>
      <p class="hero-sub">{{TAGLINE}}</p>
      <div class="search" role="search">
        <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input id="hcSearch" type="search" placeholder="Search guides..." aria-label="Search guides">
      </div>
    </div>
  </section>

  <main class="hc-wrap">
    <!-- FAQ grid (extracted from usecase exception flows) -->
    <section class="hc-section">
      <div class="section-label">— FREQUENTLY ASKED —</div>
      <h2 class="sec-title">Top questions</h2>
      <div class="faq-grid" id="faqGrid">
        <!-- repeated per FAQ -->
        <a class="faq-card" href="chapters/{{NN}}-{{name}}.html#{{anchor}}">
          <span class="faq-badge">NEW</span>
          <span class="faq-q">{{question}}</span>
          <span class="faq-arrow">→</span>
        </a>
      </div>
    </section>

    <!-- Category cards (one per top-level feature group) -->
    <section class="hc-section">
      <div class="section-label purple">— BROWSE GUIDES —</div>
      <div class="sec-head">
        <h2 class="sec-title">Browse guides</h2>
        <span class="sec-sub">Organized by category</span>
      </div>
      <div class="col-grid" id="colGrid">
        <!-- repeated per category -->
        <a class="cat-card" href="chapters/{{first-chapter-of-category}}.html">
          <div class="cat-ic">
            <svg viewBox="0 0 24 24" aria-hidden="true">{{INLINE_SVG_ICON}}</svg>
          </div>
          <span class="cat-tag">{{CATEGORY_TAG}}</span>
          <h3 class="cat-title">{{category title}}</h3>
          <p class="cat-meta">{{N}} articles</p>
        </a>
      </div>
      <p class="no-result" id="noResult" hidden>No results found.</p>
    </section>

    <!-- Optional banner CTAs (omit if unused) -->
    <section class="band">
      <div class="banner grad">
        <div class="bl">
          <div class="blabel">— VIDEO GUIDE —</div>
          <h3>{{VIDEO_TITLE}}</h3>
          <p>{{VIDEO_DESC}}</p>
        </div>
        <a class="btn" href="{{VIDEO_URL}}">Watch video guides →</a>
      </div>
      <div class="banner soft">
        <div class="bl">
          <div class="blabel">— CHANGELOG —</div>
          <h3>{{CHANGELOG_TITLE}}</h3>
          <p>{{CHANGELOG_DESC}}</p>
        </div>
        <a class="btn" href="{{CHANGELOG_URL}}">See updates →</a>
      </div>
    </section>

    <!-- Contact CTA -->
    <section class="hc-section">
      <div class="cta">
        <h3>Didn't find what you need?</h3>
        <p>{{SUPPORT_CTA_DESC}}</p>
        <a class="btn-primary" href="{{SUPPORT_URL}}">Contact us</a>
      </div>
    </section>
  </main>

  <footer class="hc-footer">
    <div class="hc-wrap">
      <p class="copy">© {{YEAR}} {{PROJECT_NAME}}. Generated by ASTRA methodology.</p>
    </div>
  </footer>

  <!-- Search overlay (shared with chapter pages) -->
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

### Placeholder reference

| Placeholder | Source |
|-------------|--------|
| `{{PROJECT_NAME}}` | `CLAUDE.md` project name (Step 0.B) |
| `{{TAGLINE}}` | one-line service description, extracted from blueprint overview or planner market-analysis |
| `{{SERVICE_URL}}` | the URL collected in Step 0.A |
| `{{NN}}-{{name}}` / `{{anchor}}` | chapter file name + heading anchor for the FAQ source section |
| `{{CATEGORY_TAG}}` | one of `SETUP / FEATURES / PARTNERS / NOTICE / USE CASES` (uppercase, kebab-case allowed) — derive from chapter grouping |
| `{{INLINE_SVG_ICON}}` | inline SVG path data. The reference set in `manual-helpcenter.css` includes `rocket / gear / handshake / bell / bulb / book`. Choose one per category. |
| `{{VIDEO_URL}}` / `{{CHANGELOG_URL}}` / `{{SUPPORT_URL}}` | optional — when not provided, omit the entire `.band` and `.cta` blocks |
| `{{YEAR}}` | current year |

### Category ↔ chapter grouping rule

When generating the Help Center index, group chapters into 3–5 categories. Typical mapping:

| Category | Chapters | Suggested icon |
|----------|----------|----------------|
| Setup | 01-getting-started, sign-up, environment-setup | rocket |
| Features | core feature chapters | gear |
| Partners (optional) | admin / partner-API / integration | handshake |
| Notice | release-notes / changelog | bell |
| Use cases | tutorials / advanced flows | bulb |

Each `cat-card` links to the *first chapter* of its category. The category subtree is then navigated via the chapter sidebar TOC.

### FAQ source

Reuse the FAQ list authored in **Chapter NN-1: FAQ / Troubleshooting** (Section 4 template). Pick the top 4–6 entries by frequency or by `<details open>` marker. Each card's `href` points to the corresponding `#anchor` inside the FAQ chapter.
