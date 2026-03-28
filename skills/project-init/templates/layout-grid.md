# Layout Grid System

> DSA customizes this for the project.
> AI references this guide when generating layouts.
> Uses modern CSS: Container Queries, CSS Grid/Subgrid, Fluid Spacing.

## 1. Breakpoints

| Token | Range | Columns | Gutter | Container Padding |
|-------|-------|---------|--------|-------------------|
| `xs` | ~479px | 4 | `--space-4` (16px) | `--space-4` (16px) |
| `sm` | 480~639px | 4 | `--space-4` (16px) | `--space-5` (20px) |
| `md` | 640~1023px | 8 | `--space-6` (24px) | `--space-6` (24px) |
| `lg` | 1024~1279px | 12 | `--space-6` (24px) | `--space-8` (32px) |
| `xl` | 1280~1535px | 12 | `--space-8` (32px) | `--space-8` (32px) |
| `2xl` | 1536px~ | 12 | `--space-8` (32px) | `--space-10` (40px) |

```css
/* Media Queries (Mobile First) */
/* Default: Mobile (xs) */
@media (min-width: 480px)  { /* sm — Large mobile  */ }
@media (min-width: 640px)  { /* md — Tablet         */ }
@media (min-width: 1024px) { /* lg — Desktop         */ }
@media (min-width: 1280px) { /* xl — Wide desktop     */ }
@media (min-width: 1536px) { /* 2xl — Ultra-wide      */ }
```

## 2. Container

| Breakpoint | Max Width | Horizontal Padding |
|------------|-----------|-------------------|
| xs/sm | 100% | `--space-4` → `--space-5` |
| md | 100% | `--space-6` |
| lg | 1024px | `--space-8` |
| xl | 1200px | `--space-8` |
| 2xl | 1400px | `--space-10` |

```css
.container {
  width: 100%;
  margin-inline: auto;
  padding-inline: var(--space-4);
}

@media (min-width: 640px)  { .container { padding-inline: var(--space-6); } }
@media (min-width: 1024px) { .container { max-width: 1024px; padding-inline: var(--space-8); } }
@media (min-width: 1280px) { .container { max-width: 1200px; } }
@media (min-width: 1536px) { .container { max-width: 1400px; padding-inline: var(--space-10); } }
```

## 3. Grid System

### CSS Grid (12-Column)

```css
.grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
}

@media (min-width: 640px) {
  .grid {
    grid-template-columns: repeat(8, 1fr);
    gap: var(--space-6);
  }
}

@media (min-width: 1024px) {
  .grid {
    grid-template-columns: repeat(12, 1fr);
    gap: var(--space-6);
  }
}

@media (min-width: 1280px) {
  .grid { gap: var(--space-8); }
}
```

### Common Layout Patterns

```
[Desktop 12-column — lg+]

1. Full width
┌──────────────────────────────────────────────────┐
│                    12 columns                     │
└──────────────────────────────────────────────────┘

2. Sidebar + Content (3+9)
┌────────────┬─────────────────────────────────────┐
│  3 columns │              9 columns               │
│  Sidebar   │              Main Content             │
└────────────┴─────────────────────────────────────┘

3. Equal Three-panel (4+4+4)
┌──────────────┬──────────────┬──────────────┐
│   4 columns  │   4 columns  │   4 columns  │
└──────────────┴──────────────┴──────────────┘

4. Dashboard (3+3+6 / asymmetric)
┌───────┬───────┬──────────────────────────────┐
│ 3 col │ 3 col │          6 columns            │
└───────┴───────┴──────────────────────────────┘

5. Content + Aside (8+4)
┌──────────────────────────────┬──────────────┐
│          8 columns           │   4 columns  │
│          Main Article        │   Aside/TOC  │
└──────────────────────────────┴──────────────┘

[Tablet 8-column — md]
- Sidebar: Collapsed (64px) or overlay
- Cards: 2 columns (4 each)
- Dashboard: 4+4 stacking

[Mobile 4-column — xs/sm]
- All elements: Full width (4 columns)
- Sidebar: Hamburger menu → overlay
- Cards: 1 column (stacked)
```

### Subgrid (for aligned nested layouts)

