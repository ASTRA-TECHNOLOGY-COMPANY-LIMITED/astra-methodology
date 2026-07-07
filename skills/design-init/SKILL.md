---
name: design-init
description: "Creates or updates docs/design-system/DESIGN.md — the design-system SSoT (YAML Front Matter tokens + Markdown Body) — and regenerates src/styles/design-tokens.css from it. Modes: new/update, --regenerate-css, --from-refs=<paths-or-urls> (extract references then merge), --apply-extract=<report-path>. Use when defining brand or design tokens, bootstrapping a design system, or regenerating CSS after DESIGN.md changes."
argument-hint: "[--regenerate-css] [--from-refs=<paths-or-urls>] [--apply-extract=<report-path>] [--auto]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Skill, TodoWrite
---

# /design-init — Design System SSoT Initialization Skill

Creates and manages `docs/design-system/DESIGN.md` as the project's design system single source of truth (SSoT). When this file changes, `src/styles/design-tokens.css` becomes an artifact regenerated automatically by this skill.

## Design Philosophy

Problems this skill solves:
- In the previous ASTRA, `design-tokens.css` (for machines) and `components.md` (for humans) were separate, forcing the AI to verify consistency between the two files every time.
- Design philosophy, persona, and anti-AI aesthetic rules were never codified in code or comments.
- Per-project design system initialization was manual.

Resolution direction:
- DESIGN.md = YAML Front Matter (machine-readable tokens) + Markdown Body (design philosophy, component guide, anti-AI rules) merged into a single file.
- design-tokens.css is auto-generated from the Front Matter. No hand-editing.
- `/service-planner`, `/handoff-publish`, and `design-token-validator` all reference DESIGN.md first.

## Execution Procedure

### Step 0: Argument parsing and mode determination

Parse from `$ARGUMENTS`:

| Token | Meaning |
|-------|---------|
| `--regenerate-css` | Regenerate only design-tokens.css from DESIGN.md. Skip other steps. |
| `--from-refs=<paths-or-urls>` | Extract tokens from image/PDF/URL references and merge. Internally invokes `/design-extract` **exactly once** to generate a report, then merges that report directly without re-entering via `--apply-extract` (no circular invocation). |
| `--apply-extract=<report-path>` | Merge an already-generated `docs/design-system/extract-report-*.md` report into DESIGN.md. Does not invoke `/design-extract` again. |
| `--auto` | Skip HITL, use conservative defaults (autorun-compatible). |

Determine the `MODE` variable (in priority order):
- `regenerate-css` if `--regenerate-css`
- `apply-extract` if `--apply-extract=...`
- `from-refs` if `--from-refs=...` (→ inside the Step 1 branch, invoke `/design-extract` and merge the resulting report verbatim)
- `update` if `docs/design-system/DESIGN.md` exists
- `init` otherwise

`AUTO_MODE=1` if `--auto`.

### Step 1: Detect existing assets

```bash
# Verify project root
test -d docs || { echo "ERROR: Run from project root (docs/ missing)"; exit 1; }

# Existing assets
EXISTING_DESIGN_MD="docs/design-system/DESIGN.md"
EXISTING_CSS="src/styles/design-tokens.css"
EXISTING_COMPONENTS="docs/design-system/components.md"
PLANNER_DIRS=$(ls -d docs/planner/[0-9][0-9][0-9]-* 2>/dev/null)
```

| State | Behavior |
|-------|----------|
| DESIGN.md exists + `update` mode | Read existing file → ask intent for changes → partial update |
| DESIGN.md missing + `init` mode | New-generation workflow (Steps 2~5) |
| `regenerate-css` mode | Run Step 6 only |
| `from-refs` mode | Invoke `Skill(design-extract, args="<refs>")` **exactly once** to produce `docs/design-system/extract-report-*.md` → store the resulting report path in `EXTRACT_REPORT_PATH` → then merge in the same way as `apply-extract` (Step 2.2 HITL uses values filled by the report as defaults) |
| `apply-extract` mode | Read the report specified by `--apply-extract=<path>` and use it as the seed for the Step 3 placeholder substitution. Does not invoke `/design-extract`. |
| Only `components.md` exists + DESIGN.md missing | Migration mode — absorb the components.md content into Body §4 during Step 2 |

