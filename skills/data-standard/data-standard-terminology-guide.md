# Ministry of the Interior and Safety Public Data Common Standard Terminology Guide

## 1. Overview

### 1.1 Selection Background

After researching domestic database standard terminology dictionaries, the **Ministry of the Interior and Safety Public Data Common Standard** was evaluated as the most authoritative and practical standard.

| Comparison Item | Ministry Common Standard | TTA ICT Terminology Dictionary | National Institute of Korean Language Standard Dictionary |
|---|---|---|---|
| **Purpose** | DB design and data standardization | ICT terminology definitions | Korean language standard definitions |
| **Number of terms** | 13,159 (2025.11) | Approx. 15,000 standards | Approx. 500,000 headwords |
| **DB design applicability** | Directly applicable | Reference level | Not applicable |
| **English abbreviation provided** | Provided (physical column names) | Partially provided | Not provided |
| **Domains/data types** | 112 domains defined | Not provided | Not provided |
| **Legal basis** | Public institution DB standardization guidelines | Voluntary adoption | Voluntary adoption |
| **Update cycle** | 1-2 revisions per year | As needed | As needed |
| **Distribution format** | CSV, JSON, XML, API | Web search | Web search |

### 1.2 Selection Rationale

1. **Legal binding force**: Based on the "Public Institution Database Standardization Guidelines" (Ministry of the Interior and Safety Notice No. 2023-18)
2. **Practical applicability**: Defines DB column names (English abbreviations), data types, and lengths for immediate application
3. **Systematic structure**: Standard Word + Standard Domain = Standard Term composition system
4. **Continuous expansion**: Expanded from 535 terms in 2020 to 13,159 terms in 2025
5. **Open format**: Available in CSV, JSON, XML, API formats for automation

---

## 2. Standard System Structure

The common standard is composed of **3 layers**.

```
┌─────────────────────────────────────────────────┐
│            Common Standard Term (Term)            │
│        e.g., 가입일자, 사업자등록번호               │
│                                                   │
│  ┌──────────────────┐  ┌──────────────────────┐  │
│  │  Common Standard  │  │  Common Standard     │  │
│  │  Word (Word)      │  │  Domain (Domain)     │  │
│  │  e.g., 가입, 사업자 │  │  e.g., 연월일C8, 번호V20│  │
│  └──────────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### 2.1 Composition Rules

```
Standard Term = Standard Word(s) (one or more) + Standard Domain (classifier word)

Examples:
  가입일자   = [가입] + [일자]  → Domain: 연월일C8
  사업자등록번호 = [사업자] + [등록] + [번호] → Domain: 사업자등록번호C10
  강사명     = [강사] + [명]   → Domain: 명V100
