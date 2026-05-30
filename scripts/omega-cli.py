#!/usr/bin/env python3
"""
OMEGA CLI — Vault Discovery, Initialization & Audit Tool
=========================================================
Never assumes a fixed path. Always discovers the repository root
and the documentation folder before acting.

Usage:
  python omega-cli.py resolve-vault          # Print the resolved vault path
  python omega-cli.py init-vault             # Discover or create docs/vault
  python omega-cli.py create-adr --title "..." [--status ...] [--deciders "..."]
  python omega-cli.py audit                  # Security + compliance scan
  python omega-cli.py status                 # Vault health report
"""

import os
import sys
import json
import argparse
import datetime
import subprocess
from pathlib import Path

# Force stdout and stderr to use UTF-8 encoding to avoid Windows console errors
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

VAULT_FOLDERS = [
    '00-Executive', '01-Architecture', '02-Product', '03-Infrastructure',
    '04-Frontend', '05-Backend', '06-Mobile', '07-AI', '08-Data',
    '09-Security', '10-Observability', '11-Design-System', '12-RBAC',
    '13-Sprints', '14-ADRs', '15-Runbooks', '16-Incidents', '17-Diagrams',
    '18-Knowledge-Graph', '19-Standards', '20-QA', '21-Compliance',
    '22-Token-Optimization', '23-Cost-Optimization', '24-Agent-Orchestration',
    '25-Platform-Engineering', '26-Workflow-Systems', '27-Developer-Experience',
    '28-Disaster-Recovery', '29-Audit-Logs', '30-Kubernetes', '31-MCP',
    '32-AI-Memory', '33-Architecture-Recovery',
]

FOLDER_DESCRIPTIONS = {
    '00-Executive':            'Vision, OKRs, roadmap, business goals',
    '01-Architecture':         'System blueprints, bounded contexts, DDD maps, event catalog',
    '02-Product':              'User stories, personas, feature flags, requirements',
    '03-Infrastructure':       'Cloud topology, network diagrams, DNS, DR policies',
    '04-Frontend':             'Component library, Web Vitals budgets, state designs',
    '05-Backend':              'API contracts, service catalog, database ERDs, queues',
    '06-Mobile':               'Expo configs, OTA updates, offline-first patterns',
    '07-AI':                   'Agent catalog, prompt library, token budgets, RAG configs',
    '08-Data':                 'Event streams, ETL DAGs, ML schemas, data catalog',
    '09-Security':             'Threat models, CORS/CSP rules, IAM, pentest reports',
    '10-Observability':        'SLOs, Prometheus alerts, Grafana dashboards, OTel configs',
    '11-Design-System':        'Design tokens, typography scales, component patterns',
    '12-RBAC':                 'Role definitions, permission matrix, access audit log',
    '13-Sprints':              'Sprint plans, retrospectives, delivery logs',
    '14-ADRs':                 'Architectural Decision Records — every significant WHY',
    '15-Runbooks':             'Operational procedures, deploy steps, incident response',
    '16-Incidents':            'Post-mortems, resolution timelines, root cause analysis',
    '17-Diagrams':             'Mermaid source files: C4, ERD, sequence, flowchart',
    '18-Knowledge-Graph':      'Cross-domain concept maps, tag registry, ontology',
    '19-Standards':            'Coding standards, git conventions, API style guide',
    '20-QA':                   'Test strategy, E2E coverage reports, load test results',
    '21-Compliance':           'ISO 27001, SOC 2, GDPR registry, audit evidence',
    '22-Token-Optimization':   'Prompt caching benchmarks, context compression logs',
    '23-Cost-Optimization':    'Cloud spend analysis, rightsizing reports, FinOps',
    '24-Agent-Orchestration':  'LangGraph flows, subagent contracts, orchestration maps',
    '25-Platform-Engineering': 'CI/CD pipelines, internal developer platform, Turborepo',
    '26-Workflow-Systems':     'Automation playbooks, GWS recipes, webhook logs',
    '27-Developer-Experience': 'Onboarding guide, local bootstrap, DX tooling',
    '28-Disaster-Recovery':    'Failover procedures, backup schedules, RTO/RPO records',
    '29-Audit-Logs':           'Security access logs, deploy audit trail, compliance events',
    '30-Kubernetes':           'Namespace registry, Helm charts, autoscaling configs',
    '31-MCP':                  'Model Context Protocol servers, tool definitions',
    '32-AI-Memory':            'Persistent memory schemas, vector DB configs, agent history',
    '33-Architecture-Recovery':'Drift detection, legacy migration maps, recovery procedures',
}

