# Vibe Coding Animation Guide

> 바이브 코딩 도구를 활용한 UI 애니메이션 구현 기법, 라이브러리 비교, 프롬프팅 전략, 성능 최적화, 접근성 가이드

## 1. 개요

### 바이브 코딩과 애니메이션

바이브 코딩 도구(v0, Cursor, Claude Code, Bolt 등)는 자연어로 애니메이션을 설명하면 동작하는 코드를 생성한다. 이 가이드는 **전문 디자이너와 개발자가 AI 도구로 고품질 애니메이션을 구현하는 방법**을 다룬다.

### AI 도구별 애니메이션 생성 특성

| 도구 | 기본 출력 | 강점 | 약점 |
|------|----------|------|------|
| **v0** | Framer Motion + Tailwind | 페이지 전환, 카드 호버, 리스트 애니메이션 | 복잡한 오케스트레이션 부족 |
| **Cursor** | 프로젝트 기존 라이브러리 감지 | 기존 애니메이션 수정 및 정제에 강함 | — |
| **Claude Code** | CSS / Framer Motion / GSAP | 접근성 인식 (`prefers-reduced-motion` 자동 포함), 복잡한 시퀀스 | — |
| **Bolt / Lovable** | CSS (간단) 또는 Framer Motion (React) | 전체 페이지 애니메이션 빠른 생성 | 프로덕션 수준의 폴리시 부족 |

### AI 생성 애니메이션의 공통 패턴과 한계

**공통 패턴:**
- 단순 hover/focus 상태 → CSS transition 기본 사용
- React 컴포넌트 → Framer Motion 우선 선택
- 스프링 물리를 베지어 곡선보다 선호 (더 자연스러운 느낌)
- 스태거 애니메이션(자식 순차 진입)이 시그니처 패턴

**한계:**
- 복잡한 다중 요소 오케스트레이션에서 타이밍 조율 미흡
- GPU 레이어, 컴포지트 힌트 등 성능 최적화 누락
- 스크롤 애니메이션의 적절한 클린업(메모리 누수) 부재
- `prefers-reduced-motion`을 명시적으로 요청하지 않으면 누락되는 경우 존재

---

## 2. 모던 CSS 애니메이션 (2025-2026)

### 2.1 View Transitions API

브라우저 지원이 확대되며 웹 애니메이션의 가장 중요한 발전으로 평가받는 API.

#### SPA 문서 전환

```css
/* JavaScript에서 전환 트리거 */
document.startViewTransition(() => {
  updateDOM(); // DOM 변경
});

/* 기본 크로스페이드 (무료) */
::view-transition-old(root) {
  animation: fade-out 0.3s ease;
}
::view-transition-new(root) {
  animation: fade-in 0.3s ease;
}
```

#### Named View Transitions (공유 요소 전환)

```css
/* 리스트 페이지의 카드 이미지 */
.product-card .product-image {
  view-transition-name: hero-image;
}

/* 상세 페이지의 히어로 이미지 — 같은 이름으로 연결 */
.product-detail .hero-image {
  view-transition-name: hero-image;
}

/* 전환 애니메이션 커스터마이징 */
::view-transition-group(hero-image) {
  animation-duration: 0.4s;
  animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
```

#### MPA 크로스 문서 전환

```css
/* 양쪽 페이지에서 opt-in */
@view-transition {
  navigation: auto;
}
```

#### 동적 view-transition-name (리스트용)

```jsx
{/* 아이템별 고유 이름 할당 */}
<div style={{ viewTransitionName: `product-${item.id}` }}>
  <img src={item.image} />
</div>
```

**주요 패턴:**
- `view-transition-class`로 그룹 전환 적용
- `@media (prefers-reduced-motion: reduce)`와 결합하여 전환 비활성화
- Next.js App Router, Astro, SvelteKit 모두 View Transition 지원 추가

---

### 2.2 Scroll-Driven Animations

JavaScript 없이 스크롤 연동 애니메이션을 구현하는 CSS 네이티브 기능.

