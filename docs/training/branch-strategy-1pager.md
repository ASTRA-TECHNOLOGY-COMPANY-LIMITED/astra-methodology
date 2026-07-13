# Branch Management Strategy 1-Pager (ASTRA)

> **Audience**: new hires encountering Git/PR workflows for the first time
> **Core message**: what you need to memorize is not commands but **"which branch do I start from, and where do I merge to"**.

---

## 1. End-to-End Flow (single diagram)

```
   ┌──────────────────────── isolated working area ────────────┐
   │   feat/login                                                │
   │   ┌──────────────┐                                          │
   │   │  my work     │ ← code here                              │
   │   └──────┬───────┘                                          │
   └──────────┼──────────────────────────────────────────────────┘
              │  Pull Request
              ▼
        ┌──────────┐   promotion (dev→staging)   ┌──────────┐   promotion (staging→main)   ┌──────────┐
        │   dev    │ ──────────────────────────► │ staging  │ ───────────────────────────► │   main   │
        │ (integ.) │                             │ (verify) │                              │ (release)│
        └────▲─────┘                             └────┬─────┘                              └──────────┘
             │                                        │
             │ ◄── cascade merge: staging → dev only, automatic on every PR ──
             └────────────────────────────────────────┘
                       changes on staging always flow down to dev
                       (main → staging is never auto-cascaded)
```

**4-tier flow**: `feature → dev → staging → main`. Code is promoted top-to-bottom by people. **Only `staging → dev` is auto-cascaded on every PR** so the integration line catches up with the verified release-candidate line. `main → staging` is not auto-cascaded — `main` is touched only through the explicit `--main` promotion.

Role of each branch:

| Branch | Role | How it changes |
|--------|------|----------------|
| `feat/*`, `fix/*`, `docs/*`, `refactor/*`, `chore/*` | Individual work | Committed to directly by the author |
| `dev` | Integration line where all work gathers | Via PR merges only |
| `staging` | Release verification line | Via promotion only |
| `main` | Production release | Via promotion only |

---

## 2. Shared Branches vs Work Branches — this is the key split

| Category | Branch | Direct commit | When created |
|----------|--------|---------------|--------------|
| **Shared branch** | `main`, `staging`, `dev`, `master` | **Forbidden** (PR only) | Once, at repository init |
| **Work branch** | `feat/*`, `fix/*`, `docs/*`, `refactor/*`, `chore/*` | OK (your own branch) | Every time a new piece of work starts |

### Work Branch Naming — tied to the blueprint and sprint with the same single word

ASTRA links the **blueprint directory name, sprint directory name, and work branch name** with the same `{feature-name}` single token. The purpose is that, given a PR, you can instantly tell "which sprint of which blueprint is this work for".

| Deliverable | Path/Name format | Concrete example |
|-------------|------------------|------------------|
| Blueprint | `docs/blueprints/{NNN}-{feature-name}/blueprint.md` | `docs/blueprints/003-payment/blueprint.md` |
| Sprint | `docs/sprints/sprint-{N}-{feature-name}/` | `docs/sprints/sprint-2-payment/` |
| Work branch | `{prefix}/{feature-name}` | `feat/payment`, `fix/payment-overflow` |

**Four rules**:

1. **`{feature-name}`**: kebab-case, lowercase Latin + hyphens only (e.g., `user-auth`, `payment-checkout`). No Korean, uppercase, or underscores.
2. **`{NNN}`**: blueprint number. 3-digit zero-padded (`001`, `002`, `003`...). The largest existing number in the repository + 1.
3. **`{N}`**: sprint sequence (`1`, `2`, `3`...). No zero-padding.
4. **`{prefix}`**: chosen by the nature of the change.

| Prefix | When to use | Example |
|--------|-------------|---------|
| `feat/` | Adding a new feature — default for blueprint-based work | `feat/payment` |
| `fix/` | Bug fix | `fix/login-error`, `fix/checkout-crash` |
| `docs/` | Documentation only (no code change) | `docs/onboarding-guide` |
| `refactor/` | Behavior-preserving structural improvement | `refactor/payment-module` |
| `chore/` | Build/config/tooling (unrelated to app behavior) | `chore/eslint-bump` |

**One-line matching example**: `docs/blueprints/003-payment/blueprint.md` (blueprint) → `docs/sprints/sprint-2-payment/` (sprint) → `feat/payment` (branch) → PR title `feat: add payment feature`.

