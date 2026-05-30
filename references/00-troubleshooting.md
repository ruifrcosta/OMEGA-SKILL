# OMEGA Universal Troubleshooting Reference

> Read this FIRST when something is broken. Contains the most common developer pain points
> across every domain OMEGA covers.

---

## 1. TypeScript / Build Errors

### "Cannot find module" after install
```bash
# 1. Clear all caches
rm -rf node_modules .next .turbo dist && pnpm install
# 2. Check tsconfig paths are correct
# 3. For monorepos: pnpm ls to verify package is linked
# 4. Check package.json "main"/"exports" field matches actual output
```

### "Type 'X' is not assignable to type 'Y'"
```
Most common root causes:
- null/undefined not handled (enable strictNullChecks)
- Array vs single item mismatch
- Async function returns Promise<T> but caller expects T

Debug path:
1. Hover over the symbol — see inferred type
2. Use satisfies operator to debug without widening
3. Use type narrowing (typeof, instanceof, discriminated union)
```

### Next.js build fails but dev works
```bash
# Common causes:
# 1. window/document used in RSC — wrap in useEffect or dynamic(() => ..., { ssr: false })
# 2. Missing NEXT_PUBLIC_ prefix on client-side env vars
# 3. Import of ESM-only package — add to experimental.serverComponentsExternalPackages

# Debug:
NEXT_TELEMETRY_DISABLED=1 NODE_OPTIONS="--inspect" next build
```

---

## 2. Database / Prisma / Supabase

### Prisma migration conflicts in team
```bash
# Reset dev DB (never in production)
npx prisma migrate reset

# In CI: always use migrate deploy (not dev)
npx prisma migrate deploy

# Fix drift (prod DB doesn't match schema):
npx prisma migrate diff --from-schema-datamodel prisma/schema.prisma --to-url $DATABASE_URL
```

### Supabase RLS blocking all queries
```sql
-- Debug: disable RLS temporarily to confirm it's the cause
ALTER TABLE your_table DISABLE ROW LEVEL SECURITY;
-- Test, then re-enable
ALTER TABLE your_table ENABLE ROW LEVEL SECURITY;

-- Check if policy exists
SELECT * FROM pg_policies WHERE tablename = 'your_table';

-- Debug current user context
SELECT auth.uid(), auth.role();
```

### Connection pool exhausted
```
Symptoms: "remaining connection slots reserved for non-replication superuser"
Fix:
1. Add PgBouncer between app and Postgres
2. Reduce pool_size in Prisma: datasource db { url = "...?connection_limit=5" }
3. Call prisma.$disconnect() in serverless cleanup
4. Never create a new PrismaClient per request — use singleton
```

### Slow queries in production (not in dev)
```sql
-- Enable pg_stat_statements
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find top offenders
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC LIMIT 20;

-- Check missing indexes
SELECT schemaname, tablename, seq_scan, idx_scan, n_live_tup
FROM pg_stat_user_tables
WHERE seq_scan > idx_scan AND n_live_tup > 5000
ORDER BY seq_scan DESC;
```

---

## 3. Docker / Kubernetes

### Container exits immediately (exit code 1)
```bash
# See the last logs before exit
docker logs --tail 100 container_name
docker logs --since 30s container_name

# Common causes:
# - Missing env var → check REQUIRED_ENV_VARS at startup
# - Port already bound → change PORT or kill existing process
# - Healthcheck failing → check HEALTHCHECK command in Dockerfile
```

### K8s pod in CrashLoopBackOff
```bash
kubectl describe pod <pod-name> -n <namespace>  # look at Events section
kubectl logs <pod-name> -n <namespace> --previous  # logs from crashed container

# Most common causes:
# 1. OOMKilled → increase resources.limits.memory
# 2. Missing ConfigMap/Secret → check volumes and envFrom
# 3. Readiness probe too aggressive → increase initialDelaySeconds
# 4. Wrong image tag → check imagePullPolicy and registry access
```

### K8s service unreachable
```bash
# 1. Check pod is running and ready
kubectl get pods -n <namespace> -l app=<label>

# 2. Check service selector matches pod labels
kubectl describe svc <service-name> -n <namespace>

# 3. Test from inside cluster
kubectl run debug --image=curlimages/curl -it --rm -- sh
curl http://<service-name>.<namespace>.svc.cluster.local:<port>/health

# 4. Check NetworkPolicy isn't blocking
kubectl get networkpolicies -n <namespace>
```

### Helm upgrade fails
```bash
helm upgrade --dry-run --debug my-release ./chart  # always dry-run first
helm history my-release  # see what's deployed
helm rollback my-release 1  # rollback to previous
```

---

## 4. CI/CD / GitHub Actions

### Workflow fails on env vars
```yaml
# Wrong: env var not available in job
env:
  MY_VAR: ${{ secrets.MY_SECRET }}  # ✓ this works for the whole job

# Wrong: secret not added to repo Settings → Secrets and variables → Actions
# Wrong: secret name has spaces or special chars

# Debug: print available env (never print the secret value)
- run: env | grep MY_VAR | wc -c  # should be > 0
```