# ─────────────────────────────────────────────────────────────────────────────
# REPOSITORY & VAULT DISCOVERY
# ─────────────────────────────────────────────────────────────────────────────

def find_repo_root(start: Path) -> Path:
    """
    Walk up from start until we find a .git directory or reach filesystem root.
    Falls back to start if no .git is found (monorepo edge case).
    """
    current = start.resolve()
    while True:
        if (current / '.git').exists():
            return current
        parent = current.parent
        if parent == current:          # reached filesystem root
            return start.resolve()     # fall back gracefully
        current = parent


def find_existing_docs_folder(repo_root: Path) -> Path | None:
    """
    Search the repo root for an existing documentation folder.
    Priority order:
      1. docs/           (GitHub Pages standard, most common)
      2. documentation/
      3. wiki/
      4. .docs/
      5. obsidian-vault/ (legacy OMEGA — still honour it)
    Returns the Path if found, None otherwise.
    """
    candidates = ['docs', 'documentation', 'wiki', '.docs', 'obsidian-vault']
    for name in candidates:
        candidate = repo_root / name
        if candidate.is_dir():
            return candidate
    return None


def is_omega_vault(folder: Path) -> bool:
    """Return True if this folder looks like an OMEGA vault (has numbered sub-folders)."""
    if not folder.is_dir():
        return False
    children = [d.name for d in folder.iterdir() if d.is_dir()]
    omega_markers = [f for f in children if f.startswith(('00-', '01-', '14-ADRs', '15-Runbooks'))]
    return len(omega_markers) >= 3


def resolve_vault_path(cwd: Path | None = None) -> tuple[Path, str]:
    """
    Master vault resolution algorithm. Returns (vault_path, resolution_reason).

    Decision tree:
      1. OMEGA_VAULT_PATH env var set → use it directly
      2. Find repo root via .git walk-up
      3. If existing docs/ folder contains OMEGA vault → use docs/vault/ subfolder
      4. If existing docs/ folder exists (not OMEGA) → use docs/vault/ inside it
      5. If no docs/ exists → create docs/vault/ at repo root
      6. If no .git found (not a repo) → use cwd/docs/vault/
    """
    if cwd is None:
        cwd = Path.cwd()

    # 1. Explicit override
    env_path = os.environ.get('OMEGA_VAULT_PATH', '').strip()
    if env_path:
        return Path(env_path).resolve(), 'env:OMEGA_VAULT_PATH'

    # 2. Find repo root
    repo_root = find_repo_root(cwd)

    # 3–5. Discover or determine docs folder
    existing_docs = find_existing_docs_folder(repo_root)

    if existing_docs is not None:
        vault_inside = existing_docs / 'vault'
        # If the docs folder IS already an OMEGA vault (legacy obsidian-vault/)
        if is_omega_vault(existing_docs):
            return existing_docs, f'existing-omega-vault:{existing_docs.relative_to(repo_root)}'
        # If there's already a vault/ subfolder inside docs/
        if vault_inside.is_dir() and is_omega_vault(vault_inside):
            return vault_inside, f'existing-docs-vault:{vault_inside.relative_to(repo_root)}'
        # docs/ exists but no vault yet — nest vault/ inside it
        return vault_inside, f'new-inside-existing-docs:{vault_inside.relative_to(repo_root)}'

    # 5. No docs folder found — create docs/vault/ at repo root
    vault_path = repo_root / 'docs' / 'vault'
    return vault_path, f'new-docs-vault:{vault_path.relative_to(repo_root)}'


# ─────────────────────────────────────────────────────────────────────────────
# OBSIDIAN CONFIG
# ─────────────────────────────────────────────────────────────────────────────

OBSIDIAN_APP_JSON = """{
  "readableLineLength": false,
  "propertiesInDocument": "hidden",
  "livePreview": true,
  "promptDelete": false,
  "defaultViewMode": "preview",
  "showInlineTitle": false,
  "strictLineBreaks": true
}"""

OBSIDIAN_APPEARANCE_JSON = """{
  "accentColor": "#ffaf1a",
  "cssTheme": "Vicious",
  "theme": "obsidian",
  "baseFontSize": 11,
  "enabledCssSnippets": [
    "MCL Multi Column",
    "Heatmap Calendar",
    "MCL Gallery Cards",
    "MCL Wide Views",
    "minimal-cards_anu",
    "omega-theme"
  ],
  "translucency": true
}"""

