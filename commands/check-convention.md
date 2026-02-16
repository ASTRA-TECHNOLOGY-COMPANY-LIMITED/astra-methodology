---
description: Checks code for coding convention compliance and reports violations
argument-hint: "<file path or directory>"
allowed-tools: Read, Glob, Grep
---

# Coding Convention Check

Check coding convention compliance for $ARGUMENTS.

> For in-depth analysis, the `convention-validator` agent can be used.

## Check Procedure

1. Read the target files and determine the language by file extension
2. Refer to the corresponding language's coding convention reference document
3. Check the following items in order

## Language Detection and Reference Documents

| Extension | Language | Reference Document |
|---|---|---|
| `.java` | Java | `skills/coding-convention/java-coding-convention.md` |
| `.ts`, `.tsx` | TypeScript | `skills/coding-convention/typescript-coding-convention.md` |
| `.tsx`, `.ts` (RN project) | React Native | `skills/coding-convention/react-native-coding-convention.md` |
| `.py` | Python | `skills/coding-convention/python-coding-convention.md` |
| `.css`, `.scss`, `.sass` | CSS/SCSS | `skills/coding-convention/css-scss-coding-convention.md` |

> **React Native Detection**: If `package.json` contains `react-native` or `expo` in dependencies, apply React Native convention as a complementary layer on top of TypeScript convention for `.tsx`/`.ts` files.

Before checking, the corresponding language's reference document must be read to confirm detailed rules.

## Check Items

### Common
- [ ] File encoding (UTF-8)
- [ ] Line length limit compliance (Java: 100 chars, TypeScript: Prettier, Python: 79 chars, CSS/SCSS: 80 chars)
- [ ] Indentation rules (Java: 2 spaces, Python: 4 spaces, CSS/SCSS: 2 spaces)
- [ ] Import order and wildcard usage
- [ ] Naming conventions (classes, methods, variables, constants)

### Java-specific (Google Java Style Guide)
- [ ] K&R brace style (opening brace on same line)
- [ ] Braces even for single-statement bodies
- [ ] @Override annotation usage
- [ ] Javadoc presence (public/protected members)
- [ ] Static member access (via class name only)
- [ ] Array declaration style (`String[] args`)
- [ ] Uppercase L suffix for long literals
- [ ] No ignored exceptions

### TypeScript-specific (Google TypeScript Style Guide)
- [ ] `export default` usage (prohibited)
- [ ] `any` type usage (prohibited -> use `unknown`)
- [ ] `var` usage (prohibited -> use `const`/`let`)
- [ ] `.forEach()` usage (prohibited -> use `for...of`)
- [ ] `const enum` usage (prohibited)
- [ ] `===` / `!==` usage (`==`/`!=` prohibited, `== null` exception)
- [ ] Missing semicolons
- [ ] `namespace` usage (prohibited)
- [ ] `import type` usage
- [ ] Filename snake_case compliance

### Python-specific (PEP 8)
- [ ] PEP 8 naming (snake_case functions/variables, CapWords classes)
- [ ] `is None` / `is not None` usage (`== None` prohibited)
- [ ] `isinstance()` usage (`type()` comparison prohibited)
- [ ] `with` statement usage (resource management)
- [ ] Empty sequence check (`if not seq:` required, `if len(seq):` prohibited)
- [ ] Bare `except:` usage (prohibited -> use specific exception types)
- [ ] Lambda assignment (prohibited)
- [ ] Docstring presence (triple double quotes)

### React Native-specific (Airbnb React/JSX + Obytes RN Starter + React Native Official)
- [ ] File naming `kebab-case` compliance (`login-screen.tsx`, `use-auth.ts`)
- [ ] Screen files suffixed with `-screen.tsx`
- [ ] Functional components only (class components prohibited)
- [ ] `export default` usage (prohibited — use named exports)
- [ ] Component naming `PascalCase` compliance
- [ ] Props type definition present for all components
- [ ] Inline styles in JSX (prohibited — use `StyleSheet.create()` or NativeWind)
- [ ] Styles defined inside component body (prohibited — define outside)
- [ ] Array index used as `key` in lists (prohibited)
- [ ] Nested ternaries in JSX (prohibited)
- [ ] Prop spreading `{...props}` usage (discouraged)
- [ ] Hooks called at top level (not inside conditions/loops)
- [ ] `useCallback` for FlatList `renderItem` and `keyExtractor`
- [ ] Callbacks defined inside JSX (prohibited — extract and memoize)
- [ ] Import order (React → third-party → internal → relative → type-only)
- [ ] `accessibilityLabel` on interactive elements without visible text
- [ ] Hardcoded user-facing strings (prohibited — use i18n keys)
- [ ] `console.log` without `__DEV__` guard (prohibited in production)
- [ ] `Dimensions.get()` in render (prohibited — use `useWindowDimensions()`)
- [ ] Max function parameters (3) and lines (110) compliance

### CSS/SCSS-specific (CSS Guidelines + Sass Guidelines)
- [ ] BEM naming (`block__element--modifier`)
- [ ] ID selector usage (prohibited)
- [ ] Nesting depth (max 3 levels)
- [ ] Property order (Positioning -> Box Model -> Typography -> Visual -> Animation)
- [ ] Color notation (lowercase hex, keywords prohibited)
- [ ] Unit rules (font: `rem`, no units on 0)
- [ ] `!important` overuse (allowed only for utility classes)
- [ ] Media query approach (mobile-first `min-width`)
- [ ] `@extend` usage (minimize, only `%placeholder`)
- [ ] `transition: all` usage (prohibited)
- [ ] Type-qualified selectors (`div.class` prohibited)
- [ ] SCSS variable naming (`$kebab-case`)

## Output Format

Report violations in the following format:

| Severity | Category | File:Line | Rule | Current Code | Suggested Fix |
|---|---|---|---|---|---|
| Error | Prohibited pattern | ... | ... | ... | ... |
| Warning | Naming | ... | ... | ... | ... |
| Info | Formatting | ... | ... | ... | ... |

Severity criteria:
- **Error**: Prohibited pattern violations (var, any, export default, == None, bare except, ID selectors, `!important` overuse, etc.)
- **Warning**: Convention mismatches (naming, line length, indentation, property order, etc.)
- **Info**: Improvement recommendations (missing Javadoc, missing docstrings, BEM mismatches, etc.)

Report total violation count and summary by severity/category at the end.
