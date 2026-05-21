# Validation Grep Patterns

These patterns live here, not in `SKILL.md`, because the regex meta-characters would false-positive against themselves if grep ever scanned `SKILL.md`. Same rationale as `skill-author/references/anti-pattern-grep.md`.

> Run from the repository root. Replace `<path>` with the file or directory under inspection.

---

## A1 — First-line verb-led summary

A correct description starts with a capitalized verb followed by a noun phrase.

```bash
# FAIL if the first description-line starts with "I " or "This tool" or "Helps"
grep -nE '^[[:space:]]*(description\s*=\s*"""|description:\s*>)[[:space:]]*$' <path> -A 1 \
  | grep -E '^\s*(I |This tool|Helps|You can|Does stuff)'
```

If the second match is non-empty, the description fails A1.

---

## A2 — Anti-pattern clause present

```bash
grep -nE 'Do NOT use|do not use this tool|Skip this tool when|Avoid using this' <path>
```

If the count is **0** for a given tool block, it fails A2.

---

## A3 — Synonyms / colloquial coverage

There is no purely syntactic check; the heuristic is "the description body contains at least three distinct verb or noun synonyms". A quick approximation:

```bash
# Word count inside description triple-quoted blocks (Python)
python3 -c "
import re, sys, pathlib
src = pathlib.Path(sys.argv[1]).read_text()
for m in re.finditer(r'\"\"\"(.+?)\"\"\"', src, re.S):
    words = set(re.findall(r'[a-zA-Z]+', m.group(1).lower()))
    print(len(words), '←', m.group(1)[:60].replace('\n',' '))
" <path>
```

Description blocks with < 25 distinct words usually fail A3. Treat this as a soft warning, not a hard fail.

---

## A4 — Per-parameter examples

```bash
# Pydantic — Field(... description="..." ...)
grep -nE 'Field\([^)]*description\s*=\s*"[^"]*"' <path> \
  | grep -vE '(e\.g\.|example:|\\[.+?\\])'

# Zod — .describe("...")
grep -nE '\.describe\("[^"]*"\)' <path> \
  | grep -vE '(e\.g\.|example:|\\[.+?\\])'
```

Any matching line that does **not** contain `e.g.`, `example:`, or a bracketed sample fails A4 for that parameter.

---

## A5 — Enum constraints where applicable

This pattern is intent-based — it finds free strings that *look like* they should have been enums:

```bash
# Free str params named like enum candidates (status/type/kind/mode/level)
grep -nE '(status|type|kind|mode|level|tier|priority)\s*:\s*str' <path>

# Same for TypeScript
grep -nE '(status|type|kind|mode|level|tier|priority)\s*:\s*z\.string\(' <path>
```

Each match is a candidate for `Literal[...]` (Python) or `z.enum([...])` (TypeScript). Confirm with the author before converting — some intentionally remain open strings.

---

## A6 — Return shape documented

```bash
grep -nE 'Returns?:' <path>
```

If the docstring or description body contains no `Returns:` (or `Return value:`) section, the tool fails A6.

---

## Side-effect detection

```bash
grep -nE '(create|update|delete|insert|remove|send|charge|publish|notify)_[a-z_]+' <path>
```

Any tool whose function name matches one of these verbs is a side-effect tool and is subject to the extra requirements in `SKILL.md` §6 (self-identifying verb, sibling tool named in anti-pattern). Missing attributes auto-escalate to P0.

---

## Composing a full PASS / FAIL report

Pseudo-shell:

```bash
for tool in $(list_tools <path>); do
  a1=$(check_first_line_verb <tool>)
  a2=$(grep -c 'Do NOT use\|Skip this tool when' <tool>)
  a3=$(distinct_word_count <tool>)
  a4=$(check_examples <tool>)
  a5=$(check_enum_candidates <tool>)
  a6=$(grep -c 'Returns:' <tool>)
  emit_row $tool $a1 $a2 $a3 $a4 $a5 $a6
done
```

The exact implementation depends on how tools are split across files in the target project — usually 1 tool per function for LangChain, or N tools per file for MCP servers.
