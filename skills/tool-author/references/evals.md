# tool-author Evaluations

Three baseline scenarios for verifying the skill triggers correctly and produces the expected output. Re-run after every SKILL.md change.

---

## Scenario 1 — Happy path (Python / Pydantic)

**Input** (user utterance):

> Add an MCP tool that creates a GitHub issue. Repo, title, body, optional labels.

**Expected**:
- Skill triggers (matches "MCP tool")
- Asks the 4 metadata questions (name, one-line purpose, language, side-effect risk)
- Side-effect risk identified as "writes data" → Step 6 special handling kicks in
- Output description has:
  - Verb-led first line ("Create a GitHub issue...")
  - `Do NOT use to comment on an existing issue (use add_issue_comment instead)`
  - `e.g.` example on every `Field`
  - `Returns:` block documenting the issue ID
- Schema uses `Pydantic BaseModel`, `pattern` for the repo regex, `min_length` / `max_length` on title

**Pass criteria**: `Step 7` final checklist returns 8/8. Validator (Step 5) reports PASS.

---

## Scenario 2 — Side-effect edge case (weak anti-pattern)

**Input**:

> Here is my delete_user tool definition. Can you check it?
>
> ```python
> @tool
> def delete_user(user_id: str) -> dict:
>     """Delete a user from the database."""
>     ...
> ```

**Expected**:
- Skill triggers in **validate** mode (matches "check it" + side-effect verb)
- Validator reports:
  - A1 ✓ (verb-led)
  - A2 ✗ (no `Do NOT use` clause) → **P0** (escalated because side-effect)
  - A4 ✗ (no example on `user_id`) → P1, escalated to P0
  - A6 ✗ (no `Returns:`) → P1, escalated to P0
- Recommends rewriting to include:
  - `Do NOT use to deactivate a user — use suspend_user instead.`
  - `user_id: str — UUID v4. e.g. '7c1a2b...'`
  - `Returns: {"deleted": bool, "deleted_at": str (ISO 8601)}`
  - `disable-model-invocation: true` at the calling layer

**Pass criteria**: All three P0 violations surfaced. Suggested rewrite would pass the validator on re-run.

---

## Scenario 3 — Ambiguous sibling pair (negative / misuse)

**Input**:

> I have two tools, `get_user` and `search_users`. Sometimes Claude picks the wrong one. Help me fix the descriptions.

**Expected**:
- Skill triggers in **refactor** mode
- Reads both tool definitions
- Detects overlapping keywords (e.g., both mention "user" and "find")
- Output: paired descriptions where:
  - `get_user` first line: "Fetch a user by their exact user_id."
  - `get_user` anti-pattern: "Do NOT use for partial-match or substring lookups — use search_users."
  - `search_users` first line: "Search users by name or email substring."
  - `search_users` anti-pattern: "Do NOT use when the user supplies a known user_id — use get_user."

**Pass criteria**: Reading either description alone unambiguously identifies the right tool for a given query. No overlapping anti-patterns ("Do NOT use for X" on one tool implies "use the other for X" on the sibling).

---

## Baseline (no-skill comparison)

For each scenario, attempt the same task without invoking this skill. Typical no-skill failures:
- Scenario 1: missing `Do NOT use` clause; `body` lacks example; no `Returns:`
- Scenario 2: validator-style audit is skipped; only surface fixes ("add a docstring") are suggested
- Scenario 3: rewrites only one of the two tools, leaving the overlap

A skilled run should beat the baseline on every scenario by surfacing at least one issue the baseline missed.
