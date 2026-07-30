---
name: landing-page
description: "Builds a premium, reference-driven marketing landing page as a self-contained HTML package — collects animation and layout references from Pinterest with a real browser (ego default, Chrome MCP fallback), synthesizes a reference-anchored design direction, produces a seamless-loop hero background video with Google Veo 3.1, and implements a responsive mobile-first page with an infinite-loop video player, reduced-motion fallbacks, and an adversarial screen-quality convergence pass. Use when the user asks to 'build a landing page', 'make a marketing or promotional page', requests an animated or video hero background, or wants a reference-based premium one-page site."
argument-hint: "[product/brand brief, service URL, or docs/planner path] [--auto] [--no-video] [--refs=<dir>] [--slug=<name>]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Skill, AskUserQuestion, WebSearch, WebFetch, mcp__fect-mcp__veo_text2video, mcp__fect-mcp__veo_img2video, mcp__fect-mcp__veo_extension, mcp__fect-mcp__vision_analyze, mcp__fect-mcp__vision_compare, mcp__fect-image__nanobanana_text2img, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__wait_for, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__resize_page, mcp__chrome-devtools__new_page, mcp__chrome-devtools__select_page, mcp__chrome-devtools__close_page
---

# Reference-Driven Premium Landing Page Builder

Produces a production-grade, self-contained landing page by combining three practices that separate professional work from generic AI output:

1. **Visual references first** — real animation/layout references are collected from Pinterest (and sibling galleries) with a real browser *before* any design decision, then distilled into a reference-anchored design brief (never copied).
2. **AI video as a design material** — the hero background is a **seamless-loop video generated with Google Veo 3.1**, art-directed to the design tokens, post-processed for the web, and played through an infinite-loop script that hides the loop seam.
3. **Convergence, not one-shot** — the finished page passes through the adversarial `screen-quality-loop` before it is reported as done.

**Core principles**:
- **Reference-anchored, never reference-copied** — references contribute *patterns* (layout archetype, motion vocabulary, palette direction); no specific design is reproduced and no third-party asset ships in the deliverable.
- **DESIGN.md is law** — when `docs/design-system/DESIGN.md` exists, its tokens and `aesthetic_rules` override tone defaults derived in Step 0.
- **Graceful degradation at every external dependency** — no Pinterest access, no Veo tools, no ffmpeg, and no browser are all survivable; each fallback is *stated in the final report*, never silently substituted.
- **Cost discipline** — default generation budget is exactly **1 still image + 1 Veo clip** (8 s, `veo-3.1-lite`); anything more requires an explicit user request (the bounded one-time Seam-QA regeneration in `references/veo-loop-video.md` §6 is part of the default budget, not an overage).
- **Motion accessibility is non-negotiable** — `prefers-reduced-motion` fallback, a visible pause control (WCAG 2.2.2), and a poster-first LCP strategy are mandatory, not polish.

**Output location**: `landing/{slug}/` (deliverable) + `landing/{slug}/.work/` (raw clips, stills, QA evidence — never referenced by the page).

> **🌐 LANGUAGE RULE**: Before executing this skill, read the project's `CLAUDE.md` and check the `## Language` section to detect the project language. If the project language is NOT Korean (`ko`), translate ALL user-facing page copy and report output into the project language. Technical identifiers (file paths, CSS variables, class names) remain untranslated. If no `CLAUDE.md` or `## Language` section exists, default to Korean.

---

## Execution Procedure

### Step 0: Intake & Design Tone

#### A. Argument Parsing

| Argument | Action |
|----------|--------|
| Text brief (e.g. `AI bookkeeping SaaS for freelancers`) | Use as the product/brand brief |
| URL | `WebFetch` the page — extract product, audience, existing brand cues |
| `docs/planner/{NNN}-*/` path | Read planner deliverables (personas, KPI, screen designs) as the brief |
| `--refs=<dir>` | Use the user's own reference images from `<dir>`; **skip Step 1 capture** (analysis still runs) |
| `--slug=<name>` | Deliverable directory name; otherwise derive kebab-case from the brand/feature |
| `--no-video` | Skip Veo entirely — hero uses the CSS animated fallback (Path C) |
| `--auto` | Zero HITL — proceed with stated assumptions (for pipeline use) |
| _(empty)_ | Scan `docs/planner/` for the latest package; if none, ask for a one-line brief |

