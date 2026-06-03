# Solo Dev Full-Stack Infrastructure Reference

Complete templates for the 6 missing areas every solo developer needs to ship a production-grade system.
Read this file for: env management, CI/CD pipelines, docker-compose dev stack, Helm charts,
branching strategy, Ingress/TLS, service mesh, registry flow, edge functions, and inter-service communication.

## Table of Contents
1. [.env Structure & Startup Validation](#env)
2. [Secret Management by Environment](#secrets)
3. [Docker Compose — Full Dev Stack](#compose)
4. [GitHub Actions — Complete CI/CD Pipelines](#cicd)
5. [Helm Charts — Production Templates](#helm)
6. [Branching Strategy & PR Protocol](#branching)
7. [Ingress, TLS & cert-manager](#ingress)
8. [Service Mesh — mTLS with Istio](#mesh)
9. [Container Registry Flow (ECR/GHCR)](#registry)
10. [Edge Functions — Cloudflare Workers & Vercel Edge](#edge)
11. [Inter-Service Communication Patterns](#communication)
12. [Debug & Maintainability Protocols](#debug)
13. [Scalability Runbooks](#scalability)

---

## 1. .env Structure & Startup Validation {#env}

### Canonical .env.example — copy per service, never commit .env

```bash
# =============================================================
# SERVICE: api  |  LAST UPDATED: 2025-01-01  |  OWNER: @team
# Required vars crash the server on startup if missing (t3-env).
# Optional vars have defaults shown.
# =============================================================

# ── DATABASE ──────────────────────────────────────────────────
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME?schema=public&connection_limit=10&pool_timeout=20
DATABASE_DIRECT_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME   # direct for migrations (bypass PgBouncer)

# ── AUTH ──────────────────────────────────────────────────────
JWT_SECRET=                          # min 64 chars, generated: openssl rand -hex 32
JWT_ACCESS_EXPIRY=15m
JWT_REFRESH_EXPIRY=7d
JWT_SIGNING_KEY_ID=v1                # used for key rotation

# ── EXTERNAL SERVICES ─────────────────────────────────────────
SUPABASE_URL=https://PROJECT.supabase.co
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=           # server-only, never expose to client

RESEND_API_KEY=re_
RESEND_FROM=noreply@yourdomain.com
RESEND_REPLY_TO=support@yourdomain.com

STRIPE_SECRET_KEY=sk_live_           # sk_test_ for non-prod
STRIPE_WEBHOOK_SECRET=whsec_
STRIPE_PUBLISHABLE_KEY=pk_live_

# ── STORAGE ───────────────────────────────────────────────────
AWS_REGION=eu-west-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=
S3_BUCKET_URL=https://BUCKET.s3.eu-west-1.amazonaws.com

# ── OBSERVABILITY ─────────────────────────────────────────────
OTEL_EXPORTER_OTLP_ENDPOINT=https://ingest.eu.signoz.cloud:443
OTEL_EXPORTER_OTLP_HEADERS=signoz-access-token=TOKEN
OTEL_SERVICE_NAME=api
SENTRY_DSN=https://KEY@SENTRY_ORG.ingest.sentry.io/PROJECT_ID
LOG_LEVEL=info                       # debug | info | warn | error

# ── REDIS ─────────────────────────────────────────────────────
REDIS_URL=redis://default:PASSWORD@HOST:6379
REDIS_TLS=true                       # false for local dev

# ── INTERNAL ──────────────────────────────────────────────────
NODE_ENV=production                  # development | test | staging | production
PORT=3000
APP_URL=https://api.yourdomain.com
ALLOWED_ORIGINS=https://app.yourdomain.com,https://admin.yourdomain.com
API_VERSION=v1
```

### t3-env Startup Validation (crashes on startup if var missing)

```typescript
// env.ts — import this at the top of every entrypoint
import { createEnv } from '@t3-oss/env-nextjs';  // or @t3-oss/env-core for Node
import { z } from 'zod';

export const env = createEnv({
  server: {
    DATABASE_URL:           z.string().url(),
    DATABASE_DIRECT_URL:    z.string().url(),
    JWT_SECRET:             z.string().min(64),
    JWT_ACCESS_EXPIRY:      z.string().default('15m'),
    JWT_REFRESH_EXPIRY:     z.string().default('7d'),
    SUPABASE_SERVICE_ROLE_KEY: z.string().min(1),
    RESEND_API_KEY:         z.string().startsWith('re_'),
    STRIPE_SECRET_KEY:      z.string().startsWith('sk_'),
    STRIPE_WEBHOOK_SECRET:  z.string().startsWith('whsec_'),
    AWS_REGION:             z.string().default('eu-west-1'),
    AWS_ACCESS_KEY_ID:      z.string().min(1),
    AWS_SECRET_ACCESS_KEY:  z.string().min(1),
    S3_BUCKET_NAME:         z.string().min(1),
    OTEL_SERVICE_NAME:      z.string().default('api'),
    REDIS_URL:              z.string().url(),
    NODE_ENV:               z.enum(['development', 'test', 'staging', 'production']),
    PORT:                   z.coerce.number().default(3000),
    ALLOWED_ORIGINS:        z.string().transform(s => s.split(',')),
  },
  client: {
    NEXT_PUBLIC_APP_URL:          z.string().url(),
    NEXT_PUBLIC_SUPABASE_URL:     z.string().url(),
    NEXT_PUBLIC_SUPABASE_ANON_KEY: z.string().min(1),
    NEXT_PUBLIC_STRIPE_PK:        z.string().startsWith('pk_'),
  },
  runtimeEnv: {
    DATABASE_URL:              process.env.DATABASE_URL,
    // ... all vars mapped
  },
  skipValidation:              process.env.SKIP_ENV_VALIDATION === 'true',
  emptyStringAsUndefined:      true,
});

// Usage: import { env } from './env'; env.DATABASE_URL
```

### Per-environment .env files — loading order

```
.env                 # base defaults committed to git (no secrets, only non-sensitive defaults)
.env.local           # local overrides — NEVER committed (gitignored)
.env.development     # dev-specific values — committed (no secrets)
.env.development.local  # local dev overrides — NEVER committed
.env.test            # test environment — committed (no secrets, uses test db)
.env.production      # prod defaults only — committed (actual secrets injected by platform)
```

---

## 2. Secret Management by Environment {#secrets}

### Decision matrix: which store per environment

| Environment | Secret Store | How injected |
|-------------|-------------|--------------|
| Local dev | `.env.local` | Developer's machine only, gitignored |
| CI/CD (tests) | GitHub Secrets | `${{ secrets.VAR }}` in workflow |
| Staging (K8s) | AWS SSM Parameter Store | External Secrets Operator → K8s Secret |
| Production (K8s) | HashiCorp Vault or AWS SSM (SecureString) | External Secrets Operator → K8s Secret |
| Vercel/Netlify | Platform env vars | Dashboard or `vercel env add` CLI |
| Cloudflare Workers | Wrangler Secrets | `wrangler secret put VAR_NAME` |

### External Secrets Operator — K8s → AWS SSM

```yaml
# infrastructure/k8s/secrets/api-secrets.yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: api-secrets
  namespace: production
spec:
  refreshInterval: 5m                # re-fetch every 5 minutes
  secretStoreRef:
    name: aws-ssm-store
    kind: ClusterSecretStore
  target:
    name: api-secrets                # K8s Secret name created
    creationPolicy: Owner
    deletionPolicy: Retain
  data:
    - secretKey: DATABASE_URL        # key in K8s Secret
      remoteRef:
        key: /production/api/DATABASE_URL   # path in SSM
    - secretKey: JWT_SECRET
      remoteRef:
        key: /production/api/JWT_SECRET
    - secretKey: STRIPE_SECRET_KEY
      remoteRef:
        key: /production/api/STRIPE_SECRET_KEY
---
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: aws-ssm-store
spec:
  provider:
    aws:
      service: ParameterStore
      region: eu-west-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
            namespace: external-secrets
```

### SSM parameter naming convention

```bash
# Convention: /environment/service/VARIABLE_NAME
/production/api/DATABASE_URL
/production/api/JWT_SECRET
/production/worker/REDIS_URL
/staging/api/DATABASE_URL

# Push a secret to SSM
aws ssm put-parameter \
  --name "/production/api/JWT_SECRET" \
  --value "$(openssl rand -hex 32)" \
  --type SecureString \
  --key-id alias/production-secrets \
  --overwrite

# Rotate a secret (update + restart pods)
aws ssm put-parameter --name "/production/api/JWT_SECRET" --value "NEW_VALUE" --overwrite
kubectl rollout restart deployment/api -n production
```

### Secret rotation checklist

```
□ JWT signing keys — rotate every 90 days (support 2 active keys during rollover)
□ Database passwords — rotate every 30 days via Vault dynamic secrets
□ API keys (third-party) — rotate every 90 days; alert 7 days before expiry
□ Webhook secrets — rotate on any suspected exposure
□ Never log secrets — use structured logging with redact middleware
□ Never commit secrets — TruffleHog in pre-commit hook + CI gate
```

---

## 3. Docker Compose — Full Dev Stack {#compose}

```yaml
# docker-compose.yml — full local dev stack with hot-reload
name: myproject

x-common: &common
  restart: unless-stopped
  networks: [dev]

services:
  # ── WEB (Next.js) ──────────────────────────────────────────
  web:
    <<: *common
    build:
      context: ./apps/web
      dockerfile: Dockerfile.dev
      target: development
    ports: ["3000:3000"]
    environment:
      NODE_ENV: development
      NEXT_PUBLIC_API_URL: http://localhost:4000
      NEXT_PUBLIC_SUPABASE_URL: ${SUPABASE_URL}
      NEXT_PUBLIC_SUPABASE_ANON_KEY: ${SUPABASE_ANON_KEY}
    volumes:
      - ./apps/web:/app                    # source mount for hot-reload
      - /app/node_modules                  # anonymous volume: don't overwrite container modules
      - /app/.next
    depends_on:
      api:
        condition: service_healthy
    command: pnpm dev

  # ── API (NestJS) ───────────────────────────────────────────
  api:
    <<: *common
    build:
      context: ./apps/api
      dockerfile: Dockerfile.dev
      target: development
    ports: ["4000:4000", "9229:9229"]      # 9229 = Node.js debugger
    environment:
      NODE_ENV: development
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/mydb
      REDIS_URL: redis://redis:6379
      SKIP_ENV_VALIDATION: "false"
    volumes:
      - ./apps/api:/app
      - /app/node_modules
      - /app/dist
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: pnpm start:debug             # --inspect=0.0.0.0:9229
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:4000/api/v1/health"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  # ── WORKER (BullMQ) ────────────────────────────────────────
  worker:
    <<: *common
    build:
      context: ./apps/api
      dockerfile: Dockerfile.dev
    environment:
      NODE_ENV: development
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/mydb
      REDIS_URL: redis://redis:6379
    volumes:
      - ./apps/api:/app
      - /app/node_modules
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    command: pnpm start:worker

  # ── POSTGRES ───────────────────────────────────────────────
  postgres:
    <<: *common
    image: postgres:16-alpine
    ports: ["5432:5432"]
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infra/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d mydb"]
      interval: 5s
      timeout: 3s
      retries: 10

  # ── REDIS ──────────────────────────────────────────────────
  redis:
    <<: *common
    image: redis:7-alpine
    ports: ["6379:6379"]
    command: redis-server --save 60 1 --loglevel warning
    volumes: [redis_data:/data]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 10

  # ── REDIS INSIGHT (UI) ─────────────────────────────────────
  redis-ui:
    <<: *common
    image: redislabs/redisinsight:latest
    ports: ["8001:8001"]
    depends_on: [redis]
    profiles: [tools]                       # opt-in: docker compose --profile tools up

  # ── MAILPIT (local email) ──────────────────────────────────
  mailpit:
    <<: *common
    image: axllent/mailpit:latest
    ports:
      - "1025:1025"                          # SMTP
      - "8025:8025"                          # Web UI
    profiles: [tools]

  # ── MINIO (local S3) ───────────────────────────────────────
  minio:
    <<: *common
    image: minio/minio:latest
    ports: ["9000:9000", "9001:9001"]
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes: [minio_data:/data]
    command: server /data --console-address ":9001"
    profiles: [tools]

  # ── GRAFANA + PROMETHEUS (local observability) ─────────────
  prometheus:
    <<: *common
    image: prom/prometheus:latest
    ports: ["9090:9090"]
    volumes:
      - ./infra/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    profiles: [observability]

  grafana:
    <<: *common
    image: grafana/grafana:latest
    ports: ["3001:3000"]
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./infra/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
    depends_on: [prometheus]
    profiles: [observability]

networks:
  dev:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  minio_data:
  grafana_data:
```

```bash
# Dev workflow commands
docker compose up -d                          # start core stack
docker compose --profile tools up -d         # + Redis UI, Mailpit, MinIO
docker compose --profile observability up -d  # + Prometheus, Grafana
docker compose logs -f api worker             # tail specific service logs
docker compose exec postgres psql -U postgres -d mydb  # psql into dev db
docker compose down -v                        # destroy everything including volumes
```

---

## 4. GitHub Actions — Complete CI/CD Pipelines {#cicd}

### Pipeline A — Web App (Next.js to Vercel)

```yaml
# .github/workflows/web-ci.yml
name: Web CI/CD

on:
  push:
    branches: [main, develop]
    paths: [apps/web/**, packages/**]
  pull_request:
    branches: [main]
    paths: [apps/web/**, packages/**]

env:
  TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
  TURBO_TEAM: ${{ secrets.TURBO_TEAM }}

jobs:
  # ── JOB 1: Quality gates ──────────────────────────────────
  quality:
    name: Lint, Type-check, Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 2 }

      - uses: pnpm/action-setup@v3
        with: { version: 9 }

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm

      - run: pnpm install --frozen-lockfile

      - name: Lint
        run: pnpm turbo lint --filter=web...

      - name: Type-check
        run: pnpm turbo type-check --filter=web...

      - name: Unit tests
        run: pnpm turbo test --filter=web...
        env:
          DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}

      - name: E2E tests (PR only)
        if: github.event_name == 'pull_request'
        run: pnpm turbo test:e2e --filter=web...
        env:
          BASE_URL: ${{ secrets.STAGING_URL }}

  # ── JOB 2: Security scan ──────────────────────────────────
  security:
    name: Security Gates
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Secret scan — TruffleHog
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}

      - name: Dependency audit
        run: pnpm audit --audit-level=high

  # ── JOB 3: Deploy to Vercel ───────────────────────────────
  deploy-preview:
    name: Deploy Preview
    needs: [quality, security]
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    environment:
      name: preview
      url: ${{ steps.deploy.outputs.url }}
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with: { version: 9 }
      - run: pnpm install --frozen-lockfile
      - name: Deploy to Vercel
        id: deploy
        run: |
          URL=$(pnpm vercel --token=${{ secrets.VERCEL_TOKEN }} \
            --scope=${{ secrets.VERCEL_ORG_ID }} \
            --yes)
          echo "url=$URL" >> $GITHUB_OUTPUT
        env:
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID_WEB }}

  deploy-production:
    name: Deploy Production
    needs: [quality, security]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://yourdomain.com
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with: { version: 9 }
      - run: pnpm install --frozen-lockfile
      - name: Deploy to Vercel Production
        run: pnpm vercel --prod --token=${{ secrets.VERCEL_TOKEN }} --yes
        env:
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID_WEB }}
```

### Pipeline B — API Service (NestJS to Kubernetes via ECR)

```yaml
# .github/workflows/api-ci.yml
name: API CI/CD

on:
  push:
    branches: [main, develop]
    paths: [apps/api/**, packages/**]
  pull_request:
    branches: [main]
    paths: [apps/api/**, packages/**]

env:
  ECR_REGISTRY: ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.eu-west-1.amazonaws.com
  ECR_REPOSITORY: myproject/api
  EKS_CLUSTER: myproject-production

jobs:
  quality:
    name: Lint, Type-check, Test
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env: { POSTGRES_PASSWORD: postgres, POSTGRES_DB: testdb }
        ports: ["5432:5432"]
        options: --health-cmd pg_isready --health-interval 5s --health-retries 10
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
        options: --health-cmd "redis-cli ping" --health-interval 5s

    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: pnpm }
      - run: pnpm install --frozen-lockfile

      - run: pnpm turbo lint --filter=api...
      - run: pnpm turbo type-check --filter=api...
      - name: Test with coverage
        run: pnpm turbo test:cov --filter=api...
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/testdb
          REDIS_URL: redis://localhost:6379
          JWT_SECRET: testsecretfortestingonly64characterslongminimumrequireddontuse
          SKIP_ENV_VALIDATION: "true"

  security:
    name: Security Gates
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: trufflesecurity/trufflehog@main
        with: { path: ./, base: ${{ github.event.repository.default_branch }} }
      - run: pnpm audit --audit-level=high
      - name: SAST — Semgrep
        uses: semgrep/semgrep-action@v1
        with:
          config: p/nodejs p/secrets p/owasp-top-ten

  build-push:
    name: Build & Push Image
    needs: [quality, security]
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.version }}
      image-digest: ${{ steps.build.outputs.digest }}

    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: eu-west-1

      - name: Login to ECR
        id: ecr-login
        uses: aws-actions/amazon-ecr-login@v2

      - name: Docker metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.ECR_REGISTRY }}/${{ env.ECR_REPOSITORY }}
          tags: |
            type=sha,prefix=,format=short
            type=ref,event=branch
            type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and push
        id: build
        uses: docker/build-push-action@v6
        with:
          context: apps/api
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          provenance: true
          sbom: true                         # software bill of materials

      - name: Scan image — Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.ECR_REGISTRY }}/${{ env.ECR_REPOSITORY }}:${{ steps.meta.outputs.version }}
          exit-code: 1
          severity: CRITICAL,HIGH

  deploy-staging:
    name: Deploy to Staging
    needs: build-push
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://api.staging.yourdomain.com

    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: eu-west-1
      - run: aws eks update-kubeconfig --name myproject-staging --region eu-west-1

      - name: Deploy with Helm
        run: |
          helm upgrade --install api-staging ./infra/helm/api \
            --namespace staging \
            --create-namespace \
            --set image.tag=${{ needs.build-push.outputs.image-tag }} \
            --set image.repository=${{ env.ECR_REGISTRY }}/${{ env.ECR_REPOSITORY }} \
            --values ./infra/helm/api/values.staging.yaml \
            --wait --timeout 5m \
            --atomic

      - name: Smoke test
        run: |
          sleep 10
          curl -f https://api.staging.yourdomain.com/api/v1/health || exit 1

  deploy-production:
    name: Deploy to Production
    needs: [build-push, deploy-staging]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: production               # requires manual approval in GitHub
      url: https://api.yourdomain.com

    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: eu-west-1
      - run: aws eks update-kubeconfig --name myproject-production --region eu-west-1

      - name: Canary deploy (10% traffic)
        run: |
          helm upgrade --install api-canary ./infra/helm/api \
            --namespace production \
            --set image.tag=${{ needs.build-push.outputs.image-tag }} \
            --set image.repository=${{ env.ECR_REGISTRY }}/${{ env.ECR_REPOSITORY }} \
            --values ./infra/helm/api/values.production.yaml \
            --set replicaCount=1 \
            --wait --timeout 5m

      - name: Canary health check (5 minutes)
        run: |
          for i in $(seq 1 30); do
            curl -f https://api.yourdomain.com/api/v1/health || exit 1
            sleep 10
          done

      - name: Full production deploy
        run: |
          helm upgrade --install api ./infra/helm/api \
            --namespace production \
            --set image.tag=${{ needs.build-push.outputs.image-tag }} \
            --values ./infra/helm/api/values.production.yaml \
            --wait --timeout 10m \
            --atomic

      - name: Remove canary
        if: always()
        run: helm uninstall api-canary --namespace production || true
```

### Pipeline C — Mobile (Expo EAS)

```yaml
# .github/workflows/mobile-ci.yml
name: Mobile CI/CD

on:
  push:
    branches: [main, develop]
    paths: [apps/mobile/**, packages/**]
  pull_request:
    branches: [main]
    paths: [apps/mobile/**]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm turbo lint type-check test --filter=mobile...

  eas-preview:
    name: EAS Preview Build
    needs: quality
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: eas update --branch pr-${{ github.event.number }} --message "PR #${{ github.event.number }}"
        working-directory: apps/mobile

  eas-staging:
    name: EAS Staging Build
    needs: quality
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: eas build --platform all --profile staging --non-interactive
        working-directory: apps/mobile

  eas-production:
    name: EAS Production Submit
    needs: quality
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: eas build --platform all --profile production --non-interactive
        working-directory: apps/mobile
      - run: eas submit --platform all --latest --non-interactive
        working-directory: apps/mobile
```

### Rollback workflow

```yaml
# .github/workflows/rollback.yml
name: Emergency Rollback

on:
  workflow_dispatch:
    inputs:
      service:
        description: Service to rollback (api / worker / web)
        required: true
        type: choice
        options: [api, worker, web]
      revision:
        description: Helm revision to rollback to (leave blank for previous)
        required: false

jobs:
  rollback:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: eu-west-1
      - run: aws eks update-kubeconfig --name myproject-production --region eu-west-1
      - name: Rollback
        run: |
          REVISION=${{ inputs.revision }}
          if [ -z "$REVISION" ]; then
            helm rollback ${{ inputs.service }} --namespace production --wait
          else
            helm rollback ${{ inputs.service }} $REVISION --namespace production --wait
          fi
      - name: Verify
        run: kubectl rollout status deployment/${{ inputs.service }} -n production --timeout=5m
```

---

## 5. Helm Charts — Production Templates {#helm}

```
infra/helm/api/
├── Chart.yaml
├── values.yaml              # base defaults
├── values.staging.yaml      # staging overrides
├── values.production.yaml   # production overrides
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── hpa.yaml
    ├── pdb.yaml
    ├── serviceaccount.yaml
    ├── configmap.yaml
    ├── externalsecret.yaml
    └── _helpers.tpl
```

```yaml
# Chart.yaml
apiVersion: v2
name: api
description: OMEGA API Helm Chart
type: application
version: 0.1.0
appVersion: "1.0.0"
dependencies:
  - name: common
    version: 2.x.x
    repository: https://charts.bitnami.com/bitnami
```

```yaml
# values.yaml — base defaults
replicaCount: 2

image:
  repository: 123456789.dkr.ecr.eu-west-1.amazonaws.com/myproject/api
  pullPolicy: IfNotPresent
  tag: latest

service:
  type: ClusterIP
  port: 80
  targetPort: 4000

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-production
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
  hosts:
    - host: api.yourdomain.com
      paths: [{ path: /, pathType: Prefix }]
  tls:
    - secretName: api-tls
      hosts: [api.yourdomain.com]

resources:
  requests: { cpu: 100m, memory: 256Mi }
  limits:   { cpu: 500m, memory: 512Mi }

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

podDisruptionBudget:
  enabled: true
  minAvailable: 1

livenessProbe:
  httpGet: { path: /api/v1/health, port: 4000 }
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet: { path: /api/v1/health/ready, port: 4000 }
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 3

startupProbe:
  httpGet: { path: /api/v1/health, port: 4000 }
  failureThreshold: 30
  periodSeconds: 10

envFrom:
  - secretRef:
      name: api-secrets             # created by ExternalSecret

env:
  - name: NODE_ENV
    value: production
  - name: PORT
    value: "4000"

securityContext:
  runAsNonRoot: true
  runAsUser: 1001
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities: { drop: [ALL] }

serviceAccount:
  create: true
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/api-service-role
```

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "api.fullname" . }}
  labels: {{ include "api.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels: {{ include "api.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels: {{ include "api.selectorLabels" . | nindent 8 }}
      annotations:
        checksum/secret: {{ include (print $.Template.BasePath "/externalsecret.yaml") . | sha256sum }}
    spec:
      serviceAccountName: {{ include "api.serviceAccountName" . }}
      securityContext: {{- toYaml .Values.podSecurityContext | nindent 8 }}
      terminationGracePeriodSeconds: 60
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: {{ .Values.service.targetPort }}
          envFrom: {{- toYaml .Values.envFrom | nindent 12 }}
          env: {{- toYaml .Values.env | nindent 12 }}
          resources: {{- toYaml .Values.resources | nindent 12 }}
          securityContext: {{- toYaml .Values.securityContext | nindent 12 }}
          livenessProbe: {{- toYaml .Values.livenessProbe | nindent 12 }}
          readinessProbe: {{- toYaml .Values.readinessProbe | nindent 12 }}
          startupProbe: {{- toYaml .Values.startupProbe | nindent 12 }}
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 5"]  # drain connections before SIGTERM
```

---

## 6. Branching Strategy & PR Protocol {#branching}

### Trunk-based development (recommended for solo/small team)

```
main                    production — protected, never commit directly
  └── develop           integration — auto-deploys to staging
        ├── feat/xxx    feature branches — max 2 days lifetime
        ├── fix/xxx     bugfix branches — max 1 day lifetime
        └── chore/xxx   maintenance branches
```

### Branch protection rules (GitHub Settings → Branches)

```
main:
  require_pull_request_before_merging: true
  required_approving_review_count: 1          # or 0 for solo dev
  dismiss_stale_reviews: true
  require_status_checks:
    - quality
    - security
  require_branches_to_be_up_to_date: true
  restrict_pushes: true
  allow_force_pushes: false
  allow_deletions: false
```

### PR size limits (enforced by Danger.js or GitHub Action)

```javascript
// dangerfile.ts
import { danger, warn, fail } from 'danger';

const modified = danger.git.modified_files;
const created = danger.git.created_files;
const linesAdded = danger.github.pr.additions;

// Size limits
if (linesAdded > 500) fail('PR is too large (>500 lines). Split into smaller PRs.');
if (linesAdded > 300) warn('PR is getting large (>300 lines). Consider splitting.');

// Always require tests with code changes
const hasCodeChanges = modified.some(f => f.match(/src\/.*\.(ts|tsx)$/));
const hasTestChanges = modified.some(f => f.match(/\.(test|spec)\.(ts|tsx)$/));
if (hasCodeChanges && !hasTestChanges) warn('Code changes without tests detected.');

// Require ADR for architectural changes
const hasArchChanges = modified.some(f => f.includes('architecture') || f.includes('schema.prisma'));
const hasADR = created.some(f => f.includes('14-ADRs/'));
if (hasArchChanges && !hasADR) warn('Architectural change detected. Consider writing an ADR.');
```

### PR template

```markdown
<!-- .github/pull_request_template.md -->
## Summary
<!-- One sentence: what does this PR do and why? -->

## Changes
- [ ] Feature / fix / refactor / chore (delete as appropriate)
- 

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] E2E tested locally
- [ ] Manual testing steps:

## Security
- [ ] No secrets committed
- [ ] Input validation applied
- [ ] RBAC checked (if applicable)
- [ ] RLS policies updated (if DB change)

## Documentation
- [ ] ADR written (if architectural change)
- [ ] Vault updated
- [ ] README updated (if public API change)

## Rollback plan
<!-- How to revert this if it causes issues in production -->
```

---

## 7. Ingress, TLS & cert-manager {#ingress}

### cert-manager installation

```bash
# Install cert-manager
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set crds.enabled=true

# Verify
kubectl get pods -n cert-manager
```

### ClusterIssuer — Let's Encrypt

```yaml
# infra/k8s/cert-manager/cluster-issuer.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-production
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: ops@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-production
    solvers:
      - http01:
          ingress:
            ingressClassName: nginx
---
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging            # for testing — no rate limits
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: ops@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-staging
    solvers:
      - http01:
          ingress:
            ingressClassName: nginx
```

### nginx-ingress installation

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/aws-load-balancer-type"=nlb \
  --set controller.metrics.enabled=true \
  --set controller.podAnnotations."prometheus\.io/scrape"=true
```

### Production Ingress with TLS, rate limiting, and security headers

```yaml
# infra/k8s/ingress/api-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  namespace: production
  annotations:
    # TLS
    cert-manager.io/cluster-issuer: letsencrypt-production

    # Rate limiting
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    nginx.ingress.kubernetes.io/rate-limit-connections: "20"

    # Security headers
    nginx.ingress.kubernetes.io/configuration-snippet: |
      add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
      add_header X-Frame-Options "DENY" always;
      add_header X-Content-Type-Options "nosniff" always;
      add_header Referrer-Policy "strict-origin-when-cross-origin" always;
      add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;

    # Connection limits
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "10"

    # WebSocket support (for SSE / WS endpoints)
    nginx.ingress.kubernetes.io/proxy-http-version: "1.1"
    nginx.ingress.kubernetes.io/proxy-set-headers: "ingress-nginx/custom-headers"

spec:
  ingressClassName: nginx
  tls:
    - hosts: [api.yourdomain.com]
      secretName: api-tls
  rules:
    - host: api.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api
                port: { number: 80 }
```

---

## 8. Service Mesh — Zero Trust mTLS with Istio {#mesh}

### Istio installation (production-grade)

```bash
# Install Istio with production profile
istioctl install --set profile=production -y

# Verify installation
kubectl get pods -n istio-system
istioctl verify-install

# Label namespace for automatic sidecar injection
kubectl label namespace production istio-injection=enabled
kubectl label namespace staging istio-injection=enabled
```

### Strict mTLS — every service must prove identity

```yaml
# infra/k8s/istio/peer-auth.yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT          # reject all plaintext — no exceptions
---
# Mesh-wide default (applies to all namespaces)
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT
```

### Authorization Policy — explicit allow, deny by default

```yaml
# infra/k8s/istio/authz-api.yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: api-allow
  namespace: production
spec:
  selector:
    matchLabels:
      app: api
  action: ALLOW
  rules:
    # Allow ingress controller to reach API
    - from:
        - source:
            principals: ["cluster.local/ns/ingress-nginx/sa/ingress-nginx"]
      to:
        - operation:
            methods: ["GET", "POST", "PUT", "PATCH", "DELETE"]

    # Allow worker to call API internally
    - from:
        - source:
            principals: ["cluster.local/ns/production/sa/worker"]
      to:
        - operation:
            methods: ["POST"]
            paths: ["/internal/*"]
---
# Deny all by default (implicit — no ALLOW rule = deny)
# But make it explicit for clarity:
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: deny-all
  namespace: production
spec:
  {}    # empty spec = deny all — must have explicit ALLOW rules above
```

### Traffic management — circuit breaker and retries

```yaml
# infra/k8s/istio/destination-rule.yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: api
  namespace: production
spec:
  host: api
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        h2UpgradePolicy: UPGRADE
        http1MaxPendingRequests: 100
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 60s
      maxEjectionPercent: 50
    retries:
      attempts: 3
      perTryTimeout: 10s
      retryOn: 5xx,reset,connect-failure
```

---

## 9. Container Registry Flow {#registry}

### GHCR (GitHub Container Registry) — simplest for open/private repos

```yaml
# In GitHub Actions workflow
- name: Login to GHCR
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}    # built-in, no secret needed

- name: Build and push
  uses: docker/build-push-action@v6
  with:
    push: true
    tags: ghcr.io/${{ github.repository_owner }}/api:${{ github.sha }}
```

### ECR (AWS) — for EKS deployments

```yaml
# In GitHub Actions — requires OIDC (no long-lived keys)
- name: Configure AWS credentials via OIDC
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789:role/github-actions-deploy
    aws-region: eu-west-1

- name: Login to ECR
  id: ecr
  uses: aws-actions/amazon-ecr-login@v2

- name: Build and push
  uses: docker/build-push-action@v6
  with:
    push: true
    tags: ${{ steps.ecr.outputs.registry }}/myproject/api:${{ github.sha }}
```

```hcl
# Terraform — ECR repository with lifecycle policy
resource "aws_ecr_repository" "api" {
  name                 = "myproject/api"
  image_tag_mutability = "IMMUTABLE"
  force_delete         = false

  image_scanning_configuration {
    scan_on_push = true      # automatic vulnerability scan on every push
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.ecr.arn
  }
}

resource "aws_ecr_lifecycle_policy" "api" {
  repository = aws_ecr_repository.api.name
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 20 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 20
      }
      action = { type = "expire" }
    }]
  })
}
```

---

## 10. Edge Functions {#edge}

### Cloudflare Workers — use cases and limits

```
Use for:                           Avoid for:
  Auth validation at edge            Database writes (use API instead)
  A/B testing / feature flags        Long-running tasks (max 30s CPU)
  Rate limiting (Durable Objects)    Heavy computation
  Geolocation-based routing          Large binary processing
  Request/response transformation    Node.js-specific modules
  Bot detection
```

```typescript
// workers/auth-middleware/index.ts
import { Env } from './types';

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // Skip auth for public routes
    const PUBLIC_PATHS = ['/api/v1/auth/', '/api/v1/health'];
    if (PUBLIC_PATHS.some(p => url.pathname.startsWith(p))) {
      return fetch(request);
    }

    // Validate JWT at the edge — no DB call
    const authHeader = request.headers.get('Authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const token = authHeader.slice(7);
    try {
      const payload = await verifyJWT(token, env.JWT_PUBLIC_KEY);

      // Forward validated claims to origin — avoid re-verification
      const modifiedRequest = new Request(request, {
        headers: {
          ...Object.fromEntries(request.headers),
          'X-User-Id': payload.sub,
          'X-User-Role': payload.role,
          'X-Workspace-Id': payload.workspaceId,
        },
      });
      return fetch(modifiedRequest);
    } catch {
      return new Response(JSON.stringify({ error: 'Invalid token' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }
  },
};

async function verifyJWT(token: string, publicKeyPem: string): Promise<Record<string, string>> {
  const key = await crypto.subtle.importKey(
    'spki',
    pemToBuffer(publicKeyPem),
    { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' },
    false,
    ['verify'],
  );
  // ... decode and verify
  return JSON.parse(atob(token.split('.')[1]));
}
```

```toml
# wrangler.toml
name = "auth-middleware"
main = "src/index.ts"
compatibility_date = "2024-01-01"
compatibility_flags = ["nodejs_compat"]

[vars]
ENVIRONMENT = "production"

[[routes]]
pattern = "api.yourdomain.com/*"
zone_name = "yourdomain.com"

[[durable_objects.bindings]]
name = "RATE_LIMITER"
class_name = "RateLimiter"
```

### Vercel Edge Functions — middleware

```typescript
// middleware.ts (Next.js)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export const config = {
  matcher: ['/dashboard/:path*', '/api/protected/:path*'],
  runtime: 'edge',
};

export function middleware(request: NextRequest) {
  const token = request.cookies.get('session-token')?.value
    ?? request.headers.get('Authorization')?.replace('Bearer ', '');

  if (!token) {
    return NextResponse.redirect(new URL('/sign-in', request.url));
  }

  // Clone request with validated user context
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set('x-user-context', 'validated');

  return NextResponse.next({ request: { headers: requestHeaders } });
}
```

---

## 11. Inter-Service Communication {#communication}

### Synchronous: internal HTTP with service discovery

```typescript
// Internal service client — NestJS HttpModule with resilience
@Injectable()
export class UserServiceClient {
  private readonly baseUrl = process.env.USER_SERVICE_URL ?? 'http://user-service.production.svc.cluster.local';

  constructor(
    private readonly http: HttpService,
    private readonly logger: Logger,
  ) {}

  async getUser(userId: string, traceId: string): Promise<User> {
    const start = Date.now();
    try {
      const { data } = await firstValueFrom(
        this.http.get<User>(`${this.baseUrl}/internal/users/${userId}`, {
          headers: {
            'X-Trace-Id':     traceId,
            'X-Service-Name': 'api',
            'X-Api-Key':      process.env.INTERNAL_API_KEY,  // service-to-service auth
          },
          timeout: 5000,
        }).pipe(
          retry({
            count: 3,
            delay: (error, attempt) => {
              if (error.status === 404) throwError(() => error);  // don't retry 404
              return timer(Math.pow(2, attempt) * 100);           // exponential backoff
            },
          }),
        ),
      );
      this.logger.log({ event: 'user_service.get', userId, ms: Date.now() - start });
      return data;
    } catch (error) {
      this.logger.error({ event: 'user_service.get_failed', userId, error: error.message });
      throw new ServiceUnavailableException('User service unavailable');
    }
  }
}
```

### Asynchronous: events via Redis Streams

```typescript
// Event publisher
@Injectable()
export class EventPublisher {
  constructor(private readonly redis: Redis) {}

  async publish<T>(stream: string, event: { type: string; data: T; correlationId: string }): Promise<string> {
    const id = await this.redis.xadd(
      stream,
      '*',                       // auto-generate ID
      'type',        event.type,
      'data',        JSON.stringify(event.data),
      'correlationId', event.correlationId,
      'publishedAt', new Date().toISOString(),
    );
    return id;
  }
}

// Event consumer (worker)
@Injectable()
export class EventConsumer implements OnModuleInit {
  private readonly GROUP = 'api-consumer-group';

  async onModuleInit() {
    // Create consumer group if it doesn't exist
    try {
      await this.redis.xgroup('CREATE', 'order.events', this.GROUP, '0', 'MKSTREAM');
    } catch (e) {
      if (!e.message.includes('BUSYGROUP')) throw e;
    }
    this.startConsuming();
  }

  private async startConsuming() {
    while (true) {
      const messages = await this.redis.xreadgroup(
        'GROUP', this.GROUP, 'worker-1',
        'COUNT', '10',
        'BLOCK', '1000',
        'STREAMS', 'order.events', '>',
      );

      for (const [stream, entries] of messages ?? []) {
        for (const [id, fields] of entries) {
          await this.processEvent(id, Object.fromEntries(fields));
          await this.redis.xack(stream, this.GROUP, id);
        }
      }
    }
  }
}
```

### gRPC — high-throughput internal APIs

```protobuf
// proto/user.proto
syntax = "proto3";
package user;

service UserService {
  rpc GetUser (GetUserRequest) returns (UserResponse);
  rpc ListUsers (ListUsersRequest) returns (stream UserResponse);
}

message GetUserRequest { string user_id = 1; }
message UserResponse {
  string id    = 1;
  string email = 2;
  string role  = 3;
}
```

```typescript
// NestJS gRPC microservice
@GrpcMethod('UserService', 'GetUser')
async getUser(request: GetUserRequest, metadata: Metadata): Promise<UserResponse> {
  const user = await this.usersService.findById(request.userId);
  return { id: user.id, email: user.email, role: user.role };
}
```

### WebSocket / SSE for real-time

```typescript
// SSE endpoint (NestJS)
@Get('events')
@Sse()
async streamEvents(@CurrentUser() user: User): Promise<Observable<MessageEvent>> {
  return new Observable(subscriber => {
    const handler = (event: SystemEvent) => {
      if (event.workspaceId === user.workspaceId) {
        subscriber.next({ data: event, type: event.type, id: event.id });
      }
    };

    this.eventEmitter.on('system.*', handler);

    // Heartbeat to keep connection alive
    const heartbeat = setInterval(() => {
      subscriber.next({ data: { type: 'heartbeat' } });
    }, 30_000);

    return () => {
      this.eventEmitter.off('system.*', handler);
      clearInterval(heartbeat);
    };
  });
}
```

---

## 12. Debug & Maintainability Protocols {#debug}

### Local debug setup — VSCode launch.json

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug API (Docker)",
      "type": "node",
      "request": "attach",
      "port": 9229,
      "address": "localhost",
      "localRoot": "${workspaceFolder}/apps/api",
      "remoteRoot": "/app",
      "restart": true,
      "skipFiles": ["<node_internals>/**"]
    },
    {
      "name": "Debug API (Local)",
      "type": "node",
      "request": "launch",
      "runtimeExecutable": "pnpm",
      "runtimeArgs": ["start:debug"],
      "cwd": "${workspaceFolder}/apps/api",
      "envFile": "${workspaceFolder}/apps/api/.env.local",
      "skipFiles": ["<node_internals>/**"],
      "sourceMaps": true,
      "outFiles": ["${workspaceFolder}/apps/api/dist/**/*.js"]
    }
  ]
}
```

### Structured logging standard

```typescript
// Every log must have these fields
logger.info({
  event:       'order.created',           // machine-readable event name
  orderId:     order.id,
  userId:      user.id,
  workspaceId: user.workspaceId,
  durationMs:  Date.now() - startTime,
  traceId:     request.headers['x-trace-id'],
  // NEVER: password, token, secret, card number, PII
});
```

### Debugging live production (read-only)

```bash
# 1. Get pod shell (ephemeral debug container — no exec needed)
kubectl debug -it deployment/api -n production \
  --image=curlimages/curl:latest \
  --target=api

# 2. Check live env (redact sensitive values first)
kubectl exec -it deployment/api -n production -- env | grep -v SECRET | grep -v KEY | grep -v PASSWORD

# 3. Port-forward to debug endpoint locally (never expose /metrics publicly)
kubectl port-forward deployment/api 4000:4000 -n production

# 4. Thread dump / heap snapshot
kubectl exec deployment/api -n production -- kill -USR2 1   # Node.js: write heap snapshot
```

### Code maintainability gates

```
Every module must have:
□ Single responsibility — one reason to change
□ No files > 300 lines — split if larger
□ No functions > 50 lines — extract if larger
□ No more than 3 levels of nesting — early returns
□ Dependency injection — never new Service() inside a service
□ No magic numbers — named constants only
□ All public methods have JSDoc with @param and @returns
□ No commented-out code — delete or put in a branch
```

---

## 13. Scalability Runbooks {#scalability}

### Scale-out checklist (before going viral)

```
□ HPA configured with CPU 70% + Memory 80% targets
□ Cluster autoscaler installed — nodes scale automatically
□ Database connection pool sized: min=5, max=(2×CPU cores)
□ PgBouncer in front of Postgres (transaction mode)
□ Redis for session storage — not in-memory
□ All assets on CDN (CloudFront / Cloudflare)
□ Rate limiting at edge (Cloudflare) + API level
□ Async all heavy operations (email, PDF, image resize) via BullMQ
□ Database read replicas for heavy read queries
□ Cursor pagination — never OFFSET on large tables
□ Images: next/image with WebP + lazy loading
□ API response caching: Cache-Control headers + Redis for expensive queries
```

### Horizontal scaling — adding a new service instance

```bash
# Manual scale for immediate traffic spike
kubectl scale deployment api --replicas=10 -n production

# Verify all pods ready
kubectl rollout status deployment/api -n production

# Watch HPA in real-time
kubectl get hpa api -n production -w

# Scale back down (HPA will take over automatically)
# kubectl scale deployment api --replicas=2 -n production
```

### Database scaling runbook

```sql
-- 1. Check current connections
SELECT count(*), state FROM pg_stat_activity GROUP BY state;

-- 2. Find long-running queries (> 30s)
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '30 seconds'
  AND state = 'active';

-- 3. Kill blocking query (replace PID)
SELECT pg_terminate_backend(PID);

-- 4. Add read replica for read-heavy operations
-- Point read queries to: postgresql://USER:PASS@READ-REPLICA-HOST:5432/DBNAME
-- Write queries: primary host
```
