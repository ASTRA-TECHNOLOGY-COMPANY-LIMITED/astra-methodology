---
name: autorun
description: "ASTRA 풀 자동 실행 — 사용자 입력 없이 기획부터 테스트까지 자동 진행하며, 테스트 통과 시까지 최대 N회 자동 반복합니다. /service-planner → /ux-publish → blueprint → /sprint-init → 구현(/generate-entity + 청사진 기반) → /test-scenario → /test-run을 순차 실행하고, 테스트 실패 시 실패 원인을 분류해 적절한 단계부터 재진입(자가 개선 루프)합니다. 모든 사용자 선택 단계는 스마트 디폴트로 자동 결정되며, 시작 시 최대 반복 횟수만 1회 입력받습니다. /pr-merge 직전에 정지합니다. 한 번의 명령으로 1주일치 작업을 무인 실행하고자 할 때 사용합니다."
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
5. **`/pr-merge` 직전 정지 (Hard Stop)**: 절대 `/pr-merge`를 호출하지 않는다. 사용자가 직접 검토 후 실행해야 한다.
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
2. Stage 1: 기획 (/service-planner)
3. Stage 1.5: 기획 검증 (planner-reviewer)
4. Stage 2: UX 컴포넌트 (/ux-publish)
5. Stage 2.5: 디자인 토큰 검증 (design-token-validator)
6. Stage 3: 청사진 작성 (blueprint.md)
7. Stage 3.5: 청사진 검증 (blueprint-reviewer)
8. Stage 4: 스프린트 계획 (/sprint-init)
9. Stage 5: 구현 (/generate-entity + 청사진 기반)
10. Stage 6: 테스트 시나리오 (/test-scenario)
11. Stage 7: 테스트 실행 (/test-run)
12. Stage 7.5: Iteration 루프 (실패 시 재진입, early exit on pass)
13. Stage 8: 최종 보고서 + /pr-merge 안내

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

## 단계 2: UX 컴포넌트 자동 생성 (`/ux-publish`)

### 2.1 자동 결정 디폴트

| 결정 지점 | 자동 디폴트 |
|---|---|
| 입력 디렉토리 | Stage 1의 `PLANNER_DIR` 자동 전달 |
| 디자인 톤 선택 | **Auto** (AI가 콘텐츠 기반으로 결정) |
| 진행 확인 | **무조건 Y** |
| AI 이미지 생성 여부 | **활성화** (`fect-image` MCP 사용 가능 시) |

### 2.2 실행
`Skill('ux-publish', '{기능 설명}')` 호출. PLANNER_DIR을 명시적으로 전달.

### 2.3 성공 기준
```
publish/{feature-slug}/
├── COPY-GUIDE.md
├── components/
├── screens/
└── preview/
```
디렉토리와 핵심 파일 존재 확인. 없으면 **STOP**.

## 단계 2.5: 디자인 토큰 검증 (자동, 비차단)

```
Task(design-token-validator, "publish/{feature-slug} 검증")
```

P0 이슈는 최종 보고서에 기록하고 진행.

## 단계 3: 청사진 자동 작성

### 3.1 디렉토리 결정
`docs/blueprints/` 스캔하여 다음 번호 결정 (3자리 zero-padding).

### 3.2 청사진 생성
다음 입력을 종합하여 `docs/blueprints/{NNN}-{feature-slug}/blueprint.md` 작성:
- `PLANNER_DIR/feature-definition.md` (기능 정의)
- `PLANNER_DIR/usecase-definition.md` (유스케이스)
- `PLANNER_DIR/ia-screen-design.md` (화면 설계)
- `PLANNER_DIR/requirements-definition.md` (요구사항/KPI)

### 3.3 청사진 표준 섹션 (자동 작성)
1. **개요** (목적, 배경, 범위)
2. **기능 명세** (사용자 시나리오, API 요구사항)
3. **데이터 모델** (ER 다이어그램, 테이블 설계 — 한국 공공데이터 표준 준수)
4. **API 명세** (엔드포인트 목록, 요청/응답 스키마)
5. **시퀀스 다이어그램** (Mermaid 형식)
6. **에러 처리 정책**
7. **성능 요구사항**
8. **보안 고려사항**
9. **테스트 전략 개요**

### 3.4 자동 적용 스킬 트리거
청사진 작성 중 DB 테이블/컬럼 명명 시 `data-standard` 스킬이 자동 적용된다 (TB_/TC_ 접두사, _YMD/_DT 접미사, 금칙어 검증).

