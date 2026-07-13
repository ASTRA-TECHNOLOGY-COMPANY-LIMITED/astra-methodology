---
name: service-planner
description: "Auto-generates planning deliverables for a feature. Runs the full planning pipeline based on the Design Thinking methodology: market analysis → actor derivation → persona interviews → pain-point analysis → idea derivation (HMW/SCAMPER/JTBD) → requirements definition (KPI/OKR) → use-case definition (journey maps) → IA / screen design → design-system-applied HTML mockup screens → feature definition (story map / risks)."
argument-hint: "[feature description or service keyword]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Task, Agent
---

# ASTRA Service Planning Auto-Generator

Auto-generates 6 planning deliverables + HTML mockup screens for a feature, based on the Design Thinking methodology.

**Methodology mapping**:
- **Empathize**: market / competitor analysis + persona interviews
- **Define**: pain-point analysis + JTBD + requirements definition
- **Ideate**: HMW + SCAMPER + idea derivation
- **Prototype**: IA structure + screen design + HTML mockup screens + feature definition

**Deliverables**:
1. `market-analysis.md` — market / competitor analysis report
2. `interview-report.md` — persona interview report (includes pain points)
3. `requirements-definition.md` — requirements definition (includes KPI/OKR + JTBD)
4. `usecase-definition.md` — use case definition (includes diagrams + customer journey map)
5. `ia-screen-design.md` — IA structure and screen design (includes wireframes)
6. **HTML mockup screen set** — `index.html` + `styles.css` + `SCR-NNN.html` (static mockups with design-token application, responsive / dark mode)
7. `feature-definition.md` — feature definition (includes story map + risks + policies)

**Output location**: `docs/planner/{NNN}-{feature-name}/` (6 markdowns + the HTML set all live in the same directory)

> **🌐 LANGUAGE RULE**: Before executing this skill, read the project's `CLAUDE.md` and check the `## Language` section to detect the project language. If the project language is NOT Korean (`ko`), you MUST translate ALL user-facing output — including prompts, messages, generated document content, section headers, table headers, and descriptions — into the project language. Technical identifiers (tool names, file paths, command names, DB table/column names) remain untranslated. If no `CLAUDE.md` exists or no `## Language` section is found, default to Korean.

## Behavioral principle: Think Before Coding (think first, write second)

The 6 planning deliverables determine the development direction for months to come. An assumption error at the first stage therefore costs the most. Apply the following principles throughout planning:

- **Make assumptions explicit**: write down important assumptions (feature scope, user definition, business model, technical constraints) in the deliverables, especially the "Preconditions" section of `requirements-definition.md`.
- **If multiple interpretations exist, present them all**: do not silently pick a single interpretation (e.g., B2C subscription payments) for an ambiguous feature description ("payment system"). Present interpretation options to the user via `AskUserQuestion`.
- **When unclear, stop and ask**: even during step-by-step deliverable generation, if a decisive assumption is unclear, immediately confirm with the user. This is far cheaper than authoring the 6 deliverables on the wrong persona / actor / priority and discarding them.
- **Push back when a simpler approach is visible**: if the user requests an overly complex feature scope, suggest "How about including only X in the MVP and splitting Y into a later sprint?"

> Source: [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) (MIT)

## Procedure

### Step 0: Preparation and context collection

#### A. Parse feature info

Inspect `$ARGUMENTS`:

| Argument form | Behavior |
|---------------|----------|
| Feature description string (e.g., `auth feature`, `payment system`) | Proceed based on the description. If ambiguous, confirm the interpretation in A.1. |
| _(none)_ | Ask for the feature info via `AskUserQuestion` |

##### A.1: Ambiguity validation (Think Before Coding)

If the feature description matches any of the following, do not silently pick a single interpretation; instead, present interpretation options to the user via `AskUserQuestion`:

- **Generic keywords**: "payment system", "auth", "admin page" — keywords admitting multiple interpretations (B2C/B2B, one-off/subscription, social/email, etc.)
- **Unknown target**: when it is unclear who the feature is for (general user vs. operator vs. external partner)
- **Unknown scope**: when MVP vs. full-stack is ambiguous

Example question:
```
You entered "payment system". Which interpretation is closest?

(a) B2C one-off payments (single-product purchases)
(b) B2C subscription payments (monthly/yearly recurring)
(c) B2B invoice payments (invoice + post-pay)
(d) Unified multi-payment platform combining (a)–(c)

Choice:
```