#### scroll() — 스크롤 진행률 타임라인

```css
/* 스크롤에 따라 채워지는 프로그레스 바 */
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

#### view() — 요소 가시성 타임라인

```css
/* 뷰포트 진입 시 페이드인 */
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

#### animation-range 네임드 범위

| 범위 | 설명 |
|------|------|
| `entry` | 요소가 스크롤포트에 진입 |
| `exit` | 요소가 스크롤포트에서 퇴장 |
| `contain` | 요소가 스크롤포트 내에 완전히 포함 |
| `cover` | 처음 보이기 시작부터 완전히 퇴장까지 |

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

`display: none`에서 애니메이션하는 오랜 문제를 해결. dialog, popover 등에 적용.

```css
/* 다이얼로그 등장 애니메이션 */
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

/* 팝오버 등장 애니메이션 */
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

**핵심:** `allow-discrete`로 `display`와 `overlay` 프로퍼티의 불연속 전환 가능. JavaScript 기반 "진입 애니메이션" 핵이 불필요해짐.

---

### 2.4 CSS 스프링 근사 — linear() 함수

CSS WG에서 네이티브 스프링이 논의 중이지만, 현재는 `linear()` 이징 함수로 근사:

```css
/* 스내피한 스프링 느낌 */
--spring-snappy: linear(
  0, 0.009, 0.035 2.1%, 0.141 4.4%, 0.723 12.9%,
  0.938 16.2%, 1.017, 1.077 21.8%, 1.106 24%, 1.113,
  1.109 28.7%, 1.078 33.4%, 1 43.7%, 0.974 53.3%,
  0.965 59.5%, 0.969 68.8%, 0.989 85%, 1
);

/* 바운시한 스프링 느낌 */
--spring-bouncy: linear(
  0, 0.004, 0.016, 0.035, 0.063 9.1%, 0.141 13.6%,
  0.527 24.2%, 0.767 30.3%, 0.879 33.3%, 1.027 39.4%,
  1.093 42.4%, 1.144 46.5%, 1.154 48.5%, 1.154,
  1.139 54.2%, 1.064 62.6%, 1 73.2%, 0.972 81.5%,
  0.957 86.3%, 0.957 91.1%, 1
);
```

> Jake Archibald의 `linear()` 제너레이터로 Framer Motion 스프링 커브를 CSS `linear()` 값으로 변환 가능

---

### 2.5 기타 모던 CSS 기능

#### @property로 커스텀 프로퍼티 애니메이션

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

#### Container Query 애니메이션

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

### 3.1 Framer Motion → Motion 진화

2024년 말 Matt Perry(Framer Motion 창시자)가 **Motion**(motion.dev)을 프레임워크 독립적 라이브러리로 출시. Framer Motion은 React 전용으로 유지, Motion은 바닐라 JS/Vue/Svelte에서 사용 가능.

```javascript
// Motion (바닐라 JS)
import { animate, scroll, inView } from "motion";

animate(".box", { opacity: [0, 1], y: [50, 0] }, { duration: 0.5 });
scroll(animate(".progress", { scaleX: [0, 1] }));
inView(".card", ({ target }) => {
  animate(target, { opacity: 1, y: 0 });
});
```

### 3.2 스프링 물리 파라미터 가이드

| 느낌 | stiffness | damping | mass | 용도 |
|------|-----------|---------|------|------|
| **스내피** | 400-500 | 30-35 | 1 | 버튼, 토글, 소형 UI |
| **반응적** | 300 | 25 | 1 | 카드, 모달, 중형 요소 |
| **부드러운** | 150-200 | 20 | 1 | 페이지 전환, 대형 요소 |
| **바운시** | 200 | 10-15 | 1 | 플레이풀 UI, 축하, 게임 |
| **무거운** | 100-150 | 25-30 | 2-3 | 드래그 가능 요소, 패널 |
| **딱딱한** | 600+ | 40+ | 1 | 즉각적 느낌, 툴바 아이템 |

### 3.3 핵심 패턴

#### 레이아웃 애니메이션

```jsx
{/* 자동 레이아웃 애니메이션 — Framer Motion의 킬러 기능 */}
<motion.div layout transition={{ type: "spring", stiffness: 300, damping: 30 }}>
  {isExpanded ? <ExpandedContent /> : <CollapsedContent />}
