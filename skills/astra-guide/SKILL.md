---
name: astra-guide
description: "ASTRA 방법론 빠른 참조 가이드. 워크플로우, 커맨드, 품질 게이트 요약을 표시합니다."
argument-hint: "[sprint|review|release|commands|gates|roles]"
allowed-tools: Read
---

# ASTRA 빠른 참조 가이드

`$ARGUMENTS`에 따라 해당 섹션의 가이드를 표시합니다.
인자가 없으면 전체 요약을 표시합니다.

## 전체 요약 (인자 없을 때)

```
ASTRA: AI-augmented Sprint Through Rapid Assembly
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VIP 원칙:
  V - Vibe-driven Development (의도를 전달하라)
  I - Instant Feedback Loop (시간 단위 피드백)
  P - Plugin-powered Quality (품질은 코드에 내장)

스프린트 주기: 1주
팀 구성: VA(1) + PE(1~2) + DE(1) + DSA(1) = 4~5명
```

## 섹션별 가이드

### sprint - 주간 일정

```
Monday:    Sprint Planning (1시간) + Feature Build 시작
Tue-Thu:   Feature Build (AI 코드 생성 + 인간 검증 반복)
Thursday:  Design Review (DSA 검수, 오후)
Friday:    Code Review + Sprint Review + Retrospective
```

### review - 리뷰 프로세스

```
Design Review (1시간 - DSA 주관):
  30분: DSA가 AI 생성 UI 검수 (chrome-devtools)
  30분: 디자인 이슈 수정 (PE 프롬프트 수정 → AI 재생성)

Code Review:
  /commit-push-pr        # PR 생성
  /code-review           # 5개 에이전트 병렬 리뷰
  /check-convention src/ # 코딩 표준 검사
  /check-naming src/entity/ # DB 네이밍 검사
```

### release - 릴리스 스프린트

```
Step R.1: 시스템 통합 테스트
  - API 연동 테스트
  - DB 데이터 정합성 확인
  - 성능 프로파일링
  - 크로스 브라우저/반응형 테스트

Step R.2: 최종 품질 게이트 (Gate 3)
  /code-review
  /check-convention src/
  /check-naming src/entity/

Step R.3: 배포 & 이관
  - 운영 매뉴얼 자동 생성
  - /clean_gone (브랜치 정리)
```

### commands - 커맨드 빠른 참조

```
기능 개발:
  /feature-dev [설명]         7단계 기능 개발 워크플로우
  /lookup-term [한글 용어]    표준 용어 확인
  /generate-entity [정의]     DB 엔티티 생성

코드 품질:
  /check-convention [대상]    코딩 표준 검사
  /check-naming [대상]        DB 네이밍 검사
  /code-review                5개 에이전트 병렬 리뷰

Git 워크플로우:
  /commit                     자동 커밋
  /commit-push-pr             커밋+푸시+PR 일괄
  /clean_gone                 브랜치 정리

품질 규칙:
  /hookify [설명]             행동 방지 규칙 생성
  /hookify:list               현재 규칙 목록

ASTRA 도구:
  /astra-init [프로젝트 정보] Sprint 0 초기 세팅
  /astra-global-setup         전역 개발환경 설정
  /astra-sprint [번호]        스프린트 초기화
  /astra-checklist            Sprint 0 완료 검증
  /astra-guide [섹션]         빠른 참조 가이드
```

### gates - 품질 게이트

```
Gate 1: WRITE-TIME (작성 시점, 자동)
  ├─ security-guidance: 9개 보안 패턴 차단
  ├─ standard-enforcer: 금칙어 + 네이밍 검사
  ├─ hookify: 프로젝트별 커스텀 규칙
  └─ coding-convention: 컨벤션 자동 적용

Gate 2: REVIEW-TIME (리뷰 시점)
  ├─ feature-dev code-reviewer: 코드 품질/버그
  └─ /code-review: 5개 에이전트 병렬, 80점+ 필터링

Gate 2.5: DESIGN-TIME (디자인 검수)
  └─ DSA 수동 검수 (디자인 토큰, 컴포넌트, 반응형, 접근성)

Gate 3: BRIDGE-TIME (릴리스 시점)
  ├─ /check-convention src/
  ├─ /check-naming src/entity/
  └─ chrome-devtools: UI/성능/네트워크/콘솔 에러
```

### roles - 역할 정의

```
VA (Vibe Architect) - 시니어 개발자 1명
  스크럼 마스터 + AI 오케스트레이션 + 아키텍처 의사결정

PE (Prompt Engineer) - 주니어 개발자 1~2명
  프롬프트 작성 + AI 결과물 검증

DE (Domain Expert) - 고객사 현업 담당자 1명
  요구사항 전달 + 우선순위 관리 + 실시간 피드백

DSA (Design System Architect) - 디자이너 1명
  디자인 시스템 구축 + AI 생성 UI 검수
```

## 가이드 표시 규칙

- `$ARGUMENTS`가 위 섹션명과 일치하면 해당 섹션만 표시
- `$ARGUMENTS`가 없으면 전체 요약 + commands 섹션 표시
- `$ARGUMENTS`가 "all"이면 모든 섹션 표시
