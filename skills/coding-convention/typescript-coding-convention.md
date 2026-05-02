⚠ Large CLAUDE.md will impact performance (43.1k chars > 40.0k) · /memory to edit                                                                                                                                                                                             
  ⎿  SessionStart:startup hook error  # TypeScript Coding Convention

> **Based on Google TypeScript Style Guide**
>
> - Official documentation: https://google.github.io/styleguide/tsguide.html
> - Community edition: https://ts.dev/style/
> - Tool: https://github.com/google/gts
> - Maintained by: Google Engineering

---

## 1. Selection Rationale

| Criteria | Google TS Guide | Airbnb | Microsoft | StandardJS |
|---|---|---|---|---|
| TypeScript native | Yes | No (JS-based) | Yes (internal use) | Partial |
| Comprehensiveness | Very high | High for JS but lacking for TS | Narrow scope | Minimal |
| Active maintenance | Yes (gts v7.0.0, 2025.12) | No (stalled since 2023.01) | Sporadic | Low |
| Tooling support | gts (ESLint + Prettier) | Community-maintained | None | ts-standard |
| Type system coverage | Extensive | None | Minimal | None |

Google TypeScript Style Guide is designed specifically for TypeScript and is the only major guide that comprehensively covers all areas including the type system, modules, classes, and error handling.

---

## 2. Source File Basic Rules

| Rule | Details |
|---|---|
| Encoding | UTF-8 required |
| Whitespace character | Only ASCII horizontal space (0x20) is allowed |
| Escape sequences | Use `\'`, `\"`, `\\`, `\b`, `\f`, `\n`, `\r`, `\t`, `\v`. Numeric escapes are prohibited |
| Octal escapes | Prohibited (legacy) |
| Non-ASCII characters | Prefer actual Unicode characters. Add comments for non-printable characters |
| Formatter | Use Prettier. No manual formatting debates |
| Semicolons | Always required. Do not rely on ASI (Automatic Semicolon Insertion) |

---

## 3. Source File Structure

Files are organized in the following order, with **exactly one blank line** between each section:

1. Copyright information (if applicable)
2. `@fileoverview` JSDoc (if applicable)
3. Imports
4. File implementation

---

## 4. Import / Export Rules

### 4.1 Import

| Rule | Details |
|---|---|
| Allowed import types | Module (`import * as foo`), Named (`import {Thing}`), Default (only when required by external libraries), Side-effect (`import '...'`) |
| Default import | Not recommended. Use only when required by external libraries |
| Import paths | Use relative paths (`./foo`) for the same project. Limit upward traversal (`../../../`) |
| Namespace vs Named | Named for frequently used symbols, Namespace for many symbols from large APIs |
| Import renaming | Allowed for conflict resolution, generated names, clarity improvement |
| `import type` | Use `import type {...}` for type-only imports (Google version) |
| `require()` | Prohibited |
| `/// <reference>` | Prohibited |

### 4.2 Export

| Rule | Details |
|---|---|
| Named exports only | `export class Foo { }`. `export default` prohibited |
| Why no default export | No canonical name, no error when importing non-existent symbol, inconsistency |
| Minimize API | Only export symbols actually used outside the module |
| No mutable exports | `export let` prohibited. Use explicit getter functions for mutable bindings |
| No container classes | No namespace classes with only static methods/properties. Export individual constants/functions |

### 4.3 Module System

| Rule | Details |
|---|---|
| ES6 modules only | Must use `import`/`export` statements |
| `namespace` prohibited | `namespace Foo { }` prohibited |
| Code organization | Organize by feature (products/checkout) rather than by type (views/models) |

---

## 5. Naming Rules

### 5.1 Identifier Styles

| Style | Applies to |
|---|---|
| `UpperCamelCase` | Classes, interfaces, types, enums, decorators, type parameters, JSX components |
| `lowerCamelCase` | Variables, parameters, functions, methods, properties, module aliases |
| `CONSTANT_CASE` | Global constants, `static readonly` class properties, enum values |

### 5.2 Detailed Rules

| Rule | Details |
|---|---|
| Do not include type info in names | The type system already expresses it |
| No underscore prefix/suffix | No `_` for private members, unused variables, etc. |
| No `I` prefix for interfaces | `IMyInterface` prohibited |
| No `opt_` prefix | No `opt_` for optional parameters |
| Treat abbreviations as words | `loadHttpUrl` (correct), `loadHTTPURL` (incorrect). Exception: platform names like `XMLHttpRequest` |
| Dollar sign (`$`) | Use only when required by third-party frameworks (jQuery, RxJS) |
| Descriptive names | Clear names that new readers can understand |
| Short names | Single-character variables only in scopes of 10 lines or fewer |
| Type parameters | Single uppercase letter (`T`) or `UpperCamelCase` |
| Test methods | xUnit-style `_` separation allowed: `testX_whenY_doesZ()` |
| File names | `snake_case` |
| Constants | Only `CONSTANT_CASE` for deeply immutable values. Use `lowerCamelCase` if instantiated multiple times |

---