`BLUEPRINT_PATH` 변수에 생성된 파일 경로 저장.

## 단계 3.5: 청사진 검증 (자동, 비차단)

```
Task(blueprint-reviewer, "{BLUEPRINT_PATH} 품질 검증")
```

P0 이슈는 최종 보고서에 기록하고 진행.

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

### 4.3 성공 기준
```
docs/sprints/sprint-{N}-{feature-slug}/
├── progress.md
└── (프롬프트 맵, 백로그 등)
```

`SPRINT_DIR` 변수에 저장.

## 단계 5: 구현 (`/generate-entity` + 청사진 기반)

청사진의 데이터 모델 및 API 명세 섹션을 기반으로 구현:

1. **엔티티 자동 생성**: 청사진에서 테이블 정의 추출 → 각 테이블에 대해 `Skill('generate-entity', '...')` 또는 `/generate-entity` 호출
2. **서비스/컨트롤러 작성**: 청사진의 API 명세에 따라 service/controller/repository 레이어 작성
3. **자동 적용 스킬 트리거**: 모든 Write/Edit 시 `coding-convention`, `data-standard`, `code-standard`가 자동 적용됨

### 5.3 성공 기준
- 엔티티/서비스/컨트롤러 파일이 `src/` 또는 프로젝트 표준 위치에 생성됨
- 청사진의 데이터 모델·API 명세가 모두 코드로 반영됨

실패 시 **STOP** + 사용자 개입 요청.

## 단계 6: 테스트 시나리오 (`/test-scenario`)

### 6.1 자동 결정 디폴트

| 결정 지점 | 자동 디폴트 |
|---|---|
| 입력 청사진/스프린트 | Stage 3, 4의 경로 자동 전달 |
| 시나리오 깊이 | **표준** (happy path + 주요 edge case) |
| Given-When-Then 형식 | **활성화** |
| 진행 확인 | **무조건 Y** |

### 6.2 실행
`Skill('test-scenario', '{기능 slug}')` 호출.

### 6.3 성공 기준
```
docs/tests/test-cases/sprint-{N}-{feature-slug}/
└── (테스트 케이스 파일들)
```

`TEST_DIR` 변수에 저장.

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

**변경 파일 추적 메커니즘**: git diff에 의존하지 않는다(autorun은 mid-pipeline에서 commit하지 않음). 대신 **iteration 시작 시 baseline 파일 목록 스냅샷**을 저장하고, 종료 시 비교한다.

1. **Iteration 시작 시 (한 번만)**: `{ITER_DIR}/iter-{CURRENT_ITER}-baseline.txt` 생성:
   ```bash
   # 추적 대상 디렉토리의 mtime 포함 파일 목록 스냅샷
   # macOS(BSD)/Linux(GNU) find 모두 호환되도록 -exec stat 사용
   # (BSD find는 -printf 미지원이므로 stat -f '%N %m' 사용)
   find docs/planner/{NNN}-{slug} docs/blueprints/{NNN}-{slug} \
        publish/{slug} src docs/tests/test-cases/sprint-{N}-{slug} \
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
               publish/{slug} src docs/tests/test-cases/sprint-{N}-{slug} \
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
| `TypeError`, `Cannot read property`, `NullPointer`, `panic:`, `Traceback`, `AttributeError`, `assertion failed`, `expected ... received`, 스택트레이스에 `src/` 경로 포함 | `CODE_BUG` | **Stage 5 (구현)** |
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
  target_stage: 1 | 2 | 3 | 5
  reason: <한 문장>
")
```
- 결과를 그대로 채택. `ENV_ISSUE`면 abort + Stage 8.

### 7.5.5 다음 iteration 진입 — Direct Patch 방식 (sub-skill 재호출 금지)

**중요한 설계 결정**: sub-skill(`/service-planner`, `/ux-publish`, `/sprint-init` 등)은 patch/modify 모드가 없다. 재호출 시 전체 재생성하거나 idempotency 충돌로 예측 불가능한 동작을 한다. 따라서 **iteration ≥ 2에서는 sub-skill을 호출하지 않고 autorun이 직접 Read/Edit/Write로 in-place 패치**한다. Sub-skill 호출은 iteration 1에서만 발생한다.

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
   | **1** (기획) | `docs/planner/{NNN}-{slug}/feature-definition.md` 등 summary가 지목한 파일 | Edit으로 해당 섹션 수정. Stage 4(/sprint-init)는 **재호출 안 함** (이미 sprint dir 존재). Stage 5는 Direct Patch로 계속. |
   | **2** (UX) | `publish/{slug}/components/...` summary가 지목한 파일 | Edit으로 컴포넌트/스타일 수정. preview HTML 재생성은 변경 파일에 한정. |
   | **3** (청사진) | `docs/blueprints/{NNN}-{slug}/blueprint.md` | Edit으로 데이터 모델/API 명세 수정. data-standard 자동 적용 스킬은 그대로 발동. |
   | **5** (구현) | `src/...` 코드 파일 — summary가 지목한 모듈/메서드 | Edit으로 직접 코드 패치. coding-convention 자동 적용. `/generate-entity` **재호출 안 함** (테이블 정의 변동 없으면). |

