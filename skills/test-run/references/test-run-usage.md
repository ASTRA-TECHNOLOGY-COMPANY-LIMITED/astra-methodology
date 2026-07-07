# Test-run Usage Examples & Operational Notes

Appendix moved out of `SKILL.md`. Read for invocation forms and the operational
caveats that apply across a run.

## Quick Run Examples

Each form analyzes the target → writes test cases → executes them:

```
/test-run http://localhost:3000   # a specific URL
/test-run login flow              # a specific scenario
/test-run                         # full project integration test
```

## Notes

- **Worktree-aware port (v5.0+)**: sources `PORT`/`SERVER_PORT`/`VITE_PORT` etc.
  from `.astra-worktree.env`; won't conflict with the main-worktree (dev) server.
- **Port-termination guarantee**: pre-launch check (0.D) → state-file + `lsof`
  PID capture (Step 3) → 4-stage cleanup (Step 10) on success/failure/interrupt.
- If a server already occupies the target port, **abort** — never kill the
  external process; the user terminates it manually and reruns.
- Do not expose `.env` secrets or personal information in logs; use test data
  only in test-dedicated DB/environments.
- Performance measurements reflect the dev environment and may differ from prod.
- **Merge/push separation (v5.0+)**: no dev merge/push here — that is
  `/pr-merge`'s job, which also removes the sprint worktree after merge.
