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
#   PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
#   if [ -z "$PLUGIN_ROOT" ] || [ ! -f "$PLUGIN_ROOT/scripts/worktree-helpers.sh" ]; then
#     echo "ERROR: CLAUDE_PLUGIN_ROOT not found." >&2; exit 1
#   fi
#   source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"
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
  # When `.git` is a file (submodule worktree), normalize to the actual gitdir directory path.
  # Comparing the file path as-is would never match the directory `common_dir`, causing false positives.
  if [ -f "$git_dir" ]; then
    git_dir=$(git rev-parse --absolute-git-dir 2>/dev/null) || return 1
  fi
  # Normalize both to absolute paths for comparison.
  git_dir=$(cd "$git_dir" && pwd 2>/dev/null) || git_dir=$(realpath "$git_dir" 2>/dev/null)
  common_dir=$(cd "$common_dir" && pwd 2>/dev/null) || common_dir=$(realpath "$common_dir" 2>/dev/null)
  [ "$git_dir" != "$common_dir" ]
}

# Guard for skills that must run from the main worktree (e.g. /service-planner,
# /test-run, /pr-merge entry). Emits a diagnostic and returns 1 when
# called from an isolated worktree.
astra_ensure_main_worktree() {
  if astra_is_isolated_worktree; then
    local main_root
    main_root=$(astra_main_worktree_root) || main_root="(unknown)"
    echo "ERROR: This command can only run from the main worktree." >&2
    echo "       Current location is an isolated worktree (.astra-worktrees/)." >&2
    echo "       Switch to the main worktree and try again:" >&2
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
      echo "ERROR: Too many branch/slug collisions ($base_branch)" >&2
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
    echo "ERROR: worktree creation failed: $branch (base=$base_ref)" >&2
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

  # If the branch is already checked out in another worktree, fail immediately
  # (git worktree add would reject with "already checked out at <path>", but
  # pre-check here so the caller gets a clearer reason).
  local already_checked_out
  already_checked_out=$(git worktree list --porcelain 2>/dev/null | awk -v b="refs/heads/$branch" '
    /^branch / && $2==b { print "yes"; exit }
  ')
  if [ "$already_checked_out" = "yes" ]; then
    echo "ERROR: '$branch' is already checked out in another worktree. Use the existing worktree or remove it and try again." >&2
    return 1
  fi

  slug="$base_slug"
  while true; do
    local path="$root/.astra-worktrees/$slug"
    if [ ! -e "$path" ]; then
      break
    fi
    slug="${base_slug}-${n}"
    n=$((n + 1))
    [ "$n" -gt 50 ] && { echo "ERROR: Too many slug collisions ($base_slug)" >&2; return 1; }
  done
  local wt_path
  wt_path=$(astra_worktree_path "$slug") || return 1

  mkdir -p "$(dirname "$wt_path")"
  if ! git worktree add "$wt_path" "$branch" >&2; then
    echo "ERROR: worktree attach failed: $branch" >&2
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
      echo "WARN: worktree removal failed: $wt_path (manual cleanup required)" >&2
      return 1
    }
  fi
  astra_prune_worktrees
  return 0
}

# --- sprint-level worktree -------------------------------------------------
#
# v5.0+ policy: /sprint-init creates a single worktree per sprint, and all
# feature work and tests happen inside it. /pr-merge then merges to dev and
# removes the worktree. The slug rule is `sprint-<N>-<name>` and the branch
# name is unified as `feat/sprint-<N>-<name>`.

# Echo `<branch>\t<worktree-path>` after creating a sprint-level worktree.
# Arguments: <sprint-number> <sprint-name> [base-ref]
#   base-ref defaults to `origin/dev` (falls back to `origin/main` if dev
#   doesn't exist remotely).
astra_create_sprint_worktree() {
  local n="$1"
  local name="$2"
  local base_ref="${3:-}"
  if [ -z "$n" ] || [ -z "$name" ]; then
    echo "ERROR: astra_create_sprint_worktree requires <sprint-number> <sprint-name>" >&2
    return 2
  fi

  # If base-ref is empty, fall back to dev then main.
  if [ -z "$base_ref" ]; then
    if git ls-remote --heads origin dev 2>/dev/null | grep -q dev; then
      base_ref="origin/dev"
    elif git ls-remote --heads origin main 2>/dev/null | grep -q main; then
      base_ref="origin/main"
    else
      base_ref="HEAD"
    fi
  fi

  local branch="feat/sprint-${n}-${name}"
  astra_create_worktree_new "$branch" "$base_ref"
}

