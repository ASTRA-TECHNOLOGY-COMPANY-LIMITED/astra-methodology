---
name: manual-generator
description: "Automatically generates a professional online service manual from a running service URL and project documents. Captures per-screen screenshots via Chrome MCP, extracts feature descriptions from blueprints / planner documents, and publishes step-by-step guides as an HTML package. Use when generating a manual, writing a user guide, or producing help documentation."
argument-hint: "[target URL or feature name]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Agent, Skill, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__click, mcp__chrome-devtools__fill, mcp__chrome-devtools__wait_for, mcp__chrome-devtools__list_pages, mcp__chrome-devtools__select_page, mcp__chrome-devtools__new_page, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__resize_page, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__emulate, mcp__chrome-devtools__hover, mcp__chrome-devtools__fill_form, mcp__chrome-devtools__press_key
---

# ASTRA Service Manual Auto-Generator

Analyzes a running service URL and project documents (blueprints, planner) and generates a **professional online service manual** as a self-contained HTML package.

**Core principles**:
- **Chrome MCP screenshot capture** — explores the actual service screens and captures step-by-step screenshots automatically
- **Screenshot annotation automation** — CSS injection highlights UI elements + overlays step numbers
- **Integration with the `/frontend-design` skill** — production-grade, refined and readable manual design
- **Expert-level writing** — second-person polite form, plain language, step-by-step format
- References the project's `src/styles/design-tokens.css` (no hardcoding)
- Supports dark mode, client-side search, responsive layout, and print styles
- Opens directly in a browser (no separate build needed)

**Output location**: `docs/manual/{feature-name}/`

**Writing-quality criteria**:
- Clear step-by-step guidance that even non-technical users can follow
- Attach a screenshot to every step (67% higher comprehension — TechSmith research)
- Consistent tone, plain language without jargon
- Highlight key info with Tip / Caution / Warning boxes

> **🌐 LANGUAGE RULE**: Before executing this skill, read the project's `CLAUDE.md` and check the `## Language` section to detect the project language. If the project language is NOT Korean (`ko`), you MUST translate ALL user-facing output — including HTML page titles, labels, chapter titles, step descriptions, callout text — into the project language. Technical identifiers (file paths, CSS variable names, class names) remain untranslated. If no `CLAUDE.md` exists or no `## Language` section is found, default to Korean.

## Additional resources

- **Writing principles / style rules**: see [references/manual-writing-guide.md](references/manual-writing-guide.md)
- **CSS component templates**: see [references/manual-css-template.md](references/manual-css-template.md)
- **HTML structure templates**: see [references/manual-html-templates.md](references/manual-html-templates.md) (chapter, index, FAQ, glossary)

---

## Procedure

### Step 0: Preparation and context collection

#### A. Parse arguments

Inspect `$ARGUMENTS`:

| Argument form | Behavior |
|---------------|----------|
| URL (starts with `http://` or `https://`) | Use the URL as the target service |
| Feature-name string (e.g., `auth`, `payment`) | Search for documents and URLs related to the feature |
| URL + feature name (e.g., `http://localhost:3000 auth`) | Use both the URL and the feature scope |
| _(none)_ | Ask for the target via `AskUserQuestion` |

If no arguments are provided, ask:

```
## Generate service manual

Please provide the target service information.

1. **Service URL** (optional): URL of the running service (e.g., http://localhost:3000)
   → If a URL is provided, real screen screenshots will be captured.
   → If no URL is provided, the manual will be generated from documents only.

2. **Documentation target**: the feature to document (e.g., "auth feature", "payment system", "all")

Input:
```

Extract `{SERVICE_URL}` and `{TARGET_FEATURE}` from the user's input.

#### B. Load project context

1. Read `CLAUDE.md` — project name, tech stack, language setting (apply LANGUAGE RULE)
2. Scan `docs/blueprints/` — collect the list of per-feature blueprints
3. Scan `docs/planner/` — collect the list of planner deliverables
4. Scan `ux/` — check for existing UX prototypes (reference routes / screens)
5. Verify the existence of `src/styles/design-tokens.css`

> **Validation**: if `src/styles/design-tokens.css` is missing, notify the user:
> "Design tokens file not found. Please initialize the project first with `/project-init`."
> Even if the file is missing, the default tokens at `$CLAUDE_PLUGIN_ROOT/skills/project-init/templates/design-tokens.css` can be used as a fallback.

#### C. Verify URL accessibility

When `{SERVICE_URL}` is provided:

