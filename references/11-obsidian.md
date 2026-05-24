# Obsidian Knowledge Vault Reference (33-Folder Structure)

## Table of Contents
1. [Standardized 33-Folder Vault Architecture](#vault-structure)
2. [Wiki-Links & Metadata Guidelines](#wiki-links)
3. [Script: Automated Vault Generation](#generation-script)
4. [Markdown Templates (ADR, Runbook, Incident)](#templates)

---

## 1. Standardized 33-Folder Vault Architecture {#vault-structure}

The Obsidian vault is the ultimate repository of organizational memory. All plans, decisions, incidents, and guides live in this vault inside the folder structure:

```
obsidian-vault/
├── 00-Executive/             # Product vision, strategic goals, business context
├── 01-Architecture/          # High-level designs, bounded context maps, ubiquitous glossary
├── 02-Product/               # User stories, product requirements, success metrics
├── 03-Infrastructure/        # Cloud architecture, network topologies, DNS mappings
├── 04-Frontend/              # Performance budgets, route hierarchies, state designs
├── 05-Backend/               # API versioning tables, database ERDs, background tasks
├── 06-Mobile/                # Expo compilation configs, sync mechanisms, OTA updates
├── 07-AI/                    # AI agent decision trees, vector indexing scales, prompt logs
├── 08-Data/                  # Event stream tables, ETL DAG topologies, ML schemas
├── 09-Security/              # CORS rules, CSP headers, IAM mappings, threat models
├── 10-Observability/         # SLIs, SLOs thresholds, Prometheus alerting rules, dashboards
├── 11-Design-System/         # Theme CSS tokens, typography scales, Figma primitive layouts
├── 12-RBAC/                  # Group permission hierarchies, scope mappings, audit logs
├── 13-Sprints/               # Milestone descriptions, deliverables logs, sprint updates
├── 14-ADRs/                  # Architectural Decision Records (see 01-architecture.md)
├── 15-Runbooks/              # Server startup steps, data recovery plans, hotfix policies
├── 16-Incidents/             # Non-blaming post-mortems, resolution timelines, error tracking
├── 17-Diagrams/              # Source code for Mermaid diagrams and architectural models
├── 18-Knowledge-Graph/       # Cross-referenced technology logs and reference definitions
├── 19-Standards/             # Coding styles, review checklists, validation policies
├── 20-QA/                    # E2E test suites, coverage reports, regression plans
├── 21-Compliance/            # ISO 27001 scopes, SOC 2 reports, GDPR registry
├── 22-Token-Optimization/     # Token cost tracking tables, context compression guides
├── 23-Cost-Optimization/      # Compute cost reductions, rightsizing logs, DB scales
├── 24-Agent-Orchestration/    # Subagent structures, token-saving loops, dispatcher logic
├── 25-Platform-Engineering/   # CI/CD pipelines, pnpm workspace setups, Turborepo rules
├── 26-Workflow-Systems/       # Standardized pipeline setups, task handlers, webhooks logs
├── 27-Developer-Experience/   # Golden paths, development tooling manuals, onboarding UX
├── 28-Disaster-Recovery/      # Backup intervals, multi-zone failover rules, cold restore steps
├── 29-Audit-Logs/             # Security access requests logs, automated compliance check logs
├── 30-Kubernetes/             # Deployment zone affinity rules, ingress control configs
├── 31-MCP/                    # Model Context Protocol servers mapping, custom tools parameters
├── 32-AI-Memory/              # Long-term semantic profiles, prompt logs database
└── 33-Architecture-Recovery/  # Legacy deconstruction checklists, monolith migration maps
```

---

## 2. Wiki-Links & Metadata Guidelines {#wiki-links}

*   **Wiki-Links**: Always reference related documents using `[[wiki-link]]` syntax (e.g. `[[ADR-0001-nestjs]]` or `[[Sev1-2026-05-24-api-outage]]`). This enables Obsidian's interactive knowledge graph to visualize dependencies.
*   **YAML Frontmatter**: Every markdown document in the vault must feature precise metadata:

```markdown
---
id: DOC-UUID
title: "Document Title"
category: architecture # executive | security | runbook | incident | disaster-recovery
status: active # draft | active | archived
date: YYYY-MM-DD
tags: [nestjs, security, cors]
related: [ADR-0001, ADR-0012]
---
```

---

## 3. Script: Automated Vault Generation {#generation-script}

The following Node.js script can be run dynamically to generate the complete Obsidian vault hierarchy in any greenfield environment.

```javascript
// scripts/init-obsidian-vault.js
const fs = require('fs');
const path = require('path');

const folders = [
  '00-Executive', '01-Architecture', '02-Product', '03-Infrastructure',
  '04-Frontend', '05-Backend', '06-Mobile', '07-AI', '08-Data',
  '09-Security', '10-Observability', '11-Design-System', '12-RBAC',
  '13-Sprints', '14-ADRs', '15-Runbooks', '16-Incidents', '17-Diagrams',
  '18-Knowledge-Graph', '19-Standards', '20-QA', '21-Compliance',
  '22-Token-Optimization', '23-Cost-Optimization', '24-Agent-Orchestration',
  '25-Platform-Engineering', '26-Workflow-Systems', '27-Developer-Experience',
  '28-Disaster-Recovery', '29-Audit-Logs', '30-Kubernetes', '31-MCP',
  '32-AI-Memory', '33-Architecture-Recovery'
];

const vaultRoot = path.join(__dirname, '../obsidian-vault');

if (!fs.existsSync(vaultRoot)) {
  fs.mkdirSync(vaultRoot);
}

folders.forEach(folder => {
  const folderPath = path.join(vaultRoot, folder);
  if (!fs.existsSync(folderPath)) {
    fs.mkdirSync(folderPath);
    // Write an empty placeholder file
    fs.writeFileSync(path.join(folderPath, '.keep'), '');
  }
});

console.log('Obsidian 33-Folder vault initialized successfully.');
```

---

## 4. Markdown Templates (ADR, Runbook, Incident) {#templates}

### SRE Runbook Template (`15-Runbooks/SOP-0001-template.md`)
```markdown
# SOP-0001: API Database Recovery Runbook

## Overview
Instructions to restore the primary PostgreSQL database from automated S3 backups.

## Prerequisites
*   Access to the production Kubernetes cluster (`kubectl`).
*   Production AWS RDS privileges.

## Step-by-Step Operations
1.  **Stop Traffic Gateways**:
    ```bash
    kubectl scale deployment titan-api --replicas=0 -n production
    ```
2.  **Verify S3 Snapshots**:
    Identify the latest valid backup snapshot using AWS CLI.
3.  **Restore DB Instance**:
    Execute RDS restore operations.
4.  **Restore Gateways**:
    ```bash
    kubectl scale deployment titan-api --replicas=3 -n production
    ```
```
