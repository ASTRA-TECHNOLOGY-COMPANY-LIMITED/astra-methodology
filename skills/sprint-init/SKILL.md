---
name: sprint-init
description: "Initializes a new ASTRA sprint. Creates an isolated sprint worktree (with port-isolated dev server settings), generates sprint prompt maps, progress trackers, and retrospective templates inside that worktree, and prints the cd path so all subsequent development and testing happens in the worktree. With --auto flag, also auto-executes the post-scaffolding pipeline: /test-scenario → implementation → /test-run → /pr-merge --auto (worktree auto-removed). Between each major stage (5.2/5.3/5.4/5.5 iteration/5.6), the skill performs a silent save (auto-state.yaml + commit) and applies a 'reference-avoidance' rule (don't re-read large prior artifacts; rely on yaml SSoT) so the system's built-in auto-compression keeps context manageable, then continues directly to the next stage without user intervention. --resume flag is reserved for true recovery (context crash, forced interrupt) — it reads auto-state.yaml and jumps to next_stage. Only halts on true blockers (gh auth, merge conflicts, Critical review issues)."
argument-hint: "[sprint-number] [sprint-name] [--auto] [--max-iter=N] [--resume]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Skill, Agent, TodoWrite
---

# ASTRA Sprint Initialization (v5.0+)

Creates a sprint-level isolated worktree, writes port-isolated env settings, and generates prompt maps / progress trackers / retrospective templates **inside that worktree**.

> **v5.0+ 정책**: sprint당 단일 worktree(`.astra-worktrees/sprint-<N>-<name>/`)에서 모든 feature 작업·테스트가 진행된다. 머지는 `/pr-merge`가 dev로 반영하고 worktree를 자동 제거한다. 트레이드오프: sprint당 PR 1개 — feature별 리뷰 granularity는 없지만 sprint 단위로 깔끔히 머지/롤백된다.

## Execution Procedure

### Step 0.A: Resume Detection (`--resume` 플래그)

**언제 쓰나**: `--resume`은 **진짜 복구용**이다. `--auto` 모드는 평상시 중간에 끊기지 않고 stage 사이에서 silent save(`auto-state.yaml` + commit)만 하면서 자동으로 다음 stage로 진행한다. 다음 경우에만 사용자가 명시적으로 `/sprint-init --resume`을 호출해 재개한다:

1. 시스템 자동 컨텍스트 압축 후 LLM이 in-flight 변수를 잃어 진행이 멈춘 경우
2. 사용자가 의도적으로 중간에 중단했다가 다시 이어가는 경우
3. 크래시·세션 종료 등으로 skill 실행이 비정상 종료된 경우

`auto-state.yaml`이 단일 진실 출처(SSoT)이므로, 위 어떤 경우든 yaml에서 `next_stage`를 읽어 정확히 그 지점부터 재개한다.

`$ARGUMENTS`에서 `--resume` 플래그를 우선 파싱한다:

```bash
RESUME_MODE=0
for arg in $ARGUMENTS; do
  if [ "$arg" = "--resume" ]; then
    RESUME_MODE=1
    break
  fi
done
```

#### `--resume` 모드 동작
`RESUME_MODE=1`이면:

1. **메인 worktree에서 호출된 케이스**: `docs/sprints/sprint-*/auto-state.yaml`을 글롭하여 `merge.merge_success != true`인 항목을 추린 뒤, **sprint 번호 N이 가장 큰 것**을 "가장 최신"으로 채택한다 (디렉토리명 `sprint-{N}-...`의 N 비교). 그 항목의 `sprint.worktree_path`로 cd 후 단계를 이어간다. worktree가 이미 제거된 상태면(머지 후 yaml만 dev에 남아 있는 케이스) 에러 출력 후 abort — `--resume`은 진행 중인 worktree가 살아 있을 때만 의미가 있다.
2. **sprint worktree 안에서 호출된 케이스**: 현재 디렉토리의 `docs/sprints/sprint-{N}-{name}/auto-state.yaml`을 읽는다 (없으면 abort).
3. `auto-state.yaml`을 읽어 다음 변수를 모두 복원한다:
   - `SPRINT_N`, `SPRINT_NAME`, `WT_PATH`, `MAX_ITER`, `CURRENT_ITER`
   - `progress.next_stage`, `progress.last_iteration_summary`, `files_to_patch_next`
   - 기타 stage별 산출물 경로
4. **Step 0~4 (worktree 생성·scaffolding)를 모두 건너뛴다** — 이미 존재한다.
5. **`progress.next_stage`로 직접 점프**한다. 예: `next_stage: 5.4`면 Step 5.4를 바로 실행.
6. 시작 안내:
   ```
   🔄 sprint-init --resume 재개
      Sprint: sprint-{N}-{name}
      Worktree: {WT_PATH}
      이전 완료: {completed_stages}
      재개 단계: Stage {next_stage} — {next_stage_description}
      Iteration: {current_iter}/{max_iter}
   ```

`RESUME_MODE=0`이면 정상 Step 0.B로 진행.

### Step 0.B: Main Worktree Guard (신규 sprint만)

Sprint worktree를 *생성*하는 명령이므로 메인 worktree에서만 실행한다. 이미 격리 worktree 안이면 거부:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
if [ -z "$PLUGIN_ROOT" ] || [ ! -f "$PLUGIN_ROOT/scripts/worktree-helpers.sh" ]; then
  echo "ERROR: CLAUDE_PLUGIN_ROOT를 찾을 수 없습니다. 플러그인 캐시 경로를 확인하세요." >&2
  exit 1
