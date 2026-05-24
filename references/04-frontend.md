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
# Screen Patterns Library

Common mobile screen archetypes with layout structure and UX rules.

---

## 1. Home / Feed Screen

**Goal:** Surface the most relevant content immediately.

**Layout:**
```
[Status bar safe area]
[Greeting / date — LG top padding]
[Primary CTA or summary card — if needed, cardless]
[Section label — muted, SM]
[List of items — no cards, editorial style]
[Bottom nav]
```

**Rules:**
- Greeting should feel personal, not generic
- First visible item is the highest priority
- Empty state = illustration + single action button
- Loading = skeleton lines (not spinner blocking content)

---

## 2. Detail / Profile Screen

**Goal:** Show complete information about one entity.

**Layout:**
```
[Back navigation — top left]
[Hero section — name, status, key info]
[Section 1 label + content]
[Thin separator]
[Section 2 label + content]
[Thin separator]
[...]
[Bottom CTA — sticky or inline]
```

**Rules:**
- No tabs inside a detail screen unless content volume demands it
- Sticky CTA only if action is frequent; otherwise inline at bottom
- Data presented in two-column key/value when space allows
- Labels muted, values foreground

---

## 3. List / Index Screen

**Goal:** Browse and find items.

**Layout:**
```
[Header with title + optional search icon]
[Filter row — horizontal scroll chips, if needed]
[List — full width, no cards]
[Each item: primary label / secondary info / right metadata]
[Thin separator between items]
[Bottom nav]
```

**Rules:**
- Items never in cards — content lives on the surface
- Separator: `1px solid rgba(0,0,0,0.04)`, padding 16px vertical
- Empty state: clear message + primary action
- Loading: skeleton rows matching real item structure

---

## 4. Form / Input Screen

**Goal:** Collect information from the user.

**Layout:**
```
[Back + title header]
[Section label — muted]
[Input field — borderless or bottom-border only]
[Helper text — small, muted]
[Input field]
[...]
[Primary CTA — full width, bottom of scroll or sticky]
```

**Rules:**
- Group related fields — never dump all fields at once
- Show one section at a time for long forms (progressive disclosure)
- Error below the specific field, not just at top
- Auto-advance to next field where logical
- CTA disabled until minimum required fields filled

---

## 5. Onboarding Flow

**Goal:** Orient the user and collect minimal required info.

**Layout per step:**
```
[Step indicator — dots or "1 of 4" — top or bottom]
[Large headline — 28–32px, centered or left]
[Supporting text — muted, 16px]
[Illustration or icon — simple, if needed]
[Primary CTA]
[Skip / secondary action — muted, smaller]
```

**Rules:**
- Maximum 4–5 steps. Fewer is always better.
- Each step has one question or one piece of info
- Never collect data that can be deferred
- Progress is always visible
- Back is always available (except step 1)

---

## 6. Settings Screen

**Goal:** Let users configure their experience.

**Layout:**
```
[Header — "Settings"]
[Section label — muted, uppercase XS]
[Setting row: icon (optional) / label / control (toggle, chevron, value)]
[Separator between rows]
[Section label]
[Setting rows]
[...]
[Destructive actions — at bottom, red/muted]
```

**Rules:**
- Destructive actions (delete account, log out) at the very bottom
- Visual separation between destructive and normal settings
- Toggles for binary settings, chevron for nested settings
- Never use switches for navigation — only for on/off states

---

## 7. Empty State

**Goal:** Guide the user when there is nothing to show.

**Structure:**
```
[Icon — 48px, muted]
[Title — 18px, foreground, centered]
[Subtitle — 14px, muted, centered, max 2 lines]
[Primary CTA button]
```

**Rules:**
- Never leave a blank screen
- Icon should relate to the content type (not generic "no results")
- CTA solves the emptiness directly ("Add your first item", "Connect your account")
- Tone: calm and helpful, not apologetic

---

## 8. Loading / Skeleton State

**Goal:** Set expectations while content loads.

