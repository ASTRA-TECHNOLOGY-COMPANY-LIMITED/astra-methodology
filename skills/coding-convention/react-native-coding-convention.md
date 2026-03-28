# React Native Coding Convention

> **Based on Airbnb React/JSX Style Guide + Obytes React Native Starter + React Native Official Docs**
>
> - Airbnb React/JSX Style Guide: https://github.com/airbnb/javascript/tree/master/react
> - Obytes React Native Starter: https://starter.obytes.com/getting-started/rules-and-conventions/
> - React Native Official Docs: https://reactnative.dev/docs/getting-started
> - Expo Documentation: https://docs.expo.dev/
> - State of React Native 2024 Survey: https://results.stateofreactnative.com/en-US/

---

## 1. Selection Rationale

| Criteria | Airbnb React/JSX | Obytes RN Starter | React Native Official | Ignite (Infinite Red) |
|---|---|---|---|---|
| React Native specificity | Partial (React only) | Yes (RN/Expo focused) | Yes (authoritative) | Yes (production-tested) |
| Comprehensiveness | High (component rules) | Very high (full stack) | Moderate (core only) | Moderate (project-specific) |
| Active maintenance | Stalled (2023.01~) | Yes (2025 active) | Yes (Meta maintained) | Yes (9+ years active) |
| Community adoption | 148K+ GitHub stars | Growing rapidly | Official standard | 17K+ GitHub stars |
| TypeScript coverage | Partial | Full (mandatory TS) | Full | Full |
| Tooling support | eslint-config-airbnb | @antfu/eslint-config | Expo ESLint config | Custom ESLint config |

This convention synthesizes the component/JSX rules from Airbnb (the most widely adopted React style guide), the project-level conventions from Obytes (the most comprehensive React Native-specific convention set), and the official guidance from React Native/Expo docs. It is designed as a complementary layer to the TypeScript convention — TypeScript convention handles language-level rules, this convention handles React Native framework-level rules.

---

## 2. Source File Basic Rules

| Rule | Details |
|---|---|
| TypeScript required | All React Native code must be written in TypeScript. JavaScript files are prohibited |
| File extension | `.tsx` for files containing JSX, `.ts` for files without JSX |
| File naming | `kebab-case` for all files and folders (e.g., `login-screen.tsx`, `use-auth-store.ts`) |
| Folder naming | `kebab-case` (e.g., `auth/`, `feed/`, `components/`) |
| Screen file suffix | Screens must end with `-screen.tsx` (e.g., `login-screen.tsx`, `feed-screen.tsx`) |
| Hook file prefix | Custom hooks must start with `use-` (e.g., `use-auth-store.ts`, `use-theme.ts`) |
| API file | Feature API files are named `api.ts` within the feature directory |
| Test file suffix | `.test.tsx` or `.test.ts`, co-located with source file |
| Encoding | UTF-8 required |
| Formatter | ESLint (with `@antfu/eslint-config`) or Prettier |

---

## 3. Project Structure

### 3.1 Feature-Based Architecture

```
src/
  app/                    # Expo Router file-based routing (thin re-export layers)
  features/               # Feature-oriented self-contained modules
    {feature-name}/
      {feature}-screen.tsx
      components/
        {component}.tsx
        {component}.test.tsx
      api.ts
      use-{store}.ts
  components/             # Shared/reusable UI components (design system)
    ui/
  lib/                    # Core infrastructure (API client, auth, i18n, hooks)
    api/
    auth/
    hooks/
    i18n/
  translations/           # i18n resource files
```

### 3.2 Structure Rules

| Rule | Details |
|---|---|
| Feature-first organization | Organize code by feature domain, not by file type (not `views/`, `models/`, `controllers/`) |
| Self-contained features | Each feature directory contains screens, components, API calls, and state management |
| Thin route layer | `app/` directory files are re-export layers only. All screen logic lives in `features/` |
| Component promotion | Move a component to shared `components/` only when used across 2+ features |
| Flat structure | Avoid deeply nested folders. Maximum 3 levels deep within `features/` |
| Co-located tests | Test files sit next to their source files, not in a separate `__tests__/` tree |

---

## 4. Component Rules

### 4.1 Component Naming

