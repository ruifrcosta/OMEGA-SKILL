# Token & Cloud Cost Optimization Reference

## Table of Contents
1. [RTK — Token Reduction System](#rtk)
2. [Model Selection Rules](#model-selection)
3. [Context Engineering — Minimize Waste](#context)
4. [Prompt Caching](#caching)
5. [Infrastructure Rightsizing](#infra)
6. [Database & Cache Cost Tactics](#db-cache)
7. [Token Budget Monitoring](#monitoring)

---

## 1. RTK — Token Reduction System {#rtk}

Prefix ALL diagnostic, build, and test commands with `rtk`:

```bash
# Instead of:
npm run build    → rtk npm run build
tsc              → rtk tsc
vitest           → rtk vitest
docker logs      → rtk docker logs

# RTK intercepts output, strips noise, compresses to relevant lines only
# Typical savings: 70–90% token reduction on build/lint output
```

**Rules:**
- Every shell command in a Claude conversation that produces > 10 lines of output uses `rtk`
- Never paste full `tsc`, `docker logs`, or `build` output without `rtk` prefix
- `rtk init -g` to install globally on a new machine

---

## 2. Model Selection Rules {#model-selection}

**Use the smallest model that correctly solves the task.**

| Task | Model |
|------|-------|
| Simple code completion, formatting, renaming | claude-haiku-4 |
| Standard feature development, debugging | claude-sonnet-4-5 |
| Architecture decisions, complex reasoning, system design | claude-opus-4 |
| Batch processing, background jobs | claude-haiku-4 (cheapest per token) |
| Real-time streaming UX (user sees output) | claude-sonnet-4-5 |

**Token budget per call:**
```typescript
// Always set max_tokens based on expected output size
const response = await anthropic.messages.create({
  model: 'claude-sonnet-4-5',
  max_tokens: estimateOutputTokens(task), // never use max (default 4096+ wastes budget)
  messages: [...]
});

function estimateOutputTokens(task: string): number {
  if (task === 'classify') return 50;
  if (task === 'summary') return 300;
  if (task === 'code-small') return 800;
  if (task === 'code-large') return 2000;
  return 1000; // safe default
}
```

---

## 3. Context Engineering — Minimize Waste {#context}

**The 4-layer layout (always this order — enables gateway caching on layers 1–2):**

```
┌─────────────────────────────────────────────────────┐
│  Layer 1: System Rules (CONSTANT — cached)          │
│  Identity, constraints, output format               │
│  Never changes → cached on first call               │
├─────────────────────────────────────────────────────┤
│  Layer 2: Workspace State (SEMI-STABLE — cached)    │
│  Project context, ADRs, tech stack                  │
│  Changes rarely → cache with 1hr TTL               │
├─────────────────────────────────────────────────────┤
│  Layer 3: RAG Context (DYNAMIC — not cached)        │
│  Semantic snippets relevant to this specific request│
│  Retrieve only what this call needs                 │
├─────────────────────────────────────────────────────┤
│  Layer 4: User Message (VOLATILE — never cached)    │
│  The actual question/request                        │
│  Always last                                        │
└─────────────────────────────────────────────────────┘
```

**Compression rules:**
- Never re-send the full file when a diff is enough
- After message 10: summarize messages 1–8, keep 9–10 full
- Semantic truncation: `grep` or line ranges instead of full file dumps
- Dedup: if the same context appears twice in a conversation, reference by name not by value
- State deduplication: strip scratchpad intermediate steps before invoking downstream agents

---

## 4. Prompt Caching {#caching}

```typescript
// Anthropic prompt caching — mark stable content as cacheable
const response = await anthropic.messages.create({
  model: 'claude-sonnet-4-5',
  max_tokens: 1000,
  system: [
    {
      type: 'text',
      text: STATIC_SYSTEM_PROMPT,
      cache_control: { type: 'ephemeral' }  // cache for 5 minutes
    },
    {
      type: 'text',
      text: workspaceContext,               // project-specific, also cacheable
      cache_control: { type: 'ephemeral' }
    }
  ],
  messages: [
    { role: 'user', content: userMessage } // volatile, never cached
  ]
});

// Cache hit indicator — log this to measure savings
console.log('Cache hit:', response.usage.cache_read_input_tokens > 0);
```

**Caching rules:**
- System prompt: always cacheable (never changes within a session)
- Workspace context: cacheable (project docs, ADRs, stack info)
- RAG snippets: not cacheable (different per request)
- User messages: never cached (always volatile)

---

## 5. Infrastructure Rightsizing {#infra}

```bash
# Monthly rightsizing review — run this, review output
kubectl top pods --all-namespaces --sort-by=cpu
kubectl top nodes

# Target: CPU utilization 40–70%, Memory 50–75%
# Below 40% CPU → downsize instance class or reduce replicas
# Above 70% CPU → upsize or scale out horizontally
```

**Cost rules:**
- Dev/staging: auto-pause after 1hr idle (serverless Postgres, scale-to-zero K8s)
- Non-critical batch: spot/preemptible instances (60–80% cheaper)
- CDN: cache aggressively — all static assets, API responses where `Cache-Control` allows
- PgBouncer: always for connection pooling — prevents connection overhead cost
- Cold data: archive to S3/GCS after 90 days (`GLACIER` tier = 10× cheaper)
- Alert: if month-over-month cloud spend increases > 20%, trigger cost review immediately

---

## 6. Database & Cache Cost Tactics {#db-cache}

```
Request
  → Redis (session, metadata) — <5ms, near-zero cost
    → HIT: return immediately
    → MISS: query PostgreSQL
      → Write to Redis (TTL below)
      → Return result

Redis TTL Scale:
  Session tokens:        15 min
  User preferences:      1 hour
  Product catalog:       6 hours
  Config/settings:       24 hours
  Analytics aggregates:  1 hour
```

**Query cost reduction:**
```sql
-- ALWAYS use indexes — verify with EXPLAIN ANALYZE before shipping
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = $1 AND status = 'pending';

-- Cursor pagination instead of OFFSET (OFFSET is O(n) — kills performance at scale)
-- BANNED:
SELECT * FROM orders LIMIT 20 OFFSET 10000;

-- CORRECT:
SELECT * FROM orders WHERE id > $cursor ORDER BY id LIMIT 20;

-- Partial indexes for common filtered queries
CREATE INDEX CONCURRENTLY idx_orders_pending
  ON orders (user_id, created_at)
  WHERE status = 'pending';  -- only indexes the rows we actually query
```

---

## 7. Token Budget Monitoring {#monitoring}

```typescript
// Track token usage per feature — alert on anomalies
interface TokenUsageLog {
  feature: string;
  model: string;
  inputTokens: number;
  outputTokens: number;
  cacheHit: boolean;
  costUsd: number;
  timestamp: Date;
}

// Cost per 1M tokens (approximate — verify current pricing)
const COST_PER_1M: Record<string, { input: number; output: number }> = {
  'claude-haiku-4':   { input: 0.25,  output: 1.25 },
  'claude-sonnet-4-5':  { input: 3.00,  output: 15.00 },
  'claude-opus-4':    { input: 15.00, output: 75.00 },
};

function logTokenUsage(response: Anthropic.Message, feature: string): void {
  const model = response.model;
  const rates = COST_PER_1M[model] ?? { input: 3, output: 15 };
  const cost = (
    (response.usage.input_tokens / 1_000_000) * rates.input +
    (response.usage.output_tokens / 1_000_000) * rates.output
  );

  // Store in analytics DB
  // Alert if cost > $0.10 per single call (anomaly)
  if (cost > 0.10) {
    logger.warn(`High token cost: ${feature} cost $${cost.toFixed(4)}`);
  }
}
```

**Monthly targets:**
- Alert if any single feature costs > $50/month in AI tokens
- Alert if total AI spend increases > 20% month-over-month
- Review: every feature's token usage vs value delivered, monthly
