---
description: Generates an HTML service manual / help center under docs/manual/ from a running service URL and project documents
argument-hint: "<service-url> <feature-name|all>"
allowed-tools: AskUserQuestion, Skill
---

# Generate Service Manual

Lightweight entry point that collects a service URL and a target feature, then delegates the full pipeline to the `/manual-generator` skill.

The skill handles document analysis (blueprints / planner), real-browser screenshot capture (ego → Chrome MCP), design tone selection, and HTML package generation under `docs/manual/{feature-name}/`. For per-step details, see [skills/manual-generator/SKILL.md](../skills/manual-generator/SKILL.md).

## Input

Parsed from `$ARGUMENTS` (order-insensitive — the token starting with `http://` or `https://` is the URL, the other is the feature):

| Position | Meaning | Example |
|----------|---------|---------|
| 1st token | Service URL (required) | `http://localhost:3000` |
| 2nd token | Feature name OR `all` (required) | `auth`, `payment`, `all` |

If either token is missing, ask via `AskUserQuestion` — use two separate questions:

```
Q1. Service URL (required) — URL of the running service for screenshot capture
    Example: http://localhost:3000

Q2. Documentation target (required) — feature scope
    Options: <feature names from docs/blueprints> | "all"
```

## Procedure

1. Parse `$ARGUMENTS` → extract `{SERVICE_URL}` and `{TARGET_FEATURE}`
2. If either is missing, run the two `AskUserQuestion` prompts above
3. Validate URL form (starts with `http://` or `https://`) — on malformed input, re-prompt
4. Invoke `Skill manual-generator` with both values:
   ```
   Skill('manual-generator', '{SERVICE_URL} {TARGET_FEATURE}')
   ```

The skill itself handles:
- Project context loading (`CLAUDE.md`, `docs/blueprints/`, `docs/planner/`, `src/styles/design-tokens.css`)
- URL accessibility check + document-only fallback (Step 0.C)
- TOC + design-tone confirmation via `AskUserQuestion`
- Real-browser screenshot capture per chapter (ego (lite) by default, Chrome MCP as fallback)
- HTML package generation (cover variant or Help Center variant)
- Validation and final report

## Output

`docs/manual/{feature-name}/`

```
docs/manual/{feature-name}/
├── index.html              ← cover or Help Center landing
├── chapters/
│   ├── 01-getting-started.html
│   └── ...
├── assets/
│   ├── tokens.css          ← copy of src/styles/design-tokens.css
│   ├── manual-base.css
│   ├── manual-components.css
│   ├── manual-print.css
│   └── manual-helpcenter.css  (only when DESIGN_TONE = Help Center)
├── screenshots/
│   ├── desktop/
│   ├── tablet/             (when RESPONSIVE_MODE >= 3)
│   └── mobile/             (when RESPONSIVE_MODE >= 2)
├── shared/
│   ├── nav.js
│   ├── search.js
│   └── theme.js
└── search-index.json
```

Open with `open docs/manual/{feature-name}/index.html`.

## Related

- `/manual-generator` — the full skill (same pipeline). Use directly when you need finer control over each step.
- `/catalog-generator` — product catalog generator (sibling skill).
- `/handoff-publish` — UX/Dev/QA handoff package (Screen-ID based).
