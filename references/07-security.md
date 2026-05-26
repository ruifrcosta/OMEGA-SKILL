# Cybersecurity & Hardening Reference

## Table of Contents
1. [Zero Trust Architecture](#zero-trust)
2. [CORS Hardening & Security Headers](#cors)
3. [RBAC — Full Implementation](#rbac)
4. [Secret Management](#secrets)
5. [JWT — Secure Patterns](#jwt)
6. [OWASP Top 10 — Defenses](#owasp)
7. [Automated Pentesting Checklist](#pentesting)
8. [Input Sanitization](#sanitization)

---

## 1. Zero Trust Architecture {#zero-trust}

Default posture: **everything is compromised until proven otherwise.**

- Service-to-service: **mTLS** via Istio or Linkerd. No plain HTTP inside the cluster.
- Tokens: short-lived JWTs with explicit `scope` and `audience` claims. Max 15min for access tokens.
- Production DB access: JIT (just-in-time) ephemeral credentials, multi-party authorization, full audit log.
- Network segmentation: workloads in separate namespaces with explicit NetworkPolicy — deny-all by default.
- Secrets: never in env files, never in git. Vault (HashiCorp) or Sealed Secrets for K8s.

---

## 2. CORS Hardening & Security Headers {#cors}

```nginx
# Production NGINX — copy exactly, adapt origins
# NEVER: Access-Control-Allow-Origin: *

add_header Content-Security-Policy "
  default-src 'self';
  script-src 'self' 'nonce-$csp_nonce';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https://cdn.yourdomain.com;
  connect-src 'self' https://api.yourdomain.com;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
" always;

add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
```

```typescript
// NestJS CORS configuration
const corsConfig = {
  origin: (process.env.ALLOWED_ORIGINS ?? '').split(',').filter(Boolean),
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Trace-ID', 'Idempotency-Key'],
};
// Never: origin: '*'
// Never: origin: true (reflects all origins)
```

---

## 3. RBAC — Full Implementation {#rbac}

### Role Hierarchy

```typescript
// types/rbac.ts
export type Role = 'super_admin' | 'admin' | 'manager' | 'user' | 'viewer';

export type ResourceAction =
  | 'read' | 'write' | 'delete' | 'admin';

export type ResourceScope =
  | 'own'      // user's own data only
  | 'team'     // user's team data
  | 'tenant'   // entire tenant
  | 'global';  // all tenants (super_admin only)

export interface Permission {
  resource: string;       // e.g. 'patient:record', 'order:invoice'
  action: ResourceAction;
  scope: ResourceScope;
}
```

### Guard Implementation (NestJS)

```typescript
// guards/permissions.guard.ts
import { Injectable, CanActivate, ExecutionContext, ForbiddenException } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { AuditLogService } from '../audit/audit-log.service';

@Injectable()
export class PermissionsGuard implements CanActivate {
  constructor(
    private reflector: Reflector,
    private auditLog: AuditLogService,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const required = this.reflector.get<Permission[]>('permissions', context.getHandler());
    if (!required?.length) return true;

    const request = context.switchToHttp().getRequest();
    const user = request.user;

    const granted = required.every(perm =>
      user?.permissions?.some((p: Permission) =>
        p.resource === perm.resource &&
        p.action === perm.action &&
        this.scopeCovers(p.scope, perm.scope)
      )
    );

    // Log EVERY access attempt — success and failure
    await this.auditLog.record({
      userId: user?.id,
      resource: required.map(p => p.resource).join(','),
      action: required.map(p => p.action).join(','),
      granted,
      ip: request.ip,
      traceId: request.headers['x-trace-id'],
    });

    if (!granted) throw new ForbiddenException('Insufficient permissions');
    return true;
  }

  private scopeCovers(granted: ResourceScope, required: ResourceScope): boolean {
    const hierarchy: Record<ResourceScope, number> = {
      own: 1, team: 2, tenant: 3, global: 4
    };
    return hierarchy[granted] >= hierarchy[required];
  }
}

// Usage on controller
@RequirePermissions({ resource: 'patient:record', action: 'read', scope: 'team' })
@UseGuards(PermissionsGuard)
async getPatientRecord(@Param('id') id: string) { ... }
```

### RBAC Permission Matrix (document in vault/12-RBAC/)

```markdown
| Resource | super_admin | admin | manager | user | viewer |
|----------|------------|-------|---------|------|--------|
| user:profile:own | admin | admin | write | write | read |
| user:profile:all | admin | admin | read | — | — |
| order:invoice | admin | write | read | read | read |
| system:settings | admin | admin | — | — | — |
| audit:log | admin | read | — | — | — |
```

---

## 4. Secret Management {#secrets}

```bash
# NEVER in code:
DATABASE_URL="postgresql://user:pass@host/db"  # BANNED

# NEVER in .env files committed to git

# CORRECT — Kubernetes Sealed Secrets
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: db-credentials
spec:
  encryptedData:
    DATABASE_URL: AgBy3i...  # encrypted with cluster public key

# CORRECT — HashiCorp Vault
vault kv put secret/prod/database url="postgresql://..."
# Access via Vault Agent sidecar or Vault Secrets Operator
```

```typescript
// Secret validation at startup — fail fast if missing
const REQUIRED_SECRETS = [
  'DATABASE_URL',
  'JWT_SECRET',
  'RESEND_API_KEY',
  'SUPABASE_SERVICE_ROLE_KEY',
];

for (const secret of REQUIRED_SECRETS) {
  if (!process.env[secret]) {
    throw new Error(`FATAL: Missing required secret: ${secret}. Check Vault/Sealed Secrets.`);
  }
}
```

---

## 5. JWT — Secure Patterns {#jwt}

```typescript
// Secure JWT configuration
const JWT_CONFIG = {
  algorithm: 'RS256',        // Asymmetric — NEVER HS256 in production
  expiresIn: '15m',          // Access token: short-lived
  issuer: 'https://auth.yourdomain.com',
  audience: 'https://api.yourdomain.com',
};

const REFRESH_TOKEN_CONFIG = {
  expiresIn: '7d',
  httpOnly: true,            // Never accessible to JS
  secure: true,              // HTTPS only
  sameSite: 'strict' as const,
  path: '/auth/refresh',     // Scoped path, not '/'
};

// Verify — always validate all claims
async function verifyToken(token: string): Promise<JWTPayload> {
  const payload = jwt.verify(token, PUBLIC_KEY, {
    algorithms: ['RS256'],
    issuer: JWT_CONFIG.issuer,
    audience: JWT_CONFIG.audience,
  }) as JWTPayload;

  // Additional checks
  if (!payload.sub) throw new UnauthorizedException('Missing subject');
  if (!payload.scope) throw new UnauthorizedException('Missing scope');

  return payload;
}
```

---

## 6. OWASP Top 10 — Defenses {#owasp}

```typescript
// A03 — Injection: ALWAYS parameterized queries
// BANNED:
const q = `SELECT * FROM users WHERE email = '${email}'`;

// CORRECT (Drizzle ORM):
const user = await db.select().from(users).where(eq(users.email, email));

// CORRECT (raw SQL):
await db.execute(sql`SELECT * FROM users WHERE email = ${email}`);

// A03 — XSS: sanitize any HTML
import DOMPurify from 'isomorphic-dompurify';
const safe = DOMPurify.sanitize(userInput, { ALLOWED_TAGS: [] }); // strip all

// A10 — SSRF: validate outbound URLs
const BLOCKED = ['127.0.0.1', '::1', '169.254.169.254', '10.', '192.168.', '172.16.'];
function validateOutboundUrl(url: string): void {
  const parsed = new URL(url);
  if (BLOCKED.some(b => parsed.hostname.startsWith(b))) {
    throw new ForbiddenException('SSRF: private address access denied');
  }
}

// A07 — Session: invalidate on logout
async function logout(sessionId: string): Promise<void> {
  await redis.del(`session:${sessionId}`);      // invalidate server-side
  // + clear httpOnly cookie on response
}
```

### OWASP Checklist (mandatory before every release)

```
□ A01 Broken Access Control    — RBAC guard on every protected endpoint
□ A02 Cryptographic Failures   — HTTPS everywhere, Argon2id passwords, AES-256 at rest
□ A03 Injection                — Parameterized queries, DOMPurify, shell escaping
□ A04 Insecure Design          — Threat model reviewed, trust boundaries documented
□ A05 Security Misconfiguration— Security headers set, debug off in prod, defaults changed
□ A06 Vulnerable Components    — pnpm audit / npm audit run, 0 critical issues
□ A07 Auth/Session Failures    — Short-lived JWTs, secure cookies, session invalidation
□ A08 Software Integrity       — CI/CD pipeline signed, dependency lockfiles committed
□ A09 Logging Failures         — All auth events logged, no PII in logs, audit trail intact
□ A10 SSRF                     — Outbound URL validation, allowlist for external calls
+ CSRF token on state-mutating forms
+ Rate limiting: 100 req/min per IP on auth endpoints, 1000 req/min elsewhere
+ Brute force: lockout after 5 failed logins, exponential backoff
```

---

## 7. Automated Pentesting Checklist {#pentesting}

```bash
# SAST — run in CI
npx biome check --unsafe .
npx eslint . --ext .ts,.tsx --rule 'security/*:error'

# Dependency audit — fail pipeline on critical
pnpm audit --audit-level=critical

# Dynamic scan (OWASP ZAP)
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://staging.yourdomain.com \
  -r zap-report.html

# Secrets scan — prevent commits
npx secretlint "**/*"
git config core.hooksPath .githooks
# .githooks/pre-commit runs secretlint

# Privilege escalation test
# Attempt each RBAC boundary manually:
# - viewer accessing admin endpoint → expect 403
# - user accessing another user's data → expect 403
# - manager accessing super_admin route → expect 403
```

---

## 8. Input Sanitization {#sanitization}

```typescript
// Every external input goes through Zod before touching the DB
import { z } from 'zod';

const CreateUserSchema = z.object({
  email: z.string().email().max(255).toLowerCase().trim(),
  name: z.string().min(1).max(100).trim(),
  role: z.enum(['user', 'viewer']),  // never accept role from client for elevated roles
});

// In controller — validate before anything else
async createUser(@Body() body: unknown) {
  const validated = CreateUserSchema.parse(body);  // throws ZodError if invalid
  return this.usersService.create(validated);
}

// File uploads — validate mime type server-side (never trust Content-Type header)
import fileType from 'file-type';
const detected = await fileType.fromBuffer(buffer);
const ALLOWED = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'];
if (!detected || !ALLOWED.includes(detected.mime)) {
  throw new BadRequestException('Invalid file type');
}
```
