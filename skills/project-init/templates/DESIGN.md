---
# ============================================================================
# DESIGN.md — Single Source of Truth for {project-name} Design System
# ----------------------------------------------------------------------------
# This Front Matter is machine-readable. AI agents (Claude Code, Cursor, etc.)
# and codegen scripts read this section. The Markdown Body below explains the
# rationale for humans.
#
# Edit policy:
#   - Hand-edit this file when the design system evolves.
#   - DO NOT hand-edit src/styles/design-tokens.css — it is regenerated from
#     this file via `/design-init --regenerate-css` (or the bundled script).
#   - Bump `meta.version` (SemVer) on any breaking token change.
# ============================================================================

meta:
  name: "{project-name} Design System"
  version: "1.0.0"
  spec: "DESIGN.md (Google Stitch / ASTRA 3-tier)"
  inspired_by:
    - "{reference 1 — e.g., Linear, Vercel, Stripe}"
    - "{reference 2}"
  generated_artifacts:
    - "src/styles/design-tokens.css"

brand:
  philosophy: >
    {Design philosophy expressed in a single sentence.
     e.g., "Calm density — keep information density high while minimizing visual noise."}
  personality:
    - "{keyword 1 — e.g., Trustworthy}"
    - "{keyword 2 — e.g., Efficient}"
    - "{keyword 3 — e.g., Calm}"
  target_persona: >
    {Primary persona in one sentence. e.g., "Enterprise operator — a power user
     who spends 6+ hours per day in the product, favors keyboard shortcuts and
     dense information."}
  voice_tone:
    - "{e.g., Direct, never cheerful}"
    - "{e.g., Specific over generic}"
    - "{e.g., Korean honorific level: hamnida-style (formal)}"

# ============================================================================
# TIER 1 — Primitive Tokens (raw values, never reference directly in components)
# ============================================================================
tokens:
  color:
    space: "oklch"  # perceptually uniform; supports P3 wide gamut
    primitive:
      primary:   # Blue family
        "50":  "oklch(97.0% 0.014 254.6)"
        "100": "oklch(93.2% 0.032 255.6)"
        "200": "oklch(87.0% 0.065 256.0)"
        "300": "oklch(78.5% 0.115 258.5)"
        "400": "oklch(70.7% 0.165 259.4)"
        "500": "oklch(62.3% 0.214 259.8)"
        "600": "oklch(54.6% 0.245 262.9)"
        "700": "oklch(48.8% 0.243 264.4)"
        "800": "oklch(42.4% 0.199 265.6)"
        "900": "oklch(37.9% 0.146 265.5)"
        "950": "oklch(28.2% 0.091 267.9)"
      neutral:   # Zinc family
        "0":    "oklch(100% 0 0)"
        "50":   "oklch(98.5% 0.002 247.8)"
        "100":  "oklch(96.7% 0.003 264.5)"
        "200":  "oklch(92.0% 0.004 286.3)"
        "300":  "oklch(87.1% 0.006 286.3)"
        "400":  "oklch(70.7% 0.015 261.1)"
        "500":  "oklch(55.2% 0.016 285.9)"
        "600":  "oklch(44.2% 0.017 285.8)"
        "700":  "oklch(37.0% 0.013 285.8)"
        "800":  "oklch(27.4% 0.006 286.0)"
        "900":  "oklch(21.0% 0.006 285.9)"
        "950":  "oklch(14.1% 0.005 285.8)"
        "1000": "oklch(0% 0 0)"
      success:   # Emerald
        "50":  "oklch(97.9% 0.021 166.1)"
        "100": "oklch(95.0% 0.052 163.1)"
        "500": "oklch(69.6% 0.170 162.5)"
        "600": "oklch(59.6% 0.145 163.2)"
        "700": "oklch(50.8% 0.118 165.6)"
        "900": "oklch(35.9% 0.074 168.3)"
      warning:   # Amber
        "50":  "oklch(98.7% 0.022 95.3)"
        "100": "oklch(96.2% 0.059 95.3)"
        "500": "oklch(76.9% 0.188 70.1)"
        "600": "oklch(66.6% 0.179 58.3)"
        "700": "oklch(55.5% 0.163 49.0)"
        "900": "oklch(39.7% 0.108 43.6)"
      error:     # Red
        "50":  "oklch(97.1% 0.013 17.4)"
        "100": "oklch(93.6% 0.032 17.7)"
        "500": "oklch(63.7% 0.237 25.3)"
        "600": "oklch(57.7% 0.245 27.3)"
        "700": "oklch(50.5% 0.213 27.5)"
        "900": "oklch(35.8% 0.140 25.7)"

  # ==========================================================================
  # TIER 2 — Semantic Tokens (intent/meaning — theme-switchable)
  # ==========================================================================
    semantic:
      surface:
        base:    "{tokens.color.primitive.neutral.0}"
        raised:  "{tokens.color.primitive.neutral.50}"
        overlay: "{tokens.color.primitive.neutral.100}"
        sunken:  "{tokens.color.primitive.neutral.100}"
        accent:  "{tokens.color.primitive.primary.50}"
      text:
        primary:    "{tokens.color.primitive.neutral.900}"
        secondary:  "{tokens.color.primitive.neutral.500}"
        tertiary:   "{tokens.color.primitive.neutral.400}"
        inverse:    "{tokens.color.primitive.neutral.0}"
        link:       "{tokens.color.primitive.primary.600}"
        link_hover: "{tokens.color.primitive.primary.700}"
      border:
        default: "{tokens.color.primitive.neutral.200}"
        strong:  "{tokens.color.primitive.neutral.300}"
        subtle:  "{tokens.color.primitive.neutral.100}"
        focus:   "{tokens.color.primitive.primary.500}"
      action:
        primary:        "{tokens.color.primitive.primary.600}"
        primary_hover:  "{tokens.color.primitive.primary.700}"
        primary_active: "{tokens.color.primitive.primary.800}"
        primary_text:   "{tokens.color.primitive.neutral.0}"
        secondary:        "{tokens.color.primitive.neutral.100}"
        secondary_hover:  "{tokens.color.primitive.neutral.200}"
        secondary_text:   "{tokens.color.primitive.neutral.900}"
        danger:        "{tokens.color.primitive.error.600}"
        danger_hover:  "{tokens.color.primitive.error.700}"
        danger_text:   "{tokens.color.primitive.neutral.0}"
        ghost_hover:   "{tokens.color.primitive.neutral.100}"
      status:
        success_bg:   "{tokens.color.primitive.success.50}"
        success_icon: "{tokens.color.primitive.success.600}"
        success_text: "{tokens.color.primitive.success.900}"
        warning_bg:   "{tokens.color.primitive.warning.50}"
        warning_icon: "{tokens.color.primitive.warning.600}"
        warning_text: "{tokens.color.primitive.warning.900}"
        error_bg:     "{tokens.color.primitive.error.50}"
        error_icon:   "{tokens.color.primitive.error.600}"
        error_text:   "{tokens.color.primitive.error.900}"
      ring:
        color:  "{tokens.color.primitive.primary.500}"
        width:  "2px"
        offset: "2px"

  # ==========================================================================
  # Typography
  # ==========================================================================
  typography:
    fonts:
      sans:    "'Geist', 'Pretendard Variable', Pretendard, -apple-system, BlinkMacSystemFont, system-ui, sans-serif"
      mono:    "'Geist Mono', 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace"
      heading: "{tokens.typography.fonts.sans}"
    scale:        # Major Third (1.250)
      xs:   "0.75rem"     # 12px
      sm:   "0.875rem"    # 14px
      base: "1rem"        # 16px
      lg:   "1.125rem"    # 18px
      xl:   "1.25rem"     # 20px
      "2xl": "1.5rem"     # 24px
      "3xl": "1.875rem"   # 30px
      "4xl": "2.25rem"    # 36px
      "5xl": "3rem"       # 48px
      "6xl": "3.75rem"    # 60px
    fluid_scale:  # clamp(min, mid, max) — mobile 375 → desktop 1440
      xs:   "clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem)"
      sm:   "clamp(0.875rem, 0.8rem + 0.35vw, 1rem)"
      base: "clamp(1rem, 0.93rem + 0.35vw, 1.125rem)"
      lg:   "clamp(1.125rem, 1rem + 0.65vw, 1.375rem)"
      xl:   "clamp(1.25rem, 1.1rem + 0.75vw, 1.5rem)"
      "2xl": "clamp(1.5rem, 1.2rem + 1.5vw, 2.25rem)"
      "3xl": "clamp(1.875rem, 1.5rem + 1.9vw, 2.75rem)"
      "4xl": "clamp(2.25rem, 1.8rem + 2.25vw, 3.25rem)"
      "5xl": "clamp(3rem, 2.2rem + 4vw, 4.5rem)"
    weight:
      regular:  400
      medium:   500
      semibold: 600
      bold:     700
    line_height:
      none:    1
      tight:   1.25
      snug:    1.375
      normal:  1.5
      relaxed: 1.625
      loose:   1.75
    letter_spacing:
      tighter: "-0.05em"
      tight:   "-0.025em"
      normal:  "0"
      wide:    "0.025em"
      wider:   "0.05em"

  # ==========================================================================
  # Spacing (4px base grid)
  # ==========================================================================
  spacing:
    scale:
      "0":    "0"
      "px":   "1px"
      "0.5":  "0.125rem"   # 2px
      "1":    "0.25rem"    # 4px
      "1.5":  "0.375rem"   # 6px
      "2":    "0.5rem"     # 8px
      "3":    "0.75rem"    # 12px
      "4":    "1rem"       # 16px
      "5":    "1.25rem"    # 20px
      "6":    "1.5rem"     # 24px
      "8":    "2rem"       # 32px
      "10":   "2.5rem"     # 40px
      "12":   "3rem"       # 48px
      "16":   "4rem"       # 64px
      "20":   "5rem"       # 80px
      "24":   "6rem"       # 96px
      "32":   "8rem"       # 128px

  # ==========================================================================
  # Radius / Border / Shadow
  # ==========================================================================
  radius:
    none: "0"
    sm:   "0.25rem"    # 4px
    md:   "0.375rem"   # 6px
    lg:   "0.5rem"     # 8px
    xl:   "0.75rem"    # 12px
    "2xl": "1rem"       # 16px
    "3xl": "1.5rem"     # 24px
    full: "9999px"
  border_width:
    default: "1px"
    thick:   "2px"
  shadow:
    xs: "0 1px 2px 0 oklch(0% 0 0 / 0.04)"
    sm: "0 1px 3px 0 oklch(0% 0 0 / 0.06), 0 1px 2px -1px oklch(0% 0 0 / 0.06)"
    md: "0 4px 6px -1px oklch(0% 0 0 / 0.07), 0 2px 4px -2px oklch(0% 0 0 / 0.05)"
    lg: "0 10px 15px -3px oklch(0% 0 0 / 0.08), 0 4px 6px -4px oklch(0% 0 0 / 0.04)"
    xl: "0 20px 25px -5px oklch(0% 0 0 / 0.08), 0 8px 10px -6px oklch(0% 0 0 / 0.04)"
    "2xl": "0 25px 50px -12px oklch(0% 0 0 / 0.2)"
    inner: "inset 0 2px 4px 0 oklch(0% 0 0 / 0.04)"

  # ==========================================================================
  # Motion (CSS-native springs via linear())
  # ==========================================================================
  motion:
    duration:
      instant:  "50ms"
      fast:     "100ms"
      normal:   "200ms"
      moderate: "300ms"
      slow:     "500ms"
    easing:
      default:  "cubic-bezier(0.4, 0, 0.2, 1)"
      in:       "cubic-bezier(0.55, 0, 1, 0.45)"
      out:      "cubic-bezier(0, 0.55, 0.45, 1)"
      in_out:   "cubic-bezier(0.65, 0, 0.35, 1)"
      out_back: "cubic-bezier(0.34, 1.56, 0.64, 1)"
    spring:
      gentle: "linear(0, 0.006, 0.025 2.8%, 0.101 6.1%, 0.539 18.9%, 0.721 25.3%, 0.849 31.5%, 0.937 38.1%, 0.968 41.8%, 0.991 45.7%, 1.006 50.1%, 1.015 55%, 1.017 63.9%, 1.001)"
      bouncy: "linear(0, 0.004, 0.016 2.5%, 0.063 5.4%, 0.251 10.6%, 0.561 17.3%, 0.742 21.6%, 0.891 26.4%, 0.976 31%, 1.025 36.2%, 1.05 42.2%, 1.048 49%, 1.029 57.6%, 1.008 68.4%, 0.998 84.8%, 1)"
      snappy: "linear(0, 0.009, 0.037 2.1%, 0.153 4.6%, 0.776 14.3%, 1.001 19.1%, 1.091 23%, 1.111 25.4%, 1.108 28.1%, 1.067 33.7%, 1.009 44.4%, 0.997 53.5%, 1)"

  # ==========================================================================
  # Breakpoints / Z-Index
  # ==========================================================================
  breakpoints:
    mobile:  "640px"
    tablet:  "768px"
    laptop:  "1024px"
    desktop: "1280px"
    wide:    "1536px"
  z_index:
    base:           0
    dropdown:       1000
    sticky:         1020
    fixed:          1030
    modal_backdrop: 1040
    modal:          1050
    popover:        1060
    tooltip:        1070
    toast:          1080
    max:            9999

# ============================================================================
# Accessibility — enforced by design-token-validator
# ============================================================================
accessibility:
  wcag_level: "AA"
  contrast:
    text_normal:     4.5   # WCAG AA
    text_large:      3.0
    interactive_ui:  3.0
  focus_ring:
    visible_always: true
    color:  "{tokens.color.semantic.ring.color}"
    width:  "{tokens.color.semantic.ring.width}"
    offset: "{tokens.color.semantic.ring.offset}"
  touch_target_min: "44px"  # WCAG 2.5.5 Target Size
  motion_levels:
    - "full"      # default
    - "reduced"   # prefers-reduced-motion → no spring/parallax
    - "off"       # essential motion only

# ============================================================================
# Component Registry — details in Body §4
# ============================================================================
components:
  - id: button
    variants: [primary, secondary, danger, ghost, outline]
    sizes: [sm, md, lg]
  - id: input
    variants: [text, email, password, search, number]
    states: [default, hover, focus, error, disabled]
  - id: card
    variants: [default, elevated, outlined, interactive, ghost]
  - id: dialog
    variants: [modal, drawer, popover, sheet]
  - id: nav
    variants: [topbar, sidebar, tabs, breadcrumb]
  - id: form
    variants: [vertical, horizontal, inline]
  - id: feedback
    variants: [toast, banner, inline_alert]

# ============================================================================
# Anti-AI Aesthetic Rules — codified in Body §5
# ============================================================================
aesthetic_rules:
  forbidden_generic_patterns:
    - "purple-to-blue gradient on hero (overused AI-generated cliché)"
    - "centered card with subtle border + drop shadow only"
    - "emoji-only feature icons"
    - "rounded-2xl + p-6 + shadow-md default everywhere"
  required_distinctive_elements:
    - "{project-specific visual element 1 — e.g., serif accent in headings}"
    - "{project-specific visual element 2 — e.g., off-grid asymmetric layout}"
---

# {project-name} Design System

> This document is the single source of truth (SSoT) for the design system.
> The CSS token file `src/styles/design-tokens.css` is auto-generated from this document.
> To change tokens, edit the Front Matter above and run `/design-init --regenerate-css`.

## 1. Design Philosophy — Why This System

{Describe the design philosophy in 2-4 sentences. Example:

> We pursue "quiet density". Keep information density at enterprise SaaS level,
> while minimizing color, shadow, and animation so a power user's eyes do not tire.
> Concentrate visual stimulus only on action triggers (Primary CTA, Status Indicator).
> Every component is keyboard-first; hover-only interaction is forbidden.}

## 2. Brand Identity & Persona

### Primary Persona
{Describe in 4-6 lines: name·role·daily usage time·core pain points·the key hypothesis the design must address.
You may quote the persona section of docs/planner/*/interview-report.md verbatim.}

### Voice & Tone
- **Headlines/CTA**: {e.g., start with a verb — "Start analysis" / "Download report"}
- **Body copy**: {e.g., Korean hamnida-style (formal), English in sentence case}
- **Error messages**: {e.g., the 3-element form — what·why·next action: "Email is not in a valid format. Please enter it as example@domain.com."}

## 3. Visual Language

### Color
- **Why OKLCH**: HSL has perceived lightness that varies by hue. OKLCH is perceptually uniform → the same L value looks like the same brightness. Also supports P3 wide gamut.
- **Primary is one color**: the brand color. Do not use a secondary color as accent (cause of gradient clichés).
- **Neutral 11 steps**: from 0 (white) to 1000 (black). Covers every text/background tonal level.
- **Status (success/warning/error)**: use only with semantic intent. No decorative use.

### Typography
- **Sans-serif default**: Geist + Pretendard (Korean script). Operate a single font family and build hierarchy via weight/size.
- **Fluid scale recommended**: auto-interpolates with viewport size, so separate mobile/tablet/desktop styles are unnecessary.
- **Headings use fluid_scale, body uses static scale** — make headings respond to viewport, keep body fixed for readability.

### Spacing
- **4px base grid**: every spacing is a multiple of 4. No arbitrary values (`13px`, `17px`).
- **fluid_space**: use fluid for large section gaps — compresses on mobile, expands on desktop.

## 4. Component Guidelines

Every component is registered under `components.{id}` in the Front Matter. To add a new component, update both the Front Matter and this section together.

### 4.1 Button

| Variant | Background | Text | Border | Hover |
|---------|-----------|------|--------|-------|
| Primary | `action.primary` | `action.primary_text` | none | `action.primary_hover` |
| Secondary | `action.secondary` | `action.secondary_text` | `border.default` | `action.secondary_hover` |
| Danger | `action.danger` | `action.danger_text` | none | `action.danger_hover` |
| Ghost | transparent | `text.link` | none | `action.ghost_hover` |
| Outline | transparent | `text.primary` | `border.strong` | `action.secondary` bg |

| Size | Height | Padding-X | Font Size |
|------|--------|-----------|-----------|
| sm | 32px | `spacing.3` | `typography.scale.sm` |
| md | 40px | `spacing.4` | `typography.scale.base` |
| lg | 44px | `spacing.5` | `typography.scale.lg` |

**States**: hover/active/focus/disabled/loading. The focus state always applies `accessibility.focus_ring`. When loading, fix the width to prevent layout shift.

### 4.2 Input

- Height: 40px (md size), padding-x: `spacing.3`
- Border: `border.default` / focus: `border.focus` + ring / error: `status.error_icon` + ring
- Label: placed above, `typography.scale.sm`, `weight.medium`
- Helper/Error: placed below, `typography.scale.xs`, fade-in with `motion.duration.fast`

### 4.3 Card

- Background: `surface.base`, Border: `border.default`, Radius: `radius.xl`
- Variants: default / elevated (shadow.md → shadow.lg on hover) / outlined / interactive (translateY -2px on hover with `motion.spring.gentle`) / ghost
- Padding: `spacing.6` (mobile: `spacing.4`)

### 4.4 Dialog / Modal

- Backdrop: `surface.overlay` with 40% opacity, `motion.duration.normal` fade
- Container: `surface.base`, `radius.2xl`, `shadow.2xl`, entry with scale + translate using `motion.spring.gentle`
- Width: mobile=`calc(100vw - spacing.8)` / desktop=clamp(320px, 50vw, 640px)

### 4.5 Navigation

- Topbar: 64px height, `surface.base`, `border-bottom: border.subtle`
- Sidebar: 240px width (collapsed: 64px), `surface.raised`
- Active state: `surface.accent` background + `text.link` text

### 4.6 Form / Feedback

- Vertical by default, gap=`spacing.4`
- Toast: top-right, auto-dismiss after 4s, entry with `motion.spring.snappy`
- Inline alert: `status.*_bg` + icon + text

> **Note**: Additional components (Table·Chart·Skeleton, etc.) are appended to this section as the project progresses.

## 5. Anti-AI Aesthetic Rules — Vibe Coding

Rules to avoid the generic look produced by AI coding tools. Codify the anti-AI aesthetics section of `docs/ux/vibe-coding-design-guide.md` for this project's context.

### Forbidden
1. **Purple→Blue gradient hero**: The most common AI cliché. Solid color, or our brand color only.
2. **default rounded-2xl + p-6 + shadow-md everywhere**: Making every card identical erases hierarchy. Vary radius/shadow by hierarchy.
3. **Emoji feature icons**: 🚀🎉⚡ — problems with consistency, accessibility, and cultural differences. Standardize on line icons.
4. **Abstract blob gradients in hero backgrounds**: meaningless decoration. Prefer showing data or real UI captures.
5. **"AI generic" font pairings**: Avoid common combinations like Inter + display sans. Operate the single font family in the Front Matter above.

### Distinctive (Recommended)
- **{project-specific visual element 1}**: {e.g., serif accent on a single heading line}
- **{project-specific visual element 2}**: {e.g., 4px color accent bar on the left of cards}
- **Data-first hero**: real product screenshots/dashboards instead of fake illustrations

### Reference-Anchored Design
When building a new screen, cite a concrete reference instead of abstract descriptions ("modern·clean"):
- "Linear's Issues page list density"
- "Stripe Dashboard's metric card hierarchy"
- "Vercel deploy log's monospace + status indicator combination"

## 6. Animation & Motion

Follow the 12 principles in `docs/ux/vibe-coding-animation-guide.md`. Rules enforced in this project:

- **micro-interactions only**: 150-300ms. Do not exceed 500ms (except for intentional large sequences).
- **spring first**: default to `motion.spring.gentle`. Use `linear()` CSS native (no Framer Motion dependency).
- **3-tier accessibility**:
  - `full`: default
  - `reduced` (`prefers-reduced-motion`): spring → linear, parallax removed, fade only
  - `off`: essential transitions only (loading); everything else 0ms
- **Forbidden**: bouncy spring on hover (fatigue inducer); 3+ looping animations playing simultaneously

## 7. Accessibility (WCAG 2.1 AA)

- **Contrast**: text normal ≥4.5:1, text large ≥3:1, interactive UI ≥3:1 — `design-token-validator` verifies token combinations
- **Focus ring**: always visible on every interactive element. Do not leave `outline: none` alone — apply the token's `focus_ring`
- **Touch target**: minimum 44×44px on mobile (WCAG 2.5.5)
- **Keyboard navigation**: every function is reachable via keyboard. Tab order matches visual order
- **Screen reader**: `aria-label`/`aria-describedby` required. Icon-only buttons add visually hidden text
- **Language**: declare `<html lang="ko">`. Mark inline English with `<span lang="en">`

## 8. Token-to-CSS Generation

When this file changes, regenerate the CSS token file with the following command:

```bash
# Invoke the Claude Code skill
/design-init --regenerate-css
```

Generation target: `src/styles/design-tokens.css`
Transformation rules:
- `tokens.color.primitive.primary.50` → `--primitive-primary-50`
- `tokens.color.semantic.surface.base` → `--surface-base`
- `tokens.typography.scale.base` → `--text-base`
- `{tokens.x.y.z}` reference → `var(--{x}-{y}-{z})` (kebab-case)

If you hand-edit `design-tokens.css`, the next `/design-init --regenerate-css` will overwrite it. To add tokens, edit this file's Front Matter.

## 9. Evolution Log

| Version | Date | Change | Rationale |
|---------|------|--------|-----------|
| 1.0.0 | {YYYY-MM-DD} | Initial DESIGN.md | Sprint 0 |
| | | | |

---

**Maintainer**: DSA (Design System Architect)
**Related**:
- `src/styles/design-tokens.css` (generated)
- `docs/ux/vibe-coding-design-guide.md`
- `docs/ux/vibe-coding-animation-guide.md`
- `docs/ux/mobile-design-guide.md`
