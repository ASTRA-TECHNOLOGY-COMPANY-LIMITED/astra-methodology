# Branch Management at a Glance

> **Who is this for?** New hires encountering Git/PR for the first time — not just developers, but designers and PMs too
> **What will you take away?** A mental picture of "which line my change starts from and which line it ends up in"
> **What to memorize?** Not the commands — the **flow**

---

## 0. 5-Minute Summary — the Core Analogy

Think of the lines where code gathers as a **stage of a performance**.

| Line | Analogy | Description |
|------|---------|-------------|
| 🔴 **main** | Main stage | Our actual production service that customers see. Accidents are not allowed |
| 🟡 **staging** | Dress rehearsal | The last check before the main stage. "Is this OK to put in front of the audience?" |
| 🟢 **dev** | Practice room | Where every new piece of work first comes together. Merge freely, break things, rebuild |
| 🌿 **feat/fix/docs/...** | Personal practice rooms | Each person's space to build their own piece. Invisible from outside |

**Workflow**: bring work created in personal practice rooms → integrate in the practice room (dev) → rehearse in dress rehearsal (staging) → put it on the main stage (main).

---

## 1. End-to-End Flow (the big picture)

<!-- DIAGRAM:01-overview -->

**How to read**:
- Solid arrows (→) are **flows initiated by people**: open a PR, after verification "promote" to the next stage.
- Dotted arrows (⤴) are **flows the tool handles automatically** — specifically `staging → dev` only. Whenever `staging` is ahead of `dev` (typically right after a `dev → staging` promotion or a `staging`-branched hotfix), the tool syncs `dev` on every PR. `main → staging` is **not** auto-cascaded; `main` is touched only via the explicit `staging → main` promotion.

| Line | Who touches it? | How does it change? |
|------|-----------------|---------------------|
| Personal work branch | The owner | Save freely (commit) |
| dev | No one touches it directly | Only via **PR (merge request)** merges from a work branch |
| staging | Release lead | Only via dev → staging **promotion** |
| main | Release lead | Only via staging → main **promotion** |

> 💡 **Core**: dev / staging / main are **official lines**. Never modified directly — always entered via PR or promotion.

---

## 2. Shared Branches vs Work Branches

Branches fall into two broad characters.

<!-- DIAGRAM:02-shared-vs-work -->

| Category | Which branches | Direct save? | When are they created? |
|----------|----------------|---------------|------------------------|
| 🏛️ **Shared branches** | `main`, `staging`, `dev` | ❌ Changeable only via PR | Once, at repository creation |
| ✏️ **Work branches** | `feat/*`, `fix/*`, `docs/*`, `refactor/*`, `chore/*` | ✅ The owner can save freely | Every time new work begins |

**Why split them this way?**
- Touching a shared branch directly **suddenly changes the state others were looking at**. Unreviewed changes are a source of accidents.
- A work branch is your own space; you can mess it up and start over without consequence.

---

## 3. How is a Branch Name Decided?

ASTRA **ties three deliverable names with a single token**. When you see a PR, you can immediately trace "which sprint of which plan is this work for".

<!-- DIAGRAM:03-naming-trinity -->

### Four Naming Rules

| Position | Rule | Example |
|----------|------|---------|
| `{feature-name}` | Lowercase Latin + hyphens only (kebab-case). No Korean, uppercase, underscores ❌ | `payment`, `user-auth`, `checkout-flow` |
| `{NNN}` | Blueprint number. 3-digit (`001`, `002`, ...) | `003-payment` |
| `{N}` | Sprint sequence. No zero-padding (`1`, `2`, `3`, ...) | `sprint-2-payment` |
| `{prefix}` | The nature of the change (table below) | `feat/payment` |

### 5 Prefixes

| Prefix | When to use | Example |
|--------|-------------|---------|
| `feat/` | **Adding a new feature** (default for blueprint-based work) | `feat/payment` |
| `fix/` | **Bug fix** | `fix/login-error`, `fix/checkout-crash` |
| `docs/` | **Documentation only** (no code change) | `docs/onboarding-guide` |
| `refactor/` | Code **structural cleanup** (behavior unchanged) | `refactor/payment-module` |
| `chore/` | **Build/config/tooling** (unrelated to service behavior) | `chore/eslint-bump` |

