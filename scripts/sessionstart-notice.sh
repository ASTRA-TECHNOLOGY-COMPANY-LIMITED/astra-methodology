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
