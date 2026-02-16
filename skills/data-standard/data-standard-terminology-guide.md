# 행정안전부 공공데이터 공통표준 용어사전 가이드

## 1. 개요

### 1.1 선정 배경

국내 데이터베이스 표준 용어사전을 조사한 결과, **행정안전부 공공데이터 공통표준**이 가장 권위 있고 실용적인 표준으로 평가됩니다.

| 비교 항목 | 행정안전부 공통표준 | TTA 정보통신용어사전 | 국립국어원 표준국어대사전 |
|---|---|---|---|
| **용도** | DB 설계 및 데이터 표준화 | ICT 용어 해설 | 국어 표준 정의 |
| **용어 수** | 13,159개 (2025.11) | 약 15,000건 표준 | 약 50만 표제어 |
| **DB 설계 적용** | 직접 적용 가능 | 참고 수준 | 해당 없음 |
| **영문약어 제공** | 제공 (물리 컬럼명) | 일부 제공 | 미제공 |
| **도메인/데이터타입** | 112개 도메인 정의 | 미제공 | 미제공 |
| **법적 근거** | 공공기관 DB 표준화 지침 | 자율 적용 | 자율 적용 |
| **갱신 주기** | 연 1~2회 제개정 | 수시 | 수시 |
| **배포 형식** | CSV, JSON, XML, API | 웹 검색 | 웹 검색 |

### 1.2 선정 이유

1. **법적 구속력**: 「공공기관의 데이터베이스 표준화 지침」(행정안전부고시 제2023-18호)에 근거
2. **실무 적용성**: DB 컬럼명(영문약어), 데이터타입, 길이까지 정의하여 즉시 적용 가능
3. **체계적 구성**: 표준단어 + 표준도메인 = 표준용어의 조합 체계
4. **지속적 확대**: 2020년 535개에서 2025년 13,159개로 지속 확대
5. **오픈 포맷**: CSV, JSON, XML, API로 제공하여 자동화 가능

---

## 2. 표준 체계 구조

공통표준은 **3개 계층**으로 구성됩니다.

```
┌─────────────────────────────────────────────────┐
│                 공통표준용어 (Term)                │
│          예: 가입일자, 사업자등록번호               │
│                                                   │
│  ┌──────────────────┐  ┌──────────────────────┐  │
│  │  공통표준단어     │  │  공통표준도메인        │  │
│  │  (Word)          │  │  (Domain)             │  │
│  │  예: 가입, 사업자  │  │  예: 연월일C8, 번호V20 │  │
│  └──────────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### 2.1 조합 규칙

```
표준용어 = 표준단어(1개 이상) + 표준도메인(분류어)

예시:
  가입일자   = [가입] + [일자]  → 도메인: 연월일C8
  사업자등록번호 = [사업자] + [등록] + [번호] → 도메인: 사업자등록번호C10
  강사명     = [강사] + [명]   → 도메인: 명V100
```

---

## 3. 표준단어 (Standard Word)

### 3.1 관리 항목

| 항목 | 설명 | 예시 |
|---|---|---|
| 공통표준단어명 | 한글 단어명 | 가입, 사업자, 등록 |
| 영문약어명 | 물리 컬럼명에 사용 | JOIN, BZMN, REG |
| 영문명 | 영문 풀네임 | Join, Businessman, Registration |
| 설명 | 단어 정의 | 단체나 조직체에 들어감 |
| 형식어 여부 | 도메인 분류어 여부 | Y/N |
| 도메인 분류명 | 형식어일 때 분류명 | 일자, 코드, 명 등 |
| 금지어 목록 | 사용 금지 유사어 | - |

### 3.2 표준단어 예시 (주요 단어)

| 한글명 | 영문약어 | 영문명 | 형식어 | 도메인분류 |
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

## 4. 표준도메인 (Standard Domain)

### 4.1 도메인 개념

도메인은 데이터의 **유형과 길이를 그룹화**한 것입니다.

```
도메인 = 분류어 + 데이터타입 + 데이터길이

예: 금액N15 = 금액(분류어) + NUMERIC(타입) + 15(길이)
    명V100 = 명(분류어) + VARCHAR(타입) + 100(길이)
