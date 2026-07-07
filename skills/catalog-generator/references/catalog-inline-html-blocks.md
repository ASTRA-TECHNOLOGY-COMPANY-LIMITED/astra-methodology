# Catalog Inline HTML Blocks (Step 4)

Literal HTML skeletons instantiated during page generation. Substitute `{...}` placeholders with product/copy/screenshot data.

## Blocks in this file
- Product card HTML (Step 4.C) — with optional screenshot gallery + illustration break
- Showcase feature-walkthrough step (Step 4.D)

## Product card HTML (Step 4.C)

Enhanced with screenshot gallery and illustration break. The `.product-card__screenshot-gallery` block is only included for hero/premium tier products that have Chrome MCP screenshots — omit it entirely for products without screenshots. The `.illustration-break` is inserted between logical product groups (e.g., after every 3–4 products or between tier boundaries).

```html
<article class="product-card product-card--{tier}" data-product-id="{id}">
  <div class="product-card__badges">
    <span class="badge badge--{type}">{badge-text}</span>
  </div>
  <div class="product-card__image">
    <img src="../images/products/{image}" alt="{product-name}" loading="lazy">
  </div>
  <!-- Screenshot Gallery (hero/premium products with SERVICE_URL only) -->
  <div class="product-card__screenshot-gallery">
    <div class="screenshot-tabs">
      <button class="screenshot-tab screenshot-tab--active" data-viewport="desktop">Desktop</button>
      <button class="screenshot-tab" data-viewport="tablet">Tablet</button>
      <button class="screenshot-tab" data-viewport="mobile">Mobile</button>
    </div>
    <div class="screenshot-panels">
      <div class="screenshot-panel screenshot-panel--active" data-viewport="desktop">
        <div class="screenshot-frame screenshot-frame--browser">
          <div class="screenshot-frame__chrome">
            <span class="screenshot-frame__dot"></span>
            <span class="screenshot-frame__dot"></span>
            <span class="screenshot-frame__dot"></span>
            <span class="screenshot-frame__url">{SERVICE_URL}/{product-route}</span>
          </div>
          <img src="../images/screenshots/desktop/{screenshot}" alt="{product-name} desktop view" loading="lazy">
        </div>
      </div>
      <div class="screenshot-panel" data-viewport="tablet">
        <div class="screenshot-frame screenshot-frame--tablet">
          <img src="../images/screenshots/tablet/{screenshot}" alt="{product-name} tablet view" loading="lazy">
        </div>
      </div>
      <div class="screenshot-panel" data-viewport="mobile">
        <div class="screenshot-frame screenshot-frame--mobile">
          <img src="../images/screenshots/mobile/{screenshot}" alt="{product-name} mobile view" loading="lazy">
        </div>
      </div>
    </div>
  </div>
  <div class="product-card__content">
    <h3 class="product-card__name">{headline}</h3>
    <p class="product-card__subtitle">{subhead}</p>
    <p class="product-card__description">{body}</p>
    <ul class="product-card__features">
      <li>{feature-1}</li>
      <li>{feature-2}</li>
    </ul>
    <div class="product-card__pricing">
      <span class="price price--original">{original-price}</span>
      <span class="price price--current">{current-price}</span>
    </div>
    <a href="#contact" class="cta-button">{cta-text}</a>
  </div>
  <div class="product-card__cross-sell">
    <p>You may also like</p>
    <div class="cross-sell-items">
      <!-- Related product thumbnails -->
    </div>
  </div>
</article>

<!-- Editorial Illustration Break (between product groups) -->
<div class="illustration-break">
  <img src="../images/illustrations/{mood-separator}" alt="" role="presentation" loading="lazy">
</div>
```

## Showcase feature-walkthrough step (Step 4.D)

Sequential screenshot cards showing key user flows:

```html
<div class="showcase-flow">
  <div class="showcase-step">
    <div class="showcase-step__number">1</div>
    <div class="showcase-step__screenshot">
      <div class="screenshot-frame screenshot-frame--browser">
        <div class="screenshot-frame__chrome">
          <span class="screenshot-frame__dot"></span>
          <span class="screenshot-frame__dot"></span>
          <span class="screenshot-frame__dot"></span>
          <span class="screenshot-frame__url">{url}</span>
        </div>
        <img src="../images/screenshots/desktop/{screenshot}" alt="{step-description}" loading="lazy">
      </div>
    </div>
    <div class="showcase-step__content">
      <h3>{step-title}</h3>
      <p>{step-description}</p>
    </div>
  </div>
</div>
```
