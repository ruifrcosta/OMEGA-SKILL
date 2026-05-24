# Mermaid & Architecture Diagram Reference

## Table of Contents
1. [Syntax Integrity Rules (Error Prevention)](#syntax-rules)
2. [C4 Container Models](#c4-models)
3. [Entity Relationship Diagrams (ERDs)](#erds)
4. [Sequence & Interaction Diagrams](#sequence)
5. [Kubernetes Topology Diagrams](#kubernetes-topologies)

---

## 1. Syntax Integrity Rules (Error Prevention) {#syntax-rules}

To prevent Mermaid parsing failures in Markdown viewers:

*   **Quote Special Characters**: Labels containing parentheses, brackets, or punctuation must be explicitly wrapped in double quotes. E.g. `id["Label (Extra Info)"]` instead of `id[Label (Extra Info)]`.
*   **Avoid HTML Tags**: Never inject raw HTML (`<br>`, `<b>`, `<i>`) inside node labels. Use Mermaid native string manipulation or formatting instead.
*   **Decouple Node Names from Labels**: Define clean node IDs (e.g. `webApp`, `postgresDb`) and map labels separately (`webApp["Web Application"]`).

---

## 2. C4 Container Models {#c4-models}

C4 container models show the high-level boundary of software systems and how containers communicate.

```mermaid
flowchart TB
    user([User Context])
    
    subgraph boundary ["OMEGA TITAN Ecosystem"]
        gateway["API Gateway (NGINX)"]
        apiApp["NestJS Core Service"]
        eventBroker[["Kafka Broker"]]
        db[(Postgres DB)]
    end
    
    user -->|HTTPS| gateway
    gateway -->|HTTP Proxy| apiApp
    apiApp -->|Publishes Events| eventBroker
    apiApp -->|Writes Reads| db
```

---

## 3. Entity Relationship Diagrams (ERDs) {#erds}

Use standard crow's foot notation (`||--o{`) to represent database relational mappings.

```mermaid
erDiagram
    ORGANIZATION ||--o{ USER : "owns"
    ORGANIZATION {
        uuid id PK
        string name
        string slug
        timestamp created_at
    }
    USER ||--o{ SESSION : "starts"
    USER {
        uuid id PK
        string email
        string password_hash
        string status
    }
    SESSION {
        uuid id PK
        uuid user_id FK
        string token
        timestamp expires_at
    }
```

---

## 4. Sequence & Interaction Diagrams {#sequence}

Use sequence diagrams to clarify asynchronous tasks, API gateways, and authorization pipelines.

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Gateway as NGINX Gateway
    participant Auth as Auth Service
    participant API as Core API
    
    Client->>Gateway: POST /v1/workspace (JWT Token)
    Gateway->>Auth: Validate JWT Signature
    Auth-->>Gateway: Signature Valid (Scopes: write:workspace)
    Gateway->>API: Forward Authorized Request
    API-->>Gateway: Create Workspace SUCCESS
    Gateway-->>Client: 201 Created (JSON Payload)
```

---

## 5. Kubernetes Topology Diagrams {#kubernetes-topologies}

Use topology flowcharts to design pod communication, routing paths, and multi-zone failovers.

```mermaid
flowchart LR
    ingress[Ingress Controller]
    
    subgraph Zone1 ["Availability Zone 1"]
        pod1["titan-api-pod-1"]
        dbPrimary[(RDS Postgres Primary)]
    end
    
    subgraph Zone2 ["Availability Zone 2"]
        pod2["titan-api-pod-2"]
        dbReplica[(RDS Postgres Replica)]
    end
    
    ingress -->|Load Balance| pod1
    ingress -->|Load Balance| pod2
    
    pod1 --> dbPrimary
    pod2 --> dbPrimary
    dbPrimary -.->|Streaming Replication| dbReplica
```
