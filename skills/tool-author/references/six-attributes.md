# Tool Description — 6 Required Attributes

Single Source of Truth for the six properties that every LLM tool description must satisfy. Derived from the L24 lesson and adapted to ASTRA's bilingual / English-description policy.

> **Why these six?** A description that lacks any one of them produces one of the five failure modes documented in [`failure-modes.md`](failure-modes.md): wrong tool, skipped tool, malformed arguments, repeated retries, or user-intent bypass.

---

## Attribute 1 — One-line summary + detailed body

The **first line** is what the LLM scans during routing; the **body** disambiguates edge cases.

```python
description = """Search the web for current information.

Use this tool when the user asks about recent events, current
prices, or live data the model would not know from training.
Do NOT use for general knowledge questions or computational tasks.
"""
```

| Rule | Reason |
|------|--------|
| First line ≤ 80 chars, verb-led ("Search...", "Fetch...", "Compute...") | LLM truncates / weighs the first sentence heaviest |
| Blank line between summary and body | Improves parser-side segmentation |
| Body lines ≤ 5 (Sweet spot 2–5) | Beyond this, other tools get drowned out in the system prompt |

---

## Attribute 2 — Anti-pattern ("when NOT to use")

The single largest cause of mis-invocation is **the LLM not knowing when to abstain**. Always include at least one negative example.

```
"Search the web for current data. Do NOT use for math or code."
```

Patterns:
- `Do NOT use for <competing domain>` — name the sibling tool if any
- `<This tool> is for X; for Y use <other_tool>` — explicit handoff
- `Skip this tool when <condition>` — covers ambiguous overlap

---

## Attribute 3 — Synonyms / abbreviations / colloquial terms

Users phrase the same intent in many ways. Bake the alternatives into the description so the LLM still matches.

```
"Calculator. Evaluates mathematical expressions, computes, arithmetic,
math problems, formulas, equations."
```

Build the synonym list from:
- Actual user transcripts (best signal)
- Common abbreviations in the domain (SLA, TPS, KPI…)
- Korean ↔ English pairs if the product is bilingual ("결제" / "payment" / "checkout")

---

## Attribute 4 — Per-parameter examples

LLMs infer formats from examples. Without them, expect free-form strings.

```python
from pydantic import BaseModel, Field

class WeatherInput(BaseModel):
    city: str = Field(
        description="City name in English. e.g. 'Seoul', 'New York', 'San Francisco'"
    )
    units: str = Field(
        default="celsius",
        description="Temperature units: 'celsius' or 'fahrenheit'"
    )
```

Checklist per parameter:
- [ ] At least one concrete example value (`e.g. 'Seoul'`)
- [ ] Unit / timezone / encoding if not obvious (`ISO 8601 UTC`, `cents not dollars`)
- [ ] Edge-case mention if the value can be tricky (`null vs empty string`)

---

## Attribute 5 — Enum constraints over free strings

Where the value space is finite, prefer `Literal` / `Enum`. The constraint flows into the JSON Schema, which the model can see.

```python
from typing import Literal

class CalcInput(BaseModel):
    operation: Literal["add", "subtract", "multiply", "divide"]
    a: float
    b: float
```

TypeScript (Zod):

```ts
import { z } from "zod";

const CalcInput = z.object({
  operation: z.enum(["add", "subtract", "multiply", "divide"]),
  a: z.number(),
  b: z.number(),
});
```

If the enum list is long (>10) or open-ended, fall back to `str` + a regex / pattern constraint and call that out in the description.

---

## Attribute 6 — Explicit return shape

The LLM uses the return shape to plan its next reasoning step. Ambiguous returns lead to wasted re-queries.

```
"""Returns:
{
  'temp': float (celsius),
  'condition': str ('sunny' | 'cloudy' | 'rain'),
  'humidity': int (percent 0-100)
}
"""
```

Patterns:
- Document units, ranges, and nullable fields
- For list returns, note ordering ("sorted by created_at DESC") and pagination
- For side-effect tools, document **state changes** as well as the return value ("Creates an issue and returns its ID")

---

## Self-check loop

After writing a description, ask:

| Question | Pass criterion |
|----------|----------------|
| Could I identify the right tool from this description alone, given a similar peer? | Yes |
| Does it state at least one *do-not-use* condition? | Yes |
| Could a user phrase their intent in a way that misses my keywords? | No (or covered) |
| Could the LLM send a wrong-typed argument? | No (enum / regex / example) |
| Could the LLM mis-handle the return? | No (shape documented) |

A description that fails any of these checks should not ship.
