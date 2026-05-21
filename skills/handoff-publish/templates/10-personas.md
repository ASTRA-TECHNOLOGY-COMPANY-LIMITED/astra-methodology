# 10. Personas — Personas / Key Scenarios

**Feature**: {{FEATURE_NAME}}
**Last updated**: {{TODAY}}

> **Why is this needed?** If designers/developers don't know **"who uses it and why"**, they work under wrong assumptions. The basis for prioritization disappears.

---

## What to include

- Personas (Top 3–5)
- Each persona's goal / pain points / usage context / device
- Core usage scenarios (Top 5–10)
- Priority (Must-have vs. Nice-to-have scenarios)

---

## Personas

### [Persona P1] Junior trade practitioner (primary)

| Item | Content |
|------|---------|
| Age / experience | 27 years old, 1–2 years at a trade company |
| Goal | Acquire knowledge immediately applicable to work |
| Pain points | Doesn't know which course to take first / fragmented info even after searching |
| Usage context | Quick info lookup during work + after-hours learning |
| Device | Desktop 60% / Mobile 40% |
| Main features | Search, course enrollment, Q&A asking |

**Decision criterion**: UX decisions are made giving top priority to P1.

---

### [Persona P2] Senior trade expert (answerer)

| Item | Content |
|------|---------|
| Age / experience | 10+ years, has Q&A-answer permission |
| Goal | Recognition of expertise + side income (points) |
| Pain points | Repetitive beginner questions / no feedback even after answering (low adoption rate) |
| Usage context | Idle minutes during work (5–10 min) |
| Device | Mostly desktop (writes long answers) |
| Main features | Write answers, dashboard (revenue/adoption rate), notifications |

---

### [Persona P3] Training manager (B2B)

| Item | Content |
|------|---------|
| Age / experience | 35 years old, HR training manager at a large enterprise |
| Goal | Build a training curriculum for employees |
| Pain points | Variance in individual course quality / hard to track per-employee learning history |
| Usage context | Intensive use 1–2 times per month |
| Device | Mostly desktop |
| Main features | Course curation, team learning-status reports |

---

## Core scenarios — Top 3

### S1. "Verify FTA origin criteria"
```
Persona: P1 (junior trade practitioner)
Trigger: needs the FTA origin criteria for a specific item during work
Flow:
  Home → enter Trade Tools → input HS Code → look up FTA origin criteria
  (no result) → search Q&A → find similar questions → check answers
  (insufficient answers) → write a question
Priority: Must-have
Related screens: {{DOMAIN_CODE}}-TOOLS-FTA, {{DOMAIN_CODE}}-EXPERT-LIST, {{DOMAIN_CODE}}-EXPERT-WRITE
```

### S2. "No answer for a specific case"
```
Persona: P1
Trigger: an edge case that search/tools can't resolve
Flow:
  Expert Q&A → write question → wait for answer → receive notification → check answer → adopt
Priority: Must-have
Related screens: {{DOMAIN_CODE}}-EXPERT-WRITE, {{DOMAIN_CODE}}-EXPERT-DETAIL-UC01, UC02, UC03
```

### S3. "Brand new to this field, where do I start?"
```
Persona: P1 (complete beginner within the junior tier)
Trigger: first week on the job
Flow:
  Home → recommended courses section → course detail → apply → enroll
Priority: Must-have
Related screens: {{DOMAIN_CODE}}-HOME, {{DOMAIN_CODE}}-COURSES-LIST-POPULAR, {{DOMAIN_CODE}}-COURSES-DETAIL
```

---

## Core scenarios — Top 5–10 (extended)

### S4. "Receiving feedback after writing an answer" (P2)
- Write answer → adoption/upvote notification → check revenue on dashboard
- Priority: Must-have
- Related screens: `{{DOMAIN_CODE}}-EXPERT-DETAIL-UC02`, `{{DOMAIN_CODE}}-EXPERT-DASHBOARD`

### S5. "Download employee-learning report" (P3)
- Admin dashboard → team learning report → Excel download
- Priority: Nice-to-have (when B2B expands)
- Related screens: `{{DOMAIN_CODE}}-ADMIN-TEAM-REPORT`

### S6. "Quick check on mobile while commuting" (P1)
- Bottom Tab → Q&A → new-answer notification → read answer
- Priority: Must-have
- Related screens: every Mobile `-M` suffix ID

### S7. "Find a desired course via search" (P1, P3)
- Global search → category filter → select course
- Priority: Must-have

### S8. "Delete a question" (P1)
- Own question detail → menu → delete → confirm modal → delete
- Priority: Should-have
- Related screens: `{{DOMAIN_CODE}}-EXPERT-MODAL01`

---

## Priority (Must-have vs. Nice-to-have)

### Must-have (MVP)
- S1, S2, S3, S4, S6, S7

### Should-have (v1.1)
- S8 (delete question)
- Edit question
- Report answer

### Nice-to-have (v1.2+)
- S5 (B2B report)
- Scheduled answer drafting
- AI answer-draft suggestions

---

## Principles

- **For design/development decisions, present the rationale as "For P1, …"**
- **When a user group not in the personas appears**, → add it after UX review
- **Flows not in the core scenarios are treated as Nice-to-have** (out of MVP scope)

---

_TODO (UX): Update the personas above with the actual interview results. If there is no interview basis, state "hypothesis-based" and include the validation plan._
