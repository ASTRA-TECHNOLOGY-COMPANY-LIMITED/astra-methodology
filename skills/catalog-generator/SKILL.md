---
name: catalog-generator
description: "Automatically generates a professional product promotional catalog as a self-contained HTML package from product data. Executes the full catalog production pipeline — planning, data normalization, design, copywriting, and validation — in a single pass without user feedback."
argument-hint: "[product data file path, URL, or product description]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task, Agent, Skill, mcp__fect-image__image_text2img, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__wait_for, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__resize_page, mcp__chrome-devtools__click, mcp__chrome-devtools__fill, mcp__chrome-devtools__press_key, mcp__chrome-devtools__new_page, mcp__chrome-devtools__select_page, mcp__chrome-devtools__close_page
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
- **Real-browser integration** — captures real product/service screenshots for "See it in action" showcases and UI demonstrations (ego (lite) by default, Chrome MCP as fallback)
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
| URL (e.g. `https://example.com/products`) | Store as `{SERVICE_URL}` — the resolved browser backend captures product screenshots from the live site |
| Text description (e.g. `5 premium kitchen items`) | Structure product data from text input |
| _(empty)_ | Auto-scan current directory for product data files (`*.csv`, `*.json`, `*.xlsx`, etc.) |

#### B. Product Data Normalization

Normalize collected data into the internal standard structure defined in `$CLAUDE_PLUGIN_ROOT/skills/catalog-generator/references/catalog-structures.md` (section "Product data normalization schema"). Read that file and map the collected data onto the schema.

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

If `{SERVICE_URL}` is available (URL argument provided), plan the screenshot capture:

0. **Resolve the backend** — `CAPTURE_BACKEND` per the plugin-wide detection order (**ego default → Chrome MCP fallback**; see `$CLAUDE_PLUGIN_ROOT/docs/development/browser-backend-policy.md`):
   ```bash
   command -v ego-browser >/dev/null 2>&1 && echo ego || echo ""
   ```
   Empty output → `chrome-mcp` when the `mcp__chrome-devtools__*` tools are present. If neither exists, leave `{SCREENSHOT_PLAN}` empty and build the catalog from Track B imagery only, stating that in the final report.

1. **Navigate & Analyze**: open `{SERVICE_URL}`, wait for `body` (10 s), and take a snapshot to understand the site structure — ego: `useOrCreateTaskSpace('astra catalog {catalog-name}')` → `openOrReuseTab` → `snapshotText()`; Chrome MCP: `navigate_page` → `wait_for` → `take_snapshot`.

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

