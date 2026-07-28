---
description: Checks code for coding convention compliance and reports violations
argument-hint: "<file path or directory>"
allowed-tools: Read, Glob, Grep
---

# Coding Convention Check

Check coding convention compliance for $ARGUMENTS.

> For in-depth analysis, the `convention-validator` agent can be used.

## Check Procedure

1. Read the target files and determine the language by file extension
2. Refer to the corresponding language's coding convention reference document
3. Check the following items in order

## Language Detection and Reference Documents

| Extension | Language | Reference Document |
|---|---|---|
| `.java` | Java | `${CLAUDE_PLUGIN_ROOT}/skills/coding-convention/java-coding-convention.md` |
| `.ts`, `.tsx` | TypeScript | `${CLAUDE_PLUGIN_ROOT}/skills/coding-convention/typescript-coding-convention.md` |
| `.tsx`, `.ts` (RN project) | React Native | `${CLAUDE_PLUGIN_ROOT}/skills/coding-convention/react-native-coding-convention.md` |
| `.py` | Python | `${CLAUDE_PLUGIN_ROOT}/skills/coding-convention/python-coding-convention.md` |
| `.css`, `.scss`, `.sass` | CSS/SCSS | `${CLAUDE_PLUGIN_ROOT}/skills/coding-convention/css-scss-coding-convention.md` |

> **React Native Detection**: If `package.json` contains `react-native` or `expo` in dependencies, apply React Native convention as a complementary layer on top of TypeScript convention for `.tsx`/`.ts` files.

Before checking, the corresponding language's reference document must be read to confirm detailed rules.

## Check Items — Rule Source (single source of truth)

Do **not** rely on a rule list inlined here. For the file's detected language, load the matching per-language rule file and check the code against every rule it defines:

- Java → `${CLAUDE_PLUGIN_ROOT}/skills/coding-convention/java-coding-convention.md`
- TypeScript → `${CLAUDE_PLUGIN_ROOT}/skills/coding-convention/typescript-coding-convention.md`
- React Native → `${CLAUDE_PLUGIN_ROOT}/skills/coding-convention/react-native-coding-convention.md` (complementary layer on top of the TypeScript rule file)
- Python → `${CLAUDE_PLUGIN_ROOT}/skills/coding-convention/python-coding-convention.md`
- CSS/SCSS → `${CLAUDE_PLUGIN_ROOT}/skills/coding-convention/css-scss-coding-convention.md`

Each rule file is the authoritative, up-to-date checklist (prohibited patterns, naming, formatting, line-length, import order, etc.). Read it in full and apply its rules verbatim — restating them here would create a drifting copy. For a deeper, agent-driven pass over the same rule files, delegate to the `convention-validator` agent.

## Output Format

Report violations in the following format:

| Severity | Category | File:Line | Rule | Current Code | Suggested Fix |
|---|---|---|---|---|---|
| Error | Prohibited pattern | ... | ... | ... | ... |
| Warning | Naming | ... | ... | ... | ... |
| Info | Formatting | ... | ... | ... | ... |

Severity criteria:
- **Error**: Prohibited pattern violations (var, any, export default, == None, bare except, ID selectors, `!important` overuse, etc.)
- **Warning**: Convention mismatches (naming, line length, indentation, property order, etc.)
- **Info**: Improvement recommendations (missing Javadoc, missing docstrings, BEM mismatches, etc.)

Report total violation count and summary by severity/category at the end.
