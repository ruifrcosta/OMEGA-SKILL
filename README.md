```
   ____  __  ___________  ______    __________  ______  ___
  / __ \/  |/  / ____/  |/  /   |  /_  __/ __ \/  _/  |/  /
 / / / / /|_/ / __/ / /|_/ / /| |   / / / / / // // /|_/ / 
/ /_/ / /  / / /___/ /  / / ___ |  / / / /_/ // // /  / /  
\____/_/  /_/_____/_/  /_/_/  |_| /_/  \____/___/_/  /_/   
                                                           
   SISTEMA OPERACIONAL DE ENGENHARIA AUTÓNOMA │ KERNEL v2.0
```

# OMEGA — Autonomous Engineering Operating System

OMEGA is a Claude skill that transforms the assistant into a full Big Tech engineering organization. Rather than answering questions about code, OMEGA acts as an autonomous software factory: it reads your project, syncs its memory, spawns specialized subagents, produces complete implementations, and documents every decision — without being asked to do any of that explicitly.

The closest analogy is having a staff engineer, security auditor, frontend craftsman, SRE, and technical writer active simultaneously, all reading from the same shared context, all producing artifacts that persist between sessions.

---

## What OMEGA does on every response

Before writing a single line of code, OMEGA runs a mandatory boot sequence. It announces itself with a structured header showing the detected domain, active phase, agents spawned, and references being read. It then resolves the vault path (never assuming a fixed location), reads all six memory-bank files to restore context from the previous session, and consults the relevant domain reference files. Only then does it implement.

After finishing, it appends a session summary to the vault and updates the memory-bank files so the next session begins with full context.

This behavior is not optional and cannot be skipped. It runs on every response.

---

## Reference architecture

OMEGA ships with 25 domain reference files that the agents read before acting. These are not guidelines — they contain the actual implementation patterns, code templates, checklists, and troubleshooting procedures used during execution.

| Reference | Domain |
|-----------|--------|
| `00-troubleshooting.md` | Universal debugging playbook — read first when anything is broken |
| `01-architecture.md` | ADRs, DDD, CQRS, hexagonal architecture, event sourcing |
| `02-design-system.md` | Design tokens, OKLCH color scales, typography, component states |
| `03-infrastructure.md` | Docker multi-stage, Kubernetes manifests, Terraform, Helm |
| `04-frontend.md` | Next.js App Router, React Server Components, Zustand, Web Vitals |
| `05-backend.md` | NestJS, Go, API contracts, Postgres indexing, queue workers |
| `06-mobile.md` | Expo Router, offline-first, Reanimated, FlashList, SecureStore |
| `07-security.md` | Zero Trust, RBAC, OWASP Top 10, CORS hardening, JWT patterns |
| `08-data.md` | Kafka, Airflow, dbt, ML pipelines, pgvector |
| `09-observability.md` | OpenTelemetry, Prometheus alerts, Grafana dashboards, SLOs |
| `10-ai-agents.md` | LangGraph, RAG hybrid search, MCP, prompt caching, token governance |
| `11-obsidian.md` | Vault discovery protocol, 33-folder structure, dual documentation/memory role |
| `12-diagrams.md` | Mermaid: C4, ERD, sequence, flowchart, state diagrams |
| `13-token-cost.md` | Prompt caching, model routing, token budget enforcement, cost attribution |
| `14-supabase-resend.md` | Supabase RLS policies, auth patterns, Resend email queuing |
| `15-qa-testing.md` | Playwright, Vitest, k6, PICT combinatorial testing, accessibility |
| `16-monorepo.md` | Turborepo, pnpm workspaces, package boundaries, design tokens |
| `17-compliance.md` | ISO 27001, SOC 2, GDPR Article 17, HIPAA column encryption |
| `18-marketing-growth.md` | CRO, conversion copy, CTA formulas, landing page structure |
| `19-google-workspace.md` | Google Workspace APIs, Apps Script, Model Armor, Sheets automation |
| `20-taste-engine.md` | Anti-slop frontend: 3-dial system, 47 bans, Pre-Flight checklist, liquid-glass CSS |
| `21-humanizer.md` | Anti-AI writing: 29-pattern audit, voice calibration, zero em-dashes |
| `22-find-skills.md` | Skill registry discovery, quality gates, installation protocol |
| `23-memory-bank.md` | 6-core memory bank scaffolding, session persistence, boot protocol |

---

## Subagent system

OMEGA routes tasks to specialized agents based on trigger keywords. Each agent announces its activation, reads its assigned reference file, executes, then documents its output to the vault.

| Trigger | Agent |
|---------|-------|
| Architecture, ADR, DDD, CQRS | Arch Agent |
| Security, CORS, RBAC, OWASP | Security Agent |
| Frontend, React, Next.js, component | Frontend Agent |
| Mobile, Expo, React Native | Mobile Agent |
| Docker, Kubernetes, Terraform | Infra Agent |
| NestJS, Go, API, queue, Postgres | Backend Agent |
| Tests, Playwright, k6, coverage | QA Agent |
| Grafana, SLO, OTel, monitoring | SRE Agent |
| LangGraph, RAG, vector, agents | AI Agent |
| Sprint, phase, milestone, roadmap | PMO Agent |
| Design, craft, shape, polish, taste | Design Agent |
| Token cost, budget, FinOps | FinOps Agent |
| Vault, ADR, Obsidian, runbook | Obsidian Agent |
| Growth, CRO, copy, conversion | Growth Agent |
| Any broken behavior, crash, error | Debug Agent |
| Frontend quality, design Pre-Flight | Taste Agent |
| Any text output: docs, ADRs, copy | Humanizer Agent |

---

## Memory system

OMEGA maintains continuity across stateless sessions through two layers.

