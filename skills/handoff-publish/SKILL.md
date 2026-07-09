---
name: handoff-publish
description: "Generates a handoff package (`{feature}-handoff/` at the branch root) for UX/UI/Dev/QA collaboration. Identifies screens via the 4-segment Screen ID scheme (DOMAIN-PAGE-SECTION-UC) and composes 11 documents centered on the SSoT `1-screen-registry.md` (state matrix, edge cases, responsive, component specs, business rules, UX writing, IA/sitemap, personas, Decision log). If service-planner deliverables exist, they are automatically converted and reused."
argument-hint: "[feature-name or planner directory name]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Skill
---

# ASTRA Handoff Package Auto-Generator

Generates a **Screen-ID-centric collaboration package** based on HANDOFF_PROCESS_GUIDE v1.1.

**Core principles (PDF §6)**:
- **Screen-ID-based collaboration**: every screen is identified by a unique ID in the `DOMAIN-PAGE-SECTION-UC{NN}` format
- **Single Source of Truth (SSoT)**: `1-screen-registry.md` is the sole source for every ID (only UX has issuance authority)
- **State-based design**: every screen is defined as a combination of State × Permission × Device

**Output location**: the `{feature}-handoff/` folder at the branch root (per PDF §8 structure)

**Deliverables (14 files + screenshots/)**:

| # | File | Role |
|---|------|------|
| 0 | `0-README.md` | this guide + Quick Start |
| 1 | `1-screen-registry.md` | **SSoT** — Screen Registry |
| 2 | `2-flows.md` | user-flow definitions |
| 3 | `3-state-matrix.md` | state × permission matrix |
| 4 | `4-edge-cases.md` | exception / caution cases |
| 5 | `5-responsive-guide.md` | responsive baseline |
| 6 | `6-component-specs.md` | card/component spec (data anatomy) |
| 7 | `7-business-rules.md` | per-screen business rules / exposure policy |
| 8 | `8-content-guide.md` | UX writing + data display rules |
| 9 | `9-ia-sitemap.md` | information architecture / sitemap |
| 10 | `10-personas.md` | personas / key scenarios |
| 11 | `11-decision-log.md` | design decision history |
| — | `DoD-CHECKLIST.md` | Definition of Done checklist per role |
| — | `walkthrough.loom.md` | walkthrough video link (manually entered) |
| — | `screenshots/` | captures keyed by Screen ID |

> **LANGUAGE RULE**: Before executing this skill, read the project's `CLAUDE.md` and check the `## Language` section to detect the project language. If the project language is NOT Korean (`ko`), translate ALL user-facing output — prompts, messages, generated headers, table labels, descriptions — into the project language. Technical identifiers (Screen IDs, file names, code snippets) remain untranslated.

---

## Out of Scope (PDF §24 — cases where this process is not applied)

The handoff process is **not** applied in the following cases. Confirm with the user explicitly at the start of Step 0:

- One-off marketing / event pages
- Quick prototype / A-B test screens
- External embedded pages (Notion / Slack embeds, etc.)
- Back-office admin screens (when UX collaboration is not needed)

If a case matches, exit this skill early and Recommended `/blueprint` or direct implementation instead.

Also, **do not apply retroactively to existing features** (PDF §26). Apply gradually only at major renewal points.

---

## Procedure

### Step 0: Out-of-Scope confirmation

Confirm via `AskUserQuestion`. If any item matches, exit the skill early:

```
## Handoff scope confirmation

This handoff process applies only to a product's core screens (long-lived screens with multi-role collaboration).
Does any of the following apply?

1. One-off marketing / event page
2. Quick prototype / A-B test
3. External embedded page
4. Back-office admin (no UX collaboration needed)
5. None of the above (proceed normally)
```

If 1–4 is chosen:
```
The handoff process is not applied to this screen.
The following workflow is Recommended instead:
- Write a blueprint: /blueprint {feature-slug}
- After sprint start, implement: /sprint-init → /feature-dev "..."
Exiting.
```
→ End the skill.

If 5 is chosen, proceed to Step 1.

---

### Step 1: Argument parsing and feature-context collection

#### A. Parse `$ARGUMENTS`

| Argument form | Behavior |
|---------------|----------|
| Planner directory name (e.g., `001-auth`) | Use `docs/planner/{dir}/` and `docs/blueprints/{dir}/` as context |
| feature-name in kebab-case (e.g., `expert-qa`) | Set the feature as the subject; search for the planner directory |
| (none) | Scan `docs/planner/` and pick via `AskUserQuestion` |

Save the selected feature-name as `{FEATURE_NAME}`.

#### B. Determine the Domain Code

The first segment of the Screen ID (`DOMAIN`) is the **product abbreviation**. Examples:
- FECT Academy → `ACAD`
- FECTQ → `FECTQ`
- AMA payments → `PAY`

