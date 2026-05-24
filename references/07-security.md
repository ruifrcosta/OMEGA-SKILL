# Cybersecurity & Hardening Reference

## Table of Contents
1. [Zero Trust Architecture](#zero-trust)
2. [CORS Hardening & CSP Policies](#cors-csp)
3. [Role-Based Access Control (RBAC) Engine](#rbac)
4. [OWASP Top 10 Defenses](#owasp)
5. [Automated Pentesting Checklists](#pentesting)

---

## 1. Zero Trust Architecture {#zero-trust}

OMEGA TITAN assumes a default-compromised posture. No client, network boundary, or internal microservice is trusted implicitly.

*   **Service-to-Service Encryption**: All network traffic between VPC subnets or cluster namespaces must utilize **mTLS** (governed via Istio or linkerd).
*   **Token Isolation**: Authenticate microservices using short-lived cryptographically signed JWTs containing explicit `scopes` and `audiences`.
*   **Least Privilege Access**: Direct access to production database systems, cloud clusters, or configuration environments requires ephemeral, audited multi-party authorizations (JIT).

---

## 2. CORS Hardening & CSP Policies {#cors-csp}

Never use wildcard origin headers (`*`) in production. Configure secure, explicit CORS boundaries and restrict script load spaces.

### hardened NGINX Gateway CORS Rules
```nginx
# Secure headers configuration
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'nonce-$random_csp_nonce'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://api.omega-titan.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self';" always;
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
```

---

## 3. Role-Based Access Control (RBAC) Engine {#rbac}

Implement strict validation of user identities, hierarchies, and resource ownership at both gate (middleware) and service layer.

### NestJS RBAC / ABAC Guard
```typescript
// guards/permissions.guard.ts
import { Injectable, CanActivate, ExecutionContext } from '@nestjs/common';
import { Reflector } from '@nestjs/core';

@Injectable()
export class PermissionsGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredPermissions = this.reflector.get<string[]>('permissions', context.getHandler());
    if (!requiredPermissions) return true;

    const request = context.switchToHttp().getRequest();
    const user = request.user; // Appended by AuthMiddleware after decoding JWT

    if (!user || !user.permissions) return false;

    // Check if user has all required scopes
    return requiredPermissions.every((perm) => user.permissions.includes(perm));
  }
}
```

---

## 4. OWASP Top 10 Defenses {#owasp}

Implement explicit security guards to prevent SQL injections, CSRF, and broken access controls.

```typescript
// Defensive coding rules
// 1. Preventing SQL Injections: Always parameterize queries. Never concatenate SQL strings.
const query = 'SELECT * FROM accounts WHERE id = $1'; // Correct

// 2. Preventing XSS Injections: Sanitize user input using standard, secure libraries.
import DOMPurify from 'isomorphic-dompurify';
const cleanHtml = DOMPurify.sanitize(userInput);

// 3. Preventing SSRF (Server-Side Request Forgery): Restrict target URLs on outbound fetch calls
const RESTRICTED_IPS = ['127.0.0.1', '169.254.169.254'];
if (RESTRICTED_IPS.includes(parsedUrl.hostname)) {
  throw new UnauthorizedException('Access to private metadata is strictly prohibited');
}
```

---

## 5. Automated Pentesting Checklists {#pentesting}

Ecosystem builds must execute security validation audits as gating stages of delivery pipelines:

*   **SAST Analysis**: Run Biome, ESLint, or SonarQube rules to scan source directories for unsafe logic.
*   **Dependency Scanning**: Run `npm audit` or `cargo audit` to identify vulnerabilities. Fail pipelines on any critical severity alert.
*   **Outbound Scans**: Periodically execute OWASP ZAP or shannon scripts against test endpoints to verify boundary resilience.