fi
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"
astra_ensure_main_worktree || exit 1
```

### Step 1: Confirm Sprint Number, Sprint Name, and Mode

Parse from `$ARGUMENTS`:
- **Sprint number** (optional): If not provided, scan existing directories in `docs/sprints/` matching the `sprint-{N}-{name}/` pattern (e.g., `sprint-1-auth/`, `sprint-2-workspace/`) to determine the next number.
- **Sprint name** (optional): The primary blueprint/feature name for this sprint.
- **`--auto`** (optional flag): If present, set `AUTO_MODE=1` and proceed to Step 5 (Auto Continue) after scaffolding. Without this flag, the skill stops at Step 4 (Output Sprint Planning Guide) as before.
- **`--max-iter=N`** (optional, only meaningful with `--auto`): max self-improving iteration count for the test loop (1 ≤ N ≤ 10). If `--auto` is set but `--max-iter` is missing, ask the user **once** via `AskUserQuestion` (default 3).

**Directory name format**: `sprint-{N}-{sprint-name}/` (e.g., `sprint-1-auth/`, `sprint-2-payment/`, `sprint-3-dashboard/`)

If the sprint name is not provided in `$ARGUMENTS`, ask the user for the primary feature/blueprint name. This name will be used as the directory suffix. Use kebab-case format (e.g., `auth`, `workspace`, `payment-dashboard`).

When scanning existing directories, extract the sprint number from directory names matching pattern `sprint-{N}-{name}` (e.g., `sprint-1-auth` → number `1`).

### Step 1.5: Sync `dev` Branch

Sprint worktree는 `origin/dev`(없으면 `origin/main`)를 base로 분기한다. 메인 worktree를 먼저 `dev`로 정렬해 두면 base가 항상 최신 상태가 된다.

1. **Check current branch**: `git branch --show-current`
2. **Preserve uncommitted changes**: `git status --porcelain`에 변경이 있으면 `git stash --include-untracked -m "astra-sprint-init"`로 보관
3. **Switch and pull**: `git fetch origin dev && git checkout dev && git pull origin dev` (`dev`가 없으면 `main`/`master`로 폴백, 그것도 없으면 현재 브랜치 유지)
4. **Restore stash**: 2단계에서 stash 했으면 `git stash pop`. 충돌 시 사용자에 보고하고 중단.

### Step 1.6: Create Sprint Worktree

`feat/sprint-{N}-{sprint-name}` 브랜치로 새 격리 worktree를 생성한다. 이 안에서 모든 feature 코드와 테스트 산출물이 작성된다.

```bash
SPRINT_N="{확정된 sprint 번호}"
SPRINT_NAME="{확정된 sprint 이름}"

if ! out=$(astra_create_sprint_worktree "$SPRINT_N" "$SPRINT_NAME"); then
  echo "ERROR: sprint worktree 생성 실패" >&2
  exit 1
fi
IFS=$'\t' read -r SPRINT_BRANCH WT_PATH <<< "$out"
if [ -z "$WT_PATH" ] || [ ! -d "$WT_PATH" ]; then
  echo "ERROR: sprint worktree 경로를 확정할 수 없습니다. 헬퍼 출력: '$out'" >&2
  exit 1
fi
```

`astra_create_sprint_worktree`가 브랜치/슬러그/포트 충돌을 모두 흡수하므로 반환된 `$SPRINT_BRANCH`·`$WT_PATH`를 *그대로* 사용한다 (희망 이름과 다를 수 있음).

### Step 1.7: Write Worktree Port Env File

worktree 안에 `.astra-worktree.env`를 생성한다. `/test-run`이 서버 기동 전 이 파일을 source 해 sprint 전용 포트를 적용한다.

```bash
# 기본 포트 베이스: 3000 (Node 기반 기본값). 다른 스택은 env 파일 내 변환식이 자동 적용.
PORT_BASE_DEFAULT=3000
if ! PORT_BASE=$(astra_compute_port_base "$PORT_BASE_DEFAULT" "$SPRINT_N"); then
  echo "ERROR: 사용 가능한 포트 베이스를 찾지 못했습니다" >&2
  exit 1
fi

astra_write_worktree_env "$WT_PATH" "$SPRINT_N" "$SPRINT_NAME" "$PORT_BASE" || exit 1
echo "Sprint 포트 베이스: $PORT_BASE (offset=$((PORT_BASE - PORT_BASE_DEFAULT)))"
```

생성된 파일에는 `ASTRA_PORT_BASE`, `PORT`, `VITE_PORT`, `SERVER_PORT`, `DJANGO_PORT`, `FASTAPI_PORT` 등 프레임워크별 값이 포함된다. `/test-run`은 감지한 스택에 맞는 값을 선택해 서버를 띄운다.

### Step 1.8: Move into Sprint Worktree

이후 산출물 작성·진행 추적은 모두 worktree 안에서 수행한다:

```bash
cd "$WT_PATH"
```

> 이 시점부터 "현재 작업 디렉토리"는 `$WT_PATH`이며, 모든 docs/sprints/* 파일은 sprint 브랜치에 커밋된다.

### Step 2: Create Sprint Prompt Map

`$WT_PATH/docs/sprints/sprint-{N}-{sprint-name}/prompt-map.md` 파일을 생성한다.

Scan `docs/blueprints/` for numbered directories matching the sprint name (or use the blueprint names provided by the user). Each blueprint becomes a feature in the prompt map. Do NOT analyze or carry over items from previous sprints.

```markdown
# Sprint {N} Prompt Map

## Sprint Goal
[Describe the business value to achieve in this sprint]

