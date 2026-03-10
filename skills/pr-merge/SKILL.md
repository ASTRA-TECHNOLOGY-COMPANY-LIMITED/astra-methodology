---
name: pr-merge
description: "PR 생성부터 코드 리뷰, 이슈 수정, 머지까지 자동화된 반복 사이클을 실행합니다. 커밋→푸시→PR 생성→코드 리뷰→수정→재리뷰→머지 워크플로우를 단일 명령으로 처리합니다."
argument-hint: "[max-iterations] [--no-review] [--draft] [--patch|--minor|--major] [--staging] [--main]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Task
---

# ASTRA PR Review & Merge Workflow

커밋부터 코드 리뷰, 이슈 수정, 머지까지 전체 사이클을 자동화합니다.
리뷰 → 수정 → 재리뷰 반복 사이클을 최대 반복 횟수까지 자동 실행합니다.

**브랜치 전략**: `feature → dev → staging → main`

## Execution Procedure

### Step 1: 인자 파싱 및 사전 검증

`$ARGUMENTS`를 파싱하여 옵션을 결정한다:

- **max-iterations**: 숫자 인자 → 최대 리뷰 반복 횟수 (기본값: 3)
- **--no-review**: 코드 리뷰 없이 커밋→푸시→PR 생성→머지만 실행
- **--draft**: PR을 Draft 상태로 생성
- **--patch / --minor / --major**: 버전 범프 유형 (기본값: --patch)
- **--staging**: 프로모션 모드 — `dev` → `staging`으로 머지
- **--main**: 프로모션 모드 — `staging` → `main`으로 머지

**모드 결정**:
- `--staging` 또는 `--main` → 프로모션 모드
- 그 외 → 기본 모드 (feature → 대상 브랜치, Step 1.1에서 결정)

다음 사전 조건을 검증한다:

1. **gh CLI 인증**: `gh auth status`를 실행하여 GitHub CLI 인증 상태를 확인한다. 인증되지 않은 경우 `gh auth login`을 안내하고 중단한다.
2. **클린 상태 확인**: `git status`로 현재 상태를 파악한다 (커밋되지 않은 변경사항, 스테이징된 파일 등).
   - 프로모션 모드에서 미커밋 변경사항이 있으면 경고하고 중단한다 (프로모션은 클린 상태에서만 실행).

### Step 1.1: 대상 브랜치 선택 (기본 모드만)

프로모션 모드가 아닌 경우, **AskUserQuestion**으로 머지 대상 브랜치를 사용자에게 물어본다:

> **어떤 브랜치에 머지할까요?**
> - `dev` — 피처 개발 (기본값)
> - `staging` — 스테이징 버그픽스
> - 기타 (직접 입력)

사용자의 선택을 `{target-branch}`로 저장한다. 입력이 없거나 기본값을 선택하면 `dev`를 사용한다.

> **참고**: 이후 모든 단계에서 `{target-branch}`는 이 단계에서 선택된 브랜치를 참조한다.

### Step 2: 브랜치 동기화 (모든 모드 공통)

모든 모드에서 실행 전 `main`, `staging`, `dev` 브랜치를 최신 상태로 동기화하고, 상위 브랜치의 변경사항을 하위 브랜치로 캐스케이드 머지한다.

현재 브랜치를 `{current-branch}`로 저장한다.

#### Step 2.1: 원격 fetch 및 브랜치 pull

```bash
git fetch origin
```

`main`, `staging`, `dev` 각 브랜치에 대해:
1. `git ls-remote --heads origin {branch}`로 원격 존재 여부를 확인한다.
2. 원격에 존재하지 않는 브랜치는 건너뛴다 (경고만 출력).
3. 원격에 존재하는 브랜치에 대해 로컬 브랜치가 없으면 `git checkout -b {branch} origin/{branch}`로 트래킹 브랜치를 생성한다.
4. 로컬 브랜치가 이미 있으면 checkout 후 pull 한다:
   ```bash
   git checkout {branch}
   git pull --rebase origin {branch}
   ```

> **필수**: `dev` 브랜치는 반드시 존재해야 한다. 원격에 `dev`가 없으면 **AskUserQuestion**으로 사용자에게 기본 브랜치로부터 `dev`를 생성할지 확인한다. 거부 시 중단한다.

#### Step 2.2: 캐스케이드 머지 (main → staging → dev)

상위 브랜치의 변경사항을 하위 브랜치로 순차적으로 머지한다. 원격에 존재하는 브랜치만 대상으로 한다.

**모드별 캐스케이드 범위**:
- **기본 모드**: 전체 캐스케이드 실행 (`main → staging → dev`)
- **`--staging` 프로모션**: `main → staging`까지만 실행 (dev는 머지 대상이 아님)
- **`--main` 프로모션**: 캐스케이드를 건너뛴다 (staging → main 방향이므로 역방향 동기화 불필요)