OBSIDIAN_GRAPH_JSON = """{
  "collapse-filter": false,
  "search": "",
  "showTags": true,
  "showAttachments": true,
  "hideUnresolved": true,
  "showOrphans": true,
  "collapse-color-groups": false,
  "colorGroups": [
    { "query": "tag:#adr",       "color": { "a": 1, "rgb": 16760576 } },
    { "query": "tag:#security",  "color": { "a": 1, "rgb": 16711680 } },
    { "query": "tag:#incident",  "color": { "a": 1, "rgb": 16744272 } },
    { "query": "tag:#runbook",   "color": { "a": 1, "rgb": 5025613  } },
    { "query": "tag:#sprint",    "color": { "a": 1, "rgb": 5592575  } },
    { "query": "tag:#memory",    "color": { "a": 1, "rgb": 10066329 } }
  ],
  "collapse-display": false,
  "showArrow": false,
  "textFadeMultiplier": 0,
  "nodeSizeMultiplier": 1,
  "lineSizeMultiplier": 1,
  "collapse-forces": false,
  "centerStrength": 0.518713248970312,
  "repelStrength": 10,
  "linkStrength": 1,
  "linkDistance": 250,
  "scale": 0.65,
  "close": false
}"""

OBSIDIAN_HOTKEYS_JSON = """{
  "editor:fold-all": [{ "modifiers": ["Mod", "Shift"], "key": "F" }],
  "editor:unfold-all": [{ "modifiers": ["Mod", "Shift"], "key": "U" }],
  "app:go-back": [{ "modifiers": ["Mod"], "key": "ArrowLeft" }],
  "app:go-forward": [{ "modifiers": ["Mod"], "key": "ArrowRight" }]
}"""

OBSIDIAN_WORKSPACE_JSON = """{
  "main": {
    "id": "main",
    "type": "split",
    "children": [],
    "direction": "vertical"
  },
  "left": {
    "id": "left",
    "type": "split",
    "children": [
      {
        "id": "left-files",
        "type": "tabs",
        "children": [{ "id": "file-explorer", "type": "leaf", "state": { "type": "file-explorer", "state": {} } }]
      }
    ],
    "direction": "horizontal",
    "width": 260
  },
  "right": {
    "id": "right",
    "type": "split",
    "children": [],
    "direction": "horizontal",
    "width": 0
  },
  "active": "main",
  "lastOpenFiles": ["00-Executive/README.md"]
}"""

OMEGA_CSS_SNIPPET = """:root {
  --omega-accent:     #ffaf1a;
  --omega-accent-dim: rgba(255, 175, 26, 0.15);
  --color-adr:        #ffaf1a;
  --color-security:   #ff4444;
  --color-incident:   #ff8800;
  --color-runbook:    #4caf50;
  --color-sprint:     #55aaff;
  --color-memory:     #9966aa;
}

/* File-tree: highlight critical OMEGA folders */
.nav-folder-title[data-path^="14-ADRs"],
.nav-folder-title[data-path^="15-Runbooks"],
.nav-folder-title[data-path^="00-Executive"] {
  color: var(--omega-accent);
  font-weight: 700;
}
.nav-folder-title[data-path^="09-Security"] { color: var(--color-security); }
.nav-folder-title[data-path^="16-Incidents"] { color: var(--color-incident); }
.nav-folder-title[data-path^="13-Sprints"] { color: var(--color-sprint); }
.nav-folder-title[data-path^="32-AI-Memory"] { color: var(--color-memory); }

/* Memory-bank notes get a subtle left border */
.nav-file-title[data-path*="memory-bank"] {
  border-left: 2px solid var(--color-memory);
  padding-left: 6px;
}

/* Status badges in properties */
.tag[data-tag="status/proposed"] { background: rgba(255,175,26,0.2); }
.tag[data-tag="status/accepted"]  { background: rgba(76,175,80,0.2); }
.tag[data-tag="status/archived"]  { background: rgba(120,120,120,0.2); }
"""


