# Vibe Coding Animation Guide

> UI animation implementation techniques, library comparison, prompting strategy, performance optimization, and accessibility guide using vibe coding tools

## 1. Overview

### Vibe Coding and Animation

Vibe coding tools (v0, Cursor, Claude Code, Bolt, etc.) generate working code from natural-language animation descriptions. This guide covers **how professional designers and developers implement high-quality animation with AI tools**.

### Animation Generation Characteristics by AI Tool

| Tool | Default output | Strengths | Weaknesses |
|------|----------------|-----------|------------|
| **v0** | Framer Motion + Tailwind | Page transitions, card hover, list animations | Weak complex orchestration |
| **Cursor** | Detects the project's existing library | Strong on editing and refining existing animations | — |
| **Claude Code** | CSS / Framer Motion / GSAP | Accessibility-aware (auto-includes `prefers-reduced-motion`), complex sequences | — |
| **Bolt / Lovable** | CSS (simple) or Framer Motion (React) | Rapid generation of whole-page animation | Lacks production-grade polish |

### Common Patterns and Limitations of AI-Generated Animation

**Common patterns:**
- Simple hover/focus states → defaults to CSS transition
- React components → prefers Framer Motion first
- Prefers spring physics over Bezier curves (more natural feel)
- Stagger animation (sequential children entry) is the signature pattern

**Limitations:**
- Weak timing orchestration in complex multi-element scenes
- Missing performance optimizations such as GPU layering and compositor hints
- Lacks proper cleanup for scroll animations (memory leaks)
- `prefers-reduced-motion` is often missing unless explicitly requested

---

## 2. Modern CSS Animation (2025–2026)

### 2.1 View Transitions API

With expanding browser support, this is considered the most important advance in web animation.

#### SPA Document Transition

```css
/* Trigger a transition in JavaScript */
document.startViewTransition(() => {
  updateDOM(); // mutate the DOM
});

/* Default cross-fade (free) */
::view-transition-old(root) {
  animation: fade-out 0.3s ease;
}
::view-transition-new(root) {
  animation: fade-in 0.3s ease;
}
```

#### Named View Transitions (shared element transition)

```css
/* List-page card image */
.product-card .product-image {
  view-transition-name: hero-image;
}

/* Detail-page hero image — connected by the same name */
.product-detail .hero-image {
  view-transition-name: hero-image;
}

/* Customize the transition animation */
::view-transition-group(hero-image) {
  animation-duration: 0.4s;
  animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
```

#### MPA Cross-document Transition

```css
/* Opt-in on both pages */
@view-transition {
  navigation: auto;
}
```

#### Dynamic view-transition-name (for lists)

```jsx
{/* Assign a unique name per item */}
<div style={{ viewTransitionName: `product-${item.id}` }}>
  <img src={item.image} />
</div>
```

**Key patterns:**
- Apply group transitions via `view-transition-class`
- Combine with `@media (prefers-reduced-motion: reduce)` to disable transitions
- Next.js App Router, Astro, SvelteKit have all added View Transition support

---

### 2.2 Scroll-Driven Animations

A native CSS feature for implementing scroll-linked animation without JavaScript.

#### scroll() — scroll-progress timeline

```css
/* A progress bar that fills as the page scrolls */
.progress-bar {
  animation: fill-bar linear;
  animation-timeline: scroll();
  animation-range: 0% 100%;
}

@keyframes fill-bar {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}
```

#### view() — element-visibility timeline

```css
/* Fade in when entering the viewport */
.reveal-card {
  animation: reveal linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;
}

@keyframes reveal {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

#### animation-range named ranges

| Range | Description |
|-------|-------------|
| `entry` | Element enters the scrollport |
| `exit` | Element exits the scrollport |
| `contain` | Element is fully within the scrollport |
| `cover` | From first visible to fully exited |

#### Named Scroll Timelines

```css
.scroll-container {
  scroll-timeline-name: --my-scroller;
  scroll-timeline-axis: block;
  overflow-y: auto;
}

.animated-child {
  animation: slide linear;
  animation-timeline: --my-scroller;
}
```

---

### 2.3 @starting-style

Solves the long-standing problem of animating from `display: none`. Applies to dialog, popover, etc.

```css
/* Dialog entrance animation */
dialog[open] {
  opacity: 1;
  transform: scale(1);
  transition: opacity 0.3s, transform 0.3s, display 0.3s allow-discrete;
}

@starting-style {
  dialog[open] {
    opacity: 0;
    transform: scale(0.95);
  }
}

/* Popover entrance animation */
[popover]:popover-open {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 0.3s, transform 0.3s,
    display 0.3s allow-discrete,
    overlay 0.3s allow-discrete;
}