1. Navigate to the URL via `mcp__chrome-devtools__navigate_page`
2. Wait for the page to load via `mcp__chrome-devtools__wait_for` (up to 15s)
3. On failure, notify the user and switch to document-based mode:
   "Cannot access the service. Please verify the service is running. Generate the manual from documents only?"

#### D. Analyze document sources

Read the following documents and build a feature map:

| Source | Path | Extracted info |
|--------|------|----------------|
| Blueprint | `docs/blueprints/{NNN}-*/blueprint.md` | feature design, API endpoints, user stories |
| Feature definition | `docs/planner/{NNN}-*/feature-definition.md` | feature structure, sub-feature detail, service policy |
| IA / screen design | `docs/planner/{NNN}-*/ia-screen-design.md` | IA structure, screen list, screen flow |
| Use case | `docs/planner/{NNN}-*/usecase-definition.md` | user flow, alternative flow, exception flow |
| UX prototype | `ux/*/index.html` | screen index, route structure |

If `{TARGET_FEATURE}` is not "all", filter only the documents related to that feature.

#### E. Choose manual settings

Use `AskUserQuestion` to choose manual-generation options:

```
## Manual generation settings

### 1. Manual scope
Select the features to document.

| # | Feature | Source | Screen count |
|---|---------|--------|--------------|
| 1 | {feature-1} | {blueprint + URL / blueprint only / planner only} | {N} |
| 2 | {feature-2} | {source} | {N} |
| ... | ... | ... | ... |

Select (all: all, partial: 1,3):

### 2. Language
| # | Language |
|---|----------|
| 1 | Korean |
| 2 | English |
| 3 | Auto (per CLAUDE.md) |

### 3. Design tone
| # | Tone | Description |
|---|------|-------------|
| 1 | Professional Enterprise | stable, trustworthy enterprise docs |
| 2 | Refined Minimal | clean, refined minimal docs |
| 3 | Soft & Warm | soft, friendly help-doc style |
| 4 | Auto | choose automatically based on project traits |

### 4. Responsive screenshots
| # | Option |
|---|--------|
| 1 | Desktop only |
| 2 | Desktop + Mobile |
| 3 | Desktop + Tablet + Mobile |
```

Save the selections as `{SELECTED_FEATURES}`, `{LANGUAGE}`, `{DESIGN_TONE}`, `{RESPONSIVE_MODE}`.

---

### Step 1: Analyze the target service and design the table of contents

#### A. Build the feature map

Analyze the documents collected in Step 0 to extract per feature:

| Item | Source |
|------|--------|
| Feature name / description | blueprint.md → overview section |
| Screen list | ia-screen-design.md → screen list table |
| User flow | usecase-definition.md → base flow / alternative flow |
| API endpoints | blueprint.md → API design section |
| Business rules | feature-definition.md → service policy |
| Screen flow diagram | ia-screen-design.md → screen-transition diagram |

#### B. Explore the service (when URL is provided)

When `{SERVICE_URL}` is provided, explore the actual service via Chrome MCP:

1. Navigate to the base URL via `mcp__chrome-devtools__navigate_page`
2. Capture page structure via `mcp__chrome-devtools__take_snapshot`
3. Analyze the navigation menu / routes and cross-check against the documents' screen list
4. If additional screens not present in documents are discovered, add them to the feature map

#### C. Generate the TOC

Design the manual's table of contents based on the feature map:

```
Chapter-structure rules:
- 01: Getting Started — always first
  - service intro, how to access, system requirements, first login
- 02 ~ NN-2: Per-feature guides — by document order or user-journey order
  - each feature: overview → step-by-step usage → tips / cautions
  - split large features into multiple chapters (e.g., 02-auth-login, 03-auth-signup)
- NN-1: FAQ / Troubleshooting — extracted from alternative / exception flows in usecase
- NN: Glossary (optional) — define project-domain terms
```

#### D. Request TOC approval

Show the TOC and get approval via `AskUserQuestion`:

```
## Confirm manual TOC

The manual will be generated with the following TOC.

| # | Chapter | Contents | Expected screenshot count |
|---|---------|----------|---------------------------|
| 01 | Getting Started | service intro, access, first screen | 3-5 |
| 02 | {feature} — {sub-feature} | {description} | {N} |
| 03 | {feature} — {sub-feature} | {description} | {N} |
| ... | ... | ... | ... |
| {NN-1} | FAQ / Troubleshooting | frequently asked questions, error resolution | 0-3 |
| {NN} | Glossary | definitions of service terms | 0 |

Total {N} chapters, approximately {N} screenshots expected

Proceed as-is? (if changes are needed, describe them):
```