def write_obsidian_config(vault_path: Path) -> None:
    """Write the .obsidian/ configuration directory."""
    obsidian_dir = vault_path / '.obsidian'
    obsidian_dir.mkdir(parents=True, exist_ok=True)

    snippets_dir = obsidian_dir / 'snippets'
    snippets_dir.mkdir(exist_ok=True)

    (obsidian_dir / 'app.json').write_text(OBSIDIAN_APP_JSON, encoding='utf-8')
    (obsidian_dir / 'appearance.json').write_text(OBSIDIAN_APPEARANCE_JSON, encoding='utf-8')
    (obsidian_dir / 'graph.json').write_text(OBSIDIAN_GRAPH_JSON, encoding='utf-8')
    (obsidian_dir / 'hotkeys.json').write_text(OBSIDIAN_HOTKEYS_JSON, encoding='utf-8')
    (obsidian_dir / 'workspace.json').write_text(OBSIDIAN_WORKSPACE_JSON, encoding='utf-8')
    (snippets_dir / 'omega-theme.css').write_text(OMEGA_CSS_SNIPPET, encoding='utf-8')

    plugins_dir = obsidian_dir / 'plugins'
    plugins_dir.mkdir(exist_ok=True)

    # Exact plugin list from examples/.obsidian/community-plugins.json
    community_plugins = [
        "dataview", "templater-obsidian", "calendar", "periodic-notes",
        "obsidian-tasks-plugin", "obsidian-kanban", "obsidian-excalidraw-plugin",
        "table-editor-obsidian", "url-into-selection", "quickadd",
        "recent-files-obsidian", "obsidian-style-settings", "obsidian-icon-folder",
        "mermaid-tools", "obsidian42-brat", "obsidian-git"
    ]
    (obsidian_dir / 'community-plugins.json').write_text(
        json.dumps(community_plugins, indent=2), encoding='utf-8'
    )

    # Core plugins — exact from examples/.obsidian/core-plugins.json
    core_plugins = {
        "file-explorer": True, "global-search": True, "switcher": True,
        "graph": True, "backlink": True, "canvas": True, "outgoing-link": True,
        "tag-pane": True, "properties": True, "page-preview": True,
        "daily-notes": True, "templates": True, "note-composer": True,
        "command-palette": True, "slash-command": False, "editor-status": True,
        "bookmarks": True, "markdown-importer": False, "zk-prefixer": False,
        "random-note": False, "outline": True, "word-count": True,
        "slides": False, "audio-recorder": False, "workspaces": True,
        "file-recovery": True, "publish": False, "sync": True, "bases": True
    }
    (obsidian_dir / 'core-plugins.json').write_text(
        json.dumps(core_plugins, indent=2), encoding='utf-8'
    )

    # daily-notes config
    (obsidian_dir / 'daily-notes.json').write_text(
        json.dumps({"folder": "13-Sprints/daily", "format": "YYYY-MM-DD", "template": "13-Sprints/templates/daily-note"}, indent=2),
        encoding='utf-8'
    )

    print('  ✓ .obsidian/ config written (app, appearance, graph, hotkeys, workspace, css, plugins, core)')


# ─────────────────────────────────────────────────────────────────────────────
# README GENERATORS
# ─────────────────────────────────────────────────────────────────────────────

def generate_folder_readme(folder: str, description: str) -> str:
    today = datetime.date.today().isoformat()
    return f"""---
folder: {folder}
description: "{description}"
created: {today}
status: active
tags: [{folder.split('-', 1)[-1].lower().replace('-', ', ')}]
---

# {folder}

> {description}

## Purpose

This folder contains all documentation related to **{folder.split('-', 1)[-1].replace('-', ' ').title()}**.

## Contents

_No documents yet. Add your first document using the OMEGA template._

## Quick Links

- [[00-Executive/README]] — Project vision & goals
- [[14-ADRs/adr-index]] — All architectural decisions
- [[15-Runbooks/runbook-index]] — Operational procedures

---

_Last updated: {today} · OMEGA Knowledge Vault_
"""


def generate_vault_readme(vault_path: Path, resolution_reason: str) -> str:
    today = datetime.date.today().isoformat()
    rel = str(vault_path)
    return f"""---
title: OMEGA Knowledge Vault
created: {today}
status: active
tags: [omega, vault, documentation, index]
---

# OMEGA Knowledge Vault

> Single source of truth for all engineering decisions, architecture, operations, and organizational knowledge.

## Vault Location

`{rel}`

Resolution method: `{resolution_reason}`

## Structure

This vault follows the **OMEGA 33-Folder Architecture** — every folder has a specific domain.
Navigate using the left file explorer or the **Knowledge Graph** (Ctrl/Cmd + G).

| Folder | Purpose |
|--------|---------|
{chr(10).join(f'| [[{f}/README\\|{f}]] | {FOLDER_DESCRIPTIONS[f]} |' for f in VAULT_FOLDERS)}

## Navigation

- **Start here**: [[00-Executive/README]] — Vision and goals
- **Decisions**: [[14-ADRs/adr-index]] — All ADRs
- **Operations**: [[15-Runbooks/runbook-index]] — Runbooks
- **Incidents**: [[16-Incidents/README]] — Post-mortems

## Standards

- Every document has YAML frontmatter with `title`, `created`, `status`, `tags`
- Every decision has an ADR in `14-ADRs/`
- Every operation has a runbook in `15-Runbooks/`
- Use `[[wiki-links]]` to connect related documents
- Never delete — archive with `status: archived` and link to replacement

---

_Generated by OMEGA CLI · {today}_
"""


