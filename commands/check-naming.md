---
description: Checks whether DB-related code naming complies with the standard term dictionary
argument-hint: "<file path or directory>"
allowed-tools: Read, Glob, Grep
---

# Standard Naming Check

Check whether DB-related naming in $ARGUMENTS complies with standards.

> For in-depth analysis, the `naming-validator` agent can be used.

## Reference Data

| File | Content | Purpose |
|---|---|---|
| `${CLAUDE_PLUGIN_ROOT}/data/standard_terms.json` | 13,176 standard terms | Column name standard compliance check |
| `${CLAUDE_PLUGIN_ROOT}/data/standard_words.json` | 3,284 standard words | Forbidden word detection, word combination check |
| `${CLAUDE_PLUGIN_ROOT}/data/standard_domains.json` | 123 standard domains | Data type/length check |

Detailed guide: `${CLAUDE_PLUGIN_ROOT}/skills/data-standard/data-standard-terminology-guide.md`

## Check Targets

- JPA/Hibernate entity classes (@Column, @Table annotations)
- TypeORM/Prisma entity/schema definitions
- SQLAlchemy/Django model definitions
- SQL DDL (CREATE TABLE, ALTER TABLE)
- DTO/VO class field names

## Check Items — Rule Source (single source of truth)

Do **not** rely on a rule list inlined here. The authoritative naming rules (standard-term compliance, suffix patterns, domain type/length, forbidden words, table-name prefixes, and abbreviation-formation rules) live in the `data-standard` skill and are backed by the reference JSON:

- Read `${CLAUDE_PLUGIN_ROOT}/skills/data-standard/data-standard-terminology-guide.md` for the full rule set and apply every rule it defines.
- Resolve each column/table against the dictionaries with targeted `jq` queries (the files are large — never load them whole):

Rows live under `.data[]`, and Korean field names require bracket notation in jq (`.["..."]`). Look a column/table up by its **English abbreviation** — the abbreviation fields are the populated, indexable ones:

```bash
# Is this column abbreviation a registered standard term? (returns domain + description)
jq -r '.data[] | select(.["공통표준용어영문약어명"]=="RAFOS_NM") | {abbr:.["공통표준용어영문약어명"], domain:.["공통표준도메인명"], desc:.["공통표준용어설명"]}' "${CLAUDE_PLUGIN_ROOT}/data/standard_terms.json"

# Standard word: abbreviation, forbidden words, synonyms (look up by the word's English abbreviation)
jq -r '.data[] | select(.["공통표준단어영문약어명"]=="RAFOS") | {abbr:.["공통표준단어영문약어명"], forbidden:.["금칙어목록"], synonyms:.["이음동의어목록"]}' "${CLAUDE_PLUGIN_ROOT}/data/standard_words.json"

# Domain type/length definition (domains file keys the row on 도메인명, e.g. "명V100")
jq -r '.data[] | select(.["도메인명"]=="명V100")' "${CLAUDE_PLUGIN_ROOT}/data/standard_domains.json"
```

Table-prefix rules (`TB_`/`TC_`/`TH_`/`TL_`/`TR_`) and the standard suffixes (`_YMD`, `_DT`, `_AMT`, `_NM`, `_CD`, `_YN`, `_NO`, `_CN`, `_SN`, `_ADDR`, …) are defined in that guide — read it rather than restating them here, so this command stays a thin dispatcher over the one rule source. For a deeper, agent-driven pass over the same dictionaries, delegate to the `naming-validator` agent.

## Output Format

Report check results in the following format:

| Type | Location | Current Naming | Standard Naming | Basis |
|---|---|---|---|---|
| Non-standard column name | User.java:25 | `cust_name` | `CSTMR_NM` | Standard term: Customer name |
| Forbidden word usage | Order.java:30 | `reg_date` | `REG_YMD` | Forbidden word 'date' -> Standard word 'date (YMD)' |
| Domain mismatch | User.java:28 | `VARCHAR(50)` | `VARCHAR(100)` | Based on Name-V100 domain |
| Suffix error | User.java:32 | `CSTMR_NAME` | `CSTMR_NM` | Name suffix should be _NM |
| Table name error | User.java:10 | `CUSTOMER` | `TB_CSTMR` | TB_ prefix + standard abbreviation |
| Abbreviation rule violation | Order.java:15 | `orderStatus` | `ORD_STTS` | Uppercase + underscore |

Report check summary at the end:
- Total number of checked items (tables, columns)
- Number of compliant items
- Number of violations (by type)
- Compliance rate (%)