Apply requested changes; when approved, store as `{APPROVED_TOC}` array.

#### E. Switch to the dev branch and sync to latest

Before creating deliverables, switch to `dev` and sync. Do not create a work branch; work directly on `dev`. Work-branch creation is handled automatically when `/pr-merge` runs.

0. **Main-worktree guard**: if called from inside an isolated worktree (`.astra-worktrees/<slug>/`), abort. dev-sync runs only in the main worktree:
   ```bash
   PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
   if [ -z "$PLUGIN_ROOT" ] || [ ! -f "$PLUGIN_ROOT/scripts/worktree-helpers.sh" ]; then
     echo "ERROR: CLAUDE_PLUGIN_ROOT not found. Check the plugin cache path." >&2
     exit 1
   fi
   source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"
   astra_ensure_main_worktree || exit 1
   ```
1. **Check the current branch**: `git branch --show-current`
2. **Skip if already on `dev`**: if the current branch is `dev`, skip steps 3–5 below and just pull (`git pull origin dev`)
3. **Preserve uncommitted changes**: check with `git status --porcelain`; if changes exist, stash temporarily via `git stash --include-untracked` (untracked files included)
4. **Switch to dev and sync**: `git fetch origin dev && git checkout dev && git pull origin dev`
5. **Restore stash**: if you stashed in step 3, restore via `git stash pop`. On conflict, report the conflicting files to the user and request manual resolution.

> **Note**: if the `dev` branch does not exist, work on `main` or `master`. If no default branch exists, work on the current branch.

---

### Step 2: Generate shared resources

#### A. Create directory structure

Create the `docs/manual/{feature-name}/` directory. `{feature-name}` is:
- Single feature: the feature name (e.g., `auth`, `payment`)
- All: the project name or `service-guide`

```
docs/manual/{feature-name}/
├── index.html
├── chapters/
├── assets/
├── screenshots/
│   ├── desktop/
│   ├── tablet/    (when RESPONSIVE_MODE >= 3)
│   └── mobile/    (when RESPONSIVE_MODE >= 2)
└── shared/
```

#### B. Copy design tokens

Copy `src/styles/design-tokens.css` → `docs/manual/{feature-name}/assets/tokens.css` **as-is**.

#### C. Integrate the `/frontend-design` skill

Call the `/frontend-design` skill to generate manual-specific CSS. Pass the following context:

```
Please generate CSS for a documentation/manual.
Design tone: {DESIGN_TONE}
Use case: online service manual (read-optimized)
Required components: sidebar TOC, step-card, callout boxes, screenshot-frame, breadcrumb, chapter-nav, search overlay
Design tokens: reference assets/tokens.css via var()
Dark mode: required
Responsive: mobile / tablet / desktop
```

> If `/frontend-design` is unavailable, use the CSS template at `references/manual-css-template.md` directly.

#### D. Generate CSS files

Generate the following files based on the `/frontend-design` output. Detailed component specs for each CSS file are in `references/manual-css-template.md`:

1. **`assets/manual-base.css`** — read-optimized layout:
   - `max-width: 800px` content area (optimal readability)
   - Left sidebar TOC (240px, collapsible, sticky)
   - 64px top header bar
   - Typography: document-optimized (line-height 1.7, generous paragraph spacing)
   - Responsive: sidebar collapses on tablet, becomes overlay on mobile
   - Dark mode: `[data-theme="dark"]` selector

2. **`assets/manual-components.css`** — manual-specific components:
   - `.step-card` — numbered step card (number circle + content + screenshot)
   - `.callout-tip`, `.callout-warning`, `.callout-note`, `.callout-danger` — info boxes
   - `.screenshot-frame` — mock browser-chrome frame + screenshot image
   - `.screenshot-annotation` — positioned numbered circles (overlay on screenshot)
   - `.breadcrumb` — chapter breadcrumb
   - `.chapter-nav` — previous/next chapter navigation
   - `.responsive-tabs` — desktop/tablet/mobile screenshot tab switching
   - `.toc-sidebar` — sidebar table of contents
   - `.search-overlay` — search modal

3. **`assets/manual-print.css`** — print:
   - Hide sidebar / header / nav
   - Avoid page-breaks in screenshots
   - Print link URLs as text

> **Note**: search-overlay styles are included in `manual-components.css` (no separate file needed).

#### E. Generate JavaScript files