</motion.div>

{/* 공유 레이아웃 애니메이션 (크로스 컴포넌트) */}
<LayoutGroup>
  {items.map(item => (
    <motion.div key={item.id} layoutId={item.id}>
      {selectedId === item.id ? <FullCard /> : <ThumbCard />}
    </motion.div>
  ))}
</LayoutGroup>
```

#### AnimatePresence (퇴장 애니메이션)

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

#### 제스처 애니메이션

```jsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  whileFocus={{ boxShadow: "0 0 0 3px rgba(66, 153, 225, 0.6)" }}
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
/>

{/* 드래그 (제약 조건 포함) */}
<motion.div
  drag
  dragConstraints={{ left: -100, right: 100, top: -50, bottom: 50 }}
  dragElastic={0.2}
  dragTransition={{ bounceStiffness: 600, bounceDamping: 20 }}
/>
```

#### 스태거 자식 요소

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

#### 스크롤 기반 애니메이션

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

// 특정 요소 기준 스크롤 추적
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

#### 성능 패턴

```jsx
// 고빈도 업데이트에는 state 대신 motion value 사용
const mouseX = useMotionValue(0);
const mouseY = useMotionValue(0);

// 복잡한 애니메이션에 willChange 적용
<motion.div style={{ willChange: "transform" }} />

// 위치만 애니메이션 (크기 제외)
<motion.div layout="position" />

// 축소 모션 지원
const prefersReducedMotion = useReducedMotion();
<motion.div animate={prefersReducedMotion ? {} : { scale: 1.1 }} />
```

---

## 4. GSAP

### 4.1 GSAP와 AI 코드 생성

GSAP는 복잡한 타임라인 기반 애니메이션의 골드 스탠다드. 2025년 완전 무료 라이센스로 전환되며 채택이 확대됨.

#### ScrollTrigger (가장 많이 요청되는 패턴)

```javascript
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger);

// 핀 + 스크럽 (수평 스크롤)
gsap.to(".horizontal-panels", {
  xPercent: -100 * (panels.length - 1),
  ease: "none",
  scrollTrigger: {
    trigger: ".horizontal-container",
    pin: true,
    scrub: 1,  // 숫자 = 부드러운 스크러빙
    snap: 1 / (panels.length - 1),
    end: () => "+=" + document.querySelector(".horizontal-container").offsetWidth,
  }
});

// 배치 리빌 (다수 요소에 최적)
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

#### 타임라인 오케스트레이션

```javascript
const tl = gsap.timeline({
  defaults: { ease: "power3.out", duration: 0.8 }
});

tl.from(".hero-title", { y: 100, opacity: 0 })
  .from(".hero-subtitle", { y: 60, opacity: 0 }, "-=0.4")
  .from(".hero-cta", { scale: 0.8, opacity: 0 }, "-=0.3")
  .from(".hero-image", { x: 100, opacity: 0 }, "-=0.5");
```

#### React 클린업 패턴 (필수)

```jsx
useEffect(() => {
  const ctx = gsap.context(() => {
    gsap.from(".title", { opacity: 0, y: 50 });
  }, containerRef); // ref로 스코프 제한

  return () => ctx.revert(); // 반드시 클린업!
}, []);
```

#### 텍스트 애니메이션 (SplitText)

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

#### AI 생성 GSAP 코드의 흔한 실수

1. 동적 콘텐츠 로드 후 `ScrollTrigger.refresh()` 누락
2. React에서 `gsap.context()` 클린업 미사용
3. 비컴포지트 프로퍼티 애니메이션 (레이아웃 스래싱)
4. `scrub: true` 대신 `scrub: 1` 사용 권장 (부드러운 스크러빙)
5. 반응형 레이아웃에서 `invalidateOnRefresh: true` 누락

