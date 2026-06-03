# Design System Tokens Reference

Consolidated from: oerlellijk/design-system-skill + dylantarre/design-system-skills

---

## Table of Contents
1. [Token Architecture (Primitive → Semantic → Component)](#architecture)
2. [Color Scales — OKLCH](#color)
3. [Type Scale Mathematics](#type)
4. [Spacing Scale](#spacing)
5. [Fluid Layout: Grid & Flex Patterns](#layout)
6. [Motion Scale](#motion)
7. [Shadow, Radius, Z-Index](#elevation)
8. [Adaptive Color Tokens](#adaptive)
9. [Framework Integration](#framework)
10. [Accessibility Compliance Checklist](#a11y)
11. [Design System Architect Agent Protocol](#agent)

---

## 1. Token Architecture {#architecture}

**Three-layer hierarchy — always follow this order:**

```
Primitive → Semantic → Component
```

### Primitive tokens (raw values, no context)
```json
{
  "color": { "blue-500": { "value": "oklch(55% 0.18 250)" } },
  "space": { "4": { "value": "1rem" } }
}
```

### Semantic tokens (purpose-based, alias primitives)
```json
{
  "color": {
    "action-primary": { "value": "{color.blue-500}" },
    "surface-default": { "value": "{color.neutral-950}" }
  }
}
```

### Component tokens (stateful, alias semantic)
```json
{
  "button": {
    "background-default":  { "value": "{color.action-primary}" },
    "background-hover":    { "value": "{color.action-primary-dark}" },
    "background-disabled": { "value": "{color.neutral-300}" }
  }
}
```

**Implementation checklist:**
- [ ] Audit existing values → establish naming convention
- [ ] Define primitives (raw values, no semantic meaning)
- [ ] Define semantic tokens (reference primitives)
- [ ] Create theme overrides (dark.json, brand variants)
- [ ] Add component tokens for stateful components

---

## 2. Color Scales — OKLCH {#color}

OKLCH is perceptually uniform. Always generate palettes in OKLCH, never raw hex.

### 11-step scale (50–950)

| Step | Lightness | Typical Use |
|------|-----------|-------------|
| 50 | 97% | Subtle backgrounds |
| 100 | 93% | Hover on light |
| 200 | 87% | Borders, dividers |
| 300 | 78% | Disabled states |
| 400 | 65% | Placeholder text |
| 500 | 55% | Primary brand |
| 600 | 45% | Hover on dark |
| 700 | 37% | Active states |
| 800 | 28% | Text on light |
| 900 | 18% | Strong text |
| 950 | 12% | Max contrast |

### OKLCH generation pattern
```css
:root {
  --color-brand-50:  oklch(97% 0.02 250);
  --color-brand-100: oklch(93% 0.05 250);
  --color-brand-200: oklch(87% 0.09 250);
  --color-brand-300: oklch(78% 0.13 250);
  --color-brand-400: oklch(65% 0.16 250);
  --color-brand-500: oklch(55% 0.18 250);  /* brand primary */
  --color-brand-600: oklch(45% 0.17 250);
  --color-brand-700: oklch(37% 0.15 250);
  --color-brand-800: oklch(28% 0.12 250);
  --color-brand-900: oklch(18% 0.08 250);
  --color-brand-950: oklch(12% 0.05 250);
}
```

### Semantic color mapping
```css
:root {
  --color-action-primary:       var(--color-brand-500);
  --color-action-primary-hover: var(--color-brand-600);
  --color-surface-default:      var(--color-neutral-950);
  --color-surface-raised:       var(--color-neutral-900);
  --color-text-primary:         var(--color-neutral-50);
  --color-text-secondary:       var(--color-neutral-400);
  --color-border-subtle:        var(--color-neutral-800);
  --color-border-default:       var(--color-neutral-700);
}
```

---

## 3. Type Scale Mathematics {#type}

### Fluid formula
```
font-size: clamp(min, preferred, max);
slope = (maxSize - minSize) / (maxViewport - minViewport)
intercept = minSize - slope × minViewport
preferred = (slope × 100)vw + intercept
```

### Scale ratios
| Ratio | Name | Character |
|-------|------|-----------|
| 1.125 | Major Second | Tight, compact UI |
| 1.200 | Minor Third | Balanced, versatile |
| 1.250 | Major Third | Comfortable reading |
| 1.333 | Perfect Fourth | Spacious, editorial |
| 1.618 | Golden Ratio | Classical proportion |

### CSS output (Major Third, 320→1280 viewport)
```css
:root {
  --font-xs:   clamp(0.75rem,  0.7vw + 0.52rem,  0.875rem);
  --font-sm:   clamp(0.875rem, 0.8vw + 0.62rem,  1rem);
  --font-base: clamp(1rem,     0.9vw + 0.71rem,  1.125rem);
  --font-lg:   clamp(1.125rem, 1.0vw + 0.8rem,   1.25rem);
  --font-xl:   clamp(1.25rem,  1.1vw + 0.9rem,   1.5rem);
  --font-2xl:  clamp(1.5rem,   1.3vw + 1.1rem,   2rem);
  --font-3xl:  clamp(1.875rem, 1.6vw + 1.4rem,   2.5rem);
  --font-4xl:  clamp(2.25rem,  2.0vw + 1.6rem,   3rem);
  --font-5xl:  clamp(3rem,     2.8vw + 2.1rem,   4rem);
}
```

---

## 4. Spacing Scale {#spacing}

Base 16px, ratio 1.5 (Perfect Fifth). Fluid via clamp().

### Base scale
| Token | Value |
|-------|-------|
| `--size-3xs` | clamp(0.25rem, …, 0.31rem) |
| `--size-2xs` | clamp(0.5rem, …, 0.63rem) |
| `--size-xs`  | clamp(0.75rem, …, 0.94rem) |
| `--size-sm`  | clamp(1rem, …, 1.25rem) |
| `--size-md`  | clamp(1.5rem, …, 1.88rem) |
| `--size-lg`  | clamp(2rem, …, 2.5rem) |
| `--size-xl`  | clamp(3rem, …, 3.75rem) |
| `--size-2xl` | clamp(4rem, …, 5rem) |
| `--size-3xl` | clamp(6rem, …, 7.5rem) |

### 1-up and 2-up pairs (use for section/hero spacing)
```css
--size-sm-md: clamp(1rem,  0.8rem + 1vw,  1.88rem);
--size-md-lg: clamp(1.5rem, 1.2rem + 1.5vw, 2.5rem);
--size-lg-xl: clamp(2rem,  1.5rem + 2.5vw, 3.75rem);
--size-sm-lg: clamp(1rem,  0.6rem + 2vw,   2.5rem); /* 2-up */
--size-md-xl: clamp(1.5rem, 0.9rem + 3vw,  3.75rem); /* 2-up */
```

---

## 5. Fluid Layout: Grid & Flex Patterns {#layout}

**Decision tree: Grid vs Flex**
```
Need explicit 2D control (rows AND columns)? → Grid
Need items to wrap?                          → Flex + flex-wrap
Single axis alignment?                       → Flex
Need overlay/stacking?                       → Grid (grid-area trick)
```

### Auto-responsive grid (no breakpoints)
```css
.grid-auto {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(18rem, 100%), 1fr));
  gap: var(--size-md);
}
```

### Stack (vertical flex)
```css
.stack { display: flex; flex-direction: column; gap: var(--size-sm); }
```

### Cluster (horizontal wrap)
```css
.cluster { display: flex; flex-wrap: wrap; gap: var(--size-xs); align-items: center; }
```

### Switcher (auto row→column at breakpoint)
```css
.switcher { display: flex; flex-wrap: wrap; gap: var(--size-md); }
.switcher > * { flex-grow: 1; flex-basis: calc((30rem - 100%) * 999); }
```

### Sidebar layout
```css
.with-sidebar { display: flex; flex-wrap: wrap; gap: var(--size-lg); }
.with-sidebar > :first-child { flex-basis: 250px; flex-grow: 1; }
.with-sidebar > :last-child { flex-basis: 0; flex-grow: 999; min-width: 60%; }
```

### Reel (horizontal scroll)
```css
.reel { display: flex; gap: var(--size-sm); overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none; }
.reel > * { flex-shrink: 0; scroll-snap-align: start; }
```

**Hard rules (never break):**
- Icons always in `aspect-ratio: 1` containers
- Always use logical properties (`padding-block`, not `padding-top`)
- `gap` on containers, never `margin` between siblings
- No hardcoded px values — always use tokens
- Every wrapper declares `display: grid` or `display: flex`

---

## 6. Motion Scale {#motion}

```css
:root {
  /* Duration */
  --motion-instant:   50ms;
  --motion-fast:     100ms;
  --motion-normal:   200ms;
  --motion-slow:     300ms;
  --motion-slower:   500ms;
  --motion-slowest:  800ms;

  /* Easing */
  --ease-out:   cubic-bezier(0.23, 1, 0.32, 1);
  --ease-in:    cubic-bezier(0.55, 0, 1, 0.45);
  --ease-inout: cubic-bezier(0.77, 0, 0.175, 1);
  --ease-drawer:cubic-bezier(0.32, 0.72, 0, 1);
  --ease-spring:cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* Press feedback — every interactive element */
.pressable { transition: transform var(--motion-fast) var(--ease-out); }
.pressable:active { transform: scale(0.97); }

/* Reduced motion — always respect */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 7. Shadow, Radius, Z-Index {#elevation}

```css
:root {
  /* Shadow scale */
  --shadow-xs: 0 1px 2px oklch(0% 0 0 / 8%);
  --shadow-sm: 0 2px 4px oklch(0% 0 0 / 10%);
  --shadow-md: 0 4px 12px oklch(0% 0 0 / 12%);
  --shadow-lg: 0 8px 24px oklch(0% 0 0 / 14%);
  --shadow-xl: 0 16px 48px oklch(0% 0 0 / 18%);

  /* Radius scale */
  --radius-xs: 2px;  --radius-sm: 4px;  --radius-md: 8px;
  --radius-lg: 12px; --radius-xl: 16px; --radius-full: 9999px;

  /* Z-index scale */
  --z-below:    -1;
  --z-base:      0;
  --z-raised:   10;
  --z-dropdown: 100;
  --z-sticky:   200;
  --z-overlay:  300;
  --z-modal:    400;
  --z-toast:    500;
  --z-tooltip:  600;
}
```

---

## 8. Adaptive Color Tokens {#adaptive}

Tokens that auto-adapt to any background via `currentColor`:

```css
:root {
  --alpha-100: 8%; --alpha-200: 12%; --alpha-300: 16%;
  --alpha-400: 24%; --alpha-500: 32%;

  --surface-hover:    color-mix(in srgb, currentColor var(--alpha-100), transparent);
  --surface-active:   color-mix(in srgb, currentColor var(--alpha-200), transparent);
  --surface-selected: color-mix(in srgb, currentColor var(--alpha-300), transparent);
  --surface-disabled: color-mix(in srgb, currentColor 4%, transparent);

  --border-subtle:  color-mix(in srgb, currentColor var(--alpha-100), transparent);
  --border-default: color-mix(in srgb, currentColor var(--alpha-200), transparent);
  --border-strong:  color-mix(in srgb, currentColor var(--alpha-400), transparent);
}
```

---

## 9. Framework Integration {#framework}

### Tailwind v4 (@theme mapping)
```css
@import "tailwindcss";
@theme {
  --spacing-sm: var(--size-sm);
  --spacing-md: var(--size-md);
  --font-size-base: var(--font-base);
  --color-action-primary: var(--color-brand-500);
  --color-surface-hover: var(--surface-hover);
}
```

### Style Dictionary (multi-platform output)
```js
export default {
  source: ['tokens/**/*.json'],
  platforms: {
    css: { transformGroup: 'css', buildPath: 'dist/', files: [{ destination: 'tokens.css', format: 'css/variables' }] },
    ios: { transformGroup: 'ios-swift', buildPath: 'ios/Sources/' },
    android: { transformGroup: 'android', buildPath: 'android/src/' }
  }
};
```

---

## 10. Accessibility Compliance Checklist {#a11y}

- [ ] Focus states: `outline: 2px solid currentColor; outline-offset: 2px` on all interactive elements
- [ ] Contrast: Normal text ≥ 4.5:1, Large text ≥ 3:1, UI components ≥ 3:1
- [ ] Touch targets: min 44×44px (iOS) / 48×48dp (Android)
- [ ] Reduced motion: `@media (prefers-reduced-motion: reduce)` implemented
- [ ] ARIA: `role`, `aria-label`, `aria-describedby` on all interactive patterns
- [ ] Color not sole conveyor of information (use icons/text alongside)
- [ ] Dark mode: all semantic tokens override in `[data-theme=dark]`

---

## 11. Design System Architect Agent Protocol {#agent}

On first run (no `design_master.md` found):
1. Ask fluid approach: typography / spacing / both / neither
2. Ask type ratio: 1.125 / 1.200 / 1.250 / 1.333 / custom
3. Ask viewport range: 320–1280 / 360–1440 / custom
4. Generate `theme.html` with type scale + spacing scale + 2–3 button variants + 2–3 input variants
5. Ask user to confirm choices → create `design_master.md`
6. Generate token files (CSS / Tailwind / JSON)

On subsequent runs:
1. Read `design_master.md` first
2. Apply recorded decisions exactly
3. New style decision → ask → record → apply

Questions to ask before any layout/component:
- "What's the priority on small screens?"
- "Should any elements be hidden on mobile?"
- "Is there an existing similar component to match?"
