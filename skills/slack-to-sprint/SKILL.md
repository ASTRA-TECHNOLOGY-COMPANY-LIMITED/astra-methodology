---
name: slack-to-sprint
description: "Slack 채널의 메시지를 분석하여 블루프린트와 스프린트 프롬프트 맵을 자동 생성합니다. 채널 선택 → 메시지 조회 → 항목 선택 → 요구사항 분석 → 블루프린트/스프린트 생성의 워크플로우를 제공합니다."
argument-hint: "[channel-name or channel-id]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, mcp__fect-slack__slack_list_channels, mcp__fect-slack__slack_get_history, mcp__fect-slack__slack_search_channels, mcp__fect-slack__slack_get_user_info, mcp__fect-slack__slack_add_reaction, mcp__fect-slack__slack_post_message
---

# Slack to Sprint: 슬랙 메시지 기반 블루프린트/스프린트 생성

Slack 채널에서 요구사항/태스크 메시지를 수집하고 분석하여 ASTRA 블루프린트와 스프린트 프롬프트 맵을 자동 생성합니다.

## 실행 절차

### Step 1: Slack 채널 선택

#### A. 인자 파싱

`$ARGUMENTS`를 확인한다:

| 인자 형태 | 동작 |
|-----------|------|
| 채널 ID (`C`로 시작) | 해당 채널을 바로 사용 |
| 채널 이름 (예: `project-tasks`) | `mcp__fect-slack__slack_search_channels`로 검색 후 매칭 |
| _(없음)_ | Step 1.B로 이동하여 대화형 선택 |

#### B. 대화형 채널 선택

인자가 없으면 `mcp__fect-slack__slack_list_channels`를 호출하여 채널 목록을 가져온다.

채널 목록을 사용자에게 보여주고 `AskUserQuestion`으로 선택을 요청한다:

```
## Slack 채널 목록

| # | 채널명 | ID | 유형 | 멤버 |
|---|--------|-----|------|------|
| 1 | general | C01234 | Public | Yes |
| 2 | project-tasks | C05678 | Private | Yes |
| 3 | dev-requirements | C09012 | Public | Yes |

메시지를 조회할 채널 번호 또는 이름을 입력하세요:
```

사용자가 번호 또는 채널명으로 선택하면 해당 채널 ID를 `{CHANNEL_ID}`, 채널명을 `{CHANNEL_NAME}`으로 저장한다.

### Step 2: 메시지 조회

#### A. 메시지 히스토리 가져오기

`mcp__fect-slack__slack_get_history`를 호출하여 선택된 채널의 최근 메시지를 가져온다:

- `channel`: `{CHANNEL_ID}`
- `limit`: 50 (최근 50개)

#### B. 메시지 목록 표시

가져온 메시지를 정리하여 사용자에게 보여준다:

```
## #{CHANNEL_NAME} 채널 최근 메시지

| # | 작성자 | 시간 | 내용 (요약) | 스레드 |
|---|--------|------|-------------|--------|
| 1 | @kim | 03-06 14:30 | 회원가입 시 이메일 인증 기능 필요... | 3 replies |
| 2 | @lee | 03-06 13:15 | 결제 모듈 PG 연동 요구사항 정리... | 5 replies |
| 3 | @park | 03-06 11:00 | 관리자 대시보드 권한 분리 필요... | - |
| ... | ... | ... | ... | ... |

처리할 항목을 선택하세요 (번호, 범위, 또는 'all'):
예: 1,2,5  또는  1-5  또는  all
```

각 메시지의 `user` ID는 `mcp__fect-slack__slack_get_user_info`로 이름을 조회하여 표시한다. 단, 메시지가 많을 경우 고유 user ID만 한 번씩 조회한다 (중복 호출 방지).

내용 요약은 메시지 텍스트의 첫 50자를 표시하고, 긴 메시지는 `...`으로 truncate한다.

#### C. 사용자 항목 선택

`AskUserQuestion`으로 사용자의 선택을 받는다. 지원하는 입력 형태:

- `1,3,5` — 개별 번호 (쉼표 구분)
- `1-5` — 범위
- `all` — 전체 선택
- `1-3,7,9-12` — 범위와 개별 번호 혼합

### Step 3: 선택된 메시지 상세 분석

#### A. 메시지 원문 수집

선택된 각 메시지의 전체 텍스트를 수집한다.

- 채널 히스토리에서 가져온 원본 메시지의 전체 텍스트를 사용한다.
- **스레드 답글 제한**: 현재 MCP 도구는 `conversations.replies` API를 지원하지 않으므로, 스레드 답글 내용은 조회할 수 없다. 원본 메시지의 `reply_count` 정보만 참고하여 스레드 활발도를 우선순위 판단에 활용한다.
- 스레드 답글 내용이 필요한 경우, 사용자에게 핵심 내용을 직접 입력하도록 안내한다.

