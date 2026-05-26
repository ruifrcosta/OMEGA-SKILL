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