### One-Line Traceability Example

> 📄 `docs/blueprints/003-payment/blueprint.md` (plan)
> → 🏃 `docs/sprints/sprint-2-payment/` (sprint progress record)
> → 🌿 `feat/payment` (work branch)
> → 📬 PR title: `feat: add payment feature`

💡 **Auto-decision**: the work branch name is generated automatically by the standard tool analyzing the nature of the change. You don't need to memorize the form — just remember the principle that **the `{feature-name}` should match the blueprint's**.

---

## 4. Concurrent Work in One Repository — Working-Area Isolation

### Why isolation is needed

Within the same repository on one computer, you sometimes want to **run multiple Claude Code sessions concurrently** for different tasks (e.g., payment feature + login bug + onboarding doc in parallel).

A plain `git checkout` cannot do this.
- The moment session A switches to `feat/payment` → all files session B was viewing change to different content.
- Session B will think its work has disappeared and panic.

### Solution: an independent folder per branch

<!-- DIAGRAM:04-worktree -->

Each work branch runs in **a separate folder inside the repository** (git worktree). Different folders → independent files.

### 4 Core Behaviors

1. **Main working area holds shared branches only** — the repo root always stays on one of `dev`/`staging`/`main`. Promotions and syncs happen here.
2. **Folder naming rule** — `/` in the branch name becomes `-`: `feat/payment` → `.astra-worktrees/feat-payment/`
3. **Auto-create, auto-clean** — when a work branch is created the folder is created with it; after a PR merge it is auto-removed.
4. **Left intact if halted** — if it's paused for conflicts or review, the folder does not disappear. Resume in place later.

> 💡 **Result**: one person can open two or three Claude sessions concurrently and work on payment, login, and docs side by side without conflict.

---

## 5. Cascade Sync — the Safety Net That Runs Every Time

### What happens?

**Right before** you open a PR, the tool syncs `staging → dev` so the integration line catches up with the verified release-candidate line.

<!-- DIAGRAM:05-cascade -->

> **Scope**: the auto-cascade is **only `staging → dev`**. `main → staging` is intentionally excluded — `main` is touched only via the explicit `staging → main` promotion. This keeps production code from leaking into the integration line outside the controlled release flow.

### Why every time?

If my `feat/login` branched off `dev` a week ago, lots of teammates' code has since landed on `dev`, and after the most recent promotion `staging` may also be ahead of `dev`. If you raise a PR in that state:

1. **Conflict explosion** — review flow breaks and time is wasted
2. **CI passes → breaks after merge** — verified against the old dev, so unreliable
3. **Release-candidate regression** — if a fix that landed on `staging` isn't reflected in `dev`, the same bug returns in the next sprint

**Cascade enforces "staging changes are always present in dev" as a rule on every PR**. The tool does it every time so people don't forget.

### What if there's a conflict?

Not auto-resolved — **the author resolves it directly**. Only a human knows the intent behind the code.

---

## 6. Why Bug Fixes Are Tricky — different origin, different route

Even with the same `fix/*` branch, **where it was found** changes the merge route completely.

<!-- DIAGRAM:06-bugfix -->

### One-Line Rule

> **Branch off the branch of the environment where you saw the bug and verify in the same environment.**

That's how you guarantee a precise fix of "the state I saw".

### Case A: bug on the dev environment (typical bug)

| Step | Content |
|------|---------|
| Where found? | `dev.fect.vn` (development integration environment) |
| Where to start? | `dev` branch |
| Where to verify? | `dev.fect.vn` |
| Where to merge? | `dev` (one place only) |

Same flow as normal feature development.

### Case B: staging/production bug (just-before or just-after release)

| Step | Content |
|------|---------|
| Where found? | `staging.fect.vn` or production (main) |
| Where to start? | `staging` branch |
| Where to verify? | `staging.fect.vn` |
| Where to merge? | `staging` + `main` + `dev` **all three** |

