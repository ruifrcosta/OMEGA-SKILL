# ADR-0005: Database & Deployment Infrastructure Governance

## Status
Accepted

## Deciders
- OMEGA Architecture Office
- CTO Agent
- Infrastructure / DevOps Agent

## Context
Deployments and database operations in legacy structures (`vercel-*`, `planetscale-skills`, etc.) were executed ad-hoc, with raw Vercel tokens passed in command line arguments (introducing high security leaks to shell logs), direct production pushes without preview gates, non-monotonic primary keys in high-write transactional MySQL tables (causing severe B-tree page splits), and unmeasured, unindexed query patterns that resulted in high latency.

To harden our infrastructure and achieve Big Tech delivery standards, we must establish strict deployment pipelines and relational database engineering standards.

## Decision
We enforce the following operational rules across all OMEGA infrastructure deployments:

### 1. Database Engineering Standards (MySQL / PlanetScale)
- **Monotonic Clustered PKs**: All high-transaction transactional tables must utilize narrow, monotonic Primary Keys (`BIGINT UNSIGNED AUTO_INCREMENT`). Random UUID values are strictly banned as clustered PKs (if needed, store them in secondary indexed `VARCHAR/BINARY` columns).
- **Encoding & collation**: Databases must strictly utilize `utf8mb4` with the `utf8mb4_0900_ai_ci` collation.
- **Index Order Constraint**: All composite indexes must place equality columns first, followed by range/sorting columns (leftmost prefix rule).
- **Data Integrity**: Prefer `NOT NULL` columns over nullable fields. Use lookup tables over inline database `ENUM` types.
- **DDL Execution Safety**: Destructive migrations (drops, table truncates) must receive explicit Architecture Office sign-off. Production migrations must utilize online schema migrations (`ALGORITHM=INPLACE` or PlanetScale non-blocking schema branches).

### 2. Deployment Governance (Vercel Core)
- **Zero Token Leakage**: The `VERCEL_TOKEN` must strictly be injected as a secure environment variable. Passing `--token` directly in CLI scripts is banned to prevent shell history compromise.
- **Preview Isolation Gate**: All deployments must default to `preview` environments. Pushes to `production` are banned unless explicitly approved by the PMO and SRE agents, or executed through approved CI/CD branch merges.
- **Monorepo Links**: Monorepos must be linked via `vercel link --repo` (tying Vercel deployments directly to git remote structures) instead of name-based directory links.

## Consequences
### Positive
- **Mitigated Key Leakage**: Passing secrets via environmental injection ensures clean, uncompromised CI/CD process listings.
- **Optimized DB Read/Write Paths**: Monotonic primary keys eliminate page splits, and leftmost composite prefix matching guarantees fast indexing.
- **Reduced Staging Drift**: Automatic preview builds prevent untested code from reaching user-facing environments.

### Negative
- **Initial Setup Rigor**: Linking monorepo pipelines and setting environment variables manually on the CLI takes more bootstrap effort.
