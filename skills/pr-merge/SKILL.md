---
name: pr-merge
description: "PR 생성부터 코드 리뷰, 이슈 수정, 머지까지 자동화된 반복 사이클을 실행합니다. 커밋→푸시→PR 생성→코드 리뷰→수정→재리뷰→머지 워크플로우를 단일 명령으로 처리합니다."
argument-hint: "[max-iterations] [--no-review] [--draft] [--patch|--minor|--major]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Task
---

# ASTRA PR Review & Merge Workflow

커밋부터 코드 리뷰, 이슈 수정, 머지까지 전체 사이클을 자동화합니다.
리뷰 → 수정 → 재리뷰 반복 사이클을 최대 반복 횟수까지 자동 실행합니다.

## Execution Procedure

### Step 1: 사전 검증

`$ARGUMENTS`를 파싱하여 옵션을 결정한다:

- **max-iterations**: 숫자 인자 → 최대 리뷰 반복 횟수 (기본값: 3)
- **--no-review**: 코드 리뷰 없이 커밋→푸시→PR 생성→머지만 실행
- **--draft**: PR을 Draft 상태로 생성
- **--patch / --minor / --major**: 버전 범프 유형 (기본값: --patch)

다음 사전 조건을 검증한다:

1. **브랜치 확인**: 현재 브랜치가 `main`, `master`, 또는 `staging`인지 확인한다. 이 브랜치들에서 실행 시 **작업 브랜치 자동 생성이 필요**하다고 플래그를 설정한다 (중단하지 않음). 이미 작업 브랜치(feature, fix 등)이면 그대로 사용한다.
2. **gh CLI 인증**: `gh auth status`를 실행하여 GitHub CLI 인증 상태를 확인한다. 인증되지 않은 경우 `gh auth login`을 안내하고 중단한다.
3. **클린 상태 확인**: `git status`로 현재 상태를 파악한다 (커밋되지 않은 변경사항, 스테이징된 파일 등).
4. **머지 대상 브랜치 결정**: `{target-branch}`는 항상 `staging`이다.
   - `git ls-remote --heads origin staging`으로 원격에 `staging` 브랜치 존재 여부를 확인한다.
   - **staging 존재**: 그대로 사용
   - **staging 미존재**: 기본 브랜치로부터 `staging`을 자동 생성한다:
     1. `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`으로 `{default-branch}`를 확인한다.
     2. **AskUserQuestion**으로 사용자에게 `staging` 브랜치를 `{default-branch}`로부터 생성하여 원격에 push할 것인지 확인한다. 거부 시 중단한다.
     3. 현재 브랜치가 `staging`인 경우 (로컬에만 존재): `git push -u origin staging`으로 현재 브랜치를 그대로 push한다.
     4. 현재 브랜치가 `staging`이 아닌 경우:
        ```
        git fetch origin
        # 로컬 staging 브랜치 존재 여부 확인
        git branch --list staging
        # 로컬 staging이 이미 존재하면: git checkout staging
        # 로컬 staging이 없으면: git checkout -b staging origin/{default-branch}
        git push -u origin staging
        git checkout {current-branch}
        ```
   - 이후 모든 단계에서 `{target-branch}`는 `staging`을 참조한다.

### Step 1.3: 작업 브랜치 생성 (필요 시)

Step 1에서 작업 브랜치 자동 생성 플래그가 설정된 경우 (현재 브랜치가 `main`, `master`, 또는 `staging`인 경우):

1. `git status`와 `git log`로 현재 변경사항 및 최근 작업 컨텍스트를 분석하여 적절한 브랜치명을 추천한다 (예: `feat/user-auth`, `fix/login-error`).
2. **AskUserQuestion**으로 브랜치명을 확인한다. 추천 브랜치명을 기본 옵션으로 제시한다.
3. 사용자가 확인한 브랜치명으로 현재 브랜치(`{current-branch}`)를 베이스로 작업 브랜치를 생성한다:
   ```
   git checkout -b {branch-name}
   ```
   작업 브랜치는 현재 HEAD를 베이스로 생성되므로, 미커밋 변경사항은 그대로 유지된다.
4. 이후 단계에서 `{branch-name}`은 이 새로 생성된 브랜치를 참조한다.

이미 작업 브랜치(feature, fix, docs 등)에 있으면 이 단계를 건너뛴다.

### Step 1.5: 대상 브랜치 동기화

머지 대상 브랜치(`staging`)의 최신 변경사항을 현재 브랜치에 동기화한다.

