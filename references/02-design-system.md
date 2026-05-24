# Design System Reference

## Table of Contents
1. [Claude-Style UI Philosophy](#philosophy)
2. [Design Tokens & Theme Scales](#tokens)
3. [Typography & Readability](#typography)
4. [Component Library Primitives](#components)
5. [Tailwind & CSS Configuration](#tailwind)
6. [Motion & Animation Standards](#motion)
7. [Accessibility & Testing](#accessibility)

---

## 1. Claude-Style UI Philosophy {#philosophy}

The OMEGA TITAN design language is inspired by Anthropic's Claude, Linear, and Vercel. It prioritizes cognitive clarity, minimal distraction, and structural refinement over loud visual embellishments.

### Key Principles

*   **Restrained Elevation**: Avoid deep shadow cascades. Use subtle, sharp border strokes (`1px border-neutral-200` or `dark:border-neutral-800`) to delineate hierarchy.
*   **Tactile Feedback**: Interactive elements should feel physically satisfying through subtle hover scale transforms and custom micro-animations.
*   **Soft Neutral Palettes**: Use high-grade warm/cool grays rather than pure black and white to minimize eye strain.
*   **Conversational Focus**: Layouts are centered around communication and prompt-driven user flows, leaving maximum real estate for content and logs.

---

## 2. Design Tokens & Theme Scales {#tokens}

Use these precise HSL values in all web interfaces to achieve a premium, unified theme.

```css
:root {
  /* Neutrals */
  --bg-primary: hsl(20, 20%, 98%);     /* Warm Cream */
  --bg-secondary: hsl(20, 15%, 95%);
  --border-subtle: hsl(20, 10%, 88%);
  --text-primary: hsl(20, 30%, 12%);
  --text-secondary: hsl(20, 15%, 45%);
  
  /* Accents */
  --accent-primary: hsl(24, 90%, 48%);  /* Clay Orange */
  --accent-hover: hsl(24, 95%, 42%);
  --accent-focus: hsl(24, 95%, 42%, 0.15);
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
}

.dark {
  /* Neutrals */
  --bg-primary: hsl(220, 15%, 10%);    /* Dark Slate */
  --bg-secondary: hsl(220, 12%, 14%);
  --border-subtle: hsl(220, 10%, 20%);
  --text-primary: hsl(220, 20%, 94%);
  --text-secondary: hsl(220, 10%, 65%);
  
  /* Accents */
  --accent-primary: hsl(24, 90%, 55%);  /* Brighter Clay Orange */
  --accent-hover: hsl(24, 95%, 60%);
  --accent-focus: hsl(24, 95%, 60%, 0.25);
}
```

---

## 3. Typography & Readability {#typography}

Use highly readable sans-serif and monospace typography for clean enterprise data representation.

*   **Primary Font**: Inter or Outfit (fallbacks: System-UI, -apple-system, sans-serif)
*   **Monospace Font**: JetBrains Mono or SF Mono (fallbacks: Consolas, monospace)

### Hierarchy Table

| Class | Font Size | Line Height | Letter Spacing | Ideal Use Case |
|-------|-----------|-------------|----------------|----------------|
| `text-xs` | `0.75rem` | `1rem` | `+0.01em` | Metadata, badges, table headers |
| `text-sm` | `0.875rem` | `1.25rem` | `0` | Primary body, inputs, buttons |
| `text-base` | `1rem` | `1.5rem` | `-0.011em` | Secondary titles, chat bubbles |
| `text-lg` | `1.125rem` | `1.75rem` | `-0.018em` | Page subtitles, dialog headers |
| `text-xl` | `1.25rem` | `1.875rem` | `-0.022em` | Section headings, card titles |
| `text-3xl` | `1.875rem` | `2.25rem` | `-0.027em` | Main dashboard titles |

---

## 4. Component Library Primitives {#components}

Every layout must use semantic and accessibility-first structures.

### AI Chat Layout Primitive
```html
<div class="flex h-screen flex-col bg-[var(--bg-primary)] text-[var(--text-primary)] font-sans antialiased">
  <!-- Nav Bar -->
  <header class="flex h-14 items-center justify-between border-b border-[var(--border-subtle)] px-6">
    <div class="flex items-center gap-3">
      <span class="h-6 w-6 rounded bg-[var(--accent-primary)]"></span>
      <h1 class="text-sm font-semibold tracking-tight">OMEGA TITAN Workspace</h1>
    </div>
    <div class="flex items-center gap-2">
      <button class="text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)]">System Health: 100%</button>
    </div>
  </header>

  <!-- Main View -->
  <main class="flex flex-1 overflow-hidden">
    <!-- Sidebar -->
    <aside class="w-64 border-r border-[var(--border-subtle)] bg-[var(--bg-secondary)] p-4 hidden md:block">
      <nav class="space-y-1">
        <a href="#" class="flex items-center gap-3 rounded-md px-3 py-2 text-sm bg-[var(--bg-primary)] text-[var(--text-primary)] shadow-sm font-medium">Dashboard</a>
        <a href="#" class="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-primary)] hover:text-[var(--text-primary)] transition-colors">Observability</a>
      </nav>
    </aside>

    <!-- Chat Area -->
    <section class="flex flex-1 flex-col overflow-y-auto">
      <div class="flex-1 space-y-6 p-6 max-w-3xl mx-auto w-full">
        <!-- AI Message -->
        <div class="flex gap-4">
          <div class="h-8 w-8 shrink-0 rounded-full bg-[var(--accent-primary)] flex items-center justify-center text-white text-xs font-semibold">Ω</div>
          <div class="space-y-2">
            <p class="text-sm font-medium">Omega Titan Engine</p>
            <div class="text-sm text-[var(--text-primary)] leading-relaxed bg-[var(--bg-secondary)] rounded-2xl p-4 border border-[var(--border-subtle)]">
              Welcome to OMEGA TITAN. All systems initialized and secure. Ready to orchestrate.
            </div>
          </div>
        </div>
      </div>

      <!-- Prompt Input Panel -->
      <div class="border-t border-[var(--border-subtle)] p-4">
        <div class="max-w-3xl mx-auto relative">
          <textarea class="w-full min-h-[50px] max-h-[200px] bg-[var(--bg-secondary)] border border-[var(--border-subtle)] rounded-xl py-3 pl-4 pr-12 text-sm focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)] resize-none" placeholder="Ask anything..."></textarea>
          <button class="absolute right-3 bottom-3 h-8 w-8 rounded-md bg-[var(--accent-primary)] hover:bg-[var(--accent-hover)] text-white flex items-center justify-center transition-colors">
            &rarr;
          </button>
        </div>
      </div>
    </section>
  </main>
</div>
```

---

## 5. Tailwind & CSS Configuration {#tailwind}

Add this system definition to `tailwind.config.js` to ensure tokens sync perfectly:

```javascript
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        titan: {
          bg: {
            primary: 'var(--bg-primary)',
            secondary: 'var(--bg-secondary)',
          },
          border: 'var(--border-subtle)',
          accent: {
            DEFAULT: 'var(--accent-primary)',
            hover: 'var(--accent-hover)',
          }
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        sharp: 'var(--shadow-sm)',
        medium: 'var(--shadow-md)',
      }
    }
  }
}
```

---

## 6. Motion & Animation Standards {#motion}

Never use flashy bounce animations in enterprise dashboards. All transitions should follow standard ease-in-out curves with small durations to maximize UX responsiveness.

### Framer Motion Constants

```typescript
export const springTight = {
  type: "spring",
  stiffness: 400,
  damping: 30
};

export const transitionSmooth = {
  ease: [0.16, 1, 0.3, 1], // Custom cubic-bezier
  duration: 0.4
};
```

---

## 7. Accessibility & Testing {#accessibility}

To obtain SOC 2 and ISO 9001 compliance, the design system must satisfy **WCAG 2.1 AA** color contrast and focus indicators:

1.  **Color Contrast**: Core text must exceed 4.5:1 contrast against backdrops (checked via playwright-axe tests).
2.  **Focus States**: All interactive components must have clear focus indicator styles (`focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)] focus-visible:outline-none`).
3.  **ARIA Labels**: Elements lacking visible text (e.g. icon-only buttons) must feature explicit `aria-label` properties.