| Rule | Details |
|---|---|
| Component names | Always `PascalCase` (`ProfileScreen`, `UserCard`, `LoginForm`) |
| Component instances | Always `camelCase` (`const loginForm = <LoginForm />`) |
| One component per file | Each file exports one primary component. Small helper components may be co-located |
| Functional components only | Class components are prohibited. Use functional components with hooks |
| Named exports only | `export default` prohibited. Use `export function` or `export const` |

### 4.2 Component Organization

Within a component file, code should follow this order:

1. Imports
2. Type definitions (Props, etc.)
3. Component function declaration
4. Helper functions (if any)
5. Styles (co-located at bottom)

### 4.3 JSX Rules

| Rule | Details |
|---|---|
| Self-closing tags | Use for components without children: `<Image />` not `<Image></Image>` |
| Boolean props | Omit value when `true`: `<Input disabled />` not `<Input disabled={true} />` |
| Parentheses for multi-line JSX | Wrap multi-line JSX in parentheses |
| Key prop | Always provide a unique, stable `key` for list items. Array index as key is prohibited |
| Conditional rendering | Use `&&` for simple conditions, ternary for if/else. Nested ternaries are prohibited |
| Fragment syntax | Use `<>...</>` short syntax. Use `<Fragment key={...}>` only when `key` is needed |

### 4.4 Props Rules

| Rule | Details |
|---|---|
| Props type definition | Always define a `type` for component props (e.g., `type LoginFormProps = { ... }`) |
| Props destructuring | Destructure props in function parameters: `function Card({ title, content }: CardProps)` |
| Prop naming | Always `camelCase`. Boolean props prefixed with `is`/`has`/`can` (e.g., `isVisible`, `hasError`) |
| Callback props | Prefix with `on` (e.g., `onPress`, `onSubmit`, `onChange`) |
| Max inline props | Move to next line when 3+ props. One prop per line |
| Spread props | Avoid spreading entire props objects (`{...props}`). Pass individual props explicitly |

---

## 5. Hooks Rules

### 5.1 Naming and Structure

| Rule | Details |
|---|---|
| Hook naming | Must start with `use` followed by a capital letter: `useAuth`, `useTheme`, `useOnlineStatus` |
| File naming | `use-{hook-name}.ts` or `use-{hook-name}.tsx` (kebab-case) |
| Single responsibility | Each custom hook handles one concern |
| Return type | Always type the return value of custom hooks explicitly |

### 5.2 Rules of Hooks

| Rule | Details |
|---|---|
| Top-level only | Always call hooks at the top level. Never inside conditions, loops, or nested functions |
| React functions only | Only call hooks from React function components or custom hooks |
| Dependency arrays | Always specify dependency arrays correctly for `useEffect`, `useMemo`, `useCallback` |
| Exhaustive deps | ESLint `react-hooks/exhaustive-deps` rule must be enabled |

### 5.3 Hook Usage Patterns

| Rule | Details |
|---|---|
| `useState` | Prefer multiple `useState` calls over complex state objects |
| `useEffect` | Limit one side effect per `useEffect`. Always include cleanup when subscribing |
| `useMemo` | Use only for expensive computations. Do not memoize primitives or simple calculations |
| `useCallback` | Use for handlers passed as props to memoized children. Required for `FlatList` render functions |
| `useRef` | Use for imperative handles and mutable values that do not trigger re-render |

---

## 6. Styling Rules

### 6.1 Styling Approach

| Rule | Details |
|---|---|
| Preferred methods | `StyleSheet.create()` (default) or NativeWind (Tailwind utility classes) |
| Co-locate styles | Define styles in the same file as the component, at the bottom |
| No inline styles | Do not define styles inside JSX: `style={{ margin: 10 }}` prohibited |
| No styles in render | Never create `StyleSheet.create()` or style objects inside the component body |
| Design tokens | Use centralized theme constants for colors, spacing, typography, and border radius |

### 6.2 StyleSheet Conventions

| Rule | Details |
|---|---|
| Variable naming | `camelCase` for style keys: `container`, `headerText`, `submitButton` |
| Grouping | Group styles by component section (container, header, body, footer) |
| No magic numbers | Extract repeated values into theme constants |
| Responsive design | Use `Dimensions`, `useWindowDimensions()`, or percentage-based layouts |
| Platform-specific | Use `Platform.select()` or `.ios.tsx`/`.android.tsx` file extensions |

### 6.3 NativeWind Conventions (when adopted)