For clear inputs (e.g., "B2C subscription payments, TossPayments integration"), skip this step.

If there are no arguments, ask:

```
## Generate service planning deliverables

Please describe the feature or service you want to plan.

Examples:
- "Member-auth system including social login"
- "Subscription-based payment system"
- "Team-collaboration workspace management"

Feature description:
```

Save the user's input as `{FEATURE_DESCRIPTION}`.

#### B. Choose planning mode

Choose the planning mode via `AskUserQuestion`:

```
## Choose planning mode

Which type of planning will you run?

1. 🆕 New service planning — plan a new feature / service from scratch
2. 🔄 Improve an existing service — analyze and derive improvements for a running service

Choice:
```

- On **new service planning**: proceed with the default workflow as-is
- On **improve an existing service**: collect additional context:

  See [references/improve-mode.md](references/improve-mode.md) — read it when the user picks improve mode; it holds the additional-info collection prompt and the per-step adaptations for `{EXISTING_SERVICE_DATA}`.

Save the collected info as `{EXISTING_SERVICE_DATA}` and reflect it in persona interviews and market analysis in later steps.

#### C. Analyze the target project

Analyze the following in the current working directory:

1. Read `CLAUDE.md` — verify project overview, tech stack, domain context
2. Scan `docs/planner/` — determine existing planning-deliverable numbering (decide the next)
3. Scan `docs/blueprints/` — check potential linkage with existing blueprints

#### D. Determine the directory number

Scan the `docs/planner/` directory to verify existing numbering and decide the next number.

```
NNN = (max existing number) + 1, or 001 if none
```

Derive an English directory name from the feature description (e.g., `auth feature` → `auth`, `payment system` → `payment`).

`{OUTPUT_DIR}` = `docs/planner/{NNN}-{feature-name}/`

Confirm the directory name via `AskUserQuestion`:

```
## Confirm deliverables directory

Deliverables save path: {OUTPUT_DIR}

Proceed with this path? If you need a change, enter the desired directory name.
(e.g., 001-auth, 002-payment)
```

#### E. Switch to the dev branch and sync to latest

Before creating deliverable files, switch to `dev` and sync to latest. Do not create a work branch; work directly on `dev`. Work-branch creation is handled automatically when `/pr-merge` runs.

0. **Main-worktree guard**: if called from inside an isolated worktree (`.worktrees/<slug>/`), abort. dev-sync runs only in the main worktree:
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

> **Note**: if the `dev` branch does not exist, work on `main` or `master`. If no default branch exists, work on the current branch.

---

### Step 1: Generate the market / competitor analysis report

#### A. Market-environment analysis

Based on `{FEATURE_DESCRIPTION}` and the project context, analyze the following:

1. **PEST analysis**: Political, Economic, Social, Technological factors
2. **Market size and trends**: market trends, growth, key changes in the domain
3. **Target market**: target customer base, market segments

> **Improve-existing-service mode**: if `{EXISTING_SERVICE_DATA}` is present, also analyze the current service's positioning and market position.

#### B. Competitor benchmarking

Select 3–5 similar services / products and benchmark:

- Direct competitors (services offering the same feature)
- Indirect competitors (services solving a similar problem in another way)
- Global references (overseas exemplars)

#### C. SWOT analysis

Derive the project's Strengths, Weaknesses, Opportunities, and Threats.

#### D. Author the market-analysis report

Read `references/templates-market-analysis.md` and instantiate the template with `{FEATURE_DESCRIPTION}` and the analysis results, writing the output to `{OUTPUT_DIR}/market-analysis.md`.

> **Important**: after authoring the market-analysis report, confirm with the user: "The market-analysis report has been generated. Proceed to the next step (actor derivation)?"

---

### Step 2: Actor derivation and selection

#### A. Auto-derive actors

Synthesize `{FEATURE_DESCRIPTION}` and the market-analysis result to derive related actors (user types).

Derivation criteria:
- **Direct users**: subjects who directly use the service (general user, subscriber, buyer, etc.)
- **Administrators**: subjects who manage / operate the service (system admin, operator, content manager, etc.)
- **Indirect users**: subjects who interact indirectly (partner, API consumer, external system, etc.)
- **Stakeholders**: subjects who care about the outcome (execs, marketers, etc.)

Derive at least 3 and at most 8 actors.

#### B. Multi-select actors

Show the derived actor list to the user and request multi-select via `AskUserQuestion`:

```
## Select actors (user types)

Below is the actor list derived for "{FEATURE_DESCRIPTION}".
Select actors to interview (comma-separate for multi-select).

| # | Actor | Type | Description |
|---|-------|------|-------------|
| 1 | General user | Direct user | end user who uses the service directly |
| 2 | System admin | Administrator | operator managing the service |
| 3 | ... | ... | ... |

Actor numbers to select (e.g., 1,2,3):
```

Save the selected actors as the `{SELECTED_ACTORS}` array.

> **Note**: if the user wants to add an actor, accept the additional actor as input and include it in the list.

---

### Step 3: Run persona interviews and generate the interview report

#### A. Generate personas per actor

Generate **3 personas** per selected actor.

Each persona includes:

| Item | Description |
|------|-------------|
| Name | a name (e.g., Min-su Kim) |
| Age | range 25–55 |
| Occupation | typical occupation for the actor |
| Tech literacy | beginner / intermediate / advanced |
| Usage context | mobile / desktop / hybrid |
| Core goal | the main purpose of using the service |
| Frustrations | dissatisfactions from prior experiences |
| Traits | usage patterns, dispositions, and other differentiators |

Personas must reflect diverse backgrounds and perspectives (distribute age range, tech literacy, usage purposes).

> **Improve-existing-service mode**: reflect real user feedback / CS data from `{EXISTING_SERVICE_DATA}` in the personas' frustrations and interview answers.

#### B. Run persona interviews

Simulate a **deep interview** for each persona.

Use the interview question bank in [references/persona-interview-guide.md](references/persona-interview-guide.md) — 4 categories (Current experience / Pain points / Needs & expectations / Value & priority), 3–5 questions each, 15–20 total.

Each persona's responses must be **realistic answers reflecting that persona's traits**.

#### C. Comprehensive pain-point analysis

Analyze all interview results and produce:

1. **Per-actor core pain points** — 5 pain points commonly observed for each actor type
2. **Interest keywords** — 5 keywords representing each actor's core interests
3. **Task analysis** — score each major task on a 5-point scale for importance / time / frequency
4. **Overall integrated pain points** — Top 10 most severe pain points across all actors

#### D. Author the interview report

Read `references/templates-interview-report.md` and instantiate the template with the persona-interview and pain-point results, writing the output to `{OUTPUT_DIR}/interview-report.md`.

> **Important**: after authoring the interview report, confirm with the user: "The interview report has been generated. Proceed to the next step (idea derivation)?"

---

### Step 4: Idea derivation and requirements-definition generation

#### A. Idea derivation

Based on the interview report's **Top 10 integrated pain points** and the market-analysis report's **planning direction**, derive solution ideas.

Idea-derivation techniques:
- **HMW (How Might We)**: convert each pain point into "How might we …?"
- **SCAMPER**: Substitute, Combine, Adapt, Modify, Put to other use, Eliminate, Reverse
- **JTBD (Jobs-to-be-Done)**: write a Job Statement for each core pain point:
  - Form: "**When** [context], **I want to** [motivation/action], **so I can** [expected outcome]"
  - Identify currently underserved needs per JTBD and reflect them in ideas
- **Tech application**: include technical solutions — AI / automation / UX improvements, etc.

> **Improve-existing-service mode**: when `{EXISTING_SERVICE_DATA}` is present, author JTBD / HMW based on real usage data (churn points, CS-inquiry types, frequency of use) and back idea priority with empirical evidence.

Derive at least 10 and at most 15 ideas.

#### B. Pick ideas

Show the derived ideas and request multi-select via `AskUserQuestion`:

```
## Select solution ideas

Ideas derived from interview pain points + market analysis.
Pick ideas to implement (comma-separate for multi-select).

| # | JTBD | HMW question | Idea | Description | Pain points addressed | Implementation difficulty | Expected impact |
|---|------|--------------|------|-------------|------------------------|---------------------------|-----------------|
| 1 | When..., I want to..., so I can... | How might we ...? | {idea} | {description} | PP-{N} | high/med/low | high/med/low |
| 2 | ... | ... | ... | ... | ... | ... | ... |

Idea numbers to select (e.g., 1,3,5,7):
```

Save the selected ideas as the `{SELECTED_IDEAS}` array.

#### C. Author the requirements definition

Read `references/templates-requirements-definition.md` and instantiate the template with the selected ideas and KPI/OKR/JTBD analysis, writing the output to `{OUTPUT_DIR}/requirements-definition.md`.

