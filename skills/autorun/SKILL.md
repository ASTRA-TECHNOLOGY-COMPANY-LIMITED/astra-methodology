---
name: autorun
description: "ASTRA 풀 자동 실행 — 사용자 입력 없이 기획부터 PR 머지·worktree 제거까지 완전 자동 진행하며, 테스트 통과 시까지 최대 N회 자동 반복합니다. /service-planner(HTML 기획화면 포함) → blueprint → /sprint-init → /test-scenario → 구현(/generate-entity + 청사진 기반) → /test-run → /pr-merge --auto → worktree 자동 제거를 순차 실행하고, 테스트 실패 시 실패 원인을 분류해 적절한 단계부터 재진입(자가 개선 루프)합니다. 모든 사용자 선택 단계는 스마트 디폴트로 자동 결정되며, 시작 시 최대 반복 횟수만 1회 입력받습니다. gh 인증 누락·머지 충돌·Critical 리뷰 이슈 같은 진짜 차단 상황에서만 HITL이 발동됩니다. 한 번의 명령으로 1주일치 작업을 무인 실행하고자 할 때 사용합니다."
argument-hint: "[기능 설명] [--max-iter=N] (N 미지정 시 기본 3회, 1회로 지정하면 단일 패스)"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task, TodoWrite, Skill, AskUserQuestion
---

# ASTRA 풀 자동 실행 (`/autorun`)

기획 → 디자인 → 청사진 → 스프린트 계획 → 구현 → 테스트까지 **사용자 입력 없이 자동 실행**하고, `/pr-merge` 직전에 정지합니다.

> **🌐 LANGUAGE RULE**: Before executing this skill, read the project's `CLAUDE.md` and check the `## Language` section. If the project language is NOT Korean (`ko`), translate ALL user-facing output and propagate the language preference to all sub-skills invoked.

## 핵심 원칙

1. **무인 실행 (Zero-Interaction during pipeline)**: 파이프라인 진행 중에는 `AskUserQuestion`을 호출하지 않는다. **단 한 번의 예외**: 시작 시 `--max-iter` 인자가 없을 때 *최대 반복 횟수*만 1회 묻는다. 이후 모든 결정은 자동 디폴트.
2. **순차 실행 (Sequential)**: 각 단계가 성공해야 다음 단계로 진행한다. 병렬화하지 않는다 (문서 의존성 때문).
3. **자가 개선 반복 (Self-Improving Loop)**: 테스트(Stage 7) 실패 시 즉시 정지하지 않고, 실패 원인을 분류하여 *적절한 단계부터 재진입*한다. 최대 N회까지 반복하며, 모든 테스트 통과 시 즉시 종료(early exit). 5회 디버그 후에도 실패 + 마지막 iteration이면 정지.
4. **컨텍스트 효율성 (Context Efficiency)**: iteration 간 핸드오프는 `iter-{i}-summary.md`(200줄 이내)만으로 한다. 전체 청사진/기획 문서를 매 iteration마다 재로딩하지 않는다.
5. **풀 자동 머지 (Full Auto Merge)**: 모든 테스트가 통과하면 `/pr-merge --auto`를 자동 호출하여 PR 생성·코드 리뷰·머지·worktree 제거까지 일관 수행한다. **단, 진짜 차단 상황**(gh 인증 누락, 머지 충돌, Critical 리뷰 이슈)에서는 `/pr-merge`가 일반 모드와 동일하게 HITL로 정지한다.
6. **멱등성 (Idempotent)**: 중간 실패 후 재실행 시 이미 완료된 단계와 iteration을 모두 인식하고, 마지막 미완료 지점부터 재개한다.
7. **Goal-Driven**: 각 단계마다 검증 가능한 성공 기준(파일 존재 여부, 테스트 통과)을 확인한다.

## 입력

```
/autorun {기능 설명} [--max-iter=N]
```

**예시**:
- `/autorun 사용자 인증 기능 구축` (대화형으로 N 입력받음, 기본 3)
- `/autorun 결제 구독 시스템 --max-iter=5` (무인 실행, 최대 5회 반복)
- `/autorun 학생 출결 관리 기능 --max-iter=1` (단일 패스, 반복 비활성화)

**`--max-iter` 의미**: 기획→구현→테스트 사이클의 *최대* 반복 횟수. 테스트가 통과하면 그 즉시 종료(early exit)하므로 항상 N회를 채우지는 않는다. 권장값은 3 (1=single-pass, 5+ 비용 폭증).

## 단계 0: 입력 파싱 및 기능 이름 결정

### 0.1 기능 설명 추출
`$ARGUMENTS`에서 기능 설명을 가져온다. 비어있으면 다음 메시지를 출력하고 정지:
```
❌ 기능 설명이 필요합니다.
사용법: /autorun {기능 설명}
예: /autorun 학생 출결 관리 시스템
```

### 0.2 기능 이름(slug) 자동 생성
- 한글 → 영문 의미 번역 (LLM이 직접 결정)
- kebab-case 변환 (예: "학생 출결 관리" → `student-attendance`)
- 너무 길면 핵심 단어 1-2개로 축약

### 0.3 진행 추적 초기화
`TodoWrite`로 다음 todos를 생성:
1. Stage 0.5: 최대 반복 횟수 결정
2. Stage 1: 기획 + HTML 기획화면 (/service-planner)
3. Stage 1.5: 기획 검증 (planner-reviewer)
4. Stage 2.5: 디자인 토큰 검증 (design-token-validator) — 기획화면 styles.css 대상
5. Stage 3: 청사진 작성 (blueprint.md)
6. Stage 3.5: 청사진 검증 (blueprint-reviewer)
7. Stage 4: 스프린트 계획 (/sprint-init)
8. Stage 5: 테스트 시나리오 (/test-scenario) — TDD: 구현 이전
9. Stage 6: 구현 (/generate-entity + 청사진 기반)
10. Stage 7: 테스트 실행 (/test-run)
11. Stage 7.5: Iteration 루프 (실패 시 재진입, early exit on pass)
12. Stage 8: /pr-merge --auto 자동 실행 (PR 생성·코드 리뷰·머지·worktree 제거)
13. Stage 9: 최종 보고서 (머지 결과 포함)

