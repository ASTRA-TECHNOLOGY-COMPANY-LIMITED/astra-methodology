---
name: catalog-generator
description: "Automatically generates a professional product promotional catalog as a self-contained HTML package from product data. Executes the full catalog production pipeline — planning, data normalization, design, copywriting, and validation — in a single pass without user feedback."
argument-hint: "[product data file path, URL, or product description]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, Skill, mcp__fect-image__image_text2img, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__wait_for, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__resize_page, mcp__chrome-devtools__click, mcp__chrome-devtools__fill, mcp__chrome-devtools__press_key, mcp__chrome-devtools__new_page, mcp__chrome-devtools__select_page, mcp__chrome-devtools__close_page
---

# Product Promotional Catalog Auto-Generator

Analyzes product data (CSV/JSON/text/URL) and produces a production-grade HTML catalog by applying **professional catalog designers' workflows and expert know-how**.

**Core Principles**:
- **Fully autonomous from input to final deliverable** — all decisions (design tone, layout, copy, product placement) are made by AI based on product characteristics, with zero user interaction
- **Expert know-how applied** — based on `$CLAUDE_PLUGIN_ROOT/docs/catalog/catalog-expert-workflow.md`
- **Built-in sales strategies** — cross-selling, upselling, price anchoring, and CTA placement applied automatically
- **Professional copywriting techniques** — benefit-driven, sensory language, storytelling, social proof
- **`/frontend-design` skill integration** — polished, production-grade design (prevents generic AI aesthetics)
- **`fect-image` MCP integration** — auto-generates hero banners, lifestyle images, editorial illustrations, and category visuals
- **Chrome MCP integration** — captures real product/service screenshots for "See it in action" showcases and UI demonstrations
- Responsive (mobile/tablet/desktop), dark mode, and print stylesheet support
- Opens directly in browser with no build step required

**Output location**: `catalog/{catalog-name}/`

> **LANGUAGE RULE**: Before executing this skill, read the project's `CLAUDE.md` and check the `## Language` section to detect the project language. If the project language is NOT Korean (`ko`), you MUST translate ALL user-facing output — including HTML page titles, labels, placeholder text, navigation text — into the project language. Technical identifiers (file paths, CSS variable names, class names) remain untranslated. If no `CLAUDE.md` exists or no `## Language` section is found, default to Korean.

---

## Execution Procedure

### Step 0: Preparation — Data Collection & Analysis

#### A. Argument Parsing

Analyze `$ARGUMENTS` to determine the product data source:

| Argument Type | Action |
|---------------|--------|
| CSV/JSON file path (e.g. `products.csv`) | Read file and extract product list |
| Directory path (e.g. `data/products/`) | Collect all data files + images from directory |
| URL (e.g. `https://example.com/products`) | Store as `{SERVICE_URL}` — Chrome MCP captures product screenshots from live site |
| Text description (e.g. `5 premium kitchen items`) | Structure product data from text input |
| _(empty)_ | Auto-scan current directory for product data files (`*.csv`, `*.json`, `*.xlsx`, etc.) |

#### B. Product Data Normalization

Normalize collected data into the internal standard structure:

```json
{
  "catalog": {
    "name": "{catalog-name}",
    "brand": "{brand-name}",
    "tagline": "{brand-slogan}",
    "contact": { "phone": "", "email": "", "website": "", "address": "" }
  },
  "categories": [
    {
      "id": "cat-01",
      "name": "{category-name}",
      "description": "{category-description}",
      "products": [
        {
          "id": "prod-001",
          "name": "{product-name}",
          "price": 0,
          "originalPrice": null,
          "description": "{product-description}",
          "features": ["{feature-1}", "{feature-2}"],
          "specs": { "{spec-key}": "{value}" },
          "images": ["{image-path}"],
          "badges": [],
          "crossSell": ["{related-product-id}"],
          "tier": "standard|premium|budget"
        }
      ]
    }
  ]
}
```

**Data Enrichment Rules**:
- If price is missing, replace pricing area with `Contact Us` label
- If images are missing, auto-generate via `fect-image` MCP based on product description
- If categories are not specified, auto-group by product characteristics
- `crossSell` field auto-maps IDs of same-category or complementary products
- `tier` auto-classifies based on price distribution (top 20% → premium, bottom 20% → budget)

