# Manual Shared Resources — JS specs & screenshot annotation injection

Detail moved out of `SKILL.md` Step 2.E and Step 3.A. Read this when generating
the `shared/*.js` files or when injecting screenshot annotations.

## JavaScript files (Step 2.E)

Generate the following three files under `shared/`:

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

## Screenshot annotation injection (Step 3.A)

These are the exact injection specs for the highlight + step-number overlay that
wrap each per-screen `take_screenshot()`. Perform steps 3a/3b before the capture
and step 3c (removal) after.

### 3a. Inject highlight CSS

Use `evaluate_script` to add the `.manual-highlight` class to the target element:

- Style: `outline: 3px solid #2563EB`, `outline-offset: 2px`, `box-shadow: 0 0 0 6px rgba(37,99,235,0.15)`
- (Intentional exception: the target service's DOM doesn't have the manual's design tokens, so hardcoding is used. If it clashes with the service's colors, substitute a contrasting color like `#FF3B30`)
- Inject `<style id="manual-highlight-style">` into head, then `querySelector('{target-selector}').classList.add('manual-highlight')`

### 3b. Inject step-number overlay

Use `evaluate_script` to add a circular badge at the top-right of the target element:

- 28x28px blue circle, white text, `z-index: 10001`
- Compute position via `getBoundingClientRect()`, `position: fixed`

### 3c. Remove injected elements (after capture)

Use `evaluate_script` to remove the `.manual-highlight` class, the
`.manual-step-badge` element, and the `<style id="manual-highlight-style">` tag,
so the next screen starts clean.
