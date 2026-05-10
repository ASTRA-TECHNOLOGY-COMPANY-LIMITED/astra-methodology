# ASTRA Skill Audit — 2026-05-10

> **⚠️ 이력 변경 (post-audit, v4.0.0)**: 본 감사 이후 `/ux-publish` 스킬은 제거되고, 그 핵심 기능(디자인 시스템 토큰을 적용한 화면 시각화)은 `/service-planner` Step 6의 HTML 기획화면 생성으로 통합되었다. 이 문서에 등장하는 ux-publish 분할/슬림화 작업 기록은 **historical record**로만 유효하며, 현재 코드베이스에는 해당 스킬이 존재하지 않는다.

skill-development 가이드 기준 19개 스킬 분석 결과.

## 1. Progressive Disclosure 미적용 (가장 큰 문제)

19개 스킬 중 **2개만** `references/` 사용 (catalog-generator, manual-generator). `examples/`, `scripts/` 사용 0개.

| 스킬 | 단어 수 | 권장(1,500-2,000) | references | 우선순위 |
|---|---:|---:|---|---|
| ux-publish | 8,107 | 4배 초과 | ❌ | P0 |
| project-init | 6,376 | 3배 초과 | ❌ | P0 |
| service-planner | 6,075 | 3배 초과 | ❌ | P0 |
| catalog-generator | 3,975 | 2배 초과 | ✅ | P2 (이미 부분적용) |
| autorun | 3,890 | 2배 초과 | ❌ | P1 |
| test-run | 3,404 | 1.7배 초과 | ❌ | P2 |
| slack-import | 3,072 | 1.5배 초과 | ❌ | P2 |
| manual-generator | 2,874 | 1.4배 초과 | ✅ | P3 (이미 부분적용) |

## 2. Frontmatter Trigger Phrase 부족

CLAUDE.md 언어 정책(영어 auto-trigger / 한국어 사용자 진입점)과 `>` vs `"..."` 형식은 양호. 다만 가이드가 권장하는 *"This skill should be used when the user asks to '...' "* 형식의 발화 trigger가 거의 없음.

| 스킬 | 누락된 trigger phrase 예시 |
|---|---|
| pr-merge | "PR 만들어줘", "리뷰 받고 머지", "이슈 수정해서 머지" |
| service-planner | "기획해줘", "요구사항 정리", "기능 기획" |
| handoff-publish | "UX 핸드오프", "디자인 인계 패키지" |
| autorun | description이 본문 첫 단락 수준(150+ 단어), 핵심 trigger로 응축 필요 |

## 3. 한국어 본문 톤

가이드는 imperative form 권장. 한국어로는 평서형("~한다/~합니다")이 표준. 일부 스킬에 polite form 잔존:
- slack-import 7건, autorun 6건, service-planner 4건, ux-publish 4건, manual-generator 3건의 "~하세요"

**검증 결과**: ux-publish의 4건은 모두 *사용자에게 보여줄 UI 메시지* (예: "디자이너 디렉토리를 선택하세요") — Claude 향 절차 지시문이 아니라 사용자 인터페이스 텍스트이므로 polite form이 의도적이고 적절. 변경하지 않음. 다른 스킬도 동일 패턴인지 별도 세션에서 분류 필요.

## 4. 누락된 패턴

- `## Additional Resources` 섹션이 어떤 스킬에도 없음 → Claude가 보조 리소스 존재를 인지 못 함
- 검증/스캐폴딩 등 deterministic 동작은 `scripts/`로 추출 가능 (autorun의 stage 결정, project-init의 디렉토리 생성)

---

## 진행 계획 (사용자 승인)

P0 작업: **ux-publish 분할** + **한국어 톤 정리** 동시 진행.

### ux-publish 분할 결과 (완료)

advisor 권고에 따라 landing은 screen-build-guide에 통합 (6→5 파일).

| 파일 | 단어 수 | 종류 |
|---|---:|---|
| `skills/ux-publish/SKILL.md` (슬림 후) | 1,847 | 본문 |
| `references/common-resources-build.md` | 1,321 | references |
| `references/ai-image-prompts.md` | 884 | references |
| `references/screen-build-guide.md` (랜딩 통합) | 1,809 | references |
| `assets/COPY-GUIDE-template.md` | 460 | assets |
| `assets/completion-report-template.md` | 436 | assets |

**결과**:
- SKILL.md 본문: 8,107 → 1,847 단어 (-77%)
- advisor 검증 기준 `< 2,500` 통과
- skill-development 가이드 권장 1,500-2,000 단어 범위 적중
- frontmatter description: 200+ 단어 → 90 단어로 압축, 4개 trigger phrase 명시
- 5개 Step 진입 위치에서 명시적 references/assets 참조 ("먼저 X를 읽는다")
- 정보 손실 0건 (모든 디테일이 references/assets에 분산)

### 한국어 톤 정리 (보류)

ux-publish의 4건은 모두 사용자 UI 메시지였으나, 슬림화 과정에서 그 UI 메시지가 절차 지시문으로 자연스럽게 압축되어 polite form이 0건으로 감소. 별도 sweep 불필요.

다른 스킬(slack-import 7건, autorun 6건, service-planner 4건, manual-generator 3건)의 polite form은 별도 세션에서 Claude 향 절차 지시문 vs 사용자 UI 메시지로 분류한 뒤 전자만 정리 권장.

---

## 다음 권장 작업 (별도 세션)

**P0 — 동일 패턴으로 분할**:
- `project-init` (6,376 → ~1,800): CLAUDE.md 보일러플레이트(L543-720)는 `assets/claude-md-template.md`로, 디자인 시스템 템플릿은 `references/`로
- `service-planner` (6,075 → ~2,000): 6개 산출물 템플릿(시장분석/인터뷰/요구사항/유즈케이스/IA/기능정의서)을 `references/deliverable-templates/`로

**P1**:
- `autorun` (3,890 → ~1,800): 단계별 디폴트 결정 매트릭스를 `references/auto-defaults.md`로
- `pr-merge`, `service-planner`, `handoff-publish` 등의 frontmatter description에 trigger phrase 보강

**P2**:
- `test-run`, `slack-import` 분할
- `catalog-generator`, `manual-generator`는 이미 references/ 사용 중 — 추가 압축은 불필요
