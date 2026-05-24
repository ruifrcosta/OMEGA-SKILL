# Token & Implementation Cost Optimization Reference

## Table of Contents
1. [Token Optimization Engine Rules](#token-rules)
2. [Context Engineering & Window Management](#context-window)
3. [Infrastructure Rightsizing & Cost Reduction](#infra-cost)
4. [Ecosystem Database & Caching Tactics](#db-cache)

---

## 1. Token Optimization Engine Rules {#token-rules}

To prevent context drift, minimize API latency, and reduce operating budgets when running autonomous agents, OMEGA TITAN mandates strict token guidelines:

*   **Prefix all Terminal Commands with `rtk`**: Enforce RTK token-optimized filters to achieve up to **90% token reduction** on output payloads (Vitest, Docker, Git, linting).
*   **Compression of Repeated Context**: Never resend complete file structures when executing contiguous updates. Propose compact diff blocks using localized line numbers.
*   **Volatile vs Persistent Memory Separation**: Keep immutable structural definitions (APIs contracts, YAML schemas, base designs) separate from active task-tracking state to leverage prompt caches.

---

## 2. Context Engineering & Window Management {#context-window}

Avoid bloated prompt history through sliding context compression:

```
Step 1: Raw Interaction (Message History 1-10)
┌────────────────────────────────────────────────────────┐
│  Full Message Payload & Tool Outputs                    │
└────────────────────────────────────────────────────────┘

Step 2: Context Compression (Triggered at Step 11+)
┌────────────────────────────────────────────────────────┐
│  Compact Recursive Summary (Steps 1-9)                 │
├────────────────────────────────────────────────────────┤
│  Full Message Payload (Step 10)                        │
└────────────────────────────────────────────────────────┘
```

### Context Compression Pipeline Guidelines
1.  **Semantic Truncation**: When querying logs or long terminal outputs, extract matching subsets (`grep` or target line arrays) rather than returning full spans.
2.  **State Deduplication**: Eliminate intermediate scratchpad steps from the persistent memory context before invoking downstream agents.

---

## 3. Infrastructure Rightsizing & Cost Reduction {#infra-cost}

Platform deployments require strict cost reviews:

*   **Instance Rightsizing**: Maintain average CPU utilization of production workloads between **40% and 70%**. Shrink or split underutilized node instances.
*   **Kubernetes Autoscaling**: Enable Horizontal Pod Autoscalers (HPA) to scale up only under load spike gates, dynamically terminating containers during quiet intervals.
*   **Database Idle-State Invalidation**: Non-production databases (development, staging environments) must automatically pause operations when idle for more than **1 hour** (e.g. Serverless PostgreSQL configurations).

---

## 4. Ecosystem Database & Caching Tactics {#db-cache}

Avoid expensive transactional database connections and unnecessary computation pipelines through multi-tier caching:

```
1. Client Request
   ├── 2. Query Redis Cache (Metadata & Session)
   │   ├── Hit  → Return Payload (Fast: <5ms)
   │   └── Miss → 3. Query PostgreSQL DB (Cardinality Index)
   │                  ├── Write to Redis Cache (TTL: 15m)
   │                  └── Return Data
```

### Redis Key Lifecycle (TTL Scale)
*   **Session Metadata Keys**: TTL **15 minutes**.
*   **Design Token & Settings Configuration Keys**: TTL **24 hours**.
*   **Calculated Report Keys**: TTL **1 hour**.
