# Sprint 1 프롬프트 맵

## 스프린트 목표
[이번 스프린트에서 달성할 비즈니스 가치를 서술]

## 기능 1: {기능명}

### 1.1 설계 프롬프트
```
/feature-dev "{기능 설명}의 설계 문서를
docs/blueprints/{feature-name}.md로 작성해줘.
{상세 요구사항}
DB 스키마는 docs/database/database-design.md를 참조할 것.
아직 코드는 수정하지 마."
```

### 1.2 DB 설계 반영 프롬프트
```
/feature-dev "docs/database/database-design.md에 {모듈명} 테이블을
추가/갱신해줘:
- {테이블 목록}
- ERD와 FK 관계 요약도 갱신할 것. 표준 용어 사전 준수.
아직 코드는 수정하지 마."
```

### 1.3 테스트 케이스 프롬프트
```
/feature-dev "docs/blueprints/{feature-name}.md의 기능 요구사항을 기반으로
테스트 케이스를 docs/tests/test-cases/{feature-name}-test-cases.md로 작성해줘.
Given-When-Then 형식, 단위/통합/엣지 케이스를 포함.
아직 코드는 수정하지 마."
```

### 1.4 구현 프롬프트
```
/feature-dev "docs/blueprints/{feature-name}.md와
docs/database/database-design.md의 내용을 엄격히 준수해서
개발을 진행해줘. 테스트는 docs/tests/test-cases/{feature-name}-test-cases.md를
참조하여 작성하고, 구현이 끝나면 모든 테스트를 실행하고
결과를 docs/tests/test-reports/에 보고해."
```

## 기능 2: {기능명}

### 2.1 설계 프롬프트
```
```

### 2.2 DB 설계 반영 프롬프트
```
```

### 2.3 테스트 케이스 프롬프트
```
```

### 2.4 구현 프롬프트
```
```

---

> **작성 가이드**: Planning 미팅에서 VA와 PE가 함께 채워 넣습니다.
> 좋은 프롬프트의 5요소: What(무엇을), Why(왜), Constraint(제약), Reference(참조), Acceptance(기준)
