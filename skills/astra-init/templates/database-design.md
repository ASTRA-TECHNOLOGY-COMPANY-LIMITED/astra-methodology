# 데이터베이스 설계 문서

> **Single Source of Truth**: 모든 테이블 설계를 이 문서에서 통합 관리합니다.
> 기능별 설계 문서에 테이블 DDL을 분산시키지 않습니다.

## 1. 전체 ERD

```
[모듈별 테이블 관계도를 여기에 작성합니다]

예시:
TB_COMM_USER ──┬── TH_COMM_USER_AGRE ── TB_COMM_TRMS
               │
               ├── TB_PAY_SBSC ── TB_PAY_PLAN
               │
               └── TB_ORDR ── TB_ORDR_PRDT
```

## 2. 공통 규칙

### 2.1 테이블 접두사

| 접두사 | 유형 | 예시 |
|--------|------|------|
| TB_ | 일반 테이블 | TB_COMM_USER (사용자) |
| TC_ | 코드 테이블 | TC_COMM_CD (공통코드) |
| TH_ | 이력 테이블 | TH_COMM_USER_AGRE (동의이력) |
| TL_ | 로그 테이블 | TL_SYS_API_LOG (API로그) |
| TR_ | 관계 테이블 | TR_USER_ROLE (사용자-역할 매핑) |

### 2.2 공통 감사 컬럼

모든 테이블에 다음 컬럼을 포함합니다:

| 컬럼명 | 타입 | 설명 | 비고 |
|--------|------|------|------|
| CRTR_ID | VARCHAR(50) | 생성자 ID | NOT NULL |
| CRT_DT | TIMESTAMP | 생성일시 | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| MDFR_ID | VARCHAR(50) | 수정자 ID | NULL 허용 |
| MDFCN_DT | TIMESTAMP | 수정일시 | NULL 허용 |

### 2.3 네이밍 규칙

- **테이블명**: `{접두사}_{모듈약어}_{엔티티명}` (예: TB_COMM_USER)
- **컬럼명**: `{한글의미의 영문약어}` (예: USER_NM, TELNO, STLM_AMT)
- **PK**: `{엔티티}_ID` 또는 `{엔티티}_SN` (일련번호)
- **FK**: 참조 테이블의 PK 컬럼명 그대로 사용
- **상태코드**: `{대상}_STTS_CD` (예: ORDR_STTS_CD)
- **코드값**: `{의미}_CD` (예: PAY_MTHD_CD)
- **금액**: `{의미}_AMT` (예: STLM_AMT)
- **수량**: `{의미}_QTY` (예: ORDR_QTY)
- **일시**: `{의미}_DT` (예: ORDR_DT)
- **여부**: `{의미}_YN` (예: USE_YN)

> 공공 데이터 표준 용어 사전을 준수합니다. `/lookup-term`으로 용어를 조회하세요.

## 3. 모듈별 테이블

### 3.1 공통 모듈 (COMM)

#### TB_COMM_USER (사용자)

| 컬럼명 | 타입 | PK | FK | NULL | 설명 |
|--------|------|----|----|------|------|
| USER_ID | VARCHAR(50) | PK | | NOT NULL | 사용자 ID |
| ... | | | | | |

```sql
-- DDL
CREATE TABLE TB_COMM_USER (
    USER_ID VARCHAR(50) NOT NULL,
    -- ...
    CRTR_ID VARCHAR(50) NOT NULL,
    CRT_DT TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    MDFR_ID VARCHAR(50),
    MDFCN_DT TIMESTAMP,
    CONSTRAINT PK_COMM_USER PRIMARY KEY (USER_ID)
);
```

### 3.2 {모듈명} ({약어})

> 기능 개발 시 `/feature-dev`로 이 섹션에 테이블을 추가합니다.

## 4. Enum/코드 값 정의

| 코드 타입 | 코드 값 | 설명 |
|----------|---------|------|
| | | |

## 5. 테이블 간 FK 관계 요약

| FK 이름 | 자식 테이블 | 자식 컬럼 | 부모 테이블 | 부모 컬럼 | ON DELETE |
|---------|-----------|----------|-----------|----------|-----------|
| | | | | | |

---

> **갱신 규칙**:
> 1. 새 기능 개발 시 이 문서에 테이블을 먼저 추가합니다.
> 2. 표준 용어 사전 준수 여부를 `/lookup-term`으로 확인합니다.
> 3. VA가 검토 후 코드 반영을 진행합니다.
