# MINIMALIST UI — Editorial & Document-Style Interface Protocol

Distilled from `Leonxlnx/taste-skill` (minimalist-skill). Premium Utilitarian Minimalism directive for "document-style" web interfaces — top-tier workspace platforms (Notion, Linear, Craft).

---

## PROTOCOL IDENTITY

**Name:** Premium Utilitarian Minimalism & Editorial UI
**Target aesthetic:** Document-style workspace platforms. High-contrast warm monochrome, bespoke typographic hierarchies, meticulous macro-whitespace, bento-grid layouts, ultra-flat components with deliberate muted pastel accents.

---

## ABSOLUTE NEGATIVE CONSTRAINTS (Banned)

- **NO** `Inter`, `Roboto`, or `Open Sans` typefaces
- **NO** generic thin-line icon libraries: Lucide, Feather, standard Heroicons
- **NO** heavy drop shadows: `shadow-md`, `shadow-lg`, `shadow-xl`. Shadows must be ultra-diffuse, low opacity (< 0.05)
- **NO** primary colored backgrounds for large elements or sections (no bright blue, green, red hero sections)
- **NO** gradients, neon colors, or 3D glassmorphism (beyond subtle navbar blurs)
- **NO** `rounded-full` (pill shapes) for large containers, cards, or primary buttons
- **NO** emojis anywhere — replace with proper icons or clean SVG primitives
- **NO** generic placeholder names: "John Doe", "Acme Corp", "Lorem Ipsum"
- **NO** AI copywriting clichés: "Elevate", "Seamless", "Unleash", "Next-Gen", "Game-changer", "Delve"

---

## TYPOGRAPHIC ARCHITECTURE

The interface relies on extreme typographic contrast and premium font selection for an editorial feel.

| Role | Font Target | Specifications |
|:---|:---|:---|
| **Primary Sans-Serif** (Body, UI, Buttons) | `SF Pro Display`, `Geist Sans`, `Helvetica Neue`, `Switzer` | Clean, geometric, system-native character |
| **Editorial Serif** (Hero Headings, Quotes) | `Lyon Text`, `Newsreader`, `Playfair Display`, `Instrument Serif` | `letter-spacing: -0.02em` to `-0.04em`, `line-height: 1.1` |
| **Monospace** (Code, Keystrokes, Metadata) | `Geist Mono`, `SF Mono`, `JetBrains Mono` | For all technical content and meta elements |

**Text Colors:**
- Body text: Never absolute black (`#000000`). Use off-black/charcoal: `#111111` or `#2F3437`
- Line height: Generous `1.6` for body legibility
- Secondary text: Muted gray `#787774`

---

## COLOR PALETTE (Warm Monochrome + Spot Pastels)

Color is a scarce resource — used only for semantic meaning or subtle accents.

| Role | Value |
|:---|:---|
| **Canvas / Background** | Pure White `#FFFFFF` or Warm Bone `#F7F6F3` / `#FBFBFA` |
| **Primary Surface (Cards)** | `#FFFFFF` or `#F9F9F8` |
| **Structural Borders / Dividers** | Ultra-light gray `#EAEAEA` or `rgba(0,0,0,0.06)` |

**Muted Pastel Accents (for tags, inline code, subtle icon backgrounds ONLY):**
| Pastel | Background | Text |
|:---|:---|:---|
| Pale Red | `#FDEBEC` | `#9F2F2D` |
| Pale Blue | `#E1F3FE` | `#1F6C9F` |
| Pale Green | `#EDF3EC` | `#346538` |
| Pale Yellow | `#FBF3DB` | `#956400` |

---

## COMPONENT SPECIFICATIONS

### Bento Box Feature Grids
- Asymmetrical CSS Grid layouts
- Card border: exactly `border: 1px solid #EAEAEA`
- Border-radius: `8px` or `12px` maximum (crisp, not rounded-full)
- Internal padding: generous `24px` to `40px`

