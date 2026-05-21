# TypeScript — Zod + LLM SDK Patterns

Reference for authoring tool schemas in TypeScript projects. Covers Zod, the Anthropic SDK, and LangChain JS `tool()`.

> SSoT for the 6 attributes is [`six-attributes.md`](six-attributes.md). This file is the *TypeScript rendering* of those attributes.

---

## 1. Minimal pattern (Anthropic Tool Use)

```ts
import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";

const CreateIssueInput = z.object({
  repo: z
    .string()
    .regex(/^[\w.-]+\/[\w.-]+$/)
    .describe("owner/repo format. e.g. 'anthropics/claude-code'"),
  title: z
    .string()
    .min(1)
    .max(200)
    .describe("Short imperative title. e.g. 'Fix race in worker pool'"),
  body: z
    .string()
    .default("")
    .describe("Markdown body. Empty string if no detail to add."),
  labels: z
    .array(z.string())
    .default([])
    .describe("Label names. e.g. ['bug', 'p1']"),
});

const tools = [
  {
    name: "create_issue",
    description: [
      "Create a GitHub issue in the given repository.",
      "",
      "Use when the user asks to file a bug, open a ticket, or report an issue.",
      "Do NOT use to comment on an existing issue (use add_issue_comment).",
    ].join("\n"),
    input_schema: zodToJsonSchema(CreateIssueInput),
  },
];
```

Keep the description string co-located with the schema so a `git grep` for the tool name reveals both.

---

## 2. Constraints that flow into JSON Schema

| Zod | JSON Schema | Why it helps |
|-----|-------------|--------------|
| `.min(n)` / `.max(n)` on strings | `minLength` / `maxLength` | Bounded strings |
| `.min(n)` / `.max(n)` on numbers | `minimum` / `maximum` | Range guards |
| `.regex(/.../)` | `pattern` | Format constraints |
| `z.enum([...])` | `enum: [...]` | Strict finite values |
| `.default(...)` | `default`, not required | Field is optional |
| `.describe("...")` | `description` | Per-parameter hint |
| `.nullable()` | `type: [..., "null"]` | Explicit null |
| `.optional()` | removed from `required` | Optional, undefined OK |

`z.any()` and `z.unknown()` produce open schemas; avoid them unless the tool truly accepts arbitrary input.

---

## 3. Optional vs required vs nullable

```ts
const Input = z.object({
  user_id: z.string(),                       // required, non-null
  note: z.string().nullable(),               // required, can be null
  tags: z.array(z.string()).default([]),     // optional, defaults to []
  ref: z.string().optional(),                // optional, may be undefined
});
```

Three concepts, three Zod methods. Choose deliberately — mixing them is the most common source of LLM-side argument errors in TypeScript projects.

---

## 4. Nested objects

```ts
const Address = z.object({
  city: z.string().describe("e.g. 'Seoul'"),
  country: z
    .string()
    .regex(/^[A-Z]{2}$/)
    .describe("ISO 3166-1 alpha-2. e.g. 'KR'"),
});

const UserInput = z.object({
  name: z.string(),
  address: Address,
});
```

Keep nesting ≤ 2 levels. For deeper structures, flatten with prefixes (`address_city`, `address_country`) — the model handles flat keys more reliably than 3+ levels of nesting.

---

## 5. LangChain JS `tool()`

```ts
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const searchUsers = tool(
  async ({ query, limit }) => {
    return await db.users.search(query, limit);
  },
  {
    name: "search_users",
    description: [
      "Search users by name or email substring.",
      "",
      "Use when the user asks to find users by partial name, email, or handle.",
      "Do NOT use when the user supplies a known user_id (use get_user_by_id).",
    ].join("\n"),
    schema: z.object({
      query: z
        .string()
        .min(1)
        .describe("Substring. e.g. 'park', 'gmail.com'"),
      limit: z
        .number()
        .int()
        .min(1)
        .max(100)
        .default(10)
        .describe("Max results, 1-100."),
    }),
  },
);
```

LangChain serialises both the description and the schema; both must satisfy the 6 attributes.

---

## 6. MCP server tool definition

```ts
import { McpServer } from "@modelcontextprotocol/sdk/server";

server.tool(
  "lookup_price",
  {
    description: [
      "Fetch the current price for a stock ticker.",
      "",
      "Use when the user asks for a live price, quote, or current value of a publicly traded company.",
      "Do NOT use for historical prices (use price_history).",
    ].join("\n"),
    inputSchema: z.object({
      ticker: z
        .string()
        .regex(/^[A-Z]{1,5}$/)
        .describe("Uppercase ticker symbol. e.g. 'AAPL', 'TSLA'"),
      currency: z
        .enum(["USD", "KRW", "EUR", "JPY"])
        .default("USD"),
    }),
  },
  async ({ ticker, currency }) => {
    // ...
  },
);
```

The MCP wire format expects the JSON Schema variant; if you author with Zod, run `zodToJsonSchema()` once at server boot rather than on every call.

---

## 7. Common smell — `z.record(z.unknown())` as a catch-all

```ts
// BAD
const Input = z.object({ params: z.record(z.unknown()) });

// GOOD
const Input = z.object({
  sql: z.string().describe("SELECT statement. e.g. \"SELECT count(*) FROM users\""),
  timeoutSeconds: z.number().int().min(1).max(300).default(30),
});
```

Open dictionaries push the entire input-validation burden onto the LLM — exactly what schema-based tool calling exists to avoid.
