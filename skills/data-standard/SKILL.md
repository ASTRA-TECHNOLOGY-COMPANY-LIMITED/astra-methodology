---
name: data-standard
description: >
  데이터베이스 테이블, 엔티티 클래스, SQL, 마이그레이션 파일을 작성할 때
  공공 데이터 표준 용어 사전을 자동 적용합니다. DB 컬럼명, 테이블명,
  변수명에 표준 영문 약어를 사용하고 도메인 규칙을 준수합니다.
  ORM 엔티티, DTO, VO, SQL DDL, 스키마 정의 작성 시 사용합니다.
---

# 데이터 표준 용어 적용 스킬

DB 관련 코드를 작성할 때 반드시 아래 표준을 따르라.
상세 가이드는 이 디렉토리의 data-standard-terminology-guide.md를 참조하라.

## 적용 대상 파일

- JPA/Hibernate 엔티티 클래스 (.java)
- TypeORM/Prisma 엔티티/스키마 (.ts)
- SQLAlchemy/Django 모델 (.py)
- SQL 파일 (.sql)
- 마이그레이션 파일
- DTO/VO 클래스

## 핵심 규칙

### 1. 컬럼명은 표준 용어 영문 약어를 사용한다

표준 용어 사전(`data/standard_terms.json`)에서 한글 용어명을 검색하여 영문 약어를 사용한다.

주요 예시:
| 한글 용어 | 영문 약어(물리 컬럼명) | 도메인 |
|---|---|---|
| 고객명 | CSTMR_NM | 명V100 |
| 가입일자 | JOIN_YMD | 연월일C8 |
| 등록일시 | REG_DT | 연월일시분초D |
| 사업자등록번호 | BRNO | 사업자등록번호C10 |
| 결제금액 | STLM_AMT | 금액N15 |
| 사용여부 | USE_YN | 여부C1 |
| 상태코드 | STTS_CD | 코드C3 |
| 전화번호 | TELNO | 전화번호V11 |
| 우편번호 | ZIP | 우편번호C5 |
| 도로명주소 | RDNMADR | 주소V200 |
| 상세주소 | DTL_ADDR | 주소V320 |
| 처리내용 | PRCS_CN | 내용V1000 |
| 변경사유 | CHG_RSN | 내용V500 |

### 2. 접미사 패턴을 준수한다

| 접미사 | 의미 | 예시 |
|---|---|---|
| _YMD | 연월일 | REG_YMD (등록일자) |
| _DT | 일시 | REG_DT (등록일시) |
| _YM | 연월 | ACNT_YM (계정연월) |
| _YR | 연도 | BSNS_YR (사업연도) |
| _AMT | 금액 | STLM_AMT (결제금액) |
| _PRC | 가격 | SUPLY_PRC (공급가격) |
| _NM | 명 | CSTMR_NM (고객명) |
| _CD | 코드 | STTS_CD (상태코드) |
| _NO | 번호 | SEQ_NO (순번) |
| _CN | 내용 | PRCS_CN (처리내용) |
| _CNT | 건수 | DEAL_CNT (거래건수) |
| _RT | 율 | TAX_RT (세율) |
| _YN | 여부 | USE_YN (사용여부) |
| _SN | 순번 | SRT_SN (정렬순서) |
| _ADDR | 주소 | DTL_ADDR (상세주소) |

### 3. 테이블명 규칙

| 접두어 | 용도 | 예시 |
|---|---|---|
| TB_ | 일반 테이블 | TB_CSTMR (고객) |
| TC_ | 코드 테이블 | TC_STTS_CD (상태코드) |
| TH_ | 이력 테이블 | TH_CSTMR_CHG (고객변경이력) |
| TL_ | 로그 테이블 | TL_LOGIN (로그인로그) |
| TR_ | 관계 테이블 | TR_CSTMR_PRDT (고객상품관계) |

### 4. 도메인 규칙에 따른 데이터 타입 매핑

#### 날짜/시간
| 도메인 | DB 타입 | Java | TypeScript | Python |
|---|---|---|---|---|
| 연월일시분초D | DATETIME | LocalDateTime | Date | datetime |
| 연월일C8 | CHAR(8) | String | string | str |
| 연월C6 | CHAR(6) | String | string | str |
| 연도C4 | CHAR(4) | String | string | str |

#### 금액/숫자
| 도메인 | DB 타입 | Java | TypeScript | Python |
|---|---|---|---|---|
| 금액N15 | NUMERIC(15) | BigDecimal | number | Decimal |
| 가격N10 | NUMERIC(10) | BigDecimal | number | Decimal |
| 수N10 | NUMERIC(10) | Long | number | int |
| 수N5 | NUMERIC(5) | Integer | number | int |
| 율N5,2 | NUMERIC(5,2) | BigDecimal | number | Decimal |

#### 문자
| 도메인 | DB 타입 | Java | TypeScript | Python |
|---|---|---|---|---|
| 명V100 | VARCHAR(100) | String | string | str |
| 명V200 | VARCHAR(200) | String | string | str |
| 내용V1000 | VARCHAR(1000) | String | string | str |
| 내용V4000 | VARCHAR(4000) | String | string | str |
| 주소V200 | VARCHAR(200) | String | string | str |

#### 코드/여부
| 도메인 | DB 타입 | Java | TypeScript | Python |
|---|---|---|---|---|
| 코드C1~C7 | CHAR(n) | String | string | str |
| 코드V20 | VARCHAR(20) | String | string | str |
| 여부C1 | CHAR(1) | String | "Y" \| "N" | str |

### 5. 금칙어 사용 금지

표준 단어 사전(`data/standard_words.json`)의 `금칙어목록` 필드에 있는 단어 사용을 금지한다.
발견 시 `이음동의어목록`의 표준어로 대체한다.

### 6. 용어 검색 방법

DB 관련 네이밍이 필요할 때:

1. `data/standard_terms.json`에서 한글 `공통표준용어명`으로 검색
2. 해당 용어의 `공통표준용어영문약어명` 값을 컬럼명으로 사용
3. `공통표준도메인명`으로 데이터 타입과 길이를 결정
4. 표준 용어에 없는 경우, `data/standard_words.json`에서 개별 단어의 `공통표준단어영문약어명`을 조합

### 7. JPA 엔티티 작성 예시

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