#### C. Load Expert References

Read the following reference files to load expert know-how into context:

1. `$CLAUDE_PLUGIN_ROOT/docs/catalog/catalog-expert-workflow.md` — Full workflow & know-how
2. `$CLAUDE_PLUGIN_ROOT/skills/catalog-generator/references/catalog-html-templates.md` — HTML structure templates
3. `$CLAUDE_PLUGIN_ROOT/skills/catalog-generator/references/catalog-css-template.md` — CSS component templates

#### D. Auto-Determine Design Tone

Analyze product data characteristics to **autonomously decide** the design tone:

| Product Characteristics | Auto-Selected Design Tone | Rationale |
|------------------------|--------------------------|-----------|
| Luxury/premium (high price, few items) | **Editorial Luxury** | Generous whitespace, large images, serif typography |
| Tech/electronics | **Modern Minimal** | Clean layout, spec tables, sans-serif |
| Fashion/beauty/lifestyle | **Bold & Vibrant** | Emotional visuals, lifestyle shots, bold colors |
| Food/beverage | **Soft & Warm** | Warm tones, soft curves, friendly copy |
| B2B/industrial/components | **Professional Enterprise** | High-density grid, comparison tables, trust signals |
| Children/education/toys | **Playful Bright** | Bright colors, rounded corners, fun illustrations |
| Mixed/indeterminate | **Refined Minimal** | Safe universal choice — clean and polished |

Store the determined tone as `{DESIGN_TONE}` and use it as the basis for all subsequent design decisions.

#### E. Service URL & Screenshot Planning

If `{SERVICE_URL}` is available (URL argument provided), plan Chrome MCP screenshot capture:

1. **Navigate & Analyze**: Open `{SERVICE_URL}` via Chrome MCP and take a snapshot to understand the site structure
   ```
   mcp__chrome-devtools__navigate_page({ url: "{SERVICE_URL}" })
   mcp__chrome-devtools__wait_for({ selector: "body", timeout: 10000 })
   mcp__chrome-devtools__take_snapshot()
   ```

2. **Build Screenshot Plan** — Map product data to live pages/routes:

   | Screenshot Type | When to Capture | Purpose |
   |----------------|----------------|---------|
   | **Product detail page** | Each product has a dedicated URL | Hero-quality product showcase |
   | **Product listing/grid** | Category pages exist | Category overview visuals |
   | **Product in-use / demo** | Interactive features available | "See it in action" showcase |
   | **Key UI moments** | Checkout, config, comparison pages | Trust-building screenshots |
   | **Mobile views** | Always (responsive resize) | Mobile-first showcase |

3. **Store as `{SCREENSHOT_PLAN}`** — Array of `{ url, selector, description, category, viewport }` entries

If no `{SERVICE_URL}` is provided, set `{SCREENSHOT_PLAN}` to empty — all visuals will come from fect-image AI generation.

#### F. Auto-Design Catalog Structure

Automatically determine page structure based on product count and categories:

| Component | Rule |
|-----------|------|
| **Cover** | Always included — brand name, tagline, hero image |
| **Brand Story** | Included when 10+ products — 1 page |
| **Table of Contents** | Included when 3+ categories |
| **Category Dividers** | Included when 2+ categories — entry page per category |
| **Product Detail Pages** | All products — 1–4 per page (based on importance & image size) |
| **Cross-Selling Sections** | Auto-placed when 3+ products in a category |
| **Bundle/Set Proposals** | Auto-generated when complementary product relationships detected |
| **Order/Contact Info** | Always included — last page |

Per-product space allocation within pages:

| Product Tier | Page Occupancy | Image Size |
|-------------|---------------|------------|
| **Hero (top revenue/new arrivals)** | 1 product / full spread | 60%+ of page |
| **Premium** | 1–2 products / page | 40–50% of page |
| **Standard** | 2–3 products / page | 30% of page |
| **List (high item count)** | 4–6 products / page (grid) | Thumbnail |

Additional visual sections (auto-included when applicable):

| Component | Rule |
|-----------|------|
| **Screenshot Showcase** | Included when `{SERVICE_URL}` provided — "See it in action" section with browser-chrome frames |
| **Editorial Illustrations** | Always included — fect-image generates mood/atmosphere illustrations between categories |
| **Product Gallery** | Included for hero/premium tier products — multi-angle screenshots + lifestyle shots |

