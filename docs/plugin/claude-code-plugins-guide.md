# Claude Code 공식 플러그인 가이드

> 작성일: 2026-03-27 | 설치 환경: macOS Darwin 25.3.0

## 목차

- [플러그인 관리 명령어](#플러그인-관리-명령어)
- [공식 플러그인 (claude-plugins-official)](#공식-플러그인-claude-plugins-official)
  - [개발 워크플로우](#개발-워크플로우)
  - [코드 품질](#코드-품질)
  - [플러그인/스킬 개발](#플러그인스킬-개발)
  - [LSP (Language Server Protocol)](#lsp-language-server-protocol)
  - [출력 스타일](#출력-스타일)
  - [외부 연동](#외부-연동)
- [Knowledge Work 플러그인 (knowledge-work-plugins)](#knowledge-work-플러그인-knowledge-work-plugins)
  - [엔지니어링](#엔지니어링)
  - [제품/프로젝트 관리](#제품프로젝트-관리)
  - [디자인](#디자인)
  - [데이터 분석](#데이터-분석)
  - [영업/마케팅](#영업마케팅)
  - [비즈니스 운영](#비즈니스-운영)
  - [법무/재무/인사](#법무재무인사)
  - [생산성](#생산성)
- [설치 현황 요약](#설치-현황-요약)

---

## 플러그인 관리 명령어

```bash
# 설치된 플러그인 목록 확인
claude plugins list

# 플러그인 설치 (전역)
claude plugin install <plugin-name>@<marketplace> -s user

# 플러그인 설치 (프로젝트 범위)
claude plugin install <plugin-name>@<marketplace> -s project

# 플러그인 제거
claude plugin uninstall <plugin-name>@<marketplace>

# 플러그인 업데이트
claude plugins update
```

### 마켓플레이스 목록

| 마켓플레이스 | 소스 | 설명 |
|-------------|------|------|
| `claude-plugins-official` | `anthropics/claude-plugins-official` | Anthropic 공식 개발 도구 |
| `knowledge-work-plugins` | `anthropics/knowledge-work-plugins` | Anthropic Knowledge Work 업무 도구 |

---

## 공식 플러그인 (claude-plugins-official)

### 개발 워크플로우

---

#### commit-commands

Git 워크플로우를 간소화하는 커밋/푸시/PR 명령어 모음.

**설치**
```bash
claude plugin install commit-commands@claude-plugins-official -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/commit` | Git 커밋 생성 (변경사항 분석 후 커밋 메시지 자동 작성) |
| `/commit-push-pr` | 커밋 + 푸시 + PR 생성을 한번에 실행 |
| `/clean_gone` | 리모트에서 삭제된 로컬 브랜치 일괄 정리 |

**활용 예시**
```
/commit                    # 현재 변경사항으로 커밋 생성
/commit-push-pr            # 커밋 → 푸시 → PR 생성 한번에
/clean_gone                # stale 브랜치 정리
```

---

#### feature-dev

기능 개발의 전체 라이프사이클을 7단계로 가이드하는 체계적 개발 워크플로우.

**설치**
```bash
claude plugin install feature-dev@claude-plugins-official -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/feature-dev` | 7단계 기능 개발 워크플로우 실행 |

**7단계 워크플로우**
1. **Discovery** — 요구사항 명확화
2. **Codebase Exploration** — 2~3개 탐색 에이전트가 병렬로 기존 코드베이스 분석
3. **Clarifying Questions** — 설계 전 모호한 점 질문
4. **Architecture Design** — 2~3개 설계 에이전트가 서로 다른 아키텍처 제안 + 트레이드오프 비교
5. **Implementation** — 선택된 설계에 따라 구현
6. **Quality Review** — 3개 리뷰어가 단순성/버그/컨벤션 검사
7. **Summary** — 구현 결과 문서화

**전용 에이전트**

| 에이전트 | 설명 |
|---------|------|
| `code-explorer` | 코드베이스 깊이 분석 (실행 경로 추적, 아키텍처 매핑) |
| `code-architect` | 아키텍처 설계 (파일 구조, 컴포넌트 설계, 데이터 플로우) |
| `code-reviewer` | 버그, 보안, 품질, 컨벤션 리뷰 |

**활용 예시**
```
/feature-dev 사용자 프로필 편집 기능 추가
/feature-dev API rate limiting 구현
```

---

#### frontend-design

프로덕션 수준의 고품질 프론트엔드 UI를 생성하는 디자인 스킬.

**설치**
```bash
claude plugin install frontend-design@claude-plugins-official -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/frontend-design` | 독창적이고 세련된 프론트엔드 인터페이스 생성 |

**특징**
- 20+ 미학적 방향 선택 (minimalist, brutalist, art deco, organic, luxury 등)
- 커스텀 타이포그래피 (제네릭 폰트 회피)
- 모션/애니메이션 (staggered reveal, scroll-trigger, hover state)
- 비대칭 레이아웃, 오버랩, 대각선 흐름
- 배경 이펙트 (그라디언트, 노이즈, 텍스처, 기하학 패턴)
- **제네릭 AI 미학 회피** — 독창적인 디자인 결과물

**활용 예시**
```
/frontend-design SaaS 대시보드 랜딩 페이지
/frontend-design 이커머스 상품 상세 페이지 (luxury 스타일)
```

---

#### ralph-loop

동일 프롬프트를 반복 실행하여 점진적으로 품질을 개선하는 자기참조 루프 (Ralph Wiggum 기법).

**설치**
```bash
claude plugin install ralph-loop@claude-plugins-official -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/ralph-loop` | Ralph 루프 시작 (반복적 자가 개선) |
| `/cancel-ralph` | 활성 Ralph 루프 취소 |

**작동 방식**
1. 프롬프트 실행 → Claude가 작업 수행
2. Stop hook가 종료 시도를 인터셉트
3. 동일 프롬프트가 다시 피드백 → 이전 결과 위에 개선
4. 완료 약속(completion promise) 감지 시 종료
5. 최대 반복 횟수 안전장치 포함

**활용 예시**
```
/ralph-loop 이 테스트 파일의 커버리지를 95%까지 올려줘
/ralph-loop UI 컴포넌트를 접근성 기준에 맞게 개선해
```

---

### 코드 품질

---

#### code-review

PR에 대해 5개의 전문 에이전트가 병렬로 코드 리뷰를 수행하는 자동화 도구.

**설치**
```bash
claude plugin install code-review@claude-plugins-official -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/code-review` | PR에 대한 자동화된 멀티 에이전트 코드 리뷰 실행 |

**리뷰 에이전트 (5개 병렬 실행)**
- CLAUDE.md 컴플라이언스 체커 (2개)
- 버그 감지기
- 히스토리 분석기 (git blame 기반)
- 코멘트 분석기

**특징**
- 신뢰도 기반 점수 (0-100), 임계값 80 이상만 보고
- 자동 false positive 필터링
- GitHub PR에 리뷰 코멘트 자동 게시

---

#### pr-review-toolkit

6개의 전문 리뷰 에이전트 번들로 PR의 다양한 품질 차원을 분석.

**설치**
```bash
claude plugin install pr-review-toolkit@claude-plugins-official -s user
```

**전용 에이전트**

| 에이전트 | 분석 영역 |
|---------|----------|
| `comment-analyzer` | 코드 코멘트 정확성 및 유지보수성 |
| `pr-test-analyzer` | 테스트 커버리지 품질 및 완전성 |
| `silent-failure-hunter` | 에러 핸들링 및 사일런트 실패 감지 |
| `type-design-analyzer` | 타입 설계 품질 및 불변성 검증 |
| `code-reviewer` | CLAUDE.md 준수 및 버그 감지 |
| `code-simplifier` | 코드 간소화 및 리팩토링 |

---

#### code-simplifier

최근 수정된 코드의 명확성, 일관성, 유지보수성을 자동으로 개선하는 에이전트.

**설치**
```bash
claude plugin install code-simplifier@claude-plugins-official -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/simplify` | 변경된 코드의 재사용성, 품질, 효율성 리뷰 후 개선 |

**특징**
- 최근 수정된 코드에 자동 초점
- 중복 제거, 복잡도 감소
- 프로젝트 표준(ES modules, React 패턴 등) 적용
- 기능은 100% 보존

---

#### security-guidance

파일 편집 시 보안 취약점을 자동 감지하여 경고하는 훅 기반 플러그인.

**설치**
```bash
claude plugin install security-guidance@claude-plugins-official -s user
```

**감지 항목**
- Command Injection
- XSS (Cross-Site Scripting)
- 안전하지 않은 코드 패턴

**특징**
- 훅 기반으로 파일 편집 시 자동 트리거
- 별도 명령어 없이 백그라운드에서 작동

---

### 플러그인/스킬 개발

---

#### plugin-dev

Claude Code 플러그인 개발의 모든 측면을 가이드하는 종합 도구.

**설치**
```bash
claude plugin install plugin-dev@claude-plugins-official -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/plugin-structure` | 플러그인 디렉토리 구조 설정 가이드 |
| `/skill-development` | 스킬(SKILL.md) 생성 및 개발 |
| `/command-development` | 슬래시 커맨드(.md) 개발 |
| `/agent-development` | 서브에이전트(.md) 생성 및 개발 |
| `/hook-development` | 훅(hooks.json) 생성 및 설정 |
| `/mcp-integration` | MCP 서버 연동 설정 |
| `/plugin-settings` | 플러그인 설정(plugin.json) 관리 |

**활용 예시**
```
/plugin-structure         # 새 플러그인 프로젝트 구조 생성
/skill-development        # 새 스킬 SKILL.md 작성
/agent-development        # 서브에이전트 정의 작성
```

---

#### skill-creator

스킬의 전체 개발 라이프사이클을 관리 — 생성, 테스트, 벤치마크, 반복 개선.

**설치**
```bash
claude plugin install skill-creator@claude-plugins-official -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/skill-creator` | 새 스킬 생성, 기존 스킬 개선, 성능 측정 |

**워크플로우**
1. 스킬 의도 캡처 및 인터뷰
2. 엣지 케이스 탐색
3. SKILL.md 작성 (메타데이터 포함)
4. 테스트 케이스 생성
5. 평가 및 벤치마크 실행
6. 정량적 지표 분석
7. 반복적 스킬 개선

---

#### mcp-server-dev

MCP 서버 설계 및 구현을 가이드하는 종합 스킬. 배포 모델, 도구 패턴, 인증 등을 포함.

**설치**
```bash
claude plugin install mcp-server-dev@claude-plugins-official -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/build-mcp-server` | MCP 서버 개발 진입점 (유스케이스 분석 → 배포 모델 결정 → 도구 패턴 선택) |
| `/build-mcp-app` | 인터랙티브 UI 위젯이 포함된 MCP 앱 개발 |
| `/build-mcpb` | MCPB (번들 로컬 서버) 개발 |

**지원 배포 모델**
- Remote HTTP (CloudFlare Workers)
- MCPB (번들 로컬 서버)
- Local stdio
- MCP Apps (인터랙티브 UI)

**지원 인증 방식**: API Key, OAuth 2.0, CIMD, DCR

---

#### claude-code-setup

코드베이스를 분석하여 최적의 Claude Code 자동화를 추천하는 분석 도구.

**설치**
```bash
claude plugin install claude-code-setup@claude-plugins-official -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/claude-automation-recommender` | 코드베이스 분석 후 자동화 추천 (hooks, skills, MCP, agents, plugins) |

**추천 카테고리**
- MCP 서버 (context7, Playwright, Supabase, GitHub, Slack 등)
- 스킬 (사용 가능한 플러그인 기반)
- 훅 (자동화 규칙)
- 서브에이전트
- 플러그인

---

#### claude-md-management

CLAUDE.md 파일의 품질을 감사하고 개선하는 도구.

**설치**
```bash
claude plugin install claude-md-management@claude-plugins-official -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/claude-md-improver` | CLAUDE.md 파일 감사 및 개선 |

**평가 기준 (6개, A-F 등급)**
1. 명령어/워크플로우 명시
2. 아키텍처 명확성
3. 비자명 패턴 설명
4. 간결성
5. 최신성
6. 실행 가능성

---

#### hookify

대화 패턴을 분석하여 원치 않는 행동을 방지하는 훅을 생성하는 도구.

**설치**
```bash
claude plugin install hookify@claude-plugins-official -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/hookify` | 대화 분석으로 방지할 행동 감지 후 훅 생성 |
| `/writing-rules` | 훅 규칙 작성 가이드 |
| `/list` | 설정된 훅 규칙 목록 |
| `/configure` | 훅 규칙 활성화/비활성화 |
| `/help` | 도움말 |

**지원 이벤트 타입**: `bash`, `file`, `stop`, `prompt`, `all`
**조건 타입**: `regex_match`, `contains`, `equals`, `not_contains`, `starts_with`, `ends_with`
**액션**: `warn` (경고), `block` (차단)

---

### LSP (Language Server Protocol)

코드 인텔리전스를 강화하는 언어 서버 플러그인. 코드 완성, 타입 체크, 에러 감지 등을 제공.

---

#### typescript-lsp

**설치**
```bash
claude plugin install typescript-lsp@claude-plugins-official -s user
```

| 항목 | 내용 |
|------|------|
| 언어 | TypeScript / JavaScript |
| 기능 | 코드 완성, 타입 체크, 에러 감지, 리팩토링 |
| 별도 명령어 | 없음 (자동 활성화) |

---

#### jdtls-lsp

**설치**
```bash
claude plugin install jdtls-lsp@claude-plugins-official -s user
```

| 항목 | 내용 |
|------|------|
| 언어 | Java |
| 기능 | 코드 완성, 에러 체크, 리팩토링, 의존성 분석 |
| 별도 명령어 | 없음 (자동 활성화) |

---

#### pyright-lsp

**설치**
```bash
claude plugin install pyright-lsp@claude-plugins-official -s user
```

| 항목 | 내용 |
|------|------|
| 언어 | Python |
| 기능 | 코드 완성, 타입 체크, 에러 감지 |
| 별도 명령어 | 없음 (자동 활성화) |

---

### 출력 스타일

---

#### learning-output-style

의사결정 포인트에서 사용자에게 코드 기여를 요청하는 인터랙티브 학습 모드.

**설치**
```bash
claude plugin install learning-output-style@claude-plugins-official -s user
```

**특징**
- 모든 코드를 자동으로 작성하지 않고, 주요 결정 포인트에서 사용자 입력 요청
- 학습 중심 워크플로우
- 별도 명령어 없이 출력 스타일로 적용

---

### 외부 연동

---

#### context7

라이브러리/프레임워크의 최신 공식 문서와 코드 예제를 실시간으로 조회하는 MCP 서버.

**설치**
```bash
claude plugin install context7@claude-plugins-official -s user
```

**특징**
- 버전별 문서 조회 (React, Express, FastAPI, Django, Prisma, Stripe, AWS SDK 등)
- 소스 리포지토리에서 직접 코드 예제 추출
- 별도 명령어 없이 MCP 도구로 자동 사용

---

#### telegram

Claude Code와 Telegram 메신저를 연결하는 MCP 서버. 봇을 통해 양방향 메시징 지원.

**설치**
```bash
claude plugin install telegram@claude-plugins-official -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/telegram:configure` | Telegram 봇 토큰 설정 및 채널 구성 |
| `/telegram:access` | 접근 제어 관리 (페어링 승인, 허용 목록, DM/그룹 정책) |

**MCP 도구**
- `reply` — Telegram 채팅에 텍스트/파일 전송 (최대 50MB)
- `react` — 이모지 반응 추가
- `edit_message` — 이전 메시지 편집

**필요 환경 변수**: `TELEGRAM_BOT_TOKEN`

---

## Knowledge Work 플러그인 (knowledge-work-plugins)

> 모든 Knowledge Work 플러그인은 **Standalone + Supercharged** 설계를 따릅니다.
> 수동 입력만으로도 작동하지만, MCP로 외부 도구를 연결하면 기능이 대폭 강화됩니다.

### 엔지니어링

---

#### engineering

엔지니어링 워크플로우 전반 — 스탠드업, 코드 리뷰, 아키텍처 결정, 인시던트 대응, 기술 문서.

**설치**
```bash
claude plugin install engineering@knowledge-work-plugins -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/standup` | 최근 활동(커밋, PR, 티켓)에서 스탠드업 업데이트 생성 |
| `/review` | 코드 변경 리뷰 (보안, 성능, 스타일, 정확성) |
| `/debug` | 구조화된 디버깅 세션 (재현 → 격리 → 진단 → 수정) |
| `/architecture` | 아키텍처 결정 문서(ADR) 생성 또는 평가 |
| `/incident` | 인시던트 대응 워크플로우 (트리아지 → 소통 → 완화 → 포스트모템) |
| `/deploy-checklist` | 배포 전 체크리스트 (테스트, 변경 리뷰, 의존성, 롤백 계획) |

**연동 가능 도구**: GitHub/GitLab, Linear/Jira, Datadog/New Relic, PagerDuty, Slack/Teams, Notion/Confluence

---

### 제품/프로젝트 관리

---

#### product-management

기능 스펙 작성, 로드맵 관리, 사용자 리서치 종합, 경쟁 분석까지 제품 관리 전반을 지원.

**설치**
```bash
claude plugin install product-management@knowledge-work-plugins -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/write-spec` | 문제 정의에서 기능 스펙/PRD 작성 |
| `/roadmap-update` | 로드맵 생성, 업데이트, 우선순위 재조정 |
| `/stakeholder-update` | 이해관계자 업데이트 (주간, 월간, 출시) |
| `/synthesize-research` | 인터뷰, 설문, 티켓에서 사용자 리서치 종합 |
| `/competitive-brief` | 경쟁 분석 브리프 생성 |
| `/metrics-review` | 제품 메트릭 리뷰 및 분석 |
| `/brainstorm` | 제품 아이디어/문제 공간 브레인스토밍 파트너 |

**연동 가능 도구**: Slack, Linear/Asana/Jira, Notion, Figma, Amplitude/Pendo, Intercom

---

### 디자인

---

#### design

디자인 크리틱, 디자인 시스템 관리, UX 카피라이팅, 접근성 감사, 개발자 핸드오프까지.

**설치**
```bash
claude plugin install design@knowledge-work-plugins -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/critique` | 디자인 피드백 (유저빌리티, 시각 계층, 접근성, 일관성) |
| `/design-system` | 디자인 시스템 감사, 문서화, 확장 |
| `/handoff` | 개발자 핸드오프 스펙 생성 (측정값, 토큰, 상태, 인터랙션) |
| `/ux-copy` | UX 카피 작성/리뷰 (마이크로카피, 에러 메시지, 온보딩) |
| `/accessibility` | 접근성 감사 (WCAG 2.1 AA, 색상 대비, 키보드 내비게이션) |
| `/research-synthesis` | 사용자 리서치 종합 (인터뷰, 설문, 유저빌리티 테스트) |

**연동 가능 도구**: Figma, Intercom/Productboard, Linear/Asana/Jira, Notion, Amplitude/Mixpanel

---

### 데이터 분석

---

#### data

SQL 작성, 데이터 탐색, 시각화, 대시보드 구축, 통계 분석까지 데이터 업무 전반을 지원.

**설치**
```bash
claude plugin install data@knowledge-work-plugins -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/analyze` | 데이터 질문 답변 (간단한 조회부터 전체 분석까지) |
| `/explore-data` | 데이터셋 프로파일링 (형태, 품질, 패턴 파악) |
| `/write-query` | 방언별 최적화된 SQL 작성 (Snowflake, BigQuery, PostgreSQL 등) |
| `/create-viz` | Python으로 출판 수준 시각화 생성 (matplotlib, seaborn, plotly) |
| `/build-dashboard` | 인터랙티브 HTML 대시보드 구축 (Chart.js, 필터, 테이블) |
| `/validate` | 분석 QA — 방법론, 정확성, 편향 검사 |

**연동 가능 도구**: Snowflake/BigQuery/Databricks, Amplitude/Looker, Jupyter, Google Sheets

---

#### enterprise-search

연결된 모든 도구에서 통합 검색. 이메일, 채팅, 문서, 위키를 한곳에서 검색.

**설치**
```bash
claude plugin install enterprise-search@knowledge-work-plugins -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/search` | 연결된 모든 소스에서 통합 검색 |
| `/digest` | 일간/주간 활동 다이제스트 생성 |

**연동 가능 도구**: Slack/Teams, Gmail/Microsoft 365, Google Drive/OneDrive/Box, Notion/Confluence, Linear/Asana/Jira, HubSpot/Salesforce

---

### 영업/마케팅

---

#### sales

영업 전체 라이프사이클 — 프로스펙팅, 아웃리치, 파이프라인 관리, 콜 준비/정리, 예측.

**설치**
```bash
claude plugin install sales@knowledge-work-plugins -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/call-summary` | 콜 노트/녹취록 처리 → 액션 아이템 추출, 팔로업 이메일 작성 |
| `/forecast` | 가중치 영업 예측 (best/likely/worst 시나리오) |
| `/pipeline-review` | 파이프라인 건강도 분석, 딜 우선순위화, 주간 액션 플랜 |
| `/draft-outreach` | 프로스펙트 리서치 후 개인화된 아웃리치 작성 |
| `/call-prep` | 영업 콜 준비 (어카운트 컨텍스트, 참석자 리서치, 의제) |
| `/daily-briefing` | 일일 영업 브리핑 (미팅, 파이프라인 알림, 이메일 우선순위) |
| `/account-research` | 회사/사람 리서치 — 영업 인텔리전스 |
| `/competitive-intelligence` | 경쟁사 리서치 및 배틀카드 생성 |
| `/create-an-asset` | 맞춤형 영업 자산 생성 (랜딩 페이지, 데크, 원페이저) |

**연동 가능 도구**: HubSpot/Salesforce, Fireflies/Gong, Clay/ZoomInfo, Slack, Gmail

---

#### marketing

콘텐츠 작성, 캠페인 기획, 브랜드 리뷰, 경쟁 분석, 성과 리포트, SEO 감사.

**설치**
```bash
claude plugin install marketing@knowledge-work-plugins -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/draft-content` | 블로그, 소셜미디어, 이메일, 랜딩 페이지, 보도자료, 사례 연구 작성 |
| `/campaign-plan` | 캠페인 브리프 생성 (목표, 채널, 콘텐츠 캘린더, 성공 지표) |
| `/brand-review` | 브랜드 보이스/스타일 가이드 기준 콘텐츠 리뷰 |
| `/competitive-brief` | 경쟁사 포지셔닝 및 메시징 비교 |
| `/performance-report` | 마케팅 성과 리포트 (핵심 지표, 트렌드, 최적화 권장사항) |
| `/seo-audit` | SEO 감사 (키워드, 온페이지, 콘텐츠 갭, 기술 검사) |
| `/email-sequence` | 멀티 이메일 시퀀스 설계 (온보딩, 너처, 리엔게이지먼트) |

**연동 가능 도구**: Slack, Canva, Figma, HubSpot, Amplitude, Notion, Ahrefs, Klaviyo

---

### 비즈니스 운영

---

#### operations

벤더 관리, 프로세스 문서화, 변경 관리, 용량 계획, 컴플라이언스 추적.

**설치**
```bash
claude plugin install operations@knowledge-work-plugins -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/vendor-review` | 벤더 평가 (비용 분석, 리스크 평가, 갱신 권장) |
| `/process-doc` | 비즈니스 프로세스 문서화 (플로차트, RACI, SOP) |
| `/change-request` | 변경 관리 요청서 (영향 분석, 롤백 계획, 승인 라우팅) |
| `/capacity-plan` | 리소스 용량 계획 (워크로드 분석, 인원 모델링, 활용률 예측) |
| `/status-report` | 상태 리포트 (프로젝트 업데이트, KPI, 리스크, 액션 아이템) |
| `/runbook` | 운영 런북 생성/업데이트 (반복 작업의 단계별 절차) |

**연동 가능 도구**: ServiceNow/Zendesk, Asana/Jira, Notion/Confluence, Slack/Teams

---

#### customer-support

티켓 트리아지, 고객 응대, 에스컬레이션, 지식 베이스 관리까지 CS 워크플로우 전반.

**설치**
```bash
claude plugin install customer-support@knowledge-work-plugins -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/triage` | 티켓 분류, 우선순위 지정(P1-P4), 라우팅 |
| `/research` | 고객 질문에 대한 멀티소스 리서치 |
| `/draft-response` | 전문적인 고객 응대 메시지 작성 |
| `/escalate` | 엔지니어링/제품/리더십 에스컬레이션 패키지 |
| `/kb-article` | 해결된 이슈에서 지식 베이스 아티클 작성 |

**연동 가능 도구**: Slack, Intercom, HubSpot, Guru/Notion, Jira

---

### 법무/재무/인사

---

#### legal

계약 리뷰, NDA 트리아지, 컴플라이언스, 법적 리스크 평가, 벤더 점검.

**설치**
```bash
claude plugin install legal@knowledge-work-plugins -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/review-contract` | 계약서 리뷰 (협상 플레이북 기준 편차 감지, 레드라인 생성) |
| `/triage-nda` | NDA 신속 트리아지 (GREEN/YELLOW/RED 분류) |
| `/vendor-check` | 벤더 기존 계약 상태 통합 조회 |
| `/brief` | 법무 브리핑 생성 (일일, 주제별, 인시던트) |
| `/respond` | 일반적 법적 문의에 대한 템플릿 기반 응답 생성 |

**연동 가능 도구**: Slack/Teams, Box/Egnyte, Microsoft 365, Jira/Confluence, CLM, CRM

---

#### finance

분개, 계정 대사, 재무제표, 차이 분석, SOX 감사 지원.

**설치**
```bash
claude plugin install finance@knowledge-work-plugins -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/journal-entry` | 분개 작성 (발생주의, 감가상각, 선급금, 급여, 수익 인식) |
| `/reconciliation` | 계정 대사 (GL↔보조원장, 은행, 제3자 데이터) |
| `/income-statement` | 손익계산서 생성 (기간 비교, 차이 분석) |
| `/variance-analysis` | 차이/변동 분석 (가격/물량, 비율/믹스 분해, 워터폴 차트) |
| `/sox-testing` | SOX 컴플라이언스 테스트 (샘플 선정, 테스트 워크페이퍼, 통제 평가) |

**연동 가능 도구**: NetSuite/SAP, Snowflake/BigQuery, Google Sheets/Excel, Tableau/Looker

---

#### human-resources

채용, 온보딩, 성과 리뷰, 보상 분석, 정책 안내, 인력 분석.

**설치**
```bash
claude plugin install human-resources@knowledge-work-plugins -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/draft-offer` | 오퍼 레터 작성 (보상, 시작일, 조건) |
| `/onboarding` | 온보딩 체크리스트 및 첫 주 계획 생성 |
| `/performance-review` | 성과 리뷰 구조화 (자기 평가, 매니저 템플릿, 캘리브레이션) |
| `/policy-lookup` | 회사 정책 검색 및 설명 (PTO, 복리후생, 경비, 원격근무) |
| `/comp-analysis` | 보상 분석 (벤치마킹, 밴드 배치, 주식 리프레시) |
| `/people-report` | 인력 리포트 (헤드카운트, 이직률, 다양성, 조직 건강도) |

**연동 가능 도구**: Workday/BambooHR, Greenhouse/Lever, Pave/Radford, Slack/Teams

---

### 생산성

---

#### productivity

태스크 관리, 일일 계획, 중요한 워크 컨텍스트 메모리 구축.

**설치**
```bash
claude plugin install productivity@knowledge-work-plugins -s user
```

**명령어**

| 명령어 | 설명 |
|--------|------|
| `/start` | 태스크 + 메모리 초기화, 대시보드 오픈 |
| `/update` | stale 항목 트리아지, 메모리 갭 체크, 외부 도구 동기화 |
| `/update --comprehensive` | 이메일/캘린더/채팅 딥 스캔, 누락된 TODO 감지 |

**특징**
- **TASKS.md** — 마크다운 기반 태스크 추적
- **2계층 메모리** — CLAUDE.md (작업 메모리) + memory/ (장기 저장)
- HTML 대시보드 (보드 뷰)

**연동 가능 도구**: Slack, Microsoft 365, Notion, Asana/Linear/Jira

---

## 설치 현황 요약

### 마켓플레이스별 현황

| 마켓플레이스 | 설치 | 미설치 | 합계 |
|-------------|:----:|:-----:|:----:|
| claude-plugins-official (내장) | 20 | 12 | 32 |
| claude-plugins-official (외부) | 2 | 15 | 17 |
| knowledge-work-plugins | 13 | 2 | 15 |
| **합계** | **35** | **29** | **64** |

### 카테고리별 현황

| 카테고리 | 플러그인 | 수량 |
|---------|---------|:----:|
| 개발 워크플로우 | commit-commands, feature-dev, frontend-design, ralph-loop | 4 |
| 코드 품질 | code-review, pr-review-toolkit, code-simplifier, security-guidance | 4 |
| 플러그인/스킬 개발 | plugin-dev, skill-creator, mcp-server-dev, claude-code-setup, claude-md-management, hookify | 6 |
| LSP | typescript-lsp, jdtls-lsp, pyright-lsp | 3 |
| 출력 스타일 | learning-output-style | 1 |
| 외부 연동 | context7, telegram | 2 |
| 엔지니어링 | engineering | 1 |
| 제품 관리 | product-management | 1 |
| 디자인 | design | 1 |
| 데이터 | data, enterprise-search | 2 |
| 영업/마케팅 | sales, marketing | 2 |
| 비즈니스 운영 | operations, customer-support | 2 |
| 법무/재무/인사 | legal, finance, human-resources | 3 |
| 생산성 | productivity | 1 |

### 미설치 플러그인 (참고용)

**claude-plugins-official 내장 (미설치)**
`agent-sdk-dev`, `clangd-lsp`, `csharp-lsp`, `explanatory-output-style`, `gopls-lsp`, `kotlin-lsp`, `lua-lsp`, `math-olympiad`, `php-lsp`, `playground`, `ruby-lsp`, `rust-analyzer-lsp`, `swift-lsp`

**claude-plugins-official 외부 (미설치)**
`asana`, `discord`, `fakechat`, `firebase`, `github`, `gitlab`, `greptile`, `imessage`, `laravel-boost`, `linear`, `playwright`, `serena`, `slack`, `supabase`, `terraform`

**knowledge-work-plugins (미설치)**
`bio-research`, `cowork-plugin-management`
