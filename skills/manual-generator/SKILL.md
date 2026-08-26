---
name: manual-generator
description: "Generates a professional service manual or help center as a self-contained HTML package under docs/manual/{feature-name}/ from a running service URL and project documents, capturing per-screen screenshots with a real browser (ego default, Chrome MCP fallback). Use when generating a manual, writing a user guide, producing help documentation, or building a help center landing page."
argument-hint: "<service-url> <feature-name|all>"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Task, Agent, Skill, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__click, mcp__chrome-devtools__fill, mcp__chrome-devtools__wait_for, mcp__chrome-devtools__list_pages, mcp__chrome-devtools__select_page, mcp__chrome-devtools__new_page, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__resize_page, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__emulate, mcp__chrome-devtools__hover, mcp__chrome-devtools__fill_form, mcp__chrome-devtools__press_key
---

# ASTRA Service Manual Auto-Generator

> **Korean output style**: for Korean user-facing text (HITL questions, status reports, answers), apply `$CLAUDE_PLUGIN_ROOT/docs/development/korean-style.md` — §"HITL 질문 작성 규칙" and §"답변·보고 원칙". Korean files written to disk are style-checked automatically by the korean-style PostToolUse hook.

Analyzes a running service URL and project documents (blueprints, planner) and generates a **professional online service manual** as a self-contained HTML package.

**Core principles**:
- **Real-browser screenshot capture** — explores the actual service screens and captures step-by-step screenshots automatically (ego (lite) by default, Chrome MCP as fallback)
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
- **JS specs + screenshot annotation injection**: see [references/manual-shared-resources.md](references/manual-shared-resources.md)
- **Browser backend + capture recipe**: see `$CLAUDE_PLUGIN_ROOT/docs/development/browser-backend-policy.md` — detection order, action mapping, ego operating rules, and the shared *Deliverable screenshot capture* sequence

---

## Procedure

### Step 0: Preparation and context collection

#### A. Parse arguments

Inspect `$ARGUMENTS`. The skill requires **both** a service URL and a target feature.

| Argument form | Behavior |
|---------------|----------|
| `<url> <feature-name\|all>` (two positional tokens — order-insensitive: a token starting with `http(s)://` is the URL, the other is the feature) | Use both directly |
| Only one token (URL only OR feature only) | Ask for the missing token via `AskUserQuestion` |
| _(none)_ | Ask for both via `AskUserQuestion` |

When asking, use two separate questions (do not bundle into one free-text prompt):

```
Q1. Service URL (required) — URL of the running service for screenshot capture
    Example: http://localhost:3000

Q2. Documentation target (required) — feature scope
    Options: <feature-name listed from docs/blueprints> | "all"
```

Extract `{SERVICE_URL}` and `{TARGET_FEATURE}` from the input. Both are mandatory at the **input-collection** layer — Step 0.C still allows a runtime fallback to document-only mode if the URL is unreachable (network-level recovery, not user choice).

#### B. Load project context

1. Read `CLAUDE.md` — project name, tech stack, language setting (apply LANGUAGE RULE)
2. Scan `docs/blueprints/` — collect the list of per-feature blueprints
3. Scan `docs/planner/` — collect the list of planner deliverables
4. Scan `ux/` — check for existing UX prototypes (reference routes / screens)
5. Verify the existence of `src/styles/design-tokens.css`

> **Validation**: if `src/styles/design-tokens.css` is missing, notify the user:
> "Design tokens file not found. Please initialize the project first with `/project-init`."
> Even if the file is missing, the default tokens at `$CLAUDE_PLUGIN_ROOT/skills/project-init/templates/design-tokens.css` can be used as a fallback.

#### C. Resolve the browser backend, then verify URL accessibility

Resolve `CAPTURE_BACKEND` per the plugin-wide detection order — **ego (default) →
Chrome MCP (fallback)**; `$ARGUMENTS` may name one explicitly. See the policy doc
(*Detection order*).

```bash
command -v ego-browser >/dev/null 2>&1 && echo ego || echo ""
```

