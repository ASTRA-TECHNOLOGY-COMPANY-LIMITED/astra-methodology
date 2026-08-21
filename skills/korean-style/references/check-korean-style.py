#!/usr/bin/env python3
"""한국어 AI 티 결정적 검사기 — 문서·제안서·주석·대화 공통 게이트.

규칙 정의는 같은 폴더의 `korean-style.md` 가 SoT다. 이 스크립트는 그 규칙을
기계 판정으로 옮긴 것이며, **판정 결과가 정본이다**. 에이전트 자가 판단으로
덮어쓰지 않는다 — 자가 평가는 언제나 통과하기 때문이다.

    python3 check-korean-style.py --surface doc docs/blueprints/auth.md
    python3 check-korean-style.py --surface proposal --kind html section-1.html
    cat answer.txt | python3 check-korean-style.py --surface chat -

exit 0 통과 / 1 경고(S2 누적·인용면제) / 2 불합격(S1 검출) / 3 실행 오류.

의존성 없음(표준 라이브러리만). 플러그인 배포본에서 그대로 실행된다.

**이 파일은 astra-methodology 와 proposal-specialist 에서 바이트 단위로 같다.**
한쪽만 고치면 드리프트다. 고칠 때는 양쪽에 같이 넣고 md5 를 맞춘다.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata

SURFACES = ("doc", "proposal", "report", "hitl", "chat", "comment")
KINDS = ("auto", "md", "html", "code", "text")

# ---------------------------------------------------------------------------
# 입력 정제 — 검사 대상이 아닌 구간을 같은 길이의 공백으로 지운다(오프셋·행 보존).
# ---------------------------------------------------------------------------

FENCE = re.compile(r"(?ms)^[ \t]*```.*?^[ \t]*```[ \t]*$")
HTML_DROP = re.compile(r"(?is)<(script|style)\b.*?</\1>|<!--.*?-->")
HTML_TAG = re.compile(r"(?s)<[^>]+>")

# 주석만 남기는 추출 — 코드 본문은 검사 대상이 아니다.
COMMENT_RX = (
    re.compile(r"(?s)/\*.*?\*/"),          # C 계열 블록
    re.compile(r"(?m)//[^\n]*"),           # C 계열 행
    re.compile(r"(?m)(?<!\S)#[^\n]*"),     # 파이썬·셸 행
    re.compile(r"(?s)\"\"\".*?\"\"\""),    # 파이썬 독스트링
    re.compile(r"(?s)<!--.*?-->"),         # 마크업
)

CODE_EXT = {
    ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".java", ".kt",
    ".go", ".rs", ".rb", ".php", ".c", ".h", ".cpp", ".hpp", ".cs",
    ".sh", ".bash", ".zsh", ".sql", ".css", ".scss", ".yml", ".yaml",
}


def blank(text: str, spans) -> str:
    """구간을 같은 길이의 공백으로 지운다. 줄바꿈은 남겨 행 번호를 보존한다."""
    out = list(text)
    for a, b in spans:
        for i in range(a, b):
            if out[i] != "\n":
                out[i] = " "
    return "".join(out)


def extract(text: str, kind: str) -> str:
    """검사 대상 텍스트만 남긴다. 길이·오프셋은 그대로 유지한다."""
    if kind == "md":
        # 코드펜스만 지운다. **인라인 코드는 지우지 않는다** — 백틱이 슬롭
        # 은신처가 되기 때문이다(자매 플러그인 실측: 백틱 안에 슬롭을 넣어 통과).
        return blank(text, [(m.start(), m.end()) for m in FENCE.finditer(text)])
    if kind == "html":
        t = blank(text, [(m.start(), m.end()) for m in HTML_DROP.finditer(text)])
        return blank(t, [(m.start(), m.end()) for m in HTML_TAG.finditer(t)])
    if kind == "code":
        keep = []
        for rx in COMMENT_RX:
            keep += [(m.start(), m.end()) for m in rx.finditer(text)]
        if not keep:
            return " " * len(text)
        drop, cursor = [], 0
        for a, b in sorted(keep):
            if a > cursor:
                drop.append((cursor, a))
            cursor = max(cursor, b)
        if cursor < len(text):
            drop.append((cursor, len(text)))
        return blank(text, drop)
    return text


def kind_of(path: str) -> str:
    low = path.lower()
    if low.endswith((".md", ".markdown", ".mdx")):
        return "md"
    if low.endswith((".html", ".htm", ".xhtml", ".vue", ".svelte")):
        return "html"
    for ext in CODE_EXT:
        if low.endswith(ext):
            return "code"
    return "text"


# ---------------------------------------------------------------------------
# 마스킹 — 한국어 규칙이 보면 안 되는 값들.
# ---------------------------------------------------------------------------

# 여기에 "덩어리를 통째로 가리는" 마스크를 넣지 않는다. 자매 플러그인 실측 사고 셋:
# 인용 200자를 가렸더니 슬롭을 따옴표에 넣어 0점이 100점이 됐고, 백틱·코드펜스를
# 가렸더니 같은 우회가 다시 열렸고, 30자짜리 화이트리스트가 "나도" 두 글자로
# 네 규칙을 지웠다. 덩어리 마스크는 extract() 가 맡는다(코드·태그뿐).
MASKS = (
    re.compile(r"https?://\S+"),                 # URL
    re.compile(r"#[\w가-힣]+"),                   # 해시태그
    re.compile(r"[A-Za-z][A-Za-z0-9_.\-]*"),     # 영문 약어·식별자
    re.compile(r"\d[\d,.\-~%/:]*"),              # 수치·날짜·단위
)

# 영문 규칙(E*)용 뷰 — 영어를 남기고 URL·수치만 가린다. 한국어 마스크가 영어를
# 통째로 지우므로 같은 뷰에서는 영문 상투어를 볼 수 없다.
MASKS_EN = (
    re.compile(r"https?://\S+"),
    re.compile(r"`[^`\n]+`"),
    re.compile(r"\d[\d,.\-~%/:]*"),
)

# 이모지만 — 화살표(→ ←)·괘선은 문서 기호이지 이모지가 아니다(오탐 주범).
EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF"   # 이모티콘·픽토그램·교통·기호 보충
    "☀-⛿"            # 기타 기호 ☀ ⚡ ⚠
    "✀-➿"            # 장식 기호 ✅ ✂
    "⬀-⯿"            # 굵은 화살표·별 ⬅ ⭐
    "〰〽㊗㊙]"
)

MD_BOLD = re.compile(r"\*\*[^*\n]{1,80}\*\*")
MD_HEAD = re.compile(r"(?m)^#{1,6}\s+\S")


def mask(text: str, patterns) -> str:
    spans = []
    for rx in patterns:
        spans += [(m.start(), m.end()) for m in rx.finditer(text)]
    return blank(text, spans)


# ---------------------------------------------------------------------------
# 패턴 — (ID, 심각도, 설명, 정규식, 임계, 고치는 법)  임계 = 이 횟수를 넘겨야 계상.
# ID 가 E 로 시작하면 영문 뷰(MASKS_EN)에서 본다.
# korean-style.md 의 규칙표와 1:1이다. 한쪽만 고치지 않는다.
# ---------------------------------------------------------------------------

# 1인칭 주어가 앞에 오면 "~야 할 것이다"는 훈계가 아니라 화자 자신의 의지다.
# **WHITELIST 로 빼면 안 된다** — 화이트리스트는 구간 통째 면제라 "나도" 두 글자로
# 그 안의 다른 규칙까지 전부 빠진다(자매 플러그인 실측 4건). 파이썬 re 는 가변폭
# lookbehind 를 못 쓰므로 analyze() 후처리로 D3 에만 건다.
FIRST_PERSON_LEAD = re.compile(
    r"(?:내가|나도|나는|저도|저는|제가|우리가|우리도)[^.!?\n]{0,30}$")

# 명사화 대상 — 뒤에 '수행/실시/진행/실행'이 붙으면 동사를 명사에 가둔 형태다.
# 목록은 닫힌 기술 용어만 담는다. 열린 명사를 넣으면 "회의를 진행합니다" 같은
# 정상 문장을 먹는다(회의는 동사가 아니라 사건이다).
NOMINALIZED = (
    r"(삭제|저장|조회|등록|수정|검증|확인|처리|분석|설계|구현|배포|검토|측정"
    r"|개선|최적화|점검|반영|적용|생성|삽입|갱신|변환|추출|작성|수집|관리|운영"
    r"|연동|이관|전환|산정|집계|정렬|필터링|캐싱)"
)

Pattern = tuple  # (id, sev, label, regex, threshold, fix)

PATTERNS: list[Pattern] = [
    # --- 번역투 T -----------------------------------------------------------
    # 관형형 "~에 대한"도 같은 번역투다("제도에 대한 설명" → "제도 설명"). 뒤 공백을
    # 요구해 "반대한 사람"·"상대한 업체"의 어간 우연 일치를 비켜 간다.
    # **`관한`은 넣지 않는다** — "개인정보 보호에 관한 법률"이 법령 제목의 표준이다.
    #
    # 짧은 카피 게이트에서는 S1(반려)이었는데 **문서 표면에서는 S2 로 낮췄다.**
    # 두 가지가 근거다. (1) 사용자 지침의 번역투 표에 `~에 대한`은 없다 — 거기 있는
    # 건 `~를 통해`·`~에 있어서`·`~하기 위해`다. (2) 이 두 저장소의 한국어 문서
    # 실측에서 "변수에 대한 집중 관리"·"섹션에 대한 상세 내용"처럼 고칠 값어치는
    # 있지만 글을 막을 정도는 아닌 용례가 대부분이었다. 임계 1 을 둬서 한 번은
    # 넘어가고 반복될 때만 잡는다 — 신호는 존재가 아니라 반복이다.
    ("T1", "S2", "~에 대해(서)·~에 대한·~에 관해",
     re.compile(r"에\s*(대(해서|해|하여|한(?=\s))|관(해서|해|하여))"), 1,
     "목적격 조사로 직결 — '제도에 대해 설명한다' → '제도를 설명한다'"),
    # 존재동사와 구분한다 — "가방에 있어."는 정상이고 "문제에 있어서"만 번역투다.
    ("T2", "S1", "~에 있어서", re.compile(r"에\s*있어서(?=\s*[가-힣])"), 0,
     "'~에서' 또는 '~할 때'"),
    # '여지는'(명사 여지+는)은 뺀다 — 이중피동이 아니다. 여섯 계열 모두에 `집`(존댓말
    # 종결 "보여집니다")과 `질`("판단되어질")이 필요하다 — 없으면 대표형이 통째로 샌다.
    ("T3", "S1", "이중 피동",
     re.compile(r"(되어[지진졌집질]|보여[지진졌집질]|잊혀[지진졌집질]"
                r"|쓰여[지진졌집질]|불려[지진졌집질]|모아[지진졌집질])"), 0,
     "단순 피동으로 — '판단되어진다' → '판단한다'"),
    ("T4", "S1", "~을 가지고 있다", re.compile(r"[을를]\s*가지고\s*있"), 0,
     "동사로 — '강점을 가지고 있다' → '강점이 있다'"),
    # 피동 어미를 되·진·받으로만 잡으면 가장 흔한 "~된다"·"~됩니다"가 전부 샌다.
    # 피동 접미사 앞에는 어간이 온다 — `\S*` 로 두면 어절 첫 글자도 잡혀
    # "지표에 의해 진도를"이 걸렸다(자매 플러그인 실측 4건).
    ("T5", "S2", "~에 의해 + 피동",
     re.compile(r"에\s*의(해|하여)\s*[가-힣]*[가-힣](되|된(?!장)|됐|됩|진|받)"), 0,
     "능동으로 — '법에 의해 정해진다' → '법이 정한다'"),
    ("T6", "S2", "이중 조사", re.compile(r"(에서의|으로의|로의|에의|로부터의|으로부터의)"), 0,
     "절로 풀기 — '현지에서의 생활' → '현지 생활'"),
    ("T7", "S2", "~를 통해 반복", re.compile(r"[을를]\s*통(해서|해|하여)"), 2,
     "3회를 넘으면 일부를 '~로'·'~해서'로 분산"),
    ("T8", "S2", "~라는 점에서 반복", re.compile(r"[라다]는\s*점에서"), 1,
     "'~라서'·'~니까'"),
    ("T9", "S3", "인칭 대명사 밀도",
     re.compile(r"\b(그|그녀|그들|그것)(는|은|가|를|의|에게|와|도)\b"), 2,
     "생략하거나 이름·호칭으로"),

    # --- 명사화·격식 과잉 N ---------------------------------------------------
    # "삭제 작업을 수행합니다" → "삭제합니다". 동사를 명사에 가두는 관공서·AI 문체다.
    # 목록형이라 위험하지만 **뒤에 오는 경동사로 판정**하므로 안전한 쪽이다
    # (앞말로 판정하는 축은 넓히면 오탐 100%가 된다 — 자매 플러그인 실측).
    ("N1", "S2", "명사화 동사 (수행·실시·진행·실행)",
     re.compile(NOMINALIZED + r"\s*(작업|업무|절차|과정)?\s*[을를]?\s*"
                r"(수행|실시|진행|실행)(하|합|했|한(?=\s)|해)"), 0,
     "동사로 되돌린다 — '삭제 작업을 수행합니다' → '삭제합니다'"),
    ("N2", "S2", "~하기 위해·~하기 위한",
     re.compile(r"[가-힣]{1,10}하기\s*위(해서|해|하여|한(?=\s))"), 1,
     "'~하려고'·'~하려면'. 관형형은 '~할'로 — '조회하기 위한 조건' → '조회할 조건'"),
    # "~해 드리도록 하겠습니다" → "~하겠습니다". 완곡을 두 겹 씌운 형태다.
    # **`하겠` 계열만 잡는다.** "늦지 않도록 하자"·"빠지지 않도록 하시죠"는 정상
    # 한국어에 가깝고, 규격서의 "~하도록 한다"도 표준 문형이라 뺐다. 사용자 지침에
    # 적힌 형태(~해 드리도록 하겠습니다)가 정확히 이 하나다. S1(차단)이라 좁게 둔다.
    ("N3", "S1", "~하도록 하겠습니다",
     re.compile(r"[가-힣]{1,8}(하|되|드리|보|주)도록\s*하겠"), 0,
     "한 겹으로 — '정리해 드리도록 하겠습니다' → '정리하겠습니다'"),
    # 쉬운 말로 바꿀 수 있는 딱딱한 한자어. '상기'는 '상기하다'(떠올리다)와 겹치므로
    # 뒤에 오는 명사로 묶는다.
    ("N4", "S2", "딱딱한 한자어",
     re.compile(r"(상기\s*(내용|사항|자료|문서|표|항목|바와|와\s*같)"
                r"|금번|익일|당해\s*(연도|사업)|제반\s*(사항|비용|절차|문제|여건)"
                r"|소정의|상이(하|한(?=\s)|합|함)|기입(하|해|란|을|이))"), 0,
     "쉬운 말로 — 상기 내용→위 내용, 상이하다→다르다, 기입→적기"),
    # '해당'은 기술 문서에서 사실상 표준어라 가볍게만 민다.
    ("N5", "S3", "'해당' 반복", re.compile(r"해당\s*[가-힣]"), 3,
     "대부분 '그' 또는 생략으로 통한다"),

    # --- AI 관용구 D ---------------------------------------------------------
    # 구어 축약 "~적으론"·"~적으로는"도 같은 상투어다. 세 단어만 명시해
    # "기본적으론"·"개인적으론" 같은 정상 부사는 비켜 간다.
    ("D1", "S1", "상투적 도입·결말어",
     re.compile(r"((?:결론|궁극|본질)적으(?:로[는은]?|론)"
                r"|요컨대|종합하면|정리하자면|정리하면(?=\s)|한마디로\s*말하면)"), 0,
     "삭제. 답은 첫 문장에서 말한다"),
    ("D2", "S1", "의의 과장",
     # 종결형만 잡으면 관형형이 샌다. 다만 **관형형은 뒤 명사로 갈린다** —
     # "주목받는 변화"(추상어=슬롭)와 "주목받는 기업"(구체 명사=사실 서술)이
     # 같은 형태다. 그냥 넓혔더니 정상 문장이 S1 으로 막혔다(실측 5건).
     re.compile(r"(시사하는\s*바가\s*[크큽]|의미가\s*[크큽]|주목할\s*만하"
                r"|주목(된다|받는다|됩니다|받습니다)"
                r"|주목(받는|되는|받은|받고\s*있는|되고\s*있는)"
                r"\s*(변화|대목|행보|움직임|흐름|점|부분|사실|현상|추세)"
                r"|평가된다|평가받는다|귀추가\s*주목|기대를\s*모으)"), 0,
     "무엇이 왜 그런지로 바꾸거나 삭제"),
    # 훈계형은 성질이 다른 둘이 섞여 있어서 나눴다. **심각도는 그 패턴이 실제로
    # 판별할 수 있는 만큼만 준다.**
    #
    # D3(S1) 은 문장 안에 판별 근거가 있다. 고정 관용구이거나(할 필요가 있다·하는
    # 것이 중요하다·명심해야) 청자 높임 `~셔야`가 문법 표지로 대상을 독자로 못박는다.
    # 오탐 위험이 없어 차단해도 된다.
    ("D3", "S1", "훈계형",
     re.compile(r"(할\s*필요(가|성이)\s*있|하는\s*것이\s*중요"
                r"|[가-힣]{1,6}[셔서]야\s*할\s*것(이다|입니다)|명심해야)"), 0,
     "'확인할 필요가 있다' → '확인하자'"),
    # D3b(S2) 는 못 갈린다. "기한을 지켜야 할 것이다"(훈계)와 "내년에는 시스템을
    # 바꿔야 할 것이다"(전망)가 같은 형태다. 갈리는 건 용언도 주어도 아니고
    # **화행**(누구에게 하는 말인가)인데, 그건 문장 어디에도 표지가 없다.
    # 뒤를 묶어 봤더니 전망·조건절 귀결 7종이 전부 차단됐다(실측). 그래서 차단이
    # 아니라 경고다 — 리포트·설계 문서는 전망을 쓰는 장르라 차단하면 글이 막힌다.
    ("D3b", "S2", "~야 할 것이다 (훈계면 고치고 전망이면 둔다)",
     re.compile(r"([을를]\s*(?:[가-힣]+\s+){0,2}[가-힣]{1,6}야\s*할\s*것(이다|입니다)"
                r"|[가-힣]{2,}(?:해|하여)야\s*할\s*것(이다|입니다))"), 0,
     "남에게 시키는 말이면 '지키자'·'지켜라'로. 전망이면 그대로 둔다"),
    ("D4", "S2", "완곡 회피",
     re.compile(r"(라고\s*할\s*수\s*있|로\s*보여진다|인\s*셈이다|라고\s*볼\s*수\s*있"
                r"|것으로\s*보(인다|입니다|이며)|것으로\s*예상|라고\s*여겨)"), 1,
     "단정할 수 있으면 단정한다"),
    ("D5", "S2", "과장 수식",
     re.compile(r"(혁신적|획기적|새로운\s*지평|게임\s*체인저|판도를\s*바꿀|놀라운"
                r"|최적의\s*솔루션|완벽한\s*대응)"), 0,
     "삭제. 강조는 수식어가 아니라 숫자로"),
    ("D6", "S2", "뜻 없는 수식어",
     re.compile(r"(매우|굉장히|효과적으로|원활하게|성공적으로|다양한|폭넓은|손쉽게"
                r"|극대화|만전을\s*기)"), 1,
     "삭제"),
    # 어휘 티는 없는데 내용도 없는 보도자료체 — 규칙 확장 실측에서 마지막까지
    # 통과하던 유형이다. "중요한 것은 X입니다"는 X 가 추상어일 때만 잡는다.
    ("D7", "S2", "공허한 수사",
     re.compile(r"(물결\s*속에서|시대의?\s*흐름\s*속|균형점을\s*찾|화두로\s*떠오"
                r"|답은\s*간단합니다|핵심은\s*딱\s*하나|새로운\s*국면"
                r"|중요한\s*것은\s*(방향|본질|자세|태도|의지|마음가짐|관점|균형))"), 0,
     "구체적 사실·숫자로 바꾸거나 삭제"),

    # --- 구조·리듬 C ---------------------------------------------------------
    # 한국어 AI 글을 가려내는 가장 값싸고 강한 신호다(KatFishNet 기반 실측 4.84배
    # 분리도). 그래서 S1 로 둔다.
    # `해도` 앞 네 글자를 뺀 이유: "섹션 유형(사업이해도, 기술방안, ...)"에서 명사
    # '이해도'의 도를 연결어미로 읽어 S1 이 났다(실측 오탐 5건). 견해·오해·양해도
    # 명사+보조사 '도'가 같은 꼴이라 같이 뺐고, 이 넷은 대응하는 연결어미가 없어
    # (오해하다 → "오해해도") 미탐을 만들지 않는다.
    # **`화`와 `분`은 일부러 넣지 않았다.** 넣으면 "변화해도,"·"강화해도,"·"충분해도,"
    # 가 통째로 미탐이 되는데, 반대급부인 '화해도'·'분해도'는 두 저장소 문서에서
    # 0회다(이해도만 22회). 좁히는 방향이라 안전하지만 그래도 최소로 좁힌다.
    ("C1", "S1", "연결어미 뒤 쉼표",
     re.compile(r"(지만|는데|면서|라서|어서|아서|으며|하며|거나|려면|더라도"
                r"|(?<![이오견양])해도|지요|는지),"), 0,
     "쉼표를 뺀다 — '발전하지만, 대응은 느리다' → '발전하지만 대응은 느리다'"),
    ("C2", "S2", "부정 대구 'A가 아니라 B'",
     re.compile(r"(이|가|은|는|도)?\s*아니라\s"), 0,
     "그냥 B라고 쓴다 (2회 이상이면 S1 승격)"),
    # 용언 3연속만 잡는다. 명사 나열("여권, 비자, 계약서")은 체크리스트 장르의
    # 기본 문형이라 대상이 아니다.
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
     re.compile(r"(함께\s*알아보|알아볼까요|알아보시죠|알아봅시다"
                r"|살펴볼까요|살펴보시죠|살펴봅시다"
                r"|오늘은\s*\S{0,20}에\s*대|이번\s*시간에는)"), 0,
     "본론부터"),
    ("A2", "S1", "마무리 인사",
     re.compile(r"(도움이?\s*되(셨|었)|참고하시기\s*바랍|참고\s*부탁|되시길\s*바랍"
                r"|읽어\s*주셔서\s*(감사|고맙)|읽어주셔서\s*(감사|고맙)"
                r"|시청해\s*주셔서|끝까지\s*(봐|읽)"
                r"|다음에도\s*(유익|좋은|알찬)|찾아뵙)"), 0,
     "삭제"),
    ("A3", "S2", "안 물어본 균형",
     re.compile(r"(물론\s.{0,40}도\s*있지만|양쪽\s*모두|일장일단|장단점이\s*있)"), 0,
     "한쪽을 고르거나 삭제"),
    ("A4", "S1", "인사 개시·홍보",
     re.compile(r"(안녕하세요|반갑습니다|소식을\s*전해\s*드리"
                r"|전해\s*드립니다|전해드립니다"
                r"|구독과?\s*좋아요|좋아요\s*눌러|구독\s*눌러"
                r"|알림\s*설정|많은\s*관심\s*부탁)"), 0,
     "본론부터"),
    # 자기 작업을 보고할 때의 상투구 — 커밋 메시지·완료 보고에서 가장 자주 샌다.
    ("A5", "S2", "작업 보고 상투구",
     re.compile(r"(성공적으로\s*(완료|수행|처리)|차질\s*없이|만전을|최선을\s*다하"
                r"|도움이\s*되었으면|더\s*궁금한\s*(점|것)이?\s*있으(시|)면"
                r"|언제든지?\s*(말씀|문의)|추가로\s*필요한\s*(사항|것)이?\s*있)"), 0,
     "'끝났습니다'로 충분하다. 남은 일이 있으면 그것만 적는다"),

    # --- 영문 AI 상투어 E (MASKS_EN 뷰) ---------------------------------------
    # 신호가 강한 것만. `landscape`·`realm`·`robust` 는 정상 기술 용어라 뺐다
    # (proposal-specialist 는 "16:9 landscape" 를 실제로 쓴다 — 확정 오탐이다).
    ("E1", "S2", "영문 AI 상투어",
     re.compile(r"(?i)\b(delve[sd]?|delving|tapestry|myriad|pivotal"
                r"|seamlessly|intricate|testament\s+to|underscor(e|es|ing)\s+the"
                r"|navigat(e|ing)\s+the\s+complexit)"), 0,
     "평범한 단어로. 'delve into' → 'look at'"),
    ("E2", "S3", "영문 상투어 반복",
     re.compile(r"(?i)\b(comprehensive|crucial|seamless|foster[s]?|leverag(e|es|ing)"
                r"|utiliz(e|es|ing)|robust|holistic|cutting[- ]edge)\b"), 2,
     "한 번은 괜찮다. 반복되면 평범한 단어로"),
    ("E3", "S2", "영문 부정 대구 (It's not X, it's Y)",
     re.compile(r"(?i)(it'?s\s+not\s+(just\s+)?\w+[^.\n]{0,40},?\s+it'?s"
                r"|not\s+only\s+\w+[^.\n]{0,40}\s+but\s+also)"), 0,
     "그냥 Y라고 쓴다"),
]

# 접속부사는 뒤에 쉼표가 와도 정상이다("하지만, ~"). C1 정규식이 어미로 잡는
# "하지만"과 어간이 붙은 "발전하지만"은 어절 전체를 봐야 구분된다.
CONJ_ADVERBS = {
    "하지만", "그렇지만", "그런데", "한데", "그러면서", "그래서", "그러니까",
    "그러므로", "다만", "게다가",
}

# 규칙이 잡아도 위반이 아닌 표현.
#
# **항목은 짧게 유지한다.** 화이트리스트는 매치가 그 구간 안에 들어가면 통째로
# 면제하므로, 긴 구간을 넣으면 그 안이 슬롭 은신처가 된다(자매 플러그인 실측:
# 30자짜리 1인칭 패턴을 넣었더니 "나도" 두 글자로 T1·D1·D6·T3 가 전부 빠졌다).
# 지금 항목은 전부 8자 이하다. 넓은 면제가 필요하면 화이트리스트가 아니라
# 해당 규칙에서 처리한다(D3 의 FIRST_PERSON_LEAD 후처리 참고).
WHITELIST = (
    # 부사 + '의' 는 이중 조사가 아니다 — "앞으로의 변화"는 자연스러운 한국어다(T6).
    re.compile(r"(앞|뒤|이후|향후|지금|평소)으?로의"),
    # "다름 아니라"는 고정 관용구다 — 부정 대구(C2)가 아니다. C2 매치가 뒤 공백까지
    # 포함하므로 화이트리스트도 공백을 덮어야 한다.
    re.compile(r"다름\s*아니라\s*"),
    # 콜아웃 머리표는 문서 서식이지 장식 이모지가 아니다.
    re.compile(r"(?m)^[ \t]*>[ \t]*[⚠💡📎📌]️?"),
)

# ---------------------------------------------------------------------------
# 표면별 설정
# ---------------------------------------------------------------------------

# off 목록이 표면별 완화의 유일한 창구다 — korean-style.md 의 "끄는 규칙" 열과
# 이 표가 정확히 같아야 한다. 한쪽만 고치지 않는다.
#
#   emoji  — 허용 개수(초과하면 한도 0 일 때 S1, 아니면 S2)
#   long   — 이 문장 수를 넘으면 "장문 부재"를 본다(None 이면 끔)
#   bold   — 볼드 밀도를 보는가(마크다운 표면만)
#   off    — 끄는 규칙
SURFACE_CFG = {
    # 설계·기획 문서, 매뉴얼, README. 절차 문서라 기계적 3단(C6)은 정상 문형이다.
    "doc":      {"emoji": 2, "long": 15, "bold": True,  "off": ("C6",)},
    # 제안서 본문. 격식 존댓말이 규범이라 종결어미 반복(C5)·3단 구성(C6)을 끈다.
    # 어휘 티(T·D·N·A)는 그대로 본다 — 격식체와 번역투는 다른 축이다.
    "proposal": {"emoji": 0, "long": 20, "bold": False, "off": ("C5", "C6", "T9")},
    # 분석 리포트(리스크·사업성·FP). 표와 수치가 본문이라 리듬 규칙을 완화한다.
    "report":   {"emoji": 1, "long": 20, "bold": True,  "off": ("C5", "C6")},
    # 사용자에게 던지는 질문. 짧아서 리듬 규칙이 맞지 않는다.
    "hitl":     {"emoji": 0, "long": None, "bold": False, "off": ("C3", "C5", "C6", "T9")},
    # 세션 응답. 짧은 답이 많아 리듬 규칙을 끄되 상투어는 그대로 본다.
    "chat":     {"emoji": 0, "long": None, "bold": True,  "off": ("C5", "T9")},
    # 코드 주석·커밋 메시지·PR 본문. 조각 문장이라 어휘 티만 본다.
    "comment":  {"emoji": 0, "long": None, "bold": False,
                 "off": ("C3", "C5", "C6", "T9", "D4", "E2")},
}

PENALTY = {"S1": 20, "S2": 7, "S3": 2}
WARN_BELOW = 85  # S1 이 없어도 이 점수 미만이면 exit 1

# 장문 기준. 대조 코퍼스 실측에서 AI 글의 결함은 문장 길이의 균일함이 아니라
# **장문의 부재**였다(1000문장당 AI 8.1 대 사람 91.3 — 사람 글의 약 9%가 장문).
# 그래서 "긴 문장이 하나도 없음"만 본다. 평균·분산은 보지 않는다.
LONG_SENT = 90

# ---------------------------------------------------------------------------


def whitelist_spans(text: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for rx in WHITELIST for m in rx.finditer(text)]


# 큰따옴표 직접 인용. 가리지 않는다(가리면 슬롭 은신처가 된다) — 대신 여기서 나온
# 위반은 `quoted` 라벨을 달아 점수·판정에서 빼고 보고에만 싣는다. 남의 말을 옮긴
# 구간은 고치는 것 자체가 왜곡이기 때문이다.
QUOTE_RX = re.compile(r"[\"“][^\"”]{0,400}[\"”]")

# 면제 조건은 **출처가 특정됐는가**다. 자매 플러그인에서 두 번 틀렸다.
#   1차: 인용 비중으로 갈랐더니 양방향으로 깨졌다 — 비중이 낮으면 앞에 평범한
#        문장만 깔아 슬롭을 통과시킬 수 있었고, 비중이 높으면 짧은 글의 정당한
#        원문 인용이 차단됐다. 비중은 정당성과 무관한 축이다.
#   2차: 귀속 표지로 바꿨는데 목록이 넓어 서사 어휘까지 들어갔다. "그가 말했다."
#        두 단어만 붙이면 임의의 슬롭이 통과했다.
# 그래서 지금은 **무엇의 말인지 지목하는 표지**만 인정한다.
SOURCE_NOUNS = (
    r"(시행령|시행규칙|법률|법령|고시|공고|공문|훈령|조례|지침|약관|규정집|판결문"
    r"|보도자료|안내문|성명서|백서|매뉴얼|제안요청서|과업지시서|입찰공고|평가표"
    r"|요구사항정의서|회의록|산출물|표준|가이드라인"
    r"|조달청|중소벤처기업부|과학기술정보통신부|행정안전부|국세청|발주처|발주기관"
    r"|고객사|담당자|심사위원|평가위원)"
)
# 출처를 지목하는 지시대명사·범용어는 배제한다. "이것에 따르면" 한 어절로 면제가
# 열렸다(실측) — 무엇의 말인지 하나도 특정하지 않는 표지다.
VAGUE = r"(?!(?:이것|그것|저것|여기|거기|이거|그거|이런|그런|자료|내용|정보)에\s*따르면)"
ATTRIBUTION = re.compile(
    r"(https?://"                                  # 인용에 붙은 출처 링크
    rf"|{SOURCE_NOUNS}"                            # 문서·법령·기관 이름
    rf"|{VAGUE}[가-힣A-Za-z0-9]{{2,}}에\s*따르면"   # "X에 따르면" — 출처를 목적어로 요구
    r"|[가-힣A-Za-z0-9]{2,}이?\s*발표한"            # "X가 발표한"
    r"|[가-힣]{2,}\s*(제|절|조|항)\s*[0-9]"          # "제안요청서 3.2절"
    r")"
)

# 인용 부호 앞뒤 이 범위 안에서 표지를 찾는다. 60자는 한국어 도입부 한 문장을
# 넉넉히 덮는 폭이다. 넓혀도 우회에 쓰이지 않는다 — 표지가 기관·법령·URL 이라
# 붙이려면 없는 출처를 지어내야 하고, 그건 문체가 아니라 사실의 문제다.
ATTRIBUTION_WINDOW = 60
# 인용 바로 앞 줄은 거리와 무관하게 후보로 보되, 그 줄의 **끝 40자**까지만 본다.
# 줄 전체를 열었더니 긴 도입부 맨 앞에 기관명 하나만 흘려도 아래 인용이 통째로
# 면제됐다(실측). 우회를 막는 주역은 40 이 아니라 min() 구조다 — 앞줄에서
# 가져오는 범위를 유한하게 자르는 순간 막힌다. 40 이 지키는 건 반대쪽이다:
# 출처가 앞줄에 있고 인용이 같은 줄에서 60자 넘게 들여쓰인 정당한 인용이다.
PREV_LINE_TAIL = 40


def quote_spans(text: str) -> list[tuple[int, int]]:
    """출처가 밝혀진 직접 인용 구간만 돌려준다."""
    out = []
    for m in QUOTE_RX.finditer(text):
        line_start = text.rfind("\n", 0, m.start()) + 1
        prev_line_start = text.rfind("\n", 0, max(line_start - 1, 0)) + 1
        prev_tail = max(prev_line_start, line_start - 1 - PREV_LINE_TAIL)
        begin = min(max(0, m.start() - ATTRIBUTION_WINDOW), prev_tail)
        if ATTRIBUTION.search(text[begin:m.start()]) or \
           ATTRIBUTION.search(text[m.end():m.end() + ATTRIBUTION_WINDOW]):
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


def hangul_ratio(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if "가" <= c <= "힣") / len(letters)


def analyze(text: str, surface: str, kind: str = "text") -> dict:
    cfg = SURFACE_CFG[surface]
    body = extract(text, kind)
    masked = mask(body, MASKS)
    masked_en = mask(body, MASKS_EN)
    wl = whitelist_spans(body)
    qs = quote_spans(body)
    findings, metrics = [], []

    def whitelisted(a: int, b: int) -> bool:
        return any(a >= s and b <= e for s, e in wl)

    def in_quote(a: int, b: int) -> bool:
        return any(a >= s and b <= e for s, e in qs)

    for pid, sev, label, rx, thr, fix in PATTERNS:
        if pid in cfg["off"]:
            continue
        view = masked_en if pid.startswith("E") else masked
        hits = [m for m in rx.finditer(view) if not whitelisted(m.start(), m.end())]
        # C1 은 접속부사 어절("하지만, ")을 제외한다 — 어미가 아니라 부사다.
        if pid == "C1":
            hits = [m for m in hits if eojeol_at(view, m.start()) not in CONJ_ADVERBS]
        # D3 계열은 1인칭 주어가 앞에 오면 훈계가 아니라 화자 자신의 의지다.
        if pid in ("D3", "D3b"):
            hits = [m for m in hits if not FIRST_PERSON_LEAD.search(view[:m.start()])]
        if len(hits) <= thr:
            continue
        counted = hits[thr:]
        # C2 는 2회 이상이면 S1 로 승격(korean-style.md C2 주).
        eff = "S1" if (pid == "C2" and len(counted) >= 2) else sev
        for m in counted:
            findings.append({
                "id": pid, "severity": eff, "label": label,
                "line": line_of(body, m.start()),
                "excerpt": body[max(0, m.start() - 12):m.end() + 12].replace("\n", " ").strip(),
                "fix": fix,
                "quoted": in_quote(m.start(), m.end()),
            })

    # 이모지 한도. **마스킹된 텍스트를 센다** — 원문을 세면 extract() 가 지운
    # 코드·태그 안의 이모지까지 한도에 잡힌다(자매 플러그인에서 실제로 밟았다).
    emojis = [m for m in EMOJI.finditer(masked) if not whitelisted(m.start(), m.end())]
    if len(emojis) > cfg["emoji"]:
        findings.append({
            "id": "C4", "severity": "S1" if cfg["emoji"] == 0 else "S2",
            "label": f"이모지 한도 초과 ({len(emojis)} > {cfg['emoji']})",
            "line": line_of(body, emojis[0].start()),
            "excerpt": "".join(m.group() for m in emojis[:8]),
            "fix": f"{surface} 표면 한도는 {cfg['emoji']}개",
            "quoted": False,
        })

    sents = sentences(masked)

    # C5 같은 종결어미 4연속 — 존댓말 설명형은 '~니다' 3연속이 정상 격식이다.
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
        if worst >= 4:
            findings.append({
                "id": "C5", "severity": "S2", "label": f"같은 종결어미 {worst}연속",
                "line": line_of(body, sents[at][0]),
                "excerpt": sents[at][1][:40],
                "fix": "종결을 섞는다",
                "quoted": False,
            })

    # 장문 부재 — 문장이 충분히 많은데 긴 문장이 하나도 없으면 기계 낭독처럼 읽힌다.
    if cfg["long"] and len(sents) >= cfg["long"]:
        longest = max(visible_len(s) for _, s in sents)
        if longest < LONG_SENT:
            metrics.append({
                "id": "M-long", "line": 1,
                "label": f"장문 부재 — {len(sents)}문장 중 최장 {longest}자 "
                         f"({LONG_SENT}자 넘는 문장이 없다)",
                "detail": ["같은 길이의 문장이 이어지면 기계 낭독처럼 들린다. "
                           "설명이 이어지는 대목 한둘은 붙여서 길게 쓴다."],
                "penalty": 5,
            })

    # 볼드 남발 — 문단마다 굵히면 아무것도 강조되지 않는다.
    if cfg["bold"] and len(sents) >= 10:
        bolds = MD_BOLD.findall(body)
        if len(bolds) > max(8, len(sents) // 4):
            metrics.append({
                "id": "M-bold", "line": 1,
                "label": f"볼드 남발 — {len(bolds)}개 / {len(sents)}문장",
                "detail": [f"예: {', '.join(b[:18] for b in bolds[:4])}"],
                "penalty": 4,
            })

    # 인용 구간 위반은 점수·판정에서 뺀다 — 고칠 수 없는 텍스트로 파이프라인을
    # 세우지 않는다. 보고에는 그대로 실어 원문 확인을 유도한다.
    live = [f for f in findings if not f.get("quoted")]
    quoted = [f for f in findings if f.get("quoted")]

    score = 100
    for f in live:
        score -= PENALTY[f["severity"]]
    for m in metrics:
        score -= m["penalty"]
    score = max(0, score)

    s1 = sum(1 for f in live if f["severity"] == "S1")
    exit_code = 2 if s1 else (1 if score < WARN_BELOW else 0)
    # 면제가 조용한 통과가 되면 안 된다. 검사기는 출처가 진짜인지 모른다 —
    # "출처: 안내문" 여덟 글자로 S1 여섯 건이 판정에서 빠질 수 있다(실측).
    # 그래서 면제를 적용했다는 사실 자체를 사람에게 올린다: exit 0 을 1 로 바닥
    # 처리한다. 1 은 차단이 아니므로 정당한 인용은 그대로 통과한다.
    if quoted and exit_code == 0:
        exit_code = 1

    return {
        "surface": surface, "kind": kind,
        "chars": len(text), "sentences": len(sents),
        "findings": findings, "quoted_findings": len(quoted), "metrics": metrics,
        "score": score,
        "s1": s1,
        "s2": sum(1 for f in live if f["severity"] == "S2"),
        "s3": sum(1 for f in live if f["severity"] == "S3"),
        "verdict": {0: "PASS", 1: "WARN", 2: "FAIL"}[exit_code],
        "exit_code": exit_code,
    }


def render(r: dict, path: str = "") -> str:
    head = (f"판정 {r['verdict']} · 점수 {r['score']}/100 · "
            f"S1 {r['s1']} S2 {r['s2']} S3 {r['s3']}")
    if r["quoted_findings"]:
        head += f" · 인용면제 {r['quoted_findings']}"
    lines = [
        f"korean-style — {path or '입력'} / 표면 {r['surface']} / "
        f"{r['chars']}자 {r['sentences']}문장",
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
# 멀쩡한 글을 통과시키는가, 면제·마스킹이 우회로가 되지 않는가.
#
# 픽스처는 (이름, 표면, 기대 exit, kind, 걸려야 하는 규칙 ID, 본문)이다.
# **ID 를 같이 본다.** exit 코드만 보면 정규식이 죽어도 다른 규칙이 대신 걸려
# 통과한다(자매 플러그인 실측: 죽은 정규식 셋이 그렇게 살아남았다). 빈 튜플은
# "아무것도 걸리면 안 된다"는 뜻이라 오탐 가드가 된다.
# ---------------------------------------------------------------------------

SELFTEST = [
    # --- 신규 규칙 N·E·지표 -------------------------------------------------
    ("N1 명사화 동사", "doc", 1, "text", ("N1",),
     "배포 작업을 수행합니다.\n검증을 실시합니다.\n데이터 이관을 진행합니다.\n"),
    ("N1 오탐 없음", "doc", 0, "text", (),
     "회의를 진행합니다.\n프로젝트를 수행한다.\n임무를 실행했다.\n실험을 실시하려고요.\n"),
    ("N2 ~하기 위해", "doc", 0, "text", ("N2",),
     "조회하기 위해 인덱스를 걸었다.\n중복을 막기 위해서 잠근다.\n검증하기 위한 조건이다.\n"),
    ("N2 임계 안쪽 통과", "doc", 0, "text", (),
     "설정을 확인하기 위해 로그를 켰다.\n나머지는 그대로 둔다.\n"),
    ("N3 ~하도록 하겠습니다", "doc", 2, "text", ("N3",),
     "정리해 드리도록 하겠습니다.\n다시 확인하도록 하겠습니다.\n"),
    ("N3 오탐 없음", "doc", 0, "text", (),
     "덮어쓰지 않도록 잠금을 건다.\n중복되지 않도록 키를 나눈다.\n"),
    ("N4 딱딱한 한자어", "doc", 1, "text", ("N4",),
     "상기 내용을 확인한다.\n금번 배포분이다.\n두 값이 상이하다.\n제반 사항을 챙긴다.\n"),
    ("N4 오탐 없음", "doc", 0, "text", (),
     "지난 일을 상기했다.\n기록을 다시 떠올린다.\n"),
    ("N5 '해당' 반복", "doc", 0, "text", ("N5",),
     "해당 파일을 연다.\n해당 설정을 지운다.\n해당 값을 비교한다.\n해당 로그를 남긴다.\n"
     "해당 절차를 반복한다.\n"),
    ("N5 임계 안쪽 통과", "doc", 0, "text", (),
     "해당 파일을 연다.\n해당 설정을 지운다.\n해당 값을 비교한다.\n"),
    ("E1 영문 AI 상투어", "doc", 0, "text", ("E1",),
     "Let us delve into the details.\nIt is a testament to the design.\n"),
    ("E2 영문 상투어 반복", "doc", 0, "text", ("E2",),
     "A comprehensive and robust solution.\nA comprehensive review of the robust pipeline.\n"
     "We leverage a holistic and cutting-edge approach here.\n"),
    ("E3 영문 부정 대구", "doc", 0, "text", ("E3",),
     "It's not a tool, it's a platform.\nNot only fast but also cheap.\n"),
    # 한국어 마스크는 영어를 통째로 지운다 — 영문 규칙이 별도 뷰를 쓰는지 고정한다.
    ("영문 규칙은 한국어 마스크에 지워지지 않는다", "doc", 0, "text", ("E1",),
     "이 설계는 tapestry 라는 표현을 씁니다.\n다른 문장은 멀쩡합니다.\n"),
    ("E 규칙도 코드펜스 안은 안 본다", "doc", 0, "md", (),
     "설정을 바꾼다.\n\n```\nWe delve into the tapestry of myriad options.\n```\n"),
    # 장문 부재 — 20문장이 전부 짧으면 기계 낭독처럼 읽힌다. 종결어미는 섞어서
    # C5(같은 종결 4연속)와 축이 겹치지 않게 둔다 — 여기서 보려는 건 길이뿐이다.
    ("M-long 장문 부재", "doc", 0, "text", ("M-long",),
     "".join(f"항목 {i}을 {v}.\n" for i, v in
             zip(range(1, 21), ["확인한다", "본다", "적었다", "지웠어요"] * 5))),
    ("M-long 장문이 있으면 통과", "doc", 0, "text", (),
     "".join(f"항목 {i}을 {v}.\n" for i, v in
             zip(range(1, 20), ["확인한다", "본다", "적었다", "지웠어요"] * 5)) +
     "이 단계에서 확인할 것은 잠금이 제대로 걸렸는지 그리고 재시도 큐가 비었는지 "
     "그리고 실패한 건이 다음 배치로 제때 넘어갔는지 이렇게 세 가지이고 셋 중에 "
     "하나라도 어긋나 있으면 그 자리에서 롤백하고 다시 처음부터 돌린다.\n"),

    # --- 표면별 완화 --------------------------------------------------------
    ("proposal 격식 종결 연속 통과", "proposal", 0, "text", (),
     "본 사업의 목표는 민원 처리 시간 단축입니다.\n현재 평균 처리 시간은 4일입니다.\n"
     "목표는 1일입니다.\n측정은 접수 시각과 완료 시각의 차이로 합니다.\n"),
    ("proposal 이모지 금지", "proposal", 2, "text", ("C4",),
     "본 사업의 목표는 처리 시간 단축입니다 🚀\n측정 기준은 접수 시각입니다 ✅\n"),
    ("doc 절차 3단 통과", "doc", 0, "text", (),
     "먼저 스키마를 만든다.\n다음으로 데이터를 옮긴다.\n마지막으로 인덱스를 건다.\n"),
    ("chat 3단은 잡는다", "chat", 0, "text", ("C6",),
     "먼저 원인을 봤다.\n다음으로 로그를 봤다.\n마지막으로 설정을 고쳤다.\n"),
    ("comment 조각 문장 통과", "comment", 0, "text", (),
     "// 잠금이 없으면 두 배치가 같은 행을 건드린다.\n"),

    # --- 추출 (kind) --------------------------------------------------------
    ("html 태그는 검사 대상이 아니다", "proposal", 0, "html", (),
     "<section class=\"delve\"><p>처리 시간을 하루로 줄입니다.</p></section>\n"),
    ("html 본문은 검사한다", "proposal", 2, "html", ("A1",),
     "<p>본 사업에 대해 함께 알아볼까요.</p>\n"),
    ("md 코드펜스는 검사 대상이 아니다", "doc", 0, "md", (),
     "설정을 바꾼다.\n\n```\n제도에 대해 함께 알아볼까요. 결론적으로 그렇습니다.\n```\n"),
    ("md 인라인 코드는 은신처가 아니다", "doc", 2, "md", ("A1",),
     "`제도에 대해 함께 알아볼까요` 를 실행한다.\n"),
    ("code 주석만 검사한다", "comment", 2, "code", ("A1",),
     "const delve = 1; // 이 값에 대해 알아볼까요\nconst x = '결론적으로';\n"),
    ("code 문자열은 검사하지 않는다", "comment", 0, "code", (),
     "const s = '제도에 대해 함께 알아볼까요';\nconst t = '결론적으로 그렇습니다';\n"),

    # --- 인용 면제 ----------------------------------------------------------
    ("귀속 없는 따옴표는 면제 안 됨", "doc", 2, "text", ("A1", "D1"),
     '"제도에 대해 함께 알아볼까요. 결론적으로 시사하는 바가 큽니다."\n'),
    ("출처 특정 인용은 면제(최소 WARN)", "doc", 1, "text", ("T3",),
     "제안요청서 원문은 이렇습니다.\n"
     '"신고 의무는 신청인 본인에게 있어서 대행 여부와 무관하게 판단되어진다."\n'),
    ("지시대명사 우회 차단", "doc", 2, "text", ("A1", "D1"),
     '이것에 따르면 "제도에 대해 함께 알아볼까요. 결론적으로 그렇습니다."\n'),
    ("인용 밖 위반은 그대로 차단", "doc", 2, "text", ("D1", "D2"),
     "제안요청서 원문은 이렇습니다.\n"
     '"신고는 도착 즉시 이루어져야 한다."\n'
     "결론적으로 이 변화는 시사하는 바가 큽니다.\n"),

    # --- 상속 규칙 오탐 가드 (자매 플러그인에서 실측으로 확정된 것들) ---------
    ("T1 관한·어간 우연 일치 오탐 없음", "doc", 0, "text", (),
     "개인정보 보호에 관한 법률 조문이다.\n반대한 사람은 없었다.\n상대한 업체가 셋이다.\n"),
    ("T3 어간 분리 오탐 없음", "doc", 0, "text", (),
     "집에 보여 준 서류다.\n잊혀 가는 관행이다.\n"),
    ("T5 어절 첫 글자 오탐 없음", "doc", 0, "text", (),
     "이 지표에 의해 진도를 판단한다.\n규정에 의해 된장 수입이 늘었다.\n"),
    ("C1 연결어미 뒤 쉼표 검출", "doc", 2, "text", ("C1",),
     "기술은 빠르게 발전하지만, 조직은 더디다.\n"),
    ("C1 접속부사 오탐 없음", "doc", 0, "text", (),
     "기한이 바뀐다.\n하지만, 관행은 그대로다.\n그런데, 책임은 본인에게 남는다.\n"),
    # 실측 오탐 — 명사 '이해도'의 도를 연결어미 '해도'로 읽었다.
    ("C1 명사+도 오탐 없음", "doc", 0, "text", (),
     "섹션 유형(사업이해도, 기술방안, 수행체계)으로 나눈다.\n"
     "그 견해도, 반대 의견도 함께 적었다.\n"),
    # 좁힘이 미탐을 만들지 않는지 양방향으로 고정한다. '화'·'분'을 제외 목록에
    # 넣으면 아래 셋이 통째로 빠진다 — 그래서 넣지 않았다는 결정을 여기 박아 둔다.
    ("C1 연결어미 해도는 그대로 잡는다", "doc", 2, "text", ("C1",),
     "몇 번을 확인해도, 결과는 같다.\n설정을 강화해도, 결과는 같다.\n"
     "예산이 충분해도, 일정은 그대로다.\n"),
    ("N3 하자·하시는 잡지 않는다", "doc", 0, "text", (),
     "늦지 않도록 하자.\n빠뜨리지 않도록 하시죠.\n중복되지 않도록 한다.\n"),
    # T1 은 존재가 아니라 반복이 신호다 — 한 번은 넘어간다.
    ("T1 한 번은 통과", "doc", 0, "text", (),
     "이 절은 인증 흐름에 대한 설명이다.\n나머지는 코드에 적었다.\n"),
    ("T1 반복은 잡는다", "doc", 0, "text", ("T1",),
     "인증에 대한 설명이다.\n권한에 대한 설명은 뒤에 있다.\n세션에 대해 다시 적었다.\n"),
    ("C3 명사 나열 통과", "doc", 0, "text", (),
     "여권, 비자, 계약서를 챙긴다.\n하노이, 다낭, 호치민은 절차가 다르다.\n"),
    ("C2 다름 아니라 통과", "doc", 0, "text", (),
     "다름 아니라 어제 겪은 일이다.\n다름 아니라 기한 얘기다.\n"),
    ("T2 존재동사 오탐 없음", "doc", 0, "text", (),
     "영수증은 가방에 있어.\n다른 해석의 여지는 없다.\n"),
    ("D2 구체 명사 오탐 없음", "doc", 0, "text", (),
     "주목받는 기업은 세 곳이다.\n올해 주목받는 품목은 전자부품이다.\n"
     "높게 평가받는 대행사를 골랐다.\n"),
    ("D2 추상어 뒤 관형형·종결형", "doc", 2, "text", ("D2",),
     "주목받는 변화다.\n주목되는 대목은 기한이다.\n이번 개정이 주목된다.\n"),
    ("D3 의지·전망 오탐 없음", "doc", 0, "text", (),
     "내가 가야 할 것입니다.\n언젠가는 바뀌어야 할 것입니다.\n"
     "나도 서류를 챙겨야 할 것입니다.\n내가 해야 할 일이 많다.\n"),
    ("D3 청자 높임은 훈계다", "doc", 2, "text", ("D3",),
     "서두르셔야 할 것입니다.\n조심하셔야 할 것입니다.\n"),
    # 화행으로만 갈리는 갈래는 차단하지 않는다. 리포트·설계 문서는 전망을 쓰는
    # 장르라 S1 으로 두면 정상 문장 7종이 통째로 막혔다(실측).
    ("D3b 전망은 차단하지 않는다", "doc", 0, "text", ("D3b",),
     "내년에는 시스템을 바꿔야 할 것이다.\n환율이 더 오르면 단가를 조정해야 할 것이다.\n"),
    ("D3b 조건절 귀결도 차단하지 않는다", "doc", 0, "text", ("D3b",),
     "기한을 넘기면 과태료를 내야 할 것이다.\n결국 시장이 답을 내야 할 것이다.\n"),
    # 반대쪽 — 오탐 위험이 없는 갈래는 그대로 차단한다.
    ("D3 고정 관용구는 차단한다", "doc", 2, "text", ("D3",),
     "확인할 필요가 있습니다.\n점검하는 것이 중요합니다.\n이 점을 명심해야 한다.\n"),
    ("1인칭 면제가 다른 규칙을 가리지 않는다", "doc", 2, "text", ("D1",),
     "나도 이 제도에 대해 정리해야 할 것입니다.\n"
     "저도 결론적으로 다시 봐야 할 것입니다.\n"),
    ("T6 부사+의 오탐 없음", "doc", 0, "text", (),
     "앞으로의 변화를 적었다.\n향후의 계획은 따로 낸다.\n"),

    # --- 종합 ---------------------------------------------------------------
    ("전형적 AI 문서 검출", "doc", 2, "text",
     ("T3", "A1", "A2", "D1", "D2", "D6", "N1", "N3"),
     "본 문서에 대해 함께 알아볼까요.\n"
     "다양한 기능을 효과적으로 제공하기 위해 설계되어졌습니다.\n"
     "검증 작업을 수행하도록 하겠습니다.\n"
     "결론적으로 이 구조는 시사하는 바가 큽니다.\n"
     "도움이 되셨길 바랍니다.\n"),
    ("사람이 쓴 기술 문서 통과", "doc", 0, "text", (),
     "배치가 두 번 돌면 같은 행을 두 번 건드린다.\n"
     "그래서 시작할 때 행 잠금을 건다.\n"
     "잠금은 배치 ID로 잡고 끝나면 푼다.\n"
     "중간에 죽으면 잠금이 남는데 이건 10분 지나면 자동으로 풀린다.\n"
     "10분은 가장 느린 배치가 7분쯤 걸려서 잡은 값이다.\n"),
    ("자기 보고 상투구 검출", "chat", 1, "text", ("A5",),
     "요청하신 작업을 성공적으로 완료하였습니다.\n"
     "더 궁금한 점이 있으시면 언제든지 말씀해 주세요.\n"),
    ("담백한 보고 통과", "chat", 0, "text", (),
     "끝났습니다.\n테스트 12개 중 12개 통과했습니다.\n"
     "설정 파일 두 개를 바꿨고, 나머지는 그대로입니다.\n"),
    ("HITL 질문 통과", "hitl", 0, "text", (),
     "인증을 세션으로 할까요, 토큰으로 할까요?\n"
     "세션은 서버가 상태를 들고 있어서 로그아웃을 즉시 끊을 수 있습니다.\n"
     "토큰은 서버가 가볍지만 만료 전에는 강제로 끊기 어렵습니다.\n"),
    ("HITL 안내형 도입 검출", "hitl", 2, "text", ("A1",),
     "인증 방식에 대해 함께 알아볼까요?\n"),
]


def selftest() -> int:
    failed = 0
    for name, surface, want, kind, want_ids, text in SELFTEST:
        got = analyze(unicodedata.normalize("NFC", text), surface, kind)
        seen = {f["id"] for f in got["findings"] if not f.get("quoted")} \
            | {m["id"] for m in got["metrics"]}
        quoted_ids = {f["id"] for f in got["findings"] if f.get("quoted")}
        missing = set(want_ids) - (seen | quoted_ids)
        # 빈 기대 = 오탐 가드. 하나라도 걸리면 실패다.
        extra = seen if not want_ids else set()
        ok = got["exit_code"] == want and not missing and not extra
        failed += 0 if ok else 1
        why = []
        if got["exit_code"] != want:
            why.append(f"exit={got['exit_code']}≠{want}")
        if missing:
            why.append("미검출=" + ",".join(sorted(missing)))
        if extra:
            why.append("오탐=" + ",".join(sorted(extra)))
        note = ("  ← " + " / ".join(why)) if why else ""
        ids = ",".join(sorted(seen | quoted_ids)) or "-"
        print(f"[{'PASS' if ok else 'FAIL'}] {name} ({surface}/{kind}) "
              f"점수={got['score']} 탐지={ids}{note}")
    print(f"\n{len(SELFTEST) - failed}/{len(SELFTEST)} 통과")
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="한국어 AI 티 결정적 검사기")
    p.add_argument("path", nargs="?", help="검사할 파일 (- 는 표준입력)")
    p.add_argument("--surface", choices=SURFACES,
                   help="표면 — 표면별로 임계와 끄는 규칙이 다르다")
    p.add_argument("--kind", choices=KINDS, default="auto",
                   help="입력 종류. auto 는 확장자로 고른다(표준입력은 text)")
    p.add_argument("--json", action="store_true", help="구조화 출력")
    p.add_argument("--min-hangul", type=float, default=0.0,
                   help="한글 비율이 이 값 미만이면 검사하지 않고 0 을 돌려준다")
    p.add_argument("--selftest", action="store_true", help="내장 픽스처로 규칙 자가 검증")
    args = p.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.path or not args.surface:
        p.error("path 와 --surface 가 필요하다 (규칙 검증만 할 때는 --selftest)")

    try:
        raw = sys.stdin.read() if args.path == "-" else open(args.path, encoding="utf-8").read()
    except OSError as e:
        print(f"korean-style: 입력을 읽지 못했다 — {e}", file=sys.stderr)
        return 3

    text = unicodedata.normalize("NFC", raw)
    if not text.strip():
        return 0

    kind = args.kind
    if kind == "auto":
        kind = kind_of(args.path) if args.path != "-" else "text"

    if args.min_hangul and hangul_ratio(extract(text, kind)) < args.min_hangul:
        return 0

    try:
        result = analyze(text, args.surface, kind)
    except Exception as e:  # 게이트가 죽어서 작업을 막지는 않게 한다
        print(f"korean-style: 분석 실패 — {e}", file=sys.stderr)
        return 3

    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json
          else render(result, "" if args.path == "-" else args.path))
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
