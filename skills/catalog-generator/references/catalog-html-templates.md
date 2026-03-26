# Catalog HTML Templates

Defines the HTML structure templates used when generating the product catalog.

## 1. Page HTML Template (Individual Pages)

Each page file `pages/{NN}-{name}.html`:

```html
<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page-title} — {catalog-name}</title>
  <link rel="stylesheet" href="../assets/tokens.css">
  <link rel="stylesheet" href="../assets/catalog-base.css">
  <link rel="stylesheet" href="../assets/catalog-components.css">
  <link rel="stylesheet" href="../assets/catalog-interactions.css">
  <link rel="stylesheet" href="../assets/catalog-print.css" media="print">
</head>
<body>
  <!-- Top Navigation Bar -->
  <header class="catalog-header">
    <a href="../index.html" class="catalog-logo">{brand-name}</a>
    <nav class="catalog-nav">
      <ul class="nav-categories">
        <!-- Category tabs: dynamically generated per catalog -->
        <li><a href="03-{category-slug}.html" class="nav-tab">{category-name}</a></li>
      </ul>
    </nav>
    <div class="header-actions">
      <button class="search-trigger" aria-label="Search" data-shortcut="Cmd+K">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
      </button>
      <button class="theme-toggle" aria-label="Toggle theme">
        <svg class="icon-sun" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/>
          <line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/>
          <line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>
        <svg class="icon-moon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:none">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      </button>
      <button class="font-size-toggle" aria-label="Font size">A</button>
    </div>
  </header>

  <!-- Search Overlay -->
  <div class="search-overlay" id="searchOverlay" hidden>
    <div class="search-dialog">
      <input type="search" class="search-input" placeholder="Search products..." autofocus>
      <ul class="search-results"></ul>
      <div class="search-empty" hidden>No results found</div>
      <footer class="search-footer">
        <kbd>Esc</kbd> to close &middot; <kbd>Enter</kbd> to select
      </footer>
    </div>
  </div>

  <!-- Main Content -->
  <main class="catalog-content" id="catalogContent">
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <a href="../index.html">Catalog</a>
      <span class="breadcrumb-sep">&rsaquo;</span>
      <span>{page-title}</span>
    </nav>

    <!-- Page-specific content inserted here -->

  </main>

  <!-- Page Navigation Footer -->
  <footer class="page-nav">
    <a href="{prev-page}.html" class="page-nav__prev" aria-label="Previous page">
      <span class="page-nav__arrow">&larr;</span>
      <span class="page-nav__label">{prev-page-title}</span>
    </a>
    <span class="page-nav__current">{current-page} / {total-pages}</span>
    <a href="{next-page}.html" class="page-nav__next" aria-label="Next page">
      <span class="page-nav__label">{next-page-title}</span>
      <span class="page-nav__arrow">&rarr;</span>
    </a>
  </footer>

  <script src="../shared/theme.js"></script>
  <script src="../shared/nav.js"></script>
  <script src="../shared/interactions.js"></script>
</body>
</html>
```

---

## 2. Cover Page Content Template

Content block for `pages/01-cover.html` `<main>`:

```html
<section class="cover" id="cover">
  <div class="cover__hero">
    <img src="../images/hero/{hero-image}" alt="{catalog-name}" class="cover__hero-img">
    <div class="cover__overlay"></div>
  </div>
  <div class="cover__content">
    <img src="../images/{logo}" alt="{brand-name}" class="cover__logo">
    <h1 class="cover__title">{catalog-headline}</h1>
    <p class="cover__tagline">{catalog-tagline}</p>
    <div class="cover__meta">
      <span class="cover__edition">{edition-label}</span>
      <span class="cover__year">{year}</span>
    </div>
  </div>
  <a href="#toc" class="cover__scroll-indicator" aria-label="Scroll down">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polyline points="6 9 12 15 18 9"/>
    </svg>
  </a>
</section>
```

---

## 3. Brand Story Content Template

Content block for `pages/02-brand-story.html` `<main>`:

```html
<section class="brand-story" id="brand-story">
  <div class="brand-story__hero">
    <img src="../images/hero/{brand-image}" alt="{brand-name} story" loading="lazy">
  </div>
  <div class="brand-story__content">
    <h2 class="brand-story__title">{brand-story-headline}</h2>
    <p class="brand-story__body">{brand-story-text}</p>
  </div>
  <div class="brand-story__metrics">
    <div class="metric-card" data-target="{value-1}">
      <span class="metric-card__number">0</span>
      <span class="metric-card__label">{label-1}</span>
    </div>
    <div class="metric-card" data-target="{value-2}">
      <span class="metric-card__number">0</span>
      <span class="metric-card__label">{label-2}</span>
    </div>
    <div class="metric-card" data-target="{value-3}">
      <span class="metric-card__number">0</span>
      <span class="metric-card__label">{label-3}</span>
    </div>
  </div>
</section>
```

---

## 4. Category Product Page Content Template

Content block for `pages/03-{category}.html` `<main>`:

```html
<section class="category-page" id="{category-id}">
  <!-- Category Divider -->
  <div class="category-divider">
    <img src="../images/categories/{category-image}" alt="{category-name}" class="category-divider__image" loading="lazy">
    <div class="category-divider__overlay"></div>
    <div class="category-divider__content">
      <h2 class="category-divider__title">{category-name}</h2>
      <p class="category-divider__description">{category-intro-text}</p>
      <span class="category-divider__count">{product-count} Products</span>
    </div>
  </div>

  <!-- Product Grid -->
  <div class="product-grid product-grid--{layout-type}">

    <!-- Hero Product (full-width) -->
    <article class="product-card product-card--hero" data-product-id="{id}">
      <div class="product-card__badges">
        <span class="badge badge--new">NEW</span>
      </div>
      <div class="product-card__image">
        <img src="../images/products/{image}" alt="{product-name}" loading="lazy">
      </div>
      <div class="product-card__content">
        <h3 class="product-card__name">{headline}</h3>
        <p class="product-card__subtitle">{subhead}</p>
        <p class="product-card__description">{body-copy}</p>
        <ul class="product-card__features">
          <li>{feature-1}</li>
          <li>{feature-2}</li>
          <li>{feature-3}</li>
        </ul>
        <div class="product-card__pricing">
          <span class="price price--original">{original-price}</span>
          <span class="price price--current">{current-price}</span>
        </div>
        <a href="#contact" class="cta-button cta-button--primary">{cta-text}</a>
      </div>
    </article>

    <!-- Standard Product Cards -->
    <article class="product-card product-card--standard" data-product-id="{id}">
      <div class="product-card__badges">
        <span class="badge badge--{type}">{badge-text}</span>
      </div>
      <div class="product-card__image">
        <img src="../images/products/{image}" alt="{product-name}" loading="lazy">
      </div>
      <div class="product-card__content">
        <h3 class="product-card__name">{headline}</h3>
        <p class="product-card__subtitle">{subhead}</p>
        <p class="product-card__description">{body-copy}</p>
        <ul class="product-card__features">
          <li>{feature-1}</li>
          <li>{feature-2}</li>
        </ul>
        <div class="product-card__pricing">
          <span class="price price--current">{current-price}</span>
        </div>
        <a href="#contact" class="cta-button">{cta-text}</a>
      </div>
    </article>

    <!-- Repeat product cards... -->

  </div>

  <!-- Cross-Selling Section (when 3+ products in category) -->
  <section class="cross-sell-section">
    <h3 class="cross-sell-section__title">You May Also Like</h3>
    <div class="cross-sell-carousel">
      <button class="carousel-prev" aria-label="Previous">&lsaquo;</button>
      <div class="carousel-track">
        <div class="cross-sell-card">
          <img src="../images/products/{thumb}" alt="{product-name}" loading="lazy">
          <span class="cross-sell-card__name">{product-name}</span>
          <span class="cross-sell-card__price">{price}</span>
        </div>
        <!-- Repeat cross-sell cards... -->
      </div>
      <button class="carousel-next" aria-label="Next">&rsaquo;</button>
    </div>
  </section>

  <!-- Bundle Proposal Box (when complementary products detected) -->
  <section class="bundle-box">
    <div class="bundle-box__badge">BUNDLE DEAL</div>
    <h3 class="bundle-box__title">Better Together</h3>
    <p class="bundle-box__description">{bundle-description}</p>
    <div class="bundle-box__products">
      <div class="bundle-product">
        <img src="../images/products/{image-1}" alt="{name-1}" loading="lazy">
        <span>{name-1}</span>
      </div>
      <span class="bundle-box__plus">+</span>
      <div class="bundle-product">
        <img src="../images/products/{image-2}" alt="{name-2}" loading="lazy">
        <span>{name-2}</span>
      </div>
    </div>
    <div class="bundle-box__pricing">
      <span class="price price--original">{individual-total}</span>
      <span class="price price--bundle">{bundle-price}</span>
      <span class="bundle-box__savings">Save {discount}%</span>
    </div>
    <a href="#contact" class="cta-button cta-button--accent">{bundle-cta}</a>
  </section>
</section>
```

