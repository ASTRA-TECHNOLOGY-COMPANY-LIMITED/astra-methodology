---
name: ai-agent-module
description: "AI 에이전트 플랫폼 모듈을 자동으로 구축합니다. 레퍼런스 설계 문서를 기반으로 블루프린트 작성, 스프린트 생성, 구현, 테스트 시나리오 작성, 테스트 실행 및 디버깅까지 전체 파이프라인을 자동 실행합니다. 멀티 프로바이더 LLM 클라이언트, SSE 스트리밍, 도구/플러그인 시스템, 스킬 시스템, 에이전트 Core Loop(4중 안전장치), RAG/메모리, HITL, 서브에이전트, 모델 라우팅/폴백, 채널 연동 기능을 포함합니다."
argument-hint: "[target-project-path]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Agent
---

# ASTRA AI 에이전트 플랫폼 모듈 자동 구축

레퍼런스 설계 문서(`$CLAUDE_PLUGIN_ROOT/docs/ai-agent/system-design.md`)를 기반으로 대상 프로젝트에 AI 에이전트 플랫폼 모듈 전체를 자동 구축합니다.

**자동 구축 범위**:
- 멀티 프로바이더 LLM 클라이언트 (Anthropic/OpenAI/Ollama — native fetch, SDK 없음)
- SSE 실시간 스트리밍 (토큰 단위 + 도구 호출/결과 + HITL + 서브에이전트)
- Agent Core Loop (executeLoop — 최대 10 iteration, 4중 안전장치)
- Context Building 파이프라인 (10단계 — 프롬프트/스킬/메모리/RAG/히스토리)
- 도구 및 플러그인 시스템 (PLUGIN.md → PluginManager → Handler Registry)
- 스킬 시스템 (GLOBAL/WORKSPACE/Agent 매핑, 온디맨드 + 직접 주입)
- HITL (Human-in-the-Loop — hitl_prompt 도구 + SSE 이벤트 + 루프 중단)
- 메모리 (pgvector flat + Neo4j graph → 하이브리드 랭킹)
- RAG (지식 베이스 + Agentic 쿼리 분류 + HyDE + 리랭킹)
- 서브에이전트 오케스트레이션 (스폰/조정/종료, 깊이/자식 제한)
- 모델 라우팅 (복잡도 기반 SIMPLE/VAGUE/COMPLEX) + 모델 폴백
- 에이전트/대화/메시지 CRUD + 자동 제목 생성 + Compaction
- 시크릿 관리 (AES-256-GCM) + OAuth 플로우
- 채널 연동 (Slack/Teams/Discord 웹훅)
- Gateway 미들웨어 (인증/워크스페이스/크레딧)

## 실행 절차

### Step 0: 사전 준비 및 컨텍스트 수집

#### A. 레퍼런스 설계 문서 로드

`$CLAUDE_PLUGIN_ROOT/docs/ai-agent/system-design.md` 파일을 읽어 레퍼런스 설계 정보를 로드한다:

1. 아키텍처 개요 — Gateway Proxy 패턴, Skill-First 설계, Plugin-Based 도구 (섹션 1)
2. 기술 스택 — Next.js 14, Drizzle ORM, native fetch LLM 클라이언트 (섹션 2)
3. 데이터베이스 스키마 — 24개 테이블 (섹션 3):
   - TB_AI_AGNT_CTGRY (에이전트 카테고리), TB_AI_AGNT (에이전트 정의)
   - TB_AI_CNVRSTN (대화), TH_AI_MSG (메시지 이력)
   - TB_AI_MMRY (메모리 — pgvector)
   - TB_AI_KNWLDG_BS (지식 베이스), TB_AI_KNWLDG_DOC (문서), TB_AI_EMBDNG_CHNK (임베딩 청크)
   - TB_AI_SKILL_DEF (스킬), TR_AI_CNFG_SKILL (에이전트-스킬 매핑)
   - TB_AI_MCP_SRVR (MCP 서버), TR_AI_CNFG_MCP_SRVR (에이전트-MCP 매핑)
   - TB_AI_SBAGNT_RUN (서브에이전트), TL_AI_SBAGNT_LOG (로그)
   - TL_AI_TKN_USG (토큰 사용량)
   - TB_AI_WKSPC_SCRT (시크릿), TB_AI_SYS_CRED (자격 증명), TH_AI_OAUTH_SESSION (OAuth)
   - TL_AI_SCRT_ACCS_LOG (시크릿 접근 로그)
   - TB_AI_CHNL_CNFG (채널), TL_AI_CHNL_MSG_LOG (채널 메시지 로그)
   - TB_AI_PRJCT (프로젝트), TB_AI_SGGSTN_TMPL (제안 템플릿)
   - TL_AI_MCP_SRVR_LOG (MCP 로그)
4. API 설계 — 대화/에이전트/지식/메모리/서브에이전트/시크릿/채널 엔드포인트 (섹션 4)
5. AI 런타임 엔진 — Core Loop, 안전장치, Context Building, 모델 라우팅, 에러 처리 (섹션 5)
6. 도구 및 플러그인 시스템 — 3계층 아키텍처, 실행 파이프라인, HITL (섹션 6)
7. 스킬 시스템 — 3단계 스코프, 활성화 모드, 분류기 (섹션 7)
8. 디렉토리 구조 (섹션 8)
9. 구현 순서 — Phase 1~8 (섹션 9)

> **중요**: 레퍼런스는 **fect-api-agent(Next.js 14 + PostgreSQL + Drizzle ORM)**를 기준으로 작성되었다. 대상 프로젝트의 기술 스택에 맞게 **적응(adapt)**해야 한다.

#### B. 대상 프로젝트 분석

`$ARGUMENTS`에서 대상 프로젝트 경로를 파싱한다. 인자가 없으면 현재 작업 디렉토리를 사용한다.

대상 프로젝트에서 다음을 분석한다:

1. `CLAUDE.md` 읽기 — 기술 스택, 프로젝트 구조, 컨벤션 확인
2. `package.json` 또는 `build.gradle` 또는 `pom.xml` 또는 `pyproject.toml` 읽기 — 프레임워크/의존성 파악
3. `docs/blueprints/` 스캔 — 기존 블루프린트 번호 확인 (다음 번호 결정)
4. `docs/database/database-design.md` 읽기 — 기존 DB 스키마 확인 (특히 인증/워크스페이스 모듈 테이블)
5. `docs/sprints/` 스캔 — `sprint-{N}-{name}/` 패턴 디렉토리에서 현재 스프린트 번호 확인
6. `src/` 스캔 — 기존 코드 구조, 라우팅 패턴, 인증 관련 기존 코드 확인
7. `src/styles/design-tokens.css` + `docs/design-system/` 스캔 — 디자인 토큰, 컴포넌트 패턴 확인

#### C. 선행 모듈 의존성 확인