**Rules:**
- Use skeleton placeholders that match the shape of real content
- Animate with shimmer (left-to-right gradient sweep)
- Never show empty containers or axis frames before data
- Show skeleton immediately; never wait 500ms+ to show something
- For > 3 seconds, add contextual message ("This is taking longer than usual...")

**Skeleton structure (list):**
```
[Line 60% width — foreground placeholder]
[Line 40% width — muted placeholder]
[Separator]
[repeat × 5]
```

---

## 9. Error State

**Goal:** Explain what went wrong and how to recover.

**Structure:**
```
[Icon — 40px, muted or error-colored]
[Title — explains the problem simply]
[Subtitle — actionable explanation, no jargon]
[Retry / recovery CTA]
[Secondary: contact support or go back]
```

**Rules:**
- Never say "Something went wrong" without a cause
- Always include a recovery action
- Timeout errors: show retry button prominently
- Network errors: detect and show offline-specific message

---

## 10. Confirmation / Success State

**Goal:** Confirm that an action succeeded.

**Structure (inline toast):**
```
[Small icon — checkmark, success green]
[Short message — "Saved", "Done", "Sent"]
[Auto-dismiss in 3s]
```

**Structure (full screen for critical actions):**
```
[Success icon — 48px]
[Title — "All done" / "Confirmed"]
[Supporting detail]
[Primary CTA — "Continue" or "Go home"]
```

**Rules:**
- Toasts: auto-dismiss 3–5s, do not steal focus
- Full-screen success: only for irreversible or high-stakes actions (payment, deletion)
- Never animate excessively on success — a subtle fade-in is enough
- Always give users a clear path forward
# Font Recommendations by App Category

## Healthcare / Medical / Wellness
**Heading:** Inter, SF Pro Display (iOS), or Figtree  
**Body:** Inter, DM Sans  
**Rationale:** Clinical precision, high legibility, neutral authority

## Finance / Fintech / Banking
**Heading:** Söhne, IBM Plex Sans, or Sora  
**Body:** IBM Plex Sans, DM Sans  
**Rationale:** Technical trust, structured, modern institutional

## Productivity / Task Management / Notes
**Heading:** Geist, Inter, or Plus Jakarta Sans  
**Body:** Inter, Geist  
**Rationale:** Efficiency-first, clear hierarchy, no decoration

## E-Commerce / Retail / Fashion
**Heading:** Playfair Display (luxury) or Plus Jakarta Sans (modern)  
**Body:** DM Sans, Nunito Sans  
**Rationale:** Premium feel for luxury; approachable for mass market

## Fitness / Sports / Health Tracking
**Heading:** Space Grotesk, Sora  
**Body:** DM Sans, Nunito  
**Rationale:** Dynamic but controlled, energetic but readable

## Education / Learning / Courses
**Heading:** Lora (editorial) or Nunito (friendly)  
**Body:** Source Serif 4, Nunito  
**Rationale:** Readable for long sessions, warm but structured

## Social / Community / Messaging
**Heading:** Plus Jakarta Sans, Nunito  
**Body:** DM Sans, Nunito  
**Rationale:** Approachable, human, conversational

## Travel / Hospitality / Food
**Heading:** Playfair Display, Cormorant Garamond  
**Body:** DM Sans, Nunito Sans  
**Rationale:** Evocative, premium, sensory

## Utilities / Tools / Productivity Apps
**Heading:** Geist Mono (code tools), Inter (general)  
**Body:** Inter, DM Sans  
**Rationale:** Functional, no-nonsense, precision

## Kids / Casual / Entertainment
**Heading:** Nunito (rounded), Fredoka  
**Body:** Nunito, Poppins  
**Rationale:** Playful but still legible

---

## Universal Rules

- Minimum body: **16px** on mobile (prevents iOS auto-zoom)
- Line-height body: **1.5–1.65**
- Line-height headings: **1.1–1.25**
- Font scale: `12 / 14 / 16 / 18 / 24 / 32 / 40`
- Weights: 400 (body), 500 (label/medium), 600 (heading), 700 (display — use sparingly)
- Letter-spacing: `-0.02em to -0.03em` for headings; **never tighten body text**
- Use tabular numbers (`font-variant-numeric: tabular-nums`) for data, prices, timers
# Color Palettes by App Category