---

## 5. Lottie / Rive

### 5.1 Lottie

AI 도구는 Lottie JSON을 직접 생성할 수 없지만 (After Effects/Figma에서 내보내기 필요), **통합 코드 작성에는 탁월**.

```jsx
// dotLottie (압축 포맷, 10배 작은 크기)
import { DotLottieReact } from "@lottiefiles/dotlottie-react";

<DotLottieReact
  src="/animations/loading.lottie"
  loop
  autoplay
/>
```

#### 스크롤 동기화 Lottie

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

Lottie 대안으로 급부상. **스테이트 머신** 기반의 인터랙티브 애니메이션이 핵심 강점.

| 비교 | Lottie | Rive |
|------|--------|------|
| **인터랙션** | 코드로 제어 | 스테이트 머신 (에디터에서 정의) |
| **파일 크기** | JSON (큼) / dotLottie (작음) | 바이너리 (작음) |
| **렌더링** | 프리베이크 | 런타임 벡터 |
| **호버/클릭 반응** | 코드 필요 | 에디터에서 설정 |

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

## 6. 마이크로 인터랙션 패턴

### 6.1 버튼 피드백

```css
/* CSS 전용 — 다층 피드백 */
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
// Framer Motion 버튼
<motion.button
  whileHover={{ scale: 1.02, y: -1 }}
  whileTap={{ scale: 0.98 }}
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
/>
```

### 6.2 로딩 상태

#### 스켈레톤 스크린

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

/* 다크 모드 */
@media (prefers-color-scheme: dark) {
  .skeleton {
    background: linear-gradient(90deg,
      hsl(0 0% 15%) 25%, hsl(0 0% 20%) 50%, hsl(0 0% 15%) 75%);
  }
}
```

### 6.3 토스트 알림

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

### 6.4 토글 / 스위치

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

### 6.5 아코디언 / 확장-축소

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

## 7. 스크롤 기반 애니메이션

### 7.1 패럴랙스

#### CSS Scroll-Driven 패럴랙스

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

### 7.2 스크롤 리빌 (CSS 전용, 2025 방식)

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

### 7.3 읽기 프로그레스 바

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

### 7.4 스티키 헤더 축소

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

### 7.5 GSAP 섹션 핀 시퀀스

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

## 8. 페이지 전환

### 8.1 View Transitions API + SPA

```typescript
// 전환 유틸리티
async function navigateWithTransition(updateFn: () => void) {
  if (!document.startViewTransition) {
    updateFn();
    return;
  }
  const transition = document.startViewTransition(updateFn);
  await transition.finished;
}
```

#### 방향 기반 페이지 전환

```css
/* 앞으로 이동: 오른쪽에서 슬라이드 인 */
::view-transition-old(root) {
  animation: slide-out-left 0.3s ease;
}
::view-transition-new(root) {
  animation: slide-in-right 0.3s ease;
}

/* 뒤로 이동: 왼쪽에서 슬라이드 인 */
.back-navigation::view-transition-old(root) {
  animation: slide-out-right 0.3s ease;
}
.back-navigation::view-transition-new(root) {
  animation: slide-in-left 0.3s ease;
}
```

### 8.2 Framer Motion 페이지 전환

```jsx
// Next.js App Router의 template.tsx
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

## 9. 성능 최적화

### 9.1 GPU 가속 프로퍼티

| 구분 | 프로퍼티 | 비용 |
|------|---------|------|
| **GPU 가속 (권장)** | `transform`, `opacity`, `filter`, `backdrop-filter`, `clip-path` | 최소 |
| **페인트 유발 (주의)** | `box-shadow`, `border-radius`, `background` | 중간 |
| **레이아웃 유발 (금지)** | `width`, `height`, `top`, `left`, `margin`, `padding`, `font-size` | 최대 |