## 단계 0.5: 최대 반복 횟수(N) 결정

### 0.5.1 인자 파싱
`$ARGUMENTS`에서 `--max-iter=N` 패턴을 찾는다 (정규식: `--max-iter=([0-9]+)`).

- **인자 발견**: N을 즉시 채택 (1 ≤ N ≤ 10 범위 검증, 범위 외면 클램프 후 경고).
- **인자 없음**: 다음 한 번만 `AskUserQuestion`을 호출:
  - 질문: "최대 반복 횟수를 입력하세요 (기획→테스트 사이클을 몇 번까지 자동 반복할까요?)"
  - 옵션: `1 (단일 패스)` / `3 (권장 — 기본값)` / `5 (집요한 자가 개선)` / `직접 입력`
  - 무응답/타임아웃: **3** 자동 채택

### 0.5.2 Iteration 컨텍스트 변수 초기화
다음 변수를 세션 컨텍스트에 보존:
- `MAX_ITER` = N (최대 반복 횟수)
- `CURRENT_ITER` = 1 (현재 진행 중인 iteration 번호)
- `ITER_DIR` = `docs/sprints/sprint-{N}-{feature-slug}/iterations/` (Stage 4 완료 후 확정)
- `ITER_HISTORY` = [] (각 iteration 결과 누적)

### 0.5.3 사용자에게 출력
```
🔁 ASTRA Autorun 시작 — 최대 {N}회 반복 모드
   기능: {feature-slug}
   Iteration 1/{N} 진행 시작...
```

## 단계 1: 기획 자동 실행 (`/service-planner`)

### 1.1 자동 결정 디폴트
`/service-planner`의 SKILL.md를 읽되, **사용자 프롬프트가 있는 모든 단계를 자동 디폴트로 우회**한다:

| 결정 지점 | 자동 디폴트 |
|---|---|
| 기획 모드 (신규/개선) | `docs/planner/` 비어있음 → **신규**, 기존 디렉토리 존재 → **개선** |
| 액터 다중 선택 | 도출된 **모든 액터 자동 선택** |
| 페르소나 인터뷰 진행 여부 | **무조건 진행** |
| 아이디어 다중 선택 | Impact 점수 상위 **5개 자동 선택** (5개 미만이면 전체) |
| 진행 확인 (Y/N) | **무조건 Y** |
| 언어 선택 | 프로젝트 `CLAUDE.md`의 `## Language` 섹션 따름, 없으면 한국어 |

### 1.2 실행
`/service-planner {기능 설명}`을 호출하되, 위 디폴트를 명시적으로 적용한다. `Skill` 도구로 호출.

### 1.3 성공 기준 검증
다음 6개 파일이 모두 존재해야 한다:
```
docs/planner/{NNN}-{feature-slug}/
├── market-analysis.md
├── interview-report.md
├── requirements-definition.md
├── usecase-definition.md
├── ia-screen-design.md
└── feature-definition.md
```

하나라도 없으면 **STOP** + 오류 보고.

`PLANNER_DIR` 변수에 생성된 디렉토리 경로 저장.

## 단계 1.5: 기획 검증 (자동, 비차단)

```
Task(planner-reviewer, "{PLANNER_DIR} 검증")
```

검증 결과를 진행 로그에 기록하되, **P0 이슈가 있어도 다음 단계로 진행**한다 (무인 실행 원칙). P0 이슈는 최종 보고서에서 강조한다.

## 단계 2.5: 디자인 토큰 검증 (자동, 비차단)

`/service-planner`가 생성한 HTML 기획화면(`{PLANNER_DIR}/styles.css`, `{PLANNER_DIR}/SCR-*.html`, `{PLANNER_DIR}/index.html`)을 대상으로 토큰 준수 여부를 검증한다.

```
Task(design-token-validator, "{PLANNER_DIR} 검증 — styles.css, SCR-*.html, index.html에서 하드코딩 색상/사이즈가 var(--*) 토큰을 우회하지 않는지 확인")
```

P0 이슈는 최종 보고서에 기록하고 진행.

## 단계 3: 청사진 자동 작성 (`/blueprint` 스킬 위임)

v5.1+ 이전에는 인라인으로 청사진을 작성했으나, `/blueprint` 전용 스킬로 분리되었다. autorun은 단순히 스킬을 `--auto` 모드로 호출한다.

### 3.1 청사진 스킬 호출

```
Skill('blueprint', '{feature-slug} --auto --from-planner={PLANNER_DIR}')
```

- `--auto`: HITL 스킵 (PK 전략·트랜잭션 경계·외부 호출 동기성 모두 보수적 디폴트 적용 — auto-inc PK / 단일 트랜잭션+Outbox / 동기+Circuit Breaker)
- `--from-planner`: `/service-planner` 산출물(`PLANNER_DIR`)을 자동 로드해 6종 산출물에서 청사진 본문 도출

호출 결과로 다음이 생성된다:
- `docs/blueprints/{NNN}-{feature-slug}/blueprint.md` — 10개 표준 섹션 (Section 10 HITL Triggers 포함)
- `docs/blueprints/{NNN}-{feature-slug}/review.md` — blueprint-reviewer 자동 호출 결과 (스킬 내부에서 수행)

`BLUEPRINT_PATH` 변수에 청사진 경로를 저장한다.

### 3.2 청사진 표준 섹션 (`/blueprint` 스킬이 자동 작성)

1. **개요** (목적, 배경, 범위, KPI)
2. **기능 명세** (사용자 시나리오, 비즈니스 규칙)
3. **데이터 모델** (ER 다이어그램, 테이블 DDL — 한국 공공데이터 표준 준수)
4. **API 명세** (엔드포인트, 요청/응답 JSON Schema, 에러 코드)
5. **시퀀스 다이어그램** (정상 / 예외 경로 Mermaid)
6. **비즈니스 로직 설계** (의사코드 — 실행 코드 아님)
7. **에러 처리 정책**
8. **비기능 요구사항** (성능·보안·가용성)
9. **테스트 전략 개요**
10. **HITL Triggers (구현 단계용)** — `/feature-dev`가 단계 5에서 그대로 따라 *꼭 필요한 결정*에서만 사용자에게 묻도록 가이드

