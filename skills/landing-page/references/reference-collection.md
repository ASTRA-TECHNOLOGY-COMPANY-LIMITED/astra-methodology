# Pinterest Reference Collection — Queries, Capture, Analysis, Board

Operational reference for `/landing-page` Step 1. Read top-to-bottom before the first capture.

**Contents**
1. Search query recipes
2. Capture procedure — ego (default)
3. Capture procedure — Chrome MCP (fallback)
4. Pinterest-specific handling (modals, login wall, grid behavior)
5. Sibling galleries (Pinterest-unreachable fallback)
6. Vision analysis prompt & per-image record
7. Reference board template
8. Originality rules

---

## 1. Search query recipes

Compose 4–5 queries as `{tone keyword} + {industry token} + {medium keyword}`. Always include at least one motion-focused query — the point of this collection is *animation* reference, not just layout.

| Design tone | Tone keywords |
|-------------|---------------|
| Dark Gradient Tech | `dark gradient hero`, `glassmorphism dashboard`, `aurora background` |
| Editorial Luxury | `editorial luxury website`, `serif fashion landing`, `macro texture hero` |
| Soft Ambient | `soft pastel app landing`, `wellness website design`, `light gradient ui` |
| Confident Minimal | `minimal fintech landing`, `swiss grid website`, `geometric b2b design` |
| Bold Kinetic | `bold typography website`, `kinetic type landing`, `brutalist web design` |

Medium keywords (rotate across queries): `landing page`, `website animation`, `hero animation`, `motion design web`, `ui animation`.

Example set for a dev-tools SaaS (Dark Gradient Tech):
```
dark gradient hero landing page
developer tools website ui
hero animation website motion design
aurora background web design
award winning saas landing page
```

Search URL form: `https://www.pinterest.com/search/pins/?q={url-encoded query}`

---

## 2. Capture procedure — ego (default)

Rules inherited from the browser backend policy (`docs/development/browser-backend-policy.md`): one screen = **one heredoc**, Task Space `astra landing {slug}`, absolute `captureScreenshot` paths, `window.scrollTo(0, 0)` before every capture (blank-frame guard), `completeTaskSpace` at the end of the step.

Per-query round (repeat per query; `REF_DIR` = absolute path of `landing/{slug}/design/references`):

