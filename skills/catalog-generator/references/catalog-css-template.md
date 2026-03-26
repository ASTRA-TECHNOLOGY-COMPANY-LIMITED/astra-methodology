# Catalog CSS Component Templates

Defines the CSS component specs and code templates for catalog generation. All CSS references `assets/tokens.css` design tokens via `var()`.

---

## 1. Design Tone Token Presets

### 1.1 Editorial Luxury

```css
:root {
  /* Colors */
  --cat-color-primary: #1a1a1a;
  --cat-color-accent: #c9a96e;
  --cat-color-bg: #faf9f7;
  --cat-color-text: #2c2c2c;
  --cat-color-text-secondary: #6b6b6b;
  --cat-color-price: #1a1a1a;
  --cat-color-price-original: #999;
  --cat-color-badge-new: #c9a96e;
  --cat-color-badge-best: #1a1a1a;
  --cat-color-badge-sale: #8b2500;
  --cat-color-badge-hot: #c9a96e;
  --cat-color-border: #e8e4df;

  /* Typography */
  --cat-font-display: 'Playfair Display', 'Noto Serif KR', Georgia, serif;
  --cat-font-body: 'Inter', 'Pretendard', -apple-system, sans-serif;
  --cat-font-size-hero: clamp(2.5rem, 5vw, 4.5rem);
  --cat-font-size-h1: clamp(2rem, 4vw, 3rem);
  --cat-font-size-h2: clamp(1.5rem, 3vw, 2rem);
  --cat-font-size-h3: clamp(1.125rem, 2vw, 1.5rem);
  --cat-font-size-body: 1rem;
  --cat-font-size-small: 0.875rem;
  --cat-font-size-caption: 0.75rem;
  --cat-font-weight-light: 300;
  --cat-font-weight-regular: 400;
  --cat-font-weight-medium: 500;
  --cat-font-weight-semibold: 600;
  --cat-font-weight-bold: 700;

  /* Spacing */
  --cat-spacing-xs: 0.25rem;
  --cat-spacing-sm: 0.5rem;
  --cat-spacing-md: 1rem;
  --cat-spacing-lg: 1.5rem;
  --cat-spacing-xl: 2rem;
  --cat-spacing-2xl: 3rem;
  --cat-spacing-3xl: 4rem;
  --cat-spacing-4xl: 6rem;

  /* Layout */
  --cat-page-max-width: 1200px;
  --cat-grid-gap: 2rem;
  --cat-product-card-min-width: 320px;
  --cat-radius-sm: 2px;
  --cat-radius-md: 4px;
  --cat-radius-lg: 8px;
  --cat-radius-full: 9999px;
}

[data-theme="dark"] {
  --cat-color-primary: #f5f0eb;
  --cat-color-accent: #d4b87a;
  --cat-color-bg: #141210;
  --cat-color-text: #e8e4df;
  --cat-color-text-secondary: #9a9590;
  --cat-color-price: #f5f0eb;
  --cat-color-border: #2a2725;
}
```

### 1.2 Modern Minimal

```css
:root {
  --cat-color-primary: #0f172a;
  --cat-color-accent: #3b82f6;
  --cat-color-bg: #ffffff;
  --cat-color-text: #1e293b;
  --cat-color-text-secondary: #64748b;
  --cat-color-price: #0f172a;
  --cat-color-price-original: #94a3b8;
  --cat-color-badge-new: #3b82f6;
  --cat-color-badge-best: #0f172a;
  --cat-color-badge-sale: #ef4444;
  --cat-color-badge-hot: #f97316;
  --cat-color-border: #e2e8f0;

  --cat-font-display: 'Inter', 'Pretendard', -apple-system, sans-serif;
  --cat-font-body: 'Inter', 'Pretendard', -apple-system, sans-serif;
  --cat-font-size-hero: clamp(2rem, 4vw, 3.5rem);
  --cat-font-size-h1: clamp(1.75rem, 3.5vw, 2.5rem);
  --cat-font-size-h2: clamp(1.25rem, 2.5vw, 1.75rem);
  --cat-font-size-h3: clamp(1rem, 2vw, 1.25rem);
  --cat-font-size-body: 0.9375rem;
  --cat-font-size-small: 0.8125rem;
  --cat-font-size-caption: 0.75rem;

  --cat-page-max-width: 1120px;
  --cat-grid-gap: 1.5rem;
  --cat-product-card-min-width: 280px;
  --cat-radius-sm: 6px;
  --cat-radius-md: 8px;
  --cat-radius-lg: 12px;
}

[data-theme="dark"] {
  --cat-color-primary: #f1f5f9;
  --cat-color-accent: #60a5fa;
  --cat-color-bg: #0f172a;
  --cat-color-text: #e2e8f0;
  --cat-color-text-secondary: #94a3b8;
  --cat-color-price: #f1f5f9;
  --cat-color-border: #1e293b;
}
```

### 1.3 Bold & Vibrant

```css
:root {
  --cat-color-primary: #1a1a2e;
  --cat-color-accent: #e94560;
  --cat-color-bg: #fefefe;
  --cat-color-text: #1a1a2e;
  --cat-color-text-secondary: #555;
  --cat-color-price: #e94560;
  --cat-color-price-original: #aaa;
  --cat-color-badge-new: #e94560;
  --cat-color-badge-best: #6c63ff;
  --cat-color-badge-sale: #ff6b35;
  --cat-color-badge-hot: #e94560;
  --cat-color-border: #eee;

  --cat-font-display: 'Montserrat', 'Pretendard', -apple-system, sans-serif;
  --cat-font-body: 'Inter', 'Pretendard', -apple-system, sans-serif;
  --cat-font-size-hero: clamp(2.5rem, 6vw, 5rem);
  --cat-font-size-h1: clamp(2rem, 4.5vw, 3.5rem);
  --cat-font-size-h2: clamp(1.5rem, 3vw, 2.25rem);
  --cat-font-size-h3: clamp(1.125rem, 2vw, 1.5rem);

  --cat-page-max-width: 1280px;
  --cat-grid-gap: 1.5rem;
  --cat-product-card-min-width: 300px;
  --cat-radius-sm: 8px;
  --cat-radius-md: 12px;
  --cat-radius-lg: 16px;
}

[data-theme="dark"] {
  --cat-color-primary: #f8f8ff;
  --cat-color-accent: #ff6b8a;
  --cat-color-bg: #0d0d1a;
  --cat-color-text: #e8e8f0;
  --cat-color-text-secondary: #8888aa;
  --cat-color-price: #ff6b8a;
  --cat-color-border: #1e1e30;
}
```