@starting-style {
  [popover]:popover-open {
    opacity: 0;
    transform: translateY(-10px);
  }
}
```

**Key idea:** `allow-discrete` enables non-continuous transitions of `display` and `overlay`. JavaScript-based "enter animation" hacks become unnecessary.

---

### 2.4 CSS Spring Approximation — linear() function

Native springs are still under discussion in the CSS WG; for now, approximate via `linear()` easing:

```css
/* Snappy spring feel */
--spring-snappy: linear(
  0, 0.009, 0.035 2.1%, 0.141 4.4%, 0.723 12.9%,
  0.938 16.2%, 1.017, 1.077 21.8%, 1.106 24%, 1.113,
  1.109 28.7%, 1.078 33.4%, 1 43.7%, 0.974 53.3%,
  0.965 59.5%, 0.969 68.8%, 0.989 85%, 1
);

/* Bouncy spring feel */
--spring-bouncy: linear(
  0, 0.004, 0.016, 0.035, 0.063 9.1%, 0.141 13.6%,
  0.527 24.2%, 0.767 30.3%, 0.879 33.3%, 1.027 39.4%,
  1.093 42.4%, 1.144 46.5%, 1.154 48.5%, 1.154,
  1.139 54.2%, 1.064 62.6%, 1 73.2%, 0.972 81.5%,
  0.957 86.3%, 0.957 91.1%, 1
);
```

> Jake Archibald's `linear()` generator can convert Framer Motion spring curves into CSS `linear()` values

---

### 2.5 Other Modern CSS Features

#### Animating Custom Properties with @property

```css
@property --gradient-angle {
  syntax: "<angle>";
  initial-value: 0deg;
  inherits: false;
}

.gradient-border {
  --gradient-angle: 0deg;
  background: conic-gradient(from var(--gradient-angle), #e91e63, #9c27b0, #2196f3, #e91e63);
  animation: rotate-gradient 3s linear infinite;
}

@keyframes rotate-gradient {
  to { --gradient-angle: 360deg; }
}
```

#### Container Query Animation

```css
@container sidebar (min-width: 300px) {
  .nav-item {
    transition: padding 0.3s ease;
    padding: 1rem;
  }
}
```

---

## 3. Framer Motion / Motion

### 3.1 Framer Motion → Motion Evolution

In late 2024, Matt Perry (creator of Framer Motion) launched **Motion** (motion.dev) as a framework-independent library. Framer Motion stays React-only; Motion runs on vanilla JS/Vue/Svelte.

```javascript
// Motion (vanilla JS)
import { animate, scroll, inView } from "motion";

animate(".box", { opacity: [0, 1], y: [50, 0] }, { duration: 0.5 });
scroll(animate(".progress", { scaleX: [0, 1] }));
inView(".card", ({ target }) => {
  animate(target, { opacity: 1, y: 0 });
});
```

### 3.2 Spring Physics Parameter Guide

| Feel | stiffness | damping | mass | Use |
|------|-----------|---------|------|-----|
| **Snappy** | 400-500 | 30-35 | 1 | Buttons, toggles, small UI |
| **Responsive** | 300 | 25 | 1 | Cards, modals, medium elements |
| **Gentle** | 150-200 | 20 | 1 | Page transitions, large elements |
| **Bouncy** | 200 | 10-15 | 1 | Playful UI, celebration, games |
| **Heavy** | 100-150 | 25-30 | 2-3 | Draggable elements, panels |
| **Stiff** | 600+ | 40+ | 1 | Instant feel, toolbar items |

### 3.3 Core Patterns

#### Layout Animation

```jsx
{/* Automatic layout animation — Framer Motion's killer feature */}
<motion.div layout transition={{ type: "spring", stiffness: 300, damping: 30 }}>
  {isExpanded ? <ExpandedContent /> : <CollapsedContent />}
</motion.div>

{/* Shared layout animation (cross-component) */}
<LayoutGroup>
  {items.map(item => (
    <motion.div key={item.id} layoutId={item.id}>
      {selectedId === item.id ? <FullCard /> : <ThumbCard />}
    </motion.div>
  ))}
</LayoutGroup>
```

#### AnimatePresence (exit animation)

```jsx
<AnimatePresence mode="wait">
  {isVisible && (
    <motion.div
      key="modal"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
    />
  )}
</AnimatePresence>
```

#### Gesture Animation

```jsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  whileFocus={{ boxShadow: "0 0 0 3px rgba(66, 153, 225, 0.6)" }}
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
/>

{/* Drag with constraints */}
<motion.div
  drag
  dragConstraints={{ left: -100, right: 100, top: -50, bottom: 50 }}
  dragElastic={0.2}
  dragTransition={{ bounceStiffness: 600, bounceDamping: 20 }}
/>
```

#### Stagger Children

```jsx
const containerVariants = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.08, delayChildren: 0.1 }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};