```

---

## 3. Standard Word

### 3.1 Managed Fields

| Field | Description | Example |
|---|---|---|
| 공통표준단어명 | Korean word name | 가입, 사업자, 등록 |
| 영문약어명 | English abbreviation for physical column names | JOIN, BZMN, REG |
| 영문명 | English full name | Join, Businessman, Registration |
| 설명 | Word definition | Entering a group or organization |
| 형식어 여부 | Whether it is a domain classifier word | Y/N |
| 도메인 분류명 | Domain classification name when it is a classifier word | 일자, 코드, 명, etc. |
| 금지어 목록 | List of prohibited similar words | - |

### 3.2 Standard Word Examples (Key Words)

| 한글명 | English Abbreviation | English Name | Classifier | Domain Classification |
|---|---|---|---|---|
| 가입 | JOIN | Join | N | - |
| 가격 | PRC | Price | Y | 금액 |
| 가산 | ADTN | Addition | N | - |
| 개설 | ESTBL | Establishment | N | - |
| 개시 | STRT | Start | N | - |
| 개업 | OPBIZ | Open Business | N | - |
| 거래 | DEAL | Deal | N | - |
| 건수 | CNT | Count | Y | 수 |
| 검사 | INSP | Inspection | N | - |
| 결제 | STLM | Settlement | N | - |
| 계좌 | ACT | Account | N | - |
| 고객 | CSTMR | Customer | N | - |
| 공급 | SUPLY | Supply | N | - |
| 관리 | MGMT | Management | N | - |
| 금액 | AMT | Amount | Y | 금액 |
| 기관 | INST | Institution | N | - |
| 기간 | PRD | Period | N | - |
| 기준 | STDR | Standard | N | - |
| 납부 | PAY | Payment | N | - |
| 내용 | CN | Content | Y | 내용 |
| 날짜 | DT | Date | Y | 일자 |
| 담당 | CHRG | Charge | N | - |
| 대상 | TRGT | Target | N | - |
| 등록 | REG | Registration | N | - |
| 명 | NM | Name | Y | 명 |
| 번호 | NO | Number | Y | 번호 |
| 변경 | CHG | Change | N | - |
| 사업자 | BZMN | Businessman | N | - |
| 사유 | RSN | Reason | Y | 내용 |
| 상태 | STTS | Status | N | - |
| 설명 | DC | Description | Y | 내용 |
| 수량 | QTY | Quantity | Y | 수 |
| 순서 | SN | Sequence Number | Y | 수 |
| 시작 | BGNG | Beginning | N | - |
| 신청 | APLCN | Application | N | - |
| 여부 | YN | Yes/No | Y | 여부 |
| 연도 | YR | Year | Y | 일자 |
| 유형 | TY | Type | N | - |
| 율 | RT | Rate | Y | 율 |
| 일시 | DT | DateTime | Y | 일자 |
| 일자 | YMD | Year Month Day | Y | 일자 |
| 전화번호 | TELNO | Telephone Number | Y | 번호 |
| 종료 | END | End | N | - |
| 주소 | ADDR | Address | Y | 주소 |
| 코드 | CD | Code | Y | 코드 |
| 합계 | SUM | Sum | N | - |
| 항목 | ARTCL | Article | N | - |

---

## 4. Standard Domain

### 4.1 Domain Concept

A domain is a **grouping of data type and length**.

```
Domain = Classifier Word + Data Type + Data Length

e.g., 금액N15 = 금액 (classifier) + NUMERIC (type) + 15 (length)
     명V100 = 명 (classifier) + VARCHAR (type) + 100 (length)
