---
name: astra-sprint
description: "ASTRA 새로운 스프린트를 초기화합니다. 스프린트 프롬프트 맵과 회고 템플릿을 생성합니다."
argument-hint: "[스프린트번호]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# ASTRA 스프린트 초기화

새로운 스프린트의 프롬프트 맵과 회고 템플릿을 생성합니다.

## 실행 절차

### 1단계: 스프린트 번호 확인

`$ARGUMENTS`에서 스프린트 번호를 파싱합니다. 없으면 `docs/prompts/` 디렉토리의 기존 파일을 확인하여 다음 번호를 자동 결정합니다.

### 2단계: 스프린트 프롬프트 맵 생성

`docs/prompts/sprint-{N}.md` 파일을 생성합니다:

```markdown
# Sprint {N} 프롬프트 맵

## 스프린트 목표
[이번 스프린트에서 달성할 비즈니스 가치를 서술]

## 기능 1: {기능명}

### 1.1 설계 프롬프트
/feature-dev "{기능 설명}의 설계 문서를
docs/blueprints/{feature-name}.md로 작성해줘.
{상세 요구사항}
DB 스키마는 docs/database/database-design.md를 참조할 것.
아직 코드는 수정하지 마."

### 1.2 DB 설계 반영 프롬프트
/feature-dev "docs/database/database-design.md에 {모듈명} 테이블을
추가/갱신해줘:
- {테이블 목록}
- ERD와 FK 관계 요약도 갱신할 것. 표준 용어 사전 준수.
아직 코드는 수정하지 마."

### 1.3 테스트 케이스 프롬프트
/feature-dev "docs/blueprints/{feature-name}.md의 기능 요구사항을 기반으로
테스트 케이스를 docs/tests/test-cases/{feature-name}-test-cases.md로 작성해줘.
Given-When-Then 형식, 단위/통합/엣지 케이스를 포함.
아직 코드는 수정하지 마."

### 1.4 구현 프롬프트
/feature-dev "docs/blueprints/{feature-name}.md와
docs/database/database-design.md의 내용을 엄격히 준수해서
개발을 진행해줘. 테스트는 docs/tests/test-cases/{feature-name}-test-cases.md를
참조하여 작성하고, 구현이 끝나면 모든 테스트를 실행하고
결과를 docs/tests/test-reports/에 보고해."

## 기능 2: {기능명}
{위와 동일한 구조로 반복}
```

### 3단계: 회고 템플릿 생성

`docs/retrospectives/sprint-{N}-retro.md` 파일을 생성합니다:

```markdown
# Sprint {N} Retrospective

## 날짜: {YYYY-MM-DD}

## AI 분석 데이터
- code-review 반복 이슈: [자동 수집]
- security-guidance 차단 건수: [자동 수집]
- standard-enforcer 위반 빈도: [자동 수집]

## 팀 논의 (AI가 잡지 못하는 영역)

### 잘한 것 (Keep)
-

### 개선할 것 (Problem)
-

### 시도할 것 (Try)
-

## 자동화된 개선 조치
- /hookify [이번 스프린트에서 발견된 반복 실수 규칙화]
- CLAUDE.md 업데이트 내용: [추가된 규칙 기술]
```

### 4단계: 스프린트 Planning 가이드 출력

```
## Sprint {N} 초기화 완료

### 생성된 파일
- docs/prompts/sprint-{N}.md (프롬프트 맵)
- docs/retrospectives/sprint-{N}-retro.md (회고 템플릿)

### Sprint Planning 진행 순서 (1시간)
1. (10분) AI 분석 보고서 리뷰
2. (20분) DE와 비즈니스 우선순위 확인 및 스프린트 목표 합의
3. (20분) 아이템별 프롬프트 설계 방향 논의 + DSA 디자인 방향 공유
4. (10분) 스프린트 백로그 확정

### 사전 준비 (Planning 전날, VA 실행)
/feature-dev "이번 스프린트 후보 백로그 아이템들의 기술적 복잡도를 분석해줘.
기존 코드베이스와의 의존성, 예상 작업 규모, 위험 요소를 정리해줘.
아직 코드는 수정하지 마."
```

## 주의사항

- 이미 존재하는 스프린트 파일은 덮어쓰지 않습니다.
- 프롬프트 맵은 Planning 미팅에서 VA와 PE가 함께 채워 넣습니다.