> **Worktree 안내**: 이 sprint의 모든 작업은 `.astra-worktrees/sprint-{N}-{sprint-name}/` 안에서 진행됩니다.
> 새 Claude Code 세션은 반드시 그 경로에서 시작하세요.

## Feature 1: {feature-name}

### 1.1 Blueprint Prompt
/blueprint {feature-name} --from-planner=docs/planner/{NNN}-{feature-name}

> `/blueprint` 스킬은 `/service-planner` 산출물(있으면 자동 로드)을 입력으로 10개 표준 섹션의 청사진을 `docs/blueprints/{NNN}-{feature-name}/blueprint.md`에 작성합니다.
> - **포함**: 데이터 플로우, 스키마 DDL, ER 다이어그램, API JSON Schema, 시퀀스 다이어그램, 의사코드 로직, HITL Triggers
> - **제외**: 실행 가능한 구현 코드, ORM 어노테이션, 프레임워크 종속 표현
> - PK 전략·트랜잭션 경계·외부 의존성 동기성처럼 사람 결정이 필요한 1-3개 항목만 자동으로 물어봅니다.
>
> **Numbering Rule**: Scan existing directories in `docs/blueprints/` to determine the next number. Use 3-digit zero-padded format (e.g., `001-`, `002-`).

### 1.2 DB Design Reflection Prompt
/feature-dev "Refer to docs/blueprints/{NNN}-{feature-name}/blueprint.md Section 3 (데이터 모델) and reflect those tables/columns/indexes/FK relationships into docs/database/database-design.md, including the ERD and FK relationship summary.

The blueprint is the single source of truth — do not change schema decisions, do not add columns not in the blueprint, do not rename. If you find a real inconsistency, stop and report instead of guessing.

HITL Guard: Before asking the user any question, first check Section 10 (HITL Triggers) of the blueprint. Only ask the user when the decision matches T1-T4 triggers (business decisions without a clear answer in the blueprint, security/permission choices, external dependency choices, destructive changes). For everything else, follow the blueprint and proceed automatically.

Do not modify any application code yet."

### 1.3 Test Case Prompt
/feature-dev "Based on docs/blueprints/{NNN}-{feature-name}/blueprint.md Section 9 (테스트 전략) and Section 9.1 (필수 테스트 케이스), write test cases to docs/tests/test-cases/sprint-{N}/{feature-name}-test-cases.md.

Use Given-When-Then format. Cover: (a) Section 5.1 happy path, (b) Section 5.2 exception paths, (c) Section 2.3 business rules, (d) Section 7 error policy items. Include unit, integration, and edge cases.

HITL Guard: Section 10 (HITL Triggers) of the blueprint defines when to ask the user. Outside those triggers, derive test cases directly from the blueprint without asking. If a test case requires a decision not in the blueprint and not in Section 10, default to the most conservative coverage and note it as TODO instead of pausing.

Do not modify any application code yet."

### 1.4 Implementation Prompt
/feature-dev "Strictly follow docs/blueprints/{NNN}-{feature-name}/blueprint.md and docs/database/database-design.md to implement the feature. Write code that matches: Section 3 (DDL → ORM entities), Section 4 (API contract → controllers/DTOs), Section 5 (sequence diagrams → service orchestration), Section 6 (pseudocode → real implementation), Section 7 (error policy → exception handlers), Section 8 (non-functional → middleware/security config).

Write tests referencing docs/tests/test-cases/sprint-{N}/{feature-name}-test-cases.md. Once implementation is complete, run all tests and report results to docs/tests/test-reports/.

HITL Guard (중요): The blueprint's Section 10 (HITL Triggers) tells you exactly when to ask the user during implementation. The four triggers are T1 (business decisions without a clear blueprint answer), T2 (security/permission policy choices), T3 (external dependency/3rd-party introduction), T4 (destructive changes like DROP/RENAME or public API signature change). Outside those triggers, do not ask — apply the blueprint as written and follow coding conventions.

Specifically do NOT ask the user about: variable/function names, code formatting, log levels, file layout, import order, DTO/Entity split, fine-grained HTTP status codes — those follow project conventions automatically. Waking the user too often defeats the automation."

## Feature 2: {feature-name}
{Repeat with the same structure as above}

---

## Sprint 종료 시 (모든 feature 구현 완료 후)

### Z.1 Integration Test
/test-run

> `.astra-worktree.env`의 sprint 전용 포트로 서버를 띄우고 테스트를 수행합니다.
> 테스트 종료 시 해당 포트의 서버 프로세스도 자동으로 정리됩니다.

### Z.2 Merge to dev
/pr-merge

> sprint 브랜치를 dev로 머지하고 worktree를 제거합니다. 사용자는 메인 worktree(dev)로 자동 복귀합니다.
```

### Step 2.5: Create Sprint Progress Tracker

Read the prompt map created in Step 2 (`docs/sprints/sprint-{N}-{sprint-name}/prompt-map.md`) and extract feature names from `## Feature {#}: {name}` headers (where `{#}` is the feature ordinal, e.g., 1, 2, 3).

Create the `docs/sprints/sprint-{N}-{sprint-name}/progress.md` file:

```markdown
# Sprint {N} Progress Tracker

## Sprint Information
- **Sprint Number**: {N}
- **Sprint Name**: {sprint-name}
- **Sprint Branch**: feat/sprint-{N}-{sprint-name}
- **Worktree**: .astra-worktrees/sprint-{N}-{sprint-name}/
- **Port Base**: {PORT_BASE}
- **Sprint Goal**: [copy from prompt map Sprint Goal section]
- **Start Date**: {YYYY-MM-DD}
- **End Date**: {YYYY-MM-DD} (+7 days)
- **Status**: In Progress

<!-- PROGRESS_TABLE_START -->
## Feature Progress

| Feature | Blueprint | DB Design | Test Cases | Implementation | Test Report | Status |
|---------|-----------|-----------|------------|----------------|-------------|--------|
| {feature-1} | - | - | - | - | - | Not Started |
| {feature-2} | - | - | - | - | - | Not Started |

**Legend**: `-` Not Started, `WIP` In Progress, `Done` Completed, `N/A` Not Applicable
<!-- PROGRESS_TABLE_END -->

<!-- SUMMARY_START -->
## Summary
- **Total Features**: {N}
- **Completed**: 0
- **In Progress**: 0
- **Overall Progress**: 0%
- **Last Updated**: {YYYY-MM-DD HH:MM}
<!-- SUMMARY_END -->

<!-- ACTIVITY_LOG_START -->
## Activity Log

| Timestamp | Event | File | Details |
|-----------|-------|------|---------|
<!-- ACTIVITY_LOG_END -->
```

- All features start as `-` (Not Started) in every column.

### Step 3: Create Retrospective Template

Create the `docs/sprints/sprint-{N}-{sprint-name}/retrospective.md` file:

```markdown
# Sprint {N} Retrospective

## Date: {YYYY-MM-DD}

## AI Analysis Data
- code-review recurring issues: [auto-collected]
- security-guidance blocked count: [auto-collected]
- astra-methodology violation frequency: [auto-collected]

## Team Discussion (areas AI cannot catch)

### What went well (Keep)
-

### What to improve (Problem)
-

### What to try (Try)
-

## Automated Improvement Actions
- /hookify [codify recurring mistakes found in this sprint]
- CLAUDE.md update content: [describe added rules]
```

### Step 3.5: Commit Sprint Scaffolding

생성된 sprint 문서 3종(`prompt-map.md`, `progress.md`, `retrospective.md`)을 sprint 브랜치에 커밋한다. 이후 feature 작업 커밋과 분리되어 머지 시 추적이 쉽다.

```bash
git add "docs/sprints/sprint-${SPRINT_N}-${SPRINT_NAME}/"
git commit -m "chore: scaffold sprint ${SPRINT_N} (${SPRINT_NAME})"
```

원격 push는 하지 않는다 — 첫 feature 커밋 또는 `/pr-merge` 시점에 함께 push 된다.

### Step 4: Output Sprint Planning Guide

```
## Sprint {N} Initialization Complete

### Worktree
- 경로: {WT_PATH}
- 브랜치: {SPRINT_BRANCH}
- 포트 베이스: {PORT_BASE}
- env 파일: {WT_PATH}/.astra-worktree.env

### Generated Files (in worktree)
- docs/sprints/sprint-{N}-{sprint-name}/prompt-map.md (prompt map)
- docs/sprints/sprint-{N}-{sprint-name}/progress.md (progress tracker)
- docs/sprints/sprint-{N}-{sprint-name}/retrospective.md (retrospective template)

### Next Steps
1. cd {WT_PATH}
2. 위 prompt-map의 Feature 1.1 ~ 1.4를 순서대로 실행 (디자인 → DB → 테스트 → 구현)
3. 모든 feature 완료 후: /test-run → /pr-merge

> **다중 세션 안내**: 새 Claude Code 세션은 반드시 {WT_PATH}에서 시작하세요.
> 메인 worktree(dev)에는 다른 sprint 작업이 진행 중일 수 있습니다.

### Sprint Planning Procedure (1 hour, run inside worktree)
1. (10 min) Review AI analysis report
2. (20 min) Confirm business priorities with DE and agree on sprint goal
3. (20 min) Discuss prompt design direction per item + DSA shares design direction
4. (10 min) Finalize sprint backlog
```

> **분기**: `--auto` 플래그가 없으면 여기서 종료. `--auto`가 있으면 **Step 5**로 진행한다.

---

### Step 5: Auto Continue (only if `--auto` flag is set)

scaffolding 완료 후 무인 모드로 다음 파이프라인을 순차 실행한다:

```
/test-scenario all → 구현(blueprint 기반) → /test-run → (실패 시 자가 개선 루프) → /pr-merge --auto → worktree 자동 제거
```

**기본 원칙** (autorun과 동일):
- 파이프라인 중에는 `AskUserQuestion`을 호출하지 않는다 (Step 1에서 `--max-iter` 미입력 시 1회만 예외).
- 각 단계의 성공 기준은 *검증 가능한 파일/테스트 결과*로만 판정한다.
- 진짜 차단(gh 인증·머지 충돌·Critical 리뷰 이슈)에서만 HITL이 발동된다.

#### Step 5.0: 사전 검증

1. **현재 worktree가 sprint worktree인지 확인**: 이미 Step 1.6/1.8에서 worktree 생성 후 cd 했으므로 `$(pwd)`가 `$WT_PATH`와 동일해야 한다. 다르면 abort.
2. **Blueprint 존재 확인**: prompt-map.md에서 추출한 각 feature에 대해 `docs/blueprints/[0-9][0-9][0-9]-{feature-name}/blueprint.md`가 worktree 안(또는 머지된 base 브랜치)에 존재해야 한다.
   - 누락 시 abort 메시지:
     ```
     ❌ --auto 모드는 blueprint 사전 작성을 요구합니다.
        누락된 blueprint: {feature-name}
        해결: /service-planner {feature-name} 또는 /feature-dev로 blueprint 작성 후 재실행.
     ```
3. **MAX_ITER 결정**: `--max-iter=N` 인자 사용. 없으면 `AskUserQuestion` 1회로 입력받음 (1/3/5 옵션, 기본 3).

