# AI Agent Engineering Reference

## Table of Contents
1. [Decision Tree — When to Build an Agent](#decision)
2. [Context Architecture — 4 Layers](#context)
3. [LangGraph — Stateful Orchestration](#langgraph)
4. [Memory: Short-Term + Long-Term (pgvector)](#memory)
5. [RAG — Hybrid Search (Dense + Sparse)](#rag)
6. [MCP Integration (Model Context Protocol)](#mcp)
7. [Prompt Engineering & Versioning](#prompts)
8. [Output Validation & Hallucination Prevention](#validation)
9. [Cost & Token Governance](#cost)
10. [Troubleshooting Playbook](#troubleshooting)

---

## 1. Decision Tree — When to Build an Agent {#decision}

```
Problem needs solving?
│
├─ Can if/else, regex, or a DB query solve it?
│   YES → deterministic code. Zero LLM calls.
│
├─ Needs semantic understanding or text synthesis?
│   NO  → still deterministic code
│   YES →
│       ├─ Single operation, no tool use?
│       │   YES → single-turn Utility LLM (one call, structured JSON out)
│       │
│       └─ Multi-step reasoning OR tool use needed?
│           YES →
│               ├─ State across turns? Cross-session memory?
│               │   NO  → stateless orchestration (LangGraph, no memory store)
│               │   YES → stateful agent (LangGraph + pgvector memory)
│               │
│               └─ Coordinates other agents?
│                   YES → build orchestration layer (supervisor pattern)
```

**Default bias:** always try the simpler option first. An agent that uses 5 LLM calls
where 1 would suffice is architectural waste.

---

## 2. Context Architecture — 4 Layers {#context}

**Always this order. Static content at the top (cached). Volatile at the bottom.**

```
┌─────────────────────────────────────────────────────┐
│ Layer 1: System Rules + Identity       [STATIC]      │ ← cache_control: ephemeral
│   identity, rules, tool definitions                  │
├─────────────────────────────────────────────────────┤
│ Layer 2: Workspace State               [SEMI-STATIC] │ ← cache when possible
│   org config, user profile, feature flags            │
├─────────────────────────────────────────────────────┤
│ Layer 3: RAG Context                   [DYNAMIC]     │ ← top-K retrieved chunks
│   semantic search results, relevant docs             │
├─────────────────────────────────────────────────────┤
│ Layer 4: Conversation + User Message   [VOLATILE]    │ ← never cache
│   message history (sliding window), current input   │
└─────────────────────────────────────────────────────┘
```

**Prompt caching saves up to 90% on static layers.** Break the system prompt at the
static/dynamic boundary and mark the static portion with `cache_control: {type: ephemeral}`.

---

## 3. LangGraph — Stateful Orchestration {#langgraph}

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    messages:     Annotated[list, operator.add]  # append-only
    workspace_id: str
    phase:        str
    tool_results: dict
    error_count:  int
    output:       str | None

async def plan(state: AgentState) -> AgentState:
    plan = await llm.ainvoke(PLAN_PROMPT.format(messages=state["messages"]))
    return {"phase": "planning", "messages": [plan]}

async def execute(state: AgentState) -> AgentState:
    results = await tool_executor.abatch(state["tool_results"])
    return {"tool_results": results, "phase": "executing"}

async def validate(state: AgentState) -> AgentState:
    parsed = OutputSchema.model_validate_json(state["tool_results"].get("raw", ""))
    return {"output": parsed.model_dump_json(), "phase": "done"}

def should_retry(state: AgentState) -> str:
    if state["error_count"] > 3: return "fail"
    if state["output"]:          return END
    return "execute"

graph = StateGraph(AgentState)
graph.add_node("plan",     plan)
graph.add_node("execute",  execute)
graph.add_node("validate", validate)
graph.set_entry_point("plan")
graph.add_edge("plan", "execute")
graph.add_edge("execute", "validate")
graph.add_conditional_edges("validate", should_retry, {END: END, "execute": "execute", "fail": END})
app = graph.compile()
```

---

## 4. Memory: Short-Term + Long-Term {#memory}

### Short-term: sliding window + recursive summarization
```python
MAX_MESSAGES    = 20
SUMMARY_TRIGGER = 16

async def compress_context(messages: list, llm) -> list:
    if len(messages) < SUMMARY_TRIGGER:
        return messages

    old, recent = messages[:-8], messages[-8:]
    summary = await llm.ainvoke(
        "Summarize these turns preserving all decisions, requirements, and constraints:\n"
        + "\n".join(f"{m['role']}: {m['content']}" for m in old)
    )
    return [{"role": "system", "content": f"[Prior context]: {summary.content}"}] + recent
```

### Long-term: pgvector (Supabase)
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE agent_memory (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id TEXT NOT NULL,
  content      TEXT NOT NULL,
  embedding    vector(1536),
  metadata     JSONB DEFAULT '{}',
  created_at   TIMESTAMPTZ DEFAULT now()
);

-- HNSW index (faster than IVFFlat at production scale)
CREATE INDEX ON agent_memory USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- RLS: workspace isolation mandatory
ALTER TABLE agent_memory ENABLE ROW LEVEL SECURITY;
CREATE POLICY workspace_isolation ON agent_memory
  USING (workspace_id = current_setting('app.workspace_id'));
```

---

## 5. RAG — Hybrid Search {#rag}

**Always hybrid. Pure vector search misses exact matches. Pure BM25 misses semantics.**

```python
async def hybrid_search(query: str, workspace_id: str, limit: int = 5) -> list:
    embedding = await embed(query)  # text-embedding-3-small

    # Dense: vector similarity
    vector_results = await supabase.rpc("match_memory", {
        "query_embedding": embedding,
        "match_count": limit * 2,
        "workspace_id": workspace_id,
    }).execute()

    # Sparse: full-text search
    fts_results = await supabase.table("agent_memory") \
        .select("*").text_search("content", query, config="english") \
        .eq("workspace_id", workspace_id).limit(limit * 2).execute()

    # Fuse with Reciprocal Rank Fusion
    return rrf([vector_results.data, fts_results.data])[:limit]

def rrf(result_sets: list, k: int = 60) -> list:
    scores = {}
    for result_set in result_sets:
        for rank, doc in enumerate(result_set):
            did = doc["id"]
            if did not in scores: scores[did] = {"doc": doc, "score": 0}
            scores[did]["score"] += 1.0 / (k + rank + 1)
    return sorted(scores.values(), key=lambda x: x["score"], reverse=True)
```

---

## 6. MCP Integration {#mcp}

```python
# Server-side: FastMCP
from fastmcp import FastMCP

mcp = FastMCP("omega-workspace")

@mcp.tool()
async def get_workspace_context(workspace_id: str) -> dict:
    """Retrieve workspace context: active sprint, recent ADRs, system health."""
    return {
        "active_sprint": await get_active_sprint(workspace_id),
        "recent_adrs":   await get_recent_adrs(workspace_id, limit=5),
        "health":        await get_health(workspace_id),
    }

if __name__ == "__main__":
    mcp.run()
```

```typescript
// Client-side: Claude API with MCP
const response = await anthropic.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 4096,
    mcp_servers: [{ type: "url", url: process.env.MCP_URL, name: "omega-workspace" }],
    messages: [{ role: "user", content: userMessage }],
});
```

---

## 7. Prompt Engineering & Versioning {#prompts}

```
apps/api/prompts/
├── workspace-summary/
│   ├── v1.0.txt   # original
│   ├── v1.1.txt   # improved classification
│   └── v2.0.txt   # current (structured JSON output)
└── code-review/
    └── v1.0.txt
```

```typescript
// NEVER inline prompts in code
const prompt = await loadPrompt('workspace-summary', 'v2.0');

// ALWAYS reference by version ID
const PROMPT_ID = 'workspace-summary:v2.0';
```

**Prompt caching (Anthropic) — mark static sections:**
```python
messages = [{
    "role": "user",
    "content": [
        {
            "type": "text",
            "text": LARGE_STATIC_DOCUMENT,
            "cache_control": {"type": "ephemeral"},  # cached
        },
        { "type": "text", "text": user_dynamic_query }  # not cached
    ]
}]
```

---

## 8. Output Validation {#validation}

```typescript
// Zod schema + retry on validation failure
const ADRSchema = z.object({
  title:    z.string().min(5).max(100),
  status:   z.enum(['proposed', 'accepted', 'deprecated', 'superseded']),
  context:  z.string().min(50),
  decision: z.string().min(50),
  consequences: z.object({
    positive: z.array(z.string()),
    negative: z.array(z.string()),
    risks:    z.array(z.string()),
  }),
});

async function generateADR(context: string, retries = 2): Promise<z.infer<typeof ADRSchema>> {
  const response = await anthropic.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 2000,
    system: "Output ONLY valid JSON matching the ADR schema. No markdown, no preamble.",
    messages: [{ role: "user", content: context }],
  });

  try {
    return ADRSchema.parse(JSON.parse(response.content[0].text));
  } catch (e) {
    if (retries > 0) return generateADR(context + "\n\nPrevious attempt failed validation. Fix and retry.", retries - 1);
    throw new AgentOutputError(`ADR validation failed after retries: ${e}`);
  }
}
```

---

## 9. Cost & Token Governance {#cost}

```typescript
const DAILY_BUDGET: Record<string, number> = {
  free:       50_000,
  pro:        500_000,
  enterprise: 5_000_000,
};

async function checkBudget(workspaceId: string, estimatedTokens: number): Promise<void> {
  const today  = new Date().toISOString().split('T')[0];
  const key    = `token_budget:${workspaceId}:${today}`;
  const used   = await redis.incrby(key, estimatedTokens);
  if (used === estimatedTokens) await redis.expire(key, 86400);

  const plan   = await getWorkspacePlan(workspaceId);
  const budget = DAILY_BUDGET[plan];

  if (used > budget) throw new TokenBudgetError(`Daily budget of ${budget} tokens exceeded`);
  if (used / budget > 0.8) await notifyBudgetWarning(workspaceId, used / budget);
}
```

**Model routing:**
```typescript
function selectModel(task: TaskType): string {
  const routing: Record<TaskType, string> = {
    classification:    'claude-haiku-4-5-20251001',
    extraction:        'claude-haiku-4-5-20251001',
    summarization:     'claude-haiku-4-5-20251001',
    code_generation:   'claude-sonnet-4-20250514',
    agent_task:        'claude-sonnet-4-20250514',
    architecture:      'claude-opus-4-20250514',
    complex_debugging: 'claude-opus-4-20250514',
  };
  return routing[task] ?? 'claude-sonnet-4-20250514';
}
```

---

## 10. Troubleshooting Playbook {#troubleshooting}

### Agent loops indefinitely
```
Cause: no termination condition OR LLM keeps calling same tool
Fix:
1. Add error_count to state; throw after max_retries (3)
2. Add tool_call_history to state; detect repeated identical calls
3. Set max_steps in LangGraph: graph.compile(checkpointer=...) with step limit
```

### Context window overflow mid-conversation
```
Cause: conversation history not being summarized
Fix: implement compress_context() — summarize old turns when len > SUMMARY_TRIGGER
Monitor: log token counts per call; alert when approaching 80% of context limit
```

### RAG returns irrelevant results
```
Diagnosis:
1. Check embedding model matches between indexing and query time
2. Run hybrid_search separately — which result set is failing?
3. Print similarity scores — if all < 0.5, chunks may be too large

Fix:
- Optimal chunk size: 256-512 tokens with 50-token overlap
- Use metadata filtering before vector search (workspace_id, doc_type)
- Add reranking step (cross-encoder) for precision-critical use cases
```

### Prompt injection detected
```python
INJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"you\s+are\s+now\s+(?:a|an)",
    r"disregard\s+(?:all|your)",
    r"system\s+prompt",
    r"<\s*script",
]

def sanitize_input(text: str, max_length: int = 4000) -> str | None:
    text = text[:max_length]
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning(f"Injection attempt: {pattern}")
            return None  # reject entirely
    return text.strip()
```

### Tool call fails silently
```
Most common causes:
1. Tool returns None/null — LangGraph treats as success
2. Exception swallowed inside tool — add explicit try/catch that raises
3. Tool schema mismatch — validate input against Pydantic model at entry

Fix: all tools should raise ToolExecutionError on failure, never return None
```