Empty output → `chrome-mcp` when the `mcp__chrome-devtools__*` tools are present.
If neither is available, tell the user (install `ego-browser` or register
`chrome-devtools-mcp`) and continue in document-only mode — a manual with no
screenshots must be labeled as such, never shipped as complete.

URL is **required** at the input layer (Step 0.A), but a runtime accessibility failure (network down, service not started) is allowed to fall back to document-only mode — this is a recovery path, not a user choice:

1. Navigate to the URL (ego: `gotoAndWait` inside the Task Space `astra manual {feature-name}`; Chrome MCP: `navigate_page`)
2. Wait for the page to load (up to 15s)
3. On failure, notify the user and ask whether to:
   - **Retry** (user starts the service, then `/manual-generator` re-runs), or
   - **Proceed as document-only** (manual is generated from blueprints / planner / ux prototypes; Step 3 screenshot capture is skipped)

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
| 4 | Help Center | search-driven landing — hero search + FAQ grid + category cards + banner CTA (see references/manual-html-templates.md §6 and references/manual-css-template.md §5) |
| 5 | Auto | choose automatically based on project traits |

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

When `{SERVICE_URL}` is provided, explore the actual service in the resolved backend:

1. Navigate to the base URL (ego: `gotoAndWait`; Chrome MCP: `navigate_page`)
2. Capture page structure (ego: `snapshotText()`; Chrome MCP: `take_snapshot`)
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

0. **Main-worktree guard**: if called from inside an isolated worktree (`.worktrees/<slug>/`), abort. dev-sync runs only in the main worktree:
   ```bash
   PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(find ~/.claude/plugins/cache -maxdepth 3 -type d -path '*/astra-methodology/*' 2>/dev/null | sort -V | tail -1)}"
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

Read `references/manual-structures.md` (section "Output directory structure") and create the `docs/manual/{feature-name}/` directory tree.

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

Generate these files from the `/frontend-design` output. **Full per-file component specs (and the Help Center §5 assets) live in `references/manual-css-template.md`** — read it when writing each file:

1. **`assets/manual-base.css`** — read-optimized layout (800px content area, 240px sticky collapsible sidebar TOC, 64px header, line-height 1.7, responsive sidebar collapse, `[data-theme="dark"]`)
2. **`assets/manual-components.css`** — manual components: `.step-card`, `.callout-tip/warning/note/danger`, `.screenshot-frame`, `.screenshot-annotation`, `.breadcrumb`, `.chapter-nav`, `.responsive-tabs`, `.toc-sidebar`, `.search-overlay` (search-overlay lives here — no separate file needed)
3. **`assets/manual-print.css`** — print: hide sidebar/header/nav, avoid screenshot page-breaks, print link URLs as text
4. **`assets/manual-helpcenter.css`** — *only when `DESIGN_TONE = Help Center`*: generate from `references/manual-css-template.md` §5 (hero/search, FAQ grid, category cards, banner + contact CTA, footer, dark-mode overrides, inline SVG icon set rocket/gear/handshake/bell/bulb/book). Chapter pages still use base + components; this file extends only `index.html`.

#### E. Generate JavaScript files

Generate `shared/nav.js`, `shared/search.js`, `shared/theme.js`. **Full per-file behavior specs are in `references/manual-shared-resources.md` (§ JavaScript files)** — read it when authoring these. Summary: nav.js = sidebar toggle + chapter prev/next + scrollspy + `←`/`→` nav; search.js = load `search-index.json` + live results + `Ctrl/Cmd+K`; theme.js = dark-mode toggle (localStorage) + font-size A+/A- + `prefers-color-scheme`.

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

Follow the **Deliverable screenshot capture** recipe in the policy doc (navigate → wait → clean UI → annotate → scroll top → capture → remove injected nodes), using the `CAPTURE_BACKEND` column of its Action mapping table. In ego mode all six sub-steps of one screen go in a **single heredoc**, and paths passed to `captureScreenshot` must be **absolute**.

#### A. Per-screen screenshot workflow

For each screen:

1. **Navigate** to `{SERVICE_URL}/{route}`.
2. **Wait** for `{main-content-selector}` (10 s).
3. **Inject highlight + step-number overlay** — add a `.manual-highlight` outline to the target element and a numbered badge at its top-right. **Exact CSS/JS injection snippets and the hardcoding-exception note are in `references/manual-shared-resources.md` (§ Screenshot annotation injection)** — read it before this step. Inject via `js(...)` (ego) or `evaluate_script` (Chrome MCP).
4. **Capture screenshot** → `screenshots/desktop/{chapter}-step-{N}.png`
5. **Remove injected elements** — per `references/manual-shared-resources.md` §3c (remove the class, the `.manual-step-badge`, and the style tag)
6. **Verify the file is non-blank** before counting it done; re-take a blank frame (ego scroll caveat) rather than publishing it.

#### B. Responsive screenshots (when RESPONSIVE_MODE >= 2)

For each screen's main screenshot (first or representative) — ego uses
`cdp('Emulation.setDeviceMetricsOverride', …)`, Chrome MCP uses `resize_page`:

1. **Tablet** (RESPONSIVE_MODE >= 3): 768×1024 → `screenshots/tablet/{chapter}-overview.png`
2. **Mobile** (RESPONSIVE_MODE >= 2): 375×812 → `screenshots/mobile/{chapter}-overview.png`
3. **Restore to desktop**: 1280×800 (ego: `cdp('Emulation.clearDeviceMetricsOverride')`) — a missed restore silently mobile-sizes every later capture.

#### C. Multi-step flow capture

For chapters that include user flows (login, form submit, CRUD, etc.):

1. Capture the starting screen (Step A workflow)
2. Execute the interaction — fill / click / press per the Action mapping table
3. Wait for `{result-indicator}`
4. Capture the next step (repeat Step A workflow)
5. Capture the final result screen

> **Caution**: interact only with test data. Be careful not to modify real data. Capture read-only flows (view, search) first when possible; for write flows (create, update, delete), confirm with the user before proceeding. **In ego mode the browser carries the user's real login session** — never drive a write flow against a production origin.

#### D. Progress report

```
📸 Screenshot capture progress: {completed}/{total} chapters
   - Chapter 01 Getting Started: 3 done
   - Chapter 02 {feature}: {N} done
   - ...