<motion.ul variants={containerVariants} initial="hidden" animate="show">
  {items.map(item => (
    <motion.li key={item.id} variants={itemVariants} />
  ))}
</motion.ul>
```

#### Scroll-Based Animation

```jsx
import { useScroll, useTransform, motion } from "framer-motion";

function ParallaxHero() {
  const { scrollYProgress } = useScroll();
  const y = useTransform(scrollYProgress, [0, 1], [0, -300]);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);

  return (
    <motion.div style={{ y, opacity }}>
      <h1>Parallax Hero</h1>
    </motion.div>
  );
}

// Scroll tracking relative to a specific element
function RevealSection() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"]
  });
  const scale = useTransform(scrollYProgress, [0, 0.5], [0.8, 1]);

  return <motion.section ref={ref} style={{ scale }} />;
}
```

#### Performance Patterns

```jsx
// Use motion values instead of state for high-frequency updates
const mouseX = useMotionValue(0);
const mouseY = useMotionValue(0);

// Apply willChange for complex animations
<motion.div style={{ willChange: "transform" }} />

// Animate position only (exclude size)
<motion.div layout="position" />

// Reduced motion support
const prefersReducedMotion = useReducedMotion();
<motion.div animate={prefersReducedMotion ? {} : { scale: 1.1 }} />
```

---

## 4. GSAP

### 4.1 GSAP and AI Code Generation

GSAP is the gold standard for complex, timeline-based animation. Adoption broadened after the move to a fully free license in 2025.

#### ScrollTrigger (the most requested pattern)

```javascript
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger);

// Pin + scrub (horizontal scroll)
gsap.to(".horizontal-panels", {
  xPercent: -100 * (panels.length - 1),
  ease: "none",
  scrollTrigger: {
    trigger: ".horizontal-container",
    pin: true,
    scrub: 1,  // number = smooth scrubbing
    snap: 1 / (panels.length - 1),
    end: () => "+=" + document.querySelector(".horizontal-container").offsetWidth,
  }
});

// Batch reveal (best for many elements)
ScrollTrigger.batch(".reveal-item", {
  onEnter: (elements) => {
    gsap.from(elements, {
      autoAlpha: 0,
      y: 60,
      stagger: 0.1,
      duration: 0.8,
      ease: "power2.out",
    });
  },
  once: true,
});
```

#### Timeline Orchestration

```javascript
const tl = gsap.timeline({
  defaults: { ease: "power3.out", duration: 0.8 }
});

tl.from(".hero-title", { y: 100, opacity: 0 })
  .from(".hero-subtitle", { y: 60, opacity: 0 }, "-=0.4")
  .from(".hero-cta", { scale: 0.8, opacity: 0 }, "-=0.3")
  .from(".hero-image", { x: 100, opacity: 0 }, "-=0.5");
```

#### React Cleanup Pattern (mandatory)

```jsx
useEffect(() => {
  const ctx = gsap.context(() => {
    gsap.from(".title", { opacity: 0, y: 50 });
  }, containerRef); // scope by ref

  return () => ctx.revert(); // must clean up!
}, []);
```

#### Text Animation (SplitText)

```javascript
const split = new SplitText(".heading", { type: "chars,words,lines" });

gsap.from(split.chars, {
  opacity: 0,
  y: 50,
  rotateX: -90,
  stagger: 0.02,
  duration: 0.6,
  ease: "back.out(1.7)",
});
```

#### Common Mistakes in AI-Generated GSAP Code

1. Missing `ScrollTrigger.refresh()` after dynamic content loads
2. Not using `gsap.context()` cleanup in React
3. Animating non-composite properties (layout thrashing)
4. Use `scrub: 1` instead of `scrub: true` (smooth scrubbing recommended)
5. Missing `invalidateOnRefresh: true` in responsive layouts

---

## 5. Lottie / Rive

### 5.1 Lottie

AI tools cannot generate Lottie JSON directly (export from After Effects/Figma is required), but are **excellent at writing integration code**.

```jsx
// dotLottie (compressed format, 10x smaller)
import { DotLottieReact } from "@lottiefiles/dotlottie-react";

<DotLottieReact
  src="/animations/loading.lottie"
  loop
  autoplay
