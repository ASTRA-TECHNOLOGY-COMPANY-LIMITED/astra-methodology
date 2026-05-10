# Skill Authoring Best Practices

이 플러그인은 다수의 SKILL.md를 직접 작성/유지보수한다. 새 스킬을 추가하거나 기존 스킬을 수정할 때는 Anthropic 공식 가이드를 따른다 — [Claude Code Skills](https://code.claude.com/docs/en/skills), [Agent Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

## 핵심 원칙

- **Concise is key** — SKILL.md는 한 번 로드되면 세션 내내 컨텍스트에 남는다. 모든 줄이 *반복* 토큰 비용이다. 본문은 **500줄 미만**으로 유지한다.
- **Default assumption: Claude is already smart** — Claude가 이미 아는 일반 지식("PDF란 무엇인가", "라이브러리 사용법")은 생략한다. 각 문장에 대해 "이 줄이 토큰 비용을 정당화하는가?"를 자문한다.
- **State, don't narrate** — 무엇을 할지(what to do)만 적고, 어떻게/왜를 길게 설명하지 않는다. CLAUDE.md 작성 원칙과 동일하다.
- **Standing instructions** — 스킬 본문은 첫 호출 이후에도 계속 적용되는 지속 지시문 형태로 쓴다. 일회성 단계만 나열하면 후속 턴에서 재참조되지 않는다.

## Frontmatter 필드

| 필드 | 제약 | 비고 |
|------|------|------|
| `name` | 64자, 소문자/숫자/하이픈 | "anthropic", "claude" 예약어 금지, XML 태그 금지 |
| `description` | 1,024자 이내, 비어 있을 수 없음 | 자동 트리거의 핵심. **3인칭 명사형 필수** |
| `when_to_use` | description과 합쳐 1,536자 cap | 트리거 문구/예시 보강용 |
| `allowed-tools` | 공백 구분 또는 YAML list | 권한 사전 승인 — 최소 권한 원칙 |
| `disable-model-invocation` | bool | 사이드이펙트가 있는 워크플로우(`/deploy`, `/commit`)는 `true` |
| `user-invocable` | bool | 백그라운드 지식 스킬은 `false`로 메뉴 노출 차단 |
| `paths` | glob 패턴 | 특정 파일에서 작업할 때만 자동 로드 |
| `model` / `effort` | 모델/추론 강도 오버라이드 | 검증 스킬은 haiku, 분석 스킬은 sonnet |
| `context: fork` | 서브에이전트 격리 실행 | 명시적 task가 있는 스킬에만 사용 |

## Description 작성 7원칙

1. **3인칭으로 작성**: "Processes Excel files..." (O) / "I can help you..." (X) / "You can use this to..." (X) — 시스템 프롬프트에 주입되므로 시점 일관성이 중요.
2. **What + When 모두 포함**: 무엇을 하는지 + 언제 호출되어야 하는지.
3. **트리거 키워드 명시**: `Use when [상황1], [상황2], or when user mentions "[키워드]"` 패턴.
4. **핵심 use case를 첫 문장에 배치**: 1,536자 cap에서 잘릴 수 있다.
5. **Auto-trigger 스킬 → 영어 description**: LLM 매칭 정확도가 더 높다. `description: >` 블록 형식.
6. **명시 호출 진입점 → 한국어 description**: `/help` 메뉴에서 한국 사용자 의도가 즉각 이해되어야 한다. `description: "..."` 단일 라인.
7. **모호한 단어 금지**: "Helps with documents", "Does stuff with files" → 거부. 구체적 동작과 트리거 명시.

**Good 예시**:
```yaml
description: >
  Validates Java/TypeScript/React Native/Python/CSS/SCSS code against project
  coding conventions. Use when reviewing code changes, before committing,
  after implementing features, or when the user asks to "check code quality".
```

## Progressive Disclosure (점진적 공개)

- **SKILL.md = 목차**, 상세 자료는 `references/`, `scripts/`, `assets/`로 분리.
- **모든 reference 링크는 SKILL.md에서 직접** (one level deep). 중첩 참조 (SKILL → A → B)는 Claude가 partial read(예: `head -100`)로 일부만 보고 누락하기 쉽다.
- **100줄 이상의 reference 파일** 상단에 목차(Contents)를 명시한다 — partial read 시에도 전체 범위 파악 가능.
- **Domain별 분리**: 한 스킬에 여러 영역이 있으면 `reference/finance.md`, `reference/sales.md` 식으로 나눠 무관 컨텍스트 로드를 차단한다.
- **Scripts: 실행 vs 참조 의도 명시** — "Run `analyze.py`" (execute) / "See `analyze.py` for the algorithm" (read). 대부분은 실행이 맞다.

## Degrees of Freedom (자유도 매칭)

| 자유도 | 적용 시점 | 형식 |
|--------|-----------|------|
| **High** (텍스트 지침) | 다양한 접근이 유효, 컨텍스트 의존 | "Analyze code structure and suggest improvements" 식 가이드 |
| **Medium** (파라미터 스크립트) | 패턴은 있으나 일부 변동 허용 | 템플릿 함수 + 파라미터 |
| **Low** (고정 스크립트) | fragile/일관성 critical, 순서 고정 | "Run exactly this command, do not modify" |

DB 마이그레이션 = low / 코드 리뷰 = high.

## Workflow & Feedback Loop 패턴

복잡한 다단계 작업은 **체크리스트 + 검증 루프**로 구조화한다:

```markdown
## Form filling workflow
- [ ] Step 1: analyze_form.py 실행
- [ ] Step 2: fields.json 작성
- [ ] Step 3: validate_fields.py 실행 (실패 시 Step 2로 복귀)
- [ ] Step 4: 검증 통과 시에만 fill_form.py 실행
- [ ] Step 5: verify_output.py로 최종 확인
```

검증 단계에서 명시적 루프를 작성한다 — Goal-Driven Execution 4원칙과 일치.

## 안티패턴 — 절대 금지

1. **Windows-style 경로**: `scripts\helper.py` ❌ → `scripts/helper.py` ✅ (cross-platform).
2. **시한성 정보**: "Before August 2025, use the old API" ❌ → 별도 `## Old patterns` 섹션 + `<details>`로 분리.
3. **너무 많은 선택지**: "Use pypdf, or pdfplumber, or PyMuPDF, or..." ❌ → 기본값 1개 + 필요 시 escape hatch.
4. **모호한 description**: "Helps with files", "Does stuff" ❌ → 구체적 동작 + 트리거 키워드.
5. **3-level 이상 중첩 참조**: SKILL → A → B → C ❌ → 모든 reference는 SKILL.md에서 직접 링크.
6. **Voodoo magic number**: `TIMEOUT = 47` ❌ → 코멘트로 근거 명시 (`# Most requests complete within 30s`).
7. **에러 punt**: 스크립트가 fail 후 "Claude가 알아서" 처리하게 두지 말 것 — 명시적 에러 처리 + 폴백.
8. **불일치 용어**: "field/box/element/control" 혼용 ❌ → 한 개념엔 한 용어.
9. **자기 소개식 description**: "I can help with..." / "You can use this..." ❌ → 항상 3인칭.
10. **MCP 도구 비한정 참조**: `bigquery_schema` ❌ → `BigQuery:bigquery_schema` (서버명 prefix).

## Evaluation-Driven Development

1. 스킬 없이 Claude로 대표 task 시도 → 실패/누락 지점 기록.
2. **3개 이상** 평가 시나리오 작성 (입력 + 기대 동작).
3. **베이스라인 측정** 후 최소한의 SKILL.md 작성 — 가상 요구사항을 미리 문서화하지 않는다.
4. 평가 실행 → 베이스라인 대비 개선 여부 비교 → 반복.

## 모델별 테스트

스킬은 모델 위에 더해지는 레이어다. 사용 예정 모델(Haiku/Sonnet/Opus)에서 각각 검증한다:
- **Haiku** — 가이드가 충분한가? (검증/규칙 스킬에 적합)
- **Sonnet** — 명확하고 효율적인가? (분석/리뷰 스킬에 적합)
- **Opus** — 과잉 설명이 없는가?

ASTRA의 모델 선택 컨벤션과 정렬 — `*-validator`(haiku), `*-reviewer`/`*-analyzer`/`*-runner`/`*-persona`(sonnet).

## Iterative 개발 (Claude A ↔ Claude B 패턴)

가장 효과적인 스킬 작성 방법은 Claude를 활용하는 것이다:
- **Claude A**: 스킬 설계/리팩토링을 돕는 인스턴스 ("Create a Skill that captures this pattern")
- **Claude B**: 새 인스턴스에서 작성된 스킬을 실제 task로 테스트
- **관찰 → Claude A로 피드백 → 개선 → 재테스트** 루프

## ASTRA 신규/수정 SKILL.md 체크리스트

- [ ] description 3인칭 + What + When + 트리거 키워드
- [ ] Auto-trigger 스킬 → 영어 `description: >` 블록 / 인터랙티브 스킬 → 한국어 `description: "..."` 단일 라인
- [ ] 본문 500줄 이내 (초과 시 `references/`, `scripts/`, `assets/` 분리)
- [ ] 모든 파일 경로 forward slash (`/`)
- [ ] reference 파일 링크 one level deep
- [ ] 시한성 정보 없음 (있으면 `## Old patterns` 섹션)
- [ ] 일관된 용어 사용
- [ ] `allowed-tools` 명시 + 최소 권한
- [ ] 사이드이펙트 위험 → `disable-model-invocation: true`
- [ ] 백그라운드 지식 스킬 → `user-invocable: false`
- [ ] 4원칙(Think Before / Simplicity / Surgical / Goal-Driven) 위배 없음
- [ ] Persona agent description은 `[EXPLICIT-INVOCATION-ONLY — DO NOT AUTO-MATCH]` 가드 prefix 유지
- [ ] 최소 3개 평가 시나리오로 사전 검증
