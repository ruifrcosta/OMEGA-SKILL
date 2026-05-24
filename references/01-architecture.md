# Architecture Reference

## Table of Contents
1. [Architecture Decision Records (ADRs)](#adrs)
2. [Domain-Driven Design (DDD)](#ddd)
3. [CQRS + Event Sourcing](#cqrs)
4. [Clean & Hexagonal Architecture](#clean)
5. [Distributed Systems Patterns](#distributed)
6. [Monorepo Structure](#monorepo-structure)
7. [Architecture Review Checklist](#checklist)

---

## 1. Architecture Decision Records (ADRs) {#adrs}

Every non-trivial technical decision requires an ADR **before implementation begins**.

**ADR Template** — save to `obsidian-vault/14-ADRs/ADR-NNNN-short-title.md`:

```markdown
---
id: ADR-0001
title: Use NestJS over Express for API Layer
status: accepted  # proposed | accepted | deprecated | superseded
date: YYYY-MM-DD
deciders: [CTO, Backend Lead]
supersedes: []
---

## Context
What problem are we solving? What constraints exist? What options were considered?

## Decision
What did we decide to do, and why?

## Consequences
**Positive**: ...
**Negative**: ...
**Risks**: ...

## Alternatives Considered
| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| Express | Minimal overhead | No DI, manual structure | Scales poorly without discipline |
| Fastify | Very fast | Less ecosystem | Team unfamiliar |

## Implementation Notes
Key patterns, library versions, or gotchas to be aware of.
```

Reject any implementation that cannot reference a valid ADR. If an ADR doesn't exist yet, create it first.

---

## 2. Domain-Driven Design (DDD) {#ddd}

### Bounded Context Map

Before writing any service, define bounded contexts. Each context owns its data and communicates via contracts.

```
┌─────────────────────┐     ┌─────────────────────┐
│    Identity Context │     │   Billing Context    │
│  - User             │────▶│  - Subscription      │
│  - Auth             │     │  - Invoice           │
│  - Session          │     │  - Payment           │
└─────────────────────┘     └─────────────────────┘
         │                           │
         ▼                           ▼
┌─────────────────────┐     ┌─────────────────────┐
│   Product Context   │     │  Analytics Context   │
│  - Feature          │     │  - Event             │
│  - Workspace        │     │  - Metric            │
│  - Permission       │     │  - Report            │
└─────────────────────┘     └─────────────────────┘
```

### Aggregate Design Rules

An aggregate is a cluster of domain objects treated as a unit for data changes:

```typescript
// Good: Aggregate enforces invariants
class Order {
  private items: OrderItem[] = [];
  private status: OrderStatus = OrderStatus.PENDING;

  addItem(product: Product, quantity: number): void {
    if (this.status !== OrderStatus.PENDING) {
      throw new DomainError('Cannot add items to a confirmed order');
    }
    this.items.push(new OrderItem(product, quantity));
    this.raise(new ItemAddedToOrderEvent(this.id, product.id, quantity));
  }
  
  // Aggregates raise domain events — never mutate directly from outside
  private raise(event: DomainEvent): void {
    this.domainEvents.push(event);
  }
}
```

### Ubiquitous Language

Build a shared glossary for each bounded context. Never mix language between contexts — an "Account" in identity context is not the same as "Account" in billing context.

Store at: `obsidian-vault/01-Architecture/ubiquitous-language-[context].md`

---

## 3. CQRS + Event Sourcing {#cqrs}

### When to Use CQRS

Use CQRS when:
- Read and write loads have different scaling needs
- Complex domain logic makes a single model hard to maintain
- Audit trail / event history is a business requirement
- You need projections optimized for specific read patterns

**Don't use CQRS** for simple CRUD services — the overhead isn't justified.

### CQRS Implementation Pattern

```typescript
// Command side — focused on intent and validation
class CreateWorkspaceCommand {
  constructor(
    public readonly ownerId: string,
    public readonly name: string,
    public readonly plan: PlanType,
  ) {}
}

class CreateWorkspaceHandler {
  async execute(cmd: CreateWorkspaceCommand): Promise<WorkspaceId> {
    const workspace = Workspace.create(cmd.ownerId, cmd.name, cmd.plan);
    await this.workspaceRepo.save(workspace);
    await this.eventBus.publish(workspace.pullDomainEvents());
    return workspace.id;
  }
}

// Query side — optimized read model (can use different DB, denormalized)
class GetWorkspaceDashboardQuery {
  constructor(public readonly workspaceId: string) {}
}

// Query handler reads from read model (PostgreSQL view, Redis, ElasticSearch)
// No business logic — pure projection
```

### Event Sourcing Pattern

```typescript
// Events are the source of truth — never mutate state directly
type WorkspaceEvent =
  | { type: 'WorkspaceCreated'; ownerId: string; name: string; plan: string }
  | { type: 'MemberInvited'; email: string; role: RoleType }
  | { type: 'WorkspaceUpgraded'; newPlan: string; timestamp: string };

// Reconstruct state by replaying events
function reconstitute(events: WorkspaceEvent[]): WorkspaceState {
  return events.reduce(applyEvent, initialState);
}
```

---

## 4. Clean & Hexagonal Architecture {#clean}

### Clean Architecture Layer Rules

```
┌─────────────────────────────────────────────┐
│              Frameworks & Drivers            │  ← HTTP, DB, UI, CLI
│  ┌───────────────────────────────────────┐  │
│  │         Interface Adapters            │  │  ← Controllers, Repos, Presenters
│  │  ┌─────────────────────────────────┐  │  │
│  │  │       Application Layer         │  │  │  ← Use Cases, Commands, Queries
│  │  │  ┌───────────────────────────┐  │  │  │
│  │  │  │      Domain Layer         │  │  │  │  ← Entities, Value Objects, Events
│  │  │  └───────────────────────────┘  │  │  │
│  │  └─────────────────────────────────┘  │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
Dependency rule: arrows point INWARD only
```

**The Golden Rule**: Domain layer has zero imports from outer layers. Infrastructure depends on domain, never the reverse. Enforce this with ESLint boundaries or Nx project constraints.

```typescript
// Domain: pure TypeScript, zero framework imports
export class Email {
  private constructor(private readonly value: string) {}

  static create(raw: string): Result<Email, 'invalid-email'> {
    if (!EMAIL_REGEX.test(raw)) return Err('invalid-email');
    return Ok(new Email(raw));
  }

  toString(): string { return this.value; }
}

// Infrastructure: implements domain port (dependency inversion)
export class PostgresUserRepository implements UserRepository {
  async findByEmail(email: Email): Promise<User | null> {
    const row = await this.db.query(
      'SELECT * FROM users WHERE email = $1',
      [email.toString()]
    );
    return row ? UserMapper.toDomain(row) : null;
  }
}
```

---

## 5. Distributed Systems Patterns {#distributed}

### Service Communication Decision Tree

```
Need to communicate between services?
├── Is immediate response required?
│   ├── Yes → REST or gRPC (synchronous)
│   │   ├── Simple CRUD → REST (JSON + OpenAPI)
│   │   └── High-performance, typed → gRPC (Protobuf)
│   └── No → Event/message-based (asynchronous)
│       ├── Ordered, partitioned, high-throughput → Kafka
│       └── Simple task queue, retry, scheduling → RabbitMQ / BullMQ
└── Need eventual consistency across services?
    └── Saga pattern (orchestration or choreography)
```

### Saga Pattern — Distributed Transactions

```
Order Saga (Orchestration):
  1. OrderService: create order (status: PENDING)
  2. → PaymentService: reserve payment
     ├─ Success → 3. InventoryService: reserve stock
     │              ├─ Success → 4. OrderService: confirm order
     │              └─ Failure → compensate: PaymentService.release()
     └─ Failure → compensate: OrderService.cancel()
```

### Circuit Breaker Pattern

```typescript
// Prevent cascade failures — open circuit when error rate exceeds threshold
const client = new CircuitBreaker(externalServiceCall, {
  timeout: 3000,          // call timeout
  errorThresholdPercentage: 50,  // open circuit at 50% error rate
  resetTimeout: 30000,    // try half-open after 30s
});

client.on('open', () => metrics.increment('circuit_breaker.open', { service: 'payment' }));
client.on('halfOpen', () => logger.warn('Circuit half-open, probing...'));
```

---

## 6. Monorepo Structure Reference {#monorepo-structure}

Full monorepo layout — adapt to project scope:

```
repo-root/
├── apps/
│   ├── web/              # Next.js web application
│   ├── api/              # NestJS API
│   ├── mobile/           # Expo React Native
│   ├── admin/            # Internal admin portal
│   └── docs/             # Documentation site
├── packages/
│   ├── ui/               # Shared component library (design system)
│   ├── config/           # Shared ESLint, TypeScript, Tailwind configs
│   ├── auth/             # Shared auth utilities
│   ├── contracts/        # Shared types, DTOs, Zod schemas
│   └── utils/            # Pure utility functions
├── services/
│   ├── notifications/    # Resend + push notification service
│   ├── analytics/        # Event tracking + aggregation
│   └── workers/          # Background job processors
├── infra/
│   ├── terraform/        # IaC — all cloud resources
│   ├── kubernetes/       # K8s manifests or Helm charts
│   └── docker/           # Dockerfiles + compose files
├── platform/
│   ├── ci/               # GitHub Actions workflows
│   ├── scripts/          # Dev tooling, migration scripts
│   └── monitoring/       # Grafana dashboards, alert rules
├── design-system/        # Tokens, Figma exports, HTML primitives
├── obsidian-vault/       # All project documentation (see 11-obsidian.md)
└── turbo.json            # Turborepo pipeline configuration
```

For detailed Turborepo and pnpm workspace configuration, see `16-monorepo.md`.

---

## 7. Architecture Review Checklist {#checklist}

Run before any architecture is finalized:

```
Scalability
□ Can each component scale independently?
□ Is shared mutable state minimized?
□ Are database queries bounded (pagination, indexes)?
□ Is there a plan for 10x and 100x growth?

Resilience
□ Are all external calls wrapped in circuit breakers?
□ Is there retry with exponential backoff + jitter?
□ Are cascading failures isolated via bulkheads?
□ Is there a tested rollback procedure?

Observability
□ Are structured logs emitted with correlation IDs?
□ Are distributed traces instrumented (OpenTelemetry)?
□ Are SLOs defined for each critical user journey?
□ Are alerting rules set with appropriate thresholds?

Security
□ Is each service's attack surface minimized?
□ Are service-to-service calls authenticated (mTLS or JWT)?
□ Are secrets in a vault (never in code or env files)?
□ Is network segmentation enforced?

Maintainability
□ Are boundaries explicit and enforced by tooling?
□ Is there a clear owner for each bounded context?
□ Are contracts versioned and backward-compatible?
□ Is complexity justified by actual requirements?
```
