# Video Background Integration — Infinite-Loop Player, CSS, Fallbacks

Operational reference for `/landing-page` Step 4.C. Contains the complete hero markup, the seam-free infinite-loop player, its CSS, the loading strategy, and the no-video CSS hero (Path C).

**Contents**
1. Hero markup template
2. `loop-video.js` — the infinite-loop player (full script)
3. Hero CSS (stage, crossfade, scrim, reduced-motion)
4. Loading strategy (poster-first LCP)
5. Mobile & constrained-context strategy
6. Accessibility checklist
7. Path C — CSS-only animated hero
8. Performance budget & measurement

---

## 1. Hero markup template

```html
<header class="hero">
  <div class="hero__media" data-loop-video
       data-src-desktop="assets/video/hero-desktop.mp4"
       data-src-mobile="assets/video/hero-mobile.mp4"
       data-poster="assets/video/hero-poster.jpg">
    <img class="hero__poster" src="assets/video/hero-poster.jpg" alt=""
         fetchpriority="high" decoding="async">
    <!-- <video> elements are injected here by loop-video.js after window.load -->
  </div>
  <div class="hero__scrim" aria-hidden="true"></div>

  <div class="hero__content">
    <h1 class="hero__title">{benefit-driven headline}</h1>
    <p class="hero__sub">{one-line supporting claim}</p>
    <a class="btn btn--primary" href="#cta">{primary conversion action}</a>
  </div>

  <button class="hero__motion-toggle" data-motion-toggle
          aria-pressed="false" hidden>
    <span data-label-pause>Pause background</span>
    <span data-label-play hidden>Play background</span>
  </button>

  <a class="hero__scroll-cue" href="#section-1" aria-label="Scroll to content"></a>
</header>
```

Rules: the poster `<img>` is real content in the initial HTML (it is the LCP element); the pause button starts `hidden` and is revealed by JS only when videos actually play (WCAG 2.2.2 — a control must exist whenever auto-motion runs > 5 s); videos are decorative → injected with `aria-hidden="true"` and empty-alt poster.

---

## 2. `loop-video.js` — the infinite-loop player

Two stacked `<video>` elements alternate: while A plays its final `CROSSFADE` seconds, B starts from 0 and fades in on top. The decoder-restart gap (the visible "hiccup" of native `loop`) always happens *under* the other, already-playing video — so even a non-bookend clip loops without a visible seam.

```js
/* loop-video.js — seam-free background video loop (no dependencies) */
(function () {
  'use strict';
  var stage = document.querySelector('[data-loop-video]');
  if (!stage) return;

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var conn = navigator.connection || {};
  // Poster-only contexts: user asked for less motion, or data saver is on.
  if (reduced.matches || conn.saveData) return;

  var isMobile = window.matchMedia('(max-width: 768px)').matches;
  var src = isMobile ? (stage.dataset.srcMobile || stage.dataset.srcDesktop)
                     : stage.dataset.srcDesktop;
  if (!src) return;

  var CROSSFADE = 0.5; // s — long enough to hide the decoder restart gap
  // Single source of truth: CSS reads this via var(--video-crossfade)
  stage.style.setProperty('--video-crossfade', CROSSFADE + 's');
  var toggle = document.querySelector('[data-motion-toggle]');
  var videos = [], front = 0, userPaused = false, started = false;

  function makeVideo() {
    var v = document.createElement('video');
    v.muted = true;                 // property AND attribute: iOS checks the attribute
    v.setAttribute('muted', '');
    v.setAttribute('playsinline', '');
    v.setAttribute('aria-hidden', 'true');
    v.loop = false;                 // looping is ours, not the decoder's
    v.preload = 'auto';
    v.src = src;
    v.className = 'hero__video';
    stage.appendChild(v);
    return v;
  }

  function swapIfEnding() {
    var a = videos[front], b = videos[1 - front];
    if (!a.duration || a.currentTime < a.duration - CROSSFADE) return;
    b.currentTime = 0;
    b.play().catch(function () {});
    b.classList.add('is-front');
    a.classList.remove('is-front');
    front = 1 - front;
  }

  function playFront() { videos[front].play().catch(fallbackToPoster); }
  function pauseAll() { videos.forEach(function (v) { v.pause(); }); }

  function fallbackToPoster() {
    // Autoplay rejected (iOS Low Power Mode, browser policy): keep the poster.
    videos.forEach(function (v) { v.remove(); });
    videos = [];
    if (toggle) toggle.hidden = true;
  }

  function start() {
    if (started) return;
    started = true;
    videos = [makeVideo(), makeVideo()];
    videos.forEach(function (v) { v.addEventListener('timeupdate', swapIfEnding); });
    videos[0].classList.add('is-front');
    videos[0].play().then(function () {
      if (toggle) toggle.hidden = false;
    }).catch(fallbackToPoster);
  }

  // Poster-first LCP: begin video work only after the page has fully loaded.
  if (document.readyState === 'complete') start();
  else window.addEventListener('load', start);

  // Pause/play control (WCAG 2.2.2)
  if (toggle) toggle.addEventListener('click', function () {
    userPaused = !userPaused;
    toggle.setAttribute('aria-pressed', String(userPaused));
    toggle.querySelector('[data-label-pause]').hidden = userPaused;
    toggle.querySelector('[data-label-play]').hidden = !userPaused;
    if (userPaused) pauseAll(); else playFront();
  });

  // Lifecycle: hidden tab / off-screen hero → pause (battery, CPU)
  document.addEventListener('visibilitychange', function () {
    if (userPaused || !videos.length) return;
    if (document.hidden) pauseAll(); else playFront();
  });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      if (userPaused || !videos.length) return;
      if (entries[0].isIntersecting) playFront(); else pauseAll();
    }, { threshold: 0.1 }).observe(stage);
  }

  // Reduced-motion switched ON mid-session → tear down to poster.
  // (A session that STARTS reduced never reaches this line — the early return
  // above already kept the page poster-only; re-enabling motion needs a reload.)
  reduced.addEventListener('change', function (e) {
    if (e.matches) { pauseAll(); fallbackToPoster(); }
  });
})();
```

