# Obsidian Knowledge Vault Reference

## Table of Contents
1. [Vault Discovery Protocol — NEVER assume a path](#discovery)
2. [Vault Structure — 33 Folders](#structure)
3. [.obsidian/ Configuration](#obsidian-config)
4. [Document Templates (ADR, Runbook, Sprint, Incident)](#templates)
5. [Wiki-Linking & Frontmatter Standards](#wiki-links)
6. [Vault Sync Protocol — when to update](#sync)

---

## 1. Vault Discovery Protocol {#discovery}

**CRITICAL RULE: OMEGA never assumes `obsidian-vault/` exists or where it is.**
Before any documentation action, run the discovery algorithm below — either via
`python scripts/omega-cli.py resolve-vault` or by applying the same logic manually.

### Discovery Algorithm (in priority order)

```
Step 1 — Check env var
   OMEGA_VAULT_PATH set? → Use it directly. Done.

Step 2 — Find the repository root
   Walk up from cwd until .git/ is found.
   No .git → treat cwd as repo root.

Step 3 — Look for existing documentation folder
   Check repo_root/ for (in order):
     docs/              ← most common, GitHub Pages standard
     documentation/
     wiki/
     .docs/
     obsidian-vault/    ← legacy OMEGA, still honoured

Step 4 — Determine vault path
   Case A: docs/ exists AND contains OMEGA numbered folders (00-*, 01-*, etc.)
     → vault = docs/           (it's already an OMEGA vault)

   Case B: docs/ exists AND has a vault/ subfolder with OMEGA structure
     → vault = docs/vault/

   Case C: docs/ exists but NO vault yet
     → vault = docs/vault/     (nest inside existing docs)

   Case D: NO docs/ folder exists anywhere
     → vault = repo_root/docs/vault/   (create the whole path)

Step 5 — Never create obsidian-vault/ at repo root
   Unless the repository already has it (Case A legacy).
   New projects always get docs/vault/ structure.
```

### CLI Usage

```bash
# See what path OMEGA resolved and why
python scripts/omega-cli.py resolve-vault

# Initialize (or sync) the vault
python scripts/omega-cli.py init-vault

# Vault health check
python scripts/omega-cli.py status
```

### Example resolution outputs

**New project, no docs folder:**
```json
{
  "repo_root": "/home/dev/techstore",
  "vault_path": "/home/dev/techstore/docs/vault",
  "vault_exists": false,
  "reason": "new-docs-vault:docs/vault"
}
```

**Project with existing docs/:**
```json
{
  "repo_root": "/home/dev/techstore",
  "vault_path": "/home/dev/techstore/docs/vault",
  "vault_exists": false,
  "reason": "new-inside-existing-docs:docs/vault"
}
```

**Legacy OMEGA project:**
```json
{
  "repo_root": "/home/dev/old-project",
  "vault_path": "/home/dev/old-project/obsidian-vault",
  "vault_exists": true,
  "reason": "existing-omega-vault:obsidian-vault"
}
```

### In Claude conversations (no filesystem access)

When Claude cannot execute scripts, apply the algorithm mentally:
1. Ask: "Does this project have a `docs/`, `documentation/`, or `wiki/` folder?"
2. If yes → vault goes inside it as `vault/` subfolder
3. If no → create `docs/vault/` at repo root
4. Never output `obsidian-vault/` paths for new projects

---

## 2. Vault Structure — 33 Folders {#structure}

Once the vault path is resolved, the structure is always:

```
{vault_path}/
├── .obsidian/                    ← Obsidian config (app, appearance, graph, hotkeys)
│   ├── app.json
│   ├── appearance.json
│   ├── graph.json
│   ├── hotkeys.json
│   ├── workspace.json
│   ├── community-plugins.json
│   └── snippets/
│       └── omega-theme.css
├── README.md                     ← Vault index with full folder table
├── .omega-vault.json             ← Machine-readable config (path, repo_root, reason)
│
├── 00-Executive/                 Vision, OKRs, roadmap, business goals
├── 01-Architecture/              System blueprints, bounded contexts, DDD maps
├── 02-Product/                   User stories, personas, feature flags
├── 03-Infrastructure/            Cloud topology, network diagrams, DR policies
├── 04-Frontend/                  Component library, Web Vitals budgets, state designs
├── 05-Backend/                   API contracts, service catalog, DB ERDs, queues
├── 06-Mobile/                    Expo configs, OTA updates, offline-first
├── 07-AI/                        Agent catalog, prompt library, token budgets
├── 08-Data/                      Event streams, ETL DAGs, ML schemas
├── 09-Security/                  Threat models, CORS/CSP, IAM, pentest reports
├── 10-Observability/             SLOs, Prometheus alerts, Grafana dashboards
├── 11-Design-System/             Design tokens, typography, component patterns
├── 12-RBAC/                      Role definitions, permission matrix, access log
├── 13-Sprints/                   Sprint plans, retrospectives, delivery logs
├── 14-ADRs/                      ← MOST CRITICAL: every architectural WHY
│   ├── adr-index.md
│   └── ADR-NNNN-title.md
├── 15-Runbooks/                  ← SECOND MOST CRITICAL: every operational HOW
│   ├── runbook-index.md
│   └── SOP-NNNN-title.md
├── 16-Incidents/                 Post-mortems, resolution timelines
├── 17-Diagrams/                  Mermaid source: C4, ERD, sequence, flowchart
├── 18-Knowledge-Graph/           Cross-domain concept maps, tag registry
├── 19-Standards/                 Coding standards, git conventions, API style
├── 20-QA/                        Test strategy, coverage reports, load results
├── 21-Compliance/                ISO 27001, SOC 2, GDPR registry
├── 22-Token-Optimization/        Prompt caching benchmarks, compression logs
├── 23-Cost-Optimization/         Cloud spend analysis, rightsizing reports
├── 24-Agent-Orchestration/       LangGraph flows, subagent contracts
├── 25-Platform-Engineering/      CI/CD pipelines, internal developer platform
├── 26-Workflow-Systems/          Automation playbooks, GWS recipes
├── 27-Developer-Experience/      Onboarding guide, local bootstrap, DX tooling
├── 28-Disaster-Recovery/         Failover procedures, backup schedules
├── 29-Audit-Logs/                Security access logs, deploy audit trail
├── 30-Kubernetes/                Namespace registry, Helm charts, autoscaling
├── 31-MCP/                       Model Context Protocol servers, tool definitions
├── 32-AI-Memory/                 Persistent memory schemas, vector DB configs
└── 33-Architecture-Recovery/     Drift detection, legacy migration maps
```

---

## 3. .obsidian/ Configuration {#obsidian-config}

The `init-vault` command writes a complete `.obsidian/` directory. Key settings:

**app.json** — Core editor settings (live preview, line numbers, readable width)

**appearance.json** — Dark theme, Inter font, JetBrains Mono for code

**graph.json** — Colour-coded knowledge graph:
- ADR nodes → amber
- Security nodes → red
- Incident nodes → orange
- Runbook nodes → green

**omega-theme.css** — Custom CSS snippet:
```css
:root { --omega-accent: #f59e0b; }
.theme-dark {
  --background-primary: #0f1117;     /* near-black */
  --background-secondary: #161b22;   /* GitHub dark secondary */
}
/* ADR/Runbook folders highlighted in amber */
.nav-folder-title[data-path^="14-"],
.nav-folder-title[data-path^="15-"] { color: var(--omega-accent); font-weight: 600; }
```

**community-plugins.json** — Recommended plugins:
- `dataview` — Query vault as a database
- `templater-obsidian` — Document templates
- `obsidian-git` — Auto-commit vault to git
- `calendar` — Sprint calendar view

---

## 4. Document Templates {#templates}

### Every document MUST have this frontmatter

```yaml
---
title: "Document Title"
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: draft       # draft | review | approved | archived
tags: [domain, type, context]
related:
  - "[[ADR-NNNN-title]]"
  - "[[15-Runbooks/related-runbook]]"
---
```

### ADR Template (`14-ADRs/ADR-NNNN-title.md`)

```markdown
---
id: ADR-NNNN
title: "Short Imperative Title"
status: proposed    # proposed | accepted | deprecated | superseded
date: YYYY-MM-DD
deciders: [CTO, Tech Lead]
supersedes: []
superseded_by: []
tags: [adr, architecture, decision]
---

# ADR-NNNN: [Title]

## Status
`proposed` — under review until YYYY-MM-DD

## Context
What problem? What constraints? What makes this decision necessary now?
Write the minimum context a new engineer would need to understand WHY.

## Decision
Active voice: "We will use X because Y."
Be specific. Explain the reasoning, not just the outcome.

## Alternatives Considered

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| Option A | ... | ... | ... |
| Option B | ... | ... | ... |

## Consequences

**Positive:**
- What gets better?

**Negative:**
- What gets harder? What tradeoffs do we accept?

**Risks:**
- What could go wrong? What's the mitigation plan?

## Implementation Notes
Key patterns, library versions, migration steps, important gotchas.

## Review Date
YYYY-MM-DD (one year from creation, or sooner if high-risk)

## Related
- [[adr-index]]
- [[../01-Architecture/README]]
```

### Runbook Template (`15-Runbooks/SOP-NNNN-title.md`)

```markdown
---
title: "Runbook: [Procedure Name]"
created: YYYY-MM-DD
reviewed: YYYY-MM-DD
status: active
severity: sev-1     # sev-1 | sev-2 | sev-3
tags: [runbook, operations, [domain]]
---

# Runbook: [Procedure Name]

## When to Use This Runbook
Describe the symptoms or trigger conditions that bring someone here.

## Pre-requisites
- Access to X
- Tool Y installed
- Permission Z

## Steps

### 1. [First major step]
```bash
# command here
```
Expected output: ...

### 2. [Second major step]
...

## Verification
How to confirm the procedure worked correctly.

## Rollback
If something went wrong, how to undo this procedure.

## Escalation
If this runbook doesn't resolve the issue, escalate to: [Name/Team]

## Related
- [[../14-ADRs/ADR-NNNN-related]]
- [[../16-Incidents/README]]
```

### Post-Mortem Template (`16-Incidents/YYYY-MM-DD-title.md`)

```markdown
---
title: "Post-Mortem: [Incident Title]"
date: YYYY-MM-DD
severity: sev-1
duration: 45m
services_affected: [service-a, service-b]
authors: [Name]
status: draft       # draft | reviewed | closed
tags: [incident, postmortem, [domain]]
---

# Post-Mortem: [Title]

## Summary
One paragraph: what happened, how long, user impact.

## Timeline

| Time (UTC) | Event |
|-----------|-------|
| HH:MM | First alert fired |
| HH:MM | On-call acknowledged |
| HH:MM | Root cause identified |
| HH:MM | Mitigation deployed |
| HH:MM | Service restored |

## Root Cause
Trace it all the way back. "The database ran out of connections because..."

## Contributing Factors
What made this worse or harder to detect?

## What Went Well
Non-blaming recognition of effective response actions.

## What Could Be Improved
Specific, actionable gaps (not vague).

## Action Items

| Item | Owner | Due Date | Ticket |
|------|-------|----------|--------|
| Add missing alert for X | @engineer | YYYY-MM-DD | PROJ-NNN |
| Improve runbook for Y | @sre | YYYY-MM-DD | PROJ-NNN |

## Related
- [[../14-ADRs/ADR-NNNN-related]]
- [[../15-Runbooks/runbook-affected]]
```

### Sprint Template (`13-Sprints/YYYY-WNN-sprint.md`)

```markdown
---
title: "Sprint YYYY-WNN"
week: YYYY-WNN
start: YYYY-MM-DD
end: YYYY-MM-DD
team: [Name, Name]
status: in-progress   # planned | in-progress | done
tags: [sprint, delivery]
---

# Sprint YYYY-WNN: [Theme]

## Sprint Goal
What does "done" look like for this sprint? One sentence.

## Mandatory Categories (all 7 must have at least one task)

### Architecture / ADR
- [ ] [[../14-ADRs/ADR-NNNN-title]] — Author: @name

### Security Validation
- [ ] Security review for [feature] — Author: @name

### Feature Development
- [ ] [Feature name] — Author: @name, Ticket: PROJ-NNN

### QA / Tests
- [ ] [Test description] — Author: @name

### Documentation
- [ ] Update [[../01-Architecture/README]] — Author: @name

### Observability
- [ ] Add alert for [condition] — Author: @name

### Cost Review
- [ ] Rightsizing review for [service] — Author: @name

## Retrospective

### What worked well?

### What didn't work?

### Process improvements for next sprint?

## Related
- [[YYYY-WNN-prev-sprint]]
- [[YYYY-WNN-next-sprint]]
```

---

## 5. Wiki-Linking & Frontmatter Standards {#wiki-links}

### Linking Rules
```markdown
# Standard wiki-link
See [[14-ADRs/ADR-0003-database-choice]]

# Link with display alias
See [[14-ADRs/ADR-0003-database-choice|our database decision]]

# Link to heading within a document
See [[01-Architecture/README#bounded-contexts]]

# Inline reference
We chose Supabase (see [[14-ADRs/ADR-0005-supabase]]) because...
```

### Tag Conventions
Always include at minimum: `[domain, document-type]`

```yaml
# ADR
tags: [adr, architecture, database]

# Runbook
tags: [runbook, operations, database]

# Incident
tags: [incident, postmortem, api]

# Sprint
tags: [sprint, delivery, 2025-Q2]
```

### Cross-Reference Rules
Every document must link to:
- Its relevant ADR(s) in `14-ADRs/`
- Related runbook(s) in `15-Runbooks/` (if it involves operations)
- The parent folder `README.md`
- Any superseding or predecessor document

---

## 6. Vault Sync Protocol {#sync}

### Mandatory sync triggers

| Event | Documents to create/update |
|-------|---------------------------|
| Architectural decision made | New ADR in `14-ADRs/`, update `01-Architecture/` |
| New service or API created | `05-Backend/` doc + runbook in `15-Runbooks/` |
| Security change | `09-Security/` doc + relevant ADR |
| Incident resolved | Post-mortem in `16-Incidents/`, update runbook |
| Sprint completed | Retrospective in `13-Sprints/` |
| Infrastructure change | `03-Infrastructure/` or `30-Kubernetes/` |
| New AI feature | `07-AI/` + `24-Agent-Orchestration/` |
| Compliance event | `21-Compliance/` + `29-Audit-Logs/` |
| Deploy runbook changed | `15-Runbooks/` + timestamp update |

### Sync checklist (run after every implementation phase)

```
□ ADR exists for every significant architectural decision
□ HLD/LLD updated in 01-Architecture/ if system structure changed
□ Runbook updated or created for every new operational procedure
□ Observability: new alerts documented in 10-Observability/
□ Sprint task list current in 13-Sprints/
□ All new documents have YAML frontmatter + tags + wiki-links
□ No orphaned documents (every doc has at least one incoming link)
□ .omega-vault.json reflects current vault path
```

### Vault health check command

```bash
python scripts/omega-cli.py status
python scripts/omega-cli.py audit
```
