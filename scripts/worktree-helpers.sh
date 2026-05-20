#!/usr/bin/env bash
# ASTRA worktree helper functions.
#
# Source this file from skills/scripts that need to manage isolated work
# branches in `.astra-worktrees/`. Functions are namespaced with `astra_`
# and intended to be safe to call multiple times.
#
# Policy:
#   - Shared branches (main, master, staging, dev) live in the MAIN worktree.
#   - All other branches (feat/*, fix/*, docs/*, refactor/*, chore/*, etc.)
#     are checked out into `.astra-worktrees/<slug>/` under the repo root.
#   - Worktrees are ephemeral: created on demand, removed when the task ends.
#
# Usage:
#   source "$CLAUDE_PLUGIN_ROOT/scripts/worktree-helpers.sh"
#   astra_ensure_main_worktree || exit 1
#   wt_path=$(astra_create_worktree "feat/foo-bar" "origin/dev") || exit 1
#   ...
#   astra_remove_worktree "feat/foo-bar"

# --- branch classification -------------------------------------------------

astra_is_shared_branch() {
  case "$1" in
    main|master|staging|dev) return 0 ;;
    *) return 1 ;;
  esac
}

astra_branch_to_slug() {
  printf '%s' "$1" | tr '/' '-'
}

# --- worktree location -----------------------------------------------------

# Echo the absolute path of the MAIN worktree (the original clone, not any
# linked worktree). Works correctly even when called from inside a linked
# worktree because git records the main worktree as the common-dir parent.
astra_main_worktree_root() {
  local common_dir
  common_dir=$(git rev-parse --git-common-dir 2>/dev/null) || return 1
  # `--git-common-dir` returns the .git directory of the main worktree.
  # The repo root is its parent (unless it's a bare repo, which we don't
  # support here — ASTRA target projects always have a working tree).
  (cd "$common_dir/.." && pwd)
}

astra_worktree_path() {
  local slug="$1"
  local root
  root=$(astra_main_worktree_root) || return 1
  printf '%s/.astra-worktrees/%s' "$root" "$slug"
}

# --- worktree introspection ------------------------------------------------

# Return 0 if we're currently inside a linked worktree (NOT the main one).
# Detection uses git metadata, not path matching — robust against custom
# worktree locations.
astra_is_isolated_worktree() {
  local git_dir common_dir
  git_dir=$(git rev-parse --git-dir 2>/dev/null) || return 1
  common_dir=$(git rev-parse --git-common-dir 2>/dev/null) || return 1
  # Normalize both to absolute paths for comparison.
  git_dir=$(cd "$git_dir" && pwd) 2>/dev/null || git_dir=$(realpath "$git_dir" 2>/dev/null)
  common_dir=$(cd "$common_dir" && pwd) 2>/dev/null || common_dir=$(realpath "$common_dir" 2>/dev/null)
  [ "$git_dir" != "$common_dir" ]
}

# Guard for skills that must run from the main worktree (e.g. /service-planner,
# /test-run, /pr-merge entry). Emits a Korean diagnostic and returns 1 when
# called from an isolated worktree.
astra_ensure_main_worktree() {
  if astra_is_isolated_worktree; then
    local main_root
    main_root=$(astra_main_worktree_root) || main_root="(unknown)"
    echo "ERROR: 이 명령은 메인 worktree에서만 실행할 수 있습니다." >&2
    echo "       현재 위치는 격리 worktree(.astra-worktrees/)입니다." >&2
    echo "       메인 worktree로 이동 후 다시 실행하세요:" >&2
    echo "         cd \"$main_root\"" >&2
    return 1
  fi
  return 0
}

# --- worktree lifecycle ----------------------------------------------------

# Remove stale worktree metadata for directories that no longer exist on disk.
# Safe to call anytime — never deletes live worktrees.
astra_prune_worktrees() {
  git worktree prune 2>/dev/null || true
}

# Ensure the main worktree's .gitignore contains `.astra-worktrees/`. Idempotent.
# Called before any worktree is created so that worktree contents never appear
# as untracked files in the main worktree (which would corrupt subsequent
# `git stash --include-untracked` invocations).
astra_ensure_gitignore_entry() {
  local root pattern=".astra-worktrees/"
  root=$(astra_main_worktree_root) || return 1
  local gitignore="$root/.gitignore"
  if [ -f "$gitignore" ]; then
    grep -Fxq "$pattern" "$gitignore" && return 0
    printf '\n# ASTRA isolated worktrees (managed by /pr-merge)\n%s\n' "$pattern" >> "$gitignore"
  else
    printf '# ASTRA isolated worktrees (managed by /pr-merge)\n%s\n' "$pattern" > "$gitignore"
  fi
  return 0
}