### 1.4 Soft & Warm

```css
:root {
  --cat-color-primary: #3d3229;
  --cat-color-accent: #d97706;
  --cat-color-bg: #fdfaf6;
  --cat-color-text: #3d3229;
  --cat-color-text-secondary: #7a6f64;
  --cat-color-price: #3d3229;
  --cat-color-price-original: #b0a79e;
  --cat-color-badge-new: #d97706;
  --cat-color-badge-best: #3d3229;
  --cat-color-badge-sale: #b45309;
  --cat-color-badge-hot: #ea580c;
  --cat-color-border: #e8e0d8;

  --cat-font-display: 'DM Serif Display', 'Noto Serif KR', Georgia, serif;
  --cat-font-body: 'DM Sans', 'Pretendard', -apple-system, sans-serif;
  --cat-font-size-hero: clamp(2rem, 4vw, 3.5rem);

  --cat-page-max-width: 1080px;
  --cat-grid-gap: 2rem;
  --cat-product-card-min-width: 300px;
  --cat-radius-sm: 8px;
  --cat-radius-md: 12px;
  --cat-radius-lg: 20px;
}

[data-theme="dark"] {
  --cat-color-primary: #f0ebe5;
  --cat-color-accent: #fbbf24;
  --cat-color-bg: #1c1814;
  --cat-color-text: #e8e0d8;
  --cat-color-text-secondary: #9a918a;
  --cat-color-border: #2d2620;
}
```

### 1.5 Professional Enterprise

```css
:root {
  --cat-color-primary: #111827;
  --cat-color-accent: #2563eb;
  --cat-color-bg: #f9fafb;
  --cat-color-text: #111827;
  --cat-color-text-secondary: #6b7280;
  --cat-color-price: #111827;
  --cat-color-price-original: #9ca3af;
  --cat-color-badge-new: #2563eb;
  --cat-color-badge-best: #111827;
  --cat-color-badge-sale: #dc2626;
  --cat-color-badge-hot: #ea580c;
  --cat-color-border: #e5e7eb;

  --cat-font-display: 'Inter', 'Pretendard', -apple-system, sans-serif;
  --cat-font-body: 'Inter', 'Pretendard', -apple-system, sans-serif;
  --cat-font-size-hero: clamp(1.75rem, 3.5vw, 2.75rem);

  --cat-page-max-width: 1280px;
  --cat-grid-gap: 1.25rem;
  --cat-product-card-min-width: 260px;
  --cat-radius-sm: 4px;
  --cat-radius-md: 6px;
  --cat-radius-lg: 8px;
}

[data-theme="dark"] {
  --cat-color-primary: #f9fafb;
  --cat-color-accent: #60a5fa;
  --cat-color-bg: #111827;
  --cat-color-text: #e5e7eb;
  --cat-color-text-secondary: #9ca3af;
  --cat-color-border: #1f2937;
}
```

### 1.6 Playful Bright

```css
:root {
  --cat-color-primary: #312e81;
  --cat-color-accent: #f472b6;
  --cat-color-bg: #fffbf5;
  --cat-color-text: #312e81;
  --cat-color-text-secondary: #6366f1;
  --cat-color-price: #312e81;
  --cat-color-price-original: #a5b4fc;
  --cat-color-badge-new: #f472b6;
  --cat-color-badge-best: #8b5cf6;
  --cat-color-badge-sale: #f97316;
  --cat-color-badge-hot: #ef4444;
  --cat-color-border: #e0e7ff;

  --cat-font-display: 'Fredoka', 'Pretendard', -apple-system, sans-serif;
  --cat-font-body: 'Nunito', 'Pretendard', -apple-system, sans-serif;
  --cat-font-size-hero: clamp(2.5rem, 6vw, 5rem);

  --cat-page-max-width: 1200px;
  --cat-grid-gap: 1.5rem;
  --cat-product-card-min-width: 280px;
  --cat-radius-sm: 12px;
  --cat-radius-md: 16px;
  --cat-radius-lg: 24px;
  --cat-radius-full: 9999px;
}

[data-theme="dark"] {
  --cat-color-primary: #e0e7ff;
  --cat-color-accent: #f9a8d4;
  --cat-color-bg: #1e1b4b;
  --cat-color-text: #e0e7ff;
  --cat-color-text-secondary: #a5b4fc;
  --cat-color-border: #312e81;
}
```

### 1.7 Refined Minimal (Default Fallback)

```css
:root {
  --cat-color-primary: #18181b;
  --cat-color-accent: #18181b;
  --cat-color-bg: #ffffff;
  --cat-color-text: #27272a;
  --cat-color-text-secondary: #71717a;
  --cat-color-price: #18181b;
  --cat-color-price-original: #a1a1aa;
  --cat-color-badge-new: #18181b;
  --cat-color-badge-best: #18181b;
  --cat-color-badge-sale: #dc2626;
  --cat-color-badge-hot: #ea580c;
  --cat-color-border: #e4e4e7;

  --cat-font-display: 'Inter', 'Pretendard', -apple-system, sans-serif;
  --cat-font-body: 'Inter', 'Pretendard', -apple-system, sans-serif;
  --cat-font-size-hero: clamp(2rem, 4vw, 3.5rem);

  --cat-page-max-width: 1120px;
  --cat-grid-gap: 1.5rem;
  --cat-product-card-min-width: 300px;
  --cat-radius-sm: 4px;
  --cat-radius-md: 8px;
  --cat-radius-lg: 12px;
}

[data-theme="dark"] {
  --cat-color-primary: #fafafa;
  --cat-color-accent: #fafafa;
  --cat-color-bg: #09090b;
  --cat-color-text: #e4e4e7;
  --cat-color-text-secondary: #a1a1aa;
  --cat-color-border: #27272a;
}
```