캐스케이드 실행 대상인 경우:

1. **main → staging** (staging이 원격에 존재하는 경우):
   ```bash
   git checkout staging
   git merge main
   ```
   - 충돌 발생 시: 충돌 파일 목록을 출력하고 사용자에게 수동 해결을 안내한 후 중단한다.
   - 머지 후 변경이 있으면: `git push origin staging`

2. **staging → dev** (staging이 원격에 존재하고, 기본 모드인 경우):
   ```bash
   git checkout dev
   git merge staging
   ```
   - 충돌 발생 시: 충돌 파일 목록을 출력하고 사용자에게 수동 해결을 안내한 후 중단한다.
   - 머지 후 변경이 있으면: `git push origin dev`

3. **main → dev** (staging이 원격에 존재하지 않고, 기본 모드인 경우):
   ```bash
   git checkout dev
   git merge main
   ```
   - 충돌 발생 시: 충돌 파일 목록을 출력하고 사용자에게 수동 해결을 안내한 후 중단한다.
   - 머지 후 변경이 있으면: `git push origin dev`

4. `git checkout {current-branch}`로 원래 브랜치로 복귀한다.

> **참고**: 캐스케이드 머지에서 변경사항이 없으면 (Already up to date) 해당 단계를 조용히 건너뛴다.

### Step 3: 모드별 분기

- **프로모션 모드** (`--staging` / `--main`): **Step 10**으로 진행
- **기본 모드**: **Step 4**로 진행

---

## 기본 모드 (feature → {target-branch})

### Step 4: 작업 브랜치 확인

현재 브랜치가 `main`, `master`, `staging`, 또는 `dev`인지 확인한다.

- **보호 브랜치에 있는 경우**: 작업 브랜치 자동 생성이 필요 → **Step 4.1**로 진행
- **이미 작업 브랜치(feature, fix, docs 등)에 있는 경우**: 그대로 사용 → **Step 5**로 진행

### Step 4.1: 작업 브랜치 생성

1. `git status`와 `git log`로 현재 변경사항 및 최근 작업 컨텍스트를 분석하여 적절한 브랜치명을 추천한다 (예: `feat/user-auth`, `fix/login-error`).
2. **AskUserQuestion**으로 브랜치명을 확인한다. 추천 브랜치명을 기본 옵션으로 제시한다.
3. 사용자가 확인한 브랜치명으로 `{target-branch}`를 베이스로 작업 브랜치를 생성한다:
   ```bash
   git checkout -b {branch-name} {target-branch}
   ```
   미커밋 변경사항은 그대로 유지된다. 현재 브랜치가 이미 `{target-branch}`인 경우에도 명시적으로 `{target-branch}`를 베이스로 지정한다.
4. 이후 단계에서 `{branch-name}`은 이 새로 생성된 브랜치를 참조한다.

### Step 5: 대상 브랜치 동기화

Step 2에서 이미 캐스케이드 머지를 완료했으므로, 작업 브랜치에 `{target-branch}`의 최신 변경사항을 반영한다:

```bash
git merge origin/{target-branch}
```

- **충돌 없음**: 다음 단계로 진행
- **충돌 발생**: 충돌 파일 목록을 출력하고, 사용자에게 수동 해결을 안내한 후 중단한다.

**건너뛰기 조건**: Step 4.1을 방금 실행한 경우 (작업 브랜치를 `{target-branch}`로부터 생성) 이미 동기화 상태이므로 건너뛴다.

### Step 6: 커밋 & 푸시

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

### Step 7: PR 생성

기존 PR이 있는지 확인하고, 없으면 새로 생성한다:

1. `gh pr list --head {branch-name} --base {target-branch} --state open`으로 기존 PR 확인
2. **기존 PR이 있으면**: PR URL을 출력하고 Step 8로 진행
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

- `--draft` 옵션이 지정된 경우 `--draft` 플래그 추가
- PR 제목은 70자 이내로 작성
- PR URL을 출력한다

**Step 8로 진행한다.**

---

## 공통: 코드 리뷰 & 머지 사이클

### Step 8: 코드 리뷰

리뷰 반복 횟수를 0으로 초기화한다.

`--no-review` 옵션이 지정된 경우 이 단계를 건너뛰고 Step 8.3으로 진행한다.

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

### Step 8.1: 리뷰 결과 판정

리뷰 결과를 바탕으로 다음 행동을 결정한다:

