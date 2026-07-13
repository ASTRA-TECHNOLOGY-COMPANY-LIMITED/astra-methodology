# Review severity rubric, completion output, and quick-run examples

Reference material for `/pr-merge` (extracted from SKILL.md — templates and examples only; all decision rules stay inline in SKILL.md).

## Severity classification (Step 8 report rendering)

| Severity | Description | Examples |
|----------|-------------|----------|
| **Critical** | Must fix immediately; risk of production outage | SQL injection, null reference, data loss |
| **High** | Recommended fix; important bug or security issue | Unhandled exception, possible auth bypass |
| **Medium** | Code-quality improvement; no functional impact | Duplicate code, inefficient logic, unclear naming |
| **Low** | Style/convention; optional improvement | Formatting, missing comments, unused imports |

## Completion output template (Step 9.7)

```
## PR Review & Merge complete

### Result summary
- PR: {PR URL}
- Merge: {branch-name} → {target-branch}
- Review iterations: {N}
- Fixed issues: Critical {n}, High {n}
- Status: ✅ merged

### Changes
- {commit summary 1}
- {commit summary 2}
```

## Quick Run Examples

```
/pr-merge                   # inside .worktrees/sprint-3-user-auth/ (the pipeline invokes it there): review loop → "finalize now?" HITL → self-transition → merge → promotion
cd "$(git rev-parse --git-common-dir)/.." && /pr-merge # Main Phase re-entry: auto-detect pending sprint PR → merge → promotion path prompt (staging/dev/skip)

/pr-merge 5                 # up to 5 review iterations (Sprint Phase only)
/pr-merge --no-review       # quick merge without code review
/pr-merge --draft           # create as Draft PR then review
/pr-merge --minor           # minor version bump (only matters on --main promotion)
/pr-merge --auto            # unattended end-to-end (both phases + auto-cd); promotion target still HITL

/pr-merge --staging         # promote dev → staging (Step 10.0 asks source: bulk dev or an integration branch)
/pr-merge --main            # promote staging → main / release (Step 10.0 asks source; version bump here)
/pr-merge --staging --no-review
```
