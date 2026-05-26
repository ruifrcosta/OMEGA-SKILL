# Infrastructure & Platform Engineering Reference

## Table of Contents
1. [Multi-Zone Architecture & Redundancy](#redundancy)
2. [Docker Configuration Patterns](#docker)
3. [Kubernetes Topology & Manifests](#kubernetes)
4. [Terraform (IaC) Standards](#terraform)
5. [Disaster Recovery & Failover Policies](#dr)

---

## 1. Multi-Zone Architecture & Redundancy {#redundancy}

OMEGA TITAN mandates a active-active multi-zone topology for all production systems. This ensures standard high availability (HA) and automatic resilience against localized cloud region outages.

```
                  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                  â”‚    Cloudflare WAF    â”‚
                  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                              â”‚
                     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”
                     â–¼                 â–¼
             â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
             â”‚ Ingress (AZ1)â”‚   â”‚ Ingress (AZ2)â”‚
             â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚                 â”‚
             â”Œâ”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”
             â–¼       â–¼       â–¼ â–¼       â–¼       â–¼
           [Web]   [API]   [Msg] [Web]  [API]  [Msg]
             â”‚       â”‚       â”‚   â”‚     â”‚       â”‚
             â””â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”˜
                     â–¼                 â–¼
             â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
             â”‚DB Master(AZ1)â”‚â”€â”€â–¶â”‚ DB Replica   â”‚
             â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Mandated HA Constraints
*   **Replica Minimum**: All deployments must maintain at least 3 running pods, distributed across distinct Availability Zones (using pod anti-affinity rules).
*   **Database Redundancy**: A primary transactional database instance paired with at least one hot standby read-replica in a different availability zone with automated promotion capability.
*   **Stateless Services**: All worker nodes and API layers must remain stateless, writing state immediately to databases or transactional message queues.

---

## 2. Docker Configuration Patterns {#docker}

Production Docker images must be multi-stage, rootless, and use optimized minimal base distributions (e.g. Node Alpine or Distroless).

### Node.js Production Dockerfile (NestJS / Next.js)
```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
RUN apk add --no-cache libc6-compat
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build && pnpm prune --prod

# Stage 2: Runner
FROM gcr.io/distroless/nodejs20-debian11 AS runner
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./package.json

ENV NODE_ENV=production
ENV PORT=3000
USER 10001:10001
EXPOSE 3000
CMD ["dist/main.js"]
```

---

## 3. Kubernetes Topology & Manifests {#kubernetes}

Deployments require strictly bounded resource quotas, health checks, and secure network boundaries.

### Production Deployment & Service Template
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: titan-api
  namespace: production
  labels:
    app: titan-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: titan-api
  template:
    metadata:
      labels:
        app: titan-api
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - titan-api
              topologyKey: topology.kubernetes.io/zone
      containers:
      - name: api
        image: production-registry/titan-api:v2.0.4
        resources:
          limits:
            cpu: "1"
            memory: 1Gi
          requests:
            cpu: 500m
            memory: 512Mi
        ports:
        - containerPort: 3000
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health/live
            port: 3000
          initialDelaySeconds: 15
          periodSeconds: 10
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 10001
---
apiVersion: v1
kind: Service
metadata:
  name: titan-api-service
  namespace: production
spec:
  ports:
  - port: 80
    targetPort: 3000
  selector:
    app: titan-api
  type: ClusterIP
```

---

## 4. Terraform (IaC) Standards {#terraform}

Terraform modules must maintain decoupled state using secure remote backends with lock verification (e.g. AWS S3 + DynamoDB or HashiCorp Vault).

### Monorepo Infrastructure Layout
```
infra/
â”œâ”€â”€ modules/
â”‚   â”œâ”€â”€ vpc/
â”‚   â”œâ”€â”€ eks/
â”‚   â””â”€â”€ database/
â””â”€â”€ environments/
    â”œâ”€â”€ dev/
    â””â”€â”€ prod/
        â”œâ”€â”€ main.tf
        â”œâ”€â”€ variables.tf
        â”œâ”€â”€ outputs.tf
        â””â”€â”€ backend.tf
```

### Production Environment Module Call (`prod/main.tf`)
```hcl
terraform {
  required_version = ">= 1.6.0"
  backend "s3" {
    bucket         = "omega-titan-terraform-state"
    key            = "prod/state.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
  }
}

module "vpc" {
  source   = "../../modules/vpc"
  cidr     = "10.0.0.0/16"
  env      = "production"
  az_count = 3
}

module "database" {
  source           = "../../modules/database"
  vpc_id           = module.vpc.vpc_id
  db_name          = "titan_prod"
  instance_class   = "db.r6g.xlarge"
  multi_az         = true
  db_subnet_groups = module.vpc.private_subnets
}
```

---

## 5. Disaster Recovery & Failover Policies {#dr}

The infrastructure must operate within validated business continuity targets:

*   **RPO (Recovery Point Objective)**: Max 1 hour. Databases must execute continuously stream binary logs to cold storage.
*   **RTO (Recovery Time Objective)**: Max 15 minutes. Automatic failover via Route 53 or Cloudflare global DNS load balancers.
*   **Failover Drills**: Triggered quarterly using chaos engineering tools (e.g. Chaos Mesh or LitmusChaos) to confirm active pods dynamically shift in case of simulated node fail.


---

## 6. Docker Development — Full Workflow {#docker-dev}
> Distilled from `netresearch/docker-development-skill`

### Security Anti-Pattern Table
| Anti-Pattern | Why Dangerous | Fix |
|---|---|---|
| `FROM node:latest` | Unpredictable builds | Pin: `node:20.18-alpine` |
| No USER instruction | Runs as root | Add `USER 10001:10001` |
| `ENV SECRET=value` | Persists in image history | Use `--mount=type=secret` |
| `COPY . .` first | Busts deps cache | Copy package.json first |
| `chmod 777` | Overpermissive | Use specific ownership |
| `--privileged` mode | Full host access | Drop specific caps instead |
| Binding to 0.0.0.0 | Exposes all interfaces | Bind to 127.0.0.1 in dev |

### BuildKit Secrets (Never ENV for Secrets)
```dockerfile
# WRONG — secret persists in layer history
# ARG NPM_TOKEN
# RUN npm config set //registry.npmjs.org/:_authToken=\

# CORRECT — secret never touches the filesystem
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm install
```bash
docker build --secret id=npmrc,src=.npmrc .
```n
### Compose — Service Ordering with Health Checks
```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy
        restart: true
  db:
    image: postgres:16-alpine
    healthcheck:
      test: [`CMD-SHELL`, `pg_isready -U postgres`]
      interval: 5s
      start_period: 30s
      retries: 5
```n
---

## 7. Kubernetes 7-Step Failure-Mode Workflow {#k8s-prod}
> Distilled from `LukasNiessen/kubernetes-skill` (KubeShark)

### Step 1: Capture Execution Context
`\ncluster_version, distribution, namespace, workload_type, deploy_method,\npolicy_enforcement, CNI/provider, addon_list\n`\n
### Step 2: Diagnose Failure Mode
- Insecure defaults · Resource starvation · Network exposure
- Privilege sprawl · Fragile rollouts · API drift

### Step 3: CRR (Conditional Reference Retrieval)
Load only the relevant reference file for the failure mode detected — not all references at once.

### Step 4: Propose Fix with Risk Controls
Answer: Why this fix / What could go wrong / What are the guardrails

### Step 5: Generate Artifacts
YAML, Helm, Kustomize, NetworkPolicies, RBAC, PDB, Kyverno/OPA policies

### Step 6: Validate Before Apply
```bash
kubectl apply --dry-run=server -f manifest.yaml
kubeconform -kubernetes-version 1.29 manifest.yaml
# NEVER direct apply to production without dry-run
```n
### Step 7: Output Contract (5-Tuple)
1. Assumptions made
2. Failure mode identified
3. Remediation + tradeoffs
4. Validation plan
5. Rollback notes

### HPA Configuration
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: api }
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource: { name: cpu, target: { type: Utilization, averageUtilization: 70 } }
  behavior:
    scaleUp: { stabilizationWindowSeconds: 30 }
    scaleDown: { stabilizationWindowSeconds: 300 }
```n
### K8s Cost Checklist
```\n□ Resource requests/limits on all containers
□ VPA for right-sizing recommendations
□ Spot instances for stateless workloads (30-70% savings)
□ Cluster autoscaler min/max node counts
□ Namespace ResourceQuotas
□ PodDisruptionBudgets for spot interruptions
□ Idle namespace cleanup CronJob
```n
---

## 8. AWS — Agentic AI, CDK & Serverless {#aws}
> Distilled from `zxkane/aws-skills`  

### 7 Well-Architected Serverless Principles
1. **Speedy/Simple/Singular** — single-purpose Lambda functions
2. **Think Concurrent Requests** — design for concurrency, not volume
3. **Share Nothing** — no local filesystem state; use S3/DynamoDB
4. **No Hardware Affinity** — portable via environment variables
5. **Orchestrate with State Machines** — Step Functions over function chaining
6. **Use Events to Trigger Transactions** — EventBridge/S3 notifications
7. **Design for Failures/Duplicates** — idempotency with DynamoDB check-before-process

### Idempotency Pattern (DLQ + DynamoDB)
```typescript
// Check-before-process idempotency
const existing = await dynamodb.getItem({ Key: { eventId } }).promise();
if (existing.Item?.processed) {
  console.log('Duplicate event, skipping:', eventId);
  return;
}
await processEvent(event);
await dynamodb.putItem({ Item: { eventId, processed: true, ttl: Date.now()/1000 + 86400 } }).promise();
```n
### AWS CDK — ECS Fargate Pattern
```typescript
const taskDef = new ecs.FargateTaskDefinition(this, 'TaskDef', { cpu: 1024, memoryLimitMiB: 2048 });
taskDef.addContainer('Api', {
  image: ecs.ContainerImage.fromEcrRepository(repo),
  logging: ecs.LogDrivers.awsLogs({ streamPrefix: 'api' }),
  secrets: { DB_PASSWORD: ecs.Secret.fromSecretsManager(dbSecret) },
  healthCheck: { command: ['CMD-SHELL', 'curl -f http://localhost:3000/health || exit 1'] },
});
```n
### AWS Cost Operations Checklist
```\n□ Compute Savings Plans (1-3yr): 30-66% savings
□ Reserved Instances for RDS/ElastiCache: up to 69%
□ S3 Intelligent-Tiering (objects > 128KB)
□ Lambda ARM64 Graviton2 (20% cheaper + faster)
□ Spot Fleet for batch/ML (70-90% savings)
□ AWS Cost Anomaly Detection alerts
□ Resource tagging enforcement
```n
