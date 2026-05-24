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
                  ┌──────────────────────┐
                  │    Cloudflare WAF    │
                  └──────────────────────┘
                              │
                     ┌────────┴────────┐
                     ▼                 ▼
             ┌──────────────┐   ┌──────────────┐
             │ Ingress (AZ1)│   │ Ingress (AZ2)│
             └──────────────┘   └──────────────┘
                     │                 │
             ┌───────┼───────┐ ┌───────┼───────┐
             ▼       ▼       ▼ ▼       ▼       ▼
           [Web]   [API]   [Msg] [Web]  [API]  [Msg]
             │       │       │   │     │       │
             └───────┼───────┘   └─────┼───────┘
                     ▼                 ▼
             ┌──────────────┐   ┌──────────────┐
             │DB Master(AZ1)│──▶│ DB Replica   │
             └──────────────┘   └──────────────┘
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
├── modules/
│   ├── vpc/
│   ├── eks/
│   └── database/
└── environments/
    ├── dev/
    └── prod/
        ├── main.tf
        ├── variables.tf
        ├── outputs.tf
        └── backend.tf
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
