#!/usr/bin/env python3
"""한국어 AI 티 결정적 검사기 — astra-methodology 한국어 출력 공통 게이트.

규칙 정의는 `docs/development/korean-style.md` 가 SoT다. 이 스크립트는 그 규칙을
기계 판정으로 옮긴 것이며, 판정 결과가 정본이다(에이전트 자가 판단으로 덮어쓰지
않는다). social-flow 의 check-style.py 를 astra 표면으로 이식한 것.

    python3 check-style.py --surface doc docs/blueprints/001-auth/blueprint.md
    grep '//' src/api.ts | python3 check-style.py --surface comment -
    python3 check-style.py --surface commit --json /tmp/commit-msg.txt

exit 0 통과 / 1 경고(S2 누적) / 2 불합격(S1 검출) / 3 실행 오류.

의존성 없음(표준 라이브러리만). 플러그인 배포본에서 그대로 실행된다.
한국어 전용 — 검사 대상에 한글이 없으면 호출부가 건너뛴다(vi/en 산출물 미적용).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata

SURFACES = ("answer", "label", "hitl", "report", "comment", "doc", "commit")

# ---------------------------------------------------------------------------
# Do-NOT — 탐지·수정 모두 제외. 위치를 보존하려고 같은 길이의 공백으로 가린다.
# ---------------------------------------------------------------------------

# 카피 검사에서 늘 가리는 것 — 바꾸면 안 되는 값들뿐이다.
# 여기에 "덩어리를 통째로 가리는" 마스크를 넣지 않는다. 실측 사고 둘: 인용 200자를
# 가렸더니 슬롭을 따옴표에 넣어 0점이 100점이 됐고, 백틱·코드펜스를 가렸더니 같은
# 우회가 다시 열렸다. 덩어리 마스크는 전부 DOC_MASKS 로 간다.
MASKS = (
    re.compile(r"https?://\S+"),                 # URL
    re.compile(r"#[\w가-힣]+"),                   # 해시태그
    re.compile(r"[A-Za-z][A-Za-z0-9_.\-]*"),     # 영문 약어·고유명사
    re.compile(r"\d[\d,.\-~%/:]*"),              # 수치·날짜·단위
    # 기계 파싱 계약 라인 — 고치면 부모 루프의 파싱이 깨진다(skill-best-practices §13).
    re.compile(r"(?m)^(ASTRA_\w+_RESULT|SEVERITY_COUNTS):.*$"),
    # 게이트 리포트의 상태 표기 — 데이터이지 장식이 아니라 이모지 한도에서 뺀다.
    re.compile(r"[✅❌⚠✔✖☑]️?"),
)

# --doc 에서만 추가로 가리는 것. 규칙표·명령 예시가 든 내부 문서를 검사할 때 쓴다.
# 산출 카피에는 켜지 않는다 — 전부 슬롭 은신처가 된다.
DOC_MASKS = (
    re.compile(r"```.*?```", re.S),              # 코드블록 (명령·예시)
    re.compile(r"`[^`\n]+`"),                    # 인라인 코드
    re.compile(r"(?m)^\s*\|.*\|\s*$"),           # 마크다운 표 행
    # 인용 블록(>)은 가리지 않는다 — 블루프린트·기획서의 > 는 인용이 아니라
    # 콜아웃 산문이라, 가리면 슬롭 은신처가 된다(실측).
)

# 이모지만 — 화살표(→ ←)·괘선은 문서 기호이지 이모지가 아니다(오탐 주범).
EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF"   # 이모티콘·픽토그램·교통·기호 보충
    "☀-⛿"            # 기타 기호 ☀ ⚡ ⚠
    "✀-➿"            # 장식 기호 ✅ ✂
    "⬀-⯿"            # 굵은 화살표·별 ⬅ ⭐
    "〰〽㊗㊙]"
)

# ---------------------------------------------------------------------------
# 패턴 — (ID, 심각도, 설명, 정규식, 임계) 임계 = 이 횟수를 넘겨야 계상.
# 심각도는 korean-style.md 표와 1:1. 여기서만 바꾸지 말고 문서도 같이 고친다.
# ---------------------------------------------------------------------------

Pattern = tuple  # (id, sev, label, regex, threshold, fix)

PATTERNS: list[Pattern] = [
    # --- 번역투 T -----------------------------------------------------------
    ("T1", "S1", "~에 대해(서)", re.compile(r"에\s*대(해서|해|하여)"), 0,
     "목적격 조사로 직결 — '제도에 대해 알아보자' → '제도를 알아보자'"),
    # 존재동사와 구분한다 — "가방에 있어."는 정상이고 "문제에 있어서"만 번역투다.
    ("T2", "S1", "~에 있어서", re.compile(r"에\s*있어서(?=\s*[가-힣])"), 0,
     "'~에서' 또는 '~할 때'"),
    # '여지는'(명사 여지+는)은 뺀다 — 이중피동이 아니다.
    ("T3", "S1", "이중 피동",
     re.compile(r"(되어[지진졌집]|보여[지진졌]|잊혀[지진졌]|쓰여[지진졌]|불려[지진졌]|모아[지진졌])"), 0,
     "단순 피동으로 — '판단되어진다' → '판단한다'"),
    ("T4", "S1", "~을 가지고 있다", re.compile(r"[을를]\s*가지고\s*있"), 0,
     "동사로 — '강점을 가지고 있다' → '강점이 있다'"),
    ("T5", "S2", "~에 의해 + 피동", re.compile(r"에\s*의(해|하여)\s*\S*(되|진|받)"), 0,
     "능동으로 — '법에 의해 정해진다' → '법이 정한다'"),
    ("T6", "S2", "이중 조사", re.compile(r"(에서의|으로의|로의|에의|로부터의|으로부터의)"), 0,
     "절로 풀기 — '현지에서의 생활' → '현지 생활'"),
    ("T7", "S2", "~를 통해 반복", re.compile(r"[을를]\s*통(해서|해|하여)"), 2,
     "3회 넘을 때만 일부를 '~로'·'~해서'로 분산"),
    ("T8", "S2", "~라는 점에서 반복", re.compile(r"[라다]는\s*점에서"), 1,
     "'~라서'·'~니까'"),
    ("T9", "S3", "인칭 대명사 밀도", re.compile(r"\b(그|그녀|그들|그것)(는|은|가|를|의|에게|와|도)\b"), 2,
     "생략하거나 이름·호칭으로"),

    # --- AI 관용구 D ---------------------------------------------------------
    ("D1", "S1", "상투적 도입·결말어",
     re.compile(r"(결론적으로|궁극적으로|본질적으로|요컨대|종합하면|정리하자면)"), 0,
     "삭제. 답은 첫 문장에서 말한다"),
    ("D2", "S1", "의의 과장",
     re.compile(r"(시사하는\s*바가\s*[크큽]|의미가\s*[크큽]|주목할\s*만하|주목(된다|됩니다|받는다|받고)"
                r"|평가된다|평가받는다|귀추가\s*주목|기대를\s*모으)"), 0,
     "무엇이 왜 그런지로 바꾸거나 삭제"),
    ("D3", "S1", "훈계형",
     re.compile(r"(할\s*필요가\s*있|하는\s*것이\s*중요|해야\s*할\s*것이다|명심해야)"), 0,
     "'확인할 필요가 있다' → '확인하자'"),
    ("D4", "S2", "완곡 회피",
     re.compile(r"(라고\s*할\s*수\s*있|로\s*보여진다|인\s*셈이다|라고\s*볼\s*수\s*있"
                r"|것으로\s*보(인다|입니다|이며)|것으로\s*예상|라고\s*여겨)"), 1,
     "단정할 수 있으면 단정한다"),
    ("D5", "S2", "과장 수식",
     re.compile(r"(혁신적|획기적|새로운\s*지평|게임\s*체인저|판도를\s*바꿀|놀라운)"), 0,
     "삭제. 강조는 수식어가 아니라 숫자로"),
    ("D6", "S2", "뜻 없는 수식어",
     re.compile(r"(매우|굉장히|효과적으로|원활하게|성공적으로|다양한|폭넓은|손쉽게)"), 1,
     "삭제"),
    # 어휘 티는 없는데 내용도 없는 보도자료체 — 규칙 확장 실측에서 마지막까지
    # 통과하던 유형이다.
    # "중요한 것은 X입니다"는 X 가 추상어일 때만 잡는다 — "중요한 것은 접수증입니다"
    # 같은 구체적 결론까지 먹으면 잘 쓴 문장이 감점된다(실측). "전환점을 맞"도
    # 사실 서술을 과포획해서 뺐다.
    ("D7", "S2", "공허한 수사",
     re.compile(r"(물결\s*속에서|시대의?\s*흐름\s*속|균형점을\s*찾|화두로\s*떠오"
                r"|답은\s*간단합니다|핵심은\s*딱\s*하나|새로운\s*국면"
                r"|중요한\s*것은\s*(방향|본질|자세|태도|의지|마음가짐|관점|균형))"), 0,
     "구체적 사실·숫자로 바꾸거나 삭제"),

    # --- 구조·리듬 C ---------------------------------------------------------
    ("C1", "S1", "연결어미 뒤 쉼표",
     re.compile(r"(지만|는데|면서|라서|어서|아서|으며|하며|거나|려면|더라도|해도|지요|는지),"), 0,
     "쉼표를 뺀다 — '발전하지만, 대응은 느리다' → '발전하지만 대응은 느리다'"),
    ("C2", "S2", "부정 대구 'A가 아니라 B'",
     re.compile(r"(이|가|은|는|도)?\s*아니라\s"), 0,
     "그냥 B라고 쓴다 (2회 이상이면 S1 승격)"),
    # 용언 3연속만 잡는다. 명사 나열("여권, 비자, 계약서")은 체크리스트 장르의
    # 기본 문형이라 대상이 아니다 — 실측에서 오탐이 났다.
    ("C3", "S2", "3항 나열 (대등 용언)",
     re.compile(r"[가-힣]{2,}고\s+[가-힣]{2,}(하)?며\s+[가-힣]{2,}[한는]"
                r"|[가-힣]{2,}하고\s*,\s*[가-힣]{2,}하고\s*,\s*[가-힣]{2,}[한하]"), 0,
     "정말 셋일 때만 셋. 대개 하나면 된다"),
    ("C6", "S2", "기계적 3단",
     re.compile(r"(먼저|첫째|첫\s*번째).{0,120}?(다음으로|둘째|두\s*번째).{0,120}?(마지막으로|끝으로|셋째)",
                re.S), 0,
     "순서가 진짜 중요할 때만"),

    # --- 조수 말투 A ---------------------------------------------------------
    ("A1", "S1", "안내형 도입",
     re.compile(r"(함께\s*알아보|알아볼까요|살펴볼까요|오늘은\s*\S{0,20}에\s*대|이번\s*시간에는)"), 0,
     "본론부터"),
    # 짧은 감사 인사 자체는 정상 응대다(platform-guide 원칙 4 골든타임). 콘텐츠를
    # 닫는 상투적 마무리만 잡는다.
    ("A2", "S1", "마무리 인사",
     re.compile(r"(도움이\s*되(셨|었)|참고하시기\s*바랍|되시길\s*바랍"
                r"|읽어주셔서\s*(감사|고맙)|시청해\s*주셔서|끝까지\s*(봐|읽)"
                r"|다음에도\s*(유익|좋은|알찬)|찾아뵙)"), 0,
     "삭제"),
    ("A3", "S2", "안 물어본 균형",
     re.compile(r"(물론\s.{0,40}도\s*있지만|양쪽\s*모두|일장일단|장단점이\s*있)"), 0,
     "한쪽을 고르거나 삭제"),
    ("A4", "S1", "인사 개시·채널 홍보",
     re.compile(r"(안녕하세요|반갑습니다|소식을\s*전해\s*드리|전해드립니다"
                r"|구독과\s*좋아요|알림\s*설정|많은\s*관심\s*부탁)"), 0,
     "본론부터. 채널 표시는 아웃트로가 맡는다"),
]

# 접속부사는 뒤에 쉼표가 와도 정상이다("하지만, ~"). C1 정규식이 어미로 잡는
# "하지만"과 어간이 붙은 "발전하지만"은 어절 전체를 봐야 구분된다.
CONJ_ADVERBS = {
    "하지만", "그렇지만", "그런데", "한데", "그러면서", "그래서", "그러니까",
    "그러므로", "다만", "게다가",
}

# 플레이북이 규정한 표현 — 패턴에 걸려도 위반이 아니다.
WHITELIST = (
    # 부사 + '의' 는 이중 조사가 아니다 — "앞으로의 변화"는 자연스러운 한국어다(T6 오탐).
    re.compile(r"(앞|뒤|이후|향후|지금|평소)으?로의"),
    # FB 사례 수집형 마무리 — 플레이북 §5 규정. 지금은 어떤 패턴에도 걸리지 않지만,
    # 질문 종결 규칙을 나중에 넣더라도 이 표현은 보호되도록 미리 선언해 둔다.
    re.compile(r"여러분은\s*어떻게\s*(하고\s*)?(계신가요|하시나요)"),
    # "다름 아니라"는 고정 관용구다 — 부정 대구(C2)가 아니다.
    # C2 매치가 뒤 공백까지 포함하므로 화이트리스트도 공백을 덮어야 한다.
    re.compile(r"다름\s*아니라\s*"),
)

# ---------------------------------------------------------------------------
# 표면별 설정
# ---------------------------------------------------------------------------

# off 목록이 표면별 완화의 유일한 창구다 — korean-style.md 의 "끄는 규칙" 열과
# 이 표가 정확히 같아야 한다. 한쪽만 고치지 않는다.
SURFACE_CFG = {
    # 사용자에게 보내는 답변·완료 보고 산문 — 전 규칙 적용.
    "answer":  {"emoji": 0, "len": None,    "off": ()},
    # AskUserQuestion 라벨·헤더 조각 — 길이 밴드로 장문 라벨을 잡는다.
    "label":   {"emoji": 0, "len": (0, 30), "off": ("C3", "C5", "C6")},
    # HITL 질문·선택지 본문 — 선택지는 원래 나열이라 종결 반복·기계적 3단을 끈다.
    "hitl":    {"emoji": 1, "len": None,    "off": ("C5", "C6")},
    # 게이트 결과·검증 리포트 — 상태 나열 장르라 3항 나열·종결 반복을 끈다.
    "report":  {"emoji": 2, "len": None,    "off": ("C3", "C5")},
    # 코드 주석·docstring — 문장 조각이라 리듬 규칙이 맞지 않는다. 어휘 티만 본다.
    "comment": {"emoji": 0, "len": None,    "off": ("C1", "C3", "C5", "C6", "T9")},
    # 블루프린트·기획 산출물 — --doc 마스크가 자동 적용된다(표·코드블록은 데이터).
    "doc":     {"emoji": 0, "len": None,    "off": ("C5", "C6")},
    # 커밋 메시지·PR 본문 — 항목 나열 장르.
    "commit":  {"emoji": 0, "len": None,    "off": ("C3", "C5", "C6")},
}

PENALTY = {"S1": 20, "S2": 7, "S3": 2}
METRIC_PENALTY = 3
WARN_BELOW = 85  # S1 이 없어도 이 점수 미만이면 exit 1

# ---------------------------------------------------------------------------


def mask(text: str, doc: bool = False) -> str:
    """Do-NOT 구간을 같은 길이의 공백으로 가린다(오프셋 보존)."""
    out = list(text)
    for rx in MASKS + (DOC_MASKS if doc else ()):
        for m in rx.finditer(text):
            for i in range(m.start(), m.end()):
                if out[i] != "\n":
                    out[i] = " "
    return "".join(out)


def whitelist_spans(text: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for rx in WHITELIST for m in rx.finditer(text)]


# 큰따옴표 직접 인용. 가리지 않는다(가리면 슬롭 은신처가 된다) — 대신 여기서 나온
# 위반은 `quoted` 라벨을 달아 점수·판정에서 빼고 보고에만 싣는다. 남의 말을 옮긴
# 구간은 고치는 것 자체가 왜곡이기 때문이다(korean-style.md §Do-NOT).
QUOTE_RX = re.compile(r"[\"“][^\"”]{0,400}[\"”]")

# 면제 조건은 **출처가 특정됐는가**다. 두 번 틀렸다.
#   1차: 인용 비중으로 갈랐더니 양방향으로 깨졌다 — 비중이 낮으면 앞에 평범한
#        문장만 깔아 슬롭을 통과시킬 수 있었고, 비중이 높으면 짧은 글의 정당한
#        원문 인용이 차단됐다. 비중은 정당성과 무관한 축이다.
#   2차: 귀속 표지로 바꿨는데 목록이 넓어 서사 어휘까지 들어갔다. "그가 말했다."
#        "이렇게." "다음과 같습니다." 두 단어만 붙이면 임의의 슬롭이 통과했다.
#        지어낸 슬롭 앞에 붙이기가 진짜 인용 앞에 붙이기보다 쉬웠다.
# 그래서 지금은 **무엇의 말인지 지목하는 표지**만 인정한다.
SOURCE_NOUNS = (
    r"(시행령|시행규칙|법률|법령|고시|공고|공문|훈령|조례|지침|약관|규정집|판결문"
    r"|보도자료|안내문|성명서|백서|매뉴얼|공안부|국세청|외교부|노동부|보건부|출입국"
    r"|대사관|영사관|세무서|관공서|당국"
    # 생활 출처. 이 장르에서 집주인·중개인·고객센터 인용은 기관 인용만큼 흔한데
    # 기관 명사만 두면 그런 인용이 통째로 차단됐다(실측: 집주인 문자 인용 exit 2,
    # 우회 수단 없음 — 남의 문자를 고치라는 처방이 되어 §Do-NOT 와 충돌했다).
    # 넓혀도 조용한 통과가 되지 않는다 — 면제는 exit 1 로 사람 눈에 올라간다.
    r"|집주인|임대인|세입자|중개인|인사팀|고객센터|상담원)"
)
# 출처를 지목하는 지시대명사·범용어는 배제한다. "이것에 따르면" 한 어절로 면제가
# 열렸다(실측) — 무엇의 말인지 하나도 특정하지 않는 표지다.
VAGUE = r"(?!(?:이것|그것|저것|여기|거기|이거|그거|이런|그런|자료|내용|정보)에\s*따르면)"
# 개인 출처 행위형 뒤에 붙어 "옮긴 것"이 아니라 "알게 된 계기"임을 드러내는 꼬리.
# 단 어미만 보면 갈리지 않는다 — "받고 알았습니다"(계기)와 "받고 그대로 옮깁니다"
# (인용 도입)가 같은 어미다(실측: 후자가 exit 2 로 막혔다). 뒤 20자 안에 옮김
# 동사가 오면 계기가 아니라 도입이므로 배제를 취소한다.
NOT_HEARSAY = (
    r"(?!\s*(?:을|를|랑|이랑)?\s*(?:보고|받고|읽고|확인하고|보니|듣고)"
    r"(?!.{0,20}(?:옮|붙여|인용|그대로|전문)))"
)
ATTRIBUTION = re.compile(
    r"(https?://"                                  # 인용에 붙은 출처 링크
    rf"|{SOURCE_NOUNS}"                            # 문서·법령·기관·생활 출처 이름
    rf"|{VAGUE}[가-힣A-Za-z0-9]{{2,}}에\s*따르면"   # "X에 따르면" — 출처를 목적어로 요구
    r"|[가-힣A-Za-z0-9]{2,}이?\s*발표한"            # "X가 발표한"
    # 개인 출처의 표준 문형 — 무엇을 옮긴 것인지(문자·메일·답변)까지 밝힌 경우.
    # 뒤에 "~를 보고/받고" 가 오면 인용 도입이 아니라 경위 서술이다("친구가 보낸
    # 문자를 보고 알았습니다") — 옮긴 게 아니라 알게 된 계기라서 표지가 아니다.
    rf"|[가-힣]{{2,}}(이|가|께서|에서)\s*(보낸|보내온|보내준|남긴|준)"
    rf"\s*(문자|메시지|메일|카톡|쪽지|답변|안내|공지|글){NOT_HEARSAY}"
    rf"|[가-힣]{{2,}}(에게|한테)\s*받은\s*(문자|메시지|메일|카톡|답변|안내){NOT_HEARSAY}"
    r")"
)
# 목록은 베트남·한국 행정 도메인에 맞춰져 있다. **채널이 늘어도 이 목록을 늘리지
# 않는다** — 재테크·IT 채널의 출처는 `X에 따르면` 이나 URL 로 적으면 그대로 면제된다.
# 명사를 계속 더하면 목록이 곧 우회로가 된다(흔한 단어가 섞이는 순간 두 글자 접두어로
# 통과한다). 목록은 관공서 문서를 자주 인용하는 채널의 편의 축일 뿐이고, 일반 축은
# URL 과 "X에 따르면" 둘이다.

# 인용 부호 앞뒤 이 범위 안에서 표지를 찾는다. 60자는 한국어 도입부 한 문장을
# 넉넉히 덮는 폭이다 — "공안부가 지난주 발표한 시행령 원문은 다음과 같습니다."(27자),
# "원문 https://example.gov.vn/decree 에는 이렇게 적혀 있습니다."(48자) 둘 다 들어온다.
# 40자였을 때 URL 도입부가 잘려 정당한 인용이 면제를 못 받았다(실측).
# 넓혀도 우회에 쓰이지 않는다 — 표지가 기관·법령·URL 이라 붙이려면 없는 출처를
# 지어내야 하고, 그건 문체가 아니라 사실 왜곡 게이트(content-reviewer P0-3)가 잡는다.
ATTRIBUTION_WINDOW = 60
# 인용 바로 앞 줄은 거리와 무관하게 후보로 보되, 그 줄의 **끝 40자**까지만 본다.
# 줄 전체를 열었더니 160자 도입부 맨 앞에 기관명 하나만 흘려도 그 아래 인용이
# 통째로 면제됐다(실측). 그 우회를 막는 주역은 40 이 아니라 아래 min() 구조다 —
# 앞줄에서 가져오는 범위를 유한하게 자르는 순간 막힌다(상수를 0 으로 놓고 재도
# exit 2 다). 40 이 지키는 건 반대쪽이다: 출처가 앞줄에 있고 인용이 같은 줄에서
# 60자 넘게 들여쓰이면 60자 창이 앞줄에 닿지 못하는데, 이때 꼬리 40자가 그 정당한
# 인용을 살린다. 0 으로 되돌리면 셀프테스트 "앞줄 꼬리는 깊은 들여쓰기를 지킨다"
# 가 깨진다 — 이 상수가 무엇을 지키는지는 그 픽스처가 증명한다.
PREV_LINE_TAIL = 40


def quote_spans(text: str) -> list[tuple[int, int]]:
    """출처가 밝혀진 직접 인용 구간만 돌려준다."""
    out = []
    for m in QUOTE_RX.finditer(text):
        # 문자 거리(60자)에 더해 **바로 앞 줄의 끝부분**을 후보로 본다. 사람은
        # 출처를 인용 앞줄 끝에 적지, 60자에 맞춰 적지 않는다.
        line_start = text.rfind("\n", 0, m.start()) + 1
        prev_line_start = text.rfind("\n", 0, max(line_start - 1, 0)) + 1
        prev_tail = max(prev_line_start, line_start - 1 - PREV_LINE_TAIL)
        begin = min(max(0, m.start() - ATTRIBUTION_WINDOW), prev_tail)
        before = text[begin:m.start()]
        after = text[m.end():m.end() + ATTRIBUTION_WINDOW]
        if ATTRIBUTION.search(before) or ATTRIBUTION.search(after):
            out.append((m.start(), m.end()))
    return out


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def eojeol_at(text: str, pos: int) -> str:
    """pos 가 속한 어절에서 구두점을 뗀 형태. 접속부사 판정용."""
    a = max(text.rfind(" ", 0, pos), text.rfind("\n", 0, pos)) + 1
    b = min((i for i in (text.find(" ", pos), text.find("\n", pos)) if i != -1),
            default=len(text))
    return text[a:b].strip(" ,.!?…\n")


def sentences(masked: str) -> list[tuple[int, str]]:
    """(시작 오프셋, 문장) 목록. 종결부호와 줄바꿈을 경계로 본다."""
    out, start = [], 0
    for m in re.finditer(r"[.!?。…]+\s*|\n+", masked):
        piece = masked[start:m.start()].strip()
        if piece:
            out.append((start, piece))
        start = m.end()
    tail = masked[start:].strip()
    if tail:
        out.append((start, tail))
    return out


def ending_key(sentence: str) -> str | None:
    """문장 마지막 어절의 끝 2음절 — 종결어미 반복 판정용."""
    words = sentence.split()
    if not words:
        return None
    last = re.sub(r"[^가-힣]", "", words[-1])
    return last[-2:] if len(last) >= 2 else (last or None)


def visible_len(sentence: str) -> int:
    return len(sentence.replace(" ", ""))


def analyze(text: str, surface: str, doc: bool = False) -> dict:
    cfg = SURFACE_CFG[surface]
    # doc 표면은 내부 문서 검사 전용이므로 DOC_MASKS 를 자동 적용한다.
    masked = mask(text, doc or surface == "doc")
    wl = whitelist_spans(text)
    qs = quote_spans(text)
    findings, metrics = [], []

    def whitelisted(a: int, b: int) -> bool:
        return any(a >= s and b <= e for s, e in wl)

    def in_quote(a: int, b: int) -> bool:
        return any(a >= s and b <= e for s, e in qs)

    for pid, sev, label, rx, thr, fix in PATTERNS:
        if pid in cfg["off"]:
            continue
        hits = [m for m in rx.finditer(masked) if not whitelisted(m.start(), m.end())]
        # C1 은 접속부사 어절("하지만, ")을 제외한다 — 어미가 아니라 부사다.
        if pid == "C1":
            hits = [m for m in hits if eojeol_at(masked, m.start()) not in CONJ_ADVERBS]
        if len(hits) <= thr:
            continue
        counted = hits[thr:]
        # C2 는 2회 이상이면 S1 로 승격(korean-style.md C2 주).
        eff = "S1" if (pid == "C2" and len(counted) >= 2) else sev
        for m in counted:
            findings.append({
                "id": pid, "severity": eff, "label": label,
                "line": line_of(text, m.start()),
                "excerpt": text[max(0, m.start() - 12):m.end() + 12].replace("\n", " ").strip(),
                "fix": fix,
                "quoted": in_quote(m.start(), m.end()),
            })

    # 이모지 한도 — masked 를 센다. text 를 세면 MASKS 의 상태 글리프 면제가
    # 무효가 된다(실측: answer 표면 ✅ 하나가 C4 S1 으로 exit 2 를 냈다).
    emojis = [m for m in EMOJI.finditer(masked) if not whitelisted(m.start(), m.end())]
    if len(emojis) > cfg["emoji"]:
        findings.append({
            "id": "C4", "severity": "S1" if cfg["emoji"] == 0 else "S2",
            "label": f"이모지 한도 초과 ({len(emojis)} > {cfg['emoji']})",
            "line": line_of(text, emojis[0].start()),
            "excerpt": "".join(m.group() for m in emojis[:8]),
            "fix": f"{surface} 표면 한도는 {cfg['emoji']}개",
        })

    sents = sentences(masked)

    # 문장 길이 (스키마 상한이 있는 표면만)
    if cfg["len"] and sents:
        lo, hi = cfg["len"]
        bad = [(off, s) for off, s in sents if not (lo <= visible_len(s) <= hi)]
        if bad:
            metrics.append({
                "id": "M-len", "label": f"문장 길이 이탈 {len(bad)}/{len(sents)} ({lo}~{hi}자)",
                "line": line_of(text, bad[0][0]), "count": len(bad), "total": len(sents),
                "detail": [f"{visible_len(s)}자: {s[:24]}" for _, s in bad[:3]],
            })

    # C5 같은 종결어미 3연속 — 문서 표대로 S2 finding 이다(점수 집계에 들어간다).
    if "C5" not in cfg["off"] and len(sents) >= 3:
        keys = [ending_key(s) for _, s in sents]
        run, worst, at = 1, 1, 0
        for i in range(1, len(keys)):
            if keys[i] and keys[i] == keys[i - 1]:
                run += 1
                if run > worst:
                    worst, at = run, i
            else:
                run = 1
        # 4연속부터 — 존댓말 설명형 채널은 '~니다' 3연속이 정상 격식이다.
        # profile.md 가 정한 격식과 싸우지 않는다(korean-style.md §고칠 때의 원칙).
        if worst >= 4:
            findings.append({
                "id": "C5", "severity": "S2", "label": f"같은 종결어미 {worst}연속",
                "line": line_of(text, sents[at][0]),
                "excerpt": sents[at][1][:40],
                "fix": "종결을 섞는다",
            })

    # 인용 구간 위반은 점수·판정에서 뺀다 — 고칠 수 없는 텍스트로 파이프라인을
    # 세우지 않는다. 보고에는 그대로 실어 원문 확인을 유도한다.
    live = [f for f in findings if not f.get("quoted")]
    quoted = [f for f in findings if f.get("quoted")]

    score = 100
    for f in live:
        score -= PENALTY[f["severity"]]
    for m in metrics:
        # 길이 이탈은 비율로 깎는다 — 한 문장만 어긋난 것과 전부 어긋난 것을 같은
        # 3점으로 치면 스키마 위반이 통과한다(실측: 1자 나레이션 1문장이 PASS 였다).
        if m.get("total"):
            ratio = m["count"] / m["total"]
            score -= min(15, round(15 * ratio)) + (5 if ratio > 0.5 else 0)
        else:
            score -= METRIC_PENALTY
    score = max(0, score)

    s1 = sum(1 for f in live if f["severity"] == "S1")
    exit_code = 2 if s1 else (1 if score < WARN_BELOW else 0)
    # 면제가 조용한 통과가 되면 안 된다. 검사기는 출처가 진짜인지 모른다 —
    # "출처: 안내문" 여덟 글자로 S1 여섯 건이 판정에서 빠질 수 있다(실측).
    # 그래서 면제를 적용했다는 사실 자체를 사람에게 올린다: exit 0 을 1(경고)로
    # 바닥 처리해 publish §1 의 기존 규칙("exit 1 은 승인 제시문에 그대로 적는다")에
    # 태운다. 1 은 차단이 아니므로 정당한 인용은 그대로 게시로 간다.
    if quoted and exit_code == 0:
        exit_code = 1

    return {
        "surface": surface,
        "chars": len(text),
        "sentences": len(sents),
        "findings": findings,
        "quoted_findings": len(quoted),
        "metrics": metrics,
        "score": score,
        "s1": s1,
        "s2": sum(1 for f in live if f["severity"] == "S2"),
        "s3": sum(1 for f in live if f["severity"] == "S3"),
        "verdict": {0: "PASS", 1: "WARN", 2: "FAIL"}[exit_code],
        "exit_code": exit_code,
    }


def render(r: dict) -> str:
    head = (f"판정 {r['verdict']} · 점수 {r['score']}/100 · "
            f"S1 {r['s1']} S2 {r['s2']} S3 {r['s3']}")
    if r["quoted_findings"]:
        head += f" · 인용면제 {r['quoted_findings']}"
    lines = [
        f"check-style — 표면 {r['surface']} / {r['chars']}자 {r['sentences']}문장",
        head,
        "",
    ]
    live = [f for f in r["findings"] if not f.get("quoted")]
    quoted = [f for f in r["findings"] if f.get("quoted")]
    if live:
        lines.append("[탐지]")
        for f in live:
            lines.append(f"  {f['severity']} {f['id']} L{f['line']} {f['label']}")
            lines.append(f"      … {f['excerpt']} …")
            lines.append(f"      → {f['fix']}")
    else:
        lines.append("[탐지] 없음")
    if quoted:
        lines.append("")
        lines.append(f"[인용 면제 {len(quoted)}건 — 점수에서 제외, 판정은 최소 WARN]")
        for f in quoted:
            lines.append(f"  ({f['severity']} {f['id']}) L{f['line']} {f['label']} — {f['excerpt']}")
        lines.append("  남의 말을 옮긴 것이면 고치지 않는다. 우리가 쓴 문장이면 따옴표를 풀고 고친다.")
    if r["metrics"]:
        lines.append("")
        lines.append("[지표]")
        for m in r["metrics"]:
            lines.append(f"  {m['id']} L{m['line']} {m['label']}")
            for d in m["detail"]:
                lines.append(f"      {d}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 자가 검증 — 규칙을 고칠 때마다 돌린다. 세 축을 본다: 슬롭을 잡는가,
# 멀쩡한 글을 통과시키는가, Do-NOT 구간에 오탐을 내지 않는가.
# ---------------------------------------------------------------------------

SELFTEST = [
    ("슬롭 검출", "answer", 2,
     "오늘은 임시거주 제도에 대해 함께 알아볼까요.\n"
     "이 제도는 개정되어졌습니다.\n"
     "신고 기한이 중요한 의미를 가지고 있습니다.\n"
     "결론적으로 이 변화는 시사하는 바가 큽니다.\n"
     "단순한 절차가 아니라 생활의 문제입니다.\n"
     "등록이 아니라 보호의 문제입니다.\n"
     "도움이 되셨길 바랍니다.\n"),
    ("정상 통과", "answer", 0,
     "신고 기한이 바뀌었다.\n전에는 사흘이었다.\n이제는 도착 즉시다.\n"
     "하루만 늦어도 과태료가 나온다.\n영수증을 받아 두자.\n"),
    ("오탐 없음", "report", 0,
     "신고가 도착 즉시로 바뀝니다 🇻🇳\n"
     "시행일은 2026년 7월 15일, 과태료는 300만~500만 동.\n"
     "접수증 사진은 남겨두세요.\n"
     "링크는 https://example.com/guide 를 보세요.\n"
     "#베트남 #임시거주 #하노이\n"),
    ("접속부사 오탐 없음", "commit", 0,
     "신고 기한이 도착 즉시로 바뀝니다.\n"
     "하지만, 집주인이 대신 신고하는 관행은 그대로입니다.\n"
     "그런데, 최종 책임은 본인에게 남습니다.\n"
     "여러분은 어떻게 하고 계신가요?\n"),
    # 어휘 티가 없는 대신 관측형 종결로 흐르는 슬롭 — 초기 규칙이 놓쳤던 유형.
    ("관측형 슬롭 검출", "commit", 2,
     "이번 개정은 많은 분들에게 도움이 될 것으로 보입니다.\n"
     "다양한 사례가 보고되고 있습니다.\n"
     "앞으로의 변화가 주목됩니다.\n"),
    # 플랫폼 문법이 요구하는 격식 — 검사기가 문어체로 끌고 가면 안 된다.
    ("반말 구어 통과", "hitl", 0,
     "신고 기한 바뀐 거 알아?\n"
     "예전엔 사흘이었는데 이제 도착하자마자야.\n"
     "집주인이 해주겠거니 하다가 과태료 물더라.\n"
     "너는 어떻게 하고 있어?\n"),
    ("키워드형 제목 통과", "comment", 0,
     "베트남 임시거주 신고 도착 즉시로 변경 — 2026년 7월 시행\n"
     "사흘이던 기한이 없어졌습니다. 과태료 기준과 접수증 보관까지 정리했습니다.\n"
     "#Shorts #베트남 #임시거주\n"),
    # 슬롭을 덩어리 마스크 뒤에 숨기는 우회 3종 — 따옴표·백틱·코드펜스.
    # 귀속 없이 따옴표만 씌운 것은 인용이 아니다.
    ("따옴표 우회 차단", "report", 2,
     '"오늘은 제도에 대해 함께 알아볼까요. '
     '결론적으로 이 변화는 시사하는 바가 큽니다."\n'),
    # 출처를 특정하지 못하는 서사 어휘로는 면제되지 않는다. 여섯 개를 각각 고정한다 —
    # 하나만 막으면 나머지가 그대로 남는다(실측으로 여섯 개 전부 통과했었다).
    ("서사 어휘 우회 차단 — 그가 말했다", "report", 2,
     '그가 말했다. "오늘은 제도에 대해 함께 알아볼까요. 결론적으로 시사하는 바가 큽니다."\n'),
    ("서사 어휘 우회 차단 — 이렇게", "report", 2,
     '이렇게. "오늘은 제도에 대해 함께 알아볼까요. 결론적으로 시사하는 바가 큽니다."\n'),
    ("서사 어휘 우회 차단 — 다음과 같습니다", "report", 2,
     '다음과 같습니다. "오늘은 제도에 대해 함께 알아볼까요. 결론적으로 시사하는 바가 큽니다."\n'),
    ("서사 어휘 우회 차단 — 전문가는 밝혔다", "report", 2,
     '전문가는 밝혔다. "오늘은 제도에 대해 함께 알아볼까요. 결론적으로 시사하는 바가 큽니다."\n'),
    ("서사 어휘 우회 차단 — 적혀 있다", "report", 2,
     '적혀 있다. "오늘은 제도에 대해 함께 알아볼까요. 결론적으로 시사하는 바가 큽니다."\n'),
    ("서사 어휘 우회 차단 — 인용", "report", 2,
     '인용. "오늘은 제도에 대해 함께 알아볼까요. 결론적으로 시사하는 바가 큽니다."\n'),
    # 무엇의 말인지 특정하지 못하는 지시대명사·범용어는 표지가 아니다.
    ("지시대명사 우회 차단 — 이것에 따르면", "report", 2,
     '이것에 따르면 "오늘은 제도에 대해 함께 알아볼까요. 결론적으로 시사하는 바가 큽니다."\n'),
    ("범용어 우회 차단 — 자료에 따르면", "report", 2,
     '자료에 따르면 "오늘은 제도에 대해 함께 알아볼까요. 결론적으로 시사하는 바가 큽니다."\n'),
    # 앞줄 머리에 기관명만 흘리고 아래에 슬롭을 묶는 우회 — 끝 40자 밖이라 안 걸린다.
    ("앞줄 머리 기관명 우회 차단", "report", 2,
     '공안부 자료를 정리했습니다. 신고 기한과 과태료 기준, 접수증 보관 방식, '
     '온라인 확인 절차까지 하나씩 짚어 봤습니다.\n'
     '"오늘은 제도에 대해 함께 알아볼까요. 결론적으로 시사하는 바가 큽니다. '
     '도움이 되셨길 바랍니다."\n'),
    # 개인 출처 인용도 면제 대상이다 — 기관만 인정하면 남의 문자를 고치라는 처방이 된다.
    ("개인 출처 인용 면제 — 집주인", "commit", 1,
     "집주인이 보낸 문자는 이랬습니다.\n"
     '"신고는 제가 대신 했고, 접수증은 나중에 드릴게요. 급하시면 직접 가셔도 되는데, '
     '서류는 제가 가지고 있어서 같이 가셔야 합니다."\n'
     "그래서 직접 갔더니 접수 기록이 없었습니다.\n"),
    # "~를 보고 알았습니다" 는 옮긴 게 아니라 알게 된 계기다 — 표지가 아니다.
    ("경위 서술은 표지가 아니다", "commit", 2,
     "친구가 보낸 문자를 보고 알았습니다. 제도가 바뀐 걸 몰랐거든요.\n"
     '"오늘은 제도에 대해 함께 알아볼까요. 결론적으로 시사하는 바가 큽니다."\n'),
    # 같은 어미라도 뒤에 옮김 동사가 오면 계기가 아니라 인용 도입이다. 주체가
    # SOURCE_NOUNS 밖(친구·사장님·선배)일 때 행위형이 유일한 통로라 이걸 막으면
    # 정당한 인용이 차단된다.
    ("옮김 동사가 오면 인용 도입이다", "commit", 1,
     "친구가 보낸 문자를 받고 그대로 옮깁니다.\n"
     '"신고는 제가 대신 했고, 접수증은 나중에 드릴게요. 급하시면 직접 가셔도 '
     '되는데, 서류는 제가 가지고 있어서 같이 가셔야 합니다."\n'),
    ("개인 출처 인용 면제 — 행위형", "commit", 1,
     "사장님이 보낸 메일 그대로입니다.\n"
     '"연차는 본인이 신청해야 하는데, 대리 신청은 인정되지 않습니다."\n'),
    # 출처를 특정하면 면제된다 — 기관명·법령명·URL 세 경로. 면제돼도 exit 는 1 이다
    # (검사기는 출처의 진위를 모른다 — 면제 사실을 사람에게 올려 확인시킨다).
    ("출처 특정 인용 면제 — 기관·법령", "commit", 1,
     '공안부 시행령 원문은 이렇게 돼 있습니다.\n'
     '"신고 의무는 체류자 본인에게 있어서 대행 여부와 무관하게 판단되어진다."\n'),
    ("출처 특정 인용 면제 — URL", "commit", 1,
     '원문 https://example.gov.vn/decree 에는 이렇게 적혀 있습니다.\n'
     '"신고 의무는 체류자 본인에게 있어서 대행 여부와 무관하게 판단되어진다."\n'),
    # 면제는 조용한 PASS 가 되지 못한다 — 짧은 출처 접두어로 S1 을 지워도 exit 는 1.
    ("면제는 exit 0 을 만들지 못한다", "report", 1,
     '출처: 안내문\n'
     '"오늘은 제도에 대해 함께 알아볼까요. 결론적으로 시사하는 바가 큽니다. '
     '도움이 되셨길 바랍니다."\n'),
    # PREV_LINE_TAIL 이 지키는 유일한 형태 — 출처가 앞줄에 있고 인용이 같은 줄에서
    # 60자 넘게 들여쓰인 경우. 60자 창은 앞줄에 닿지 못하고 앞줄 꼬리만 닿는다.
    # 상수를 0 으로 되돌리면 이 정당한 인용이 exit 2 로 막힌다(실측).
    ("앞줄 꼬리는 깊은 들여쓰기를 지킨다", "commit", 1,
     "이번에 바뀐 부분은 시행령에 그대로 나와 있습니다.\n"
     "제가 읽은 그대로 아래에 옮겨 둡니다. 손대거나 앞뒤를 자르지 않았고 번역도 "
     "하지 않았어요. 원문입니다 "
     '"신고 의무는 체류자 본인에게 있어서 대행 여부와 무관하게 판단되어진다."\n'),
    # 사람은 출처를 60자에 맞춰 적지 않는다 — 인용 바로 앞 줄이면 거리와 무관하게 면제.
    ("앞 줄 귀속은 거리와 무관", "commit", 1,
     '아래는 이번에 바뀐 부분을 확인하려고 찾아본 공안부 시행령의 해당 조문 원문 '
     '그대로이며, 번역 없이 옮깁니다.\n'
     '"신고 의무는 체류자 본인에게 있어서 대행 여부와 무관하게 판단되어진다."\n'),
    ("백틱 우회 차단", "report", 2,
     "`오늘은 제도에 대해 함께 알아볼까요. 결론적으로 시사하는 바가 큽니다.`\n"),
    ("코드펜스 우회 차단", "report", 2,
     "```\n오늘은 제도에 대해 함께 알아볼까요. 도움이 되셨길 바랍니다.\n```\n"),
    # 체크리스트 장르의 기본 문형 — 명사 나열은 3항 나열이 아니다.
    ("명사 나열 통과", "commit", 0,
     "여권, 비자, 계약서를 챙기세요.\n하노이, 다낭, 호치민은 절차가 다릅니다.\n"),
    # 원문 인용은 고칠 수 없다 — 점수는 세우지 않되 면제 사실은 경고로 남는다.
    ("인용 구간은 점수 제외", "commit", 1,
     "공안부 시행령 원문은 이렇게 돼 있습니다.\n"
     "\"신고 의무는 체류자 본인에게 있어서 대행 여부와 무관하게 판단되어진다.\"\n"
     "쉽게 말하면 집주인이 해줬어도 책임은 본인이 집니다.\n"),
    # 인용 밖 슬롭까지 봐주지는 않는다.
    ("인용 밖 위반은 그대로 차단", "commit", 2,
     "시행령 원문은 이렇다.\n"
     "\"신고는 도착 즉시 이루어져야 한다.\"\n"
     "결론적으로 이 변화는 시사하는 바가 큽니다.\n"),
    # 면제 조건은 비중이 아니라 출처 표시다 — 임계 경계 양쪽을 고정한다.
    # ① 귀속 없는 따옴표는 비중이 낮아도 면제되지 않는다(우회 차단).
    ("귀속 없는 인용은 면제 안 됨", "report", 2,
     "이번 개정 내용을 정리했습니다. 시행일과 과태료 기준을 아래에 적었습니다.\n"
     "접수증 보관 방법도 함께 넣었습니다. 필요한 분은 저장해두세요.\n"
     "현장에서 자주 나오는 질문도 마지막에 붙였습니다.\n"
     "\"오늘은 제도에 대해 함께 알아볼까요. 결론적으로 시사하는 바가 큽니다.\"\n"),
    # ② 귀속 있는 인용은 비중이 높아도 면제된다(정당한 원문 인용).
    ("귀속 있는 인용은 비중 무관 면제", "commit", 1,
     "시행령 원문입니다.\n"
     "\"거주지 이전 신고는 도착 즉시 이루어져야 하며, 신고 의무는 체류자 본인에게 "
     "있어서 집주인의 대행 여부와 무관하게 판단되어진다.\"\n"),
    # 고정 관용구는 부정 대구가 아니다.
    ("다름 아니라 통과", "hitl", 0,
     "다름 아니라 어제 겪은 일인데.\n다름 아니라 신고 기한 얘기야.\n"),
    # 어휘 티 없이 내용만 빈 보도자료체.
    ("공허한 수사 검출", "commit", 1,
     "디지털 전환의 물결 속에서 제도도 바뀝니다.\n"
     "규제와 자율의 균형점을 찾아가는 과정입니다.\n"
     "중요한 것은 방향입니다.\n"),
    # 존재동사 "있어"·명사 "여지"는 번역투가 아니다.
    ("존재동사 오탐 없음", "hitl", 0,
     "영수증은 가방에 있어.\n지금 어디에 있어?\n다른 해석의 여지는 없다.\n"),
    # 어휘 티 대신 조수 말투·기계적 열거로 흐르는 슬롭.
    ("조수 말투 나레이션 검출", "answer", 2,
     "안녕하세요! 오늘 소식입니다.\n"
     "빠르고 간편하며 안전한 절차입니다.\n"
     "첫째로 신청서를 냅니다. 둘째로 서류를 냅니다. 마지막으로 기다립니다.\n"
     "끝까지 읽어주셔서 고맙습니다.\n"),
    # --- astra 전용 픽스처 -------------------------------------------------
    # HITL 선택지 — 결과 중심 라벨 + 선택지별 결과 한 줄, 정상 문형.
    ("HITL 선택지 통과", "hitl", 0,
     "머지 후 어느 브랜치로 승격할까요?\n"
     "1. dev — 통합 브랜치에 바로 반영 (권장)\n"
     "2. staging — 배포 전 검증 환경으로 승격\n"
     "3. skip — 이번에는 승격하지 않음\n"),
    # 게이트 리포트의 ✅/❌/⚠️ 상태 표기는 데이터라 이모지 한도에서 뺀다.
    ("리포트 상태 표기 통과", "report", 0,
     "✅ 테스트 12건 전부 통과\n"
     "❌ 네이밍 위반 2건 — 표준 용어로 바꿔야 한다\n"
     "⚠️ 커버리지 71%는 목표 80%에 못 미친다\n"),
    # 기계 파싱 계약 라인은 검사 대상이 아니다 — 고치면 부모 루프가 깨진다.
    ("계약 라인은 가린다", "report", 0,
     "검증이 끝났다.\n"
     "ASTRA_LOOP_RESULT: score=90 verdict=FAIL p0=0\n"),
    # doc 표면은 DOC_MASKS 자동 적용 — 규칙 표 안의 예시 문구는 데이터다.
    ("문서 표 마스킹", "doc", 0,
     "규칙 표는 아래와 같다.\n"
     "\n"
     "| 규칙 | 예 |\n"
     "|---|---|\n"
     "| D1 | 결론적으로 이 변화는 시사하는 바가 큽니다 |\n"
     "\n"
     "표 밖 본문은 평소처럼 쓴다.\n"),
    ("문서 본문 슬롭 검출", "doc", 2,
     "결론적으로 이 정리는 시사하는 바가 큽니다.\n"
     "도움이 되셨길 바랍니다.\n"),
    ("커밋 메시지 통과", "commit", 0,
     "포트 충돌 시 +100 이동이 안 되던 문제를 고쳤다.\n"
     "원인은 helper 가 상태 파일을 읽지 않던 것.\n"),
    ("주석 조각 통과", "comment", 0,
     "포트가 이미 점유된 경우 +100 씩 밀어 재시도\n"
     "한 번 실패하면 사용자에게 알린다\n"),
    # label 은 길이 밴드가 있다 — 30자를 넘는 장문 라벨은 경고로 올린다.
    ("장문 라벨 경고", "label", 1,
     "이 옵션을 고르면 통합 브랜치의 모든 변경 사항이 스테이징 환경으로 한꺼번에 "
     "승격되고 배포 검증 대상이 됩니다\n"),
    # 상태 글리프는 어느 표면에서든 이모지 한도 밖이다 — EMOJI 를 masked 에서
    # 세지 않으면 이 픽스처가 깨진다(회귀 고정).
    ("상태 표기는 한도 밖", "answer", 0,
     "✅ 끝났다.\n"),
    # doc 의 > 는 콜아웃 산문이다 — 가리면 인용 부호가 슬롭 은신처가 된다.
    ("문서 콜아웃도 본다", "doc", 2,
     "> 결론적으로 이 변경은 시사하는 바가 큽니다. 도움이 되셨길 바랍니다.\n"),
]


def selftest() -> int:
    failed = 0
    for name, surface, want, text in SELFTEST:
        got = analyze(unicodedata.normalize("NFC", text), surface)
        ok = got["exit_code"] == want
        failed += 0 if ok else 1
        ids = ",".join(sorted({f["id"] for f in got["findings"]})) or "-"
        print(f"[{'PASS' if ok else 'FAIL'}] {name} ({surface}) "
              f"exit={got['exit_code']} 기대={want} 점수={got['score']} 탐지={ids}")
    print(f"\n{len(SELFTEST) - failed}/{len(SELFTEST)} 통과")
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="한국어 AI 티 결정적 검사기")
    p.add_argument("path", nargs="?", help="검사할 텍스트 파일 (- 는 표준입력)")
    p.add_argument("--surface", choices=SURFACES,
                   help="표면 — 표면별로 임계와 끄는 규칙이 다르다")
    p.add_argument("--json", action="store_true", help="구조화 출력")
    p.add_argument("--doc", action="store_true",
                   help="내부 문서 모드 — 마크다운 표·인용 블록을 추가로 가린다. "
                        "산출 카피에는 쓰지 않는다(표가 슬롭 은신처가 된다)")
    p.add_argument("--selftest", action="store_true", help="내장 픽스처로 규칙 자가 검증")
    args = p.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.path or not args.surface:
        p.error("path 와 --surface 가 필요하다 (규칙 검증만 할 때는 --selftest)")

    # UnicodeDecodeError 는 ValueError 계열이라 OSError 로는 안 잡힌다 — 레거시
    # EUC-KR/CP949 소스에서 트레이스백 대신 실행 오류(3)로 나가야 exit 1(경고)과
    # 구분된다.
    try:
        raw = sys.stdin.read() if args.path == "-" else open(args.path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"check-style: 입력을 읽지 못했다 — {e}", file=sys.stderr)
        return 3

    text = unicodedata.normalize("NFC", raw)
    if not text.strip():
        print("check-style: 빈 입력", file=sys.stderr)
        return 3

    try:
        result = analyze(text, args.surface, args.doc)
    except Exception as e:  # 게이트가 죽어서 파이프라인을 막지는 않게 한다
        print(f"check-style: 분석 실패 — {e}", file=sys.stderr)
        return 3

    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render(result))
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
