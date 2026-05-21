---
name: tool-author
description: >
  Authors and validates LLM tool descriptions and input schemas (Anthropic Tool
  Use, MCP servers, LangChain @tool, Pydantic, Zod). Use when the user mentions
  "tool description", "function calling", "MCP tool", "Pydantic schema", "Zod
  schema", "@tool decorator", "input_schema", "tool spec", "툴 정의", "함수 호출
  스키마", or when editing files that define LLM tool surfaces. Enforces the six
  required attributes (one-line summary, anti-pattern, synonyms, parameter
  examples, enum constraints, return shape) and blocks the seven known failure
  modes — wrong-tool selection, skipped tool, malformed arguments, retry loops,
  user-intent bypass, wrong side-effect, and un-auditable traces. For authoring
  ASTRA SKILL.md files use /skill-author instead — this skill is for *runtime*
  LLM tool surfaces, not for skill files themselves.
paths:
  - "tools/**/*.py"
  - "tools/**/*.ts"
  - "mcp/**/*.py"
  - "mcp/**/*.ts"
  - "**/tools.py"
  - "src/**/*.tool.ts"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion
---

# Tool Author

Writes a new LLM tool surface (description + input schema) or refactors an existing one to satisfy the **6 required attributes** documented in [`references/six-attributes.md`](references/six-attributes.md). The validator catches the **7 failure modes** in [`references/failure-modes.md`](references/failure-modes.md). For Python/TypeScript rendering, see [`references/python-pydantic.md`](references/python-pydantic.md) and [`references/typescript-zod.md`](references/typescript-zod.md).

> **Scope**: this skill is for *runtime LLM tool surfaces* that the model invokes during a session — Anthropic `tools` array, MCP `server.tool()`, LangChain `@tool`, OpenAI function-calling schemas. It is **not** for authoring ASTRA `SKILL.md` files (use `/skill-author`).

---

## 0. Mode Decision

Determine the mode from arguments or `AskUserQuestion`:

| Mode | Trigger | Entry point |
|------|---------|-------------|
| **new** | "write new tool", "add MCP tool", empty target file | Step 1 |
| **refactor** | existing tool file passed as argument, "improve this tool description" | Step 4 |
| **validate** | "lint this tool", "check tool description", `paths` auto-trigger | Step 5 |

### 0.A Auto-trigger surface

The frontmatter `paths:` covers the most common LLM-tool-file conventions:

| Glob | Matches |
|------|---------|
| `tools/**/*.{py,ts}` | dedicated tool directory |
| `mcp/**/*.{py,ts}` | MCP server projects |
| `**/tools.py` | single-file Python convention |
| `src/**/*.tool.ts` | naming-prefix TypeScript convention |

If a project keeps tool definitions elsewhere (e.g. `api/handlers/tools/`, `lib/agents/`), append those globs to the frontmatter. Avoid catch-alls like `**/*.py` — they drown out other skills.

---

## 1. Collect Tool Metadata (new mode)

Ask the four questions at once with `AskUserQuestion`:

1. **Tool name** (snake_case for Python tools, camelCase for TypeScript)
2. **One-line purpose** (verb-led, ≤ 80 chars — becomes the description's first line)
3. **Language**: Python (Pydantic) / TypeScript (Zod) / JSON Schema (raw)
4. **Side-effect risk**: read-only / writes data / external API with cost / payments

If side-effect risk ≥ "writes data", apply the special handling in Step 6.

---

## 2. Draft the Description — Apply the 6 Attributes

The description is the *only* signal the LLM uses to decide between tools. Apply each attribute from [`references/six-attributes.md`](references/six-attributes.md) in order:

```
<verb-led one-line summary, ≤ 80 chars>

Use when <situation 1>, <situation 2>, or when the user mentions
"<keyword>", "<synonym>", "<colloquial>".

Do NOT use for <competing-domain> — use <sibling_tool> instead.

Returns: <shape, units, ordering, nullability>.
```

Per-parameter, attach an example value and (where applicable) an enum:

```
<param_name>: <type> — <one-line description>. e.g. '<example>', '<example>'
```

### 2.1 Self-check before moving on

| Question | If "no" |
|----------|---------|
| Does the first line start with a verb? | Rewrite |
| Is there at least one `Do NOT use` clause? | Add one |
| Are synonyms / colloquial phrasings covered? | Add them |
| Does every parameter have an example? | Add examples |
| Are finite value spaces declared as enums? | Convert to `Literal` / `z.enum` |
| Is the return shape documented? | Document it |

---

## 3. Render the Schema

Switch on the language chosen in Step 1:

- **Python**: follow [`references/python-pydantic.md`](references/python-pydantic.md). Prefer Pydantic `BaseModel` over hand-written JSON Schema. The model docstring carries the description; per-field `Field(description=...)` carries parameter docs.
- **TypeScript**: follow [`references/typescript-zod.md`](references/typescript-zod.md). Compose the description string with `[...].join("\n")` for readability; co-locate it with the Zod schema.
- **JSON Schema (raw)**: follow the hand-written example in `python-pydantic.md` §7. Same six attributes apply; the validator does not care where the schema came from.

Keep nesting ≤ 2 levels. If the input shape would need 3+ levels, flatten it with prefixed keys.

---

## 4. Refactor Mode

1. Read the target file (`Read`)
2. Extract the existing description string and schema (regex on `description = """..."""` or the `description:` key)
3. Run the validation grep patterns from [`references/validation-greps.md`](references/validation-greps.md)
4. Classify each violation:
   - **P0** (auto-fix, no confirmation): missing first-line verb, vague first sentence ("does stuff", "helps with"), missing return shape on a read-only tool
   - **P1** (confirm via `AskUserQuestion`): no anti-pattern, no synonyms, free-string where enum is possible
   - **P2** (report only): no example values on numeric fields, nesting > 2 levels
5. Apply P0 immediately; ask before applying P1; emit a report for P2

For side-effect tools, *any* missing attribute escalates to P0 — see Step 6.

---

## 5. Validate Mode

Run the validation pass without modifying files. Use it as a CI gate, a PR pre-check, or whenever a `paths`-matched file is edited.

```bash
# From the repository root
grep -nE "description\s*=\s*['\"]" <path>            # locate descriptions
grep -nE "Field\(" <path>                            # locate Pydantic fields
grep -nE "\.describe\(" <path>                       # locate Zod descriptions
```

The full pattern list — including the "Do NOT use" detection, enum detection, and return-shape detection — is in [`references/validation-greps.md`](references/validation-greps.md). The patterns live in a reference file because grep meta-characters inside SKILL.md body would false-positive against themselves.

Emit a table:

```
| Tool name       | A1 | A2 | A3 | A4 | A5 | A6 | Severity |
|-----------------|----|----|----|----|----|----|----------|
| create_issue    | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | PASS     |
| search_users    | ✓  | ✗  | ✗  | ✓  | n/a| ✓  | P1       |
```

`Ax` columns map 1-to-1 to the six attributes. `n/a` is allowed when an attribute does not apply (e.g., a tool with no enumerable fields).

---

## 6. Side-Effect Tools — Special Handling

Tools that mutate state (DB writes, payments, sent messages, file creation) are the most expensive to get wrong. Apply two extra requirements on top of the six attributes:

1. **Self-identify**: the first line must contain a verb that signals mutation — `Create`, `Update`, `Delete`, `Send`, `Charge`, `Publish`. Avoid neutral verbs like `Process`, `Handle`, `Run`.
2. **Anti-pattern names a sibling**: the `Do NOT use` clause must point at the read-only sibling tool by name. Example: *"Do NOT use to check whether an issue exists — use get_issue."*

In the validator, side-effect tools get any missing attribute auto-escalated to **P0**. Severity rationale lives in `failure-modes.md` §"Why side-effect tools are special".

If the side-effect is irreversible (charges money, sends an email, posts to Slack), also recommend `disable-model-invocation: true` at the calling layer, or — for MCP — a confirmation step before the side effect fires.

---

## 7. Final Checklist

Before declaring the tool done:

- [ ] Description first line is verb-led and ≤ 80 chars
- [ ] At least one `Do NOT use for ... — use <other_tool> instead.` clause
- [ ] Synonyms / colloquial keywords covered in the description body
- [ ] Every parameter has an `e.g.` example or a `Literal` / `z.enum` constraint
- [ ] Return shape documented with units, ordering, and nullability
- [ ] Schema nesting ≤ 2 levels
- [ ] No `Any` / `unknown` / `**kwargs` / `z.record(z.unknown())` as a catch-all
- [ ] (Side-effect tools) self-identifying verb in first line; sibling tool named in anti-pattern
- [ ] Validator (`Step 5`) reports PASS

If any item fails, return to Step 2 (refactor mode) for the offending tool.

---

## 8. Evaluation Scenarios

Per ASTRA BP §9, write *at least 3* scenarios in `references/evals.md` covering:

1. **Happy path** — well-formed description, validator returns PASS
2. **Side-effect edge case** — destructive tool with weak anti-pattern, validator returns P0
3. **Ambiguous sibling pair** — `get_x` vs `search_x` with overlapping descriptions, validator flags the overlap

Baseline by running the same scenarios without this skill and comparing description quality.

---

**Reference index**

| Need | File |
|------|------|
| The 6 attributes (SSoT) | [`references/six-attributes.md`](references/six-attributes.md) |
| Failure modes + severity ladder | [`references/failure-modes.md`](references/failure-modes.md) |
| Python / Pydantic rendering | [`references/python-pydantic.md`](references/python-pydantic.md) |
| TypeScript / Zod rendering | [`references/typescript-zod.md`](references/typescript-zod.md) |
| Validation grep patterns | [`references/validation-greps.md`](references/validation-greps.md) |
