# Vibe Coding Design Guide

> Workflows, techniques, and best-practice guide for professional designers using vibe coding tools

## 1. Overview

### What is Vibe Coding?

**Vibe Coding** is a concept popularized in February 2025 when Andrej Karpathy (former Tesla AI director, OpenAI co-founder) defined it as "a way of programming where you forget that code exists and surrender yourself fully to the vibes".

In the design context, vibe coding refers to **a way of working where designers use AI coding tools to turn visual ideas, rough concepts, and natural-language descriptions directly into working UI code**. The designer describes the desired vibe and the AI generates the implementation.

### Difference vs. the Traditional Workflow

| Aspect | Traditional | Vibe Coding |
|--------|-------------|-------------|
| **Flow** | Designer → Figma mockup → Developer → Code | Designer → AI prompt → working prototype |
| **Handoff** | Static comps + spec doc | The prototype itself is the starting point for code |
| **Iteration speed** | 1–2 weeks (comp → interactive prototype) | A few hours |
| **Exploration breadth** | 1–2 directions due to cost | 5–10 variants in parallel |

### Core Insight

> "When implementation becomes nearly free, the bottleneck is no longer implementation but **taste**." — Andrej Karpathy

---

## 2. Major Tool Comparison

### Per-tool Use Case and Characteristics

| Tool | Best-fit design use | Strengths | Limitations |
|------|---------------------|-----------|-------------|
| **v0** (Vercel) | UI component exploration, landing pages | Top-tier visual quality, native Tailwind/React, easy iteration | Frontend only, components can converge in look |
| **Bolt.new** (StackBlitz) | Full interactive prototypes, MVPs | Full-stack, instant deploy, browser-based | Code quality can be rough, fine styling is difficult |
| **Lovable** | App prototypes (designer-friendly) | Lowest barrier to entry, Supabase integration | Limited fine-grained design control |
| **Cursor** | Design system implementation, component library | Full IDE power, strong on systematic work | Coding knowledge required |
| **Claude Code** | Design systems, complex multi-file projects | Handles complex codebases, agentic workflow | CLI-based (higher barrier) |
| **Replit Agent** | Quick prototypes, experiments | No installation, instant deploy | Limited design control |
| **Figma AI** | Visual exploration, wireframing | Natural integration within existing design workflows | No code output |
| **Framer** | Marketing sites, portfolios | Designer-friendly, built-in hosting, visual editor | Limited to marketing / content sites |

### Recommended Tool Combinations

Tool combination patterns used by professional designers:

1. **v0 → Cursor**: generate initial UI with v0 → refine systematically in Cursor
2. **Figma → Builder.io → Cursor**: Figma design → convert to code → enhance with AI
3. **Claude Code → browser preview**: design system work — generate tokens + components + documentation
4. **Bolt → Git → Cursor/Claude Code**: prototype with Bolt → extract code → refine in a specialized editor
5. **v0 + Framer**: generate components with v0 → assemble and publish in Framer

---

## 3. Expert Workflow

### 3.1 Prompt-Driven Design Workflow

A 5-stage workflow developed by professional designers:

#### Stage 1: Vision & References ("vibe board" setup)

Replaces or complements the traditional mood board:

- Organize reference screenshots, aesthetic direction, and design principles in natural language
- Author a **"design brief prompt"** — a structured document covering visual direction, brand personality, target user, and interaction philosophy
- Replaces or complements the traditional creative brief

```markdown
# Design Brief Prompt Example

## Brand personality
- Minimal yet warm, technical yet approachable
- References: Linear's density + Notion's friendliness

## Visual direction
- Palette: neutral gray base + single accent color
- Typography: Geist Sans + Pretendard (Korean)
- Space: generous whitespace, 8px baseline grid

## Target user
- Korean startup product manager (30s)
- Data-driven decisions, efficiency first

## Interaction philosophy
- Immediate feedback, minimum click path
- Keyboard-first navigation
```

#### Stage 2: Rapid Generation & Exploration

- Use v0, Bolt, etc., to **generate 5–10 variants quickly**
- Never accept the first generation as final
- Apply **Progressive Refinement** technique:
  - Layer 1: layout and structure
  - Layer 2: typography and color
  - Layer 3: component-level details
  - Layer 4: micro-interactions and states
  - Layer 5: edge cases and responsive behavior

#### Stage 3: Iterative Refinement

- Conversational iteration: "softer card shadow", "increase contrast between header and body"
- **The quality of refinement prompts** matters more than the initial prompt
- Maintain a **prompt library** of verified refinement instructions

#### Stage 4: Design System Extraction

- After reaching the desired visual quality, **extract design tokens** (color, spacing, type scale)
- Systematize the output into reusable components
- Tools strong at systematic work, like Claude Code, shine at this stage

#### Stage 5: Production Hardening

- Accessibility audit and fixes (WCAG AA)
- Refine responsive behavior
- Performance optimization
- Polish animations and interactions

---

### 3.2 Design Engineer Workflow

