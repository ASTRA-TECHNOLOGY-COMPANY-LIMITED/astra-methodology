---
name: astra-checklist
description: "ASTRA Sprint 0 완료 체크리스트를 검증합니다. 필수 파일, 설정, 품질 게이트 구성을 확인합니다."
allowed-tools: Read, Bash, Glob, Grep
---

# ASTRA Sprint 0 완료 체크리스트 검증

현재 프로젝트의 ASTRA Sprint 0 세팅이 올바르게 완료되었는지 검증합니다.

## 검증 항목

### A. 프로젝트 구조 검증

다음 파일/디렉토리의 존재 여부를 확인합니다:

| 경로 | 필수 | 설명 |
|------|------|------|
| `CLAUDE.md` | 필수 | 프로젝트 AI 규칙 |
| `.claude/settings.json` | 선택 | 프로젝트별 설정 |
| `docs/design-system/design-tokens.css` | 필수 | 디자인 토큰 |
| `docs/design-system/components.md` | 필수 | 컴포넌트 가이드 |
| `docs/design-system/layout-grid.md` | 필수 | 레이아웃 그리드 |
| `docs/blueprints/overview.md` | 필수 | 프로젝트 개요 |
| `docs/blueprints/database-design.md` | 필수 | 중앙 DB 설계 문서 |
| `docs/prompts/sprint-1.md` | 필수 | 첫 스프린트 프롬프트 맵 |

### B. CLAUDE.md 내용 검증

CLAUDE.md에 다음 섹션이 포함되어 있는지 확인합니다:

- [ ] 아키텍처 (백엔드, 프론트엔드, DB)
- [ ] 코딩 규칙
- [ ] 디자인 규칙
- [ ] 금지 사항
- [ ] 테스트 규칙
- [ ] 커밋 컨벤션
- [ ] 설계 문서 규칙

### C. 디자인 시스템 검증

`docs/design-system/design-tokens.css`에 다음 토큰이 정의되어 있는지 확인:

- [ ] 컬러 토큰 (`--color-*`)
- [ ] 타이포그래피 토큰 (`--font-size-*`, `--font-weight-*`)
- [ ] 스페이싱 토큰 (`--spacing-*`)
- [ ] 반응형 브레이크포인트

### D. DB 설계 문서 검증

`docs/blueprints/database-design.md`에 다음 섹션이 포함되어 있는지 확인:

- [ ] 전체 ERD 섹션
- [ ] 공통 규칙 (테이블 접두사, 감사 컬럼, 네이밍)
- [ ] 모듈별 테이블 섹션
- [ ] FK 관계 요약 섹션

### E. 전역 설정 검증

- [ ] `~/.claude/settings.json` 에 Agent Teams 환경변수
- [ ] `~/.claude/.mcp.json` 에 MCP 서버 3개 (chrome-devtools, postgres, context7)

### F. 품질 게이트 검증

hookify 규칙이 설정되어 있는지 확인:
- `.claude/` 디렉토리에 `hookify.*.local.md` 파일 존재 여부

## 결과 출력

검증 결과를 다음 형식으로 출력합니다:

```
## ASTRA Sprint 0 체크리스트 검증 결과

### 점수: {통과}/{전체} ({퍼센트}%)

### 통과 항목
- [x] {항목명}

### 미통과 항목
- [ ] {항목명} - {해결 방법}

### 권장 조치
1. {구체적인 조치 사항}
```

## 주의사항

- 이 스킬은 읽기 전용입니다. 파일을 수정하지 않습니다.
- 각 항목의 통과/미통과를 명확히 표시합니다.
- 미통과 항목에는 구체적인 해결 방법을 제시합니다.
