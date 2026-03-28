# Component Style Guide

> DSA customizes this for the project.
> AI references this guide when generating UI.
> All values reference Semantic or Component tokens — never use Primitive tokens directly.

## Token Reference Convention

```
Tier 1 (Primitive):  --primitive-*      → Color/space raw values (NEVER use in components)
Tier 2 (Semantic):   --surface-*, --text-*, --border-*, --action-*, --status-*
Tier 3 (Component):  --btn-*, --card-*, --input-*, --dialog-*, --nav-*
```

---

## 1. Button

### Variants
| Variant | Background | Text | Border | Hover |
|---------|-----------|------|--------|-------|
| Primary | `--action-primary` | `--action-primary-text` | none | `--action-primary-hover` |
| Secondary | `--action-secondary` | `--action-secondary-text` | `--border-default` | `--action-secondary-hover` |
| Danger | `--action-danger` | `--action-danger-text` | none | `--action-danger-hover` |
| Ghost | transparent | `--text-link` | none | `--action-ghost-hover` |
| Outline | transparent | `--text-primary` | `--border-strong` | `--action-secondary` bg |

### Sizes
| Size | Height | Padding-X | Font Size | Icon Size | Radius |
|------|--------|-----------|-----------|-----------|--------|
| sm | `--btn-sm-height` (32px) | `--btn-sm-px` | `--btn-sm-text` | 16px | `--btn-radius` |
| md | `--btn-md-height` (40px) | `--btn-md-px` | `--btn-md-text` | 18px | `--btn-radius` |
| lg | `--btn-lg-height` (44px) | `--btn-lg-px` | `--btn-lg-text` | 20px | `--btn-radius` |

### States
- **Hover**: Background shifts to `-hover` variant, `transition: all var(--duration-fast) var(--ease-out)`
- **Active**: Background shifts to `-active` variant, `scale(0.98)` with `--ease-spring-snappy`
- **Focus**: `outline: var(--ring-width) solid var(--ring-color)`, `outline-offset: var(--ring-offset)`
- **Disabled**: `opacity: 0.5`, `cursor: not-allowed`, `pointer-events: none`
- **Loading**: Spinner + text, `cursor: wait`, button width locked to prevent layout shift

### Icons
- Position: left of text (default), right for forward actions
- Gap: `--space-2` (8px) between icon and text
- Icon-only: Square shape, same height/width as button height

---

## 2. Input Field

### Base Style
- Height: `--input-height` (40px)
- Padding: `--space-2` `--input-px`
- Background: `--input-bg`
- Border: `--border-width-default` `--input-border`
- Radius: `--input-radius`
- Font: `--input-text` `--weight-regular`
- Transition: `border-color var(--duration-fast) var(--ease-out)`

### States
| State | Border | Ring | Background |
|-------|--------|------|------------|
| Default | `--input-border` | none | `--input-bg` |
| Hover | `--border-strong` | none | `--input-bg` |
| Focus | `--input-border-focus` | `--ring-width` `--ring-color` (with offset) | `--input-bg` |
| Error | `--status-error-icon` | `--ring-width` `--status-error-icon` | `--input-bg` |
| Disabled | `--border-subtle` | none | `--surface-sunken`, `opacity: 0.6` |

### Label
- Position: Above the input
- Gap: `--space-1-5` (6px)
- Font: `--text-sm` `--weight-medium` `--text-primary`

### Error & Helper Text
- Font: `--text-xs` `--weight-regular`
- Error: `--status-error-text`
- Helper: `--text-tertiary`
- Gap from input: `--space-1` (4px)
- Transition: `opacity var(--duration-fast)`, slide-up entry

---

## 3. Card

### Base Style
- Background: `--card-bg`
- Border: `--border-width-default` `--card-border`
- Radius: `--card-radius` (12px)
- Shadow: `--card-shadow`
- Padding: `--card-padding`

### Variants
| Variant | Shadow | Border | Hover Effect |
|---------|--------|--------|--------------|
| Default | `--card-shadow` | `--card-border` | None |
| Elevated | `--shadow-md` | none | `--shadow-lg` |
| Outlined | none | `--border-strong` | Border color `--border-focus` |
| Interactive | `--card-shadow` | `--card-border` | `--card-shadow-hover`, `translateY(-2px)` with `--ease-spring-gentle` |
| Ghost | none | none | `--surface-raised` bg |

### Container Query Support
```css
.card-container { container-type: inline-size; }
@container (min-width: 400px) { /* Horizontal card layout */ }
@container (min-width: 600px) { /* Expanded card with sidebar */ }
```

---

## 4. Modal / Dialog

### Base Style
- Backdrop: `--dialog-backdrop`
- Background: `--dialog-bg`
- Radius: `--dialog-radius` (16px)
- Shadow: `--dialog-shadow`
- Padding: `--dialog-padding`