# Resolve a non-conflicting (branch, slug) pair. A pair is FREE when:
#   - the local branch does NOT yet exist (no `refs/heads/<branch>`), AND
#   - `.astra-worktrees/<slug>` is not a registered worktree, AND
#   - `.astra-worktrees/<slug>` does not exist as a directory.
# Suffixes `-2`, `-3`, ... are appended to BOTH branch and slug in lock-step
# until a free pair is found. Echoes `<branch>\t<slug>` (tab-separated).
astra_resolve_branch_and_slug() {
  local base_branch="$1"
  local root
  root=$(astra_main_worktree_root) || return 1
  astra_prune_worktrees

  local branch="$base_branch"
  local slug
  slug=$(astra_branch_to_slug "$branch")
  local n=2
  while true; do
    local path="$root/.astra-worktrees/$slug"
    local registered
    registered=$(git worktree list --porcelain 2>/dev/null | awk -v p="$path" '
      /^worktree / { wt=$2 }
      $0=="" { if (wt==p) { print "yes"; exit } }
      END { if (wt==p) print "yes" }
    ')
    if ! git show-ref --verify --quiet "refs/heads/$branch" \
       && [ -z "$registered" ] \
       && [ ! -e "$path" ]; then
      printf '%s\t%s' "$branch" "$slug"
      return 0
    fi
    branch="${base_branch}-${n}"
    slug=$(astra_branch_to_slug "$branch")
    n=$((n + 1))
    if [ "$n" -gt 50 ]; then
      echo "ERROR: 브랜치/슬러그 충돌이 너무 많습니다 ($base_branch)" >&2
      return 1
    fi
  done
}

# Create an isolated worktree for a NEW branch based on `<base-ref>`.
#   astra_create_worktree_new <branch-name> <base-ref>
#
# Echoes `<resolved-branch>\t<worktree-path>` (tab-separated) on success. The
# caller MUST capture the resolved branch — when conflicts force a suffix,
# the actual branch may differ from the requested one (e.g. `feat/x-2`).
#
# Usage:
#   IFS=$'\t' read -r BRANCH WT_PATH < <(astra_create_worktree_new "feat/x" "origin/dev") || exit 1
astra_create_worktree_new() {
  local requested_branch="$1"
  local base_ref="$2"
  if [ -z "$requested_branch" ] || [ -z "$base_ref" ]; then
    echo "ERROR: astra_create_worktree_new requires <branch> <base-ref>" >&2
    return 2
  fi

  astra_ensure_gitignore_entry || return 1

  local resolved branch slug wt_path
  resolved=$(astra_resolve_branch_and_slug "$requested_branch") || return 1
  branch="${resolved%%$'\t'*}"
  slug="${resolved##*$'\t'}"
  wt_path=$(astra_worktree_path "$slug") || return 1

  mkdir -p "$(dirname "$wt_path")"
  if ! git worktree add -b "$branch" "$wt_path" "$base_ref" >&2; then
    echo "ERROR: worktree 생성 실패: $branch (base=$base_ref)" >&2
    return 1
  fi
  printf '%s\t%s' "$branch" "$wt_path"
}

# Attach a worktree for an EXISTING branch (local or remote-tracking). Slug
# directory collisions get `-2`/`-3` suffix (branch is fixed). Echoes
# `<branch>\t<worktree-path>` for consistency with `astra_create_worktree_new`.
astra_create_worktree_existing() {
  local branch="$1"
  if [ -z "$branch" ]; then
    echo "ERROR: astra_create_worktree_existing requires <branch>" >&2
    return 2
  fi

  astra_ensure_gitignore_entry || return 1
  astra_prune_worktrees

  local base_slug="$(astra_branch_to_slug "$branch")"
  local root slug n=2
  root=$(astra_main_worktree_root) || return 1
  slug="$base_slug"
  while true; do
    local path="$root/.astra-worktrees/$slug"
    if [ ! -e "$path" ]; then
      break
    fi
    slug="${base_slug}-${n}"
    n=$((n + 1))
    [ "$n" -gt 50 ] && { echo "ERROR: 슬러그 충돌이 너무 많습니다 ($base_slug)" >&2; return 1; }
  done
  local wt_path
  wt_path=$(astra_worktree_path "$slug") || return 1

  mkdir -p "$(dirname "$wt_path")"
  if ! git worktree add "$wt_path" "$branch" >&2; then
    echo "ERROR: worktree attach 실패: $branch" >&2
    return 1
  fi
  printf '%s\t%s' "$branch" "$wt_path"
}

# Remove an isolated worktree by branch slug. The associated branch is NOT
# deleted here — call `git branch -d <branch>` separately after verifying
# the branch is fully merged.
astra_remove_worktree() {
  local branch="$1"
  if [ -z "$branch" ]; then
    echo "ERROR: astra_remove_worktree requires <branch>" >&2
    return 2
  fi
  local slug wt_path
  slug=$(astra_branch_to_slug "$branch")
  wt_path=$(astra_worktree_path "$slug") || return 1

  if [ -d "$wt_path" ]; then
    git worktree remove "$wt_path" 2>/dev/null || git worktree remove --force "$wt_path" 2>/dev/null || {
      echo "WARN: worktree 제거 실패: $wt_path (수동 정리 필요)" >&2
      return 1
    }
  fi
  astra_prune_worktrees
  return 0
}
