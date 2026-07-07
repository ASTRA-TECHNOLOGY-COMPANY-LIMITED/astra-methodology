# Grader: TypeScript convention applied

Score 1.0 when ALL of the following hold in the produced code / transcript, otherwise score proportionally (each bullet worth 0.25):

- The generated file uses a **named export** (no `export default`).
- No `any` type appears; the function has explicit parameter and return types.
- No `var` declarations; `const`/`let` only.
- Strict equality (`===`/`!==`) is used wherever equality is checked (score this bullet 0.25 automatically if no equality check exists).

Evidence must come from the actual file content written by the agent, not from stated intentions.