```

### 4.2 Domain Classification by Group

#### Date/Time Domains

| Domain Name | Data Type | Length | Storage Format | Display Format |
|---|---|---|---|---|
| 연월일시분초D | DATETIME | - | YYYYMMDDHH24MISS | YYYY-MM-DD HH:MI:SS |
| 연월일C8 | CHAR | 8 | YYYYMMDD | YYYY-MM-DD |
| 연월C6 | CHAR | 6 | YYYYMM | YYYY-MM |
| 연도C4 | CHAR | 4 | YYYY | YYYY |
| 월C2 | CHAR | 2 | MM | MM |
| 시분초C6 | CHAR | 6 | HH24MISS | HH:MI:SS |

#### Amount/Numeric Domains

| Domain Name | Data Type | Length | Decimal | Storage Format |
|---|---|---|---|---|
| 금액N15 | NUMERIC | 15 | 0 | 999999999999999 |
| 가격N10 | NUMERIC | 10 | 0 | 9999999999 |
| 수N10 | NUMERIC | 10 | 0 | 9999999999 |
| 수N5 | NUMERIC | 5 | 0 | 99999 |
| 면적N19,9 | NUMERIC | 19 | 9 | 9999999999.999999999 |
| 율N5,2 | NUMERIC | 5 | 2 | 999.99 |
| 율N7,4 | NUMERIC | 7 | 4 | 999.9999 |

#### Character Domains

| Domain Name | Data Type | Length | Purpose |
|---|---|---|---|
| 명V100 | VARCHAR | 100 | General names/titles |
| 명V200 | VARCHAR | 200 | Long names |
| 명V500 | VARCHAR | 500 | Very long names |
| 내용V500 | VARCHAR | 500 | General content/description |
| 내용V1000 | VARCHAR | 1000 | Long content |
| 내용V2000 | VARCHAR | 2000 | Very long content |
| 내용V4000 | VARCHAR | 4000 | Large content |
| 주소V200 | VARCHAR | 200 | General address |
| 주소V320 | VARCHAR | 320 | Detailed address |

#### Code Domains

| Domain Name | Data Type | Length | Purpose |
|---|---|---|---|
| 코드C1 | CHAR | 1 | 1-digit classification code |
| 코드C2 | CHAR | 2 | 2-digit classification code |
| 코드C3 | CHAR | 3 | 3-digit classification code |
| 코드C5 | CHAR | 5 | 5-digit classification code |
| 코드C7 | CHAR | 7 | 7-digit classification code |
| 코드V20 | VARCHAR | 20 | Variable-length code |
| 여부C1 | CHAR | 1 | Y/N flag |

#### Number Domains

| Domain Name | Data Type | Length | Purpose |
|---|---|---|---|
| 번호V20 | VARCHAR | 20 | General number |
| 계좌번호V20 | VARCHAR | 20 | Account number |
| 주민등록번호C13 | CHAR | 13 | Resident registration number |
| 사업자등록번호C10 | CHAR | 10 | Business registration number |
| 법인등록번호C13 | CHAR | 13 | Corporate registration number |
| 전화번호V11 | VARCHAR | 11 | Phone number |
| 우편번호C5 | CHAR | 5 | Postal code |
| 여권번호C9 | CHAR | 9 | Passport number |

---

## 5. Standard Term Examples

### 5.1 Managed Fields

| Field | Description |
|---|---|
| 공통표준용어명 | Korean term (logical column name) |
| 영문약어명 | Physical column name |
| 공통표준도메인명 | Applied domain |
| 허용범위 | Maximum/minimum values or valid values |
| 저장형식 | DB storage format |
| 표현형식 | Display format |

### 5.2 Key Standard Term List

#### Date/Time Related

| Term Name | English Abbreviation | Domain | Storage Format | Display Format |
|---|---|---|---|---|
| 가입일자 | JOIN_YMD | 연월일C8 | YYYYMMDD | YYYY-MM-DD |
| 가입일시 | JOIN_DT | 연월일시분초D | YYYYMMDDHH24MISS | YYYY-MM-DD HH:MI:SS |
| 개설일자 | ESTBL_YMD | 연월일C8 | YYYYMMDD | YYYY-MM-DD |
| 개시일자 | STRT_YMD | 연월일C8 | YYYYMMDD | YYYY-MM-DD |
| 개업일자 | OPBIZ_YMD | 연월일C8 | YYYYMMDD | YYYY-MM-DD |
| 결제일자 | STLM_YMD | 연월일C8 | YYYYMMDD | YYYY-MM-DD |
| 납부일자 | PAY_YMD | 연월일C8 | YYYYMMDD | YYYY-MM-DD |
| 등록일자 | REG_YMD | 연월일C8 | YYYYMMDD | YYYY-MM-DD |
| 등록일시 | REG_DT | 연월일시분초D | YYYYMMDDHH24MISS | YYYY-MM-DD HH:MI:SS |
| 변경일자 | CHG_YMD | 연월일C8 | YYYYMMDD | YYYY-MM-DD |
| 변경일시 | CHG_DT | 연월일시분초D | YYYYMMDDHH24MISS | YYYY-MM-DD HH:MI:SS |
| 시작일자 | BGNG_YMD | 연월일C8 | YYYYMMDD | YYYY-MM-DD |
| 신청일자 | APLCN_YMD | 연월일C8 | YYYYMMDD | YYYY-MM-DD |
| 종료일자 | END_YMD | 연월일C8 | YYYYMMDD | YYYY-MM-DD |
| 처리일자 | PRCS_YMD | 연월일C8 | YYYYMMDD | YYYY-MM-DD |
| 처리일시 | PRCS_DT | 연월일시분초D | YYYYMMDDHH24MISS | YYYY-MM-DD HH:MI:SS |
| 취소일자 | CNCL_YMD | 연월일C8 | YYYYMMDD | YYYY-MM-DD |

#### Amount/Quantity Related

| Term Name | English Abbreviation | Domain | Display Format |
|---|---|---|---|
| 가산금액 | ADTN_AMT | 금액N15 | 999,999,999,999,999 |
| 거래금액 | DEAL_AMT | 금액N15 | 999,999,999,999,999 |
| 결제금액 | STLM_AMT | 금액N15 | 999,999,999,999,999 |
| 공급가격 | SUPLY_PRC | 가격N10 | 9,999,999,999 |
| 납부금액 | PAY_AMT | 금액N15 | 999,999,999,999,999 |
| 개별공시지가 | INDIV_OALP | 가격N10 | 9,999,999,999 |
| 합계금액 | SUM_AMT | 금액N15 | 999,999,999,999,999 |

#### Name/Content Related

| Term Name | English Abbreviation | Domain |
|---|---|---|
| 강사명 | INSTR_NM | 명V100 |
| 고객명 | CSTMR_NM | 명V100 |
| 관리기관명 | MGMT_INST_NM | 명V200 |
| 담당자명 | CHRG_NM | 명V100 |
| 사업자명 | BZMN_NM | 명V100 |
| 시설명 | FCLT_NM | 명V200 |
| 처리내용 | PRCS_CN | 내용V1000 |
| 변경사유 | CHG_RSN | 내용V500 |

#### Code/Number Related

| Term Name | English Abbreviation | Domain |
|---|---|---|
| 가족관계코드 | FAM_REL_CD | 코드C3 |
| 가상계좌번호 | VR_ACTNO | 계좌번호V20 |
| 사업자등록번호 | BRNO | 사업자등록번호C10 |
| 법인등록번호 | CRNO | 법인등록번호C13 |
| 전화번호 | TELNO | 전화번호V11 |
| 우편번호 | ZIP | 우편번호C5 |
| 삭제여부 | DEL_YN | 여부C1 |
| 사용여부 | USE_YN | 여부C1 |

#### Address Related

| Term Name | English Abbreviation | Domain |
|---|---|---|
| 도로명주소 | RDNMADR | 주소V200 |
| 지번주소 | LOTNO_ADDR | 주소V200 |
| 상세주소 | DTL_ADDR | 주소V320 |

---

## 6. English Abbreviation Naming Rules

### 6.1 Basic Principles

1. **Separate words with underscore (_) when combining**: `JOIN_YMD`, `REG_DT`
2. **Classifier word (format word) is placed last**: 가입 + 일자 -> `JOIN_YMD`
3. **English abbreviations use uppercase**: `CSTMR_NM`, `BRNO`
4. **Recommended maximum of 30 characters**

### 6.2 Key Suffix Patterns

| Category | Suffix | Meaning | Example |
|---|---|---|---|
| Date | _YMD | Date (year-month-day) | JOIN_YMD (가입일자) |
| Date | _DT | DateTime | REG_DT (등록일시) |
| Date | _YM | Year-month | ACNT_YM (계정연월) |
| Date | _YR | Year | BSNS_YR (사업연도) |
| Amount | _AMT | Amount | DEAL_AMT (거래금액) |
| Price | _PRC | Price | SUPLY_PRC (공급가격) |
| Name | _NM | Name | CSTMR_NM (고객명) |
| Code | _CD | Code | STTS_CD (상태코드) |
| Number | _NO | Number | SEQ_NO (순번) |
| Content | _CN | Content | PRCS_CN (처리내용) |
| Count | _CNT | Count | DEAL_CNT (거래건수) |
| Rate | _RT | Rate/ratio | TAX_RT (세율) |
| Flag | _YN | Yes/No flag | USE_YN (사용여부) |
| Sequence | _SN | Sequence number | SRT_SN (정렬순서) |
| Address | _ADDR | Address | DTL_ADDR (상세주소) |

---

## 7. JPA Entity Mapping Guide

### 7.1 Domain-to-Java Type Mapping

| Domain Group | Data Type | Java Type | JPA Annotation |
|---|---|---|---|
| 연월일시분초D | DATETIME | LocalDateTime | @Column(columnDefinition = "DATETIME") |
| 연월일C8 | CHAR(8) | String | @Column(length = 8, columnDefinition = "CHAR(8)") |
| 연월C6 | CHAR(6) | String | @Column(length = 6, columnDefinition = "CHAR(6)") |
| 연도C4 | CHAR(4) | String | @Column(length = 4, columnDefinition = "CHAR(4)") |
| 금액N15 | NUMERIC(15) | BigDecimal | @Column(precision = 15, scale = 0) |
| 가격N10 | NUMERIC(10) | BigDecimal | @Column(precision = 10, scale = 0) |
| 수N10 | NUMERIC(10) | Long | @Column |
| 수N5 | NUMERIC(5) | Integer | @Column |
| 율N5,2 | NUMERIC(5,2) | BigDecimal | @Column(precision = 5, scale = 2) |
| 명V100 | VARCHAR(100) | String | @Column(length = 100) |
| 명V200 | VARCHAR(200) | String | @Column(length = 200) |
| 내용V1000 | VARCHAR(1000) | String | @Column(length = 1000) |
| 내용V4000 | VARCHAR(4000) | String | @Column(length = 4000) |
| 코드C3 | CHAR(3) | String | @Column(length = 3, columnDefinition = "CHAR(3)") |
| 여부C1 | CHAR(1) | String | @Column(length = 1, columnDefinition = "CHAR(1)") |
| 주소V200 | VARCHAR(200) | String | @Column(length = 200) |
| 전화번호V11 | VARCHAR(11) | String | @Column(length = 11) |
| 사업자등록번호C10 | CHAR(10) | String | @Column(length = 10, columnDefinition = "CHAR(10)") |

### 7.2 Entity Example

```java
@Entity
@Table(name = "TB_CSTMR")  // Customer table
public class Customer {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "CSTMR_SN")  // Customer sequence number
    private Long customerSn;

    @Column(name = "CSTMR_NM", length = 100, nullable = false)  // Customer name
    private String customerNm;

    @Column(name = "BRNO", length = 10, columnDefinition = "CHAR(10)")  // Business registration number
    private String brno;

    @Column(name = "TELNO", length = 11)  // Phone number
    private String telno;

    @Column(name = "RDNMADR", length = 200)  // Road name address
    private String rdnmadr;

    @Column(name = "DTL_ADDR", length = 320)  // Detailed address
    private String dtlAddr;

    @Column(name = "ZIP", length = 5, columnDefinition = "CHAR(5)")  // Postal code
    private String zip;

    @Column(name = "JOIN_YMD", length = 8, columnDefinition = "CHAR(8)")  // Join date
    private String joinYmd;

    @Column(name = "REG_DT")  // Registration datetime
    private LocalDateTime regDt;

    @Column(name = "CHG_DT")  // Change datetime
    private LocalDateTime chgDt;

    @Column(name = "USE_YN", length = 1, columnDefinition = "CHAR(1) DEFAULT 'Y'")  // Use flag
    private String useYn;

    @Column(name = "DEL_YN", length = 1, columnDefinition = "CHAR(1) DEFAULT 'N'")  // Delete flag
    private String delYn;
}
```

---

## 8. Table Naming Rules

### 8.1 Table Name Pattern

```
TB_[business area abbreviation]_[entity name abbreviation]