---

## 5. Contact Page Content Template

Content block for `pages/XX-contact.html` `<main>`:

```html
<section class="contact-page" id="contact">
  <h2 class="contact-page__title">Get In Touch</h2>
  <p class="contact-page__subtitle">Ready to order? We'd love to hear from you.</p>

  <div class="contact-grid">
    <div class="contact-card">
      <div class="contact-card__icon">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/>
          <line x1="12" y1="17" x2="12" y2="21"/>
        </svg>
      </div>
      <h3>Online</h3>
      <p>{website-url}</p>
      <a href="{website-url}" class="cta-button">Visit Website</a>
    </div>

    <div class="contact-card">
      <div class="contact-card__icon">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07
          19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72"/>
        </svg>
      </div>
      <h3>Phone</h3>
      <p>{phone-number}</p>
      <p class="contact-card__hours">{business-hours}</p>
    </div>

    <div class="contact-card">
      <div class="contact-card__icon">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
          <polyline points="22,6 12,13 2,6"/>
        </svg>
      </div>
      <h3>Email</h3>
      <p>{email-address}</p>
      <a href="mailto:{email-address}" class="cta-button">Send Email</a>
    </div>

    <div class="contact-card">
      <div class="contact-card__icon">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
          <circle cx="12" cy="10" r="3"/>
        </svg>
      </div>
      <h3>Visit Us</h3>
      <p>{address}</p>
    </div>
  </div>

  <!-- QR Code Placeholder -->
  <div class="qr-section">
    <div class="qr-code" aria-label="QR code for {website-url}">
      <div class="qr-placeholder">QR</div>
    </div>
    <p class="qr-section__label">Scan to visit our website</p>
  </div>

  <!-- Shipping & Warranty Info -->
  <div class="info-grid">
    <div class="info-card">
      <h4>Shipping</h4>
      <p>{shipping-info}</p>
    </div>
    <div class="info-card">
      <h4>Returns & Warranty</h4>
      <p>{warranty-info}</p>
    </div>
    <div class="info-card">
      <h4>After-Sales Service</h4>
      <p>{service-info}</p>
    </div>
  </div>
</section>
```

---

## 6. Index Page Template (`index.html`)

The index page uses a safe DOM-based page loader instead of innerHTML injection. Page content sections are statically embedded during generation (not fetched at runtime), ensuring both security and offline compatibility.

