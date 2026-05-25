# OMEGA References — Unified Index

Three layers. One folder. Zero ambiguity.

```
references/
├── 01–19: Engineering domains (architecture, infra, security, mobile…)
├── design/: Design vocabulary (23 commands + supporting files)
└── intelligence/: System-level audit maps and capability graphs
```

---

## Layer 1 — Engineering Domains (19 files)

Read before executing the corresponding engineering domain.

| File | Domain | When to Load |
|------|--------|-------------|
| `01-architecture.md` | DDD, CQRS, ADR templates, distributed patterns | Any architectural decision |
| `02-design-system.md` | Tokens, component standards, HTML generation | Design system work |
| `03-infrastructure.md` | K8s, Docker, Terraform, DR policies | Infrastructure changes |
| `04-frontend.md` | Next.js App Router, Zustand, animations, Core Web Vitals | Frontend development |
| `05-backend.md` | NestJS, Go, API contracts, queues, Postgres | Backend development |
| `06-mobile.md` | Expo Router, offline-first, biometrics, EAS | Mobile development |
| `07-security.md` | Zero Trust, CORS/CSP, RBAC, OWASP, pentesting | Any security decision |
| `08-data.md` | Spark, Kafka, ML pipelines, analytics | Data engineering |
| `09-observability.md` | OTel, Prometheus, Grafana, SLOs, incidents | Observability setup |
| `10-ai-agents.md` | Agent decision tree, RAG, memory governance | AI agent work |
| `11-obsidian.md` | Vault governance, document templates, 33-folder structure | Documentation tasks |
| `12-diagrams.md` | Mermaid templates by diagram type | Any diagram generation |
| `13-token-cost.md` | RTK, prompt caching, token budget rules | Optimization tasks |
| `14-supabase-resend.md` | RLS, Edge Functions, Resend retry patterns | Supabase or email work |
| `15-qa-testing.md` | Test pyramid, load testing, coverage rules | QA and testing |
| `16-monorepo.md` | Turborepo, pnpm, componentization | Monorepo setup |
| `17-compliance.md` | ISO 27001, SOC 2, GDPR, HIPAA-like | Compliance or audit |
| `18-marketing-growth.md` | CRO, copywriting, conversion playbooks | Growth and marketing |
| `19-google-workspace.md` | GWS API, Model Armor, shell escaping | GWS integrations |

---

## Layer 2 — Design Vocabulary (41 files in `design/`)

Loaded by the impeccable command router. Each file corresponds to one command.

### Context Setup (load first for any design task)
| File | Command | Role |
|------|---------|------|
| `design/teach.md` | `teach` | Set up PRODUCT.md and DESIGN.md |
| `design/document.md` | `document` | Generate DESIGN.md from existing code |
| `design/brand.md` | — | Register for brand/marketing surfaces |
| `design/product.md` | — | Register for product/app surfaces |

### Build Commands
| File | Command | What it does |
|------|---------|-------------|
| `design/craft.md` | `craft [feature]` | Shape then build end-to-end |
| `design/shape.md` | `shape [feature]` | Plan UX/UI before writing code |
| `design/extract.md` | `extract [target]` | Pull reusable tokens into design system |

### Evaluate Commands
| File | Command | What it does |
|------|---------|-------------|
| `design/critique.md` | `critique [target]` | UX review with heuristic scoring |
| `design/audit.md` | `audit [target]` | Technical checks: a11y, perf, responsive |
| `design/heuristics-scoring.md` | — | Nielsen 10 heuristics scoring guide |
| `design/personas.md` | — | 5-persona design testing framework |

### Refine Commands
| File | Command | What it does |
|------|---------|-------------|
| `design/polish.md` | `polish [target]` | Final quality pass before shipping |
| `design/bolder.md` | `bolder [target]` | Amplify safe or bland designs |
| `design/quieter.md` | `quieter [target]` | Tone down aggressive designs |
| `design/distill.md` | `distill [target]` | Strip to essence, remove complexity |
| `design/harden.md` | `harden [target]` | Production-ready: errors, i18n, edge cases |
| `design/onboard.md` | `onboard [target]` | Design first-run flows, empty states |

### Enhance Commands
| File | Command | What it does |
|------|---------|-------------|
| `design/animate.md` | `animate [target]` | Add purposeful animations |
| `design/colorize.md` | `colorize [target]` | Add strategic color to monochromatic UIs |
| `design/typeset.md` | `typeset [target]` | Improve typography hierarchy |
| `design/layout.md` | `layout [target]` | Fix spacing, rhythm, visual hierarchy |
| `design/delight.md` | `delight [target]` | Add personality and memorable touches |
| `design/overdrive.md` | `overdrive [target]` | Push past conventional limits |
| `design/live.md` | `live` | Visual variant mode in browser |

### Fix Commands
| File | Command | What it does |
|------|---------|-------------|
| `design/clarify.md` | `clarify [target]` | Improve UX copy, labels, error messages |
| `design/adapt.md` | `adapt [target]` | Adapt for different devices/screens |
| `design/optimize.md` | `optimize [target]` | Diagnose and fix UI performance |

### Style & Calibration
| File | Command | What it does |
|------|---------|-------------|
| `design/taste-engine.md` | `taste / flavor / bento` | Set design dials: variance, motion, density |
| `design/minimalist-ui.md` | `minimalist [target]` | Editorial/document-style UI |
| `design/marketing-growth.md` | `copy / cro / growth / launch` | 41-domain marketing stack |
| `design/design-squad.md` | `squad design/system/handoff` | Multi-agent design orchestration |
| `design/ui-intelligence.md` | `intel / intel system / intel stack` | BM25 design DB search |
| `design/codex.md` | — | Visual direction & image generation |

### Supporting References
| File | Domain |
|------|--------|
| `design/motion-design.md` | Duration/easing rules, 100/300/500 rule |
| `design/typography.md` | Type scale, pairing, readability |
| `design/color-and-contrast.md` | OKLCH, contrast ratios, palettes |
| `design/interaction-design.md` | 8 interactive states, gesture rules |
| `design/cognitive-load.md` | Mental effort assessment framework |
| `design/spatial-design.md` | Depth, layering, z-axis |
| `design/ux-writing.md` | Voice, tone, microcopy |
| `design/responsive-design.md` | Breakpoints, fluid grids, mobile-first |

---

## Layer 3 — Intelligence Maps (12 files in `intelligence/`)

Consult for system-level decisions. Read-only strategic reference.

| File | Purpose |
|------|---------|
| `intelligence/01-capability-intelligence-graph.md` | Full capability taxonomy map |
| `intelligence/02-orchestration-intelligence-graph.md` | 30-subagent hierarchy and routing |
| `intelligence/03-dependency-graph.md` | Monorepo package boundary map |
| `intelligence/04-architecture-intelligence-report.md` | Hexagonal/DDD/CQRS baseline |
| `intelligence/05-governance-gap-analysis.md` | ISO/SOC2/GDPR compliance gaps |
| `intelligence/06-ai-orchestration-analysis.md` | LangGraph, Model Armor, agent comms |
| `intelligence/07-workflow-intelligence-map.md` | Golden paths: greenfield, SRE, perf |
| `intelligence/08-security-audit-map.md` | Zero Trust, threat model, pentest rules |
| `intelligence/09-observability-audit-map.md` | OTel pipeline, SLO governance |
| `intelligence/10-documentation-audit-map.md` | Obsidian sync governance |
| `intelligence/11-token-optimization-audit.md` | Token cost baseline and RTK rules |
| `intelligence/12-cloud-cost-optimization-audit.md` | FinOps right-sizing baseline |