Workflow of a **Design Engineer** working at the intersection of design and code:

- Perform complex interaction exploration in **Figma**
- Use **vibe coding tools** for fast implementation of standard patterns
- **Inject** the personal component library as context into AI tools
- Use AI-generated code as a starting point and **refine CSS/styling by hand**

### 3.3 Non-Coder Designer Workflow

Methodology for designers without a coding background:

- Center on **screenshot-based prompting**: "Make something like this but with [changes]"
- Use **low-barrier tools** like v0, Lovable
- Focus on **mastering a single tool** rather than tool switching
- After producing a prototype, **delegate production-code extraction** to developers

---

## 4. Core Prompting Techniques

### 4.1 Anti-AI Aesthetic Prompts

The most discussed technique in the design community. Instructions that **explicitly avoid the generic aesthetic typical of AI generation**:

```
"Please avoid the typical AI/SaaS landing page feel"
"No gradient blob backgrounds"
"Do not use default shadcn/ui styling as-is; customize for a unique feel"
"As if made by a senior designer at [specific studio], not by an AI"
```

### 4.2 Reference-Anchored Prompts

Provide concrete URLs or specific existing designs as **reference points**:

```
"Typography hierarchy should feel like the Stripe docs"
"Spacing and density similar to the Linear interface"
"Card component like the database view in Notion"
```

> Output quality improves dramatically compared to abstract descriptions

### 4.3 Constraint-First Prompts

Present **constraints first**, not features:

```
"Whole palette uses only 3 colors"
"At most 2 font families"
"Grid strictly on an 8px baseline"
"At most 3 variants per component"
```

> Without constraints, AI tends to over-design; constraints yield consistent results

### 4.4 Layered Prompting (the "Onion" Technique)

Don't explain everything in one prompt — **layer it stepwise**:

| Layer | Focus | Example prompt |
|-------|-------|----------------|
| 1 | Layout & structure | "2-column dashboard layout, 240px fixed sidebar" |
| 2 | Typography & color | "Headings in Geist Sans 600, body 400, accent #2563EB" |
| 3 | Component details | "Cards rise 2px and shadow expands on hover" |
| 4 | Micro-interactions | "150ms scale 0.98 → 1.0 spring on button click" |
| 5 | Edge cases & responsive | "Below 768px the sidebar collapses; show hamburger menu" |

### 4.5 Design Token Injection

Provide CSS custom properties (design tokens) as context **before** component generation:

```css
/* Please generate all components using these tokens */
:root {
  --color-primary: oklch(0.55 0.15 250);
  --color-surface: oklch(0.98 0.005 250);
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --font-sans: 'Geist Sans', 'Pretendard', sans-serif;
  --transition-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

> Guarantees consistency across components generated over multiple prompts

---

## 5. Best Practices

### DO (Recommended)

- **Provide brand/style context first**, then generate
- **Iterate in small steps** rather than regenerating from scratch
- Save successful prompts and build a **prompt library**
- Use **version control (git)** for design prototypes too
- **Test on real devices**, not just the generation preview
- **State accessibility requirements up front** ("WCAG AA compliant", "minimum 44px touch target")
- **Include responsive behavior in the initial prompt** (do not bolt on later)
- **Explicitly request each interactive state** (hover, focus, active, disabled, error, loading, empty)

### DON'T

- Do **not accept** the first generation as final
- Do not use vibe coding for **brand-specific work** without sufficient brand guidelines
- Do not **ignore code quality** of the generated code — visual correctness is not enough
- Do not **skip** the design-token / system step — ad-hoc generation breeds inconsistency
- Do not **rely on a single tool** — tools have different strengths
- Do not **let the AI design freely** without constraints

---

## 6. Limitations and Challenges

### 6.1 Visual Quality Challenges

#### The "AI Aesthetic" Problem

AI-generated design tends to **converge to a recognizable style**. Professional designers call it the "v0 look" or "AI slop aesthetic":

- Subtle gradients on cards
- Rounded corners everywhere
- Default blue/purple/indigo palette
- Inter or system font stacks
- Identical spacing patterns

#### Brand Differentiation

It is hard to achieve a truly unique brand design from vibe coding alone. AI tends to regress to the mean of its training data.

#### Typographic Nuance

Fine typographic control (optical kerning, widow/orphan control, precise baseline grid) is hard to achieve via prompts alone.

### 6.2 Technical Challenges

| Challenge | Description | Mitigation |
|-----------|-------------|------------|
| **Code quality** | Visually correct but structurally problematic (inline styles, lack of semantic HTML, etc.) | Code review and refactoring after generation are mandatory |
| **Design-system consistency** | Without token injection, inconsistent across prompts (subtly different grays, spacing, etc.) | Pre-define design tokens and inject as context |
| **Incomplete state coverage** | hover, focus, disabled, error, loading, empty states missing | Request each state explicitly |
| **Animation/motion** | Complex animation (springs, orchestration, scroll triggers) is hard via prompts | Use a dedicated animation step with detailed prompts or manual work |
| **Responsive design** | Stops at simple stack/side arrangement | Creative responsive adaptation needs manual intervention |
| **Accessibility** | Missing ARIA attributes, lacking keyboard navigation, insufficient contrast | State accessibility requirements in the initial prompt |

### 6.3 Workflow Challenges

- **Context-window limits**: as the prototype grows, prior design decisions are lost, leading to inconsistency
- **Version-control friction**: many designers are unfamiliar with git, making iteration tracking difficult
- **Collaboration gap**: vibe coding is currently a solo activity — no Figma-level real-time collaboration
- **The "last 10%" problem**: from a 90% prototype to finished production design still requires significant manual work
- **Handoff mismatch**: generated code doesn't match the project's architecture, conventions, or component library

---

## 7. Structural Changes to the Design-Development Workflow

### 7.1 The Collapse of Handoff

| Change | Description |
|--------|-------------|
| **Handoff disappears** | The prototype itself is the starting point of production code, not a reference image |
| **Rise of the Design Engineer** | The role combining design + frontend implementation becomes mainstream |
| **Prototyping speed revolution** | From 1–2 weeks to a few hours. Live prototypes used in client meetings |
| **Figma's changing role** | From "where all design happens" → "where exploration and collaboration happen" |
| **The taste gap is the bottleneck** | With implementation nearly free, design taste, creativity, and strategic thinking become the differentiators |

### 7.2 New Workflow Patterns

#### Parallel Exploration

Instead of sequentially refining one design direction, **generate 5–10 full prototypes in parallel** → user-test → invest in the winner. Previously impossible due to cost.

#### Living Specification

Instead of static design specs (Figma file + Zeplin annotations), **the working prototype itself is the spec**. Developers refer to executing code, not measurements in a design tool.

#### Continuous Design

Design iteration does not stop at handoff. Designers **continue to refine actual product code throughout development via vibe coding**.

#### Client Prototype in the Meeting

Design consultants **generate live prototypes during client meetings reflecting real-time feedback**. A workflow that was impossible before vibe coding.

### 7.3 Team Structure Impact

| Change | Result |
|--------|--------|
| **Smaller teams** | 1 design engineer ≈ traditional 1 designer + 1–2 frontend developers |
| **Faster validation** | PMF can be validated with functional prototypes before hiring a full dev team |
| **Democratization** | Non-technical founders and PMs can build functional prototypes themselves |
| **Specialization shift** | "Ability to use Figma" decreases in value; "great design sense + ability to express it" rises |

### 7.4 What Doesn't Change

Even with vibe coding, areas where human judgment remains essential:

- **User research** — understanding user needs still requires human judgment
- **Brand strategy** — developing visual identity requires human creative direction
- **Complex interaction design** — especially accessibility expertise
- **Design system governance** — architecture decisions for large-scale systems need humans
- **Design taste and aesthetic judgment** — its importance rises, if anything, because of vibe coding

---

## 8. Vibe Coding in the Korean Market

**Vibe Coding** is spreading especially rapidly in the Korean tech community:

- **Rapid adoption**: active uptake by Korean designers of tools like v0, Bolt
- **Cultural fit**: the "ppalli-ppalli" (hurry-hurry) culture aligns well with the speed of vibe coding
- **Use in small teams**: especially useful at startups that can't separately hire designers and developers
- **Community activity**: workflows actively discussed on GeekNews, Disquiet, YouTube
- **Educational content**: many vibe coding design tutorials produced in Korean blogs and YouTube channels

---

## 9. Application in ASTRA Projects

How to connect existing ASTRA skills with vibe-coding techniques:

| ASTRA skill | Vibe-coding integration point |
|-------------|-------------------------------|
| `/service-planner` (Step 6 HTML mockups) | Quality boost via design token injection + anti-AI aesthetic prompts; apply reference anchoring when the design tone is auto-decided |
| `/frontend-design` | Apply reference anchoring + constraint-first prompts |
| `/catalog-generator` | Layered prompting: layout → typography → color, in sequence |
| `/manual-generator` | Pre-define manual design tone with a vibe board |
| `/handoff-publish` | Apply constraint-first prompting when deciding design for the Screen ID-based collaboration package |

### Recommended Process

1. **Build the vibe board** → organize references, brand personality, constraints
2. **Define design tokens** → set up the 3-tier token system in `src/styles/design-tokens.css`
3. **Parallel exploration** → rapidly generate 5–10 design directions
4. **Layered refinement** → refine in the order layout → typography → color → interaction
5. **Design system extraction** → systematize into reusable components
6. **Production hardening** → accessibility, responsive, performance, animation polish

---

## References

- Andrej Karpathy, "Vibe Coding" (2025-02)
- Vercel v0 Documentation
- Bolt.new by StackBlitz
- Lovable (formerly GPT Engineer)
- Cursor Documentation
- Claude Code Documentation
- ASTRA `docs/ux/ux-interaction-patterns.md` — interaction patterns guide
- ASTRA `docs/ux/mobile-design-guide.md` — mobile design guide