> **Auto-decision**: the work branch name is determined automatically by the standard tool analyzing the nature of the change (e.g., new file added → `feat/`, existing file modified + test → `fix/`). You do not need to make it yourself.

### Working-Area Isolation — multiple Claude Code sessions concurrently in the same repository

In the same local repository on one computer, you can **run multiple Claude Code sessions in parallel** to work on different things. A plain `git checkout` cannot do this — the moment session A checks out `feat/payment`, all files in session B's working directory change, and session B's in-progress code appears to vanish.

ASTRA solves this by placing **a separate OS-level directory** (git worktree) for each work branch:

```
repo root/                            ← main worktree: always on dev/staging/main
├── .worktrees/                ← per-work-branch isolated directories
│   ├── feat-payment/                ← Claude session A working here (feat/payment)
│   └── fix-login-error/             ← Claude session B working here (fix/login-error)
├── src/
└── ...
```

Each directory is an independent working tree, so while session A edits payment code, session B can edit login code and **neither's files affect the other**.

**Four core behaviors**:

1. **Main worktree holds only shared branches** — the repo root always stays on one of `dev`/`staging`/`main`/`master`. Cascade merges and promotions happen here.
2. **Isolated directory naming rule** — replace `/` in the branch name with `-`. Example: `feat/payment` → `.worktrees/feat-payment/`.
3. **Auto-create, auto-clean** — when you start a new work branch, the worktree is also created; after a PR is merged it is automatically removed and the main worktree returns to `dev`.
4. **Left intact if interrupted** — if the workflow is halted (conflicts, review pending), the worktree is not automatically cleaned and stays put so you can resume in the same place later.

> **Result**: one person can open two or three Claude sessions and work on payment, login, and docs simultaneously without conflicts.

### Never Do

- ❌ Direct `git commit` to `main`/`staging`/`dev` — always via PR
- ❌ `git checkout main` and coding there — branch off into a work branch first
- ❌ Creating a PR directly on the GitHub web — go through the standard tool so cascade and verification are wired automatically
- ❌ Creating or deleting `.worktrees/` by hand — automatically managed
- ❌ Using Korean, uppercase, or underscores in branch names (forbidden: `feat/결제`, `feat/Payment_Module`)
- ❌ Creating a branch with a `{feature-name}` different from the blueprint's — traceability is lost

---

## 3. Cascade Merge — the invariant every PR follows

The following sync must always happen **before** a PR is created:

```
   fetch remote
        │
        ▼
   merge staging into dev    ──► push dev
        │
        ▼
   merge dev into my work    ──► PR can now be created safely
   branch
```

> **Scope**: the auto-cascade is **only `staging → dev`**. `main → staging` is intentionally excluded — `main` is touched only via the explicit `--main` promotion. This protects production code on `main` from being mixed into the integration line outside the controlled release flow.

### Why is this done every time?

If my `feat/login` branched off `dev` a week ago, plenty of teammates' code has since landed on `dev`, and after the latest promotion `staging` may also be ahead of `dev`. If you raise a PR in that state:

1. Conflicts explode on the PR → review flow breaks
2. CI may pass against the old `dev` but break after merge
3. If a release-candidate fix landed on `staging` but is not reflected in `dev`, it regresses in the next sprint

**Cascade enforces the invariant "staging changes are always reflected in dev" on every PR**. The tool does it every time so people don't forget.

### What if there's a conflict?

When a conflict occurs during cascade, **it is not auto-resolved** — the author resolves it manually, then proceeds. Only a human knows the intent behind code.

---

## 4. Bug Fixes (`fix/*`) — different origin, different merge route

Even with the same `fix/*` branch, **where it was branched from** changes test environment and merge target. The criterion is "**in which environment was the bug observed**".

| Situation | Branch origin | Test environment | Merge target |
|-----------|---------------|------------------|--------------|
| Bug found in development integration | `dev` | `dev.fect.vn` | `dev` |
| Bug found in release verification / production | `staging` | `staging.fect.vn` | `staging` → `dev` → `main` (all three) |

### Environment domain = branch origin (when confused, use this table)

| Where you saw the bug | Branch from | Verify in |
|-----------------------|-------------|-----------|
| Local / `dev.fect.vn` | `dev` | `dev.fect.vn` |
| `staging.fect.vn` / production (`main`) | `staging` | `staging.fect.vn` |

> **Rule**: branch off the branch of the environment where you saw the bug, and verify in the same environment. That gives the guarantee that "the state I saw" is what gets fixed.