#### G. Switch to dev Branch

Before generating output files, switch to the `dev` branch and sync with the latest state. Do not create a work branch — work directly on `dev`. Work branch creation is handled automatically by `/pr-merge`.

0. **Main worktree guard**: Abort if invoked from inside an isolated worktree (`.astra-worktrees/<slug>/`). Dev-sync runs in the main worktree only:
   ```bash
   PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
   if [ -z "$PLUGIN_ROOT" ] || [ ! -f "$PLUGIN_ROOT/scripts/worktree-helpers.sh" ]; then
     echo "ERROR: CLAUDE_PLUGIN_ROOT를 찾을 수 없습니다. 플러그인 캐시 경로를 확인하세요." >&2
     exit 1
   fi
   source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"
   astra_ensure_main_worktree || exit 1
   ```
1. **Check current branch**: `git branch --show-current`
2. **Skip if already on `dev`**: If the current branch is `dev`, skip steps 3–5 and run only the pull (`git pull origin dev`)
3. **Preserve uncommitted changes**: Check with `git status --porcelain`; if there are changes, save them with `git stash --include-untracked` (includes untracked files)
4. **Switch to dev and sync**: `git fetch origin dev && git checkout dev && git pull origin dev`
5. **Restore stash**: If step 3 stashed changes, restore them with `git stash pop`. On conflict, report the conflicting files to the user and request manual resolution.

> **Note**: If the `dev` branch does not exist, fall back to `main` or `master`. If no default branch exists, work on the current branch.

---

### Step 1: Generate Common Resources

#### A. Create Directory Structure

```
catalog/{catalog-name}/
├── index.html              # Cover + TOC + navigation hub
├── pages/                  # Individual page HTML files
│   ├── 01-cover.html       # Cover (standalone view)
│   ├── 02-brand-story.html # Brand story (optional)
│   ├── 03-{category}.html  # Category product pages
│   ├── {NN}-showcase.html  # Screenshot showcase — "See it in action" (when SERVICE_URL)
│   └── XX-contact.html     # Order/contact info
├── assets/
│   ├── tokens.css          # Design tokens (colors, typography, spacing)
│   ├── catalog-base.css    # Layout & typography
│   ├── catalog-components.css  # Product cards, badges, CTAs, screenshots, illustrations
│   ├── catalog-print.css   # Print-optimized styles
│   └── catalog-interactions.css # Hover, transitions, animations
├── images/                 # Product images + AI-generated visuals
│   ├── hero/               # Hero banner images
│   ├── products/           # Product images
│   ├── lifestyle/          # Lifestyle shots (AI-generated)
│   ├── illustrations/      # Editorial illustrations (AI-generated, mood/atmosphere)
│   ├── categories/         # Category visuals (AI-generated)
│   └── screenshots/        # Chrome MCP captured screenshots
│       ├── desktop/        # Desktop viewport (1280×800)
│       ├── tablet/         # Tablet viewport (768×1024)
│       └── mobile/         # Mobile viewport (375×812)
└── shared/
    ├── nav.js              # Navigation (page transitions, TOC)
    ├── interactions.js     # Interactions (filter, search, gallery, screenshot tabs)
    └── theme.js            # Dark mode, font size adjustment
```

#### B. Generate Design Tokens

Create `assets/tokens.css` based on `{DESIGN_TONE}`.

Reference the **tone-specific token presets** in `$CLAUDE_PLUGIN_ROOT/skills/catalog-generator/references/catalog-css-template.md` to define CSS Custom Properties.

If the project has `src/styles/design-tokens.css`, extend it with catalog-specific tokens. Otherwise, use the reference default tokens.

Tokens must include:
- Colors: `--cat-color-primary`, `--cat-color-accent`, `--cat-color-bg`, `--cat-color-text`, `--cat-color-price`, `--cat-color-badge-*`
- Typography: `--cat-font-display`, `--cat-font-body`, `--cat-font-size-*`, `--cat-font-weight-*`
- Spacing: `--cat-spacing-*`, `--cat-radius-*`
- Layout: `--cat-page-max-width`, `--cat-grid-gap`, `--cat-product-card-min-width`
- Dark mode: `[data-theme="dark"]` variable set

