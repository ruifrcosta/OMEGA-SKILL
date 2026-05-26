# Taste Engine — Anti-Slop Frontend Reference

Sourced from: taste-skill (Leonxlnx), emil-design-eng philosophy, and the UI prompts corpus.
Read this file before ANY frontend/UI task.

---

## 0. BRIEF INFERENCE — Read Before Touching Code

Before writing a single line, state aloud:
**"Reading this as: <page kind> for <audience>, with a <vibe>, leaning toward <design family>."**

| Page Kind | Examples |
|-----------|---------|
| B2B SaaS landing | Linear-style, Geist, restrained motion |
| Agency / creative | Awwwards, experimental, kinetic type |
| Premium consumer | Apple-y, glassmorphism, Instrument Serif |
| E-Commerce | Playfair Display / Nunito / Amber |
| Portfolio | Editorial, scroll-driven, custom type |
| Public sector | Trust-first, GOV.UK, accessibility-critical |

If brief is ambiguous → ask exactly **one** question, never a dump.
If clearly inferable → declare the design read and proceed.

---

## 1. THE THREE DIALS

Set these after the design read. Every layout, motion, and density decision is gated by them.

```
DESIGN_VARIANCE:  8   (1=Perfect Symmetry, 10=Artsy Chaos)
MOTION_INTENSITY: 6   (1=Static, 10=Cinematic Physics)
VISUAL_DENSITY:   4   (1=Art Gallery, 10=Cockpit)
```

### Dial → Stack Inference

| Signal | VARIANCE | MOTION | DENSITY |
|--------|----------|--------|---------|
| "minimalist / clean / Linear-style" | 5-6 | 3-4 | 2-3 |
| "premium consumer / Apple-y / luxury" | 7-8 | 5-7 | 3-4 |
| "playful / agency / Awwwards" | 9-10 | 8-10 | 3-4 |
| "landing page / marketing (default)" | 7-9 | 6-8 | 3-5 |
| "trust-first / public-sector" | 3-4 | 2-3 | 4-5 |

---

## 2. HARDCODED BANS (never break)

### Visual
- NO Inter as primary font — use Geist, Outfit, Cabinet Grotesk, Satoshi first
- NO AI purple/blue glow by default
- NO neon gradients — use neutral bases (Zinc/Slate/Stone) + singular accent
- NO nested card grids as default layout
- NO div-based fake product screenshots
- NO hand-rolled SVG icon paths
- NO glassmorphism as default — only for premium/Apple briefs

### Typography
- NO em-dash (`—`) anywhere. Ever. Not in headlines, body, attribution, captions, buttons.
  Use period, comma, or hyphen instead. This is a hard ban.
- NO oversized H1s that just scream without hierarchy
- NO serif for dashboards or data-dense product UI

### Layout
- NEVER `h-screen` for heroes — always `min-h-[100dvh]`
- NEVER complex flex math (`w-[calc(33%-1rem)]`) — use CSS Grid
- NEVER centered hero when `DESIGN_VARIANCE > 4` — force asymmetric/split

### Motion
- NEVER `window.addEventListener('scroll', ...)` — use Motion `useScroll()` / GSAP ScrollTrigger
- NEVER animate `width`, `height`, `top`, `left` — only `transform` and `opacity`
- NEVER `useState` for continuous values (mouse pos, scroll) — use `useMotionValue`

### Content / Copy
- NO em-dashes (covered above, repeated for emphasis)
- NO fake-precise numbers without sourcing
- NO "Elevate", "Seamless", "Unleash", "Next-Gen", "Game-changer"
- NO "John Doe", "Acme Co", "SmartFlow" — invent contextual, premium names
- NO section-number eyebrows (`001 · Capabilities`, `06 · how it works`)
- NO scroll cues (`Scroll`, `↓ scroll`, `Scroll to explore`)

---

## 3. LIQUID GLASS — Canonical CSS

Use only for: premium consumer, Apple-adjacent, luxury, media-overlay contexts.
NOT for: dashboards, public-sector, boring B2B.
Label as "web approximation, not official Apple Liquid Glass."