---

## 2. catalog-base.css — Layout & Typography

```css
/* Reset & Base */
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

html[data-font="small"] { font-size: 14px; }
html[data-font="medium"] { font-size: 16px; }
html[data-font="large"] { font-size: 18px; }

body {
  font-family: var(--cat-font-body);
  font-size: var(--cat-font-size-body, 1rem);
  line-height: 1.6;
  color: var(--cat-color-text);
  background-color: var(--cat-color-bg);
  transition: color 0.2s ease, background-color 0.2s ease;
}

/* Header */
.catalog-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: var(--cat-color-bg);
  border-bottom: 1px solid var(--cat-color-border);
  display: flex;
  align-items: center;
  padding: 0 var(--cat-spacing-xl);
  z-index: 100;
  gap: var(--cat-spacing-md);
  backdrop-filter: blur(12px);
  background: color-mix(in srgb, var(--cat-color-bg) 85%, transparent);
}

.catalog-logo {
  font-family: var(--cat-font-display);
  font-size: var(--cat-font-size-h3);
  font-weight: var(--cat-font-weight-bold, 700);
  text-decoration: none;
  color: var(--cat-color-primary);
  white-space: nowrap;
}

.nav-categories {
  display: flex;
  list-style: none;
  gap: var(--cat-spacing-sm);
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.nav-tab {
  padding: var(--cat-spacing-sm) var(--cat-spacing-md);
  text-decoration: none;
  color: var(--cat-color-text-secondary);
  font-size: var(--cat-font-size-small);
  font-weight: var(--cat-font-weight-medium, 500);
  border-radius: var(--cat-radius-full);
  white-space: nowrap;
  transition: color 0.15s, background 0.15s;
}

.nav-tab:hover,
.nav-tab--active {
  color: var(--cat-color-primary);
  background: color-mix(in srgb, var(--cat-color-primary) 8%, transparent);
}

.header-actions {
  margin-left: auto;
  display: flex;
  gap: var(--cat-spacing-sm);
}

.header-actions button {
  background: none;
  border: 1px solid var(--cat-color-border);
  border-radius: var(--cat-radius-md);
  padding: var(--cat-spacing-sm);
  cursor: pointer;
  color: var(--cat-color-text-secondary);
  transition: background 0.15s, color 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-actions button:hover {
  background: color-mix(in srgb, var(--cat-color-primary) 5%, transparent);
  color: var(--cat-color-primary);
}

/* Main Layout */
.catalog-content,
.catalog-unified {
  max-width: var(--cat-page-max-width);
  margin: 0 auto;
  padding: calc(64px + var(--cat-spacing-2xl)) var(--cat-spacing-xl) var(--cat-spacing-3xl);
}

/* Breadcrumb */
.breadcrumb {
  font-size: var(--cat-font-size-small);
  color: var(--cat-color-text-secondary);
  margin-bottom: var(--cat-spacing-xl);
}

.breadcrumb a {
  color: var(--cat-color-text-secondary);
  text-decoration: none;
}

.breadcrumb a:hover {
  color: var(--cat-color-primary);
}

.breadcrumb-sep {
  margin: 0 var(--cat-spacing-xs);
}

/* Typography */
h1 { font-family: var(--cat-font-display); font-size: var(--cat-font-size-h1); font-weight: var(--cat-font-weight-bold, 700); line-height: 1.2; }
h2 { font-family: var(--cat-font-display); font-size: var(--cat-font-size-h2); font-weight: var(--cat-font-weight-semibold, 600); line-height: 1.3; }
h3 { font-family: var(--cat-font-display); font-size: var(--cat-font-size-h3); font-weight: var(--cat-font-weight-semibold, 600); line-height: 1.4; }

/* Product Grid */
.product-grid {
  display: grid;
  gap: var(--cat-grid-gap);
}

.product-grid--2col {
  grid-template-columns: repeat(auto-fill, minmax(var(--cat-product-card-min-width), 1fr));
}

.product-grid--3col {
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
}

.product-grid--list {
  grid-template-columns: 1fr;
}

/* Page Navigation Footer */
.page-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--cat-spacing-xl) 0;
  border-top: 1px solid var(--cat-color-border);
  margin-top: var(--cat-spacing-3xl);
}

.page-nav a {
  display: flex;
  align-items: center;
  gap: var(--cat-spacing-sm);
  text-decoration: none;
  color: var(--cat-color-text-secondary);
  font-size: var(--cat-font-size-small);
  transition: color 0.15s;
}

.page-nav a:hover {
  color: var(--cat-color-primary);
}

.page-nav__current {
  font-size: var(--cat-font-size-caption);
  color: var(--cat-color-text-secondary);
}

/* Floating TOC */
.floating-toc {
  position: fixed;
  top: calc(64px + var(--cat-spacing-xl));
  left: var(--cat-spacing-xl);
  width: 180px;
  z-index: 50;
}

.floating-toc ul {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--cat-spacing-xs);
}

.toc-link {
  display: block;
  padding: var(--cat-spacing-xs) var(--cat-spacing-sm);
  font-size: var(--cat-font-size-small);
  color: var(--cat-color-text-secondary);
  text-decoration: none;
  border-left: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
}

.toc-link:hover,
.toc-link--active {
  color: var(--cat-color-primary);
  border-left-color: var(--cat-color-accent);
}

/* Responsive */
@media (max-width: 1024px) {
  .floating-toc { display: none; }
  .catalog-content,
  .catalog-unified {
    padding-left: var(--cat-spacing-lg);
    padding-right: var(--cat-spacing-lg);
  }
}

@media (max-width: 768px) {
  .catalog-header {
    padding: 0 var(--cat-spacing-md);
  }
  .catalog-content,
  .catalog-unified {
    padding-left: var(--cat-spacing-md);
    padding-right: var(--cat-spacing-md);
  }
  .nav-categories {
    display: none; /* Replace with hamburger menu on mobile */
  }
  .product-grid--2col,
  .product-grid--3col {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  html { font-size: 15px; }
  .catalog-header { height: 56px; }
  .catalog-content,
  .catalog-unified {
    padding-top: calc(56px + var(--cat-spacing-lg));
  }
}
```

