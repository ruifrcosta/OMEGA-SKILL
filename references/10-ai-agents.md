# AI Agent Engineering Reference

## Table of Contents
1. [AI Agent Decision Tree](#decision-tree)
2. [Context Engineering Systems](#context-engineering)
3. [Memory Governance (Short & Long Term)](#memory-governance)
4. [RAG Orchestration Architecture](#rag-orchestration)
5. [Hallucination Prevention & Prompt Versioning](#hallucination)

---

## 1. AI Agent Decision Tree {#decision-tree}

Avoid implementing AI agents for tasks easily solved with deterministic code. Use this decision tree:

```
Is an AI agent required?
├── Can the task be solved with standard logical rules (if/else, regex, database query)?
│   ├── Yes → Use deterministic code (Zero AI calls).
│   └── No → Does the task require semantic understanding or fuzzy text synthesis?
│       ├── No → Use deterministic code.
│       └── Yes → Does the task demand dynamic multi-turn reasoning and tool use?
│           ├── Yes → Build an **Orchestration Agent** (with tools/subagents).
│           └── No → Build a single-turn **Utility LLM Service** (structured JSON prompt).
```

---

## 2. Context Engineering Systems {#context-engineering}

To minimize token drift, reduce hallucination, and optimize caching, implement structured context layout systems.

```
┌────────────────────────────────────────────────────────┐
│  System Rules & Identity (Constant)                     │
├────────────────────────────────────────────────────────┤
│  Dynamic Context: Workspace State (Cached/Injected)     │
├────────────────────────────────────────────────────────┤
│  Retrieval-Augmented Context (Semantic RAG Snippets)   │
├────────────────────────────────────────────────────────┤
│  User Interaction Message Payload (Volatile History)   │
└────────────────────────────────────────────────────────┘
```

---

## 3. Memory Governance (Short & Long Term) {#memory-governance}

*   **Short-Term Memory**: Conversation history restricted to a sliding window of the last **N** messages, supplemented with sliding recursive summaries.
*   **Long-Term Memory**: Semantic embeddings of documents, facts, or user contexts stored inside vector stores (e.g. Supabase pgvector or Pinecone) and queried as needed.

### LangChain / Custom Memory Ingestion
```python
# lib/memory_service.py
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class KnowledgeSnippet(Base):
    __tablename__ = 'knowledge_snippets'
    
    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    embedding = Column(Vector(1536))  # OpenAI standard dimensions
```

---

## 4. RAG Orchestration Architecture {#rag-orchestration}

OMEGA TITAN mandates a **Hybrid Search** strategy for RAG (Retrieval-Augmented Generation), combining dense vector semantic searches with sparse keyword matches (BM25 / Full-text indexing).

```python
# lib/search_orchestrator.py
def hybrid_search(query: str, limit: int = 5):
    # 1. Fetch dense semantic results via pgvector
    vector_results = db.fetch_vector_matches(query, limit=limit)
    
    # 2. Fetch sparse keyword matches via PostgreSQL full-text search
    keyword_results = db.fetch_fts_matches(query, limit=limit)
    
    # 3. Combine and rank using Reciprocal Rank Fusion (RRF)
    return rrf(vector_results, keyword_results)[:limit]
```

---

## 5. Hallucination Prevention & Prompt Versioning {#hallucination}

1.  **Strict Output Schemas**: Force models to output valid JSON conforming to an explicit Zod schema using structural JSON models.
2.  **Prompt Versioning**: Maintain all prompt templates under VCS control (`apps/api/prompts/`) as raw files and reference them via explicit version IDs (e.g. `PROMPT_WORKSPACE_SUMMARY_V1_2`).
3.  **Assertion Validation**: Filter and sanitize outputs before consumption. If the response violates the schema boundary, reject the step and request a retry.