- **Critical + High = 0건**: 리뷰 통과 → **Step 8.3**으로 진행
- **Critical + High > 0건 AND 반복 횟수 < MAX**: 이슈 수정 필요 → **Step 8.2**로 진행
- **반복 횟수 = MAX에 도달**: **AskUserQuestion**으로 사용자에게 선택지를 제공
  - (a) 추가 반복 허용 (MAX 증가)
  - (b) 남은 이슈를 무시하고 머지 진행 (단, Critical 이슈가 있으면 이 선택지는 제공하지 않음)
  - (c) 워크플로우 중단

**머지 차단 조건**: Critical 이슈가 1건이라도 남아있으면 머지를 진행할 수 없다.

### Step 8.2: 이슈 수정 & 재리뷰

1. 이슈 목록을 사용자에게 표시한다.
2. **AskUserQuestion**으로 자동 수정 진행 여부를 확인한다.
3. 사용자 확인 후, 각 이슈를 순서대로 수정한다:
   - 해당 파일을 읽고 이슈 위치를 파악
   - Edit tool로 코드 수정
   - 수정 내용 요약 출력
4. 프로젝트에 테스트가 설정되어 있으면 테스트를 실행하여 수정이 기존 기능을 깨뜨리지 않았는지 확인한다.
5. 수정된 파일을 `git add`로 스테이징
6. 반복 횟수를 1 증가시킨다.
7. `git commit` — 메시지는 "fix: address code review issues (iteration {N})" 형식 (N은 1부터 시작)
8. `git push`로 원격에 푸시
9. **Step 8로 복귀**하여 재리뷰 실행 (반복 횟수는 유지, 재초기화하지 않음)

### Step 8.3: PR 머지 확인

1. **AskUserQuestion**으로 사용자에게 최종 머지 확인을 요청한다.
   - PR URL, 리뷰 결과 요약 (통과 여부, 반복 횟수), 변경 파일 수를 표시
2. 사용자가 머지를 거부하면 워크플로우를 중단한다.

### Step 8.4: PR 머지

사용자 확인 후 PR을 머지한다:

1. Draft PR인 경우 먼저 `gh pr ready`로 Ready 상태로 변경
2. `gh pr merge --merge --delete-branch`로 머지 실행
   - 프로모션 모드에서는 `--delete-branch`를 제외한다 (소스 브랜치는 영구 브랜치)

**모드 확인**: `--staging` 또는 `--main` 플래그가 지정된 경우 **Step 11**로, 그 외는 **Step 9**로 진행한다.

---

## 기본 모드: 정리

### Step 9: 정리 및 버전 업데이트

머지 후 로컬 환경을 정리한다:

1. `git fetch origin`으로 원격 최신 상태를 가져온다.
2. `git checkout {target-branch}`로 전환한다.
3. `git pull --rebase`로 최신 상태 동기화
4. 머지된 로컬 브랜치 삭제: `git branch -d {branch-name}`
5. 최종 요약을 출력한다:

> **참고**: 기본 모드에서는 버전 범프를 수행하지 않는다. 버전 범프는 `--main` 프로모션 (Step 11)에서만 실행된다.

```
## PR Review & Merge 완료

### 결과 요약
- PR: {PR URL}
- 머지: {branch-name} → {target-branch}
- 리뷰 반복: {N}회
- 수정된 이슈: Critical {n}건, High {n}건
- 상태: ✅ 머지 완료

### 변경사항
- {커밋 요약 1}
- {커밋 요약 2}
```

---

## 프로모션 모드 (--staging / --main)

### Step 10: 프로모션 준비

프로모션 모드는 브랜치 간 코드를 승격(promote)하는 워크플로우이다.

**브랜치 매핑**:
- `--staging`: `{source-branch}` = `dev`, `{target-branch}` = `staging`
- `--main`: `{source-branch}` = `staging`, `{target-branch}` = `main`

**검증 절차**:

1. **소스 브랜치 확인**: `git ls-remote --heads origin {source-branch}`로 원격에 `{source-branch}`가 존재하는지 확인한다. 없으면 에러 메시지를 출력하고 중단한다.
2. **대상 브랜치 확인**: `git ls-remote --heads origin {target-branch}`로 원격에 `{target-branch}`가 존재하는지 확인한다.
   - **존재하지 않으면**: **AskUserQuestion**으로 `{target-branch}` 브랜치를 `{source-branch}`로부터 생성할지 확인한다. 승인 시 생성하고 push, 거부 시 중단한다.
3. **소스 브랜치로 전환**: `git checkout {source-branch}`
4. **차이 확인**: `git log origin/{target-branch}..origin/{source-branch} --oneline`으로 프로모션할 커밋이 있는지 확인한다. 차이가 없으면 "프로모션할 변경사항이 없습니다"를 출력하고 중단한다.
5. 커밋 목록을 사용자에게 표시한다.

### Step 10.1: 프로모션 PR 생성