Do not add `autoplay` attributes — playback is always initiated via `play()` so the rejection path is observable.

---

## 3. Hero CSS

```css
.hero { position: relative; min-height: 100svh; display: grid; place-items: center;
        overflow: hidden; }
.hero__media { position: absolute; inset: 0; }
.hero__poster,
.hero__video { position: absolute; inset: 0; width: 100%; height: 100%;
               object-fit: cover; }
.hero__video { opacity: 0; transition: opacity var(--video-crossfade, 0.5s) linear; }
/* duration is set by loop-video.js from its CROSSFADE constant — single SSoT */
.hero__video.is-front { opacity: 1; }

/* Scrim: guarantees text contrast over any video frame */
.hero__scrim { position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(180deg,
    var(--scrim-strong) 0%, var(--scrim-soft) 45%, var(--scrim-strong) 100%); }

.hero__content { position: relative; z-index: 1; text-align: center;
                 padding: var(--space-6) var(--space-4); max-width: 52rem; }

.hero__motion-toggle { position: absolute; z-index: 2;
  bottom: var(--space-4); right: var(--space-4);
  min-width: 44px; min-height: 44px; }

@media (prefers-reduced-motion: reduce) {
  .hero__video { display: none; }        /* CSS backstop for the JS guard */
  .hero__motion-toggle { display: none; }
  .hero__scroll-cue { animation: none; }
}
```

Scrim tokens (`--scrim-strong`/`--scrim-soft`) live in `tokens.css`, tuned so headline contrast against the *brightest* video region stays ≥ 4.5:1 — check against `qa-first.png`, not the average frame.

---

## 4. Loading strategy (poster-first LCP)

1. Initial HTML contains **no `<video>`** — only the poster `<img fetchpriority="high">`. LCP is the poster, independent of video weight.
2. `loop-video.js` loads with `defer`; video elements are created after `window.load`, so video bytes never compete with critical rendering.
3. `hero-poster.jpg` is the *first frame* of the loop (Path A guarantees this), so the poster → video transition is invisible — no flash, no content jump.
4. Below-the-fold imagery uses `loading="lazy"`; the poster must NOT.

---

## 5. Mobile & constrained-context strategy

| Context | Behavior |
|---------|----------|
| Viewport ≤ 768 px | `hero-mobile.mp4` (720 w) selected at injection time |
| `prefers-reduced-motion: reduce` | poster only — videos never created (JS) + `display:none` backstop (CSS) |
| `navigator.connection.saveData` | poster only |
| `play()` rejected (Low Power Mode, policy) | poster only, toggle hidden |
| Orientation change / resize | keep the chosen source — do not hot-swap mid-session (a reload picks up the new bucket) |

The source pick happens once at injection; `<source media>` inside `<video>` is deliberately avoided (its re-evaluation behavior is inconsistent across engines — JS selection is deterministic).

---

## 6. Accessibility checklist

