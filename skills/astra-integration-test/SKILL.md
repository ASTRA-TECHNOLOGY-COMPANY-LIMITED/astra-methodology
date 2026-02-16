---
name: astra-integration-test
description: "서버를 실행하고 Chrome MCP로 통합 테스트를 수행합니다. 서버 로그 모니터링, 페이지 검증, API 동작 확인, 성능 측정을 자동으로 진행합니다."
argument-hint: "[테스트 대상 URL 또는 시나리오]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__click, mcp__chrome-devtools__fill, mcp__chrome-devtools__fill_form, mcp__chrome-devtools__press_key, mcp__chrome-devtools__hover, mcp__chrome-devtools__list_console_messages, mcp__chrome-devtools__get_console_message, mcp__chrome-devtools__list_network_requests, mcp__chrome-devtools__get_network_request, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__wait_for, mcp__chrome-devtools__emulate, mcp__chrome-devtools__resize_page, mcp__chrome-devtools__list_pages, mcp__chrome-devtools__select_page, mcp__chrome-devtools__new_page, mcp__chrome-devtools__handle_dialog, mcp__chrome-devtools__performance_start_trace, mcp__chrome-devtools__performance_stop_trace, mcp__chrome-devtools__performance_analyze_insight
---

# ASTRA 통합 테스트

서버를 실행하고 Chrome MCP(chrome-devtools)를 통해 실제 브라우저 환경에서 통합 테스트를 수행합니다.
LLM이 서버 로그를 직접 모니터링하여 오류를 감지하고, 페이지 동작을 검증합니다.

## 실행 절차

### 1단계: 프로젝트 환경 파악

현재 프로젝트의 기술 스택과 서버 실행 방법을 파악합니다:

1. `CLAUDE.md`에서 기술 스택 확인 (백엔드, 프론트엔드, DB)
2. `package.json`, `build.gradle`, `pom.xml`, `pyproject.toml` 등에서 실행 스크립트 확인
3. `.env`, `.env.local` 등에서 환경변수 확인 (포트 번호, DB URL 등)

**기술 스택별 서버 실행 명령어 감지:**

| 기술 스택 | 감지 파일 | 실행 명령어 |
|----------|----------|-----------|
| Next.js | `package.json` → `next dev` | `npm run dev` |
| React (CRA/Vite) | `package.json` → `vite` / `react-scripts` | `npm run dev` / `npm start` |
| Spring Boot (Gradle) | `build.gradle` | `./gradlew bootRun` |
| Spring Boot (Maven) | `pom.xml` | `./mvnw spring-boot:run` |
| NestJS | `package.json` → `@nestjs/core` | `npm run start:dev` |
| FastAPI | `pyproject.toml` / `main.py` | `uvicorn main:app --reload` |
| Django | `manage.py` | `python manage.py runserver` |

### 2단계: 서버 시작 및 로그 모니터링

**백그라운드로 서버를 실행하고 로그를 캡처합니다:**

```
# 서버를 백그라운드로 실행 (Bash run_in_background=true)
{서버 실행 명령어}

# 서버 시작 대기 (포트가 열릴 때까지)
# 최대 60초 대기, 5초 간격 확인
```

**서버 시작 확인 순서:**
1. Bash `run_in_background=true`로 서버 프로세스 시작
2. `TaskOutput`으로 서버 로그를 주기적으로 확인하여 시작 완료 메시지 감지
3. 시작 실패 시 로그에서 오류 원인 분석 후 사용자에게 보고

**로그 모니터링 패턴:**

| 기술 스택 | 시작 완료 시그널 | 오류 패턴 |
|----------|---------------|----------|
| Next.js | `Ready in` / `Local:` | `Error:` / `EADDRINUSE` |
| Spring Boot | `Started .* in .* seconds` | `APPLICATION FAILED TO START` |
| NestJS | `Nest application successfully started` | `Error:` / `Cannot find module` |
| FastAPI | `Uvicorn running on` | `ERROR:` / `ModuleNotFoundError` |

### 3단계: 테스트 시나리오 결정

`$ARGUMENTS`를 확인합니다:

- **URL이 제공된 경우**: 해당 페이지에 대한 기본 검증 수행
- **시나리오가 제공된 경우**: 시나리오에 따라 단계별 테스트 수행
- **인자 없는 경우**: `docs/tests/test-cases/` 디렉토리에서 테스트 케이스 목록을 확인하고, 사용자에게 테스트 대상을 질문

### 4단계: 페이지 기본 검증

각 페이지에 대해 다음을 자동 수행합니다:

#### A. 페이지 로드 검증

```
1. chrome-devtools navigate_page로 대상 URL 접속
2. wait_for로 핵심 콘텐츠 로드 확인
3. take_snapshot으로 페이지 구조 확인
```

#### B. 콘솔 에러 확인

```
1. list_console_messages (types: ["error", "warn"])
2. 에러가 있으면 get_console_message로 상세 내용 확인
3. 서버 로그와 대조하여 백엔드/프론트엔드 오류 분류
```

#### C. 네트워크 요청 검증

