# TASTE ENGINE — Precision Design Variance System

Extracted from `taste-skill` (Leonxlnx/taste-skill). Implements a 3-dial metric system for deterministic, AI-bias-corrected frontend engineering.

---

## ACTIVE BASELINE CONFIGURATION

| Dial | Default | Range | Description |
|:---|:---:|:---:|:---|
| `DESIGN_VARIANCE` | **8** | 1–10 | 1=Perfect Symmetry ↔ 10=Artsy Chaos |
| `MOTION_INTENSITY` | **6** | 1–10 | 1=Static/No movement ↔ 10=Cinematic/Magic Physics |
| `VISUAL_DENSITY` | **4** | 1–10 | 1=Art Gallery/Airy ↔ 10=Pilot Cockpit/Packed Data |

**Rule:** These are the global baseline. Listen to the user — adapt dynamically based on explicit requests. Use these values to drive all logic in sections below.

---

## DIAL DEFINITIONS

### DESIGN_VARIANCE (1–10)

| Level | Mode | Implementation |
|:---|:---|:---|
| 1–3 | Predictable | Flexbox `justify-center`, strict 12-column symmetrical grids, equal paddings |
| 4–7 | Offset | `margin-top: -2rem` overlapping, varied image aspect ratios (4:3 next to 16:9), left-aligned headers over center-aligned data |
| 8–10 | Asymmetric | Masonry layouts, CSS Grid with `grid-template-columns: 2fr 1fr 1fr`, massive empty zones (`padding-left: 20vw`) |

> **MOBILE OVERRIDE (CRITICAL):** For levels 4–10, any asymmetric layout above `md:` MUST fall back to strict single-column (`w-full`, `px-4`, `py-8`) on viewports < 768px.

### MOTION_INTENSITY (1–10)

| Level | Mode | Implementation |
|:---|:---|:---|
| 1–3 | Static | No automatic animations. CSS `:hover` and `:active` states only |
| 4–7 | Fluid CSS | `transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1)`. Use `animation-delay` cascades. Focus on `transform` and `opacity` |
| 8–10 | Advanced Choreography | Framer Motion hooks, GSAP ScrollTrigger. NEVER `window.addEventListener('scroll')` |

### VISUAL_DENSITY (1–10)

| Level | Mode | Implementation |
|:---|:---|:---|
| 1–3 | Art Gallery Mode | Massive whitespace. Huge section gaps. Ultra-expensive and clean |
| 4–7 | Daily App Mode | Normal spacing for standard web apps |
| 8–10 | Cockpit Mode | Tiny paddings. 1px lines only. Everything packed. Monospace (`font-mono`) for all numbers |

---

## DESIGN ENGINEERING DIRECTIVES (AI Bias Correction)

LLMs have statistical biases toward specific UI cliché patterns. OMEGA enforces these engineered correction rules:

### Rule 1: Deterministic Typography
- **Display/Headlines:** Default `text-4xl md:text-6xl tracking-tighter leading-none`
- **ANTI-SLOP:** Ban `Inter` for "Premium" or "Creative" surfaces. Force: `Geist`, `Outfit`, `Cabinet Grotesk`, `Satoshi`
- **TECHNICAL UI RULE:** Serif fonts are BANNED for Dashboard/Software UI. Use exclusively: `Geist` + `Geist Mono`, `Satoshi` + `JetBrains Mono`
- **Body/Paragraphs:** `text-base text-gray-600 leading-relaxed max-w-[65ch]`

### Rule 2: Color Calibration
- Max 1 Accent Color. Saturation < 80%
- **THE LILA BAN:** AI Purple/Blue aesthetic BANNED. No purple button glows, no neon gradients. Use Zinc/Slate bases + singular high-contrast accents (Emerald, Electric Blue, Deep Rose)
- Maintain ONE consistent palette — no fluctuation between warm and cool grays

