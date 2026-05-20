#!/usr/bin/env bash
# inject-feature-dev-cwd.sh
# UserPromptSubmit hook: When user invokes /feature-dev from inside an ASTRA
# sprint worktree, inject cwd-anchored sprint paths into the LLM context so
# the external feature-dev plugin (which has no concept of "sprint") does
# not fall back to the main worktree where sprint files do not exist yet.
#
# Background: Sprint progress/prompt-map/retrospective files are written by
# /sprint-init INSIDE the linked worktree (.astra-worktrees/sprint-N-name/).
# They are unstaged at that point, so they only exist in that worktree's
# working directory — never visible from the main worktree.
#
# Without this hook the LLM frequently searches docs/sprints/ from the main
# worktree (or git root) and reports "sprint not found", because that's
# where it has been pre-conditioned to look by the rest of the conversation.
#
# Non-blocking — emits context only; exits 0 unconditionally.

INPUT=$(cat)
PROMPT=$(echo "$INPUT" | jq -r '.prompt // ""' 2>/dev/null)

# Detect /feature-dev invocation. Matches both plain and namespaced forms:
#   /feature-dev "..."
#   /feature-dev:feature-dev "..."
case "$PROMPT" in
  "/feature-dev"|"/feature-dev "*|"/feature-dev:"*)
    : # match — fall through
    ;;
  *)
    exit 0
    ;;
esac

# Only inject context when invoked from inside a sprint worktree.
CWD=$(pwd)
case "$CWD" in
  */.astra-worktrees/sprint-*)
    SPRINT_SLUG=$(basename "$CWD")
    SPRINT_DIR=""
    if [ -d "$CWD/docs/sprints/$SPRINT_SLUG" ]; then
      SPRINT_DIR="$CWD/docs/sprints/$SPRINT_SLUG"
    else
      # The on-disk sprint directory name may not match the worktree slug
      # exactly (e.g. worktree slug strips the feat/ prefix). Fall back to
      # the most recently modified sprint-* directory under this worktree.
      CAND=$(ls -td "$CWD"/docs/sprints/sprint-* 2>/dev/null | head -1)
      [ -n "$CAND" ] && SPRINT_DIR="$CAND"
    fi

    cat <<EOF
[ASTRA cwd guard] /feature-dev invoked from a sprint worktree.

Current working directory: $CWD
This is a linked git worktree, NOT the main worktree.

Sprint files (progress.md, prompt-map.md, retrospective.md) live ONLY here:
  $SPRINT_DIR

These files are uncommitted at this stage, so they are NOT visible from
the main worktree. Anchor every sprint-related path to the cwd above.
Do NOT search the main worktree or git root for sprint files — they do
not exist there.

Blueprint files (docs/blueprints/...) are dev-committed and visible in
both worktrees; either path resolves the same content.
EOF
    ;;
esac

exit 0