def generate_adr_index() -> str:
    today = datetime.date.today().isoformat()
    return f"""---
title: ADR Index
created: {today}
status: active
tags: [adr, index, architecture]
---

# Architectural Decision Records

> All significant technical decisions, documented with context, rationale, and consequences.

## Active ADRs

_No ADRs yet. Create the first one:_
```bash
python scripts/omega-cli.py create-adr --title "Your Decision Title"
```

## ADR Status Legend

| Status | Meaning |
|--------|---------|
| `proposed` | Under discussion — not yet implemented |
| `accepted` | Approved and implemented |
| `deprecated` | Superseded but kept for historical reference |
| `superseded` | Replaced by a newer ADR (link provided) |

## Guidelines

- Create an ADR **before** implementing any significant architectural choice
- Never delete an ADR — mark as `deprecated` and link to the replacement
- Every ADR must answer: WHY this decision, not just WHAT

---

_OMEGA Knowledge Vault · [[README]]_
"""


def generate_runbook_index() -> str:
    today = datetime.date.today().isoformat()
    return f"""---
title: Runbook Index
created: {today}
status: active
tags: [runbook, operations, index]
---

# Operational Runbooks

> Step-by-step procedures for every repeatable operational task.

## Active Runbooks

_No runbooks yet. Add your first runbook to this folder._

## Runbook Template

```markdown
---
title: "Runbook: [Procedure Name]"
created: YYYY-MM-DD
reviewed: YYYY-MM-DD
status: active
severity: sev-1 | sev-2 | sev-3
tags: [runbook, operations]
---

# Runbook: [Procedure Name]

## Symptoms / When to use this runbook

## Pre-requisites

## Steps

1. Step one
2. Step two

## Verification

## Rollback

## Related
- [[14-ADRs/ADR-NNNN]]
- [[16-Incidents/README]]
```

---

_OMEGA Knowledge Vault · [[README]]_
"""


# ─────────────────────────────────────────────────────────────────────────────
# COMMANDS
# ─────────────────────────────────────────────────────────────────────────────

def cmd_resolve_vault(args) -> None:
    """Print the resolved vault path and why it was chosen."""
    vault_path, reason = resolve_vault_path(Path.cwd())
    repo_root = find_repo_root(Path.cwd())
    print(json.dumps({
        'repo_root':     str(repo_root),
        'vault_path':    str(vault_path),
        'vault_exists':  vault_path.exists(),
        'reason':        reason,
        'is_omega_vault': is_omega_vault(vault_path) if vault_path.exists() else False,
    }, indent=2))


