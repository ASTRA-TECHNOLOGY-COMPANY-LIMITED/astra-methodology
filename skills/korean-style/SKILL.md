---
name: korean-style
description: >
  Writes Korean text that reads like a person wrote it, not an LLM. Applies to every
  Korean sentence this plugin produces — design documents, planner deliverables, manuals,
  code comments, commit messages, PR bodies, HITL questions to the user, and answers in
  the session. Use whenever writing or reviewing Korean prose, and run the deterministic
  checker before handing any Korean deliverable back. 한국어 문서·주석·질문·답변 작성 시
  번역투·AI 상투어·조수 말투를 걷어낸다.
---

# 사람처럼 쓰기

기준은 하나다. **옆자리 동료에게 소리 내어 말했을 때 어색하면 고쳐 쓴다.**

이 스킬은 두 개로 되어 있다. 규칙 정본은 [references/korean-style.md](references/korean-style.md),
판정은 [references/check-korean-style.py](references/check-korean-style.py) 가 한다.
**판정은 스크립트가 정본이다** — 자가 평가는 언제나 통과하기 때문이다.

> 두 references 파일은 `proposal-specialist` 플러그인의 사본과 byte-identical 이다.
> 고칠 땐 양쪽을 같이 고치고 md5 를 맞춘다. 플러그인 산출물 훅 게이트
> (`scripts/check-korean-style.sh` → `scripts/check-style.py`, 규칙 정본
> `docs/development/korean-style.md`)는 별도 판정기다 — 이 스킬의 검사기는
> 한국어 산출물을 넘기기 전에 스스로 돌리는 용도다.

## 언제 적용하나

한국어 문장을 만드는 **모든 곳**이다. 문서만이 아니다.

| 무엇을 쓰나 | 표면 |
| --- | --- |
| 설계 문서(`docs/blueprints/`), 기획 산출물(`docs/planner/`), 매뉴얼, README | `doc` |
| 리스크·사업성·FP 분석 리포트 | `report` |
| 코드 주석, 커밋 메시지, PR 본문 | `comment` |
| 사용자에게 던지는 질문(HITL) | `hitl` |
| 세션에서 사용자에게 하는 답 | `chat` |

파일로 남는 것은 PostToolUse 훅이 자동으로 검사한다(`scripts/check-korean-style.sh`).
**질문과 답은 파일이 아니라 훅이 못 본다** — 그건 아래 규칙을 지켜서 막는다.

## 가장 자주 새는 다섯 가지

전체 규칙 36종은 규칙 정본에 있다. 실제로 가장 자주 걸리는 건 이 다섯이다.

**연결어미 뒤 쉼표.** 한국어 AI 글을 가려내는 가장 강한 신호다(실측 4.84배 분리도).

```text
쓰지 않는다:  기술은 빠르게 발전하지만, 조직은 더디다.
대신:        기술은 빠르게 발전하지만 조직은 더디다.
```

**"~에 대해 / ~를 통해 / ~하기 위해".** 조사로 직결한다. "제도에 대해 설명한다" → "제도를
설명한다", "API를 통해 조회한다" → "API로 조회한다", "확인하기 위해" → "확인하려고".

**동사를 명사에 가두기.** "삭제 작업을 수행합니다" → "삭제합니다". 수행·진행·실시·실행이
붙으면 대개 그 앞 명사가 이미 동사다.

**상투적 도입과 마무리.** "결론적으로", "함께 알아볼까요", "도움이 되셨길 바랍니다",
"성공적으로 완료하였습니다", "더 궁금한 점이 있으시면 언제든지" — 전부 뺀다. 답은 첫 문장에서
말하고, 끝나면 "끝났습니다"로 충분하다.

**훈계형.** "확인할 필요가 있습니다" → "확인하자". "~하는 것이 중요합니다"는 중요하면 무엇이 왜
그런지를 쓴다.

## 질문(HITL)과 답을 쓸 때

훅이 못 보는 표면이라 여기서 정한다.

**질문은 선택지가 무엇을 바꾸는지까지 적는다.** "어떤 방식으로 하시겠습니까?"만 던지지 않는다.
고르면 무엇이 달라지는지를 한 줄씩 붙인다.

> 인증을 세션으로 할까요, 토큰으로 할까요?
> 세션은 서버가 상태를 들고 있어서 로그아웃을 즉시 끊을 수 있습니다.
> 토큰은 서버가 가볍지만 만료 전에는 강제로 끊기 어렵습니다.

**답은 결론부터.** 무엇을 조사했고 어떻게 검증했는지로 시작하지 않는다.

- 쓰지 않는다: "요청하신 내용에 대해 분석을 수행한 결과, 다음과 같은 사항을 확인하였습니다."
- 대신: "테스트 세 개가 깨져 있습니다. 전부 같은 원인입니다."

**숫자·`file:line`·버전은 결론이 바뀌는 것만 남긴다.** 나머지는 "실측으로 확인했다" 한마디로
접는다. 정밀도를 자랑하려고 근거를 늘어놓지 않는다.

**내부 은어를 상대가 먼저 쓰지 않았으면 쓰지 않는다.** 게이트·시임·오탐 같은 말은 풀어서 쓰거나
처음 나올 때 괄호로 푼다.

## 검사

```bash
CHK="${CLAUDE_PLUGIN_ROOT}/skills/korean-style/references/check-korean-style.py"

python3 "$CHK" --surface doc docs/blueprints/auth.md
python3 "$CHK" --surface report docs/planner/001-login/kpi.md
cat draft.md | python3 "$CHK" --surface chat -
```

exit **0** 통과 / **1** 경고 / **2** 반려(S1) / **3** 실행 오류.

**S1 은 예외 없이 고친 뒤 다시 돌린다.** exit 3 도 통과가 아니다 — 경로를 고쳐 다시 돌리고,
그래도 못 돌리면 "문체 미검증"이라고 밝힌다.

> 출력을 줄이려고 `| head` 를 붙이지 않는다. `$?` 가 검사기가 아니라 `head` 의 것이 되어,
> S1 이 여섯 건인 FAIL 이 `0` 으로 보인다(실측). 명령 치환도 같은 함정이다.

Bash 로 생성한 산출물(스크립트가 써낸 HTML·마크다운)은 PostToolUse 훅을 지나지 않는다.
그런 산출물은 만든 직후 검사기를 직접 한 번 돌린다.

## 고칠 때

**빼기만 한다.** AI 티를 지우려다 원문에 없던 비유·상투구를 새로 심지 않는다. 넣는 순간 그게
새 AI 티다.

**규칙을 고쳤으면 `--selftest` 를 돌린다.** 픽스처는 규칙 ID 까지 확인하므로, 정규식이 죽으면
바로 드러난다. 규칙 정본(`korean-style.md`)의 표와 검사기의 `PATTERNS`·`SURFACE_CFG` 는 함께
움직인다(C4·C5 는 절차 검사라 `PATTERNS` 밖이다) — 한쪽만 고치지 않는다.
