---
description: DB 관련 코드의 네이밍이 표준 용어 사전을 준수하는지 검사합니다
---

# 표준 네이밍 검사

$ARGUMENTS 에 대해 DB 관련 네이밍의 표준 준수 여부를 검사하라.

## 검사 대상

- JPA/Hibernate 엔티티 클래스 (@Column, @Table 어노테이션)
- TypeORM/Prisma 엔티티/스키마 정의
- SQLAlchemy/Django 모델 정의
- SQL DDL (CREATE TABLE, ALTER TABLE)
- DTO/VO 클래스의 필드명

## 검사 항목

### 1. 표준 용어 일치
- `data/standard_terms.json`에서 컬럼명이 `공통표준용어영문약어명`과 일치하는지 확인
- 불일치 시 가장 유사한 표준 용어 제안

### 2. 접미사 패턴 일관성
- 날짜 관련 컬럼에 `_YMD` 또는 `_DT` 접미사 사용 여부
- 금액 관련 컬럼에 `_AMT` 또는 `_PRC` 접미사 사용 여부
- 명칭 관련 컬럼에 `_NM` 접미사 사용 여부
- 코드 관련 컬럼에 `_CD` 접미사 사용 여부
- 여부 관련 컬럼에 `_YN` 접미사 사용 여부
- 의미와 접미사가 일치하는지 확인

### 3. 도메인 규칙 준수
- `data/standard_domains.json`을 참조하여 데이터 타입과 길이가 도메인 정의와 일치하는지 확인
- VARCHAR(50)인데 도메인이 명V100이면 길이 불일치로 보고

### 4. 금칙어 검출
- `data/standard_words.json`의 `금칙어목록` 필드 기반으로 검출
- 금칙어 발견 시 `이음동의어목록`의 표준어 제안

### 5. 테이블명 규칙
- TB_/TC_/TH_/TL_/TR_ 접두사 확인
- 접두사 누락 또는 오사용 보고

## 출력 형식

검사 결과를 아래 형식으로 보고하라:

| 유형 | 위치 | 현재 네이밍 | 표준 네이밍 | 비고 |
|---|---|---|---|---|
| 비표준컬럼명 | User.java:25 | `cust_name` | `CSTMR_NM` | 표준 용어: 고객명 |
| 금칙어사용 | Order.java:30 | `reg_date` | `REG_YMD` | 금칙어 '날짜' → 표준어 '일자' |
| 도메인불일치 | User.java:28 | `VARCHAR(50)` | `VARCHAR(100)` | 명V100 도메인 기준 |
| 접미사오류 | User.java:32 | `CSTMR_NAME` | `CSTMR_NM` | 명칭 접미사는 _NM |
| 테이블명오류 | User.java:10 | `CUSTOMER` | `TB_CSTMR` | TB_ 접두사 + 표준 약어 |

마지막에 검사 요약을 보고하라:
- 총 검사 항목 수
- 표준 준수 항목 수
- 위반 항목 수 (유형별)
- 표준 준수율 (%)
