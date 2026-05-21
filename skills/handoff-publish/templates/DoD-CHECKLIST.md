# Definition of Done — Per-Stage Completion Criteria

**Feature**: {{FEATURE_NAME}}
**Last updated**: {{TODAY}}

> Criteria each role must satisfy before saying "I'm done" (PDF §19).
> Each role checks **themselves**; evidence is left in the PR description / Figma link / Loom / test report, etc.

---

## 19.1 UX stage DoD

- [ ] Screen Registry (`1-screen-registry.md`) registration complete
- [ ] State Matrix (`3-state-matrix.md`) authored
- [ ] Permission Matrix (the permission section of `3-state-matrix.md`) authored
- [ ] Business Rules (`7-business-rules.md`) authored (covers every Registry ID)
- [ ] Edge Cases (`4-edge-cases.md`) organized
- [ ] Component Specs (`6-component-specs.md`) defined (when a new component is introduced)
- [ ] Decision Log (`11-decision-log.md`) updated (when changes occur)
- [ ] Loom walkthrough recorded (5–10 min) → link recorded in `walkthrough.loom.md`

---

## 19.2 UI designer stage DoD

- [ ] Figma frame created for every Registry ID (frame name = ID)
- [ ] All states (LOADING / EMPTY / DEFAULT / ERROR) designed
- [ ] Per-permission UI differences reflected (relevant screens)
- [ ] Mobile / Tablet breakpoints designed
- [ ] Color contrast verified (WCAG AA)
  - body text 4.5:1 / large text 3:1
- [ ] Focus state designed
- [ ] All edge cases reflected
- [ ] Only design system tokens used (no custom colors/spacing ❌)

---

## 19.3 Developer stage DoD

- [ ] Every ID component implemented + `// @feature: {SCREEN-ID}` comment
- [ ] All state branches handled (`isLoading` / `isEmpty` / `isError`)
- [ ] All 3 i18n locales (ko/en/vi) registered (build fails on missing key)
- [ ] Keyboard / focus / ARIA behavior verified
- [ ] Lighthouse 90+ (mobile)
- [ ] Only design system classes used (minimize inline styles)
- [ ] `npm run lint` / `npx tsc --noEmit` pass

---

## 19.4 QA stage DoD

- [ ] Verified every ID × state × permission
- [ ] Device matrix verified (Chrome/Safari × Desktop/Tablet/Mobile)
- [ ] All 3 locales verified (check Vietnamese length truncation)
- [ ] Accessibility verified (keyboard / screen reader sampling)
- [ ] Regression tests pass

---

## Verification commands (developer — items that can be automated)

Among developer DoD, the items that can be automatically verified:

```bash
# Lint / TypeCheck
npm run lint
npx tsc --noEmit

# Lighthouse (Chrome headless)
npx lighthouse https://localhost:3000/{{FEATURE_ROUTE}} \
  --only-categories=performance,accessibility \
  --emulated-form-factor=mobile \
  --throttling-method=devtools

# i18n missing-key validation (use the project's i18n library lint rule)
npm run i18n:lint

# Color-contrast verification (axe-core CLI)
npx @axe-core/cli https://localhost:3000/{{FEATURE_ROUTE}} \
  --tags wcag2aa,wcag21aa
```

---

## Caveat: items that cannot be automated

The following **must be checked manually**:

- **Loom walkthrough recording** (UX)
- **1:1 matching between Figma frames and Registry IDs** (verified between UX and UI)
- **Per-permission UI differences** (login test with actually-different accounts)
- **Screen reader testing** (VoiceOver / NVDA)
- **Figma ↔ code pixel parity** (design review)
- **Vietnamese length truncation** (verify rendering with real data)

---

## PR description template (developer)

When creating a PR, include the following sections:

```markdown
## Handoff reference

- Handoff package: `{{FEATURE_NAME}}-handoff/`
- Implemented Screen IDs:
  - [ ] `{{DOMAIN_CODE}}-...`
  - [ ] `{{DOMAIN_CODE}}-...`

## DoD checks

- [ ] `@feature` comment added to every ID
- [ ] State branches handled (isLoading/isEmpty/isError)
- [ ] i18n keys registered in all 3 locales (ko/en/vi)
- [ ] lint + tsc pass
- [ ] Lighthouse 90+ (screenshot attached)
- [ ] a11y keyboard test passed
- [ ] Figma ↔ implementation parity (review link attached)

## Items not applied (if any)

- [ ] {explanation of why it cannot be applied}
```

---

_This file is for reference. It can be edited, but when **removing** an item, leave the rationale in `11-decision-log.md`._