AI 에이전트 모듈은 **인증 모듈**에 **의존**한다 (Gateway 미들웨어가 인증 토큰을 검증하므로). 다음을 확인한다:

**인증 모듈 (필수)**:
1. TB_COMM_USER 테이블 존재 여부
2. JWT 인증 미들웨어 존재 여부

**워크스페이스 모듈 (필수)**:
1. TB_COMM_WKSPC 테이블 존재 여부
2. TR_COMM_WKSPC_MBR 테이블 존재 여부
3. 워크스페이스 멤버십/역할 검증 미들웨어 존재 여부

**결제 모듈 (선택)**:
1. 크레딧 기반 과금 사용 시 필요
2. TB_PAY_CRDT_BLNC 테이블 존재 여부

선행 모듈이 없는 경우 `AskUserQuestion`으로 사용자에게 알린다:

```
## 선행 모듈 의존성 확인

AI 에이전트 모듈은 인증 모듈(TB_COMM_USER, JWT)과 워크스페이스 모듈(TB_COMM_WKSPC)에 의존합니다.

감지 결과:
- 인증 모듈: {감지됨/미감지}
- 워크스페이스 모듈: {감지됨/미감지}
- 결제 모듈 (선택): {감지됨/미감지}

다음 중 선택해 주세요:
1. 미감지된 모듈을 먼저 구축 (/auth-module, /workspace-module 순서대로 실행)
2. 기존 인증/워크스페이스 시스템이 있으며 경로를 알려주겠음
3. Gateway 없이 독립 실행 모드로 구축 (자체 인증 + 단일 워크스페이스)
```

#### D. 기술 스택 적응 매트릭스

대상 프로젝트의 기술 스택에 따라 레퍼런스 설계를 적응한다:

| 레퍼런스 (fect-api-agent) | 대상 프로젝트 | 적응 방법 |
|--------------------------|------------|----------|
| Next.js 14 API Routes | Spring Boot | `@RestController` + WebFlux (SSE) |
| Next.js 14 API Routes | NestJS | `@Controller` + `@Sse()` |
| Next.js 14 API Routes | FastAPI | `@router` + `StreamingResponse` |
| Next.js 14 API Routes | Next.js | 그대로 사용 |
| Drizzle ORM | JPA/Hibernate | `@Entity` + `@Table` + `@Column` |
| Drizzle ORM | TypeORM | `@Entity` + `@Column` |
| Drizzle ORM | Prisma | `schema.prisma` 모델 |
| Drizzle ORM | SQLAlchemy | `Base` + `Column` |
| native fetch (Anthropic) | Anthropic SDK | `@anthropic-ai/sdk` |
| native fetch (OpenAI) | OpenAI SDK | `openai` 패키지 |
| TransformStream (SSE) | Spring WebFlux | `Flux<ServerSentEvent>` |
| TransformStream (SSE) | NestJS | `Observable<MessageEvent>` |
| TransformStream (SSE) | FastAPI | `EventSourceResponse` |
| pgvector (Node.js) | pgvector (Java) | `com.pgvector` 라이브러리 |
| pgvector (Node.js) | pgvector (Python) | `pgvector-python` 패키지 |

적응이 필요한 경우 `AskUserQuestion`으로 사용자에게 확인한다:

```
## AI 에이전트 모듈 기술 스택 확인

레퍼런스: Next.js 14 + PostgreSQL + Drizzle ORM + native fetch (Anthropic/OpenAI)
대상 프로젝트: {detected-tech-stack}

다음 사항을 확인해 주세요:
1. 서버 프레임워크: {detected} (SSE 스트리밍 방식 결정)
2. ORM: {detected}
3. LLM 프로바이더: Anthropic / OpenAI / 둘 다 / 기타 ({detected})
4. LLM 연동 방식: native fetch / SDK ({recommended})
5. 벡터 DB: pgvector / Pinecone / Qdrant / 기타 ({detected or pgvector 권장})
6. 그래프 DB (선택): Neo4j / 미사용 ({detected})

추가 요구사항이 있으면 알려주세요 (예: 특정 LLM만 지원, Gateway 없이 독립 실행 등).
```

#### E. 기능 모듈 정의

레퍼런스 설계 문서에서 추출한 AI 에이전트 모듈 기능 목록:

| # | 모듈 | 기능 | 주요 구현 |
|---|------|------|----------|
| 1 | 인프라 | DB 스키마 + 리소스 로더 | 24개 테이블, prompts/skills/plugins 파싱 |
| 2 | LLM | 멀티 프로바이더 클라이언트 | Anthropic/OpenAI/Ollama native fetch |
| 3 | 스트리밍 | SSE 핸들러 | createSSEStream, SSEWriter, keep-alive |
| 4 | 런타임 | Agent Core Loop | executeLoop, 4중 안전장치 |
| 5 | 컨텍스트 | Context Builder | 10단계 파이프라인 |
| 6 | 도구 | 플러그인 시스템 | PluginManager, Handler Registry, 20+ 도구 |
| 7 | HITL | Human-in-the-Loop | hitl_prompt + SSE + 루프 중단 |
| 8 | 메모리 | Flat + Graph 메모리 | pgvector + Neo4j 하이브리드 |
| 9 | RAG | 지식 베이스 검색 | Agentic 분류, HyDE, 리랭킹 |
| 10 | 모델 | 라우팅 + 폴백 | 복잡도 분류, 프로바이더 순회 |
| 11 | 서브에이전트 | 오케스트레이션 | 스폰/관리/종료, 깊이 제한 |
| 12 | 스킬 | 스킬 시스템 | Merger, 분류기, 모델 업그레이드 |
| 13 | API | CRUD 엔드포인트 | 대화/에이전트/지식/시크릿/채널 |
| 14 | 미들웨어 | Gateway 통합 | withGatewayAuth/withAiContext/withCredits |
| 15 | 보안 | 시크릿 + OAuth | AES-256-GCM, PKCE OAuth 플로우 |

---

### Step 1: 블루프린트 자동 생성

레퍼런스 설계 문서를 기반으로 AI 에이전트 모듈 블루프린트를 생성한다.

#### A. 블루프린트 번호 결정

`docs/blueprints/` 디렉토리를 스캔하여 기존 블루프린트 번호를 확인하고 다음 번호를 결정한다.

```
NNN = (기존 최대 번호) + 1
```

#### B. AI 에이전트 모듈 블루프린트 생성

`docs/blueprints/{NNN}-ai-agent/blueprint.md` 파일을 생성한다.

레퍼런스 설계 문서의 내용을 대상 프로젝트 기술 스택에 맞게 적응하여 다음 섹션을 포함한다:

```markdown
# AI 에이전트 플랫폼 모듈 설계 문서

## 1. 개요
- 설계 원칙 (레퍼런스 섹션 1.1 적응)
- 아키텍처 다이어그램 (대상 프로젝트에 맞게 수정)
- Gateway 헤더 프로토콜 (레퍼런스 섹션 1.3)
- 타 모듈과의 관계 (레퍼런스 섹션 1.4)

## 2. 기술 스택
- 핵심 의존성 (레퍼런스 섹션 2.1 적응)
- LLM 프로바이더 설정 (레퍼런스 섹션 2.2 적응)
- 환경 변수 (레퍼런스 섹션 2.4 적응 — 실제 값은 placeholder로)

## 3. 데이터베이스 스키마
- ER 다이어그램 (레퍼런스 섹션 3.1)
- 테이블 정의 — 24개 테이블 (레퍼런스 섹션 3.2~3.14 적응)
- DDL (대상 DB에 맞게 변환)
- ORM 스키마 정의 (대상 ORM에 맞게 변환)

## 4. API 설계
- 미들웨어 체인 (레퍼런스 섹션 4.1)
- 엔드포인트 목록 (레퍼런스 섹션 4.2)
- SSE 이벤트 프로토콜 (레퍼런스 섹션 4.4)
- 에러 응답 형식 (레퍼런스 섹션 4.5)

## 5. AI 런타임 엔진
- Core Loop (레퍼런스 섹션 5.1)
- 4중 안전장치 (레퍼런스 섹션 5.2)
- Context Building (레퍼런스 섹션 5.3)
- 모델 라우팅 + 폴백 (레퍼런스 섹션 5.5~5.7)

## 6. 도구 및 플러그인 시스템
- Plugin 아키텍처 (레퍼런스 섹션 6.1)
- 도구 실행 파이프라인 (레퍼런스 섹션 6.2)
- HITL 상세 (레퍼런스 섹션 6.6)

## 7. 스킬 시스템
- 스킬 스코프 (레퍼런스 섹션 7.1)
- 스킬 활성화 모드 (레퍼런스 섹션 7.3)

## 8. 디렉토리 구조
- 신규 추가 파일 목록 (대상 프로젝트 구조에 맞게)

## 9. 구현 순서
- Phase 1~8 (레퍼런스 섹션 9)
```

> **참고**: 레퍼런스 설계 문서의 모든 섹션을 빠짐없이 반영한다. 기술 스택만 대상 프로젝트에 맞게 변환하고, AI 런타임 로직과 안전장치 설계는 원본을 최대한 유지한다.

#### C. DB 설계 문서 반영

`docs/database/database-design.md`에 AI 에이전트 모듈 테이블을 추가한다:

1. 레퍼런스의 24개 테이블을 추가
2. ER 다이어그램 업데이트
3. FK 관계 요약 업데이트 (TB_COMM_USER, TB_COMM_WKSPC와의 관계)
4. 공공 데이터 표준 네이밍 규칙 준수 확인

#### D. 블루프린트 생성 완료 보고

```
## Step 1 완료: 블루프린트 생성

### 생성된 파일
- docs/blueprints/{NNN}-ai-agent/blueprint.md (AI 에이전트 모듈 설계 문서)
- docs/database/database-design.md (DB 테이블 24개 추가)

### 포함된 기능
- AI 런타임 엔진 (Core Loop + 4중 안전장치)
- 멀티 프로바이더 LLM 클라이언트 (Anthropic/OpenAI/Ollama)
- SSE 스트리밍 (20+ 이벤트 타입)
- 도구/플러그인 시스템 (20+ 내장 도구)
- 스킬 시스템 (3단계 스코프)
- HITL + 서브에이전트 + 메모리 + RAG

Step 2로 진행합니다...
```

---

### Step 2: 스프린트 계획 자동 생성

블루프린트의 구현 순서(Phase 1~8)를 기반으로 스프린트 프롬프트 맵을 생성한다.

#### A. 스프린트 번호 결정

`docs/sprints/` 디렉토리에서 `sprint-{N}-{name}/` 패턴 디렉토리를 스캔하여 다음 스프린트 번호를 결정한다.

#### B. 스프린트 프롬프트 맵 생성

`docs/sprints/sprint-{N}-ai-agent/prompt-map.md`를 생성한다.

레퍼런스의 Phase를 스프린트 Feature 단위로 분할한다:

