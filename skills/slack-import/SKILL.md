---
name: slack-import
description: "Slack 채널의 List 항목을 분석하여 블루프린트와 스프린트 프롬프트 맵을 자동 생성합니다. 채널 선택 → List 선택 → Item 선택 → 상태 업데이트 → 요구사항 분석 → 블루프린트/스프린트 생성의 워크플로우를 제공합니다."
argument-hint: "[channel-name or channel-id]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, mcp__fect-slack__slack_list_channels, mcp__fect-slack__slack_get_history, mcp__fect-slack__slack_search_channels, mcp__fect-slack__slack_get_user_info, mcp__fect-slack__slack_add_reaction, mcp__fect-slack__slack_post_message, mcp__fect-slack__slack_file_list, mcp__fect-slack__slack_list_items_list, mcp__fect-slack__slack_list_items_info, mcp__fect-slack__slack_list_items_update
---

# Slack Import: 슬랙 List 기반 블루프린트/스프린트 생성

Slack 채널에 공유된 List의 항목을 수집하고 분석하여 ASTRA 블루프린트와 스프린트 프롬프트 맵을 자동 생성합니다.

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

List를 조회할 채널 번호 또는 이름을 입력하세요:
```

사용자가 번호 또는 채널명으로 선택하면 해당 채널 ID를 `{CHANNEL_ID}`, 채널명을 `{CHANNEL_NAME}`으로 저장한다.

### Step 2: Slack List 선택

#### A. 채널 내 List 조회

`mcp__fect-slack__slack_file_list`를 호출하여 선택된 채널에 공유된 파일 목록을 가져온다:

- `channel`: `{CHANNEL_ID}`
- `count`: 100

반환된 파일 목록에서 Slack List 유형(`mimetype`이 list 관련이거나, `filetype`이 `list` 등)을 필터링한다.

> **참고**: Slack List는 파일 시스템에서 `F`로 시작하는 ID를 가진다. 파일 목록에서 List로 식별되는 항목만 추출한다. 만약 `file_list`로 List를 찾을 수 없는 경우, `mcp__fect-slack__slack_get_history`로 채널 메시지를 조회하여 List가 공유된 메시지(attachment 또는 file 정보)에서 List ID를 추출한다.

#### B. List 목록 표시 및 선택

발견된 List 목록을 사용자에게 보여주고 `AskUserQuestion`으로 선택을 요청한다:

```
## #{CHANNEL_NAME} 채널의 Slack Lists

| # | List 이름 | ID | 생성일 |
|---|-----------|-----|--------|
| 1 | 요구사항 백로그 | F01ABC | 2026-03-01 |
| 2 | 스프린트 태스크 | F02DEF | 2026-03-05 |

조회할 List 번호를 선택하세요:
```

> **List를 찾을 수 없는 경우**: 채널에 List가 없으면 사용자에게 안내하고, List ID를 직접 입력받거나 기존 메시지 기반 워크플로우로 대체할지 묻는다.

사용자가 선택하면 해당 List ID를 `{LIST_ID}`, List 이름을 `{LIST_NAME}`으로 저장한다.

### Step 3: List Item 선택

#### A. List Item 조회

`mcp__fect-slack__slack_list_items_list`를 호출하여 선택된 List의 항목을 가져온다:

- `list_id`: `{LIST_ID}`
- `limit`: 100

#### B. 상태 필터링 (시작되지 않음만 표시)

조회된 Item 목록에서 **"시작되지 않음"** 상태의 항목만 필터링한다:

1. 아래 **알려진 상태 컬럼 매핑**을 확인하여 상태 컬럼 ID와 "시작되지 않음" 옵션 ID를 확인한다

   | List ID | 상태 컬럼 ID | 시작되지 않음 | 진행중 | 완료 |
   |---------|-------------|-------------|--------|------|
   | `F0A5ZLTQ4T0` | `Col0A5L8XT9RD` | `Opt7MNHB19N` | `OptXBPNOYKC` | `OptTR35W8NA` |

2. 각 Item의 상태 컬럼 값이 "시작되지 않음" 옵션 ID와 일치하는 항목만 추출한다
   - 예: `Col0A5L8XT9RD` 값이 `Opt7MNHB19N`인 항목만 필터
3. 알려진 매핑이 없는 List의 경우, 사용자에게 상태 컬럼과 "시작되지 않음" 옵션을 확인한 뒤 필터링한다
4. 상태 컬럼이 비어있는 Item도 "시작되지 않음"으로 간주하여 포함한다

> **필터링 결과가 0건인 경우**: "시작되지 않음 상태의 항목이 없습니다. 전체 항목을 표시할까요?" 라고 `AskUserQuestion`으로 확인한다.

#### C. Item 목록 표시

필터링된 Item 목록을 테이블로 표시한다. 각 Item의 필드(컬럼) 값을 가독성 있게 보여준다:

```
## {LIST_NAME} — 항목 목록 (시작되지 않음)