### Docker build cache not working in Actions
```yaml
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha          # GitHub Actions cache
    cache-to: type=gha,mode=max   # max = cache all layers
    # Ensure Dockerfile uses --mount=type=cache for package managers
```

### Tests pass locally, fail in CI
```
Common causes:
1. Race condition — CI has multiple CPUs, reveals timing issues
2. Missing env var — check .env.test is committed or secrets are set
3. Port conflict — run tests with random ports or use testcontainers
4. Timezone difference — CI is UTC, local might not be
5. File path case sensitivity — CI is Linux (case-sensitive), Mac is not
```

---

## 5. Authentication / JWT / Supabase Auth

### JWT expired but user still sees authenticated UI
```
Cause: client checks local token without verifying expiry
Fix: always decode JWT and check exp before using
```
```typescript
function isTokenExpired(token: string): boolean {
  const payload = JSON.parse(atob(token.split('.')[1]));
  return payload.exp * 1000 < Date.now();
}
// Better: use supabase.auth.getUser() — validates server-side
```

### "Invalid JWT" from Supabase
```
Causes:
1. Wrong SUPABASE_JWT_SECRET (check dashboard → Settings → API)
2. Token from different project (staging token in production)
3. Custom JWT missing required claims (sub, aud, role, iat, exp)

Debug:
- Paste token at jwt.io to decode and inspect claims
- Check aud claim matches "authenticated"
```

### CORS error on API call
```
Symptoms: "blocked by CORS policy" in browser console
Debug steps:
1. Is the error on the preflight (OPTIONS) or the actual request?
2. Check allowed origins in backend: exact match, no trailing slash
3. Check credentials mode: if withCredentials=true, wildcard (*) CORS won't work

Fix in NestJS:
app.enableCors({
  origin: ['https://app.domain.com'],  // explicit, never '*' in production
  credentials: true,
  methods: ['GET','POST','PUT','PATCH','DELETE','OPTIONS'],
  allowedHeaders: ['Content-Type','Authorization','X-Trace-Id'],
});
```

---

## 6. Performance Debugging

### Node.js — high CPU, not high memory
```bash
# Profile with clinic.js
npx clinic flame -- node app.js
# Look for: tight loops, regex on large strings, synchronous fs calls

# Quick check: is event loop blocked?
const { monitorEventLoopDelay } = require('perf_hooks');
const histogram = monitorEventLoopDelay({ resolution: 20 });
histogram.enable();
setInterval(() => {
  console.log('EL delay p99:', histogram.percentile(99), 'ms');
  histogram.reset();
}, 5000);
```

### React — component re-renders too often
```typescript
// Find the culprit
import { useEffect, useRef } from 'react';

function useWhyDidYouUpdate(name: string, props: Record<string, unknown>) {
  const prev = useRef(props);
  useEffect(() => {
    const changed = Object.entries(props).filter(([k, v]) => prev.current[k] !== v);
    if (changed.length) console.log(`[${name}] re-render caused by:`, Object.fromEntries(changed));
    prev.current = props;
  });
}

// Common fixes:
// 1. Object/array created inline → move to useMemo/useCallback
// 2. Context re-renders all consumers → split into smaller contexts
// 3. Zustand selector returns new object every time → use shallow equality
import { useShallow } from 'zustand/react/shallow';
const { a, b } = useStore(useShallow(state => ({ a: state.a, b: state.b })));
```

### Next.js — large bundle size
```bash
ANALYZE=true next build
# Open .next/analyze/client.html
# Look for: duplicate deps, full lodash import, large icons packages

# Common fixes:
import { debounce } from 'lodash-es';        // not 'lodash'
import { CalendarIcon } from 'lucide-react'; // not * from lucide
import dynamic from 'next/dynamic';
const HeavyChart = dynamic(() => import('./HeavyChart'), { ssr: false });
```

---

## 7. Observability — When Alerts Fire

### High error rate (> 2%)
```
Immediate actions (0-5 min):
1. Check Grafana RED dashboard
2. kubectl logs -n production -l app=api --since=5m | grep ERROR
3. Was there a recent deployment? → kubectl rollout history deployment/api
4. If yes → kubectl rollout undo deployment/api

Root cause (5-30 min):
5. Check which endpoints are failing (group by route in logs)
6. Check DB connections (is pool exhausted?)
7. Check upstream dependencies (external APIs, auth service)
```

### Memory leak (pod OOMKilled)
```bash
# 1. Get heap snapshot before restart
kubectl exec -it <pod> -- node -e "process.report.writeReport()"

# 2. Common Node.js leaks:
# - Event emitters not removed → check removeListener calls
# - Closures in setInterval/setTimeout → ensure clearInterval/clearTimeout
# - Prisma/DB client not reused (new client per request)
# - Cache growing unbounded → use LRU cache with max size

# 3. Quick mitigation: increase resources.limits.memory by 50%
# 4. Permanent fix: find and fix leak using clinic.js heapprofiler
```
