# Per-Document Auto-Fill Specs (handoff-publish Steps 4-12 detail)

Read this while auto-filling each handoff document. Each section below maps to the correspondingly numbered mainline step.

## Step 4: 1-screen-registry.md

If planning deliverables loaded in Step 1-C exist, convert the screen list from `ia-screen-design.md` into the Screen Registry table format.

| Planner column | Registry column |
|----------------|------------------|
| Screen ID (SCR-NNN) | ID (converted 4-segment) |
| Screen name | Screen name |
| Type | State/Case (default / before adoption / no answers, etc.) |
| Description | Trigger (cause / entry path) |
| — | Design status (initial: 🔄 not started) |

If there is no planning document, leave only the 4 placeholder rows from the PDF §9.1 example (LIST, LIST-EMPTY, LIST-LOADING, DETAIL-UC01).

## Step 5: 2-flows.md

If a journey map / Mermaid diagram exists in `usecase-definition.md`, convert it to the PDF §10 example tree format:

```
[{scenario name} Flow]

{SCREEN-ID}
    └ Click "{action}"
        ├ ({condition}) → {SCREEN-ID}
        └ ({condition}) → {SCREEN-ID}
            └ Click "{action}"
                ├ (success)         → {SCREEN-ID}
                ├ (insufficient tokens) → {SCREEN-ID}
                └ (network error)   → {SCREEN-ID}
```

Map the **success/failure/exception branches** of every button-click/submit to IDs. If missing branches are found, record them in `11-decision-log.md` and add placeholder IDs to the Registry.

## Step 6: 3-state-matrix.md, 4-edge-cases.md

**3-state-matrix.md**: keep the state definitions (LOADING/EMPTY/DEFAULT/ERROR/PARTIAL) as-is from the template. If `feature-definition.md` contains a `permissions per actor` table, auto-convert it for the permission matrix section; otherwise, leave only the 6-column table header (Not logged in / Regular user / Question owner / Answerer / Admin + Action column).

**4-edge-cases.md**: insert the 8 base items from PDF §13 as checkboxes. If `feature-definition.md` has a risk section, extend with additional items.

## Step 7: 5-responsive-guide.md

Use PDF §12 as-is. Keep only the Desktop (≥1024) / Tablet (768~1023) / Mobile (<768) breakpoints + the ID-notation convention (`-T`, `-M` suffixes). If `docs/design-system/DESIGN.md` Front Matter `tokens.breakpoints` exists in the project, use those values as the top priority (legacy fallback: the breakpoint variables in `src/styles/design-tokens.css`).

## Step 8: 6-component-specs.md

**Design system SSoT reference (v5.2.0+ priority)**:
- 1st priority: `docs/design-system/DESIGN.md` Body §4 (Component Guidelines) — global components are referenced via reference links in this file. Front Matter `tokens.color.semantic.*`, `tokens.typography.*` token names are used as-is in the props tables of `6-component-specs.md`.
- 2nd priority (legacy fallback): projects without DESIGN.md reference `docs/design-system/components.md`, and a `/design-init` Recommended note is added at the top of this file.

For feature-specific components, read the UI elements section from `feature-definition.md` and auto-generate in the PDF §14.1 format (props / variants / usage). At minimum, include scaffolds for the 4 card types (CourseCard, QuestionCard, InsightCard, NoticeCard) + Modal (Confirm/Form/Error).

## Step 9: 7-business-rules.md

For each Registry ID, create an empty block in the PDF §15.1 format (exposure policy / components used / per-permission branching / handling when no data / data source + caching). If the `blueprint.md` contains API endpoints, auto-fill the `data source` row.

## Step 10: 8-content-guide.md

Reflect the entire PDF §16–17 content in the template as-is:
- Brand voice (tone / form of address / forbidden expressions)
- Microcopy rules (buttons / errors / Empty / modals)
- Data display rules (images / dates / numbers / text truncation)
- i18n 3-language policy (ko/en/vi, Vietnamese 1.4× length assumption)

If the project specifies different languages, substitute via `{{LANGUAGE_POLICY}}` from Step 3.

## Step 11: 9-ia-sitemap.md, 10-personas.md, 11-decision-log.md

- **9-ia-sitemap.md**: if `ia-screen-design.md` has a menu tree, reconstruct it as an ASCII tree in the PDF §3 format. The URL conventions and depth policy (max 3 depth Recommended) stay as in the template.
- **10-personas.md**: organize the Top 3–5 personas from `interview-report.md` in the PDF §4 format (goal / pain points / usage context / device). Also extract the Top 5–10 key scenarios.
- **11-decision-log.md**: record the Step 2-B SCR-NNN → 4-segment ID conversion log as the first entry. Subsequent changes are added by UX directly.

## Step 12: 0-README.md variable substitution

- **0-README.md**: keep template as-is (PDF §7 Quick Start + 5-min guide per role). Only verify that `{{FEATURE_NAME}}`/`{{DOMAIN_CODE}}` from Step 3 were substituted correctly.
- **walkthrough.loom.md**: already copied as a template in Step 3, so no separate creation needed. UX adds the Loom URL manually after recording.
- **DoD-CHECKLIST.md**: already copied as a template in Step 3; keep the per-role (UX/UI/Dev/QA) checklist format as-is.

## Appendix: Anti-patterns (PDF §23)

The 10 problems this skill aims to prevent:

1. Missing modal/error screens → register modal IDs in the Registry
2. Per-state UI undefined → mandate the State Matrix
3. Missing Mobile design → mandate the Responsive Guide
4. Per-permission UI differences not reflected → mandate the permission matrix
5. Figma/code IDs created separately → SSoT (Registry) + UX-only issuance authority
6. Changes reflected on only one side → Decision Log + change-management process
7. Inconsistent card data items → mandate 6-component-specs.md
8. Arbitrary exposure conditions → mandate 7-business-rules.md
9. Vietnamese length truncation → assume 1.4× length
10. Accessibility non-compliance → Accessibility guide + DoD