### Rule 3: Layout Diversification
- **ANTI-CENTER BIAS:** Centered Hero/H1 BANNED when `DESIGN_VARIANCE > 4`. Force: Split Screen (50/50), Left-Aligned/Right-Asset, Asymmetric Whitespace

### Rule 4: Materiality & Anti-Card Overuse
- For `VISUAL_DENSITY > 7`: Generic card containers BANNED. Use `border-t`, `divide-y`, or negative space
- Cards ONLY when elevation communicates hierarchy. Tint shadows to background hue

### Rule 5: Interactive UI States (Mandatory)
Generate ALL states — not just success:
- **Loading:** Skeletal loaders matching layout sizes (no generic circular spinners)
- **Empty States:** Beautifully composed, showing how to populate data
- **Error States:** Clear inline error reporting
- **Tactile Feedback:** On `:active`, use `-translate-y-[1px]` or `scale-[0.98]`

### Rule 6: Data & Form Patterns
- Forms: Label above input. Helper text in markup. Error text below input. `gap-2` for input blocks

---

## CREATIVE ARSENAL (High-End Concepts)

When `MOTION_INTENSITY > 5`, systematically implement these high-end concepts:

### "Liquid Glass" Refraction
Beyond `backdrop-blur`: add `border-white/10` inner border + `shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]` to simulate physical edge refraction.

### Magnetic Micro-Physics
Buttons that pull slightly toward cursor. CRITICAL: NEVER use `useState` for magnetic hover — use EXCLUSIVELY Framer Motion's `useMotionValue` and `useTransform` outside React render cycle.

### Perpetual Micro-Interactions (MOTION_INTENSITY > 5)
- Infinite animations: Pulse, Typewriter, Float, Shimmer, Carousel
- Spring physics: `type: "spring", stiffness: 100, damping: 20`
- No linear easing anywhere

### Staggered Orchestration
- `staggerChildren` (Framer) or CSS cascade (`animation-delay: calc(var(--index) * 100ms)`)
- Parent variants and Children MUST be in identical Client Component tree

### Navigation Patterns (Arsenal)
- Mac OS Dock Magnification — Nav icons scale fluidly on hover
- Magnetic Button — Physically pulls toward cursor
- Gooey Menu — Sub-items detach like viscous liquid
- Dynamic Island — Pill-shaped morphing status component
- Contextual Radial Menu — Circular at exact click coordinates
- Floating Speed Dial — FAB springs into curved secondary actions
- Mega Menu Reveal — Full-screen stagger-fade dropdowns

### Layout Patterns (Arsenal)
- **Bento Grid** — Asymmetric tile-based grouping (Apple Control Center)
- **Masonry Layout** — Staggered without fixed row heights
- **Chroma Grid** — Continuously animating gradient borders
- **Split Screen Scroll** — Two halves sliding opposite directions
- **Curtain Reveal** — Hero parting like curtain on scroll

### Card Patterns (Arsenal)
- **Parallax Tilt Card** — 3D-tilt tracking mouse
- **Spotlight Border Card** — Border illuminates under cursor
- **Holographic Foil Card** — Iridescent rainbow on hover
- **Morphing Modal** — Button expands into full-screen dialog

### Scroll Animations (Arsenal)
- Sticky Scroll Stack, Horizontal Scroll Hijack, Locomotive Scroll Sequence
- Zoom Parallax, Scroll Progress Path, Liquid Swipe Transition

### Typography (Arsenal)
- Kinetic Marquee, Text Mask Reveal, Text Scramble Effect
- Circular Text Path, Kinetic Typography Grid

---

## BENTO 2.0 PARADIGM (Motion-Engine Architecture)

For modern SaaS dashboards and feature sections — "Vercel-core meets Dribbble-clean":

### Design Philosophy
- Background: `#f9fafb`. Cards: `#ffffff` with `border-slate-200/50`
- Corners: `rounded-[2.5rem]` for major containers
- Shadow: `shadow-[0_20px_40px_-15px_rgba(0,0,0,0.05)]` (diffusion, never clutter)
- Typography: `Geist`, `Satoshi`, `Cabinet Grotesk`. `tracking-tight` for headers
- Labels: Outside and BELOW cards (gallery-style, not inside)
- Padding: Generous `p-8` or `p-10` inside cards