## 6. Type System

### 6.1 Type Inference

| Rule | Details |
|---|---|
| Leverage inference | Omit annotations for obvious types (string, number, boolean, RegExp, `new` expressions) |
| Annotate when helpful | Use annotations when inference is unclear in complex expressions |
| Return types | Optional. Reviewers may request for clarity |

### 6.2 Null and Undefined

| Rule | Details |
|---|---|
| No general preference | Decide based on context |
| Nullable type aliases | Do not include `\|null`, `\|undefined` in type aliases. Add only at the point of use |
| Optional vs undefined | Prefer `field?` over `\|undefined` in fields/parameters |
| Null comparison | `== null` is allowed to check both null and undefined simultaneously |

### 6.3 Interface vs Type Alias

| Rule | Details |
|---|---|
| Object types | Use `interface` (type alias + object literal prohibited) |
| Union, tuple, primitive | Use type alias |
| Reason | Interface provides better display, performance, and intent clarity |

### 6.4 Array Types

| Rule | Details |
|---|---|
| Simple types | Use `T[]` or `readonly T[]` |
| Complex types | Use `Array<string \| number>` |
| Multidimensional | `T[][]`, `T[][][]` |

### 6.5 `any` Type

| Rule | Details |
|---|---|
| Avoid `any` | Prohibited. Consider specific types, `unknown`, or lint suppression + documentation |
| Prefer `unknown` | `unknown` is safer — requires type narrowing before use |
| Suppressing warnings | Add comment explaining legitimate reasons for `any` (e.g., test mocks) |

### 6.6 `{}` (Empty Object Type)

Instead of `{}`, use `unknown` (any value including null/undefined), `Record<string, T>` (dictionary), or `object` (excludes primitives).

### 6.7 Enum

| Rule | Details |
|---|---|
| Use `enum` | Always use `enum`, `const enum` prohibited |
| Enum values | `CONSTANT_CASE` |
| Boolean conversion | Do not convert with `Boolean()` or `!!`. Use explicit comparison operators |

### 6.8 Wrapper Types

`String`, `Boolean`, `Number` prohibited. Always use lowercase `string`, `boolean`, `number`. Constructor usage like `new String()` is also prohibited.

---

## 7. Variables

| Rule | Details |
|---|---|
| `const` by default | Always use `const`. Use `let` only for reassignment |
| `let` | Only for variables that are reassigned |
| `var` prohibited | Never use |
| One per declaration | `let a = 1, b = 2;` prohibited |
| No forward references | Do not use variables before declaration |

---

## 8. Functions

### 8.1 Declarations and Expressions

| Rule | Details |
|---|---|
| Prefer function declarations | Use `function foo() { }` for named functions |
| Arrow functions | Use in expressions instead of pre-ES6 `function` keyword |
| Function expressions prohibited | Use arrow functions. Exceptions: dynamic `this` binding, generator functions |

### 8.2 Arrow Function Bodies

| Rule | Details |
|---|---|
| Concise body | Only when the return value is actually used |
| Block body | When the return value is unused (prevent accidental returns) |

### 8.3 `this` Keyword

| Rule | Details |
|---|---|
| Allowed usage | Class constructors, class methods, functions with explicit `this` type, arrow functions within a valid `this` scope |
| Prohibited usage | Global object, event targets |
| Preference | Arrow functions or explicit parameters instead of `.bind()`, `.call()`, `.apply()` |

### 8.4 Parameters

| Rule | Details |
|---|---|
| Default initialization | Use simple initialization without side effects |
| Destructuring | Use for readability when there are many optional parameters |
| Rest parameters | Use instead of `arguments`. Do not use `arguments` as a local variable name |
| Spread | Use function spread instead of `Function.prototype.apply` |

### 8.5 Constructors

| Rule | Details |
|---|---|
| Always use parentheses | `new Foo()` (correct), `new Foo` (incorrect) |
| Omit empty constructors | Omit if there are no parameter properties, visibility modifiers, or decorators |

---

## 9. Classes

### 9.1 Member Rules

| Rule | Details |
|---|---|
| Private field syntax prohibited | `#ident` prohibited. Use TypeScript `private` keyword |
| `readonly` | Apply to properties not reassigned outside the constructor |
| Parameter properties | Remove boilerplate: `constructor(private readonly barService: BarService) {}` |
| Initialize at declaration | Prefer field initializers over constructor initialization |
| No shape changes | Do not add/remove properties after constructor completion |
| Restrict visibility | Maximize restrictions. Use `public` modifier only for non-readonly parameter properties |
| No bracket access | `obj['foo']` to bypass visibility is prohibited |

### 9.2 Getters and Setters

| Rule | Details |
|---|---|
| Getters must be pure | Consistent results, no side effects, no observable state changes |
| Non-trivial logic required | At least one accessor per property must have logic (no simple field wrapping) |

### 9.3 Static Methods

| Rule | Details |
|---|---|
| Avoid private static | Prefer module-local (non-exported) functions |
| No dynamic dispatch | Static methods should only be called on the base class |
| No `this` in static | Do not use `this` in static context |