The first layer is `memory-bank/` at the project root — six markdown files that serve as working memory. OMEGA reads all six at session start, then updates them at session end with what changed, what was decided, and what to pick up next.

```
memory-bank/
    projectbrief.md      Requirements, scope, and what is explicitly out of scope
    productContext.md    Why this project exists, UX goals, user flows
    systemPatterns.md    Architecture patterns, DDD contexts, critical paths
    techContext.md       Stack, versions, constraints, package limits
    activeContext.md     Current sprint focus, recent changes, active decisions
    progress.md          Task checklist: [ ] planned, [/] in-progress, [x] done
```

The second layer is the vault's `32-AI-Memory/` folder — session logs, learned patterns, and error memory. These persist across sessions through obsidian-git.

---

## Vault system

OMEGA never creates documentation at the project root and never assumes a fixed vault location. At the start of every session it runs a discovery algorithm:

1. Is `OMEGA_VAULT_PATH` set? Use it.
2. Is there a `.git` directory? Walk up to find the repo root.
3. Does `docs/` exist? Vault goes in `docs/vault/`.
4. Does `documentation/` or `wiki/` exist? Vault goes inside it.
5. Does a legacy `obsidian-vault/` exist? Honor it, never rename.
6. Nothing found? Create `docs/vault/`.

When initialized, the vault receives a complete `.obsidian/` configuration matching the canonical setup in `examples/.obsidian/`, including the Vicious theme, amber accent (`#ffaf1a`), and 16 community plugins.

The 33 vault folders cover every domain of organizational knowledge, from `00-Executive` through `33-Architecture-Recovery`. ADRs live in `14-ADRs/`. Runbooks live in `15-Runbooks/`. Post-mortems live in `16-Incidents/`. Agent memory archives live in `32-AI-Memory/`.

To initialize the vault on a project:

```bash
python scripts/omega-cli.py resolve-vault   # see where it resolves
python scripts/omega-cli.py init-vault      # create it
python scripts/omega-cli.py status          # check health
python scripts/omega-cli.py audit           # scan for secrets and vault gaps
python scripts/omega-cli.py create-adr --title "Your Decision" --status proposed
```

---

## Design system

OMEGA applies a different visual identity based on the project's business domain.

| Domain | Heading / Body | Accent |
|--------|---------------|--------|
| Healthcare | Figtree / DM Sans | Emerald `#059669` |
| Finance | Söhne / IBM Plex Sans | Royal Blue `#1D4ED8` |
| Productivity | Geist / Geist Mono | Violet `#7C3AED` |
| E-Commerce | Playfair Display / Nunito | Amber `#FBBF24` |
| Fitness | Space Grotesk / DM Sans | Green `#16A34A` |
| Education | Lora / Source Serif 4 | Blue `#2563EB` |
| NFT / Web3 | Anton / mono | Neon `#6FFF00` |
| Travel / Media | Instrument Serif / Barlow | Amber `#F59E0B` |

Every frontend task sets three dials before producing any output: `DESIGN_VARIANCE` (1 = symmetric, 10 = asymmetric chaos), `MOTION_INTENSITY` (1 = static, 10 = cinematic), and `VISUAL_DENSITY` (1 = art gallery, 10 = cockpit). These govern layout, animation, and component density decisions.

Hardcoded bans include `transition: all`, `scale(0)` entrances, `ease-in` on UI elements, `h-screen` for heroes, nested card grids, neon gradients, and em-dashes in any text output.

---

## Governance

Every significant architectural decision requires an ADR written before implementation begins. OMEGA will refuse to implement something that lacks a corresponding ADR when the decision is non-trivial.

OMEGA classifies all findings by severity:

- Critical: blocks execution. Security breach, architecture corruption, data loss risk. Must be corrected before any implementation.
- High: alerts and proposes a fix. Performance under scale, structural drift. Waits for confirmation before proceeding.
- Medium: logs and proceeds. Minor technical debt, style deviation. Creates a TODO in `progress.md`.
- Low: proceeds silently. Cosmetic changes. Updates context and continues.

Every security task validates against the OWASP Top 10. Every API endpoint receives: input validation, RBAC check, rate limiting, structured logging with trace ID, idempotency key on mutations, and a versioned path.

---

## Installation

OMEGA is installed as a Claude skill. Upload the `.skill` file through Claude's settings interface under Skills, or install via the CLI if available:

```bash
npx skills add ruifrcosta/OMEGA-SKILL -g -y
```

To update:

```bash
npx skills update
```

To check the vault after installation on a project:

```bash
python scripts/omega-cli.py status
```

---

## Repository structure

```
OMEGA-SKILL/
    SKILL.md                     Core skill definition and boot sequence
    README.md                    This file
    references/                  25 domain reference files (read by agents at runtime)
        00-troubleshooting.md
        01-architecture.md
        ...
        23-memory-bank.md
        design/                  Design command references (craft, shape, polish, etc.)
        intelligence/            Orchestration and capability graphs
        external/                Integrated skills (taste-skill, humanizer, ui-ux-pro-max)
    scripts/
        omega-cli.py             Vault discovery, initialization, ADR creation, audit
        load-context.mjs         Design context loader
        live.mjs                 Live server for visual iteration
        design-parser.mjs        Design token and command parser
    examples/
        .obsidian/               Canonical Obsidian configuration
            community-plugins.json
            appearance.json      Vicious theme, amber accent
            graph.json           Domain-colored knowledge graph
            snippets/            CSS snippets (MCL, Heatmap Calendar, omega-theme)
            plugins/             Plugin manifests
        showcases/               Example HTML outputs
```

---

OMEGA v7 — Autonomous Engineering, Design, and Governance Operating System.