#### C. Generate CSS Files

Reference `$CLAUDE_PLUGIN_ROOT/skills/catalog-generator/references/catalog-css-template.md` to create 4 CSS files:

1. **`catalog-base.css`** — Layout, grid, typography, responsive breakpoints
2. **`catalog-components.css`** — Product cards, price tags, badges, CTA buttons, comparison tables, bundle boxes
3. **`catalog-print.css`** — A4 print optimization (page breaks, margins, resolution)
4. **`catalog-interactions.css`** — Hover effects, page transitions, gallery animations

Invoke the `/frontend-design` skill to apply polished design matching `{DESIGN_TONE}`:

```
/frontend-design Catalog design system — tone: {DESIGN_TONE}, purpose: product promotional catalog, components: product card / price tag / CTA button / badge / comparison table / bundle box
```

#### D. Generate JS Common Modules

Reference the JS section of `$CLAUDE_PLUGIN_ROOT/skills/catalog-generator/references/catalog-html-templates.md` to create 3 JS files:

1. **`nav.js`** — Page navigation, side TOC, current location highlight, keyboard navigation (← →)
2. **`interactions.js`** — Product filter, search, image gallery (lightbox), comparison feature
3. **`theme.js`** — Dark/light mode toggle, font size adjustment, localStorage settings persistence

---

### Step 2: Visual Asset Production — Screenshots & AI Illustrations

This step produces all visual assets that elevate the catalog from basic to premium quality. Two parallel tracks:
- **Track A**: Chrome MCP screenshots (when `{SERVICE_URL}` available)
- **Track B**: fect-image AI-generated illustrations (always)

#### A. Chrome MCP Screenshot Capture (when `{SERVICE_URL}` available)

> Skip this section entirely if `{SCREENSHOT_PLAN}` is empty.

For each entry in `{SCREENSHOT_PLAN}`:

1. **Navigate to target page**:
   ```
   mcp__chrome-devtools__navigate_page({ url: "{entry.url}" })
   mcp__chrome-devtools__wait_for({ selector: "{entry.selector}", timeout: 10000 })
   ```

2. **Clean up UI for catalog-quality capture** — inject CSS via `evaluate_script` to hide distracting elements:
   ```javascript
   // Inject cleanup styles for catalog-quality screenshots
   var style = document.createElement('style');
   style.id = 'catalog-capture-style';
   style.textContent = `
     .cookie-banner, .chat-widget, .popup-overlay,
     [class*="cookie"], [class*="chat-bot"], [class*="intercom"],
     [class*="notification-bar"] { display: none !important; }
   `;
   document.head.appendChild(style);
   ```

3. **Optional: Highlight key product area** — for product detail pages, add a subtle focus effect:
   ```javascript
   // Add premium highlight to product showcase area
   var target = document.querySelector('{entry.selector}');
   if (target) {
     target.style.boxShadow = '0 0 0 3px rgba(var(--highlight-rgb, 37,99,235), 0.15)';
     target.style.borderRadius = '12px';
   }
   ```

4. **Desktop capture** (1280×800):
   ```
   mcp__chrome-devtools__resize_page({ width: 1280, height: 800 })
   mcp__chrome-devtools__take_screenshot()
   ```
   → Save to `images/screenshots/desktop/{entry.category}-{N}.png`

5. **Tablet capture** (768×1024):
   ```
   mcp__chrome-devtools__resize_page({ width: 768, height: 1024 })
   mcp__chrome-devtools__take_screenshot()
   ```
   → Save to `images/screenshots/tablet/{entry.category}-{N}.png`

6. **Mobile capture** (375×812):
   ```
   mcp__chrome-devtools__resize_page({ width: 375, height: 812 })
   mcp__chrome-devtools__take_screenshot()
   ```
   → Save to `images/screenshots/mobile/{entry.category}-{N}.png`

7. **Cleanup injected styles** — `evaluate_script` to remove `#catalog-capture-style` and reset inline styles

8. **Restore desktop viewport**:
   ```
   mcp__chrome-devtools__resize_page({ width: 1280, height: 800 })
   ```

