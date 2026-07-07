# Manual Data & Output Structures

Reference skeletons used by the pipeline.

## Sections in this file
- Output directory structure (Step 2.A)
- Search index schema (Step 5.B)

## Output directory structure (Step 2.A)

Create under `docs/manual/{feature-name}/`. `{feature-name}` is the single feature name (e.g., `auth`, `payment`) or, for "all", the project name / `service-guide`.

```
docs/manual/{feature-name}/
├── index.html
├── chapters/
├── assets/
├── screenshots/
│   ├── desktop/
│   ├── tablet/    (when RESPONSIVE_MODE >= 3)
│   └── mobile/    (when RESPONSIVE_MODE >= 2)
└── shared/
```

## Search index schema (Step 5.B)

Scan every chapter to build `search-index.json`. Each section's `content` includes the first 200 characters of the body text (for search matching).

```json
[
  {
    "chapter": "01",
    "title": "Getting Started",
    "url": "chapters/01-getting-started.html",
    "sections": [
      { "heading": "Service introduction", "anchor": "#intro", "content": "..." },
      { "heading": "How to access", "anchor": "#access", "content": "..." }
    ]
  }
]
```