### 3.3 자동 적용 스킬 트리거
`/blueprint` 스킬이 DDL을 작성하는 동안 `data-standard` 스킬과 PostToolUse 훅이 자동 발동되어 TB_/TC_ 접두사, _YMD/_DT 접미사, 금칙어 검증을 수행한다 (autorun은 별도 호출 불필요).

### 3.4 검증 결과 수집 (이전 단계 3.5)

`Task(blueprint-reviewer, ...)`는 `/blueprint` 스킬 내부에서 자동 수행되므로 autorun은 별도 호출하지 않는다. `review.md`를 읽어 P0 이슈 수만 최종 보고서에 기록하고 진행한다.

```bash
P0_ISSUES=$(grep -c "P0" "docs/blueprints/{NNN}-{feature-slug}/review.md" 2>/dev/null || echo 0)
echo "blueprint-reviewer P0 이슈: $P0_ISSUES개"
```

### 3.5 청사진 자동 커밋 (worktree 가시성 보장)

`/blueprint --auto`는 내부 Step 6에서 청사진을 메인 worktree의 현재 브랜치(dev)에 자동 commit한다. autorun은 commit 결과만 확인하면 된다.

```bash
# autorun이 메인 worktree(dev)에 있으므로 청사진은 dev에 commit됨
# 단계 4의 sprint-init이 dev base로 sprint worktree를 생성할 때 청사진이 함께 carry된다
git log -1 --oneline -- "docs/blueprints/{NNN}-{feature-slug}/" || {
  echo "WARN: 청사진 commit이 감지되지 않습니다. sprint worktree에서 청사진이 보이지 않을 수 있습니다."
}
```

## 단계 4: 스프린트 계획 (`/sprint-init`)

### 4.1 자동 결정 디폴트

| 결정 지점 | 자동 디폴트 |
|---|---|
| 스프린트 번호 | `docs/sprints/` 스캔 후 다음 번호 |
| 기능 이름 | 기능 slug 자동 사용 |
| 청사진 연결 | Stage 3의 `BLUEPRINT_PATH` 자동 매핑 |
| 진행 확인 | **무조건 Y** |

### 4.2 실행
`Skill('sprint-init', '{기능 slug}')` 호출.

> **v5.0+ 중요**: `/sprint-init`은 `.astra-worktrees/sprint-<N>-<feature-slug>/`에 sprint worktree를 생성하고 모든 sprint 산출물을 그 안에 작성한다. autorun은 호출 직후 **반드시 worktree 경로로 cd**한 뒤 단계 5 이후를 실행해야 한다. cd하지 않으면 단계 5(테스트 시나리오)/단계 6(구현)의 산출물과 단계 7의 `/test-run`, 단계 8의 `/pr-merge --auto`가 모두 메인 worktree에서 일어나 격리가 깨진다.

### 4.3 성공 기준 + worktree 이동
```
.astra-worktrees/sprint-{N}-{feature-slug}/
├── .astra-worktree.env          # 포트 베이스
└── docs/sprints/sprint-{N}-{feature-slug}/
    ├── prompt-map.md
    ├── progress.md
    └── retrospective.md
```

```bash
WT_PATH=".astra-worktrees/sprint-${N}-${feature-slug}"
cd "$WT_PATH" || {
  echo "ERROR: sprint worktree로 이동 실패: $WT_PATH" >&2
  exit 1
}
```

`SPRINT_DIR`은 worktree 내부 경로(`docs/sprints/sprint-{N}-{feature-slug}/`)로 저장한다. 이후 모든 stage(5/6/7)는 이 디렉토리에서 실행된다.

## 단계 5: 테스트 시나리오 (`/test-scenario`) — TDD: 구현 이전

> **순서 변경 (v5.x+)**: 테스트 시나리오를 구현 *이전*에 작성하여 TDD 원칙을 따른다. 청사진에 정의된 spec을 테스트로 명문화한 뒤 구현이 그 테스트를 만족하도록 한다. 시나리오는 청사진(blueprint)을 SSoT로 사용하며, 아직 존재하지 않는 route/endpoint 코드 스캔은 자연스럽게 누락된다 (정상).

### 5.1 자동 결정 디폴트

| 결정 지점 | 자동 디폴트 |
|---|---|
| 입력 청사진/스프린트 | Stage 3, 4의 경로 자동 전달 |
| 시나리오 깊이 | **표준** (happy path + 주요 edge case) |
| Given-When-Then 형식 | **활성화** |
| 진행 확인 | **무조건 Y** |

### 5.2 실행
`Skill('test-scenario', '{기능 slug}')` 호출.

### 5.3 성공 기준
```
docs/tests/test-cases/sprint-{N}-{feature-slug}/
└── (테스트 케이스 파일들)
```

`TEST_DIR` 변수에 저장.

## 단계 6: 구현 (`/generate-entity` + 청사진 기반)

청사진의 데이터 모델 및 API 명세 섹션을 기반으로 구현하되, **Stage 5에서 작성한 테스트 시나리오를 만족하도록** 구현 방향을 잡는다:

1. **엔티티 자동 생성**: 청사진에서 테이블 정의 추출 → 각 테이블에 대해 `Skill('generate-entity', '...')` 또는 `/generate-entity` 호출
2. **서비스/컨트롤러 작성**: 청사진의 API 명세 + 테스트 시나리오의 Given-When-Then을 함께 참조하여 service/controller/repository 레이어 작성
3. **자동 적용 스킬 트리거**: 모든 Write/Edit 시 `coding-convention`, `data-standard`, `code-standard`가 자동 적용됨

### 6.2 HITL 가드 (autorun 무인 실행 원칙)

구현 중 결정점에 다다르면 청사진의 **Section 10 (HITL Triggers)**를 먼저 확인한다:

- Section 10에 명시된 결정(예: HITL-02 보안 알고리즘, HITL-03 외부 의존성)인데 청사진 본문에 답이 없으면 → autorun은 **STOP + 사용자 보고**. 무인 진행 위험.
- Section 10에 없거나 답이 청사진에 명시된 경우 → **자동 진행**. 사용자에게 묻지 않는다.
- Section 10의 Anti-HITL 목록(변수명·포맷·로그 레벨 등)에 해당하는 결정 → 코딩 컨벤션 따라 **자동 진행**.