```
1. list_network_requests (resourceTypes: ["xhr", "fetch"])
2. 실패한 요청 (4xx, 5xx) 감지
3. get_network_request로 요청/응답 상세 확인
4. 서버 로그에서 해당 요청의 백엔드 처리 로그 확인
```

#### D. 반응형 레이아웃 검증

```
1. 데스크톱 (1280x720) → take_snapshot
2. 태블릿 (768x1024) → take_snapshot
3. 모바일 (375x667) → take_snapshot
4. 각 뷰포트에서 레이아웃 깨짐 확인
```

### 5단계: 시나리오 기반 통합 테스트

테스트 케이스 문서(`docs/tests/test-cases/`)를 참조하여 사용자 시나리오를 실행합니다:

#### 폼 입력 테스트

```
1. take_snapshot으로 폼 요소 uid 확인
2. fill / fill_form으로 테스트 데이터 입력
3. click으로 제출 버튼 클릭
4. wait_for로 응답 대기
5. list_network_requests로 API 호출 확인
6. 서버 로그에서 요청 처리 확인
7. take_snapshot으로 결과 화면 확인
```

#### 인증 플로우 테스트

```
1. 로그인 페이지 접속
2. 테스트 계정으로 로그인 시도
3. 토큰 발급 확인 (네트워크 요청)
4. 인증 필요 페이지 접근 확인
5. 토큰 만료 시 갱신 동작 확인
```

#### API 연동 테스트

```
1. 기능 페이지 접속
2. 데이터 로드 요청 확인 (네트워크)
3. 서버 로그에서 DB 쿼리 실행 확인
4. 응답 데이터와 화면 표시 일치 확인
5. CRUD 작업 수행 후 서버 로그 및 화면 검증
```

### 6단계: 서버 로그 분석

테스트 중 서버 로그를 주기적으로 확인합니다:

**확인 항목:**
- 예외/스택트레이스 발생 여부
- SQL 쿼리 실행 로그 (N+1 문제 감지)
- API 응답 시간 이상 (3초 이상)
- 메모리/리소스 경고
- 인증/인가 실패 로그

**로그 확인 방법:**
```
# TaskOutput으로 서버 프로세스의 최근 출력 확인 (block=false)
# 오류 패턴 검색: ERROR, Exception, WARN, FATAL
```

### 7단계: 성능 측정 (선택)

사용자가 성능 측정을 요청하거나, 주요 페이지인 경우:

```
1. performance_start_trace (reload=true, autoStop=true)
2. 트레이스 완료 후 결과 분석
3. Core Web Vitals (LCP, FID, CLS) 확인
4. 병목 지점 식별 및 개선 제안
```

### 8단계: 테스트 결과 보고서 생성

`docs/tests/test-reports/`에 테스트 결과를 기록합니다:

```markdown
# 통합 테스트 보고서

## 테스트 환경
- 일시: {날짜}
- 서버: {기술 스택 + 버전}
- 브라우저: Chrome (chrome-devtools MCP)

## 테스트 결과 요약

| 항목 | 결과 | 비고 |
|------|------|------|
| 서버 시작 | PASS/FAIL | |
| 콘솔 에러 | {건수} | |
| 네트워크 실패 | {건수} | |
| 반응형 레이아웃 | PASS/FAIL | |
| 시나리오 테스트 | {통과}/{전체} | |
| 서버 로그 오류 | {건수} | |

## 상세 결과

### 페이지별 검증
{페이지별 결과}

### 시나리오 테스트
{시나리오별 결과}

### 서버 로그 분석
{주요 로그 이슈}

### 발견된 이슈
1. [심각도] {이슈 설명}
   - 발견 위치: {페이지/API}
   - 서버 로그: {관련 로그}
   - 재현 방법: {단계}

## 성능 측정 (수행한 경우)
{Core Web Vitals 결과}
```

### 9단계: 서버 종료

테스트 완료 후 서버 프로세스를 종료합니다:

```
# TaskStop으로 백그라운드 서버 프로세스 종료
# 또는 Ctrl+C 시그널 전송
```

사용자에게 서버 종료 여부를 확인한 후 종료합니다.

## 빠른 실행 예시

```
# 특정 URL 테스트
/astra-integration-test http://localhost:3000

# 특정 시나리오 테스트
/astra-integration-test 로그인 플로우

# 전체 통합 테스트 (test-cases 디렉토리 기반)
/astra-integration-test

# 특정 테스트 케이스 파일 기반
/astra-integration-test docs/tests/test-cases/auth-test-cases.md
```

## 주의사항

- 서버가 이미 실행 중인 경우 중복 실행하지 않습니다. 포트 사용 여부를 먼저 확인합니다.
- `.env` 파일의 민감 정보는 로그에 노출하지 않습니다.
- 테스트 데이터는 테스트 전용 DB/환경에서만 사용합니다.
- 서버 로그에서 개인정보가 포함된 부분은 마스킹 처리합니다.
- 성능 측정은 개발 환경 기준이며, 프로덕션 성능과 차이가 있을 수 있습니다.
- 테스트 완료 후 반드시 서버 프로세스를 종료합니다.