5. 패치 후 재실행 단계:
   - 청사진/기획/UX 수정 시 → Stage 5(구현) 부분 재패치 → Stage 6(테스트 시나리오) 영향받은 케이스만 재생성 (역시 직접 Edit) → Stage 7(/test-run) **재호출** (이건 sub-skill이지만 idempotent)
   - 구현만 수정 시 → 곧바로 Stage 7 재호출
6. 변경된 파일 목록을 다음 iteration summary에 누적 (7.5.1 참조).

### 7.5.6 예외: Stage 6 테스트 시나리오 재호출 정책
`/test-scenario`는 idempotent하지 않을 수 있다. 따라서 재진입 시:
- 테스트 케이스 파일 중 summary가 지목한 것만 Edit으로 직접 수정
- 새로운 시나리오가 필요한 경우만 `/test-scenario` 재호출 (입력에 "추가 시나리오: {목록}" 명시)

`/test-run`은 idempotent하므로 매 iteration마다 그대로 호출한다.

## 단계 8: 최종 보고서 + `/pr-merge` 안내

### 8.1 파이프라인 실행 보고서 작성
`docs/sprints/sprint-{N}-{feature-slug}/pipeline-report.md`에 다음 작성:

```markdown
# ASTRA Autorun 자동 실행 보고서

**기능**: {feature-slug}
**실행 시각**: {timestamp}
**총 소요 시간**: {duration}
**최종 결과**: ✅ PASS (early exit) / ❌ FAIL (max iterations exhausted) / ⚠️ ABORT (env issue)
**iterations_used**: {final_iter}/{MAX_ITER}

## Iteration 요약 (자가 개선 루프)

| Iter | 결과 | 재진입 단계 | 분류 | 테스트 통과율 | Summary |
|---|---|---|---|---|---|
| 1 | ❌ FAIL | - | CODE_BUG | 12/15 | iterations/iter-1-summary.md |
| 2 | ❌ FAIL | Stage 5 | SPEC_GAP | 14/15 | iterations/iter-2-summary.md |
| 3 | ✅ PASS | Stage 3 | - | 15/15 | iterations/iter-3-summary.md |

## 마지막 iteration 단계별 결과

| 단계 | 결과 | 산출물 | 검증 결과 |
|---|---|---|---|
| 1. 기획 | ✅ / ⚠️ / ❌ | {경로} | planner-reviewer: {요약} |
| 2. UX 컴포넌트 | ✅ / ⚠️ / ❌ | {경로} | design-token: {요약} |
| 3. 청사진 | ✅ / ⚠️ / ❌ | {경로} | blueprint-reviewer: {요약} |
| 4. 스프린트 계획 | ✅ / ⚠️ / ❌ | {경로} | - |
| 5. 구현 | ✅ / ⚠️ / ❌ | {파일 N개} | coding-convention: {요약} |
| 6. 테스트 시나리오 | ✅ / ⚠️ / ❌ | {경로} | - |
| 7. 테스트 실행 | ✅ / ⚠️ / ❌ | {경로} | 통과: {N}/{M} |

## ⚠️ 주의 필요 항목 (P0 이슈)

{검증 단계에서 발견된 P0 이슈 목록 — 마지막 iteration 기준}

## 🚫 미해결 실패 (FAIL/ABORT 종료 시만)

- {분류}: {원인 요약}
- 마지막 시도: Stage {N} 재진입, 결과 {fail/abort}
- 권장 조치: {수동 디버그 / 환경 점검 / 청사진 재설계}

## 📋 다음 단계

1. 위 산출물을 검토하고 필요한 수정 사항을 적용하세요.
2. 수정 완료 후 `/pr-merge`를 실행하여 커밋·리뷰·머지 사이클을 진행하세요.
3. 관련 페르소나 분석이 필요하면 다음을 호출하세요:
   - 기획 검토: `Task(planner-reviewer)`
   - 디자인 검토: `Task(designer-persona)`
   - 개발 검토: `Task(developer-persona)`
   - 테스트 검토: `Task(tester-persona)`
```

