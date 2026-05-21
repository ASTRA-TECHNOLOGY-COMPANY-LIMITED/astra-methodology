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