/>
```

#### Scroll-Synced Lottie

```jsx
function ScrollLottie() {
  const { scrollYProgress } = useScroll();
  const frame = useTransform(scrollYProgress, [0, 1], [0, 100]);
  const [dotLottie, setDotLottie] = useState(null);

  useEffect(() => {
    return frame.onChange(v => { dotLottie?.setFrame(v); });
  }, [dotLottie, frame]);

  return (
    <DotLottieReact
      src="/scroll-animation.lottie"
      autoplay={false}
      dotLottieRefCallback={setDotLottie}
    />
  );
}
```

### 5.2 Rive

A rising alternative to Lottie. **State-machine-based** interactive animation is its core strength.

| Comparison | Lottie | Rive |
|------------|--------|------|
| **Interaction** | Controlled by code | State machines (defined in the editor) |
| **File size** | JSON (large) / dotLottie (small) | Binary (small) |
| **Rendering** | Pre-baked | Runtime vector |
| **Hover/click reactions** | Code required | Configured in the editor |

```jsx
import { useRive, useStateMachineInput } from "@rive-app/react-canvas";

function InteractiveButton() {
  const { rive, RiveComponent } = useRive({
    src: "/button.riv",
    stateMachines: "ButtonState",
    autoplay: true,
  });

  const hoverInput = useStateMachineInput(rive, "ButtonState", "isHovered");

  return (
    <RiveComponent
      onMouseEnter={() => hoverInput && (hoverInput.value = true)}
      onMouseLeave={() => hoverInput && (hoverInput.value = false)}
    />
  );
}
```

---

## 6. Micro-Interaction Patterns

### 6.1 Button Feedback

```css
/* CSS-only — multi-layer feedback */
.btn {
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.btn:active {
  transform: translateY(0) scale(0.98);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition-duration: 0.05s;
}
```

```jsx
// Framer Motion button
<motion.button
  whileHover={{ scale: 1.02, y: -1 }}
  whileTap={{ scale: 0.98 }}
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
/>
```

### 6.2 Loading States

#### Skeleton Screen

```css
.skeleton {
  background: linear-gradient(
    90deg,
    hsl(0 0% 90%) 25%,
    hsl(0 0% 95%) 50%,
    hsl(0 0% 90%) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: 4px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
  .skeleton {
    background: linear-gradient(90deg,
      hsl(0 0% 15%) 25%, hsl(0 0% 20%) 50%, hsl(0 0% 15%) 75%);
  }
}
```

### 6.3 Toast Notifications

```jsx
<AnimatePresence>
  {toasts.map(toast => (
    <motion.div
      key={toast.id}
      layout
      initial={{ opacity: 0, y: 50, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, x: 100, transition: { duration: 0.2 } }}
      transition={{ type: "spring", stiffness: 350, damping: 25 }}
    >
      {toast.message}
    </motion.div>
  ))}
</AnimatePresence>
```

### 6.4 Toggle / Switch

```jsx
<motion.div
  onClick={() => setIsOn(!isOn)}
  style={{
    width: 50, height: 28, borderRadius: 14,
    background: isOn ? "#4CAF50" : "#ccc",
    padding: 3, cursor: "pointer",
    display: "flex", justifyContent: isOn ? "flex-end" : "flex-start"
  }}
>
  <motion.div
    layout
    transition={{ type: "spring", stiffness: 500, damping: 30 }}
    style={{ width: 22, height: 22, borderRadius: "50%", background: "#fff" }}
  />
</motion.div>
```

### 6.5 Accordion / Expand-Collapse

```jsx
<motion.div
  animate={{ height: isOpen ? "auto" : 0 }}
  initial={false}
  transition={{ type: "spring", stiffness: 300, damping: 30 }}
  style={{ overflow: "hidden" }}
>
  <div style={{ padding: "1rem" }}>{content}</div>
</motion.div>
```

---

## 7. Scroll-Based Animation

### 7.1 Parallax

#### CSS Scroll-Driven Parallax

```css
.parallax-element {
  animation: parallax linear;
  animation-timeline: scroll();
}

@keyframes parallax {
  from { transform: translateY(0); }
  to { transform: translateY(calc(var(--parallax-speed, 0.5) * -200px)); }
}
```

### 7.2 Scroll Reveal (CSS-only, 2025 style)

```css
.reveal {
  opacity: 0;
  transform: translateY(30px);
  animation: reveal-up 0.6s ease both;
  animation-timeline: view();
  animation-range: entry 0% entry 40%;
}

@keyframes reveal-up {
  to { opacity: 1; transform: translateY(0); }
}
```

### 7.3 Reading-Progress Bar

```css
.reading-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  background: var(--color-primary);
  transform-origin: left;
  animation: reading-progress linear;
  animation-timeline: scroll(root);
}

@keyframes reading-progress {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}
```

### 7.4 Sticky Header Shrink

```css
.sticky-header {
  position: sticky;
  top: 0;
  animation: shrink-header linear both;
  animation-timeline: scroll();
  animation-range: 0px 200px;
}

@keyframes shrink-header {
  from {
    padding-block: 2rem;
    font-size: 2rem;
  }
  to {
    padding-block: 0.5rem;
    font-size: 1rem;
    backdrop-filter: blur(10px);
    background: oklch(1 0 0 / 0.8);
  }
}
```

### 7.5 GSAP Section Pin Sequence

```javascript
gsap.timeline({
  scrollTrigger: {
    trigger: ".features-section",
    start: "top top",
    end: "+=300%",
    pin: true,
    scrub: 1,
  }
})
.to(".feature-1", { opacity: 0, y: -50 })
.from(".feature-2", { opacity: 0, y: 50 })
.to(".feature-2", { opacity: 0, y: -50 })
.from(".feature-3", { opacity: 0, y: 50 });
```

---

## 8. Page Transitions

### 8.1 View Transitions API + SPA

```typescript
// Transition utility
async function navigateWithTransition(updateFn: () => void) {
  if (!document.startViewTransition) {
    updateFn();
    return;
  }
  const transition = document.startViewTransition(updateFn);
  await transition.finished;
}
```

#### Direction-based Page Transition

```css
/* Forward navigation: slide in from the right */
::view-transition-old(root) {
  animation: slide-out-left 0.3s ease;
}
::view-transition-new(root) {
  animation: slide-in-right 0.3s ease;
}

/* Backward navigation: slide in from the left */
.back-navigation::view-transition-old(root) {
  animation: slide-out-right 0.3s ease;
}
.back-navigation::view-transition-new(root) {
  animation: slide-in-left 0.3s ease;
}
```

### 8.2 Framer Motion Page Transition

```jsx
// Next.js App Router's template.tsx
"use client";
import { AnimatePresence, motion } from "framer-motion";
import { usePathname } from "next/navigation";

export default function Template({ children }) {
  const pathname = usePathname();

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
```

---

## 9. Performance Optimization

### 9.1 GPU-Accelerated Properties

| Category | Property | Cost |
|----------|----------|------|
| **GPU-accelerated (recommended)** | `transform`, `opacity`, `filter`, `backdrop-filter`, `clip-path` | Minimal |
| **Triggers paint (caution)** | `box-shadow`, `border-radius`, `background` | Medium |
| **Triggers layout (forbidden)** | `width`, `height`, `top`, `left`, `margin`, `padding`, `font-size` | High |

### 9.2 Proper Use of will-change

```css
/* Good: applied right before animation */
.card:hover {
  will-change: transform;
}

/* Bad: always on (wastes GPU memory) */
.card {
  will-change: transform; /* don't do this */
}
```

```javascript
// Best: apply before animation in JS, remove after
element.style.willChange = 'transform';
element.addEventListener('transitionend', () => {
  element.style.willChange = 'auto';
}, { once: true });
```

### 9.3 The contain Property

```css
/* Isolate animation repaint */
.animated-card {
  contain: layout style paint;
}

/* Scroll container with many animated children */
.scroll-list-item {
  content-visibility: auto;
  contain-intrinsic-size: 0 80px;
}
```

### 9.4 Performance Measurement

```javascript
// Detect animation frame drops
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.duration > 50) { // 3+ frames at 60fps
      console.warn('Long animation frame:', entry.duration, 'ms');
    }
  }
});
observer.observe({ type: 'long-animation-frame', buffered: true });
```

---

## 10. Animation Prompting Techniques

### 10.1 Prompt Quality Tiers

#### Tier 1: Basic (generic result)
> "Add animation to this card"

#### Tier 2: Descriptive (better result)
> "Add a hover animation to this card: rises 4px while the shadow expands smoothly, with a spring transition that is responsive but not bouncy"

#### Tier 3: Detailed spec (best result)
> "Add a hover interaction to the product card:
> - On hover: translateY(-4px), box-shadow 0 2px 8px → 0 8px 24px (opacity 0.08)
> - Spring: stiffness 400, damping 25 (fast and stable)
> - Inner image scales to 1.03 (overflow hidden)
> - Title color transitions gray-700 → primary
> - Tap/active: scale 0.98 (tactile feedback)
> - prefers-reduced-motion: keep opacity only, no transform
> - Use Framer Motion (already in the project)"

### 10.2 Proven Prompt Patterns

| Pattern | Example |
|---------|---------|
| **Reference a real product** | "Like the Apple Music 'Now Playing' card — springs up from the bottom while the blurred background fades in" |
| **Specify physics** | "Spring with mass: 1, stiffness: 300, damping: 25 — similar to iOS's default spring" |
| **Describe the feel** | "Should be snappy and responsive, not floaty. Tactile feel like pressing a physical button" |
| **Orchestration** | "Stagger list items with a 60ms delay. Container fades in first (200ms), then children rise one by one" |
| **State accessibility** | "Support prefers-reduced-motion. Reduced-motion users skip transforms; show only a short opacity fade" |
| **Easing context** | "ease-out on entry, ease-in on exit, ease-in-out on state changes" |
| **Scroll behavior** | "Use CSS scroll-driven animations. Start at 20% visible, fully revealed at 60%" |

### 10.3 English Prompt Examples

> "Add a hover animation to this card. Rises 4px and the shadow expands smoothly. Use spring physics (stiffness 400, damping 25) so it's responsive yet natural. Also support prefers-reduced-motion."

> "List items appear one by one as the user scrolls. Use CSS scroll-driven animations. Begin appearing at 20% in the viewport and fully visible at 60%."

---

## 11. Animation Design Principles

### 11.1 Applying Disney's 12 Principles to UI

| Principle | UI application | Example |
|-----------|----------------|---------|
| **Squash & Stretch** | Button press | scale 0.98 on tap |
| **Anticipation** | Subtle pull-back before motion | Button pulls back slightly before navigating |
| **Staging** | Focus on the core action | Background blur/darken when a modal opens |
| **Follow-through & Overlap** | List sequential stop | Items don't stop together — they stagger |
| **Slow In, Slow Out** | Apply easing | Enter: ease-out; Exit: ease-in |
| **Arc** | Natural curved paths | Non-linear movement via `offset-path` |
| **Secondary Action** | Icon bounce + text fade | Ripple effect + color change concurrently |
| **Timing** | Time per interaction type | Micro: 100-200ms, Page: 300-500ms |
| **Exaggeration** | Spring overshoot | Scale above 1.0 then settle |
| **Appeal** | Purposeful smooth motion | Intentional, polished movement |

### 11.2 Timing Guidelines

| Interaction type | Duration | Easing |
|------------------|----------|--------|
| Button hover | 100-150ms | ease-out |
| Button active/tap | 50-100ms | ease-in |
| Tooltip show | 150-200ms | ease-out |
| Tooltip hide | 100-150ms | ease-in |
| Dropdown open | 200-250ms | ease-out or spring |
| Modal enter | 250-350ms | spring (300, 25) |
| Modal exit | 200-250ms | ease-in |
| Page transition | 300-500ms | ease-in-out or spring |
| Toast enter | 300-400ms | spring (350, 25) |
| Toast exit | 200ms | ease-in |
| Skeleton shimmer | 1500ms | ease-in-out, infinite |
| Loading spinner | 800-1200ms | linear, infinite |
| Stagger delay | 50-100ms | per child |
| Scroll reveal | 400-600ms | ease-out or spring |

### 11.3 Easing Curve Reference

```css
/* Material Design */
--ease-standard: cubic-bezier(0.4, 0, 0.2, 1);
--ease-decelerate: cubic-bezier(0, 0, 0.2, 1);    /* for entry */
--ease-accelerate: cubic-bezier(0.4, 0, 1, 1);     /* for exit */

