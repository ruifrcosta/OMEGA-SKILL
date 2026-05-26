# OMEGA Find-Skills Discovery & Extension Reference
> Distilled from the `find-skills` specification

This reference details the automated discovery, verification, and installation protocols for extending agent capabilities using the open agent skills ecosystem.

---

## 1. When to Trigger Ecosystem Discovery
OMEGA triggers the find-skills protocol whenever the user:
- Asks *"how do I do X"* for common domain tasks.
- Asks *"is there a skill for X"* or *"find a skill for X"*.
- Inquires *"can you do X"* for specialized capabilities.
- Expresses a desire to extend existing tools, templates, or workflows.
- Mentions a need for assistance in specialized fields (e.g. video rendering, advanced parsers).

---

## 2. The Skills CLI Command Suite
The Skills CLI (`npx skills`) acts as the ecosystem package manager.

| Command | Action | Runtime Context |
|---|---|---|
| `npx skills find [query]` | Interactive / keyword search | Search the public registry |
| `npx skills add <package>` | Install skill from GitHub/source | Installs to local or global paths |
| `npx skills check` | Check for updates | Scans installed plugins |
| `npx skills update` | Update all installed packages | Pulled from upstream repository |

Registry Showcase: [skills.sh](https://skills.sh/)

---

## 3. The 6-Step Search & Install Protocol

### Step 1: Needs Classification
Identify the specific domain (e.g. React, Testing, DevOps), the action (e.g. profiling, bundling), and if an existing package is likely to contain this capability.

### Step 2: Leaderboard Check-First
Before running a blind CLI search, query the [skills.sh](https://skills.sh/) leaderboard for highly popular, battle-tested options:
- `vercel-labs/agent-skills` (React, Next.js, web design)
- `anthropics/skills` (Frontend design, document processing)

### Step 3: Targeted Search Execution
Run the CLI search using narrow keywords:
```bash
npx skills find react performance
npx skills find changelog
```

### Step 4: Strict Quality Gates
**Do not trust search results blindly.** Validate the following signals:
1. **Install Count**: Prefer skills with **1K+ installs**. Reject or treat with extreme caution anything < 100 installs.
2. **Author Reputation**: Verify if the publisher is an established source (`vercel-labs`, `anthropics`, `microsoft`).
3. **Repository Stars**: Star counts **< 100** on the source git repository indicate a high risk of bugs.

### Step 5: High-Fidelity Recommendation Presentation
Format the recommendation clearly, providing:
- Skill name and action description.
- Install count and verified publisher.
- Simple installation command.
- Learn-more link.

*Example*:
> I found a verified skill: `react-best-practices` by Vercel Engineering (185K installs).
> Install command: `npx skills add vercel-labs/agent-skills@react-best-practices`

### Step 6: Direct Automated Installation
If requested, install the package directly into the global configuration path:
```bash
npx skills add <owner/repo@skill> -g -y
```
*(The `-g` flag registers the package globally; `-y` skips interaction screens)*

---

## 4. Fallback Protocol
If no matching skill is discovered:
1. Acknowledge that the search yielded no verified packages.
2. Offer to fulfill the request using OMEGA's built-in references.
3. Suggest that the user can scaffold their own package:
   `npx skills init my-custom-skill`