**건너뛰기 조건**: Step 1.3에서 작업 브랜치를 `staging`으로부터 방금 생성한 경우 (즉, `{current-branch}`가 `staging`이었던 경우), 이미 `origin/staging` HEAD와 동일하므로 이 단계를 건너뛴다.

그 외의 경우:

```
git fetch origin {target-branch}
git merge origin/{target-branch}
```

- **충돌 없음**: 다음 단계로 진행
- **충돌 발생**: 충돌 파일 목록을 출력하고, 사용자에게 수동 해결을 안내한 후 중단한다. 자동 충돌 해결은 시도하지 않는다.

> **참고**: `{current-branch}`가 `main`/`master`였던 경우, `origin/staging`에 `main`에 없는 변경사항이 포함될 수 있다. 충돌 가능성이 있으므로 merge 전 사용자에게 안내한다.

### Step 2: 커밋 & 푸시

미커밋 변경사항을 처리한다:

1. `git status`로 변경사항을 확인한다.
2. 변경사항이 있으면 변경 내용 요약을 사용자에게 보여주고 **AskUserQuestion**으로 커밋 진행 여부를 확인한다.
3. 사용자 확인 후:
   - 변경된 파일을 `git add`로 스테이징 (민감 파일 `.env`, `credentials` 등 제외)
   - `git diff --staged`로 스테이징된 변경사항 분석
   - `git log`로 최근 커밋 메시지 스타일 확인
   - 변경사항을 분석하여 커밋 메시지 작성 후 `git commit` 실행
4. `git push -u origin {branch-name}`으로 원격에 푸시한다.

변경사항이 없으면 이 단계를 건너뛴다.

### Step 3: PR 생성

기존 PR이 있는지 확인하고, 없으면 새로 생성한다:

1. `gh pr list --head {branch-name} --state open`으로 기존 PR 확인
2. **기존 PR이 있으면**: PR URL을 출력하고 Step 4로 진행
3. **기존 PR이 없으면**: ASTRA 템플릿으로 PR 생성