/* Apple style */
--ease-apple: cubic-bezier(0.25, 0.1, 0.25, 1);
--ease-apple-bounce: cubic-bezier(0.175, 0.885, 0.32, 1.275);
```

---

## 12. Mobile-Specific Animation

### 12.1 Touch Gestures

#### Swipe to Dismiss

```jsx
<motion.div
  drag="x"
  dragConstraints={{ left: 0, right: 0 }}
  onDragEnd={(_, info) => {
    if (Math.abs(info.offset.x) > 100 || Math.abs(info.velocity.x) > 500) {
      onDismiss();
    }
  }}
/>
```

#### Pull-to-Refresh

```jsx
<motion.div
  drag="y"
  dragConstraints={{ top: 0, bottom: 100 }}
  dragElastic={0.5}
  style={{ y }}
  onDragEnd={(_, info) => {
    if (info.offset.y > 80) onRefresh();
  }}
>
  <motion.div className="spinner" style={{ rotate: spinnerRotate, opacity: pullProgress }} />
  {children}
</motion.div>
```

#### iOS-style Back Swipe

```jsx
<motion.div
  initial={{ x: "100%" }}
  animate={{ x: 0 }}
  exit={{ x: "100%" }}
  transition={{ type: "spring", stiffness: 300, damping: 30 }}
  drag="x"
  dragConstraints={{ left: 0 }}
  dragElastic={0}
  onDragEnd={(_, info) => {
    if (info.offset.x > 100 || info.velocity.x > 300) {
      router.back();
    }
  }}
