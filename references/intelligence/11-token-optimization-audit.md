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

---

## 5. TOON Array Optimization Format {#toon-format}
> Distilled from `claude-starter/Codex-starter`

To save 30-50% on token consumption for large arrays of structured JSON (such as file lists, API route mappings, database logs, and model registries), OMEGA utilizes the **TOON (Token-Optimized Object Notation)** compact serialization format.

### Serialization Example:
- **Standard JSON (120 tokens)**:
```json
[
  {"method": "GET", "path": "/api/users", "auth": "required"},
  {"method": "POST", "path": "/api/users", "auth": "required"},
  {"method": "GET", "path": "/api/health", "auth": "none"}
]
```
- **TOON Format (70 tokens — 40%+ savings)**:
```
[3]{method,path,auth}:
GET,/api/users,required
POST,/api/users,required
GET,/api/health,none
```

### TOON Encoding/Decoding Commands:
- `/analyze-tokens` - Analyze current conversation for token-heavy JSON blocks.
- `/convert-to-toon` - Convert raw JSON block at clipboard or prompt to TOON.
- `/toon-encode` / `/toon-decode` - Programmatic translation on file contents.
- `/toon-validate` - Perform syntax verification on TOON structures.

---

## 6. Dynamic Terminal State Window Title Auto-Update {#terminal-title}
> Distilled from `bluzername/claude-code-terminal-title.git`

In multi-terminal or multi-session workflows (such as parallel multi-agent orchestration), OMEGA auto-updates the terminal title to reflect the current active task state. This prevents context confusion for both the human developer and automated orchestration agents.

### ANSI Escape Output Protocol
Each time a major task or phase starts, emit the ANSI title escape code:
```bash
# macOS/Linux standard terminals:
echo -ne "\033]0;[Folder] | [Task-Verb: Target]\007"
```

### Task Verb Classification:
- **`Debug: [API/DB]`**: For active diagnostics or log traces.
- **`Build: [Feature]`**: For writing active component code.
- **`Test: [Suite]`**: For running unit/E2E test pipelines.
- **`Fix: [Issue]`**: For applying refactors or security hardening.
- **`Deploy: [Env]`**: For infrastructure provisioning and migrations.