```markdown
# Sprint {N} Prompt Map

## Sprint Goal
AI 에이전트 플랫폼 모듈 전체 구축 — 멀티 프로바이더 LLM, SSE 스트리밍, Core Loop, 도구/스킬 시스템, HITL, 메모리/RAG, 서브에이전트

## Feature 1: 기반 인프라 (Phase 1)

### 1.1 Design Prompt
(Already completed — see docs/blueprints/{NNN}-ai-agent/blueprint.md 섹션 2~3)

### 1.2 DB Design Reflection Prompt
/feature-dev "docs/blueprints/{NNN}-ai-agent/blueprint.md 섹션 3의 DDL을 기반으로
docs/database/database-design.md에 AI 에이전트 모듈 테이블 24개를 추가/업데이트한다.
ER 다이어그램과 FK 관계도 반영한다. pgvector 확장 설치도 포함. 코드 수정 없음."

### 1.3 Test Case Prompt
/feature-dev "docs/blueprints/{NNN}-ai-agent/blueprint.md를 기반으로
docs/tests/test-cases/sprint-{N}/ai-infra-test-cases.md에
DB 스키마 검증, 리소스 로더 파싱, 환경 변수 검증 테스트 케이스를 작성한다. 코드 수정 없음."

### 1.4 Implementation Prompt
/feature-dev "docs/blueprints/{NNN}-ai-agent/blueprint.md Phase 1을 참조하여
기반 인프라를 구현한다:
- 의존성 설치, 환경 변수 설정
- Drizzle ORM 설정 및 DB 스키마 정의 (24개 테이블)
- DB 마이그레이션 (pgvector 확장 포함)
- 리소스 로더 (prompts, skills, plugins YAML 파싱)
- 싱글톤 초기화 (instrumentation.ts)
테스트 실행 후 결과를 docs/tests/test-reports/에 기록한다."

## Feature 2: AI 런타임 코어 (Phase 2)

### 2.1 Design Prompt
(Already completed — see docs/blueprints/{NNN}-ai-agent/blueprint.md 섹션 5)

### 2.2 Test Case Prompt
/feature-dev "docs/blueprints/{NNN}-ai-agent/blueprint.md 섹션 5를 기반으로
docs/tests/test-cases/sprint-{N}/ai-runtime-test-cases.md에
LLM 클라이언트(Anthropic/OpenAI 호출/스트리밍), SSE 이벤트 시퀀스,
Core Loop(도구 호출/HITL 중단/안전장치), Context Builder 테스트 케이스를 작성한다. 코드 수정 없음."

### 2.3 Implementation Prompt
/feature-dev "docs/blueprints/{NNN}-ai-agent/blueprint.md Phase 2를 참조하여 구현:
- LLM 클라이언트 (native fetch — Anthropic Messages API, OpenAI Chat Completions)
  - Anthropic: prompt caching, extended thinking, tool_use content blocks
  - OpenAI: tool_calls 포맷
  - 스트리밍: AsyncGenerator<StreamDelta>
- SSE 스트림 핸들러 (createSSEStream, SSEWriter, 15초 keep-alive)
- Agent Runner Core Loop (executeLoop — 최대 10 iteration)
- Context Builder (10단계 파이프라인)
- 4중 안전장치:
  - LoopGuard (3규칙: 연속 반복, 동일 도구, 주기 패턴)
  - ToolContextTracker (중복 도구 호출 방지)
  - WorkflowGuard (필수 도구 강제)
  - ContextGuard (토큰 예산 보호 + compaction)
테스트 실행 후 결과를 docs/tests/test-reports/에 기록한다."

## Feature 3: 도구 및 플러그인 시스템 (Phase 3)

### 3.1 Design Prompt
(Already completed — see docs/blueprints/{NNN}-ai-agent/blueprint.md 섹션 6)

### 3.2 Test Case Prompt
/feature-dev "docs/blueprints/{NNN}-ai-agent/blueprint.md 섹션 6을 기반으로
docs/tests/test-cases/sprint-{N}/ai-tools-test-cases.md에
PluginManager 초기화, 도구 해석/실행, HITL 이벤트/루프 중단,
핵심 도구 (calculator, datetime, memory) 테스트 케이스를 작성한다. 코드 수정 없음."

### 3.3 Implementation Prompt
/feature-dev "docs/blueprints/{NNN}-ai-agent/blueprint.md Phase 3을 참조하여 구현:
- Plugin Manager (싱글톤 — PLUGIN.md 로드, 핸들러 바인딩, ToolRegistry)
- Handler Registry (도구 코드 → 핸들러 함수 매핑)
- Tool Resolver (enblToolCds + skill allowed-tools → OpenAI Tool[] 포맷)
- Tool Dispatcher (30초 타임아웃, ToolExecutionContext)
- 핵심 도구 핸들러:
  - calculator (재귀하강 파서)
  - datetime
  - web_search
  - memory_save / memory_search (pgvector)
  - hitl_prompt (SSE hitl_question 이벤트 + 루프 중단)
  - skill_get (온디맨드 스킬 fetch)
테스트 실행 후 결과를 docs/tests/test-reports/에 기록한다."

## Feature 4: 에이전트 설정 + 지식 베이스 (Phase 4)

### 4.1 Design Prompt
(Already completed — see docs/blueprints/{NNN}-ai-agent/blueprint.md 섹션 4.2, 5.4)

### 4.2 Test Case Prompt
/feature-dev "docs/blueprints/{NNN}-ai-agent/blueprint.md 섹션 4.2를 기반으로
docs/tests/test-cases/sprint-{N}/ai-config-kb-test-cases.md에
에이전트 CRUD, 스킬 매핑, 지식 베이스 CRUD, 문서 업로드/청크,
RAG 검색 (SIMPLE/VAGUE/COMPLEX), 메모리 하이브리드 랭킹 테스트 케이스를 작성한다. 코드 수정 없음."

### 4.3 Implementation Prompt
/feature-dev "docs/blueprints/{NNN}-ai-agent/blueprint.md Phase 4를 참조하여 구현:
- 에이전트 CRUD API (카테고리, 에이전트 설정, 스킬 매핑, MCP 서버 매핑)
- 지식 베이스 CRUD + 문서 업로드 (multipart) + 청크 생성 (pgvector 임베딩)
- RAG 서비스:
  - 쿼리 분류기 (SIMPLE/VAGUE/COMPLEX)
  - HyDE 의사 문서 생성 (VAGUE 쿼리용)
  - Agentic 쿼리 분해 (COMPLEX 쿼리용)
  - 리랭킹 (선택)
- 메모리 서비스 (pgvector flat + Neo4j graph)
- 통합 메모리 컨텍스트 (하이브리드 랭킹 — top_k=10)
테스트 실행 후 결과를 docs/tests/test-reports/에 기록한다."

## Feature 5: 모델 라우팅 + 서브에이전트 (Phase 5)

### 5.1 Design Prompt
(Already completed — see docs/blueprints/{NNN}-ai-agent/blueprint.md 섹션 5.5~5.7)

### 5.2 Test Case Prompt
/feature-dev "docs/blueprints/{NNN}-ai-agent/blueprint.md 섹션 5.5~5.7을 기반으로
docs/tests/test-cases/sprint-{N}/ai-routing-subagent-test-cases.md에
모델 라우팅 (복잡도 분류), 폴백 (프로바이더 전환), 에러 분류/재시도,
서브에이전트 (스폰/관리/킬, 깊이 제한) 테스트 케이스를 작성한다. 코드 수정 없음."

### 5.3 Implementation Prompt
/feature-dev "docs/blueprints/{NNN}-ai-agent/blueprint.md Phase 5를 참조하여 구현:
- 모델 라우터 (classifyQueryComplexity → SIMPLE/VAGUE/COMPLEX → 모델 선택)
- Skill-Triggered 모델 업그레이드 (skill_get 호출 시 COMPLEX 모델로)
- 모델 폴백 (fallbackModels[] 순회 — AUTH 에러 건너뜀)
- 에러 분류기 (AUTH/RATE_LIMIT/CONTEXT_OVERFLOW/TIMEOUT/SERVER/NETWORK)
- 재시도 전략 (exponential backoff — base 1s, max 30s, factor 2)
- 서브에이전트 스폰 검증 (깊이 3, 자식 3, 화이트리스트)
- 서브에이전트 CRUD API + SSE 이벤트 (spawned/completed/failed/killed)
테스트 실행 후 결과를 docs/tests/test-reports/에 기록한다."

## Feature 6: 미들웨어 + 시크릿 + OAuth (Phase 6)

### 6.1 Design Prompt
(Already completed — see docs/blueprints/{NNN}-ai-agent/blueprint.md 섹션 4.1, 3.12, 3.13)

### 6.2 Test Case Prompt
/feature-dev "docs/blueprints/{NNN}-ai-agent/blueprint.md 섹션 4.1, 3.12를 기반으로
docs/tests/test-cases/sprint-{N}/ai-middleware-secret-test-cases.md에
Gateway 미들웨어 (인증/컨텍스트/크레딧), 시크릿 관리 (AES-256-GCM),
OAuth 플로우 (PKCE), 채널 웹훅 테스트 케이스를 작성한다. 코드 수정 없음."

### 6.3 Implementation Prompt
/feature-dev "docs/blueprints/{NNN}-ai-agent/blueprint.md Phase 6을 참조하여 구현:
- withGatewayAuth (X-User-id, X-Workspace-id 등 헤더 파싱/검증)
- withAiContext (워크스페이스 ACTIVE 검증, 로케일 결정)
- withCredits (크레딧 잔여 확인 — -1=무제한, ≤0=402)
- 워크스페이스 시크릿 관리 (AES-256-GCM 암호화/복호화)
- 시크릿 접근 감사 로그 (TL_AI_SCRT_ACCS_LOG)
- 시스템 자격 증명 CRUD + OAuth 플로우 (initiate/callback/exchange — PKCE)
- 채널 설정 CRUD + 웹훅 수신 (Slack/Teams — 서명 검증)
테스트 실행 후 결과를 docs/tests/test-reports/에 기록한다."

## Feature 7: 스킬 시스템 + 대화 관리 (Phase 7)

### 7.1 Design Prompt
(Already completed — see docs/blueprints/{NNN}-ai-agent/blueprint.md 섹션 7)

### 7.2 Test Case Prompt
/feature-dev "docs/blueprints/{NNN}-ai-agent/blueprint.md 섹션 7을 기반으로
docs/tests/test-cases/sprint-{N}/ai-skill-conv-test-cases.md에
Skill Merger (GLOBAL+WORKSPACE+Agent), 스킬 분류기, 대화 CRUD,
Compaction, 자동 제목 생성, 메모리 자동 추출 테스트 케이스를 작성한다. 코드 수정 없음."

### 7.3 Implementation Prompt
/feature-dev "docs/blueprints/{NNN}-ai-agent/blueprint.md Phase 7을 참조하여 구현:
- Skill Merger (GLOBAL + WORKSPACE → Agent 매핑 필터 — 화이트리스트)
- 스킬 분류기 (사용자 쿼리 → 스킬 카탈로그 매칭 → 자동 주입)
- Skill-Triggered 모델 업그레이드 (skill_get → COMPLEX 모델)
- 대화 CRUD (생성/목록/수정/삭제/고정)
- 메시지 페이징 (커서 기반 — MSG_SN 순서)
- 대화 Compaction (80% 토큰 → 이전 메시지 요약 → smryCn 저장)
- 자동 제목 생성 (첫 메시지 후 비동기 LLM 호출)
- 메모리 자동 추출 (MIN_MESSAGES_FOR_EXTRACTION=4, MIN_TURNS_BETWEEN=3)
테스트 실행 후 결과를 docs/tests/test-reports/에 기록한다."

## Feature 8: 통합 및 최적화 (Phase 8)

### 8.1 Design Prompt
(Already completed — see docs/blueprints/{NNN}-ai-agent/blueprint.md 섹션 5.6, 부록)

### 8.2 Test Case Prompt
/feature-dev "docs/blueprints/{NNN}-ai-agent/blueprint.md 섹션 5.6, 부록을 기반으로
docs/tests/test-cases/sprint-{N}/ai-integration-test-cases.md에
Anthropic Prompt Caching, Extended Thinking, 토큰 사용량 로깅,
MCP 서버 스키마 캐싱, 크론 서비스, UI 액션 통합 테스트를 작성한다. 코드 수정 없음."

### 8.3 Implementation Prompt
/feature-dev "docs/blueprints/{NNN}-ai-agent/blueprint.md Phase 8을 참조하여 구현:
- Anthropic Prompt Caching (cache_control on system messages)
- Extended Thinking 모드
- 토큰 사용량 로깅 (TL_AI_TKN_USG) + 포탈 비동기 리포팅
- MCP 서버 등록 + 도구 스키마 캐싱 (tool_schma_cache JSONB)
- 크론 서비스 (PostgreSQL 분산 스케줄러)
- UI 액션 처리 (POST /conversations/[convId]/ui-actions)
- 전체 통합 테스트 (메시지 전송 → SSE 스트리밍 → 도구 호출 → 응답)
테스트 실행 후 결과를 docs/tests/test-reports/에 기록한다."
```

