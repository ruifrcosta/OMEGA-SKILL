# OMEGA Workflow Intelligence Map
## Golden Paths for Greenfield, Feature Additions, SRE Recovery, & Performance Tuning

This document diagrams the standard operational procedures (SOPs) and golden paths executed by OMEGA for typical engineering activities.

---

## 1. Greenfield Project Development (Phase 1 to 20)

Developing a greenfield project requires strict adherence to all 20 phases. Shortcuts are strictly prohibited.

```mermaid
graph TD
    P1[Phase 1: Repo Discovery] --> P2[Phase 2: Intelligence Extraction]
    P2 --> P3[Phase 3: Capability Mapping]
    P3 --> P4[Phase 4: Governance Audit]
    P4 --> P5[Phase 5: Architecture Reconstruction]
    P5 --> P6[Phase 6: Platform Engineering]
    P6 --> P7[Phase 7: Infrastructure Engineering]
    P7 --> P8[Phase 8: AI Orchestration]
    P8 --> P9[Phase 9: Design System Engineering]
    P9 --> P10[Phase 10: Backend Engineering]
    P10 --> P11[Phase 11: Frontend Engineering]
    P11 --> P12[Phase 12: Mobile Engineering]
    P12 --> P13[Phase 13: Data Engineering]
    P13 --> P14[Phase 14: Security Engineering]
    P14 --> P15[Phase 15: Observability Engineering]
    P15 --> P16[Phase 16: QA & Validation]
    P16 --> P17[Phase 17: Doc Synchronization]
    P17 --> P18[Phase 18: Deployment Governance]
    P18 --> P19[Phase 19: Self-Healing Validation]
    P19 --> P20[Phase 20: Continuous Optimization]
```

---

## 2. Feature Addition Golden Path

Adding a feature to an existing codebase requires a highly targeted workflow to ensure backward compatibility and prevent regression:

```
[Phase 5: Architecture]  ──► Create detailed ADR & update schema configurations
        │
        ▼
[Phase 16: QA TDD Red]   ──► Write failing Playwright/Vitest test scripts
        │
        ▼
[Phase 10/11: Implement] ──► Implement logic in packages/apps workspace
        │
        ▼
[Phase 16: QA TDD Green] ──► Execute 'rtk test' validation checks
        │
        ▼
[Phase 17: Doc Update]   ──► Sync Obsidian Vault records and update Runbooks
```

---

## 3. SRE Recovery Workflow (Emergency Protocol)

In the event of production crashes or service disruptions, OMEGA initiates a strict recovery protocol:

```mermaid
sequenceDiagram
    participant P as Prometheus Alert
    participant S as SRE Agent
    participant I as Incident Response Agent
    participant K as Kubernetes Cluster
    participant R as Runbook / Vault

    P->>S: Trigger Critical SLO Alert
    S->>I: Initiate Incident Handler
    I->>K: Inspect active pods and query logs (rtk kubectl logs)
    K-->>I: Pod logs with OOM/CrashLoopBackOff
    I->>R: Fetch corresponding recovery SOP (obsidian-vault/15-Runbooks/)
    R-->>I: Runbook details (Scale up, rollback config)
    I->>K: Execute rollback to previous stable version
    K-->>I: Deployment stable
    I->>S: Log Incident Report (obsidian-vault/16-Incidents/)
```

---

## 4. Performance Tuning / Optimization Loop

When high-latency or slow-queries are detected:

1. **Profile**: Run observability checks to locate the bottleneck (e.g., database slow queries, bloated bundles, high-cardinality logging).
2. **Design Patch**: Formulate an optimization patch (e.g., adding index, caching-aside, tree-shaking).
3. **Validate**: Execute automated benchmark tests (`rtk vitest` or k6 load scripts) to prove performance improvements.
4. **Publish**: Deploy the patch, and record results.

---

## 5. Standard Code Cleanup Pipeline (Multi-Stage Cleanup) {#cleanup-pipeline}
> Distilled from `claude-starter`

Before any release build, OMEGA executes a sequential, multi-stage cleanup pipeline to eradicate technical debt and maintain structural sanity.

### Order of Execution (Destructive → Constructive → Cosmetic)
If any step fails, the pipeline halts immediately.

```
[Start: cleanup-all]
        │
        ▼
[Stage 1: unused]     ──► Remove unused imports, dead variables, unreachable code
        │
        ▼
[Stage 2: cycles]     ──► Detect and break circular file/module dependency loops
        │
        ▼
[Stage 3: dedupe]     ──► Merge identical blocks and helper wrappers into shared packages
        │
        ▼
[Stage 4: types]      ──► Elevate weak or 'any' types to strict, documented interfaces
        │
        ▼
[Stage 5: defensive]  ──► Enforce runtime try/catch gates and sanitization layers
        │
        ▼
[Stage 6: legacy]     ──► Upgrade older runtime versions and deprecated patterns
        │
        ▼
[Stage 7: slop]       ──► Format files using biome/prettier and strip verbose logs
```

---

## 6. External Skill Discovery & Installation Policy {#skills-install}
> Distilled from `vercel-labs/skills.git` (find-skills)

To prevent duplication and guarantee reliability, OMEGA uses a strict validation framework before installing or recommending third-party skills.

### Discovery Protocol
If a task requires capabilities not present in OMEGA's native references:
1. Search the marketplace: `npx skills find [query]`.
2. Evaluate trust signals:
   - **Trusted Authors**: `vercel-labs`, `anthropics`, `microsoft`
   - **Quality threshold**: Stars ≥ 100 on the source repository
   - **Install safety**: Preferred install count ≥ 1K (be highly cautious below 100)
3. If trusted, present the command to the user for one-click installation:
   `npx skills add <owner/repo> -g -y`
4. If no reliable ecosystem skill exists, scaffold a custom skill via:
   `npx skills init <skill-name>`
