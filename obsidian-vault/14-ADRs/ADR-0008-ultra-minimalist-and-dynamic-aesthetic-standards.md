# ADR-0008: Ultra-Minimalist Design Systems & Dynamic Aesthetic Standards

## Status
Accepted

## Deciders
- OMEGA Architecture Office
- UX / Design System Agent
- Product Agent

## Context
Standard UI design systems are often static, rigid, and cluttered — relying heavily on elevated boxes ("cards"), dark drop-shadows, generic fonts, and the same color palettes regardless of project domains. This leads to high cognitive load, visual anxiety, and a generic, unrefined product experience.

To establish OMEGA as a premium, highly addictive, and visually silent AI-native engineering factory, we must formalize our **Ultra-Minimalist Mobile & Web UI System** and establish a **Dynamic Aesthetic Mapping Framework**, ensuring that typography, scale, and color morph natively based on each project's distinct domain.

## Decision
We enforce the following absolute design rules across all OMEGA frontend and mobile projects:

### 1. The Core Philosophy of Visual Silence
- **The "No Cards" Rule**: Content must sit directly on the clean surface background. Elevated panels, visible card containers, physical drop-shadows, and heavy borders are strictly prohibited.
- **Rhythm over Boundaries**: Visual separation must be achieved exclusively through whitespace gaps (following a strict 4/8dp grid), typography weight hierarchy, near-invisible borders (`1px solid rgba(0,0,0,0.04)`), and alignment.
- **Inter-active states**: Every interactive component must provide instant physical tactile response on touch/press (enforcing a standard `transform: scale(0.97)` active state).

### 2. Dynamic Visual Identity Mapping
Colors and typographies must **NEVER** be static. OMEGA UI systems must dynamically adapt the semantic system tokens (`--bg`, `--fg`, `--accent`, `--muted`) and font pairings according to the project's target category:

- **Healthcare / Wellness**: Emerald green (`#059669`) for calm/precision, paired with clean, clinical typography (Inter / Figtree / DM Sans).
- **Finance / Fintech**: Trustworthy indigo-blue (`#1d4ed8`) for authority, paired with structured, institutional typography (Söhne / IBM Plex Sans / Sora).
- **Productivity / Tools**: Violet (`#7c3aed`) for modern focus, paired with Geist or Plus Jakarta Sans.
- **E-Commerce / Fashion**: High-contrast premium black (`#0f0f0f`), paired with Editorial Serifs (Playfair / PP Editorial) or Plus Jakarta Sans.
- **Fitness / Sports Tracking**: Vibrant green or warning red, paired with Space Grotesk for high energy.
- **Travel / Food**: Amber Terracotta (`#c2410c`) for sensory warmth, paired with Cormorant Garamond.

### 3. The Retention & Addiction Engine
- Every user interface flow designed under OMEGA must explicitly define its **Addiction Hook** and **Core Loop** (Trigger -> Action -> Variable Reward -> Investment) appropriate to the app category (e.g. streaks and completion satisfaction for productivity; XP/levels and streaks for education).
- Screens must be designed sequentially to automatically pull the user forward, minimizing user steps to zero.

## Consequences
### Positive
- **Visual Calm**: Restructuring screens to eliminate noisy containers reduces user cognitive friction.
- **Bespoke Domain Fitting**: Automatically mapping color/font pairs to the app's target category makes every product feel tailored and professionally designed.
- **Compounding Quality**: Polish passes on micro-interactions (`scale(0.97)` on press, no transition: all) combine to create highly tactile, satisfying apps.

### Negative
- **Highly Custom Code**: Moving away from standard tailwind UI templates means OMEGA must code component interfaces bespoke from core primitives.
