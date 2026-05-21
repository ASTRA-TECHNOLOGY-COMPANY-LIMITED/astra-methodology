# 11. Decision Log — Design Decision History

**Feature**: {{FEATURE_NAME}}
**Owner**: {{OWNER}}
**Last updated**: {{TODAY}}

> **Why is this needed?** Three months later, when a new designer/developer joins and asks "why did you do this?", **if there's no one to answer, they will arbitrarily revert it.** Decision history is the core of institutional knowledge.

---

## What to include (per entry)

- Date
- Affected Screen ID(s)
- Change (Before → After)
- Rationale
- Alternatives considered
- Decider

---

## When to write

- **All decisions that affect an ID** (design / policy / technical)
- **Label changes, component removal, sort changes**, etc. that are user-visible
- **IA changes, URL changes, permission-policy changes**
- **Out-of-Scope judgments** (why something is not included in the handoff)

---

## Change log

<!--
Add new entries in reverse-chronological order (newest at the top) in the format below.
Do not delete — preserve the history.
-->

## {{TODAY}} — Initial creation of the handoff package

- **Affected**: entire Registry (initial setup)
- **Change**: created the handoff package {{FEATURE_NAME}}-handoff/ via the `/handoff-publish` skill
- **Rationale**: applied HANDOFF_PROCESS_GUIDE v1.1 — establish the shared baseline for UX/UI/Dev/QA
- **Legacy ID conversion log** (SCR-NNN → 4-segment):
  <!-- Record the auto-conversion result from Step 2-B here -->
  - `SCR-001` → `{{DOMAIN_CODE}}-EXPERT-LIST`
  - `SCR-002` → `{{DOMAIN_CODE}}-EXPERT-LIST-EMPTY`
  - `SCR-003` → `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC01`
  - _(replace with the actual conversion list)_
- **Alternatives considered**: keep SCR-NNN + run alias in parallel → rejected (dual-maintenance burden)
- **Decider**: {{OWNER}}

---

<!-- Example entries (add real entries in the format below as decisions occur) -->

## 2026-04-24 — Hero CTA label change (example)

- **Affected**: `{{DOMAIN_CODE}}-HOME-HERO-CTA`
- **Before**: "Ask now"
- **After**: "Sign up and ask"
- **Rationale**: honest UX — button label should match the actual behavior (this is in fact a login gate)
- **Alternatives considered**: do not remove (Hero CTA is core to conversion)
- **Decider**: {{OWNER}}

---

## 2026-04-24 — Remove "Ask too" CTA from Expert Q&A bottom (example)

- **Affected**: `{{DOMAIN_CODE}}-HOME-EXPERT-QA-CTA`
- **Rationale**: duplicate CTA + login gate when not logged in → violates honesty
- **Alternatives considered**: relabel and keep → rejected (the top already has "See all")
- **Decider**: {{OWNER}}

---

## Change-management process (PDF §22)

When a change occurs, perform **all** of the following steps:

```
1. Update 1-screen-registry.md (mark changed IDs with 🔁 changed YYYY-MM-DD)
2. Add a decision entry in 11-decision-log.md (this file)
3. One-line summary of the change (reason + scope)
4. Share in the Slack #{{DOMAIN_CODE}}-design channel
5. For larger changes, add a 1–2 min Loom video
6. After UI/Dev acknowledge, mark ✅ acknowledged
```

---

## Decision-log template (copy and use)

```markdown
## YYYY-MM-DD — {decision title}

- **Affected**: {list of Screen IDs}
- **Before**: {prior state — label, component, policy, etc.}
- **After**: {changed state}
- **Rationale**: {why — user feedback / data / policy}
- **Alternatives considered**: {other options considered + why they were rejected}
- **Decider**: {name / role}
- **Slack share**: {link or message ID}
- **Loom link**: {optional — for larger changes}
```

---

_This file is **append-only**. Do not edit or remove past entries. If a reversal is required, record it as a new entry._