---

## 10. Control Flow

| Rule | Details |
|---|---|
| Use braces | Always use for multi-line blocks. Single-line `if` may omit: `if (x) x.doFoo();` |
| Assignment in control statements | Avoid. When used, indicate intent with extra parentheses |
| Array iteration | Use `for (... of someArr)`. Do not use `for...in` on arrays (returns string indices) |
| Object iteration | Use `Object.keys(obj)` or `Object.entries()` |
| `.forEach()` | Prohibited (invalidates compiler reachability checks) |
| `===` / `!==` | Always use. Exception: `== null` for simultaneous null/undefined check |
| Switch `default` | Must always exist and be placed last |
| Switch fall-through | Only empty groups may fall through. Non-empty groups are prohibited |

---

## 11. Error Handling

| Rule | Details |
|---|---|
| Always `new Error()` | `Error()` without `new` prohibited |
| Throw only Error instances | Or subclasses. Prefer custom exceptions |
| `unknown` in catch | Declare catch parameters as `unknown`. Narrow with type guards |
| Empty catch blocks | Prohibited unless justified with a comment |
| Limit try block scope | Move code that does not throw outside try-catch |
| Promise rejection | Use `Promise.reject(new Error(...))`. Do not reject with non-Error values |

---

## 12. Type Coercion

| Rule | Details |
|---|---|
| String conversion | Use `String()` function or template literals. Do not cast via string concatenation |
| Boolean conversion | Use `Boolean()` or `!!`. No explicit conversion needed in conditions with implicit coercion |
| Number conversion | Use `Number()`. Explicit `NaN` check on the return value is required |
| Unary `+` prohibited | Do not use `+x` for string-to-number conversion |
| `parseInt`/`parseFloat` | Use only for strings other than decimal. Note: silently ignores trailing characters |
| Integer parsing | `Number()` followed by `Math.floor()` or `Math.trunc()` |

---

## 13. Comments and Documentation

### 13.1 JSDoc vs Line Comments

| Rule | Details |
|---|---|
| `/** JSDoc */` | For documentation (consumed by tools, editors, generators) |
| `// line comments` | For implementation details (human readers only) |
| Multi-line comments | Use multiple `//` lines. Block-style `/* */` prohibited |
| No decorative boxes | Do not wrap with asterisk frames |

### 13.2 JSDoc Content Rules

| Rule | Details |
|---|---|
| Document all top-level exports | Explain purpose for module consumers |
| Do not restate types | TypeScript already declares them. Omit `@type`, `@implements`, `@enum`, `@private` |
| Do not use `@override` | Compiler does not enforce it, leading to annotation mismatch |
| `@param`/`@return` | Use only when there is information beyond the signature |

### 13.3 Allowed JSDoc Tags

`@fileoverview`, `@param`, `@return`, `@throws`, `@deprecated`, `@see`, `@example`, `@nocollapse`

---

## 14. Decorators

| Rule | Details |
|---|---|
| Do not define new decorators | Use only framework-provided decorators (Angular, Polymer, etc.) |
| Reason | Experimental feature, known bugs, differences from TC39 standard |
| Placement | Immediately before the decorated symbol. No blank lines in between |

---

## 15. Prohibited Features List

| # | Prohibited Feature |
|---|---|
| 1 | `var` keyword |
| 2 | `const enum` |
| 3 | `export default` |
| 4 | `export let` (mutable exports) |
| 5 | `namespace Foo { }` |
| 6 | `require()` imports |
| 7 | `/// <reference>` directives |
| 8 | Wrapper type constructors (`new String()`, `new Boolean()`, `new Number()`) |
| 9 | `Array()` constructor |
| 10 | `Object()` constructor |
| 11 | Private field syntax (`#ident`) |
| 12 | Dynamic code execution functions and `Function(...string)` constructor |
| 13 | `with` statement |
| 14 | `debugger` statement (production) |
| 15 | Modifying built-in prototypes |
| 16 | Adding symbols to the global object |
| 17 | Non-standard ECMAScript features |
| 18 | Legacy octal escapes |
| 19 | `@ts-ignore` directives |
| 20 | `@ts-nocheck` directives |
| 21 | `@ts-expect-error` (except in tests) |
| 22 | Function expressions (use arrow functions) |
| 23 | Container/namespace classes (static-only classes) |
| 24 | `.forEach()` (Array, Map, Set) |

---

## 16. Consistency and Ambiguity

| Rule | Details |
|---|---|
| Local consistency | For issues not addressed by the guide, follow same-file pattern > same-directory pattern |
| Formatter authority | Source code formatting is automated by Prettier. No manual formatting debates |

---

## References

- [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)
- [ts.dev Style Guide (Community Edition)](https://ts.dev/style/)
- [Google gts - GitHub](https://github.com/google/gts)
- [Airbnb JavaScript Style Guide - GitHub](https://github.com/airbnb/javascript)
- [Microsoft TypeScript Coding Guidelines](https://github.com/microsoft/TypeScript/wiki/Coding-guidelines)
