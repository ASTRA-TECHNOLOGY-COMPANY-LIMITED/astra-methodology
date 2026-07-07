# HTML Mockup Templates

Literal skeletons for the Step 6.F HTML mockup set. Instantiate each with `{DESIGN_TONE}`, screen, and persona data. All colors/sizes/spacing must be `var(--*)` tokens (no hardcoding).

## Sections in this file
- Per-screen `SCR-NNN.html` skeleton (Step 6.F.3)
- Screen index `index.html` skeleton (Step 6.F.4)
- `ia-screen-design.md` §7 "HTML mockup preview" block (Step 6.F.5)
- Design system loading & tone decision (Step 6.E)
- Output location tree (Step 6.F.1)
- Shared styles `styles.css` structure (Step 6.F.2)
- Per-screen generation rules (Step 6.F.3)

## Per-screen `SCR-NNN.html` skeleton (Step 6.F.3)

Generate one file per SCR-NNN listed in `ia-screen-design.md` §4/§5:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SCR-NNN — {screen name} | {feature name}</title>
  <!--
    Screen ID: SCR-NNN
    Related UC: UC-XXX
    Related FR: FR-XXX
    Design tone: {DESIGN_TONE}
    Tone rationale: {one-line rationale}
  -->
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <header class="gnb"> ... </header>          <!-- when needed -->
  <aside class="sidebar"> ... </aside>         <!-- when needed -->
  <main class="page-content">
    <!-- implement the UI elements from the wireframe in semantic HTML -->
  </main>
  <footer> ... </footer>                       <!-- when needed -->
  <a href="index.html" class="back-to-index">← All screens</a>
</body>
</html>
```

## Screen index `index.html` skeleton (Step 6.F.4)

Navigation hub showing all SCR-NNN screens at a glance:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{feature name} mockup index</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <header class="page-header">
    <h1>{feature name} mockups</h1>
    <p class="meta">Design tone: {DESIGN_TONE} · Screens: {N} · Authored: {YYYY-MM-DD}</p>
  </header>
  <main class="screen-grid">
    <!-- each screen as a card -->
    <a href="SCR-001.html" class="screen-card">
      <div class="screen-card__id">SCR-001</div>
      <div class="screen-card__title">{screen name}</div>
      <div class="screen-card__type">{type}</div>
      <div class="screen-card__meta">UC-XXX · FR-XXX</div>
    </a>
    ...
  </main>
  <footer class="legend">
    <p>Related docs: <a href="ia-screen-design.md">ia-screen-design.md</a> · <a href="feature-definition.md">feature-definition.md</a></p>
  </footer>
</body>
</html>
```

## `ia-screen-design.md` §7 block (Step 6.F.5)

Append this section to the body of `ia-screen-design.md` (at the end of §6 or as its own section):

```markdown
## 7. HTML mockup preview

Open `index.html` in a browser to visually verify every screen.

| Screen ID | HTML file | Screen name |
|-----------|-----------|-------------|
| SCR-001 | [SCR-001.html](SCR-001.html) | {screen name} |
| SCR-002 | [SCR-002.html](SCR-002.html) | {screen name} |
| ... | ... | ... |

- Design tone: **{DESIGN_TONE}** ({one-line selection rationale})
- Design-token source: `{token path}`
- Responsive: mobile / tablet / desktop
- Dark mode: auto-switch via `prefers-color-scheme`
```

---

## Design system loading & tone decision (Step 6.E)

Read this before generating `styles.css`. It determines where design tokens come from and which `{DESIGN_TONE}` to apply.

##### E.1 Load the design system SSoT

Determine the design-system source in the following priority order (v5.2.0+ DESIGN.md prioritized):

| Priority | Path | Use when | Extract |
|----------|------|----------|---------|
| 1 | `docs/design-system/DESIGN.md` | SSoT exists | Front Matter tokens + Body §1 philosophy + §2 persona + §5 aesthetic_rules |
| 2 | `src/styles/design-tokens.css` | DESIGN.md absent + only CSS exists (legacy project) | CSS variable list |
| 3 | `$CLAUDE_PLUGIN_ROOT/skills/project-init/templates/DESIGN.md` | the project has no design system at all (right after Sprint 0, etc.) | template defaults |

**If DESIGN.md is loaded**: parse the Front Matter YAML to extract available tokens such as `tokens.color.semantic.*`, `tokens.typography.scale`, `tokens.spacing.scale`. Body §5 `aesthetic_rules.forbidden_generic_patterns` is used as an exclusion rule during HTML generation. Body §2 persona is used when deciding the tone of dummy data.