1. **`shared/nav.js`**:
   - Sidebar TOC toggle (mobile: hamburger menu)
   - Chapter prev/next navigation
   - Scrollspy: highlight the section currently being read in the TOC
   - Keyboard navigation: `←` / `→` to move between chapters

2. **`shared/search.js`**:
   - Load `search-index.json`
   - Real-time results when typing a query
   - Click a result to jump to the chapter + section
   - Keyboard: `Ctrl+K` / `Cmd+K` to open search

3. **`shared/theme.js`**:
   - Dark-mode toggle (persisted in `localStorage`)
   - Font-size A+/A- adjustment (3 levels)
   - System theme detection (`prefers-color-scheme`)

#### F. Progress report

```
✅ Shared resources generated
   - CSS: manual-base.css, manual-components.css, manual-print.css
   - JS: nav.js, search.js, theme.js
   - Design tokens: tokens.css
```

---

### Step 3: Screenshot capture

> If `{SERVICE_URL}` is not provided (document-based mode), skip this step and generate the manual without screenshots in Step 4. If UX prototypes exist in the `ux/` directory, you may open those HTML files to capture screenshots.

For each chapter in the approved TOC, capture the required screenshots.

#### A. Per-screen screenshot workflow

For each screen:

1. **Navigate**:
   ```
   mcp__chrome-devtools__navigate_page({ url: "{SERVICE_URL}/{route}" })
   ```

2. **Wait for content to load**:
   ```
   mcp__chrome-devtools__wait_for({ selector: "{main-content-selector}", timeout: 10000 })
   ```

3. **Inject highlight CSS** — use `evaluate_script` to add the `.manual-highlight` class to the target element:
   - Style: `outline: 3px solid #2563EB`, `outline-offset: 2px`, `box-shadow: 0 0 0 6px rgba(37,99,235,0.15)`
   - (Intentional exception: the target service's DOM doesn't have the manual's design tokens, so hardcoding is used. If it clashes with the service's colors, substitute a contrasting color like `#FF3B30`)
   - Inject `<style id="manual-highlight-style">` into head, then `querySelector('{target-selector}').classList.add('manual-highlight')`

4. **Inject step-number overlay** — use `evaluate_script` to add a circular badge at the top-right of the target element:
   - 28x28px blue circle, white text, `z-index: 10001`
   - Compute position via `getBoundingClientRect()`, `position: fixed`

5. **Capture screenshot** — `take_screenshot()` → `screenshots/desktop/{chapter}-step-{N}.png`

6. **Remove injected elements** — use `evaluate_script` to remove the `.manual-highlight` class, the `.manual-step-badge` element, and the style tag

#### B. Responsive screenshots (when RESPONSIVE_MODE >= 2)

For each screen's main screenshot (first or representative):

1. **Tablet** (RESPONSIVE_MODE >= 3):
   ```
   mcp__chrome-devtools__resize_page({ width: 768, height: 1024 })
   ```
   → capture → `screenshots/tablet/{chapter}-overview.png`

2. **Mobile** (RESPONSIVE_MODE >= 2):
   ```
   mcp__chrome-devtools__resize_page({ width: 375, height: 812 })
   ```
   → capture → `screenshots/mobile/{chapter}-overview.png`

3. **Restore to desktop**:
   ```
   mcp__chrome-devtools__resize_page({ width: 1280, height: 800 })
   ```

#### C. Multi-step flow capture

For chapters that include user flows (login, form submit, CRUD, etc.):

1. Capture the starting screen (Step A workflow)
2. Execute the interaction:
   - Input: `mcp__chrome-devtools__fill({ selector: "{input}", value: "{test-data}" })`
   - Click: `mcp__chrome-devtools__click({ selector: "{button}" })`
   - Key press: `mcp__chrome-devtools__press_key({ key: "Enter" })`
3. Wait for result: `mcp__chrome-devtools__wait_for({ selector: "{result-indicator}" })`
4. Capture the next step (repeat Step A workflow)
5. Capture the final result screen

> **Caution**: interact only with test data. Be careful not to modify real data. Capture read-only flows (view, search) first when possible; for write flows (create, update, delete), confirm with the user before proceeding.

#### D. Progress report

```
📸 Screenshot capture progress: {completed}/{total} chapters
   - Chapter 01 Getting Started: 3 done
   - Chapter 02 {feature}: {N} done
   - ...
```

---

### Step 4: Author chapters

Write each chapter from the approved TOC as HTML.

#### A. Writing rules

Read `references/manual-writing-guide.md` and apply the writing rules. Key rules:

| Rule | Application |
|------|-------------|
| Second-person polite form | "Please click the Login button" (O), "Click the Login button" (X — too curt for end-user docs) |
| Plain language | "An auth token is refreshed" (X) → "You stay logged in automatically" (O) |
| Step-by-step format | Split every procedure into numbered steps |
| Visual-first | Use a screenshot when a screenshot is clearer than text |
| Consistent terminology | Use the same name for the same UI element throughout the manual |
| Tip / caution boxes | Optional info uses `.callout-tip`, dangerous actions use `.callout-warning` |

#### B. Chapter HTML structure

Refer to the **chapter HTML template** in `references/manual-html-templates.md` to generate each chapter.

Key structural elements:
- `manual-header` — sticky top header (project name, search / theme / font buttons)
- `toc-sidebar` — left fixed sidebar (links to all chapters)
- `breadcrumb` — navigation path (Manual › Chapter name)
- `chapter` > `steps` > `step-card` — numbered step-by-step guide
- `screenshot-frame` > `screenshot-chrome` + `screenshot-body` — mock browser frame
- `callout-tip/warning/note/danger` — info boxes
- `responsive-preview` > `responsive-tabs` — responsive screenshot tabs (optional)
- `chapter-nav` — previous/next chapter navigation
- `search-overlay` — search modal

#### C. Per-chapter content

**01-getting-started.html** (Getting Started):
- Service introduction (1–2 paragraphs, extracted from the project CLAUDE.md)
- System requirements (browsers, resolution, etc.)
- How to access (URL + screenshot)
- First login / signup flow (step-card)
- Main-screen composition (description of main regions + annotated screenshot)

**02 ~ NN-2: per-feature chapters**:
- Feature overview (extracted from blueprint / feature-definition)
- Step-by-step usage (usecase base flow → step-card)
- Advanced features / settings (optional)
- Caveats (usecase alternative/exception flow → callout-warning)
- Related tips (callout-tip)

**NN-1: FAQ / Troubleshooting**:
- FAQ extracted from usecase exception flows
- Common error situations and resolutions
- Q&A format (`<details><summary>` accordion)

**NN: Glossary** (optional):
- Definitions of technical terms used in the service
- Alphabetical / Hangul order
- Use a `<dl>` definition list

#### D. Progress report (every 2 chapters)

```
📝 Chapter authoring progress: {completed}/{total}
   - ✅ 01 Getting Started
   - ✅ 02 {feature}
   - 🔄 03 {feature} (in progress)
   - ⏳ 04 {feature}
```

---

### Step 5: Generate cover page + TOC index

#### A. Generate index.html

Refer to the **index (cover) HTML template** in `references/manual-html-templates.md` to generate it.

Key structural elements:
- `cover` — project name, manual title, meta info (version / generation date)
- `quick-start-callout` — "First time here?" CTA → link to 01-getting-started.html
- `index-search` — large search input
- `index-toc` > `toc-grid` > `toc-card` — per-chapter cards (number, title, description, meta)

#### B. Generate search-index.json

Scan every chapter to build the search index:

```json
[
  {
    "chapter": "01",
    "title": "Getting Started",
    "url": "chapters/01-getting-started.html",
    "sections": [
      { "heading": "Service introduction", "anchor": "#intro", "content": "..." },
      { "heading": "How to access", "anchor": "#access", "content": "..." }
    ]
  }
]
```

The `content` of each section includes the first 200 characters of the body text (for search matching).

---

### Step 6: Validation and wrap-up

#### A. File-integrity validation

1. Verify every chapter HTML file was generated
2. Verify every screenshot reference matches a real file:
   ```
   Collect every image under screenshots/ via Glob
   Extract <img src=""> from every chapter HTML
   Warn on any unmatched reference
   ```
3. Verify cross-chapter links (prev/next, breadcrumb)
4. Verify every chapter is included in `search-index.json`

#### B. Generation result report

```
## ✅ Manual generation complete

| Item | Value |
|------|-------|
| Location | docs/manual/{feature-name}/ |
| Chapter count | {N} |
| Screenshots | desktop {N}, tablet {N}, mobile {N} |
| Total file count | {N} |
| Total size | {N} MB |

### Open in browser
\`\`\`bash
open docs/manual/{feature-name}/index.html
\`\`\`

### Generated chapters
| # | Chapter | Screenshots |
|---|---------|-------------|
| 01 | Getting Started | {N} |
| 02 | {feature} | {N} |
| ... | ... | ... |
```