#### B. Ambiguity Check (Think Before Coding — max 1 HITL)

If the brief does not pin down **(1) target audience** and **(2) the single primary conversion action** (sign-up / purchase / contact / download), ask once with interpretation options. Under `--auto`, choose the most probable interpretation and record it under "Assumptions" in the final report. Never ask more than one intake question.

#### C. Design SSoT Load

1. `docs/design-system/DESIGN.md` exists → load tokens + `aesthetic_rules`; the tone table below only fills gaps.
2. Else → derive the design tone from the brief:

| Brand/product signal | Design tone | Hero motion direction |
|----------------------|-------------|-----------------------|
| SaaS / dev tools / AI product | **Dark Gradient Tech** | slow aurora / gradient drift, sparse particle field |
| Luxury / premium goods | **Editorial Luxury** | macro material drift (silk, liquid metal), shallow depth of field |
| Consumer app / lifestyle / wellness | **Soft Ambient** | soft-focus scene, drifting light leaks, gentle parallax |
| Finance / B2B / enterprise | **Confident Minimal** | abstract geometry, slow line & mesh motion, restrained palette |
| Creative studio / event / portfolio | **Bold Kinetic** | high-contrast shapes, sweeping color fields |

3. Load the two UX guides — they govern all aesthetic and motion decisions in Steps 2–4:
   - `$CLAUDE_PLUGIN_ROOT/docs/ux/vibe-coding-design-guide.md` (§4 prompting techniques, §4.1 anti-AI aesthetics, §4.2 reference-anchored prompts)
   - `$CLAUDE_PLUGIN_ROOT/docs/ux/vibe-coding-animation-guide.md` (§15 motion accessibility, §18 AI-generated video backgrounds)

#### D. Main-Worktree Guard & dev Sync

Landing pages are planning-phase deliverables — run in the main worktree on `dev`, like the other dev-sync skills:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(find ~/.claude/plugins/cache -maxdepth 3 -type d -path '*/astra-methodology/*' 2>/dev/null | sort -V | tail -1)}"
if [ -z "$PLUGIN_ROOT" ] || [ ! -f "$PLUGIN_ROOT/scripts/worktree-helpers.sh" ]; then
  echo "ERROR: CLAUDE_PLUGIN_ROOT not found. Check the plugin cache path." >&2; exit 1
fi
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"
astra_ensure_main_worktree || exit 1
```

Then sync `dev` exactly as `/catalog-generator` Step 0.G does (check branch → stash if dirty → `git fetch origin dev && git checkout dev && git pull origin dev` → pop stash; fall back to `main`/`master` when `dev` is absent).

---

### Step 1: Reference Collection (Pinterest)

Collect **6–12 animation/layout references** before designing anything. Full procedure, query recipes, popup handling, and the board template: read `$CLAUDE_PLUGIN_ROOT/skills/landing-page/references/reference-collection.md` BEFORE starting this step.

#### A. Resolve the Browser Backend

Per the plugin-wide order (**ego default → Chrome MCP fallback**; SSoT: `$CLAUDE_PLUGIN_ROOT/docs/development/browser-backend-policy.md`):

```bash
command -v ego-browser >/dev/null 2>&1 && echo ego || echo ""
```

Empty output → `chrome-mcp` when `mcp__chrome-devtools__*` tools are present. Neither available → **capture fallback**: `WebSearch` for current landing-page/animation showcase descriptions (award galleries, motion showcases) and build a text-only reference board; state "reference board: search-derived (no browser)" in the final report.

#### B. Search & Capture

1. Build 4–5 Pinterest search queries from `{tone} + {industry} + medium` (recipes in the reference file).
2. Per query: open `https://www.pinterest.com/search/pins/?q={query}`, dismiss overlay modals, `window.scrollTo(0, 0)` (ego blank-frame guard), capture the result grid, then open the top 1–2 pins and capture their detail views.
3. ego mode: one screen = one heredoc; Task Space `astra landing {slug}`; `captureScreenshot` with **absolute** paths; close with `completeTaskSpace('astra landing {slug}', { keep: false })` when done.
4. Save captures to `landing/{slug}/design/references/ref-{NN}.png`. Pinterest unreachable (login wall persists / network block) → retry the same queries on the sibling galleries listed in the reference file; still nothing → capture fallback of Step 1.A.