### Why does Case B merge in all three?

`staging` is about to become `main`. So if you fix on `staging` only:

| Missed place | Result |
|--------------|--------|
| Doesn't reach `main` | Production stays buggy (customer harm persists) |
| Doesn't reach `dev` | New code flows on the next sprint and **the same bug returns** (regression) |

**In other words, Case B = "the fixed place + upstream (main) + downstream (dev)" simultaneously**. Miss any and the same bug reappears days later.

### Never Do

- ❌ Saw the bug on `staging` but branched off `dev` — may not reproduce due to environment differences
- ❌ In Case B, merge only to `staging` — the "regression" above
- ❌ Treating Case B like Case A by going through `dev` only — the staging→main line stays exposed in the meantime

---

## 7. Promotion — who, when, what to check

> **⚠️ Company-specific policy — fill in with your team**

`dev → staging`, `staging → main` transitions are not ordinary merges but **promotions**. Putting something on the main stage is a decision, so the responsible person and timing must be defined.

| Transition | Who runs it? | When? | Pre-check |
|------------|--------------|-------|-----------|
| `dev → staging` | TODO (e.g., sprint lead) | TODO (e.g., 17:00 Thursday at sprint end) | TODO (e.g., E2E pass on dev, QA sign-off) |
| `staging → main` | TODO (e.g., release manager) | TODO (e.g., 10:00 every other Tuesday) | TODO (e.g., 48 hours of issue-free time on staging, release notes drafted) |

### Bumping the Version Number (SemVer)

At `staging → main` promotion, the release version is bumped by one. Like a magazine issue going from issue 1 → issue 2.

| Kind | Change | When |
|------|--------|------|
| `patch` | `1.2.3` → `1.2.4` | Bug fixes only |
| `minor` | `1.2.3` → `1.3.0` | New features added |
| `major` | `1.2.3` → `2.0.0` | Compatibility broken (rare) |

> **Decision criterion**: if existing users' code breaks → major; if a new feature → minor; otherwise → patch.

---

## 8. A One-Page Decision Tree

<!-- DIAGRAM:07-decision -->

It looks complex, but it boils down to three branches: **new feature / bug fix / release stage**.

---

## 9. Frequently Asked Questions (FAQ)

**Q. What if I'm in the middle of work and something else comes up?**
A. Leave the current work branch as-is and create another work branch to proceed. Working areas are isolated, so there's no effect (see §4).

**Q. What if a PR review surfaces Critical issues?**
A. **Any single remaining Critical issue blocks merge**. Fix and update the same PR.

**Q. Can I use forceful commands like `git push --force`?**
A. **Strictly forbidden** on shared branches (`main`/`staging`/`dev`). Allowed on your own work branch for your own PR, but normally unnecessary.

**Q. Confused about where to start from?**
A. Memorize the rule: **branch off the branch of the environment where you saw the bug**. If on `dev.fect.vn`, use `dev`; if on `staging.fect.vn` or production, use `staging`.

**Q. Cascade conflicts happen too often.**
A. Keep work branches short-lived. Branches unmerged for over a week are risky. **Small, frequent merges** are the right answer.

**Q. Should designers / PMs also create branches?**
A. **Yes**, if the deliverables they change (design tokens, planning documents) live in the repository. The tool handles branch creation on your behalf, so you don't need to memorize the commands — just understand the flow.

---

## 10. Onboarding-Week Checklist

- [ ] **Day 1**: read this document carefully and print one copy to keep by your desk
- [ ] **Days 2–3**: first PR with a mentor — focus on **where you branched from and where you merge to**
- [ ] **Days 4–5**: observe the `dev → staging` promotion process alongside someone
- [ ] **Week 2**: when the first `staging` bug occurs, practice the §6 Case B flow with a mentor
- [ ] **Ongoing**: return to this document whenever you get stuck — **memorize the flow, not the commands**

---

*Last updated: TODO (fill in date) | Maintainer: TODO (fill in name)*
