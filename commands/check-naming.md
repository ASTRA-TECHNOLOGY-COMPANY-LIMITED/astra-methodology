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
| `data/standard_terms.json` | 13,176 standard terms | Column name standard compliance check |
| `data/standard_words.json` | 3,284 standard words | Forbidden word detection, word combination check |
| `data/standard_domains.json` | 123 standard domains | Data type/length check |

Detailed guide: `skills/data-standard/data-standard-terminology-guide.md`

## Check Targets

- JPA/Hibernate entity classes (@Column, @Table annotations)
- TypeORM/Prisma entity/schema definitions
- SQLAlchemy/Django model definitions
- SQL DDL (CREATE TABLE, ALTER TABLE)
- DTO/VO class field names

## Check Items

### 1. Standard Term Compliance
- Check whether column names match `공통표준용어영문약어명` in `data/standard_terms.json`
- Suggest the most similar standard term when there is a mismatch
- Check whether abbreviations are composed of `공통표준단어영문약어명` combinations from `data/standard_words.json`

### 2. Suffix Pattern Consistency
- Whether date-related columns use `_YMD` or `_DT` suffix
- Whether amount-related columns use `_AMT` or `_PRC` suffix
- Whether name-related columns use `_NM` suffix
- Whether code-related columns use `_CD` suffix
- Whether boolean-related columns use `_YN` suffix
- Whether number-related columns use `_NO` suffix
- Whether content-related columns use `_CN` suffix
- Whether count-related columns use `_CNT` suffix
- Whether rate-related columns use `_RT` suffix
- Whether sequence-related columns use `_SN` suffix
- Whether address-related columns use `_ADDR` suffix
- Check whether the meaning matches the suffix

### 3. Domain Rule Compliance
- Check whether data types and lengths match domain definitions by referencing `data/standard_domains.json`
- Report length mismatch if VARCHAR(50) but domain is Name-V100
- Check CHAR vs VARCHAR distinction
- Check NUMERIC precision/scale

### 4. Forbidden Word Detection
- Detect based on the `금칙어목록` field in `data/standard_words.json`
- Suggest standard terms from `이음동의어목록` when forbidden words are found

### 5. Table Name Rules
- Check prefixes: TB_ (general) / TC_ (code) / TH_ (history) / TL_ (log) / TR_ (relation)
- Report missing or misused prefixes
- Report prefix-table type mismatches (e.g., using TB_ for a history table)

### 6. English Abbreviation Naming Rules
- Check uppercase usage
- Check underscore separator usage
- Check whether classifier words are placed at the end
- Check within 30 characters

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