```css
/* Parent grid */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-6);
}

/* Child inherits parent grid alignment */
.card {
  display: grid;
  grid-template-rows: subgrid;
  grid-row: span 3; /* header, body, footer aligned across cards */
}
```

## 4. Container Queries (Component-Level Responsive)

Container queries enable components to adapt based on their parent container's size, not the viewport. This is essential for reusable components that appear in sidebars, modals, and main content areas.

```css
/* Define a query container */
.card-container {
  container-type: inline-size;
  container-name: card;
}

/* Component adapts to container width */
@container card (max-width: 300px) {
  .card { flex-direction: column; }
  .card-image { aspect-ratio: 16/9; width: 100%; }
}

@container card (min-width: 301px) {
  .card { flex-direction: row; }
  .card-image { width: 120px; aspect-ratio: 1; }
}

@container card (min-width: 500px) {
  .card-title { font-size: var(--fluid-lg); }
  .card-meta { display: flex; gap: var(--space-4); }
}
```

### Container Query Units

```css
/* Proportional sizing within containers */
.card-title {
  font-size: clamp(var(--text-sm), 4cqi, var(--text-xl));
  padding: clamp(var(--space-3), 2cqi, var(--space-6));
}
```

### When to Use What

| Technique | Use When |
|-----------|----------|
| Media Queries | Major page layout shifts (sidebar collapse, nav changes) |
| Container Queries | Component-level adaptation (card, widget, panel) |
| CSS Grid | Page-level and section-level layout |
| Subgrid | Aligned children across sibling components |
| `clamp()` | Fluid typography and spacing |

## 5. Page Layout

### Base Page Structure

```
┌─────────────────────────────────────────────┐
│               GNB (56px, sticky)             │
├──────────┬──────────────────────────────────┤
│          │         Page Header               │
│  Sidebar │  ────────────────────────────────│
│  (240px) │                                   │
│          │         Main Content              │
│          │         (scrollable)              │
│          │                                   │
│          │  ────────────────────────────────│
│          │         Footer (optional)         │
├──────────┴──────────────────────────────────┤
```

```css
.app-layout {
  display: grid;
  grid-template-columns: var(--sidebar-width) 1fr;
  grid-template-rows: var(--nav-height) 1fr;
  min-height: 100dvh;
}

/* Mobile: sidebar as overlay */
@media (max-width: 1023px) {
  .app-layout {
    grid-template-columns: 1fr;
  }
}
```

### Spacing Rules

| Context | Spacing Token | Value |
|---------|---------------|-------|
| GNB ↔ Content | 0 (GNB is sticky, content scrolls underneath) | — |
| Page Header ↔ Main | `--space-6` | 24px |
| Section ↔ Section | `--fluid-space-lg` | 24~40px |
| Card ↔ Card | `--space-4` ~ `--space-6` | 16~24px |
| Label ↔ Input | `--space-1-5` | 6px |
| Form field ↔ Field | `--space-4` | 16px |
| Form group ↔ Group | `--space-8` | 32px |
| Inline elements | `--space-2` ~ `--space-3` | 8~12px |

### Fluid Section Spacing

```css
.section + .section {
  margin-top: var(--fluid-space-lg);
}

.page-header {
  padding-block: var(--fluid-space-md);
}
```

## 6. Responsive Behavior Summary

| Element | Mobile (xs/sm) | Tablet (md) | Desktop (lg+) |
|---------|---------------|-------------|----------------|
| GNB | Hamburger + logo | Icon + text | Full navigation |
| Sidebar | Overlay (drawer) | Collapsed (64px) | Expanded (240px) |
| Card grid | 1 column | 2 columns | 3~4 columns |
| Table | Card conversion | Horizontal scroll + sticky col | Full table |
| Modal | Full screen (100dvh) | Centered (max 640px) | Centered (max 640px) |
| Form | 1 column | 2 columns | 2 columns |
| Toast | Top-center, full-width | Top-right, 420px | Top-right, 420px |
| Bottom sheet | Full-width drawer | Side sheet (400px) | — (use modal) |

---

> **DSA Checkpoint**: Verify that this grid system suits the project's page composition.
> Dashboard-centric projects may need a 16-column grid or custom sidebar widths.
> Container queries are recommended for all reusable components.