---

## 3. catalog-components.css — Product Cards, Badges, CTAs

```css
/* Product Card */
.product-card {
  background: var(--cat-color-bg);
  border: 1px solid var(--cat-color-border);
  border-radius: var(--cat-radius-lg);
  overflow: hidden;
  position: relative;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px color-mix(in srgb, var(--cat-color-primary) 8%, transparent);
}

.product-card--hero {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: var(--cat-spacing-xl);
}

.product-card--highlight {
  outline: 3px solid var(--cat-color-accent);
  outline-offset: 2px;
}

/* Badges */
.product-card__badges {
  position: absolute;
  top: var(--cat-spacing-md);
  left: var(--cat-spacing-md);
  display: flex;
  gap: var(--cat-spacing-xs);
  z-index: 2;
}

.badge {
  display: inline-block;
  padding: var(--cat-spacing-xs) var(--cat-spacing-sm);
  font-size: var(--cat-font-size-caption);
  font-weight: var(--cat-font-weight-bold, 700);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-radius: var(--cat-radius-sm);
  color: #fff;
}

.badge--new  { background: var(--cat-color-badge-new); }
.badge--best { background: var(--cat-color-badge-best); }
.badge--sale { background: var(--cat-color-badge-sale); }
.badge--hot  { background: var(--cat-color-badge-hot); }

/* Product Image */
.product-card__image {
  position: relative;
  overflow: hidden;
  background: color-mix(in srgb, var(--cat-color-border) 30%, transparent);
}

.product-card__image img {
  width: 100%;
  height: auto;
  display: block;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.product-card:hover .product-card__image img {
  transform: scale(1.03);
}

/* Product Content */
.product-card__content {
  padding: var(--cat-spacing-lg);
}

.product-card__name {
  font-family: var(--cat-font-display);
  font-size: var(--cat-font-size-h3);
  font-weight: var(--cat-font-weight-semibold, 600);
  color: var(--cat-color-primary);
  margin-bottom: var(--cat-spacing-xs);
}

.product-card__subtitle {
  font-size: var(--cat-font-size-small);
  color: var(--cat-color-text-secondary);
  margin-bottom: var(--cat-spacing-md);
}

.product-card__description {
  font-size: var(--cat-font-size-body);
  color: var(--cat-color-text);
  line-height: 1.6;
  margin-bottom: var(--cat-spacing-md);
}

.product-card__features {
  list-style: none;
  margin-bottom: var(--cat-spacing-lg);
}

.product-card__features li {
  position: relative;
  padding-left: var(--cat-spacing-lg);
  font-size: var(--cat-font-size-small);
  color: var(--cat-color-text-secondary);
  line-height: 1.8;
}

.product-card__features li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.6em;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--cat-color-accent);
}

/* Pricing */
.product-card__pricing {
  display: flex;
  align-items: baseline;
  gap: var(--cat-spacing-sm);
  margin-bottom: var(--cat-spacing-lg);
}

.price--original {
  font-size: var(--cat-font-size-small);
  color: var(--cat-color-price-original);
  text-decoration: line-through;
}

.price--current {
  font-size: var(--cat-font-size-h3);
  font-weight: var(--cat-font-weight-bold, 700);
  color: var(--cat-color-price);
}

.price--bundle {
  font-size: var(--cat-font-size-h2);
  font-weight: var(--cat-font-weight-bold, 700);
  color: var(--cat-color-accent);
}

/* CTA Button */
.cta-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--cat-spacing-sm) var(--cat-spacing-xl);
  font-size: var(--cat-font-size-small);
  font-weight: var(--cat-font-weight-semibold, 600);
  text-decoration: none;
  border-radius: var(--cat-radius-md);
  border: 2px solid var(--cat-color-primary);
  color: var(--cat-color-primary);
  background: transparent;
  cursor: pointer;
  transition: background 0.2s, color 0.2s, transform 0.15s;
}

.cta-button:hover {
  background: var(--cat-color-primary);
  color: var(--cat-color-bg);
  transform: translateY(-1px);
}

.cta-button--primary {
  background: var(--cat-color-primary);
  color: var(--cat-color-bg);
  border-color: var(--cat-color-primary);
}

.cta-button--primary:hover {
  opacity: 0.9;
}

.cta-button--accent {
  background: var(--cat-color-accent);
  color: #fff;
  border-color: var(--cat-color-accent);
}

/* Cover Section */
.cover {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  overflow: hidden;
}

.cover__hero {
  position: absolute;
  inset: 0;
}

.cover__hero-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom,
    color-mix(in srgb, var(--cat-color-primary) 30%, transparent),
    color-mix(in srgb, var(--cat-color-primary) 70%, transparent));
}

.cover__content {
  position: relative;
  z-index: 1;
  color: #fff;
  padding: var(--cat-spacing-3xl);
}

.cover__title {
  font-family: var(--cat-font-display);
  font-size: var(--cat-font-size-hero);
  font-weight: var(--cat-font-weight-bold, 700);
  margin-bottom: var(--cat-spacing-md);
}

.cover__tagline {
  font-size: var(--cat-font-size-h3);
  font-weight: var(--cat-font-weight-light, 300);
  opacity: 0.9;
}

.cover__scroll-indicator {
  position: absolute;
  bottom: var(--cat-spacing-2xl);
  color: #fff;
  opacity: 0.7;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(8px); }
}

/* Category Divider */
.category-divider {
  position: relative;
  height: 360px;
  border-radius: var(--cat-radius-lg);
  overflow: hidden;
  margin-bottom: var(--cat-spacing-2xl);
  display: flex;
  align-items: flex-end;
}

.category-divider__image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.category-divider__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top,
    color-mix(in srgb, var(--cat-color-primary) 80%, transparent),
    transparent 60%);
}

.category-divider__content {
  position: relative;
  z-index: 1;
  padding: var(--cat-spacing-2xl);
  color: #fff;
}

.category-divider__title {
  font-family: var(--cat-font-display);
  font-size: var(--cat-font-size-h1);
  margin-bottom: var(--cat-spacing-sm);
}

.category-divider__count {
  font-size: var(--cat-font-size-small);
  opacity: 0.8;
}

/* Cross-Sell Carousel */
.cross-sell-section {
  margin-top: var(--cat-spacing-3xl);
  padding-top: var(--cat-spacing-2xl);
  border-top: 1px solid var(--cat-color-border);
}

.cross-sell-section__title {
  font-size: var(--cat-font-size-h3);
  margin-bottom: var(--cat-spacing-lg);
}

.cross-sell-carousel {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--cat-spacing-sm);
}

.carousel-track {
  display: flex;
  gap: var(--cat-spacing-md);
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  padding: var(--cat-spacing-sm) 0;
}

.carousel-track::-webkit-scrollbar { display: none; }

.cross-sell-card {
  flex-shrink: 0;
  width: 200px;
  scroll-snap-align: start;
  text-align: center;
}

.cross-sell-card img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: var(--cat-radius-md);
  margin-bottom: var(--cat-spacing-sm);
}

.cross-sell-card__name {
  display: block;
  font-size: var(--cat-font-size-small);
  font-weight: var(--cat-font-weight-medium, 500);
  color: var(--cat-color-text);
}

.cross-sell-card__price {
  display: block;
  font-size: var(--cat-font-size-small);
  color: var(--cat-color-price);
  font-weight: var(--cat-font-weight-semibold, 600);
}

.carousel-prev,
.carousel-next {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--cat-color-border);
  background: var(--cat-color-bg);
  cursor: pointer;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--cat-color-text-secondary);
  transition: background 0.15s, color 0.15s;
}

.carousel-prev:hover,
.carousel-next:hover {
  background: var(--cat-color-primary);
  color: var(--cat-color-bg);
}

/* Bundle Box */
.bundle-box {
  position: relative;
  border: 2px dashed var(--cat-color-accent);
  border-radius: var(--cat-radius-lg);
  padding: var(--cat-spacing-2xl);
  margin-top: var(--cat-spacing-2xl);
  text-align: center;
}

.bundle-box__badge {
  position: absolute;
  top: calc(-1 * var(--cat-spacing-sm) - 2px);
  left: 50%;
  transform: translateX(-50%);
  background: var(--cat-color-accent);
  color: #fff;
  padding: var(--cat-spacing-xs) var(--cat-spacing-lg);
  font-size: var(--cat-font-size-caption);
  font-weight: var(--cat-font-weight-bold, 700);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  border-radius: var(--cat-radius-full);
}

.bundle-box__products {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--cat-spacing-lg);
  margin: var(--cat-spacing-xl) 0;
}

.bundle-product {
  text-align: center;
}

.bundle-product img {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: var(--cat-radius-md);
  margin-bottom: var(--cat-spacing-sm);
}

.bundle-box__plus {
  font-size: var(--cat-font-size-h2);
  color: var(--cat-color-text-secondary);
}

.bundle-box__savings {
  display: inline-block;
  background: var(--cat-color-badge-sale);
  color: #fff;
  padding: var(--cat-spacing-xs) var(--cat-spacing-md);
  border-radius: var(--cat-radius-full);
  font-size: var(--cat-font-size-small);
  font-weight: var(--cat-font-weight-bold, 700);
  margin-left: var(--cat-spacing-sm);
}

/* Brand Story Metrics */
.brand-story__metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--cat-spacing-lg);
  margin-top: var(--cat-spacing-2xl);
}

.metric-card {
  text-align: center;
  padding: var(--cat-spacing-xl);
}

.metric-card__number {
  display: block;
  font-family: var(--cat-font-display);
  font-size: var(--cat-font-size-h1);
  font-weight: var(--cat-font-weight-bold, 700);
  color: var(--cat-color-accent);
}

.metric-card__label {
  display: block;
  font-size: var(--cat-font-size-small);
  color: var(--cat-color-text-secondary);
  margin-top: var(--cat-spacing-xs);
}

/* Contact Page */
.contact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--cat-spacing-lg);
  margin: var(--cat-spacing-2xl) 0;
}

.contact-card {
  padding: var(--cat-spacing-xl);
  border: 1px solid var(--cat-color-border);
  border-radius: var(--cat-radius-lg);
  text-align: center;
}

.contact-card__icon {
  margin-bottom: var(--cat-spacing-md);
  color: var(--cat-color-accent);
}

.contact-card h3 {
  margin-bottom: var(--cat-spacing-sm);
}

.qr-section {
  text-align: center;
  padding: var(--cat-spacing-2xl) 0;
}

.qr-placeholder {
  width: 160px;
  height: 160px;
  border: 2px solid var(--cat-color-border);
  border-radius: var(--cat-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--cat-spacing-md);
  font-size: var(--cat-font-size-h2);
  color: var(--cat-color-text-secondary);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--cat-spacing-lg);
  margin-top: var(--cat-spacing-xl);
}

.info-card {
  padding: var(--cat-spacing-lg);
  background: color-mix(in srgb, var(--cat-color-primary) 3%, transparent);
  border-radius: var(--cat-radius-md);
}

.info-card h4 {
  margin-bottom: var(--cat-spacing-sm);
  font-weight: var(--cat-font-weight-semibold, 600);
}

/* Search Overlay */
.search-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: color-mix(in srgb, var(--cat-color-primary) 50%, transparent);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 20vh;
}

.search-dialog {
  background: var(--cat-color-bg);
  border-radius: var(--cat-radius-lg);
  width: 90%;
  max-width: 560px;
  box-shadow: 0 24px 64px color-mix(in srgb, var(--cat-color-primary) 20%, transparent);
  overflow: hidden;
}

.search-input {
  width: 100%;
  padding: var(--cat-spacing-lg);
  border: none;
  font-size: var(--cat-font-size-h3);
  background: transparent;
  color: var(--cat-color-text);
  outline: none;
}

.search-results {
  list-style: none;
  max-height: 320px;
  overflow-y: auto;
  border-top: 1px solid var(--cat-color-border);
}

.search-result-item {
  padding: var(--cat-spacing-md) var(--cat-spacing-lg);
  cursor: pointer;
  transition: background 0.1s;
}

.search-result-item:hover {
  background: color-mix(in srgb, var(--cat-color-accent) 8%, transparent);
}

.search-footer {
  padding: var(--cat-spacing-sm) var(--cat-spacing-lg);
  font-size: var(--cat-font-size-caption);
  color: var(--cat-color-text-secondary);
  border-top: 1px solid var(--cat-color-border);
}

.search-footer kbd {
  display: inline-block;
  padding: 1px 6px;
  border: 1px solid var(--cat-color-border);
  border-radius: 3px;
  font-size: 0.7rem;
}

/* Lightbox */
.lightbox {
  position: fixed;
  inset: 0;
  z-index: 300;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.lightbox--open {
  opacity: 1;
}

.lightbox__backdrop {
  position: absolute;
  inset: 0;
  background: color-mix(in srgb, var(--cat-color-primary) 85%, transparent);
}

.lightbox__content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.lightbox__content img {
  max-width: 100%;
  max-height: 85vh;
  object-fit: contain;
  border-radius: var(--cat-radius-md);
}

.lightbox__close {
  position: absolute;
  top: calc(-1 * var(--cat-spacing-xl));
  right: 0;
  background: none;
  border: none;
  color: #fff;
  font-size: 2rem;
  cursor: pointer;
}

/* ===== Screenshot Frame Components ===== */

/* Browser Chrome Frame */
.screenshot-frame {
  border-radius: var(--cat-radius-lg);
  overflow: hidden;
  box-shadow: 0 8px 32px color-mix(in srgb, var(--cat-color-primary) 12%, transparent),
              0 2px 8px color-mix(in srgb, var(--cat-color-primary) 6%, transparent);
  background: var(--cat-color-bg);
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.screenshot-frame.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.screenshot-frame--hero {
  max-width: 960px;
  margin: 0 auto;
}

.screenshot-frame__chrome {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: color-mix(in srgb, var(--cat-color-primary) 5%, var(--cat-color-bg));
  border-bottom: 1px solid var(--cat-color-border);
}

.screenshot-frame__dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--cat-color-border);
}

.screenshot-frame__dot:nth-child(1) { background: #FF5F57; }
.screenshot-frame__dot:nth-child(2) { background: #FEBC2E; }
.screenshot-frame__dot:nth-child(3) { background: #28C840; }

[data-theme="dark"] .screenshot-frame__dot:nth-child(1) { background: #FF6961; }
[data-theme="dark"] .screenshot-frame__dot:nth-child(2) { background: #FFD866; }
[data-theme="dark"] .screenshot-frame__dot:nth-child(3) { background: #5AF78E; }

.screenshot-frame__url {
  flex: 1;
  margin-left: 8px;
  padding: 4px 12px;
  font-size: 0.7rem;
  color: var(--cat-color-text-secondary);
  background: color-mix(in srgb, var(--cat-color-primary) 3%, transparent);
  border-radius: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.screenshot-frame img {
  display: block;
  width: 100%;
  height: auto;
}

/* Tablet Frame */
.screenshot-frame--tablet {
  border: 8px solid color-mix(in srgb, var(--cat-color-primary) 10%, var(--cat-color-bg));
  border-radius: 16px;
  max-width: 480px;
  margin: 0 auto;
}

/* Mobile Frame */
.screenshot-frame--mobile {
  border: 6px solid color-mix(in srgb, var(--cat-color-primary) 10%, var(--cat-color-bg));
  border-radius: 24px;
  max-width: 280px;
  margin: 0 auto;
  padding: 8px 0;
}

.screenshot-frame--mobile::before {
  content: '';
  display: block;
  width: 36px;
  height: 4px;
  margin: 0 auto 6px;
  border-radius: 2px;
  background: var(--cat-color-border);
}

/* Screenshot Tabs */
.screenshot-tabs {
  display: flex;
  justify-content: center;
  gap: var(--cat-spacing-sm);
  margin-bottom: var(--cat-spacing-lg);
}

.screenshot-tab {
  padding: 8px 20px;
  border: 1px solid var(--cat-color-border);
  border-radius: 100px;
  background: transparent;
  color: var(--cat-color-text-secondary);
  font-size: var(--cat-font-size-body);
  cursor: pointer;
  transition: all 0.2s ease;
}

.screenshot-tab:hover {
  border-color: var(--cat-color-accent);
  color: var(--cat-color-accent);
}

.screenshot-tab--active {
  background: var(--cat-color-accent);
  border-color: var(--cat-color-accent);
  color: #fff;
}

/* Screenshot Panels */
.screenshot-panel {
  display: none;
}

.screenshot-panel--active {
  display: block;
  animation: fadeInUp 0.4s ease;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Product Card Screenshot Gallery */
.product-card__screenshot-gallery {
  margin: var(--cat-spacing-lg) 0;
  padding: var(--cat-spacing-lg);
  background: color-mix(in srgb, var(--cat-color-primary) 2%, transparent);
  border-radius: var(--cat-radius-lg);
}

/* ===== Showcase Page ===== */

.showcase-page {
  max-width: var(--cat-page-max-width);
  margin: 0 auto;
  padding: var(--cat-spacing-xxl) var(--cat-spacing-lg);
}

.showcase-hero {
  text-align: center;
  margin-bottom: var(--cat-spacing-xxl);
}

.showcase-hero__title {
  font-family: var(--cat-font-display);
  font-size: var(--cat-font-size-h1);
  margin-bottom: var(--cat-spacing-sm);
}

.showcase-hero__subtitle {
  font-size: var(--cat-font-size-h4);
  color: var(--cat-color-text-secondary);
  margin-bottom: var(--cat-spacing-xl);
}

/* 3-Device Showcase */
.showcase-devices {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: var(--cat-spacing-xl);
  margin: var(--cat-spacing-xxl) 0;
  perspective: 1200px;
  transform: rotateX(var(--tilt-x, 0deg)) rotateY(var(--tilt-y, 0deg));
  transition: transform 0.1s ease-out;
}

.showcase-device--desktop { flex: 0 0 55%; }
.showcase-device--tablet { flex: 0 0 22%; }
.showcase-device--mobile { flex: 0 0 12%; }

@media (max-width: 768px) {
  .showcase-devices {
    flex-direction: column;
    align-items: center;
  }
  .showcase-device--desktop,
  .showcase-device--tablet,
  .showcase-device--mobile {
    flex: 0 0 auto;
    width: 100%;
    max-width: 480px;
  }
}

/* Feature Walkthrough */
.showcase-flow {
  margin: var(--cat-spacing-xxl) 0;
}

.showcase-flow__title {
  font-family: var(--cat-font-display);
  font-size: var(--cat-font-size-h2);
  text-align: center;
  margin-bottom: var(--cat-spacing-xl);
}

.showcase-step {
  display: grid;
  grid-template-columns: 48px 1fr 1fr;
  gap: var(--cat-spacing-lg);
  align-items: start;
  margin-bottom: var(--cat-spacing-xl);
  padding: var(--cat-spacing-lg);
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.showcase-step.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.showcase-step:nth-child(even) {
  direction: rtl;
}

.showcase-step:nth-child(even) > * {
  direction: ltr;
}

.showcase-step__number {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--cat-color-accent);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--cat-font-size-h3);
  font-weight: var(--cat-font-weight-bold, 700);
  flex-shrink: 0;
}

.showcase-step__content h4 {
  font-size: var(--cat-font-size-h3);
  margin-bottom: var(--cat-spacing-sm);
}

.showcase-step__content p {
  color: var(--cat-color-text-secondary);
  line-height: 1.6;
}

@media (max-width: 768px) {
  .showcase-step {
    grid-template-columns: 40px 1fr;
  }
  .showcase-step__screenshot {
    grid-column: 1 / -1;
  }
  .showcase-step:nth-child(even) {
    direction: ltr;
  }
}

/* Responsive Comparison */
.showcase-responsive {
  margin: var(--cat-spacing-xxl) 0;
  text-align: center;
}

.showcase-responsive__title {
  font-family: var(--cat-font-display);
  font-size: var(--cat-font-size-h2);
  margin-bottom: var(--cat-spacing-lg);
}

.screenshot-panels--showcase {
  max-width: 960px;
  margin: 0 auto;
}

/* Showcase CTA Section */
.showcase-cta {
  position: relative;
  text-align: center;
  padding: var(--cat-spacing-xxl);
  border-radius: var(--cat-radius-lg);
  overflow: hidden;
  margin: var(--cat-spacing-xxl) 0;
}

.showcase-cta__bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.showcase-cta__bg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.08;
}

.showcase-cta__title,
.showcase-cta__description {
  position: relative;
  z-index: 1;
}

.showcase-cta__title {
  font-family: var(--cat-font-display);
  font-size: var(--cat-font-size-h2);
  margin-bottom: var(--cat-spacing-md);
}

.showcase-cta__description {
  color: var(--cat-color-text-secondary);
  margin-bottom: var(--cat-spacing-xl);
  max-width: 480px;
  margin-inline: auto;
}

.cta-button--large {
  padding: 16px 40px;
  font-size: var(--cat-font-size-h4);
  position: relative;
  z-index: 1;
}

/* ===== Editorial Illustration Breaks ===== */

.illustration-break {
  margin: var(--cat-spacing-xxl) calc(-1 * var(--cat-spacing-lg));
  overflow: hidden;
  position: relative;
  opacity: 0;
  transform: scale(0.98);
  transition: opacity 0.8s ease, transform 0.8s ease;
}

.illustration-break.is-visible {
  opacity: 1;
  transform: scale(1);
}

.illustration-break img {
  display: block;
  width: 100%;
  height: auto;
  max-height: 200px;
  object-fit: cover;
}

.illustration-break--wide img {
  max-height: 320px;
}

.illustration-break--with-text {
  position: relative;
}

.illustration-break__overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--cat-color-primary) 40%, transparent);
}

.illustration-break__quote {
  color: #fff;
  font-family: var(--cat-font-display);
  font-size: var(--cat-font-size-h3);
  font-style: italic;
  text-align: center;
  max-width: 600px;
  padding: 0 var(--cat-spacing-lg);
  text-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

/* Detail Texture Background */
.texture-bg-section {
  position: relative;
  padding: var(--cat-spacing-xxl) var(--cat-spacing-lg);
  border-radius: var(--cat-radius-lg);
  overflow: hidden;
}

.texture-bg-section::before {
  content: '';
  position: absolute;
  inset: 0;
  background: var(--texture-bg) center / cover no-repeat;
  opacity: 0.04;
  z-index: 0;
}

[data-theme="dark"] .texture-bg-section::before {
  opacity: 0.06;
}

.texture-bg-section > * {
  position: relative;
  z-index: 1;
}
```