#### C. 스프린트 프로그레스 트래커 생성

`docs/sprints/sprint-{N}-ai-agent/progress.md`를 생성한다:

```markdown
# Sprint {N} Progress Tracker

## Sprint Information
- **Sprint Number**: {N}
- **Sprint Goal**: AI 에이전트 플랫폼 모듈 전체 구축
- **Start Date**: {TODAY}
- **End Date**: {TODAY + 7 days}
- **Status**: In Progress

<!-- PROGRESS_TABLE_START -->
## Feature Progress

| Feature | Blueprint | DB Design | Test Cases | Implementation | Test Report | Status |
|---------|-----------|-----------|------------|----------------|-------------|--------|
| 기반 인프라 | Done | - | - | - | - | Not Started |
| AI 런타임 코어 | Done | Done | - | - | - | Not Started |
| 도구/플러그인 시스템 | Done | N/A | - | - | - | Not Started |
| 에이전트 설정 + 지식 베이스 | Done | Done | - | - | - | Not Started |
| 모델 라우팅 + 서브에이전트 | Done | Done | - | - | - | Not Started |
| 미들웨어 + 시크릿 + OAuth | Done | Done | - | - | - | Not Started |
| 스킬 시스템 + 대화 관리 | Done | Done | - | - | - | Not Started |
| 통합 및 최적화 | Done | N/A | - | - | - | Not Started |

**Legend**: `-` Not Started, `WIP` In Progress, `Done` Completed, `N/A` Not Applicable
<!-- PROGRESS_TABLE_END -->

<!-- SUMMARY_START -->
## Summary
- **Total Features**: 8
- **Completed**: 0
- **In Progress**: 0
- **Overall Progress**: 0%
- **Last Updated**: {TIMESTAMP}
<!-- SUMMARY_END -->

<!-- ACTIVITY_LOG_START -->
## Activity Log

| Timestamp | Event | File | Details |
|-----------|-------|------|---------|
| {TIMESTAMP} | blueprint | docs/blueprints/{NNN}-ai-agent/blueprint.md | AI 에이전트 모듈 블루프린트 생성 |
| {TIMESTAMP} | db-design | docs/database/database-design.md | AI 에이전트 테이블 24개 추가 |
<!-- ACTIVITY_LOG_END -->
```

#### D. 스프린트 계획 완료 보고

```
## Step 2 완료: 스프린트 계획 생성

### 생성된 파일
- docs/sprints/sprint-{N}-ai-agent/prompt-map.md (프롬프트 맵)
- docs/sprints/sprint-{N}-ai-agent/progress.md (프로그레스 트래커)

### 스프린트 구조
- Feature 1: 기반 인프라 (DB 스키마 24개 + 리소스 로더)
- Feature 2: AI 런타임 코어 (LLM 클라이언트 + SSE + Core Loop + 안전장치)
- Feature 3: 도구/플러그인 시스템 (PluginManager + 20+ 도구 + HITL)
- Feature 4: 에이전트 설정 + 지식 베이스 (CRUD + RAG + 메모리)
- Feature 5: 모델 라우팅 + 서브에이전트 (복잡도 분류 + 폴백 + 오케스트레이션)
- Feature 6: 미들웨어 + 시크릿 + OAuth (Gateway 통합 + AES-256 + PKCE)
- Feature 7: 스킬 시스템 + 대화 관리 (Merger + 분류기 + Compaction)
- Feature 8: 통합 및 최적화 (Prompt Caching + Extended Thinking + 토큰 로깅)

Step 3으로 진행합니다...
```

