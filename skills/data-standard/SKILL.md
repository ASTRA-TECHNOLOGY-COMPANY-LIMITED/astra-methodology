---
name: data-standard
description: >
  Automatically applies the public data standard terminology dictionary when writing
  database tables, entity classes, SQL, and migration files. Uses standard English
  abbreviations for DB column names, table names, and variable names, and complies
  with domain rules. Used when writing ORM entities, DTOs, VOs, SQL DDL, and schema definitions.
---

# Data Standard Terminology Application Skill

When writing DB-related code, you must follow the standards below.
For the detailed guide, refer to data-standard-terminology-guide.md in this directory.

## Target Files

- JPA/Hibernate entity classes (.java)
- TypeORM/Prisma entities/schemas (.ts)
- SQLAlchemy/Django models (.py)
- SQL files (.sql)
- Migration files
- DTO/VO classes

## Core Rules

### 1. Use standard terminology English abbreviations for column names

Search for the Korean term name in the standard terminology dictionary (`data/standard_terms.json`) and use the English abbreviation.

Key examples:
| Korean Term | English Abbreviation (physical column name) | Domain |
|---|---|---|
| 고객명 (Customer Name) | CSTMR_NM | 명V100 |
| 가입일자 (Join Date) | JOIN_YMD | 연월일C8 |
| 등록일시 (Registration DateTime) | REG_DT | 연월일시분초D |
| 사업자등록번호 (Business Registration Number) | BRNO | 사업자등록번호C10 |
| 결제금액 (Payment Amount) | STLM_AMT | 금액N15 |
| 사용여부 (Use Status) | USE_YN | 여부C1 |
| 상태코드 (Status Code) | STTS_CD | 코드C3 |
| 전화번호 (Phone Number) | TELNO | 전화번호V11 |
| 우편번호 (Postal Code) | ZIP | 우편번호C5 |
| 도로명주소 (Road Name Address) | RDNMADR | 주소V200 |
| 상세주소 (Detailed Address) | DTL_ADDR | 주소V320 |
| 처리내용 (Processing Content) | PRCS_CN | 내용V1000 |
| 변경사유 (Change Reason) | CHG_RSN | 내용V500 |

### 2. Follow suffix patterns

| Suffix | Meaning | Example |
|---|---|---|
| _YMD | Date (year-month-day) | REG_YMD (Registration Date) |
| _DT | DateTime | REG_DT (Registration DateTime) |
| _YM | Year-Month | ACNT_YM (Account Year-Month) |
| _YR | Year | BSNS_YR (Business Year) |
| _AMT | Amount | STLM_AMT (Payment Amount) |
| _PRC | Price | SUPLY_PRC (Supply Price) |
| _NM | Name | CSTMR_NM (Customer Name) |
| _CD | Code | STTS_CD (Status Code) |
| _NO | Number | SEQ_NO (Sequence Number) |
| _CN | Content | PRCS_CN (Processing Content) |
| _CNT | Count | DEAL_CNT (Transaction Count) |
| _RT | Rate | TAX_RT (Tax Rate) |
| _YN | Yes/No | USE_YN (Use Status) |
| _SN | Sequence | SRT_SN (Sort Order) |
| _ADDR | Address | DTL_ADDR (Detailed Address) |

### 3. Table name rules

| Prefix | Purpose | Example |
|---|---|---|
| TB_ | General table | TB_CSTMR (Customer) |
| TC_ | Code table | TC_STTS_CD (Status Code) |
| TH_ | History table | TH_CSTMR_CHG (Customer Change History) |
| TL_ | Log table | TL_LOGIN (Login Log) |
| TR_ | Relation table | TR_CSTMR_PRDT (Customer-Product Relation) |

### 4. Data type mapping based on domain rules

#### Date/Time
| Domain | DB Type | Java | TypeScript | Python |
|---|---|---|---|---|
| 연월일시분초D | DATETIME | LocalDateTime | Date | datetime |
| 연월일C8 | CHAR(8) | String | string | str |
| 연월C6 | CHAR(6) | String | string | str |
| 연도C4 | CHAR(4) | String | string | str |

#### Amount/Number
| Domain | DB Type | Java | TypeScript | Python |
|---|---|---|---|---|
| 금액N15 | NUMERIC(15) | BigDecimal | number | Decimal |
| 가격N10 | NUMERIC(10) | BigDecimal | number | Decimal |
| 수N10 | NUMERIC(10) | Long | number | int |
| 수N5 | NUMERIC(5) | Integer | number | int |
| 율N5,2 | NUMERIC(5,2) | BigDecimal | number | Decimal |

#### String
| Domain | DB Type | Java | TypeScript | Python |
|---|---|---|---|---|
| 명V100 | VARCHAR(100) | String | string | str |
| 명V200 | VARCHAR(200) | String | string | str |
| 내용V1000 | VARCHAR(1000) | String | string | str |
| 내용V4000 | VARCHAR(4000) | String | string | str |
| 주소V200 | VARCHAR(200) | String | string | str |

#### Code/Boolean
| Domain | DB Type | Java | TypeScript | Python |
|---|---|---|---|---|
| 코드C1~C7 | CHAR(n) | String | string | str |
| 코드V20 | VARCHAR(20) | String | string | str |
| 여부C1 | CHAR(1) | String | "Y" \| "N" | str |

### 5. Forbidden words must not be used

Words in the `금칙어목록` (forbidden word list) field of the standard word dictionary (`data/standard_words.json`) are prohibited.
When found, replace them with the standard word from the `이음동의어목록` (synonym list).

### 6. How to look up terminology

When DB-related naming is needed:

1. Search by Korean `공통표준용어명` (common standard term name) in `data/standard_terms.json`
2. Use the `공통표준용어영문약어명` (common standard term English abbreviation) value as the column name
3. Determine the data type and length from the `공통표준도메인명` (common standard domain name)
4. If not found in the standard terms, combine individual word abbreviations from `공통표준단어영문약어명` in `data/standard_words.json`

### 7. JPA Entity Example

```java
@Entity
@Table(name = "TB_CSTMR")
public class Customer {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  @Column(name = "CSTMR_SN")
  private Long customerSn;

  @Column(name = "CSTMR_NM", length = 100, nullable = false)
  private String customerNm;

  @Column(name = "BRNO", length = 10, columnDefinition = "CHAR(10)")
  private String brno;

  @Column(name = "TELNO", length = 11)
  private String telno;

  @Column(name = "JOIN_YMD", length = 8, columnDefinition = "CHAR(8)")
  private String joinYmd;

  @Column(name = "REG_DT")
  private LocalDateTime regDt;

  @Column(name = "USE_YN", length = 1, columnDefinition = "CHAR(1) DEFAULT 'Y'")
  private String useYn;
}
```