Examples:
  TB_CSTMR       → Customer
  TB_CSTMR_ORDR  → Customer Order
  TB_PRDT        → Product
  TB_STLM        → Settlement
```

### 8.2 Common Prefixes

| Prefix | Purpose | Example |
|---|---|---|
| TB_ | General table | TB_CSTMR |
| TC_ | Code table | TC_STTS_CD |
| TH_ | History table | TH_CSTMR_CHG |
| TL_ | Log table | TL_LOGIN |
| TR_ | Relationship table | TR_CSTMR_PRDT |

---

## 9. References and Sources

### 9.1 Official Data Downloads

| Resource Name | Source | URL |
|---|---|---|
| Public Data Common Standard Terms (latest) | Public Data Portal | https://www.data.go.kr/data/15156379/fileData.do |
| Public Data Common Standard Words (latest) | Public Data Portal | https://www.data.go.kr/data/15156439/fileData.do |
| Public Institution DB Standardization Guidelines | National Law Information Center | https://law.go.kr/행정규칙/공공기관의데이터베이스표준화지침 |
| TTA ICT Terminology Dictionary | TTA | https://terms.tta.or.kr/main.do |

### 9.2 Related Legislation

- **Act on Promotion of the Provision and Use of Public Data** (Public Data Act)
- **Public Institution Database Standardization Guidelines** (Ministry of the Interior and Safety Notice No. 2023-18)
- **Public Database Standardization Management Manual** (2023.4)

### 9.3 Standard Status (as of November 2025)

| Category | Cumulative Count | Notes |
|---|---|---|
| Common standard terms | 13,159 | 8th revision (2025.11) |
| Common standard words | Approx. 2,400 | Including English abbreviations |
| Common standard domains | 112 | Data type/length definitions |

---

> **Document created**: 2026-02-14
> **Reference data**: Ministry of the Interior and Safety Public Data Common Standard 8th revision (as of 2025.11.01)
> **Note**: The latest data can be downloaded in CSV/JSON/XML format from the Public Data Portal (data.go.kr)