| # | 제목 | 상태 | 담당자 | 마감일 | 기타 |
|---|------|------|--------|--------|------|
| 1 | 회원가입 이메일 인증 기능 | 시작되지 않음 | @kim | 03-15 | High |
| 2 | PG 결제 연동 | 시작되지 않음 | @lee | 03-20 | High |
| ... | ... | ... | ... | ... | ... |

총 {전체}건 중 {필터링}건 표시 (시작되지 않음만)

처리할 항목을 선택하세요 (번호, 범위, 또는 'all'):
예: 1  또는  1,3,5  또는  all
여러 항목을 하나의 블루프린트로 묶으려면 괄호를 사용하세요: (1,2,3)
```

> **컬럼 매핑**: List의 스키마(컬럼 정의)를 기반으로 테이블 헤더를 동적으로 구성한다. `mcp__fect-slack__slack_list_items_info`를 첫 번째 Item에 호출하여 스키마 구조를 파악할 수 있다.

#### D. 사용자 항목 선택

`AskUserQuestion`으로 사용자의 선택을 받는다.

**기본 동작**: 각 Item은 **1개의 독립된 블루프린트**로 생성된다. 여러 Item을 하나의 블루프린트로 묶으려면 괄호 `()` 그룹핑 문법을 사용해야 한다.

지원하는 입력 형태:

- `1` — 단일 항목 선택
- `1,3,5` — 개별 번호 (쉼표 구분, 각각 별도 블루프린트)
- `1-5` — 범위 (각각 별도 블루프린트)
- `all` — 전체 선택 (각각 별도 블루프린트)
- `1-3,7,9-12` — 범위와 개별 번호 혼합 (각각 별도 블루프린트)
- `(1,2,3)` — 괄호 그룹핑: 1, 2, 3번을 **하나의 블루프린트**로 병합
- `(1-3),4,(5,6)` — 괄호 안 범위도 지원: 1+2+3 병합, 4 독립, 5+6 병합
- `(1,2),3,(4,5)` — 혼합: 1+2 병합, 3 독립, 4+5 병합

> **파싱 순서**:
> 1. 괄호 밖의 쉼표로 최상위 토큰을 분리한다
> 2. 괄호로 감싸인 토큰: 내부를 파싱하여 하나의 병합 그룹으로 처리한다 (내부 범위 `1-3`도 전개)
> 3. 괄호 없는 토큰: 범위가 있으면 개별 번호로 전개하여 각각 독립 블루프린트로 처리한다

안내 메시지 예시:
```
처리할 항목을 선택하세요 (번호, 범위, 또는 'all'):
예: 1  또는  1,3,5  또는  all
여러 항목을 하나의 블루프린트로 묶으려면 괄호를 사용하세요: (1,2,3)
```

### Step 4: 선택된 Item 상태 업데이트

선택된 각 Item의 상태를 "진행 중"으로 업데이트한다.

#### A. 상태 필드 식별

List의 스키마에서 상태(status) 관련 컬럼을 식별한다:

1. **알려진 상태 컬럼 매핑 확인**: Step 3.B의 알려진 상태 컬럼 매핑 테이블에 해당하는 List이면 매핑을 바로 사용한다.

2. **알려진 매핑이 없는 경우**: `select` 타입 컬럼 중 상태를 나타내는 컬럼을 식별한다.
   - 3개 이상의 Item을 샘플링하여 select 컬럼의 옵션 ID 분포를 확인
   - 사용자에게 각 옵션 ID의 라벨(시작되지 않음/진행중/완료)을 `AskUserQuestion`으로 확인
   - 확인된 매핑을 이 스킬 파일의 테이블에 추가하여 다음 실행 시 재사용

> **상태 값을 찾을 수 없는 경우**: 사용자에게 상태 컬럼과 값을 직접 지정하도록 `AskUserQuestion`으로 요청한다.

#### B. 상태 업데이트 실행 (→ 진행중)

선택된 각 Item에 대해 상태를 확인한 뒤 **상태 선택 옵션**을 **"진행중"**으로 변경한다:

> **주의**: Slack List Item의 체크박스(완료 체크)는 절대 건드리지 않는다. 체크박스는 담당자가 직접 테스트를 완료한 후 수동으로 체크하는 용도이다. **상태(status) 선택 컬럼의 옵션값만** 변경한다.

1. 각 Item의 현재 상태를 확인한다. 이미 "진행중" 또는 "완료" 상태인 Item은 건너뛰고 사용자에게 알린다.
2. "시작되지 않음" 상태의 Item만 `mcp__fect-slack__slack_list_items_update`를 **Item마다 개별 호출**한다:

- `list_id`: `{LIST_ID}`
- `cells`: `[{ "column_id": "{status_column_id}", "row_id": "{Item_ID}", "select": ["{진행중_옵션_ID}"] }]`
  - 예: `[{ "column_id": "Col0A5L8XT9RD", "row_id": "Rec...", "select": ["OptXBPNOYKC"] }]` (알려진 매핑 사용 시)
  - 여러 Item을 처리할 때는 Item마다 별도 API 호출을 수행한다

업데이트 결과를 사용자에게 보고한다:

```
## 상태 업데이트 완료