Each palette includes semantic tokens. Adapt to dark mode by using desaturated lighter tonal variants — never invert.

---

## Healthcare / Medical / Wellness

**Light Mode**
```
--bg:      #ffffff
--fg:      #0f172a
--muted:   #64748b
--accent:  #059669   (emerald — calm, clinical)
--border:  rgba(15,23,42,0.05)
--error:   #dc2626
--success: #16a34a
```

**Dark Mode**
```
--bg:      #0a0f14
--fg:      #f1f5f9
--muted:   #94a3b8
--accent:  #34d399
--border:  rgba(255,255,255,0.06)
```

---

## Finance / Fintech / Banking

**Light Mode**
```
--bg:      #fafaf9
--fg:      #111827
--muted:   #6b7280
--accent:  #1d4ed8   (blue — authority, trust)
--border:  rgba(17,24,39,0.05)
--error:   #dc2626
--success: #059669
```

**Dark Mode**
```
--bg:      #0d1117
--fg:      #f9fafb
--muted:   #9ca3af
--accent:  #60a5fa
--border:  rgba(255,255,255,0.06)
```

---

## Productivity / Tools / Utilities

**Light Mode**
```
--bg:      #ffffff
--fg:      #1a1a1a
--muted:   #737373
--accent:  #7c3aed   (violet — focus, modern)
--border:  rgba(0,0,0,0.05)
--error:   #ef4444
--success: #22c55e
```

**Dark Mode**
```
--bg:      #111111
--fg:      #f5f5f5
--muted:   #a3a3a3
--accent:  #a78bfa
--border:  rgba(255,255,255,0.06)
```

---

## E-Commerce / Retail / Fashion

**Light — Modern**
```
--bg:      #ffffff
--fg:      #0f0f0f
--muted:   #737373
--accent:  #0f0f0f   (near-black — editorial, premium)
--border:  rgba(0,0,0,0.06)
--error:   #dc2626
--success: #16a34a
```

**Light — Vibrant**
```
--bg:      #fafafa
--fg:      #111827
--muted:   #6b7280
--accent:  #f97316   (orange — energy, conversion)
--border:  rgba(0,0,0,0.05)
```

**Dark Mode**
```
--bg:      #0a0a0a
--fg:      #fafafa
--muted:   #a3a3a3
--accent:  #fbbf24
--border:  rgba(255,255,255,0.06)
```

---

## Fitness / Sports / Health Tracking

**Light Mode**
```
--bg:      #f8fafc
--fg:      #0f172a
--muted:   #64748b
--accent:  #16a34a   (green — vitality) or #dc2626 (energy)
--border:  rgba(15,23,42,0.04)
--error:   #ef4444
--success: #22c55e
```

**Dark Mode**
```
--bg:      #060d14
--fg:      #f1f5f9
--muted:   #94a3b8
--accent:  #4ade80
--border:  rgba(255,255,255,0.06)
```

---

## Travel / Food / Hospitality

**Light Mode**
```
--bg:      #fffbf5
--fg:      #1c1917
--muted:   #78716c
--accent:  #c2410c   (amber/terracotta — warmth)
--border:  rgba(28,25,23,0.05)
--error:   #dc2626
--success: #16a34a
```

**Dark Mode**
```
--bg:      #0c0a09
--fg:      #faf5f0
--muted:   #a8a29e
--accent:  #fb923c
--border:  rgba(255,255,255,0.06)
```

---

## Education / Learning

**Light Mode**
```
--bg:      #ffffff
--fg:      #1e293b
--muted:   #64748b
--accent:  #2563eb   (blue — knowledge, authority)
--border:  rgba(30,41,59,0.05)
--error:   #dc2626
--success: #16a34a
```

**Dark Mode**
```
--bg:      #0f172a
--fg:      #f1f5f9
--muted:   #94a3b8
--accent:  #60a5fa
--border:  rgba(255,255,255,0.06)
```

