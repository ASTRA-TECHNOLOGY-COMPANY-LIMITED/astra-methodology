# Veo 3.1 Seamless-Loop Hero Video — Prompts, Generation, Post-Production

Operational reference for `/landing-page` Step 3. All tool names carry their server prefix; the `fect-mcp` tools are user-level (not bundled with this plugin) — their absence routes to Path B/C per the SKILL.md decision table.

**Contents**
1. Path decision recap
2. First-frame art direction (nanobanana still)
3. Path A — bookend generation (`veo_img2video`)
4. Cyclic-motion prompt recipes per tone
5. Path B — `veo_text2video` + self-crossfade loop
6. Seam QA
7. ffmpeg post-production (strip, encode ladder, poster)
8. Verification gates & budget
9. `veo_extension` note (non-hero use only)

---

## 1. Path decision recap

| Available | Path | Loop mechanism |
|-----------|------|----------------|
| Veo + fect-image | **A** | first frame == last frame (bookend) |
| Veo only | **B** | ffmpeg self-crossfade |
| neither / `--no-video` | **C** | CSS animated hero (`video-integration.md` §7) |

Default generation budget: **1 still + 1 clip**. A failed Seam QA allows exactly one regeneration at a higher model tier before falling through (A → B → C).

---

## 2. First-frame art direction (nanobanana still)

`mcp__fect-image__nanobanana_text2img` → save to `landing/{slug}/.work/hero-frame.png`.

Prompt skeleton (fill from `direction.md` tokens):

```
Wide 16:9 abstract background for a premium landing page hero.
{tone-specific scene, from §4 table}.
Color palette: {2–3 token colors, named plainly, e.g. "deep indigo #1a1040, electric violet accents"}.
Composition: calm, low-detail negative space across the {left third / center} where a headline will sit;
visual interest concentrated {right / lower third}.
No text, no letters, no logos, no people, no faces, no UI elements.
Cinematic lighting, subtle film grain, high dynamic range.
```

Rules:
- **No text/faces/UI** is mandatory — text in generated stills reads as gibberish, faces trigger uncanny artifacts under Veo motion, and fake UI collides with the real page content.
- The negative-space side must match where `direction.md` places the headline.
- Palette drift check: after generation, confirm the still's dominant colors sit within the token palette (visual check is enough); off-palette → regenerate with more explicit color language before ever touching Veo.

---

## 3. Path A — bookend generation

```
mcp__fect-mcp__veo_img2video:
  sourceImagePath: {abs}/landing/{slug}/.work/hero-frame.png
  lastImagePath:   {abs}/landing/{slug}/.work/hero-frame.png   ← same file: this IS the loop trick
  prompt:          {cyclic motion recipe, §4}
  durationSeconds: 8            # 1080p requires 8
  resolution:      "1080p"
  aspectRatio:     "16:9"
  model:           (default veo-3.1-lite-generate-preview)
  outputPath:      {abs}/landing/{slug}/.work
  filename:        hero-raw.mp4
```

Why it works: Veo interpolates first-frame → motion → last-frame. With identical bookend frames, frame 0 and frame N are pixel-identical, so `loop` playback has no visual seam — only the decoder restart gap, which the JS crossfade player hides.

Model escalation: lite → `veo-3.1-fast-generate-preview` only when the lite clip fails Seam QA or shows heavy artifacts; the full model only on explicit user request. Generation is asynchronous (1–6 min) — do not fire parallel speculative generations.

---

## 4. Cyclic-motion prompt recipes per tone

The motion must be **ambient and cyclic** — it drifts away from the start state and visibly returns to it. Forbidden in every recipe: camera cuts, new subjects entering, text appearing, speed ramps, faces, and any one-way motion (a car driving off cannot loop).

| Tone | Prompt core |
|------|-------------|
| Dark Gradient Tech | `Slow aurora-like gradient ribbons drift and breathe across the frame, subtle particle motes float upward and fade, gentle pulsing glow; the motion settles back to its opening state by the end. Static camera. No cuts, no text. Calm, continuous, hypnotic ambient motion.` |
| Editorial Luxury | `Macro fabric/liquid-metal surface undulates in slow motion, soft specular highlights travel across folds and return, shallow depth of field breathes slightly; ends in the exact composition it began. Static camera, no cuts, no text.` |
| Soft Ambient | `Soft out-of-focus light leaks drift diagonally and dissolve, pastel color fields slowly cross-blend and return, faint dust motes float; the scene returns to its opening state. Static camera, dreamy, no cuts, no text.` |
| Confident Minimal | `Thin geometric lines and a sparse wireframe mesh rotate a few degrees and glide back, one soft light sweep crosses and retreats; composition ends where it started. Static camera, precise, restrained, no cuts, no text.` |
| Bold Kinetic | `Large color fields slide past each other in slow sweeping arcs and swing back to their opening positions, hard-edged shapes rotate subtly; high contrast, ends as it began. Static camera, no cuts, no text.` |

Append to every prompt: `Ambient sound only, no music, no voices.` (the audio track is stripped in post, but Veo generates audio natively — keeping it minimal avoids audio-driven motion artifacts).

---

## 5. Path B — `veo_text2video` + self-crossfade loop

```
mcp__fect-mcp__veo_text2video:
  prompt:          {§4 cyclic-motion recipe} + {tone scene description} + {token palette, named plainly}
  durationSeconds: 8            # 1080p requires 8
  resolution:      "1080p"
  aspectRatio:     "16:9"
  model:           (default veo-3.1-lite-generate-preview)
  outputPath:      {abs}/landing/{slug}/.work
  filename:        hero-raw.mp4
```

Then make it loop by blending the tail into the head (output duration = D − F):

