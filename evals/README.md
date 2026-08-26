# ASTRA Plugin Evals

Regression cases for `claude plugin eval` (early access as of 2026-07 — the CLI
reports "currently in early access"; these cases follow the documented
`evals/**/prompt.md + graders/*.md` layout so they run as soon as the feature GA's).

Run (once available):

```bash
claude plugin eval astra-methodology                 # all cases, with no-plugin baseline arm
claude plugin eval --case "trigger-*" .              # trigger-accuracy cases only, from repo path
claude plugin eval --threshold 0.8 --json .          # CI gate
```

## What is covered

| Case | Verifies |
|------|----------|
| `trigger-coding-convention/` | `coding-convention` auto-skill fires when editing a TypeScript file (Gate 1 write-time enforcement) |
| `trigger-blueprint-invocation/` | A feature-design request routes to the `/blueprint` skill (not ad-hoc authoring) |

Each case directory contains `prompt.md` (the user turn) and `graders/*.md`
(LLM-judge rubrics scored 0–1). Add new cases as sibling directories.