Read the project name / domain from `CLAUDE.md`, present candidates, and confirm `{DOMAIN_CODE}` (2–6 uppercase characters) via `AskUserQuestion`. This domain code is used consistently across every screen ID thereafter.

> If an existing handoff package exists, auto-extract DOMAIN from that folder's `1-screen-registry.md`.

#### C. Load existing deliverables (use if present; otherwise scaffold)

If the following files exist, read them and reflect them in the handoff files:

| Source | Mapping target |
|--------|----------------|
| `docs/planner/{NNN}-{feature}/ia-screen-design.md` | `1-screen-registry.md`, `9-ia-sitemap.md`, `2-flows.md` |
| `docs/planner/{NNN}-{feature}/interview-report.md` | `10-personas.md` |
| `docs/planner/{NNN}-{feature}/requirements-definition.md` | draft exposure policy for `7-business-rules.md` |
| `docs/planner/{NNN}-{feature}/feature-definition.md` | `7-business-rules.md`, permission matrix in `3-state-matrix.md` |
| `docs/blueprints/{NNN}-{feature}/blueprint.md` | API/data policy in `7-business-rules.md` |
| `docs/design-system/DESIGN.md` | `6-component-specs.md` (SSoT — reference Front Matter tokens + Body §4 component guidelines via reference links) |
| `docs/design-system/components.md` | `6-component-specs.md` (legacy fallback — used only when DESIGN.md is absent) |

> If none are present, create an empty scaffold and leave TODO comments for UX/PM to fill. In this case, the AI auto-fill in Steps 5–10 is skipped.

#### D. Determine the output directory

Default: `{FEATURE_NAME}-handoff/` at the branch root (e.g., `fect-academy-handoff/`).

If it already exists, `AskUserQuestion`:
- Keep + update (default)
- Delete and recreate
- Abort

Confirm `{HANDOFF_DIR}`.

#### E. Switch to the dev branch and sync to latest

Before creating deliverable files, switch to the `dev` branch and synchronize to the latest. Do not create a work branch; work directly on `dev`. Work-branch creation is handled automatically when `/pr-merge` runs.

0. **Main-worktree guard**: if called from inside an isolated worktree (`.astra-worktrees/<slug>/`), abort. dev-sync runs only in the main worktree:
   ```bash
   PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(find ~/.claude/plugins/cache -maxdepth 3 -type d -path '*/astra-methodology/*' 2>/dev/null | sort -V | tail -1)}"
   if [ -z "$PLUGIN_ROOT" ] || [ ! -f "$PLUGIN_ROOT/scripts/worktree-helpers.sh" ]; then
     echo "ERROR: CLAUDE_PLUGIN_ROOT not found. Check the plugin cache path." >&2
     exit 1
   fi
   source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"
   astra_ensure_main_worktree || exit 1
   ```
1. **Check the current branch**: `git branch --show-current`
2. **Skip if already on `dev`**: if the current branch is `dev`, skip steps 3–5 below and just pull (`git pull origin dev`)
3. **Preserve uncommitted changes**: check with `git status --porcelain`; if changes exist, stash temporarily via `git stash --include-untracked` (untracked files included)
4. **Switch to dev and sync**: `git fetch origin dev && git checkout dev && git pull origin dev`
5. **Restore stash**: if you stashed in step 3, restore via `git stash pop`. On conflict, report the conflicting files to the user and request manual resolution.

> **Note**: if the `dev` branch does not exist, work on `main` or `master`. If none of those default branches exist, work on the current branch.

---

### Step 2: Design the Screen ID issuance scheme

Every screen gets a unique ID in the `{DOMAIN}-{PAGE}-{SECTION}-UC{NN}` format (e.g., `ACAD-EXPERT-DETAIL-UC03`). `DOMAIN` is from Step 1-B; `PAGE` is the route unit; `SECTION` is the screen type (LIST/DETAIL/FORM/MODAL...); `UC{NN}` is the state/case discriminator. State suffixes `-LOADING`/`-EMPTY`/`-ERROR` may replace `UC`.

Three tasks in this step:
1. Issue IDs for all screens per the format above.
2. Convert any legacy `SCR-NNN` IDs from `ia-screen-design.md` and log the old/new mapping in `11-decision-log.md`.
3. Ensure the required-screen set (all states, all modals, edge cases, hidden URL-param screens) is covered — warn and add placeholders for any missing.

Detailed format rules, the SCR-NNN conversion algorithm, and the required-screen checklist with the missing-screen warning: see [references/screen-id-scheme.md](references/screen-id-scheme.md). Read it before issuing IDs.

---

### Step 3: Copy templates and substitute variables

Copy all files (14 templates) from `$CLAUDE_PLUGIN_ROOT/skills/handoff-publish/templates/` to `{HANDOFF_DIR}`, and substitute the following variables:

> Copy targets: `0-README.md` (1), `1-screen-registry.md` ~ `11-decision-log.md` (11), `DoD-CHECKLIST.md`, `walkthrough.loom.md`.

| Variable | Value |
|----------|-------|
| `{{FEATURE_NAME}}` | feature-name from Step 1 |
| `{{DOMAIN_CODE}}` | domain code from Step 1-B |
| `{{TODAY}}` | today's date (YYYY-MM-DD) |
| `{{OWNER}}` | project UX Lead (collected from CLAUDE.md or via `AskUserQuestion`) |
| `{{PROJECT_NAME}}` | project name from CLAUDE.md |
| `{{LANGUAGE_POLICY}}` | project i18n language list (default: `ko / en / vi`) |

Also create an empty `screenshots/` directory (`walkthrough.loom.md` is already copied via the templates).

---

### Steps 4–12: Auto-fill each handoff document

Fill the 14 files in order, sourcing from the deliverables loaded in Step 1-C. Each step below is one document group; the exact table columns, tree formats, and PDF-section templates for each live in [references/document-autofill-specs.md](references/document-autofill-specs.md) — **read it before writing each document.**

| Step | Document(s) | Fill from | Fallback when no planner doc |
|------|-------------|-----------|------------------------------|
| 4 | `1-screen-registry.md` | `ia-screen-design.md` screen list → 4-segment Registry rows | 4 placeholder rows (PDF §9.1) |
| 5 | `2-flows.md` | `usecase-definition.md` journey map → tree with success/failure/exception branches | — |
| 6 | `3-state-matrix.md`, `4-edge-cases.md` | `feature-definition.md` permission table + risk section | template state defs + 8 base edge cases |
| 7 | `5-responsive-guide.md` | DESIGN.md `tokens.breakpoints` (fallback: design-tokens.css) | PDF §12 breakpoints as-is |
| 8 | `6-component-specs.md` | DESIGN.md Body §4 (1st) / `components.md` (fallback) + `feature-definition.md` UI elements | 4 card scaffolds + Modal |
| 9 | `7-business-rules.md` | `blueprint.md` API endpoints → data-source rows | empty PDF §15.1 blocks per ID |
| 10 | `8-content-guide.md` | PDF §16–17 as-is; `{{LANGUAGE_POLICY}}` substitution | — |
| 11 | `9-ia-sitemap.md`, `10-personas.md`, `11-decision-log.md` | `ia-screen-design.md` menu tree, `interview-report.md` personas, Step 2 conversion log | template as-is |
| 12 | `0-README.md`, `walkthrough.loom.md`, `DoD-CHECKLIST.md` | verify `{{FEATURE_NAME}}`/`{{DOMAIN_CODE}}` substitution only | template as-is |

---

### Step 13: Report results to the user

Report in the following format:

```
✅ Handoff package generation complete

Location: {HANDOFF_DIR}
Domain code: {DOMAIN_CODE}
Registered Screen IDs: {N}

Generated files:
  0-README.md
  1-screen-registry.md ({N} IDs registered)
  2-flows.md ({N} Flows defined)
  3-state-matrix.md
  4-edge-cases.md
  5-responsive-guide.md
  6-component-specs.md ({N} components)
  7-business-rules.md
  8-content-guide.md
  9-ia-sitemap.md
  10-personas.md ({N} personas)
  11-decision-log.md ({N} conversion records)
  DoD-CHECKLIST.md
  walkthrough.loom.md
  screenshots/

⚠️ Sections with limited auto-fill (UX must supplement directly):
  - 1-screen-registry.md: review state/trigger consistency
  - 3-state-matrix.md: permission matrix (per feature)
  - 6-component-specs.md: props of feature-specific components
  - 10-personas.md: refine based on real interviews

Next steps (PDF §7 Quick Start):
  1. UX: verify and fill in every ID in 1-screen-registry.md
  2. UI: author Figma frame names in the Screen ID format
  3. Dev: add `// @feature: {SCREEN-ID}` comments to components
  4. UX: record the Loom walkthrough (5–10 min)

DoD checks are in PDF §19. A `/check-dod` command is planned.
```

---

## Anti-patterns (PDF §23)

The 10 problems this skill prevents (missing modals, undefined per-state UI, missing mobile, split Figma/code IDs, one-sided changes, etc.) are catalogued in the Appendix of [references/document-autofill-specs.md](references/document-autofill-specs.md). Consult it if unsure why a document is mandated.

---

## Caveats

- **Forbidden to issue an ID without registering** (PDF §20): if UI/Dev discover one, request UX to add it
- **Screen ID issuance is UX's sole authority**: do not edit `1-screen-registry.md` outside of this skill (will be enforced via a future `/register-screen` command)
- **No retroactive application to existing features**: apply only to new features or at major renewal points (PDF §26)