**Multi-step flow capture** — For interactive product demos (configurators, dashboards, etc.):
1. Capture initial state
2. Interact: `mcp__chrome-devtools__click()`, `mcp__chrome-devtools__fill()`, `mcp__chrome-devtools__press_key()`
3. `mcp__chrome-devtools__wait_for()` for result
4. Capture result state
5. Label screenshots as `{category}-step-{N}.png` for sequential display

#### B. Hero Banner Generation (fect-image)

Use `mcp__fect-image__image_text2img` to generate the cover hero image.

Prompt composition — use rich, art-directed prompts for premium quality:
```
Cinematic product catalog hero banner, {product-category} theme,
{DESIGN_TONE} aesthetic, premium commercial photography,
dramatic lighting, shallow depth of field, editorial magazine quality,
{brand-color} color accent, ultra-wide 21:9 composition,
negative space for text overlay on the left third
```

Save generated image to `images/hero/`.

#### C. Category Visual Generation (fect-image)

If there are 2+ categories, generate a divider image for each category.

Prompt composition:
```
{category-name} product category editorial visual, {DESIGN_TONE} style,
abstract artistic background, luxury commercial catalog quality,
soft gradient lighting, cinematic color grading, 3:2 aspect ratio
```

Save generated images to `images/categories/`.

#### D. Editorial Illustration Generation (fect-image) — NEW

Generate mood/atmosphere illustrations placed between categories and in feature sections. These elevate the catalog from a simple product list to an editorial experience.

| Illustration Type | Placement | Prompt Strategy |
|------------------|-----------|----------------|
| **Mood separator** | Between categories | Abstract, atmospheric, brand-color gradients |
| **Lifestyle scene** | Near hero/premium products | Product in aspirational real-life context |
| **Detail texture** | Background for spec sections | Macro texture, material close-up |
| **Infographic base** | Feature comparison sections | Clean geometric, data-visualization style |
| **Brand atmosphere** | Brand story page | Emotional, storytelling visual |

Prompt composition per type:

**Mood separator**:
```
Abstract artistic illustration, {DESIGN_TONE} aesthetic,
flowing {brand-color} gradients, organic shapes, editorial magazine divider,
minimalist composition, ultra-clean, no text, 4:1 wide panoramic
```

**Lifestyle scene**:
```
{product-name} in {aspirational-context}, editorial lifestyle photography,
{target-audience-lifestyle} setting, warm natural lighting,
magazine-quality composition, {DESIGN_TONE} color palette, 16:9
```

**Detail texture**:
```
Macro close-up of {product-material/texture}, abstract product detail,
{DESIGN_TONE} color grading, shallow depth of field,
premium material texture, subtle bokeh, 3:2 aspect ratio
```

**Infographic base**:
```
Clean geometric abstract background, {DESIGN_TONE} color scheme,
subtle grid pattern, modern data visualization aesthetic,
plenty of negative space for overlay content, 16:9
```

**Brand atmosphere**:
```
{brand-story-theme} conceptual illustration, {DESIGN_TONE} editorial style,
cinematic dramatic lighting, emotional storytelling mood,
abstract artistic interpretation, premium quality, 2:1 wide
```

Save generated images to `images/illustrations/`.

**Generation rules**:
- Mood separators: 1 per category transition (min 1, max 4)
- Lifestyle scenes: 1 per hero/premium product without existing images
- Detail textures: 1–2 for spec-heavy categories
- Infographic base: 1 if comparison tables exist
- Brand atmosphere: 1 for brand story page (if included)

#### E. Lifestyle Shot Generation (fect-image)

For products with no provided images and no Chrome MCP screenshots, generate lifestyle images:

```
{product-name} in real-life premium setting, editorial product photography,
{usage-scene-description}, dramatic studio lighting with natural fill,
{DESIGN_TONE} mood, luxury commercial catalog quality,
styled with complementary props, shallow depth of field, 4:5 portrait
```

Save generated images to `images/lifestyle/`.

> **Rule**: Generate only the minimum required images — prioritize Chrome MCP screenshots over AI generation. For products with both a service URL and AI images, use screenshots for "in action" views and AI images for aspirational lifestyle shots. Skip AI image generation for any product that already has user-provided images.

---

### Step 3: Copywriting — Product Descriptions & Headlines

Apply Section 5 (Copywriting Know-How) from `$CLAUDE_PLUGIN_ROOT/docs/catalog/catalog-expert-workflow.md` to generate all text content.