/>
```

#### Bottom Sheet

```jsx
<motion.div
  drag="y"
  dragConstraints={{ top: -sheetHeight, bottom: 0 }}
  dragElastic={0.1}
  initial={{ y: "100%" }}
  animate={{ y: isOpen ? 0 : "100%" }}
  transition={{ type: "spring", stiffness: 300, damping: 30 }}
  onDragEnd={(_, info) => {
    if (info.velocity.y > 500 || info.offset.y > sheetHeight * 0.5) {
      onClose();
    }
  }}
>
  <div className="drag-handle" />
  {children}
</motion.div>
```

### 12.2 Haptic Feedback

```javascript
// Web Vibration API
function hapticFeedback(type = 'light') {
  if (!navigator.vibrate) return;
  switch (type) {
    case 'light': navigator.vibrate(10); break;
    case 'medium': navigator.vibrate(20); break;
    case 'heavy': navigator.vibrate(30); break;
    case 'success': navigator.vibrate([10, 50, 10]); break;
    case 'error': navigator.vibrate([30, 50, 30, 50, 30]); break;
  }
}

// React Native (Expo Haptics)
import * as Haptics from 'expo-haptics';
Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);   // tap
Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);  // toggle
Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success); // success
```

### 12.3 Mobile Performance Cautions

- Animate only `transform` and `opacity` (mandatory on mobile)
- Use `passive: true` on touch event listeners
- Avoid `box-shadow` animation (very expensive on mobile GPUs)
- Don't overuse `will-change: transform` (each instance consumes mobile GPU memory)
- Test under CPU throttling 4x/6x (simulate low-end devices)
- Apply `content-visibility: auto` to offscreen content in long lists

---

## 13. 3D / WebGL Animation

### React Three Fiber (R3F)

```jsx
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Float, Environment } from "@react-three/drei";