```html
<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{catalog-name} — {brand-name}</title>
  <meta name="description" content="{catalog-description}">
  <link rel="stylesheet" href="assets/tokens.css">
  <link rel="stylesheet" href="assets/catalog-base.css">
  <link rel="stylesheet" href="assets/catalog-components.css">
  <link rel="stylesheet" href="assets/catalog-interactions.css">
  <link rel="stylesheet" href="assets/catalog-print.css" media="print">
</head>
<body>
  <!-- Sticky Header -->
  <header class="catalog-header catalog-header--sticky">
    <a href="index.html" class="catalog-logo">{brand-name}</a>
    <nav class="catalog-nav">
      <ul class="nav-categories">
        <li><a href="#cover" class="nav-tab nav-tab--active">Home</a></li>
        <!-- Dynamic category tabs -->
        <li><a href="#{category-id}" class="nav-tab">{category-name}</a></li>
      </ul>
    </nav>
    <div class="header-actions">
      <button class="search-trigger" aria-label="Search (Cmd+K)">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
      </button>
      <button class="theme-toggle" aria-label="Toggle theme"></button>
      <button class="font-size-toggle" aria-label="Font size">A</button>
    </div>
  </header>

  <!-- Search Overlay (same as page template) -->
  <div class="search-overlay" id="searchOverlay" hidden>
    <div class="search-dialog">
      <input type="search" class="search-input" placeholder="Search products..." autofocus>
      <ul class="search-results"></ul>
      <div class="search-empty" hidden>No results found</div>
      <footer class="search-footer">
        <kbd>Esc</kbd> to close &middot; <kbd>Enter</kbd> to select
      </footer>
    </div>
  </div>

  <!-- Unified Single-Scroll View -->
  <!-- NOTE: During generation, the skill statically embeds each page's
       <main> content directly into these sections. This avoids runtime
       fetch + innerHTML injection (XSS risk) and works fully offline. -->
  <main class="catalog-unified" id="catalogUnified">
    <!-- Cover section (statically embedded) -->
    <section class="catalog-section" id="cover">
      <!-- 01-cover.html main content placed here at build time -->
    </section>

    <!-- Brand Story section (statically embedded, optional) -->
    <section class="catalog-section" id="brand-story">
      <!-- 02-brand-story.html main content placed here at build time -->
    </section>

    <!-- Category sections (statically embedded) -->
    <section class="catalog-section" id="{category-id}">
      <!-- 03-{category}.html main content placed here at build time -->
    </section>

    <!-- Contact section (statically embedded) -->
    <section class="catalog-section" id="contact">
      <!-- XX-contact.html main content placed here at build time -->
    </section>
  </main>

  <!-- Floating TOC (sidebar, shows on scroll past cover) -->
  <aside class="floating-toc" id="floatingToc" hidden>
    <nav aria-label="Table of Contents">
      <ul>
        <li><a href="#cover" class="toc-link toc-link--active">Cover</a></li>
        <li><a href="#brand-story" class="toc-link">Our Story</a></li>
        <li><a href="#{category-id}" class="toc-link">{category-name}</a></li>
        <li><a href="#contact" class="toc-link">Contact</a></li>
      </ul>
    </nav>
  </aside>

  <script src="shared/theme.js"></script>
  <script src="shared/nav.js"></script>
  <script src="shared/interactions.js"></script>
</body>
</html>
```

> **IMPORTANT — Static Embedding**: The skill MUST statically embed page content into `index.html` at generation time (copy the `<main>` content from each page file directly into the corresponding `<section>`). Do NOT use runtime `fetch()` + `innerHTML` injection, as this creates XSS vulnerabilities and breaks offline viewing. The individual `pages/*.html` files remain independently accessible for standalone viewing.

---

## 7. JavaScript Modules

### 7.1 `shared/theme.js` — Theme & Font Size

