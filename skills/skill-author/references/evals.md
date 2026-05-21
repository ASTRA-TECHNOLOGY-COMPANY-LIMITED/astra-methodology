# skill-author Evaluations

At least three evaluation scenarios that verify this skill behaves as intended. The baseline is the result of attempting the same task *without* this skill.

## Scenario 1: Write a new validation skill (happy path)

- **Input**: user utterance "Create a new skill that counts keyword frequency in Slack messages."
- **Expected**:
  1. `/skill-author` is invoked (or auto-triggered)
  2. Step 0 auto-decides `new` mode
  3. Step 1 bundles the 4 metadata questions (name, type, side-effects, permissions) into a single `AskUserQuestion`
  4. Type = "validation-utility" → English `description: >` block + 7-principle application
  5. After authoring the body, the BP §13 13-item checklist is invoked automatically (`/skill-lint`)
  6. A `references/evals.md` guidance prompt is emitted
- **Pass criteria**:
  - Generated SKILL.md is 13/13 PASS or 0 FAIL on `/skill-lint`
  - description contains the `Use when` trigger phrase
  - Body ≤ 500 lines

## Scenario 2: Refactor an existing skill (refactor mode)

- **Input**: `/skill-author skills/example-broken/SKILL.md` (a hypothetical skill deliberately written with 1st-person description + Windows path + 700 lines)
- **Expected**:
  1. Step 0 auto-decides `refactor` mode
  2. `/skill-lint` runs the 13 checks → 3 FAILs (1st-person description, Windows path, over 500 lines)
  3. P0 classification: description 1st→3rd person, Windows path → forward slash → **auto-applied**
  4. P1 classification: over 500 lines → `AskUserQuestion` confirms the references/ split, then apply
  5. After fixes, re-run `/skill-lint` → verify no regression
- **Pass criteria**:
  - P0 items are fixed immediately without user confirmation
  - P1 items are applied after a user response
  - On re-validation, 0 FAILs

## Scenario 3: Automatic anti-pattern blocking (negative)

- **Input**: user attempts to directly write `"I can help you write skills..."` in the description
- **Expected**:
  1. Step 2.1 description self-check matches the 1st-person pattern ("I can")
  2. Immediate block + 3rd-person rewrite guidance: "First-person self-introduction description violates BP §3 principle 1 — rewrite as 'Creates skills...'"
  3. If the user does not rewrite, refuse to proceed to the next step
- **Pass criteria**:
  - If any one of 1st-person / vague verb / Windows path / time-sensitive expression / 3-level nesting is found during authoring, authoring is interrupted and a fix prompt is emitted
  - If the user refuses to fix, SKILL.md is not saved

## Scenario 4 (bonus): Meta skill self-identification

- **Input**: user asks "Create a new skill-creation skill" (when `skill-author` already exists)
- **Expected**:
  1. The skill detects that it already exists via Grep
  2. Prompts: "`/skill-author` already exists — create a new one, or improve the existing one?"
  3. Branches into new / refactor mode according to the user's choice
- **Pass criteria**:
  - Prevents duplicate skill creation
  - Surfaces conflicts with the existing skill explicitly

---

**Baseline (without the skill)**:
- Claude either loads the BP in full each time (wasting tokens) or remembers only part of it, producing inconsistent SKILL.md files
- 1st-person descriptions, time-sensitive info, and Windows paths are frequently missed
- The 13-item checklist is volatile — different items get missed on each invocation

**With the skill (goal)**:
- Token-efficient because only BP §3 / §8 / §13 are partially referenced step-by-step
- Consistency assured by automatic anti-pattern blocking
- Regression prevented by `/skill-lint`
