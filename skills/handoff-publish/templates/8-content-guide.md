# 8. Content Guide — UX Writing + Data Display Rules

**Feature**: {{FEATURE_NAME}}
**Last updated**: {{TODAY}}

> **Why is this needed?** Even when the same component is used, inconsistent labels/messages across screens break the user experience. This guarantees a consistent brand voice + honest UX principles.

---

## 16.1 Brand voice

- **Tone**: professional, trustworthy, practitioner-focused
- **Form of address**: polite to the user (e.g., "Please…")
- **Forbidden**: exaggeration / vague phrasing / lazy expressions like "Loading..."

---

## 16.2 Microcopy rules

### [Buttons]
- **Principle**: action verb + honesty
- ✅ **"Sign up and ask"** (specifies the actual action)
- ❌ "Ask now" (in reality, this is a login gate)

### [Error messages]
- **Principle**: what + why + how to resolve
- ✅ **"You don't have enough tokens. Recharge and try again. [Recharge]"**
- ❌ "An error occurred"

### [Empty state]
- **Principle**: invite the next action
- ✅ **"No questions yet. [Write your first question]"**
- ❌ "No data"

### [Confirmation modals]
- **Principle**: what + spell out the consequence
- ✅ **"Delete this question? Once deleted it cannot be restored."**
- ❌ "Are you sure?"

---

## 16.3 Data display rules

### [Images/media]
- **Thumbnail ratios**: 16:9 (courses), 4:3 (insights), 1:1 (profiles)
- **Recommended resolutions**: 320×180 (thumbnail), 800×450 (detail)
- **Formats**: WebP first, JPEG fallback
- **Placeholder**: category color + first letter
- **alt text required**: decorative images use `alt=""` (screen readers skip)

### [Date/time]
- Within 1 hour: "just now", "10 min ago"
- Within 24 hours: "3 hr ago"
- Within 7 days: "3 days ago"
- Beyond 7 days: "2026.04.20"
- When absolute time is needed: hover tooltip
- **Timezone**: user's local timezone (server stores UTC)

### [Numbers]
- Under 1,000: exact number ("847 people")
- 1,000–9,999: "1.2K" or "1,234"
- 10,000+: "1.2만" (Korean) / "12K" (English)
- Currency: "₩12,000" / "$12.00" (locale)

### [Text truncation]
- **Card title**: 2 lines (`line-clamp-2`)
- **Card description**: 3 lines
- **Instructor/author name**: 1-line truncate
- **Category badge**: do not truncate (keep short)

---

## 17. i18n localization policy

> FECT enforces **3 mandatory languages: Korean / English / Vietnamese**. If a designer only views the Korean text, the layout will break at Vietnamese length.

### 17.1 Translation scope / exceptions

| Target | Policy |
|--------|--------|
| All UI text (buttons/labels/messages) | ✅ translation required (3 languages) |
| Brand names ("FECT", "ASTRA") | ❌ do not translate |
| Intentional English (design spec) | ❌ do not translate + `i18n-ignore` comment |

### 17.2 Text length assumptions
- Assume **Vietnamese = 1.4× the length of Korean**
- Design line-breaks / truncation against the **Vietnamese baseline**
- Button width should be flexible to text length (avoid fixed width)

### 17.3 Procedure for adding new text

```
1. UX writes 3 translations: ko/en/vi
2. Developer registers the i18n key (using the project's i18n library)
3. Code calls t('key')
4. Lint verifies the key exists in every locale file
```

→ A lint rule that fails the build when only the code adds a key without the locale file is Recommended.

### i18n key naming convention

```
{{feature}}.{{screen}}.{{element}}.{{state}}

Example:
expert.detail.acceptButton.default
expert.detail.acceptButton.disabled
expert.list.empty.message
expert.list.empty.cta
```

---

## 18. Accessibility (a11y) guidelines

> Accessibility is **a legal requirement and a foundation of trust**. UX/UI/Dev are all responsible.

### 18.1 Compliance level
- Target: **WCAG 2.1 AA**

### 18.2 Color contrast
- Body text / background: **at least 4.5:1**
- Large text (18pt+): **at least 3:1**
- Design system tokens satisfy this automatically (verify when using custom colors)

### 18.3 Keyboard navigation
- All interactions must be possible by keyboard (Tab / Enter / ESC)
- Tab order matches visual order
- Focus state is **visually clear** (designer's responsibility)

### 18.4 Modals / dropdowns
- Close with ESC
- Focus trap (Tab stays inside the modal)
- After closing, focus returns to the trigger element

### 18.5 Screen readers
- Image `alt` attribute required (decorative images use `alt=""`)
- Button `aria-label` (icon-only buttons)
- Form fields linked to `<label>`
- Use `aria-live` when dynamic content changes

### 18.6 Responsibility split
- **Designer**: color contrast, focus-state design, visual order
- **Developer**: ARIA attributes, keyboard handlers, focus-trap implementation
- **QA**: screen-reader testing (VoiceOver / NVDA)

---

## Per-screen copy reference (this feature)

List the key text for each Screen ID. Developers use this section as the `ko` value when registering i18n keys.

### `{{DOMAIN_CODE}}-EXPERT-LIST`
- Header: "Expert Q&A"
- Subhead: "Ask trade experts directly and get answers"
- CTA (logged in): "Ask"
- CTA (not logged in): "Sign up and ask"
- EMPTY message: "No questions yet"
- EMPTY CTA: "Write your first question"

### `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC02`
- Adopt button: "Adopt this answer"
- Adopt button disabled hover: "Only the question owner can adopt"
- Answer-writing placeholder: "Enter your answer (minimum 50 characters)"
- Submit answer button: "Submit answer"

### `{{DOMAIN_CODE}}-EXPERT-MODAL01` (delete confirmation)
- Title: "Delete this question?"
- Description: "A deleted question cannot be restored. Registered answers will be deleted together."
- Cancel: "Cancel"
- Confirm: "Delete"

_TODO (UX): Beyond the examples above, list the key copy for every Registry ID._
