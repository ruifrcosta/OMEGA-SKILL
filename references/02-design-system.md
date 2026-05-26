# Design System Reference

## Table of Contents
1. [Visual Silence Philosophy](#philosophy)
2. [Design Tokens — Semantic System](#tokens)
3. [Typography — The Primary Visual Element](#typography)
4. [Component Standards](#components)
5. [Motion & Animation Rules](#motion)
6. [Accessibility — WCAG AA Minimum](#accessibility)
7. [HTML Generation Standards](#html)

---

## 1. Visual Silence Philosophy {#philosophy}

The OMEGA design language is inspired by Claude, Linear, Notion, and Vercel.
Cognitive clarity over visual noise. Structural refinement over decoration.

**Core principles:**
- **No cards.** Content lives directly on the surface. Organisation via spacing, not containers.
- **No shadows.** Never `box-shadow`, `drop-shadow`, or `elevation`. Hierarchy via typography + whitespace.
- **No AI slop fonts.** Never Inter, Roboto, or Arial as primary on premium surfaces.
- **4/8dp grid.** Always. Every spacing value is a multiple of 4.
- **Semantic tokens.** Raw hex values never appear in component code.

**Hard bans:**
- `transition: all` → specify exact properties + duration
- `scale(0)` entrance → always `scale(0.95) + opacity: 0`
- `ease-in` on UI → always `cubic-bezier(0.23, 1, 0.32, 1)`
- Nested card grids · glassmorphism · neon gradients · side-stripe borders
- Copy: "Elevate" "Seamless" "Unleash" "Next-Gen" "Game-changer" em dashes (—)

---

## 2. Design Tokens — Semantic System {#tokens}

### Universal Semantic Token Map

```css
:root {
  /* Surfaces */
  --bg:        #ffffff;              /* primary surface */
  --bg-subtle: #fafafa;              /* secondary surface */

  /* Text */
  --fg:        #0f172a;              /* primary text */
  --muted:     #64748b;              /* secondary / captions */

  /* Brand */
  --accent:    [category-specific]; /* see brand table below */
  --accent-hover: [accent darkened 6%];

  /* Structure */
  --border:    rgba(15,23,42,0.05); /* near-invisible */
  --radius:    0.5rem;              /* 8px base, scale up as needed */

  /* Feedback */
  --error:     #dc2626;
  --success:   #16a34a;
  --warning:   #d97706;

  /* Motion */
  --ease-out:    cubic-bezier(0.23, 1, 0.32, 1);
  --ease-in:     cubic-bezier(0.55, 0, 1, 0.45);
  --ease-inout:  cubic-bezier(0.77, 0, 0.175, 1);
  --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
}

.dark {
  --bg:        #0a0a0a;
  --bg-subtle: #111111;
  --fg:        #f5f5f5;
  --muted:     #a3a3a3;
  --border:    rgba(255,255,255,0.06);
}
```

### Brand Morphing Table (category → full palette)

| Category | Heading Font | Body Font | Light Accent | Dark Accent |
|----------|-------------|-----------|-------------|------------|
| Healthcare | Figtree 600 | DM Sans 400 | `#059669` | `#34d399` |
| Finance | Söhne 600 | IBM Plex Sans 400 | `#1d4ed8` | `#60a5fa` |
| Productivity | Geist 600 | Geist 400 | `#7c3aed` | `#a78bfa` |
| E-Commerce | Playfair Display 600 | Nunito 400 | `#0f0f0f` | `#fbbf24` |
| Fitness | Space Grotesk 600 | DM Sans 400 | `#16a34a` | `#4ade80` |
| Education | Lora 600 | Source Serif 4 400 | `#2563eb` | `#60a5fa` |
| Social | Plus Jakarta Sans 600 | DM Sans 400 | `#7c3aed` | `#a78bfa` |
| Travel | Playfair Display 600 | DM Sans 400 | `#c2410c` | `#fb923c` |
| Developer | Geist 600 | Geist Mono 400 | `#0f172a` | `#f8fafc` |

### Tailwind Config (token-bridged)

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg:      'var(--bg)',
        'bg-subtle': 'var(--bg-subtle)',
        fg:      'var(--fg)',
        muted:   'var(--muted)',
        accent:  'var(--accent)',
        border:  'var(--border)',
        error:   'var(--error)',
        success: 'var(--success)',
      },
      fontFamily: {
        // override per project using brand table above
        display: ['var(--font-display)', 'sans-serif'],
        body:    ['var(--font-body)', 'sans-serif'],
        mono:    ['var(--font-mono)', 'monospace'],
      },
    }
  }
}
```

---

## 3. Typography — The Primary Visual Element {#typography}

Typography IS the hierarchy. It does the work shadows and cards do in lesser designs.

### Type Scale

| Role | Size | Weight | Line-height | Letter-spacing |
|------|------|--------|-------------|---------------|
| Display | 40px | 600 | 1.1 | -0.03em |
| H1 | 32px | 600 | 1.15 | -0.03em |
| H2 | 24px | 600 | 1.2 | -0.025em |
| H3 | 18px | 600 | 1.3 | -0.02em |
| Body | 16px | 400 | 1.6 | 0 |
| Small | 14px | 400 | 1.5 | 0 |
| Caption | 12px | 500 | 1.4 | 0.01em |

**Rules:**
- Body minimum: 16px on mobile (prevents iOS auto-zoom)
- Headings: always tight letter-spacing (`-0.02em` to `-0.03em`)
- Body: never tighten letter-spacing
- Tabular numbers: `font-variant-numeric: tabular-nums` for data, prices, timers
- Fix widows: never leave one word on the last line of a heading

---

## 4. Component Standards {#components}

Every component ships with ALL states defined. No exceptions.

**Required states:** `default` · `hover` · `pressed` · `disabled` · `loading` · `error` · `empty` · `success`

### Button System

```tsx
// Primary
<button className="
  h-11 px-5 rounded-full
  bg-[var(--accent)] text-white font-medium text-sm
  transition-transform duration-150 ease-[var(--ease-out)]
  hover:opacity-90
  active:scale-[0.97]
  disabled:opacity-40 disabled:pointer-events-none
">
  Get started
</button>

// Secondary
<button className="
  h-11 px-5 rounded-full border border-[var(--border)]
  bg-transparent text-[var(--fg)] font-medium text-sm
  transition-transform duration-150 ease-[var(--ease-out)]
  hover:bg-[var(--bg-subtle)]
  active:scale-[0.97]
">
  Learn more
</button>
```

### Input System (invisible, never enterprise-form style)

```tsx
<div className="space-y-1">
  <label className="text-sm font-medium text-[var(--fg)]">
    Email
  </label>
  <input
    className="
      w-full h-11 px-0
      bg-transparent border-0 border-b border-[var(--border)]
      text-[var(--fg)] text-sm
      placeholder:text-[var(--muted)]
      focus:outline-none focus:border-[var(--accent)]
      transition-colors duration-150
    "
    type="email"
    placeholder="you@company.com"
  />
  {error && (
    <p className="text-xs text-[var(--error)]">{error}</p>
  )}
</div>
```

### List Items (never cards)

```tsx
// Content lives on the surface. Separator only.
<div className="divide-y divide-[var(--border)]">
  {items.map(item => (
    <div key={item.id} className="
      flex items-center justify-between py-4
      transition-opacity duration-100
      active:opacity-60
    ">
      <div>
        <p className="text-sm font-medium text-[var(--fg)]">{item.title}</p>
        <p className="text-xs text-[var(--muted)] mt-0.5">{item.subtitle}</p>
      </div>
      <span className="text-xs text-[var(--muted)]">{item.meta}</span>
    </div>
  ))}
</div>
```

---

## 5. Motion & Animation Rules {#motion}

### Frequency Gate (run before any animation decision)

| Frequency | Decision |
|-----------|----------|
| 100+/day (keyboard shortcuts, command palette) | **No animation. Ever.** |
| Tens/day (tab switches, list navigation) | Minimal or none |
| Occasional (modals, sheets, drawers) | Standard 150–300ms |
| Rare / first-time (onboarding, celebrations) | Can add delight |

### Enforced Easing Curves

```css
/* NEVER use ease, ease-in, or linear for UI */
--ease-out:    cubic-bezier(0.23, 1, 0.32, 1);   /* entering elements */
--ease-in:     cubic-bezier(0.55, 0, 1, 0.45);   /* exiting elements */
--ease-inout:  cubic-bezier(0.77, 0, 0.175, 1);  /* on-screen movement */
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);   /* iOS-like sheets */
```

### Duration Scale

| Element | Duration |
|---------|---------|
| Press feedback | 100–150ms |
| Tooltip, small popover | 125–175ms |
| Dropdown, select | 150–200ms |
| Modal, drawer, sheet | 220–350ms |
| Page transition | 200–300ms |

### Entry Rules

```css
/* ALWAYS start from these values, never from scale(0) or opacity(0) alone */
.entering {
  transform: scale(0.95);
  opacity: 0;
}
.entered {
  transform: scale(1);
  opacity: 1;
  transition: transform 200ms var(--ease-out), opacity 200ms var(--ease-out);
}
```

### Popover Origin (critical)

```css
/* Popovers scale from their trigger, never from center */
.popover { transform-origin: var(--radix-popover-content-transform-origin); }
.tooltip { transform-origin: var(--radix-tooltip-content-transform-origin); }
/* Exception: modals use center because they're not anchored to a trigger */
.modal { transform-origin: center; }
```

### Stagger (lists entering together)

```css
.item:nth-child(1) { animation-delay: 0ms; }
.item:nth-child(2) { animation-delay: 40ms; }
.item:nth-child(3) { animation-delay: 80ms; }
.item:nth-child(4) { animation-delay: 120ms; }
/* Max stagger: 40–60ms per item. Never block interaction during stagger. */
```

### Press Feedback (mandatory on every interactive element)

```css
.pressable {
  transition: transform 150ms var(--ease-out);
}
.pressable:active {
  transform: scale(0.97);
}
```

---

## 6. Accessibility — WCAG AA Minimum {#accessibility}

```
Text contrast:     ≥ 4.5:1 (normal), ≥ 3:1 (large text / UI elements)
Focus indicators:  2px ring, accent color, always visible (never removed)
Touch targets:     ≥ 44×44pt (iOS) / ≥ 48×48dp (Android)
ARIA:              Every icon-only button has aria-label
Keyboard:          Full tab navigation in visual order
Motion:            prefers-reduced-motion respected always
Dynamic type:      Text scales without truncation up to 2× system size
```

```css
/* Focus ring — never remove, always style */
:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  border-radius: 4px;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 7. HTML Generation Standards {#html}

```html
<!-- Semantic, accessible, SSR-compatible -->
<!DOCTYPE html>
<html lang="pt" class="h-full">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <!-- Preload critical fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
</head>
<body class="h-full bg-[var(--bg)] text-[var(--fg)] antialiased">

  <!-- Skip to content for keyboard users -->
  <a href="#main" class="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 z-50">
    Skip to content
  </a>

  <main id="main" role="main" aria-label="Main content">
    <section aria-labelledby="section-title">
      <h2 id="section-title" class="text-xl font-semibold tracking-tight">...</h2>
      <!-- Content with ARIA where meaningful images/icons exist -->
    </section>
  </main>

</body>
</html>
```

**Semantic rules:**
- Every `<section>` has an `aria-labelledby` pointing to its heading
- Icon-only buttons always have `aria-label="..."`
- Meaningful images always have descriptive `alt="..."`
- Decorative images use `alt=""`
- Forms: every input has a visible `<label>`, not just placeholder
- Error messages use `role="alert"` or `aria-live="polite"`

---

## 8. Design Token Generator — OKLCH System {#oklch-tokens}
> Distilled from `dylantarre/design-system-skills`

### OKLCH — Modern Perceptually Uniform Color Space
OKLCH is the default for new projects. It ensures perceptually uniform lightness steps that traditional HSL/RGB cannot guarantee.

```css
/* 11-Step color scale (50-950) using OKLCH */
:root {
  --color-primary-50:  oklch(96% 0.04 250);
  --color-primary-100: oklch(92% 0.07 250);
  --color-primary-200: oklch(85% 0.11 250);
  --color-primary-300: oklch(76% 0.14 250);
  --color-primary-400: oklch(67% 0.16 250);
  --color-primary-500: oklch(57% 0.17 250);  /* base */
  --color-primary-600: oklch(48% 0.16 250);
  --color-primary-700: oklch(40% 0.14 250);
  --color-primary-800: oklch(32% 0.11 250);
  --color-primary-900: oklch(23% 0.07 250);
  --color-primary-950: oklch(15% 0.04 250);
}
```

### Semantic Token Auto-Generation
Auto-generate harmonized semantic colors from brand hue:
| Semantic | Hue Offset from Brand | Example (Brand=250°) |
|---|---|---|
| Success | 145° | oklch(57% 0.17 145) |
| Warning | 70° | oklch(57% 0.17 70) |
| Error | 25° | oklch(57% 0.17 25) |
| Info | 250° (same) | oklch(57% 0.17 250) |

### Chroma Reduction at Extremes
- Lightness > 0.9 → reduce chroma by 30%
- Lightness < 0.2 → reduce chroma by 70%

### Output Formats (ask user before generating)
```
1. CSS Custom Properties   → :root { --color-*: oklch(...) }
2. Tailwind Config         → colors: { primary: { 50: 'oklch(...)' } }
3. JSON Design Tokens      → { "color": { "primary": { "50": { "value": "..." } } } }
```

### Spacing Scale — T-shirt vs Numeric
```css
/* T-shirt naming (simple projects) */
:root {
  --space-xs: 4px;   --space-sm: 8px;   --space-md: 16px;
  --space-lg: 24px;  --space-xl: 32px;  --space-2xl: 48px;
}
/* Numeric naming (design systems) */
:root {
  --space-100: 4px;  --space-200: 8px;  --space-300: 12px;
  --space-400: 16px; --space-500: 24px; --space-600: 32px;
  --space-700: 48px; --space-800: 64px;
}
```

---

## 9. UI/UX Consultation — Style-Neutral Framework {#uiux-framework}
> Distilled from `oil-oil/ui-ux-guide`

### Two-Layer Architecture (NEVER merge these)
- **Layer 1 — UX Hard Rules**: Universal across ALL style families
- **Layer 2 — Style Lens**: Per-project, user-selected, never imposed

### UX Hard Rules (Apply to Every Project)
1. **Task-first hierarchy** — CTA identifiable in < 3 seconds
2. **5 states mandatory** — loading · empty · error · success · permission-denied
3. **Affordance + signifier** — clickable looks clickable; constraints shown before submit
4. **Error prevention + recoverability** — prevent first, recover gracefully
5. **Feedback loop closure** — did it work? what changed? what's next?
6. **Consistency** — same interaction = same component + wording + placement
7. **CRAP visual hierarchy** — Contrast / Repetition / Alignment / Proximity
8. **Spacing scale discipline** — pick ONE scale; off-scale values need explicit justification
9. **Help text layering L0–L3** — label → placeholder → hint → error
10. **UI copy discipline** — from user tasks / system state, never AI meta-text

### 8 Style Families (Never default-imposed)
```
modern-minimal    editorial    brutal       playful
premium-luxury    tech-cyberpunk   warm-content   brand-driven
```

### Project Stage Classifier (Run Before First Question)
| Stage | Signals | Opening Direction |
|---|---|---|
| Blank | No files / only setup | Design from scratch |
| Half-done | Components but no design spec | Establish tokens first |
| Mature | Has design-spec.md | Review + iterate |
| Legacy | Inconsistent old patterns | Audit + modernize |
| Uncertain | Mixed signals | Stage 1: scan + classify |

### Phase 0 Rule: Scan Before Asking
```
BEFORE asking ANY question:
1. Check tailwind.config.js — extract existing tokens
2. Check package.json — identify component library (shadcn, MUI, Radix...)
3. Check existing design-spec.md — don't re-derive what's already decided
4. THEN ask only what you don't know
```

### Review Mode — P0/P1/P2 Triage
```
P0 (Critical)   — Violates UX Hard Rule; blocks task completion
P1 (Important)  — Degrades experience; high fix priority
P2 (Polish)     — Consistency issue; low priority
```
Each finding: [Severity] HCI Law: [law name] — Issue: [description] — Fix: [proposal]

### One-Question Protocol
- Ask one question at a time
- Always provide a default the user can accept silently
- No starred (★) recommendations unless user explicitly asks

