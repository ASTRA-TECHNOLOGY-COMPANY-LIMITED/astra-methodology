# Mobile App Design — Comprehensive Guide

> A reference document that systematically organizes platform guidelines, expert know-how, and framework-by-framework implementation strategies for delivering polished, professional UX/UI in Android/iOS mobile applications

---

## Table of Contents

1. [Platform Design Guidelines](#1-platform-design-guidelines)
2. [Touch Interaction & Gesture Design](#2-touch-interaction--gesture-design)
3. [Navigation Patterns](#3-navigation-patterns)
4. [Typography & Visual Hierarchy](#4-typography--visual-hierarchy)
5. [Color System & Dark Mode](#5-color-system--dark-mode)
6. [Design Token System](#6-design-token-system)
7. [Mobile Form Design](#7-mobile-form-design)
8. [Animation & Motion](#8-animation--motion)
9. [Haptic Feedback](#9-haptic-feedback)
10. [Onboarding & First Impressions](#10-onboarding--first-impressions)
11. [Performance UX](#11-performance-ux)
12. [Accessibility](#12-accessibility)
13. [Per-Framework Implementation Strategies](#13-per-framework-implementation-strategies)
14. [Expert Know-How — What Makes an App Polished](#14-expert-know-how--what-makes-an-app-polished)

---

## 1. Platform Design Guidelines

### 1.1 Apple Human Interface Guidelines (HIG)

Apple's design philosophy rests on four pillars: **Clarity**, **Deference**, **Depth**, **Consistency**.

#### Liquid Glass (iOS 26, 2025+)

The biggest visual change Apple has introduced, announced at WWDC 2025. The largest design refresh since iOS 7 in 2013.

| Item | Content |
|------|---------|
| **Core concepts** | Translucency, depth, fluid responsiveness |
| **Coverage** | Across iOS 26, iPadOS 26, macOS 26, watchOS 26, tvOS 26 |
| **Color palette** | Refined colors, left-aligned bold typography, concentric rhythm |
| **System integration** | Tab Bar, Toolbar, System Font automatically adapt to Dark Mode, Dynamic Type, and Liquid Glass |

**Design principles:**
- Prefer system components (Tab Bar, Toolbar, System Font) — they auto-adapt to Liquid Glass, Dark Mode, and Dynamic Type
- Opacity and blur layer on top of content to produce depth
- Consider the integrated rhythm (concentricity) between hardware and software

#### iOS Key Numbers

| Item | Value | Rationale |
|------|-------|-----------|
| **Minimum touch target** | 44×44pt | Apple accessibility research: anything smaller causes ≥25% of users to mis-tap |
| **Safe Area** | Avoid notch / Dynamic Island / Home Indicator regions | Prevents overlap with system UI |
| **Dynamic Type** | Support 11 text sizes | Honor user preferences |
| **Minimum font size** | 11pt (body: 17pt recommended) | Readability |

### 1.2 Material Design 3 (Android)

Google's Material Design 3 uses color, size, shape, and containment to guide users to core elements.

#### Material 3 Expressive (Android 16, 2025+)

The next-generation Material Design announced at Google I/O 2025. A bolder, more expressive design language.

| Item | Content |
|------|---------|
| **Spring animation** | Physics-based bounce for natural interaction |
| **Bold typography** | Bigger, bolder text strengthens visual hierarchy |
| **Dynamic Color** | Material You's personalized color system |
| **Shape** | Diverse forms from rounded corners to superellipses |

#### Android Key Numbers

| Item | Value | Rationale |
|------|-------|-----------|
| **Minimum touch target** | 48×48dp | Material Design accessibility guidelines |
| **Base spacing unit** | 8dp increments | Google UX research: uniform padding raises task completion by 16% |
| **Bottom navigation** | 3–5 items | Place core destinations in the thumb zone |
| **Minimum font size** | 12sp (body: 14sp recommended) | Material typography guide |

### 1.3 Cross-Platform Integration Principles

When supporting both platforms:

| Principle | Description | Example |
|-----------|-------------|---------|
| **Respect platform conventions** | Follow each OS's native pattern | iOS: back swipe; Android: system back button |
| **Maintain brand consistency** | Unify color, logo, tone & manner | Custom button styles identical on both |
| **Adaptive components** | Convert automatically by platform | iOS: ActionSheet; Android: BottomSheet |
| **Common UX patterns** | Make core user experiences identical | Unified payment, onboarding, search flows |

---

## 2. Touch Interaction & Gesture Design

### 2.1 Thumb Zone

Core interactive elements in mobile apps must be placed within the **thumb zone**.

```
┌────────────────────┐
│    😰 Hard zone     │   ← Hard to reach with one hand
│   (top corners)     │
├────────────────────┤
│   😐 OK zone        │   ← Reachable with some effort
│   (middle area)     │
├────────────────────┤
│   😊 Easy zone      │   ← Naturally reachable
│   (bottom center→  │      Best for core actions
│    right)           │
└────────────────────┘
```

**Design rules:**
- **CTA buttons**: place in the bottom third of the screen
- **Navigation**: use a bottom tab bar or bottom sheet
- **Dangerous actions** (delete, etc.): place outside the thumb zone to prevent mistakes
- **FAB (Floating Action Button)**: place at the bottom right (optimal for right-handed users)

### 2.2 Standard Gesture Mapping

| Gesture | Action | Use case | Caution |
|---------|--------|----------|---------|
| **Tap** | Select, activate | Buttons, links, cards | Touch target ≥ 44pt/48dp |
| **Double tap** | Zoom / like | Image zoom, SNS like | Avoid collision with single tap |
| **Long press** | Context menu | Edit mode, multi-select | Activates after ≥ 500ms |
| **Swipe (horizontal)** | Screen transition, delete | Card paging, mail delete | Always provide Undo |
| **Swipe (vertical)** | Scroll, refresh | List browsing, pull-to-refresh | Avoid collision with system gestures |
| **Pinch** | Zoom in/out | Maps, image gallery | Also support double-tap to zoom |
| **Drag** | Move, reorder | List reorder, sliders | Visual feedback during movement is mandatory |

**Expert tips:**
- Don't make a gesture the only undiscoverable interaction — always provide a button alternative
- Avoid collisions with system gestures (iOS back swipe, Android system back)
- On gesture recognition, provide **immediate and clear feedback** (visual + haptic)
- The same gesture should perform a **consistent action** across the entire app

### 2.3 Touch Feedback Design

| Level | Duration | Applies to | Example |
|-------|----------|------------|---------|
| **Visual** | Immediate (~100ms) | Every touchable element | Ripple, color change, scale(0.95) |
| **Haptic** | Immediate | Important state change | Toggle switch, item deletion confirmation |
| **Animation** | 150–300ms | State transitions | Page transition, modal open |
| **Sound** | Immediate | Special events (optional) | Payment success, message sent |

---

## 3. Navigation Patterns

### 3.1 Bottom Tab Bar

The **standard top-level navigation** for mobile apps. First-choice pattern recommended by both platforms.

| Item | Recommendation |
|------|----------------|
| **Number of items** | 3–5 (an odd count helps visual rhythm) |
| **Icons** | Simple geometric forms, universally recognizable |
| **Labels** | Icon + 1-word label (accessibility) |
| **Active indication** | Color change + filled-icon variant in tandem |
| **Badges** | Red dot or number for unseen items |

**Expert tips:**
- The bottom tab is in the thumb zone, ideal for one-handed use
- Re-tap on active tab → scroll the section to top (Instagram pattern)
- Preserve state across tab switches (scroll position, input)
- iOS calls it Tab Bar, Android calls it Navigation Bar

### 3.2 Navigation Drawer

A pattern for secondary navigation or rarely used features such as settings.

| Item | Recommendation |
|------|----------------|
| **Use case** | More than 5 destinations, secondary features, settings |
| **Trigger** | Hamburger icon (☰) or left-edge swipe |
| **Placement** | Slide from the left (both iOS/Android) |
| **Caution** | Don't hide core features in the drawer |

**Hybrid strategy:** Bottom tab bar (core 3–5) + drawer (the rest) is the most effective combination

### 3.3 Bottom Sheet

A mobile-optimized pattern that temporarily shows important information and is easy to dismiss.

| Type | Description | Use case |
|------|-------------|----------|
| **Modal** | Dim background, blocks interaction | Option selection, confirmation, share |
| **Non-modal** | Background remains interactive | Map details, music player |
| **Expandable** | Drag-adjustable height | Map app details (Apple Maps, Google Maps) |

**Design rules:**
- Place a drag handle (pill bar) at the top to afford dismissal
- Must close via the back button/gesture too (avoid confusion)
- Start at ≤ 50% screen height (expand as needed)
- If scrolling content is present, clearly distinguish in-sheet scroll vs. sheet-dismiss gestures

### 3.4 Navigation Rail

A vertical navigation placed on the left for tablets and foldables.

| Item | Recommendation |
|------|----------------|
| **Activation condition** | Screen width ≥ 600dp (tablet, foldable opened) |
| **Placement** | Pinned to the left, 80dp wide |
| **Switching rule** | On a phone, use bottom tabs → on a tablet, switch to Navigation Rail automatically |

---

## 4. Typography & Visual Hierarchy

### 4.1 Typography Scale

| Role | iOS (pt) | Android (sp) | Purpose |
|------|----------|--------------|---------|
| **Display Large** | 34 Bold | 57 Regular | Hero section title |
| **Display Small** | 28 Bold | 36 Regular | Major section title |
| **Headline** | 22 Bold | 28 Regular | Card titles, primary content headers |
| **Title** | 20 Semibold | 22 Medium | Subsections, modal titles |
| **Body** | 17 Regular | 14–16 Regular | Body text, descriptions, general content |
| **Callout** | 16 Regular | 14 Medium | Emphasized text, labels |
| **Caption** | 12 Regular | 12 Regular | Secondary descriptions, timestamps |
| **Footnote** | 11 Regular | 11 Regular | Minimum-size guide text |

### 4.2 Building Visual Hierarchy

```
┌─────────────────────────────────────┐
│  ★ 1st: size + weight               │   Display / Headline
│  ────────────────────────────        │
│  ★ 2nd: color contrast              │   Primary vs Secondary color
│  ────────────────────────────        │
│  ★ 3rd: spacing (whitespace)        │   Margin / Padding
│  ────────────────────────────        │
│  ★ 4th: position                    │   top → bottom, left → right
│  ────────────────────────────        │
│  ★ 5th: decoration                  │   underlines, badges, icons
└─────────────────────────────────────┘
```

**Expert tips:**
- Use at most **4 levels** of font size on a screen (more becomes cluttered)
- Line height should be **1.4–1.6×** the font size (optimal for mobile readability)
- Tighten letter-spacing slightly for large text (-0.5%), loosen it slightly for small text (+1–2%)
- **Prefer System Fonts**: iOS SF Pro, Android Roboto — guarantees rendering optimization and accessibility
- Use custom fonts only when brand identity demands; choose Variable Fonts to optimize file size

### 4.3 Hangul Typography Considerations

| Item | Recommendation |
|------|----------------|
| **Minimum size** | 12pt/14sp (recommended 2pt larger than Latin) |
| **Line height** | 1.6–1.8× the font size (Hangul needs more vertical space) |
| **Letter spacing** | 0 to +2% (Hangul reads better with generous default spacing) |
| **Recommended fonts** | Pretendard (Variable), Noto Sans KR, Spoqa Han Sans Neo |
| **Mixed text** | Latin and Hangul baselines differ, so vertical-align tuning is needed |

---

## 5. Color System & Dark Mode

### 5.1 Semantic Color Tokens

Define colors by **semantic role**, not as absolute values.

| Role | Light Mode | Dark Mode | Purpose |
|------|------------|-----------|---------|
| **surface** | #FFFFFF | #121212 | Base background |
| **on-surface** | #1C1B1F | #E6E1E5 | Text on surface |
| **surface-variant** | #F5F5F5 | #1E1E1E | Card / section background |
| **primary** | brand color | lighter variant | CTA, active state |
| **on-primary** | #FFFFFF | #000000 | Text on primary |
| **error** | #B3261E | #F2B8B5 | Error messages |
| **outline** | #79747E | #938F99 | Borders, dividers |

### 5.2 Dark Mode Design Principles

Dark mode is not a simple color inversion of light mode. Each inversion is a **deliberate design decision**.

| Principle | Description |
|-----------|-------------|
| **Surface elevation hierarchy** | Higher elevation → brighter surface (express depth in dark mode) |
| **Reduce saturation** | High-saturation colors on dark backgrounds cause eye strain → reduce saturation by 10–20% |
| **Honor contrast ratios** | Minimum 4.5:1 for text (WCAG AA); 3:1 for large text |
| **Avoid pure black** | Use #121212 instead of #000000 — pure black causes smearing on OLED |
| **System-setting integration** | Auto-reflect OS dark mode via the `prefers-color-scheme` media query |

**Expert tips:**
- Shadows lose effect in dark mode → use **surface color layering** to express depth instead
- Apply a subtle transparent overlay (5–15% white) on images to harmonize with dark backgrounds
- Use 87% transparency instead of pure white (#FFFFFF) for body text to reduce eye strain

---

## 6. Design Token System

### 6.1 Token Hierarchy

```
┌─────────────────────────────────────────────┐
│  Reference Token (raw value)                 │
│  e.g., color.blue.500 = #2196F3              │
├─────────────────────────────────────────────┤
│  Semantic Token (assigned meaning)           │
│  e.g., color.primary = color.blue.500        │
│        color.primary.dark = color.blue.200   │
├─────────────────────────────────────────────┤
│  Component Token (component-specific)        │
│  e.g., button.background = color.primary     │
│        button.text = color.on-primary        │
└─────────────────────────────────────────────┘
```

### 6.2 Token Implementation per Framework

#### React Native (TypeScript)

```typescript
// design-tokens.ts
export const tokens = {
  color: {
    primary: '#2196F3',
    onPrimary: '#FFFFFF',
    surface: '#FFFFFF',
    onSurface: '#1C1B1F',
    error: '#B3261E',
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  },
  radius: {
    sm: 4,
    md: 8,
    lg: 16,
    full: 9999,
  },
  typography: {
    displayLarge: { fontSize: 34, fontWeight: '700', lineHeight: 41 },
    headline: { fontSize: 22, fontWeight: '700', lineHeight: 28 },
    body: { fontSize: 17, fontWeight: '400', lineHeight: 24 },
    caption: { fontSize: 12, fontWeight: '400', lineHeight: 16 },
  },
} as const;
```

#### Flutter (Dart)

```dart
// design_tokens.dart
class DesignTokens {
  // Colors
  static const Color primary = Color(0xFF2196F3);
  static const Color onPrimary = Color(0xFFFFFFFF);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color onSurface = Color(0xFF1C1B1F);
  static const Color error = Color(0xFFB3261E);

  // Spacing
  static const double spacingXs = 4.0;
  static const double spacingSm = 8.0;
  static const double spacingMd = 16.0;
  static const double spacingLg = 24.0;
  static const double spacingXl = 32.0;

  // Border Radius
  static const double radiusSm = 4.0;
  static const double radiusMd = 8.0;
  static const double radiusLg = 16.0;
}
```

#### Kotlin Multiplatform (Compose)

```kotlin
// DesignTokens.kt
object DesignTokens {
    object Colors {
        val primary = Color(0xFF2196F3)
        val onPrimary = Color(0xFFFFFFFF)
        val surface = Color(0xFFFFFFFF)
        val onSurface = Color(0xFF1C1B1F)
        val error = Color(0xFFB3261E)
    }

    object Spacing {
        val xs = 4.dp
        val sm = 8.dp
        val md = 16.dp
        val lg = 24.dp
        val xl = 32.dp
    }

    object Radius {
        val sm = 4.dp
        val md = 8.dp
        val lg = 16.dp
    }
}
```

### 6.3 Token Categories

| Category | Example tokens | Description |
|----------|----------------|-------------|
| **Color** | `color.primary`, `color.surface`, `color.error` | Brand, background, semantic colors |
| **Spacing** | `spacing.xs(4)` ~ `spacing.xl(32)` | Whitespace system based on multiples of 8dp |
| **Typography** | `typography.body`, `typography.headline` | Font size + weight + line height |
| **Radius** | `radius.sm(4)` ~ `radius.full(9999)` | Corner roundness |
| **Shadow/Elevation** | `elevation.level1` ~ `elevation.level5` | Depth (light mode) |
| **Duration** | `duration.fast(150ms)`, `duration.normal(300ms)` | Animation duration |
| **Easing** | `easing.standard`, `easing.decelerate` | Animation curves |

---

## 7. Mobile Form Design

### 7.1 Core Principles

Forms are the **biggest drop-off area** on mobile. As of 2025, 82% of users expect to complete a core form on mobile (up from 67% in 2024).

| Principle | Description |
|-----------|-------------|
| **Single-column layout** | A 1-column structure that matches mobile scrolling (no multi-column) |
| **Minimum fields** | Remove unnecessary input fields — every field removed lifts conversion |
| **Logical grouping** | Group related fields visually to reduce cognitive load |
| **Progress indication** | Multi-step forms need a progress bar or step indicator |

### 7.2 Keyboard Type Mapping

Setting the right keyboard type **2–3x** speeds up input.

| Input type | iOS keyboardType | Android inputType | inputMode (Web) |
|------------|------------------|-------------------|-----------------|
| **Email** | `emailAddress` | `textEmailAddress` | `email` |
| **Phone** | `phonePad` | `phone` | `tel` |
| **Number (integer)** | `numberPad` | `number` | `numeric` |
| **Amount (decimal)** | `decimalPad` | `numberDecimal` | `decimal` |
| **URL** | `URL` | `textUri` | `url` |
| **Password** | `default` + `secureTextEntry` | `textPassword` | — |
| **Search** | `webSearch` | `text` (+ `imeOptions=search`) | `search` |

### 7.3 Validation Strategy

| Strategy | Timing | Applies to | Pros |
|----------|--------|------------|------|
| **Blur validation** | On focus loss | Most input fields | Doesn't interrupt typing |
| **Live validation** | On every keystroke | Password strength, username duplication | Immediate feedback |
| **Submit validation** | On form submit | Complex / server-side rules | Network-efficient |

**Expert tips:**
- Error messages should be **specific and actionable** — "Invalid input" ✕ → "Email address needs an @ symbol" ○
- Provide feedback on success too (green check, subtle animation)
- **Enable Autofill**: apply proper autocomplete attributes to name, email, phone, address, payment info → 30%+ uplift in completion
- Required/optional marking: instead of marking required fields with `*`, label optional fields with "(optional)" — since most are required, marking the minority is efficient

### 7.4 Mobile Form Anti-Patterns

| Anti-pattern | Problem | Correct alternative |
|--------------|---------|---------------------|
| **Placeholder as label** | Label disappears on input → context lost | Use floating labels |
| **Auto focus advance** | Removes user control | Let the user move to the next field |
| **Custom dropdown** | Harder than native pickers | Use native Select / Picker |
| **Inline-only errors** | Errors hidden by scroll go unnoticed | Pair an error summary with auto-scroll |

---

## 8. Animation & Motion

### 8.1 Motion Design Principles

| Principle | Description | Example |
|-----------|-------------|---------|
| **Functional** | Animation must convey information | Page-transition direction → hierarchy relation |
| **Natural** | Mimic physical laws | Spring animation, deceleration curves |
| **Immediate** | React instantly to user action | Touch feedback within 100ms |
| **Restrained** | Excess motion impedes | ≤ 2 concurrent animations on a screen |

### 8.2 Animation Duration Guide

| Type | Duration | Example |
|------|----------|---------|
| **Micro feedback** | 50–150ms | Button press, ripple |
| **State transition** | 150–300ms | Toggle, checkbox, tab switch |
| **Screen transition** | 250–400ms | Page navigation, modal open |
| **Composite animation** | 300–600ms | Card expansion, list-item entry |
| **Decorative** | 600–1000ms | Onboarding illustrations, celebration effects |

### 8.3 Easing Curve Selection

| Curve | Mathematical form | Use |
|-------|-------------------|-----|
| **Standard (ease-in-out)** | `cubic-bezier(0.4, 0, 0.2, 1)` | General movement, size change |
| **Decelerate (ease-out)** | `cubic-bezier(0, 0, 0.2, 1)` | Elements entering the screen |
| **Accelerate (ease-in)** | `cubic-bezier(0.4, 0, 1, 1)` | Elements leaving the screen |
| **Spring** | Physics-based (damping, stiffness) | M3 Expressive, iOS natural bounce |

**Expert tips:**
- **Must** support the `prefers-reduced-motion: reduce` media query — cater to motion-sensitive users
- List-item entry animations apply **stagger** — each item enters in sequence with a 30–50ms offset
- Using Lottie lets designers create complex animations in After Effects and play them at native performance
- If an animation cannot sustain 60fps, remove it — stuttering animation is worse than none

---

## 9. Haptic Feedback

### 9.1 Haptic Design Principles

Haptics are "invisible design" that, used correctly, dramatically improve an app's **physical tangibility**.

| Principle | Description |
|-----------|-------------|
| **Causal** | Haptics must be a **direct result** of user action |
| **Synchronous** | Fire at **exactly the same moment** as the visual/auditory event (animation peak, button press) |
| **Restrained** | Good haptics don't demand attention; they guide and confirm |
| **Consistent** | Use the same haptic pattern for the same kind of event |

### 9.2 Haptic Types and Applications

| Type | iOS (UIFeedbackGenerator) | Android (HapticFeedbackConstants) | Use case |
|------|---------------------------|-----------------------------------|----------|
| **Selection** | `UISelectionFeedbackGenerator` | `CLOCK_TICK` | Picker scroll, segment switch |
| **Light Impact** | `.light` | `CONTEXT_CLICK` | Toggle switch, checkbox |
| **Medium Impact** | `.medium` | `VIRTUAL_KEY` | Button tap, list-item select |
| **Heavy Impact** | `.heavy` | `LONG_PRESS` | Drag-and-drop start/end |
| **Success** | `UINotificationFeedbackGenerator.success` | Custom pattern | Task complete, payment success |
| **Warning** | `.warning` | Custom pattern | Warning, limit reached |
| **Error** | `.error` | `REJECT` | Invalid input, failure |

**Expert tips:**
- Multimodal design: orchestrate visual + auditory + haptic together — sight/sound reinforce haptic perception
- A subtle `selection` haptic when reaching a snap point during scrolling adds physical click feel
- **Avoid excessive haptics**: haptics on every touch are annoying. Apply only to interactions with state changes
- Provide a setting for users to disable haptics

---

## 10. Onboarding & First Impressions

### 10.1 Onboarding Patterns

The first experience determines retention. **70%** of users churn within the first session due to confusing or long onboarding. Conversely, well-designed onboarding lifts retention by **50%+**.

| Pattern | Description | Best fit |
|---------|-------------|----------|
| **Progressive Onboarding** | Introduce features step by step; advanced features later | Complex productivity apps (Notion, Figma) |
| **Coach Marks** | Point at specific UI elements with explanations | Apps with unique interactions |
| **Welcome Carousel** | 3–5 slides communicating core value | Apps where brand story matters |
| **Personalization** | Collect preferences/goals first to tailor | Content / recommendation apps (Spotify, TikTok) |
| **Interactive Tutorial** | Guide the first task inside the actual app | Tool-style apps (Canva, Duolingo) |

### 10.2 Onboarding Design Principles

| Principle | Description |
|-----------|-------------|
| **Allow Skip** | Always offer a skip option — for returning or power users |
| **≤ 3 steps** | At most 3 onboarding steps. Spread the rest progressively |
| **Value first** | Communicate "why this app is useful" before explaining features |
| **Experience immediately** | When possible, let the user try the app before account creation (lazy registration) |
| **2-second rule** | Loading ≤ 2 seconds — beyond that, retention drops 31% |

### 10.3 Splash & Loading

| Element | Recommendation |
|---------|----------------|
| **Splash screen** | Brand logo only, kept simple. Max 1–2 seconds |
| **Skeleton UI** | Same shape as the actual layout. Hints at content positions |
| **Shimmer effect** | A left-to-right gradient animation conveys "alive" |
| **Step-wise messages** | For long loading, show status messages like "Loading data..." |

---

## 11. Performance UX

### 11.1 Optimizing Perceived Performance

The speed users **feel** matters more than the actual speed.

| Strategy | Description | Effect |
|----------|-------------|--------|
| **Optimistic update** | Reflect UI before server response | Immediate reactivity |
| **Skeleton UI** | Show layout skeleton instead of an empty screen | ~30% reduction in perceived wait |
| **Progressive image loading** | Blurred image → sharp image | Prevents empty spaces |
| **Infinite-scroll prefetch** | Pre-load the next page before reaching the bottom | Seamless exploration |
| **Asset preload** | Pre-load next-screen assets on the current screen | Instant transitions |

### 11.2 Per-Framework Performance Benchmarks

| Metric | React Native (New Arch) | Flutter | Native |
|--------|-------------------------|---------|--------|
| **Cold start** | ~1.2s | ~0.8s | ~0.5s |
| **Avg frame time** | ~18ms | ~17ms | ~16ms |
| **Jank rate** | ~3% | ~1.4% | <1% |
| **Memory usage** | Medium | Lowest | Low |

### 11.3 Performance Optimization Checklist

- [ ] Lists use virtualization (VirtualizedList/ListView) — constant memory even with thousands of items
- [ ] Resize images to appropriate resolutions + use WebP/AVIF
- [ ] Prevent unnecessary re-renders (React: `React.memo`, Flutter: `const` widgets)
- [ ] Move heavy compute off the main thread (Isolate/Worker)
- [ ] Monitor bundle size — affects initial load
- [ ] Set a network request caching strategy (SWR / Stale-While-Revalidate)
- [ ] Animations use the native driver / Impeller (avoid the JS thread)

---

## 12. Accessibility

### 12.1 Legal Requirements

With the EU Accessibility Act (EAA) taking effect in June 2025, mobile-app accessibility is now a **legal obligation**. WCAG 2.1/2.2 is the global standard; Korea follows the "Act on Anti-Discrimination Against Persons with Disabilities" and "Korean Web Content Accessibility Guidelines 2.2".

### 12.2 Screen Reader Support

| Platform | Screen reader | Key requirements |
|----------|---------------|------------------|
| **iOS** | VoiceOver | `accessibilityLabel` on every UI element, alt text on images, gesture alternatives |
| **Android** | TalkBack | `contentDescription` set, logical focus order, touch-exploration support |

### 12.3 Accessibility Checklist

| Category | Item | Criterion |
|----------|------|-----------|
| **Touch target** | Minimum size | 44×44pt (iOS) / 48×48dp (Android) |
| **Color contrast** | Normal text | ≥ 4.5:1 (WCAG AA) |
| **Color contrast** | Large text (≥ 18pt) | ≥ 3:1 |
| **Color dependency** | Don't convey info by color alone | Pair with icons, text, patterns |
| **Text size** | Support Dynamic Type / font scaling | Up to 200% scaling |
| **Motion** | Respect reduced-motion preference | Honor `prefers-reduced-motion` |
| **Focus** | Logical focus order | Natural left→right, top→bottom navigation |
| **Alt text** | Decorative images get empty labels | Informational images get descriptive labels |
| **Time limits** | Auto-advancing slides/timers | Pausable / extendable |
| **Orientation** | Support both portrait/landscape | Honor user preference |

### 12.4 Per-Framework Accessibility Implementation

| Framework | Label | Role | Hint |
|-----------|-------|------|------|
| **React Native** | `accessibilityLabel` | `accessibilityRole` | `accessibilityHint` |
| **Flutter** | `Semantics(label:)` | `Semantics(button:true)` | `Semantics(hint:)` |
| **KMP (Compose)** | `contentDescription` | `Role.Button` | `stateDescription` |

---

## 13. Per-Framework Implementation Strategies

### 13.1 React Native / Expo

| Area | Recommended library | Description |
|------|---------------------|-------------|
| **Navigation** | Expo Router (file-based) | Next.js-style routing |
| **State management** | Zustand + TanStack Query | Separate client/server state |
| **Animation** | React Native Reanimated | Native-thread animation (60fps) |
| **Gesture** | React Native Gesture Handler | Native gesture recognition |
| **Design system** | Tamagui / NativeWind / Gluestack UI | Compile-time style optimization |
| **Icons** | @expo/vector-icons | 6,000+ icons (MaterialIcons, Ionicons, etc.) |
| **Images** | expo-image | Caching, progressive loading, BlurHash |
| **Haptics** | expo-haptics | Unified iOS/Android haptic API |
| **Lottie** | lottie-react-native | After Effects animation playback |

**Architecture pattern:**
```
src/
├── app/              # Expo Router file-based routing
│   ├── (tabs)/       # Tab navigation group
│   ├── (auth)/       # Auth flow group
│   └── _layout.tsx   # Root layout
├── components/       # Reusable UI components
│   ├── ui/           # Atomic UI (Button, Input, Card)
│   └── features/     # Feature-specific composite components
├── hooks/            # Custom hooks
├── stores/           # Zustand stores
├── services/         # API layer
├── styles/           # Design tokens, theme
└── utils/            # Utility functions
```

### 13.2 Flutter

| Area | Recommended package | Description |
|------|---------------------|-------------|
| **Navigation** | GoRouter | Declarative routing, deep-link support |
| **State management** | Riverpod / Bloc | Reactive / event-driven state management |
| **Animation** | Built-in Flutter + Rive | Impeller rendering engine (60fps+) |
| **Design system** | Material 3 / Cupertino / Adaptive | Platform-adaptive widgets |
| **Images** | cached_network_image | Caching, placeholders, error handling |
| **Haptics** | HapticFeedback class (built-in) | Unified iOS/Android |
| **Lottie** | lottie package | After Effects animation |
| **Data models** | Freezed + json_serializable | Auto-generated immutable data classes |

**Architecture pattern (feature-first):**
```
lib/
├── app/                    # App entry, router setup
├── core/                   # Common utilities, constants, extensions
│   ├── theme/              # ThemeData, design tokens
│   ├── network/            # Dio/http setup
│   └── utils/              # Common utilities
├── features/               # Per-feature directories
│   ├── auth/
│   │   ├── data/           # Repository impl, data sources
│   │   ├── domain/         # Entities, use cases
│   │   └── presentation/   # Widgets, providers/Bloc
│   └── home/
└── shared/                 # Shared widgets, models
```

### 13.3 Kotlin Multiplatform (Compose Multiplatform)

| Area | Recommended library | Description |
|------|---------------------|-------------|
| **Navigation** | Voyager / Decompose | Multiplatform navigation |
| **State management** | MVI + StateFlow | Kotlin-Flow reactive |
| **DI** | Koin | Multiplatform dependency injection |
| **Network** | Ktor | Multiplatform HTTP client |
| **DB** | SQLDelight | Multiplatform typesafe SQL |
| **Design system** | Material Design 3 (Compose) | Compose Material 3 theming |
| **Images** | Coil (Compose) | Native Compose image loader |
| **Serialization** | kotlinx.serialization | Multiplatform JSON serialization |

**Architecture pattern (shared + platform):**
```
project/
├── shared/                        # Shared business logic
│   └── src/
│       ├── commonMain/            # Common code
│       │   ├── domain/            # Entities, use cases
│       │   ├── data/              # Repository, network
│       │   └── presentation/      # ViewModel (StateFlow)
│       ├── androidMain/           # Android expect implementations
│       └── iosMain/               # iOS expect implementations
├── composeApp/                    # Compose Multiplatform UI
│   └── src/
│       ├── commonMain/            # Shared Compose UI
│       │   ├── theme/             # Material 3 theme
│       │   ├── components/        # Shared components
│       │   └── screens/           # Screen Composables
│       ├── androidMain/           # Android-only UI
│       └── iosMain/               # iOS-only UI
└── build.gradle.kts
```

---

## 14. Expert Know-How — What Makes an App Polished

### 14.1 The "Last 10%" — from Basic to Pro

The difference between an average and a polished app lies not in features but in **polish quality**.

#### Visual Polish

| Element | Amateur | Pro |
|---------|---------|-----|
| **Shadow** | Black drop-shadow | Surface-color layering + subtle colored shadows |
| **Corners** | Inconsistent radii | Unified radius scale (4/8/12/16/24) |
| **Spacing** | Arbitrary pixel values | Consistent spacing on an 8dp grid |
| **Color** | Pure black/white | Subtle tones (#121212, #F8F8F8) |
| **Icons** | Mixed styles | A single icon set (filled or outlined, no mixing) |
| **Images** | Raw originals | Consistent ratios + containers + loading placeholders |

#### Interaction Polish

| Element | Amateur | Pro |
|---------|---------|-----|
| **Transition** | Pops in/out instantly | Directional fade/slide (250–400ms) |
| **Touch response** | None | Ripple + scale(0.97) + haptic |
| **Loading** | Empty screen → suddenly content | Skeleton → fade-in |
| **Error** | `alert("Error")` | Inline error + retry + preserved context |
| **Empty state** | Blank screen or "No data" | Illustration + description + CTA |
| **Keyboard** | Hides input fields | Auto-scroll + `KeyboardAvoidingView` |

### 14.2 Details That Build Trust

| Detail | Implementation | UX effect |
|--------|----------------|-----------|
| **Scroll elasticity** | System default bounce (iOS), overscroll (Android) | Physical tangibility |
| **Custom pull-to-refresh** | Customize with brand logo/animation | Brand reinforcement |
| **Edge-case handling** | Offline, empty state, long text, multi-line | Stability and polish |
| **Transition continuity** | Shared Element Transition (iOS Hero, Android) | Spatial context retention |
| **State preservation** | Keep scroll/input state across tab switches and background returns | Task continuity |
| **Dark-mode images** | Reduce image brightness by 5–15% in dark mode | Reduced eye strain |

### 14.3 Anti-Patterns — Strictly Avoid

| Anti-pattern | Problem | Correct alternative |
|--------------|---------|---------------------|
| **Animation everywhere** | Distracting, performance drop, accessibility issues | Use meaningful motion only for state change |
| **Custom scrollbar** | Breaks native scroll physics | Keep system scroll |
| **Ads/messages in splash** | Wrecks first impressions, churn spikes | Brand logo only for 1–2 seconds |
| **Immediate notification permission request** | Permission without context = denial | Explain value first, then ask (Just-in-Time) |
| **Hardcoded inline styles** | Breaks consistency, no dark-mode support | Use a design-token system |
| **Infinite loading spinner** | Perceived as the app hanging | Timeout + retry + offline handling |
| **Excessive permission requests** | Loss of trust | Ask for minimum permission at the moment needed |
| **Ignore Back button** | Confuses Android users | Always honor the system Back action |

### 14.4 Polished-App Checklist

```
Foundations (Must-Have)
├── [ ] Consistent design-token system (color, spacing, type, radius)
├── [ ] Full dark-mode support (auto-reflects system setting)
├── [ ] Accessibility (screen reader, touch target, contrast)
├── [ ] Keyboard avoidance (KeyboardAvoidingView)
├── [ ] Three-state set: error / empty / loading
├── [ ] Safe Area handling (notch, Dynamic Island, home indicator)
└── [ ] Offline / network handling

Polish (Nice-to-Have)
├── [ ] Skeleton UI + shimmer loading
├── [ ] Meaningful haptic feedback
├── [ ] Shared Element Transition
├── [ ] List-item stagger animation
├── [ ] Swipe actions + Undo
├── [ ] Progressive image loading (BlurHash → original)
└── [ ] prefers-reduced-motion support

Delight
├── [ ] Custom pull-to-refresh animation
├── [ ] Lottie animation on success/celebration
├── [ ] State preservation (tab switch, background return)
├── [ ] Context-aware permission requests (Just-in-Time)
└── [ ] Progressive onboarding (coach marks)
```

---

## References

### Official platform guides
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Apple — Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios)
- [Material Design 3](https://m3.material.io/)
- [Android Design — Layouts and Navigation](https://developer.android.com/design/ui/mobile/guides/layout-and-content/layout-and-nav-patterns)

### UX/UI design guides
- [Mobile UX Design: The Ultimate Guide 2026 (UXCam)](https://uxcam.com/blog/mobile-ux/)
- [11 Proven Mobile App UI/UX Design Principles for 2026](https://www.designstudiouiux.com/blog/principles-mobile-app-design/)
- [Mastering Mobile App Design: Comprehensive In-Depth Guide 2026](https://www.designstudiouiux.com/blog/mobile-app-design-comprehensive-guide/)
- [Mobile Navigation UX Best Practices, Patterns & Examples (2026)](https://www.designstudiouiux.com/blog/mobile-navigation-ux/)
- [Bottom Sheets: Definition and UX Guidelines (NN/g)](https://www.nngroup.com/articles/bottom-sheet/)

### Interaction & haptics
- [2025 Guide to Haptics: Enhancing Mobile UX with Tactile Feedback](https://saropa-contacts.medium.com/2025-guide-to-haptics-enhancing-mobile-ux-with-tactile-feedback-676dd5937774)
- [Haptics Design Principles (Android)](https://developer.android.com/develop/ui/views/haptics/haptics-principles)
- [10 Gesture UI Design Tips for iOS & Android Apps](https://www.zeepalm.com/blog/10-gesture-ui-design-tips-for-ios-and-android-apps)

### Onboarding & retention
- [App Onboarding Guide — Top 10 Onboarding Flow Examples 2026](https://uxcam.com/blog/10-apps-with-great-user-onboarding/)
- [Mobile Onboarding UX: 11 Best Practices for Retention (2026)](https://www.designstudiouiux.com/blog/mobile-app-onboarding-best-practices/)
- [12 Mobile App Design Patterns That Boost Retention](https://procreator.design/blog/mobile-app-design-patterns-boost-retention/)

### Accessibility
- [Mobile App Accessibility: A Comprehensive Guide (2026)](https://www.accessibilitychecker.org/guides/mobile-apps-accessibility/)
- [Mobile App Accessibility in 2025 (Adapptor)](https://www.adapptor.com.au/blog/mobile-app-accessibility-in-2025)

### Form design
- [Best Practices for Mobile Form Design (Smashing Magazine)](https://www.smashingmagazine.com/2018/08/best-practices-for-mobile-form-design/)
- [Mobile Form Best Practices (IvyForms)](https://ivyforms.com/blog/mobile-form-best-practices/)
- [The Ultimate Guide to Mobile Form Design: 17 Best Practices](https://www.marketingscoop.com/marketing/the-ultimate-guide-to-mobile-form-design-17-best-practices-for-2024/)

### Design tokens
- [Design Tokens beyond colors, typography, and spacing (Bumble Tech)](https://medium.com/bumble-tech/design-tokens-beyond-colors-typography-and-spacing-ad7c98f4f228)
- [Color Tokens: Guide to Light and Dark Modes (Bootcamp)](https://medium.com/design-bootcamp/color-tokens-guide-to-light-and-dark-modes-in-design-systems-146ab33023ac)

### Framework comparison
- [Flutter vs React Native vs Native: 2025 Performance Benchmark](https://www.synergyboat.com/blog/flutter-vs-react-native-vs-native-performance-benchmark-2025)
- [Flutter vs React Native: Complete 2025 Framework Comparison](https://www.thedroidsonroids.com/blog/flutter-vs-react-native-comparison)