| # | 항목 | 이전 상태 | 현재 상태 |
|---|------|-----------|-----------|
| 1 | 회원가입 이메일 인증 기능 | 대기 | 진행 중 |
| 2 | PG 결제 연동 | 대기 | 진행 중 |

{N}개 항목이 "진행 중"으로 업데이트되었습니다.
```

### Step 5: 선택된 Item 상세 분석

#### A. Item 데이터 수집

선택된 **모든** Item에 대해 `mcp__fect-slack__slack_list_items_info`를 **반드시** 호출하여 상세 정보를 조회한다. List 목록 API(`slack_list_items_list`)의 응답만으로는 필드 데이터가 불완전할 수 있으므로, 개별 Item 상세 조회를 생략하지 않는다.

- 각 Item의 **모든 필드 값을 원문 그대로** 수집한다 (제목, 설명, 상태, 담당자, 마감일, 우선순위, 본문/메모, 커스텀 필드 등)
- 설명(description)이나 본문(notes/memo) 등 장문 텍스트 필드가 있으면 **내용을 축약하지 않고 전체를 보존**한다
- 담당자 필드에 user ID가 있으면 이 시점에서 `mcp__fect-slack__slack_get_user_info`로 이름 조회 (고유 user ID만 한 번씩 조회, 중복 호출 방지)

#### B. 요구사항 추출

각 Item에서 다음 정보를 추출한다:

1. **기능명** (Feature Name): Item 제목 기반 핵심 기능 (한글 + 영문 kebab-case)
2. **기능 설명**: Item의 필드 데이터를 기반으로 요구사항 요약 (2-3문장)
3. **요구사항 목록**: 구체적인 기능 요구사항 (bullet list)
4. **우선순위**: Item의 우선순위 필드 또는 내용 분석으로 판단 (High/Medium/Low)
5. **관련 모듈**: 연관되는 시스템 모듈 추정
6. **기술적 고려사항**: API, DB, 외부 연동 등 기술 요소
7. **의존성**: 다른 기능과의 선후 관계
8. **디자인 참조 (Figma)**: Item 필드에서 Figma 링크(`https://www.figma.com/...` 또는 `https://figma.com/...`)를 감지하여 수집한다. 링크가 없으면 빈 값으로 둔다.
9. **담당자**: Item의 담당자 정보 (Assignee)