### Case A — `dev` branch (typical bug)

```
   dev ──► fix/login-error ──► verify on dev.fect.vn ──► PR ──► merge to dev
```

A typical bug found by QA/dev in the integration environment. Same flow as normal feature development.

### Case B — `staging` branch (just-before/after-release bug)

```
   staging ──► fix/checkout-crash ──► verify on staging.fect.vn
                                              │
                                              ▼
                                        ┌──► staging  (fix the current release candidate)
                                        ├──► main     (reflect into production — emergency release)
                                        └──► dev      (prevent regression in the next sprint)
```

**Why merge to all three?**

`staging` is about to become `main`. So if you fix only on `staging`:

1. **If it never reaches `main`** → production stays buggy
2. **If it never reaches `dev`** → in the next sprint, new code flows `dev`→`staging` and the same bug returns (regression)

In other words, Case B must be flowed in "the fixed place + upstream (main) + downstream (dev)" three directions at once to be safe. Miss any and the same bug reappears days later.

### Never Do

- ❌ Saw the bug in `staging` but branched from `dev` — may not reproduce due to environment differences
- ❌ In Case B, merge only to `staging` and skip the `main`/`dev` backports — causes the "regression" above
- ❌ Treating Case B like Case A by going through `dev` only — the `staging`→`main` line stays exposed in the meantime

---

## 5. Promotion Timing & Authority

> **⚠️ Company-specific policy — fill in directly**

`dev → staging`, `staging → main` transitions are not ordinary merges but **promotions**. Who runs them, when, and what is checked must be defined as a team policy.

| Transition | Who runs it? | When? | Pre-check items |
|------------|--------------|-------|-----------------|
| `dev → staging` | TODO: (e.g., sprint lead) | TODO: (e.g., 17:00 Thursday at sprint end) | TODO: (e.g., E2E pass on dev, QA sign-off) |
| `staging → main` | TODO: (e.g., release manager) | TODO: (e.g., 10:00 every other Tuesday) | TODO: (e.g., 48 hours of issue-free time on staging, release notes drafted) |

### Version Bump (SemVer)

At `staging → main` promotion, the release version is bumped.

- `patch`: `1.2.3 → 1.2.4` — bug fixes only
- `minor`: `1.2.3 → 1.3.0` — new features added
- `major`: `1.2.3 → 2.0.0` — compatibility broken

> **Decision criterion**: if existing users' code breaks it's major; if it's a new feature it's minor; otherwise it's patch.

---

## 6. One-Line Decision Tree

```
What are you about to do?
├── add a new feature                            →  branch feat/* off dev
├── fix a bug found on dev                       →  branch fix/* off dev, verify on dev.fect.vn, merge to dev
├── fix a bug found on staging/production        →  branch fix/* off staging, verify on staging.fect.vn,
│                                                     merge to all three of staging + main + dev
├── sprint ends, start release verification      →  promote dev → staging
└── release (production deploy)                  →  promote staging → main + SemVer bump
```

---

## 7. Frequently Asked Questions (FAQ)

**Q. What if another piece of work interrupts the current one?**
A. Leave the current work branch as-is and branch off a new work branch to proceed. Working areas are isolated, so there is no interference.

**Q. What if a PR review surfaces Critical issues?**
A. **Any single remaining Critical issue blocks merge**. Fix and update the same PR.

**Q. Can I use `git push --force`?**
A. **Strictly forbidden** on shared branches (`main`/`staging`/`dev`). Allowed on your own work branch for your own PR, but normally unnecessary.

**Q. Confused about where to branch from?**
A. Memorize the rule: **branch off the branch of the environment where you saw the bug**. If on `dev.fect.vn`, use `dev`; if on `staging.fect.vn`, use `staging`.

**Q. Cascade conflicts happen too often.**
A. Keep work branches short-lived. Branches that go unmerged for over a week are risky. **Small, frequent merges are the right answer**.

---

## Next Steps (post-training)

1. Day 1 as a new hire: print this document and keep it by your desk
2. First PR: walk through it step by step with a mentor — focus on **where it branched from and where it merges to**
3. End of week 1: observe a `dev → staging` promotion alongside someone
4. When your first `staging`-branched bug occurs: practice the §4 Case B flow with a mentor
5. Return to this document whenever you get stuck — **what to memorize is the flow, not the commands**

---

*Last updated: TODO (fill in date) | Maintainer: TODO (fill in name)*