---

### Step 3: 구현 자동 실행

스프린트 프롬프트 맵의 각 Feature를 순서대로 구현한다.

#### A. Feature별 구현 순서

각 Feature에 대해 다음 순서로 진행한다:

1. **테스트 케이스 작성** — 프롬프트 맵의 Test Case Prompt 실행
2. **구현** — 프롬프트 맵의 Implementation Prompt 실행
3. **프로그레스 업데이트** — progress.md 테이블 갱신

#### B. Feature 1: 기반 인프라 구현

레퍼런스 Phase 1에 해당하는 작업을 실행한다:

1. **의존성 설치** — 프로젝트 패키지 매니저로 필요 패키지 설치
2. **환경 변수 템플릿** — `.env.example`에 AI 에이전트 관련 환경 변수 추가
3. **DB 클라이언트 설정** — Drizzle ORM 초기화 및 연결 (싱글톤)
4. **DB 스키마 정의** — 레퍼런스의 Drizzle 스키마를 대상 ORM으로 변환하여 작성
   - 에이전트 (TB_AI_AGNT, TB_AI_AGNT_CTGRY)
   - 대화/메시지 (TB_AI_CNVRSTN, TH_AI_MSG)
   - 메모리 (TB_AI_MMRY — pgvector 1536-dim)
   - 지식 베이스 (TB_AI_KNWLDG_BS, TB_AI_KNWLDG_DOC, TB_AI_EMBDNG_CHNK)
   - 스킬 (TB_AI_SKILL_DEF, TR_AI_CNFG_SKILL)
   - MCP (TB_AI_MCP_SRVR, TR_AI_CNFG_MCP_SRVR)
   - 서브에이전트 (TB_AI_SBAGNT_RUN, TL_AI_SBAGNT_LOG)
   - 토큰 (TL_AI_TKN_USG)
   - 시크릿 (TB_AI_WKSPC_SCRT, TB_AI_SYS_CRED, TH_AI_OAUTH_SESSION)
   - 채널 (TB_AI_CHNL_CNFG, TL_AI_CHNL_MSG_LOG)
   - 프로젝트 (TB_AI_PRJCT)
   - 로그 (TL_AI_SCRT_ACCS_LOG, TL_AI_CHNL_MSG_LOG, TL_AI_MCP_SRVR_LOG)
   - 제안 (TB_AI_SGGSTN_TMPL)
5. **DB 마이그레이션** — pgvector 확장 설치 + 마이그레이션 파일 생성/실행
6. **리소스 로더** — `resources/` 디렉토리에서 prompts/skills/plugins YAML 파싱 → 메모리 캐시
7. **서버 초기화** — `instrumentation.ts`에서 리소스 로드 + PluginManager 초기화

#### C. Feature 2: AI 런타임 코어 구현

레퍼런스 Phase 2에 해당하는 작업을 실행한다:

1. **LLM 클라이언트** — native fetch로 Anthropic/OpenAI API 호출
   - Anthropic: `/v1/messages` + prompt caching + extended thinking + tool_use
   - OpenAI: `/v1/chat/completions` + tool_calls
   - 스트리밍: `AsyncGenerator<StreamDelta>` 반환
   - Ollama: `/api/chat` (도구 미지원)
2. **SSE 스트림 핸들러** — `createSSEStream()`, `SSEWriter.write()`, 15초 keep-alive
3. **Agent Runner** — `runAgentStream()` + `executeLoop()` (최대 10 iteration)
4. **Context Builder** — 10단계 파이프라인 (시스템 프롬프트 → 스킬 → 메모리 → RAG → 히스토리)
5. **LoopGuard** — 3규칙 (연속 반복 3회, 동일 도구 5회, 주기 패턴)
6. **ToolContextTracker** — 도구 호출 기록 + 중복 방지 요약 주입
7. **WorkflowGuard** — required-tools 추적 + 넛지 + tool_choice 강제
8. **ContextGuard** — 토큰 예산 80% 초과 시 compaction 트리거

#### D. Feature 3: 도구/플러그인 시스템 구현

레퍼런스 Phase 3에 해당하는 작업을 실행한다:

1. **Plugin Manager** — PLUGIN.md 로드, 핸들러 바인딩, ToolRegistry (싱글톤)
2. **Handler Registry** — 도구 코드→핸들러 매핑
3. **Tool Resolver** — enblToolCds + skill allowed-tools → OpenAI Tool[] 포맷
4. **Tool Dispatcher** — dispatch(toolName, args, context), 30초 타임아웃
5. **핵심 도구 구현**:
   - `calculator` — 재귀하강 파서 (사칙연산 + 괄호)
   - `datetime` — 현재 시간, 시간대 변환
   - `web_search` — 웹 검색 API 래퍼
   - `memory_save` / `memory_search` — pgvector 임베딩 저장/검색
   - `hitl_prompt` — 입력 검증, SSE hitl_question 이벤트 발행, executeLoop 중단
   - `skill_get` — 온디맨드 스킬 XML 카탈로그에서 fetch
   - `skill_create` / `skill_update` / `skill_delete` — 워크스페이스 스킬 CRUD

#### E. Feature 4: 에이전트 설정 + 지식 베이스 구현

레퍼런스 Phase 4에 해당하는 작업을 실행한다:

1. **에이전트 CRUD API** — 카테고리, 에이전트, 설정, 스킬 매핑, MCP 매핑
2. **지식 베이스 CRUD** + 문서 업로드 (multipart/form-data)
3. **문서 처리** — 텍스트 추출 → 청크 분할 → 임베딩 생성 → TB_AI_EMBDNG_CHNK 저장
4. **RAG 서비스** — Agentic 쿼리 분류 + HyDE + 쿼리 분해 + 리랭킹
5. **메모리 서비스** — pgvector flat search + Neo4j graph search (선택) → 하이브리드 랭킹

#### F. Feature 5: 모델 라우팅 + 서브에이전트 구현

레퍼런스 Phase 5에 해당하는 작업을 실행한다:

1. **모델 라우터** — classifyQueryComplexity → SIMPLE/VAGUE/COMPLEX → 모델 선택
2. **모델 폴백** — fallbackModels[] 순회 (AUTH 에러 건너뜀)
3. **에러 분류기** — 6종 (AUTH/RATE_LIMIT/CONTEXT_OVERFLOW/TIMEOUT/SERVER/NETWORK)
4. **재시도** — exponential backoff (base 1s, max 30s, factor 2, max 2회)
5. **서브에이전트** — 스폰 검증 (깊이 ≤ 3, 자식 ≤ 3, 화이트리스트) + 실행 + SSE 이벤트