def cmd_init_vault(args) -> None:
    """
    Discover or create the project documentation vault.
    Never blindly creates obsidian-vault/ — always respects existing structure.
    """
    cwd = Path.cwd()
    vault_path, reason = resolve_vault_path(cwd)
    repo_root = find_repo_root(cwd)

    print(f'\n[OMEGA] Repository root : {repo_root}')
    print(f'[OMEGA] Vault path      : {vault_path}')
    print(f'[OMEGA] Resolution      : {reason}')

    already_omega = vault_path.exists() and is_omega_vault(vault_path)

    if already_omega:
        print('[OMEGA] Existing OMEGA vault detected — syncing missing folders only.\n')
    else:
        print('[OMEGA] Initialising new vault...\n')

    vault_path.mkdir(parents=True, exist_ok=True)

    # Write .obsidian config
    write_obsidian_config(vault_path)

    # Create all 33 folders + README
    created = 0
    for folder in VAULT_FOLDERS:
        folder_path = vault_path / folder
        folder_path.mkdir(exist_ok=True)
        readme = folder_path / 'README.md'
        if not readme.exists():
            readme.write_text(
                generate_folder_readme(folder, FOLDER_DESCRIPTIONS[folder]),
                encoding='utf-8'
            )
            created += 1
            print(f'  + {folder}/README.md')

    # Vault root README
    vault_readme = vault_path / 'README.md'
    if not vault_readme.exists():
        vault_readme.write_text(generate_vault_readme(vault_path, reason), encoding='utf-8')
        print(f'  + README.md (vault index)')

    # ADR index
    adr_index = vault_path / '14-ADRs' / 'adr-index.md'
    if not adr_index.exists():
        adr_index.write_text(generate_adr_index(), encoding='utf-8')
        print(f'  + 14-ADRs/adr-index.md')

    # Runbook index
    rb_index = vault_path / '15-Runbooks' / 'runbook-index.md'
    if not rb_index.exists():
        rb_index.write_text(generate_runbook_index(), encoding='utf-8')
        print(f'  + 15-Runbooks/runbook-index.md')

    # 32-AI-Memory: session log and learned patterns
    ai_mem_dir = vault_path / '32-AI-Memory'
    ai_mem_dir.mkdir(exist_ok=True)

    session_log = ai_mem_dir / 'session-log.md'
    if not session_log.exists():
        session_log.write_text(f"""---
title: "OMEGA Session Log"
created: {datetime.date.today().isoformat()}
updated: {datetime.date.today().isoformat()}
status: active
tags: [memory, agent, session]
---

# OMEGA Session Log

This file is the agent's long-term memory archive.
Append a new entry at the end of every session.

## Log Format

```markdown
## YYYY-MM-DD — Session N
**Focus:** [what was worked on]
**Decisions:** [key choices made]
**Patterns learned:** [reusable patterns discovered]
**Files changed:** [list of vault paths modified]
**Next session:** [what to pick up]
```

---

_Maintained by OMEGA Obsidian Agent · [[README]]_
""", encoding='utf-8')
        print('  + 32-AI-Memory/session-log.md')

    learned = ai_mem_dir / 'learned-patterns.md'
    if not learned.exists():
        learned.write_text(f"""---
title: "Learned Patterns"
created: {datetime.date.today().isoformat()}
status: active
tags: [memory, agent, patterns]
---

# Learned Patterns

Reusable patterns OMEGA has discovered across projects.
Add entries when a new pattern proves valuable.

## Pattern Format
```markdown
### [Pattern Name]
**Context:** when to apply
**Solution:** the pattern
**Outcome:** result observed
**First seen:** YYYY-MM-DD
```

---

_OMEGA Knowledge Vault · [[32-AI-Memory/session-log]] · [[README]]_
""", encoding='utf-8')
        print('  + 32-AI-Memory/learned-patterns.md')

    error_mem = ai_mem_dir / 'error-memory.md'
    if not error_mem.exists():
        error_mem.write_text(f"""---
title: "Error Memory"
created: {datetime.date.today().isoformat()}
status: active
tags: [memory, agent, errors]
---

# Error Memory

Mistakes and corrections logged to prevent repetition.

## Entry Format
```markdown
### YYYY-MM-DD — [Error Description]
**What happened:** describe the mistake
**Root cause:** why it happened
**Correction:** what was done to fix it
**Prevention:** how to avoid in future
```

---

_OMEGA Knowledge Vault · [[32-AI-Memory/session-log]] · [[README]]_
""", encoding='utf-8')
        print('  + 32-AI-Memory/error-memory.md')

    # Write vault config file so other tools can find it
    config = {
        'vault_path': str(vault_path),
        'repo_root':  str(repo_root),
        'reason':     reason,
        'initialized': datetime.date.today().isoformat(),
        'version': '2.0.0',
    }
    (vault_path / '.omega-vault.json').write_text(json.dumps(config, indent=2), encoding='utf-8')

    status = 'synced' if already_omega else 'created'
    print(f'\n[OMEGA] ✓ Vault {status}. {created} new documents written.')
    print(f'[OMEGA] ✓ Open in Obsidian: File → Open vault → {vault_path}\n')