```bash
gh pr create --base {target-branch} --title "{PR 제목}" --body "$(cat <<'EOF'
## Summary
- {변경사항 요약 1}
- {변경사항 요약 2}

## Test plan
- [ ] 코드 리뷰 통과
- [ ] 테스트 실행 확인

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- `--base {target-branch}` 플래그로 머지 대상 브랜치를 명시적으로 지정
- `--draft` 옵션이 지정된 경우 `--draft` 플래그 추가
- PR 제목은 70자 이내로 작성
- PR URL을 출력한다

### Step 4: 코드 리뷰

`--no-review` 옵션이 지정된 경우 이 단계를 건너뛰고 Step 7로 진행한다.

`feature-dev:code-reviewer` Task 에이전트를 스폰하여 코드 리뷰를 실행한다:

```
Task tool (subagent_type: "feature-dev:code-reviewer")
- PR의 변경사항을 기준으로 코드 리뷰 실행
- 버그, 로직 오류, 보안 취약점, 코드 품질 이슈를 분석
```

리뷰 결과를 다음 4단계로 분류하여 출력한다:

| 심각도 | 설명 | 예시 |
|--------|------|------|
| **Critical** | 즉시 수정 필수, 프로덕션 장애 위험 | SQL injection, null 참조, 데이터 손실 |
| **High** | 수정 권장, 중요 버그 또는 보안 이슈 | 미처리 예외, 인증 우회 가능성 |
| **Medium** | 코드 품질 개선, 기능에는 영향 없음 | 중복 코드, 비효율 로직, 불명확한 네이밍 |
| **Low** | 스타일/컨벤션, 선택적 개선 | 포매팅, 주석 누락, 미사용 import |

### Step 4.5: 리뷰 결과 판정

리뷰 결과를 바탕으로 다음 행동을 결정한다:

- **Critical + High = 0건**: 리뷰 통과 → **Step 7**로 진행
- **Critical + High > 0건 AND 반복 횟수 < MAX**: 이슈 수정 필요 → **Step 5**로 진행
- **반복 횟수 = MAX에 도달**: **AskUserQuestion**으로 사용자에게 선택지를 제공
  - (a) 추가 반복 허용 (MAX 증가)
  - (b) 남은 이슈를 무시하고 머지 진행 (단, Critical 이슈가 있으면 이 선택지는 제공하지 않음)
  - (c) 워크플로우 중단

**머지 차단 조건**: Critical 이슈가 1건이라도 남아있으면 머지를 진행할 수 없다.

### Step 5: 이슈 수정

Step 4에서 발견된 Critical 및 High 이슈를 수정한다:

1. 이슈 목록을 사용자에게 표시한다.
2. **AskUserQuestion**으로 자동 수정 진행 여부를 확인한다.
3. 사용자 확인 후, 각 이슈를 순서대로 수정한다:
   - 해당 파일을 읽고 이슈 위치를 파악
   - Edit tool로 코드 수정
   - 수정 내용 요약 출력
4. 프로젝트에 테스트가 설정되어 있으면 테스트를 실행하여 수정이 기존 기능을 깨뜨리지 않았는지 확인한다.

### Step 6: 재커밋 & 푸시

수정사항을 커밋하고 푸시한 뒤 재리뷰한다:

1. 수정된 파일을 `git add`로 스테이징
2. `git commit` — 메시지는 "fix: address code review issues (iteration {N})" 형식
3. `git push`로 원격에 푸시
4. **Step 4로 복귀**하여 재리뷰 실행

### Step 7: PR 머지 확인

1. **AskUserQuestion**으로 사용자에게 최종 머지 확인을 요청한다.
   - PR URL, 리뷰 결과 요약 (통과 여부, 반복 횟수), 변경 파일 수를 표시
2. 사용자가 머지를 거부하면 워크플로우를 중단한다.

### Step 8: PR 머지

사용자 확인 후 PR을 머지한다:

1. Draft PR인 경우 먼저 `gh pr ready`로 Ready 상태로 변경
2. `gh pr merge --merge --delete-branch`로 머지 실행

### Step 9: 정리 및 버전 업데이트

머지 후 로컬 환경을 정리하고, 필요 시 버전을 업데이트한다:

1. `git fetch origin`으로 원격 최신 상태를 가져온다.
2. `git checkout {target-branch}`으로 머지 대상 브랜치로 전환한다. 로컬에 해당 브랜치가 없으면 `git checkout -b {target-branch} origin/{target-branch}`로 트래킹 브랜치를 생성하며 전환한다.
3. `git pull --rebase`로 최신 상태 동기화 (fast-forward가 불가능한 경우에도 안전하게 동기화)
4. 머지된 로컬 브랜치 삭제: `git branch -d {branch-name}`
5. `.claude-plugin/plugin.json` 파일이 존재하는 플러그인 프로젝트에서 버전을 업데이트한다:
   - `.claude-plugin/plugin.json`과 `.claude-plugin/marketplace.json`의 존재 여부를 확인한다.
   - 파일이 존재하면 `--patch` / `--minor` / `--major` 옵션에 따라 SemVer 버전을 범프한다:
     - `--patch` (기본값): `x.y.z` → `x.y.z+1`
     - `--minor`: `x.y.z` → `x.y+1.0`
     - `--major`: `x.y.z` → `x+1.0.0`
   - 두 파일 모두 동일한 버전으로 업데이트한다.
   - `{target-branch}`에 직접 커밋하고 푸시한다: "chore: bump version to {new-version}"
   - 파일이 존재하지 않으면 버전 업데이트를 건너뛴다.
6. 최종 요약을 출력한다:

```
## PR Review & Merge 완료

### 결과 요약
- PR: {PR URL}
- 리뷰 반복: {N}회
- 수정된 이슈: Critical {n}건, High {n}건
- 버전: {old-version} → {new-version} (해당 시)
- 상태: ✅ 머지 완료

### 변경사항
- {커밋 요약 1}
- {커밋 요약 2}
```

## Quick Run Examples

```
# 기본 실행 (최대 3회 리뷰 반복)
/pr-merge

# 리뷰 반복 최대 5회
/pr-merge 5

# 코드 리뷰 없이 빠른 머지
/pr-merge --no-review

# Draft PR로 생성 후 리뷰
/pr-merge --draft

# minor 버전 범프와 함께 실행
/pr-merge --minor

# 옵션 조합
/pr-merge 5 --minor --draft
```

## Notes

- main/master/staging 브랜치에서 실행하면 자동으로 작업 브랜치를 생성한다.
- **머지 대상 브랜치**: 항상 `staging`으로 머지한다. 원격에 `staging`이 없으면 기본 브랜치로부터 자동 생성한다.
- 머지 완료 후 최종 체크아웃 위치는 `staging`이다.
- Critical 이슈가 남아있으면 머지가 차단된다.
- 충돌 발생 시 자동 해결을 시도하지 않고, 사용자에게 안내 후 중단한다.
- 버전 범프는 `.claude-plugin/plugin.json`이 존재하는 프로젝트에서만 실행된다.
- 커밋, 자동 수정, 머지 전에는 반드시 사용자 확인을 거친다.