#### Step 5.1: 진행 추적 초기화

`TodoWrite`로 todos 생성:
1. Step 5.2: 테스트 시나리오 생성
2. Step 5.3: 구현 (각 feature)
3. Step 5.4: 통합 테스트 실행
4. Step 5.5: 자가 개선 루프 (실패 시)
5. Step 5.6: /pr-merge --auto 실행
6. Step 5.7: 최종 보고서

Iteration 추적 변수:
- `MAX_ITER` = 위에서 결정된 N
- `CURRENT_ITER` = 1
- `ITER_DIR` = `docs/sprints/sprint-{N}-{sprint-name}/iterations/`
- `mkdir -p "$ITER_DIR"`

#### Step 5.1.5: Silent Save Protocol (재사용 가능한 공통 패턴)

`--auto` 모드는 stage마다 다량의 컨텍스트(파일 내용, 테스트 로그, 코드 리뷰 출력)를 누적한다. **각 major stage 종료 시 상태를 yaml에 영속화한 뒤, "참조 회피 규칙"을 적용한 채 곧바로 다음 stage로 진행**한다. 사용자 개입은 없다.

수동 `/compact` 슬래시 명령은 의도적으로 사용하지 않는다 — Claude Code의 시스템 자동 압축이 컨텍스트 한계에 근접하면 알아서 작동하고, 그 사이 LLM은 큰 객체 재참조를 회피해 신규 토큰 누적을 최소화한다.

이 프로토콜은 Step 5.2 종료, 5.3 종료, 5.4 종료, 5.5 iteration 종료, 5.6 종료 시점에 호출된다.

##### 5.1.5.A 체크포인트 파일 작성

각 stage 종료 시 `$WT_PATH/docs/sprints/sprint-{N}-{sprint-name}/auto-state.yaml`을 갱신한다:

```yaml
# auto-state.yaml — sprint-init --auto 재개용 SSoT
sprint:
  number: {N}
  name: {sprint-name}
  worktree_path: {WT_PATH}
  branch: feat/sprint-{N}-{sprint-name}
  port_base: {PORT_BASE}

iteration:
  max_iter: {MAX_ITER}
  current_iter: {CURRENT_ITER}

progress:
  completed_stages: [5.0, 5.1, 5.2, ...]   # 지금까지 끝난 stage 번호 목록
  next_stage: 5.3                           # 재개 시 점프할 단계
  next_stage_description: "구현 (Iteration 1만)"

features:
  - name: {feature-name-1}
    blueprint: docs/blueprints/{NNN}-{feature-name-1}/blueprint.md
    status: pending | done | in-progress

scenarios:
  generated_dir: docs/tests/test-cases/sprint-{N}-{sprint-name}/
  files: [auth-test-cases.md, payment-test-cases.md, ...]   # 5.2 완료 후 채움

implementation:
  entities_created: [User.java, Payment.java, ...]
  services_created: [...]
  controllers_created: [...]

last_test_result:
  passed: {N}
  total: {M}
  failed_tests: []
  log_excerpt: "..."   # 마지막 실패 로그 핵심 100줄 이내

last_iteration_classification: null | CODE_BUG | SPEC_GAP | DESIGN_MISALIGN | ENV_ISSUE
files_to_patch_next: []   # iteration 2+ 진입 시 사용 (summary가 지목한 src/ 파일들)

merge:
  pr_url: null
  merge_success: null
  worktree_removed: null
```

##### 5.1.5.B 체크포인트 파일 커밋 (필수)

상태 파일을 sprint 브랜치에 커밋한다. **이 단계를 빠뜨리면** 다음 케이스에서 파일이 사라진다:
- 5.6.A 직후 `/pr-merge --auto`의 `git add -u`는 *추적 중인* 파일만 스테이징한다 → untracked `auto-state.yaml`은 머지에 포함 안 됨 → worktree 제거 시 함께 사라짐.
- `--resume`이 메인 worktree에서 yaml을 찾을 때, 머지된 dev에 yaml이 있어야 함.

```bash
git add "docs/sprints/sprint-${SPRINT_N}-${SPRINT_NAME}/auto-state.yaml"
git commit -m "chore: auto-state checkpoint after Stage ${X}"
```

> `--auto` 진행 중 발생하는 커밋이므로 메시지는 자동 생성. push는 `/pr-merge --auto` 또는 다음 checkpoint에서 일괄 처리되므로 여기서는 생략 가능 (단, 만약 사용자가 중간에 다른 머신에서 `--resume`하려면 push 필요).

##### 5.1.5.C 참조 회피 규칙 적용 후 다음 stage 자동 진행

체크포인트 작성·커밋 직후 다음 한 줄을 가볍게 출력하고 **곧바로 다음 stage를 호출**한다. exit 하지 않는다:

```
✅ Stage {X} 완료 → Stage {Y} 자동 진행 (상태: docs/sprints/sprint-{N}-{sprint-name}/auto-state.yaml)
```

그리고 다음 stage 진입 직전에 **반드시 다음 컨텍스트 효율 규칙을 LLM 스스로에게 적용**한다:

> ⚡ **컨텍스트 효율 규칙 (자동 진행 중 매 stage 전환점)**
> - 이전 stage에서 로딩한 대형 객체(테스트 로그 전체, 브라우저 스냅샷, 이전 구현 파일의 전체 내용)을 **재참조하지 않는다**.
> - 단일 진실 출처(SSoT): `auto-state.yaml` (+ iteration 재개 시 `last_iteration_summary` 파일).
> - 다음 stage에서 필요한 파일은 **선택적으로** Read/Edit 한다 — 전체 디렉토리 트리·전체 청사진을 다시 읽지 않는다.
> - 이렇게 하면 Claude Code의 시스템 자동 압축(컨텍스트 한계 근접 시 작동)이 효과적으로 동작해 mid-skill 토큰 폭발을 막는다.