> autorun 모드에서는 어떠한 경우에도 `AskUserQuestion`을 *최소화*한다 (시작 시 max-iter 1회 입력이 유일). Section 10 트리거가 발동되면 차단하고 명확하게 사용자 보고로 넘긴다.

### 6.3 성공 기준
- 엔티티/서비스/컨트롤러 파일이 `src/` 또는 프로젝트 표준 위치에 생성됨
- 청사진의 데이터 모델·API 명세가 모두 코드로 반영됨

실패 시 **STOP** + 사용자 개입 요청.

## 단계 7: 테스트 실행 (`/test-run`)

### 7.1 자동 결정 디폴트

| 결정 지점 | 자동 디폴트 |
|---|---|
| 테스트 환경 | **cmux 브라우저** (가용 시), 폴백: **Chrome MCP** |
| 자동 디버그 재시도 | **활성화** (최대 5회) |
| 진행 확인 | **무조건 Y** |

### 7.2 실행
`Skill('test-run', '{기능 slug}')` 호출.

### 7.3 성공 기준
- 테스트 보고서 파일 존재: `docs/tests/test-reports/sprint-{N}-{feature-slug}/`
- **모든 테스트 통과** OR 5회 재시도 후에도 명확한 실패 보고

### 7.4 결과 분기
- **모든 테스트 통과** → Stage 7.5의 *early exit 경로* 진입 → Stage 8로.
- **5회 자동 디버그 후에도 실패** → Stage 7.5의 *iteration 결정 경로* 진입.

## 단계 7.5: Iteration 루프 (자가 개선)

### 7.5.1 Iteration 종료 처리 (매 iteration 끝마다 항상 실행)

**변경 파일 추적 메커니즘**: git diff에 의존하지 않는다(autorun은 mid-pipeline에서 commit하지 않는다 — **단일 예외**: v5.1+ 단계 3.5에서 `/blueprint --auto`가 청사진 단일 커밋을 dev에 만든다. 이는 worktree 가시성 보장용이며 iteration 루프 시작 *전*이라 baseline 스냅샷에 영향 없음). 대신 **iteration 시작 시 baseline 파일 목록 스냅샷**을 저장하고, 종료 시 비교한다.

1. **Iteration 시작 시 (한 번만)**: `{ITER_DIR}/iter-{CURRENT_ITER}-baseline.txt` 생성:
   ```bash
   # 추적 대상 디렉토리의 mtime 포함 파일 목록 스냅샷
   # macOS(BSD)/Linux(GNU) find 모두 호환되도록 -exec stat 사용
   # (BSD find는 -printf 미지원이므로 stat -f '%N %m' 사용)
   find docs/planner/{NNN}-{slug} docs/blueprints/{NNN}-{slug} \
        src docs/tests/test-cases/sprint-{N}-{slug} \
        -type f 2>/dev/null \
        -exec stat -f '%N %m' {} \; 2>/dev/null \
        | sort > {ITER_DIR}/iter-{CURRENT_ITER}-baseline.txt
   # Linux 환경(GNU coreutils stat)에서는 위 명령이 실패할 수 있다.
   # 그 경우 다음 fallback 사용: -exec stat -c '%n %Y' {} \;
   ```
   - iteration 1에서는 baseline이 비어 있을 수 있다 (정상).
   - autorun이 직접 Edit으로 수정한 파일도 mtime 변화로 감지된다.
   - **플랫폼 감지**: `uname -s`로 Darwin/Linux 분기 처리 가능 (macOS는 `stat -f '%N %m'`, Linux는 `stat -c '%n %Y'`).

2. **Iteration 종료 시**: 동일 명령으로 현재 스냅샷을 떠서 baseline과 diff:
   ```bash
   # 현재 스냅샷을 동일 방식으로 생성 후 비교
   diff {ITER_DIR}/iter-{CURRENT_ITER}-baseline.txt \
        <(find docs/planner/{NNN}-{slug} docs/blueprints/{NNN}-{slug} \
               src docs/tests/test-cases/sprint-{N}-{slug} \
               -type f 2>/dev/null \
               -exec stat -f '%N %m' {} \; 2>/dev/null | sort) \
        | grep '^>' | awk '{print $2}' > /tmp/changed_files.txt
   ```
   - 결과를 summary의 "변경된 산출물" 섹션에 기록.

3. **Iteration 요약 작성**: `{ITER_DIR}/iter-{CURRENT_ITER}-summary.md` 생성 (200줄 이내):
   ```markdown
   # Iteration {i} Summary

   **결과**: PASS / FAIL
   **소요**: {duration}
   **테스트**: {passed}/{total}

   ## 변경된 산출물 (이번 iteration, baseline diff 결과)
   - {파일 경로 목록 — /tmp/changed_files.txt에서 추출}

   ## 실패 원인 분류 (FAIL 시만)
   - **분류**: CODE_BUG / SPEC_GAP / DESIGN_MISALIGN / ENV_ISSUE
   - **근거**: {1-3줄 요약, 실패 메시지·스택·로그 핵심만}
   - **다음 재진입 단계**: Stage {3|5|2|1|abort}
   - **수정 방향**: {1-2줄, 어느 파일의 어느 부분을 어떻게 고칠지}
   - **수정 대상 파일** (다음 iteration이 Edit 할 파일): {구체적 경로 목록}

   ## 잔존 P0 이슈
   - {planner-reviewer / blueprint-reviewer / design-token-validator P0 항목}

   ## 다음 iteration 입력 컨텍스트 (다음 회차가 읽을 것)
   - 읽어야 할 산출물: {경로 목록 — 위 "수정 대상 파일" + 직접 의존 문서 1-2개}
   - 읽지 말 것: 전체 청사진, 전체 기획 문서 (재로딩 금지)
   ```

4. `ITER_HISTORY`에 `{iter, result, classification, target_stage, changed_files_count}` 추가.

### 7.5.2 Early Exit 판정
**테스트 PASS** 시:
- 안내 출력: `✅ Iteration {CURRENT_ITER}/{MAX_ITER} 통과 — early exit`
- Stage 8로 직진.