```css
.liquid-glass {
  background: rgba(255, 255, 255, 0.01);
  background-blend-mode: luminosity;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border: none;
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}
.liquid-glass::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1.4px;
  background: linear-gradient(180deg,
    rgba(255,255,255,0.45) 0%, rgba(255,255,255,0.15) 20%,
    rgba(255,255,255,0) 40%, rgba(255,255,255,0) 60%,
    rgba(255,255,255,0.15) 80%, rgba(255,255,255,0.45) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}
```

---

## 4. ANIMATION DECISION FRAMEWORK

**Ask before animating:** How often will users see this?

| Frequency | Decision |
|-----------|----------|
| 100+ times/day (keyboard shortcuts) | NO animation. Ever. |
| Tens/day (tab switches, hover) | Remove or drastically reduce |
| Occasional (modals, drawers) | Standard animation |
| Rare/first-time (onboarding) | Can add delight |

### Easing (always use custom curves)

```css
--ease-out:     cubic-bezier(0.23, 1, 0.32, 1);    /* UI interactions — feels instant */
--ease-in-out:  cubic-bezier(0.77, 0, 0.175, 1);   /* on-screen movement */
--ease-drawer:  cubic-bezier(0.32, 0.72, 0, 1);    /* iOS-like drawer */
```

Never `ease-in` for UI — it starts slow and feels broken.

### Duration Targets

| Element | Duration |
|---------|----------|
| Button press feedback | 100-160ms |
| Tooltips, small popovers | 125-200ms |
| Dropdowns | 150-250ms |
| Modals, drawers | 200-500ms |

### Entry/Exit Rules
- NEVER `scale(0)` — start from `scale(0.95)` + `opacity: 0`
- Exit faster than enter (60-70% of enter duration)
- Stagger lists: 30-60ms per item
- Popovers: `transform-origin: var(--radix-popover-content-transform-origin)`
- Modals: keep `transform-origin: center`

---

## 5. COMPONENT QUALITY GATES

Every component must have ALL states implemented:
`default | hover | focus | active | loading | error | empty | success | disabled`

### Button
```css
.button { transition: transform 160ms ease-out; }
.button:active { transform: scale(0.97); }
```

### GSAP Sticky-Stack (canonical skeleton)
```tsx
ScrollTrigger.create({
  trigger: card,
  start: "top top",           // ← ALWAYS "top top"
  endTrigger: lastCard,
  end: "top top",
  pin: true,
  pinSpacing: false,
});
```

### GSAP Horizontal-Pan (canonical skeleton)
```tsx
gsap.to(track, {
  x: -distance,
  ease: "none",
  scrollTrigger: {
    trigger: wrap,
    start: "top top",         // ← ALWAYS "top top"
    end: () => `+=${distance}`,
    pin: true,
    scrub: 1,
    invalidateOnRefresh: true,
  },
});
```

---

## 6. DYNAMIC BRAND MORPHING TABLE

Applied automatically based on project category detection:

| Category | Heading / Body | Light Accent | Dark Accent |
|----------|---------------|-------------|-------------|
| Healthcare | Figtree / DM Sans | `#059669` Emerald | `#34D399` |
| Finance | Söhne / IBM Plex Sans | `#1D4ED8` Royal Blue | `#60A5FA` |
| Productivity | Geist Sans / Geist Mono | `#7C3AED` Violet | `#A78BFA` |
| E-Commerce | Playfair Display / Nunito | `#0F0F0F` Pitch Black | `#FBBF24` |
| Fitness | Space Grotesk / DM Sans | `#16A34A` Vitality | `#4ADE80` |
| Education | Lora / Source Serif 4 | `#2563EB` Blue | `#60A5FA` |
| Social | Plus Jakarta Sans / DM Sans | `#7C3AED` Violet | `#A78BFA` |
| SaaS/Tech | Geist / Geist Mono | `#0EA5E9` Sky | `#38BDF8` |
| NFT/Web3 | Anton / mono | `#6FFF00` Neon | `#A3E635` |
| Travel | Instrument Serif / Barlow | `#F59E0B` Amber | `#FBBF24` |
| Media/Film | Inter / mono | `#FFFFFF` White | `#E5E5E5` |