function Scene() {
  return (
    <Canvas camera={{ position: [0, 0, 5] }}>
      <Environment preset="city" />
      <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
        <mesh>
          <torusKnotGeometry args={[1, 0.3, 128, 32]} />
          <meshStandardMaterial color="#6366f1" metalness={0.8} roughness={0.2} />
        </mesh>
      </Float>
      <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} />
    </Canvas>
  );
}
```

### Commonly Used drei Helpers

| Helper | Effect |
|--------|--------|
| `<Float>` | Smooth floating animation |
| `<MeshDistortMaterial>` | Organic distortion |
| `<MeshWobbleMaterial>` | Wobble effect |
| `<Trail>` | Motion trail |
| `<Sparkles>` | Sparkle particles |
| `<Stars>` | Star field background |

### 3D Performance

- Use `instancedMesh` for repeated geometry
- `<AdaptiveDpr>` for automatic resolution scaling
- Compress textures with KTX2/Basis
- Minimize computation inside `useFrame`

---

## 14. Library Comparison

### Selection Criteria

| Situation | Recommendation |
|-----------|----------------|
| Simple hover/focus/active | **CSS** |
| Scroll-linked (standard) | **CSS** scroll-driven animations |
| Entry from `display: none` | **CSS** @starting-style |
| Skeleton, spinner, progress | **CSS** |
| React layout animation | **Framer Motion** (killer feature) |
| Exit animation | **Framer Motion** AnimatePresence |
| Gestures (drag, swipe) | **Framer Motion** |
| Complex timeline orchestration | **GSAP** |
| SVG morph, path animation | **GSAP** |
| Advanced scroll pinning | **GSAP** ScrollTrigger |
| Text split animation | **GSAP** SplitText |
| Non-React (Vue, Svelte, vanilla) | **Motion** (motion.dev) |
| Best AI-tool support | Hybrid of **CSS + Framer Motion** |

> **Most common 2025 pattern**: CSS for simple states, Framer Motion for component lifecycle (enter/exit/layout). Most AI tools produce this combination by default.

### Bundle Size Comparison

| Library | Size |
|---------|------|
| CSS | 0 KB |
| Motion (vanilla) | ~18 KB |
| anime.js | ~17 KB |
| GSAP | ~28 KB (+plugins) |
| Framer Motion | ~32 KB |

---

## 15. Accessibility

### 15.1 3-Tier Approach (2025 industry best practice)

```css
/* Tier 1: full animation (default) */
.card {
  transition: transform 0.3s, opacity 0.3s ease;
}