```

### 4.2 도메인 그룹별 분류

#### 날짜/시간 도메인

| 도메인명 | 데이터타입 | 길이 | 저장형식 | 표현형식 |
|---|---|---|---|---|
| 연월일시분초D | DATETIME | - | YYYYMMDDHH24MISS | YYYY-MM-DD HH:MI:SS |
| 연월일C8 | CHAR | 8 | YYYYMMDD | YYYY-MM-DD |
| 연월C6 | CHAR | 6 | YYYYMM | YYYY-MM |
| 연도C4 | CHAR | 4 | YYYY | YYYY |
| 월C2 | CHAR | 2 | MM | MM |
| 시분초C6 | CHAR | 6 | HH24MISS | HH:MI:SS |

#### 금액/숫자 도메인

| 도메인명 | 데이터타입 | 길이 | 소수점 | 저장형식 |
|---|---|---|---|---|
| 금액N15 | NUMERIC | 15 | 0 | 999999999999999 |
| 가격N10 | NUMERIC | 10 | 0 | 9999999999 |
| 수N10 | NUMERIC | 10 | 0 | 9999999999 |
| 수N5 | NUMERIC | 5 | 0 | 99999 |
| 면적N19,9 | NUMERIC | 19 | 9 | 9999999999.999999999 |
| 율N5,2 | NUMERIC | 5 | 2 | 999.99 |
| 율N7,4 | NUMERIC | 7 | 4 | 999.9999 |

#### 문자 도메인

| 도메인명 | 데이터타입 | 길이 | 용도 |
|---|---|---|---|
| 명V100 | VARCHAR | 100 | 일반 이름/명칭 |
| 명V200 | VARCHAR | 200 | 긴 명칭 |
| 명V500 | VARCHAR | 500 | 매우 긴 명칭 |
| 내용V500 | VARCHAR | 500 | 일반 내용/설명 |
| 내용V1000 | VARCHAR | 1000 | 긴 내용 |
| 내용V2000 | VARCHAR | 2000 | 매우 긴 내용 |
| 내용V4000 | VARCHAR | 4000 | 대용량 내용 |
| 주소V200 | VARCHAR | 200 | 일반 주소 |
| 주소V320 | VARCHAR | 320 | 상세 주소 |

#### 코드 도메인

| 도메인명 | 데이터타입 | 길이 | 용도 |
|---|---|---|---|
| 코드C1 | CHAR | 1 | 1자리 분류코드 |
| 코드C2 | CHAR | 2 | 2자리 분류코드 |
| 코드C3 | CHAR | 3 | 3자리 분류코드 |
| 코드C5 | CHAR | 5 | 5자리 분류코드 |
| 코드C7 | CHAR | 7 | 7자리 분류코드 |
| 코드V20 | VARCHAR | 20 | 가변길이 코드 |
| 여부C1 | CHAR | 1 | Y/N 여부 |

#### 번호 도메인

| 도메인명 | 데이터타입 | 길이 | 용도 |
|---|---|---|---|
| 번호V20 | VARCHAR | 20 | 일반 번호 |
| 계좌번호V20 | VARCHAR | 20 | 계좌번호 |
| 주민등록번호C13 | CHAR | 13 | 주민등록번호 |
| 사업자등록번호C10 | CHAR | 10 | 사업자등록번호 |
| 법인등록번호C13 | CHAR | 13 | 법인등록번호 |
| 전화번호V11 | VARCHAR | 11 | 전화번호 |
| 우편번호C5 | CHAR | 5 | 우편번호 |
| 여권번호C9 | CHAR | 9 | 여권번호 |

---

## 5. 표준용어 (Standard Term) 예시

### 5.1 관리 항목

| 항목 | 설명 |
|---|---|
| 공통표준용어명 | 한글 용어 (논리 컬럼명) |
| 영문약어명 | 물리 컬럼명 |
| 공통표준도메인명 | 적용 도메인 |
| 허용범위 | 최대/최소값 또는 유효값 |
| 저장형식 | DB 저장 방식 |
| 표현형식 | 화면 표현 방식 |

### 5.2 주요 표준용어 목록

#### 날짜/시간 관련

| 용어명 | 영문약어명 | 도메인 | 저장형식 | 표현형식 |
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

#### 금액/수량 관련

| 용어명 | 영문약어명 | 도메인 | 표현형식 |
|---|---|---|---|
| 가산금액 | ADTN_AMT | 금액N15 | 999,999,999,999,999 |
| 거래금액 | DEAL_AMT | 금액N15 | 999,999,999,999,999 |
| 결제금액 | STLM_AMT | 금액N15 | 999,999,999,999,999 |
| 공급가격 | SUPLY_PRC | 가격N10 | 9,999,999,999 |
| 납부금액 | PAY_AMT | 금액N15 | 999,999,999,999,999 |
| 개별공시지가 | INDIV_OALP | 가격N10 | 9,999,999,999 |
| 합계금액 | SUM_AMT | 금액N15 | 999,999,999,999,999 |

#### 명칭/내용 관련

| 용어명 | 영문약어명 | 도메인 |
|---|---|---|
| 강사명 | INSTR_NM | 명V100 |
| 고객명 | CSTMR_NM | 명V100 |
| 관리기관명 | MGMT_INST_NM | 명V200 |
| 담당자명 | CHRG_NM | 명V100 |
| 사업자명 | BZMN_NM | 명V100 |
| 시설명 | FCLT_NM | 명V200 |
| 처리내용 | PRCS_CN | 내용V1000 |
| 변경사유 | CHG_RSN | 내용V500 |

#### 코드/번호 관련

| 용어명 | 영문약어명 | 도메인 |
|---|---|---|
| 가족관계코드 | FAM_REL_CD | 코드C3 |
| 가상계좌번호 | VR_ACTNO | 계좌번호V20 |
| 사업자등록번호 | BRNO | 사업자등록번호C10 |
| 법인등록번호 | CRNO | 법인등록번호C13 |
| 전화번호 | TELNO | 전화번호V11 |
| 우편번호 | ZIP | 우편번호C5 |
| 삭제여부 | DEL_YN | 여부C1 |
| 사용여부 | USE_YN | 여부C1 |

#### 주소 관련

| 용어명 | 영문약어명 | 도메인 |
|---|---|---|
| 도로명주소 | RDNMADR | 주소V200 |
| 지번주소 | LOTNO_ADDR | 주소V200 |
| 상세주소 | DTL_ADDR | 주소V320 |

---

## 6. 영문약어 명명 규칙

### 6.1 기본 원칙

1. **단어 조합 시 언더스코어(_)로 구분**: `JOIN_YMD`, `REG_DT`
2. **형식어(분류어)는 마지막에 배치**: `가입` + `일자` → `JOIN_YMD`
3. **영문약어는 대문자 사용**: `CSTMR_NM`, `BRNO`
4. **최대 30자 이내 권장**

### 6.2 주요 접미어 패턴

| 분류 | 접미어 | 의미 | 예시 |
|---|---|---|---|
| 날짜 | _YMD | 연월일 | JOIN_YMD (가입일자) |
| 날짜 | _DT | 일시 | REG_DT (등록일시) |
| 날짜 | _YM | 연월 | ACNT_YM (계정연월) |
| 날짜 | _YR | 연도 | BSNS_YR (사업연도) |
| 금액 | _AMT | 금액 | DEAL_AMT (거래금액) |
| 가격 | _PRC | 가격 | SUPLY_PRC (공급가격) |
| 명칭 | _NM | 명 | CSTMR_NM (고객명) |
| 코드 | _CD | 코드 | STTS_CD (상태코드) |
| 번호 | _NO | 번호 | SEQ_NO (순번) |
| 내용 | _CN | 내용 | PRCS_CN (처리내용) |
| 수량 | _CNT | 건수 | DEAL_CNT (거래건수) |
| 율 | _RT | 율/비율 | TAX_RT (세율) |
| 여부 | _YN | 여부 | USE_YN (사용여부) |
| 순서 | _SN | 순번 | SRT_SN (정렬순서) |
| 주소 | _ADDR | 주소 | DTL_ADDR (상세주소) |

---

## 7. JPA 엔티티 매핑 가이드

### 7.1 도메인-Java 타입 매핑

| 도메인 그룹 | 데이터타입 | Java 타입 | JPA 어노테이션 |
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

### 7.2 엔티티 작성 예시

```java
@Entity
@Table(name = "TB_CSTMR")  // 고객 테이블
public class Customer {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "CSTMR_SN")  // 고객순번
    private Long customerSn;

    @Column(name = "CSTMR_NM", length = 100, nullable = false)  // 고객명
    private String customerNm;

    @Column(name = "BRNO", length = 10, columnDefinition = "CHAR(10)")  // 사업자등록번호
    private String brno;

    @Column(name = "TELNO", length = 11)  // 전화번호
    private String telno;

    @Column(name = "RDNMADR", length = 200)  // 도로명주소
    private String rdnmadr;

    @Column(name = "DTL_ADDR", length = 320)  // 상세주소
    private String dtlAddr;

    @Column(name = "ZIP", length = 5, columnDefinition = "CHAR(5)")  // 우편번호
    private String zip;

    @Column(name = "JOIN_YMD", length = 8, columnDefinition = "CHAR(8)")  // 가입일자
    private String joinYmd;

    @Column(name = "REG_DT")  // 등록일시
    private LocalDateTime regDt;

    @Column(name = "CHG_DT")  // 변경일시
    private LocalDateTime chgDt;

    @Column(name = "USE_YN", length = 1, columnDefinition = "CHAR(1) DEFAULT 'Y'")  // 사용여부
    private String useYn;

    @Column(name = "DEL_YN", length = 1, columnDefinition = "CHAR(1) DEFAULT 'N'")  // 삭제여부
    private String delYn;
}
```

---

## 8. 테이블 명명 규칙

### 8.1 테이블명 패턴

```
TB_[업무영역약어]_[엔티티명약어]

