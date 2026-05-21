# Anti-pattern Grep Recipes

The set of *exact grep commands* used for the automatic anti-pattern blocking in `skill-author` SKILL.md §4. Why these are not inlined into the main SKILL.md: backslash meta-characters would accidentally match the Windows-path detection regex and produce false positives during self-test.

## Contents
- §1 Windows path detection
- §2 Time-sensitive expression detection
- §3 First-person description detection
- §4 3-level nested reference detection
- §5 Vague verb detection
- §6 Unqualified MCP tool reference detection

Each pattern **must exclude this file itself** from the validation target (`--exclude='anti-pattern-grep.md'` or `grep ... <file> | grep -v anti-pattern-grep.md`).

---

## §1 Windows paths

```bash
grep -nE '[A-Za-z_-]+\\[A-Za-z_]' "$SKILL_FILE"
```

On match: replace with forward slashes (`scripts\\helper.py` → `scripts/helper.py`)

## §2 Time-sensitive expressions

```bash
grep -niE '(before|after|until|as of) ((jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* (19|20)[0-9]{2}|(19|20)[0-9]{2})' "$SKILL_FILE"
```

On match: split into an `## Old patterns` section + a `<details>` toggle.

## §3 First-person description

Extract only the frontmatter description block, then inspect:

```bash
awk '/^description:/,/^[a-z_-]+:/' "$SKILL_FILE" | grep -iE '\b(I (can|will|am)|you can use|let me)\b'
```

On match: rewrite in third person as "Does X. Use when..."

## §4 3-level nested references

```bash
# First check whether SKILL.md links to references/*.md, then check whether
# any references/*.md links again into another references/ inside.
grep -lE '\]\(references/' "$SKILL_FILE" | xargs -I{} dirname {} | while read dir; do
  find "$dir/references" -name '*.md' -exec grep -lE '\]\(references/|\]\(\.\./references/' {} +
done
```

On match: flatten the nested reference so it is linked directly from SKILL.md.

## §5 Vague verbs

```bash
grep -niE 'helps with|does stuff|processes things|handles things' "$SKILL_FILE"
```

On match: replace with concrete verbs (`validates`, `generates`, `extracts`, `formats`, `parses`...).

## §6 Unqualified MCP tool references

```bash
grep -nE 'mcp__[a-z_-]+__[a-z_]+' "$SKILL_FILE" | grep -v 'mcp__[a-z_-]+__'
```

Or natural-language references where the server prefix is missing (e.g. "Use bigquery_schema" without a server qualifier):

```bash
grep -niE '(?<!mcp__)(bigquery_|context7_|slack_|chrome-devtools_)' "$SKILL_FILE"
```

On match: replace with `mcp__<server>__<tool>`, or in prose use the "<ServerName>:<tool>" form.