0. **Main worktree guard**: Abort if invoked from inside an isolated worktree (`.worktrees/<slug>/`). Dev-sync runs in the main worktree only:
   ```bash
   PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(find ~/.claude/plugins/cache -maxdepth 3 -type d -path '*/astra-methodology/*' 2>/dev/null | sort -V | tail -1)}"
   if [ -z "$PLUGIN_ROOT" ] || [ ! -f "$PLUGIN_ROOT/scripts/worktree-helpers.sh" ]; then
     echo "ERROR: CLAUDE_PLUGIN_ROOT not found. Check the plugin cache path." >&2
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

Read `$CLAUDE_PLUGIN_ROOT/skills/catalog-generator/references/catalog-structures.md` (section "Output directory structure") and create the directory tree under `catalog/{catalog-name}/`.

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
- **Track A**: browser screenshots — ego (lite) by default, Chrome MCP as fallback (when `{SERVICE_URL}` available)
- **Track B**: fect-image AI-generated illustrations (always)

#### A. Browser Screenshot Capture (when `{SERVICE_URL}` available)

> Skip this section entirely if `{SCREENSHOT_PLAN}` is empty.

Backend is `CAPTURE_BACKEND` from Step 0.E — **ego (default) → Chrome MCP
(fallback)**. Follow the **Deliverable screenshot capture** recipe in
`$CLAUDE_PLUGIN_ROOT/docs/development/browser-backend-policy.md` and use its
Action mapping column for the resolved backend. In ego mode one screen = **one
heredoc**, and `captureScreenshot` paths must be **absolute**.

For each entry in `{SCREENSHOT_PLAN}`:

1. **Navigate** to `{entry.url}`, **wait** for `{entry.selector}` (10 s).

2. **Clean up UI for catalog-quality capture** — inject this stylesheet in-page (`js(...)` in ego, `evaluate_script` in Chrome MCP):
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
   window.scrollTo(0, 0);   // blank-frame guard (required in ego mode)
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

4. **Capture at three viewports** — set the viewport, capture, repeat. ego uses `cdp('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile })`; Chrome MCP uses `resize_page`:

   | Viewport | Size | Output |
   |---|---|---|
   | Desktop | 1280×800 | `images/screenshots/desktop/{entry.category}-{N}.png` |
   | Tablet | 768×1024 | `images/screenshots/tablet/{entry.category}-{N}.png` |
   | Mobile | 375×812 | `images/screenshots/mobile/{entry.category}-{N}.png` |

5. **Cleanup injected styles** — remove `#catalog-capture-style` and reset the inline styles from step 3, so they do not leak into the next entry.

6. **Restore the desktop viewport** — 1280×800; in ego mode `cdp('Emulation.clearDeviceMetricsOverride')`.

7. **Verify each file is non-blank** before using it in the catalog. A blank or missing capture is re-taken; if it still fails, that product falls back to Track B imagery and the final report says so — never present a catalog as screenshot-backed when the captures did not happen.

**Multi-step flow capture** — For interactive product demos (configurators, dashboards, etc.):
1. Capture initial state
2. Interact — click / fill / press per the Action mapping table
3. Wait for the result indicator
4. Capture result state
5. Label screenshots as `{category}-step-{N}.png` for sequential display

> In ego mode the browser carries the user's real login session — keep demo
> interactions read-only and never point a write flow at a production origin.

Once every entry is captured, **ego only**: close the Task Space in a final
heredoc — `completeTaskSpace('astra catalog {catalog-name}', { keep: false })`.

#### B. Hero Banner Generation (fect-image)

Use `mcp__fect-image__image_text2img` to generate the cover hero image. Read `$CLAUDE_PLUGIN_ROOT/skills/catalog-generator/references/catalog-image-prompts.md` (section "Hero banner") for the prompt and save the result to `images/hero/`.

#### C. Category Visual Generation (fect-image)

If there are 2+ categories, generate a divider image for each category. Use the "Category visual" prompt in `$CLAUDE_PLUGIN_ROOT/skills/catalog-generator/references/catalog-image-prompts.md` and save the results to `images/categories/`.

#### D. Editorial Illustration Generation (fect-image)

Generate mood/atmosphere illustrations placed between categories and in feature sections. These elevate the catalog from a simple product list to an editorial experience.

Read `$CLAUDE_PLUGIN_ROOT/skills/catalog-generator/references/catalog-image-prompts.md` (section "Editorial illustrations") for the 5 illustration types, their placements, and per-type prompts BEFORE generating. Apply the following generation-count rules to decide how many of each to produce, then save the results to `images/illustrations/`:

- Mood separators: 1 per category transition (min 1, max 4)
- Lifestyle scenes: 1 per hero/premium product without existing images
- Detail textures: 1–2 for spec-heavy categories
- Infographic base: 1 if comparison tables exist
- Brand atmosphere: 1 for brand story page (if included)

#### E. Lifestyle Shot Generation (fect-image)

For products with no provided images and no browser screenshots, generate lifestyle images using the "Lifestyle shot" prompt in `$CLAUDE_PLUGIN_ROOT/skills/catalog-generator/references/catalog-image-prompts.md`. Save the results to `images/lifestyle/`.

> **Rule**: Generate only the minimum required images — prioritize browser screenshots over AI generation. For products with both a service URL and AI images, use screenshots for "in action" views and AI images for aspirational lifestyle shots. Skip AI image generation for any product that already has user-provided images.

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
- **Product Screenshot Gallery**: For hero/premium products with browser screenshots, add a responsive screenshot tab component (desktop/tablet/mobile views) inside the product card
- **Detail Texture Backgrounds**: Apply detail texture illustrations as subtle background images for spec/comparison sections

Read `$CLAUDE_PLUGIN_ROOT/skills/catalog-generator/references/catalog-inline-html-blocks.md` (section "Product card HTML") and instantiate the product-card skeleton per product.

> **Note**: The `.product-card__screenshot-gallery` block is only included for hero/premium tier products that have browser screenshots. Omit entirely for products without screenshots. The `.illustration-break` is inserted between logical product groups (e.g., after every 3–4 products or between tier boundaries).

#### D. Screenshot Showcase Page (`pages/{NN}-showcase.html`, when `{SERVICE_URL}` available)

A dedicated "See it in action" page that showcases the product/service through captured screenshots — this is the premium differentiator that builds trust and demonstrates real product quality.

Structure:
1. **Hero section** — Full-width desktop screenshot in browser-chrome frame with headline "See It In Action"
2. **Device showcase** — 3-device mockup display (desktop + tablet + mobile) with perspective tilt
3. **Feature walkthrough** — Sequential screenshot cards showing key user flows. Read `$CLAUDE_PLUGIN_ROOT/skills/catalog-generator/references/catalog-inline-html-blocks.md` (section "Showcase feature-walkthrough step") and instantiate one step per key flow.
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
| Browser Screenshots ({CAPTURE_BACKEND}) | {N} (desktop: {N}, tablet: {N}, mobile: {N}) | Live service capture |
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
