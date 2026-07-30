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

All helpers are **flat global functions** operating on the active tab (per the policy doc's Action mapping — there is no chainable tab object), and waits are in **seconds**.

> **Three execution-verified rules** (measured against live Pinterest on ego lite 0.4.5.8 — each one produced a silently blank deliverable before it was fixed). They are the reason this procedure is split into separate navigate / probe / capture rounds:
>
> 1. **Never navigate and capture in the same round.** A search page can stay *genuinely blank* (white capture, `document.body.innerText.length === 0`, zero pin anchors) for **over a minute** while `openOrReuseTab`/`gotoAndWait` resolve, `waitForElement` succeeds, `document.readyState` reads `"complete"`, and `pageInfo()` reports the right URL. None of those signals prove the page painted.
> 2. **An in-round wait does not help.** `wait(45)` inside the navigating round left the page just as blank; the content appeared only in a *later* round, after idle time between heredocs. So the readiness retry must **end the round and re-probe in a new one** — never loop on `wait()` inside one round.
> 3. **Hide overlays, never `remove()` them.** Pinterest wraps its feed in obfuscated-class divs that match `[data-test-id*="modal"]` / `[role="dialog"]`; `remove()` on that selector deleted the grid's own ancestor and produced a pure-white 14 KB capture. Hide instead, skip any node that *contains* the feed, and re-measure the feed afterwards (measured: 4 overlays hidden, feed height 2681 px → 2681 px, capture 1.8 MB).
> 4. **Neutralize the backdrop too.** The signup nag's scrim is a *separate* full-viewport `rgba(0,0,0,0.6)` layer. Hiding the dialog leaves it, washing every reference dark and biasing the palette analysis in §6 toward false darkness. Making it transparent took the same capture from 1.8 MB to 2.6 MB of true color.

**Round 1 — navigate only** (repeat per query; `REF_DIR` = absolute path of `landing/{slug}/design/references`):

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('astra landing {slug}');
await gotoAndWait('https://kr.pinterest.com/search/pins/?q=dark%20gradient%20hero%20landing%20page', { timeout: 25, settle: 3 });
cliLog('navigated: ' + JSON.stringify(await pageInfo()));
EOF
```

> `gotoAndWait` navigates the *current* tab. `openOrReuseTab` with a new URL opens an **additional** tab each time (verified: 4 queries → 4 tabs), which is harmless but pointless here — use it only for the first tab of the space. Pinterest redirects to a locale host (`www.` → `kr.`); either host works.

**Round 2 — readiness probe.** Its only job is to answer "did it paint?". If not, end the round and re-run this same probe as a new round (up to 6 attempts, i.e. ~2 min of wall time; do other work between attempts rather than sleeping):

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('astra landing {slug}');
const p = await js(String.raw`(() => JSON.stringify({
  pins: document.querySelectorAll('a[href^="/pin/"]').length,
  bodyLen: document.body.innerText.length,
  imgs: [...document.images].filter(i => i.complete && i.naturalWidth > 0).length
}))()`);
cliLog('READY_PROBE: ' + p);
EOF
```

Treat `bodyLen > 0 && pins > 0 && imgs > 0` as READY. Anything else = NOT READY → new round, probe again. After the attempt budget is exhausted, stop fighting it and fall through to §5's sibling galleries — **never capture a NOT-READY page**.

**Round 3 — sweep, verify, capture, extract** (only once the probe returned READY):

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('astra landing {slug}');
// Hide overlay nags + neutralize the scrim WITHOUT deleting the feed's own
// ancestors, then re-measure to prove the feed survived.
const swept = await js(String.raw`(() => {
  const feed = document.querySelector('[data-test-id="search-feed"], div[role="list"]');
  const before = feed ? Math.round(feed.getBoundingClientRect().height) : 0;
  const safe = el => feed && el !== feed && !el.contains(feed);   // never touch a feed ancestor
  let hidden = 0, unscrimmed = 0;
  document.querySelectorAll('[data-test-id*="modal"], [data-test-id*="signup"], [role="dialog"]').forEach(el => {
    if (!safe(el)) return;
    el.style.setProperty('display', 'none', 'important');
    hidden++;
  });
  // The signup nag's backdrop is a separate full-viewport translucent layer —
  // left in place it washes the whole capture dark and biases palette analysis.
  const vw = innerWidth, vh = innerHeight;
  document.querySelectorAll('body *').forEach(el => {
    if (!safe(el)) return;
    const cs = getComputedStyle(el);
    if (cs.position !== 'fixed' && cs.position !== 'absolute') return;
    const r = el.getBoundingClientRect();
    if (r.width < vw * 0.9 || r.height < vh * 0.9) return;         // must cover the viewport
    const m = (cs.backgroundColor || '').match(/rgba?\(([^)]+)\)/);
    const alpha = m ? parseFloat((m[1].split(',')[3] || '1').trim()) : 0;
    if (alpha > 0 && alpha < 1) {                                  // translucent scrim only
      el.style.setProperty('background-color', 'transparent', 'important');
      unscrimmed++;
    }
  });
  window.scrollTo(0, 0);                                           // blank-frame guard
  const after = feed ? Math.round(feed.getBoundingClientRect().height) : 0;
  return JSON.stringify({ before, hidden, unscrimmed, after, feedSurvived: after > 200 });
})()`);
cliLog('SWEEP: ' + swept);
if (!JSON.parse(swept).feedSurvived) {
  cliLog('ABORT: sweep collapsed the feed — do not capture this frame');
} else {
  cliLog('capture: ' + await captureScreenshot('{REF_DIR}/ref-01-grid.png'));
  // Pin IDs come from a DOM query — NOT from snapshotText() (see below).
  cliLog('PINS: ' + await js(String.raw`(() => JSON.stringify(
    [...document.querySelectorAll('a[href^="/pin/"]')]
      .map(a => a.getAttribute('href'))
      .filter((h, i, arr) => arr.indexOf(h) === i).slice(0, 5)
  ))()`));
}
EOF
```

Then open the 1–2 most relevant pins in their own **navigate → probe → capture** rounds (same three-round shape; pin detail pages show the animation larger and often autoplay GIF/video pins), waiting on `[data-test-id="pin-closeup-image"], main` and writing `ref-02-closeup.png`.

**Pin IDs**: use the `js()` DOM query above. `snapshotText()` is *not* a substitute — on a grid holding 44 pin anchors it yielded **zero** `/pin/{id}/` matches (it returns an accessibility-style outline with `[ref=N, loc=…]`, not raw hrefs). `@N` refs also expire with the snapshot, so across rounds always navigate by URL.

After the final query round, close the space:

```bash
ego-browser nodejs <<'EOF'
await completeTaskSpace('astra landing {slug}', { keep: false });
cliLog('task space closed');
EOF
```

**Verify every capture — size is the cheap tell.** `[ -s … ]` is not enough: a blank white 2560×1410 PNG still weighs ~14 KB, while a real Pinterest grid capture measured 0.7–1.0 MB. Check the byte size and `Read` the PNG before putting it on the board:

```bash
for f in {REF_DIR}/ref-*.png; do
  KB=$(du -k "$f" | cut -f1)
  [ "$KB" -lt 60 ] && echo "SUSPECT (likely blank, ${KB}KB): $f" || echo "ok (${KB}KB): $f"
done
```

A suspect frame has exactly three causes, in order of likelihood: the page had not painted (§2 rule 1 — re-probe in a new round), the sweep collapsed the feed (§2 rule 3 — the `feedSurvived` guard should have caught it), or `scrollY != 0` (the policy doc's blank-frame caveat). Retake; never place a blank capture on the board and never count it in the reference total.

---

## 3. Capture procedure — Chrome MCP (fallback)

Same flow with MCP tools: `new_page` (own tab per session) → `navigate_page` to the search URL → `wait_for` the grid → `evaluate_script` with the same modal-dismiss + `scrollTo(0,0)` snippet → `take_screenshot` to the same paths → `take_snapshot` to read pin hrefs → navigate to pin detail pages and repeat. Open pin details in a second tab and `select_page` back to the grid tab between excursions; `close_page` the tabs when the step ends. Use `resize_page` 1280×800 before the first capture for consistent reference framing.

---

## 4. Pinterest-specific handling

- **Signup modal**: appears after the first scroll or a few seconds; §2's Round 3 hide-sweep handles current variants. A logged-out session still renders the full grid *behind* the nag (measured: 42–54 pin anchors, all images loaded, with "로그인/가입하기" text present), so a login prompt is **not** a reason to bail — only a hard full-page gate is. ego's inherited login state usually avoids it entirely; in Chrome MCP with a clean profile, fall back to §5 galleries instead of fighting it.
- **Slow first paint under repeated loads**: after several searches in quick succession, later navigations took over a minute to paint (§2 rule 1). Space the queries out — the readiness probe is what makes this safe, not luck.
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
