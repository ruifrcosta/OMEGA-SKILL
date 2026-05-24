# ADR-0003: High-End Frontend Aesthetics & Motion Choreography Standards

## Status
Accepted

## Deciders
- OMEGA Architecture Office
- Frontend Agent
- UX / Design System Agent

## Context
Standard AI-generated web interfaces suffer from "AI slop" aesthetics — cookie-cutter Tailwind grids, overused purple/blue gradients, flat cards, sticky top-glued headers, and generic system fonts (Inter, Roboto, Arial). 

To ensure OMEGA outputs exude haptic depth, cinematic spatial rhythm, and the premium quality of a $150k+ bespoke digital agency (in the vein of Stripe, Vercel, or Linear), we must formalize design token governance, spatial layout archetypes, nested container techniques ("Double-Bezel"), and spring-physics-driven motion choreography (using GSAP and Framer Motion).

## Decision
We enforce the following absolute visual and technical standards across all OMEGA frontend projects:

### 1. Absolute Font and Icon Sanctions (Banned Elements)
- **Banned Typography**: Inter, Roboto, Arial, Open Sans, Helvetica, system fonts. Headings must pair a distinctive display/variable font with character (e.g., `Geist`, `Clash Display`, `Plus Jakarta Sans`, `PP Editorial New`) and a highly refined body font.
- **Banned Icons**: Standard thick Lucide or FontAwesome lines. Use only precise, ultra-light line iconography (e.g., Phosphor Light, Remix Line, custom SVG paths).
- **Banned Borders/Shadows**: Flat 1px gray borders and harsh, dark CSS drop shadows (`shadow-md`). Use nested bezel rings and soft diffused ambient ambient shadows.

### 2. Physical Nested Architecture (The Double-Bezel / Doppelrand)
All premium cards, mockups, or featured containers must use nested hardware enclosures:
- **Outer Shell**: Border or ring highlight (`border border-white/10` or `ring-1 ring-black/5`), light padding (`p-1.5` or `p-2`), and a generous outer border radius (`rounded-[2rem]`).
- **Inner Core**: Distinct inner content background, inner highlight (`shadow-[inset_0_1px_1px_rgba(255,255,255,0.15)]`), and a calculated smaller inner radius: `rounded-[calc(2rem-0.375rem)]` (or equivalent outer-minus-padding calculation) to keep concentric curves perfect.

### 3. Motion Choreography & Spring Physics (GSAP & Framer Motion)
- **Banned Interpolation**: Standard `linear` and `ease-in-out` transitions.
- **Enforced Curves**: All animations must simulate mass and spring physics. CSS/Tailwind transitions must use high-damping cubic-beziers: `ease-[cubic-bezier(0.32,0.72,0,1)]`.
- **GSAP ScrollTrigger**: When scroll-driven animations are built:
  - Register plugins strictly once: `gsap.registerPlugin(ScrollTrigger)`.
  - Use `scrub: number` (e.g., `scrub: 1` or `scrub: 0.5`) to create lag-catchup smoothness.
  - Horizontal scrolling sections must use **ease: "none"** to maintain a 1:1 mapping with the scroller.
  - Clean up animations on unmount (`useGSAP` or `ScrollTrigger.getAll().forEach(t => t.kill())`).
- **Intersection Observer**: Entry reveals must use `IntersectionObserver` or Framer Motion's `whileInView` (`translate-y-16 blur-md opacity-0` -> `translate-y-0 blur-0 opacity-100` over 800ms). Never hook up heavy animations directly to `window.addEventListener('scroll')` to avoid layout thrashing and paint bottlenecks.

### 4. GPU Performance Guardrails
- **Safe Properties**: Animate exclusively via GPU-friendly properties: `transform` (scale, translate, rotate) and `opacity`. Never animate layout-triggering properties (`top`, `left`, `width`, `height`).
- **Blur Isolation**: Apply heavy `backdrop-blur` filters ONLY to fixed, sticky layer overlays (navbars, modal sheets) to prevent mobile repainting frame drops.

## Consequences
### Positive
- **Distinguished Identity**: Eliminates "AI aesthetic" completely, ensuring every OMEGA build feels bespoke, costly, and carefully crafted.
- **Concentric curve alignment**: Enforcing calculated bezel margins prevents standard overlapping corner glitches.
- **Hardware-accelerated rendering**: Keeps web and mobile experiences running at a locked 60/120fps.

### Negative
- **Layout Math Overhead**: Enforcing concentric border calculations and custom beziers requires a high degree of precision in tailwind classes.
