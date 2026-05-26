# Frontend Engineering Reference

## Table of Contents
1. [Next.js App Router Architecture](#nextjs)
2. [Server vs Client Components](#components)
3. [Zustand State Management Patterns](#zustand)
4. [Micro-Animations: Framer Motion & GSAP](#animations)
5. [Core Web Vitals & Web Performance Budgets](#performance)

---

## 1. Next.js App Router Architecture {#nextjs}

OMEGA TITAN web applications are built on the Next.js App Router. We enforce layout composition, strict routing patterns, and data-fetching boundaries.

### Folder Structure
```
app/
├── (auth)/                 # Route group for authentication flows
│   ├── login/
│   └── layout.tsx
├── (dashboard)/            # Route group for authenticated workspace
│   ├── workspace/
│   │   ├── page.tsx
│   │   └── loading.tsx
│   └── layout.tsx
├── api/                    # Route handlers (REST / Webhooks)
│   └── webhooks/
│       └── route.ts
├── layout.tsx              # Root HTML composition
└── providers.tsx           # Client context providers
```

---

## 2. Server vs Client Components {#components}

To minimize client-side bundle size, follow a server-first philosophy.

*   **React Server Components (RSC)**: Default for all pages, layouts, and static elements. Fetch data directly from databases/external APIs using async/await. Keep database credentials completely server-bound.
*   **Client Components (`'use client'`)**: Use strictly for interactive leaves (forms, buttons, charts, real-time web socket interfaces).

### RSC Composition Example
```tsx
// app/workspace/page.tsx (RSC)
import { Suspense } from 'react';
import { fetchActiveProjects } from '@/lib/db';
import { ProjectCard } from '@/components/project-card';
import { InteractiveSearch } from '@/components/interactive-search'; // 'use client'

export default async function WorkspacePage() {
  const initialProjects = await fetchActiveProjects();

  return (
    <div class="space-y-6">
      <h1 class="text-xl font-bold tracking-tight">Active Projects</h1>
      <InteractiveSearch />
      <Suspense fallback={<p class="text-sm text-neutral-500">Loading pipeline...</p>}>
        <ProjectList projects={initialProjects} />
      </Suspense>
    </div>
  );
}

async function ProjectList({ projects }: { projects: any[] }) {
  return (
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      {projects.map((project) => (
        <ProjectCard key={project.id} data={project} />
      ))}
    </div>
  );
}
```

---

## 3. Zustand State Management Patterns {#zustand}

For global client-side state, we utilize Zustand. Store patterns must separate state, actions, and selectors to prevent wasteful rendering cycles.

```typescript
// store/use-workspace-store.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface WorkspaceState {
  activeId: string | null;
  sidebarOpen: boolean;
  setActiveWorkspace: (id: string) => void;
  toggleSidebar: () => void;
}

export const useWorkspaceStore = create<WorkspaceState>()(
  devtools(
    persist(
      (set) => ({
        activeId: null,
        sidebarOpen: true,
        setActiveWorkspace: (id) => set({ activeId: id }, false, 'setActiveWorkspace'),
        toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen }), false, 'toggleSidebar'),
      }),
      { name: 'titan-workspace-storage' }
    )
  )
);
```

---

## 4. Micro-Animations: Framer Motion & GSAP {#animations}

Use GSAP for complex timelines, parallax, or high-performance canvas triggers. Use Framer Motion for UI state transitions, layouts, and page transitions.

### Framer Motion Layout Transition
```tsx
'use client';

import { motion, AnimatePresence } from 'framer-motion';

export function NavigationTab({ active }: { active: boolean }) {
  return (
    <div class="relative cursor-pointer px-4 py-2 text-sm font-medium">
      <span class="relative z-10">Workspace</span>
      {active && (
        <motion.div
          layoutId="activeTabIndicator"
          className="absolute inset-0 rounded-md bg-neutral-100 dark:bg-neutral-800"
          transition={{ type: 'spring', stiffness: 380, damping: 30 }}
        />
      )}
    </div>
  );
}
```

---

## 5. Core Web Vitals & Web Performance Budgets {#performance}

All pages must pass the strict Core Web Vitals budget verified during build-time checking:

*   **LCP (Largest Contentful Paint)**: Under **1.8s**. Mandatory image optimization using `next/image` with responsive `sizes`.
*   **INP (Interaction to Next Paint)**: Under **150ms**. Offload blocking heavy JS operations to Web Workers or schedule them using `requestIdleCallback`.
*   **CLS (Cumulative Layout Shift)**: **0.00**. Never insert dynamic blocks or banners above already rendered content without pre-allocating aspect-ratio bounds.
*   **Dynamic Bundle Checking**: Builds must automatically fail if the initial client bundle of any page exceeds **85kB**.

---

## Integrated Taste Engine Integration

For ALL frontend tasks, read `references/20-taste-engine.md` FIRST.

### Minimum activation sequence for any UI task:

```
1. Read 20-taste-engine.md §0 → declare Design Read
2. Set Three Dials from §1 (VARIANCE / MOTION / DENSITY)
3. Apply Brand Morphing Table §6 → fonts + accent
4. Check §2 for HARDCODED BANS
5. Use liquid-glass from §3 only if premium context
6. Apply animation rules from §4 + §5
7. Run §9 Pre-Flight Checklist before output
```

### Canonical video hero (from UI prompts corpus)

```tsx
<div className="relative min-h-[100dvh] w-full overflow-hidden">
  <video autoPlay loop muted playsInline
    className="absolute inset-0 w-full h-full object-cover z-0"
    src="VIDEO_URL" />
  <div className="relative z-10 flex flex-col min-h-[100dvh]">
    {/* content */}
  </div>
</div>
```

### React + GSAP mouse parallax (from Wanderful/MicroVisuals patterns)

```tsx
useEffect(() => {
  let rAF: number;
  let currentX = 0, currentY = 0, targetX = 0, targetY = 0;
  const STRENGTH = 20;

  const onMouse = (e: MouseEvent) => {
    const cx = window.innerWidth / 2, cy = window.innerHeight / 2;
    targetX = ((e.clientX - cx) / cx) * STRENGTH;
    targetY = ((e.clientY - cy) / cy) * STRENGTH;
  };

  const loop = () => {
    currentX += (targetX - currentX) * 0.06;
    currentY += (targetY - currentY) * 0.06;
    if (videoBgRef.current) gsap.set(videoBgRef.current, { x: currentX, y: currentY });
    rAF = requestAnimationFrame(loop);
  };

  window.addEventListener('mousemove', onMouse);
  rAF = requestAnimationFrame(loop);
  return () => { window.removeEventListener('mousemove', onMouse); cancelAnimationFrame(rAF); };
}, []);
```