### Animation Engine (Perpetual Motion)
- All cards contain perpetual micro-interactions
- Spring physics only: `type: "spring", stiffness: 100, damping: 20`
- `layout` and `layoutId` props for smooth re-ordering
- Infinite loops per card (Pulse, Typewriter, Float, Carousel)
- PERFORMANCE: Wrap dynamic lists in `<AnimatePresence>`. Perpetual animations MUST be memoized and isolated in microscopic Client Components

### 5-Card Archetypes
1. **Intelligent List** — Infinite auto-sorting loop with `layoutId` swaps
2. **Command Input** — Multi-step Typewriter cycling prompts with blinking cursor
3. **Live Status** — Breathing status indicators + pop-up badge with overshoot spring
4. **Wide Data Stream** — Infinite horizontal carousel `x: ["0%", "-100%"]`
5. **Contextual UI** — Staggered text highlight + float-in floating action toolbar

---

## AI TELLS — FORBIDDEN PATTERNS

### Visual & CSS
- NO Neon/Outer Glows (`box-shadow` glows banned)
- NO Pure Black (`#000000` banned — use Zinc-950, Off-Black)
- NO Oversaturated Accents
- NO Excessive Gradient Text on large headers
- NO Custom Mouse Cursors

### Typography
- **NO Inter Font** — BANNED. Use `Geist`, `Outfit`, `Cabinet Grotesk`, `Satoshi`
- NO Oversized H1s that just scream — control with weight/color
- Serif ONLY for creative/editorial. NEVER on clean Dashboards

### Layout & Spacing
- NO 3-Column Card Layouts (generic equal cards) — use 2-col Zig-Zag, asymmetric grid, or horizontal scroll
- Math-perfect padding/margins — no floating elements with awkward gaps

### Content & Data (The "Jane Doe" Effect)
- NO Generic Names ("John Doe", "Sarah Chan", "Jack Su") — use creative realistic names
- NO Generic Avatars (standard SVG egg icons)
- NO Fake Numbers (`99.99%`, `50%`) — use organic data (`47.2%`, `+1 (312) 847-1928`)
- NO Startup Slop Names ("Acme", "Nexus", "SmartFlow")
- NO AI Copywriting Clichés ("Elevate", "Seamless", "Unleash", "Next-Gen")

### External Resources
- NO Broken Unsplash Links — use `https://picsum.photos/seed/{random_string}/800/600`
- shadcn/ui MUST be customized — never in generic default state

---

## PERFORMANCE GUARDRAILS

- DOM Cost: Grain/noise filters ONLY on `fixed, pointer-events-none` pseudo-elements — NEVER on scrolling containers
- Hardware Acceleration: Animate EXCLUSIVELY via `transform` and `opacity`. NEVER `top`, `left`, `width`, `height`
- Z-Index Restraint: NEVER spam `z-50` unprompted. Use only for systemic layer contexts
- GSAP vs Framer: NEVER mix in same component tree. Framer = UI/Bento. GSAP = isolated full-page scrolltelling/canvas

---

## PRE-FLIGHT CHECK

Before outputting any frontend code:
- [ ] Global state used appropriately (no arbitrary prop-drilling)?
- [ ] Mobile layout collapse guaranteed (`w-full`, `px-4`, `max-w-7xl mx-auto`)?
- [ ] Full-height sections use `min-h-[100dvh]` (NOT `h-screen`)?
- [ ] `useEffect` animations have strict cleanup functions?
- [ ] Empty, loading, and error states provided?
- [ ] Cards omitted in favor of spacing where possible?
- [ ] CPU-heavy perpetual animations isolated in Client Components?
- [ ] Dependency check: verify `package.json` before importing any 3rd-party library?
