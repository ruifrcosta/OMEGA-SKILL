# Backend Engineering Reference

## Table of Contents
1. [Service Selection Matrix](#selection)
2. [NestJS — Production Patterns](#nestjs)
3. [Go — High-Concurrency Services](#go)
4. [API Design & Contracts](#api)
5. [Database Patterns & Query Optimization](#db)
6. [Queue & Event Processing](#queues)
7. [Resilience: Idempotency, Retry, Circuit Breaker](#resilience)
8. [Troubleshooting Playbook](#troubleshooting)

---

## 1. Service Selection Matrix {#selection}

| Use Case | Stack | Why |
|----------|-------|-----|
| API gateway, orchestration, admin panel | NestJS | DI, guards, interceptors, ecosystem |
| High-concurrency microservice (>10k rps) | Go | Goroutines, minimal memory, fast cold start |
| Data pipeline, ML, scripting | Python | Ecosystem, libraries, prototyping speed |
| Serverless edge functions | Next.js Server Actions / Hono | Cold start < 50ms, no infra |
| Real-time (websockets, SSE) | NestJS + Socket.io OR Go + gorilla/websocket | Choose based on existing stack |

Never mix Node and Go in the same service. Decide at service boundary level.

---

## 2. NestJS — Production Patterns {#nestjs}

### Bootstrap (never skip these)
```typescript
// main.ts
async function bootstrap() {
  const app = await NestFactory.create(AppModule, {
    bufferLogs: true,
    rawBody: true,  // needed for Stripe webhook verification
  });

  // 1. Versioning
  app.enableVersioning({ type: VersioningType.URI });
  app.setGlobalPrefix('api');

  // 2. Validation — strict, always
  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,            // strip unknown fields
    forbidNonWhitelisted: true, // reject unknown fields
    transform: true,            // auto-cast primitives
    transformOptions: { enableImplicitConversion: true },
  }));

  // 3. Security headers
  app.use(helmet());
  app.enableCors({ origin: process.env.ALLOWED_ORIGINS?.split(',') ?? [] });

  // 4. Compression
  app.use(compression());

  // 5. Shutdown hooks (K8s SIGTERM)
  app.enableShutdownHooks();

  await app.listen(process.env.PORT ?? 3000);
}
```

### DTO Pattern (every endpoint)
```typescript
import { IsString, IsEmail, IsEnum, IsOptional, Length } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export enum UserRole { ADMIN = 'admin', MEMBER = 'member', VIEWER = 'viewer' }

export class CreateUserDto {
  @ApiProperty({ example: 'alice@corp.com' })
  @IsEmail()
  email: string;

  @IsString()
  @Length(2, 100)
  name: string;

  @IsEnum(UserRole)
  @IsOptional()
  role?: UserRole = UserRole.MEMBER;
}
```

### Interceptor — Structured Response Envelope
```typescript
@Injectable()
export class ResponseEnvelopeInterceptor implements NestInterceptor {
  intercept(ctx: ExecutionContext, next: CallHandler): Observable<any> {
    return next.handle().pipe(
      map(data => ({
        success: true,
        data,
        meta: { timestamp: new Date().toISOString(), version: 'v1' },
      })),
    );
  }
}
```

### Exception Filter — Typed errors, never raw 500s
```typescript
@Catch()
export class GlobalExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger('GlobalExceptionFilter');

  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    const status = exception instanceof HttpException
      ? exception.getStatus()
      : HttpStatus.INTERNAL_SERVER_ERROR;

    const message = exception instanceof HttpException
      ? exception.getResponse()
      : 'Internal server error';

    this.logger.error({
      statusCode: status,
      path: request.url,
      method: request.method,
      traceId: request.headers['x-trace-id'],
      error: exception instanceof Error ? exception.message : String(exception),
    });

    response.status(status).json({
      success: false,
      statusCode: status,
      message,
      path: request.url,
      timestamp: new Date().toISOString(),
    });
  }
}
```

---

## 3. Go — High-Concurrency Services {#go}

### HTTP Service Skeleton (stdlib + chi)
```go
package main

import (
    "context"
    "log/slog"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"
    "github.com/go-chi/chi/v5"
    "github.com/go-chi/chi/v5/middleware"
)

func main() {
    logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
    r := chi.NewRouter()

    r.Use(middleware.RequestID)
    r.Use(middleware.RealIP)
    r.Use(middleware.Recoverer)
    r.Use(middleware.Timeout(30 * time.Second))

    r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
    })

    srv := &http.Server{
        Addr:         ":" + getEnv("PORT", "8080"),
        Handler:      r,
        ReadTimeout:  10 * time.Second,
        WriteTimeout: 30 * time.Second,
        IdleTimeout:  120 * time.Second,
    }

    // Graceful shutdown — mandatory for K8s
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

    go func() {
        logger.Info("server starting", "addr", srv.Addr)
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            logger.Error("server error", "err", err)
            os.Exit(1)
        }
    }()

    <-quit
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()
    if err := srv.Shutdown(ctx); err != nil {
        logger.Error("forced shutdown", "err", err)
    }
    logger.Info("server stopped")
}

func getEnv(key, fallback string) string {
    if v := os.Getenv(key); v != "" { return v }
    return fallback
}
```

### Worker Pool (bounded concurrency — never unbounded goroutines)
```go
func processWithPool(items []Item, concurrency int) []Result {
    sem := make(chan struct{}, concurrency)
    results := make(chan Result, len(items))

    for _, item := range items {
        sem <- struct{}{}
        go func(i Item) {
            defer func() { <-sem }()
            results <- process(i)
        }(item)
    }

    // Drain semaphore
    for i := 0; i < cap(sem); i++ { sem <- struct{}{} }
    close(results)

    var out []Result
    for r := range results { out = append(out, r) }
    return out
}
```

---

## 4. API Design & Contracts {#api}

### Checklist for every endpoint
```
□ Versioned path (/api/v1/...)
□ DTO validates input (whitelist + forbidNonWhitelisted)
□ RBAC guard (role + permission + scope)
□ Rate limiting (per user/IP)
□ Idempotency-Key header on mutations
□ Structured error response (never raw exception)
□ OpenAPI annotation (@ApiProperty, @ApiOperation)
□ Request tracing (X-Trace-Id propagated)
□ Response time < 200ms p95 (or justify exception)
```

### Pagination — cursor always, never offset on large tables
```typescript
// GET /api/v1/items?cursor=abc123&limit=20
export class PaginationDto {
  @IsOptional() @IsString() cursor?: string;
  @IsOptional() @IsInt() @Min(1) @Max(100)
  @Transform(({ value }) => parseInt(value))
  limit: number = 20;
}

// Query pattern
const items = await db.items.findMany({
  where: { id: { gt: decodeCursor(cursor) }, ...filters },
  take: limit + 1,  // fetch one extra to detect hasNextPage
  orderBy: { id: 'asc' },
});

const hasNextPage = items.length > limit;
return {
  items: items.slice(0, limit),
  nextCursor: hasNextPage ? encodeCursor(items[limit - 1].id) : null,
};
```

---

## 5. Database Patterns & Query Optimization {#db}

### Index Strategy (mandatory)
```sql
-- 1. Every FK gets an index
CREATE INDEX CONCURRENTLY idx_orders_user_id ON orders(user_id);
CREATE INDEX CONCURRENTLY idx_orders_workspace_id ON orders(workspace_id);

-- 2. Composite: equality columns FIRST, range/sort LAST
CREATE INDEX CONCURRENTLY idx_orders_ws_status_created
ON orders(workspace_id, status, created_at DESC)
WHERE status != 'archived';  -- partial index = smaller, faster

-- 3. ALWAYS verify with EXPLAIN ANALYZE before shipping
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT * FROM orders WHERE workspace_id = $1 AND status = 'pending'
ORDER BY created_at DESC LIMIT 20;
-- Look for: "Index Scan" not "Seq Scan" on large tables
```

### N+1 Detector (NestJS + Prisma)
```typescript
// BAD: N+1
const orders = await prisma.order.findMany();
for (const order of orders) {
  const user = await prisma.user.findUnique({ where: { id: order.userId } }); // N queries!
}

// GOOD: single query with include
const orders = await prisma.order.findMany({
  include: { user: { select: { id: true, name: true, email: true } } },
});
```

### Connection Pool (always PgBouncer in transaction mode for serverless)
```
Application (serverless) → PgBouncer (transaction mode) → Postgres
  - max_client_conn: 1000
  - default_pool_size: 25  (2× CPU cores)
  - pool_mode: transaction  (never session for serverless)
```

---

## 6. Queue & Event Processing {#queues}

### BullMQ — Production Worker
```typescript
// workers/email.worker.ts
@Processor('email', {
  concurrency: 5,
  limiter: { max: 100, duration: 60_000 },  // 100/min rate limit
})
export class EmailWorker extends WorkerHost {
  async process(job: Job<EmailJobData>): Promise<void> {
    const { to, template, data } = job.data;

    try {
      await this.resend.emails.send({ to, subject: data.subject, react: template(data) });
      await job.updateProgress(100);
    } catch (err) {
      // Only throw for retryable errors
      if (err.statusCode >= 500) throw err;  // Will retry
      // Log non-retryable, don't throw (goes to completed, not failed)
      this.logger.warn('Email delivery failed (non-retryable)', { to, err: err.message });
    }
  }
}

// Queue options: exponential backoff with jitter
const queue = new Queue('email', {
  defaultJobOptions: {
    attempts: 5,
    backoff: { type: 'exponential', delay: 1000 },
    removeOnComplete: { count: 1000 },
    removeOnFail: { count: 5000 },
  },
});
```

---

## 7. Resilience: Idempotency, Retry, Circuit Breaker {#resilience}

### Idempotency Guard (NestJS Middleware)
```typescript
@Injectable()
export class IdempotencyMiddleware implements NestMiddleware {
  constructor(private readonly redis: RedisService) {}

  async use(req: Request, res: Response, next: NextFunction) {
    const key = req.headers['idempotency-key'] as string;
    if (!key || !['POST', 'PUT', 'PATCH', 'DELETE'].includes(req.method)) {
      return next();
    }

    const existing = await this.redis.get(`idempotency:${key}`);
    if (existing) {
      const cached = JSON.parse(existing);
      return res.status(cached.status).json(cached.body);
    }

    // Capture response
    const originalJson = res.json.bind(res);
    res.json = (body: any) => {
      this.redis.setex(
        `idempotency:${key}`,
        86400,  // 24h TTL
        JSON.stringify({ status: res.statusCode, body }),
      );
      return originalJson(body);
    };

    next();
  }
}
```

### Circuit Breaker (Opossum)
```typescript
import CircuitBreaker from 'opossum';

const breaker = new CircuitBreaker(externalApiCall, {
  timeout: 3000,          // 3s timeout
  errorThresholdPercentage: 50,  // open after 50% failures
  resetTimeout: 30000,    // try again after 30s
  volumeThreshold: 5,     // min calls before evaluating
});

breaker.fallback(() => ({ cached: true, data: lastKnownGoodData }));
breaker.on('open', () => logger.warn('Circuit OPEN — external API degraded'));
breaker.on('close', () => logger.info('Circuit CLOSED — external API recovered'));
```

---

## 8. Troubleshooting Playbook {#troubleshooting}

### High Memory (Node.js)
```bash
# 1. Identify the leak
node --inspect app.js
# Chrome DevTools → Memory → Take heap snapshot → Compare

# 2. Common causes
# - Event listeners not removed (missing removeEventListener)
# - Closures holding large objects
# - Unbounded caches (use LRU cache with max size)
# - Prisma not calling $disconnect() in serverless

# 3. Quick fix for serverless (Lambda/Vercel)
process.on('SIGTERM', async () => {
  await prisma.$disconnect();
  process.exit(0);
});
```

### Slow Postgres Queries
```sql
-- Find queries > 1s in last hour
SELECT query, mean_exec_time, calls, total_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 1000
ORDER BY total_exec_time DESC
LIMIT 20;

-- Find missing indexes (sequential scans on large tables)
SELECT relname, seq_scan, idx_scan
FROM pg_stat_user_tables
WHERE seq_scan > idx_scan AND n_live_tup > 10000
ORDER BY seq_scan DESC;
```

### NestJS Module Won't Load
```
Error: Nest can't resolve dependencies of X — check:
1. Provider not in module providers[] array
2. Module not imported in the consumer module
3. Circular dependency → use forwardRef(() => X)
4. Missing @Injectable() decorator
5. Wrong scope (REQUEST scope in SINGLETON context)
```

### Go — Race Condition Debug
```bash
go test -race ./...
go run -race main.go
# Always run with -race in CI; zero-tolerance for data races
```