> **Important**: after authoring the requirements definition, confirm with the user: "The requirements definition has been generated. Proceed to the next step (use-case definition)?"

---

### Step 5: Generate the use-case definition

Define use cases per actor, based on the interview report and the requirements definition.

#### A. Use-case derivation

For each selected actor, map requirements to use cases:

- One requirement may correspond to 1+ use cases
- Identify relationships among use cases: `<<include>>`, `<<extend>>`, generalization

#### B. Derive customer journey maps

For core use cases (3–5), author customer journey maps:

Components:
- **Phase**: time-ordered service touchpoints (Awareness → Exploration → Sign-up → Use → Re-visit)
- **Action**: the user's actions per phase
- **Touchpoint**: the channel / screen where the user meets the service
- **Emotion**: the user's emotional state per phase (😊 positive / 😐 neutral / 😤 negative)
- **Pain point**: inconveniences at each phase
- **Opportunity area**: points where improvement is possible

#### C. Author the use-case definition

Read `references/templates-usecase-definition.md` and instantiate the template with the use-case and customer-journey-map results, writing the output to `{OUTPUT_DIR}/usecase-definition.md`.

> **Important**: after authoring the use-case definition, confirm with the user: "The use-case definition has been generated. Proceed to the next step (IA structure and screen design)?"

---

### Step 6: IA structure and screen design + HTML mockup-screen generation

Based on the use-case and requirements definitions, design the information architecture (IA) and author both the wireframes (markdown) of major screens and the static HTML mockups with design-token application. Flow: A→D (markdown authoring) → E (design system / tone decision) → F (HTML generation).

#### A. IA (Information Architecture) design

Based on the feature definition and use cases, design the overall menu structure:

- **Depth 1**: top menu (GNB)
- **Depth 2**: mid menu (LNB or tabs)
- **Depth 3**: leaf menu (detail pages)

Map related use cases and requirements to each menu item.

> **Improve-existing-service mode**: start from the current service's IA and mark only changed / added menu items separately (e.g., `[NEW]`, `[CHANGED]`). For existing screens, only the parts that need changes are written as wireframes.

#### B. Screen flow

For major user scenarios (based on the main flows of the use cases), author the screen-transition paths as Mermaid flowcharts.

#### C. Text-based wireframes

Author ASCII-based wireframes for core screens (3–5):

- Layout structure (header, sidebar, content, footer)
- Major UI element placement (button, input field, table, card, etc.)
- Functional description of each element

#### D. Author the IA structure and screen-design report

Read `references/templates-ia-screen-design.md` and instantiate the template (§1–§6) with the IA, screen-flow, and wireframe results, writing the output to `{OUTPUT_DIR}/ia-screen-design.md`. (§7 HTML mockup preview is appended later in Step 6.F.5.)

#### E. Load the design system and auto-decide the design tone

Decide the design tokens and design tone to use for HTML mockup generation.

The full loading procedure — SSoT priority order (DESIGN.md → design-tokens.css → template), component/layout guides, the required Vibe Coding guides, and the `{DESIGN_TONE}` auto-decision table — lives in [references/templates-html-mockup.md](references/templates-html-mockup.md) (§Design system loading & tone decision). Read it before generating styles.css.

#### F. Generate HTML mockup screens (design-token-applied static mockups)

**Purpose**: complement the text wireframes by providing visual mockups the user can verify in the browser immediately. Not production components — **static HTML/CSS mockups** that are high-fidelity wireframes with design tokens applied.

**Core principles**:
- Use only static HTML/CSS (no JS framework / bundler needed; opens directly in the browser)
- Use design tokens 100% (no hardcoded colors/sizes; `var(--*)` or fallback values)
- Auto-support for responsive (mobile/tablet/desktop) + dark mode (`prefers-color-scheme`)
- Implement micro-interactions (hover/focus/active) with CSS only
- Dummy data is natural content based on persona info
- No AI-image generation (inefficient at the planning stage) — icons are inline SVG or CSS gradients

##### F.1 Output location

**All HTML/CSS files are created directly in the same directory as the markdown deliverables (`{OUTPUT_DIR}/`)**. Do not create a separate subfolder.

See the output-location tree in [references/templates-html-mockup.md](references/templates-html-mockup.md) (§Output location tree).

##### F.2 Generate shared styles (styles.css)

