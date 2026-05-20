---
name: sprint-init
description: "Initializes a new ASTRA sprint. Creates an isolated sprint worktree (with port-isolated dev server settings), generates sprint prompt maps, progress trackers, and retrospective templates inside that worktree, and prints the cd path so all subsequent development and testing happens in the worktree."
argument-hint: "[sprint-number]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# ASTRA Sprint Initialization (v5.0+)

Creates a sprint-level isolated worktree, writes port-isolated env settings, and generates prompt maps / progress trackers / retrospective templates **inside that worktree**.

> **v5.0+ 정책**: sprint당 단일 worktree(`.astra-worktrees/sprint-<N>-<name>/`)에서 모든 feature 작업·테스트가 진행된다. 머지는 `/pr-merge`가 dev로 반영하고 worktree를 자동 제거한다. 트레이드오프: sprint당 PR 1개 — feature별 리뷰 granularity는 없지만 sprint 단위로 깔끔히 머지/롤백된다.

## Execution Procedure

### Step 0: Main Worktree Guard

Sprint worktree를 *생성*하는 명령이므로 메인 worktree에서만 실행한다. 이미 격리 worktree 안이면 거부:

```bash
source "$CLAUDE_PLUGIN_ROOT/scripts/worktree-helpers.sh"
astra_ensure_main_worktree || exit 1
```

### Step 1: Confirm Sprint Number and Sprint Name

Parse from `$ARGUMENTS`:
- **Sprint number** (optional): If not provided, scan existing directories in `docs/sprints/` matching the `sprint-{N}-{name}/` pattern (e.g., `sprint-1-auth/`, `sprint-2-workspace/`) to determine the next number.
- **Sprint name** (optional): The primary blueprint/feature name for this sprint.

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

### 1.1 Design Prompt
/feature-dev "Write the design document for {feature description}
to docs/blueprints/{NNN}-{feature-name}/blueprint.md.
{detailed requirements}
Refer to docs/database/database-design.md for DB schema.
Do not modify any code yet."

> **Numbering Rule**: Scan existing directories in `docs/blueprints/` to determine the next number. Use 3-digit zero-padded format (e.g., `001-`, `002-`).

### 1.2 DB Design Reflection Prompt
/feature-dev "Add/update the {module-name} tables in
docs/database/database-design.md:
- {table list}
- Also update the ERD and FK relationship summary. Follow standard terminology dictionary.
Do not modify any code yet."

### 1.3 Test Case Prompt
/feature-dev "Based on the feature requirements in docs/blueprints/{NNN}-{feature-name}/blueprint.md,
write test cases to docs/tests/test-cases/sprint-{N}/{feature-name}-test-cases.md.
Use Given-When-Then format, include unit/integration/edge cases.
Do not modify any code yet."

### 1.4 Implementation Prompt
/feature-dev "Strictly follow the contents of docs/blueprints/{NNN}-{feature-name}/blueprint.md and
docs/database/database-design.md to proceed with development.
Write tests referencing docs/tests/test-cases/sprint-{N}/{feature-name}-test-cases.md,
and once implementation is complete, run all tests and
report results to docs/tests/test-reports/."

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

## Notes

- Existing sprint files are not overwritten.
- The prompt map is filled in collaboratively by VA and PE during the Planning meeting.
- Sprint worktree 안의 작업·테스트·머지가 끝나면 `/pr-merge`가 worktree를 자동 제거한다. 충돌·중단으로 worktree가 남으면 사용자가 해결 후 `/pr-merge` 재실행으로 이어진다.
- `.astra-worktree.env`를 사용자가 수정하지 말 것 — `/test-run`이 자동 source 한다.
