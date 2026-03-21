# AI 에이전트 플랫폼 설계 문서

> **프로젝트**: AI 에이전트 플랫폼 모듈 (AI Agent Platform Module)
> **버전**: 1.0.0
> **작성일**: 2026-03-21
> **기반 레퍼런스**: fect-api-agent (Next.js 14 + PostgreSQL + Drizzle ORM + Anthropic/OpenAI)

---

## 목차

1. [아키텍처 개요](#1-아키텍처-개요)
2. [기술 스택](#2-기술-스택)
3. [데이터베이스 스키마](#3-데이터베이스-스키마)
4. [API 설계](#4-api-설계)
5. [AI 런타임 엔진](#5-ai-런타임-엔진)
6. [도구 및 플러그인 시스템](#6-도구-및-플러그인-시스템)
7. [스킬 시스템](#7-스킬-시스템)
8. [디렉토리 구조](#8-디렉토리-구조)
9. [구현 순서](#9-구현-순서)

---

## 1. 아키텍처 개요

### 1.1 설계 원칙

본 모듈은 **멀티 프로바이더 AI 에이전트 플랫폼**을 구현한다. 핵심 설계 원칙:

- **Gateway Proxy 패턴**: 모든 요청은 포탈(Gateway)을 경유 — 인증, 워크스페이스, 빌링은 Gateway 책임
- **Skill-First 설계**: 에이전트의 능력은 스킬(YAML+Markdown)로 정의 — 시스템 프롬프트에 동적 주입
- **Plugin-Based 도구 확장**: 도구는 PLUGIN.md로 선언, 핸들러로 실행 — 런타임 등록
- **Multi-Provider LLM**: SDK 없이 native fetch로 Anthropic/OpenAI/Ollama 통합
- **SSE 실시간 스트리밍**: 토큰 단위 스트리밍, 도구 호출/결과, HITL 질문까지 프론트엔드에 실시간 전달
- **4중 안전장치**: LoopGuard, ToolContextTracker, WorkflowGuard, ContextGuard

### 1.2 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (React/Next.js)                    │
│  EventSource(SSE) ←── POST /conversations/[id]/messages      │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Portal Gateway (fect-api-portal)            │
│  Firebase Auth │ Workspace Context │ Credit Billing           │
│  → X-User-id, X-Company-id, X-Ws-Role, X-Credits-Remaining  │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Server (fect-api-agent)               │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Context      │  │ Agent Runner │  │ SSE Stream   │       │
│  │ Builder      │──▶│ (Core Loop) │──▶│ Handler      │       │
│  │ (10-step)    │  │              │  │              │       │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘       │
│         │                  │                                  │
│  ┌──────┴───────┐  ┌──────┴───────┐                          │
│  │ Skill Merger │  │ Tool         │                          │
│  │ + Model      │  │ Dispatcher   │                          │
│  │   Router     │  │ + Plugin Mgr │                          │
│  └──────────────┘  └──────┬───────┘                          │
│                           │                                   │
└───────────────────────────┼───────────────────────────────────┘
                            │
            ┌───────────────┼───────────────────┐
            ▼               ▼                   ▼
     ┌────────────┐  ┌────────────┐     ┌────────────┐
     │ PostgreSQL  │  │ Anthropic  │     │   Neo4j    │
     │ + pgvector  │  │ / OpenAI   │     │ (Graph     │
     │ (Drizzle)   │  │ / Ollama   │     │  Memory)   │
     └────────────┘  └────────────┘     └────────────┘
```

### 1.3 Gateway 헤더 프로토콜

Portal Gateway가 주입하는 헤더:

| 헤더 | 필수 | 설명 |
|------|------|------|
| `X-User-id` | Y | 인증된 사용자 ID |
| `X-Company-id` | N | 소속 회사 ID |
| `X-Workspace-id` | Y | 현재 워크스페이스 ID |
| `X-Ws-Role` | Y | 워크스페이스 내 역할 (OWNER/ADMIN/MEMBER) |
| `X-Ws-Status` | Y | 워크스페이스 상태 (ACTIVE 필수) |
| `X-Credits-Remaining` | Y | 잔여 크레딧 (-1=무제한, ≤0=부족) |
| `X-Subscription-Id` | N | 구독 ID |
| `Accept-Language` | N | 로케일 (ko/en/vi) |

### 1.4 타 모듈과의 관계

| 항목 | 인증 모듈 | 워크스페이스 모듈 | 결제 모듈 | AI 에이전트 모듈 |
|------|----------|-----------------|----------|----------------|
| 사용자 식별 | `TB_COMM_USER.ID` 정의 | 멤버십 FK | 감사 로그 FK | `TH_AI_MSG.user_id`, `TL_AI_TKN_USG.user_id` FK |
| 워크스페이스 | `BSC_WKSPC_ID` FK | `TB_COMM_WKSPC.ID` 정의 | `WKSPC_ID` FK | 모든 AI 테이블에 `wrkspce_id` FK |
| 인증/권한 | JWT 발급 | 멤버십 검증 | 구독 검증 | Gateway 헤더로 전달받아 미들웨어에서 검증 |
| 빌링 연동 | - | - | 크레딧 관리 | `X-Credits-Remaining`으로 크레딧 차감 여부 판단 |

---

## 2. 기술 스택

### 2.1 핵심 의존성

```json
{
  "dependencies": {
    "next": "^14.x",
    "drizzle-orm": "^0.38.x",
    "postgres": "^3.4.x",
    "zod": "^3.x",
    "nanoid": "^5.x",
    "dayjs": "^1.x"
  },
  "devDependencies": {
    "drizzle-kit": "^0.30.x",
    "typescript": "^5.x"
  }
}
```

### 2.2 LLM 프로바이더별 추가 의존성

| 프로바이더 | 구현 방식 | 비고 |
|-----------|----------|------|
| Anthropic | native fetch (`/v1/messages`) | Prompt caching, Extended thinking 지원 |
| OpenAI | native fetch (`/v1/chat/completions`) | GPT-4o, o1 지원 |
| Ollama | native fetch (`/api/chat`) | 로컬 모델, 도구 미지원 |
| OpenAI-Compatible | OpenAI 프로토콜 동일 | vLLM 등 |

> **설계 결정**: SDK 의존성 없이 native fetch로 구현. 프로바이더별 요청/응답 포맷 변환을 내부에서 처리.

### 2.3 외부 서비스

| 서비스 | 용도 | 선택/필수 |
|--------|------|----------|
| PostgreSQL + pgvector | 메인 DB + 벡터 검색 (메모리, RAG) | 필수 |
| Neo4j | 그래프 메모리 (엔티티-관계 저장) | 선택 |
| Redis | 크론 작업 분산 락 | 선택 |

### 2.4 환경 변수

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
DATABASE_SCHEMA=app

# LLM Providers
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com  # 또는 커스텀 엔드포인트

# Gateway
PORTAL_INTERNAL_URL=http://localhost:8080

# Optional
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=...
```

---

## 3. 데이터베이스 스키마

### 3.1 ER 다이어그램

```
TB_AI_AGNT_CTGRY ──1:N──▶ TB_AI_AGNT
                                │
                    ┌───────────┼───────────┐
                    │           │           │
               TR_AI_CNFG  TR_AI_CNFG  TB_AI_CNVRSTN
               _SKILL      _MCP_SRVR       │
                    │           │           │
               TB_AI_SKILL  TB_AI_MCP   TH_AI_MSG
               _DEF         _SRVR          │
                                       TL_AI_TKN_USG

TB_AI_KNWLDG_BS ──1:N──▶ TB_AI_KNWLDG_DOC ──1:N──▶ TB_AI_EMBDNG_CHNK

TB_AI_MMRY (pgvector 1536-dim)

TB_AI_SBAGNT_RUN ──1:N──▶ TL_AI_SBAGNT_LOG
     │ (self-FK: prnt_run_id)

TB_AI_WKSPC_SCRT
TB_AI_SYS_CRED ──▶ TH_AI_OAUTH_SESSION
TL_AI_SCRT_ACCS_LOG

TB_AI_CHNL_CNFG ──▶ TL_AI_CHNL_MSG_LOG
```

### 3.2 TB_AI_AGNT_CTGRY (에이전트 카테고리)

```sql
CREATE TABLE TB_AI_AGNT_CTGRY (
    ID              SERIAL PRIMARY KEY,
    CTGRY_CD        VARCHAR(50) NOT NULL UNIQUE,   -- 카테고리 코드
    CTGRY_NM        VARCHAR(100) NOT NULL,          -- 카테고리명
    CTGRY_DC        TEXT,                            -- 카테고리 설명
    SORT_SN         INTEGER DEFAULT 0,               -- 정렬 순서
    ACTV_YN         CHAR(1) DEFAULT 'Y',            -- 활성 여부
    RGST_DT         TIMESTAMPTZ DEFAULT NOW(),
    MDFCN_DT        TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.3 TB_AI_AGNT (에이전트 정의 — 글로벌 단건)

```sql
CREATE TABLE TB_AI_AGNT (
    ID              SERIAL PRIMARY KEY,
    AGNT_CD         VARCHAR(50) NOT NULL UNIQUE,    -- 에이전트 코드 (URL slug)
    AGNT_NM         VARCHAR(100) NOT NULL,           -- 에이전트명
    AGNT_DC         TEXT,                             -- 에이전트 설명
    AGNT_SBTTL      VARCHAR(200),                    -- 서브타이틀
    CTGRY_ID        INTEGER REFERENCES TB_AI_AGNT_CTGRY(ID),
    ICON_NM         VARCHAR(50),                     -- 아이콘명
    CLR_THME_CD     VARCHAR(20),                     -- 컬러 테마 코드
    DSHBRD_PATH     VARCHAR(200),                    -- 대시보드 경로

    -- LLM 설정 (글로벌)
    SYS_PRMPT       TEXT,                             -- 시스템 프롬프트
    MDL_PRVDR_CD    VARCHAR(20) NOT NULL DEFAULT 'ANTHROPIC',  -- ANTHROPIC/OPENAI/OLLAMA/OPENAI_COMPAT
    MDL_NM          VARCHAR(100) NOT NULL,            -- 모델명 (claude-sonnet-4-20250514 등)
    TMPRT           NUMERIC(3,2) DEFAULT 0.7,         -- Temperature (0~2)
    MAX_TKN_CNT     INTEGER DEFAULT 4096,             -- 최대 출력 토큰
    TOP_P           NUMERIC(3,2),                     -- Nucleus sampling
    CNTXT_WNDW_CNT  INTEGER DEFAULT 20,               -- 대화 히스토리 윈도우 크기

    -- 기능 플래그
    MMRY_SRCH_YN    CHAR(1) DEFAULT 'N',             -- 메모리 검색 활성화
    RAG_SRCH_YN     CHAR(1) DEFAULT 'N',             -- RAG 검색 활성화
    GRPH_MMRY_YN    CHAR(1) DEFAULT 'N',             -- 그래프 메모리 활성화
    TOOL_YN         CHAR(1) DEFAULT 'Y',             -- 도구 사용 활성화
    RERNK_YN        CHAR(1) DEFAULT 'N',             -- 리랭킹 활성화

    -- 도구 및 설정
    ENBL_TOOL_CDS   JSONB DEFAULT '[]',              -- 활성화된 도구 코드 배열
    STNG            JSONB DEFAULT '{}',              -- 설정 (routing, fallbackModels 등)
    BASE_URL        VARCHAR(500),                     -- 커스텀 LLM 엔드포인트
    API_KEY_REF     VARCHAR(100),                     -- API 키 참조명

    -- 메타
    STTS_CD         VARCHAR(20) DEFAULT 'ACTIVE',
    BADGE_LBL       VARCHAR(20),
    SORT_SN         INTEGER DEFAULT 0,
    ACTV_YN         CHAR(1) DEFAULT 'Y',
    RGST_DT         TIMESTAMPTZ DEFAULT NOW(),
    MDFCN_DT        TIMESTAMPTZ DEFAULT NOW()
);
```

**STNG JSONB 구조**:
```json
{
  "routing": {
    "enabled": true,
    "classifierModel": "claude-haiku-4-5-20251001",
    "rules": {
      "SIMPLE": { "provider": "ANTHROPIC", "model": "claude-haiku-4-5-20251001" },
      "VAGUE": { "provider": "ANTHROPIC", "model": "claude-sonnet-4-20250514" },
      "COMPLEX": { "provider": "ANTHROPIC", "model": "claude-opus-4-20250514" }
    }
  },
  "fallbackModels": [
    { "provider": "OPENAI", "model": "gpt-4o" }
  ]
}
```

### 3.4 TB_AI_CNVRSTN (대화)

```sql
CREATE TABLE TB_AI_CNVRSTN (
    ID              SERIAL PRIMARY KEY,
    WRKSPCE_ID      INTEGER NOT NULL,                 -- 워크스페이스 ID
    AGNT_ID         INTEGER NOT NULL REFERENCES TB_AI_AGNT(ID),
    USER_ID         INTEGER NOT NULL,                  -- 사용자 ID
    CNVRSTN_NM      VARCHAR(200),                     -- 대화 제목 (자동 생성)
    SMRY_CN         TEXT,                              -- Compaction 요약
    MSG_CNT         INTEGER DEFAULT 0,                 -- 메시지 수
    LAST_MSG_DT     TIMESTAMPTZ,                      -- 마지막 메시지 시각
    TOT_TKN_CNT     INTEGER DEFAULT 0,                 -- 총 토큰 수
    CMPCTN_CNT      INTEGER DEFAULT 0,                 -- Compaction 횟수
    PRJCT_ID        INTEGER,                           -- 프로젝트 ID (선택)
    PNND_YN         CHAR(1) DEFAULT 'N',              -- 고정 여부
    MTDT            JSONB DEFAULT '{}',               -- 메타데이터
    STTS_CD         VARCHAR(20) DEFAULT 'ACTIVE',     -- ACTIVE/ARCHIVED/DELETED
    RGST_DT         TIMESTAMPTZ DEFAULT NOW(),
    MDFCN_DT        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ai_cnvrstn_ws_user ON TB_AI_CNVRSTN(WRKSPCE_ID, USER_ID, STTS_CD);
CREATE INDEX idx_ai_cnvrstn_ws_agnt ON TB_AI_CNVRSTN(WRKSPCE_ID, AGNT_ID);
CREATE INDEX idx_ai_cnvrstn_last_msg ON TB_AI_CNVRSTN(LAST_MSG_DT DESC);
```

### 3.5 TH_AI_MSG (메시지 이력)

```sql
CREATE TABLE TH_AI_MSG (
    ID              SERIAL PRIMARY KEY,
    WRKSPCE_ID      INTEGER NOT NULL,
    CNVRSTN_ID      INTEGER NOT NULL REFERENCES TB_AI_CNVRSTN(ID) ON DELETE CASCADE,
    ROLE_CD         VARCHAR(20) NOT NULL,              -- user / assistant / tool
    CN              TEXT,                               -- 메시지 내용
    TOOL_CALLS      JSONB,                             -- 도구 호출 배열 [{id, name, arguments}]
    TOOL_CALL_ID    VARCHAR(100),                      -- 도구 결과의 호출 ID
    TOOL_NM         VARCHAR(100),                      -- 도구명
    ATCH_FILES      JSONB,                             -- 첨부 파일 메타데이터
    INPUT_TKN_CNT   INTEGER DEFAULT 0,
    OTPUT_TKN_CNT   INTEGER DEFAULT 0,
    MDL_NM          VARCHAR(100),                      -- 사용된 모델명
    MSG_SN          INTEGER NOT NULL,                  -- 메시지 순서 번호
    STTS_CD         VARCHAR(20) DEFAULT 'ACTIVE',
    RGST_DT         TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ai_msg_conv_sn ON TH_AI_MSG(CNVRSTN_ID, MSG_SN);
CREATE INDEX idx_ai_msg_ws_dt ON TH_AI_MSG(WRKSPCE_ID, RGST_DT);
CREATE INDEX idx_ai_msg_conv_role ON TH_AI_MSG(CNVRSTN_ID, ROLE_CD);
```

### 3.6 TB_AI_MMRY (메모리 — pgvector)

```sql
CREATE TABLE TB_AI_MMRY (
    ID              SERIAL PRIMARY KEY,
    WRKSPCE_ID      INTEGER NOT NULL,
    AGNT_ID         INTEGER REFERENCES TB_AI_AGNT(ID),
    TY_CD           VARCHAR(20) NOT NULL,              -- MANUAL / AUTO_EXTRACTED
    CTGRY_CD        VARCHAR(50),                       -- 카테고리 코드
    CN              TEXT NOT NULL,                      -- 메모리 내용
    CNTXTL_CN       TEXT,                               -- 컨텍스트 내용
    LANG_CD         VARCHAR(10),                       -- 언어 코드
    SRC_CNVRSTN_ID  INTEGER REFERENCES TB_AI_CNVRSTN(ID),
    EMBDNG          VECTOR(1536),                      -- pgvector 임베딩
    IMPRTNS_SN      INTEGER DEFAULT 5,                 -- 중요도 점수 (1~10)
    ACTV_YN         CHAR(1) DEFAULT 'Y',
    RGST_DT         TIMESTAMPTZ DEFAULT NOW(),
    MDFCN_DT        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ai_mmry_ws_actv ON TB_AI_MMRY(WRKSPCE_ID, ACTV_YN);
CREATE INDEX idx_ai_mmry_ws_agnt ON TB_AI_MMRY(WRKSPCE_ID, AGNT_ID);
CREATE INDEX idx_ai_mmry_embdng ON TB_AI_MMRY USING ivfflat (EMBDNG vector_cosine_ops);
```

### 3.7 TB_AI_KNWLDG_BS / TB_AI_KNWLDG_DOC / TB_AI_EMBDNG_CHNK (지식 베이스 — RAG)

```sql
-- 지식 베이스 정의
CREATE TABLE TB_AI_KNWLDG_BS (
    ID              SERIAL PRIMARY KEY,
    WRKSPCE_ID      INTEGER NOT NULL,
    KNWLDG_BS_NM    VARCHAR(200) NOT NULL,             -- 지식 베이스명
    KNWLDG_BS_DC    TEXT,                               -- 설명
    EMBDNG_MDL_NM   VARCHAR(100) DEFAULT 'text-embedding-3-small',
    EMBDNG_DIMS     INTEGER DEFAULT 1536,
    CHNK_TKN_CNT   INTEGER DEFAULT 500,                -- 청크 토큰 수
    CHNK_OVRLP_CNT  INTEGER DEFAULT 50,                -- 청크 오버랩
    DOC_CNT         INTEGER DEFAULT 0,
    CHNK_CNT        INTEGER DEFAULT 0,
    STTS_CD         VARCHAR(20) DEFAULT 'ACTIVE',
    RGST_DT         TIMESTAMPTZ DEFAULT NOW(),
    MDFCN_DT        TIMESTAMPTZ DEFAULT NOW()
);

-- 지식 문서
CREATE TABLE TB_AI_KNWLDG_DOC (
    ID              SERIAL PRIMARY KEY,
    WRKSPCE_ID      INTEGER NOT NULL,
    KNWLDG_BS_ID    INTEGER NOT NULL REFERENCES TB_AI_KNWLDG_BS(ID) ON DELETE CASCADE,
    DOC_NM          VARCHAR(500) NOT NULL,
    DOC_TY_CD       VARCHAR(20),                       -- PDF/TXT/MD/DOCX
    FILE_SZ         BIGINT,
    FILE_URL        VARCHAR(1000),
    RAW_TXT         TEXT,
    CHNK_CNT        INTEGER DEFAULT 0,
    TKN_CNT         INTEGER DEFAULT 0,
    FILE_HASH       VARCHAR(64),                       -- SHA-256
    STTS_CD         VARCHAR(20) DEFAULT 'PROCESSING',  -- PROCESSING/COMPLETED/FAILED
    ERR_MSG         TEXT,
    RGST_DT         TIMESTAMPTZ DEFAULT NOW(),
    MDFCN_DT        TIMESTAMPTZ DEFAULT NOW()
);

-- 임베딩 청크
CREATE TABLE TB_AI_EMBDNG_CHNK (
    ID              SERIAL PRIMARY KEY,
    WRKSPCE_ID      INTEGER NOT NULL,
    KNWLDG_BS_ID    INTEGER NOT NULL,
    DOC_ID          INTEGER NOT NULL REFERENCES TB_AI_KNWLDG_DOC(ID) ON DELETE CASCADE,
    CHNK_SN         INTEGER NOT NULL,                  -- 청크 순서
    CHNK_TXT        TEXT NOT NULL,
    EMBDNG          VECTOR(1536),
    TKN_CNT         INTEGER,
    STRT_OFFSET     INTEGER,
    END_OFFSET      INTEGER,
    MTDT            JSONB DEFAULT '{}',
    RGST_DT         TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_embdng_chnk_vec ON TB_AI_EMBDNG_CHNK USING ivfflat (EMBDNG vector_cosine_ops);
```

### 3.8 TB_AI_SKILL_DEF / TR_AI_CNFG_SKILL (스킬)

```sql
-- 워크스페이스 커스텀 스킬
CREATE TABLE TB_AI_SKILL_DEF (
    ID              SERIAL PRIMARY KEY,
    WRKSPCE_ID      INTEGER NOT NULL,
    SKILL_NM        VARCHAR(100) NOT NULL,
    CN              TEXT NOT NULL,                      -- 스킬 내용 (Markdown)
    SKILL_DC        TEXT,
    ICON_NM         VARCHAR(50),
    SGSTN_YN        CHAR(1) DEFAULT 'N',              -- 제안 표시 여부
    SORT_SN         INTEGER DEFAULT 0,
    ACTV_YN         CHAR(1) DEFAULT 'Y',
    RGST_DT         TIMESTAMPTZ DEFAULT NOW(),
    MDFCN_DT        TIMESTAMPTZ DEFAULT NOW()
);

-- 에이전트-스킬 매핑
CREATE TABLE TR_AI_CNFG_SKILL (
    ID              SERIAL PRIMARY KEY,
    AGNT_ID         INTEGER NOT NULL REFERENCES TB_AI_AGNT(ID),
    SKILL_NM        VARCHAR(100) NOT NULL,
    SKILL_SRC_CD    VARCHAR(20) NOT NULL,              -- GLOBAL / WORKSPACE
    ENBL_YN         CHAR(1) DEFAULT 'Y',
    SORT_SN         INTEGER DEFAULT 0,
    ACTV_YN         CHAR(1) DEFAULT 'Y',
    RGST_DT         TIMESTAMPTZ DEFAULT NOW(),
    MDFCN_DT        TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.9 TB_AI_MCP_SRVR / TR_AI_CNFG_MCP_SRVR (MCP 서버)

```sql
CREATE TABLE TB_AI_MCP_SRVR (
    ID              SERIAL PRIMARY KEY,
    WRKSPCE_ID      INTEGER NOT NULL,
    SRVR_CD         VARCHAR(50) NOT NULL,
    SRVR_NM         VARCHAR(200) NOT NULL,
    SRVR_DC         TEXT,
    TRNSPRT_TY_CD   VARCHAR(20) NOT NULL,              -- stdio / http / sse
    TRNSPRT_CNFG    JSONB NOT NULL,                    -- 전송 설정 (command, args, url 등)
    AUTH_CNFG       JSONB,                              -- 인증 설정
    HLTH_STTS_CD    VARCHAR(20),
    LAST_HLTH_CHK_DT TIMESTAMPTZ,
    TOOL_CNT        INTEGER DEFAULT 0,
    LAST_DSCVR_DT   TIMESTAMPTZ,
    TOOL_SCHMA_CACHE JSONB,                            -- 도구 스키마 캐시
    ACTV_YN         CHAR(1) DEFAULT 'Y',
    SORT_SN         INTEGER DEFAULT 0,
    RGST_DT         TIMESTAMPTZ DEFAULT NOW(),
    MDFCN_DT        TIMESTAMPTZ DEFAULT NOW()
);

-- 에이전트-MCP 서버 매핑
CREATE TABLE TR_AI_CNFG_MCP_SRVR (
    ID              SERIAL PRIMARY KEY,
    AGNT_ID         INTEGER NOT NULL REFERENCES TB_AI_AGNT(ID),
    MCP_SRVR_ID     INTEGER NOT NULL REFERENCES TB_AI_MCP_SRVR(ID),
    ENBL_YN         CHAR(1) DEFAULT 'Y',
    ACTV_YN         CHAR(1) DEFAULT 'Y',
    RGST_DT         TIMESTAMPTZ DEFAULT NOW(),
    MDFCN_DT        TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.10 TB_AI_SBAGNT_RUN / TL_AI_SBAGNT_LOG (서브에이전트)

```sql
CREATE TABLE TB_AI_SBAGNT_RUN (
    ID              SERIAL PRIMARY KEY,
    WRKSPCE_ID      INTEGER NOT NULL,
    RUN_UUID        VARCHAR(36) NOT NULL UNIQUE,       -- UUID
    PRNT_CNVRSTN_ID INTEGER REFERENCES TB_AI_CNVRSTN(ID),
    PRNT_RUN_ID     INTEGER REFERENCES TB_AI_SBAGNT_RUN(ID),  -- Self-FK (중첩)
    AGNT_ID         INTEGER NOT NULL REFERENCES TB_AI_AGNT(ID),
    SPAWN_DEPTH     INTEGER DEFAULT 0,                 -- 중첩 깊이
    TASK_CN         TEXT,                               -- 태스크 내용
    LABEL_NM        VARCHAR(200),
    MDL_PRVDR_CD    VARCHAR(20),
    MDL_NM          VARCHAR(100),
    THINKING_LVL    VARCHAR(20),
    RUN_TMOT_SEC    INTEGER DEFAULT 300,               -- 실행 타임아웃 (초)
    CLNP_STRTGY     VARCHAR(20) DEFAULT 'KEEP',        -- KEEP / DELETE
    STTS_CD         VARCHAR(20) DEFAULT 'PENDING',     -- PENDING/RUNNING/SUCCESS/FAILURE/KILLED
    STRT_DT         TIMESTAMPTZ,
    END_DT          TIMESTAMPTZ,
    OTCM_CD         VARCHAR(20),                       -- 결과 코드
    OTCM_ERR_MSG    TEXT,                               -- 에러 메시지
    RSLT_CN         TEXT,                               -- 결과 내용
    INPUT_TKN_CNT   INTEGER DEFAULT 0,
    OTPUT_TKN_CNT   INTEGER DEFAULT 0,
    TOT_TKN_CNT     INTEGER DEFAULT 0,
    RNTM_MS         INTEGER,                            -- 실행 시간 (ms)
    ANNC_YN         CHAR(1) DEFAULT 'Y',               -- SSE 알림 여부
    ARCHV_DT        TIMESTAMPTZ,
    RGST_DT         TIMESTAMPTZ DEFAULT NOW(),
    MDFCN_DT        TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE TL_AI_SBAGNT_LOG (
    ID              SERIAL PRIMARY KEY,
    WRKSPCE_ID      INTEGER NOT NULL,
    RUN_ID          INTEGER NOT NULL REFERENCES TB_AI_SBAGNT_RUN(ID),
    LOG_LVL_CD      VARCHAR(10),                       -- INFO/WARN/ERROR
    CN              TEXT,
    RGST_DT         TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.11 TL_AI_TKN_USG (토큰 사용량 로그)

```sql
CREATE TABLE TL_AI_TKN_USG (
    ID              SERIAL PRIMARY KEY,
    WRKSPCE_ID      INTEGER NOT NULL,
    USER_ID         INTEGER NOT NULL,
    CNVRSTN_ID      INTEGER,
    MSG_ID          INTEGER,
    MDL_PRVDR_CD    VARCHAR(20),
    MDL_NM          VARCHAR(100),
    INPUT_TKN_CNT   INTEGER DEFAULT 0,
    OTPUT_TKN_CNT   INTEGER DEFAULT 0,
    TOT_TKN_CNT     INTEGER DEFAULT 0,
    USG_TY_CD       VARCHAR(20) DEFAULT 'WEB_CHAT',    -- WEB_CHAT / API / BATCH
    RGST_DT         TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.12 TB_AI_WKSPC_SCRT / TB_AI_SYS_CRED (비밀 관리)

```sql
-- 워크스페이스 시크릿 (AES-256-GCM 암호화)
CREATE TABLE TB_AI_WKSPC_SCRT (
    ID              SERIAL PRIMARY KEY,
    WRKSPCE_ID      INTEGER NOT NULL,
    SCRT_KEY        VARCHAR(100) NOT NULL,
    SCRT_VAL        TEXT NOT NULL,                      -- AES-256-GCM 암호화
    SCRT_IV         VARCHAR(32) NOT NULL,               -- 초기화 벡터
    SCRT_TAG        VARCHAR(32) NOT NULL,               -- 인증 태그
    SCRT_DC         TEXT,
    CTGRY_CD        VARCHAR(50),
    MSKD_VAL        VARCHAR(100),                      -- 마스킹된 표시값
    ACTV_YN         CHAR(1) DEFAULT 'Y',
    RGST_DT         TIMESTAMPTZ DEFAULT NOW(),
    MDFCN_DT        TIMESTAMPTZ DEFAULT NOW()
);

-- 시스템 자격 증명 (OAuth 토큰, API 키)
CREATE TABLE TB_AI_SYS_CRED (
    ID              SERIAL PRIMARY KEY,
    CRED_NM         VARCHAR(100) NOT NULL,
    PRVDR_CD        VARCHAR(50) NOT NULL,               -- GOOGLE/GITHUB/SLACK 등
    AUTH_TYP_CD     VARCHAR(20),                        -- OAUTH2/API_KEY/BEARER
    ACCS_TKN        TEXT,                                -- 암호화된 Access Token
    ACCS_IV         VARCHAR(32),
    ACCS_TAG        VARCHAR(32),
    RFRSH_TKN       TEXT,                                -- 암호화된 Refresh Token
    RFRSH_IV        VARCHAR(32),
    RFRSH_TAG       VARCHAR(32),
    EXPS_DT         TIMESTAMPTZ,                        -- 토큰 만료
    PRRT            INTEGER DEFAULT 0,                   -- 우선순위
    STTS_CD         VARCHAR(20) DEFAULT 'ACTIVE',
    ERR_CNT         INTEGER DEFAULT 0,
    LAST_ERR_MSG    TEXT,
    LAST_USE_DT     TIMESTAMPTZ,
    RGST_DT         TIMESTAMPTZ DEFAULT NOW(),
    MDFCN_DT        TIMESTAMPTZ DEFAULT NOW()
);

-- OAuth 세션
CREATE TABLE TH_AI_OAUTH_SESSION (
    ID              SERIAL PRIMARY KEY,
    STATE           VARCHAR(128) NOT NULL UNIQUE,       -- PKCE state
    CD_VRFR         VARCHAR(128),                       -- Code Verifier
    PRVDR_CD        VARCHAR(50) NOT NULL,
    CRED_NM         VARCHAR(100),
    RDRC_URI        VARCHAR(500),
    PRRT            INTEGER DEFAULT 0,
    STTS_CD         VARCHAR(20) DEFAULT 'PENDING',     -- PENDING/SUCCESS/FAILED
    ERR_MSG         TEXT,
    EXPS_DT         TIMESTAMPTZ NOT NULL,
    RGST_DT         TIMESTAMPTZ DEFAULT NOW(),
    MDFCN_DT        TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.13 TB_AI_CHNL_CNFG (채널 — Slack/Teams/Discord)

```sql
CREATE TABLE TB_AI_CHNL_CNFG (
    ID              SERIAL PRIMARY KEY,
    WRKSPCE_ID      INTEGER NOT NULL,
    AGNT_ID         INTEGER NOT NULL REFERENCES TB_AI_AGNT(ID),
    CHNL_TY_CD      VARCHAR(20) NOT NULL,              -- SLACK/TEAMS/DISCORD
    CHNL_NM         VARCHAR(200),
    CRDNTL          JSONB,                              -- 채널 자격 증명
    WBHK_URL        VARCHAR(500),                      -- 웹훅 URL
    WBHK_SCRT       VARCHAR(200),                      -- 웹훅 시크릿
    DLVRY_MODE_CD   VARCHAR(20) DEFAULT 'DIRECT',      -- DIRECT / ASYNC
    TXT_CHNK_LMT    INTEGER DEFAULT 4000,
    DM_PLCY_CD      VARCHAR(20) DEFAULT 'OPEN',        -- OPEN / WHITELIST
    ALLW_LST        JSONB,                              -- 허용 목록
    STNG            JSONB DEFAULT '{}',
    ACTV_YN         CHAR(1) DEFAULT 'Y',
    RGST_DT         TIMESTAMPTZ DEFAULT NOW(),
    MDFCN_DT        TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.14 TB_AI_PRJCT (프로젝트)

```sql
CREATE TABLE TB_AI_PRJCT (
    ID              SERIAL PRIMARY KEY,
    WRKSPCE_ID      INTEGER NOT NULL,
    PRJCT_CD        VARCHAR(50) NOT NULL,
    PRJCT_NM        VARCHAR(200) NOT NULL,
    DC              TEXT,
    STTS_CD         VARCHAR(20) DEFAULT 'ACTIVE',
    SORT_SN         INTEGER DEFAULT 0,
    RGST_DT         TIMESTAMPTZ DEFAULT NOW(),
    MDFCN_DT        TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.15 TL_AI_SCRT_ACCS_LOG (시크릿 접근 감사 로그)

```sql
CREATE TABLE TL_AI_SCRT_ACCS_LOG (
    ID              SERIAL PRIMARY KEY,
    WRKSPCE_ID      INTEGER NOT NULL,
    SCRT_ID         INTEGER NOT NULL REFERENCES TB_AI_WKSPC_SCRT(ID),
    USER_ID         INTEGER NOT NULL,
    ACCS_TY_CD      VARCHAR(20) NOT NULL,              -- READ / DECRYPT / UPDATE / DELETE
    ACCS_RSLT_CD    VARCHAR(20) DEFAULT 'SUCCESS',     -- SUCCESS / DENIED / ERROR
    IP_ADDR         VARCHAR(45),
    USR_AGNT        TEXT,
    RGST_DT         TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_scrt_accs_log_ws ON TL_AI_SCRT_ACCS_LOG(WRKSPCE_ID, RGST_DT DESC);
CREATE INDEX idx_scrt_accs_log_scrt ON TL_AI_SCRT_ACCS_LOG(SCRT_ID);
```

### 3.16 TL_AI_CHNL_MSG_LOG (채널 메시지 로그)

```sql
CREATE TABLE TL_AI_CHNL_MSG_LOG (
    ID              SERIAL PRIMARY KEY,
    WRKSPCE_ID      INTEGER NOT NULL,
    CHNL_CNFG_ID    INTEGER NOT NULL REFERENCES TB_AI_CHNL_CNFG(ID),
    DRCTN_CD        VARCHAR(10) NOT NULL,              -- INBOUND / OUTBOUND
    MSG_CN          TEXT,
    SNDR_ID         VARCHAR(200),                      -- 외부 발신자 ID
    CNVRSTN_ID      INTEGER REFERENCES TB_AI_CNVRSTN(ID),
    STTS_CD         VARCHAR(20) DEFAULT 'SUCCESS',     -- SUCCESS / FAILED / FILTERED
    ERR_MSG         TEXT,
    RGST_DT         TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chnl_msg_log_ws ON TL_AI_CHNL_MSG_LOG(WRKSPCE_ID, RGST_DT DESC);
CREATE INDEX idx_chnl_msg_log_chnl ON TL_AI_CHNL_MSG_LOG(CHNL_CNFG_ID);
```

### 3.17 TL_AI_MCP_SRVR_LOG (MCP 서버 이벤트 로그)

```sql
CREATE TABLE TL_AI_MCP_SRVR_LOG (
    ID              SERIAL PRIMARY KEY,
    WRKSPCE_ID      INTEGER NOT NULL,
    MCP_SRVR_ID     INTEGER NOT NULL REFERENCES TB_AI_MCP_SRVR(ID),
    EVNT_TY_CD      VARCHAR(30) NOT NULL,              -- CONNECT / DISCONNECT / DISCOVER / ERROR / HEALTH_CHECK
    EVNT_CN         TEXT,
    TOOL_CNT        INTEGER,
    ERR_MSG         TEXT,
    RGST_DT         TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_mcp_srvr_log_srvr ON TL_AI_MCP_SRVR_LOG(MCP_SRVR_ID, RGST_DT DESC);
```

### 3.18 TB_AI_SGGSTN_TMPL (제안 템플릿)

```sql
CREATE TABLE TB_AI_SGGSTN_TMPL (
    ID              SERIAL PRIMARY KEY,
    WRKSPCE_ID      INTEGER NOT NULL,
    AGNT_ID         INTEGER REFERENCES TB_AI_AGNT(ID),
    SGGSTN_CN       TEXT NOT NULL,                      -- 제안 내용
    CTGRY_CD        VARCHAR(50),                        -- 카테고리 코드
    SORT_SN         INTEGER DEFAULT 0,
    ACTV_YN         CHAR(1) DEFAULT 'Y',
    RGST_DT         TIMESTAMPTZ DEFAULT NOW(),
    MDFCN_DT        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sggstn_tmpl_ws_agnt ON TB_AI_SGGSTN_TMPL(WRKSPCE_ID, AGNT_ID, ACTV_YN);
```

---

## 4. API 설계

### 4.1 미들웨어 체인

모든 라우트에 적용되는 미들웨어:

```
withGatewayAuth() → withAiContext() → withCredits() → handler
```

1. **withGatewayAuth()** — `X-User-id`, `X-Workspace-id`, `X-Ws-Role` 등 Gateway 헤더 파싱/검증
2. **withAiContext()** — 워크스페이스 ACTIVE 상태 검증, 로케일 결정
3. **withCredits()** — `X-Credits-Remaining` 검사 (-1=무제한, ≤0=402 반환)

### 4.2 엔드포인트 목록

#### 대화 및 메시지

| Method | Path | 설명 |
|--------|------|------|
| `POST` | `/ai/conversations/[convId]/messages` | 메시지 전송 (SSE 스트리밍 응답) |
| `GET` | `/ai/conversations/[convId]/messages` | 메시지 이력 조회 (커서 페이징) |
| `GET` | `/ai/conversations` | 대화 목록 |
| `POST` | `/ai/conversations` | 대화 생성 |
| `PATCH` | `/ai/conversations/[convId]` | 대화 수정 (제목, 고정) |
| `DELETE` | `/ai/conversations/[convId]` | 대화 삭제 |
| `POST` | `/ai/conversations/[convId]/ui-actions` | UI 액션 처리 |

#### 에이전트 설정

| Method | Path | 설명 |
|--------|------|------|
| `GET` | `/ai/agents` | 에이전트 목록 (공개) |
| `GET` | `/ai/agents/[agntCd]` | 에이전트 상세 |
| `GET` | `/ai/agent-configs/[agentId]` | 에이전트 설정 조회 |
| `PUT` | `/ai/agent-configs/[agentId]` | 에이전트 설정 수정 |
| `GET` | `/ai/agent-configs/[agentId]/skills` | 에이전트 스킬 목록 |
| `POST/PUT/DELETE` | `/ai/agent-configs/[agentId]/skills/[skillId]` | 스킬 매핑 관리 |
| `GET/POST/PUT/DELETE` | `/ai/agent-configs/[agentId]/mcp-servers/[srvId]` | MCP 서버 매핑 관리 |

#### 지식 베이스

| Method | Path | 설명 |
|--------|------|------|
| `GET/POST` | `/ai/knowledge-bases` | 지식 베이스 CRUD |
| `GET/PUT/DELETE` | `/ai/knowledge-bases/[kbId]` | 단건 관리 |
| `GET/POST/DELETE` | `/ai/knowledge-bases/[kbId]/documents/[docId]` | 문서 업로드/삭제 |

#### 메모리 및 그래프

| Method | Path | 설명 |
|--------|------|------|
| `GET/POST/DELETE` | `/ai/memories/[memoryId]` | 메모리 CRUD |
| `GET` | `/ai/graph/search` | 그래프 시맨틱 검색 |
| `GET` | `/ai/graph/stats` | 그래프 통계 |
| `GET/POST/DELETE` | `/ai/graph/entities/[entityId]` | 엔티티 관리 |

#### 서브에이전트

| Method | Path | 설명 |
|--------|------|------|
| `POST` | `/ai/subagents` | 서브에이전트 스폰 |
| `GET` | `/ai/subagents/[runUuid]` | 실행 상태 조회 |
| `POST` | `/ai/subagents/[runUuid]/steer` | HITL 조정 |
| `POST` | `/ai/subagents/[runUuid]/kill` | 서브에이전트 종료 |

#### 시크릿 및 자격 증명

| Method | Path | 설명 |
|--------|------|------|
| `GET/POST/DELETE` | `/ai/secrets` | 워크스페이스 시크릿 관리 |
| `GET/POST/DELETE` | `/ai/sys-credentials` | 시스템 자격 증명 관리 |
| `POST` | `/ai/sys-credentials/oauth/initiate` | OAuth 플로우 시작 |
| `POST` | `/ai/sys-credentials/oauth/callback` | OAuth 콜백 |
| `GET` | `/ai/sys-credentials/oauth/status/[sessionId]` | OAuth 상태 확인 |

#### 채널 (Slack/Teams)

| Method | Path | 설명 |
|--------|------|------|
| `GET` | `/ai/channel-configs` | 채널 설정 목록 |
| `POST` | `/ai/channels/webhook/[channelType]` | 웹훅 수신 |

### 4.3 메시지 전송 API 상세

```
POST /ai/conversations/[convId]/messages
Content-Type: application/json
Accept: text/event-stream

Request Body:
{
  "content": "사용자 메시지",
  "attachFiles": [
    {
      "fileId": "abc123",
      "fileName": "report.pdf",
      "fileType": "application/pdf",
      "fileUrl": "https://..."
    }
  ]
}

Response: SSE Stream (text/event-stream)
```

### 4.4 SSE 이벤트 프로토콜

```
event: {eventType}\ndata: {jsonPayload}\n\n
```

**이벤트 시퀀스**:
```
message_start → content_delta* / thinking_delta* → tool_call_start* → tool_call_result*
  → message_end → title_generated → memory_extracted → done
```

**전체 이벤트 타입**:

| 이벤트 | 페이로드 | 설명 |
|--------|---------|------|
| `message_start` | `{ messageId }` | 메시지 생성 시작 |
| `content_delta` | `{ delta: string }` | 텍스트 토큰 스트리밍 |
| `thinking_delta` | `{ delta: string }` | Extended thinking 스트리밍 |
| `tool_call_start` | `{ toolCallId, toolName, arguments }` | 도구 호출 시작 |
| `tool_call_result` | `{ toolCallId, toolName, result }` | 도구 결과 |
| `message_end` | `{ content, toolCalls, usage }` | 최종 어시스턴트 메시지 |
| `title_generated` | `{ title }` | 대화 제목 자동 생성 |
| `memory_extracted` | `{ memories: [] }` | 메모리 추출 완료 |
| `retry` | `{ attempt, reason, model }` | LLM 재시도 |
| `error` | `{ code, message }` | 에러 |
| `done` | `{}` | 스트림 종료 |
| `hitl_question` | `{ question, header, options, multiSelect }` | HITL 질문 |
| `subagent_spawned` | `{ runUuid, label, agentName }` | 서브에이전트 시작 |
| `subagent_completed` | `{ runUuid, result }` | 서브에이전트 완료 |
| `subagent_failed` | `{ runUuid, error }` | 서브에이전트 실패 |
| `subagent_killed` | `{ runUuid }` | 서브에이전트 종료 |
| `warning` | `{ type, message }` | 가드 경고 |
| `ui_layout_changed` | `{ layout }` | UI 레이아웃 변경 |
| `ui_section_changed` | `{ sectionId, content }` | UI 섹션 변경 |

**Keep-Alive**: 15초 간격 SSE 코멘트 (`: keep-alive\n\n`)

### 4.5 에러 응답 형식

```json
{
  "error": {
    "code": "INSUFFICIENT_CREDITS",
    "message": "크레딧이 부족합니다.",
    "status": 402
  }
}
```

| 코드 | HTTP | 설명 |
|------|------|------|
| `UNAUTHORIZED` | 401 | Gateway 인증 실패 |
| `FORBIDDEN` | 403 | 권한 부족 |
| `INSUFFICIENT_CREDITS` | 402 | 크레딧 부족 |
| `NOT_FOUND` | 404 | 리소스 미존재 |
| `WORKSPACE_INACTIVE` | 403 | 비활성 워크스페이스 |
| `RATE_LIMIT_EXCEEDED` | 429 | 요청 제한 초과 |
| `LLM_ERROR` | 502 | LLM 프로바이더 에러 |

---

## 5. AI 런타임 엔진

### 5.1 Core Agent Loop (`executeLoop`)

```
함수: executeLoop(context, writer)
반복 (최대 MAX_TOOL_ITERATIONS = 10):
  1. 클라이언트 연결 확인 (writer.isClosed() → early exit)
  2. message_start 이벤트 발행 (첫 iteration만)
  3. LLM 호출 (스트리밍 + 재시도 + 모델 폴백)
     → content_delta / thinking_delta 이벤트 발행
  4. tool_calls 확인
     A. 도구 없음:
        → WorkflowGuard 검사 (required-tools 미호출 시 경고+재시도)
        → finalContent 설정, BREAK
     B. HITL 도구 호출됨:
        → hitl_question 이벤트 발행
        → finalContent 설정, BREAK (사용자 응답 대기)
     C. 도구 호출됨:
        → LoopGuard 검사 (무한루프 감지)
        → ToolContextTracker 주입 (중복 방지)
        → 도구 실행 (30초 타임아웃)
        → tool_call_start / tool_call_result 이벤트 발행
        → 결과를 히스토리에 추가
        → 다음 iteration
  5. message_end 이벤트 발행
```

### 5.2 4중 안전장치

#### LoopGuard (무한루프 방지)

| 규칙 | 조건 | 단계 |
|------|------|------|
| Rule 1 | 동일 도구 호출 3회 연속 반복 | HARD stop |
| Rule 2 | 단일 도구 5회 이상 호출 (UI 도구는 8회) | HARD stop |
| Rule 3 | 주기 패턴 감지 (주기 1~3, 2+ 사이클) | SOFT → HARD |

- iteration ≥ 3: Soft 위반 시 LLM에 경고 메시지 주입
- iteration ≥ 4: Hard 위반 시 에러 + loop 중단
- Soft 경고는 1회만 발화; LLM이 패턴을 깨면 리셋

#### ToolContextTracker (중복 도구 방지)

- 모든 도구 호출을 args 포함하여 기록
- 비교 키: `file_id`, `sheet`, `startRow`, `endRow`, `action`, `operationId`, `section_id`
- iteration ≥ 2: 이미 호출된 도구 + 잔여 쿼터 요약을 시스템 메시지로 주입

#### WorkflowGuard (필수 도구 강제)

- 스킬 frontmatter의 `required-tools` 추적
- 도구 미호출 + 필수 도구 미완료 시:
  - iteration ≤ 2: 넛지 메시지 + `tool_choice='required'` 강제
  - 최대 2회 재시도

#### ContextGuard (토큰 예산 보호)

- 컨텍스트 윈도우 사용률 모니터링
- 80% 초과 시 대화 compaction 트리거 (이전 메시지 요약)
- 요약을 `TB_AI_CNVRSTN.SMRY_CN`에 저장

### 5.3 Context Building 파이프라인 (10단계)

```
① 기본 시스템 프롬프트 (_default.md)
② 에이전트별 프롬프트 (resources/prompts/{agntCd}.md)
③ 스킬 컨텍스트 (frontmatter skills[] → 직접 주입; 온디맨드 → skill_get 카탈로그)
④ Progressive UI 가이드 (enblToolCds 기반 도구 사용법)
⑤ 에이전트 UI 레이아웃 가이드
⑥ 통합 메모리 컨텍스트 (pgvector flat + Neo4j graph → 하이브리드 랭킹)
⑦ RAG 컨텍스트 (Agentic 쿼리 분해 / HyDE 임베딩 / 리랭킹)
⑧ 대화 Compaction 요약 (smryCn 존재 시)
⑨ 대화 히스토리 (cntxtWndwCnt 윈도우 크기)
⑩ 현재 사용자 메시지 (+ attachFile 메타데이터) + ContextGuard 토큰 예산 검사
```

### 5.4 Agentic RAG 쿼리 분류

| 분류 | 전략 | 설명 |
|------|------|------|
| SIMPLE | 키워드 직접 검색 | 명확한 질의 |
| VAGUE | HyDE 의사 문서 생성 → 임베딩 | 암묵적 의도 |
| COMPLEX | 쿼리 분해 → 서브쿼리 검색 → 결과 병합 | 복합 질의 |

### 5.5 모델 라우팅 (`model-router`)

```
IF 라우팅 비활성 → agentConfig.mdlNm 사용
IF 스킬 매칭됨 → 라우팅 바이패스 (강한 모델 필요)
ELSE → classifyQueryComplexity(query)
  SIMPLE → model_simple (예: claude-haiku)
  VAGUE  → model_vague  (예: claude-sonnet)
  COMPLEX → model_complex (예: claude-opus)
```

**Skill-Triggered 모델 업그레이드**: `skill_get` 호출 시 → COMPLEX 모델로 자동 승격

### 5.6 Multi-Provider LLM 클라이언트

SDK 없이 native fetch 구현:

| 프로바이더 | API 엔드포인트 | 특이사항 |
|-----------|---------------|---------|
| OpenAI | `POST /v1/chat/completions` | tool_calls 포맷 |
| Anthropic | `POST /v1/messages` | tool_use content blocks, prompt caching, extended thinking |
| Ollama | `POST /api/chat` | 도구 미지원 |

**스트리밍 출력**: `AsyncGenerator<StreamDelta>`
```typescript
type StreamDelta = {
  type: 'content_delta' | 'thinking_delta' | 'tool_call_delta' | 'done';
  delta?: string;
  thinking?: string;
  toolCallIndex?: number;
  toolCallId?: string;
  toolName?: string;
  toolArgsDelta?: string;
  finishReason?: string;
  usage?: { inputTokens: number; outputTokens: number; totalTokens: number };
};
```

### 5.7 에러 분류 및 재시도

| 카테고리 | 재시도 | 전략 |
|----------|--------|------|
| AUTH (401/403) | 불가 | 즉시 실패, 폴백 건너뜀 |
| RATE_LIMIT (429) | 가능 | Exponential backoff, Retry-After 헤더 존중 |
| CONTEXT_OVERFLOW (400) | 가능 | Compaction 트리거 후 재시도 |
| TIMEOUT (408) | 가능 | Exponential backoff |
| SERVER (5xx) | 가능 | Exponential backoff |
| NETWORK | 가능 | Exponential backoff |

**재시도 설정**: maxRetries=2, baseDelay=1s, maxDelay=30s, backoffFactor=2

**모델 폴백**: `agentConfig.stng.fallbackModels[]` 순회 → 다른 프로바이더 자동 전환

---

## 6. 도구 및 플러그인 시스템

### 6.1 Plugin 아키텍처 (3계층)

```
Layer 1: PLUGIN.md (리소스 정의)
  └── resources/plugins/{name}/PLUGIN.md
  └── YAML frontmatter: 도구 코드, 이름, 설명, 파라미터 스키마

Layer 2: PluginManager (싱글톤)
  └── 서버 시작 시 초기화 (instrumentation.ts)
  └── PLUGIN.md 로드 → 핸들러 바인딩 → ToolRegistry 등록

Layer 3: Handler Registry (핸들러 매핑)
  └── 도구 코드 → 핸들러 함수
  └── 예: 'hitl_prompt' → executeHitlPrompt(args, ctx)
```

### 6.2 도구 실행 파이프라인

```
LLM tool_calls[] 반환
  → parseToolArguments() (JSON → typed object)
  → dispatch(toolName, args, context)
  → PluginManager.getToolHandler() (핸들러 조회)
  → Handler 실행 (30초 타임아웃)
  → ToolResult { result?, error? } 반환
  → formatToolResult() (LLM용 직렬화)
  → tool message를 대화 히스토리에 추가
```

### 6.3 ToolExecutionContext

```typescript
interface ToolExecutionContext {
  wsId: number;                              // 워크스페이스 ID
  userId: number;                            // 사용자 ID
  agntId: number;                            // 에이전트 ID
  cnvrstnId?: number;                        // 대화 ID
  secretStore?: Map<string, string>;         // 턴 단위 시크릿 저장소
  parentRunId?: number;                      // 서브에이전트 부모 ID
  spawnDepth?: number;                       // 중첩 깊이
  sseWriter?: SSEWriter;                     // SSE 이벤트 작성기
  subscriptionId?: number;                   // 구독 ID
  requestHeaders?: Record<string, string>;   // 요청 헤더
}
```

### 6.4 Tool Resolution

```
Agent config.enblToolCds[]
  + Skill allowed-tools[] (병합된 스킬에서 추출)
  + MCP 서버 tool_schma_cache (캐시된 스키마)
  → PluginManager tool registry
  → OpenAI Tool[] 포맷 출력
```

### 6.5 내장 도구 목록

| 카테고리 | 도구 코드 | 설명 |
|----------|----------|------|
| 검색 | `web_search` | 웹 검색 |
| 검색 | `news_search` | 뉴스 검색 |
| 검색 | `image_search` | 이미지 검색 |
| 검색 | `maps_search` | 지도/장소 검색 |
| 메모리 | `memory_save` | 메모리 저장 (pgvector) |
| 메모리 | `memory_search` | 메모리 검색 |
| 그래프 | `graph_memory_save` | 그래프 메모리 저장 (Neo4j) |
| 그래프 | `graph_memory_search` | 그래프 메모리 검색 |
| 지식 | `knowledge_search` | RAG 검색 |
| 유틸 | `calculator` | 계산기 (재귀하강 파서) |
| 유틸 | `datetime` | 날짜/시간 |
| 유틸 | `environment` | 환경 정보 |
| 유틸 | `cron` | 크론 작업 관리 |
| UI | `ui_layout_query` | UI 레이아웃 조회 |
| UI | `ui_section_upsert` | UI 섹션 업서트 |
| 스프레드시트 | `spreadsheet_read` | 엑셀 읽기 |
| 스프레드시트 | `spreadsheet_write` | 엑셀 쓰기 |
| 스킬 | `skill_get` | 스킬 조회 (온디맨드) |
| 스킬 | `skill_create/update/delete` | 스킬 CRUD |
| 서브에이전트 | `subagent_spawn` | 서브에이전트 생성 |
| 서브에이전트 | `subagent_manage` | 서브에이전트 관리 |
| HITL | `hitl_prompt` | Human-in-the-Loop 질문 |
| 연동 | `slack_action` | Slack 액션 |
| 연동 | `openapi_query` | OpenAPI 스펙 조회/실행 |

### 6.6 HITL (Human-in-the-Loop) 상세

```
① LLM이 hitl_prompt(question, header, options, multi_select) 호출
② 서버: 입력 검증 (question 필수, header 최대 12자, options 2~4개)
③ SSE 'hitl_question' 이벤트 발행:
   { question, header, options: [{label, description, value}], multiSelect }
④ executeLoop 즉시 중단 (LLM 재호출 없음)
⑤ 프론트엔드: HitlMessage 컴포넌트 렌더링
⑥ 사용자 선택/입력 → 후속 user message로 전송
⑦ 대화 재개 (새로운 executeLoop 시작)
```

---

## 7. 스킬 시스템

### 7.1 스킬 스코프 (3단계)

```
GLOBAL (resources/skills/) → WORKSPACE (TB_AI_SKILL_DEF) → Agent 매핑 필터 (TR_AI_CNFG_SKILL)
```

**Skill Merger 로직**:
1. GLOBAL 스킬 로드 (서버 시작 시 캐시)
2. WORKSPACE 스킬로 오버라이드
3. 에이전트 매핑 존재 시 → 화이트리스트 필터링 (enbl_yn='Y'만)
4. 매핑 없으면 → 전체 스킬 사용 가능

### 7.2 스킬 정의 형식

```yaml
---
name: skill-name
description: 스킬 설명
autoActivate: false          # true=항상 활성, false=온디맨드
allowed-tools: [tool_a, tool_b]   # 에이전트 도구에 자동 병합
required-tools: [hitl_prompt]     # WorkflowGuard 트리거
app:
  tags: [excel, upload]
  emoji: "📊"
  version: "1.0.0"
---

[스킬 상세 지침 — Markdown]
```

### 7.3 스킬 활성화 모드

| 모드 | 트리거 | 주입 방식 |
|------|--------|----------|
| Direct Injection | 에이전트 프롬프트 frontmatter `skills[]` | 시스템 메시지에 직접 주입 |
| On-Demand | `skill_get` 도구로 런타임 요청 | XML 카탈로그에서 fetch |
| Auto-Classify | 사용자 쿼리 분석 → 스킬 매칭 | 분류기가 자동 주입 |

### 7.4 스킬 분류기 (Agentic Skill Matching)

- 사용자 쿼리를 스킬 카탈로그와 비교
- 매칭된 스킬 자동 주입 + `skill_get` 고려
- **라우팅 바이패스**: 스킬 매칭 시 복잡도 기반 모델 라우팅 무시 (강한 모델 필요)

---

## 8. 디렉토리 구조

```
{project}/
├── app/
│   └── api/
│       └── agent/
│           └── v1/
│               └── ai/
│                   ├── conversations/
│                   │   └── [convId]/
│                   │       ├── messages/route.ts      # GET(목록), POST(SSE 전송)
│                   │       └── ui-actions/route.ts     # POST(UI 액션)
│                   ├── agents/
│                   │   ├── route.ts                    # GET(에이전트 목록)
│                   │   └── [agntCd]/route.ts           # GET(에이전트 상세)
│                   ├── agent-configs/
│                   │   └── [agentId]/
│                   │       ├── route.ts                # GET/PUT(설정)
│                   │       ├── skills/route.ts         # GET/POST(스킬 매핑)
│                   │       ├── knowledge-bases/        # GET/POST/DELETE
│                   │       └── mcp-servers/            # GET/POST/DELETE
│                   ├── knowledge-bases/
│                   │   ├── route.ts                    # GET/POST
│                   │   └── [kbId]/
│                   │       ├── route.ts                # GET/PUT/DELETE
│                   │       └── documents/route.ts      # GET/POST/DELETE
│                   ├── memories/route.ts               # GET/POST/DELETE
│                   ├── graph/                           # search, stats, entities
│                   ├── subagents/                       # spawn, status, steer, kill
│                   ├── secrets/route.ts                 # GET/POST/DELETE
│                   ├── sys-credentials/                 # CRUD + OAuth flow
│                   └── channel-configs/route.ts         # GET + webhook
├── lib/
│   ├── ai/
│   │   ├── runtime/
│   │   │   ├── agent-runner.ts         # Core loop (executeLoop, runAgentStream)
│   │   │   ├── context-builder.ts      # 10-step context pipeline
│   │   │   ├── llm-client.ts           # Multi-provider LLM (native fetch)
│   │   │   ├── stream-handler.ts       # SSE stream utilities
│   │   │   ├── loop-guard.ts           # 무한루프 방지 (3규칙)
│   │   │   ├── context-guard.ts        # 토큰 예산 보호
│   │   │   ├── model-router.ts         # 복잡도 기반 모델 선택
│   │   │   ├── model-fallback.ts       # 다중 프로바이더 폴백
│   │   │   ├── error-classifier.ts     # 에러 분류
│   │   │   └── retry.ts               # Exponential backoff
│   │   ├── tools/
│   │   │   ├── tool-resolver.ts        # 도구 가용성 해석
│   │   │   ├── tool-dispatcher.ts      # 도구 라우팅/실행
│   │   │   ├── plugin-manager.ts       # 플러그인 생명주기
│   │   │   ├── handler-registry.ts     # 핸들러 매핑
│   │   │   └── handlers/              # 20+ 핸들러 구현
│   │   │       ├── hitl-prompt.ts
│   │   │       ├── web-search.ts
│   │   │       ├── memory.ts
│   │   │       ├── knowledge.ts
│   │   │       ├── calculator.ts
│   │   │       ├── spreadsheet.ts
│   │   │       ├── subagent.ts
│   │   │       ├── skill-crud.ts
│   │   │       ├── ui-sync.ts
│   │   │       └── ...
│   │   ├── skills/
│   │   │   └── skill-merger.ts         # 3단계 스킬 병합
│   │   ├── memory/
│   │   │   ├── memory-service.ts       # pgvector 메모리
│   │   │   └── graph-memory.ts         # Neo4j 그래프 메모리
│   │   ├── rag/
│   │   │   ├── rag-service.ts          # Agentic RAG
│   │   │   ├── query-classifier.ts     # SIMPLE/VAGUE/COMPLEX
│   │   │   └── hyde.ts                 # HyDE 의사 문서 생성
│   │   ├── constants.ts                # 모든 상수 중앙 집중
│   │   ├── model/
│   │   │   └── model-catalog.ts        # 모델 스펙 (가격, 토큰 한도)
│   │   └── i18n/
│   │       └── locale-resolver.ts
│   ├── auth/
│   │   └── gateway-auth.ts             # Gateway 헤더 파싱
│   └── db/
│       ├── index.ts                    # Drizzle 싱글톤
│       └── schema/
│           ├── ai.ts                   # 대화, 메시지, 메모리, 토큰, 지식
│           ├── ai-agent.ts             # 에이전트, 카테고리
│           ├── ai-skill.ts             # 스킬, 매핑
│           ├── ai-subagent.ts          # 서브에이전트
│           ├── ai-secret.ts            # 시크릿
│           ├── ai-sys-cred.ts          # 시스템 자격 증명
│           ├── ai-channel.ts           # 채널
│           └── ai-project.ts           # 프로젝트
├── resources/
│   ├── prompts/
│   │   ├── _default.md                 # 기본 시스템 프롬프트
│   │   └── {agntCd}.md                 # 에이전트별 프롬프트
│   ├── skills/
│   │   └── {skill-name}/SKILL.md       # 글로벌 스킬 정의
│   ├── plugins/
│   │   └── {tool-name}/PLUGIN.md       # 도구 플러그인 정의
│   └── templates/
│       └── ui/                         # UI 레이아웃 템플릿
└── instrumentation.ts                  # 서버 시작 시 리소스 로딩
```

---

## 9. 구현 순서

### Phase 1: 기반 인프라 (DB + LLM + 리소스)

1. Drizzle ORM 설정 및 DB 스키마 정의 (26개 테이블)
2. DB 마이그레이션 실행 (pgvector 확장 포함)
3. 환경 변수 설정 (`.env.example`)
4. 리소스 로더 (prompts, skills, plugins 파싱)
5. 싱글톤 초기화 (`instrumentation.ts`)

### Phase 2: AI 런타임 코어

1. LLM 클라이언트 (native fetch — Anthropic/OpenAI/Ollama)
2. SSE 스트림 핸들러 (createSSEStream, SSEWriter, keep-alive)
3. 에이전트 러너 코어 루프 (executeLoop)
4. Context Builder (10단계 파이프라인)
5. 안전장치 4종 (LoopGuard, ToolContextTracker, WorkflowGuard, ContextGuard)

### Phase 3: 도구 및 플러그인

1. Plugin Manager + Handler Registry
2. Tool Resolver + Tool Dispatcher
3. 핵심 도구 구현 (calculator, datetime, web_search, memory, hitl_prompt)
4. HITL 프로세스 (SSE 이벤트 + 루프 중단)
5. 스킬 CRUD 도구 (skill_get, skill_create 등)

### Phase 4: 에이전트 설정 + 지식 베이스

1. 에이전트 CRUD API (카테고리, 설정, 스킬 매핑)
2. 지식 베이스 CRUD + 문서 업로드/청크 생성
3. RAG 서비스 (Agentic 쿼리 분류, HyDE, 리랭킹)
4. 메모리 서비스 (pgvector flat + Neo4j graph)
5. 통합 메모리 컨텍스트 (하이브리드 랭킹)

### Phase 5: 모델 라우팅 + 서브에이전트

1. 모델 라우터 (복잡도 분류 → 모델 선택)
2. 모델 폴백 (프로바이더 순회)
3. 에러 분류기 + 재시도 전략
4. 서브에이전트 스폰/관리/킬 (깊이/자식 수 제한)
5. 서브에이전트 SSE 이벤트 (spawned/completed/failed/killed)

### Phase 6: 미들웨어 + 채널 + 시크릿

1. Gateway 인증 미들웨어 (withGatewayAuth)
2. AI 컨텍스트 미들웨어 (withAiContext)
3. 크레딧 미들웨어 (withCredits)
4. 워크스페이스 시크릿 관리 (AES-256-GCM 암호화)
5. OAuth 플로우 (initiate/callback/exchange)
6. 채널 설정 + 웹훅 수신 (Slack/Teams)

### Phase 7: 스킬 시스템 + 대화 관리

1. Skill Merger (GLOBAL + WORKSPACE → Agent 필터)
2. 스킬 분류기 (Agentic Skill Matching)
3. Skill-Triggered 모델 업그레이드
4. 대화 CRUD (생성, 목록, 수정, 삭제, 고정)
5. 대화 Compaction (장기 대화 요약)
6. 자동 제목 생성 + 메모리 자동 추출

### Phase 8: 통합 및 최적화

1. Anthropic Prompt Caching 적용
2. Extended Thinking 모드
3. 토큰 사용량 로깅 + 포탈 리포팅
4. MCP 서버 등록/스키마 캐싱
5. 크론 서비스 (분산 스케줄러)
6. UI 액션 처리

---

## 부록: 핵심 상수

```typescript
// lib/ai/constants.ts
const MAX_TOOL_ITERATIONS = 10;
const LOOP_GUARD_MAX_EXACT_REPEATS = 3;
const LOOP_GUARD_MAX_SAME_TOOL = 5;        // UI 도구는 8
const MAX_WORKFLOW_GUARD_RETRIES = 2;
const MEMORY_SEARCH_MAX_RESULTS = 6;
const GRAPH_MEMORY_MAX_RESULTS = 5;
const RAG_SEARCH_MAX_RESULTS = 5;
const HYBRID_RANKING_TOP_K = 10;
const MIN_MESSAGES_FOR_EXTRACTION = 4;
const MIN_TURNS_BETWEEN_EXTRACTION = 3;
const TOOL_EXECUTION_TIMEOUT_MS = 30_000;
const SSE_KEEPALIVE_INTERVAL_MS = 15_000;
const RETRY_MAX_RETRIES = 2;
const RETRY_BASE_DELAY_MS = 1_000;
const RETRY_MAX_DELAY_MS = 30_000;
const RETRY_BACKOFF_FACTOR = 2;
```