Generate `{OUTPUT_DIR}/styles.css` per the 9-section structure (tokens · dark-mode override · reset · typography · layout utilities · components · animation · accessibility · print) in [references/templates-html-mockup.md](references/templates-html-mockup.md) (§Shared styles `styles.css` structure).

##### F.3 Generate per-screen HTML (`SCR-NNN.html`)

Based on Section 4 (screen list) + Section 5 (wireframes) of `ia-screen-design.md`, **generate a separate HTML file per SCR-NNN listed**.

Read `references/templates-html-mockup.md` (section "Per-screen `SCR-NNN.html` skeleton") and instantiate the skeleton for each SCR-NNN.

Generation rules — semantic HTML, token-only values, responsive breakpoints, dark mode, accessibility, persona-based dummy data, disabled interactions, inline-SVG icons, cross-page navigation — are tabulated in [references/templates-html-mockup.md](references/templates-html-mockup.md) (§Per-screen generation rules).

##### F.4 Generate the screen index (`index.html`)

Generate a navigation hub showing all SCR-NNN screens at a glance. Read `references/templates-html-mockup.md` (section "Screen index `index.html` skeleton") and instantiate it.

##### F.5 Augment the IA / screen-design report

Add an HTML-preview guidance section to the body of `ia-screen-design.md` (at the end of Section 6 or as its own section). Read `references/templates-html-mockup.md` (section "`ia-screen-design.md` §7 block") and instantiate it.

##### F.6 Screen-quality convergence loop (adversarial, max 5 iterations)

After F.2–F.5 complete, run the `screen-quality-loop` protocol (skills/screen-quality-loop/SKILL.md) over the **full mockup set as one batch** (MODE=mockup): delegate `{OUTPUT_DIR}`'s `SCR-NNN.html` + `index.html` + `styles.css` to the read-only `screen-verifier` agent (Agent tool) — sibling baseline is the other SCR screens plus `index.html`; SSoT paths are `docs/design-system/DESIGN.md` and `{OUTPUT_DIR}/styles.css`. Parse ONLY the final `ASTRA_SCREEN_RESULT:` tail line (absent line = FAIL, never PASS), apply the Fix Directives in this parent context, and repeat until **score ≥ 90 AND p0 == 0** or **5 iterations** (hard cap, no HITL). Write each report to `{OUTPUT_DIR}/screen-quality/verify-{i}.md`. If the cap is reached without passing, report the remaining P0s/directives honestly and continue — the loop never blocks Step 7.

> **Important**: after the F.6 loop finishes, confirm with the user: "The IA/screen-design report and HTML mockups have been generated (screen-quality score {score}/100{, achieved | after 5 iterations — remaining issues listed above}). You can open `{OUTPUT_DIR}/index.html` in the browser to check. Proceed to the next step (feature definition)?"

---

### Step 7: Generate the feature definition

Synthesize the interview report, requirements definition, use-case definition, and IA/screen-design report to author the final feature definition.

#### A. Feature structuring

Structure features based on requirements and use cases:
- **Feature Group**: top category
- **Feature**: implementation unit
- **Sub-feature**: detailed behavior

#### B. User Story Mapping

Rearrange features as a User Story Map to visualize the MVP scope:
- **User Activity** (row): the user's big activity unit (corresponds to a Feature Group)
- **User Task** (row): specific tasks within an activity (corresponds to a Feature)
- **User Story** (column): detail stories of a task (corresponds to a Sub-feature)
- **Release Slice**: horizontal division by release (MVP / v1.1 / v1.2)

> **Improve-existing-service mode**: in the feature tree, distinguish between existing and new/changed features (e.g., `[NEW]`, `[CHANGED]`, `[AS-IS]`). In the User Story Map, place only the changes included in the current release in the MVP slice.

#### C. Author the feature definition

Read `references/templates-feature-definition.md` and instantiate the template with the feature-structuring and story-map results, writing the output to `{OUTPUT_DIR}/feature-definition.md`.

> **Important**: after authoring the feature definition, confirm with the user: "The feature definition has been generated. Print the final completion report?"

---

### Step 8: Completion report

When every deliverable is generated, report the result to the user:

Instantiate the report template in [references/completion-report.md](references/completion-report.md) — the deliverables table, the "open index.html" hint, the run Summary (actors/personas/pain points/JTBD/ideas/KPIs/requirements/use cases/journey maps/IA/wireframes/mockups/features/story map/risks/policies), and the closing next-steps line — filling every `{N}` / `{DESIGN_TONE}` / `{OUTPUT_DIR}` placeholder.