### 8.2 사용자 안내 메시지 출력

```
═══════════════════════════════════════════════════════
{✅ / ❌ / ⚠️} ASTRA Autorun 자동 실행 완료

🔁 Iterations: {final_iter}/{MAX_ITER} ({early-exit on PASS / max reached / abort})

📁 산출물 위치:
  - 기획: docs/planner/{NNN}-{feature-slug}/
  - 청사진: docs/blueprints/{NNN}-{feature-slug}/
  - 스프린트: docs/sprints/sprint-{N}-{feature-slug}/
  - UI 컴포넌트: publish/{feature-slug}/
  - 테스트: docs/tests/test-cases/sprint-{N}-{feature-slug}/
  - Iteration 요약: docs/sprints/sprint-{N}-{feature-slug}/iterations/
  - 보고서: docs/sprints/sprint-{N}-{feature-slug}/pipeline-report.md

⚠️ P0 이슈: {N}건 (보고서 참조)
✅ 테스트: {통과}/{전체}

📋 다음 단계 (수동 실행 필요):
  → 산출물 검토 후 /pr-merge 실행

❗ /pr-merge는 자동 실행되지 않았습니다.
   수동 검토 후 명시적으로 실행하세요.
═══════════════════════════════════════════════════════
```

### 8.3 `/pr-merge` 절대 호출 금지
이 단계에서 **절대로 `/pr-merge`를 호출하지 않는다**. 사용자에게 안내만 한다.

## 실패 처리 정책

### 즉시 정지 조건 (Hard Stop — iteration 진입 전)
- Stage 1~6 중 산출물 파일 누락 (iteration 루프는 Stage 7 실패에만 적용)
- `/generate-entity` 또는 자동 적용 스킬이 명시적 오류 반환
- 분류 결과가 `ENV_ISSUE` (환경/인프라 문제는 iteration으로 해결 불가)

### Iteration 루프 진입 조건 (Stage 7 실패 시)
- `/test-run`이 5회 자동 디버그 후에도 실패 + `CURRENT_ITER < MAX_ITER`
  → 7.5의 분류·재진입 로직 실행
- `CURRENT_ITER == MAX_ITER`까지 도달하면 그 시점에서 정지 + Stage 8 보고서 작성

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

2. `docs/planner/{NNN}-{feature-slug}/` 6개 파일 모두 존재 → Stage 1 건너뛰기
3. `publish/{feature-slug}/` 존재 → Stage 2 건너뛰기
4. `docs/blueprints/{NNN}-{feature-slug}/blueprint.md` 존재 → Stage 3 건너뛰기
5. `docs/sprints/sprint-{N}-{feature-slug}/` 존재 → Stage 4 건너뛰기
6. 구현 산출물 감지 (모듈별 시그니처 파일 존재) → Stage 5 건너뛰기
7. `docs/tests/test-cases/sprint-{N}-{feature-slug}/` 존재 → Stage 6 건너뛰기

`MAX_ITER`는 재실행 시 처리:
- `--max-iter=N` 인자가 있으면 그 값을 그대로 사용 (Stage 0.5.1 규칙 준수, 프롬프트 안 함).
- 인자가 없으면 0.5.1과 동일하게 한 번 묻는다 (사용자가 한도를 늘려 재시도할 수 있도록).

이 동작을 사용자에게 출력으로 알린다:
```
🔄 재개 모드 감지
  - 이전 iteration: 2회 완료 (마지막: FAIL, CODE_BUG)
  - Stage 1~4: ✅ 건너뜀
  - Stage 5 (구현): ⏳ Iteration 3 재개 시작 (target: Stage 5)
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
| `/service-planner` | Stage 1에서 호출 (디폴트 자동 적용) |
| `/ux-publish` | Stage 2에서 호출 |
| `/handoff-publish` | **호출 안 함** (선택적 산출물, 사용자 명시 시만) |
| `/sprint-init` | Stage 4에서 호출 |
| `/generate-entity` | Stage 5에서 호출 (청사진 데이터 모델 기반 엔티티 생성) |
| `/test-scenario` | Stage 6에서 호출 |
| `/test-run` | Stage 7에서 호출 (반복마다 재호출, 최대 MAX_ITER회) |
| `tester-persona` | Stage 7.5의 *AMBIGUOUS* 분기에서만 호출 (실패 분류) |
| `/pr-merge` | **절대 호출 금지** — 안내만 출력 |
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
