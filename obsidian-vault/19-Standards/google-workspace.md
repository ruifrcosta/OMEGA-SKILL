# Google Workspace (GWS) Command & Integration Standard

This document maps out the unified OMEGA standards for interacting with the Google Workspace REST API suite (Gmail, Calendar, Sheets, Drive, Docs) via the `gws` command-line utility.

---

## 1. Global Command Architecture

All GWS interactions inside OMEGA must utilize the unified `gws` binary, structured as follows:

```bash
gws <service> <resource> [sub-resource] <method> [flags]
```

### Supported Core Services
- `gmail`: Message dispatching, reading, triaging, threads, and automated mail watch.
- `sheets`: Grid cell reading, appending, range management, and CSV backups.
- `calendar`: Event creation, scheduling, free-time sweeps, dynamic invites.
- `drive`: Bulk file downloads, folder mapping, change watching.
- `docs`: Document templating, dynamic writing, draft creation.

---

## 2. Mandatory Security & Formatting Flags

| Flag | Purpose | Standard Constraint |
|------|---------|---------------------|
| `--format json` | Integration Input | Enforced for machine pipelines to prevent text-scraping failures. |
| `--dry-run` | Operations Gate | Mandatory for destructive methods (e.g., `delete`) in staging environments. |
| `--sanitize <TEMPLATE>` | Model Armor | Mandatory for any public-facing write/send operations processing dynamic inputs. |
| `--page-all` | Large Datasets | Enforced when exporting logs or large directories. Uses NDJSON. |

---

## 3. Shell Expansion & Argument Escaping

### The Zsh Sheet Range Hazard
Zsh interprets the exclamation mark (`!`) in sheet ranges (e.g., `Sheet1!A1:B10`) as a shell history expansion. 
To guarantee cross-platform execution durability:

```bash
# ❌ INCORRECT (Triggers terminal history error on Zsh)
gws sheets +read --spreadsheet ID --range 'Sheet1!A1:D10'

# ✅ CORRECT (Safely escapes range expansions)
gws sheets +read --spreadsheet ID --range "Sheet1!A1:D10"
```

### JSON String Wrapping
When passing query parameters (`--params`) or body contents (`--json`), wrap the complete value in **single quotes** and the inner keys/values in **double quotes**:

```bash
gws drive files list --params '{"pageSize": 5}'
```

---

## 4. The OMEGA Model Armor Guardrail
Model Armor sanitizes user prompts and system outputs to prevent PII leakage and injection exploits.

### Standard Sanitization Wrapper
```bash
gws gmail messages send --json '{"userId":"me", "message":{"raw":"..."}}' --sanitize "pii-mask-template"
```
This ensures raw customer datasets are scanned and masked prior to hitting the external mail relay networks.
