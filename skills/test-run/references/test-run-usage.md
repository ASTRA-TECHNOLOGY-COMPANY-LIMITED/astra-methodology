# Test-run Usage Examples & Operational Notes

Appendix moved out of `SKILL.md`. Read for invocation forms and the operational
caveats that apply across a run.

## Quick Run Examples

Each form analyzes the target → writes test cases → executes them:

```
/test-run http://localhost:3000   # a specific URL
/test-run login flow              # a specific scenario
/test-run                         # full project integration test
/test-run Chrome MCP http://localhost:3000 # force the Chrome MCP backend
/test-run cmux http://localhost:3000       # force the cmux backend
```

Without a backend keyword the detection order applies — **ego (default) → Chrome
MCP (fallback) → cmux (legacy)**; see
`$CLAUDE_PLUGIN_ROOT/docs/development/browser-backend-policy.md`.

## Notes

- **Worktree-aware port (v5.0+)**: sources `PORT`/`SERVER_PORT`/`VITE_PORT` etc.
  from `.astra-worktree.env`; won't conflict with the main-worktree (dev) server.
- **Port-termination guarantee**: pre-launch check (0.D) → state-file + `lsof`
  PID capture (Step 3) → 4-stage cleanup (Step 10) on success/failure/interrupt.
- If a server already occupies the target port, **abort** — never kill the
  external process; the user terminates it manually and reruns.
- Do not expose `.env` secrets or personal information in logs; use test data
  only in test-dedicated DB/environments.
- **ego mode inherits the user's real login state** for the target origin, so an
  auth scenario can start already signed in (a broken login flow then looks like
  a PASS) and writes land in the real account. Clear the session first or record
  the scenario as `SKIP` — see `references/browser-ego.md`. Never point ego mode
  at a production origin for write-heavy scenarios.
- Performance measurements reflect the dev environment and may differ from prod.
- **Merge/push separation (v5.0+)**: no dev merge/push here — that is
  `/pr-merge`'s job, which also removes the sprint worktree after merge.