#### C. Vision Analysis → Reference Board

For each capture, extract a structured record (analysis prompt in the reference file): layout archetype, hero treatment, **motion vocabulary** (what moves, how slowly, what easing), palette direction, typography character, density, one distinctive detail worth *adapting*. Use `mcp__fect-mcp__vision_analyze` when available; otherwise `Read` each PNG directly (multimodal read).

Write `landing/{slug}/design/reference-board.md` — per-image records + a synthesis section ("what these references agree on"). Verify with `[ -f ]` before claiming the board exists.

**Originality guard**: the board records *patterns*, never instructions to reproduce a specific pin. Reference captures stay in `design/references/` as internal working material — they are never linked from `index.html` and never shipped as page assets.

---

### Step 2: Design Direction Synthesis

Distill the reference board + design tone + DESIGN.md into a **committed design brief** at `landing/{slug}/design/direction.md`, containing exactly these decisions:

1. **Layout archetype** — e.g. full-viewport video hero + alternating feature bands + closing CTA.
2. **Motion vocabulary** — the page-wide motion rules (durations, easings, scroll-reveal style) drawn from the reference board, mapped onto `vibe-coding-animation-guide.md` techniques.
3. **Hero media plan** — Path A/B/C decision (Step 3 table), plus the video's subject, mood, and camera behavior.
4. **Palette + typography** — from DESIGN.md tokens when present; otherwise derived from tone + references (OKLCH values, one display + one body family).
5. **Anti-AI distinctive elements** — at least **2** concrete distinctive choices (per design-guide §4.1 / DESIGN.md `aesthetic_rules`): e.g. asymmetric grid, editorial serif pairing, grain/noise texture, custom scroll indicator, oversized numerals. Generic centered-hero + three-cards + purple-gradient output is a defect, not a baseline.

**HITL (skip under `--auto`)**: present the 5 decisions as a compact summary and ask a single confirm/adjust question. This is the last decision gate — everything after runs unattended.

---

### Step 3: Hero Loop Video Production (Veo 3.1)

Read `$CLAUDE_PLUGIN_ROOT/skills/landing-page/references/veo-loop-video.md` BEFORE this step — it holds the prompt recipes, tool-call templates, and all ffmpeg commands.

#### A. Path Decision

| Condition | Path |
|-----------|------|
| `mcp__fect-mcp__veo_*` present **and** `mcp__fect-image__nanobanana_text2img` present | **A — Bookend loop** (default) |
| `mcp__fect-mcp__veo_*` present, fect-image absent | **B — text2video + crossfade loop** |
| Veo tools absent, or `--no-video` | **C — CSS animated hero** (no video; template in `references/video-integration.md`) |

Tool presence is determined from the session's available tools (the `fect-mcp` server is user-level and not bundled — absence is normal, not an error). Record the chosen path; the final report must state it and, for B/C, why.

#### B. Path A — Bookend Loop (first frame == last frame)

The seamless-loop trick: generate one art-directed still, then have Veo animate it **from that frame back to that frame** — `veo_img2video` with `lastImagePath` set to the *same file* as `sourceImagePath`. The clip's first and last frames are pixel-identical, so it loops without a visible seam, and the still doubles as the LCP poster.

1. **Still**: `mcp__fect-image__nanobanana_text2img` → `landing/{slug}/.work/hero-frame.png` — 16:9, token-matched palette, calm negative space where the headline will sit, **no text, no logos, no faces** (prompt template per tone in the reference file).
2. **Clip**: `mcp__fect-mcp__veo_img2video` — `sourceImagePath` = `lastImagePath` = `hero-frame.png`, `durationSeconds: 8`, `resolution: "1080p"` (1080p requires 8 s), `aspectRatio: "16:9"`, default model (`veo-3.1-lite` — raise to `fast`/full only if the lite output fails Seam QA twice). Prompt = **cyclic ambient motion** that visibly returns to its start (recipes per tone in the reference file; no cuts, no new subjects, no text).
3. **Verify (never claim without it)**: `[ -f ]` the mp4 + `ffprobe` duration ≥ 7 s. Missing/short → regenerate once; still failing → Path B; Veo erroring entirely → Path C.
4. **Seam QA**: extract first + last frames, compare with `mcp__fect-mcp__vision_compare` (or `Read` both). A visible jump → apply the ffmpeg crossfade loop from the reference file on top.