### 9.2 will-change 올바른 사용

```css
/* 좋음: 애니메이션 직전에 적용 */
.card:hover {
  will-change: transform;
}

/* 나쁨: 항상 켜둠 (GPU 메모리 낭비) */
.card {
  will-change: transform; /* 하지 마세요 */
}
```

```javascript
// 최선: JS로 애니메이션 전 적용, 후 제거
element.style.willChange = 'transform';
element.addEventListener('transitionend', () => {
  element.style.willChange = 'auto';
}, { once: true });
```

### 9.3 contain 프로퍼티

```css
/* 애니메이션 리페인트 격리 */
.animated-card {
  contain: layout style paint;
}

/* 많은 애니메이션 자식이 있는 스크롤 컨테이너 */
.scroll-list-item {
  content-visibility: auto;
  contain-intrinsic-size: 0 80px;
}
```

### 9.4 성능 측정

```javascript
// 애니메이션 프레임 드롭 감지
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.duration > 50) { // 60fps 기준 3프레임 이상
      console.warn('Long animation frame:', entry.duration, 'ms');
    }
  }
});
observer.observe({ type: 'long-animation-frame', buffered: true });
```

---

## 10. 애니메이션 프롬프팅 기법

### 10.1 프롬프트 품질 단계

#### Tier 1: 기본 (제네릭한 결과)
> "이 카드에 애니메이션 추가해줘"

#### Tier 2: 설명적 (나은 결과)
> "이 카드에 호버 애니메이션 추가: 4px 올라가면서 그림자가 부드럽게 확장, 반응 빠르지만 바운시하지 않은 스프링 전환"

#### Tier 3: 상세 스펙 (최고 결과)
> "프로덕트 카드에 호버 인터랙션 추가:
> - 호버 시: translateY(-4px), box-shadow 0 2px 8px → 0 8px 24px (opacity 0.08)
> - 스프링: stiffness 400, damping 25 (빠르고 안정적)
> - 내부 이미지 1.03 스케일 (overflow hidden)
> - 제목 색상 gray-700 → primary 전환
> - 탭/active: scale 0.98 (촉각 피드백)
> - prefers-reduced-motion: transform 없이 opacity만
> - Framer Motion 사용 (프로젝트에서 이미 사용 중)"

### 10.2 검증된 프롬프트 패턴

| 패턴 | 예시 |
|------|------|
| **실제 제품 참조** | "Apple Music 'Now Playing' 카드처럼 — 바닥에서 스프링으로 올라오고, 블러 배경 페이드인" |
| **물리 지정** | "mass: 1, stiffness: 300, damping: 25 스프링 — iOS 기본 스프링과 유사하게" |
| **느낌 설명** | "스내피하고 반응적이어야 함, 둥둥 뜨는 느낌 아님. 물리 버튼을 누르는 촉감" |
| **오케스트레이션** | "리스트 아이템 60ms 딜레이로 스태거. 컨테이너 먼저 페이드인(200ms), 자식이 하나씩 올라옴" |
| **접근성 명시** | "prefers-reduced-motion 지원. 축소 모션 사용자는 transform 생략, 짧은 opacity 페이드만" |
| **이징 컨텍스트** | "진입에 ease-out, 퇴장에 ease-in, 상태 변경에 ease-in-out" |
| **스크롤 동작** | "CSS scroll-driven animations 사용. 20% 보일 때 시작, 60%에서 완전 표시" |

### 10.3 한국어 프롬프트 예시

> "이 카드에 호버 애니메이션을 추가해주세요. 위로 4px 올라가고 그림자가 부드럽게 확장되는 효과. 스프링 물리(stiffness 400, damping 25)를 사용해서 반응이 빠르면서도 자연스럽게. prefers-reduced-motion도 지원해주세요."

> "목록 아이템이 스크롤할 때 하나씩 나타나는 애니메이션. CSS scroll-driven animations 사용. 뷰포트에 20% 보일 때부터 서서히 나타나서 60%일 때 완전히 보이게."

