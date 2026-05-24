# Monorepo & Componentization Reference

## Table of Contents
1. [pnpm Workspaces Setup](#pnpm-workspaces)
2. [Turborepo Pipeline Configuration](#turborepo)
3. [Component Isolation & Package Boundaries](#package-boundaries)
4. [Centralizing Design Tokens](#tokens-integration)

---

## 1. pnpm Workspaces Setup {#pnpm-workspaces}

OMEGA TITAN structures its monorepo workspaces using **pnpm** for rapid installation speeds, shared lockfile integrity, and robust node_modules optimization.

### Workspaces Configuration (`pnpm-workspace.yaml`)
```yaml
packages:
  # Applications
  - 'apps/*'
  # Shared services
  - 'services/*'
  # Shared utility packages
  - 'packages/*'
```

---

## 2. Turborepo Pipeline Configuration {#turborepo}

We utilize **Turborepo** to orchestrate build, lint, and test pipelines. Turborepo caches output artifacts locally and remotely to prevent repeated computation.

### Pipeline Layout (`turbo.json`)
```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": [".env.production", "tsconfig.json"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "dist/**", "build/**"],
      "inputs": ["src/**", "app/**", "tsconfig.json"]
    },
    "lint": {
      "outputs": []
    },
    "test": {
      "dependsOn": ["^build"],
      "outputs": [],
      "inputs": ["src/**/*.ts", "app/**/*.tsx", "test/**/*.spec.ts"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

---

## 3. Component Isolation & Package Boundaries {#package-boundaries}

To maintain architectural boundaries, packages must define clear boundaries using ESLint rules or Nx boundary tags:

*   **Dependency Arrows**: A shared package (e.g. `packages/ui` or `packages/utils`) must never depend on consumer applications (e.g. `apps/web` or `apps/api`).
*   **Encapsulation Rules**: Keep internal service details hidden inside private modules. Expose only typed contracts and explicit interfaces via the `index.ts` entrypoints.

### UI Package Exports Layout (`packages/ui/index.ts`)
```typescript
// Exposing explicitly validated primitives only
export { Button } from './src/button';
export { Input } from './src/input';
export { Modal } from './src/modal';

// Do not expose internal component sub-logic or utility libraries
```

---

## 4. Centralizing Design Tokens {#tokens-integration}

Design tokens defined in `02-design-system.md` are central to the monorepo. They must be packaged as a shared npm package and integrated across all apps:

```
packages/design-tokens/
├── package.json
├── index.js                  # Exports variables (HSL scales)
└── tailwind-preset.js        # Exports shared presets for tailwind configs
```

### presetted Presets Integration (`apps/web/tailwind.config.js`)
```javascript
module.exports = {
  // Pull shared preset config from workspace package
  presets: [require('@omega/design-tokens/tailwind-preset')],
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
}
```