### Primary CTA Buttons
- Solid background: `#111111`, text: `#FFFFFF`
- Border-radius: `4px` to `6px`. No box-shadow
- Hover: subtle shift to `#333333` or `transform: scale(0.98)`

### Tags & Status Badges
- Pill-shaped (`border-radius: 9999px`), `text-xs`, uppercase `letter-spacing: 0.05em`
- Background: exclusively muted pastels above

### Accordions (FAQ)
- Strip all container boxes
- Separate items with `border-bottom: 1px solid #EAEAEA` ONLY
- Toggle: clean sharp `+` and `-` icons

### Keystroke Micro-UIs
- Render shortcuts as physical `<kbd>` tags:
  ```css
  border: 1px solid #EAEAEA;
  border-radius: 4px;
  background: #F7F6F3;
  font-family: Geist Mono, monospace;
  ```

### Faux-OS Window Chrome
- When mocking software: wrap in minimal container
- White top bar with three small light gray circles (macOS window controls)

---

## ICONOGRAPHY & IMAGERY

| Element | Directive |
|:---|:---|
| **System Icons** | Phosphor Icons (Bold or Fill weights) or Radix UI Icons. Standardize stroke width globally |
| **Illustrations** | Monochromatic, rough continuous-line ink sketches on white. Single offset geometric shape filled with muted pastel |
| **Photography** | Desaturated, warm-toned. Subtle `opacity: 0.04` warm grain overlay. Never oversaturated stock |
| **Hero Backgrounds** | Subtle full-width imagery at very low opacity, soft radial light spots (`radial-gradient` at `opacity: 0.03`), or minimal geometric line patterns |
| **Image Placeholders** | `https://picsum.photos/seed/{context}/1200/800` |

---

## SUBTLE MOTION (Invisible Sophistication)

Motion should feel invisible — present but never distracting. Goal: quiet sophistication, not spectacle.

### Scroll Entry
```css
/* Elements fade in as they enter viewport */
transform: translateY(12px);
opacity: 0;
/* Resolves over 600ms */
transition: all 600ms cubic-bezier(0.16, 1, 0.3, 1);
```
Use `IntersectionObserver` — NEVER `window.addEventListener('scroll')`

### Hover States
Cards: ultra-subtle shadow shift:
```css
/* Default → hover */
box-shadow: 0 0 0 → 0 2px 8px rgba(0,0,0,0.04);
transition: 200ms;
```
Buttons: `scale(0.98)` on `:active`

### Staggered Reveals
```css
animation-delay: calc(var(--index) * 80ms);
```
Never mount everything simultaneously.

### Background Ambient Motion (Optional)
- Single very slow-moving radial gradient blob: `animation-duration: 20s+`, `opacity: 0.02–0.04`
- ONLY on `position: fixed; pointer-events: none` layer
- NEVER on scrolling containers

### Performance Rules
- Animate EXCLUSIVELY via `transform` and `opacity`
- No layout-triggering properties (`top`, `left`, `width`, `height`)
- `will-change: transform` sparingly, only on actively animating elements

---

## EXECUTION PROTOCOL

When generating minimalist editorial frontend code:

1. **Establish macro-whitespace first** — massive vertical padding between sections (`py-24` or `py-32`)
2. **Constrain typography content width** — `max-w-4xl` or `max-w-5xl`
3. **Apply custom typographic hierarchy** — monochromatic color variables immediately
4. **Enforce 1px border rule** — every card, divider, and border uses `1px solid #EAEAEA`
5. **Add scroll-entry animations** — all major content blocks
6. **Ensure sections have visual depth** — subtle background imagery, ambient gradients, or minimal textures
7. **Deliver production-ready code** — no manual adjustments required

---

## WHEN TO APPLY THIS PROTOCOL

Activate `minimalist-ui` when the physical scene description suggests:
- Workspace/productivity tool (Notion, Linear, Craft competitors)
- Professional dashboard with document-like layout
- Editorial publication or blog
- Developer tool with code-heavy interface
- High-end SaaS with knowledge workers as primary audience
- Any surface where whitespace IS the design