---

## 11. 애니메이션 디자인 원칙

### 11.1 디즈니 12원칙의 UI 적용

| 원칙 | UI 적용 | 예시 |
|------|--------|------|
| **찌그러짐 & 늘어남** | 버튼 프레스 | 탭 시 scale 0.98 |
| **예비 동작** | 이동 전 미세한 끌림 | 버튼이 약간 뒤로 당겨진 후 페이지 이동 |
| **무대 연출** | 핵심 액션에 집중 | 모달 열릴 때 배경 흐림/어둡게 |
| **따라가기 & 겹침** | 리스트 순차 정지 | 아이템들이 동시에 멈추지 않고 스태거 |
| **느린 시작, 느린 끝** | 이징 적용 | 진입: ease-out, 퇴장: ease-in |
| **호** | 자연스러운 곡선 경로 | `offset-path`로 비선형 이동 |
| **부수 동작** | 아이콘 바운스 + 텍스트 페이드 | 리플 이펙트 + 색상 변경 동시 |
| **타이밍** | 인터랙션 유형별 시간 | 마이크로: 100-200ms, 페이지: 300-500ms |
| **과장** | 스프링 오버슈트 | 1.0 이상 스케일 후 정착 |
| **매력** | 목적 있는 부드러운 모션 | 의도적이고 세련된 움직임 |

### 11.2 타이밍 가이드라인

| 인터랙션 유형 | 듀레이션 | 이징 |
|-------------|---------|------|
| 버튼 호버 | 100-150ms | ease-out |
| 버튼 active/탭 | 50-100ms | ease-in |
| 툴팁 표시 | 150-200ms | ease-out |
| 툴팁 숨김 | 100-150ms | ease-in |
| 드롭다운 열기 | 200-250ms | ease-out 또는 spring |
| 모달 진입 | 250-350ms | spring (300, 25) |
| 모달 퇴장 | 200-250ms | ease-in |
| 페이지 전환 | 300-500ms | ease-in-out 또는 spring |
| 토스트 진입 | 300-400ms | spring (350, 25) |
| 토스트 퇴장 | 200ms | ease-in |
| 스켈레톤 쉬머 | 1500ms | ease-in-out, infinite |
| 로딩 스피너 | 800-1200ms | linear, infinite |
| 스태거 딜레이 | 50-100ms | 자식당 |
| 스크롤 리빌 | 400-600ms | ease-out 또는 spring |

### 11.3 이징 커브 레퍼런스

```css
/* Material Design */
--ease-standard: cubic-bezier(0.4, 0, 0.2, 1);
--ease-decelerate: cubic-bezier(0, 0, 0.2, 1);    /* 진입용 */
--ease-accelerate: cubic-bezier(0.4, 0, 1, 1);     /* 퇴장용 */

/* Apple 스타일 */
--ease-apple: cubic-bezier(0.25, 0.1, 0.25, 1);
--ease-apple-bounce: cubic-bezier(0.175, 0.885, 0.32, 1.275);
```

---

## 12. 모바일 전용 애니메이션

### 12.1 터치 제스처

#### 스와이프로 닫기

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

#### 당겨서 새로고침

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

#### iOS 스타일 뒤로 스와이프

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

#### 바텀 시트

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

