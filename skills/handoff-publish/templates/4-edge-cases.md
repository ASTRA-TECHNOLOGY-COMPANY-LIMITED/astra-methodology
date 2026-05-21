# 4. Edge Cases — Exception / Caution Cases

**Feature**: {{FEATURE_NAME}}
**Last updated**: {{TODAY}}

> The items below must be included; for each case specify the screen ID exposed, the handling policy, and the UX message.

---

## Required edge cases

- [ ] **Insufficient tokens / remaining count is 0**
  - When exposed: right before using a paid feature / when checking remaining balance during an API call
  - Screen exposed: `{{DOMAIN_CODE}}-EXPERT-MODAL02` (insufficient-tokens modal)
  - Message: "You don't have enough tokens. Recharge and try again. [Recharge]"
  - Handling: modal → "Recharge" → navigate to payment page / "Cancel" → return to previous screen

- [ ] **No permission** (not on the plan, expired, etc.)
  - When exposed: permission check on page entry
  - Screen exposed: `{{DOMAIN_CODE}}-EXPERT-MODAL-PERMISSION` or an upgrade-prompt page
  - Message: "This feature is available on the Pro plan. [Upgrade plan]"
  - Handling: server returns 403 → client displays upgrade-prompt UI

- [ ] **Not-logged-in block**
  - When exposed: clicking a feature that requires login
  - Screen exposed: `{{DOMAIN_CODE}}-EXPERT-MODAL-LOGIN`
  - Message: "Please log in to use this feature. [Log in]"
  - Handling: save the current URL as a `returnTo` parameter → return after login

- [ ] **No data** (EMPTY)
  - When exposed: API returns an empty array
  - Screen exposed: `{{DOMAIN_CODE}}-EXPERT-LIST-EMPTY` (and the EMPTY state of each list screen)
  - Message: "No questions yet. [Write your first question]"
  - Handling: a CTA prompting the next action is required

- [ ] **Network error**
  - When exposed: fetch failure / timeout
  - Screen exposed: the `-ERROR` state of each screen (`{{DOMAIN_CODE}}-EXPERT-LIST-ERROR`)
  - Message: "Connection is unstable. [Retry]"
  - Handling: retry button + auto-retry policy (up to 3 attempts, exponential backoff)

- [ ] **State transitions** (waiting → adopted, recruiting → closed, etc.)
  - Example: `UC02 → UC03` transition when an answer is adopted
  - Exposure policy: decide between real-time update vs. update after refresh
  - UX: feedback via animation / toast on transition

- [ ] **Self vs. other UI differences**
  - Example: edit/delete menu shown only to the question owner
  - Implementation: conditional render after `user.id === post.authorId` check
  - Server validation: permissions must also be re-validated on the server

- [ ] **Demo mode** (preview when not logged in)
  - When exposed: a not-logged-in user enters via "Try it" etc.
  - Data: mock data (no real DB queries)
  - Constraint: data-mutation actions (write/delete/adopt, etc.) are disabled
  - CTA: "To actually use this, [Log in]"

---

## Additional edge cases (feature-specific)

<!-- TODO (UX): add edge cases specific to this feature below -->

- [ ] **Concurrency conflict**
  - Example: multiple users simultaneously try to adopt an answer on the same question
  - Policy: server accepts the first-arriving request; others get a 409 response
  - UX: "Another answer has already been adopted. Please refresh."

- [ ] **Large data volumes**
  - Example: a single question has more than 100 answers
  - Policy: pagination or infinite scroll (default 20 items)
  - UX: when answer count exceeds the threshold, show a "Load more" button

- [ ] **Text length exceeded**
  - Example: title exceeds 200 characters
  - Policy: real-time count on the client + server-side validation
  - UX: "You can enter up to 200 characters."

- [ ] **Inappropriate content (report accumulation)**
  - Example: an answer that exceeds the report threshold
  - Policy: auto-blind (restored or removed after admin review)
  - UX: "This answer has been hidden due to reports. [Expand]"

---

## Edge-case verification checklist (QA reference)

| # | Case | Trigger path | Expected result | Test ID |
|---|------|--------------|------------------|---------|
| 1 | Insufficient tokens | Remaining tokens < 1 when writing a question | MODAL02 shown + recharge prompt | — |
| 2 | No permission | Free plan accesses a Pro feature | upgrade prompt | — |
| 3 | Not logged in | Click "Ask" while not logged in | MODAL-LOGIN shown | — |
| 4 | EMPTY | First entry, zero data | EMPTY state + CTA | — |
| 5 | ERROR | API call while network is offline | ERROR state + retry | — |
| 6 | Concurrency | Adopt simultaneously from 2 browsers | only one succeeds, the other gets 409 | — |

---

_Update this list whenever a missing edge case is discovered. The discoverer adds the item directly and records it in `11-decision-log.md`._