All helpers are **flat global functions** operating on the active tab (per the policy doc's Action mapping — there is no chainable tab object), and waits are in **seconds**:

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('astra landing {slug}');
await openOrReuseTab('https://www.pinterest.com/search/pins/?q=dark%20gradient%20hero%20landing%20page', { wait: true, timeout: 20 });
await waitForElement('div[role="list"], [data-test-id="search-feed"]');
// Dismiss overlay modals (login/signup nags) — generic sweep — then blank-frame guard
await js(String.raw`(() => {
  document.querySelectorAll('[data-test-id*="modal"], [data-test-id*="signup"], [role="dialog"]')
    .forEach(el => el.remove());
  document.body.style.overflow = 'auto';
  window.scrollTo(0, 0);
  return document.title;
})()`);
cliLog(await captureScreenshot('{REF_DIR}/ref-01-grid.png'));
EOF
```

Then open the 1–2 most relevant pins from that grid in their own round(s) — pin detail pages show the animation at a larger size and often autoplay GIF/video pins:

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('astra landing {slug}');
await openOrReuseTab('https://www.pinterest.com/pin/{pin-id}/', { wait: true, timeout: 20 });
await waitForElement('[data-test-id="pin-closeup-image"], main');
await js(String.raw`(() => { window.scrollTo(0, 0); return true })()`);
cliLog(await captureScreenshot('{REF_DIR}/ref-02-closeup.png'));
EOF
```

Pin IDs: `snapshotText()` in the grid round (or a follow-up round with the same space) and read the anchors — grid anchors have `href="/pin/{id}/"`. `@N` refs expire with the snapshot; across rounds use the URL directly, as above.

After the final query round, close the space:

```bash
ego-browser nodejs <<'EOF'
await completeTaskSpace('astra landing {slug}', { keep: false });
cliLog('task space closed');
EOF
```

**Verify every capture**: `[ -s "{REF_DIR}/ref-NN.png" ]` and visually non-blank (a blank frame means capture happened while scrolled — rescroll to top and retake). Never place a blank capture on the board.

---

## 3. Capture procedure — Chrome MCP (fallback)

Same flow with MCP tools: `new_page` (own tab per session) → `navigate_page` to the search URL → `wait_for` the grid → `evaluate_script` with the same modal-dismiss + `scrollTo(0,0)` snippet → `take_screenshot` to the same paths → `take_snapshot` to read pin hrefs → navigate to pin detail pages and repeat. Open pin details in a second tab and `select_page` back to the grid tab between excursions; `close_page` the tabs when the step ends. Use `resize_page` 1280×800 before the first capture for consistent reference framing.

---

## 4. Pinterest-specific handling

- **Signup modal**: appears after the first scroll or a few seconds; the generic dismiss sweep in §2 handles current variants. If a full-page login wall persists (logged-out hard gate), ego's inherited login state usually avoids it; in Chrome MCP with a clean profile, fall back to §5 galleries instead of fighting it.
- **Infinite grid**: do NOT scroll-and-capture repeatedly — the first two viewports of a well-chosen query beat ten viewports of one query. Prefer more queries over more scrolling (and ego screenshots require `scrollY == 0` anyway).
- **Animated pins**: a static screenshot of a video/GIF pin still captures its composition and palette; note "animated pin — motion inferred from stills" in its record rather than guessing precise motion.
- **Respectful use**: view + screenshot for internal design study only. No scraping beyond the captures, no asset downloads, no automation against logged-in write actions.

---

## 5. Sibling galleries (Pinterest-unreachable fallback)

Retry the same queries, in order, on:

1. `https://dribbble.com/search/{query}` — strongest for UI motion shots
2. `https://www.behance.net/search/projects?search={query}` — long-form case studies
3. `https://www.awwwards.com/websites/?text={query}` — real production sites (best "premium" calibration)

Same capture rules. If no browser backend exists at all — or if Pinterest **and** all three sibling galleries stay unreachable despite a working browser — use `WebSearch` for recent showcase roundups matching the queries and write text-only records (source + described pattern) — mark the board `search-derived`.

---

## 6. Vision analysis prompt & per-image record

Analyze each capture with `mcp__fect-mcp__vision_analyze` (or a direct multimodal `Read`). Prompt template:

```
Analyze this landing page / UI design reference for a design study. Report concisely:
1. Layout archetype (hero structure, grid, section rhythm)
2. Hero treatment (media type, text placement, CTA position)
3. Motion vocabulary — what appears to move or animate, how fast, what easing character
   (if this is a static shot of an animated design, infer conservatively and say so)
4. Palette direction (dominant + accent, light/dark, approximate OKLCH character)
5. Typography character (serif/sans, weight contrast, display vs body relationship)
6. Density & whitespace strategy
7. ONE distinctive detail worth adapting (a pattern, not a copyable asset)
```

Per-image record format (one per capture, in the board):

```markdown
### ref-{NN} — {query it came from}
![ref](references/ref-{NN}.png)
- Layout: …
- Hero: …
- Motion: …
- Palette: …
- Type: …
- Density: …
- Distinctive detail: …
```

---

## 7. Reference board template

`landing/{slug}/design/reference-board.md`:

```markdown
# Reference Board — {slug}

- Source: {Pinterest | Dribbble/Behance/Awwwards | search-derived}
- Queries: {list}
- Captures: {N} (design/references/)

## Records
{per-image records, §6}

## Synthesis — what these references agree on
- Layout consensus: …
- Motion consensus: … (speeds, easing character, what kind of elements move)
- Palette consensus: …
- Typography consensus: …
- Divergences worth exploiting: … (where our page can differ and stand out)

## Carried into direction.md
{3–5 bullet decisions this board directly feeds}
```

The synthesis section is mandatory — a board with records but no synthesis has not done its job.

---

## 8. Originality rules

- References contribute **patterns** (archetypes, motion vocabulary, palette direction, density strategies) — never a 1:1 reproduction of any single reference.
- No third-party image, video, font file, or code from a reference ever ships in `landing/{slug}/assets/`.
- The distinctive-elements requirement (SKILL.md Step 2.5) must be satisfiable by the *synthesis*, not by cloning the single best reference.
- If the user supplies `--refs=<dir>`, treat their images under the same rules — analyze, synthesize, adapt.