**병합 규칙**: 사용자가 Step 3.D에서 괄호 `()` 그룹핑으로 묶은 Item만 하나의 기능으로 병합한다. 괄호 없이 선택된 Item은 각각 독립된 기능으로 처리한다. 유사한 주제라도 자동 병합하지 않는다.

#### C. 분석 결과 확인

추출된 기능 목록을 사용자에게 보여주고 확인을 요청한다:

```
## 요구사항 분석 결과

### 기능 1: 이메일 인증 (email-verification)
- **출처**: {LIST_NAME} — Item #1 (@kim)
- **설명**: 회원가입 시 이메일 인증 코드를 발송하고 검증하는 기능
- **요구사항**:
  - 6자리 인증 코드 이메일 발송
  - 인증 코드 5분 유효시간
  - 3회 실패 시 재발송 필요
- **우선순위**: High
- **관련 모듈**: 회원 관리, 알림
- **기술 고려**: SMTP 연동, Redis 임시 저장
- **디자인 참조**: https://www.figma.com/file/abc123 (또는 없음)

### 기능 2: PG 결제 연동 (pg-payment)
- **출처**: {LIST_NAME} — Item #2 (@lee)
- **설명**: 이니시스 PG사 연동을 통한 카드/계좌이체 결제 처리
- **요구사항**: ...
- **우선순위**: High
- **관련 모듈**: 결제, 주문
- **디자인 참조**: 없음

...

수정할 내용이 있으면 알려주세요. 없으면 "확인"을 입력하세요:
```

사용자가 수정을 요청하면 해당 항목을 조정한다. "확인"이면 Step 6으로 진행한다.

### Step 6: 기존 프로젝트 컨텍스트 확인

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

#### D. dev 브랜치 전환 및 최신화

블루프린트 파일을 생성하기 전에, `dev` 브랜치로 전환하고 최신 상태로 동기화한다. 작업 브랜치는 생성하지 않으며, `dev`에서 직접 작업한다. 작업 브랜치 생성은 `/pr-merge` 실행 시 자동으로 처리된다.

1. **현재 브랜치 확인**: `git branch --show-current`
2. **이미 `dev` 브랜치인 경우 스킵**: 현재 브랜치가 `dev`이면 아래 3~5단계를 건너뛰고 pull만 실행한다 (`git pull origin dev`)
3. **미커밋 변경사항 보존**: `git status --porcelain`으로 확인하여 변경사항이 있으면 `git stash --include-untracked`로 임시 저장한다 (untracked 파일도 포함)
4. **dev 브랜치 전환 및 최신화**: `git fetch origin dev && git checkout dev && git pull origin dev`
5. **stash 복원**: step 3에서 stash 했으면 `git stash pop`으로 복원한다. 충돌 발생 시 충돌 파일 목록을 사용자에게 보고하고 수동 해결을 요청한다.

> **참고**: `dev` 브랜치가 존재하지 않으면 `main` 또는 `master` 브랜치에서 작업한다. 어떤 기본 브랜치도 없으면 현재 브랜치에서 작업한다.

### Step 7: 블루프린트 생성

각 기능별로 `docs/blueprints/{NNN}-{feature-name}/blueprint.md`를 생성한다.

#### 블루프린트 템플릿:

```markdown
# {기능명 (한글)}

## 개요
- **기능명**: {기능명}
- **출처**: Slack List "{LIST_NAME}" — @{담당자}
  <!-- 병합된 경우: @{담당자1}, @{담당자2} 형태로 모든 담당자를 나열한다 -->
- **우선순위**: {High/Medium/Low}
- **관련 모듈**: {모듈 목록}

<!-- Figma 링크가 있는 경우에만 이 섹션을 포함한다 -->
## 디자인 참조
- **Figma**: {Figma URL}

## 배경 및 목적
{Item 데이터를 바탕으로 작성한 배경 설명}

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

## 원본 Slack List Item

> **List**: {LIST_NAME}
> **담당자**: @{담당자}
> **상태**: 진행 중

아래는 `slack_list_items_info`로 조회한 원본 필드 데이터 전체이다. 축약하지 않고 모든 필드를 그대로 포함한다.

> **병합된 경우 (괄호 그룹핑)**: 각 원본 Item의 데이터를 `### 원본 Item {N}: {제목}` 소제목으로 구분하여 모두 포함한다. 어떤 Item의 데이터도 생략하지 않는다.

