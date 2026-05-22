# Manual CSS Component Templates

Defines the detailed specs and code templates for the CSS components used in manual generation. All CSS references design tokens from `assets/tokens.css` via `var()`.

## 1. manual-base.css — Layout

### Core layout structure

```css
/* Manual layout — optimized for reading */

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

/* Font size adjustment (wired up by theme.js) */
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

/* Dark mode */
[data-theme="dark"] body {
  color: var(--color-text-primary-dark, #e2e8f0);
  background-color: var(--color-bg-primary-dark, #0f172a);
}

/* Top header (64px) */
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

/* Main layout — sidebar + content */
.manual-layout {
  display: flex;
  min-height: 100vh;
  padding-top: 64px;
}

/* Sidebar TOC (240px, sticky) */
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

/* Main content (max-width 800px, reading-optimized) */
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

/* Responsive: tablet */
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

/* Responsive: mobile */
@media (max-width: 767px) {
  .manual-content {
    padding: var(--spacing-4, 1rem);
  }
  .chapter h1 {
    font-size: var(--font-size-2xl, 1.5rem);
  }
}
```

### Index page only

```css
/* index.html — cover + table of contents */
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

/* TOC card grid */
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

/* Footer */
.manual-footer {
  text-align: center;
  padding: var(--spacing-8, 2rem) var(--spacing-4, 1rem);
  margin-top: var(--spacing-12, 3rem);
  border-top: 1px solid var(--color-border-default, #e2e8f0);
  font-size: var(--font-size-sm, 0.875rem);
  color: var(--color-text-tertiary, #94a3b8);
}

/* Large search input (index page) */
.search-input-large {
  width: 100%;
  max-width: 560px;
  margin: 0 auto;
  display: block;
  padding: var(--spacing-4, 1rem) var(--spacing-5, 1.25rem);
  border: 1px solid var(--color-border-default, #e2e8f0);
  border-radius: var(--radius-lg, 0.5rem);
  font-size: var(--font-size-lg, 1.125rem);
  outline: none;
  background: var(--color-bg-primary, #ffffff);
  color: inherit;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.search-input-large:focus {
  border-color: var(--color-primary, #2563eb);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

[data-theme="dark"] .search-input-large {
  background: var(--color-bg-secondary-dark, #1e293b);
  border-color: var(--color-border-default-dark, #334155);
}
```

## 2. manual-components.css — Components

### Step Card

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

### Callout Boxes

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

/* Dark-mode callouts */
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

### Screenshot Frame

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

/* Mock browser chrome */
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

/* Numbered annotation circle over screenshot */
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

### Breadcrumb

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

### Chapter Navigation (Prev/Next)

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

### Responsive Tabs (responsive screenshot tabs)

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

### TOC Sidebar

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