**If only CSS is loaded** (legacy): token extraction is the same but aesthetic_rules / persona info is absent. Print a Recommended note about running `/design-init` for the user, and proceed.

##### E.2 Load component / layout guides (optional)

When DESIGN.md is loaded, Body §4 is the component-spec SSoT (no separate load needed).

Only for legacy projects without DESIGN.md, load the following:

- `docs/design-system/components.md` — specs for buttons / inputs / cards, etc.
- `docs/design-system/layout-grid.md` — grid / breakpoint system

##### E.3 Load the Vibe Coding guides (required)

Load `$CLAUDE_PLUGIN_ROOT/docs/ux/vibe-coding-design-guide.md` (Anti-AI aesthetics, reference anchoring) and `$CLAUDE_PLUGIN_ROOT/docs/ux/vibe-coding-animation-guide.md` (spring easing, micro-interactions). On absence, print a warning and proceed without the guides.

##### E.4 Auto-decide the design tone ({DESIGN_TONE})

**If DESIGN.md exists**: `brand.personality` + `brand.target_persona` in the Front Matter already defines the tone, so skip the separate auto-decision. When generating HTML, apply the DESIGN.md tone as-is.

**If DESIGN.md does not exist**: do not ask the user; synthesize the feature description + market analysis + persona info and auto-select one of the following (`AskUserQuestion` is forbidden). Note the rationale (one line) in an HTML file comment.

| Design tone | Suitable domains |
|-------------|------------------|
| Refined Minimal | SaaS, productivity tools, admin dashboards |
| Bold & Vibrant | consumer apps, marketing, campaign pages |
| Soft & Warm | community, education, healthcare |
| Editorial | content, media, commerce curation |
| Professional Enterprise | B2B, finance, public / enterprise |


---

## Output location tree (Step 6.F.1)

All HTML/CSS files live in `{OUTPUT_DIR}/` alongside the markdown deliverables — no subfolder.

```
{OUTPUT_DIR}/
├── market-analysis.md
├── interview-report.md
├── requirements-definition.md
├── usecase-definition.md
├── ia-screen-design.md
├── feature-definition.md            # generated in Step 7
├── styles.css                       # shared styles (design tokens + components + animation)
├── index.html                       # screen index (navigation hub)
├── SCR-001.html                     # per-screen static HTML mockup
├── SCR-002.html
└── ...
```

---

## Shared styles `styles.css` structure (Step 6.F.2)

Generate `{OUTPUT_DIR}/styles.css` with the following structure:

1. **`:root` design tokens** — define the tokens loaded in Step E.1 as-is (fill missing items with fallback tokens)
2. **Dark-mode token override** — `@media (prefers-color-scheme: dark) :root { ... }`
3. **CSS Reset** — `box-sizing: border-box`, reset margin / padding
4. **Base typography** — body font, heading scale, line-height
5. **Layout utilities** — `.container` (responsive max-width), `.grid-N` (12-column), breakpoints (mobile-first)
6. **Component styles** — styled to match `{DESIGN_TONE}`:
   - `.btn` (primary/secondary/ghost) + hover/focus/active/disabled
   - `.input` + floating label, focus ring
   - `.card` (default/elevated/interactive) + hover lift
   - `.gnb`, `.sidebar`, `.page-layout`
   - `.table`, `.modal`, `.toast`, `.badge`, `.skeleton`
7. **Animation** — spring-easing variables, fadeInUp/shimmer keyframes
8. **Accessibility** — `:focus-visible` focus ring, `prefers-reduced-motion` handling
9. **Print styles** (optional) — `@media print` defaults

---

## Per-screen generation rules (Step 6.F.3)

Generation rules:

| Rule | Content |
|------|---------|
| Semantic HTML | use `header`, `nav`, `main`, `section`, `article`, `aside`, `footer` |
| Design tokens | all colors/sizes/spacing are `var(--*)` only (no hardcoding) |
| Responsive | support mobile (<768px) / tablet (768-1023px) / desktop (≥1024px) |
| Dark mode | auto-supported via the token overrides in styles.css (no extra work) |
| Accessibility | `aria-*` attributes, `alt` text, focus management, sufficient contrast, 44px touch targets |
| Dummy data | natural content using persona names/traits from the interview report |
| Disabled interactions | never write `onclick` on `<button>`/links (static mockup) — use `href="#"` or `disabled` |
| Icons | inline SVG or CSS pseudo-elements. No external font / image dependencies |
| Cross-page navigation | provide a "← All screens" link at top/bottom returning to `index.html` |