### 12.2 햅틱 피드백

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
Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);   // 탭
Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);  // 토글
Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success); // 성공
```

### 12.3 모바일 성능 주의사항

- `transform`과 `opacity`만 애니메이션 (모바일에서 필수)
- 터치 이벤트 리스너에 `passive: true` 사용
- `box-shadow` 애니메이션 금지 (모바일 GPU에서 매우 비쌈)
- `will-change: transform` 남용 금지 (각 인스턴스가 모바일 GPU 메모리 소비)
- CPU 쓰로틀링 4x, 6x에서 테스트 (저사양 기기 시뮬레이션)
- 긴 리스트의 오프스크린 콘텐츠에 `content-visibility: auto` 적용

---

## 13. 3D / WebGL 애니메이션

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

### 자주 사용되는 drei 헬퍼

| 헬퍼 | 효과 |
|------|------|
| `<Float>` | 부드러운 부유 애니메이션 |
| `<MeshDistortMaterial>` | 유기적 왜곡 |
| `<MeshWobbleMaterial>` | 흔들림 효과 |
| `<Trail>` | 모션 트레일 |
| `<Sparkles>` | 반짝이 파티클 |
| `<Stars>` | 별 필드 배경 |

### 3D 성능

- 반복 지오메트리에 `instancedMesh` 사용
- `<AdaptiveDpr>`로 자동 해상도 조절
- KTX2/Basis로 텍스처 압축
- `useFrame` 내 연산 최소화

---

## 14. 라이브러리 비교

### 선택 기준

| 상황 | 추천 |
|------|------|
| 단순 hover/focus/active | **CSS** |
| 스크롤 연동 (표준) | **CSS** scroll-driven animations |
| `display: none`에서 진입 | **CSS** @starting-style |
| 스켈레톤, 스피너, 프로그레스 | **CSS** |
| React 레이아웃 애니메이션 | **Framer Motion** (킬러 기능) |
| 퇴장 애니메이션 | **Framer Motion** AnimatePresence |
| 제스처 (드래그, 스와이프) | **Framer Motion** |
| 복잡한 타임라인 오케스트레이션 | **GSAP** |
| SVG 모핑, 패스 애니메이션 | **GSAP** |
| 고급 스크롤 핀닝 | **GSAP** ScrollTrigger |
| 텍스트 스플릿 애니메이션 | **GSAP** SplitText |
| 비 React (Vue, Svelte, 바닐라) | **Motion** (motion.dev) |
| AI 도구 지원 최고 | **CSS + Framer Motion** 하이브리드 |

> **2025년 가장 일반적인 패턴**: CSS로 단순 상태, Framer Motion으로 컴포넌트 생명주기 (진입/퇴장/레이아웃). 대부분의 AI 도구가 기본적으로 이 조합을 생성.

### 번들 크기 비교

| 라이브러리 | 크기 |
|-----------|------|
| CSS | 0 KB |
| Motion (바닐라) | ~18 KB |
| anime.js | ~17 KB |
| GSAP | ~28 KB (+플러그인) |
| Framer Motion | ~32 KB |

---

## 15. 접근성

### 15.1 3단계 접근법 (2025 업계 베스트 프랙티스)

```css
/* Tier 1: 풀 애니메이션 (기본) */
.card {
  transition: transform 0.3s, opacity 0.3s ease;
}

/* Tier 2: 축소 — 제거가 아닌 단순화 */
@media (prefers-reduced-motion: reduce) {
  .card {
    transition: opacity 0.15s ease; /* opacity만 유지, transform 제거 */
  }

  .parallax { transform: none; }
  .auto-scroll { scroll-behavior: auto; }

  /* 장식적 애니메이션은 완전 제거 */
  .background-particles,
  .floating-shapes {
    animation: none;
  }

  /* 필수 피드백은 유지 */
  .button { transition: background-color 0.1s; }
}

/* Tier 3: 애니메이션 없음 (커스텀 토글) */
[data-motion="none"] * {
  animation: none !important;
  transition: none !important;
}
```

### 15.2 전정 장애 고려사항

**위험한 애니메이션 패턴:**
- 대규모 모션 (풀페이지 패럴랙스, 줌 배경)
- 회전과 스피닝
- 화면 전체 빠른 이동
- 자동 재생 캐러셀/슬라이더
- 주변부의 지속/반복 애니메이션

**안전한 애니메이션 패턴:**
- 불투명도 페이드 (거의 항상 안전)
- 소규모 트랜스폼 (< 10px 이동)
- 색상 전환
- 테두리/아웃라인 변경
- 짧고 목적이 있는 피드백 애니메이션

### 15.3 WCAG 2.2 요구사항

| 기준 | 레벨 | 요구사항 |
|------|------|---------|
| 2.3.1 3번 이하 깜박임 | A | 초당 3번 이상 깜박이는 콘텐츠 금지 |
| 2.3.3 인터랙션 애니메이션 | AAA | 인터랙션 유발 모션 비활성화 가능해야 함 |
| 2.2.2 일시 정지/중지/숨기기 | A | 5초 이상 자동 재생 애니메이션은 제어 메커니즘 필수 |

### 15.4 사용자 토글 구현

```jsx
// 시스템 설정 외 앱 내 별도 제어 제공
const [motionLevel, setMotionLevel] = useState('full');

