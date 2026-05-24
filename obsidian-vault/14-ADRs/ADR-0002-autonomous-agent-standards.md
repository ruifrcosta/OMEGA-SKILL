# ADR-0002: Autonomous Agent Creation and Orchestration Standards

## Status
Accepted

## Deciders
- OMEGA Architecture Office
- CTO Agent

## Context
OMEGA requires a strictly governed, multi-agent orchestration architecture to handle complex software engineering capabilities. Historically, the agent landscape was highly fragmented (e.g., disparate tools inside `.agents`, `agent-development`, `coding-agent`, etc.), leading to duplicated prompts, divergent trigger mechanisms, and inconsistent model utilization.

To establish OMEGA as a Big Tech-grade Autonomous Engineering Operating System, we must formalize the standards for creating, validating, and triggering autonomous subagents, ensuring consistency across the entire 33-Folder Obsidian organizational memory vault and all runtime execution contexts.

## Decision
We establish the **OMEGA Autonomous Agent Forge Protocol**, dictating that all autonomous agents must strictly adhere to the following architectural constraints:

### 1. Agent Metadata (Frontmatter)
Every agent configuration must include a YAML frontmatter block defining:
- `name`: Must be lowercase, hyphenated, and alphanumeric (e.g., `security-agent`).
- `description`: The core triggering condition. Must include explicit `<example>` blocks mapping `Context`, `user`, `assistant`, and `<commentary>`.
- `model`: Must default to `inherit` to optimize token costs and leverage the orchestrator's active session, unless a specific model (e.g., `opus` or `haiku`) is architecturally justified.
- `color`: Must correspond to the agent's domain (e.g., `blue` for analysis, `red` for security, `green` for operations).
- `tools`: Must adhere to the **Principle of Least Privilege**.

### 2. System Prompt Governance
The agent's system prompt (the markdown body) must:
- Be written in the second person ("You are the OMEGA Security Agent...").
- Define a clear **Analysis Process** (step-by-step logic).
- Specify explicit **Output Formats** (JSON, Markdown, CLI commands).
- Include comprehensive **Edge Case** handling.
- Be stored permanently within `obsidian-vault/24-Agent-Orchestration/`.

### 3. Orchestration Centralization
- OMEGA is the **ONLY** root orchestration layer.
- Subagents cannot spawn other subagents unless authorized by the OMEGA Workflow system.
- Legacy standalone scripts inside `.agents` or `agent-development` are deprecated and subsumed by this architecture.

## Consequences
### Positive
- **Reduced Token Waste**: Defaulting to `inherit` and enforcing concise system prompts lowers operational costs.
- **Predictable Behavior**: Strict system prompt templating eliminates AI hallucination and fragmented execution.
- **Unified Governance**: Centralizing definitions inside `obsidian-vault/24-Agent-Orchestration` ensures the Architecture Office has full oversight over AI execution.

### Negative
- **Initial Migration Cost**: Translating all legacy fragmented agents to this strict protocol requires manual extraction and auditing (handled in OMEGA implementation batches).