| 필드명 | 값 |
|--------|-----|
| {필드1 이름} | {필드1 값 — 전체 내용} |
| {필드2 이름} | {필드2 값 — 전체 내용} |
| ... | ... |

> **장문 텍스트 필드** (설명, 메모, 본문 등)는 아래에 원문 전체를 포함한다:
>
> {장문 필드 원문 전체 — 줄바꿈 포함하여 그대로 기재}
```

### Step 8: 스프린트 프롬프트 맵 생성

#### A. 스프린트 번호 결정

1. `docs/sprints/` 디렉토리에서 `sprint-{N}-{name}/` 패턴의 디렉토리를 스캔하여 가장 큰 스프린트 번호를 확인
2. 해당 스프린트의 `progress.md`를 읽어 **End Date** 필드를 파싱한다. `Bash`로 `date` 명령을 실행하여 오늘 날짜를 가져온다.
   - **End Date가 오늘 이후**: 활성 스프린트로 판단 → 사용자에게 확인: "Sprint {N}이 진행 중입니다 (종료: {End Date}). 이 스프린트에 추가할까요, 새 스프린트를 시작할까요?"
   - **End Date가 오늘 이전 또는 End Date 파싱 불가**: 완료된 스프린트로 판단 → 다음 번호로 새 스프린트 생성
3. 활성 스프린트가 없거나 사용자가 새 스프린트를 원하면 다음 번호로 생성

#### B. 프롬프트 맵 생성 또는 업데이트

**새 스프린트 생성 시**: 스프린트 디렉토리명을 `sprint-{N}-{primary-feature-name}/` 형태로 생성한다 (예: `sprint-1-auth/`, `sprint-2-workspace/`). `{primary-feature-name}`은 추출된 기능 중 첫 번째 기능명을 사용한다. `docs/sprints/sprint-{N}-{primary-feature-name}/prompt-map.md`를 생성한다.

```markdown
# Sprint {N} Prompt Map

## Sprint Goal
Slack List "{LIST_NAME}" 에서 수집된 요구사항 기반 — {기능 요약}

## Source
- **Slack List**: {LIST_NAME} ({LIST_ID})
- **Slack Channel**: #{CHANNEL_NAME}
- **Collected**: {YYYY-MM-DD}
- **Items Analyzed**: {분석된 Item 수}
- **Features Extracted**: {추출된 기능 수}

## Feature {F}: {feature-name}

> **번호 규칙**: `{F}`는 Feature 순번 (1, 2, 3, ...). 서브섹션도 `{F}.1`, `{F}.2` 형태로 Feature 번호와 일치시킨다. 이는 `sprint-init` 스킬의 프롬프트 맵 형식과 동일하다.

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

**기존 스프린트에 추가 시**: 기존 `prompt-map.md`를 읽고, `## Feature {#}:` 패턴으로 마지막 Feature 번호를 파악한 뒤, 해당 번호 + 1부터 새 기능을 번호 매긴다. 서브섹션도 `{F}.1`, `{F}.2` 형식으로 Feature 번호와 일치시킨다.

#### C. 진행 추적 파일 생성/업데이트

새 스프린트인 경우 `docs/sprints/sprint-{N}-{sprint-name}/progress.md`를 생성한다:

```markdown
# Sprint {N} Progress Tracker

## Sprint Information
- **Sprint Number**: {N}
- **Sprint Goal**: Slack List "{LIST_NAME}" 기반 요구사항 구현
- **Start Date**: {YYYY-MM-DD}
- **End Date**: {YYYY-MM-DD} (+7 days)
- **Status**: In Progress

<!-- SLACK_LIST_MAPPING_START -->
## Slack List Mapping

- **List ID**: {LIST_ID}
- **List Name**: {LIST_NAME}
- **Status Column**: {status_column_id}
- **Status Options**: `시작되지 않음`={시작되지않음_옵션_ID}, `진행중`={진행중_옵션_ID}, `완료`={완료_옵션_ID}

| Feature | Slack Item ID |
|---------|---------------|
| {feature-1} | {Rec_ID_1} |
| {feature-2} | {Rec_ID_2} |
<!-- SLACK_LIST_MAPPING_END -->

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
- **Overall Progress**: 0%
- **Last Updated**: {YYYY-MM-DD HH:MM}
<!-- SUMMARY_END -->

<!-- ACTIVITY_LOG_START -->
## Activity Log

| Timestamp | Event | File | Details |
|-----------|-------|------|---------|
| {YYYY-MM-DD HH:MM} | Blueprint Created | docs/blueprints/{NNN}-{feature}/blueprint.md | Slack List "{LIST_NAME}"에서 추출 |
<!-- ACTIVITY_LOG_END -->
```

기존 스프린트에 추가하는 경우 progress.md의 테이블에 새 행을 추가하고, Activity Log에 기록한다.

#### D. 회고 템플릿 생성

새 스프린트인 경우 `docs/sprints/sprint-{N}-{sprint-name}/retrospective.md`를 생성한다 (sprint-init 스킬과 동일한 포맷).

### Step 9: Slack 피드백 (선택)

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
:spiral_calendar_pad: 프롬프트 맵: docs/sprints/sprint-{N}-{sprint-name}/prompt-map.md
```

### Step 10: 결과 요약

```
## Slack to Sprint 완료

### 소스
- **채널**: #{CHANNEL_NAME}
- **List**: {LIST_NAME} ({LIST_ID})
- **분석 Item**: {N}개
- **추출 기능**: {M}개
- **상태 업데이트**: {N}개 항목 → "진행 중"

### 생성된 블루프린트
| # | 기능명 | 경로 | 우선순위 |
|---|--------|------|----------|
| {NNN} | {기능명} | docs/blueprints/{NNN}-{name}/ | High |
| {NNN} | {기능명} | docs/blueprints/{NNN}-{name}/ | Medium |

### 스프린트
- **Sprint {N}** 프롬프트 맵: docs/sprints/sprint-{N}-{sprint-name}/prompt-map.md
- **Sprint {N}** 진행 추적: docs/sprints/sprint-{N}-{sprint-name}/progress.md
- **Sprint {N}** 회고 템플릿: docs/sprints/sprint-{N}-{sprint-name}/retrospective.md

### 다음 단계
1. 생성된 블루프린트를 검토하고 DE와 함께 요구사항 확인
2. `/sprint-init {N}`으로 스프린트 세부 계획 조정
3. 프롬프트 맵의 각 단계를 순서대로 실행
4. `/test-scenario`로 E2E 테스트 시나리오 생성
```

## 빠른 실행 예시

```
# 대화형 모드 — 채널 목록에서 선택
/slack-import

# 채널 이름으로 직접 지정
/slack-import project-tasks

# 채널 ID로 직접 지정
/slack-import C01234567890
```

## 주의사항

- `SLACK_BOT_TOKEN` 환경 변수가 설정되어 있어야 한다. 미설정 시 안내 메시지를 출력하고 중단한다.
- 프로젝트가 ASTRA로 초기화되어 있어야 한다 (`CLAUDE.md`, `docs/blueprints/` 존재). 미초기화 시 `/project-init` 안내.
- 기존 블루프린트 파일은 덮어쓰지 않는다. 중복 시 사용자 확인 후 처리.
- List Item의 필드 구조는 List마다 다를 수 있으므로, 스키마를 동적으로 파악하여 처리한다.
- 상태 업데이트 가드: Step 4.B에서 "진행중" 또는 "완료" 상태의 Item은 자동으로 건너뛴다. "전체 항목 표시" 폴백으로 선택된 경우에도 동일하게 적용된다.
- **체크박스 금지**: Slack List Item의 체크박스(완료 체크)는 자동화로 변경하지 않는다. 체크박스는 담당자가 직접 테스트 완료 후 수동으로 체크하는 용도이다. 모든 상태 변경은 상태 선택(select) 컬럼의 옵션값만 업데이트한다.
