# DB 네이밍 규칙

> 공공 데이터 표준 용어 사전을 기반으로 테이블명, 컬럼명의 네이밍 규칙을 정의합니다.
> `/lookup-term`으로 표준 용어를 조회하세요.

## 1. 테이블 네이밍

### 1.1 접두사 규칙

| 접두사 | 유형 | 예시 |
|--------|------|------|
| TB_ | 일반 테이블 | TB_COMM_USER (사용자) |
| TC_ | 코드 테이블 | TC_COMM_CD (공통코드) |
| TH_ | 이력 테이블 | TH_COMM_USER_AGRE (동의이력) |
| TL_ | 로그 테이블 | TL_SYS_API_LOG (API로그) |
| TR_ | 관계 테이블 | TR_USER_ROLE (사용자-역할 매핑) |

### 1.2 테이블명 패턴

`{접두사}_{모듈약어}_{엔티티명}`

| 모듈 | 약어 | 예시 테이블 |
|------|------|-----------|
| 공통 | COMM | TB_COMM_USER, TC_COMM_CD |
| 결제 | PAY | TB_PAY_PLAN, TB_PAY_SBSC |
| 주문 | ORDR | TB_ORDR, TB_ORDR_PRDT |
| 알림 | NTFC | TH_NTFC_HIST |
| 시스템 | SYS | TL_SYS_API_LOG |

## 2. 컬럼 네이밍

### 2.1 기본 패턴

`{한글 의미의 영문 약어}`

- 표준 용어 사전에 등록된 약어를 우선 사용합니다.
- `/lookup-term [한글 용어]`로 약어를 조회합니다.

### 2.2 접미사 규칙

| 접미사 | 용도 | 예시 |
|--------|------|------|
| _ID | 식별자 | USER_ID, ORDR_ID |
| _SN | 일련번호 | STLM_SN |
| _NM | 이름 | USER_NM, PRDT_NM |
| _CD | 코드 | ORDR_STTS_CD, PAY_MTHD_CD |
| _AMT | 금액 | STLM_AMT, ORDR_AMT |
| _QTY | 수량 | ORDR_QTY |
| _DT | 일시 | ORDR_DT, CRT_DT |
| _YN | 여부 | USE_YN, DEL_YN |
| _CN | 내용 | NTFC_CN |
| _ADDR | 주소 | DLVR_ADDR |
| _TELNO | 전화번호 | MBTLNUM |

### 2.3 공통 감사 컬럼

모든 테이블에 포함하는 필수 컬럼:

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| CRTR_ID | VARCHAR(50) | 생성자 ID |
| CRT_DT | TIMESTAMP | 생성일시 |
| MDFR_ID | VARCHAR(50) | 수정자 ID |
| MDFCN_DT | TIMESTAMP | 수정일시 |

## 3. PK/FK 네이밍

### 3.1 PK (Primary Key)

- 제약조건명: `PK_{모듈약어}_{엔티티명}`
- 예시: `PK_COMM_USER`, `PK_PAY_PLAN`

### 3.2 FK (Foreign Key)

- 제약조건명: `FK_{자식테이블약어}_{부모테이블약어}`
- 컬럼명: 참조 테이블의 PK 컬럼명 그대로 사용
- 예시: TB_ORDR의 USER_ID → TB_COMM_USER의 USER_ID 참조

## 4. 인덱스 네이밍

- 일반 인덱스: `IDX_{테이블약어}_{컬럼명}`
- 유니크 인덱스: `UDX_{테이블약어}_{컬럼명}`
- 예시: `IDX_COMM_USER_EMAIL`, `UDX_COMM_USER_LOGIN_ID`

## 5. 표준 용어 매핑 예시

| 한글 용어 | 영문 약어 | 도메인 | 데이터 타입 |
|----------|----------|--------|-----------|
| 사용자 | USER | | |
| 결제금액 | STLM_AMT | 금액 | NUMERIC |
| 주문번호 | ORDR_NO | 번호 | VARCHAR |
| 주문일시 | ORDR_DT | 일시 | TIMESTAMP |
| 상품명 | PRDT_NM | 명 | VARCHAR |

> 전체 표준 용어 목록은 `/lookup-term` 커맨드로 조회합니다.

---

> **갱신 규칙**:
> 1. 새로운 도메인 용어가 필요할 때 이 문서에 추가합니다.
> 2. 표준 용어 사전에 없는 용어는 VA가 약어를 결정하고 등록합니다.
