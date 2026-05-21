# {{PROJECT_NAME}} — {{FEATURE_NAME}} Handoff Package

**Authored**: {{TODAY}}
**Owner**: {{OWNER}} (UX Lead)
**Scope**: {{PROJECT_NAME}}, and all future new feature development
**Domain code**: `{{DOMAIN_CODE}}`

> **TL;DR** — Define every screen by a Screen ID → call them by the same name — `1-screen-registry.md` is the single source of truth for IDs — define not screens but **"cases (state/permission/responsive)"** — deliver screen definitions + collaboration policy + operational rules together as a Handoff package.

---

## 🎯 Purpose

Define an efficient process where UX → UI → Dev → QA can collaborate against the same baseline.

**Goals**:
- Fast and accurate communication via a **shared vocabulary** between teams
- Standardized workflows that **produce the same result no matter who participates**
- A consistent working environment where changes are **automatically tracked and shared**
- A structure where AI tools like Claude Code can be leveraged through a **shared context**

---

## 👥 Roles and responsibilities (RACI)

| Task | UX | UI designer | Developer | QA |
|------|----|-------------|-----------|----|
| Issue Screen IDs | ✅ Owner | Consulted | Informed | Informed |
| Author the handoff package | ✅ Owner | Consulted | Informed | Informed |
| Author Figma frames | Consulted | ✅ Owner | Informed | Informed |
| Implement the code | Consulted | Consulted | ✅ Owner | Informed |
| Decide ID changes/additions | ✅ Owner | Notified | Notified | Notified |
| Verification / missing-check | Reviewer | Reviewer | Reviewer | ✅ Owner |

**Rule**: any new ID issued by a non-UX role is void. UX must register the ID in the Screen Registry (`1-screen-registry.md`) before use.

---

## 🧠 3 core principles

### 1. Screen-ID-based collaboration

Every screen is identified by a unique ID.

```
{{DOMAIN_CODE}}-EXPERT-DETAIL-UC03
─────────     ──────   ──────   ────
domain         page    section  use case
```

→ Prevents calling the same screen by different names → design / dev / QA / Claude Code all use the same baseline.

### 2. Single Source of Truth (SSoT)

```
1-screen-registry.md = the single source of truth for every screen ID (Screen Registry)
```

⚠️ **Must follow**: all IDs are created in this document — Figma follows this document — code follows this document — creating IDs ad-hoc in Figma/code is **forbidden**.

> 💡 **What "register in the Registry" means**: it means adding a new row to the table in `1-screen-registry.md` and committing. Example) Designer needs a new screen → asks UX → UX adds a row to the table → then the designer starts the Figma work.

### 3. State-based design

Every screen is defined not as a static screen but as a combination of **State × Permission × Device**.

---

## 🚀 Quick Start — 5-minute guide per role

### 🎨 UI designer

```
1. git pull → check the {{FEATURE_NAME}}-handoff/ folder
2. Pick the ID to work on from 1-screen-registry.md
3. Check the state/permission of the screen in 3-state-matrix.md
4. Check the responsive definition in 5-responsive-guide.md
5. Check the exposure policy / data mapping in 7-business-rules.md
6. Check the spec of cards/components to use in 6-component-specs.md
7. Author the Figma frame name in the Screen ID format
   e.g., "{{DOMAIN_CODE}}-EXPERT-DETAIL-UC03 / Question Detail / Adopted"
8. When done → share via PR or Figma link
```

### 💻 Developer

```
1. Find the ID in the {{FEATURE_NAME}}-handoff/ folder
2. Add an ID comment to the component/page
   // @feature: {{DOMAIN_CODE}}-EXPERT-DETAIL-UC03
3. Find the same ID frame in Figma
4. Check the data policy in 7-business-rules.md
5. Check copy / i18n keys in 8-content-guide.md
6. If you find a missing or contradictory ID, contact UX immediately
```

### 🤖 Using Claude Code

```
Designer: "Compare the Figma {{DOMAIN_CODE}}-* frames against 1-screen-registry.md
           and tell me which IDs are missing designs."

Developer: "Implement {{DOMAIN_CODE}}-EXPERT-DETAIL-UC03.
            Reference the same-ID frame in Figma for design,
            and 7-business-rules.md for business rules."

UX:       "Compare 1-screen-registry.md against the @feature comments in code
           and find IDs that are out of sync."
```

→ Pass context with the same ID → AI auto-detects what's missing.

---

## 📂 Package structure

```
{{FEATURE_NAME}}-handoff/
├── 0-README.md              (this file — guide + Quick Start)
├── 1-screen-registry.md     (Screen Registry — SSoT)
├── 2-flows.md               (user flows)
├── 3-state-matrix.md        (state + permission definitions)
├── 4-edge-cases.md          (exception / caution cases)
├── 5-responsive-guide.md    (responsive baseline)
├── 6-component-specs.md     (card/component spec + data anatomy)
├── 7-business-rules.md      (per-screen business rules / exposure policy)
├── 8-content-guide.md       (UX writing + data display rules)
├── 9-ia-sitemap.md          (information architecture / sitemap)
├── 10-personas.md           (personas / key scenarios)
├── 11-decision-log.md       (design decision history)
├── screenshots/             (captures keyed by Screen ID)
│   ├── {{DOMAIN_CODE}}-EXPERT-LIST.png
│   └── {{DOMAIN_CODE}}-EXPERT-DETAIL-UC03.png
└── walkthrough.loom.md      (walkthrough video link)
```

---

## ✅ Key takeaways

1. Define **"cases"**, not screens
2. Collaborate against the **ID** (UX has sole authority to issue)
3. The **Screen Registry** (`1-screen-registry.md`) is the source of truth (SSoT)
4. **Business Rules + Component Specs** specify what is shown and how
5. **Content Guide + i18n + a11y** secure consistency / localization / accessibility
6. **Definition of Done** unifies completion criteria per stage
7. **Decision Log** preserves the decision history
8. Talk to **Claude Code** using the same ID

---

> 💬 "UX's role is not to make a design, but to define how the product behaves."

**Document version**: v1.1 | **Reference guide**: HANDOFF_PROCESS_GUIDE (FECT Academy UX Lead Joy)