---

## 4. catalog-print.css — Print Optimization

```css
@media print {
  /* Page setup */
  @page {
    size: A4;
    margin: 15mm 12mm;
  }

  /* Hide interactive elements */
  .catalog-header,
  .search-overlay,
  .floating-toc,
  .page-nav,
  .theme-toggle,
  .font-size-toggle,
  .search-trigger,
  .cover__scroll-indicator,
  .carousel-prev,
  .carousel-next {
    display: none !important;
  }

  /* Reset layout */
  body {
    font-size: 10pt;
    color: #000;
    background: #fff;
  }

  .catalog-content,
  .catalog-unified {
    max-width: 100%;
    padding: 0;
  }

  /* Page breaks */
  .cover,
  .brand-story,
  .category-divider,
  .contact-page {
    break-before: page;
  }

  .product-card {
    break-inside: avoid;
    box-shadow: none;
    border: 1px solid #ddd;
  }

  .bundle-box {
    break-inside: avoid;
  }

  /* Image handling */
  img {
    max-width: 100%;
    page-break-inside: avoid;
  }

  /* CTA buttons → text in print */
  .cta-button {
    border: 1px solid #000;
    background: none;
    color: #000;
  }

  /* Ensure link URLs are visible */
  a[href^="http"]::after {
    content: " (" attr(href) ")";
    font-size: 8pt;
    color: #666;
  }

  a[href^="#"]::after {
    content: none;
  }

  /* Product grid: single column for clean print */
  .product-grid {
    grid-template-columns: 1fr;
  }

  .product-card--hero {
    grid-template-columns: 1fr 1fr;
  }

  /* Screenshot frames: simplify for print */
  .screenshot-frame {
    box-shadow: none;
    border: 1px solid #ddd;
    opacity: 1;
    transform: none;
  }

  .screenshot-tabs,
  .showcase-devices--tablet,
  .showcase-devices--mobile {
    display: none;
  }

  .screenshot-panel {
    display: block !important;
  }

  .screenshot-panel[data-viewport="tablet"],
  .screenshot-panel[data-viewport="mobile"] {
    display: none !important;
  }

  .screenshot-frame__chrome {
    background: #f5f5f5;
  }

  /* Illustration breaks: show as decorative dividers */
  .illustration-break {
    opacity: 1;
    transform: none;
    margin: 12mm 0;
  }

  .illustration-break img {
    max-height: 80px;
  }

  .illustration-break--with-text .illustration-break__overlay {
    background: none;
  }

  .illustration-break__quote {
    color: #333;
    text-shadow: none;
  }

  /* Showcase page */
  .showcase-page {
    break-before: page;
  }

  .showcase-step {
    opacity: 1;
    transform: none;
    break-inside: avoid;
  }

  .showcase-devices {
    perspective: none;
    transform: none;
  }

  .showcase-cta__bg {
    display: none;
  }

  .texture-bg-section::before {
    display: none;
  }
}
```

