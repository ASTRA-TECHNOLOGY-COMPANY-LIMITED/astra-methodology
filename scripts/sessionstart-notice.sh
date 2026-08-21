#!/bin/bash
# sessionstart-notice.sh — consolidated SessionStart hook for the ASTRA plugin.
#
# Replaces four separate SessionStart echo hooks (banner + three env-var
# warnings) that printed on every session. The banner still prints every
# session; the env-var status lines are throttled to at most once per 24h
# via a marker file, and only *missing* env vars produce output (a set var
# prints nothing — the old "enabled" noise lines are dropped entirely).
#
# Always exits 0 so it can never block session start.

# Banner — always shown.
echo '🌟 ASTRA methodology is active. Run /astra-guide for a quick reference.'

# Korean style rules — always shown, deliberately.
#
# Files go through the PostToolUse gate (check-korean-style.sh), but the two
# surfaces that matter most to the user never become files: the questions we ask
# and the answers we give. No hook can see those, so the rules have to be in
# context from the first turn. Kept to a dozen lines for that reason.
cat <<'STYLE'
[한국어 문체] 이 플러그인이 쓰는 모든 한국어 — 문서·주석·커밋 메시지·질문·답변 — 는
사람이 쓴 것처럼 읽혀야 한다. 기준: 옆자리 동료에게 소리 내어 말했을 때 어색하면 고친다.
  - 연결어미 뒤 쉼표를 찍지 않는다: "발전하지만, 조직은" → "발전하지만 조직은"
  - ~에 대해 / ~를 통해 / ~하기 위해 → 조사로 직결하거나 ~로 · ~하려고
  - "삭제 작업을 수행합니다" → "삭제합니다" (동사를 명사에 가두지 않는다)
  - 결론적으로 · 함께 알아볼까요 · 도움이 되셨길 · 성공적으로 완료하였습니다 · 더 궁금한
    점이 있으시면 — 전부 쓰지 않는다. 답은 첫 문장에서 말하고 끝나면 "끝났습니다".
  - 훈계하지 않는다: "확인할 필요가 있습니다" → "확인하자"
  - 질문(HITL)은 선택지가 무엇을 바꾸는지 한 줄씩 붙인다. 답은 결론부터.
파일은 PostToolUse 훅이 자동 검사해 지적을 돌려준다. 규칙과 검사기는
${CLAUDE_PLUGIN_ROOT}/skills/korean-style/ — 규칙을 고칠 땐 --selftest 를 돌린다.
STYLE

MARKER_DIR="$HOME/.claude/.astra-hooks"
MARKER="$MARKER_DIR/sessionstart-notice"

# Show the env-var status block only when the marker is absent or older than 24h.
show_status=0
if [ ! -f "$MARKER" ]; then
  show_status=1
else
  # find -mmin +1440 => modified more than 24h (1440 min) ago
  if [ -n "$(find "$MARKER" -mmin +1440 2>/dev/null)" ]; then
    show_status=1
  fi
fi

if [ "$show_status" -eq 1 ]; then
  [ -z "$GOOGLE_API_KEY" ] && echo '[ASTRA] GOOGLE_API_KEY is not set. Set this environment variable to use the fect-image (Gemini) MCP.'
  [ -z "$OPENAI_API_KEY" ] && echo '[ASTRA] OPENAI_API_KEY is not set. Set this environment variable to use the fect-gpt-image MCP.'
  mkdir -p "$MARKER_DIR" 2>/dev/null
  touch "$MARKER" 2>/dev/null
fi

exit 0