##### 5.1.5.D `--resume` 모드 (진짜 복구 전용)

평상 흐름에서 `--resume`은 호출되지 않는다. 다음 비정상 경로에서만 사용한다 (Step 0.A 참조):

- 시스템 자동 압축 후 LLM이 in-flight 변수를 잃어 다음 stage를 자동 호출하지 못한 경우
- 사용자가 의도적으로 중간에 정지했다가 다시 이어가는 경우
- 크래시·세션 종료로 skill 실행이 비정상 종료된 경우

핵심:
1. `auto-state.yaml`이 SSoT — 컨텍스트 압축으로 변수가 휘발되었어도 이 파일에서 모두 복원 가능
2. `progress.next_stage`로 직접 점프
3. iteration 재개 시 `last_iteration_summary` 파일과 `files_to_patch_next` 목록만 추가로 로딩

##### 5.1.5.E 멱등성

`auto-state.yaml`은 매 체크포인트마다 *완전히 덮어쓴다*. partial update 금지 — 부분 갱신은 stage 간 정합성을 깨뜨릴 수 있다. 항상 최신 상태 스냅샷을 통째로 쓴다.

매 checkpoint마다 새 git commit이 생긴다 (`chore: auto-state checkpoint after Stage X`). PR이 머지될 때 이 commit들은 squash 또는 그대로 머지된다 (사용자 git workflow에 따라).

> **참고**: 이 프로토콜은 `--auto` 모드 전용이다. `--auto` 없이 sprint-init만 실행하는 흐름은 영향받지 않는다.

#### Step 5.2: 테스트 시나리오 생성 (Iteration 1만)

`Skill('test-scenario', 'all')`을 호출한다. 모든 feature에 대해 `docs/tests/test-cases/sprint-{N}-{sprint-name}/`에 시나리오가 생성된다.

성공 기준: 시나리오 파일 ≥ 1개 존재.

##### 5.2.Z 💾 Silent Save

Step 5.2 종료 직후 **Step 5.1.5의 Silent Save Protocol을 실행**한다:
- `auto-state.yaml`에 `completed_stages: [5.0, 5.1, 5.2]`, `next_stage: 5.3`, `scenarios.files: [...]` 기록 + commit
- 5.1.5.C의 참조 회피 규칙 적용 (테스트 시나리오 생성 과정에서 로딩한 청사진 전체 내용은 더 이상 재참조하지 않음)
- **곧바로 Step 5.3 자동 진행** — exit/사용자 입력 대기 없음

#### Step 5.3: 구현 (Iteration 1만)

prompt-map.md에서 추출한 각 feature에 대해 순차 실행:

1. blueprint.md를 읽고 **데이터 모델 섹션**에서 테이블 정의 추출
2. 각 테이블에 대해 `Skill('generate-entity', '{table-name}')` 호출 (또는 청사진 기반 직접 entity 작성)
3. **API 명세 섹션**에 따라 service/controller/repository 레이어 작성
4. 자동 적용 스킬(`coding-convention`, `data-standard`, `code-standard`)은 매 Write/Edit마다 발동된다.

성공 기준: 청사진의 모든 테이블 정의·API 엔드포인트가 `src/` (또는 프로젝트 표준 위치) 코드로 반영됨.

##### 5.3.Z 💾 Silent Save

Step 5.3은 가장 많은 컨텍스트(다수의 entity·service·controller 생성)를 누적하는 단계다. **반드시 5.1.5 Silent Save Protocol을 실행**한다:
- `auto-state.yaml`에 `completed_stages: [..., 5.3]`, `next_stage: 5.4`, `implementation.{entities/services/controllers}_created: [...]` 기록 + commit
- 5.1.5.C의 참조 회피 규칙 적용 (방금 생성한 entity/service/controller 파일 전체 내용은 더 이상 재참조하지 않음 — 다음 stage는 테스트 실행이고 파일 경로만 알면 됨)
- **곧바로 Step 5.4 자동 진행** — exit/사용자 입력 대기 없음

#### Step 5.4: 통합 테스트 실행

`Skill('test-run', '')` 호출. `.astra-worktree.env`의 sprint 전용 포트로 서버 기동, 테스트 수행, 종료 시 자동 포트 정리.

##### 5.4.Z 💾 Silent Save

`/test-run`은 브라우저 스냅샷·콘솔 로그·네트워크 요청 로그 등 큰 결과물을 컨텍스트에 누적한다. **반드시 5.1.5 Silent Save Protocol을 실행**한다:
- `auto-state.yaml`에 `completed_stages: [..., 5.4]`, `last_test_result: { passed, total, failed_tests, log_excerpt }` 기록 + commit
  - 테스트 통과 시 → `next_stage: 5.6`
  - 테스트 실패 + `CURRENT_ITER < MAX_ITER` → `next_stage: 5.5`
  - 테스트 실패 + `CURRENT_ITER == MAX_ITER` → `next_stage: 5.7` (보고서 직진)
- `log_excerpt`는 마지막 실패 로그 핵심 100줄 이내로 축약 (전체 로그를 yaml에 박지 말 것)
- 5.1.5.C의 참조 회피 규칙 적용 (브라우저 스냅샷·전체 콘솔 로그·네트워크 요청은 더 이상 재참조하지 않음 — yaml의 `log_excerpt`만 들고 다음 stage 진행)
- **곧바로 `next_stage`로 자동 점프** — exit/사용자 입력 대기 없음

