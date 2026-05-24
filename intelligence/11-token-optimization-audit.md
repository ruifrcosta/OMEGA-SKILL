# OMEGA Token Optimization Audit
## Context Window Efficiency, Prompt Caching, & RTK Command Architectures

This document establishes the token optimization frameworks, prompt caching rules, and context engineering standards enforced across the OMEGA platform.

---

## 1. The Token-First Efficiency Principle

Large context windows degrade LLM performance, increase costs, and introduce hallucinations. OMEGA enforces the **Token-First Efficiency Principle** across all interactions.

```
                  Unoptimized Run:
                  [Large redundant logs] + [Full code files] ──► 80k tokens (High cost/latency)

                  Optimized Run (OMEGA):
                  [rtk log filter] + [rtk read chunks] ──► 12k tokens (Low cost/fast response)
```

---

## 2. RTK Token-Optimized Command Protocols

To keep terminal command output clean and prevent token bloat, all command executions must use the `rtk` prefix.

| Normal Command | RTK Command | Typical Savings | OMEGA Verification Mechanism |
| :--- | :--- | :--- | :--- |
| `cargo clippy` | `rtk cargo clippy` | 80% | Groups warnings by file, removes duplicates |
| `vitest run` | `rtk vitest run` | 99.5% | Limits output to failures and exceptions |
| `tsc` | `rtk tsc` | 83% | Deduplicates TypeScript import errors |
| `git status` | `rtk git status` | 75% | Displays compact tree of changed files |
| `pnpm install` | `rtk pnpm install` | 90% | Limits stdout to installation summaries |

---

## 3. Context & Prompt Caching Rules

Our system structures prompts to maximize cache hits:

1. **Static Prompts First**: System prompts, domain reference files, and standard guidelines are sent first in the payload block, allowing long-term model-level prompt caching.
2. **Dynamic Context Isolation**: Place ephemeral files, terminal outputs, and active conversation logs at the end of the context window to prevent cache invalidation.
3. **Log Filtering**: Never output long stack traces. Use `rtk log <file>` to filter out redundant messages.

---

## 4. Context Extraction Audit Protocol (Read Rules)

When inspecting large files:

- **Banned**: Loading entire files exceeding 1000 lines.
- **Allowed**: Use `rtk read <file>` or `view_file` specifying exact `StartLine` and `EndLine` parameters to extract the target functions.
- **Summary**: Keep long data payloads out of the prompt. Compress telemetry datasets into high-fidelity markdown tables before shipping to subagents.