<select value={motionLevel} onChange={e => setMotionLevel(e.target.value)}>
  <option value="full">전체 애니메이션</option>
  <option value="reduced">축소된 애니메이션</option>
  <option value="none">애니메이션 없음</option>
</select>
```

---

## 16. 애니메이션 디자인 토큰

### 표준화된 모션 토큰 체계

```css
:root {
  /* 듀레이션 토큰 */
  --duration-instant: 50ms;
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  --duration-glacial: 800ms;

  /* 이징 토큰 */
  --ease-default: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.175, 0.885, 0.32, 1.275);
  --ease-spring: linear(/* 스프링 값 */);

  /* 스프링 토큰 (JS 라이브러리용 — stiffness / damping) */
  --spring-snappy: 400 / 30;
  --spring-gentle: 200 / 20;
  --spring-bouncy: 300 / 10;
}
```

### 모션 디자인 시스템 레퍼런스

| 시스템 | 분류 | 설명 |
|--------|------|------|
| **IBM Carbon Motion** | Productive / Expressive | 빠르고 최소 / 장난스럽고 매력적 |
| **Material Design 3** | Emphasized / Standard / De-emphasized | 500ms / 300ms / 200ms |
| **Apple HIG** | 유동적 스프링 | 컨텍스트별 특정 damping 비율 |

---

## 17. 신흥 트렌드

### CSS-First 르네상스

이전에 JavaScript가 필수였던 애니메이션이 CSS만으로 가능해지는 강력한 트렌드:

| 이전 (JS 필수) | 현재 (CSS 가능) |
|---------------|-----------------|
| ScrollTrigger | `animation-timeline: scroll()` |
| AnimatePresence | `@starting-style` |
| JS 스프링 라이브러리 | `linear()` 이징 |
| React 전환 라이브러리 | View Transitions API |

### 서버 주도 애니메이션

CMS/API에서 애니메이션 구성을 받아 적용하는 패턴 등장:

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

> 배포 없이 애니메이션 업데이트 가능, A/B 테스트 지원

### "60fps or Nothing" 사고방식

- Chrome DevTools 애니메이션 인스펙터 개선
- Long Animation Frame API로 jank 감지
- Core Web Vitals의 INP(Interaction to Next Paint)가 애니메이션 성능 반영
- 번들 사이즈처럼 **애니메이션 복잡도도 예산 관리** 대상

---

## 참고 자료

- [View Transitions API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transitions_API)
- [CSS Scroll-Driven Animations](https://developer.chrome.com/docs/css-ui/scroll-driven-animations)
- [Framer Motion Documentation](https://www.framer.com/motion/)
- [Motion (motion.dev)](https://motion.dev/)
- [GSAP Documentation](https://gsap.com/docs/)
- [Rive Documentation](https://rive.app/docs/)
- [LottieFiles](https://lottiefiles.com/)
- [React Three Fiber](https://docs.pmnd.rs/react-three-fiber)
- ASTRA `docs/ux/ux-interaction-patterns.md` — 인터랙션 패턴 가이드
- ASTRA `docs/ux/mobile-design-guide.md` — 모바일 디자인 가이드
- ASTRA `docs/ux/vibe-coding-design-guide.md` — 바이브 코딩 디자인 가이드
