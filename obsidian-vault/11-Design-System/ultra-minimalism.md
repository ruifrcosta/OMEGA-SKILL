# OMEGA Ultra-Minimalist & Dynamic Design System

This document outlines the OMEGA standards for ultra-minimalist mobile and web user interfaces, incorporating visual silence, spatial rhythm, dynamic project-specific themes, and user retention engines.

---

## 1. The Principle of Visual Silence

OMEGA designs convey visual calm and high-end institutional trust by stripping away all non-essential visual elements.

### A. The "No Cards" Absolute Rule
**There are no cards.** Content must sit directly on the background surface. 
- **Prohibited**: Elevated containers, visible filled panels, physical drop-shadows, glow effects, or solid grey background grids.
- **Enforced Separation**: Grouping and separation must be achieved strictly via:
  - Whitespace rhythm (allowing layouts to breathe heavily).
  - Explicit typography weight and size hierarchy.
  - Near-invisible dividers when absolutely necessary: `1px solid rgba(0,0,0,0.04)` in Light Mode, or `rgba(255,255,255,0.06)` in Dark Mode.

### B. Micro-Interaction Polish
- **Active Press State**: Every button, input field, and list item must verify it heard the user by providing immediate tactile feedback:
  ```css
  active:scale-[0.97] transition-transform duration-150 ease-out
  ```
- **GPU-Safe Animation**: Never animate layout-triggering properties (`width`, `height`, `top`, `left`). Animate exclusively via `transform` (scale, translate) and `opacity`.
- **Entrance Scaling**: Never animate elements from `scale(0)` or raw `opacity(0)`. Entrance slide-ins must animate from `scale(0.95)` and `opacity: 0` to create organic physical depth:
  ```css
  transform: scale(0.95); opacity: 0;
  ```

---

## 2. Dynamic Identity Matrices (Project-Based Theme Morphing)

Colors and fonts are **never** static. OMEGA user interfaces must dynamically morph their typography and semantic color tokens (`--bg`, `--fg`, `--accent`, `--muted`) based on the project's target domain:

| App Category | Primary Font Pairing (Heading / Body) | Light Mode Palette (`--bg` / `--fg` / `--accent`) | Dark Mode Palette (`--bg` / `--fg` / `--accent`) | Visual Tone & Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Healthcare / Wellness** | Figtree / DM Sans | `#FFFFFF` / `#0F172A` / `#059669` (Emerald) | `#0A0F14` / `#F1F5F9` / `#34D399` | Calm, clinical precision, high legibility. |
| **Finance / Fintech** | Söhne or Sora / IBM Plex Sans | `#FAFAF9` / `#111827` / `#1D4ED8` (Royal Blue) | `#0D1117` / `#F9FAFB` / `#60A5FA` | Structured authority, technical trust. |
| **Productivity / Tools** | Geist Sans / Geist Mono | `#FFFFFF` / `#1A1A1A` / `#7C3AED` (Violet) | `#111111` / `#F5F5F5` / `#A78BFA` | Focus, modern efficiency, no-nonsense utility. |
| **E-Commerce / Fashion** | Playfair Display / Nunito Sans | `#FFFFFF` / `#0F0F0F` / `#0F0F0F` (Pitch Black) | `#0A0A0A` / `#FAFAFA` / `#FBBF24` | Premium editorial, high-end sensory impact. |
| **Fitness / Sports** | Space Grotesk / DM Sans | `#F8FAFC` / `#0F172A` / `#16A34A` (Vitality Green) | `#060D14` / `#F1F5F9` / `#4ADE80` | Dynamic kinetic energy, controlled readability. |
| **Education / Learning** | Lora / Source Serif 4 | `#FFFFFF` / `#1E293B` / `#2563EB` (Knowledge Blue) | `#0F172A` / `#F1F5F9` / `#60A5FA` | Warm editorial, readable for prolonged study. |
| **Social / Community** | Plus Jakarta Sans / DM Sans | `#FFFFFF` / `#111827` / `#7C3AED` (Violet) | `#0D0D0D` / `#F9FAFB` / `#A78BFA` | Approachable, conversational, high-end warmth. |

---

## 3. The Self-Interrogation Protocol (UX Quality Gate)

Prior to compiling any screen or flow, the system must silently execute this four-phase audit:

### Phase 1: Context & Navigation Flow
- What is the single job of this screen? (If the answer contains "and", it must be split into two screens).
- What does the user feel when they arrive? (Anxious, curious, in flow). What should they feel leaving?
- Is the navigation path forward (`enter from right`) and backward (`exit to right`) spatially coherent?

### Phase 2: Addiction & Retention Mechanics
- What is the user's reason to return tomorrow? (Streak maintenance, progress milestones, content freshness).
- Is there an investment hook? (Has the user put in data, customized a theme, or unlocked XP?).

### Phase 3: Emotional Feedback
- Does the loading state build anticipation? (Enforce customized Skeleton layouts matching actual content, never generic spinners).
- Does the empty state feel like an opportunity or a failure? (Must include an inviting headline + one clear CTA).

### Phase 4: Micro-Polish
- Are all touch targets at minimum `44x44pt` on mobile to prevent fat-finger errors?
- Do interactive buttons scale on tap?

---

## 4. The Addiction Loop Engine
Every product designed by OMEGA must integrate a high-retention loop matching its category:

```
Trigger (Notification / Streak alert) 
   ↓
Action (One-thumb effortless tap/swipe)
   ↓
Variable Reward (Achievement unlock / Content discovery)
   ↓
Investment (Saved data / Streak maintenance)
```
- **Productivity**: Streaks + completion satisfaction + inbox zero hooks.
- **Education**: XP/levels + streaks + social comparison.
- **Fintech**: Portfolio growth graphs + goals proximity thresholds.