### 7.5.3 반복 한도 도달 판정
**FAIL** 이고 `CURRENT_ITER == MAX_ITER`:
- 안내 출력: `❌ 최대 반복 횟수({MAX_ITER}) 소진, 미해결 실패 — 정지`
- Stage 8로 진행 (보고서에 미해결 실패 강조).

### 7.5.4 실패 원인 분류 (재진입 단계 결정)
**FAIL** 이고 `CURRENT_ITER < MAX_ITER` 일 때만 실행.

#### 1차: 패턴 매칭 (저비용, 우선)
`/test-run` 출력의 마지막 실패 로그를 분석:

| 신호 (정규식/키워드) | 분류 | 재진입 단계 |
|---|---|---|
| `TypeError`, `Cannot read property`, `NullPointer`, `panic:`, `Traceback`, `AttributeError`, `assertion failed`, `expected ... received`, 스택트레이스에 `src/` 경로 포함 | `CODE_BUG` | **Stage 6 (구현)** |
| `404 Not Found`, `endpoint not implemented`, `missing field`, `schema mismatch`, 테스트가 청사진에 없는 동작 요구 | `SPEC_GAP` | **Stage 3 (청사진)** |
| `screenshot diff > threshold`, `aria-label missing`, `contrast insufficient`, UI 상호작용/접근성 실패 | `DESIGN_MISALIGN` | **Stage 2 (UX)** |
| `ECONNREFUSED`, `port already in use`, `database connection`, `permission denied`, 환경/인프라 오류 | `ENV_ISSUE` | **abort** (사용자 개입 필수) |
| 위 어느 것에도 해당 안 됨 OR 복합 신호 | `AMBIGUOUS` | 2차 분류로 |

**언어 편향 주의**: 위 키워드는 JS/TS/Java/Python에 편중되어 있다. Go(`panic:`, `runtime error`)와 Rust(`thread '...' panicked`)는 일부 포함되지만, 그 외 언어/프레임워크는 AMBIGUOUS로 떨어져 2차 분류(tester-persona)로 위임될 가능성이 높다. 이는 의도된 fall-through이다 — 정확한 분류를 위한 비용 지불.

#### 2차: tester-persona 위임 (1차가 모호할 때만)
```
Task(tester-persona, "
다음 테스트 실패 로그를 분석하고 재진입 단계를 결정하세요.
- 로그: {마지막 100줄}
- 청사진 경로: {BLUEPRINT_PATH}
- 테스트 시나리오: {TEST_DIR}
출력 형식:
  classification: CODE_BUG | SPEC_GAP | DESIGN_MISALIGN | ENV_ISSUE
  target_stage: 1 | 2 | 3 | 6
  reason: <한 문장>
")
```
- 결과를 그대로 채택. `ENV_ISSUE`면 abort + Stage 8.

### 7.5.5 다음 iteration 진입 — Direct Patch 방식 (sub-skill 재호출 금지)

**중요한 설계 결정**: sub-skill(`/service-planner`, `/sprint-init` 등)은 patch/modify 모드가 없다. 재호출 시 전체 재생성하거나 idempotency 충돌로 예측 불가능한 동작을 한다. 따라서 **iteration ≥ 2에서는 sub-skill을 호출하지 않고 autorun이 직접 Read/Edit/Write로 in-place 패치**한다. Sub-skill 호출은 iteration 1에서만 발생한다.

1. `CURRENT_ITER += 1`
2. 안내 출력:
   ```
   🔁 Iteration {CURRENT_ITER}/{MAX_ITER} 진입 (Direct Patch 모드)
      재진입 단계: Stage {target_stage}
      분류: {classification}
      참조 컨텍스트: {ITER_DIR}/iter-{CURRENT_ITER-1}-summary.md
   ```
3. **컨텍스트 효율 규칙** (필수):
   - `iter-{CURRENT_ITER-1}-summary.md`를 먼저 읽는다.
   - summary의 "읽어야 할 산출물" 목록에 있는 파일만 추가 로딩.
   - 전체 청사진/기획 문서를 다시 Read하지 **않는다**. summary가 델타와 수정 방향을 정확히 명시한다.
4. **재진입 단계별 직접 패치 절차** (sub-skill 호출 X, autorun이 Edit 도구로 직접 수정):

   | target_stage | 직접 패치 대상 | 수행 작업 |
   |---|---|---|
   | **1** (기획) | `docs/planner/{NNN}-{slug}/feature-definition.md` 등 summary가 지목한 파일 | Edit으로 해당 섹션 수정. Stage 4(/sprint-init)는 **재호출 안 함** (이미 sprint dir 존재). Stage 6은 Direct Patch로 계속. |
   | **2** (UX HTML 기획화면) | `docs/planner/{NNN}-{slug}/styles.css`, `SCR-*.html`, `index.html` summary가 지목한 파일 | Edit으로 토큰/마크업 수정. 디자인 톤 변경 시 styles.css만 갱신. |
   | **3** (청사진) | `docs/blueprints/{NNN}-{slug}/blueprint.md` | Edit으로 데이터 모델/API 명세 수정. data-standard 자동 적용 스킬은 그대로 발동. 청사진 수정 시 영향받는 테스트 시나리오도 Stage 5 패치 대상에 자동 포함. |
   | **6** (구현) | `src/...` 코드 파일 — summary가 지목한 모듈/메서드 | Edit으로 직접 코드 패치. coding-convention 자동 적용. `/generate-entity` **재호출 안 함** (테이블 정의 변동 없으면). |

5. 패치 후 재실행 단계:
   - 청사진/기획/UX 수정 시 → Stage 5(테스트 시나리오) 영향받은 케이스만 재생성 (직접 Edit) → Stage 6(구현) 부분 재패치 → Stage 7(/test-run) **재호출** (이건 sub-skill이지만 idempotent)
   - 구현만 수정 시 → 곧바로 Stage 7 재호출
6. 변경된 파일 목록을 다음 iteration summary에 누적 (7.5.1 참조).

