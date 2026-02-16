---
description: 한글 테이블/컬럼 정의로부터 표준을 준수하는 엔티티 코드를 생성합니다
---

# 표준 엔티티 생성

$ARGUMENTS 의 한글 테이블/컬럼 정의를 바탕으로 표준을 준수하는 엔티티 코드를 생성하라.

## 입력 형식 예시

다양한 형태의 입력을 처리한다:
- "고객 테이블: 고객명, 고객번호, 생년월일, 이메일주소, 가입일자, 사용여부"
- "주문(고객순번, 주문일자, 결제금액, 상태코드, 배송주소)"
- 표 형태의 컬럼 목록

## 생성 절차

### 1단계: 용어 매핑
각 한글 컬럼명을 `data/standard_terms.json`에서 검색한다.
표준 용어가 있으면 영문 약어, 도메인, 데이터 타입을 가져온다.
표준 용어가 없으면 `data/standard_words.json`에서 단어를 조합한다.

### 2단계: 매핑 테이블 출력
| 한글 컬럼명 | 영문 약어 | 도메인 | 데이터 타입 | 출처 |
|---|---|---|---|---|
| (용어) | (약어) | (도메인) | (타입) | 표준용어 / 단어조합 |

### 3단계: 코드 생성
프로젝트 언어에 맞는 엔티티 클래스를 생성한다.
언어가 불분명하면 Java JPA를 기본으로 생성하고, TypeScript와 Python도 함께 제공한다.

#### Java (JPA)
- `@Entity`, `@Table(name = "TB_...")` 어노테이션
- `@Column(name = "...", length = ...)` 으로 물리 컬럼명 매핑
- CHAR 타입은 `columnDefinition` 명시
- 도메인에 따른 Java 타입 매핑 (BigDecimal, LocalDateTime, String 등)
- Google Java Style Guide 준수 (2스페이스 인덴트, K&R 중괄호 등)

#### TypeScript (TypeORM)
- `@Entity()`, `@Column()` 데코레이터
- 표준 접미사에 따른 타입 매핑
- Google TypeScript Style Guide 준수 (named export, const, === 등)

#### Python (SQLAlchemy)
- `Column()`, `Table()` 정의
- PEP 8 준수 (snake_case, 4스페이스 등)

### 4단계: DDL 생성
표준 테이블명 규칙(TB_ 접두사)을 적용한 SQL DDL도 함께 생성한다.

```sql
CREATE TABLE TB_테이블약어 (
    컬럼약어 데이터타입(길이) [NOT NULL] [DEFAULT ...] COMMENT '한글 컬럼명',
    ...
);
```

## 추가 규칙

- 모든 테이블에 기본 감사(audit) 컬럼을 포함: REG_DT(등록일시), CHG_DT(변경일시)
- 사용여부(USE_YN) 컬럼이 명시되면 DEFAULT 'Y' 설정
- 삭제여부(DEL_YN) 컬럼이 명시되면 DEFAULT 'N' 설정
- PK는 테이블명_SN (순번) 패턴으로 자동 생성 (명시되지 않은 경우)
