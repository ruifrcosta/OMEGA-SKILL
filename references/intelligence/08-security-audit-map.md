# OMEGA Security Audit Map
## Threat Modeling, Zero Trust Networks, CORS/CSP Configurations, & Penetration Testing Rules

This document establishes the security policies, access controls, network boundaries, and vulnerability testing rules enforced across all OMEGA components.

---

## 1. Zero Trust Cross-Service Architecture

To eliminate trust assumptions inside our network, OMEGA enforces the **Zero Trust architecture**. Services must explicitly authenticate and authorize every interaction.

```
                    ┌──────────────────────────────┐
                    │       External Traffic       │
                    └──────────────┬───────────────┘
                                   │ (HTTPS + TLS 1.3)
                                   ▼
                    ┌──────────────────────────────┐
                    │    Cloudflare / NGINX        │
                    │       Reverse Proxy          │
                    └──────────────┬───────────────┘
                                   │ (mTLS, JWT Verification)
                                   ▼
                    ┌──────────────────────────────┐
                    │     NestJS API Gateway       │
                    └──────────────┬───────────────┘
                                   │ (Internal mTLS, Spiffe/Spire)
                                   ▼
                    ┌──────────────────────────────┐
                    │  Internal Microservices      │
                    │  (Catalog / Payments / ML)   │
                    └──────────────────────────────┘
```

- **mTLS (mutual TLS)**: Required for all inter-service network packets.
- **Micro-segmentation**: Services are containerized and isolated. A breach in `catalog-service` cannot access database endpoints of `payment-service`.

---

## 2. Hardened CORS & CSP (Content Security Policy)

OMEGA prohibits permissive configuration wildcards (`*`) inside headers.

### 2.1. NGINX CORS Whitelist Configuration
```nginx
# Secure CORS Configuration
map $http_origin $cors_origin {
    default "";
    "~^https://(web|mobile|docs)\.omega\.dev$" "$http_origin";
}

server {
    listen 443 ssl http2;
    server_name api.omega.dev;

    add_header 'Access-Control-Allow-Origin' $cors_origin always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
    add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;

    if ($request_method = 'OPTIONS') {
        add_header 'Access-Control-Max-Age' 1728000;
        add_header 'Content-Type' 'text/plain; charset=utf-8';
        add_header 'Content-Length' 0;
        return 204;
    }
}
```

### 2.2. Hardened CSP Header
```http
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-r4nd0m' https://apis.google.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data: https://images.unsplash.com; connect-src 'self' https://api.omega.dev wss://api.omega.dev; frame-ancestors 'none'; form-action 'self'; base-uri 'self';
```

---

## 3. RBAC (Role-Based Access Control) Model

We map authorization using strict role segregation, checking permissions at the API Gateway level.

```
                    ┌──────────────┐
                    │  User Token  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ API Gateway  │ ──► Parse User Role: 'ADMIN', 'DEV', 'USER'
                    └──────┬───────┘
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
           [Admin Path]        [Client Path]
           (Requires:          (Requires:
            write:system)       read:profile)
```

---

## 4. Penetration Testing Rules & SAST Scanner Gates

To prevent code injection and vulnerability shipping:

1. **Static Analysis (SAST)**: Pre-commit git hooks trigger dependency security checking. High-severity alerts abort the release pipeline.
2. **Secrets Detection**: Trufflehog/GitLeaks scans code to prevent accidental commit of API tokens and database keys.
3. **Automated DAST**: Weekly OWASP ZAP scans executed in sandbox/staging, verifying endpoints against SQL injection, XSS, and broken authentication.
