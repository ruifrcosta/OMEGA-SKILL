# UI INTELLIGENCE — Design Database Search System

Distilled from `nextlevelbuilder/ui-ux-pro-max-skill`. BM25-ranked searchable databases for styles, colors, typography, charts, UX guidelines, and stack-specific patterns.

---

## SEARCH ENGINE OVERVIEW

The `ui-ux-pro-max` system is a BM25 + regex hybrid search engine over curated CSV databases. It provides design decisions with reasoning, not just templates.

**Primary command:**
```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<query>" --domain <domain> [-n <max_results>]
```

**Design system generation (always start here for new projects):**
```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]
```

---

## AVAILABLE SEARCH DOMAINS

| Domain | Use For | Example Keywords |
|:---|:---|:---|
| `product` | Product type recommendations | SaaS, e-commerce, portfolio, healthcare, beauty, service |
| `style` | UI styles, colors, effects | glassmorphism, minimalism, dark mode, brutalism |
| `typography` | Font pairings with Google Fonts imports | elegant, playful, professional, modern |
| `color` | Color palettes by product type | saas, ecommerce, healthcare, beauty, fintech, service |
| `landing` | Page structure, CTA strategies | hero, testimonial, pricing, social-proof |
| `chart` | Chart types, library recommendations | trend, comparison, timeline, funnel, pie |
| `ux` | Best practices, anti-patterns | animation, accessibility, z-index, loading |
| `react` | React/Next.js performance | waterfall, bundle, suspense, memo, rerender, cache |
| `web` | App interface guidelines | accessibilityLabel, touch targets, safe areas |
| `prompt` | AI prompts, CSS keywords | (style name) |

---

## DESIGN SYSTEM WORKFLOW (Standard OMEGA Protocol)

### Step 1: Generate Design System (REQUIRED for new projects)
```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<product> <industry> <style>" --design-system -p "Project Name"
```
Returns: Complete design system — pattern, style, colors, typography, effects, anti-patterns

### Step 2: Persist Design System (Master + Overrides Pattern)
```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name"
```
Creates:
- `design-system/MASTER.md` — Global Source of Truth with all design rules
- `design-system/pages/` — Folder for page-specific overrides

**With page-specific override:**
```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name" --page "dashboard"
```
Creates `design-system/pages/dashboard.md` with page-specific deviations from Master

**Hierarchical retrieval rule:**
1. Building specific page → check `design-system/pages/<page-name>.md`
2. If page file exists → its rules OVERRIDE Master file
3. If not → use `design-system/MASTER.md` exclusively

### Step 3: Supplement with Detailed Searches
After getting design system, use domain searches for additional details:
```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

### Step 4: Stack-Specific Guidelines
```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<keyword>" --stack <stack>
```

**Available Stacks:** `html-tailwind` (default), `react`, `nextjs`, `astro`, `vue`, `nuxtjs`, `nuxt-ui`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`, `jetpack-compose`

---

## DATABASE INVENTORY

The system contains these curated CSV databases:
- `products.csv` — Product type patterns (58k)
- `styles.csv` — UI styles and effects (143k)
- `colors.csv` — Color palettes by context (32k)
- `typography.csv` — Font pairings (50k)
- `charts.csv` — Chart types and libraries (19k)
- `ux-guidelines.csv` — Best practices (19k)
- `landing.csv` — Landing page structures (17k)
- `react-performance.csv` — React perf patterns (15k)
- `google-fonts.csv` — Complete Google Fonts (745k)
- `icons.csv` — Icon library reference (21k)
- `app-interface.csv` — App interface guidelines (10k)
- `ui-reasoning.csv` — Reasoning rules for design selection (53k)
- `design.csv` — Design patterns (108k)

---

## COMMON STICKING POINTS

| Problem | Search Solution |
|:---|:---|
| Can't decide on style/color | Re-run `--design-system` with different keywords |
| Dark mode contrast issues | `--domain color "dark mode accessible pairs"` |
| Animations feel unnatural | `--domain ux "spring-physics easing exit-faster"` |
| Form UX is poor | `--domain ux "inline-validation error-clarity focus-management"` |
| Navigation feels confusing | `--domain ux "nav-hierarchy back-behavior"` |
| Layout breaks on small screens | `--domain ux "mobile-first breakpoint-consistency"` |
| Performance / jank | `--domain react "virtualize-lists main-thread debounce"` |

---

## QUERY STRATEGY

- Use **multi-dimensional keywords** — combine product + industry + tone + density:
  - `"entertainment social vibrant content-dense"` not just `"app"`
- Try different keywords for same need: `"playful neon"` → `"vibrant dark"` → `"content-first minimal"`
- Use `--design-system` first for full recommendations, then `--domain` to deep-dive
- Always add stack flag for implementation-specific guidance

---

## PRE-DELIVERY VALIDATION FLOW

```bash
# UX validation pass
python3 skills/ui-ux-pro-max/scripts/search.py "animation accessibility z-index loading" --domain ux

# Quick Reference §1–§3 (CRITICAL + HIGH priority)
```

Verify:
- [ ] Tested on 375px (small phone) AND landscape orientation
- [ ] Behavior with reduced-motion enabled
- [ ] Dynamic Type at largest size
- [ ] Dark mode contrast independently (don't assume light mode values work)
- [ ] All touch targets ≥44pt
- [ ] No content hidden behind safe areas

---

## PROFESSIONAL UI RULES (Frequently Overlooked)

### Icons & Visual Elements
- Default: `@phosphor-icons/react` or `@radix-ui/react-icons`
- NEVER: emojis as structural icons (font-dependent, inconsistent, non-themeable)
- NEVER: raster PNG icons that blur
- Consistent stroke width within same visual layer (1.5px OR 2px — never mixed)
- Filled vs. Outline: ONE style per hierarchy level
- Touch targets: minimum 44×44pt (use `hitSlop` if icon is smaller)
- Icon contrast: WCAG 4.5:1 for small elements, 3:1 minimum for larger glyphs

### Interaction Standards
- Tap feedback within 80–150ms
- Micro-interaction timing: 150–300ms with native easing
- Disabled states: visually clear AND non-interactive
- NO controls that look tappable but do nothing

### Light/Dark Mode
- Primary text contrast: ≥4.5:1 in BOTH modes
- Secondary text: ≥3:1 in both modes
- Dividers/borders distinguishable in both modes
- Modal scrim: 40–60% black opacity
- Both themes tested independently — never inferred

### Layout & Spacing
- Safe area compliance: ALL fixed headers, tab bars, CTA bars
- Content width: consistent per device class
- 8dp spacing rhythm: consistent 4/8dp for padding/gaps/sections
- Readable text measure: no edge-to-edge paragraphs on tablets

---

## STACKS REFERENCE

| Stack | Focus |
|:---|:---|
| `html-tailwind` | Standard web (default) |
| `react` | React components and hooks |
| `nextjs` | App Router, SSR, RSC patterns |
| `astro` | Islands architecture |
| `vue` | Vue 3 Composition API |
| `svelte` | SvelteKit patterns |
| `swiftui` | iOS/macOS native |
| `react-native` | Cross-platform mobile |
| `flutter` | Dart/Flutter |
| `shadcn` | shadcn/ui component system |
| `jetpack-compose` | Android native |