# Remove the sprint worktree by sprint number + name.
astra_remove_sprint_worktree() {
  local n="$1"
  local name="$2"
  if [ -z "$n" ] || [ -z "$name" ]; then
    echo "ERROR: astra_remove_sprint_worktree requires <sprint-number> <sprint-name>" >&2
    return 2
  fi
  astra_remove_worktree "feat/sprint-${n}-${name}"
}

# --- port allocation -------------------------------------------------------
#
# The main worktree (dev) uses the base port; sprint worktrees use base + 100*N.
# When a worktree for the same sprint number is already alive (resume/rebrand
# scenarios), `lsof` detects ports in use and shifts by +100.

# Echo a free port starting from `<base> + 100*<sprint-number>`. If that port
# is in use, shift by +100 until a free port is found (max 10 shifts).
# Arguments: <base-port> <sprint-number>
astra_compute_port_base() {
  local base="$1"
  local n="$2"
  if [ -z "$base" ] || [ -z "$n" ]; then
    echo "ERROR: astra_compute_port_base requires <base-port> <sprint-number>" >&2
    return 2
  fi

  local candidate=$((base + 100 * n))
  local tries=0
  while [ "$tries" -lt 10 ]; do
    if ! astra_port_in_use "$candidate"; then
      printf '%s' "$candidate"
      return 0
    fi
    candidate=$((candidate + 100))
    tries=$((tries + 1))
  done
  echo "ERROR: Port candidates shifted 10 times but all are in use (base=$base, N=$n)" >&2
  return 1
}

# Return 0 if <port> is currently bound by any process.
# When `lsof` is unavailable, fall back to `ss` / `netstat`. If all fail,
# report "not in use" (false negative — caller must verify directly).
astra_port_in_use() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -i ":$port" -sTCP:LISTEN -t >/dev/null 2>&1
    return $?
  fi
  if command -v ss >/dev/null 2>&1; then
    ss -ltn "sport = :$port" 2>/dev/null | grep -q ":$port"
    return $?
  fi
  if command -v netstat >/dev/null 2>&1; then
    netstat -an 2>/dev/null | grep -E "[:\.]$port[[:space:]]+.*LISTEN" -q
    return $?
  fi
  return 1
}

# Echo the absolute path of the worktree env file managed by sprint-init.
astra_worktree_env_path() {
  local wt_path="$1"
  if [ -z "$wt_path" ]; then
    echo "ERROR: astra_worktree_env_path requires <worktree-path>" >&2
    return 2
  fi
  printf '%s/.astra-worktree.env' "$wt_path"
}

# Write `.astra-worktree.env` into the sprint worktree. Idempotent — overwrites.
# Arguments: <worktree-path> <sprint-number> <sprint-name> <port-base>
astra_write_worktree_env() {
  local wt_path="$1"
  local n="$2"
  local name="$3"
  local port_base="$4"
  if [ -z "$wt_path" ] || [ -z "$n" ] || [ -z "$name" ] || [ -z "$port_base" ]; then
    echo "ERROR: astra_write_worktree_env requires <worktree-path> <sprint-number> <sprint-name> <port-base>" >&2
    return 2
  fi
  local env_file
  env_file=$(astra_worktree_env_path "$wt_path") || return 1

  cat > "$env_file" <<EOF
# Auto-generated by /sprint-init — do not edit by hand.
# Sourced by /test-run before launching the project's dev server so that
# the sprint worktree never collides with the main worktree's default port.
ASTRA_SPRINT_NUMBER=${n}
ASTRA_SPRINT_NAME=${name}
ASTRA_PORT_BASE=${port_base}

# Framework-specific ports (offset = port_base - 3000).
# /test-run picks the right one for the detected stack.
PORT=${port_base}
NEXT_PUBLIC_PORT=${port_base}
VITE_PORT=$((port_base + 2173))
SERVER_PORT=$((port_base + 5080))
DJANGO_PORT=$((port_base + 5000))
FASTAPI_PORT=$((port_base + 5000))
EOF

  # Ensure the env file (locally generated, never tracked) is gitignored
  # inside the sprint worktree so accidental `git add -A` doesn't stage it.
  local gi_file="$wt_path/.gitignore"
  if [ -f "$gi_file" ]; then
    grep -Fxq ".astra-worktree.env" "$gi_file" \
      || printf '\n# Local sprint env (auto-generated by /sprint-init)\n.astra-worktree.env\n' >> "$gi_file"
  else
    cat > "$gi_file" <<'GIEOF'
# Local sprint env (auto-generated by /sprint-init)
.astra-worktree.env
GIEOF
  fi
  return 0
}