def cmd_create_adr(args) -> None:
    vault_path, _ = resolve_vault_path(Path.cwd())
    adr_dir = vault_path / '14-ADRs'
    adr_dir.mkdir(parents=True, exist_ok=True)

    existing = sorted(adr_dir.glob('ADR-*.md'))
    next_id = len(existing) + 1
    slug = args.title.lower().replace(' ', '-').replace('/', '-')[:60]
    filename = f'ADR-{next_id:04d}-{slug}.md'
    filepath = adr_dir / filename

    today = datetime.date.today().isoformat()
    content = f"""---
id: ADR-{next_id:04d}
title: "{args.title}"
status: {args.status}
date: {today}
deciders: [{args.deciders}]
supersedes: []
superseded_by: []
tags: [adr, architecture, decision]
---

# ADR-{next_id:04d}: {args.title}

## Status

`{args.status}`

## Context

> What problem are we solving? What constraints exist? What alternatives were considered?

_Fill in the context here._

## Decision

> What did we decide to do, and specifically why?

_Fill in the decision here._

## Alternatives Considered

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| Alternative A | ... | ... | ... |
| Alternative B | ... | ... | ... |

## Consequences

**Positive:**
- ...

**Negative:**
- ...

**Risks:**
- ...

## Implementation Notes

_Key patterns, library versions, migration steps, or gotchas._

## Review Date

{(datetime.date.today().replace(year=datetime.date.today().year + 1)).isoformat()}

## Related

- [[adr-index]]
- [[../01-Architecture/README]]

---

_OMEGA Knowledge Vault · {today}_
"""
    filepath.write_text(content, encoding='utf-8')
    print(f'[OMEGA] ✓ ADR created: {filepath}')

    # Update adr-index to include the new ADR
    index_path = adr_dir / 'adr-index.md'
    if index_path.exists():
        index_text = index_path.read_text(encoding='utf-8')
        entry = f'| [[ADR-{next_id:04d}-{slug}\\|ADR-{next_id:04d}]] | {args.title} | `{args.status}` | {today} |\n'
        if '## Active ADRs' in index_text and '_No ADRs yet' in index_text:
            index_text = index_text.replace(
                '_No ADRs yet. Create the first one:_\n```bash\npython scripts/omega-cli.py create-adr --title "Your Decision Title"\n```',
                f'| ADR | Title | Status | Date |\n|-----|-------|--------|------|\n{entry}'
            )
        elif '| ADR | Title | Status | Date |' in index_text:
            index_text = index_text.replace(
                '| ADR | Title | Status | Date |\n|-----|-------|--------|------|\n',
                f'| ADR | Title | Status | Date |\n|-----|-------|--------|------|\n{entry}'
            )
        index_path.write_text(index_text, encoding='utf-8')
        print(f'[OMEGA] ✓ adr-index.md updated')


def cmd_audit(args) -> None:
    """Security + compliance scan on the repository."""
    cwd = Path.cwd()
    repo_root = find_repo_root(cwd)
    vault_path, _ = resolve_vault_path(cwd)

    print(f'[OMEGA] Auditing: {repo_root}')
    print(f'[OMEGA] Vault at: {vault_path}\n')

    violations = []
    SKIP_DIRS = {'.git', 'node_modules', '.next', 'dist', 'build', '.turbo',
                 vault_path.name, '.obsidian', '__pycache__', '.venv', 'venv'}

    SECRET_PATTERNS = [
        ('hardcoded-password',   r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']{4,}["\']'),
        ('hardcoded-api-key',    r'(?i)(api[_-]?key|apikey)\s*=\s*["\'][a-zA-Z0-9_\-]{16,}["\']'),
        ('hardcoded-secret',     r'(?i)(secret[_-]?key|auth[_-]?token)\s*=\s*["\'][^"\']{8,}["\']'),
        ('private-key-header',   r'-----BEGIN (RSA |EC )?PRIVATE KEY-----'),
    ]
    CORS_PATTERNS = [
        ('wildcard-cors',        r"Access-Control-Allow-Origin['\"]?\s*[:=]\s*['\"]?\*"),
    ]
    SECURITY_PATTERNS = SECRET_PATTERNS + CORS_PATTERNS

    import re
    EXTENSIONS = {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.py', '.go',
                  '.json', '.yaml', '.yml', '.env', '.conf', '.nginx'}

    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            if not any(fname.endswith(ext) for ext in EXTENSIONS):
                continue
            # Skip .env.example files — they're templates
            if fname in {'.env.example', '.env.sample', '.env.template'}:
                continue
            fpath = Path(root) / fname
            try:
                text = fpath.read_text(encoding='utf-8', errors='ignore')
                for line_no, line in enumerate(text.splitlines(), 1):
                    # Skip lines that reference environment variables (safe patterns)
                    if 'process.env' in line or 'os.environ' in line or 'os.getenv' in line:
                        continue
                    for rule_name, pattern in SECURITY_PATTERNS:
                        if re.search(pattern, line):
                            violations.append({
                                'rule': rule_name,
                                'file': str(fpath.relative_to(repo_root)),
                                'line': line_no,
                                'content': line.strip()[:120],
                            })
            except Exception:
                pass

    # Vault health check
    vault_issues = []
    if not vault_path.exists():
        vault_issues.append('Vault not initialised — run: python scripts/omega-cli.py init-vault')
    else:
        adr_dir = vault_path / '14-ADRs'
        adrs = list(adr_dir.glob('ADR-*.md')) if adr_dir.exists() else []
        if len(adrs) == 0:
            vault_issues.append('No ADRs found in 14-ADRs/ — document architectural decisions')
        runbook_dir = vault_path / '15-Runbooks'
        runbooks = list(runbook_dir.glob('*.md')) if runbook_dir.exists() else []
        if len([r for r in runbooks if r.name != 'README.md' and r.name != 'runbook-index.md']) == 0:
            vault_issues.append('No runbooks found in 15-Runbooks/ — document operational procedures')

    # Report
    if violations:
        print(f'[OMEGA] ⚠  Security violations: {len(violations)}\n')
        for v in violations:
            print(f'  [{v["rule"].upper()}] {v["file"]}:{v["line"]}')
            print(f'    → {v["content"]}\n')
    else:
        print('[OMEGA] ✓ No security violations detected.\n')

    if vault_issues:
        print(f'[OMEGA] ⚠  Vault issues: {len(vault_issues)}\n')
        for issue in vault_issues:
            print(f'  • {issue}')
        print()
    else:
        print('[OMEGA] ✓ Vault health: OK\n')

    total = len(violations) + len(vault_issues)
    if total == 0:
        print('[OMEGA] ✓ Full audit passed. Zero compliance violations.')
    else:
        print(f'[OMEGA] ✗ Audit completed with {total} issue(s). Fix before deploying.')
        sys.exit(1)