#### G. Feature 6: 미들웨어 + 시크릿 + OAuth 구현

레퍼런스 Phase 6에 해당하는 작업을 실행한다:

1. **withGatewayAuth** — Gateway 헤더 파싱/검증 미들웨어
2. **withAiContext** — 워크스페이스 ACTIVE 검증, 로케일
3. **withCredits** — 크레딧 확인 (-1=무제한, ≤0=402)
4. **시크릿 관리** — AES-256-GCM 암호화/복호화 + 감사 로그
5. **OAuth** — initiate (PKCE state+verifier) → callback → exchange → 토큰 저장
6. **채널** — 설정 CRUD + Slack/Teams 웹훅 수신 (서명 검증)

#### H. Feature 7: 스킬 시스템 + 대화 관리 구현

레퍼런스 Phase 7에 해당하는 작업을 실행한다:

1. **Skill Merger** — GLOBAL → WORKSPACE 오버라이드 → Agent 매핑 화이트리스트
2. **스킬 분류기** — 사용자 쿼리 vs 스킬 카탈로그 매칭 → 자동 주입
3. **대화 CRUD** — 생성/목록/수정/삭제/고정 + 커서 기반 메시지 페이징
4. **Compaction** — 토큰 80% 초과 시 이전 메시지 요약 → smryCn 저장
5. **자동 제목 생성** — 첫 메시지 후 비동기 LLM 호출
6. **메모리 자동 추출** — 4+ 메시지, 3+ 턴 간격 조건 충족 시

#### I. Feature 8: 통합 및 최적화 구현

레퍼런스 Phase 8에 해당하는 작업을 실행한다:

1. **Anthropic Prompt Caching** — 시스템 메시지에 cache_control 적용
2. **Extended Thinking** — Anthropic thinking_type 모드
3. **토큰 로깅** — TL_AI_TKN_USG 기록 + 포탈 비동기 리포팅
4. **MCP 서버** — 등록 + 도구 스키마 캐싱
5. **크론 서비스** — PostgreSQL 분산 스케줄러
6. **UI 액션** — POST /conversations/[convId]/ui-actions

#### J. 구현 완료 보고

```
## Step 3 완료: 구현

### 구현된 Feature
| Feature | 파일 수 | 상태 |
|---------|---------|------|
| 기반 인프라 | {N}개 | Done |
| AI 런타임 코어 | {N}개 | Done |
| 도구/플러그인 시스템 | {N}개 | Done |
| 에이전트 설정 + 지식 베이스 | {N}개 | Done |
| 모델 라우팅 + 서브에이전트 | {N}개 | Done |
| 미들웨어 + 시크릿 + OAuth | {N}개 | Done |
| 스킬 시스템 + 대화 관리 | {N}개 | Done |
| 통합 및 최적화 | {N}개 | Done |

Step 4로 진행합니다...
```

---

### Step 4: 테스트 시나리오 자동 생성

구현된 AI 에이전트 모듈에 대해 종합적인 E2E 테스트 시나리오를 생성한다.

#### A. 테스트 시나리오 생성

`Agent` 도구를 사용하여 `/test-scenario ai-agent` 스킬과 동일한 방식으로 테스트 시나리오를 생성한다.

생성할 시나리오 파일:

1. `docs/tests/test-cases/sprint-{N}/ai-runtime-e2e-scenarios.md` — AI 런타임 E2E
2. `docs/tests/test-cases/sprint-{N}/ai-tools-e2e-scenarios.md` — 도구/플러그인 E2E
3. `docs/tests/test-cases/sprint-{N}/ai-agent-config-e2e-scenarios.md` — 에이전트 설정 E2E
4. `docs/tests/test-cases/sprint-{N}/ai-knowledge-e2e-scenarios.md` — 지식 베이스/RAG E2E

#### B. 시나리오 그룹 구성

**AI 런타임 시나리오**:
| 그룹 | 시나리오 유형 |
|------|------------|
| 메시지 전송 | Happy: 단순 텍스트, 첨부 파일 / Error: 빈 메시지, 비활성 대화 / Edge: 동시 전송 |
| SSE 스트리밍 | Happy: 완전한 이벤트 시퀀스 / Error: 클라이언트 연결 끊김 / Edge: 장시간 스트리밍 |
| 도구 호출 루프 | Happy: 단일 도구, 다중 도구 / Error: 도구 타임아웃 / Edge: 10 iteration 도달 |
| 안전장치 | Happy: LoopGuard soft 경고 → 패턴 수정 / Error: hard stop / Edge: WorkflowGuard 재시도 |
| 모델 폴백 | Happy: rate limit → 다른 프로바이더 / Error: AUTH → 즉시 실패 / Edge: 모든 프로바이더 실패 |

**도구/플러그인 시나리오**:
| 그룹 | 시나리오 유형 |
|------|------------|
| HITL | Happy: 옵션 선택, 텍스트 입력 / Error: 잘못된 options 수 / Edge: 다중 선택 |
| 메모리 | Happy: 저장+검색 / Error: 빈 임베딩 / Edge: 중복 저장 |
| 계산기 | Happy: 사칙연산, 괄호 / Error: 잘못된 수식 |
| 스킬 CRUD | Happy: 생성/조회/수정/삭제 / Error: 미존재 스킬 |

**에이전트 설정 시나리오**:
| 그룹 | 시나리오 유형 |
|------|------------|
| 에이전트 CRUD | Happy: 생성/수정/비활성화 / Error: 중복 코드 |
| 스킬 매핑 | Happy: 매핑 추가/제거 / Error: 미존재 스킬명 |
| MCP 서버 | Happy: 등록/스키마 캐싱 / Error: 연결 실패 |

**지식 베이스 시나리오**:
| 그룹 | 시나리오 유형 |
|------|------------|
| 문서 업로드 | Happy: PDF/TXT/MD 업로드 → 청크 생성 / Error: 지원하지 않는 형식 |
| RAG 검색 | Happy: SIMPLE/VAGUE/COMPLEX 각각 / Error: 빈 지식 베이스 |
| 하이브리드 메모리 | Happy: flat+graph 통합 검색 / Edge: Neo4j 미연결 시 flat만 |

#### C. 시나리오 생성 완료 보고

```
## Step 4 완료: 테스트 시나리오 생성

### 생성된 파일
- docs/tests/test-cases/sprint-{N}/ai-runtime-e2e-scenarios.md ({N}개 시나리오)
- docs/tests/test-cases/sprint-{N}/ai-tools-e2e-scenarios.md ({N}개 시나리오)
- docs/tests/test-cases/sprint-{N}/ai-agent-config-e2e-scenarios.md ({N}개 시나리오)
- docs/tests/test-cases/sprint-{N}/ai-knowledge-e2e-scenarios.md ({N}개 시나리오)

### 시나리오 통계
| Type | Runtime | Tools | Config | Knowledge | Total |
|------|---------|-------|--------|-----------|-------|
| Happy Path | {n} | {n} | {n} | {n} | {n} |
| Error Path | {n} | {n} | {n} | {n} | {n} |
| Edge Case | {n} | {n} | {n} | {n} | {n} |
| **Total** | **{n}** | **{n}** | **{n}** | **{n}** | **{n}** |

Step 5로 진행합니다...
```

