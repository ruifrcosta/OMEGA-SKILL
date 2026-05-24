# OMEGA Deployment & Vercel CLI Blueprints

This document outlines the OMEGA standards for deploying multi-service React/Next.js platforms to Vercel via CI/CD and token-based CLI automation, eliminating interactive shell dependencies.

---

## 1. Secure Token Injection Pattern

**Never** pass the Vercel Access Token directly in a command line argument (e.g. `vercel deploy --token ...`). Doing so exposes secrets in CI/CD logs, shell command history, and process listings.

### Enforced Secure Pattern
Inject the token strictly as an environment variable in the running context:

```bash
# 1. Inject via environment
export VERCEL_TOKEN="vca_your_secure_access_token_here"

# 2. Execute Vercel commands (the CLI natively reads VERCEL_TOKEN)
vercel deploy -y --no-wait
```

---

## 2. Monorepo Linking Structure
To automate builds inside monorepos (managed via pnpm workspaces and Turborepo) without manual configuration:

- **Environment Linking (Preferred)**: Export the target project and organization IDs in the deployment runner to bypass local state directories completely:
  ```bash
  export VERCEL_ORG_ID="team_org_id"
  export VERCEL_PROJECT_ID="proj_project_id"
  ```
- **Repository Linking**: If env parameters are unavailable, link the local root workspace to Vercel via git remote mapping (generating a persistent `.vercel/repo.json` index):
  ```bash
  vercel link --repo --scope "your-team-slug" -y
  ```

---

## 3. Environment Variable Management

All environment variables used by the deployed applications must be managed programmatically via the Vercel CLI.

### Safe CLI Commands
- **Retrieve current configuration**:
  ```bash
  vercel env ls --scope "your-team-slug"
  ```
- **Inject new variables (isolated by environment)**:
  ```bash
  # Production environment only
  echo "production_db_url" | vercel env add DATABASE_URL production --scope "your-team-slug"
  
  # Preview environment only
  echo "preview_db_url" | vercel env add DATABASE_URL preview --scope "your-team-slug"
  ```
- **Pull variables locally for SRE debugging**:
  ```bash
  vercel env pull --scope "your-team-slug"
  ```

---

## 4. Operational Guardrails

1. **Default to Preview**: All deployments must target a `preview` branch unless the production flag (`--prod`) is explicitly requested by a SRE/PMO release trigger.
2. **Auto-confirm Operations**: Always pass the `-y` auto-confirm flag and `--no-wait` async options inside CI/CD processes to prevent terminal freezes:
   ```bash
   vercel deploy --scope "your-team-slug" -y --no-wait
   ```
3. **Structured Outputs**: For subsequent build steps or validation logs, utilize the JSON output format flag:
   ```bash
   vercel ls --format json --scope "your-team-slug"
   ```