#### Step 5.5: 자가 개선 루프 (테스트 실패 시)

**모든 테스트 통과** → Step 5.6으로 즉시 진행 (early exit).

**실패** + `CURRENT_ITER < MAX_ITER`:

1. **실패 분류** (autorun Stage 7.5.4와 동일한 패턴 매칭 + 폴백 시 `tester-persona` 위임):
   | 신호 | 분류 | 재진입 |
   |------|------|--------|
   | TypeError, NullPointer, panic, stack trace에 `src/` | `CODE_BUG` | Direct Patch (src/ 파일 Edit, sub-skill 재호출 금지) |
   | 404 Not Found, schema mismatch, 청사진에 없는 동작 요구 | `SPEC_GAP` | **abort** (blueprint 수정 필요) |
   | screenshot diff, aria-label, contrast 등 UI 실패 | `DESIGN_MISALIGN` | **abort** (UX 수정 필요) |
   | ECONNREFUSED, port in use, db connection | `ENV_ISSUE` | **abort** (사용자 개입) |

2. **Direct Patch** (sub-skill 재호출 금지 — autorun Stage 7.5.5와 동일 원칙):
   - `CODE_BUG` 케이스: summary가 지목한 `src/` 파일을 Edit으로 직접 수정. 새 entity 생성 등 sub-skill 재호출 금지.
   - 다른 분류는 abort.

3. **Abort 시 명확한 안내 메시지**:
   ```
   ❌ {분류} 분류 — sprint-init --auto는 이 카테고리를 자가 개선하지 않습니다.

   {SPEC_GAP일 때}:
     blueprint 수정이 필요합니다. sprint-init은 blueprint를 다시 그리지 않습니다.
     해결책 2가지:
       (1) docs/blueprints/{NNN}-{feature}/blueprint.md 수동 수정 후 /pr-merge --auto
       (2) /autorun "{기능 설명}" --max-iter=N — blueprint도 자동 패치하는 풀 파이프라인

   {DESIGN_MISALIGN일 때}:
     HTML 기획화면(styles.css, SCR-*.html) 수정이 필요합니다.
     해결책: /service-planner 재실행 후 /pr-merge --auto, 또는 /autorun 풀 파이프라인.

   {ENV_ISSUE일 때}:
     환경/인프라 문제 — 사용자 진단이 필요합니다.
     로그: {로그 위치}
   ```

3. **Iteration 요약 작성**: `$ITER_DIR/iter-{CURRENT_ITER}-summary.md` (200줄 이내, autorun과 동일 형식).

4. `CURRENT_ITER += 1`.

##### 5.5.Z 💾 Silent Save (iteration 사이마다 실행)

**Iteration 간 컨텍스트 정리는 필수**다. 디버그 로그·이전 코드 패치 시도·classification 분석 등이 누적되어 다음 iteration이 토큰 한도에 일찍 도달할 위험이 크다. **반드시 5.1.5 Silent Save Protocol을 실행**한다:
- `auto-state.yaml`에 `current_iter: {CURRENT_ITER}`, `last_iteration_classification: {분류}`, `files_to_patch_next: [{summary가 지목한 src/ 파일 경로 목록}]`, `next_stage: 5.5` (또는 5.4 — 재시도 흐름)으로 기록 + commit
- iteration summary 경로(`$ITER_DIR/iter-{CURRENT_ITER-1}-summary.md`)도 `auto-state.yaml`의 `progress.last_iteration_summary` 필드에 기록 (다음 iteration 재개 시 *오직 이 summary 파일만* 읽도록)
- 5.1.5.C의 참조 회피 규칙을 **엄격히 적용** — 이전 iteration의 디버그 로그·classification 분석·시도된 패치 diff는 더 이상 재참조하지 않음. summary 파일과 `files_to_patch_next`만 들고 다음 iteration 진입.
- **곧바로 재개**: summary 파일을 먼저 읽고 `files_to_patch_next` 파일들을 Direct Patch → 5.4(test-run) 재호출 — exit/사용자 입력 대기 없음

> **컨텍스트 효율 규칙 (iteration 재진입 시)**: `auto-state.yaml`과 `last_iteration_summary` 파일만 읽고 patch 대상 파일을 Edit한다. 전체 청사진·기획 문서·이전 iteration의 src 파일을 다시 Read하지 **않는다**.

**실패** + `CURRENT_ITER == MAX_ITER`:
- 안내 출력: `❌ 최대 반복({MAX_ITER}) 소진, 미해결 실패 — /pr-merge 실행하지 않고 정지`
- Step 5.7 (보고서)로 직진, **`/pr-merge`는 호출하지 않는다**.

#### Step 5.6: PR 머지 (테스트 통과 시만)

##### 5.6.A 💾 Pre-merge Silent Save (특히 중요)

머지 직전에 한 번 더 상태를 영속화한다. `/pr-merge --auto` 자체가 PR 생성·코드 리뷰·이슈 수정·재리뷰까지 많은 컨텍스트를 추가로 소비하므로, 진입 시점의 컨텍스트가 가벼울수록 안정적이다.

**이 save는 다른 곳보다 더 엄격하다**: pr-merge가 시작되면 머지 후 worktree가 사라지므로, `auto-state.yaml`이 sprint 브랜치 commit 안에 반드시 포함되어 있어야 dev로 머지된 뒤 메인 worktree에서 접근 가능하다.

**5.1.5 Silent Save Protocol을 실행**하되 다음 추가 검증:

1. `auto-state.yaml`에 `completed_stages: [..., 5.5_passed]`, `next_stage: 5.6.B`, 최종 `last_test_result` 기록
2. **반드시 git commit** (5.1.5.B 규칙 — 추적되지 않은 yaml이 worktree 제거와 함께 사라지는 사고 방지):
   ```bash
   git add docs/sprints/sprint-${N}-${SPRINT_NAME}/auto-state.yaml
   git commit -m "chore: pre-merge checkpoint (Stage 5.6.A)"
   ```
3. 다음 한 줄을 가볍게 출력하고 **곧바로 Step 5.6.B 자동 호출**:
   ```
   ✅ Pre-merge save 완료 → /pr-merge --auto 자동 호출 (worktree 제거 예정)
   ```
4. 5.1.5.C의 참조 회피 규칙 적용 — 이전 iteration 로그, 청사진 전체, 테스트 출력은 더 이상 재참조하지 않음. pr-merge는 git diff와 PR 메타데이터로 작업한다.

##### 5.6.B `/pr-merge --auto` 호출

`Skill('pr-merge', '--auto')` 호출.

`/pr-merge --auto`가 다음을 자동 처리한다:
- 변경사항 커밋 (확인 프롬프트 자동 승인)
- PR 생성
- 코드 리뷰 → 이슈 수정 → 재리뷰 사이클 (최대 3회)
- Critical 이슈 잔존 시 halt (true HITL)
- 머지 (최종 확인 프롬프트 자동 승인)
- **worktree 자동 제거** + 메인 worktree(dev) 복귀

> sprint-init은 sprint worktree 안에서 실행되고 있으므로, /pr-merge가 머지 완료 후 자기 자신이 들어 있는 worktree를 제거한다. 사용자는 머지 완료 시 메인 worktree(dev)로 자동 복귀된다.

##### 5.6.C 머지 결과를 `auto-state.yaml`에 기록

worktree 제거 직후, **메인 worktree에서** 다음을 수행한다:
1. `cd $(astra_main_worktree_root)` (worktree가 제거되었으면 자동으로 메인에 있겠지만, 안전을 위해 명시)
2. 머지 결과(`pr_url`, `merge_success: true`, `worktree_removed: true`)를 `docs/sprints/sprint-{N}-{sprint-name}/auto-state.yaml`(메인 worktree 경로)에 기록

> **경로 주의**: worktree가 제거되었으므로 `auto-state.yaml`은 이제 *메인 worktree*의 `docs/sprints/sprint-{N}-{sprint-name}/`에 존재한다 (Sprint 브랜치 머지로 dev에 반영된 파일). 만약 메인 worktree에 해당 경로가 없으면 (sprint 브랜치가 dev로 머지되어 파일이 따라왔어야 함) `git pull origin dev`로 동기화 후 다시 확인.

##### 5.6.D Final Silent Save (선택)

5.7 보고서는 일반적으로 컨텍스트 부담이 작으므로 별도 silent save는 생략한다. 5.6.C에서 이미 머지 결과(pr_url, merge_success)를 yaml에 기록했으므로 5.7에서는 그 yaml만 다시 읽으면 된다 — exit/사용자 확인 없이 곧바로 Step 5.7로 진행한다.

#### Step 5.7: 최종 보고서 출력

**데이터 소스**: `auto-state.yaml`을 다시 읽어 보고서 값을 채운다. 시스템 자동 압축으로 in-flight 변수가 휘발되었을 가능성을 대비해, 컨텍스트에 남아 있는 값에 의존하지 않고 상태 파일을 단일 진실 출처로 사용한다.

```
═══════════════════════════════════════════════════════
{✅ / ❌ / ⚠️} Sprint {N} --auto 완료

🔁 Iterations: {iteration.current_iter}/{iteration.max_iter}
✅ 테스트: {last_test_result.passed}/{last_test_result.total}
📦 Sprint Branch: feat/sprint-{N}-{sprint-name}
🌿 Worktree: {merge.worktree_removed ? "removed" : "preserved (실패로 인해 유지)"}

📁 산출물:
  - 청사진: docs/blueprints/[NNN]-*/blueprint.md
  - 스프린트: docs/sprints/sprint-{N}-{sprint-name}/
  - 테스트: docs/tests/test-cases/sprint-{N}-{sprint-name}/
  - Iteration 요약: docs/sprints/sprint-{N}-{sprint-name}/iterations/
  - 자동 실행 상태: docs/sprints/sprint-{N}-{sprint-name}/auto-state.yaml

{merge.pr_url (머지 성공 시)}
{last_iteration_classification가 set이면 미해결 실패 요약}
═══════════════════════════════════════════════════════
```

보고서 출력 후 `auto-state.yaml`은 보존한다 (디버그/재현용). 다음 sprint에서는 새 파일이 작성된다.

---

## Notes

- Existing sprint files are not overwritten.
- The prompt map is filled in collaboratively by VA and PE during the Planning meeting.
- Sprint worktree 안의 작업·테스트·머지가 끝나면 `/pr-merge`가 worktree를 자동 제거한다. 충돌·중단으로 worktree가 남으면 사용자가 해결 후 `/pr-merge` 재실행으로 이어진다.
- `.astra-worktree.env`를 사용자가 수정하지 말 것 — `/test-run`이 자동 source 한다.
- **`--auto` 모드 사용 시 주의**:
  - blueprint가 사전에 준비되어 있어야 한다 (sprint-init은 blueprint를 생성하지 않음).
  - `SPEC_GAP` / `DESIGN_MISALIGN` 분류 시 자동 머지하지 않고 abort — blueprint·UX 수정은 사용자 판단 필요.
  - 기획부터 풀스택 자동 생성이 필요하면 `/autorun {기능 설명}`을 사용하라.