---

## 7. UI-UX PRO MAX INTEGRATION

### Mandatory quality gates before shipping any UI

**Accessibility (CRITICAL):**
- Color contrast minimum 4.5:1 for body text, 3:1 for large text
- All interactive elements have visible focus rings (2-4px)
- Icon-only buttons must have `aria-label`
- Never convey info by color alone (add icon/text)
- `prefers-reduced-motion` respected for MOTION_INTENSITY > 3

**Touch & Interaction (CRITICAL):**
- Min tap target: 44×44pt (Apple) / 48×48dp (Material)
- Min spacing between targets: 8px
- No hover-only interactions (must work on touch)
- Loading state on all async buttons
- `cursor: pointer` on all clickable elements

**Performance (HIGH):**
- Hero images: `next/image priority` or preloaded
- Lazy load non-above-fold components
- Declare `width`/`height` on all images (prevents CLS)
- Virtualize lists with 50+ items

### Route to data files
For detailed style/color/font queries:
- `references/external/ui-ux-pro-max/data/styles.csv` — 50+ styles
- `references/external/ui-ux-pro-max/data/colors.csv` — 161 palettes
- `references/external/ui-ux-pro-max/data/typography.csv` — 57 font pairings
- `references/external/ui-ux-pro-max/data/ux-guidelines.csv` — 99 UX rules
- `references/external/ui-ux-pro-max/data/stacks/` — per-stack patterns

---

## 8. HERO SECTION PATTERNS (from UI prompts corpus)

### Canonical Video Hero Pattern
```tsx
<div className="relative min-h-[100dvh] w-full overflow-hidden">
  {/* Layer 0: video */}
  <video autoPlay loop muted playsInline
    className="absolute inset-0 w-full h-full object-cover z-0" />

  {/* Layer 1: gradient overlay (only if needed) */}
  <div className="absolute inset-0 bg-gradient-to-b from-black/20 via-transparent to-black/60 z-[1] pointer-events-none" />

  {/* Layer 2: nav + content */}
  <div className="relative z-10 flex flex-col min-h-[100dvh]">
    {/* navbar */}
    {/* hero content */}
  </div>
</div>
```

### Fade-Rise Animation (canonical)
```css
@keyframes fade-rise {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}
.animate-fade-rise          { animation: fade-rise 0.8s ease-out both; }
.animate-fade-rise-delay    { animation: fade-rise 0.8s ease-out 0.2s both; }
.animate-fade-rise-delay-2  { animation: fade-rise 0.8s ease-out 0.4s both; }
```

### Blur-Fade-Up (cinematic)
```css
@keyframes blurFadeUp {
  from { opacity: 0; filter: blur(20px); transform: translateY(40px); }
  to   { opacity: 1; filter: blur(0);    transform: translateY(0); }
}
.animate-blur-fade-up { animation: blurFadeUp 1s ease-out forwards; opacity: 0; }
```

---

## 9. PRE-FLIGHT CHECKLIST

Run before ANY frontend output:

```
□ Design read declared?
□ Three dials set (VARIANCE / MOTION / DENSITY)?
□ ZERO em-dashes in entire output?
□ Page theme locked (no mid-page mode flip)?
□ Color consistency locked (one accent throughout)?
□ Shape consistency locked (one corner-radius system)?
□ Hero fits viewport (≤2 lines headline, ≤20 words sub, CTA visible)?
□ min-h-[100dvh] used (never h-screen)?
□ No centered hero when VARIANCE > 4?
□ Reduced motion respected for MOTION_INTENSITY > 3?
□ All component states implemented (default/hover/focus/error/loading/empty)?
□ Button contrast passes WCAG AA?
□ No fake div screenshots?
□ No hand-rolled SVG icon paths?
□ useMotionValue (not useState) for continuous values?
□ No window.addEventListener('scroll')?
□ GSAP uses start:"top top" + pin:true?
□ All images have width/height declared?
□ Touch targets ≥ 44×44pt?
```
