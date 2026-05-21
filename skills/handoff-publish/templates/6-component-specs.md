# 6. Component Specs — Card / Component Specifications

**Feature**: {{FEATURE_NAME}}
**Last updated**: {{TODAY}}

> **Why is this needed?** When the same card is used across multiple screens, having designers/developers build it differently per screen breaks consistency. Define the **data structure (anatomy)** of the component once and reference it from every screen.

---

## 14.1 Authoring format (example)

## CourseCard

### Required props
- `courseId`, `title`, `thumbnail`, `instructor`, `rating`, `studentCount`, `price`

### Conditional props
- `isNew` (shown when registered within 7 days)
- `isBest` (shown when in top 10%)
- `progress` (only while enrolled)
- `discountPrice` (when a discount price exists)

### Size variants
- `Large` (4:3, featured)
- `Medium` (16:9, list default)
- `Small` (1:1, sidebar)

### Used in
- `/academy/courses` (list)
- `/academy` (popular courses section)
- `/academy/courses/[id]` (related courses)
- `/academy` (in-progress card)

---

## QuestionCard

### Required props
- `questionId`, `title`, `excerpt`, `author`, `createdAt`, `answerCount`, `viewCount`

### Conditional props
- `isAccepted` (badge when adoption is complete)
- `isHot` (5 or more answers within 24 hours)
- `hasImage` (whether an image is included)
- `category` (category badge)

### Size variants
- `Large` (main featured)
- `Medium` (list default)
- `Compact` (sidebar, related questions)

### Used in
- `/{{DOMAIN_CODE}}/expert` (list)
- `/{{DOMAIN_CODE}}/expert/[id]` (related questions)
- Dashboard (my questions card)

---

## InsightCard

### Required props
- `insightId`, `title`, `summary`, `thumbnail`, `publishedAt`, `category`

### Conditional props
- `isPremium` (premium-only content)
- `readTime` (estimated read time)

### Size variants
- `Feature` (main banner)
- `Standard` (list default)

### Used in
- `/{{DOMAIN_CODE}}/insight` (list)
- `/{{DOMAIN_CODE}}` (main featured)

---

## NoticeCard

### Required props
- `noticeId`, `title`, `publishedAt`

### Conditional props
- `isPinned` (pinned to top)
- `isNew` (within 7 days)
- `hasAttachment` (has an attachment)

### Used in
- `/{{DOMAIN_CODE}}/insight?tab=notice`
- Header notice banner (latest 1)

---

## Modal components

### 14.2 Modal — common

| Variant | Purpose | Composition |
|---------|---------|-------------|
| `Confirm` | Confirm destructive action (delete, account removal, etc.) | title + description + Cancel / Confirm buttons |
| `Form` | Simple input (report, feedback, etc.) | title + input field + Cancel / Submit buttons |
| `Error` | Error message + recovery action | title + description + Retry / Close |
| `Login Gate` | Login prompt | title + CTA link + Close |

---

## Search bar / Filter bar / Pagination

### SearchBar
- Props: `placeholder`, `onSearch`, `initialValue`, `debounceMs` (default 300ms)
- States: focus / typing / has results / no results
- Used in: top of list pages

### FilterBar
- Props: `filters[]`, `onChange`, `activeFilters`
- Composition: chip-based multi-select
- Used in: list pages

### Pagination
- Props: `currentPage`, `totalPages`, `onChange`
- Variants: `Numbered` (page numbers) / `LoadMore` (load-more button) / `Infinite` (infinite scroll)
- Mobile default: LoadMore

---

## 14.3 Principles

- **DRY**: define a component **once**; reference only from screen rules
- **Per-screen data mapping** is authored in `7-business-rules.md`
- **Adding a new component requires UX approval** (reusability judgment)

---

## Component implementation checklist (Dev reference)

When implementing each component:

- [ ] Define prop types (TypeScript interface)
- [ ] Clearly distinguish required vs. optional props
- [ ] Unify variants under the `variant` prop (e.g., `variant: 'large' | 'medium' | 'small'`)
- [ ] Use only design tokens (no hardcoded colors/sizes)
- [ ] Link to anatomy with a `// @feature: COMPONENT-{NAME}` comment
- [ ] Author Storybook stories (include every variant)
- [ ] Accessibility: role, aria-label, keyboard navigation

---

_TODO (UX/UI): Beyond the examples above, add every shared component used in this feature. For existing global components (defined in `docs/design-system/components.md`), leave only a reference link — do not duplicate the description._