예시:
  TB_CSTMR       → 고객
  TB_CSTMR_ORDR  → 고객주문
  TB_PRDT        → 상품(Product)
  TB_STLM        → 결제(Settlement)
```

### 8.2 공통 접두어

| 접두어 | 용도 | 예시 |
|---|---|---|
| TB_ | 일반 테이블 | TB_CSTMR |
| TC_ | 코드 테이블 | TC_STTS_CD |
| TH_ | 이력 테이블 | TH_CSTMR_CHG |
| TL_ | 로그 테이블 | TL_LOGIN |
| TR_ | 관계 테이블 | TR_CSTMR_PRDT |

---

## 9. 참고 자료 및 출처

### 9.1 공식 자료 다운로드

| 자료명 | 출처 | URL |
|---|---|---|
| 공공데이터 공통표준용어 (최신) | 공공데이터포털 | https://www.data.go.kr/data/15156379/fileData.do |
| 공공데이터 공통표준단어 (최신) | 공공데이터포털 | https://www.data.go.kr/data/15156439/fileData.do |
| 공공기관의 DB 표준화 지침 | 국가법령정보센터 | https://law.go.kr/행정규칙/공공기관의데이터베이스표준화지침 |
| TTA 정보통신용어사전 | TTA | https://terms.tta.or.kr/main.do |

### 9.2 관련 법령

- **공공데이터의 제공 및 이용 활성화에 관한 법률** (공공데이터법)
- **공공기관의 데이터베이스 표준화 지침** (행정안전부고시 제2023-18호)
- **공공데이터베이스 표준화 관리 매뉴얼** (2023.4)

### 9.3 표준 현황 (2025년 11월 기준)

| 구분 | 누적 수량 | 비고 |
|---|---|---|
| 공통표준용어 | 13,159개 | 8차 제개정 (2025.11) |
| 공통표준단어 | 약 2,400개 | 영문약어 포함 |
| 공통표준도메인 | 112개 | 데이터타입/길이 정의 |

---

> **문서 작성일**: 2026-02-14
> **기준 데이터**: 행정안전부 공공데이터 공통표준 8차 제개정 (2025.11.01 기준)
> **참고**: 최신 데이터는 공공데이터포털(data.go.kr)에서 CSV/JSON/XML 형식으로 다운로드 가능