```bash
W=landing/{slug}/.work
D=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$W/hero-raw.mp4")
# xfade rejects non-CFR input, and trim+setpts drops the frame-rate metadata
# (it reports 1/0) — so re-assert the source rate with fps= before the fade.
FPS=$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of default=nw=1:nk=1 "$W/hero-raw.mp4")
F=1.0   # crossfade length in seconds — 1.0 masks ambient-motion discontinuity well
OFF=$(awk -v d="$D" -v f="$F" 'BEGIN{printf "%.3f", d - 2*f}')
ffmpeg -y -i "$W/hero-raw.mp4" -filter_complex \
  "[0:v]split[a][b];\
   [a]trim=start=${F},setpts=PTS-STARTPTS,fps=${FPS}[main];\
   [b]trim=duration=${F},setpts=PTS-STARTPTS,fps=${FPS}[head];\
   [main][head]xfade=transition=fade:duration=${F}:offset=${OFF}[v]" \
  -map "[v]" -an -c:v libx264 -pix_fmt yuv420p "$W/hero-loop.mp4"
# Verify before claiming a loop exists: exit code alone is not enough.
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$W/hero-loop.mp4"   # expect D − F
```

How it works: `main` = clip from t=F onward; `head` = the first F seconds; the crossfade lands the final frame on the exact frame where playback restarts. Path A skips this unless Seam QA fails.

> **Verified by execution** (ffmpeg 7.1.1): without the `fps=` filters this command aborts with `The inputs needs to be a constant frame rate; current rate of 1/0 is invalid` and writes no output. With them it exits 0 and produces exactly D − F seconds at the source rate.

Poster for Path B: `ffmpeg -y -i "$W/hero-loop.mp4" -frames:v 1 -q:v 3 "$W/hero-poster-src.png"`.

---

## 6. Seam QA

```bash
W=landing/{slug}/.work
ffmpeg -y -i "$W/{hero-raw|hero-loop}.mp4" -frames:v 1 "$W/qa-first.png"
ffmpeg -y -sseof -0.05 -i "$W/{hero-raw|hero-loop}.mp4" -frames:v 1 "$W/qa-last.png"
```

Compare `qa-first.png` vs `qa-last.png` with `mcp__fect-mcp__vision_compare` (or `Read` both): they must be near-identical in composition, palette, and element positions. Verdict handling:

- **Match** → proceed to §7.
- **Mismatch, Path A** → apply the §5 crossfade on `hero-raw.mp4`; if still visibly jumping, regenerate once at the `fast` model; then fall to Path B behavior (accept crossfaded output).
- **Mismatch, Path B** → increase `F` to 1.5 and re-run the crossfade.

Never skip Seam QA — "loops seamlessly" in the final report must be backed by this comparison.

---

## 7. ffmpeg post-production

```bash
W=landing/{slug}/.work; V=landing/{slug}/assets/video; mkdir -p "$V"
SRC="$W/hero-loop.mp4"; [ -f "$SRC" ] || SRC="$W/hero-raw.mp4"   # Path A without crossfade uses raw

# Desktop: 1920w, strip audio, web-optimized H.264
ffmpeg -y -i "$SRC" -an -vf "scale=1920:-2" -c:v libx264 -crf 24 -preset slow \
  -pix_fmt yuv420p -movflags +faststart "$V/hero-desktop.mp4"
# Mobile: 720w, tighter CRF
ffmpeg -y -i "$SRC" -an -vf "scale=720:-2" -c:v libx264 -crf 26 -preset slow \
  -pix_fmt yuv420p -movflags +faststart "$V/hero-mobile.mp4"
# Poster: Path A → the art-directed still (it IS frame 0); Path B → hero-poster-src.png (§5)
POSTER_SRC="$W/hero-frame.png"; [ -f "$POSTER_SRC" ] || POSTER_SRC="$W/hero-poster-src.png"
ffmpeg -y -i "$POSTER_SRC" -vf "scale=1920:-2" -q:v 4 "$V/hero-poster.jpg"
```

Notes:
- `-an` always — a muted background video with an audio track wastes bytes and can defeat mobile autoplay policies.
- `-pix_fmt yuv420p` + `+faststart` are required for universal browser playback / progressive start.
- Optional second format (`-c:v libvpx-vp9 -crf 34 -b:v 0` → `.webm`) only when the H.264 desktop file cannot meet budget at acceptable quality.

---

## 8. Verification gates & budget

After every generation/encode, before any claim:

```bash
V=landing/{slug}/assets/video
[ -f "$V/hero-desktop.mp4" ] && [ -f "$V/hero-mobile.mp4" ] && [ -f "$V/hero-poster.jpg" ] || echo "MISSING OUTPUT"
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$V/hero-desktop.mp4"   # expect ≥ 6.5
du -k "$V"/hero-desktop.mp4 "$V"/hero-mobile.mp4 "$V"/hero-poster.jpg
```

Budget: desktop ≤ 4096 KB · mobile ≤ 1536 KB · poster ≤ 200 KB. Over → bump CRF by 2 and re-encode (repeat once; still over → reduce scale to 1600w/640w). Report final sizes in the completion report.

No ffmpeg on the machine: copy the raw Veo mp4 to both `hero-desktop.mp4`/`hero-mobile.mp4`, export the poster from the still (Path A) — and state "unoptimized video (ffmpeg absent)" in the report.

---

## 9. `veo_extension` note (non-hero use only)

`mcp__fect-mcp__veo_extension` (+7 s per call, 720p only, lite unsupported) is for long-form ambient sequences in *showcase sections* on explicit user request — never for the hero: extension re-renders at 720p and breaks the bookend identity, destroying the loop. The hero loop is always a single 8 s clip.