### Sizes
| Size | Width | Use Case |
|------|-------|----------|
| sm | `--dialog-sm-width` (448px) | Confirmations, alerts |
| md | `--dialog-md-width` (512px) | Forms, details |
| lg | `--dialog-lg-width` (640px) | Complex content |
| full | 100vw, 100dvh | Mobile full-screen |

### Structure
```
┌───────────────────────────────────────┐
│ Header (Title + Close)    [X]         │
│ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │
│                                       │
│ Body (Scrollable, max-height: 60vh)   │
│                                       │
│ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │
│ Footer (Actions — right-aligned)      │
└───────────────────────────────────────┘
```

- Header: `--fluid-lg` `--weight-semibold`, padding-bottom `--space-4`
- Dividers: `--border-subtle`
- Footer: gap `--space-3`, padding-top `--space-4`
- Entry: `scale(0.95) → scale(1)` + `opacity: 0 → 1`, `--ease-spring-snappy`, `--duration-normal`
- Exit: `opacity → 0`, `--duration-fast`

---

## 5. Table

### Base Style
- Header: `--surface-raised` bg, `--weight-semibold`, `--text-sm`, `--text-secondary`
- Row: `--surface-base` bg, hover `--surface-raised`
- Cell padding: `--space-3` vertical, `--space-4` horizontal
- Border: bottom only, `--border-subtle`
- Text alignment: Left (text), Right (numbers), Center (status/actions)

### Responsive
- Mobile (<640px): Convert to card layout or horizontal scroll
- Tablet+: Default table layout with sticky header
- Pinned columns: First column sticky on horizontal scroll

---

## 6. Navigation

### GNB (Global Navigation Bar)
- Height: `--nav-height` (56px)
- Background: `--surface-base` with `backdrop-filter: blur(12px) saturate(180%)`
- Bottom border: `--border-subtle`
- z-index: `--z-sticky`
- Layout: Logo (left), Menu (center or left), User actions (right)
- Transition: `background var(--duration-normal)` on scroll

### Sidebar
- Width: `--sidebar-width` (240px), collapsed `--sidebar-width-collapsed` (64px)
- Background: `--sidebar-bg`
- Menu item: height 36px, radius `--radius-md`, padding `--space-2` `--space-3`
- Active: `--surface-accent` bg + `--text-link` text + `--weight-medium`
- Hover: `--action-ghost-hover` bg
- Collapse: `--ease-spring-gentle`, `--duration-moderate`

### Tabs
- Indicator: `--action-primary`, 2px bottom bar, animated position with `--ease-spring-snappy`
- Tab gap: `--space-1`
- Tab padding: `--space-2` `--space-4`
- Inactive: `--text-tertiary` text
- Active: `--text-primary` text, `--weight-medium`

---

## 7. Toast / Notification

### Variants
| Variant | Background | Icon Color | Left Accent |
|---------|-----------|------------|-------------|
| Success | `--status-success-bg` | `--status-success-icon` | `--status-success-icon` (3px left border) |
| Warning | `--status-warning-bg` | `--status-warning-icon` | `--status-warning-icon` |
| Error | `--status-error-bg` | `--status-error-icon` | `--status-error-icon` |
| Info | `--status-info-bg` | `--status-info-icon` | `--status-info-icon` |

### Style
- Radius: `--toast-radius` (12px)
- Shadow: `--toast-shadow`
- Padding: `--toast-padding`
- Max width: 420px
- Position: Top-right (desktop), Top-center (mobile)
- z-index: `--z-toast`

### Animation
- Entry: `translateX(100%) → translateX(0)`, `--ease-spring-bouncy`, `--duration-moderate`
- Auto-dismiss: 5 seconds, progress bar at bottom
- Exit: `opacity → 0`, `translateY(-8px)`, `--duration-fast`

---

## 8. Badge / Tag

### Sizes
| Size | Height | Font | Padding | Radius |
|------|--------|------|---------|--------|
| sm | 20px | `--text-xs` | `--space-1` `--space-2` | `--radius-full` |
| md | 24px | `--text-xs` `--weight-medium` | `--space-1` `--space-2-5` | `--radius-full` |
| lg | 28px | `--text-sm` `--weight-medium` | `--space-1` `--space-3` | `--radius-full` |

### Color Mapping
- Status: Use `--status-*-bg` background + `--status-*-text` text
- Primary: `--surface-accent` bg + `--text-link` text
- Neutral: `--surface-raised` bg + `--text-secondary` text
- Dot indicator: 6px circle before text, color matches variant

---

## 9. Skeleton / Loading

### Base Style
- Background: `--surface-raised`
- Radius: Match the element being loaded (e.g., `--radius-lg` for cards)
- Animation: Shimmer pulse, `--duration-slow` cycle