```javascript
(function() {
  'use strict';

  // Theme Toggle
  const THEME_KEY = 'catalog-theme';
  const FONT_KEY = 'catalog-font-size';

  function getStoredTheme() {
    return localStorage.getItem(THEME_KEY) || 'light';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
    document.querySelectorAll('.icon-sun').forEach(function(el) { el.style.display = theme === 'light' ? '' : 'none'; });
    document.querySelectorAll('.icon-moon').forEach(function(el) { el.style.display = theme === 'dark' ? '' : 'none'; });
  }

  applyTheme(getStoredTheme());

  document.querySelectorAll('.theme-toggle').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var current = document.documentElement.getAttribute('data-theme');
      applyTheme(current === 'dark' ? 'light' : 'dark');
    });
  });

  // Font Size Toggle
  var sizes = ['small', 'medium', 'large'];
  var currentSizeIdx = sizes.indexOf(localStorage.getItem(FONT_KEY) || 'medium');
  if (currentSizeIdx < 0) currentSizeIdx = 1;

  function applyFontSize(idx) {
    document.documentElement.setAttribute('data-font', sizes[idx]);
    localStorage.setItem(FONT_KEY, sizes[idx]);
  }

  applyFontSize(currentSizeIdx);

  document.querySelectorAll('.font-size-toggle').forEach(function(btn) {
    btn.addEventListener('click', function() {
      currentSizeIdx = (currentSizeIdx + 1) % sizes.length;
      applyFontSize(currentSizeIdx);
    });
  });
})();
```

### 7.2 `shared/nav.js` — Navigation & Keyboard

```javascript
(function() {
  'use strict';

  // Floating TOC visibility
  var toc = document.getElementById('floatingToc');
  var cover = document.getElementById('cover');

  if (toc && cover) {
    var observer = new IntersectionObserver(function(entries) {
      toc.hidden = entries[0].isIntersecting;
    }, { threshold: 0.1 });
    observer.observe(cover);
  }

  // Active section tracking
  var sections = document.querySelectorAll('.catalog-section');
  var tocLinks = document.querySelectorAll('.toc-link');

  if (sections.length && tocLinks.length) {
    var sectionObserver = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          var id = entry.target.id;
          tocLinks.forEach(function(link) {
            link.classList.toggle('toc-link--active', link.getAttribute('href') === '#' + id);
          });
        }
      });
    }, { rootMargin: '-20% 0px -80% 0px' });

    sections.forEach(function(s) { sectionObserver.observe(s); });
  }

  // Keyboard navigation (arrow keys for page-level nav)
  document.addEventListener('keydown', function(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    var prevLink = document.querySelector('.page-nav__prev');
    var nextLink = document.querySelector('.page-nav__next');

    if (e.key === 'ArrowLeft' && prevLink) {
      prevLink.click();
    } else if (e.key === 'ArrowRight' && nextLink) {
      nextLink.click();
    }
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
    anchor.addEventListener('click', function(e) {
      var target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
})();
```

### 7.3 `shared/interactions.js` — Search, Gallery, Filters

