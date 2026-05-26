# OMEGA Memory Bank & Project Persistence System
> Distilled from the expert Cline's Memory Bank pattern

This document formalizes the memory structures and state persistence framework used by OMEGA to maintain continuity across stateless runtime sessions.

---

## 1. The Core Memory Bank Architecture
To prevent context drift and eliminate file volume bloat (solving the 200-file ZIP limit), OMEGA condenses all project memory into **6 Core Markdown Files** stored inside the project workspace directory under `memory-bank/`.

```
        ┌────────────────────────────────────────────────────────┐
        │                 projectbrief.md                        │
        │           (Foundation & Project Scope)                 │
        └──────────────────────────────────────────┬─────────────┘
                                                   │
                         ┌─────────────────────────┼─────────────────────────┐
                         ▼                         ▼                         ▼
              ┌────────────────────┐    ┌────────────────────┐    ┌────────────────────┐
              │  productContext.md │    │  systemPatterns.md │    │   techContext.md   │
              │  (Why & UX Goals)  │    │  (Architecture)    │    │ (Tech & Tooling)   │
              └──────────┬─────────┘    └──────────┬─────────┘    └──────────┬─────────┘
                         │                         │                         │
                         └─────────────────────────┼─────────────────────────┘
                                                   ▼
                                        ┌────────────────────┐
                                        │  activeContext.md  │
                                        │ (Focus & Decisions)│
                                        └──────────┬─────────┘
                                                   ▼
                                        ┌────────────────────┐
                                        │    progress.md     │
                                        │ (Todo & Statuses)  │
                                        └────────────────────┘
```

---

## 2. Core Files Specifications

### 1. `projectbrief.md` (The Scope Source of Truth)
- **Role**: Defines the fundamental requirements, core objectives, and explicit scope boundaries of the project.
- **Updated when**: Project scope changes or new major features are authorized.

### 2. `productContext.md` (The Product Vision)
- **Role**: Explains *why* the project exists, what specific problems it solves, how it should work flow-wise, and the targeted UX experience.
- **Updated when**: User persona profiles shift, or product workflows are redesigned.

### 3. `systemPatterns.md` (System Architecture)
- **Role**: Maps out the system architecture, component relationships, key design patterns (e.g. Hexagonal, CQRS), and critical implementation paths.
- **Updated when**: New technology adapters are added, or structural patterns evolve.

### 4. `techContext.md` (Technology Stack & Constraints)
- **Role**: Documents the precise technologies used (Node version, DB engine), the development setup configuration, constraints, and tool usage rules.
- **Updated when**: Dependency versions are upgraded or new packages are introduced.

### 5. `activeContext.md` (Active Focus & Learnings)
- **Role**: Tracks the immediate work focus, recent modifications, next operational steps, active design considerations, and session-specific learnings.
- **Updated when**: Every major task completion or session initialization.

### 6. `progress.md` (Visual Todo & Status Log)
- **Role**: Visual representation of project completion. Contains completed items, tasks in progress, remaining checklist items, known bugs, and the evolutionary history of design decisions.
- **Updated when**: Any milestone is achieved or task status transitions.

---

## 3. The Boot & Read Protocol (Stateless Persistence)
At the start of **every session or task initialization**, OMEGA executes the **Memory Bank Sync**:

1. **Verify Existence**: Check if the `memory-bank/` directory exists in the workspace. If not, scaffold it immediately with empty templates based on the 6 core files.
2. **Atomic Read**: Read **ALL 6 core files** before executing any commands or writing code. Announce: `[MEMORY BANK SYNC ACTIVE] — Resyncing project history`.
3. **Detect Drifts**: Compare current workspace files against `progress.md` and `activeContext.md` to identify external modifications.
4. **Task Alignment**: Read the immediate target checklist from `progress.md` to guarantee alignment.

---

## 4. Updates & Verification Rules
The Memory Bank files are live documents. OMEGA must update them:
- Immediately after implementing any significant structural change.
- When new system patterns are identified.
- When explicitly requested via the command **"update memory bank"** (triggers a full review of all 6 files).
- At the end of every user prompt cycle to keep `activeContext.md` and `progress.md` synchronized.
- **Rule**: Never print empty placeholders inside context files. Every document must contain high-fidelity, dated state records.

---

## 5. One-Question-with-Opinionated-Default Protocol (Anti-Loop Gate)
To prevent the agent from stalling in perpetual clarification loops:
1. **Analyze Stack**: Automatically detect the current tech stack using a Phase 0 scan on `package.json`, `Cargo.toml`, or `go.mod`.
2. **Draft Solution**: When facing architectural design questions, OMEGA drafts a single, highly opinionated, optimized solution conforming to the tech stack.
3. **Ask & Act**: Present the proposed solution with a clear **Default Choice** that the user can accept silently.
4. **Advance**: If the user does not reject the proposal in their next response, OMEGA assumes implicit consent and implements it immediately.