- [ ] Pause/play control visible whenever video plays, ≥ 44×44 px, `aria-pressed` state (WCAG 2.2.2)
- [ ] `prefers-reduced-motion` honored in **both** JS (never inject) and CSS (backstop)
- [ ] Injected videos `aria-hidden="true"`, `muted`, `playsinline`; poster `alt=""` (decorative)
- [ ] Headline/CTA contrast ≥ 4.5:1 over the brightest video frame (scrim-enforced)
- [ ] No content or focus order depends on the video — the page is fully usable poster-only
- [ ] Scroll-reveal animations follow the 3-tier model of `docs/ux/vibe-coding-animation-guide.md` §15

---

## 7. Path C — CSS-only animated hero

When Veo is unavailable or `--no-video`: an animated gradient + grain hero that follows the same motion vocabulary. Keep the identical markup minus `data-loop-video` (no JS, no pause button needed if total looping motion is subtle *and* `prefers-reduced-motion` freezes it — when motion is prominent, keep the toggle and flip a `data-paused` attribute).

```css
.hero--css {
  background:
    radial-gradient(120% 90% at 80% 10%, var(--hero-glow-1), transparent 60%),
    radial-gradient(100% 80% at 15% 85%, var(--hero-glow-2), transparent 55%),
    var(--surface-hero);
  background-size: 200% 200%, 180% 180%, auto;
  animation: hero-drift 24s ease-in-out infinite alternate;
}
@keyframes hero-drift {
  from { background-position: 0% 0%, 100% 100%, 0 0; }
  to   { background-position: 100% 60%, 0% 30%, 0 0; }
}
/* Grain: tiny tiled data-URI noise PNG, opacity ~0.04, mix-blend-mode: overlay */
.hero--css::after { content: ""; position: absolute; inset: 0;
  background-image: var(--noise-tile); opacity: 0.04; mix-blend-mode: overlay; }
@media (prefers-reduced-motion: reduce) { .hero--css { animation: none; } }
```

Enhance per tone with the animation guide's CSS-native techniques (aurora blobs via blurred pseudo-elements, slow `linear()` spring drifts, scroll-driven parallax on decorations). Still counts toward the ≥ 2 distinctive elements only if executed distinctively.

---

## 8. Performance budget & measurement

| Asset | Budget |
|-------|--------|
| `hero-desktop.mp4` | ≤ 4 MB |
| `hero-mobile.mp4` | ≤ 1.5 MB |
| `hero-poster.jpg` | ≤ 200 KB |
| CSS total | ≤ 60 KB |
| JS total | ≤ 10 KB (no frameworks, no animation libraries by default) |
| Fonts | ≤ 2 families, `woff2`, `font-display: swap` |

Measurement during Step 5: `du -k` the asset tree; confirm the poster renders before any `<video>` exists, then assert playback **only in a visible tab**. A Lighthouse pass (Chrome MCP `lighthouse_audit`) is the optional deep check — per the browser backend policy, performance auditing is a documented escalation from ego to Chrome MCP.

**Execution-verified reference values** (this exact player + a 3 s clip, served over HTTP, Chromium visible tab) — use them as the expected shape of a passing smoke test:

| Assertion | Measured |
|---|---|
| Videos injected after `load` | 2, both `muted` · `playsinline` · `aria-hidden="true"` · `loop === false` |
| Front/back state | front `opacity: 1`, back `opacity: 0`, back `paused: true` |
| Playback engaged | `readyState: 4`, `duration: 3`, front `currentTime: 2.61` |
| Crossfade mid-swap | both videos playing at `t = 2.69` / `0.03`, opacities `0.935` / `0.065`, `is-front` already flipped |
| Pause control | revealed only after `play()` resolves; `127 × 44` px; click → both paused + `aria-pressed="true"` + labels swapped + `currentTime` frozen; second click resumes |
| `prefers-reduced-motion: reduce` | **0 videos injected**, poster visible, control stays hidden, hero renders full-size |
| Viewport 390 × 844 | `hero-mobile.mp4` selected for both elements, no horizontal overflow |
| `--video-crossfade` | `0.5s`, set by the script (single SSoT with the CSS transition) |

> **Do not run the playback assertions under ego.** Its agent Task Spaces are hidden tabs with a frozen paint loop (`visibilityState: "hidden"`, `requestAnimationFrame` firing 0×/2 s), so Chromium never decodes the media: the identical page reports `readyState: 0` / `currentTime: 0` / `duration: 0` indefinitely, with no `video.error` and the mp4 already fetched. That is an artifact of the harness, not a defect in the page — see SKILL.md Step 5.B for the escalation rule.
