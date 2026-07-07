# Step 0 — Worktree Context & Port Isolation (v5.0+)

Detailed setup for SKILL.md Step 0. Testing runs on the **current branch of the
current worktree**; this skill never performs a dev merge (that is `/pr-merge`'s
job). Run blocks A–D in order before starting the server.

## Contents
- [A. Detect worktree context](#a-detect-worktree-context)
- [B. Commit unstaged changes](#b-commit-unstaged-changes)
- [C. Load worktree port env](#c-load-worktree-port-env)
- [D. Pre-launch port availability check](#d-pre-launch-port-availability-check)

## A. Detect worktree context

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/*/astra-methodology/* 2>/dev/null | sort -V | tail -1)}"
if [ -z "$PLUGIN_ROOT" ] || [ ! -f "$PLUGIN_ROOT/scripts/worktree-helpers.sh" ]; then
  echo "ERROR: CLAUDE_PLUGIN_ROOT not found. Check the plugin cache path." >&2
  exit 1
fi
source "$PLUGIN_ROOT/scripts/worktree-helpers.sh"

CURRENT_BRANCH=$(git branch --show-current)
if astra_is_isolated_worktree; then IN_SPRINT_WT=1; else IN_SPRINT_WT=0; fi
```

| Context | Handling |
|---------|----------|
| Sprint worktree (isolated, sprint branch) | Test on current branch as-is (normal) |
| Main worktree + work branch (compatibility) | Test on current branch as-is |
| Main worktree + shared branch (dev/main/staging/master) | Test on current branch as-is (one-off fallback) |

## B. Commit unstaged changes

If uncommitted changes exist on the current branch before testing, create a wip
commit so file changes during testing do not introduce non-determinism:

```bash
if [ -n "$(git status --porcelain)" ]; then
  git add -u
  git commit -m "wip: pre-test commit on ${CURRENT_BRANCH}"
fi
```

`git add -u` only stages already-tracked files — `.env`, `node_modules/`, and
build artifacts are excluded.

## C. Load worktree port env

A sprint worktree contains the `.astra-worktree.env` written by `/sprint-init`.
Source it to apply sprint-specific ports:

```bash
WT_ENV="$(astra_worktree_env_path "$(pwd)")"
if [ -f "$WT_ENV" ]; then
  set -a; . "$WT_ENV"; set +a   # shellcheck disable=SC1090
  echo "Sprint worktree env loaded: PORT=$PORT (base=$ASTRA_PORT_BASE)"
else
  echo "No .astra-worktree.env — using default port"
fi
```

## D. Pre-launch port availability check

> The executable form of this check (source helpers → set `TEST_PORT` → abort if
> a port is bound) lives **inline in SKILL.md Step 0** — it is load-bearing and
> must run even if this reference is skipped. This section only explains *why*.

Verify that *every* per-stack port is available; abort if any one is occupied (so
as not to kill another worktree or external process). Checking only a single
`PORT` cannot preempt runtime conflicts in Spring Boot (`SERVER_PORT`),
Django/FastAPI (`DJANGO_PORT`/`FASTAPI_PORT`), or Vite (`VITE_PORT`) stacks. The
SKILL.md loop iterates over port *values* (`for p in "$PORT" "$SERVER_PORT" …`)
rather than variable names — zsh does not support bash's `${!var}` indirect
expansion, so value iteration is the portable form.
