# UX/UI Interaction Patterns — Comprehensive Guide

> A reference document systematically organizing interaction patterns that deliver excellent user experience in web and mobile applications

---

## Table of Contents

1. [Micro-interactions](#1-micro-interactions)
2. [Navigation Patterns](#2-navigation-patterns)
3. [Feedback & Response](#3-feedback--response)
4. [Gesture-based Interactions](#4-gesture-based-interactions)
5. [Scroll Interactions](#5-scroll-interactions)
6. [Form Interactions](#6-form-interactions)
7. [Transition & Animation](#7-transition--animation)
8. [Onboarding](#8-onboarding)
9. [Accessibility Interactions](#9-accessibility-interactions)
10. [Delight Patterns](#10-delight-patterns)
11. [Dark Patterns — Things to Avoid](#11-dark-patterns--things-to-avoid)

---

## 1. Micro-interactions

Micro-interactions are small, precise, momentary interactions focused on a single task. They follow the 4-stage structure of Trigger → Rules → Feedback → Loops & Modes (Dan Saffer, 2013).

### 1.1 Button Feedback

| Item | Content |
|------|---------|
| **Description** | A pattern that provides visual and tactile reactions when the user presses a button. Includes press effect (scale down), color change, ripple effect, etc. |
| **UX principle** | **Feedback Principle** — the system should show an immediate reaction to every user action. A response within 100ms is perceived as "immediate" (Jakob Nielsen). |
| **Platform** | Both (Web + Mobile) |
| **Implementation complexity** | Low |
| **Real-world examples** | Material Design's Ripple Effect (all Google products), iOS button highlight state, Stripe's button loading animation |

**Implementation tips:**
- Combine `transform: scale(0.95)` with `transition: 150ms ease` for a natural press effect
- Apply visual change on `:active` pseudo-class; keep the focus ring on `:focus-visible`
- On mobile, use `touch-action: manipulation` to remove the 300ms tap delay
- For disabled buttons, apply `opacity: 0.4` + `pointer-events: none`

### 1.2 Toggle Animation

| Item | Content |
|------|---------|
| **Description** | A pattern that clearly conveys state change via animation (slide, color change, icon morph) when switching ON/OFF. |
| **UX principle** | **Visibility of System Status** — Nielsen's heuristic #1. Always communicate the current state to the user. |
| **Platform** | Both |
| **Implementation complexity** | Low |
| **Real-world examples** | iOS Settings toggle (green slide), Android Material Switch, Slack's notification toggle |

**Implementation tips:**
- Toggle transition duration of 200–300ms is ideal (too fast = unnoticeable; too slow = sluggish)
- Don't rely on color alone for state — pair with icons (check/X) or text labels (for color-vision deficiency)
- Respect the `prefers-reduced-motion` media query
- When the toggle requires server sync, apply optimistic update

### 1.3 Loading States

| Item | Content |
|------|---------|
| **Description** | Visual indications that data is loading. Many forms: spinner, progress bar, skeleton UI, shimmer effect, etc. |
| **UX principle** | **Doherty Threshold** — productivity jumps sharply when system response is within 400ms. Anything longer requires progress feedback. |
| **Platform** | Both |
| **Implementation complexity** | Medium |
| **Real-world examples** | Skeleton Screen at Facebook/LinkedIn, YouTube's shimmer loading, Notion's page loading animation |

**Implementation tips:**
- 0–100ms: no feedback needed / 100–400ms: a simple indicator / 400ms–1s: spinner / 1s+: progress bar or skeleton
- Build skeletons in the same layout shape as the real content to reduce cognitive load
- Shimmer effect: left-to-right gradient animation to convey "alive" status
- Replace the infinite spinner with expected time or step-by-step messages (e.g., "Analyzing data...")

### 1.4 Pull-to-Refresh

| Item | Content |
|------|---------|
| **Description** | A native mobile pattern where pulling down at the top of a list refreshes content. First invented by Loren Brichter in the Tweetie app (2008). |
| **UX principle** | **Direct Manipulation** — giving users the feeling of manipulating interface objects directly lowers learning cost (Ben Shneiderman). |
| **Platform** | Mobile (limited on Web) |
| **Implementation complexity** | Medium |
| **Real-world examples** | Twitter/X pull-to-refresh, Instagram feed, Gmail inbox, Naver app |

**Implementation tips:**
- Provide visual feedback proportional to pull distance (icon rotation, progress)
- Release before threshold → snap back; after threshold → refresh
- A 300ms minimum delay after refresh ensures the user can perceive completion
- On the Web, use `overscroll-behavior: contain` to prevent default browser behavior

### 1.5 Like/Heart Animation

| Item | Content |
|------|---------|
| **Description** | When a like/heart button is pressed, a rich animation (particle burst, scale change, color fill, etc.) provides emotional satisfaction. |
| **UX principle** | **Emotional Design** — Don Norman's three levels; the "visceral" level. Immediate sensory reactions trigger positive emotion. **Variable Reward** — subtly different animations each time stimulate a dopamine response. |
| **Platform** | Both |
| **Implementation complexity** | Medium |
| **Real-world examples** | Twitter/X heart-burst animation, Instagram double-tap heart, Medium clap counter, KakaoStory like |

**Implementation tips:**
- Implement with Lottie or CSS keyframes (SVG path morphing + scale + opacity)
- Animation duration of 300–600ms is ideal — too short and users miss it, too long and repetition becomes obstructive
- Mobile double-tap likes are implemented as a large heart overlay at the center of the feed image
- For unlike, handle silently without flashy animation (asymmetric feedback)

### 1.6 Counter Animation

| Item | Content |
|------|---------|
| **Description** | When a number changes, an animation (odometer roll, slide, fade) emphasizes the change. |
| **UX principle** | **Change Blindness Prevention** — humans easily miss gradual change; visual emphasis at the moment of change is needed. |
| **Platform** | Both |
| **Implementation complexity** | Low |
| **Real-world examples** | Robinhood stock price changes, Toss net-worth view, GitHub star counter, Coupang cart badge |

**Implementation tips:**
- Apply top→bottom or bottom→top slide according to increase/decrease direction
- Implement smooth counting via `requestAnimationFrame`
- For large jumps, apply easing (ease-out) to decelerate gradually
- Animate financial numbers (prices, points) together with thousand-separator commas

---

## 2. Navigation Patterns

Navigation determines how users find and move to destinations within the app. Good navigation should be "invisible" — the user shouldn't be conscious of the navigation itself and should focus on content.

### 2.1 Tab Bar

| Item | Content |
|------|---------|
| **Description** | A top-level navigation pattern placing 3–5 primary sections at the bottom of the screen with icons + labels. Recommended as a standard pattern by both iOS Human Interface Guidelines and Material Design. |
| **UX principle** | **Fitts's Law** — the larger and closer the target, the faster the access. Bottom tabs sit in the thumb zone, making them easy to operate. **Miller's Law** — working memory holds 7±2 items; limit tabs to 5 or fewer. |
| **Platform** | Mobile (a top-tab variant on Web) |
| **Implementation complexity** | Low |
| **Real-world examples** | Instagram (Home/Search/Reels/Shopping/Profile), KakaoTalk (Friends/Chats/View/Shopping/More), YouTube, Toss |

**Implementation tips:**
- Honor the minimum touch target of 48x48dp (Material) or 44x44pt (iOS HIG)
- Distinguish the active tab clearly via color + icon change (filled/outlined)
- Notification badge at minimum size; include the count in `aria-label` for accessibility
- Preserve state on tab switch — keep scroll positions and input states per tab

### 2.2 Hamburger Menu

| Item | Content |
|------|---------|
| **Description** | A pattern that hides navigation behind a three-line icon (☰). Saves screen space but has low discoverability. |
| **UX principle** | **Cognitive Load Theory** — hiding information simplifies the screen, but conflicts with the **Out of Sight, Out of Mind** principle. NNGroup research confirms reduced exploration when menus are hidden. |
| **Platform** | Both (mobile-first; secondary on desktop) |
| **Implementation complexity** | Low |
| **Real-world examples** | Gmail (mobile), Spotify (past → now switched to a tab bar), Facebook (past → now switched to a tab bar) |

**Implementation tips:**
- Expose key features in the tab bar; only place secondary features in the hamburger menu
- When the menu opens, show an overlay (scrim) and support closing by swipe
- Pair menu items with icons to speed scanning
- On the Web, expand to a sidebar at ≥ 768px and collapse to a hamburger below

### 2.3 Gesture Navigation

| Item | Content |
|------|---------|
| **Description** | A pattern for moving between screens via touch gestures (swipe, edge gestures). Examples: iOS edge swipe for back, Android's system gesture navigation. |
| **UX principle** | **Direct Manipulation** + **Jakob's Law** — users expect gestures learned in other apps to work the same way. Following OS-level gesture conventions minimizes learning cost. |
| **Platform** | Mobile |
| **Implementation complexity** | Medium |
| **Real-world examples** | iOS system back (edge swipe), Android 10+ gesture navigation, Tinder swipe, Safari tab switching |

**Implementation tips:**
- Don't conflict with platform-default gestures (back, home, etc.)
- Provide a visual hint at gesture start (page-edge shadow, preview)
- When the finger lifts mid-gesture, decide complete/cancel based on a threshold
- Always provide a button alternative so a gesture is never the only path (accessibility)

### 2.4 Breadcrumbs

| Item | Content |
|------|---------|
| **Description** | A secondary navigation showing the page's hierarchical location as a path (Home > Category > Subcategory > Current). |
| **UX principle** | **Cognitive Map** — lets users know where they are in the information space. **Hansel & Gretel effect** — the comfort of being able to retrace one's steps. |
| **Platform** | Web (limited on mobile due to space constraints) |
| **Implementation complexity** | Low |
| **Real-world examples** | Amazon product categories, Google search results, Notion page path, Jira issue path |

**Implementation tips:**
- Display the last item (current page) as plain text, not a link
- Use `<nav aria-label="Breadcrumb">` + `<ol>` semantic markup
- Add structured data (Schema.org BreadcrumbList) for SEO
- On mobile, replace with a single "< parent category" back link

### 2.5 Bottom Sheet

| Item | Content |
|------|---------|
| **Description** | A modal panel that rises from the bottom. Used to show extra options, details, filters, etc., while preserving context. |
| **UX principle** | **Context Preservation** — provide additional information without a full-page transition, so the user's workflow is not interrupted. **Fitts's Law** — rises from the bottom, so it stays within the thumb zone. |
| **Platform** | Mobile (modal/side-panel variant on Web) |
| **Implementation complexity** | Medium |
| **Real-world examples** | Google Maps place details, Apple Maps, Uber ride info, KakaoMap, Toss payment sheet |

**Implementation tips:**
- Support 3 heights: peek (preview), half, full
- Place a grab bar at the top to visually indicate draggability
- Background scrim (semi-transparent overlay) + tap outside to close
- Resolve gesture conflicts between scrollable content and sheet dragging (drag the sheet only when scroll is at the top)

### 2.6 Swipe Navigation

| Item | Content |
|------|---------|
| **Description** | Move between tabs or pages by swiping left/right. Combine with a top tab indicator to show the current position. |
| **UX principle** | **Spatial Memory** — placing content spatially helps users remember its location. **Direct Manipulation** — page movement proportional to swipe distance provides a physical feel. |
| **Platform** | Mobile |
| **Implementation complexity** | Medium |
| **Real-world examples** | KakaoTalk chat list (left swipe → menu), Tinder card swipe, iOS Weather city switching, Chrome mobile tab switching |

**Implementation tips:**
- Peek the next page slightly in the swipe direction to hint "there's more"
- On the first/last page, bounce to indicate the boundary
- Use native components like ViewPager (Android) or UIPageViewController (iOS)
- The tab indicator underline moves along with the swipe in a linked animation

---

## 3. Feedback & Response

A system's appropriate reaction to user action is core to building trust. Nielsen's heuristic #1, "Visibility of System Status," underpins all feedback patterns.

### 3.1 Haptic Feedback

| Item | Content |
|------|---------|
| **Description** | A pattern combining touch interactions with vibration to provide a physical feel. Uses iOS's Taptic Engine and Android's HapticFeedback API. |
| **UX principle** | **Multisensory Feedback** — combining sight + touch raises cognitive accuracy beyond a single sense. **Affordance** — reproduces the "pressed" feel of a physical button to confirm action completion. |
| **Platform** | Mobile |
| **Implementation complexity** | Low |
| **Real-world examples** | iPhone keyboard typing, Apple Watch Digital Crown, Toss "transfer complete" vibration, Samsung One UI touch feedback |

**Implementation tips:**
- iOS: `UIImpactFeedbackGenerator` (light/medium/heavy), `UINotificationFeedbackGenerator` (success/warning/error)
- Android: use system constants such as `HapticFeedbackConstants.LONG_PRESS`, `VIRTUAL_KEY`
- Web: `navigator.vibrate()` API (supported on Android Chrome; not on iOS Safari)
- Excessive haptics drain battery and tire users — apply selectively to important actions

### 3.2 Skeleton Screen

| Item | Content |
|------|---------|
| **Description** | While data loads, show a gray-block skeleton of the actual UI layout. Shortens perceived loading time more than a spinner. |
| **UX principle** | **Perceived Performance** — what matters is the speed users *feel*, not the actual speed. A skeleton sets up the expectation that content is about to appear. Luke Wroblewski's research showed skeleton screens shorten perceived waiting compared to spinners. |
| **Platform** | Both |
| **Implementation complexity** | Medium |
| **Real-world examples** | Facebook feed, LinkedIn profile, YouTube video list, Naver News, Baemin |

**Implementation tips:**
- Match the skeleton's layout to the real content (height, width, spacing)
- Shimmer animation: `background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)` + `animation: shimmer 1.5s infinite`
- Represent text areas as multi-line rounded rectangles, images as square/circular blocks
- Replace with a fade-in transition when data arrives

### 3.3 Optimistic Update

| Item | Content |
|------|---------|
| **Description** | Update the UI immediately without waiting for the server response; roll back on failure. Hides network latency to provide instant responsiveness. |
| **UX principle** | **Doherty Threshold** — response within 400ms is optimal. Network round-trips exceed it, so updating the UI first improves perceived speed. **Trust Design** — most requests succeed, so optimize UX around the success case. |
| **Platform** | Both |
| **Implementation complexity** | High |
| **Real-world examples** | Instagram like, Twitter/X tweet posting, Slack message send, iMessage bubble |

**Implementation tips:**
- Rollback logic is mandatory on failure — keep a snapshot of the previous state
- On failure, notify the user via toast and provide retry
- Use TanStack Query's `useMutation` + `onMutate` (optimistic) + `onError` (rollback)
- Do **not** apply optimistic updates to hard-to-undo actions (payment, delete)

### 3.4 Progress Indicator

| Item | Content |
|------|---------|
| **Description** | Visualizes the progress of an operation. Determinate (percent) and indeterminate (infinite loop) variants exist. |
| **UX principle** | **Goal-Gradient Effect** — behavior accelerates as the goal nears. A progress bar evokes "almost done" and prevents drop-off. **Endowed Progress Effect** — showing some progress already made (rather than 0%) raises completion motivation. |
| **Platform** | Both |
| **Implementation complexity** | Low |
| **Real-world examples** | YouTube video upload, GitHub Actions build progress, LinkedIn profile completeness, Naver Cloud file upload |

**Implementation tips:**
- Use determinate (percent) when total time is predictable; indeterminate otherwise
- A progress bar that slows toward the end feels natural (matches reality)
- For multi-step tasks, use a step indicator (Step 1/3, Step 2/3, Step 3/3)
- Use the `<progress>` HTML element — basic accessibility for free

### 3.5 Toast / Snackbar Notification

| Item | Content |
|------|---------|
| **Description** | A short message that appears briefly at the top or bottom of the screen and fades away. Conveys information without interrupting the user's workflow. |
| **UX principle** | **Minimal Interruption** — convey side information without breaking the current task. **Auto-dismiss** — no user action required; time-based auto-removal minimizes cognitive load. |
| **Platform** | Both |
| **Implementation complexity** | Low |
| **Real-world examples** | Gmail "Message sent" + undo, Android Material Snackbar, Slack notifications, VS Code notifications |

**Implementation tips:**
- Duration: 3s for short messages, 5s for long messages, 8s when an action is included
- Include an "Undo" action for reversible operations
- Queue multiple toasts and show them sequentially
- Use `role="status"` or `aria-live="polite"` for screen-reader accessibility
- Error toasts should not auto-dismiss; let the user close them

---

## 4. Gesture-based Interactions

On touch devices, gestures transfer physical-world manipulation into digital form. Well-designed gestures are intuitive and efficient, but discoverability is limited, so always provide an alternative.

### 4.1 Swipe Actions

| Item | Content |
|------|---------|
| **Description** | Swiping list items left/right reveals quick actions (delete, archive, mark-read). |
| **UX principle** | **Efficiency of Use** — provide power-user shortcuts to speed up tasks. **Progressive Disclosure** — keep the base screen clean and surface actions only when needed. |
| **Platform** | Mobile |
| **Implementation complexity** | Medium |
| **Real-world examples** | iOS Mail (swipe → delete/archive/flag), Gmail, Todoist (swipe → complete/reschedule), KakaoTalk chats |

**Implementation tips:**
- Map different actions to left vs. right swipes (e.g., left → delete, right → archive)
- Reveal action icons + color according to swipe distance → auto-execute past a threshold
- Use semantic color: red for delete, blue/gray for archive
- Provide an "Undo" toast on delete to prevent mistakes

### 4.2 Pinch-to-Zoom

| Item | Content |
|------|---------|
| **Description** | A multi-touch gesture that zooms by spreading or pinching two fingers. Popularized at the iPhone announcement in 2007. |
| **UX principle** | **Direct Manipulation** — reproduces the physical experience of stretching content. **Natural Mapping** — finger spacing maps intuitively to zoom level. |
| **Platform** | Mobile (Ctrl+scroll or trackpad gestures on Web) |
| **Implementation complexity** | Medium |
| **Real-world examples** | Google Maps zoom, Photos app, Safari webpage zoom, Figma canvas zoom |

**Implementation tips:**
- Configure min/max zoom levels (commonly 1x–5x)
- Anchor the zoom center to the midpoint between fingers
- Provide a double-tap as a fast zoom in/out alternative (for accessibility and one-handed use)
- On the Web, set `touch-action: none` to disable default browser zoom and implement custom (only for specialty UI like maps)

### 4.3 Drag and Drop

| Item | Content |
|------|---------|
| **Description** | Grab an element and move it to a desired location. Used for reordering, categorizing, and layout placement. |
| **UX principle** | **Direct Manipulation + Spatial Memory** — a digital transfer of the physical act of moving objects. The visual relationship between drag source and drop target should be intuitive. |
| **Platform** | Both (desktop-first; on mobile use long press + drag) |
| **Implementation complexity** | High |
| **Real-world examples** | Trello card movement, Notion block reorder, Figma layer reorder, app icon reorder (iOS/Android) |

**Implementation tips:**
- On drag start, show a translucent "ghost" copy and highlight drop zones
- On mobile, enter drag mode via long press (300–500ms); fire a haptic on start
- Snap near drop zones to encourage precise placement
- Add `aria-grabbed`, `aria-dropeffect` ARIA attributes for accessibility
- Libraries: `@dnd-kit/core` (React), `SortableJS`, `react-beautiful-dnd`

### 4.4 Long Press

| Item | Content |
|------|---------|
| **Description** | Pressing and holding an element activates a context menu, preview, edit mode, etc. The equivalent of right-click on desktop. |
| **UX principle** | **Progressive Disclosure** — hide infrequent features to simplify the interface while keeping them accessible. **Secondary Action** — provides a second channel distinct from the primary (tap). |
| **Platform** | Mobile |
| **Implementation complexity** | Low |
| **Real-world examples** | iOS 3D Touch / Haptic Touch preview, WhatsApp message reactions, KakaoTalk message copy/delete/reply, Android app icon shortcuts |

**Implementation tips:**
- Long-press recognition window: 300–500ms (too short → accidental activation; too long → sluggish)
- On long-press start, provide visual feedback (scale up, highlight) + haptic
- Essential functions must not be exclusive to long press — always provide an alternative path (menu button, etc.)
- iOS: Context Menu API; Android: `setOnLongClickListener`

### 4.5 Double Tap

| Item | Content |
|------|---------|
| **Description** | Rapidly tap the same spot twice to trigger an action (like, zoom in, select). |
| **UX principle** | **Efficiency (shortcut)** — fast path for power users. But because of low discoverability, it must not be the only access route. |
| **Platform** | Mobile |
| **Implementation complexity** | Low |
| **Real-world examples** | Instagram double-tap like, iOS Photos double-tap zoom, YouTube double-tap 10-second jump, Android double-tap to wake |

**Implementation tips:**
- Double-tap interval: 200–300ms
- Avoid confusion with single tap — adding a 300ms delay to single tap degrades UX, so assign double tap only to secondary actions distinct from single tap
- Provide a clear visual confirmation on success (e.g., Instagram's large heart overlay)
- For accessibility, always provide a button alternative for the same action

---

## 5. Scroll Interactions

Scrolling is the most frequent interaction on web and mobile. Combining interactions with scrolling enriches content consumption, but performance optimization is key.

### 5.1 Parallax Scrolling

| Item | Content |
|------|---------|
| **Description** | A visual effect where background and foreground scroll at different speeds, creating depth. |
| **UX principle** | **Depth Perception** — motion parallax leverages the human depth-perception mechanism. **Immersion** — gives 3D experience to a flat screen, improving content immersion. |
| **Platform** | Web (use caution on mobile due to performance) |
| **Implementation complexity** | Medium |
| **Real-world examples** | Apple product pages (iPhone, MacBook), Nike landing pages, Spotify Wrapped, Samsung Galaxy pages |

**Implementation tips:**
- Use CSS `transform: translate3d()` for GPU acceleration (`will-change: transform`)
- Disable or lighten parallax on mobile — scroll performance is the top priority
- Respect `prefers-reduced-motion`
- Run animations only when the element enters the viewport via Intersection Observer (perf)

### 5.2 Infinite Scroll

| Item | Content |
|------|---------|
| **Description** | A pattern that automatically loads more content when the user reaches the bottom of the page, providing uninterrupted browsing. |
| **UX principle** | **Flow State** — Mihaly Csikszentmihalyi's Flow theory. An uninterrupted content stream sustains a state of immersion. However, downsides include inaccessibility of the footer, loss of position, and anxiety from a lack of an "end". |
| **Platform** | Both |
| **Implementation complexity** | Medium |
| **Real-world examples** | Instagram feed, Twitter/X timeline, Pinterest board, Facebook news feed |

**Implementation tips:**
- Use Intersection Observer to load the next page when a "sentinel" enters the viewport
- Always provide a "back to top" button (FAB) — a return path after long scrolling
- When content ends, show a "You've seen everything" message
- On back-navigation, restore the previous scroll position
- Infinite scroll suits exploratory content (feeds); pagination suits goal-directed content (search results)

### 5.3 Sticky Header

| Item | Content |
|------|---------|
| **Description** | A header (navigation bar) that stays pinned to the top while scrolling, always accessible. A variant hides/shows it based on scroll direction. |
| **UX principle** | **Persistent Accessibility** — keep core navigation always available. **Fitts's Law** — pinning to the screen edge yields an "infinite target" effect (the screen edge acts as a natural stop). |
| **Platform** | Both |
| **Implementation complexity** | Low |
| **Real-world examples** | Naver top bar, Amazon search bar, Medium read-progress indicator, GitHub file-browser header |

**Implementation tips:**
- Implement simply via CSS `position: sticky; top: 0;`
- Hide on scroll-down, show on scroll-up (show-on-scroll-up) — detect direction via `scroll` events
- Apply padding-top equal to header height to avoid overlap
- On mobile, shrink to a compact header on scroll to free up content area

### 5.4 Scroll-triggered Animation

| Item | Content |
|------|---------|
| **Description** | Animations (fade-in, slide-up, etc.) fire when an element enters the viewport as the user scrolls. |
| **UX principle** | **Attention Direction** — motion automatically draws human visual attention. Selectively applied to important content, it reinforces information hierarchy. **Progressive Disclosure** — reveal information sequentially as the user scrolls. |
| **Platform** | Web (consider performance on mobile apps) |
| **Implementation complexity** | Medium |
| **Real-world examples** | Apple product pages, Stripe homepage, Toss service pages, Airbnb host pages |

**Implementation tips:**
- Detect viewport entry via Intersection Observer (threshold: 0.1–0.3)
- Use CSS `@keyframes` + `animation-fill-mode: forwards` to retain the final state
- Libraries: AOS (Animate On Scroll), Framer Motion, GSAP ScrollTrigger
- Run the animation once (running it every time is distracting)
- Honor `prefers-reduced-motion` — display immediately when motion is reduced

### 5.5 Scroll Snap

| Item | Content |
|------|---------|
| **Description** | When scrolling stops, the view automatically snaps to the nearest content boundary. Used for card carousels and full-screen sections. |
| **UX principle** | **Alignment** — content doesn't get stuck mid-way, improving visual polish. **Predictability** — predictable scroll outcomes preserve user control. |
| **Platform** | Both |
| **Implementation complexity** | Low |
| **Real-world examples** | Instagram Reels (vertical snap), TikTok feed, App Store app carousel, Daangn image carousel |

**Implementation tips:**
- CSS `scroll-snap-type: x mandatory` (horizontal) or `y mandatory` (vertical)
- Apply `scroll-snap-align: start | center | end` to child elements
- `mandatory` always snaps; `proximity` snaps only near snap points
- Use pagination dots to show current position and total count

---

## 6. Form Interactions

Forms are the core interface for data exchange between users and the system. A well-designed form dramatically improves completion rates. Per Luke Wroblewski, form optimization alone can lift conversion 25–40%.

### 6.1 Inline Validation

| Item | Content |
|------|---------|
| **Description** | A pattern that validates in real time when the user leaves a field (blur) or as they type, and provides feedback. |
| **UX principle** | **Immediate Feedback** — finding errors immediately lowers correction cost. Per-field feedback is more effective than a list of errors after submit. Per Luke Wroblewski's research, inline validation reduced completion time by 22% and errors by 22% vs. on-submit validation. |
| **Platform** | Both |
| **Implementation complexity** | Medium |
| **Real-world examples** | Gmail signup (email duplicate check), GitHub repo name validation, Toss account-number input, Naver signup |

**Implementation tips:**
- **Timing matters**: validate on blur, not on change — error messages while typing are intrusive
- However, "positive feedback" like password strength can be shown live while typing
- Show errors below the field in red with an icon (✗)
- Show success state too — green check (✓) confirms "this field is OK"
- Connect the error message to the field via `aria-describedby` (accessibility)

### 6.2 Floating Labels

| Item | Content |
|------|---------|
| **Description** | The placeholder rises above the field to become a label when the user starts typing. Popularized by Material Design. |
| **UX principle** | **Space Efficiency** — combining label and placeholder saves vertical space. **Context Retention** — solves the problem where placeholders disappear after input and the user forgets which field is which. |
| **Platform** | Both |
| **Implementation complexity** | Low |
| **Real-world examples** | All Material Design products, Airbnb search form, Toss transfer input, Stripe payment form |

**Implementation tips:**
- Label transition: `transform: translateY(-20px) scale(0.75)` + `transition: 200ms`
- Always use a `<label>` and connect with `for` (accessibility)
- Keep the label in the raised position whenever there's a value
- When the label shrinks, readability drops — keep it at least 12px
- On error, change label + border color to red

### 6.3 Auto-complete

| Item | Content |
|------|---------|
| **Description** | Suggests possible choices in real time based on the user's input, speeding up entry. |
| **UX principle** | **Hick's Law** — more options → longer decision time. Auto-complete filters irrelevant options to shorten decisions. **Recognition over Recall** — recognizing from a list is easier than recalling from memory (Nielsen heuristic #6). |
| **Platform** | Both |
| **Implementation complexity** | Medium |
| **Real-world examples** | Google search autocomplete, GitHub issue/mention (@), Slack channels/mentions, Naver Maps address search, Kakao address API |

**Implementation tips:**
- Start suggesting after 2–3 characters (1 char gives too many results)
- Apply debounce (200–300ms) to optimize server requests
- Support keyboard navigation (↑↓) + Enter to select
- Bold-highlight the matching substring
- Apply the ARIA pattern: `role="combobox"`, `aria-autocomplete`, `aria-activedescendant`
- Show recent / popular searches in the empty state

### 6.4 Smart Defaults

| Item | Content |
|------|---------|
| **Description** | Pre-fill the most likely value based on the user's context (location, time, prior input, statistical majority). |
| **UX principle** | **Principle of Least Effort** — users will use minimal energy to achieve a goal. **Default Effect** — the tendency not to change a preset default is overwhelming (opt-in participation is 50–90% lower than opt-out). |
| **Platform** | Both |
| **Implementation complexity** | Medium |
| **Real-world examples** | Departure city on flight booking (based on current location), default delivery address in food apps, default 1-hour event in calendars, prior address auto-fill on e-commerce |

**Implementation tips:**
- GPS-based country/city auto-select; browser-language-based language setting
- Learn from prior input: recently used addresses, payment methods first
- Use statistically most-common values as defaults (e.g., top of the country list = the service's main market)
- Defaults must be changeable any time, and change should be easy

### 6.5 Step-by-Step Wizard

| Item | Content |
|------|---------|
| **Description** | Splits a complex form into multiple steps and handles them one at a time. Displays a progress indicator per step. |
| **UX principle** | **Chunking** — George Miller's theory. Breaking information into small chunks reduces cognitive load. **Goal-Gradient Effect** — progress indication boosts completion motivation. **Completion Bias** — the psychological tendency to finish a started process. |
| **Platform** | Both |
| **Implementation complexity** | Medium |
| **Real-world examples** | TurboTax tax filing, Typeform surveys, Toss account opening, Baemin store onboarding, Airbnb listing creation |

**Implementation tips:**
- Show the total step count so users can estimate effort (Step 2 of 4)
- Must allow going back (preserve input)
- Keep each step to ≤ 3–5 fields
- Provide a review/summary screen at the final step
- Support drafts so users can leave mid-way and return

### 6.6 Input Mask

| Item | Content |
|------|---------|
| **Description** | Auto-formats input of specific shapes such as phone (010-1234-5678) or card number (1234 5678 9012 3456). |
| **UX principle** | **Error Prevention** — Nielsen heuristic #5. Designing to prevent errors is superior to error messages. **Reduced cognitive load** — users don't need to remember the format; the system applies it. |
| **Platform** | Both |
| **Implementation complexity** | Medium |
| **Real-world examples** | Stripe card payment (4-digit card-number grouping), Toss account input, Naver phone authentication |

**Implementation tips:**
- For numeric-only fields, use `inputmode="numeric"` (mobile numeric keypad)
- Implement auto-hyphen/space insertion considering input direction (add/delete)
- Keep the cursor position correct when the mask applies (avoid cursor jumps)
- Libraries: `cleave.js`, `react-input-mask`, `imask`
- On server send, strip mask characters and transmit the pure value

---

## 7. Transition & Animation

Animation helps the user's cognitive model. It provides a visual narrative explaining where you came from, where you're going, and what changed. The 12 Disney animation principles (1981) remain valid for digital UI animation.

### 7.1 Page Transition

| Item | Content |
|------|---------|
| **Description** | A pattern providing spatial continuity via slide, fade, zoom, etc., when moving between pages. |
| **UX principle** | **Spatial Consistency** — conveying spatial relationships between pages via animation helps the user understand information structure intuitively. **Continuity Principle** — smooth transitions retain context better than hard cuts. |
| **Platform** | Both |
| **Implementation complexity** | Medium |
| **Real-world examples** | iOS UINavigationController (push/pop slide), Material Design container transform, Next.js page transitions, Toss screen transitions |

**Implementation tips:**
- Drill-down: slide in left → right; return: slide right → left
- Same-level (sibling): fade or cross-dissolve
- Transition duration: 200–300ms (mobile), 150–250ms (desktop)
- Web: View Transitions API (`document.startViewTransition()`)
- Block user input during transition to prevent double navigation

### 7.2 Shared Element Transition

| Item | Content |
|------|---------|
| **Description** | A common element (image, card) animates its position and size across two screens for a seamless link. |
| **UX principle** | **Object Constancy** — perceived as the same object transforming, so users feel "the existing element expanded" rather than "a new page opened". This dramatically reduces context-switching cost. |
| **Platform** | Both |
| **Implementation complexity** | High |
| **Real-world examples** | Google Photos gallery → detail, Material Design card expansion, iOS App Store card → detail, Airbnb listing card → detail |

**Implementation tips:**
- Give the shared element the same ID/tag on both screens
- Compute start/end position+size and apply `transform` animation (avoid layout triggers)
- FLIP technique (First, Last, Invert, Play): render the final position → invert transform → play
- React: Framer Motion `layoutId`; Flutter: `Hero` widget; Android: `SharedElementTransition`
- Web: `view-transition-name` CSS property in the View Transitions API

### 7.3 Morphing Animation

| Item | Content |
|------|---------|
| **Description** | A smooth transformation from one shape to another. Examples: icon morphs (hamburger → X, play → pause), button-shape changes. |
| **UX principle** | **Continuity & Transformation** — visually link state changes so "what changed" is immediately clear. A digital application of Disney's "Squash and Stretch". |
| **Platform** | Both |
| **Implementation complexity** | Medium |
| **Real-world examples** | Material Design hamburger → arrow icon, iOS lock-screen icon morph, music app play/pause button, Notion toggle arrow rotation |

**Implementation tips:**
- SVG path morph: interpolate the `d` attribute by matching point counts of two SVG paths
- CSS: `clip-path` transitions for simple shape morphs
- Use Lottie files so designers author complex morphs; developers just play them
- Libraries: `flubber` (SVG morph), `anime.js`, Lottie

### 7.4 Spring Physics

| Item | Content |
|------|---------|
| **Description** | Instead of mechanical easing (ease-in/out), use spring physics (mass, stiffness, damping) for natural motion. |
| **UX principle** | **Naturalism** — motion that obeys real physics feels more natural than artificial easing. Springs overshoot then settle, giving an "alive" feel. **Disney principle: Follow Through** — after the main motion stops, secondary elements continue due to inertia. |
| **Platform** | Both |
| **Implementation complexity** | Medium |
| **Real-world examples** | UIKit Dynamics throughout iOS, Facebook/Meta app transitions, Framer Motion default animations, Apple widget stacks |

**Implementation tips:**
- Key parameters: `stiffness` (higher → faster), `damping` (lower → bouncier), `mass` (higher → heavier)
- React: `framer-motion` `type: "spring"`; React Native: `withSpring` in `react-native-reanimated`
- Spring approximations are possible with CSS `cubic-bezier()` but limited
- Applying spring to interactive elements (drag, etc.) creates a natural "release-and-return" feel

### 7.5 Staggered Animation

| Item | Content |
|------|---------|
| **Description** | Several elements don't appear simultaneously; they enter sequentially with a small delay (50–100ms). |
| **UX principle** | **Visual Hierarchy** — sequential entry guides natural reading order. **Attention Guidance** — when all elements appear together it's hard to know where to look; sequential entry creates a flow for the eye. **Disney principle: Staging** — direct the audience's eye where intended. |
| **Platform** | Both |
| **Implementation complexity** | Low |
| **Real-world examples** | Material Design list-item entry, iOS settings list animation, Notion sidebar expansion, Slack channel-list loading |

**Implementation tips:**
- Apply `animation-delay: calc(index * 50ms)` to each element
- React: `staggerChildren` in `framer-motion`
- Apply stagger to only the first 5–10 elements (more becomes waiting)
- Common default animation: `opacity: 0→1` + `translateY: 20px→0`
- Same-group elements should enter from the same direction for consistency

---

## 8. Onboarding

Onboarding helps users discover the product's value as quickly as possible. Good onboarding isn't "teaching" but "letting them experience". Samuel Hulick's "Superhero Journey" framework captures the core philosophy.

### 8.1 Progressive Disclosure

| Item | Content |
|------|---------|
| **Description** | Instead of revealing all features at once, surface them gradually as the user progresses. |
| **UX principle** | **Hick's Law** — fewer options → faster decisions. Initially expose only core features; reveal advanced ones as skill grows. **Reduced cognitive load** — minimize the information to be processed at once and lower the learning burden. |
| **Platform** | Both |
| **Implementation complexity** | Medium |
| **Real-world examples** | Notion (basic blocks first, advanced blocks later), Figma (basic → advanced tools), Slack (channel join → app install → workflow) |

**Implementation tips:**
- Hide extra features behind "More" / "Advanced options"
- Behavior-based triggers: introduce related advanced features after a feature is used N times
- Focus on 3–5 core actions for first use
- Optimize exposure order using usage frequency (most-used first)

### 8.2 Tooltips

| Item | Content |
|------|---------|
| **Description** | A small popup explaining the function of a UI element on hover or touch. |
| **UX principle** | **Recognition over Recall** — users get help when they need it without having to remember. **Contextual Help** — learn in the current context without navigating to a help page. |
| **Platform** | Both (on mobile, hover is unavailable — use tap or an info icon) |
| **Implementation complexity** | Low |
| **Real-world examples** | GitHub icon tooltips, Figma tool descriptions, Jira field help, Notion shortcut hints |

**Implementation tips:**
- Delay tooltip appearance by 200–500ms (avoid reacting to unintentional hover)
- 300ms warm-up; instant or 100ms delayed dismissal
- ≤ 2 lines of text; if more is needed, add a "Learn more" link
- `role="tooltip"` + `aria-describedby` for accessibility
- On mobile, show on tap of an `(i)` icon; close on tap outside

### 8.3 Coach Marks

| Item | Content |
|------|---------|
| **Description** | On first launch, highlight key UI elements with an overlay and explain them in sequence. |
| **UX principle** | **Guided Exploration** — structured guidance beats free exploration for early learning. But excessive coach marks suggest "a complex UI that needs explaining", so use sparingly. |
| **Platform** | Both (more common in mobile apps) |
| **Implementation complexity** | Medium |
| **Real-world examples** | Slack new-user onboarding, Duolingo first lesson, KakaoTalk new-feature intro, Instagram Reels first use |

**Implementation tips:**
- Limit to 3–5 steps (longer → users start looking for "Skip")
- Always provide a "Skip" button
- Dim the background with a translucent overlay and spotlight only the target
- Interactive (perform the action) > passive reading for learning
- Persist the coach-marks-completed flag in local storage to avoid re-display

### 8.4 Empty States

| Item | Content |
|------|---------|
| **Description** | Instead of showing a blank screen when there is no content, provide a guidance message, illustration, and CTA. |
| **UX principle** | **Call to Action** — empty states are an opportunity to clearly point to the "next action". **Primacy Effect** — the first experience shapes the overall impression. Beautiful empty states make a positive first impression. |
| **Platform** | Both |
| **Implementation complexity** | Low |
| **Real-world examples** | Dropbox "Drag files here", Trello "Create your first card", Mailchimp campaign empty state, Toss Securities "Add a watch-list stock" |

**Implementation tips:**
- Include 3 elements: illustration (emotional connection) + explanatory message (current state) + CTA (next action)
- Handle different empty types: first use (onboarding guidance), no search results (suggest changing the query), error (retry guidance), done (congratulations)
- Search empty: instead of "No results", show "Try different keywords" + popular searches
- Use light, friendly illustrations that fit the brand tone (heavy empty states feel burdensome)

### 8.5 Feature Discovery

| Item | Content |
|------|---------|
| **Description** | A pattern that alerts users about new or updated features. Badges, pulse animations, "What's New" modals, etc. |
| **UX principle** | **Zeigarnik Effect** — unfinished items (unread badges) linger in memory longer than finished ones. A red badge dot creates the tension of "something unchecked" and drives exploration. |
| **Platform** | Both |
| **Implementation complexity** | Low |
| **Real-world examples** | iOS app-icon badges, Slack "New feature" banner, Figma "What's new" modal, KakaoTalk new-emoticon notice |

**Implementation tips:**
- Intensity hierarchy: badge dot (low) < inline banner (medium) < modal (high) — choose by feature importance
- Show only once; provide a "Don't show again" option
- Auto-remove the badge dot upon entry to the feature
- Excessive notifications cause "notification fatigue" — use judiciously
- Run a separate changelog page so interested users can explore voluntarily

---

## 9. Accessibility Interactions

Accessibility is not optional — it is essential. WCAG 2.1 AA is often a legal requirement (Korea's Anti-Discrimination Act, US ADA, etc.), and accessibility improvements lift the experience for all users (the Curb Cut Effect).

### 9.1 Screen Reader Patterns

| Item | Content |
|------|---------|
| **Description** | Provide proper semantic markup and ARIA attributes so visually impaired users can navigate via screen readers (VoiceOver, TalkBack, NVDA). |
| **UX principle** | **Equivalent Access** — all users must have access to the same information and functionality (WCAG Principle 1: Perceivable). |
| **Platform** | Both |
| **Implementation complexity** | Medium |
| **Real-world examples** | gov.uk (UK government website), Apple products in general, gov.kr (Korea), Naver's accessibility improvements |

**Implementation tips:**
- Prefer semantic HTML: `<button>`, `<nav>`, `<main>`, `<article>`, `<header>`, `<footer>`
- Meaningful `alt` text on images; `alt=""` + `aria-hidden="true"` on decorative images
- For dynamic content changes, use `aria-live="polite"` (non-urgent) or `aria-live="assertive"` (urgent)
- Use proper ARIA roles for custom components: `role="dialog"`, `role="tablist"`, `role="alert"`, etc.
- Icon buttons must have `aria-label` (e.g., `<button aria-label="Close"><XIcon /></button>`)

### 9.2 Focus Management

| Item | Content |
|------|---------|
| **Description** | Ensure focus moves in a logical order on keyboard navigation, and when modals/dialogs open, focus moves appropriately and is trapped within. |
| **UX principle** | **Keyboard Accessibility** — every interactive element must be reachable and operable via keyboard (WCAG 2.1.1). **Focus Trapping** — keep Tab from escaping a modal so context isn't lost. |
| **Platform** | Both (especially Web) |
| **Implementation complexity** | Medium |
| **Real-world examples** | Gmail keyboard shortcuts, GitHub issue/PR keyboard navigation, the entirety of VS Code, Jira boards |

**Implementation tips:**
- `tabindex="0"` (add to natural order), `tabindex="-1"` (programmatic focus only); avoid positive tabindex
- Open modal: move focus to the first interactive element; loop Tab within the modal
- Close modal: restore focus to the triggering element
- Distinguish `:focus-visible` (only on keyboard focus) vs. `:focus` (any focus)
- Use the `focus-trap` library or the native `<dialog>` element's built-in trapping

### 9.3 Reduced Motion

| Item | Content |
|------|---------|
| **Description** | Reduce or remove unnecessary animations for users with vestibular disorders, migraines, attention disorders, etc. |
| **UX principle** | **Inclusive Design** — accommodate users with diverse physical and cognitive conditions. Excessive motion can trigger nausea (vestibular disorder) or seizures (photosensitive epilepsy). |
| **Platform** | Both |
| **Implementation complexity** | Low |
| **Real-world examples** | iOS "Reduce Motion", macOS/Windows accessibility settings, Apple.com (parallax alternative), Stripe homepage |

**Implementation tips:**
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
- Don't remove motion entirely — substitute with a cross-fade; the minimum needed to convey context transition should remain
- Provide a stop button for auto-playing videos/GIFs
- Disable parallax, parallax-style scroll animations, and auto-carousels when `prefers-reduced-motion: reduce`

### 9.4 Color Contrast

| Item | Content |
|------|---------|
| **Description** | Ensure sufficient luminance contrast between text and background so low-vision and color-deficient users can read content. |
| **UX principle** | **Perceivability** — WCAG Principle 1. Information must be presented perceivably. WCAG 1.4.3: minimum 4.5:1 for normal text, 3:1 for large text. |
| **Platform** | Both |
| **Implementation complexity** | Low |
| **Real-world examples** | Material Design color system, Apple HIG color guide, gov.kr high-contrast mode, Naver accessibility |

**Implementation tips:**
- WCAG AA minimums: 4.5:1 for normal text (≤14px), 3:1 for large text (≥18px or 14px bold)
- WCAG AAA: 7:1 normal, 4.5:1 large
- Don't communicate information by color alone — pair with icons, patterns, or text labels (color-blindness friendly)
- Tools: WebAIM Contrast Checker, Chrome DevTools contrast inspector, Figma a11y plugin
- High-contrast mode: `@media (forced-colors: active)` + system color keywords

### 9.5 Touch Target Sizing

| Item | Content |
|------|---------|
| **Description** | Make touch/click areas large enough so users with motor impairments or larger fingers can operate precisely. |
| **UX principle** | **Fitts's Law** — larger and closer targets are faster and more accurate. Small targets cause errors and frustrate users. |
| **Platform** | Both (especially Mobile) |
| **Implementation complexity** | Low |
| **Real-world examples** | iOS Human Interface Guidelines (44x44pt), Material Design (48x48dp), WCAG 2.5.8 (24x24 CSS px), gov.kr |

**Implementation tips:**
- Minimum touch target: 44x44pt (iOS) / 48x48dp (Android) / 24x24px (WCAG AA, recommend 44x44px AAA)
- Even if the visual size is small, the touch area should be large — extend with `padding`
- Keep at least 8dp between adjacent touch targets (avoid mistakes)
- For short link text (e.g., "here"), add padding to provide a sufficient touch area
- Include `min-height: 44px; min-width: 44px;` in the default style of interactive elements

---

## 10. Delight Patterns

Delight is the design element that provides emotional satisfaction beyond functional requirements. It corresponds to the "reflective" level of Don Norman's three-level emotional design, and contributes to brand differentiation and user loyalty. However, apply it only after baseline usability is achieved — adding delight to an inconvenient product backfires.

### 10.1 Easter Eggs

| Item | Content |
|------|---------|
| **Description** | A hidden feature or message that users discover accidentally or intentionally. Conveys brand personality and triggers word-of-mouth. |
| **UX principle** | **Variable Reward** — Nir Eyal's Hook Model. Unpredictable rewards raise the motivation to explore. **Joy of Discovery** — pride and belonging from finding something yourself. |
| **Platform** | Both |
| **Implementation complexity** | Low–Medium |
| **Real-world examples** | Google "do a barrel roll", Chrome dinosaur game (offline), Slack loading messages, GitHub 404 page parallax, VS Code Konami code |

**Implementation tips:**
- Place where it doesn't affect core features (404 pages, loading screens, deep settings)
- Design so missing it doesn't impair product use
- Keep the humor aligned with team culture or brand personality
- Use classic triggers like the Konami Code (↑↑↓↓←→←→BA)

### 10.2 Celebration Animation

| Item | Content |
|------|---------|
| **Description** | When the user reaches a goal, completes a task, or hits a milestone, a visual celebration (confetti, fireworks, badge) plays. |
| **UX principle** | **Positive Reinforcement** — B.F. Skinner's operant conditioning. Reward after desired behavior promotes repetition. **Peak-End Rule** — Daniel Kahneman. The peak and the end of an experience determine the overall impression; celebrating at completion sustains a positive impression. |
| **Platform** | Both |
| **Implementation complexity** | Medium |
| **Real-world examples** | Duolingo lesson completion, GitHub first-PR-merged confetti, Notion checklist completion, Linear issue completion, Toss goal achieved |

**Implementation tips:**
- Use the `canvas-confetti` library for easy confetti effects
- Play complex celebration animations from Lottie files
- Keep effects short (1–3 seconds), originating near the completion button rather than the center
- Don't overuse — apply only to meaningful achievements (daily login + confetti is too much)
- Respect `prefers-reduced-motion`: substitute motion with a static badge or congratulations message

### 10.3 Gamification

| Item | Content |
|------|---------|
| **Description** | Apply game mechanics (points, badges, levels, leaderboards, streaks, quests) to non-game contexts. |
| **UX principle** | **Self-Determination Theory** — Deci & Ryan. Three intrinsic motivations — autonomy, competence, relatedness — sustain continued engagement. Gamification mostly leverages competence (leveling up) and relatedness (leaderboards). |
| **Platform** | Both |
| **Implementation complexity** | High |
| **Real-world examples** | Duolingo (streaks, XP, leagues), LinkedIn profile completeness, GitHub Contributions graph, Toss step counter, Samsung Health badges |

**Implementation tips:**
- Visualize "how much is left to the next level" via a progress bar
- Streaks are powerful but breaking them hurts — provide a "freeze" feature
- Leaderboards can frustrate users outside the top — mitigate via friends-only or weekly reset
- Extrinsic rewards (points) alone don't sustain long-term engagement — connect to intrinsic motivation (learning, growth)

### 10.4 Personalized Experience

| Item | Content |
|------|---------|
| **Description** | Tailor content and interface to the user's behavior, preferences, location, time, etc. |
| **UX principle** | **Cocktail Party Effect** — attention focuses automatically on info related to one's name or interests. **Self-Reference Effect** — self-related information is remembered better. |
| **Platform** | Both |
| **Implementation complexity** | High |
| **Real-world examples** | Spotify Discover Weekly, Netflix recommendations, YouTube recommendations, Toss personalized financial products, Coupang personalized home |

**Implementation tips:**
- Greet by name ("Hello, Cheolsoo Kim"); time-of-day greetings ("Good morning")
- Behavior-based shortcuts: place frequently used features near the top
- Explain personalization transparently ("Users who viewed this product also bought…")
- Provide options to disable / adjust personalization (preserve user control)
- Privacy and transparency first — comply with GDPR, Korea's Personal Information Protection Act

### 10.5 Sound Design

| Item | Content |
|------|---------|
| **Description** | Pair UI interactions with appropriate sound effects for a multisensory experience. Notification, completion, error, transition sounds, etc. |
| **UX principle** | **Multisensory Enhancement** — combining sight + sound improves cognitive accuracy and reaction time. **Sonic Branding** — a specific sound becomes associated with the brand and strengthens recognition and emotional ties (e.g., Intel sound logo, KakaoTalk notification). |
| **Platform** | Both (more active on mobile) |
| **Implementation complexity** | Medium |
| **Real-world examples** | KakaoTalk message notification, Toss transfer-complete sound, iOS keyboard click, Slack notification "Knock Brush", Facebook Messenger pop |

**Implementation tips:**
- Default sound OFF — let users opt in (respect silent mode)
- Effects should be short and pleasant, 100–500ms
- Error sounds should attract attention without being unpleasant (no sharp screeches)
- Implement with the Web Audio API or Howler.js; pre-load to avoid network delay
- For repeating interactions (typing), lower volume or vary to prevent fatigue

---

## 11. Dark Patterns — Things to Avoid

Dark patterns (deceptive patterns) are fraudulent design techniques that mislead users or push them into unintended actions. Harry Brignull coined the term in 2010, and the EU's Digital Services Act (DSA), the US FTC, and Korea's Fair Trade Commission are tightening regulation. They may improve short-term business metrics but destroy user trust and create legal risk over time.

### 11.1 Confirmshaming

| Item | Content |
|------|---------|
| **Description** | Phrasing the refusal option to induce guilt and steer users to accept. |
| **Why it's bad** | Emotionally manipulates autonomous decision-making. Short-term clicks rise but brand antipathy and distrust accumulate. |
| **Real-world examples** | "No, I'd rather give up the discount", "I'm not interested in my health", "No, I don't want to save money" |

**Correct alternatives:**
- Use neutral refusal phrasing: "No thanks, maybe later" / "Decide later"
- Make the visual weight of accept/refuse equal (size, color, position)

### 11.2 Forced Continuity

| Item | Content |
|------|---------|
| **Description** | After a free trial ends, auto-convert to a paid subscription without clear notice. Also includes deliberately complex cancellation procedures. |
| **Why it's bad** | Charges users without explicit consent, causing financial harm. Korea's E-Commerce Act and EU consumer protection law explicitly prohibit or regulate this behavior. |
| **Real-world examples** | Free trial requires a card → silent paid conversion; hiding cancel deep in settings; requiring a phone call to cancel |

**Correct alternatives:**
- Email/in-app notifications 3 days and 1 day before trial end about paid conversion
- Cancellation should be as easy as signing up — within 2 clicks in Settings
- "Are you sure you want to cancel?" → clear choices "Yes, cancel" / "Keep subscription"
- Continue service until the remaining period ends after cancellation

### 11.3 Trick Questions

| Item | Content |
|------|---------|
| **Description** | Double negatives, confusing phrasing, flipping checkbox meanings to push the user into the opposite of intent. |
| **Why it's bad** | Exploits the user's cognitive shortcuts (fast scanning, pattern-based judgment). Violates the design principle of clarity. |
| **Real-world examples** | "Don't uncheck if you don't want to receive marketing email" (double negative); the meaning of checkboxes alternates per item (check = consent vs. check = decline mixed) |

**Correct alternatives:**
- Simple positive phrasing: "I'll receive marketing email" (check = consent)
- Keep checkbox direction consistent (uniformly check = consent)
- Forbid double negatives — meaning must be clear at first read

### 11.4 Hidden Costs

| Item | Content |
|------|---------|
| **Description** | Surcharges, shipping, service fees, etc., that weren't disclosed earlier suddenly appear in the final checkout step. |
| **Why it's bad** | Destroys trust in pricing transparency. Sales spike momentarily, but cart-abandonment skyrockets. Per Baymard Institute, unexpected extra costs are the #1 reason (48%) for cart abandonment. |
| **Real-world examples** | Airfare without taxes/fees in the displayed price; shipping shown only at checkout; sudden service/handling fees |

**Correct alternatives:**
- Show total cost (with shipping) from the listing stage
- If tax/fee is separate, label "+ fees" next to the price
- In the cart, break down costs item by item (price + shipping + tax) transparently
- Clearly state the threshold for free shipping

### 11.5 Roach Motel (easy in, hard out)

| Item | Content |
|------|---------|
| **Description** | An asymmetric design that makes signup/subscribe/consent very easy and cancellation/withdrawal/unsubscribe deliberately hard. |
| **Why it's bad** | Structurally limits the user's freedom of choice. "Cancellation is hard, so they'll stick around" is short-sighted and leads to negative reviews, regulatory complaints, and lawsuits over time. |
| **Real-world examples** | Email subscribe in 1 click but unsubscribe requires login; account deletion only via phone/email to support; a chain of "Are you sure?" steps to cancel a subscription |

**Correct alternatives:**
- **Symmetric design**: if signup is 3 steps, cancellation is ≤ 3 steps
- Place withdrawal/cancellation links directly accessible from Settings
- "Unsubscribe" link at email footer should process instantly in one click
- It's OK to ask for a reason — but it must be optional, not required

### 11.6 Visual Interference

| Item | Content |
|------|---------|
| **Description** | Use visual design to emphasize one option or hide another. E.g., big "Agree" button vs. tiny gray "Decline" link. |
| **Why it's bad** | Formally the choices exist, but the visual hierarchy is manipulated to limit real choice. Especially around privacy or marketing consent, this can become a legal issue when abused. |
| **Real-world examples** | "Agree" button large and blue, "Decline" a small gray text link; cookie banner has only "Accept all" as a button while "Manage settings" is a text link |

**Correct alternatives:**
- Give agree/decline equal visual weight (size, color, position)
- Cookie banner: "Accept all" / "Reject all" / "Manage settings" with equal visual weight
- The more important the choice (privacy, payment), the smaller the visual difference between options should be

### 11.7 Forced Action

| Item | Content |
|------|---------|
| **Description** | Force unrelated actions (rate the app, social share, allow contact access) to use desired features. |
| **Why it's bad** | Invades user autonomy, and forced behavior (e.g., 5-star rating) also damages data integrity. Both Apple App Store and Google Play Store forbid forced reviews. |
| **Real-world examples** | "You can't use this feature unless you rate the app"; "Invite 5 friends to unlock"; forcing unnecessary personal-info collection to use a core feature |

**Correct alternatives:**
- Ask for ratings politely at the right moment and never re-ask on refusal (or only once after a long interval)
- Optional sharing: bonus if shared, full functionality without
- Collect data minimally and explain the reason transparently

---

## Appendix: UX Principles Quick Glossary

| Principle | Description | Proposer / Source |
|-----------|-------------|-------------------|
| **Fitts's Law** | Time to reach a target is proportional to distance and inversely proportional to size | Paul Fitts (1954) |
| **Hick's Law** | More options → decision time grows logarithmically | William Hick (1952) |
| **Jakob's Law** | Users expect a design based on their experience on other sites | Jakob Nielsen |
| **Miller's Law** | Working memory holds 7±2 items at once | George Miller (1956) |
| **Doherty Threshold** | Productivity jumps sharply when system response is within 400ms | Walter Doherty (1982) |
| **Goal-Gradient Effect** | Effort increases as one nears the goal | Clark Hull (1932) |
| **Peak-End Rule** | The peak and the end of an experience define the overall impression | Daniel Kahneman |
| **Von Restorff Effect** | An item that stands out among similar items is remembered better | Hedwig von Restorff (1933) |
| **Zeigarnik Effect** | Unfinished tasks are remembered better than finished ones | Bluma Zeigarnik (1927) |
| **Aesthetic-Usability Effect** | Aesthetically pleasing designs are perceived as easier to use | Masaaki Kurosu & Kaori Kashimura (1995) |
| **Tesler's Law** | Every process has an irreducible minimum of complexity | Larry Tesler |
| **Serial Position Effect** | The first and last items in a list are remembered best | Hermann Ebbinghaus (1885) |
| **Cognitive Load Theory** | Cognitive resources are finite; minimize unnecessary load | John Sweller (1988) |

---

## References

- Norman, D. (2004). *Emotional Design: Why We Love (or Hate) Everyday Things*
- Saffer, D. (2013). *Microinteractions: Designing with Details*
- Krug, S. (2014). *Don't Make Me Think, Revisited*
- Eyal, N. (2014). *Hooked: How to Build Habit-Forming Products*
- Wroblewski, L. (2008). *Web Form Design: Filling in the Blanks*
- Nielsen, J. (1994). *10 Usability Heuristics for User Interface Design*
- Brignull, H. (2010). *Dark Patterns: Deception vs. Honesty in UI Design*
- Material Design Guidelines — material.io
- Apple Human Interface Guidelines — developer.apple.com/design
- Web Content Accessibility Guidelines (WCAG) 2.1 — w3.org/WAI
- Laws of UX — lawsofux.com
