# Backend Engineering Reference

## Table of Contents
1. [Polyglot Service Patterns (NestJS, Go, Python)](#polyglot)
2. [API Versioning & Typed Contracts](#api-contracts)
3. [Database Optimization & Postgres Indexing](#db-ops)
4. [Asynchronous Message Queues & Event Processing](#event-queues)
5. [Idempotency & Resilience Patterns](#resilience)

---

## 1. Polyglot Service Patterns (NestJS, Go, Python) {#polyglot}

OMEGA TITAN structures its backend service layers based on business complexity and scalability demands.

*   **NestJS (NodeJS)**: Primary API Gateway and enterprise orchestration layer. Maximizes developer velocity and integrates with high-level design tokens, Supabase, and Resend workflows.
*   **Go (Golang)**: Optimized microservices demanding high concurrency, low latency, and efficient memory usage (e.g. streaming processing, message router).
*   **Python**: Specialized analytic pipelines, AI engine orchestration, vector storage indexing, and machine learning models.

---

## 2. API Versioning & Typed Contracts {#api-contracts}

Production APIs must be strictly versioned using URI path prefixing (e.g. `/v1/`, `/v2/`). All requests and responses must be validated at runtime using schemas.

### NestJS Global Prefix & DTO Validation
```typescript
// main.ts
import { ValidationPipe } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.setGlobalPrefix('v1');
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
    }),
  );
  await app.listen(3000);
}
bootstrap();
```

---

## 3. Database Optimization & Postgres Indexing {#db-ops}

Production PostgreSQL databases must run with structured, deterministic indexes. Ad-hoc unindexed queries are strictly prohibited on tables with more than 10,000 rows.

### Mandated SQL Patterns
*   **Indexes on Foreign Keys**: Every relational foreign key column must maintain a corresponding B-Tree index.
*   **Composite Index Ordering**: Build composite indexes ordered by cardinality (most selective fields first).
*   **Preventing Table Scans**: Verify queries use indexes using Postgres execution plan check scripts.

```sql
-- Creating composite indexes for high-throughput filters
CREATE INDEX CONCURRENTLY idx_users_org_status 
ON users (org_id, status) 
WHERE status = 'ACTIVE';

-- Verify index usage using EXPLAIN ANALYZE
EXPLAIN ANALYZE SELECT * FROM users WHERE org_id = 'org_abc123' AND status = 'ACTIVE';
```

---

## 4. Asynchronous Message Queues & Event Processing {#event-queues}

High-throughput service communication utilizes RabbitMQ or Kafka. Tasks that exceed 100ms processing times must run asynchronously inside background workers.

### BullMQ Worker Pattern (NestJS Task Orchestrator)
```typescript
// processors/image-processor.ts
import { Processor, WorkerHost } from '@nestjs/bullmq';
import { Job } from 'bullmq';
import { Logger } from '@nestjs/common';

@Processor('media')
export class MediaProcessor extends WorkerHost {
  private readonly logger = new Logger(MediaProcessor.name);

  async process(job: Job<any, any, string>): Promise<any> {
    this.logger.log(`Processing media job: ${job.id}`);
    
    switch (job.name) {
      case 'compress':
        await this.handleCompression(job.data);
        break;
      default:
        throw new Error('Unsupported job type');
    }
  }

  private async handleCompression(data: { fileId: string; url: string }) {
    // Media compression logic goes here
    this.logger.log(`Media compressed successfully: ${data.fileId}`);
  }
}
```

---

## 5. Idempotency & Resilience Patterns {#resilience}

All mutating endpoints (POST, PUT, DELETE) must enforce idempotency using an `Idempotency-Key` header. This prevents repeated mutations from double clicks or network retries.

### Go API Gateway Idempotency Middleware
```go
// middleware/idempotency.go
package middleware

import (
	"context"
	"net/http"
	"time"

	"github.com/go-redis/redis/v8"
)

func IdempotencyMiddleware(rdb *redis.Client) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			key := r.Header.Get("Idempotency-Key")
			if key == "" {
				next.ServeHTTP(w, r)
				return
			}

			ctx := context.Background()
			val, err := rdb.Get(ctx, key).Result()
			if err == nil {
				// Key already exists, replay saved response
				w.WriteHeader(http.StatusConflict)
				w.Write([]byte(val))
				return
			}

			// Key doesn't exist, acquire lock for 1 hour
			err = rdb.Set(ctx, key, "IN_PROGRESS", 1*time.Hour).Err()
			if err != nil {
				http.Error(w, "Locking failed", http.StatusInternalServerError)
				return
			}

			next.ServeHTTP(w, r)
		})
	}
}
```
