# Failure Modes — What Ambiguous Tool Descriptions Cause

Reference for the validation step. Each row maps a missing attribute (from [`six-attributes.md`](six-attributes.md)) to the observable failure during runtime.

| # | Failure mode | Symptom in logs / traces | Most often caused by |
|---|--------------|--------------------------|----------------------|
| 1 | **Wrong-tool selection** | LLM calls `search_users` when the user clearly gave an ID | Overlapping descriptions between `get_x` and `search_x`; missing anti-pattern (Attribute 2) |
| 2 | **Skipped tool** | LLM produces an answer from training data when a tool was the right path | First-line not verb-led; missing trigger keywords (Attribute 1, 3) |
| 3 | **Malformed arguments** | `ValidationError` from the tool function; type mismatch | No per-parameter examples; free `str` where an enum belongs (Attribute 4, 5) |
| 4 | **Retry-loop explosion** | Same tool called 3–5× in a row with permuted arguments | Return shape unclear → model cannot tell whether previous call succeeded (Attribute 6) |
| 5 | **User-intent bypass** | LLM replies "I cannot do that" though a tool exists | Description so vague the LLM under-confidently routes; missing first-line directive (Attribute 1) |
| 6 | **Wrong side-effect** (most severe) | Real DB row created, payment fired, message sent — all spuriously | Side-effect tool described as a "read" or with weak anti-pattern (Attribute 2, 6) |
| 7 | **Un-auditable trace** | Post-incident review cannot reconstruct *why* the tool was called | No documented decision rule in the description |

---

## Severity ladder (used by the validator)

- **P0 — block merge**: any side-effect tool missing an anti-pattern, return-shape, or enum constraint that could cause failure #6.
- **P1 — warn**: read-only tool missing Attribute 1, 4, or 6.
- **P2 — flag**: Attribute 3 (synonyms) absent — usually a soft accuracy hit, not a correctness risk.

---

## Why "side-effect tools are special"

Read-only failures cost a retry. Side-effect failures **leave durable damage** (rows in tables, money moved, notifications delivered). Hence the rule of thumb:

> A side-effect tool description must explicitly name itself a side-effect tool, list at least one anti-pattern that disambiguates it from any read-only sibling, and document the *exact* state mutation it performs.

This is the same rationale ASTRA uses for `disable-model-invocation: true` on workflows like `/pr-merge` and `/deploy`.