/* Indentation (section level) */
.toc-nav .toc-section {
  padding-left: var(--spacing-6, 1.5rem);
  font-size: var(--font-size-xs, 0.75rem);
}
```

### Search Overlay (search modal)

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

## 3. manual-print.css — Print

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

## 4. JavaScript Templates

### Core features of shared/nav.js

```javascript
// Feature list (implementation guide):
// 1. Sidebar toggle: clicking .sidebar-toggle toggles .open on .toc-sidebar
// 2. Scrollspy: IntersectionObserver detects the section currently in view → moves .active on the TOC entry
// 3. Chapter navigation: ← → keyboard events to follow the prev/next link
// 4. Mobile overlay close: clicking outside the sidebar closes it
// 5. Responsive tabs: clicking .responsive-tabs .tab switches the active .tab-content
```

### Core features of shared/search.js

```javascript
// Feature list (implementation guide):
// 1. Fetch search-index.json → keep it in memory
// 2. Cmd+K / Ctrl+K → open the search overlay
// 3. Live filter on input (match against title + content)
// 4. Highlight results (wrap matched keywords with <mark>)
// 5. ↑↓ to select a result, Enter to navigate
// 6. ESC to close
```

### Core features of shared/theme.js

```javascript
// Feature list (implementation guide):
// 1. Dark-mode toggle: switch the html[data-theme] attribute + persist in localStorage
// 2. System-theme detection: prefers-color-scheme media query → use as the initial value
// 3. Font-size adjustment: cycle the html[data-font] attribute (small → medium → large) + persist in localStorage
// 4. On page load, restore the saved settings
```

## 5. manual-helpcenter.css — Help Center Index Components

Used **only** when `DESIGN_TONE = Help Center` (Step 0.E). The components below render the Section 6 HTML template in `manual-html-templates.md`. Loaded *in addition to* `manual-base.css` + `manual-components.css` — the chapter pages still use the standard sidebar+content layout.

All brand colors are read from `assets/tokens.css`. If the project's design tokens do not define `--primary-blue` / `--primary-purple` / `--brand-gradient`, the fallback values below kick in (intentional fallback, not duplication).

### Color + gradient tokens (fallbacks only)

```css
:root {
  --hc-primary: var(--primary-blue, #155EEF);
  --hc-primary-50: var(--primary-blue-50, #EFF4FF);
  --hc-primary-100: var(--primary-blue-100, #D1E0FF);
  --hc-accent: var(--primary-purple, #7F56D9);
  --hc-accent-50: var(--primary-purple-50, #F4F0FF);
  --hc-accent-100: var(--primary-purple-100, #E9D7FE);
  --hc-grad: var(--brand-gradient, linear-gradient(135deg, var(--hc-primary) 0%, var(--hc-accent) 100%));
  --hc-grad-soft: linear-gradient(135deg, var(--hc-primary-50) 0%, var(--hc-accent-50) 100%);
  --hc-grad-glow:
    radial-gradient(ellipse 60% 80% at 82% 38%, color-mix(in srgb, var(--hc-accent) 14%, transparent), transparent 65%),
    radial-gradient(ellipse 80% 60% at 12% 92%, color-mix(in srgb, var(--hc-primary) 14%, transparent), transparent 65%),
    linear-gradient(135deg, #FAFBFF 0%, #F5F2FE 100%);
  --hc-maxw: 1160px;
  --hc-shadow-card: 0 1px 2px rgba(16,24,40,.04), 0 8px 24px rgba(16,24,40,.05), 0 24px 48px color-mix(in srgb, var(--hc-primary) 4%, transparent);
  --hc-shadow-card-hover: 0 4px 8px rgba(16,24,40,.06), 0 16px 40px color-mix(in srgb, var(--hc-primary) 10%, transparent);
}

.hc-wrap { max-width: var(--hc-maxw); margin: 0 auto; padding: 0 32px; }
.hc-body { font-family: var(--font-family-sans, 'Pretendard', sans-serif); line-height: 1.7; }
```

### Header

```css
.hc-header {
  position: sticky; top: 0; z-index: 50;
  background: linear-gradient(135deg, #344054 0%, #475467 100%);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(255,255,255,.08);
}
.hc-header .nav { display: flex; align-items: center; justify-content: space-between; height: 72px; }
.hc-header .brand { display: flex; align-items: center; gap: 11px; color: #fff; }
.hc-header .brand-mark { font-weight: 700; font-size: 18px; letter-spacing: -.3px; }
.hc-header .sep { width: 1px; height: 20px; background: rgba(255,255,255,.25); }
.hc-header .tag { font-size: 14px; font-weight: 500; color: rgba(255,255,255,.72); }
.hc-header .nav-right { display: flex; align-items: center; gap: 20px; }
.hc-header .nav-link {
  color: rgba(255,255,255,.78); font-size: 14px; font-weight: 500;
  transition: color .2s;
}
.hc-header .nav-link:hover { color: #fff; }
```

### Hero with search

```css
.hero {
  position: relative;
  padding: 88px 0 72px;
  text-align: center;
  background: var(--hc-grad-glow);
  border-bottom: 1px solid var(--color-border, #E4E7EC);
}
.hero-title {
  font-size: clamp(32px, 4vw, 46px);
  font-weight: 800;
  letter-spacing: -1.5px;
  line-height: 1.22;
}
.hero-title .grad {
  background: var(--hc-grad);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero-sub {
  color: var(--color-text-muted, #475467);
  margin-top: 16px;
  font-size: 18px;
}
.hero .search {
  position: relative;
  max-width: 640px;
  margin: 38px auto 0;
  display: flex;
  align-items: center;
  gap: 13px;
  background: #fff;
  border: 1px solid var(--color-border, #E4E7EC);
  border-radius: 14px;
  padding: 17px 20px;
  box-shadow: var(--hc-shadow-card);
  transition: border-color .2s, box-shadow .2s;
}
.hero .search:focus-within {
  border-color: var(--hc-primary);
  box-shadow: 0 0 0 4px var(--hc-primary-50);
}
.hero .search input {
  flex: 1;
  border: 0;
  background: transparent;
  font-size: 16px;
  outline: none;
  color: var(--color-text-primary, #101828);
}
.hero .search svg {
  width: 21px; height: 21px;
  stroke: var(--color-text-muted, #98A2B3);
  fill: none;
  stroke-width: 2;
}
```

### Section heading

```css
.hc-section { padding: 60px 0; }
.section-label {
  font-family: 'DM Sans', var(--font-family-sans, sans-serif);
  font-size: 12px;
  font-weight: 500;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: var(--hc-primary);
  margin-bottom: 14px;
}
.section-label.purple { color: var(--hc-accent); }
.sec-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 26px;
}
.sec-title { font-size: 28px; font-weight: 700; letter-spacing: -.6px; }
.sec-sub { color: var(--color-text-muted, #667085); font-size: 14px; }
```

### FAQ grid (2-column)

```css
.faq-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}
.faq-card {
  display: flex;
  align-items: center;
  gap: 13px;
  background: #fff;
  border: 1px solid var(--color-border, #E4E7EC);
  border-radius: 12px;
  padding: 18px 20px;
  box-shadow: var(--hc-shadow-card);
  transition: .22s;
  color: inherit;
  text-decoration: none;
}
.faq-card:hover {
  border-color: var(--hc-primary-100);
  box-shadow: var(--hc-shadow-card-hover);
  transform: translateY(-2px);
}
.faq-q { font-size: 15px; font-weight: 500; }
.faq-badge {
  font-family: 'DM Sans', sans-serif;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .06em;
  color: #fff;
  background: var(--hc-primary);
  padding: 3px 8px;
  border-radius: 6px;
}
.faq-arrow {
  margin-left: auto;
  color: var(--color-text-muted, #98A2B3);
  transition: .2s;
}
.faq-card:hover .faq-arrow {
  color: var(--hc-primary);
  transform: translateX(3px);
}

@media (max-width: 768px) {
  .faq-grid { grid-template-columns: 1fr; }
}
```

### Category cards (3-column)

```css
.col-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}
.cat-card {
  background: #fff;
  border: 1px solid var(--color-border, #E4E7EC);
  border-radius: 18px;
  padding: 28px;
  box-shadow: var(--hc-shadow-card);
  transition: .25s;
  color: inherit;
  text-decoration: none;
  display: block;
}
.cat-card:hover {
  border-color: var(--hc-primary-100);
  transform: translateY(-4px);
  box-shadow: var(--hc-shadow-card-hover);
}
.cat-ic {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--hc-primary-50);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 18px;
}
.cat-ic svg {
  width: 24px;
  height: 24px;
  stroke: var(--hc-primary);
  stroke-width: 1.5;
  fill: none;
}
.cat-tag {
  display: inline-block;
  font-family: 'DM Sans', sans-serif;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .06em;
  padding: 4px 10px;
  border-radius: 6px;
  margin-bottom: 12px;
  background: var(--hc-primary-50);
  color: var(--hc-primary);
}
.cat-card.accent .cat-ic { background: var(--hc-accent-50); }
.cat-card.accent .cat-ic svg { stroke: var(--hc-accent); }
.cat-card.accent .cat-tag { background: var(--hc-accent-50); color: var(--hc-accent); }
.cat-title { font-size: 19px; font-weight: 700; margin-bottom: 6px; letter-spacing: -.3px; }
.cat-meta { color: var(--color-text-muted, #667085); font-size: 13px; }

@media (max-width: 1024px) { .col-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px)  { .col-grid { grid-template-columns: 1fr; } }
```

### Banner CTA (gradient + soft)

```css
.band { padding-top: 10px; display: flex; flex-direction: column; gap: 18px; }
.banner {
  position: relative;
  overflow: hidden;
  border-radius: 22px;
  padding: 42px 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 30px;
  flex-wrap: wrap;
}
.banner.grad { background: var(--hc-grad); }
.banner.grad::after {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 50% 80% at 88% 20%, rgba(255,255,255,.18), transparent 60%);
  pointer-events: none;
}
.banner.soft {
  background: var(--hc-grad-soft);
  border: 1px solid var(--hc-accent-100);
}
.banner .bl { position: relative; z-index: 1; }
.banner .blabel {
  font-family: 'DM Sans', sans-serif;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: .12em;
  text-transform: uppercase;
  margin-bottom: 12px;
}
.banner.grad .blabel { color: rgba(255,255,255,.7); }
.banner.soft .blabel { color: var(--hc-accent); }
.banner h3 { font-size: 24px; font-weight: 700; letter-spacing: -.5px; }
.banner.grad h3 { color: #fff; }
.banner.soft h3 { color: var(--color-text-primary, #101828); }
.banner p { font-size: 15px; margin-top: 8px; }
.banner.grad p { color: rgba(255,255,255,.85); }
.banner.soft p { color: var(--color-text-muted, #475467); }
.banner .btn {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  gap: 9px;
  font-family: 'DM Sans', sans-serif;
  font-weight: 700;
  font-size: 15px;
  padding: 15px 26px;
  border-radius: 10px;
  transition: .2s;
  white-space: nowrap;
  text-decoration: none;
}
.banner.grad .btn { background: #fff; color: var(--hc-primary); }
.banner.soft .btn { background: var(--hc-accent); color: #fff; }
.banner .btn:hover { transform: translateY(-1px); }
```

### Contact CTA

```css
.cta {
  text-align: center;
  background: var(--color-bg-subtle, #F9FAFB);
  border: 1px solid var(--color-border, #E4E7EC);
  border-radius: 18px;
  padding: 48px 32px;
}
.cta h3 { font-size: 22px; font-weight: 700; margin-bottom: 8px; }
.cta p { color: var(--color-text-muted, #475467); font-size: 15px; margin-bottom: 20px; }
.btn-primary {
  display: inline-block;
  background: var(--hc-primary);
  color: #fff;
  font-weight: 700;
  font-size: 15px;
  padding: 13px 26px;
  border-radius: 10px;
  text-decoration: none;
  transition: .2s;
}
.btn-primary:hover {
  background: color-mix(in srgb, var(--hc-primary) 92%, black);
}
```

### Footer

```css
.hc-footer {
  border-top: 1px solid var(--color-border, #E4E7EC);
  padding: 32px 0;
  margin-top: 60px;
}
.hc-footer .copy {
  color: var(--color-text-muted, #98A2B3);
  font-size: 13px;
  text-align: center;
}
```

### Dark-mode overrides

```css
[data-theme="dark"] .hc-body { background: var(--color-bg-primary-dark, #0f172a); }
[data-theme="dark"] .hero { background: linear-gradient(135deg, #1a1f3a 0%, #2a1f4a 100%); }
[data-theme="dark"] .faq-card,
[data-theme="dark"] .cat-card,
[data-theme="dark"] .cta {
  background: #1e293b;
  border-color: #334155;
  color: #e2e8f0;
}
[data-theme="dark"] .hero .search { background: #1e293b; border-color: #334155; }
[data-theme="dark"] .hero .search input { color: #e2e8f0; }
```

### Inline SVG icon set (paste into `{{INLINE_SVG_ICON}}` placeholders)

```html
<!-- rocket: setup / getting started -->
<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/>
<path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/>
<path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/>

<!-- gear: features / settings -->
<circle cx="12" cy="12" r="3"/>
<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>

<!-- handshake: partners / integrations -->
<path d="m11 17 2 2a1 1 0 1 0 3-3"/>
<path d="m14 14 2.5 2.5a1 1 0 1 0 3-3l-3.88-3.88a3 3 0 0 0-4.24 0l-.88.88a1 1 0 1 1-3-3l2.81-2.81a5.79 5.79 0 0 1 7.06-.87l.47.28a2 2 0 0 0 1.42.25L21 4"/>
<path d="m21 3 1 11h-2"/>
<path d="M3 3 2 14l6.5 6.5a1 1 0 1 0 3-3"/>
<path d="M3 4h8"/>

<!-- bell: announcements / notice -->
<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>
<path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>

<!-- bulb: use cases / tips -->
<path d="M9 18h6"/>
<path d="M10 22h4"/>
<path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"/>

<!-- book: glossary / reference -->
<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
<path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
```

### Search wiring (extends `shared/search.js`)

The Help Center search input (`#hcSearch`) reuses the existing `search-index.json`. Add the following snippet to `shared/search.js`:

```javascript
// Help Center hero search → live-filter FAQ + category cards
const hcInput = document.getElementById('hcSearch');
if (hcInput) {
  hcInput.addEventListener('input', (e) => {
    const q = e.target.value.trim().toLowerCase();
    document.querySelectorAll('.faq-card, .cat-card').forEach(el => {
      const text = el.textContent.toLowerCase();
      el.hidden = q && !text.includes(q);
    });
    const visibleCount = document.querySelectorAll('.faq-card:not([hidden]), .cat-card:not([hidden])').length;
    document.getElementById('noResult').hidden = !(q && visibleCount === 0);
  });
}
```