### 7.5.6 예외: Stage 5 테스트 시나리오 재호출 정책
`/test-scenario`는 idempotent하지 않을 수 있다. 따라서 재진입 시:
- 테스트 케이스 파일 중 summary가 지목한 것만 Edit으로 직접 수정
- 새로운 시나리오가 필요한 경우만 `/test-scenario` 재호출 (입력에 "추가 시나리오: {목록}" 명시)

`/test-run`은 idempotent하므로 매 iteration마다 그대로 호출한다.

## 단계 8: `/pr-merge --auto` 자동 실행 (테스트 통과 시만)

테스트가 통과(early exit)한 경우에만 진입한다. 미해결 실패(`MAX_ITER` 소진 또는 `ENV_ISSUE` abort)는 이 단계를 건너뛰고 Stage 9로 직진한다.

### 8.0 사전 조건 확인
- `CURRENT_ITER`의 최종 상태가 PASS
- 작업 디렉토리가 sprint worktree (`$WT_PATH`) 안인지 확인 — Stage 4.3에서 cd 된 상태가 유지되어야 한다.

### 8.1 `/pr-merge --auto` 호출

```
Skill('pr-merge', '--auto')
```

`/pr-merge --auto`가 다음을 자동 처리한다:

| 단계 | 처리 방식 |
|---|---|
| 미커밋 변경사항 커밋 | 자동 (확인 프롬프트 우회) |
| 브랜치 동기화 (main→staging→dev 캐스케이드) | 자동, 충돌 시 halt (HITL) |
| PR 생성 | 자동 (ASTRA 템플릿) |
| 코드 리뷰 (feature-dev:code-reviewer Agent) | 자동 |
| Critical/High 이슈 수정 (최대 3 iteration) | 자동 (Surgical Changes 원칙) |
| 머지 (최종 확인 프롬프트) | 자동 승인 |
| **sprint worktree 제거** | 자동 (메인 worktree(dev)로 복귀) |

### 8.2 HITL 발동 조건 (진짜 차단)

다음 상황에서는 `/pr-merge --auto`가 정지하고 사용자 개입을 요청한다 — autorun은 이를 그대로 위임받는다:

- **gh CLI 미인증**: `gh auth login` 안내 후 종료
- **캐스케이드 머지 충돌**: 충돌 파일 목록 출력 후 종료 (수동 해결 필요)
- **rebase 충돌** (target 브랜치 → 작업 브랜치): 동일
- **Critical 리뷰 이슈 ≥ 1건이 MAX iteration 후에도 잔존**: 머지 차단 (`gh pr merge` 호출 안 함)
- **MAX iteration 도달 + High 이슈만 잔존**: `/pr-merge` 자체의 `AskUserQuestion`이 발동 (a/b/c 선택). autorun은 이 프롬프트를 사용자에게 그대로 노출한다 — 우회하지 않음.

### 8.3 결과 캡처
`/pr-merge --auto`의 출력에서 다음을 추출하여 `MERGE_RESULT` 변수에 저장:
- PR URL
- 머지 성공 여부 (true/false)
- 리뷰 반복 횟수
- worktree 제거 여부

> **중요**: `/pr-merge`가 worktree를 제거하면 현재 작업 디렉토리가 메인 worktree(dev)로 자동 변경된다. Stage 9의 보고서 작성은 메인 worktree에서 진행한다.

---

## 단계 9: 최종 보고서

### 9.0 working directory 정합성 보장

Stage 8의 `/pr-merge --auto`가 머지 성공 시 worktree를 제거하고 메인 worktree로 cd 한다. 그러나 Skill 도구가 sub-skill의 cwd 변경을 부모 컨텍스트로 propagate하는지는 보장되지 않는다. Stage 9.1 보고서 작성 전에 명시적으로 메인 worktree로 cd 한다:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"

# Stage 8이 머지 성공으로 worktree를 제거했으면 이미 메인 worktree에 있어야 하지만,
# Skill 호출 경계에서 cwd가 유실되었을 수 있다. 무조건 메인 worktree로 cd.
MAIN_ROOT=$(astra_main_worktree_root)
if [ -z "$MAIN_ROOT" ] || [ ! -d "$MAIN_ROOT" ]; then
  echo "ERROR: 메인 worktree 경로를 확정할 수 없습니다" >&2
  exit 1
fi
cd "$MAIN_ROOT"

# 머지가 성공했으면 dev가 최신이지만, 명시적으로 동기화하여 보고서를 정확한 base에 작성한다.
if [ "$MERGE_RESULT" = "success" ]; then
  git fetch origin dev 2>/dev/null
  git checkout dev 2>/dev/null
  git pull --rebase origin dev 2>/dev/null || true
fi
```

**머지 실패 또는 미실행 케이스**: sprint worktree는 그대로 남아 있고 Stage 8을 건너뛰었다. 이 경우 worktree 안에 보고서를 쓰는 것이 합리적이지만, autorun이 메인 worktree로 cd 했다면 worktree 경로를 명시적으로 참조하여 보고서를 쓴다:

```bash
if [ "$MERGE_RESULT" != "success" ]; then
  REPORT_DIR="$MAIN_ROOT/.astra-worktrees/sprint-${SPRINT_N}-${FEATURE_SLUG}/docs/sprints/sprint-${SPRINT_N}-${FEATURE_SLUG}"
else
  REPORT_DIR="$MAIN_ROOT/docs/sprints/sprint-${SPRINT_N}-${FEATURE_SLUG}"
fi
```

### 9.1 파이프라인 실행 보고서 작성
`$REPORT_DIR/pipeline-report.md`에 다음 작성:

```markdown
# ASTRA Autorun 자동 실행 보고서

**기능**: {feature-slug}
**실행 시각**: {timestamp}
**총 소요 시간**: {duration}
**최종 결과**: ✅ MERGED / ❌ FAIL (max iterations exhausted) / ⚠️ ABORT (env issue) / 🟡 BLOCKED (Critical 리뷰 이슈 잔존)
**iterations_used**: {final_iter}/{MAX_ITER}
**머지 결과**: {MERGE_RESULT} (PR URL: {pr_url}, worktree 제거: {yes/no})

## Iteration 요약 (자가 개선 루프)

