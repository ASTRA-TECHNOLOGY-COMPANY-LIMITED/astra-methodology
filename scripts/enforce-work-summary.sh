#!/bin/bash
# enforce-work-summary.sh
# Stop hook: 작업 완료 후 사용자의 언어로 작업 설명을 반드시 제공하도록 강제
#
# Stop 훅은 Claude가 응답을 마칠 때 실행됨
# - decision: "block" + reason → Claude가 reason을 보고 응답을 계속
# - exit 0 (출력 없음) → Claude가 정상적으로 종료
# - stop_hook_active: true → 이전 Stop 훅에 의해 이미 계속된 상태 (무한루프 방지)

INPUT=$(cat)

# 무한루프 방지: 이미 Stop 훅에 의해 계속된 상태면 종료
STOP_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
if [ "$STOP_ACTIVE" = "true" ]; then
  exit 0
fi

# Claude의 마지막 응답 텍스트
MESSAGE=$(echo "$INPUT" | jq -r '.last_assistant_message // ""')

# 빈 응답이면 스킵 (도구 출력만 있는 경우)
if [ -z "$MESSAGE" ]; then
  exit 0
fi

# 단어 수 계산 (짧은 응답은 요약 불필요)
WORD_COUNT=$(echo "$MESSAGE" | wc -w | tr -d ' ')
if [ "$WORD_COUNT" -lt 80 ]; then
  exit 0
fi

# 질문이나 확인 요청만 있는 응답은 스킵
if echo "$MESSAGE" | tail -5 | grep -qE '(\?$|확인해|알려주|선택해|어떤 것|어떻게|원하시|괜찮으|할까요|드릴까)'; then
  exit 0
fi

# 이미 작업 요약/설명이 있는지 확인 (한국어 + 영어 + 일본어 마커)
MESSAGE_LOWER=$(echo "$MESSAGE" | tr '[:upper:]' '[:lower:]')
if echo "$MESSAGE" | grep -qE '(완료했습니다|수행했습니다|작업 요약|작업 설명|변경 사항|수정 사항|작업 내용|처리했습니다|적용했습니다|구현했습니다|생성했습니다|업데이트했습니다|추가했습니다|삭제했습니다|리팩토링했습니다|수정했습니다)'; then
  exit 0
fi
if echo "$MESSAGE_LOWER" | grep -qE "(summary|here['''']s what|completed|changes made|what i did|in summary|to summarize|accomplished|implemented|created|updated|modified|refactored)"; then
  exit 0
fi
if echo "$MESSAGE" | grep -qE '(完了しました|変更内容|作業内容|実装しました|更新しました|修正しました)'; then
  exit 0
fi

# 작업 설명이 없으면 블록하고 이유를 전달
jq -n '{
  "decision": "block",
  "reason": "[ASTRA Stop Hook] 작업이 완료된 것으로 보이지만 작업 설명이 누락되었습니다. 사용자의 언어로 수행한 작업 내용을 간결하게 설명해주세요. (예: 어떤 파일을 수정했는지, 무엇을 변경했는지, 주의사항이 있는지)"
}' || exit 0
exit 0