```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--surface-raised) 25%,
    var(--surface-overlay) 50%,
    var(--surface-raised) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s var(--ease-in-out) infinite;
}
```

### Patterns
- Text: Multiple lines, varying widths (100%, 80%, 60%)
- Avatar: Circle `--radius-full`
- Card: Rectangle with internal line placeholders
- Table: Row-shaped bars with consistent spacing

---

## 10. Avatar

### Sizes
| Size | Dimension | Font (initials) | Icon |
|------|-----------|-----------------|------|
| xs | 24px | `--text-xs` | 14px |
| sm | 32px | `--text-sm` | 16px |
| md | 40px | `--text-base` | 20px |
| lg | 48px | `--text-lg` | 24px |
| xl | 64px | `--text-2xl` | 32px |

### Style
- Shape: Circle (`--radius-full`)
- Fallback: Initials on `--surface-accent` background, `--text-link` text
- Border: `--border-width-thick` `--surface-base` (for stacked groups)
- Group: Overlapping with `-8px` margin, right items on top (higher z-index)
- Online indicator: 10px green circle at bottom-right, `--status-success-icon`

---

## 11. Sheet / Drawer

### Base Style
- Background: `--surface-base`
- Shadow: `--shadow-2xl`
- Radius: `--radius-2xl` on visible corners only
- Backdrop: `--dialog-backdrop`

### Directions
| Direction | Width/Height | Use Case |
|-----------|-------------|----------|
| Right | 400px (default), max 50vw | Detail panels, settings |
| Bottom | auto (content), max 85dvh | Mobile actions, filters |
| Left | `--sidebar-width` | Secondary navigation |

### Animation
- Entry: Slide from edge, `--ease-spring-gentle`, `--duration-moderate`
- Handle (mobile bottom sheet): 4px × 40px bar, `--border-strong`, centered at top
- Drag-to-dismiss: velocity-based, spring snap back or close

---

## 12. Command Palette (Cmd+K)

### Style
- Width: 560px max
- Background: `--surface-base`
- Border: `--border-default`
- Radius: `--radius-2xl`
- Shadow: `--shadow-2xl`
- z-index: `--z-modal`

### Structure
```
┌───────────────────────────────────────┐
│ 🔍 Search input (no border)          │
├───────────────────────────────────────┤
│ Group label                           │
│  ▸ Item + shortcut badge    ⌘K       │
│  ▸ Item + description                │
│ Group label                           │
│  ▸ Item                              │
└───────────────────────────────────────┘
```

- Search input: `--text-base`, `--space-4` padding, no visible border
- Group label: `--text-xs` `--weight-semibold` `--text-tertiary`, uppercase
- Item height: 40px, `--space-3` padding
- Active item: `--surface-accent` bg, `--text-link` text
- Shortcut badge: `--surface-raised` bg, `--text-xs` `--font-mono`, `--radius-sm`
- Entry: `scale(0.98) → scale(1)`, `opacity: 0 → 1`, `--ease-spring-snappy`

---

## 13. Toggle / Switch

### Sizes
| Size | Track W×H | Thumb | Travel |
|------|-----------|-------|--------|
| sm | 36px × 20px | 16px | 16px |
| md | 44px × 24px | 20px | 20px |

### Style
- Track off: `--surface-overlay` (light), `--border-strong` bg (dark)
- Track on: `--action-primary`
- Thumb: `--surface-base`, `--shadow-sm`
- Transition: Thumb `--ease-spring-bouncy` `--duration-normal`, Track `--duration-fast`
- Focus: Ring around track

---

## Global Interaction Guidelines

### Focus Management
- All interactive elements must show a visible focus ring: `--ring-width` `--ring-color` `--ring-offset`
- Tab order follows visual layout (left-to-right, top-to-bottom)
- Focus trap inside modals, dialogs, and drawers

### Transitions
| Context | Duration | Easing |
|---------|----------|--------|
| Button hover/active | `--duration-fast` | `--ease-out` |
| Input focus | `--duration-fast` | `--ease-out` |
| Card hover | `--duration-normal` | `--ease-spring-gentle` |
| Modal open | `--duration-normal` | `--ease-spring-snappy` |
| Modal close | `--duration-fast` | `--ease-in` |
| Page transition | `--duration-moderate` | `--ease-spring-gentle` |
| Toast enter | `--duration-moderate` | `--ease-spring-bouncy` |
| Sidebar collapse | `--duration-moderate` | `--ease-spring-gentle` |

### Touch Targets
- Minimum: 44px × 44px (WCAG 2.2 Level AA)
- Recommended: 48px × 48px for primary actions on mobile
- Padding-based expansion when visual size is smaller

---

> **DSA Checkpoint**: Verify that each component aligns with the project branding.
> Adjust Tier 3 (Component) tokens first, then Tier 2 (Semantic) if needed.
> Primitive tokens should only change for brand palette customization.
