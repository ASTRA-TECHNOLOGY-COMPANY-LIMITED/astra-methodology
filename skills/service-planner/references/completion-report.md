# Step 8 completion-report template

Instantiate this block once every deliverable is generated and print it to the user. Fill each `{N}` / `{DESIGN_TONE}` / `{OUTPUT_DIR}` placeholder from the run.

```
## Planning deliverables generation complete

📁 Deliverables location: {OUTPUT_DIR}

| # | Deliverable | File | Status |
|---|-------------|------|--------|
| 1 | Market / competitor analysis | market-analysis.md | ✅ done |
| 2 | Interview report | interview-report.md | ✅ done |
| 3 | Requirements definition | requirements-definition.md | ✅ done |
| 4 | Use-case definition | usecase-definition.md | ✅ done |
| 5 | IA / screen-design report | ia-screen-design.md | ✅ done |
| 6 | HTML mockup index | index.html | ✅ done |
| 7 | Shared styles | styles.css | ✅ done |
| 8 | Per-screen HTML mockups | SCR-001.html ~ SCR-{N}.html | ✅ done ({N}) |
| 9 | Feature definition | feature-definition.md | ✅ done |

▶︎ Open `{OUTPUT_DIR}/index.html` in your browser to view the HTML mockups.

### Summary
- Planning mode: {new service planning / improve existing service}
- Analyzed actors: {N} types, {N × 3} personas
- Market / competitor analysis: {N} competitors, {N} SWOT strategies
- Derived pain points: {N}
- Derived JTBDs: {N}
- Adopted ideas: {N}
- Defined KPIs: {N} (OKRs: {N})
- Defined requirements: functional {N} + non-functional {N}
- Defined use cases: {N}
- Customer journey maps: {N}
- IA menu items: {N}
- Wireframes: {N} screens (markdown + HTML)
- HTML mockups: {N} SCR-NNN.html (design tone {DESIGN_TONE} applied, responsive + dark mode)
- Defined features: Feature Groups {N}, Features {N}, Sub-features {N}
- User Story Map: MVP {N}, v1.1 {N}, v1.2 {N}
- Risks: {N} identified
- Service policies: {N} defined

Next, run `/project-init` (initial project setup) or author a blueprint (`docs/blueprints/{NNN}-{feature}/blueprint.md`). For long-running features that need designer/QA collaboration, you can additionally generate a Screen-ID-based collaboration package via `/handoff-publish`.
```
