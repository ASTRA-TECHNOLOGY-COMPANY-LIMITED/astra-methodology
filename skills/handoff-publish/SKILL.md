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
   PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
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

#### A. Screen ID format (PDF §6.1)

```
{DOMAIN}-{PAGE}-{SECTION}-UC{NN}
────   ─────   ───────   ────
domain page    section   use-case number (2 digits)

Example: ACAD-EXPERT-DETAIL-UC03
         ACAD-EXPERT-LIST
         ACAD-EXPERT-LIST-EMPTY
         ACAD-EXPERT-MODAL01
```

Detailed rules:
- `DOMAIN`: product abbreviation (decided in Step 1-B)
- `PAGE`: menu/route unit (uppercase Latin letters; hyphens allowed when necessary)
- `SECTION`: screen type — LIST / DETAIL / FORM / MODAL / DASHBOARD / SETTINGS, etc. Omit if not needed.
- `UC{NN}`: **state/case discriminator** on the same page (e.g., UC01=default, UC02=before adoption, UC03=adopted)
- State suffix: `-LOADING`, `-EMPTY`, `-ERROR` may be appended directly instead of UC

#### B. Conversion rules for legacy SCR-NNN

If `docs/planner/.../ia-screen-design.md` contains `SCR-001`-style IDs, convert with these rules:

1. Read the screen's `Related UC`, `Type`, and `Screen Name` columns
2. PAGE = route or main feature keyword (e.g., `Expert Q&A list` → `EXPERT-LIST`)
3. SECTION = type mapping (list→LIST, detail→DETAIL, form→WRITE, modal→MODAL)
4. UC{NN} = the `Related UC` number, 2-digit zero-padded (UC-1 → UC01)
5. **Record the old/new mapping table as the first entry in `11-decision-log.md`** after conversion.

Example: `SCR-005` (question detail, adopted, UC-3) → `ACAD-EXPERT-DETAIL-UC03`

#### C. Required screens (PDF §9.2)

Minimum screens that must be included in the Registry:

- Default screen (DEFAULT)
- All states (LOADING / EMPTY / DEFAULT / ERROR) — State Matrix expansion
- All modals (Confirm / Form / Error included)
- Edge-case screens
- Hidden screens reachable only via URL parameters

If the planning document's screen list does not cover the above, warn the user:

```
⚠️ The following screens are missing from the planning document:
- {SCREEN-ID}-LOADING (loading state)
- {SCREEN-ID}-EMPTY (empty state)
- {SCREEN-ID}-ERROR (error state)

They will be added to the Registry as placeholders with "🔄 not started" status.
Proceed? (yes/no)
```

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

### Step 4: Auto-fill 1-screen-registry.md

If planning deliverables loaded in Step 1-C exist, convert the screen list from `ia-screen-design.md` into the Screen Registry table format.

| Planner column | Registry column |
|----------------|------------------|
| Screen ID (SCR-NNN) | ID (converted 4-segment) |
| Screen name | Screen name |
| Type | State/Case (default / before adoption / no answers, etc.) |
| Description | Trigger (cause / entry path) |
| — | Design status (initial: 🔄 not started) |

If there is no planning document, leave only the 4 placeholder rows from the PDF §9.1 example (LIST, LIST-EMPTY, LIST-LOADING, DETAIL-UC01).

---

### Step 5: Auto-fill 2-flows.md

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

---

### Step 6: Auto-fill 3-state-matrix.md, 4-edge-cases.md

**3-state-matrix.md**: keep the state definitions (LOADING/EMPTY/DEFAULT/ERROR/PARTIAL) as-is from the template. If `feature-definition.md` contains a `permissions per actor` table, auto-convert it for the permission matrix section; otherwise, leave only the 6-column table header (Not logged in / Regular user / Question owner / Answerer / Admin + Action column).

**4-edge-cases.md**: insert the 8 base items from PDF §13 as checkboxes. If `feature-definition.md` has a risk section, extend with additional items.

---

### Step 7: Auto-fill 5-responsive-guide.md

Use PDF §12 as-is. Keep only the Desktop (≥1024) / Tablet (768~1023) / Mobile (<768) breakpoints + the ID-notation convention (`-T`, `-M` suffixes). If `docs/design-system/DESIGN.md` Front Matter `tokens.breakpoints` exists in the project, use those values as the top priority (legacy fallback: the breakpoint variables in `src/styles/design-tokens.css`).

---

### Step 8: Auto-fill 6-component-specs.md

**Design system SSoT reference (v5.2.0+ priority)**:
- 1st priority: `docs/design-system/DESIGN.md` Body §4 (Component Guidelines) — global components are referenced via reference links in this file. Front Matter `tokens.color.semantic.*`, `tokens.typography.*` token names are used as-is in the props tables of `6-component-specs.md`.
- 2nd priority (legacy fallback): projects without DESIGN.md reference `docs/design-system/components.md`, and a `/design-init` Recommended note is added at the top of this file.

For feature-specific components, read the UI elements section from `feature-definition.md` and auto-generate in the PDF §14.1 format (props / variants / usage). At minimum, include scaffolds for the 4 card types (CourseCard, QuestionCard, InsightCard, NoticeCard) + Modal (Confirm/Form/Error).

---

### Step 9: Auto-fill 7-business-rules.md

For each Registry ID, create an empty block in the PDF §15.1 format (exposure policy / components used / per-permission branching / handling when no data / data source + caching). If the `blueprint.md` contains API endpoints, auto-fill the `data source` row.

---

### Step 10: Auto-fill 8-content-guide.md

Reflect the entire PDF §16–17 content in the template as-is:
- Brand voice (tone / form of address / forbidden expressions)
- Microcopy rules (buttons / errors / Empty / modals)
- Data display rules (images / dates / numbers / text truncation)
- i18n 3-language policy (ko/en/vi, Vietnamese 1.4× length assumption)

If the project specifies different languages, substitute via `{{LANGUAGE_POLICY}}` from Step 3.

---

### Step 11: Auto-fill 9-ia-sitemap.md, 10-personas.md, 11-decision-log.md

- **9-ia-sitemap.md**: if `ia-screen-design.md` has a menu tree, reconstruct it as an ASCII tree in the PDF §3 format. The URL conventions and depth policy (max 3 depth Recommended) stay as in the template.
- **10-personas.md**: organize the Top 3–5 personas from `interview-report.md` in the PDF §4 format (goal / pain points / usage context / device). Also extract the Top 5–10 key scenarios.
- **11-decision-log.md**: record the Step 2-B SCR-NNN → 4-segment ID conversion log as the first entry. Subsequent changes are added by UX directly.

---

### Step 12: Verify 0-README.md variable substitution

- **0-README.md**: keep template as-is (PDF §7 Quick Start + 5-min guide per role). Only verify that `{{FEATURE_NAME}}`/`{{DOMAIN_CODE}}` from Step 3 were substituted correctly.
- **walkthrough.loom.md**: already copied as a template in Step 3, so no separate creation needed. UX adds the Loom URL manually after recording.
- **DoD-CHECKLIST.md**: already copied as a template in Step 3; keep the per-role (UX/UI/Dev/QA) checklist format as-is.

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

---

## Caveats

- **Forbidden to issue an ID without registering** (PDF §20): if UI/Dev discover one, request UX to add it
- **Screen ID issuance is UX's sole authority**: do not edit `1-screen-registry.md` outside of this skill (will be enforced via a future `/register-screen` command)
- **No retroactive application to existing features**: apply only to new features or at major renewal points (PDF §26)