#### B. 요구사항 추출

각 메시지에서 다음 정보를 추출한다:

1. **기능명** (Feature Name): 메시지에서 식별된 핵심 기능 (한글 + 영문 kebab-case)
2. **기능 설명**: 요구사항 요약 (2-3문장)
3. **요구사항 목록**: 구체적인 기능 요구사항 (bullet list)
4. **우선순위**: 메시지 내용/리액션/스레드 참여도로 판단 (High/Medium/Low)
5. **관련 모듈**: 연관되는 시스템 모듈 추정
6. **기술적 고려사항**: API, DB, 외부 연동 등 기술 요소
7. **의존성**: 다른 기능과의 선후 관계

유사한 주제의 메시지는 하나의 기능으로 병합한다.

#### C. 분석 결과 확인

추출된 기능 목록을 사용자에게 보여주고 확인을 요청한다:

```
## 요구사항 분석 결과

### 기능 1: 이메일 인증 (email-verification)
- **출처**: 메시지 #1 (@kim, 03-06 14:30)
- **설명**: 회원가입 시 이메일 인증 코드를 발송하고 검증하는 기능
- **요구사항**:
  - 6자리 인증 코드 이메일 발송
  - 인증 코드 5분 유효시간
  - 3회 실패 시 재발송 필요
- **우선순위**: High
- **관련 모듈**: 회원 관리, 알림
- **기술 고려**: SMTP 연동, Redis 임시 저장

### 기능 2: PG 결제 연동 (pg-payment)
- **출처**: 메시지 #2 (@lee, 03-06 13:15)
- **설명**: 이니시스 PG사 연동을 통한 카드/계좌이체 결제 처리
- **요구사항**: ...
- **우선순위**: High
- **관련 모듈**: 결제, 주문

...

수정할 내용이 있으면 알려주세요. 없으면 "확인"을 입력하세요:
```

사용자가 수정을 요청하면 해당 항목을 조정한다. "확인"이면 Step 4로 진행한다.

### Step 4: 기존 프로젝트 컨텍스트 확인

블루프린트와 스프린트를 생성하기 전에 기존 프로젝트 상태를 확인한다.

#### A. 프로젝트 구조 확인

1. `CLAUDE.md` 존재 여부 확인 — 없으면 사용자에게 `/project-init` 실행을 안내하고 중단
2. `docs/blueprints/` 디렉토리 스캔 — 기존 블루프린트 번호 파악
3. `docs/sprints/` 디렉토리 스캔 — 현재 스프린트 번호 파악
4. `docs/database/database-design.md` 존재 여부 확인

#### B. 중복 확인

기존 블루프린트 디렉토리명과 추출된 기능명을 비교한다:

- 이름이 유사한 블루프린트가 있으면 사용자에게 알린다
- "기존 블루프린트를 업데이트할까요, 아니면 새로 생성할까요?" 확인

#### C. 번호 결정

기존 블루프린트 디렉토리 중 가장 큰 번호를 찾아 다음 번호를 결정한다:

- 예: `001-auth/`, `002-payment/` 존재 시 → 다음은 `003`부터 시작
- 3자리 zero-padded (예: `003`, `004`, ...)

### Step 5: 블루프린트 생성

각 기능별로 `docs/blueprints/{NNN}-{feature-name}/blueprint.md`를 생성한다.

#### 블루프린트 템플릿:

```markdown
# {기능명 (한글)}

## 개요
- **기능명**: {기능명}
- **출처**: Slack #{CHANNEL_NAME} — @{작성자} ({날짜})
- **우선순위**: {High/Medium/Low}
- **관련 모듈**: {모듈 목록}

## 배경 및 목적
{메시지 원문을 바탕으로 작성한 배경 설명}

## 기능 요구사항

### 필수 요구사항 (Must)
- {요구사항 1}
- {요구사항 2}

### 선택 요구사항 (Should)
- {요구사항}

### 향후 고려 (Could)
- {요구사항}

## 기술 설계

### API 엔드포인트
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/{resource} | {설명} |

### 데이터 모델
{관련 테이블/엔티티 구조 — docs/database/database-design.md 참조하여 작성}

### 외부 연동
{외부 API, 서비스 연동 사항}

## 의존성
- **선행 기능**: {의존하는 기능}
- **후행 기능**: {이 기능에 의존하는 기능}

## 인수 조건
- [ ] {인수 조건 1}
- [ ] {인수 조건 2}

## 원본 Slack 메시지

> **채널**: #{CHANNEL_NAME}
> **작성자**: @{작성자}
> **시간**: {timestamp}
>
> {원본 메시지 텍스트}
```

