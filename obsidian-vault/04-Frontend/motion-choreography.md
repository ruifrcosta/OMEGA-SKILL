# Motion Choreography & Premium Frontend Aesthetics

This document outlines the standard architecture, patterns, and code specs for premium, high-performance UI and scroll-linked animation in OMEGA web applications.

---

## 1. Aesthetic Archetypes (Variance Engine)

To prevent generic outputs, the system dynamically selects and implements one of these three premium visual profiles based on context:

### A. Ethereal Glassmorphism (SaaS / Tech / AI)
- **Background**: OLED Deep Black (`#050505`) with wide, faint, moving radial gradients (mesh mesh-like orbs of glowing indigo, emerald, or violet).
- **Cards**: Translucent dark frames (`bg-black/30 backdrop-blur-2xl border border-white/10 shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)]`).
- **Typography**: Geometric wide sans (e.g., `Geist Sans`, `Plus Jakarta Sans`).

### B. Editorial Luxury (Agency / Portfolio / Editorial)
- **Background**: Warm Ivory Cream (`#FDFBF7`) or Deep Roasted Espresso (`#1A120B`).
- **Texture**: Subtle noise/grain pseudo-element overlay (`pointer-events-none opacity-[0.025] mix-blend-overlay fixed inset-0`).
- **Typography**: Classy Variable Serif headers (e.g., `PP Editorial New`, `Playfair Display`) paired with a highly structured monospace/sans for metadata.

### C. Soft Structuralism (Healthcare / Consumer / Products)
- **Background**: Ice Cold Silver (`#F3F4F6`) or Pure White.
- **Cards**: Elevated floating shapes with extremely diffused, multi-layered ambient drop shadows:
  ```css
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.01), 0 20px 25px -5px rgba(0, 0, 0, 0.03), 0 0 40px rgba(0, 0, 0, 0.02);
  ```
- **Typography**: Heavy, punchy, compact Grotesk headers.

---

## 2. Haptic Micro-Aesthetics: "Double-Bezel" (Doppelrand)

Concentric radius design is mandatory. To prevent corner conflicts, inner and outer curves must be calculated precisely based on padding.

### HTML/Tailwind Pattern
```html
<!-- Outer Shell (Aluminum Frame / Ambient Wrapper) -->
<div class="p-2 bg-black/5 dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-[2rem] shadow-sm">
  <!-- Inner Core (Glass Plate / Active Content) -->
  <div class="p-6 bg-white dark:bg-[#0b0b0b] rounded-[calc(2rem-0.5rem)] shadow-[inset_0_1px_1px_rgba(255,255,255,0.1)]">
    <h3 class="text-xl font-semibold">Machined Hardware Interface</h3>
    <p class="text-sm opacity-60">Concentric corner curves perfectly aligned.</p>
  </div>
</div>
```

---

## 3. High-Performance Motion Specs (GSAP + React)

Standard `linear` and generic `ease-in-out` transitions are completely banned. Enforced fluid curves utilize high-damping spring physics.

### Standard Fluid Bezier
Use this curve for all standard UI state transitions (hover, focus, page sweeps):
```css
transition-all duration-700 ease-[cubic-bezier(0.32,0.72,0,1)]
```

### GSAP ScrollTrigger Standard (React / TypeScript)
When driving animations by scroll, developers must adhere to this unified pattern to prevent memory leaks and coordinate triggers.

```typescript
import React, { useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { useGSAP } from '@gsap/react';

// 1. Mandatory registration
gsap.registerPlugin(ScrollTrigger);

export const StaggeredCascadeGrid = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    if (!containerRef.current) return;

    // 2. Query targets inside the component scope
    const cards = containerRef.current.querySelectorAll('.bezel-card');

    // 3. Drive timeline via ScrollTrigger
    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: containerRef.current,
        start: 'top 80%', // start when container top enters 80% viewport
        end: 'bottom 20%',
        toggleActions: 'play none none reverse', // discrete clean playbacks
      }
    });

    tl.fromTo(cards, 
      { opacity: 0, y: 50, filter: 'blur(8px)' },
      { 
        opacity: 1, 
        y: 0, 
        filter: 'blur(0px)',
        duration: 0.8,
        stagger: 0.15,
        ease: 'power3.out' // clean GSAP curve
      }
    );
  }, { scope: containerRef }); // 4. Scoping enforces strict cleanup on component unmount

  return (
    <div ref={containerRef} className="py-32 grid grid-cols-1 md:grid-cols-3 gap-8 px-8">
      <div className="bezel-card p-1 bg-white/5 border border-white/10 rounded-[1.5rem]">
        <div className="p-8 bg-[#0c0c0c] rounded-[calc(1.5rem-4px)]">Grid Card 1</div>
      </div>
      <div className="bezel-card p-1 bg-white/5 border border-white/10 rounded-[1.5rem]">
        <div className="p-8 bg-[#0c0c0c] rounded-[calc(1.5rem-4px)]">Grid Card 2</div>
      </div>
      <div className="bezel-card p-1 bg-white/5 border border-white/10 rounded-[1.5rem]">
        <div className="p-8 bg-[#0c0c0c] rounded-[calc(1.5rem-4px)]">Grid Card 3</div>
      </div>
    </div>
  );
};
```

---

## 4. Mobile Responsiveness Controls (Universal Collapse)

Complex bento boxes and asymmetrical overlapping grids are highly prone to visual breakage and touch conflicts on touchscreens.

### Enforced Responsive Overrides
1. **Bento Grids**: Above `md` use complex grid structures (`grid-cols-12`, `col-span-8`, `row-span-2`). Below `md` (768px), force a single-column layout (`grid-cols-1`) and reset all spans (`col-span-1`).
2. **Rotations & Margins**: Remove all visual rotations (e.g. `-rotate-3`) and negative-margin overlaps below `md` to avoid tap-target clipping.
3. **Double Viewport jumps**: Never use standard CSS `h-screen` which cuts off on mobile browsers (Safari/Chrome navigation bars). Always use modern dynamic viewport units: `min-h-[100dvh]`.
