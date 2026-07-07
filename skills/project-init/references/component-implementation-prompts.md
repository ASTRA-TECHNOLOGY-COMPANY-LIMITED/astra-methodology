# Component Implementation Prompts (Step 5-B)

Literal `frontend-design` invocation prompts. Substitute the `{...}` placeholders with the project's design system, tech stack, and token paths, then translate the whole prompt into the Step 0 language before invoking the skill. Use the Web prompt for Web projects and the Mobile prompt for Mobile projects.

## Web project prompt

```
"Implement the design system common components for project {project-name}.

- Design system: {selected-design-system}
- Frontend: {frontend-tech-stack}
- **Design system SSoT**: docs/design-system/DESIGN.md (YAML Front Matter + Markdown Body — unifies tokens, persona, anti-AI aesthetic rules)
- Design tokens CSS: src/styles/design-tokens.css (artifact auto-generated from DESIGN.md — do not hand-edit)
- Component guide: docs/design-system/DESIGN.md §4 (legacy: docs/design-system/components.md)
- Layout guide: see docs/design-system/layout-grid.md

Implement the following common components:
1. Button — Primary/Secondary/Danger/Ghost/Outline variants, sm/md/lg sizes, loading/disabled states
2. Input — text input, label, error state, helper text, disabled state
3. Card — Default/Elevated/Outlined/Interactive/Ghost variants, Container Query responsive
4. Modal/Dialog — header/body/footer structure, backdrop, sm/md/lg/full sizes, Spring animation
5. Toast — Success/Warning/Error/Info variants, Spring entry animation, auto-dismiss
6. Badge — status badges, category tags, sm/md/lg sizes, dot indicator
7. Table — sorting, hover, sticky header, responsive (mobile card switch)
8. Dropdown/Select — option list, search, multi-select, Command Palette style
9. Tabs — animated indicator, active/inactive states
10. Sidebar Layout — collapse/expand, Spring transition animation, active menu highlight
11. Skeleton — text/avatar/card/table shimmer patterns
12. Avatar — image/initials/icon, xs~xl sizes, online indicator, group stacking
13. Toggle/Switch — sm/md sizes, Spring bounce transition

All components must:
- Reference Semantic/Component tokens only (no direct Primitive references)
- Support OKLCH-based dark mode
- Be responsive + Container Query compatible
- Follow accessibility (ARIA, focus ring, keyboard navigation)
- Use Spring easing (--ease-spring-*) + prefers-reduced-motion handling
- Follow the project's coding conventions
- Also generate a design system preview page (where every component can be verified in light/dark mode)"
```

## Mobile project prompt

```
"Implement the mobile design system common components for project {project-name}.

- Design system: {selected-design-system}
- Mobile framework: {mobile-framework}
- **Design system SSoT**: docs/design-system/DESIGN.md (YAML Front Matter + Markdown Body)
- Design tokens: {token-file-path} (artifact auto-generated from DESIGN.md)
- Component guide: docs/design-system/DESIGN.md §4 (legacy: docs/design-system/components.md)
- Mobile design guide: see $CLAUDE_PLUGIN_ROOT/docs/ux/mobile-design-guide.md (platform guidelines, touch interactions, animation timing, haptic feedback, accessibility criteria)

Implement the following common components:
1. Button — Primary/Secondary/Danger/Ghost variants, sm/md/lg sizes, loading/disabled states, haptic feedback
2. TextInput — text input, label, error state, helper text, disabled state, keyboard-type support
3. Card — Default/Elevated/Outlined/Pressable variants
4. BottomSheet — snap points, drag handle, backdrop, size variants
5. Toast/Snackbar — Success/Warning/Error/Info variants, auto-dismiss, swipe-to-dismiss
6. Badge — status badges, notification counts, sm/md sizes
7. ListItem — leading icon, title/subtitle, trailing accessory, swipe actions
8. BottomNavigation — tab icon + label, active indicator, badge support
9. Avatar — image/initials/icon, sm/md/lg/xl sizes, online status indicator
10. LoadingIndicator — Spinner/Skeleton/Shimmer variants, full-screen overlay
11. Dialog/Alert — title/message/action buttons, confirm/cancel pattern
12. SearchBar — search icon, clear button, cancel button, autocomplete support

All components must:
- Use design tokens (theme system)
- Support dark mode (linked to system setting)
- Provide a minimum touch area of 44×44dp
- Follow accessibility (screen reader labels, focus management)
- Follow the project's coding conventions
- Also generate a design system preview screen (Storybook or an in-app preview screen)"
```