---

### Step 5: 테스트 실행 및 디버깅

#### A. 유닛/통합 테스트 실행

프로젝트의 테스트 프레임워크를 자동 감지하여 테스트를 실행한다:

| 프레임워크 | 명령어 |
|-----------|-------|
| Jest | `npx jest --coverage --passWithNoTests` |
| Vitest | `npx vitest run --coverage` |
| JUnit | `./gradlew test` 또는 `mvn test` |
| pytest | `python -m pytest --cov` |

```bash
# 테스트 실행 및 결과 수집
{TEST_COMMAND} 2>&1
```

#### B. 서버 기동 및 E2E 테스트

1. **서버 기동** — 프로젝트의 개발 서버를 백그라운드로 실행
2. **서버 준비 대기** — 헬스체크 엔드포인트 또는 포트 확인
3. **API 테스트** — `curl`로 핵심 엔드포인트 테스트:
   - `GET /api/agent/v1/ai/agents` → 200 (에이전트 목록)
   - `POST /api/agent/v1/ai/conversations` → 201 (대화 생성)
   - `POST /api/agent/v1/ai/conversations/[id]/messages` → SSE 스트리밍 확인
   - `GET /api/agent/v1/ai/knowledge-bases` → 200 (지식 베이스 목록)
   - `GET /api/agent/v1/ai/memories` → 200 (메모리 검색)
4. **SSE 스트리밍 검증** — 이벤트 시퀀스 확인:
   - `message_start` → `content_delta`+ → `message_end` → `done`
5. **도구 호출 검증** — 도구 사용을 유도하는 메시지로 테스트:
   - "3 + 5 * 2를 계산해줘" → `tool_call_start(calculator)` → `tool_call_result`
6. **HITL 검증** — HITL 도구를 포함한 스킬 실행:
   - `hitl_question` 이벤트 발행 확인

#### C. 디버깅 자동화

테스트 실패 시 다음 디버깅 사이클을 자동으로 수행한다:

```
반복 (최대 5회):
  1. 실패한 테스트 / 에러 로그 분석
  2. 원인 파악 (컴파일 에러, 런타임 에러, 로직 에러)
  3. 수정 코드 작성 및 적용
  4. 테스트 재실행
  5. 성공 시 → 사이클 종료
  6. 실패 시 → 1로 돌아감
```

5회 반복 후에도 실패하면 `AskUserQuestion`으로 사용자에게 도움을 요청한다:

```
## 테스트 디버깅 지원 요청

다음 테스트가 {N}회 시도 후에도 실패합니다:

### 실패 테스트
- {test-name}: {error-message}

### 시도한 수정
1. {attempt-1}
2. {attempt-2}
...

### 필요한 정보
- {question-1}
```

#### D. 테스트 보고서 생성

`docs/tests/test-reports/sprint-{N}/ai-agent-test-report.md`를 생성한다:

```markdown
# AI 에이전트 모듈 테스트 보고서

## 테스트 결과 요약
| 테스트 스위트 | Pass | Fail | Skip | Total |
|-------------|------|------|------|-------|
| 기반 인프라 | {n} | {n} | {n} | {n} |
| AI 런타임 코어 | {n} | {n} | {n} | {n} |
| 도구/플러그인 | {n} | {n} | {n} | {n} |
| 에이전트 설정 | {n} | {n} | {n} | {n} |
| 지식 베이스/RAG | {n} | {n} | {n} | {n} |
| 모델 라우팅 | {n} | {n} | {n} | {n} |
| 서브에이전트 | {n} | {n} | {n} | {n} |
| 미들웨어/시크릿 | {n} | {n} | {n} | {n} |
| 스킬/대화 관리 | {n} | {n} | {n} | {n} |
| **Total** | **{n}** | **{n}** | **{n}** | **{n}** |

## 커버리지
- Statement: {n}%
- Branch: {n}%
- Function: {n}%
- Line: {n}%

## 디버깅 이력
| # | 에러 | 원인 | 수정 |
|---|------|------|------|
| 1 | {error} | {cause} | {fix} |

## 미해결 이슈
- {issue-1}
```

#### E. 테스트 완료 보고

```
## Step 5 완료: 테스트 실행 및 디버깅

### 테스트 결과
- 전체: {n} / Pass: {n} / Fail: {n} / Coverage: {n}%
- 디버깅 사이클: {n}회

### 보고서
- docs/tests/test-reports/sprint-{N}/ai-agent-test-report.md

Step 6(최종 보고)으로 진행합니다...
```

---

### Step 6: 최종 보고 및 프로그레스 업데이트

#### A. 프로그레스 트래커 최종 업데이트

`docs/sprints/sprint-{N}-ai-agent/progress.md`의 모든 Feature를 `Done`으로 업데이트한다.

#### B. 최종 보고

```
## AI 에이전트 모듈 자동 구축 완료

### 생성된 산출물
| 산출물 | 경로 |
|--------|------|
| 블루프린트 | docs/blueprints/{NNN}-ai-agent/blueprint.md |
| DB 설계 | docs/database/database-design.md (24개 테이블 추가) |
| 스프린트 맵 | docs/sprints/sprint-{N}-ai-agent/prompt-map.md |
| 프로그레스 | docs/sprints/sprint-{N}-ai-agent/progress.md |
| 테스트 보고서 | docs/tests/test-reports/sprint-{N}/ai-agent-test-report.md |

### 구현 통계
| Feature | 파일 수 |
|---------|---------|
| 기반 인프라 (DB + 리소스) | {n} |
| AI 런타임 코어 (LLM + SSE + Loop) | {n} |
| 도구/플러그인 (20+ 도구) | {n} |
| 에이전트 설정 + 지식 베이스 | {n} |
| 모델 라우팅 + 서브에이전트 | {n} |
| 미들웨어 + 시크릿 + OAuth | {n} |
| 스킬 시스템 + 대화 관리 | {n} |
| 통합 및 최적화 | {n} |
| **Total** | **{n}** |

### 보안 체크리스트
- [ ] AES-256-GCM 시크릿 암호화
- [ ] OAuth PKCE 플로우
- [ ] Gateway 인증 미들웨어
- [ ] 크레딧 과금 검증
- [ ] 웹훅 서명 검증
- [ ] 도구 실행 타임아웃 (30초)
- [ ] LoopGuard 무한루프 방지
- [ ] ContextGuard 토큰 예산 보호
- [ ] Rate Limiting (선택)
- [ ] LLM API 키 환경 변수 분리
```