/* Tier 2: reduced — simplification, not removal */
@media (prefers-reduced-motion: reduce) {
  .card {
    transition: opacity 0.15s ease; /* keep opacity only; drop transform */
  }

  .parallax { transform: none; }
  .auto-scroll { scroll-behavior: auto; }

  /* Decorative animations are fully removed */
  .background-particles,
  .floating-shapes {
    animation: none;
  }

  /* Essential feedback is preserved */
  .button { transition: background-color 0.1s; }
}

/* Tier 3: no animation (custom toggle) */
[data-motion="none"] * {
  animation: none !important;
  transition: none !important;
}
```

### 15.2 Vestibular Disorder Considerations

**Dangerous animation patterns:**
- Large-scale motion (full-page parallax, zooming backgrounds)
- Rotation and spinning
- Full-screen rapid movement
- Auto-playing carousels/sliders
- Sustained/repeating peripheral animation

**Safe animation patterns:**
- Opacity fades (almost always safe)
- Small transforms (< 10px movement)
- Color transitions
- Border/outline changes
- Short, purposeful feedback animations

### 15.3 WCAG 2.2 Requirements

| Criterion | Level | Requirement |
|-----------|-------|-------------|
| 2.3.1 Three Flashes or Below | A | No content flashes more than 3 times per second |
| 2.3.3 Animation from Interactions | AAA | Interaction-triggered motion must be disable-able |
| 2.2.2 Pause, Stop, Hide | A | Auto-playing animation longer than 5s requires a control mechanism |

### 15.4 User Toggle Implementation

```jsx
// Provide an in-app control in addition to the system setting
const [motionLevel, setMotionLevel] = useState('full');

<select value={motionLevel} onChange={e => setMotionLevel(e.target.value)}>
  <option value="full">Full animations</option>
  <option value="reduced">Reduced animations</option>
  <option value="none">No animations</option>
</select>
```

---

## 16. Animation Design Tokens

### Standardized Motion Token System

```css
:root {
  /* Duration tokens */
  --duration-instant: 50ms;
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  --duration-glacial: 800ms;

  /* Easing tokens */
  --ease-default: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.175, 0.885, 0.32, 1.275);
  --ease-spring: linear(/* spring values */);

  /* Spring tokens (for JS libraries — stiffness / damping) */
  --spring-snappy: 400 / 30;
  --spring-gentle: 200 / 20;
  --spring-bouncy: 300 / 10;
}
```

### Motion Design System References

| System | Classification | Description |
|--------|----------------|-------------|
| **IBM Carbon Motion** | Productive / Expressive | Fast & minimal / Playful & engaging |
| **Material Design 3** | Emphasized / Standard / De-emphasized | 500ms / 300ms / 200ms |
| **Apple HIG** | Fluid spring | Context-specific damping ratios |

---

## 17. Emerging Trends

### CSS-First Renaissance

A strong trend where animations once requiring JavaScript become possible with CSS alone:

| Previously (JS required) | Now (CSS possible) |
|--------------------------|--------------------|
| ScrollTrigger | `animation-timeline: scroll()` |
| AnimatePresence | `@starting-style` |
| JS spring library | `linear()` easing |
| React transition libraries | View Transitions API |

### Server-Driven Animation

A pattern that takes animation configuration from a CMS/API and applies it:

```json
{
  "entrance": {
    "type": "spring",
    "stiffness": 300,
    "damping": 25,
    "delay": 0.1,
    "stagger": 0.08
  }
}
```

> Update animations without redeploy; supports A/B testing

### "60fps or Nothing" Mindset

- Chrome DevTools animation inspector improvements
- Long Animation Frame API for jank detection
- Core Web Vitals INP (Interaction to Next Paint) reflects animation performance
- **Budget animation complexity** like bundle size

---

## References

- [View Transitions API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transitions_API)
- [CSS Scroll-Driven Animations](https://developer.chrome.com/docs/css-ui/scroll-driven-animations)
- [Framer Motion Documentation](https://www.framer.com/motion/)
- [Motion (motion.dev)](https://motion.dev/)
- [GSAP Documentation](https://gsap.com/docs/)
- [Rive Documentation](https://rive.app/docs/)
- [LottieFiles](https://lottiefiles.com/)
- [React Three Fiber](https://docs.pmnd.rs/react-three-fiber)
- ASTRA `docs/ux/ux-interaction-patterns.md` — interaction patterns guide
- ASTRA `docs/ux/mobile-design-guide.md` — mobile design guide
- ASTRA `docs/ux/vibe-coding-design-guide.md` — vibe coding design guide