```

**ego only** — once all captures are done, close the Task Space in a final heredoc:
`completeTaskSpace('astra manual {feature-name}', { keep: false })`. Runs on every
exit path, including an aborted run; an un-closed space leaves orphaned windows.

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

Pick the template by `DESIGN_TONE`:

- `Professional Enterprise` / `Refined Minimal` / `Soft & Warm` / `Auto` → **§2 Index (Cover) HTML Template** in `references/manual-html-templates.md` (cover + quick-start callout + search + toc-grid)
- `Help Center` → **§6 Help Center Index Template** in `references/manual-html-templates.md` (sticky header + hero with search + FAQ grid + category cards + banner CTAs + contact CTA + footer). Pull the placeholder values from the project context (Step 0.B): `{PROJECT_NAME}` from `CLAUDE.md`, `{TAGLINE}` from blueprint overview, `{SERVICE_URL}` from Step 0.A. Group chapters into 3–5 categories (Setup / Features / Partners / Notice / Use cases) — the rule table is in the §6 reference. Pick the top 4–6 FAQ entries from Chapter NN-1 (FAQ / Troubleshooting). When `{VIDEO_URL}` / `{CHANGELOG_URL}` / `{SUPPORT_URL}` are not available, omit the corresponding `.banner` / `.cta` blocks rather than leaving empty placeholders.

Key structural elements (cover variant):
- `cover` — project name, manual title, meta info (version / generation date)
- `quick-start-callout` — "First time here?" CTA → link to 01-getting-started.html
- `index-search` — large search input
- `index-toc` > `toc-grid` > `toc-card` — per-chapter cards (number, title, description, meta)

#### B. Generate search-index.json

Scan every chapter to build the search index. Read `references/manual-structures.md` (section "Search index schema") and instantiate `search-index.json` per that schema.

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