```javascript
(function() {
  'use strict';

  // === Search (Cmd+K) ===
  var overlay = document.getElementById('searchOverlay');
  var searchInput = overlay ? overlay.querySelector('.search-input') : null;
  var resultsList = overlay ? overlay.querySelector('.search-results') : null;
  var emptyState = overlay ? overlay.querySelector('.search-empty') : null;

  // Build search index from product cards
  var products = [];
  document.querySelectorAll('.product-card').forEach(function(card) {
    var nameEl = card.querySelector('.product-card__name');
    var subtitleEl = card.querySelector('.product-card__subtitle');
    var descEl = card.querySelector('.product-card__description');
    products.push({
      id: card.dataset.productId,
      name: nameEl ? nameEl.textContent : '',
      subtitle: subtitleEl ? subtitleEl.textContent : '',
      description: descEl ? descEl.textContent : '',
      element: card
    });
  });

  function openSearch() {
    if (!overlay) return;
    overlay.hidden = false;
    searchInput.value = '';
    searchInput.focus();
    renderResults('');
  }

  function closeSearch() {
    if (!overlay) return;
    overlay.hidden = true;
  }

  function renderResults(query) {
    if (!resultsList || !emptyState) return;
    // Clear existing results safely
    while (resultsList.firstChild) {
      resultsList.removeChild(resultsList.firstChild);
    }
    if (!query) { emptyState.hidden = true; return; }

    var q = query.toLowerCase();
    var matches = products.filter(function(p) {
      return p.name.toLowerCase().indexOf(q) !== -1 ||
             p.subtitle.toLowerCase().indexOf(q) !== -1 ||
             p.description.toLowerCase().indexOf(q) !== -1;
    });

    emptyState.hidden = matches.length > 0;

    matches.forEach(function(p) {
      var li = document.createElement('li');
      li.className = 'search-result-item';
      li.textContent = p.name;
      li.addEventListener('click', function() {
        closeSearch();
        p.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        p.element.classList.add('product-card--highlight');
        setTimeout(function() { p.element.classList.remove('product-card--highlight'); }, 2000);
      });
      resultsList.appendChild(li);
    });
  }

  // Keyboard shortcuts
  document.addEventListener('keydown', function(e) {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      overlay && !overlay.hidden ? closeSearch() : openSearch();
    }
    if (e.key === 'Escape') closeSearch();
  });

  if (searchInput) {
    searchInput.addEventListener('input', function(e) { renderResults(e.target.value); });
  }

  if (overlay) {
    overlay.addEventListener('click', function(e) {
      if (e.target === overlay) closeSearch();
    });
  }

  document.querySelectorAll('.search-trigger').forEach(function(btn) {
    btn.addEventListener('click', openSearch);
  });

  // === Image Gallery / Lightbox ===
  document.querySelectorAll('.product-card__image img').forEach(function(img) {
    img.style.cursor = 'zoom-in';
    img.addEventListener('click', function() {
      // Build lightbox using safe DOM methods
      var lightbox = document.createElement('div');
      lightbox.className = 'lightbox';

      var backdrop = document.createElement('div');
      backdrop.className = 'lightbox__backdrop';

      var content = document.createElement('div');
      content.className = 'lightbox__content';

      var lbImg = document.createElement('img');
      lbImg.src = img.src;
      lbImg.alt = img.alt;

      var closeBtn = document.createElement('button');
      closeBtn.className = 'lightbox__close';
      closeBtn.setAttribute('aria-label', 'Close');
      closeBtn.textContent = '\u00D7'; // × character

      content.appendChild(lbImg);
      content.appendChild(closeBtn);
      lightbox.appendChild(backdrop);
      lightbox.appendChild(content);
      document.body.appendChild(lightbox);

      requestAnimationFrame(function() { lightbox.classList.add('lightbox--open'); });

      function closeLightbox() {
        lightbox.classList.remove('lightbox--open');
        setTimeout(function() { lightbox.remove(); }, 300);
      }

      backdrop.addEventListener('click', closeLightbox);
      closeBtn.addEventListener('click', closeLightbox);
      document.addEventListener('keydown', function handler(e) {
        if (e.key === 'Escape') { closeLightbox(); document.removeEventListener('keydown', handler); }
      });
    });
  });

  // === Counter Animation (Brand Story metrics) ===
  document.querySelectorAll('.metric-card').forEach(function(card) {
    var target = parseInt(card.dataset.target, 10);
    var numberEl = card.querySelector('.metric-card__number');
    if (!numberEl || isNaN(target)) return;

    var counterObserver = new IntersectionObserver(function(entries) {
      if (entries[0].isIntersecting) {
        counterObserver.disconnect();
        var current = 0;
        var step = Math.max(1, Math.ceil(target / 60));
        var timer = setInterval(function() {
          current = Math.min(current + step, target);
          numberEl.textContent = current.toLocaleString();
          if (current >= target) clearInterval(timer);
        }, 16);
      }
    }, { threshold: 0.5 });
    counterObserver.observe(card);
  });

  // === Cross-sell Carousel ===
  document.querySelectorAll('.cross-sell-carousel').forEach(function(carousel) {
    var track = carousel.querySelector('.carousel-track');
    var prevBtn = carousel.querySelector('.carousel-prev');
    var nextBtn = carousel.querySelector('.carousel-next');
    if (!track || !prevBtn || !nextBtn) return;

    var scrollAmount = 220;
    prevBtn.addEventListener('click', function() { track.scrollBy({ left: -scrollAmount, behavior: 'smooth' }); });
    nextBtn.addEventListener('click', function() { track.scrollBy({ left: scrollAmount, behavior: 'smooth' }); });
  });

  // === Screenshot Tabs (Desktop/Tablet/Mobile) ===
  document.querySelectorAll('.screenshot-tabs').forEach(function(tabGroup) {
    var gallery = tabGroup.closest('.product-card__screenshot-gallery') ||
                  tabGroup.closest('.showcase-responsive');
    if (!gallery) return;

    var tabs = tabGroup.querySelectorAll('.screenshot-tab');
    var panels = gallery.querySelectorAll('.screenshot-panel');

    tabs.forEach(function(tab) {
      tab.addEventListener('click', function() {
        var viewport = tab.dataset.viewport;
        tabs.forEach(function(t) { t.classList.toggle('screenshot-tab--active', t === tab); });
        panels.forEach(function(p) {
          p.classList.toggle('screenshot-panel--active', p.dataset.viewport === viewport);
        });
      });
    });
  });

  // === Scroll-triggered Animations for Illustrations & Screenshots ===
  var animatedEls = document.querySelectorAll('.illustration-break, .screenshot-frame, .showcase-step');
  if (animatedEls.length) {
    var animObserver = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          animObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    animatedEls.forEach(function(el) { animObserver.observe(el); });
  }

  // === Device Showcase 3D Tilt (on hover) ===
  document.querySelectorAll('.showcase-devices').forEach(function(showcase) {
    showcase.addEventListener('mousemove', function(e) {
      var rect = showcase.getBoundingClientRect();
      var x = (e.clientX - rect.left) / rect.width - 0.5;
      var y = (e.clientY - rect.top) / rect.height - 0.5;
      showcase.style.setProperty('--tilt-x', (y * 8) + 'deg');
      showcase.style.setProperty('--tilt-y', (x * -8) + 'deg');
    });
    showcase.addEventListener('mouseleave', function() {
      showcase.style.setProperty('--tilt-x', '0deg');
      showcase.style.setProperty('--tilt-y', '0deg');
    });
  });
})();
```