---

## Social / Community

**Light Mode**
```
--bg:      #ffffff
--fg:      #111827
--muted:   #6b7280
--accent:  #7c3aed   (violet — creative, community)
--border:  rgba(0,0,0,0.05)
--error:   #ef4444
--success: #22c55e
```

**Dark Mode**
```
--bg:      #0d0d0d
--fg:      #f9fafb
--muted:   #9ca3af
--accent:  #a78bfa
--border:  rgba(255,255,255,0.06)
```

---

## Universal Color Rules

1. **Never use raw hex in components** — always reference semantic tokens
2. **Test contrast separately** for light and dark mode
3. **Primary text:** ≥ 4.5:1 contrast ratio
4. **Secondary text / icons:** ≥ 3:1
5. **Error and success colors** must always pair with an icon or label — never color alone
6. **Dark mode accent** = lighter, desaturated variant of light mode accent (never inverted)
7. **Border opacity range:** `0.04–0.08` — subtle enough to be invisible at first glance
# Addiction Patterns by App Type

The best apps are not addictive by accident. These patterns are used deliberately by the highest-retention products in the world. Apply them at the right places in the UX flow.

---

## The Core Loop

Every great app has a core loop. Design every screen as part of this loop, never in isolation.

```
Trigger → Action → Variable Reward → Investment → (repeat)
```

If you can't identify which part of the loop a screen belongs to, ask: "why would the user come back to this screen tomorrow?"

---

## Universal Patterns (apply to any app type)

### Progress Bars & Completion
Show partial progress toward a goal. The closer users are to completion, the more compelled they feel to finish.

- Profile: "Your profile is 60% complete"
- Course: "3 of 7 lessons done"
- Onboarding: step indicators
- **Avoid:** 100% completion with no next goal — create the next one immediately

### Streaks
Daily use creates habit. Streaks create loss aversion.

- Show streak count prominently on the home screen
- Send a "don't lose your streak" notification at a time when the user is likely idle
- Allow a "freeze" mechanic (one missed day) to reduce frustration
- **Design:** Show the streak with a small flame or dot pattern, never as a number alone

### Milestones & Badges
Celebrate non-obvious achievements to create surprise.

- First action completed
- 7-day streak
- 100th item in a list
- Top 10% of users
- **Design:** Celebration should be subtle but satisfying — a haptic + small animation, not a full-screen takeover

### Variable Reward (the most powerful mechanism)
Predictable rewards bore. Unpredictable rewards engage.

- Discovery feeds (content the user didn't know they'd see)
- "New this week" sections
- Random positive feedback messages (not always "Good job!")
- Personalisation that improves over time ("This feels like it's learning me")

### Social Proof & Comparison
Humans calibrate behaviour against others.

- "42 people completed this today"
- "You're in the top 15% of users"
- "3 friends are using this"
- Activity feeds showing what peers are doing
- **Design:** Show social data next to the relevant action, not on a separate social tab

### Content Freshness
Give users a reason to open the app again.

- "5 new items since your last visit"
- Badge on the app icon (use sparingly — only when content is truly new)
- "Trending now" or "This week's highlights"
- **Design:** Never show "0 new items" — instead, hide the freshness indicator entirely

---

## Patterns by App Category

### Productivity Apps (task managers, note apps, calendars)

**Primary hook:** Completion satisfaction + inbox zero moments

- **Swipe to complete** — the satisfying arc of a task disappearing
- **Overdue count** — creates mild urgency without anxiety
- **Focus mode** — limits distractions for a set time, feels like an achievement to complete
- **Weekly review** — "You completed 23 tasks this week. That's your best week."
- **Tomorrow view** — always show what's coming, never let the slate feel empty

**Design note:** The act of completion must feel physically satisfying. The animation of a task completing should have weight — not just a checkmark, but a brief visual celebration.

### Social Apps

**Primary hook:** Social validation + fear of missing out

