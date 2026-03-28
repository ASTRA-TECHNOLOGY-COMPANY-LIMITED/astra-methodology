---
name: coding-convention
description: >
  Automatically applies the project's coding conventions when writing or modifying code.
  Used when editing or creating Java, TypeScript, React Native, Python, CSS/SCSS files,
  or when performing code reviews and refactoring.
---

# Coding Convention Application Skill

When writing or modifying code, you must follow the conventions below.
For detailed rules for each language, refer to the reference documents in this directory.

## Language Detection

Detect the language from the target file extension:
- `.java` → Apply Java convention (reference: java-coding-convention.md)
- `.ts`, `.tsx` → Apply TypeScript convention (reference: typescript-coding-convention.md)
- `.tsx`, `.ts` (React Native project) → Additionally apply React Native convention (reference: react-native-coding-convention.md)
- `.py` → Apply Python convention (reference: python-coding-convention.md)
- `.css`, `.scss`, `.sass` → Apply CSS/SCSS convention (reference: css-scss-coding-convention.md)

> **React Native Detection**: If the project contains `react-native` or `expo` in `package.json` dependencies, apply the React Native convention as a complementary layer on top of the TypeScript convention for all `.tsx`/`.ts` files.

> **Mobile Design Guide**: When working on a mobile project (React Native, Flutter, or KMP), additionally reference `$CLAUDE_PLUGIN_ROOT/docs/ux/mobile-design-guide.md` for UI/UX implementation decisions. This guide provides platform-specific guidelines (Apple HIG Liquid Glass, Material Design 3 Expressive), touch interaction patterns (thumb zone, gesture mapping), animation timing (50~400ms per type), haptic feedback mapping (iOS UIFeedbackGenerator / Android HapticFeedbackConstants), dark mode principles (surface elevation, #121212 not #000000), accessibility requirements (44pt/48dp touch targets, 4.5:1 contrast), and expert polish tips. Apply these standards when creating or modifying UI components, screens, navigation, forms, and animations.

## Java Convention Essentials (based on Google Java Style Guide)

- **Encoding**: UTF-8
- **Indent**: 2 spaces (block), +4 spaces (continuation lines)
- **Line length**: 100 characters
- **Braces**: K&R style, always use even for single statements
- **Naming**:
  - Package: `com.example.deepspace` (all lowercase)
  - Class: `UpperCamelCase` (test classes end with `Test`)
  - Method: `lowerCamelCase` (verb/verb phrase)
  - Constant: `UPPER_SNAKE_CASE` (`static final` + deeply immutable)
  - Field/parameter/local variable: `lowerCamelCase`
  - Type variable: `T`, `E`, `RequestT`
- **Import**: No wildcards, separate static/non-static, ASCII sort
- **Javadoc**: Required for all `public`/`protected` members. Summary is a noun/verb phrase (not a sentence)
- **@Override**: Always use when legal
- **Exceptions**: Never silently ignore
- **Static members**: Access only via class name (`instance.staticMethod()` is prohibited)
- **finalize()**: Do not override
- **Arrays**: `String[] args` (O), `String args[]` (X)
- **long literals**: Uppercase `L` (`100L`)

## CSS/SCSS Convention Essentials (based on CSS Guidelines + Sass Guidelines)

- **Indent**: 2 spaces, no tabs
- **Line length**: 80 characters
- **Naming**: BEM (`block__element--modifier`), lowercase kebab-case
- **File naming**: `kebab-case`, SCSS partials use `_` prefix
- **Selectors**:
  - No ID selectors (`#id` usage prohibited)
  - No type qualification (`div.class` prohibited)
  - Maximum depth 3 levels (ideally 1~2)
- **Property order**: Group by type (Positioning → Box Model → Typography → Visual → Animation → Misc)
- **Colors**: Lowercase hex, shorthand when possible (`#fff`), no color keywords
- **Units**: Font in `rem`, line-height as unitless number, no units on 0
- **Value notation**: Leading zero required (`0.5`), `border: 0` (not `none`)
- **SCSS nesting**: Maximum 3 levels, nesting recommended only for pseudo-classes/state classes
- **SCSS variables**: `$kebab-case`, constants `$UPPER_SNAKE_CASE`, manage related values with Map
- **@extend**: Avoid usage, use only `%placeholder` when required
- **!important**: Only proactive use in utility classes, reactive use prohibited
- **Media queries**: Mobile-first (`min-width`), write inline with components
- **z-index**: Centrally managed with Map + getter function, no arbitrary values
- **Animations**: Only `transform`/`opacity`, no `transition: all`, `prefers-reduced-motion` support required
- **File structure**: 7-1 pattern (abstracts, base, components, layout, pages, themes, vendors)
- **Prohibited patterns**: ID selectors, `!important` abuse, `transition: all`, `@extend .class`, color keywords, magic numbers, 4+ level nesting

## TypeScript Convention Essentials (based on Google TypeScript Style Guide)

- **Semicolons**: Always required
- **Formatter**: Prettier
- **Naming**:
  - Class/interface/type/enum: `UpperCamelCase`
  - Variable/parameter/function/method: `lowerCamelCase`
  - Global constants, enum values: `CONSTANT_CASE`
  - File names: `snake_case`
  - Type parameter: `T` or `UpperCamelCase`
- **Export**: `export default` prohibited, use named exports only
- **Import**: Use `import type {...}`, `require()` prohibited
- **Types**: `any` prohibited → use `unknown`. Use `interface` for objects, `type alias` for union/tuple
- **Variables**: `const` by default, `let` only when reassignment is needed. `var` is strictly prohibited
- **Prohibited patterns**: `var`, `const enum`, `export default`, `export let`, `namespace`, `#ident`, `.forEach()`, `.bind()/.call()/.apply()`, `@ts-ignore`, `@ts-nocheck`
- **Control flow**: `===`/`!==` required (exception: `== null`). Use `for...of` (`for...in` prohibited for arrays)
- **Error handling**: `new Error()` required, catch uses `unknown`, empty catch needs justification

## React Native Convention Essentials (based on Airbnb React/JSX + Obytes RN Starter + React Native Official Docs)

> Applied as a complementary layer on top of the TypeScript convention when the project is a React Native/Expo project.

- **File naming**: `kebab-case` for all files and folders (`login-screen.tsx`, `use-auth-store.ts`)
- **Screen suffix**: `-screen.tsx` (e.g., `login-screen.tsx`, `feed-screen.tsx`)
- **Hook prefix**: `use-` file naming (e.g., `use-auth.ts`), `use` + PascalCase in code (`useAuth`)
- **Components**: Functional only (class components prohibited), `PascalCase` naming
- **Exports**: Named exports only (`export default` prohibited)
- **Props**: Always define `type` for props, destructure in parameters, `camelCase` naming
- **JSX**: Self-closing for childless elements, omit `true` value for boolean props, no nested ternaries
- **Styling**: Use `StyleSheet.create()` or NativeWind. No inline styles. Styles co-located at file bottom
- **State**: TanStack Query (server state) + Zustand (client state). Separate server/client state
- **Navigation**: Expo Router file-based routing. `app/` as thin re-export layer, logic in `features/`
- **Structure**: Feature-based architecture (`features/` → `components/` → `lib/`). Co-locate tests
- **Hooks**: Top-level only, correct dependency arrays, single responsibility per hook
- **Performance**: `React.memo` for expensive components, `useCallback` for FlatList renderers, stable `keyExtractor`, no callbacks in JSX
- **Imports**: React core → third-party → internal (`@/`) → relative → type-only
- **Max constraints**: 3 function params, 110 lines per function
- **Accessibility**: `accessibilityLabel` + `accessibilityRole` on interactive elements, minimum 44×44 touch target
- **Prohibited**: Class components, `export default`, inline styles, array index as key, nested ternaries, `any` for props, `console.log` in production, `Dimensions.get()` in render

## Python Convention Essentials (based on PEP 8)

- **Indent**: 4 spaces, no tabs
- **Line length**: 79 characters (comments/docstrings 72 characters)
- **Naming**:
  - Package: `mypackage` (short lowercase)
  - Module: `my_module` (lowercase_underscore)
  - Class: `CapWords` (CamelCase)
  - Exception: `CapWords` + `Error` suffix
  - Function/method: `lowercase_with_underscores`
  - Constant: `UPPER_CASE_WITH_UNDERSCORES`
  - Instance method first argument: `self`, class method: `cls`
- **Import order**: Standard library → Third-party → Local (blank line between groups)
- **No wildcard imports**: Avoid `from module import *`
- **Comparison**: `is None` / `is not None` (`== None` prohibited), use `isinstance()` (`type()` prohibited)
- **Empty sequences**: `if not seq:` (use falsy), `if len(seq):` prohibited
- **Docstrings**: `"""triple double quotes"""`, imperative mood ("Return X"), all public members
- **Lambda assignment prohibited**: `f = lambda x: 2*x` prohibited → `def f(x): return 2*x`
- **Resource management**: Use `with` statement
- **Blank lines**: 2 blank lines before/after top-level definitions, 1 blank line before/after methods within a class