### Step 2: Collect brand identity inputs

In `init` or `update` mode, collect inputs to fill Front Matter `brand` and Body §1~§2.

#### Step 2.1: Auto-cite from planner deliverables (when present)

If `PLANNER_DIRS` is non-empty, read `interview-report.md` and `requirements-definition.md` of the most recent directory and auto-extract:

- `brand.target_persona` ← one-sentence summary of the primary persona from interview-report.md
- Body §2 Primary Persona ← entire persona section from interview-report.md (cited with source)
- `brand.voice_tone` ← tone guide from requirements-definition.md (when present)

#### Step 2.2: HITL questions (`AUTO_MODE=0`)

Ask the following 4 items via `AskUserQuestion` (multiSelect=false):

1. **Brand tone** (choose one: Calm / Bold / Playful / Trustworthy / Technical) — primary keyword for `brand.personality`
2. **Primary color family** (choose one: Blue / Indigo / Emerald / Rose / Amber / Neutral) — determines Front Matter `tokens.color.primitive.primary.*`
3. **Typography pairing** (Geist+Pretendard recommended / Inter+Pretendard / Manrope+Pretendard / user-specified)
4. **Density** (Compact: enterprise SaaS density / Comfortable: general product / Spacious: marketing) — determines spacing scale defaults and component heights

If `AUTO_MODE=1`, defaults: Calm / Blue / Geist+Pretendard / Comfortable.

#### Step 2.3: Design philosophy sentence

Accept free-form input (not `AskUserQuestion`) — guide the user to write "this project's design philosophy" as a single sentence. If empty, auto-generate from the persona ("a {tone} design system for {persona}").

### Step 3: Generate DESIGN.md

Read `$CLAUDE_PLUGIN_ROOT/skills/project-init/templates/DESIGN.md` and substitute the following placeholders:

| Placeholder | Value |
|-------------|-------|
| `{project-name}` | `name` from `package.json`, or the directory name if absent |
| `brand.philosophy` | Step 2.3 input |
| `brand.personality` | Step 2.2 (answer #1 + 2 supplemental defaults) |
| `brand.target_persona` | Step 2.1 auto-extract, or user input if absent |
| `brand.voice_tone` | Step 2.1 auto-extract, or 3 defaults if absent |
| `tokens.color.primitive.primary.*` | 11 OKLCH steps based on the Step 2.2 (#2) color family (use a lookup table) |
| `tokens.typography.fonts.sans/mono` | Step 2.2 (#3) |
| `spacing.scale` defaults | adjust component heights per Step 2.2 (#4) density |
| Body §1 Design Philosophy | Step 2.3 + 2-3 auto-augmented sentences |
| Body §2 Persona citation | Step 2.1 citation or user input |
| Body §5 aesthetic_rules project-specific elements | 2 tone-based defaults |
| `Version 1.0.0` Date | `$(date +%Y-%m-%d)` |

Output: `docs/design-system/DESIGN.md`

**Primary color OKLCH lookup**:
```
Blue:    base hue 259°,  L 62.3% (500)  — Linear/Vercel tone
Indigo:  base hue 277°,  L 58.5% (500)  — Stripe tone
Emerald: base hue 162°,  L 69.6% (500)
Rose:    base hue 17°,   L 67.0% (500)
Amber:   base hue 70°,   L 76.9% (500)
Neutral: minimal color emphasis — primary=neutral-900
```

For each family, the 11 steps (50/100/200/.../950) apply a lightness curve (Tailwind standard curve as reference). Concrete values are loaded from `$CLAUDE_PLUGIN_ROOT/skills/design-init/assets/color-palettes.yaml`.

### Step 4: Auto-generate design-tokens.css (call Step 6)

Before proceeding to Step 5, immediately call Step 6 (`regenerate-css`). Without the CSS, preview is impossible.

### Step 5: Verification and preview

#### Step 5.1: Invoke design-token-validator

```
Task(
  subagent_type: "astra-methodology:design-token-validator",
  description: "Verify DESIGN.md",
  prompt: "Verify the Front Matter token consistency and WCAG contrast ratios of docs/design-system/DESIGN.md. Report any violations."
)
```

If the report contains Critical items, show them to the user and guide them to fix.

#### Step 5.2: HTML preview (`AUTO_MODE=0` and with user consent)

Generate `docs/design-system/preview.html` so the user can visually verify the applied tokens. Structure:
- Color swatches (full Primitive + Semantic)
- Typography scale (xs ~ 6xl)
- Spacing scale visualization
- 5 variant samples each of Button/Input/Card components
- Anti-AI aesthetic rules checklist

After generation, output only the path. The user opens it directly.

### Step 6: Regenerate design-tokens.css (`--regenerate-css` or called from Step 4)

Parse the Front Matter of `docs/design-system/DESIGN.md` and generate `src/styles/design-tokens.css`.

#### Step 6.1: Front Matter parsing + reference resolution

Parse the YAML Front Matter, then resolve the ASTRA reference syntax `"{tokens.color.primitive.neutral.0}"` into CSS variable **chains** (not OKLCH value lookups) — e.g. `--surface-base: var(--primitive-neutral-0)` — so the browser chain-resolves at runtime and dark-mode overrides work cleanly. The concrete Python parser + `resolve_ref` implementation: see [references/css-generation.md](references/css-generation.md). Read it before writing the parser.

#### Step 6.2: Transformation rules

| YAML path | CSS variable name |
|-----------|-------------------|
| `tokens.color.primitive.{family}.{shade}` | `--primitive-{family}-{shade}` |
| `tokens.color.semantic.{group}.{name}` | `--{group}-{name}` (snake_case → kebab-case) |
| `tokens.typography.scale.{key}` | `--text-{key}` |
| `tokens.typography.fluid_scale.{key}` | `--fluid-{key}` |
| `tokens.typography.weight.{key}` | `--weight-{key}` |
| `tokens.spacing.scale.{key}` | `--space-{key}` |
| `tokens.radius.{key}` | `--radius-{key}` |
| `tokens.shadow.{key}` | `--shadow-{key}` |
| `tokens.motion.duration.{key}` | `--duration-{key}` |
| `tokens.motion.easing.{key}` | `--ease-{key.replace('_', '-')}` |
| `tokens.motion.spring.{key}` | `--ease-spring-{key}` |
| `tokens.breakpoints.{key}` | `--breakpoint-{key}` |
| `tokens.z_index.{key}` | `--z-{key}` |

**Reference substitution**: `"{tokens.color.primitive.neutral.0}"` → `var(--primitive-neutral-0)`.

#### Step 6.3–6.4: Write the CSS file + show diff

Write `src/styles/design-tokens.css` with an `AUTO-GENERATED from DESIGN.md — DO NOT EDIT BY HAND` header (regenerate command, timestamp, source `meta.version`), a `:root` block ordered Primitive → Semantic, then diff against the existing file before overwriting. Exact header format + diff snippet: see [references/css-generation.md](references/css-generation.md).

### Step 7: Workflow termination

Output the following to the user:

1. ✅ Generated file list (DESIGN.md, design-tokens.css, preview.html)
2. 📋 Next steps:
   - `/service-planner` auto-references DESIGN.md
   - When adding a new component, register it in this file §4 + Front Matter `components.*` together
   - After token changes: `/design-init --regenerate-css`
3. ⚠️ `src/styles/design-tokens.css` must not be hand-edited

## Workflow checklist

- [ ] Step 0: argument parsing + MODE determination
- [ ] Step 1: detect existing assets (DESIGN.md / CSS / components.md / planner)
- [ ] Step 2: collect brand inputs (planner auto-cite + 4 HITL questions + philosophy sentence)
- [ ] Step 3: substitute template placeholders → write DESIGN.md
- [ ] Step 4: auto-generate design-tokens.css (call Step 6)
- [ ] Step 5: design-token-validator verification + (optional) preview.html
- [ ] Step 6: Front Matter → CSS conversion (entry point when regenerate-css is invoked standalone)
- [ ] Step 7: output result + next-step guidance

## Behavior mode matrix

| Argument | DESIGN.md exists | Behavior |
|----------|------------------|----------|
| (none) | × | init: full Step 0~7 |
| (none) | ○ | update: Step 0~7, partial-update intent asked in Step 2 |
| `--regenerate-css` | ○ | Step 0 + Step 6 + Step 7 only |
| `--regenerate-css` | × | Error: "DESIGN.md is missing. Run /design-init first" |
| `--from-refs=...` | × | Invoke `Skill(design-extract)` once → merge the generated report directly in this skill (no recursive call) → proceed Step 2~7 |
| `--from-refs=...` | ○ | Same as above but ask user confirmation before merging |
| `--apply-extract=<path>` | × | Use the report as seed to proceed Step 3~7 |
| `--apply-extract=<path>` | ○ | Partial-update the existing DESIGN.md from report content (after user confirmation) |
| `--auto` | any | All HITL above is handled with defaults |

## Conventions and notes

- **Fixed output location**: DESIGN.md is always `docs/design-system/DESIGN.md`. Do not change.
- **Fixed CSS output location**: `src/styles/design-tokens.css`. `tokens.json` or `theme.ts` will be handled by separate skills (future).
- **Legacy `components.md`**: Do not delete after migration — preserve it. Add a deprecation comment at the top noting that its content has been absorbed into Body §4.
- **Version bump**: bump Front Matter `meta.version` as a major bump only for breaking changes (token name change/removal). Patch bump for token value changes only.
- **Validation failure handling**: When design-token-validator reports Critical, never proceed automatically. Fix after user confirmation.
- **WCAG verification**: In Step 5.1, warn on any (text, surface) combination whose contrast ratio is below 4.5. Warnings are emitted even in AUTO_MODE.

## ASTRA integration points

| Integration point | Behavior |
|-------------------|----------|
| `/project-init` | Invokes this skill with `--auto` during Sprint 0 init to seed the default design system |
| `/service-planner` Step E | References in order: DESIGN.md 1st → design-tokens.css 2nd → plugin templates 3rd |
| `/handoff-publish` | `6-component-specs.md` cites DESIGN.md Body §4 by reference link |
| `design-token-validator` agent | Treats DESIGN.md Front Matter as the SSoT. CSS is a fallback. |
| `/design-audit` command | Validates changed files against DESIGN.md immediately |
| `/design-extract` skill | Extracts tokens from references and joins this skill |
| `/design-redesign` skill | Audits and fixes existing UI against DESIGN.md |

## Evaluation scenarios (skill verification)

After authoring/edits, verify behavior with the following 3 scenarios:

1. **Empty project (init)**: Only `docs/` exists and `docs/design-system/` is absent → DESIGN.md + design-tokens.css are newly created. preview.html renders correctly.
2. **Legacy present (migration)**: `src/styles/design-tokens.css` and `docs/design-system/components.md` already exist → integrate into DESIGN.md, convert CSS to a generated artifact (with the warning header), and mark components.md as deprecated.
3. **Reference input (from-refs)**: `--from-refs=https://linear.app` → `/design-extract` is invoked, colors/fonts are extracted and reflected in DESIGN.md, validator passes after contrast verification.

Each scenario must pass Step 5.1 validation for PASS.

## Four-principles application

- **Think Before Coding**: Use the 4 HITL questions in Step 2 to make ambiguous design requirements explicit before proceeding.
- **Simplicity First**: One default + escape hatch. Limit options like "Inter/Manrope/user-specified" — 6 options → 4 options.
- **Surgical Changes**: Step 6 regeneration overwrites only the CSS. Other files must never be modified. Even in `update` mode, only sections the user confirmed are partially updated.
- **Goal-Driven Execution**: Use the Step 5.1 validator verification as the explicit PASS criterion. If Critical items remain, do not proceed to Step 7 completion.