#### A. Catalog Headline & Tagline

Generate a main catalog headline matched to brand and product characteristics:

- Compress core benefit into a single sentence
- Directly appeal to target customer desires/pain points
- Match tone to `{DESIGN_TONE}` (luxury → restrained elegance, B2B → trust & efficiency)

#### B. Category Introduction Text

Write intro copy for each category entry page:

- 1–2 sentences articulating the category value proposition
- Focus on the problem solved / desire fulfilled by the category

#### C. Per-Product Copy

Generate copy for every product in the following structure:

```
[Headline] — 1 line, attention-grabbing benefit-driven phrase
[Subhead]  — 1 line, key differentiator summary
[Body]     — 2–3 lines, storytelling + sensory language
[Bullets]  — 3–5 key specs/features
```

**Copywriting Rules**:
1. **Benefits > Features**: "500ml capacity" → "Enjoy cold drinks all day long"
2. **Sensory Language**: Expressions that stimulate the five senses (sight, touch, taste, etc.)
3. **Social Proof**: Include specific numbers where possible ("Chosen by 100,000+ customers")
4. **Scannability**: Bold text, bullet points, short paragraphs
5. **CTA Insertion**: Action-driving phrase for each product ("Order Now", "Request a Quote")

#### D. Cross-Selling & Bundle Copy

- Related product recommendation: "Products that pair perfectly with this item"
- Bundle proposal: "Save {N}% when purchased together"
- Upselling prompt: "Looking for higher performance?" → link to premium product

---

### Step 4: Generate Page HTML

Reference `$CLAUDE_PLUGIN_ROOT/skills/catalog-generator/references/catalog-html-templates.md` to generate each page's HTML.

#### A. Cover Page (`pages/01-cover.html`)

- Fullscreen hero image (generated in Step 2.B)
- Brand logo + catalog name + tagline
- Bottom: brief contact info display
- Scroll-down indicator (animated down-arrow)
- If `{SERVICE_URL}` available: overlay subtle screenshot montage (3 device frames at angle) in background

#### B. Brand Story Page (`pages/02-brand-story.html`, when 10+ products)

- Brand atmosphere illustration (generated in Step 2.D) as full-width hero background
- Brand history or value proposition (based on provided data)
- Key metrics counter animation (founding year, customer count, product count, etc.)
- Full-width image or video placeholder
- If `{SERVICE_URL}` available: embed 1–2 key screenshots in browser-chrome frames as "trust signals"

#### C. Category Product Pages (`pages/03-{category}.html`)

Generate one HTML file per category. Structure:

1. **Category Divider Area** — category visual + intro text
2. **Product Grid/List** — apply placement rules determined in Step 0.E

Apply expert know-how for product placement:

- **Z-Pattern Eye Flow**: Place highest-margin products at the top-right corners
- **Price Anchoring**: Show high-priced products first → makes mid-range feel reasonable
- **Cross-Selling Section**: Add "Products you may also like" area when 3+ products in category
- **Bundle Proposal Box**: Dedicated highlight area when complementary product relationships are detected
- **Badge System**: Auto-assign NEW (new arrival), BEST (popular), SALE (discounted), HOT (recommended)
- **Editorial Illustration Breaks**: Insert mood separator illustrations (from Step 2.D) between product groups to create magazine-like visual rhythm
- **Product Screenshot Gallery**: For hero/premium products with Chrome MCP screenshots, add a responsive screenshot tab component (desktop/tablet/mobile views) inside the product card
- **Detail Texture Backgrounds**: Apply detail texture illustrations as subtle background images for spec/comparison sections

Product card HTML structure (enhanced with screenshot gallery and illustrations):

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

> **Note**: The `.product-card__screenshot-gallery` block is only included for hero/premium tier products that have Chrome MCP screenshots. Omit entirely for products without screenshots. The `.illustration-break` is inserted between logical product groups (e.g., after every 3–4 products or between tier boundaries).

#### D. Screenshot Showcase Page (`pages/{NN}-showcase.html`, when `{SERVICE_URL}` available)

A dedicated "See it in action" page that showcases the product/service through captured screenshots — this is the premium differentiator that builds trust and demonstrates real product quality.

