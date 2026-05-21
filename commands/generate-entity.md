---
description: Generates standard-compliant entity code from Korean table/column definitions
argument-hint: "<Korean table definition> (e.g., 고객 테이블: 고객명, 고객번호, 가입일자)"
allowed-tools: Read, Write, Glob, Grep
---

# Standard Entity Generation

Generate standard-compliant entity code based on the Korean table/column definition provided in $ARGUMENTS.

## Reference Data

| File | Purpose |
|---|---|
| `data/standard_terms.json` | Korean term -> English abbreviation, domain mapping |
| `data/standard_words.json` | Individual word abbreviation, forbidden word check |
| `data/standard_domains.json` | Data type/length mapping per domain |

## Input Format Examples

Various input formats are supported:
- "고객 테이블: 고객명, 고객번호, 생년월일, 이메일주소, 가입일자, 사용여부"
- "주문(고객순번, 주문일자, 결제금액, 상태코드, 배송주소)"
- Tabular column lists

## Generation Procedure

### Step 1: Term Mapping
Search each Korean column name in `data/standard_terms.json`.
If a standard term exists, retrieve the English abbreviation, domain, and data type.
If no standard term exists, combine words from `data/standard_words.json`.

### Step 2: Mapping Table Output
| Korean Column Name | DB Column (Abbreviation) | Full Field Name | Domain | Data Type | Source |
|---|---|---|---|---|---|
| (term) | (abbreviation) | (full English name) | (domain) | (type) | Standard term / Word combination |

### Step 3: Code Generation
Generate an entity class matching the project language.
If the language is unclear, generate Java JPA by default and also provide TypeScript and Python.

**Field naming rule**: Physical DB column names use standard abbreviations (`CSTMR_NM`), but entity/DTO/interface field names must use **full English names** (`customerName`). Expand each standard word abbreviation to its full English name from `data/standard_words.json`. Apply `lowerCamelCase` for Java/TypeScript, `snake_case` for Python.

**Boolean field rule**: `_YN` (yes/no flag) columns must use `BOOLEAN` type in both DDL and entity code. Field names use `is`/`has` prefix with a past participle or adjective (e.g., `USE_YN` → `isUsed`, `DEL_YN` → `isDeleted`).

#### Java (JPA)
- `@Entity`, `@Table(name = "TB_...")` annotations
- `@Column(name = "...", length = ...)` for physical column name mapping
- CHAR types must specify `columnDefinition`
- Java type mapping based on domain (BigDecimal, LocalDateTime, String, etc.)
- **Field names use full English** (e.g., `private String customerName`, not `customerNm`)
- **`_YN` fields use `boolean`** (e.g., `private boolean isUsed`, not `String useYn`)
- Comply with Google Java Style Guide (ref: `skills/coding-convention/java-coding-convention.md`)

#### TypeScript (TypeORM)
- `@Entity()`, `@Column()` decorators
- Type mapping based on standard suffixes
- **Field names use full English** (e.g., `customerName: string`, not `customerNm`)
- **`_YN` fields use `boolean`** (e.g., `isUsed: boolean`)
- Comply with Google TypeScript Style Guide (ref: `skills/coding-convention/typescript-coding-convention.md`)

#### Python (SQLAlchemy)
- `Column()`, `Table()` definitions
- **Field names use full English snake_case** (e.g., `customer_name`, not `customer_nm`)
- **`_YN` fields use `bool`** (e.g., `is_used: Mapped[bool]`)
- Comply with PEP 8 (ref: `skills/coding-convention/python-coding-convention.md`)

### Step 4: DDL Generation
Also generate SQL DDL applying the standard table name rules (TB_ prefix).
`_YN` (yes/no flag) columns must use `BOOLEAN` type with `DEFAULT true` or `DEFAULT false`.

```sql
CREATE TABLE TB_{TABLE_ABBR} (
    {COL_ABBR} {DATA_TYPE}({LENGTH}) [NOT NULL] [DEFAULT ...] COMMENT '{Korean column name}',
    USE_YN BOOLEAN DEFAULT true COMMENT '사용여부',
    ...
);
```

## Additional Rules

- Include default audit columns in all tables: REG_DT (registration datetime), CHG_DT (modification datetime)
- If USE_YN (use status) column is specified, set BOOLEAN DEFAULT true
- If DEL_YN (deletion status) column is specified, set BOOLEAN DEFAULT false
- PK is auto-generated with table name_SN (sequence number) pattern (if not explicitly specified)
- If a word matches the forbidden word dictionary (`금칙어목록` in `data/standard_words.json`), replace it with the standard term
