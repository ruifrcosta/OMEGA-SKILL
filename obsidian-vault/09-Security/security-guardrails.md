# OMEGA Application Security Guardrails

This document establishes the mandatory non-negotiable security practices for both web applications and native desktop clients developed under OMEGA.

---

## 1. Web Application Non-Negotiables

Developers and compilers must implement these rules in all backend/frontend web systems:

### A. Input and Command Ingestion (Anti-Injection)
- **Prepared SQL Statements**: Raw SQL concatenation is strictly banned. Parameterized prepared queries (using Prisma or raw database drivers) are mandatory:
  ```typescript
  // ❌ BANNED (SQL Injection vulnerability)
  const query = `SELECT * FROM users WHERE name = '${input}'`;
  
  // ✅ ENFORCED (Prepared statement)
  const users = await prisma.user.findMany({ where: { name: input } });
  ```
- **Shell Spawning**: String-based shell command executions (`exec('command ' + input)`) are banned. Always utilize spawn methods with explicit parameter arrays:
  ```typescript
  // ✅ ENFORCED (Param array prevents shell command injection)
  import { spawn } from 'child_process';
  spawn('git', ['clone', repoUrl]);
  ```

### B. Identity, Auth & Session Protection
- **HttpOnly Auth Cookies**: Authentication or JWT storage cookies must be flagged with `HttpOnly`, `Secure`, and `SameSite=Strict/Lax` headers.
- **Tokens Cryptography**: Do not use `Math.random()` to generate CSRF, reset, or authentication tokens. Use secure cryptographically random token libraries:
  ```typescript
  import crypto from 'crypto';
  const token = crypto.randomBytes(32).toString('hex');
  ```
- **Password Protection**: Storing raw passwords or weak hashes (MD5, SHA1) is banned. Password values must be hashed using high-performance, parameter-tuned `Argon2id` or `bcrypt`.

---

## 2. Desktop Application Hardening (Electron & Tauri)

Client-side native platforms introduce unique local attack vectors that require strict process sandbox controls.

### A. Electron Process Isolations
- **Banned settings**: `nodeIntegration` must strictly be set to `false`, and `contextIsolation` and `webSecurity` must strictly be set to `true`.
- **Minimal Bridge API**: The main process must never expose a raw `ipcRenderer` channel to the renderer view. Instead, expose highly restricted, schema-validated bridge contracts using `contextBridge`:
  ```typescript
  // In preload.ts
  import { contextBridge, ipcRenderer } from 'electron';
  
  contextBridge.exposeInMainWorld('api', {
    saveDocument: (filename: string, content: string) => {
      // Validate schema before passing to ipc
      if (typeof filename !== 'string' || typeof content !== 'string') return;
      ipcRenderer.send('save-doc', { filename, content });
    }
  });
  ```

### B. Tauri Sandboxing Scopes
- Limit local script capability inside `tauri.conf.json`. Restrict `fs` (file system), `http` (network), and `shell` (terminal commands) capabilities to the minimum logical scopes.
- Do not utilize raw, arbitrary event streams for sensitive IPC methods. Always route transactions via Tauri's structured command invocation schema (`invoke()`).

---

## 3. Web Safety Header Governance
The following headers must be enforced on all OMEGA web responses:

| Header | Standard Policy | Purpose |
|--------|-----------------|---------|
| `Content-Security-Policy` | `default-src 'self';` | Blocks remote XSS script injection vectors. |
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` | Enforces SSL encryption layers. |
| `X-Content-Type-Options` | `nosniff` | Blocks dangerous MIME-type sniffing exploits. |
| `X-Frame-Options` | `DENY` or `SAMEORIGIN` | Blocks Clickjacking iframe positioning. |
