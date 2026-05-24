#!/usr/bin/env python3
import os
import sys
import argparse
import datetime
import uuid

folders = [
    '00-Executive', '01-Architecture', '02-Product', '03-Infrastructure', 
    '04-Frontend', '05-Backend', '06-Mobile', '07-AI', '08-Data', 
    '09-Security', '10-Observability', '11-Design-System', '12-RBAC', 
    '13-Sprints', '14-ADRs', '15-Runbooks', '16-Incidents', '17-Diagrams', 
    '18-Knowledge-Graph', '19-Standards', '20-QA', '21-Compliance', 
    '22-Token-Optimization', '23-Cost-Optimization', '24-Agent-Orchestration', 
    '25-Platform-Engineering', '26-Workflow-Systems', '27-Developer-Experience', 
    '28-Disaster-Recovery', '29-Audit-Logs', '30-Kubernetes', '31-MCP', 
    '32-AI-Memory', '33-Architecture-Recovery'
]

def init_vault(base_dir):
    print(f"[*] Initializing OMEGA Obsidian Memory Vault at: {base_dir}")
    os.makedirs(base_dir, exist_ok=True)
    for folder in folders:
        folder_path = os.path.join(base_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        readme_path = os.path.join(folder_path, "README.md")
        if not os.path.exists(readme_path):
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(f"# OMEGA Vault - {folder}\n\nInitialized for OMEGA operations.\n")
    print("[+] Successfully initialized all 34 directories.")

def create_adr(base_dir, title, status, deciders):
    adr_dir = os.path.join(base_dir, "14-ADRs")
    os.makedirs(adr_dir, exist_ok=True)
    
    # Calculate incremental ID
    existing = [f for f in os.listdir(adr_dir) if f.startswith("ADR-") and f.endswith(".md")]
    next_id = len(existing) + 1
    filename = f"ADR-{next_id:04d}-{title.lower().replace(' ', '-')}.md"
    filepath = os.path.join(adr_dir, filename)
    
    adr_content = f"""---
id: ADR-{next_id:04d}
title: "{title}"
status: {status}
date: {datetime.date.today().isoformat()}
deciders: [{deciders}]
supersedes: []
---

# ADR-{next_id:04d}: {title}

## Context
Provide background context and why this technical decision is required.

## Decision
What is the explicit design solution and architectural decision?

## Consequences
- **Positive**: ...
- **Negative**: ...
- **Risks**: ...

## Alternatives Considered
| Option | Pros | Cons | Why Rejected |
| :--- | :--- | :--- | :--- |
| Alternative 1 | ... | ... | ... |
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(adr_content)
    print(f"[+] Standardized ADR created at: {filepath}")

def run_audit(target_dir):
    print(f"[*] Auditing directories for compliance under: {target_dir}")
    violations = 0
    # Simple regex search patterns
    secret_patterns = ["password", "private_key", "api_key", "secret_key"]
    cors_patterns = ["Access-Control-Allow-Origin: *", "Access-Control-Allow-Origin': '*'"]
    
    for root, _, files in os.walk(target_dir):
        if "obsidian-vault" in root or "node_modules" in root or ".git" in root:
            continue
        for file in files:
            if not file.endswith(('.ts', '.js', '.py', '.go', '.nginx', '.conf', '.json', '.md')):
                continue
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for line_no, line in enumerate(f, 1):
                        # Secrets check
                        if "key" in file.lower() or "env" in file.lower():
                            continue # Skip environmental mappings
                        for pattern in secret_patterns:
                            if pattern in line.lower() and "=" in line and ("const" in line or "let" in line or "var" in line or "export" in line):
                                if not any(x in line for x in ["process.env", "config", "import", "type"]):
                                    print(f"[!] SEC-WARN [{file}:{line_no}]: Possible hardcoded secret: {line.strip()}")
                                    violations += 1
                        # CORS Check
                        for pattern in cors_patterns:
                            if pattern in line:
                                print(f"[!] CORS-WARN [{file}:{line_no}]: Permissive CORS header detected: {line.strip()}")
                                violations += 1
            except Exception as e:
                pass
    if violations == 0:
        print("[+] Audit completed successfully. Zero standard compliance violations detected.")
    else:
        print(f"[!] Audit completed with {violations} compliance warnings.")

def main():
    parser = argparse.ArgumentParser(description="OMEGA Enterprise Orchestration CLI Tool")
    subparsers = parser.add_subparsers(dest="command")
    
    # Init Vault
    init_parser = subparsers.add_parser("init-vault", help="Verify and physically initialize the 33-Folder structure")
    init_parser.add_argument("--dir", default=r"C:\Users\rui.rodrigues\Desktop\AlphaSkill\OMEGA\obsidian-vault", help="Base path to Obsidian vault")
    
    # Create ADR
    adr_parser = subparsers.add_parser("create-adr", help="Generate a standardized Architectural Decision Record")
    adr_parser.add_argument("--title", required=True, help="Title of the decision")
    adr_parser.add_argument("--status", default="accepted", choices=["proposed", "accepted", "deprecated", "superseded"])
    adr_parser.add_argument("--deciders", default="CTO, PMO", help="List of decision makers")
    adr_parser.add_argument("--dir", default=r"C:\Users\rui.rodrigues\Desktop\AlphaSkill\OMEGA\obsidian-vault", help="Base path to Obsidian vault")
    
    # Audit Workspace
    audit_parser = subparsers.add_parser("audit", help="Audits local files for CORS leaks, hardcoded secrets, and compliance standards")
    audit_parser.add_argument("--dir", default=r"C:\Users\rui.rodrigues\Desktop\AlphaSkill\OMEGA", help="Base path of OMEGA ecosystem")
    
    args = parser.parse_args()
    
    if args.command == "init-vault":
        init_vault(args.dir)
    elif args.command == "create-adr":
        create_adr(args.dir, args.title, args.status, args.deciders)
    elif args.command == "audit":
        run_audit(args.dir)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