---

## 5. catalog-interactions.css — Hover & Animation

```css
/* Product card hover effects */
.product-card {
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1),
              box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px color-mix(in srgb, var(--cat-color-primary) 10%, transparent);
}

/* Badge entrance */
.badge {
  animation: badgeIn 0.3s ease-out both;
}

@keyframes badgeIn {
  from { opacity: 0; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1); }
}

/* Scroll-triggered fade-in */
.catalog-section,
.product-card,
.bundle-box,
.cross-sell-section,
.contact-card,
.metric-card {
  opacity: 0;
  transform: translateY(20px);
  animation: fadeInUp 0.5s ease-out forwards;
}

@keyframes fadeInUp {
  to { opacity: 1; transform: translateY(0); }
}

/* Stagger children */
.product-grid .product-card:nth-child(1) { animation-delay: 0.05s; }
.product-grid .product-card:nth-child(2) { animation-delay: 0.10s; }
.product-grid .product-card:nth-child(3) { animation-delay: 0.15s; }
.product-grid .product-card:nth-child(4) { animation-delay: 0.20s; }
.product-grid .product-card:nth-child(5) { animation-delay: 0.25s; }
.product-grid .product-card:nth-child(6) { animation-delay: 0.30s; }

.contact-grid .contact-card:nth-child(1) { animation-delay: 0.05s; }
.contact-grid .contact-card:nth-child(2) { animation-delay: 0.10s; }
.contact-grid .contact-card:nth-child(3) { animation-delay: 0.15s; }
.contact-grid .contact-card:nth-child(4) { animation-delay: 0.20s; }

/* Image zoom on hover */
.product-card__image {
  overflow: hidden;
}

.product-card__image img {
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.product-card:hover .product-card__image img {
  transform: scale(1.05);
}

/* CTA button press effect */
.cta-button:active {
  transform: translateY(1px);
}

/* Cover scroll indicator bounce */
.cover__scroll-indicator {
  animation: bounce 2s infinite;
}

/* Carousel smooth scroll */
.carousel-track {
  scroll-behavior: smooth;
}

/* Screenshot frame hover — subtle lift */
.screenshot-frame--browser:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px color-mix(in srgb, var(--cat-color-primary) 15%, transparent),
              0 4px 12px color-mix(in srgb, var(--cat-color-primary) 8%, transparent);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

/* Screenshot tab switch animation */
.screenshot-tab {
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease, transform 0.15s ease;
}

.screenshot-tab:active {
  transform: scale(0.96);
}

/* Showcase step stagger */
.showcase-flow .showcase-step:nth-child(1) { transition-delay: 0.05s; }
.showcase-flow .showcase-step:nth-child(2) { transition-delay: 0.15s; }
.showcase-flow .showcase-step:nth-child(3) { transition-delay: 0.25s; }
.showcase-flow .showcase-step:nth-child(4) { transition-delay: 0.35s; }
.showcase-flow .showcase-step:nth-child(5) { transition-delay: 0.45s; }

/* Illustration break — parallax-like subtle scale on scroll */
.illustration-break img {
  transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.illustration-break:hover img {
  transform: scale(1.02);
}

/* 3-Device showcase entrance */
.showcase-device {
  opacity: 0;
  transform: translateY(30px);
  animation: deviceReveal 0.6s ease-out forwards;
}

.showcase-device--desktop { animation-delay: 0.1s; }
.showcase-device--tablet { animation-delay: 0.25s; }
.showcase-device--mobile { animation-delay: 0.4s; }

@keyframes deviceReveal {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }

  .screenshot-frame,
  .illustration-break,
  .showcase-step,
  .showcase-device {
    opacity: 1;
    transform: none;
  }
}
```
