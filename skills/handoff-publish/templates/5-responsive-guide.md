# 5. Responsive Guide — Responsive Baseline

**Feature**: {{FEATURE_NAME}}
**Last updated**: {{TODAY}}

---

## 12.1 ID notation convention

```
Desktop (≥1024):    {{DOMAIN_CODE}}-EXPERT-DETAIL-UC03
Tablet  (768~1023): {{DOMAIN_CODE}}-EXPERT-DETAIL-UC03-T
Mobile  (<768):     {{DOMAIN_CODE}}-EXPERT-DETAIL-UC03-M
```

---

## 12.2 Principles

- **Design for Desktop first** → for Tablet/Mobile, define only the breakpoints
- **Create a separate ID only when structure differs** (LNB → Bottom tabs, etc.)
- **Pure style changes** (font size, padding) do not split the ID → handle within the same ID

---

## Breakpoint details

| Breakpoint | Width | Main changes |
|------------|-------|--------------|
| Desktop | ≥1024px | Base layout. Left LNB + main content + right widget (optional) |
| Tablet | 768~1023px | Remove right widget; shrink left LNB or switch to hamburger menu |
| Mobile | <768px | LNB → Bottom Tab; content becomes 1-column; cards become full-width |

---

## Layout-branch checklist

For each screen, verify the following:

- [ ] **Desktop → Tablet transition**
  - Handling of the right widget / sidebar
  - Column priority in tables (which columns to hide)
  - Card grid column changes (e.g., 4 → 2)

- [ ] **Tablet → Mobile transition**
  - Navigation pattern (LNB → Bottom Tab / Drawer)
  - Modal size (whether to switch to a full-screen modal)
  - Form-field layout (2-col → 1-col)
  - Action-button position (fixed-bottom FAB / sticky CTA)

---

## Breakpoint tokens

Must match the project's design tokens (`src/styles/design-tokens.css` or the Tailwind config):

```css
/* design-tokens.css example */
--breakpoint-sm: 640px;
--breakpoint-md: 768px;   /* enters tablet */
--breakpoint-lg: 1024px;  /* enters desktop */
--breakpoint-xl: 1280px;
```

```css
/* Mobile-first approach */
.card {
  /* base mobile style */
}

@media (min-width: 768px) {
  /* tablet style */
}

@media (min-width: 1024px) {
  /* desktop style */
}
```

---

## Touch targets (Mobile)

- **Minimum touch area**: 44×44px (iOS HIG) / 48×48dp (Material)
- **Spacing**: at least 8px gap between touch targets
- **Hover-effect substitute**: on Mobile, substitute with `:active` / press animation

---

## Per-screen branching ID list

| Desktop ID | Tablet branch needed? | Mobile branch needed? | Mobile ID |
|------------|----------------------|------------------------|-----------|
| `{{DOMAIN_CODE}}-EXPERT-LIST` | ❌ (only column count) | ✅ (1-col cards + Bottom Tab) | `{{DOMAIN_CODE}}-EXPERT-LIST-M` |
| `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC03` | ❌ | ✅ (sticky answer input) | `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC03-M` |
| `{{DOMAIN_CODE}}-EXPERT-WRITE` | ❌ | ✅ (full-screen form) | `{{DOMAIN_CODE}}-EXPERT-WRITE-M` |
| `{{DOMAIN_CODE}}-EXPERT-MODAL01` | ❌ | ✅ (convert to Bottom Sheet) | `{{DOMAIN_CODE}}-EXPERT-MODAL01-M` |

_TODO (UI designer): During actual Figma work, confirm whether branching is required and update the table above._