def cmd_status(args) -> None:
    """Print vault health summary."""
    cwd = Path.cwd()
    vault_path, reason = resolve_vault_path(cwd)
    repo_root = find_repo_root(cwd)

    print(f'\n[OMEGA] Vault Status Report')
    print(f'  Repository root : {repo_root}')
    print(f'  Vault path      : {vault_path}')
    print(f'  Resolution      : {reason}')
    print(f'  Vault exists    : {vault_path.exists()}')

    if not vault_path.exists():
        print('\n  ⚠  Vault not initialised.')
        print('  Run: python scripts/omega-cli.py init-vault\n')
        return

    print(f'\n  Folder status:')
    missing = []
    for folder in VAULT_FOLDERS:
        fp = vault_path / folder
        docs = list(fp.glob('*.md')) if fp.exists() else []
        non_readme = [d for d in docs if d.name not in ('README.md',)]
        status = f'{len(non_readme)} doc(s)' if non_readme else 'empty'
        marker = '✓' if fp.exists() else '✗'
        print(f'  {marker} {folder:<40} {status}')
        if not fp.exists():
            missing.append(folder)

    if missing:
        print(f'\n  ⚠  {len(missing)} folder(s) missing. Run init-vault to fix.')
    else:
        print(f'\n  ✓ All 33 folders present.')

    adr_count = len(list((vault_path / '14-ADRs').glob('ADR-*.md')))
    print(f'  ✓ ADRs: {adr_count}')
    print()


# ─────────────────────────────────────────────────────────────────────────────
# CLI ENTRYPOINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='OMEGA CLI — Vault discovery, initialization, and audit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    sub = parser.add_subparsers(dest='command', required=True)

    sub.add_parser('resolve-vault', help='Show resolved vault path and detection reason')

    sub.add_parser('init-vault', help='Discover existing docs/ or create docs/vault/ at repo root')

    adr_p = sub.add_parser('create-adr', help='Create a new Architectural Decision Record')
    adr_p.add_argument('--title',    required=True,  help='Decision title')
    adr_p.add_argument('--status',   default='proposed',
                       choices=['proposed', 'accepted', 'deprecated', 'superseded'])
    adr_p.add_argument('--deciders', default='CTO, Tech Lead',
                       help='Comma-separated list of decision makers')

    sub.add_parser('audit',  help='Security and compliance scan')
    sub.add_parser('status', help='Vault health report')

    args = parser.parse_args()

    dispatch = {
        'resolve-vault': cmd_resolve_vault,
        'init-vault':    cmd_init_vault,
        'create-adr':    cmd_create_adr,
        'audit':         cmd_audit,
        'status':        cmd_status,
    }
    dispatch[args.command](args)


if __name__ == '__main__':
    main()
