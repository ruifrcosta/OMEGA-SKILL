# ADR-0004: Google Workspace (GWS) Automation and Integration Standards

## Status
Accepted

## Deciders
- OMEGA Architecture Office
- CTO Agent
- Workflow Agent

## Context
Google Workspace (GWS) API integrations (Gmail, Sheets, Docs, Calendar, Drive) are vital for automated company operations. However, legacy implementations were severely fragmented, containing over 50 isolated `recipe-*` scripts and `gws-*` folders. This caused auth duplication, lack of consistent Model Armor sanitization, security vulnerabilities with raw credentials, and continuous execution errors due to zsh/bash shell expansions (e.g. zsh history expansion on the `!` sheet range symbol).

We must centralize these systems into a unified OMEGA GWS Integration Standard.

## Decision
We enforce a strict integration protocol for all Google Workspace automated workflows inside OMEGA:

### 1. Unified Authentication Standard
- Custom scripts must never load raw API keys.
- Authentication must strictly leverage standard environment paths:
  - **Service Accounts**: Enforce `GOOGLE_APPLICATION_CREDENTIALS` pointing to the secure JSON vault key.
  - **Developer Sessions**: Standardized browser OAuth login using `gws auth login`.

### 2. Mandatory Model Armor Sanitization
- Under OMEGA's security guidelines, any write/send operations (such as drafting emails or creating documents) that process raw user inputs **MUST** wrap parameters with the Model Armor sanitization flag:
  ```bash
  --sanitize <TEMPLATE>
  ```
- This prevents PII leakage and checks against content safety templates prior to execution.

### 3. Shell Expansion Protection
- Shell commands targeting Google Sheets ranges (e.g., `Sheet1!A1:D10`) contain the `!` character, which triggers history expansion in Zsh. 
- All shell executions in OMEGA scripts **MUST** wrap ranges in double quotes with escaped inner quotes instead of single quotes to guarantee script durability:
  ```bash
  # WRONG
  gws sheets +read --spreadsheet ID --range 'Sheet1!A1:D10'
  
  # CORRECT
  gws sheets +read --spreadsheet ID --range "Sheet1!A1:D10"
  ```

### 4. Interactive Gates
- Write or delete operations (e.g., deleting a Calendar event, bulk sending emails) must include an interactive confirmation gate or run with the `--dry-run` validation flag first to confirm payload schema correctness.

## Consequences
### Positive
- **Security Hardening**: Unified GCP credential ingestion ensures zero hardcoded key leaks.
- **Model Armor Protection**: Prevents malicious injection or sensitive data leakage (PII) over public mail networks.
- **Syntactic Stability**: Enforcing double-quote ranges prevents terminal execution crashes on Zsh shells.

### Negative
- **Validation Overhead**: Forcing interactive approval or dry-runs increases workflow execution steps.