#### C. Path B — text2video + Crossfade Loop

`mcp__fect-mcp__veo_text2video` with the loop-friendly prompt recipe, then make it seamless with the ffmpeg **self-crossfade** (blend the final second into the opening second; command in the reference file). Poster = extracted first frame.

#### D. Post-Production (all video paths)

With ffmpeg (`command -v ffmpeg`): strip audio (`-an` — background video is always muted; Veo's native audio track is dead weight), encode the ladder `hero-desktop.mp4` (1920 w, H.264 CRF 24, `+faststart`) + `hero-mobile.mp4` (720 w, CRF 26), and produce `hero-poster.jpg` (Path A: converted from `hero-frame.png`; Path B: first frame). Outputs land in `landing/{slug}/assets/video/`.

**No ffmpeg** → use the raw Veo mp4 as both variants; the JS crossfade player (Step 4) masks any residual seam. State the missing compression in the final report — do not present the page as size-optimized.

**Budget gate**: `hero-desktop.mp4` ≤ 4 MB, `hero-mobile.mp4` ≤ 1.5 MB, poster ≤ 200 KB (check with `stat -f%z` / `du -k`). Over budget → raise CRF and re-encode before proceeding.

> A 9:16 portrait variant (second Veo generation) is generated **only** on explicit user request — the default mobile strategy is the 720 w downscale + poster-first loading.

---

### Step 4: Page Implementation

Read `$CLAUDE_PLUGIN_ROOT/skills/landing-page/references/video-integration.md` BEFORE this step — it holds the hero markup, the full `loop-video.js` infinite-loop player, the CSS patterns, and the CSS-only fallback hero.

#### A. File Structure

```
landing/{slug}/
├── index.html                  # self-contained entry — no build step
├── assets/
│   ├── css/tokens.css          # design tokens (from DESIGN.md, or generated from direction.md)
│   ├── css/landing.css         # layout + components + motion
│   ├── js/loop-video.js        # seam-free infinite-loop video player
│   ├── video/                  # hero-desktop.mp4 · hero-mobile.mp4 · hero-poster.jpg
│   └── img/                    # section imagery (only what the design needs)
├── design/                     # reference-board.md · direction.md · references/*.png (internal)
└── .work/                      # raw clips, stills, QA screenshots (internal)
```

#### B. Section Architecture

Decide sections from the brief; minimum viable set:

| Section | Rules |
|---------|-------|
| **Hero** (full-viewport video) | H1 states the primary benefit in audience language; single primary CTA; scrim overlay keeping text contrast ≥ 4.5:1 over *every* video frame; visible pause/play control (WCAG 2.2.2); scroll indicator |
| **Social proof strip** | Logos/metrics — only with real data from the brief; never fabricate customers or numbers |
| **Feature/value sections (2–4)** | One benefit per section, alternating layout per the archetype; scroll-reveal per motion vocabulary |
| **Closing CTA** | Repeats the same primary conversion action — one conversion goal per page |
| **Footer** | Contact, minimal legal links |

Copywriting: benefits over features, sensory + specific, scannable (short lines, strong subheads); every CTA is the *same* action.

#### C. Video Integration (the infinite-loop script)

Implement per the reference file:
- **Poster-first LCP**: `index.html` ships only the hero poster (as `<img>`/background) + a `[data-loop-video]` stage; `loop-video.js` injects **two stacked `<video muted playsinline aria-hidden>` elements after `window.load`** and crossfades between them near each clip's end — the decoder restart gap that makes even perfect loops hiccup is hidden under the crossfade.
- **Source pick at runtime**: mobile viewport → `hero-mobile.mp4`; `prefers-reduced-motion: reduce` or `navigator.connection.saveData` → poster only, videos never injected.
- **Autoplay-rejection fallback**: a rejected `play()` promise (iOS Low Power Mode etc.) → poster stays, pause control hides.
- **Lifecycle**: pause when the tab is hidden (`visibilitychange`) and when the hero leaves the viewport (IntersectionObserver).

#### D. Responsive & Motion Implementation

- Mobile-first CSS; breakpoints 768 / 1120 px; fluid type via `clamp()`; touch targets ≥ 44 px.
- Scroll-reveal and micro-interactions implemented with the CSS-native techniques from `vibe-coding-animation-guide.md` (§2 scroll-driven animations, §6 micro-interactions) — no JS animation library for a static landing page unless the motion vocabulary demands it.
- Every animation respects the 3-tier motion-accessibility model (guide §15): full / reduced (opacity-only) / none.
- All colors, spacing, radii, and type sizes come from `tokens.css` — hardcoded values are `design-token-validator` violations.

---

### Step 5: Verification & Convergence

#### A. Static Validation

| Check | Criteria |
|-------|----------|
| Files | `index.html`, 2 CSS, `loop-video.js`, poster + video files (video paths A/B) all exist |
| References | every `src`/`href` in HTML resolves to a real file; nothing references `design/` or `.work/` |
| Video budget | sizes within Step 3.D gate |
| Accessibility | pause control present; `prefers-reduced-motion` blocks in CSS **and** JS; `aria-hidden` on injected videos; scrim contrast tokens |
| Responsive | mobile-first media queries at 768/1120; no horizontal overflow at 375 px |
| Tokens | zero hardcoded colors/fonts/spacing in `landing.css` (spot-check with Grep) |
| Distinctive elements | the ≥ 2 anti-AI elements from `direction.md` are actually implemented |

Fix everything found before proceeding.

#### B. Browser Smoke Test

With the Step 1 backend (skip only if no backend — then state so in the report): open `file://…/landing/{slug}/index.html`, wait for load, then
1. verify the loop player engaged — evaluate `document.querySelectorAll('video').length >= 1 && document.querySelector('video').currentTime > 0` after ~3 s (video paths only);
2. capture desktop (1280×800) and mobile (375×812) screenshots to `landing/{slug}/.work/qa/`, scrolled to top;
3. confirm both screenshots are non-blank before citing them as evidence.

#### C. Adversarial Convergence

Invoke the `screen-quality-loop` skill (Skill tool) on the new page with the full Stage-1 kickoff contract:
- MODE `app` (standalone HTML page in the project tree)
- NEW SCREENS `landing/{slug}/index.html`
- SIBLING BASELINE `none` — a landing page is a standalone deliverable; the verifier falls back to the design SSoT's layout definitions
- DESIGN SSoT PATHS `docs/design-system/DESIGN.md` + `landing/{slug}/assets/css/tokens.css` — the deliverable is self-contained, so its own token file substitutes for `src/styles/design-tokens.css` (mark the latter `[missing]` if the project has none)
- REPORT_DIR `docs/design-system/screen-quality/landing-{slug}/`

The loop drives fixes until **score ≥ 90 AND p0 == 0** or 5 iterations; apply its fix directives in this parent context.

#### D. Final Report

```
## Landing Page Complete — landing/{slug}/

- Brief: {one line} · Primary conversion: {action} · Assumptions: {list or "none"}
- Design tone: {tone} · DESIGN.md: {used / absent}
- References: {N} captured ({Pinterest / sibling gallery / search-derived}) → design/reference-board.md
- Hero media: Path {A|B|C} — {detail; for B/C, why} · Loop seam QA: {pass / crossfade applied}
- Video budget: desktop {N} MB · mobile {N} MB · poster {N} KB {(within budget / over — reason)}
- Distinctive elements: {the ≥2 implemented}
- Accessibility: reduced-motion ✓ · pause control ✓ · contrast ✓
- Screen quality loop: score {N}, p0 {N}, iterations {N}
- Preview: open landing/{slug}/index.html
```

Every fallback taken (no browser, no Pinterest, no Veo, no ffmpeg, skipped smoke test) must appear in this report explicitly.