| Rule | Details |
|---|---|
| Class ordering | Follow Tailwind's recommended order: layout → spacing → sizing → typography → visual |
| Conditional classes | Use `clsx` or `cn` utility for conditional class composition |
| Responsive | Use Tailwind breakpoints (`sm:`, `md:`, `lg:`) for responsive design |
| Custom classes | Define in `tailwind.config.js`, not as inline arbitrary values |

---

## 7. State Management

### 7.1 State Type Selection

| State Type | Recommended Tool | Use Case |
|---|---|---|
| Server state | TanStack Query (React Query) | API data, caching, re-validation, background refetch |
| Client state | Zustand | UI state, user preferences, lightweight global state |
| Local state | `useState` / `useReducer` | Component-scoped state |
| Form state | React Hook Form + Zod | Form input, validation, submission |
| Secure storage | react-native-mmkv | Auth tokens, sensitive data |

### 7.2 State Management Rules

| Rule | Details |
|---|---|
| Separate server/client state | Never mix API-fetched data and UI state in the same store |
| Minimal global state | Keep global state to a minimum. Prefer local state when possible |
| No prop drilling | When passing props through 3+ levels, lift state to Zustand store or use Context |
| Context API limits | Use Context only for rarely changing values (theme, locale). Not for frequently updated state |
| Immutable updates | Always return new objects/arrays. Never mutate state directly |

---

## 8. Navigation Patterns

### 8.1 Expo Router (Recommended)

| Rule | Details |
|---|---|
| File-based routing | Routes defined by file structure in `app/` directory |
| Layout files | Use `_layout.tsx` for navigation layout definitions |
| Route groups | Use `(group)` folders for layout grouping without affecting URL |
| Dynamic routes | Use `[param].tsx` for dynamic segments |
| Typed routes | Enable typed routes in `app.json`: `"experiments": { "typedRoutes": true }` |
| Thin routes | `app/` files import and re-export from `features/`. No screen logic in `app/` |

### 8.2 React Navigation (Alternative)

| Rule | Details |
|---|---|
| Type safety | Always type navigation props using `NativeStackScreenProps` or `CompositeScreenProps` |
| Screen naming | Screen names in `PascalCase` matching the component name |
| Navigation params | Define param types with `RootStackParamList` type |
| Deep linking | Configure deep linking in navigation container |

---

## 9. Performance Optimization

### 9.1 Memoization Rules

| Rule | Details |
|---|---|
| `React.memo` | Wrap components that receive same props frequently. Provide custom comparator for object props |
| Do not over-memoize | Only memoize components that are demonstrably expensive to re-render |
| `useCallback` for lists | Required for `FlatList` `renderItem` and `keyExtractor` |
| `useMemo` scope | Use only for computationally expensive operations (sorting, filtering large arrays) |

### 9.2 FlatList / FlashList Optimization

| Rule | Details |
|---|---|
| Stable `keyExtractor` | Always provide a unique key. Array index as key is prohibited |
| `getItemLayout` | Provide when item heights are fixed (eliminates measurement overhead) |
| `removeClippedSubviews` | Set `true` for lists with 500+ items |
| `maxToRenderPerBatch` | Set to 10–15 items |
| `windowSize` | Set to 10–15 for optimal memory/performance balance |
| `renderItem` outside JSX | Define `renderItem` function outside JSX and wrap in `useCallback` |
| FlashList preferred | Use Shopify's `FlashList` as drop-in replacement for better performance |

### 9.3 Image Optimization

| Rule | Details |
|---|---|
| Expo Image preferred | Use `expo-image` instead of default `Image` for better caching and memory |
| Specify dimensions | Always set `width` and `height` or use `aspectRatio` |
| Placeholder | Provide `placeholder` or `placeholderContentFit` for loading states |
| Cache policy | Configure cache policy for frequently displayed images |

### 9.4 General Performance Rules

| Rule | Details |
|---|---|
| No callbacks in render | Define event handlers outside JSX. Use `useCallback` when passing to children |
| No styles in render | Create styles outside component body |
| Reanimated for animations | Use React Native Reanimated (runs on UI thread). Avoid `Animated` API for complex animations |
| Hermes engine | Ensure Hermes is enabled (default in modern React Native) |
| New Architecture | Enable Fabric and TurboModules when compatible |

---

## 10. Import Rules

### 10.1 Import Order

