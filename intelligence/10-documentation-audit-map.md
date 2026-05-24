# OMEGA Documentation Audit Map
## Obsidian-First Architectural Records, Wiki-Links, & Sync Governance

This document establishes the repository documentation standard, Obsidian vault folder structure, and synchronization rules enforced across the OMEGA platform.

---

## 1. The Obsidian-First Knowledge Ecosystem

OMEGA rejects fragmented, out-of-date, and shallow documentation. All organizational memory, sprint metrics, architectural design records (ADRs), and recovery runbooks must be written in standard Markdown inside:

```
obsidian-vault/
```

### 1.1. Wiki-Link Ingestion Rules
To build a highly connected knowledge graph, files must reference each other using **wiki-links** containing relative paths:

- Example of linking an ADR: `[[obsidian-vault/14-ADRs/004-Supabase-RLS-Model.md]]`
- Example of linking a Runbook: `[[obsidian-vault/15-Runbooks/R03-Database-Restore.md]]`

---

## 2. Mandatory Obsidian Folder Structure

The Obsidian knowledge base is organized into **33 dedicated folders** covering all executive, architectural, and operational domains of a Big Tech organization:

```
obsidian-vault/
├── 00-Executive/                # OKRs, high-level business goals, quarterly plans
├── 01-Architecture/             # System blueprints, hexagonal models, DDD maps
├── 02-Product/                  # Product specifications, user stories, roadmaps
├── 03-Infrastructure/           # Terraform modules, network diagrams, VPC configurations
├── 04-Frontend/                 # Next.js configurations, state management, bundle metrics
├── 05-Backend/                  # API contracts, database designs, background queue plans
├── 06-Mobile/                   # Expo builds, deployment records, local secure storage
├── 07-AI/                       # Prompt architectures, model sanitizers, LangGraph states
├── 08-Data/                     # Kafka event maps, Airflow DAG models, ETL pipelines
├── 09-Security/                 # Threat modeling, CORS configurations, pentesting reports
├── 10-Observability/            # SLO specifications, Grafana board links, Prometheus rules
├── 11-Design-System/            # Spacing tokens, UI palettes, custom animations
├── 12-RBAC/                     # Roles permission tables, IAM policies
├── 13-Sprints/                  # Weekly agile sprints, task checklists
├── 14-ADRs/                     # Architectural Decision Records (ADRs)
├── 15-Runbooks/                 # Troubleshooting procedures, deploy steps, disaster steps
├── 16-Incidents/                # Post-mortems, crash histories, remediation records
├── 17-Diagrams/                 # Raw Mermaid codes, BPMN XML configurations
├── 18-Knowledge-Graph/          # Tag indices, ontology mappings
├── 19-Standards/                # Code standards, formatting metrics, lint presets
├── 20-QA/                       # E2E test coverages, Playwright reports
├── 21-Compliance/               # ISO 27001, ISO 9001 checklists, SOC 2 reports
├── 22-Token-Optimization/       # Context reduction reports, prompt tokens metrics
├── 23-Cost-Optimization/        # Sizing recommendations, AWS costs ledgers
├── 24-Agent-Orchestration/      # LangGraph flows, agent JSON contracts
├── 25-Platform-Engineering/     # Monorepo workspaces, internal developer platform guides
├── 26-Workflow-Systems/         # Golden Paths configurations, developer golden paths
├── 27-Developer-Experience/     # Local machine bootstrap instructions, dev requirements
├── 28-Disaster-Recovery/        # Failover procedures, backup schedules, recovery trials
├── 29-Audit-Logs/               # Admin activities logs, compliance changelogs
├── 30-Kubernetes/               # Helm charts specs, pod topologies, K8s manifests
├── 31-MCP/                      # Model Context Protocol integrations, server instructions
├── 32-AI-Memory/                # Agent milestone history, error memory
└── 33-Architecture-Recovery/    # Recovery procedures from architectural drift
```

---

## 3. Strict Synchronization Protocols (Gated Release)

To prevent the documentation from drifting away from actual code, OMEGA enforces the **Doc Synchronization pipeline**:

```
Developer makes code changes ──► Compile checks ──► Run tests ──► Audit Obsidian Vault
                                                                         │
                                                                         ▼
                                                            Sync Check: ADRs & Runbooks
                                                            fully match modified paths
                                                                         │
                                                                         ▼
                                                            Deploy production release
```

Every PR that modifies a core component must contain a corresponding documentation commit updating the relevant Obsidian vaults. Shallow documentation commits are automatically rejected at the CI level.