---

## 8. Screenshot Showcase Page Content Template

Content block for `pages/{NN}-showcase.html` `<main>` (only generated when `{SERVICE_URL}` is available):

```html
<section class="showcase-page" id="showcase">
  <!-- Hero Screenshot -->
  <div class="showcase-hero">
    <h2 class="showcase-hero__title">See It In Action</h2>
    <p class="showcase-hero__subtitle">Experience the product firsthand — real screenshots from the live service</p>
    <div class="screenshot-frame screenshot-frame--browser screenshot-frame--hero">
      <div class="screenshot-frame__chrome">
        <span class="screenshot-frame__dot"></span>
        <span class="screenshot-frame__dot"></span>
        <span class="screenshot-frame__dot"></span>
        <span class="screenshot-frame__url">{SERVICE_URL}</span>
      </div>
      <img src="../images/screenshots/desktop/{hero-screenshot}" alt="{product-name} overview" loading="lazy">
    </div>
  </div>

  <!-- 3-Device Showcase -->
  <div class="showcase-devices">
    <div class="showcase-device showcase-device--desktop">
      <div class="screenshot-frame screenshot-frame--browser">
        <div class="screenshot-frame__chrome">
          <span class="screenshot-frame__dot"></span>
          <span class="screenshot-frame__dot"></span>
          <span class="screenshot-frame__dot"></span>
          <span class="screenshot-frame__url">{SERVICE_URL}</span>
        </div>
        <img src="../images/screenshots/desktop/{screenshot}" alt="Desktop view" loading="lazy">
      </div>
    </div>
    <div class="showcase-device showcase-device--tablet">
      <div class="screenshot-frame screenshot-frame--tablet">
        <img src="../images/screenshots/tablet/{screenshot}" alt="Tablet view" loading="lazy">
      </div>
    </div>
    <div class="showcase-device showcase-device--mobile">
      <div class="screenshot-frame screenshot-frame--mobile">
        <img src="../images/screenshots/mobile/{screenshot}" alt="Mobile view" loading="lazy">
      </div>
    </div>
  </div>

  <!-- Editorial Illustration Divider -->
  <div class="illustration-break illustration-break--wide">
    <img src="../images/illustrations/{mood-separator}" alt="" role="presentation" loading="lazy">
  </div>

  <!-- Feature Walkthrough -->
  <div class="showcase-flow">
    <h3 class="showcase-flow__title">How It Works</h3>

    <div class="showcase-step">
      <div class="showcase-step__number">1</div>
      <div class="showcase-step__screenshot">
        <div class="screenshot-frame screenshot-frame--browser">
          <div class="screenshot-frame__chrome">
            <span class="screenshot-frame__dot"></span>
            <span class="screenshot-frame__dot"></span>
            <span class="screenshot-frame__dot"></span>
            <span class="screenshot-frame__url">{step-url}</span>
          </div>
          <img src="../images/screenshots/desktop/{step-screenshot}" alt="{step-title}" loading="lazy">
        </div>
      </div>
      <div class="showcase-step__content">
        <h4>{step-title}</h4>
        <p>{step-description}</p>
      </div>
    </div>
    <!-- Repeat showcase-step for each flow step... -->
  </div>

  <!-- Responsive Comparison -->
  <div class="showcase-responsive">
    <h3 class="showcase-responsive__title">Beautiful On Every Device</h3>
    <div class="screenshot-tabs">
      <button class="screenshot-tab screenshot-tab--active" data-viewport="desktop">Desktop</button>
      <button class="screenshot-tab" data-viewport="tablet">Tablet</button>
      <button class="screenshot-tab" data-viewport="mobile">Mobile</button>
    </div>
    <div class="screenshot-panels screenshot-panels--showcase">
      <div class="screenshot-panel screenshot-panel--active" data-viewport="desktop">
        <div class="screenshot-frame screenshot-frame--browser">
          <div class="screenshot-frame__chrome">
            <span class="screenshot-frame__dot"></span>
            <span class="screenshot-frame__dot"></span>
            <span class="screenshot-frame__dot"></span>
            <span class="screenshot-frame__url">{SERVICE_URL}</span>
          </div>
          <img src="../images/screenshots/desktop/{screenshot}" alt="Desktop view" loading="lazy">
        </div>
      </div>
      <div class="screenshot-panel" data-viewport="tablet">
        <div class="screenshot-frame screenshot-frame--tablet">
          <img src="../images/screenshots/tablet/{screenshot}" alt="Tablet view" loading="lazy">
        </div>
      </div>
      <div class="screenshot-panel" data-viewport="mobile">
        <div class="screenshot-frame screenshot-frame--mobile">
          <img src="../images/screenshots/mobile/{screenshot}" alt="Mobile view" loading="lazy">
        </div>
      </div>
    </div>
  </div>

  <!-- CTA Section -->
  <div class="showcase-cta">
    <div class="showcase-cta__bg">
      <img src="../images/illustrations/{infographic-base}" alt="" role="presentation" loading="lazy">
    </div>
    <h3 class="showcase-cta__title">Ready to Experience It Yourself?</h3>
    <p class="showcase-cta__description">{cta-description}</p>
    <a href="#contact" class="cta-button cta-button--primary cta-button--large">{cta-text}</a>
  </div>
</section>
```

---

## 9. Editorial Illustration Break Template

Inserted between product groups and categories for magazine-like visual rhythm:

```html
<!-- Mood Separator (between categories/product groups) -->
<div class="illustration-break" role="presentation">
  <img src="../images/illustrations/{mood-image}" alt="" loading="lazy">
</div>

<!-- Full-Width Illustration with Overlay Text (category transition) -->
<div class="illustration-break illustration-break--with-text">
  <img src="../images/illustrations/{illustration-image}" alt="" loading="lazy">
  <div class="illustration-break__overlay">
    <p class="illustration-break__quote">{editorial-quote}</p>
  </div>
</div>

<!-- Detail Texture Background Section (for spec/comparison areas) -->
<div class="texture-bg-section" style="--texture-bg: url('../images/illustrations/{texture-image}')">
  <!-- Spec tables, comparison content placed inside -->
</div>
```
