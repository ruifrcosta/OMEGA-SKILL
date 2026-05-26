# QA & Test Engineering Reference

## Table of Contents
1. [Playwright E2E & Accessibility Tests](#playwright)
2. [Vitest Unit & Integration Tests](#vitest)
3. [k6 Load & Stress Testing Scripts](#k6)
4. [Ecosystem Test Strategy Checks](#test-strategy)

---

## 1. Playwright E2E & Accessibility Tests {#playwright}

We utilize Playwright for E2E tests and to audit accessibility boundaries (`axe-core`) during build stages.

### Workspace Creation & Accessibility E2E Test
```typescript
// tests/workspace.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Workspace Orchestration', () => {
  test('should create a workspace and pass accessibility audits', async ({ page }) => {
    // 1. Authenticate & Navigate
    await page.goto('/login');
    await page.fill('input[type="email"]', 'engineer@omega-titan.com');
    await page.fill('input[type="password"]', 'SuperSecurePassword123!');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/workspace');

    // 2. Accessibility Scan
    const accessibilityResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityResults.violations).toEqual([]);

    // 3. Perform Mutation
    await page.click('[aria-label="Create Workspace"]');
    await page.fill('[placeholder="Workspace name"]', 'Titan Labs');
    await page.click('button:has-text("Confirm")');

    // 4. Validate State
    await expect(page.locator('h1')).toContainText('Titan Labs');
  });
});
```

---

## 2. Vitest Unit & Integration Tests {#vitest}

Unit and integration tests run inside **Vitest** for extreme speed and mock reliability.

### Business Domain Aggregate Unit Test
```typescript
// domain/order.spec.ts
import { describe, it, expect } from 'vitest';
import { Order } from './order';
import { OrderStatus } from './types';

describe('Order Aggregate', () => {
  it('should enforce status invariance when adding items', () => {
    const order = Order.create('user_abc123');
    expect(order.getStatus()).toBe(OrderStatus.PENDING);

    order.addItem({ productId: 'prod_999', price: 49.99 }, 2);
    expect(order.getItemsCount()).toBe(1);

    // Confirm state transition
    order.confirm();
    expect(order.getStatus()).toBe(OrderStatus.CONFIRMED);

    // Attempting modification on confirmed order must throw DomainError
    expect(() => {
      order.addItem({ productId: 'prod_888', price: 9.99 }, 1);
    }).toThrow('Cannot add items to a confirmed order');
  });
});
```

---

## 3. k6 Load & Stress Testing Scripts {#k6}

Production services must withstand expected peak loads. Load scripts are structured using **k6** to validate scaling rules.

### Performance Load Script (`tests/load/api-stress.js`)
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 50 },  // Ramp-up to 50 active clients
    { duration: '3m', target: 50 },  // Maintain peak stress load
    { duration: '1m', target: 0 },   // Ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<250'], // 95% of queries must resolve within 250ms
    http_req_failed: ['rate<0.01'],    // Failure rate must remain below 1%
  },
};

export default function () {
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer test-jwt-token-here',
    },
  };

  const response = http.get('https://api.omega-titan.com/v1/workspace', params);
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'body is valid': (r) => r.json().hasOwnProperty('workspaces'),
  });

  sleep(1);
}
```

---

## 4. Ecosystem Test Strategy Checks {#test-strategy}

Our code pipelines require target boundaries before shipping code blocks to environment deployments:

*   **Coverage Target**: Minimum **85%** statement and branch coverage on critical business contexts.
*   **Regression Audits**: Any resolved bug requires a matching regression test reproducing the error condition before release approval.
*   **Boundary Contracts**: Always mock external network boundaries (payment gateways, notification endpoints) during Unit tests to guarantee hermetic run isolation.

---

## 5. Contract Testing {#contract-testing}

```typescript
// Pact — consumer-driven contract tests
// Consumer defines what it expects from the provider
// Provider verifies it can satisfy all consumers

// Consumer test (frontend expecting this API shape)
import { PactV3 } from '@pact-foundation/pact';

const provider = new PactV3({
  consumer: 'web-frontend',
  provider: 'orders-api',
});

describe('Orders API contract', () => {
  it('returns order list in expected shape', async () => {
    await provider
      .given('user has orders')
      .uponReceiving('GET /v1/orders')
      .withRequest({ method: 'GET', path: '/v1/orders' })
      .willRespondWith({
        status: 200,
        body: {
          orders: eachLike({
            id: string('ord_123'),
            status: string('pending'),
            total_cents: integer(4999),
          }),
        },
      })
      .executeTest(async (mockServer) => {
        const res = await fetch(`${mockServer.url}/v1/orders`);
        expect(res.status).toBe(200);
      });
  });
});
```

## 6. CI/CD Quality Gates {#ci-gates}

```yaml
# .github/workflows/quality.yml
name: Quality Gates
on: [push, pull_request]

jobs:
  gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Type check
        run: rtk pnpm tsc --noEmit
        # GATE: zero TypeScript errors

      - name: Lint
        run: rtk pnpm biome check .
        # GATE: zero lint errors

      - name: Unit tests + coverage
        run: rtk pnpm vitest run --coverage
        # GATE: coverage >= 80%

      - name: Coverage threshold check
        run: |
          COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.statements.pct')
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "Coverage ${COVERAGE}% below 80% threshold"
            exit 1
          fi

      - name: E2E tests
        run: rtk pnpm playwright test
        # GATE: all critical journeys pass

      - name: Security audit
        run: pnpm audit --audit-level=critical
        # GATE: zero critical vulnerabilities

      - name: Build
        run: rtk pnpm build
        # GATE: production build succeeds
        # GATE: bundle size < 150kb initial

  load-test:
    needs: gates
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Load test staging
        run: rtk k6 run --out json=results.json tests/load/api-stress.js
        env:
          BASE_URL: https://staging.yourdomain.com
        # GATE: p95 < 200ms, error rate < 1%
```

## 7. Snapshot & Visual Regression {#snapshots}

```typescript
// Vitest snapshots for API responses
it('order response matches snapshot', async () => {
  const response = await request(app).get('/v1/orders/ord_123');
  expect(response.body).toMatchInlineSnapshot(`
    {
      "id": "ord_123",
      "status": "pending",
      "items": [...],
      "total_cents": 4999,
    }
  `);
});

// Playwright visual regression
test('checkout page renders correctly', async ({ page }) => {
  await page.goto('/checkout');
  await expect(page).toHaveScreenshot('checkout-desktop.png', {
    maxDiffPixels: 100,  // allow minor rendering differences
  });
});
```
