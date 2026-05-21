# 1. Screen Registry

**Owner**: {{OWNER}} (UX) — **sole authority to issue IDs**
**Feature**: {{FEATURE_NAME}}
**Domain code**: `{{DOMAIN_CODE}}`
**Last updated**: {{TODAY}}

> **This document is the Single Source of Truth (SSoT).**
> Every Screen ID is created in this table. Figma frame names, `@feature:` comments in code, and screenshot filenames must all follow the IDs in this table.
> **IDs created by any role other than UX are void.** They must be registered in this table before use.

---

## Base structure

| ID | Screen name | State/Case | Trigger | Design status |
|----|-------------|------------|---------|---------------|
| `{{DOMAIN_CODE}}-EXPERT-LIST` | List | default | GNB > Expert Q&A | 🔄 |
| `{{DOMAIN_CODE}}-EXPERT-LIST-EMPTY` | List | no data | new category | 🔄 |
| `{{DOMAIN_CODE}}-EXPERT-LIST-LOADING` | List | skeleton | right after entry |  🔄 |
| `{{DOMAIN_CODE}}-EXPERT-LIST-ERROR` | List | error | API failure | 🔄 |
| `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC01` | Question Detail | no answers | card click (0 answers) | 🔄 |
| `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC02` | Question Detail | before adopt | card click (with answers) | 🔄 |
| `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC03` | Question Detail | adopted | card click (adopted) | 🔄 |
| `{{DOMAIN_CODE}}-EXPERT-WRITE` | Write Question | default | "Ask" button | 🔄 |
| `{{DOMAIN_CODE}}-EXPERT-WRITE-ERROR` | Write Question | validation failed | required input missing | 🔄 |
| `{{DOMAIN_CODE}}-EXPERT-MODAL01` | Delete confirm | Confirm | own question > delete | ❌ |
| `{{DOMAIN_CODE}}-EXPERT-MODAL-LOGIN` | Login prompt | Gate | not logged in > Ask | 🔄 |

**Design status legend**:
- ✅ done
- 🔄 in progress / not started
- ❌ not applicable (cannot proceed)
- 🔁 changed (YYYY-MM-DD)

---

## 9.2 Required inclusions

The following screens must be registered in the Registry **without omission**:

- [ ] Base screen (DEFAULT)
- [ ] All states (LOADING / EMPTY / DEFAULT / ERROR)
- [ ] All modals (Confirm / Form / Error included)
- [ ] Edge-case screens
- [ ] Hidden screens reachable only via URL parameter
- [ ] When UI differs by permission, a separate ID or a note in the "State/Case" column

---

## Screen ID naming rules

```
{DOMAIN}-{PAGE}-{SECTION}-{UC}
────    ─────   ───────   ────
domain  page    section   use case (2 digits; distinguishes state/case)

{{DOMAIN_CODE}}-EXPERT-DETAIL-UC03
```

- `DOMAIN`: product abbreviation (2–6 uppercase characters) — `{{DOMAIN_CODE}}`
- `PAGE`: menu/route unit, uppercase
- `SECTION`: LIST / DETAIL / FORM / WRITE / MODAL / DASHBOARD / SETTINGS (optional)
- `UC{NN}` or state suffix (`-LOADING`, `-EMPTY`, `-ERROR`): distinguishes state/case for the same page

**Responsive branching (separate ID only when structure differs)**:
```
Desktop (≥1024):  {{DOMAIN_CODE}}-EXPERT-DETAIL-UC03
Tablet  (768~1023): {{DOMAIN_CODE}}-EXPERT-DETAIL-UC03-T
Mobile  (<768):   {{DOMAIN_CODE}}-EXPERT-DETAIL-UC03-M
```
→ Pure style changes (font, padding) do not split the ID (see `5-responsive-guide.md`).

---

## Change log

ID changes/additions/removals must be recorded in `11-decision-log.md`.
- Changed IDs are marked `🔁 changed YYYY-MM-DD`
- Removed IDs are not deleted from the table; mark them `❌ deprecated YYYY-MM-DD`

---

_This document is maintained by UX (`{{OWNER}}`). Other roles request changes via Slack or an issue._