- **Notification layer** — someone liked, commented, replied (but only high-value moments)
- **Stories / ephemeral content** — creates urgency before content disappears
- **Unread count** — always slightly elevated to maintain curiosity
- **Active friends indicator** — "3 friends are online now"
- **Comment previews** — show first few words, require tap to read the rest

**Design note:** The feed must always end with a "discover more" prompt, never with a blank end.

### Health & Fitness Apps

**Primary hook:** Progress visualisation + personal records

- **Progress charts** — even small improvements feel significant when visualised
- **Personal records** — "Your best pace ever" creates pride
- **Body/habit calendar** — visual grid of consistency, like GitHub contributions
- **Weekly comparison** — "You ran 12km more than last week"
- **Rest day acknowledgement** — even rest days should feel active ("Recovery day — you're doing great")

**Design note:** Progress must be visible from the first day, even when actual results are minimal. Small wins must be celebrated visibly.

### Finance Apps

**Primary hook:** Portfolio/savings growth + milestone proximity

- **Net worth tracker** — even small increases feel good
- **Goal proximity** — "You're 73% to your emergency fund goal"
- **Spending insight** — "You spent 20% less on food this month"
- **Round-up moments** — micro-saving feels effortless
- **Safe-to-spend** — one clear number removes anxiety

**Design note:** The primary screen must always show forward movement, never just a static balance. Every number should have a delta.

### Education Apps

**Primary hook:** XP + levels + streaks + social comparison

- **XP after every action** — micro-reward for completing a lesson, a quiz, a review
- **Level-up animation** — full moment of celebration on level advancement
- **Leaderboard** — weekly, resetting, so users always have a chance
- **Mastery paths** — show what mastery looks like before the user reaches it
- **Spaced repetition prompts** — "You have 12 words ready for review"

**Design note:** The app should feel like a game in its structure but never in its aesthetics. Progress must be visible and never feel arbitrary.

### E-Commerce Apps

**Primary hook:** Wishlist + scarcity + price drops

- **Wishlist price drop alerts** — high-intent, welcome notifications
- **Stock scarcity** — "Only 3 left" (only when true)
- **Recently viewed** — easy re-access without search
- **Personalised "because you liked X"** — discovery that feels curated
- **Flash sale countdowns** — time-limited deals create urgency

**Design note:** Never show an empty wishlist without a personalised recommendation to fill it. The wishlist is a retention anchor.

### Content & Media Apps

**Primary hook:** Personalisation + "continue where you left off" + playlists/queues

- **Continue watching/reading/listening** — the most powerful re-engagement
- **Up next** — auto-queue removes friction to continue
- **Personalisation feedback loop** — every action improves recommendations
- **Download for offline** — increases commitment and reduces churn
- **Watch/read time stats** — "You've read 3 books this month"

**Design note:** The first item visible on the home screen should always be something the user will want to tap. This is more important than any other design decision on the home screen.

---

## Anti-Patterns (never use these)

| Anti-pattern | Why it fails |
|---|---|
| Notifications for non-events | Trains users to ignore all notifications |
| Fake scarcity ("Only 2 left!") when it's not true | Destroys trust permanently |
| Dark patterns in unsubscribe flows | Creates resentment, increases churn |
| Forced social sharing for rewards | Feels manipulative, users resent it |
| Asking for rating too early | Gets low ratings + users feel interrupted |
| Gamification without meaning | XP that means nothing creates zero engagement |
| Progress bars that never reach 100% | Feels like a trick, destroys trust |
| Onboarding longer than 4 steps | Users abandon before the core experience |

---

## The Timing of Retention Moments

The right pattern at the wrong time fails.

| Moment | Right action |
|---|---|
| First launch (session 1) | Deliver immediate value. No paywall. No signup until value is clear. |
| End of first session | Show progress made. Preview what comes next. |
| Day 2 notification | Reference the specific thing they did on day 1. |
| After first positive outcome | This is the right moment to ask for a rating. |
| After 7 days | Show a "week in review" to make progress visible. |
| After inactivity (3+ days) | Reference what they'll lose or miss, not just "come back". |
| At streak risk | Send notification within the user's historically active window. |