Structure:
1. **Hero section** — Full-width desktop screenshot in browser-chrome frame with headline "See It In Action"
2. **Device showcase** — 3-device mockup display (desktop + tablet + mobile) with perspective tilt
3. **Feature walkthrough** — Sequential screenshot cards showing key user flows:
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
4. **Responsive comparison** — Side-by-side responsive views with tab switching
5. **CTA section** — "Ready to experience it yourself?" with primary action button

Apply editorial illustration backgrounds from Step 2.D as subtle section dividers within the showcase page.

#### E. Order/Contact Page (`pages/XX-contact.html`)

- Ordering instructions (online / phone / email / in-person)
- Contact information card
- QR code placeholder (website link)
- Business hours, shipping info, after-sales service

#### F. Index Page (`index.html`)

Entry point for the entire catalog — includes:

- **Inline Cover**: Hero area (01-cover content embedded)
- **Interactive TOC**: Category links + representative image thumbnails
- **Search Bar**: Client-side product name/category search (Cmd+K)
- **Navigation Bar**: Category tabs + dark mode toggle + font size control
- **Unified Inline View**: Fetches `<main>` content from `pages/*.html` and assembles into a single-scroll view (SPA-style)
- **Individual Page Links**: Each page remains independently accessible

---

### Step 5: Validation & Completion Report

#### A. Output Validation

Automatically validate all generated files against the following criteria:

| Validation Item | Criteria |
|----------------|----------|
| **File Existence** | `index.html` + all `pages/*.html` + 4 CSS files + 3 JS files |
| **HTML Validity** | No unclosed tags, no broken relative paths |
| **Image References** | All `<img src>` paths match actual files in `images/` |
| **Screenshot References** | All `images/screenshots/` paths match captured files (when `{SERVICE_URL}`) |
| **Illustration References** | All `images/illustrations/` paths match generated files |
| **Link Integrity** | All internal page-to-page links are valid |
| **Screenshot Tabs** | Desktop/tablet/mobile tabs work correctly (JS interaction test) |
| **Responsiveness** | 3-tier `@media` queries (mobile/tablet/desktop) present |
| **Dark Mode** | `[data-theme="dark"]` styles present for all components incl. screenshot frames |
| **Print Styles** | `catalog-print.css` contains `@page`, `break-*`, and screenshot print rules |
| **Product Count Match** | Input data product count = HTML product card count |
| **Visual Quality** | Illustration breaks placed between categories, no consecutive text-only sections |

If broken references are found, fix them immediately.

#### B. Final Report

```
## Catalog Generation Complete

### Basic Info
- **Catalog Name**: {catalog-name}
- **Design Tone**: {DESIGN_TONE}
- **Service URL**: {SERVICE_URL or "N/A — AI visuals only"}
- **Total Products**: {N} ({category-count} categories)
- **Total Pages**: {N} pages

### Generated Files
| File | Description |
|------|-------------|
| `catalog/{name}/index.html` | Main entry point (cover + TOC + unified view) |
| `catalog/{name}/pages/*.html` | {N} individual pages |
| `catalog/{name}/pages/{NN}-showcase.html` | Screenshot showcase page (if SERVICE_URL) |
| `catalog/{name}/assets/*.css` | 4 stylesheets |
| `catalog/{name}/shared/*.js` | 3 JS modules |
| `catalog/{name}/images/` | {N} total image assets |

### Visual Assets
| Type | Count | Source |
|------|-------|--------|
| Chrome MCP Screenshots | {N} (desktop: {N}, tablet: {N}, mobile: {N}) | Live service capture |
| Hero Banner | 1 | fect-image AI |
| Category Visuals | {N} | fect-image AI |
| Editorial Illustrations | {N} (mood: {N}, lifestyle: {N}, texture: {N}) | fect-image AI |
| Lifestyle Shots | {N} | fect-image AI |
| User-Provided Images | {N} | Original data |

### Applied Sales Strategies
- Cross-selling sections: {N}
- Bundle proposals: {N}
- Price anchoring: {applied/not-applied}
- CTA placements: {N} total
- Screenshot showcase: {"included — builds trust with real product visuals" / "not included — no SERVICE_URL"}

### Preview
> Open `catalog/{name}/index.html` in a browser to preview.
> Print: Use browser print (Cmd+P) for A4-optimized output.
```