### Step 6: 스프린트 프롬프트 맵 생성

#### A. 스프린트 번호 결정

1. `docs/sprints/` 디렉토리에서 가장 큰 스프린트 번호를 확인
2. 해당 스프린트의 `progress.md`를 읽어 **End Date** 필드를 파싱한다. `Bash`로 `date` 명령을 실행하여 오늘 날짜를 가져온다.
   - **End Date가 오늘 이후**: 활성 스프린트로 판단 → 사용자에게 확인: "Sprint {N}이 진행 중입니다 (종료: {End Date}). 이 스프린트에 추가할까요, 새 스프린트를 시작할까요?"
   - **End Date가 오늘 이전 또는 End Date 파싱 불가**: 완료된 스프린트로 판단 → 다음 번호로 새 스프린트 생성
3. 활성 스프린트가 없거나 사용자가 새 스프린트를 원하면 다음 번호로 생성

#### B. 프롬프트 맵 생성 또는 업데이트

**새 스프린트 생성 시**: `docs/sprints/sprint-{N}/prompt-map.md`를 생성한다.

```markdown
# Sprint {N} Prompt Map

## Sprint Goal
Slack #{CHANNEL_NAME} 채널에서 수집된 요구사항 기반 — {기능 요약}

## Source
- **Slack Channel**: #{CHANNEL_NAME}
- **Collected**: {YYYY-MM-DD}
- **Messages Analyzed**: {분석된 메시지 수}
- **Features Extracted**: {추출된 기능 수}

## Feature {F}: {feature-name}

> **번호 규칙**: `{F}`는 Feature 순번 (1, 2, 3, ...). 서브섹션도 `{F}.1`, `{F}.2` 형태로 Feature 번호와 일치시킨다. 이는 `sprint-plan` 스킬의 프롬프트 맵 형식과 동일하다.

### {F}.1 Design Prompt
/feature-dev "docs/blueprints/{NNN}-{feature-name}/blueprint.md의 설계를
기반으로 {기능 설명}을 위한 상세 설계 문서를 작성해줘.
{핵심 요구사항 요약}
docs/database/database-design.md를 참조할 것.
아직 코드는 수정하지 마."

### {F}.2 DB Design Reflection Prompt
/feature-dev "docs/blueprints/{NNN}-{feature-name}/blueprint.md를 기반으로
docs/database/database-design.md에 {관련 테이블} 테이블을 추가/수정해줘.
ERD와 FK 관계 요약도 업데이트할 것.
표준 용어 사전을 따를 것.
아직 코드는 수정하지 마."

### {F}.3 Test Case Prompt
/feature-dev "docs/blueprints/{NNN}-{feature-name}/blueprint.md의 기능 요구사항을 기반으로
docs/tests/test-cases/sprint-{N}/{feature-name}-test-cases.md에 테스트 케이스를 작성해줘.
Given-When-Then 포맷을 사용하고, 단위/통합/엣지 케이스를 포함할 것.
아직 코드는 수정하지 마."

### {F}.4 Implementation Prompt
/feature-dev "docs/blueprints/{NNN}-{feature-name}/blueprint.md와
docs/database/database-design.md의 내용을 엄격히 따라 개발을 진행해줘.
docs/tests/test-cases/sprint-{N}/{feature-name}-test-cases.md를 참조하여 테스트를 작성하고,
구현이 완료되면 모든 테스트를 실행하여
docs/tests/test-reports/에 결과를 보고해줘."

## Feature {F+1}: {feature-name}
{위와 동일한 구조 반복 — 서브섹션 번호를 Feature 번호와 일치시킨다}
```

**기존 스프린트에 추가 시**: 기존 `prompt-map.md`를 읽고, 마지막 Feature 번호 이후에 새 기능을 추가한다.

#### C. 진행 추적 파일 생성/업데이트

새 스프린트인 경우 `docs/sprints/sprint-{N}/progress.md`를 생성한다:

```markdown
# Sprint {N} Progress Tracker

## Sprint Information
- **Sprint Number**: {N}
- **Sprint Goal**: Slack #{CHANNEL_NAME} 기반 요구사항 구현
- **Start Date**: {YYYY-MM-DD}
- **End Date**: {YYYY-MM-DD} (+7 days)
- **Status**: In Progress

<!-- PROGRESS_TABLE_START -->
## Feature Progress

| Feature | Blueprint | DB Design | Test Cases | Implementation | Test Report | Status |
|---------|-----------|-----------|------------|----------------|-------------|--------|
| {feature-1} | Done | - | - | - | - | In Progress |
| {feature-2} | Done | - | - | - | - | In Progress |

**Legend**: `-` Not Started, `WIP` In Progress, `Done` Completed, `N/A` Not Applicable
<!-- PROGRESS_TABLE_END -->

<!-- SUMMARY_START -->
## Summary
- **Total Features**: {N}
- **Completed**: 0
- **In Progress**: {N}
- **Overall Progress**: {blueprint_pct}%
- **Last Updated**: {YYYY-MM-DD HH:MM}
<!-- SUMMARY_END -->

<!-- ACTIVITY_LOG_START -->
## Activity Log

| Timestamp | Event | File | Details |
|-----------|-------|------|---------|
| {YYYY-MM-DD HH:MM} | Blueprint Created | docs/blueprints/{NNN}-{feature}/blueprint.md | Slack #{CHANNEL_NAME}에서 추출 |
<!-- ACTIVITY_LOG_END -->
```

기존 스프린트에 추가하는 경우 progress.md의 테이블에 새 행을 추가하고, Activity Log에 기록한다.

#### D. 회고 템플릿 생성

새 스프린트인 경우 `docs/sprints/sprint-{N}/retrospective.md`를 생성한다 (sprint-plan 스킬과 동일한 포맷).

### Step 7: Slack 피드백 (선택)

사용자에게 Slack 채널에 처리 결과를 게시할지 묻는다:

```
Slack #{CHANNEL_NAME} 채널에 처리 결과를 게시할까요? (y/n)
```

사용자가 `y`를 선택하면 `mcp__fect-slack__slack_post_message`로 요약 메시지를 게시한다:

```
:clipboard: *ASTRA Sprint {N} — 요구사항 반영 완료*

다음 항목이 Sprint {N} 백로그로 등록되었습니다:

{기능 목록 (bullet)}

:page_facing_up: 블루프린트: docs/blueprints/ 에서 확인
:spiral_calendar_pad: 프롬프트 맵: docs/sprints/sprint-{N}/prompt-map.md
```

또한 처리된 원본 메시지에 `mcp__fect-slack__slack_add_reaction`으로 `:white_check_mark:` 리액션을 추가한다.

### Step 8: 결과 요약

```
## Slack to Sprint 완료

### 소스
- **채널**: #{CHANNEL_NAME}
- **분석 메시지**: {N}개
- **추출 기능**: {M}개

### 생성된 블루프린트
| # | 기능명 | 경로 | 우선순위 |
|---|--------|------|----------|
| {NNN} | {기능명} | docs/blueprints/{NNN}-{name}/ | High |
| {NNN} | {기능명} | docs/blueprints/{NNN}-{name}/ | Medium |

### 스프린트
- **Sprint {N}** 프롬프트 맵: docs/sprints/sprint-{N}/prompt-map.md
- **Sprint {N}** 진행 추적: docs/sprints/sprint-{N}/progress.md
- **Sprint {N}** 회고 템플릿: docs/sprints/sprint-{N}/retrospective.md

### 다음 단계
1. 생성된 블루프린트를 검토하고 DE와 함께 요구사항 확인
2. `/sprint-plan {N}`으로 스프린트 세부 계획 조정
3. 프롬프트 맵의 각 단계를 순서대로 실행
4. `/test-scenario`로 E2E 테스트 시나리오 생성
```

## 빠른 실행 예시

```
# 대화형 모드 — 채널 목록에서 선택
/slack-to-sprint

# 채널 이름으로 직접 지정
/slack-to-sprint project-tasks

# 채널 ID로 직접 지정
/slack-to-sprint C01234567890
```

## 주의사항

- `SLACK_BOT_TOKEN` 환경 변수가 설정되어 있어야 한다. 미설정 시 안내 메시지를 출력하고 중단한다.
- 프로젝트가 ASTRA로 초기화되어 있어야 한다 (`CLAUDE.md`, `docs/blueprints/` 존재). 미초기화 시 `/project-init` 안내.
- 기존 블루프린트 파일은 덮어쓰지 않는다. 중복 시 사용자 확인 후 처리.
- 메시지 분석 시 코드 스니펫, 이미지, 파일 첨부는 텍스트 내용만 분석한다.
- 스레드 답글은 현재 MCP 도구 한계로 직접 조회할 수 없다. 원본 메시지와 `reply_count`만 활용하며, 필요 시 사용자에게 핵심 내용 입력을 요청한다.