Imports must be organized in the following groups, separated by blank lines:

```typescript
// 1. React / React Native core
import { useState, useCallback } from 'react';
import { View, Text, Pressable } from 'react-native';

// 2. Third-party libraries
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'expo-router';

// 3. Internal modules (absolute imports)
import { Button } from '@/components/ui/button';
import { useAuth } from '@/lib/auth/utils';

// 4. Relative imports (same feature/module)
import { LoginForm } from './components/login-form';

// 5. Type-only imports
import type { User } from '@/types';
```

### 10.2 Import Rules

| Rule | Details |
|---|---|
| Absolute imports | Configure and use path aliases (`@/` or `~/`) for project-internal imports |
| No circular imports | Circular dependencies between modules are prohibited |
| Named imports only | `import default` prohibited (consistent with TypeScript convention) |
| Type imports | Use `import type` for type-only imports |
| Sort within groups | Alphabetical sort within each import group |

---

## 11. Error Handling

### 11.1 Error Boundary Pattern

| Rule | Details |
|---|---|
| Global error boundary | Wrap root component with error boundary for crash recovery |
| Feature error boundaries | Wrap independent feature screens with granular error boundaries |
| `react-error-boundary` | Use the `react-error-boundary` library for functional error boundary support |
| Fallback UI | Always provide a user-friendly fallback UI with retry action |

### 11.2 Async Error Handling

| Rule | Details |
|---|---|
| Try-catch for async | Always wrap `async` operations in try-catch blocks |
| TanStack Query errors | Use `onError` callbacks and `isError` state for API errors |
| Error typing | Catch parameter as `unknown`, then narrow with type guards |
| User feedback | Always show user-facing error messages (toast, alert, inline error) |
| Logging | Log errors to crash reporting service (Sentry, Crashlytics) in production |

---

## 12. Testing Conventions

### 12.1 Testing Stack

| Layer | Tool | Target |
|---|---|---|
| Unit tests | Jest | Business logic, utility functions, custom hooks |
| Component tests | React Native Testing Library (RNTL) | Rendering, user interactions, accessibility |
| E2E tests | Maestro | Full user journeys, critical paths |

### 12.2 Testing Rules

| Rule | Details |
|---|---|
| Co-located tests | Place test files next to source: `login-form.test.tsx` beside `login-form.tsx` |
| User-centric queries | Prefer `getByRole`, `getByText`, `getByLabelText` over `getByTestId` |
| Test behavior | Test user-visible behavior, not implementation details |
| Mock externals | Mock API calls, native modules, and navigation with Jest mocks |
| Hook testing | Use `renderHook` from `@testing-library/react-native` |
| Coverage target | Minimum 80% line coverage for business logic, 70% for components |

---

## 13. Accessibility (a11y)

| Rule | Details |
|---|---|
| `accessibilityLabel` | Provide for all interactive elements without visible text |
| `accessibilityRole` | Set appropriate role (`button`, `link`, `header`, `image`, etc.) |
| `accessibilityState` | Indicate `disabled`, `selected`, `checked`, `expanded` states |
| Touch target size | Minimum 44×44 points for all touchable elements |
| Color contrast | Minimum 4.5:1 contrast ratio for normal text, 3:1 for large text |
| Screen reader testing | Test with VoiceOver (iOS) and TalkBack (Android) |

---

## 14. Internationalization (i18n)

| Rule | Details |
|---|---|
| No hardcoded strings | All user-facing text must use i18n translation keys |
| Translation library | Use `i18next` + `react-i18next` or `expo-localization` |
| Key naming | Use dot-notation namespace: `auth.login.title`, `common.button.submit` |
| Sorted keys | Translation JSON keys must be sorted alphabetically |
| Identical keys | All language files must have identical key sets |
| RTL support | Test layouts with RTL languages. Use `I18nManager` for RTL flip |

---

## 15. Prohibited Patterns