1. `gh pr list --head {source-branch} --base {target-branch} --state open`으로 기존 프로모션 PR 확인
2. **기존 PR이 있으면**: PR URL을 출력하고 Step 8로 진행
3. **기존 PR이 없으면**: 프로모션 PR 생성

```bash
gh pr create --head {source-branch} --base {target-branch} --title "promote: {source-branch} → {target-branch}" --body "$(cat <<'EOF'
## Promotion: {source-branch} → {target-branch}

### Commits included
{커밋 목록}

### Checklist
- [ ] 코드 리뷰 통과
- [ ] 테스트 통과 확인

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- `--draft` 옵션이 지정된 경우 `--draft` 플래그 추가
- PR URL을 출력하고 **Step 8**로 진행 (공통 코드 리뷰 & 머지 사이클)

> **Note**: Step 8.2에서 이슈 수정 시 `{source-branch}`에서 커밋하고 푸시한다.

---

## 프로모션 모드: 정리

### Step 11: 프로모션 완료 정리

1. `git fetch origin`으로 원격 최신 상태를 가져온다.
2. `git checkout {target-branch}`으로 전환한다.
3. `git pull --rebase`로 최신 상태 동기화
4. 프로모션에서는 소스 브랜치를 삭제하지 않는다 (`dev`, `staging`은 영구 브랜치).
5. 버전 범프는 `--main` 프로모션일 때만 실행한다 (릴리스 버전 관리):
   - `.claude-plugin/plugin.json`과 `.claude-plugin/marketplace.json`의 존재 여부를 확인한다.
   - 파일이 존재하면 `--patch` / `--minor` / `--major` 옵션에 따라 SemVer 버전을 범프한다:
     - `--patch` (기본값): `x.y.z` → `x.y.z+1`
     - `--minor`: `x.y.z` → `x.y+1.0`
     - `--major`: `x.y.z` → `x+1.0.0`
   - 두 파일 모두 동일한 버전으로 업데이트한다.
   - `main`에 직접 커밋하고 푸시한다: "chore: bump version to {new-version}"
6. 최종 요약을 출력한다:

```
## Promotion 완료

### 결과 요약
- PR: {PR URL}
- 프로모션: {source-branch} → {target-branch}
- 포함 커밋: {N}건
- 리뷰 반복: {N}회
- 버전: {old-version} → {new-version} (--main일 때만)
- 상태: ✅ 프로모션 완료
```

---

## Quick Run Examples

```
# 기본 실행 — feature → dev 머지 (최대 3회 리뷰 반복)
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

# 프로모션: dev → staging
/pr-merge --staging

# 프로모션: staging → main (릴리스)
/pr-merge --main

# 프로모션 + minor 버전 범프
/pr-merge --main --minor

# 프로모션 + 리뷰 스킵
/pr-merge --staging --no-review
```

## Notes

- **브랜치 전략**: `feature → dev → staging → main` 순서로 코드를 승격한다.
- **공통 전처리**: 모든 모드에서 실행 전 `main` / `staging` / `dev`를 pull 받는다. 캐스케이드 머지는 모드별로 범위가 다르다: 기본 모드에서는 전체(`main → staging → dev`), `--staging`에서는 `main → staging`만, `--main`에서는 건너뛴다.
- **기본 모드**: 실행 시 머지 대상 브랜치를 사용자에게 물어본다 (`dev`, `staging`, 또는 기타). 스테이징 버그픽스는 `staging`에 직접 머지하고, 피처 개발은 `dev`에 머지할 수 있다. `main`/`master`/`staging`/`dev` 브랜치에서 실행하면 자동으로 작업 브랜치를 생성한다. 원격에 `dev`이 없으면 기본 브랜치로부터 자동 생성한다.
- **프로모션 모드 (`--staging`)**: `dev` → `staging`으로 승격한다. 작업 브랜치 생성/커밋 단계를 건너뛰고 PR 기반 머지에 집중한다.
- **프로모션 모드 (`--main`)**: `staging` → `main`으로 승격한다. 릴리스 프로모션이므로 버전 범프가 이 단계에서 실행된다.
- 머지 완료 후 최종 체크아웃 위치는 `{target-branch}`이다.
- Critical 이슈가 남아있으면 머지가 차단된다.
- 충돌 발생 시 자동 해결을 시도하지 않고, 사용자에게 안내 후 중단한다.
- 버전 범프는 `--main` 프로모션에서만 실행되며, `.claude-plugin/plugin.json`이 존재하는 프로젝트에서만 적용된다.
- 커밋, 자동 수정, 머지 전에는 반드시 사용자 확인을 거친다.
- 프로모션 모드에서 소스 브랜치(`dev`, `staging`)는 삭제하지 않는다.
