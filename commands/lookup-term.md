---
description: Looks up English abbreviation, domain, and data type for a Korean term from the standard term dictionary
argument-hint: "<Korean term or English abbreviation> (e.g., 고객명, 등록일시, CSTMR_NM)"
allowed-tools: Read, Bash
---

# Standard Term Lookup

Look up the standard term corresponding to "$ARGUMENTS".

## Reference Data

| File | Content | Purpose |
|---|---|---|
| `data/standard_terms.json` | 13,176 standard terms | Korean term name -> English abbreviation, domain, type |
| `data/standard_words.json` | 3,284 standard words | Individual word abbreviation, combination suggestions |
| `data/standard_domains.json` | 123 standard domains | Type/length details per domain |

## Lookup Procedure

> **Dataset caveat**: in the bundled dataset the Korean name fields (`공통표준용어명`, `공통표준단어명`) are **empty in every row**. Korean input is therefore matched against `이음동의어목록` (synonyms — this is where the Korean names live) and `공통표준용어설명` (description); English/abbreviation input against `공통표준용어영문약어명`. Korean field names require jq bracket form (`.["필드명"]` — bare `.필드명` is a jq syntax error). Rows live under `.data[]`.

1. Search `data/standard_terms.json` via targeted `jq` (13K rows — never read the whole file):
   ```bash
   # Korean input → synonym/description match (rows live under .data[])
   jq -r --arg q "$ARGUMENTS" '.data[] | select((.["이음동의어목록"] // "" | contains($q)) or (.["공통표준용어설명"] // "" | contains($q)))' data/standard_terms.json | head -80
   # English/abbreviation input → abbreviation match
   jq -r --arg q "$ARGUMENTS" '.data[] | select(.["공통표준용어영문약어명"] // "" | ascii_upcase | contains($q | ascii_upcase))' data/standard_terms.json | head -80
   ```
2. If exactly one row matches, output the detailed information (use the first synonym as the display term name, since the Korean name field is empty)
3. If several rows match, show up to 10 partial match results
4. If no term is found, search individual words in `data/standard_words.json` the same way (`이음동의어목록` / `공통표준단어설명` / `공통표준단어영문약어명` under `.data[]`) and suggest combinations

## Output Format

### Exact Match Found

| Item | Value |
|---|---|
| **Standard Term Name** | (Korean term name) |
| **English Abbreviation** | (physical column name) |
| **Term Description** | (description) |
| **Domain** | (domain name) |
| **Data Type** | (type + length) |
| **Storage Format** | (format) |
| **Display Format** | (screen format) |
| **Allowed Values** | (if applicable) |
| **Synonyms** | (if applicable) |

### Type Mapping by Language

| Language | Type | Notes |
|---|---|---|
| Java | (Java type + JPA annotation) | |
| TypeScript | (TS type) | |
| Python | (Python type) | |

### Partial Match Found

Display partial match results in a table:

| # | Term Name | English Abbreviation | Domain |
|---|---|---|---|
| 1 | ... | ... | ... |

### No Term Found

Suggest by combining individual words:

"The entered term is not found in the standard term dictionary. The following is suggested based on individual word combinations:"

| Korean Word | English Abbreviation | Notes |
|---|---|---|
| ... | ... | ... |

**Suggested Column Name**: (combined English abbreviation)