| Iter | 결과 | 재진입 단계 | 분류 | 테스트 통과율 | Summary |
|---|---|---|---|---|---|
| 1 | ❌ FAIL | - | CODE_BUG | 12/15 | iterations/iter-1-summary.md |
| 2 | ❌ FAIL | Stage 6 | SPEC_GAP | 14/15 | iterations/iter-2-summary.md |
| 3 | ✅ PASS | Stage 3 | - | 15/15 | iterations/iter-3-summary.md |

## 마지막 iteration 단계별 결과

| 단계 | 결과 | 산출물 | 검증 결과 |
|---|---|---|---|
| 1. 기획 | ✅ / ⚠️ / ❌ | {경로} | planner-reviewer: {요약} |
| 2. UX 컴포넌트 | ✅ / ⚠️ / ❌ | {경로} | design-token: {요약} |
| 3. 청사진 | ✅ / ⚠️ / ❌ | {경로} | blueprint-reviewer: {요약} |
| 4. 스프린트 계획 | ✅ / ⚠️ / ❌ | {경로} | - |
| 5. 테스트 시나리오 | ✅ / ⚠️ / ❌ | {경로} | - |
| 6. 구현 | ✅ / ⚠️ / ❌ | {파일 N개} | coding-convention: {요약} |
| 7. 테스트 실행 | ✅ / ⚠️ / ❌ | {경로} | 통과: {N}/{M} |
| 8. PR 머지 (/pr-merge --auto) | ✅ / 🟡 / ⏭️ | PR {url} | 리뷰 반복: {N}회, worktree: {removed/preserved} |

## ⚠️ 주의 필요 항목 (P0 이슈)

{검증 단계에서 발견된 P0 이슈 목록 — 마지막 iteration 기준}

## 🚫 미해결 실패 (FAIL/ABORT/BLOCKED 종료 시만)

- {분류}: {원인 요약}
- 마지막 시도: Stage {N} 재진입, 결과 {fail/abort/blocked}
- 권장 조치: {수동 디버그 / 환경 점검 / 청사진 재설계 / Critical 이슈 수동 해결}

## 📋 다음 단계

**머지 성공 시**:
1. 메인 worktree(dev)에서 다음 sprint를 시작하세요.
2. 추가 검토가 필요하면 페르소나 분석 호출:
   - 개발 검토: `Task(developer-persona)`
   - 테스트 검토: `Task(tester-persona)`

**미해결 실패 시**:
1. 위 산출물(worktree 또는 dev 브랜치)을 검토하고 수정 사항을 적용하세요.
2. sprint worktree가 남아있다면 그 안에서 수정 후 `/pr-merge`를 재실행하세요.
3. 관련 페르소나 분석이 필요하면 다음을 호출하세요:
   - 기획 검토: `Task(planner-reviewer)`
   - 디자인 검토: `Task(designer-persona)`
   - 개발 검토: `Task(developer-persona)`
   - 테스트 검토: `Task(tester-persona)`
```

### 9.2 사용자 안내 메시지 출력

```
═══════════════════════════════════════════════════════
{✅ MERGED / ❌ FAIL / ⚠️ ABORT / 🟡 BLOCKED} ASTRA Autorun 완전 자동 실행 완료

🔁 Iterations: {final_iter}/{MAX_ITER} ({early-exit on PASS / max reached / abort})

🎯 머지 결과:
  - PR URL: {pr_url 또는 "—"}
  - 머지 성공: {yes / no}
  - 리뷰 자동 수정 반복: {N}회
  - Sprint Worktree: {removed (메인 dev 복귀) / preserved (실패로 유지)}

📁 산출물 위치:
  - 기획 + HTML 기획화면: docs/planner/{NNN}-{feature-slug}/
  - 청사진: docs/blueprints/{NNN}-{feature-slug}/
  - 스프린트: docs/sprints/sprint-{N}-{feature-slug}/
  - 테스트: docs/tests/test-cases/sprint-{N}-{feature-slug}/
  - Iteration 요약: docs/sprints/sprint-{N}-{feature-slug}/iterations/
  - 보고서: docs/sprints/sprint-{N}-{feature-slug}/pipeline-report.md

⚠️ P0 이슈: {N}건 (보고서 참조)
✅ 테스트: {통과}/{전체}

{머지 성공 시 메시지}:
  ✅ dev 브랜치에 머지 완료 — 현재 메인 worktree(dev)로 복귀했습니다.
  다음 sprint를 시작하려면 /autorun 또는 /sprint-init을 실행하세요.

{미해결 실패 시 메시지}:
  ❗ /pr-merge가 자동 실행되지 못했습니다.
  원인: {Critical 이슈 잔존 / 머지 충돌 / 환경 오류 / 테스트 실패}
  해결 후 sprint worktree에서 /pr-merge를 수동 실행하세요.
═══════════════════════════════════════════════════════
```

### 9.3 `/pr-merge --auto` 호출 정책
- 테스트가 통과한 경우(early exit)에만 Stage 8에서 `/pr-merge --auto`를 자동 호출한다.
- 미해결 실패(MAX_ITER 소진 / ENV_ISSUE abort) 시에는 호출하지 않고 Stage 9에서 보고서만 작성한다.
- HITL이 정말 필요한 상황(gh 인증·머지 충돌·Critical 이슈)에서는 `/pr-merge` 자체가 정지하며, autorun은 이를 그대로 보고서에 반영한다.

## 실패 처리 정책

### 즉시 정지 조건 (Hard Stop — iteration 진입 전)
- Stage 1~6 중 산출물 파일 누락 (iteration 루프는 Stage 7 실패에만 적용)
- `/generate-entity` 또는 자동 적용 스킬이 명시적 오류 반환
- 분류 결과가 `ENV_ISSUE` (환경/인프라 문제는 iteration으로 해결 불가)

### Iteration 루프 진입 조건 (Stage 7 실패 시)
- `/test-run`이 5회 자동 디버그 후에도 실패 + `CURRENT_ITER < MAX_ITER`
  → 7.5의 분류·재진입 로직 실행
- `CURRENT_ITER == MAX_ITER`까지 도달하면 그 시점에서 정지. Stage 8(`/pr-merge --auto`)은 **건너뛰고** Stage 9 보고서 작성으로 직진.

### 비차단 조건 (Continue with Warning)
- 검증 에이전트(planner-reviewer, blueprint-reviewer, design-token-validator)의 P0 이슈
- `convention-validator`, `naming-validator` 경고
- 부수 산출물 누락 (예: README, 다이어그램 일부)

### 정지 시 출력 형식
```
❌ ASTRA Autorun 정지 (단계 {N}: {단계명})