| # | Prohibited Pattern | Reason |
|---|---|---|
| 1 | Class components | Legacy pattern. Use functional components + hooks |
| 2 | `export default` | No canonical name, inconsistent imports |
| 3 | Inline styles in JSX | Performance cost: new objects created every render |
| 4 | `StyleSheet.create()` inside component body | Creates new stylesheet every render |
| 5 | Array index as list `key` | Causes bugs with reordering, insertion, deletion |
| 6 | Nested ternaries in JSX | Unreadable. Extract to variables or separate components |
| 7 | Prop spreading (`{...props}`) | Hides what props are passed, makes debugging difficult |
| 8 | `console.log` in production | Use proper logging service. Remove or guard with `__DEV__` |
| 9 | Hardcoded strings in UI | Must use i18n translation keys |
| 10 | Direct state mutation | Always use setter functions from `useState` or immutable patterns |
| 11 | `useEffect` without cleanup | Subscriptions, timers, listeners must be cleaned up |
| 12 | Bare `catch` without error handling | Always handle or report caught errors |
| 13 | `any` type for props/state | Use specific types or `unknown` |
| 14 | Callbacks defined inside JSX | Causes unnecessary child re-renders |
| 15 | `FlatList` without `keyExtractor` | Required for correct reconciliation |
| 16 | Deep prop drilling (3+ levels) | Use state management or Context |
| 17 | Mixed server/client state | Keep API data and UI state in separate stores |
| 18 | `Dimensions.get()` in render | Use `useWindowDimensions()` hook instead |

---

## 16. ESLint Configuration

### 16.1 Recommended Plugins

| Plugin | Purpose |
|---|---|
| `eslint-plugin-react` | React-specific linting rules |
| `eslint-plugin-react-hooks` | Rules of Hooks enforcement |
| `eslint-plugin-react-native` | React Native specific rules (no inline styles, no color literals) |
| `@typescript-eslint/eslint-plugin` | TypeScript rules |
| `eslint-plugin-simple-import-sort` | Import ordering |
| `eslint-plugin-testing-library` | Testing Library best practices |

### 16.2 Key Rules

| Rule | Setting |
|---|---|
| `max-params` | `['error', 3]` — Maximum 3 function parameters |
| `max-lines-per-function` | `['error', 110]` — Maximum 110 lines per function |
| `react-hooks/rules-of-hooks` | `'error'` |
| `react-hooks/exhaustive-deps` | `'warn'` |
| `react-native/no-inline-styles` | `'error'` |
| `react-native/no-color-literals` | `'warn'` |
| `unicorn/filename-case` | `['error', { case: 'kebabCase' }]` |

---

## 17. Key Metrics Summary

| Metric | Value |
|---|---|
| File naming | `kebab-case` |
| Component naming | `PascalCase` |
| Variable/function naming | `camelCase` |
| Constant naming | `UPPER_SNAKE_CASE` |
| Hook naming | `use` + `PascalCase` (e.g., `useAuth`) |
| Max function params | 3 |
| Max function lines | 110 |
| Components | Functional only (no class components) |
| Exports | Named only (no `export default`) |
| Styling | `StyleSheet.create()` or NativeWind |
| State management | TanStack Query (server) + Zustand (client) |
| Navigation | Expo Router (file-based) |
| Testing | Jest + RNTL + Maestro |
| Min touch target | 44×44 points |

---

## References

- [Airbnb React/JSX Style Guide](https://github.com/airbnb/javascript/tree/master/react)
- [Obytes React Native Starter - Rules and Conventions](https://starter.obytes.com/getting-started/rules-and-conventions/)
- [Obytes React Native Starter - Project Structure](https://starter.obytes.com/getting-started/project-structure/)
- [React Native Official Docs](https://reactnative.dev/docs/getting-started)
- [React Native TypeScript Guide](https://reactnative.dev/docs/typescript)
- [React Native Performance Optimization](https://reactnative.dev/docs/optimizing-flatlist-configuration)
- [Expo Documentation](https://docs.expo.dev/)
- [Expo Router Documentation](https://docs.expo.dev/router/introduction/)
- [State of React Native 2024 Survey](https://results.stateofreactnative.com/en-US/)
- [Ignite Boilerplate by Infinite Red](https://github.com/infinitered/ignite)
- [React Official Docs - Custom Hooks](https://react.dev/learn/reusing-logic-with-custom-hooks)
- [eslint-plugin-react-native](https://github.com/Intellicode/eslint-plugin-react-native)
- [ASTRA Mobile Design Guide](../../docs/ux/mobile-design-guide.md) — Platform guidelines (Apple HIG, Material Design 3), touch interaction, animation timing, haptic feedback, dark mode, accessibility, and expert polish tips
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Material Design 3](https://m3.material.io/)
