# Python — Pydantic + LLM SDK Patterns

Reference for authoring tool schemas in Python projects. Covers Pydantic v2, Anthropic SDK, and LangChain `@tool`.

> SSoT for the 6 attributes is [`six-attributes.md`](six-attributes.md). This file is the *Python rendering* of those attributes.

---

## 1. Minimal pattern (Anthropic Tool Use)

```python
from pydantic import BaseModel, Field
from typing import Literal

class CreateIssueInput(BaseModel):
    """Create a GitHub issue in the given repository.

    Use when the user asks to file a bug, open a ticket, or report an issue.
    Do NOT use to comment on an existing issue (use add_issue_comment instead).
    """
    repo: str = Field(
        description="owner/repo format. e.g. 'anthropics/claude-code'",
        pattern=r"^[\w.-]+/[\w.-]+$",
    )
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Short imperative title. e.g. 'Fix race condition in worker pool'",
    )
    body: str = Field(
        default="",
        description="Markdown body. Empty string if no detail to add.",
    )
    labels: list[str] = Field(
        default_factory=list,
        description="Label names. e.g. ['bug', 'p1']",
    )

# Anthropic tools array
tools = [
    {
        "name": "create_issue",
        "description": CreateIssueInput.__doc__,
        "input_schema": CreateIssueInput.model_json_schema(),
    }
]
```

The docstring on the BaseModel **is** the description — keep the 6 attributes there, not scattered across `Field` descriptions.

---

## 2. Field constraints that flow into JSON Schema

| Pydantic | Resulting JSON Schema | Why it helps the LLM |
|----------|-----------------------|----------------------|
| `min_length`, `max_length` | `minLength`, `maxLength` | Hard guard against empty or runaway strings |
| `ge`, `le`, `gt`, `lt` | `minimum`, `maximum`, exclusive variants | Range-bound numeric inputs |
| `pattern=r"..."` | `pattern` | Format constraints (e.g. `owner/repo`) |
| `Literal["a", "b"]` | `enum: ["a", "b"]` | Strict finite values |
| `default=...` | `default` (but not `required`) | Field becomes optional |
| `Field(..., description=...)` | `description` | Per-parameter hint visible to the model |

Avoid `Any` and unannotated `dict` — they degrade the schema to "unknown shape" and the model will guess.

---

## 3. Optional vs required

```python
class Input(BaseModel):
    user_id: str                      # required → in schema "required" array
    note: str | None = None           # optional, nullable
    tags: list[str] = Field(default_factory=list)  # optional, never None
```

A field is *required* iff it has **no default**. `str | None = None` is *optional and nullable* — different from required.

---

## 4. Nested objects

```python
class Address(BaseModel):
    city: str = Field(description="e.g. 'Seoul'")
    country: str = Field(description="ISO 3166-1 alpha-2. e.g. 'KR'", pattern=r"^[A-Z]{2}$")

class UserInput(BaseModel):
    """Create a user profile.

    Use when the user provides a name and an address.
    """
    name: str
    address: Address
```

The model will produce a nested dict matching the structure. Keep nesting ≤ 2 levels — deeper structures noticeably degrade accuracy.

---

## 5. LangChain `@tool` decorator

```python
from langchain_core.tools import tool

@tool
def search_users(query: str, limit: int = 10) -> list[dict]:
    """Search users by name or email substring.

    Use when the user asks to find users by partial name, email, or handle.
    Do NOT use when the user supplies a known user_id (use get_user_by_id).

    Args:
        query: Substring to match against name or email. e.g. 'park', 'gmail.com'
        limit: Max results. 1-100. Default 10.

    Returns:
        List of {id: str, name: str, email: str} sorted by relevance.
    """
    ...
```

LangChain reads the docstring and the type hints; both are visible to the LLM. Make sure the docstring carries the 6 attributes.

---

## 6. Common smell — `**kwargs` / free dict

```python
# BAD
def run_query(**kwargs) -> dict:
    """Run a query."""

# GOOD
class RunQueryInput(BaseModel):
    """Run a SQL query against the analytics warehouse.

    Use when the user asks for a SQL-based data pull. Do NOT use for
    ad-hoc spreadsheet analysis (use load_dataframe instead).
    """
    sql: str = Field(description="SELECT statement. e.g. \"SELECT count(*) FROM users\"")
    timeout_seconds: int = Field(default=30, ge=1, le=300)
```

`**kwargs` produces no schema. The model receives "this tool takes anything" — the worst possible signal.

---

## 7. Anthropic SDK — input_schema by hand

If you cannot use Pydantic (e.g. constraints not expressible), write the JSON Schema directly:

```python
tool = {
    "name": "lookup_price",
    "description": "Fetch the current price for a stock ticker.\n\nUse when the user asks for a live price, quote, or current value of a publicly traded company.",
    "input_schema": {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "Uppercase ticker symbol. e.g. 'AAPL', 'TSLA'",
                "pattern": "^[A-Z]{1,5}$",
            },
            "currency": {
                "type": "string",
                "enum": ["USD", "KRW", "EUR", "JPY"],
                "default": "USD",
            },
        },
        "required": ["ticker"],
    },
}
```

Even hand-written schemas must satisfy the 6 attributes — the validator does not distinguish where the schema came from.