원인: {구체적 오류 메시지}

지금까지 완료된 단계:
- ✅ 단계 1: 기획 — {경로}
- ✅ 단계 2: UX 컴포넌트 — {경로}
- ❌ 단계 3: 청사진 — 실패

권장 조치:
1. {구체적 다음 행동, 예: "청사진 수동 작성 후 /autorun {feature} --resume"}
2. 또는 실패 단계만 수동 실행: {예: "/sprint-init {feature}"}
3. 문제 진단: Task({관련 에이전트}, "...")
```

## 재개 모드 (Idempotent Resume)

### 재실행 시 동작
같은 기능 slug로 재실행되면 다음 순서로 자동 판정:

1. **Iteration 진행 상태 우선 확인**: `docs/sprints/sprint-{N}-{feature-slug}/iterations/iter-*-summary.md` 스캔
   - 가장 큰 i 값을 `LAST_ITER`로 저장
   - `LAST_ITER`의 summary가 PASS → 작업 완료, 재실행 불필요. 사용자에게 보고서 위치만 안내하고 종료.
   - `LAST_ITER`의 summary가 FAIL → `CURRENT_ITER = LAST_ITER + 1` 로 시작, summary의 `target_stage`로 점프.
   - summary 파일 없음 → 일반 Stage 단위 재개 (아래 2~7).

2. `docs/planner/{NNN}-{feature-slug}/` 6개 markdown + `index.html` + `styles.css` + `SCR-*.html` 모두 존재 → Stage 1 건너뛰기
3. `docs/blueprints/{NNN}-{feature-slug}/blueprint.md` 존재 → Stage 3 건너뛰기
4. `docs/sprints/sprint-{N}-{feature-slug}/` 존재 → Stage 4 건너뛰기
5. `docs/tests/test-cases/sprint-{N}-{feature-slug}/` 존재 → Stage 5 (테스트 시나리오) 건너뛰기
6. 구현 산출물 감지 (모듈별 시그니처 파일 존재) → Stage 6 (구현) 건너뛰기

`MAX_ITER`는 재실행 시 처리:
- `--max-iter=N` 인자가 있으면 그 값을 그대로 사용 (Stage 0.5.1 규칙 준수, 프롬프트 안 함).
- 인자가 없으면 0.5.1과 동일하게 한 번 묻는다 (사용자가 한도를 늘려 재시도할 수 있도록).

이 동작을 사용자에게 출력으로 알린다:
```
🔄 재개 모드 감지
  - 이전 iteration: 2회 완료 (마지막: FAIL, CODE_BUG)
  - Stage 1~5: ✅ 건너뜀
  - Stage 6 (구현): ⏳ Iteration 3 재개 시작 (target: Stage 6)
  - 컨텍스트: iter-2-summary.md 참조
```

## 사용 시 주의사항

### 적합한 사용 사례
- **신규 기능을 빠르게 프로토타이핑**할 때
- **Sprint 0 직후 첫 기능 시드**가 필요할 때
- **데모 환경 셋업**을 위한 빠른 풀스택 생성

### 부적합한 사용 사례
- 기존 코드베이스의 **부분 수정 / 버그 픽스** (자체 호출 비용이 너무 큼)
- **민감한 비즈니스 로직** (사용자 검토 게이트 없이 진행되어 위험)
- **레거시 통합** (자동 결정만으로 호환성 보장 어려움)
- **법규/컴플라이언스 영향** 기능 (수동 검토 필수)

### 권장 후속 워크플로우
1. 파이프라인 완료 → `pipeline-report.md` 검토
2. P0 이슈 수동 수정
3. 페르소나 에이전트 검토 (`Task(developer-persona)`, `Task(tester-persona)`)
4. 검토 통과 시 `/pr-merge` 실행

## 다른 스킬과의 관계

| 스킬 | `/autorun`과의 관계 |
|---|---|
| `/service-planner` | Stage 1에서 호출 (디폴트 자동 적용 + HTML 기획화면 동시 생성) |
| `/handoff-publish` | **호출 안 함** (선택적 산출물, 사용자 명시 시만) |
| `/sprint-init` | Stage 4에서 호출 |
| `/generate-entity` | Stage 6에서 호출 (청사진 데이터 모델 기반 엔티티 생성) |
| `/test-scenario` | Stage 5에서 호출 (구현 *이전*, TDD 흐름) |
| `/test-run` | Stage 7에서 호출 (반복마다 재호출, 최대 MAX_ITER회) |
| `tester-persona` | Stage 7.5의 *AMBIGUOUS* 분기에서만 호출 (실패 분류) |
| `/pr-merge` | **Stage 8에서 `/pr-merge --auto`로 자동 호출** (테스트 통과 시만). 미해결 실패 시 호출 안 함. worktree 제거는 /pr-merge가 담당. |
| `/check-naming`, `/check-convention` | 자동 적용 스킬 + 검증 에이전트가 대체 수행 |

## ASTRA 4원칙 적용

| 원칙 | 파이프라인 적용 |
|---|---|
| **Think Before Coding** | 기획 단계(/service-planner)에서 모호성 검증 및 구현 방향 명확화 |
| **Simplicity First** | ⚠️ 광범위 산출물 생성형 스킬 묶음이므로 *원칙 예외* (CLAUDE.md 기재) — 단, 내부 코드는 4원칙 준수 |
| **Surgical Changes** | 기존 코드 수정 없이 신규 기능 디렉토리만 추가 |
| **Goal-Driven** | 각 단계의 산출물 파일 존재 여부가 명확한 성공 기준 |

---

**최종 점검**: 이 스킬은 *광범위 산출물 생성형 스킬*로 분류되어 Simplicity First의 범위 제한을 받지 않는다 (CLAUDE.md "ASTRA 자동 빌더 예외" 절 참조). 그러나 내부에서 호출하는 모든 코드 생성은 코딩 컨벤션과 4원칙을 그대로 따른다.
