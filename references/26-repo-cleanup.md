# Repository Cleanup & Code Health Reference

Read before any task involving: cleaning an AI-generated codebase, removing dead code,
reorganising files, fixing import chains, or preparing a repository for scale.

## Critical Rule

**OMEGA never deletes or moves a file without first mapping every import of that file.**
Every cleanup action follows: Audit → Map → Verify Safe → Act → Test → Document.
Zero broken imports. Zero silent regressions.

---

## Table of Contents
1. [Cleanup Philosophy — Safe Before Clean](#philosophy)
2. [Import Map — Full Dependency Graph](#import-map)
3. [Dead Code Detection](#dead-code)
4. [AI-Generated File Patterns to Eliminate](#ai-patterns)
5. [Canonical Clean Repository Structure](#structure)
6. [File Migration Protocol](#migration)
7. [Automated Cleanup Pipeline](#automation)
8. [Clean Code Quality Gates](#gates)
9. [Scalability Checklist](#scalability)

---

## 1. Cleanup Philosophy {#philosophy}

Three laws that override every other consideration:

**Law 1 — Map before move.**
No file is touched until its full import chain is known. One missed import crashes a production route.

**Law 2 — Incremental, never big bang.**
Large cleanups in one PR are unreviable. Maximum 20 files per cleanup PR.
Each PR must pass all tests before the next begins.

**Law 3 — Context preserved, not discarded.**
Every moved file carries its history. Every deleted abstraction has its logic
absorbed elsewhere — never silently dropped.

---

## 2. Import Map — Full Dependency Graph {#import-map}

Before touching any file, run a complete import analysis.

### Find every import of a file

```bash
# Find every file that imports target.ts
TARGET="src/lib/utils/date.ts"
rg --type ts "from ['\"].*${TARGET%.*}['\"]" --include="*.ts" --include="*.tsx" -l

# Find barrel exports that re-export target
rg --type ts "export.*from ['\"].*${TARGET%.*}" -l

# Find dynamic imports
rg --type ts "import\(['\"].*${TARGET%.*}" -l

# Find require() (legacy JS)
rg --type js "require\(['\"].*${TARGET%.*}" -l
```

### Generate full dependency graph (madge)

```bash
# Install once
pnpm add -D madge

# Full graph — shows every file → imports
npx madge src/ --ts-config tsconfig.json --extensions ts,tsx

# Find circular dependencies (crash risk)
npx madge --circular --extensions ts,tsx src/
# Output: Circular dependencies: 3
# src/components/auth/LoginForm.tsx -> src/lib/auth.ts -> src/components/auth/LoginForm.tsx

# Orphaned files (no imports, no entry point)
npx madge --orphans --extensions ts,tsx src/

# Export as JSON for scripting
npx madge src/ --json > /tmp/dep-graph.json

# Visual graph (open in browser)
npx madge src/ --image /tmp/dep-graph.svg
```

### Map a full module before deleting/moving

```typescript
// scripts/map-imports.ts — run before any refactor
import { execSync } from 'child_process';
import * as fs from 'fs';

function mapImports(targetFile: string): {
  directImporters: string[];
  barrelReexports: string[];
  dynamicImports: string[];
  totalUsages: number;
} {
  const stem = targetFile.replace(/\.(ts|tsx|js|jsx)$/, '');
  const escapedStem = stem.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

  const search = (pattern: string) =>
    execSync(`rg "${pattern}" --type ts --type tsx -l src/ 2>/dev/null || true`)
      .toString().trim().split('\n').filter(Boolean);

  const directImporters = search(`from ['"].*${escapedStem}['"]`);
  const barrelReexports = search(`export.*from ['"].*${escapedStem}['"]`);
  const dynamicImports  = search(`import\\(['"].*${escapedStem}['"]\\)`);

  return {
    directImporters,
    barrelReexports,
    dynamicImports,
    totalUsages: directImporters.length + barrelReexports.length + dynamicImports.length,
  };
}

// Usage
const map = mapImports('src/lib/old-utils.ts');
if (map.totalUsages > 0) {
  console.error(`Cannot delete: ${map.totalUsages} imports found`);
  console.log(JSON.stringify(map, null, 2));
  process.exit(1);
}
```

---

## 3. Dead Code Detection {#dead-code}

### TypeScript — unused exports

```bash
# ts-prune: finds exported symbols with zero imports
pnpm add -D ts-prune
npx ts-prune | grep -v "used in module"

# Output example:
# src/lib/old-helper.ts:12 - formatDate (not used)
# src/components/LegacyModal.tsx:1 - default (not used)
# src/types/deprecated.ts:5 - OldUserType (not used)
```

### Unused dependencies

```bash
# depcheck: finds packages in package.json not actually imported
pnpm add -D depcheck
npx depcheck --ignores="@types/*,typescript,eslint*"

# Output:
# Unused dependencies:
#   * lodash (installed but never imported)
#   * moment (installed but date-fns used instead)
# Missing dependencies:
#   * zod (imported but not in package.json — will crash in CI)
```

### Unused CSS / Tailwind classes

```bash
# PurgeCSS analysis (without removing)
npx purgecss --css dist/**/*.css --content "src/**/*.{ts,tsx,html}" --rejected
```

### Dead route detection (Next.js)

```bash
# Find Next.js pages with zero incoming links
npx next-unused
# Lists pages that are never linked from other pages
# Confirm with analytics before deleting — could be direct URL routes
```

---

## 4. AI-Generated File Patterns to Eliminate {#ai-patterns}

These are the most common pollution patterns left by AI coding sessions.

### Pattern 1 — Scattered test files at wrong locations

```bash
# Find test files outside __tests__/ or .test.ts convention
find src -name "*.test.ts" -o -name "*.spec.ts" | while read f; do
  dir=$(dirname "$f")
  expected="${dir}/__tests__/$(basename $f)"
  if [[ "$f" != *"__tests__"* ]] && [[ "$f" != *".test."* ]]; then
    echo "MISPLACED: $f"
  fi
done

# Correct structure:
# src/lib/auth.ts            ← source
# src/lib/__tests__/auth.test.ts  ← test (co-located)
# OR
# src/__tests__/lib/auth.test.ts  ← test (centralised)
# Pick ONE convention and enforce it with ESLint
```

### Pattern 2 — Duplicate utility files

```bash
# Find files with similar names that might be duplicates
find src -name "*.ts" | xargs basename | sort | uniq -d

# Common duplicates from AI sessions:
# utils.ts, utils2.ts, utilities.ts, helpers.ts, common.ts
# auth.ts, auth-utils.ts, auth-helpers.ts, authUtils.ts
# → Consolidate into ONE canonical module per domain
```

### Pattern 3 — TODO/FIXME debt accumulation

```bash
# Audit all TODOs with context
rg "TODO|FIXME|HACK|XXX|TEMP|@deprecated" --type ts -n | sort

# Convert to tracked issues (not silent comments)
# Before: // TODO: add error handling
# After:  Delete the TODO, create a GitHub issue, add issue number
# Never: leave TODOs for more than one sprint
```

### Pattern 4 — Console.log left from debugging

```bash
# Find all console statements
rg "console\.(log|warn|error|debug|info)" --type ts --type tsx -n

# Legitimate: console.error in catch blocks in scripts
# Must remove: console.log in components, services, API handlers
# Replace with: structured logger (pino, winston)
```

### Pattern 5 — Commented-out code blocks

```bash
# Find large commented blocks (3+ consecutive comment lines)
rg -U "^(\s*//.*\n){3,}" --type ts -l

# Rule: commented code is dead code
# If it might be needed: put it in a branch, not a comment
# If it won't be needed: delete it
```

### Pattern 6 — Type: any escape hatches

```bash
# Find all 'any' usages
rg ": any\b|as any\b|<any>" --type ts -n | grep -v ".test." | grep -v "// eslint-disable"

# Each 'any' is a type-safety hole that could crash at runtime
# Fix:
# : any        → proper type or unknown
# as any       → proper cast or type guard
# Record<string, any> → Record<string, unknown> then narrow
```

### Pattern 7 — Unused imports

```bash
# TypeScript compiler catches these with noUnusedLocals
# In tsconfig.json:
{
  "compilerOptions": {
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}

# ESLint rule for import order and unused imports
# @typescript-eslint/no-unused-vars
# eslint-plugin-unused-imports
```

### Pattern 8 — Magic strings and numbers

```bash
# Find hardcoded strings that should be constants
rg '"[A-Z_]{5,}"' --type ts -n  # likely should be enum/const

# Before (AI generated):
if (user.role === 'SUPER_ADMIN') ...
if (status === 'PROCESSING') ...

# After (clean):
if (user.role === UserRole.SUPER_ADMIN) ...
if (status === OrderStatus.PROCESSING) ...
```

---

## 5. Canonical Clean Repository Structure {#structure}

Every file must have exactly one home. No ambiguity.

```
project-root/
├── apps/
│   ├── web/                   Next.js app
│   │   ├── app/               App Router routes ONLY — no logic
│   │   ├── components/        UI components
│   │   │   ├── ui/            Base: Button, Input, Card (shadcn)
│   │   │   ├── features/      Feature-scoped: AuthForm, OrderList
│   │   │   └── layouts/       Page layouts: DashboardLayout
│   │   ├── lib/               Client-side utilities
│   │   │   ├── actions/       Server Actions (mutations)
│   │   │   ├── hooks/         React hooks
│   │   │   ├── stores/        Zustand stores
│   │   │   └── utils/         Pure functions, no side effects
│   │   └── styles/
│   └── api/                   NestJS app
│       └── src/
│           ├── modules/       Feature modules (auth, orders, users)
│           │   └── [module]/
│           │       ├── dto/           Input validation
│           │       ├── entities/      DB models
│           │       ├── [module].controller.ts
│           │       ├── [module].service.ts
│           │       ├── [module].module.ts
│           │       └── __tests__/
│           ├── common/        Cross-cutting: guards, interceptors, filters
│           ├── config/        Environment config (t3-env)
│           └── main.ts
├── packages/
│   ├── ui/                    Shared React components
│   ├── types/                 Shared TypeScript types (NO code, types only)
│   ├── utils/                 Pure utility functions (no framework deps)
│   └── config/                Shared ESLint, TSConfig, Tailwind config
├── infra/
│   ├── k8s/                   Kubernetes manifests
│   ├── terraform/             IaC modules
│   ├── helm/                  Helm charts
│   └── docker-compose.yml
├── docs/
│   └── vault/                 OMEGA Obsidian vault
├── memory-bank/               OMEGA session memory
├── scripts/                   Build, maintenance, one-off scripts
└── .github/
    ├── workflows/             CI/CD pipelines
    ├── CODEOWNERS
    └── pull_request_template.md
```

### File placement decision tree

```
Is this a React component?
  → apps/web/components/ui/       if base/generic
  → apps/web/components/features/ if feature-specific
  → packages/ui/                  if shared across apps

Is this a TypeScript type or interface?
  → packages/types/               if shared across apps
  → apps/[app]/src/types/         if app-specific

Is this a utility function?
  → packages/utils/               if pure, no framework deps
  → apps/[app]/src/lib/utils/     if framework-specific

Is this a server-side operation (NestJS)?
  → apps/api/src/modules/[domain]/  always — never in web/

Is this a database model?
  → apps/api/src/modules/[domain]/entities/  always
```

---

## 6. File Migration Protocol {#migration}

**Never move a file without following this protocol. One missed step breaks production.**

```
Step 1 — Map all imports of the file
  npx ts-prune | grep filename
  rg "from.*filename" src/ -l
  rg "export.*from.*filename" src/ -l  (barrel re-exports)
  Result: list of ALL files that import the target

Step 2 — Assess breakage risk
  If total imports = 0 → can delete (verify with tests)
  If total imports ≤ 5 → safe to migrate (update all manually)
  If total imports > 5 → use barrel export as bridge (see below)

Step 3 — Create the new file at the target location
  Copy content to new location
  Update relative imports INSIDE the file (../../../ chains)
  Never use absolute paths unless @alias is configured

Step 4 — Bridge old → new (for high-import files)
  At old location, replace content with re-export:
  // DEPRECATED: moved to packages/utils/date.ts
  // Remove this bridge after all imports updated (sprint YYYY-WNN)
  export * from '../../packages/utils/date';

Step 5 — Update all importers
  For each file in Step 1's list: update the import path
  Use sed for mechanical replacements:
  find src -name "*.ts" -exec sed -i
    "s|from '../lib/old-utils'|from '@scope/utils'|g" {} \;

Step 6 — Run full test suite
  pnpm test — must be green before merging
  pnpm build — must succeed (catches import errors)
  pnpm type-check — must be clean

Step 7 — Remove bridge after one sprint
  Delete the re-export bridge file
  Run tests again
  Document in ADR if this was an architectural change
```

---

## 7. Automated Cleanup Pipeline {#automation}

```typescript
// scripts/cleanup-audit.ts
// Run weekly in CI to catch drift

import { execSync } from 'child_process';

interface CleanupReport {
  unusedExports: string[];
  circularDeps: string[];
  anyUsages: number;
  consoleLogs: number;
  todos: number;
  unusedDeps: string[];
  orphanedFiles: string[];
}

async function runCleanupAudit(): Promise<CleanupReport> {
  const run = (cmd: string) =>
    execSync(cmd, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();

  const unusedExports = run('npx ts-prune 2>/dev/null | grep "not used" | head -20')
    .split('\n').filter(Boolean);

  const circularRaw = run('npx madge --circular --extensions ts,tsx src/ 2>/dev/null || echo ""');
  const circularDeps = circularRaw.split('\n').filter(l => l.includes('->'));

  const anyUsages = parseInt(
    run('rg ": any\\b|as any\\b" --type ts src/ --count-matches 2>/dev/null | awk -F: \'{sum+=$2} END{print sum}\'') || '0'
  );

  const consoleLogs = parseInt(
    run('rg "console\\.log" --type ts --type tsx src/ -c 2>/dev/null | wc -l') || '0'
  );

  const todos = parseInt(
    run('rg "TODO|FIXME|HACK" --type ts src/ -c 2>/dev/null | wc -l') || '0'
  );

  return { unusedExports, circularDeps, anyUsages, consoleLogs, todos, unusedDeps: [], orphanedFiles: [] };
}

async function main() {
  const report = await runCleanupAudit();
  const hasIssues = report.circularDeps.length > 0 || report.anyUsages > 10;

  console.log(JSON.stringify(report, null, 2));

  if (hasIssues) {
    console.error('Cleanup audit failed. Fix circular deps and any usages before merging.');
    process.exit(1);
  }
}

main();
```

```yaml
# .github/workflows/cleanup-audit.yml
name: Cleanup Audit

on:
  schedule:
    - cron: '0 9 * * 1'   # Every Monday 9am
  pull_request:
    branches: [main]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - name: Run cleanup audit
        run: npx ts-node scripts/cleanup-audit.ts
      - name: Check circular dependencies
        run: |
          CIRCULAR=$(npx madge --circular --extensions ts,tsx src/ 2>/dev/null | grep "->")
          if [ -n "$CIRCULAR" ]; then
            echo "CIRCULAR DEPENDENCIES FOUND:"
            echo "$CIRCULAR"
            exit 1
          fi
      - name: Type safety audit
        run: |
          ANY_COUNT=$(rg ": any\b|as any\b" --type ts src/ -c | awk -F: '{sum+=$2} END{print sum}')
          echo "Type:any usages: $ANY_COUNT"
          if [ "$ANY_COUNT" -gt "20" ]; then
            echo "Too many 'any' usages. Maximum: 20. Current: $ANY_COUNT"
            exit 1
          fi
```

---

## 8. Clean Code Quality Gates {#gates}

Enforced in CI. PRs blocked if any gate fails.

### ESLint rules (mandatory)

```json
// .eslintrc.json — non-negotiable rules
{
  "rules": {
    "no-console": ["error", { "allow": ["error", "warn"] }],
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unused-vars": "error",
    "no-commented-out-code": "warn",
    "import/no-cycle": "error",
    "import/no-unused-modules": ["warn", { "unusedExports": true }],
    "import/order": ["error", {
      "groups": ["builtin", "external", "internal", "parent", "sibling", "index"],
      "newlines-between": "always",
      "alphabetize": { "order": "asc" }
    }],
    "@typescript-eslint/consistent-type-imports": ["error", { "prefer": "type-imports" }],
    "no-magic-numbers": ["warn", { "ignore": [0, 1, -1], "ignoreArrayIndexes": true }]
  }
}
```

### TypeScript strict mode (mandatory)

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true,
    "noUncheckedIndexedAccess": true
  }
}
```

### File size limits (enforced by ESLint max-lines)

```json
{
  "rules": {
    "max-lines": ["warn", { "max": 300, "skipComments": true, "skipBlankLines": true }],
    "max-lines-per-function": ["warn", { "max": 50, "skipComments": true }],
    "complexity": ["warn", { "max": 10 }],
    "max-depth": ["warn", { "max": 3 }],
    "max-params": ["warn", { "max": 4 }]
  }
}
```

### Pre-commit hooks (Husky + lint-staged)

```json
// package.json
{
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix --max-warnings 0",
      "prettier --write",
      "bash -c 'npx madge --circular --extensions ts,tsx $0 2>/dev/null && exit 0 || exit 1'"
    ],
    "*.{json,md,yml,yaml}": ["prettier --write"]
  }
}
```

```bash
# Install Husky
pnpm add -D husky lint-staged
npx husky init

# .husky/pre-commit
#!/bin/sh
npx lint-staged
npx tsc --noEmit --project tsconfig.json

# .husky/commit-msg
npx commitlint --edit "$1"
```

### Commit message convention (Conventional Commits)

```
feat:     new feature
fix:      bug fix
refactor: code restructuring (no feature change, no bug fix)
chore:    maintenance (deps update, config)
docs:     documentation only
test:     tests only
perf:     performance improvement
ci:       CI/CD changes
cleanup:  dead code removal, file reorganisation (use for cleanup PRs)

Examples:
feat(auth): add biometric login for iOS
fix(orders): prevent double-charge on retry
cleanup(api): remove unused dto files from AI session
refactor(web): consolidate duplicate utility functions
```

---

## 9. Scalability Checklist {#scalability}

Before marking a repository as "production-ready to scale":

```
ARCHITECTURE
□ No circular dependencies (madge --circular = 0)
□ No god objects (no class > 500 lines, no module > 20 exported symbols)
□ Bounded contexts enforced (no cross-module direct imports)
□ All packages have a clear ownership (CODEOWNERS file)
□ Feature flags in place for any rollout risk

TYPE SAFETY
□ strict: true in tsconfig
□ Zero : any usages in production code
□ All API responses typed (Zod for runtime, TypeScript for compile-time)
□ No @ts-ignore without a comment explaining why

DEPENDENCIES
□ Zero circular dependencies
□ Zero unused dependencies (depcheck clean)
□ All deps pinned with exact versions in production
□ Lock file committed (pnpm-lock.yaml / yarn.lock)
□ Dependabot or Renovate configured for automated updates

OBSERVABILITY AT SCALE
□ All requests have trace IDs
□ All errors are caught and logged with context
□ Metrics exposed for all critical business operations
□ Alerts defined for error rate, latency, and queue depth

DATABASE
□ All queries use indexes (EXPLAIN ANALYZE verified)
□ Cursor pagination (no OFFSET on tables > 10k rows)
□ Connection pooling configured (PgBouncer in transaction mode)
□ No N+1 queries (verified with query count logging in tests)

BUILD
□ Build time < 5 minutes (measure and optimise if exceeded)
□ Test suite < 10 minutes (parallelise if exceeded)
□ Docker image < 200MB (multi-stage + distroless)
□ Bundle size analysed and within budget
□ Turborepo cache hitting > 50% in CI
```
